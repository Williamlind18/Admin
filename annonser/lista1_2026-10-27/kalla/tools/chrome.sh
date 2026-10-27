#!/bin/sh
# headless_shell = old headless: --window-size is the exact viewport. Proxy passed explicitly for Google Fonts.
exec /opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell --no-sandbox --proxy-server="http://127.0.0.1:32801" --allow-file-access-from-files "$@"
