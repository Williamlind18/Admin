"""Offer cards that replace the two shots whose stylised English price text could not be removed."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W_DIR, PRODUCT = sys.argv[1], sys.argv[2]
FONT = os.path.join(W_DIR, "fonts", "Montserrat-ExtraBold.ttf")
W, H = 720, 1280
TEAL, NAVY, WHITE = (10, 147, 168, 255), (19, 38, 58, 255), (255, 255, 255, 255)
f = lambda s: ImageFont.truetype(FONT, s)

def card(name, top_line, big, small):
    img = Image.new("RGBA", (W, H), WHITE)
    a, b = (233, 246, 248), (196, 233, 240)
    g = ImageDraw.Draw(img)
    for y in range(H):
        k = y / (H - 1)
        g.line([(0, y), (W, y)], fill=tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3)) + (255,))
    S = 500
    prod = Image.open(PRODUCT).convert("RGB").resize((S, S), Image.LANCZOS)
    px, py = (W - S) // 2, 280
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((px, py + 10, px + S, py + S + 10), 30, fill=(0, 0, 0, 80))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), 30, fill=255)
    img.paste(prod, (px, py), m)
    d = ImageDraw.Draw(img)
    d.text((360, 236), top_line, font=f(40), fill=TEAL, anchor="mm")
    size = 74
    while f(size).getlength(big) > 640:
        size -= 2
    d.text((360, 846), big, font=f(size), fill=NAVY, anchor="mm")
    d.text((360, 1062), small, font=f(30), fill=NAVY, anchor="mm")  # below the captions, inside the 4:5 crop
    img.convert("RGB").save(os.path.join(W_DIR, "ov", name))

card("cardA.png", "REA – SNART SLUT", "4 PAKET –50 %", "Fri frakt  ·  20 kr per tablett")
card("cardB.png", "REA – SNART SLUT", "20 KR / TABLETT", "4 paket till halva priset")
print("ok")
