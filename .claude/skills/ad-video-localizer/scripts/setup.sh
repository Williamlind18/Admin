#!/usr/bin/env bash
# Install everything the pipeline needs. Safe to re-run; takes ~1 min the first time.
# Usage: bash setup.sh <work-dir>
# - ffmpeg: static build from the imageio-ffmpeg wheel (PyPI is reachable in the cloud sandbox;
#   note this build has NO drawtext filter - captions go through libass/ASS instead)
# - espeak-ng: synthetic reference voice for one of the three alignment methods (apt)
# - Montserrat ExtraBold: caption font from Google Fonts (falls back to DejaVu Sans Bold)
set -u
WORK="${1:-.}"
mkdir -p "$WORK/fonts"

pip install -q imageio-ffmpeg librosa soundfile numpy scipy 2>&1 | grep -vi "warning" | tail -2

if ! command -v espeak-ng >/dev/null 2>&1; then
  apt-get install -y -qq espeak-ng >/dev/null 2>&1 || \
  { apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq espeak-ng >/dev/null 2>&1; } || \
  echo "WARN: espeak-ng could not be installed - alignment will use the other two methods"
fi

if [ ! -s "$WORK/fonts/Montserrat-ExtraBold.ttf" ]; then
  url=$(curl -sS -m 20 "https://fonts.googleapis.com/css2?family=Montserrat:wght@800" | grep -oE "https://fonts.gstatic.com/[^)]+\.ttf" | head -1)
  if [ -n "$url" ]; then
    curl -sS -m 30 -o "$WORK/fonts/Montserrat-ExtraBold.ttf" "$url"
  else
    echo "WARN: font download failed - use --font 'DejaVu Sans' in make_captions.py"
  fi
fi

python3 - <<'EOF'
import imageio_ffmpeg, subprocess, shutil
ff = imageio_ffmpeg.get_ffmpeg_exe()
filters = subprocess.run([ff, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
print("ffmpeg:", ff)
print("atempo filter (voice speed-up):", "yes" if " atempo " in filters else "NO")
print("ass filter:", "yes" if " ass " in filters else "NO - captions cannot be burned in")
print("espeak-ng:", "yes" if shutil.which("espeak-ng") else "no")
EOF
ls -la "$WORK/fonts"
