"""Copy an .srt and end each cue 1 ms before the next one starts (no overlaps). usage: srt_fix.py IN OUT"""
import sys
def pt(t): h, m, r = t.split(':'); s, ms = r.split(','); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x - h * 3600 - m * 60
    return f'{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}'
ev = []
for b in open(sys.argv[1], encoding='utf-8').read().strip().split('\n\n'):
    L = b.split('\n'); a, c = L[1].split(' --> '); ev.append([pt(a), pt(c), '\n'.join(L[2:])])
for i in range(len(ev) - 1):
    if ev[i][1] > ev[i + 1][0] - 0.001: ev[i][1] = ev[i + 1][0] - 0.001
with open(sys.argv[2], 'w', encoding='utf-8') as f:
    for i, (a, c, t) in enumerate(ev, 1): f.write(f'{i}\n{ts(a)} --> {ts(c)}\n{t}\n\n')
print(sys.argv[2], len(ev))
