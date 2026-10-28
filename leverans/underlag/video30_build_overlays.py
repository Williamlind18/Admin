"""Build the Swedish overlays for video30 (720x1280). Usage: python3 -I build_overlays.py WORKDIR PRODUCT_PNG"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W_DIR, PRODUCT = sys.argv[1], sys.argv[2]
OUT = os.path.join(W_DIR, "ov")
FONT = os.path.join(W_DIR, "fonts", "Montserrat-ExtraBold.ttf")
W, H = 720, 1280
TEAL, NAVY, BLACK, WHITE = (10, 147, 168, 255), (19, 38, 58, 255), (0, 0, 0, 255), (255, 255, 255, 255)


def f(size):
    return ImageFont.truetype(FONT, size)


def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def shadow(img, box, r, blur=10, alpha=90, dy=5):
    s = canvas()
    x0, y0, x1, y1 = box
    ImageDraw.Draw(s).rounded_rectangle((x0, y0 + dy, x1, y1 + dy), r, fill=(0, 0, 0, alpha))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))


def text_box(name, box, lines, r=24, fill=WHITE, color=BLACK):
    """White rounded box with centred lines [(text, size)], text shrunk to fit."""
    img = canvas()
    shadow(img, box, r)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, r, fill=fill)
    x0, y0, x1, y1 = box
    fitted = []
    for t, size in lines:
        while f(size).getlength(t) > (x1 - x0) * 0.9 and size > 10:
            size -= 1
        fitted.append((t, size))
    total = sum(s for _, s in fitted) * 1.12
    y = (y0 + y1) / 2 - total / 2
    for t, size in fitted:
        d.text(((x0 + x1) / 2, y + size * 0.56), t, font=f(size), fill=color, anchor="mm")
        y += size * 1.12
    img.save(os.path.join(OUT, name))


def feather_patch(img, ref, dst, src, blur=6):
    """Copy paper texture from src box of ref onto dst box of img with soft edges."""
    x0, y0, x1, y1 = dst
    sx, sy = src
    piece = ref.crop((sx, sy, sx + x1 - x0, sy + y1 - y0)).convert("RGBA")
    m = Image.new("L", piece.size, 0)
    ImageDraw.Draw(m).rectangle((blur, blur, piece.size[0] - blur, piece.size[1] - blur), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(blur / 2))
    piece.putalpha(m)
    img.alpha_composite(piece, (x0, y0))


# 1) SEBUM label on the hair-strand graphic (white background, black text like the original)
img = canvas()
d = ImageDraw.Draw(img)
d.text((694, 430), "SEBUM", font=f(64), fill=(25, 25, 25, 255), anchor="ra")
d.text((694, 506), "HUNDENS HUDFETT", font=f(23), fill=(25, 25, 25, 255), anchor="ra")
img.save(os.path.join(OUT, "sebum.png"))

# 2) Pet hair = protein / sebum = fat graphic (original footage underneath)
ref = Image.open(os.path.join(OUT, "ref_pf.png")).convert("RGB")
img = canvas()
feather_patch(img, ref, (116, 508, 324, 580), (456, 508))      # "PET HAIR"
feather_patch(img, ref, (30, 890, 690, 995), (30, 1000))         # original caption box
img.save(os.path.join(OUT, "pf_base.png"))
img = canvas()
ImageDraw.Draw(img).text((220, 545), "DJURHÅR", font=f(30), fill=(45, 45, 45, 255), anchor="mm")
img.save(os.path.join(OUT, "pf_hair.png"))
img = canvas()
feather_patch(img, ref, (404, 672, 572, 786), (404, 556))        # "FAT"
t = Image.new("RGBA", (260, 110), (0, 0, 0, 0))
ImageDraw.Draw(t).text((10, 55), "FETT", font=f(66), fill=(208, 25, 31, 255), anchor="lm")
t = t.transform(t.size, Image.AFFINE, (1, 0.18, -10, 0, 1, 0), resample=Image.BICUBIC)  # slight italic like the brush font
img.alpha_composite(t, (408, 676))
img.save(os.path.join(OUT, "pf_fat.png"))

# 3) Enzyme names on the 3D blobs (white boxes, black text)
text_box("amy.png", (268, 585, 458, 722), [("Alfa-", 40), ("amylas", 40)], r=20)
text_box("pro.png", (222, 586, 512, 732), [("Proteas", 54)], r=22)
text_box("lip.png", (276, 616, 534, 782), [("Lipas", 60)], r=22)


# 4) Badges replacing "EWG verified" / "septic safe" with claims from the product page
def badge(name, lines):
    img = canvas()
    box = (112, 400, 608, 880)
    shadow(img, box, 34)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 34, fill=WHITE)
    cx, cy, rr = 360, 640, 205
    d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=TEAL, width=22)
    d.ellipse((cx - rr + 34, cy - rr + 34, cx + rr - 34, cy + rr - 34), outline=TEAL, width=4)
    sizes = [s for _, s in lines]
    total = sum(sizes) * 1.1
    y = cy - total / 2
    for t, s in lines:
        while f(s).getlength(t) > 2 * (rr - 55) and s > 10:
            s -= 1
        d.text((cx, y + s * 0.55), t, font=f(s), fill=TEAL, anchor="mm")
        y += s * 1.1
    img.save(os.path.join(OUT, name))


badge("badge_avk.png", [("AVKALKAR", 50), ("MASKINEN", 34)])
badge("badge_alla.png", [("PASSAR", 46), ("ALLA TVÄTT-", 40), ("MASKINER", 46)])

# 5) Green check marks above the two washers
img = canvas()
d = ImageDraw.Draw(img)
for cx, cy in ((184, 320), (538, 320)):
    r = 116
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(18, 196, 26, 255))
    d.line([(cx - 52, cy + 2), (cx - 14, cy + 40), (cx + 56, cy - 34)], fill=WHITE, width=26, joint="curve")
img.save(os.path.join(OUT, "checks.png"))

# 6) Offer lines: slim white bars in the lower third, above the captions and inside the 4:5 crop
BAR = (40, 806, 680, 892)
text_box("offer1.png", BAR, [("4 PAKET –50 %  ·  FRI FRAKT", 38)], r=26)
text_box("offer2.png", BAR, [("BARA 20 KR PER TABLETT", 38)], r=26)
text_box("offer3.png", BAR, [("30 DAGARS PENGARNA TILLBAKA", 36)], r=26)

# 7) Full-screen end card from the product page; everything inside y 200-1080 (Meta 4:5 crop)
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
    star(276 + i * 42, 232, 17, (245, 179, 1, 255))
d.text((360, 272), "4,8 av 5  ·  +15 000 kunder", font=f(24), fill=NAVY, anchor="mm")
word = "NORRTVÄTT"
fw = f(42)
spacing = 9
total = sum(fw.getlength(c) for c in word) + spacing * (len(word) - 1)
x = 360 - total / 2
for c in word:
    d.text((x, 322), c, font=fw, fill=NAVY, anchor="lm")
    x += fw.getlength(c) + spacing
S = 380
prod = Image.open(PRODUCT).convert("RGB").resize((S, S), Image.LANCZOS)
px, py = (W - S) // 2, 360
shadow(img, (px, py, px + S, py + S), 28, blur=14, alpha=80, dy=8)
frame = Image.new("RGBA", (S + 14, S + 14), WHITE)
m = Image.new("L", frame.size, 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, S + 13, S + 13), 32, fill=255)
img.paste(frame, (px - 7, py - 7), m)
m = Image.new("L", (S, S), 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, S - 1, S - 1), 26, fill=255)
img.paste(prod, (px, py), m)
d = ImageDraw.Draw(img)
d.text((360, 800), "REA – SNART SLUT", font=f(58), fill=TEAL, anchor="mm")
d.text((360, 862), "4 PAKET –50 %  ·  FRI FRAKT", font=f(34), fill=NAVY, anchor="mm")
d.rounded_rectangle((110, 1000, 610, 1072), 36, fill=TEAL)
d.text((360, 1036), "SÄKRA ERBJUDANDET", font=f(32), fill=WHITE, anchor="mm")
d.text((360, 906), "Prova i 30 dagar – pengarna tillbaka", font=f(24), fill=NAVY, anchor="mm")
img.save(os.path.join(OUT, "endcard.png"))
print("ok")
