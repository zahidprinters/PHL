import os, sys, time, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')
SRC = '/dev/mmcblk0'   # eMMC (read-only source)
DST = '/dev/mmcblk1'   # SD card (destination)
SRC_BYTES = 7818182656

# Safety: confirm destination is the big removable SD, not the eMMC; unmount it; launch dd.
SETUP = r'''
set -e
echo "=== identify devices ==="
lsblk -o NAME,SIZE,RM,MOUNTPOINT /dev/mmcblk0 /dev/mmcblk1
SRCSZ=$(blockdev --getsize64 /dev/mmcblk0)
DSTSZ=$(blockdev --getsize64 /dev/mmcblk1)
echo "src_bytes=$SRCSZ dst_bytes=$DSTSZ"
if [ "$SRCSZ" -ne %d ]; then echo "ABORT: eMMC size unexpected"; exit 3; fi
if [ "$DSTSZ" -lt "$SRCSZ" ]; then echo "ABORT: SD smaller than eMMC"; exit 4; fi
echo "=== unmount any SD mounts ==="
for m in $(mount | grep '/dev/mmcblk1' | awk '{print $1}'); do umount "$m" && echo "umounted $m"; done
mount | grep '/dev/mmcblk1' || echo "no mmcblk1 mounts"
echo "=== launching background clone ==="
rm -f /tmp/clone.log
nohup sh -c 'dd if=/dev/mmcblk0 of=/dev/mmcblk1 bs=4M conv=fsync 2>/tmp/clone.log; echo "EXIT=$?" >> /tmp/clone.log; echo "CLONE_DONE" >> /tmp/clone.log' >/dev/null 2>&1 &
sleep 2
echo "launched pid $!"
''' % SRC_BYTES

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username='root', password=PW, timeout=20,
          look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = c.exec_command(SETUP, timeout=120)
print(stdout.read().decode('utf-8', 'replace'))
err = stderr.read().decode('utf-8', 'replace')
if err.strip():
    print('--- stderr ---')
    print(err)
c.close()
