# Board photos — 2026-10-09

Six photos supplied by the user 2026-10-09 (`docs/photos/`). Two show the
CM4412 CPU module, three show the carrier board, one is a byte-identical
duplicate. A seventh, `IMG_20261011_153945.jpg` (2026-10-11), shows the
enclosure front-panel label — see the last section.

    Get-FileHash docs\photos\*.jpeg -Algorithm SHA256
    carrier-3.jpg == carrier-3-duplicate.jpg   C951CB70… (same file, twice)

## Carrier board — `CMITECH ECU Rev 1.2`

Silkscreen, top-right of the board: **`CMITECH` / `ECU Rev 1.2`**.

### The LAN section (top-right quadrant) — THIS IS THE FINDING

Two RJ45 jacks sit side by side, labelled in silkscreen **`LAN1`** and
**`LAN2`**. Directly to their left is one large square QFP, legibly marked:

    MICREL
    KSZ8995XA
    1249M2      ← date/lot: 2012, week 49
    M9242030
    MO2062U0

**A Micrel/Microchip KSZ8995XA — an integrated 5-port 10/100 QoS Ethernet
switch.** This is the "companion network chip" that #2's owner was suspected to
be. It has five MAC+PHY pairs on one die, so two RJ45 jacks hanging off a single
NIC is exactly what it is for.

The photos put it in the same few square centimetres as the LAN9512 and both
jacks — which is precisely where the user said the second 93LC66A lives.

Datasheet (KS8995XA rev 2.6, `docs/raw/ksz8995xa-datasheet.txt`) confirms the
mechanism:

- Functional diagram contains a dedicated **`EEPROM I/F`** block.
- *"The KS8995XA functions as an unmanaged switch. If no EEPROM exists, the
  KS8995XA will operate from its default and strap-in settings."*
- *"If a 2-wire EEPROM exists, the KS8995XA can perform more advanced features
  like broadcast storm protection and rate control."*
- *"The chip starts automatically after trying to read the external EEPROM. If
  EEPROM does not exist, the chip will use default values for all internal
  registers."*
- Config EEPROM is read automatically at power-up, over the `SCL`/`SDA` pins
  (pin 110 `SCL`, pin 111 `SDA`), i.e. a **2-wire I²C EEPROM**.
- Config registers are `0`–`109` — fits a 2 Kbit (93LC56) or 4 Kbit (93LC66)
  device easily.

> **Caveat, stated plainly.** The KSZ8995XA's config EEPROM is a 2-wire part.
> A 93LC66A is a 3-wire Microwire part. They are not the same bus. So #2 is
> *not* proven to be the switch's config EEPROM, and the two chips are
> different parts. What the photos establish is: a real 5-port switch exists,
> it is the only chip that can make two jacks one NIC, and it is physically in
> #2's neighbourhood. That makes the switch the leading candidate for what #2
> configures — and it retires the "RJ45 #2 is on the STM8" theory. It does not
> make #2 proven. The deciding test is unchanged: a live cable in **RJ45 #2**
> watched against `ethtool eth0`.

### The RTC battery — answers an open question

A **coin cell in a through-hole holder sits immediately left of the CM4412
module**, marked `38` on the cell, next to silkscreen `F-RST`. That is the
MCP7940N's backup battery (#17), and it is the physical answer to "does a
battery hold the clock across a power cut" — the hardware is there. Whether it
still holds a charge is untested; a load test is needed.

### Other port labels read off the silkscreen

`STATUS` (LED, top-left) · `LAN1` · `LAN2` · `PWR` · `USB1` `USB2` `USB3` ·
`+12V` `+12V` · `W-OUT1` `W-OUT2` · `GPO` · `IN1` `IN2` · `RS485` (green 3-pin,
bottom-right) · `F-RST` (reset button) · micro-USB (bottom-left) · HDMI
(bottom-right) · microSD (bottom-centre, a SanDisk Ultra is fitted).

Left edge: a long green screw-terminal block — the GPI/GPO header row.
A white barcode sticker reads **`CM4412` / `CTE03095`**.

## CPU module — `CMITECH CPU MODULE Rev 1.0`, 2014.02.04

A separate daughtercard plugged into the carrier:

| | |
|---|---|
| Silkscreen | `CMITECH CPU MODULE Rev 1.0` / `2014.02.04` |
| SoC | **Samsung Exynos 4412**, marked `Exynos` `4412 ARM ACA` `S1T5W11` `GREEN MEMORY` |
| Sticker | `CM4412` / `CTE03095` |
| Crystal | a can marked **`X32K`** — the 32.768 kHz RTC reference |
| Passives | rows of `C…`/`R…` around the SoC; a second bare die above the Exynos (PoP memory) |

This is a CMITECH CM4412 system-on-module — Exynos 4412 + RAM on one card. It
explains the `CM4412` string already seen in the vendor binaries.

## What this changes

| Was | Now |
|---|---|
| RJ45 #2 "almost certainly wired to the STM8" | **Retired.** A KSZ8995XA 5-port switch is the far better explanation for two jacks on one NIC |
| 93LC66A #2's owner "unknown, likely STM8-side" | **Leading candidate: the KSZ8995XA switch**, still unproven |
| "does a battery hold the RTC?" | **A battery holder is physically present** — charge untested |

Nothing here was measured on the running board; these are photographs. The
deciding test for #2 is unchanged — a live cable in **RJ45 #2** against
`ethtool eth0`.

## Front-panel label — `IMG_20261011_153945.jpg` (2026-10-11)

The enclosure's printed label. Its MAC `00:25:FF:FE:44:45` equals `eth0` —
same unit. Terminal blocks as printed (rotation makes exact pin order hard
to read from the photo; **confirm order on the physical block before
wiring**):

| Block | Pins |
|---|---|
| `INPUT` (+12VDC) | `PG` · `GND` · `+12V` |
| **`WIEGAND INPUT`** | **`+12V OUT` · `DATA0` · `DATA1` · `GND`** |
| `WIEGAND OUTPUT 1` | `GND` · `DATA1` · `DATA0` |
| `WIEGAND OUTPUT 2` | `GND` · `DATA1` · `DATA0` |
| `GPO` | `OUT1` · `OUT2` · `GND` |
| `GPI` | `IN1` · `IN2` · `GND` |
| `RS-232` | `RX` · `TX` · `GND` |
| `RS-485` | `D+` · `D-` |
| `RELAY` | `NO` · `C` · `NC` |

Also printed: `Power` / `Ethernet` / `Status` LEDs · `WAN` + `LAN` TCP/IP ·
USB 1–4 (USB 1 bracketed as `IRIS Camera`) · `AUDIO OUT` (`LEFT`/`RIGHT`) ·
`RESET` · sticker `CMITECH / IRIS CAMERA / ECU-30 / 12V 2A / FA1405A001008 /
MADE IN KOREA`.

**The `+12V OUT` pin on the WIEGAND INPUT block is a reader supply** — leave
it unconnected when driving DATA0/DATA1 from a logic device.

## Wiegand-area photos — four WhatsApp images (2026-10-11, evening)

Supplied by the user the same day as the front-label shot; moved from the
project root to `docs/photos/` with meaningful names:

| File | What it shows |
|---|---|
| `2026-10-11_ecu30-top-powered.jpeg` | Full carrier top view, **board powered** (STATUS + LAN LEDs lit). Terminal-row silkscreen readable: `W-IN` · `W-OUT1` · `W-OUT2` · `GPO` · `GPI` · `RS232` · `RS485-1` · `RS485-2`. KSZ8995XA, coin cell, CM4412 sticker, heatsink all visible |
| `2026-10-11_w-in-area-wide.jpeg` | W-IN area close-up: silkscreen **`U20`** beside an SOIC-14 marked `HCT08 / 10 12 / n408`, with `C144` `C136` `C137` `FB20` `C152` nearby; `Q8`/`Q9` (marking `W42`) + `R128`/`R129` below |
| `2026-10-11_wiegand-area-wide.jpeg` | Wider Wiegand strip: `U20` sits between `L12` and the `W-OUT1`/`W-OUT2` transistor groups (`Q8`–`Q11`, all `W42`); `U15`/`U16` marked `93S3Y`/`93829` near W-OUT2 — likely the W-OUT drivers |
| `2026-10-11_u20-hct08-macro.jpeg` | Macro of U20: pin-1 dot visible, legible `HCT08` marking — **the photo that verifies the chip identity** |

**This confirms the user-reported finding: silkscreen `U20` carries a chip
marked `HCT08`** — a 74HCT08-class quad 2-input AND gate in SOIC-14 — sitting
right where the W-IN input path was expected (next to `FB20`/`C152` on the
W-IN side). What the photos do **not** settle: where each gate's second input
goes (VCC-tied vs STM8-gated) — that still needs the continuity recipe in
`docs/BOARD.md` §9. `R128`/`R129` and `FB20` are candidates for the on-board
pull-ups / input filtering but are untraced; do not treat their presence as
proof of the pull-up location.
