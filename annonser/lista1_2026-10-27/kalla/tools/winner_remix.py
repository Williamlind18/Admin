"""Variants of the winning ad (before/after + tablet + orange circle + cream banner) with new hooks."""
import sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from adlib import LEX, INTER, ORANGE, CREAM, WHITE, cap_font, fit, text_c, stars

SRC = sys.argv[1]
OUT = sys.argv[2]
VARIANT = sys.argv[3]


def base():
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    for (x0, x1), word, cx in [((112, 394), "Före", 252.5), ((636, 918), "Efter", 776.5)]:
        d.rectangle((x0, 52, x1, 128), fill=WHITE)
        text_c(d, cx, 113, word, cap_font(INTER, 50), (0, 0, 0))
    yy, xx = np.mgrid[0:H, 0:W]
    a = np.asarray(im).copy()
    a[((xx - 99) ** 2 + (yy - 1140) ** 2 < 246 ** 2) & (xx <= 335)] = ORANGE
    im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((372, 1162, 985, 1246), radius=30, fill=CREAM)
    return im, d


im, d = base()
CX = 157
if VARIANT == "betyg":
    r = 18
    total = 5 * 2 * r + 4 * r * 0.35
    stars(d, CX - total / 2, 962, r, fill=WHITE)
    text_c(d, CX, 1068, "4,8/5", fit(LEX[800], 66, "4,8/5", 250), WHITE)
    text_c(d, CX, 1132, "1 046", cap_font(LEX[800], 40), WHITE)
    text_c(d, CX, 1172, "RECENSIONER", fit(LEX[800], 24, "RECENSIONER", 230), WHITE)
    banner = "Upp till 50% rabatt"
elif VARIANT == "garanti":
    text_c(d, CX, 980, "PROVA", cap_font(LEX[800], 28), WHITE)
    text_c(d, CX, 1080, "30", cap_font(LEX[800], 84), WHITE)
    text_c(d, CX, 1136, "DAGAR", cap_font(LEX[800], 42), WHITE)
    text_c(d, CX, 1178, "RISKFRITT", fit(LEX[800], 26, "RISKFRITT", 230), WHITE)
    banner = "Nöjd eller pengarna tillbaka"
else:
    raise SystemExit("unknown variant")
bf = fit(LEX[800], 54, banner, 590)
hb = bf.getbbox("H")
text_c(d, 670 if bf.getlength(banner) > 520 else 636, 1204 + (hb[3] - hb[1]) / 2, banner, bf, ORANGE)
im.save(OUT, quality=95)
print("saved", OUT, "banner font", bf.size)
