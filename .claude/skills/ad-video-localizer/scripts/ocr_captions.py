#!/usr/bin/env python3
"""Read burned-in captions (white boxes with dark text, TikTok style) frame by frame.

Gives you the original script with timestamps when the user has none, and per-frame
rectangles of the caption box for removing it with lama_inpaint.py.

Usage:
  ocr_captions.py SRC.mp4 OUT_DIR [--band 0.70-0.86] [--pad 5] [--box-h 0.030-0.047] [--fill 0.45]
Small caption boxes (e.g. 720x1280 with 36 px boxes) need --box-h 0.022-0.05 --fill 0.38.
Writes OUT_DIR/captions_ocr.txt (start-end text, one caption per line),
OUT_DIR/segments.json and OUT_DIR/masks.json ({frame: [[x0, y0, x1, y1]]}).
Needs tesseract (apt-get install tesseract-ocr) and opencv-python-headless.
Frames where the box merges with a white background are filled from the nearest
detected box of the same caption; check the gap list it prints.
"""
import argparse, json, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe, probe  # noqa: E402


def band_box(white, im, Wd, hmin, hmax, minlen=50):
    """Caption box = a white band above and a white band below the text with the same left/right
    edges, white side margins between them and dark text inside. Works when the box touches white
    backgrounds above or below it. Returns (x, y, w, h) in crop coordinates or None."""
    pad = np.zeros((white.shape[0], 1), np.int8)
    d = np.diff(np.hstack([pad, white.astype(np.int8), pad]), axis=1)
    runs = []
    for y in np.where((white.sum(1) >= minlen))[0]:
        st, en = np.where(d[y] == 1)[0], np.where(d[y] == -1)[0]
        for x0, x1 in zip(st, en):
            if x1 - x0 >= minlen and x0 > 2 and x1 < Wd - 3:
                runs.append((int(y), int(x0), int(x1)))
    bands = []  # consecutive rows with (almost) the same run
    for y, x0, x1 in runs:
        for bd in bands:
            if bd[1] == y - 1 and abs(bd[2] - x0) <= 4 and abs(bd[3] - x1) <= 4:
                bd[1] = y; bd[2] = min(bd[2], x0); bd[3] = max(bd[3], x1); break
        else:
            bands.append([y, y, x0, x1])
    dark = im.max(axis=2) < 110
    best = None
    for A in bands:
        for B in bands:
            g0, g1 = A[1] + 1, B[0]
            if not (4 <= g1 - g0 <= hmax) or abs(A[2] - B[2]) > 6 or abs(A[3] - B[3]) > 6:
                continue
            x0, x1 = max(A[2], B[2]), min(A[3], B[3])
            h = B[1] - A[0] + 1
            if not (hmin <= h <= hmax + 10):
                continue
            side = np.r_[white[g0:g1, x0:x0 + 3].ravel(), white[g0:g1, x1 - 3:x1].ravel()].mean()
            txt = dark[g0:g1, x0:x1].mean()
            if side > 0.75 and txt > 0.04:
                if best is None or x1 - x0 > best[2]:
                    best = (x0, A[0], x1 - x0, h)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out_dir")
    ap.add_argument("--band", default="0.70-0.86", help="vertical band (fractions of height) where captions sit")
    ap.add_argument("--pad", type=int, default=5)
    ap.add_argument("--vpad", type=int, default=6, help="extra rows above/below the box in the masks (use ~12 for "
                    "bands mode: its box can be a few rows short and leave a thin white edge after inpainting)")
    ap.add_argument("--box-h", default="0.030-0.047", help="caption box height range (fractions of height)")
    ap.add_argument("--fill", type=float, default=0.45, help="min share of white pixels in the box")
    ap.add_argument("--mode", choices=["cc", "bands"], default="cc",
                    help="cc: box = white connected component (default). bands: box = matching white rows above "
                         "and below the text; use it when the box touches white backgrounds or the text is large")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    info = probe(a.src); Wd, Hd = info["width"], info["height"]
    b0, b1 = (float(x) for x in a.band.split("-"))
    Y0, Y1 = int(Hd * b0), int(Hd * b1)
    h0, h1 = (float(x) for x in a.box_h.split("-"))
    hmin, hmax = int(Hd * h0), int(Hd * h1)
    ff = ffmpeg_exe()
    p = subprocess.Popen([ff, "-loglevel", "error", "-i", a.src, "-vf", f"crop={Wd}:{Y1-Y0}:0:{Y0}", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    n = Wd * (Y1 - Y0) * 3
    boxes, crops, f = [], {}, 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        im = np.frombuffer(b, np.uint8).reshape(Y1 - Y0, Wd, 3)
        white = (im.min(axis=2) > 236).astype(np.uint8)
        if a.mode == "bands":
            best = band_box(white, im, Wd, hmin, hmax)
            if best:
                x, y, w, h = best
                c = im[y:y + h, x:x + w]
                sig = cv2.resize((c.max(axis=2) < 110).astype(np.uint8) * 255, (64, 8), interpolation=cv2.INTER_AREA)
                boxes.append((f, x, y + Y0, w, h, sig)); crops[f] = c.copy()
            else:
                boxes.append((f, None))
            f += 1
            continue
        k, lab, st, _ = cv2.connectedComponentsWithStats(white, connectivity=4)
        best = None
        for j in range(1, k):
            x, y, w, h, area = st[j]
            if hmin <= h <= hmax and w >= 40 and w <= 0.75 * Wd and area >= a.fill * w * h:
                sub = (lab[y:y + h, x:x + w] == j)
                if sub[1].mean() > 0.85 and sub[-2].mean() > 0.6 and sub[:, 1].mean() > 0.85 and sub[:, -2].mean() > 0.85:
                    if best is None or area > best[4]: best = (int(x), int(y + Y0), int(w), int(h), int(area))
        if best:
            x, y, w, h, _ = best
            c = im[y - Y0:y - Y0 + h, x:x + w]
            sig = cv2.resize((c.max(axis=2) < 110).astype(np.uint8) * 255, (64, 8), interpolation=cv2.INTER_AREA)
            boxes.append((f, x, y, w, h, sig)); crops[f] = c.copy()
        else:
            boxes.append((f, None))
        f += 1
    N = f
    # group consecutive frames with the same caption
    segs, cur = [], None
    for bx in boxes:
        if bx[1] is None:
            if cur: segs.append(cur); cur = None
            continue
        same = cur and abs(cur[-1][1] - bx[1]) <= 3 and abs(cur[-1][3] - bx[3]) <= 6 and \
            np.abs(cur[-1][5].astype(float) - bx[5]).mean() < 25
        if same: cur.append(bx)
        else:
            if cur: segs.append(cur)
            cur = [bx]
    if cur: segs.append(cur)
    out, lines, prev = [], [], None
    for s in segs:
        mid = s[len(s) // 2][0]
        big = cv2.resize(crops[mid], None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(a.out_dir, "_ocr.png"), big)
        t = subprocess.run(["tesseract", os.path.join(a.out_dir, "_ocr.png"), "-", "--psm", "7"],
                           capture_output=True, text=True).stdout.strip().strip("|‘~ ").strip()
        out.append({"start": s[0][0], "end": s[-1][0], "text": t})
        if t != prev:
            lines.append(f"{s[0][0] / info['fps']:7.2f}-{(s[-1][0] + 1) / info['fps']:7.2f}  {t}")
        prev = t
    if os.path.exists(os.path.join(a.out_dir, "_ocr.png")):
        os.remove(os.path.join(a.out_dir, "_ocr.png"))
    det = {bx[0]: (bx[1], bx[2], bx[3], bx[4]) for bx in boxes if bx[1] is not None}
    masks = {}
    for fr in range(N):
        g = det.get(fr)
        if g is None:  # short dropouts: borrow the nearest detection within 20 frames
            for d in range(1, 21):
                g = det.get(fr - d) or det.get(fr + d)
                if g: break
        if g:
            x, y, w, h = g
            masks[fr] = [[max(0, x - a.pad), y - a.vpad, min(Wd, x + w + a.pad), y + h + a.vpad]]
    json.dump({k: list(v) for k, v in det.items()}, open(os.path.join(a.out_dir, "det.json"), "w"))  # raw detections
    json.dump(out, open(os.path.join(a.out_dir, "segments.json"), "w"), ensure_ascii=False)
    json.dump(masks, open(os.path.join(a.out_dir, "masks.json"), "w"))
    open(os.path.join(a.out_dir, "captions_ocr.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"{len(out)} caption segments, {len(masks)} of {N} frames masked -> {a.out_dir}")


if __name__ == "__main__":
    main()
