#!/usr/bin/env python3
"""Decide where each sentence starts and how much it is sped up.

The voice clips are laid out back to back with short, even gaps (default
0.18 s - the user found 0.5-1.3 s pauses too long). Visual anchors pin chosen
sentences to moments in the video (e.g. "this" on the close-up, "before/after"
on the microscope shots). Between anchors every block gets one uniform tempo;
the optimizer searches the anchor windows to keep the HIGHEST tempo as low as
possible. Tempo > 1.10 starts to sound rushed: fix the script instead (shorten,
merge, move lines) and ask the user before dropping content.

Anchor syntax (repeat --anchor):
  ID:start=LO-HI   sentence ID must START inside [LO, HI] seconds
  ID:end=LO-HI     sentence ID must END inside [LO, HI]  (use for a deictic
                   word at the end of the sentence, e.g. "... det här.")
  ID:start=T       exact
IDs refer to the NN of NN.txt/NN.mp3.

Usage:
  plan_timeline.py SENT_DIR --video-duration 110.4 [--order 1,2,3,...]
                   [--anchor 9:end=44.3-46.6 --anchor 19:start=87.4-89.6]
                   [--gap 0.18] [--max-tempo 1.10]
Writes SENT_DIR/plan.json.
"""
import argparse
import itertools
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, save_json  # noqa: E402


def parse_anchor(s):
    sid_, rest = s.split(":", 1)
    kind, rng = rest.split("=", 1)
    if kind not in ("start", "end"):
        raise SystemExit(f"bad anchor kind in {s!r} (use start or end)")
    if "-" in rng:
        lo, hi = (float(x) for x in rng.split("-", 1))
    else:
        lo = hi = float(rng)
    return int(sid_), kind, lo, hi


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sent_dir")
    ap.add_argument("--video-duration", type=float, required=True)
    ap.add_argument("--order", help="comma-separated sentence ids in spoken order (default: all, ascending)")
    ap.add_argument("--anchor", action="append", default=[])
    ap.add_argument("--gap", type=float, default=0.18, help="normal pause between sentences")
    ap.add_argument("--anchor-gap", type=float, default=0.30, help="pause before a start-anchor / after an end-anchor")
    ap.add_argument("--max-gap", type=float, default=0.45, help="never stretch pauses beyond this")
    ap.add_argument("--lead", type=float, default=0.10, help="first word starts here")
    ap.add_argument("--tail", type=float, default=0.25, help="last word ends this long before the video ends")
    ap.add_argument("--max-tempo", type=float, default=1.10, help="warn above this speed-up (aim <= 1.08)")
    ap.add_argument("--step", type=float, default=0.1)
    a = ap.parse_args()

    F = load_json(os.path.join(a.sent_dir, "fused.json"))
    if not F:
        raise SystemExit("run align_words.py first")
    dur = {s["id"]: s["dur_eff"] for s in F["sentences"]}
    order = [int(x) for x in a.order.split(",")] if a.order else [s["id"] for s in F["sentences"]]
    missing = [i for i in order if i not in dur]
    if missing:
        raise SystemExit(f"no aligned audio for sentences {missing}")
    pos = {i: k for k, i in enumerate(order)}

    anchors = []
    for s in a.anchor:
        i, kind, lo, hi = parse_anchor(s)
        if i not in pos:
            raise SystemExit(f"anchor sentence {i} is not in the order")
        anchors.append({"pos": pos[i] + (1 if kind == "end" else 0), "kind": kind, "lo": lo, "hi": hi, "id": i})
    anchors.sort(key=lambda x: (x["pos"], x["lo"]))
    if len({x["pos"] for x in anchors}) != len(anchors):
        raise SystemExit("two anchors fall on the same sentence boundary - keep one")
    video_end = a.video_duration - a.tail

    def blocks_for(times):
        bnds = [{"pos": 0, "kind": "start", "t": a.lead}]
        bnds += [{"pos": x["pos"], "kind": x["kind"], "t": t} for x, t in zip(anchors, times)]
        bnds.append({"pos": len(order), "kind": "end", "t": video_end})
        out = []
        for b0, b1 in zip(bnds[:-1], bnds[1:]):
            ids = order[b0["pos"]:b1["pos"]]
            t0 = b0["t"] if b0["kind"] == "start" else b0["t"] + a.anchor_gap
            t1 = b1["t"] if b1["kind"] == "end" else b1["t"] - a.anchor_gap
            if not ids:
                if t1 < t0 - 1e-6:
                    return None
                continue
            S, n = sum(dur[i] for i in ids), len(ids)
            room = t1 - t0 - (n - 1) * a.gap
            if room <= 0.05:
                return None
            f, gap, lead = S / room, a.gap, 0.0
            if f < 1.0:
                f = 1.0
                spare = (t1 - t0) - S
                gap = min(a.max_gap, spare / (n - 1)) if n > 1 else a.gap
                leftover = spare - gap * (n - 1)
                # keep an end-anchor exact: put leftover silence before the block
                lead = leftover if b1["kind"] == "end" and b1["pos"] != len(order) else 0.0
            out.append({"ids": ids, "t0": t0 + lead, "t1": t1, "tempo": f, "gap": gap})
        return out

    grids = []
    step = a.step
    while True:
        grids = [np.arange(x["lo"], x["hi"] + 1e-9, step) if x["hi"] > x["lo"] else np.array([x["lo"]]) for x in anchors]
        if np.prod([len(g) for g in grids]) <= 150000 or step > 1:
            break
        step *= 2
    best = None
    for times in itertools.product(*grids) if grids else [()]:
        if any(t2 <= t1 for t1, t2 in zip(times, times[1:])):
            continue
        bl = blocks_for(times)
        if not bl:
            continue
        fs = [b["tempo"] for b in bl]
        score = max(fs) + 0.02 * float(np.std(fs))
        if best is None or score < best[0]:
            best = (score, times, bl)
    if best is None:
        raise SystemExit("no feasible layout - anchors too tight or script far too long for the video")
    _, times, bl = best

    items = []
    for b in bl:
        t = b["t0"]
        for i in b["ids"]:
            items.append({"id": i, "start": round(t, 3), "tempo": round(b["tempo"], 4),
                          "end": round(t + dur[i] / b["tempo"], 3)})
            t += dur[i] / b["tempo"] + b["gap"]
    items.sort(key=lambda x: order.index(x["id"]))
    warnings = []
    mt = max(b["tempo"] for b in bl)
    if mt > a.max_tempo:
        worst = max(bl, key=lambda b: b["tempo"])
        warnings.append(f"block {worst['ids']} needs x{mt:.2f} - shorten/merge lines there or move a line "
                        f"before an anchor; ask the user before dropping content")
    if items[-1]["end"] > a.video_duration:
        warnings.append("voice runs past the end of the video")
    save_json({"video_duration": a.video_duration, "order": order, "gap": a.gap,
               "anchors": [{"id": x["id"], "kind": x["kind"], "t": round(t, 2)} for x, t in zip(anchors, times)],
               "blocks": [{"ids": b["ids"], "tempo": round(b["tempo"], 4), "gap": round(b["gap"], 3)} for b in bl],
               "items": items, "max_tempo": round(mt, 4), "warnings": warnings},
              os.path.join(a.sent_dir, "plan.json"))
    for it in items:
        print(f"s{it['id']:02d} {it['start']:7.2f} - {it['end']:7.2f}  x{it['tempo']:.3f}")
    print("blocks:", "; ".join(f"{b['ids'][0]}..{b['ids'][-1]} x{b['tempo']:.3f} gap {b['gap']:.2f}s" for b in bl))
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
