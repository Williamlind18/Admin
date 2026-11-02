#!/bin/bash
set -e
cd "$(dirname "$0")"
O=""
for s in sebum.png@65.667-66.5 pf_base.png@76.70-78.133 pf_hair.png@76.833-78.133 pf_fat.png@77.90-78.133 \
         amy.png@142.367-143.1 pro.png@150.8-152.133 lip.png@162.967-164.333 \
         badge_avk.png@186.067-187.333 badge_alla.png@187.333-188.333 checks.png@188.367-191.433 \
         offer1.png@232.70-234.40 offer3.png@236.767-240.90 endcard.png@242.933-248.5; do O="$O --overlay ov/$s"; done
python3 sk/render_ov.py --video base.mp4 --audio vo.wav --ass captions.ass --fonts fonts --out final.mp4 --preview preview.mp4 \
  --bed music_bed.wav --bed-db -19 --overlay-fade 0.06 --crf 22 $O \
  --check-frames 66.0,77.6,78.05,142.7,151.2,163.4,186.6,187.8,189.6,231.0,233.5,235.5,238.5,245.0
