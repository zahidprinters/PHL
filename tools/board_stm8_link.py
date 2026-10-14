"""Focused probe: what IS /dev/ttySTM8, and where are the missing peripherals?

Follows the board_inventory.py survey, which found a device nobody had noticed:
/dev/ttySTM8 -- a kernel-provided tty whose name says exactly which chip it talks
to. If it is the SoC<->STM8S207 link, every GPI/GPO/relay/Wiegand operation the
board is capable of is reachable through it without Daikin's GUI.

Also chases the two loose ends the survey could not settle:
  * two RJ45 sockets but one interface (the other may have no driver at all)
  * two 93LC66A EEPROMs that are on no I2C bus Linux can see

Read-only. Opens nothing, writes nothing.

    $env:PHL_BOARD_PASS = '<password>'
    python tools/board_stm8_link.py
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")

CMDS = [
    ("=== /dev/ttySTM8 : what created it? ===",
     "ls -l /dev/ttySTM8; echo '--- driver binding ---'; "
     "ls -l /sys/class/tty/ttySTM8/device/driver 2>/dev/null; "
     "ls -l /sys/class/tty/ttySTM8/ 2>/dev/null; "
     "readlink -f /sys/class/tty/ttySTM8/device 2>/dev/null"),

    ("=== registered serial drivers (which one claims it) ===",
     "cat /proc/tty/drivers 2>/dev/null; echo '--- per-tty uart:unknown lines ---'; "
     "cat /proc/tty/driver/serial 2>/dev/null | head -20"),

    ("=== udev rules / init scripts mentioning ttySTM8 ===",
     "grep -rl 'ttySTM8' /etc/udev /lib/udev /etc/init.d /etc/rc* 2>/dev/null | head; "
     "grep -rn 'ttySTM8' /etc/udev/rules.d/ /lib/udev/rules.d/ 2>/dev/null | head -10"),

    ("=== which kernel module provides the name ===",
     "lsmod | head -30; echo '--- any vendor/vendorso module ---'; "
     "lsmod | grep -viE '^(Module|Cat|Used)' | tail -20"),

    ("=== is anything holding ttySTM8 right now ===",
     "fuser /dev/ttySTM8 2>&1; echo '--- lsof ---'; lsof /dev/ttySTM8 2>/dev/null || true; "
     "echo '--- vendor processes ---'; ps aux | grep -iE '[C]MIMIR|[c]miris|[e]ma' | grep -v grep"),

    ("=== the second RJ45: any unclaimed ethernet at all ===",
     "dmesg | grep -iE 'macb|dwmac|ethernet|gmace|eth[01]|smsc|9512' | tail -25; "
     "echo '--- every NIC-like device tree node, any depth ---'; "
     "find /proc/device-tree -name 'ethernet*' -o -name 'gmac*' 2>/dev/null | head; "
     "echo '--- kernel config: is dwmac/macb even built? ---'; "
     "zcat /proc/config.gz 2>/dev/null | grep -iE 'DW_MACB|SAMSUNG_DWCMC|STMMAC|SMSC95' || echo 'no config.gz match'"),

    ("=== USB topology: where does each RJ45 hang ===",
     "dmesg | grep -E '1-2|hub 1|usb 1-' | tail -20; "
     "echo '--- lsusb tree ---'; lsusb -t 2>/dev/null || lsusb"),

    ("=== 93LC66A EEPROMs: not on I2C, so SPI or STM8-side ===",
     "ls /sys/bus/spi/devices/ 2>/dev/null; echo '--- spidev present? ---'; "
     "ls /dev/spidev* 2>/dev/null || echo 'no /dev/spidev'; "
     "echo '--- any driver/module naming the part ---'; lsmod | grep -iE '93lc|at24|spidev'; "
     "echo '--- any file on the box referencing it ---'; "
     "find / -xdev -iname '*93lc*' -o -xdev -iname '*at24*' 2>/dev/null | head"),

    ("=== what the vendor app calls this port ===",
     "strings /usr/local/bin/CMIMIRDemo | grep -iE 'ttySTM8|/dev/tty|STM8' | sort -u | head -15; "
     "echo '--- from the ema library ---'; "
     "strings /usr/local/lib/libemaLib_arm_1.0.1.so | grep -iE 'ttySTM8|/dev/tty|STM8|serial' | sort -u | head -15"),
]
def main():
    """Run the ttySTM8 and missing-peripheral probes."""
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
            _, out, err = c.exec_command(cmd, timeout=120)
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