#!/usr/bin/env bash
# Rebuilds the edited source videos the Swedish ads were rendered from, starting from the
# original GitHub releases. Run: bash leverans/norska/rebuild_sources.sh WORKDIR [5|11|14|15 ...]
# Writes WORKDIR/videoN/src.mp4 (the exact footage the Swedish version used, same frame count).
set -euo pipefail
W=${1:?usage: rebuild_sources.sh WORKDIR [video numbers]}; shift
VIDS=${*:-5 11 14 15}
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
REL=https://github.com/Williamlind18/Admin/releases/download
get() { mkdir -p "$W/video$1/dl"; [ -s "$W/video$1/dl/src_orig.mp4" ] || curl -sSL -o "$W/video$1/dl/src_orig.mp4" "$REL/$2"; }
for v in $VIDS; do
  case $v in
  5)  # remove the competitor's Florida map shot (frames 4665-4777, 155.50-159.27 s) -> 244.57 s
      get 5 video5/norrtvatt.claude.-.1.3.mp4
      "$FF" -v error -y -i "$W/video5/dl/src_orig.mp4" \
        -vf "select='not(between(n\,4665\,4777))',setpts=N/FRAME_RATE/TB" \
        -af "aselect='not(between(t\,155.5\,159.2667))',asetpts=N/SR/TB" \
        -c:v libx264 -preset fast -crf 14 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k "$W/video5/src.mp4" ;;
  11) # used as is
      get 11 video11/Norrtvatt.trimmad.-.C3.mp4
      cp "$W/video11/dl/src_orig.mp4" "$W/video11/src.mp4" ;;
  14) # 480x832 download -> 1080x1872: denoise, deband, Lanczos, adaptive sharpening
      get 14 video14/norrtvatt_-_konkurrent_6.mp4
      "$FF" -v error -y -i "$W/video14/dl/src_orig.mp4" \
        -vf "hqdn3d=1.5:1.5:3:3,deband=1thr=0.015:2thr=0.015:3thr=0.015:range=12:blur=1,scale=1080:1872:flags=lanczos,cas=strength=0.6" \
        -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a copy "$W/video14/src.mp4" ;;
  15) get 15 video15/Norrtvatt.trimmad.-.C5.mp4
      d="$W/video15"; rm -rf "$d/f56" "$d/f86"; mkdir -p "$d/f56" "$d/f86"
      # (a) "60 DAY MONEY BACK" (frames 3212-3241) removed: frames 3156-3211 slowed to 86 frames
      "$FF" -v error -i "$d/dl/src_orig.mp4" -vf "select='between(n\,3156\,3211)'" -fps_mode passthrough "$d/f56/%03d.png"
      "$FF" -v error -framerate 30 -i "$d/f56/%03d.png" \
        -vf "setpts=PTS*87/55,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none" \
        -fps_mode passthrough "$d/f86/%03d.png"
      [ "$(ls "$d/f86" | wc -l)" = 86 ] || { echo "expected 86 interpolated frames"; exit 1; }
      "$FF" -v error -y -i "$d/dl/src_orig.mp4" -framerate 30 -i "$d/f86/%03d.png" -filter_complex \
        "[0:v]trim=end_frame=3156,setpts=PTS-STARTPTS[a];[1:v]format=yuv420p,setsar=1,setpts=N/30/TB[b];[0:v]trim=start_frame=3242,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,fps=30[v]" \
        -map "[v]" -c:v libx264 -preset fast -crf 14 -pix_fmt yuv420p "$d/src_a.mp4"
      # (b) blurry "3 REASONS" panel (frames 431-536) replaced by mirrored footage of the woman
      #     sniffing the washer (1965-2010) and her face in the drum (1904-1963)
      "$FF" -v error -y -i "$d/src_a.mp4" -filter_complex \
        "[0:v]split=4[s0][s1][s2][s3];[s0]trim=end_frame=431,setpts=PTS-STARTPTS[a];[s1]trim=start_frame=1965:end_frame=2011,setpts=PTS-STARTPTS,hflip[b];[s2]trim=start_frame=1904:end_frame=1964,setpts=PTS-STARTPTS,hflip[c];[s3]trim=start_frame=537,setpts=PTS-STARTPTS[d];[a][b][c][d]concat=n=4:v=1:a=0,fps=30[v]" \
        -map "[v]" -c:v libx264 -preset fast -crf 14 -pix_fmt yuv420p "$d/src.mp4"
      rm -rf "$d/f56" "$d/f86" "$d/src_a.mp4" ;;
  *) echo "unknown video $v"; exit 1 ;;
  esac
  echo "video$v: $("$FF" -i "$W/video$v/src.mp4" 2>&1 | grep -o 'Duration: [0-9:.]*')"
done
