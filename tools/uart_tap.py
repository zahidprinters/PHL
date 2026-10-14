#!/usr/bin/env python2
"""Tap the SoC<->STM8S207 serial link so its protocol can be learned.

Goal: use the board's GPO/GPI/relay/Wiegand WITHOUT depending on Daikin's
CMIMIRDemo or their libraries. The blocker is that the EMA framing lives in
stripped vendor code. This sidesteps that: rather than guess the frame format,
capture what the vendor tool actually sends.

Method: a PTY acts as a man-in-the-middle.

    CMIMIRDemo  ->  /dev/pts/N (the tap)  ->  /dev/ttySACn (the real STM8 link)

Everything in both directions is written to a log with direction markers. Run
CMIMIRDemo pointed at the PTY, press its GPO / relay / Wiegand buttons, and the
exact bytes it sends are recorded. With a few of those, the frame format can be
reimplemented directly in Python via pyserial -- no vendor code at run time.

READ-ONLY with respect to the physical I/O in the sense that this script itself
sends nothing; it only forwards what the vendor tool emits. Pressing the vendor
tool's own relay button WILL actuate the relay, so let the operator decide what to
press.

Run:  ./uart_tap.py <real-port> <baud> [logfile]
"""

import os
import pty
import select
import sys
import termios
import time

import serial


def set_raw(fd):
    """Put a terminal into raw mode so bytes pass through untouched."""
    attrs = termios.tcgetattr(fd)
    new = list(attrs)
    new[0] &= ~(termios.ICANON | termios.ECHO | termios.ISIG)
    new[3] &= ~(termios.ICANON | termios.ECHO | termios.ISIG)
    new[6][termios.VMIN] = 1
    new[6][termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW, new)


def show(data):
    """Render bytes for a human: printable chars plus a hex column."""
    txt = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
    return "%s   | %s" % (data.encode("hex"), txt)


def main():
    """Relay between the PTY and the real UART, logging everything."""
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    real_port = sys.argv[1]
    baud = int(sys.argv[2])
    logfile = sys.argv[3] if len(sys.argv) > 3 else "/root/uart_tap.log"

    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)
    set_raw(master)
    set_raw(slave)

    ser = serial.Serial(real_port, baud, timeout=0)
    log = open(logfile, "wb")

    print("=" * 64)
    print("TAP LIVE")
    print("  real port : %s @ %d" % (real_port, baud))
    print("  use THIS  : %s" % slave_name)
    print("  logging to: %s" % logfile)
    print("  Ctrl+C here stops the tap.")
    print("=" * 64)

    print("\nNow run CMIMIRDemo and choose %s as the serial port." % slave_name)
    print("Press its GPO / relay / Wiegand buttons -- the bytes are recorded.\n")

    try:
        while True:
            readable, _, _ = select.select([master], [], [], 0.2)
            if master in readable:
                try:
                    data = os.read(master, 1024)
                except OSError:
                    break
                if not data:
                    continue
                # vendor app -> STM8
                log.write(b"TX " + data + b"\n")
                log.flush()
                ser.write(data)
                print("TX %s" % show(data))

            # STM8 -> vendor app
            try:
                reply = ser.read(1024)
            except Exception:
                reply = b""
            if reply:
                log.write(b"RX " + reply + b"\n")
                log.flush()
                os.write(master, reply)
                print("RX %s" % show(reply))
    except KeyboardInterrupt:
        print("\nTap stopped.")
    finally:
        try:
            ser.close()
        except Exception:
            pass
        log.close()
        os.close(master)
        os.close(slave)
    return 0


if __name__ == "__main__":
    sys.exit(main())