"""For each 3 s window of the Swedish ad, find which music time matches best (raw waveform xcorr at 8 kHz).
usage: bedmap.py KEY   -> prints t_video : t_music (corr)"""
import sys, subprocess, numpy as np
SR = 8000
def load(f):
    return np.frombuffer(subprocess.run(["ffmpeg","-nostdin","-v","error","-i",f,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,np.float32).astype(np.float64)
k = sys.argv[1]; sv = load(f"vid/{k}.mp4"); m = load(f"music/{k}.mp3")
W = 3*SR
from numpy.fft import rfft, irfft
out = []
for t0 in np.arange(0, len(sv)/SR - 3, 6.0):
    s = sv[int(t0*SR):int(t0*SR)+W]; s = s - s.mean()
    n = len(m) + W
    nf = 1 << int(np.ceil(np.log2(n)))
    c = irfft(rfft(m, nf) * np.conj(rfft(s, nf)), nf)[:len(m)-W]
    # normalise by local music energy
    e = np.sqrt(np.convolve(m**2, np.ones(W), 'valid')[:len(c)] * (s@s)) + 1e-9
    r = c / e; j = int(np.argmax(r))
    out.append(f"{t0:5.0f}:{j/SR:6.2f}({r[j]:.2f})")
print(" ".join(out))
