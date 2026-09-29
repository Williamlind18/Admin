#!/usr/bin/env python3
"""Captions from hand-picked chunks, plus white label boxes over burned-in text.

Use this instead of make_captions.py's automatic chunks when several splits read
badly ("Det löser inte upp | det"). Same style and timing rule as make_captions.py.

chunks.txt has one line per placed sentence, "NN: chunk | chunk | ...", e.g.
    17: Det löser | inte upp det
The words of each line must match the sentence's words in words_global.json
(punctuation ignored); a sentence left out with --order is simply left out here.

A label is a white rounded box (layer 1) with optional black Montserrat ExtraBold
text (layer 2), used to cover burned-in foreign text or leftover captions:
    --label "236.75,238.79,668,966,932,1090,SÄKER FÖR\\NAVLOPP"   (start,end,x0,y0,x1,y1[,text])
Leave the text out to just blank a spot (e.g. a stray English caption on white paper).
Find the pixels on a full-res frame with a ruler and the times frame by frame (fps=30),
and end the box exactly at the scene cut.

Usage: chunk_captions.py WORK/words_global.json WORK/chunks.txt --video SRC.mp4 --out WORK/captions.ass
       [--label ...] [--label-size 42] [--y 0.75] [--max-chars 15]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, probe  # noqa: E402


def clean(w):
    return re.sub(r"[.,;:]$", "", w)


def rrect(w, h, r):
    k = 0.5523 * r
    return (f"m {r} 0 l {w - r} 0 b {w - r + k} 0 {w} {r - k} {w} {r} l {w} {h - r} b {w} {h - r + k} {w - r + k} {h} "
            f"{w - r} {h} l {r} {h} b {r - k} {h} 0 {h - r + k} 0 {h - r} l 0 {r} b 0 {r - k} {r - k} 0 {r} 0")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("chunks")
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--y", type=float, default=0.75)
    ap.add_argument("--font", default="Montserrat ExtraBold")
    ap.add_argument("--size", type=float, default=0.0854)
    ap.add_argument("--max-chars", type=int, default=15)
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--label-size", type=int, default=42)
    a = ap.parse_args()
    G = load_json(a.words)
    info = probe(a.video)
    W, H, dur = info["width"], info["height"], info["duration"]

    chunks = []
    for line in open(a.chunks, encoding="utf-8"):
        if not line.strip():
            continue
        sid, rest = line.split(":", 1)
        ws = [x for x in G if x["sent"] == int(sid)]
        parts = [p.split() for p in rest.split("|")]
        want = [clean(w) for p in parts for w in p]
        got = [clean(x["w"]) for x in ws]
        if want != got:
            sys.exit(f"sentence {sid}: chunk words {want} do not match {got}")
        i = 0
        for p in parts:
            chunks.append(ws[i:i + len(p)])
            i += len(p)
    if sum(len(c) for c in chunks) != len(G):
        sys.exit("chunks.txt does not cover every placed sentence")

    events = []
    for n, c in enumerate(chunks):
        st, en = c[0]["start"], c[-1]["end"] + 0.12
        if n + 1 < len(chunks):
            nx = chunks[n + 1][0]["start"]
            en = nx if nx - c[-1]["end"] < 0.35 else min(en, nx)
        events.append((st, min(en, dur), " ".join(clean(x["w"]) for x in c)))

    def ts(t):
        return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

    size = round(W * a.size)
    outline, shadow = round(size * 0.092, 1), round(size * 0.037, 1)
    ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
           "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
           "MarginR, MarginV, Encoding",
           f"Style: Cap,{a.font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,"
           f"{outline},{shadow},5,{round(W * 0.05)},{round(W * 0.05)},0,1",
           f"Style: Lbl,{a.font},{a.label_size},&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,1,"
           "0,0,5,0,0,0,1", "", "[Events]",
           "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for st, en, txt in events:
        t = txt
        if len(txt) > a.max_chars + 3 and "-" in txt:  # long compound with hyphens: break the line after a hyphen
            parts = txt.split("-")
            half, acc, k = len(txt) // 2, 0, 0
            for k, p in enumerate(parts[:-1]):
                acc += len(p) + 1
                if acc >= half:
                    break
            t = "-".join(parts[:k + 1]) + "-\\N" + "-".join(parts[k + 1:])
        fs = "" if (len(txt) <= a.max_chars or "\\N" in t) else "{\\fs%d}" % max(round(size * 0.63), round(size * a.max_chars / len(txt)))
        ass.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\pos({W // 2},{round(H * a.y)})\\fad(40,0)}}{fs}{t}")

    for spec in a.label:
        f = spec.split(",", 6)
        st, en = float(f[0]), float(f[1])
        x0, y0, x1, y1 = (int(v) for v in f[2:6])
        text = f[6] if len(f) > 6 else ""
        w, h = x1 - x0, y1 - y0
        ass.append(f"Dialogue: 1,{ts(st)},{ts(en)},Lbl,,0,0,0,,{{\\an7\\pos({x0},{y0})\\bord0\\shad0\\1c&HFFFFFF&\\p1}}"
                   f"{rrect(w, h, min(18, h // 3))}")
        if text:
            ass.append(f"Dialogue: 2,{ts(st)},{ts(en)},Lbl,,0,0,0,,{{\\an5\\pos({(x0 + x1) // 2},{(y0 + y1) // 2})"
                       f"\\bord0\\shad0}}{text}")

    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(ass) + "\n")
    print(f"{len(events)} caption chunks + {len(a.label)} labels -> {a.out}")


if __name__ == "__main__":
    main()
