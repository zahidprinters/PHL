/* LD_PRELOAD shim: log every open() the target makes, and every byte that
 * crosses the serial fd afterwards.
 *
 * The board has no strace, and the question is "how does libemaLib talk to the
 * STM8?". Intercepting open/open64 finds the port; intercepting read/write on
 * that port shows the EMA framing itself, produced by the vendor code. That
 * is how we learn the protocol without guessing a struct layout.
 *
 * Only the fd opened from a /dev/tty* path is traced, so Qt and libc noise is
 * ignored. Writes are dumped in hex; reads report how many bytes came back.
 *
 * Build: gcc -shared -fPIC -O0 -o opentrace.so opentrace.c -ldl
 */

#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdarg.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

static int serial_fd = -1;

static void note(const char *fn, const char *path)
{
    if (path && (strstr(path, "tty") || strstr(path, "pts")))
        fprintf(stderr, "[TRACE] %s(\"%s\")\n", fn, path);
}

static void hexdump(const char *tag, const void *buf, ssize_t n)
{
    const unsigned char *p = (const unsigned char *)buf;
    ssize_t i;

    fprintf(stderr, "[%s] %zd bytes:", tag, n);
    /* C89: the loop variable is declared here, not inside the for. */
    for (i = 0; i < n; i++)
        fprintf(stderr, " %02x", p[i]);
    fputc('\n', stderr);
}

static int is_traced(int fd)
{
    return fd >= 0 && fd == serial_fd;
}

int open(const char *path, int flags, ...)
{
    static int (*real)(const char *, int, ...) = NULL;
    if (!real)
        real = dlsym(RTLD_NEXT, "open");

    /* mode is only meaningful with O_CREAT, and is then the 4th vararg. */
    mode_t mode = 0;
    if (flags & O_CREAT) {
        va_list ap;
        va_start(ap, flags);
        mode = va_arg(ap, mode_t);
        va_end(ap);
    }

    note("open", path);
    int fd = real(path, flags, mode);
    if (fd >= 0 && path && strstr(path, "tty"))
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
    if (fd >= 0 && path && strstr(path, "tty"))
        serial_fd = fd;
    return fd;
}

ssize_t write(int fd, const void *buf, size_t count)
{
    static ssize_t (*real)(int, const void *, size_t) = NULL;
    if (!real)
        real = dlsym(RTLD_NEXT, "write");

    if (is_traced(fd) && count && count < 4096)
        hexdump("TX", buf, (ssize_t)count);

    return real(fd, buf, count);
}

ssize_t read(int fd, void *buf, size_t count)
{
    static ssize_t (*real)(int, void *, size_t) = NULL;
    if (!real)
        real = dlsym(RTLD_NEXT, "read");

    ssize_t n = real(fd, buf, count);

    if (is_traced(fd) && n > 0 && n < 4096)
        hexdump("RX", buf, n);

    return n;
}