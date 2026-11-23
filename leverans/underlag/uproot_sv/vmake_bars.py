"""Second pass: white bars left by Vmake in frames where the source pill detector found nothing (or other spots).
A bar = bright low-saturation elongated box in the Vmake frame whose area in the source held dark text on white.
usage: vmake_bars.py SRC VMAKE MASKS_IN.json MASKS_OUT.json"""
import sys, json, subprocess, numpy as np, cv2
src, vm, mi, mo = sys.argv[1:5]
W, H = 720, 900; n = W * H * 3
masks = json.load(open(mi))
def rd(p): return subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
a, b = rd(src), rd(vm); f = 0; added = 0
def overl(r, rs):
    return any(not (r[2] < q[0] or q[2] < r[0] or r[3] < q[1] or q[3] < r[1]) for q in rs)
while True:
    x = a.stdout.read(n); y = b.stdout.read(n)
    if len(x) < n or len(y) < n: break
    I = np.frombuffer(x, np.uint8).reshape(H, W, 3); V = np.frombuffer(y, np.uint8).reshape(H, W, 3)
    gv = cv2.cvtColor(V, cv2.COLOR_BGR2GRAY); sv = cv2.cvtColor(V, cv2.COLOR_BGR2HSV)[:, :, 1]
    wv = ((gv > 200) & (sv < 45)).astype(np.uint8)
    wv = cv2.morphologyEx(wv, cv2.MORPH_CLOSE, np.ones((5, 15), np.uint8))
    nn, lab, st, _ = cv2.connectedComponentsWithStats(wv)
    gi = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY)
    cur = masks.get(str(f), [])
    for j in range(1, nn):
        x0, y0, w, h, ar = st[j]
        if not (60 <= w <= 600 and 5 <= h <= 70 and w > 2.5 * h and ar > 0.5 * w * h): continue
        # source must show caption text there: dark pixels inside a mostly white box
        reg = gi[max(0, y0 - 6):y0 + h + 6, x0:x0 + w]
        dark = (reg < 90).mean(); white = (reg > 210).mean()
        if not (0.04 < dark < 0.5 and white > 0.35): continue
        r = [int(max(0, x0 - 14)), int(max(0, y0 - 18)), int(min(W, x0 + w + 14)), int(min(H, y0 + h + 18))]
        if overl(r, cur): continue
        cur.append(r); added += 1
    if cur: masks[str(f)] = cur
    f += 1
json.dump(masks, open(mo, 'w')); print('frames', f, 'added bars', added, 'mask frames', len(masks))
