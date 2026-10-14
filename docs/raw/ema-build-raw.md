=== build + trace tools ===
g++        /usr/bin/g++
strace     MISSING
ltrace     MISSING
--- Qt4 present? ---
lrwxrwxrwx 1 root root      18 May 28  2015 /usr/lib/arm-linux-gnueabihf/libQtCore.so.4 -> libQtCore.so.4.8.1
lrwxrwxrwx 1 root root      18 May 28  2015 /usr/lib/arm-linux-gnueabihf/libQtCore.so.4.8 -> libQtCore.so.4.8.1
-rw-r--r-- 1 root root 2052968 May 28  2015 /usr/lib/arm-linux-gnueabihf/libQtCore.so.4.8.1

=== strings: config file names and default port hints ===
.init
.init_array
/dev/ttyS0
/dev/ttySAC0
ttyACM*
ttyS
ttyS*
ttyUSB
ttyUSB*

=== the library's own NEEDED list, complete ===
NEEDED               libQtCore.so.4
  NEEDED               libpthread.so.0
  NEEDED               libstdc++.so.6
  NEEDED               libgcc_s.so.1
  NEEDED               libc.so.6
  NEEDED               ld-linux-armhf.so.3

=== uploading /root/ema_probe.cpp ===
45 /root/ema_probe.cpp

=== compiling against libemaLib ===
ema_probe.cpp: In function æint main()Æ:
ema_probe.cpp:30:10: error: invalid use of æEMAMain::EMAMainÆ
NO BINARY
