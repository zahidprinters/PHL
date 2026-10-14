import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

SCRIPT = r'''#!/bin/bash
set -u
DEV=/dev/mmcblk0
NEWP=${DEV}p3
MNT=/data
LABEL=data

echo "=== tool check ==="
missing=0
for t in fdisk mkfs.ext4 blkid; do
  if command -v $t >/dev/null 2>&1; then echo "  have $t"; else echo "  MISSING $t"; missing=1; fi
done
[ $missing -eq 0 ] || { echo "ABORT: required tool missing"; exit 1; }

# record p2 end before, to prove it is untouched
P2_BEFORE=$(fdisk -l $DEV 2>/dev/null | awk '/mmcblk0p2/{print $2"-"$3}')

echo "=== idempotency: does p3 already exist? ==="
if [ -b "$NEWP" ]; then
  echo "  $NEWP already exists -> skip create/mkfs, go to mount+fstab"
else
  echo "=== geometry ==="
  TS=$(fdisk -l $DEV 2>/dev/null | awk '/total [0-9]+ sectors/{print $(NF-1)}')
  P2END=$(fdisk -l $DEV 2>/dev/null | awk '/mmcblk0p2/{print $3}')
  echo "  total sectors=$TS  p2 end=$P2END"
  START=$(( ((P2END + 2048) / 2048) * 2048 ))   # next 1MiB-aligned sector after p2
  echo "  new p3: start=${START}s  end=default(last sector $((TS-1)))"

  echo "=== backup fstab ==="
  cp -a /etc/fstab /etc/fstab.bak.$(date +%s) && echo "  backed up (/etc/fstab.bak.*)"

  echo "=== create p3 via fdisk (adds one partition in free space; p1/p2 preserved) ==="
  printf 'n\np\n\n%s\n\nw\n' "$START" | fdisk $DEV >/tmp/fdisk.out 2>&1
  rc=$?
  sed 's/^/  fdisk| /' /tmp/fdisk.out
  [ $rc -eq 0 ] || { echo "FDISK FAILED rc=$rc"; exit 1; }

  echo "=== re-read partition table ==="
  partprobe $DEV 2>/dev/null; sleep 1
  [ -b "$NEWP" ] || { partx -a $DEV 2>/dev/null; sleep 1; }
  [ -b "$NEWP" ] || { blockdev --rereadpt $DEV 2>/dev/null; sleep 1; }
  if [ ! -b "$NEWP" ]; then
    echo "  ERROR: $NEWP did not appear. Current table:"; fdisk -l $DEV; exit 1
  fi
  echo "  $NEWP present"

  # safety: confirm p2 unchanged before formatting
  P2_AFTER=$(fdisk -l $DEV 2>/dev/null | awk '/mmcblk0p2/{print $2"-"$3}')
  if [ "$P2_BEFORE" = "$P2_AFTER" ]; then
    echo "  p2 unchanged ($P2_AFTER) - safe"
  else
    echo "  ERROR: p2 changed! before=$P2_BEFORE after=$P2_AFTER - ABORT before mkfs"; exit 1
  fi

  echo "=== mkfs.ext4 (LABEL=$LABEL) on $NEWP ==="
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
with sftp.open('/tmp/mkdata.sh', 'wb') as f:
    f.write(SCRIPT.replace('\r\n', '\n').encode('utf-8'))
sftp.close()
i, o, e = c.exec_command('bash /tmp/mkdata.sh 2>&1', timeout=180)
print(o.read().decode('utf-8', 'replace'))
err = e.read().decode('utf-8', 'replace')
if err.strip():
    print('--- stderr ---'); print(err)
c.close()
