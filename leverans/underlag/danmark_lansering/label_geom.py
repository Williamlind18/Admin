"""Per-frame geometry of the labels: diff Swedish render vs original footage. Prints json list."""
import subprocess, numpy as np, cv2, json, sys
W,H=1080,1908; T0=128.0
def fr(p):
    pr=subprocess.Popen(["ffmpeg","-nostdin","-v","error","-i",p,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
    while True:
        b=pr.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        yield np.frombuffer(b,np.uint8).reshape(H,W,3)
out=[]
for i,(a,b) in enumerate(zip(fr(sys.argv[1]),fr(sys.argv[2]))):
    t=T0+i/30
    d=(np.abs(a.astype(int)-b.astype(int)).max(2)>40).astype(np.uint8)
    d[int(0.70*H):int(0.80*H)]=0   # captions
    # label pixels must be whitish in the Swedish render (box) or dark text inside
    d=cv2.morphologyEx(d,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(d)
    best=None
    for j in range(1,n):
        if st[j][4]>8000 and (best is None or st[j][4]>st[best][4]): best=j
    if best is None: continue
    ys,xs=np.where(lab==best)
    (cx,cy),(bw,bh),ang=cv2.minAreaRect(np.stack([xs,ys],1).astype(np.float32))
    if bw<bh: bw,bh,ang=bh,bw,ang+90
    if ang>45: ang-=180
    out.append(dict(t=round(t,3),cx=round(cx,1),cy=round(cy,1),w=round(bw,1),h=round(bh,1),ang=round(ang,2),area=int(st[best][4])))
json.dump(out,open(sys.argv[3],"w"))
for o in out: print(o)
