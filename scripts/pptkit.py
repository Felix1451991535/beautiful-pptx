# -*- coding: utf-8 -*-
"""pptkit —— 基于 python-pptx 的「精美 PPT」可复用工具库
功能：主题(配色/字体)写入母版、12 栏栅格、文本/形状/渐变蒙版/图片裁切填充/
ECG 装饰线、原生图表统一风格、页面切换(淡入/平滑 Morph/推入)、进入动画(淡入/擦除/浮入/缩放)、
视频、备注、页脚。依赖：python-pptx>=1.0, Pillow, lxml
"""
import copy, itertools
from lxml import etree
from PIL import Image
from pptx import Presentation
from pptx.util import Emu, Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION, XL_TICK_MARK, XL_TICK_LABEL_POSITION
from pptx.oxml.ns import qn
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_P14 = "http://schemas.microsoft.com/office/powerpoint/2010/main"
NS_P159 = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"
NS_MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"

# ------------------------------------------------------------------ 主题
# 角色化配色：任何页面只引用角色名，换主题=换字典
THEMES = {
    "A": dict(name="医工青蓝", dark_mode=False,
              bg="FFFFFF", surface="F3F6FA", line="D9E2EC",
              ink="102A43", text="334E68", muted="5B6B7F",
              primary="0F4C81", accent="00A3A3", accent_text="007A7A", highlight="F2A541",
              dark="0B2545", on_dark="FFFFFF", on_dark_muted="B6C6D9", accent_on_dark="2EE6D6",
              chart_gray="C3CDD8", chart_gray2="98A6B5", primary_text="0F4C81"),
    "B": dict(name="学术墨绿", dark_mode=False,
              bg="FFFFFF", surface="F2F6F4", line="DCE5E1",
              ink="1B2B28", text="3D504B", muted="5E6E69",
              primary="1F5F4F", accent="2A9D8F", accent_text="1E7268", highlight="E9A23B",
              dark="12332B", on_dark="FFFFFF", on_dark_muted="B5CCC5", accent_on_dark="5ED3C3",
              chart_gray="C5D1CC", chart_gray2="9AABA4", primary_text="1F5F4F"),
    "C": dict(name="暗场科技", dark_mode=True,
              bg="0B0F19", surface="161B2E", line="2A3148",
              ink="F5F5F7", text="C9CEDB", muted="8B93A7",
              primary="3B5BDB", accent="22D3EE", accent_text="22D3EE", highlight="FBBF24",
              dark="05070D", on_dark="FFFFFF", on_dark_muted="9AA3B8", accent_on_dark="22D3EE",
              chart_gray="3A4258", chart_gray2="5A6480", primary_text="8FA8FF"),
}
# 字体：中文(ea) + 西文(latin)。Windows 默认可用；若安装思源黑体/阿里巴巴普惠体，改这里即可全局替换
FONTS = dict(ea="微软雅黑", latin="Segoe UI")
FONTS_FREE = dict(ea="思源黑体 CN", latin="Source Sans 3")  # 免费可商用方案（需先安装）

# ------------------------------------------------------------------ 栅格 (英寸)
SW, SH = 13.333, 7.5          # 16:9
M = 0.667                      # 左右页边距 ≈ 5% 宽
CW = SW - 2 * M                # 内容宽 12.0
COLS, GUT = 12, 0.25
COLW = (CW - (COLS - 1) * GUT) / COLS
TOP_EYEBROW, TOP_TITLE, TITLE_H = 0.50, 0.80, 0.75
CONTENT_TOP, CONTENT_BOTTOM = 1.85, 6.75
FOOTER_Y = 7.0
# 字号阶梯 (pt)
TYPE = dict(display=60, h0=44, h1=28, h2=20, body=18, small=15, caption=12, foot=10)


def col(i, span=1):
    """第 i 栏(0 起)开始、跨 span 栏 -> (x, w)"""
    return M + i * (COLW + GUT), span * COLW + (span - 1) * GUT


def In(v):
    return Emu(int(round(v * 914400)))


def rgb(h):
    return RGBColor.from_string(h)


# ------------------------------------------------------------------ 演示文稿 & 母版
def new_presentation(T, fonts=FONTS):
    prs = Presentation()
    prs.slide_width, prs.slide_height = In(SW), In(SH)
    _patch_theme(prs, T, fonts)
    _patch_master(prs, T)
    return prs


def _patch_theme(prs, T, fonts):
    part = prs.slide_master.part.part_related_by(RT.THEME)
    root = etree.fromstring(part.blob)
    a = lambda t: "{%s}%s" % (NS_A, t)
    cs = root.find(".//" + a("clrScheme"))
    cs.set("name", "pptkit-" + T["name"])
    dk, lt = (T["bg"], T["ink"]) if T["dark_mode"] else (T["ink"], T["bg"])
    vals = dict(dk1=dk, lt1=lt, dk2=T["dark"] if not T["dark_mode"] else T["surface"], lt2=T["surface"] if not T["dark_mode"] else T["text"],
                accent1=T["primary"], accent2=T["accent"], accent3=T["highlight"], accent4=T["muted"],
                accent5=T["dark"], accent6=T["chart_gray"], hlink=T["primary"], folHlink=T["muted"])
    for k, v in vals.items():
        el = cs.find(a(k))
        for c in list(el):
            el.remove(c)
        etree.SubElement(el, a("srgbClr")).set("val", v)
    fs = root.find(".//" + a("fontScheme"))
    fs.set("name", "pptkit")
    for which in ("majorFont", "minorFont"):
        f = fs.find(a(which))
        f.find(a("latin")).set("typeface", fonts["latin"])
        f.find(a("ea")).set("typeface", fonts["ea"])
        for s in f.findall(a("font")):
            if s.get("script") in ("Hans", "Hant"):
                s.set("typeface", fonts["ea"])
    part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _set_xfrm(sp, x, y, w, h):
    spPr = sp.find(qn("p:spPr"))
    xfrm = spPr.find(qn("a:xfrm"))
    if xfrm is None:
        xfrm = etree.SubElement(spPr, qn("a:xfrm"))
        spPr.insert(0, xfrm)
    for c in list(xfrm):
        xfrm.remove(c)
    off = etree.SubElement(xfrm, qn("a:off")); off.set("x", str(In(x))); off.set("y", str(In(y)))
    ext = etree.SubElement(xfrm, qn("a:ext")); ext.set("cx", str(In(w))); ext.set("cy", str(In(h)))


def _ph_type(sp):
    ph = sp.find(".//" + qn("p:ph"))
    return None if ph is None else (ph.get("type") or "body")


def _style_lvl(lvl, size, color, bold=None, algn=None):
    if algn: lvl.set("algn", algn)
    d = lvl.find(qn("a:defRPr"))
    d.set("sz", str(int(size * 100)))
    if bold is not None: d.set("b", "1" if bold else "0")
    for c in d.findall(qn("a:solidFill")):
        d.remove(c)
    sf = etree.Element(qn("a:solidFill")); etree.SubElement(sf, qn("a:srgbClr")).set("val", color)
    d.insert(0, sf)


def _patch_master(prs, T):
    """母版：背景色、标题/正文样式、占位符落在栅格上；版式改中文名"""
    m = prs.slide_master
    m.background.fill.solid(); m.background.fill.fore_color.rgb = rgb(T["bg"])
    el = m._element
    ts = el.find(qn("p:txStyles"))
    _style_lvl(ts.find(qn("p:titleStyle")).find(qn("a:lvl1pPr")), TYPE["h1"], T["ink"], True, "l")
    body = ts.find(qn("p:bodyStyle"))
    for i, sz in enumerate([TYPE["body"], 16, 15, 14, 14, 14, 14, 14, 14], start=1):
        lv = body.find(qn("a:lvl%dpPr" % i))
        if lv is not None:
            _style_lvl(lv, sz, T["text"])
            lv.set("marL", str(In(0.3 * i))); lv.set("indent", str(In(-0.25)))
    for sp in el.iter(qn("p:sp")):
        t = _ph_type(sp)
        if t == "title":
            _set_xfrm(sp, M, TOP_TITLE, CW, TITLE_H)
            bp = sp.find(".//" + qn("a:bodyPr"))
            bp.set("anchor", "t"); [bp.set(k, "0") for k in ("lIns", "tIns", "rIns", "bIns")]
            for c in list(bp): bp.remove(c)
        elif t == "body":
            _set_xfrm(sp, M, CONTENT_TOP, CW, CONTENT_BOTTOM - CONTENT_TOP)
        elif t == "dt":
            _set_xfrm(sp, M, FOOTER_Y, 2.5, 0.3)
        elif t == "ftr":
            _set_xfrm(sp, M + 3, FOOTER_Y, CW - 6, 0.3)
        elif t == "sldNum":
            _set_xfrm(sp, SW - M - 1.5, FOOTER_Y, 1.5, 0.3)
    names = {0: "封面", 1: "标题和内容", 2: "章节过渡", 3: "左右两栏", 4: "对比", 5: "仅标题",
             6: "空白", 7: "内容与说明", 8: "图片与说明", 9: "标题和竖排文字", 10: "竖排标题与文本"}
    k = SW / 10.0
    for i, lay in enumerate(prs.slide_layouts):
        lay._element.cSld.set("name", names.get(i, lay.name))
        for sp in lay._element.iter(qn("p:sp")):
            t = _ph_type(sp)
            xfrm = sp.find(qn("p:spPr")).find(qn("a:xfrm"))
            if t == "title" and i not in (0, 2):
                if xfrm is not None: sp.find(qn("p:spPr")).remove(xfrm)   # 继承母版标题位置
                continue
            if xfrm is not None:                                          # 4:3 -> 16:9 横向缩放
                off, ext = xfrm.find(qn("a:off")), xfrm.find(qn("a:ext"))
                off.set("x", str(int(int(off.get("x")) * k))); ext.set("cx", str(int(int(ext.get("cx")) * k)))
    # 封面 / 章节版式占位符定位与样式
    for sp in prs.slide_layouts[0]._element.iter(qn("p:sp")):
        t = _ph_type(sp)
        if t == "ctrTitle": _set_xfrm(sp, M, 2.2, 7.0, 1.9); _ph_style(sp, TYPE["h0"], T["ink"], True, "b")
        if t == "subTitle": _set_xfrm(sp, M, 4.3, 7.0, 0.6); _ph_style(sp, TYPE["h2"], T["text"], False, "t")
    sec = prs.slide_layouts[2]
    sec.background.fill.solid(); sec.background.fill.fore_color.rgb = rgb(T["dark"])
    for sp in sec._element.iter(qn("p:sp")):
        t = _ph_type(sp)
        if t == "title": _set_xfrm(sp, M + 0.3, 4.4, 9.0, 1.1); _ph_style(sp, TYPE["h0"], T["on_dark"], True, "t")
        if t == "body": _set_xfrm(sp, M + 0.3, 5.45, 9.0, 0.6); _ph_style(sp, TYPE["h2"], T["on_dark_muted"], False, "t")
    for i in (3,):   # 左右两栏：落到 6+6 栅格
        bodies = [sp for sp in prs.slide_layouts[i]._element.iter(qn("p:sp")) if _ph_type(sp) in ("body", "obj")]
        for j, sp in enumerate(bodies[:2]):
            x, w = col(j * 6, 6); _set_xfrm(sp, x, CONTENT_TOP, w, CONTENT_BOTTOM - CONTENT_TOP)
    # 删除不常用版式，保持母版干净：保留 封面/标题和内容/章节过渡/左右两栏/仅标题/空白
    for lay in list(prs.slide_layouts):
        if lay.name not in ("封面", "标题和内容", "章节过渡", "左右两栏", "仅标题", "空白"):
            prs.slide_layouts.remove(lay)


def _ph_style(sp, size, color, bold, anchor):
    """覆盖版式占位符的列表样式（左对齐、字号、颜色）"""
    txb = sp.find(qn("p:txBody"))
    bp = txb.find(qn("a:bodyPr")); bp.set("anchor", anchor)
    for kk in ("lIns", "tIns", "rIns", "bIns"): bp.set(kk, "0")
    for ch in list(bp): bp.remove(ch)
    ls = txb.find(qn("a:lstStyle"))
    for ch in list(ls): ls.remove(ch)
    lv = etree.SubElement(ls, qn("a:lvl1pPr")); lv.set("marL", "0"); lv.set("indent", "0"); lv.set("algn", "l")
    etree.SubElement(lv, qn("a:buNone"))
    d = etree.SubElement(lv, qn("a:defRPr")); d.set("sz", str(int(size * 100))); d.set("b", "1" if bold else "0")
    sf = etree.SubElement(d, qn("a:solidFill")); etree.SubElement(sf, qn("a:srgbClr")).set("val", color)


def layout(prs, name):
    for lay in prs.slide_layouts:
        if lay.name == name: return lay
    raise KeyError(name)


def blank(prs):
    return prs.slides.add_slide(layout(prs, "空白"))


def titled(prs, title, T, eyebrow=None):
    """内容页：使用『仅标题』版式，标题进占位符（大纲/无障碍/Morph 友好）"""
    s = prs.slides.add_slide(layout(prs, "仅标题"))
    s.shapes.title.text = title
    s.shapes.title.name = "Title"
    if eyebrow:
        add_rect(s, M, TOP_EYEBROW + 0.07, 0.28, 0.06, T["accent"], name="EyebrowBar")
        add_text(s, M + 0.4, TOP_EYEBROW - 0.04, 6, 0.3, eyebrow, size=TYPE["caption"], color=T["accent_text"],
                 bold=True, letter=100, name="Eyebrow")
    return s


def set_bg(slide, hexcolor):
    slide.background.fill.solid(); slide.background.fill.fore_color.rgb = rgb(hexcolor)


# ------------------------------------------------------------------ 基础元素
def _nostyle(shp):
    st = shp._element.find(qn("p:style"))
    if st is not None:
        shp._element.remove(st)


def _alpha(shp, alpha):
    """alpha: 0~1 不透明度"""
    clr = shp._element.spPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
    etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 100000)))


def add_rect(slide, x, y, w, h, fill=None, line=None, line_w=0.75, radius=None, alpha=None, name=None,
             shape=MSO_SHAPE.RECTANGLE):
    st = MSO_SHAPE.ROUNDED_RECTANGLE if radius else shape
    shp = slide.shapes.add_shape(st, In(x), In(y), In(w), In(h))
    _nostyle(shp)
    if fill:
        shp.fill.solid(); shp.fill.fore_color.rgb = rgb(fill)
        if alpha is not None: _alpha(shp, alpha)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line); shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    if radius:
        shp.adjustments[0] = min(0.5, radius / min(w, h))
    if name: shp.name = name
    shp.text_frame.text = ""
    return shp


def add_oval(slide, x, y, d, fill=None, line=None, line_w=1.5, name=None):
    return add_rect(slide, x, y, d, d, fill, line, line_w, name=name, shape=MSO_SHAPE.OVAL)


def add_line(slide, x1, y1, x2, y2, color, width=1.0, dash=None, name=None):
    ln = slide.shapes.add_connector(1, In(x1), In(y1), In(x2), In(y2))
    _nostyle(ln)
    ln.line.color.rgb = rgb(color); ln.line.width = Pt(width)
    if dash: ln.line.dash_style = dash
    if name: ln.name = name
    return ln


def set_gradient(shp, stops, angle=0):
    """stops: [(位置0~1, HEX, 不透明度0~1), ...]；angle: 0=左→右, 90=上→下"""
    spPr = shp._element.spPr
    for tag in ("a:solidFill", "a:gradFill", "a:noFill", "a:blipFill", "a:pattFill"):
        for e in spPr.findall(qn(tag)): spPr.remove(e)
    gs = "".join('<a:gs pos="%d"><a:srgbClr val="%s"><a:alpha val="%d"/></a:srgbClr></a:gs>'
                 % (int(p * 100000), c, int(al * 100000)) for p, c, al in stops)
    xml = ('<a:gradFill xmlns:a="%s" rotWithShape="1"><a:gsLst>%s</a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>'
           % (NS_A, gs, int(angle * 60000)))
    g = etree.fromstring(xml)
    geom = spPr.find(qn("a:prstGeom"))
    geom.addnext(g)
    return shp


def add_gradient_rect(slide, x, y, w, h, stops, angle=0, name=None):
    shp = add_rect(slide, x, y, w, h, fill="FFFFFF", name=name)
    return set_gradient(shp, stops, angle)


def add_text(slide, x, y, w, h, paras, size=18, color="333333", bold=False, align="l", anchor="t",
             spacing=1.2, space_after=0, font=None, letter=0, name=None, wrap=True):
    """paras: str（\\n 分段）| [段落]；段落 = str | [(文本, {size,color,bold,font,letter}), ...] | dict(runs=..., size=.., space_before=..)"""
    tb = slide.shapes.add_textbox(In(x), In(y), In(w), In(h))
    tf = tb.text_frame
    tf.word_wrap = wrap; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = dict(t=MSO_ANCHOR.TOP, m=MSO_ANCHOR.MIDDLE, b=MSO_ANCHOR.BOTTOM)[anchor]
    if isinstance(paras, str):
        paras = paras.split("\n")
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = dict(l=PP_ALIGN.LEFT, c=PP_ALIGN.CENTER, r=PP_ALIGN.RIGHT, j=PP_ALIGN.JUSTIFY)[align]
        p.line_spacing = spacing
        pd = para if isinstance(para, dict) else {}
        runs = pd.get("runs", para) if isinstance(para, dict) else para
        if isinstance(runs, str): runs = [(runs, {})]
        p.space_after = Pt(pd.get("space_after", space_after))
        if "space_before" in pd: p.space_before = Pt(pd["space_before"])
        for txt, st in runs:
            r = p.add_run(); r.text = txt
            f = r.font
            f.size = Pt(st.get("size", pd.get("size", size)))
            f.bold = st.get("bold", pd.get("bold", bold))
            f.color.rgb = rgb(st.get("color", pd.get("color", color)))
            fn = st.get("font", font)
            rPr = r._r.get_or_add_rPr()
            rPr.set("lang", "zh-CN"); rPr.set("altLang", "en-US")
            if fn:
                for tag in ("a:latin", "a:ea"):
                    e = rPr.find(qn(tag))
                    if e is None: e = etree.SubElement(rPr, qn(tag))
                    e.set("typeface", fn)
            sp = st.get("letter", letter)
            if sp: rPr.set("spc", str(int(sp)))
    if name: tb.name = name
    return tb


def add_picture_cover(slide, path, x, y, w, h, focus=(0.5, 0.5), radius=None, name=None):
    """等比裁切铺满（CSS object-fit: cover），focus 为保留重点(0~1)"""
    iw, ih = Image.open(path).size
    pic = slide.shapes.add_picture(path, In(x), In(y), In(w), In(h))
    br, ir = w / h, iw / ih
    if ir > br:
        ex = 1 - br / ir; l = ex * focus[0]; pic.crop_left, pic.crop_right = l, ex - l
    else:
        ex = 1 - ir / br; t = ex * focus[1]; pic.crop_top, pic.crop_bottom = t, ex - t
    if radius:
        geom = pic._element.spPr.find(qn("a:prstGeom"))
        geom.set("prst", "roundRect")
        av = geom.find(qn("a:avLst"))
        if av is None: av = etree.SubElement(geom, qn("a:avLst"))
        gd = etree.SubElement(av, qn("a:gd")); gd.set("name", "adj")
        gd.set("fmla", "val %d" % int(min(50000, radius / min(w, h) * 100000)))
    if name: pic.name = name
    return pic


def ecg_points(beats=3):
    """单位坐标的心电折线 (x 0~1, y 0~1，0.6 为基线)"""
    beat = [(0, .6), (.12, .6), (.17, .54), (.22, .6), (.32, .6), (.35, .66), (.39, .08), (.43, .78), (.46, .6),
            (.6, .6), (.68, .48), (.76, .6), (1, .6)]
    pts = []
    for b in range(beats):
        for bx, by in beat[(1 if b else 0):]:
            pts.append(((b + bx) / beats, by))
    return pts


def add_ecg_line(slide, x, y, w, h, color, width=1.5, beats=3, name=None):
    pts = [(In(x + px * w), In(y + py * h)) for px, py in ecg_points(beats)]
    fb = slide.shapes.build_freeform(pts[0][0], pts[0][1], scale=1.0)
    fb.add_line_segments(pts[1:], close=False)
    shp = fb.convert_to_shape()
    _nostyle(shp)
    shp.fill.background(); shp.line.color.rgb = rgb(color); shp.line.width = Pt(width)
    if name: shp.name = name
    return shp


def footer(slide, T, page, text, dark=False):
    c = T["on_dark_muted"] if dark else T["muted"]
    add_text(slide, M, FOOTER_Y, 7, 0.3, text, size=TYPE["foot"], color=c, name="Footer")
    add_text(slide, SW - M - 1.5, FOOTER_Y, 1.5, 0.3, "%02d" % page, size=TYPE["foot"], color=c, align="r",
             name="PageNo")


def add_credit(slide, text, corner="br", dark_bg=True):
    """图片署名：小号白字 + 半透明深色底，放在图片角落，保证任何底图上都可读"""
    w = 0.2 + sum(0.13 if ord(c) > 0x2E80 else 0.07 for c in text)
    x = SW - w - 0.2 if corner == "br" else 0.2
    tb = add_text(slide, x, SH - 0.45, w, 0.3, text, size=9, color="FFFFFF", align="c", anchor="m", name="Credit")
    tb.fill.solid(); tb.fill.fore_color.rgb = rgb("000000"); _alpha(tb, 0.45)
    return tb


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def group(slide, name=None):
    g = slide.shapes.add_group_shape()
    if name: g.name = name
    return g


# ------------------------------------------------------------------ 图表（原生、可编辑）
def _fix_axids(chart):
    """python-pptx 模板的坐标轴 ID 可能为负数，OOXML 架构要求 UInt32，统一取绝对值"""
    cs = chart._chartSpace
    for tag in ("c:axId", "c:crossAx"):
        for e in cs.iter(qn(tag)):
            v = int(e.get("val"))
            if v < 0: e.set("val", str(abs(v)))


def _axis_font(axis, T, size=12):
    axis.tick_labels.font.size = Pt(size); axis.tick_labels.font.color.rgb = rgb(T["muted"])


def bar_chart(slide, x, y, w, h, cats, vals, T, highlight=None, horizontal=True, fmt='0.0', label_size=14,
              series_name="值", gap=70):
    """去杂乱：无网格、无图例、无数值轴；灰色基底 + 1 根强调色"""
    cd = CategoryChartData(); cd.categories = cats; cd.add_series(series_name, vals)
    kind = XL_CHART_TYPE.BAR_CLUSTERED if horizontal else XL_CHART_TYPE.COLUMN_CLUSTERED
    gf = slide.shapes.add_chart(kind, In(x), In(y), In(w), In(h), cd)
    ch = gf.chart
    ch.has_legend = False; ch.has_title = False
    ch.font.size = Pt(12); ch.font.color.rgb = rgb(T["text"])
    pl = ch.plots[0]; pl.gap_width = gap; pl.vary_by_categories = False
    pl.has_data_labels = True
    dl = pl.data_labels; dl.font.size = Pt(label_size); dl.font.bold = True; dl.font.color.rgb = rgb(T["ink"])
    dl.number_format = fmt; dl.number_format_is_linked = False; dl.position = XL_LABEL_POSITION.OUTSIDE_END
    for i, pt in enumerate(pl.series[0].points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = rgb(T["accent"] if i == highlight else T["chart_gray"])
    va = ch.value_axis; va.visible = False; va.has_major_gridlines = False; va.minimum_scale = 0
    ca = ch.category_axis; ca.format.line.color.rgb = rgb(T["line"]); ca.major_tick_mark = XL_TICK_MARK.NONE
    _axis_font(ca, T, 14)
    _fix_axids(ch)
    return gf


def line_chart(slide, x, y, w, h, cats, series, T, colors, widths=None, ymin=None, ymax=None, fmt='0',
               legend=True):
    cd = CategoryChartData(); cd.categories = cats
    for nm, vs in series: cd.add_series(nm, vs)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, In(x), In(y), In(w), In(h), cd)
    ch = gf.chart; ch.has_title = False
    ch.font.size = Pt(12); ch.font.color.rgb = rgb(T["text"])
    ch.has_legend = legend
    if legend:
        ch.legend.position = XL_LEGEND_POSITION.TOP; ch.legend.include_in_layout = False
        ch.legend.font.size = Pt(13); ch.legend.font.color.rgb = rgb(T["text"])
    for i, s in enumerate(ch.plots[0].series):
        s.smooth = False
        s.format.line.color.rgb = rgb(colors[i]); s.format.line.width = Pt((widths or [3] * 9)[i])
        s.marker.style = 8; s.marker.size = 7
        s.marker.format.fill.solid(); s.marker.format.fill.fore_color.rgb = rgb(colors[i])
        s.marker.format.line.color.rgb = rgb(colors[i])
    va = ch.value_axis; va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = rgb(T["line"]); va.major_gridlines.format.line.width = Pt(0.5)
    va.format.line.fill.background(); va.major_tick_mark = XL_TICK_MARK.NONE
    va.tick_labels.number_format = fmt; va.tick_labels.number_format_is_linked = False
    if ymin is not None: va.minimum_scale = ymin
    if ymax is not None: va.maximum_scale = ymax
    _axis_font(va, T)
    ca = ch.category_axis; ca.format.line.color.rgb = rgb(T["line"]); ca.major_tick_mark = XL_TICK_MARK.NONE
    _axis_font(ca, T, 13)
    _fix_axids(ch)
    return gf


# ------------------------------------------------------------------ 切换
def _insert_after_clrmap(sld, el):
    for old in list(sld):
        if old.tag in (qn("p:transition"), "{%s}AlternateContent" % NS_MC):
            sld.remove(old)
    anchor = sld.find(qn("p:clrMapOvr"))
    if anchor is None: anchor = sld.find(qn("p:cSld"))
    anchor.addnext(el)


def set_transition(slide, kind="fade", dur=700, direction=None):
    """kind: fade | morph | push | wipe | none
    morph 需 PowerPoint 2019 / 2021 / 2024 / Microsoft 365（2016 仅能播放，旧版本自动回退为淡入）"""
    if kind == "none": return
    body = {"fade": "<p:fade/>", "morph": '<p159:morph option="byObject"/>',
            "push": '<p:push dir="%s"/>' % (direction or "u"), "wipe": '<p:wipe dir="%s"/>' % (direction or "r")}[kind]
    req = "p159" if kind == "morph" else "p14"
    spd = "slow" if dur >= 1000 else "med"
    xml = ('<mc:AlternateContent xmlns:mc="{mc}" xmlns:p="{p}" xmlns:p14="{p14}">'
           '<mc:Choice xmlns:p159="{p159}" Requires="{req}"><p:transition spd="{spd}" p14:dur="{dur}">{body}</p:transition></mc:Choice>'
           '<mc:Fallback><p:transition spd="{spd}"><p:fade/></p:transition></mc:Fallback></mc:AlternateContent>'
           ).format(mc=NS_MC, p=NS_P, p14=NS_P14, p159=NS_P159, req=req, spd=spd, dur=dur, body=body)
    _insert_after_clrmap(slide._element, etree.fromstring(xml))


# ------------------------------------------------------------------ 进入动画
# effect: fade 淡入 | wipe_l/wipe_b/wipe_t/wipe_r 擦除 | rise 浮入(上浮) | zoom 缩放
_EFF = {"fade": (10, 0), "wipe_l": (22, 8), "wipe_b": (22, 4), "wipe_t": (22, 1), "wipe_r": (22, 2),
        "rise": (42, 0), "zoom": (53, 16)}
_WIPE = {"wipe_l": "wipe(left)", "wipe_b": "wipe(down)", "wipe_t": "wipe(up)", "wipe_r": "wipe(right)"}


def _behaviors(nid, spid, eff, dur):
    tgt = '<p:tgtEl><p:spTgt spid="%d"/></p:tgtEl>' % spid
    out = ('<p:set><p:cBhvr><p:cTn id="%d" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>%s'
           '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
           % (next(nid), tgt))
    def anim(attr, frm, to):
        return ('<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base"><p:cTn id="%d" dur="%d" fill="hold" decel="100000"/>%s'
                '<p:attrNameLst><p:attrName>%s</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
                '<p:tav tm="0"><p:val><p:strVal val="%s"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="%s"/></p:val></p:tav>'
                '</p:tavLst></p:anim>' % (next(nid), dur, tgt, attr, frm, to))
    if eff in _WIPE:
        out += ('<p:animEffect transition="in" filter="%s"><p:cBhvr><p:cTn id="%d" dur="%d"/>%s</p:cBhvr></p:animEffect>'
                % (_WIPE[eff], next(nid), dur, tgt))
    else:
        out += ('<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="%d" dur="%d"/>%s</p:cBhvr></p:animEffect>'
                % (next(nid), dur, tgt))
        if eff == "rise":
            out += anim("ppt_x", "#ppt_x", "#ppt_x") + anim("ppt_y", "#ppt_y+.06", "#ppt_y")
        elif eff == "zoom":
            out += anim("ppt_w", "#ppt_w*0.7", "#ppt_w") + anim("ppt_h", "#ppt_h*0.7", "#ppt_h")
    return out


def animate(slide, groups, auto_first=True):
    """groups: [ [item, ...], ... ]，每个内层列表 = 一次单击（第一组可设为切换后自动播放）
    item: dict(shape=形状, effect='fade', dur=500, delay=0, trigger='after'|'with')
    组内第一项为单击/自动触发，其余默认『上一动画之后』。"""
    nid = itertools.count(3)
    seq, bld, seen = [], [], set()
    for gi, grp in enumerate(groups):
        auto = auto_first and gi == 0
        blocks, t = [], 0
        for k, it in enumerate(grp):
            trig = "first" if k == 0 else it.get("trigger", "after")
            if trig in ("first", "after"):
                blocks.append(dict(offset=t, items=[], end=t))
            b = blocks[-1]
            b["items"].append((trig, it))
            b["end"] = max(b["end"], b["offset"] + it.get("delay", 0) + it.get("dur", 500))
            t = b["end"]
        gxml = ['<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>%s</p:stCondLst><p:childTnLst>'
                % (next(nid), '<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>' if auto else "")]
        for b in blocks:
            gxml.append('<p:par><p:cTn id="%d" fill="hold"><p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>'
                        % (next(nid), b["offset"]))
            for trig, it in b["items"]:
                shp = it["shape"]; spid = shp.shape_id; eff = it.get("effect", "fade"); dur = it.get("dur", 500)
                pid, sub = _EFF[eff]
                nt = {"first": "afterEffect" if auto else "clickEffect", "after": "afterEffect", "with": "withEffect"}[trig]
                gxml.append('<p:par><p:cTn id="%d" presetID="%d" presetClass="entr" presetSubtype="%d" fill="hold" grpId="0" nodeType="%s">'
                            '<p:stCondLst><p:cond delay="%d"/></p:stCondLst><p:childTnLst>%s</p:childTnLst></p:cTn></p:par>'
                            % (next(nid), pid, sub, nt, it.get("delay", 0), _behaviors(nid, spid, eff, dur)))
                if spid not in seen:
                    seen.add(spid)
                    tag = shp._element.tag
                    if tag == qn("p:sp"):
                        bld.append('<p:bldP spid="%d" grpId="0" animBg="1"/>' % spid)
                    elif tag == qn("p:graphicFrame"):
                        bld.append('<p:bldGraphic spid="%d" grpId="0"><p:bldAsOne/></p:bldGraphic>' % spid)
            gxml.append("</p:childTnLst></p:cTn></p:par>")
        gxml.append("</p:childTnLst></p:cTn></p:par>")
        seq.append("".join(gxml))
    xml = ('<p:timing xmlns:p="%s"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
           '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>%s</p:childTnLst></p:cTn>'
           '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           '</p:childTnLst></p:cTn></p:par></p:tnLst>%s</p:timing>'
           % (NS_P, "".join(seq), ("<p:bldLst>%s</p:bldLst>" % "".join(bld)) if bld else ""))
    sld = slide._element
    old = sld.find(qn("p:timing"))
    if old is not None: sld.remove(old)
    el = etree.fromstring(xml)
    ext = sld.find(qn("p:extLst"))
    if ext is not None: ext.addprevious(el)
    else: sld.append(el)


def seq(shapes, effect="fade", dur=500, gap=0, trigger="after"):
    """把一串形状变成依次出现的 item 列表"""
    return [dict(shape=s, effect=effect, dur=dur, delay=gap if i else 0, trigger=trigger) for i, s in enumerate(shapes)]


# ------------------------------------------------------------------ 视频
def add_video(slide, path, x, y, w, h, poster):
    """嵌入 mp4（PowerPoint 2010+ 可播放；单击播放）。注意：该页不要再调用 animate()，以免覆盖媒体时间线"""
    return slide.shapes.add_movie(path, In(x), In(y), In(w), In(h), poster_frame_image=poster, mime_type="video/mp4")
