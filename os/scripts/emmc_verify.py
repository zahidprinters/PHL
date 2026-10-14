import gzip, hashlib, os

GZ = r'd:\phl\os\backup-eMMC\emmc_backup.img.gz'
EXPECT = 7818182656

h = hashlib.sha256()
total = 0
with gzip.open(GZ, 'rb') as f:
    while True:
        chunk = f.read(4 * 1024 * 1024)
        if not chunk:
            break
        h.update(chunk)
        total += len(chunk)

print('decompressed_bytes = %d' % total)
print('expected_bytes     = %d' % EXPECT)
print('raw_sha256         = %s' % h.hexdigest())
print('SIZE-OK' if total == EXPECT else 'SIZE-MISMATCH')
