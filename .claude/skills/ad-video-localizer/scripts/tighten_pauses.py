#!/usr/bin/env python3
"""Shorten long pauses inside each sentence clip (comma/colon pauses of 0.3-0.8 s in paragraph
takes) to KEEP seconds, so the planner does not have to speed the voice up.

Usage: tighten_pauses.py SENT_DIR [--min 0.20] [--keep 0.16]
Originals are kept in SENT_DIR/raw/ (re-running starts from them). Run before align_words.py.
"""
import glob
import os
import shutil
import subprocess
import sys

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe  # noqa: E402


def main():
    D = sys.argv[1]
    MIN = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 0.20
    KEEP = float(sys.argv[sys.argv.index("--keep") + 1]) if "--keep" in sys.argv else 0.16
    os.makedirs(os.path.join(D, "raw"), exist_ok=True)
    total = 0.0
    for p in sorted(glob.glob(os.path.join(D, "[0-9][0-9].mp3"))):
        raw = os.path.join(D, "raw", os.path.basename(p))
        if not os.path.exists(raw):
            shutil.copy(p, raw)
        y, sr = librosa.load(raw, sr=44100, mono=True)
        hop = 441
        db = librosa.amplitude_to_db(librosa.feature.rms(y=y, frame_length=1764, hop_length=hop)[0], ref=np.max)
        sil = db < max(np.percentile(db, 20) + 6, -45)
        idx = np.where(~sil)[0]
        a0, a1 = idx[0], idx[-1]
        runs, i = [], a0
        while i < a1:
            if sil[i]:
                j = i
                while j < a1 and sil[j]:
                    j += 1
                if (j - i) * hop / sr > MIN:
                    runs.append((i * hop, j * hop))
                i = j
            else:
                i += 1
        out, last, fade = [], 0, int(0.01 * sr)
        for s, e in runs:
            keep = int(KEEP * sr)
            cut_s, cut_e = s + keep // 2, e - keep // 2
            seg = y[last:cut_s].copy()
            seg[-fade:] *= np.linspace(1, 0, fade)
            out.append(seg)
            last = cut_e
            total += (cut_e - cut_s) / sr
        seg = y[last:].copy()
        if runs:
            seg[:fade] *= np.linspace(0, 1, fade)
        out.append(seg)
        sf.write(p + ".wav", np.concatenate(out), sr)
        subprocess.run([ffmpeg_exe(), "-loglevel", "error", "-y", "-i", p + ".wav", "-c:a", "libmp3lame",
                        "-b:a", "192k", p], check=True)
        os.remove(p + ".wav")
    print(f"removed {total:.1f} s of pauses inside sentences (pauses > {MIN}s -> {KEEP}s)")


if __name__ == "__main__":
    main()
