"""Find time ranges where Vmake left the Swedish captions in. usage: cap_left.py KEY CAPY"""
import sys, subprocess, json, re, numpy as np
k, capy = sys.argv[1], float(sys.argv[2])
o = json.loads(subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","json",f"vid/{k}.mp4"],capture_output=True,text=True).stdout)
W, H = o["streams"][0]["width"], o["streams"][0]["height"]; s = 360 / W; w, h = 360, int(H*s)//2*2
srt = open(f"src/{k}/sv.srt", encoding="utf-8").read().strip().split("\n\n")
spans = []
for b in srt:
    m = re.findall(r"(\d+):(\d+):(\d+),(\d+)", b.split("\n")[1])
    t = [int(a)*3600+int(b_)*60+int(c)+int(d)/1000 for a,b_,c,d in m]; spans.append(t)
def talking(t): return any(a+0.1 <= t <= b-0.1 for a,b in spans)
def fr(p):
    pr = subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",p,"-vf",f"fps=4,scale={w}:{h}","-f","rawvideo","-pix_fmt","gray","-"],stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(w*h)
        if len(b) < w*h: break
        yield np.frombuffer(b,np.uint8).reshape(h,w)
y0, y1 = int((capy-0.035)*h), int((capy+0.035)*h)
bad = []
for i,(a,b) in enumerate(zip(fr(f"vid/{k}.mp4"), fr(f"clean/{k}_clean.mp4"))):
    t = i/4
    if not talking(t): continue
    d = (np.abs(a[y0:y1].astype(int)-b[y0:y1].astype(int)) > 50).mean()
    if d < 0.004: bad.append(t)
# group
gs = []
for t in bad:
    if gs and t - gs[-1][1] <= 0.5: gs[-1][1] = t
    else: gs.append([t, t])
print(k, "frames with captions left:", len(bad), "spans:", [(a, b) for a, b in gs if b - a >= 0.5][:40])
