# Raw evidence — RTC (MCP7940N) + 93LC66A EEPROMs

Captured over SSH on 2026-10-11 by `tools/rtc_probe.py` + `tools/mcp7940_dump.c`.
Strictly read-only: I2C reads, `ethtool -e` (read), config/dmesg inspection.

## MCP7940N register dump (read-only, /dev/i2c-1 addr 0x6f, I2C_SLAVE_FORCE)

```
reg  hex
00   c9
01   30
02   00
03   28
04   00
05   00
06   00
07   80
08   ea
09   00
0a   00
0b   00
0c   00
0d   01
0e   00
0f   00
10   00
11   00
12   00
13   00
14   00
15   01
16   00
17   00
18   00
19   00
1a   00
1b   00
1c   00
1d   00
1e   00
1f   00

-- decode --
ST bit (reg0x00 bit7, oscillator run): RUNNING (1)
seconds : 49 (BCD)
minutes : 30 (BCD)
hours   : 00 (BCD, 12/24 bit=0)
dow     : 28   mday: 00   month: 00   year: 00
mday valid for rtc_valid_tm: NO (=0) -> kernel returns EINVAL
control (0x07): 80

-- tick test (1.3 s apart) --
reg0x00: c9 -> d1 : CHANGING (clock is running)
```

Earlier attempt without FORCE:

```
I2C_SLAVE 0x6f: Device or resource busy
```

## RTC driver / boot / sysfs

```
rtc-mcp7940n 1-006f: chip found, driver version 0.1
using rtc device, rtc-mcp7940n, for alarms
rtc-mcp7940n 1-006f: rtc core: registered rtc-mcp7940n as rtc0
rtc-mcp7940n 1-006f: hctosys: unable to read the hardware clock

/sys/class/rtc/rtc0 -> .../s3c2440-i2c.1/i2c-1/1-006f/rtc/rtc0
  rtc0/name: rtc-mcp7940n
  rtc0/date: Invalid argument
  rtc0/time: Invalid argument
hwclock -r: ioctl(RTC_RD_TIME) ... failed: Invalid argument

zcat /proc/config.gz:
CONFIG_RTC_HCTOSYS=y
CONFIG_RTC_HCTOSYS_DEVICE="rtc0"
CONFIG_RTC_DRV_MCP7940N=y
# CONFIG_RTC_DRV_S3C is not set
# CONFIG_RTC_DRV_MAX77686 is not set
```

## Who sets the clock (nobody found)

```
date: Fri Oct  9 01:07:26 KST 2026   <- correct despite failed hctosys
uptime: 30 min
/etc/adjtime: 0.000000 1399479429 0.000000 / 1399479429 / UTC
init.d: hwclock, hwclock-save present; grep -l hwclock -> only bootlogd matched
ntp processes: none
rc.local: empty (exit 0)
```

## 93LC66A / LAN9512 evidence

```
zcat /proc/config.gz:
# CONFIG_SPI is not set
# CONFIG_EEPROM_93CX6 is not set
# CONFIG_EEPROM_AT24 is not set

/dev/spidev* : none
i2c buses: /dev/i2c-0 1 4 5 8 (s3c2410-i2c x5)
bound devices:
  0-0006 -> dummy          1-0008 -> usb3503
  0-0008 -> usb3503        1-001a -> wm8960
  0-0009 -> max77686       1-006f -> mcp7940n
                           8-0038 -> hdmiphy

lsusb:
  1d6b:0002 S5P EHCI root hub      1d6b:0001 s5p OHCI root hub
  0424:3503 (USB3503 hub)          0424:9512 (LAN9512 hub function)
  0424:ec00 (LAN9512 eth function) 09da:0025 A4tech dongle

eth0: 00:25:ff:fe:44:45  driver /sys/bus/usb/drivers/smsc95xx
dmesg: smsc95xx v1.0.4; eth0 register ... 00:25:ff:fe:44:45; link up 100Mbps FD

ethtool -i eth0 -> supports-eeprom-access: yes
ethtool -e eth0:
Offset          Values
0x0000  a5 00 25 ff fe 44 45 01 04 05 09 04 0a 1d 00 00
0x0010  00 00 00 00 00 00 12 22 12 2b 12 34 12 3d 00 00
0x0020  24 04 12 95 00 01 9b 18 00 02 30 30 01 00 01 00
0x0030  32 00 00 00 00 00 21 03 00 01 0a 03 53 00 4d 00
0x0040  53 00 43 00 12 01 00 02 ff 00 01 40 24 04 00 ec
0x0050  00 01 01 00 00 01 09 02 27 00 01 01 00 e0 01 09
0x0060  04 00 00 03 ff 00 ff 00 12 01 00 02 ff 00 ff 40
0x0070  24 04 00 ec 00 01 01 00 00 01 09 02 27 00 01 01
0x0080  00 e0 01 09 04 00 00 03 ff 00 ff 00 ff ff ff ff
0x0090..0x0160  ff (erased)
```

Decode: `a5` = SMSC valid-EEPROM signature; bytes 1-6 = MAC (= eth0);
0x0020 `24 04 12 95` = VID:PID 0424:9512; 0x0048 `24 04 00 ec` = 0424:ec00;
0x003c `53 00 4d 00 53 00 43 00` = UTF-16 "SMSC".

## Vendor binary string scan (local, vendor-backup/)

```
libcmirisLib2_arm_2.0.92.so: EEPROM class (board number, serial, model,
    Mirlin license, lock/unlock) — MPIC camera over USB, not these chips.
CMIMIRDemo / libemaLib: no eeprom/i2c/spidev/bitbang strings at all.
```
