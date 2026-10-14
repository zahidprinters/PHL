// Reproduce the vendor's own writeEvent call and capture the frame it makes.
//
// CMIMIRDemo has exactly ONE call to ema_writeEvent (PLT 0xe41c, reached at
// 0x14bb8). Immediately before it it builds the event on the stack at sp+148:
//
//     sp+148 (+0)  = 56
//     sp+152 (+4)  = 32      <- the type field we already mapped
//     sp+201 (+53) = 1
//     sp+202 (+54) = 30
//
// Our earlier sweep only reached type 20, so type 32 was never tried. This
// reproduces the vendor's struct byte for byte and reports the frame the
// serialiser produces.
//
// Runs under nullwrite.so, so the frame is captured and SWALLOWED: the STM8
// receives nothing. Only once the format is known do we ever transmit it.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_vendor ema_vendor.cpp -I/usr/include/qt4 \
//       -L/usr/local/lib -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread

#include <QCoreApplication>
#include <cstdio>
#include <cstdlib>
#include <cstring>

struct _EMA_EVENT {
    unsigned char raw[256];
};

class EMAMain {
public:
    EMAMain();
    ~EMAMain();
    bool open();
    void close();
    bool isOpen();
    int readEvent();
    void writeEvent(_EMA_EVENT *evt);
};

#define EVSIZE 256

// The vendor's event, assembled exactly as CMIMIRDemo does at 0x14ba0.
static void build_vendor_event(unsigned char *ev)
{
    memset(ev, 0, EVSIZE);
    *(unsigned int *)(ev + 0) = 56;    // sp+148
    *(unsigned int *)(ev + 4) = 32;    // sp+152  <- type
    ev[53] = 1;                         // sp+201
    ev[54] = 30;                        // sp+202
}

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) {
        printf("calloc failed\n");
        return 2;
    }
    EMAMain *ema = new (mem) EMAMain();

    unsigned char *ev = (unsigned char *)calloc(1, EVSIZE);
    if (!ev) {
        printf("calloc event failed\n");
        return 2;
    }

    printf("[1] open\n");
    fflush(stdout);
    ema->open();

    printf("\n@@ VENDOR EVENT verbatim: type=32 off53=1 off54=30\n");
    fflush(stdout);
    build_vendor_event(ev);
    ema->writeEvent((_EMA_EVENT *)ev);

    // Sweep the value byte at offset 8, which is the field we proved earlier
    // drives the last byte of a 5-byte write frame, to see if type 32 uses it.
    printf("\n@@ same, but offset 8 = 1\n");
    fflush(stdout);
    build_vendor_event(ev);
    ev[8] = 1;
    ema->writeEvent((_EMA_EVENT *)ev);

    // And with the two trailing fields varied, in case they are the real
    // selectors and type 32 is a group command.
    printf("\n@@ type=32, off53=0 off54=0\n");
    fflush(stdout);
    build_vendor_event(ev);
    ev[53] = 0;
    ev[54] = 0;
    ema->writeEvent((_EMA_EVENT *)ev);

    printf("\n@@ type=32, off53=1 off54=31\n");
    fflush(stdout);
    build_vendor_event(ev);
    ev[53] = 1;
    ev[54] = 31;
    ema->writeEvent((_EMA_EVENT *)ev);

    printf("\n@@ DONE\n");
    fflush(stdout);
    ema->close();
    return 0;
}
