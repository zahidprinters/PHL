import os, sys, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')
USERS = ['root', 'linaro', 'odroid', 'linux']

CMD = r'''
echo "=== whoami ==="; id
echo "=== lsblk ==="; lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINT 2>/dev/null
echo "=== df ==="; df -h 2>/dev/null
echo "=== cmdline (how eMMC boots) ==="; cat /proc/cmdline
echo "=== mmcblk0 partition table ==="; fdisk -l /dev/mmcblk0 2>/dev/null || parted /dev/mmcblk0 unit s print 2>/dev/null
echo "=== mmcblk0 size bytes ==="; blockdev --getsize64 /dev/mmcblk0 2>/dev/null
echo "=== boot files (vfat p1) ==="; ls -la /media/boot 2>/dev/null | head -20
echo "=== usb storage present? ==="; dmesg 2>/dev/null | grep -iE "usb storage|Direct-Access|Attached scsi|sd[0-9]:" | tail -8
echo "=== current block devs ==="; ls -l /dev/mmcblk* /dev/sd* 2>/dev/null
'''

def run(user):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(HOST, username=user, password=PW, timeout=15,
              look_for_keys=False, allow_agent=False)
    stdin, stdout, stderr = c.exec_command(CMD, timeout=90)
    out = stdout.read().decode('utf-8', 'replace')
    err = stderr.read().decode('utf-8', 'replace')
    c.close()
    return out, err

last = None
for u in USERS:
    try:
        out, err = run(u)
        print('### connected as:', u)
        print(out)
        if err.strip():
            print('--- stderr ---')
            print(err)
        sys.exit(0)
    except Exception as e:
        last = '%s: %s' % (u, e)
        continue
print('ALL AUTH FAILED. last:', last)
sys.exit(1)
