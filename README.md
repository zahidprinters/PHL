# phl — board bring-up

Understanding and using a **Daikin CMIMIR / Intelligent Manager** HVAC controller:
an Exynos 4412 running Ubuntu Linaro plus an **STM8S207** that owns the industrial
I/O.

## Start here

**[`docs/BOARD.md`](docs/BOARD.md) — the map.** Board identity, CPU/RAM/ROM, an
architecture diagram, and a **peripheral checklist** of 18 rows
(WORKS / LINK FOUND / OPEN / CLOSED). Everything in it was measured, not
assumed. Raw command output is in `docs/raw/`.

**[`docs/HARDWARE-COMPLETE.md`](docs/HARDWARE-COMPLETE.md) — the complete
picture.** Every chip, driver, bus and SoC resource on the board in one place,
what works today, and what is untapped (SoC ADC, PWM, GPIO, buttons). Boot
snapshot for analysis: `docs/raw/board-full-survey-raw.md`.

The short version: the link to the STM8S207 (`/dev/ttySAC0` @ 115200 8N1) is
found and the industrial I/O is **driven from Linux** — IN1/IN2, OUT1/OUT2 and
the relay all work, live on the board's desktop UI (**EMA_Controls**).
**RS232 is `/dev/ttySAC3`** and **RS485 is `/dev/ttySAC2`** — both direct Linux
UARTs that never go through the STM8, each proved with a control run. The
**micro-USB is closed** — fully diagnosed (no gadget function in the kernel in
normal mode; stub adbd in Android mode), no further work, use LAN/SSH.
**Both RJ45 jacks are one NIC (`eth0`).** The board carries a **Micrel
KSZ8995XA 5-port switch** between the LAN9512 and the two jacks, so RJ45 #2 can
never appear as a second interface — it needs a cable test, not a driver. Also
diagnosed: **93LC66A #1 is the LAN9512's own config EEPROM** (dumped with
`ethtool -e eth0`), and the **MCP7940N RTC** runs but was never given a date —
one `hwclock --systohc` from working (not yet run). A coin cell for it is
physically present.
What's left: the **3 front-panel buttons**, the
RJ45 #2 cable test (is it really just a switch port?), and that RTC
initialisation. The Wiegand read side (W-IN) is **pending** (parked
2026-10-11 — plan documented in `docs/BOARD.md` §9). (There is no analog I/O
on this board — only the audio codec, which works.)

## Connect

The board is at `192.168.100.127` and accepts SSH and VNC as `root`. The password
goes in an environment variable, never in a file, a log, or a command line:

    $env:PHL_BOARD_PASS = '<password>'
    python tools\board_ssh.py

## The desktop app — EMA_Controls

On the board's desktop, `EMA_Controls.sh` launches `tools/ema_ui.py`:

| Section | Shows / does |
|---|---|
| **IN1 / IN2 lamps** | light when the input is bridged to GND (active-low) |
| **OUT1 / OUT2 lamps + buttons** | click to switch; lamp shows the board's report |
| **RELAY button** | `55 05 04 01 01` / `01 00` |
| **SEND WIEGAND** | runs `/root/ema_wsend` on W-OUT; parks the reader, shows OK/FAILED |
| **reference line** | static: `RS232 = /dev/ttySAC3`, `RS485 = /dev/ttySAC2`, `STM8 = /dev/ttySAC0` |
| hex / frames / link line | last frame, frame count, link health |

Every display follows **what the board reports**, never the click — commands
retry up to 3x because the STM8 can silently refuse a frame.

## The HMI — custom SPA on Node-RED (v1.0)

Since 2026-10-14 the appliance screen is a **hand-written vanilla-JS SPA** served
by Node-RED itself (node-red-dashboard was removed — Angular-1 was too slow on
the 2012 ARM and had FF52 styling bugs):

- **Kiosk:** Firefox 52 boots fullscreen straight to `http://localhost:1880/`
  (OpenBox autostart; no browser chrome). Cold-boot verified: power-on →
  Node-RED + OpenBox + Firefox in ~2 minutes, unattended.
- **Tabs:** Home (clock/date/mode/setpoint), I/O (8 DI + 8 DO LEDs, analog
  in/out tables), Manual (override + DO toggles + AO sliders), Settings
  (language/engineer-installer role/units/theme/PIN), Info (IP, Modbus RTU
  params, attached devices), Raw (register dump + 0…4095 analog scaling).
- **All controls are grey/disabled in v1** — they unlock only when the logic
  workflow is wired (`locked` flag in the flow + the `/api/cmd` stub).
- **Backend:** Node-RED flow (`os/node-red/hmi-flow.json`) builds a state JSON
  every 1 s; the SPA polls `GET /api/state`. Editor is at `/red`.
- **Repo:** `os/node-red/static/` (index.html, app.css, app.js) +
  `os/node-red/hmi-flow.json` + `cleanup.sh` (board tidy pass).

## Tools

Most are **read-only**: they report, they never change the board. The `ema_*`
family is the exception — those talk protocol and actuate.

| Tool | What it does |
|---|---|
| `tools/board_inventory.py` | Full hardware survey. `--out docs\raw\BOARD-raw.md` to save it |
| `tools/board_facts.py` | The three open questions: which UART is real, is there a native GMAC, where are the EEPROMs |
| `tools/board_stm8_link.py` | Hunts the SoC↔STM8 link; shows what `/dev/ttySTM8` really is |
| `tools/board_ssh.py` | Quick shell-out: identity, os, disk, memory, uptime |
| `tools/rs232_loopback.py` | Identifies the RS232 UART with a one-wire jumper; uses tx/rx counters as ground truth *(board)* |
| `tools/rs485_probe.py` | Drives a UART in timed windows so a meter across D+/D− names the RS485 port *(board)* |
| `tools/link_health.py` | OPEN/CLOSE handshake against the STM8; pass = the digital I/O is usable *(board)* |
| `tools/ema_ui.py` | **The desktop app (EMA_Controls)** — lamps, output buttons, relay *(runs on the board)* |
| `tools/ema_uimap.py` | Replays the full OUT1/OUT2 frame map and PASS/FAILs each action *(board)* |
| `tools/ema_gap.py` | Regression check for the OUT2 recipe while OUT1 is closed *(board)* |
| `tools/uart_sniff.py` | Listen on a candidate UART for the STM8 traffic *(board)* |
| `tools/uart_tap.py` | Man-in-the-middle PTY to capture the vendor tool's frames *(board)* |
| `tools/uart_console.py` | Serial console capture/send *(board)* |
| `tools/i2c_scan.py` | I2C bus scanner *(board)* |

`board_*.py` and the SSH helpers run from this PC. The rest are **python2 and
belong on the board** (`scp` them over first).

## Safety

The `board_*` probes are strictly read-only. The `ema_*` tools **do actuate** —
they switch real outputs and the relay — so they are only run when a test is
intended, and every command is confirmed from the STM8's own status/ack before
it counts as done. Opening `/dev/ttySAC1` is deliberately avoided everywhere:
it is the kernel console, and disturbing it can hang the board.

## Archive

`archive/` holds the previous attempts — Philips Dynalite lighting work, and the
ECU-30 Android/USB driver hunt. Both were dead ends. Kept rather than deleted, so
they can be recovered; delete the folder when you are sure.

## Status

`CHANGELOG.md` records what has and has not been verified against real hardware.
The headline: the **SoC↔STM8 link is found** and the industrial I/O is **driven
from Linux** — IN1/IN2, OUT1/OUT2 (ON+OFF), the relay and **Wiegand OUT** all
work on the desktop app **EMA_Controls**. What is left: the front-panel
buttons, the RJ45 #2 cable test, and RTC initialisation — the Wiegand read
side (W-IN) is pending (parked 2026-10-11). (There is no analog I/O on this
board — only the audio codec, which works.)
