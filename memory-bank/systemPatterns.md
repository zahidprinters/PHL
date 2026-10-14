# System Patterns

Architecture, and the decisions behind it. Structure detail lives in
`docs/ARCHITECTURE.md`; this file explains *why* the structure is that way.

## Architecture
Two processors, and that is the whole problem:

- **Exynos 4412** runs Linux. It has audio, HDMI, eMMC, USB and one Ethernet.
- **STM8S207** is a microcontroller that owns the industrial I/O: GPI/GPO
  (IN1/IN2, OUT1/OUT2), RJ45 #2, Wiegand, the EEPROMs.

They talk over one serial link: **`/dev/ttySAC0` @ 115200 8N1** — found. The
protocol (framing, event types, GPO/relay commands) was recovered from
`libemaLib` disassembly plus live traffic, and everything digital is now driven
from Linux. The remaining open STM8 items (Wiegand read side, RJ45 #2) still
need their request formats built on the same channel. There is **no analog
I/O** on this board (user, 2026-10-14) — audio (WM8960) is the only
analog-class peripheral and it already works.

**RS232 and RS485 are the exception — neither ever went through the STM8.**
They are direct Linux UARTs on `/dev/ttySAC3` and `/dev/ttySAC2` respectively,
each proved with a control run. Do not re-derive this from older notes that
said otherwise.

**The four UARTs, settled:**

| device | role | how proved |
|---|---|---|
| `ttySAC0` | STM8 link | `[TRACE] open()` + live acks |
| `ttySAC1` | kernel console | `console=ttySAC1,115200n8` — never open |
| `ttySAC2` | **RS485** | meter across D+/D−: 0.646 V → 220 mV while TX |
| `ttySAC3` | **RS232** | TX↔RX jumper echoed `RS232LB` |

## Design decisions
- **2026-10-10 - Facts are measured, never remembered.** Every claim in
  `docs/BOARD.md` is backed by saved raw output in `docs/raw/`, regenerable with
  one command. Early notes drifted badly enough to send us down three wrong
  paths; prose claims cannot be trusted on a board like this. (supersedes: relying
  on accumulated notes)
- **2026-10-10 - All probes are strictly read-only.** No writes, no register
  pokes, no ports opened. A headless HVAC controller with VNC-only recovery is
  not a machine to experiment on.
- **2026-10-10 - The console UART is excluded everywhere.** `ttySAC1` is
  `console=`; touching it can hang the board with no way back.
- **2026-10-10 - Dead work is archived, not deleted.** `archive/` holds the
  Dynalite and ECU-30 work. One `Remove-Item` discards it; nothing is lost now.
- **2026-10-10 - Attack the link before the peripherals.** The SoC<->STM8 link
  unblocks 6 items at once; working peripherals individually cannot start.
- **2026-10-10 - Reuse `libemaLib` rather than reverse the protocol.** It already
  exports `EMAMain::open/writeEvent/setReadEvent/checkWriteEvent`. Driving it
  through ctypes beats guessing an undocumented frame format.
- **2026-10-10 - A send is never success.** The STM8 silently refuses some
  valid-looking frames: received (echo register updates), zero ack, no action.
  Every actuation is confirmed from status/ack and retried — this rule was
  written after silent refusals produced two false "does not work" conclusions.
- **2026-10-10 - The swallowing shim (`nullwrite.c`) before any live frame.**
  Capture what the serialiser *would* send, print it, transmit nothing. It is
  how the protocol was learned without actuating a live HVAC controller.
- **2026-10-10 - Desktop UI displays the board's report, never the click.**
  Buttons queue commands; lamps/buttons flip only when an ack or status
  confirms. Same contract for inputs, outputs and relay (EMA_Controls).

## Patterns in use
- One SSH session per tool; a list of `(heading, command)` pairs; print
  `stdout or stderr` per section so a silent failure is visible.
- **A section that raises is reported, never skipped silently.** On a 13-section
  survey, one swallowed exception hides the other twelve.
- Evidence is saved, not just summarised. `docs/raw/` is the audit trail.

## Critical paths
- **The serial link (`ttySAC0` @ 115200)** — every remaining peripheral runs
  over it. Never open it from two programs at once (the UI holds it).
- **SSH access** — lose it and there is no recovery but a power cycle.

## Component relationships
- `tools/board_inventory.py` writes `docs/raw/BOARD-raw.md`; `docs/BOARD.md` is
  the interpretation written on top of it. Regenerate, never hand-edit the raw.
- `tools/board_facts.py` and `tools/board_stm8_link.py` exist because the main
  survey could not settle three specific questions. They are not general-purpose.