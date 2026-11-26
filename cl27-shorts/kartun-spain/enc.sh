cd "$(dirname "$0")"
until [ -f logs/done ]; do sleep 10; done
grep -h "FATAL\|PAGEERROR" logs/*.log | head -3
for id in realmadrid barcelona; do
  n=$(ls frames/$id | wc -l)
  ffmpeg -y -loglevel error -framerate 30 -i frames/$id/f%04d.jpg -i mix_$id.wav -vf "format=yuv420p" -af "loudnorm=I=-14:TP=-1.5" -c:v libx264 -crf 17 -preset medium -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart out/sejarah_$id.mp4 && echo "ENC $id ok frames=$n" || echo "ENC $id FAIL frames=$n"
done
