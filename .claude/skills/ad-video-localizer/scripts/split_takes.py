#!/usr/bin/env python3
"""Split one multi-sentence take (a paragraph read in a single generation) into one clip per sentence.

Reading 6-9 sentences in one take keeps the voice, accent and intonation consistent; the rest of
the pipeline still works per sentence. The n-1 sentence boundaries are picked among the silent
gaps by a DP that prefers long pauses close to where the text (vowel count) says each boundary
should fall. Comma or colon pauses can still win, so check the printed "CHECK" line and the gap
list, and pass --cuts to set the boundaries by hand when a sentence is clearly too long/short.

Usage:
  split_takes.py TAKE.mp3 SENT_DIR ID1 ID2 ... IDn [--cuts 3.27,8.61,...] [--gaps]
Writes SENT_DIR/NN.mp3 for each id (the ids' NN.txt must exist).
"""
import os
import re
import subprocess
import sys

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe  # noqa: E402

VOWELS = r"[aeiouyåäöéAEIOUYÅÄÖÉ]"


def main():
    args = sys.argv[1:]
    cuts_arg = None
    if "--cuts" in args:
        k = args.index("--cuts")
        cuts_arg = [float(x) for x in args[k + 1].split(",")]
        del args[k:k + 2]
    show_gaps = "--gaps" in args
    args = [x for x in args if x != "--gaps"]
    take, D, ids = args[0], args[1], args[2:]
    texts = [open(os.path.join(D, f"{i}.txt"), encoding="utf-8").read().strip() for i in ids]
    y, sr = librosa.load(take, sr=44100, mono=True)
    hop = 441
    db = librosa.amplitude_to_db(librosa.feature.rms(y=y, frame_length=1764, hop_length=hop)[0], ref=np.max)
    sil = db < max(np.percentile(db, 20) + 6, -45)
    idx = np.where(~sil)[0]
    a0, a1 = idx[0], idx[-1]
    gaps, i = [], a0
    while i < a1:
        if sil[i]:
            j = i
            while j < a1 and sil[j]:
                j += 1
            if j - i >= 8:
                gaps.append(((i + j) / 2 * hop / sr, (j - i) * hop / sr))
            i = j
        else:
            i += 1
    T0, T1 = a0 * hop / sr, a1 * hop / sr
    L = np.cumsum([len(re.findall(VOWELS, t)) + 1 for t in texts])
    exp = T0 + (T1 - T0) * L[:-1] / L[-1]
    n, m = len(ids) - 1, len(gaps)
    if show_gaps:
        print("gaps (centre/length s):", " ".join(f"{t:.2f}/{d:.2f}" for t, d in gaps))
    if cuts_arg is not None:
        if len(cuts_arg) != n:
            sys.exit(f"--cuts needs {n} times")
        bounds = [(t, 0.0) for t in cuts_arg]
    elif n == 0:
        bounds = []
    else:
        if m < n:
            sys.exit(f"only {m} pauses for {n} boundaries in {take}")
        C = np.full((n + 1, m + 1), 1e9)
        C[0, :] = 0
        P = np.zeros((n + 1, m + 1), int)
        for k in range(1, n + 1):
            for g in range(k, m + 1):
                t, d = gaps[g - 1]
                cost = -min(d, 0.8) * 4 + abs(t - exp[k - 1]) * 1.5
                P[k, g] = int(C[k - 1, :g].argmin())
                C[k, g] = C[k - 1, :g].min() + cost
        g, picks = int(C[n, n:].argmin()) + n, []
        for k in range(n, 0, -1):
            picks.append(g - 1)
            g = P[k, g]
        bounds = [gaps[p] for p in reversed(picks)]
    cuts = [0.0] + [b[0] for b in bounds] + [len(y) / sr]
    for k, i in enumerate(ids):
        tmp = os.path.join(D, f".{i}.wav")
        sf.write(tmp, y[int(cuts[k] * sr):int(cuts[k + 1] * sr)], sr)
        subprocess.run([ffmpeg_exe(), "-loglevel", "error", "-y", "-i", tmp, "-c:a", "libmp3lame", "-b:a", "192k",
                        os.path.join(D, f"{i}.mp3")], check=True)
        os.remove(tmp)
    share = [(L[k] - (L[k - 1] if k else 0)) / L[-1] * (T1 - T0) for k in range(len(ids))]
    ratio = [(cuts[k + 1] - cuts[k]) / share[k] for k in range(len(ids))]
    bad = [f"{i}:{r:.2f}" for i, r in zip(ids, ratio) if r < 0.75 or r > 1.35]
    print(os.path.basename(take), ids[0], "-", ids[-1], "cuts:", ", ".join(f"{c:.2f}" for c in cuts[1:-1]))
    if bad:
        print("  CHECK (sentence length vs its text; <0.75 or >1.35 usually means a comma pause was picked):",
              " ".join(bad), "- rerun with --gaps and set --cuts")


if __name__ == "__main__":
    main()
