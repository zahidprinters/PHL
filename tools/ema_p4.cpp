// Find the struct offsets that populate class-03 payload bytes 4-7.
//
// Established so far:
//   type 17 -> 55 0a 03 01 00 00 00 00 01 00   closes OUT1
//   type 19 -> 55 0a 03 01 00 00 00 00 01 01   does NOT release it
//
// In every class-03 frame, payload bytes 4-7 are 00 00 00 00 -- the only fields
// no event type ever fills. Those are almost certainly where the real output
// and state parameters live, which is why the release frame does nothing: it
// is incomplete.
//
// Method: pin the type, then set ONE struct byte at a time to a distinctive
// value and look for payload bytes 4-7 (or any byte) to change. That maps
// offset -> frame position in one pass. This is exactly the technique that
// found offsets 53/54 for class 04.
//
// NOTHING IS TRANSMITTED. Run under nullwrite.so, which captures and swallows
// every write, so this is zero risk to the board.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_p4 ema_p4.cpp -I/usr/include/qt4 \
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
#define PROBE_VAL 0x77      /* distinctive, so a moved byte is obvious */
#define PIN_TYPE 19         /* the release frame: it is the one that does not work */

int main(int argc, char **argv)
{
    int lo = (argc > 1) ? atoi(argv[1]) : 0;
    int hi = (argc > 2) ? atoi(argv[2]) : 200;

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    unsigned char *ev = (unsigned char *)calloc(1, EVSIZE);
    if (!ev) { printf("calloc failed\n"); return 2; }

    printf("[open]\n");
    fflush(stdout);
    ema->open();

    printf("@@BASE type=%d, nothing else set\n", PIN_TYPE);
    fflush(stdout);
    memset(ev, 0, EVSIZE);
    ((unsigned int *)ev)[1] = PIN_TYPE;
    ema->writeEvent((_EMA_EVENT *)ev);

    for (int off = lo; off <= hi; off++) {
        memset(ev, 0, EVSIZE);
        ((unsigned int *)ev)[1] = PIN_TYPE;      // type stays pinned
        ((unsigned char *)ev)[off] = PROBE_VAL;  // the byte under test
        printf("@@OFF %d\n", off);
        fflush(stdout);
        ema->writeEvent((_EMA_EVENT *)ev);
    }

    printf("@@END\n");
    fflush(stdout);
    ema->close();
    return 0;
}