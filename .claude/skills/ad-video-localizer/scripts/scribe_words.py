#!/usr/bin/env python3
"""Use an ElevenLabs Scribe transcript (word timestamps) of the voice take.

The connector's creative_transcribe_audio, wired to the take's tts node, returns
per-word start/end seconds (words_download_url -> words.json). That gives three
things the model-free tools can only estimate:

  1. a check that the take says exactly the script (skipped or changed words),
  2. sentence starts in the take, to guide split_take.py --starts
     (needed for voices with short 0.1-0.3 s sentence pauses),
  3. word timings for the captions (--apply, after split_take + align_words).

Usage:
  scribe_words.py words.json WORK/script.txt WORK/sent --starts
      -> checks the words, writes WORK/sent/scribe_starts.json
  scribe_words.py words.json WORK/script.txt WORK/sent --apply
      -> needs sent/split.json (split_take) and sent/fused.json (align_words);
         keeps fused_align.json as a backup, prints how far the two disagree and
         writes the Scribe timings into fused.json
"""
import argparse
import json
import os
import re
import shutil
import sys

import numpy as np


def norm(s):
    return re.sub(r"[^\wåäöæøéü-]", "", s.lower())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("script")
    ap.add_argument("sent_dir")
    ap.add_argument("--starts", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    d = json.load(open(a.words, encoding="utf-8"))
    sw = [w for w in (d["words"] if isinstance(d, dict) else d) if w.get("type", "word") == "word"]
    lines = [ln.strip() for ln in open(a.script, encoding="utf-8") if ln.strip()]
    toks = [(i, t) for i, ln in enumerate(lines, 1) for t in ln.split()]
    if len(toks) != len(sw):
        print(f"WARNING: script has {len(toks)} words, the transcript {len(sw)} - the take may skip or add words")
    bad = [(i, t, x["text"]) for (i, t), x in zip(toks, sw) if norm(t) != norm(x["text"])]
    for i, t, x in bad[:20]:
        print(f"  sentence {i:02d}: script '{t}' / take '{x}'")
    if bad or len(toks) != len(sw):
        sys.exit("the take does not match the script word for word - check it before going on "
                 "(an ASR spelling difference such as a number is fine; fix NN.txt or the script and rerun)")
    print(f"take matches the script: {len(sw)} words")

    starts = {}
    for (i, _), x in zip(toks, sw):
        starts.setdefault(i, x["start"])
    if a.starts:
        p = os.path.join(a.sent_dir, "scribe_starts.json")
        json.dump(starts, open(p, "w"))
        print(f"sentence starts -> {p}  (use: split_take.py TAKE SENT --starts {p})")

    if a.apply:
        cuts = json.load(open(os.path.join(a.sent_dir, "split.json")))
        fp = os.path.join(a.sent_dir, "fused.json")
        FJ = json.load(open(fp, encoding="utf-8"))
        shutil.copy(fp, os.path.join(a.sent_dir, "fused_align.json"))
        k, diffs = 0, []
        for s in FJ["sentences"]:
            off = cuts[str(s["id"])][0]
            b0, b1 = s["bounds"]
            for w in s["words"]:
                x = sw[k]
                k += 1
                st = min(max(x["start"] - off, b0), b1)
                en = min(max(x["end"] - off, b0), b1)
                diffs.append(abs(w["start"] - st))
                w["start"], w["end"] = round(st, 3), round(max(en, st + 0.05), 3)
            for j in range(len(s["words"]) - 1):
                if s["words"][j]["end"] > s["words"][j + 1]["start"]:
                    s["words"][j]["end"] = s["words"][j + 1]["start"]
        json.dump(FJ, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        dd = np.array(diffs)
        print(f"align_words vs Scribe: median {np.median(dd):.2f}s, 90% {np.percentile(dd, 90):.2f}s, "
              f"max {dd.max():.2f}s -> Scribe timings written to {fp}")


if __name__ == "__main__":
    main()
