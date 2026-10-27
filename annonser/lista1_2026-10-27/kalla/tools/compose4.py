"""Bild 4 (3 enzymer): Norrtvätts kartong, svenska texter och nytt klistermärke."""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from boxlib import box_texture, warp_to_quad, quad_from_plane, over, font_for_cap, inpaint

src, boxphoto, out, fdir = sys.argv[1:5]
F = lambda n: f"{fdir}/{n}.ttf"
orig = np.asarray(Image.open(src).convert("RGB"))
H, W = orig.shape[:2]
o = orig.astype(int)
BG = (247, 241, 225)
CARDS = [(62, 367), (388, 693), (713, 1018)]
TEXT_X = [124, 453, 775]  # where the bullet text starts in each card

# ---------- 1. text removal ----------
u8 = orig.copy()
u8[85:206, 195:885] = BG    # "3 Enzymes."
u8[208:272, 150:930] = BG   # subhead
# text = pixels clearly darker than the smooth card gradient behind them (median-filtered estimate)
lum = orig.astype(np.float32).mean(axis=2)
bgl = cv2.medianBlur(orig, 45).astype(np.float32).mean(axis=2)
dark = ((bgl - lum) > 9).astype(np.uint8)
m = np.zeros((H, W), np.uint8)
for (x0, x1), tx in zip(CARDS, TEXT_X):
    m[376:424, x0 + 10:x1 - 10] |= dark[376:424, x0 + 10:x1 - 10]       # card title
    m[748:870, tx - 3:x1 - 6] |= dark[748:870, tx - 3:x1 - 6]          # bullet text (icons left alone)
m = cv2.dilate(m, np.ones((5, 5), np.uint8), iterations=2)
u8 = inpaint(u8, m * 255, 5)
# Telea leaves faint coloured blotches from the old anti-aliased edges: smooth the filled pixels and
# give them the card's paper grain back
sm_ = cv2.GaussianBlur(u8.astype(np.float32), (0, 0), 7)
grain = np.random.default_rng(4).normal(0, 2.2, u8.shape).astype(np.float32)
mf = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.5)[..., None]
u8 = (u8 * (1 - mf) + (sm_ + grain) * mf).clip(0, 255).astype(np.uint8)

# move the bullet blocks (icons + empty card) 30 px up so the taller box does not crowd them
SHIFT = 30
for x0, x1 in CARDS:
    u8[745 - SHIFT:903 - SHIFT, x0 + 6:x1 - 6] = u8[745:903, x0 + 6:x1 - 6].copy()
img = u8.astype(np.float32)

# ---------- 2. box: same width as the Uproot front, taller (portrait box), bottom on the same floor ----------
front = [[53, 909], [464, 903], [464, 1290], [53, 1303]]
side = [[33, 911], [53, 909], [53, 1303], [34, 1300]]
v0 = 1 - (411 / 0.934) / 394.0
nfront = quad_from_plane(front, 0, 1, v0, 1)
nside = quad_from_plane(side, 0, 1, v0, 1)
# side face: stretch the plain white side of the old box to the new height
sidepix = orig[905:1306, 30:56].astype(np.float32)
Ms = cv2.getPerspectiveTransform((np.float32(side) - np.float32([30, 905])).astype(np.float32), np.float32([[0, 0], [20, 0], [20, 400], [0, 400]]))
side_tex = cv2.warpPerspective(sidepix, Ms, (20, 400), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
rgb, al = warp_to_quad(side_tex, nside, (W, H))
img = over(img, rgb, al)
tex = box_texture(boxphoto)
oldwhite = np.median(o[960:1200, 70:440][o[960:1200, 70:440].min(axis=2) > 225], axis=0)
texwhite = np.median(tex[tex.min(axis=2) > 235].reshape(-1, 3), axis=0)
rgb, al = warp_to_quad(np.clip(tex * (oldwhite / texwhite), 0, 255), nfront, (W, H))
img = over(img, rgb, al)
# loose tablets in front of the box (bottom right) come back on top
reg = np.zeros((H, W), bool); reg[1205:1325, 428:580] = True
tab = reg & (o[..., 1] - o[..., 0] > 25) & (o[..., 1] > 100)
tab = cv2.morphologyEx(tab.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
tab = cv2.morphologyEx(tab, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
ta = cv2.GaussianBlur(tab.astype(np.float32), (0, 0), 1.0) * reg
img = over(img, orig.astype(np.float32), ta)

# ---------- 3. old sticker out ----------
u8 = img.clip(0, 255).astype(np.uint8)
a = u8.astype(int)
sreg = np.zeros((H, W), bool); sreg[950:1325, 712:990] = True
cyan = (a[..., 2] - a[..., 0] > 80) & (a[..., 1] - a[..., 0] > 80)   # the arrow pointing at the box stays
notbg = np.abs(a - np.array(BG)).sum(axis=2) > 18
sm = (sreg & notbg & ~cyan).astype(np.uint8)
sm = cv2.dilate(cv2.morphologyEx(sm, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)), np.ones((7, 7), np.uint8))
sm[:, :712] = 0
# keep the shelf/floor shading below y~1290 untouched where it is not sticker
u8 = inpaint(u8, sm * 255, 7)
im = Image.fromarray(u8)
d = ImageDraw.Draw(im)

# ---------- 4. new texts ----------
GOLD, NAVY, TEAL = (181, 123, 2), (7, 60, 80), (19, 56, 58)


def c_text(cx, base, s, f, fill):
    d.text((cx - f.getlength(s) / 2, base), s, font=f, fill=fill, anchor="ls")


c_text(540, 177, "3 enzymer.", font_for_cap(F("Lexend-600"), 84), GOLD)
sf = font_for_cap(F("Lexend-600"), 37)
while sf.getlength("En tablett. Ingen unken lukt.") > 760:
    sf = ImageFont.truetype(sf.path, sf.size - 1)
c_text(540, 254, "En tablett. Ingen unken lukt.", sf, NAVY)
tf = font_for_cap(F("Lexend-600"), 24)
for (x0, x1), t in zip(CARDS, ["Alfa-amylas", "Proteas", "Lipas"]):
    c_text((x0 + x1) / 2, 410, t, tf, NAVY)
BUL = [[("Löser tvättmedelsrester", "i trumma & gummilist"), ("Når dit tvättmedel", "inte når")],
       [("Bryter ner proteinet", "i djurhår"), ("Sköljer ut pälsen", "helt")],
       [("Löser fett från oljor", "& djurens hudflagor"), ("Tar bort bakterier", "vid källan")]]
bf = font_for_cap(F("Lexend-500"), 15)
widest = max(bf.getlength(l) for card in BUL for b in card for l in b)
maxw = min(x1 - 12 - tx for (x0, x1), tx in zip(CARDS, TEXT_X))
if widest > maxw:
    bf = ImageFont.truetype(bf.path, int(bf.size * maxw / widest))
for (x0, x1), tx, card in zip(CARDS, TEXT_X, BUL):
    for (l1, l2), base in zip(card, [770 - SHIFT, 838 - SHIFT]):
        d.text((tx, base), l1, font=bf, fill=TEAL, anchor="ls")
        d.text((tx, base + 22.5), l2, font=bf, fill=TEAL, anchor="ls")

# ---------- 5. sticker: SPECIALERBJUDANDE / UPP TILL / 50% / RABATT / BEGRÄNSAD TID ----------
SW, SH = 330, 430
st = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
RED, PINK, YEL = (226, 40, 26), (246, 160, 170), (255, 226, 0)
russo = F("RussoOne-400")


def tall_text(s, cap, fill, stroke, stretch=1.28):
    """Russo One drawn and stretched vertically, like the original sticker lettering."""
    f = font_for_cap(russo, cap / stretch)
    b = f.getbbox(s, stroke_width=stroke)
    lay = Image.new("RGBA", (b[2] - b[0] + 4, b[3] - b[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((2 - b[0], 2 - b[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=fill)
    return lay.resize((lay.width, int(lay.height * stretch)), Image.LANCZOS)


rows = [("UPP TILL", 36, YEL), ("50%", 92, YEL), ("RABATT", 56, (255, 255, 255))]
y = 78
placed = []
for s, cap, col in rows:
    letters = tall_text(s, cap, col, 0)
    if letters.width > 250:
        letters = letters.resize((250, int(letters.height * 250 / letters.width)), Image.LANCZOS)
    placed.append((letters, (SW - letters.width) // 2, y))
    y += letters.height + 10
# red plate behind the letters: one rounded plate per row (+ the label), merged, with a pink offset shadow
lab_f = ImageFont.truetype(F("Oswald-700"), 25)
lab = "SPECIALERBJUDANDE"
lw = lab_f.getlength(lab)
lab_box = (int((SW - lw) / 2) - 10, 34, int((SW + lw) / 2) + 10, 72)
plate = Image.new("L", (SW, SH), 0)
pd = ImageDraw.Draw(plate)
pd.rounded_rectangle((lab_box[0] - 13, lab_box[1] - 13, lab_box[2] + 13, lab_box[3] + 8), radius=16, fill=255)
for lay, x, yy in placed:
    pd.rounded_rectangle((x - 16, yy - 12, x + lay.width + 16, yy + lay.height + 12), radius=18, fill=255)
blob_np = cv2.morphologyEx(np.asarray(plate), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
blob_img = Image.fromarray(cv2.GaussianBlur(blob_np, (0, 0), 0.8))
shadow = Image.new("RGBA", (SW, SH), PINK + (255,))
st.paste(shadow, (-9, 9), blob_img)
st.paste(Image.new("RGBA", (SW, SH), RED + (255,)), (0, 0), blob_img)
sd = ImageDraw.Draw(st)
sd.rectangle(lab_box, fill=(255, 255, 255))
sd.text(((SW - lw) / 2, (lab_box[1] + lab_box[3]) / 2 + 1), lab, font=lab_f, fill=(0, 0, 0), anchor="lm")
for lay, x, yy in placed:
    st.alpha_composite(lay, (x, yy))
# ribbon
rib_f = ImageFont.truetype(F("Oswald-700"), 30)
rib = "BEGRÄNSAD TID"
rw = rib_f.getlength(rib)
ry = y + 22
sd.rounded_rectangle(((SW - rw) / 2 - 22, ry, (SW + rw) / 2 + 22, ry + 50), radius=6, fill=RED)
sd.text((SW / 2, ry + 26), rib, font=rib_f, fill=(255, 255, 255), anchor="mm")
st = st.rotate(7, resample=Image.BICUBIC, expand=True)
cx, cy = 850, 1140
im.paste(st, (int(cx - st.width / 2), int(cy - st.height / 2)), st)

im.save(out, quality=95)
print("saved", out, "bullet font", bf.size, "box", np.round(nfront, 1).tolist())
