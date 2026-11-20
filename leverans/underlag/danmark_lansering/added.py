"""What did the Swedish delivery add on top of the original? Diff at 2 fps outside the caption band.
usage: added.py KEY CAPY  (orig/<KEY>.mp4 vs vid/<KEY>.mp4) -> time spans with bbox"""
import sys, subprocess, json, numpy as np, cv2
k, capy = sys.argv[1], float(sys.argv[2])
o = json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","json",f"vid/{k}.mp4"],capture_output=True,text=True).stdout)["streams"][0]
W, H = o["width"], o["height"]; s = 360 / W; w, h = 360, int(H*s)//2*2
def fr(p):
    pr = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",p,"-vf",f"fps=2,scale={w}:{h}","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(w*h)
        if len(b) < w*h: break
        yield np.frombuffer(b,np.uint8).reshape(h,w).astype(int)
hits = []
for i,(a,b) in enumerate(zip(fr(f"vid/{k}.mp4"), fr(f"orig/{k}.mp4"))):
    d = (np.abs(a-b) > 45).astype(np.uint8)
    d[int((capy-0.045)*h):int((capy+0.045)*h)] = 0
    d = cv2.morphologyEx(d, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    if d.mean() < 0.003: continue
    ys, xs = np.where(d)
    hits.append((i/2, round(d.mean(),3), int(xs.min()/s), int(ys.min()/s), int(xs.max()/s), int(ys.max()/s)))
grp = []
for t, fr_, x0, y0, x1, y1 in hits:
    if grp and t - grp[-1][1] <= 0.6: g = grp[-1]; g[1] = t; g[2] = max(g[2], fr_); g[3] = [min(g[3][0],x0), min(g[3][1],y0), max(g[3][2],x1), max(g[3][3],y1)]
    else: grp.append([t, t, fr_, [x0,y0,x1,y1]])
for a, b, f_, bb in grp: print(f"{a:6.1f}-{b+0.5:6.1f} cover {f_:.2f} box {bb}")
