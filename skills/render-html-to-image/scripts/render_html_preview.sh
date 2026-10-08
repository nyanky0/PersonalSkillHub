#!/usr/bin/env bash
# Render an HTML mockup to a PNG using headless Edge/Chrome.
# Use when a static preview image of an HTML artifact is needed and there is no
# Chromium in the browser-automation backend.
# Usage: render_html_preview.sh <input.html> <output.png> [width] [height] [scale]
set -euo pipefail

IN="${1:?usage: render_html_preview.sh <in.html> <out.png> [w] [h] [scale]}"
OUT="${2:?need output path}"
W="${3:-1600}"; H="${4:-900}"; SCALE="${5:-2}"

BROWSER=""
for p in \
  "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  "/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
  "/c/Program Files/Google/Chrome/Application/chrome.exe" \
  "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"; do
  [ -f "$p" ] && BROWSER="$p" && break
done
[ -n "$BROWSER" ] || { echo "no Edge/Chrome found" >&2; exit 1; }

# native (C:/...) paths for the browser args — MSYS conversion is off for native programs
nat() { cygpath -m "$1" 2>/dev/null || echo "$1"; }
IN_ABS="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
OUT_DIR="$(cd "$(dirname "$OUT")" && pwd)"
OUT_NAME="$(basename "$OUT")"
TMP="$(nat "$(mktemp -d)")"

"$BROWSER" --headless=new --disable-gpu --hide-scrollbars --no-first-run \
  --force-device-scale-factor="$SCALE" --window-size="$W,$H" \
  --user-data-dir="$TMP" --screenshot="$(nat "$OUT_DIR")/$OUT_NAME" \
  "file:///$(nat "$IN_ABS")"
rm -rf "$TMP" 2>/dev/null || true
echo "wrote $(nat "$OUT_DIR")/$OUT_NAME"
