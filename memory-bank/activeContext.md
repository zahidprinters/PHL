# Active Context

**This file changes most often — update it at the end of every session.**

_Last updated: 2026-10-14 (**HMI idle screen-blank shipped** — Settings → Display → "Screen blank" select (Always on / 30 s / 1 / 2 / 5 / 10 min), persists in `localStorage` `hmi.blank` (seconds, 0=never), full-screen black `#blanker` overlay after idle, wakes on touch/click/key and re-arms. **Frontend-only on purpose** — NOT gated by the controls lock (it's a display pref, not a hardware cmd), so it works in v1 with commands still locked; no backend call. Files: `os/node-red/static/{index.html,app.css,app.js}`. Ceiling: software blank, not real backlight-off (DPMS/backlight API behind `/api/cmd` is the upgrade once logic workflow unlocks). Regression guard `tests/blank_check.js` → 13/13 via `vm`+fake clock. FF52-safe (explicit top/left/right/bottom, no `inset`). Next: still board-side logic workflow; blank not yet eyeballed on the 1024×600 panel.)_

_Last updated: 2026-10-14 (**PRODUCTION TONE — dev phase closed.** Repo frozen to the reference set: tools/ (44 = README table + ema_* frame recipes + infra), docs/ + raw evidence, logs/ captures, session-archive, vendor-backup (pristine), os/ (eMMC backup VERIFIED — sha256_gz `a7bb2f50…a09af` recomputed == recorded). Clean pass: temp/ gone (183 MB), zero-byte junk + 2 hash-verified duplicates deleted, 8 closed-question probes moved tools/ → archive/board-oneoff-probes/ (board_gui_probe, board_ema_capi/disasm/probe, gpio_scan, rs485_pins/recon/phase). `.gitignore` + shared template got `*.img/*.img.gz/*.raw`. **`.git` re-init'd as production baseline — history restarts 2026-10-14.** FROM NOW ON: only screen (SPA) + Node-RED work; all hardware I/O via flows. **NEXT SESSION: board-side production pass — needs `PHL_BOARD_PASS` set (not available this session): tar /root snapshot → os/, archive dev leftovers (EMA_Controls desktop app?), verify nodered/SPA/kiosk state, then start the logic workflow.**)_
_Last updated: 2026-10-14 (**HMI SPA v1.0 shipped** — dashboard REMOVED (tar backup `/data/node-red-dashboard-2.29.3.tar.gz`), flow = 9 pure logic/http nodes, `os/node-red/static/{index.html,app.css,app.js}` served via `httpStatic '/data/nodered/static/'` (absolute-from-chroot!), editor at `/red`, kiosk = `http://localhost:1880/` (homepage + restart_ff.sh + openbox autostart `/etc/X11`+`/etc/xdg` — openbox autostart is the REAL kiosk launcher, not GNOME), cold-boot x2 verified. All controls grey/`disabled` — unlock happens via `locked:false` in flow's `build state` + `/api/cmd` stub replacement when the logic workflow lands. Board cleaned: /root junk gone, old EMA probe code archived `/root/old-hw/` (59 files), apt cache freed (NO autoremove — risky for desktop libs). Gotchas: old fn-node has no `process`; SFTP needs sync+sleep; `.git` vanished from D:\phl mid-session (not our doing — re-init when wanted). Next: wire real logic (STM8/Modbus → state fields), unlock controls, tab-by-tab UI review, 1024×600 panel fit check.)_
_Last updated: 2026-10-13 (**Node-RED dashboard + HMI kiosk installed**; openbox autostart now fires `firefox http://localhost:1880/ui` instead of EMA_Controls.sh — FF52 borderless/fullscreen forced by an openbox rule in `/root/.config/openbox/rc.xml` + hardened FF52 `user.js`. Dashboard module is a **userDir local install** (`/data/nodered/node_modules/node-red-dashboard`, NOT global — `npm ls -g` is empty by design). HMI starter flow deployed. **TWO OPEN ISSUES for next session, in order:** (1) **flow-file name mismatch — settings.js says `flowFile: 'flows.json'` but the only flow on disk is `flows_linaro-ubuntu-desktop.json` and `flows.json` does NOT exist → a clean restart serves an EMPTY dashboard; reconcile the name first**; (2) FF52 client-side LESS compile renders /ui magenta/unstyled — was mid-hunt on `main.backgroundColor`/`uiTheme`. Full record in CHANGELOG 2026-10-13 entry.)_
_Last updated: 2026-10-13 (**fb-early + boot splash REVOKED by user decision** after the 2nd power cycle showed nothing and slower boot-to-app. Boot log proved the job AGAIN never ran python (`Read-only file system` in fb-early.log, 0 pixclk lines in dmesg) — **even `started mountall` is too early; this vendor image remounts rw later via an unidentified path**. Board: conf → `.disabled`, `/root/fb_early.py` + `splash.raw` deleted, `Unknown job: fb-early`, session+Node-RED unaffected. Boot back to "No Signal until app ~20 s". Repo files stay in `os/desktop/` marked REVOKED. Parked unless reopened: u-boot env via serial (the real fix) or the true rw-remount anchor. **Learned: on this image a boot job that writes anywhere on / cannot assume rw even after mountall**)_
_Last updated: 2026-10-11 (board apt update/upgrade/clean done — safe subset only; `dist-upgrade` REJECTED because it would remove unity/ubuntu-desktop/linaro-ubuntu-desktop; 6 packages intentionally held back; dead Linaro PPAs parked as .disabled; vendor holds on kernel images kept)_
_Last updated: 2026-10-11 (VNC headless-safe: `prompt-enabled=false` + `notify-on-connect=false` — no board-screen dialog per connection; restart vino via full path `/usr/lib/vino/vino-server`, bare name not on root PATH — confirm no popup on next connect)_
_Last updated: 2026-10-11 (all OS/backup/tooling consolidated into permanent `os/` archive — backup-eMMC/, scripts/, logs/ + os/README.md; temp/ now empty; paths repointed)_
_Last updated: 2026-10-11 (SD card = full-capacity playground: cloned vendor OS boots standalone with eMMC removed; 51 GB `/data` partition p3 added + fstab-persistent;)_
_Last updated: 2026-10-11 (eMMC backed up to PC + verified; eMMC cloned to SD card from the board — boot chain byte-identical; SD boot test is the immediate next step)_
_Last updated: 2026-10-11 (RTC diagnosed; 93LC66A #1 proven; #2 located — switch hypothesis, cable test pending)_
_Last updated: 2026-10-13 (libemaLib serialiser FULLY decoded from jump table — real GPO types are 17/18/19, relay type 32, GPI12 read type 65, enum types 8–11 are dead; Wiegand WRITE_DATA handshake decoded (SET_CONFIG seeds session `this+490`); **W-OUT is NOT extra GPO** — it is Wiegand DATA0/DATA1 pulse output, "6 GPO" claim refuted; error codes corrected; `docs/VENDOR-PROTOCOL.md` rewritten + `docs/raw/libemaLib-jumptable.md` added)_
_Last updated: 2026-10-13 (Wiegand OUT **WORKS** — `tools/ema_wsend.cpp` drives W-OUT 2 live; ~9000 cards, STM8 echoes every frame, 0 refusals; both DATA0/DATA1 physically verified with bench LEDs; open- **collector** confirmed — LED must be `+12V → 1k → LED → pin`; idle LOW at boot, released after close; halfword endianness = **LITTLE**-endian; checklist now 14 WORK / 3 OPEN / 1 CLOSED — LINK FOUND category empty)_
_Last updated: 2026-10-13 (**EMA_Controls desktop app gained a Wiegand W-OUT test row** — SEND WIEGAND button runs the proven `/root/ema_wsend` as a subprocess; the UI's `Reader` thread is parked first so the binary gets `/dev/ttySAC0` to itself, then polling resumes; verdict (OK/FAILED) comes back via the inbox queue on the Qt thread; py_compile clean, relaunched on VNC PID 3020 — **the button click itself still needs the user at the desktop**)_
_Last updated: 2026-10-14 (**Wiegand click-tested by the user — all work**: port 1 & port 2 × W-OUT1 (DATA0) & W-OUT2 (DATA1), every combination pulses from the desktop app; closes "only port 2 exercised on pins". Confirmed one channel, not two outputs — for independent lines use OUT1/OUT2. Remaining open on Wiegand: read side/W-IN (needs scope + Arduino), 26-bit, parity, f12/f14 units. **Correction: NO analog I/O on this board (user) — only the WM8960 audio codec, already WORKS; "analog I/O" removed from the roadmap everywhere**)_
_Last updated: 2026-10-11 (**W-IN read side marked PENDING — deferred**; plan parked intact in `docs/BOARD.md` §9. Focus moves to the main board work. U20 = 74HCT08 input buffer photo-verified the same day)_
_Last updated: 2026-10-11 (**upgrade to Ubuntu 14.04.6 assessed live — REJECTED, not run**: `do-release-upgrade -c` offers it, kernel hijack unlikely (boot.ini pins /media/boot/uImage), but the Linaro desktop is provably uninstallable (Remv unity chain), VNC rides on that desktop, trusty is EOL too, kernel/driver set unchanged — zero benefit vs one hard-requirement risk. Safer path for newer userland = armhf Debian chroot on /data)_
_Last updated: 2026-10-12 (**desktop stripped to a bare openbox appliance** — 1160→637 packages, rootfs 1.2G→**776M**; session = lightdm root autologin → **openbox 3.5** with a plain-shell autostart of just vino-server + EMA_Controls.sh (no panel/menu/wallpaper/status bar); verified live: openbox + vino-server + ema_ui processes up, session log `Starting session openbox as user root`, and from the PC **VNC 5900 ✓ / SSH 22 ✓ / HTTP 1880 → 200**. Two traps: `python-serial` was apt-auto-flagged (naive autoremove would kill `uart_*.py` — kept manual) and `apt-mark unhold` segfaults on precise's apt (use `dpkg --set-selections`). Session config archived in `os/desktop/`. **COLD BOOT VERIFIED same day (user power cycle): openbox + vino + ema_ui + nodered all auto-started unattended**; pending: user's VNC visual check + `/data` cleanup)_
_Last updated: 2026-10-12 (**VNC direct access** — the Allow/Deny "Question" dialog and connect notification are off: `org.gnome.Vino prompt-enabled=false`, `notify-on-connect=false`, `icon-visibility=never` via gsettings; **root cause: vino 3.4.2 = GSettings/dconf — the 10-11 gconftool-2 "fix" wrote dead GConf keys under /apps/vino/**. Auth was already `['none']` (no password), view-only false. vino restarted (single PID on :5900). Proven before/after: baseline `xwininfo -root -tree` during a raw RFB handshake showed `"Question" ("vino-server")` dialog → after the fix no dialog; handshake `SEC_TYPES [18,1] → None → SECR 0`. Persists in `/root/.config/dconf/user`. Pending: user's viewer test, cold-boot re-check)_
_Last updated: 2026-10-12 (**power-on "No Signal" fixed** — u-boot runs its built-in env (boot-partition scripts are dead), so the kernel gets empty fb_* args, s3cfb sits at unclockable 1024x1200, no fbcon (CONFIG_FRAMEBUFFER_CONSOLE unset) → nothing mode-sets HDMI until Xorg (~15-20 s). New upstart job **fb-early** (`/etc/init/fb-early.conf` + `/root/fb_early.py`, repo `os/desktop/`) does FBIOPUT_VSCREENINFO 1080p60 + mmap black-clear at `startup` (~3-5 s). Live-tested via stop/start lightdm: dmesg pixclk 19528→6734, sysfs 1920,1080, session restored fully (X/openbox/vino/ema_ui), HTTP 200 + VNC ✓. Traps: vendor s3cfb rejects fb write() ENOSPC → mmap; ioctl GET right after PUT shows mixed per-window state (sysfs is truth). **Awaiting the user's power cycle for the visual confirmation.** Side-finding: cold-boot RTC date is LOST (board starts in 2001; clock fixed mid-boot by something else) — hwclock --systohc still pending)_



_Last updated: 2026-10-11 (**rootfs slimmed 3043→1172 MB used — 1871 MB freed, 61%**: stage-1 file purge + 198 pkg purge (vendor packs, KDE, thunderbird, vlc, cups, bt, telepathy, ubuntuone…) + 323 apt orphans + 30 unity pkgs; unity → **LXDE** via lightdm-gtk-greeter (vino-server in LXDE autostart, user-session=LXDE, autologin root kept) — boot-idle RAM 546→151 MB; vendor bins CMIMIRDemo + libema/cmicolor/cmiris libs archived hash-verified to `os/vendor-snapshot/` then deleted; python-qt4/python-sip de-auto'd + libqtassistantclient4 kept (EMA_Controls protection), libtelepathy-glib0 kept (vino dep); **warm `reboot` HANGS — no LED/no screen — use power cycle** (user-confirmed; boots clean after cycle, LXDE on screen); `board_run.py` gained `--download` + PHL_BOARD_TIMEOUT; next = **Node-RED HMI in an armhf chroot** (host glibc 2.15 too old for modern Node))_



_Last updated: 2026-10-12 (project refocused on the current vendor-OS board and its real hardware; earlier off-board experiments removed as not viable on this 32-bit, 1 GB board)_
_Last updated: 2026-10-11 (**Node-RED 1.3.7 HMI is LIVE** at http://192.168.100.127:1880 — node v10.24.1 inside an Ubuntu 14.04 armhf chroot at `/data/chroot14` (16.04's glibc rejects kernel 3.0.68; trusty's 2.19 passes; libstdc++6 from xenial copied in for `GLIBCXX_3.4.20`; apt = `ports.ubuntu.com` — old-releases has NO trusty). Upstart job `/etc/init/nodered.conf` auto-starts it (repo copy `os/node-red/`). **INCIDENT: `rm -rf /data/chroot` walked a live `/dev` bind mount and deleted real host device nodes — every new SSH session now dies before the banner; board needs a POWER CYCLE (devtmpfs rebuilds /dev).** Rule: never `rm -rf` a tree with bind mounts still attached — umount first. **Not yet verified: cold-boot auto-start — the same power cycle will test it**)_

## Current focus
**One workstream: the board.** A Daikin CMIMIR HVAC controller (Exynos 4412 +
STM8S207). The deliverable is the peripheral checklist in **`docs/BOARD.md`**.

**18 checklist rows, 14 WORK, 3 OPEN, 1 CLOSED — no BLOCKED and no LINK FOUND
rows remain.** Driven from Linux
today: 12 V header, RJ45 #1, **IN1/IN2**, **OUT1/OUT2 (ON+OFF)**, **relay**,
**RS232 (`ttySAC3`)**, **RS485 (`ttySAC2`, TX)**, WM8960 audio, 4× USB,
8 GB eMMC, HDMI, the STM8 link itself. **micro-USB is CLOSED** — diagnosed,
no further work — see below.
All of the
digital I/O is on the board's desktop app **EMA_Controls**
(`/root/Desktop/EMA_Controls.sh` → `tools/ema_ui.py`); its reference line
lists all three UARTs, and its **SEND WIEGAND** button drives W-OUT through
the proven `/root/ema_wsend`.

**LINK FOUND = 0 — Wiegand was the last one and it is now WORKS** (2026-10-13,
`tools/ema_wsend.cpp`; both DATA0/DATA1 verified with bench LEDs). RJ45 #2 was
re-scoped to **OPEN** — the board
photos show a **Micrel KSZ8995XA 5-port switch** between the LAN9512 and the two
jacks (`LAN1`/`LAN2`), so both are `eth0`; there is no second NIC and no request
frame to build. One live cable in #2 against `ethtool eth0` would close it.

**The fourth UART, `ttySAC1`, is the debug/console port** — 115200 8N1,
**1.8 V logic** (not 3.3 V, not RS232). `login` + `bash` hold it after every
boot via `auto-serial-console`, and `/dev/console` or `wall` will make it
transmit on demand.

## Next steps
0. **Node-RED dashboard kiosk — INSTALLED 2026-10-13, TWO FIXES PENDING (do these first):**
   - **(a) Flow-file name mismatch.** `settings.js` (board + repo) says
     `flowFile: 'flows.json'`, but the only flow on disk is
     `flows_linaro-ubuntu-desktop.json` and `flows.json` does NOT exist → a clean
     restart reads settings.js, finds no flows.json, serves an **EMPTY**
     dashboard. Fix: rename the flow file to `flows.json` (or drop the
     `flowFile` override). Confirm which file running PID 1257 loaded.
   - **(b) FF52 renders /ui magenta/unstyled** — dashboard theme CSS compiles
     client-side from `app.min.less`; a failed compile strips all widget CSS.
     Resume the `main.backgroundColor`/`uiTheme` hunt; an explicit theme may
     sidestep the broken default.
   Kiosk already in place: openbox `autostart` fires `firefox …/ui` (not
   EMA_Controls.sh), fullscreen/borderless via `/root/.config/openbox/rc.xml`,
   hardened FF52 `user.js`. Dashboard is a **userDir local install**
   (`/data/nodered/node_modules/node-red-dashboard`).
1. ~~POWER CYCLE~~ **DONE (2026-10-12):** `/dev` recovered, SSH works, and
   the power cycle delivered **every cold-boot proof at once** —
   **Node-RED** upstart job auto-started (HTTP 200, no manual
   `initctl start`) **and the new openbox session came up unattended**
   (`uptime` 9 min: openbox + vino-server + `/root/ema_ui.py` all started
   at 01:53; PC probes: VNC 5900 True, HTTP 1880 → 200). Still open:
   the half-done `/data` cleanup **safely** (no live bind mounts after
   boot): remove remnants of `/data/chroot` (the dead 16.04 tree) and the
   uploaded tarballs if still present; keep `/data/chroot14` + `/data/nodered`.
   Plus the user's VNC visual check: bare screen, EMA window, no chrome.
1. ~~SD CARD BOOT TEST~~ **DONE.** SD card boots the full vendor OS standalone
   (eMMC removed, `/` = `mmcblk0p2`). Card is now a full-capacity playground:
   - eMMC **out** (backup) — `emmc_backup.img.gz` (2.55 GB, sha256 `70b75811…`) on PC.
   - **`/data`** = new p3, ext4, 51 GB free, fstab-persistent (`LABEL=data`).
   - **Permanent archive now in `os/`** (see `os/README.md`): `backup-eMMC/`
     (the irreplaceable 2.43 GB image, sha256 `70b75811…`), `scripts/` (23 reusable tools), `logs/`.
     `temp/` is now empty — everything was moved to `os/`.
   - Reload recipe in `os/README.md`: `scripts\Write-ImageToCard.ps1 -Image
     backup-eMMC\emmc_backup.img -ConfirmDisk 1` + `scripts\Compare-Card.ps1`.
     Both rootfs's share UUID `e139ce78…` — harmless while eMMC stays out;
     retune if both disks ever run together.
1. ~~**Wiegand read side (W-IN)**~~ — **PENDING (deferred 2026-10-11)** —
   send side DONE (live 2026-10-13, click-tested 2026-10-14). Receiving needs
   a scope/logic analyzer + Arduino pulse simulator; `55 04 06 01` (type 65)
   has never been answered. Parked — full plan intact in `docs/BOARD.md` §9
   (meter idle voltage → Arduino D2/D3/GND → arm via SET_CONFIG → decode push).
2. ~~Analog I/O~~ — **closed: no analog section on this board (user,
   2026-10-14)**; audio (WM8960) is the only analog-class peripheral and it
   already works. The "float-heavy loop writing 30" lead is retired.
3. **RS485 receive path** — attach a device; `rx` has never moved, baud unknown.
4. ~~**Verify the debug port physically**~~ — ✅ **DONE (2026-10-12).** 1.8 V
   adapter + level shifter + PuTTY on COM4 captured the full boot and a root
   shell. Board runs vendor OS from the SD card over the debug port alone (no
   Ethernet). `ttySAC1` is now proven, not just identified.
5. RJ45 #2 bring-up — same STM8 channel, same technique.
6. **Initialise the RTC** — `hwclock --systohc` (a write; user's go), reboot,
   confirm `hctosys`, then test battery hold across a power cycle.
7. **Identify 93LC66A #2's owner** — location known (LAN section, beside the
   LAN9512). The board photos named the neighbour: a **Micrel KSZ8995XA 5-port
   switch** — the leading candidate, but **unproven** (the switch wants a 2-wire
   I²C config EEPROM; a 93LC66A is 3-wire Microwire). The same test decides both
   this and row 3: a live cable in **RJ45 #2** watched against `ethtool eth0`,
   with RJ45 #1 as a control.
8. ~~**Micro-USB/ADB**~~ — **CLOSED 2026-10-11.** Fully diagnosed both modes;
   no further work. Never chase PC drivers (proven wrong on Windows and
   Linux); a fix would need a kernel rebuild, accepted as-is, not pursued.

## Recently changed
- **Power-on "No Signal" fixed (2026-10-12).** u-boot = built-in env
  (boot-partition scripts unused) → empty `fb_*` bootargs → s3cfb fallback
  1024x1200 (unclockable) → dead screen until Xorg (~15-20 s). New
  `fb-early` upstart job mode-sets 1080p60 + black via mmap at `startup`
  (~3-5 s). Live-tested (stop/start lightdm: pixclk 19528→6734, sysfs
  1920x1080, full session restored). **Needs the user's power cycle for
  visual confirmation.** Repo: `os/desktop/fb-early.conf` + `fb_early.py`.
- **VNC direct access (2026-10-12).** `prompt-enabled` + `notify-on-connect`
  → false, `icon-visibility` → never, via `gsettings set org.gnome.Vino …`
  (vino 3.4.2 = GSettings/dconf; `/apps/vino` GConf keys are dead — that's
  why the 10-11 fix never worked). No Allow/Deny popup, no password
  (`authentication-methods ['none']`). Proven with before/after
  `xwininfo -root -tree` (dialog present → absent) + raw RFB handshake
  (None → SECR 0). DB: `/root/.config/dconf/user`.
- **Desktop stripped to a bare openbox appliance (2026-10-12).** 1160→637
  packages, rootfs 1.2G→776M. LXDE → **openbox 3.5** (lightdm root autologin
  kept; `~/.dmrc` + AccountsService + lightdm.conf all say openbox;
  openbox.desktop wraps `dbus-launch --exit-with-session`); session autostart
  is 3 lines of plain shell — vino-server + EMA_Controls.sh, nothing else.
  Verified live: openbox + vino + ema_ui running; PC sees VNC 5900, SSH 22,
  Node-RED HTTP 200. Traps: `python-serial` apt-auto-flagged (kept manual —
  it guards `uart_*.py`), `apt-mark unhold` segfaults on precise →
  `dpkg --set-selections`. Board config archived in `os/desktop/`.
  **Cold boot verified same day (power cycle): openbox + vino + ema_ui +
  nodered auto-started. Pending: user's VNC visual check, `/data` cleanup.**
- **STM8 firmware readback assessed (2026-10-12).** No software path exists —
  the EMA protocol has no read-flash command and `ema_getEMAVersion` is a
  hardcoded stub; the STM8 can't be put into its UART bootloader from Linux (no
  reset/SWIM line exposed). **Top hardware next-step:** an **ST-Link/V2 clone +
  SWIM** (`stm8flash -c stlinkv2 -p stm8s207?rb -r fw.hex`) reads the whole
  128 KB flash and would answer Wiegand WRITE, class `02`, analog and
  `GPI12_READ` at once. Needs the STM8S207 SWIM pin (pin 1 = SWIM/NRST) traced
  to a test pad. Recorded in `docs/VENDOR-PROTOCOL.md`.
- **Vendor protocol framework decoded from libemaLib (2026-10-12, jump table
  completed 2026-10-13).** Disassembled `libemaLib`; `EMAMain::checkWriteEvent`
  @ 0x54e0 is the frame serialiser (jump table on event type at struct `+4`).
  Full event→frame map + struct offsets in **`docs/VENDOR-PROTOCOL.md`**:
  OUT1=`+49`, OUT2=`+50`, relay sel=`+53`/state=`+54`, Wiegand value=`+8`,
  token/bitlen=`+10`, config=`+12/+14`, card=`+16…`. Silent-refusal causes now
  known (returns negative: `-23` state>1, `-24` wiegand byte8∉{1,2}, `-16/-17`
  session `buf[490]` 0/mismatch, `-13` unhandled type). Real GPO types are
  **17/18/19**, relay **32**, GPI12 status read **65** (`55 04 06 01`, never
  sent); enum types 8–11 are dead no-ops, and no-op writes can re-send the
  **stale previous frame** (the "type 8 → `55 04 01 01`" mystery). Wiegand
  WRITE needs SET_CONFIG (type 4) to seed `buf[490]` first; `close()` zeroes it.
  **W-OUT is Wiegand DATA0/DATA1 pulse output — not extra GPO** ("6 GPO" refuted).
  CMIMIRDemo = face+iris biometric terminal; libcmirisLib2 EEPROM/I²C = the iris
  camera, not this board.
- **Complete hardware survey + full board picture (2026-10-12).** Read-only SSH
  survey (27 sections) captured to `docs/raw/board-full-survey-raw.md` (the boot
  snapshot); interpreted into **`docs/HARDWARE-COMPLETE.md`**. New findings:
  board-file kernel (no DTB); **SoC ADC `exynos4412-adc` present but driverless**
  (untapped 4-ch/12-bit analog-in); **PWM timers** untapped; **buttons =
  `odroid-keypad`** on `event0` (bypass STM8, keycodes undecoded); a **second RTC
  `s3c64xx-rtc`**; new I²C device `0-0006`; vendor stack confirmed on disk.
  Untapped = analog-in (ADC), PWM-out, ~250 GPIO pads (5 used), SoC RTC, buttons,
  BT/IR — all gated by missing kernel drivers, not hardware. *(2026-10-14: the
  user confirms the board has **no analog section** — audio/WM8960 is the only
  analog-class peripheral; the SoC ADC/PWM are SoC-internal silicon, not board
  I/O.)*
- **Wiegand vendor-side mapped under the swallowing shim (2026-10-09).**
  Two swallowed scans on the live board (nothing transmitted to the STM8):
  the vendor enum is 0-indexed with **Wiegand = event types 2–6** (enum names
  live in CMIMIRDemo, not libemaLib). **GET_CONFIG (5) → `55 05 02 03 <value>`
  and AUTO_DETECT (6) → `55 05 02 04 <value>`, value = struct offset 8**
  (offset 8 = 1 flips the frame value byte — verified). READ_DATA / WRITE_DATA
  / SET_CONFIG emit **nothing** through libemaLib 1.0.1 (256-offset sweep,
  struct fills, card numbers, setReadEvent — all silent), so the WRITE_DATA
  frame is still unknown (next: disassemble CMIMIRDemo's Wiegand UI or try a
  newer libemaLib). Wiegand is **DIGITAL, 2-wire** — headers `W-IN` (receive)
  and `W-OUT` (`W-OUT1`/`W-OUT2` = D0/D1, emulate a card). **2026-10-11: the
  user found `U20` = 74HCT08 quad AND between the Wiegand INPUT terminals and
  the STM8** — non-inverting (pulse polarity unchanged), HCT inputs are
  high-impedance ⇒ pull-ups are on-board (expect ~5 V idle at DATA0/DATA1),
  5 V domain ⇒ Arduino, not ESP32-C3; the gates' second inputs are untraced ⇒
  possible software gating (continuity recipe in `docs/BOARD.md` §9). Front
  label read (`docs/photos/IMG_20261011_153945.jpg`): WIEGAND INPUT =
  `+12V OUT · DATA0 · DATA1 · GND`. Hardware pending: meter the idle voltage →
  wire Arduino D2/D3/GND → pulse a 26-bit card while armed via SET_CONFIG →
  decode the push frame `readEvent` returns (**the one remaining unknown**).
  Tools: `tools/ema_wscan*.cpp`, `tools/board_wiegand_scan*.py`; raw:
  `docs/raw/wiegand-frames{,-2}-raw.md`. **Later 2026-10-11: four Wiegand-area
   photos received — the macro shot confirms silkscreen `U20` = chip marked
   `HCT08` (SOIC-14), so the finding is photo-verified, not just user-reported**
   (`docs/photos/2026-10-11_u20-hct08-macro.jpeg`); `R128`/`R129`/`FB20` sit
   nearby as untraced pull-up/filter candidates.
- **Board photos identify the companion chip as a Micrel KSZ8995XA 5-port switch
  (2026-10-09).** Six user photos moved to `docs/photos/`; `carrier-3.jpg` and
  `carrier-3-duplicate.jpg` are byte-identical (sha256 `C951CB70…`), so five
  distinct images. Reading them: the LAN section carries a legible
  **`MICREL / KSZ8995XA / 1249M2 / M9242030 / MO2062U0`** — a 5-port 10/100 QoS
  switch between the LAN9512 and the two jacks (silkscreened `LAN1`/`LAN2`).
  **This retires "RJ45 #2 is on the STM8"**: a 5-port switch is the only chip
  that makes two jacks one NIC, which is exactly the symptom that had been
  misread as "wired to the STM8". Row 3 → OPEN, re-scoped to a cable test.
  **93LC66A #2 narrowed but NOT solved** — it sits beside the switch, making it
  the leading candidate owner, but the datasheet documents the config bus as
  **I²C 2-wire (`SCL`/`SDA`, pins 110/111)** and a 93LC66A is **3-wire
  Microwire** — different bus, different part family, and the config interface
  names no `93Cxx`. Also from the photos: an **RTC coin cell is physically
  present** (holder left of the CM4412 module, by `F-RST`), and the module is a
  **CMITECH CPU MODULE Rev 1.0 (2014.02.04), Exynos 4412 `S1T5W11`, sticker
  `CM4412 / CTE03095`**. Datasheet extracts in `docs/raw/ksz8995xa-datasheet.txt`,
  photo readings in `docs/raw/board-photos-raw.md`. **Nothing run against the
  live board**; the RJ45 #2 cable test remains the single decisive next step.
- **eMMC backed up + cloned to SD from the board (2026-10-11).** Backup: full raw
  `dd /dev/mmcblk0` over SSH with board-side gzip → `d:\phl\temp\emmc_backup.img.gz`
  (2.55 GB). PC gunzip+sha256 = exactly 7818182656 bytes, `raw_sha256=70b75811…`,
  gzip CRC OK → **verified safety backup**. Clone: `dd if=/dev/mmcblk0 of=/dev/mmcblk1
  bs=4M conv=fsync` **on the board** (bypasses the Windows raw-write fight) → full
  7818182656 bytes, Dirty=0. **Card hash ≠ backup hash is expected**: eMMC root is
  live-`rw` (cmdline `ro` remounted rw), so backup(T1) and clone(T2) are different
  moments. Boot-critical immutable regions match exactly: **first 16 MB (BL1/BL2/
  u-boot) and first 128 MB (+vfat boot: uImage/boot.scr/dtb) eMMC==SD** → card will
  boot like the eMMC; ext4 journal replays rootfs on mount. **eMMC left in as backup.**
  Confirmed ODROID-**X** (`mem=1023M`). Next: power off → switch→SD → power on → HDMI+ping.
- **RTC diagnosed + 93LC66A #1 proven (2026-10-11).** MCP7940N register dump
  (read-only C probe, `I2C_SLAVE_FORCE`): **oscillator runs, H:M:S ticks, but
  date regs are 0/0/0** → `rtc_valid_tm` rejects → EINVAL everywhere (the old
  "logins timestamped 1970" cause). Fix = `hwclock --systohc`, **not run yet**.
  93LC66A #1: dumped with `ethtool -e eth0` — `0xA5` sig, MAC, USB IDs, `SMSC`
  → **it is the LAN9512's config EEPROM on the chip's own Microwire pins**;
  kernel has no SPI at all, so I2C scanning was the wrong question all along.
  #2 located next to the LAN9512 (user) → companion-chip/switch hypothesis;
  RJ45 #2 cable test is the decider. Checklist: row 14
  BLOCKED → 14 WORKS + 14a OPEN, RTC = row 17 OPEN; **no BLOCKED left**.
  Tools: `mcp7940_dump.c`, `rtc_probe.py`; raw: `docs/raw/rtc-93lc66a-raw.md`.
- **Micro-USB CLOSED — no further work (user decision, 2026-10-11).** Root
  cause was found just before closing: the kernel has **no gadget function at
  all** (`/proc/config.gz`: `CONFIG_USB_GADGET=y` + `S3C_OTGD=y` but every
  `g_*` `not set`, zero `g_*.ko`). From a Linux PC the board attaches then dies in
  an enumeration loop (`error -110/-71`) — **the same failure Windows calls
  Code 43**, reproduced on two OSes. Fix would need a kernel rebuild; accepted
  as-is instead. Checklist: row 12 → **CLOSED**, counts 12/2/1/1 (PARTIAL
  bucket retires). **Reopen only if a kernel rebuild is approved.**
- **Micro-USB identified from a Linux PC** (board repowered into Android
  mode): enumerates as `18d1:0002 Android 1.0`, interface `FF/42/03` = ADB.
  **`adb devices` empty — because the far end is a stub**: raw pyusb probes get
  a flat 4-byte `FAIL` to CNXN/SYNC/AUTH/garbage/even silence. A real adbd
  answers with a 24-byte header. Row 12 downgraded WORKS → **PARTIAL**, retired
  to **CLOSED** later the same day (root cause found, no further work).
  Board is off-network in Android mode.
- **RS485 identified as `/dev/ttySAC2`** by measuring DC across the pair with a
  **control run**: `ttySAC2` 0.646 V → ~220 mV while transmitting (twice);
  `ttySAC3` held 0.646 V identically. Marked **WORKS (TX)** — RX untested.
  Tool: `tools/rs485_probe.py`.
- **RS232 identified as `/dev/ttySAC3`** by one-wire loopback + control.
- **Debug port identified as `ttySAC1`**, and its console output is drivable:
  `echo X > /dev/console` (+17 bytes) and `wall` (+495 bytes) both move
  `ttySAC1 tx`. Writing to `/dev/kmsg` does **not** reach it — different path.
- **Desktop reference line** now shows all three UARTs; deployed and running.
- **Board power-cycled several times by the user** (confirmed intentional, not
  crashes — no panic/oops/OOM/watchdog). The UI does **not** autostart and must
  be relaunched after every boot.

## Tried and failed — do not repeat
- **Jumper/loopback on RS485**: 5 phases, **0/50 echoes**. Structurally
  impossible on a 2-terminal half-duplex connector — TX and RX are one pair.
  Ask the wire count *before* choosing a test.
- **`TIOCGRS485`**: `EINVAL` on both UARTs. Kernel config has
  `CONFIG_SERIAL_S5PV210=y` only — no RS485 mode, no PINCTRL.
- **Finding a driver-enable GPIO**: the whole system claims 5 pins
  (STATUS LED, Backlight, KEY POWER, hdmi-cec, hpd-plug) — none is DE.
- **Vendor stack as an RS485 path**: `libemaLib` only opens `/dev/ttySAC0` via
  vendored `QextSerialPort`; the event enum has no RS232/RS485 entry.
- **`/dev/ttySTM8` is a trap.** Symlink to `/dev/pts/0`, not a serial port.
- **`/dev/ttyS0..3` are phantoms.** 8250 stubs, `port:00000000 irq:0`.
- **Making the second RJ45 appear in Linux is impossible as things stand.** No
  `macb`/`dwmac`/`stmmac`, no `ethernet@` node in the device tree.
- **`libgpiod`/`gpioget` for the headers** — dead; no gpiochip in this kernel,
  and the pins belong to the STM8 anyway.
- **CMIMIRDemo as a driver for the I/O** — unusable; wants a CMI iris imager
  that is not attached. Still the source of the frame format via disassembly.
- **Assuming a send succeeded** — cost hours. The STM8 silently refuses
  valid-looking frames; only status/ack tells the truth.
- **Single-mask GPO frames / bare OUT2 close** — silently refused. Always mask
  both channels; OUT2 close needs the prep frame.
- **Writing to `/dev/kmsg` to drive the console** — does not reach `ttySAC1`.
  Use `/dev/console` or `wall` instead.
- **Launching the UI with `setsid ... &` alone** — silently produced nothing.
  Needs `DISPLAY=:0` **and** a detached `nohup setsid` with output redirected.

## Open questions
- [ ] What is class `02` (`55 05 02 03 <value>`)? Accepted, varying replies,
      no device identified.
- [x] ~~Where are the two 93LC66A EEPROMs wired?~~ **#1: the LAN9512's config
      EEPROM, dumped with `ethtool -e eth0`. #2: located by the user — right
      next to the LAN9512** (reported 2026-10-11). Remaining: which chip owns
      it — test = live cable in RJ45 #2 vs `ethtool eth0` (switch hypothesis).
- [ ] Did `hwclock --systohc` get run yet? (RTC date regs are 0/0/0; fix known,
      pending the user's go.)
- [ ] Does the RTC hold across a power cut — is there a battery?
- [ ] Who set the system clock at boot when `hctosys` failed and no NTP runs?
- [x] ~~Are RS232/RS485 on the STM8, or do they bypass it to the SoC?~~
      **Both bypass it** — RS232 = `ttySAC3`, RS485 = `ttySAC2`, each proved
      with a control run.
- [ ] RAM was 916 MB of 991 MB in use with no swap — real, or a leak?

## Active decisions
- Facts are **re-measured on demand**, never carried in prose (`docs/raw/`).
- Probes are read-only; **actuation is deliberate and confirmed** — every
  frame is verified from the STM8's status/ack before it counts.
- `/dev/ttySAC1` is **never opened** — it is the console and holds a live
  `login`+`bash`; opening it can hang a headless board. Drive it only via
  `/dev/console`.
- Dead work is **archived, not deleted** (`archive/`).
- **A send is never success** (silent refusals) — the UI retries 3x and shows
  the board's report, never the click.
- **A needle that moves needs a run that should not move it** — every
  identification so far (RS232 loopback, RS485 differential) was confirmed by a
  control.
