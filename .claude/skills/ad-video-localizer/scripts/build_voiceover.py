#!/usr/bin/env python3
"""Assemble the voice track from the per-sentence clips according to plan.json.

For every planned sentence: cut the clip to its speech, shorten internal pauses
longer than 0.30 s to 0.22 s, speed it up with the rubberband filter
(pitch-preserving; atempo fallback), and place it so the first word starts at
the planned time. Word timings from fused.json are transformed the same way.

Usage: build_voiceover.py SENT_DIR --out WORK/vo.wav
Writes the wav (exactly video length) and words_global.json next to it.
"""
import argparse
import os
import subprocess
import sys
import tempfile

import librosa
import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ffmpeg_exe, load_json, save_json, sid  # noqa: E402

SR = 44100
PRE, POST, KEEP, MAXP = 0.03, 0.08, 0.22, 0.30


def has_rubberband():
    out = subprocess.run([ffmpeg_exe(), "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return " rubberband " in out


def stretch(seg, f, rb):
    if abs(f - 1.0) < 1e-3:
        return seg
    with tempfile.TemporaryDirectory() as td:
        i, o = os.path.join(td, "i.wav"), os.path.join(td, "o.wav")
        sf.write(i, seg, SR)
        filt = f"rubberband=tempo={f:.4f}:pitchq=quality" if rb else f"atempo={f:.4f}"
        subprocess.run([ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", "-i", i, "-af", filt, o], check=True)
        out, _ = sf.read(o, dtype="float32")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sent_dir")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    F = {s["id"]: s for s in load_json(os.path.join(a.sent_dir, "fused.json"))["sentences"]}
    P = load_json(os.path.join(a.sent_dir, "plan.json"))
    rb = has_rubberband()
    if not rb:
        print("note: rubberband filter missing - using atempo (slightly lower quality)")
    total = P["video_duration"]
    track = np.zeros(int((total + 2) * SR), np.float32)
    words_out = []
    for it in P["items"]:
        s = F[it["id"]]
        f = it["tempo"]
        a0, a1 = s["bounds"]
        y, _ = librosa.load(os.path.join(a.sent_dir, f"{sid(it['id'])}.mp3"), sr=SR, mono=True)
        c0 = max(0.0, a0 - PRE)
        seg = y[int(c0 * SR):int((a1 + POST) * SR)].copy()
        words = [{"w": w["w"], "start": w["start"] - c0, "end": w["end"] - c0} for w in s["words"]]
        for ps, pe in sorted(s["pauses"], reverse=True):  # shorten long internal pauses
            if pe - ps <= MAXP:
                continue
            cut = (pe - ps) - KEEP
            x0 = ps - c0 + KEEP / 2
            x1 = x0 + cut
            seg = np.concatenate([seg[:int(x0 * SR)], seg[int(x1 * SR):]])
            for w in words:
                for k in ("start", "end"):
                    if w[k] >= x1:
                        w[k] -= cut
                    elif w[k] > x0:
                        w[k] = x0
        n = int(0.008 * SR)
        seg[:n] *= np.linspace(0, 1, n)
        seg[-n:] *= np.linspace(1, 0, n)
        seg = stretch(seg, f, rb)
        onset = (a0 - c0) / f
        place = it["start"] - onset
        o = int(max(0.0, place) * SR)
        seg = seg[:max(0, len(track) - o)]
        track[o:o + len(seg)] += seg
        for w in words:
            words_out.append({"w": w["w"], "start": round(place + w["start"] / f, 3),
                              "end": round(place + w["end"] / f, 3), "sent": it["id"]})
    track = track[:int(total * SR)]
    peak = float(np.abs(track).max())
    if peak > 0.99:
        track *= 0.99 / peak
    sf.write(a.out, track, SR)
    save_json(words_out, os.path.join(os.path.dirname(os.path.abspath(a.out)), "words_global.json"))
    print(f"wrote {a.out} ({total:.2f}s, {len(P['items'])} sentences, voice ends at "
          f"{max(w['end'] for w in words_out):.2f}s) + words_global.json")


if __name__ == "__main__":
    main()
