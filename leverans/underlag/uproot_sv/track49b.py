"""Exact per-frame offsets of video49's badges (passthrough decode): icon 1, badge-1 text, ribbon of badge 2."""
import subprocess, numpy as np, cv2, json
W,H=720,1280; fps=30
f0,n=1266,142
p=subprocess.Popen(['ffmpeg','-v','error','-ss',str((f0-0.5)/fps),'-i','src/video49.mp4','-frames:v',str(n),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
frames={f0+k:np.frombuffer(p.stdout.read(W*H*3),np.uint8).reshape(H,W,3) for k in range(n)}
REF=1349
ref=cv2.cvtColor(frames[REF],cv2.COLOR_RGB2GRAY)
def tm(g,box,region,widths=(1.0,)):
    x0,y0,x1,y1=box; best=None
    rx0,ry0,rx1,ry1=region; sub=g[ry0:ry1,rx0:rx1]
    for wf in widths:
        t=ref[y0:y1,x0:x0+int((x1-x0)*wf)]
        r=cv2.matchTemplate(sub,t,cv2.TM_CCOEFF_NORMED); _,m,_,l=cv2.minMaxLoc(r)
        if best is None or m>best[0]+0.02: best=(m,(l[0]+rx0-x0,l[1]+ry0-y0))
    return round(float(best[0]),3),best[1]
out={}
for f,fr in frames.items():
    g=cv2.cvtColor(fr,cv2.COLOR_RGB2GRAY)
    i1=tm(g,(455,290,625,440),(300,200,720,600),(1.0,0.5))
    t1=tm(g,(383,478,700,540),(200,420,720,620),(1.0,0.6,0.35,0.2))
    rb=tm(g,(420,700,676,780),(250,600,720,880),(1.0,0.5,0.3))
    i2=tm(g,(480,575,625,690),(300,480,720,840),(1.0,0.5))
    out[f]=dict(i1=i1,t1=t1,rb=rb,i2=i2)
json.dump({str(k):v for k,v in out.items()},open('tmp/v49_track_exact.json','w'))
for f in sorted(out):
    if f<1285 or 1315<f<1332 or f>1398 or f%10==0: print(f,out[f])
