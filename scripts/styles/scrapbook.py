# -*- coding: utf-8 -*-
"""风格 1 · 手账拼贴 Scrapbook —— 旧皱纸 + 拍立得真实照片 + 半透明胶带 + 手写砖红大标题。
调用：
    from styles import scrapbook as S
    prs = S.new()                                  # 主题/字体已写入母版
    s = S.cover(prs, "adventures", kicker="a year of small", photos=[...])
版式函数都返回 slide，可继续用 S.polaroid / S.tape_strip / S.scrap / S.hand 往上加元素。"""
import random
from common import *          # noqa
import textures as X

T = make_theme("scrapbook", bg="EBE0CA", ink="2E2622", text="3B302A", muted="5F5346", primary="B3261E",
               accent="B3261E", dark="2E2622", on_dark="F6EFE2", on_dark_muted="D9CDBB", surface="FBF8F0",
               highlight="C8A57A", kraft="C8A57A", tape="E3D3AE", frame="FBFAF5", blue="5B7BA6")
# 字体：全部 Windows 自带（Ink Free 需 Win10 1803+；更早系统回退 Segoe Print）
F_HAND = ("Ink Free", "楷体")          # 手写标题/拍立得题字；中文用楷体（Office 用户可换 华文行楷）
F_BODY = ("Georgia", "楷体")           # 正文：衬线，读得清
F_TAG = ("Franklin Gothic Medium", "微软雅黑")   # 红色小号大写署名/角标
F_TYPE = ("Courier New", "仿宋")       # 票根/打字机小字
SIZE = dict(mega=140, title=60, h2=40, hand=28, body=18, caption=20, tag=11)
PHOTO = dict(sat=0.86, contrast=0.96, lift=16, warm=7, grain=4.0)   # 胶片感：降饱和、抬黑、偏暖、颗粒


def new():
    return new_deck(T, F_BODY[0], F_BODY[1])


def bg(prs, seed=3):
    s = blank(prs, T["bg"])
    pic(s, X.paper_crumpled(seed=seed), 0, 0, SW, SH, name="Paper")
    return s


def tape_strip(slide, cx, cy, w=1.5, rot=0, kind="plain", seed=1):
    h = w * 0.26
    path = X.tape(seed=seed, color="D9C393", alpha=0.74) if kind == "plain" else X.tape(seed=seed, stripes=True, color="E9C7B5", stripe_color="D99A8A")
    return pic_c(slide, path, cx, cy, w, h, rot=rot, name="Tape")


def polaroid(slide, photo, cx, cy, w=3.0, rot=0, caption=None, tape="top", focus=(0.5, 0.5), seed=1,
             cap_color=None, cap_size=None):
    """拍立得：白框(带阴影) + 方形照片 + 可选手写题字 + 胶带。cx,cy 为整张拍立得中心"""
    h = w * 1.19; m = w * 0.055; pw = w - 2 * m
    fr = rect(slide, cx - w / 2, cy - h / 2, w, h, fill=T["frame"], rot=rot, name="PolaroidFrame")
    shadow(fr, blur=9, dist=3.5, dir=100, alpha=0.30)
    pcx, pcy = place(cx, cy, 0, -h / 2 + m + pw / 2, rot)
    path = grade(photo, 1, 1, focus=focus, **PHOTO)
    pic(slide, path, pcx - pw / 2, pcy - pw / 2, pw, pw, rot=rot, name="PolaroidPhoto")
    if caption:
        bh = h - m - pw
        ccx, ccy = place(cx, cy, 0, h / 2 - bh / 2, rot)
        text(slide, ccx - pw / 2, ccy - bh / 2, pw, bh, caption, size=cap_size or SIZE["caption"],
             color=cap_color or T["ink"], font=F_HAND, align="c", anchor="m", rot=rot, name="PolaroidCaption")
    if tape:
        rnd = random.Random(seed)
        if tape == "top":
            tx, ty = place(cx, cy, rnd.uniform(-.15, .15) * w, -h / 2 + 0.02, rot)
            tape_strip(slide, tx, ty, w * 0.5, rot + rnd.uniform(-8, 8), seed=seed)
        elif tape == "corners":
            for sx, sy, a in ((-1, -1, -40), (1, 1, -40)):
                tx, ty = place(cx, cy, sx * (w / 2 - 0.12), sy * (h / 2 - 0.12), rot)
                tape_strip(slide, tx, ty, w * 0.36, rot + a + rnd.uniform(-6, 6), seed=seed + sx)
    return fr


def scrap(slide, kind, x, y, w, h, rot=0, shadow_on=True):
    """纸片：kind = lined(横格纸) | kraft(牛皮纸) | plain(白卡纸)"""
    if kind == "lined": path = X.lined_paper()
    elif kind == "kraft": path = X.kraft()
    else: path = X.kraft(base="F7F3EA", seed=7)
    p = pic(slide, path, x, y, w, h, rot=rot, name="Scrap-" + kind, crop_fit=False)
    if shadow_on: shadow(p, blur=6, dist=2.5, dir=100, alpha=0.22)
    return p


def hand(slide, x, y, w, h, s, size=None, color=None, rot=0, align="l", anchor="t", spacing=1.0, **kw):
    """手写字（标题/批注）"""
    return text(slide, x, y, w, h, s, size=size or SIZE["title"], color=color or T["primary"], font=F_HAND,
                bold=kw.pop("bold", True), align=align, anchor=anchor, spacing=spacing, rot=rot, **kw)


def body(slide, x, y, w, h, s, size=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["body"], color=color or T["text"], font=F_BODY,
                spacing=kw.pop("spacing", 1.3), **kw)


def tag(slide, x, y, w, s, align="l", color=None):
    return text(slide, x, y, w, 0.3, s.upper(), size=SIZE["tag"], color=color or T["primary"], font=F_TAG,
                letter=120, align=align, name="Tag")


def arrow(slide, pts, color=None, width=2.0, seed=4):
    """手绘箭头：抖动折线 + 两笔箭头"""
    rnd = random.Random(seed)
    j = [(x + rnd.uniform(-.03, .03), y + rnd.uniform(-.03, .03)) for x, y in pts]
    c = color or T["ink"]
    freeform(slide, j, c, width, name="HandArrow")
    (x1, y1), (x2, y2) = j[-2], j[-1]
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    for d in (2.6, -2.6):
        freeform(slide, [(x2 + 0.22 * math.cos(a + d), y2 + 0.22 * math.sin(a + d)), (x2, y2)], c, width)


def scribble_line(slide, x, y, w, color=None, width=2.5, seed=5):
    """手绘下划线"""
    rnd = random.Random(seed)
    n = 9; pts = [(x + w * i / (n - 1), y + rnd.uniform(-.035, .035)) for i in range(n)]
    return freeform(slide, pts, color or T["primary"], width, name="Scribble")


# ------------------------------------------------------------------ 版式
def cover(prs, title, kicker, photos, handle="@saturday.club", byline="notes by mia chen", scrawl="jan – dec, 2026"):
    s = bg(prs)
    scrap(s, "lined", 4.55, 3.55, 3.9, 3.95, rot=-3)
    polaroid(s, photos[0], 2.05, 2.25, 2.6, rot=-8, seed=2)
    polaroid(s, photos[1], 11.25, 4.75, 2.55, rot=7, seed=3, tape="corners")
    hand(s, 0.25, 2.3, 12.85, 3.1, title, size=SIZE["mega"], align="c", anchor="m", rot=-3, name="Title")
    hand(s, 3.7, 1.55, 5.0, 0.8, kicker, size=34, color=T["ink"], bold=False, rot=-3, name="Kicker")
    hand(s, 4.85, 5.75, 3.4, 0.6, scrawl, size=24, color=T["blue"], bold=False, rot=-3, align="c")
    tag(s, 9.2, 0.62, 3.5, handle, align="r")
    tag(s, 0.7, 6.75, 4, byline)
    return s


def story(prs, heading, paras, photo, date_tag="jan 2026", focus=(0.5, 0.5)):
    s = bg(prs, seed=4)
    polaroid(s, photo, 3.7, 3.85, 4.4, rot=-4, tape="corners", seed=5, focus=focus)
    scrap(s, "kraft", 6.35, 5.65, 1.9, 0.75, rot=6)
    text(s, 6.35, 5.65, 1.9, 0.75, date_tag.upper(), size=13, color=T["ink"], font=F_TYPE, align="c", anchor="m",
         rot=6, bold=True, letter=150)
    hand(s, 7.3, 1.25, 5.6, 1.2, heading, size=56)
    scribble_line(s, 7.4, 2.45, 3.6)
    body(s, 7.35, 2.9, 5.3, 3.0, paras)
    arrow(s, [(8.9, 5.55), (8.3, 6.15), (7.25, 6.1), (6.4, 5.7)], seed=6)
    return s


def collage(prs, heading, items, note=None):
    """3 张拍立得：items=[(photo, caption, focus)]"""
    s = bg(prs, seed=5)
    hand(s, 0.75, 0.45, 7.5, 1.1, heading, size=54)
    xs = [2.75, 6.6, 10.45]; ys = [4.45, 3.85, 4.35]; rots = [-7, 3, -3.5]
    for i, (ph, cap, fc) in enumerate(items[:3]):
        polaroid(s, ph, xs[i], ys[i], 3.3, rot=rots[i], caption=cap, seed=10 + i, focus=fc)
    if note:
        hand(s, 7.95, 0.62, 4.7, 1.0, note, size=24, color=T["ink"], bold=False, rot=3, align="r")
    return s


def note_quote(prs, quote, who, photo=None):
    s = bg(prs, seed=6)
    scrap(s, "lined", 2.35, 1.05, 7.4, 5.6, rot=-2)
    tape_strip(s, 6.05, 1.18, 2.0, rot=-6, kind="stripe", seed=7)
    text(s, 3.45, 2.05, 5.8, 3.0, quote, size=40, color=T["ink"], font=F_HAND, spacing=1.15, rot=-2, anchor="m")
    hand(s, 5.2, 5.25, 4.0, 0.6, who, size=24, rot=-2, align="r", bold=False)
    if photo:
        polaroid(s, photo, 11.0, 3.8, 2.6, rot=8, seed=8)
    return s


def big_number(prs, number, label, line, photo, ticket="ADMIT ONE · SUMMER 26"):
    s = bg(prs, seed=7)
    hand(s, 0.55, 0.2, 6.3, 5.3, number, size=260, anchor="m", align="c", rot=-4)
    hand(s, 0.95, 5.0, 6.0, 0.9, label, size=44, color=T["ink"], rot=-2, align="c")
    body(s, 1.6, 5.95, 4.9, 0.8, line, size=16, align="c", color=T["muted"])
    polaroid(s, photo, 9.8, 3.35, 3.7, rot=5, seed=9, tape="corners")
    tk = rect(s, 7.6, 6.15, 3.6, 0.72, fill="E7D7B8", line=T["primary"], line_w=1.0, dash="dash", rot=-3)
    shadow(tk, blur=4, dist=1.5, alpha=0.2)
    text(s, 7.6, 6.15, 3.6, 0.72, ticket, size=13, color=T["primary"], font=F_TYPE, bold=True, align="c",
         anchor="m", rot=-3, letter=60)
    return s


def three_notes(prs, heading, notes3):
    """三张不同纸片的短笔记：notes3=[(手写小标题, 正文)]，不用编号"""
    s = bg(prs, seed=8)
    hand(s, 0.75, 0.5, 8, 1.1, heading, size=54)
    cfg = [("kraft", 0.9, 2.45, 3.6, 3.2, -4), ("lined", 4.75, 1.55, 3.9, 4.7, 2.5), ("plain", 9.15, 2.95, 3.4, 3.1, -2)]
    for (kind, x, y, w, h, r), (t, b) in zip(cfg, notes3):
        scrap(s, kind, x, y, w, h, rot=r)
        cx, cy = x + w / 2, y + h / 2
        tape_strip(s, *place(cx, cy, 0, -h / 2 + 0.05, r), w=1.3, rot=r + random.Random(x).uniform(-10, 10), seed=int(x))
        hx, hy = place(cx, cy, 0, -h / 2 + 0.95, r)
        hand(s, hx - (w - 0.7) / 2, hy - 0.4, w - 0.7, 0.8, t, size=34, rot=r, color=T["primary"])
        bx, by = place(cx, cy, 0, -h / 2 + 2.25, r)
        body(s, bx - (w - 0.8) / 2, by - 0.8, w - 0.8, 1.6, b, size=17, rot=r)
    return s


def closing(prs, title, line, photo, handle="@saturday.club"):
    s = bg(prs, seed=9)
    polaroid(s, photo, 9.9, 3.6, 4.0, rot=-5, caption="same time next year?", seed=12, tape="corners",
             focus=(0.5, 0.4))
    hand(s, 0.7, 1.0, 7.6, 4.1, title, size=110, anchor="m", rot=-4, spacing=0.9)
    scribble_line(s, 1.0, 5.0, 4.6, seed=9)
    body(s, 1.0, 5.35, 6.0, 0.8, line, size=18)
    tag(s, 0.7, 6.75, 4, handle)
    return s


# ------------------------------------------------------------------ 示例
def build_demo(out):
    prs = new()
    s = cover(prs, "adventures", "a year of small", ["scrap_picnic", "scrap_coffee"])
    notes(s, "封面：一个巨大的手写词 + 两张拍立得 + 一张横格纸，角落红色小字署名。")
    story(prs, "how it started", "One rainy Sunday we made a rule:\ngo somewhere new every weekend,\nno matter how small.\n\nA park. A bakery. A bus to the end of the line.",
          "scrap_photos", focus=(0.5, 0.35))
    collage(prs, "little weekends", [("scrap_friends", "the park, may", (0.5, 0.4)),
                                     ("scrap_blanket", "picnic, june", (0.45, 0.5)),
                                     ("scrap_street", "the sea, july", (0.5, 0.55))], note="(we never planned much)")
    note_quote(prs, "“The best days were the ones we almost stayed home.”", "— our notebook, p. 37",
               photo="scrap_town")
    big_number(prs, "52", "weekends outside", "Rain or shine, one small trip every week.", "scrap_town")
    three_notes(prs, "things we learned", [("go early", "Mornings are quieter, and the light is softer for photos."),
                                           ("pack light", "One bag, one camera, one snack. Everything else is extra."),
                                           ("keep notes", "Two lines a day is enough to remember a whole year.")])
    closing(prs, "see you\noutside", "Thanks for reading our little year.", "scrap_friends")
    return finish(prs, out, "风格 1 · 手账拼贴 Scrapbook", "旧皱纸 · 拍立得真实照片 · 半透明胶带 · 手写砖红标题（Ink Free / 楷体）")


if __name__ == "__main__":
    build_demo(os.path.join(STY, "scrapbook", "20261004-风格-手账拼贴.pptx"))
