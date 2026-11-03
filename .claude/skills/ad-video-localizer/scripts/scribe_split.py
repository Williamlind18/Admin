"""Cut a voice take into sentence clips + fused.json using Scribe word timestamps.
Usage: scribe_split.py WORK   (needs WORK/take.mp3, WORK/script.txt, WORK/scribe_words.json)"""
import sys, json, re, difflib, subprocess, numpy as np, librosa, imageio_ffmpeg
W = sys.argv[1]; S = W + '/sent'
FF = imageio_ffmpeg.get_ffmpeg_exe()
lines = [l.strip() for l in open(W + '/script.txt', encoding='utf-8') if l.strip()]
toks = [(i, t) for i, l in enumerate(lines) for t in l.split()]
def norm(t): return re.sub(r'[^a-zåäöé0-9]', '', t.lower())
sw = [w for w in json.load(open(W + '/scribe_words.json'))['words'] if w.get('type', 'word') == 'word']
# expand scribe words and script tokens to comparable units (split hyphens)
def units(t): return [u for u in re.split(r'[-\s]', t) if norm(u)]
A = [(k, norm(u)) for k, (_, t) in enumerate(toks) for u in units(t)]
B = [(k, norm(u)) for k, w in enumerate(sw) for u in units(w['text'])]
sm = difflib.SequenceMatcher(None, [a for _, a in A], [b for _, b in B], autojunk=False)
st = [None] * len(toks); en = [None] * len(toks)
for blk in sm.get_matching_blocks():
    for d in range(blk.size):
        ka = A[blk.a + d][0]; kb = B[blk.b + d][0]
        st[ka] = sw[kb]['start'] if st[ka] is None else min(st[ka], sw[kb]['start'])
        en[ka] = sw[kb]['end'] if en[ka] is None else max(en[ka], sw[kb]['end'])
# merged scribe words like "såhär" -> two script tokens: handle replace ops by spreading
for tag, a0, a1, b0, b1 in sm.get_opcodes():
    if tag == 'replace':
        ks = sorted(set(A[x][0] for x in range(a0, a1))); kb = sorted(set(B[x][0] for x in range(b0, b1)))
        t0, t1 = sw[kb[0]]['start'], sw[kb[-1]]['end']
        L = [len(toks[k][1]) for k in ks]; tot = sum(L); c = t0
        for k, l in zip(ks, L):
            if st[k] is None: st[k] = c
            c += (t1 - t0) * l / tot
            if en[k] is None: en[k] = c
miss = [toks[k][1] for k in range(len(toks)) if st[k] is None]
# interpolate any remaining gaps
for k in range(len(toks)):
    if st[k] is None:
        p = max([j for j in range(k) if en[j] is not None], default=None); n = min([j for j in range(k + 1, len(toks)) if st[j] is not None], default=None)
        a = en[p] if p is not None else 0.0; b = st[n] if n is not None else a + 0.4
        st[k], en[k] = a + 0.02, max(a + 0.05, b - 0.02)
print('unmatched script tokens:', miss)
y, sr = librosa.load(W + '/take.mp3', sr=16000); hop = 160
db = 20 * np.log10(librosa.feature.rms(y=y, frame_length=400, hop_length=hop)[0] + 1e-9)
thr = db.max() - 42
def refine_start(t):
    i = int(t * 100); lo = max(0, i - 25)
    j = i
    while j > lo and db[j - 1] > thr: j -= 1
    return j / 100
def refine_end(t):
    i = int(t * 100); hi = min(len(db) - 1, i + 30)
    j = i
    while j < hi and db[j] > thr: j += 1
    return j / 100
N = len(lines); ss = []; ee = []
for i in range(N):
    ks = [k for k, (li, _) in enumerate(toks) if li == i]
    ss.append(refine_start(st[ks[0]])); ee.append(refine_end(en[ks[-1]]))
cuts = [max(0.0, ss[0] - 0.15)] + [(ee[i] + ss[i + 1]) / 2 for i in range(N - 1)] + [min(len(y) / sr, ee[-1] + 0.2)]
out = []
for i in range(N):
    c0, c1 = cuts[i], cuts[i + 1]
    subprocess.run([FF, '-v', 'error', '-y', '-i', W + '/take.mp3', '-ss', f'{c0:.3f}', '-to', f'{c1:.3f}', '-c:a', 'libmp3lame', '-q:a', '2', f'{S}/{i + 1:02d}.mp3'], check=True)
    open(f'{S}/{i + 1:02d}.txt', 'w', encoding='utf-8').write(lines[i] + '\n')
    ks = [k for k, (li, _) in enumerate(toks) if li == i]
    words = [{'w': toks[k][1], 'start': round(max(0.0, st[k] - c0), 3), 'end': round(en[k] - c0, 3)} for k in ks]
    words[0]['start'] = round(ss[i] - c0, 3); words[-1]['end'] = round(ee[i] - c0, 3)
    pauses = [[round(words[j]['end'], 3), round(words[j + 1]['start'], 3)] for j in range(len(words) - 1) if words[j + 1]['start'] - words[j]['end'] >= 0.30]
    dur = ee[i] - ss[i]; eff = dur - sum(max(0.0, (b - a) - 0.22) for a, b in pauses)
    out.append(dict(id=i + 1, text=lines[i], bounds=[round(ss[i] - c0, 3), round(ee[i] - c0, 3)], pauses=pauses, dur=round(dur, 3), dur_eff=round(eff, 3), methods=1, spread=0.0, words=words))
json.dump(dict(lang='sv', sentences=out), open(S + '/fused.json', 'w'), ensure_ascii=False, indent=1)
print(f'{N} sentences, effective speech {sum(o["dur_eff"] for o in out):.1f}s; sentence pauses: min {min(ss[i+1]-ee[i] for i in range(N-1)):.2f} median {sorted(ss[i+1]-ee[i] for i in range(N-1))[N//2]:.2f}')
