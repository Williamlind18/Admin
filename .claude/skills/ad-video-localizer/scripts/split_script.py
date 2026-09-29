#!/usr/bin/env python3
"""Split the approved script into one text file per sentence and prepare the
word-by-word reference text.

Input: a UTF-8 text file with ONE SENTENCE PER LINE, in the order you expect to
speak them (blank lines ignored). A line may hold two short sentences if they
belong together ("Har du husdjur? Då behöver du det här.").

Writes to SENT_DIR:
  NN.txt          one per line (01, 02, ...)
  iso.txt         every word followed by a period - the text for the cheap
                  word-by-word reference take (see references/elevenlabs.md)
  iso_map.json    which sentence owns how many words of iso.txt
Re-running after edits: lines whose text changed get their old NN.mp3 renamed
to NN.old.mp3 so a stale clip is never used - regenerate those sentences.

Also prints a length budget so you can see *before spending credits* whether
the script fits the video.
Usage: split_script.py SCRIPT.txt SENT_DIR [--video-duration SEC] [--model eleven_v3]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import clean_word, save_json, sid  # noqa: E402

# Measured speaking rates (characters incl. spaces per second of speech) for a
# Swedish female voice. Other voices/languages differ by +-15 %.
RATE = {"eleven_v3": 16.3, "eleven_multilingual_v2": 19.3, "eleven_flash_v2_5": 18.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("sent_dir")
    ap.add_argument("--video-duration", type=float)
    ap.add_argument("--model", default="eleven_v3")
    ap.add_argument("--gap", type=float, default=0.18)
    a = ap.parse_args()
    os.makedirs(a.sent_dir, exist_ok=True)
    lines = [l.strip() for l in open(a.script, encoding="utf-8") if l.strip()]

    changed, iso_words, iso_map = [], [], []
    for i, line in enumerate(lines, 1):
        p = os.path.join(a.sent_dir, f"{sid(i)}.txt")
        if os.path.exists(p) and open(p, encoding="utf-8").read().strip() != line:
            mp3 = os.path.join(a.sent_dir, f"{sid(i)}.mp3")
            if os.path.exists(mp3):
                os.replace(mp3, os.path.join(a.sent_dir, f"{sid(i)}.old.mp3"))
            changed.append(i)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(line + "\n")
        words = [clean_word(w) for w in line.split() if clean_word(w)]
        iso_words += words
        iso_map.append([i, len(words)])
    with open(os.path.join(a.sent_dir, "iso.txt"), "w", encoding="utf-8") as fh:
        fh.write(" ".join(w + "." for w in iso_words) + "\n")
    save_json(iso_map, os.path.join(a.sent_dir, "iso_map.json"))

    rate = RATE.get(a.model, 16.3)
    chars = sum(len(l) for l in lines)
    est = chars / rate
    print(f"{len(lines)} sentences, {chars} characters (~{chars} credits with {a.model}, "
          f"~{len(' '.join(w + '.' for w in iso_words)) // 2} credits for the flash word reference)")
    print(f"estimated speech with {a.model}: {est:.1f}s")
    if a.video_duration:
        avail = a.video_duration - 0.35 - (len(lines) - 1) * a.gap
        need = est / avail
        verdict = ("fits at natural speed" if need <= 1.0 else
                   "fits with a mild speed-up" if need <= 1.08 else
                   "TIGHT - consider trimming/merging lines" if need <= 1.12 else
                   "TOO LONG - shorten the script before generating")
        print(f"video {a.video_duration:.1f}s, room for speech {avail:.1f}s -> needs tempo x{need:.2f}: {verdict}")
    if changed:
        print("CHANGED lines (old audio renamed to NN.old.mp3; make a new whole take, see SKILL.md \"Changed sentences\"):",
              ", ".join(sid(i) for i in changed))


if __name__ == "__main__":
    main()
