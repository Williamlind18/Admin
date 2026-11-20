#!/usr/bin/env python3
"""Frame-index map Swedish delivery -> original (tiny grey thumbnails, caption band masked).
usage: framemap.py KEY [win]   prints runs where the best match is not the same frame, and saves work/KEY_framemap.json"""
import json, subprocess, sys
import numpy as np
k = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 90
def thumbs(p):
    b = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-vf", "scale=36:64,format=gray", "-f", "rawvideo", "-"],
                       capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, 64, 36).astype(np.float32).copy()
    a[:, 44:52] = 0
    return a
o, s = thumbs(f"orig/{k}.mp4"), thumbs(f"vid/{k}.mp4")
res = []
for i, f in enumerate(s):
    lo, hi = max(0, i - win), min(len(o), i + win + 1)
    d = np.abs(o[lo:hi] - f).mean((1, 2))
    j = lo + int(d.argmin())
    same = float(np.abs(o[min(i, len(o) - 1)] - f).mean())
    res.append((i, j, round(float(d.min()), 2), round(same, 2)))
json.dump(res, open(f"work/{k}_framemap.json", "w"))
print("frames sv", len(s), "orig", len(o))
cur = None
for i, j, d, same in res:
    bad = j != i and same > 1.5 or d > 3
    if bad and cur is None: cur = [i, i]
    elif bad: cur[1] = i
    elif cur: print(f"run {cur[0]}-{cur[1]} ({cur[0]/30:.2f}-{(cur[1]+1)/30:.2f}s)"); cur = None
if cur: print(f"run {cur[0]}-{cur[1]}")
