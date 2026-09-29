#!/usr/bin/env python3
"""End card: the user's product photo plus a white offer box with black
Montserrat ExtraBold text, as a transparent PNG the size of the video. Burn it
in with render.py --overlay card.png --overlay-start S --overlay-end E.

Layout that the user approved (Maskinrent video 3, 1080x1332): the photo
centred near the top in a white rounded frame, the offer box right under it,
both with a soft shadow, and the captions (y = 0.75) still free below.

The product photo can be a crop of a screenshot of the user's product page
(store domains are usually blocked in the sandbox): pass --crop x0,y0,x1,y1 a
few pixels inside the photo so no page background shows.

Usage: make_endcard.py --product shot.png [--crop 387,16,909,538] --video SRC.mp4
       --title "HÖSTREA" --subtitle "Upp till 50 % rabatt" --font WORK/fonts/Montserrat-ExtraBold.ttf
       --out WORK/card.png
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import probe  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", required=True, help="product photo or screenshot")
    ap.add_argument("--crop", help="x0,y0,x1,y1 of the photo inside --product")
    ap.add_argument("--video", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--photo", type=float, default=0.52, help="photo width as a fraction of video width")
    ap.add_argument("--top", type=float, default=0.072, help="top of the photo as a fraction of video height")
    a = ap.parse_args()
    info = probe(a.video)
    W, H = info["width"], info["height"]
    u = W / 1080  # every size below was tuned at 1080 px wide

    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def mask(size, r):
        m = Image.new("L", size, 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
        return m

    def shadow(x0, y0, x1, y1, r):
        s = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(s).rounded_rectangle((x0, y0 + 10 * u, x1, y1 + 10 * u), r, fill=(0, 0, 0, 110))
        card.alpha_composite(s.filter(ImageFilter.GaussianBlur(22 * u)))

    prod = Image.open(a.product).convert("RGB")
    if a.crop:
        prod = prod.crop(tuple(int(v) for v in a.crop.split(",")))
    S = round(W * a.photo)
    prod = prod.resize((S, round(S * prod.height / prod.width)), Image.LANCZOS)
    px, py = (W - S) // 2, round(H * a.top)
    r, pad = round(34 * u), round(8 * u)
    shadow(px, py, px + S, py + prod.height, r)
    frame = Image.new("RGBA", (S + 2 * pad, prod.height + 2 * pad), (255, 255, 255, 255))
    card.paste(frame, (px - pad, py - pad), mask(frame.size, r + pad))
    card.paste(prod, (px, py), mask(prod.size, r))

    f1 = ImageFont.truetype(a.font, round(100 * u))
    f2 = ImageFont.truetype(a.font, round(56 * u))
    bw = round(700 * u)
    bh = round((196 if a.subtitle else 130) * u)
    bx, by = (W - bw) // 2, py + prod.height + round(30 * u)
    shadow(bx, by, bx + bw, by + bh, round(36 * u))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), round(36 * u), fill=(255, 255, 255, 255))
    d.text((W // 2, by + round((66 if a.subtitle else 65) * u)), a.title, font=f1, fill=(0, 0, 0, 255), anchor="mm")
    if a.subtitle:
        d.text((W // 2, by + round(150 * u)), a.subtitle, font=f2, fill=(0, 0, 0, 255), anchor="mm")
    card.save(a.out)
    print(f"{a.out}: {W}x{H}, photo {S}px at y={py}, offer box bottom at y={by + bh} "
          f"(captions are centred at y={round(H * 0.75)})")


if __name__ == "__main__":
    main()
