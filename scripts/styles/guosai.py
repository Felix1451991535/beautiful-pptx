# -*- coding: utf-8 -*-
"""风格 7 · 国赛金奖风（大学生创新大赛 / 挑战杯路演）—— 满版大照片 + 书法大标题（金色发光）+ 统一深色主色调。
主色方案：深绿（农业/环保/乡村振兴，默认）、深蓝（科技/工程）、酒红（文化/非遗）；金色只给标题、关键数字、细线。
字体：标题 华文行楷（随 Microsoft Office 安装，Windows 本身不带）→ 无 Office 时回退 楷体（Windows 自带）；正文 微软雅黑。"""
from common import *          # noqa
import textures as X

SCHEMES = {
    "green": dict(bg="05241A", panel="0A3626", tint="0E3B2A", muted="A7BFB1"),
    "blue": dict(bg="061630", panel="0B2448", tint="0D2A57", muted="A9B7CF"),
    "wine": dict(bg="2A0A10", panel="3D1119", tint="4A1420", muted="CFB0B3"),
}
T = make_theme("guosai", bg="05241A", ink="F4EFE2", text="E6E2D6", muted="A7BFB1", primary="E2BE6A",
               accent="E2BE6A", dark="05241A", on_dark="F4EFE2", on_dark_muted="A7BFB1", surface="0A3626",
               highlight="F3DFA2", dark_mode=True, gold="E2BE6A", gold_light="F6E3AE", panel="0A3626", tint="0E3B2A")
F_CAL = ("华文行楷", "华文行楷")         # 书法标题（Office 字体）；可改 "楷体"（Windows 自带）或 "方正姚体"（Office）
F_CAL_FALLBACK = ("楷体", "楷体")
F_BODY = ("Segoe UI", "微软雅黑")
F_NUM = ("Bahnschrift", "微软雅黑")      # 数字：Bahnschrift（Win10 1709+ 自带，DIN 风格）
SIZE = dict(mega=150, display=88, h1=48, h2=28, lead=22, body=16, small=13)


def new(scheme="green"):
    sc = SCHEMES[scheme]
    T.update(bg=sc["bg"], dark=sc["bg"], surface=sc["panel"], panel=sc["panel"], tint=sc["tint"], muted=sc["muted"],
             on_dark_muted=sc["muted"])
    return new_deck(T, F_BODY[0], F_BODY[1])


def photo_bg(prs, img, focus=(0.5, 0.5), dark=0.55, side=None):
    """满版照片 → 统一色调（tint）→ 暗角 →（可选）一侧渐变压暗供放字"""
    s = blank(prs, T["bg"])
    pic(s, grade(img, SW, SH, focus=focus, sat=0.9, contrast=1.1, tint=T["tint"], tint_amt=0.38, vignette=0.35),
        0, 0, SW, SH, name="Photo")
    o = rect(s, 0, 0, SW, SH, fill=T["bg"], alpha=dark * 0.6, name="Tone")
    if side == "left":
        g = rect(s, 0, 0, SW * 0.7, SH, fill=T["bg"]); set_gradient(g, [(0, T["bg"], 0.92), (0.55, T["bg"], 0.6), (1, T["bg"], 0.0)], 0)
    elif side == "bottom":
        g = rect(s, 0, SH * 0.35, SW, SH * 0.65, fill=T["bg"]); set_gradient(g, [(0, T["bg"], 0.0), (1, T["bg"], 0.95)], 90)
    return s


def plain(prs):
    s = blank(prs, T["bg"])
    pic(s, X.glow_field([(0.85, 0.1, 0.5, 0.35, "1F6B47", 0.55, 0), (0.1, 1.0, 0.45, 0.3, "0F4A33", 0.6, 0)],
                        base=T["bg"]), 0, 0, SW, SH, name="Glow")
    return s


def cal(slide, x, y, w, h, s, size=None, color=None, glow=True, **kw):
    """书法标题：金色 + 外发光（用金色模糊阴影模拟，PowerPoint/LibreOffice 都能显示）"""
    tb = text(slide, x, y, w, h, s, size=size or SIZE["display"], color=color or T["gold_light"], font=F_CAL,
              spacing=kw.pop("spacing", 1.0), **kw)
    if glow: text_shadow(tb, blur=16, dist=0, color="F2C661", alpha=0.45)
    return tb


def body(slide, x, y, w, h, s, size=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["body"], color=color or T["text"], font=F_BODY,
                spacing=kw.pop("spacing", 1.4), **kw)


def gold_rule(slide, x, y, w, alpha=0.8, width=1.0):
    return line(slide, x, y, x + w, y, T["gold"], width, alpha=alpha)


def streak(slide, cx, cy, w=9, h=0.9):
    return pic_c(slide, X.light_streak("FFE2A0", alpha=0.55), cx, cy, w, h, name="Streak")


# ------------------------------------------------------------------ 版式
def cover(prs, title, sub, info, img, event, focus=(0.5, 0.5)):
    s = photo_bg(prs, img, focus, dark=0.5, side="left")
    pic(s, X.vignette_png(color=T["bg"], strength=0.7), 0, 0, SW, SH, name="Vignette")
    body(s, 0.85, 0.6, 8, 0.4, event, size=SIZE["small"], color=T["gold_light"], letter=150)
    gold_rule(s, 0.85, 1.05, 0.9)
    streak(s, 4.3, 3.35, 9.5, 1.0)
    cal(s, 0.6, 1.4, 10.5, 3.0, title, size=SIZE["mega"], anchor="m")
    body(s, 0.9, 4.25, 8.5, 0.6, sub, size=SIZE["lead"], color=T["ink"], letter=60)
    x = 0.9
    for i, it in enumerate(info):
        if i: line(s, x - 0.25, 5.72, x - 0.25, 6.05, T["gold"], 1.0, alpha=0.7)
        body(s, x, 5.65, 3.4, 0.45, it, size=SIZE["small"] + 1, color=T["muted"])
        x += 0.25 + len(it) * 0.205 + 0.3
    return s


def pain(prs, heading, items, img, focus=(0.5, 0.5)):
    """左照片右数据：三条『大数字 + 一句话』，金色细线分隔"""
    s = plain(prs)
    pic(s, grade(img, 5.4, SH, focus=focus, sat=0.9, contrast=1.08, tint=T["tint"], tint_amt=0.3), 0, 0, 5.4, SH)
    g = rect(s, 3.9, 0, 1.52, SH, fill=T["bg"]); set_gradient(g, [(0, T["bg"], 0.0), (1, T["bg"], 1.0)], 0)
    cal(s, 6.1, 0.65, 6.8, 1.2, heading, size=SIZE["h1"] + 4)
    y = 2.1
    for num, d in items:
        gold_rule(s, 6.15, y, 6.4, alpha=0.45, width=0.75)
        text(s, 6.15, y + 0.2, 2.6, 1.1, num, size=48, color=T["gold"], font=F_NUM, anchor="m")
        body(s, 8.9, y + 0.25, 3.7, 1.0, d, size=SIZE["body"], anchor="m")
        y += 1.5
    return s


def divider(prs, word, sub, img, focus=(0.5, 0.5)):
    s = photo_bg(prs, img, focus, dark=0.75)
    pic(s, X.vignette_png(color=T["bg"], strength=0.85, inner=0.3), 0, 0, SW, SH, name="Vignette")
    streak(s, SW / 2, 3.45, 11, 1.2)
    cal(s, 0.5, 1.4, SW - 1.0, 3.6, word, size=200, align="c", anchor="m")
    gold_rule(s, SW / 2 - 0.6, 5.25, 1.2)
    body(s, 0, 5.45, SW, 0.5, sub, size=SIZE["lead"] - 2, color=T["ink"], align="c", letter=300)
    return s


def solution(prs, heading, feats, img, focus=(0.5, 0.5)):
    s = photo_bg(prs, img, focus, dark=0.35, side="left")
    cal(s, 0.85, 0.7, 9.5, 1.2, heading, size=SIZE["h1"])
    y = 2.15
    for t, d in feats:
        gold_rule(s, 0.9, y, 5.6, alpha=0.5, width=0.75)
        body(s, 0.9, y + 0.2, 5.6, 0.5, t, size=SIZE["h2"] - 4, color=T["gold_light"], bold=True)
        body(s, 0.9, y + 0.75, 5.6, 0.7, d, size=SIZE["body"], color=T["text"])
        y += 1.5
    return s


def data(prs, heading, big_s, big_label, cats, vals, note):
    s = plain(prs)
    cal(s, 0.85, 0.65, 7, 1.2, heading, size=SIZE["h1"] + 4)
    text(s, 0.85, 2.2, 4.6, 1.6, big_s, size=96, color=T["gold"], font=F_NUM, anchor="b")
    body(s, 0.9, 3.9, 4.2, 0.6, big_label, size=SIZE["lead"] - 2, color=T["ink"])
    body(s, 0.9, 4.6, 4.0, 1.2, note, size=SIZE["small"], color=T["muted"])
    T2 = dict(T, accent=T["gold"], chart_gray="3E6B55", ink=T["ink"], text=T["text"], line="3E6B55")
    K.bar_chart(s, 5.9, 1.6, 6.6, 5.0, cats, vals, T2, highlight=len(vals) - 1, horizontal=False, fmt='0.0',
                label_size=14)
    return s


def gallery(prs, heading, items):
    s = plain(prs)
    cal(s, 0.85, 0.6, 8, 1.2, heading, size=SIZE["h1"] + 4)
    xs = [0.85, 4.95, 9.05]; w = 3.45; h = 3.9
    for i, (img, cap, fc) in enumerate(items):
        x = xs[i]; y = 2.0 if i != 1 else 1.7
        p = pic(s, grade(img, w, h, focus=fc, sat=0.95, contrast=1.05, tint=T["tint"], tint_amt=0.18), x, y, w, h)
        rect(s, x - 0.08, y - 0.08, w + 0.16, h + 0.16, line=T["gold"], line_w=0.75, line_alpha=0.6)
        body(s, x, y + h + 0.2, w, 0.5, cap, size=SIZE["small"] + 1, color=T["muted"])
    return s


def closing(prs, line_s, sub, img, focus=(0.5, 0.5)):
    s = photo_bg(prs, img, focus, dark=0.7)
    pic(s, X.vignette_png(color=T["bg"], strength=0.8), 0, 0, SW, SH, name="Vignette")
    streak(s, SW / 2, 3.2, 11, 1.1)
    cal(s, 0.5, 1.6, SW - 1.0, 3.0, line_s, size=SIZE["display"] + 8, align="c", anchor="m", spacing=1.15)
    body(s, 0, 5.2, SW, 0.5, sub, size=SIZE["body"], color=T["muted"], align="c", letter=200)
    return s


def build_demo(out):
    prs = new("green")
    cover(prs, "青禾计划", "AI 农情监测 · 让每一亩田都被看见", ["赛道：高教主赛道 · 创意组", "团队：示例团队", "指导老师：XXX"],
          "gs_terrace", "第 X 届中国国际大学生创新大赛 · 示例模板", focus=(0.5, 0.5))
    pain(prs, "看不见的损失", [("30%", "病虫害发现滞后，错过最佳防治窗口（示例数据）"),
                         ("6 小时", "人工巡田一次的平均耗时（示例数据）"),
                         ("1 : 800", "基层农技员与农户的服务比（示例数据）")], "gs_planting", focus=(0.5, 0.5))
    divider(prs, "看见", "解 决 方 案", "gs_field", focus=(0.5, 0.5))
    solution(prs, "一架无人机，一张农情图", [("多光谱巡田", "每日自动航拍，20 分钟覆盖 500 亩"),
                                     ("AI 病害识别", "叶片级识别 12 类常见病虫害"),
                                     ("处方图下发", "生成施药处方，精准到每一垄")], "gs_drone", focus=(0.6, 0.5))
    data(prs, "试点成效", "+18.6%", "试点区亩产提升", ["2023", "2024", "2025"], [512.0, 561.5, 607.2],
         "三个试点村、两季水稻的平均亩产（公斤），示例数据。")
    gallery(prs, "田间实证", [("gs_seedling", "育苗期长势监测", (0.5, 0.5)), ("gs_green", "温室环境数据采集", (0.5, 0.5)),
                          ("gs_terrace2", "梯田航拍建模", (0.5, 0.5))])
    closing(prs, "谢谢聆听\n恳请指导", "青禾计划 · 示例团队", "gs_terrace2", focus=(0.5, 0.5))
    return finish(prs, out, "风格 7 · 国赛金奖风", "满版照片统一深绿调 · 华文行楷金色发光标题（Office 字体，回退楷体）· 微软雅黑正文 · 金色细线")


if __name__ == "__main__":
    build_demo(os.path.join(STY, "guosai", "20261004-风格-国赛金奖.pptx"))
