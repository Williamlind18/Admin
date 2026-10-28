#!/usr/bin/env python3
"""Remove burned-in text with LaMa inpainting: for each frame, fill the given rectangles
(per-frame masks JSON {frame: [[x0, y0, x1, y1], ...]}, e.g. from ocr_captions.py) from the
surrounding picture, working on a crop around each group of rectangles, and write a clean video.

Setup (once): pip install torch (CPU build is fine), then
  curl -L -o big-lama.pt https://github.com/enesmsahin/simple-lama-inpainting/releases/download/v0.1.0/big-lama.pt
The user must allow running this downloaded model (it is TorchScript, i.e. code).
Speed on the 4-core sandbox: ~0.7 s per frame alone, ~1.8 s with two processes in parallel.
Split long videos with --start/--end and run 2 processes with LAMA_THREADS=2.

Usage: lama_inpaint.py SRC.mp4 masks.json OUT.mp4 --model big-lama.pt [--start F --end F] [--crf 14]
"""
import subprocess, numpy as np, json, sys, torch, time, argparse
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe  # noqa: E402
FF = ffmpeg_exe()
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("masks"); ap.add_argument("out")
ap.add_argument("--model", required=True)
ap.add_argument("--start", type=int, default=0); ap.add_argument("--end", type=int, default=10**9)
ap.add_argument("--crf", default="14")
a = ap.parse_args()
torch.set_num_threads(int(__import__("os").environ.get("LAMA_THREADS", "3")))
model = torch.jit.load(a.model, map_location="cpu").eval()
masks = {int(k): v for k, v in json.load(open(a.masks)).items()}
from common import probe  # noqa: E402
_i = probe(a.src); W, H = _i["width"], _i["height"]
dec = subprocess.Popen([FF, "-loglevel", "error", "-i", a.src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen([FF, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(_i["fps"]),
                        "-i", "-", "-c:v", "libx264", "-crf", a.crf, "-preset", "medium", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
n = W * H * 3
f = 0
t0 = time.time()
done = 0
def inpaint(img, rects):
    ys0 = min(r[1] for r in rects); ys1 = max(r[3] for r in rects)
    # context band: 64 px above/below, multiple of 8
    c0 = max(0, (ys0 - 64) // 8 * 8); c1 = min(H, ((ys1 + 64 + 7) // 8) * 8)
    xs0 = min(r[0] for r in rects); xs1 = max(r[2] for r in rects)
    d0 = max(0, (xs0 - 96) // 8 * 8); d1 = min(W, ((xs1 + 96 + 7) // 8) * 8)
    crop = img[c0:c1, d0:d1]
    m = np.zeros(crop.shape[:2], np.float32)
    for x0, y0, x1, y1 in rects:
        m[max(0, y0 - c0):max(0, y1 - c0), max(0, x0 - d0):max(0, min(W, x1) - d0)] = 1
    with torch.no_grad():
        ti = torch.from_numpy(crop).permute(2, 0, 1)[None].float() / 255
        tm = torch.from_numpy(m)[None, None]
        out = model(ti, tm)[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255
    res = img.copy()
    mm = m[..., None]
    res[c0:c1, d0:d1] = (out * mm + crop * (1 - mm)).astype(np.uint8)
    return res
while True:
    b = dec.stdout.read(n)
    if len(b) < n:
        break
    if f < a.start:
        f += 1; continue
    if f >= a.end:
        break
    img = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    rects = masks.get(f)
    if rects:
        groups = []
        for r in sorted(rects, key=lambda r: r[1]):
            if groups and r[1] - max(q[3] for q in groups[-1]) < 120:
                groups[-1].append(r)
            else:
                groups.append([r])
        for g in groups:
            img = inpaint(img, g)
        done += 1
    enc.stdin.write(img.tobytes())
    f += 1
    if f % 300 == 0:
        print(f"frame {f}  inpainted {done}  {time.time()-t0:.0f}s", flush=True)
enc.stdin.close(); enc.wait()
print("done", f, done, f"{time.time()-t0:.0f}s")
