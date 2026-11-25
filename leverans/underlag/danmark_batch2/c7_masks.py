"""LaMa masks for the Swedish text in video39 (DK batch 2 C7), from textmasks.py output (tm_all.json, band 0.12-0.88).
Pass 1: captions (centre y 0.62-0.80), the title box (frames 0-160) and the offer boxes (2812-2940).
Pass 2: the captions that sit at y ~0.365 in 55.6-58.6 s, and each caption's first (fade-in) frame the detector missed.
Frame 600 still shows the caption faded into the Swedish blur box; it is patched from frame 601 in the render.
usage: c7_masks.py tm_all.json SV.srt OUT1.json OUT2.json"""
import json, sys
tm, srt, o1, o2 = sys.argv[1:5]
m = {int(k): v for k, v in json.load(open(tm)).items()}; H, N = 1920, 3255
cap = lambda f: [r for r in m.get(f, []) if 0.62 <= (r[1] + r[3]) / 2 / H <= 0.80]
out = {}
for f in range(N):
    rs = cap(f)
    if f <= 160: rs.append([300, 430, 790, 712])
    if 2812 <= f <= 2940: rs.append([200, 768, 880, 1018])
    if 2896 <= f <= 2940: rs.append([180, 1025, 900, 1205])
    if rs: out[f] = [[max(0, int(r[0])), max(0, int(r[1])), min(1080, int(r[2])), min(H, int(r[3]))] for r in rs]
json.dump({str(k): v for k, v in out.items()}, open(o1, 'w'))
def ts(s): h, mi, x = s.replace(',', '.').split(':'); return int(h) * 3600 + int(mi) * 60 + float(x)
out2 = {}
for f in range(1660, 1766):
    rs = [r for r in m.get(f, []) if 0.32 <= (r[1] + r[3]) / 2 / H <= 0.42]
    if rs: out2[f] = [[max(0, r[0] - 6), r[1] - 6, min(1080, r[2] + 6), r[3] + 6] for r in rs]
for b in open(srt, encoding='utf-8').read().strip().split('\n\n'):
    L = b.split('\n'); a, c = (ts(x) for x in L[1].split(' --> '))
    for f in range(int(round(a * 30)) + 1, int(round(c * 30)) - 1):
        if cap(f) or 1660 <= f <= 1765: continue
        rs = cap(f - 1) + cap(f + 1)
        box = [min(r[0] for r in rs), min(r[1] for r in rs), max(r[2] for r in rs), max(r[3] for r in rs)] if rs else None
        if box and box not in out2.get(f, []): out2.setdefault(f, []).append(box)
json.dump({str(k): v for k, v in sorted(out2.items())}, open(o2, 'w'))
print(len(out), len(out2))
