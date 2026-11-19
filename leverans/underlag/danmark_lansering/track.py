"""Per-frame white box near an expected box in the SOURCE. usage: track.py KEY t0 t1 x0 y0 x1 y1 [--json out]
Prints runs of frames where a white box overlaps the expected box (IoU>0.5), with the box per run."""
import sys, subprocess, json, numpy as np, cv2
a = sys.argv; k = a[1]; t0, t1 = float(a[2]), float(a[3]); E = list(map(int, a[4:8]))
o = json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,r_frame_rate","-of","json",f"vid/{k}.mp4"],capture_output=True,text=True).stdout)["streams"][0]
W, H = o["width"], o["height"]; n_, d_ = map(int, o["r_frame_rate"].split("/")); fps = n_/d_
p = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-ss",f"{t0:.3f}","-i",f"vid/{k}.mp4","-t",f"{t1-t0:.3f}","-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
def iou(b, c):
    ix = max(0, min(b[2], c[2]) - max(b[0], c[0])); iy = max(0, min(b[3], c[3]) - max(b[1], c[1]))
    i = ix*iy; u = (b[2]-b[0])*(b[3]-b[1]) + (c[2]-c[0])*(c[3]-c[1]) - i
    return i / u if u else 0
res = []; i = 0
while True:
    b = p.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    img = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    white = ((hsv[:,:,2] > 215) & (hsv[:,:,1] < 35)).astype(np.uint8)*255
    white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 9)))
    cn, _ = cv2.findContours(white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for c in cn:
        (cx, cy), (bw, bh), ang = cv2.minAreaRect(c)
        if bw < bh: bw, bh, ang = bh, bw, ang + 90
        if ang > 45: ang -= 180
        if cv2.contourArea(c) / (bw*bh + 1e-6) < 0.8: continue
        bb = [cx-bw/2, cy-bh/2, cx+bw/2, cy+bh/2]
        s = iou(bb, E)
        if s > float(__import__("os").environ.get("IOU","0.5")) and (best is None or s > best[0]): best = (s, [round(v) for v in bb], round(ang, 1))
    res.append((round(t0 + i/fps, 3), best[1] if best else None, best[2] if best else None)); i += 1
runs = []
for t, bb, ang in res:
    if bb is None:
        continue
    if runs and abs(t - runs[-1]["t1"] - 1/fps) < 1e-3 and max(abs(x-y) for x, y in zip(bb, runs[-1]["box"])) <= 4 and abs(ang - runs[-1]["ang"]) < 0.6:
        runs[-1]["t1"] = t; runs[-1]["n"] += 1
    else:
        runs.append(dict(t0=t, t1=t, box=bb, ang=ang, n=1))
for r in runs: print(f"{r['t0']:.3f}-{r['t1']+1/fps:.3f} n={r['n']} box={r['box']} ang={r['ang']}")
if "--json" in a: json.dump(res, open(a[a.index("--json")+1], "w"))
