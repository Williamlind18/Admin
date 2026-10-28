# Track the MANUAL items by integrating the global motion from their keyframe, and mark a frame as
# "detected" when the crop still looks like the keyframe crop (normalised correlation). Adds them to tracks.json.
import sys, json, numpy as np, cv2
sys.path.insert(0, '.')
from items import MANUAL
from frames import get_frames
MOT = {int(k): v for k, v in json.load(open('motion.json')).items()}
T = json.load(open('tracks.json'))
A, B = 215, 1772
for it in MANUAL:
    n0 = it['n']; x0, y0, x1, y1 = it['box']; w, h = x1 - x0, y1 - y0
    lo, hi = max(A, n0 - 120), min(B, n0 + 120)
    FR = get_frames('dl/src_orig.mp4', range(lo, hi + 1))
    g = lambda n: cv2.cvtColor(FR[n], cv2.COLOR_RGB2GRAY).astype(np.float32)
    ref = g(n0)[y0 - 4:y1 + 4, x0 - 4:x1 + 4]
    tr = {n0: [x0, y0, 1.0, 1]}
    for step in (1, -1):
        px, py = float(x0), float(y0); miss = 0; n = n0 + step
        while lo <= n <= hi and miss < 24:
            m = MOT.get(n if step == 1 else n + 1, [0, 0, 0])
            px += m[0] * step; py += m[1] * step
            X, Y = int(round(px)), int(round(py))
            img = g(n)
            ok = 0
            if X - 10 >= 0 and Y - 10 >= 0 and X + w + 10 <= 720 and Y + h + 10 <= 1280:
                win = img[Y - 10:Y + h + 10, X - 10:X + w + 10]
                r = cv2.matchTemplate(win, ref, cv2.TM_CCOEFF_NORMED)
                _, mx, _, loc = cv2.minMaxLoc(r)
                if mx >= 0.6:
                    ok = 1
                    px += loc[0] - 6; py += loc[1] - 6   # refine
            miss = 0 if ok else miss + 1
            tr[n] = [px, py, 1.0, ok]
            n += step
    T[it['id']] = {'box': it['box'], 'hcap': float(h), 'tr': {str(k): v for k, v in sorted(tr.items())}}
    det = sorted(k for k, v in tr.items() if v[3])
    print(it['id'], len(det), det[0], det[-1])
json.dump(T, open('tracks.json', 'w'))
