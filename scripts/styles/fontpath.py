"""Locate a CJK font file portably: env override → common Noto paths → fc-match."""
import os, subprocess
_C = {"sans": ["/usr/share/fonts/opentype/noto/NotoSansCJK-{w}.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-{w}.ttc",
               "/System/Library/Fonts/PingFang.ttc", "C:/Windows/Fonts/msyh.ttc"],
      "serif": ["/usr/share/fonts/opentype/noto/NotoSerifCJK-{w}.ttc", "/usr/share/fonts/noto-cjk/NotoSerifCJK-{w}.ttc",
                "C:/Windows/Fonts/simsun.ttc"]}


def cjk_font(kind="sans", bold=False):
    env = os.environ.get("PPTKIT_%s_FONT" % kind.upper())
    if env and os.path.exists(env):
        return env
    for p in _C[kind]:
        p = p.format(w="Bold" if bold else "Regular")
        if os.path.exists(p):
            return p
    fam = "Noto %s CJK SC:%s" % ("Serif" if kind == "serif" else "Sans", "bold" if bold else "regular")
    try:
        p = subprocess.run(["fc-match", "-f", "%{file}", fam], capture_output=True, text=True).stdout.strip()
        if p and os.path.exists(p):
            return p
    except FileNotFoundError:
        pass
    if kind == "serif":
        return cjk_font("sans", bold)
    raise FileNotFoundError("No CJK font found; install fonts-noto-cjk or set PPTKIT_SANS_FONT")
