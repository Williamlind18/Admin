#!/bin/sh
exec /opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell --no-sandbox --proxy-server="$HTTPS_PROXY" --allow-file-access-from-files "$@"
