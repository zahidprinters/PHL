import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
PID=$(pgrep -f 'dd if=/dev/mmcblk0' | head -1)
echo "dd pid=$PID"
if [ -n "$PID" ]; then
  echo "state: $(cat /proc/$PID/stat 2>/dev/null | awk '{print $3}')"
  echo "wchan: $(cat /proc/$PID/wchan 2>/dev/null)"
  echo "--- io ---"
  cat /proc/$PID/io 2>/dev/null
fi
echo "=== markers ==="
grep -E 'EXIT=|CLONE_DONE' /tmp/clone.log 2>/dev/null || echo "still flushing"
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
