#!/usr/bin/env python3
"""Translate moving white label boxes with black text (e.g. "WEEK" / "TWO") frame by frame.

Some ads put short labels in white rectangles that slide in and move from shot to shot (video 51:
"WEEK | TWO", "MONTH | TWO", "MONTH | THREE" over the footage). A fixed ASS box can't follow them.
For every frame in a range this finds the black words that have white all around them (the label
boxes) inside a band, paints a white rectangle over each word (widened when the new word is longer)
and draws the target-language word in black at the same letter height, so the labels keep their
position and animation. Words are matched top to bottom, then left to right. A box outline alone is
not enough: the box merged with white backgrounds or ran off the frame edge in video 51.

Usage: relabel_boxes.py SRC.mp4 OUT.mp4 --range T0-T1:Y0-Y1:WORD1|WORD2 [--range ...]
       [--font Montserrat-ExtraBold.ttf] [--min-h 16] [--max-h 60] [--ring 0.6] [--test DIR --at 40,45]
  --range  time range (s), vertical band (px) where the boxes sit, and the words top to bottom
  --test   write before/after PNGs of the frames at --at (seconds) to DIR and stop
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe, probe  # noqa: E402


def find_boxes(f, y0, y1, a):
    """Label words = clusters of black letters with white all around them (the label box). Works when
    the box itself merges with a white background or runs off the frame edge, where a box contour fails."""
    import cv2
    band = f[y0:y1]
    dark = (band.max(axis=2) < 90).astype(np.uint8)
    white = band.min(axis=2) >= 225
    words = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, np.ones((3, 7), np.uint8))  # small: a wider kernel bridged the box margin into dark backgrounds
    k, lab, st, _ = cv2.connectedComponentsWithStats(words, connectivity=8)
    cand = []
    Hb, Wb = dark.shape
    for j in range(1, k):
        x, y, w, h, area = st[j]
        if not (a.min_h <= h <= a.max_h and w >= 8):
            continue
        top = white[max(0, y - 6):max(0, y - 1), x:x + w]
        bot = white[y + h + 1:y + h + 6, x:x + w]
        if top.size == 0 or bot.size == 0 or min(top.mean(), bot.mean()) < a.ring:
            continue
        cand.append([x, y, x + w, y + h])
    # one label per text line: join pieces that overlap vertically and sit close together
    cand.sort(key=lambda b: (b[1] + b[3]) / 2)
    lines = []
    for b in cand:
        for L in lines:
            ov = min(L[3], b[3]) - max(L[1], b[1])
            gap = max(b[0] - L[2], L[0] - b[2])
            if ov > 0.5 * min(L[3] - L[1], b[3] - b[1]) and gap < 40:
                L[0], L[1], L[2], L[3] = min(L[0], b[0]), min(L[1], b[1]), max(L[2], b[2]), max(L[3], b[3])
                break
        else:
            lines.append(list(b))
    boxes = [(x0, y0_ + y0, x1 - x0, y1_ - y0_) for x0, y0_, x1, y1_ in lines if x1 - x0 >= a.min_w]
    return boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--range", action="append", default=[])
    ap.add_argument("--font", default=os.path.expanduser("~/.fonts/Montserrat-ExtraBold.ttf"))
    ap.add_argument("--min-w", type=int, default=30, help="min width of a word (px)")
    ap.add_argument("--min-h", type=int, default=16, help="letter height range (px)")
    ap.add_argument("--max-h", type=int, default=60)
    ap.add_argument("--ring", type=float, default=0.6, help="min share of white pixels around a word")
    ap.add_argument("--cap", type=float, default=0.74, help="cap height / font size of the font")
    ap.add_argument("--pad-x", type=int, default=9)
    ap.add_argument("--pad-y", type=int, default=7)
    ap.add_argument("--crf", type=int, default=14)
    ap.add_argument("--test")
    ap.add_argument("--at", default="")
    a = ap.parse_args()
    ranges = []
    for r in a.range:
        t, band, words = r.split(":", 2)
        t0, t1 = (float(v) for v in t.split("-"))
        y0, y1 = (int(v) for v in band.split("-"))
        ranges.append((t0, t1, y0, y1, words.split("|")))
    info = probe(a.src)
    W, H, fps = info["width"], info["height"], info["fps"]
    tests = sorted(int(round(float(v) * fps)) for v in a.at.split(",") if v) if a.test else []
    dec = subprocess.Popen([ffmpeg_exe(), "-nostdin", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-"], stdout=subprocess.PIPE)
    enc = None
    if not a.test:
        rate = "24000/1001" if abs(fps - 23.976) < 0.01 else ("30000/1001" if abs(fps - 29.97) < 0.01 else str(fps))
        enc = subprocess.Popen([ffmpeg_exe(), "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", rate, "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                "-crf", str(a.crf), "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    fonts = {}
    n, done = 0, 0
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        t = n / fps
        rr = next((r for r in ranges if r[0] <= t < r[1]), None)
        if tests and n not in tests:
            n += 1
            if n > tests[-1]:
                break
            continue
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        if rr:
            t0, t1, y0, y1, words = rr
            boxes = sorted(find_boxes(f, y0, y1, a), key=lambda b: (b[1], b[0]))  # top to bottom
            if boxes:
                orig = f.copy()
                im = Image.fromarray(f.copy())
                d = ImageDraw.Draw(im)
                for (x, y, w, h), word in zip(boxes, words):
                    size = max(10, int(h / a.cap))  # the English letters' height gives the font size
                    font = fonts.get(size) or fonts.setdefault(size, ImageFont.truetype(a.font, size))
                    bb = d.textbbox((0, 0), word, font=font)
                    tw = bb[2] - bb[0]
                    cx = x + w / 2
                    half = max(w, tw) / 2 + a.pad_x
                    d.rectangle([max(0, cx - half), y - a.pad_y, min(W - 1, cx + half), y + h + a.pad_y],
                                fill=(255, 255, 255))
                    tx = min(max(cx - tw / 2, 2), W - tw - 2) - bb[0]
                    ty = y + h / 2 - (bb[1] + bb[3]) / 2
                    d.text((tx, ty), word, font=font, fill=(0, 0, 0))
                f = np.asarray(im)
                done += 1
                if tests:
                    Image.fromarray(np.hstack([orig, f])).save(os.path.join(a.test, f"relabel_{t:.2f}.png"))
        if tests:
            n += 1
            if n > tests[-1]:
                break
            continue
        enc.stdin.write(np.ascontiguousarray(f).tobytes())
        n += 1
    dec.stdout.close()
    if enc:
        enc.stdin.close()
        enc.wait()
    print(f"{n} frames, labels redrawn in {done}")


if __name__ == "__main__":
    main()
