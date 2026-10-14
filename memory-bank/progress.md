# Progress

What works, what is left, what is broken. Reviewed when resuming work.

## Status
Digital I/O phase **done**: link found, inputs decoded, outputs solved ON+OFF,
relay controlled — all on the desktop app **EMA_Controls**, click-tested by the
user ("all working"). **Serial ports solved too**: RS232 = `ttySAC3`,
RS485 = `ttySAC2` — both direct UARTs, both proved with a control run.
**Storage/clock diagnosed (2026-10-11):** 93LC66A #1 = the LAN9512's config
EEPROM (dumped via `ethtool -e eth0`); the MCP7940N RTC runs but was never
given a date — one `hwclock --systohc` from working (**not yet run**).
**Board now runs from the SD card (2026-10-11):** eMMC out (backup on PC as
`emmc_backup.img.gz`); the card boots the full vendor OS standalone and has a
**Wiegand OUT SOLVED (2026-10-13):** `tools/ema_wsend.cpp` drives W-OUT 2 —
SET_CONFIG→WRITE_DATA handshake ACKed by the STM8, ~9000 cards 0 refusals,
both DATA0/DATA1 physically verified with bench LEDs (open-collector — LED
wiring `+12V → 1k → LED → pin`). **No analog I/O exists on this board (user,
2026-10-14)** — the WM8960 audio codec is the only analog-class peripheral and
it already works; "analog I/O" is removed from the roadmap.
**Rootfs slimmed (2026-10-11):** `/` 3043→**1172 MB** used (1871 MB freed, 61%),
~551 packages purged incl. the whole vendor pack + unity → **LXDE**; boot-idle
RAM **151 MB**; vendor binaries archived hash-verified to `os/vendor-snapshot/`.
**Desktop stripped to appliance (2026-10-12):** 1160→637 packages, `/` now
**776 MB** used (~430 MB more freed); LXDE → **bare openbox 3.5** — session
autostart is only vino-server + EMA_Controls.sh (no panel/menu/wallpaper);
verified live with openbox+vino+ema_ui processes and VNC 5900 / SSH 22 /
HTTP 1880 all reachable from the PC. Session config archived in
`os/desktop/`; **cold-boot VERIFIED (power cycle, 2026-10-12): openbox +
vino-server + `/root/ema_ui.py` + node-red all auto-started unattended**
(warm reboot hangs — power cycle instead, proven 2026-10-11).
**Power-on "No Signal" — attempted then REVOKED (2026-10-12/13):** `fb-early`
upstart job (mode-set 1080p60 + paint `/root/splash.raw`, repo
`os/desktop/` marked REVOKED) was built, live-tested as a script (fb md5 ==
file md5, 1024x600 buffer FIMD-scaled to 1080p), but **never once executed
at boot**: CRLF .conf first, then `startup` and even `started mountall` both
hit a **read-only rootfs** (the vendor image remounts rw later, path
unidentified). User saw no splash ×2 power cycles and slower boot-to-app →
**revoked**: conf `.disabled`, /root files deleted, boot back to
"**No Signal until X/EMA UI ~20 s**". Parked: u-boot env via serial console
= the real fix. Side-finding: the
RTC loses its date on power-off (cold boot starts in year 2001).
**Node-RED HMI LIVE (2026-10-11):** http://192.168.100.127:1880 — Node-RED 1.3.7
+ node v10.24.1 in an Ubuntu 14.04 armhf chroot at `/data/chroot14` (16.04's
glibc rejects kernel 3.0.68), upstart job `/etc/init/nodered.conf` auto-starts
it. **Cold-boot auto-start verified (2026-10-12):** after the power cycle
the job came up on its own — HTTP 200, no manual `initctl start` — and the
same power cycle resolved the `/dev`-deletion incident (SSH sessions died
at the banner; `devtmpfs` rebuilt `/dev` at boot).
**PRODUCTION TONE — dev phase closed (2026-10-14):** repo reduced to the
frozen reference set (`tools/` 44 files incl. all `ema_*` frame recipes,
`docs/` + `raw/` evidence, `logs/` captures, `session-archive/`, `vendor-backup/`,
`os/` incl. the **hash-verified eMMC backup** — `sha256_gz=a7bb2f50…a09af`
recomputed == recorded, 2,546,914,166 bytes). Clean pass removed 183 MB
`temp/`, zero-byte junk, 2 hash-identical duplicates; 8 closed-question probes
moved to `archive/board-oneoff-probes/`. `.gitignore` (+ shared template) now
excludes `*.img/*.img.gz/*.raw`. **Git re-init'd as the production baseline.**
From now on: screen + Node-RED only, hardware I/O through flows. **Board-side
pass pending `PHL_BOARD_PASS`.**
**HMI SPA v1.0 LIVE (2026-10-14):** dashboard removed entirely (backup
`/data/node-red-dashboard-2.29.3.tar.gz`); Node-RED now serves a custom
vanilla-JS SPA from `httpStatic` — 6 tabs (Home/I-O/Manual/Settings/Info/Raw),
1 s poll of `GET /api/state`, editor at `/red`, **all controls grey/disabled**
until the logic workflow unlocks them (`locked` flag in flow + `/api/cmd`
stub). Kiosk boots fullscreen to `http://localhost:1880/` — **cold-boot
verified twice** (power-on → nodered + openbox + FF in ~2 min). Board cleaned:
107 junk files gone from /root, old EMA probe code archived `/root/old-hw/`,
apt cache freed (no autoremove).
**Node-RED dashboard + HMI kiosk (2026-10-13, historical):** `node-red-dashboard` installed
as a **userDir-local module** (`/data/nodered/node_modules/`, not global) with a
starter HMI flow; the openbox session now autostarts **Firefox at `/ui`
fullscreen** (kiosk via openbox `rc.xml` rule + hardened FF52 `user.js`) instead
of EMA_Controls.sh. **Two open fixes for next session:** (1) flow-file name
mismatch (`settings.js` → `flows.json` vs on-disk
`flows_linaro-ubuntu-desktop.json`) would serve an empty dashboard on clean
restart; (2) FF52 client-side LESS compile renders `/ui` magenta/unstyled.

## Works
- **SSH to the board.** `root` @ `192.168.100.127`, password via `PHL_BOARD_PASS`.
  **VNC also available — direct since 2026-10-12**: port 5900, no Allow/Deny
  prompt, no password (vino `org.gnome.Vino` dconf: prompt-enabled false,
  notify-on-connect false, icon-visibility never).
- **The SoC<->STM8 link** — `/dev/ttySAC0` @ **115200 8N1**. Recovered by
  disassembling `libemaLib`, confirmed by live traffic. `/dev/ttySTM8` is a trap.
- **IN1 / IN2** — status bytes 6/7, active-low. Proven by physically bridging
  each input; live lamps on the desktop UI.
- **OUT1 / OUT2 — ON and OFF, both channels.** Frame map in `docs/BOARD.md`
  ("Output bits"): full-state frames for OUT1; a **two-frame prep+close recipe**
  for OUT2. Verified 12/12 across state combinations, then click-tested.
- **Relay** — `55 05 04 01 01` / `01 00`, selector `01`.
- **Wiegand OUT — WORKS, click-tested 2026-10-14 (both ports × both pins).**
  `tools/ema_wsend.cpp <port> <bits> <card-hex> [count] [gap_ms] [f12] [f14]`
  does open → SET_CONFIG → WRITE_DATA(s) → close. STM8 echoes (=ACKs) every
  frame; halfwords are little-endian on the wire. Lines are **open-collector**,
  idle LOW after boot, released after close; LED test = `+12V → 1k → LED → pin`
  lights during a flood, off at close, on both lines. ~100 µs pulses — invisible
  to the eye at normal card rates. DATA0/DATA1 are **one channel** (0-bits and
  1-bits), not independent outputs — use OUT1/OUT2 for two separate lines.
- **EMA_Controls desktop app** (`tools/ema_ui.py`, launcher
  `/root/Desktop/EMA_Controls.sh`): input lamps, output buttons, relay button,
  **and a Wiegand W-OUT test row** (SEND WIEGAND). Display follows the board's
  report, never the click; retries 3x. The Wiegand button runs `/root/ema_wsend`
  as a subprocess after parking the `Reader` thread so the binary owns
  `/dev/ttySAC0`; the OK/FAILED verdict returns via the inbox queue.
- **RS232 = `/dev/ttySAC3`, a direct Linux UART — not an STM8 peripheral.**
  Proven by a bare-wire TX↔RX loopback (`RS232LB` echoed, `rx 0→7`) **and** a
  control run with the wire removed (`rx` frozen at 7). `ttySAC2` ruled out:
  tx 105, rx 0. Tool: `tools/rs232_loopback.py`.
- **RS485 = `/dev/ttySAC2` (2-terminal, half-duplex).** Identified by measuring
  **DC across the pair** in 30 s windows, **with a control**:

  | port | idle | during TX |
  |---|---|---|
  | `ttySAC2` | 0.646 V | **~220 mV** (twice, reproducible) |
  | `ttySAC3` | 0.646 V | **0.646 V** (control, held still) |

  Marked **WORKS (TX)** — the pair is driven; `rx` never moved because no
  device is attached. Kernel has no RS485 mode, so DTR/RTS is asserted by hand.
  Tool: `tools/rs485_probe.py`.
- **Regression checks**: `tools/ema_uimap.py` 8/8, `tools/ema_gap.py` 4/4.
- **Readback without a meter**: status b4/b5 = raw OUT1/OUT2 contacts,
  b6/b7 = inputs, b8/b9 = mask echo; request acks carry actual b4/b5 too.
- **Confirmed WORKS on the board:** RJ45 #1 (`eth0`, smsc95xx), WM8960 audio,
  4x USB hub chain, HDMI, eMMC root, 12 V header. **micro-USB is CLOSED**
  (diagnosed, no further work) — see below.
- **Vendor stack backed up** to `vendor-backup/` (4 binaries, SHA256 in
  `MANIFEST.md`); `docs/raw/` holds the survey evidence.
- **93LC66A #1 — the LAN9512's own config EEPROM.** Read with
  `ethtool -e eth0`: `0xA5` valid-sig, MAC `00:25:ff:fe:44:45` (= `eth0`),
  USB IDs `0424:9512`/`0424:ec00`, UTF-16 `SMSC`. The chip sits on the
  LAN9512's dedicated Microwire pins and is loaded by the chip itself at
  power-up — no SoC bus, no kernel support needed. Raw:
  `docs/raw/rtc-93lc66a-raw.md`.

## Does not work
- **RS485 receive path** — the port is identified and transmits, but `rx` has
  **never moved**: no RS485 device has ever been attached. Baud rate unknown.
- **Wiegand read side (W-IN)** — **PENDING (deferred 2026-10-11)** — send side
  WORKS; read side unmapped; parked to focus on the main board work.
- ~~Analog I/O~~ — **none on this board (user, 2026-10-14)** — audio only, and
  audio already works. Removed from the roadmap.
- **RJ45 #2** — on the STM8, channel proven, request format not built.
  (**RS232 and RS485 used to be listed here and were both wrong** — they are
  direct UARTs; see Works.)
- **RS232 baud rate and line voltage** — port path proven, but no real device
  has ever been attached; loopback cannot establish either.
- **93LC66A #2** — master not proven. No SoC-side path exists (no SPI in the
  kernel at all, all 7 I2C devices named). **Location known (user): LAN section,
  beside the LAN9512 — and the board photos name the neighbour as a Micrel
  KSZ8995XA 5-port switch**, the leading candidate owner. Unproven: the switch's
  documented config bus is I²C 2-wire, a 93LC66A is 3-wire Microwire. (#1 works —
  `ethtool -e`.)
- **MCP7940N RTC reads `EINVAL` everywhere.** Chip is healthy — read-only dump
  (`tools/mcp7940_dump.c`) shows oscillator running and H:M:S ticking — but the
  **date registers are 0/0/0**, so `hctosys` fails at boot. Fix =
  `hwclock --systohc`, **not yet run** (a write; awaiting the user's go).
- **Class `02` (`55 05 02 03 <value>`)** — accepted, varying replies, unmapped.
- **The micro-USB OTG port — CLOSED 2026-10-11, no further work.** Diagnosed
  both modes: normal mode has **no gadget function in this kernel**
  (`/proc/config.gz` — all `g_*` disabled) so enumeration dies (`-110/-71` =
  Windows Code 43); Android mode enumerates as ADB `18d1:0002` but replies with
  a flat 4-byte `FAIL` — a stub adbd. **Fix would need a kernel rebuild —
  accepted as-is, not pursued. Reopen only if that is ever approved.**

## Milestones
| Date | Milestone | Notes |
|---|---|---|
| 2026-10-04 | Board reached over SSH + VNC | `linaro-ubuntu-desktop` |
| 2026-10-10 | Board identified: Daikin CMIMIR + STM8S207 | Explained every earlier dead end |
| 2026-10-10 | cpu3 flap root-caused, log spam stopped | Board runs on 2 cores, permanently |
| 2026-10-10 | Inventory re-measured; workspace cleaned | 15/15 classified, 12 settled |
| 2026-10-10 | **SoC<->STM8 link found** (`ttySAC0` @ 115200) | Frame format recovered from `libemaLib` + live traffic |
| 2026-10-10 | **IN1/IN2 decoded, relay controlled** | Verified by physical tests |
| 2026-10-10 | **OUT1/OUT2 ON+OFF solved; EMA_Controls UI** | 12/12 frame-map tests + user click-through |
| 2026-10-09 | **Board photos name the companion chip: KSZ8995XA 5-port switch** | Photo review + datasheet; "RJ45 #2 on STM8" retired, both jacks = `eth0`; 93LC66A #2 narrowed but unproven; RTC coin cell confirmed present. Nothing run on the board |
| 2026-10-11 | **RS232 identified = `/dev/ttySAC3`** | One-wire loopback + control run; old "behind STM8" note corrected |
| 2026-10-11 | **RS485 identified = `/dev/ttySAC2`** | Differential meter reading + control run; marked WORKS (TX) |
| 2026-10-11 | **RTC diagnosed; 93LC66A #1 proven = LAN9512 EEPROM** | Read-only register dump + `ethtool -e` dump; no BLOCKED rows left |
| 2026-10-11 | **eMMC backed up + cloned to SD; SD is now the playground** | `emmc_backup.img.gz` (sha256 `70b75811…`); card boots standalone; 51 GB `/data` added |
| 2026-10-14 | **HMI SPA v1.0 — dashboard removed, custom SPA, cold-boot verified** | 6 tabs, all controls locked; openbox autostart is the kiosk launcher; `httpStatic` must be chroot-absolute |
| 2026-10-14 | **Production tone: dev phase closed, git baseline rebuilt** | Reference set frozen, temp/ (183 MB) + dupes gone, 8 probes archived, eMMC backup hash-verified |

## Known issues
- **The STM8 silently refuses some frames** (received, no ack, no action).
  Always confirm from status/ack. Single-mask GPO frames and unprimed OUT2
  closes are refused — see the recipe in `docs/BOARD.md`.
- **The STM8's state survives a Linux reboot.** Only a power cycle restores
  power-on output states; there is no software reset path from Linux.
- **2 of 4 cores are permanently off** (`online=0,3`). Do not chase performance.
- **RAM showed 916 MB of 991 MB in use** at survey time with no swap. Unverified
  snapshot — check for a leak before trusting any timing.
- **The device tree is stripped**: `model` and `compatible` are empty,
  `Hardware` reads only `ODROIDX`.
- **Kernel is from 2014.** No `gpiochip`, no native MAC. Any "just install the
  userspace tool" plan fails: the kernel side is what is missing.