"""Settle the three facts the survey could not prove.

Each of these is a question the board itself can answer with a read:

  1. Which /dev/ttySACn is real and free? The SoC<->STM8S207 link is one of them,
     and RS232/RS485 sit behind the STM8. A port with irq:0 is a phantom.
  2. Can the second RJ45 ever appear? It needs a native GMAC driver; this kernel
     appears to have none, only the USB LAN9512 (smsc95xx = eth0).
  3. Where do the two 93LC66A EEPROMs live if they are on no Linux-visible bus?

Read-only. Opens nothing, writes nothing.

    $env:PHL_BOARD_PASS = '<password>'
    python tools/board_facts.py
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")

CMDS = [
    ("=== 1. every UART: does it have a real IRQ behind it? ===",
     "echo 'irq:0 on a serial line means no hardware behind it'; "
     "cat /proc/tty/driver/serial 2>/dev/null; "
     "echo '--- ttySAC device -> driver -> irq ---'; "
     "for t in /sys/class/tty/ttySAC*; do "
     "  printf '%-12s driver=%-14s irq=%s\\n' \"$(basename $t)\" "
     "\"$(basename $(readlink -f $t/device/driver 2>/dev/null))\" "
     "\"$(cat $t/device/irq 2>/dev/null || echo n/a)\"; done"),

    ("=== 2. native GMAC: driver, or does it not exist in this kernel? ===",
     "echo '--- modules that would drive a SoC MAC ---'; "
     "lsmod | grep -iE 'macb|dwmac|stmmac|gmac|ether'; "
     "echo '--- kernel config ---'; zcat /proc/config.gz 2>/dev/null | grep -iE 'DW_MACB|STMMAC|MACB|GMAC'; "
     "echo '--- any such module file shipped? ---'; "
     "find /lib/modules/$(uname -r) -iname '*macb*' -o -iname '*dwmac*' -o -iname '*stmmac*' 2>/dev/null | head; "
     "echo '--- other kernels/boot dirs available ---'; ls -la /boot/ 2>/dev/null | head -12; "
     "echo '--- does the SoC even have an ethernet node? ---'; "
     "find /proc/device-tree -iname '*ethernet*' -o -iname '*gmac*' 2>/dev/null | head"),

    ("=== 3. 93LC66A EEPROM: which bus could hold it? ===",
     "echo '--- SPI controllers in device-tree ---'; "
     "find /proc/device-tree -iname 'spi@*' 2>/dev/null | while read n; do "
     "  printf '  %-40s status=[%s]\\n' \"$n\" \"$(tr '\\0' ' ' < $n/status 2>/dev/null)\"; done; "
     "echo '--- SPI busses registered ---'; ls /sys/bus/spi/devices/ 2>/dev/null || echo '(no spi devices)'; "
     "echo '--- unclaimed I2C addresses at 0x50-0x57 (read byte, no write) ---'; "
     "which i2cdetect || echo 'i2cdetect NOT installed'; "
     "echo '--- any EEPROM driver loaded? ---'; lsmod | grep -iE 'at24|93lc|eeprom' || echo 'none'"),
]


def main():
    """Print the three fact-finding probes."""
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