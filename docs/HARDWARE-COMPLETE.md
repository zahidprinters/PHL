# Board — complete hardware picture (what we have, how it works)

The single reference for everything on this board, measured over SSH on
2026-10-12. Raw evidence: `docs/raw/board-full-survey-raw.md` (full `dmesg`,
`lsmod`, `iomem`, kernel config, EEPROM dump, interrupts, vendor packages).
This is the *current vendor-OS board* — an Exynos 4412 Linux host plus an
STM8S207 that owns the industrial I/O.

> Boot snapshot for analysis: `docs/raw/board-full-survey-raw.md`
> (`@@@ dmesg-boot @@@`), plus the earlier serial boot capture in
> `docs/raw/debug-port-boot-raw.md`.

---

## 1. Identity

| | |
|---|---|
| Product | Daikin **CMIMIR / Intelligent Manager** HVAC controller |
| Main SoC | **Samsung Exynos 4412** — ARM Cortex-A9, ARMv7, up to 1.0 GHz, **2 of 4 cores online** |
| MCU | **STM8S207** — owns the industrial I/O (digital in/out, relay, Wiegand) |
| RAM | **991 MB** (`mem=1023M`), **no swap** |
| Kernel | **3.0.68** `#11 SMP`, Hardkernel/`mkjasia` build, **2014** |
| Kernel style | **Board-file, NOT device-tree** — `/proc/device-tree` is empty, `Hardware=ODROIDX`. Board wiring is hard-coded in C, not a DTB. |
| OS | **Linaro 12.11** (Ubuntu 12.04 *precise*), `armv7l` |
| Root storage | **SD card** (`mmcblk0`, eMMC removed): `p1` boot 128 MB · `p2` root 5.4 GB (2.1 GB free) · `p3` `/data` 54 GB (51 GB free) |

## 2. The two processors, and the one link between them

```
   Exynos 4412 (Linux)                    STM8S207 (vendor firmware)
   ─────────────────────                  ─────────────────────────
   audio, HDMI, USB, LAN, RTC,   serial   IN1/IN2, OUT1/OUT2,
   eMMC/SD, display, buttons  <-------->  relay, Wiegand
                                        (ttySAC0 @ 115200 8N1)
```

- **Link = `/dev/ttySAC0` @ 115200 8N1.** Framing + event types recovered from
  `libemaLib` disassembly + live traffic. **IN1/IN2, OUT1/OUT2 (ON+OFF) and the
  relay all work** and are driven from Linux (desktop app **EMA_Controls**).
- **RS232 = `/dev/ttySAC3`, RS485 = `/dev/ttySAC2`** — these **bypass the STM8**;
  they are direct SoC UARTs (each proved with a control run).
- `/dev/ttyS0..3` are **phantoms** (8250 stubs, no hardware). `/dev/ttySTM8` is a
  symlink trap.

## 3. SoC built-in hardware resources (the inventory)

From `iomem`, `/proc/interrupts`, and the kernel config. "Linux-usable?" answers
whether stock Linux can touch it today.

| Block | Controller / address | Driver in kernel | Linux-usable? |
|---|---|---|---|
| **UART x4** | `s5pv210-uart.0-3` @ 0x1380_0000 | `SERIAL_S5PV210=y` | yes `ttySAC0-3` (see §2) |
| **I2C x5** | `s3c2440-i2c.0,1,4,5` + hdmiphy | `I2C_S3C2410=y` | yes, 7 devices (see §4) |
| **ADC** | `exynos4412-adc` @ 0x126c_0000 | **`# CONFIG_S3C_ADC is not set`** | **no** — hardware present, no driver; 4-ch/12-bit, untapped |
| **PWM** | `s3c24xx-pwm` (4 ch) | `S3C24XX_PWM=y`, `HAVE_PWM=y` | partial — driver present, no board binding exposed |
| **GPIO** | GPA0..GPV4 (~250 pads) | **no `GPIO_SYSFS`, no `PINCTRL`** | **no** — no sysfs/debugfs control; pads physically exist |
| **RTC (SoC)** | `s3c64xx-rtc` @ 0x1007_0000 | built-in | a *second* RTC on the SoC (rtc0 = external MCP7940N) |
| **Watchdog** | `s3c2410-wdt` | `S3C2410_WATCHDOG=y` | present, `inactive, reset disabled` |
| **Thermal (TMU)** | `tmu` @ 0x100c_0000 | `EXYNOS_THERMAL=y` | yes, throttles 82->110 C |
| **eMMC** | `dw_mmc` @ 0x1255_0000 | built-in | yes (eMMC currently removed) |
| **SD x2** | `s3c-sdhci.2/.3` | built-in | yes, `mmc1` = SD card |
| **USB host** | `s5p-ehci` + `s5p-ohci` | built-in | yes, 1x USB2.0 + 1x USB1.1 |
| **USB OTG (device)** | `s3c-udc` @ 0x1248_0000 | `S3C_OTGD=y`, **no `g_*` gadget** | **no** — micro-USB CLOSED (no gadget built) |
| **Display** | `s3cfb` + `s5p-hdmi` + `s5p-mixer` | built-in | yes, fb0-7, HDMI + mixer layers |
| **Audio I2S** | `samsung-i2s.0` @ 0x0383_0000 | built-in | yes, feeds WM8960 |
| **DMA x3** | `s3c-pl330` | built-in | yes |
| **Bluetooth** | USB BT stack | `btusb`, `rfcomm` | stack present, no module attached |
| **IR remote** | `lirc_dev` (major 252) | built-in | driver present, no IR sensor seen |
| **PMIC** | `max77686` (I2C 0-0009) | `MFD_MAX77686=y`, `REGULATOR_MAX77686=y` | yes, all power rails + 12 V header |

**GPIO claimed today (only 5):** STATUS LED (gpio-31, out hi), Backlight
(gpio-38), KEY POWER (gpio-202), hdmi-cec (gpio-223), hpd-plug (gpio-224).
Everything else is an **unclaimed pad** — real silicon, unreachable from Linux
without a kernel change (no gpiochip, no pinctrl).

## 4. External chips (measured on the board)

| Chip | Bus / ID | What it is | Status |
|---|---|---|---|
| **STM8S207** | `ttySAC0` | industrial-I/O MCU | digital I/O + relay work |
| **WM8960** | I2C `1-001a` | audio codec + Class-D speaker amp | play + capture (`card 0 Ctis_wm8960`) |
| **MCP7940N** | I2C `1-006f` | RTC | alive, date = **2001-01-01** (never set) |
| **max77686** | I2C `0-0009` | PMIC | all power rails |
| **usb3503** x2 | I2C `0-0008`, `1-0008` | USB hub controllers | yes |
| **LAN9512** | USB `0424:9512` + `0424:ec00` | USB 2.0 Ethernet | `eth0`, 100 Mb/s full-duplex, MAC `00:25:ff:fe:44:45` |
| **KSZ8995XA** | (from photos) | 5-port switch -> 2x RJ45 | both jacks = `eth0` |
| **93LC66A #1** | LAN9512 Microwire | config EEPROM | dumped (`ethtool -e`): `0xA5` sig, MAC, USB IDs, `SMSC` |
| **93LC66A #2** | near LAN9512 | second EEPROM | owner unproven (no SoC SPI; kernel has no SPI at all) |
| **H26M42003GMR** | eMMC | 8 GB storage | backed up (`os/backup-eMMC/`), removed |
| I2C `0-0006` | bus 0 | unidentified device | not yet identified |

**Kernel has no SPI at all** (`# CONFIG_SPI is not set`, `# CONFIG_EEPROM_93CX6
is not set`) — which is why the 93LC66A EEPROMs are invisible to the SoC and are
loaded by their own master chips.

## 5. Front-panel buttons

Handled by the vendor **`odroid-keypad`** input driver — `input0` / `event0`,
`Vendor=16b4 Product=0701`, `CONFIG_KEYBOARD_ODROID=y`. The three physical
buttons (reset / F-reset / unnamed) are GPIO keys on this driver. **They do not
go through the STM8.** To map button->keycode: read `event0` while pressing.

## 6. Vendor (Daikin) stack

| File | Size | Role |
|---|---|---|
| `/usr/local/bin/CMIMIRDemo` | 127 KB | vendor GUI (wants a CMI iris imager — not attached) |
| `/usr/local/lib/libemaLib_arm_1.0.1.so` | 47 KB | **EMA protocol lib** — reverse-engineered; exports `EMAMain::open/writeEvent/...` + a C API |
| `/usr/local/lib/libcmirisLib2_arm_2.0.92.so` | 1.06 MB | iris/color imaging |
| `/usr/local/lib/libcmicolorLib_arm_0.9.0.so` | 47 KB | color |
| (all dated **May 2014**) | | backed up to `vendor-backup/` with SHA256 |

Key installed packages: `python-qt4` (the only GUI toolkit — EMA_Controls),
`vino` (VNC, made headless-safe), `xrdp` (RDP), `pulseaudio`, `unity`,
`qt4-dev-tools`/`qt4-designer`, `stress`, Linaro dashboard tools.

## 7. What WORKS today vs. what is untapped

**Working, driven from Linux:** STM8 link · IN1/IN2 · OUT1/OUT2 (ON+OFF) ·
relay · RS232 (`ttySAC3`) · RS485 (`ttySAC2`, TX) · WM8960 audio · RJ45 #1
(`eth0`) · 93LC66A #1 · USB host · HDMI/display · SD storage · debug/console
port (`ttySAC1`, 1.8 V).

**Untapped potential (silicon is there, Linux can't reach it yet):**
- **Analog input** — the Exynos **4-ch/12-bit ADC** (`exynos4412-adc`) has **no
  driver**. If ADC pins are bonded out to a header, this is a real analog-in
  path (needs a small kernel driver).
- **PWM output** — 4 PWM timers exist (`s3c24xx-pwm`); usable for dimming /
  soft analog-out via an RC filter, if bound to pins.
- **GPIO** — ~250 pads, 5 used. A kernel change (gpiochip/pinctrl) would expose
  the rest — but many belong to the STM8's domain.
- **Second RTC** — the SoC's own `s3c64xx-rtc`, independent of the MCP7940N.
- **Buttons** — `event0` gives all three as key events (undecoded keycodes).
- **Bluetooth / IR** — stacks present, no modules attached.
- **Wiegand** — LINK FOUND; WRITE_DATA frame **decoded 2026-10-13** (needs a
  SET_CONFIG handshake first — see `docs/VENDOR-PROTOCOL.md`). Not yet sent
  live.

## 8. Known constraints (do not re-learn these)
- **Board-file kernel, no device tree** — wiring is in C; there is no DTB to edit.
- **No SPI, no gpiochip, no pinctrl, no ADC driver, no USB gadget.**
- **2 of 4 cores permanently offline**; 991 MB RAM, no swap.
- **STM8 state survives a Linux reboot** — only a power cycle resets it.
- **`ttySAC1` is the console** — never open it from a tool; it holds `login`+`bash`.
- Kernel is from **2014**; `dist-upgrade` would remove the desktop — don't.
  **A release upgrade to 14.04.6 is offered by `do-release-upgrade` but was
  checked and REJECTED (2026-10-11):** same desktop-removal outcome, trusty is
  EOL too (2019/2024), kernel/driver set unchanged (3.0.68 stays either way),
  zero hardware gained. Details in `CHANGELOG.md`.
