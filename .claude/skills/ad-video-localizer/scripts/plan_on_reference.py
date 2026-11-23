#!/usr/bin/env python3
"""Plan a translated voice track on the approved timing of the original-language version (SV_TXT: idx<TAB>start<TAB>end<TAB>text per sentence).

Each sentence i (1:1 with the Swedish sentence i) gets a start s_i and a duration factor u_i = 1/tempo.
Minimises  sum (s_i - S_i)^2  +  MU * sum (u_i - 1)^2  +  NU * sum (gap_i - G0)^2
subject to  gap_i in [GMIN, GMAX],  tempo in [TMIN, TMAX],  s_0 = first Swedish start,
the last sentence ending before the video ends.

Usage: plan_on_reference.py SENT_DIR SV_TXT --video-duration D [--tmin 0.94 --tmax 1.08 --gmin 0.2 --gmax 0.9]
Writes SENT_DIR/plan.json in build_voiceover.py's format.
"""
import argparse
import json
import os

import numpy as np
from scipy.optimize import minimize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sent_dir")
    ap.add_argument("sv_txt")
    ap.add_argument("--video-duration", type=float, required=True)
    ap.add_argument("--tmin", type=float, default=0.94)
    ap.add_argument("--tmax", type=float, default=1.08)
    ap.add_argument("--gmin", type=float, default=0.2)
    ap.add_argument("--gmax", type=float, default=0.9)
    ap.add_argument("--g0", type=float, default=0.35)
    ap.add_argument("--mu", type=float, default=12.0)
    ap.add_argument("--nu", type=float, default=0.6)
    ap.add_argument("--tail", type=float, default=0.3)
    ap.add_argument("--first", type=float, default=None, help="pin first start (default: Swedish first start)")
    a = ap.parse_args()
    F = json.load(open(os.path.join(a.sent_dir, "fused.json")))["sentences"]
    F.sort(key=lambda s: s["id"])
    d = np.array([s["dur_eff"] for s in F])
    S = np.array([float(l.split("\t")[1]) for l in open(a.sv_txt, encoding="utf-8") if l.strip()])
    n = len(d)
    assert len(S) == n, (len(S), n)
    first = S[0] if a.first is None else a.first

    def unpack(x):
        return x[:n], x[n:]

    def obj(x):
        s, u = unpack(x)
        g = s[1:] - s[:-1] - d[:-1] * u[:-1]
        return ((s - S) ** 2).sum() + a.mu * ((u - 1) ** 2).sum() + a.nu * ((g - a.g0) ** 2).sum()

    cons = []
    for i in range(n - 1):
        cons.append({"type": "ineq", "fun": lambda x, i=i: x[i + 1] - x[i] - d[i] * x[n + i] - a.gmin})
        cons.append({"type": "ineq", "fun": lambda x, i=i: a.gmax - (x[i + 1] - x[i] - d[i] * x[n + i])})
    cons.append({"type": "eq", "fun": lambda x: x[0] - first})
    cons.append({"type": "ineq", "fun": lambda x: a.video_duration - a.tail - (x[n - 1] + d[n - 1] * x[2 * n - 1])})
    bounds = [(0, a.video_duration)] * n + [(1 / a.tmax, 1 / a.tmin)] * n
    # feasible-ish start: sequential from Swedish starts
    s0 = [first]
    for i in range(1, n):
        s0.append(max(S[i], s0[-1] + d[i - 1] + a.gmin))
    x0 = np.concatenate([np.array(s0), np.ones(n)])
    r = minimize(obj, x0, method="SLSQP", bounds=bounds, constraints=cons,
                 options={"maxiter": 2000, "ftol": 1e-9})
    s, u = unpack(r.x)
    tempo = 1 / u
    ends = s + d * u
    g = s[1:] - ends[:-1]
    items = [{"id": int(F[i]["id"]), "start": round(float(s[i]), 3), "tempo": round(float(tempo[i]), 4),
              "end": round(float(ends[i]), 3)} for i in range(n)]
    json.dump({"video_duration": a.video_duration, "order": [it["id"] for it in items], "gap": a.g0,
               "anchors": [], "blocks": [], "items": items, "max_tempo": round(float(tempo.max()), 4),
               "warnings": [] if r.success else [r.message]},
              open(os.path.join(a.sent_dir, "plan.json"), "w"), indent=1)
    dev = s - S
    print(f"{os.path.basename(os.path.dirname(a.sent_dir.rstrip('/')))}: ok={r.success} "
          f"dev mean {np.abs(dev).mean():.2f} max {np.abs(dev).max():.2f} (s{int(np.abs(dev).argmax()):02d}) | "
          f"tempo {tempo.min():.3f}-{tempo.max():.3f} | gap {g.min():.2f}-{g.max():.2f} mean {g.mean():.2f} "
          f"n>0.7: {(g > 0.7).sum()} | voice end {ends[-1]:.2f}/{a.video_duration:.2f}")


if __name__ == "__main__":
    main()
