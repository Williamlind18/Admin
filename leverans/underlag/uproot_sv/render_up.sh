#!/bin/bash
# usage: render_up.sh PIC ASS MIX OUT PREVIEW
set -e
FD=/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/v22it/fonts
ffmpeg -v error -y -i "$1" -i "$3" -map 0:v -map 1:a -vf "subtitles=$2:fontsdir=$FD" -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest -movflags +faststart "$4"
ffmpeg -v error -y -i "$4" -vf scale=540:-2 -c:v libx264 -crf 27 -preset medium -c:a aac -b:a 128k -movflags +faststart "$5"
ls -la "$4" "$5"
