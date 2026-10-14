"""Dump CMIMIRDemo's disassembly and relocations for offline analysis.

Everything here is READ-ONLY against /usr/local/bin/CMIMIRDemo. Nothing in the
vendor area is modified -- the user has one board and these files cannot be
reinstalled, so they are only ever read.

A local copy already exists in vendor-backup/ from tools/vendor_backup.py, so
this can be run against that instead if the vendor path ever becomes
unavailable.

Two artefacts are produced:

  relocations.txt  the dynamic relocations, which tell us the GOT slot for each
                   imported symbol. Mapping GOT -> PLT stub -> call site is what
                   turns a stripped binary's anonymous `.plt` calls back into
                   named ones.
  disasm.txt       the full disassembly of .text and .plt, for searching.

    $env:PHL_BOARD_PASS = '<password>'
    python tools/vendor_disasm.py [--out <dir>]
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")
BIN = "/usr/local/bin/CMIMIRDemo"

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "vendor-backup")

# Generated on the board in /tmp, then pulled. objdump on a 126 KB binary emits
# megabytes, so it is written to a file rather than streamed through the shell.
CMDS = [
    ("relocations for the ema_* imports",
     "readelf -r %s 2>/dev/null | grep -i ema" % BIN),

    ("dynamic symbols for ema_*",
     "readelf -sW --dyn-syms %s 2>/dev/null | grep -i ema" % BIN),

    ("section headers, to know .plt size and .text size",
     "readelf -SW %s 2>/dev/null | grep -E '\\.text|\\.plt|\\.rel\\.plt|\\.got'" % BIN),
]


def run(c, cmd, timeout=300):
    """Run one shell command on the board and return its output as text."""
    _, out, err = c.exec_command(cmd, timeout=timeout)
    text = (out.read() or b"").decode("utf-8", "replace")
    e = (err.read() or b"").decode("utf-8", "replace")
    return text if text else e


def main():
    """Pull relocations and the full disassembly to vendor-backup/."""
    password = os.environ.get("PHL_BOARD_PASS")
    if not password:
        print("Set PHL_BOARD_PASS first.")
        return 1
    if "--out" in sys.argv:
        global OUT
        OUT = sys.argv[sys.argv.index("--out") + 1]

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(HOST, port=PORT, username=USER, password=password, timeout=25,
                  allow_agent=False, look_for_keys=False)
    except OSError as err:
        print(f"CONNECT FAILED - {err}")
        return 3

    os.makedirs(OUT, exist_ok=True)

    for label, cmd in CMDS:
        print(label)
        print(run(c, cmd))
        print()

    print("=== generating disassembly on the board (read-only) ===")
    # force-thumb is essential: the binary interworks and the real functions are
    # Thumb-2. Without it objdump decodes .text as ARM and emits nothing but
    # "UNDEFINED instruction", which looks like a corrupt dump but is not.
    run(c, "objdump -d -M force-thumb %s > /tmp/cmimir.disasm 2>/dev/null; "
           "readelf -r %s > /tmp/cmimir.relocs 2>/dev/null; "
           "wc -c /tmp/cmimir.disasm /tmp/cmimir.relocs" % (BIN, BIN))
    print(run(c, "wc -c /tmp/cmimir.disasm /tmp/cmimir.relocs 2>/dev/null"))
    print(run(c, "grep -c 'UNDEFINED' /tmp/cmimir.disasm 2>/dev/null "
                 "| sed 's/^/undefined-instruction lines: /'"))

    for remote, local in (("/tmp/cmimir.disasm", "disasm.txt"),
                          ("/tmp/cmimir.relocs", "relocations.txt")):
        try:
            sftp = c.open_sftp()
            sftp.get(remote, os.path.join(OUT, local))
            sftp.close()
            size = os.path.getsize(os.path.join(OUT, local))
            print(f"pulled {remote} -> {local} ({size} bytes)")
        except Exception as err:
            print(f"pull {remote} failed: {err}")

    c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())