#!/usr/bin/env python3
"""Rebuild captions.ass from hand-written caption chunks.

make_captions.py splits blindly in places ("ekosystem i det | tysta"). When
several chunks are clumsy, write them by hand: one line per sentence, in spoken
order, chunks separated by '|', words spelled exactly as in words_global.json
(trailing punctuation dropped). Run make_captions.py first (it writes the style
header and the .srt), then this script rewrites the Dialogue lines of the .ass
with the same position, font sizing and timing rule.

Usage: hand_captions.py WORK/words_global.json CHUNKS.txt WORK/captions.ass
       [--video-duration SEC] [--y 0.75] [--max-chars 15]
"""
import argparse
import json
import re
import sys


def clean(w):
    return re.sub(r"[.,;:!?]$", "", w)


def ts(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("chunks")
    ap.add_argument("ass")
    ap.add_argument("--video-duration", type=float, default=1e9)
    ap.add_argument("--y", type=float, default=0.75)
    ap.add_argument("--max-chars", type=int, default=15)
    a = ap.parse_args()

    G = json.load(open(a.words, encoding="utf-8"))
    words = G if isinstance(G, list) else G["words"]
    lines = [l.strip() for l in open(a.chunks, encoding="utf-8") if l.strip()]
    by_sent = {}
    for x in words:
        by_sent.setdefault(x["sent"], []).append(x)
    sents = sorted(by_sent)
    if len(sents) != len(lines):
        sys.exit(f"{len(lines)} chunk lines but {len(sents)} sentences")

    chunks = []
    for sid, line in zip(sents, lines):
        ws, i = by_sent[sid], 0
        for part in line.split("|"):
            toks = part.split()
            got = [clean(x["w"]) for x in ws[i:i + len(toks)]]
            if got != toks:
                sys.exit(f"sentence {sid}: chunk {toks} != words {got}")
            chunks.append((ws[i:i + len(toks)], part.strip()))
            i += len(toks)
        if i != len(ws):
            sys.exit(f"sentence {sid}: {len(ws) - i} words not in any chunk")

    head = []
    for l in open(a.ass, encoding="utf-8"):
        if l.startswith("Dialogue:"):
            break
        head.append(l.rstrip("\n"))
    h = "\n".join(head)
    size = int(re.search(r"Style: Cap,[^,]+,(\d+)", h).group(1))
    W = int(re.search(r"PlayResX: (\d+)", h).group(1))
    H = int(re.search(r"PlayResY: (\d+)", h).group(1))

    out = list(head)
    for n, (grp, txt) in enumerate(chunks):
        st, en = grp[0]["start"], grp[-1]["end"] + 0.12
        if n + 1 < len(chunks):
            nx = chunks[n + 1][0][0]["start"]
            en = nx if nx - grp[-1]["end"] < 0.35 else min(en, nx)
        t = txt
        if len(txt) > a.max_chars + 3 and "-" in txt:  # long hyphen compound: break after the middle hyphen
            parts = txt.split("-")
            k = max(1, (len(parts) + 1) // 2)
            t = "-".join(parts[:k]) + "-\\N" + "-".join(parts[k:])
        fs = "" if (len(txt) <= a.max_chars or "\\N" in t) else \
            "{\\fs%d}" % max(round(size * 0.63), round(size * a.max_chars / len(txt)))
        out.append(f"Dialogue: 0,{ts(st)},{ts(min(en, a.video_duration))},Cap,,0,0,0,,"
                   f"{{\\pos({W // 2},{round(H * a.y)})\\fad(40,0)}}{fs}{t}")
    with open(a.ass, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"{len(chunks)} hand-written caption chunks -> {a.ass}")


if __name__ == "__main__":
    main()
