import os, time, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')

def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username='root', password=PW, timeout=8,
              look_for_keys=False, allow_agent=False)
    return c

# 1) fire the reboot (backgrounded so our channel closes cleanly)
print('sending reboot...')
try:
    c = connect()
    c.exec_command('sync; (sleep 2; reboot) >/dev/null 2>&1 &')
    c.close()
    print('  reboot issued')
except Exception as e:
    print('  reboot send error (continuing to poll):', e)

# 2) poll until the board is back
print('waiting for board to return (up to ~180s)...')
back = False
for i in range(36):
    time.sleep(5)
    try:
        c = connect()
        i2, o, e = c.exec_command('uptime; echo READY', timeout=10)
        out = o.read().decode('utf-8', 'replace').strip()
        c.close()
        if 'READY' in out:
            print('  board back after ~%ds: %s' % ((i + 1) * 5, out.splitlines()[0]))
            back = True
            break
    except Exception:
        pass
if not back:
    print('  board did NOT return within 180s - check HDMI / power, then tell me.')
    raise SystemExit(1)
