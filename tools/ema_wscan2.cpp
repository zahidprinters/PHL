// Probe the Wiegand events that writeEvent() DROPS (types 2-4: READ_DATA,
// WRITE_DATA, SET_CONFIG). NOTHING IS TRANSMITTED - runs under nullwrite.so.
//
// The single-byte sweep showed types 2-4 emit no frame whatever one byte is
// set to, so they either need several fields at once, or they do not go
// through writeEvent at all. This tries:
//
//   Phase C  whole-struct fills (all 0x01, then a realistic card number)
//   Phase D  type 3 (WRITE_DATA) with a 26-bit card at offsets 8..13 plus a
//            length byte swept at every offset
//   Phase E  setReadEvent() for type 2 - the READ path, a different call
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_wscan2 ema_wscan2.cpp \
//       -I/usr/include/qt4 -I/usr/include/qt4/QtCore \
//       -L/usr/local/lib -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread

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
    void setReadEvent(_EMA_EVENT *evt);
    void writeEvent(_EMA_EVENT *evt);
};

#define EVSIZE 256

static void settype(unsigned char *ev, int t)
{
    memset(ev, 0, EVSIZE);
    ((unsigned int *)ev)[1] = (unsigned int)t;   // offset 4 = event type
}

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    unsigned char *ev = (unsigned char *)calloc(1, EVSIZE);
    if (!ev) { printf("calloc event failed\n"); return 2; }

    printf("@@PHASE C - whole-struct fills\n");
    fflush(stdout);
    ema->open();

    for (int t = 2; t <= 4; t++) {
        // all bytes 0x01 except the type dword
        settype(ev, t);
        for (int i = 0; i < EVSIZE; i++)
            if (i < 4 || i > 7) ev[i] = 0x01;
        printf("@@TYPE %d FILL ALL01\n", t);
        fflush(stdout);
        ema->writeEvent((_EMA_EVENT *)ev);

        // a plausible 26-bit card number 0x012345 at offsets 8..13
        settype(ev, t);
        static const unsigned char card[] = {0x01, 0x23, 0x45, 0x00, 0x00, 0x00};
        memcpy(ev + 8, card, sizeof card);
        printf("@@TYPE %d FILL CARD012345\n", t);
        fflush(stdout);
        ema->writeEvent((_EMA_EVENT *)ev);

        // card + every plausible length byte value 26/34 at each offset
        for (int off = 8; off < 40; off++) {
            for (int len = 26; len <= 34; len += 8) {
                settype(ev, t);
                memcpy(ev + 8, card, sizeof card);
                ev[off] = (unsigned char)len;
                printf("@@TYPE %d LEN %d AT %d\n", t, len, off);
                fflush(stdout);
                ema->writeEvent((_EMA_EVENT *)ev);
            }
        }
    }

    printf("@@PHASE E - setReadEvent for type 2 (READ_DATA)\n");
    fflush(stdout);
    for (int t = 2; t <= 4; t++) {
        settype(ev, t);
        for (int i = 0; i < EVSIZE; i++)
            if (i < 4 || i > 7) ev[i] = 0x01;
        printf("@@SETREAD TYPE %d FILL ALL01\n", t);
        fflush(stdout);
        ema->setReadEvent((_EMA_EVENT *)ev);
        // let the library pump the link, then see what it produced
        for (int i = 0; i < 20; i++) {
            QCoreApplication::processEvents(QEventLoop::AllEvents, 50);
            ema->readEvent();
            usleep(50000);
        }
    }

    printf("@@END\n");
    fflush(stdout);
    ema->close();
    return 0;
}
