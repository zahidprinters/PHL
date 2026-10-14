import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
echo "ALIVE"; uptime
echo "=== clone.log ==="
cat /tmp/clone.log 2>/dev/null || echo "(no log)"
echo "=== dd proc ==="
pgrep -af 'dd if=/dev/mmcblk0' || echo NO_DD
echo "=== sd size now ==="
blockdev --getsize64 /dev/mmcblk1 2>/dev/null
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
