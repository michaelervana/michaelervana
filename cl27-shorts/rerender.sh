#!/bin/bash
# After the current batch, re-render the two videos that used the old kick-off clip.
cd "$(dirname "$0")"
until grep -q RENDERDONE out/render2.log; do sleep 20; done
./render.sh cuju larangan1314
