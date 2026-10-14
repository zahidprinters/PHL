// Reverse the OUTPUT the same way we reversed the INPUT.
//
// For inputs we toggled a pin and watched the status frame change. For outputs
// the effect is on a pin we cannot see in the traffic, so instead: capture the
// status frame, perform a write, then re-open the link to make the STM8 emit a
// fresh status frame, and diff the two. Any byte that moved is the output's
// state field -- and if it moves, the command demonstrably did something.
//
// This uses only open/close plus the single known-good write (type 5). No new
// commands are invented, so there is no guesswork and no new actuation risk.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_stat ema_stat.cpp -I/usr/include/qt4 \
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
#define GPO_TYPE 5

static void send(EMAMain *ema, int value)
{
    _EMA_EVENT ev;
    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = GPO_TYPE;          // byte offset 4 = type
    ((unsigned char *)&ev)[8] = (unsigned char)value;   // byte offset 8 = value
    ema->writeEvent(&ev);
}

// Pump the event loop briefly so the library can deliver whatever the STM8 says.
static void settle(EMAMain *ema, double seconds)
{
    long ticks = (long)(seconds * 20);
    for (long i = 0; i < ticks; i++) {
        QCoreApplication::processEvents(QEventLoop::AllEvents, 40);
        ema->readEvent();
        usleep(50000);
    }
}

// One cycle: open, let the STM8 volunteer a status frame, close again.
static void cycle(EMAMain *ema, double wait_s)
{
    ema->open();
    settle(ema, wait_s);
    ema->close();
    settle(ema, 0.5);
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

    printf("=== STEP 1: status BEFORE any write ===\n");
    fflush(stdout);
    cycle(ema, 3.0);

    printf("\n=== STEP 2: write type=%d value=1, then re-open for fresh status ===\n",
           GPO_TYPE);
    fflush(stdout);
    ema->open();
    settle(ema, 1.0);
    send(ema, 1);
    settle(ema, 2.0);
    ema->close();
    settle(ema, 0.5);
    cycle(ema, 3.0);

    printf("\n=== STEP 3: write value=0, then re-open for fresh status ===\n");
    fflush(stdout);
    ema->open();
    settle(ema, 1.0);
    send(ema, 0);
    settle(ema, 2.0);
    ema->close();
    settle(ema, 0.5);
    cycle(ema, 3.0);

    printf("\n=== STEP 4: write value=1 again (confirm it moves again) ===\n");
    fflush(stdout);
    ema->open();
    settle(ema, 1.0);
    send(ema, 1);
    settle(ema, 2.0);
    ema->close();
    settle(ema, 0.5);
    cycle(ema, 3.0);

    printf("\n=== done ===\n");
    fflush(stdout);
    return 0;
}