"""A6: package/price ad - the four bundles from norrtvatt.se."""
import sys
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from adlib import (LEX, ORANGE, CREAM, NAVY, WHITE, cap_font, fit, text_c, check, shadow_layer,
                   paste_shadowed, box_rgba)

boxphoto, out = sys.argv[1], sys.argv[2]
W, H = 1080, 1350
im = Image.new("RGBA", (W, H), CREAM + (255,))
d = ImageDraw.Draw(im)
text_c(d, W / 2, 118, "Välj ditt paket", cap_font(LEX[800], 62), NAVY)
sub = "Tidig höstrea – upp till 50% rabatt"
text_c(d, W / 2, 178, sub, fit(LEX[700], 28, sub, 900), ORANGE)

PACKS = [  # name, tablets, years, price, pct, per-tablet (rounded), badge, ordinary price (499 kr x packs, as on the site)
    ("1-PACK", 12, "1 år", "449 kr", "-10%", "37 kr/tablett", None, "499 kr"),
    ("2-PACK", 24, "2 år", "619 kr", "-40%", "26 kr/tablett", "MEST KÖPT", "998 kr"),
    ("3-PACK", 36, "3 år", "799 kr", "-45%", "22 kr/tablett", None, "1 497 kr"),
    ("4-PACK", 48, "4 år", "999 kr", "-50%", "21 kr/tablett", "BÄSTA PRIS", "1 996 kr"),
]
box = box_rgba(boxphoto, 150)
box_small = box_rgba(boxphoto, 132)
cw, chh, gx, gy = 470, 470, 40, 40
x0s, y0s = [50, 50 + cw + gx], [232, 232 + chh + gy]
for i, (name, n, yrs, price, pct, per, badge, strike) in enumerate(PACKS):
    x0, y0 = x0s[i % 2], y0s[i // 2]
    hi = badge is not None
    im.alpha_composite(shadow_layer((W, H), (x0, y0, x0 + cw, y0 + chh), 28, blur=18, offset=(0, 10), alpha=55))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y0, x0 + cw, y0 + chh), radius=28, fill=WHITE,
                        outline=ORANGE if hi else None, width=5 if hi else 0)
    # boxes, fanned, kept clear of the discount badge (top right)
    k = int(name[0])
    bxi = box if k <= 2 else box_small
    step = 52 if k <= 2 else 40
    total = bxi.width + step * (k - 1)
    area0, area1 = x0 + 24, x0 + cw - 128
    bx0 = (area0 + area1) / 2 - total / 2 if k > 1 else x0 + (cw - total) / 2
    for j in range(k):
        paste_shadowed(im, bxi, (bx0 + j * step, y0 + 50 + (k - 1 - j) * 4 + (12 if k > 2 else 0)), blur=8, offset=(4, 6), alpha=70)
    d = ImageDraw.Draw(im)
    # discount badge
    d.ellipse((x0 + cw - 118, y0 + 18, x0 + cw - 18, y0 + 118), fill=ORANGE)
    text_c(d, x0 + cw - 68, y0 + 80, pct, fit(LEX[800], 26, pct, 82), WHITE)
    if badge:
        bfnt = cap_font(LEX[800], 17)
        bw = bfnt.getlength(badge) + 36
        d.rounded_rectangle((x0 + cw / 2 - bw / 2, y0 - 22, x0 + cw / 2 + bw / 2, y0 + 22), radius=22, fill=NAVY)
        text_c(d, x0 + cw / 2, y0 + 9, badge, bfnt, WHITE)
    yb = y0 + 268
    text_c(d, x0 + cw / 2, yb + 30, name, cap_font(LEX[800], 28), NAVY)
    text_c(d, x0 + cw / 2, yb + 66, f"{n} tabletter · räcker {yrs}", cap_font(LEX[500], 18), (60, 100, 115))
    pf = cap_font(LEX[800], 50)
    if strike:
        sf = cap_font(LEX[600], 24)
        wp, ws = pf.getlength(price), sf.getlength(strike)
        xs = x0 + cw / 2 - (wp + 18 + ws) / 2
        d.text((xs, yb + 140), price, font=pf, fill=ORANGE, anchor="ls")
        sx = xs + wp + 18
        d.text((sx, yb + 140), strike, font=sf, fill=(140, 140, 140), anchor="ls")
        d.line([(sx - 2, yb + 128), (sx + ws + 2, yb + 128)], fill=(140, 140, 140), width=3)
    else:
        text_c(d, x0 + cw / 2, yb + 140, price, pf, ORANGE)
    text_c(d, x0 + cw / 2, yb + 176, per, cap_font(LEX[500], 17), (60, 100, 115))

# trust row
items = ["Fri frakt", "30 dagars pengarna-tillbaka", "4,8/5 (1 046 recensioner)"]
tf = cap_font(LEX[600], 18)
widths = [tf.getlength(t) + 40 for t in items]
gap = 34
x = W / 2 - (sum(widths) + gap * (len(items) - 1)) / 2
y = 1282
for t, w in zip(items, widths):
    check(d, x + 13, y - 7, 13, (16, 160, 110), WHITE, width=3)
    d.text((x + 34, y), t, font=tf, fill=NAVY, anchor="ls")
    x += w + gap
im.convert("RGB").save(out, quality=95)
print("saved", out)
