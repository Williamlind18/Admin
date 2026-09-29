#!/usr/bin/env python3
"""Assemble the voice track from the per-sentence clips according to plan.json.

For every planned sentence: cut the clip to its speech, shorten internal pauses
longer than 0.30 s to 0.22 s, level-match it, speed it up with the rubberband
filter (pitch-preserving, speech settings; atempo fallback), and place it so the
first word starts at the planned time. Word timings from fused.json are
transformed the same way.

Level matching: clips that came from the same continuous take (fused.json
"para" field, set by split_takes.py) share one gain so the natural emphasis
inside a take is kept; takes are matched to each other. Loose per-sentence
clips get at most +-2 dB so a whispered or emphatic line is not flattened.

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
        # phase=independent + window=short is Rubber Band's recommended setting for speech
        filt = f"rubberband=tempo={f:.4f}:phase=independent:window=short" if rb else f"atempo={f:.4f}"
        subprocess.run([ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", "-i", i, "-af", filt, o], check=True)
        out, _ = sf.read(o, dtype="float32")
    return out


def speech_level_db(seg):
    """Loudness of the voiced part (50 ms frames within 25 dB of the loudest)."""
    n = int(0.05 * SR)
    m = len(seg) // n
    if m == 0:
        return None
    p = (seg[:m * n].reshape(m, n) ** 2).mean(1)
    db = 10 * np.log10(p + 1e-12)
    v = db[db > db.max() - 25]
    return float(10 * np.log10(np.mean(10 ** (v / 10))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sent_dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-level-match", action="store_true")
    a = ap.parse_args()
    F = {s["id"]: s for s in load_json(os.path.join(a.sent_dir, "fused.json"))["sentences"]}
    P = load_json(os.path.join(a.sent_dir, "plan.json"))
    rb = has_rubberband()
    if not rb:
        print("note: rubberband filter missing - using atempo (slightly lower quality)")
    total = P["video_duration"]
    track = np.zeros(int((total + 2) * SR), np.float32)
    words_out = []

    # cut every planned clip first so levels can be matched before placing
    cuts = {}
    for it in P["items"]:
        s = F[it["id"]]
        a0, a1 = s["bounds"]
        y, _ = librosa.load(os.path.join(a.sent_dir, f"{sid(it['id'])}.mp3"), sr=SR, mono=True)
        c0 = max(0.0, a0 - PRE)
        cuts[it["id"]] = (c0, y[int(c0 * SR):int((a1 + POST) * SR)].copy())
    gains = {i: 0.0 for i in cuts}
    if not a.no_level_match:
        groups = {}
        for i, (_, seg) in cuts.items():
            groups.setdefault(F[i].get("para") or f"s{i}", []).append(i)
        levels = {g: speech_level_db(np.concatenate([cuts[i][1] for i in ids])) for g, ids in groups.items()}
        ref = float(np.median([v for v in levels.values() if v is not None]))
        for g, ids in groups.items():
            lim = 4.0 if len(ids) > 1 else 2.0
            gdb = float(np.clip(ref - levels[g], -lim, lim)) if levels[g] is not None else 0.0
            for i in ids:
                gains[i] = gdb
        spread = max(levels.values()) - min(levels.values())
        print(f"level match: {len(groups)} group(s), spread before {spread:.1f} dB")

    for it in P["items"]:
        s = F[it["id"]]
        f = it["tempo"]
        a0, a1 = s["bounds"]
        c0, seg = cuts[it["id"]]
        seg = seg * (10 ** (gains[it["id"]] / 20))
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
