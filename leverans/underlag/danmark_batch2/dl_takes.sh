#!/bin/bash
# usage: dl_takes.sh LIST  (lines: NAME SESSION GEN SIGNATURE) -> takes/NAME.mp3
B=https://elevenlabsusercontent.com/database/workspace/7a7550a05dcf474e81a525d4d3ce6a47/content_generation
while read n s g sig; do
  [ -z "$n" ] && continue
  [ -s takes/$n.mp3 ] && continue
  for i in 1 2 3 4; do curl -sSL --fail -o takes/$n.mp3 "$B/$s/$g/content.mp3?Expires=1795611600&KeyName=assets-cdn-key-1&Signature=$sig" && break || sleep $((2**i)); done
  echo "$n $(ffprobe -v error -show_entries format=duration -of csv=p=0 takes/$n.mp3)"
done < "$1"
