"""Read-only hardware inventory of the board. The single source of truth.

Replaces the old scattered board_*.py probes. Everything here is a READ command:
no writes, no register pokes, no port opens. It only reports what the board is,
so docs/BOARD.md is measured from the running system rather than remembered.

Usage:
    $env:PHL_BOARD_PASS = '<password>'
    python tools/board_inventory.py            # print to stdout
    python tools/board_inventory.py --out docs/BOARD.md
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")

# (heading, shell command). Keep each command read-only and short -- a few of these
# are the first evidence we have ever had for a peripheral, so a probe that fails
# to run is worse than one that runs and prints nothing.
SECTIONS = [
    ("Board identity", """
cat /proc/device-tree/model 2>/dev/null | tr -d '\\0'; echo
echo -n 'compatible: '; tr '\\0' ' ' < /proc/device-tree/compatible 2>/dev/null; echo
echo -n 'hostname  : '; hostname
echo '--- os ---'; sed -n '1,4p' /etc/os-release 2>/dev/null
uname -a"""),

    ("CPU", """
echo -n 'cores online/present: '; cat /sys/devices/system/cpu/online /sys/devices/system/cpu/present | tr '\\n' ' '; echo
grep -E '^(model name|Hardware|Revision|Serial)' /proc/cpuinfo | sort -u
echo -n 'features  : '; grep -m1 ^Features /proc/cpuinfo
echo '--- freq ---'
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq 2>/dev/null
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null"""),

    ("RAM", """
grep -E 'MemTotal|MemFree|SwapTotal' /proc/meminfo
free -m | head -2
echo -n 'dt memory reg: '; for f in /proc/device-tree/memory@*/reg; do tr '\\0' ' ' < $f; done 2>/dev/null; echo"""),

    ("ROM / storage (eMMC + EEPROMs)", """
ls -l /dev/mmcblk* 2>/dev/null | head
echo '--- sizes ---'; cat /proc/partitions | tail -10
echo '--- fs ---'; df -h / /boot 2>/dev/null | head -4
echo -n 'eMMC name  : '; cat /sys/block/mmcblk0/device/name 2>/dev/null
echo -n 'eMMC cid   : '; cat /sys/block/mmcblk0/device/cid 2>/dev/null
echo -n 'eMMC manfid: '; cat /sys/block/mmcblk0/device/manfid 2>/dev/null
echo -n 'eMMC oemid : '; cat /sys/block/mmcblk0/device/oemid 2>/dev/null
echo '--- spi/nor ---'; ls /sys/bus/spi/devices/ 2>/dev/null | head"""),

    ("Ethernet: why 2 RJ45 but only 1 interface", """
echo '=== interfaces Linux has ==='; ls /sys/class/net/
for i in $(ls /sys/class/net/); do
  [ "$i" = lo ] && continue
  printf '  %-8s driver=%-10s mac=%s\\n' "$i" \\
    "$(basename $(readlink -f /sys/class/net/$i/device/driver 2>/dev/null))" \\
    "$(cat /sys/class/net/$i/address 2>/dev/null)"
done
ip -4 addr show 2>/dev/null | grep -E '^[0-9]+:|inet '
echo '=== is the native SoC GMAC present at all? ==='
ls /sys/bus/platform/drivers/ 2>/dev/null | grep -iE 'macb|eth|dw|gmac'
echo '=== ethernet device-tree nodes and their status ==='
for n in $(find /proc/device-tree -maxdepth 3 -name 'ethernet@*' 2>/dev/null); do
  printf '  %-50s status=[%s]\\n' "$n" "$(tr '\\0' ' ' < $n/status 2>/dev/null)"
done
echo '=== kernel messages about ethernet ==='
dmesg 2>/dev/null | grep -iE 'ethernet|macb|gmace|smsc|eth[01]' | tail -15
echo '=== USB ethernet chip (the LAN9512) ==='
lsusb 2>/dev/null
lsmod 2>/dev/null | grep -iE 'usbnet|smsc'"""),

    ("USB: 4 ports + the mystery micro-USB", """
echo '=== host controllers in device-tree ==='
for n in $(find /proc/device-tree -maxdepth 3 -name 'usb@*' 2>/dev/null); do
  printf '%-46s dr_mode=[%s] status=[%s]\\n' "$n" \\
    "$(tr '\\0' ' ' < $n/dr_mode 2>/dev/null)" "$(tr '\\0' ' ' < $n/status 2>/dev/null)"
done
echo '=== host controller drivers present ==='
ls /sys/bus/platform/drivers/ 2>/dev/null | grep -iE 'dwc|ehci|ohci|usb'
echo '=== currently enumerated USB devices ==='
lsusb 2>/dev/null
echo '=== which port is the OTG/device port? ==='
ls -l /sys/class/udc/ 2>/dev/null || echo 'no /sys/class/udc (no gadget controller registered)'
echo '--- adb/gadget running? ---'; ps aux | grep -E '[a]dbd|[g]_serial' || echo 'no adbd/gadget'
echo '--- gadget configfs ---'; ls /sys/kernel/config/usb_gadget/ 2>/dev/null || echo 'no gadget configured'
echo '=== hub / port events ==='
dmesg 2>/dev/null | grep -iE 'ehci|ohci|new .* USB device|hub' | tail -12"""),

    ("Serial: RS232 / RS485 / console / STM8 link", """
echo '=== tty devices present ==='; ls /dev/ttyS* /dev/ttySAC* /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
echo '=== DT aliases (which serial is which) ==='
tr '\\0' '\\n' < /proc/device-tree/aliases 2>/dev/null | grep -iE 'serial|uart'
echo '=== per-UART DT status (a disabled node never registers a tty) ==='
for n in $(find /proc/device-tree -maxdepth 3 -name 'serial@*' 2>/dev/null); do
  printf '  %-44s status=[%s]\\n' "$n" "$(tr '\\0' ' ' < $n/status 2>/dev/null)"
done
echo '=== console ==='; cat /proc/cmdline | tr ' ' '\\n' | grep -i console
echo '=== who holds a free serial port (the STM8 link lives here) ==='
for p in /dev/ttySAC0 /dev/ttySAC2 /dev/ttySAC3; do printf '  %s: ' $p; fuser $p 2>&1 | tail -1; done
echo '=== Daikin vendor stack (the STM8 owner) ==='
ls /usr/local/bin/ 2>/dev/null | head; ls /usr/local/lib/*.so 2>/dev/null
ps aux | grep -iE '[C]MIMIR|[c]miris' || echo 'no CMIMIR process running'"""),

    ("Digital I/O (IN1/IN2, GPO OUT1/OUT2)", """
echo '=== sysfs gpio export API ==='; ls /sys/class/gpio/ 2>/dev/null || echo 'ABSENT: /sys/class/gpio missing'
echo '=== gpiochip char devices (libgpiod) ==='; ls /dev/gpiochip* 2>/dev/null || echo 'ABSENT: no /dev/gpiochip*'
echo '=== kernel GPIO consumers (read-only listing) ==='
echo "debugfs pins claimed: $(cat /sys/kernel/debug/gpio 2>/dev/null | grep -c '^[0-9]*-')"
cat /sys/kernel/debug/gpio 2>/dev/null | head -20
echo '=== industrialio / relay / wiegand ==='
lsmod 2>/dev/null | grep -iE 'iio|relay|wiegand' || echo 'no iio/relay/wiegand module'
ls /sys/bus/iio/devices/ 2>/dev/null || echo 'no IIO devices'
find /sys -maxdepth 4 -iname '*wiegand*' 2>/dev/null | head"""),

    ("I2C buses + 93LC66A EEPROMs", """
ls /dev/i2c-* 2>/dev/null
echo '=== adapters ==='; for a in $(ls /sys/class/i2c-adapter/ 2>/dev/null); do
  printf '  %-8s name=%s\\n' "$a" "$(cat /sys/class/i2c-adapter/$a/name)"; done
echo '=== every device bound on I2C ==='
for d in /sys/bus/i2c/devices/*/; do
  n=$(cat $d/name 2>/dev/null); [ -n "$n" ] && printf '  %-14s %s\\n' "$(basename $d)" "$n"
done
echo '=== 93LC66A usually sits at 0x50-0x57; read-only probe of that range ==='
for b in /dev/i2c-0 /dev/i2c-1 /dev/i2c-4 /dev/i2c-5; do
  [ -e $b ] || continue
  echo "--- $b ---"; i2cdetect -y -r $b 0x50-0x57 2>&1 | tail -12
done"""),

    ("Audio (WM8960 + L/R)", """
cat /proc/asound/cards 2>/dev/null || echo 'NO ALSA card'
echo '--- playback pcm ---'; aplay -l 2>/dev/null | head
echo '--- codec driver ---'; lsmod 2>/dev/null | grep -iE 'wm8960|snd|i2s'
grep -rl wm8960 /sys/bus/i2c/devices/*/name 2>/dev/null"""),

    ("Power: 12 V header, regulators, RTC", """
echo '=== regulators declared in DT ==='
for n in $(find /proc/device-tree -maxdepth 4 -name '*regulator*' 2>/dev/null | head -20); do
  printf '  %-44s status=[%s]\\n' "$n" "$(tr '\\0' ' ' < $n/status 2>/dev/null)"; done
echo '=== rtc ==='; ls /sys/class/rtc/ 2>/dev/null; cat /sys/class/rtc/rtc0/name 2>/dev/null
echo '=== I2C drivers bound (incl. PMIC) ==='; ls /sys/bus/i2c/drivers/ 2>/dev/null"""),
]


def run(c):
    """Execute every section and return a list of (heading, output) pairs."""
    out = []
    for title, cmd in SECTIONS:
        try:
            _, so, se = c.exec_command(cmd, timeout=120)
            text = (so.read() or b"").decode("utf-8", "replace").rstrip()
            err = (se.read() or b"").decode("utf-8", "replace").rstrip()
            out.append((title, text if text else (err or "(no output)")))
        except Exception as exc:                  # one dead section must never
            out.append((title, f"PROBE FAILED: {exc}"))   # hide the other twelve
    return out


def render(sections):
    """Format the survey as the body of docs/BOARD.md."""
    parts = ["Collected over SSH from the live board by `tools/board_inventory.py`.",
             "Strictly read-only: no writes, no register pokes, no ports opened.", ""]
    for title, text in sections:
        parts.append(f"## {title}")
        parts.append("")
        parts.append("```")
        parts.append(text)
        parts.append("```")
        parts.append("")
    return "\n".join(parts)


def main():
    """Survey the board, then print it or write it to a markdown file."""
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

    body = render(run(c))
    c.close()

    if "--out" in sys.argv:
        path = sys.argv[sys.argv.index("--out") + 1]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body + "\n")
        print(f"wrote {path}")
    else:
        print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())