# Wiegand WRITE_DATA — live send evidence (raw captures)

Board: 192.168.100.127 (/root)  Tool: `tools/ema_wsend.cpp`  Date: 2026-10-13
Two phases: swallow run (`nullwrite.so`, STM8 received nothing) then live runs
(`opentrace.so`, frames transmitted and echoed back).

## Phase 1 — swallow run (frame recipe verification)

    $ LD_PRELOAD=./nullwrite.so ./ema_wsend 2 24 AAAAAA 2 300
    === opening link ===
    [OPEN] open("/dev/ttySAC0")
    [FRAME 1] 4 bytes: 55 04 01 01
        isOpen=1
    === Wiegand transmit: port=2 bits=24 card=00aaaaaa x2 every 300ms ===
    [FRAME 2] 11 bytes: 55 0b 02 02 02 18 00 64 00 e8 03
    [FRAME 3] 10 bytes: 55 0a 02 01 02 18 00 aa aa aa
      card  1/2 rc=0
    [FRAME 4] 11 bytes: 55 0b 02 02 02 18 00 64 00 e8 03
    [FRAME 5] 10 bytes: 55 0a 02 01 02 18 00 aa aa aa
      card  2/2 rc=0
    === closing link (0 refusals) ===
    [FRAME 6] 4 bytes: 55 04 01 00
    done

Decode: SET_CONFIG `55 0b 02 02 <port=02> <bits=18 00> <f12=64 00> <f14=e8 03>`
→ halfwords are **little-endian** (24=0x0018 → `18 00`, 100 → `64 00`,
1000 → `e8 03`). WRITE_DATA `55 0a 02 01 <port=02> <token=18 00> <card aa aa aa>`
— token = bits value, card big-endian, n=3, len=n+7=10.

## Phase 2 — live runs (frames transmitted, STM8 echoes = ACK)

30-card run excerpt (identical pattern for 20-card / 1000ms runs):

    [TX] 11 bytes: 55 0b 02 02 02 18 00 64 00 e8 03
    [TX] 10 bytes: 55 0a 02 01 02 18 00 aa aa aa
      card  1/30 rc=0
    [RX] 11 bytes: 55 0b 02 02 02 18 00 64 00 e8 03   <- echo of SET_CONFIG
    [RX] 10 bytes: 55 0a 02 01 02 18 00 aa aa aa      <- echo of WRITE_DATA
    ... (30/30, occasional 11-byte echo ending `e8 00` = read-boundary artifact)
    === closing link (0 refusals) ===
    [TX] 4 bytes: 55 04 01 00
    [RX] 4 bytes: 55 04 01 00
    done

Flood runs: `./ema_wsend 2 24 AAAAAA 3000 5` (~3000 cards/15 s, port 2 then
port 1) — both completed, 0 refusals. Cumulative: ~9000 cards across all live
runs, zero validator refusals, every WRITE_DATA echoed by the STM8.

## Phase 3 — physical bench verification (user, LEDs)

- W-OUT2 block: DATA0, DATA1, GND. W-OUT1/W-OUT2 pins are **open-collector**.
- Wiring `pin → 1k → LED → GND`: **stays dark** (line idles released/high-Z —
  cannot source current).
- Wiring `+12 V → 1k → LED → pin`: **lights during flood** (line pulls low on
  each bit), fades, **off after close** (released). Verified on BOTH pins.
- Cold boot (no session yet): pins sit **LOW** → both LEDs steady-on until the
  first open/close cycle releases them.
- The ~100 µs/bit pulses are invisible at normal card rates (1 card/s) — the
  flood test (back-to-back cards) makes the average current visible as dimming.

## Phase 4 — user click-test via the desktop app (2026-10-14)

All combinations from the EMA_Controls SEND WIEGAND row: **port 1 × W-OUT1,
port 1 × W-OUT2, port 2 × W-OUT1, port 2 × W-OUT2 — all four pulse, all work.**

Closes the last open question of 2026-10-13 ("only port 2 exercised on pins").
Also confirms on hardware what the protocol implies: DATA0 and DATA1 are **one
Wiegand channel** — 0-bits pulse DATA0, 1-bits pulse DATA1 — so both pins pulse
on every card regardless of port. They cannot serve as two independent control
lines; OUT1/OUT2 are the outputs for that.


## Open observations
- The STM8 occasionally emitted a 4-byte `55 0a 01 00`-shaped fragment at the
  end of a flood (read-boundary artifact suspected, not confirmed).
- Reply of `55 04 06 01` (type 65, GPI12 read) was never observed.
