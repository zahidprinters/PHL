import os, sys, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
PID=$(pgrep -f 'dd if=/dev/mmcblk0' | head -1)
if [ -n "$PID" ]; then
  kill -USR1 "$PID" 2>/dev/null
  echo "dd running (pid $PID)"
else
  echo "dd not running"
fi
sleep 1
echo "=== /tmp/clone.log ==="
cat /tmp/clone.log 2>/dev/null || echo "(no log yet)"
if grep -q CLONE_DONE /tmp/clone.log 2>/dev/null; then echo "STATUS=COMPLETE"; else echo "STATUS=RUNNING"; fi
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
