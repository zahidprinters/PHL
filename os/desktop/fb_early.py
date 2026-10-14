#!/usr/bin/env python2
"""Force the HDMI framebuffer to 1080p early in boot and show the splash,
re-painting until Xorg takes over.

Why: the board's u-boot runs its built-in default environment, so the kernel
gets empty fb_x_res/fb_y_res/hdmi_phy_res and s3cfb sits at its default
1024x1200 -- a mode the HDMI PHY cannot clock out. The monitor shows
"No Signal" until Xorg mode-sets (~20 s into boot). The upstart job runs
this after `started mountall` -- the rootfs is still read-only before that,
and the original `start on startup` version died on its log redirection
(never once executed; proven by the empty pixclk history in dmesg).

The monitor only reports HDMI online ~17 s into boot and the hotplug
handler may renegotiate the pipeline, so the mode-set + paint is REPEATED
every second until /tmp/.X0-lock appears (X owns the fb) or 60 s pass.
Splash = /root/splash.raw at the driver's real buffer size (1024x600@32,
FIMD-scaled to the 1080p output), copied into both buffer halves.

Limits: fixed 1920x1080 (the panel in use); splash copied raw (no
scaling/rotation); a failed ioctl is retried next tick, only logged on
state change.
"""
import array
import fcntl
import mmap
import os
import sys
import time

FBIOGET_VSCREENINFO = 0x4600
FBIOPUT_VSCREENINFO = 0x4601
FBIOGET_FSCREENINFO = 0x4602
FB_ACTIVATE_NOW = 0
FB_ACTIVATE_FORCE = 128
FB_SYNC_HOR_HIGH_ACT = 1
FB_SYNC_VERT_HIGH_ACT = 2

SPLASH = '/root/splash.raw'
X_LOCK = '/tmp/.X0-lock'   # Xorg writes it at start; gone means X never ran

# struct fb_var_screeninfo (kernel 3.0, ARM32) = 40 native u32 fields.
# 1080p60 CEA timings: 148.5 MHz pixel clock -> pixclock in picoseconds.
TIMINGS = dict(pixclock=6734, l=148, r=88, u=36, d=4, hsl=44, vsl=5)


def log(msg):
    sys.stdout.write('fb_early: %s\n' % msg)
    sys.stdout.flush()


def build_var(xres, yres, bpp):
    v = array.array('I', [0] * 40)
    v[0], v[1], v[2], v[3] = xres, yres, xres, yres
    v[6] = bpp
    # x8r8g8b8 little-endian: blue in bits 0-7, transparency in 24-31
    v[8], v[9] = 16, 8      # red offset/length
    v[11], v[12] = 8, 8     # green
    v[14], v[15] = 0, 8     # blue
    v[17], v[18] = 24, 8    # transp
    v[21] = FB_ACTIVATE_NOW | FB_ACTIVATE_FORCE
    v[22] = v[23] = 0xFFFFFFFF  # physical size unknown
    v[25] = TIMINGS['pixclock']
    v[26], v[27] = TIMINGS['l'], TIMINGS['r']
    v[28], v[29] = TIMINGS['u'], TIMINGS['d']
    v[30], v[31] = TIMINGS['hsl'], TIMINGS['vsl']
    v[32] = FB_SYNC_HOR_HIGH_ACT | FB_SYNC_VERT_HIGH_ACT
    return v


def main():
    for _ in range(30):  # s3cfb registers ~0.5 s in; wait up to 15 s
        if os.path.exists('/dev/fb0'):
            break
        time.sleep(0.5)
    else:
        log('/dev/fb0 never appeared')
        return 1

    img = None
    if os.path.exists(SPLASH):
        img = open(SPLASH, 'rb').read()

    fd = os.open('/dev/fb0', os.O_RDWR)
    mapped = [None, 0]   # [mmap object, its length]

    def paint():
        """One mode-set + one full paint; returns a short status string."""
        cur = array.array('I', [0] * 40)
        fcntl.ioctl(fd, FBIOGET_VSCREENINFO, cur)
        want = build_var(1920, 1080, cur[6] or 32)
        fcntl.ioctl(fd, FBIOPUT_VSCREENINFO, want)
        # The vendor driver keeps a small window buffer (1024x600@32) that
        # the FIMD scaler stretches to the 1080p HDMI output; var GET after
        # PUT returns that real buffer geometry, and fix smem_len (u32 @20)
        # covers both halves of the double buffer.
        geo = array.array('I', [0] * 40)
        fcntl.ioctl(fd, FBIOGET_VSCREENINFO, geo)
        fix = array.array('B', '\x00' * 80)
        fcntl.ioctl(fd, FBIOGET_FSCREENINFO, fix)
        smem_len = (fix[20] | fix[21] << 8 | fix[22] << 16 | fix[23] << 24)
        xres, yres, bpp = geo[0], geo[1], geo[6]
        frame = xres * yres * (bpp // 8)
        # fb write() returns ENOSPC on this vendor s3cfb - mmap is the way.
        if mapped[0] is None or mapped[1] != smem_len:
            if mapped[0] is not None:
                mapped[0].close()
            mapped[0] = mmap.mmap(fd, smem_len)
            mapped[1] = smem_len
        if img is not None and len(img) == frame:
            off = 0
            while off + frame <= smem_len:  # fill every buffer half
                mapped[0][off:off + frame] = img
                off += frame
            return 'splash shown (%dx%d, %d halves)' % (xres, yres,
                                                        off // frame)
        mapped[0][:smem_len] = '\x00' * smem_len
        if img is None:
            return 'black (no splash file)'
        return 'black (splash %d bytes, buffer needs %d)' % (len(img), frame)

    deadline = time.time() + 60
    last = [None]
    try:
        while True:
            if os.path.exists(X_LOCK):
                log('X took over; last seen: %s' % last[0])
                break
            if time.time() >= deadline:
                log('gave up after 60 s; last seen: %s' % last[0])
                break
            try:
                st = paint()
            except IOError as e:
                st = 'driver refused mode-set: %s' % e
            if st != last[0]:  # only log state changes, not every tick
                log(st)
                last[0] = st
            time.sleep(1.0)
    finally:
        if mapped[0] is not None:
            mapped[0].close()
        os.close(fd)
    return 0


if __name__ == '__main__':
    sys.exit(main())

