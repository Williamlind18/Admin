"""Batch-2 voice pipeline: sentence files, espeak-DTW cuts, split, align, plan on the Swedish timing, build.
usage (from dk2/): voice_b2.py KEY [KEY ...]"""
import json, os, re, subprocess, sys
S = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SK, TL = os.path.join(S, "dk", "sk"), os.path.join(S, "dk", "tools")
plan = json.load(open("takes_plan2.json"))
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit(f"failed: {' '.join(cmd[:3])}")
    return r.stdout
for k in sys.argv[1:]:
    W = f"work/{k}"; SD = f"{W}/sent"; os.makedirs(SD, exist_ok=True)
    da = [l.strip() for l in open(f"da/{k}.txt") if l.strip()]
    for i, t in enumerate(da):
        open(f"{SD}/{i:02d}.txt", "w").write(t + "\n")
    log = []
    for p in [x for x in plan if x["ad"] == k]:
        ids = [f"{i:02d}" for i in p["ids"]]
        take = f"takes/named/{k}_G{p['g']:02d}.mp3"
        if len(ids) > 1:
            out = run(["python3", f"{TL}/ref_cuts.py", take, SD] + ids + ["--lang", "da"])
            m = re.search(r"CUTS\s+([0-9.,]+)", out)
            cuts = m.group(1).strip(",") if m else None
            cmd = ["python3", f"{SK}/split_takes.py", take, SD] + ids + (["--cuts", cuts] if cuts else [])
        else:
            cmd = ["python3", f"{SK}/split_takes.py", take, SD] + ids
        out2 = run(cmd)
        log.append(f"{k} G{p['g']} cuts {cuts if len(ids) > 1 else '-'}")
    open(f"{W}/split.log", "w").write("\n".join(log) + "\n")
    run(["python3", f"{SK}/align_words.py", SD, "--lang", "da"])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"vid/{k}.mp4"],
                               capture_output=True, text=True).stdout)
    out = run(["python3", f"{TL}/plan_da.py", SD, f"sv/{k}.txt", "--video-duration", f"{dur:.3f}", "--tmin", "0.92",
               "--tmax", "1.08", "--gmin", "0.2", "--gmax", "1.2", "--g0", "0.35", "--tail", "0.3"])
    print(k, out.strip().splitlines()[-1] if out.strip() else "")
    run(["python3", f"{SK}/build_voiceover.py", SD, "--out", f"{W}/vo.wav"])
    import shutil; shutil.copy(f"{W}/words_global.json", f"{W}/words_global_raw.json")
    print(k, "voice built", dur)
