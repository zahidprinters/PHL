=== compilers on the board ===
gcc                            /usr/bin/gcc
g++                            /usr/bin/g++
cc                             /usr/bin/cc
arm-linux-gnueabi-gcc          MISSING
arm-linux-gnueabihf-gcc        /usr/bin/arm-linux-gnueabihf-gcc
make                           /usr/bin/make
ld                             /usr/bin/ld
--- versions ---
gcc (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3
g++ (Ubuntu/Linaro 4.6.3-1ubuntu5) 4.6.3

=== binutils / demangler ===
nm           /usr/bin/nm
objdump      /usr/bin/objdump
readelf      /usr/bin/readelf
c++filt      /usr/bin/c++filt
strings      /usr/bin/strings
file         /usr/bin/file

=== EMAMain mangled names (argument counts are encoded here) ===
_ZN7EMAMain10writeEventEP10_EMA_EVENT
_ZN7EMAMain12setReadEventEP10_EMA_EVENT
_ZN7EMAMain15checkWriteEventEP10_EMA_EVENT
_ZN7EMAMain4openEv
_ZN7EMAMain5closeEv
_ZN7EMAMain6isOpenEv
_ZN7EMAMain9readEventEv
_ZN7EMAMainC1Ev
_ZN7EMAMainC2Ev
_ZN7EMAMainD1Ev
_ZN7EMAMainD2Ev

=== the same, demangled ===
EMAMain::writeEvent(_EMA_EVENT*)
EMAMain::setReadEvent(_EMA_EVENT*)
EMAMain::checkWriteEvent(_EMA_EVENT*)
EMAMain::open()
EMAMain::close()
EMAMain::isOpen()
EMAMain::readEvent()
EMAMain::EMAMain()
EMAMain::EMAMain()
EMAMain::~EMAMain()
EMAMain::~EMAMain()

=== every exported symbol (full API surface) ===
_Z21qMetaTypeDeleteHelperI12QextPortInfoEvPT_
_Z24qMetaTypeConstructHelperI12QextPortInfoEPvPKT_
_ZN10ReadThread3runEv
_ZN10ReadThread5abortEv
_ZN10ReadThreadC1EP7QObject
_ZN10ReadThreadC2EP7QObject
_ZN10ReadThreadD0Ev
_ZN10ReadThreadD1Ev
_ZN10ReadThreadD2Ev
_ZN11QReadLockerD1Ev
_ZN11QReadLockerD2Ev
_ZN12QextPortInfoD1Ev
_ZN12QextPortInfoD2Ev
_ZN14QextSerialPort10dsrChangedEb
_ZN14QextSerialPort10lineStatusEv
_ZN14QextSerialPort10setTimeoutEl
_ZN14QextSerialPort11errorStringEv
_ZN14QextSerialPort11qt_metacallEN11QMetaObject4CallEiPPv
_ZN14QextSerialPort11qt_metacastEPKc
_ZN14QextSerialPort11setBaudRateE12BaudRateType
_ZN14QextSerialPort11setDataBitsE12DataBitsType
_ZN14QextSerialPort11setPortNameERK7QString
_ZN14QextSerialPort11setStopBitsE12StopBitsType
_ZN14QextSerialPort12setQueryModeENS_9QueryModeE
_ZN14QextSerialPort14setFlowControlE8FlowType
_ZN14QextSerialPort16staticMetaObjectE
_ZN14QextSerialPort4openE6QFlagsIN9QIODevice12OpenModeFlagEE
_ZN14QextSerialPort5closeEv
_ZN14QextSerialPort5flushEv
_ZN14QextSerialPort6setDtrEb
_ZN14QextSerialPort6setRtsEb
_ZN14QextSerialPort7readAllEv
_ZN14QextSerialPort8readDataEPcx
_ZN14QextSerialPort9setParityE10ParityType
_ZN14QextSerialPort9writeDataEPKcx
_ZN14QextSerialPortC1ENS_9QueryModeEP7QObject
_ZN14QextSerialPortC1ERK12PortSettingsNS_9QueryModeEP7QObject
_ZN14QextSerialPortC1ERK7QStringNS_9QueryModeEP7QObject
_ZN14QextSerialPortC1ERK7QStringRK12PortSettingsNS_9QueryModeEP7QObject
_ZN14QextSerialPortC2ENS_9QueryModeEP7QObject
_ZN14QextSerialPortC2ERK12PortSettingsNS_9QueryModeEP7QObject
_ZN14QextSerialPortC2ERK7QStringNS_9QueryModeEP7QObject
_ZN14QextSerialPortC2ERK7QStringRK12PortSettingsNS_9QueryModeEP7QObject
_ZN14QextSerialPortD0Ev
_ZN14QextSerialPortD1Ev
_ZN14QextSerialPortD2Ev
_ZN20QextSerialEnumerator11qt_metacallEN11QMetaObject4CallEiPPv
_ZN20QextSerialEnumerator11qt_metacastEPKc
_ZN20QextSerialEnumerator13deviceRemovedERK12QextPortInfo
_ZN20QextSerialEnumerator16deviceDiscoveredERK12QextPortInfo
_ZN20QextSerialEnumerator16staticMetaObjectE
_ZN20QextSerialEnumerator18setUpNotificationsEv
_ZN20QextSerialEnumerator8getPortsEv
_ZN20QextSerialEnumeratorC1EP7QObject
_ZN20QextSerialEnumeratorC2EP7QObject
_ZN20QextSerialEnumeratorD0Ev
_ZN20QextSerialEnumeratorD1Ev
_ZN20QextSerialEnumeratorD2Ev
_ZN21QextSerialPortPrivate10_q_canReadEv
_ZN21QextSerialPortPrivate10setDtr_sysEb

=== any EMA type/struct/enum symbols ===
_Z21qMetaTypeDeleteHelperI12QextPortInfoEvPT_
_Z24qMetaTypeConstructHelperI12QextPortInfoEPvPKT_
_ZN14QextSerialPort11setBaudRateE12BaudRateType
_ZN14QextSerialPort11setDataBitsE12DataBitsType
_ZN14QextSerialPort11setStopBitsE12StopBitsType
_ZN14QextSerialPort14setFlowControlE8FlowType
_ZN14QextSerialPort9setParityE10ParityType
_ZN15QSocketNotifierC1EiNS_4TypeEP7QObject
_ZN21QextSerialPortPrivate11setBaudRateE12BaudRateTypeb
_ZN21QextSerialPortPrivate11setDataBitsE12DataBitsTypeb
_ZN21QextSerialPortPrivate11setStopBitsE12StopBitsTypeb
_ZN21QextSerialPortPrivate14setFlowControlE8FlowTypeb
_ZN21QextSerialPortPrivate9setParityE10ParityTypeb
_ZN5QListIP10_EMA_EVENTE13detach_helperEi
_ZN5QListIP10_EMA_EVENTE18detach_helper_growEii
_ZN5QListIP10_EMA_EVENTE6appendERKS1_
_ZN6QQueueIP10_EMA_EVENTED1Ev
_ZN6QQueueIP10_EMA_EVENTED2Ev
_ZN7EMAMain10writeEventEP10_EMA_EVENT
_ZN7EMAMain12setReadEventEP10_EMA_EVENT
_ZN7EMAMain15checkWriteEventEP10_EMA_EVENT
_ZN7EMAMain4openEv
_ZN7EMAMain5closeEv
_ZN7EMAMain6isOpenEv
_ZN7EMAMain9readEventEv
_ZN7EMAMainC1Ev
_ZN7EMAMainC2Ev
_ZN7EMAMainD1Ev
_ZN7EMAMainD2Ev
_ZN7QObject10childEventEP11QChildEvent

=== are there headers or a sample anywhere on the board? ===
/usr/local/bin/CMIMIRDemo
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/fiemap.h
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/nodemask.h
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/dma_remapping.h
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/consolemap.h
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/pagemap.h
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/davinci_emac.h
/usr/src/linux-headers-3.0.57-odroidx2/include/linux/semaphore.h
/usr/src/linux-headers-3.0.57-odroidx2/include/sound/memalloc.h
/usr/src/linux-headers-3.0.57-odroidx2/include/config/cpu/freq/gov/ondemand.h
/usr/src/linux-headers-3.0.57-odroidx2/include/config/net/ematch.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/x86/include/asm/irq_remapping.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/ia64/include/asm/irq_remapping.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/arm/mach-at91/include/mach/at91rm9200_emac.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/mips/include/asm/mach-tx49xx/ioremap.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/mips/include/asm/mach-powertv/ioremap.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/mips/include/asm/mach-bcm63xx/ioremap.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/mips/include/asm/mach-tx39xx/ioremap.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/mips/include/asm/mach-au1x00/ioremap.h
/usr/src/linux-headers-3.6.0-1-linaro-lt-origen/arch/mips/include/asm/mach-generic/ioremap.h
--- /usr/local/include ---
none
--- /usr/local/src or similar ---
bin
etc
games
lib
man
sbin
share

=== library dependencies: can we link a stub against it? ===
NEEDED               libQtCore.so.4
  NEEDED               libpthread.so.0
  NEEDED               libstdc++.so.6
  NEEDED               libgcc_s.so.1
  NEEDED               libc.so.6
  NEEDED               ld-linux-armhf.so.3
--- is it stripped? ---
/usr/local/lib/libemaLib_arm_1.0.1.so: ELF 32-bit LSB shared object, ARM, version 1 (SYSV), dynamically linked, BuildID[sha1]=0x419d2798de2fc02b29beaf5b1bf566b8342cfc01, stripped
--- SONAME ---

