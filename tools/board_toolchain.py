"""What do we need to build a caller for libemaLib, and what does its API look like?

The plan for the SoC<->STM8 link is to stop guessing the protocol and use
Daikin's own implementation: libemaLib_arm_1.0.1.so already exports EMAMain,
which speaks EMA to the STM8 over a QextSerialPort. If we can call it, the
framing comes for free.

Two things decide whether that is possible, and this checks both:
  1. Is there a compiler on the board (or cross-tools on this PC)?
  2. What exactly does EMAMain::open() take, and what does _EMA_EVENT look like?
     Mangled C++ names encode the argument count, so nm + demangling tells us
     whether we can call it from a stub without the original headers.

Read-only. Compiles nothing and runs nothing.

    $env:PHL_BOARD_PASS = '<password>'
    python tools/board_toolchain.py
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")

CMDS = [
    ("=== compilers on the board ===",
     "for c in gcc g++ cc arm-linux-gnueabi-gcc arm-linux-gnueabihf-gcc make ld; do "
     "printf '%-30s %s\\n' $c \"$(command -v $c || echo MISSING)\"; done; "
     "echo '--- versions ---'; gcc --version 2>/dev/null | head -1; g++ --version 2>/dev/null | head -1"),

    ("=== binutils / demangler ===",
     "for c in nm objdump readelf c++filt strings file; do "
     "printf '%-12s %s\\n' $c \"$(command -v $c || echo MISSING)\"; done"),

    ("=== EMAMain mangled names (argument counts are encoded here) ===",
     "nm -D --defined-only /usr/local/lib/libemaLib_arm_1.0.1.so 2>/dev/null "
     "| grep -i EMAMain | awk '{print $NF}'"),

    ("=== the same, demangled ===",
     "nm -D --defined-only /usr/local/lib/libemaLib_arm_1.0.1.so 2>/dev/null "
     "| grep -i EMAMain | awk '{print $NF}' | c++filt 2>/dev/null || echo 'c++filt missing'"),

    ("=== every exported symbol (full API surface) ===",
     "nm -D --defined-only /usr/local/lib/libemaLib_arm_1.0.1.so 2>/dev/null | awk '{print $NF}' | head -60"),

    ("=== any EMA type/struct/enum symbols ===",
     "nm -D /usr/local/lib/libemaLib_arm_1.0.1.so 2>/dev/null | grep -iE 'EMA|event|type' | awk '{print $NF}' | head -30"),

    ("=== are there headers or a sample anywhere on the board? ===",
     "find / -xdev \\( -iname '*ema*.h' -o -iname '*cmimir*' -o -iname '*ema*.cpp' \\) 2>/dev/null | head -20; "
     "echo '--- /usr/local/include ---'; ls /usr/local/include/ 2>/dev/null || echo 'none'; "
     "echo '--- /usr/local/src or similar ---'; ls /usr/local/ 2>/dev/null"),

    ("=== library dependencies: can we link a stub against it? ===",
     "objdump -p /usr/local/lib/libemaLib_arm_1.0.1.so 2>/dev/null | grep NEEDED; "
     "echo '--- is it stripped? ---'; file /usr/local/lib/libemaLib_arm_1.0.1.so; "
     "echo '--- SONAME ---'; objdump -p /usr/local/lib/libemaLib_arm_1.0.1.so 2>/dev/null | grep SONAME"),
]
def main():
    """Report the build capability and the EMAMain API shape."""
    password = os.environ.get("PHL_BOARD_PASS")
    if not password:
        print("Set PHL_BOARD_PASS first.")
        return 1

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(HOST, port=PORT, username=USER, password=password, timeout=20,
                  allow_agent=False, look_for_keys=False)
    except OSError as err:
        print(f"CONNECT FAILED - {err}")
        return 3

    for label, cmd in CMDS:
        print(label)
        try:
            _, out, err = c.exec_command(cmd, timeout=180)
            text = (out.read() or b"").decode("utf-8", "replace").strip()
            e = (err.read() or b"").decode("utf-8", "replace").strip()
            print(text if text else (e if e else "(no output)"))
        except Exception as exc:
            print(f"PROBE FAILED: {exc}")
        print()

    c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())