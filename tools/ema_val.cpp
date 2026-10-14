// Sweep the class-02 value byte.
//
//   ON   type 5, value V  ->  55 05 02 03 V
//
// Class 04 (selector + state) is exhausted: only selector 01, the relay, does
// anything. Class 02 is the other command the STM8 honours, and only values 00
// and 01 have ever been sent. The value may be a channel selector rather than a
// state, which would make higher values the GPOs.
//
// V values 0..8, each with a clear off/on/off bracket so a meter reading can be
// attributed to one value.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_val ema_val.cpp -I/usr/include/qt4 \
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
#define TYPE_C02 5

static void send(EMAMain *ema, int value)
{
    _EMA_EVENT ev;
    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = TYPE_C02;        // offset 4 = type
    ((unsigned char *)&ev)[8] = (unsigned char)value;   // offset 8 = value
    ema->writeEvent(&ev);
    printf("    -> 55 05 02 03 %02x\n", value);
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
    int vmax = (argc > 1) ? atoi(argv[1]) : 8;
    double off_s = (argc > 2) ? atof(argv[2]) : 6.0;
    double on_s = (argc > 3) ? atof(argv[3]) : 12.0;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    printf("\n=== opening link ===\n");
    fflush(stdout);
    ema->open();
    send(ema, 0);
    hold(ema, off_s, "BASELINE");

    for (int v = 1; v <= vmax; v++) {
        printf("\n=== VALUE %02x : OFF ===\n", v);
        fflush(stdout);
        send(ema, 0);
        hold(ema, off_s, "off");

        printf("=== VALUE %02x : ON %.0fs  <<< WATCH THE METER ===\n", v, on_s);
        fflush(stdout);
        send(ema, v);
        hold(ema, on_s, "ON");
    }

    printf("\n=== back to 00 ===\n");
    fflush(stdout);
    send(ema, 0);
    hold(ema, off_s, "final");
    ema->close();
    printf("done\n");
    fflush(stdout);
    return 0;
}