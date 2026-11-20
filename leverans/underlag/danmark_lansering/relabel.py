#!/usr/bin/env python3
"""Rebuild one Swedish white label in another language, frame by frame, from the diff between the Swedish
delivery (vid/KEY.mp4) and the text-free original (orig/KEY.mp4).

usage: relabel.py KEY NAME T0 T1 --sv "15 000|NÖJDA KUNDER" --da "15.000|TILFREDSE KUNDER"
                  [--roi x0,y0,x1,y1] [--ref T] [--radius 0.12]
Writes ov/KEY/NAME/%04d.png (one per video frame from the first frame with a label) and appends the item to
ov/KEY/spec.json. Per frame: the label is the largest diff component inside the ROI (minAreaRect gives centre,
size and angle). The text layout comes from the reference frame: each Swedish line's ink box in label
coordinates sets the Danish line's size (same ink height) and centre."""
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


def ink_h(text, size):
    f = ImageFont.truetype(FONT, size)
    l, t, r, b = f.getbbox(text)
    return b - t, r - l, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key"); ap.add_argument("name"); ap.add_argument("t0", type=float); ap.add_argument("t1", type=float)
    ap.add_argument("--sv", required=True); ap.add_argument("--da", required=True)
    ap.add_argument("--roi"); ap.add_argument("--ref", type=float); ap.add_argument("--radius", type=float, default=0.12)
    ap.add_argument("--min-area", type=float, default=0.004)
    ap.add_argument("--base", help="text-free video on the Swedish timeline (default orig/KEY.mp4)")
    a = ap.parse_args()
    k = a.key
    W, H, fps = probe(f"vid/{k}.mp4")
    roi = [int(v) for v in a.roi.split(",")] if a.roi else [0, 0, W, H]
    geo, svf = [], []
    for i, (s, o) in enumerate(zip(frames(f"vid/{k}.mp4", a.t0, a.t1, W, H), frames(a.base or f"orig/{k}.mp4", a.t0, a.t1, W, H))):
        d = (np.abs(s.astype(int) - o.astype(int)).max(2) > 40).astype(np.uint8)
        d = cv2.dilate(d, np.ones((9, 9), np.uint8))
        hsv = cv2.cvtColor(s, cv2.COLOR_BGR2HSV)
        white = ((hsv[:, :, 2] > 200) & (hsv[:, :, 1] < 45)).astype(np.uint8)
        d = d & white   # the label is white and differs from the original
        m = np.zeros_like(d); x0, y0, x1, y1 = roi; m[y0:y1, x0:x1] = 1; d *= m
        d = cv2.morphologyEx(d, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(d)
        best = max(range(1, n), key=lambda j: st[j][4], default=None)
        t = a.t0 + i / fps
        if best is None or st[best][4] < a.min_area * W * H:
            geo.append(None); svf.append(None); continue
        ys, xs = np.where(lab == best)
        (cx, cy), (bw, bh), ang = cv2.minAreaRect(np.stack([xs, ys], 1).astype(np.float32))
        if bw < bh:
            bw, bh, ang = bh, bw, ang + 90
        if ang > 45:
            ang -= 180
        geo.append(dict(t=t, cx=cx, cy=cy, w=bw, h=bh, ang=ang)); svf.append(s if a.ref is None or abs(t - a.ref) < 0.6 / fps else None)
    idx = [i for i, g in enumerate(geo) if g]
    if not idx:
        raise SystemExit("no label found")
    first, last = idx[0], idx[-1]
    # reference frame: given, or the middle of the run
    ri = min(idx, key=lambda i: abs(geo[i]["t"] - a.ref)) if a.ref is not None else idx[len(idx) // 2]
    if svf[ri] is None:
        svf[ri] = next(frames(f"vid/{k}.mp4", geo[ri]["t"], geo[ri]["t"] + 1 / fps, W, H))
    g = geo[ri]
    M = cv2.getRotationMatrix2D((g["cx"], g["cy"]), g["ang"], 1.0)
    rot = cv2.warpAffine(cv2.cvtColor(svf[ri], cv2.COLOR_BGR2GRAY), M, (W, H), borderValue=255)
    bx0, by0 = int(g["cx"] - g["w"] / 2 + 4), int(g["cy"] - g["h"] / 2 + 4)
    box = rot[by0:int(g["cy"] + g["h"] / 2 - 4), bx0:int(g["cx"] + g["w"] / 2 - 4)]
    dark = box < 100
    rows = np.where(dark.sum(1) > 0)[0]
    bands, cur = [], [rows[0]]
    for r in rows[1:]:
        if r - cur[-1] > 2:
            bands.append(cur); cur = [r]
        else:
            cur.append(r)
    bands.append(cur)
    sv_lines, da_lines = a.sv.split("|"), a.da.split("|")
    # merge accent rows (small bands right above a line) into the following line
    merged = []
    for i, b in enumerate(bands):
        if merged and len(merged[-1]) < 0.5 * len(b) and b[0] - merged[-1][-1] < 0.8 * len(b):
            merged[-1] = merged[-1] + list(range(merged[-1][-1] + 1, b[0])) + b
        else:
            merged.append(b)
    bands = merged
    if len(bands) != len(sv_lines):
        print("warning: found", len(bands), "ink lines for", len(sv_lines), "Swedish lines")
    layout = []
    for b, svt, dat in zip(bands, sv_lines, da_lines):
        cols = np.where(dark[b[0]:b[-1] + 1].any(0))[0]
        h_ink = b[-1] - b[0] + 1
        hh, ww, _ = ink_h(svt, 100)
        size = 100 * h_ink / hh
        wsv = cols[-1] - cols[0] + 1
        size_w = 100 * wsv / ww       # the width gives a second estimate (robust to accents)
        size = min(size, size_w) if abs(size - size_w) / size_w > 0.12 else (size + size_w) / 2
        cxl = (bx0 + (cols[0] + cols[-1]) / 2) - g["cx"]
        cyl = (by0 + (b[0] + b[-1]) / 2) - g["cy"]
        layout.append(dict(text=dat, size=size, dx=cxl / g["w"], dy=cyl / g["h"]))
    # Danish lines must fit inside the label
    for L in layout:
        while ink_h(L["text"], int(L["size"]))[1] > 0.9 * g["w"]:
            L["size"] *= 0.97
    print("layout", [(L["text"], round(L["size"], 1), round(L["dx"], 3), round(L["dy"], 3)) for L in layout])
    out = os.path.join("ov", k, a.name)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    # smooth geometry over 5 frames (fill short gaps by holding the last value)
    seq = geo[first:last + 1]
    for i in range(len(seq)):
        if seq[i] is None:
            seq[i] = dict(seq[i - 1])
    arr = {q: np.array([s[q] for s in seq]) for q in ("cx", "cy", "w", "h", "ang")}
    if len(seq) >= 5:
        for q in arr:
            arr[q] = np.convolve(np.pad(arr[q], 2, mode="edge"), np.ones(5) / 5, mode="valid")
    for i in range(len(seq)):
        w, h = arr["w"][i] + 2, arr["h"][i] + 2
        sc = w / g["w"]
        lab = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
        d = ImageDraw.Draw(lab)
        d.rounded_rectangle((0, 0, w - 1, h - 1), a.radius * min(w, h), fill=(255, 255, 255, 255))
        for L in layout:
            f = ImageFont.truetype(FONT, max(8, int(round(L["size"] * sc))))
            l, t, r, b = f.getbbox(L["text"])
            x = w / 2 + L["dx"] * w - (l + r) / 2
            y = h / 2 + L["dy"] * h - (t + b) / 2
            d.text((x, y), L["text"], font=f, fill=(0, 0, 0, 255))
        rotd = lab.rotate(-arr["ang"][i], resample=Image.BICUBIC, expand=True)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.alpha_composite(rotd, (int(round(arr["cx"][i] - rotd.size[0] / 2)), int(round(arr["cy"][i] - rotd.size[1] / 2))))
        img.save(os.path.join(out, f"{i:04d}.png"))
    sp = os.path.join("ov", k, "spec.json")
    spec = json.load(open(sp)) if os.path.exists(sp) else dict(items=[])
    spec["items"] = [it for it in spec["items"] if not it.get("pattern", "").startswith(out + "/")]
    t0 = seq[0]["t"]
    spec["items"].append(dict(kind="seq", pattern=f"{out}/%04d.png", n=len(seq), t0=round(t0, 3),
                              t1=round(t0 + len(seq) / fps, 3)))
    json.dump(spec, open(sp, "w"), indent=1)
    print(k, a.name, "frames", len(seq), "from", round(t0, 3), "to", round(t0 + len(seq) / fps, 3))


if __name__ == "__main__":
    main()
