"""Why did VNC die on the board: session state, vino/tightvnc configs, autostart,
IPv6 address. Read-only SSH survey."""
import os

import paramiko

pw = os.environ.get('PHL_BOARD_PASS', 'pakistan')
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('192.168.100.127', username='root', password=pw, timeout=10)
cmds = [
    'ps aux | grep -Ei "gnome-session|lxsession|xfce|mate|session-child|vino|x11vnc|Xvnc|tight" | grep -v grep',
    'ls -la /root/.vnc/ 2>/dev/null || echo no-root-.vnc; echo ---; ls -la /home/linaro/.vnc/ 2>/dev/null || echo no-linaro-.vnc',
    'grep -a vnc /root/.bash_history 2>/dev/null | tail -15 || echo no-root-history; echo ---; grep -a vnc /home/linaro/.bash_history 2>/dev/null | tail -15 || echo no-linaro-history',
    'ls /etc/xdg/autostart/ | grep -Ei "vnc|vino"; echo ---; ls -la /root/.gconf/apps/vino/ 2>/dev/null || echo no-gconf-vino; ls -la /root/.config/vino* 2>/dev/null',
    'which vino-server Xvnc vncserver x11vnc 2>/dev/null; echo ---; dpkg -l | grep -Ei "vino|vnc" | head',
    'ip -6 addr show scope link | grep -E "inet6|^[0-9]"',
    'netstat -lntp | grep 5900 || echo NO-5900-LISTENER',
    'ls -la /root/.vnc/*.log 2>/dev/null && tail -30 /root/.vnc/*.log 2>/dev/null || echo no-vnc-logs',
]
for cmd in cmds:
    print('=== ' + cmd[:95])
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
