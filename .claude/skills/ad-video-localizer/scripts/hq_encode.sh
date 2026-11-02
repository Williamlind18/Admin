#!/usr/bin/env bash
# Best-quality copy for GitHub: two-pass x264 at ~95 MB (GitHub refuses files over 100 MB), encoded
# straight from the source + captions (not from final.mp4), with final.mp4's mixed audio copied as is.
# The user asked for "bästa kvalitet" (2026-11-02): video 14 went from 3.8 to 9.0 Mbit/s, video 15 from
# 5.2 to 6.3 Mbit/s. Usage: hq_encode.sh SRC.mp4 captions.ass FONTS_DIR final.mp4 OUT.mp4 [MB=95]
set -euo pipefail
SRC=$1; ASS=$2; FONTS=$3; FINAL=$4; OUT=$5; MB=${6:-95}
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
DUR=$("$FF" -i "$SRC" 2>&1 | sed -n 's/.*Duration: \([0-9:.]*\).*/\1/p' | awk -F: '{print $1*3600+$2*60+$3}')
K=$(python3 -c "print(int($MB*8*1024/$DUR - 212))")
LOG=$(mktemp -d)/hq
echo "duration ${DUR}s -> video ${K}k"
VF="ass=$(echo "$ASS" | sed 's/:/\\:/g'):fontsdir=$(echo "$FONTS" | sed 's/:/\\:/g')"
"$FF" -v error -y -i "$SRC" -vf "$VF" -c:v libx264 -b:v ${K}k -preset slow -pass 1 -passlogfile "$LOG" \
  -pix_fmt yuv420p -an -f mp4 /dev/null
"$FF" -v error -y -i "$SRC" -i "$FINAL" -map 0:v -map 1:a -vf "$VF" -c:v libx264 -b:v ${K}k -preset slow \
  -pass 2 -passlogfile "$LOG" -pix_fmt yuv420p -c:a copy -movflags +faststart -shortest "$OUT"
ls -la "$OUT"
