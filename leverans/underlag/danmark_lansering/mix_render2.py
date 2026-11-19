#!/usr/bin/env python3
"""Danish launch set: mix the Danish voice with the Swedish ad's music bed at the Swedish levels, then render with
the Danish overlays (ov/<key>/spec.json) and captions.   usage (from dk2/): mix_render2.py KEY [--mix-only]"""
import json
import math
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(os.path.dirname(D), "v22it", "fonts")
SR = 44100

CONF = {
    "a5c4": dict(bed=("jump", 233.0, 10.0)),
    "a5c5": dict(bed=("loop", 136.0, 4.04)),
    "a5c1": dict(bed=("loop", 136.0, 4.04)),
    "a3c1": dict(bed="linear"),
    "a1c4": dict(bed="linear"),
}


def load(f, sr=SR):
    a = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", f, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True).stdout
    return np.frombuffer(a, np.float32).astype(np.float64)


def probe(f):
    o = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,r_frame_rate", "-show_entries", "format=duration", "-of",
                                   "json", f], capture_output=True, text=True).stdout)
    s = o["streams"][0]
    return s["width"], s["height"], s["r_frame_rate"], float(o["format"]["duration"])


def make_bed(key, total):
    m = load(os.path.join(D, "music", f"{key}.mp3"))
    n = int(total * SR)
    mode = CONF[key]["bed"]
    if isinstance(mode, tuple) and mode[0] == "loop":
        _, P, X = mode
        L = len(m)
        k = int(math.ceil(total / P)) + 1
        bed = np.zeros(int((k * P + L / SR + 1) * SR))
        xf = int(X * SR)
        r = np.linspace(0, 1, xf)
        for i in range(k):
            st = int(round(i * P * SR))
            seg = m.copy()
            if i > 0:
                seg[:xf] *= r
            if i < k - 1:
                seg[L - xf:] *= r[::-1]
            bed[st:st + L] += seg
    elif isinstance(mode, tuple) and mode[0] == "jump":
        _, J, back = mode
        j, xf = int(J * SR), int(0.3 * SR)
        a = m[:j + xf].copy()
        b = m[int((J - back) * SR):].copy()
        r = np.linspace(0, 1, xf)
        a[j:j + xf] *= r[::-1]
        b[:xf] *= r
        bed = np.zeros(j + len(b))
        bed[:len(a)] += a
        bed[j:j + len(b)] += b
    else:
        bed = m
    if len(bed) < n:
        bed = np.concatenate([bed, np.zeros(n - len(bed))])
    return bed[:n]


def ebur(f):
    o = subprocess.run(["ffmpeg", "-nostdin", "-i", f, "-vn", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])


def active_rms(x, thr_pct=55):
    fr = int(0.05 * SR)
    k = len(x) // fr
    r = np.sqrt((x[:k * fr].reshape(k, fr) ** 2).mean(1))
    return float(r[r > np.percentile(r, thr_pct)].mean())


def mix(key):
    W, H, fps, dur = probe(os.path.join(D, "clean", f"{key}_clean.mp4"))
    n = int(dur * SR)
    src = os.path.join(D, "vid", f"{key}.mp4")
    sv = load(src)[:n]
    sv = np.concatenate([sv, np.zeros(max(0, n - len(sv)))])
    bed = make_bed(key, dur)
    g = float(sv @ bed / (bed @ bed))
    sv_voice = sv - g * bed
    vo, vsr = sf.read(os.path.join(D, "work", key, "vo.wav"))
    if vo.ndim > 1:
        vo = vo.mean(1)
    if vsr != SR:
        import librosa
        vo = librosa.resample(vo, orig_sr=vsr, target_sr=SR)
    vo = np.concatenate([vo, np.zeros(max(0, n - len(vo)))])[:n]
    scale = active_rms(sv_voice) / active_rms(vo)
    out = scale * vo + g * bed
    f = int(0.6 * SR)
    out[-f:] *= np.linspace(1, 0, f)
    raw = os.path.join(D, "work", key, "mix_raw.wav")
    sf.write(raw, np.stack([out, out], 1).astype(np.float32), SR, subtype="FLOAT")
    I = ebur(src)
    m = subprocess.run(["ffmpeg", "-nostdin", "-i", raw, "-af", f"loudnorm=I={I}:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
    af = (f"loudnorm=I={I}:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR), "-c:a",
                    "pcm_s16le", os.path.join(D, "work", key, "mix.wav")], check=True)
    os.remove(raw)
    info = dict(music_gain=round(g, 4), voice_scale=round(scale, 3), target_I=I,
                result_I=ebur(os.path.join(D, "work", key, "mix.wav")))
    print(key, info)
    return info


def captions(key, spec, H):
    """captions.ass with the per-range y overrides from the overlay spec (e.g. the SMS section in A5 C5)."""
    src = os.path.join(D, "work", key, "captions.ass")
    out = os.path.join(D, "work", key, "captions_final.ass")
    ov = spec.get("cap_y_override", [])

    def sec(ts):
        h, m_, s = ts.split(":")
        return int(h) * 3600 + int(m_) * 60 + float(s)
    lines = []
    for ln in open(src, encoding="utf-8"):
        if ln.startswith("Dialogue:") and ov:
            st = sec(ln.split(",")[1])
            for t0, t1, y in ov:
                if t0 <= st < t1:
                    ln = re.sub(r"\\pos\((\d+),(\d+)\)", lambda mm: f"\\pos({mm.group(1)},{round(H * y)})", ln)
        lines.append(ln)
    open(out, "w", encoding="utf-8").writelines(lines)
    return out


def render(key):
    clean = os.path.join(D, "clean", f"{key}_clean.mp4")
    W, H, fps, dur = probe(clean)
    w = os.path.join(D, "work", key)
    sp = os.path.join(D, "ov", key, "spec.json")
    spec = json.load(open(sp)) if os.path.exists(sp) else dict(items=[])
    out = os.path.join(w, f"{key}_da.mp4")
    inputs = ["-i", clean, "-i", os.path.join(w, "mix.wav")]
    nin = 2
    chain, last = [], "0:v"
    src_idx = None
    for i, it in enumerate(spec["items"]):
        t0, t1 = it["t0"], min(it["t1"], dur + 1)
        en = f"enable='between(t,{t0},{t1})'"
        if it["kind"] == "png":
            inputs += ["-loop", "1", "-framerate", fps, "-i", os.path.join(D, it["file"])]
            chain.append(f"[{last}][{nin}:v]overlay=0:0:{en}:shortest=1[o{i}]")
            nin += 1
        elif it["kind"] == "seq":
            inputs += ["-framerate", "30", "-i", os.path.join(D, it["pattern"])]
            chain.append(f"[{nin}:v]setpts=PTS-STARTPTS+{t0}/TB[s{i}]")
            chain.append(f"[{last}][s{i}]overlay=0:0:{en}:eof_action=pass[o{i}]")
            nin += 1
        elif it["kind"] == "src":
            if src_idx is None:
                inputs += ["-i", os.path.join(D, "vid", f"{key}.mp4")]
                src_idx = nin
                nin += 1
                n_src = sum(1 for x in spec["items"] if x["kind"] == "src")
                chain.append(f"[{src_idx}:v]split={n_src}" + "".join(f"[sv{j}]" for j in range(n_src)))
                src_k = 0
            x0, y0, x1, y1 = it["box"]
            chain.append(f"[sv{src_k}]crop={x1 - x0}:{y1 - y0}:{x0}:{y0}[c{i}]")
            chain.append(f"[{last}][c{i}]overlay={x0}:{y0}:{en}[o{i}]")
            src_k += 1
        last = f"o{i}"
    ass = captions(key, spec, H).replace(":", "\\:")
    chain.append(f"[{last}]ass='{ass}':fontsdir='{FONTS}'[v]")
    total_kbps = 93 * 8 * 1024 / dur
    vmax = int(total_kbps - 170)
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y"] + inputs + [
        "-filter_complex", ";".join(chain), "-map", "[v]", "-map", "1:a", "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-crf", "20", "-maxrate", f"{vmax}k", "-bufsize", f"{vmax * 2}k", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-r", fps, "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart",
        out]
    subprocess.run(cmd, check=True)
    kbps = min(2200, int((27 * 8 * 1024) / dur) - 128 - 30)
    prev = os.path.join(w, f"{key}_da_preview.mp4")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", out, "-vf", "scale=540:-2", "-c:v", "libx264",
                    "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.2)}k", "-bufsize", f"{kbps * 2}k", "-preset",
                    "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", prev],
                   check=True)
    for f in (out, prev):
        print(f, round(os.path.getsize(f) / 2 ** 20, 1), "MB")


if __name__ == "__main__":
    k = sys.argv[1]
    mix(k)
    if "--mix-only" not in sys.argv:
        render(k)
