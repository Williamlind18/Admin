#!/usr/bin/env python3
"""Render clean video + mix + captions (+ PNG overlays) to a full-quality mp4 (<= ~93 MB) and preview parts.
usage: render_no.py CLEAN.mp4 MIX.wav CAPTIONS.ass OUT.mp4 [--ov=png:t0:t1 ...] [--seq=PATTERN%05d.png:START_FRAME ...]
       [--prev-dir DIR --prev-name NAME]   (--seq: a PNG sequence overlaid from START_FRAME, e.g. a line that fades in)"""
import json, os, subprocess, sys
FONTS = "/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/v22it/fonts"
clean, mix, ass, out = sys.argv[1:5]
ovs = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--ov=")]
o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                               "-show_entries", "format=duration", "-of", "json", clean], capture_output=True, text=True).stdout)
W, H, fps = o["streams"][0]["width"], o["streams"][0]["height"], o["streams"][0]["r_frame_rate"]
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mix],
                           capture_output=True, text=True).stdout)
inputs = ["-i", clean, "-i", mix]; chain, last = [], "0:v"
for i, spec in enumerate(ovs):
    png, t0, t1 = spec.rsplit(":", 2)
    inputs += ["-loop", "1", "-i", png]
    chain.append(f"[{last}][{i + 2}:v]overlay=0:0:enable='between(t,{t0},{t1})':shortest=1[o{i}]"); last = f"o{i}"
seqs = [a.split("=", 1)[1] for a in sys.argv if a.startswith("--seq=")]
for j, spec in enumerate(seqs):
    pat, f0 = spec.rsplit(":", 1); n = inputs.count("-i")
    inputs += ["-framerate", fps, "-start_number", f0, "-i", pat]
    chain.append(f"[{n}:v]setpts=PTS-STARTPTS+{int(f0)}/({fps})/TB[s{j}];[{last}][s{j}]overlay=0:0:eof_action=pass[q{j}]"); last = f"q{j}"
chain.append(f"[{last}]ass='{ass}':fontsdir='{FONTS}'[v]")
vmax = int(93 * 8 * 1024 / dur - 170)
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + inputs + ["-filter_complex", ";".join(chain), "-map", "[v]", "-map", "1:a",
                "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "20", "-maxrate", f"{vmax}k", "-bufsize", f"{vmax * 2}k", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-r", fps, "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", out], check=True)
print(out, round(os.path.getsize(out) / 2 ** 20, 1), "MB", round(dur, 2), "s")
# preview parts: <= 130 s each, 480 px wide, ~9.5 MB
pd = sys.argv[sys.argv.index("--prev-dir") + 1] if "--prev-dir" in sys.argv else os.path.dirname(out)
name = sys.argv[sys.argv.index("--prev-name") + 1] if "--prev-name" in sys.argv else os.path.splitext(os.path.basename(out))[0]
nparts = int(dur // 130) + (1 if dur % 130 > 0.5 else 0)
L = dur / nparts
for k in range(nparts):
    a = k * L; p = os.path.join(pd, f"{name} – förhandsvisning{'' if nparts == 1 else f' del {k + 1} av {nparts}'}.mp4")
    kbps = int(9.3 * 8 * 1024 / L - 96)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{L:.3f}", "-i", out, "-vf", "scale=480:-2",
                    "-c:v", "libx264", "-profile:v", "main", "-level", "3.1", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.3)}k",
                    "-bufsize", f"{kbps * 2}k", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                    "-movflags", "+faststart", p], check=True)
    print(p, round(os.path.getsize(p) / 2 ** 20, 1), "MB")
