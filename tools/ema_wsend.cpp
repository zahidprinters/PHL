// Transmit a Wiegand card on W-OUT — the first live use of the WRITE handshake.
//
// Sequence (decoded 2026-10-13 from checkWriteEvent, see
// docs/raw/libemaLib-jumptable.md):
//   1. open()            -> 55 04 01 01
//   2. SET_CONFIG (type 4) seeds the libemaLib session (this+490 = ev+10)
//        -> 55 0b 02 02 <port> <bits 2B> <f12 2B> <f14 2B>
//   3. WRITE_DATA (type 3) requires ev+10 == session token
//        -> 55 (n+7) 02 01 <port> <bits 2B> <card nB>,  n = ceil(bits/8)
//   4. close()           -> 55 04 01 00  (also zeroes the session fields)
//
// ev+8 = 1 or 2 selects the Wiegand port. Both ports and both pins (DATA0,
// DATA1) click-tested live 2026-10-14 — all work; the two pins are one channel
// (0-bits → DATA0, 1-bits → DATA1), not independent outputs.
// f12/f14 (struct +12/+14) are timing parameters: the library only checks
// 1..50000 with f12 < f14; units are NOT decoded, 100/1000 are plausible
// pulse/gap values (us) — see the "semantics unknown" note in the output.
//
// Every call's return value is checked: writeEvent returns checkWriteEvent's
// error code (-16 no session, -17 token mismatch, -18..-20 range checks,
// -24 ev+8 not in {1,2}; -8 serial write failed), so a refused frame shows
// up here instead of silently doing nothing.
//
// Build (on the board):
//   g++ -std=c++0x -O0 -o ema_wsend ema_wsend.cpp -I/usr/include/qt4 \
//       -I/usr/include/qt4/QtCore -L/usr/local/lib \
//       -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread
//
// Zero-risk check first (nothing reaches the STM8):
//   LD_PRELOAD=./nullwrite.so ./ema_wsend 2 24 AAAAAA 2 300
// Live (LEDs on W-OUT should flash with every card):
//   LD_PRELOAD=./opentrace.so ./ema_wsend 2 24 AAAAAA 30 700
//
// W-OUT pins are OPEN-COLLECTOR (verified on hardware 2026-10-13): an LED must
// be wired +12V -> 1k -> LED -> pin (lights on each pull-low). pin -> 1k -> LED
// -> GND NEVER lights. Idle is LOW after boot, released (high-Z) after close.
//
// 24 bits / 0xAAAAAA is the default card: exactly 3 bytes, alternating 1s
// and 0s, so BOTH data lines pulse regardless of bit-packing direction.

#include <QCoreApplication>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <unistd.h>

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
    int writeEvent(_EMA_EVENT *evt);   // real signature returns the error code
};

#define TYPE_WSET  4
#define TYPE_WSEND 3

// One SET_CONFIG + WRITE_DATA pair. Returns 0 or the serialiser's error code.
static int send_card(EMAMain *ema, int port, unsigned int bits,
                     unsigned long cardv, unsigned int f12, unsigned int f14)
{
    _EMA_EVENT ev;
    unsigned int n = (bits + 7) / 8;    // same formula as the serialiser
    unsigned int i;
    int rc;

    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = TYPE_WSET;                // +4  type
    ((unsigned char *)&ev)[8]  = (unsigned char)port;    // +8  port 1|2
    ((unsigned char *)&ev)[10] = (unsigned char)(bits & 0xff);
    ((unsigned char *)&ev)[11] = (unsigned char)(bits >> 8);
    ((unsigned char *)&ev)[12] = (unsigned char)(f12 & 0xff);
    ((unsigned char *)&ev)[13] = (unsigned char)(f12 >> 8);
    ((unsigned char *)&ev)[14] = (unsigned char)(f14 & 0xff);
    ((unsigned char *)&ev)[15] = (unsigned char)(f14 >> 8);
    rc = ema->writeEvent(&ev);
    if (rc != 0) {
        printf("  SET_CONFIG refused: %d\n", rc);
        return rc;
    }

    memset(&ev, 0, sizeof ev);
    ((unsigned int *)&ev)[1] = TYPE_WSEND;               // +4  type
    ((unsigned char *)&ev)[8]  = (unsigned char)port;
    ((unsigned char *)&ev)[10] = (unsigned char)(bits & 0xff);
    ((unsigned char *)&ev)[11] = (unsigned char)(bits >> 8);
    // Card big-endian into offsets 16.., only the n bytes the serialiser
    // will read — the STM8's bit-order preference is unknown, so the test
    // card 0xAAAAAA alternates bits either way and blinks both lines.
    for (i = 0; i < n; i++)
        ((unsigned char *)&ev)[16 + i] =
            (unsigned char)((cardv >> (8 * (n - 1 - i))) & 0xff);
    rc = ema->writeEvent(&ev);
    if (rc != 0)
        printf("  WRITE_DATA refused: %d\n", rc);
    return rc;
}

int main(int argc, char **argv)
{
    // ./ema_wsend <port 1|2> <bits 1..32> <card hex 4B> [count] [gap_ms]
    //             [f12] [f14]
    int port = (argc > 1) ? atoi(argv[1]) : 2;
    unsigned int bits = (argc > 2) ? (unsigned int)atoi(argv[2]) : 24;
    unsigned long cardv = (argc > 3) ? strtoul(argv[3], 0, 16) : 0xAAAAAAUL;
    int count = (argc > 4) ? atoi(argv[4]) : 30;
    int gap_ms = (argc > 5) ? atoi(argv[5]) : 700;
    unsigned int f12 = (argc > 6) ? (unsigned int)atoi(argv[6]) : 100;
    unsigned int f14 = (argc > 7) ? (unsigned int)atoi(argv[7]) : 1000;

    if (port != 1 && port != 2) { printf("port must be 1 or 2\n"); return 2; }
    // The serialiser sends ceil(bits/8) bytes read from struct offsets 16..19,
    // so more than 32 bits would run past the card this tool supplies.
    if (bits < 1 || bits > 32)  { printf("bits must be 1..32\n"); return 2; }
    if (f12 < 1 || f12 >= f14 || f14 > 50000) {
        printf("need 1 <= f12 < f14 <= 50000\n"); return 2;
    }

    QCoreApplication app(argc, argv);

    void *mem = calloc(1, 256 * 1024);
    if (!mem) { printf("calloc failed\n"); return 2; }
    EMAMain *ema = new (mem) EMAMain();

    printf("=== opening link ===\n"); fflush(stdout);
    ema->open();
    printf("    isOpen=%d\n", (int)ema->isOpen());

    printf("=== Wiegand transmit: port=%d bits=%u card=%08lx x%d every %dms ===\n",
           port, bits, cardv, count, gap_ms);
    printf("    (timing f12=%u f14=%u — range-checked only, units unknown)\n",
           f12, f14);
    printf("    WATCH THE LEDs: each card = a burst of ~100us pulses\n");
    fflush(stdout);

    int fails = 0;
    for (int i = 0; i < count; i++) {
        int rc = send_card(ema, port, bits, cardv, f12, f14);
        if (rc != 0) fails++;
        printf("  card %2d/%d rc=%d\n", i + 1, count, rc); fflush(stdout);
        // No readEvent() here: it blocks forever when the STM8 sends no reply
        // (the property that keeps this lib out of the TUI). Whatever arrives
        // just sits in the tty input buffer — harmless for this test.
        QCoreApplication::processEvents(QEventLoop::AllEvents, 40);
        usleep(gap_ms * 1000);
    }

    printf("=== closing link (%d refusals) ===\n", fails); fflush(stdout);
    ema->close();
    printf("done\n");
    fflush(stdout);
    return fails ? 1 : 0;
}