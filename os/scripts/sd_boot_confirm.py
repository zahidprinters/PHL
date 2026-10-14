import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
echo "=== uptime (fresh boot?) ==="; uptime
echo "=== root device (SD or eMMC?) ==="
findmnt -no SOURCE / 2>/dev/null || (mount | grep ' on / ')
echo "=== by-uuid of root ==="
ls -l /dev/disk/by-uuid/ 2>/dev/null
echo "=== lsblk (which mmc is root, sizes) ==="
lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINT
echo "=== cmdline root= ==="
cat /proc/cmdline | tr ' ' '\n' | grep -i root
echo "=== kernel ==="
uname -a
echo "=== SD writable test (safe playground?) ==="
mount | grep -E ' on / ' 
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username='root', password=PW, timeout=20,
          look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = c.exec_command(CMD, timeout=60)
print(stdout.read().decode('utf-8', 'replace'))
err = stderr.read().decode('utf-8', 'replace')
if err.strip():
    print('--- stderr ---'); print(err)
c.close()
