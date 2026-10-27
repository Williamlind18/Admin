"""A7: 'Utan vs. med Maskinrent' comparison ad (front-loader seal before/after + claims from norrtvatt.se)."""
import sys
from PIL import Image, ImageDraw
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from adlib import (LEX, ORANGE, CREAM, NAVY, WHITE, cap_font, fit, text_c, check, cross, shadow_layer,
                   paste_shadowed, box_rgba)

dirty, clean, boxphoto, out = sys.argv[1:5]
W, H = 1080, 1350
im = Image.new("RGBA", (W, H), (244, 248, 250, 255))
d = ImageDraw.Draw(im)
text_c(d, W / 2, 112, "Utan vs. med Maskinrent", fit(LEX[800], 58, "Utan vs. med Maskinrent", 980), NAVY)
text_c(d, W / 2, 166, "En tablett i månaden för en fräsch tvättmaskin.", cap_font(LEX[500], 24), (60, 100, 115))

GREY = (75, 85, 99)
TEALD = (0, 150, 180)
cols = [(dirty, "UTAN", GREY, False, ["Unken lukt i tvätten", "Mögel & beläggningar", "Djurhår som fastnar"]),
        (clean, "MED MASKINRENT", TEALD, True, ["Fräsch, ren lukt", "Ren trumma & gummilist", "Löser upp djurhår & fett"])]
cw, gap, x0 = 486, 28, 40
for i, (src, label, col, good, rows) in enumerate(cols):
    x = x0 + i * (cw + gap)
    y = 205
    ch = 820
    im.alpha_composite(shadow_layer((W, H), (x, y, x + cw, y + ch), 26, blur=16, offset=(0, 8), alpha=50))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + cw, y + ch), radius=26, fill=WHITE, outline=col if good else None, width=5 if good else 0)
    ph = Image.open(src).convert("RGB")
    # crop: the gasket ring, left half of the frame (same crop for both)
    cx0, cy0 = int(ph.width * 0.05), int(ph.height * 0.09)
    cwid = int(ph.width * 0.86)
    chei = int(cwid * 520 / (cw - 24))
    ph = ph.crop((cx0, cy0, cx0 + cwid, cy0 + chei)).resize((cw - 24, 520), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", ph.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, ph.width - 1, ph.height - 1), radius=18, fill=255)
    ph.putalpha(m)
    im.alpha_composite(ph, (x + 12, y + 12))
    d = ImageDraw.Draw(im)
    lf = cap_font(LEX[800], 24)
    lw = lf.getlength(label) + 44
    d.rounded_rectangle((x + cw / 2 - lw / 2, y + 500, x + cw / 2 + lw / 2, y + 556), radius=28, fill=col)
    text_c(d, x + cw / 2, y + 540, label, lf, WHITE)
    rf = fit(LEX[600], 21, max(rows, key=len), cw - 110)
    for j, t in enumerate(rows):
        ry = y + 622 + j * 64
        (check if good else cross)(d, x + 46, ry - 9, 17, (16, 160, 110) if good else (220, 60, 50), WHITE, width=4)
        d.text((x + 78, ry), t, font=rf, fill=NAVY, anchor="ls")

# bottom: box + offer
box = box_rgba(boxphoto, 190)
paste_shadowed(im, box, (60, 1062), blur=12, offset=(4, 10), alpha=80)
d = ImageDraw.Draw(im)
t1 = "Upp till 50% rabatt"
text_c(d, 655, 1132, t1, fit(LEX[800], 46, t1, 700), ORANGE)
t2 = "Fri frakt · 30 dagars pengarna-tillbaka"
text_c(d, 655, 1186, t2, fit(LEX[600], 22, t2, 700), NAVY)
bw = 360
d.rounded_rectangle((655 - bw / 2, 1222, 655 + bw / 2, 1292), radius=35, fill=NAVY)
bf_ = cap_font(LEX[800], 26)
tw_ = bf_.getlength("Handla nu")
tx = 655 - (tw_ + 40) / 2
d.text((tx, 1268), "Handla nu", font=bf_, fill=WHITE, anchor="ls")
ax, ay = tx + tw_ + 16, 1257
d.line([(ax, ay), (ax + 24, ay)], fill=WHITE, width=5)
d.polygon([(ax + 30, ay), (ax + 18, ay - 10), (ax + 18, ay + 10)], fill=WHITE)
im.convert("RGB").save(out, quality=95)
print("saved", out)
