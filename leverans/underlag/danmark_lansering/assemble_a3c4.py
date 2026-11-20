#!/usr/bin/env python3
"""clean/a3c4_clean.mp4 on the Swedish timeline: the original, with frames 431-536 from the LaMa-cleaned Swedish
replacement shot and 3156-3241 the original's 3156-3210 slowed down (the Swedish edit skips orig 3211-3241)."""
import subprocess
import numpy as np
W, H, N = 1080, 1908, 3611
dec = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", "orig/a3c4.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
seg = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", "work/a3c4_seg1_lama.mp4", "-f", "rawvideo", "-pix_fmt",
                        "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p",
                        "clean/a3c4_clean.mp4"], stdin=subprocess.PIPE)
n = W * H * 3
buf = {}
orig = []
def get(j):
    while len(orig) <= j:
        b = dec.stdout.read(n)
        if len(b) < n:
            return orig_last[0]
        orig_last[0] = b
        if 3150 <= len(orig) <= 3215:
            buf[len(orig)] = b
        orig.append(len(orig))
    return buf.get(j, orig_last[0])
orig_last = [None]
for i in range(N):
    if 431 <= i <= 536:
        get(i)
        out = seg.stdout.read(n)
    elif 3156 <= i <= 3241:
        get(i)
        j = int(round(3156 + (i - 3156) * 54 / 85))
        out = buf[j]
    else:
        out = get(i)
    enc.stdin.write(out)
enc.stdin.close(); enc.wait()
print("done", len(orig))
