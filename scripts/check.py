# -*- coding: utf-8 -*-
"""交付前自动检查：文字溢出(估算)、越界、字号过小、主题对比度、切换/动画统计、PDF 字体
用法: python3 check.py deck.pptx [render.pdf]
估算采用 Noto Sans CJK 字宽 + 1.45 倍行高（比微软雅黑 1.32 更保守）"""
import sys, subprocess
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from fontpath import cjk_font
from pptx import Presentation
from pptx.util import Emu
from pptx.oxml.ns import qn
from PIL import ImageFont

FR = cjk_font("sans")
FB = cjk_font("sans", True)
_cache = {}


def font(sz, b):
    k = (round(sz), b)
    if k not in _cache: _cache[k] = ImageFont.truetype(FB if b else FR, max(1, round(sz * 4)))  # 4x 精度
    return _cache[k]


def text_height(tf, width_pt):
    total = 0.0
    for p in tf.paragraphs:
        runs = p.runs
        sizes = [r.font.size.pt if r.font.size else 18 for r in runs] or [18]
        ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
        lh = max(sizes) * 1.45 * ls
        lines, cur = 1, 0.0
        for r in runs:
            sz = r.font.size.pt if r.font.size else 18
            f = font(sz, bool(r.font.bold))
            for ch in r.text:
                w = f.getlength(ch) / 4
                if cur + w > width_pt + 0.5 and cur > 0:
                    lines += 1; cur = w
                else:
                    cur += w
        sa = p.space_after.pt if p.space_after is not None else 0
        sb = p.space_before.pt if p.space_before is not None else 0
        total += lines * lh + sa + sb
    return total


def walk(shapes):
    for s in shapes:
        if s.shape_type == 6:  # group
            yield from walk(s.shapes)
        else:
            yield s


def main(path, pdf=None):
    prs = Presentation(path)
    SW, SH = prs.slide_width, prs.slide_height
    issues = []
    for i, sl in enumerate(prs.slides, 1):
        tr = sl._element.find(".//" + qn("p:transition")) is not None or b"AlternateContent" in sl._element.xml.encode()
        anims = len(sl._element.findall(".//" + qn("p:animEffect")))
        print("p%02d  切换:%s  动画效果数:%d" % (i, "有" if tr else "无", anims))
        for s in walk(sl.shapes):
            if s.left is None: continue
            if s.left < -Emu(10000) or s.top < -Emu(10000) or s.left + s.width > SW + 10000 or s.top + s.height > SH + 10000:
                issues.append("p%02d 越界: %s" % (i, s.name))
            if not s.has_text_frame or not s.text_frame.text.strip(): continue
            tf = s.text_frame
            for p in tf.paragraphs:
                for r in p.runs:
                    if r.font.size and r.font.size.pt < 10 and r.text.strip() and "图片" not in r.text and "#" not in r.text:
                        issues.append("p%02d 字号<10pt: %s '%s'" % (i, s.name, r.text[:12]))
            ins = (tf.margin_left + tf.margin_right) / 12700
            w = s.width / 12700 - ins
            have = (s.height - tf.margin_top - tf.margin_bottom) / 12700
            if tf._txBody.find(qn("a:bodyPr")).get("vert") in ("eaVert", "vert", "vert270", "mongolianVert", "wordArtVert", "wordArtVertRtl"):
                # 竖排文本：列沿高度方向排，换列沿宽度方向推进 → 宽高互换后估算
                w, have = s.height / 12700 - (tf.margin_top + tf.margin_bottom) / 12700, s.width / 12700 - ins
            need = text_height(tf, w)
            if need > have * 1.02 + 2:
                issues.append("p%02d 可能溢出: %s 需要%.0fpt / 框高%.0fpt  '%s'" % (i, s.name, need, have, tf.text[:16].replace("\n", " ")))
    print("\n== 问题 ==" if issues else "\n== 未发现溢出/越界/过小字号 ==")
    for x in issues: print(" -", x)
    if pdf:
        out = subprocess.run(["pdffonts", pdf], capture_output=True, text=True).stdout
        print("\n== PDF 字体 ==\n" + out)
    return issues


def contrast(a, b):
    def L(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = sorted([L(a), L(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


def theme_report(T):
    pairs = [("ink", "bg", 4.5), ("text", "bg", 4.5), ("muted", "bg", 4.5), ("muted", "surface", 4.5),
             ("accent_text", "bg", 4.5), ("primary", "bg", 4.5), ("accent", "bg", 3.0),
             ("on_dark", "dark", 4.5), ("on_dark_muted", "dark", 4.5), ("accent_on_dark", "dark", 3.0)]
    rows = []
    for a, b, need in pairs:
        r = contrast(T[a], T[b]); rows.append((a, b, round(r, 2), need, "OK" if r >= need else "FAIL"))
    if not T["dark_mode"]:
        r = contrast("FFFFFF", T["primary"]); rows.append(("white", "primary", round(r, 2), 4.5, "OK" if r >= 4.5 else "FAIL"))
    return rows


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    sys.path.insert(0, __import__("os").path.dirname(__file__))
    from pptkit import THEMES
    for k, T in THEMES.items():
        print("\n主题", k, T["name"], "对比度(WCAG)：")
        for row in theme_report(T): print("  %-14s on %-8s %5.2f (≥%.1f) %s" % row)
