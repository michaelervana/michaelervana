#!/bin/bash
# Render the given compositions to out/videos/<name>.mp4 (names from src/vo.json).
cd "$(dirname "$0")"
B=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
for id in "$@"; do
  name=$(python3 -I -c "import json;print(json.load(open('src/vo.json'))['$id']['name'])")
  echo "== $id -> $name $(date +%T)"
  npx remotion render $id out/videos/$name.mp4 --codec=h264 --crf=20 --audio-codec=aac --audio-bitrate=192k --concurrency=4 --browser-executable=$B --log=error 2>&1 | tail -3
  ffprobe -v error -show_entries format=duration,size -of csv=p=0 out/videos/$name.mp4
done
echo RENDERDONE
