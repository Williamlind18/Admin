#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 sk/render_ov.py --video base.mp4 --audio vo.wav --ass captions.ass --fonts fonts --out final.mp4 --preview preview.mp4 \
  --bed music_bed.wav --bed-db -19 --overlay-fade 0.06 --crf 22 --overlay ov/endcard33.png@102.5-113.0 \
  --check-frames 84.0,86.5,88.0,90.0,95.0,98.0,100.5,101.8,103.0,110.0
