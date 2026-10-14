# Changelog

Newest at top. One entry per completed task.

## 2026-10-14 (5) — Board production folder + agent config bundle

Turned the board into a clean, self-contained project home for continued work.

- **Board `/data/phl` re-created from a fresh clone** of `origin/main` (GitHub),
  replacing the CRLF-corrupted working tree left by the earlier Windows tar
  transfer. Production move: GitHub is the single canonical source; the board
  is a clean checkout, not a hand-copied tree.
- Ships the **`.cline/` agent config** (global `rules/`, `templates/`,
  `tools/`, `skills/`, `plugins/`) into the project so Cline runs fully on the
  board when SSH'd into `/data/phl`. `~/.cline/data/` telemetry (90 MB) is
  intentionally excluded.
- HMI Settings page switched to **multi-column layout** (`index.html`: the
  HMI/Display/Security cards wrapped in `.grid`; reuses the existing
  responsive grid, no field types changed). Live on the board at
  `/data/chroot14/data/nodered/static/` (byte-identical, SHA-256 verified).
- Tested: board `git clone` → clean `git status`, `.cline/` + `vendor-snapshot/`
  present, LF endings. Windows `git status` clean, pushed to origin/main.
- Not tested: nothing further pending; visual multi-column already confirmed
  earlier on hardware. `.cline/machine.md` carries the dev-machine Windows
  username (`C:\Users\PC`) — flagged on a public repo, scrub if desired.

## 2026-10-14 (4) — HMI Settings: idle screen blank

Added a display blank/sleep control to the HMI Settings page.

- **Settings → Display → "Screen blank"** select: Always on / 30 s / 1 / 2 / 5 / 10 min.
- Choice persists in `localStorage` (`hmi.blank`, seconds; `0` = never), survives reloads.
- After the idle timeout with no touch/click/key, a full-screen black overlay
  (`#blanker`) covers the panel; any input wakes it and restarts the countdown.
- **Not gated by the controls lock** — it is a local display preference, not a
  hardware command, so it stays active while hardware controls are locked.
  No backend call; purely a CSS overlay in `static/`.
- Ceiling: this is a *software* blank (black overlay), not real backlight
  power-off. True DPMS/backlight-off is the upgrade path (`xset dpms` / board
  backlight API behind `/api/cmd`) once the logic workflow unlocks commands.
- Tested: `node tests/blank_check.js` → 13 passed, 0 failed (real `app.js`
  driven through `vm` with a fake clock + DOM/localStorage shim).
  `node --check os/node-red/static/app.js` → OK.
- Not tested: visual blank/wake on the physical 1024x600 panel (needs board).

## 2026-10-14 (3) — Git compatible + published to GitHub

Repo made push-ready and the production baseline published to a real remote.

- **Added `LICENSE`** — MIT, canonical author `Nadeem`, year 2026.
- **Added `project.json`** — name `PHL`, description, author, license, created date.
- **Remote `origin`** — `https://github.com/zahidprinters/PHL.git`.
- **Pushed** branch `main`; local now tracks `origin/main`, fully in sync.
- Commits: `2de1f08` (production baseline, 150 files) + `8ae2715` (LICENSE + project.json).

Why: a repo needs a LICENSE and metadata before its first public push;
workflow rule "Every new project needs a LICENSE before its first push".

Tested: `git push -u origin main` → `* [new branch] main -> main`,
exit 0; `git status -sb` → `## main...origin/main` (in sync).
Not tested: GitHub auth is HTTPS credential-manager cached; a fresh clone
from another machine will need that account's credentials.

## 2026-10-14 (2) — Production tone: dev phase closed, reference set frozen, git baseline rebuilt

Development phase ends; from now on only the **screen (SPA) and Node-RED**
are worked on, with all board hardware accessed through Node-RED.

- **Reference set frozen (kept on purpose):** `tools/` (44 files: README-tool
  table + STM8 frame recipes `ema_*` + board infra + vnc_shot), `docs/` (BOARD,
  VENDOR-PROTOCOL, HARDWARE-COMPLETE, `raw/` evidence, photos), `logs/` raw
  captures, `session-archive/`, `vendor-backup/` (pristine, untouched),
  `os/` (eMMC backup, node-red stack, desktop config, scripts, vendor-snapshot),
  `memory-bank/`, `CHANGELOG.md` + `CHANGELOG-archive.md`.
- **Repo clean pass:** `temp/` deleted — 183 MB / 4339 files (the node-v10.24.1
  tarball extract, already installed on the board); zero-byte junk removed
  (root `dmesg`, `docs/raw/ema-probe-raw.md`, `logs/ab.log`, `logs/ema_build.txt`,
  `logs/emmc_backup.err`); 2 hash-verified duplicates removed
  (`docs/photos/carrier-3-duplicate.jpg` == `carrier-3.jpg`,
  `logs/emmc_backup.out` == `os/backup-eMMC/emmc_backup.log`).
- **`tools/` triage — 8 closed-question probes moved to
  `archive/board-oneoff-probes/`:** `board_gui_probe.py`, `board_ema_capi.py`,
  `board_ema_disasm.py`, `board_ema_probe.py` (mining absorbed into
  `docs/raw/libemaLib-*`), `gpio_scan.c` (no gpiochip in this kernel),
  `rs485_pins.py` / `rs485_recon.py` / `rs485_phase.py` (superseded by
  `rs485_probe.py`). Only CHANGELOG (historical) cites them now.
- **eMMC backup VERIFIED:** `os/backup-eMMC/emmc_backup.img.gz` = 2,546,914,166
  bytes; SHA256 recomputed live = `a7bb2f504bd84b429d3add41456acaa06fd76ca563d9246a6f84a7d5ad6a09af`
  == the `sha256_gz` recorded in `emmc_backup.log` at capture time. Log tail:
  `7818182656 bytes (7.8 GB) copied, 802.619 s, 9.7 MB/s`.
- **`.gitignore` extended** with a Backup-images section (`*.img`, `*.img.gz`,
  `*.raw`) — project **and** the shared template at
  `~/.cline/templates/gitignore` (the 2.4 GB backup must never stage).
- **Git re-initialized** as the production baseline: the old `.git` disappeared
  mid-session earlier (never deleted by any command here), so this is a fresh
  `git init` + first commit — history restarts at this entry, canonical author.

### Tested
    temp/ count after delete = 0. Duplicate removals gated on SHA256 equality (both True).
    Backup hash recomputed (Get-FileHash) == recorded sha256_gz in emmc_backup.log.
    8 moves done, tools/ now 44 files; grep proved no live doc cites the moved files
    (CHANGELOG history only). git status after baseline commit = clean, *.img.gz not staged.
### Not tested
    Board-side production pass (board /root leftovers, desktop-app archive, /root snapshot
    tar) — NOT done yet, PHL_BOARD_PASS not available this session; board cleanup runs next
    session after the password is set. README tool table re-verified against tools/ only by
    grep, not line-by-line.

## 2026-10-14 — HMI pivot v1.0: dashboard removed, custom SPA served by Node-RED, cold-boot verified

Strategic pivot: node-red-dashboard (Angular-1, 15-30 s loads on the 2012 ARM,
FF52 LESS-compile styling bugs) is a dead end for a modern look — replaced with a
**hand-written vanilla-JS SPA** served by Node-RED itself. Node-RED stays the
backend/webserver; all logic goes in flows.

- **Board — clean pass first** (per request): 107 debug files removed from
  `/root` (old logs/sh/py/json), `/var/log` rotated logs, apt cache 26 MB
  (`clean`+`autoclean` only — `autoremove` deliberately NOT run, it can pull
  libs the running desktop needs), FF crash dumps + caches. The old EMA-era
  hardware-probe code (`ema_*`, `pmic_*`, `rs485_*.pyc`, 59 files — reverse-
  engineered, no git copy on board) **archived to `/root/old-hw/`, not deleted.**
- **Dashboard removed:** `node-red-dashboard` uninstalled from userDir; tar
  backup at `/data/node-red-dashboard-2.29.3.tar.gz`. All `ui_*` nodes removed
  from the flow first (deploy-before-delete: no missing-node errors).
- **New flow** (`os/node-red/hmi-flow.json`, 9 nodes): inject 1 s → `build state`
  (placeholder state JSON in flow context — clock, mode, alarm, modbus, devices,
  io arrays, raw regs, `locked:true`) → `GET /api/state`; `POST /api/cmd` =
  locked stub answering `{ok:false, error:'locked'}`.
- **settings.js patched** (backup `settings.js.bak-v1`): `httpAdminRoot '/red'`
  (editor moves), `httpStatic '/data/nodered/static/'`.
- **SPA v1.0** (`os/node-red/static/`: index.html 9 KB, app.css 8 KB, app.js 7 KB):
  6 tabs — Home (time/date/mode/setpoint cards), I/O (8 DI + 8 DO LEDs, analog
  in/out tables), Manual (override switch + DO toggles + AO sliders), Settings
  (language/role/units/theme/PIN — all `disabled`), Info (IP, Modbus params,
  device list), Raw (register table + 0…4095 scaling table). **Every control is
  grey/disabled** until the logic workflow flips `locked`. 1 s poll, LINK chip,
  data-age footer, FF52-safe subset (no optional chaining, no flex `gap`).
- **Kiosk pointed at `/`:** homepage in user.js/prefs.js, `restart_ff.sh`, and
  both openbox autostart files (`/etc/X11` + `/etc/xdg` — the real kiosk
  launcher; a stale gnome autostart experiment was removed to avoid double start).
- **Gotchas found the hard way:** `httpStatic` must be **absolute from the
  chroot's view** (`/data/nodered/static/`, NOT `/data/chroot14/...` and not
  relative — express.static uses cwd); `process` is not defined in the old
  function-node sandbox (uptime now tracks `t0` in flow context); board SFTP
  uploads need `sync; sleep 3` before exec sees the file; an `httpStatic`
  sed with unquoted path produced invalid JS — patch via script file, not
  inline sed.

### Tested
    Board clean pass ran (root listing shrunk, 26 MB apt cache freed). Flow loads with no
    errors after dashboard removal. GET /api/state returns full JSON; GET / = 200 (9064 B);
    POST /api/cmd = locked stub; editor at /red = 200. **Two full cold boots:** power-on →
    nodered (upstart) + openbox + firefox `http://localhost:1880/` auto-start in ~2 min,
    VNC screenshot shows fullscreen SPA (clock ticking, uptime counting, LINK OK, CONTROLS
    LOCKED). node --check passed on app.js.
### Not tested
    Real 1024×600 panel fit (screenshots are the 1920×1080 virtual screen; the
    `max-height:700px` media query is unverified on hardware). Other tabs (I/O, Manual,
    Settings, Info, Raw) render logic is code-reviewed but only Home was screenshotted —
    click-through each tab on the real panel. `git` status: `.git` disappeared from
    `D:\phl` mid-session (not by any command in this session) — version control needs a
    fresh `git init` when the user wants it.

## 2026-10-14 — Kiosk rc.xml syntax-error dialog fixed (stock file + injected rule)

The message showing behind the dashboard was an **"Openbox Syntax Error"**
dialog (window `0xc000ff`, at +672+358). Root cause: the `kiosk-rc.xml`
deployed 2026-10-13 was a **minimal partial openbox config** — openbox 3.5
refuses to parse it, so (a) the Firefox borderless/fullscreen rule never
applied and (b) openbox popped the error dialog at session start.

Fix: rebuild the config **from the stock `/etc/xdg/openbox/rc.xml` (23 KB,
known-good)** and inject only the two Firefox `<application>` rules right
after `<applications>`, then `openbox --reconfigure`. Verified:
- `xwininfo -root -tree | grep -c 'syntax error'` → **0** (dialog gone)
- VNC screenshot: dashboard now **borderless + fullscreen**, no error.

**Repo:** `os/desktop/kiosk-rc.xml` replaced with the stock+rule version
(23,800 B) so the broken partial file is never re-deployed.

Still open (unchanged, separate issue): **FF52 renders `/ui` magenta with no
widgets** — the dashboard theme CSS compiles client-side from `app.min.less`
and that compile fails in FF52. Dashboard structure loads (the "HMI" tab
shows) but widget styling is stripped. Next session's HMI task.

### Tested
    openbox --reconfigure clean; error-dialog count 0; dashboard fullscreen in the VNC grab.
### Not tested
    The magenta/widget-styling issue (FF52 LESS compile) — not addressed here. The 1024x600 panel
    fit still needs the u-boot bootargs change (fb6 is the HDMI-mixer fb, boot-time only — a
    runtime ioctl mode-set was refused, confirmed 2026-10-14).

## 2026-10-13 — Node-RED dashboard installed + HMI kiosk (autostart fires the dashboard, not EMA_Controls)

Session goal: make the Node-RED **dashboard** the appliance UI instead of the PyQt
EMA_Controls app — full-screen, no bars/window chrome — so the screen is a pure
web HMI. Node-RED was already running in the trusty chroot; this added the
dashboard module, a starter flow, and a kiosk launch.

- **Board — dashboard installed** into the Node-RED **userDir** (correct place for
  node-red-dashboard, NOT global): `/data/chroot14/data/nodered/node_modules/
  node-red-dashboard` (+ its deps: gridstack, socket.io, jquery…). `npm ls -g`
  shows nothing because it is a local install — verify with
  `ls /data/chroot14/data/nodered/node_modules/node-red-dashboard`.
- **Board — HMI flow deployed** (`hmi-flow.json`, 1264 B): a `ui_tab` "HMI" +
  `ui_group` "Status" + inject(5s) → clock `ui_text` + random `ui_gauge`.
- **Board — kiosk launch** replaces EMA_Controls.sh in the openbox session:
  - `autostart` now runs `vino-server &` + `firefox http://localhost:1880/ui &`
    (EMA_Controls.sh is still on the desktop for manual launch over VNC).
  - FF52 has **no `--kiosk` flag**, so fullscreen/borderless is forced by an
    openbox window rule: `/root/.config/openbox/rc.xml` (class Firefox →
    `decor no` + `fullscreen yes`).
  - A hardened FF52 profile `user.js` (`/root/.mozilla/firefox/fdg2sjwb.default/`)
    kills every prompt/infobar/telemetry/update that could appear over the HMI.
- **Repo:** archived to `os/node-red/hmi-flow.json`, `os/desktop/{autostart,
  kiosk-rc.xml, kiosk-user.js}`; a new `tools/vnc_shot.py` grabs the VNC
  framebuffer as PNG for visual checks.

### Tested
    initctl status nodered → start/running (PID 1257); dashboard module present in
    userDir node_modules; flow file on disk; autostart = vino + firefox /ui;
    rc.xml Firefox rule present; http://127.0.0.1:1880 answers. VNC screenshot
    earlier this session DID render the HMI flow (MODE MANUAL / OUT1 / OUT2 /
    IN1 / IN2, theme "ECU-30 HMI").
### Not tested / OPEN (next session)
    1. **Flow-file name mismatch (must fix first):** settings.js (board + repo)
       says `flowFile: 'flows.json'`, but the only flow on disk is
       `flows_linaro-ubuntu-desktop.json` (the default hostname name) and
       `flows.json` does NOT exist. A clean restart reads settings.js → looks for
       flows.json → finds none → serves an EMPTY dashboard. Reconcile: either
       rename the flow file to flows.json, or drop the `flowFile` override so
       Node-RED uses its default name. Verify which file the running PID 1257
       actually loaded (`/proc/1257/cwd`, or its startup log).
    2. **FF52 client-side LESS compile → magenta / unstyled /ui.** The dashboard
       theme CSS compiles in-browser from `app.min.less`; if that fails in FF52
       all widget CSS vanishes (this is the pink screen). Was mid-hunt: next
       check `main.backgroundColor`/`uiTheme` resolution in the dashboard server
       and whether an explicit theme sidesteps the broken default.
    3. Kiosk fullscreen on the real panel and the actual dashboard widgets were
       seen once; a post-power-cycle check (No Signal → firefox /ui fullscreen,
       no chrome) has NOT been re-confirmed.

## 2026-10-13 — fb-early + boot splash REVOKED (user decision) — boot back to "No Signal until the app"

Second power cycle: **still no splash and boot-to-app felt slower** — and the
boot log proves the job again **never executed python** (`cannot create
/var/log/upstart/fb-early.log: Read-only file system`, `pixclk` lines in
dmesg: 0). So even `start on started mountall` is too early on this vendor
image — the rootfs remount-rw happens later than mountall, through some path
not yet identified. Rather than keep chasing, the user called it: revoke.

- **Board:** job stopped, `/etc/init/fb-early.conf` → `.disabled`,
  `/root/fb_early.py` + `/root/splash.raw` + the log deleted;
  `initctl reload-configuration` → `Unknown job: fb-early`. Session +
  Node-RED verified unaffected. Boot is back to the original behaviour:
  **"No Signal" until Xorg/EMA UI (~20 s)**.
- **Repo:** the experiment's files stay in `os/desktop/` as an archived dead
  end (per the "kept, not deleted" rule), table rows marked REVOKED.
- **Open again:** power-on "No Signal". Known paths forward if ever wanted:
  u-boot env via serial console (real fix, sets fb_x_res/fb_y_res properly),
  or an fb-early job anchored on whatever event actually remounts rw — but
  this is **parked** unless the user reopens it.

### Tested
    Revoke: `initctl status` → Unknown job; files absent; `pgrep openbox` + HTTP :1880 OK. Nothing else touched.
### Not tested
    The next power cycle should look exactly like the pre-fb-early boots (No Signal ~20 s → EMA UI). Not yet watched.

## 2026-10-13 — The splash (and the whole fb-early job) NEVER ran at boot: CRLF .conf + read-only rootfs — fixed

User power cycle: **"No Signal" straight to the app, no splash** — exactly the
risk flagged in the previous entry. Diagnosis found the job had never
executed once at any boot (not even the original black-screen version):

- **Root cause 1 — CRLF line endings.** The upstart .conf files were written
  by the Windows-side editor with CRLF. dash parses `…2>&1\r` as a redirect
  to a bogus fd → `Syntax error: Bad fd number`, or in the boot case dies one
  step earlier on the append (see below). Both repo copies converted to LF
  (`fb-early.conf` 19 CRLF pairs, `fb_early.py` 148 — python tolerated them,
  dash did not).
- **Root cause 2 — `start on startup` fires while `/` is still read-only**
  (cmdline `ro`, mountall remounts later): `>> /var/log/upstart/fb-early.log`
  failed with "Read-only file system" (the 3 lines found in the log) and sh
  aborted before python. dmesg across all boots has **no pixclk line** —
  proof the mode-set never executed.
- **Fix:** LF-only conf; job now `start on started mountall` (rw guaranteed,
  ~2-3 s in); and since the monitor only reports HDMI online **~17 s** into
  boot (this boot's dmesg: `HDMI_STATE=online` at 16.82 s) with hotplug able
  to renegotiate the pipeline, `/root/fb_early.py` now **re-paints every
  second until `/tmp/.X0-lock` appears (X owns the fb) or 60 s pass**,
  logging only state changes.

### Tested
    Live (job via upstart, not hand-run): `start fb-early` → `start/running`, log `splash shown (1024x600, 2 halves)`, dmesg `pixclk is changed from 19528 Hz to 6734 Hz`, fb md5 == splash md5 (`37301679…`) across the loop; timeout path logged (`gave up after 60 s`); X-takeover path logged (`X took over`) and job exits cleanly when X owns the fb; session + Node-RED :1880 + VNC :5900 back afterwards. Board files verified CR-free (0 bytes).
### Not tested
    **The real power cycle again** — expected now: `started mountall` fires, splash within seconds of HDMI online (~17 s), gone when the EMA UI appears (~20 s). Also unverified: behaviour if mountall itself fails (job would simply not start; acceptable).

## 2026-10-13 — Boot splash replaces the fb-early black screen ("ECU-30 HMI — Starting…")

The `fb-early` job cleared the screen to black; it now paints `/root/splash.raw`
instead (dark gradient, "ECU-30 HMI", accent bar, "Starting..."). The image is
generated on the PC by **`os/desktop/make_splash.py`** (Pillow) — the board only
copies bytes, no image library needed on-board.

- **Driver truth found while wiring this up:** fb0 is a **1024x600@32 window
  buffer** (stride 4096, smem 4,915,200 B = both halves of a double buffer)
  that the **FIMD scaler stretches to the 1920x1080 HDMI output** — sysfs
  `virtual_size` reports the OUTPUT, the var GET reports the buffer geometry,
  and the fix `line_length` field reads garbage in this vendor struct
  (u32 @42 = `0x10000000`). Hence: splash generated at buffer size
  (1024x600 → 2,457,600 B, md5 `373016796348e960588e347c34b1e1ad`) and written
  into **both** buffer halves so it shows regardless of pan position.
- Repo copies: `os/desktop/make_splash.py` + `os/desktop/splash.raw`
  (regenerate = re-run the script, then re-upload both raw + fb_early.py).

### Tested
    Live, without a power cycle: `stop lightdm` → `python2 /root/fb_early.py` → `fb_early: splash shown (1024x600, 2 halves)`, RC 0; **mmap'd framebuffer md5 == splash.raw md5 exactly** (`373016796348e960588e347c34b1e1ad`); sysfs `1920,1080` @32 intact; `start lightdm` → session back (X, openbox, vino, ema_ui) and Node-RED HTTP on :1880. `py_compile` clean. (First attempt had failed on a stale 1920x1080 assumption: splash size 8.3 MB > mmap cap → correctly fell back to black.)
### Not tested
    **The visible splash at a real power cycle** — pixel content is proven in fb memory, but whether the scaler displays it on the monitor (and how the 1.9×-scaled text looks) needs the user's eyes. Expected: title card with signal within a few seconds, EMA UI at the same ~20 s as before.

## 2026-10-12 — "No Signal" at power-on fixed: early HDMI mode-set job (black 1080p from ~5 s instead of a dead screen until X at ~20 s)

The monitor showed "No Signal" for the first ~15-20 s after every power
cycle — long enough to look broken. Root cause (measured):

- The u-boot on this board runs its **built-in default environment** — none
  of the boot-partition scripts are sourced (their contents don't match the
  running cmdline; verified against `boot.ini`, `boot.txt`, `boot`,
  `boot-hdmi1080.txt`). The kernel therefore gets **empty
  `fb_x_res/fb_y_res/hdmi_phy_res`** bootargs.
- s3cfb registers at 0.44 s with its fallback mode **1024x1200** (pixclk
  19528), the HDMI PHY + mixer probe by 2.8 s and the monitor is detected
  online at 9.7 s — but that mode cannot be clocked out, and this kernel
  has **no framebuffer console** (`CONFIG_FRAMEBUFFER_CONSOLE is not
  set`), so nothing mode-sets the pipeline until **Xorg starts (~15-20 s)**.
- Fix (no u-boot changes — those need a serial session): upstart job
  **`/etc/init/fb-early.conf`** runs `/root/fb_early.py` on `startup` —
  `FBIOPUT_VSCREENINFO` with explicit 1080p60 CEA timings (6734 ps
  pixclock), then an mmap-cleared black screen. Signal within a few
  seconds; Xorg takes over later exactly as before (same mode).
- Side-findings: this vendor s3cfb **refuses fb `write()` (ENOSPC)** — the
  screen clear must use **mmap**; and the ioctl GET immediately after PUT
  reports a mixed per-window state while sysfs shows the real 1920x1080.
  Repo copies: `os/desktop/fb-early.conf` + `os/desktop/fb_early.py`.
- Also noticed, **not fixed**: on cold boot the RTC has lost its date — the
  board starts in **2001** and something resets the clock to real time
  mid-boot. Separate issue; the long-pending `hwclock --systohc` applies.

### Tested
    Live, without a power cycle: `stop lightdm` → `python2 /root/fb_early.py` → RC 0, dmesg `s3cfb s3cfb.0: pixclk is changed from 19528 Hz to 6734 Hz`, sysfs `fb0/virtual_size` = **1920,1080**; `start lightdm` → session fully back (X :0, openbox, vino-server, python2 ema_ui all running); Node-RED HTTP 200 and VNC 5900 from the PC afterwards. `py_compile` clean. First attempt failed with fb `write()` → ENOSPC; mmap version passes.
### Not tested
    **The real cold boot** — the job is installed (`start on startup`, log `/var/log/upstart/fb-early.log`) but the panel's behaviour at the next power cycle needs the user's eyes: expect a **black screen with signal within a few seconds** (no more "No Signal"), EMA UI at the same ~20 s as before. Behaviour on a non-1080p monitor untested (fixed 1080p by design).

## 2026-10-12 — VNC opens directly: Allow/Deny prompt + connect notification off, no password

Every VNC connection used to pop the vino dialog (Allow/Deny, "another user
is trying to access the desktop") before you could get in. Fixed at the root:

- **Root cause of the popup surviving the 10-11 "fix":** vino **3.4.2**
  configures through **GSettings/dconf (`org.gnome.Vino`)**, not GConf. The
  earlier `gconftool-2` keys under `/apps/vino/...` are **dead leftovers**
  (vino ships an `org.gnome.Vino.convert` GConf→GSettings migration file;
  no gconfd runs) — writing there never had any effect.
  `org.gnome.Vino prompt-enabled` defaults to **true** → your dialog.
- **Changes (root; persist in `/root/.config/dconf/user`):**
  `prompt-enabled=false` (no Allow/Deny dialog),
  `notify-on-connect=false` (no connect notification),
  `icon-visibility=never` (no floating tray icon on the bare screen).
  Already correct, untouched: `authentication-methods=['none']` (no
  password) and `view-only=false` (full control).
- vino-server restarted after the change (single instance on :5900 —
  second start is refused by its own guard).

### Tested
    Baseline before the change: raw RFB handshake to :5900 while connected showed the dialog in `xwininfo -root -tree` — `0x1200074 "Question": ("vino-server" "Vino-server") 640x177`. After the change, identical test: **no Question window at all**; handshake completes `SEC_TYPES [18,1] → chose 1 (None) → SECR 0`, connection held 6 s. Readback: `prompt-enabled false`, `notify-on-connect false`, `icon-visibility 'never'`, `authentication-methods ['none']`, `view-only false`. Tray icon window `Map State: IsUnMapped`. dconf DB rewritten (02:18). One transient: right after restart the port showed connection-refused for a few seconds (bind race) then steady LISTEN.
### Not tested
    The user's actual VNC viewer from the PC — expect straight in, no dialog, no password (confirm on next connect). Cold-boot persistence of `/root/.config/dconf/user` (it's a normal rootfs file; not yet re-tested after a power cycle).

## 2026-10-12 — Desktop stripped to a bare openbox appliance: 1160→637 packages, 1.2G→776M, no desktop chrome; VNC + EMA UI + Node-RED verified from the PC

The board is now an HMI appliance: **Node-RED (http://192.168.100.127:1880)
is the interface**; the X session exists only to host vino (VNC) and the
EMA touchscreen app — no panel, no menu, no wallpaper, no status bar.

- **Packages: 1160 → 637** (rootfs 1.2 GB → **776 MB** used, ~430 MB freed).
  Three gated passes, each `apt-get -s`-simulated first:
  1. ~310 explicit desktop/gnome/ubuntu leftovers purged (no-conflict sim).
  2. 219 autoremove orphans — run in 3 gated rounds protecting a keep-list
     via `apt-mark manual`: vino + its libtelepathy-glib0/libappindicator3-1/
     gconf stack, lightdm + gtk-greeter, openbox, xterm (+ xbitmaps),
     dbus/x11 basics, python-qt4/python-sip/libqtassistantclient4 (EMA
     runtime), python-serial (board `uart_*.py` tools), NetworkManager,
     xrdp, tightvncserver, alsa/pulseaudio, fonts, gcc/toolchain.
  3. Vendor-held kernel packages unheld, old linaro3.6 images removed.
  - **Two traps:** `python-serial` was apt-auto-flagged — a plain autoremove
    would have silently deleted the board serial tools' dependency (now
    manual). `apt-mark unhold` **segfaults** on this apt (0.8.44) — unhold
    with `dpkg --set-selections` (`<pkg> hold`) instead.
- **Session: LXDE → bare openbox.** lightdm root autologin kept;
  `user-session=openbox` + `/root/.dmrc` Session=openbox + openbox.desktop
  `Exec=/usr/bin/dbus-launch --exit-with-session /usr/bin/openbox-session`.
  - This dbus-launch has no `--exit-with-x11` — only `--exit-with-session`.
  - openbox **3.5** reads `/etc/xdg/openbox/autostart` as **plain shell**;
    the newer `@command` syntax silently does nothing. The whole autostart
    is 3 lines: `vino-server &` + `EMA_Controls.sh &`.
  - The session-start preference is a 3-way fight: `~/.dmrc` outvoted
    lightdm.conf until it and the AccountsService cache both said openbox.
- **Verified live (this session):** after `service lightdm restart` the
  session log shows `Starting session openbox as user root`; **openbox**,
  **vino-server**, and **python2 (EMA_Controls)** all running; from this PC:
  **VNC 5900 TCP ✓, SSH 22 ✓, HTTP 1880 → 200 `<title>Node-RED</title>`**.
  **COLD BOOT VERIFIED** after the user's power cycle: openbox session,
  vino-server, `/root/ema_ui.py`, and node-red all auto-started unattended.
- Board-side session config archived in **`os/desktop/`** (autostart,
  lightdm.conf, openbox.desktop, dmrc-root).

### Tested
    `dpkg -l | grep -c '^ii'` → 637; `df -h /` → 776M of 5.3G (16%). Sim-first purge (no conflicts, exit 0) and 3× gated autoremove (exit 0 each). Post-restart process list: openbox + vino-server + python2 (EMA UI); session-start log line quoted above. PC probes: `Test-NetConnection :5900` True, `:22` True; `Invoke-WebRequest :1880` → 200. **COLD BOOT VERIFIED (user power cycle, `uptime` 9 min):** lightdm→openbox session, vino-server, `/root/ema_ui.py`, and node-red all auto-started unattended (initctl `start/running`, processes started at 01:53); PC probes re-run after that boot → HTTP 200 + VNC 5900 True.
### Not tested
    VNC visual check by the user (bare screen, EMA window, no chrome). Touchscreen input and audio playback after the strip. The still-pending `/data` cleanup (remnants of `/data/chroot` + uploaded tarballs).

## 2026-10-11 — Node-RED 1.3.7 HMI installed and running in a Ubuntu 14.04 armhf chroot; cleanup incident: board needs power cycle

Node-RED is **live on the board at http://192.168.100.127:1880** (HTTP 200 from
this PC, editor loads). Stack on `/data/chroot14`:

- **Ubuntu 14.04.5 base armhf** (SHA256-verified `4fb183c9…`, official cdimage
  hash) at `/data/chroot14`, **Node v10.24.1** at `/usr/local/node10` inside it.
- **Why 14.04, not 16.04:** the 16.04 armhf glibc's startup `uname` check
  rejects kernel 3.0.68 (`FATAL: kernel too old` — armhf baseline is ≥3.2) and
  fails **every** binary including `/bin/echo`. 14.04's glibc 2.19 passes.
- **GLIBCXX fix:** trusty's libstdc++ (GCC 4.8) is one symbol version short for
  node 10 (`GLIBCXX_3.4.20`); copied `libstdc++.so.6` + `libgcc_s.so.1` from
  the (discarded) 16.04 tree — both are forward-compatible on glibc 2.19.
- **apt in the chroot:** EOL trusty armhf lives on **`ports.ubuntu.com`**
  directly — `old-releases.ubuntu.com` has **no trusty at all** and no
  `ubuntu-ports/` tree (verified by directory listing).
- **Node-RED 1.3.7** (last line supporting node 10) via `npm install -g
  node-red@1.3.7 --unsafe-perm`; 301 packages; bcrypt (optional, admin
  password hashing) and **serialport** skipped — no compiler in the base chroot
  and prebuilt fetch failed; the serial node type stays unloaded, EMA/serial
  I/O will go through exec + the proven host python tools instead.
- **Auto-start:** upstart job `/etc/init/nodered.conf` (`start on filesystem`,
  respawn, binds /proc /dev /sys into the chroot pre-start, unmounts
  post-stop). Repo copies: `os/node-red/`.
- **Gotcha found the hard way:** SSH's exec environment has an **empty PATH**
  — everything inside chroot invocations needs an explicit
  `/usr/bin/env PATH=…`. And **upstart .conf files uploaded from Windows must
  be CRLF→LF converted first** (a stray `\r` silently turns paths into
  nonexistent ones).
- **Incident — cleanup after the run broke SSH (board awaiting power cycle):**
  `rm -rf /data/chroot` (the dead 16.04 tree) walked into `/data/chroot/dev`,
  a **live bind mount of the host `/dev`** — bind mounts share the
  superblock, so `rm` deleted **real host device nodes** (`/dev/null`,
  `/dev/ptmx` and siblings). sshd's privsep child can no longer open
  `/dev/null`, so every new session is dropped before the banner while the
  listener keeps accepting (TCP 22/5900/3389/1880 all still connect, node-red
  still serves HTTP 200). Recovery = power cycle: `devtmpfs` rebuilds `/dev`
  at boot; the binds were manual mounts and do not persist. **Rule for next
  time: `umount` every bind under a tree before `rm -rf`-ing it — or reboot
  first and delete after.**

### Tested
    In-chroot: `chroot /data/chroot14 /bin/echo OK`; `node -v` = v10.24.1; `npm -v` = 6.14.12; `apt-get update` + `ca-certificates` install (148 certs). `node-red --help` reports v1.3.7. `initctl start nodered` → `start/running`, log shows flows started, `netstat -ltn` shows 0.0.0.0:1880 LISTEN. `Invoke-WebRequest http://192.168.100.127:1880` from this PC → HTTP 200, `<title>Node-RED</title>`. Node-RED still serving (HTTP 200) even after the /dev damage — it runs on pre-opened fds.
### Not tested
    Cold-boot auto-start of the `nodered` upstart job (blocked on the power cycle — that same power cycle is the recovery step). Flow editing/deploy via the browser UI. Any serial/EMA integration from Node-RED. The incomplete `/data` cleanup (remnants + the surviving `chroot14` mount cleanup) — to be redone safely after reboot.

## 2026-10-11 — Rootfs slimmed 3043→1172 MB (1871 MB freed): unity→LXDE, 551 packages purged, vendor binaries archived+removed


Four stages on the live board over SSH, each gated by a removal simulation:

- **Stage 1 (file level): 787 MB freed** — docs/man/help/locales(cached), IME
  data, qtcreator demos, thumbnails, caches + `apt-get clean`.
- **Stage 2 (packages): 198 purged** — vendor packs (`hwpack-linaro-leb-origen`,
  `ubuntu-origen-extras*`), KDE stack (kate, kde-runtime, kdelibs), thunderbird,
  vlc, cups/printer stack, bluetooth, telepathy apps, ubuntuone, update-manager,
  apport/whoopsie, opencv, mpich, qtcreator, games. Traps handled: `vino` depends
  `libtelepathy-glib0` (kept — kills VNC otherwise); held `linux-image*` protected.
- **Stage 2b/2c (apt orphans): 323 purged** — apt's own autoremove list minus the
  protected set (`libkms1` re-marked manual via `extended_states`, old kernels,
  PyQt stack). python-qt4 cascade root-caused twice: `ubuntu-sso-client-qt`
  (rdepends of a removal candidate) and `libqtassistantclient4` (a python-qt4
  hard dep sitting in the orphan set). python-qt4 + python-sip de-auto'd in
  `/var/lib/apt/extended_states` so apt can never cascade-remove EMA_Controls'
  toolkit again.
- **Vendor binaries archived, then deleted** — `CMIMIRDemo` + 3 libs from
  `/usr/local/{bin,lib}` downloaded to **`os/vendor-snapshot/`**, md5-verified
  board↔PC identical (README inside lists all four hashes), then removed from
  the board with the Desktop symlink.
- **Desktop swap: unity → LXDE** — `lxde-core` + `lightdm-gtk-greeter`
  (29 pkgs, 23 MB); lightdm.conf `user-session=LXDE` + gtk greeter, `~/.dmrc`
  Session=LXDE, vino-server added to LXDE autostart; then the whole unity stack
  purged (unity, unity-2d*, lenses/scopes, zeitgeist, overlay-scrollbar,
  unity-greeter — 30 pkgs). **Boot-idle RAM: 546 → 151 MB.**
- **Loose ends:** nanum + wqy-microhei fonts, 94 MB apt lists cache, 74 MB
  apt-xapian cache, /usr/share/gnome/help purged.
- **Totals:** `/` 3043 → **1172 MB used / 3969 MB free (23%)**; packages
  ~1683 → **1160**; apt check clean throughout.
- **Gotcha: warm `reboot` hangs** (no status LED, no screen); power cycle
  always recovers and boots the slimmed OS clean (user-verified: status LED
  normal, LXDE desktop on screen). Suspected Exynos warm-reset quirk, unproven
  — prefer power cycle.
- `tools/board_run.py`: `PHL_BOARD_TIMEOUT` env override (default 120 s; 900 s
  used for bulk ops) + new `--download <remote> <local>` SFTP fetch.

### Tested
    Board-side after every stage + again after the user's power cycle: `apt-get check` OK; `dpkg` audit clean; SSH (:22), vino (:5900), xrdp (:3389) all listening; LXDE session alive (X, lxpanel, openbox, pcmanfm); vino-server starts inside LXDE autostart; ttySAC0 present; WM8960 playback+capture in `aplay -l`; `import PyQt4, serial` OK; EMA_Controls.sh launcher on the desktop; `dpkg -l | grep -c '^ii'` = 1160; dmesg shows only the board's usual WiFi-SDIO probe timeouts. PyQt cascade protection proven by gate (ABORT8/9 fired, fixed, GATE-A-OK passed).
### Not tested
    VNC/RDP user-visible session quality after the desktop swap (processes listen, user has not click-verified VNC yet); warm reboot hang root cause (one occurrence, no debug-port capture); EMA_Controls click test post-swap (Wiegand row etc.); Node-RED not yet installed.

## 2026-10-11 — Upgrade to Ubuntu 14.04.6 LTS checked live on the board — REJECTED (not run)

- **Checked, read-only, on the running board:** `do-release-upgrade -c`
  answers *"New release '14.04.6 LTS' available"* from Linaro 12.11
  (precise/armhf). So the path exists on paper. Boot chain checked too:
  U-Boot loads the vendor **`/media/boot/uImage`** by name, so a trusty
  generic kernel would sit unused in `/boot` — kernel hijack risk is low.
- **Rejected anyway — upgrading would not be safe and would buy nothing:**
  1. **The desktop dies.** The precise-only `dist-upgrade` plan already ends in
     `Remv unity` + `Remv ubuntu-desktop` + `Remv linaro-ubuntu-desktop`
     (proven 2026-10-11); a full release upgrade is a bigger hammer on the
     same Linaro build. **VNC (`vino` 3.4.2) serves that desktop** — losing it
     violates the project's hard requirement *never lose SSH/VNC*.
  2. **The display stack is vendor-built** (2012 Mali/X userspace vs trusty's
     X server ABI) — unverifiable without risking the only display path.
  3. **Trusty in 2026 is also long-EOL** (standard 2019, ESM 2024) — same
     dead archive, zero security gain over precise.
  4. **Kernel stays 3.0.68 either way** (apt-held + boot-script-pinned) — no
     hardware feature, driver or peripheral works better afterwards.
  5. Vendor 32-bit binaries (libemaLib/CMIMIRDemo) would be moving target
     against a whole-new userspace for no gain.
- **Safer alternative recorded:** if a newer userspace is wanted for
  development, bootstrap an armhf Debian chroot on `/data` (51 GB free) —
  the vendor OS, SSH and VNC are untouched, and it can be deleted in one
  command.

### Tested
    Live board checks (read-only): `lsb_release` = Linaro 12.11/precise, `uname -r` = 3.0.68, `do-release-upgrade -c` = "14.04.6 available", `apt-mark showhold` = libkms1 + 3 old linux-images, `df` / = 2.1 G free, /data = 51 G free, `/media/boot/uImage` present, vino 3.4.2 installed.
### Not tested
    The upgrade itself was deliberately NOT run (that is the decision). No full package-plan simulation exists for a Linaro-precise → trusty hop.


## 2026-10-11 — Wiegand read side (W-IN) marked PENDING — deferred to focus on the main board work

- **W-IN is parked, not abandoned.** Everything needed to run the test later is
  written down: U20 = 74HCT08 input path (photo-verified), front-label pinout,
  and the step-by-step plan (meter idle voltage → Arduino D2/D3/GND pulses →
  arm via SET_CONFIG → decode the push frame) in `docs/BOARD.md` §9.
- Marked **PENDING (deferred 2026-10-11)** everywhere it was called "still
  open": `docs/BOARD.md` (§9, W-OUT note, next steps), `docs/ARCHITECTURE.md`,
  `README.md` (both mentions), `os/README.md`, memory-bank (`activeContext`,
  `progress`).
- Checklist counts unchanged: row 9 Wiegand stays **WORKS** — that verdict is
  the proven send side; W-IN was never a separate row.

### Tested
    n/a — documentation status change only, no board interaction.
### Not tested
    The entire W-IN plan remains unexecuted — that is exactly what PENDING records.


## 2026-10-11 — U20 photo-verified: chip marked HCT08 beside W-IN — user report confirmed

- **Four WhatsApp photos of the Wiegand area** moved from the project root to
  `docs/photos/` (`2026-10-11_ecu30-top-powered.jpeg`, `_w-in-area-wide`,
  `_wiegand-area-wide`, `_u20-hct08-macro`) and logged in
  `docs/raw/board-photos-raw.md`. The macro shot shows silkscreen `U20` beside
  an SOIC-14 marked **`HCT08`** — the previously user-reported 74HCT08 is now
  photo-confirmed. Full top view also confirms the powered board and the
  terminal-row silkscreen (`W-IN` · `W-OUT1` · `W-OUT2` · `GPO` · `GPI` · …).
- `docs/BOARD.md` §9's U20 note updated from "user-reported, chip photo
  pending" to photo-verified, with the photo file cited. Open question
  unchanged: the gates' second inputs still need the continuity check;
  `R128`/`R129`/`FB20` are untraced candidates for the on-board pull-ups.

### Tested
    Photo read-back: U20 marking `HCT08` legible in `2026-10-11_u20-hct08-macro.jpeg`; silkscreen positions cross-checked against the wide shots.
### Not tested
    Idle voltage at DATA0/DATA1; second-input continuity; R128/R129/FB20 net tracing — all still pending the hardware session.


## 2026-10-11 — Wiegand input path identified: U20 = 74HCT08 buffer; front-label pinout read

- **User reported a 74HCT08 (quad 2-input AND gate) at silkscreen `U20`,
  between the Wiegand INPUT terminals and the STM8.** Checked against the
  read-side test plan: AND is non-inverting (idle-HIGH / active-LOW pulse
  plan unchanged), HCT inputs are high-impedance (⇒ pull-ups are on-board,
  expect ~5 V idle at DATA0/DATA1 with nothing connected), and the 5 V HCT
  domain re-confirms **Arduino over ESP32-C3**. **Open:** what each gate's
  second input does — tied to VCC = always enabled, wired to an STM8 pin =
  software-gated (pulses blocked while disabled). Continuity recipe recorded
  in `docs/BOARD.md` §9 (inputs 1,2,4,5,9,10,12,13 / outputs 3,6,8,11).
- **Front-panel label photographed** — `IMG_20261011_153945.jpg` moved to
  `docs/photos/`, readings appended to `docs/raw/board-photos-raw.md`:
  WIEGAND INPUT = `+12V OUT · DATA0 · DATA1 · GND` (**never wire `+12V OUT`
  to a logic driver**); label MAC `00:25:FF:FE:44:45` matches `eth0` — same
  unit. `docs/BOARD.md` §9's "W-IN (2 pins)" corrected accordingly.
- **Why:** settles the pull-up / logic-level questions before any wire is
  cut on the pending Arduino W-IN test.

### Tested
    Docs cross-check only: label photo read + 74HCT08 datasheet behaviour. U20 itself not photographed or probed yet.
### Not tested
    Idle voltage at DATA0/DATA1 (predicted ~5 V); continuity of the gates' second inputs; end-to-end pulse pass-through — all pending hardware session.


## 2026-10-14 — Correction: there is NO analog I/O on this board — audio only

- **User confirmed the board has no analog section** — the WM8960 audio codec
  is the only analog-class peripheral (checklist row 10, already WORKS).
  "Analog I/O" removed from the roadmap everywhere it was listed as open work:
  `README.md`, `docs/ARCHITECTURE.md`, `docs/BOARD.md`, `os/README.md`,
  memory-bank (`activeContext`, `progress`, `systemPatterns`).
- The old lead (vendor's float-heavy `writeEvent` loop writing `30` = "reads
  like a 0–100 scale") is **retired** — there is no analog device on this board
  for it to address. The SoC's internal ADC/PWM silicon stays recorded as
  untapped SoC-internal features, not as board I/O.

### Tested
    n/a — documentation correction based on the user's physical inspection of the board
### Not tested
    nothing new — no code change


## 2026-10-14 — Wiegand click-tested end-to-end: both ports, both pins — all work

- **User tested all combinations from the EMA_Controls desktop app** — port 1
  and port 2, on **W-OUT1 (DATA0)** and **W-OUT2 (DATA1)** — every combination
  pulses. Closes the last open bench question from 2026-10-13 ("only port 2
  exercised on pins"). The SEND WIEGAND button works as designed: reader parks,
  send runs, lamps resume, verdict shown.
- **The "can't use the lines separately" question answered:** DATA0 and DATA1
  are one Wiegand channel, not two outputs — 0-bits pulse DATA0, 1-bits pulse
  DATA1, so every card uses both lines by construction. Applications needing
  two independent control lines must use OUT1/OUT2.

### Tested
    EMA_Controls SEND WIEGAND: port 1 & port 2 × W-OUT1 & W-OUT2 pins -> all four pulse, user-confirmed on the bench
### Not tested
    26-bit cards, STM8 parity computation, f12/f14 units, read side (READ_DATA/type-65 reply) — all still open, unchanged


## 2026-10-13 — Wiegand OUT solved end-to-end: `ema_wsend` drives W-OUT 2 live, LEDs verified

- **`tools/ema_wsend.cpp` (new)** — CLI: `./ema_wsend <port> <bits 1..32> <card hex>
  [count] [gap_ms] [f12] [f14]`. Opens the link, does the SET_CONFIG→WRITE_DATA
  handshake per card, checks every `writeEvent` return (0 = sent); no `readEvent`
  (it would block forever — the STM8 sends no unsolicited frames).
- **Handshake proven LIVE**: open → SET_CONFIG `55 0b 02 02 <port> <bits 2B>
  <f12 2B> <f14 2B>` → WRITE_DATA `55 (n+7) 02 01 <port> <bits 2B> <card nB>` →
  close `55 04 01 00`. The STM8 ACKs by **echoing every frame back**; ~9000 cards
  across 30-card / 20-card / flood runs on the bench with **0 refusals**.
- **Halfword endianness RESOLVED: little-endian on the wire** (`24 → 18 00`,
  `100 → 64 00`, `1000 → e8 03`) — the previous entry's "assumed big-endian"
  note was wrong. Captured under `nullwrite.so`; the frames are byte-identical
  to what the vendor serialiser itself produces.
- **Physical output verified on the user's bench (W-OUT 2):** W-OUT1/W-OUT2 are
  **open-collector**. LED wired `+12V → 1k → LED → pin` lights on the pull-low
  pulses; the old `pin → 1k → LED → GND` wiring stayed dark (cannot light an
  open-collector line — proven, not assumed). Idle **LOW after boot** (LED
  steady), **released (high-Z) after close** (LED off); during a write both
  DATA0 and DATA1 pulse — the eye integrates the ~100 µs pulses into dimming.
- **`int writeEvent(...)` confirmed against disassembly @ 0x579c**: returns the
  validator code (−16/−17/−18…−20/−24), −12 null event, −8 serial write fail —
  the checked return in `ema_wsend` is real, not decoration.
- Board checklist **#9 Wiegand → WORKS** (was LINK FOUND): now **14 WORK,
  3 OPEN, 1 CLOSED**. Updated `docs/BOARD.md`, `docs/VENDOR-PROTOCOL.md`;
  raw evidence in `docs/raw/wiegand-send-raw.md`; new generic SSH helper
  `tools/board_run.py` (exec/upload; password from `PHL_BOARD_PASS` only).

### Tested
    LD_PRELOAD=./nullwrite.so ./ema_wsend 2 24 AAAAAA 2 300  -> 6 frames, exact recipe, 0 refusals, nothing transmitted
    LD_PRELOAD=./opentrace.so ./ema_wsend 2 24 AAAAAA 30 700 -> 30/30, every frame echoed (1 run cut by user power-cycle, rerun clean)
    ... ./ema_wsend 2 24 AAAAAA 20 700 / 30 1000             -> 20/20, 30/30, 0 refusals
    flood 3000 cards @5ms, port 2 then port 1                 -> both clean
    bench LEDs (+12V→1k→LED→pin both lines): lit during flood, faded, off at close = physical proof both lines pulse
### Not tested
    26-bit format never run on hardware (24-bit only); STM8 parity handling unknown (bits appear sent as given);
    f12/f14 semantics still unknown (range-checked only, units unknown); W-OUT1 vs W-OUT2 pin mapping not
    distinguished on the block (only port 2 exercised on pins); read side (READ_DATA/GET_CONFIG replies) still not decoded

## 2026-10-13 — EMA_Controls desktop app gains a Wiegand W-OUT test row

- **SEND WIEGAND button** added to `tools/ema_ui.py`. Widgets: port (1/2),
  bits (1–32), card hex (≤8 hex digits, input-masked), count, gap ms. The card
  is big-endian, MSB first; the STM8 does NOT recompute parity, so it is sent
  as given.
- **The button runs the proven `/root/ema_wsend` as a subprocess** rather than
  re-implementing the handshake in Python — one source of truth, and the
  binary is already bench-verified on this exact board.
- **Port arbitration solved:** `ema_wsend` opens `/dev/ttySAC0` itself, so the
  UI's background `Reader` thread is **parked first** — `Reader.pause()` lets
  it finish the current cycle, write CLOSE, close the tty and set a parked flag;
  the worker waits on that flag (≤8 s) before launching the binary, then calls
  `Reader.resume()` in a `finally`. Lamps and frame polling freeze during the
  send and restart on their own. A serial error mid-send is caught and shown,
  never crashes the UI.
- The verdict comes back through the existing `inbox` queue (pumped on the Qt
  main thread) so no Qt widget is touched off-thread: `_wiegand_summary()`
  scans `ema_wsend`'s stdout for the first `refused` line, else `OK — N sent,
  0 refusals`. Button is disabled during the run.

### Tested
    python tools/board_run.py python2 -m py_compile /root/ema_ui.py  -> [exit 0]
    relaunch on DISPLAY=:0 (setsid, detached)                        -> PID 3020 holds /dev/ttySAC0, log empty (no exceptions)
    park/run/resume + inbox verdict wiring                          -> reviewed against Reader.pause()/is_parked()/resume() contracts
### Not tested
    the SEND WIEGAND click itself on the live board (needs the user at the VNC desktop + an LED on W-OUT);
    each widget value not exercised end-to-end — only the code path and a clean launch are confirmed

## 2026-10-13 — libemaLib serialiser fully decoded (jump table), two doc errors corrected

- **`checkWriteEvent` (0x54e0) jump table decoded completely** — 66 entries
  (types 0–65). Types 7–15 and 20–65 are **no-ops**; the real GPO frames come
  from **types 17/18/19** (OUT1/OUT2/BOTH, struct `+49`/`+50`) and the relay from
  **type 32** (`55 05 04 <sel> <state>`). The enum names GPO1/2/12_WRITE and
  RELAY_WRITE (types 8–11) are dead in this library version. Evidence:
  **`docs/raw/libemaLib-jumptable.md`** (new), sourced from
  `docs/raw/libemaLib-disasm.txt` lines 1315–1611.
- **Corrected error codes** (previous entry's `-12/-15/-16/-17/-18/-19/-22/-23`
  list was off by one and mis-assigned): actual returns are `-13` (types 2/16),
  `-16` (no Wiegand session), `-17` (token mismatch), `-18/-19/-20` (SET_CONFIG
  range/order checks), `-23` (state byte > 1), `-24` (ev+8 ∉ {1,2}).
- **Corrected `GPI12_READ`**: it is **not** type 7 (a no-op) — `55 04 06 01` is
  built by **type 65**. Also found `EMAMain::close` zeroes the session fields
  (`this+490..494`), so SET_CONFIG must be redone after every open.
- **Wiegand WRITE_DATA handshake decoded**: SET_CONFIG (type 4) seeds
  `this+490 = ev+10`; WRITE_DATA (type 3) then requires `ev+10 == this+490` and
  `ev+8 ∈ {1,2}` — the frame `55 (n+7) 02 01 <b8> <b10 2B> <card nB>` is built.
  Earlier "types 2–4 emit nothing" was the missing session, not a missing
  implementation.
- **Answered the "6 GPO" question (user, 2026-10-13): no.** Vendor code has
  exactly two GPOs; W-OUT1/W-OUT2 are Wiegand DATA0/DATA1 pulse lines
  (~20 ms burst per card write, then idle HIGH) — not static latchable outputs.
- Rewrote **`docs/VENDOR-PROTOCOL.md`** (complete map + struct offsets +
  handshake + stale-buffer trap), corrected **`docs/BOARD.md`** §9 Wiegand
  table and the open-questions bullet.

### Tested
    static decode of disasm lines 1315–1611, cross-checked byte-for-byte against
    frames captured live earlier (GPO type 17/18/19 frames match exactly)
### Not tested
    no frame sent to the board this pass; SET_CONFIG→WRITE_DATA handshake and
    `55 04 06 01` (type 65) are decoded but not yet transmitted live; halfword
    endianness (helper 0x4ee0) assumed big-endian, unverified

## 2026-10-12 — Vendor protocol framework decoded from libemaLib disassembly

- **Disassembled `libemaLib_arm_1.0.1.so`** (force-thumb) and located
  **`EMAMain::checkWriteEvent` @ 0x54e0 — the STM8 frame serialiser**. It reads
  the event type at struct `+4` and branches via a jump table (`tbh`), building
  the frame at `buf[24]=0x55, [25]=len, [26]=class, [27]=op, [28+]=payload`.
  Full event→frame map + struct offsets recovered and written to
  **`docs/VENDOR-PROTOCOL.md`**.
- **Struct offsets now known:** OUT1=`+49`, OUT2=`+50`, relay sel=`+53`, relay
  state=`+54`, Wiegand value=`+8`, card data=`+10/+12/+14`.
- **Why frames were "silently refused" is now explained:** `checkWriteEvent`
  returns a negative error and builds nothing unless preconditions hold —
  `-22` if a GPO/relay state byte > 1, `-23` if Wiegand `byte@+8` not in {1,2},
  `-15/-16` if the internal Wiegand session field `buf[490]` is 0 / mismatched.
- **Two new leads:** (1) **`GPI12_READ` (type 7) → `55 04 06 01`** — a class-06
  read request we have never sent; the clean way to poll input/output status.
  (2) **Wiegand WRITE_DATA is implementable** but needs a handshake first
  (GET_CONFIG/AUTO_DETECT seeds `buf[490]`) — that was the missing step.
- **Software identity:** CMIMIRDemo is a **face+iris biometric terminal**
  (Haar cascade, `Enroll.db`, voice WAVs) with the EMA I/O layer; the
  `libcmirisLib2` EEPROM/I²C classes belong to the **iris camera over USB**, not
  this board. libemaLib hardcodes `/dev/ttySAC0` via QextSerialPort.

### Tested
    full force-thumb disasm of libemaLib captured (7680 lines) + dynamic symbols
    serializer decode cross-checked against frames already captured live on hardware

### Not tested
    - Static analysis only; nothing sent to the board.
    - GPI12_READ (55 04 06 01) and the Wiegand handshake NOT yet exercised.
    - buf[490] seeding order inferred, not traced end-to-end.

## 2026-10-12 — Complete hardware survey + boot snapshot; full board picture documented

- **Full read-only survey over SSH** (27 sections: identity, interrupts, full
  `dmesg`, `lsmod`, `iomem`, GPIO, I²C/SPI/UART/USB, audio, network + EEPROM
  dump, RTC, buttons, storage, thermal, kernel config, vendor stack). Raw saved
  to `docs/raw/board-full-survey-raw.md` — **this is the boot snapshot for
  reference/analysis.** Interpreted into the new master doc
  **`docs/HARDWARE-COMPLETE.md`**.
- **New findings this pass:**
  - The kernel is **board-file based, no device tree** (`/proc/device-tree` empty,
    `Hardware=ODROIDX`) — wiring is hard-coded in C; there is no DTB to edit.
  - **SoC ADC present but driverless**: `exynos4412-adc` @ 0x126c0000 exists in
    `iomem`, but `# CONFIG_S3C_ADC is not set` — a real, untapped **4-ch/12-bit
    analog-in** resource if the pins are bonded out.
  - **PWM timers present** (`s3c24xx-pwm`, `HAVE_PWM=y`) — untapped dimming /
    soft analog-out potential.
  - **Front-panel buttons = `odroid-keypad`** input driver (`input0`/`event0`,
    `16b4:0701`); they bypass the STM8. Button→keycode not yet decoded.
  - **A second RTC** on the SoC (`s3c64xx-rtc`), independent of the MCP7940N.
  - New unidentified **I²C device `0-0006`** on bus 0.
  - Confirmed vendor stack on disk: `CMIMIRDemo` + `libemaLib`/`libcmirisLib2`/
    `libcmicolorLib` (all May 2014), already backed up.
- **Untapped potential recorded** (silicon there, Linux can't reach it yet):
  analog-in via the ADC, PWM-out, ~250 GPIO pads (5 used), the SoC RTC, the
  three buttons, BT/IR stacks. All gated by missing kernel drivers, not hardware.

### Tested
    full SSH survey re-run end-to-end; raw saved; dmesg/probes/interrupts parsed
    ethtool -e EEPROM dump re-captured (0xA5 sig, MAC, USB IDs, SMSC)

### Not tested
    - Nothing written to the board; survey is read-only.
    - ADC/PWM/GPIO/buttons NOT exercised — they need kernel work first.
    - I2C 0-0006 not identified; Wiegand WRITE_DATA frame still unknown.
    - Board was power-cycled mid-session by the user; the SSH survey is the
      clean post-reboot capture.

## 2026-10-12 — Debug port (ttySAC1) physically verified — full serial console + root shell

- **Question:** can the 1.8 V debug header be driven now that a 1.8 V adapter +
  level shifter exist? **Yes — confirmed end-to-end.**
- **Rig:** 1.8 V USB-UART adapter → level shifter → board 4-pin header
  (VCC/TX/RX/GND) → **Prolific PL2303 on COM4**, PuTTY @ **115200 8N1**.
- **Captured:** full U-Boot 2010.12 banner → kernel `3.0.68` → `Linaro 12.11`
  → `root@linaro-ubuntu-desktop:~#`. The board booted the **vendor OS from the SD
  card** (`root=UUID=e139ce78`, the eMMC clone) **with no Ethernet attached** —
  the debug port alone gives complete screenless access. That was the goal.
- **Boot also re-confirmed** every peripheral probing cleanly: WM8960
  (`#0: Ctis_wm8960`), LAN9512 (`0424:9512` + `ec00` SMSC), MCP7940N RTC
  (`1-006f chip found`). RTC still reads **2001-01-01** (`setting system clock
  to 2001-01-01`) — the uninitialised-clock finding, now seen in a live boot.
- **Why my Python capture got 0 bytes but PuTTY worked:** the capture set
  `DTR=False`; counterfeit PL2303 clones won't receive unless **DTR is asserted**
  (PuTTY does this by default). Fixed `tools/../temp/com4_capture.py` to
  `DTR=True`. Not a hardware fault — a host-side line-setting gotcha.
- **Note (not a fault):** the first boot after power-yanking ran a forced
  `fsck` ("not cleanly unmounted") and auto-rebooted once; the second boot was
  clean. Expect that whenever power is pulled without a shutdown.

### Tested
    PuTTY COM4 @115200  -> full U-Boot + kernel + root shell captured
    ping 192.168.100.127 -> unreachable (expected: no RJ45 cable attached)
    boot shows all peripherals init; RTC=2001; SD rootfs UUID=e139ce78

### Not tested
    - Ethernet never re-plugged, so the vendor OS LAN path was not re-confirmed
      this session (it was proven earlier when the board was at .127).
    - Login password over serial not tried (dropped straight to a root shell).
    - the alternate-OS image was never booted — this card is the vendor clone.
      Serial now makes that diagnosis trivial (write image, boot, watch PuTTY).

## 2026-10-09 — Wiegand mapped as far as libemaLib goes (swallowed scan, nothing transmitted)

- **Question:** what do `W-IN` / `W-OUT` do, and can the vendor side drive them?
  Checked **on the board, read-only against the STM8** — the swallowing shim
  (`nullwrite.so`) captured every frame the library intends and the STM8 never
  saw a byte. Raw: `docs/raw/wiegand-frames-raw.md`, `wiegand-frames2-raw.md`.
  Tools: `tools/ema_wscan.cpp`, `tools/ema_wscan2.cpp`,
  `tools/board_wiegand_scan.py`, `tools/board_wiegand_scan2.py`.
- **Wiegand is DIGITAL, not analog** — a 2-wire pulse protocol (idle HIGH with
  pull-up, ~100 µs LOW pulses, DATA0 = `0` bit, DATA1 = `1` bit). Physical
  headers on the GPI/GPO row: **`W-IN`** (receive from a reader) and **`W-OUT`**
  (`W-OUT1`/`W-OUT2` = DATA0/DATA1, emulate a card toward a reader).
- **The enum is 0-indexed and Wiegand = event types 2–6** (recovered from
  `EMA_EVENT_TYPE_WIEGAND_*` strings in CMIMIRDemo — libemaLib itself has no
  Wiegand strings): 2 `READ_DATA`, 3 `WRITE_DATA`, 4 `SET_CONFIG`, 5
  `GET_CONFIG`, 6 `AUTO_DETECT`.
- **Type 5 `WIEGAND_GET_CONFIG` → `55 05 02 03 <value>` and type 6
  `AUTO_DETECT` → `55 05 02 04 <value>`; the value is struct offset 8**
  (setting offset 8 to 1 flipped the frame's value byte 00 → 01 — verified).
  This also finally maps the old "class 02, accepted but unmapped" family.
- **Types 2/3/4 emit NOTHING through libemaLib 1.0.1.** A 256-offset sweep per
  type, whole-struct fills, a 26-bit card number, card+length combos, and the
  `setReadEvent()` path — all silent. The library does not implement the
  Wiegand read/write/set paths; only the enum names exist (in the demo). The
  WRITE_DATA frame is still unknown → next software step is disassembling
  CMIMIRDemo's Wiegand UI or trying a newer libemaLib.
- **Tested:** the two swallowed scans re-run end-to-end on the live board.
- **Not tested:** no Wiegand frame has ever been **transmitted** to the STM8;
  W-IN/W-OUT lines never measured with a scope — that needs the hardware below.

## 2026-10-09 — Board photos identify the companion chip: a KSZ8995XA 5-port switch

- **Six board photos supplied by the user were reviewed** and moved into the
  project as `docs/photos/` (`carrier-1..3`, `cm4412-module-1..2`). One pair is
  byte-identical — `carrier-3.jpg` and `carrier-3-duplicate.jpg` share sha256
  `C951CB70…`, so five distinct images. Readings from them are recorded in
  `docs/raw/board-photos-raw.md`.
- **The previously-unidentified companion chip is legible: `MICREL / KSZ8995XA /
  1249M2 / M9242030 / MO2062U0`.** A **Micrel/Microchip KSZ8995XA — an
  integrated 5-port 10/100 QoS Ethernet switch**, sitting between the LAN9512
  and the two RJ45 jacks, which are silkscreened **`LAN1`** and **`LAN2`**.
  This is the first new chip identified on the board.
- **This retires the "RJ45 #2 is on the STM8" theory.** A 5-port switch is the
  only kind of chip that can put two physical jacks on one NIC, which is exactly
  the symptom that had been misread as "wired to the STM8" — no second interface
  ever appeared because there was never a second NIC. Both jacks are `eth0`.
  Row 3 moves **LINK FOUND → OPEN** and is re-scoped: there is no request frame
  to build and no `eth1` to bring up; it needs a cable test, not protocol work.
- **Datasheet checked rather than assumed** — `docs/raw/ksz8995xa-datasheet.txt`
  holds the extracts. It confirms the mechanism: *"The chip starts automatically
  after trying to read the external EEPROM. If EEPROM does not exist, the chip
  will use default values for all internal registers."* So this family
  configures itself at power-up over its own pins, invisible to Linux — the same
  reason `ethtool -e eth0` works for 93LC66A #1 and the same reason no driver
  sees it.
- **93LC66A #2 narrowed but deliberately NOT marked solved.** It sits in the same
  LAN section beside the switch, making the KSZ8995XA the leading candidate
  owner. **What stops it being proven:** the datasheet documents the config
  bus as **I²C, 2-wire (`SCL`/`SDA`, pins 110/111)**, and a **93LC66A is a
  3-wire Microwire part** — different bus, different part family, and the config
  interface names no `93Cxx` anywhere. Row 14a stays OPEN, owner "not yet
  proven".
- **RTC battery question answered from the photos**: a **coin cell in a
  through-hole holder** sits immediately left of the CM4412 module, beside the
  `F-RST` silkscreen. The hardware to hold the clock across a power cut is
  physically present; whether the cell still holds charge is untested.
- **CPU module identified**: `CMITECH CPU MODULE Rev 1.0`, `2014.02.04`, with an
  `Exynos 4412` marked `S1T5W11`, a `X32K` 32.768 kHz can, and a sticker
  `CM4412 / CTE03095` — a CMITECH CM4412 system-on-module, matching the
  `CM4412` string already seen in the vendor binaries.
- Docs updated: `docs/BOARD.md` (rows 3 + 14a, sections #3, #14, #17,
  next-steps), `docs/ARCHITECTURE.md` (Layout, Gotchas, Open issues).

### Tested

- Nothing was run against the live board in this task — it is a photograph
  review plus a datasheet check. The earlier LAN9512/MAC/EEPROM facts already in
  `BOARD.md` are untouched and were not re-measured.
- `Get-FileHash docs\photos\*.jpeg -Algorithm SHA256` — run, to prove the
  duplicate pair before keeping both.

### Not tested

- **The RJ45 #2 cable test was not performed.** Still the single decisive test:
  a live cable in **RJ45 #2** against `ethtool eth0`, then the same in #1 as a
  control. If #2 lights `eth0`, the switch reading is confirmed and row 3 closes.
- **The 93LC66A #2 ↔ KSZ8995XA link is unproven** — no probe, no bus trace, no
  EEPROM dump of a second chip. Candidate only.
- **The RTC coin cell's charge is untested**, and `hwclock --systohc` remains
  unrun (a write, awaiting the user's go).

## 2026-10-11 — Board: update + upgrade + clean (safe subset only)

- Ran on the SD-card vendor OS (`Linaro 12.11 / Ubuntu precise armhf`, sources already on `old-releases.ubuntu.com`):
  - **Disabled 2 dead 2012 Linaro PPA lists** (parked as `.disabled` in `/etc/apt/sources.list.d/`) — they would have broken `apt update`.
  - `apt-get update` → all `Hit`, clean.
  - `apt-get upgrade` → 0 pending initially; installed the one real update **`ubuntu-minimal 1.267→1.267.2`** (+`ubuntu-advantage-tools`) after a dry-run proving it removes nothing.
  - `apt-get clean` → `/var/cache/apt` now 84 KB; root 2.1 GB free.
  - `apt-get check` → no broken dependencies.
- **Deliberately NOT done — `dist-upgrade`:** its plan was `Remv unity` + `Remv ubuntu-desktop` + `Remv linaro-ubuntu-desktop` (vendor Unity 5.16 → precise-updates 5.20 chain is uninstallable on Linaro's build) — it would have **deleted the working desktop**. The 6 packages stay held back on purpose: `duplicity libunity-core-5.0-5 linux-tools unity unity-common unity-services`.
- **Left alone:** `apt-mark hold` list (`libkms1` + 3 old `linux-image-*`) is a deliberate vendor pin protecting the booting kernel — `autoremove` correctly refused to touch the held `libkms1` (74 kB, not worth unholding).
- **Tested:** all four apt stages above with output; `apt-get check` clean; vino still alive; uptime OK.
- **Not tested:** no reboot after upgrade (not needed — dpkg reported success); held-back packages remain un-upgradable by design.

## 2026-10-11 — VNC made headless-safe: per-connection popup disabled

- **Problem:** every TigerVNC connection raised the vino "Allow this desktop to be viewed?" confirm dialog on the board's screen (`org.gnome.Vino prompt-enabled=true`) — unusable once the board runs screenless after development.
- **Fix:** `gsettings set org.gnome.Vino prompt-enabled false` and `notify-on-connect false` (connect banner off too). Values land in `/root/.config/dconf/user` → survive reboot; the stock `vino-server.desktop` autostart (`AutostartCondition=GSettings org.gnome.Vino enabled`) relaunches at boot.
- Restarted `vino-server` to re-read settings. **Gotcha:** it must be started as `/usr/lib/vino/vino-server` — bare `vino-server` is not on root's non-login PATH (first restart attempt died with `execvp: No such file or directory`).
- **Tested:** `gsettings get` reads `false`/`false`, dconf db updated, PID running, port 5900 LISTEN (v4+v6), RFB handshake `RFB 003.007` from this PC after restart.
- **Not tested:** the absence of the on-screen dialog is inferred from the vino setting, not observed on the monitor — confirm on next connect. Dialog only returns if someone flips `prompt-enabled` back.

## 2026-10-11 — Consolidated all OS/backup/tooling into a permanent `os/` archive

- **Problem:** every critical artifact (esp. the 2.43 GB eMMC backup) sat in
  `temp/`, which is throwaway by convention, with no git repo as a safety net.
- **Fix:** created a permanent `os/` tree and **moved** everything out of `temp/`
  (moved, not copied — only 12 GB free on D:, so duplication was not an option;
  moving also takes the big files out of the scratch zone):
  - `os/backup-eMMC/` — `emmc_backup.img.gz` (2.43 GB) + `emmc_backup.log`.
  - `os/scripts/` — 25 reusable board tools.
  - `os/logs/` — reserved for run logs.
- **Repointed every hardcoded path** in the moved scripts from `d:\phl\temp\…`
  to the new `os/…` locations (10 files fixed; verified no stale `temp` refs remain).
- **Wrote `os/README.md`** — full documentation: folder map, board access, current
  hardware state, the recovery/reload recipe, and the backup SHA256.
- Corrected a stale param name in the docs: the writer script takes `-Image`
  (not `-SourcePath`).
- Tested: folder listing, path-replace sweep + `CLEAN` verification, `temp/` now empty.
- Not tested: re-running the moved scripts end-to-end (paths repointed by inspection;
  the two card scripts `Write-ImageToCard.ps1`/`Compare-Card.ps1` were only re-read,
  not executed — they need a physical card in the reader).

## 2026-10-11 — SD card turned into full-capacity playground: cloned vendor OS boots standalone + 51 GB /data partition added

- **SD card now boots the full vendor OS on its own.** With the eMMC physically
  removed, the board runs entirely from the cloned card (`/` = `mmcblk0p2`),
  proving the earlier blank screen was **that image**, not the SD
  slot or boot switch. eMMC is out and safe; `emmc_backup.img.gz` on the PC is
  the recovery source.
- **Reclaimed the card's wasted space.** The eMMC clone only laid down its tiny
  5.4 GB rootfs onto the 60 GB card, leaving ~54 GB unallocated. Added partition
  `p3` (sectors 11532288→124735487) in the free space — **boot p1 and rootfs p2
  untouched** (verified `p2 end=11532287` unchanged).
  - Formatted ext4, `LABEL=data`, mounted at `/data` → **54 GB total, 51 GB free**.
  - Persistent via `/etc/fstab`: `LABEL=data /data ext4 defaults,noatime 0 2`.
  - Write test passed (`/data/write_test.txt` written, read back, synced, removed).
- Notes / gotchas found along the way:
  - `parted` is NOT installed on the vendor image — used `fdisk` (scripted) instead.
  - Creating a partition on the live card succeeds on disk but the kernel won't
    re-read the table while root is mounted (`BLKRRPART` → EBUSY / "Device busy").
    The node appears only **after a reboot**. Recovery: partition entry is already
    correct on disk, so just reboot then `mkfs`+mount (script `mkdata_resume.py`).
  - `blockdev --getsize64` reports a bogus 2.1 GB (3.0-kernel driver caps at 2^31-1);
    `fdisk -l` (124,735,488 sectors) is the authoritative 60 GB.
- Tested: `fdisk -l` geometry check, `mkfs.ext4`, mount, `df -h /data` (51G avail),
  live write+read+sync. Reboot confirmed the board returns (static IP 192.168.100.127).
- Not tested: an actual power-cycle reboot verifying `/data` auto-mounts from fstab
  (the reboot done was to expose p3; fstab mount itself only verified via current mount).

## 2026-10-11 — eMMC backed up to PC (verified) and cloned to SD card (boot chain verified)

- **eMMC → PC backup.** Full raw `dd` of `/dev/mmcblk0` streamed over SSH with
  gzip **on the board** (only ~2.55 GB crosses the 100 Mbit link instead of
  7.8 GB raw). Saved to `d:\phl\temp\emmc_backup.img.gz`.
  - `dd` reported **7818182656 bytes** = exact eMMC size (1864×4M records).
  - PC-side gunzip + sha256: decompresses to exactly 7818182656 bytes;
    `raw_sha256 = 70b758114c2eb03cab45228aa14f5dc1b7519c37bededd3a107cebb040e305f0`.
    gzip CRC passed → transfer intact. **This is the safety backup.**
- **eMMC → SD clone** done **from the board** (`dd if=/dev/mmcblk0 of=/dev/mmcblk1
  bs=4M conv=fsync`, PID-backgrounded, polled). Wrote the full 7818182656 bytes;
  `Dirty=32kB / Writeback=0` confirmed all data physically on the card. Chosen
  over the Windows raw-write path, which fought write-permission the whole session.
- **Why the card hash ≠ backup hash (and why it is fine):** the eMMC root is
  actually **mounted `rw`** (cmdline `ro` is remounted rw at boot), so the running
  board writes logs etc. The backup (T1) and the clone (T2) are different moments
  of a live disk. The **boot-critical, immutable** regions match exactly:
  - first 16 MB (BL1/BL2/u-boot): eMMC == SD → `44f0c067…`
  - first 128 MB (+ vfat boot p1: uImage, boot.scr, dtb): eMMC == SD → `77075900…`
  - ext4 journal replays any in-flight rootfs writes on mount → boots clean.
- **Board facts confirmed this session:** ODROID-**X** (cmdline `mem=1023M`, X2
  would be 2047M); vendor kernel 3.0.68 Hardkernel KST-2014; eMMC p1 vfat BOOT +
  p2 ext4 rootfs (UUID e139ce78…); static IPv4 `192.168.100.127/24`; SSH root/`pakistan`.
- Tools added under `d:\phl\temp\`: `emmc_probe.py`, `emmc_backup.py`,
  `emmc_verify.py`, `clone_start.py`, `clone_status*.py`, `clone_done.py`,
  `clone_ps.py`, `verify_start.py`, `bootcmp.py`.

### Tested
    d:\phl\temp\emmc_verify.py        -> SIZE-OK, raw_sha256=70b75811…  (backup intact)
    board: dd if=/dev/mmcblk0 of=/dev/mmcblk1 bs=4M conv=fsync
                                        -> 7818182656 bytes copied, 461.6 s, 16.9 MB/s
    board: sha256 first 16 MB / 128 MB eMMC vs SD -> BOOTLOADER_MATCH / BOOT128_MATCH

### Not tested
- **Boot of the SD card** — the whole point of the clone; pending the physical
  boot test (power off → switch to SD → power on → HDMI + ping). eMMC left in
  place as the backup.

## 2026-10-11 — 93LC66A #2 located next to the LAN9512; switch hypothesis opens RJ45 #2

- **User placed chip #2 physically: right beside the LAN9512** (not near the
  STM8). Both 93LC66As live in the LAN section → #2's master is a *companion
  network chip*, most plausibly a small **Ethernet switch**: RJ45 #1 + #2 →
  switch → LAN9512 would present **one NIC with two jacks** — never a second
  interface, i.e. exactly the symptom previously read as "port 2 is dead".
- **Correction recorded:** the "RJ45 #2 not in Linux" verdict rested only on
  the absence of a second NIC. **A cable-in-port-2 test against `ethtool eth0`
  has never been run** — it is now the next hardware test (direct cable to the
  Linux PC; never both jacks on the same switch — loop risk if the
  hypothesis holds).
- Docs updated: `docs/BOARD.md` (row 14a, §14, Next step 5), memory bank
  (activeContext open question + next step 7 + Recently-changed, progress).

### Tested
    Nothing new — this entry records a user-supplied physical observation and
    the reasoning it changed.

### Not tested
- The RJ45 #2 cable test (the decider) — pending a machine restart.
- The companion chip's markings — not read.

## 2026-10-11 — RTC diagnosed (alive, never given a date); 93LC66A #1 proven = the LAN9512's config EEPROM

- **MCP7940N RTC root cause found with a read-only I2C register dump**
  (`tools/mcp7940_dump.c`, run with `I2C_SLAVE_FORCE` at `0x6f` on `/dev/i2c-1`
  — plain `I2C_SLAVE` returns `EBUSY` because `rtc-mcp7940n` owns the address):
  - `reg0x00 = c9` → **ST bit set, oscillator running**; tick test `c9 → d1`
    (seconds 49 → 51 in 1.3 s) → **H:M:S is alive and ticking**
  - **`mday/month/year` all `0x00`** → `rtc_valid_tm()` rejects → **`EINVAL`
    on every read**: `hwclock -r`, sysfs `date`/`time`, and boot-time `hctosys`
    (`dmesg: unable to read the hardware clock`)
  - **The chip was never given a date.** The kernel only reads; nothing on this
    board ever wrote one. Origin of the old "no working RTC / logins timestamped
    1970" note.
- **Fix identified, NOT run:** `hwclock --systohc` once (a write — awaiting the
  user's go), then reboot to confirm `hctosys` succeeds.
- **93LC66A #1 proven: the LAN9512's own config EEPROM.** Chain: kernel has
  **no SPI at all** (`# CONFIG_SPI is not set`, no `93CX6`, no `spidev`); the
  chip is on no I2C bus (all 7 devices named); `lsusb` shows one LAN9512
  (`0424:9512` hub fn + `0424:ec00` eth fn); and **`ethtool -e eth0` dumps the
  chip**: `0xA5` valid-sig, MAC `00:25:ff:fe:44:45` (= `eth0`), USB IDs
  `24 04 12 95` / `24 04 00 ec`, UTF-16 `"SMSC"`, rest `0xFF`. The LAN9512
  reads it over its dedicated Microwire pins at power-up — no OS involvement,
  which is exactly why a kernel with zero SPI still has a working MAC.
- **93LC66A #2 stays open** — no second master visible from the SoC (7 I2C
  devices all named; no SPI; one LAN9512). Suspected STM8-side; the open
  question is **physical location** — ask where it sits on the board.
- **Vendor binaries scanned** (local `vendor-backup/`): no `/dev/i2c`, no
  `spidev`, no bit-bang strings — vendor code never reaches serial buses.
  `libcmirisLib2`'s `EEPROM` class (board number/serial/license) is the MPIC
  **camera** over USB, not these chips.
- **Checklist updated:** row 14 `BLOCKED` → **14 WORKS + 14a OPEN**; RTC added
  as row 17 `OPEN`. Counts now **19 rows: 13 WORK, 2 LINK FOUND, 3 OPEN,
  1 CLOSED — no BLOCKED rows remain.** Also corrected two stale docs:
  the `i2cdetect` gotcha (scanning I2C was the wrong question) and the
  "LINK FOUND rows: RS232" line in *Next step* (RS232 is WORKS).
- New tools: `tools/mcp7940_dump.c` (read-only register dumper, compiled on the
  board) and `tools/rtc_probe.py` (upload → compile → dump → evidence sweep).
  Raw output: `docs/raw/rtc-93lc66a-raw.md`.

### Tested
    python temp\rtc_ee2.py (promoted to tools/rtc_probe.py)
        connected; C probe compiled on the board -> COMPILED_OK
        register dump -> 00=c9 01=30 02=00 04=00 05=00 06=00, tick c9->d1 CHANGING
        dmesg -> "chip found" + "hctosys: unable to read the hardware clock"
        hwclock -r / sysfs date / sysfs time -> Invalid argument (EINVAL)
        ethtool -i eth0 -> supports-eeprom-access: yes
        ethtool -e eth0 -> a5 + MAC 00:25:ff:fe:44:45 + 0424:9512/ec00 + "SMSC"
        lsusb -> 0424:3503 hub, 0424:9512, 0424:ec00, 09da:0025 dongle
        /proc/config.gz -> CONFIG_RTC_DRV_MCP7940N=y; # CONFIG_SPI is not set;
            # CONFIG_EEPROM_93CX6 is not set
        7 I2C devices all named: dummy, usb3503 x2, max77686, wm8960, mcp7940n, hdmiphy
        local strings scan -> no /dev/i2c | spidev | bitbang in vendor binaries

### Not tested
- **`hwclock --systohc` was not run** — it writes to the chip; awaiting the go.
- **RTC hold across a power cut (battery)** — untested; note time, power cycle,
  compare.
- **Who set the system date correctly at boot** despite the failed `hctosys` —
  no NTP process runs, `rc.local` is empty, `/etc/adjtime` exists; unidentified.
- 93LC66A #2's master and physical position — unknown.
- The `ethtool -e` dump was `head`-truncated at 0x160; the full 512-byte dump
  was not saved.

## 2026-10-11 — micro-USB CLOSED: fully diagnosed, no further work

- **Decision (user): close the micro-USB workstream.** Both modes were already
  diagnosed to root cause; nothing was left to probe. All work continues over
  **LAN/SSH** (`192.168.100.127`).
- **Status:** checklist row 12 **PARTIAL → CLOSED**. Counts now
  **12 WORK, 2 LINK FOUND, 1 CLOSED, 1 BLOCKED** (the PARTIAL bucket retires).
- **What is closed and why (final record):**
  - *Normal mode:* kernel has **no gadget function** (`/proc/config.gz`, all
    `g_*` disabled) → attach but enumeration dies — the Windows Code 43 root
    cause. Fix = kernel rebuild → **accepted as-is, not pursued.**
  - *Android mode:* enumerates as ADB `18d1:0002` but the far end is a stub
    (flat 4-byte `FAIL` to every input) → no working adbd.
  - **Reopen only if a kernel rebuild is approved.** No PC drivers to chase
    (proven on Windows *and* Linux), no configfs to mount on this 3.0.68 kernel.
- Docs updated to CLOSED everywhere: `docs/BOARD.md` (row 12, §12 header,
  "Micro-USB / ADB" section now carries the decision), `README.md`,
  `docs/ARCHITECTURE.md`, memory bank (`activeContext`, `progress`).

### Tested
    Nothing new — this entry records a decision, not a measurement.
    Prior evidence (config.gz, Linux enumeration loop, Android-mode probes)
    is documented in the two 2026-10-11 entries below.

### Not tested
- Kernel rebuild with `CONFIG_USB_ZERO`/`G_SERIAL` — deliberately not attempted.

## 2026-10-11 — Micro-USB root cause found: no gadget function exists in this kernel

- **Board repowered into normal mode, plugged into the a Linux PC.** Linux
  sees **no device in `lsusb`** — but dmesg shows the board attaching and
  failing enumeration in a loop (device numbers 13 → 22):

  ```
  usb 1-1: Device not responding to setup address.
  usb 1-1: device descriptor read/64, error -110 / -71
  usb usb1-port1: unable to enumerate USB device
  ```

  No sysfs node ever appears. **This is the same failure Windows reports as
  Code 43 "Device Descriptor Request Failed" — reproduced on a second OS.**
- **Root cause proven from the board's own `/proc/config.gz`:**

  ```
  CONFIG_USB_GADGET=y              framework present
  CONFIG_USB_GADGET_S3C_OTGD=y     controller driver built-in (hence the attach)
  # CONFIG_USB_ZERO is not set     no gadget function built
  # CONFIG_USB_ETH / GADGETFS / G_SERIAL / G_MULTI — all not set
  ```

  `/lib/modules` has **zero** `g_*.ko`. The board has **no gadget function at
  all** — controller pulls D+, nothing answers SETUP, descriptor read times out.
  Board side while plugged: `VBUS online=0`, `NO-UDC`.
- **Answer to "do we need to install a driver on Linux": no — and none can
  work.** Driver binding happens *after* enumeration; this device never gets
  there. Both PC-side hunts (Windows and Linux) were aimed at the wrong layer.
- **Corrected my own documented "next step."** BOARD.md previously said *mount
  configfs, create a gadget* — **impossible**: kernel 3.0.68 predates
  configfs USB gadgets, and every `g_*` function is disabled in this build.
  Real options recorded: (1) kernel rebuild with `CONFIG_USB_ZERO`/`G_SERIAL`,
  (2) Android mode (port enumerates cleanly as `18d1:0002` there), (3) leave it.
- Checklist row 12 stays **PARTIAL**; counts unchanged (12/2/1/1).

### Tested
    Linux lsusb / dmesg while board plugged (normal mode)
        -> no device; attach + error -110/-71 loop, unable to enumerate
    Linux /sys/bus/usb/devices/1-1/uevent       -> node never created
    Board /sys/class/power_supply/usb/online     -> 0
    Board /sys/class/udc                         -> absent
    Board /proc/config.gz gadget options         -> all g_* = not set
    Board /lib/modules g_*.ko search             -> zero files
    Board SSH                                    -> up (uptime 11 min)

### Not tested
- A kernel rebuild (option 1) — not attempted, would be a major change.
- Whether another boot mode besides Android exposes a working gadget.
- VBUS meter measurement on the micro-USB pin (superseded by the config
  evidence; no longer needed to explain the failure).

## 2026-10-11 — Micro-USB identified: ADB gadget in Android mode, but no adbd behind it

- **The board was repowered into Android/normal-mode testing and plugged into a
  a Linux PC** (192.168.100.139). In Android mode the micro-USB **enumerates
  cleanly on Linux**: `ID 18d1:0002 Google Inc. Android 1.0`, interface
  `bInterfaceClass=ff sub=42 proto=03` (**ADB signature**), bulk EPs `0x81/0x02`,
  no `/dev/ttyACM*`. The board is **off the network** in that mode.
- **`adb` (installed on Linux) shows an empty device list** even though the
  device is present and nothing else claims it.
- **Proved why, by speaking raw ADB protocol with pyusb** — bypassing the adb
  tool entirely. Every input gets the identical 4-byte reply `FAIL`:

  | sent | reply |
  |---|---|
  | CNXN (v01000001 and v01000000) | `FAIL` |
  | SYNC / AUTH | `FAIL` |
  | 1 garbage byte | `FAIL` |
  | nothing (0 bytes) | `FAIL` |

  A real adbd always answers with a **24-byte header**. Identical replies to
  everything — including silence — mean a **fixed stub responder, not a working
  adbd**. First write is accepted (31 bytes), later writes stall until USB reset
  (far end buffers but never reads).
- **Conclusion: no Windows/Linux driver will ever fix this.** The earlier
  driver hunt was aimed at the wrong layer — the hardware and descriptor are
  fine (Linux enumerates it), there is just no adbd behind the interface.
- Checklist row 12 downgraded **WORKS → PARTIAL**; counts now
  **12 WORK / 2 LINK FOUND / 1 PARTIAL / 1 BLOCKED**.
- **Also corrected** a wrong claim I made earlier in this session: my first
  summary said Linux showed a `SAMSUNG SMDK Exynos Platform Serial` string —
  that was an earlier sighting, and this session's enumeration shows
  `Product: Android 1.0`. Recorded in BOARD.md as not re-verified.

### Tested
    lsusb / sysfs on Linux                -> 18d1:0002, FF/42/03, EPs 0x81/0x02
    adb devices (Linux, adb 29.0.6)          -> empty
    raw pyusb CNXN/SYNC/AUTH/garbage/empty    -> 4 bytes "FAIL" every time
    ping 192.168.100.127 in Android mode      -> unreachable (expected)

### Not tested
- What serves FF/42/03 on the board in Android mode (configfs/gadget inspection
  needs the board in that mode and reachable).
- Whether another boot mode exposes a real adbd.
- The earlier `SAMSUNG SMDK Exynos Platform Serial` string was not reproduced.

## 2026-10-11 — Debug header marked unverified; micro-USB plugged into a PC (Code 43 vs board silence)
- **Debug header documented and explicitly marked UNVERIFIED.** Physical
  layout recorded as **4-pin: VCC, TX, RX, GND**, logic **1.8 V**. The user
  needs to source 1.8 V hardware first, so `docs/BOARD.md` now carries a
  warning block: *identified by elimination + config + process ownership, but
  no terminal has ever been attached.* Until hardware exists it stays
  **identified, not proven end-to-end**.
- **Micro-USB was actually plugged into this PC.** Both ends measured:

  | end | result |
  |---|---|
  | Windows | `Unknown USB Device (Device Descriptor Request Failed)` **Code 43**; no new COM port |
  | Board | **nothing** - no dmesg OTG/UDC/VBUS event, `/sys/class/udc` absent, `power_supply/usb online=0`, no new device on `lsusb` or `debugfs/usb/devices` |

  **They disagree, and that is the finding.** Windows starts enumeration; the
  board never notices a cable. That mismatch is the classic signature of a
  **charge-only or damaged data cable**, so the cable is the first suspect -
  not a driver, and not configfs.
- **Corrected a stale claim** in the micro-USB section: it said
  `s3c-usbgadget` was loaded. `lsmod` shows no gadget module; `s3c-udc` appears
  only in `dmesg` and is almost certainly built-in. Rewrote the section as a
  measured table.
- **Established why "find drivers" can never work as currently configured:**
  no UDC registered, no gadget configured, configfs not mounted, no function
  module loaded. The hardware and controller driver *are* present and powered
  (`s3c-udc` + `LDO12 VDD33_UOTG_3V3`, `LDO15 VDD10_OTG`), but nothing is
  bound to them - a UDC with no gadget behaves as if unplugged.

### Tested
    Get-PnpDevice baseline before plug-in          -> 9 USB items, COM3 only
    Get-PnpDevice after plug-in                    -> +1 Error: Code 43 descriptor failure
    dmesg on board while connected                 -> no OTG/VBUS/connect events
    /sys/class/power_supply/usb/online             -> 0 (no VBUS seen)
    lsusb + debugfs/usb/devices while connected    -> only the LAN9512 hub chain
    lsmod | grep gadget                            -> none loaded

### Not tested
- **No alternative cable tried yet** - the leading hypothesis is untested.
- **VBUS not measured** on the micro-USB, so host-vs-device mode is unknown.
  A meter reading would settle it: board sourcing 5 V means host mode.
- configfs gadget never configured (deliberate - not attempted).
- Debug header still needs 1.8 V hardware.

## 2026-10-11 — Debug port identified as ttySAC1 (1.8 V), console output drivable
- **The debug port is `/dev/ttySAC1`** — the kernel console. Identified by
  elimination plus config: only four UARTs exist and the other three are
  `ttySAC0` (STM8), `ttySAC2` (RS485), `ttySAC3` (RS232), so a serial debug
  header could only be the fourth. Confirmed by
  `console=tty1 console=ttySAC1,115200n8` and by `auto-serial-console` holding
  a `login` + `bash` on it **after every boot** (PIDs repeat across reboots,
  e.g. 1541/1902 vs 1542/1922).
- **⚠️ It is 1.8 V logic, not 3.3 V — corrected from my own bad advice.** I
  first told the user 3.3 V TTL, which is wrong. At 1.8 V a 5 V RS232 adapter
  **destroys** the pin, a 3.3 V adapter driving into it risks damage, and even
  for reading a 3.3 V receiver typically needs ~2.3 V for a valid high so 1.8 V
  highs may not register. Correct answer: **1.8 V TTL adapter or a level
  shifter.** Recorded in `docs/BOARD.md`, `docs/ARCHITECTURE.md` and the
  memory bank.
- **Console output is drivable on demand** — which is what makes the port
  testable without ever opening `ttySAC1`:

  | method | `ttySAC1 tx` delta |
  |---|---|
  | `echo X > /dev/console` | **+17** |
  | `wall` | **+495** |
  | `echo X > /dev/kmsg` | **+0** |

  The `/dev/kmsg` row is the useful negative: the kernel ring buffer and the
  console are different paths here, so dmesg writes do not exercise the port.
  Tried loglevel changes first (`printk` stayed `4 4 1 7`); the fix was
  `/dev/console`, not loglevel.
- **`ttySAC1` is never opened by any tool** — it holds a live `login`+`bash`
  and opening the console can hang a headless board. Now written into the
  decisions list, not just a gotcha.
- **Board was power-cycled several times — by the user, confirmed.** Looked
  like crashes (uptime 41 → 8 → 5 min, UART counters resetting) so I checked:
  no panic, no oops, no OOM, `watchdog inactive, reset disabled`, eth0
  `errors:0 dropped:0`. Nothing to chase.
- **Fixed a corrupted memory-bank file:** `activeContext.md` had two
  `## Current focus` blocks (a stale duplicate from an earlier edit) with
  contradictory counts (13/2/1 vs 12/3/1). Rewrote the file, and merged four
  failure notes that only existed in the stale copy (`libgpiod`, CMIMIRDemo
  unusable, assuming a send succeeded, single-mask GPO refusal).
- **UI does not autostart** — relaunched after the latest boot (PID 3638).

### Tested
    echo X > /dev/console   -> ttySAC1 tx +17
    wall                    -> ttySAC1 tx +495
    echo X > /dev/kmsg      -> ttySAC1 tx +0 (no effect)
    auto-serial-console     -> start/running, process 1541
    fuser /dev/ttySAC1      -> login (1541) + bash (1902)
    UI relaunch             -> PID 3638 holds /dev/ttySAC0, log 0 bytes
    activeContext.md        -> single Current focus block, no duplicate

### Not tested
- **The debug port has never been electrically verified from a terminal** —
  no 1.8 V adapter has been attached. The identification is by elimination,
  config and process ownership, not by seeing bytes on the wire.
- Whether a 1.8 V adapter can actually log in (password unknown).
- Whether the console is stalled after boot: later dmesg writes did not
  transmit, and `ttySAC1` shows no CTS while `ttySAC0` does — flow-control
  stall is a hypothesis, not confirmed, because opening it to read `stty` is
  forbidden.

## 2026-10-11 — RS485 identified as /dev/ttySAC2 (differential measurement + control)
- **RS485 is `/dev/ttySAC2`.** The connector is 2-terminal, half-duplex (D+/D-),
  and it was identified by measuring **DC across the pair** while driving each
  candidate port for 30 s:

  | port | idle | during TX | verdict |
  |---|---|---|---|
  | **ttySAC2** | 0.646 V | **~220 mV** | moved, twice, reproducible |
  | ttySAC3 | 0.646 V | 0.646 V | **control: held still** |

  **The control run is what makes this a finding rather than an observation.**
  Same meter, same setup, same window - only `ttySAC2` moved, so board
  activity, meter drift and ground shift are all ruled out. Without it we only
  knew "something changed once".
- **The reading falls rather than rises, which is expected:** the probe sends a
  `55 AA` alternating pattern, so a DC-averaged meter collapses toward the mean
  while the transceiver is busy. The idle 0.646 V is the bus's fail-safe bias.
- **What is NOT claimed:** reception (rx stayed 0 - no device attached to talk
  back), baud rate, and any actual RS485 communication. Checklist marks it
  **WORKS (TX)**, not plain WORKS.
- **The loopback method is impossible here and that is now recorded** rather
  than retried: 5 phases, **0/50 echoes**. On a half-duplex pair TX and RX are
  the same two wires, so there is no line to jump; shorting D+ to D- forces the
  differential to zero. A negative about the method, not the port.
- **Vendor stack ruled out as a path:** `libemaLib`'s 77 `SerialPort` strings
  are vendored `QextSerialPort` opening only `/dev/ttySAC0`, and the event enum
  has no RS232/RS485 entry.
- **Kernel cannot do RS485:** config has `CONFIG_SERIAL_S5PV210=y` only - no
  `SERIAL_S5PV210_RS485`, no `PINCTRL`. `TIOCGRS485` returns `EINVAL`, and
  direction control cannot be automatic. The probe works by asserting DTR/RTS.
  Only 5 GPIOs are claimed system-wide, none of them a driver-enable.
- **Board recovered during this session.** It rebooted mid-task (counters reset,
  UI not running, `ttySAC0 rx:0`). Checked link health before anything else:
  `link_health.py` got the OPEN ack, so **the STM8 link was alive and the UI was
  simply not started**. Relaunched it. Also found `ema_ui.py` needs
  `DISPLAY=:0` *and* a detached launch - my first `setsid` attempt silently
  produced nothing.
- **New tools:** `rs485_probe.py` (single-window mode so the two ports are
  separated in time and easy to read off a meter), `rs485_recon.py`,
  `rs485_pins.py`, `link_health.py`.
- **Desktop reference line extended** to
  `RS232 = /dev/ttySAC3 | RS485 = /dev/ttySAC2 | STM8 = /dev/ttySAC0`.
- **Two bugs of mine, both fixed:** used `os.argv` (does not exist - it is
  `sys.argv`); and indexed `counters()` positionally, which reads ttySAC0/ttySAC1
  instead of the port under test.

### Tested
    rs485_probe.py /dev/ttySAC2 30   -> meter 0.646 V -> ~220 mV -> 0.646 V (x2)
    rs485_probe.py /dev/ttySAC3 30   -> meter held 0.646 V (control)
    link_health.py                   -> LINK OK, OPEN ack received
    UI redeploy                      -> board py_compile PY2_OK, PID 2618 holds
                                        /dev/ttySAC0, log 0 bytes, label present
    local ast.parse                  -> all tools OK

### Not tested
- **Reception on ttySAC2** - no RS485 device has ever been attached.
- **Baud rate** for a real device; **--no-rts** polarity not tried (the
  positive result means the default worked).
- The UI's 3x-retry failure path has never been triggered.
- Cause of the SSH channel reset at 25.6 s during one window: board showed no
  reboot, no oops, and eth0 had `errors:0 dropped:0` - transient, unresolved.
- RJ45 #2 and Wiegand remain LINK FOUND; EEPROMs still BLOCKED.

## 2026-10-11 — RS485: A/B/A/B jumper test (0/40, method invalidated); probe written, NOT run
- **Ran the four-phase A/B/A/B jumper test the user asked for.** Result on both
  `ttySAC2` and `ttySAC3`, all four phases:

  | phase | jumper | ttySAC2 rx | ttySAC3 rx | echoes |
  |---|---|---|---|---|
  | 1 | ON  | +0 | +0 | 0/10 |
  | 2 | OFF | +0 | +0 | 0/10 |
  | 3 | ON  | +0 | +0 | 0/10 |
  | 4 | OFF | +0 | +0 | 0/10 |

  **4 phases, 40 attempts, zero echoes.** Reproducible across a refit.
- **The method is structurally invalid for this port, and that is the real
  finding.** The connector has **only 2 terminals (D+/D-) and is half-duplex**,
  so TX and RX are the *same* pair - there is no separate line to jumper.
  Shorting D+ to D- does not loop anything; it forces the differential to zero.
  The RS232 technique does not transfer to a differential pair. **I should have
  checked the wire count before running the test, not after.**
- **New tools:**
  - `tools/rs485_phase.py` — one labelled phase of the A/B sequence; prints
    before/after counters plus `rx delta`, the only signal that a loop exists.
  - `tools/rs485_probe.py` — **the test that can actually answer it**: drives
    each candidate port for 15 s windows so a meter across D+/D- shows which
    port's transceiver is enabled (~1.5-5 V differential). Asserts DTR+RTS
    because DE usually hangs off one of them; `--no-rts` for the other polarity.
- **Bug fixed in `rs485_phase.py`:** used `os.argv`, which has never existed —
  it is `sys.argv`. The board reported `AttributeError: 'module' object has no
  attribute 'argv'`. Caught by running it, not by reading it.
- **Desktop label confirmed by the user** ("i confirm label it ther thx") — the
  RS232 reference line on `ema_ui.py` is visible on the VNC desktop.

### Tested
    rs485_phase.py phases 1-4        -> 0/40 echoes, rx delta +0 on both ports every phase
    rs485_phase.py / rs485_probe.py  -> local ast.parse OK, pure ASCII,
                                        board `python -m py_compile` BOARD_COMPILE_OK
    desktop RS232 reference label    -> confirmed visually by the user

### Not tested
- **`rs485_probe.py` was NEVER RUN.** The command aborted before producing
  output (shell-level timeout: the probe needs ~100 s of sustained transmission).
  **The RS485 port is still unidentified.** Next step: re-run it with a longer
  allowance, one port at a time if needed.
- No meter reading was taken across D+/D-, so we do not yet know whether RS485
  is on a Linux UART or behind the STM8.
- Still no real RS232 device attached; baud rate and line voltage unknown.

## 2026-10-11 — RS232 re-verified; reference line added to the desktop app
- **Re-ran the loopback with the jumper refitted: `ttySAC3` echoed again**, this
  time at **all five baud rates**, `rx 7 -> 42` (+35 = 5 x 7 bytes).
  Confirms the port is stable across repeated jumper cycles, not a one-off.
- **That run demonstrated the documented caveat live**: loopback echoes at
  *every* baud because TX and RX share one setting. Recorded so nobody reads
  the baud column as a real answer. `ttySAC2` stayed at `rx:0` throughout —
  still ruled out with the wire fitted.
- **Added a static reference line to `tools/ema_ui.py`** under the header:
  `reference: RS232 = /dev/ttySAC3    STM8 link = /dev/ttySAC0 @ 115200`.
  Purely informational — it does not touch the serial port or the frame
  logic. Also documented RS232 in the module docstring so the two ports
  cannot be confused by a later reader.
- **Deployed safely**: py_compile ran **on the board first**; the running
  instance was only stopped after the new file passed, then restarted.

### Tested
    rs232_loopback.py (jumper refitted) -> ECHO-OK ttySAC3 at 115200/9600/19200/38400/57600, rx 7->42
    ttySAC2 during the same run          -> tx 105->140, rx still 0
    board-side `python -m py_compile`    -> PY2_OK before swap
    process after restart                -> /proc/6109 = `python2 /root/ema_ui.py`, DISPLAY=:0
    /root/ema_ui.log                     -> 0 bytes (no errors)
    grep of deployed file                -> reference label present

### Not tested
- The reference label is **not visually confirmed** — it is in the running
  file and the app started without error, but I cannot see the VNC desktop.
- Still **no real RS232 device attached**; baud rate and line voltage remain
  unknown.
- The 3x-retry failure path in the UI has never been triggered.

## 2026-10-11 — RS232 identified as /dev/ttySAC3 (direct UART, not the STM8)
- **The long-standing "RS232 is behind the STM8" note was wrong.** It is a plain
  Linux UART. Found by jumping TX to RX on the connector with a bare wire — no
  adapter, dongle or extra hardware needed.
- **A/B validated both directions:**
  - jumper fitted  -> `ttySAC3` rx `0 -> 7`, payload `RS232LB` echoed exactly
  - jumper removed -> `ttySAC3` rx `7 -> 7`, **frozen** (control run)
  The rx counter is what makes this conclusive; without the control run an
  internal artifact could not have been ruled out.
- **`ttySAC2` ruled out**, not merely "not chosen": it transmitted all 105 bytes
  and **received zero**. Worth stating as a method — the driver increments `tx`
  for every byte handed to the UART *whether or not a pin is wired*, so `tx`
  alone proves nothing; only a matching `rx` increment shows the wire exists.
- **Two things loopback deliberately does not establish**, both now in
  `docs/BOARD.md`: (1) the **real baud rate** — loopback echoes at any speed
  because TX and RX share one setting, so 115200 "working" only proves the
  config was self-consistent; (2) the **line voltage** — true RS232 (±5-10 V)
  vs bare TTL cannot be told apart, so a meter on TX to GND is still needed if
  real RS232 gear will be attached.
- **New tool `tools/rs232_loopback.py`**: opens only ttySAC2/ttySAC3 (never
  ttySAC0 = STM8 link, never ttySAC1 = kernel console), probes 5 baud rates,
  and reports counters before/after so the result can be re-read from hardware.
- **Also fixed a stale claim** in `docs/BOARD.md`: "No actuator frame has ever
  been sent" was true only of the initial discovery run and had become false.
  Reworded to say so, with a forward reference to the outputs section.

### Tested
    tools/rs232_loopback.py (jumper ON)  -> ** ECHO-OK ttySAC3 @115200 'RS232LB', rx 0->7
    tools/rs232_loopback.py (jumper OFF) -> no echo, rx frozen at 7 (control)
    saved tool re-run on board           -> runs under Python 2.7.3, correct "no echo"
    local python ast.parse               -> SYNTAX OK

### Not tested
- **No real RS232 device has been attached or spoken to.** Only the physical
  port path is proven end to end; nothing on the far end was tested.
- Real baud rate and line voltage still unknown (see above).
- `ttySAC2` is transmitted-to but has never received; its actual destination
  is unknown and uninvestigated.
- RS485 still LINK FOUND behind the STM8 — this result does not transfer to it.

## 2026-10-10 — OUT1/OUT2 solved (ON+OFF both channels), UI extended, app renamed EMA_Controls
- **The digital outputs are fully solved.** Complete verified frame map:
  - OUT1 toggle: single full-state frame `55 0a 03 01 <b4> <b5> 00 00 01 01`
    (b4/b5 = desired OUT1/OUT2 states).
  - OUT2 open: `55 0a 03 01 <a1> 01 00 00 01 01`.
  - OUT2 close: **two-frame recipe** — prep `55 0a 03 01 <a1> 01 00 00 01 00`
    then `55 0a 03 01 00 00 00 00 00 01`.
- **Two protocol rules found (both had caused earlier false negatives):**
  1. Frames must mask BOTH channels (b8=b9=01). Single-mask frames are
     **silently refused** — received (echo register updates), zero ack, no
     action. This is why identical frames "worked" once and later failed.
  2. OUT2 close needs the prep frame to prime the echo register (b9=00) —
     without it the close is refused. This is why "release does not work"
     was concluded earlier; those attempts were ignored frames.
- **Readback decoded:** status frame b4/b5 = raw OUT1/OUT2 contact (00=ON),
  b6/b7 = IN1/IN2, b8/b9 = last request's mask echo. Request acks (byte3=01)
  also carry actual b4/b5, so commands confirm within the same read window.
- **Desktop UI extended** (`tools/ema_ui.py`): OUT1/OUT2 lamps + buttons added
  next to IN1/IN2 lamps and the relay button. Display follows the board's
  report, never the click; commands retry up to 3x, then show
  "board did not respond". Window title and desktop launcher renamed to
  **EMA_Controls** (`/root/Desktop/EMA_Controls.sh`).
- **Regression checks kept:** `tools/ema_uimap.py` (8/8) and
  `tools/ema_gap.py` (4/4) replay the whole frame map against the hardware.

### Tested
    ema_uimap.py                  -> 8/8 PASS (all OUT1 toggles, recipe, singles)
    ema_gap.py                    -> 4/4 PASS (OUT2 ops while OUT1 closed)
    mixed/fullstate suites        -> failure modes characterized, rules derived
    user click-through of UI      -> "all working" (inputs, outputs, relay)
    launcher rename + restart     -> window "EMA_Controls..." live, PID holds
                                     /dev/ttySAC0, empty log

### Not tested
- The UI retry path (3x no-response) — never triggered; only the happy path
  was exercised by the user.
- **Wiegand and analog I/O remain untouched**; RJ45 #2, RS232, RS485 still
  LINK FOUND.
- Class `02` (`55 05 02 03 <value>`) remains accepted-but-unmapped.

## 2026-10-10 — OUT2 switched from a clean power-on baseline; per-channel ON proven
- **First output actuation from a known baseline.** After a genuine power cycle
  (both outputs floating, both LEDs dark), type 18 was sent live: **40 frames of
  `55 0a 03 01 00 00 00 00 00 01` over 20 s, acknowledged 40/40, and the user
  confirmed the OUT2 LED lit.**
- **Per-channel ON control established:** type 17 (`...01 00`) closes OUT1;
  type 18 (`...00 01`) turns OUT2 on. **Byte 8 of the class-`03` request is the
  channel selector** (`01`=OUT1, `00`=OUT2).
- **Two process errors this session, both corrected and worth remembering:**
  (1) a test was announced "RUNNING" when the script had only been uploaded, never
  executed — the user watched a test that never ran; (2) an earlier tool printed its
  *intended* frame rather than the transmitted one. In both cases only the trace log
  revealed the truth. **Verify the log before telling the user to watch.**
- **New observation to decode:** the class-`03` ack does not mirror our request. We
  sent `55 0a 03 01 00 00 00 00 00 01`; the STM8 answered
  `55 0a 03 01 01 00 01 00 00 01` — bytes 4 and 6 are **its own values**, not ours.
  Byte 4 changed across the power cycle with inputs idle, which fits a live
  output-state indicator.

### Tested
    power cycle                  -> OUT1/OUT2 floating, LEDs dark, no relay click
    type 18, 40 frames, 20 s     -> OUT2 LED lit (user confirmed), acked 40/40
    prior: type 17               -> OUT1 closes (reproduced twice from floating)
    prior: type 19, 20 s hold    -> does NOT open a closed OUT1

### Not tested
- **OFF for either output — unsolved.** No command found that opens the contact.
- **Type 17 from this clean baseline** — the earlier "both LEDs lit" came from a
  polluted state, so strict per-channel independence of the two ON commands is
  inferred, not cleanly proven.
- The ack bytes 4/6 as state indicators — a hypothesis, not yet decoded.
- Type 18's effect on OUT1 and type 17's effect on OUT2 (cross-check of the
  selector claim).

## 2026-10-10 — Root cause of the "stuck" output found: the STM8 has its own reset domain
- **The user's diagnosis was correct and is confirmed.** A Linux `reboot` resets
  the Exynos only. The **STM8S207 is a separate microcontroller with its own reset
  domain** — it keeps running, keeps its GPIO state, and keeps the last
  configuration it was given. That is why OUT1/OUT2 stayed as they were across a
  full reboot, and why the "it is still on" behaviour persisted.
- **Consequence: a software reboot cannot return the outputs to their power-on
  state.** Only removing board power, or resetting the STM8 specifically, will.
- **Checked from Linux whether the STM8 can be reset in software: it cannot.**
  There is no sysfs node and no driver for it. `/dev/watchdog` exists, but that
  is the Exynos side. From Linux the only handle on the STM8 is the serial link.
- **The spread of meter readings now makes sense.** OUT1 has read **1.7 mV**,
  **~2.0 V** and **~8.x V** in different states. That is the signature of a
  **floating contact**, not a fixed supply: the reading depends on the STM8's
  current state, the attached load, and leakage. Any single reading is
  provisional and must be compared against a known state.
- **This also reframes earlier results honestly.** The "LED stays on" behaviour
  may never have been a failed command at all — the STM8 may simply have been
  holding a state it was given in an earlier session and never reset. Every
  Linux-level reboot in this project left that state untouched.

### Tested
    uptime after user reboot       -> Linux restarted, STM8 state retained
    ls /dev/watchdog*              -> /dev/watchdog exists (Exynos side only)
    find /sys/devices -iname *stm8* -> nothing; no STM8 reset path from Linux
    fuser /dev/ttySAC0             -> port free, no process holding the link

### Not tested
- **A full power cycle was not performed.** It is a physical action on the user's
  HVAC controller and is their call, not something to do unprompted.
- **Whether a true power cycle returns OUT1/OUT2 to the 1.7 mV power-on state is
  unverified.** It is the expected outcome but has not been tested.
- **Whether the earlier GPO "does not hold" result was a real protocol failure or
  simply a stale latched state from a prior session is still unresolved**, and
  the two explanations now need to be separated before more command hunting.

## 2026-10-10 — OUT1/OUT2 electrical model established; GPO command found but does not hold
- **Major reinterpretation of the digital outputs, based on a fresh-boot
  measurement.** OUT1 and OUT2 idle at **1.7 mV**, not 2 V. That is a contact
  **closed to ground**, not a floating line. Earlier readings of 0.5–2.0 V were
  taken with an LED/resistor load attached and were misleading.
- **The LED wiring was the blocker all along.** Wired `12V+ → LED → 1 kΩ → OUT1`,
  the LED **lights immediately with no commands at all**, because OUT1 already
  sits at ground. The user confirmed it lit. Every earlier "no effect" test had
  the LED reversed, so a working output looked dead.
- **A GPO release command was observed to work once.** Sending
  `55 0a 03 01 00 00 00 00 01 01` (event type 19) turned the LED **dark** — the
  contact opened. On that same run the STM8 returned a status frame with
  **byte 8 changed from `00` to `01`**, i.e. the board reports the output state
  back, the same way bytes 6 and 7 report IN1/IN2. That readback is the key
  result: **GPO commands are now verifiable without a meter.**
- **But the change does not hold.** The LED came back on, and holding the frame
  by re-sending it every 0.5 s for 45 s (`tools/ema_gpo.cpp`) did **not** keep it
  open. Closing the link also returns the output to closed. So the release is
  either momentary, or needs a different/longer command than the one found.
- **A flawed test was identified and corrected.** The earlier per-type test set
  a "value" at struct offset 8, but for the class-`03` family **the value byte
  does not reach the frame** — byte 8 of the frame comes from the event type.
  The value 0 and value 1 phases therefore transmitted identical bytes and could
  not have shown a difference. Types 17–20 produce fixed frames:
  `17 → ...01 00`, `18 → ...00 01`, `19/20 → ...01 01`.
- **Board rebooted cleanly** mid-session (uptime 1 min, `/dev/ttySAC0` free).
  Notably **`/dev/ttySTM8` did not survive the reboot** — confirming it was only
  ever a symlink someone had placed in `/dev`, never a real device.
- **Command classes surveyed, all read-only until proven:**
  - `02` → `55 05 02 03 <value>`, values `00`–`08` all echoed, no effect
  - `04` → `55 05 04 <selector> <state>`, selectors `01`–`12` all echoed,
    **only `01` (relay) acts**
  - `03` → `55 0a 03 01 …`, replies with live varying data; the only family that
    has ever moved a digital output

### Tested
    fresh boot -> OUT1 = OUT2 = 1.7 mV
    LED wired 12V+ / LED / 1k / OUT1 -> lights with NO command (user confirmed)
    type 19 frame -> LED went dark, status byte 8 flipped 00 -> 01
    ema_gpo 1 45 (re-assert every 0.5s) -> LED did not stay dark
    reboot -> /dev/ttySTM8 absent, /dev/ttySAC0 free, UI restarted

### Not tested
- **OUT1 / OUT2 are still NOT controllable.** One release was observed but it
  does not persist, and the re-assert approach failed. Cause unknown: could be a
  watchdog in the STM8 firmware, a required companion frame, or a wrong command
  shape for sustained control.
- **Whether the two outputs are independent is unknown** — no OUT2 command found.
- **Wiegand untouched.** No Wiegand event has ever been sent.
- **Analog I/O not started.** No analog command has been identified.
- The exact meaning of status byte 8 is inferred from a single observed flip,
  not confirmed across repeated cycles.

## 2026-10-10 — Relay verified by meter and by the desktop button; selector sweep closed
- **Relay control is confirmed working through both routes.** The user checked it
  with a multimeter and confirmed it switches via the CLI blink *and* the desktop
  button. 8 blink cycles sent `55 05 04 01 01` 8× and `55 05 04 01 00` 9×, and the
  STM8 echoed every one.
- **`ema_ui.py` is running again on `DISPLAY=:0`** with the input lamps and the
  relay button live.
- **Class-`04` selector sweep is closed.** Selectors `01`–`12` were each driven
  with the meter on OUT1/OUT2. Only `01` (the relay) produced a physical change.
- **Correction to an earlier claim of mine:** I suggested the STM8's echo could be
  used to identify which selectors are valid. It cannot — **every** class-`04`
  selector sent was echoed back, including ones with no effect. The echo proves
  the frame was received, not that it addressed a real device. Only physical
  observation distinguishes them.
- **OUT1/OUT2 are therefore not under class `04`.** That command space is now
  exhausted: selector and state are its only two fields.
- **Notable finding from the vendor disassembly:** `CMIMIRDemo` contains exactly
  one `ema_writeEvent` call, and it sends the **relay** command
  (`55 05 04 01 01`). The vendor GUI never writes a GPO from that site. That is
  real evidence the GPO headers may not be reachable through this write path at
  all, rather than a command we have simply failed to guess.
- **The one remaining untested axis** is the value byte of class `02`
  (`55 05 02 03 <value>`): only `00` and `01` have been tried, and that value may
  be a channel selector rather than a state.

### Tested
    ema_blink 8 5 5                -> 8x "55 05 04 01 01", 9x "55 05 04 01 00"
    RX echo count                   -> 17/17 frames echoed
    ema_ui.py on DISPLAY=:0         -> running, log empty
    user                           -> relay confirmed by meter, CLI and UI

### Not tested
- **OUT1 / OUT2 are still not driven.** No command found moves them.
- **Whether the outputs are fed through the relay** was not resolved. The user
  checked the meter during a relay blink and the relay switched, but no
  OUT1/OUT2 reading change was reported, so the outputs appear independent.
- **Wiegand untouched** — no Wiegand event has ever been sent.
- Class `02` with values `02`–`08` has not been tried.
- Whether it is safe to leave the relay energised indefinitely is unknown and
  untested.

## 2026-10-10 — RELAY CONTROL CONFIRMED; relay button added to the desktop UI
- **The relay works, and is now controllable from the board's desktop.**
  `55 05 04 01 01` closes it, `55 05 04 01 00` opens it. The user confirmed the
  relay clicking during a 10-cycle blink, and again on a 15-cycle re-run.
- **Byte 3 is a device selector, byte 4 is a state** — not a pulse. The relay
  holds until the `00` frame arrives.
- **Selector `01` does not move OUT1 or OUT2.** Those stayed flat across every
  class-`04` test, which is what finally distinguished the relay from the GPOs.
- **The STM8 echoes class-`04` frames back unchanged**, which makes the echo an
  authoritative state report. Verified: 10× `01 01` and 11× `01 00` sent, all 21
  echoed.
- **`tools/ema_blink.cpp`** blinks the relay on demand:
  `./ema_blink <cycles> <on_s> <off_s>`.
- **`tools/ema_ui.py` gained a RELAY button** under the two input lamps:
  - clicking queues `55 05 04 01 01` / `55 05 04 01 00` onto an outbox that the
    reader thread drains, so a command goes out immediately instead of waiting
    for the next polling cycle
  - the button reflects **what the STM8 echoed**, not what was clicked. If the
    board ever reported the opposite, the caption says so rather than lying
  - green when energised, grey when open
  - `QtCore.SIGNAL(toggled(bool))` was replaced with `signal.connect(slot)`; the
    macro form parses `toggled(bool)` as a Python call and dies with
    `NameError: global name 'toggled' is not defined`
- **A documentation correction:** an earlier changelog entry reported the
  status frame's trailing byte changing from `00` to `4c`. That was an artefact
  of frame boundaries in the tracer output, not a real state change — the status
  frame is consistently `... 00 00` when the link is idle.

### Tested
    python2 -m py_compile ema_ui.py -> PY2 SYNTAX OK
    first UI launch -> NameError on SIGNAL macro (fixed, relaunched)
    DISPLAY=:0 python2 /root/ema_ui.py  -> running, log empty
    blink run 1 -> 10x "55 05 04 01 01", 11x "55 05 04 01 00", 21/21 echoed
    blink run 2 -> 15 cycles, 2s on / 2s off
    user: relay confirmed working by ear

### Not tested
- **The UI relay button has not been clicked by the user yet** — the button is
  running but unexercised. The underlying frames are proven separately.
- **OUT1 / OUT2 remain undriven.** They are either another selector under class
  `04` (values `02`, `03`, `04` are the obvious next sweep) or a different class.
  Not tested.
- **Wiegand is untouched.** No Wiegand event has been sent. The vendor enum lists
  `WIEGAND_READ_DATA`, `WIEGAND_WRITE_DATA`, `WIEGAND_SET_CONFIG`,
  `WIEGAND_GET_CONFIG` and `WIEGAND_AUTO_DETECT`, so the command types exist, but
  none has been mapped to a type value or a frame.
- Whether the relay command is safe to leave energised indefinitely is untested
  and unknown.

## 2026-10-10 — Vendor stack backed up; CMIMIRDemo disassembled; second command class found
- **Vendor backup taken first**, as instructed — there is only one board and its
  Daikin binaries cannot be reinstalled. `tools/vendor_backup.py` pulled, read-only:
  `CMIMIRDemo` (127 KB), `libemaLib_arm_1.0.1.so` (47 KB),
  `libcmirisLib2_arm_2.0.92.so` (1.06 MB), `libcmicolorLib_arm_0.9.0.so` (48 KB),
  the desktop launcher, plus SHA256s in `vendor-backup/MANIFEST.md`.
  **Nothing in the vendor area on the board was modified.**
- **`tools/vendor_disasm.py`** dumped `CMIMIRDemo`'s disassembly and relocations
  to `vendor-backup/` for offline analysis. Two things had to be got right:
  - `objdump` needs **`-M force-thumb`**. The binary interworks and is Thumb-2;
    without it `.text` decodes as ARM and every line reads
    `<UNDEFINED> instruction`. Forcing Thumb cut that from thousands of lines to 77.
  - Calls are **`blx`**, not `bl`, and targets are even (`blx e41c`). A `bl`-only
    search finds zero call sites and looks like "the calls aren't there".
- **Mapped the imported symbols to PLT stubs** via `readelf -sW --dyn-syms`:
  `ema_writeEvent` = `0xe41c`, `ema_readEvent` = `0xe878`, `ema_open` = `0xecb8`.
- **`CMIMIRDemo` has exactly ONE call to `ema_writeEvent`**, at `0x14bb8`. The
  event is built on the stack at `sp+148`, in the four instructions before it:

  | struct offset | value |
  |---|---|
  | +0 | 56 |
  | **+4** | **32** ← the type field |
  | +53 | 1 |
  | +54 | 30 |

- **Type 32 was never tried** — the earlier swallowed sweep only reached type 20.
- **A second command class was found by replaying the vendor's struct byte for
  byte** (`tools/ema_vendor.cpp`, still under the swallowing shim):

  | struct | frame emitted |
  |---|---|
  | off53=1, off54=30 | `55 05 04 01 1e` (`1e` = 30) |
  | off53=0, off54=0 | `55 05 04 00 00` |
  | off53=1, off54=31 | `55 05 04 01 1f` (`1f` = 31) |

  **So the wire format is `55 | 05 | 04 | <b53> | <b54>` — a two-parameter
  command.** Byte 3 is struct offset 53, byte 4 is struct offset 54. Neither
  affects anything when type is 5, which is why the earlier single-byte sweep
  only ever exposed `55 05 02 03 <value>`.
- **Command classes now known:**
  - `02` → one parameter: `55 05 02 03 <value>` (accepted by the STM8, but no
    visible effect on OUT1/OUT2)
  - `04` → two parameters: `55 05 04 <b53> <b54>` — **never yet transmitted**
  - `01`/`03` → open/close handshake and status

### Tested
    vendor_backup.py            -> 4 binaries saved + sha256 manifest
    objdump -d (ARM mode)       -> thousands of UNDEFINED lines (wrong mode)
    objdump -d -M force-thumb   -> 77 UNDEFINED lines (correct)
    blx-call search             -> ema_writeEvent: 1 site at 0x14bb8
    ema_vendor under nullwrite  -> 5 frames captured, 0 transmitted
    frame class 04 confirmed    -> byte3=off53, byte4=off54, proven by two values

### Not tested
- **Class `04` has never been transmitted.** The frames were captured with the
  writes swallowed, so the STM8 has never seen `55 05 04 ...`.
- **What byte 3 and byte 4 mean is still unknown.** If byte 3 selects the output
  and byte 4 the state, `55 05 04 01 01` would be "channel 1 ON" — but that is a
  hypothesis, not a measurement.
- No GPO, relay or Wiegand command has been confirmed to change anything
  physical. OUT1/OUT2 remain unmoved.
- The vendor call sits inside a float-heavy loop, so class `04` may be a
  ramp/timing command rather than a plain GPO write. Its purpose is unconfirmed.

## 2026-10-10 — OUTPUT WRITE COMMAND CONFIRMED WORKING on real hardware
- **The first actuator command ever sent to the STM8 — and it was accepted.**
  `tools/ema_drive.cpp` sends `55 05 02 03 <value>` and the STM8 replies with an
  11-byte acknowledgement that **echoes the value back**:

  ```
  TX  55 05 02 03 00   →  RX  55 0b 02 03 00 1a 00 64 00 4c 04
  TX  55 05 02 03 01   →  RX  55 0b 02 03 01 1a 00 64 00 4c 04
  TX  55 05 02 03 00   →  RX  55 0b 02 03 00 1a 00 64 00 4c 04
  ```

  The `01` in the reply is our own value coming back, so the STM8 genuinely
  parsed the command. This is not a no-op.
- **Command format now fully known:** `55 | 05 | 02 | 03 | <value>` — SOF,
  length, write class, operation `03`, value. `55 0b` in the reply confirms the
  length byte counts the whole frame, matching the model built from the input
  frames.
- **Run structure:** 20 s baseline (value 0) → 60 s ON (value 1) → 20 s OFF,
  with phase lengths as CLI args so a re-run needs no rebuild. 600 read events
  during the ON phase, all clean.
- **Physical readings so far:** OUT1/OUT2 idle at **2.00 V**, and after the first
  drive attempt the user reported **OUT1 in the millivolt range** and **OUT2
  below 1 V**. Loading OUT with an LED + 1 kΩ halved the idle reading
  (2.00 V → ~0.98 V), which shows a weak high-impedance line that switches to
  ground — consistent with a relay dry contact or open-collector output, and it
  rules out OUT sourcing voltage.
- **This rules out the risky case:** an output that sources 12 V would short if
  wired as the user first tried (LED + 1 kΩ to ground). It does not source, so
  the sink-style wiring `12V+ → LED → 1 kΩ → OUT` is the correct and safe one.
- **A stale `uart_tap.py` (PID 4994) from an earlier session was found holding
  `/dev/ttySAC0` the whole time.** It has been killed, along with every other
  EMA process, so nothing stray can reach the STM8 during a test.

### Tested
    g++ -std=c++0x -o ema_drive ema_drive.cpp -l:libemaLib...   -> builds
    ./ema_drive 20 60 20  (detached, LD_PRELOAD=opentrace.so)   -> all 3 phases ran
    TX/RX trace -> open/close handshake + 3 acknowledged writes
    user meter: OUT1 ~2.00 V idle, then mV range after driving
    user meter: OUT2 below 1 V
    LED + 1k load on OUT -> 2.00 V fell to ~0.98 V

### Not tested
- **Which physical output op `03` selects is still not confirmed.** The user was
  mid-measurement across the 60 s ON window and the readings per phase were not
  captured. Until that is settled, `op 03` is unlabelled — it is *a* write, but
  not proven to be OUT1.
- **Op `04` (types 6–15) has never been driven.**
- **No LED has been driven from an output**, only a meter across it.
- The trailing byte of the write ack is `4c`, and the status frame's last byte
  changed from `00` to `4c` once writes began. Its meaning is unknown — possibly
  a sequence counter or checksum. Not decoded.

## 2026-10-10 — EMA write vocabulary enumerated SAFELY (writes swallowed, nothing actuated)
- **Recovered the event struct layout and the write frame classes without
  sending a single command to the STM8.** The method: `tools/nullwrite.c`, an
  `LD_PRELOAD` shim that captures every `write()` to the serial fd and then
  **swallows it** — the real `write()` is never called, but the library is told
  the write succeeded. libemaLib therefore builds the frame it *intended* to
  send, we read it, and the STM8 receives nothing.
- **`_EMA_EVENT` has its event-type field at byte offset +4.** Proven by
  observation: a dword of `1` there emits the OPEN frame, `0` emits CLOSE.
- **Frame classes recovered from a type sweep (offset +4, values 0–20):**

  | type | frame emitted | reading |
  |---|---|---|
  | 0 | `55 04 01 00` | CLOSE |
  | 1 | `55 04 01 01` | OPEN |
  | 5 | `55 05 02 03 00` | write class, op `03`, value `00` |
  | 6–15 | `55 05 02 04 00` | write class, op `04`, value `00` |
  | 17 | `55 0a 03 01 00 00 00 00 01 01` | 10-byte request, selector byte 8 = `01` |
  | 18 | `55 0a 03 01 00 00 00 00 00 01` | 10-byte request, selector byte 8 = `00` |
  | 19, 20 | `55 0a 03 01 00 00 00 00 01 01` | as 17 |

  The `55 05 02 .. ..` shape is the write class: `02` is the class, byte 3 is the
  operation, **byte 4 is the value** — currently `00` because the payload field
  in the struct is still zero.
- **Independent confirmation of 115200 baud** from `EMAMain::open()`
  disassembly, which contains the literal `mov.w r1, #115200`.
- **`writeEvent` reads struct offsets +8, +24, +64** (from its disassembly).
- **A first sweep using `0x5a` as the probe value produced no information** —
  it is not a valid event type, so the serialiser rejected every case and fell
  back to the default frame. That is why the sweep was redone with small,
  realistic enum values.
- **Still nothing has been actuated.** No GPO, relay or Wiegand command has ever
  reached the STM8. The value field and the mapping from op `03`/`04` to
  OUT1/OUT2 are not yet identified, so no actuator frame was attempted.

### Tested
    gcc -shared -fPIC -o nullwrite.so nullwrite.c -ldl          -> builds
    g++ -std=c++0x -o ema_wprobe ema_wprobe.cpp -l:libemaLib...  -> builds+links
    LD_PRELOAD=nullwrite.so ./ema_wprobe                          -> 197 lines captured
    sweep dword 1 at offsets 0..96 -> only offset 4 changed the frame
    sweep offset 4, values 0..20    -> 7 distinct frame shapes enumerated
    STM8 received none of it (writes swallowed) -> board state untouched
    ema_ui.py restarted on DISPLAY=:0 after the port was freed

### Not tested
- **The struct offset that carries the output VALUE is still unknown.** Every
  captured frame had value byte `00` because the payload was zero, so which
  field drives byte 4 of `55 05 02 .. ..` is untested.
- **Which op is OUT1 and which is OUT2 is unknown.** Op `03` (type 5) and op
  `04` (types 6–15) are both candidates and neither is identified.
- **No actuator frame has been sent**, by design. The multimeter baseline on
  OUT1/OUT2 has not been taken yet.
- Types 2, 3, 4, 16 emitted no frame at all — either invalid types or paths
  that return early. Unexplained.

## 2026-10-10 — Live desktop indicator UI for IN1/IN2, running on the board
- **`tools/ema_ui.py` — new.** A PyQt4 app that puts two indicator lamps on the
  board's own desktop, one per digital input, driven by real STM8S207 traffic.
  Bridge an input to GND and its lamp lights. This turns the decoded byte map
  into something you can verify by eye, live.
- **How it gets fresh data.** The STM8 answers one open with one status frame
  and then goes quiet, so the reader cycles close/open on a background thread
  (open, collect 1.5 s, close, pause). Serial work is off the Qt thread, so the
  window stays responsive and the lamps repaint immediately.
- **The lamp logic is the decoded mapping**, not a guess: byte 6 = IN1,
  byte 7 = IN2, both **active-low**, so the lamp is lit when the byte is `00`.
- **Launched on the board's desktop** via `/root/Desktop/EMA_Inputs.sh`, which
  any desktop user can double-click. Verified running as PID 12067 on
  `DISPLAY=:0`, holding `/dev/ttySAC0`, with an empty error log.
- **Still strictly read-only.** It transmits only `55 04 01 01` (open) and
  `55 04 01 00` (close). No GPO, relay or Wiegand command.
- Board-side prerequisites found by probing rather than assumed: **PyQt4 is
  installed** (`/usr/lib/python2.7/dist-packages/PyQt4`), and the desktop is a
  live GNOME session (metacity + `gnome-session --session=ubuntu`) on `:0`.
  Tk, PySide and PyQt5 are all absent, so PyQt4 is the only viable toolkit.

### Tested
    python2 -m py_compile ema_ui.py                    -> PY2 SYNTAX OK
    setsid env DISPLAY=:0 python2 /root/ema_ui.py      -> pgrep = 12067
    /root/ema_ui.log                                   -> empty (no errors)
    fuser /dev/ttySAC0                                  -> 12068 12190 (UI holds it)
    ls /root/Desktop/                                   -> EMA_Inputs.sh present
    user confirms the window is visible on the VNC desktop

### Not tested
- **The lamps were not observed changing from here** — this session cannot see
  the VNC display. The user must bridge IN1/IN2 and confirm the lamps light.
  The underlying byte mapping is already proven by the capture logs; only the
  display path is unverified.
- Lamp rendering (`QPainter` ellipse + label) has not been visually checked for
  layout or colour on this 470x400 window.
- Closing the window leaves the reader thread to exit on its next loop; not
  explicitly reaped.

## 2026-10-10 — IN1 and IN2 DECODED by physical test; board-side input monitor built
- **Both digital inputs on the header are now decoded from live traffic.** No
  guessing: each was identified by bridging it to GND while a capture ran and
  watching exactly which frame byte changed.
- `tools/ema_capture.py` — new. Cycles open/collect/close so the STM8 is
  re-elicited repeatedly (it answers one open with one status frame, then goes
  quiet), groups frames per cycle, and prints a per-byte table that flags any
  position whose value differs between cycles.
- **Result, from `55 0a 03 00 01 01 BB RR 00 00`:**

  | Input | Byte | Idle | Bridged | Observed window |
  |---|---|---|---|---|
  | **IN1** | 6 | `01` | `00` | 00:51:43 → 00:52:10 (27 s) |
  | **IN2** | 7 | `01` | `00` | 00:53:47 → 00:54:04 (17 s) |

- **Both inputs are active-low** (`00` = asserted). Expected for opto-isolated
  24 V inputs.
- **The bits are independent.** Shorting IN1 left byte 7 at `01`; shorting IN2
  left byte 6 at `01`. The two tests never overlapped.
- Raw captures kept: `logs/ema_cap_in1.log`, `logs/ema_cap_in2.log`.
- **Still nothing has been driven.** Only open/close frames were ever sent.

### Tested
    ema_capture.py --cycles 4 --hold 3      -> 4/4 cycles, identical status frame
    40-cycle background capture, 229 status frames parsed
    IN1 bridged  -> byte6 01->00 for 27s, then 00->01
    IN2 bridged  -> byte7 01->00 for 17s, byte6 stayed 01
    distinct frames seen: (1,1) x147, (1,0) x79, (0,1) x41; never (0,0)

### Not tested
- **The combined state was never exercised.** Bridging both inputs together
  should give `55 0a 03 00 01 01 00 00 00 00`, a frame never yet observed. That
  is the remaining proof that the two bits are independent and not correlated.
- **OUT1 / OUT2 are still not driven.** That needs the `_EMA_EVENT` layout, and
  no actuator frame has been sent.
- Frames in capture cycles 1-4 carried a `01 00` pattern before any input was
  touched. Treated as stale buffered data from the prior session; the steady
  state from cycle 5 onward is what the conclusions rest on.

## 2026-10-10 — SoC↔STM8 LINK FOUND AND PROVEN: `/dev/ttySAC0` @ 115200 8N1
- **The single blocker is solved.** The board talks to its STM8S207 over
  **`/dev/ttySAC0` at 115200 baud, 8N1, raw**, and the link was observed
  open, acknowledged, and closed.
- **Method: stop guessing the protocol, use Daikin's own code.** Compiled a
  small C++ stub against the installed `libemaLib_arm_1.0.1.so` — the board has
  `g++ 4.6.3` and `libQtCore.so.4`, and C++ name mangling resolves the stripped
  library's symbols, so no headers are needed. The library opened the port
  itself, which identified it outright.
- **Framing recovered from live traffic** (captured with an `LD_PRELOAD` shim
  that hooks `open`/`read`/`write` on the serial fd — the board has no `strace`):
  - `0x55` | LEN | payload… | `00 00` — SOF, **total** length, payload, trailer
  - open `55 04 01 01` → ack `55 04 01 01`
  - status `55 0a 03 00 01 01 xx xx 00 00`
  - close `55 04 01 00` → ack `55 04 01 00`
- **`tools/ema_link.py` now talks to the STM8 with no vendor code at all** —
  plain pyserial at 115200, its own frame parser, and change tracking that flags
  which byte positions carry live state. This is the portable artifact.
- **Found a plain-C API in the same library**, so the protocol never has to be
  reimplemented: `ema_createEMA`, `ema_destroyEMA`, `ema_open`, `ema_close`,
  `ema_readEvent`, `ema_writeEvent`, `ema_cancelPendingReadEvent`,
  `ema_clearEventQueue`, `ema_getEMAVersion`. Unmangled symbols, so Python
  `ctypes` can call them directly.
- **Two dead ends closed by measurement, not assumption:**
  * `/dev/ttySTM8` is a symlink to `/dev/pts/0` — a pseudo-terminal, not a port.
  * The STM8 does **not** stream status. A 60-second capture received the ack
    plus exactly one status frame, then silence. Earlier "periodic" frames were
    an artefact of a shorter run.

### Tested
    g++ ... -l:libemaLib_arm_1.0.1.so -lQtCore -lpthread   -> builds and LINKS
    LD_PRELOAD=opentrace.so ./ema_probe                     -> RESULT: LINK IS LIVE
    probe trace: [TRACE] open("/dev/ttySAC0")               -> port identified
    probe trace: [TX] 55 04 01 01 / [RX] 55 04 01 01        -> open + ack
    probe trace: [RX] 55 0a 03 00 01 01 01 01 00 00         -> status frame
    probe trace: [TX] 55 04 01 00 / [RX] 55 04 01 00        -> close + ack
    tcgetattr on the fd -> in=4098 out=4098 (B115200), 8N1, raw
    60s capture -> 2 frames total (ack + one status); NOT a stream
    nm -D CMIMIRDemo | grep ema_ -> ema_createEMA/ema_open/ema_readEvent/...
    python2 /root/ema_link.py --seconds 25 -> opened, acked, decoded 2 frames
    TX counted over a 60s run -> 2 (open and close only)

### Not tested
- **No actuator frame was ever sent.** Only open and close went out. Nothing has
  been driven; no GPO, relay, Wiegand or input was touched.
- **The `_EMA_EVENT` struct layout is still unknown** — field offsets and the
  event-type enum. That is what now blocks reading IN1/IN2 and driving
  OUT1/OUT2, not the link itself.
- **Which status byte is which input is unproven.** One burst showed byte 6
  alternating `01`/`00`, which is suggestive but not evidence. The clean test is
  to toggle IN1 while `ema_link.py` runs.
- `readEvent()` returned `-9` on every poll. Understood (nothing armed via
  `setReadEvent`), but the success path was not exercised.
- The 93LC66A EEPROMs were still never positively scanned.

## 2026-10-10 — Workspace cleaned; board inventory re-measured from the live board
- **Scope change: this project is now only about the board.** The Philips Dynalite
  DDLE802 work and the ECU-30 Windows/Android-USB driver hunt were both dead ends
  and are moved to `archive/` — **moved, not deleted**, so nothing is lost. To
  discard them for good, delete the `archive/` directory; to get one back, move it
  out again.
- **Re-measured every fact over SSH instead of trusting old notes.** Three new
  tools, all strictly read-only (no writes, no register pokes, no ports opened):
  `tools/board_inventory.py` (full survey, writes `docs/raw/BOARD-raw.md`),
  `tools/board_stm8_link.py` (chased the STM8 link), `tools/board_facts.py`
  (settled the three open questions). Old one-off probes are in
  `archive/board-oneoff-probes/`.
- **`docs/BOARD.md` is the new single source of truth** — identity, CPU, RAM, ROM,
  an ASCII architecture diagram, and a **15-row peripheral checklist** marking each
  item WORKS or BLOCKED. Raw evidence kept verbatim in `docs/raw/`.
- **Three findings that change the picture:**
  * **`/dev/ttySTM8` is a red herring.** It is a symlink to `/dev/pts/0`, a
    pseudo-terminal left over from an earlier capture attempt. It is not a serial
    port and talks to no chip. Anyone treating it as the STM8 link is chasing
    nothing.
  * **The second RJ45 cannot appear in Linux at all.** The kernel has no native
    GMAC driver (`macb`/`dwmac`/`stmmac` all absent) and there is **no `ethernet@`
    node anywhere in the device tree**. The only NIC is `eth0` = `smsc95xx`, the
    LAN9512 on USB. This confirms the physical reading: RJ45 #2 is on the STM8.
  * **The micro-USB port is the USB OTG/debug port, and it is not broken.** No PC
    driver will ever bind to it because it is not a host port. The board has
    `s3c-usbgadget` loaded but **no UDC registered and no gadget configured**, so
    it presents nothing at all to a PC. Fixing it is a board-side `configfs`
    change (ADB or CDC-ACM), not a PC driver — which is what the earlier ADB work
    was unknowingly chasing.
- **Confirmed real vs phantom serial:** only `/dev/ttySAC0..3` are bound to
  `s5pv210-uart`. `/dev/ttyS0..3` are 8250 stubs reporting `port:00000000 irq:0`,
  i.e. no hardware behind them. `ttySAC1` is the kernel console.
- **12 of 15 peripherals are now classified.** WORKS: 12 V header, RJ45 #1, WM8960
  audio, 4× USB, micro-USB (as a port), 8 GB eMMC, HDMI. BLOCKED behind the
  unknown SoC↔STM8 link: RJ45 #2, RS232, RS485, IN1/IN2, OUT1/OUT2, Wiegand, the
  two 93LC66A EEPROMs.

### Tested
    python -c "import ast; ast.parse(...)"                  -> SYNTAX OK (all 3 tools)
    python tools/board_inventory.py --out docs/raw/BOARD-raw.md -> wrote (over SSH)
    python tools/board_stm8_link.py                         -> ran, 9 probe groups
    python tools/board_facts.py                             -> ran, 3 probe groups
    ssh root@192.168.100.127 ls -l /dev/ttySTM8             -> /dev/ttySTM8 -> /dev/pts/0
    ssh ... ls /sys/class/net/                              -> eth0 driver=smsc95xx only
    ssh ... lsmod | grep -iE 'macb|dwmac|stmmac'            -> (nothing)
    ssh ... find /proc/device-tree -iname '*ethernet*'      -> (nothing)
    ssh ... ls /sys/class/udc /sys/kernel/config/usb_gadget -> both absent
    ssh ... cat /proc/tty/driver/serial                     -> ttyS0-3 all irq:0

### Not tested
- **The SoC↔STM8 link is still unidentified.** No port has been opened, nothing
  has been written to the board, and no peripheral has been actuated. This remains
  the single blocker for 6 of the 8 BLOCKED rows.
- **The 93LC66A EEPROMs were never positively scanned.** `i2cdetect` is not
  installed on the board, so the `0x50–0x57` range is untested. Their absence is a
  negative from bus enumeration, not a confirmed scan. Not ruled out: SPI (no
  controllers exist), or an I2C bus Linux cannot see.
- **RS232/RS485 wiring is assumed, not confirmed.** The physical inspection says
  STM8; nothing in Linux confirms or contradicts it.
- `docs/BOARD.md` RAM figure is a single snapshot (916 MB of 991 MB in use) —
  not investigated.

## 2026-10-10 — BOARD IDENTIFIED: Daikin CMIMIR board; vendor tool launched
- **The board is a Daikin CMIMIR / Intelligent Manager HVAC controller**, not a
  generic SBC. This was revealed by the user spotting an **STM8S207** MCU, then
  confirmed from software: `/usr/local/bin/CMIMIRDemo` and its vendor libraries
  are installed (`libemaLib_arm_1.0.1.so`, `libcmirisLib2_arm_2.0.92.so`,
  `libcmicolorLib_arm_0.9.0.so`).
- **This single fact explains every dead end from earlier in this project:**
  * no Wiegand driver in Linux — Wiegand is the **STM8's** job, not the SoC's;
  * no usable Linux GPIO — the GPI/GPO are **STM8 pins**, not Exynos GPIOs;
  * `/dev/ttyS0..3` are phantom — the real RS232/RS485 hang off the **STM8**;
  * no GPIO expander on I2C, which had looked like a gap, but nothing was missing:
    the I/O simply is not on the I2C bus.
- `CMIMIRDemo` embeds the exact operation set the board is documented to have:
  `EMA_EVENT_TYPE_GPO1_WRITE`, `GPO2_WRITE`, `GPO12_WRITE`, `GPI12_READ`,
  `RELAY_WRITE`, `WIEGAND_READ_DATA`, `WIEGAND_WRITE_DATA`,
  `WIEGAND_SET_CONFIG`, `WIEGAND_GET_CONFIG`, `WIEGAND_AUTO_DETECT`,
  plus `OPEN`/`CLOSE`. GUI strings confirm the workflow: *"Device opened
  successfully!"*, *"Device has not opened yet! Please open first"*, and a
  `comboBox_SerialNumbers` port selector.
- `libemaLib` is a Qt `QextSerialPort` wrapper that enumerates `/dev/ttyS0`,
  `/dev/ttySAC0`, `ttyACM*` and `ttyUSB*` — so the SoC<->STM8 link is one of the
  Exynos UARTs. **ttySAC0, ttySAC2 and ttySAC3 are free** (ttySAC1 is the console).
- **Launched the tool on the board's X display** (`DISPLAY=:0`, the VNC session)
  and confirmed it is running as PID 3716, with no errors in its log.
- **Retracted the earlier plan to unbind the max77686 PMIC driver.** With the real
  architecture understood, that was the wrong target entirely — the PMIC was never
  involved in the GPI/GPO. The risk was avoided rather than taken.
- **Why:** the user opened the case and read the chip marking. Physical
  inspection beat every software probe, and found in one sentence what an hour of
  sysfs archaeology could not.

### Tested
    find / -xdev -iname '*stm8*' -o -iname '*wiegand*' -> (nothing; Linux side has no such files)
    file /usr/local/bin/CMIMIRDemo -> ELF 32-bit LSB, ARM, dynamically linked, stripped
    strings CMIMIRDemo -> EMA_EVENT_TYPE_{GPO1_WRITE,GPO2_WRITE,GPO12_WRITE,GPI12_READ,
        RELAY_WRITE,WIEGAND_READ_DATA,WIEGAND_WRITE_DATA,WIEGAND_SET_CONFIG,
        WIEGAND_GET_CONFIG,WIEGAND_AUTO_DETECT,OPEN,CLOSE}, "Device opened successfully!",
        "Device has not opened yet! Please open first", comboBox_SerialNumbers
    ldd CMIMIRDemo -> libcmirisLib2_arm_2.0.92.so, libemaLib_arm_1.0.1.so,
        libcmicolorLib_arm_0.9.0.so, libQt4
    ls /root/Desktop/ -> Link_to_CMIRDemo -> /usr/local/bin/CMIMIRDemo
    ls /usr/local/lib/ -> 3 vendor .so + python2.7 site/dist-packages (no bindings)
    strings libemaLib -> /dev/ttyS0, /dev/ttySAC0, ttyACM*, ttyUSB*,
        "USB-serial adapter"; QextSerialPort::setBaudRate/setDataBits/setParity
    ls /tmp/.X11-unix/ -> X0  (display :0 present)
    fuser /dev/ttySAC0 /dev/ttySAC2 /dev/ttySAC3 -> (no holders; ttySAC1 is the console)
    DISPLAY=:0 nohup /usr/local/bin/CMIMIRDemo & -> ps confirms PID 3716 running
    /tmp/cmimirdemo.log -> empty (no startup errors)

### Not tested
- **The GUI window has not been visually confirmed** — it is running, but this
  agent cannot see the VNC session. The user must confirm the window appeared.
- **The STM8 link was never opened**, so no GPO/GPI/relay/Wiegand operation has
  actually been performed. Which of ttySAC0/2/3 carries the link is still unproven.
- No Python bindings exist for the EMA libraries, so scripting the I/O from Python
  would require writing ctypes bindings against `libemaLib` — not attempted.
- The STM8 firmware itself remains a black box; its protocol is undocumented here.

## 2026-10-10 — GPO/GPI: corrected a wrong earlier finding, mapped the usable routes
- **Retracted my earlier claim that GPIO was unavailable.** I had concluded that from
  `ls /sys/class/gpio/` being empty and `lsmod | grep gpio` returning nothing. Both
  checks were misleading: the relevant config options are **built-in (`=y`)** so they
  never appear in `lsmod`, and the export directory is simply absent.
- GPIO **is** registered and enumerable — `/sys/kernel/debug/gpio` lists every Exynos
  bank from GPA0 through GPV4 (~300 pins), confirmed with
  `CONFIG_GPIOLIB=y`, `CONFIG_SAMSUNG_GPIOLIB_4BIT=y`, `CONFIG_S3C_GPIO_CFG_S3C24XX=y`.
- **Pins already in use, recorded so they are not clobbered:** gpio-31 STATUS LED (out),
  gpio-38 Backlight (in), gpio-202 KEY POWER (in), gpio-223 hdmi-cec (in),
  gpio-224 hpd-plug (in).
- **Established that no off-the-shelf GPIO tool can work here:** `/sys/class/gpio`
  missing, `/dev/gpiochip*` missing (confirmed by `find /dev -iname "*gpio*"` →
  nothing), and no `gpioget`/`gpiotool`/`libgpiod` installed. Those all depend on
  the two missing interfaces.
- **Identified the two routes that do work:** (1) `/dev/mem` direct register access —
  present as `crw-r----- root kmem` — using the Exynos4 per-bank layout
  CON/DAT/PUD/DRV at +0x00/+0x04/+0x08/+0x0C; (2) the **max77686 PMIC's own GPIOs**
  over `/dev/i2c-0`, since the PMIC is bound at `0-0009` (`modalias i2c:max77686`).
  Noted `CONFIG_I2C_GPIO=y` and `CONFIG_I2C_CHARDEV=y` are also available.
- **Identified the true blocker and did not paper over it:** nothing on the board
  records which SoC pin each physical GPO/GPI connector is wired to. That mapping
  exists only in the schematic or must be found by driving candidate pins and
  probing with a meter. Offered to write the `/dev/mem` tool but deliberately did
  **not** touch live hardware registers without the user confirming they have a
  meter on the connector.

### Tested
    cat /sys/kernel/debug/gpio -> banks GPA0..GPV4 enumerated, ~300 pins
    ls -d /sys/class/gpio -> "No such file or directory"
    zcat /proc/config.gz | grep GPIO -> CONFIG_GPIOLIB=y, CONFIG_SYSFS=y,
        CONFIG_DEBUG_FS=y, CONFIG_SAMSUNG_GPIOLIB_4BIT=y, CONFIG_S5P_GPIO_DRVSTR=y,
        CONFIG_S3C_GPIO_CFG_S3C24XX=y, CONFIG_I2C_GPIO=y, CONFIG_I2C_CHARDEV=y
    mount | grep ' /sys ' -> sysfs mounted rw
    ls /sys/class/ -> 30 entries, none named gpio
    find /dev -iname "*gpio*" -> (nothing)   <- no char device either
    ls -l /dev/mem -> crw-r----- 1 root kmem
    ls -l /dev/i2c-* -> i2c-0,1,4,5,8 present, root-only
    /sys/bus/i2c/devices/0-0009/name -> max77686 ; modalias i2c:max77686
    ls /sys/bus/i2c/drivers/ -> dummy, exynos_hdcp, max77686, rtc-mcp7940n,
        s5p-hdmiphy, usb3503, wm8960-codec
    grep gpio /proc/iomem -> (nothing)
    pins in use -> gpio-31 out, gpio-38 in, gpio-202 in, gpio-223 in, gpio-224 in

### Not tested
- **No pin was driven.** No read or write to `/dev/mem` was performed, and no
  register was modified. The route is documented, not exercised.
- **The board's actual GPO/GPI-to-SoC-pin mapping is unknown.** It was not
  determined, so it is not possible yet to say which pin controls which connector.
- Whether the GPO/GPI connectors work at all on this board is **unverified**; the
  four used pins found are board functions (LED, backlight, HDMI), not the
  user-facing connectors.

## 2026-10-10 — CPU3 flap root-caused; idle cores proven unusable; log spam stopped
- Root-caused the `CPU3: Booted secondary processor` / `CPU3: shutdown` loop that
  filled 188 MB of logs before the earlier cleanup. Topology: `present=0-3`,
  `online=0,3`, `nproc=2` — cpu0 stable, **cpu1 and cpu2 permanently offline**,
  cpu3 flapping every few seconds.
- **Ruled out every suspicious suspect, with evidence:**
  * `ps aux | grep lava` → nothing running. The Linaro **PM-QA / LAVA test suite**
    is installed at `/root/.local/share/lava_test/installed-tests/pwrmgmt/pm-qa/`
    (includes `cpuhotplug_08.sh`, `cpuidle_killer.c`) — but **no test is running**.
    It is a leftover QA suite, not the cause.
  * `/etc/init.d/ondemand` references `cpu*/cpufreq/scaling_governor`, **not**
    `cpu*/online` — `grep -n online` returns nothing. Not the cause.
  * `/etc/cron.d/john` (John the Ripper cracker) — **both cron lines are commented
    out**. Harmless red herring.
  * No userspace watchdog daemon; only the standard `[watchdog/0]` kernel thread.
  * No kernel panic / oops / BUG in dmesg — the "shutdown" lines are CPU shutdown,
    not a crash.
- **Tried to enable the two idle cores and both FAILED** — writing `1` to
  `cpu1/online` and `cpu2/online` each dropped straight back to `0` within 8s. The
  kernel cannot boot those cores in this configuration; it is a hardware/firmware
  limitation, not a userspace setting. So there is no hidden performance to unlock.
- **Offlined cpu3**, which succeeded and **stopped the log spam completely**
  (dmesg CPU3 event count frozen at 103 across a 12s sample).
- **Recorded the tradeoff honestly: the board now runs on 1 core, not 2.** Before,
  cpu3 was online for only a second or two between flaps, so its real contribution
  was small, but this is still a reduction and `--revert` is provided.
- Also documented two unrelated board facts: the SoC is **EXYNOS4412** (`Machine:
  ODROIDX`), and **`/dev/rtc0` exists but fails** (`hwclock: Invalid argument`), so
  the board has **no working RTC** — which is why every login is timestamped
  `Thu Jan 1 09:00 1970`.
- **Flagged an unexplained reboot**: `last` shows the previous SSH session ended as
  **"crash"** at 21:36:32 with a boot at 21:35:45, partway through this session.
  Nothing performed here would reboot a board (the cleanup only removed logs and
  the apt cache). Cause **not yet established**.
- Board verified healthy afterwards: no broken packages, 0 still upgradable,
  SSH 22 / RDP 3389 / VNC 5900 all still open.

### Tested
    /sys/devices/system/cpu/{present,online,possible} -> 0-3 / 0,3 / 0-3 ; nproc=2
    cpu0=1 cpu1=0 cpu2=0 cpu3=1
    ps aux | grep -i lava -> (nothing running)
    grep -n online /etc/init.d/ondemand -> (no match; governor only)
    /etc/cron.d/john -> both cron lines commented out with #
    ps aux | grep watchdog -> only [watchdog/0] kernel thread
    dmesg | grep -iE 'panic|oops|BUG:|Call trace' -> nothing
    echo 1 > cpu1/online -> after 8s reads 0  FAILED
    echo 1 > cpu2/online -> after 8s reads 0  FAILED
    echo 0 > cpu3/online -> succeeded
    CPU3 dmesg events 103 -> 103 over 12s  (STOPPED)
    final state 0=1 1=0 2=0 3=0, nproc=1
    dmesg head -> CPU EXYNOS4412 (id 0xe4412211), Machine: ODROIDX
    hwclock -> "ioctl(RTC_RD_TIME) to /dev/rtc0 failed: Invalid argument"
    last -> "root pts/1 192.168.100.10 21:36:32 2026 - crash"
    postcheck -> broken (nothing); 0 still upgradable; ports 22/3389/5900 OPEN

### Not tested
- **Why cpu1 and cpu2 refuse to boot was not established** — only that they cannot.
  Likely SoC power/firmware sequencing in this vendor kernel, unproven.
- **The 21:36 crash was not root-caused.** No kernel panic was logged, and the
  cause remains open.
- Whether running on 1 core instead of 2 hurts a real workload was **not measured**;
  no benchmark was run before/after.
- The CPU3 parking is **not persistent across reboot** — it was a runtime sysfs
  change only, and nothing was added to init scripts.

## 2026-10-10 — Cleanup: ~1.1 GB freed on the board, 42 MB on the PC
- Surveyed before deleting anything. Biggest wins: **811 MB** of downloaded `.deb`
  files in `/var/cache/apt/archives` (left by the upgrade) and **277 MB** in
  `/var/log` (188 MB of it a single rotated `kern.log.1`).
- Board cleanup ran: `apt-get clean`, removed rotated/archived logs, truncated the
  oversized current `kern.log`/`syslog`, dropped unresolvable apt `Packages.lz4`
  lists, cleared `/tmp`, removed `/root/.bashrc~` and `.bzr.log`.
  **`/var/log` 277 MB -> 3.1 MB. Disk 1.1 GB free (80%) -> 2.1 GB free (59%).**
- **Autoremove: protected `libkms1` deliberately.** `apt-get -s autoremove` listed it
  as an orphan, but it is the Kernel Mode Setting library the display stack needs —
  and this board has no physical screen, so losing the GUI means losing VNC and RDP
  along with it. Holding it made apt **abort rather than override**:
  `E: There are problems and -y was used without --force-yes`. The hold did its job.
- Removed the other 8 orphans explicitly instead: `filezilla-common`,
  `firefox-globalmenu`, `gir1.2-ubuntuoneui-3.0`, `libtinyxml2.6.2`,
  `libubuntuoneui-3.0-1`, `libwxbase2.8-0`, `libwxgtk2.8-0`,
  `thunderbird-globalmenu` (16.7 MB).
- **Verified after cleanup: no broken packages, `libkms1` still installed, and
  SSH 22 / RDP 3389 / VNC 5900 all still OPEN** — the real proof the display stack
  was not harmed.
- PC side: `temp/` 42.4 MB -> 0. Duplicated platform-tools, the Google USB driver,
  the two zip downloads, the HTML scrapes and the Dynalite PDFs were all
  re-downloadable. Kept only `ecu30_ed25519`. Updated `memory-bank/techContext.md`,
  which had claimed the reference sheets were stored in `temp/`.
- **Deliberately not done:** PC Python packages were left alone. There are ~100
  outdated packages (esphome, bleak, aiohttp, an automation stack), but removing
  or bulk-upgrading those risks breaking a working installation for no space gain.
- **Why:** the disk was at 80% on a 5.3 GB rootfs with 1.1 GB free — tight for a
  system with no easy recovery path, and every gigabyte is real safety margin.

### Tested
    board disk before 5.3G / 4.1G used / 1.1G free / 80%
    board disk after  5.3G / 3.0G used / 2.1G free / 59%
    /var/log 277M -> 3.1M ; /var/cache/apt/archives 811M -> cleared
    apt-mark hold libkms1 -> "libkms1 set on hold."
    apt-get -y autoremove -> "E: There are problems and -y was used without --force-yes"  (aborted, nothing removed)
    explicit remove of the other 8 -> 8 removed, 16.7 MB freed
    dpkg -l libkms1 -> "hi  libkms1 2.4.46-1ubuntu0.0.0.1  (held, installed)"
    postcheck -> broken packages (nothing); 1682 ii, 27 rc, 4 hi
    ports 22 / 3389 / 5900 on 192.168.100.127 -> all OPEN after cleanup
    d:\phl\temp 42.4 MB -> 0.0 MB

### Not tested
- **The board has still not been rebooted** — `/var/run/reboot-required` remains.
  Whether it boots cleanly after the upgrade is still unknown.
- **No GUI session was actually opened after the cleanup.** Ports 22/3389/5900 being
  open proves the services are listening, not that the desktop renders. The real
  test is opening the VNC window.
- The 27 `rc` (config-only leftover) packages were **not** purged — that would
  free very little and was not requested.
- The oversized log growth (188 MB in one rotated `kern.log.1`) was **not root-
  caused**; only the symptom was cleaned. Something on the board is logging heavily
  and will refill `/var/log` again.

## 2026-10-04 — TigerVNC installed; VNC session to the board launched
- Installed **TigerVNC Viewer 1.16.2** via `winget install TigerVNC.TigerVNC`
  (SourceForge and RealVNC direct downloads were both blocked — SourceForge
  returned 403 and `download.realvnc.com` does not resolve; winget fetched and
  hash-verified the same SourceForge package successfully).
- Installed to `C:\Program Files\TigerVNC\vncviewer.exe`.
- Started `tools\vnc_forward.py` in the background (**PID 15748**) forwarding
  `127.0.0.1:5900` -> `[fe80::225:ffff:fefe:4445%16]:5900`.
  Verified listening, and verified it relays a real `RFB 003.007` greeting.
- Launched the viewer at `127.0.0.1:5900` (**PID 18784**). Both processes confirmed
  alive after launch.
- The forwarder is required: TigerVNC cannot reliably address an IPv6 link-local
  target with a scope id, so localhost is the reliable front door.
- **Why:** this is the first route that gives a screen on a headless board, and a
  terminal there lets us run `adb tcpip 5555` and finally clear the `unauthorized`
  RSA prompt that blocked every USB attempt.

### Tested
    winget search tigervnc -> TigerVNC.TigerVNC 1.16.2
    winget install TigerVNC.TigerVNC --silent -> "Successfully installed"
    C:\Program Files\TigerVNC\vncviewer.exe -> ProductVersion 1.16.2
    Start-Process vnc_forward.py --listen 5900 -> PID 15748
    Get-NetTCPConnection -LocalPort 5900 -State Listen -> True
    localhost:5900 handshake -> "RFB 003.007"  (relayed from the board)
    Start-Process vncviewer.exe 127.0.0.1:5900 -> PID 18784, alive
    Get-Process 15748,18784 -> both alive

### Not tested
- **The VNC session itself has not been observed.** The viewer was launched, but
  this agent cannot see its window, so whether a desktop actually rendered is
  unconfirmed — the user must report what appears on screen.
- No ADB session exists yet; `adb devices` is still empty. `adb tcpip 5555` has not
  been run because that requires being logged into the board's desktop first.
- Neither background process survives a reboot or session change; both must be
  restarted with the commands documented in the handoff.

