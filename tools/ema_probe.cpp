// Probe for Daikin's libemaLib EMA protocol layer (SoC <-> STM8S207 link).
//
// v2: the first run proved the link is /dev/ttySAC0 and that open() succeeds,
// but readEvent() returned -9 every time because libemaLib delivers serial
// traffic through a QSocketNotifier. A notifier only fires while a Qt event
// loop is running, and v1 never started one ("QSocketNotifier: Can only be
// used with threads started with QThread").
//
// Fix: construct a QCoreApplication and pump it with processEvents(). That
// needs no moc/QObject subclass, so this stays a single translation unit.
//
// Build (on the board):
//   g++ -std=c++11 -O0 -g -o ema_probe ema_probe.cpp \
//       -L/usr/local/lib -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread

#include <QCoreApplication>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <new>
#include <unistd.h>
#include <dirent.h>
#include <termios.h>

class EMAMain {
public:
    EMAMain();
    ~EMAMain();
    bool open();
    void close();
    bool isOpen();
    int readEvent();
    void writeEvent(void *evt);
};

// Find the serial fd the library opened, then report its line settings.
// The library picks the baud internally, so this is how we learn it.
static int find_serial_fd(void)
{
    DIR *d = opendir("/proc/self/fd");
    if (!d)
        return -1;
    struct dirent *e;
    int found = -1;
    while ((e = readdir(d)) != 0 && found < 0) {
        if (e->d_name[0] == '.')
            continue;
        char link[64], target[512];
        snprintf(link, sizeof link, "/proc/self/fd/%s", e->d_name);
        ssize_t n = readlink(link, target, sizeof target - 1);
        if (n <= 0)
            continue;
        target[n] = 0;
        if (strstr(target, "/dev/tty"))
            found = atoi(e->d_name);
    }
    closedir(d);
    return found;
}

// Report any serial fd the library managed to open, so we learn the port.
static void dump_serial_fds(const char *when)
{
    int fd = find_serial_fd();
    if (fd < 0) {
        printf("    -- no serial fd open %s --\n", when);
        fflush(stdout);
        return;
    }

    char link[64], target[512];
    snprintf(link, sizeof link, "/proc/self/fd/%d", fd);
    ssize_t n = readlink(link, target, sizeof target - 1);
    if (n > 0)
        target[n] = 0;

    printf("    -- serial fds %s --\n", when);
    printf("    fd %d -> %s\n", fd, target);

    struct termios t;
    if (tcgetattr(fd, &t) == 0) {
        speed_t is = cfgetispeed(&t), os = cfgetospeed(&t);
        printf("    baud in=%lu out=%lu  (B%d00)\n",
               (unsigned long)is, (unsigned long)os, (int)is / 100);
        printf("    bits=%c stop=%c parity=%c\n",
               t.c_cflag & CS8 ? '8' : '7',
               t.c_cflag & CSTOPB ? '2' : '1',
               (t.c_cflag & PARENB) ? ((t.c_cflag & PARODD) ? 'O' : 'E') : 'N');
        printf("    raw mode: %s\n", (t.c_lflag & ICANON) ? "no" : "yes");
    } else {
        printf("    tcgetattr failed\n");
    }
    fflush(stdout);
}

int main(int argc, char **argv)
{
    // Provides the event loop the QSocketNotifier needs to deliver reads.
    QCoreApplication app(argc, argv);

    // EMAMain derives from QObject and embeds a QextSerialPort plus a QQueue,
    // so its true size is unknown. Over-allocate rather than guess a layout:
    // 256 KB is free on a 1 GB board and cannot under-run.
    void *mem = calloc(1, 256 * 1024);
    if (!mem) {
        printf("calloc failed\n");
        return 2;
    }
    EMAMain *ema = new (mem) EMAMain();

    printf("[1] isOpen() before open = %d\n", (int)ema->isOpen());
    fflush(stdout);

    printf("[2] calling open()\n");
    fflush(stdout);
    bool r = ema->open();
    printf("[3] open() returned %d\n", (int)r);
    printf("[4] isOpen() after open  = %d\n", (int)ema->isOpen());
    fflush(stdout);
    dump_serial_fds("after open");

    bool live = ema->isOpen();
    if (live) {
        // Pump Qt events, then drain whatever the library has queued.
        // Nonzero return means an event actually arrived.
        printf("[5] polling readEvent() with the Qt event loop running\n");
        int got = 0;
        for (int i = 0; i < 40; i++) {
            QCoreApplication::processEvents(QEventLoop::AllEvents, 25);
            int rc = ema->readEvent();
            if (rc != 0) {
                printf("    readEvent[%02d] -> %d   <-- EVENT\n", i, rc);
                got++;
            } else if (i % 8 == 0) {
                printf("    readEvent[%02d] -> 0 (idle)\n", i);
            }
            fflush(stdout);
            usleep(200000);
        }
        printf("[6] events received: %d\n", got);

        printf("[7] closing\n");
        fflush(stdout);
        ema->close();
        printf("[8] closed, isOpen = %d\n", (int)ema->isOpen());
        fflush(stdout);
    }

    printf("RESULT: %s\n", live ? "LINK IS LIVE" : "LINK DID NOT OPEN");
    fflush(stdout);
    return live ? 0 : 1;
}