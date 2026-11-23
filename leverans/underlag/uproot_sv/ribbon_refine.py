"""Refine ribbon offsets for video49 badge 2 by matching adaptive letter masks (robust to the glare pulse)."""
import subprocess, numpy as np, cv2, json
W,H=720,1280; fps=30
o=json.load(open('tmp/v49_badge_off2.json')); RB={int(k):v for k,v in o['rb'].items()}
def letters(img):
    g=img[:,:,1].astype(np.float32); mn=img.min(2).astype(np.float32)
    bgG=cv2.medianBlur(img[:,:,1],21).astype(np.float32)
    bgM=cv2.medianBlur(img.min(2).astype(np.uint8),21).astype(np.float32)
    dark=(bgG-g>22)&(img[:,:,1]>img[:,:,0])          # dark-green letters on the light band
    white=(mn-bgM>45)                                 # white letters on the blue band
    return dark.astype(np.uint8), white.astype(np.uint8)
f0,n=1319,85
p=subprocess.Popen(['ffmpeg','-v','error','-ss',str((f0-0.5)/fps),'-i','src/video49.mp4','-frames:v',str(n),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
frames={f0+k:np.frombuffer(p.stdout.read(W*H*3),np.uint8).reshape(H,W,3) for k in range(n)}
ref=np.array(__import__('PIL.Image',fromlist=['Image']).open('tmp/fr/v49_ref1349.png').convert('RGB'))
rd,rw=letters(ref)
T=np.zeros((H,W),np.float32); T[716:752,420:670]=rd[716:752,420:670]; T[754:776,450:642]+=rw[754:776,450:642]
tpl=T[710:780,415:675]
out={}
for f in range(1328,1404):
    d,w=letters(frames[f]); M=np.zeros((H,W),np.float32); M[:]=0
    M[680:810]=d[680:810]+w[680:810]
    dx0,dy0=[int(round(v)) for v in RB[f]]
    y0,x0=710+dy0-12,415+dx0-12
    sub=M[y0:y0+tpl.shape[0]+24, max(0,x0):x0+tpl.shape[1]+24]
    if sub.shape[1]<tpl.shape[1]+24: out[f]=RB[f]; continue
    r=cv2.matchTemplate(sub,tpl,cv2.TM_CCORR_NORMED); _,m,_,l=cv2.minMaxLoc(r)
    out[f]=(dx0-12+l[0], dy0-12+l[1]); 
    if f%4==0: print(f,'rb',RB[f],'refined',out[f],round(m,3))
for f in range(1319,1328): out[f]=RB[f]
o['rb']={str(k):v for k,v in out.items()}
json.dump(o,open('tmp/v49_badge_off2.json','w'))
