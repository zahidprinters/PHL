#!/usr/bin/env python
"""Map the Wiegand event frames from the vendor side WITHOUT transmitting.

The five Wiegand enum events (READ_DATA, WRITE_DATA, SET_CONFIG, GET_CONFIG,
AUTO_DETECT - believed types 2..6) have never had a frame mapped. This runs
`ema_wscan.cpp` on the board under the `nullwrite.so` swallowing shim, so
libemaLib builds every frame it intends and the STM8 receives nothing.

Phases captured:
  A  event types 1..10          -> which frame each type emits
  B  struct offset sweep, types 2..6 -> which offset carries the card/data value

Read-only against the STM8: the shim swallows every write() to the serial fd.
Files are written to /root on the board (scratch space, alongside the other
one-off probes).

    $env:PHL_BOARD_PASS = '<password>'
    python tools\\board_wiegand_scan.py

Output is also saved to docs/raw/wiegand-frames-raw.md when --out is given.
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")
BOARD_DIR = "/root"

SCAN_CPP = "tools/ema_wscan.cpp"
SHIM_C = "tools/nullwrite.c"

CMDS = [
    ("=== Wiegand enum strings in CMIMIRDemo ===",
     "strings /usr/local/bin/CMIMIRDemo | grep -i wiegand | sort -u"),

    ("=== build nullwrite.so (swallowing shim) ===",
     "cd /root && gcc -shared -fPIC -O0 -o nullwrite.so nullwrite.c -ldl 2>&1 && echo BUILD-OK"),

    ("=== build ema_wscan ===",
     "cd /root && g++ -std=c++0x -O0 -o ema_wscan ema_wscan.cpp "
     "-I/usr/include/qt4 -I/usr/include/qt4/QtCore "
     "-L/usr/local/lib -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread 2>&1 && echo BUILD-OK"),

    ("=== run under the shim: NOTHING TRANSMITTED ===",
     "cd /root && LD_PRELOAD=./nullwrite.so ./ema_wscan 2>&1"),
]


def main():
    password = os.environ.get("PHL_BOARD_PASS")
    if not password:
        print("Set PHL_BOARD_PASS first.")
        return 1

    out_path = None
    if "--out" in sys.argv:
        out_path = sys.argv[sys.argv.index("--out") + 1]

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(HOST, port=PORT, username=USER, password=password, timeout=20,
                  allow_agent=False, look_for_keys=False)
    except OSError as err:
        print("CONNECT FAILED - %s" % err)
        return 3

    # Upload the scanner and the shim (both live in this repo).
    sftp = c.open_sftp()
    for local in (SCAN_CPP, SHIM_C):
        remote = BOARD_DIR + "/" + os.path.basename(local)
        try:
            sftp.put(local, remote)
            print("uploaded %s -> %s" % (local, remote))
        except Exception as exc:
            print("UPLOAD FAILED %s: %s" % (local, exc))
    sftp.close()

    chunks = []
    for label, cmd in CMDS:
        print(label)
        try:
            _, out, err = c.exec_command(cmd, timeout=600)
            text = (out.read() or b"").decode("utf-8", "replace").strip()
            e = (err.read() or b"").decode("utf-8", "replace").strip()
            text = text if text else (e if e else "(no output)")
        except Exception as exc:
            text = "PROBE FAILED: %s" % exc
        print(text)
        print()
        chunks.append("%s\n\n%s\n" % (label, text))

    c.close()

    if out_path:
        with open(out_path, "w") as fh:
            fh.write("# Wiegand frames - swallowed capture (raw output)\n\n")
            fh.write("Board: %s  Method: ema_wscan.cpp under nullwrite.so\n" % HOST)
            fh.write("NOTHING was transmitted to the STM8 in this run.\n\n")
            fh.write("\n".join(chunks))
        print("written: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
