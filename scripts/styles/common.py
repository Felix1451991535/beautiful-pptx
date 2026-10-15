# -*- coding: utf-8 -*-
"""风格库公共工具：路径、照片调色、带旋转/阴影的图片、双字体文字、竖排、渲染与总览图。
所有风格模块（scrapbook / editorial / aurora / glass / riso / japanese / guosai）都基于这里。"""
import os, sys, json, glob, hashlib, math, subprocess, shutil
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from fontpath import cjk_font
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from lxml import etree
from pptx.util import Pt, Emu
from pptx.oxml.ns import qn
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.dirname(HERE)
ROOT = os.path.dirname(LIB)
sys.path.insert(0, LIB)
import pptkit as K  # noqa: E402
from pptkit import In, rgb, SW, SH, add_rect, add_line, set_gradient, set_bg, notes, set_transition  # noqa

STY = os.path.join(ROOT, "styles")
RAW = os.path.join(STY, "assets", "raw")       # Pexels 原图（来源见 styles/assets/SOURCES.md）
GEN = os.path.join(STY, "assets", "gen")       # 程序生成的纹理/调色后图片（可随时重新生成）
os.makedirs(GEN, exist_ok=True)
FONTS_CONF = os.path.join(HERE, "fonts.conf")
EMU = 914400


def raw(name):
    p = os.path.join(RAW, name if "." in name else name + ".jpg")
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    return p


def _key(*a, **k):
    return hashlib.md5(json.dumps([a, k], sort_keys=True, default=str).encode()).hexdigest()[:10]


def gen_path(prefix, ext, *a, **k):
    return os.path.join(GEN, "%s_%s.%s" % (prefix, _key(*a, **k), ext))


# ------------------------------------------------------------------ 主题
def make_theme(name, bg, ink, text, muted, primary, accent, dark, on_dark="FFFFFF", on_dark_muted="D0D0D0",
               surface=None, highlight=None, dark_mode=False, **extra):
    """补全 pptkit.new_presentation 需要的键；extra 放风格专有色"""
    T = dict(name=name, bg=bg, ink=ink, text=text, muted=muted, primary=primary, accent=accent,
             accent_text=accent, dark=dark, surface=surface or bg, highlight=highlight or accent,
             chart_gray=muted, on_dark=on_dark, on_dark_muted=on_dark_muted, accent_on_dark=accent,
             dark_mode=dark_mode)
    T["line"] = muted
    T.update(extra)
    return T


def new_deck(T, latin, ea):
    prs = K.new_presentation(T, dict(latin=latin, ea=ea))
    return prs


def blank(prs, bg=None):
    s = K.blank(prs)
    if bg: set_bg(s, bg)
    return s


# ------------------------------------------------------------------ 照片调色
def grade(src, W, H, focus=(0.5, 0.5), sat=1.0, contrast=1.0, bright=1.0, lift=0, warm=0, tint=None,
          tint_amt=0.0, vignette=0.0, grain=0.0, blur=0, px=1600):
    """裁切到 W:H（英寸比例）并调色，返回缓存 jpg 路径。
    sat 饱和度倍数 | contrast 对比度 | bright 亮度 | lift 黑位抬升(0~60) | warm 冷暖(+暖/-冷, 0~20)
    tint/tint_amt 统一色调(保留明度) | vignette 暗角(0~0.6) | grain 颗粒σ(0~12) | blur 高斯模糊半径(px)"""
    src = raw(src) if not os.path.isabs(src) else src
    out = gen_path("ph_" + os.path.splitext(os.path.basename(src))[0], "jpg", W, H, focus, sat, contrast, bright,
                   lift, warm, tint, tint_amt, vignette, grain, blur, px)
    if os.path.exists(out): return out
    im = Image.open(src).convert("RGB")
    pw = int(px if W >= H else px * W / H); ph = int(pw * H / W)
    im = ImageOps.fit(im, (pw, ph), Image.LANCZOS, centering=focus)
    if sat != 1: im = ImageEnhance.Color(im).enhance(sat)
    if contrast != 1: im = ImageEnhance.Contrast(im).enhance(contrast)
    if bright != 1: im = ImageEnhance.Brightness(im).enhance(bright)
    a = np.asarray(im).astype(np.float32)
    if lift: a = lift + a * (255 - lift) / 255.0
    if warm:
        a[..., 0] += warm; a[..., 1] += warm * 0.35; a[..., 2] -= warm
    if tint and tint_amt:
        lum = (a[..., 0] * .299 + a[..., 1] * .587 + a[..., 2] * .114)[..., None] / 255.0
        tc = np.array([int(tint[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
        # 保留明度的统一色调：暗部→tint 深色、亮部→接近白
        toned = np.where(lum < .5, 2 * lum * tc, 255 - 2 * (1 - lum) * (255 - tc))
        a = a * (1 - tint_amt) + toned * tint_amt
    if vignette:
        yy, xx = np.mgrid[0:ph, 0:pw]
        d = np.sqrt(((xx - pw / 2) / (pw / 2)) ** 2 + ((yy - ph / 2) / (ph / 2)) ** 2) / 1.414
        a *= (1 - vignette * np.clip(d, 0, 1) ** 2)[..., None]
    if grain:
        a += np.random.default_rng(7).normal(0, grain, a.shape[:2])[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    im.save(out, quality=88)
    return out


# ------------------------------------------------------------------ 形状/图片
def _rot(dx, dy, deg):
    r = math.radians(deg)
    return dx * math.cos(r) - dy * math.sin(r), dx * math.sin(r) + dy * math.cos(r)


def place(cx, cy, dx, dy, deg):
    """局部坐标 (dx,dy)（相对父元素中心、未旋转）→ 父元素旋转 deg 后的全局中心"""
    ox, oy = _rot(dx, dy, deg)
    return cx + ox, cy + oy


def shadow(shp, blur=8, dist=3, dir=90, color="000000", alpha=0.30):
    """外阴影（PowerPoint 与 LibreOffice 均支持）。blur/dist 单位 pt，dir 角度(90=向下)"""
    spPr = shp._element.spPr
    eff = spPr.find(qn("a:effectLst"))
    if eff is None:
        eff = etree.SubElement(spPr, qn("a:effectLst"))
    for c in list(eff): eff.remove(c)
    sh = etree.SubElement(eff, qn("a:outerShdw"))
    sh.set("blurRad", str(int(blur * 12700))); sh.set("dist", str(int(dist * 12700)))
    sh.set("dir", str(int(dir * 60000))); sh.set("algn", "ctr"); sh.set("rotWithShape", "0")
    c = etree.SubElement(sh, qn("a:srgbClr")); c.set("val", color)
    etree.SubElement(c, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    return shp


def pic(slide, path, x, y, w, h=None, rot=0, radius=None, name=None, crop_fit=True, focus=(0.5, 0.5)):
    """放图片：h=None 时按原图比例；crop_fit=True 时等比裁切铺满 w×h"""
    iw, ih = Image.open(path).size
    if h is None: h = w * ih / iw
    p = slide.shapes.add_picture(path, In(x), In(y), In(w), In(h))
    if crop_fit:
        br, ir = w / h, iw / ih
        if abs(br - ir) > 1e-3:
            if ir > br:
                ex = 1 - br / ir; l = ex * focus[0]; p.crop_left, p.crop_right = l, ex - l
            else:
                ex = 1 - ir / br; t = ex * focus[1]; p.crop_top, p.crop_bottom = t, ex - t
    if not rot:
        _clip_to_slide(p, x, y, w, h)
    if radius:
        geom = p._element.spPr.find(qn("a:prstGeom")); geom.set("prst", "roundRect")
        av = geom.find(qn("a:avLst"))
        if av is None: av = etree.SubElement(geom, qn("a:avLst"))
        gd = etree.SubElement(av, qn("a:gd")); gd.set("name", "adj")
        gd.set("fmla", "val %d" % int(min(50000, radius / min(w, h) * 100000)))
    if rot: p.rotation = rot
    if name: p.name = name
    return p


def _clip_to_slide(p, x, y, w, h):
    """出血到页面外的图片：改为裁切图片本身（视觉不变），避免越界元素"""
    l, t = max(0.0, -x), max(0.0, -y)
    r, b = max(0.0, x + w - SW), max(0.0, y + h - SH)
    if not (l or t or r or b): return
    cl, cr, ct, cb = p.crop_left, p.crop_right, p.crop_top, p.crop_bottom
    sx, sy = (1 - cl - cr) / w, (1 - ct - cb) / h
    p.crop_left, p.crop_right = cl + l * sx, cr + r * sx
    p.crop_top, p.crop_bottom = ct + t * sy, cb + b * sy
    p.left, p.top = In(x + l), In(y + t)
    p.width, p.height = In(w - l - r), In(h - t - b)


def pic_c(slide, path, cx, cy, w, h=None, rot=0, **kw):
    """以中心点放图片"""
    if h is None:
        iw, ih = Image.open(path).size; h = w * ih / iw
    return pic(slide, path, cx - w / 2, cy - h / 2, w, h, rot=rot, **kw)


def rect(slide, x, y, w, h, fill=None, line=None, line_w=0.75, alpha=None, rot=0, radius=None, name=None,
         shape=MSO_SHAPE.RECTANGLE, line_alpha=None, dash=None):
    s = add_rect(slide, x, y, w, h, fill=fill, line=line, line_w=line_w, alpha=alpha, radius=radius, name=name,
                 shape=shape)
    if rot: s.rotation = rot
    if line and line_alpha is not None:
        clr = s._element.spPr.find(qn("a:ln")).find(".//" + qn("a:srgbClr"))
        etree.SubElement(clr, qn("a:alpha")).set("val", str(int(line_alpha * 100000)))
    if line and dash:
        ln = s._element.spPr.find(qn("a:ln"))
        d = etree.SubElement(ln, qn("a:prstDash")); d.set("val", dash)
    return s


def line(slide, x1, y1, x2, y2, color, width=0.75, alpha=None, dash=None, name=None):
    s = add_line(slide, x1, y1, x2, y2, color, width=width, dash=dash, name=name)
    if alpha is not None:
        clr = s._element.spPr.find(qn("a:ln")).find(".//" + qn("a:srgbClr"))
        etree.SubElement(clr, qn("a:alpha")).set("val", str(int(alpha * 100000)))
    return s


def freeform(slide, pts, color, width=1.5, closed=False, fill=None, name=None):
    """手绘感折线：pts 英寸坐标列表"""
    fb = slide.shapes.build_freeform(In(pts[0][0]), In(pts[0][1]), scale=1.0)
    fb.add_line_segments([(In(x), In(y)) for x, y in pts[1:]], close=closed)
    s = fb.convert_to_shape()
    K._nostyle(s)
    if fill:
        s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    else:
        s.fill.background()
    if color:
        s.line.color.rgb = rgb(color); s.line.width = Pt(width)
    else:
        s.line.fill.background()
    if name: s.name = name
    return s


# ------------------------------------------------------------------ 文字
def text(slide, x, y, w, h, paras, size=18, color="333333", font=None, bold=False, italic=False, align="l",
         anchor="t", spacing=1.15, space_after=0, letter=0, rot=0, name=None, wrap=True, vert=None,
         autofit=False):
    """paras: str（\\n 分段）| [段落]；段落 = str | [(文本, {size,color,bold,italic,font,letter})] | dict(runs=,..)
    font: "Georgia" 或 ("Georgia", "宋体")=(西文, 中文)；vert="eaVert" 竖排（中文直排）"""
    tb = slide.shapes.add_textbox(In(x), In(y), In(w), In(h))
    tf = tb.text_frame
    tf.word_wrap = wrap; tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = dict(t=MSO_ANCHOR.TOP, m=MSO_ANCHOR.MIDDLE, b=MSO_ANCHOR.BOTTOM)[anchor]
    bp = tf._txBody.find(qn("a:bodyPr"))
    if vert: bp.set("vert", vert)
    if isinstance(paras, str): paras = paras.split("\n")
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        pd = para if isinstance(para, dict) else {}
        p.alignment = dict(l=PP_ALIGN.LEFT, c=PP_ALIGN.CENTER, r=PP_ALIGN.RIGHT, j=PP_ALIGN.JUSTIFY)[pd.get("align", align)]
        p.line_spacing = pd.get("spacing", spacing)
        runs = pd.get("runs", para) if isinstance(para, dict) else para
        if isinstance(runs, str): runs = [(runs, {})]
        p.space_after = Pt(pd.get("space_after", space_after))
        if "space_before" in pd: p.space_before = Pt(pd["space_before"])
        for txt, st in runs:
            r = p.add_run(); r.text = txt
            f = r.font
            f.size = Pt(st.get("size", pd.get("size", size)))
            f.bold = st.get("bold", pd.get("bold", bold))
            f.italic = st.get("italic", pd.get("italic", italic))
            f.color.rgb = rgb(st.get("color", pd.get("color", color)))
            fn = st.get("font", pd.get("font", font))
            rPr = r._r.get_or_add_rPr()
            rPr.set("lang", st.get("lang", "zh-CN")); rPr.set("altLang", "en-US")
            if fn:
                lat, ea = (fn, fn) if isinstance(fn, str) else fn
                for tag, val in (("a:latin", lat), ("a:ea", ea), ("a:cs", lat)):
                    e = rPr.find(qn(tag))
                    if e is None: e = etree.SubElement(rPr, qn(tag))
                    e.set("typeface", val)
            sp = st.get("letter", pd.get("letter", letter))
            if sp: rPr.set("spc", str(int(sp)))
            a = st.get("alpha")
            if a is not None:
                clr = rPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
                etree.SubElement(clr, qn("a:alpha")).set("val", str(int(a * 100000)))
    if rot: tb.rotation = rot
    if name: tb.name = name
    return tb


def text_shadow(tb, blur=6, dist=2, dir=90, color="000000", alpha=0.45):
    """给文本框内所有 run 加外阴影（文字发光/压暗用）"""
    for r in tb._element.iter(qn("a:r")):
        rPr = r.find(qn("a:rPr"))
        eff = etree.Element(qn("a:effectLst"))
        sh = etree.SubElement(eff, qn("a:outerShdw"))
        sh.set("blurRad", str(int(blur * 12700))); sh.set("dist", str(int(dist * 12700)))
        sh.set("dir", str(int(dir * 60000))); sh.set("algn", "ctr"); sh.set("rotWithShape", "0")
        c = etree.SubElement(sh, qn("a:srgbClr")); c.set("val", color)
        etree.SubElement(c, qn("a:alpha")).set("val", str(int(alpha * 100000)))
        sf = rPr.find(qn("a:solidFill"))
        sf.addnext(eff)
    return tb


def credit(slide, s, x=None, y=None, color="8A8A8A", size=10, font="Segoe UI", align="r", w=4.5):
    """照片署名（Pexels 要求非强制，但我们统一保留，便于追溯）"""
    if x is None: x = SW - 0.45 - w
    if y is None: y = SH - 0.38
    return text(slide, x, y, w, 0.25, s, size=size, color=color, font=font, align=align, name="Credit")


# ------------------------------------------------------------------ 渲染 / 检查 / 总览
def render(pptx, outdir, dpi=110):
    """独立 LibreOffice profile + 独立 fontconfig，不与其他任务抢锁"""
    os.makedirs(outdir, exist_ok=True)
    env = dict(os.environ, FONTCONFIG_FILE=FONTS_CONF)
    prof = "-env:UserInstallation=file:///tmp/lo_styles_profile"
    subprocess.run(["soffice", prof, "--headless", "--convert-to", "pdf", "--outdir", outdir, pptx],
                   check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    for f in glob.glob(os.path.join(outdir, "slide-*.png")): os.remove(f)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, os.path.join(outdir, "slide")], check=True)
    return pdf, sorted(glob.glob(os.path.join(outdir, "slide-*.png")))


def _font(sz, bold=False):
    p = cjk_font("sans", bold)
    return ImageFont.truetype(p, sz)


def overview(pngs, out, title, subtitle="", cols=4, tw=560, pad=26, bg="#EDEBE6", fg="#2A2A2A"):
    ims = [Image.open(p).convert("RGB") for p in pngs]
    th = int(tw * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    head = 96
    W = cols * tw + (cols + 1) * pad; H = head + rows * (th + pad) + pad
    sheet = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(sheet)
    d.text((pad, 22), title, fill=fg, font=_font(34, True))
    if subtitle: d.text((pad, 64), subtitle, fill="#6B6B6B", font=_font(18))
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad); y = head + r * (th + pad)
        t = im.resize((tw, th), Image.LANCZOS)
        sh = Image.new("RGBA", (tw + 16, th + 16), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([8, 10, tw + 8, th + 10], fill=(0, 0, 0, 50))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        sheet.paste(sh, (x - 8, y - 6), sh)
        sheet.paste(t, (x, y))
    sheet.save(out)
    return out


def validate(pptx, pdf=None):
    """scripts/check.py + OOXML 校验；返回 (check_issues, ooxml_ok, ooxml_output)"""
    sys.path.insert(0, LIB)
    import importlib, io, contextlib
    import check
    importlib.reload(check)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        issues = check.main(pptx, pdf)
    r = subprocess.run(["npx", "-y", "@xarsh/ooxml-validator", pptx], capture_output=True, text=True, timeout=600)
    outp = (r.stdout + r.stderr).strip()
    ok = r.returncode == 0 and ('"ok":true' in outp.replace(" ", "") or "valid" in outp.lower() or outp == "")
    return issues, ok, outp


VERT = ("eaVert", "vert", "vert270", "mongolianVert", "wordArtVert", "wordArtVertRtl")


def fit_boxes(prs, margin=1.04):
    """按 scripts/check.py 的保守估算（Noto 字宽 × 1.45 行高）给文本框留足空间：
    只沿"不移动文字"的方向扩框（顶对齐向下、底对齐向上、居中两头；竖排向左），所以版面视觉不变，
    但在 Windows 真实字体下也有余量。扩出页面时夹回页内。"""
    sys.path.insert(0, LIB)
    import check
    for sl in prs.slides:
        for sh in sl.shapes:
            if not sh.has_text_frame or not sh.text_frame.text.strip(): continue
            tf = sh.text_frame
            vert = tf._txBody.find(qn("a:bodyPr")).get("vert") in VERT
            W, H = sh.width / 12700, sh.height / 12700
            need = check.text_height(tf, H if vert else W) * margin + 3
            have = W if vert else H
            if need <= have: continue
            grow = int((need - have) * 12700)
            if vert:
                nl = max(0, sh.left - grow); sh.width = sh.width + (sh.left - nl); sh.left = nl
                continue
            anc = tf._txBody.find(qn("a:bodyPr")).get("anchor", "t")
            top = sh.top - (grow if anc == "b" else grow // 2 if anc == "ctr" else 0)
            hgt = sh.height + grow
            top = max(0, top); hgt = min(hgt, prs.slide_height - top)
            sh.top, sh.height = int(top), int(hgt)


def finish(prs, out_pptx, style_title, subtitle, outdir=None):
    """保存 → 渲染 → 总览 → 检查，打印结果"""
    os.makedirs(os.path.dirname(out_pptx), exist_ok=True)
    fit_boxes(prs)
    prs.save(out_pptx)
    outdir = outdir or os.path.join(os.path.dirname(out_pptx), "render")
    pdf, pngs = render(out_pptx, outdir)
    ov = overview(pngs, os.path.join(os.path.dirname(out_pptx), "总览.png"), style_title, subtitle)
    print("saved", out_pptx, len(pngs), "pages; overview", ov)
    return pdf, pngs, ov
