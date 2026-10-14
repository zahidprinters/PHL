// Drive the class-04 command: 55 05 04 <b53> <b54>
//
// Frame recovered from CMIMIRDemo's own writeEvent call at 0x14bb8, which sets
// struct offset 53 -> frame byte 3 and offset 54 -> frame byte 4. This is the
// first command we would transmit that we did not invent by guessing.
//
//   OFF : type 32, b53=0, b54=0   ->  55 05 04 00 00
//   ON  : type 32, b53=1, b54=1   ->  55 05 04 01 01
//
// Long phases, because the operator is watching a meter and an LED, not a
// terminal.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_c04 ema_c04.cpp -I/usr/include/qt4 \
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

static void send(EMAMain *ema, int b53, int b54)
{
    _EMA_EVENT ev;
    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = TYPE_C04;          // offset 4 = type
    ((unsigned char *)&ev)[53] = (unsigned char)b53;
    ((unsigned char *)&ev)[54] = (unsigned char)b54;
    ema->writeEvent(&ev);
    printf("    sent class04 b53=%d b54=%d\n", b53, b54);
    fflush(stdout);
}

static void hold(EMAMain *ema, double seconds, const char *label)
{
    long ticks = (long)(seconds * 10);
    printf("    [%s] %.0fs - watch the meter and the LED\n", label, seconds);
    fflush(stdout);
    for (long i = 0; i < ticks; i++) {
        QCoreApplication::processEvents(QEventLoop::AllEvents, 50);
        ema->readEvent();
        usleep(100000);
    }
}

int main(int argc, char **argv)
{
    double t_base = (argc > 1) ? atof(argv[1]) : 20;
    double t_on = (argc > 2) ? atof(argv[2]) : 60;
    double t_off = (argc > 3) ? atof(argv[3]) : 15;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    printf("\n=== PHASE 1: baseline OFF %.0fs ===\n", t_base);
    fflush(stdout);
    ema->open();
    send(ema, 0, 0);
    hold(ema, t_base, "BASELINE");

    printf("\n=== PHASE 2: ON 55 05 04 01 01  %.0fs ===\n", t_on);
    fflush(stdout);
    send(ema, 1, 1);
    hold(ema, t_on, "ON");

    printf("\n=== PHASE 3: OFF %.0fs ===\n", t_off);
    fflush(stdout);
    send(ema, 0, 0);
    hold(ema, t_off, "OFF");

    ema->close();
    printf("\ndone\n");
    fflush(stdout);
    return 0;
}