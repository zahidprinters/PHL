// Enumerate the WIEGAND event frames WITHOUT sending anything to the STM8.
//
// Runs under nullwrite.so: every frame is captured and swallowed, so this is a
// pure read of what libemaLib's serialiser produces. The STM8 never sees a byte.
//
// The vendor enum carries five Wiegand events (progress notes: enum types 2-6):
//     WIEGAND_READ_DATA  WRITE_DATA  SET_CONFIG  GET_CONFIG  AUTO_DETECT
// No frame for any of them has ever been mapped. This scanner answers two
// questions in one pass:
//
//   Phase A  types 1..10   -> what frame does each Wiegand type emit?
//   Phase B  types 2..6    -> which struct offset carries the card/data value?
//                             (pin type, set ONE struct byte to 1 per case;
//                              whichever offset moves a frame byte is the field)
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_wscan ema_wscan.cpp -I/usr/include/qt4 \
//       -L/usr/local/lib -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread
// Run:
//   LD_PRELOAD=./nullwrite.so ./ema_wscan 2>&1

#include <QtCore/QCoreApplication>
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

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    unsigned char *ev = (unsigned char *)calloc(1, EVSIZE);
    if (!ev) { printf("calloc event failed\n"); return 2; }

    printf("@@PHASE A - event types 1..10\n");
    fflush(stdout);
    ema->open();

    for (int t = 1; t <= 10; t++) {
        memset(ev, 0, EVSIZE);
        ((unsigned int *)ev)[1] = (unsigned int)t;   // offset 4 = event type
        printf("@@TYPE %d\n", t);
        fflush(stdout);
        ema->writeEvent((_EMA_EVENT *)ev);
    }

    printf("@@PHASE B - struct offset sweep per Wiegand type 2..6\n");
    fflush(stdout);
    for (int t = 2; t <= 6; t++) {
        for (int off = 0; off < EVSIZE; off++) {
            memset(ev, 0, EVSIZE);
            ((unsigned int *)ev)[1] = (unsigned int)t;   // type stays pinned
            ((unsigned char *)ev)[off] = 1;              // one byte set
            printf("@@TYPE %d OFFSET %d\n", t, off);
            fflush(stdout);
            ema->writeEvent((_EMA_EVENT *)ev);
        }
    }

    printf("@@END\n");
    fflush(stdout);
    ema->close();
    return 0;
}
