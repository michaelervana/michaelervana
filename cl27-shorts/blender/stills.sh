#!/bin/bash
# one still per shot (middle of each shot) + contact sheet:  ./stills.sh <story> [scale]
cd "$(dirname "$0")"; id=$1; sc=${2:-50}
F=$(python3 -c "
import json,importlib,sys; sys.path.insert(0,'.')
T=json.load(open('timing.json'))['$id']
import ast
src=open('story_$id.py').read()
# shot starts without importing bpy: parse 'from_' and 'at'
import re
shots=re.findall(r\"dict\(from_=(\d+)(?:, at=([0-9.]+))?\", src)
st=[]
for i,(fr,at) in enumerate(shots):
    L=T['lines'][int(fr)]; st.append(0.0 if i==0 else (float(at) if at else L['t0']-0.12))
tail=float(re.search(r'TAIL = ([0-9.]+)', src).group(1)); end=T['dur']+tail; st.append(end)
print(','.join(str(int(((st[i]+st[i+1])/2)*30)) for i in range(len(st)-1)))
")
echo "frames $F"
mkdir -p stills/$id
xvfb-run -a -s "-screen 0 1280x1024x24" blender -b -noaudio -y --python film.py -- $id "$F" stills/$id $sc 3 2>&1 | grep -E "BUILD|FRAME|DONE|Error|rror:|Traceback|line [0-9]+|NO GAME|GAMEBOARDS" | head -30
python3 -c "
from PIL import Image; import glob
fs=sorted(glob.glob('stills/$id/*.jpg')); ims=[Image.open(f).resize((216,384)) for f in fs]
n=len(ims); cols=min(6,n); rows=(n+cols-1)//cols
s=Image.new('RGB',(cols*220,rows*388),(0,0,0))
for i,im in enumerate(ims): s.paste(im,((i%cols)*220,(i//cols)*388))
s.save('stills/sheet_$id.jpg',quality=88); print('sheet', n)"
