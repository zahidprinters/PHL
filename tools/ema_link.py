#!/usr/bin/env python2
"""Talk to the STM8S207 over the SoC link, without any Daikin library.

Everything this needs was measured, not guessed:

    port  /dev/ttySAC0
    baud  115200, 8 data bits, no parity, 1 stop bit, raw
    frame 0x55 | LEN | payload... | 0x00 0x00
          SOF  total length

    open   55 04 01 01      ack 55 04 01 01
    close  55 04 01 00      ack 55 04 01 00
    status 55 0a 03 00 01 01 xx xx 00 00     (~1/second, unsolicited)

The genuinely useful part is CHANGE TRACKING. The STM8 sends these status
frames whether or not anyone asks, so whatever fields differ between frames are
the live inputs -- that is how the digital inputs get identified without
guessing which byte is which.

READ-ONLY BY DEFAULT: it sends only the open and close frames that the vendor
library also sends. It never writes a GPO, relay or Wiegand frame. Writing is a
separate, deliberate mode (--write) that is not implemented here on purpose:
guessing an actuator frame against a live HVAC controller could switch a relay.

Runs on the board (python2 + pyserial, both present).

    ./ema_link.py --seconds 30
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
            # Drop leading junk up to the next start byte.
            if start_byte not in self.buf:
                self.buf = ""
                break
            start = self.buf.index(start_byte)
            if start:
                self.buf = self.buf[start:]
            if len(self.buf) < 2:
                break
            length = ord(self.buf[1])
            # Sanity: a frame cannot be shorter than its own SOF+LEN header.
            if length < 2 or length > 64:
                self.buf = self.buf[1:]
                continue
            if len(self.buf) < length:
                break
            frames.append(self.buf[:length])
            self.buf = self.buf[length:]
        return frames


def classify(frame):
    """Name a frame by its length and type byte, where the type is known."""
    if len(frame) < 3:
        return "short"
    return {2: "ACK", 3: "STATUS"}.get(len(frame), "len%d" % len(frame))


def main():
    """Open the link, log frames, and report which byte positions vary."""
    seconds = 30
    for i, a in enumerate(sys.argv):
        if a == "--seconds" and i + 1 < len(sys.argv):
            seconds = int(sys.argv[i + 1])

    print("EMA link monitor - %s @ %d 8N1" % (PORT, BAUD))
    print("read-only: sends open and close only, never an actuator frame\n")

    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.2)
    except Exception as err:
        print("cannot open %s: %s" % (PORT, err))
        return 1

    print("--> open frame  %s" % hexs(FRAME_OPEN))
    ser.write(FRAME_OPEN)
    ser.flush()
    print()

    parser = Parser()
    seen = []          # every frame body, for change tracking
    end = time.time() + seconds

    while time.time() < end:
        try:
            chunk = ser.read(64)
        except Exception:
            continue
        if not chunk:
            continue
        for frame in parser.feed(chunk):
            body = [ord(c) for c in frame]
            seen.append(body)
            print("%s  [%s]" % (hexs(frame), classify(frame)))
            sys.stdout.flush()

    print("\n<-- close frame %s" % hexs(FRAME_CLOSE))
    try:
        ser.write(FRAME_CLOSE)
        ser.close()
    except Exception:
        pass

    report_changes(seen)
    return 0


def report_changes(frames):
    """Print which byte positions actually varied - those are the live inputs.

    Everything else in the stream is constant overhead. Comparing the first
    frame with the rest shows exactly which fields carry live state, which is
    how a field gets named without the vendor's struct definitions.
    """
    if len(frames) < 2:
        print("\nonly %d frame(s) seen; not enough to compare" % len(frames))
        return

    width = max(len(f) for f in frames)
    varying = [i for i in range(width)
               if len(set(f[i] for f in frames if i < len(f))) > 1]

    print("\n=== %d frames received ===" % len(frames))
    print("byte positions that VARY (live state): %s"
          % (", ".join(str(i) for i in varying) if varying else "none"))
    for i in varying:
        vals = sorted(set(f[i] for f in frames if i < len(f)))
        print("   byte[%d] took values %s" % (i, vals))
    print("byte positions that are CONSTANT: %s"
          % ", ".join(str(i) for i in range(width) if i not in varying))


if __name__ == "__main__":
    sys.exit(main())