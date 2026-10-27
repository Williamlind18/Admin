"""Replace the AI-garbled box fronts on the pallet photo with the real Norrtvätt box print."""
import sys
import cv2
import numpy as np
from PIL import Image
sys.path.insert(0, sys.argv[4])
from boxlib import box_texture

src, boxphoto, out = sys.argv[1:4]
im = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
H, W = im.shape[:2]
orig = im.copy()  # all edge detection runs on the untouched photo
o = im.astype(int)
r, g, b = o[..., 0], o[..., 1], o[..., 2]
tq = (((b - r) > 60) & ((g - r) > 45) & (b > 130)).astype(np.uint8)
tq = cv2.morphologyEx(tq, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

# row: (search band y0, y1, column starts, last right edge, row bottom)
ROWS = [(818, 862, [34, 267, 499, 730, 958, 1187, 1419], 1645, 1093),
        (1096, 1140, [63, 285, 513, 739, 962, 1185, 1415], 1642, 1349),
        (1348, 1392, [88, 303, 524, 744, 962, 1182, 1405], 1625, 1590),
        (1586, 1630, [114, 320, 534, 749, 963, 1178, 1397], 1611, 1816),
        (1798, 1862, [139, 342, 547, 755, 965, 1174, 1386], 1594, 2021)]
tex = box_texture(boxphoto, 2)
tex_white = np.median(tex[tex.min(axis=2) > 235].reshape(-1, 3), axis=0)
count = 0
tops = []
NOMINAL_TOP = [826, 1103, 1355, 1593, 1823]  # measured band starts; never paste below these
for (y0, y1, xs, xlast, ybot), ntop in zip(ROWS, NOMINAL_TOP):
    for i, x0 in enumerate(xs):
        x1 = (xs[i + 1] - 4) if i + 1 < len(xs) else xlast
        # top edge of this box: where the bright lip above it drops into the dark seam (fallback: band start)
        prof = orig[y0 - 20:y1, x0 + 20:x1 - 20].mean(axis=(1, 2))
        drops = [j for j in range(3, len(prof)) if prof[j - 3:j].max() > 165 and prof[j] < 110 and prof[j - 1] >= 110]  # edge may take 2-3 rows
        if drops:
            top = min(y0 - 20 + drops[-1], ntop)
        else:
            col = tq[y0:y1, x0 + 10:x1 - 10].sum(axis=1)
            hit = np.where(col > (x1 - x0) * 0.15)[0]
            top = min(y0 + int(hit[0]) if len(hit) else ntop, ntop)
        tops.append(top)
        bw, bh = x1 - x0, ybot - top
        t = cv2.resize(tex, (bw, bh), interpolation=cv2.INTER_AREA)
        t = cv2.GaussianBlur(t, (0, 0), 0.6)
        reg = im[top:top + bh, x0:x0 + bw]
        wsel = reg.min(axis=2) > 170
        ref = np.median(reg[wsel], axis=0) if wsel.sum() > 50 else tex_white
        t = np.clip(t * (ref / tex_white), 0, 255)
        # soft 2 px edge so the paste sits in the photo
        a = np.zeros((bh, bw), np.float32)
        a[2:-2, 2:-2] = 1
        a = cv2.GaussianBlur(a, (0, 0), 1.0)[..., None]
        im[top:top + bh, x0:x0 + bw] = reg * (1 - a) + t * a
        count += 1
grain = np.random.default_rng(1).normal(0, 2.0, im.shape).astype(np.float32)
Image.fromarray(np.clip(im + grain * 0.6, 0, 255).astype(np.uint8)).save(out)
print("replaced", count, "box fronts ->", out, "tops", tops)
