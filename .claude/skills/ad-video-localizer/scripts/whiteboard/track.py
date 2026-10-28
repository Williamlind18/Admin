# Track each text item of items.py through the animation using the per-frame OCR words.
# Output tracks.json: {id: {n: [x0, y0, scale, detected]}} for every frame the tracker followed.
import json, re, sys, difflib
import numpy as np
sys.path.insert(0, '.')
from items import ITEMS
from tools_lines import load

F = load()
MOT = {int(k): v for k, v in json.load(open('motion.json')).items()}
N0, N1 = min(F), max(F)


def norm(t):
    return re.sub(r"[^A-Z0-9&]", "", t.upper().replace('’', "'"))


def match(a, b):
    if not a or not b:
        return False
    if a == b:
        return True
    return len(a) >= 3 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.8


def words(n):
    return [w for w in F.get(n, []) if w[1] >= 70 and norm(w[0])]


tracks = {}
for it in ITEMS:
    toks = [norm(t) for t in it['en'].split()]
    toks = [t for t in toks if t]
    n0 = it['n']
    bx0, by0, bx1, by1 = it['box']
    # reference words at the keyframe: offsets inside the item box
    ref = []
    for w in words(n0):
        t, c, x, y, ww, hh = w
        cx, cy = x + ww / 2, y + hh / 2
        if not (bx0 - 12 <= cx <= bx1 + 12 and by0 - 10 <= cy <= by1 + 10):
            continue
        # an OCR word can hold several tokens ("SKIN CELLS" is two)
        for k, tok in enumerate(toks):
            if match(norm(t), tok) or (len(norm(t)) >= 4 and norm(t) in ''.join(toks)):
                ref.append((norm(t), x - bx0, y - by0, ww, hh))
                break
    if not ref:
        print('no reference words for', it['id'], it['en'], file=sys.stderr)
        continue
    xs0 = [r[1] for r in ref]; ys0 = [r[2] for r in ref]
    xs1 = [r[1] + r[3] for r in ref]; ys1 = [r[2] + r[4] for r in ref]
    # tighten the box to the reference words when they cover it
    it['box'] = [bx0 + min(0, min(xs0)), by0 + min(0, min(ys0)), bx0 + max(bx1 - bx0, max(xs1)), by0 + max(by1 - by0, max(ys1))]
    tr = {n0: [bx0, by0, 1.0, 1]}
    for step in (1, -1):
        px, py, s = bx0, by0, 1.0
        miss = 0
        n = n0 + step
        while N0 <= n <= N1 and miss < 48:
            m = MOT.get(n if step == 1 else n + 1, [0, 0, 0])
            gx, gy = (m[0], m[1]) if step == 1 else (-m[0], -m[1])
            pred = (px + gx, py + gy)
            R = min(30 + 10 * miss, 80)
            cand = []
            for t, c, x, y, ww, hh in words(n):
                nt = norm(t)
                for (rt, ox, oy, rw, rh) in ref:
                    if match(nt, rt) or (len(rt) >= 4 and len(nt) >= 4 and (rt.startswith(nt) or nt.startswith(rt))):
                        sw = hh / rh if nt == rt else s
                        sw = float(np.clip(sw, 0.3, 3.0))
                        ix, iy = x - ox * sw, y - oy * sw
                        if abs(ix - pred[0]) < R and abs(iy - pred[1]) < R:
                            cand.append((ix, iy, sw))
            if cand:
                px = float(np.median([c[0] for c in cand])); py = float(np.median([c[1] for c in cand]))
                s = float(np.median([c[2] for c in cand]))
                miss = 0
                tr[n] = [px, py, s, 1]
            else:
                miss += 1
                px, py = pred
                tr[n] = [px, py, s, 0]
            n += step
    hs = [r[4] for r in ref if re.fullmatch(r'[A-Z]+', r[0])] or [r[4] for r in ref]
    # smooth the scale: OCR box heights are noisy; snap to 1 unless a real zoom is happening
    ks = sorted(tr)
    det_s = {k: tr[k][2] for k in ks if tr[k][3]}
    for k in ks:
        near = [v for kk, v in det_s.items() if abs(kk - k) <= 6]
        sc = float(np.median(near)) if near else tr[k][2]
        tr[k][2] = 1.0   # OCR heights are too noisy for scale; the animation pans but hardly zooms
    tracks[it['id']] = {'box': it['box'], 'hcap': float(np.median(hs)), 'tr': {str(k): v for k, v in sorted(tr.items())}}
    det = sorted(k for k, v in tr.items() if v[3])
    print(f"{it['id']:4s} {it['en'][:28]:28s} det {len(det):4d}  {det[0]}-{det[-1]}  ({det[0]/23.976:.1f}-{det[-1]/23.976:.1f}s)")
json.dump(tracks, open('tracks.json', 'w'))
