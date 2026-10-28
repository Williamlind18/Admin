#!/usr/bin/env python3
"""Read and remove burned-in captions (white boxes with dark text, the usual UGC-ad style).

  read    OCR every caption with its time -> CAPS.json, plus mosaics caps_N.png of the caption
          strip (open them with Read and correct the OCR by eye). This gives the original
          script with timestamps when the user has no transcript.
  remove  Paint every caption box out with OpenCV inpainting (and optionally a big hook text
          at the top in the first seconds), and optionally cut the video at --end (e.g. the
          competitor's end card). Writes a silent video; the new voice/captions go on top.
          Put the new captions at the same height (make_captions.py --y BOX_CENTRE / HEIGHT),
          so they cover the slight smudge the inpainting leaves.

Find the box rows first: grab a frame with a caption and look at it (the box was rows 890-938
of 1280 on the Norrtvätt "panel" video). The box width is measured per frame from the clear
white margin above the text, so boxes of any width are found.

Usage:
  burned_captions.py read   SRC.mp4 --box 890-938 --out WORK/caps.json
  burned_captions.py remove SRC.mp4 --box 890-938 --out WORK/clean.mp4 \\
        [--hook 320-510:4.45] [--end 220.32]
Needs opencv-python-headless (pip) and, for `read`, tesseract-ocr (apt).
"""
import argparse
import collections
import json
import os
import re
import subprocess
import sys
import tempfile

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe  # noqa: E402


def box_extent(f, y0, y1):
    """Columns of the caption box: white in the margin rows above the text, with ink below."""
    band = f[y0 + 2:y0 + 9].astype(np.int16)
    white = (band.min(axis=2) >= 225) & ((band.max(axis=2) - band.min(axis=2)) < 30)
    col = white.mean(axis=0) > 0.8
    ink = (cv2.cvtColor(f[y0 + 10:y1 - 9], cv2.COLOR_BGR2GRAY) < 90).any(axis=0)
    xs = np.where(col)[0]
    if len(xs) == 0:
        return None
    runs, s, p = [], xs[0], xs[0]
    for x in xs[1:]:
        if x > p + 10:
            runs.append((s, p))
            s = x
        p = x
    runs.append((s, p))
    c = f.shape[1] // 2
    best = None
    for a, b in runs:
        if b - a < 40 or not (a <= c + 60 and b >= c - 60) or ink[a:b + 1].sum() < 8:
            continue
        if best is None or b - a > best[1] - best[0]:
            best = (int(a), int(b))
    return best


def hook_mask(f, r0, r1):
    """Big white/red hook text (white letters >= 242, red highlight boxes)."""
    band = f[r0:r1].astype(np.int16)
    b, g, r = band[..., 0], band[..., 1], band[..., 2]
    core = ((band.min(axis=2) >= 242) | ((r > 100) & (r - g > 45) & (r - b > 35))).astype(np.uint8) * 255
    core = cv2.morphologyEx(core, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    m = np.zeros(f.shape[:2], np.uint8)
    m[r0:r1] = cv2.dilate(core, np.ones((15, 15), np.uint8))
    return m


def ocr(crop, td):
    img = cv2.resize(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    _, img = cv2.threshold(img, 140, 255, cv2.THRESH_BINARY)
    img = cv2.copyMakeBorder(img, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
    p = os.path.join(td, "c.png")
    cv2.imwrite(p, img)
    return subprocess.run(["tesseract", p, "-", "--psm", "7", "-l", "eng"], capture_output=True, text=True).stdout.strip()


def cmd_read(a, y0, y1):
    cap = cv2.VideoCapture(a.src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    td = tempfile.mkdtemp()
    segs, cur, k = [], None, 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        e = box_extent(f, y0, y1)
        sig = None
        if e:
            ink = cv2.cvtColor(f[y0 + 4:y1 - 4, e[0]:e[1] + 1], cv2.COLOR_BGR2GRAY) < 110
            sig = cv2.resize(ink.astype(np.uint8) * 255, (64, 8), interpolation=cv2.INTER_AREA) > 60
        if e and cur and abs(e[0] - cur["x0"]) <= 6 and abs(e[1] - cur["x1"]) <= 6 and (sig ^ cur["sig"]).mean() < 0.08:
            cur["end"] = k + 1
            if cur["end"] - cur["start"] in (4, 10, 16):   # read a few frames in, after the pop-in animation
                cur["crop"] = f[y0 + 4:y1 - 4, e[0]:e[1] + 1].copy()
        else:
            if cur:
                segs.append(cur)
            cur = None if not e else {"start": k, "end": k + 1, "x0": e[0], "x1": e[1], "sig": sig,
                                      "crop": f[y0 + 4:y1 - 4, e[0]:e[1] + 1].copy(), "mid": None}
        k += 1
    if cur:
        segs.append(cur)
    norm = lambda t: re.sub(r"[^a-z0-9' ]", "", t.lower()).strip()  # noqa: E731
    out = []
    for s in segs:
        txt = ocr(s["crop"], td)
        if out and s["start"] / fps - out[-1]["end"] < 0.2 and norm(txt) and (
                norm(txt) in norm(out[-1]["text"]) or norm(out[-1]["text"]) in norm(txt)):
            out[-1]["end"] = round(s["end"] / fps, 3)       # flicker of the same caption
            if len(norm(txt)) > len(norm(out[-1]["text"])):
                out[-1]["text"] = txt
            continue
        out.append({"start": round(s["start"] / fps, 3), "end": round(s["end"] / fps, 3), "text": txt})
    json.dump(out, open(a.out, "w"), indent=1, ensure_ascii=False)
    # mosaics of the caption strip in the middle of each caption, for reading by eye
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    tiles = []
    for i, m in enumerate(out):
        cap.set(cv2.CAP_PROP_POS_FRAMES, int((m["start"] * 0.35 + m["end"] * 0.65) * fps))
        ok, f = cap.read()
        strip = cv2.resize(f[y0 - 6:y1 + 6], (520, round((y1 - y0 + 12) * 520 / W)))
        lab = np.full((strip.shape[0], 90, 3), 255, np.uint8)
        cv2.putText(lab, f"{i:03d}", (4, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2)
        cv2.putText(lab, f"{m['start']:.1f}", (4, strip.shape[0] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        tiles.append(np.hstack([lab, strip]))
    base = os.path.splitext(a.out)[0]
    for p in range(0, len(tiles), 60):
        ch = tiles[p:p + 60]
        while len(ch) % 2:
            ch.append(np.full_like(tiles[0], 255))
        h = len(ch) // 2
        cv2.imwrite(f"{base}_{p // 60 + 1}.png", np.hstack([np.vstack(ch[:h]), np.vstack(ch[h:])]))
    for m in out:
        print(f"{m['start']:7.2f}-{m['end']:7.2f}  {m['text']}")
    print(f"{len(out)} captions -> {a.out} and {base}_N.png")


def cmd_remove(a, y0, y1):
    cap = cv2.VideoCapture(a.src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    last = int(round(a.end * fps)) if a.end else 10 ** 9
    hook = None
    if a.hook:
        rows, t = a.hook.split(":")
        hook = (*(int(v) for v in rows.split("-")), float(t))
    p = subprocess.Popen([ffmpeg_exe(), "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "fast",
                          "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    frames, ext = collections.deque(), collections.deque()
    done = k = 0

    def emit(i):
        es = [e for e in list(ext)[max(0, i - 2):i + 3] if e]   # union over +-2 frames covers pop-in/out
        f = frames[i]
        mask = np.zeros((H, W), np.uint8)
        if es:
            x0, x1 = max(0, min(e[0] for e in es) - 10), min(W - 1, max(e[1] for e in es) + 10)
            mask[y0 - 5:y1 + 5, x0:x1 + 1] = 255
        if hook and done / fps < hook[2]:
            mask |= hook_mask(f, hook[0], hook[1])
        p.stdin.write((cv2.inpaint(f, mask, 7, cv2.INPAINT_TELEA) if mask.any() else f).tobytes())

    while k < last:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
        ext.append(box_extent(f, y0, y1))
        k += 1
        if len(frames) >= 3:
            emit(len(frames) - 3)
            done += 1
            if len(frames) > 6:
                frames.popleft()
                ext.popleft()
    for j in (2, 1):
        emit(len(frames) - j)
        done += 1
    p.stdin.close()
    p.wait()
    print(f"wrote {a.out}: {done} frames ({done / fps:.2f}s), captions inpainted")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["read", "remove"])
    ap.add_argument("src")
    ap.add_argument("--box", required=True, help="rows of the caption box, e.g. 890-938")
    ap.add_argument("--out", required=True)
    ap.add_argument("--hook", help="ROW0-ROW1:SECONDS - big hook text area removed before SECONDS")
    ap.add_argument("--end", type=float, help="cut the video here (seconds), e.g. before an end card")
    a = ap.parse_args()
    y0, y1 = (int(v) for v in a.box.split("-"))
    (cmd_read if a.cmd == "read" else cmd_remove)(a, y0, y1)


if __name__ == "__main__":
    main()
