// Hold a GPO state by keeping the session alive and re-asserting it.
//
// Decoded from the class-03 family:
//     55 0a 03 01 00 00 00 00 01 00   -> contact CLOSED   (LED lit, ~1.7 mV)
//     55 0a 03 01 00 00 00 00 01 01   -> contact RELEASED (LED dark, line high)
//
// And the board READS IT BACK: byte 8 of the status frame flipped 00 -> 01 when
// we released it, so the effect is verifiable without a meter.
//
// The catch found on the bench: the change is MOMENTARY. Closing the link puts
// the output back to closed, which is why an earlier run appeared to do nothing
// -- the command worked, then was undone the moment the session ended. So the
// desired state has to be re-sent continuously for as long as it should hold.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_gpo ema_gpo.cpp -I/usr/include/qt4 \
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
#define TYPE_C03 19          /* the frame that releases the contact */

// 0 = closed, 1 = released. This is the LAST byte of the frame.
static void send(EMAMain *ema, int released)
{
    _EMA_EVENT ev;
    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = TYPE_C03;                    // offset 4 = type
    ((unsigned char *)&ev)[53] = 1;                         // selector
    ((unsigned char *)&ev)[54] = (unsigned char)released;  // state
    ema->writeEvent(&ev);
}

int main(int argc, char **argv)
{
    // ./ema_gpo <released> <seconds> [output] [type]
    //   released : 0 = closed, 1 = released  (struct offset 54 -> frame byte 9)
    //   output   : 1 = OUT1, 0 = OUT2        (struct offset 53 -> frame byte 8)
    //   type     : the event type that produced this frame shape (17..20)
    //
    // Decoded frame shape:
    //     55 0a 03 01 00 00 00 00 | OUTPUT | STATE
    //   b8 selects the output, b9 is the contact state.
    int released = (argc > 1) ? atoi(argv[1]) : 1;
    double secs = (argc > 2) ? atof(argv[2]) : 30.0;
    int output = (argc > 3) ? atoi(argv[3]) : 1;
    int type = (argc > 4) ? atoi(argv[4]) : 17;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    printf("\n=== opening link ===\n");
    fflush(stdout);
    ema->open();
    printf("    isOpen=%d\n", (int)ema->isOpen());
    printf("=== holding output=%d %s for %.0fs ===\n", output,
           released ? "RELEASED" : "CLOSED", secs);
    printf("    frame: 55 0a 03 01 00 00 00 00 %02x %02x\n", output, released);
    printf("    expect OUT%d %s\n", output ? 1 : 2,
           released ? "floating" : "shorted to GND");
    fflush(stdout);

    long ticks = (long)(secs * 2);
    for (long i = 0; i < ticks; i++) {
        _EMA_EVENT ev;
        memset(&ev, 0, sizeof ev);
        ((unsigned int *)&ev)[1] = (unsigned int)type;            // offset 4
        ((unsigned char *)&ev)[53] = (unsigned char)output;      // offset 53 -> b8
        ((unsigned char *)&ev)[54] = (unsigned char)released;    // offset 54 -> b9
        ema->writeEvent(&ev);
        QCoreApplication::processEvents(QEventLoop::AllEvents, 40);
        ema->readEvent();
        usleep(500000);
    }
    printf("\n=== hold released, closing link ===\n");
    fflush(stdout);
    ema->close();
    printf("done\n");
    fflush(stdout);
    return 0;
}