// Drive the class-03 command family - the one class we discovered but never sent.
//
// From the swallowed sweep, event types 17..20 emit 10-byte frames:
//
//   type 17 -> 55 0a 03 01 00 00 00 00 01 01
//   type 18 -> 55 0a 03 01 00 00 00 00 00 01
//   type 19 -> 55 0a 03 01 00 00 00 00 01 01
//   type 20 -> 55 0a 03 01 00 00 00 00 01 01
//
// Compare the status frame the STM8 sends us:
//
//   55 0a 03 00 01 01 BB RR 00 00
//              ^^ byte 3 is 00 on the status frame and 01 on these requests,
//                 i.e. byte 3 looks like a direction flag.
//
// Same length, same class, same shape as the status frame - which is what a
// GPO read/write command would look like. The vendor enum lists GPO1_WRITE,
// GPO2_WRITE, GPO12_WRITE and GPI12_READ, so this family is the most likely home
// for the digital outputs.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_c03 ema_c03.cpp -I/usr/include/qt4 \
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

static void send(EMAMain *ema, int type, int value)
{
    _EMA_EVENT ev;
    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = (unsigned int)type;        // offset 4 = type
    ((unsigned char *)&ev)[8] = (unsigned char)value;     // offset 8 = value
    ema->writeEvent(&ev);
    printf("    -> type %d, value %d\n", type, value);
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
    // ./ema_c03 [type] [off_s] [on_s]
    // A single type is driven at a time, so a meter reading can be attributed
    // to one type rather than guessed from a parade.
    double off_s = (argc > 2) ? atof(argv[2]) : 10.0;
    double on_s = (argc > 3) ? atof(argv[3]) : 30.0;
    int only = (argc > 1) ? (int)strtol(argv[1], 0, 0) : 0;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    int types[4] = {17, 18, 19, 20};
    int first = only ? 0 : 1;
    int last = only ? 0 : 4;
    if (only) {
        types[0] = only;
    } else {
        for (int i = 0; i < 4; i++) types[i] = 17 + i;
    }

    printf("\n=== opening link ===\n");
    fflush(stdout);
    ema->open();
    send(ema, 17, 0);
    hold(ema, off_s, "BASELINE");

    for (int i = first; i < (only ? 1 : 4); i++) {
        int t = types[i];
        printf("\n=== TYPE %d : value 0 (%.0fs) ===\n", t, off_s);
        fflush(stdout);
        send(ema, t, 0);
        hold(ema, off_s, "zero");

        printf("=== TYPE %d : value 1 (%.0fs)  <<< WATCH THE METER ===\n",
               t, on_s);
        fflush(stdout);
        send(ema, t, 1);
        hold(ema, on_s, "ONE");
    }

    printf("\n=== releasing back to 0 ===\n");
    fflush(stdout);
    send(ema, types[0], 0);
    hold(ema, off_s, "final");
    ema->close();
    printf("done\n");
    fflush(stdout);
    return 0;
}