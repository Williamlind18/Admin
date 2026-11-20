#!/usr/bin/env python3
"""Map every frame of an edited video to its best-matching frame in a source (tiny grey thumbnails, L2 via BLAS).
usage: globalmap.py EDIT.mp4 SOURCE.mp4 OUT.json [--mask y0,y1]  (mask = caption band as fractions of height)"""
import json, subprocess, sys
import numpy as np
E, SRC, OUT = sys.argv[1:4]
mask = (0.62, 0.86)
if "--mask" in sys.argv:
    mask = tuple(float(x) for x in sys.argv[sys.argv.index("--mask") + 1].split(","))
TW, TH = 24, 42
def thumbs(p):
    b = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", p, "-vf", f"fps=30,scale={TW}:{TH},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, TH, TW).astype(np.float32).copy()
    a[:, int(mask[0] * TH):int(mask[1] * TH)] = 0
    return a.reshape(len(a), -1)
e, s = thumbs(E), thumbs(SRC)
e2 = (e ** 2).sum(1)[:, None]; s2 = (s ** 2).sum(1)[None, :]
best, dist = [], []
for i0 in range(0, len(e), 500):
    d = e2[i0:i0 + 500] + s2 - 2 * e[i0:i0 + 500] @ s.T
    j = d.argmin(1)
    best += j.tolist(); dist += np.sqrt(np.maximum(d[np.arange(len(j)), j], 0) / e.shape[1]).tolist()
json.dump({"src": best, "dist": [round(x, 2) for x in dist], "n_edit": len(e), "n_src": len(s)}, open(OUT, "w"))
print("edit", len(e), "src", len(s))
