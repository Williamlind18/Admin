#!/bin/bash
# OCR the cleaned video at 2 fps; print time + words (conf>=70, len>=3) per frame.
k=$1; D=$2
F=$D/ocr/$k; rm -rf $F; mkdir -p $F
ffmpeg -nostdin -v error -i $D/clean/${k}_clean.mp4 -vf "fps=2,scale=720:-2" -q:v 2 $F/f_%05d.jpg
ls $F/*.jpg | xargs -P 4 -I{} sh -c 'OMP_THREAD_LIMIT=1 tesseract {} {}.o --psm 11 tsv >/dev/null 2>&1'
python3 - "$F" <<'PY'
import sys,glob,os,csv
F=sys.argv[1]
for p in sorted(glob.glob(F+'/f_*.jpg.o.tsv')):
    n=int(os.path.basename(p)[2:7]); t=(n-1)/2
    ws=[]
    for r in csv.DictReader(open(p),delimiter='\t',quoting=csv.QUOTE_NONE):
        try: c=float(r['conf'])
        except: continue
        w=(r['text'] or '').strip()
        if c>=70 and len(w)>=3 and any(ch.isalpha() for ch in w): ws.append(f"{w}@{r['left']},{r['top']}")
    if ws: print(f"{t:7.1f}  "+' '.join(ws))
PY
