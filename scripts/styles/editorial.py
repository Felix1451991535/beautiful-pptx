# -*- coding: utf-8 -*-
"""风格 2 · 杂志留白 Editorial（参考 Kami）—— 暖羊皮纸底、单一墨蓝强调、大衬线标题、书刊感。
规则来自 Kami design.md：只用一个彩色（墨蓝 1B365D，可换砖红 A2412B），衬线承担层级，不加粗、不用卡片阴影、不用冷灰。"""
from common import *          # noqa
import textures as X

ACCENTS = dict(ink_blue="1B365D", brick="A2412B")
T = make_theme("editorial", bg="F5F4ED", ink="141413", text="3D3D3A", muted="6B6A64", primary="1B365D",
               accent="1B365D", dark="141413", on_dark="F5F4ED", on_dark_muted="B8B6AC", surface="FAF9F5",
               highlight="1B365D", olive="504E49", rule="D9D6CA", ivory="FAF9F5")
F_SERIF = ("Georgia", "宋体")              # 标题+正文同一衬线；Office 用户中文可换 华文中宋
F_META = ("Segoe UI", "微软雅黑")          # 仅用于极小的栏目名/页眉（大写+字距）
SIZE = dict(display=88, h1=44, h2=28, lead=22, body=16, caption=12, meta=10)
PHOTO = dict(sat=0.82, contrast=0.97, lift=10, warm=5, grain=2.0)   # 柔和暖调、轻微褪色


def new(accent="ink_blue"):
    T["primary"] = T["accent"] = T["highlight"] = ACCENTS.get(accent, accent)
    return new_deck(T, F_SERIF[0], F_SERIF[1])


def page(prs, running=None, num=None):
    s = blank(prs, T["bg"])
    if running:
        text(s, 0.75, 0.42, 6, 0.25, running.upper(), size=SIZE["meta"], color=T["muted"], font=F_META, letter=200)
    if num is not None:
        text(s, SW - 0.75 - 1, 0.42, 1, 0.25, "%02d" % num, size=SIZE["meta"], color=T["muted"], font=F_META,
             align="r", letter=100)
    return s


def serif(slide, x, y, w, h, s, size=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["body"], color=color or T["text"], font=F_SERIF,
                spacing=kw.pop("spacing", 1.45), **kw)


def meta(slide, x, y, w, s, color=None, align="l"):
    return text(slide, x, y, w, 0.3, s.upper(), size=SIZE["meta"], color=color or T["muted"], font=F_META,
                letter=220, align=align)


def rule(slide, x, y, w, color=None, width=0.75):
    return line(slide, x, y, x + w, y, color or T["rule"], width)


def photo(slide, name, x, y, w, h, focus=(0.5, 0.5), **kw):
    return pic(slide, grade(name, w, h, focus=focus, **{**PHOTO, **kw}), x, y, w, h)


# ------------------------------------------------------------------ 版式
def cover(prs, title, issue, deck_line, img, focus=(0.5, 0.5)):
    s = blank(prs, T["bg"])
    photo(s, img, 8.35, 0, SW - 8.35, SH, focus=focus)
    meta(s, 0.85, 0.75, 6, issue, color=T["primary"])
    serif(s, 0.8, 2.0, 7.2, 3.2, title, size=SIZE["display"], color=T["ink"], spacing=0.98, anchor="b")
    rule(s, 0.85, 5.55, 1.2, T["primary"], 1.25)
    serif(s, 0.85, 5.8, 6.4, 0.9, deck_line, size=SIZE["lead"], color=T["olive"], spacing=1.3)
    return s


def contents(prs, heading, items, running, num):
    """目录：衬线大数字（墨蓝）+ 标题 + 一句话，细线分隔；不用编号圆"""
    s = page(prs, running, num)
    serif(s, 0.85, 1.25, 4.2, 1.6, heading, size=SIZE["h1"], color=T["ink"], spacing=1.05)
    y = 1.35
    for pg, t, d in items:
        rule(s, 5.6, y, 6.95)
        serif(s, 5.6, y + 0.25, 1.1, 0.8, pg, size=30, color=T["primary"])
        serif(s, 6.85, y + 0.22, 5.7, 0.6, t, size=SIZE["h2"] - 2, color=T["ink"], spacing=1.1)
        serif(s, 6.85, y + 0.85, 5.7, 0.5, d, size=SIZE["body"] - 1, color=T["muted"], spacing=1.3)
        y += 1.65
    rule(s, 5.6, y, 6.95)
    return s


def essay(prs, headline, dek, cols, img, caption, running, num, focus=(0.5, 0.5)):
    """长文跨页：首字下沉 + 两栏正文 + 侧栏竖图"""
    s = page(prs, running, num)
    serif(s, 0.85, 1.0, 8.0, 1.0, headline, size=SIZE["h1"] - 4, color=T["ink"], spacing=1.05)
    serif(s, 0.85, 1.95, 8.0, 0.6, dek, size=SIZE["lead"] - 4, color=T["olive"])
    rule(s, 0.85, 2.75, 8.1)
    p1, *rest = cols[0].split("\n")
    lead, tail = p1.split(" ", 4)[:4], p1.split(" ", 4)[4:]          # 段首 4 个词用墨蓝+字距（代替易错位的首字下沉）
    paras = [[(" ".join(lead).upper() + " ", {"color": T["primary"], "letter": 80, "size": SIZE["body"] - 2}),
              (" ".join(tail), {})]] + [{"runs": r, "space_before": 10} for r in rest]
    serif(s, 0.85, 3.02, 3.95, 3.8, paras, size=SIZE["body"])
    serif(s, 5.05, 3.02, 3.9, 3.8, cols[1], size=SIZE["body"])
    photo(s, img, 9.55, 1.0, 2.95, 5.15, focus=focus)
    serif(s, 9.55, 6.3, 2.95, 0.6, caption, size=SIZE["caption"], color=T["muted"], spacing=1.3)
    return s


def full_photo(prs, img, caption, credit_s, focus=(0.5, 0.5)):
    s = blank(prs, T["bg"])
    photo(s, img, 0, 0, SW, SH, focus=focus)
    rect(s, 0.6, 5.95, 4.9, 0.95, fill=T["bg"])
    serif(s, 0.85, 6.1, 4.5, 0.7, caption, size=13, color=T["text"], spacing=1.3, anchor="m")
    credit(s, credit_s, color="EDEBE4")
    return s


def big_number(prs, number, unit_line, body_s, source, running, num):
    s = page(prs, running, num)
    serif(s, 0.7, 1.1, 7.2, 3.6, number, size=210, color=T["primary"], spacing=0.9, anchor="b")
    rule(s, 0.85, 5.15, 6.4)
    serif(s, 0.85, 5.35, 6.4, 0.6, unit_line, size=SIZE["lead"], color=T["ink"])
    serif(s, 8.3, 2.55, 4.2, 2.6, body_s, size=SIZE["lead"] - 2, color=T["text"], spacing=1.45)
    meta(s, 8.3, 6.55, 4.2, source)
    return s


def bars(prs, heading, rows, note, running, num):
    """极简横条：只有墨蓝一种色，最高项实色、其余 35% 透明度；数值直接写在条尾"""
    s = page(prs, running, num)
    serif(s, 0.85, 1.0, 5.0, 1.8, heading, size=SIZE["h1"] - 6, color=T["ink"], spacing=1.1)
    serif(s, 0.85, 3.0, 4.2, 2.0, note, size=SIZE["body"], color=T["muted"])
    y = 1.3; mx = max(v for _, v in rows)
    for i, (lab, v) in enumerate(rows):
        serif(s, 6.2, y, 6.2, 0.4, lab, size=SIZE["body"], color=T["ink"], spacing=1.1)
        w = 5.4 * v / mx
        rect(s, 6.2, y + 0.48, w, 0.16, fill=T["primary"], alpha=1.0 if v == mx else 0.35)
        serif(s, 6.2 + w + 0.15, y + 0.33, 1.0, 0.4, "%d%%" % v, size=SIZE["body"], color=T["primary"])
        y += 1.1
    return s


def pull_quote(prs, quote, who, running, num):
    s = page(prs, running, num)
    rule(s, SW / 2 - 0.6, 1.9, 1.2, T["primary"], 1.25)
    serif(s, 2.0, 2.2, SW - 4.0, 2.9, quote, size=40, color=T["ink"], align="c", anchor="m", spacing=1.25)
    meta(s, 2.0, 5.45, SW - 4.0, who, align="c")
    return s


def closing(prs, line_s, sub, credits, img, focus=(0.5, 0.5)):
    s = blank(prs, T["bg"])
    photo(s, img, 0, 0, 4.9, SH, focus=focus)
    serif(s, 5.7, 1.4, 6.8, 2.4, line_s, size=SIZE["h1"] + 8, color=T["ink"], spacing=1.05, anchor="b")
    rule(s, 5.75, 4.1, 1.2, T["primary"], 1.25)
    serif(s, 5.75, 4.35, 6.5, 0.6, sub, size=SIZE["lead"] - 2, color=T["olive"])
    serif(s, 5.75, 5.55, 6.5, 1.3, credits, size=SIZE["caption"], color=T["muted"], spacing=1.4)
    return s


def build_demo(out):
    prs = new()
    R = "The Quiet Hours"
    cover(prs, "The Quiet\nHours", "Vol. 03 — On slow mornings", "Notes on coffee, light, and the first hour of the day.",
          "edit_window", focus=(0.5, 0.55))
    contents(prs, "In this\nissue", [("06", "Why the first hour matters", "A short essay on attention before the noise."),
                                     ("14", "Seven-forty", "What our readers do before eight o’clock."),
                                     ("22", "A table by the window", "Photographs from four quiet kitchens.")], R, 2)
    essay(prs, "Why the first hour matters", "Before the phone, before the inbox — a small room of time.",
          ["Most of us start the day by reacting. The alarm, the messages, the news.\nThe first hour is the only one nobody else has claimed yet. Protect it, and the rest of the day tends to follow its tone: slower, clearer, a little kinder.",
           "Nothing about it needs to be grand. Boil water. Open a window. Read four pages of something printed on paper.\n\nThe point is not productivity. It is to arrive in the day before the day arrives in you."],
          "edit_sun", "Morning light, a cup, and a book left open from the night before.", R, 3, focus=(0.5, 0.6))
    full_photo(prs, "edit_reader", "Reading by the window — the oldest morning ritual we know.",
               "Photo: cottonbro studio / Pexels", focus=(0.5, 0.45))
    big_number(prs, "7:40", "the average time our readers make the first cup",
               "Earlier than we expected — and almost always before checking a phone.", "Reader survey, n = 1,240 (sample data)", R, 5)
    bars(prs, "How the first hour is spent", [("Reading", 34), ("Making coffee or tea", 28), ("A short walk", 19), ("Writing a few lines", 12)],
         "Share of readers naming each activity as their main morning ritual. Sample data for layout.", R, 6)
    pull_quote(prs, "“The morning is not something to get through. It is the one part of the day that is still entirely yours.”",
               "— A reader in Lisbon", R, 7)
    closing(prs, "Thank you\nfor reading.", "Next issue: The Long Evenings.",
            "Photographs: Ioana Motoc, cottonbro studio, Nur Nur (Pexels).\nType: Georgia & SimSun. Paper: #F5F4ED. Ink: #1B365D.",
            "edit_table", focus=(0.5, 0.5))
    return finish(prs, out, "风格 2 · 杂志留白 Editorial（Kami）", "暖羊皮纸 #F5F4ED · 单一墨蓝 #1B365D · Georgia / 宋体 · 细线与留白，无卡片")


if __name__ == "__main__":
    build_demo(os.path.join(STY, "editorial", "20261004-风格-杂志留白.pptx"))
