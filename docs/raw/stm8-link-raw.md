=== /dev/ttySTM8 : what created it? ===
lrwxrwxrwx 1 root root 10 Oct  4 23:19 /dev/ttySTM8 -> /dev/pts/0
--- driver binding ---

=== registered serial drivers (which one claims it) ===
/dev/tty             /dev/tty        5       0 system:/dev/tty
/dev/console         /dev/console    5       1 system:console
/dev/ptmx            /dev/ptmx       5       2 system
/dev/vc/0            /dev/vc/0       4       0 system:vtmaster
rfcomm               /dev/rfcomm   216 0-255 serial
s3c2410_serial       /dev/ttySAC   204 64-67 serial
serial               /dev/ttyS       4 64-67 serial
pty_slave            /dev/pts      136 0-1048575 pty:slave
pty_master           /dev/ptm      128 0-1048575 pty:master
unknown              /dev/tty        4 1-63 console
--- per-tty uart:unknown lines ---
serinfo:1.0 driver revision:
0: uart:unknown port:00000000 irq:0
1: uart:unknown port:00000000 irq:0
2: uart:unknown port:00000000 irq:0
3: uart:unknown port:00000000 irq:0

=== udev rules / init scripts mentioning ttySTM8 ===
(no output)

=== which kernel module provides the name ===
Module                  Size  Used by
usb_storage            38659  1 
cpufreq_ondemand        6655  1 
fuse                   64741  4 
smsc95xx               12893  0 
usbnet                 15749  1 smsc95xx
nfsd                  252141  0 
exportfs                3844  1 nfsd
btrfs                 574554  0 
--- any vendor/vendorso module ---
usb_storage            38659  1 
cpufreq_ondemand        6655  1 
fuse                   64741  4 
smsc95xx               12893  0 
usbnet                 15749  1 smsc95xx
nfsd                  252141  0 
exportfs                3844  1 nfsd
btrfs                 574554  0

=== is anything holding ttySTM8 right now ===
/dev/pts/0:           4994
--- lsof ---
--- vendor processes ---

=== the second RJ45: any unclaimed ethernet at all ===
[    3.095478] usb 1-2.3: New USB device found, idVendor=0424, idProduct=9512
[    3.175255] Bluetooth: BNEP (Ethernet Emulation) ver 1.3
[    3.507541] usb 1-2.3.1: Manufacturer: SMSC
[    6.854884] smsc95xx v1.0.4
[    6.911721] smsc95xx 1-2.3.1:1.0: eth0: register 'smsc95xx' at usb-s5p-ehci-2.3.1, smsc95xx USB 2.0 Ethernet, 00:25:ff:fe:44:45
[    6.911849] usbcore: registered new interface driver smsc95xx
[    7.691843] ADDRCONF(NETDEV_UP): eth0: link is not ready
[    9.256140] ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[    9.257233] smsc95xx 1-2.3.1:1.0: eth0: link up, 100Mbps, full-duplex, lpa 0x45E1
--- every NIC-like device tree node, any depth ---
--- kernel config: is dwmac/macb even built? ---
CONFIG_USB_NET_SMSC95XX=m

=== USB topology: where does each RJ45 hang ===
[    3.096718] usb 1-2.3: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[    3.104521] hub 1-2.3:1.0: USB hub found
[    3.107970] hub 1-2.3:1.0: 3 ports detected
[    3.390286] usb 1-2.3.1: new high speed USB device number 4 using s5p-ehci
[    3.496018] usb 1-2.3.1: New USB device found, idVendor=0424, idProduct=ec00
[    3.499962] usb 1-2.3.1: New USB device strings: Mfr=1, Product=0, SerialNumber=0
[    3.507541] usb 1-2.3.1: Manufacturer: SMSC
[    6.911721] smsc95xx 1-2.3.1:1.0: eth0: register 'smsc95xx' at usb-s5p-ehci-2.3.1, smsc95xx USB 2.0 Ethernet, 00:25:ff:fe:44:45
[    9.257233] smsc95xx 1-2.3.1:1.0: eth0: link up, 100Mbps, full-duplex, lpa 0x45E1
[ 4228.310563] usb 1-2.3.2: new high speed USB device number 5 using s5p-ehci
[ 4228.805149] usb 1-2.3.2: device not accepting address 5, error -71
[ 4228.820949] hub 1-2.3:1.0: unable to enumerate USB device on port 2
[ 4229.025594] usb 1-2.3.2: new high speed USB device number 7 using s5p-ehci
[ 4229.131949] usb 1-2.3.2: New USB device found, idVendor=abcd, idProduct=1234
[ 4229.132007] usb 1-2.3.2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[ 4229.132055] usb 1-2.3.2: Product: UDisk           
[ 4229.132091] usb 1-2.3.2: Manufacturer: General 
[ 4229.132125] usb 1-2.3.2: SerialNumber: \xffffffd0\xffffff89\xffffff89
[ 4229.186275] scsi0 : usb-storage 1-2.3.2:1.0
[ 4270.605580] usb 1-2.3.2: USB disconnect, device number 7
--- lsusb tree ---
/:  Bus 02.Port 1: Dev 1, Class=root_hub, Driver=s5p-ohci/3p, 12M
/:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=s5p-ehci/3p, 480M
    |__ Port 2: Dev 2, If 0, Class=hub, Driver=hub/3p, 480M
        |__ Port 3: Dev 3, If 0, Class=hub, Driver=hub/3p, 480M
            |__ Port 1: Dev 4, If 0, Class=vend., Driver=smsc95xx, 480M

=== 93LC66A EEPROMs: not on I2C, so SPI or STM8-side ===
--- spidev present? ---
no /dev/spidev
--- any driver/module naming the part ---
--- any file on the box referencing it ---
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/i2c/at24.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/include/linux/i2c/at24.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/include/config/eeprom/at24.h
/usr/src/linux-headers-3.0.60-odroidx2/include/linux/i2c/at24.h

=== what the vendor app calls this port ===
--- from the ema library ---
/dev/ttyS0
/dev/ttySAC0
14QextSerialPort
20QextSerialEnumerator
Bluetooth-serial adapter 
QextSerialEnumerator
QextSerialPort
Serial port 
USB-serial adapter 
_ZN14QextSerialPort10dsrChangedEb
_ZN14QextSerialPort10lineStatusEv
_ZN14QextSerialPort10setTimeoutEl
_ZN14QextSerialPort11errorStringEv
_ZN14QextSerialPort11qt_metacallEN11QMetaObject4CallEiPPv
_ZN14QextSerialPort11qt_metacastEPKc

