"""Swedish overlays for video33 (720x1280). Usage: python3 build_ov33.py WORKDIR PRODUCT_PNG
Everything that carries text stays inside the Meta 4:5 crop (y 190-1090) and leaves the caption band
(y ~825-890, captions at 0.67) free on the full-screen cards."""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W_DIR, PRODUCT = sys.argv[1], sys.argv[2]
OUT = os.path.join(W_DIR, "ov")
os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(W_DIR, "fonts", "Montserrat-ExtraBold.ttf")
SMS_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
W, H = 720, 1280
TEAL, NAVY, BLACK, WHITE = (10, 147, 168, 255), (19, 38, 58, 255), (0, 0, 0, 255), (255, 255, 255, 255)


def f(size, path=FONT):
    return ImageFont.truetype(path, size)


def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def shadow(img, box, r, blur=10, alpha=90, dy=5):
    s = canvas()
    x0, y0, x1, y1 = box
    ImageDraw.Draw(s).rounded_rectangle((x0, y0 + dy, x1, y1 + dy), r, fill=(0, 0, 0, alpha))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))


def fit(text, size, width, path=FONT):
    while f(size, path).getlength(text) > width and size > 10:
        size -= 1
    return size


def text_box(name, box, lines, r=24, fill=WHITE, color=BLACK, img=None):
    """White rounded box with centred lines [(text, size)], each line shrunk to fit."""
    own = img is None
    img = img or canvas()
    shadow(img, box, r)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, r, fill=fill)
    x0, y0, x1, y1 = box
    fitted = [(t, fit(t, s, (x1 - x0) * 0.88)) for t, s in lines]
    total = sum(s for _, s in fitted) * 1.12
    y = (y0 + y1) / 2 - total / 2
    for t, s in fitted:
        d.text(((x0 + x1) / 2, y + s * 0.56), t, font=f(s), fill=color, anchor="mm")
        y += s * 1.12
    if own:
        img.save(os.path.join(OUT, name))
    return img


# 1) Enzyme labels: white boxes over the glowing English words (union of the label's positions)
text_box("amy.png", (105, 470, 635, 754), [("ALFA-", 112), ("AMYLAS", 112)], r=30)
text_box("pro.png", (36, 490, 692, 712), [("PROTEAS", 120)], r=30)
text_box("lip.png", (85, 486, 655, 708), [("LIPAS", 140)], r=30)

# 2) News headline (CNN screenshot that zooms): Swedish headline box per time slice + a dark panel
#    over the duplicated headline lower down, so the captions stay readable on top of it
HEAD = [("FORSKARE SKAPAR", 44), ("”SUPERENZYM”", 50)]
text_box("nasa_a.png", (55, 328, 495, 530), HEAD, r=22)
text_box("nasa_b.png", (0, 392, 500, 500), HEAD, r=18)
text_box("nasa_c.png", (0, 360, 530, 466), HEAD, r=18)
text_box("nasa_d.png", (0, 328, 535, 446), HEAD, r=18)
img = canvas()
ImageDraw.Draw(img).rounded_rectangle((-20, 780, 700, 1030), 26, fill=(8, 10, 16, 252))
img = img.filter(ImageFilter.GaussianBlur(3))
img.save(os.path.join(OUT, "nasa_low.png"))

# 3) Text message: Swedish bubble over the original one (same place, colour and size)
BUB = (90, 771, 619, 854)
BUB_FILL = (188, 180, 181, 255)


def sms(name, lines, cursor=False):
    img = canvas()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(BUB, 24, fill=BUB_FILL)
    fs = f(23, SMS_FONT)
    y = 797 if len(lines) == 2 else 812
    for i, t in enumerate(lines):
        d.text((112, y + i * 28), t + ("_" if cursor and i == len(lines) - 1 else ""), font=fs, fill=(24, 22, 22, 255), anchor="lm")
    img.save(os.path.join(OUT, name))


sms("sms1.png", ["Första gången de inte l"], cursor=True)
sms("sms2.png", ["Första gången de inte luktar blöt hund.", "Tack"])


# 4) Full-screen cards from the product page
def gradient():
    img = Image.new("RGBA", (W, H), WHITE)
    top, bot = (233, 246, 248), (196, 233, 240)
    g = ImageDraw.Draw(img)
    for y in range(H):
        k = y / (H - 1)
        g.line([(0, y), (W, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,))
    return img


def product(img, S, py):
    prod = Image.open(PRODUCT).convert("RGB").resize((S, S), Image.LANCZOS)
    px = (W - S) // 2
    shadow(img, (px, py, px + S, py + S), 28, blur=14, alpha=80, dy=8)
    frame = Image.new("RGBA", (S + 14, S + 14), WHITE)
    m = Image.new("L", frame.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, S + 13, S + 13), 32, fill=255)
    img.paste(frame, (px - 7, py - 7), m)
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), 26, fill=255)
    img.paste(prod, (px, py), m)


def spaced(d, cx, cy, word, size, fill, spacing=9):
    fw = f(size)
    total = sum(fw.getlength(c) for c in word) + spacing * (len(word) - 1)
    x = cx - total / 2
    for c in word:
        d.text((x, cy), c, font=fw, fill=fill, anchor="lm")
        x += fw.getlength(c) + spacing


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def pill(d, cy, text, size=34):
    w = f(size).getlength(text) + 70
    d.rounded_rectangle((360 - w / 2, cy - 34, 360 + w / 2, cy + 34), 34, fill=TEAL)
    d.text((360, cy), text, font=f(size), fill=WHITE, anchor="mm")


# product name card (over the trade-show booth while "Produkten heter Maskinrent, från Norrtvätt")
img = gradient()
d = ImageDraw.Draw(img)
spaced(d, 360, 236, "NORRTVÄTT", 34, TEAL)
d.text((360, 300), "MASKINRENT", font=f(fit("MASKINRENT", 80, 640)), fill=NAVY, anchor="mm")
product(img, 420, 360)
d = ImageDraw.Draw(img)
for i in range(5):
    star(d, 276 + i * 42, 950, 17, (245, 179, 1, 255))
d.text((360, 992), "4,8 av 5  ·  +15 000 kunder", font=f(26), fill=NAVY, anchor="mm")
img.save(os.path.join(OUT, "card_prod.png"))

# offer cards (replace the competitor packaging shots during the offer lines)
img = gradient()
d = ImageDraw.Draw(img)
d.text((360, 236), "REA", font=f(60), fill=TEAL, anchor="mm")
d.text((360, 310), "4 PAKET –50 %", font=f(fit("4 PAKET –50 %", 78, 640)), fill=NAVY, anchor="mm")
product(img, 420, 370)
d = ImageDraw.Draw(img)
pill(d, 968, "FRI FRAKT")
img.save(os.path.join(OUT, "card_offer.png"))

img = gradient()
d = ImageDraw.Draw(img)
d.text((360, 236), "REA", font=f(60), fill=TEAL, anchor="mm")
d.text((360, 310), "RÄCKER I 4 ÅR", font=f(fit("RÄCKER I 4 ÅR", 78, 640)), fill=NAVY, anchor="mm")
product(img, 420, 370)
d = ImageDraw.Draw(img)
d.text((360, 968), "4 paket till halva priset", font=f(30), fill=NAVY, anchor="mm")
img.save(os.path.join(OUT, "card_years.png"))

# guarantee bar at the top of the frame (inside the 4:5 crop, away from the captions)
text_box("bar_30.png", (40, 206, 680, 290), [("30 DAGARS PENGARNA TILLBAKA", 36)], r=26)

# 5) End card: caption band (825-890) kept free for "Klicka på länken och se själv"
img = gradient()
d = ImageDraw.Draw(img)
for i in range(5):
    star(d, 276 + i * 42, 222, 17, (245, 179, 1, 255))
d.text((360, 260), "4,8 av 5  ·  +15 000 kunder", font=f(24), fill=NAVY, anchor="mm")
spaced(d, 360, 306, "NORRTVÄTT", 40, NAVY)
product(img, 340, 336)
d = ImageDraw.Draw(img)
d.text((360, 726), "REA", font=f(64), fill=TEAL, anchor="mm")
d.text((360, 778), "4 PAKET –50 %  ·  FRI FRAKT", font=f(32), fill=NAVY, anchor="mm")
d.text((360, 938), "Prova i 30 dagar – pengarna tillbaka", font=f(24), fill=NAVY, anchor="mm")
d.rounded_rectangle((110, 984, 610, 1056), 36, fill=TEAL)
d.text((360, 1020), "SÄKRA ERBJUDANDET", font=f(32), fill=WHITE, anchor="mm")
img.save(os.path.join(OUT, "endcard33.png"))
print("ok")
