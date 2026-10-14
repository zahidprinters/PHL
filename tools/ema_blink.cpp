// Blink the relay, so it can be confirmed by ear and by eye.
//
// Class 04 is the actuator command:  55 | 05 | 04 | b53 | b54
// Driving b53=1 b54=1 was observed to actuate the RELAY (OUT1 and OUT2 showed
// no change). Byte 3 selects what is being driven and byte 4 appears to be the
// state, so a blink keeps the selector at 1 and toggles only the state:
//
//     ON   ->  55 05 04 01 01
//     OFF  ->  55 05 04 01 00
//
// The OFF frame keeps b53=1 on purpose. Zeroing both bytes (00 00) was the
// "baseline" used earlier, but for a clean on/off toggle the selector should stay
// put and only the state change.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_blink ema_blink.cpp -I/usr/include/qt4 \
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
    ((unsigned int *)&ev)[1] = TYPE_C04;      // offset 4  = type
    ((unsigned char *)&ev)[53] = (unsigned char)b53;
    ((unsigned char *)&ev)[54] = (unsigned char)b54;
    ema->writeEvent(&ev);
    printf("    -> 55 05 04 %02x %02x\n", b53, b54);
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
    int blinks = (argc > 1) ? atoi(argv[1]) : 8;
    double on_s = (argc > 2) ? atof(argv[2]) : 3.0;
    double off_s = (argc > 3) ? atof(argv[3]) : 3.0;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    printf("\n=== opening link ===\n");
    fflush(stdout);
    ema->open();
    printf("    isOpen=%d\n", (int)ema->isOpen());
    fflush(stdout);
    hold(ema, 3, "settle");

    for (int b = 1; b <= blinks; b++) {
        printf("\n=== BLINK %d of %d : ON ===\n", b, blinks);
        fflush(stdout);
        send(ema, 1, 1);
        hold(ema, on_s, "ON");

        printf("=== BLINK %d of %d : OFF ===\n", b, blinks);
        fflush(stdout);
        send(ema, 1, 0);
        hold(ema, off_s, "OFF");
    }

    printf("\n=== leaving relay OFF ===\n");
    fflush(stdout);
    send(ema, 1, 0);
    hold(ema, 2, "final");
    ema->close();
    printf("done\n");
    fflush(stdout);
    return 0;
}