# Tech Context

Stack, setup, and the constraints that are not obvious from the code.

## Stack
| Layer | Technology | Version | Notes |
|---|---|---|---|
| PC tooling | Python | 3.11.9 | system Python, no venv |
| On-board tools | Python | **2.7** | `uart_*.py`, `i2c_scan.py` are python2 |
| Remote access | `paramiko` over SSH | - | password via `PHL_BOARD_PASS` |
| Board OS | Ubuntu Linaro | kernel `3.0.68` (2014) | `armv7l` |
| SoC | Samsung Exynos 4412 | - | 4x Cortex-A9, only 2 online |
| Memory | 1 GB DDR | - | 991 MB usable |
| Storage | Hynix 8 GB eMMC | - | `H8G2d` = `H26M42003GMR` |
| MCU | STM8S207 | - | owns the industrial I/O |

## Setup
    $env:PHL_BOARD_PASS = '<password>'
    python tools\board_ssh.py
    python tools\board_inventory.py --out docs\raw\BOARD-raw.md
    python tools\board_facts.py
    python tools\board_stm8_link.py

Board-side tools are python2 and run **on the board**:
    scp tools\uart_sniff.py root@192.168.100.127:/root/
    ssh root@192.168.100.127 chmod +x /root/uart_sniff.py
    ssh root@192.168.100.127 /root/uart_sniff.py /dev/ttySAC0 115200

## Constraints
- **`/dev/ttySAC1` is the kernel console** (`console=ttySAC1,115200n8`). Opening
  or reconfiguring it can hang a headless board. Excluded from every tool.
- **`/dev/ttySAC0/2/3`** are real (`s5pv210-uart`). **`ttySAC0` = STM8 link,
  `ttySAC3` = RS232, `ttySAC2` = RS485** — all three proven. `ttySAC2` and
  `ttySAC3` transmit but never receive, because no external device is attached.
- **The kernel has no RS485 support**: config is `CONFIG_SERIAL_S5PV210=y`
  only — no `SERIAL_S5PV210_RS485`, no `PINCTRL`. `TIOCGRS485` returns
  `EINVAL`, so direction control must be done by asserting DTR/RTS manually.
- **Only 5 GPIOs are claimed system-wide**: STATUS LED (31), Backlight (38),
  KEY POWER (202), hdmi-cec (223), hpd-plug (224). There is no driver-enable
  pin, and `/sys/kernel/debug/pinctrl` does not exist.
- **`/dev/ttyS0..3` are phantoms** — `port:00000000 irq:0`, no hardware behind them.
- **`/dev/ttySTM8` is a symlink to `/dev/pts/0`.** Not a serial port.
- **Only `eth0` exists**, driven by `smsc95xx` (the LAN9512 on USB). There is no
  native GMAC driver and no `ethernet@` device-tree node.
- **No GPIO userspace API**: `/sys/class/gpio` and `/dev/gpiochip*` both absent.
- **`i2cdetect` is not installed** on the board.
- **The device tree is stripped** — `model`/`compatible` empty, `Hardware` = `ODROIDX`.
- **2 of 4 cores permanently off**; cpu3 offlined to stop a boot loop.
- The board has **no display** reachable except VNC, so a hang means a power cycle.

## I2C devices found on the bus
| Address | Name | What it is |
|---|---|---|
| `0-0008`, `1-0008` | `usb3503` | USB hub controller |
| `0-0009` | `max77686` | PMIC (also feeds the 12 V header) |
| `1-001a` | `wm8960` | audio codec |
| `1-006f` | `mcp7940n` | RTC |
| `8-0038` | `hdmiphy` | HDMI PHY |

## External services
| Service | Why | Failure looks like |
|---|---|---|
| PyPI | `paramiko`, `pyserial` | import error |
| SSH to the board | all discovery | `CONNECT FAILED - ...` |

## Tooling notes
- Board tools take the password from `PHL_BOARD_PASS`, never a file or argument:
  `$env:PHL_BOARD_PASS='<pw>'; python tools\<tool>.py`
- `tools/board_inventory.py` has 13 sections; `--out` saves raw markdown.
- `tools/board_facts.py` and `tools/board_stm8_link.py` print to stdout.
- `temp/` retains only `ecu30_ed25519` (a generated board access key).