# Architecture Map

The map, not a manual. **Start here** instead of reading the whole project.
Keep it short and accurate. If it is wrong, fix it before you trust it.

> Companion to `memory-bank/`: this file says what the code **is** (read to
> navigate). The memory bank says what we **decided and why** (read to
> continue). Do not duplicate decisions here.

Last updated: 2026-10-14

## Purpose
Know what this board is and get every peripheral on it working. The board is a
Daikin **CMIMIR / Intelligent Manager** HVAC controller: an Exynos 4412 running
Ubuntu Linaro, plus an STM8S207 that owns the industrial I/O. The SoC↔STM8 link
is found and the digital I/O is driven from Linux; the deliverable is the
peripheral checklist in `docs/BOARD.md`, worked down row by row.

## Stack
| Layer | Technology | Version |
|---|---|---|
| Tooling language | Python (this PC) | 3.11.9 |
| On-board tools | Python | **2.7** — `uart_*.py` / `i2c_scan.py` are python2 |
| Remote access | `paramiko` over SSH | - |
| Board OS | Ubuntu Linaro | `3.0.68 #11 SMP 2014 armv7l` |
| SoC | Samsung Exynos 4412 | 4× Cortex-A9, 2 online |
| RAM / ROM | 1 GB DDR / 8 GB eMMC (Hynix) | - |
| MCU | STM8S207 | owns the I/O; firmware a black box |

| SoC↔STM8 link | `/dev/ttySAC0` @ 115200 8N1 | status + ack frames; vendor `libemaLib` recovered by disassembly |
| Board UI | **PyQt4** (python2) | the only toolkit on this image — Tk/PySide/PyQt5 absent |
| Board desktop | **bare openbox 3.5** (lightdm root autologin) | appliance mode since 2026-10-12 — no panel/menu/wallpaper/status bar; session autostart = vino-server + EMA_Controls.sh only (`/etc/xdg/openbox/autostart`, plain shell); openbox.desktop wraps `dbus-launch --exit-with-session`; configs archived in `os/desktop/` |
| **HMI** | **Node-RED 1.3.7** on node v10.24.1 + custom vanilla-JS SPA | runs in an **Ubuntu 14.04 armhf chroot** at `/data/chroot14` (host glibc 2.15 too old; 16.04's glibc rejects kernel 3.0.68); http://192.168.100.127:1880 serves the SPA at `/` (httpStatic, repo `os/node-red/static/`), editor at `/red`, API `GET /api/state` + `POST /api/cmd` (locked); upstart job `/etc/init/nodered.conf` (repo: `os/node-red/`). node-red-dashboard REMOVED 2026-10-14 (tar backup on board) |

## Layout
| Path | Holds |
|---|---|
| `docs/BOARD.md` | **the deliverable** — identity, architecture, 18-row peripheral checklist |
| `docs/raw/` | verbatim command output backing every claim in `BOARD.md` |
| `docs/photos/` | board photos; readings taken from them live in `docs/raw/board-photos-raw.md` |
| `tools/board_*.py` | read-only SSH probes; run from this PC |
| `tools/uart_*.py`, `tools/i2c_scan.py` | python2, **run on the board** |
| `memory-bank/` | decisions and next steps across sessions |
| `archive/` | dead ends kept, not deleted — `board-oneoff-probes/` (incl. 8 probes moved there in the 2026-10-14 production pass: gui/ema-mining/gpio/rs485 sub-phase probes), `docs-superseded/`, `dynalite/`, `ecu30-android-usb/` |
| `os/` | permanent OS archive: eMMC backup, board scripts, `vendor-snapshot/` (CMITECH binaries, md5-verified), `node-red/` (upstart job + settings for the HMI), `desktop/` (appliance X-session config + the revoked fb-early splash experiment, kept as record) — see `os/README.md` |
| `temp/`, `logs/` | scratch and captures, gitignored. `temp/` is emptied on every production pass (last: 2026-10-14, 183 MB node tarball removed); `logs/` keeps the small raw captures, with `ema_cap_in1/2.log` tracked on purpose as evidence cited by `docs/BOARD.md` |

## Key modules
| Module | File | Responsibility |
|---|---|---|
| inventory | `tools/board_inventory.py` | 13-section read-only survey; `--out` writes `docs/raw/` |
| facts | `tools/board_facts.py` | the three open questions: real UARTs, native GMAC, EEPROMs |
| stm8 link | `tools/board_stm8_link.py` | hunts the SoC↔STM8 link; proved `/dev/ttySTM8` is a red herring |
| ssh | `tools/board_ssh.py` | quick shell-out for identity/os/disk/memory |
| sniff / tap | `tools/uart_sniff.py`, `tools/uart_tap.py` | passively read a UART; MITM a PTY to capture vendor frames |
| console | `tools/uart_console.py` | serial console capture/send |
| i2c scan | `tools/i2c_scan.py` | enumerate I2C addresses |
| **rs232 loopback** | `tools/rs232_loopback.py` | one-wire A/B test to name the RS232 UART; tx/rx counters as ground truth |
| **rs485 probe** | `tools/rs485_probe.py` | timed TX windows so a meter across D+/D− names the RS485 UART; single-port mode keeps the two ports separated in time |
| **link health** | `tools/link_health.py` | OPEN/CLOSE handshake; pass means the digital I/O is usable |
| **board UI** | `tools/ema_ui.py` | **EMA_Controls** — desktop app: input lamps, output buttons, relay; display follows the board's report, retries 3x |
| **GPO frame map** | `tools/ema_uimap.py`, `tools/ema_gap.py` | regression checks: replay every OUT1/OUT2 action against the hardware, PASS/FAIL each |

## Flow
1. Set `PHL_BOARD_PASS`, then run a `board_*.py` probe. Each opens one SSH
   session, runs a list of shell commands, prints `(stdout or stderr)` per
   section. **A section that throws is reported, never skipped silently** — a
   failed probe must not hide the other twelve.
2. `board_inventory.py --out docs\raw\BOARD-raw.md` persists the raw text;
   `docs/BOARD.md` is the interpretation written on top of it.
3. Findings are recorded as WORKS/BLOCKED rows in the `docs/BOARD.md` checklist.
   **Nothing is marked WORKS unless it was observed working.**
4. Protocol work: recover a frame (disassembly / swallowing shim / type scan),
   verify it from the STM8's own status or ack, add it to the frame map in
   `docs/BOARD.md`, then wire it into `ema_ui.py` behind a button whose display
   is driven by the board's report — never by the click.

## External dependencies
| What | Why | Failure looks like |
|---|---|---|
| `paramiko` | SSH from this PC to the board | `ModuleNotFoundError: paramiko` |
| `pyserial` | for the on-board `uart_*` tools | `ModuleNotFoundError: serial` |

## Decisions
- **2026-10-14 (5) - HMI screen-blank deployed to board; live path is inside the chroot.**
  Node-RED now runs in `chroot14`; `httpStatic: '/data/nodered/static/'` resolves
  (chroot-relative) to **`/data/chroot14/data/nodered/static/`** on the host — NOT
  `/data/nodered/static/` (the old note's path, which does not exist). Deploy the
  SPA there. Kiosk = `/etc/xdg/openbox/autostart` line 8 `firefox http://localhost:1880/`
  as root; **FF cache fully disabled** (`browser.cache.{disk,memory}.enable=false`), so
  no cache-busting on redeploy. Pre-deploy backup taken as `static.bak-20261014`.
- **2026-10-14 (4) - HMI screen-blank is frontend-only, on purpose.** The idle
  blank is a local display preference, not a hardware command, so it lives
  entirely in `static/` (black `#blanker` overlay) and is deliberately NOT
  gated by the controls lock — it works in v1 while hardware commands stay
  locked. Preference persists in `localStorage` (`hmi.blank`, seconds). A real
  backlight power-off would need `/api/cmd` -> board (DPMS/backlight API), the
  upgrade path once the logic workflow unlocks commands. Regression guard:
  `node tests/blank_check.js` (loads real `app.js` via `vm`, fake clock).
- **2026-10-14 - PRODUCTION TONE: development phase closed.** Everything that
  drives the board's hardware (protocol tools, frame recipes, raw evidence,
  flows, backups) stays as the frozen reference set; dev-phase debris is gone
  (temp/, zero-byte files, verified duplicates) and closed-question probes
  moved from `tools/` to `archive/board-oneoff-probes/`. From now on the only
  active work areas are **the screen (SPA) and Node-RED flows** — all hardware
  I/O goes through Node-RED. Git was re-initialized as the baseline (`*.img*`
  excluded — the eMMC backup is verified by its recorded `sha256_gz`, not by
  git). The board itself gets a matching cleanup pass.
- **2026-10-10 - Facts are re-measured, not remembered.** Every claim in
  `docs/BOARD.md` is backed by saved raw output in `docs/raw/`. Old notes
  drifted; the inventory is regenerated on demand.
- **2026-10-10 - Dead work is archived, never deleted.** `archive/` is one
  `Remove-Item` away and nothing was lost getting here.
- **2026-10-10 - Every probe is strictly read-only.** No writes, no register
  pokes, no ports opened, on a board with no display to recover through.
- **2026-10-10 - `/dev/ttySAC1` is excluded everywhere.** It is the kernel
  console; touching it can hang a headless board.
- **2026-10-10 - The SoC↔STM8 link is the next target.** It unblocks 6 of the 8
  BLOCKED peripherals at once, so it beats working them one at a time.
- **2026-10-10 - A send is never success.** The STM8 silently refuses some
  valid-looking frames (received, no ack, no action). Every actuation is
  confirmed from status/ack and retried; the UI does this by design.
- **2026-10-10 - The desktop UI shows the board's report, not the click.**
  Buttons queue commands; lamps/buttons flip only when the board confirms.
- **2026-10-11 - A negative control is part of the test.** The RS232 loopback
  only counts as proven because it was re-run with the wire removed and `rx`
  froze. A one-sided result cannot distinguish a real path from an artifact.
- **2026-10-11 - Same again for RS485.** `ttySAC2` moving from 0.646 V to
  220 mV means nothing on its own; it means something because `ttySAC3` was
  then run identically and did not move. Any measurement that changes a
  needle needs a run that should not change it.
- **2026-10-11 - Check the wire count before choosing a test.** The RS485
  jumper exercise was structurally impossible on a 2-terminal half-duplex
  connector; asking first would have saved five phases.

- **2026-10-11 - Slim the OS, do not upgrade it.** unity/ubuntu-desktop purged → LXDE (23 MB); the release stays precise (upgrade rejected the same day). Vendor binaries are archived hash-verified in `os/vendor-snapshot/` **before** deletion — "no camera work" is a decision, not data loss.

- **2026-10-11 - Node-RED goes in an armhf chroot, not on the host.** Host glibc 2.15 < 2.17 (node ≥ 8 needs it), and no armv7l-musl Node build exists. 16.04's glibc hard-rejects kernel 3.0.68 (`uname` check, armhf baseline ≥ 3.2), so the chroot is **Ubuntu 14.04** (glibc 2.19) with `libstdc++6` from xenial grafted in (`GLIBCXX_3.4.20`). Node-RED pinned to **1.3.7** — the last line that runs on node 10.

- **2026-10-12 - The desktop is an appliance, not a desktop.** Node-RED is the interface; the entire X session is bare openbox + vino + the EMA touchscreen UI — no panel, menu, wallpaper, or status bar. 1160→637 packages, rootfs 1.2G→776M. Every autoremove is gated behind a keep-list (`apt-mark manual`): vino stack (incl. libtelepathy-glib0), lightdm/openbox/xterm, dbus/x11, PyQt + pyserial (EMA + uart tools), NM/SSH/RDP, audio, fonts, toolchain.

## Gotchas
- **Never `rm -rf` a tree that still has bind mounts under it.** Bind mounts
  share the superblock, so `rm` reaches the *real* files — 2026-10-11 a cleanup
  of the abandoned 16.04 chroot walked into its `/dev` bind and **deleted host
  device nodes** (`/dev/null`, `/dev/ptmx`, …). The listener kept accepting but
  every new SSH session died before the banner (sshd's privsep child can no
  longer open `/dev/null`). `umount` every bind first, or reboot and delete
  after; `devtmpfs` rebuilds `/dev` at boot. Same trap for `/proc` and `/sys`.
- **SSH's exec environment has an empty PATH.** `board_run.py` commands land in
  a non-login shell with no PATH — anything invoked by bare name inside a
  `chroot …` needs an explicit `env PATH=/usr/local/node10/bin:/usr/bin:/bin`.
  Symptom: `xxx: not found` for a binary that exists.
- **Upstart `.conf` files uploaded from Windows keep CRLF** and fail with
  phantom errors (`mount point /data/chroot14/proc\r does not exist`).
  Convert LF first — and precise's `chroot` lives in `/usr/sbin`, so the job
  calls it bare or by that full path.
- **`/dev/ttySTM8` is a symlink to `/dev/pts/0`.** A pseudo-terminal, not a
  serial port, left over from an earlier capture. It talks to no chip.
- **`/dev/ttyS0..3` are phantoms** — 8250 stubs reporting `port:00000000 irq:0`.
  Only `/dev/ttySAC0..3` are real (`s5pv210-uart`).
- **No native Ethernet MAC exists in this kernel.** No `macb`/`dwmac`/`stmmac`,
  and no `ethernet@` node in the device tree at all. The only NIC is the LAN9512
  on USB. **Both RJ45 jacks are `eth0`** — a **KSZ8995XA 5-port switch** (seen in
  the board photos) sits between them and the LAN9512, so a second interface can
  never appear, by construction. Do not chase an `eth1`.
- **No GPIO userspace API exists.** `/sys/class/gpio` and `/dev/gpiochip*` are
  both absent, so `libgpiod`/`gpioget` cannot work. The missing half is the
  *kernel*, not the package.
- **The board's DT is stripped** — `/proc/device-tree/model` and `compatible` are
  empty, and `Hardware` reads only `ODROIDX`. Do not expect self-describing
  hardware.
- **Two of four cores are permanently off** (`online=0,3`), and cpu3 was
  offlined to stop a boot loop. 2 cores is the ceiling; do not chase performance.
- **The 93LC66A EEPROMs are on no SoC bus — and never were.** #1 hangs off the
  LAN9512's own Microwire pins; the chip reads it at power-up and
  `ethtool -e eth0` dumps it. The kernel has *no SPI at all*, and `i2cdetect`
  is uninstalled anyway — scanning I2C was the wrong question. A chip that
  configures itself at power-up over its own pins is invisible to Linux by
  construction. #2 sits in the same LAN section beside a **KSZ8995XA 5-port
  switch** (photos); the switch is the leading candidate owner but is
  **unproven** — it wants a 2-wire I²C EEPROM, and a 93LC66A is 3-wire
  Microwire.
- **The RTC returns `EINVAL` until someone gives it a date.** MCP7940N (i2c
  `1-006f`) powers up with mday/month/year = 0; the kernel only reads, so
  `hctosys` fails every boot. Reading its registers directly needs
  `I2C_SLAVE_FORCE` — plain `I2C_SLAVE` returns `EBUSY` because `rtc-mcp7940n`
  owns the address.
- **Warm `reboot` hangs the board** — no status LED, no screen, only a power
  cycle recovers it (observed once, 2026-10-11, on the slimmed OS; boots clean
  after the cycle). Suspected Exynos warm-reset/SD re-init quirk, unproven.
  Prefer the power cycle; to root-cause it, capture `/dev/ttySAC1` (115200,
  1.8 V) during a soft reboot.
- **`vino` depends on `libtelepathy-glib0`** — autoremoving that lib kills VNC.
  It is the only reason a telepathy library is still installed.
- **`python-qt4` is EMA_Controls' runtime** — python-qt4 + python-sip are
  de-auto'd in `/var/lib/apt/extended_states`, and `libqtassistantclient4` (a
  python-qt4 hard dep) must stay out of orphan purges, or apt cascade-removes
  the desktop app's toolkit.
- **The STM8 silently refuses some frames** — received, no ack, no action.
  Single-mask GPO frames and an unprimed OUT2 close are refused; the prep-frame
  recipe in `docs/BOARD.md` ("Output bits") is mandatory.
- **Acks and status frames are both 10 bytes** — byte 3 decides: `00` = status
  (inputs), `01` = request ack (output states).
- **A rising `tx` counter proves nothing about wiring.** The UART driver counts
  every byte handed to it regardless of whether a pin is connected. Only a
  matching `rx` increment shows a wire exists — which is why the RS232 test is
  an A/B with the jumper fitted *and* removed.
- **RS232 is `/dev/ttySAC3` and RS485 is `/dev/ttySAC2`** — both direct Linux
  UARTs, neither behind the STM8. Anyone re-reading old notes that say
  "behind the STM8" should trust this instead.
- **Loopback cannot test a half-duplex differential pair.** On a 2-terminal
  RS485 port TX and RX are the same two wires, so there is nothing to jump;
  shorting D+ to D− forces the differential to zero. 5 phases / 0/50 echoes
  were spent learning this — use `rs485_probe.py` with a meter instead.
- **This kernel has no RS485 support**: `CONFIG_SERIAL_S5PV210=y` only, no
  `SERIAL_S5PV210_RS485`, no `PINCTRL`. `TIOCGRS485` returns `EINVAL` and
  direction control cannot be automatic — assert DTR/RTS manually.
- **The debug/console port (`ttySAC1`) is 1.8 V logic.** Not 3.3 V, not RS232.
  A 5 V adapter destroys it; a 3.3 V adapter driving into it risks damage, and
  may not even read 1.8 V highs. Use a 1.8 V TTL adapter. It is **never
  opened** by our tools — it holds a live `login`+`bash`.
- **`/dev/kmsg` does not reach the serial console.** Drive console output with
  `/dev/console` or `wall` instead; `/dev/kmsg` only fills the ring buffer.
- **openbox 3.5 autostart is plain shell — `@command` lines silently do
  nothing** (that syntax is openbox 3.6+). This board's dbus-launch also has
  no `--exit-with-x11`, only `--exit-with-session`. And lightdm's session
  choice is outvoted by `/root/.dmrc` + the AccountsService cache — all three
  must say `openbox` or the login silently runs a different session.
- **`apt-mark unhold` segfaults on precise's apt (0.8.44)** — unhold with
  `dpkg --set-selections` (`<pkg> hold`) instead. Also `python-serial` was
  apt-auto-flagged for removal: a naive autoremove would have killed the
  on-board `uart_*.py` tools — it is manual now; re-check the keep-list
  before any future autoremove.
- **vino 3.4.2 configures through GSettings/dconf (`org.gnome.Vino`), NOT
  GConf.** `/apps/vino/*` keys (gconftool-2) are dead leftovers — a fix
  written there silently does nothing (the 2026-10-11 popup fix didn't stick
  for exactly this reason). Use `gsettings set org.gnome.Vino <key> …` with
  `DBUS_SESSION_BUS_ADDRESS` exported (derive it from openbox's
  `/proc/<pid>/environ`); the database is `/root/.config/dconf/user`.
  Direct VNC access = `prompt-enabled false` + `notify-on-connect false` +
  `icon-visibility never`.
- **u-boot uses its built-in default environment; the boot-partition scripts
  are dead.** The kernel cmdline (empty `fb_x_res/fb_y_res/hdmi_phy_res`,
  `mem=1023M`) matches none of `boot.ini`/`boot*.scr`/`boot` on the card —
  do not edit those expecting effect; changing u-boot env needs the serial
  console. Consequences: s3cfb sits at an unclockable 1024x1200 until X
  mode-sets (~20 s; the monitor shows "No Signal" meanwhile) — an `fb-early`
  job was built to fix this 2026-10-12/13 and **REVOKED** (never executed at
  boot; see CHANGELOG), the kernel has
  **no fbcon** (`CONFIG_FRAMEBUFFER_CONSOLE is not set`), and this vendor
  s3cfb **refuses fb `write()` (ENOSPC)** — clear screens via mmap.
  **fb0 geometry is scaled:** the window buffer is **1024x600@32** (stride
  4096, double-buffered in 4.9 MB) and the FIMD scaler stretches it to the
  1920x1080 output — sysfs `virtual_size` reports the OUTPUT, the var GET
  reports the BUFFER, and fix `line_length` reads garbage. Paint at buffer
  size (the splash is 1024x600 for exactly this reason).
- **Upstart .conf files must be LF, never CRLF.** Windows-written CRLF makes
  dash die with `Syntax error: Bad fd number` on `2>&1\r` — the fb-early job
  silently never ran at boot for two days this way (2026-10-12/13). Related:
  the rootfs is still mounted **read-only at `startup`** (and even at
  `started mountall` on this vendor image — the fb-early job died on EROFS
  in both spots before being revoked 2026-10-13), so any boot job that
  writes a log must find the real rw-remount anchor first.
- **Node-RED runs inside the chroot** (`chroot /data/chroot14 … node-red
  --userDir /data/nodered`): host path `/data/chroot14/data/nodered/X` = node
  path `/data/nodered/X`. `httpStatic` must be **absolute from the chroot's
  view** (`/data/nodered/static/`) — a host path silently 404s, a relative
  path resolves against `process.cwd()` (upstart cwd, not userDir).
- **Old function-node sandbox has no `process`** (Node-RED 1.3.7): track
  start time with `flow.get/set`, not `process.uptime()`.
- **The real kiosk launcher is OpenBox, not GNOME**: `/etc/X11/openbox/autostart`
  (+ `/etc/xdg/openbox/autostart` mirror) runs `firefox <url> &` — a GNOME
  autostart entry would double-start FF. The URL was baked in there, not only
  in the FF profile.
- **Board SFTP uploads can lag**: after `board_run.py --upload`, run
  `sync; sleep 3` before exec-ing the file, and never trust "uploaded"
  alone for tiny scripts (seen: exec right after upload said "Can't open").

## Open issues
- **Wiegand out**: WORKS — driven live 2026-10-13, click-tested both ports ×
  both pins 2026-10-14. Read side (W-IN) **pending** (deferred 2026-10-11) — needs a scope + Arduino.
- **Analog I/O: does not exist on this board (user, 2026-10-14).** No analog
  section — the WM8960 audio codec is the only analog-class peripheral and it
  already works. The old "float-heavy loop writing 30" lead is retired.
- **RJ45 #2 bring-up (revised 2026-10-09).** Not an STM8 job after all: the board
  photos show a **Micrel KSZ8995XA 5-port switch** between the LAN9512 and the
  two jacks (`LAN1`/`LAN2`), so both are `eth0`. The settling test is one live
  cable in #2 against `ethtool eth0`, with #1 as a control — never yet run.
  **RS232 and RS485 are not in this group** — both are direct Linux UARTs.
- **RS485 receive path untested.** The port is identified and transmits, but
  `rx` never moved because no device was attached. Baud rate unknown.
- **RS232 baud rate and line voltage unknown.** Port path proven, but no real
  device has ever been attached.
- **RTC initialisation not run.** `hwclock --systohc` (a write) awaits the
  user's go; battery hold across a power cut untested; and whoever set the
  system date at boot despite the failed `hctosys` is unidentified.
- **93LC66A #2's owner — leading candidate, not proven.** No SoC-side path
  exists (no SPI, all I2C devices named). Photos put it in the LAN section beside
  a **KSZ8995XA 5-port switch**, which is the only chip that can make two jacks
  one NIC. Still unproven: the switch wants a 2-wire I²C config EEPROM, and a
  93LC66A is a 3-wire Microwire part. Same RJ45 #2 cable test is the first
  evidence.
- The micro-USB OTG port: **CLOSED, no further work** (decision 2026-10-11).
  Diagnosed — normal mode has *no gadget function built into the kernel*
  (3.0.68, all `g_*` disabled), which is the Windows Code 43 root cause and
  fixable only by a kernel rebuild (not pursued); Android mode enumerates as
  ADB (`18d1:0002`) but answers a flat 4-byte `FAIL` — no working adbd. PC-side
  drivers are not the problem, in either mode. **Use LAN/SSH instead.**
- Where the two 93LC66A EEPROMs are wired. Not on any Linux-visible bus.
  **#1 answered** — the LAN9512's config EEPROM. **#2 narrowed** to the LAN
  section beside a KSZ8995XA switch, owner unproven.
- Class `02` (`55 05 02 03 <value>`) is accepted by the STM8 and replies with
  varying data, but is not mapped to any device.
