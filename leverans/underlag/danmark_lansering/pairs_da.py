import json,re,sys
p=sys.argv[1]; W=json.load(open(p,encoding='utf-8')); out=[]
for w in W:
    if out and w['w'].lower().strip('.,:;!?') in ('her','der') and out[-1]['w'].lower() in ('den','det','de') and out[-1]['sent']==w['sent'] and w['w'].lower().startswith('her'):
        out[-1]['w']+=' '+w['w']; out[-1]['end']=w['end']
    else: out.append(dict(w))
json.dump(out,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=0); print(p,len(W),'->',len(out))
