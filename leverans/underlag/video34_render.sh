#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 sk/render_ov.py --video base.mp4 --audio vo.wav --ass captions.ass --fonts fonts --out final.mp4 --preview preview.mp4 \
  --bed music_bed.wav --bed-db -19 --overlay-fade 0.06 --crf 22 $(python3 overlay_args.py) \
  --check-frames 1.0,7.5,11.5,13.5,22.0,28.5,37.8,44.6,49.5,60.0,66.0,71.5,75.0,82.0,86.5,90.0,95.5,98.0,102.0,108.0
