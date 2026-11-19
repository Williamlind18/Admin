#!/usr/bin/env python3
"""Find sentence boundaries in a paragraph take by DTW against an espeak-ng reference of the same text,
then snap each boundary to a real silence gap in the take.

Usage: espeak_cuts.py TAKE.mp3 SENT_DIR ID1 ... IDn [--lang da]
Prints: cuts (comma separated) and a table with the DTW estimate, chosen gap and gap length.
"""
import os
import subprocess
import sys
import tempfile

import librosa
import numpy as np

SR = 16000
HOP = 160  # 10 ms


def feats(y):
    m = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=512)[1:]
    m = (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
    return m


def gaps_of(y, min_frames=8):
    hop = 160
    db = librosa.amplitude_to_db(librosa.feature.rms(y=y, frame_length=640, hop_length=hop)[0], ref=np.max)
    sil = db < max(np.percentile(db, 20) + 6, -45)
    idx = np.where(~sil)[0]
    a0, a1 = idx[0], idx[-1]
    out, i = [], a0
    while i < a1:
        if sil[i]:
            j = i
            while j < a1 and sil[j]:
                j += 1
            if j - i >= min_frames:
                out.append(((i + j) / 2 * hop / SR, (j - i) * hop / SR))
            i = j
        else:
            i += 1
    return out, a0 * hop / SR, a1 * hop / SR


def main():
    args = sys.argv[1:]
    lang = "da"
    if "--lang" in args:
        k = args.index("--lang")
        lang = args[k + 1]
        del args[k:k + 2]
    take, D, ids = args[0], args[1], args[2:]
    texts = [open(os.path.join(D, f"{i}.txt"), encoding="utf-8").read().strip() for i in ids]
    y, _ = librosa.load(take, sr=SR, mono=True)
    # reference: espeak per sentence, joined by 0.35 s silence
    parts, bnd, t = [], [], 0.0
    with tempfile.TemporaryDirectory() as td:
        for n, tx in enumerate(texts):
            f = os.path.join(td, f"{n}.wav")
            subprocess.run(["espeak-ng", "-v", lang, "-s", "165", "-w", f, tx], check=True)
            r, _ = librosa.load(f, sr=SR)
            r, _ = librosa.effects.trim(r, top_db=40)
            parts.append(r)
            t += len(r) / SR
            if n < len(texts) - 1:
                parts.append(np.zeros(int(0.35 * SR)))
                bnd.append(t + 0.175)
                t += 0.35
    ref = np.concatenate(parts)
    ty, _ = librosa.effects.trim(y, top_db=40)
    off = 0.0
    nz = np.where(np.abs(y) > np.abs(y).max() * 10 ** (-40 / 20))[0]
    off = nz[0] / SR if len(nz) else 0.0
    A, B = feats(y), feats(ref)
    _, wp = librosa.sequence.dtw(X=B, Y=A, metric="cosine", subseq=False)
    wp = wp[::-1]
    est = []
    for b in bnd:
        fr = int(b * SR / HOP)
        m = wp[wp[:, 0] == min(fr, B.shape[1] - 1)][:, 1]
        est.append(float(np.median(m)) * HOP / SR)
    gaps, T0, T1 = gaps_of(y)
    n, m = len(est), len(gaps)
    if n == 0:
        print("CUTS ")
        return
    if m < n:
        print("ERR too few gaps", m, n)
        sys.exit(1)
    C = np.full((n + 1, m + 1), 1e9)
    C[0, :] = 0
    P = np.zeros((n + 1, m + 1), int)
    for k in range(1, n + 1):
        for g in range(k, m + 1):
            tg, d = gaps[g - 1]
            cost = abs(tg - est[k - 1]) * 2.0 - min(d, 0.6) * 3.0
            P[k, g] = int(C[k - 1, :g].argmin())
            C[k, g] = C[k - 1, :g].min() + cost
    g, picks = int(C[n, n:].argmin()) + n, []
    for k in range(n, 0, -1):
        picks.append(g - 1)
        g = P[k, g]
    picks = picks[::-1]
    rows = []
    for k, p in enumerate(picks):
        tg, d = gaps[p]
        flag = " <-- far" if abs(tg - est[k]) > 0.6 else (" <-- short gap" if d < 0.2 else "")
        rows.append(f"  {ids[k]}|{ids[k+1]} est {est[k]:6.2f} gap {tg:6.2f} len {d:.2f}{flag}")
    print("CUTS " + ",".join(f"{gaps[p][0]:.2f}" for p in picks))
    print("\n".join(rows))


if __name__ == "__main__":
    main()
