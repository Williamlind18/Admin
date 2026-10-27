"""Bild 6 (före/efter, tabletten, orange cirkel): byt texterna till svenska och Norrtvätts erbjudande."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

src, out, fdir = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert("RGB")
W, H = im.size
d = ImageDraw.Draw(im)
INTER = f"{fdir}/Inter-700.ttf"
LEX = f"{fdir}/Lexend-800.ttf"
ORANGE = (174, 76, 15)
CREAM = (248, 241, 225)


def font_for_cap(path, cap):
    """Font size whose capital H is `cap` px tall."""
    f = ImageFont.truetype(path, 100)
    b = f.getbbox("H")
    return ImageFont.truetype(path, max(1, round(100 * cap / (b[3] - b[1]))))


def text_c(cx, baseline, s, font, fill, max_w=None):
    """Draw s centred on cx with its baseline at `baseline` (shrinks to max_w)."""
    while max_w and font.getlength(s) > max_w:
        font = ImageFont.truetype(font.path, font.size - 1)
    w = font.getlength(s)
    d.text((cx - w / 2, baseline), s, font=font, fill=fill, anchor="ls")
    return font


# 1) Före / Efter: blank the white label interiors, then write the Swedish words.
for (x0, x1), word, cx in [((112, 394), "Före", 252.5), ((636, 918), "Efter", 776.5)]:
    d.rectangle((x0, 52, x1, 128), fill=(255, 255, 255))
    text_c(cx, 113, word, font_for_cap(INTER, 50), (0, 0, 0))

# 2) Orange circle (centre 99,1140, r 248): repaint flat orange, left of the cream banner.
yy, xx = np.mgrid[0:H, 0:W]
circle = ((xx - 99) ** 2 + (yy - 1140) ** 2 < (248 - 2) ** 2) & (xx <= 335)
a = np.asarray(im).copy()
a[circle] = ORANGE
im = Image.fromarray(a)
d = ImageDraw.Draw(im)
CX = 157
text_c(CX, 985, "UPP TILL", font_for_cap(LEX, 26), (255, 255, 255))
text_c(CX, 1078, "50%", font_for_cap(LEX, 71), (255, 255, 255))
text_c(CX, 1160, "RABATT", font_for_cap(LEX, 58), (255, 255, 255), max_w=262)
text_c(CX, 1237, "+ FRI FRAKT", font_for_cap(LEX, 27), (255, 255, 255), max_w=250)

# 3) Cream banner: blank the old headline, write the store's own sale name.
d.rounded_rectangle((372, 1162, 985, 1246), radius=30, fill=CREAM)
text_c(636, 1226, "Tidig höstrea", font_for_cap(LEX, 54), ORANGE, max_w=560)

im.save(out, quality=95)
print("saved", out, im.size)
