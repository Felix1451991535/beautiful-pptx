# -*- coding: utf-8 -*-
"""程序生成的纹理 / 光效 / 装饰素材（不使用任何 AI 生成图）。
每个函数：参数确定 → 结果确定（固定随机种子），输出缓存到 styles/assets/gen/，返回文件路径。
在风格说明书里引用这里的函数名和参数，换颜色/尺寸只需改参数重新调用。"""
import math, os
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__))); from fontpath import cjk_font
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from common import gen_path, raw, grade

PX = (2400, 1350)   # 全幅背景默认分辨率（16:9）


def _hex(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def _noise(w, h, cells, rng):
    """value noise：低分辨率随机 → 双三次放大，返回 0~1"""
    cw, ch = max(2, int(cells)), max(2, int(cells * h / w))
    a = (rng.random((ch, cw)) * 255).astype(np.uint8)
    return np.asarray(Image.fromarray(a).resize((w, h), Image.BICUBIC)).astype(np.float32) / 255.0


def fbm(w, h, rng, base=4, octaves=5, gain=0.5):
    tot, amp, s = np.zeros((h, w), np.float32), 1.0, 0
    for o in range(octaves):
        tot += amp * _noise(w, h, base * 2 ** o, rng); s += amp; amp *= gain
    return tot / s


def _save(arr, out, mode="RGB", q=88):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode)
    if out.endswith(".jpg"): im.save(out, quality=q)
    else: im.save(out, optimize=True)
    return out


# ================================================================== 手账：旧纸 / 胶带 / 横格纸 / 牛皮纸
def paper_crumpled(base="EBE0CA", crease=0.05, stains=0.55, seed=3, size=PX, folds=1.0):
    """皱纸：脊状分形噪声做高度场（折痕网）→ 按斜上方光源求明暗 + 低频污渍 + 边缘泛黄 + 细颗粒。
    crease 明暗强度（0.04 轻微 ~ 0.10 明显），folds 折痕密度倍数"""
    out = gen_path("paper", "jpg", base, crease, stains, seed, size, folds, "v5")
    if os.path.exists(out): return out
    W, H = size; rng = np.random.default_rng(seed)
    w, h = W // 2, H // 2
    hgt = np.zeros((h, w), np.float32); amp = 0.35
    for o in range(5):
        n = _noise(w, h, 10 * folds * 2 ** o, rng)
        hgt += amp * (1 - np.abs(2 * n - 1)) ** 2.2; amp *= 0.55
    yy0, xx0 = np.mgrid[0:h, 0:w].astype(np.float32)
    for i in range(int(110 * folds)):                      # 长折痕：随机短线段的"屋脊/山谷"
        cx, cy = rng.uniform(0, w), rng.uniform(0, h); a = rng.uniform(0, math.pi)
        L = rng.uniform(.06, .32) * w; wd = rng.uniform(10, 42); sg = rng.choice([-1, 1]) * rng.uniform(.6, 1.4)
        ux, uy = math.cos(a), math.sin(a)
        along = (xx0 - cx) * ux + (yy0 - cy) * uy; perp = -(xx0 - cx) * uy + (yy0 - cy) * ux
        hgt += sg * np.clip(1 - np.abs(perp) / wd, 0, 1) * np.clip(1 - (along / (L / 2)) ** 2, 0, 1) * 1.2
    gy, gx = np.gradient(hgt)
    shade = (gx * -0.7 + gy * -0.7) / (np.std(gx) * 2.2 + 1e-6)          # 光从左上来
    shade = np.clip(shade, -2.5, 2.5)
    shade = np.asarray(Image.fromarray(((shade + 3) * 40).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 40 - 3
    col = _hex(base)[None, None, :] * np.ones((H, W, 1), np.float32)
    col *= (1 + crease * shade * 0.5)[..., None]
    n = fbm(W, H, rng, base=3, octaves=4)
    st = np.clip((n - 0.56) * 3, 0, 1) * stains
    col *= (1 - st[..., None] * np.array([0.04, 0.08, 0.16]))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = np.clip(r - 0.7, 0, 1) ** 1.4
    col *= (1 - v[..., None] * np.array([0.10, 0.16, 0.28]))
    col += rng.normal(0, 2.6, (H, W))[..., None]
    return _save(col, out)


def tape(w=900, h=230, color="E3D3AE", alpha=0.62, seed=1, stripes=False, stripe_color="C9A97C"):
    """半透明纸胶带：锯齿撕口 + 纵向纤维 + 边缘略深；可选条纹（和纸胶带）"""
    out = gen_path("tape", "png", w, h, color, alpha, seed, stripes, stripe_color)
    if os.path.exists(out): return out
    rng = np.random.default_rng(seed)
    a = np.full((h, w), alpha, np.float32)
    a *= 0.92 + 0.08 * _noise(w, h, 40, rng)
    a *= 0.95 + 0.05 * np.tile(rng.random(w)[None, :], (h, 1))  # 纵向纤维
    col = _hex(color)[None, None, :] * np.ones((h, w, 1), np.float32)
    if stripes:
        xx = np.arange(w)[None, :] * np.ones((h, 1))
        m = ((xx + np.arange(h)[:, None] * 0.6) // (w / 14)) % 2 == 0
        col[m] = _hex(stripe_color)
    # 上下边缘略深
    yy = np.arange(h)[:, None] / h
    col *= (1 - 0.06 * (np.exp(-yy * 18) + np.exp(-(1 - yy) * 18)))[..., None]
    mask = Image.new("L", (w, h), 0); d = ImageDraw.Draw(mask)
    def zig(x0, sgn):
        pts = []; y = 0
        while y <= h:
            pts.append((x0 + sgn * rng.uniform(0, 18), y)); y += rng.uniform(6, 14)
        pts.append((x0 + sgn * rng.uniform(0, 18), h)); return pts
    L = zig(6, 1); R = zig(w - 6, -1)
    d.polygon(L + list(reversed(R)), fill=255)
    m = np.asarray(mask).astype(np.float32) / 255
    rgba = np.dstack([col, (a * m * 255)])
    return _save(rgba, out, "RGBA")


def lined_paper(w=1100, h=1400, paper="FBF8F0", line_c="9FB6D3", margin_c="D98C8C", gap=52, torn="top", seed=2):
    """横格纸片：蓝色横线 + 红色页边线 + 一侧撕口（带纤维白边）"""
    out = gen_path("lined", "png", w, h, paper, line_c, margin_c, gap, torn, seed)
    if os.path.exists(out): return out
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    body = Image.new("RGB", (w, h), tuple(int(x) for x in _hex(paper))); bd = ImageDraw.Draw(body)
    for y in range(int(gap * 2.2), h, gap):
        bd.line([(0, y), (w, y)], fill=tuple(int(x) for x in _hex(line_c)), width=2)
    bd.line([(int(w * .13), 0), (int(w * .13), h)], fill=tuple(int(x) for x in _hex(margin_c)), width=2)
    arr = np.asarray(body).astype(np.float32)
    arr *= (0.97 + 0.03 * fbm(w, h, rng, 6, 3))[..., None]
    mask = Image.new("L", (w, h), 0); md = ImageDraw.Draw(mask)
    pts = [(0, h), (w, h)]; x = w; edge = []
    while x >= 0:
        edge.append((x, rng.uniform(4, 26) + 6 * math.sin(x / 37))); x -= rng.uniform(5, 16)
    edge.append((0, rng.uniform(4, 26)))
    md.polygon(pts + edge, fill=255)
    m = np.asarray(mask.filter(ImageFilter.GaussianBlur(0.8))).astype(np.float32)
    rgba = np.dstack([arr, m])
    img = Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), "RGBA")
    if torn == "bottom": img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(out, optimize=True)
    return out


def kraft(w=1000, h=700, base="C8A57A", seed=4, torn=True):
    """牛皮纸片：纤维噪点 + 撕边"""
    out = gen_path("kraft", "png", w, h, base, seed, torn)
    if os.path.exists(out): return out
    rng = np.random.default_rng(seed)
    col = _hex(base)[None, None, :] * (0.9 + 0.12 * fbm(w, h, rng, 8, 5))[..., None]
    col += rng.normal(0, 6, (h, w))[..., None]
    mask = Image.new("L", (w, h), 0); md = ImageDraw.Draw(mask)
    j = lambda: rng.uniform(0, 14) if torn else 0
    poly = [(x, j()) for x in range(0, w + 1, 12)] + [(w - j(), y) for y in range(0, h + 1, 12)] + \
           [(x, h - j()) for x in range(w, -1, -12)] + [(j(), y) for y in range(h, -1, -12)]
    md.polygon(poly, fill=255)
    rgba = np.dstack([col, np.asarray(mask).astype(np.float32)])
    return _save(rgba, out, "RGBA")


def grain_overlay(size=(1600, 900), density=0.012, dark="3A2A20", light="FFFFFF", seed=5, alpha=0.5):
    """全幅透明颗粒/灰尘层（复古印刷、旧照片）"""
    out = gen_path("grain", "png", size, density, dark, light, seed, alpha)
    if os.path.exists(out): return out
    W, H = size; rng = np.random.default_rng(seed)
    a = np.zeros((H, W), np.float32); col = np.zeros((H, W, 3), np.float32)
    m1 = rng.random((H, W)) < density; m2 = rng.random((H, W)) < density * 0.6
    col[m1] = _hex(dark); a[m1] = rng.uniform(0.3, 1, m1.sum()) * alpha * 255
    col[m2] = _hex(light); a[m2] = rng.uniform(0.3, 1, m2.sum()) * alpha * 255
    return _save(np.dstack([col, a]), out, "RGBA")


# ================================================================== 光效：极光 / 柔光渐变 / 模糊 / 暗角
def glow_field(blobs, base="05060B", size=PX, curtains=0.0, dither=2.0, seed=6, mode="screen"):
    """多个大椭圆高斯光斑叠加。blobs: [(cx, cy, rx, ry, hex, strength, angle_deg)]，坐标为 0~1 比例。
    mode='screen' 用于深色底（极光），'mix' 用于浅色底（玻璃风柔彩背景）。curtains>0 叠加极光竖向帘幕纹理"""
    out = gen_path("glow", "jpg", blobs, base, size, curtains, dither, seed, mode)
    if os.path.exists(out): return out
    W, H = size; rng = np.random.default_rng(seed)
    w, h = W // 2, H // 2
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    col = _hex(base)[None, None, :] * np.ones((h, w, 1), np.float32) / 255.0
    curtain = None
    if curtains:
        f = np.zeros(w, np.float32)
        for _ in range(9):
            f += np.sin(np.arange(w) / w * rng.uniform(8, 40) * math.pi + rng.uniform(0, 6)) * rng.uniform(.3, 1)
        curtain = (0.5 + 0.5 * f / np.abs(f).max())[None, :]
    for (cx, cy, rx, ry, hx, k, ang) in blobs:
        a = math.radians(ang)
        dx, dy = xx / w - cx, (yy / h - cy) * h / w
        u = dx * math.cos(a) + dy * math.sin(a); v = -dx * math.sin(a) + dy * math.cos(a)
        g = np.exp(-((u / rx) ** 2 + (v / ry) ** 2) * 2.2) * k
        if curtain is not None:
            g *= (1 - curtains) + curtains * curtain
        c = _hex(hx) / 255.0
        if mode == "screen":
            col = 1 - (1 - col) * (1 - g[..., None] * c)
        else:
            col = col * (1 - g[..., None]) + c * g[..., None]
    col = col * 255 + rng.normal(0, dither, (h, w))[..., None]
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(1.5))
    a2 = np.asarray(im).astype(np.float32) + np.random.default_rng(seed + 1).normal(0, dither, (H, W))[..., None]
    return _save(a2, out)


def blurred(path, radius=60, bright=1.0, sat=1.0):
    """玻璃面板用：整页背景的高斯模糊版（同尺寸，便于按面板位置精确裁切）"""
    out = gen_path("blur_" + os.path.splitext(os.path.basename(path))[0], "jpg", path, radius, bright, sat)
    if os.path.exists(out): return out
    im = Image.open(path).convert("RGB")
    sm = im.resize((im.width // 4, im.height // 4), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius / 4))
    im2 = sm.resize(im.size, Image.BICUBIC)
    from PIL import ImageEnhance
    if bright != 1: im2 = ImageEnhance.Brightness(im2).enhance(bright)
    if sat != 1: im2 = ImageEnhance.Color(im2).enhance(sat)
    im2.save(out, quality=90)
    return out


def radial_glow(color="FFD27A", size=1200, falloff=2.4, alpha=0.9, squash=1.0):
    """透明背景的圆形/椭圆光晕 PNG（发光点、镜头光）"""
    out = gen_path("rglow", "png", color, size, falloff, alpha, squash)
    if os.path.exists(out): return out
    w, h = size, max(8, int(size * squash))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = np.clip(1 - r, 0, 1) ** falloff * alpha * 255
    col = _hex(color)[None, None, :] * np.ones((h, w, 1))
    return _save(np.dstack([col, a]), out, "RGBA")


def vignette_png(size=(1600, 900), color="000000", strength=0.75, inner=0.45, power=1.8):
    """透明中心、四周压暗的暗角层"""
    out = gen_path("vig", "png", size, color, strength, inner, power)
    if os.path.exists(out): return out
    W, H = size
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.414
    a = np.clip((r - inner) / (1 - inner), 0, 1) ** power * strength * 255
    col = _hex(color)[None, None, :] * np.ones((H, W, 1))
    return _save(np.dstack([col, a]), out, "RGBA")


def light_streak(color="FFE2A0", w=2400, h=220, alpha=0.85):
    """横向镜头光条（国赛风标题后的光）"""
    out = gen_path("streak", "png", color, w, h, alpha)
    if os.path.exists(out): return out
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx - w / 2) / (w / 2); v = (yy - h / 2) / (h / 2)
    a = np.exp(-(v * 3.2) ** 2) * np.clip(1 - np.abs(u), 0, 1) ** 1.6
    a += 0.8 * np.exp(-(v * 18) ** 2) * np.clip(1 - np.abs(u), 0, 1) ** 0.8
    col = _hex(color)[None, None, :] * np.ones((h, w, 1))
    return _save(np.dstack([col, np.clip(a, 0, 1) * alpha * 255]), out, "RGBA")


# ================================================================== 孔版：双色网点 / 套印错位
def _screen(w, h, cell, angle):
    a = math.radians(angle)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx * math.cos(a) + yy * math.sin(a)) / cell
    v = (-xx * math.sin(a) + yy * math.cos(a)) / cell
    return (np.cos(2 * math.pi * u) + np.cos(2 * math.pi * v)) / 4 + 0.5     # 0~1 圆网点阈值


def riso_duotone(src, W, H, focus=(0.5, 0.5), c1="FF48B0", c2="0078BF", paper="F3EEE3", cell=9, offset=(7, -5),
                 px=1500, gamma1=1.0, gamma2=1.3, k1=0.85, k2=1.0, contrast=1.25, seed=8):
    """真实照片 → 两个专色的网点分色（c1 管中间调、c2 管暗部），c1 版错位 offset 像素，正片叠底到纸色上。
    W,H 为目标英寸比例。返回 jpg 路径"""
    out = gen_path("riso_" + os.path.splitext(os.path.basename(src))[0], "jpg", src, W, H, focus, c1, c2, paper,
                   cell, offset, px, gamma1, gamma2, k1, k2, contrast, seed)
    if os.path.exists(out): return out
    from PIL import ImageOps, ImageEnhance
    im = Image.open(raw(src) if not os.path.isabs(src) else src).convert("L")
    pw = int(px if W >= H else px * W / H); ph = int(pw * H / W)
    S = 2  # 2x 超采样抗锯齿
    im = ImageOps.fit(im, (pw * S, ph * S), Image.LANCZOS, centering=focus)
    im = ImageOps.autocontrast(im, cutoff=1); im = ImageEnhance.Contrast(im).enhance(contrast)
    g = np.asarray(im).astype(np.float32) / 255.0
    dark = 1 - g
    rng = np.random.default_rng(seed)
    d1 = np.clip(dark ** gamma1 * k1, 0, 1); d2 = np.clip((dark ** gamma2) * k2 - 0.12, 0, 1)
    m1 = (d1 > _screen(pw * S, ph * S, cell * S, 15)).astype(np.float32)
    m2 = (d2 > _screen(pw * S, ph * S, cell * S, 75)).astype(np.float32)
    ox, oy = offset[0] * S, offset[1] * S
    m1 = np.roll(np.roll(m1, oy, 0), ox, 1)
    ink = 0.82 + 0.18 * _noise(pw * S, ph * S, 60, rng)          # 油墨不匀
    a1 = m1 * ink * 0.92; a2 = m2 * ink * 0.95
    p = _hex(paper) / 255; C1 = _hex(c1) / 255; C2 = _hex(c2) / 255
    col = p[None, None, :] * (1 - a1[..., None] * (1 - C1)) * (1 - a2[..., None] * (1 - C2))
    col *= 255
    im2 = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).resize((pw, ph), Image.LANCZOS)
    im2.save(out, quality=90)
    return out


def halftone_blob(color="FF48B0", size=1000, cell=22, seed=9, shape="circle", alpha=0.95):
    """透明底的网点渐变色块（圆/条），装饰用"""
    out = gen_path("htblob", "png", color, size, cell, seed, shape, alpha)
    if os.path.exists(out): return out
    w = h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if shape == "circle":
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        dens = np.clip(1.05 - r, 0, 1) ** 0.7
    else:
        dens = np.clip(xx / w, 0, 1)
    m = (dens > _screen(w, h, cell, 20)).astype(np.float32)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))).astype(np.float32)
    col = _hex(color)[None, None, :] * np.ones((h, w, 1))
    return _save(np.dstack([col, m * alpha]), out, "RGBA")


# ================================================================== 日式：和纸 / 印章
def washi(base="F5F0E6", fibers=520, size=PX, seed=10):
    """和纸：极淡云纹 + 随机纤维丝（亮丝与少量暗丝）"""
    out = gen_path("washi", "jpg", base, fibers, size, seed, "v2")
    if os.path.exists(out): return out
    W, H = size; rng = np.random.default_rng(seed)
    col = _hex(base)[None, None, :] * (0.985 + 0.03 * fbm(W, H, rng, 3, 4))[..., None]
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(fibers):
        x, y = rng.uniform(0, W), rng.uniform(0, H); ang = rng.uniform(0, 2 * math.pi)
        L = rng.uniform(20, 120); pts = [(x, y)]
        for _ in range(8):
            ang += rng.normal(0, .35); x += math.cos(ang) * L / 8; y += math.sin(ang) * L / 8; pts.append((x, y))
        if rng.random() < .95: d.line(pts, fill=(255, 253, 248, int(rng.uniform(70, 170))), width=int(rng.integers(1, 3)))
        else: d.line(pts, fill=(190, 178, 160, int(rng.uniform(18, 40))), width=1)
    lay = lay.filter(ImageFilter.GaussianBlur(0.6))
    im = Image.alpha_composite(im, lay).convert("RGB")
    a = np.asarray(im).astype(np.float32) + rng.normal(0, 1.6, (H, W))[..., None]
    return _save(a, out)


SEAL_FONT = cjk_font("serif", True)


def seal(chars="茶", color="B7282E", size=600, font=SEAL_FONT, style="white", seed=11, round_=False):
    """朱文/白文印章 PNG：style='white' 白文（字镂空），'red' 朱文（红字+红边框）。边缘与印面带随机残缺。
    chars 1~4 字（4 字按 2×2 排、右起竖读）"""
    out = gen_path("seal", "png", chars, color, size, os.path.basename(font), style, seed, round_)
    if os.path.exists(out): return out
    rng = np.random.default_rng(seed); S = size
    m = Image.new("L", (S, S), 0); d = ImageDraw.Draw(m)
    pad = int(S * .06)
    if round_: d.ellipse([pad, pad, S - pad, S - pad], fill=255)
    else: d.rounded_rectangle([pad, pad, S - pad, S - pad], radius=int(S * .05), fill=255)
    txt = Image.new("L", (S, S), 0); td = ImageDraw.Draw(txt)
    n = len(chars)
    if n == 1:
        f = ImageFont.truetype(font, int(S * .62)); cells = [(chars, S / 2, S / 2)]
    elif n == 2:
        f = ImageFont.truetype(font, int(S * .40)); cells = [(chars[0], S / 2, S * .30), (chars[1], S / 2, S * .70)]
    else:
        f = ImageFont.truetype(font, int(S * .36))
        pos = [(S * .70, S * .30), (S * .70, S * .70), (S * .30, S * .30), (S * .30, S * .70)]
        cells = [(c, *pos[i]) for i, c in enumerate(chars[:4])]
    for c, cx, cy in cells:
        td.text((cx, cy), c, font=f, fill=255, anchor="mm")
    t = np.asarray(txt).astype(np.float32) / 255; mm = np.asarray(m).astype(np.float32) / 255
    if style == "white":
        a = mm * (1 - t)
    else:
        ring = np.asarray(Image.new("L", (S, S), 0)).copy()
        r = Image.new("L", (S, S), 0); rd = ImageDraw.Draw(r)
        if round_: rd.ellipse([pad, pad, S - pad, S - pad], outline=255, width=int(S * .05))
        else: rd.rounded_rectangle([pad, pad, S - pad, S - pad], radius=int(S * .05), outline=255, width=int(S * .05))
        a = np.clip(np.asarray(r).astype(np.float32) / 255 + t, 0, 1)
    wear = _noise(S, S, 50, rng) * 0.6 + _noise(S, S, 160, rng) * 0.4
    a *= (wear > 0.23).astype(np.float32) * 0.9 + 0.1 * (wear > 0.15)
    edge = _noise(S, S, 14, rng)
    a *= np.clip((edge - 0.08) * 6, 0, 1)
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32)
    col = _hex(color)[None, None, :] * np.ones((S, S, 1))
    return _save(np.dstack([col, a * 0.94]), out, "RGBA")


def brush_stroke(color="B7282E", w=1600, h=260, seed=12, alpha=0.9):
    """干笔刷痕（横向），日式/国风点缀"""
    out = gen_path("brush", "png", color, w, h, seed, alpha)
    if os.path.exists(out): return out
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = xx / w; v = (yy - h / 2) / (h / 2)
    thick = 0.75 * np.clip(np.sin(np.clip(u, 0, 1) * math.pi) ** 0.35, 0, 1) * (1 - 0.35 * u)
    bend = 0.12 * np.sin(u * 3.0 + 0.4)
    body = (np.abs(v - bend) < thick).astype(np.float32)
    bristle = np.tile(rng.random(h)[:, None], (1, w))
    streak = np.asarray(Image.fromarray((bristle * 255).astype(np.uint8)).resize((w, h))).astype(np.float32) / 255
    dry = (streak > (0.15 + 0.75 * u ** 2.2)).astype(np.float32)
    a = body * dry
    a = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)
    col = _hex(color)[None, None, :] * np.ones((h, w, 1))
    return _save(np.dstack([col, a * alpha]), out, "RGBA")


# ================================================================== 玻璃：柔彩背景上的渐变球体
def orbs(base_path, items, seed=13):
    """在背景图上画清晰的渐变球体（玻璃面板压上去时，模糊版里能看到彩色透出来）。
    items: [(cx, cy, r, 亮色hex, 暗色hex)]，cx/cy/r 为相对宽度的比例"""
    out = gen_path("orbs", "jpg", base_path, items, seed)
    if os.path.exists(out): return out
    im = Image.open(base_path).convert("RGB"); W, H = im.size
    a = np.asarray(im).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for cx, cy, r, c1, c2 in items:
        cx, cy, r = cx * W, cy * H, r * W
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r
        inside = np.clip((1 - d) * r / 2.0, 0, 1)                    # 2px 抗锯齿边
        hl = np.sqrt((xx - (cx - r * .38)) ** 2 + (yy - (cy - r * .42)) ** 2) / (r * 1.5)
        t = np.clip(hl, 0, 1)[..., None]
        col = _hex(c1) * (1 - t) + _hex(c2) * t
        a = a * (1 - inside[..., None]) + col * inside[..., None]
    return _save(a, out)
