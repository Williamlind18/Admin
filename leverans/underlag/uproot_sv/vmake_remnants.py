"""Find caption pills in the source and check whether Vmake left a white bar there. Writes LaMa masks.
usage: vmake_remnants.py SRC VMAKE OUT_src_pills.json OUT_masks.json"""
import sys, json, subprocess, numpy as np, cv2, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pilldetect import pills
src, vm, o1, o2 = sys.argv[1:5]
W, H = 720, 900; n = W * H * 3
def rd(p): return subprocess.Popen(['ffmpeg', '-v', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
a, b = rd(src), rd(vm)
sp, masks, f, rem = {}, {}, 0, 0
while True:
    x = a.stdout.read(n); y = b.stdout.read(n)
    if len(x) < n or len(y) < n: break
    I = np.frombuffer(x, np.uint8).reshape(H, W, 3); V = np.frombuffer(y, np.uint8).reshape(H, W, 3)
    ps = pills(I, 0, H)
    if ps:
        sp[f] = ps
        g = cv2.cvtColor(V, cv2.COLOR_BGR2GRAY); s = cv2.cvtColor(V, cv2.COLOR_BGR2HSV)[:, :, 1]
        wh = (g > 200) & (s < 45)
        for x0, y0, x1, y1 in ps:
            ix0, iy0, ix1, iy1 = x0 + 8, y0 + 8, x1 - 8, y1 - 8
            frac = wh[iy0:iy1, ix0:ix1].mean() if ix1 > ix0 and iy1 > iy0 else 0
            ring = np.concatenate([wh[max(0, iy0 - 14):iy0, ix0:ix1].ravel(), wh[iy1:iy1 + 14, ix0:ix1].ravel()])
            rf = ring.mean() if ring.size else 0
            if frac > 0.12 and frac > rf + 0.08:
                masks.setdefault(str(f), []).append([max(0, x0 - 6), max(0, y0 - 6), min(W, x1 + 6), min(H, y1 + 6)]); rem += 1
    f += 1
json.dump({str(k): v for k, v in sp.items()}, open(o1, 'w')); json.dump(masks, open(o2, 'w'))
print('frames', f, 'with pills', len(sp), 'remnant frames', len(masks))
