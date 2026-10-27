"""Bild 5 (Last chance): två Norrtvätt-kartonger, svensk rubrik, pris per tablett och fri frakt."""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from boxlib import box_texture, warp_to_quad, quad_from_plane, over, font_for_cap, inpaint

src, boxphoto, out, fdir = sys.argv[1:5]
F = lambda n: f"{fdir}/{n}.ttf"
orig = np.asarray(Image.open(src).convert("RGB"))
H, W = orig.shape[:2]
o = orig.astype(int)
r, g, b = o[..., 0], o[..., 1], o[..., 2]
yy, xx = np.mgrid[0:H, 0:W]

# ---------- masks of what sits in front of the boxes (from the original) ----------
reg = (yy >= 620) & (yy <= 1000) & (xx >= 40) & (xx <= 352) & (yy <= 970 - 0.17 * (xx - 100))
t = (reg & (r > 60) & (r < 185) & (g > 120) & (b > 100) & (g - r > 25)).astype(np.uint8)
t = cv2.morphologyEx(t, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
n, lab, st, _ = cv2.connectedComponentsWithStats(t)
t = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
ff = t.copy(); cv2.floodFill(ff, np.zeros((H + 2, W + 2), np.uint8), (0, 0), 1); t = t | (1 - ff)
t = cv2.morphologyEx(t, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
# the tablet's right edge, traced by hand where it meets the box's turquoise band (colour alone leaks there)
ry = [690, 720, 740, 760, 780, 800, 815, 870, 920, 975]
rx = [296, 315, 322, 328, 333, 336, 338, 345, 350, 352]
xr = np.interp(np.arange(H), ry, rx)
xr[:690] = W
t[xx > xr[:, None] + 1] = 0
tablet = cv2.GaussianBlur(t.astype(np.float32), (0, 0), 1.0)
wt = (o.min(axis=2) > 170).astype(np.uint8); wt[:584] = 0; wt[750:] = 0; wt[:, :300] = 0; wt[:, 480:] = 0
n, lab, st, _ = cv2.connectedComponentsWithStats(wt)
arrow = cv2.dilate((lab == lab[640, 428]).astype(np.uint8), np.ones((3, 3), np.uint8))
arrow = cv2.GaussianBlur(arrow.astype(np.float32), (0, 0), 0.8)

# ---------- 1. headline + pill out (smooth inpaint over the dark gradient) ----------
lum = o.mean(axis=2)
bgl = cv2.medianBlur(orig, 61).astype(np.float32).mean(axis=2)
band = (yy >= 318) & (yy <= 626) & (xx >= 30) & (xx <= 895)
txt = band & ((np.abs(lum - bgl) > 14) | (r - g > 80))
txt &= ~(arrow > 0.05) & ~(t > 0)
txt &= ~((yy > 580) & (xx > 820))  # the box corner up there is replaced anyway
m = cv2.dilate(txt.astype(np.uint8), np.ones((7, 7), np.uint8), iterations=2)
m[(arrow > 0.05) | (t > 0)] = 0
u8 = inpaint(orig.copy(), m * 255, 9)
sm_ = cv2.GaussianBlur(u8.astype(np.float32), (0, 0), 9)
noise = np.random.default_rng(5).normal(0, 1.6, u8.shape).astype(np.float32)
mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2)[..., None]
img = u8 * (1 - mf) + (sm_ + noise) * mf

# ---------- 2. the two boxes (Norrtvätt's box is portrait: same width, taller along the box's own axis) ----------
tex = box_texture(boxphoto)
texwhite = np.median(tex[tex.min(axis=2) > 235].reshape(-1, 3), axis=0)


def shading(quad, white_ref):
    """Per-channel light falloff on the old box, fitted as a plane over its near-white print."""
    poly = np.zeros((H, W), np.uint8)
    cv2.fillPoly(poly, [np.int32(np.round(quad))], 1)
    poly = cv2.erode(poly, np.ones((15, 15), np.uint8))
    sat = o.max(axis=2) - o.min(axis=2)
    sel = (poly > 0) & (sat < 28) & (o.min(axis=2) > 150) & (t == 0) & (m == 0)
    ys, xs = np.where(sel)
    A = np.c_[np.ones(len(xs)), xs, ys]
    coef = [np.linalg.lstsq(A, o[ys, xs, c] / white_ref[c], rcond=None)[0] for c in range(3)]
    return np.stack([np.clip(cf[0] + cf[1] * xx + cf[2] * yy, 0.55, 1.03) for cf in coef], axis=-1).astype(np.float32)


big_old = [[272, 743], [868, 586], [976, 1119], [380, 1276]]
small_old = [[47, 990], [447, 1122], [282, 1497], [-39, 1381]]
# Norrtvätt's logo sits further left than Uproot's, so the big box slides ~38 px to the right along its
# own top edge; otherwise the tablet in front hides "NO" of NORRTVÄTT. Clear the old box first so the
# strip it leaves behind becomes background.
SHIFT_U = 0.062
clear = np.zeros((H, W), np.uint8)
cv2.fillPoly(clear, [np.int32(np.round(big_old))], 1)
clear = cv2.dilate(clear, np.ones((5, 5), np.uint8))
clear[(xx - 288.5) ** 2 + (yy - 1119) ** 2 < 142 ** 2] = 1  # old red circle: repainted later, must not bleed red
clear[(t > 0) | (arrow > 0.05)] = 0
img = inpaint(img.clip(0, 255).astype(np.uint8), clear * 255, 15).astype(np.float32)
for old, u0, real_aspect in [(small_old, 0.0, 1.12), (big_old, SHIFT_U, 1.12)]:  # small first: big box is in front
    q = quad_from_plane(old, u0, 1 + u0, 0, real_aspect / 0.934)
    rgb, al = warp_to_quad(tex, q, (W, H))
    rgb = rgb * shading(old, texwhite)
    img = over(img, np.clip(rgb, 0, 255), al)
    print("box quad", np.round(q, 1).tolist())

# tablet + arrow back on top, then the tablet's cyan glow over the new boxes
img = over(img, orig.astype(np.float32), tablet)
img = over(img, orig.astype(np.float32), arrow)
glow = cv2.GaussianBlur(t.astype(np.float32), (0, 0), 24) * (1 - tablet)
gcol = np.array([95, 235, 245], np.float32)
ga = np.clip(glow * 1.25, 0, 0.6)[..., None]
img = img * (1 - ga) + (255 - (255 - img) * (255 - gcol) / 255) * ga  # screen blend

im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
d = ImageDraw.Draw(im)

# ---------- 3. red circle: + FRI FRAKT ----------
RED = (250, 1, 0)
cx, cy, rad = 288.5, 1119, 133.5
d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=RED)


def c_text(x, base, s, f, fill="white", anchor="ms"):
    d.text((x, base), s, font=f, fill=fill, anchor=anchor)


mont = F("Montserrat-800")
c_text(cx, 1071, "+", font_for_cap(mont, 34))
ff_ = font_for_cap(mont, 56)
c_text(cx, 1144, "FRI", ff_)
fk = font_for_cap(mont, 40)
while fk.getlength("FRAKT") > 200:
    fk = ImageFont.truetype(mont, fk.size - 1)
c_text(cx, 1195, "FRAKT", fk)

# ---------- 4. pill + headline, tilted like the original (~2.4 deg) ----------
ANG = 2.4
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ld = ImageDraw.Draw(lay)
pf = font_for_cap(mont, 52)
pill_txt = "SISTA CHANSEN"
pw = pf.getlength(pill_txt)
PX, PY = 450, 389  # pill centre
pill = (PX - pw / 2 - 44, PY - 43, PX + pw / 2 + 44, PY + 43)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh).rounded_rectangle((pill[0] + 4, pill[1] + 10, pill[2] + 4, pill[3] + 10), radius=26, fill=(0, 0, 0, 120))
lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9)))
ld.rounded_rectangle(pill, radius=26, fill=RED + (255,))
ld.text((PX, PY + 2), pill_txt, font=pf, fill=(255, 255, 255, 255), anchor="mm")

bebas = F("BebasNeue-400")
hf = font_for_cap(bebas, 128)
left, right = "21 KR", "/TABLETT"
while hf.getlength(left + right) + 4 > 830:
    hf = ImageFont.truetype(bebas, hf.size - 1)
tw = hf.getlength(left + right)
x0, base = 470 - tw / 2, 590
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.text((x0 + 5, base + 7), left + right, font=hf, fill=(0, 0, 0, 150), anchor="ls", stroke_width=3, stroke_fill=(0, 0, 0, 150))
lay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)))
ld.text((x0, base), left, font=hf, fill=(11, 250, 254, 255), anchor="ls", stroke_width=2, stroke_fill=(11, 250, 254, 255))
ld.text((x0 + hf.getlength(left), base), right, font=hf, fill=(255, 255, 255, 255), anchor="ls",
        stroke_width=2, stroke_fill=(255, 255, 255, 255))
lay = lay.rotate(ANG, resample=Image.BICUBIC, center=(470, 480))
im = im.convert("RGBA")
im.alpha_composite(lay)
im = im.convert("RGB")
im.save(out, quality=95)
print("saved", out, "headline font", hf.size, "pill", [round(v) for v in pill])
