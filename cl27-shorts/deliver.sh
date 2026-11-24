#!/bin/bash
# Lighter copy for sending/uploading: ~6 Mbps H.264 High, AAC 192k, faststart.
cd "$(dirname "$0")"
for f in "$@"; do n=$(basename "$f"); ffmpeg -loglevel error -y -i "$f" -c:v libx264 -preset slow -crf 21 -maxrate 7M -bufsize 14M -profile:v high -pix_fmt yuv420p -c:a copy -movflags +faststart "out/tiktok/$n"; echo "$n $(du -h out/tiktok/$n | cut -f1)"; done
