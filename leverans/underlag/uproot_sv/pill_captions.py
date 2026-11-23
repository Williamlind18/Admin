#!/usr/bin/env python3
"""Convert a captions.ass (chunk timings) into Uproot-style pills: black Montserrat ExtraBold in white rounded boxes,
placed at the height of the original pill at that time. usage: pill_captions.py IN.ass OUT.ass DETECT1.json[,DETECT2.json] FPS DEFAULT_Y [SIZE]"""
import json, re, sys, statistics
from PIL import ImageFont
FONT = "/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/v22it/fonts/Montserrat-ExtraBold.ttf"
inp, outp, dets, fps, ydef = sys.argv[1], sys.argv[2], sys.argv[3].split(","), float(sys.argv[4]), int(sys.argv[5])
SIZE = int(sys.argv[6]) if len(sys.argv) > 6 and not sys.argv[6].startswith("--") else 31
IGN = [float(v) for v in sys.argv[sys.argv.index("--ignore") + 1].split("-")] if "--ignore" in sys.argv else None
pf = ImageFont.truetype(FONT, round(SIZE * 0.8205))
ycent = {}
for d in dets:
    for k, rs in json.load(open(d)).items():
        for x0, y0, x1, y1 in rs:
            c = (y0 + y1) / 2
            if IGN and IGN[0] <= c <= IGN[1]: continue
            ycent.setdefault(int(k), []).append(c)
def t(s):
    h, m, x = s.split(":"); return int(h) * 3600 + int(m) * 60 + float(x)
def ts(v): return f"{int(v // 3600)}:{int(v % 3600 // 60):02d}:{v % 60:05.2f}"
L = open(inp, encoding="utf-8").read().splitlines()
hdr = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 720", "PlayResY: 1280", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
       "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, "
       "StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       f"Style: Pill,Montserrat ExtraBold,{SIZE},&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,1,0,0,5,10,10,0,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
ev = []
for l in L:
    if not l.startswith("Dialogue"): continue
    parts = l.split(",", 9); a, b = t(parts[1]), t(parts[2])
    txt = re.sub(r"\{[^}]*\}", "", parts[9]).replace("\\N", "").strip()
    fr = [ycent[f] for f in range(int(a * fps), int(b * fps) + 1) if f in ycent]
    ys = [y for lst in fr for y in lst]
    y = int(statistics.median(ys)) if ys else ydef
    if abs(y - ydef) < 25: y = ydef
    w = pf.getlength(txt); pw, ph, r = int(w + 30), int(SIZE * 1.42), 11
    x0, y0 = 360 - pw // 2, y - ph // 2
    path = (f"m {r} 0 l {pw - r} 0 b {pw} 0 {pw} 0 {pw} {r} l {pw} {ph - r} b {pw} {ph} {pw} {ph} {pw - r} {ph} "
            f"l {r} {ph} b 0 {ph} 0 {ph} 0 {ph - r} l 0 {r} b 0 0 0 0 {r} 0")
    ev.append(f"Dialogue: 0,{ts(a)},{ts(b)},Pill,,0,0,0,,{{\\an7\\pos({x0},{y0})\\p1\\1c&HFFFFFF&\\bord0\\shad0}}{path}")
    ev.append(f"Dialogue: 1,{ts(a)},{ts(b)},Pill,,0,0,0,,{{\\an5\\pos(360,{y + 1})}}{txt}")
open(outp, "w", encoding="utf-8").write("\n".join(hdr + ev) + "\n")
print(outp, len(ev) // 2, "pills")
