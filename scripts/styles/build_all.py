# -*- coding: utf-8 -*-
"""一键：生成 7 套示例 deck → LibreOffice 渲染 → 每套总览 → check.py + OOXML 校验 → 风格库汇总对比图。
用法：python3 scripts/styles/build_all.py [风格名 ...]"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter
from common import STY, validate, _font
import styles_registry as R

OUT = {
    "scrapbook": "scrapbook/20261004-风格-手账拼贴.pptx", "editorial": "editorial/20261004-风格-杂志留白.pptx",
    "aurora": "aurora/20261004-风格-深色极光.pptx", "glass": "glass/20261004-风格-通透玻璃.pptx",
    "riso": "riso/20261004-风格-复古孔版.pptx", "japanese": "japanese/20261004-风格-日式留白.pptx",
    "guosai": "guosai/20261004-风格-国赛金奖.pptx",
}
PICK = {"scrapbook": [1, 3, 5, 6], "editorial": [1, 3, 5, 7], "aurora": [1, 3, 4, 6], "glass": [1, 3, 4, 5],
        "riso": [1, 3, 4, 5], "japanese": [1, 4, 5, 6], "guosai": [1, 2, 3, 5]}


def summary(results, out):
    tw, pad, lab = 520, 24, 300
    th = int(tw * 9 / 16)
    W = lab + 4 * tw + 5 * pad; head = 110
    H = head + len(results) * (th + pad) + pad
    im = Image.new("RGB", (W, H), "#ECEAE4"); d = ImageDraw.Draw(im)
    d.text((pad, 26), "pptkit 风格库总览 · 7 套可编辑风格预设", fill="#222", font=_font(40, True))
    d.text((pad, 78), "全部 python-pptx 生成、可编辑；照片来自 Pexels，纹理/光效均为程序生成（预览字体为开源近似字体，Windows 下以说明书所列字体为准）",
           fill="#666", font=_font(18))
    for r, (key, pngs) in enumerate(results):
        y = head + r * (th + pad)
        cn = R.STYLES[key]["cn"]
        d.text((pad, y + 10), "%d  %s" % (r + 1, cn), fill="#222", font=_font(30, True))
        d.text((pad, y + 56), key, fill="#888", font=_font(18))
        fits = R.STYLES[key]["fits"].split("、")[:4]
        for i, f in enumerate(fits):
            d.text((pad, y + 96 + i * 26), "· " + f, fill="#555", font=_font(16))
        for c, p in enumerate(pngs):
            x = lab + pad + c * (tw + pad)
            t = Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS)
            sh = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rectangle([10, 12, tw + 10, th + 12], fill=(0, 0, 0, 55))
            sh = sh.filter(ImageFilter.GaussianBlur(6)); im.paste(sh, (x - 10, y - 8), sh)
            im.paste(t, (x, y))
    im.save(out)
    return out


def main(names):
    report = {}
    for key in names:
        mod = R.get_style(key)
        out = os.path.join(STY, OUT[key])
        pdf, pngs, ov = mod.build_demo(out)
        issues, ok, outp = validate(out, pdf)
        report[key] = dict(pptx=out, pages=len(pngs), overview=ov, check_issues=issues, ooxml_ok=ok)
        print("==", key, "pages", len(pngs), "check issues", len(issues), "ooxml", ok)
        for i in issues: print("   ", i)
        if not ok: print(outp[:2000])
    rows = []
    for key in R.STYLES:
        rd = os.path.join(STY, os.path.dirname(OUT[key]), "render")
        if os.path.isdir(rd):
            rows.append((key, [os.path.join(rd, "slide-%d.png" % i) for i in PICK[key]]))
    print(summary(rows, os.path.join(STY, "20261004-风格库总览.png")))
    json.dump(report, open(os.path.join(STY, "build_report.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv[1:] or list(R.STYLES))
