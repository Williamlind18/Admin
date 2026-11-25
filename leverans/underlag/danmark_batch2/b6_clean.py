"""Rebuild a Swedish batch-6 picture from its release (frame map work/KEY/map.json) with CTA cards in another language.
CTA = card run split into name/year/offer cards (c1, c5, c2) + clips (first one with pill_30) + final card c4 with pill_order.
usage: b6_clean.py KEY SRC.mp4 SV.mp4 W H CARDDIR PILL_ORDER_Y   -> clean/KEY_clean.mp4"""
import json, os, subprocess, sys
import numpy as np
S = '/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/dkb2'
KEY, SRC, SV, W, H, CARDS, POY = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6], int(sys.argv[7])
FPS = 30; PILL_Y = {'pill_30': 10, 'pill_order': POY}
M = json.load(open(f'{S}/work/{KEY}/map.json')); src = np.array(M['src']); dist = np.array(M['dist']); N = len(src)
CARD = dist > 28
c0 = next(k for k in range(N) if CARD[k] and k > N * 0.6)
def clip_runs(a, b, tol=3):
    out, k = [], a
    while k < b:
        m = k + 1; ref = src[k] - k
        while m < b and abs((src[m] - m) - ref) <= tol: m += 1
        off = int(np.median(src[k:m] - np.arange(k, m))); out.append(['clip', k, m, k + off, None]); k = m
    # merge slivers (< 4 frames) into the next run
    res = []
    for it in out:
        if res and res[-1][2] - res[-1][1] < 4:
            p = res.pop(); it = ['clip', p[1], it[2], it[3] - (it[1] - p[1]), None]
        res.append(it)
    return res
items = clip_runs(0, c0, tol=1)
c1end = c0
while c1end < N and CARD[c1end]: c1end += 1
def thumbs(p, a, n):
    b = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-ss', f'{(a - 0.5) / FPS:.4f}', '-i', p, '-frames:v', str(n), '-vf',
                        'scale=24:42,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, 42, 24).astype(np.float32)
T = thumbs(SV, c0, c1end - c0)
dd = np.abs(np.diff(T, axis=0)).mean((1, 2)); cuts = sorted((np.argsort(dd)[-2:] + 1 + c0).tolist())
items += [['card', c0, cuts[0], 'c1', None], ['card', cuts[0], cuts[1], 'c5', None], ['card', cuts[1], c1end, 'c2', None]]
c4s = c1end
while c4s < N and not (CARD[c4s] and all(CARD[c4s:N])): c4s += 1
cl = clip_runs(c1end, c4s)
cl[0][4] = 'pill_30'
items += cl + [['card', c4s, N, 'c4', 'pill_order']]
assert items[0][1] == 0 and all(items[q][2] == items[q + 1][1] for q in range(len(items) - 1)) and items[-1][2] == N
for it in items[-(len(cl) + 4):]:
    print(it[0], round(it[1] / 30, 2), round(it[2] / 30, 2), it[3] if it[0] == 'card' else round(it[3] / 30, 2), it[4])
json.dump([[int(x) if isinstance(x, (np.integer,)) else x for x in it] for it in items], open(f'{S}/work/{KEY}/edl.json', 'w'))
tmp = f'{S}/work/{KEY}/segs'; os.makedirs(tmp, exist_ok=True); os.makedirs(f'{S}/clean', exist_ok=True)
ENC = ['-an', '-c:v', 'libx264', '-crf', '12', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', str(FPS)]
files = []
for k, (kind, a, b, x, ov) in enumerate(items):
    nf = b - a; out = f'{tmp}/{k:03d}.mp4'
    if kind == 'clip':
        # seek up to 1 s early and drop K frames: a seek straight to the frame landed one frame late in about half
        # the segments of video11/video16 (repeated first frame), which -0.5 frame offsets did not fix
        K = min(30, x); vf = f'trim=start_frame={K},setpts=PTS-STARTPTS,scale={W}:{H}'
        cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-ss', f'{(x - K) / FPS:.4f}', '-i', SRC]
        cmd += (['-i', f'{CARDS}/{ov}.png', '-filter_complex', f'[0:v]{vf}[b];[b][1:v]overlay=0:{PILL_Y[ov]}'] if ov
                else ['-vf', vf])
    else:
        zp = f"scale={W*2}:{H*2},zoompan=z='1+0.05*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nf}:s={W}x{H}:fps={FPS}"
        cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-y', '-loop', '1', '-i', f'{CARDS}/{x}.png']
        cmd += (['-loop', '1', '-i', f'{CARDS}/{ov}.png', '-filter_complex', f"[0:v]{zp}[b];[b][1:v]overlay=0:{PILL_Y[ov]}:enable=gte(t\\,0.4)"]
                if ov else ['-vf', zp])
    subprocess.run(cmd + ENC + ['-frames:v', str(nf), out], check=True); files.append(out)
lst = f'{tmp}/list.txt'; open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', f'{S}/clean/{KEY}_clean.mp4'], check=True)
for f in files: os.remove(f)
# verify body against the Swedish edit
def th(p):
    b = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', p, '-vf', 'scale=24:42,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, 42, 24).astype(np.float32).copy(); a[:, 26:36] = 0; return a
a, b = th(f'{S}/clean/{KEY}_clean.mp4'), th(SV)
d = np.abs(a - b).mean((1, 2))
print('frames', len(a), len(b), '| body diff mean', d[:c0].mean().round(2), 'max', d[:c0].max().round(2), 'frames>3:', int((d[:c0] > 3).sum()))
