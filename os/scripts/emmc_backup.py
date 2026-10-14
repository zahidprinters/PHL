import os, sys, gzip, hashlib, time, paramiko

HOST = '192.168.100.127'
PW = os.environ.get('PHL_BOARD_PASS', '')
OUT = r'd:\phl\os\backup-eMMC\emmc_backup.img.gz'
LOG = r'd:\phl\os\backup-eMMC\emmc_backup.log'
EXPECT = 7818182656  # full eMMC size in bytes

def log(msg):
    line = '[%s] %s' % (time.strftime('%H:%M:%S'), msg)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

# Full raw clone of the eMMC user area; gzip ON THE BOARD (root is ro -> consistent).
# Compressing before the wire keeps a 100 Mbit link busy: ~2 GB crosses instead of 7.8 GB raw.
CMD = 'dd if=/dev/mmcblk0 bs=4M 2>/tmp/dd.err | gzip -1; cat /tmp/dd.err >&2'


log('connecting to %s' % HOST)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username='root', password=PW, timeout=20,
          look_for_keys=False, allow_agent=False)

stdin, stdout, stderr = c.exec_command(CMD, timeout=7200)
h = hashlib.sha256()          # hash of the COMPRESSED stream (transfer integrity)
total = 0
t0 = time.time()
last = 0
with open(OUT, 'wb') as f:    # board already gzipped; write bytes as-is
    while True:
        chunk = stdout.read(1024 * 1024)
        if not chunk:
            break
        f.write(chunk)
        h.update(chunk)
        total += len(chunk)
        now = time.time()
        if now - last >= 5:
            last = now
            log('%.2f GB compressed  (%.1f MB/s)' % (total / 1e9, total / (now - t0) / 1e6))

err = stderr.read().decode('utf-8', 'replace')
c.close()

log('DONE compressed_bytes=%d sha256_gz=%s' % (total, h.hexdigest()))
log('dd_stderr: %s' % err.strip())
