#!/usr/bin/env python3
"""Look at a source video before writing the script.

Produces in --out:
  info.json        duration, resolution, fps, audio, scene cuts, audio report
  sheet_NN.png     contact sheets (open them with the Read tool to *see* the video)
  at_<t>.png       single frames for --at times (e.g. to check a key visual)
and prints a summary. With --reference OLD.mp4 it also maps which parts of the
new cut come from where in the old video (useful when the user re-uploads a
trimmed version of a video you already timed).

Usage:
  analyze_video.py VIDEO --out DIR [--every 2] [--at 44.5,90] [--reference OLD.mp4]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import probe, run_ff, to_wav16k, save_json  # noqa: E402

FP_W, FP_H, FP_FPS = 24, 24, 10


def fingerprints(video, out_raw):
    run_ff(["-i", video, "-vf", f"fps={FP_FPS},scale={FP_W}:{FP_H},format=gray", "-f", "rawvideo", out_raw])
    a = np.fromfile(out_raw, np.uint8).reshape(-1, FP_W * FP_H).astype(float)
    os.remove(out_raw)
    return a


def scene_cuts(fp):
    d = np.abs(np.diff(fp, axis=0)).mean(1)
    cuts = []
    for i in range(1, len(d) - 1):
        loc = np.median(d[max(0, i - 10):i + 10])
        if d[i] > 18 and d[i] > 2.5 * loc:
            if not cuts or (i + 1) / FP_FPS - cuts[-1] > 0.25:
                cuts.append(round((i + 1) / FP_FPS, 1))
    return cuts


def map_to_reference(fp_new, fp_old):
    def z(a):
        a = a - a.mean(1, keepdims=True)
        return a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-6)
    C = z(fp_new) @ z(fp_old).T
    best, score = C.argmax(1), C.max(1)
    off = best - np.arange(len(best))
    segs, s = [], 0
    for i in range(1, len(best) + 1):
        if i == len(best) or abs(off[i] - off[s]) > 3 or score[i] < 0.8:
            segs.append([s, i - 1, int(np.median(off[s:i])), float(score[s:i].mean())])
            s = i
    merged = []
    for a, b, of, sc in segs:
        if merged and abs(merged[-1][2] - of) <= 3:
            merged[-1][1] = b
            merged[-1][3] = (merged[-1][3] + sc) / 2
        else:
            merged.append([a, b, of, sc])
    return [{"new_start": a / FP_FPS, "new_end": b / FP_FPS, "old_start": (a + of) / FP_FPS,
             "old_end": (b + of) / FP_FPS, "match": round(sc, 2)} for a, b, of, sc in merged]


def audio_report(video, tmp_wav):
    import librosa
    to_wav16k(video, tmp_wav)
    y, _ = librosa.load(tmp_wav, sr=16000)
    os.remove(tmp_wav)
    w = 800  # 50 ms
    n = len(y) // w
    rms = np.sqrt(np.mean(y[:n * w].reshape(n, w) ** 2, axis=1))
    db = 20 * np.log10(rms + 1e-9)
    blk = 10  # 0.5 s blocks -> quietest 50 ms inside each
    mins = db[:n // blk * blk].reshape(-1, blk).min(1)
    floor = float(np.percentile(mins, 20))
    return {
        "mean_db": round(float(db.mean()), 1),
        "p90_db": round(float(np.percentile(db, 90)), 1),
        "floor_db": round(floor, 1),
        "background_likely": bool(floor > -45),
        "note": ("Audio never gets quiet between words -> music/SFX is mixed under the voice. "
                 "It cannot be separated here; the new video will have voice only unless the user "
                 "supplies the music as a separate file." if floor > -45 else
                 "Quiet gaps between words -> probably voice only."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--out", required=True)
    ap.add_argument("--every", type=float, default=2.0, help="seconds between contact-sheet frames")
    ap.add_argument("--at", default="", help="comma-separated times to export as single frames")
    ap.add_argument("--reference", help="older/longer version of the same video to map against")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    info = probe(a.video)
    cols, rows = 8, 3
    tile_w = 180 if (info["width"] or 0) < (info["height"] or 1) else 240
    run_ff(["-i", a.video, "-vf", f"fps=1/{a.every},scale={tile_w}:-2,tile={cols}x{rows}",
            os.path.join(a.out, "sheet_%02d.png")])
    per_sheet = cols * rows * a.every
    info["contact_sheets"] = {"seconds_per_frame": a.every, "frames_per_sheet": cols * rows,
                              "seconds_per_sheet": per_sheet,
                              "how_to_read": "sheet_01 frame k (row-major, from 0) is at t = k*seconds_per_frame; "
                                             "sheet_02 starts at seconds_per_sheet, etc."}
    for t in [x for x in a.at.split(",") if x.strip()]:
        run_ff(["-ss", t.strip(), "-i", a.video, "-frames:v", "1", "-vf", "scale=360:-2",
                os.path.join(a.out, f"at_{float(t):.1f}.png")])

    fp = fingerprints(a.video, os.path.join(a.out, "_fp.raw"))
    info["scene_cuts"] = scene_cuts(fp)
    if info["has_audio"]:
        info["audio"] = audio_report(a.video, os.path.join(a.out, "_a.wav"))
    if a.reference:
        fo = fingerprints(a.reference, os.path.join(a.out, "_fo.raw"))
        info["mapping_to_reference"] = map_to_reference(fp, fo)
    save_json(info, os.path.join(a.out, "info.json"))

    print(f"{a.video}: {info['duration']:.2f}s  {info['width']}x{info['height']}  {info['fps']} fps  audio={info['has_audio']}")
    print(f"contact sheets: {a.out}/sheet_*.png  ({a.every}s per frame, {per_sheet:.0f}s per sheet)")
    print("scene cuts:", " ".join(str(c) for c in info["scene_cuts"]))
    if "audio" in info:
        print("audio:", info["audio"]["note"], f"(floor {info['audio']['floor_db']} dB)")
    for m in info.get("mapping_to_reference", []):
        print(f"  new {m['new_start']:6.1f}-{m['new_end']:6.1f}s  <-  reference {m['old_start']:6.1f}-{m['old_end']:6.1f}s  (match {m['match']})")


if __name__ == "__main__":
    main()
