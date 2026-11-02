#!/usr/bin/env python3
"""Predict the tempos plan_timeline.py will need for a script, BEFORE paying for the takes.

Fits sentence duration = a + b * syllables on a take you already have from the same voice (any
fused.json from align_words.py, e.g. a sister video), writes a fake fused.json for SCRIPT and runs
plan_timeline.py with your anchors. Use --scale 1.03-1.05 to allow for a slower take: three takes of
the same script differed by up to 6 % in length (video 15, Norwegian).

Built for the Norwegian versions (2026-11-02): the Norwegian voice read ~10 % slower than the Swedish
one, so straight translations needed x1.09-1.14. The prediction matched the real takes to ~0.02.

Usage: predict_tempo.py CAL_SENT_DIR/fused.json SCRIPT.txt [--scale 1.03] -- <plan_timeline args>
       e.g. ... -- --video-duration 120.37 --max-gap 0.6 --anchor 5:start=17.8-18.2 ...
"""
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

VOWELS = "aeiouyåäöæøü"


def syl(t):
    return len(re.findall(f"[{VOWELS}]", t.lower()))


def main():
    if "--" not in sys.argv:
        sys.exit(__doc__)
    k = sys.argv.index("--")
    own, plan_args = sys.argv[1:k], sys.argv[k + 1:]
    scale = 1.0
    if "--scale" in own:
        i = own.index("--scale")
        scale = float(own[i + 1])
        del own[i:i + 2]
    cal, script = own
    S = json.load(open(cal, encoding="utf-8"))["sentences"]
    x = np.array([syl(s["text"]) for s in S], float)
    y = np.array([s["dur_eff"] for s in S])
    A = np.vstack([np.ones_like(x), x]).T
    (a, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    print(f"fit on {len(S)} sentences: dur = {a:.2f} s + {b * 1000:.0f} ms/syllable "
          f"(residual sd {np.std(y - A @ [a, b]):.2f} s), scale {scale}")
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip()]
    with tempfile.TemporaryDirectory() as d:
        sents = [{"id": i + 1, "text": t, "dur_eff": scale * (a + b * syl(t))} for i, t in enumerate(lines)]
        json.dump({"sentences": sents}, open(os.path.join(d, "fused.json"), "w"))
        print(f"predicted speech {sum(s['dur_eff'] for s in sents):.1f} s for {len(lines)} sentences")
        planner = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan_timeline.py")
        r = subprocess.run([sys.executable, planner, d] + plan_args, capture_output=True, text=True)
    out = [l for l in (r.stdout + r.stderr).splitlines() if l.startswith(("blocks", "WARNING", "Error", "Traceback"))]
    print("\n".join(out) if out else r.stdout[-2000:] + r.stderr[-2000:])


if __name__ == "__main__":
    main()
