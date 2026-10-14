# Debug port (ttySAC1) — PuTTY capture, 2026-10-12

Rig: 1.8 V USB-UART adapter + level shifter -> board 4-pin header (VCC/TX/RX/GND)
-> Prolific PL2303 on COM4, PuTTY @ 115200 8N1, DTR asserted (default).

No Ethernet attached. Board booted the **vendor OS from the SD card** to a root
shell over the debug port alone. Key excerpts from the capture:

## U-Boot
```
U-Boot 2010.12-svn (Dec 21 2012 - 19:44:04) for Exynox4412
CPU: S5PC220 [Samsung SOC on SMP Platform Base on ARM CortexA9]
DRAM:  2047 MiB
Checking Boot Mode ... SDMMC
MMC Device 0: 60906 MB
ModeKey Check... run normal_boot
Net:   No ethernet found.
Hit any key to stop autoboot:  0
reading zImage  2300364 bytes read
reading uInitrd 3042217 bytes read
```

## Kernel cmdline (note console + root UUID)
```
Kernel command line: console=tty1 console=ttySAC1,115200n8 fb_x_res= fb_y_res=
  hdmi_phy_res= root=UUID=e139ce78-9841-40fe-8823-96a304a09859 rootwait ro mem=1023M
Linux version 3.0.68 (root@mkjasia) ... #11 SMP Wed May 7 10:42:42 KST 2014
Machine: ODROIDX
```

## Peripherals all probe clean
```
rtc-mcp7940n 1-006f: chip found, driver version 0.1
rtc-mcp7940n 1-006f: rtc core: registered rtc-mcp7940n as rtc0
wm8960 i2c probe
wm8960-codec 1-001a: No platform data supplied
asoc: wm8960-hifi <-> samsung-i2s.0 mapping ok
  #0: Ctis_wm8960
usb 1-2.3:   idVendor=0424, idProduct=9512   (LAN9512 hub fn)
usb 1-2.3.1: idVendor=0424, idProduct=ec00   Manufacturer: SMSC  (LAN9512 eth fn)
```

## RTC still uninitialised (2001)
```
rtc-mcp7940n 1-006f: setting system clock to 2001-01-01 01:31:30 UTC (978312690)
```

## Root filesystem = the SD clone
```
mmcblk0: mmc1:aaaa SD64G 59.4 GiB
 mmcblk0: p1 p2 p3
EXT4-fs (mmcblk0p2): mounted filesystem without journal.
```

## First boot did a forced fsck (power was yanked) then auto-rebooted
```
rootfs was not cleanly unmounted, check forced.
rootfs: ***** FILE SYSTEM WAS MODIFIED *****
rootfs: ***** REBOOT LINUX *****
mountall: System must be rebooted: /
[   20.338136] Restarting system.
```
Second boot: `rootfs: clean` -> reached login.

## Login / shell
```
Welcome to Linaro 12.11 (GNU/Linux 3.0.68 armv7l)
Last login: Mon Jan  1 10:30:11 KST 2001 on tty1
root@linaro-ubuntu-desktop:~#
```

Full unfiltered capture is in the chat session; this file keeps the load-bearing
lines. Boot log also served as live confirmation of the RTC-2001 finding and of
every peripheral's driver probing successfully.
