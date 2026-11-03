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
Needs SENT_DIR/NN.txt from split_script.py. Writes SENT_DIR/NN.mp3 (320 kb/s)
and prints one row per sentence - check that 'ratio' stays roughly 0.6-1.4 and
that every 'pause_after' is a real pause (>= ~0.3 s). A pause under 0.2 s or a
ratio far off (both are marked '<-- check') means a cut landed inside a sentence: listen/inspect before going on.

--words: some voices barely pause between sentences (video 39, "kvinna 30-40 år skånsk - SE": 0.06-0.15 s),
so the silences cannot tell sentence breaks from word gaps. Transcribe the take with ElevenLabs Scribe
(creative_transcribe_audio, ~5.5 credits per second) and pass its word list ([{text, start, end}, ...],
the `words` of the transcript): the script's words are matched to Scribe's words and each sentence is cut
at the quietest point between its last word and the next sentence's first word.
"""
import argparse
import json
import os
import re
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
    ap.add_argument("--words", help="Scribe word timings of the take (json list of {text, start, end})")
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
    if a.words:
        return split_by_words(a, ids, texts, y, sr, db)
    sp = np.where(db > -50)[0]
    s0, s1 = int(sp[0]), int(sp[-1] + 1)
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

    ff = ffmpeg_exe()
    print(f"take {len(y) / sr:.1f}s, speech {s0 / FPS:.2f}-{s1 / FPS:.2f}s, {C} silences, {N} sentences")
    print(" id   start     end    dur  expect  ratio  pause_after  text")
    for k in range(N):
        st = starts[first[k]] / FPS
        en = (ends[first[k + 1] - 1] if k + 1 < N else s1) / FPS
        pause = 0.0
        if k + 1 < N:
            c = cands[first[k + 1] - 1]
            pause = (c[1] - c[0]) / FPS
        flag = "  <-- check" if (k + 1 < N and pause < 0.35) or not 0.6 <= (en - st) / exp[k] <= 1.5 else ""
        print(f" {ids[k]:02d} {st:7.2f} {en:7.2f} {en - st:6.2f} {exp[k]:6.2f}  {(en - st) / exp[k]:5.2f}"
              f"   {pause:5.2f}   {texts[k][:44]}{flag}")
        a0 = max(0.0, st - 0.06)
        b0 = en + (min(0.12, pause / 2) if k + 1 < N else 0.3)
        subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", a.take, "-ss", f"{a0:.3f}",
                        "-to", f"{b0:.3f}", "-c:a", "libmp3lame", "-b:a", "320k",
                        os.path.join(a.sent_dir, f"{sid(ids[k])}.mp3")], check=True)


def norm(w):
    return re.sub(r"[^\wåäöæøü]", "", w.lower())


def split_by_words(a, ids, texts, y, sr, db):
    import difflib
    words = json.load(open(a.words, encoding="utf-8"))
    if isinstance(words, dict):
        words = words.get("words", [])
    words = [w for w in words if w.get("type", "word") == "word" and norm(w["text"])]
    sw, owner = [], []  # script words and the sentence each belongs to
    for k, t in enumerate(texts):
        for w in t.replace("-", " ").split():
            if norm(w):
                sw.append(norm(w))
                owner.append(k)
    tw = []
    for w in words:  # split hyphenated Scribe words the same way
        parts = [p for p in w["text"].replace("-", " ").split() if norm(p)]
        for p in parts:
            tw.append((norm(p), w["start"], w["end"]))
    sm = difflib.SequenceMatcher(None, sw, [x[0] for x in tw], autojunk=False)
    match = {}
    for blk in sm.get_matching_blocks():
        for d in range(blk.size):
            match[blk.a + d] = blk.b + d
    print(f"matched {len(match)} of {len(sw)} script words to {len(tw)} Scribe words")
    N = len(ids)
    first_w = [owner.index(k) for k in range(N)]
    last_w = [len(owner) - 1 - owner[::-1].index(k) for k in range(N)]

    def t_of(i, end, step):
        while 0 <= i < len(sw) and i not in match:
            i += step
        if not 0 <= i < len(sw):
            return None
        x = tw[match[i]]
        return x[2] if end else x[1]

    starts, ends = [], []
    for k in range(N):
        starts.append(t_of(first_w[k], False, +1))
        ends.append(t_of(last_w[k], True, -1))
    cuts = []
    for k in range(N - 1):
        e, s_ = ends[k], starts[k + 1]
        lo, hi = int(min(e, s_) * FPS) - 3, int(max(e, s_) * FPS) + 3
        seg = db[max(lo, 0):max(hi, lo + 1)]
        cuts.append((max(lo, 0) + int(np.argmin(seg))) / FPS)
    ff = ffmpeg_exe()
    total = len(y) / sr
    print(f"take {total:.1f}s, {N} sentences, cut by Scribe word timings")
    print(" id   start     end    dur  gap_after  text")
    for k in range(N):
        st = starts[k] if k == 0 else max(starts[k], cuts[k - 1]) if starts[k] else cuts[k - 1]
        en = ends[k] if k == N - 1 else min(ends[k], cuts[k]) if ends[k] else cuts[k]
        gap = (starts[k + 1] - ends[k]) if k + 1 < N and starts[k + 1] and ends[k] else 0.0
        flag = "  <-- check" if k + 1 < N and gap < 0.03 else ""
        print(f" {ids[k]:02d} {st:7.2f} {en:7.2f} {en - st:6.2f}   {gap:5.2f}   {texts[k][:44]}{flag}")
        a0 = max(0.0, st - 0.06) if k == 0 else max(cuts[k - 1], st - 0.06)
        b0 = (en + 0.3) if k == N - 1 else min(cuts[k] + 0.02, en + 0.12)
        subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-i", a.take, "-ss", f"{a0:.3f}",
                        "-to", f"{min(b0, total):.3f}", "-c:a", "libmp3lame", "-b:a", "320k",
                        os.path.join(a.sent_dir, f"{sid(ids[k])}.mp3")], check=True)


if __name__ == "__main__":
    main()
