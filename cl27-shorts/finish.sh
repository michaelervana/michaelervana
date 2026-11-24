#!/bin/bash
# Wait for the game capture and the first render batch, encode the last gameplay clips, then render the remaining six.
cd "$(dirname "$0")"
S=/tmp/claude-0/-home-user-michaelervana/cae80eca-14e3-555f-bd93-c7c4e83500db/scratchpad
until grep -q " done$" $S/vid/cap2.log || grep -q FATAL $S/vid/cap2.log; do sleep 20; done
echo "capture finished $(date +%T)"
for c in rain orbit players; do
  [ -f $S/vid/cap/$c/0000.jpg ] && ffmpeg -loglevel error -y -framerate 20 -i $S/vid/cap/$c/%04d.jpg -vf "fps=30,scale=1080:1920:flags=lanczos" -c:v libx264 -preset veryfast -crf 19 -g 15 -pix_fmt yuv420p public/media/game/$c.mp4
done
python3 -I - <<'PY'
import json, subprocess, os
m = json.load(open('src/media.json'))
for c in ['rain', 'orbit', 'players']:
    f = f'public/media/game/{c}.mp4'
    if os.path.exists(f): m['g:' + c] = round(float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout), 3)
json.dump(m, open('src/media.json','w'), indent=1); print({k: m[k] for k in m if k[2:] in ('rain','orbit','players')})
PY
until grep -q RENDERDONE out/render1.log; do sleep 20; done
./render.sh cuju kemari skorgila maracanazo perangbola bolatertua
