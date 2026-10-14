// Recover the EMA write format WITHOUT sending anything to the STM8.
//
// Pairs with nullwrite.c: that shim captures writes to the serial fd and then
// swallows them, so libemaLib builds the frame it would have sent, we print it,
// and the STM8 receives nothing. There is no actuation risk in this run at all.
//
// Method: allocate a zeroed _EMA_EVENT, then set ONE byte at a time to a
// recognisable value and call writeEvent(). Comparing the emitted frames shows
// which struct offsets the serialiser reads, where each lands in the frame, and
// how many bytes are affected -- which is the struct layout and the wire format
// in one pass.
//
// Offsets 8, 24 and 64 are already known to be read (from the disassembly of
// writeEvent); the sweep confirms them and finds the rest.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_wprobe ema_wprobe.cpp -I/usr/include/qt4 \
//       -L/usr/local/lib -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread

#include <QCoreApplication>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>

// The vendor type must be named, not replaced by void*: C++ mangling encodes
// the pointee type, so writeEvent(_EMA_EVENT*) is _ZN7EMAMain10writeEventEP10_EMA_EVENT
// and would NOT match a declaration taking void*.
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
#define PROBE_VAL 0x5a        /* distinctive, so a moved byte is obvious */

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) {
        printf("calloc failed\n");
        return 2;
    }
    EMAMain *ema = new (mem) EMAMain();

    printf("[1] open (its bytes are swallowed by nullwrite.so)\n");
    fflush(stdout);
    ema->open();
    printf("[2] isOpen=%d\n", (int)ema->isOpen());
    fflush(stdout);

    // A scratch event. Zeroed, so only the byte under test is non-zero.
    void *evmem = calloc(1, EVSIZE);
    if (!evmem) {
        printf("calloc event failed\n");
        return 2;
    }
    _EMA_EVENT *ev = (_EMA_EVENT *)evmem;

    // 0) All zero: establishes the baseline frame the serialiser emits.
    printf("\n@@ BASELINE (all-zero event)\n");
    fflush(stdout);
    ema->writeEvent(ev);

    // Sweep SMALL values at the three offsets the disassembly says writeEvent
    // actually reads (+8, +24, +64). The first sweep used 0x5a, which is not a
    // valid event type, so the serialiser rejected every case and emitted the
    // same default frame. Real enum values are small and dense.
    static const int OFFS[] = {8, 24, 64};
    printf("\n@@ SWEEP2: offsets 8/24/64 x values 1..12\n");
    fflush(stdout);
    for (int oi = 0; oi < 3; oi++) {
        for (int val = 1; val <= 12; val++) {
            memset(ev, 0, EVSIZE);
            ((unsigned char *)ev)[OFFS[oi]] = (unsigned char)val;
            printf("@@OFFSET %d\n", OFFS[oi]);
            printf("@@VALUE %d\n", val);
            fflush(stdout);
            ema->writeEvent(ev);
        }
    }

    // Also try the whole struct as a single dword at each 4-byte slot, in case
    // the type is a 32-bit field whose low byte is not the selector.
    printf("\n@@ SWEEP3: 4-byte value 1 at each 4-byte slot 0..96\n");
    fflush(stdout);
    for (int off = 0; off <= 96; off += 4) {
        memset(ev, 0, EVSIZE);
        ((unsigned int *)ev)[off / 4] = 1;
        printf("@@OFFSET %d\n", off);
        printf("@@VALUE DWORD 1\n");
        fflush(stdout);
        ema->writeEvent(ev);
    }

    // SWEEP4 - the decisive one. A dword of 1 at offset +4 emits the OPEN frame
    // while 0 emits CLOSE, so +4 is the event-type field. Sweep its value to
    // enumerate the protocol: which numbers mean GPO write, relay, Wiegand.
    printf("\n@@ SWEEP4: dword at offset 4, values 0..20\n");
    fflush(stdout);
    for (int val = 0; val <= 20; val++) {
        memset(ev, 0, EVSIZE);
        ((unsigned int *)ev)[1] = (unsigned int)val;   // byte offset 4
        printf("@@OFFSET 4\n");
        printf("@@VALUE TYPE %d\n", val);
        fflush(stdout);
        ema->writeEvent(ev);
    }

    // SWEEP5 - locate the field that carries the OUTPUT VALUE. Type 5 emits
    // `55 05 02 03 00`, so byte 4 of the frame is the value and reads 00 while
    // the struct payload is zero. Pin type=5, then set ONE struct byte to 1 at a
    // time: whichever offset flips frame byte 4 to 01 is the value field.
    printf("\n@@ SWEEP5: type=5 fixed, value byte 1 at each offset\n");
    fflush(stdout);
    for (int off = 0; off < EVSIZE; off++) {
        memset(ev, 0, EVSIZE);
        ((unsigned int *)ev)[1] = 5;               // type at byte offset 4
        ((unsigned char *)ev)[off] = 1;
        printf("@@OFFSET %d\n", off);
        printf("@@VALUE PAYLOAD %d\n", off);
        fflush(stdout);
        ema->writeEvent(ev);
    }

    printf("\n@@ DONE\n");
    fflush(stdout);

    ema->close();
    return 0;
}