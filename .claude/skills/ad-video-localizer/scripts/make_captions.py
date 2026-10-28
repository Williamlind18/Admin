#!/usr/bin/env python3
"""Burned-in caption file (ASS) + subtitle file (SRT) from words_global.json.

Style that the user approved: 1-3 words at a time (max ~15 characters), bold
white Montserrat ExtraBold with a thick black outline, centred at 75 % of the
frame height (where UGC ads usually have their old - often blurred - captions,
so the new text covers them). Each phrase is split into chunks by a small search
that avoids ending a chunk on a small word ("och", "i", "ett" ...) and lone short words.
Everything scales with the video resolution.

Usage: make_captions.py WORK/words_global.json --video SRC.mp4 --out-dir WORK
       [--y 0.75] [--font "Montserrat ExtraBold"] [--lang sv] [--max-words 3] [--max-chars 15]
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, probe  # noqa: E402

FUNC = {
    "sv": "det den de en ett att och i på till av som med för om ditt din dina mina min mitt kan är har så ut från efter "
          "inte du jag man vi sig mig dig hela alla var vad när upp ner bara nu över fri tolv trettio femtio sextio "
          "ni er ert era sin sitt sina hans hennes deras vid mot än utan under genom",
    "en": "the a an and or to of in on at for with your my our their is are was be it this that so as by from not "
          "you i we they he she its all just up out",
}
# words that must not end a chunk mid-phrase (conjunctions, prepositions, articles)
DANGLE = {
    "sv": "och i på till av som med för om att en ett mot från efter utan under genom vid än eller men så",
    "en": "the a an and or to of in on at for with by from as but",
}


def clean(w):
    return re.sub(r"[.,;:]$", "", w)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words")
    ap.add_argument("--video", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--y", type=float, default=0.75, help="vertical centre of the captions (0 top - 1 bottom)")
    ap.add_argument("--font", default="Montserrat ExtraBold")
    ap.add_argument("--size", type=float, default=0.0854, help="font size as a fraction of video width")
    ap.add_argument("--lang", default="sv")
    ap.add_argument("--max-words", type=int, default=3)
    ap.add_argument("--max-chars", type=int, default=15)
    ap.add_argument("--upper", action="store_true", help="ALL CAPS captions")
    a = ap.parse_args()
    G = load_json(a.words)
    info = probe(a.video)
    W, H, dur = info["width"], info["height"], info["duration"]
    func = set(FUNC.get(a.lang, "").split())

    def L(ws):
        return len(" ".join(clean(c["w"]) for c in ws))

    dangle = set(DANGLE.get(a.lang, "").split())

    def cost(c, last):
        """Fewer chunks are better; a chunk that ends on a small word mid-phrase, a lone short word
        or a chunk over the character limit costs extra."""
        end = clean(c[-1]["w"]).lower()
        k = 1.0 + 0.4 * max(0, L(c) - a.max_chars)
        if not last:
            k += 4.0 if end in dangle else 1.5 if end in func else 0.0
        if len(c) == 1 and len(clean(c[0]["w"])) <= 4:
            k += 1.5
        return k

    # phrases end at a sentence boundary or punctuation; inside each, pick the cheapest split into 1-3 words
    phrases, cur = [], []
    for x in G:
        if cur and (cur[-1]["sent"] != x["sent"] or cur[-1]["w"][-1] in ",.!?…"):
            phrases.append(cur)
            cur = []
        cur.append(x)
    if cur:
        phrases.append(cur)
    chunks = []
    for ph in phrases:
        n = len(ph)
        best, back = [0.0] + [None] * n, [0] * (n + 1)
        for i in range(1, n + 1):
            for j in range(max(0, i - a.max_words), i):
                c = ph[j:i]
                if best[j] is None or (len(c) > 1 and L(c) > a.max_chars + 4):
                    continue
                v = best[j] + cost(c, i == n)
                if best[i] is None or v < best[i]:
                    best[i], back[i] = v, j
        cut, i = [], n
        while i > 0:
            cut.append((back[i], i))
            i = back[i]
        chunks += [ph[j:i] for j, i in reversed(cut)]

    events = []
    for n, c in enumerate(chunks):
        st, en = c[0]["start"], c[-1]["end"] + 0.12
        if n + 1 < len(chunks):
            nx = chunks[n + 1][0]["start"]
            en = nx if nx - c[-1]["end"] < 0.35 else min(en, nx)
        txt = " ".join(clean(x["w"]) for x in c)
        events.append((st, min(en, dur), txt.upper() if a.upper else txt))

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
           f"{outline},{shadow},5,{round(W * 0.05)},{round(W * 0.05)},0,1", "", "[Events]",
           "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for st, en, txt in events:
        t = txt
        if len(txt) > a.max_chars + 3 and "-" in txt:  # long compound with hyphens: break the line after a hyphen
            parts = txt.split("-")
            half = len(txt) // 2
            acc, k = 0, 0
            for k, p in enumerate(parts[:-1]):
                acc += len(p) + 1
                if acc >= half:
                    break
            t = "-".join(parts[:k + 1]) + "-\\N" + "-".join(parts[k + 1:])
        fs = "" if (len(txt) <= a.max_chars or "\\N" in t) else "{\\fs%d}" % max(round(size * 0.63), round(size * a.max_chars / len(txt)))
        ass.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\pos({W // 2},{round(H * a.y)})\\fad(40,0)}}{fs}{t}")
    with open(os.path.join(a.out_dir, "captions.ass"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(ass) + "\n")

    def srt_ts(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    lines, n, order = [], 1, []
    for x in G:
        if x["sent"] not in order:
            order.append(x["sent"])
    for s in order:
        ws = [x for x in G if x["sent"] == s]
        groups, cur2 = [], []
        for x in ws:
            if cur2 and len(" ".join(y["w"] for y in cur2 + [x])) > 42:
                groups.append(cur2)
                cur2 = []
            cur2.append(x)
        groups.append(cur2)
        for g in groups:
            lines.append(f"{n}\n{srt_ts(g[0]['start'])} --> {srt_ts(g[-1]['end'] + 0.1)}\n{' '.join(y['w'] for y in g)}\n")
            n += 1
    with open(os.path.join(a.out_dir, "subtitles.srt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"{len(events)} caption chunks -> {a.out_dir}/captions.ass, subtitles.srt  (font {a.font} {size}px at y={a.y})")
    print(" | ".join(e[2] for e in events[:40]) + (" ..." if len(events) > 40 else ""))


if __name__ == "__main__":
    main()
