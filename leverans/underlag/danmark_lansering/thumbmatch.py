#!/usr/bin/env python3
"""Find where frames of the Swedish delivery (A..B s) come from in the original: tiny grey thumbnails, the caption
band masked out.  usage: thumbmatch.py KEY A B [step]"""
import subprocess, sys
import numpy as np
k, A, B = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.25
def thumbs(p, ss=None, t=None, fps=None):
    cmd = ["ffmpeg", "-nostdin", "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + ["-i", p] + \
          (["-t", str(t)] if t else []) + ["-vf", (f"fps={fps}," if fps else "") + "scale=36:64,format=gray", "-f", "rawvideo", "-"]
    b = subprocess.run(cmd, capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).reshape(-1, 64, 36).astype(np.float32)
    a[:, 44:52] = 0   # caption band (~0.69-0.81)
    return a
o = thumbs(f"orig/{k}.mp4")
of = 30.0
q = thumbs(f"vid/{k}.mp4", A, B - A, 1 / step)
for i, f in enumerate(q):
    d = np.abs(o - f).mean((1, 2))
    j = int(d.argmin())
    print(f"{A + i * step:7.2f} -> orig {j / of:7.2f}  diff {d[j]:5.1f}   same-time diff {d[min(len(d) - 1, int((A + i * step) * of))]:5.1f}")
