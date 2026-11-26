cd "$(dirname "$0")"
( RESUME=1 node render.js realmadrid frames/realmadrid 0-1080 > logs/a.log 2>&1 ) &
( RESUME=1 node render.js realmadrid frames/realmadrid 1081-1700 > logs/b.log 2>&1; RESUME=1 node render.js barcelona frames/barcelona 0-520 >> logs/b.log 2>&1 ) &
( RESUME=1 node render.js barcelona frames/barcelona 521-1600 > logs/c.log 2>&1 ) &
wait; echo ALLDONE > logs/done
