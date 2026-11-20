#!/usr/bin/env python3
"""Static title box PNG (full frame) that replaces a Swedish white title box: same box, same line tops, font size
matched to the Swedish ink widths.   usage: title_box.py OUT.png W H x0,y0,x1,y1 RADIUS 'sv1|sv2|..' 'w1,w2,..' 'top1,top2,..' 'da1|da2|..'"""
import sys
from PIL import Image, ImageDraw, ImageFont
import os
FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "v22it", "fonts", "Montserrat-ExtraBold.ttf")
out, W, H, box, rad, sv, widths, tops, da = sys.argv[1:10]
W, H, rad = int(W), int(H), float(rad)
x0, y0, x1, y1 = [int(v) for v in box.split(",")]
sv, da = sv.split("|"), da.split("|")
widths = [float(v) for v in widths.split(",")]; tops = [float(v) for v in tops.split(",")]
f100 = ImageFont.truetype(FONT, 100)
sizes = [100 * w / (f100.getbbox(t)[2] - f100.getbbox(t)[0]) for t, w in zip(sv, widths)]
size = sorted(sizes)[len(sizes) // 2]
print("sizes", [round(s, 1) for s in sizes], "->", round(size, 1))
f = ImageFont.truetype(FONT, round(size))
while max(f.getbbox(t)[2] - f.getbbox(t)[0] for t in da) > 0.92 * (x1 - x0):
    size *= 0.98; f = ImageFont.truetype(FONT, round(size))
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle((x0, y0, x1, y1), rad, fill=(255, 255, 255, 255))
cx = (x0 + x1) / 2
for t, top in zip(da, tops):
    l, tt, r, b = f.getbbox(t)
    d.text((cx - (l + r) / 2, top - tt), t, font=f, fill=(0, 0, 0, 255))
img.save(out)
print("saved", out, "size", round(size, 1))
