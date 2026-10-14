#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""STM8 link health check - open/close handshake against /dev/ttySAC0.

Sends the vendor's own OPEN frame and waits for the STM8's ack, then CLOSEs.
This is the same handshake every other tool uses, so a pass here means the
link is usable; a fail means the digital I/O (IN1/IN2, OUT1/OUT2, relay) is
down until it is fixed.

Deliberately does NOT touch ttySAC1 (kernel console), ttySAC2 or ttySAC3.

Usage:  python link_health.py [port] [baud]
"""
import os
import re
import sys
import termios
import time

COUNTS = "/proc/tty/driver/s3c2410_serial"
PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttySAC0"
BAUD = int(sys.argv[2]) if len(sys.argv) > 2 else 115200
SOF = 0x55
OPEN = "\x55\x04\x01\x01"
CLOSE = "\x55\x04\x01\x00"


def counters():
    """tx/rx counts for `PORT` as (tx, rx), or None if unparseable.

    The counter lines are keyed by index and do NOT contain the device name:
        0: uart:S3C6400/10 mmio:0x13800000 irq:16 tx:2512 rx:0 RTS|...
    so the name has to be mapped to its index first.
    """
    name = PORT.rsplit("/", 1)[-1]
    m = re.match(r"ttySAC(\d+)$", name)
    if not m:
        return None
    idx = int(m.group(1))
    for line in open(COUNTS):
        g = re.match(r"(\d+):.*tx:(\d+) rx:(\d+)", line)
        if g and int(g.group(1)) == idx:
            return (int(g.group(2)), int(g.group(3)))
    return None


def main():
    before = counters()
    print("port   : %s @ %d 8N1" % (PORT, BAUD))
    print("before : tx=%s rx=%s" % (before[0], before[1]) if before else "?")

    try:
        fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    except OSError as e:
        print("RESULT : OPEN FAILED - %s" % e)
        return 1
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

        os.write(fd, OPEN)
        print("sent   : %s  (OPEN)" % " ".join("%02x" % ord(c) for c in OPEN))

        got = ""
        end = time.time() + 3.0
        while time.time() < end and len(got) < 4:
            try:
                got += os.read(fd, 64)
            except OSError:
                time.sleep(0.02)
        print("recv   : %s" % (" ".join("%02x" % ord(c) for c in got)
                               or "(nothing)"))

        os.write(fd, CLOSE)
        end = time.time() + 2.0
        while time.time() < end:
            try:
                extra = os.read(fd, 64)
            except OSError:
                break
            if extra:
                got += extra
            else:
                time.sleep(0.02)
    finally:
        os.close(fd)

    after = counters()
    print("after  : tx=%s rx=%s" % (after[0], after[1]) if after else "?")

    ok = got.startswith("\x55")
    print("")
    print("RESULT : %s" % ("LINK OK - STM8 answered" if ok else
                           "LINK DEAD - no response from the STM8"))
    if ok:
        print("frames : %s" % " | ".join(
            " ".join("%02x" % ord(c) for c in got[i:i + 4])
            for i in range(0, len(got), 4)))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
