#!/usr/bin/env python3
"""Per-frame geometry of a static white label (white in the Swedish frame, different from the base) plus its ink
lines in one reference frame.   usage: measure_box.py KEY T0 T1 x0,y0,x1,y1 [--base clean/KEY_clean.mp4]"""
import subprocess, sys, json
import numpy as np, cv2
k, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
x0, y0, x1, y1 = [int(v) for v in sys.argv[4].split(",")]
base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else f"orig/{k}.mp4"
o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                               "-of", "json", f"vid/{k}.mp4"], capture_output=True, text=True).stdout)["streams"][0]
W, H = o["width"], o["height"]
def frames(p):
    b = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(t0), "-i", p, "-t", str(t1 - t0), "-f", "rawvideo",
                        "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.uint8).reshape(-1, H, W, 3)
S, B = frames(f"vid/{k}.mp4"), frames(base)
rows = []
for i in range(min(len(S), len(B))):
    s, b = S[i][y0:y1, x0:x1], B[i][y0:y1, x0:x1]
    d = np.abs(s.astype(int) - b.astype(int)).max(2) > 40
    g = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
    wm = ((g > 225) & d).astype(np.uint8)
    wm = cv2.morphologyEx(wm, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(wm)
    if n < 2: rows.append(None); continue
    j = max(range(1, n), key=lambda j: st[j][4])
    x, y, w, h, a = st[j]
    rows.append((i, x0 + x, y0 + y, w, h, a) if a > 4000 else None)
on = [r for r in rows if r]
print("frames with box", len(on), "of", len(rows), "first", on[0][0] if on else None, "last", on[-1][0] if on else None)
if on:
    print("t", round(t0 + on[0][0] / 30, 3), "-", round(t0 + (on[-1][0] + 1) / 30, 3))
    for q, nm in zip(range(1, 5), "x y w h".split()):
        v = [r[q] for r in on]; print(nm, min(v), int(np.median(v)), max(v))
    r = on[len(on) // 2]; i, x, y, w, h, _ = r
    g = cv2.cvtColor(S[i], cv2.COLOR_BGR2GRAY)[y + 6:y + h - 6, x + 6:x + w - 6]
    dark = g < 110
    rr = np.where(dark.sum(1) > 0)[0]
    bands, cur = [], [rr[0]]
    for v in rr[1:]:
        if v - cur[-1] > 3: bands.append(cur); cur = [v]
        else: cur.append(v)
    bands.append(cur)
    for bd in bands:
        cols = np.where(dark[bd[0]:bd[-1] + 1].any(0))[0]
        print("ink line y", y + 6 + bd[0], y + 6 + bd[-1], "x", x + 6 + cols[0], x + 6 + cols[-1])
    cv2.imwrite(f"qa/{k}_box_{t0}.png", S[i][y - 10:y + h + 10, x - 10:x + w + 10])
