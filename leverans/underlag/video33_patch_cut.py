"""One pass over the video: re-clean the frames where burned_captions.py left a caption (detection gaps
at caption changes, captions on white backgrounds) and drop the cut segments, writing cut.mp4.

Every kept frame is cleaned from src.mp4 with the same inpaint as burned_captions.py, using the union of the nearest detected boxes
before and after the gap, plus manual boxes.
Usage: python3 patch_cut.py manual.json   (manual.json: [[t0, t1, x, y, w, h], ...])
"""
import json
import sys

import cv2
import imageio_ffmpeg
import numpy as np

import timeline as T

D = json.load(open("caps/boxes.json"))
fps, W, H = D["fps"], D["W"], D["H"]
det = [b for _, b in D["frames"]]
N = len(det)
MAXRUN = int(1.4 * fps)
PAD = 4

WIN = 6  # frames: captions that alternate in detection (two on screen) are both masked
extra = {}
for i in range(N):
    near = [det[j] for j in range(max(0, i - WIN), min(N, i + WIN + 1)) if det[j]]
    if near:
        extra[i] = near
k = 0
while k < N:
    if det[k] is None:
        j = k
        while j < N and det[j] is None:
            j += 1
        if j - k <= MAXRUN:
            p = det[k - 1] if k > 0 else None
            q = det[j] if j < N else None
            for m in range(k, j):
                extra.setdefault(m, []).extend(b for b in (p, q) if b)
        k = j
    else:
        k += 1
for t0, t1, x, y, w, h in json.load(open(sys.argv[1])):
    for m in range(max(0, int(t0 * fps) - 1), min(N, int(t1 * fps) + 2)):
        extra.setdefault(m, []).append([x, y, w, h])


def clean(img, bl):
    mask = np.zeros((H, W), np.uint8)
    for x, y, w, h in bl:
        cv2.rectangle(mask, (x - PAD, y - PAD), (x + w + PAD, y + h + PAD), 255, -1)
    ys, xs = np.where(mask > 0)
    y0, y1, x0, x1 = max(0, ys.min() - 40), min(H, ys.max() + 40), max(0, xs.min() - 40), min(W, xs.max() + 40)
    roi, mroi = img[y0:y1, x0:x1].copy(), mask[y0:y1, x0:x1]
    blur = cv2.GaussianBlur(cv2.inpaint(roi, mroi, 7, cv2.INPAINT_TELEA), (0, 0), 7)
    fe = cv2.GaussianBlur(cv2.dilate(mroi, np.ones((9, 9), np.uint8)).astype(np.float32) / 255.0, (0, 0), 4)[..., None]
    res = img.copy()
    res[y0:y1, x0:x1] = (blur * fe + roi * (1 - fe)).astype(np.uint8)
    return res


def reader(path):
    r = imageio_ffmpeg.read_frames(path, pix_fmt="rgb24")
    r.__next__()
    return r


def kept(i):
    t = i / fps
    return not any(a <= t < b for a, b in T.CUTS)


src = reader("in/src.mp4")
wr = imageio_ffmpeg.write_frames("cut.mp4", (W, H), fps=fps, codec="libx264", pix_fmt_in="rgb24", macro_block_size=1,
                                 output_params=["-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p"])
wr.send(None)
n_out = n_patch = 0
for i, fs in enumerate(src):
    if not kept(i):
        continue
    img = np.frombuffer(fs, np.uint8).reshape(H, W, 3)
    if i in extra:
        bl = {tuple(b) for b in extra[i]}
        out = clean(img, [list(b) for b in bl])
        n_patch += 1
    else:
        out = img
    wr.send(np.ascontiguousarray(out))
    n_out += 1
wr.close()
print(f"cut.mp4: {n_out} frames ({n_out / fps:.2f} s), {n_patch} frames re-cleaned; expected {T.duration():.2f} s")
