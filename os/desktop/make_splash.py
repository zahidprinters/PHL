#!/usr/bin/env python3
"""Generate the boot splash: raw BGRA for the fb-early job (fb_early.py).

The vendor s3cfb keeps a 1024x600@32 buffer that the FIMD scaler stretches
to the 1920x1080 HDMI output, so the splash is generated at BUFFER size
(1024x600) and shown scaled full-screen. Writes splash.raw next to this
script; the board copies it verbatim (no image library on the board).
Re-run after editing text/colors, then re-upload splash.raw to the board.
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 600  # fb0 buffer geometry (scaler output = 1920x1080)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splash.raw')


def font(names, size):
    for n in names:
        p = os.path.join(r'C:\Windows\Fonts', n)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit('no font among %s in C:\\Windows\\Fonts' % names)


def main():
    # dark vertical gradient background (near-black navy)
    top, bot = (10, 14, 22), (22, 30, 44)
    row = Image.new('RGB', (1, H))
    row.putdata([tuple(int(top[c] + (bot[c] - top[c]) * y / H)
                       for c in range(3)) for y in range(H)])
    img = row.resize((W, H))

    d = ImageDraw.Draw(img)
    f_title = font(['segoeuib.ttf', 'arialbd.ttf'], 58)
    f_sub = font(['segoeui.ttf', 'arial.ttf'], 25)
    f_small = font(['segoeui.ttf', 'arial.ttf'], 17)

    title, sub = 'ECU-30 HMI', 'Starting...'
    tw = d.textlength(title, font=f_title)
    d.text(((W - tw) / 2, 200), title, font=f_title, fill=(235, 240, 248))
    lw = 250  # accent line under the title
    d.rectangle([(W - lw) / 2, 292, (W + lw) / 2, 296], fill=(52, 152, 219))
    sw = d.textlength(sub, font=f_sub)
    d.text(((W - sw) / 2, 318), sub, font=f_sub, fill=(150, 165, 185))
    d.text((34, H - 48), 'Node-RED  -  EMA Controls', font=f_small,
           fill=(95, 110, 130))

    # fb0 is x8r8g8b8 little-endian: memory bytes B,G,R,A per pixel
    r, g, b = img.split()
    a = Image.new('L', (W, H), 255)
    bgra = Image.merge('RGBA', (b, g, r, a)).tobytes()
    assert len(bgra) == W * H * 4
    with open(OUT, 'wb') as f:
        f.write(bgra)
    print('wrote %s (%d bytes)' % (OUT, len(bgra)))


if __name__ == '__main__':
    main()
