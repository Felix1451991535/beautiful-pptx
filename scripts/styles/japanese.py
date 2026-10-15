# -*- coding: utf-8 -*-
"""风格 6 · 日式留白 Japanese Minimal —— 米白和纸、竖排标题、大面积留白、细线、印章红点缀。
规则：每页最多一个强调（印章或红点）；文字占画面 ≤ 15%；照片低饱和、偏暖、抬黑位；不加粗、不用卡片。"""
from common import *          # noqa
import textures as X

T = make_theme("japanese", bg="F6F2EA", ink="2B2926", text="3E3A35", muted="6B655C", primary="B7282E",
               accent="B7282E", dark="2B2926", on_dark="F6F2EA", on_dark_muted="D8D2C6", surface="FBF9F4",
               highlight="B7282E", rule="CFC7B8")
F_TITLE = ("Georgia", "宋体")          # 标题：宋体（Windows 自带；Office 用户可换 华文中宋/华文宋体）
F_BODY = ("Georgia", "等线")           # 正文：等线（Win10+ 自带）；若要全衬线可用 宋体 ≥16pt
F_LATIN = ("Georgia", "宋体")
SIZE = dict(display=60, h1=36, h2=26, body=16, small=12, meta=10)
PHOTO = dict(sat=0.62, contrast=0.92, bright=1.04, lift=22, warm=6, grain=2.0)   # 低饱和、雾感、偏暖


def new():
    return new_deck(T, F_BODY[0], F_BODY[1])


def page(prs):
    s = blank(prs, T["bg"])
    pic(s, X.washi(base=T["bg"], fibers=260, seed=31), 0, 0, SW, SH, name="Washi")
    return s


def vtext(slide, x, y, w, h, s, size=None, color=None, font=None, letter=200, **kw):
    """竖排（中文直排，从右往左换列）。w 约等于 列数 × 字号 × 1.6"""
    return text(slide, x, y, w, h, s, size=size or SIZE["display"], color=color or T["ink"], font=font or F_TITLE,
                vert="eaVert", letter=letter, spacing=kw.pop("spacing", 1.3), **kw)


def htext(slide, x, y, w, h, s, size=None, color=None, font=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["body"], color=color or T["text"], font=font or F_BODY,
                spacing=kw.pop("spacing", 1.8), letter=kw.pop("letter", 60), **kw)


def latin(slide, x, y, w, s, align="l", color=None):
    return text(slide, x, y, w, 0.3, s.upper(), size=SIZE["meta"], color=color or T["muted"], font=F_LATIN,
                letter=400, align=align)


def seal_mark(slide, cx, cy, d=0.62, chars="茶", style="white"):
    return pic_c(slide, X.seal(chars, color=T["primary"], style=style), cx, cy, d, d, name="Seal")


def red_dot(slide, cx, cy, d=0.16):
    o = slide.shapes.add_shape(9, In(cx - d / 2), In(cy - d / 2), In(d), In(d))
    K._nostyle(o); o.fill.solid(); o.fill.fore_color.rgb = rgb(T["primary"]); o.line.fill.background()
    return o


def hair(slide, x1, y1, x2, y2):
    return line(slide, x1, y1, x2, y2, T["rule"], 0.6)


def photo(slide, name, x, y, w, h, focus=(0.5, 0.5), **kw):
    return pic(slide, grade(name, w, h, focus=focus, **{**PHOTO, **kw}), x, y, w, h)


# ------------------------------------------------------------------ 版式
def cover(prs, title, sub, en, img, focus=(0.5, 0.5)):
    s = page(prs)
    vtext(s, 10.55, 0.9, 1.3, 5.2, title, size=SIZE["display"])
    vtext(s, 9.75, 1.0, 0.6, 4.2, sub, size=SIZE["body"] + 2, color=T["muted"], font=F_BODY, letter=300)
    seal_mark(s, 11.2, 6.45, 0.6)
    photo(s, img, 0.9, 3.9, 4.3, 2.75, focus=focus)
    latin(s, 0.9, 6.85, 5, en)
    return s


def intro(prs, heading, body_s, img, focus=(0.5, 0.5)):
    s = page(prs)
    photo(s, img, 0, 0, 5.0, SH, focus=focus)
    htext(s, 6.3, 2.2, 6.0, 0.8, heading, size=SIZE["h2"] + 2, color=T["ink"], font=F_TITLE, letter=120, spacing=1.3)
    hair(s, 6.32, 3.25, 7.3, 3.25)
    htext(s, 6.3, 3.6, 5.6, 2.4, body_s, size=SIZE["body"])
    return s


def one_line(prs, line_s, en=None):
    s = page(prs)
    htext(s, 1.5, 3.2, 10.5, 0.8, line_s, size=SIZE["h2"] + 2, color=T["ink"], font=F_TITLE, letter=150, spacing=1.2)
    red_dot(s, 1.6, 4.45)
    if en: latin(s, 1.5, 6.6, 8, en)
    return s


def number(prs, num, vlabel, note):
    s = page(prs)
    text(s, 1.2, 1.7, 7.5, 3.2, num, size=150, color=T["ink"], font=F_LATIN, anchor="b", spacing=0.9)
    hair(s, 1.3, 5.25, 4.3, 5.25)
    htext(s, 1.3, 5.5, 6.0, 1.0, note, size=SIZE["body"], color=T["muted"])
    vtext(s, 10.6, 1.2, 0.9, 4.6, vlabel, size=SIZE["h2"] + 2)
    red_dot(s, 11.05, 6.1)
    return s


def steps(prs, items):
    """三步竖排、自右向左阅读；列间细竖线；不用编号圆"""
    s = page(prs)
    x = 10.6
    for i, (t, d) in enumerate(items):
        vtext(s, x, 1.1, 0.9, 3.4, t, size=SIZE["h1"] + 4, letter=400)
        vtext(s, x - 0.75, 1.25, 0.6, 4.6, d, size=SIZE["body"] - 1, color=T["muted"], font=F_BODY, letter=200,
              spacing=1.5)
        if i < len(items) - 1:
            hair(s, x - 1.45, 1.2, x - 1.45, 6.2)
        x -= 3.15
    red_dot(s, 11.05, 6.55)
    latin(s, 0.9, 6.85, 5, "three steps, no hurry")
    return s


def full_photo(prs, img, vline, focus=(0.5, 0.5)):
    """大图占右侧 62%，左侧和纸上一行竖排短句（字永远不压在照片上）"""
    s = page(prs)
    photo(s, img, 5.05, 0, SW - 5.05, SH, focus=focus, bright=0.95)
    vtext(s, 3.2, 1.0, 0.9, 4.8, vline, size=SIZE["h2"], letter=300)
    red_dot(s, 3.62, 6.3, 0.13)
    return s


def closing(prs, word, en):
    s = page(prs)
    vtext(s, 6.2, 1.6, 1.1, 3.6, word, size=SIZE["display"] + 6, letter=600)
    seal_mark(s, 6.75, 5.75, 0.62, chars="一期一会", style="red")
    latin(s, 0, 6.85, SW, en, align="c")
    return s


def build_demo(out):
    prs = new()
    cover(prs, "一杯茶的时间", "慢下来的二十分钟", "a cup of tea · notes on slowness", "jp_cups", focus=(0.5, 0.5))
    intro(prs, "先，温一只杯子。", "热水注入、倒掉。\n杯壁暖了，茶香才不会被冷意收走。\n这一步什么也不为，只是让手先慢下来。",
          "jp_making", focus=(0.5, 0.5))
    one_line(prs, "水沸之后，让它安静一分钟。", "let the water rest")
    number(prs, "80°C", "绿茶的水温", "太烫会苦，太凉不香。八十度左右刚好。")
    steps(prs, [("温杯", "热水润过杯壁，再倒掉"), ("投茶", "三克茶叶，约一小勺"), ("静候", "注水后等两分钟，不必看表")])
    full_photo(prs, "jp_bamboo", "风过竹林，茶刚好", focus=(0.5, 0.35))
    closing(prs, "谢谢", "thank you for your time")
    return finish(prs, out, "风格 6 · 日式留白 Japanese Minimal", "米白和纸 #F6F2EA · 竖排宋体 · 细线 · 印章红 #B7282E 点缀 · 低饱和雾感照片")


if __name__ == "__main__":
    build_demo(os.path.join(STY, "japanese", "20261004-风格-日式留白.pptx"))
