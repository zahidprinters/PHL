import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

SCRIPT = r'''#!/bin/bash
set -u
DEV=/dev/mmcblk0
NEWP=${DEV}p3
MNT=/data
LABEL=data

echo "=== force kernel to re-read partition table (p3 already written to disk) ==="
partprobe $DEV 2>/dev/null; sleep 1
[ -b "$NEWP" ] || { partx -va $DEV 2>/dev/null; sleep 1; }
[ -b "$NEWP" ] || { blockdev --rereadpt $DEV 2>/dev/null; sleep 1; }

if [ ! -b "$NEWP" ]; then
  echo "  $NEWP STILL not visible (kernel uses old table)."
  echo "  The entry is on disk; it will appear after a REBOOT."
  echo "  -> Reboot the board, then re-run this script to format+mount."
  exit 2
fi
echo "  $NEWP is now visible"

echo "=== verify geometry (p2 must be untouched, p3 fills the card) ==="
fdisk -l $DEV 2>/dev/null | grep -E 'mmcblk0p[123]'
P2END=$(fdisk -l $DEV 2>/dev/null | awk '/mmcblk0p2/{print $3}')
if [ "$P2END" = "11532287" ]; then
  echo "  p2 end=11532287 unchanged -> SAFE"
else
  echo "  ERROR: p2 end=$P2END (expected 11532287) - ABORT"; exit 1
fi

echo "=== mkfs.ext4 (LABEL=$LABEL) on $NEWP ==="
if blkid $NEWP >/dev/null 2>&1 && [ -n "$(blkid -s TYPE -o value $NEWP)" ]; then
  echo "  already has filesystem ($(blkid -s TYPE -o value $NEWP)) - skip mkfs"
else
  mkfs.ext4 -F -L $LABEL $NEWP || { echo "MKFS FAILED"; exit 1; }
fi

echo "=== mount /data ==="
mkdir -p $MNT
if grep -qE "[[:space:]]$MNT[[:space:]]" /proc/mounts; then
  echo "  already mounted"
else
  mount $NEWP $MNT || { echo "MOUNT FAILED"; exit 1; }
  echo "  mounted"
fi

echo "=== persist in fstab ==="
if grep -qE "[[:space:]]$MNT[[:space:]]" /etc/fstab; then
  echo "  fstab already has $MNT"
else
  echo "LABEL=$LABEL  $MNT  ext4  defaults,noatime  0 2" >> /etc/fstab
  echo "  added fstab entry"
fi

echo
echo "=== RESULT ==="
blkid $NEWP
echo
df -h $MNT
echo
echo "=== fstab tail ==="
tail -3 /etc/fstab
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username='root', password=PW, timeout=20,
          look_for_keys=False, allow_agent=False)
sftp = c.open_sftp()
with sftp.open('/tmp/mkdata_resume.sh', 'wb') as f:
    f.write(SCRIPT.replace('\r\n', '\n').encode('utf-8'))
sftp.close()
i, o, e = c.exec_command('bash /tmp/mkdata_resume.sh 2>&1', timeout=180)
print(o.read().decode('utf-8', 'replace'))
err = e.read().decode('utf-8', 'replace')
if err.strip():
    print('--- stderr ---'); print(err)
c.close()
