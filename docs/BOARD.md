# Board — what it is, and what works

> **Complete hardware picture (every chip, driver, bus, SoC resource, what works
> and what is untapped): [`HARDWARE-COMPLETE.md`](HARDWARE-COMPLETE.md).**
> Boot snapshot for analysis: `raw/board-full-survey-raw.md`.
> STM8 protocol framework (event→frame map, struct offsets, silent-refusal
> causes): [`VENDOR-PROTOCOL.md`](VENDOR-PROTOCOL.md).

Every line here was **measured on the live board over SSH**, not remembered.
Raw evidence is kept in `docs/raw/`. Re-measure with:

    $env:PHL_BOARD_PASS = '<password>'
    python tools\board_inventory.py --out docs\raw\BOARD-raw.md

## Identity

| | |
|---|---|
| What it really is | Daikin **CMIMIR / Intelligent Manager** HVAC controller |
| SoC | Samsung **Exynos 4412**, 4× ARM Cortex-A9 (`armv7l`), 200 MHz–1.2 GHz, `ondemand` |
| Cores online | **only 2 of 4** — `online=0,3`; cpu1 and cpu2 are permanently off |
| RAM | **991 MB** usable of 1 GB. No swap. *Was 916 MB in use at survey time — abnormally high, see Gotchas.* |
| ROM | **8 GB eMMC**, Hynix `H8G2d` (CID `90014a48…`) — this is the `H26M42003GMR` on the silkscreen |
| Partitions | `mmcblk0p1` 128 MB boot · `mmcblk0p2` 5.3 GB root (59% used) · `mmcblk0boot0/1` |
| OS | Ubuntu Linaro, hostname `linaro-ubuntu-desktop` |
| Kernel | `3.0.68 #11 SMP Wed May 7 10:42:42 KST 2014 armv7l` — a **2014** kernel |
| Access | SSH + VNC, user `root`, password from `PHL_BOARD_PASS` |

## The one fact that explains everything else

```
  physical headers: GPI/GPO, RS232, RS485, RJ45#2, Wiegand, 93LC66A #2?
                              │
                        ┌─────▼─────┐
                        │ STM8S207  │  ← separate MCU, owns the industrial I/O
                        └─────┬─────┘
                              │  SOLVED: /dev/ttySAC0 @ 115200 8N1
  Exynos 4412 (Ubuntu Linux)  │
      ├── ttySAC0  ← the STM8 link (confirmed by the vendor library)
      ├── ttySAC2/3  real UARTs, unused
      ├── ttySAC1    kernel console, leave alone
      ├── eth0       LAN9512 on USB
      └── I2C x5, audio, HDMI, eMMC, USB hub
```

**Consequence:** GPI/GPO, RS232, RS485 and RJ45 #2 are **not Linux devices** —
they are STM8 pins, reached over the UART above. That is why every Linux-side
attempt at `/sys/class/gpio`, a Wiegand driver, and `/dev/ttyS*` failed: those
were the wrong devices.

## The SoC↔STM8 link — SOLVED

Found by compiling a stub against Daikin's own `libemaLib` and watching which
file descriptor it opens, rather than guessing.

| | |
|---|---|
| Port | **`/dev/ttySAC0`** — confirmed by `[TRACE] open("/dev/ttySAC0")` |
| Line | **115200 baud, 8 data bits, no parity, 1 stop bit, raw** |
| Framing | `0x55` \| LEN \| payload… \| `00 00` — SOF, **total** length, payload, trailer |

Frames observed on the wire:

| Direction | Bytes | Meaning |
|---|---|---|
| TX → STM8 | `55 04 01 01` | open |
| RX ← STM8 | `55 04 01 01` | ack |
| RX ← STM8 | `55 0a 03 00 01 01 xx xx 00 00` | status |
| TX → STM8 | `55 04 01 00` | close |
| RX ← STM8 | `55 04 01 00` | ack |

Notes on behaviour, all measured:
- The STM8 sends **one** status frame after open. It is **not** a periodic
  stream — a 60-second run received only the ack plus that one frame. Getting
  regular updates needs a request frame, whose format is not yet known.
- `EMAMain::readEvent()` returns `-9` until a read is armed with
  `setReadEvent()`; it is not a passive poll.
- **No actuator frame had ever been sent at this point** — only open and close.
  That stopped being true later; see **Output bits — SOLVED** for the frames
  that are now routinely transmitted.

### The library is drivable — no need to guess the protocol

`libemaLib_arm_1.0.1.so` exports a plain **C** API as well as the C++ class,
and these are unmangled symbols, so Python `ctypes` can call them directly:

```
ema_createEMA  ema_destroyEMA  ema_open  ema_close
ema_readEvent  ema_writeEvent  ema_cancelPendingReadEvent
ema_clearEventQueue  ema_getEMAVersion
```

The C++ path also works: a stub declaring `class EMAMain { open(); isOpen();
readEvent(); writeEvent(_EMA_EVENT*); … }` compiles and links against the
stripped library, because C++ name mangling resolves it. The board has
`g++ 4.6.3` and `libQtCore.so.4`. **A `QCoreApplication` is required** — the
library delivers reads through a `QSocketNotifier`, which does nothing without a
running event loop.

**What is still missing is the `_EMA_EVENT` struct layout** (field offsets and
the event-type enum values). With that, `ema_writeEvent` gives a correct frame
by construction, and `ema_readEvent` retrieves input states.

## Peripheral status — the checklist to work down

`WORKS` = usable from Linux today. `LINK FOUND` = the channel to the STM8 is
located and proven, but the request/response format for that specific peripheral
is not yet implemented. `OPEN` = investigated but not yet working — either the
target is not yet located, or the fix is known and pending. **18 rows: 14 WORK,
3 OPEN, 1 CLOSED — no BLOCKED rows and no LINK FOUND rows remain.**

| # | Peripheral | In Linux | Status | Route / notes |
|---|---|---|---|---|
| 1 | **12 V power header** | n/a | **WORKS** | Fed by the `max77686` PMIC on I2C `0-0009` |
| 2 | **RJ45 #1** (LAN9512) | `eth0` | **WORKS** | `smsc95xx`+`usbnet` over USB, 100 M full-duplex, MAC `00:25:ff:fe:44:45` |
| 3 | **RJ45 #2** (silkscreen `LAN2`) | no | **OPEN** | **Behind a Micrel KSZ8995XA 5-port switch — not the STM8.** Same `eth0` as #1, so there is no second NIC to bind; that absence was previously misread as "on the STM8". Decides with a live cable vs `ethtool eth0`. See #3 |
| 4 | STM8S207 | **yes** | **WORKS** | Reached over `/dev/ttySAC0` @ 115200 8N1. See "The SoC↔STM8 link" |
| 5 | **RS232** | **`ttySAC3`** | **WORKS** | **Direct Linux UART, proven by loopback — not behind the STM8 at all** |
| 6 | **RS485** (D+/D−, half-duplex) | **`ttySAC2`** | **WORKS (TX)** | **Identified by differential measurement + control run. TX proven; RX untested (no device attached), kernel has no RS485 mode |
| 7 | **IN1 / IN2** (digital in) | **yes** | **WORKS** | **Decoded.** Status frame byte 6 = IN1, byte 7 = IN2, active-low |
| 8 | **OUT1 / OUT2** (GPO) | **yes** | **WORKS** | **Decoded.** Full frame map below; driven from the desktop UI, state verified from status bytes 4/5 |
| 9 | Wiegand in/out | `tools/ema_wsend.cpp` | **WORKS** | **Driven live 2026-10-13, click-tested 2026-10-14:** both ports (1, 2) × both pins, all pulse. SET_CONFIG→WRITE_DATA handshake (see `VENDOR-PROTOCOL.md`); STM8 ACKs by echoing every frame. `W-OUT1`/`W-OUT2` = DATA0/DATA1 — **one channel**: 0-bits → DATA0, 1-bits → DATA1, so both lines pulse per card; not independent outputs (use OUT1/OUT2 for that). **Open-collector** — wire LEDs `+12V → 1k → LED → pin` (pin→LED→GND never lights); idle LOW at boot, released after close. Headers `W-IN` / `W-OUT` |
| 9a | **Relay** | **yes** | **WORKS** | `55 05 04 01 01` on / `01 00` off. Selector `01`. Confirmed on hardware |
| 10 | **WM8960 audio** (+ / − L,R) | card 0 | **WORKS** | I2C `1-001a`; PCM `wm8960-hifi-0` play, `-1` capture |
| 11 | **4× USB 2.0** | hub chain | **WORKS** | `s5p-ehci` 3 ports → hub `1-2` → hub `1-2.3` (3 ports). A stick worked at `1-2.3.2` |
| 12 | **micro-USB** | mode-dependent | **CLOSED** | Fully diagnosed; **no further work decided.** Normal mode: no gadget function built into the kernel (Code 43 root cause — needs a kernel rebuild, not pursued). Android mode: ADB `18d1:0002` but stub replies `FAIL`. Use LAN/SSH. See #12 |
| 13 | **8 GB eMMC** | root fs | **WORKS** | `mmcblk0`. Root 5.3 GB |
| 14 | **93LC66A #1** — LAN9512 config EEPROM | `ethtool -e eth0` | **WORKS** | Proven: `0xA5` sig, MAC `00:25:ff:fe:44:45` (= `eth0`), USB IDs `0424:9512`/`0424:ec00`, `SMSC` string. LAN9512 loads it over its own Microwire pins — no SoC bus. See #14 |
| 14a | **93LC66A #2** — master not yet proven | no | **OPEN** | Not on any SoC bus (no SPI at all, all 7 I2C devices named). **Sits in the LAN section beside the LAN9512 and the KSZ8995XA switch** (photo) — so a network chip, not the STM8. Switch is the leading candidate; unproven. See #14 |
| 15 | **HDMI mini** | yes | **WORKS** | I2C `8-0038` = `hdmiphy`. Drives the display/VNC session |
| 16 | **3 push buttons + STATUS LED** | LED: kernel only; buttons: no | **OPEN** | LED = `gpio-31`, `odroid_led_timer` blinks ~1 Hz (not userspace-controllable). The 3 buttons are **invisible to running Linux** — two press rounds proved it. See #16 |
| 17 | **MCP7940N RTC** (I2C `1-006f`) | `/dev/rtc0` | **OPEN** | Chip alive — oscillator runs, H:M:S ticks — but **date registers are 0/0/0**, so every kernel read returns `EINVAL` and boot `hctosys` fails. Fix = one `hwclock --systohc`, **not yet run**. See #17 |

### #14 — the 93LC66A EEPROMs — one proven, one open

**#1 is the LAN9512's own configuration EEPROM.** The proof chain:

- The kernel has **no SPI at all** (`# CONFIG_SPI is not set`, no `93CX6`, no
  `/dev/spidev*`), and the chip is on **no I2C bus** — all 7 devices are named:
  dummy, usb3503 ×2, max77686, wm8960, mcp7940n, hdmiphy.
- `lsusb` shows one LAN9512 presenting as two USB devices: `0424:9512` (hub
  function) + `0424:ec00` (ethernet function).
- **`ethtool -e eth0` dumps the chip itself** (`supports-eeprom-access: yes`):

  ```
  0x0000  a5 00 25 ff fe 44 45 ...   0xA5 = SMSC valid-EEPROM signature
                                      MAC 00:25:ff:fe:44:45 = eth0's MAC
  0x0020  24 04 12 95 ...            USB VID:PID 0424:9512 (hub fn)
  0x0048  24 04 00 ec ...            USB VID:PID 0424:ec00 (eth fn)
  0x003c  53 00 4d 00 53 00 43 00    UTF-16 "SMSC"
  rest    ff ...                     erased
  ```

- The LAN9512 reads the chip **itself**, over its dedicated Microwire pins, at
  power-up — before Linux starts. No driver, no bus, no OS involvement. That is
  exactly why a kernel with zero SPI support still has a working MAC.

**#2's master is still unproven, but its neighbourhood is now photographed.**
No second Ethernet MAC, no free I2C address, no SPI — and the user placed it
physically **right next to the LAN9512**. The board photos then named the
companion chip: a **Micrel/Microchip KSZ8995XA**, an integrated 5-port
10/100 QoS switch, sitting between the LAN9512 and the two RJ45 jacks
(`LAN1`, `LAN2`). That is the only kind of chip that can put two physical
jacks on one NIC, so it retires the old "RJ45 #2 is on the STM8" reading.

> ⚠️ **What is proven and what is not.** Proven from the photos: a real 5-port
> switch exists, it is in #2's neighbourhood, and it explains two jacks on
> `eth0`. **Not proven: that #2 belongs to the switch.** The KSZ8995XA loads
> its config from a **2-wire I²C EEPROM** (`SCL`/`SDA`, pins 110/111); a
> 93LC66A is a **3-wire Microwire** part. Different bus, different part — the
> switch is the *leading candidate*, not a confirmation. The deciding test is
> unchanged: a live cable in **RJ45 #2** watched against `ethtool eth0`.

The vendor binaries were scanned too: no `/dev/i2c`, no `spidev`, no bit-bang
strings anywhere — the vendor code never reaches serial buses directly.
(`libcmirisLib2`'s `EEPROM` class — board number, serial, license — is the
MPIC **camera** over USB, not these chips.)

### #17 — MCP7940N RTC — chip alive, date never initialised

| | |
|---|---|
| Bus | I2C **1**, address **0x6F** (`1-006f`) |
| Driver | vendor `rtc-mcp7940n` v0.1, built-in (`CONFIG_RTC_DRV_MCP7940N=y`) |
| Node | `/dev/rtc0` / `/sys/class/rtc/rtc0` |
| Boot log | `chip found` ✅ … `hctosys: unable to read the hardware clock` ❌ |

Every read fails: `hwclock -r` → `Invalid argument`; sysfs `date`/`time` →
`Invalid argument`. A read-only register dump (`tools/mcp7940_dump.c`, run with
`I2C_SLAVE_FORCE` because the driver owns the address) shows exactly why:

```
00  c9   ST bit = 1    oscillator RUNNING
01  30   minutes 30
02  00   hours 00
04  00   mday  = 00   ← INVALID (needs 1..31)
05  00   month = 00   ← INVALID
06  00   year  = 00   ← never set

tick test (1.3 s apart): c9 → d1  (seconds 49 → 51) → CHANGING
```

**The hardware is healthy — the chip was simply never given a date.** The
kernel only ever *reads*, and nothing on this board has ever written one, so
`rtc_valid_tm()` rejects `mday=0` → `EINVAL` on every path. This is the origin
of the old "no working RTC / logins timestamped 1970" note.

**Fix: `hwclock --systohc` once** — writes system date+time into the chip,
after which every boot's `hctosys` succeeds. **Not yet run — a write, awaiting
the user's go.**

**The battery is physically there.** The board photos show a **coin cell in a
through-hole holder immediately left of the CM4412 module**, next to the
silkscreen `F-RST` (`docs/raw/board-photos-raw.md`). So the hardware for
holding the clock across a power cut exists; whether the cell still holds a
charge is untested. Also still open: *who* set the system date correctly at
boot despite the failed `hctosys` (no NTP process runs, `rc.local` is empty).

### #10 — WM8960 audio (full detail)

| | |
|---|---|
| Chip | Wolfson **WM8960** — stereo codec + Class-D speaker amp, I2C `1-001a` |
| Codec driver | `CONFIG_SND_SOC_WM8960=y` (mainline) |
| Machine driver | `CONFIG_SND_SOC_CTIS_WM8960=y` — **vendor's own**, creates card `Ctis_wm8960` |
| I2S | `CONFIG_SND_SAMSUNG_I2S=y` + `_MASTER` — **the SoC is I2S master**, codec is slave |
| Devices | play `hw:0,0` (`Playback wm8960-hifi-0`), capture `hw:0,1` (`Capture wm8960-hifi-1`) |

Mixer as booted (`amixer`): headphone 121/127, speaker **127/127** (Class-D
wide open), DAC 255/255, capture 63/63, LINPUT1/RINPUT1 boost **on**,
output-mixer PCM routed L+R; mono/ALC/3D/HPF all off.

**Both directions tested live:** `aplay -D hw:0,0 … -d 1` and
`arecord -D hw:0,1 … -d 1` → exit 0, capture file exactly 192000 bytes =
1.000 s of 48 kHz / S16 / stereo. Quirk: `/proc/asound/card0/` holds only `id`
(this kernel exposes no `pcm0p` subdirs) — use `/proc/asound/pcm` and
`/dev/snd/*` instead.

### #12 — the micro-USB port (OTG / debug) — **CLOSED**

**No further work on this port** (decision recorded below the table). What was
proven before closing:

| boot mode | what the PC sees |
|---|---|
| normal (Linux up) | **nothing** — no UDC registered, no gadget configured |
| **Android mode** | **`18d1:0002 Google Inc. Android 1.0`**, interface `FF/42/03` = **ADB** — but the far end is a stub (below) |

**Normal mode — the board presents no device at all** (re-measured over SSH):

| check | result |
|---|---|
| `/sys/class/udc` | **absent** — no UDC registered |
| `/sys/kernel/config/usb_gadget` | **absent** — no gadget configured |
| configfs | **not mounted** |
| gadget function modules (`g_ether`, `g_serial`, `g_mass_storage`…) | **none loaded** |
| `dmesg` | `s3c-udc : S3C HS USB OTG Device Driver` — controller **is** present |
| `dmesg` | `LDO12 VDD33_UOTG_3V3: 3300 mV`, `LDO15 VDD10_OTG: 1000 mV` — **PHY is powered** |

**Root cause — proven from `/proc/config.gz` on the board:**

```
CONFIG_USB_GADGET=y                 framework present
CONFIG_USB_GADGET_S3C_OTGD=y        controller driver built-in
# CONFIG_USB_ZERO is not set        no gadget function compiled
# CONFIG_USB_ETH is not set
# CONFIG_USB_GADGETFS is not set
# CONFIG_USB_G_SERIAL is not set
# CONFIG_USB_G_MULTI is not set
```

`/lib/modules` contains **zero** `g_*.ko` files. So there is **no gadget
function on this system at all** — not unloaded, *not built*.

**Both PCs fail for the same reason, and neither is at fault.** Measured from
a Linux PC while plugged in, the board attaches (the `s3c-udc` driver pulls D+)
but **nothing answers SETUP packets**:

```
usb 1-1: Device not responding to setup address.
usb 1-1: device descriptor read/64, error -110
usb usb1-port1: unable to enumerate USB device     (retries, device #13 → #22)
```

That is the **identical failure Windows reports as Code 43 "Device Descriptor
Request Failed"**. Board side confirms: `VBUS online=0`, `NO-UDC`.

> ⚠️ **No PC driver can fix this.** Driver binding happens *after* enumeration
> succeeds; this device never completes enumeration. The fix must be board-side.

> ⚠️ **Corrected the earlier "next step" in this section.** It said *mount
> configfs, create a gadget* — that is **impossible on this kernel**: 3.0.68
> predates configfs USB gadgets (libcomposite), and this build has every
> gadget function disabled. Real options: **(1)** rebuild the kernel with
> `CONFIG_USB_ZERO`/`CONFIG_USB_G_SERIAL`, **(2)** use **Android mode**, where
> the port enumerates cleanly as `18d1:0002`, **(3)** leave it — normal mode
> has no functional micro-USB.

**Android mode — measured from a Linux PC** (board repowered into that
mode; it is **off the network there** — ping to `192.168.100.127` fails):

| check | result |
|---|---|
| `lsusb` | `Bus 001 Device 002: ID 18d1:0002 Google Inc. Android 1.0` |
| descriptor | `Product: Android 1.0`, **enumerates cleanly** (no Code 43 on Linux) |
| interface | `bInterfaceClass=ff  sub=42  proto=03` — the **ADB** signature |
| endpoints | `0x81` IN, `0x02` OUT (bulk) |
| `/dev/ttyACM*` | **absent** — not a CDC serial gadget in this mode |
| `adb devices` (Linux, adb 29.0.6) | **empty** — server starts, device thread runs, never finds it |

**Why adb fails: the far end is a stub, not a real adbd.** A raw pyusb probe
spoke ADB protocol directly, bypassing the `adb` tool:

```
CNXN (both protocol versions) -> 4 bytes: "FAIL"
SYNC                           -> 4 bytes: "FAIL"
AUTH                           -> 4 bytes: "FAIL"
1 garbage byte                 -> 4 bytes: "FAIL"
0 bytes (nothing sent)         -> 4 bytes: "FAIL"
```

A real adbd answers with a 24-byte header (`CNXN` or `AUTH`). This one answers
**identically to everything, including silence** — a fixed responder. (First
write is accepted, 31 bytes; subsequent writes stall until a USB reset, i.e.
the far end buffers but never reads.)

> ⚠️ **No PC driver will ever fix this.** The Windows "driver" problem and the
> board-side behaviour are separate: Linux enumerates it fine, so the hardware
> and descriptor are OK — there simply is no working adbd behind the interface.
> Previous "find a driver" attempts were chasing the wrong layer.

**Unresolved:** *what* serves `FF/42/03` in Android mode (needs the board
reachable or a gadget/configfs inspection in that mode), and whether another
boot mode exposes a real adbd. An earlier sighting of a
`SAMSUNG SMDK Exynos Platform Serial` string suggests the gadget type may vary
between modes — not re-verified in this session.

### #5 — RS232 — direct to Linux, not the STM8

**It was never behind the STM8.** The original note said *"behind the STM8;
request format unknown"* — that was wrong, and a one-wire loopback proved it.

Four UARTs exist; the byte counters separate them:

```
0: ttySAC0  tx:13436 rx:21704   STM8 link
1: ttySAC1  tx:3510  rx:0       kernel console
2: ttySAC2  tx:105   rx:0       transmits, never receives
3: ttySAC3  tx:77    rx:7       RS232  <- looped back cleanly
```

**The test needs nothing but a wire.** Jumper TX to RX on the connector, run
`tools/rs232_loopback.py`, then remove it and run again as a control:

| | rx on ttySAC3 | |
|---|---|---|
| jumper fitted | `0 → 7` | `RS232LB` echoed byte-for-byte |
| jumper removed | `7 → 7` | frozen — the echo was the wire, not an artifact |

`ttySAC2` is ruled out because it **transmitted all 105 bytes and never
received one**. That distinction matters: the driver increments `tx` for every
byte handed to the UART **whether or not a pin is wired**, so `tx` alone proves
nothing — only a matching `rx` increment does.

**Not established by loopback:**

- **Real baud rate.** Loopback echoes at any speed, because TX and RX share one
  setting. 115200 "worked" only because we configured it consistently.
- **Line voltage.** Doesn't distinguish true RS232 (±5–10 V) from bare TTL.
  With the jumper still in, measure TX to GND: negative (~−5 to −10 V) means a
  real line driver; 0/+3.3 V means TTL and needs a MAX232.

So RS232 needs **no event types and no frames** — just open `/dev/ttySAC3`.

### #6 — RS485 — SOLVED, `/dev/ttySAC2`

**Identified by differential measurement, with a control run.**

The connector is **2 terminals (D+/D−), half-duplex** — TX and RX are the same
pair, so there is no separate line to jump, and the RS232 method cannot work
here. Shorting D+ to D− just forces the differential to zero.

**What does show up is the transceiver's own bias.** An RS485 bus sits at a
small fail-safe differential when idle; driving it moves that. Measured **DC
across the pair** (not to GND), jumper removed, 30-second windows:

| port | idle | during TX | verdict |
|---|---|---|---|
| **`ttySAC2`** | 0.646 V | **~220 mV** | **moved — twice, reproducible** |
| `ttySAC3` | 0.646 V | **0.646 V** | control: held perfectly still |

The control is the point. Same meter, same setup, same window — and only
`ttySAC2` moved, so the change cannot be board activity, meter drift or a
ground shift. `ttySAC3` is separately proven to be RS232, which fits.

The `55 AA` pattern is alternating, so a DC-averaged meter collapses toward the
mean while it transmits — that is why the reading *falls* rather than rises.

**Caveats — what this does and does not prove:**

- ✅ the port is identified and **drives the pair**
- ✅ transmit path: `wrote 189184 bytes` per window, counters confirm
- ❌ **reception is unproven** — `rx` stayed `0` throughout, because no RS485
  device was attached to talk back
- ❌ baud rate unknown; no actual RS485 communication has ever happened
- ❌ the kernel has **no RS485 mode** (`CONFIG_SERIAL_S5PV210` only — no
  `SERIAL_S5PV210_RS485`, no `PINCTRL`), so `TIOCGRS485` returns `EINVAL` and
  direction control cannot be automatic. The probe works by asserting DTR/RTS.

**Negative results, kept so they are not repeated:**

- **Loopback/jumper is structurally impossible on this connector** — 5 phases,
  **0/50 echoes**. A negative about the method, not the port.
- **The vendor stack never drives RS485**: `libemaLib`'s 77 `SerialPort`
  strings are vendored `QextSerialPort` opening only `/dev/ttySAC0`, and the
  event enum has **no RS232/RS485 entry** (`CLOSE OPEN WIEGAND×5 GPI12_READ
  GPO1_WRITE GPO2_WRITE GPO12_WRITE RELAY_WRITE`).
- **No driver-enable GPIO is claimed** — the whole system claims 5 pins
  (STATUS LED, Backlight, KEY POWER, hdmi-cec, hpd-plug).

Run it with `tools/rs485_probe.py /dev/ttySAC2 30` (add `--no-rts` if a
transceiver needs the opposite polarity).

### The debug / console port — `ttySAC1`, **1.8 V logic**

The fourth and last UART. Only four exist and the other three are taken
(`ttySAC0` STM8, `ttySAC2` RS485, `ttySAC3` RS232), so a serial debug header
could only be `ttySAC1` — and the config says so:

```
/proc/cmdline →  console=tty1 console=ttySAC1,115200n8
auto-serial-console start/running, process 1541
/dev/ttySAC1:  root  1541  login
               root  1902  bash
```

| | |
|---|---|
| Device | `/dev/ttySAC1` (kernel console) |
| Speed | **115200 8N1** |
| Logic | **1.8 V** — ⚠️ **not** 3.3 V, and **not** RS232 |
| Header | **4-pin: VCC, TX, RX, GND** |
| Status | ✅ **VERIFIED WORKING** — 1.8 V adapter + level shifter + PuTTY on COM4 |
| Contents | boot log, `login:` prompt, root shell — every boot |
| Service | `auto-serial-console` |

> **✅ Physically verified end-to-end (2026-10-12).** A 1.8 V USB-UART adapter
> through a level shifter, on COM4 @ 115200, captured the full U-Boot + kernel
> boot and reached a root shell (`root@linaro-ubuntu-desktop:~#`). The board
> booted the **vendor OS from the SD card** (kernel `3.0.68`, `Linaro 12.11`,
> `root=UUID=e139ce78`) with **no Ethernet cable attached** — the debug port
> alone gives complete screenless access. Working rig: **Prolific PL2303 on
> COM4, DTR asserted** (PuTTY does this by default; a raw pyserial open with
> `DTR=False` receives nothing on these clones).

**⚠️ 1.8 V is the trap here.** A 5 V RS232 adapter will **destroy** the pin,
and a 3.3 V adapter *driving* into it risks damage too. Even for reading, a
3.3 V receiver typically needs ~2.3 V for a valid high, so 1.8 V logic highs
may not register at all. Use a **1.8 V TTL adapter** or a proper level shifter.

**It is never opened by any tool in this repo** — it holds a live
`login`+`bash`, and opening the console can hang a headless board. Console
output is driven indirectly instead:

| method | effect on `ttySAC1 tx` |
|---|---|
| `echo X > /dev/console` | **+17** ✓ works |
| `wall` | **+495** ✓ works |
| `echo X > /dev/kmsg` | **+0** ✗ does not reach it — different path |

That last row matters: kernel ring-buffer writes are *not* a way to exercise
this port. `dmesg` messages land in the ring buffer and are simply not
forwarded here at the current loglevel.

### #3 — two RJ45 sockets, one network port

**The board carries a Micrel/Microchip KSZ8995XA** — an integrated 5-port
10/100 QoS switch — sitting between the LAN9512 and the two jacks, which are
silkscreened **`LAN1`** and **`LAN2`**. Read off the board photos
(`docs/raw/board-photos-raw.md`).

So RJ45 #2 is not on the STM8 at all. It is a second port of a switch whose
uplink is the LAN9512, which is `eth0`. Both jacks are therefore the *same*
NIC, and that is why nothing ever showed up as a second interface:

- The only NIC in Linux is `eth0` = `smsc95xx`, the **LAN9512 on USB**
- The kernel has **no native GMAC driver at all** — no `macb`, `dwmac` or
  `stmmac` module, and **no `ethernet@` node anywhere in the device tree**
- A switch needs **no driver and no bus**: it bridges frames in hardware,
  before Linux is involved

**What this means in practice.** There is no `eth1` to bring up and no request
frame to build — that whole line of attack was aimed at the wrong chip. RJ45 #2
should already pass traffic for whatever is plugged into it. The one test that
settles it has never been run:

> Plug a live cable into **RJ45 #2** and watch `ethtool eth0` (and the link
> LEDs) for a partner appearing on the switch. Do the same into **RJ45 #1** as
> a control. If #2 lights the same `eth0`, the switch reading is confirmed.

> ⚠️ The old note here said RJ45 #2 was "almost certainly wired to the STM8",
> inferred purely from there being no second NIC. **A switch produces exactly
> the same symptom**, so that inference never held. It is now replaced by the
> photographed chip. The STM8 may still carry *some* RJ45 #2 function — nothing
> rules that out — but not its Ethernet.

## Input bits — DECODED by experiment

The status frame carries both digital inputs as separate bits, confirmed by
physically bridging each input to GND and watching the stream:

```
55 0a 03 00 01 01  BB RR 00 00
                   ││
                   │└─ byte 7 = IN2
                   └─── byte 6 = IN1
```

| Input | Byte | Idle (open) | Bridged to GND | Window observed |
|---|---|---|---|---|
| **IN1** | 6 | `01` | `00` | 00:51:43 → 00:52:10 (27 s) |
| **IN2** | 7 | `01` | `00` | 00:53:47 → 00:54:04 (17 s) |

**Both inputs are active-low**: `00` = asserted/bridged, `01` = open. That is what
an opto-isolated 24 V input on a live controller should read as.

The two bits are independent — shorting IN1 left byte 7 at `01`, and shorting
IN2 left byte 6 at `01`. The combined state (`byte6=00, byte7=00`) was never
observed and remains untested.

Raw captures are kept in `logs/ema_cap_in1.log` and `logs/ema_cap_in2.log`.

### Live control UI — EMA_Controls

`tools/ema_ui.py` puts the whole digital I/O on the board's desktop: IN1/IN2
lamps, OUT1/OUT2 lamps **and buttons**, a relay button, and a **Wiegand W-OUT
test row**. Installed at `/root/ema_ui.py` with a launcher at
`/root/Desktop/EMA_Controls.sh`; run with:

    DISPLAY=:0 python2 /root/ema_ui.py

PyQt4 is the only viable toolkit on this image (Tk, PySide and PyQt5 are all
absent). The reader cycles close/open on a background thread, because the STM8
answers one open with one status frame and then goes quiet.

Every button follows the same contract: **the display shows what the board
reports, never the click.** Commands retry up to 3x until an ack/status
confirms them, because the STM8 can silently refuse a frame.

The **SEND WIEGAND** button drives W-OUT for real: it runs `/root/ema_wsend`
(`tools/ema_wsend.cpp`) as a subprocess with the port/bits/card/count/gap from
the widgets. That binary opens `/dev/ttySAC0` by itself, so the reader thread
is **parked first** — it finishes its cycle, writes CLOSE, closes the tty and
waits; polling and the lamps freeze during the send and restart on their own
afterward. The result line is a one-word verdict (OK / FAILED + first refusal).
Wire an LED on W-OUT1/W-OUT2 (`+12V → 1k → LED → pin`, open-collector) to watch
one burst per card.

### Relay — CONTROLLED AND CONFIRMED

The relay is driven by command class `04`, which was recovered by disassembling
`CMIMIRDemo` and then confirmed on the hardware.

| | |
|---|---|
| Frame | `55 | 05 | 04 | <selector> | <state>` |
| Relay ON | `55 05 04 01 01` |
| Relay OFF | `55 05 04 01 00` |
| Byte 3 | device selector (`01` = relay) |
| Byte 4 | state (`00` off, `01` on) |

Byte 4 is a **state**, not a pulse: the relay stays energised until the frame
sends `00` back. It **does not** move OUT1 or OUT2 — those are unaffected by
selector `01`.

The STM8 echoes every class-`04` frame back unchanged, so the echo is the
authoritative relay state. The desktop UI relies on that: the button shows what
the board confirmed, not what was clicked.

`tools/ema_blink.cpp` blinks it on demand:
`./ema_blink <cycles> <on_s> <off_s>`

**The GPO headers OUT1/OUT2 are driven by class `03`, not class `04`** — the
verified frame map is in "Output bits" below. Class `02`
(`55 05 02 03 <value>`) is also accepted but still unmapped to any device.

### #9 — Wiegand — mapped as far as the library goes

**Digital, 2-wire** (the user's guess is right — not analog). Idle HIGH with a
pull-up (~5 V typical); a bit is a ~100 µs LOW pulse: `0` = pulse on DATA0,
`1` = pulse on DATA1, ~1 ms between bits, ~20 ms between frames. The same
protocol runs both directions. Headers on the GPI/GPO row: **`W-IN`** (receives
from a reader — front-panel label: the WIEGAND INPUT block is
`+12V OUT · DATA0 · DATA1 · GND`; wire only DATA0, DATA1 and GND to a driver,
the `+12V OUT` pin is a reader supply, never a logic input) and **`W-OUT`**
(`W-OUT1`/`W-OUT2` = DATA0/DATA1, emulates a card toward a reader/controller).

The vendor enum (recovered from CMIMIRDemo strings) is **0-indexed** and the
Wiegand events are **types 2–6** — but the jump-table decode of
`checkWriteEvent` (2026-10-13, see `VENDOR-PROTOCOL.md`) shows the real picture:

| Type | Enum | Frame via `writeEvent` | Verified |
|---|---|---|---|
| 2 | `WIEGAND_READ_DATA` | **none** — serialiser returns `-13` | swallowed |
| **3** | **`WIEGAND_WRITE_DATA`** | **`55 (n+7) 02 01 <b8> <b10 2B> <card nB>` — needs the SET_CONFIG handshake first** | frame decoded |
| **4** | **`WIEGAND_SET_CONFIG`** | **`55 0b 02 02 <b8> <f10> <f12> <f14>` — seeds the session (`this+490 = ev+10`)** | frame decoded |
| 5 | `WIEGAND_GET_CONFIG` | `55 05 02 03 <value>` — value = struct offset 8 | swallowed + live |
| 6 | `WIEGAND_AUTO_DETECT` | `55 05 02 04 <value>` — value = struct offset 8 | swallowed |

**The earlier "types 2–4 never emit" was a session-precondition artefact**, not
a missing implementation. The swallowed scans failed because no SET_CONFIG had
run: `this+490` was 0, so the serialiser returned `-16` (no session) before
building anything. The WRITE_DATA frame *is* implemented — the recipe is:

1. **SET_CONFIG** (type 4): `ev+8` ∈ {1,2}, `ev+10` = bit length (1..265),
   `ev+12`/`ev+14` = timing params (1..50000, `ev+12 < ev+14`) → seeds session.
2. **WRITE_DATA** (type 3): `ev+10` must equal the seeded token, `ev+8` ∈ {1,2},
   card bytes at `ev+16…`, `n = ceil(bitlen/8)`.

The STM8 then pulses **W-OUT1 (DATA0)** for 0-bits and **W-OUT2 (DATA1)** for
1-bits — a Wiegand card transmission.

> **W-OUT is NOT extra GPO.** The vendor code has exactly two GPOs (OUT1/OUT2,
> struct `+49`/`+50`, class-03 via types 17/18/19). W-OUT1/W-OUT2 are the
> Wiegand DATA0/DATA1 lines: you can put arbitrary bit patterns on them via any
> card number, but each write is a ~20 ms burst of ~100 µs pulses, then idle
> HIGH — pulse-encoded, not a latchable contact. "Total 6 GPO" is **not**
> supported; static W-OUT outputs would need the STM8 firmware changed.
>
> **They are one channel, not two outputs** (confirmed by the user's bench test
> 2026-10-14): port 1 and port 2 × both pins, every combination pulses — because
> every card's 0-bits go to DATA0 and 1-bits to DATA1. For two independent
> control lines use OUT1/OUT2.

> **W-IN input path: `U20` = 74HCT08 — photo-verified.** An SOIC-14 at
> silkscreen `U20`, marked **`HCT08`**, photographed beside the W-IN area on
> 2026-10-11 (`docs/photos/2026-10-11_u20-hct08-macro.jpeg`, logged in
> `docs/raw/board-photos-raw.md`). A **74HCT08 quad 2-input AND gate** sits
> between the Wiegand INPUT terminals and the STM8:
>
> - AND is **non-inverting** → polarity unchanged: idle HIGH, active-LOW
>   ~100 µs pulses. The Arduino pulse plan stands as designed.
> - HCT inputs are high-impedance, so the **pull-ups are on-board** — expect
>   **~5 V idle at DATA0/DATA1 with nothing connected** (the meter check that
>   decides whether any external pull-up is needed: likely none). The 5 V rail
>   also re-confirms **Arduino 5 V over ESP32-C3** (3.3 V, not 5 V-tolerant,
>   would idle against that pull-up).
> - W-IN only feeds U20's inputs — the board never drives these terminals, so
>   a push-pull Arduino driver cannot contend with anything.
> - **Open: what each gate's second input does.** Tied to VCC = always
>   enabled; wired to an STM8 pin = software-gated, pulses pass only while
>   enabled. Only 2 of 4 gates are needed for DATA0/DATA1; the other two are
>   untraced. Continuity recipe, board unpowered: HCT08 inputs are pins
>   1,2,4,5,9,10,12,13, outputs 3,6,8,11, VCC = 14 — trace terminal → input,
>   then check whether the partner input reaches pin 14 (via a resistor) or
>   an STM8 pin.

> **PENDING (deferred 2026-10-11):** the read side — W-IN. `55 04 06 01` (type 65, the status-read
> request) has never been answered by the STM8, `WIEGAND_READ_DATA` serialises
> nothing (`-13`), and W-IN testing needs only the **Arduino pulse simulator**
> (D2 → DATA0, D3 → DATA1, GND → GND, ~100 µs LOW pulses, ~1 ms between bits)
> — no logic analyzer: the STM8 assembles the pulses and pushes the card to
> Linux. First check: meter on DATA0/DATA1 with nothing connected, expect
> ~5 V idle (see the U20 note above).


Complete command set. Every state combination verified on hardware
(`tools/ema_uimap.py` 8/8 + `tools/ema_gap.py` 4/4 PASS), then click-tested
end-to-end on the desktop UI by hand.

Frame: `55 0a 03 01 | b4 b5 | 00 00 | b8 b9`
- **b4 / b5** = desired OUT1 / OUT2 contact state (`00` = close to GND, `01` = open)
- **b8 / b9** = per-channel mask (`01` = apply to that channel)

| Action | Frame | Verified |
|---|---|---|
| **OUT1 ON** | `55 0a 03 01 00 <b5> 00 00 01 01` (`<b5>` = OUT2's true state) | all 4 combos |
| **OUT1 OFF** | `55 0a 03 01 01 <b5> 00 00 01 01` | all 4 combos |
| **OUT2 ON** | **two frames**: prep `55 0a 03 01 <a1> 01 00 00 01 00`, then close `55 0a 03 01 00 00 00 00 00 01` | `<a1>` = `00` and `01` |
| **OUT2 OFF** | `55 0a 03 01 <a1> 01 00 00 01 01` | `<a1>` = `00` and `01` |

`<a1>` = OUT1's true state (`00` = ON).

### The two rules that made it work

1. **Always mask BOTH channels (`b8 = b9 = 01`).** Single-mask frames
   (`b8=01, b9=00`) were **silently refused** in some session states: the STM8
   receives them (the status echo register updates) but sends no ack and takes
   no action. The original "type 17 closes OUT1" worked only by luck of session
   history — later it refused the identical frame with zero acks.
2. **OUT2 close needs the prep frame first.** Prep writes `b9=00`, priming the
   echo register; without it the close is refused. This is why the earlier
   "release does not work" conclusion was wrong — those attempts were frames
   the STM8 had decided to ignore.

### Readback — no meter needed

- **Status frame** `55 0a 03 00 | b4 b5 | b6 b7 | b8 b9`:
  **b4/b5 = raw contact OUT1/OUT2** (`00` = shorted = ON), b6/b7 = IN1/IN2,
  b8/b9 = echo of the last request's mask bytes.
- **Request acks** (byte 3 = `01`) also carry the actual b4/b5, so a command is
  confirmed within the same read window instead of waiting for the next status.
- Tell acks from status by **byte 3**: `00` = status (inputs included),
  `01` = request ack (output states only).

### Electrical model

Floating/dry contacts, not driven supplies: power-on floats (8 V decaying,
wandering), 1.7 mV = shorted to GND. LED rig: `12V+ → LED → 1 kΩ → OUT`, one
resistor per LED, anodes toward 12 V. State survives a Linux reboot (the STM8
keeps it) — only a **power cycle** returns the contacts to floating (see
"Why the outputs survive a reboot" below).

The desktop UI (**EMA_Controls**) drives all of it: buttons queue the verified
frames, retries run up to 3x, and the display follows the board's report —
never the click.

## After the digital outputs

- **Wiegand in/out** — vendor enum lists `WIEGAND_READ_DATA`, `WIEGAND_WRITE_DATA`,
  `WIEGAND_SET_CONFIG`, `WIEGAND_GET_CONFIG`, `WIEGAND_AUTO_DETECT`. **Mapped
  2026-10-09** (swallowed scan, see \"Wiegand\" below): event types **2–6**.
  `GET_CONFIG` (5) and `AUTO_DETECT` (6) emit class-02 frames; the other three
  are dropped by libemaLib's serialiser entirely.
- **Analog I/O — does not exist on this board (user, 2026-10-14).** No analog
  section; the WM8960 audio codec is the only analog-class peripheral and it
  already works. The old hint (vendor's float-heavy `writeEvent` loop writing
  **30** `0x1e`, read as a 0–100 scale for a class-`04` analog-output command)
  is **retired** — there is no analog device on this board for it to address.

## Why the outputs survive a reboot

**The STM8S207 is a separate microcontroller with its own reset domain.** A Linux
`reboot` resets the Exynos only — the STM8 keeps running, keeps its GPIO state,
and keeps whatever configuration it was last given. This was verified by the
user noticing that OUT1/OUT2 stayed as they were across a full Linux reboot.

So to return the outputs to their power-on state you must remove power to the
board (or reset the STM8 specifically). **A software reboot cannot do it.**

There is `/dev/watchdog` on the Exynos side, but nothing exposed that resets the
STM8 — no sysfs node, no driver. From Linux the only handles on the STM8 are the
serial link itself.

### The floating reading

OUT1 has been observed at **1.7 mV**, **~2.0 V** and **~8.x V** in different
states. That spread is the signature of a **floating contact**: the meter's
reading depends on the STM8's current state, on what load is attached, and on
leakage paths — not on a fixed supply. Treat any single reading as provisional
and always compare against a known state.

## Command vocabulary — complete for event types 1–40

Enumerated with `tools/ema_tscan.cpp` under the swallowing shim, so **not one
byte of this reached the STM8**. Every frame is produced purely by the event type
in struct offset +4:

| Event type(s) | Frame emitted | What it is |
|---|---|---|
| 1 | `55 04 01 01` | open |
| 5 | `55 05 02 03 00` | class 02, op 03, value 0 |
| 6–15 | `55 05 02 04 00` | class 02, op 04 — **the STM8 ignores these** |
| **17** | `55 0a 03 01 00 00 00 00 **01 00**` | closes OUT1 |
| **18** | `55 0a 03 01 00 00 00 00 **00 01**` | releases OUT2 |
| **19–31** | `55 0a 03 01 00 00 00 00 **01 01**` | releases OUT1 |
| 32–39 | `55 05 04 00 00` | class 04 with selector 0 |
| 40 | `55 04 01 00` | close |

**Two facts that matter, and both contradict earlier assumptions:**

1. **There is no `...00 00` frame.** OUT2 *closed* does not exist in this
   vocabulary, so the "byte 8 = output, byte 9 = state" reading is wrong. The two
   bytes are not free parameters.
2. **The event type fully determines the frame.** Thirteen types (19–31) collapse
   to the same bytes. Struct offsets 53/54 are **ignored** for this family — they
   only affect class `04`. Setting them changed nothing, and one tool printed its
   *intended* frame rather than the transmitted one, which hid that.

### Where the real parameters must be — tested and ruled out

The obvious hypothesis was that payload bytes 4–7 (`00 00 00 00` in every frame)
are populated by some struct offset we had not found. **Tested directly**
(`tools/ema_p4.cpp`, type 19 pinned, offsets 0–200 swept one byte at a time,
writes swallowed — **nothing transmitted**):

> **1 offset out of 199 changed the frame at all**, and offset +200 sits past the
> end of the struct (it produced the close frame, i.e. a read overrun).

**So the class-`03` frame has no hidden parameters.** `55 0a 03 01 00 00 00 00 01 01`
is the complete, whole frame for type 19. There is no unset field waiting to be
filled — the "payload bytes 4–7 must be the real parameters" idea is **dead**.

### What that leaves

> **Superseded:** the "release does not work" conclusion below was **wrong** and
> is kept only as history. The state lives in bytes 4/5 of the frame (not in the
> event type), and OUT2 close needs a prep frame first — see **"Output bits —
> SOLVED"** above. What this scan *did* establish stands: the event type alone
> does not fill bytes 4–7.

- **Closing OUT1 works and is reproducible** from a floating power-on state:
  type 17 → `55 0a 03 01 00 00 00 00 01 00` → contact shorts to ground.
- **Releasing does not work.** Type 19's frame is sent whole, 80 times, and
  acknowledged 79 times, yet the contact stays closed.
- Therefore the release is **not in this vocabulary**. Either the event type that
  releases the output lies outside 1–40, or the GPOs are driven by a mechanism
  this write path never reaches. The vendor GUI having only **one** `writeEvent`
  call — and it being the relay — supports the second reading.

## Gotchas

- **A `QCoreApplication` is mandatory** when using `libemaLib`. It delivers
  reads through a `QSocketNotifier`, which does nothing without a running event
  loop — without one, `readEvent()` returns `-9` forever and the warning
  *"QSocketNotifier: Can only be used with threads started with QThread"*
  appears.
- **`readEvent()` is not a passive poll.** It returns `-9` until a read is armed
  with `setReadEvent()`. Do not read `-9` as "no data"; it means "nothing armed".
- **The STM8 does not stream status.** It answers open, then goes quiet. A
  60-second capture got the ack and exactly one status frame.
- **`gcc 4.6` rejects `-std=c++11`**; the accepted spelling is `-std=c++0x`.
  Its default C mode is C89, so `for (int i = ...)` is an error in `.c` files.
- **`/dev/ttySTM8` is a trap.** A symlink to `/dev/pts/0`, not a device.
- **`/dev/ttyS0..3` are phantoms** — `port:00000000 irq:0`, no hardware.
- **`ttySAC1` is the kernel console.** Disturbing it can hang the board. Every
  tool here excludes it. Note the link is `ttySAC0`, **not** `ttySAC1`.
- **Two cores are dead.** cpu1/cpu2 drop straight back to 0 if enabled; cpu3 was
  offlined to stop a boot loop. 2 of 4 cores is the ceiling.
- **RAM looked 92% used** (916 MB of 991 MB), no swap. Unverified snapshot.
- **Kernel is from 2014** (`3.0.68`): no `macb`/`dwmac`, no `gpiochip`, no
  `/sys/class/gpio`. Any "just install libgpiod" plan fails — the kernel side is
  what is missing.
- **The 93LC66A chips are on no SoC bus — and never were.** Scanning I2C for
  them was the wrong question: #1 hangs off the LAN9512's own Microwire pins and
  the chip itself reads it at power-up (`ethtool -e eth0` dumps it), and the
  kernel has *no SPI at all*. `i2cdetect` is still uninstalled and irrelevant
  for them.
- **The STM8 silently refuses some valid-looking frames.** It receives them (the
  status echo register updates) but sends **no ack and takes no action**. Never
  treat a send as success — confirm from status/ack and retry. The UI does this
  by design (3 retries, then "board did not respond").
- **Single-mask GPO frames and an unprimed OUT2 close are refused** — always
  mask both channels and use the prep-frame recipe (see "Output bits").
- **Acks and status frames are both 10 bytes** — tell them apart by byte 3:
  `00` = status (carries the inputs), `01` = request ack (carries actual output
  states only).
- **The device tree is stripped** — `model`/`compatible` empty, `Hardware` reads
  only `ODROIDX`.

## Not proven / open

- **The `_EMA_EVENT` layout is only partly known.** Offset +4 = event type and
  offsets 53/54 feed class-`04` frames — but class-`03` frames ignore struct
  offsets entirely (199-offset sweep moved nothing); bytes 4/5 are chosen by
  the *caller*, which is why hand-assembled frames work.
- **Class-`02` (`55 05 02 03 <value>`) is accepted but unmapped** — replies
  carry varying data (`1a 00 64 00 4c 04`); no device identified. **Update
  2026-10-09: op `03` = `WIEGAND_GET_CONFIG` (type 5), op `04` = the
  AUTO_DETECT/GPO/relay family (types 6–15)**, value = struct offset 8 — so
  this *is* the Wiegand config channel; what each value means is unknown (#9).
- **The combined input state is untested.** Bridging IN1 and IN2 together should
  yield `55 0a 03 00 01 01 00 00 00 00`, a frame never yet seen. That would prove
  the two bits are independent rather than merely correlated.
- ~~Where the two 93LC66A EEPROMs are wired.~~ **#1 answered — the LAN9512's
  config EEPROM, dumped with `ethtool -e eth0` (see #14).** #2's master is
  still unknown: no SoC-side path exists (no SPI, all I2C devices named), so
  the open question is its **physical location** on the board.
- **The RTC fix has not been run.** `hwclock --systohc` would initialise the
  date registers, but it is a write and awaits the user's go. Unexplained:
  who set the system date correctly at boot when `hctosys` failed and no NTP
  runs; and whether a battery holds the RTC across a power cut.
- ~~Whether RS232/RS485 sit on the STM8 or bypass it to the SoC.~~ **RS232:
  answered — it bypasses the STM8 entirely, `/dev/ttySAC3`.** RS485 still open.
- **Wiegand** — enum types 2–6 recovered (`WIEGAND_READ_DATA`, `WRITE_DATA`,
  `SET_CONFIG`, `GET_CONFIG`, `AUTO_DETECT`); GET_CONFIG (5) / AUTO_DETECT (6)
  frames mapped under the swallowing shim 2026-10-09. **WRITE_DATA (3) and
  SET_CONFIG (4) frames decoded 2026-10-13 from the checkWriteEvent jump
  table** (see §9 and `VENDOR-PROTOCOL.md`): WRITE needs a SET_CONFIG handshake
  first — the earlier "emits nothing" was the missing session, not a missing
  implementation. W-OUT = DATA0/DATA1 pulse lines (not static GPO).
  **Live since 2026-10-13** (`tools/ema_wsend.cpp`), click-tested 2026-10-14
  (both ports × both pins). The read side (W-IN) is **pending** (deferred
   2026-10-11) — a scope/logic
  analyzer + Arduino pulse simulator are needed to simulate a reader. Raw:
  `docs/raw/wiegand-frames-raw.md`, `wiegand-frames2-raw.md`,
  `wiegand-send-raw.md`.
- **Analog I/O — CLOSED, does not exist (user, 2026-10-14).** No analog section
  on this board; the WM8960 audio codec is the only analog-class peripheral and
  it already works (row 10). The old "float-heavy loop writing `30`" lead was
  based on a wrong assumption — retired.

## Micro-USB / ADB — CLOSED (no further work)

**Decision: closed 2026-10-11.** Fully diagnosed both modes; nothing more to
probe. Use **LAN/SSH** for all work.

- **It is not a driver problem — on either PC, in either mode.**
  - *Normal mode:* board attaches but **no gadget function exists** (kernel
    config proves it) → enumeration dies → Windows Code 43, Linux `-110/-71`.
  - *Android mode:* enumerates cleanly (`18d1:0002`, `FF/42/03` = ADB) but raw
    protocol probes get a flat 4-byte `FAIL` to CNXN/SYNC/AUTH/garbage/even
    silence — a stub, not a 24-byte-header adbd.
- **Normal mode's micro-USB cannot be fixed without a kernel rebuild**
  (3.0.68, configfs gadgets don't exist, all `g_*` functions disabled) —
  **accepted as-is, rebuild not pursued.**
- **Do not reopen:** no PC drivers to chase (proven on both OSes), no configfs
  to mount, no gadget to bind. Revisit only if a kernel rebuild is ever approved.

## Next step

**Done:** link found, inputs decoded, relay controlled, OUT1/OUT2 ON+OFF solved,
all of it on the desktop UI (**EMA_Controls**).

1. **Wiegand read side (W-IN)** — **PENDING (deferred 2026-10-11)** — send side
   is WORKS; receiving a card needs a scope/logic analyzer + Arduino pulse
   simulator. Parked to make room for the main board work; plan is intact in §9.
2. ~~Analog I/O~~ — **closed: no analog section on this board (user,
   2026-10-14).** Audio (WM8960) is the only analog-class peripheral and it
   already works.
3. **RJ45 #2** — now believed to be a plain second port on the KSZ8995XA switch
   (same `eth0`), not an STM8 job. **Run the cable test**: live cable in #2
   against `ethtool eth0`, then the same in #1 as a control. If #2 lights `eth0`
   the switch reading is confirmed and this row closes. **RS485's receive path**
   still needs a real device attached (TX is proven, `rx` never moved).
4. **Initialise the RTC** — one `hwclock --systohc` (write; user's go), reboot,
   confirm `hctosys`, then test the coin cell's hold across a power cycle.
5. **Identify 93LC66A #2's owner** — location known (LAN section, beside the
   LAN9512 and the KSZ8995XA switch). The switch is the leading candidate but is
   *unproven*: it wants a 2-wire I²C config EEPROM, and a 93LC66A is a 3-wire
   Microwire part. The same RJ45 #2 cable test is the first evidence either way.
