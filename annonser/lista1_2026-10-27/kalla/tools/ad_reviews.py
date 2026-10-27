"""A5: review ad - real review headlines from norrtvatt.se, 4,8/5 from 1 046 reviews, offer."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from adlib import LEX, NAVY, WHITE, cap_font, fit, text_c, stars, shadow_layer

shop, out = sys.argv[1], sys.argv[2]
W, H = 1080, 1350
BG_TOP, BG_BOT = np.array([212, 239, 246]), np.array([236, 248, 251])
g = np.linspace(0, 1, H)[:, None, None]
bg = (BG_TOP * (1 - g) + BG_BOT * g) * np.ones((H, W, 3))
im = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")

# hero product photo (splash shot), feathered into the background, right side
ph = Image.open(f"{shop}/box_10.png").convert("RGBA").resize((760, 760), Image.LANCZOS)
m = Image.new("L", ph.size, 0)
ImageDraw.Draw(m).ellipse((40, 40, 720, 720), fill=255)
ph.putalpha(m.filter(ImageFilter.GaussianBlur(45)))
im.alpha_composite(ph, (W - 700, 400))

d = ImageDraw.Draw(im)
# top: stars + headline quote
r = 26
sw = 5 * 2 * r + 4 * r * 0.35
stars(d, W / 2 - sw / 2, 92, r)
hf = fit(LEX[800], 54, "”Äntligen luktar tvätten", 940)
text_c(d, W / 2, 210, "”Äntligen luktar tvätten", hf, NAVY)
text_c(d, W / 2, 290, "faktiskt rent”", hf, NAVY)
text_c(d, W / 2, 345, "Sara M.  ·  Maskinrent-kund", cap_font(LEX[500], 22), (40, 90, 110))

# review cards on the left
cards = [("”Perfekt när man har hund”", "Helena A."),
         ("”Stor skillnad på vår gamla maskin”", "Pernilla A."),
         ("”Önskar att jag hade hittat dessa tidigare”", "Jessica B.")]
qf = cap_font(LEX[700], 19)
nf = cap_font(LEX[500], 15)
lh = int(qf.size * 1.22)
x0, y, cw = 48, 425, 500
for q, name in cards:
    lines, cur = [], ""
    for w_ in q.split():
        t = (cur + " " + w_).strip()
        if qf.getlength(t) > cw - 60:
            lines.append(cur)
            cur = w_
        else:
            cur = t
    lines.append(cur)
    ch = 66 + lh * len(lines) + 46
    im.alpha_composite(shadow_layer((W, H), (x0, y, x0 + cw, y + ch), 22, blur=16, offset=(0, 8), alpha=45))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0, y, x0 + cw, y + ch), radius=22, fill=WHITE)
    stars(d, x0 + 30, y + 36, 13)
    for i, ln in enumerate(lines):
        d.text((x0 + 30, y + 66 + lh * (i + 1) - 8), ln, font=qf, fill=NAVY, anchor="ls")
    d.text((x0 + 30, y + ch - 22), f"– {name}", font=nf, fill=(70, 110, 125), anchor="ls")
    y += ch + 24

# rating summary + offer bar
y = 1150
d.rounded_rectangle((48, y, W - 48, y + 150), radius=28, fill=NAVY)
text_c(d, 280, y + 62, "4,8/5", cap_font(LEX[800], 40), WHITE)
stars(d, 280 - (5 * 2 * 13 + 4 * 13 * 0.35) / 2, y + 92, 13)
text_c(d, 280, y + 128, "1 046 recensioner", cap_font(LEX[500], 15), (200, 230, 240))
d.line([(500, y + 30), (500, y + 120)], fill=(60, 110, 130), width=2)
off = "Upp till 50% rabatt"
text_c(d, 768, y + 70, off, fit(LEX[800], 32, off, 440), (255, 196, 120))
sub = "Fri frakt  ·  30 dagars pengarna-tillbaka"
text_c(d, 768, y + 114, sub, fit(LEX[500], 16, sub, 440), WHITE)
im.convert("RGB").save(out, quality=95)
print("saved", out)
