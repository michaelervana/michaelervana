#!/bin/bash
cd "$(dirname "$0")"
./render_all.sh parkirbus 66 3 > logs/run_parkirbus.log 2>&1
./render_all.sh tikitaka 66 3 > logs/run_tikitaka.log 2>&1
echo ALLDONE > logs/alldone
