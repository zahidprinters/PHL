#!/bin/sh
# Restart the kiosk browser with the X env the SSH exec session lacks.
export DISPLAY=:0
export XAUTHORITY=/root/.Xauthority
killall firefox 2>/dev/null
sleep 3
setsid nohup firefox 'http://localhost:1880/' >/root/ff.log 2>&1 < /dev/null &
exit 0
