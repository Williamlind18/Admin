"""Remove the burned-in captions from every frame of src.mp4 (no cuts) -> clean_full.mp4.
Boxes: all detected boxes within +-6 frames, gaps <= 1.4 s filled from both sides, plus manual.json."""
import json, sys
import cv2, imageio_ffmpeg, numpy as np
D = json.load(open("boxes_all.json"))
fps, W, H = D["fps"], D["W"], D["H"]
det = D["frames"]; N = len(det)
WIN, MAXRUN, PAD = 6, int(1.4 * fps), 5
extra = {i: [] for i in range(N)}
for i in range(N):
    for j in range(max(0, i - WIN), min(N, i + WIN + 1)):
        extra[i].extend(det[j])
k = 0
while k < N:
    if not det[k]:
        j = k
        while j < N and not det[j]: j += 1
        if j - k <= MAXRUN:
            for m in range(k, j):
                if k > 0: extra[m].extend(det[k - 1])
                if j < N: extra[m].extend(det[j])
        k = j
    else:
        k += 1
manual = {i: [] for i in range(N)}
for t0, t1, x, y, w, h in json.load(open("manual.json")):
    for m in range(max(0, int(t0 * fps)), min(N, int(t1 * fps) + 1)):
        manual[m].append([x, y, w, h])

def looks_like_caption(img, b):
    x, y, w, h = b
    crop = img[max(0, y):y + h, max(0, x):x + w]
    if crop.size == 0:
        return False
    return (crop.min(axis=2) > 200).mean() > 0.45

def clean(img, bl):
    mask = np.zeros((H, W), np.uint8)
    for x, y, w, h in bl:
        cv2.rectangle(mask, (x - PAD, y - PAD), (x + w + PAD, y + h + PAD), 255, -1)
    ys, xs = np.where(mask > 0)
    y0, y1, x0, x1 = max(0, ys.min() - 40), min(H, ys.max() + 40), max(0, xs.min() - 40), min(W, xs.max() + 40)
    roi, mroi = img[y0:y1, x0:x1].copy(), mask[y0:y1, x0:x1]
    blur = cv2.GaussianBlur(cv2.inpaint(roi, mroi, 7, cv2.INPAINT_TELEA), (0, 0), 7)
    fe = cv2.GaussianBlur(cv2.dilate(mroi, np.ones((9, 9), np.uint8)).astype(np.float32) / 255.0, (0, 0), 4)[..., None]
    res = img.copy(); res[y0:y1, x0:x1] = (blur * fe + roi * (1 - fe)).astype(np.uint8)
    return res

r = imageio_ffmpeg.read_frames("src.mp4", pix_fmt="rgb24"); r.__next__()
wr = imageio_ffmpeg.write_frames("clean_full.mp4", (W, H), fps=fps, codec="libx264", pix_fmt_in="rgb24", macro_block_size=1,
                                 output_params=["-crf", "14", "-preset", "medium"])
wr.send(None); n = p = 0
for i, fs in enumerate(r):
    img = np.frombuffer(fs, np.uint8).reshape(H, W, 3)
    bl = {tuple(b) for b in extra.get(i, []) if b in det[i] or looks_like_caption(img, b)} | {tuple(b) for b in manual[i]}
    if bl:
        img = clean(img, [list(b) for b in bl]); p += 1
    wr.send(np.ascontiguousarray(img)); n += 1
wr.close()
print(f"clean_full.mp4: {n} frames, {p} cleaned")
