"""Voice + new music bed, music ~17 dB under the voice, then two-pass loudnorm to -15 LUFS.
usage: mix_up.py VO.wav MUSIC.mp3 DUR OUT.wav [music_under_db]"""
import sys, subprocess, json, numpy as np, soundfile as sf
vo, mus, dur, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
under = float(sys.argv[5]) if len(sys.argv) > 5 else 17.0
SR = 48000
def load(p):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()
v, m = load(vo), load(mus)
n = int(round(dur * SR))
def fit(x):
    if len(x) >= n: return x[:n]
    return np.vstack([x, np.zeros((n - len(x), 2), np.float32)])
v, m = fit(v), fit(m)
# speech RMS over active 50 ms blocks
blk = SR // 20
def act_rms(x):
    k = len(x) // blk
    e = np.sqrt((x[:k * blk].reshape(k, blk, 2) ** 2).mean(axis=(1, 2)) + 1e-12)
    thr = np.percentile(e, 95) * 0.1
    return float(np.sqrt((e[e > thr] ** 2).mean()))
rv, rm = act_rms(v), act_rms(m)
g = (rv / rm) * 10 ** (-under / 20)
m = m * g
fi, fo = int(0.25 * SR), int(1.2 * SR)
m[:fi] *= np.linspace(0, 1, fi)[:, None]
m[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = v + m
tmp = out + '.pre.wav'
sf.write(tmp, mix, SR, subtype='FLOAT')
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', tmp, '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True)
js = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
af = (f"loudnorm=I=-15:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:"
      f"measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', af, '-ar', str(SR), '-c:a', 'pcm_s16le', out], check=True)
r = subprocess.run(['ffmpeg', '-hide_banner', '-i', out, '-af', 'ebur128=framelog=quiet', '-f', 'null', '-'], capture_output=True, text=True)
I = [l for l in r.stderr.splitlines() if l.strip().startswith('I:')][-1].strip()
print(f'music gain {20*np.log10(g):.1f} dB (music {under} dB under voice); final {I}')
