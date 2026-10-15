# -*- coding: utf-8 -*-
"""风格 3 · 深色极光 Aurora —— 近黑蓝底 + 程序生成的极光光晕（多椭圆高斯叠加，screen 混合）+ 发布会式超大字。
规则：一页一个信息；大字用 Segoe UI Semibold / Light（Windows 自带），中文 微软雅黑；光晕只做背景，不压字。"""
from common import *          # noqa
import textures as X

T = make_theme("aurora", bg="07080F", ink="F4F6FB", text="DCE1EC", muted="8E97AA", primary="3CF0C5",
               accent="3CF0C5", dark="07080F", on_dark="F4F6FB", on_dark_muted="8E97AA", surface="11131D",
               highlight="8C6CFF", dark_mode=True, violet="8C6CFF", magenta="FF4FA3", blue="2D7BFF")
F_DISPLAY = ("Segoe UI Semibold", "微软雅黑")
F_LIGHT = ("Segoe UI Light", "微软雅黑")
F_BODY = ("Segoe UI", "微软雅黑")
SIZE = dict(mega=120, display=80, h1=44, lead=24, body=18, meta=12)
# 预设光晕（坐标 0~1）：(cx, cy, rx, ry, 颜色, 强度, 角度)
GLOWS = {
    "horizon": [(0.18, 1.02, 0.55, 0.22, "19E3B1", 0.95, -12), (0.55, 0.98, 0.5, 0.2, "6A4CFF", 0.9, 8),
                (0.92, 0.85, 0.32, 0.22, "FF4FA3", 0.55, -20)],
    "center": [(0.5, 0.52, 0.42, 0.26, "5B3CFF", 0.75, 0), (0.42, 0.6, 0.25, 0.14, "19E3B1", 0.45, -10)],
    "corner": [(0.95, 0.05, 0.45, 0.35, "2D7BFF", 0.7, 20), (0.78, 0.2, 0.25, 0.2, "19E3B1", 0.5, 0)],
    "left": [(0.0, 0.5, 0.35, 0.6, "6A4CFF", 0.75, 0), (0.12, 0.8, 0.3, 0.2, "19E3B1", 0.55, -15)],
    "dawn": [(0.5, 1.08, 0.75, 0.32, "19E3B1", 0.85, 0), (0.25, 1.0, 0.35, 0.2, "2D7BFF", 0.6, 0),
             (0.78, 1.0, 0.35, 0.2, "FF4FA3", 0.5, 0)],
}
PHOTO = dict(sat=0.7, contrast=1.15, bright=0.75, lift=0, tint="1A2340", tint_amt=0.25)   # 压暗、偏冷、降饱和


def new():
    return new_deck(T, F_BODY[0], F_BODY[1])


def bg(prs, glow="horizon", curtains=0.18):
    s = blank(prs, T["bg"])
    pic(s, X.glow_field(GLOWS[glow], base=T["bg"], curtains=curtains), 0, 0, SW, SH, name="AuroraGlow")
    return s


def grad_text(tb, stops, angle=0):
    """文字渐变填充：stops=[(pos 0~1, hex)]。PowerPoint 完整支持；LibreOffice 预览可能退化为纯色"""
    for r in tb._element.iter(qn("a:r")):
        rPr = r.find(qn("a:rPr"))
        sf = rPr.find(qn("a:solidFill"))
        gf = etree.Element(qn("a:gradFill")); gf.set("rotWithShape", "1")
        gl = etree.SubElement(gf, qn("a:gsLst"))
        for pos, hx in stops:
            g = etree.SubElement(gl, qn("a:gs")); g.set("pos", str(int(pos * 100000)))
            etree.SubElement(g, qn("a:srgbClr")).set("val", hx)
        lin = etree.SubElement(gf, qn("a:lin")); lin.set("ang", str(int(angle * 60000))); lin.set("scaled", "0")
        sf.addprevious(gf); rPr.remove(sf)
    return tb


def big(slide, x, y, w, h, s, size=None, font=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["display"], color=color or T["ink"], font=font or F_DISPLAY,
                spacing=kw.pop("spacing", 1.0), **kw)


def small(slide, x, y, w, h, s, size=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["body"], color=color or T["muted"], font=F_BODY,
                spacing=kw.pop("spacing", 1.35), **kw)


def meta(slide, x, y, w, s, color=None, align="l"):
    return text(slide, x, y, w, 0.3, s, size=SIZE["meta"], color=color or T["primary"], font=F_BODY, letter=300,
                align=align)


# ------------------------------------------------------------------ 版式
def cover(prs, title, sub, meta_s):
    s = bg(prs, "horizon")
    meta(s, 0.9, 0.8, 6, meta_s)
    big(s, 0.8, 1.9, 11.5, 2.2, title, size=SIZE["mega"], anchor="b", letter=-150)
    small(s, 0.9, 4.25, 9, 0.7, sub, size=SIZE["lead"], color=T["text"])
    return s


def statement(prs, line_s, sub=None, glow="center"):
    s = bg(prs, glow)
    big(s, 1.0, 1.6, SW - 2.0, 3.4, line_s, size=SIZE["display"], align="c", anchor="m", spacing=1.1)
    if sub: small(s, 1.0, 5.25, SW - 2.0, 0.6, sub, align="c")
    return s


def hero(prs, img, number, unit, desc, focus=(0.5, 0.5)):
    """产品照片右侧出血，左侧用底色渐变无缝融合；左边一个超大数字"""
    s = blank(prs, T["bg"])
    x0 = 5.4
    pic(s, grade(img, SW - x0, SH, focus=focus, **{**PHOTO, "bright": 0.62, "contrast": 1.2}), x0, 0, SW - x0, SH)
    g = rect(s, x0 - 0.01, 0, 3.2, SH, fill=T["bg"]); set_gradient(g, [(0, T["bg"], 1.0), (1, T["bg"], 0.0)], 0)
    g2 = rect(s, x0, SH - 1.8, SW - x0, 1.8, fill=T["bg"]); set_gradient(g2, [(0, T["bg"], 0.0), (1, T["bg"], 0.85)], 90)
    pic(s, X.radial_glow("6A4CFF", 900, 1.8, 0.55), -3.2, -1.2, 8.5, 8.5, name="Glow")      # 透明 PNG 光晕，不产生接缝
    pic(s, X.radial_glow("19E3B1", 900, 2.0, 0.45), -2.6, 4.0, 6.5, 6.5, name="Glow")
    big(s, 0.8, 1.3, 5.6, 2.8, number, size=180, font=F_LIGHT, anchor="b", letter=-300)
    big(s, 0.9, 4.15, 5.0, 0.7, unit, size=30, color=T["primary"])
    small(s, 0.9, 4.95, 4.4, 1.3, desc)
    return s


def specs(prs, heading, items):
    """三项参数横排：只有数字 + 标签 + 细竖线，不加卡片"""
    s = bg(prs, "corner", curtains=0)
    small(s, 0.9, 0.95, 8, 0.7, heading, size=SIZE["lead"], color=T["text"])
    xs = [0.9, 5.0, 9.1]
    for i, (num, lab, d) in enumerate(items):
        x = xs[i]
        if i: line(s, x - 0.45, 2.75, x - 0.45, 5.6, "FFFFFF", 0.75, alpha=0.18)
        big(s, x, 2.6, 3.9, 1.6, num, size=72, font=F_LIGHT, letter=-150)
        big(s, x, 4.25, 3.6, 0.5, lab, size=20, color=T["primary"])
        small(s, x, 4.8, 3.4, 1.0, d, size=15)
    return s


def photo_feature(prs, img, title, desc, focus=(0.5, 0.5)):
    s = blank(prs, T["bg"])
    pic(s, grade(img, SW, SH, focus=focus, **{**PHOTO, "bright": 1.35}), 0, 0, SW, SH)
    g = rect(s, 0, 0, 8.5, SH, fill=T["bg"]); set_gradient(g, [(0, T["bg"], 0.92), (0.6, T["bg"], 0.55), (1, T["bg"], 0.0)], 0)
    pic(s, X.radial_glow("19E3B1", 800, 2.2, 0.35), -2.5, 3.5, 7, 7)
    big(s, 0.9, 2.0, 6.8, 2.2, title, size=SIZE["h1"] + 10, anchor="b", spacing=1.1)
    small(s, 0.9, 4.45, 5.6, 1.4, desc)
    return s


def date_price(prs, big_s, sub, meta_s):
    s = bg(prs, "dawn")
    meta(s, 0, 1.35, SW, meta_s, align="c")
    tb = big(s, 0.5, 1.9, SW - 1.0, 2.6, big_s, size=150, align="c", anchor="m", font=F_LIGHT, letter=-200)
    grad_text(tb, [(0, "FFFFFF"), (1, "9FF5DD")], 90)
    small(s, 1.0, 4.6, SW - 2.0, 0.7, sub, size=SIZE["lead"], color=T["text"], align="c")
    return s


def closing(prs, line_s, sub):
    s = bg(prs, "horizon", curtains=0.25)
    big(s, 0.9, 1.4, 11, 3.2, line_s, size=96, anchor="b", spacing=1.0, letter=-120)
    small(s, 0.95, 4.85, 8, 0.6, sub)
    return s


def build_demo(out):
    prs = new()
    cover(prs, "Lumen One", "听见更少，感受更多。", "2026 秋季发布会 · OCT 24")
    statement(prs, "安静，\n是新的奢侈。", "我们花了三年，只为把世界调小一点。")
    hero(prs, "aur_head2", "40", "小时续航", "开启降噪后仍有 40 小时；充电 10 分钟，再听 5 小时。", focus=(0.6, 0.45))
    specs(prs, "关键参数", [("−38 dB", "主动降噪", "自适应模式，每秒 5 万次环境采样"),
                          ("248 g", "整机重量", "铝合金头梁，佩戴一整天也轻"),
                          ("6 mic", "通话麦克风", "嘈杂街头也能听清你的声音")])
    photo_feature(prs, "aur_head", "为长时间佩戴\n而设计", "记忆海绵耳垫与可调头梁，均匀分散压力。", focus=(0.5, 0.08))
    date_price(prs, "10.24", "全渠道开售 · 三种颜色 · 示例数据", "AVAILABLE")
    closing(prs, "Hear less.\nFeel more.", "Lumen One · 感谢观看")
    return finish(prs, out, "风格 3 · 深色极光 Aurora", "近黑蓝 #07080F · 程序生成极光光晕 · Segoe UI Semibold/Light + 微软雅黑 · 一页一个信息")


if __name__ == "__main__":
    build_demo(os.path.join(STY, "aurora", "20261004-风格-深色极光.pptx"))
