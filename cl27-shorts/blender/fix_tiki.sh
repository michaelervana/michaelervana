#!/bin/bash
# after the main render: redo the "tiki, taka!" shot (frames 837-938) with the smaller words, then post + encode again
cd "$(dirname "$0")"
until [ -f logs/alldone ]; do sleep 20; done
python3 -c "
import os
for d in ('frames/tikitaka', 'post/tikitaka'):
    for f in range(837, 939):
        p = os.path.join(d, 'f%04d.jpg' % f)
        if os.path.exists(p): os.remove(p)
print('cleared')"
( RESUME=1 xvfb-run -a -s "-screen 0 1280x1024x24" blender -b -noaudio -y --python film.py -- tikitaka 837-887 frames/tikitaka 66 3 > logs/fix_a.log 2>&1 ) &
( RESUME=1 xvfb-run -a -s "-screen 0 1280x1024x24" blender -b -noaudio -y --python film.py -- tikitaka 888-938 frames/tikitaka 66 3 > logs/fix_b.log 2>&1 ) &
wait
python3 post.py frames/tikitaka post/tikitaka 3 tikitaka
ffmpeg -y -loglevel error -framerate 30 -i post/tikitaka/f%04d.jpg -i mix_tikitaka.wav -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -af "loudnorm=I=-14:TP=-1.5" -shortest -movflags +faststart out/tikitaka.mp4 && echo "FIXED tikitaka $(ffprobe -v error -show_entries format=duration -of csv=p=0 out/tikitaka.mp4)s" > logs/fixdone
