import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
echo "=== PHYSICAL CARD (mmcblk0 = the SD now) ==="
b=$(blockdev --getsize64 /dev/mmcblk0)
awk -v b="$b" 'BEGIN{printf "  %d bytes = %.1f GB (%.1f GiB)\n", b, b/1e9, b/1073741824}'
echo
echo "=== PARTITION TABLE ==="
fdisk -l /dev/mmcblk0 2>/dev/null
echo
echo "=== USABLE NOW (df) ==="
df -h / /media/boot
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username='root', password=PW, timeout=20,
          look_for_keys=False, allow_agent=False)
i, o, e = c.exec_command(CMD, timeout=40)
print(o.read().decode('utf-8', 'replace'))
err = e.read().decode('utf-8', 'replace')
if err.strip():
    print('--- stderr ---'); print(err)
c.close()
