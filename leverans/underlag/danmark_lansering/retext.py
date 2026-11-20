#!/usr/bin/env python3
"""Swap the words on a moving Swedish label: show the Swedish label region from the Swedish delivery (src crop)
and paint the new words over its text, frame by frame. For labels whose white box blends into a white object.

usage: retext.py KEY NAME T0 T1 --sv "FRI FRAKT" --da "FRI FRAGT" --roi x0,y0,x1,y1
The ROI must not touch the caption band; it is copied from vid/KEY.mp4 for T0-T1 (kind "src" in the spec)."""
import argparse
import json
import os
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT = os.path.join(S, "v22it", "fonts", "Montserrat-ExtraBold.ttf")


def probe(p):
    o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate", "-of", "json", p],
                                  capture_output=True, text=True).stdout)["streams"][0]
    a, b = o["r_frame_rate"].split("/")
    return o["width"], o["height"], float(a) / float(b)


def frames(p, t0, t1, W, H):
    pr = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t0:.3f}", "-i", p, "-t", f"{t1 - t0:.3f}",
                           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key"); ap.add_argument("name"); ap.add_argument("t0", type=float); ap.add_argument("t1", type=float)
    ap.add_argument("--sv", required=True); ap.add_argument("--da", required=True); ap.add_argument("--roi", required=True)
    a = ap.parse_args()
    k = a.key
    W, H, fps = probe(f"vid/{k}.mp4")
    x0, y0, x1, y1 = [int(v) for v in a.roi.split(",")]
    f100 = ImageFont.truetype(FONT, 100)
    l, t, r, b = f100.getbbox(a.sv)
    sv_h100, sv_w100 = b - t, r - l
    geo = []
    for i, (s, o) in enumerate(zip(frames(f"vid/{k}.mp4", a.t0, a.t1, W, H), frames(f"orig/{k}.mp4", a.t0, a.t1, W, H))):
        g = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY).astype(int)
        go = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY).astype(int)
        ink = ((g < 70) & (go - g > 60)).astype(np.uint8)   # dark in the Swedish frame, not dark in the original
        m = np.zeros_like(ink); m[y0:y1, x0:x1] = 1; ink *= m
        ink = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.morphologyEx(ink, cv2.MORPH_CLOSE, np.ones((9, 25), np.uint8)))
        keep = [j for j in range(1, n) if st[j][4] >= 150]   # every word of the label, not just the biggest
        if not keep or sum(st[j][4] for j in keep) < 400:
            geo.append(None); continue
        ys, xs = np.where(np.isin(lab, keep))
        (cx, cy), (bw, bh), ang = cv2.minAreaRect(np.stack([xs, ys], 1).astype(np.float32))
        if bw < bh:
            bw, bh, ang = bh, bw, ang + 90
        if ang > 45:
            ang -= 180
        geo.append([cx, cy, bw, bh, ang])
    idx = [i for i, gg in enumerate(geo) if gg]
    first, last = idx[0], idx[-1]
    seq = geo[first:last + 1]
    for i in range(len(seq)):
        if seq[i] is None:
            seq[i] = list(seq[i - 1])
    arr = np.array(seq)
    if len(arr) >= 5:
        for c in range(5):
            arr[:, c] = np.convolve(np.pad(arr[:, c], 2, mode="edge"), np.ones(5) / 5, mode="valid")
    out = os.path.join("ov", k, a.name)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    for i, (cx, cy, bw, bh, ang) in enumerate(arr):
        size = 100 * min(bh / sv_h100, bw / sv_w100)    # same ink height (and width) as the Swedish words
        f = ImageFont.truetype(FONT, max(8, int(round(size))))
        l, t, r, b = f.getbbox(a.da)
        pw, ph = max(bw, r - l) + 0.5 * bh, bh * 1.6
        lab = Image.new("RGBA", (int(pw), int(ph)), (0, 0, 0, 0))
        d = ImageDraw.Draw(lab)
        d.rectangle((0, 0, pw, ph), fill=(255, 255, 255, 255))
        d.text((pw / 2 - (l + r) / 2, ph / 2 - (t + b) / 2), a.da, font=f, fill=(0, 0, 0, 255))
        rot = lab.rotate(-ang, resample=Image.BICUBIC, expand=True)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.alpha_composite(rot, (int(round(cx - rot.size[0] / 2)), int(round(cy - rot.size[1] / 2))))
        img.save(os.path.join(out, f"{i:04d}.png"))
    sp = os.path.join("ov", k, "spec.json")
    spec = json.load(open(sp)) if os.path.exists(sp) else dict(items=[])
    spec["items"] = [it for it in spec["items"] if not it.get("pattern", "").startswith(out + "/")
                     and it.get("name") != a.name]
    t0 = a.t0 + first / fps
    t1 = t0 + len(arr) / fps
    spec["items"].append(dict(kind="src", name=a.name, box=[x0, y0, x1, y1], t0=round(t0, 3), t1=round(t1, 3)))
    spec["items"].append(dict(kind="seq", pattern=f"{out}/%04d.png", n=len(arr), t0=round(t0, 3), t1=round(t1, 3)))
    json.dump(spec, open(sp, "w"), indent=1)
    print(k, a.name, "frames", len(arr), "from", round(t0, 3), "to", round(t1, 3), "size", round(size, 1))


if __name__ == "__main__":
    main()
