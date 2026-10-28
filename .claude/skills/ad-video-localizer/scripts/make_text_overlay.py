#!/usr/bin/env python3
"""Headline overlay: the user's own offer text as a transparent PNG the size of
the video, to replace burned-in text that was removed (e.g. with Vmake) or to
add an offer banner. Burn it in with render.py --overlay (default: whole video).

Each --line is "SIZE|text~color|text~color..." where SIZE is the font size in
px at 1080 px video width (scaled to the real width) and color is white, accent
(the brand colour, --accent) or a #rrggbb value. Lines that are wider than
--max-width shrink to fit. White text gets a thin dark outline and a soft
shadow so it reads on busy footage. Montserrat ExtraBold by default.

Example (Maskinrent video25, replacing "BUY 2 GET 2 FREE / LAST CHANCE / ONLY $9.99/PACK"):
  make_text_overlay.py --video clean.mp4 --font WORK/fonts/Montserrat-ExtraBold.ttf --out WORK/title.png \
      --top 0.125 --line "52|NORRTVÄTT~accent" --line "112|2-PACK ~white|−40 %~accent" \
      --line "112|SISTA CHANSEN~white" --line "64|ENDAST ~white|25 KR/TABLETT~accent"
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import probe  # noqa: E402


def color(name, accent):
    if name == "white":
        return (255, 255, 255, 255)
    if name == "accent":
        name = accent
    name = name.lstrip("#")
    return tuple(int(name[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--line", action="append", required=True)
    ap.add_argument("--top", type=float, default=0.12, help="top of the first line (fraction of height)")
    ap.add_argument("--gap", type=float, default=0.18, help="space between lines (fraction of line size)")
    ap.add_argument("--max-width", type=float, default=0.88, help="fraction of video width")
    ap.add_argument("--accent", default="#1cc4dc", help="brand colour (Norrtvätt teal, lightened to read on video)")
    a = ap.parse_args()
    info = probe(a.video)
    W, H = info["width"], info["height"]
    u = W / 1080

    text = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(text)
    y = round(H * a.top)
    for spec in a.line:
        size_s, *segs = spec.split("|")
        segs = [s.rsplit("~", 1) if "~" in s else (s, "white") for s in segs]
        size = round(float(size_s) * u)
        while True:
            f = ImageFont.truetype(a.font, size)
            widths = [d.textlength(t, font=f) for t, _ in segs]
            if sum(widths) <= W * a.max_width or size < 12:
                break
            size -= 2
        stroke = max(1, round(size * 0.045))
        x = (W - sum(widths)) / 2
        asc = f.getmetrics()[0]
        for (t, c), w in zip(segs, widths):
            d.text((x, y), t, font=f, fill=color(c, a.accent), stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
            x += w
        y += round(asc * 1.0 + size * a.gap)

    alpha = text.split()[3]
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda v: int(v * 0.55)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6 * u))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(shadow, (round(3 * u), round(5 * u)))
    out.alpha_composite(text)
    out.save(a.out)
    print(f"{a.out}: {W}x{H}, text from y={round(H * a.top)} to y={y} (captions at y={round(H * 0.75)})")


if __name__ == "__main__":
    main()
