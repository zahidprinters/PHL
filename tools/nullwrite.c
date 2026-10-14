/* LD_PRELOAD shim: record serial writes but SWALLOW them.
 *
 * Recovering the GPO frame format by trial and error on live hardware would mean
 * sending commands we do not understand to an HVAC controller that may switch a
 * relay. This removes that risk entirely.
 *
 * Every write() to the serial fd is captured and reported on stderr, and then
 * DISCARDED -- the real write() is never called. So libemaLib builds the frame
 * it intended to send, we read it, and the STM8 receives nothing at all.
 *
 * The open/close handshake bytes are swallowed too, so the STM8 never even sees
 * a session start. That is harmless for a format-discovery run: we only want to
 * know what the serialiser produces.
 *
 * Build: gcc -shared -fPIC -O0 -o nullwrite.so nullwrite.c -ldl
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdarg.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

static int serial_fd = -1;

/* Frame counter, so successive captures can be told apart in the log. */
static unsigned long frame_no = 0;

static int is_tty(const char *path)
{
    return path && strstr(path, "tty");
}

static void report(const void *buf, size_t n)
{
    const unsigned char *p = (const unsigned char *)buf;
    size_t i;

    frame_no++;
    fprintf(stderr, "[FRAME %lu] %d bytes:", frame_no, (int)n);
    for (i = 0; i < n && i < 128; i++)
        fprintf(stderr, " %02x", p[i]);
    fputc('\n', stderr);
    fflush(stderr);
}

static void note(const char *fn, const char *path)
{
    if (is_tty(path))
        fprintf(stderr, "[OPEN] %s(\"%s\")\n", fn, path);
}

int open(const char *path, int flags, ...)
{
    static int (*real)(const char *, int, ...) = NULL;
    if (!real)
        real = dlsym(RTLD_NEXT, "open");

    /* Mode is only present when O_CREAT is set, as the 4th vararg. */
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list ap;
        va_start(ap, flags);
        mode = va_arg(ap, mode_t);
        va_end(ap);
    }

    note("open", path);
    int fd = real(path, flags, mode);
    if (fd >= 0 && is_tty(path))
        serial_fd = fd;
    return fd;
}

int open64(const char *path, int flags, ...)
{
    static int (*real)(const char *, int, ...) = NULL;
    if (!real)
        real = dlsym(RTLD_NEXT, "open64");

    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list ap;
        va_start(ap, flags);
        mode = va_arg(ap, mode_t);
        va_end(ap);
    }

    note("open64", path);
    int fd = real(path, flags, mode);
    if (fd >= 0 && is_tty(path))
        serial_fd = fd;
    return fd;
}

/* The whole point: capture, then lie about success so the library carries on. */
ssize_t write(int fd, const void *buf, size_t count)
{
    static ssize_t (*real)(int, const void *, size_t) = NULL;
    if (!real)
        real = dlsym(RTLD_NEXT, "write");

    if (fd >= 0 && fd == serial_fd && count && count < 256) {
        report(buf, count);
        return (ssize_t)count;        /* swallowed: real() never called */
    }
    return real(fd, buf, count);
}

ssize_t read(int fd, void *buf, size_t count)
{
    static ssize_t (*real)(int, void *, size_t) = NULL;
    if (!real)
        real = dlsym(RTLD_NEXT, "read");

    ssize_t n = real(fd, buf, count);
    /* No STM8 will reply (its bytes were never sent), so reads just time out. */
    (void)buf;
    return n;
}