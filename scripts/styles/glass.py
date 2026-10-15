# -*- coding: utf-8 -*-
"""风格 4 · 通透玻璃 Glass —— 浅色柔彩渐变 + 渐变球体 + 半透明磨砂玻璃面板。
磨砂实现（PowerPoint 无实时背景模糊）：把"整页背景图"预先高斯模糊，按面板位置精确裁切成一张图片放在面板处，
再叠 白色 35% 透明度 + 1pt 白色半透明描边 + 极淡阴影。移动面板后需重新调用 glass_panel 以更新裁切。"""
from common import *          # noqa
import textures as X

T = make_theme("glass", bg="F3F1FA", ink="26243B", text="3B3955", muted="6E6B86", primary="6A4CF0",
               accent="6A4CF0", dark="26243B", on_dark="FFFFFF", on_dark_muted="E4E1F5", surface="FFFFFF",
               highlight="FF8A73", coral="FF8A73", chart_gray="C7BFEA", line="B9B3D6")
F_TITLE = ("Segoe UI Semibold", "微软雅黑")
F_NUM = ("Segoe UI Light", "微软雅黑")
F_BODY = ("Segoe UI", "微软雅黑")
SIZE = dict(display=60, h1=40, h2=26, lead=20, body=16, meta=12)
PASTEL = [(0.1, 0.15, 0.45, 0.4, "FFD3C4", 0.9, 0), (0.85, 0.2, 0.45, 0.45, "CFC2FF", 0.9, 0),
          (0.7, 0.95, 0.5, 0.35, "B9E4FF", 0.85, 0), (0.15, 0.95, 0.4, 0.3, "C9F2E1", 0.8, 0)]
ORBS = {
    "cover": [(0.74, 0.46, 0.17, "B9A8FF", "6A4CF0"), (0.16, 0.2, 0.06, "FFC2B0", "FF7A62"), (0.92, 0.88, 0.07, "A8E6FF", "3FA9E8")],
    "stat": [(0.33, 0.62, 0.13, "FFC2B0", "FF7A62"), (0.86, 0.25, 0.09, "B9A8FF", "6A4CF0")],
    "chart": [(0.12, 0.78, 0.1, "A8E6FF", "3FA9E8"), (0.88, 0.16, 0.08, "FFC2B0", "FF7A62")],
    "end": [(0.5, 0.5, 0.15, "B9A8FF", "6A4CF0"), (0.22, 0.78, 0.05, "FFC2B0", "FF7A62"), (0.8, 0.22, 0.05, "A8E6FF", "3FA9E8")],
}
PHOTO = dict(sat=0.92, contrast=0.95, bright=1.06, lift=14, warm=-2)   # 明亮、低对比、略冷


def new():
    return new_deck(T, F_BODY[0], F_BODY[1])


def background(kind):
    base = X.glow_field(PASTEL, base=T["bg"], mode="mix", dither=1.2)
    return X.orbs(base, ORBS[kind]) if kind in ORBS else base


def page(prs, kind="cover"):
    s = blank(prs, T["bg"])
    path = background(kind)
    pic(s, path, 0, 0, SW, SH, name="Background")
    return s, path


def glass_panel(slide, bg_path, x, y, w, h, radius=0.28, tint="FFFFFF", alpha=0.36, blur=70, line_alpha=0.75,
                dark=False):
    """磨砂玻璃：模糊背景的精确裁切 + 白色半透明层 + 细描边 + 柔和阴影。bg_path 必须是铺满整页的那张背景"""
    bl = X.blurred(bg_path, radius=blur, bright=1.0)
    p = slide.shapes.add_picture(bl, In(x), In(y), In(w), In(h))
    p.crop_left, p.crop_right = x / SW, 1 - (x + w) / SW
    p.crop_top, p.crop_bottom = y / SH, 1 - (y + h) / SH
    geom = p._element.spPr.find(qn("a:prstGeom")); geom.set("prst", "roundRect")
    av = geom.find(qn("a:avLst"))
    if av is None: av = etree.SubElement(geom, qn("a:avLst"))
    gd = etree.SubElement(av, qn("a:gd")); gd.set("name", "adj"); gd.set("fmla", "val %d" % int(radius / min(w, h) * 100000))
    p.name = "GlassBlur"
    shadow(p, blur=28, dist=8, dir=90, color="4B3F8F", alpha=0.12)
    r = rect(slide, x, y, w, h, fill=tint, alpha=alpha, radius=radius, line="FFFFFF", line_w=1.25,
             line_alpha=line_alpha, name="GlassTint")
    return r


def title(slide, x, y, w, h, s, size=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["h1"], color=color or T["ink"], font=F_TITLE,
                spacing=kw.pop("spacing", 1.1), **kw)


def body(slide, x, y, w, h, s, size=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["body"], color=color or T["text"], font=F_BODY,
                spacing=kw.pop("spacing", 1.4), **kw)


def num_unit(s, size, color, unit_color=None):
    """'128万' → 数字(细体大号) + 单位(小一半、常规字重)，避免中文单位在大字号下显得过重"""
    import re
    m = re.match(r"^([\d.,+\-−%]+)\s*(.*)$", s)
    if not m: return [[(s, {})]]
    return [[(m.group(1), {"size": size}), (" " + m.group(2) if m.group(2) else "", {"size": int(size * 0.42), "color": unit_color or color, "font": F_BODY})]]


# ------------------------------------------------------------------ 版式
def cover(prs, t, sub, meta_s):
    s, bgp = page(prs, "cover")
    glass_panel(s, bgp, 0.9, 1.55, 7.6, 4.4, radius=0.35)
    title(s, 1.45, 2.05, 6.6, 2.0, t, size=SIZE["display"], anchor="b", spacing=1.05)
    body(s, 1.5, 4.2, 6.4, 0.6, sub, size=SIZE["lead"])
    body(s, 1.5, 5.15, 6.4, 0.4, meta_s, size=SIZE["meta"], color=T["muted"])
    return s


def statement(prs, line_s, sub):
    s, bgp = page(prs, "stat")
    glass_panel(s, bgp, 3.1, 2.15, 9.3, 3.25, radius=0.32)
    title(s, 3.7, 2.55, 8.2, 1.7, line_s, size=48, anchor="m")
    body(s, 3.75, 4.35, 8.0, 0.6, sub, size=SIZE["lead"] - 2, color=T["muted"])
    return s


def stats(prs, heading, big1, big2, big3):
    """不等大的三块玻璃（非对称），数字大、说明短"""
    s, bgp = page(prs, "stat")
    title(s, 0.9, 0.75, 7, 0.8, heading, size=SIZE["h2"] + 4)
    glass_panel(s, bgp, 0.9, 1.9, 6.4, 4.75, radius=0.32)
    text(s, 1.45, 2.35, 5.6, 2.2, num_unit(big1[0], 120, T["primary"]), size=120, color=T["primary"], font=F_NUM, anchor="b", spacing=1.0)
    title(s, 1.5, 4.7, 5.3, 0.6, big1[1], size=SIZE["h2"])
    body(s, 1.5, 5.35, 5.3, 0.9, big1[2], color=T["muted"])
    glass_panel(s, bgp, 7.7, 1.9, 4.75, 2.2, radius=0.3)
    text(s, 8.2, 2.15, 4.0, 1.1, num_unit(big2[0], 54, T["ink"], T["muted"]), size=54, color=T["ink"], font=F_NUM, anchor="b")
    body(s, 8.25, 3.3, 4.0, 0.6, big2[1], color=T["muted"])
    glass_panel(s, bgp, 7.7, 4.4, 4.75, 2.25, radius=0.3)
    text(s, 8.2, 4.65, 4.0, 1.1, num_unit(big3[0], 54, T["ink"], T["muted"]), size=54, color=T["ink"], font=F_NUM, anchor="b")
    body(s, 8.25, 5.8, 4.0, 0.6, big3[1], color=T["muted"])
    return s


def photo_glass(prs, img, quote, who, focus=(0.5, 0.5)):
    """满版照片 + 压在照片上的磨砂卡（模糊的是照片本身）"""
    s = blank(prs, T["bg"])
    path = grade(img, SW, SH, focus=focus, **PHOTO)
    pic(s, path, 0, 0, SW, SH)
    glass_panel(s, path, 0.8, 4.05, 6.6, 2.6, radius=0.3, alpha=0.42, blur=50)
    title(s, 1.3, 4.45, 5.7, 1.4, quote, size=26, spacing=1.25, anchor="m")
    body(s, 1.32, 5.95, 5.6, 0.4, who, size=SIZE["meta"] + 1, color=T["muted"])
    credit(s, "Photo: Pexels", color="FFFFFF")
    return s


def chart(prs, heading, desc, cats, vals):
    s, bgp = page(prs, "chart")
    title(s, 0.9, 1.1, 4.0, 2.4, heading, size=SIZE["h1"] - 4, anchor="b")
    body(s, 0.92, 3.75, 3.6, 1.2, desc, color=T["muted"])
    glass_panel(s, bgp, 5.2, 1.0, 7.3, 5.5, radius=0.32)
    ch = K.bar_chart(s, 5.6, 1.45, 6.5, 4.7, cats, vals, T, highlight=len(vals) - 1, horizontal=False, fmt='0',
                     label_size=14)
    return s


def photo_bg_center(prs, img, line_s, sub, focus=(0.5, 0.5)):
    s = blank(prs, T["bg"])
    path = grade(img, SW, SH, focus=focus, sat=0.95, bright=1.05, lift=8)
    pic(s, path, 0, 0, SW, SH)
    glass_panel(s, path, 2.9, 2.2, 7.55, 3.1, radius=0.35, alpha=0.30, blur=60)
    title(s, 3.2, 2.55, 6.95, 1.5, line_s, size=44, align="c", anchor="m")
    body(s, 3.2, 4.15, 6.95, 0.6, sub, align="c", color=T["text"], size=SIZE["lead"] - 2)
    credit(s, "Photo: Pexels", color="FFFFFF")
    return s


def closing(prs, t, sub):
    s, bgp = page(prs, "end")
    glass_panel(s, bgp, 3.65, 2.45, 6.05, 2.6, radius=0.4)
    title(s, 3.65, 2.7, 6.05, 1.4, t, size=54, align="c", anchor="m")
    body(s, 3.65, 4.1, 6.05, 0.5, sub, align="c", color=T["muted"])
    return s


def build_demo(out):
    prs = new()
    cover(prs, "2026\n年度回顾", "把一年，过成看得见的样子", "示例团队 · 2026.12")
    statement(prs, "少做一点，做好一点。", "这是我们今年最常说的一句话。")
    stats(prs, "这一年的三个数字", ("128 万", "累计服务用户", "比去年增长 46%（示例数据）"),
          ("4.8 分", "用户满意度"), ("37 场", "线下活动"))
    photo_glass(prs, "glass_team", "“最好的工作，发生在大家愿意多问一句的时候。”", "—— 年度团队访谈", focus=(0.6, 0.5))
    chart(prs, "每个季度\n都比上一季\n好一点", "季度活跃用户（万人），示例数据。", ["Q1", "Q2", "Q3", "Q4"], [62, 78, 95, 128])
    photo_bg_center(prs, "glass_sky2", "2027，继续向前", "更轻的产品，更近的用户", focus=(0.5, 0.45))
    closing(prs, "谢谢", "示例团队 · 2026 年度回顾")
    return finish(prs, out, "风格 4 · 通透玻璃 Glass", "柔彩渐变 + 渐变球体 · 预模糊背景裁切实现磨砂玻璃 · Segoe UI / 微软雅黑 · 强调色 #6A4CF0")


if __name__ == "__main__":
    build_demo(os.path.join(STY, "glass", "20261004-风格-通透玻璃.pptx"))
