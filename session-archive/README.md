# Session archive — 2026-10-10

Everything captured while reverse-engineering the Daikin CMIMIR board's
STM8S207 link. Pulled off the board before a power cycle.

## How to talk to the STM8

| | |
|---|---|
| Port | `/dev/ttySAC0` |
| Line | **115200 baud, 8N1, raw** |
| Frame | `0x55` │ LEN (total) │ payload… │ `00 00` |

Found by compiling a stub against `libemaLib_arm_1.0.1.so` and watching which fd
it opened — not by guessing.

## What works

### Digital inputs — PROVEN by physical test
Status frame `55 0a 03 00 01 01 BB RR 00 00`:

| Bit | Byte | Idle | Bridged to GND | Window |
|---|---|---|---|---|
| **IN1** | 6 | `01` | `00` | 00:51:43 → 00:52:10 |
| **IN2** | 7 | `01` | `00` | 00:53:47 → 00:54:04 |

Active-low. Logs: `ema_cap_in1.log`, `ema_cap_in2.log`.

### Relay — PROVEN
```
55 05 04 01 01   ON
55 05 04 01 00   OFF
```
Class 04 = selector + state. Selector `01` = relay. Byte 4 is a **state**, not a
pulse. The STM8 echoes class-04 frames back, so the echo is authoritative.
Only selector `01` (of `01`–`12`) has any physical effect.

## What does not work — and why

### Digital outputs OUT1 / OUT2 — NOT SOLVED

**Electrical model (established, solid):** both are **dry relay contacts with no
internal voltage source**. On power-up OUT1 reads ~8 V decaying to ~3 V then
floats — textbook phantom voltage on an open contact. With
`12V+ → LED → 1 kΩ → OUT` the LED lights when the contact is closed. The LED
never worked in early tests because it was reversed, which made a *working*
output look dead.

**State persists across a Linux reboot** — the STM8 is a separate MCU with its
own reset domain, and there is no way to reset it from Linux (no sysfs node, no
driver). Only removing board power clears it.

**Commands found:**

| Type | Frame | Observed |
|---|---|---|
| 17 | `55 0a 03 01 00 00 00 00 01 00` | closes OUT1 ✅ (user: "shorted to gnd") |
| 18 | `55 0a 03 01 00 00 00 00 00 01` | **turns OUT2 ON** ✅ (post-power-cycle, LED lit, acked 40/40) |
| 19–31 | `55 0a 03 01 00 00 00 00 01 01` | released OUT1 — **sent 80×, acked 79×, contact stayed closed** |

**The blocker:** in every class-`03` frame, **payload bytes 4–7 are `00 00 00 00`**
— the only fields no event type ever fills. Those must be where the output and
state parameters live. **There is no `...00 00` frame** (OUT2 closed) anywhere in
types 1–40, which disproves the earlier "byte 8 = output, byte 9 = state" idea.

**Next step (zero risk):** replay type 17 under `nullwrite.so`, vary one struct
offset at a time, and watch for payload bytes 4–7 to change. Same technique that
found offsets 53/54 for the relay.

## Complete command vocabulary — types 1–40

From `tscan.log`, captured with writes **swallowed** (nothing transmitted):

| Types | Frame |
|---|---|
| 1 | `55 04 01 01` |
| 5 | `55 05 02 03 00` |
| 6–15 | `55 05 02 04 00` (STM8 ignores these) |
| 17 | `55 0a 03 01 00 00 00 00 01 00` |
| 18 | `55 0a 03 01 00 00 00 00 00 01` |
| 19–31 | `55 0a 03 01 00 00 00 00 01 01` |
| 32–39 | `55 05 04 00 00` |
| 40 | `55 04 01 00` |

## Errors made in this session — do not repeat

1. **Class-`03` ignores struct offsets 53/54.** They only work for class `04`. A
   tool printed its *intended* frame instead of the transmitted one, so 80
   "release" attempts were really re-closing OUT1.
2. **The class-`02` value byte never reached the frame** for types 17–20 — value
   0 and value 1 produced identical bytes, so that test could show nothing.
3. **The echo proves receipt, not validity.** Every class-`04` selector was
   echoed, including ones with no effect.
4. **A status byte change `00`→`4c` was a tracer artefact**, not real state.
5. **Probing with the value byte at offset 8 only ever found class `02`.** The
   `02`/`03`/`04` class byte comes from the event type itself.

## Files here

| File | What |
|---|---|
| `ema_cap_in1/in2.log` | input capture during physical shorting |
| `wsweep.log`, `wsweep5.log` | struct-offset sweeps under the shim |
| `tscan.log` | full type 1–40 vocabulary, nothing transmitted |
| `val.log`, `sel02–04.log`, `parade*.log` | value and selector sweeps |
| `c03.log`, `c04.log`, `t17/t19.log`, `out1rel2.log` | GPO command attempts |
| `blink.log`, `relay_out.log` | relay confirmation |
| `onboard_*.cpp/.py/.c` | the tools exactly as they sit on the board |

## Untouched

Wiegand (no event ever sent) and analog I/O (not started). A hint for analog:
the vendor's single `writeEvent` call sits in a float-heavy loop and wrote **30**
(`0x1e`) into the state field — that reads like a 0–100 percentage scale.
