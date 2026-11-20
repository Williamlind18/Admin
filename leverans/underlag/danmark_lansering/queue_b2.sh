#!/bin/bash
# mix + render + small preview parts for each key; writes work/<k>/DONE when everything is finished
S=/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad; D=$S/dk2; cd $D
for k in "$@"; do
  echo "== $k $(date +%T)"
  python3 tools/mix_render2.py $k 2>&1 | tail -3
  f=work/$k/${k}_da.mp4; P=work/$k/prev; mkdir -p $P
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
  n=$(python3 -c "import math;print(max(1,math.ceil($dur/130)))")
  for i in $(seq 1 $n); do
    t0=$(python3 -c "print(($i-1)*$dur/$n)"); pd=$(python3 -c "print($dur/$n)"); kb=$(python3 -c "print(min(900,int(9.5*8192/$pd-80)))")
    out=$P/part${i}of${n}.mp4
    ffmpeg -nostdin -v error -y -ss $t0 -i $f -t $pd -vf "scale=480:-2,fps=30" -c:v libx264 -profile:v main -level 3.1 -pix_fmt yuv420p -b:v ${kb}k -maxrate $((kb*13/10))k -bufsize $((kb*2))k -g 60 -preset medium -c:a aac -b:a 80k -ar 44100 -ac 2 -movflags +faststart $out
  done
  touch work/$k/DONE; echo "$k done $(date +%T)"
done
echo QUEUEDONE
