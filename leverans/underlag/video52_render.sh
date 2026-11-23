#!/bin/bash
set -e
cd "$(dirname "$0")"
python3 sk/render_ov.py --video clean_full.mp4 --audio vo.wav --ass captions.ass --fonts fonts --out final.mp4 --preview preview.mp4 \
  --bed music_bed.wav --bed-db -19 --overlay-fade 0.06 --crf 22 --overlay endcard.png@279.0-283.3 \
  --check-frames 31.0,33.0
