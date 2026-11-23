"""Drop/trim ASS events inside windows where the original ad shows no captions (banner, offer graphic).
usage: hide_caps.py IN.ass OUT.ass a-b,c-d   (seconds)"""
import sys, re
inp, out, wins = sys.argv[1], sys.argv[2], [tuple(float(x) for x in w.split('-')) for w in sys.argv[3].split(',')]
def t2s(t):
    h, m, s = t.split(':'); return int(h) * 3600 + int(m) * 60 + float(s)
def s2t(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x - h * 3600 - m * 60
    return f'{h}:{m:02d}:{s:05.2f}'
lines, dropped, trimmed = [], 0, 0
for ln in open(inp, encoding='utf-8'):
    if not ln.startswith('Dialogue:'):
        lines.append(ln); continue
    parts = ln.split(',', 9)
    a, b = t2s(parts[1]), t2s(parts[2])
    a0, b0 = a, b
    for w0, w1 in wins:
        if a >= w0 and b <= w1: a = b = None; break
        if a < w0 < b <= w1: b = w0; trimmed += 1
        elif w0 <= a < w1 < b: a = w1; trimmed += 1
    if a is None or ((a, b) != (a0, b0) and b - a < 0.4):
        dropped += 1; continue
    parts[1], parts[2] = s2t(a), s2t(b)
    lines.append(','.join(parts))
open(out, 'w', encoding='utf-8').writelines(lines)
print('dropped', dropped, 'trimmed', trimmed)
