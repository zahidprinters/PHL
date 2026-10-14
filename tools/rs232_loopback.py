#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RS232 loopback test - identifies which Linux UART reaches the connector.

Put a wire (or tweezers) across TX and RX on the board's RS232 connector, run
this, and read the result. Remove the wire and run again as a control: rx must
freeze. Ground truth is /proc/tty/driver/s3c2410_serial counters, because the
driver increments tx for every byte handed to the UART whether or not a pin is
wired - so tx alone proves nothing, while a matching rx increment does.

Only ttySAC2 and ttySAC3 are ever opened. ttySAC0 is the STM8 link and ttySAC1
is the kernel console; touching either can hang the board or desync the digital
I/O. Nothing is written to the STM8.

Known result on this board: **ttySAC3 is the RS232 port.** ttySAC2 transmits
but never receives.

Not established by loopback: the real baud rate for a device on the far end
(loopback echoes at any speed, since TX and RX share one setting) and the line
voltage (true RS232 vs bare TTL) - check that with a meter on TX to GND:
negative ~= -5..-10 V means a real line driver.
"""
import fcntl
import os
import re
import termios
import time

COUNTS = "/proc/tty/driver/s3c2410_serial"
# 0 = STM8 link, 1 = kernel console - never touched
PORTS = (("/dev/ttySAC2", 2), ("/dev/ttySAC3", 3))
BAUDS = (115200, 9600, 19200, 38400, 57600)
PAYLOAD = b"RS232LB"


def counters():
    """Read per-UART tx/rx byte counts. Returns {index: (tx, rx)}."""
    out = {}
    for line in open(COUNTS):
        m = re.match(r"(\d+):.*tx:(\d+) rx:(\d+)", line)
        if m:
            out[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return out


def trial(fd, baud):
    """Configure raw 8N1 at baud, transmit PAYLOAD, collect echoes for 0.8 s.

    Returns the bytes read back. Does not interpret them - the caller compares
    against PAYLOAD. Baud failures are returned as empty, not raised.
    """
    spd = getattr(termios, "B%d" % baud, None)
    if spd is None:
        return b""
    attrs = termios.tcgetattr(fd)
    attrs[4] = spd              # ispeed
    attrs[5] = spd              # ospeed
    attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL   # 8 bits, no parity
    attrs[3] = 0                # raw: no echo, no flow control
    attrs[1] = 0
    attrs[0] = 0
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    termios.tcflush(fd, termios.TCIOFLUSH)

    os.write(fd, PAYLOAD)
    got = b""
    deadline = time.time() + 0.8
    while time.time() < deadline and len(got) < len(PAYLOAD):
        try:
            chunk = os.read(fd, 64)
        except OSError:
            chunk = b""
        if chunk:
            got += chunk
        else:
            time.sleep(0.02)
    return got


def main():
    before = counters()
    print("=== BEFORE ===")
    for i, (tx, rx) in sorted(before.items()):
        print("  ttySAC%d tx:%-8d rx:%-8d" % (i, tx, rx))

    hits = []
    for dev, idx in PORTS:
        for baud in BAUDS:
            b4 = counters()[idx]
            try:
                fd = os.open(dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            except OSError as e:
                print("   %-12s OPEN-FAIL %s" % (dev, e))
                break
            try:
                got = trial(fd, baud)
            finally:
                os.close(fd)
            af = counters()[idx]
            if got == PAYLOAD:
                print("** %-12s ECHO-OK   baud %-6d %r  counters %s -> %s"
                      % (dev, baud, got, b4, af))
                hits.append((dev, baud))
            else:
                print("   %-12s no echo   baud %-6d got %r  counters %s -> %s"
                      % (dev, baud, got, b4, af))

    print("\n=== AFTER ===")
    for i, (tx, rx) in sorted(counters().items()):
        print("  ttySAC%d tx:%-8d rx:%-8d" % (i, tx, rx))

    if hits:
        print("\nRESULT: looped port(s): %s"
              % ", ".join("%s @ %d" % h for h in hits))
        print("note: the echoed baud is not necessarily the device's real baud.")
    else:
        print("\nRESULT: no echo. Is the TX-RX jumper in place?")
        print("Re-run with the wire fitted, then again without it as a control.")


if __name__ == "__main__":
    main()
