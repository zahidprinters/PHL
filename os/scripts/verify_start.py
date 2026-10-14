import os, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')
EXPECT_HASH = '70b758114c2eb03cab45228aa14f5dc1b7519c37bededd3a107cebb040e305f0'

# Hash the SD card's first 1864*4M = 7818182656 bytes (exactly the eMMC image size).
LAUNCH = r'''
rm -f /tmp/verify.log
nohup sh -c 'dd if=/dev/mmcblk1 bs=4M count=1864 2>/dev/null | sha256sum > /tmp/verify.log; echo "VERIFY_DONE" >> /tmp/verify.log' >/dev/null 2>&1 &
sleep 1
echo "verify launched"
'''

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username='root', password=PW, timeout=20,
          look_for_keys=False, allow_agent=False)
stdin, stdout, stderr = c.exec_command(LAUNCH, timeout=30)
print(stdout.read().decode('utf-8', 'replace'))
c.close()
print('expect_hash = %s' % EXPECT_HASH)
