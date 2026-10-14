# MCP7940N RTC register dump (read-only C probe) + 93LC66A ownership evidence.
import paramiko, time

LOCAL_C = r'd:\phl\tools\mcp7940_dump.c'

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for attempt in range(6):
    try:
        c.connect('192.168.100.127', 22, username='root', password='pakistan',
                  timeout=15, banner_timeout=20, auth_timeout=20)
        print('connected on attempt %d' % (attempt + 1))
        break
    except Exception as ex:
        print('attempt %d failed: %s' % (attempt + 1, ex))
        time.sleep(4)
else:
    raise SystemExit('could not connect after 6 attempts')


def r(cmd, t=30):
    i, o, e = c.exec_command(cmd, timeout=t)
    return (o.read() + e.read()).decode('utf8', 'replace')


sftp = c.open_sftp()
sftp.put(LOCAL_C, '/root/mcp7940_dump.c')
sftp.close()
print('=== upload ===\nuploaded /root/mcp7940_dump.c')

print('=== compile ===')
print(r('which gcc g++ cc 2>&1; gcc -std=gnu99 -o /root/mcp7940_dump '
        '/root/mcp7940_dump.c 2>&1 && echo COMPILED_OK || '
        '{ echo "gcc failed, trying g++"; g++ -std=gnu99 -x c -o /root/mcp7940_dump '
        '/root/mcp7940_dump.c 2>&1 && echo COMPILED_OK_GXX; }'))

print('=== MCP7940N register dump (read-only) ===')
print(r('/root/mcp7940_dump 2>&1'))

sections = [
    ("dmesg rtc / hctosys",
     "dmesg | grep -iE 'rtc|hctosys' | head -20"),

    ("/sys/class/rtc + sysfs attrs",
     "ls -l /sys/class/rtc/ 2>&1; "
     "for f in name date time epoch wakealarm since; do "
     "echo -n \"  rtc0/$f: \"; cat /sys/class/rtc/rtc0/$f 2>&1 | head -1; done"),

    ("every RTC driver in kernel config",
     "zcat /proc/config.gz | grep -E 'CONFIG_RTC_DRV|CONFIG_RTC_HCTOSYS'"),

    ("who sets the clock at boot",
     "grep -rl hwclock /etc/init.d /etc/rcS.d /etc/rc.local 2>/dev/null | head; "
     "grep -h hwclock /etc/init.d/* /etc/rcS.d/* 2>/dev/null | head -5; "
     "echo '--- rc.local ---'; cat /etc/rc.local 2>/dev/null | head -15"),

    ("usb devices (lsusb)",
     "lsusb 2>&1"),

    ("eth0 driver + MAC + smsc95xx config",
     "cat /sys/class/net/eth0/address 2>&1; "
     "readlink -f /sys/class/net/eth0/device/driver 2>&1; "
     "zcat /proc/config.gz | grep -iE 'SMSC95|USB_NET' | head -10; "
     "dmesg | grep -iE 'smsc|95xx|lan95|usbnet|eth0:' | head -15"),

    ("usb device ids from sysfs",
     "for d in /sys/bus/usb/devices/*; do "
     "v=$(cat $d/idVendor 2>/dev/null); p=$(cat $d/idProduct 2>/dev/null); "
     "n=$(cat $d/product 2>/dev/null); "
     "[ -n \"$v\" ] && echo \"  $v:$p $n\"; done"),

    ("eeprom mentions anywhere in kernel boot log",
     "dmesg | grep -iE 'eeprom|93c|macb|eep' | head -10"),

    ("can ethtool dump the LAN9512 eeprom?",
     "which ethtool; ethtool -i eth0 2>&1 | head -8; "
     "echo '--- eeprom dump attempt (read-only) ---'; "
     "ethtool -e eth0 2>&1 | head -25"),

    ("who sets the system clock (rtc read fails, yet date said 2026)",
     "date; uptime; echo '--- adjtime ---'; cat /etc/adjtime 2>&1; "
     "echo '--- init.d list ---'; ls /etc/init.d/ 2>&1; "
     "echo '--- ntp processes ---'; ps 2>/dev/null | grep -iE 'ntp|chrony|timesync' | grep -v grep; "
     "echo '--- hwclock in init scripts ---'; grep -l hwclock /etc/init.d/* 2>/dev/null"),
]

for title, cmd in sections:
    print('\n=== %s ===' % title)
    print(r(cmd).rstrip())

c.close()

