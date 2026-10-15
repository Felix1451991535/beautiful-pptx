# -*- coding: utf-8 -*-
"""pptx -> PDF (LibreOffice) -> 逐页 PNG -> 总览拼图
用法: python3 render.py deck.pptx outdir [contact_sheet.png]"""
import os, sys, glob, subprocess, shutil
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from fontpath import cjk_font
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))


def render(pptx, outdir, sheet=None, dpi=110, cols=4):
    os.makedirs(outdir, exist_ok=True)
    env = dict(os.environ, FONTCONFIG_FILE=os.path.join(HERE, "fonts.conf"))
    prof = "-env:UserInstallation=file:///tmp/lo_pptkit_profile"
    subprocess.run(["soffice", prof, "--headless", "--convert-to", "pdf", "--outdir", outdir, pptx],
                   check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = os.path.join(outdir, os.path.splitext(os.path.basename(pptx))[0] + ".pdf")
    for f in glob.glob(os.path.join(outdir, "slide-*.png")): os.remove(f)
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, os.path.join(outdir, "slide")], check=True)
    pngs = sorted(glob.glob(os.path.join(outdir, "slide-*.png")))
    fonts = subprocess.run(["pdffonts", pdf], capture_output=True, text=True).stdout
    if sheet:
        contact_sheet(pngs, sheet, cols)
    return pdf, pngs, fonts


def contact_sheet(pngs, out, cols=4, tw=640, pad=28, label_h=34, bg="F3F6FA"):
    ims = [Image.open(p).convert("RGB") for p in pngs]
    th = int(tw * ims[0].height / ims[0].width)
    rows = (len(ims) + cols - 1) // cols
    W = cols * tw + (cols + 1) * pad; H = rows * (th + label_h) + (rows + 1) * pad
    sheet = Image.new("RGB", (W, H), "#" + bg); d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(cjk_font("sans"), 20)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad); y = pad + r * (th + label_h + pad)
        t = im.resize((tw, th), Image.LANCZOS)
        d.rectangle([x - 1, y - 1, x + tw, y + th], outline="#D9E2EC")
        sheet.paste(t, (x, y))
        d.text((x, y + th + 6), "%02d" % (i + 1), fill="#5B6B7F", font=font)
    sheet.save(out)
    return out


if __name__ == "__main__":
    pdf, pngs, fonts = render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print(pdf, len(pngs), "pages"); print(fonts)
