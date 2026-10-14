import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')
SD_HASH = '1d96ad78210c6a45a228c29baf561f491a6ce43ea3d915d7daccb5ded2dd948b'

CMD = r'''
echo "=== rw mounts on eMMC (mmcblk0) ==="
mount | grep mmcblk0
echo "=== what is writable under / ==="
for d in /var /var/log /etc /media/boot /home; do
  if mountpoint -q "$d" 2>/dev/null; then m=$(mount | grep " $d " | awk '{print $1, $6}'); echo "$d -> $m"; fi
done
echo "=== launch eMMC hash now (T2) ==="
rm -f /tmp/emmc_hash.log
nohup sh -c 'dd if=/dev/mmcblk0 bs=4M count=1864 2>/dev/null | sha256sum > /tmp/emmc_hash.log; echo DONE >> /tmp/emmc_hash.log' >/dev/null 2>&1 &
sleep 1
echo "emmc hash launched"
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username='root', password=PW, timeout=20,
          look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = c.exec_command(CMD, timeout=40)
print(stdout.read().decode('utf-8', 'replace'))
err = stderr.read().decode('utf-8', 'replace')
if err.strip():
    print('--- stderr ---'); print(err)
c.close()
print('SD_HASH_NOW = %s' % SD_HASH)
