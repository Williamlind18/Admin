#!/usr/bin/env python3
"""Remove the original's burned-in captions (a white box with black text, centred) from every frame.

Per frame it finds the caption box inside the band for that time, then fills the box with a smooth
push-pull fill: a pyramid blur of the surrounding pixels, feathered at the edge with light grain.
The result is a soft blurred patch with no text, and the new captions are placed over it (video 22).
Frames without a caption are left untouched. Spatial inpainting (OpenCV Telea) smeared streaks and
left white edges; this fill looked cleaner.

Usage: remove_captions.py SRC.mp4 OUT.mp4 --band 0-9.4:296-364 --band 9.4-999:876-946
       [--log boxes.json] [--pad 9]
The band (T0-T1:Y0-Y1, source pixels) should be ~15 px taller than the box on each side.
Then check: the log lists frames where no box was found. Compare those times with the caption
sheets (caption_sheets.py) and look at a few before/after frames.
Place the new captions at the box centre: --y (y0+y1)/2/H in chunk_captions.py / make_captions.py.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe, probe  # noqa: E402


def parse_band(s):
    tr, yr = s.split(":")
    t0, t1 = (float(v) for v in tr.split("-"))
    y0, y1 = (int(v) for v in yr.split("-"))
    return t0, t1, y0, y1


def caption_box(f, y0, y1):
    """(x0, top, x1, bottom) of the centred white caption box in rows y0..y1, or None."""
    W = f.shape[1]
    cx = W // 2
    band = f[y0:y1].astype(np.int16)
    white = band.min(axis=2) > 222
    dark = band.max(axis=2) < 90
    cand = ndimage.binary_closing(white.mean(axis=0) > 0.30, structure=np.ones(25))
    lab, _ = ndimage.label(cand)
    ids = np.unique(lab[cx - 20:cx + 21])
    ids = ids[ids > 0]
    if not len(ids):
        return None
    xs = np.where(lab == ids[0])[0]
    r = min(cx - xs[0], xs[-1] - cx)          # the box is centred: if one side merged with a white background, mirror the other
    if r < 25:
        return None
    a, b = cx - r, cx + r
    if dark[:, a:b + 1].mean() < 0.02:        # no text inside: a white object, not a caption
        return None
    ys = np.where((white | dark)[:, a:b + 1].mean(axis=1) > 0.75)[0]
    if len(ys) < 25:
        return None
    return int(a), int(y0 + ys[0]), int(b), int(y0 + ys[-1])


def pushpull(g, valid, levels=5):
    import cv2
    pyr = [(g * valid[..., None], valid)]
    for _ in range(levels):
        im, w = pyr[-1]
        pyr.append((cv2.pyrDown(im), cv2.pyrDown(w)))
    im, w = pyr[-1]
    est = im / np.maximum(w, 1e-4)[..., None]
    for i in range(levels - 1, -1, -1):
        im, w = pyr[i]
        up = cv2.resize(est, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_LINEAR)
        ww = np.clip(w * 4, 0, 1)[..., None]
        est = im / np.maximum(w, 1e-4)[..., None] * ww + up * (1 - ww)
    return est


def main():
    import cv2
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--band", action="append", required=True, help="T0-T1:Y0-Y1 (seconds : source pixels)")
    ap.add_argument("--log", default="")
    ap.add_argument("--pad", type=int, default=9)
    ap.add_argument("--crf", type=int, default=12)
    a = ap.parse_args()
    info = probe(a.src)
    W, H, fps = info["width"], info["height"], info["fps"]
    bands = [parse_band(b) for b in a.band]
    rate = "30000/1001" if abs(fps - 29.97) < 0.01 else str(fps)
    dec = subprocess.Popen([ffmpeg_exe(), "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen([ffmpeg_exe(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", rate, "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf),
                            "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(1)
    boxes, n, P = [], 0, a.pad
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        t = n / fps
        band = next(((y0, y1) for t0, t1, y0, y1 in bands if t0 <= t < t1), None)
        box = caption_box(f, *band) if band else None
        boxes.append(box)
        if box:
            x0, y0, x1, y1 = box
            X0, Y0, X1, Y1 = max(0, x0 - P), y0 - P, min(W - 1, x1 + P), y1 + P
            cy0, cy1 = max(0, Y0 - 160), min(H, Y1 + 160)
            crop = f[cy0:cy1].astype(np.float32)
            hole = np.zeros(crop.shape[:2], np.float32)
            hole[Y0 - cy0:Y1 - cy0 + 1, X0:X1 + 1] = 1
            est = pushpull(crop, 1 - hole) + rng.normal(0, 1.6, crop.shape).astype(np.float32)
            alpha = cv2.GaussianBlur(cv2.dilate(hole, np.ones((5, 5), np.uint8)), (0, 0), 2.0)
            alpha = np.maximum(alpha, hole)[..., None]
            f[cy0:cy1] = (crop * (1 - alpha) + est * alpha).clip(0, 255).astype(np.uint8)
        enc.stdin.write(f.tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    if a.log:
        json.dump(boxes, open(a.log, "w"))
    missing, runs = [i for i, b in enumerate(boxes) if b is None], []
    for i in missing:
        if runs and i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    print(f"{n} frames, {n - len(missing)} with a caption box removed")
    print("no box found at: " + (", ".join(f"{s / fps:.2f}-{e / fps:.2f}s" for s, e in runs) or "-"))


if __name__ == "__main__":
    main()
