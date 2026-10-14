"""Restore board VNC (take 2): vino 3.4.2 on GNOME3 reads GSettings/dconf.
Set org.gnome.Vino keys via the session bus, start vino, verify RFB."""
import os
import socket
import time

import paramiko

pw = os.environ.get('PHL_BOARD_PASS', 'pakistan')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.100.127', username='root', password=pw, timeout=10)


def sh(cmd, t=20):
    i, o, e = c.exec_command(cmd, timeout=t)
    return o.read().decode(errors='replace').strip(), e.read().decode(errors='replace').strip()


out, _ = sh("pid=$(pgrep -f 'gnome-session --session=ubuntu' | head -1); "
            "tr '\\0' '\\n' < /proc/$pid/environ | sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p'")
bus = out.splitlines()[0] if out else ''
print('bus:', (bus[:80] + '...') if bus else 'NOT FOUND')
env = "DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS='%s'" % bus

print('=== gsettings vino schema?')
out, _ = sh('%s gsettings list-schemas 2>/dev/null | grep -i vino' % env)
print(out or 'NO-GSETTINGS-SCHEMA')
has_schema = bool(out)

if has_schema:
    print('=== keys:')
    out, _ = sh('%s gsettings list-keys org.gnome.Vino' % env)
    print(out)
    wanted = {
        'enabled': 'true',
        'view-only': 'false',
        'require-encryption': 'false',
        'network-enabled': 'true',
    }
    for k, v in wanted.items():
        if k in out.split():
            o1, e1 = sh('%s gsettings set org.gnome.Vino %s %s' % (env, k, v))
            print('  set %s = %s  %s' % (k, v, 'ok' if not e1 else 'ERR ' + e1[:70]))
    print('=== read back enabled:')
    out, _ = sh('%s gsettings get org.gnome.Vino enabled' % env)
    print('  enabled =', out)
else:
    print('=== gconf readback via session bus (debug):')
    out, _ = sh('%s gconftool-2 -R /apps/vino/server 2>/dev/null | head -30' % env)
    print(out)

print('=== starting vino-server:')
sh('%s nohup /usr/lib/vino/vino-server >/tmp/vino.log 2>&1 &' % env)
time.sleep(4)
out, _ = sh('cat /tmp/vino.log; echo ---; netstat -lntp | grep 5900 || echo NO-5900')
print(out)
c.close()

print('=== RFB probe from PC ...')
try:
    s = socket.create_connection(('192.168.100.127', 5900), timeout=5)
    banner = s.recv(32).decode(errors='replace')
    s.close()
    print('banner: %r' % banner)
    print('VNC-RESTORED-OK' if banner.startswith('RFB') else 'VNC-UNEXPECTED-BANNER')
except OSError as ex:
    print('probe failed: %s' % ex)
    print('VNC-RESTORE-FAILED')
