"""Third LaMa pass for Vmake leftovers in video56: white bars and lines that vmake_lines.py still finds after pass 2.
Only the caption band (detected line top at y 580-700 in 720x900) counts. The caption pills were centred, so each mask is
a box centred on x 360 that reaches 60 px past the detected line on its far side, from 40 px above to 24 px below it,
put on the frame before and after too. Frames later covered by patches are skipped.
usage: vmake_bars3.py lines.json OUT_masks.json [PATCHED a-b,c-d]"""
import sys, json
lj, out = sys.argv[1:3]
P = [tuple(int(x) for x in r.split('-')) for r in (sys.argv[3] if len(sys.argv) > 3 else '7636-7733,8467-999999').split(',')]
skip = lambda f: any(a <= f <= b for a, b in P)
det = {int(k): [q for q in v if 580 <= q[1] <= 700] for k, v in json.load(open(lj)).items()}
det = {f: v for f, v in det.items() if v and not skip(f)}
masks = {}
for f, v in det.items():
    for q in v:
        hw = max(abs(q[0] - 360), abs(q[2] - 360)) + 60
        r = [max(80, 360 - hw), max(582, q[1] - 40), min(640, 360 + hw), min(705, q[3] + 24)]
        for g in (f - 1, f, f + 1):
            if skip(g): continue
            L = masks.setdefault(g, [])
            if L: L[0] = [min(L[0][0], r[0]), min(L[0][1], r[1]), max(L[0][2], r[2]), max(L[0][3], r[3])]
            else: L.append(r)
json.dump({str(k): v for k, v in sorted(masks.items())}, open(out, 'w'))
print('detected', len(det), 'masked frames', len(masks))
