#!/usr/bin/env python3
"""Compare several whole-script takes for drawn-out words, to pick the best one.

eleven_v3 sometimes stretches words, especially before commas and full stops ("tvätte---n"),
and every generation differs. Generate 2-3 takes (generations_count), split and align each into
its own SENT dir, then run this. Lower is better on every column except the speech rate.

Usage: score_takes.py SENT_A SENT_B [SENT_C ...]      (each with fused.json from align_words.py)
"""
import json
import os
import re
import sys

import numpy as np


def syl(w):
    return max(1, len(re.findall(r"[aeiouyåäöæøü]+", w.lower())))


def main():
    for d in sys.argv[1:]:
        sents = json.load(open(os.path.join(d, "fused.json"), encoding="utf-8"))["sentences"]
        chars = sum(len(s["text"]) for s in sents)
        eff = sum(s["dur_eff"] for s in sents)
        per, fin, long_words = [], [], []
        for s in sents:
            for w in s["words"]:
                dur = w["end"] - w["start"]
                r = dur / syl(w["w"])
                per.append(r)
                if re.search(r"[,.:]$", w["w"]):
                    fin.append(r)
                if r > 0.30 and dur > 0.36:
                    long_words.append(f"s{s['id']:02d} {w['w']} {dur:.2f}")
        print(f"{os.path.basename(os.path.normpath(d)):<12} rate {chars / eff:4.1f} chars/s  speech {eff:5.1f}s  "
              f"ms/syllable median {1000 * np.median(per):3.0f}  before punctuation {1000 * np.mean(fin):3.0f}  "
              f"drawn-out words {len(long_words)}: {', '.join(long_words[:10])}")


if __name__ == "__main__":
    main()
