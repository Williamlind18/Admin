#!/usr/bin/env python3
"""Karaoke hook (Maskinrent video 10). Usage: karaoke_hook.py WORK FONTS_DIR OUT.ass GROUPS_JSON
GROUPS_JSON = [[sentence_id, first_word_index, n_words], ...] over words_global.json; append OUT.ass Dialogue lines to captions.ass."""
# Karaoke hook in the original style: white uppercase Montserrat ExtraBold with a black rim, and a red rounded
# box behind the word being spoken. Word positions are measured by rendering each word in a marker colour
# with libass itself, so the boxes line up exactly.
import json, os, subprocess, sys
import numpy as np, imageio_ffmpeg, cv2
WORK, FONTS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
GROUPS = json.loads(sys.argv[4])   # [[sentence_id, first_word_index, n_words], ...] in words_global order
W, H, X, Y, FS = 720, 1280, 360, 398, 62
PADX, BOXH, R = 20, 74, 14
ff = imageio_ffmpeg.get_ffmpeg_exe()
G = json.load(open(os.path.join(WORK, "words_global.json")))
by = {}
for w in G: by.setdefault(w["sent"], []).append(w)
HEAD = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 720\nPlayResY: 1280\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n"
        "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, "
        "Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        f"MarginR, MarginV, Encoding\nStyle: H,Montserrat ExtraBold,{FS},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,"
        "100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
def measure(words, k):
    txt = " ".join(("{\\1c&H0000FF&}" + w + "{\\1c&H000000&}") if i == k else w for i, w in enumerate(words))
    tmp = os.path.join(WORK, "_m.ass")
    open(tmp, "w", encoding="utf-8").write(HEAD + f"Dialogue: 0,0:00:00.00,0:00:01.00,H,,0,0,0,,{{\\pos({X},{Y})\\1c&H000000&}}{txt}\n")
    png = os.path.join(WORK, "_m.png")
    subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", f"color=white:s={W}x{H}:d=1", "-vf",
                    f"ass={tmp}:fontsdir={FONTS}", "-frames:v", "1", png], check=True)
    im = cv2.imread(png)
    red = (im[..., 2] > 200) & (im[..., 1] < 80) & (im[..., 0] < 80)
    xs = np.where(red.any(0))[0]
    return int(xs.min()), int(xs.max())
def ts(t):
    cs = int(round(t * 100)); return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"
lines = []
flat = []
for sid, i0, n in GROUPS:
    flat.append(by[sid][i0:i0 + n])
for gi, grp in enumerate(flat):
    words = [w["w"].upper() for w in grp]
    g_end = flat[gi + 1][0]["start"] - 0.03 if gi + 1 < len(flat) else grp[-1]["end"] + 0.35
    text = " ".join(words)
    for k, w in enumerate(grp):
        x0, x1 = measure(words, k)
        st = grp[0]["start"] - 0.04 if k == 0 else w["start"]
        en = grp[k + 1]["start"] if k + 1 < len(grp) else g_end
        bw, bh = x1 - x0 + 2 * PADX, BOXH
        path = (f"m {R} 0 l {bw - R} 0 b {bw} 0 {bw} 0 {bw} {R} l {bw} {bh - R} b {bw} {bh} {bw} {bh} {bw - R} {bh} "
                f"l {R} {bh} b 0 {bh} 0 {bh} 0 {bh - R} l 0 {R} b 0 0 0 0 {R} 0")
        cx = (x0 + x1) / 2
        lines.append(f"Dialogue: 3,{ts(st)},{ts(en)},Lab,,0,0,0,,{{\\an5\\pos({cx:.1f},{Y})\\bord0\\shad0\\1c&H0100E4&\\p1}}{path}")
        lines.append(f"Dialogue: 4,{ts(st)},{ts(en)},Lab,,0,0,0,,{{\\an5\\pos({X},{Y})\\fnMontserrat ExtraBold\\fs{FS}"
                     f"\\1c&HFFFFFF&\\3c&H000000&\\bord3\\shad2\\4c&H90000000&}}{text}")
open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
for f in ("_m.ass", "_m.png"):
    try: os.remove(os.path.join(WORK, f))
    except FileNotFoundError: pass
print(len(lines) // 2, "word events;", " | ".join(" ".join(w["w"].upper() for w in g) for g in flat))
