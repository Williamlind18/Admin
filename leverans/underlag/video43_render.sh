#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 sk/render_ov.py --video base.mp4 --audio vo.wav --ass captions.ass --fonts fonts --out final.mp4 --preview preview.mp4 \
  --bed music_bed.wav --bed-db -19 --overlay-fade 0.06 --crf 22 --overlay endcard.png@227.5-231.6 \
  --check-frames 1.0,10.0,20.5,33.0,45.0,60.0,80.0,95.0,110.0,125.0,140.0,150.0,165.0,180.0,195.0,205.0,215.0,222.0,226.5,229.0
