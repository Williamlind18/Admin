"""Sentence cuts for split_takes.py --cuts from Scribe word timings.
Usage: cuts_from_words.py TAKE.mp3 WORDS.json SENT_DIR ID1 ID2 ...
Each cut is placed in the quietest stretch between the last word of one sentence and the first
word of the next (Scribe word ends are loose, so the audio decides inside that window)."""
import difflib, json, os, re, sys
import librosa, numpy as np

take, wj, D, *ids = sys.argv[1:]
norm = lambda s: re.sub(r"[^\wåäöé-]", "", s.lower())
ws = json.load(open(wj))
ws = [w for w in (ws.get("words", ws) if isinstance(ws, dict) else ws) if w.get("type", "word") == "word"]
sent = [open(os.path.join(D, f"{i}.txt"), encoding="utf-8").read().split() for i in ids]
script = [(k, norm(t)) for k, s in enumerate(sent) for t in s]
heard = [norm(w["text"]) for w in ws]
sm = difflib.SequenceMatcher(a=[t for _, t in script], b=heard, autojunk=False)
owner = {}
for a, b, n in sm.get_matching_blocks():
    for j in range(n):
        owner[b + j] = script[a + j][0]
y, sr = librosa.load(take, sr=22050)
hop = 110
db = librosa.amplitude_to_db(librosa.feature.rms(y=y, frame_length=441, hop_length=hop)[0], ref=np.max)
cuts = []
for k in range(len(ids) - 1):
    last = max(j for j, o in owner.items() if o == k)
    first = min(j for j, o in owner.items() if o == k + 1)
    t0, t1 = ws[last]["end"] - 0.25, ws[first]["start"] + 0.08
    f0, f1 = int(t0 * sr / hop), int(t1 * sr / hop)
    seg = db[f0:f1]
    quiet = seg < min(seg) + 6
    # centre of the longest quiet run
    best, run, s = (0, f0), 0, None
    for i, q in enumerate(list(quiet) + [False]):
        if q and s is None:
            s = i
        if not q and s is not None:
            if i - s > best[0]:
                best = (i - s, f0 + (s + i) // 2)
            s = None
    c = best[1] * hop / sr
    cuts.append(round(c, 2))
    print(f"{ids[k]}|{ids[k+1]}: '{ws[last]['text']}' {ws[last]['end']:.2f} -> '{ws[first]['text']}' {ws[first]['start']:.2f}  cut {c:.2f}", file=sys.stderr)
print(",".join(f"{c:.2f}" for c in cuts))
