# Vendor protocol framework — decoded from libemaLib disassembly

Recovered by disassembling `libemaLib_arm_1.0.1.so` (the STM8 serialiser) on
2026-10-12, **fully re-decoded 2026-10-13 from the jump table**. Raw:
`docs/raw/libemaLib-disasm.txt`, `libemaLib-dynsym.txt`,
`cmimir-writeevent-callsite.txt`, `libemaLib-jumptable.md`. This is the
authoritative "framework" — how a high-level `EMA_EVENT` becomes bytes on
`/dev/ttySAC0`.

## The two vendor software layers

- **CMITECH biometric** (`CMIMIRDemo` + `libcmirisLib2` + `libcmicolorLib` +
  `share/CMITECH/`): face (Haar cascade) + iris recognition, voice prompts, an
  `Enroll.db` template store. The `libcmirisLib2` EEPROM/I²C classes
  (`EEPROM::setBoardNumber/setSerialNumber/...`, `Command::setI2CCmd`,
  `setEEPROMLockEnableCmd`) belong to the **iris camera over USB**, not this
  board.
- **EMA industrial I/O** (`libemaLib`): the STM8 protocol. Opens **`/dev/ttySAC0`**
  via `QextSerialPort` (hardcoded; also probes `/dev/ttyS0`, `ttyUSB*`).
  Exports the C API `ema_createEMA/open/readEvent/writeEvent/close/...` and
  `ema_getEMAVersion`; the C++ class `EMAMain` has `writeEvent/setReadEvent/
  checkWriteEvent/readEvent`. **`checkWriteEvent` is the frame serialiser.**

## The serialiser itself (`EMAMain::checkWriteEvent`, 0x54e0–0x579b)

```asm
54e2:  movs r3, #85        ; 0x55
54e4:  strb r3, [r0, #24]  ; frame[0] = start byte, buffer at this+24
54e8:  ldr  r3, [r1, #4]   ; event TYPE from EMA_EVENT+4
54ee:  cmp  r3, #65        ; 0x41
54f0:  bhi  5590           ; type > 65 -> no-op (see below)
54f2:  tbh  [pc, r3, lsl#1]; jump table at 0x54f6
```

- Frame buffer: `this+24` = `0x55`, `+25` = length, `+26` = class, `+27` = op,
  `+28…` = payload; `this+64` = total length.
- Jump table: entry `i` at `0x54f6 + 2i`, target `= 0x54f6 + entry*2`.
- **Types 7–15 and 20–65 are no-ops** (entry `0x004d` → `0x5590`: just re-reads
  the length and returns 0). Nothing is built — and any previous frame stays in
  the buffer (see "the stale-buffer trap").

## The `EMA_EVENT` struct (offsets the serialiser reads)

| Offset | Field | Used by |
|---|---|---|
| `+4` | **event type** (uint32) — the serialiser's jump-table index | all |
| `+8` | byte — Wiegand value / channel | WIEGAND_*, GET/AUTO, SET/WRITE |
| `+10` | 16-bit — Wiegand token / bit length | SET_CONFIG (seeds session), WRITE |
| `+12` `+14` | 16-bit — Wiegand config params (1..50000) | SET_CONFIG only |
| `+16…` | card data bytes (n = ceil(bitlen/8)) | WIEGAND WRITE only |
| `+49` (0x31) | **OUT1 / GPO1 state** (0 or 1) | types 17, 19 |
| `+50` (0x32) | **OUT2 / GPO2 state** (0 or 1) | types 18, 19 |
| `+53` (0x35) | **relay selector** | type 32 |
| `+54` (0x36) | **relay state** | type 32 |

Internal session fields (libemaLib, not the struct): `this+490` = Wiegand token
(seeded by SET_CONFIG's `ev+10`), `this+492`/`this+494` = config params,
`this+488` = Wiegand value.

## Complete event-type → frame map (definitive)

`checkWriteEvent` reads the type at `+4` and jumps through the table at
`0x54f6`. Every row below was read from the disassembly and cross-checked
against frames we captured live (✅).

| Type | Enum name | Frame on the wire | Payload from | Verified |
|---|---|---|---|---|
| 0 | CLOSE | `55 04 01 00` | fixed | ✅ live |
| 1 | OPEN | `55 04 01 01` | fixed | ✅ live |
| 2 | WIEGAND_READ_DATA | **none** — return `-13` | — | ✅ swallowed |
| **3** | **WIEGAND_WRITE_DATA** | `55 (n+7) 02 01 <b8> <b10 2B> <card nB>` — **needs session** | `+8`∈{1,2}, `+10`, `+16…` | ✅ frame decoded |
| **4** | **WIEGAND_SET_CONFIG** | `55 0b 02 02 <b8> <f10> <f12> <f14>` — **seeds session** | `+8,+10,+12,+14` | ✅ frame decoded |
| 5 | WIEGAND_GET_CONFIG | `55 05 02 03 <b8>` | `+8` | ✅ swallowed + live |
| 6 | WIEGAND_AUTO_DETECT | `55 05 02 04 <b8>` | `+8` | ✅ swallowed |
| 7 | GPI12_READ | **no-op in checkWriteEvent** | — | ✅ swallowed |
| 8 | GPO1_WRITE | **no-op** (dead enum name) | — | ✅ swallowed |
| 9 | GPO2_WRITE | **no-op** (dead enum name) | — | ✅ swallowed |
| 10 | GPO12_WRITE | **no-op** (dead enum name) | — | ✅ swallowed |
| 11 | RELAY_WRITE | **no-op** (dead enum name) | — | ✅ swallowed |
| 16 | — | **none** — return `-13` | — | ✅ swallowed |
| **17** | *(internal — OUT1)* | `55 0a 03 01 <b49> · · · 01 00` | `+49` | ✅ live |
| **18** | *(internal — OUT2)* | `55 0a 03 01 · <b50> · · 00 01` | `+50` | ✅ live |
| **19** | *(internal — BOTH)* | `55 0a 03 01 <b49> <b50> · · 01 01` | `+49`, `+50` | ✅ live |
| **32** | *(internal — relay)* | `55 05 04 <b53> <b54>` | `+53`, `+54` | ✅ live |
| **65** (0x41) | *(internal — GPI12 read)* | `55 04 06 01` | fixed | not yet sent |

**Two big corrections to earlier notes:**
1. `GPO1/2/12_WRITE` and `RELAY_WRITE` (enum types 8–11) are **no-ops in this
   library version** — the enum names ship in CMIMIRDemo but the serialiser
   does nothing with them. The real GPO frames come from **types 17/18/19** and
   the relay from **type 32** (internal types set by `setReadEvent` or direct
   API use).
2. `GPI12_READ` is **not** type 7 — type 7 is a no-op. `55 04 06 01` is built by
   **type 65**, which `setReadEvent` selects for status reads.

## GPO byte semantics (cross-checked against live captures)

Frame `55 0a 03 01 | b4 b5 | · · | b8 b9`:
- **b4** = OUT1 new state, **b5** = OUT2 new state (`00` = close/ON, `01` = released/OFF)
- **b8** = OUT1 channel-active flag, **b9** = OUT2 channel-active flag
- Type 17: OUT1 only (`b8=01, b9=00`) · Type 18: OUT2 only (`b8=00, b9=01`)
- **Type 19: both channels, independent** (`b8=b9=01`) — the clean way to drive both
- Bytes 6/7 are never written by any builder (stale from the previous frame)

Status frame readback `55 0a 03 00 | b4 b5 | b6 b7 | …`: b4/b5 = OUT1/OUT2
contact state, b6/b7 = IN1/IN2 — **no meter needed to verify a GPO write**.

## Serialiser internals — why frames get "silently refused"

`checkWriteEvent` returns **0** on success (frame built) or a **negative error**
(no frame built, nothing sent) — these negatives are the silent refusals we kept
hitting. Decoded from the disassembly:

| Code | Condition (struct field) |
|---|---|
| `-13` | type unhandled (2, 16) |
| `-16` | Wiegand write: no session (`this+490 == 0`) |
| `-17` | Wiegand write: token mismatch (`ev+10 != this+490`) |
| `-18` | SET_CONFIG: `ev+10` out of [1, 265] |
| `-19` | SET_CONFIG: `ev+12`/`ev+14` out of [1, 50000] |
| `-20` | SET_CONFIG: `ev+12 >= ev+14` |
| `-23` | GPO/relay: a state byte (`+49`/`+50`/`+53`/`+54`) > 1 |
| `-24` | Wiegand: `ev+8` not in {1, 2} |

**So a "valid-looking" frame is dropped unless every precondition holds.** The
STM8 then never sees it — which is why our earlier WIEGAND_WRITE attempts
produced nothing: no SET_CONFIG had been sent, so `this+490` was 0 and the
serialiser returned `-16` before building anything.

## The stale-buffer trap (explains a past mystery)

A no-op type (7–15, 20–65) returns 0 **without touching the frame buffer** —
so a write of a no-op type can **re-transmit the previous frame**. That is
almost certainly what "type 8 produces `55 04 01 01`" was: a stale OPEN frame
left in the buffer from the previous write. **Always verify what the trace
shows, never what the type number "should" do.**

## The Wiegand WRITE handshake (this is how W-OUT works)

`WIEGAND_SET_CONFIG` (type 4) **seeds libemaLib's internal session**:
`this+490 = ev+10` (token), `this+492 = ev+12`, `this+494 = ev+14`,
`this+488 = ev+8`. Validated: `ev+10` ∈ [1, 265], `ev+12`/`ev+14` ∈ [1, 50000],
`ev+12 < ev+14`, `ev+8` ∈ {1, 2}.

`WIEGAND_WRITE_DATA` (type 3) then requires:
1. `this+490 != 0` (session exists) — else return `-16`
2. `ev+10 == this+490` (token match) — else return `-17`
3. `ev+8` ∈ {1, 2} — else return `-24`
4. Card data at `ev+16…`, count `n = (ev+10 >> 3)` (+1 if `ev+10 << 29 != 0`,
   i.e. round up to whole bytes)

Frame: `55 (n+7) 02 01 <b8> <ev10 2B> <card nB>`. The STM8 then pulses
**W-OUT1 (DATA0)** for 0-bits and **W-OUT2 (DATA1)** for 1-bits — it transmits
a Wiegand card.

## W-OUT vs GPO — the answer to "are there 4 more GPOs?"

**No.** The vendor code exposes exactly **two** GPOs (OUT1/OUT2, struct `+49`/
`+50`, class-03 frames via types 17/18/19). There is no GPO3/GPO4 and W-OUT is
**not** a static output:

- **W-OUT1/W-OUT2 = Wiegand DATA0/DATA1**, driven only by `WIEGAND_WRITE_DATA`
  (type 3) after a SET_CONFIG handshake — as a **pulse-encoded card
  transmission**, not a static level.
- You *can* put arbitrary bit patterns on them (any card number), but each
  write is a ~20 ms burst of ~100 µs pulses, then the lines return to idle
  HIGH. That is a different animal from a relay contact you can latch.
- **"Total 6 GPO" is not supported by the vendor code.** If you want the W-OUT
  pins as static outputs you would need the STM8 firmware changed (ST-Link/SWIM
  route) — Linux cannot re-purpose them.

## What this gives us

- The **struct offsets are now known**: OUT1=`+49`, OUT2=`+50`, relay sel=`+53`,
  relay state=`+54`, Wiegand value=`+8`, token/bitlen=`+10`, config
  params=`+12/+14`, card data=`+16…`. Python/UI code can set these directly.
- We can call the **C API via ctypes** (`ema_createEMA/ema_open/ema_writeEvent/
  ema_readEvent/ema_close`) and pass a filled `EMA_EVENT` — the library does the
  framing, gating and the Wiegand handshake for us.
- **`ema_getEMAVersion`** (0x51e4) returns a hardcoded `1, 0, 1` — not a query.
- `55 04 06 01` (type 65) is the status-read request — a cleaner alternative to
  the open→read-one-frame→close dance.

## Not yet done / honest limits
- **SET_CONFIG→WRITE_DATA is LIVE-VERIFIED** (2026-10-13): `tools/ema_wsend.cpp`
  drove W-OUT on the bench, ~9000 cards, 0 refusals, STM8 echoed every frame;
  both DATA0/DATA1 physically verified with LEDs. **Both ports (1, 2) × both
  pins click-tested 2026-10-14 — all work; DATA0/DATA1 are one channel (0-bits
  and 1-bits), not independent outputs.** Evidence:
  `docs/raw/wiegand-send-raw.md`, CHANGELOG 2026-10-13/10-14.
- **The 2-byte field endianness (helper 0x4ee0) is LITTLE-endian on the wire**
  (`bits=24 → 18 00`, `f12=100 → 64 00`, `f14=1000 → e8 03`) — the old
  "assumed big-endian" note was wrong; resolved from live captures.
- **W-OUT electrical behaviour (measured):** open-collector — LED must be wired
  `+12V → 1k → LED → pin`. Idle **LOW after boot**, **released (high-Z) after
  session close**. Both lines pulse per card; ~100 µs pulses are invisible to
  the eye — flood the port to see LED dimming, or use a scope.
- The **read side** (`setReadEvent` 0x5a68 dispatch → `readEvent` parser) is
  still not fully decoded, and `55 04 06 01` (type 65) has still never been
  answered by the STM8 in our tests (no reply observed).
- 26-bit cards, STM8 parity computation, and the semantics/units of the
  SET_CONFIG f12/f14 fields remain unverified.


## Can we read the STM8's own firmware from the OS? — No (needs hardware)

Checked 2026-10-12: there is **no software path** to dump the STM8S207 flash.
- The EMA protocol has no read-flash/memory command (only the 12 event types
  above); `GPI12_READ` reads GPIO states, not program. `ema_getEMAVersion`
  returns a hardcoded constant, not a query.
- The STM8 cannot be reset into its UART bootloader from Linux (no reset/SWIM
  line exposed; the EMA UART is the only link; a power-cycle can't hold the
  boot-mode pin condition). SWIM is a physical pin.

**The clean path is hardware:** an **ST-Link/V2 clone + SWIM** with `stm8flash`
(`stm8flash -c stlinkv2 -p stm8s207?rb -r fw.hex`) reads the *entire* 128 KB
flash → the whole firmware → every open protocol question (Wiegand WRITE, class
`02`, analog, `GPI12_READ` semantics) answered at once. To wire it: identify the
STM8S207 chip, find its SWIM pin (pin 1 = SWIM/NRST), trace it (multimeter
continuity) to a via/test pad, connect SWIM + NRST + GND. A UART-bootloader path
exists (Boot ROM, sync `0x7F`→`0x79`) but needs SWIM held low during a reset and
is void if the vendor disabled it via option bytes.
