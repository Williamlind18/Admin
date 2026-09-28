#!/usr/bin/env bash
# Download generated ElevenLabs clips (signed storage.googleapis.com URLs, valid ~2 h).
# Input: a text file with one "NAME URL" pair per line, e.g.
#   01 https://storage.googleapis.com/xi-backend/...content.mp3?X-Goog-...
#   iso https://storage.googleapis.com/...
# Copy each URL EXACTLY from the creative_get_flow_run_status result (media[].url).
# Usage: bash download_clips.sh urls.txt SENT_DIR
set -u
list="$1"; dir="$2"; mkdir -p "$dir"; fail=0
while read -r name url; do
  [ -z "${name:-}" ] && continue
  case "$name" in \#*) continue;; esac
  code=$(curl -sS -m 120 -o "$dir/$name.mp3" -w "%{http_code}" "$url")
  size=$(stat -c %s "$dir/$name.mp3" 2>/dev/null || echo 0)
  if [ "$code" != "200" ] || [ "$size" -lt 2000 ]; then
    echo "FAILED $name (HTTP $code, $size bytes) - URL expired or mistyped; poll the run status again for a fresh URL"
    rm -f "$dir/$name.mp3"; fail=1
  else
    echo "ok $name ($size bytes)"
  fi
done < "$list"
exit $fail
