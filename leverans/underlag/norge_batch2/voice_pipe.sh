#!/bin/bash
# usage: voice_pipe.sh KEY VIDEO_DURATION   (needs no/KEY.txt, sv/KEY.txt, takes/KEY.mp3)
set -e
SK=/home/user/Admin/.claude/skills/ad-video-localizer/scripts
SP=/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad
cd $SP/no2
k=$1; D=$2; W=work/$k
mkdir -p $W/sent; cp no/$k.txt $W/script.txt
python3 $SK/split_script.py $W/script.txt $W/sent --video-duration $D > /dev/null 2>&1
n=$(ls $W/sent/[0-9][0-9].txt | wc -l); ids=$(seq -f %02g 1 $n | tr '\n' ' ')
ffmpeg -nostdin -v error -y -i takes/$k.mp3 -ac 1 -ar 16000 tmp/$k.wav
HOP=320 python3 tools/espeak_cuts_hop.py tmp/$k.wav $W/sent $ids --lang nb > $W/espeak_cuts.txt
grep -E "far|short" $W/espeak_cuts.txt || true
rm -f $W/sent/[0-9][0-9].mp3; rm -rf $W/sent/raw
python3 $SP/dk/sk/split_takes.py takes/$k.mp3 $W/sent $ids --cuts $(head -1 $W/espeak_cuts.txt | cut -d' ' -f2) 2>&1 | grep CHECK || true
python3 tools/trim_breaths.py $W/sent
rm -rf $W/sent/cache $W/sent/.cache
python3 $SK/align_words.py $W/sent --lang no > $W/align.log 2>&1; tail -1 $W/align.log
python3 $SK/plan_on_reference.py $W/sent sv/$k.txt --video-duration $D --gmin 0.2 --g0 0.3 --tmin 1.0 --gmax 1.2
python3 $SK/build_voiceover.py $W/sent --out $W/vo.wav 2>&1 | tail -1
cp $W/words_global.json $W/words_global_raw.json
python3 tools/numbers_no.py $W/words_global.json
