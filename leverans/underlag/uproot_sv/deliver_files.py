"""Write the delivery .srt (no overlaps) and manus for one Uproot 1:1 ad.
usage: deliver_files.py vXX OUTDIR NAME"""
import sys, re, json, os
v, outdir, name = sys.argv[1:4]
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x - h * 3600 - m * 60
    return f'{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}'
def pt(t):
    h, m, r = t.split(':'); s, ms = r.split(','); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
blocks = [b for b in open(f'{S}/work/{v}/subtitles.srt', encoding='utf-8').read().strip().split('\n\n') if b.strip()]
ev = []
for b in blocks:
    ln = b.split('\n'); a, c = ln[1].split(' --> '); ev.append([pt(a), pt(c), '\n'.join(ln[2:])])
for i in range(len(ev) - 1):
    if ev[i][1] > ev[i + 1][0] - 0.001: ev[i][1] = ev[i + 1][0] - 0.001
with open(f'{outdir}/{name}.srt', 'w', encoding='utf-8') as f:
    for i, (a, c, t) in enumerate(ev, 1):
        f.write(f'{i}\n{ts(a)} --> {ts(c)}\n{t}\n\n')
# manus: Swedish sentences with their start time in the finished ad + the English original
w = json.load(open(f'{S}/work/{v}/words_global.json')); w = w['words'] if isinstance(w, dict) else w
sv = [l.strip() for l in open(f'{S}/manus/{v}.txt', encoding='utf-8') if l.strip()]
starts = {}
for x in w: starts.setdefault(x['sent'], x['start'])
key = 'video' + v[1:]
if os.path.exists(f'{S}/manus/user_transcript_{v}.txt'):
    # one transcript per file: everything from the first mm:ss line on
    lines = [l.strip() for l in open(f'{S}/manus/user_transcript_{v}.txt', encoding='utf-8') if l.strip() and l.strip() not in ('Ask AI', 'Copy')]
    lines = lines[next(i for i, l in enumerate(lines) if re.fullmatch(r'\d\d:\d\d', l)):]
else:
    ut = open(f'{S}/manus/user_transcripts.txt', encoding='utf-8').read()
    seg = ut[ut.index(key + ' manus'):]
    nxt = [ut.index(k + ' manus') for k in ('video49', 'video50') if (k + ' manus') in ut and ut.index(k + ' manus') > ut.index(key + ' manus')]
    seg = seg[:min(nxt) - ut.index(key + ' manus')] if nxt else seg
    lines = [l.strip() for l in seg.split('\n') if l.strip() and l.strip() not in ('Ask AI', 'Copy')][1:]
en = []
for l in lines:
    if re.fullmatch(r'\d\d:\d\d', l): en.append([l, ''])
    elif en: en[-1][1] = (en[-1][1] + ' ' + l).strip()
os.makedirs(f'{outdir}/manus', exist_ok=True)
with open(f'{outdir}/manus/manus_{key}_sv.txt', 'w', encoding='utf-8') as f:
    f.write(f'Maskinrent {key} sv: svensk 1:1-version av Uproot {key}. Start i den färdiga annonsen, mm:ss.\n\n')
    for i, s in enumerate(sv, 1):
        t = starts.get(i, 0.0); f.write(f'{int(t // 60):02d}:{t % 60:05.2f}  {s}\n')
    f.write('\n--- Uproots engelska original (från användaren) ---\n\n')
    for t, s in en: f.write(f'{t}  {s}\n')
print('srt', len(ev), 'manus', len(sv), 'en', len(en))
