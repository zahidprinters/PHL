// Sweep the class-04 device selector to find OUT1 and OUT2.
//
// Relay is selector 01 (confirmed). Byte 3 is a device selector and byte 4 is
// the state, so the next candidates are simply 02, 03, 04...
//
// Two things are learned per selector:
//   * does the STM8 echo it? An unrecognised selector should be ignored, which
//     is how the earlier op-04 sweep proved types 6..15 were invalid.
//   * does the meter on OUT1 / OUT2 move during the ON window?
//
// Phases are long because the operator is watching a meter.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_sel ema_sel.cpp -I/usr/include/qt4 \
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
#define TYPE_C04 32

static void send(EMAMain *ema, int sel, int state)
{
    _EMA_EVENT ev;
    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = TYPE_C04;      // offset 4  = type
    ((unsigned char *)&ev)[53] = (unsigned char)sel;
    ((unsigned char *)&ev)[54] = (unsigned char)state;
    ema->writeEvent(&ev);
    printf("    -> 55 05 04 %02x %02x\n", sel, state);
    fflush(stdout);
}

static void hold(EMAMain *ema, double seconds, const char *label)
{
    long ticks = (long)(seconds * 10);
    printf("    [%s] %.0fs\n", label, seconds);
    fflush(stdout);
    for (long i = 0; i < ticks; i++) {
        QCoreApplication::processEvents(QEventLoop::AllEvents, 50);
        ema->readEvent();
        usleep(100000);
    }
}

int main(int argc, char **argv)
{
    // ./ema_sel <selector> <off_s> <on_s>  -- defaults to selector 2
    int sel = (argc > 1) ? (int)strtol(argv[1], 0, 0) : 2;
    double off_s = (argc > 2) ? atof(argv[2]) : 8.0;
    double on_s = (argc > 3) ? atof(argv[3]) : 20.0;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    printf("\n=== SELECTOR %02x : OFF %.0fs (baseline) ===\n", sel, off_s);
    fflush(stdout);
    ema->open();
    send(ema, sel, 0);
    hold(ema, off_s, "BASELINE");

    printf("\n=== SELECTOR %02x : ON %.0fs  <<< WATCH THE METER ===\n",
           sel, on_s);
    fflush(stdout);
    send(ema, sel, 1);
    hold(ema, on_s, "ON");

    printf("\n=== SELECTOR %02x : OFF %.0fs ===\n", sel, off_s);
    fflush(stdout);
    send(ema, sel, 0);
    hold(ema, off_s, "OFF");

    ema->close();
    printf("\ndone\n");
    fflush(stdout);
    return 0;
}