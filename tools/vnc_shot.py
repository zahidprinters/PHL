#!/usr/bin/env python3
"""Capture the board's X screen over VNC (vino :5900, no-auth) to a PNG.

Why: dd /dev/fb0 is NOT a screenshot on this board — X renders through the
Exynos mixer's own layers and fb0 keeps the stale kernel penguin logo.
The VNC stream is the real screen (what a remote viewer sees).

Does not handle: authentication (vino runs method 'none'), encodings other
than Raw (requests raw explicitly; vino always honours it on a LAN), zlib/
tight/hextile (server is asked for raw only).
Usage: python tools/vnc_shot.py [host] [out.png]   (defaults: board + temp/vnc.png)
"""
import socket
import struct
import sys

from PIL import Image

HOST = sys.argv[1] if len(sys.argv) > 1 else '192.168.100.127'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'temp/vnc.png'
PORT = 5900


def rd(sock, n):
    buf = b''
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise EOFError('connection closed at %d/%d bytes' % (len(buf), n))
        buf += chunk
    return buf


def main():
    s = socket.create_connection((HOST, PORT), timeout=20)
    ver = rd(s, 12)                       # 'RFB 003.008\n'
    s.sendall(b'RFB 003.008\n')
    n_types = rd(s, 1)[0]                 # security handshake (3.8)
    types = rd(s, n_types)
    if 1 not in types:                    # 1 = None
        raise SystemExit('server demands auth (types %r)' % list(types))
    s.sendall(b'\x01')
    result = struct.unpack('!I', rd(s, 4))[0]
    if result != 0:
        raise SystemExit('security result %d' % result)
    s.sendall(b'\x01')                    # ClientInit: shared
    w, h = struct.unpack('!HH', rd(s, 4))
    rd(s, 16)                             # pixel-format + name-length, unused
    nlen = struct.unpack('!I', rd(s, 4))[0]
    rd(s, nlen)                           # desktop name

    # 32bpp, little-endian, R@16 G@8 B@0 -> bytes per pixel are B,G,R,0.
    # Shifts are ONE byte each: red=16 green=8 blue=0 then 3 pad bytes.
    # Writing them as u16s (the old 00 10 00 08 00 00) put green on bit16
    # and made every screenshot come out magenta (255,0,255) — 2026-10-14.
    s.sendall(b'\x00\x00\x00\x00\x20\x18\x00\x01\x00\xff\x00\xff\x00\xff'
              b'\x10\x08\x00\x00\x00\x00')                      # SetPixelFormat
    s.sendall(struct.pack('!BBH', 2, 0, 1) + struct.pack('!i', 0))  # raw only
    s.sendall(struct.pack('!BBHHHH', 3, 0, 0, 0, w, h))             # full update

    msg = rd(s, 1)[0]
    if msg != 0:
        raise SystemExit('expected FramebufferUpdate, got %d' % msg)
    rd(s, 1)
    n_rects = struct.unpack('!H', rd(s, 2))[0]
    px = bytearray()
    for _ in range(n_rects):
        rx, ry, rw, rh, enc = struct.unpack('!HHHH i', rd(s, 12))
        if enc != 0:
            raise SystemExit('server ignored raw request (enc %d)' % enc)
        px += rd(s, rw * rh * 4)
    s.close()
    Image.frombytes('RGBA', (w, h), bytes(px), 'raw', 'BGRA') \
         .convert('RGB').save(OUT)
    print('saved %s (%dx%d, %d rects)' % (OUT, w, h, n_rects))


if __name__ == '__main__':
    main()
