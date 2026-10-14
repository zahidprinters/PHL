import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
echo "=== clone.log tail ==="
tail -4 /tmp/clone.log 2>/dev/null
echo "=== done markers ==="
grep -E 'EXIT=|CLONE_DONE' /tmp/clone.log 2>/dev/null || echo "markers not present yet (fsync?)"
echo "=== dd still running? ==="
pgrep -f 'dd if=/dev/mmcblk0' >/dev/null && echo "DD_RUNNING" || echo "DD_FINISHED"
echo "=== load ==="
uptime
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
