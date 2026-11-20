#!/usr/bin/env python3
"""Trim leading breath / trailing room noise of each sentence clip NN.mp3 (originals kept in raw/).
Onset = first 10 ms frame above ON dB (rel. clip max) minus PRE s; end = last frame above OFF dB plus POST s.
usage: trim_breaths.py SENT_DIR [--on -26 --off -30 --pre 0.10 --post 0.10]"""
import glob, os, shutil, subprocess, sys
import librosa, numpy as np
D = sys.argv[1]
def opt(n, d): return float(sys.argv[sys.argv.index(n) + 1]) if n in sys.argv else d
ON, OFF, PRE, POST = opt("--on", -26), opt("--off", -30), opt("--pre", 0.10), opt("--post", 0.10)
os.makedirs(os.path.join(D, "raw"), exist_ok=True)
tot0 = tot1 = 0
for p in sorted(glob.glob(os.path.join(D, "[0-9][0-9].mp3"))):
    raw = os.path.join(D, "raw", os.path.basename(p))
    if not os.path.exists(raw):
        shutil.copy(p, raw)
    y, sr = librosa.load(raw, sr=44100)
    e = librosa.feature.rms(y=y, frame_length=1764, hop_length=441)[0]
    db = 20 * np.log10(e + 1e-9); db -= db.max()
    on = np.where(db > ON)[0][0] * 0.01; off = np.where(db > OFF)[0][-1] * 0.01 + 0.04
    a = max(0.0, on - PRE); b = min(len(y) / sr, off + POST)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-ss", f"{a:.3f}", "-to", f"{b:.3f}",
                    "-c:a", "libmp3lame", "-b:a", "192k", p], check=True)
    tot0 += len(y) / sr; tot1 += b - a
print(f"{D}: {tot0:.1f}s -> {tot1:.1f}s")
