#!/bin/bash
# 14 stills spread over the video plus a contact sheet (7 x 2)
cd "$(dirname "$0")"; id=$1
F=$(node -e "const T=require('./timing.json')['$id'];const n=14,fr=[];for(let i=0;i<n;i++)fr.push(Math.round((1.4+i*(T.dur-2)/(n-1))*30));console.log(fr.join(','))")
mkdir -p stills/$id; node render.js $id stills/$id "$F" 2>&1 | grep -E "PAGEERROR|FATAL|error" | head -5
python3 -I -c "
from PIL import Image; import glob
fs=sorted(glob.glob('stills/$id/*.jpg')); ims=[Image.open(f).resize((216,384)) for f in fs]
s=Image.new('RGB',(7*220,2*388),(0,0,0))
for i,im in enumerate(ims[:14]): s.paste(im,((i%7)*220,(i//7)*388))
s.save('stills/sheet_$id.jpg',quality=85)"
