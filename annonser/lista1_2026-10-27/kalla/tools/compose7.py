"""Bild 7 (före/efter-trumma + lila banner): Norrtvätts kartong + svenska texter."""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from boxlib import box_texture, warp_to_quad, quad_from_plane, over, font_for_cap, inpaint

src, boxphoto, out, fdir = sys.argv[1:5]
INTER, LEX = f"{fdir}/Inter-700.ttf", f"{fdir}/Lexend-800.ttf"
orig = np.asarray(Image.open(src).convert("RGB"))
H, W = orig.shape[:2]
img = orig.astype(np.float32)

# ---------- 1. box: same width as the Uproot box, taller (Norrtvätt's box is portrait), bottom kept ----------
old = [[622.5, 721.5], [920.0, 720.0], [917.5, 982.5], [624.5, 987.5]]
v0 = 1 - (297.5 / 0.934) / 265.0
quad = quad_from_plane(old, 0, 1, v0, 1)
tex = box_texture(boxphoto)
rgb, al = warp_to_quad(tex, quad, (W, H))
# match the white point of the old box print (it sat a touch darker/warmer than the studio photo)
oldwhite = np.median(orig[740:980, 640:900][orig[740:980, 640:900].min(axis=2) > 225], axis=0)
texwhite = np.median(tex[tex.min(axis=2) > 235].reshape(-1, 3), axis=0)
rgb = np.clip(rgb * (oldwhite / texwhite), 0, 255)
# soft contact shadow on the drum, then the box
sh = cv2.GaussianBlur(np.roll(np.roll(al, 6, 0), 5, 1), (0, 0), 7) * 0.35
img = img * (1 - sh[..., None])
img = over(img, rgb, al)
# keep the loose tablets (in front of the box at the bottom right)
reg = np.zeros((H, W), bool); reg[890:1010, 903:1020] = True
o = orig.astype(int)
tab = reg & (o[..., 1] - o[..., 0] > 22) & (o[..., 1] > 100)
tab = cv2.morphologyEx(tab.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))  # drop thin slivers of old print
tab = cv2.morphologyEx(tab, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
tab = cv2.dilate(tab, np.ones((3, 3), np.uint8))
ta = cv2.GaussianBlur(tab.astype(np.float32), (0, 0), 1.0)
ta[890:955, :906] = 0  # the tablets start at x~906; left of that is old box print
img = over(img, orig.astype(np.float32), ta * reg)

# ---------- 2. banner: remove "Holiday Sale" (incl. the part above the banner) ----------
u8 = img.clip(0, 255).astype(np.uint8)
a = u8.astype(int)
box = np.zeros((H, W), bool); box[1000:1145, 195:900] = True
cream = (a[..., 0] > 200) & (a[..., 1] > 190) & (a[..., 2] > 160) & (a[..., 0] - a[..., 2] > 8)
navy = (a[..., 2] - a[..., 0] > 22) & (a[..., 1] > 38) & (a[..., 2] > 60)
m = (box & (cream | navy)).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
m = cv2.dilate(m, np.ones((5, 5), np.uint8))
m[1073:, :] = 0  # inside the banner we simply repaint
u8 = inpaint(u8, m * 255, 9)
# give the filled patches some of the drum's grain back so they do not read as smooth smears
grain = np.random.default_rng(7).normal(0, 6, u8.shape[:2]).astype(np.float32)[..., None]
mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)[..., None]
u8 = (u8 + grain * mf).clip(0, 255).astype(np.uint8)
im = Image.fromarray(u8)
d = ImageDraw.Draw(im)
PURPLE, NAVY, CREAM = (46, 33, 86), (40, 48, 80), (243, 238, 222)
d.rounded_rectangle((125, 1073, 955, 1301), radius=26, fill=PURPLE)


def draw_c(cx, base, s, f, fill, stroke=0, sfill=None):
    w = f.getlength(s)
    d.text((cx - w / 2, base), s, font=f, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=sfill)


# headline: same size/position as "Holiday Sale" (cap ~84 px, baseline 1112), navy outline
hf = font_for_cap(LEX, 84)
while hf.getlength("Tidig höstrea") > 690:
    hf = ImageFont.truetype(LEX, hf.size - 1)
draw_c(540, 1112, "Tidig höstrea", hf, CREAM, stroke=10, sfill=NAVY)

# offer line:  UPP/TILL  50% RABATT  +  FRI/FRAKT
small = font_for_cap(LEX, 21)
side = font_for_cap(LEX, 30)
plus = font_for_cap(LEX, 40)
gap = 14
wl = max(small.getlength("UPP"), small.getlength("TILL"))
wr = max(side.getlength("FRI"), side.getlength("FRAKT"))
wp = plus.getlength("+")
big = font_for_cap(LEX, 69)
while wl + big.getlength("50% RABATT") + wp + wr + 4 * gap > 770:
    big = ImageFont.truetype(LEX, big.size - 1)
total = wl + big.getlength("50% RABATT") + wp + wr + 4 * gap
x = 540 - total / 2
base = 1232
capb = big.getbbox("H")[3] - big.getbbox("H")[1]
mid = base - capb / 2
draw_c(x + wl / 2, mid - 3, "UPP", small, "white")
draw_c(x + wl / 2, mid + 27, "TILL", small, "white")
x += wl + gap
d.text((x, base), "50% RABATT", font=big, fill="white", anchor="ls")
x += big.getlength("50% RABATT") + gap
draw_c(x + wp / 2, mid + 20, "+", plus, "white")
x += wp + gap
draw_c(x + wr / 2, mid - 4, "FRI", side, "white")
draw_c(x + wr / 2, mid + 36, "FRAKT", side, "white")

# ---------- 3. Före / Efter ----------
for (x0, x1), word, cx in [((118, 416), "Före", 267), ((669, 967), "Efter", 818)]:
    d.rectangle((x0, 55, x1, 135), fill=(255, 255, 255))
    draw_c(cx, 120, word, font_for_cap(INTER, 53), (0, 0, 0))

im.save(out, quality=95)
print("saved", out, "big font", big.size, "headline", hf.size, "box quad", np.round(quad, 1).tolist())
