"""Exact (passthrough-decoded) measurements for video50 graphics."""
import subprocess, numpy as np, cv2, json
W,H=720,1280
def frames(f0,n):
    fps=2997/125
    p=subprocess.Popen(['ffmpeg','-v','error','-ss',str((f0-0.5)/fps),'-i','src/video50.mp4','-frames:v',str(n),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
    for k in range(n):
        yield f0+k, np.frombuffer(p.stdout.read(W*H*3),np.uint8).reshape(H,W,3)
# OXYGEN segment
fr={f:a.astype(np.int16) for f,a in frames(448,100)}
dark=[f for f in fr if fr[f].mean()<80]
o0,o1=min(dark),max(dark); print('OX dark frames',o0,o1)
stack=np.stack([fr[f] for f in range(o0,o1+1)])
plate=np.percentile(stack,8,axis=0).astype(np.int16)
bbox={}
for f in range(o0,o1+1):
    d=(fr[f]-plate).max(2); core=d>70; core[780:]=False
    rows=np.nonzero(core.sum(1)>6)[0]
    if len(rows)==0: bbox[f]=None; continue
    top=rows[0]; bot=top
    for r in rows:
        if r-bot>25: break
        bot=r
    cols=np.nonzero(core[top:bot+1].sum(0)>0)[0]
    bbox[f]=[int(cols.min()),int(top),int(cols.max()),int(bot)]
json.dump({'range':[o0,o1],'bbox':{str(k):v for k,v in bbox.items()}},open('tmp/v50_ox_exact.json','w'))
print({f:bbox[f] for f in range(o0,o0+6)}, {f:bbox[f] for f in range(483,506,2)})
# cyan pills
pills={}
for f,a in frames(2360,90):
    a=a.astype(int)
    m=((a[:,:,0]<110)&(a[:,:,1]>160)&(a[:,:,2]>160)&(a[:,:,2]-a[:,:,0]>90)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m,8)
    bands={}
    for j in range(1,n):
        x,y,w,h,ar=[int(v) for v in st[j]]
        if ar<400 or w<40 or not (140<=x<=180 or x+w>=540): continue
        b='top' if y<500 else 'bot'
        r=[x,y,x+w,y+h]
        if b in bands: o=bands[b]; bands[b]=[min(o[0],r[0]),min(o[1],r[1]),max(o[2],r[2]),max(o[3],r[3])]
        else: bands[b]=r
    if bands: pills[f]=bands
fs=sorted(pills); print('pills',fs[0],fs[-1], pills[fs[0]], pills[fs[-1]])
json.dump({str(k):v for k,v in pills.items()},open('tmp/v50_pills_exact.json','w'))
# end card start
for f,a in frames(2765,14):
    print('card?',f,round(float(a.mean()),1))
# enzyme labels: white count in label rect
for rng in [(1500,1512),(1548,1556),(1619,1630),(1714,1726),(1744,1755),(1836,1846)]:
    s=[]
    for f,a in frames(rng[0],rng[1]-rng[0]):
        r=a[738:792,190:535].astype(int); s.append((f,int((r.min(2)>215).sum())))
    print('enz',s)
