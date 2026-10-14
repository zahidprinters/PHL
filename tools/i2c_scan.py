#!/usr/bin/env python2
"""Enumerate every I2C device on every adapter, read-only.

Purpose: identify which IC could be driving the board's GPI/GPO connectors, so
the PCB can be traced to it. A GPIO expander (PCA953x, TCA9555, MAX7312 ...) would
show up here; so would the max77686 PMIC, whose own GPIOs are a likely home for a
couple of clean lines.

Addresses already owned by a kernel driver return EBUSY -- that is informative in
itself, since it names the driver holding the device. Read-only: every probe is a
zero-length write, which just checks for an ACK.

Run:  ./i2c_scan.py
"""

import fcntl
import os
import struct
import sys

I2C_SLAVE = 0x0703
I2C_RDWR = 0x0707

# struct i2c_rdwr_ioctl_data { __u32 nmsgs; struct i2c_msg msgs[1]; }
# 32-bit ARM layout: nmsgs(4), addr(2), flags(2), len(2), pad(2), buf ptr(4)
FMT = "=IHHHHI"
SIZE = struct.calcsize(FMT)


def scan(adapter):
    """Probe one adapter and return the list of responding addresses."""
    path = "/dev/i2c-%d" % adapter
    found = []
    try:
        fd = os.open(path, os.O_RDWR)
    except IOError as err:
        print("  %s: cannot open (%s)" % (path, err))
        return found
    try:
        for addr in range(0x03, 0x78):
            # Zero-length write == address-only probe.
            # nmsgs, addr, flags, len, pad, buf-pointer
            buf = struct.pack(FMT, 1, addr, 0, 0, 0, 0x1000)
            try:
                fcntl.ioctl(fd, I2C_RDWR, buf)
                found.append(addr)
            except IOError:
                # EBUSY means a driver owns it; EIO/ENXIO means nothing there.
                pass
    finally:
        os.close(fd)
    return found


def main():
    """Scan every i2c adapter present and list the results."""
    adapters = sorted(int(n.split("-")[1]) for n in os.listdir("/dev")
                      if n.startswith("i2c-") and n[4:].isdigit())
    for a in adapters:
        print("i2c-%d:" % a)
        addrs = scan(a)
        if not addrs:
            print("  (no responding addresses)")
        for addr in addrs:
            print("  0x%02X" % addr)
    return 0


if __name__ == "__main__":
    sys.exit(main())