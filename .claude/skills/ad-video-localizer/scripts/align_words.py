#!/usr/bin/env python3
"""Find when every word is spoken in each per-sentence voice clip.

ElevenLabs (via the connector) returns no timestamps, and no speech-recognition
model can be downloaded in the sandbox, so timings are estimated three
independent ways and the MEDIAN is used per word boundary. One method alone is
wrong by 0.3-0.8 s for ~20 % of words; the median of three is good enough for
1-3-word captions.

  1. syllables  - syllable nuclei (energy peaks) + pauses matched to the text
                  with dynamic programming
  2. espeak     - DTW against a robotic espeak-ng rendering of the same words
  3. reference  - DTW against a same-voice "word. by. word." take (iso.mp3,
                  cheap flash model), whose words are cut at the pauses

Inputs in SENT_DIR: NN.txt + NN.mp3 per sentence (required); optional iso.mp3 +
iso.txt + iso_map.json (from split_script.py) and isoNN.mp3 overrides for
sentences regenerated after the reference was made.
Output: SENT_DIR/fused.json (words with start/end, speech bounds, long internal
pauses, effective duration) + a printed summary.

Usage: align_words.py SENT_DIR [--lang sv]
"""
import argparse
import io
import os
import shutil
import subprocess
import sys

import librosa
import numpy as np
import scipy.signal as ss

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import clean_word, db_curve, load_json, nsyl, save_json, sentence_ids, sid, to_wav16k  # noqa: E402

SR, HOP, FPS = 16000, 160, 100
ESPEAK_VOICE = {"sv": "sv", "en": "en-us", "no": "nb", "nb": "nb", "da": "da", "de": "de", "fi": "fi",
                "fr": "fr", "es": "es", "it": "it", "nl": "nl", "pl": "pl", "pt": "pt"}


def load(path):
    y, _ = librosa.load(path, sr=SR)
    return y


def bounds(db, thr=-50):
    sp = np.where(db > thr)[0]
    return int(sp[0]), int(sp[-1] + 1)


def long_pauses(db, a, b, thr=-50, min_s=0.30):
    q = db < thr
    runs, i = [], a
    while i < b:
        if q[i]:
            j = i
            while j < b and q[j]:
                j += 1
            if (j - i) / FPS >= min_s:
                runs.append([round(i / FPS, 3), round(j / FPS, 3)])
            i = j
        else:
            i += 1
    return runs


def btype(tokens, k):
    """Break strength after word k: 2 sentence end, 1 comma-like, 0 none."""
    if k < 0 or k == len(tokens) - 1:
        return 2
    w = tokens[k]
    if w[-1] in ".!?…":
        return 2
    if w[-1] in ",:;":
        return 1
    return 0


# ---------------------------------------------------------------- method 1
def syllable_align(y, db, tokens):
    N = len(tokens)
    T = len(db)
    syl = [(k, s == 0) for k, w in enumerate(tokens) for s in range(nsyl(w))]
    E = len(syl)
    X = np.abs(librosa.stft(y, n_fft=512, hop_length=HOP))
    f = librosa.fft_frequencies(sr=SR, n_fft=512)
    env = 20 * np.log10(X[(f > 300) & (f < 2500)].sum(0) + 1e-6)
    env = np.convolve(env, np.ones(5) / 5, mode="same")[:T]
    pk, _ = ss.find_peaks(env, prominence=3.5, distance=7)
    pk = [int(p) for p in pk if db[p] > -42]
    Pn = len(pk)
    quiet = db < -55
    pauses, i = [], 0
    while i < T:
        if quiet[i]:
            j = i
            while j < T and quiet[j]:
                j += 1
            if j - i >= 7:
                pauses.append((i, j))
            i = j
        else:
            i += 1

    def pause_between(a, b):
        for s, e in pauses:
            if s >= a and e <= b:
                return (s, e)
        return None

    s0, s1 = bounds(db)
    if Pn == 0 or N == 1:
        return [s0 / FPS] + [None] * (N - 1)
    pb = [None] + [pause_between(pk[j - 1], pk[j]) for j in range(1, Pn)]

    def tcost(i, j):
        k, init = syl[i]
        p = pb[j]
        bt = btype(tokens, k - 1) if init else -1
        if p is not None:
            hard = (p[1] - p[0]) >= 13
            if not init:
                return 4.0 if hard else 0.8
            if hard:
                return -0.6 if bt > 0 else 0.6
            return -0.3 if bt > 0 else 0.1
        if init and bt == 2:
            return 1.2
        if init and bt == 1:
            return 0.25
        return 0.0

    INF = 1e9
    dp = np.full((E + 1, Pn + 1), INF)
    bk = np.zeros((E + 1, Pn + 1), np.int8)
    dp[0, 0] = 0
    for i in range(E + 1):
        for j in range(Pn + 1):
            c = dp[i, j]
            if c >= INF:
                continue
            if i < E and j < Pn:
                v = c + tcost(i, j)
                if v < dp[i + 1, j + 1]:
                    dp[i + 1, j + 1] = v
                    bk[i + 1, j + 1] = 1
            if j < Pn:
                v = c + 1.0 + (tcost(i, j) if i < E else 0)
                if v < dp[i, j + 1]:
                    dp[i, j + 1] = v
                    bk[i, j + 1] = 2
            if i < E:
                v = c + 0.9
                if v < dp[i + 1, j]:
                    dp[i + 1, j] = v
                    bk[i + 1, j] = 3
    i, j, match = E, Pn, {}
    while i > 0 or j > 0:
        m = bk[i, j]
        if m == 1:
            match[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif m == 2:
            j -= 1
        else:
            i -= 1
    fp, lp = [None] * N, [None] * N
    for si, (k, _) in enumerate(syl):
        if si in match:
            t = pk[match[si]]
            if fp[k] is None:
                fp[k] = t
            lp[k] = t
    start, end = [None] * N, [None] * N
    start[0], end[N - 1] = s0, s1
    anchored = [k for k in range(N) if fp[k] is not None]
    if not anchored:
        return [s0 / FPS] + [None] * (N - 1)
    for a, b in zip(anchored[:-1], anchored[1:]):
        lo, hi = lp[a], fp[b]
        p = pause_between(lo, hi)
        if p:
            cut_end, cut_start = p
        else:
            m = lo + int(np.argmin(db[lo:hi + 1])) if hi > lo else lo
            cut_end = cut_start = m
        mids = list(range(a + 1, b))
        if not mids:
            end[a], start[b] = cut_end, cut_start
        else:
            ws = [nsyl(tokens[k]) for k in mids]
            tot = sum(ws) + 1
            pts = [lo + (hi - lo) * (sum(ws[:n]) + 0.5) / tot for n in range(len(ws) + 1)]
            end[a] = int(pts[0])
            for n, k in enumerate(mids):
                start[k], end[k] = int(pts[n]), int(pts[n + 1])
            start[b] = int(pts[-1])
    a0 = anchored[0]
    if a0 > 0:
        ws = [nsyl(tokens[k]) for k in range(a0 + 1)]
        tot = sum(ws)
        for k in range(a0):
            start[k] = int(s0 + (fp[a0] - s0) * sum(ws[:k]) / tot)
            end[k] = int(s0 + (fp[a0] - s0) * sum(ws[:k + 1]) / tot)
        start[a0] = end[a0 - 1]
    if start[a0] is None:
        start[a0] = s0
    aL = anchored[-1]
    for k in range(aL + 1, N):
        ws = [nsyl(tokens[q]) for q in range(aL + 1, N)]
        tot = sum(ws)
        n = k - aL - 1
        start[k] = int(lp[aL] + (s1 - lp[aL]) * sum(ws[:n]) / tot)
    for k in range(N):
        if start[k] is None:
            start[k] = end[k - 1] if k > 0 and end[k - 1] is not None else s0
    return [s / FPS for s in start]


# ---------------------------------------------------------------- method 2
def espeak_align(y, db, tokens, voice):
    if not shutil.which("espeak-ng"):
        return None
    import soundfile as sf
    a, b = bounds(db)
    parts, starts, t = [], [], 0
    for w in tokens:
        text = clean_word(w).replace("-", " ")
        raw = subprocess.run(["espeak-ng", "-v", voice, "-s", "170", "--stdout", text], capture_output=True).stdout
        z, zsr = sf.read(io.BytesIO(raw), dtype="float32")
        z = librosa.resample(z, orig_sr=zsr, target_sr=SR)
        z, _ = librosa.effects.trim(z, top_db=30)
        starts.append(t)
        parts.append(z)
        t += len(z)
        g = int((0.25 if w[-1] in ",;:" else 0.0) * SR)
        parts.append(np.zeros(g, np.float32))
        t += g
    syn = np.concatenate(parts)

    def feats(sig):
        m = librosa.feature.mfcc(y=sig, sr=SR, n_mfcc=13, hop_length=HOP, n_fft=512)[1:]
        d = librosa.feature.delta(m, width=9, mode="nearest") if m.shape[1] >= 9 else m * 0
        f = np.vstack([m, d])
        f = (f - f.mean(1, keepdims=True)) / (f.std(1, keepdims=True) + 1e-6)
        v = (db_curve(sig) > -50).astype(float)[None, :]
        n = min(f.shape[1], v.shape[1])
        return np.vstack([f[:, :n], v[:, :n] * 9])

    A = feats(syn)
    B = feats(y[a * HOP:b * HOP])
    _, wp = librosa.sequence.dtw(X=A, Y=B, step_sizes_sigma=np.array([[1, 1], [0, 1], [1, 0]]),
                                 weights_add=np.array([0, 0.2, 0.2]))
    first = {}
    for p, q in wp[::-1]:
        first.setdefault(p, q)
    return [a / FPS] + [a / FPS + first[min(int(s / HOP), A.shape[1] - 1)] * HOP / SR for s in starts[1:]]


# ---------------------------------------------------------------- method 3
def segment_isolated(y, words):
    """Cut a 'word. word. word.' take into words: pauses + expected length per syllable."""
    db = db_curve(y)
    N = len(words)
    ns = np.array([nsyl(w) for w in words])
    sm = np.convolve(db, np.ones(3) / 3, mode="same")
    sp = np.where(db > -45)[0]
    s0, s1 = int(sp[0]), int(sp[-1] + 1)
    cands, q, i = [], db < -40, s0
    while i < s1:
        if q[i]:
            j = i
            while j < s1 and q[j]:
                j += 1
            cands.append(((i + j) // 2, i, j, j - i, -db[i:j].min()))
            i = j
        else:
            i += 1
    pk, _ = ss.find_peaks(-sm[s0:s1], prominence=10, distance=5)
    for p in pk + s0:
        if db[p] >= -40:
            cands.append((int(p), int(p), int(p) + 1, 0, -db[p]))
    cands.sort()
    C = len(cands)

    def bcost(c):
        L, depth = c[3], c[4]
        if L >= 15:
            return -2.0
        if L >= 8:
            return -1.0
        if L >= 3:
            return 0.0
        return 1.5 if depth > 30 else 3.0

    spf = np.sum(db[s0:s1] > -40) / ns.sum()
    INF = 1e18
    dp = np.full((N + 1, C + 1), INF)
    bk = np.zeros((N + 1, C + 1), int)
    dp[0, 0] = 0
    cstart = [s0] + [c[2] for c in cands]
    cend = [None] + [c[1] for c in cands]
    for k in range(N - 1):
        exp = ns[k] * spf + 8
        for j in np.where(dp[k] < INF)[0]:
            st = cstart[j]
            for jj in range(j + 1, C + 1):
                dur = cend[jj] - st
                if dur < 0.3 * exp:
                    continue
                if dur > 3.5 * exp:
                    break
                c = dp[k, j] + 3 * np.log(dur / exp) ** 2 + bcost(cands[jj - 1])
                if c < dp[k + 1, jj]:
                    dp[k + 1, jj] = c
                    bk[k + 1, jj] = j
    best, bj = INF, -1
    for j in np.where(dp[N - 1] < INF)[0]:
        dur = s1 - cstart[j]
        exp = ns[N - 1] * spf + 8
        c = dp[N - 1, j] + 3 * np.log(max(dur, 1) / exp) ** 2
        if c < best:
            best, bj = c, j
    if bj < 0:
        return None
    bnd, j, k = [], bj, N - 1
    while k > 0:
        bnd.append(j)
        j = bk[k, j]
        k -= 1
    bnd = bnd[::-1]
    out, prev = [], s0
    for k in range(N):
        if k < N - 1:
            c = cands[bnd[k] - 1]
            e, nxt = c[1], c[2]
        else:
            e, nxt = s1, None
        out.append((prev / FPS, e / FPS))
        prev = nxt
    return out


def reference_align(y, db, tokens, ref_y, ref_segs):
    a, b = bounds(db)
    parts, starts, t = [], [], 0
    for (s, e), w in zip(ref_segs, tokens):
        seg = ref_y[int(s * SR):int(e * SR)]
        starts.append(t)
        parts.append(seg)
        t += len(seg)
        g = int((0.15 if w[-1] in ",;:?" else 0.0) * SR)
        parts.append(np.zeros(g, np.float32))
        t += g
    ref = np.concatenate(parts)

    def feats(sig):
        m = librosa.feature.mfcc(y=sig, sr=SR, n_mfcc=20, hop_length=HOP, n_fft=512)[1:]
        d = librosa.feature.delta(m, width=9, mode="nearest") if m.shape[1] >= 9 else m * 0
        e = db_curve(sig)[None, :]
        n = min(m.shape[1], e.shape[1])
        return np.vstack([m[:, :n], d[:, :n], np.clip(e[:, :n] + 60, 0, 60) / 3])

    A, B = feats(ref), feats(y[a * HOP:b * HOP])
    Z = np.hstack([A, B])
    mu, sd = Z.mean(1, keepdims=True), Z.std(1, keepdims=True) + 1e-6
    _, wp = librosa.sequence.dtw(X=(A - mu) / sd, Y=(B - mu) / sd, metric="cosine",
                                 step_sizes_sigma=np.array([[1, 1], [0, 1], [1, 0]]),
                                 weights_add=np.array([0, 0.1, 0.1]))
    first = {}
    for p, q in wp[::-1]:
        first.setdefault(p, q)
    return [a / FPS] + [a / FPS + first[min(int(s / HOP), A.shape[1] - 1)] * HOP / SR for s in starts[1:]]


# ---------------------------------------------------------------- fusion
def fuse(estimates, db, a, b):
    ests = [e for e in estimates if e is not None]
    n = len(ests[0])
    st, spreads = [a], []
    for j in range(1, n):
        vals = sorted(e[j] for e in ests if e[j] is not None)
        if not vals:
            st.append(None)
            continue
        spreads.append(vals[-1] - vals[0])
        st.append(float(np.median(vals)))
    for j in range(1, n):  # fill gaps proportionally
        if st[j] is None:
            st[j] = st[j - 1] + 0.1
    for j in range(1, n):  # monotonic, min 60 ms per word
        st[j] = max(st[j], st[j - 1] + 0.06)
    for j in range(1, n):  # snap to a nearby energy dip (word boundary) within +-50 ms
        c = int(round(st[j] * FPS))
        lo, hi = max(c - 5, int(st[j - 1] * FPS) + 6), min(c + 6, len(db) - 1)
        if hi > lo and 0 <= c < len(db):
            m = lo + int(np.argmin(db[lo:hi]))
            if db[m] < db[c] - 3:
                st[j] = m / FPS
    st = [min(max(s, a), b) for s in st]
    return st, (float(np.median(spreads)) if spreads else 0.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sent_dir")
    ap.add_argument("--lang", default="sv")
    a = ap.parse_args()
    D = a.sent_dir
    cache = os.path.join(D, ".cache")
    os.makedirs(cache, exist_ok=True)
    voice = ESPEAK_VOICE.get(a.lang, a.lang)
    if not shutil.which("espeak-ng"):
        print("note: espeak-ng missing - using the other methods only")

    # global word-by-word reference
    iso_segs, iso_words, iso_map, ref_y = None, None, None, None
    if os.path.exists(os.path.join(D, "iso.mp3")) and os.path.exists(os.path.join(D, "iso.txt")):
        ref_y = load(to_wav16k(os.path.join(D, "iso.mp3"), os.path.join(cache, "iso.wav")))
        iso_words = [w.rstrip(".") for w in open(os.path.join(D, "iso.txt"), encoding="utf-8").read().split()]
        iso_segs = segment_isolated(ref_y, iso_words)
        iso_map = load_json(os.path.join(D, "iso_map.json"), [])
        if iso_segs is None:
            print("note: could not segment iso.mp3 - skipping the reference method")
    offsets, off = {}, 0
    for i, cnt in (iso_map or []):
        offsets[i] = (off, cnt)
        off += cnt

    out, total = [], 0.0
    print(f"{'id':>3} {'speech':>7} {'eff':>6} {'methods':>8} {'spread':>6}  text")
    for i in sentence_ids(D):
        mp3 = os.path.join(D, f"{sid(i)}.mp3")
        if not os.path.exists(mp3):
            print(f"{sid(i)}: no audio yet - skipped")
            continue
        text = open(os.path.join(D, f"{sid(i)}.txt"), encoding="utf-8").read().strip()
        tokens = text.split()
        y = load(to_wav16k(mp3, os.path.join(cache, f"{sid(i)}.wav")))
        db = db_curve(y)
        a0, a1 = bounds(db)
        pauses = long_pauses(db, a0, a1)
        est = [syllable_align(y, db, tokens), espeak_align(y, db, tokens, voice)]
        # same-voice reference: per-sentence override first, else slice of iso.mp3
        ref = None
        ov = os.path.join(D, f"iso{sid(i)}.mp3")
        clean = [clean_word(w).lower() for w in tokens]
        if os.path.exists(ov):
            oy = load(to_wav16k(ov, os.path.join(cache, f"iso{sid(i)}.wav")))
            segs = segment_isolated(oy, [clean_word(w) for w in tokens])
            if segs:
                ref = reference_align(y, db, tokens, oy, segs)
        elif iso_segs and i in offsets:
            o, cnt = offsets[i]
            if cnt == len(tokens) and [w.lower() for w in iso_words[o:o + cnt]] == clean:
                ref = reference_align(y, db, tokens, ref_y, iso_segs[o:o + cnt])
        est.append(ref)
        starts, spread = fuse(est, db, a0 / FPS, a1 / FPS)
        ends = starts[1:] + [a1 / FPS]
        dur = (a1 - a0) / FPS
        eff = dur - sum(max(0.0, (e - s) - 0.22) for s, e in pauses)
        total += eff
        n_methods = sum(1 for e in est if e is not None)
        out.append({"id": i, "text": text, "bounds": [a0 / FPS, a1 / FPS], "pauses": pauses,
                    "dur": round(dur, 3), "dur_eff": round(eff, 3), "methods": n_methods,
                    "spread": round(spread, 3),
                    "words": [{"w": w, "start": round(s, 3), "end": round(e, 3)} for w, s, e in zip(tokens, starts, ends)]})
        print(f"{sid(i):>3} {dur:6.2f}s {eff:5.2f}s {n_methods:>8} {spread:5.2f}s  {text[:60]}")
    save_json({"lang": a.lang, "sentences": out}, os.path.join(D, "fused.json"))
    print(f"total effective speech: {total:.1f}s  ->  {os.path.join(D, 'fused.json')}")


if __name__ == "__main__":
    main()
