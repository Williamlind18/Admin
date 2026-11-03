#!/usr/bin/env python3
"""Remove free-floating white overlay text (titles, offer graphics) that has no caption box.

remove_captions.py handles boxed captions. This handles the rest: white or near-white letters, often
with a dark outline or shadow, drawn straight on the footage (video 39: the opening title "One enzyme
tablet. This is what came out of a 'clean' washing machine." and the "BUY 2 GET 2 FREE / 30 Day money
back guarantee" graphic). The text pixels are found per frame (bright, low saturation), grown to take
in the outline, and filled with the same push-pull fill as remove_captions.py. Put the new text on top
afterwards (an ASS line in the same place hides what is left).

Usage: remove_overlay_text.py SRC.mp4 OUT.mp4 --region F0-F1:X0,Y0,X1,Y1 [--region ...]
       [--min 200] [--grow 6] [--blur F0-F1:SIGMA] [--bridge F0-F1]
  --region  frame range (inclusive) and box where text may appear
  --min     a pixel counts as text if all of R, G, B are >= MIN and max-min < 40
  --grow    pixels added around each letter (outline, shadow, anti-aliasing)
  --blur    extra Gaussian blur over whole frames, e.g. to make a defocused competitor box unreadable
  --bridge  replace frames F0..F1 with a cross-fade from frame F0-1 to frame F1+1, for a few frames where
            the text fills most of the picture (video 39: a 10-frame zoom of "money back guarantee")
"""
import argparse
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe, probe  # noqa: E402
from remove_captions import pushpull  # noqa: E402


def main():
    import cv2
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--region", action="append", default=[])
    ap.add_argument("--blur", action="append", default=[])
    ap.add_argument("--bridge", action="append", default=[])
    ap.add_argument("--min", type=int, default=200)
    ap.add_argument("--grow", type=int, default=6)
    ap.add_argument("--crf", type=int, default=12)
    a = ap.parse_args()
    regions = []
    for r in a.region:
        fr, box = r.split(":")
        f0, f1 = (int(v) for v in fr.split("-"))
        regions.append((f0, f1, [int(v) for v in box.split(",")]))
    blurs = []
    for b in a.blur:
        fr, s = b.split(":")
        f0, f1 = (int(v) for v in fr.split("-"))
        blurs.append((f0, f1, float(s)))
    bridges = [tuple(int(v) for v in b.split("-")) for b in a.bridge]
    info = probe(a.src)
    W, H, fps = info["width"], info["height"], info["fps"]
    rate = "30000/1001" if abs(fps - 29.97) < 0.01 else str(fps)
    dec = subprocess.Popen([ffmpeg_exe(), "-nostdin", "-v", "error", "-i", a.src, "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([ffmpeg_exe(), "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", rate, "-i", "-", "-c:v", "libx264", "-preset", "medium",
                            "-crf", str(a.crf), "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(1)
    k = np.ones((2 * a.grow + 1, 2 * a.grow + 1), np.uint8)
    n, touched = 0, 0
    prev, held = None, []
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        for f0, f1, (x0, y0, x1, y1) in regions:
            if not f0 <= n <= f1:
                continue
            crop = f[y0:y1, x0:x1].astype(np.float32)
            mx, mn = crop.max(2), crop.min(2)
            text = ((mn >= a.min) & (mx - mn < 40)).astype(np.uint8)
            if text.sum() < 20:
                continue
            hole = cv2.dilate(text, k).astype(np.float32)
            est = pushpull(crop, 1 - hole) + rng.normal(0, 1.4, crop.shape).astype(np.float32)
            alpha = np.maximum(cv2.GaussianBlur(hole, (0, 0), 1.5), hole)[..., None]
            f[y0:y1, x0:x1] = (crop * (1 - alpha) + est * alpha).clip(0, 255).astype(np.uint8)
            touched += 1
        for f0, f1, s in blurs:
            if f0 <= n <= f1:
                f = cv2.GaussianBlur(f, (0, 0), s)
        br = next(((b0, b1) for b0, b1 in bridges if b0 <= n <= b1), None)
        if br:
            held.append(n)
        else:
            if held and prev is not None:
                for i in range(len(held)):
                    w = (i + 1) / (len(held) + 1)
                    enc.stdin.write((prev.astype(np.float32) * (1 - w) + f.astype(np.float32) * w)
                                    .clip(0, 255).astype(np.uint8).tobytes())
                held = []
            enc.stdin.write(f.tobytes())
            prev = f
        n += 1
    for _ in held:  # a bridge that runs to the end: hold the last good frame
        enc.stdin.write(prev.tobytes())
    enc.stdin.close()
    enc.wait()
    print(f"{n} frames, text filled in {touched} region-frames")


if __name__ == "__main__":
    main()
