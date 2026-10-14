#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Drive each candidate UART so a meter across D+/D- can identify the RS485 port.

Why this instead of a loopback: the port is 2-wire half-duplex, so TX and RX
share the same pair and there is no separate line to jumper. The four-phase
A/B jumper test recorded in docs/BOARD.md therefore showed 0/40 echoes on both
ttySAC2 and ttySAC3 - expected, not a failure. What does show up on a meter is
the DRIVER: when a port's transceiver is enabled it puts a differential of
roughly 1.5..5 V across D+/D-, and that only happens on the port actually
wired to the connector.

Readout: DC volts ACROSS the pair (probe D+ with one lead and D- with the
other). Not to GND - a differential measurement has no meaningful ground
reference.

Each window transmits continuously for WINDOW seconds so a slow meter has time
to settle. RTS and DTR are both asserted because on most boards the transceiver
driver-enable (DE) hangs off one of them; if nothing moves, try the opposite
polarity (see --no-rts) before concluding the port is absent.

Only ttySAC2 and ttySAC3 are opened. ttySAC0 is the STM8 link and ttySAC1 is
the kernel console; opening either can desync the digital I/O or hang the board.
"""
import fcntl
import os
import re
import struct
import sys
import termios
import time

COUNTS = "/proc/tty/driver/s3c2410_serial"
PORTS = (("/dev/ttySAC2", 2), ("/dev/ttySAC3", 3))
BAUD = 115200
WINDOW = 15          # seconds of continuous TX per port
GAP = 5              # silence between windows so the meter can return to rest
PASSES = 2           # A/B repeated -> A/B/A/B

TIOCMGET = 0x5415
TIOCMSET = 0x5418
TIOCM_DTR = 0x002
TIOCM_RTS = 0x004


def counters():
    """Per-UART tx/rx counts as {index: (tx, rx)} - hardware ground truth."""
    out = {}
    for line in open(COUNTS):
        m = re.match(r"(\d+):.*tx:(\d+) rx:(\d+)", line)
        if m:
            out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return out


def drive(dev, seconds, assert_rts):
    """Hold the port open, assert control lines, and transmit for `seconds`.

    Returns (bytes_written, error_or_None). The pattern is a 0x55/0xAA stream:
    alternating bits, so the differential pair toggles rather than sitting at
    one level - easier to see on a scope and still reads on a DC meter.
    """
    try:
        fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError as e:
        return 0, str(e)
    try:
        attrs = termios.tcgetattr(fd)
        spd = getattr(termios, "B%d" % BAUD)
        attrs[4] = spd
        attrs[5] = spd
        attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
        attrs[3] = 0
        attrs[1] = 0
        attrs[0] = 0
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        termios.tcflush(fd, termios.TCIOFLUSH)

        # Assert DTR/RTS so a transceiver whose DE is wired to either one
        # starts driving the pair. Best effort - some kernels reject it.
        try:
            flags = struct.pack("I", 0)
            flags = fcntl.ioctl(fd, TIOCMGET, flags)
            val = struct.unpack("I", flags)[0]
            val |= TIOCM_DTR
            if assert_rts:
                val |= TIOCM_RTS
            else:
                val &= ~TIOCM_RTS
            fcntl.ioctl(fd, TIOCMSET, struct.pack("I", val))
        except (OSError, IOError):
            pass

        chunk = b"\x55\xaa" * 64
        written = 0
        deadline = time.time() + seconds
        while time.time() < deadline:
            try:
                written += os.write(fd, chunk)
            except OSError:
                time.sleep(0.02)
            else:
                time.sleep(0.02)
        return written, None
    finally:
        os.close(fd)


def main():
    assert_rts = "--no-rts" not in sys.argv
    # Optional single-window mode so the caller can separate the two ports in
    # time (much easier to read off a meter than alternating 15 s blocks):
    #     python rs485_probe.py /dev/ttySAC2 30
    single = None
    for a in sys.argv[1:]:
        if a.startswith("/dev/ttySAC"):
            single = a
    if single:
        secs = 30
        for a in sys.argv[1:]:
            if a.isdigit():
                secs = int(a)
        # counters() is keyed by UART index, so map the device name first -
        # indexing it positionally would read ttySAC0/ttySAC1 instead.
        idx = int(single.rsplit("SAC", 1)[-1])
        print("SINGLE WINDOW: %s  transmitting for %d s - WATCH THE METER NOW"
              % (single, secs))
        print("(probes across D+/D-, jumper OFF, DC volts)")
        sys.stdout.flush()
        before = counters()[idx]
        n, err = drive(single, secs, assert_rts)
        after = counters()[idx]
        if err:
            print("  OPEN/DRIVE FAILED: %s" % err)
        print("  wrote %d bytes   tx %d -> %d   rx %d -> %d"
              % (n, before[0], after[0], before[1], after[1]))
        print("  window complete.")
        return

    print("RS485 PORT PROBE  -  watch the meter across D+/D-")
    print("baud %d, window %ds, gap %ds, %d passes, RTS=%s"
          % (BAUD, WINDOW, GAP, PASSES, "asserted" if assert_rts else "held low"))
    print("Measure DC volts BETWEEN D+ and D-, not to GND.")
    print("")

    for p in range(1, PASSES + 1):
        for dev, idx in PORTS:
            before = counters()[idx]
            print(">>> PASS %d  PORT %-13s  TRANSMITTING FOR %d s  - WATCH NOW"
                  % (p, dev, WINDOW))
            sys.stdout.flush()
            n, err = drive(dev, WINDOW, assert_rts)
            after = counters()[idx]
            if err:
                print("    OPEN/DRIVE FAILED: %s" % err)
            print("    wrote %d bytes   tx %d -> %d   rx %d -> %d"
                  % (n, before[0], after[0], before[1], after[1]))
            print("<<< window %d.%d done" % (p, 1 if dev.endswith("2") else 2))
            sys.stdout.flush()
            time.sleep(GAP)
        print("--- pass %d complete, both ports idle for %ds ---" % (p, GAP))
        sys.stdout.flush()

    print("")
    print("RESULT READING:")
    print("  meter moved ONLY during ttySAC2 -> RS485 is ttySAC2")
    print("  meter moved ONLY during ttySAC3 -> RS485 is ttySAC3")
    print("  meter moved during both        -> they are the same pair / bridged")
    print("  meter never moved              -> not on a Linux UART (STM8-side),")
    print("     or the driver-enable line is not DTR/RTS - try --no-rts.")


if __name__ == "__main__":
    main()
