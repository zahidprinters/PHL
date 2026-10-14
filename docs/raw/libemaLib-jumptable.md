# libemaLib — `checkWriteEvent` jump-table decode (raw evidence)

Source: `libemaLib_arm_1.0.1.so`, force-thumb disassembly in
`libemaLib-disasm.txt` (this file's line numbers refer to that copy). Function
at **0x54e0**, frame buffer at `this+24`. Decoded 2026-10-13.

## Prologue (disasm lines 1315–1325)

```asm
54e2: movs r3, #85          ; 0x55
54e4: strb r3, [r0, #24]    ; buf[0] = start byte
54e8: ldr  r3, [r1, #4]     ; r3 = event type (struct +4)
54ee: cmp  r3, #65          ; 0x41
54f0: bhi  5590             ; type > 65 -> no-op
54f2: tbh  [pc, r3, lsl #1] ; jump table, base 0x54f6
```

## Jump-table entries (halfwords at 0x54f6, disasm lines 1326–1390)

Target = `0x54f6 + entry*2`. Entry `0x004d` → `0x5590` = the no-op.

| Entry addr | Raw | Type | Target | Handler |
|---|---|---|---|---|
| 0x54f6 | 0x0050 | 0 | 0x5596 | CLOSE: len=4, class=1, op=0 → `55 04 01 00` |
| 0x54f8 | 0x0058 | 1 | 0x55a6 | OPEN: len=4, class=1, op=1 → `55 04 01 01` |
| 0x54fa | 0x005e | 2 | 0x55b2 | `mvn r0,#12` → return **-13** |
| 0x54fc | 0x0061 | 3 | 0x55b8 | **WIEGAND_WRITE_DATA** (session-gated) |
| 0x54fe | 0x0092 | 4 | 0x561a | **WIEGAND_SET_CONFIG** (validates + seeds session) |
| 0x5500 | 0x00e2 | 5 | 0x56ba | GET_CONFIG: len=5, class=2, op=3, payload=ev+8 |
| 0x5502 | 0x00ec | 6 | 0x56ce | AUTO_DETECT: len=5, class=2, op=4, payload=ev+8 |
| 0x5504–0x5514 | 0x004d ×9 | 7–15 | 0x5590 | **no-op** |
| 0x5516 | 0x005e | 16 | 0x55b2 | same as type 2 → return **-13** |
| 0x5518 | 0x00f1 | 17 | 0x56d8 | **OUT1 write** (uses ev+49) |
| 0x551a | 0x0105 | 18 | 0x5700 | **OUT2 write** (uses ev+50) |
| 0x551c | 0x0119 | 19 | 0x5728 | **BOTH write** (uses ev+49 and ev+50) |
| 0x551e–0x5534 | 0x004d ×12 | 20–31 | 0x5590 | **no-op** |
| 0x5536 | 0x0133 | 32 | 0x575c | **relay write** (uses ev+53, ev+54) |
| 0x5538–0x5574 | 0x004d ×32 | 33–64 | 0x5590 | **no-op** |
| 0x5576 | 0x013f | 65 | 0x5774 | **GPI12 read**: len=4, class=6, op=1 → `55 04 06 01` |

The no-op at 0x5590 (disasm lines 1403–1404):

```asm
5590: ldrb r3, [r0, #64]   ; re-read the (old) length
5594: b.n  5588            ; buf[25]=r3, return 0 — buffer untouched
```

## Handler blocks (disasm line refs)

**Type 0/1 — CLOSE/OPEN** (lines 1405–1418): write len/class/op, return 0.
**Type 2/16 — error** (lines 1419–1420): `mvn.w r0, #12` → -13, nothing built.

**Type 3 — WRITE_DATA** (lines 1421–1461):
```asm
55b8: ldrh r3, [r0, #490]     ; session token
55bc: mvn.w r0, #15           ; -16 if no session
55c4: ldrh r2, [r5, #10]      ; ev+10
55c6: cmp  r2, r3             ; must equal session
55ca: mvnne.w r0, #16         ; -17 on mismatch
55d0: ldrb r3, [r5, #8]       ; ev+8
55d2: subs r3, #1 / cmp #1    ; must be 1 or 2
55d6: bhi.w 5784              ; -> mvn r0,#23 = -24
55da: ... class=2, op=1, buf[28]=ev+8
55ec: ldrh r3, [r5, #10]      ; ev+10 appended as halfword (helper 0x4ee0)
55f6: ldrh r0, [r5, #10]; lsls #29 -> carry bits
5790: lsrs r0, #3; adds #1    ; n = bitlen/8 rounded UP if bitlen%8 != 0
5604: loop copies ev+16.. -> buf+31..
5612: len = n + 7
```

**Type 4 — SET_CONFIG** (lines 1462–1517):
```asm
561a: ldrh ip, [r5, #10]      ; ev+10
561e: add  r3, ip, #-1; cmp #264 ; (ev+10-1) <= 264 -> 1..265
5628: mvncs.w r0, #17         ; -18 out of range
562e: ldrh r3, [r5, #12]      ; ev+12: same check vs 49999 -> -19
5642: ldrh r1, [r5, #14]      ; ev+14: same check
564e: cmp  r3, r1; bcs 5796   ; ev+12 < ev+14 required -> else -20
5654: ldrb r2, [r5, #8]; subs #1; cmp #1 ; ev+8 in {1,2} -> else -24
5660: strb [r4, #488] = ev+8  ; seed session fields
5674: strh [r4, #490] = ev+10 ; token
5678: strh [r4, #492] = ev+12
5682: strh [r4, #494] = ev+14
5664: class=2, op=2; buf[28]=ev+8; then ev+10/12/14 appended as halfwords
56b4: len = 11 -> `55 0b 02 02 <b8> <f10 2B> <f12 2B> <f14 2B>`
```

**Types 17/18/19 — GPO** (lines 1533–1584): each checks its state byte(s)
`<= 1` else `mvn r0, #22` = **-23** (0x578a). Frames (buf offset → byte):

| Type | buf[26] | buf[27] | buf[28] | buf[29] | buf[32] | buf[33] | len |
|---|---|---|---|---|---|---|---|
| 17 | 3 | 1 | ev+49 | — | 1 | 0 | 10 |
| 18 | 3 | 1 | — | ev+50 | 0 | 1 | 10 |
| 19 | 3 | 1 | ev+49 | ev+50 | 1 | 1 | 10 |

buf[30]/buf[31] never written (stale).

**Type 32 — relay** (lines 1585–1594): `buf[26]=4, buf[27]=ev+53, buf[28]=ev+54, len=5` → `55 05 04 <sel> <state>`. No validation.

**Type 65 — GPI12 read** (lines 1595–1602): `len=4, buf[26]=6, buf[27]=1` → `55 04 06 01`. Fixed, no payload.

**Error tails** (lines 1603–1611):
```asm
5784: mvn.w r0, #23   ; -24  ev+8 not in {1,2}
578a: mvn.w r0, #22   ; -23  GPO/relay state byte > 1
5796: mvn.w r0, #19   ; -20  ev+14 out of range or ev+12 >= ev+14
```

## `writeEvent` wrapper (0x579c, disasm lines 1613–1633)

`mvn r4, #11` (-12) on null event; calls `checkWriteEvent` (0x5070); if it
returns non-zero, that error passes through; else writes `buf[24..]`, length
`buf[64]`, to the serial device; write failure → `mvn r4, #7` (-8).

## Related

- `EMAMain::close` (0x57d4, lines 1685–1688) resets the session:
  `strh 0 → this+490`, `strh 0 → this+492`, `strh 0 → this+494`, `strb 1 → this+488`.
  **So every new open needs a fresh SET_CONFIG before WRITE_DATA works.**
- Helper at **0x4ee0** appends a 2-byte field (used for ev+10/12/14); assumed
  big-endian, verify against a live capture.
