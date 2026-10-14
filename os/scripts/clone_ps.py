import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
echo "=== all dd / clone procs ==="
ps -eo pid,ppid,stat,wchan:20,args | grep -iE 'dd if|clone|mmcblk1' | grep -v grep
echo "=== clone.log full ==="
cat /tmp/clone.log
echo "=== sync state (is flush ongoing?) ==="
grep -E 'Dirty|Writeback' /proc/meminfo
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
