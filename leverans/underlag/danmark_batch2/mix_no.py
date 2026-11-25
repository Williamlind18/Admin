#!/usr/bin/env python3
"""Mix the Norwegian voice with the Swedish ad's music bed at the Swedish voice/music ratio, then loudness-match
to the Swedish ad. usage: mix_no.py VO.wav SV_AUDIO BED DUR OUT.wav [--fade-in 0] [--fade-out 0.6]"""
import json, re, subprocess, sys
import numpy as np, soundfile as sf
SR = 44100
vo_p, sv_p, bed_p, dur, out_p = sys.argv[1:6]; dur = float(dur)
def opt(n, d): return float(sys.argv[sys.argv.index(n) + 1]) if n in sys.argv else d
FI, FO = opt("--fade-in", 0.0), opt("--fade-out", 0.6)
def load(f):
    a = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(a, np.float32).astype(np.float64)
def fit(x, n): return np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n]
def ebur(f):
    o = subprocess.run(["ffmpeg", "-nostdin", "-i", f, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
def active_rms(x, pct=55):
    fr = int(0.05 * SR); k = len(x) // fr
    r = np.sqrt((x[:k * fr].reshape(k, fr) ** 2).mean(1)); return float(r[r > np.percentile(r, pct)].mean())
n = int(dur * SR)
sv = fit(load(sv_p), n); bed = fit(load(bed_p), n); vo = fit(load(vo_p), n)
if FI > 0: bed[:int(FI * SR)] *= np.linspace(0, 1, int(FI * SR))
g = float(sv @ bed / (bed @ bed))
resid = sv - g * bed
scale = active_rms(resid) / active_rms(vo)
mix = scale * vo + g * bed
f = int(FO * SR); mix[-f:] *= np.linspace(1, 0, f)
raw = out_p.replace(".wav", "_raw.wav")
sf.write(raw, np.stack([mix, mix], 1).astype(np.float32), SR, subtype="FLOAT")
I = ebur(sv_p)
m = subprocess.run(["ffmpeg", "-nostdin", "-i", raw, "-af", f"loudnorm=I={I}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I={I}:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", out_p], check=True)
# how well did the bed explain the Swedish track? (residual energy in music-only stretches)
print(json.dumps(dict(music_gain=round(g, 4), voice_scale=round(scale, 3), sv_I=I, out_I=ebur(out_p),
                      bed_fit_db=round(20 * np.log10(active_rms(resid) / active_rms(sv)), 2))))
