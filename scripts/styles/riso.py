# -*- coding: utf-8 -*-
"""风格 5 · 复古孔版 Risograph —— 两个专色（荧光粉 FF48B0 + 孔版蓝 0078BF）+ 网点照片 + 套印错位 + 粗体大字。
规则：全页只用纸色 + 两个专色（可选第三色黄 FFE800）；照片一律转成双色网点；大标题用"粉色底版 + 蓝色半透明压印"模拟错位套印。"""
from common import *          # noqa
import textures as X
from pptx.enum.dml import MSO_LINE

T = make_theme("riso", bg="F2EDE1", ink="0078BF", text="1D3F6E", muted="4F6E95", primary="0078BF",
               accent="FF48B0", dark="1D3F6E", on_dark="F2EDE1", on_dark_muted="DDD5C4", surface="F2EDE1",
               highlight="FF48B0", pink="FF48B0", blue="0078BF", yellow="FFE800")
F_HEAD = ("Impact", "黑体")                 # Windows 自带；中文标题用黑体（加粗）
F_ALT = ("Arial Black", "黑体")
F_BODY = ("Courier New", "仿宋")            # 打字机正文；中文正文用仿宋或等线
SIZE = dict(mega=150, display=110, h1=54, lead=22, body=16, meta=12)
MIS = (0.06, 0.035)                        # 套印错位（英寸）：粉版相对蓝版向右下偏移


def new():
    return new_deck(T, F_BODY[0], F_BODY[1])


def page(prs, grain=True):
    s = blank(prs, T["bg"])
    pic(s, X.washi(base=T["bg"], fibers=45, seed=21), 0, 0, SW, SH, name="Paper")
    return s


def grain_on(slide):
    """最上层的油墨颗粒/灰尘（最后调用）"""
    pic(slide, X.grain_overlay(dark="1D3F6E", density=0.006, alpha=0.35, seed=22), 0, 0, SW, SH, name="Grain")


def riso_text(slide, x, y, w, h, s, size=None, under=None, over=None, font=None, mis=MIS, over_alpha=0.88, **kw):
    """错位套印字：先印 under（粉）再印 over（蓝，半透明 → 叠色处发紫，像真实孔版叠印）"""
    under = under or T["pink"]; over = over or T["blue"]
    a = text(slide, x + mis[0], y + mis[1], w, h, s, size=size or SIZE["display"], color=under, font=font or F_HEAD,
             spacing=kw.get("spacing", 0.92), align=kw.get("align", "l"), anchor=kw.get("anchor", "t"), name="RisoUnder")
    paras = s.split("\n")
    b = text(slide, x, y, w, h, [[(p, {"alpha": over_alpha})] for p in paras], size=size or SIZE["display"], color=over,
             font=font or F_HEAD, spacing=kw.get("spacing", 0.92), align=kw.get("align", "l"),
             anchor=kw.get("anchor", "t"), name="RisoOver")
    return a, b


def mono(slide, x, y, w, h, s, size=None, color=None, **kw):
    return text(slide, x, y, w, h, s, size=size or SIZE["body"], color=color or T["text"], font=F_BODY,
                spacing=kw.pop("spacing", 1.35), **kw)


def halftone(slide, img, x, y, w, h, focus=(0.5, 0.5), block=True, **kw):
    """双色网点照片；block=True 时在下面垫一块错位的粉色实地（套印没对准的效果）"""
    if block:
        rect(slide, x + 0.14, y + 0.12, w, h, fill=T["pink"], alpha=0.9, name="MisregBlock")
    return pic(slide, X.riso_duotone(img, w, h, focus=focus, paper=T["bg"], **kw), x, y, w, h, name="Halftone")


# ------------------------------------------------------------------ 版式
def cover(prs, title, img, meta_s, focus=(0.5, 0.5)):
    s = page(prs)
    halftone(s, img, 7.1, 0.75, 5.5, 5.95, focus=focus)
    riso_text(s, 0.65, 1.0, 7.0, 4.2, title, size=SIZE["mega"] - 22, spacing=0.88, anchor="b")
    rect(s, 0.75, 5.55, 5.8, 0.08, fill=T["pink"])
    mono(s, 0.75, 5.8, 6.2, 0.9, meta_s, size=SIZE["meta"] + 2, color=T["blue"], letter=100)
    grain_on(s)
    return s


def intro(prs, heading, body_s, img, focus=(0.5, 0.5)):
    s = page(prs)
    pic(s, X.riso_duotone(img, 6.9, SH, focus=focus, paper=T["bg"]), 0, 0, 6.9, SH, name="Halftone")
    riso_text(s, 7.6, 0.95, 5.2, 1.9, heading, size=SIZE["h1"] + 10)
    mono(s, 7.65, 3.0, 4.9, 3.3, body_s, size=SIZE["body"] + 1)
    grain_on(s)
    return s


def big_number(prs, number, line_s, note):
    s = page(prs)
    pic(s, X.halftone_blob(T["pink"], 1000, 20), 6.3, -0.6, 7.6, 7.6, name="HalftoneBlob")
    riso_text(s, 0.6, 0.6, 12.6, 4.2, number, size=230, under=T["blue"], over=T["pink"], over_alpha=0.9)
    mono(s, 0.8, 4.95, 6.4, 1.1, line_s, size=SIZE["lead"] + 2, color=T["blue"], bold=True)
    mono(s, 0.8, 6.2, 6.4, 0.5, note, size=SIZE["meta"], color=T["muted"])
    grain_on(s)
    return s


def verbs(prs, items):
    """三个动词大字竖排堆叠，右侧打字机说明；颜色交替，不用编号"""
    s = page(prs)
    y = 0.45
    for i, (v, d) in enumerate(items):
        u, o = (T["pink"], T["blue"]) if i % 2 == 0 else (T["blue"], T["pink"])
        riso_text(s, 0.7, y, 7.0, 2.1, v, size=SIZE["display"] + 20, under=u, over=o)
        mono(s, 6.4, y + 0.6, 5.2, 1.2, d, size=SIZE["body"] + 2)
        if i < len(items) - 1:
            line(s, 6.4, y + 2.15, 12.0, y + 2.15, T["blue"], 1.0, dash=MSO_LINE.ROUND_DOT)
        y += 2.2
    grain_on(s)
    return s


def full_halftone(prs, img, word, focus=(0.5, 0.5)):
    s = page(prs)
    pic(s, X.riso_duotone(img, SW, SH, focus=focus, paper=T["bg"], cell=11, k1=0.75), 0, 0, SW, SH, name="Halftone")
    rect(s, 0.7, 4.75, 7.6, 2.0, fill=T["bg"])
    riso_text(s, 0.95, 4.75, 10.5, 2.0, word, size=SIZE["display"], anchor="m")
    grain_on(s)
    return s


def quote(prs, q, who):
    s = page(prs)
    pic(s, X.halftone_blob(T["blue"], 1000, 24, seed=3), 9.2, 3.6, 5.6, 5.6, name="HalftoneBlob")
    text(s, 1.0, 0.75, 1.5, 1.6, "“", size=160, color=T["pink"], font=F_HEAD)
    mono(s, 2.3, 1.3, 9.6, 3.6, q, size=32, color=T["blue"], bold=True, spacing=1.3, anchor="m")
    mono(s, 2.35, 5.15, 9.0, 0.5, who, size=SIZE["body"], color=T["pink"], bold=True)
    grain_on(s)
    return s


def closing(prs, title, info, img, focus=(0.5, 0.5)):
    s = page(prs)
    halftone(s, img, 8.6, 0.0, 4.73, SH, focus=focus, block=False, c1=T["pink"], c2=T["blue"])
    riso_text(s, 0.65, 0.7, 7.8, 4.4, title, size=SIZE["display"] + 10, spacing=0.9)
    rect(s, 0.75, 5.25, 0.9, 0.9, fill=T["yellow"], alpha=0.95)
    mono(s, 1.9, 5.25, 6.2, 1.2, info, size=SIZE["body"] + 1, color=T["blue"], bold=True)
    grain_on(s)
    return s


def build_demo(out):
    prs = new()
    cover(prs, "GROW\nTOGETHER", "riso_harvest", "ROOFTOP GARDEN CLUB\nZINE NO. 04 — SPRING 2026", focus=(0.55, 0.5))
    intro(prs, "WHO\nWE ARE", "Forty neighbours, one flat roof, and too many seeds.\n\nWe meet every Saturday to dig, water, swap cuttings and drink terrible coffee. No experience needed.",
          "riso_roof", focus=(0.45, 0.5))
    big_number(prs, "312 KG", "of tomatoes shared with the building last summer", "Sample numbers for layout only.")
    verbs(prs, [("DIG", "Turn the beds in March. Bring gloves; we have spades."),
                ("SOW", "Seeds go in by April. Label everything — trust us."),
                ("SHARE", "Harvest goes on the lobby table. Take what you need.")])
    full_halftone(prs, "riso_tomato", "EAT LOCAL", focus=(0.5, 0.5))
    quote(prs, "Nobody here is an expert. We just keep showing up, and the garden keeps forgiving us.", "— Ana, 3rd floor")
    closing(prs, "SEE YOU\nSATURDAY", "Every Sat · 9:00 am\nRooftop, Block C\nBring a mug.", "riso_crates", focus=(0.5, 0.5))
    return finish(prs, out, "风格 5 · 复古孔版 Risograph", "纸色 + 荧光粉 #FF48B0 + 孔版蓝 #0078BF · 双色网点照片 · 套印错位 · Impact / Courier New")


if __name__ == "__main__":
    build_demo(os.path.join(STY, "riso", "20261004-风格-复古孔版.pptx"))
