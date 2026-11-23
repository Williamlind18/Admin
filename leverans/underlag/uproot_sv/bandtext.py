#!/usr/bin/env python3
"""Caption masks: black text on white pills, centred, at known heights. usage: bandtext.py SRC OUT.json Y1,Y2,..."""
import sys, json, subprocess
import numpy as np, cv2
def find1(g, Y, W=720):
    band = g[Y - 11:Y + 11]
    white = band > 200; dark = band < 95
    wr = white.mean(0); dk = dark.sum(0)
    txt = (dk >= 2) & (wr > 0.30)
    xs = np.where(txt)[0]
    if len(xs) < 15: return None, 0
    cl = []; s = xs[0]; p = xs[0]
    for x in xs[1:]:
        if x - p > 34: cl.append((s, p)); s = x
        p = x
    cl.append((s, p))
    best = None
    for a, b in cl:
        if a <= W / 2 + 90 and b >= W / 2 - 90:
            best = [a, b]
    if best is None: return None, 0
    for a, b in sorted(cl, reverse=True):
        if b < best[0] and best[0] - b <= 34: best[0] = a
    for a, b in sorted(cl):
        if a > best[1] and a - best[1] <= 34: best[1] = b
    x0, x1 = best
    if x1 - x0 < 30: return None, 0
    n = int(dark[:, x0:x1 + 1].sum())
    if n < 60: return None, 0
    up = (g[Y - 17:Y - 13, x0:x1 + 1] > 200).mean(); dn = (g[Y + 13:Y + 17, x0:x1 + 1] > 200).mean()
    if up < 0.75 or dn < 0.75: return None, 0
    return [int(max(0, x0 - 18)), int(Y - 30), int(min(W, x1 + 18)), int(Y + 30)], n
def find(g, Y, W=720):
    best, bn = None, 0
    for y in range(Y - 14, Y + 15, 2):
        r, n = find1(g, y, W)
        if r and n > bn: best, bn = r, n
    return best
if __name__ == "__main__":
    src, outp, ys = sys.argv[1], sys.argv[2], [int(v) for v in sys.argv[3].split(",")]
    W, H = 720, 1280
    pr = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    res, i = {}, 0
    while True:
        b = pr.stdout.read(W * H)
        if len(b) < W * H: break
        g = np.frombuffer(b, np.uint8).reshape(H, W)
        r = [x for x in (find(g, Y) for Y in ys) if x]
        if r: res[str(i)] = r
        i += 1
    json.dump(res, open(outp, "w")); print(src, i, "frames,", len(res), "with captions")
