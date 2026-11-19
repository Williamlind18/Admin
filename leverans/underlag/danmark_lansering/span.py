"""Span of a static overlay in the SOURCE video around a reference time.
usage: span.py KEY T x0 y0 x1 y1 [--win 8] [--thr 10]   (prints t_start t_end, frame-accurate)"""
import sys, subprocess, json, numpy as np
a = sys.argv; k, T = a[1], float(a[2]); x0, y0, x1, y1 = map(int, a[3:7])
win = float(a[a.index("--win")+1]) if "--win" in a else 8.0
thr = float(a[a.index("--thr")+1]) if "--thr" in a else 10.0
o = json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,r_frame_rate","-of","json",f"vid/{k}.mp4"],capture_output=True,text=True).stdout)["streams"][0]
W, H = o["width"], o["height"]; n_, d_ = map(int, o["r_frame_rate"].split("/")); fps = n_/d_
t0 = max(0, T - win)
p = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-ss",f"{t0:.3f}","-i",f"vid/{k}.mp4","-t",f"{2*win:.3f}","-vf",f"crop={x1-x0}:{y1-y0}:{x0}:{y0}","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
sz = (x1-x0)*(y1-y0); fr = []
while True:
    b = p.stdout.read(sz)
    if len(b) < sz: break
    fr.append(np.frombuffer(b,np.uint8).astype(np.float32))
i_ref = int(round((T - t0) * fps)); ref = fr[min(i_ref, len(fr)-1)]
mad = [float(np.abs(f - ref).mean()) for f in fr]
i = i_ref
while i > 0 and mad[i-1] < thr: i -= 1
j = i_ref
while j < len(fr)-1 and mad[j+1] < thr: j += 1
print(f"{k} T={T} span {t0 + i/fps:.3f} - {t0 + (j+1)/fps:.3f}  (fps {fps:.3f}; mad just outside: {mad[i-1] if i>0 else -1:.1f} / {mad[j+1] if j+1<len(mad) else -1:.1f})")
