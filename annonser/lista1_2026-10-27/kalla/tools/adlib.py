"""Small design kit for Norrtvätt image ads (Pillow)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FDIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
LEX = {w: os.path.join(FDIR, f"Lexend-{w}.ttf") for w in (500, 600, 700, 800)}
INTER = os.path.join(FDIR, "Inter-700.ttf")
MONT = os.path.join(FDIR, "Montserrat-800.ttf")

ORANGE = (174, 76, 15)
CREAM = (248, 241, 225)
TEAL = (0, 172, 205)        # box band turquoise
NAVY = (7, 60, 80)
INK = (17, 24, 39)
GOLD = (255, 184, 0)
WHITE = (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, int(round(size)))


def cap_font(path, cap):
    """Font whose capital H is `cap` px tall."""
    f = ImageFont.truetype(path, 200)
    b = f.getbbox("H")
    return ImageFont.truetype(path, max(1, round(200 * cap / (b[3] - b[1]))))


def fit(path, cap, text, max_w):
    f = cap_font(path, cap)
    while f.getlength(text) > max_w and f.size > 6:
        f = ImageFont.truetype(path, f.size - 1)
    return f


def text_c(d, cx, base, s, f, fill, **kw):
    d.text((cx - f.getlength(s) / 2, base), s, font=f, fill=fill, anchor="ls", **kw)


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def stars(d, x, cy, r, n=5, gap=None, fill=GOLD):
    gap = gap if gap is not None else r * 0.35
    for i in range(n):
        star(d, x + r + i * (2 * r + gap), cy, r, fill)
    return n * 2 * r + (n - 1) * gap


def check(d, cx, cy, r, bg, fg, width=None):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    w = width or max(2, int(r * 0.28))
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.35)],
           fill=fg, width=w, joint="curve")


def cross(d, cx, cy, r, bg, fg, width=None):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg)
    w = width or max(2, int(r * 0.26))
    k = r * 0.4
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=fg, width=w)
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=fg, width=w)


def shadow_layer(size, box, radius, blur=18, offset=(0, 10), alpha=70):
    """RGBA soft drop shadow of a rounded rectangle."""
    lay = Image.new("RGBA", size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(lay).rounded_rectangle((x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]),
                                          radius=radius, fill=(0, 0, 0, alpha))
    return lay.filter(ImageFilter.GaussianBlur(blur))


def paste_shadowed(base, img, xy, blur=16, offset=(0, 12), alpha=90):
    """Paste an RGBA image with a soft shadow made from its own alpha."""
    a = img.split()[3]
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: v * alpha // 255))
    pad = blur * 3
    big = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    big.paste(sh, (pad, pad))
    big = big.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(big, (int(xy[0] - pad + offset[0]), int(xy[1] - pad + offset[1])))
    base.alpha_composite(img, (int(xy[0]), int(xy[1])))


def glow(img_rgba, color=(80, 230, 245), radius=28, strength=1.4):
    """Return an RGBA glow layer (same size) around the alpha of img_rgba."""
    a = np.asarray(img_rgba.split()[3]).astype(np.float32) / 255
    from cv2 import GaussianBlur
    g = GaussianBlur(a, (0, 0), radius) * strength
    g = np.clip(g, 0, 1)
    out = np.zeros((*a.shape, 4), np.uint8)
    out[..., :3] = color
    out[..., 3] = (g * 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def box_rgba(tex_path_or_arr, width):
    """Flat front of the Norrtvätt box as RGBA at a given width (rounded 3 px corners)."""
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from boxlib import box_texture
    tex = box_texture(tex_path_or_arr, 2)
    im = Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8)).convert("RGBA")
    h = round(width * im.height / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, width - 1, h - 1), radius=3, fill=255)
    im.putalpha(m)
    return im
