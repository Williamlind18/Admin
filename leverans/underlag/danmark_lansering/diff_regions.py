"""Where did Vmake remove something outside the caption band? usage: diff_regions.py KEY CAPY"""
import sys, subprocess, json, numpy as np, cv2
k, capy = sys.argv[1], float(sys.argv[2])
def probe(p):
    o = json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","json",p],capture_output=True,text=True).stdout)
    return o["streams"][0]["width"], o["streams"][0]["height"]
W, H = probe(f"vid/{k}.mp4"); s = 360 / W; w, h = 360, int(H * s) // 2 * 2
def fr(p):
    pr = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",p,"-vf",f"fps=2,scale={w}:{h}","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(w*h)
        if len(b) < w*h: break
        yield np.frombuffer(b,np.uint8).reshape(h,w)
hits = []
for i,(a,b) in enumerate(zip(fr(f"vid/{k}.mp4"), fr(f"clean/{k}_clean.mp4"))):
    d = (np.abs(a.astype(int)-b.astype(int)) > 50).astype(np.uint8)
    y0, y1 = int((capy-0.05)*h), int((capy+0.05)*h)
    d[y0:y1] = 0
    d = cv2.dilate(d, np.ones((7,15),np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(d)
    for j in range(1, n):
        x, y, bw, bh, ar = st[j]
        if ar > 600 and bw > 25:
            hits.append((i/2, int(x/s), int(y/s), int(bw/s), int(bh/s)))
groups = []
for t,x,y,bw,bh in hits:
    for g in groups:
        if abs(g['y']-y) < 60/s*0.5 and t - g['t1'] <= 1.0:
            g['t1'] = t; g['n'] += 1; g['x0']=min(g['x0'],x); g['x1']=max(g['x1'],x+bw); g['y1']=max(g['y1'],y+bh); break
    else:
        groups.append(dict(t0=t,t1=t,y=y,x0=x,x1=x+bw,y1=y+bh,n=1))
for g in groups:
    if g['n'] >= 2: print(f"{g['t0']:7.1f}-{g['t1']:7.1f} n={g['n']:3d} x {g['x0']}-{g['x1']} y {g['y']}-{g['y1']}")
