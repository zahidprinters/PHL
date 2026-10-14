#!/usr/bin/env python2
"""Capture repeated EMA status frames, so an input change can be spotted.

The STM8 volunteers exactly ONE status frame per open, then goes quiet. That is
no good for watching a physical input: by the time you bridge IN1, nothing more
is coming. So this re-triggers the exchange - close then open - once per cycle.

Both frames used here are the vendor's own handshake frames:
    close  55 04 01 00      open  55 04 01 01
They were the only two frames ever transmitted while mapping this link, and
neither actuates anything. No GPO, relay or Wiegand command is sent.

Output is grouped per cycle and ends with a per-byte summary, which is how a
physical short gets matched to a frame field: bridge the input, and whichever
byte position changes is that input.

Runs on the board (python2 + pyserial, both present).

    ./ema_capture.py --cycles 4 --hold 3
"""

import sys
import time

import serial

PORT = "/dev/ttySAC0"
BAUD = 115200
SOF = 0x55

FRAME_OPEN = "\x55\x04\x01\x01"
FRAME_CLOSE = "\x55\x04\x01\x00"


def hexs(data):
    """Render bytes as spaced hex, for a human."""
    return " ".join("%02x" % ord(b) for b in data)


class Parser(object):
    """Resyncs on 0x55 and splits the stream into length-delimited frames."""

    def __init__(self):
        self.buf = ""

    def feed(self, chunk):
        """Add received data and return every complete frame it revealed."""
        self.buf += chunk
        frames = []
        start_byte = chr(SOF)
        while True:
            if start_byte not in self.buf:
                self.buf = ""
                break
            start = self.buf.index(start_byte)
            if start:
                self.buf = self.buf[start:]
            if len(self.buf) < 2:
                break
            length = ord(self.buf[1])
            if length < 2 or length > 64:
                self.buf = self.buf[1:]
                continue
            if len(self.buf) < length:
                break
            frames.append(self.buf[:length])
            self.buf = self.buf[length:]
        return frames


def status_frames(frames):
    """Keep only the 10-byte status frames, dropping the 4-byte acks."""
    return [f for f in frames if len(f) == 10]


def main():
    """Cycle open/collect/close and report every status frame seen."""
    cycles = 4
    hold = 3.0
    for i, a in enumerate(sys.argv):
        if a == "--cycles" and i + 1 < len(sys.argv):
            cycles = int(sys.argv[i + 1])
        if a == "--hold" and i + 1 < len(sys.argv):
            hold = float(sys.argv[i + 1])

    print("EMA capture - %s @ %d 8N1" % (PORT, BAUD))
    print("%d cycles, %.1fs hold each" % (cycles, hold))
    print("sends only open/close handshake frames; no actuator command\n")

    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.2)
    except Exception as err:
        print("cannot open %s: %s" % (PORT, err))
        return 1

    parser = Parser()
    per_cycle = []

    for cycle in range(cycles):
        ser.write(FRAME_OPEN)
        ser.flush()

        got = []
        end = time.time() + hold
        while time.time() < end:
            try:
                chunk = ser.read(64)
            except Exception:
                continue
            if not chunk:
                continue
            got.extend(parser.feed(chunk))

        ser.write(FRAME_CLOSE)
        try:
            ser.flush()
        except Exception:
            pass

        stats = status_frames(got)
        per_cycle.append(stats)

        print("CYCLE %d  (%d status frame%s)" % (cycle + 1, len(stats),
                                                  "" if len(stats) == 1 else "s"))
        for f in got:
            print("    %s" % hexs(f))
        sys.stdout.flush()
        time.sleep(0.4)

    try:
        ser.close()
    except Exception:
        pass

    summarise(per_cycle)
    return 0


def summarise(per_cycle):
    """Show each status frame field across cycles, so a change stands out."""
    allstats = [f for stats in per_cycle for f in stats]
    if not allstats:
        print("\nNO status frames captured - check wiring or the link.")
        return

    width = max(len(f) for f in allstats)
    print("\n=== per-cycle comparison of the 10-byte status frame ===")
    print("byte | " + " | ".join("cyc%d" % (i + 1) for i in range(len(per_cycle))))
    for i in range(width):
        cells = []
        for stats in per_cycle:
            if not stats:
                cells.append("--")
                continue
            vals = sorted(set("%02x" % ord(f[i]) for f in stats))
            cells.append("/".join(vals))
        # Mark a position whose value differs between cycles with populated ones.
        distinct = set(c for c in cells if c not in ("--",))
        marker = "  <== VARIES" if len(distinct) > 1 else ""
        print(" [%d] | %s%s" % (i, "  | ".join(cells), marker))


if __name__ == "__main__":
    sys.exit(main())