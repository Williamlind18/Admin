"""A3/A4: the winning layout on new front-loader before/after photos, with Norrtvätt's own square tablet."""
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from adlib import (LEX, INTER, ORANGE, CREAM, WHITE, cap_font, fit, text_c, glow, shadow_layer)

dirty, clean, tablet, out, variant = sys.argv[1:6]
W, H = 1080, 1350


def fill(path):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


A, B = fill(dirty), fill(clean)
im = B.copy()
im.paste(A.crop((0, 0, W // 2, H)), (0, 0))
im = im.convert("RGBA")
d = ImageDraw.Draw(im)
d.rectangle((W // 2 - 5, 0, W // 2 + 5, H), fill=WHITE)

# Före / Efter labels (winner style, scaled to 1080 wide)
k = W / 1024
for cx, word in [(252.5 * k, "Före"), (776.5 * k, "Efter")]:
    bw, bh = 330 * k, 115 * k
    im.alpha_composite(shadow_layer((W, H), (cx - bw / 2, 36 * k, cx + bw / 2, 36 * k + bh), 22, blur=10, offset=(0, 4), alpha=40))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((cx - bw / 2, 36 * k, cx + bw / 2, 36 * k + bh), radius=22, fill=WHITE)
    text_c(d, cx, 36 * k + bh / 2 + 53 * k / 2, word, cap_font(INTER, 53 * k), (0, 0, 0))

# Norrtvätt's tablet in the middle, glowing like the winner's
t = Image.open(tablet).convert("RGBA")
t = t.crop(t.getbbox())
tw = 390
t = t.resize((tw, round(t.height * tw / t.width)), Image.LANCZOS).rotate(-8, resample=Image.BICUBIC, expand=True)
pad = 90
tl = Image.new("RGBA", (t.width + 2 * pad, t.height + 2 * pad), (0, 0, 0, 0))
tl.alpha_composite(t, (pad, pad))
g = glow(tl, color=(70, 235, 250), radius=22, strength=2.2)
cx, cy = W // 2, int(H * 0.47)
im.alpha_composite(g, (cx - tl.width // 2, cy - tl.height // 2))
im.alpha_composite(tl, (cx - tl.width // 2, cy - tl.height // 2))

# orange circle bottom-left + cream banner (winner geometry scaled)
d = ImageDraw.Draw(im)
ccx, ccy, r = 99 * k, 1140 * k + (H - 1280 * k), 248 * k
oy = H - 1280 * k
d.rounded_rectangle((338 * k, 1153 * k + oy, 999 * k, 1253 * k + oy), radius=50 * k, fill=CREAM)
d.ellipse((ccx - r, ccy - r, ccx + r, ccy + r), fill=ORANGE)
CX = 157 * k
if variant == "rea":
    text_c(d, CX, 985 * k + oy, "UPP TILL", cap_font(LEX[800], 26 * k), WHITE)
    text_c(d, CX, 1078 * k + oy, "50%", cap_font(LEX[800], 71 * k), WHITE)
    text_c(d, CX, 1160 * k + oy, "RABATT", fit(LEX[800], 58 * k, "RABATT", 262 * k), WHITE)
    text_c(d, CX, 1237 * k + oy, "+ FRI FRAKT", fit(LEX[800], 27 * k, "+ FRI FRAKT", 250 * k), WHITE)
    banner = "Tidig höstrea"
elif variant == "manad":
    text_c(d, CX, 985 * k + oy, "FRÅN", cap_font(LEX[800], 28 * k), WHITE)
    text_c(d, CX, 1080 * k + oy, "21 KR", fit(LEX[800], 74 * k, "21 KR", 262 * k), WHITE)
    text_c(d, CX, 1142 * k + oy, "PER", cap_font(LEX[800], 34 * k), WHITE)
    text_c(d, CX, 1196 * k + oy, "MÅNAD", fit(LEX[800], 40 * k, "MÅNAD", 250 * k), WHITE)
    banner = "1 tablett i månaden"
bf = fit(LEX[800], 54 * k, banner, 600 * k)
hb = bf.getbbox("H")
text_c(d, (636 if bf.getlength(banner) < 520 * k else 668) * k, 1203 * k + oy + (hb[3] - hb[1]) / 2, banner, bf, ORANGE)
im.convert("RGB").save(out, quality=95)
print("saved", out)
