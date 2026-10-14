# Project Brief

The foundation document. Everything else in the memory bank builds on this.
Keep it stable — if the scope changes, rewrite this first, then the rest.

## What this is
Understand and drive every peripheral on a **Daikin CMIMIR / Intelligent Manager**
HVAC controller board: an Exynos 4412 running Ubuntu Linaro, plus an **STM8S207**
MCU that owns the industrial I/O.

## Hard requirements
- Produce a **peripheral checklist** of everything on the board, each marked
  WORKS or BLOCKED with evidence. → `docs/BOARD.md`
- Reach the GPI/GPO headers (**IN1/IN2, OUT1/OUT2**) the user can physically see.
- Use the second RJ45, RS232, RS485, Wiegand and the 93LC66A EEPROMs.
- Never lose SSH/VNC access — the board has no display to recover through.

## Explicitly out of scope
- Writing to the board in any way until the link is understood. Every tool is
  read-only by decision, not by accident.
- Replacing the 2014 kernel or the vendor Daikin stack.
- The Philips Dynalite lighting work and the ECU-30 Windows/Android-USB driver
  hunt. Both were dead ends; they live in `archive/`.

## Success criteria
- Every peripheral on the board is listed with a WORKS/BLOCKED verdict and the
  evidence behind it.
- The **SoC↔STM8 serial link is identified** — this unblocks 6 of 8 BLOCKED items.
- A GPO on the board's OUT1/OUT2 header is driven and observed to change.
