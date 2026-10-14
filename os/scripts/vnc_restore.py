"""Restore the board's VNC (vino sharing display :0) after the reboot.
Enables sharing via the RUNNING gnome session's D-Bus, starts vino-server,
verifies port 5900 + RFB banner, and reports why autostart failed."""
import os
import re
import socket
import time

import paramiko

pw = os.environ.get('PHL_BOARD_PASS', 'pakistan')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.100.127', username='root', password=pw, timeout=10)


def sh(cmd, t=20):
    i, o, e = c.exec_command(cmd, timeout=t)
    out = o.read().decode(errors='replace').strip()
    err = e.read().decode(errors='replace').strip()
    return out, err


print('=== why autostart failed (session log):')
out, _ = sh("grep -i vino /root/.xsession-errors /var/log/lightdm/:0.log 2>/dev/null | tail -10 || echo no-hints")
print(out or '(no log hints)')

print('=== autostart file:')
out, _ = sh('grep -E "^(Exec|Hidden|OnlyShowIn|X-GNOME)" /etc/xdg/autostart/vino-server.desktop')
print(out)

print('=== session D-Bus address:')
out, _ = sh("pid=$(pgrep -f 'gnome-session --session=ubuntu' | head -1); "
            "tr '\\0' '\\n' < /proc/$pid/environ | sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p'")
bus = out.splitlines()[0] if out else ''
print(bus[:120] or '(NOT FOUND)')

env = "DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS='%s'" % bus

print('=== enabling vino via session bus:')
sets = [
    ('/apps/vino/server/enabled', 'boolean', 'true'),
    ('/apps/vino/server/network-enabled', 'boolean', 'true'),
    ('/apps/vino/server/require-encryption', 'boolean', 'false'),
    ('/apps/vino/server/auth-method', 'string', 'none'),
]
for key, typ, val in sets:
    out, err = sh("%s gconftool-2 --set %s --type %s %s" % (env, key, typ, val))
    print('  %s -> %s %s' % (key, 'ok' if not err else 'ERR ' + err[:80], out[:60]))

print('=== starting vino-server:')
sh('%s nohup /usr/lib/vino/vino-server >/tmp/vino.log 2>&1 &' % env)
time.sleep(4)
out, _ = sh('cat /tmp/vino.log; echo ---; netstat -lntp | grep 5900 || echo NO-5900')
print(out)

c.close()

print('=== RFB probe from PC to 192.168.100.127:5900 ...')
try:
    s = socket.create_connection(('192.168.100.127', 5900), timeout=5)
    banner = s.recv(32).decode(errors='replace')
    s.close()
    print('banner: %r' % banner)
    print('VNC-RESTORED-OK' if banner.startswith('RFB') else 'VNC-UNEXPECTED-BANNER')
except OSError as ex:
    print('probe failed: %s' % ex)
    print('VNC-RESTORE-FAILED')
