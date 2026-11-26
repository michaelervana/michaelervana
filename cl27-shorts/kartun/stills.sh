#!/bin/bash
# stills at the middle of each shot for one story, plus a contact sheet
cd "$(dirname "$0")"; id=$1
F=$(node -e "const T=require('./timing.json')['$id'];const fr=T.lines.map((l,i)=>Math.round(((l.t0+l.t1)/2)*30));fr.push(Math.round(9.4*30),Math.round(T.dur*30)-5);console.log(fr.join(','))")
rm -rf stills/$id; node render.js $id stills/$id "$F" 2>&1 | grep -E "PAGEERROR|FATAL|error" | head -3
python3 -I -c "
from PIL import Image; import glob
fs=sorted(glob.glob('stills/$id/*.jpg')); ims=[Image.open(f).resize((216,384)) for f in fs]
s=Image.new('RGB',(5*220,2*388),(0,0,0))
for i,im in enumerate(ims): s.paste(im,((i%5)*220,(i//5)*388))
s.save('stills/sheet_$id.jpg',quality=85)"
