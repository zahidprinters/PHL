// Enumerate the class-03 frames for event types 21..40. NOTHING IS TRANSMITTED.
//
// Runs under nullwrite.so: every frame is captured and swallowed, so this is a
// pure read of what the serialiser produces.
//
// Why: types 17-20 gave 55 0a 03 01 00 00 00 00 XX YY with
//     17 -> ...01 00   (OUT1 closed)
//     18 -> ...00 01   (OUT2 released)
//     19 -> ...01 01   (OUT1 released)
// and no type yet produces ...00 00 (OUT2 closed). If the family pairs
// closed/released per output, that frame must exist further along the type
// range -- which was only ever swept as far as 20.
//
// If a ...00 00 frame exists, the GPO command set is complete and purely
// type-driven, with the struct offsets ignored. If none appears, class 03 is
// probably a query family and the GPO writes live elsewhere.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_tscan ema_tscan.cpp -I/usr/include/qt4 \
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

int main(int argc, char **argv)
{
    int lo = (argc > 1) ? atoi(argv[1]) : 21;
    int hi = (argc > 2) ? atoi(argv[2]) : 40;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    unsigned char *ev = (unsigned char *)calloc(1, EVSIZE);
    if (!ev) { printf("calloc failed\n"); return 2; }

    printf("[open]\n");
    fflush(stdout);
    ema->open();

    for (int t = lo; t <= hi; t++) {
        memset(ev, 0, EVSIZE);
        ((unsigned int *)ev)[1] = (unsigned int)t;   // offset 4 = type
        printf("@@TYPE %d\n", t);
        fflush(stdout);
        ema->writeEvent((_EMA_EVENT *)ev);
    }

    printf("@@END\n");
    fflush(stdout);
    ema->close();
    return 0;
}