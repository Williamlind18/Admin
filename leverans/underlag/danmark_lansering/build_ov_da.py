#!/usr/bin/env python3
"""Danish (Nordvask) overlays for launch-set batch 1. Coordinates follow the Swedish deliveries, which use the
same layouts as the Norwegian builders (leverans/underlag/video30_*_no.py, video33_build_ov33_no.py).
Writes ov/<key>/*.png and ov/<key>/spec.json  (items: png | seq | src crop, with times in seconds).
usage: build_ov_da.py  (run from dk2/)"""
import json
import math
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = os.path.join(S, "v22it", "fonts", "Montserrat-ExtraBold.ttf")
SMS_FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
PRODUCT = os.path.join(S, "dk", "assets", "maskinren_produktbild_no.png")
TEAL, NAVY, BLACK, WHITE = (10, 147, 168, 255), (19, 38, 58, 255), (0, 0, 0, 255), (255, 255, 255, 255)


def f(size, path=FONT):
    return ImageFont.truetype(path, size)


def fit(text, size, width, path=FONT):
    while f(size, path).getlength(text) > width and size > 10:
        size -= 1
    return size


def frame(key, t, src="clean"):
    p = f"clean/{key}_clean.mp4" if src == "clean" else f"vid/{key}.mp4"
    o = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", p, "-frames:v", "1", "-f",
                        "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return Image.open(__import__("io").BytesIO(o)).convert("RGB")


class Ad:
    def __init__(self, key, W, H):
        self.key, self.W, self.H = key, W, H
        self.dir = os.path.join("ov", key)
        os.makedirs(self.dir, exist_ok=True)
        self.items = []

    def canvas(self):
        return Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))

    def add(self, name, img, t0, t1):
        img.save(os.path.join(self.dir, name + ".png"))
        self.items.append(dict(kind="png", file=f"{self.dir}/{name}.png", t0=round(t0, 3), t1=round(t1, 3)))

    def src_crop(self, box, t0, t1):
        self.items.append(dict(kind="src", box=list(box), t0=round(t0, 3), t1=round(t1, 3)))

    def seq(self, name, frames, t0):
        d = os.path.join(self.dir, name)
        os.makedirs(d, exist_ok=True)
        for i, im in enumerate(frames):
            im.save(os.path.join(d, f"{i:04d}.png"))
        self.items.append(dict(kind="seq", pattern=f"{d}/%04d.png", n=len(frames), t0=round(t0, 3),
                               t1=round(t0 + len(frames) / 30, 3)))

    def save(self, extra=None):
        spec = dict(items=self.items)
        if extra:
            spec.update(extra)
        json.dump(spec, open(os.path.join(self.dir, "spec.json"), "w"), indent=1)


def shadow(img, box, r, blur=10, alpha=90, dy=5):
    s = Image.new("RGBA", img.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(s).rounded_rectangle((x0, y0 + dy, x1, y1 + dy), r, fill=(0, 0, 0, alpha))
    img.alpha_composite(s.filter(ImageFilter.GaussianBlur(blur)))


def text_box(img, box, lines, r=24, fill=WHITE, color=BLACK, with_shadow=False, width=0.88):
    if with_shadow:
        shadow(img, box, r)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, r, fill=fill)
    x0, y0, x1, y1 = box
    fitted = [(t, fit(t, s, (x1 - x0) * width)) for t, s in lines]
    total = sum(s for _, s in fitted) * 1.12
    y = (y0 + y1) / 2 - total / 2
    for t, s in fitted:
        d.text(((x0 + x1) / 2, y + s * 0.56), t, font=f(s), fill=color, anchor="mm")
        y += s * 1.12
    return img


def gradient(W, H):
    img = Image.new("RGBA", (W, H), WHITE)
    top, bot = (233, 246, 248), (196, 233, 240)
    g = ImageDraw.Draw(img)
    for y in range(H):
        k = y / (H - 1)
        g.line([(0, y), (W, y)], fill=tuple(round(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,))
    return img


def product(img, S_, py, frame_=True, radius=26):
    W = img.size[0]
    prod = Image.open(PRODUCT).convert("RGB").resize((S_, S_), Image.LANCZOS)
    px = (W - S_) // 2
    shadow(img, (px, py, px + S_, py + S_), 28, blur=14, alpha=80, dy=8)
    if frame_:
        fr = Image.new("RGBA", (S_ + 14, S_ + 14), WHITE)
        m = Image.new("L", fr.size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, S_ + 13, S_ + 13), 32, fill=255)
        img.paste(fr, (px - 7, py - 7), m)
    m = Image.new("L", (S_, S_), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, S_ - 1, S_ - 1), radius, fill=255)
    img.paste(prod, (px, py), m)


def spaced(d, cx, cy, word, size, fill, spacing=9):
    fw = f(size)
    total = sum(fw.getlength(c) for c in word) + spacing * (len(word) - 1)
    x = cx - total / 2
    for c in word:
        d.text((x, cy), c, font=fw, fill=fill, anchor="lm")
        x += fw.getlength(c) + spacing


def star(d, cx, cy, r, fill=(245, 179, 1, 255)):
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


def endcard(stars_y, rating_y, word_y, word_size, prod_size, prod_y, head_y, head, head_size, offer_y, guar_y,
            btn_y0, btn_y1, offer_size=34):
    img = gradient(720, 1280)
    d = ImageDraw.Draw(img)
    for i in range(5):
        star(d, 276 + i * 42, stars_y, 17)
    d.text((360, rating_y), "4,8 ud af 5  ·  +15.000 kunder", font=f(24), fill=NAVY, anchor="mm")
    spaced(d, 360, word_y, "NORDVASK", word_size, NAVY)
    product(img, prod_size, prod_y)
    d = ImageDraw.Draw(img)
    d.text((360, head_y), head, font=f(fit(head, head_size, 660)), fill=TEAL, anchor="mm")
    d.text((360, offer_y), "4 PAKKER –50 %  ·  FRI FRAGT", font=f(offer_size), fill=NAVY, anchor="mm")
    d.text((360, guar_y), "Prøv i 30 dage – pengene tilbage", font=f(24), fill=NAVY, anchor="mm")
    d.rounded_rectangle((110, btn_y0, 610, btn_y1), 36, fill=TEAL)
    d.text((360, (btn_y0 + btn_y1) / 2), "SIKR DIG TILBUDDET", font=f(32), fill=WHITE, anchor="mm")
    return img


def inpaint_patch(img_rgb, box, dark=120):
    """Remove dark text pixels inside box (x0,y0,x1,y1) by inpainting; returns RGBA crop-sized patch."""
    a = np.array(img_rgb)
    x0, y0, x1, y1 = box
    roi = a[y0:y1, x0:x1].copy()
    g = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    m = (g < dark).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))
    out = cv2.inpaint(roi, m, 5, cv2.INPAINT_TELEA)
    return Image.fromarray(out).convert("RGBA")


# ---------------------------------------------------------------- A5 C4 (video30, 720x1280)
def a5c4():
    A = Ad("a5c4", 720, 1280)
    # 1) SEBUM label: only the small line changes (HUNDENS HUDFETT -> HUNDENS HUDFEDT)
    ref = frame("a5c4", 66.0)
    img = A.canvas()
    img.alpha_composite(inpaint_patch(ref, (440, 500, 705, 536)), (440, 500))
    ImageDraw.Draw(img).text((694, 506), "HUNDENS HUDFEDT", font=f(23), fill=(25, 25, 25, 255), anchor="ra")
    A.add("sebum", img, 65.70, 66.467)
    # 2) hair = protein / sebum = fat: DJURHÅR -> DYREHÅR, restore "= PROTEIN", "= FEDT"
    ref = frame("a5c4", 77.5)
    img = A.canvas()
    piece = ref.crop((456, 508, 456 + 208, 508 + 72)).convert("RGBA")
    m = Image.new("L", piece.size, 0)
    ImageDraw.Draw(m).rectangle((6, 6, piece.size[0] - 6, piece.size[1] - 6), fill=255)
    piece.putalpha(m.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(piece, (116, 508))
    ImageDraw.Draw(img).text((220, 545), "DYREHÅR", font=f(30), fill=(45, 45, 45, 255), anchor="mm")
    A.add("pf_hair", img, 76.80, 78.133)
    A.src_crop((350, 370, 665, 455), 77.0, 78.133)      # "= PROTEIN" as in the original (Vmake wiped it)
    A.src_crop((360, 705, 416, 757), 77.867, 78.133)    # "=" in front of FETT
    img = A.canvas()
    t = Image.new("RGBA", (260, 110), (0, 0, 0, 0))
    ImageDraw.Draw(t).text((10, 55), "FEDT", font=f(64), fill=(208, 25, 31, 255), anchor="lm")
    t = t.transform(t.size, Image.AFFINE, (1, 0.18, -10, 0, 1, 0), resample=Image.BICUBIC)
    img.alpha_composite(t, (408, 676))
    A.add("pf_fedt", img, 77.9, 78.133)
    # 3) enzyme names in the (now empty) white boxes
    A.add("amy", text_box(A.canvas(), (268, 585, 458, 722), [("Alfa-", 40), ("amylase", 40)], r=20), 142.467, 143.1)
    A.add("pro", text_box(A.canvas(), (222, 586, 512, 732), [("Protease", 54)], r=22), 150.9, 152.133)
    A.add("lip", text_box(A.canvas(), (276, 616, 534, 782), [("Lipase", 60)], r=22), 163.067, 164.333)

    # 4) badges (cover the Swedish badge completely)
    def badge(lines):
        img = A.canvas()
        box = (112, 400, 608, 880)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, 34, fill=WHITE)
        cx, cy, rr = 360, 640, 205
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=TEAL, width=22)
        d.ellipse((cx - rr + 34, cy - rr + 34, cx + rr - 34, cy + rr - 34), outline=TEAL, width=4)
        total = sum(s for _, s in lines) * 1.1
        y = cy - total / 2
        for t, s in lines:
            s2 = fit(t, s, 2 * (rr - 55))
            d.text((cx, y + s * 0.55), t, font=f(s2), fill=TEAL, anchor="mm")
            y += s * 1.1
        return img
    A.add("badge_afk", badge([("AFKALKER", 50), ("MASKINEN", 34)]), 186.10, 187.40)
    A.add("badge_alle", badge([("PASSER TIL", 44), ("ALLE VASKE-", 40), ("MASKINER", 46)]), 187.40, 188.333)

    # 5) offer cards (full frame), bars and end card
    def card(top_line, big, small):
        img = gradient(720, 1280)
        product(img, 500, 280, frame_=False, radius=30)
        d = ImageDraw.Draw(img)
        d.text((360, 236), top_line, font=f(40), fill=TEAL, anchor="mm")
        d.text((360, 846), big, font=f(fit(big, 74, 640)), fill=NAVY, anchor="mm")
        d.text((360, 1062), small, font=f(30), fill=NAVY, anchor="mm")
        return img
    A.add("cardA", card("UDSALG – SNART SLUT", "4 PAKKER –50 %", "Fri fragt  ·  20 kr pr. tablet"), 229.70, 232.70)
    BAR = (40, 806, 680, 892)
    A.add("bar1", text_box(A.canvas(), BAR, [("4 PAKKER –50 %  ·  FRI FRAGT", 38)], r=26), 232.867, 234.40)
    A.add("cardB", card("UDSALG – SNART SLUT", "20 KR / TABLET", "4 pakker til halv pris"), 234.40, 236.80)
    A.add("bar2", text_box(A.canvas(), BAR, [("PENGENE TILBAGE I 30 DAGE", 36)], r=26), 236.90, 240.90)
    A.add("endcard", endcard(232, 272, 322, 42, 380, 360, 800, "UDSALG – SNART SLUT", 58, 862, 906, 1000, 1072),
          242.967, 999)
    A.save()


# ---------------------------------------------------------------- A5 C5 (video33, 720x1280)
def a5c5():
    A = Ad("a5c5", 720, 1280)
    G = json.load(open("work/a5c5/words_global.json"))
    st = {}
    for w in G:
        st.setdefault(w["sent"], w["start"])
    HEAD = [("FORSKERE SKABER", 44), ("”SUPERENZYM”", 50)]
    A.add("nasa_a", text_box(A.canvas(), (55, 328, 495, 530), HEAD, r=22), 192.40, 192.933)
    A.add("nasa_b", text_box(A.canvas(), (0, 392, 500, 500), HEAD, r=18), 192.933, 193.467)
    A.add("nasa_c", text_box(A.canvas(), (0, 355, 530, 466), HEAD, r=18), 193.467, 193.967)
    A.add("nasa_d", text_box(A.canvas(), (0, 328, 535, 446), HEAD, r=18), 193.967, 194.50)
    A.add("amy", text_box(A.canvas(), (105, 470, 635, 754), [("ALFA-", 112), ("AMYLASE", 112)], r=30), 237.70, 239.433)
    A.add("pro", text_box(A.canvas(), (36, 490, 692, 712), [("PROTEASE", 130)], r=30), 248.25, 250.90)
    A.add("lip", text_box(A.canvas(), (85, 482, 655, 708), [("LIPASE", 130)], r=30), 265.25, 268.367)
    BUB = (90, 771, 619, 854)

    def sms(lines, cursor=False):
        img = A.canvas()
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(BUB, 24, fill=(188, 180, 181, 255))
        fs = f(23, SMS_FONT)
        y = 797 if len(lines) == 2 else 812
        for i, t in enumerate(lines):
            d.text((112, y + i * 28), t + ("_" if cursor and i == len(lines) - 1 else ""), font=fs,
                   fill=(24, 22, 22, 255), anchor="lm")
        return img
    A.add("sms1", sms(["Første gang de ikke l"], cursor=True), 345.30, 345.95)
    A.add("sms2", sms(["Første gang de ikke lugter af våd hund.", "Tak"]), 345.95, 347.95)
    # product name card
    img = gradient(720, 1280)
    d = ImageDraw.Draw(img)
    spaced(d, 360, 236, "NORDVASK", 34, TEAL)
    d.text((360, 300), "MASKINREN", font=f(fit("MASKINREN", 80, 640)), fill=NAVY, anchor="mm")
    product(img, 420, 360)
    d = ImageDraw.Draw(img)
    for i in range(5):
        star(d, 276 + i * 42, 950, 17)
    d.text((360, 992), "4,8 ud af 5  ·  +15.000 kunder", font=f(26), fill=NAVY, anchor="mm")
    A.add("card_prod", img, 362.90, 367.733)

    def offer_card(big, bottom_pill=None, bottom_text=None):
        img = gradient(720, 1280)
        d = ImageDraw.Draw(img)
        d.text((360, 236), "UDSALG", font=f(60), fill=TEAL, anchor="mm")
        d.text((360, 310), big, font=f(fit(big, 78, 640)), fill=NAVY, anchor="mm")
        product(img, 420, 370)
        d = ImageDraw.Draw(img)
        if bottom_pill:
            pill(d, 968, bottom_pill)
        if bottom_text:
            d.text((360, 968), bottom_text, font=f(30), fill=NAVY, anchor="mm")
        return img
    t_years = min(389.267, st[82] - 0.12)
    t_bar = min(392.067, st[83] - 0.12)
    A.add("card_offer", offer_card("4 PAKKER –50 %", bottom_pill="FRI FRAGT"), 383.30, t_years)
    A.add("card_years", offer_card("HOLDER I 4 ÅR", bottom_text="4 pakker til halv pris"), t_years, 392.033)
    A.add("bar_30", text_box(A.canvas(), (40, 206, 680, 290), [("PENGENE TILBAGE I 30 DAGE", 36)], r=26), t_bar,
          395.733)
    A.add("endcard", endcard(222, 260, 306, 40, 340, 336, 726, "UDSALG", 64, 778, 938, 984, 1056, offer_size=32),
          395.733, 999)
    A.save(extra=dict(cap_y_override=[[344.2, 348.85, 0.781]]))


# ---------------------------------------------------------------- A3 C1 (video5, 1080x1908)
def a3c1():
    A = Ad("a3c1", 1080, 1908)
    img = A.canvas()   # same size and baselines as the Swedish "SÄKER FÖR / AVLOPP" (caps 19 px, baselines 1016/1058)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((668, 966, 931, 1089), 22, fill=WHITE)
    d.text((799.5, 1016), "SIKKER FOR", font=f(26), fill=BLACK, anchor="ms")
    d.text((799.5, 1058), "AFLØB", font=f(26), fill=BLACK, anchor="ms")
    A.add("aflob", img, 236.75, 238.833)
    A.save()


# ---------------------------------------------------------------- A1 C4 (Maskinrent 4, 1080x1908)
def a1c4():
    A = Ad("a1c4", 1080, 1908)
    geom = json.load(open("ocr/a1c4_geom.json"))

    def label_frames(rows, w, h, text, size, r, text_dx):
        cys = np.array([g["cy"] for g in rows]); cxs = np.array([g["cx"] for g in rows])
        angs = np.array([g["ang"] for g in rows])
        k = 5
        sm = lambda v: np.convolve(np.pad(v, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
        cys, cxs, angs = sm(cys), sm(cxs), sm(angs)
        out = []
        for cx, cy, ang in zip(cxs, cys, angs):
            lab = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
            d = ImageDraw.Draw(lab)
            d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=WHITE)
            d.text((w / 2 + text_dx, h / 2), text, font=f(size), fill=BLACK, anchor="mm")
            rot = lab.rotate(-ang, resample=Image.BICUBIC, expand=True)
            img = A.canvas()
            img.alpha_composite(rot, (int(round(cx - rot.size[0] / 2)), int(round(cy - rot.size[1] / 2))))
            out.append(img)
        return out
    l1 = [g for g in geom if g["t"] < 133.29]
    l2 = [g for g in geom if g["t"] >= 133.29]
    # Swedish text sizes: "Syreblekmedel" ~340 px wide, "Natriumperkarbonat (syreblekmedel)" ~586 px wide
    s1 = fit("Syreblekmedel", 80, 340)
    s2 = fit("Natriumperkarbonat (syreblekmedel)", 60, 586)
    A.seq("lab1", label_frames(l1, 1040, 134, "Iltblegemiddel", s1, 0, -84), l1[0]["t"])
    A.seq("lab2", label_frames(l2, 1004, 120, "Natriumperkarbonat (iltblegemiddel)", s2, 14, 0), l2[0]["t"])
    A.save()


if __name__ == "__main__":
    for fn in (a5c4, a5c5, a3c1, a1c4):
        fn()
        print(fn.__name__, "ok")
