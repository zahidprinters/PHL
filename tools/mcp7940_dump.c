/* mcp7940_dump.c - READ-ONLY MCP7940N RTC register dump over I2C.
 * Opens /dev/i2c-1, slave 0x6f, reads regs 0x00-0x1F via I2C_RDWR
 * (write register address, repeated-start read).  Writes NOTHING.
 * Decodes the time registers and runs a 1.3 s tick test on reg 0x00.
 */
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>

#define I2C_SLAVE        0x0703 /* refused with EBUSY when the kernel driver
                                 * owns the address (rtc-mcp7940n owns 0x6f) */
#define I2C_SLAVE_FORCE  0x0706 /* bypass the owner check; read-only here.
                                 * Transfers still serialise on the adapter
                                 * lock, so no interleaving with the driver. */
#define I2C_RDWR         0x0707
#define I2C_M_RD         0x0001

struct i2c_msg {
    unsigned short addr;
    unsigned short flags;
    unsigned short len;
    unsigned char *buf;
};

struct i2c_rdwr_ioctl_data {
    struct i2c_msg *msgs;
    unsigned int nmsgs;
};

static int reg_read(int fd, unsigned char reg, unsigned char *val)
{
    struct i2c_msg msgs[2];
    struct i2c_rdwr_ioctl_data rdwr;

    memset(msgs, 0, sizeof(msgs));
    msgs[0].addr = 0x6f;
    msgs[0].flags = 0;
    msgs[0].len = 1;
    msgs[0].buf = &reg;
    msgs[1].addr = 0x6f;
    msgs[1].flags = I2C_M_RD;
    msgs[1].len = 1;
    msgs[1].buf = val;
    rdwr.msgs = msgs;
    rdwr.nmsgs = 2;
    return ioctl(fd, I2C_RDWR, &rdwr);
}

int main(void)
{
    unsigned char r[32];
    unsigned char s1, s2;
    int i, fd, bad;

    fd = open("/dev/i2c-1", O_RDWR);
    if (fd < 0) { perror("open /dev/i2c-1"); return 1; }
    if (ioctl(fd, I2C_SLAVE_FORCE, 0x6f) < 0) { perror("I2C_SLAVE_FORCE 0x6f"); return 1; }

    bad = 0;
    printf("reg  hex\n");
    for (i = 0; i < 32; i++) {
        if (reg_read(fd, (unsigned char)i, &r[i]) < 0) {
            printf("%02x   --   (NAK - register reserved/absent)\n", i);
            r[i] = 0;
            bad = 1;
        } else {
            printf("%02x   %02x\n", i, r[i]);
        }
    }

    printf("\n-- decode --\n");
    printf("ST bit (reg0x00 bit7, oscillator run): %s\n",
           (r[0] & 0x80) ? "RUNNING (1)" : "STOPPED (0) <-- clock does not tick");
    printf("seconds : %02x (BCD)\n", r[0] & 0x7f);
    printf("minutes : %02x (BCD)\n", r[1] & 0x7f);
    printf("hours   : %02x (BCD, 12/24 bit=%d)\n", r[2] & 0x3f, (r[2] >> 6) & 1);
    printf("dow     : %02x   mday: %02x   month: %02x   year: %02x\n",
           r[3], r[4], r[5], r[6]);
    if ((r[4] & 0x3f) >= 1 && (r[4] & 0x3f) <= 31)
        printf("mday valid for rtc_valid_tm: yes\n");
    else
        printf("mday valid for rtc_valid_tm: NO (=%d) -> kernel returns EINVAL\n",
               r[4] & 0x3f);
    printf("control (0x07): %02x\n", r[7]);

    printf("\n-- tick test (1.3 s apart) --\n");
    s1 = 0;
    s2 = 0;
    if (reg_read(fd, 0x00, &s1) >= 0) {
        usleep(1300000);
        if (reg_read(fd, 0x00, &s2) < 0)
            s2 = 0xff;
        printf("reg0x00: %02x -> %02x : %s\n", s1, s2,
               ((s1 & 0x7f) != (s2 & 0x7f)) ? "CHANGING (clock is running)"
                                             : "UNCHANGED (clock stopped/stuck)");
    } else {
        printf("could not re-read reg 0x00\n");
    }
    close(fd);
    return bad;
}
