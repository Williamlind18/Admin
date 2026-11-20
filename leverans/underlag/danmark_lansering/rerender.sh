#!/bin/bash
# render only (mix.wav already made) + small preview parts; work/<k>/DONE2 when finished
S=/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad; D=$S/dk2; cd $D
until grep -q QUEUEDONE /tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/tasks/bj16rsrjr.output; do sleep 15; done
for k in "$@"; do
  echo "== $k $(date +%T)"
  python3 -c "import sys; sys.path.insert(0,'tools'); import mix_render2 as m; m.render('$k')" 2>&1 | tail -2
  f=work/$k/${k}_da.mp4; P=work/$k/prev; mkdir -p $P; rm -f $P/part*.mp4
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)
  n=$(python3 -c "import math;print(max(1,math.ceil($dur/130)))")
  for i in $(seq 1 $n); do
    t0=$(python3 -c "print(($i-1)*$dur/$n)"); pd=$(python3 -c "print($dur/$n)"); kb=$(python3 -c "print(min(900,int(9.5*8192/$pd-80)))")
    ffmpeg -nostdin -v error -y -ss $t0 -i $f -t $pd -vf "scale=480:-2,fps=30" -c:v libx264 -profile:v main -level 3.1 -pix_fmt yuv420p -b:v ${kb}k -maxrate $((kb*13/10))k -bufsize $((kb*2))k -g 60 -preset medium -c:a aac -b:a 80k -ar 44100 -ac 2 -movflags +faststart $P/part${i}of${n}.mp4
  done
  touch work/$k/DONE2; echo "$k done $(date +%T)"
done
echo RERENDERDONE
