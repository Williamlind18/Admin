#!/usr/bin/env python3
"""Split ONE continuous voice take of the whole script into per-sentence clips NN.mp3.

Why: separate generations per sentence sound like different people (eleven_v3
varies timbre, stress and pronunciation from call to call). One take keeps the
same speaker and a natural flow; cutting it at the sentence pauses keeps the
per-sentence pipeline (align_words -> plan_timeline -> build_voiceover) working.

How: the take is read with sentence pauses of ~0.4-0.8 s. The cuts are chosen
among the silences with dynamic programming: each sentence should last about as
long as its syllable count predicts (or as the same sentence did in earlier
clips, with --expect), and longer silences are preferred as sentence breaks.

Usage: split_take.py TAKE.mp3 SENT_DIR [--expect durations.json] [--words scribe_words.json]

--words: a Scribe transcript of the take (the `words` list, or the file behind
`words_download_url`). The cuts are then placed between the last word of one
sentence and the first word of the next (script and transcript words are matched
with difflib), which is exact even for voices that pause only ~0.1 s between
sentences, where the pause-based split guesses.
Needs SENT_DIR/NN.txt from split_script.py. Writes SENT_DIR/NN.mp3 (320 kb/s)
and prints one row per sentence - check that 'ratio' stays roughly 0.6-1.4 and
that every 'pause_after' is a real pause (>= ~0.3 s). A pause under 0.2 s or a
ratio far off (both are marked '<-- check') means a cut landed inside a sentence: listen/inspect before going on.
"""
import argparse
import json
import os
import subprocess
import sys

import librosa
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import db_curve, ffmpeg_exe, nsyl, sentence_ids, sid  # noqa: E402

FPS = 100  # db_curve frames per second at 16 kHz / hop 160


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("take")
    ap.add_argument("sent_dir")
    ap.add_argument("--expect", help="json {id: seconds} with earlier per-sentence durations (optional)")
    ap.add_argument("--words", help="Scribe word timings of the take (json list or {'words': [...]})")
    a = ap.parse_args()

    ids = sentence_ids(a.sent_dir)
    texts = [open(os.path.join(a.sent_dir, f"{sid(i)}.txt"), encoding="utf-8").read().strip() for i in ids]
    if a.expect:
        old = json.load(open(a.expect))
        w = np.array([float(old[str(i)]) for i in ids])
    else:  # syllables + a small constant per sentence for its onset/final lengthening
        w = np.array([sum(nsyl(t) for t in txt.split()) + 1.5 for txt in texts], float)

    y, sr = librosa.load(a.take, sr=16000)
    db = db_curve(y)
    sp = np.where(db > -50)[0]
    s0, s1 = int(sp[0]), int(sp[-1] + 1)
    if a.words:
        spans, matched, total = spans_from_words(a.words, texts, s1 / FPS)
        exp = w / w.sum() * (s1 - s0) / FPS
        write_clips(a, ids, texts, spans, exp, y, sr, f"cuts from {a.words} ({matched}/{total} words matched)",
                    pause_check=False)
        return
    q = db < -42
    cands, i = [], s0
    while i < s1:
        if q[i]:
            j = i
            while j < s1 and q[j]:
                j += 1
            if j - i >= 6:
                cands.append((i, j))
            i = j
        else:
            i += 1
    N, C = len(ids), len(cands)
    exp = w / w.sum() * (s1 - s0) / FPS  # expected seconds per sentence, its share of pauses included
    starts = [s0] + [c[1] for c in cands]  # a sentence starts where the previous silence ends
    ends = [c[0] for c in cands] + [s1]   # and ends where the next silence starts

    def bonus(c):
        L = c[1] - c[0]
        # sentence breaks in a v3 take are ~0.4-0.8 s, comma pauses ~0.1-0.35 s: favour the long ones strongly
        return -4.0 if L >= 45 else -3.0 if L >= 35 else -1.0 if L >= 25 else 0.5 if L >= 12 else 1.5

    INF = 1e18
    dp = np.full((N, C + 1), INF)
    bk = np.full((N, C + 1), -1, int)
    dp[0][0] = 0
    for k in range(N - 1):
        for j in np.where(dp[k] < INF)[0]:
            for e in range(j, C):
                dur = (ends[e] - starts[j]) / FPS
                if dur < 0.4 * exp[k]:
                    continue
                if dur > 2.2 * exp[k]:
                    break
                c = dp[k][j] + 4 * np.log(dur / exp[k]) ** 2 + bonus(cands[e])
                if c < dp[k + 1][e + 1]:
                    dp[k + 1][e + 1] = c
                    bk[k + 1][e + 1] = j
    best, bj = INF, -1
    for j in np.where(dp[N - 1] < INF)[0]:
        c = dp[N - 1][j] + 4 * np.log(max((s1 - starts[j]) / FPS, 0.05) / exp[N - 1]) ** 2
        if c < best:
            best, bj = c, j
    if bj < 0:
        sys.exit("no segmentation found - does the take contain every sentence of script.txt?")
    first = [0] * N
    first[N - 1] = bj
    for k in range(N - 1, 0, -1):
        first[k - 1] = bk[k][first[k]]

    spans = []  # (start, end, pause_after) in seconds
    for k in range(N):
        st = starts[first[k]] / FPS
        en = (ends[first[k + 1] - 1] if k + 1 < N else s1) / FPS
        pause = 0.0
        if k + 1 < N:
            c = cands[first[k + 1] - 1]
            pause = (c[1] - c[0]) / FPS
        spans.append((st, en, pause))
    write_clips(a, ids, texts, spans, exp, y, sr, f"{C} silences", pause_check=True)


def spans_from_words(path, texts, s1):
    """Sentence spans from Scribe word timings, matched to the script words with difflib."""
    import difflib
    import re
    d = json.load(open(path, encoding="utf-8"))
    ws = d.get("words", d) if isinstance(d, dict) else d
    ws = [w for w in ws if w.get("type", "word") == "word"]
    norm = lambda t: re.sub(r"[^0-9a-zåäöéü]", "", t.lower())
    hyp = [norm(w["text"]) for w in ws]
    ref, owner = [], []
    for k, t in enumerate(texts):
        for tok in t.split():
            ref.append(norm(tok))
            owner.append(k)
    m = [None] * len(ref)
    for blk in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_matching_blocks():
        for i in range(blk.size):
            m[blk.a + i] = blk.b + i
    N = len(texts)
    first_w, last_w = [None] * N, [None] * N
    for i, k in enumerate(owner):
        if m[i] is None:
            continue
        if first_w[k] is None:
            first_w[k] = m[i]
        last_w[k] = m[i]
    missing = [k + 1 for k in range(N) if first_w[k] is None]
    if missing:
        sys.exit(f"--words: no transcript words matched sentence(s) {missing}")
    spans = []
    for k in range(N):
        st = ws[first_w[k]]["start"]
        en = ws[last_w[k]]["end"] if k + 1 == N else ws[last_w[k]]["end"]
        nxt = ws[first_w[k + 1]]["start"] if k + 1 < N else None
        if nxt is not None and nxt < en:  # overlapping estimates: cut in the middle
            en = nxt = (en + nxt) / 2
        spans.append((st, en, (nxt - en) if nxt is not None else 0.0))
    matched = sum(x is not None for x in m)
    return spans, matched, len(ref)


def write_clips(a, ids, texts, spans, exp, y, sr, note, pause_check):
    ff = ffmpeg_exe()
    N = len(ids)
    print(f"take {len(y) / sr:.1f}s, {note}, {N} sentences")
    print(" id   start     end    dur  expect  ratio  pause_after  text")
    for k in range(N):
        st, en, pause = spans[k]
        bad_pause = pause_check and k + 1 < N and pause < 0.35
        flag = "  <-- check" if bad_pause or not 0.6 <= (en - st) / exp[k] <= 1.5 else ""
        print(f" {ids[k]:02d} {st:7.2f} {en:7.2f} {en - st:6.2f} {exp[k]:6.2f}  {(en - st) / exp[k]:5.2f}"
              f"   {pause:5.2f}   {texts[k][:44]}{flag}")
        a0 = max(0.0, st - 0.06)
        b0 = en + (min(0.12, pause / 2) if k + 1 < N else 0.3)
        subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", a.take, "-ss", f"{a0:.3f}",
                        "-to", f"{b0:.3f}", "-c:a", "libmp3lame", "-b:a", "320k",
                        os.path.join(a.sent_dir, f"{sid(ids[k])}.mp3")], check=True)


if __name__ == "__main__":
    main()
