#!/usr/bin/env python3
"""Plan the timeline when the voice is SHORTER than the footage.

plan_timeline.py minimises the highest tempo. When the take is short, every
block ends up at x1.00, pauses hit --max-gap and the rest of the spare time
becomes one long silence before each anchor (2 s on the Norrtvätt "tre misstag"
video). This planner uses the same anchors and writes the same plan.json, but it
picks the anchor times inside their windows so the spare time is spread evenly
over all pauses, and it may slow a block down a little (atempo >= --min-tempo,
0.96 is inaudible) so pauses stay near --target-gap instead of growing long.
If a block is too long it speeds up like plan_timeline.py (up to --max-tempo).

Usage (same anchor syntax as plan_timeline.py):
  balance_plan.py SENT_DIR --video-duration 139.6 --anchor 3:start=5.8-6.6 \
      --anchor 11:start=33.3-33.9 [--min-tempo 0.96] [--target-gap 0.25]
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, save_json  # noqa: E402
from plan_timeline import parse_anchor  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sent_dir")
    ap.add_argument("--video-duration", type=float, required=True)
    ap.add_argument("--order")
    ap.add_argument("--anchor", action="append", default=[])
    ap.add_argument("--gap", type=float, default=0.18, help="shortest pause between sentences")
    ap.add_argument("--anchor-gap", type=float, default=0.30)
    ap.add_argument("--target-gap", type=float, default=0.25, help="pause length to aim for")
    ap.add_argument("--max-gap", type=float, default=0.42, help="pauses above this are penalised hard")
    ap.add_argument("--min-tempo", type=float, default=0.96, help="slowest allowed atempo")
    ap.add_argument("--max-tempo", type=float, default=1.08)
    ap.add_argument("--lead", type=float, default=0.10)
    ap.add_argument("--tail", type=float, default=0.30)
    ap.add_argument("--step", type=float, default=0.05)
    a = ap.parse_args()

    F = load_json(os.path.join(a.sent_dir, "fused.json"))
    if not F:
        raise SystemExit("run align_words.py first")
    dur = {s["id"]: s["dur_eff"] for s in F["sentences"]}
    order = [int(x) for x in a.order.split(",")] if a.order else [s["id"] for s in F["sentences"]]
    pos = {i: k for k, i in enumerate(order)}
    anchors = []
    for s in a.anchor:
        i, kind, lo, hi = parse_anchor(s)
        anchors.append({"id": i, "kind": kind, "lo": lo, "hi": hi, "pos": pos[i] + (1 if kind == "end" else 0)})
    anchors.sort(key=lambda x: x["pos"])
    cuts = [0] + [x["pos"] for x in anchors] + [len(order)]
    blocks_ids = [order[cuts[k]:cuts[k + 1]] for k in range(len(cuts) - 1)]
    T, M = a.target_gap, a.max_gap

    def pc(p):  # cost of one pause
        return (p - T) ** 2 + (4 * (p - M) ** 2 if p > M else 0.0)

    def block(ids, t0, t1, slot_min):
        """ids placed inside [t0, t1]; slot = the spare pause at the block edge (>= slot_min)."""
        if not ids:
            return (0.0, 1.0, a.gap, 0.0) if t1 >= t0 - 1e-6 else None
        S, inner, L = sum(dur[i] for i in ids), len(ids) - 1, t1 - t0
        room = L - inner * a.gap - slot_min
        if room <= 0.05:
            return None
        if S / room > 1.0:  # too long: speed up with the shortest pauses
            f = S / room
            return (200 * (f - 1) ** 2, f, a.gap, slot_min) if f <= a.max_tempo else None
        best = None
        for f in np.arange(1.0, a.min_tempo - 1e-9, -0.005):
            spare = L - S / f
            for g in np.arange(a.gap, max(a.gap, spare / max(inner, 1)) + 0.011, 0.01) if inner else [a.gap]:
                slot = spare - inner * g
                if slot < slot_min - 1e-9:
                    break
                c = inner * pc(g) + pc(slot) + 60 * (1 - f) ** 2
                if best is None or c < best[0]:
                    best = (c, float(f), float(g), float(slot))
        return best

    video_end = a.video_duration - a.tail
    grids = [np.round(np.arange(x["lo"], x["hi"] + 1e-9, a.step), 3) for x in anchors]

    def edges(k, tp, t):
        """block k spans from boundary k (time tp) to boundary k+1 (time t)."""
        b0 = anchors[k - 1] if k > 0 else None
        b1 = anchors[k] if k < len(anchors) else None
        t0 = a.lead if b0 is None else (tp if b0["kind"] == "start" else tp + a.anchor_gap)
        if b1 is None:
            return t0, video_end, 0.0, "end"
        if b1["kind"] == "start":
            return t0, t, a.anchor_gap, "end"
        return t0, t, 0.0, "front"  # end anchor: last word ends exactly at t, spare goes in front

    states = {None: (0.0, [])}
    for k in range(len(anchors) + 1):
        new = {}
        for t in (grids[k] if k < len(anchors) else [None]):
            best = None
            for tp, (c, path) in states.items():
                if tp is not None and t is not None and t <= tp:
                    continue
                t0, t1, smin, where = edges(k, tp, t)
                r = block(blocks_ids[k], t0, t1, smin)
                if r and (best is None or c + r[0] < best[0]):
                    best = (c + r[0], path + [(blocks_ids[k], t0, t1, where, r, t)])
            if best:
                new[t] = best
        if not new:
            raise SystemExit(f"no feasible layout around anchor {k} - widen the windows or shorten the script")
        states = new
    _, path = min(states.values(), key=lambda v: v[0])

    items, blocks = [], []
    for ids, t0, t1, where, (_, f, g, slot), _t in path:
        t = t0 + (slot if where == "front" else 0.0)
        for i in ids:
            items.append({"id": i, "start": round(t, 3), "tempo": round(f, 4), "end": round(t + dur[i] / f, 3)})
            t += dur[i] / f + g
        if ids:
            blocks.append({"ids": ids, "tempo": round(f, 4), "gap": round(g, 3)})
    times = [p[5] for p in path[:-1]]
    warnings = [] if items[-1]["end"] <= a.video_duration else ["voice runs past the end of the video"]
    save_json({"video_duration": a.video_duration, "order": order, "gap": a.gap,
               "anchors": [{"id": x["id"], "kind": x["kind"], "t": round(float(t), 2)} for x, t in zip(anchors, times)],
               "blocks": blocks, "items": items, "max_tempo": max(b["tempo"] for b in blocks), "warnings": warnings},
              os.path.join(a.sent_dir, "plan.json"))
    prev = None
    for it in items:
        gap = "" if prev is None else f"  pause {it['start'] - prev:.2f}"
        print(f"s{it['id']:02d} {it['start']:7.2f} - {it['end']:7.2f}  x{it['tempo']:.3f}{gap}")
        prev = it["end"]
    gaps = [b["start"] - x["end"] for x, b in zip(items, items[1:])]
    print(f"pauses {min(gaps):.2f}-{max(gaps):.2f} s (mean {np.mean(gaps):.2f}), tempo "
          f"x{min(b['tempo'] for b in blocks):.3f}-x{max(b['tempo'] for b in blocks):.3f}")
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
