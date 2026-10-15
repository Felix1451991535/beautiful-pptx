# -*- coding: utf-8 -*-
"""手账拼贴素材（全部程序生成，无 AI 图）：旧纸背景 / 拍立得相纸+半透明胶带 / 撕纸片 / 手绘箭头
照片用下方 grade() 统一调色。输出 assets/scrap/*.png|jpg"""
import os, math, random, json
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
RAW, OUT = os.path.join(HERE, "..", "..", "styles", "assets", "raw"), os.path.join(HERE, "assets/scrap")
from PIL import ImageFilter
GRADE = dict(sat=0.72, contrast=0.94, lift=16, grain=0.03, shift=(7, 2, -7))


def grade(im, sat=None):
    g = dict(GRADE, sat=sat or GRADE["sat"])
    im = ImageEnhance.Color(im).enhance(g["sat"])
    im = ImageEnhance.Contrast(im).enhance(g["contrast"])
    lut = [int(g["lift"] + v * (250 - g["lift"]) / 255) for v in range(256)]   # 抬黑位 + 压白点 = 哑光
    chans = [ch.point([min(255, max(0, x + s)) for x in lut]) for ch, s in zip(im.split(), g["shift"])]
    im = Image.merge("RGB", chans)
    if g["grain"]:
        n = Image.effect_noise(im.size, 48).convert("L").filter(ImageFilter.GaussianBlur(0.5))
        im = Image.blend(im, Image.merge("RGB", (n, n, n)), g["grain"])
    return im

DPI = 100          # PNG 素材（相框/纸片/贴纸）分辨率；照片 JPG 单独用 PDPI
PDPI = 150
PP = lambda v: int(round(v * PDPI))
SW, SH = 13.333, 7.5
P = lambda v: int(round(v * DPI))


def noise(w, h, scale, seed, blur=0):
    """低频噪声：小图随机→放大"""
    rnd = random.Random(seed)
    sw, sh = max(2, int(w / scale)), max(2, int(h / scale))
    im = Image.new("L", (sw, sh)); im.putdata([rnd.randint(0, 255) for _ in range(sw * sh)])
    im = im.resize((w, h), Image.BICUBIC)
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im


# ------------------------------------------------------------------ 背景：米色旧纸（褶皱+污渍+暗角+颗粒）
def old_paper(seed=3):
    W, H = P(SW), P(SH)
    base = Image.new("RGB", (W, H), (234, 223, 201))
    rnd = random.Random(seed)
    # 大块深浅（旧纸不均匀）
    blot = noise(W, H, 160, seed, 30)
    dark = Image.new("RGB", (W, H), (214, 197, 166))
    base = Image.composite(dark, base, blot.point(lambda v: int(max(0, v - 120) * 0.9)))
    # 褶皱：随机折线，一侧亮一侧暗
    crease = Image.new("L", (W, H), 128); d = ImageDraw.Draw(crease)
    for _ in range(26):
        x, y = rnd.uniform(-0.1, 1.1) * W, rnd.uniform(-0.1, 1.1) * H
        a = rnd.uniform(0, math.pi); L = rnd.uniform(0.25, 0.9) * W
        pts = []
        for k in range(8):
            a += rnd.uniform(-0.25, 0.25)
            pts.append((x, y)); x += math.cos(a) * L / 7; y += math.sin(a) * L / 7
        sh = rnd.choice([-1, 1]) * rnd.randint(10, 22)
        d.line([(px, py + 2) for px, py in pts], fill=128 - sh, width=2)
        d.line(pts, fill=128 + sh, width=2)
    crease = crease.filter(ImageFilter.GaussianBlur(1.6))
    hi = Image.new("RGB", (W, H), (248, 241, 226)); lo = Image.new("RGB", (W, H), (196, 178, 146))
    base = Image.composite(hi, base, crease.point(lambda v: int(max(0, v - 128) * 5)))
    base = Image.composite(lo, base, crease.point(lambda v: int(max(0, 128 - v) * 4)))
    # 细纤维 + 颗粒
    fib = noise(W, H, 2, seed + 1).filter(ImageFilter.GaussianBlur(0.6))
    g = Image.merge("RGB", (fib, fib, fib))
    base = Image.blend(base, ImageChops.multiply(base, g.point(lambda v: 150 + v // 3)), 0.25)
    # 暗角（边缘发黄发暗）
    vig = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vig)
    for i in range(60):
        t = i / 60; dv.rectangle([P(0.0) + i * 6, i * 6, W - i * 6, H - i * 6], outline=int(255 * (1 - t) ** 2.2))
    vig = vig.filter(ImageFilter.GaussianBlur(40))
    base = Image.composite(Image.new("RGB", (W, H), (190, 165, 125)), base, vig.point(lambda v: int(v * 0.55)))
    base = base.resize((1600, 900), Image.LANCZOS)
    out = os.path.join(OUT, "paper_bg.jpg"); base.save(out, "JPEG", quality=82, progressive=False); return out


# ------------------------------------------------------------------ 胶带
def tape(w, h, seed, color=(236, 226, 196), alpha=165, plain=False):
    rnd = random.Random(seed)
    im = Image.new("RGBA", (w, h), color + (alpha,))
    tex = noise(w, h, 3, seed, 0.8)
    streak = noise(w, max(2, h // 8), 1, seed + 5).resize((w, h), Image.BICUBIC)
    a = Image.blend(tex, streak, 0.5).point(lambda v: int(alpha - 22 + v * 44 / 255))
    if plain: a = streak.point(lambda v: int(alpha - 12 + v * 24 / 255))
    # 锯齿状撕口（左右两端）
    m = Image.new("L", (w, h), 255); d = ImageDraw.Draw(m)
    for side in (0, 1):
        pts, y = [], 0
        while y < h:
            dx = rnd.randint(0, max(2, w // 40)); pts.append((dx if side == 0 else w - 1 - dx, y)); y += rnd.randint(3, 7)
        poly = ([(0, 0)] + pts + [(0, h)]) if side == 0 else ([(w, 0)] + pts + [(w, h)])
        d.polygon(poly, fill=0)
    im.putalpha(ImageChops.multiply(a, m))
    # 轻微高光
    hl = Image.new("RGBA", (w, h), (255, 255, 250, 0)); dh = ImageDraw.Draw(hl)
    dh.rectangle([0, int(h * 0.15), w, int(h * 0.3)], fill=(255, 255, 250, 28))
    return Image.alpha_composite(im, hl)


def paste_rot(canvas, piece, cx, cy, angle):
    """piece 以 (cx,cy) 为中心、顺时针 angle 度贴到 canvas"""
    r = piece.rotate(-angle, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(r, (int(cx - r.width / 2), int(cy - r.height / 2)))


def shadowed(im, angle, off=(0.03, 0.06), blur=0.06, op=0.38):
    """整体旋转 + 投影；返回 RGBA"""
    r = im.rotate(-angle, resample=Image.BICUBIC, expand=True)
    pad = P(0.25)
    out = Image.new("RGBA", (r.width + 2 * pad, r.height + 2 * pad), (0, 0, 0, 0))
    a = r.split()[3].point(lambda v: int(v * op))
    sh = Image.new("RGBA", r.size, (60, 42, 25, 0)); sh.putalpha(a)
    shl = Image.new("RGBA", out.size, (0, 0, 0, 0)); shl.alpha_composite(sh, (pad + P(off[0]), pad + P(off[1])))
    shl = shl.filter(ImageFilter.GaussianBlur(P(blur)))
    out.alpha_composite(shl); out.alpha_composite(r, (pad, pad))
    # 裁掉透明边，记录"原中心 - 新中心"偏移，PPT 放置时用来还原卡片中心
    bx = out.split()[3].point(lambda v: 255 if v > 6 else 0).getbbox()
    global LAST_OFF
    LAST_OFF = ((out.width / 2 - (bx[0] + bx[2]) / 2) / DPI, (out.height / 2 - (bx[1] + bx[3]) / 2) / DPI)
    return out.crop(bx)


META = {}
LAST_OFF = (0, 0)


def polaroid(name, pid, pw, ph, angle, focus=(0.5, 0.5), tapes=("tl", "br"), sat=None, seed=1, bottom=None):
    """拍立得 = 不透明 JPG 照片（PPT 里用标准 rotation 旋转）+ 轻量 PNG 相框（白边/胶带/投影已烘焙、照片区挖空、调色板压缩）。
    tapes: tl/tr/bl/br/top"""
    b = 0.13 if pw > 2.2 else 0.1
    bb = bottom if bottom is not None else (b * 3.2)
    W, H = P(pw + 2 * b), P(ph + b + bb)
    bleed = 0.04
    ph_im = Image.open(os.path.join(RAW, "%s.jpg" % pid)).convert("RGB")
    ph_im = ImageOps.fit(ph_im, (PP(pw + 2 * bleed), PP(ph + 2 * bleed)), Image.LANCZOS, centering=focus)
    ph_im = grade(ph_im, sat)
    ph_im.save(os.path.join(OUT, name + "_photo.jpg"), "JPEG", quality=84, progressive=False)   # 标准 baseline JPG
    tp = P(0.5)
    CW, CH = W + 2 * tp, H + 2 * tp
    card = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    card.paste(Image.new("RGBA", (W, H), (250, 247, 240, 255)), (tp, tp))
    hole = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(hole).rectangle([tp + P(b), tp + P(b), tp + P(b) + P(pw) - 1, tp + P(b) + P(ph) - 1], fill=255)
    tl = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    rnd = random.Random(seed)
    tw, th = P(min(1.5, max(1.0, pw * 0.42))), P(0.36)
    pos = dict(tl=(tp, tp, -38), tr=(tp + W, tp, 38), bl=(tp, tp + H, 38), br=(tp + W, tp + H, -38),
               top=(tp + W / 2, tp + P(0.02), 0))
    for k, t in enumerate(tapes):
        x, y, a = pos[t]
        paste_rot(tl, tape(tw, th, seed * 10 + k, alpha=150, plain=True), x, y, a + rnd.uniform(-6, 6))
    rc = card.rotate(-angle, resample=Image.BICUBIC, expand=True)
    rh = hole.rotate(-angle, resample=Image.NEAREST, expand=True)
    rt = tl.rotate(-angle, resample=Image.BICUBIC, expand=True)
    pad = P(0.25)
    S = (rc.width + 2 * pad, rc.height + 2 * pad)
    sh_a = Image.new("L", S, 0); sh_a.paste(rc.split()[3].point(lambda v: int(v * 0.38)), (pad + P(0.03), pad + P(0.06)))
    sh_a = sh_a.filter(ImageFilter.GaussianBlur(P(0.06)))
    out = Image.new("RGBA", S, (60, 42, 25, 0)); out.putalpha(sh_a)
    out.alpha_composite(rc, (pad, pad))
    hole_full = Image.new("L", S, 0); hole_full.paste(rh, (pad, pad))
    out.putalpha(ImageChops.subtract(out.split()[3], hole_full))          # 照片区挖空（无阴影、无白底）
    out.alpha_composite(rt, (pad, pad))                                   # 胶带最后贴，可盖住照片角
    bx = out.split()[3].point(lambda v: 255 if v > 6 else 0).getbbox()
    off = ((out.width / 2 - (bx[0] + bx[2]) / 2) / DPI, (out.height / 2 - (bx[1] + bx[3]) / 2) / DPI)
    out = out.crop(bx)
    f = os.path.join(OUT, name + ".png"); compact_png(out).save(f, optimize=True)
    th_ = math.radians(angle)
    cy_off = (H / 2 - P(bb) / 2) / DPI                      # 卡片中心 → 底条中心（未旋转）
    py_off = (b - bb) / 2                                   # 卡片中心 → 照片中心（未旋转）
    META[name] = dict(w=out.width / DPI, h=out.height / DPI, angle=angle, off=off,
                      card_w=W / DPI, card_h=H / DPI, strip_h=bb,
                      strip_dx=-cy_off * math.sin(th_), strip_dy=cy_off * math.cos(th_),
                      photo=name + "_photo.jpg", photo_w=pw + 2 * bleed, photo_h=ph + 2 * bleed,
                      photo_dx=-py_off * math.sin(th_), photo_dy=py_off * math.cos(th_))
    return f


def compact_png(im):
    """标准 8bit RGBA PNG（兼容性铁律：不用调色板 PNG）；体积靠 100dpi + 低噪纹理控制"""
    return im.convert("RGBA")


def scrap(name, kind, w, h, angle, seed=1, torn="tb", tapes=()):
    """撕纸片：kind = lined(横线笔记纸) | kraft(牛皮纸) | white(白纸) | grid(方格纸)"""
    rnd = random.Random(seed)
    W, H = P(w), P(h)
    col = dict(lined=(250, 248, 242), kraft=(196, 162, 118), white=(249, 246, 238), grid=(248, 246, 240))[kind]
    im = Image.new("RGB", (W, H), col)
    tex = noise(W, H, 6, seed, 1.5)
    im = Image.blend(im, ImageChops.multiply(im, Image.merge("RGB", [tex.point(lambda v: 200 + v // 5)] * 3)),
                     0.6 if kind == "kraft" else 0.25)
    d = ImageDraw.Draw(im)
    if kind == "lined":
        for y in range(P(0.55), H, P(0.3)): d.line([(0, y), (W, y)], fill=(170, 190, 205), width=2)
        d.line([(P(0.45), 0), (P(0.45), H)], fill=(214, 150, 140), width=2)
    if kind == "grid":
        for y in range(0, H, P(0.2)): d.line([(0, y), (W, y)], fill=(205, 212, 214), width=1)
        for x in range(0, W, P(0.2)): d.line([(x, 0), (x, H)], fill=(205, 212, 214), width=1)
    # 撕边：沿指定边做不规则锯齿 + 白色纤维边
    m = Image.new("L", (W, H), 255); dm = ImageDraw.Draw(m)
    def edge(side):
        pts, t, n = [], 0, W if side in "tb" else H
        amp = P(0.07)
        while t <= n:
            o = rnd.randint(0, amp)
            if side == "t": pts.append((t, o))
            if side == "b": pts.append((t, H - 1 - o))
            if side == "l": pts.append((o, t))
            if side == "r": pts.append((W - 1 - o, t))
            t += rnd.randint(4, 12)
        if side == "t": poly = [(0, 0)] + pts + [(W, 0)]
        if side == "b": poly = [(0, H)] + pts + [(W, H)]
        if side == "l": poly = [(0, 0)] + pts + [(0, H)]
        if side == "r": poly = [(W, 0)] + pts + [(W, H)]
        dm.polygon(poly, fill=0)
    for sd in torn: edge(sd)
    m = m.filter(ImageFilter.GaussianBlur(0.7))
    piece = im.convert("RGBA"); piece.putalpha(m)
    tp = P(0.5)
    card = Image.new("RGBA", (W + 2 * tp, H + 2 * tp), (0, 0, 0, 0)); card.alpha_composite(piece, (tp, tp))
    tw, th = P(1.25), P(0.34)
    pos = dict(tl=(tp + P(0.1), tp + P(0.05), -35), tr=(tp + W - P(0.1), tp + P(0.05), 35), top=(tp + W / 2, tp, -2),
               left=(tp, tp + H / 2, 88), right=(tp + W, tp + H / 2, 92))
    for k, t in enumerate(tapes):
        x, y, a = pos[t]; paste_rot(card, tape(tw, th, seed * 7 + k), x, y, a + rnd.uniform(-5, 5))
    out = shadowed(card, angle, off=(0.02, 0.035), blur=0.04, op=0.28)
    f = os.path.join(OUT, name + ".png"); compact_png(out).save(f, optimize=True)
    META[name] = dict(w=out.width / DPI, h=out.height / DPI, angle=angle, off=LAST_OFF)
    return f


def strip(name, w, angle, seed=1):
    """单独一条胶带（贴在文字上的那种），可放字"""
    t = tape(P(w), P(0.62), seed, color=(232, 218, 176), alpha=200)
    card = Image.new("RGBA", (t.width + P(0.4), t.height + P(0.4)), (0, 0, 0, 0)); card.alpha_composite(t, (P(0.2), P(0.2)))
    out = shadowed(card, angle, off=(0.01, 0.02), blur=0.03, op=0.12)
    f = os.path.join(OUT, name + ".png"); compact_png(out).save(f); META[name] = dict(w=out.width / DPI, h=out.height / DPI, angle=angle, off=LAST_OFF)
    return f


def hand_line(name, pts_in, color=(166, 50, 38), width=0.045, head=True, seed=1, curve=False):
    """手绘箭头/下划线：折线加抖动，两遍描边模拟马克笔"""
    rnd = random.Random(seed)
    xs = [p[0] for p in pts_in]; ys = [p[1] for p in pts_in]
    pad = 0.3
    x0, y0 = min(xs) - pad, min(ys) - pad
    W, H = P(max(xs) - x0 + pad), P(max(ys) - y0 + pad)
    S = 3  # 超采样
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    def tr(p): return ((p[0] - x0) * DPI * S, (p[1] - y0) * DPI * S)
    pts = [tr(p) for p in pts_in]
    # 细分 + 抖动
    dense = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(bx - ax, by - ay) / (12 * S)))
        for k in range(n):
            t = k / n
            dense.append((ax + (bx - ax) * t + rnd.uniform(-1, 1) * S * 0.8, ay + (by - ay) * t + rnd.uniform(-1, 1) * S * 0.8))
    dense.append(pts[-1])
    if curve and len(dense) > 4:   # 平滑
        sm = [dense[0]]
        for i in range(1, len(dense) - 1):
            sm.append(((dense[i - 1][0] + dense[i][0] * 2 + dense[i + 1][0]) / 4, (dense[i - 1][1] + dense[i][1] * 2 + dense[i + 1][1]) / 4))
        sm.append(dense[-1]); dense = sm
    lw = int(width * DPI * S)
    c = color + (235,)
    d.line(dense, fill=c, width=lw, joint="curve")
    for p in (dense[0], dense[-1]): d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=c)
    if head:
        (ax, ay), (bx, by) = dense[-4], dense[-1]
        ang = math.atan2(by - ay, bx - ax); L = 0.2 * DPI * S
        for s_ in (1, -1):
            a = ang + math.pi - s_ * 0.5 + rnd.uniform(-0.05, 0.05)
            e = (bx + math.cos(a) * L, by + math.sin(a) * L)
            d.line([e, (bx, by)], fill=c, width=lw)
            d.ellipse([e[0] - lw / 2, e[1] - lw / 2, e[0] + lw / 2, e[1] + lw / 2], fill=c)
    im = im.resize((W, H), Image.LANCZOS)
    f = os.path.join(OUT, name + ".png"); compact_png(im).save(f, optimize=True)
    META[name] = dict(w=W / DPI, h=H / DPI, x0=x0, y0=y0)
    return f


def _finish(name, im, angle, op=0.25, off=(0.02, 0.04), blur=0.04, **meta):
    out = shadowed(im, angle, off=off, blur=blur, op=op)
    f = os.path.join(OUT, name + ".png"); compact_png(out).save(f, optimize=True)
    META[name] = dict(w=out.width / DPI, h=out.height / DPI, angle=angle, off=LAST_OFF, **meta)
    return f


def sticky(name, w, h, angle, color=(240, 224, 152), seed=1, tape_on=False):
    """便利贴：浅黄方块，底部微卷（渐暗），可加一条胶带"""
    W, H = P(w), P(h); tp = P(0.4)
    card = Image.new("RGBA", (W + 2 * tp, H + 2 * tp), (0, 0, 0, 0))
    note = Image.new("RGB", (W, H), color)
    g = Image.new("L", (W, H), 0); dg = ImageDraw.Draw(g)
    for y in range(int(H * 0.7), H): dg.line([(0, y), (W, y)], fill=int(40 * ((y - H * 0.7) / (H * 0.3)) ** 2))
    note = Image.composite(Image.new("RGB", (W, H), tuple(int(c * 0.85) for c in color)), note, g)
    card.paste(note, (tp, tp))
    if tape_on: paste_rot(card, tape(P(0.9), P(0.3), seed, alpha=150, plain=True), tp + W / 2, tp + P(0.02), random.Random(seed).uniform(-6, 6))
    return _finish(name, card, angle, op=0.3, off=(0.03, 0.06), blur=0.06)


def sticker(name, d, angle=0, color=(166, 50, 38)):
    """圆形贴纸：砖红实心圆 + 内圈细白线（文字由 PPT 写）"""
    S = 3; D = P(d) * S; tp = P(0.15) * S
    im = Image.new("RGBA", (D + 2 * tp, D + 2 * tp), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.ellipse([tp, tp, tp + D, tp + D], fill=color + (255,))
    k = int(D * 0.06); dr.ellipse([tp + k, tp + k, tp + D - k, tp + D - k], outline=(250, 240, 228, 230), width=max(2, int(D * 0.012)))
    im = im.resize((im.width // S, im.height // S), Image.LANCZOS)
    return _finish(name, im, angle, op=0.3, off=(0.02, 0.04), blur=0.03)


def ticket(name, w, h, angle, seed=1):
    """票根：牛皮纸 + 两侧半圆缺口 + 砖红虚线框（文字由 PPT 用 Courier New 写）"""
    S = 2; W, H = P(w) * S, P(h) * S
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, W, H], fill=(214, 186, 140, 255))
    r = int(H * 0.16)
    for x in (0, W): dr.ellipse([x - r, H / 2 - r, x + r, H / 2 + r], fill=(0, 0, 0, 0))
    m = int(H * 0.14); dash = int(H * 0.08); lw = max(2, int(H * 0.025)); c = (166, 50, 38, 255)
    for x in range(m + r, W - m - r, dash * 2):
        dr.line([(x, m), (min(x + dash, W - m - r), m)], fill=c, width=lw); dr.line([(x, H - m), (min(x + dash, W - m - r), H - m)], fill=c, width=lw)
    for y in range(m, H - m, dash * 2):
        for x in (m + r, W - m - r): dr.line([(x, y), (x, min(y + dash, H - m))], fill=c, width=lw)
    im = im.resize((W // S, H // S), Image.LANCZOS)
    tp = P(0.2); card = Image.new("RGBA", (im.width + 2 * tp, im.height + 2 * tp), (0, 0, 0, 0)); card.alpha_composite(im, (tp, tp))
    return _finish(name, card, angle, op=0.22)


def doodle(name, kind, size=0.6, color=(166, 50, 38), seed=1, width=0.035):
    """手绘涂鸦：star / heart / circle（椭圆圈）/ tick / sparkle"""
    rnd = random.Random(seed); c = size / 2
    if kind == "star":
        pts = []
        for k in range(11):
            a = -math.pi / 2 + k * math.pi * 4 / 5
            pts.append((c + c * math.cos(a) + rnd.uniform(-.02, .02), c + c * math.sin(a) + rnd.uniform(-.02, .02)))
        return hand_line(name, pts, color=color, width=width, head=False, seed=seed)
    if kind == "heart":
        pts = [(c + c * 0.95 * 16 * math.sin(t) ** 3 / 16, c - c * 0.95 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
               for t in [i / 40 * 2 * math.pi for i in range(42)]]
        return hand_line(name, pts, color=color, width=width, head=False, seed=seed, curve=True)
    if kind == "circle":   # size = 宽；高 = 0.42 宽
        h = size * 0.42
        pts = [(size / 2 + size / 2 * math.cos(t) * (1 + 0.04 * k), h / 2 + h / 2 * math.sin(t))
               for k, t in enumerate([-0.6 + i / 40 * 2.25 * math.pi for i in range(41)])]
        return hand_line(name, pts, color=color, width=width, head=False, seed=seed, curve=True)
    if kind == "tick":
        return hand_line(name, [(0, size * .55), (size * .35, size * .9), (size, 0)], color=color, width=width * 1.3, head=False, seed=seed)
    if kind == "sparkle":
        out = []
        for k, (a, L) in enumerate([(-2.3, .5), (-1.6, .6), (-0.9, .5)]):
            out.append([(c + .25 * c * math.cos(a), c + .25 * c * math.sin(a)), (c + L * size * math.cos(a), c + L * size * math.sin(a))])
        pts = []
        for seg in out: pts += seg
        return multi_line(name, out, color, width, seed)


def multi_line(name, segs, color, width, seed):
    xs = [p[0] for s_ in segs for p in s_]; ys = [p[1] for s_ in segs for p in s_]
    pad = 0.1; x0, y0 = min(xs) - pad, min(ys) - pad
    W, H = P(max(xs) - x0 + pad), P(max(ys) - y0 + pad); S = 3
    im = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); lw = int(width * DPI * S)
    for seg in segs:
        q = [((x - x0) * DPI * S, (y - y0) * DPI * S) for x, y in seg]
        d.line(q, fill=color + (235,), width=lw)
        for x, y in (q[0], q[-1]): d.ellipse([x - lw / 2, y - lw / 2, x + lw / 2, y + lw / 2], fill=color + (235,))
    im = im.resize((W, H), Image.LANCZOS); f = os.path.join(OUT, name + ".png"); im.save(f)
    META[name] = dict(w=W / DPI, h=H / DPI); return f


if __name__ == "__main__":
    # Demo: generate a small set of photo-free scrapbook assets into assets/scrap/.
    # polaroid(name, pexels_id, w, h, angle, focus, tapes, sat) needs styles/assets/raw/<pexels_id>.jpg first.
    os.makedirs(OUT, exist_ok=True)
    print(old_paper())
    print(scrap("demo_lined", "lined", 6.4, 1.05, -1.5, seed=40, torn="tb", tapes=("left",)))
    print(scrap("demo_kraft", "kraft", 3.2, 4.6, -8, seed=41, torn="lrb", tapes=()))
    print(sticky("demo_note", 2.6, 2.1, 6, (240, 224, 152), seed=3, tape_on=True))
    print(sticker("demo_sticker", 1.25))
    print(ticket("demo_ticket", 4.2, 0.9, -2))
    print(doodle("demo_star", "star", 0.55, seed=1))
