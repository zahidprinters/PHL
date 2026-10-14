=== 1. every UART: does it have a real IRQ behind it? ===
irq:0 on a serial line means no hardware behind it
serinfo:1.0 driver revision:
0: uart:unknown port:00000000 irq:0
1: uart:unknown port:00000000 irq:0
2: uart:unknown port:00000000 irq:0
3: uart:unknown port:00000000 irq:0
--- ttySAC device -> driver -> irq ---
ttySAC0      driver=s5pv210-uart   irq=n/a
ttySAC1      driver=s5pv210-uart   irq=n/a
ttySAC2      driver=s5pv210-uart   irq=n/a
ttySAC3      driver=s5pv210-uart   irq=n/a

=== 2. native GMAC: driver, or does it not exist in this kernel? ===
--- modules that would drive a SoC MAC ---
--- kernel config ---
--- any such module file shipped? ---
--- other kernels/boot dirs available ---
total 9580
drwxr-xr-x  2 root root    4096 Oct  4 21:32 .
drwxr-xr-x 23 root root    4096 Nov 27  2013 ..
-rw-r--r--  1 root root 1238067 Jan 24  2013 System.map-3.0.60-odroidx2
-rw-r--r--  1 root root   77272 Jan 24  2013 config-3.0.60-odroidx2
-rw-r--r--  1 root root   77208 Apr  5  2014 config-3.0.68
-rw-r--r--  1 root root 3044620 Jan 24  2013 initrd.img-3.0.60-odroidx2
-rw-r--r--  1 root root 3048082 Oct  4 21:32 initrd.img-3.0.68
-rw-r--r--  1 root root 2300348 Jan 24  2013 vmlinuz-3.0.60-odroidx2
--- does the SoC even have an ethernet node? ---

=== 3. 93LC66A EEPROM: which bus could hold it? ===
--- SPI controllers in device-tree ---
--- SPI busses registered ---
(no spi devices)
--- unclaimed I2C addresses at 0x50-0x57 (read byte, no write) ---
i2cdetect NOT installed
--- any EEPROM driver loaded? ---
none

