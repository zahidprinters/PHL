"""Vendor-board VNC diagnosis: is a VNC server running, X alive, port 5900 open?
Read-only SSH survey."""
import os
import sys

import paramiko

pw = os.environ.get('PHL_BOARD_PASS', 'pakistan')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.100.127', username='root', password=pw, timeout=10)
cmds = [
    'ps aux | grep -Ei "vnc|x11vnc|vino|Xorg|xinit|gdm|lightdm|lxsession|startx" | grep -v grep',
    'netstat -lntp 2>/dev/null | head -30',
    'ls -la /tmp/.X11-unix/ 2>/dev/null; echo ---; ls /home 2>/dev/null',
    'tail -20 /var/log/Xorg.0.log 2>/dev/null || echo no-Xorg-log',
    'runlevel; who -a | head -5',
    'dpkg -l | grep -Ei "vnc|xserver" | head -10',
    'grep -rE "VNC|vnc" /etc/init/ 2>/dev/null | head; ls /etc/init/ | head -30',
    'iptables -L -n 2>/dev/null | head -15',
]
for cmd in cmds:
    print('=== ' + cmd[:90])
    try:
        i, o, e = c.exec_command(cmd, timeout=15)
        out = o.read().decode(errors='replace').strip()
        print(out[:2500] if out else '(empty)')
        err = e.read().decode(errors='replace').strip()
        if err:
            print('[stderr] ' + err[:300])
    except Exception as ex:
        print('[fail] %s' % ex)
c.close()
