#!/usr/bin/env python2
"""Passively listen on the free Exynos UARTs to find the STM8S207 link.

READ-ONLY: this opens each candidate port and reads. It never writes, so it cannot
actuate anything on a live HVAC controller. The goal is to find which UART carries
the SoC<->STM8 traffic and at what baud rate, which is step one of using the I/O
without Daikin's framework.

The board has pyserial 2.5 installed, so no compiler work is needed.

ttySAC1 is the kernel console and is deliberately NOT touched.

Run:  ./uart_sniff.py [seconds-per-baud]
"""

import sys
import time

import serial

# Console is excluded on purpose: writing/reading it can disturb the login.
PORTS = ["/dev/ttySAC0", "/dev/ttySAC2", "/dev/ttySAC3"]
BAUDS = [115200, 9600, 38400, 57600, 19200, 230400, 4800, 230400]


def listen(port, baud, seconds):
    """Read from one port at one baud rate; return any bytes seen."""
    try:
        ser = serial.Serial(port, baud, timeout=0.2)
    except Exception as err:
        return None, str(err)
    got = b""
    try:
        end = time.time() + seconds
        while time.time() < end:
            chunk = ser.read(256)
            if chunk:
                got += chunk
    except Exception:
        pass
    finally:
        try:
            ser.close()
        except Exception:
            pass
    return got, None


def main():
    """Sweep every free UART and baud rate, reporting anything that arrives."""
    per = 4
    if len(sys.argv) > 1:
        per = int(sys.argv[1])

    print("Passive listen only - nothing is transmitted.")
    print("ttySAC1 (console) is excluded.\n")

    hits = 0
    for port in PORTS:
        print("== %s ==" % port)
        for baud in BAUDS:
            data, err = listen(port, baud, per)
            if err:
                print("   %-7d cannot open: %s" % (baud, err))
                continue
            if data:
                hits += 1
                printable = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
                print("   %-7d GOT %d bytes: %s" % (baud, len(data), printable[:200]))
                print("            hex: %s" % data[:64].encode("hex"))
            else:
                print("   %-7d silent" % baud)
        print()

    print("Total ports/bauds with data: %d" % hits)
    return 0


if __name__ == "__main__":
    sys.exit(main())