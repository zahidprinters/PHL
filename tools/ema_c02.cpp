// Drive the class-02 write family: 55 05 02 04 <value>
//
// The event enum, recovered from the EMA_EVENT_TYPE_* string order in
// CMIMIRDemo, is 0-indexed:
//
//   0 CLOSE   1 OPEN
//   2..6 WIEGAND_READ_DATA / WRITE_DATA / SET_CONFIG / GET_CONFIG / AUTO_DETECT
//   7 GPI12_READ
//   8 GPO1_WRITE     9 GPO2_WRITE     10 GPO12_WRITE     11 RELAY_WRITE
//
// A type sweep showed types 6-15 ALL emit the same frame with the value byte
// zero: 55 05 02 04 00. That means types 8, 9, 10 and 11 -- the GPO and relay
// writes -- are in that group, and the ONLY thing distinguishing them is the
// value byte, which was never varied for this family.
//
// For class 02 the value lives at struct offset 8. (Offsets 53/54 are ignored
// here -- those are class 04 fields. Getting that wrong is what made an earlier
// release attempt silently re-send the close frame.)
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_c02 ema_c02.cpp -I/usr/include/qt4 \
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
    ((unsigned int *)&ev)[1] = (unsigned int)type;      // offset 4 = type
    ((unsigned char *)&ev)[8] = (unsigned char)value;   // offset 8 = value
    ema->writeEvent(&ev);
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
    // ./ema_c02 <type> <value> <seconds>
    int type = (argc > 1) ? atoi(argv[1]) : 8;
    int value = (argc > 2) ? atoi(argv[2]) : 1;
    double secs = (argc > 3) ? atof(argv[3]) : 25.0;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    printf("\n=== opening link ===\n");
    fflush(stdout);
    ema->open();
    printf("=== type %d (GPO guess) value %d, %.0fs ===\n", type, value, secs);
    printf("    expected frame: 55 05 02 04 %02x\n", value);
    fflush(stdout);

    long ticks = (long)(secs * 2);
    for (long i = 0; i < ticks; i++) {
        send(ema, type, value);
        QCoreApplication::processEvents(QEventLoop::AllEvents, 40);
        ema->readEvent();
        usleep(500000);
    }
    printf("\n=== value 0 (restore) ===\n");
    fflush(stdout);
    send(ema, type, 0);
    hold(ema, 3, "restore");
    ema->close();
    printf("done\n");
    fflush(stdout);
    return 0;
}