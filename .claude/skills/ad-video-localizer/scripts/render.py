#!/usr/bin/env python3
"""Render the final video: original picture + new voice track + burned-in
captions, loudness-normalised for social (-14 LUFS). Optionally mixes a music
bed the user supplied, and makes a small preview that fits the 30 MB chat
upload limit. Afterwards it checks the result and prints a short QA report.

Usage:
  render.py --video SRC.mp4 --audio WORK/vo.wav --ass WORK/captions.ass --fonts WORK/fonts
            --out WORK/final.mp4 [--preview WORK/preview.mp4 --preview-mb 28]
            [--bed music.mp3 --bed-db -16] [--check-frames 44.5,90]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import db_curve, probe, run_ff, to_wav16k  # noqa: E402


def ass_times(path):
    def t(s):
        h, m, sec = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(sec)
    out = []
    for line in open(path, encoding="utf-8"):
        if line.startswith("Dialogue:"):
            p = line.split(",", 9)
            out.append((t(p[1]), t(p[2])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--ass", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--crf", type=int, default=21)
    ap.add_argument("--bed", help="optional music bed (the user's own file)")
    ap.add_argument("--bed-db", type=float, default=-16.0, help="music level relative to the voice")
    ap.add_argument("--preview")
    ap.add_argument("--preview-mb", type=float, default=28.0)
    ap.add_argument("--check-frames", default="", help="times to export as PNG for a visual check")
    a = ap.parse_args()

    ass = a.ass.replace("\\", "/").replace(":", "\\:")
    fonts = a.fonts.replace("\\", "/").replace(":", "\\:")
    vf = f"ass={ass}:fontsdir={fonts}"
    if a.bed:
        gain = 10 ** (a.bed_db / 20)
        af = (f"[1:a]aresample=44100[v];[2:a]aresample=44100,volume={gain:.3f},aloop=loop=-1:size=2e9[b];"
              f"[v][b]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        run_ff(["-i", a.video, "-i", a.audio, "-i", a.bed, "-filter_complex", af, "-map", "0:v", "-map", "[a]",
                "-vf", vf, "-c:v", "libx264", "-crf", str(a.crf), "-preset", "fast", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", "-shortest", a.out])
    else:
        run_ff(["-i", a.video, "-i", a.audio, "-map", "0:v", "-map", "1:a", "-vf", vf,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-crf", str(a.crf), "-preset", "fast",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart",
                "-shortest", a.out])
    info = probe(a.out)
    size_mb = os.path.getsize(a.out) / 2 ** 20
    print(f"final: {a.out}  {info['width']}x{info['height']}  {info['duration']:.2f}s  {size_mb:.1f} MB")

    if a.preview:
        kbps = int((a.preview_mb * 8 * 1024) / info["duration"]) - 128 - 40
        run_ff(["-i", a.out, "-c:v", "libx264", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.2)}k",
                "-bufsize", f"{kbps * 2}k", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", a.preview])
        print(f"preview: {a.preview}  {os.path.getsize(a.preview) / 2 ** 20:.1f} MB ({kbps} kb/s video)")

    # QA: every spoken moment has a caption, no long silences, no clipping.
    # Speech is measured on the voice track: a music bed would count as speech.
    import librosa
    tmp = a.out + ".qa.wav"
    to_wav16k(a.out, tmp)
    y, _ = librosa.load(tmp, sr=16000)
    os.remove(tmp)
    to_wav16k(a.audio, tmp)
    yv, _ = librosa.load(tmp, sr=16000)
    os.remove(tmp)
    db = db_curve(yv)
    speech = db > -45
    cov = np.zeros(len(db), bool)
    for s, e in ass_times(a.ass):
        cov[int(s * 100):int(e * 100)] = True
    uncovered = (speech & ~cov).sum() / 100
    q, runs, i = ~speech, [], 0
    first, last = np.argmax(speech), len(speech) - np.argmax(speech[::-1])
    while i < len(q):
        if q[i]:
            j = i
            while j < len(q) and q[j]:
                j += 1
            if j - i >= 50 and first < i and j < last:
                runs.append(f"{i / 100:.1f}s ({(j - i) / 100:.2f}s)")
            i = j
        else:
            i += 1
    peak = 20 * np.log10(np.abs(y).max() + 1e-9)
    print(f"QA: speech without caption {uncovered:.2f}s | pauses > 0.5 s: {', '.join(runs) or 'none'} | peak {peak:.1f} dBFS")
    for t in [x for x in a.check_frames.split(",") if x.strip()]:
        png = os.path.splitext(a.out)[0] + f"_at_{float(t):.1f}.png"
        run_ff(["-ss", t.strip(), "-i", a.out, "-frames:v", "1", "-vf", "scale=360:-2", png])
        print("frame:", png)


if __name__ == "__main__":
    main()
