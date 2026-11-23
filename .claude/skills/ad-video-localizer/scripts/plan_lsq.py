#!/usr/bin/env python3
"""Plan sentence starts and tempos against the original's sentence times (bounded least squares).

Same job as plan_on_reference.py, but solved as a linear least-squares problem with box bounds
(scipy lsq_linear), so it converges with 100+ sentences where SLSQP stopped with
"Positive directional derivative" and gave gaps of only gmin or gmax (Uproot video57, 107 sentences).

Variables are each sentence's duration D_i (tempo = dur_eff / D_i, bounded by --tmin/--tmax) and each
gap g_i (bounded by --gmin/--gmax). Minimises
  sum_i w_i (s_i - S_i)^2 + mu * sum_i (D_i/d_i - 1)^2 + nu * sum_i (g_i - g0)^2
with the voice ending before T - tail. S_i come from REF (idx<TAB>start<TAB>end<TAB>text, one line per
sentence); the first sentence starts at its REF start. --pin 3:40,97:10 gives key sentences
(a name on its shot, the product name) a higher weight w_i.

Usage: plan_lsq.py WORK/sent WORK/ref.txt --T VIDEO_DUR [--mu 50 --nu 10 --tmin 0.96 --tmax 1.12
       --gmax 0.4 --pin 3:40] [--dry]
Writes WORK/sent/plan.json in the format build_voiceover.py reads.
"""
import json, sys, os, numpy as np
from scipy.optimize import lsq_linear
import argparse
ap=argparse.ArgumentParser()
ap.add_argument('sent'); ap.add_argument('ref')
ap.add_argument('--T',type=float,required=True); ap.add_argument('--tail',type=float,default=0.3)
ap.add_argument('--tmin',type=float,default=1.0); ap.add_argument('--tmax',type=float,default=1.12)
ap.add_argument('--gmin',type=float,default=0.15); ap.add_argument('--gmax',type=float,default=0.45)
ap.add_argument('--g0',type=float,default=0.22); ap.add_argument('--mu',type=float,default=100)
ap.add_argument('--nu',type=float,default=5); ap.add_argument('--wend',type=float,default=0.0)
ap.add_argument('--dry',action='store_true')
ap.add_argument('--pin',default='',help='id:weight,...')
a=ap.parse_args()
F=json.load(open(os.path.join(a.sent,'fused.json')))
F=F if isinstance(F,list) else F['sentences']
F.sort(key=lambda s:s['id'])
d=np.array([s['dur_eff'] for s in F]); n=len(d)
R=[l.rstrip('\n').split('\t') for l in open(a.ref,encoding='utf-8') if l.strip()]
S=np.array([float(r[1]) for r in R]); E=np.array([float(r[2]) for r in R])
s0=S[0]
m=n+(n-1)
rows=[];b=[]
PIN={int(k):float(v) for k,v in (x.split(':') for x in a.pin.split(',') if x)}
for i in range(1,n):
    w=np.sqrt(PIN.get(i+1,1.0))
    r=np.zeros(m); r[:i]=1; r[n:n+i]=1; rows.append(r*w); b.append((S[i]-s0)*w)
for i in range(n):
    r=np.zeros(m); r[i]=np.sqrt(a.mu)/d[i]; rows.append(r); b.append(np.sqrt(a.mu))
for i in range(n-1):
    r=np.zeros(m); r[n+i]=np.sqrt(a.nu); rows.append(r); b.append(np.sqrt(a.nu)*a.g0)
if a.wend>0:
    for i in range(n):  # sentence ends
        r=np.zeros(m); r[:i+1]=1; r[n:n+i]=1; rows.append(r*np.sqrt(a.wend)); b.append(np.sqrt(a.wend)*(E[i]-s0))
A=np.array(rows); b=np.array(b)
lb=np.concatenate([d/a.tmax,np.full(n-1,a.gmin)]); ub=np.concatenate([d/a.tmin,np.full(n-1,a.gmax)])
# end constraint: iterate with penalty if violated
Wend=0
for it in range(30):
    if Wend>0:
        A2=np.vstack([A,np.ones(m)*Wend]); b2=np.append(b,Wend*(a.T-a.tail-s0))
    else: A2,b2=A,b
    r=lsq_linear(A2,b2,bounds=(lb,ub),method='bvls')
    x=r.x; end=s0+x.sum()
    if end<=a.T-a.tail+0.02: break
    Wend=10 if Wend==0 else Wend*3
D=x[:n]; g=x[n:]
s=np.concatenate([[s0],s0+np.cumsum(D[:-1]+g)])
tempo=d/D; ends=s+D
dev=s-S
print(f"dev mean {np.abs(dev).mean():.2f} max {np.abs(dev).max():.2f} (s{int(np.abs(dev).argmax())+1}) | tempo mean {tempo.mean():.3f} max {tempo.max():.3f} n>1.08 {(tempo>1.08).sum()} | gap {g.min():.2f}-{g.max():.2f} mean {g.mean():.2f} n>0.35 {(g>0.35).sum()} | end {ends[-1]:.2f}")
if not a.dry:
    items=[{"id":int(F[i]['id']),"start":round(float(s[i]),3),"tempo":round(float(tempo[i]),4),"end":round(float(ends[i]),3)} for i in range(n)]
    json.dump({"video_duration":a.T,"order":[it['id'] for it in items],"gap":a.g0,"anchors":[],"blocks":[],"items":items,
               "max_tempo":round(float(tempo.max()),4),"warnings":[]},open(os.path.join(a.sent,'plan.json'),'w'),indent=1)
