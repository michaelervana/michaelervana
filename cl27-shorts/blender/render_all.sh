#!/bin/bash
# Full render of one story: two Blender processes (each half of the frames) -> OpenCV post (glare, flares, HUSS) -> H.264 with audio.
#   ./render_all.sh <story> [scale%] [samples]
cd "$(dirname "$0")"; id=$1; sc=${2:-66}; smp=${3:-3}
N=$(python3 -c "import json,re;T=json.load(open('timing.json'))['$id'];s=open('story_$id.py').read();tail=float(re.search(r'TAIL = ([0-9.]+)',s).group(1));print(int(round((T['dur']+tail)*30)))")
H=$((N / 2)); mkdir -p frames/$id post/$id logs out
echo "story $id frames $N scale $sc samples $smp"
for part in "0-$((H - 1))" "$H-$((N - 1))"; do
  ( RESUME=1 xvfb-run -a -s "-screen 0 1280x1024x24" blender -b -noaudio -y --python film.py -- $id $part frames/$id $sc $smp > logs/${id}_${part}.log 2>&1 ) &
done
wait
got=$(ls frames/$id | wc -l); echo "rendered $got / $N"
python3 post.py frames/$id post/$id 3 $id
ffmpeg -y -loglevel error -framerate 30 -i post/$id/f%04d.jpg -i mix_$id.wav -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -af "loudnorm=I=-14:TP=-1.5" -shortest -movflags +faststart out/$id.mp4 && echo "ENCODED $id $(ffprobe -v error -show_entries format=duration -of csv=p=0 out/$id.mp4)s"
