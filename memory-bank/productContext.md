# Product Context

Why this project exists, in terms a new person would understand.

## The problem
A Daikin CMIMIR / Intelligent Manager HVAC controller board runs Ubuntu on an
Exynos 4412, but a second chip — an **STM8S207** — sits between it and most of
the physical I/O. The board looks like a Linux computer with two Ethernet ports,
serial ports and GPIO headers. In Linux it has **one** Ethernet port, **no** GPIO,
and **no** usable serial ports. Daikin's own software can drive everything, but
it needs an iris-imager device that is not attached, and its protocol is in
stripped binaries.

So the board is far more capable than its operating system admits, and the
hardware is undocumented. Every attempt so far has been blocked by the same
unknown: how the SoC and the STM8 talk to each other.

## Who it is for
One engineer who has the board physically in hand, can read the silkscreen and
probe with a meter, and drives it over SSH and VNC.

## What it does
- Documents every peripheral with a measured WORKS/BLOCKED verdict.
- Explains the two-processor architecture so the dead ends stop repeating.
- Provides read-only probes that re-measure the board at any time.

## User experience goals
- Every claim traceable to saved command output, never to memory.
- No risk to the board: read-only until the link is understood.
- The next person picks up from `docs/BOARD.md` and knows exactly what is left.

## What we are deliberately not doing
- Writing to the board until the SoC<->STM8 link is identified.
- Installing userspace tools to paper over a missing kernel (the `libgpiod` trap).
- Replacing the 2014 kernel or the vendor Daikin stack.
- Repeating the Linux-side GPIO / Wiegand / `/dev/ttyS*` search. Those devices
  belong to the STM8 and will never appear in Linux.
