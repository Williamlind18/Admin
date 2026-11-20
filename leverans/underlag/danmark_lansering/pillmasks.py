#!/usr/bin/env python3
"""Masks for one-line caption pills (white rounded box, black text) at a fixed height. A column belongs to the pill
when the pill's padding rows above and below the text are white there; the pill must hold dark text. Works on
bright and busy backgrounds where a white-blob search fails.
usage: pillmasks.py SRC OUT.json TOP0,TOP1 BOT0,BOT1 Y0,Y1     (padding strips and the mask rows, in pixels)"""
import sys, json, subprocess
import numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]
t0, t1 = [int(v) for v in sys.argv[3].split(",")]; b0, b1 = [int(v) for v in sys.argv[4].split(",")]
Y0, Y1 = [int(v) for v in sys.argv[5].split(",")]
o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                               "-of", "json", src], capture_output=True, text=True).stdout)["streams"][0]
W, H = o["width"], o["height"]
pr = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                      stdout=subprocess.PIPE)
res, i = {}, 0
while True:
    b = pr.stdout.read(W * H)
    if len(b) < W * H: break
    g = np.frombuffer(b, np.uint8).reshape(H, W)
    col = (g[t0:t1].min(0) > 215) & (g[b0:b1].min(0) > 215)
    runs, cur = [], None
    for x in range(W):
        if col[x]:
            cur = [x, x] if cur is None or x - cur[1] > 4 else [cur[0], x]
            if cur and (not runs or runs[-1][0] != cur[0]): runs.append(cur)
            runs[-1] = cur
    best = None
    for x0, x1 in runs:
        if x1 - x0 < 50: continue
        mid = g[t1:b0, x0:x1 + 1]
        dark = (mid < 80).mean()
        if 0.04 < dark < 0.5 and (best is None or x1 - x0 > best[1] - best[0]):
            best = (x0, x1)
    if best:
        res[i] = [[max(0, best[0] - 16), Y0, min(W, best[1] + 17), Y1]]
    i += 1
json.dump({str(k): v for k, v in res.items()}, open(out, "w"))
print("frames", i, "with pill", len(res))
