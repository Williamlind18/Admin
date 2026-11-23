#!/bin/bash
# usage: voice_up.sh VID VIDEO_DURATION  (manus/VID.txt, manus/VID_ref.txt, manus/groups.json, takes/VID_aa-bb.mp3)
SK=/home/user/Admin/.claude/skills/ad-video-localizer/scripts
SP=/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad
cd $SP/up
v=$1; D=$2; W=work/$v; mkdir -p $W/sent
python3 - "$v" <<'PY'
import sys
v=sys.argv[1]
L=[l.strip() for l in open(f"manus/{v}.txt",encoding="utf-8") if l.strip()]
for i,t in enumerate(L,1): open(f"work/{v}/sent/{i:02d}.txt","w",encoding="utf-8").write(t+"\n")
PY
for g in $(python3 -c "import json;print(' '.join(f'{a:02d}-{b:02d}' for a,b in json.load(open('manus/groups.json'))['$v']))"); do
  a=${g%-*}; b=${g#*-}; ids=$(seq -f %02g $((10#$a)) $((10#$b)) | tr '\n' ' ')
  ffmpeg -nostdin -v error -y -i takes/${v}_$g.mp3 -ac 1 -ar 16000 tmp/take.wav
  python3 $SK/espeak_cuts.py tmp/take.wav $W/sent $ids --lang sv > $W/cuts_$g.txt
  cuts=$(head -1 $W/cuts_$g.txt | cut -d' ' -f2)
  grep -E "far|short" $W/cuts_$g.txt
  if [ -n "$cuts" ]; then python3 $SP/dk/sk/split_takes.py takes/${v}_$g.mp3 $W/sent $ids --cuts $cuts 2>&1 | grep -E "CHECK" ; else python3 $SP/dk/sk/split_takes.py takes/${v}_$g.mp3 $W/sent $ids 2>&1 | grep CHECK; fi
done
rm -rf $W/sent/raw; python3 $SP/no2/tools/trim_breaths.py $W/sent
python3 $SK/align_words.py $W/sent --lang sv > $W/align.log 2>&1; tail -1 $W/align.log
python3 $SK/plan_on_reference.py $W/sent manus/${v}_ref.txt --video-duration $D --gmin ${GMIN:-0.2} --g0 0.3 --tmin 1.0 --gmax 1.2 --tail ${TAIL:-0.3}
