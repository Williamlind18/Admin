#!/usr/bin/env python3
"""Choose exact anchor times inside their windows for plan_timeline.py.

plan_timeline.py searches every combination of anchor times, which is fine for a
handful of anchors but explodes for long videos with 15-25 key moments (it
coarsens the grid and the result gets worse). Blocks between two anchors are
independent once the anchor times are fixed, so dynamic programming over the
anchors finds the times that keep the highest block tempo as low as possible
(ties broken by the sum of squared speed-ups). It prints the exact --anchor
arguments to pass on to plan_timeline.py with the same --gap/--anchor-gap/--tail.

Usage:
  optimize_anchors.py SENT_DIR --video-duration 312.5 [--gap 0.15 --anchor-gap 0.2 --tail 0.15]
                      --anchor 6:start=18.2-20.8 --anchor 11:start=32.6-34.6 ...
  ARGS=$(optimize_anchors.py ... | tail -1); plan_timeline.py SENT_DIR ... $ARGS
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sent_dir")
    ap.add_argument("--video-duration", type=float, required=True)
    ap.add_argument("--anchor", action="append", default=[])
    ap.add_argument("--gap", type=float, default=0.18)
    ap.add_argument("--anchor-gap", type=float, default=0.30)
    ap.add_argument("--lead", type=float, default=0.10)
    ap.add_argument("--tail", type=float, default=0.25)
    ap.add_argument("--step", type=float, default=0.1)
    a = ap.parse_args()

    F = load_json(os.path.join(a.sent_dir, "fused.json"))
    dur = {s["id"]: s["dur_eff"] for s in F["sentences"]}
    order = [s["id"] for s in F["sentences"]]
    anc = []
    for s in a.anchor:
        i, rest = s.split(":", 1)
        kind, rng = rest.split("=", 1)
        lo, hi = (float(x) for x in rng.split("-", 1)) if "-" in rng else (float(rng),) * 2
        anc.append((int(i), kind, lo, hi))
    anc.sort(key=lambda x: order.index(x[0]))
    pos = [order.index(i) + (1 if k == "end" else 0) for i, k, _, _ in anc]
    grids = [np.round(np.arange(lo, hi + 1e-9, a.step), 3) for _, _, lo, hi in anc]

    def tempo(ids, t0, t1):
        if not ids:
            return 1.0 if t1 >= t0 - 1e-6 else 99.0
        S, n = sum(dur[i] for i in ids), len(ids)
        room = t1 - t0 - (n - 1) * a.gap
        return 99.0 if room <= 0.05 else max(1.0, S / room)

    def start_of(k, t):  # where the block after anchor k begins
        return t if anc[k][1] == "start" else t + a.anchor_gap

    def end_before(k, t):  # where the block before anchor k must end
        return t - a.anchor_gap if anc[k][1] == "start" else t

    best = []
    for k, g in enumerate(grids):
        ids = order[(pos[k - 1] if k else 0):pos[k]]
        cur = {}
        for t in g:
            if k == 0:
                f = tempo(ids, a.lead, end_before(0, t))
                cur[t] = ((f, (f - 1) ** 2), None)
                continue
            cand = None
            for tp, (sc, _) in best[k - 1].items():
                if tp >= t:
                    continue
                f = tempo(ids, start_of(k - 1, tp), end_before(k, t))
                s = (max(sc[0], f), sc[1] + (f - 1) ** 2)
                if cand is None or s < cand[0]:
                    cand = (s, tp)
            if cand:
                cur[t] = cand
        best.append(cur)
    fin = None
    for t, (sc, _) in best[-1].items():
        f = tempo(order[pos[-1]:], start_of(len(anc) - 1, t), a.video_duration - a.tail)
        s = (max(sc[0], f), sc[1] + (f - 1) ** 2)
        if fin is None or s < fin[0]:
            fin = (s, t)
    times = [fin[1]]
    for k in range(len(anc) - 1, 0, -1):
        times.append(best[k][times[-1]][1])
    times.reverse()
    print(f"highest block tempo x{fin[0][0]:.3f}")
    print(" ".join(f"--anchor {i}:{k}={t:.2f}" for (i, k, _, _), t in zip(anc, times)))


if __name__ == "__main__":
    main()
