"""Shared helpers for the ad-video-localizer scripts.

Everything here is deliberately dependency-light: numpy + librosa for audio,
ffmpeg (static build from the imageio-ffmpeg wheel) for media work.
"""
import json
import os
import re
import shutil
import subprocess
import sys

VOWELS = "aeiouyåäöæøü"


def ffmpeg_exe():
    """Locate an ffmpeg binary: $FFMPEG, the imageio-ffmpeg wheel, or PATH."""
    p = os.environ.get("FFMPEG")
    if p and os.path.exists(p):
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    p = shutil.which("ffmpeg")
    if p:
        return p
    sys.exit("ffmpeg not found - run scripts/setup.sh first")


def run_ff(args, check=True):
    """Run ffmpeg quietly (overwrite outputs)."""
    return subprocess.run([ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", *args], check=check)


def probe(path):
    """Duration / size / fps / audio presence of a media file, parsed from `ffmpeg -i`."""
    r = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", path], capture_output=True, text=True)
    txt = r.stderr
    info = {"path": path, "duration": None, "width": None, "height": None, "fps": None, "has_audio": False}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", txt)
    if m:
        info["duration"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    m = re.search(r"Video: .*?, (\d{2,5})x(\d{2,5})", txt)
    if m:
        info["width"], info["height"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"([\d.]+) fps", txt)
    if m:
        info["fps"] = float(m.group(1))
    info["has_audio"] = "Audio:" in txt
    return info


def to_wav16k(src, dst):
    """Mono 16 kHz wav for analysis (cached: skipped if dst is newer than src)."""
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    run_ff(["-i", src, "-ac", "1", "-ar", "16000", dst])
    return dst


def db_curve(y, hop=160, frame=400):
    """RMS level in dBFS per hop (10 ms at 16 kHz)."""
    import numpy as np
    import librosa
    e = librosa.feature.rms(y=y, frame_length=frame, hop_length=hop)[0]
    return 20 * np.log10(e + 1e-6)


def nsyl(word):
    """Rough syllable count: one per vowel letter (works well for Swedish, OK for English)."""
    w = word.lower().replace("oo", "o").replace("ee", "e")
    return max(1, len(re.findall(f"[{VOWELS}]", w)))


def clean_word(w):
    """Strip sentence punctuation for synthesis/matching (keeps hyphens inside words)."""
    return re.sub(r"[.,!?:;…\"“”()]", "", w)


def sentence_ids(sent_dir):
    """Sorted numeric ids of NN.txt files in sent_dir."""
    ids = []
    for f in os.listdir(sent_dir):
        m = re.fullmatch(r"(\d+)\.txt", f)
        if m:
            ids.append(int(m.group(1)))
    return sorted(ids)


def sid(i):
    return f"{i:02d}"


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(obj, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
