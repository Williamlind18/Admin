#!/usr/bin/env python3
"""Read the original voiceover from the ad's own burned-in captions, with timestamps.

Many ads carry word-synced captions (e.g. black text in white boxes). Cropping the caption band
every few frames, keeping only crops where the caption changed and tiling them with their start
times gives a transcript with ~0.2 s timing, so the user does not need to paste one (video 22).
Open the caps_NN.png sheets with Read and write the lines down with their start times.

The band is given per time range, because the captions can sit in different places (video 22:
y 300-360 for the first 9.4 s, y 882-942 after). Find it on analyze_video.py's contact sheets.

Usage: caption_sheets.py SRC.mp4 OUTDIR --band 0-9.4:300-360 --band 9.4-999:882-942
       [--x 100-620] [--step 5] [--change 0.03]
Writes OUTDIR/caps_NN.png (84 crops per sheet) and OUTDIR/times.txt.
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe, probe  # noqa: E402


def parse_band(s):
    tr, yr = s.split(":")
    t0, t1 = (float(v) for v in tr.split("-"))
    y0, y1 = (int(v) for v in yr.split("-"))
    return t0, t1, y0, y1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("outdir")
    ap.add_argument("--band", action="append", required=True, help="T0-T1:Y0-Y1 (seconds : source pixels)")
    ap.add_argument("--x", default="", help="X0-X1 crop (default: middle 72 %% of the width)")
    ap.add_argument("--step", type=int, default=5, help="look at every Nth frame")
    ap.add_argument("--change", type=float, default=0.03, help="share of changed white pixels that counts as a new caption")
    a = ap.parse_args()
    os.makedirs(a.outdir, exist_ok=True)
    info = probe(a.src)
    W, H, fps = info["width"], info["height"], info["fps"]
    bands = [parse_band(b) for b in a.band]
    x0, x1 = (int(v) for v in a.x.split("-")) if a.x else (int(W * 0.14), int(W * 0.86))
    bh = max(y1 - y0 for _, _, y0, y1 in bands)

    p = subprocess.Popen([ffmpeg_exe(), "-v", "error", "-i", a.src, "-vf", f"select='not(mod(n\\,{a.step}))'",
                          "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    kept, last, k = [], None, 0
    while True:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        t = k * a.step / fps
        k += 1
        band = next(((y0, y1) for t0, t1, y0, y1 in bands if t0 <= t < t1), None)
        if band is None:
            continue
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        crop = np.zeros((bh, x1 - x0, 3), np.uint8)
        crop[:band[1] - band[0]] = f[band[0]:band[1], x0:x1]
        sig = crop.min(axis=2) > 235
        if last is None or (sig ^ last).mean() > a.change:
            kept.append((t, crop))
            last = sig
    print(f"{len(kept)} distinct caption crops")

    font = ImageFont.load_default()
    per_col, cols, lw = 28, 3, 70
    cw = (x1 - x0) + lw
    for s in range(0, len(kept), per_col * cols):
        chunk = kept[s:s + per_col * cols]
        img = Image.new("RGB", (cols * cw, per_col * bh), (40, 40, 40))
        d = ImageDraw.Draw(img)
        for i, (t, c) in enumerate(chunk):
            x, y = (i // per_col) * cw, (i % per_col) * bh
            d.text((x + 2, y + bh // 2 - 6), f"{t:6.2f}", fill=(255, 255, 0), font=font)
            img.paste(Image.fromarray(c), (x + lw, y))
        img.save(os.path.join(a.outdir, f"caps_{s // (per_col * cols):02d}.png"))
    with open(os.path.join(a.outdir, "times.txt"), "w") as fh:
        fh.writelines(f"{t:.3f}\n" for t, _ in kept)


if __name__ == "__main__":
    main()
