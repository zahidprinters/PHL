# Board full survey - raw capture over SSH (192.168.100.127)
# Read-only. One section per marker @@@ name @@@.


@@@ identity @@@
Linux linaro-ubuntu-desktop 3.0.68 #11 SMP Wed May 7 10:42:42 KST 2014 armv7l armv7l armv7l GNU/Linux

processor	: 0
processor	: 3
Features	: swp half thumb fastmult vfp edsp thumbee neon vfpv3 tls 
Hardware	: ODROIDX
Revision	: 0000
Serial		: 0000000000000000

2

MemTotal:         991260 kB
MemFree:          537288 kB
Buffers:           30528 kB
Cached:           224324 kB
SwapCached:            0 kB

@@@ cmdline @@@
console=tty1 console=ttySAC1,115200n8 fb_x_res= fb_y_res= hdmi_phy_res= root=UUID=e139ce78-9841-40fe-8823-96a304a09859 rootwait ro mem=1023M

@@@ os @@@
Linaro 12.11 \n \l

DISTRIB_ID=Ubuntu
DISTRIB_RELEASE=12.11
DISTRIB_CODENAME=precise
DISTRIB_DESCRIPTION="Linaro 12.11"

Linux version 3.0.68 (root@mkjasia) (gcc version 4.7.3 20121106 (prerelease) (crosstool-NG linaro-1.13.1-4.7-2012.11-20121123 - Linaro GCC 2012.11) ) #11 SMP Wed May 7 10:42:42 KST 2014

@@@ interrupts @@@
           CPU0       CPU3       
 18:       1793          0  s3c-uart
 20:          0          0  s3c-uart  s5pv210-uart
 22:         53          0  s3c-uart  s5pv210-uart
 98:          0          0       GIC  s3c-pl330.0
 99:          0          0       GIC  s3c-pl330.1
100:          0          0       GIC  s3c-pl330.2
107:          0          0       GIC  s3c2410-wdt
121:          9          0       GIC  mct_comp_irq
122:       1058          0       GIC  s3c2440-i2c.0
123:        160          0       GIC  s3c2440-i2c.1
126:          0          0       GIC  s3c2440-i2c.4
127:          0          0       GIC  s3c2440-i2c.5
134:       1052          0       GIC  ehci_hcd:usb1, ohci_hcd:usb2
135:          0          0       GIC  s3c-udc
139:      25241          0       GIC  mmc1
140:          0          0       GIC  mmc2
141:        182          0       GIC  dw-mci
155:       3904          0       GIC  s5p-mixer
156:          1          0       GIC  hdmi
157:        154          0       GIC  s3c2440-hdmiphy-i2c
212:          0          0  COMBINER  tmu interrupt
236:          0          0  COMBINER  s5p-sysmmu.12
281:          0          0  COMBINER  s3cfb
358:          0          0  exynos-eint  usb3503-irq
376:          0          0  exynos-eint  usb3503-irq
IPI0:          0          0          0          0  Timer broadcast interrupts
IPI1:       8508       9854       9811       7554  Rescheduling interrupts
IPI2:         77         51         78         75  Function call interrupts
IPI3:          0          1          0          1  Single function call interrupts
IPI4:          0          0          0          0  CPU stop interrupts
IPI5:          0          0          0          0  CPU backtrace
LOC:       7528       5941       6552       4963  Local timer interrupts
Err:          0

@@@ dmesg-boot @@@
[    0.000000] Initializing cgroup subsys cpuset
[    0.000000] Initializing cgroup subsys cpu
[    0.000000] Linux version 3.0.68 (root@mkjasia) (gcc version 4.7.3 20121106 (prerelease) (crosstool-NG linaro-1.13.1-4.7-2012.11-20121123 - Linaro GCC 2012.11) ) #11 SMP Wed May 7 10:42:42 KST 2014
[    0.000000] CPU: ARMv7 Processor [413fc090] revision 0 (ARMv7), cr=10c5387d
[    0.000000] CPU: VIPT nonaliasing data cache, VIPT aliasing instruction cache
[    0.000000] Machine: ODROIDX
[    0.000000] Memory policy: ECC disabled, Data cache writealloc
[    0.000000] CPU EXYNOS4412 (id 0xe4412211)
[    0.000000] exynos4_init_clocks: initializing clocks
[    0.000000] S3C24XX Clocks, Copyright 2004 Simtec Electronics
[    0.000000] s3c_register_clksrc: clock audiocdclk has no registers set
[    0.000000] audiocdclk: no parent clock specified
[    0.000000] s3c_register_clksrc: clock armclk has no registers set
[    0.000000] exynos4_setup_clocks: registering clocks
[    0.000000] exynos4_setup_clocks: xtal is 24000000
[    0.000000] EXYNOS4: PLL settings, A=1000000000, M=880000000, E=96000000 V=350000000
[    0.000000] EXYNOS4: ARMCLK=1000000000, DMC=440000000, ACLK200=24000000
[    0.000000] ACLK160=176000000, ACLK133=146666666, ACLK100=110000000
[    0.000000] EXYNOS4: ACLK400=24000000 ACLK266=880000000
[    0.000000] Unable to set parent aclk_160 of clock dout_mmc0.
[    0.000000] Unable to set parent aclk_160 of clock dout_mmc1.
[    0.000000] Unable to set parent aclk_160 of clock dout_mmc2.
[    0.000000] uclk1: source is mout_mpll_user (6), rate is 110000000
[    0.000000] uclk1: source is mout_mpll_user (6), rate is 110000000
[    0.000000] uclk1: source is mout_mpll_user (6), rate is 110000000
[    0.000000] uclk1: source is mout_mpll_user (6), rate is 110000000
[    0.000000] sclk_csis: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_csis: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_cam0: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_cam1: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_fimc: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_fimc: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_fimc: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_fimc: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_fimd: source is mout_mpll_user (6), rate is 55000000
[    0.000000] sclk_fimd: source is xusbxti (1), rate is 1500000
[    0.000000] sclk_mfc: source is mout_mfc0 (0), rate is 55000000
[    0.000000] sclk_g3d: source is mout_g3d0 (0), rate is 55000000
[    0.000000] sclk_pwi: source is xusbxti (1), rate is 1500000
[    0.000000] On node 0 totalpages: 261888
[    0.000000] free_area_init_node: node 0, pgdat c062a6e0, node_mem_map c0665000
[    0.000000]   Normal zone: 1472 pages used for memmap
[    0.000000]   Normal zone: 0 pages reserved
[    0.000000]   Normal zone: 186944 pages, LIFO batch:31
[    0.000000]   HighMem zone: 574 pages used for memmap
[    0.000000]   HighMem zone: 72898 pages, LIFO batch:15
[    0.000000] PERCPU: Embedded 7 pages/cpu @c0e6c000 s5792 r8192 d14688 u32768
[    0.000000] pcpu-alloc: s5792 r8192 d14688 u32768 alloc=8*4096
[    0.000000] pcpu-alloc: [0] 0 [0] 1 [0] 2 [0] 3 
[    0.000000] Built 1 zonelists in Zone order, mobility grouping on.  Total pages: 259842
[    0.000000] Kernel command line: console=tty1 console=ttySAC1,115200n8 fb_x_res= fb_y_res= hdmi_phy_res= root=UUID=e139ce78-9841-40fe-8823-96a304a09859 rootwait ro mem=1023M
[    0.000000] PID hash table entries: 4096 (order: 2, 16384 bytes)
[    0.000000] Dentry cache hash table entries: 131072 (order: 7, 524288 bytes)
[    0.000000] Inode-cache hash table entries: 65536 (order: 6, 262144 bytes)
[    0.000000] Memory: 1023MB = 1023MB total
[    0.000000] Memory: 988084k/988084k available, 59468k reserved, 293888K highmem
[    0.000000] Virtual kernel memory layout:
[    0.000000]     vector  : 0xffff0000 - 0xffff1000   (   4 kB)
[    0.000000]     fixmap  : 0xfff00000 - 0xfffe0000   ( 896 kB)
[    0.000000]     DMA     : 0xfea00000 - 0xffe00000   (  20 MB)
[    0.000000]     vmalloc : 0xee800000 - 0xf6000000   ( 120 MB)
[    0.000000]     lowmem  : 0xc0000000 - 0xee000000   ( 736 MB)
[    0.000000]     pkmap   : 0xbfe00000 - 0xc0000000   (   2 MB)
[    0.000000]     modules : 0xbf000000 - 0xbfe00000   (  14 MB)
[    0.000000]       .init : 0xc0008000 - 0xc003c000   ( 208 kB)
[    0.000000]       .text : 0xc003c000 - 0xc05d9000   (5748 kB)
[    0.000000]       .data : 0xc05da000 - 0xc062b340   ( 325 kB)
[    0.000000]        .bss : 0xc062b364 - 0xc0664c1c   ( 231 kB)
[    0.000000] SLUB: Genslabs=13, HWalign=32, Order=0-0, MinObjects=0, CPUs=4, Nodes=1
[    0.000000] Hierarchical RCU implementation.
[    0.000000] NR_IRQS:456
[    0.000000] Console: colour dummy device 80x30
[    0.000000] console [tty1] enabled
[    0.000000] Calibrating delay loop... 1992.29 BogoMIPS (lpj=4980736)
[    0.045000] pid_max: default: 32768 minimum: 301
[    0.045000] Security Framework initialized
[    0.045000] Mount-cache hash table entries: 512
[    0.045000] Initializing cgroup subsys cpuacct
[    0.045000] Initializing cgroup subsys devices
[    0.045000] Initializing cgroup subsys freezer
[    0.045000] Initializing cgroup subsys blkio
[    0.045000] CPU: Testing write buffer coherency: ok
[    0.045000] CPU0: thread -1, cpu 0, socket 10, mpidr 80000a00
[    0.045000] L310 cache controller enabled
[    0.045000] l2x0: 16 ways, CACHE_ID 0x4100c4c8, AUX_CTRL 0x7e470001, Cache size: 1048576 B
[    0.045000] CPU1: Booted secondary processor
[    0.045000] CPU1: thread -1, cpu 1, socket 10, mpidr 80000a01
[    0.045000] CPU2: Booted secondary processor
[    0.045000] CPU2: thread -1, cpu 2, socket 10, mpidr 80000a02
[    0.045000] CPU3: Booted secondary processor
[    0.045000] CPU3: thread -1, cpu 3, socket 10, mpidr 80000a03
[    0.045000] Brought up 4 CPUs
[    0.045000] SMP: Total of 4 processors activated (7969.17 BogoMIPS).
[    0.045000] devtmpfs: initialized
[    0.050000] print_constraints: dummy: 
[    0.050000] NET: Registered protocol family 16
[    0.055000] SMDK MAIN Board Rev 0.1 (ADC value:744)
[    0.170000] exynos4_pmu_init: PMU supports 4412(96)
[    0.170000] S3C Power Management, Copyright 2004 Simtec Electronics
[    0.170000] EXYNOS4: Initializing architecture
[    0.170000] s3c24xx-pwm s3c24xx-pwm.1: tin at 110000000, tdiv at 110000000, tin=divclk, base 8
[    0.170000] s5p-sysmmu s5p-sysmmu.12: Initialized for s5p-mixer.
[    0.180000] bio: create slab <bio-0> at 0
[    0.180000] SCSI subsystem initialized
[    0.180000] usbcore: registered new interface driver usbfs
[    0.180000] usbcore: registered new interface driver hub
[    0.185000] usbcore: registered new device driver usb
[    0.185000] max77686 0-0009: No interrupt specified.
[    0.200000] print_constraints: LDO1 VDD_ALIVE: 1000 mV 
[    0.200000] print_constraints: LDO2 VDDQ_M1_1V4: 1200 mV 
[    0.205000] print_constraints: LDO3 VDDQ_AUD_1V8: 1800 mV 
[    0.205000] print_constraints: LDO4 VDDQ_MMC2_2V8: 2800 mV 
[    0.205000] print_constraints: LDO5 VDDQ_MMC1_1V8: 1800 mV 
[    0.205000] print_constraints: LDO6 VDD10_MPLL_1V0: 1000 mV 
[    0.210000] print_constraints: LDO7 VDD10_EPLL_1V0: 1000 mV 
[    0.210000] print_constraints: LDO8 VDD10_MIPI_1V0: 1000 mV 
[    0.210000] print_constraints: LDO9 VT_CORE_1V8: 1800 mV 
[    0.210000] print_constraints: LDO10 VDD18_MIPI_1V8: 1800 mV 
[    0.210000] print_constraints: LDO11 VDD18_ABB1_1V8: 1800 mV 
[    0.215000] print_constraints: LDO12 VDD33_UOTG_3V3: 3300 mV 
[    0.215000] print_constraints: LDO13 VDD18_MIPIHSI_1V8: 1800 mV 
[    0.215000] print_constraints: LDO14 VDD18_ADC_1V8: 1800 mV 
[    0.215000] print_constraints: LDO15 VDD10_OTG: 1000 mV 
[    0.215000] print_constraints: LDO16 VDD18_HSIC: 1800 mV 
[    0.220000] print_constraints: LDO17 VDDQ_CAM_1V8: 1800 mV 
[    0.220000] print_constraints: LDO18 VDDQ_ISP_1V8: 1800 mV 
[    0.220000] print_constraints: LDO19 VT_CAM_1V8: 1800 mV 
[    0.220000] print_constraints: LDO20 EMMC_IO_1V8: 1800 mV 
[    0.220000] print_constraints: LDO21 TFLASH_2V8: 2800 mV 
[    0.220000] print_constraints: LDO22 2V8: 2800 mV 
[    0.225000] print_constraints: LDO23 VDD_TOUCH_2V8: 2800 mV 
[    0.225000] print_constraints: LDO24 VDD_TOUCHLED_3V3: 3300 mV 
[    0.225000] print_constraints: LDO25 VDDQ_LCD_3V0: 1800 mV 
[    0.225000] print_constraints: LDO26 VDD_MOTOR_3V0: 3000 mV 
[    0.225000] print_constraints: BUCK1 vdd_mif: 1100 mV 
[    0.225000] print_constraints: BUCK2 vdd_arm: 800 <--> 1500 mV at 1300 mV 
[    0.230000] print_constraints: BUCK3 vdd_int: 1125 mV 
[    0.230000] print_constraints: BUCK4 vdd_g3d: 850 <--> 1200 mV at 1100 mV 
[    0.230000] print_constraints: BUCK5 VDDQ_CKEM1_2: 1200 mV 
[    0.230000] print_constraints: BUCK6 1V35: 1350 mV 
[    0.230000] print_constraints: BUCK7 2V0: 2000 mV 
[    0.235000] print_constraints: BUCK8 3V0: 3000 mV 
[    0.235000] print_constraints: BUCK9 1V2: 1200 mV 
[    0.235000] print_constraints: EN32KHz AP: 
[    0.235000] print_constraints: EN32KHz CP: 
[    0.235000] s3c-i2c s3c2440-i2c.0: i2c-0: S3C I2C adapter
[    0.235000] s3c-i2c s3c2440-i2c.1: i2c-1: S3C I2C adapter
[    0.235000] s3c-i2c s3c2440-i2c.4: i2c-4: S3C I2C adapter
[    0.235000] s3c-i2c s3c2440-i2c.5: i2c-5: S3C I2C adapter
[    0.235000] s3c-i2c s3c2440-hdmiphy-i2c: i2c-8: S3C I2C adapter
[    0.235000] Advanced Linux Sound Architecture Driver Version 1.0.24.
[    0.235000] Bluetooth: Core ver 2.16
[    0.240000] NET: Registered protocol family 31
[    0.240000] Bluetooth: HCI device and connection manager initialized
[    0.240000] Bluetooth: HCI socket layer initialized
[    0.240000] Bluetooth: L2CAP socket layer initialized
[    0.240000] Bluetooth: SCO socket layer initialized
[    0.240000] Switching to clocksource mct-frc
[    0.251065] NET: Registered protocol family 2
[    0.251255] IP route cache hash table entries: 32768 (order: 5, 131072 bytes)
[    0.251839] TCP established hash table entries: 131072 (order: 8, 1048576 bytes)
[    0.253318] TCP bind hash table entries: 65536 (order: 7, 524288 bytes)
[    0.254188] TCP: Hash tables configured (established 131072 bind 65536)
[    0.254204] TCP reno registered
[    0.254219] UDP hash table entries: 512 (order: 2, 16384 bytes)
[    0.254256] UDP-Lite hash table entries: 512 (order: 2, 16384 bytes)
[    0.254571] NET: Registered protocol family 1
[    0.254825] RPC: Registered named UNIX socket transport module.
[    0.254842] RPC: Registered udp transport module.
[    0.254855] RPC: Registered tcp transport module.
[    0.254868] RPC: Registered tcp NFSv4.1 backchannel transport module.
[    0.254997] Trying to unpack rootfs image as initramfs...
[    0.420143] Freeing initrd memory: 2968K
[    0.420223] PMU: registered new PMU device of type 0
[    0.420418] Exynos4 : ARM Clock down on idle mode is enabled
[    0.421660] Loaded driver for PL330 DMAC-0 s3c-pl330
[    0.421678] 	DBUFF-64x8bytes Num_Chans-8 Num_Peri-1 Num_Events-32
[    0.421781] Loaded driver for PL330 DMAC-1 s3c-pl330
[    0.421797] 	DBUFF-32x4bytes Num_Chans-8 Num_Peri-32 Num_Events-32
[    0.421900] Loaded driver for PL330 DMAC-2 s3c-pl330
[    0.421916] 	DBUFF-32x4bytes Num_Chans-8 Num_Peri-32 Num_Events-32
[    0.422659] highmem bounce pool size: 64 pages
[    0.422883] ashmem: initialized
[    0.433538] nfs4filelayout_init: NFSv4 File Layout Driver Registering...
[    0.433602] msgmni has been set to 1361
[    0.434553] io scheduler noop registered
[    0.434570] io scheduler deadline registered
[    0.434639] io scheduler cfq registered
[    0.434653] io scheduler sio registered
[    0.434664] io scheduler zen registered
[    0.434886] io scheduler bfq registered (default)
[    0.435240] registerd claa070 LCD Driver.
[    0.435655] s3cfb s3cfb.0: [fb2] dma: 0x6b822000, cpu: 0xee839000, size: 0x004b0000
[    0.438861] FIMD src sclk = 440000000
[    0.438870] s3cfb_lcd_on
[    0.438891] s3cfb s3cfb.0: registered successfully
[    0.439234] Serial: 8250/16550 driver, 4 ports, IRQ sharing disabled
[    0.655245] s5pv210-uart.0: ttySAC0 at MMIO 0x13800000 (irq = 16) is a S3C6400/10
[    0.735068] s5pv210-uart.1: ttySAC1 at MMIO 0x13810000 (irq = 20) is a S3C6400/10
[    1.749428] console [ttySAC1] enabled
[    1.840069] s5pv210-uart.2: ttySAC2 at MMIO 0x13820000 (irq = 24) is a S3C6400/10
[    1.920061] s5pv210-uart.3: ttySAC3 at MMIO 0x13830000 (irq = 28) is a S3C6400/10
[    2.006654] brd: module loaded
[    2.006716] fsynccontrol_init misc_register(fsynccontrol)
[    2.010046] ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver
[    2.016169] s5p-ehci s5p-ehci: S5P EHCI Host Controller
[    2.021182] s5p-ehci s5p-ehci: new USB bus registered, assigned bus number 1
[    2.028306] s5p-ehci s5p-ehci: irq 134, io mem 0x12580000
[    2.040040] s5p-ehci s5p-ehci: USB 0.0 started, EHCI 1.00
[    2.040151] usb usb1: New USB device found, idVendor=1d6b, idProduct=0002
[    2.046580] usb usb1: New USB device strings: Mfr=3, Product=2, SerialNumber=1
[    2.053776] usb usb1: Product: S5P EHCI Host Controller
[    2.058976] usb usb1: Manufacturer: Linux 3.0.68 ehci_hcd
[    2.064352] usb usb1: SerialNumber: s5p-ehci
[    2.069092] hub 1-0:1.0: USB hub found
[    2.072343] hub 1-0:1.0: 3 ports detected
[    2.076683] ohci_hcd: USB 1.1 'Open' Host Controller (OHCI) Driver
[    2.082541] s5p-ohci s5p-ohci: Already power on PHY
[    2.087340] s5p-ohci s5p-ohci: s5p OHCI
[    2.091164] s5p-ohci s5p-ohci: new USB bus registered, assigned bus number 2
[    2.098194] s5p-ohci s5p-ohci: irq 134, io mem 0x12590000
[    2.159060] usb usb2: New USB device found, idVendor=1d6b, idProduct=0001
[    2.160218] usb usb2: New USB device strings: Mfr=3, Product=2, SerialNumber=1
[    2.167415] usb usb2: Product: s5p OHCI
[    2.171226] usb usb2: Manufacturer: Linux 3.0.68 ohci_hcd
[    2.176610] usb usb2: SerialNumber: s5p-ohci
[    2.181337] hub 2-0:1.0: USB hub found
[    2.184580] hub 2-0:1.0: 3 ports detected
[    2.189046] usbcore: registered new interface driver usblcd
[    2.215363] usb3503_hw_init : read val = 0x32
[    2.348962] usb3503_hw_init : read val = 0xfffffffa
[    2.460373] s3c-udc : S3C HS USB OTG Device Driver,(c) 2008-2009 Samsung Electronics
[    2.460380] s3c-udc : version 15 March 2009
[    2.466790] odroid_keypad_init
[    2.470079] input: odroid-keypad as /devices/virtual/input/input0
[    2.475770] odroid_keypad_open
[    2.478990] --------------------------------------------------------
[    2.485136] odroid-keypad driver initialized!! Ver 1.0
[    2.490243] --------------------------------------------------------
[    2.496578] platform_driver_register 0 
[    2.500524] usbcore: registered new interface driver xpad
[    2.506329] rtc-mcp7940n 1-006f: chip found, driver version 0.1
[    2.512913] using rtc device, rtc-mcp7940n, for alarms
[    2.516624] rtc-mcp7940n 1-006f: rtc core: registered rtc-mcp7940n as rtc0
[    2.523750] i2c /dev entries driver
[    2.527984] Linux media interface: v0.10
[    2.531342] lirc_dev: IR Remote Control driver registered, major 252 
[    2.537428] IR NEC protocol handler initialized
[    2.541933] IR RC5(x) protocol handler initialized
[    2.545047] usb 1-2: new high speed USB device number 2 using s5p-ehci
[    2.553226] IR RC6 protocol handler initialized
[    2.557718] IR JVC protocol handler initialized
[    2.562229] IR Sony protocol handler initialized
[    2.566828] IR RC5 (streamzap) protocol handler initialized
[    2.572374] IR LIRC bridge handler initialized
[    2.576796] Linux video capture interface: v2.00
[    2.581703] exynos-mdev: Media65535[0xeb26c000] was registered successfully
[    2.588446] hdmiphy init start
[    2.591611] i2c-core: driver [exynos_hdcp] using legacy suspend method
[    2.597875] i2c-core: driver [exynos_hdcp] using legacy resume method
[    2.604295] Samsung HDMI output driver, (c) 2010-2011 Samsung Electronics Co., Ltd.
[    2.612144] s5p-hdmi exynos4-hdmi: hdmiphy i2c bus number = 8
[    2.622351] hdmiphy_probe start
[    2.622404] s5p-hdmiphy 8-0038: probe successful
[    2.680345] usb 1-2: New USB device found, idVendor=0424, idProduct=3503
[    2.681422] usb 1-2: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[    2.689142] hub 1-2:1.0: USB hub found
[    2.692344] hub 1-2:1.0: 3 ports detected
[    2.735120] s5p-hdmi exynos4-hdmi: probe sucessful
[    2.735307] Samsung TV Mixer driver, (c) 2010-2011 Samsung Electronics Co., Ltd.
[    2.747564] s5p-mixer s5p-mixer: probe start
[    2.747720] s5p-mixer s5p-mixer: resources acquired
[    2.751072] s5p-mixer s5p-mixer: added output 'S5P HDMI connector' from module 's5p-hdmi'
[    2.759448] s5p-mixer s5p-mixer: registered layer mxr0_video0 as /dev/video20
[    2.766523] fb5: registered frame buffer emulation for /dev/video20
[    2.772730] s5p-mixer s5p-mixer: registered layer mxr0_graph0 as /dev/video16
[    2.779856] fb6: registered frame buffer emulation for /dev/video16
[    2.786092] s5p-mixer s5p-mixer: registered layer mxr0_graph1 as /dev/video17
[    2.793217] fb7: registered frame buffer emulation for /dev/video17
[    2.799285] s5p-mixer s5p-mixer: mixer0 create links
[    2.804229] s5p-mixer s5p-mixer: mixer links are created successfully
[    2.810646] s5p-mixer s5p-mixer: probe successful
[    2.815480] samsung-fake-battery samsung-fake-battery: samsung_fake_bat_probe
[    2.823090] S3C2410 Watchdog Timer, (c) 2004 Simtec Electronics
[    2.828579] s3c2410-wdt s3c2410-wdt: watchdog inactive, reset disabled, irq enabled
[    2.836678] device-mapper: uevent: version 1.0.3
[    2.840943] device-mapper: ioctl: 4.20.0-ioctl (2011-02-02) initialised: dm-devel@redhat.com
[    2.849011] Bluetooth: Generic Bluetooth USB driver ver 0.6
[    2.854653] usbcore: registered new interface driver btusb
[    2.860391] cpuidle: using governor ladder
[    2.864858] cpuidle: using governor menu
[    2.868168] dw_mmc dw_mmc: Using internal DMA controller.
[    2.873381] mmc0: no vmmc regulator found
[    2.877532] dw_mmc dw_mmc: Version ID is 240a
[    2.881680] dw_mmc dw_mmc: DW MMC controller at irq 141, 32 bit host data width, 128 deep fifo
[    2.890434] sdhci: Secure Digital Host Controller Interface driver
[    2.896425] sdhci: Copyright(c) Pierre Ossman
[    2.900824] s3c-sdhci s3c-sdhci.2: clock source 2: sclk_mmc (440000000 Hz)
[    2.907631] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 400000Hz, actual 400000HZ div = 125)
[    2.907646] mmc1: no vmmc regulator found
[    2.907806] Registered led device: mmc1::
[    2.908008] mmc1: SDHCI controller on samsung-hsmmc [s3c-sdhci.2] using ADMA
[    2.908067] s3c-sdhci s3c-sdhci.3: clock source 2: sclk_mmc (440000000 Hz)
[    2.908101] mmc2: no vmmc regulator found
[    2.908240] Registered led device: mmc2::
[    2.908407] mmc2: SDHCI controller on samsung-hsmmc [s3c-sdhci.3] using ADMA
[    2.908927] zram: num_devices not specified. Using default: 1
[    2.908934] zram: Creating 1 devices ...
[    2.910171] wm8960 i2c probe
[    2.910742] Samsung Audio Subsystem Driver, (c) 2011 Samsung Electronics
[    2.910802] audss_init: RCLK SRC[busclk]
[    2.911233] wm8960-codec 1-001a: No platform data supplied
[    2.990120] usb 1-2.3: new high speed USB device number 3 using s5p-ehci
[    3.021664] asoc: wm8960-hifi <-> samsung-i2s.0 mapping ok
[    3.023546] asoc: wm8960-hifi <-> samsung-i2s.0 mapping ok
[    3.027010] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 300000Hz, actual 299401HZ div = 167)
[    3.027954] ALSA device list:
[    3.027960]   #0: Ctis_wm8960
[    3.028045] GACT probability on
[    3.028534] TCP cubic registered
[    3.029363] NET: Registered protocol family 10
[    3.030842] Mobile IPv6
[    3.030870] ip6_tables: (C) 2000-2006 Netfilter Core Team
[    3.030913] IPv6 over IPv4 tunneling driver
[    3.033800] NET: Registered protocol family 17
[    3.033824] NET: Registered protocol family 15
[    3.074143] Bluetooth: RFCOMM TTY layer initialized
[    3.078960] Bluetooth: RFCOMM socket layer initialized
[    3.084104] Bluetooth: RFCOMM ver 1.11
[    3.087805] Bluetooth: BNEP (Ethernet Emulation) ver 1.3
[    3.093084] Bluetooth: BNEP filters: protocol multicast
[    3.098296] Bluetooth: HIDP (Human Interface Emulation) ver 1.2
[    3.104349] Registering the dns_resolver key type
[    3.108905] EXYNOS4X12: Adaptive Support Voltage init
[    3.113913] EXYNOS4X12(SG):  ORIG : 3 MOD : 0 RESULT : 3
[    3.119200] VFP support v0.3: 
[    3.119210] usb 1-2.3: New USB device found, idVendor=0424, idProduct=9512
[    3.119220] usb 1-2.3: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[    3.136396] implementor 41 architecture 3 part 30 variant 9 rev 4
[    3.136560] hub 1-2.3:1.0: USB hub found
[    3.146343] hub 1-2.3:1.0: 3 ports detected
[    3.146351] ThumbEE CPU extension supported.
[    3.146367] Registering SWP/SWPB emulation handler
[    3.146435] DVFS : VDD_ARM Voltage table set with 3 Group
[    3.146598] cpufreq governor is changed to performance
[    3.147554] exynos4_integrated_dvfs_hotplug_init, max(1200000),min(200000)
[    3.147606] TMU: Memory Allocation Sucessful
[    3.147611] TMU: Platform data set
[    3.147615] TMU: Copied the Dev access Information 
[    3.147631] TMU: IRQ Granted!
[    3.147635] TMU: IO Resource alloced on Memory
[    3.147640] TMU: Memory area resersed
[    3.147664] TMU: IO Memory Remapped
[    3.147679] TMU: Created Sysfs
[    3.180034] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 200000Hz, actual 200000HZ div = 250)
[    3.211468] TMU: Workqueue Created
[    3.214757] TMU: Work Created
[    3.217723] ** temperature set value **
[    3.217726] Throttling stop_temp  = 82  start_temp     = 85
[    3.217730] Waring stop_temp      = 102 start_tmep     = 105
[    3.217734] Tripping temp         = 110
[    3.217737] Hw_tripping temp      = 113
[    3.217739] Mem throttle stop_temp= 80, start_temp     = 85
[    3.217743] Trhottling freq = 800000   Warning freq = 200000
[    3.251566] TC_voltage stop_temp = 13  Start_temp = 10
[    3.256648] TMU: Printed Parameters
[    3.260116] @@@ get_refresh_interval = 0x2e
[    3.264268] @@@ get_refresh_interval = 0x5d
[    3.268444] exynos_tmu_init: cpufreq_level[12], busfreq_value[0]
[    3.275436] Tmu Initialization is sucessful...!
[    3.279423] registered taskstats version 1
[    3.280034] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 196079Hz, actual 196078HZ div = 255)
[    3.292937] regulator_init_complete: BUCK4 vdd_g3d: incomplete constraints, leaving on
[    3.301556] rtc-mcp7940n 1-006f: setting system clock to 2001-01-01 04:14:41 UTC (978322481)
[    3.309112] Freeing init memory: 208K
[    3.368814] udevd[716]: starting version 175
[    3.370186] mmc1: cmd 52 command timeout error
[    3.371986] mmc1: cmd 52 command timeout error
[    3.379633] mmc1: cmd 5 command timeout error
[    3.380746] mmc1: cmd 5 command timeout error
[    3.385073] mmc1: cmd 5 command timeout error
[    3.389398] mmc1: cmd 5 command timeout error
[    3.433277] mmc1: new high speed SDXC card at address aaaa
[    3.433781] mmcblk0: mmc1:aaaa SD64G 59.4 GiB 
[    3.438864]  mmcblk0: p1 p2 p3
[    3.463184] Btrfs loaded
[    3.500075] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 400000Hz, actual 400000HZ div = 125)
[    3.545349] usb 1-2.3.1: new high speed USB device number 4 using s5p-ehci
[    3.555205] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 300000Hz, actual 299401HZ div = 167)
[    3.615057] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 200000Hz, actual 200000HZ div = 250)
[    3.650602] usb 1-2.3.1: New USB device found, idVendor=0424, idProduct=ec00
[    3.652051] usb 1-2.3.1: New USB device strings: Mfr=1, Product=0, SerialNumber=0
[    3.659493] usb 1-2.3.1: Manufacturer: SMSC
[    3.695120] mmc_host mmc0: Bus speed (slot 0) = 100000000Hz (slot req 196079Hz, actual 196078HZ div = 255)
[    3.724766] EXT4-fs (mmcblk0p2): mounted filesystem without journal. Opts: (null)
[    3.750151] usb 1-2.3.3: new full speed USB device number 5 using s5p-ehci
[    3.860344] usb 1-2.3.3: New USB device found, idVendor=09da, idProduct=0025
[    3.861751] usb 1-2.3.3: New USB device strings: Mfr=2, Product=1, SerialNumber=0
[    3.869220] usb 1-2.3.3: Product: A4tech 2.4G Wireless Device
[    3.874957] usb 1-2.3.3: Manufacturer: HS6209
[    4.671044] init: ureadahead main process (834) terminated with status 5
[    4.926605] init: mounted-proc main process (843) terminated with status 1
[    5.341172] udevd[924]: starting version 175
[    5.529487] EXT4-fs (mmcblk0p2): re-mounted. Opts: errors=remount-ro
[    5.741013] EXT4-fs (mmcblk0p3): mounted filesystem with ordered data mode. Opts: (null)
[    6.008470] input: HS6209 A4tech 2.4G Wireless Device as /devices/platform/s5p-ehci/usb1/1-2/1-2.3/1-2.3.3/1-2.3.3:1.0/input/input1
[    6.009048] generic-usb 0003:09DA:0025.0001: input: USB HID v1.11 Keyboard [HS6209 A4tech 2.4G Wireless Device] on usb-s5p-ehci-2.3.3/input0
[    6.015139] input: HS6209 A4tech 2.4G Wireless Device as /devices/platform/s5p-ehci/usb1/1-2/1-2.3/1-2.3.3/1-2.3.3:1.1/input/input2
[    6.016772] generic-usb 0003:09DA:0025.0002: input,hiddev0: USB HID v1.11 Mouse [HS6209 A4tech 2.4G Wireless Device] on usb-s5p-ehci-2.3.3/input1
[    6.016843] usbcore: registered new interface driver usbhid
[    6.016850] usbhid: USB HID core driver
[    6.096560] Installing knfsd (copyright (C) 1996 okir@monad.swb.de).
[    6.166314] init: gator-daemon main process (1188) terminated with status 1
[    6.196027] smsc95xx v1.0.4
[    6.250870] smsc95xx 1-2.3.1:1.0: eth0: register 'smsc95xx' at usb-s5p-ehci-2.3.1, smsc95xx USB 2.0 Ethernet, 00:25:ff:fe:44:45
[    6.250959] usbcore: registered new interface driver smsc95xx
[    6.515825] init: idmapd main process (1267) terminated with status 1
[    6.515899] init: idmapd main process ended, respawning
[    6.664303] init: idmapd main process (1299) terminated with status 1
[    6.664373] init: idmapd main process ended, respawning
[    6.771553] init: failsafe main process (1262) killed by TERM signal
[    6.797921] init: idmapd main process (1330) terminated with status 1
[    6.798028] init: idmapd main process ended, respawning
[    6.920980] init: idmapd main process (1370) terminated with status 1
[    6.921055] init: idmapd main process ended, respawning
[    6.971058] init: idmapd main process (1383) terminated with status 1
[    6.971128] init: idmapd main process ended, respawning
[    7.062794] init: idmapd main process (1400) terminated with status 1
[    7.062863] init: idmapd main process ended, respawning
[    7.663264] init: idmapd main process (1420) terminated with status 1
[    7.663343] init: idmapd main process ended, respawning
[    8.353273] init: hybrid-gfx main process (1483) terminated with status 1
[    8.383146] init: idmapd main process (1509) terminated with status 1
[    8.383231] init: idmapd main process ended, respawning
[    8.486749] init: idmapd main process (1547) terminated with status 1
[    8.486842] init: idmapd main process ended, respawning
[    8.620949] init: idmapd main process (1575) terminated with status 1
[    8.621031] init: idmapd main process ended, respawning
[    8.736403] init: idmapd main process (1611) terminated with status 1
[    8.736515] init: idmapd respawning too fast, stopped
[    8.919407] init: plymouth-stop pre-start process (1662) terminated with status 1
[    8.929759] init: tty1 main process (1663) killed by TERM signal
[    9.295887] vb2_common_vm_open: ea34ec94, refcount: 1, vma: 406f2000-40ae7000
[    9.295898] vb2_cma_phys_mmap_pfn_range: mapped paddr 0x6d022000 at 0x406f2000, size 4149248
[    9.364694] ADDRCONF(NETDEV_UP): eth0: link is not ready
[    9.618128] unplugged
[    9.618188] s5p_hpd_kobject_uevent: sent uevent HDMI_STATE=offline
[   10.953123] ADDRCONF(NETDEV_CHANGE): eth0: link becomes ready
[   10.954228] smsc95xx 1-2.3.1:1.0: eth0: link up, 100Mbps, full-duplex, lpa 0x45E1
[   12.592283] init: anacron main process (1489) killed by TERM signal
[   12.693325] fuse init (API version 7.16)
[   14.372809] warning: process `colord' used the deprecated sysctl system call with 8.1.2.
[   25.450500] init: origen-bluetooth pre-start process (1478) terminated with status 1
[   68.802925] CPU1: shutdown
[   68.804201] CPU2: shutdown
[   68.812723] CPU3: shutdown
[   74.031445] CPU3: Booted secondary processor

@@@ modules @@@
Module                  Size  Used by
cpufreq_ondemand        6655  1 
fuse                   64741  2 
smsc95xx               12893  0 
usbnet                 15749  1 smsc95xx
nfsd                  252141  0 
exportfs                3844  1 nfsd
usbhid                 35768  0 
btrfs                 574554  0 

@@@ proc-devices @@@
Character devices:
  1 mem
  4 /dev/vc/0
  4 tty
  4 ttyS
  5 /dev/tty
  5 /dev/console
  5 /dev/ptmx
  7 vcs
 10 misc
 13 input
 21 sg
 29 fb
 81 video4linux
 89 i2c
116 alsa
128 ptm
136 pts
180 usb
189 usb_device
204 ttySAC
216 rfcomm
252 BaseRemoteCtl
253 media
254 rtc

Block devices:
  1 ramdisk
259 blkext
  8 sd
 65 sd
 66 sd
 67 sd
 68 sd
 69 sd
 70 sd
 71 sd
128 sd
129 sd
130 sd
131 sd
132 sd
133 sd
134 sd
135 sd
179 mmc
253 zram
254 device-mapper

@@@ iomem @@@
03830000-038300ff : samsung-i2s.0
  03830000-038300ff : samsung-i2s
10060000-10060fff : s3c2410-wdt
  10060000-10060fff : s3c2410-wdt
10070000-100700ff : s3c64xx-rtc
100b0000-100b0fff : s5p-tvout-cec
100c0000-100cfffe : tmu
  100c0000-100cfffe : tmu
10a40000-10a40fff : s5p-sysmmu.15
11a20000-11a20fff : s5p-sysmmu.1
11a30000-11a30fff : s5p-sysmmu.2
11a40000-11a40fff : s5p-sysmmu.3
11a50000-11a50fff : s5p-sysmmu.4
11a60000-11a60fff : s5p-sysmmu.5
11c00000-11c07fff : s3cfb.0
  11c00000-11c07fff : s3cfb
12480000-12480fff : s3c-usbgadget
  12480000-12480fff : s3c-usbgadget
12530000-12530fff : s3c-sdhci.2
  12530000-12530fff : mmc1
12540000-12540fff : s3c-sdhci.3
  12540000-12540fff : mmc2
12550000-12550fff : dw_mmc
12580000-125800ff : s5p-ehci
12590000-125900ff : s5p-ohci
12680000-12681000 : s3c-pl330.1
  12680000-12681000 : s3c-pl330
12690000-12691000 : s3c-pl330.2
  12690000-12691000 : s3c-pl330
126c0000-126c1fff : exynos4412-adc
12850000-12851000 : s3c-pl330.0
  12850000-12851000 : s3c-pl330
12c00000-12c0ffff : vp
12c10000-12c1ffff : mxr
12c20000-12c2ffff : s5p-sdo
12d00000-12dfffff : exynos4-hdmi
12e20000-12e20fff : s5p-sysmmu.12
  12e20000-12e20fff : s5p-sysmmu.12
13620000-13620fff : s5p-sysmmu.13
13630000-13630fff : s5p-sysmmu.14
13800000-138000ff : s5pv210-uart.0
  13800000-138000ff : s5pv210-uart
13810000-138100ff : s5pv210-uart.1
  13810000-138100ff : s5pv210-uart
13820000-138200ff : s5pv210-uart.2
  13820000-138200ff : s5pv210-uart
13830000-138300ff : s5pv210-uart.3
  13830000-138300ff : s5pv210-uart
13860000-13860fff : s3c2440-i2c.0
  13860000-13860fff : s3c2440-i2c
13870000-13870fff : s3c2440-i2c.1
  13870000-13870fff : s3c2440-i2c
138a0000-138a0fff : s3c2440-i2c.4
  138a0000-138a0fff : s3c2440-i2c
138b0000-138b0fff : s3c2440-i2c.5
  138b0000-138b0fff : s3c2440-i2c
138e0000-138e0fff : s3c2440-hdmiphy-i2c
  138e0000-138e0fff : s3c2440-hdmiphy-i2c
40000000-7fefffff : System RAM
  4003c000-405d8fff : Kernel text
  405da000-40664c1b : Kernel data

@@@ devicetree @@@
== model/compatible ==


== tree ==

@@@ gpio @@@
== /sys/class/gpio ==
== debugfs gpio (claimed) ==
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

GPIOs 65-72, GPF2:

GPIOs 74-79, GPF3:

GPIOs 81-87, GPK0:

GPIOs 89-95, GPK1:

GPIOs 97-103, GPK2:

GPIOs 105-111, GPK3:

GPIOs 113-120, GPL0:

GPIOs 122-124, GPL1:

GPIOs 126-133, GPL2:

GPIOs 135-140, GPY0:

GPIOs 142-145, GPY1:

GPIOs 147-152, GPY2:

GPIOs 154-161, GPY3:

GPIOs 163-170, GPY4:

GPIOs 172-179, GPY5:

GPIOs 181-188, GPY6:

GPIOs 190-197, GPX0:

GPIOs 199-206, GPX1:
 gpio-202 (KEY POWER           ) in  hi

GPIOs 208-215, GPX2:

GPIOs 217-224, GPX3:
 gpio-223 (hdmi-cec            ) in  hi
 gpio-224 (hpd-plug            ) in  lo

GPIOs 226-232, GPZ:

GPIOs 234-241, GPJ0:

GPIOs 243-247, GPJ1:

GPIOs 249-256, GPM0:

GPIOs 258-264, GPM1:

GPIOs 266-270, GPM2:

GPIOs 272-279, GPM3:

GPIOs 281-288, GPM4:

GPIOs 290-297, GPV0:

GPIOs 299-306, GPV1:

GPIOs 308-315, GPV2:

GPIOs 317-324, GPV3:

GPIOs 326-327, GPV4:
== dt gpio/key/led/pwm nodes ==

@@@ pinctrl @@@
== debugfs pinctrl ==
(absent = no pinctrl in this kernel)

@@@ i2c @@@
== devices ==
0-0006
0-0008
0-0009
1-0008
1-001a
1-006f
8-0038
i2c-0
i2c-1
i2c-4
i2c-5
i2c-8
== /dev/i2c ==
/dev/i2c-0
/dev/i2c-1
/dev/i2c-4
/dev/i2c-5
/dev/i2c-8
== adapters ==
s3c2410-i2c
s3c2410-i2c
s3c2410-i2c
s3c2410-i2c
s3c2410-i2c

@@@ spi @@@
== /dev/spi ==
== cfg ==
# CONFIG_INLINE_SPIN_TRYLOCK is not set
# CONFIG_INLINE_SPIN_TRYLOCK_BH is not set
# CONFIG_INLINE_SPIN_LOCK is not set
# CONFIG_INLINE_SPIN_LOCK_BH is not set
# CONFIG_INLINE_SPIN_LOCK_IRQ is not set
# CONFIG_INLINE_SPIN_LOCK_IRQSAVE is not set
CONFIG_INLINE_SPIN_UNLOCK=y
# CONFIG_INLINE_SPIN_UNLOCK_BH is not set
CONFIG_INLINE_SPIN_UNLOCK_IRQ=y
# CONFIG_INLINE_SPIN_UNLOCK_IRQRESTORE is not set
# CONFIG_MUTEX_SPIN_ON_OWNER is not set
# CONFIG_EEPROM_93CX6 is not set
# CONFIG_SCSI_SPI_ATTRS is not set
# CONFIG_SPI is not set
# SPI GPIO expanders:
CONFIG_SND_SOC_I2C_AND_SPI=y
# SPI RTC drivers
# CONFIG_DEBUG_SPINLOCK is not set
# CONFIG_DEBUG_SPINLOCK_SLEEP is not set

@@@ uart @@@
== nodes ==
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
== driver ==

@@@ usb @@@
== lsusb ==
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 002 Device 001: ID 1d6b:0001 Linux Foundation 1.1 root hub
Bus 001 Device 002: ID 0424:3503 Standard Microsystems Corp. 
Bus 001 Device 003: ID 0424:9512 Standard Microsystems Corp. 
Bus 001 Device 004: ID 0424:ec00 Standard Microsystems Corp. 
Bus 001 Device 005: ID 09da:0025 A4 Tech Co., Ltd 
== sysfs ==
1-0:1.0
1-2
1-2.3
1-2.3.1
1-2.3.1:1.0
1-2.3.3
1-2.3.3:1.0
1-2.3.3:1.1
1-2.3:1.0
1-2:1.0
2-0:1.0
usb1
usb2
== usb gadget cfg ==
# CONFIG_SERIAL_NONSTANDARD is not set
CONFIG_SERIAL_8250=y
# CONFIG_SERIAL_8250_CONSOLE is not set
CONFIG_SERIAL_8250_NR_UARTS=4
CONFIG_SERIAL_8250_RUNTIME_UARTS=4
# CONFIG_SERIAL_8250_EXTENDED is not set
CONFIG_SERIAL_SAMSUNG=y
CONFIG_SERIAL_SAMSUNG_UARTS_4=y
CONFIG_SERIAL_SAMSUNG_UARTS=4
CONFIG_SERIAL_SAMSUNG_CONSOLE=y
CONFIG_SERIAL_S5PV210=y
CONFIG_SERIAL_CORE=y
CONFIG_SERIAL_CORE_CONSOLE=y
# CONFIG_SERIAL_TIMBERDALE is not set
# CONFIG_SERIAL_ALTERA_JTAGUART is not set
# CONFIG_SERIAL_ALTERA_UART is not set
# CONFIG_SERIAL_XILINX_PS_UART is not set
CONFIG_USB_GADGET=y
# CONFIG_USB_GADGET_DEBUG is not set
# CONFIG_USB_GADGET_DEBUG_FILES is not set
# CONFIG_USB_GADGET_DEBUG_FS is not set
CONFIG_USB_GADGET_VBUS_DRAW=2
CONFIG_USB_GADGET_SELECTED=y
# CONFIG_USB_GADGET_FUSB300 is not set
# CONFIG_USB_GADGET_R8A66597 is not set
CONFIG_USB_GADGET_S3C_OTGD=y
# CONFIG_USB_GADGET_PXA_U2O is not set
# CONFIG_USB_GADGET_M66592 is not set
# CONFIG_USB_GADGET_DUMMY_HCD is not set
CONFIG_USB_GADGET_DUALSPEED=y
# CONFIG_USB_ZERO is not set
# CONFIG_USB_ETH is not set
# CONFIG_USB_GADGETFS is not set
# CONFIG_USB_G_SERIAL is not set

@@@ audio @@@
== cards ==
 0 [Ctiswm8960     ]: Ctis_wm8960 - Ctis_wm8960
                      Ctis_wm8960
== pcm ==
00-00: Playback wm8960-hifi-0 :  : playback 1 : capture 1
00-01: Capture wm8960-hifi-1 :  : playback 1 : capture 1
== aplay -l ==
**** List of PLAYBACK Hardware Devices ****
card 0: Ctiswm8960 [Ctis_wm8960], device 0: Playback wm8960-hifi-0 []
  Subdevices: 1/1
  Subdevice #0: subdevice #0
card 0: Ctiswm8960 [Ctis_wm8960], device 1: Capture wm8960-hifi-1 []
  Subdevices: 1/1
  Subdevice #0: subdevice #0
== amixer controls ==
Simple mixer control 'Headphone',0
Simple mixer control 'Headphone Playback ZC',0
Simple mixer control 'Speaker',0
Simple mixer control 'Speaker AC',0
Simple mixer control 'Speaker DC',0
Simple mixer control 'Speaker Playback ZC',0
Simple mixer control 'PCM Playback -6dB',0
Simple mixer control 'Mono Output Mixer Left',0
Simple mixer control 'Mono Output Mixer Right',0
Simple mixer control 'Playback',0
Simple mixer control 'Capture',0
Simple mixer control '3D',0
Simple mixer control '3D Filter Lower Cut-Off',0
Simple mixer control '3D Filter Upper Cut-Off',0
Simple mixer control 'ADC High Pass Filter',0
Simple mixer control 'ADC PCM',0
Simple mixer control 'ADC Polarity',0
Simple mixer control 'ALC Attack',0
Simple mixer control 'ALC Decay',0
Simple mixer control 'ALC Function',0
Simple mixer control 'ALC Hold Time',0
Simple mixer control 'ALC Max Gain',0
Simple mixer control 'ALC Min Gain',0
Simple mixer control 'ALC Mode',0
Simple mixer control 'ALC Target',0
Simple mixer control 'DAC Deemphasis',0
Simple mixer control 'DAC Polarity',0
Simple mixer control 'Left Boost Mixer LINPUT1',0
Simple mixer control 'Left Boost Mixer LINPUT2',0
Simple mixer control 'Left Boost Mixer LINPUT3',0
Simple mixer control 'Left Input Mixer Boost',0
Simple mixer control 'Left Output Mixer Boost Bypass',0
Simple mixer control 'Left Output Mixer LINPUT3',0
Simple mixer control 'Left Output Mixer PCM',0
Simple mixer control 'Noise Gate',0
Simple mixer control 'Noise Gate Threshold',0
Simple mixer control 'Right Boost Mixer RINPUT1',0
Simple mixer control 'Right Boost Mixer RINPUT2',0
Simple mixer control 'Right Boost Mixer RINPUT3',0
Simple mixer control 'Right Input Mixer Boost',0
Simple mixer control 'Right Output Mixer Boost Bypass',0
Simple mixer control 'Right Output Mixer PCM',0
Simple mixer control 'Right Output Mixer RINPUT3',0

@@@ network @@@
== addr ==
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN \    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
1: lo    inet 127.0.0.1/8 scope host lo
1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever
2: sit0: <NOARP> mtu 1480 qdisc noop state DOWN \    link/sit 0.0.0.0 brd 0.0.0.0
3: ip6tnl0: <NOARP> mtu 1452 qdisc noop state DOWN \    link/tunnel6 :: brd ::
4: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1488 qdisc pfifo_fast state UP qlen 1000\    link/ether 00:25:ff:fe:44:45 brd ff:ff:ff:ff:ff:ff
4: eth0    inet 192.168.100.127/24 brd 192.168.100.255 scope global eth0
4: eth0    inet6 fe80::225:ffff:fefe:4445/64 scope link \       valid_lft forever preferred_lft forever
== net ==
eth0
ip6tnl0
lo
sit0
== ethtool -i ==
driver: smsc95xx
version: 22-Aug-2005
firmware-version: smsc95xx USB 2.0 Ethernet
bus-info: usb-s5p-ehci-2.3.1
supports-statistics: no
supports-test: no
supports-eeprom-access: yes
supports-register-dump: no
== ethtool ==
Settings for eth0:
	Supported ports: [ TP MII ]
	Supported link modes:   10baseT/Half 10baseT/Full 
	                        100baseT/Half 100baseT/Full 
	Supported pause frame use: No
	Supports auto-negotiation: Yes
	Advertised link modes:  10baseT/Half 10baseT/Full 
	                        100baseT/Half 100baseT/Full 
	Advertised pause frame use: Symmetric Receive-only
	Advertised auto-negotiation: Yes
	Link partner advertised link modes:  10baseT/Half 10baseT/Full 
	                                     100baseT/Half 100baseT/Full 
	Link partner advertised pause frame use: Symmetric
	Link partner advertised auto-negotiation: Yes
	Speed: 100Mb/s
	Duplex: Full
== eeprom dump (93LC66A #1) ==
Offset		Values
------		------
0x0000		a5 00 25 ff fe 44 45 01 04 05 09 04 0a 1d 00 00 
0x0010		00 00 00 00 00 00 12 22 12 2b 12 34 12 3d 00 00 
0x0020		24 04 12 95 00 01 9b 18 00 02 30 30 01 00 01 00 
0x0030		32 00 00 00 00 00 21 03 00 01 0a 03 53 00 4d 00 
0x0040		53 00 43 00 12 01 00 02 ff 00 01 40 24 04 00 ec 
0x0050		00 01 01 00 00 01 09 02 27 00 01 01 00 e0 01 09 
0x0060		04 00 00 03 ff 00 ff 00 12 01 00 02 ff 00 ff 40 
0x0070		24 04 00 ec 00 01 01 00 00 01 09 02 27 00 01 01 
0x0080		00 e0 01 09 04 00 00 03 ff 00 ff 00 ff ff ff ff 
0x0090		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x00a0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x00b0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x00c0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x00d0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x00e0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x00f0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0100		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0110		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0120		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0130		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0140		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0150		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0160		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0170		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0180		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x0190		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x01a0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x01b0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x01c0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x01d0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x01e0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 
0x01f0		ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff 

@@@ rtc @@@
== /proc/driver/rtc ==
rtc_time	: 04:15:54
rtc_date	: 2001-01-01
24hr		: yes
== nodes ==
/dev/rtc0
== hwclock ==
Mon Jan  1 13:15:55 2001  -0.388075 seconds
== class ==
rtc0

@@@ input-buttons @@@
I: Bus=0019 Vendor=16b4 Product=0701 Version=0001
N: Name="odroid-keypad"
P: Phys=odroid-keypad/input0
S: Sysfs=/devices/virtual/input/input0
U: Uniq=
H: Handlers=kbd event0 
B: PROP=0
B: EV=3
B: KEY=100000 0 0 0

I: Bus=0003 Vendor=09da Product=0025 Version=0111
N: Name="HS6209 A4tech 2.4G Wireless Device"
P: Phys=usb-s5p-ehci-2.3.3/input0
S: Sysfs=/devices/platform/s5p-ehci/usb1/1-2/1-2.3/1-2.3.3/1-2.3.3:1.0/input/input1
U: Uniq=
H: Handlers=sysrq kbd event1 
B: PROP=0
B: EV=120013
B: KEY=10000 7 ff9f207a c14057ff febeffdf ffefffff ffffffff fffffffe
B: MSC=10
B: LED=1f

I: Bus=0003 Vendor=09da Product=0025 Version=0111
N: Name="HS6209 A4tech 2.4G Wireless Device"
P: Phys=usb-s5p-ehci-2.3.3/input1
S: Sysfs=/devices/platform/s5p-ehci/usb1/1-2/1-2.3/1-2.3.3/1-2.3.3:1.1/input/input2
U: Uniq=
H: Handlers=kbd event2 
B: PROP=0
B: EV=1f
B: KEY=4837fff 72ff32d bf544446 0 0 ff0001 20f90 8b17c000 677bfa d941dfed 9ed680 4400 0 10000002
B: REL=1c3
B: ABS=7f01 0
B: MSC=10

== nodes ==
by-id
by-path
event0
event1
event2

@@@ video @@@
/dev/fb0
/dev/fb1
/dev/fb2
/dev/fb3
/dev/fb4
/dev/fb5
/dev/fb6
/dev/fb7
/dev/video16
/dev/video17
/dev/video20
== fb ==
0 s3cfb
1 s3cfb
2 s3cfb
3 s3cfb
4 s3cfb
5 
6 
7 

@@@ storage @@@
NAME        MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
mmcblk0     179:0    0  59.5G  0 disk 
├─mmcblk0p1 179:1    0   128M  0 part /media/boot
├─mmcblk0p2 179:2    0   5.4G  0 part /
└─mmcblk0p3 179:3    0    54G  0 part /data

Filesystem      Size  Used Avail Use% Mounted on
/dev/mmcblk0p2  5.3G  3.0G  2.1G  60% /
udev            483M  4.0K  483M   1% /dev
tmpfs           485M  4.0K  485M   1% /tmp
tmpfs           194M  620K  193M   1% /run
none            5.0M     0  5.0M   0% /run/lock
none            485M   24K  484M   1% /run/shm
/dev/mmcblk0p1  127M  7.4M  119M   6% /media/boot
/dev/mmcblk0p3   54G  180M   51G   1% /data

major minor  #blocks  name

 179        0   62367744 mmcblk0
 179        1     131072 mmcblk0p1
 179        2    5633024 mmcblk0p2
 179        3   56601600 mmcblk0p3
== mounts ==
/dev/mmcblk0p2 on / type ext4 (rw,noatime,errors=remount-ro)
none on /sys/kernel/debug type debugfs (rw)
none on /sys/kernel/security type securityfs (rw)
/dev/mmcblk0p1 on /media/boot type vfat (rw,nosuid,nodev,flush,umask=000)
/dev/mmcblk0p3 on /data type ext4 (rw,noatime)
gvfs-fuse-daemon on /root/.gvfs type fuse.gvfs-fuse-daemon (rw,nosuid,nodev)

@@@ thermal-wdt @@@
== thermal zones ==
== temp ==
== cpufreq ==
1200000
== wdt dmesg ==
[    2.823090] S3C2410 Watchdog Timer, (c) 2004 Simtec Electronics
[    2.828579] s3c2410-wdt s3c2410-wdt: watchdog inactive, reset disabled, irq enabled

@@@ kernel-cfg @@@
CONFIG_HAVE_PWM=y
CONFIG_USE_GENERIC_SMP_HELPERS=y
CONFIG_KEYBOARD_GPIO_POLLED=m
# CONFIG_S3C_BOOT_WATCHDOG is not set
# CONFIG_S3C_ADC is not set
CONFIG_SAMSUNG_DEV_PWM=y
CONFIG_S3C24XX_PWM=y
CONFIG_S5P_DEV_I2C_HDMIPHY=y
CONFIG_EXYNOS_THERMAL=y
CONFIG_SMP=y
CONFIG_SMP_ON_UP=y
CONFIG_HIGHMEM=y
CONFIG_CPU_FREQ=y
CONFIG_CPU_FREQ_TABLE=y
CONFIG_CPU_FREQ_STAT=y
# CONFIG_CPU_FREQ_STAT_DETAILS is not set
CONFIG_CPU_FREQ_DEFAULT_GOV_PERFORMANCE=y
# CONFIG_CPU_FREQ_DEFAULT_GOV_POWERSAVE is not set
# CONFIG_CPU_FREQ_DEFAULT_GOV_USERSPACE is not set
# CONFIG_CPU_FREQ_DEFAULT_GOV_ONDEMAND is not set
# CONFIG_CPU_FREQ_DEFAULT_GOV_CONSERVATIVE is not set
# CONFIG_CPU_FREQ_DEFAULT_GOV_INTERACTIVE is not set
# CONFIG_CPU_FREQ_DEFAULT_GOV_ADAPTIVE is not set
CONFIG_CPU_FREQ_GOV_PERFORMANCE=y
CONFIG_CPU_FREQ_GOV_POWERSAVE=m
CONFIG_CPU_FREQ_GOV_USERSPACE=m
CONFIG_CPU_FREQ_GOV_ONDEMAND=m
# CONFIG_CPU_FREQ_GOV_INTERACTIVE is not set
CONFIG_CPU_FREQ_GOV_CONSERVATIVE=m
# CONFIG_CPU_FREQ_GOV_ADAPTIVE is not set
CONFIG_PM_SLEEP_SMP=y
# CONFIG_RFKILL_REGULATOR is not set
# CONFIG_SENSORS_LIS3LV02D is not set
# CONFIG_SENSORS_TSL2550 is not set
# CONFIG_SENSORS_BH1780 is not set
# CONFIG_SENSORS_BH1770 is not set
# CONFIG_SENSORS_APDS990X is not set
# CONFIG_SENSORS_AK8975 is not set
# CONFIG_EEPROM_93CX6 is not set
# CONFIG_SENSORS_LIS3_I2C is not set
# CONFIG_MPU_SENSORS_TIMERIRQ is not set
# CONFIG_INV_SENSORS is not set
# CONFIG_SCSI_SPI_ATTRS is not set
CONFIG_INPUT_KEYBOARD=y
CONFIG_KEYBOARD_ADP5588=m
CONFIG_KEYBOARD_ADP5589=m
CONFIG_KEYBOARD_ATKBD=m
CONFIG_KEYBOARD_QT1070=m
CONFIG_KEYBOARD_QT2160=m
CONFIG_KEYBOARD_LKKBD=m
CONFIG_KEYBOARD_GPIO=m
CONFIG_KEYBOARD_TCA6416=m
CONFIG_KEYBOARD_MATRIX=m
# CONFIG_KEYBOARD_LM8323 is not set
CONFIG_KEYBOARD_MAX7359=m
CONFIG_KEYBOARD_MCS=m
CONFIG_KEYBOARD_MPR121=m
CONFIG_KEYBOARD_NEWTON=m
CONFIG_KEYBOARD_OPENCORES=m
CONFIG_KEYBOARD_STOWAWAY=m
CONFIG_KEYBOARD_SUNKBD=m
CONFIG_KEYBOARD_XTKBD=m
CONFIG_KEYBOARD_ODROID=y
# CONFIG_MOUSE_PS2_TOUCHKIT is not set
CONFIG_MOUSE_APPLETOUCH=m
# CONFIG_INPUT_TOUCHSCREEN is not set
# CONFIG_INPUT_GPIO is not set
# CONFIG_INPUT_PWM_BEEPER is not set
# CONFIG_INPUT_GPIO_ROTARY_ENCODER is not set
CONFIG_SERIAL_S5PV210=y
CONFIG_I2C_S3C2410=y
# CONFIG_GPIO_SYSFS is not set
# CONFIG_THERMAL is not set
CONFIG_WATCHDOG=y
# CONFIG_WATCHDOG_NOWAYOUT is not set
# Watchdog Device Drivers
CONFIG_SOFT_WATCHDOG=m
CONFIG_HAVE_S3C2410_WATCHDOG=y
CONFIG_S3C2410_WATCHDOG=y
# CONFIG_MAX63XX_WATCHDOG is not set
# USB-based Watchdog Cards
# CONFIG_USBPCWATCHDOG is not set
CONFIG_MFD_MAX77686=y
CONFIG_REGULATOR=y
# CONFIG_REGULATOR_DEBUG is not set
# CONFIG_REGULATOR_DUMMY is not set
# CONFIG_REGULATOR_FIXED_VOLTAGE is not set
# CONFIG_REGULATOR_VIRTUAL_CONSUMER is not set
# CONFIG_REGULATOR_USERSPACE_CONSUMER is not set
# CONFIG_REGULATOR_BQ24022 is not set
# CONFIG_REGULATOR_MAX1586 is not set
# CONFIG_REGULATOR_MAX8649 is not set
# CONFIG_REGULATOR_MAX8660 is not set
# CONFIG_REGULATOR_MAX8952 is not set
CONFIG_REGULATOR_MAX77686=y
# CONFIG_REGULATOR_LP3971 is not set
# CONFIG_REGULATOR_LP3972 is not set
# CONFIG_REGULATOR_TPS65023 is not set
# CONFIG_REGULATOR_TPS6507X is not set
# CONFIG_REGULATOR_ISL6271A is not set
# CONFIG_REGULATOR_AD5398 is not set
# Encoders, decoders, sensors and other helper chips
# CONFIG_VIDEO_VP27SMPX is not set
CONFIG_VIDEO_EXYNOS_HDMI=y
CONFIG_VIDEO_EXYNOS_HDMI_AUDIO_I2S=y
# CONFIG_VIDEO_EXYNOS_HDMI_DEBUG is not set
CONFIG_VIDEO_EXYNOS_HDMIPHY=y
# CONFIG_VIDEO_EXYNOS_HDMI_CEC is not set
CONFIG_DRM=m
CONFIG_DRM_MALI=m
CONFIG_BACKLIGHT_PWM=y
# CONFIG_FRAMEBUFFER_CONSOLE is not set
CONFIG_SND_SOC=y
# CONFIG_SND_SOC_CACHE_LZO is not set
CONFIG_SND_SOC_SAMSUNG=y
# CONFIG_SND_SOC_ODROID_MAX98095 is not set
# CONFIG_SND_SOC_ODROID_MAX98090 is not set
CONFIG_SND_SOC_CTIS_WM8960=y
# CONFIG_SND_SOC_SAMSUNG_SMDK_SPDIF is not set
CONFIG_SND_SOC_I2C_AND_SPI=y
# CONFIG_SND_SOC_ALL_CODECS is not set
CONFIG_SND_SOC_WM8960=y
CONFIG_HID_KEYTOUCH=m
CONFIG_HID_MULTITOUCH=m
CONFIG_USB_STORAGE_ONETOUCH=m
CONFIG_USB_GADGET=y
# CONFIG_USB_GADGET_DEBUG is not set
# CONFIG_USB_GADGET_DEBUG_FILES is not set
# CONFIG_USB_GADGET_DEBUG_FS is not set
CONFIG_USB_GADGET_VBUS_DRAW=2
CONFIG_USB_GADGET_SELECTED=y
# CONFIG_USB_GADGET_FUSB300 is not set
# CONFIG_USB_GADGET_R8A66597 is not set
CONFIG_USB_GADGET_S3C_OTGD=y
# CONFIG_USB_GADGET_PXA_U2O is not set
# CONFIG_USB_GADGET_M66592 is not set
# CONFIG_USB_GADGET_DUMMY_HCD is not set
CONFIG_USB_GADGET_DUALSPEED=y
# CONFIG_USB_GADGETFS is not set
CONFIG_MMC_SDHCI=y
# CONFIG_MMC_SDHCI_PLTFM is not set
CONFIG_MMC_SDHCI_S3C=y
CONFIG_MMC_SDHCI_S3C_DMA=y
# CONFIG_LEDS_PWM is not set
# CONFIG_LEDS_REGULATOR is not set
# CONFIG_RTC_DRV_TEST is not set
# CONFIG_RTC_DRV_DS1307 is not set
# CONFIG_RTC_DRV_DS1374 is not set
# CONFIG_RTC_DRV_DS1672 is not set
# CONFIG_RTC_DRV_DS3232 is not set
# CONFIG_RTC_DRV_MAX6900 is not set
# CONFIG_RTC_DRV_MAX77686 is not set
# CONFIG_RTC_DRV_RS5C372 is not set
# CONFIG_RTC_DRV_ISL1208 is not set
# CONFIG_RTC_DRV_ISL12022 is not set
# CONFIG_RTC_DRV_X1205 is not set
# CONFIG_RTC_DRV_PCF8563 is not set
# CONFIG_RTC_DRV_PCF8583 is not set
# CONFIG_RTC_DRV_M41T80 is not set
# CONFIG_RTC_DRV_BQ32K is not set
# CONFIG_RTC_DRV_S35390A is not set
# CONFIG_RTC_DRV_FM3130 is not set
# CONFIG_RTC_DRV_RX8581 is not set
# CONFIG_RTC_DRV_RX8025 is not set
# CONFIG_RTC_DRV_EM3027 is not set
# CONFIG_RTC_DRV_RV3029C2 is not set
# CONFIG_RTC_DRV_CMOS is not set
# CONFIG_RTC_DRV_DS1286 is not set
# CONFIG_RTC_DRV_DS1511 is not set
# CONFIG_RTC_DRV_DS1553 is not set
# CONFIG_RTC_DRV_DS1742 is not set
# CONFIG_RTC_DRV_STK17TA8 is not set
# CONFIG_RTC_DRV_M48T86 is not set
# CONFIG_RTC_DRV_M48T35 is not set
# CONFIG_RTC_DRV_M48T59 is not set
# CONFIG_RTC_DRV_MSM6242 is not set
# CONFIG_RTC_DRV_BQ4802 is not set
# CONFIG_RTC_DRV_RP5C01 is not set
# CONFIG_RTC_DRV_V3020 is not set
CONFIG_RTC_DRV_MCP7940N=y
# CONFIG_RTC_DRV_S3C is not set
# CONFIG_TOUCHSCREEN_CLEARPAD_TM1217 is not set
# CONFIG_TOUCHSCREEN_SYNAPTICS_I2C_RMI4 is not set
# CONFIG_DEBUG_HIGHMEM is not set

@@@ firmware @@@
edgeport
emi26
emi62
keyspan_pda
mts_cdma.fw
mts_edge.fw
mts_gsm.fw
rt2870.bin
ti_3410.fw
ti_5052.fw
whiteheat.fw
whiteheat_loader.fw

@@@ vendor-bin @@@
== /usr/local/bin ==
total 136
drwxr-xr-x 2 root root   4096 May 20  2014 .
drwxr-xr-x 8 root root   4096 May 20  2014 ..
-rwxr-xr-x 1 root root 129760 May 20  2014 CMIMIRDemo
== /usr/local/lib (vendor) ==
-rwxr-xr-x 1 root root   48845 May 20  2014 libcmicolorLib_arm_0.9.0.so
-rwxr-xr-x 1 root root 1085688 May 20  2014 libcmirisLib2_arm_2.0.92.so
-rwxr-xr-x 1 root root   47296 May 20  2014 libemaLib_arm_1.0.1.so
== /opt ==
== find vendor ==
/usr/local/bin/CMIMIRDemo
/usr/local/lib/libcmirisLib2_arm_2.0.92.so
/usr/local/lib/libemaLib_arm_1.0.1.so

@@@ vendor-pkgs @@@
ii  base-files                                  6.5ubuntur6linaro12.11                              Debian base system miscellaneous files
ii  checkbox-qt                                 0.13.10                                             QT4 interface for checkbox
ii  compiz                                      1:0.9.8+bzr3287-0linaro3                            OpenGL window and compositing manager
ii  compiz-core                                 1:0.9.8+bzr3287-0linaro3                            OpenGL window and compositing manager
ii  compiz-gnome                                1:0.9.8+bzr3287-0linaro3                            OpenGL window and compositing manager - GNOME window decorator
ii  compiz-plugins-default                      1:0.9.8+bzr3287-0linaro3                            OpenGL window and compositing manager - default plugins
ii  compiz-plugins-main-default                 1:0.9.8+bzr3287-0linaro3                            transitional dummy package.
ii  flash-kernel                                2.28ubuntu42.2linaro1                               utility to make certain embedded devices bootable
ii  gatortests                                  0.1.20120611-0linaro1                               Gator tests
ii  gir1.2-gst-plugins-base-0.10                0.10.36-1+ti1.6.4.1+1linaro1                        Description: GObject introspection data for the GStreamer Plugins Base library
ii  gsettings-desktop-schemas                   3.4.1-0ubuntu1                                      GSettings deskop-wide schemas
ii  gstreamer0.10-alsa                          0.10.36-1+ti1.6.4.1+1linaro1                        GStreamer plugin for ALSA
ii  gstreamer0.10-gconf                         0.10.31-1ubuntu2+ti1.6.4.1+1linaro1                 GStreamer plugin for getting the sink/source information from GConf
ii  gstreamer0.10-plugins-base                  0.10.36-1+ti1.6.4.1+1linaro1                        GStreamer plugins from the "base" set
ii  gstreamer0.10-plugins-base-apps             0.10.36-1+ti1.6.4.1+1linaro1                        GStreamer helper programs from the "base" set
ii  gstreamer0.10-plugins-good                  0.10.31-1ubuntu2+ti1.6.4.1+1linaro1                 GStreamer plugins from the "good" set
ii  gstreamer0.10-pulseaudio                    0.10.31-1ubuntu2+ti1.6.4.1+1linaro1                 GStreamer plugin for PulseAudio
ii  gstreamer0.10-x                             0.10.36-1+ti1.6.4.1+1linaro1                        GStreamer plugins for X11 and Pango
ii  hwpack-linaro-leb-origen                    20121021-424                                        Dummy package to install a hwpack
ii  imagemagick                                 8:6.6.9.7-5ubuntu3.9                                image manipulation programs
ii  imagemagick-common                          8:6.6.9.7-5ubuntu3.9                                image manipulation programs -- infrastructure
ii  indicator-sound                             0.8.5.0-0ubuntu2.2~linaro1                          System sound indicator.
ii  lava-test                                   0.13-0ubuntu1~linaro1                               LAVA test execution framework
ii  lava-tool                                   0.6-0ubuntu1~linaro1                                Command line utility for Linaro validation services
ii  libasound2                                  1.0.25-1ubuntu11~1linaro3                           shared library for ALSA applications
ii  libasound2-dev                              1.0.25-1ubuntu11~1linaro3                           shared library for ALSA applications -- development files
ii  libatk-adaptor-schemas                      2.4.0-1ubuntu2                                      at-spi2-atk GSettings schemas
ii  libcompizconfig0                            1:0.9.8+bzr3287-0linaro3                            Settings library for plugins - OpenCompositing Project
ii  libdecoration0                              1:0.9.8+bzr3287-0linaro3                            Compiz window decoration library
ii  libgstreamer-plugins-base0.10-0             0.10.36-1+ti1.6.4.1+1linaro1                        GStreamer libraries from the "base" set
ii  libjpeg-turbo8                              1.2.1+svn837~ci9+20120614+f8eb71d-0linaro1          IJG JPEG compliant runtime library.
ii  libjpeg-turbo8-dev                          1.2.1+svn837~ci9+20120614+f8eb71d-0linaro1          Development files for the IJG JPEG library
ii  libmail-sendmail-perl                       0.79.16-1                                           Send email from a perl script
ii  libmailtools-perl                           2.08-1                                              Manipulate email in perl programs
ii  libntrack-qt4-1                             016-1ubuntu1                                        Qt 4 API for ntrack
ii  libpulse-mainloop-glib0                     1:2.0-0ubuntu1~linaro2                              PulseAudio client libraries (glib support)
ii  libpulse0                                   1:2.0-0ubuntu1~linaro2                              PulseAudio client libraries
ii  libpulsedsp                                 1:2.0-0ubuntu1~linaro2                              PulseAudio OSS pre-load library
ii  libqt4-core                                 4:4.8.1-0ubuntu4.9                                  transitional package for Qt 4 core non-GUI runtime libraries
ii  libqt4-dbg                                  4:4.8.1-0ubuntu4.9                                  Qt 4 library debugging symbols
ii  libqt4-dbus                                 4:4.8.1-0ubuntu4.9                                  Qt 4 D-Bus module
ii  libqt4-declarative                          4:4.8.1-0ubuntu4.9                                  Qt 4 Declarative module
ii  libqt4-declarative-gestures                 4:4.8.1-0ubuntu4.9                                  Qt 4 gestures QML plugin
ii  libqt4-declarative-particles                4:4.8.1-0ubuntu4.9                                  Qt 4 particles QML plugin
ii  libqt4-designer                             4:4.8.1-0ubuntu4.9                                  Qt 4 designer module
ii  libqt4-dev                                  4:4.8.1-0ubuntu4.9                                  Qt 4 development files
ii  libqt4-gui                                  4:4.8.1-0ubuntu4.9                                  transitional package for Qt 4 GUI runtime libraries
ii  libqt4-help                                 4:4.8.1-0ubuntu4.9                                  Qt 4 help module
ii  libqt4-network                              4:4.8.1-0ubuntu4.9                                  Qt 4 network module
ii  libqt4-opengl                               4:4.8.1-0ubuntu4.9                                  Qt 4 OpenGL module
ii  libqt4-opengl-dev                           4:4.8.1-0ubuntu4.9                                  Qt 4 OpenGL library development files
ii  libqt4-qt3support                           4:4.8.1-0ubuntu4.9                                  Qt 3 compatibility library for Qt 4
ii  libqt4-script                               4:4.8.1-0ubuntu4.9                                  Qt 4 script module
ii  libqt4-scripttools                          4:4.8.1-0ubuntu4.9                                  Qt 4 script tools module
ii  libqt4-sql                                  4:4.8.1-0ubuntu4.9                                  Qt 4 SQL module
ii  libqt4-sql-mysql                            4:4.8.1-0ubuntu4.9                                  Qt 4 MySQL database driver
ii  libqt4-sql-sqlite                           4:4.8.1-0ubuntu4.9                                  Qt 4 SQLite 3 database driver
ii  libqt4-svg                                  4:4.8.1-0ubuntu4.9                                  Qt 4 SVG module
ii  libqt4-test                                 4:4.8.1-0ubuntu4.9                                  Qt 4 test module
ii  libqt4-xml                                  4:4.8.1-0ubuntu4.9                                  Qt 4 XML module
ii  libqt4-xmlpatterns                          4:4.8.1-0ubuntu4.9                                  Qt 4 XML patterns module
ii  libtimezonemap1                             0.3.2                                               GTK+3 timezone map widget
ii  libunity-core-5.0-5                         5.16.0-0ubuntu1linaro1                              Core library for the Unity interface.
ii  libvpx1                                     1.0.0-1.1linaro4                                    VP8 video codec (shared library)
ii  libwayland0                                 0.95.0-0ubuntulinaro2                               wayland compositor infrastructure - shared libraries
ii  libwrap0                                    7.6.q-21                                            Wietse Venema's TCP wrappers library
ii  linaro-overlay                              1112.2                                              Linaro Overlay Specific Changes
ii  linaro-overlay-minimal                      1112.2                                              Linaro Overlay for Linaro headless/minimal images
ii  linaro-ubuntu-desktop                       032-precise                                         Linaro Ubuntu Desktop profile
ii  linux-firmware                              1.80~linaro3                                        Firmware for Linux kernel drivers
ii  linux-headers-3.0.57-odroidx2               20130110                                            Header files related to Linux kernel, specifically,
ii  linux-headers-3.0.60-odroidx2               20130124                                            Header files related to Linux kernel, specifically,
ii  linux-headers-3.6.0-1-linaro-lt-origen      3.6.0-1.1~ci+121020091538                           Linux kernel headers for version 3.6.0 on Samsung ORIGEN-based systems
ii  linux-headers-linaro-lt-origen              3.6.0.1.1                                           Linux kernel headers for the Samsung ORIGEN architecture.
ii  linux-image-3.0.51-20130103-odroidu2:armel  3.0.51-20130103                                     Linux kernel image for version 3.0.51 on hardkernel ODROIDU2-based systems
hi  linux-image-3.0.57-odroidx2                 20130110                                            Linux kernel binary image for version 3.0.57-odroidx2
hi  linux-image-3.0.60-odroidx2                 20130124                                            Linux kernel binary image for version 3.0.60-odroidx2
hi  linux-image-3.6.0-1-linaro-lt-origen        3.6.0-1.1~ci+121020091538                           Linux kernel image for version 3.6.0 on Samsung ORIGEN-based systems
ii  linux-image-linaro-lt-origen                3.6.0.1.1                                           Linux kernel image for the Samsung ORIGEN architecture.
ii  linux-linaro-tools-3.6.0-1-linaro-lt-origen 3.6.0-1.1~ci+121020091538                           Linux kernel version specific tools for version 3.6.0-1
ii  linux-tools-linaro-lt-origen                3.6.0.1.1                                           Linux kernel tools for the Samsung ORIGEN architecture.
ii  origen-bluetooth                            0.10                                                Samsung Origen Bluetooth Scripts
ii  origen-wlan                                 0.8                                                 Samsung Origen Wlan Scripts
ii  printer-driver-splix                        2.0.0+svn300-1.1ubuntu2                             Driver for Samsung and Xerox SPL2 and SPLc laser printers
ii  pulseaudio                                  1:2.0-0ubuntu1~linaro2                              PulseAudio sound server
ii  pulseaudio-module-bluetooth                 1:2.0-0ubuntu1~linaro2                              Bluetooth module for PulseAudio sound server
ii  pulseaudio-module-gconf                     1:2.0-0ubuntu1~linaro2                              GConf module for PulseAudio sound server
ii  pulseaudio-module-x11                       1:2.0-0ubuntu1~linaro2                              X11 module for PulseAudio sound server
ii  pulseaudio-utils                            1:2.0-0ubuntu1~linaro2                              Command line tools for the PulseAudio sound server
ii  python-json-schema-validator                2.3-0ubuntu1~linaro2                                JSON manipulation utilities developed by the Linaro infrastructure team
ii  python-linaro-dashboard-bundle              1.8-0ubuntu1~linaro1                                Library for manipulating LAVA dashboard bundles
ii  python-qt4                                  4.9.1-2ubuntu1                                      Python bindings for Qt4
ii  python-qt4-dbus                             4.9.1-2ubuntu1                                      DBus Support for PyQt4
ii  qt4-demos                                   4:4.8.1-0ubuntu4.9                                  Qt 4 examples and demos
ii  qt4-designer                                4:4.8.1-0ubuntu4.9                                  graphical designer for Qt 4 applications
ii  qt4-dev-tools                               4:4.8.1-0ubuntu4.9                                  Qt 4 development tools
ii  qt4-doc                                     4:4.8.1-0ubuntu4.9                                  Qt 4 API documentation
ii  qt4-linguist-tools                          4:4.8.1-0ubuntu4.9                                  Qt 4 Linguist tools
ii  qt4-qmake                                   4:4.8.1-0ubuntu4.9                                  Qt 4 qmake Makefile generator tool
ii  qt4-qmlviewer                               4:4.8.1-0ubuntu4.9                                  Qt 4 QML viewer
ii  shared-desktop-ontologies                   0.8.1-1                                             shared ontologies for semantic searching
ii  stress                                      1.0.1-1build1linaro1                                A tool to impose load on and stress test a computer system
ii  stress-dbgsym                               1.0.1-1build1linaro1                                debug symbols for package stress
ii  tcpd                                        7.6.q-21                                            Wietse Venema's TCP wrapper utilities
ii  thunderbird                                 1:45.8.0+build1-0ubuntu0.12.04.1                    Email, RSS and newsgroup client with integrated spam filter
ii  thunderbird-gnome-support                   1:45.8.0+build1-0ubuntu0.12.04.1                    Email, RSS and newsgroup client - GNOME support
ii  ubuntu-wallpapers                           0.34.1linaro1                                       Ubuntu Wallpapers
ii  ubuntu-wallpapers-precise                   0.34.1linaro1                                       Ubuntu 12.04 Wallpapers
ii  unity                                       5.16.0-0ubuntu1linaro1                              Interface designed for efficiency of space and interaction.
ii  unity-common                                5.16.0-0ubuntu1linaro1                              Common files for the Unity interface.
ii  unity-services                              5.16.0-0ubuntu1linaro1                              Services for the Unity interface
ii  upstart                                     1.5-0ubuntu8~linaro1                                event-based init daemon
ii  vino                                        3.4.2-0ubuntu1.3.1                                  VNC server for GNOME
ii  xrdp                                        0.5.0-2+deb7u1build0.12.04.1                        Remote Desktop Protocol (RDP) server

@@@ end @@@
SURVEY_COMPLETE
