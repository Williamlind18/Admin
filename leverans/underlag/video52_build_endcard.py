"""Closing offer still for video52 (replaces Uproot's blue end still 279.0-end), same blue style:
NORRTVÄTT logo (asset, never redrawn), product image, KÖP 2 FÅ 2 + FRI FRAKT, 4 paket 999 kr,
rating 4,8/5, 15 000+ nöjda kunder, 30-day guarantee, norrtvatt.se. Output: endcard.png 720x1280."""
import math, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = "/home/user/Admin"
LOGO = f"{REPO}/.claude/skills/norrtvatt-iterations/assets/norrtvatt_logo.png"
PROD = f"{REPO}/leverans/underlag/maskinrent_produktbild_sv.png"
FONT = "fonts/Montserrat-ExtraBold.ttf"
W, H = 720, 1280
f = lambda s: ImageFont.truetype(FONT, s)

# background: vivid blue gradient with a soft centre glow (like the original)
bg = Image.new("RGB", (W, H))
px = bg.load()
for y in range(H):
    for x in range(W):
        t = y / H
        r, g, b = (34 + 10 * (1 - t)), (128 - 40 * t), (240 - 25 * t)
        d = math.hypot((x - W / 2) / W, (y - H * 0.5) / H)
        k = max(0.0, 1 - d * 1.8) * 45
        px[x, y] = (int(min(255, r + k * 0.6)), int(min(255, g + k)), int(min(255, b + k * 0.3)))
img = bg.convert("RGBA")

# bubbles
random.seed(7)
bub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(bub)
for _ in range(16):
    r = random.randint(8, 26)
    y = random.choice([random.randint(400, 520), random.randint(900, 1240)])
    x = random.choice([random.randint(18, 70), random.randint(650, 702)]) if y > 880 else random.randint(20, W - 20)
    bd.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255, 150), width=2)
    bd.ellipse((x - r * 0.45, y - r * 0.6, x - r * 0.1, y - r * 0.3), fill=(255, 255, 255, 120))
img = Image.alpha_composite(img, bub)
d = ImageDraw.Draw(img)


def shadow(box, radius, blur=14, alpha=90, off=8):
    s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((box[0], box[1] + off, box[2], box[3] + off), radius, fill=(0, 30, 90, alpha))
    return s.filter(ImageFilter.GaussianBlur(blur))


def centered(text, y, font, fill, x=W // 2):
    w = d.textlength(text, font=font)
    d.text((x - w / 2, y), text, font=font, fill=fill)


# logo on a white pill (asset pasted as is)
logo = Image.open(LOGO).convert("RGBA")
lw = 380
logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
pill = (W // 2 - lw // 2 - 34, 70, W // 2 + lw // 2 + 34, 70 + logo.height + 40)
img = Image.alpha_composite(img, shadow(pill, 40, alpha=70))
d = ImageDraw.Draw(img)
d.rounded_rectangle(pill, 40, fill="white")
img.alpha_composite(logo, (W // 2 - lw // 2, 90))
d = ImageDraw.Draw(img)

# offer badges (KÖP 2 FÅ 2 bubble + PLUS + FRI FRAKT pills, as in the original)
badge = Image.new("RGBA", (300, 200), (0, 0, 0, 0))
bdd = ImageDraw.Draw(badge)
bdd.rounded_rectangle((10, 10, 290, 180), 70, fill=(28, 92, 230), outline="white", width=6)
bdd.polygon([(60, 165), (40, 198), (100, 172)], fill=(28, 92, 230))
for t, yy, sz, col in (("KÖP 2", 28, 46, "white"), ("FÅ 2", 76, 72, (120, 230, 255))):
    ff = f(sz)
    bdd.text((150 - bdd.textlength(t, font=ff) / 2, yy), t, font=ff, fill=col)
badge = badge.rotate(6, resample=Image.BICUBIC, expand=True)
img.alpha_composite(badge, (40, 205))
d = ImageDraw.Draw(img)
for box, txt, fill, col, sz in (((370, 232, 640, 300), "PLUS", "white", (28, 92, 230), 40),
                                 ((340, 318, 690, 392), "FRI FRAKT", (40, 200, 240), "white", 46)):
    img = Image.alpha_composite(img, shadow(box, 36, blur=8, alpha=70, off=5))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 36, fill=fill)
    ff = f(sz)
    centered(txt, box[1] + (box[3] - box[1] - sz * 1.2) / 2, ff, col, x=(box[0] + box[2]) // 2)

# product image as a rounded card
ps = 430
prod = Image.open(PROD).convert("RGBA").resize((ps, ps), Image.LANCZOS)
mask = Image.new("L", (ps, ps), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, ps, ps), 34, fill=255)
px0, py0 = W // 2 - ps // 2, 440
card = (px0 - 8, py0 - 8, px0 + ps + 8, py0 + ps + 8)
img = Image.alpha_composite(img, shadow(card, 40, blur=18, alpha=110, off=12))
d = ImageDraw.Draw(img)
d.rounded_rectangle(card, 40, fill="white")
img.paste(prod, (px0, py0), mask)
d = ImageDraw.Draw(img)

# black price pill
y = py0 + ps + 40
box = (95, y, W - 95, y + 78)
d.rounded_rectangle(box, 39, fill=(14, 14, 18))
centered("4 PAKET · 999 KR", y + 15, f(40), "white")

# trust row: stars + rating + customers
y += 108
tr = "4,8/5 · 15 000+ nöjda kunder"
tw = 5 * 36 + 4 + d.textlength(tr, font=f(26))
sx, r = int(W / 2 - tw / 2) + 15, 15
for i in range(5):
    cx, cy = sx + i * 36, y + 18
    pts = [(cx + (r if k % 2 == 0 else r * 0.45) * math.sin(k * math.pi / 5),
            cy - (r if k % 2 == 0 else r * 0.45) * math.cos(k * math.pi / 5)) for k in range(10)]
    d.polygon(pts, fill=(255, 204, 51))
d.text((sx - 15 + 5 * 36 + 4, y), tr, font=f(26), fill="white")
y += 52
centered("30 dagars pengarna-tillbaka-garanti", y, f(26), (225, 240, 255))
y += 62
centered("norrtvatt.se", y, f(50), "white")

img.convert("RGB").save(sys.argv[1] if len(sys.argv) > 1 else "endcard.png")
print("ok", y)
