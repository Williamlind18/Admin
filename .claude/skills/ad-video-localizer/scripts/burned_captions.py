#!/usr/bin/env python3
"""Read and remove burned-in captions of the common TikTok style: a white (rounded) box with dark text.

  burned_captions.py detect SRC.mp4 OUT_DIR
      [--box-h 55]  Finds the caption box in every frame (box shape where it stands out from the footage, black
      glyphs on white where the box merges with a bright background), writes OUT_DIR/boxes.json,
      OUT_DIR/segments.json and contact sheets OUT_DIR/captions_N.png: one crop per caption with its
      start time, so the original script and its timing can be read with the Read tool.
  burned_captions.py remove SRC.mp4 OUT_DIR/boxes.json CLEAN.mp4 [--manual 85.0-87.0:x,y,w,h]
                     [--only 3,14,30]
      Masks each frame's box (plus the neighbouring frames' boxes, and holds a box through short
      detection drop-outs), inpaints it (Telea) and blurs the patch with a feathered edge, so a soft
      smudge is left instead of text. Put the new captions over the same spot. --manual adds a box
      for a stretch the detector missed (check segments.json for gaps while a caption is on screen);
      --only writes before/after PNGs for those times instead of a video.

Needs opencv-python-headless (pip). Captions in other styles (no box, coloured text) need other
thresholds. The result is a smudge, not a perfect reconstruction; the paid Vmake subtitle removal
(vmake-skill, ask first) is the cleaner option.
"""
import argparse
import json
import os
import sys

import numpy as np

try:
    import cv2
except ImportError:
    raise SystemExit("pip install opencv-python-headless")
import imageio_ffmpeg
from PIL import Image, ImageDraw


def frames(src):
    rd = imageio_ffmpeg.read_frames(src, pix_fmt="rgb24")
    meta = next(rd)
    return rd, meta["size"], meta["fps"]


def by_box(img, W, bh):
    white = (img.min(axis=2) >= 243).astype(np.uint8)
    closed = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(closed, 8)
    best = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if not (0.8 * bh <= h <= 1.2 * bh and 70 <= w <= 700) or area / float(w * h) < 0.85:
            continue
        dark = (img[y:y + h, x:x + w].max(axis=2) < 90).mean()
        if not (0.04 <= dark <= 0.45) or abs(x + w / 2 - W / 2) > 40:
            continue
        best.append((int(x), int(y), int(w), int(h)))
    return best


def by_text(img, W, bh):
    dark = (img.max(axis=2) < 80).astype(np.uint8)
    near = cv2.dilate((img.min(axis=2) >= 235).astype(np.uint8), np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(dark & near, cv2.MORPH_CLOSE, np.ones((3, 19), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(m, 8)
    best = []
    for i in range(1, n):
        x, y, w, h, _ = st[i]
        if not (14 <= h <= min(34, bh - 6) and w >= 40) or abs(x + w / 2 - W / 2) > 45:
            continue
        bx, by, bw = x - 16, y + h // 2 - bh // 2, w + 32
        if bx < 0 or by < 0 or by + bh > img.shape[0]:
            continue
        reg = img[by:by + bh, bx:bx + bw]
        txt = cv2.dilate((reg.max(axis=2) < 140).astype(np.uint8), np.ones((3, 3), np.uint8))
        if not (txt == 0).any() or (reg.min(axis=2) >= 225)[txt == 0].mean() < 0.85:
            continue
        best.append((int(bx), int(by), int(bw), int(bh)))
    return best


def pick(img, W, bh, row):
    """The caption box in one frame. A graphic (e.g. a white badge) can look like a caption box, so a
    candidate on the usual caption row wins; otherwise the box-shape match, then the text match, as before."""
    boxes, texts = by_box(img, W, bh), None
    if row is not None:
        near = [b for b in boxes if abs(b[1] + b[3] / 2 - row) <= 1.5 * bh]
        if not near:
            texts = by_text(img, W, bh)
            near = [b for b in texts if abs(b[1] + b[3] / 2 - row) <= 1.5 * bh]
        if near:
            return max(near, key=lambda b: b[2] * b[3])
    if boxes:
        return max(boxes, key=lambda b: b[2] * b[3])
    texts = by_text(img, W, bh) if texts is None else texts
    return max(texts, key=lambda b: b[2]) if texts else None


def detect(a):
    os.makedirs(a.out_dir, exist_ok=True)
    rd, (W, H), fps = frames(a.src)
    Y0, Y1 = int(H * 0.35), int(H * 0.92)
    # the usual caption row, from a quick pass over every 15th frame
    centres = []
    for k, fr in enumerate(rd):
        if k % 15 == 0:
            b = pick(np.frombuffer(fr, np.uint8).reshape(H, W, 3)[Y0:Y1], W, a.box_h, None)
            if b:
                centres.append(b[1] + b[3] / 2)
    row = float(np.median(centres)) if centres else None
    rd, _, _ = frames(a.src)
    rows, sigs, crops = [], {}, {}
    for k, fr in enumerate(rd):
        full = np.frombuffer(fr, np.uint8).reshape(H, W, 3)
        img = full[Y0:Y1]
        b = pick(img, W, a.box_h, row)
        if b:
            x, y, w, h = b[0], b[1] + Y0, b[2], b[3]
            b = [x, y, w, h]
            reg = full[y + 4:y + h - 4, x + 6:x + w - 6]
            sigs[k] = cv2.resize((reg.max(axis=2) < 110).astype(np.float32), (96, 10), interpolation=cv2.INTER_AREA)
            crops[k] = full[max(0, y - 4):y + h + 4, max(0, x - 4):x + w + 4].copy()
        rows.append([k, b])
    json.dump({"fps": fps, "W": W, "H": H, "frames": rows}, open(os.path.join(a.out_dir, "boxes.json"), "w"))

    box = dict((k, b) for k, b in rows if b)
    segs = []
    for k in sorted(box):
        b = box[k]
        for s in reversed(segs[-3:]):
            r = box[s["ref"]]
            if k - s["last"] <= 10 and abs(b[0] - r[0]) <= 12 and abs(b[2] - r[2]) <= 24 \
                    and abs(b[1] + b[3] / 2 - r[1] - r[3] / 2) <= 10 and np.abs(sigs[k] - sigs[s["ref"]]).mean() < 0.05:
                s["last"] = k; s["frames"].append(k)
                break
        else:
            segs.append({"first": k, "last": k, "ref": k, "frames": [k]})
    segs = [s for s in segs if len(s["frames"]) >= 4]
    out = [{"t0": round(s["first"] / fps, 2), "t1": round((s["last"] + 1) / fps, 2), "box": box[s["ref"]]} for s in segs]
    json.dump(out, open(os.path.join(a.out_dir, "segments.json"), "w"), indent=1)
    rowh, per = 70, 24
    for p in range(0, len(segs), per):
        part = segs[p:p + per]
        im = Image.new("RGB", (720, rowh * len(part)), "gray")
        dr = ImageDraw.Draw(im)
        for i, s in enumerate(part):
            c = Image.fromarray(crops[s["frames"][len(s["frames"]) // 2]])
            c.thumbnail((600, 64))
            im.paste(c, (110, i * rowh + 3))
            dr.text((4, i * rowh + 25), f"{p + i:03d} {s['first'] / fps:.2f}", fill="yellow")
        im.save(os.path.join(a.out_dir, f"captions_{p // per}.png"))
    nobox = [k for k, b in rows if not b]
    print(f"{len(rows)} frames, {len(rows) - len(nobox)} with a caption box, {len(out)} caption segments")
    print("sheets:", ", ".join(f"captions_{i}.png" for i in range((len(segs) + per - 1) // per)))
    runs, cur = [], None
    for k in nobox:
        if cur and k == cur[1] + 1:
            cur[1] = k
        else:
            cur = [k, k]; runs.append(cur)
    for r in runs:
        if r[1] - r[0] >= 15:
            print(f"no box {r[0] / fps:.2f}-{(r[1] + 1) / fps:.2f} s: check whether a caption is on screen there (--manual)")


def remove(a):
    D = json.load(open(a.boxes)); fps, W, H = D["fps"], D["W"], D["H"]
    det = [b for _, b in D["frames"]]
    N = len(det)

    def sim(p, q):
        return p and q and abs(p[0] - q[0]) <= 14 and abs(p[2] - q[2]) <= 28 and abs(p[1] - q[1]) <= 12

    boxes = [[] for _ in range(N)]
    for k in range(N):
        boxes[k] += [det[j] for j in (k - 1, k, k + 1) if 0 <= j < N and det[j]]
        if det[k] is None:
            p = next((det[j] for j in range(k - 1, max(-1, k - 16), -1) if det[j]), None)
            q = next((det[j] for j in range(k + 1, min(N, k + 16)) if det[j]), None)
            if sim(p, q):
                boxes[k] += [p, q]
    for m in a.manual:
        rng, bx = m.split(":")
        t0, t1 = (float(x) for x in rng.split("-"))
        b = [int(x) for x in bx.split(",")]
        for k in range(max(0, int(round(t0 * fps)) - 1), min(N, int(round(t1 * fps)) + 1)):
            boxes[k].append(b)

    def clean(img, bl):
        if not bl:
            return img
        mask = np.zeros((H, W), np.uint8)
        for x, y, w, h in bl:
            cv2.rectangle(mask, (x - a.pad, y - a.pad), (x + w + a.pad, y + h + a.pad), 255, -1)
        ys, xs = np.where(mask > 0)
        y0, y1, x0, x1 = max(0, ys.min() - 40), min(H, ys.max() + 40), max(0, xs.min() - 40), min(W, xs.max() + 40)
        roi, mroi = img[y0:y1, x0:x1].copy(), mask[y0:y1, x0:x1]
        blur = cv2.GaussianBlur(cv2.inpaint(roi, mroi, 7, cv2.INPAINT_TELEA), (0, 0), 7)
        fe = cv2.GaussianBlur(cv2.dilate(mroi, np.ones((9, 9), np.uint8)).astype(np.float32) / 255.0, (0, 0), 4)[..., None]
        res = img.copy()
        res[y0:y1, x0:x1] = (blur * fe + roi * (1 - fe)).astype(np.uint8)
        return res

    rd, _, _ = frames(a.src)
    if a.only:
        want = {int(round(float(t) * fps)): t for t in a.only.split(",")}
        base = os.path.splitext(a.out)[0]
        for k, fr in enumerate(rd):
            if k in want:
                img = np.frombuffer(fr, np.uint8).reshape(H, W, 3)
                Image.fromarray(img).save(f"{base}_{want[k]}_before.png")
                Image.fromarray(clean(img, boxes[k])).save(f"{base}_{want[k]}_after.png")
            if k >= max(want):
                break
        return
    wr = imageio_ffmpeg.write_frames(a.out, (W, H), fps=fps, codec="libx264", pix_fmt_in="rgb24", macro_block_size=1,
                                     output_params=["-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p"])
    wr.send(None)
    for k, fr in enumerate(rd):
        img = np.frombuffer(fr, np.uint8).reshape(H, W, 3)
        wr.send(np.ascontiguousarray(clean(img, boxes[k] if k < N else [])))
    wr.close()
    print("wrote", a.out, "(no audio: render.py adds the new voice)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("detect"); d.add_argument("src"); d.add_argument("out_dir")
    d.add_argument("--box-h", type=int, default=55, help="caption box height in pixels (measure one frame)")
    r = sub.add_parser("remove"); r.add_argument("src"); r.add_argument("boxes"); r.add_argument("out")
    r.add_argument("--manual", action="append", default=[], help="T0-T1:x,y,w,h")
    r.add_argument("--only", help="comma-separated times: write before/after PNGs instead of a video")
    r.add_argument("--pad", type=int, default=4)
    a = ap.parse_args()
    detect(a) if a.cmd == "detect" else remove(a)


if __name__ == "__main__":
    main()
