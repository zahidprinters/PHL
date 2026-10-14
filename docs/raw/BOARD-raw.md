Collected over SSH from the live board by `tools/board_inventory.py`.
Strictly read-only: no writes, no register pokes, no ports opened.

## Board identity

```

compatible: 
hostname  : linaro-ubuntu-desktop
--- os ---
Linux linaro-ubuntu-desktop 3.0.68 #11 SMP Wed May 7 10:42:42 KST 2014 armv7l armv7l armv7l GNU/Linux
```

## CPU

```
cores online/present: 0,3 0-3 
Hardware	: ODROIDX
Revision	: 0000
Serial		: 0000000000000000
features  : Features	: swp half thumb fastmult vfp edsp thumbee neon vfpv3 tls 
--- freq ---
200000
1200000
ondemand
```

## RAM

```
MemTotal:         991260 kB
MemFree:           62276 kB
SwapTotal:             0 kB
             total       used       free     shared    buffers     cached
Mem:           968        907         60          0        121        518
dt memory reg:
```

## ROM / storage (eMMC + EEPROMs)

```
brw-rw---- 1 root disk 179,  0 Jan  1  1970 /dev/mmcblk0
brw-rw---- 1 root disk 179, 16 Jan  1  1970 /dev/mmcblk0boot0
brw-rw---- 1 root disk 179, 32 Jan  1  1970 /dev/mmcblk0boot1
brw-rw---- 1 root disk 179,  1 Jan  1  1970 /dev/mmcblk0p1
brw-rw---- 1 root disk 179,  2 Jan  1  1970 /dev/mmcblk0p2
--- sizes ---
major minor  #blocks  name

 179        0    7634944 mmcblk0
 179        1     131072 mmcblk0p1
 179        2    5633024 mmcblk0p2
 179       32       4096 mmcblk0boot1
 179       16       4096 mmcblk0boot0
--- fs ---
Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.3G  3.0G  2.1G  59% /
/dev/mmcblk0p2  5.3G  3.0G  2.1G  59% /
eMMC name  : H8G2d
eMMC cid   : 90014a48384732640403007bbfa24123
eMMC manfid: 0x000090
eMMC oemid : 0x014a
--- spi/nor ---
```

## Ethernet: why 2 RJ45 but only 1 interface

```
=== interfaces Linux has ===
eth0
ip6tnl0
lo
sit0
  eth0     driver=smsc95xx   mac=00:25:ff:fe:44:45
  ip6tnl0  driver=           mac=00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
  sit0     driver=           mac=00:00:00:00
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN 
    inet 127.0.0.1/8 scope host lo
4: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1488 qdisc pfifo_fast state UP qlen 1000
    inet 192.168.100.127/24 brd 192.168.100.255 scope global eth0
=== is the native SoC GMAC present at all? ===
dw_mmc
=== ethernet device-tree nodes and their status ===
=== kernel messages about ethernet ===
[    3.175255] Bluetooth: BNEP (Ethernet Emulation) ver 1.3
[    3.507541] usb 1-2.3.1: Manufacturer: SMSC
[    6.854884] smsc95xx v1.0.4
[    6.911721] smsc95xx 1-2.3.1:1.0: eth0: register 'smsc95xx' at usb-s5p-ehci-2.3.1, smsc95xx USB 2.0 Ethernet, 00:25:ff:fe:44:45
[    6.911849] usbcore: registered new interface driver smsc95xx
[    7.691843] ADDRCONF(NETDEV_UP): eth0: link is not ready
[    9.256140] ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[    9.257233] smsc95xx 1-2.3.1:1.0: eth0: link up, 100Mbps, full-duplex, lpa 0x45E1
=== USB ethernet chip (the LAN9512) ===
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 001 Device 002: ID 0424:3503 Standard Microsystems Corp. 
Bus 001 Device 003: ID 0424:9512 Standard Microsystems Corp. 
Bus 001 Device 004: ID 0424:ec00 Standard Microsystems Corp. 
smsc95xx               12893  0 
usbnet                 15749  1 smsc95xx
```

## USB: 4 ports + the mystery micro-USB

```
=== host controllers in device-tree ===
=== host controller drivers present ===
s3c-usbgadget
s5p-ehci
s5p-ohci
=== currently enumerated USB devices ===
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 001 Device 002: ID 0424:3503 Standard Microsystems Corp. 
Bus 001 Device 003: ID 0424:9512 Standard Microsystems Corp. 
Bus 001 Device 004: ID 0424:ec00 Standard Microsystems Corp. 
=== which port is the OTG/device port? ===
no /sys/class/udc (no gadget controller registered)
--- adb/gadget running? ---
root      7188  0.0  0.1   3748  1136 ?        Ss   00:14   0:00 bash -c ?echo '=== host controllers in device-tree ==='?for n in $(find /proc/device-tree -maxdepth 3 -name 'usb@*' 2>/dev/null); do?  printf '%-46s dr_mode=[%s] status=[%s]\n' "$n" \?    "$(tr '\0' ' ' < $n/dr_mode 2>/dev/null)" "$(tr '\0' ' ' < $n/status 2>/dev/null)"?done?echo '=== host controller drivers present ==='?ls /sys/bus/platform/drivers/ 2>/dev/null | grep -iE 'dwc|ehci|ohci|usb'?echo '=== currently enumerated USB devices ==='?lsusb 2>/dev/null?echo '=== which port is the OTG/device port? ==='?ls -l /sys/class/udc/ 2>/dev/null || echo 'no /sys/class/udc (no gadget controller registered)'?echo '--- adb/gadget running? ---'; ps aux | grep -E '[a]dbd|[g]_serial' || echo 'no adbd/gadget'?echo '--- gadget configfs ---'; ls /sys/kernel/config/usb_gadget/ 2>/dev/null || echo 'no gadget configured'?echo '=== hub / port events ==='?dmesg 2>/dev/null | grep -iE 'ehci|ohci|new .* USB device|hub' | tail -12
--- gadget configfs ---
no gadget configured
=== hub / port events ===
[    2.209597] hub 2-0:1.0: 3 ports detected
[    2.570069] usb 1-2: new high speed USB device number 2 using s5p-ehci
[    2.714124] hub 1-2:1.0: USB hub found
[    2.717343] hub 1-2:1.0: 3 ports detected
[    3.005153] usb 1-2.3: new high speed USB device number 3 using s5p-ehci
[    3.104521] hub 1-2.3:1.0: USB hub found
[    3.107970] hub 1-2.3:1.0: 3 ports detected
[    3.390286] usb 1-2.3.1: new high speed USB device number 4 using s5p-ehci
[    6.911721] smsc95xx 1-2.3.1:1.0: eth0: register 'smsc95xx' at usb-s5p-ehci-2.3.1, smsc95xx USB 2.0 Ethernet, 00:25:ff:fe:44:45
[ 4228.310563] usb 1-2.3.2: new high speed USB device number 5 using s5p-ehci
[ 4228.820949] hub 1-2.3:1.0: unable to enumerate USB device on port 2
[ 4229.025594] usb 1-2.3.2: new high speed USB device number 7 using s5p-ehci
```

## Serial: RS232 / RS485 / console / STM8 link

```
=== tty devices present ===
/dev/ttyS0
/dev/ttyS1
/dev/ttyS2
/dev/ttyS3
/dev/ttySAC0
/dev/ttySAC0
/dev/ttySAC1
/dev/ttySAC1
/dev/ttySAC2
/dev/ttySAC2
/dev/ttySAC3
/dev/ttySAC3
/dev/ttySTM8
=== DT aliases (which serial is which) ===
=== per-UART DT status (a disabled node never registers a tty) ===
=== console ===
console=tty1
console=ttySAC1,115200n8
=== who holds a free serial port (the STM8 link lives here) ===
  /dev/ttySAC0: /dev/ttySAC0:         4994
  /dev/ttySAC2:   /dev/ttySAC3: === Daikin vendor stack (the STM8 owner) ===
CMIMIRDemo
/usr/local/lib/libcmicolorLib_arm_0.9.0.so
/usr/local/lib/libcmirisLib2_arm_2.0.92.so
/usr/local/lib/libemaLib_arm_1.0.1.so
root      7202  4.0  0.1   3752  1168 ?        Ss   00:14   0:00 bash -c ?echo '=== tty devices present ==='; ls /dev/ttyS* /dev/ttySAC* /dev/ttyUSB* /dev/ttyACM* 2>/dev/null?echo '=== DT aliases (which serial is which) ==='?tr '\0' '\n' < /proc/device-tree/aliases 2>/dev/null | grep -iE 'serial|uart'?echo '=== per-UART DT status (a disabled node never registers a tty) ==='?for n in $(find /proc/device-tree -maxdepth 3 -name 'serial@*' 2>/dev/null); do?  printf '  %-44s status=[%s]\n' "$n" "$(tr '\0' ' ' < $n/status 2>/dev/null)"?done?echo '=== console ==='; cat /proc/cmdline | tr ' ' '\n' | grep -i console?echo '=== who holds a free serial port (the STM8 link lives here) ==='?for p in /dev/ttySAC0 /dev/ttySAC2 /dev/ttySAC3; do printf '  %s: ' $p; fuser $p 2>&1 | tail -1; done?echo '=== Daikin vendor stack (the STM8 owner) ==='?ls /usr/local/bin/ 2>/dev/null | head; ls /usr/local/lib/*.so 2>/dev/null?ps aux | grep -iE '[C]MIMIR|[c]miris' || echo 'no CMIMIR process running'
```

## Digital I/O (IN1/IN2, GPO OUT1/OUT2)

```
=== sysfs gpio export API ===
ABSENT: /sys/class/gpio missing
=== gpiochip char devices (libgpiod) ===
ABSENT: no /dev/gpiochip*
=== kernel GPIO consumers (read-only listing) ===
debugfs pins claimed: 0
GPIOs 0-7, GPA0:

GPIOs 9-14, GPA1:

GPIOs 16-23, GPB:

GPIOs 25-29, GPC0:

GPIOs 31-35, GPC1:
 gpio-31  (STATUS LED          ) out hi

GPIOs 37-40, GPD0:
 gpio-38  (Backlight           ) in  lo

GPIOs 42-45, GPD1:

GPIOs 47-54, GPF0:

GPIOs 56-63, GPF1:

=== industrialio / relay / wiegand ===
no iio/relay/wiegand module
no IIO devices
```

## I2C buses + 93LC66A EEPROMs

```
/dev/i2c-0
/dev/i2c-1
/dev/i2c-4
/dev/i2c-5
/dev/i2c-8
=== adapters ===
  i2c-0    name=s3c2410-i2c
  i2c-1    name=s3c2410-i2c
  i2c-4    name=s3c2410-i2c
  i2c-5    name=s3c2410-i2c
  i2c-8    name=s3c2410-i2c
=== every device bound on I2C ===
  0-0006         dummy
  0-0008         usb3503
  0-0009         max77686
  1-0008         usb3503
  1-001a         wm8960
  1-006f         mcp7940n
  8-0038         hdmiphy
  i2c-0          s3c2410-i2c
  i2c-1          s3c2410-i2c
  i2c-4          s3c2410-i2c
  i2c-5          s3c2410-i2c
  i2c-8          s3c2410-i2c
=== 93LC66A usually sits at 0x50-0x57; read-only probe of that range ===
--- /dev/i2c-0 ---
bash: line 11: i2cdetect: command not found
--- /dev/i2c-1 ---
bash: line 11: i2cdetect: command not found
--- /dev/i2c-4 ---
bash: line 11: i2cdetect: command not found
--- /dev/i2c-5 ---
bash: line 11: i2cdetect: command not found
```

## Audio (WM8960 + L/R)

```
 0 [Ctiswm8960     ]: Ctis_wm8960 - Ctis_wm8960
                      Ctis_wm8960
--- playback pcm ---
**** List of PLAYBACK Hardware Devices ****
card 0: Ctiswm8960 [Ctis_wm8960], device 0: Playback wm8960-hifi-0 []
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: Ctiswm8960 [Ctis_wm8960], device 1: Capture wm8960-hifi-1 []
  Subdevices: 1/1
  Subdevice #0: subdevice #0
--- codec driver ---
/sys/bus/i2c/devices/1-001a/name
```

## Power: 12 V header, regulators, RTC

```
=== regulators declared in DT ===
=== rtc ===
rtc0
rtc-mcp7940n
=== I2C drivers bound (incl. PMIC) ===
dummy
exynos_hdcp
max77686
rtc-mcp7940n
s5p-hdmiphy
usb3503
wm8960-codec
```

