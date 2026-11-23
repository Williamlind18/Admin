#!/usr/bin/env python3
"""Remove big burned-in titles letter by letter with LaMa, so a translated title can go in the same
place in the same style (no white box).

lama_inpaint.py fills whole rectangles, which is right for caption boxes but repaints a lot of footage
under a big title. This one builds a per-frame pixel mask from the title's colour inside a rectangle,
grows it over the outline/glow, and lets LaMa fill only those pixels (plus a feathered edge). Frames
outside the ranges are copied as they are.

Usage: lama_text_remove.py SRC.mp4 OUT.mp4 --model big-lama.pt --spec T0-T1:X0,Y0,X1,Y1:MODE[:GROW] [...]
       [--test DIR --at 4.0,33.0] [--crf 14]
MODE picks the text pixels (RGB):
  white   min(R,G,B) >= 200 and max-min < 45 (white titles with a dark outline or glow)
  glow    min >= 170 and max-min < 70 (soft glowing white/cyan text)
  silver  min >= 140 and max-min < 60 (white titles that shade to grey)
  faint   min >= 110 and max-min < 50 (the first second of a title that fades in)
  fainter min >= 80 and max-min < 40 (what is left of it over a grey scene)
  yellow  R > 235, G > 225, 90 < B < 200 (pale yellow titles; orange/white highlights are left alone)
  red     dark red text: R > 70, R > G + 40, R > B + 25, G < 90, plus the green underline bars
  green   white letters on a green sticker (white pixels next to green ones)
  dark    dark text inside the largest light shape (a pill): max(R,G,B) < 190
  white3d white letter faces plus the grey 3D extrusion next to them (3D titles)
  cyan    light cyan/white glowing letters (keeps green bubbles)
  rect    the whole rectangle (LaMa may rebuild letter shapes from what is left at the edges)
GROW (px, default 6) dilates the mask over the outline/shadow.
Video 51: the white "YOUR WASHER IS ALREADY CONTAMINATED", "AS LITTLE AS 2 WEEKS", "HOW DO YOU BREAK IT?",
the yellow "PROTEASE"/"LIPASE", "ALPHA AMYLASE", "FREE SHIPPING" and the text of the "60 day" pill. A
white box over them looked "gigantic" to the user; removing the letters and setting Swedish text in the
same style was what they wanted. Needs torch (CPU) and big-lama.pt (see lama_inpaint.py).
"""
import argparse
import os
import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe, probe  # noqa: E402


def text_mask(crop, mode):
    c = crop.astype(np.int16)
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(2), c.min(2)
    if mode == "white":
        m = (mn >= 200) & (mx - mn < 45)
    elif mode == "glow":
        m = (mn >= 170) & (mx - mn < 70)
    elif mode == "faint":  # a title still fading in (semi-transparent letters)
        m = (mn >= 110) & (mx - mn < 50)
    elif mode == "fainter":  # the last trace of a fading title over a grey scene
        m = (mn >= 80) & (mx - mn < 40)
    elif mode == "silver":  # white-to-grey 3D titles: everything light and unsaturated
        m = (mn >= 140) & (mx - mn < 60)
    elif mode == "yellow":
        m = (R > 235) & (G > 225) & (B > 90) & (B < 200)
    elif mode == "red":
        m = ((R > 70) & (R > G + 40) & (R > B + 25) & (G < 90)) | ((G > 150) & (G > R + 30) & (G > B + 60))
    elif mode == "green":  # only white pixels on or next to the green sticker (not white boxes behind it)
        import cv2
        gr = ((G > 150) & (G > R + 30) & (G > B + 60)).astype(np.uint8)
        m = (mn >= 200) & (cv2.dilate(gr, np.ones((9, 9), np.uint8)) > 0)
    elif mode == "dark":  # only dark pixels inside the light pill
        import cv2
        light = (mn >= 200).astype(np.uint8)
        cnts, _ = cv2.findContours(light, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        inside = np.zeros(R.shape, np.uint8)
        if cnts:
            cv2.drawContours(inside, [max(cnts, key=cv2.contourArea)], -1, 1, -1)
        m = (mx < 190) & (inside > 0)
    elif mode == "white3d":  # white letter faces plus their grey 3D extrusion (only next to the faces)
        import cv2
        face = ((mn >= 205) & (mx - mn < 40)).astype(np.uint8)
        face = cv2.morphologyEx(face, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        near = cv2.dilate(face, np.ones((19, 19), np.uint8)) > 0
        m = (face > 0) | (near & (mn >= 95) & (mx - mn < 45))
    elif mode == "cyan":  # light cyan/white glowing letters (green bubbles left alone)
        m = ((mn >= 160) & (mx - mn < 80) & (B >= G - 25)) | ((B > 170) & (G > 160) & (R > 100) & (B >= G - 10) & (G - R < 110))
    elif mode == "rect":
        m = np.ones(R.shape, bool)
    else:
        raise SystemExit(f"unknown mode {mode}")
    return m.astype(np.uint8)


def main():
    import cv2
    import torch
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--model", required=True)
    ap.add_argument("--spec", action="append", default=[])
    ap.add_argument("--crf", type=int, default=14)
    ap.add_argument("--test")
    ap.add_argument("--at", default="")
    a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("LAMA_THREADS", "4")))
    model = torch.jit.load(a.model, map_location="cpu").eval()
    specs = []
    for s in a.spec:
        parts = s.split(":")
        t0, t1 = (float(v) for v in parts[0].split("-"))
        x0, y0, x1, y1 = (int(v) for v in parts[1].split(","))
        grow = int(parts[3]) if len(parts) > 3 else 6
        specs.append((t0, t1, x0, y0, x1, y1, parts[2], grow))
    info = probe(a.src)
    W, H, fps = info["width"], info["height"], info["fps"]
    rate = "24000/1001" if abs(fps - 23.976) < 0.01 else ("30000/1001" if abs(fps - 29.97) < 0.01 else str(fps))
    tests = sorted(int(round(float(v) * fps)) for v in a.at.split(",") if v) if a.test else []
    dec = subprocess.Popen([ffmpeg_exe(), "-nostdin", "-v", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-"], stdout=subprocess.PIPE)
    enc = None
    if not a.test:
        enc = subprocess.Popen([ffmpeg_exe(), "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", rate, "-i", "-", "-c:v", "libx264", "-preset", "medium",
                                "-crf", str(a.crf), "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    n, done, t_start = 0, 0, time.time()
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        if tests and n not in tests:
            n += 1
            if n > tests[-1]:
                break
            continue
        t = n / fps
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        orig = img.copy() if tests else None
        for t0, t1, x0, y0, x1, y1, mode, grow in specs:
            if not t0 <= t < t1:
                continue
            m = text_mask(img[y0:y1, x0:x1], mode)
            if m.sum() < 60:
                continue
            m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1))
            m = cv2.dilate(m, k)
            full = np.zeros((H, W), np.uint8)
            full[y0:y1, x0:x1] = m
            ys, xs = np.nonzero(full)
            c0 = max(0, (ys.min() - 48) // 8 * 8)
            c1 = min(H, ((ys.max() + 48 + 7) // 8) * 8)
            d0 = max(0, (xs.min() - 48) // 8 * 8)
            d1 = min(W, ((xs.max() + 48 + 7) // 8) * 8)
            crop = img[c0:c1, d0:d1]
            mm = full[c0:c1, d0:d1].astype(np.float32)
            with torch.no_grad():
                ti = torch.from_numpy(crop).permute(2, 0, 1)[None].float() / 255
                tm = torch.from_numpy(mm)[None, None]
                out = model(ti, tm)[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255
            out = out[:crop.shape[0], :crop.shape[1]]
            alpha = np.maximum(cv2.GaussianBlur(mm, (0, 0), 1.5), mm)[..., None]
            img[c0:c1, d0:d1] = (out * alpha + crop * (1 - alpha)).clip(0, 255).astype(np.uint8)
            done += 1
        if tests:
            cv2.imwrite(os.path.join(a.test, f"lama_{t:.2f}.png"), cv2.cvtColor(np.hstack([orig, img]), cv2.COLOR_RGB2BGR))
            n += 1
            if n > tests[-1]:
                break
            continue
        enc.stdin.write(img.tobytes())
        n += 1
        if n % 500 == 0:
            print(f"frame {n}, {done} inpaints, {time.time() - t_start:.0f}s", flush=True)
    dec.stdout.close()
    dec.terminate()
    if enc:
        enc.stdin.close()
        enc.wait()
    print(f"{n} frames, {done} inpaints, {time.time() - t_start:.0f}s")


if __name__ == "__main__":
    main()
