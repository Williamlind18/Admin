"""Norwegian (Nordvask) closing card for b5.1 C3, 720x1280. Same drawing code as the Norwegian card
(leverans/underlag/video30_build_overlays_no.py on claude/focused-hamilton-930j6d), laid out like the
Swedish b5.1 C3 card it replaces (stars 220, rating 262, wordmark 306, product 338 px at y 337,
headline 727, offer 778, guarantee 940, button 984-1056)."""
import math, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FONT, PRODUCT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 720, 1280
TEAL, NAVY, WHITE = (10, 147, 168, 255), (19, 38, 58, 255), (255, 255, 255, 255)
f = lambda s: ImageFont.truetype(FONT, s)
img = Image.new("RGBA", (W, H), WHITE)
top, bot = (233, 246, 248), (196, 233, 240)
g = ImageDraw.Draw(img)
for y in range(H):
    k = y / (H - 1)
    g.line([(0, y), (W, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,))
d = ImageDraw.Draw(img)
def star(cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)
for i in range(5):
    star(276 + i * 42, 220, 17, (245, 179, 1, 255))
d.text((360, 262), "4,8 av 5  ·  +15 000 kunder", font=f(24), fill=NAVY, anchor="mm")
word, fw, spacing = "NORDVASK", f(42), 9
total = sum(fw.getlength(c) for c in word) + spacing * (len(word) - 1)
x = 360 - total / 2
for c in word:
    d.text((x, 306), c, font=fw, fill=NAVY, anchor="lm")
    x += fw.getlength(c) + spacing
S = 338
prod = Image.open(PRODUCT).convert("RGB").resize((S, S), Image.LANCZOS)
px, py = (W - S) // 2, 337
s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(s).rounded_rectangle((px, py + 8, px + S, py + S + 8), 28, fill=(0, 0, 0, 80))
img.alpha_composite(s.filter(ImageFilter.GaussianBlur(14)))
frame = Image.new("RGBA", (S + 14, S + 14), WHITE)
m = Image.new("L", frame.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, S + 13, S + 13), 32, fill=255)
img.paste(frame, (px - 7, py - 7), m)
m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), 26, fill=255)
img.paste(prod, (px, py), m)
d = ImageDraw.Draw(img)
d.text((360, 727), "SALG", font=f(58), fill=TEAL, anchor="mm")
d.text((360, 778), "4 PAKKER –50 %  ·  FRI FRAKT", font=f(34), fill=NAVY, anchor="mm")
d.text((360, 940), "Prøv i 30 dager – pengene tilbake", font=f(24), fill=NAVY, anchor="mm")
d.rounded_rectangle((110, 984, 610, 1056), 36, fill=TEAL)
d.text((360, 1020), "SIKRE TILBUDET", font=f(32), fill=WHITE, anchor="mm")
img.convert("RGB").save(OUT)
print("ok")
