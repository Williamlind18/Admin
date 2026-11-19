import sys,subprocess,re,numpy as np,cv2,json
k=sys.argv[1]
src=f'vid/{k}.mp4'; cln=f'clean/{k}_clean.mp4'
srt=open(f'src/{k}/sv.srt',encoding='utf-8').read().strip().split('\n\n')
ents=[]
for b in srt:
    L=b.split('\n'); m=re.match(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)',L[1])
    g=[int(x) for x in m.groups()]; t0=g[0]*3600+g[1]*60+g[2]+g[3]/1000; t1=g[4]*3600+g[5]*60+g[6]+g[7]/1000
    ents.append(((t0+t1)/2,' '.join(L[2:])))
sel=ents[5::max(1,len(ents)//25)][:25]
def fr(p,t):
    o=subprocess.run(['ffmpeg','-nostdin','-v','error','-ss',str(t),'-i',p,'-frames:v','1','-f','image2pipe','-vcodec','png','-'],capture_output=True).stdout
    return cv2.imdecode(np.frombuffer(o,np.uint8),cv2.IMREAD_GRAYSCALE)
res=[]
for t,txt in sel:
    a=fr(src,t); b=fr(cln,t); H,W=a.shape
    d=(np.abs(a.astype(int)-b.astype(int))>60).astype(np.uint8)
    d[:int(H*0.3)]=0
    rows=np.where(d.sum(1)>W*0.004)[0]
    if len(rows)==0: continue
    # largest contiguous band
    bands=[];s=rows[0];p=rows[0]
    for r in rows[1:]:
        if r-p>6: bands.append((s,p)); s=r
        p=r
    bands.append((s,p))
    s,e=max(bands,key=lambda x:d[x[0]:x[1]+1].sum())
    cols=np.where(d[s:e+1].sum(0)>0)[0]
    res.append((round(t,1),txt,round((s+e)/2/H,3),e-s+1,cols.min(),cols.max()))
for r in res: print(r)
ys=[r[2] for r in res]; hs=[r[3] for r in res]
print(k,'W,H',W,H,'y median',np.median(ys),'height median',np.median(hs))
