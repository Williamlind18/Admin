"""findquad.py img x0 y0 x1 y1 [seed_x seed_y] : quad of the flat region (LCD/paper) containing the seed, via flood fill on colour."""
import sys, json, cv2, numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")); x0, y0, x1, y1 = map(int, sys.argv[2:6])
sx, sy = (int(sys.argv[6]), int(sys.argv[7])) if len(sys.argv) > 7 else ((x0 + x1) // 2, (y0 + y1) // 2)
tol = int(sys.argv[8]) if len(sys.argv) > 8 else 12
roi = cv2.GaussianBlur(im[y0:y1, x0:x1].copy(), (0, 0), 2)
mask = np.zeros((roi.shape[0] + 2, roi.shape[1] + 2), np.uint8)
cv2.floodFill(roi, mask, (sx - x0, sy - y0), (255, 0, 0), (tol,) * 3, (tol,) * 3, cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8) | 8)
m = mask[1:-1, 1:-1]
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cs, key=cv2.contourArea)
hull = cv2.convexHull(c); eps = 0.01 * cv2.arcLength(hull, True)
for k in range(60):
    ap = cv2.approxPolyDP(hull, eps, True)
    if len(ap) <= 4: break
    eps *= 1.15
p = ap.reshape(-1, 2).astype(float) + [x0, y0]
# order TL, TR, BR, BL
s = p.sum(1); d = p[:, 0] - p[:, 1]
q = [p[np.argmin(s)], p[np.argmax(d)], p[np.argmax(s)], p[np.argmin(d)]]
print(json.dumps([[round(a, 1), round(b, 1)] for a, b in q]), "area", int(cv2.contourArea(c)))
cv2.imwrite(sys.argv[1] + ".mask.png", m)
