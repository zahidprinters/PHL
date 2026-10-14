import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

CMD = r'''
echo "=== root device + free space ==="
findmnt -no SOURCE,FSAVAIL,FSUSED,SIZE% /
echo "=== write test on / (SD rootfs) ==="
d=$(mktemp -d //.wtest.XXXXXX) && echo "write-ok: $d" && rmdir "$d" || echo "WRITE-FAIL"
echo "=== EMA_Controls present (full vendor OS on SD)? ==="
ls -l /root/Desktop/EMA_Controls.sh 2>/dev/null && echo "EMA present" || echo "EMA missing"
echo "=== three UARTs present? ==="
ls /dev/ttySAC* 2>/dev/null
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
