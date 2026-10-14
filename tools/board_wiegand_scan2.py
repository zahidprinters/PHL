#!/usr/bin/env python
"""Second Wiegand swallow-scan: the events writeEvent() drops (types 2-4).

Phase C fills the struct with plausible payloads (all-0x01, a 26-bit card
number, card+length combos); Phase E tries the setReadEvent() path instead.
Everything runs under nullwrite.so: the STM8 receives nothing.

    $env:PHL_BOARD_PASS = '<password>'
    python tools\\board_wiegand_scan2.py [--out docs/raw/wiegand-frames2-raw.md]
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")

CMDS = [
    ("=== build ema_wscan2 ===",
     "cd /root && g++ -std=c++0x -O0 -o ema_wscan2 ema_wscan2.cpp "
     "-I/usr/include/qt4 -I/usr/include/qt4/QtCore "
     "-L/usr/local/lib -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread 2>&1 && echo BUILD-OK"),

    ("=== run under the shim: NOTHING TRANSMITTED ===",
     "cd /root && LD_PRELOAD=./nullwrite.so ./ema_wscan2 2>&1"),
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

    sftp = c.open_sftp()
    try:
        sftp.put("tools/ema_wscan2.cpp", "/root/ema_wscan2.cpp")
        print("uploaded tools/ema_wscan2.cpp -> /root/ema_wscan2.cpp")
    except Exception as exc:
        print("UPLOAD FAILED: %s" % exc)
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
        print(text[:4000])
        if len(text) > 4000:
            print("... [%d more chars]" % (len(text) - 4000))
        print()
        chunks.append("%s\n\n%s\n" % (label, text))

    c.close()

    if out_path:
        with open(out_path, "w") as fh:
            fh.write("# Wiegand frames, second pass - swallowed capture (raw)\n\n")
            fh.write("Board: %s  Method: ema_wscan2.cpp under nullwrite.so\n" % HOST)
            fh.write("NOTHING was transmitted to the STM8 in this run.\n\n")
            fh.write("\n".join(chunks))
        print("written: %s" % out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
