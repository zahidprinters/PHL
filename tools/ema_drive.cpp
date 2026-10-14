// Drive one GPO test pulse on the real hardware, with long readable phases.
//
// The command was recovered with writes SWALLOWED (nullwrite.c), so this is the
// first time a write frame actually reaches the STM8. Structure, all previously
// proven by observation rather than guessed:
//
//     _EMA_EVENT  offset +4 = event type,  offset +8 = value
//     type 5, value 1  ->  frame 55 05 02 03 01   (ON)
//     type 5, value 0  ->  frame 55 05 02 03 00   (OFF)
//
// Which output op 03 actually selects -- OUT1, OUT2, or the relay -- is not yet
// known. That is what this run measures, with a meter on the connector.
//
// Phases are long on purpose: the operator is watching a multimeter, not a
// terminal, so the ON window has to be human-sized.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_drive ema_drive.cpp -I/usr/include/qt4 \
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
#define TYPE_OFF 5

// Pump the Qt event loop so the library's read path stays alive, and report
// anything the STM8 sends back while we wait.
static void hold(EMAMain *ema, double seconds, const char *label)
{
    int chunks = 0;
    printf("    [%s] %.0fs - watch the meter\n", label, seconds);
    fflush(stdout);
    long ticks = (long)(seconds * 10);
    for (long i = 0; i < ticks; i++) {
        QCoreApplication::processEvents(QEventLoop::AllEvents, 50);
        if (ema->readEvent() != 0)
            chunks++;
        usleep(100000);
    }
    printf("    [%s] done (%d read events)\n", label, chunks);
    fflush(stdout);
}

static void send_type(EMAMain *ema, int type, int value)
{
    _EMA_EVENT ev;
    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = (unsigned int)type;  // byte offset 4 = type
    ((unsigned char *)&ev)[8] = (unsigned char)value;  // byte offset 8 = value
    ema->writeEvent(&ev);
    printf("    sent type=%d value=%d\n", type, value);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    // ./ema_drive [baseline_s] [on_s] [off_s] [type]
    // Phase lengths and the event type are arguments so a re-run needs no
    // rebuild. type 5 -> op 03, types 6..15 -> op 04 (from the swallowed sweep).
    double t_base = (argc > 1) ? atof(argv[1]) : 12;
    double t_on = (argc > 2) ? atof(argv[2]) : 15;
    double t_off = (argc > 3) ? atof(argv[3]) : 8;
    int type = (argc > 4) ? atoi(argv[4]) : TYPE_OFF;
    // type < 0 selects the parade: every candidate type in turn, so a single
    // watch of the connector (or an LED) reveals WHICH type drives it.
    bool parade = (type < 0);

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) {
        printf("calloc failed\n");
        return 2;
    }
    EMAMain *ema = new (mem) EMAMain();

    printf("\n=== PHASE 1: baseline (OFF) %.0fs, type=%d ===\n", t_base, type);
    fflush(stdout);
    ema->open();
    printf("    isOpen=%d\n", (int)ema->isOpen());
    fflush(stdout);
    send_type(ema, type, 0);
    hold(ema, t_base, "BASELINE");

    if (parade) {
        // Each type: 2s dark, 5s ON, 1s dark. The marker lines in this log are
        // the timeline the operator matches against what they saw on the
        // connector, so "it moved during type 9" identifies the command.
        for (int t = 5; t <= 15; t++) {
            printf("\n=== PARADE type=%d : ON for %.0fs ===\n", t, t_on);
            fflush(stdout);
            send_type(ema, t, 0);
            hold(ema, 2, "pre");
            send_type(ema, t, 1);
            hold(ema, t_on, "ON");
            send_type(ema, t, 0);
            hold(ema, 1, "post");
        }
        printf("\n=== parade done ===\n");
        fflush(stdout);
        ema->close();
        printf("done\n");
        fflush(stdout);
        return 0;
    }

    printf("\n=== PHASE 2: ON %.0fs ===\n", t_on);
    fflush(stdout);
    send_type(ema, type, 1);
    hold(ema, t_on, "ON");

    printf("\n=== PHASE 3: OFF %.0fs ===\n", t_off);
    fflush(stdout);
    send_type(ema, type, 0);
    hold(ema, t_off, "OFF");

    printf("\n=== closing link ===\n");
    fflush(stdout);
    ema->close();
    printf("done\n");
    fflush(stdout);
    return 0;
}