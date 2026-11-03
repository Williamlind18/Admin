#!/usr/bin/env python3
"""Split a one-take voice into sentence clips using the word-by-word reference (iso.mp3).

Use it when split_take.py cannot find the sentence breaks because the take has very short
pauses (0.05-0.3 s, Maskinrent video 8): every row marked '<-- check' and ratios far from 1.

How: the iso reference is cut into words (align_words.segment_isolated) and re-joined into one
signal with sentence gaps. DTW (MFCC + deltas + energy) against the whole take predicts where each
sentence starts. Each cut is then snapped to the nearest silence within 0.35 s, or to the deepest
energy dip when there is none. Clips get the same padding as split_take.py.

Usage: split_take_ref.py WORK/take.mp3 WORK/sent
Needs SENT_DIR/NN.txt, iso.txt, iso_map.json (split_script.py) and iso.mp3 (the flash reference).
"""
import json
import os
import subprocess
import sys

import librosa
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import align_words as aw  # noqa: E402
from common import db_curve, ffmpeg_exe, sid, to_wav16k  # noqa: E402

SR, HOP = 16000, 320


def feats(sig):
    m = librosa.feature.mfcc(y=sig, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=1024)[1:]
    d = librosa.feature.delta(m, width=9, mode="nearest")
    e = librosa.amplitude_to_db(librosa.feature.rms(y=sig, frame_length=1024, hop_length=HOP), ref=1.0)
    n = min(m.shape[1], e.shape[1])
    return np.vstack([m[:, :n], d[:, :n], np.clip(e[:, :n] + 60, 0, 60) / 3])


def main():
    take, D = sys.argv[1], sys.argv[2]
    cache = os.path.join(D, "_cache")
    os.makedirs(cache, exist_ok=True)
    ref_y = aw.load(to_wav16k(os.path.join(D, "iso.mp3"), os.path.join(cache, "iso.wav")))
    words = [w.rstrip(".") for w in open(os.path.join(D, "iso.txt"), encoding="utf-8").read().split()]
    segs = aw.segment_isolated(ref_y, words)
    if segs is None:
        sys.exit("could not cut iso.mp3 into words")
    imap = json.load(open(os.path.join(D, "iso_map.json")))
    parts, sstart, t, o = [], {}, 0, 0
    for i, cnt in imap:
        toks = open(os.path.join(D, f"{sid(i)}.txt"), encoding="utf-8").read().split()
        sstart[i] = t
        for k in range(cnt):
            s, e = segs[o + k]
            seg = ref_y[int(s * SR):int(e * SR)]
            parts.append(seg)
            t += len(seg)
            g = int((0.45 if k == cnt - 1 else 0.15 if toks[k][-1] in ",;:" else 0.02) * SR)
            parts.append(np.zeros(g, np.float32))
            t += g
        o += cnt
    ref = np.concatenate(parts)
    y = aw.load(to_wav16k(take, os.path.join(cache, "take.wav")))
    A, B = feats(ref), feats(y)
    Z = np.hstack([A, B])
    mu, sd = Z.mean(1, keepdims=True), Z.std(1, keepdims=True) + 1e-6
    _, wp = librosa.sequence.dtw(X=(A - mu) / sd, Y=(B - mu) / sd, metric="cosine",
                                 step_sizes_sigma=np.array([[1, 1], [0, 1], [1, 0]]),
                                 weights_add=np.array([0, 0.1, 0.1]))
    first = {}
    for p, q in wp[::-1]:
        first.setdefault(p, q)
    ids = [i for i, _ in imap]
    pred = {i: first[min(sstart[i] // HOP, A.shape[1] - 1)] * HOP / SR for i in ids}

    db = db_curve(y)  # 100 frames per second
    sp = np.where(db > -50)[0]
    s0, s1 = int(sp[0]), int(sp[-1] + 1)
    q, sil, i = db < -42, [], s0
    while i < s1:
        if q[i]:
            j = i
            while j < s1 and q[j]:
                j += 1
            if j - i >= 4:
                sil.append((i, j))
            i = j
        else:
            i += 1
    sm = np.convolve(db, np.ones(5) / 5, mode="same")
    cuts = []
    for k in ids[1:]:
        tt = int(round(pred[k] * 100))
        near = [s for s in sil if abs((s[0] + s[1]) / 2 - tt) <= 35]
        if near:
            s = max(near, key=lambda s: (s[1] - s[0]) - 0.2 * abs((s[0] + s[1]) / 2 - tt))
            cuts.append((s[0], s[1], "silence"))
        else:
            m = tt - 35 + int(np.argmin(sm[tt - 35:tt + 35]))
            cuts.append((m - 2, m + 2, "dip  <-- check"))
    ff = ffmpeg_exe()
    print(" id   start     end    dur  pause_after  cut")
    st = s0
    for n, k in enumerate(ids):
        last = n == len(cuts)
        en = s1 if last else cuts[n][0]
        pause = 0.0 if last else (cuts[n][1] - cuts[n][0]) / 100
        print(f" {k:02d} {st / 100:7.2f} {en / 100:7.2f} {(en - st) / 100:6.2f}   {pause:5.2f}   {'' if last else cuts[n][2]}")
        a0 = max(0.0, st / 100 - 0.06)
        b0 = en / 100 + (0.3 if last else min(0.12, pause / 2))
        subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", take, "-ss", f"{a0:.3f}", "-to", f"{b0:.3f}",
                        "-c:a", "libmp3lame", "-b:a", "320k", os.path.join(D, f"{sid(k)}.mp3")], check=True)
        if not last:
            st = cuts[n][1]


if __name__ == "__main__":
    main()
