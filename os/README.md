# `os/` — OS images, backups & board tooling (permanent archive)

Everything needed to recover, re-flash, and experiment with the ODROID-X board
lives here. **This folder is permanent — do not treat it like `temp/`.** The
old `temp/` copies were moved here on 2026-10-11 so nothing is lost to a
scratch-folder cleanup.

> ⚠️ There is **no git repo** for this project — **this disk is the only copy.**
> The eMMC backup in `backup-eMMC/` is irreplaceable. Keep it safe.

---

## Board access (current)

| | |
|---|---|
| **Board IP** | `192.168.100.127` (static, on the office LAN) |
| **SSH** | `ssh root@192.168.100.127` — password: env `PHL_BOARD_PASS` (= `pakistan`) |
| **VNC** | `192.168.100.127:5900` (vino — autostarts inside the bare **openbox** session; **direct access since 2026-10-12: no Allow/Deny prompt, no password**) |
| **RDP** | `192.168.100.127:3389` (xrdp) |
| **Board** | ODROID-X, Exynos 4412, 1 GB RAM, kernel 3.0.68 (Hardkernel build) |

## Current hardware state

- **Boots from the SD card.** eMMC module is **removed** (kept as backup).
- SD card layout:
  - `p1` boot (128 MB, FAT32) — unchanged
  - `p2` rootfs (5.4 GB, ext4) — the running OS, stripped 2026-10-11/12: **776 MB used, ~4.3 GB free** (unity → LXDE → **bare openbox appliance**, 1160→637 packages; details in `CHANGELOG.md`)
  - `p3` **`/data`** (54 GB, ext4, `LABEL=data`) — **51 GB free** for experiments,
    auto-mounts via `/etc/fstab`.
- **eMMC is out and safe.** Its full image is in `backup-eMMC/`.

---

## Folder map

### `backup-eMMC/` — the safety net (irreplaceable)
| File | What |
|---|---|
| `emmc_backup.img.gz` | Full raw image of the original eMMC (2.43 GB compressed; decompresses to exactly **7,818,182,656 bytes**). |
| `emmc_backup.log` | The `dd` capture log from when the backup was taken. |

- **SHA256 of the raw (gunzipped) image:** `70b758114c2eb03cab45228aa14f5dc1b7519c37bededd3a107cebb040e305f0`
- **Verify the backup** (decompress + hash): `python scripts/emmc_verify.py`
- **This is what you restore from if the SD card ever breaks.**

### `scripts/` — reusable board tooling (24 files)
Run from an **elevated** PowerShell unless noted. Board scripts auto-read
`PHL_BOARD_PASS` from the environment.

**Card writing / verification (Windows, elevated):**
- `Write-ImageToCard.ps1` — write an image to the USB card reader (defaults to
  the eMMC backup image).
  ```powershell
  powershell -ExecutionPolicy Bypass -File scripts\Write-ImageToCard.ps1 -Image <path\to.img> -ConfirmDisk 1
  ```
- `Compare-Card.ps1` — hash the card vs. an image and report MATCH/MISMATCH
  (defaults to the eMMC backup image).

**eMMC backup / restore:**
- `emmc_backup.py` — re-dump the board's current storage over SSH (writes to `backup-eMMC/`).
- `emmc_verify.py` — verify `backup-eMMC/emmc_backup.img.gz` against the known SHA256.

**Board helpers (SSH, not elevated):**
- `reboot_wait.py` — reboot the board and wait for it to return on the network.
- `mkdata_part.py` / `mkdata_resume.py` — (re)create the `/data` partition.
- `card_size.py`, `sd_ready.py`, `sd_boot_confirm.py` — storage/size checks.
- `vnc_state.py`, `vnc_restore.py`, `vnc_restore2.py` — inspect/restore the VNC (vino) server.
- `clone_*.py` — the eMMC→SD clone helpers.
- `emmc_probe.py`, `emmc_hash_start.py`, `verify_start.py` — eMMC survey/verify helpers.

### `vendor-snapshot/` — CMITECH binaries, archived before deletion (2026-10-11)
| File | What |
|---|---|
| `CMIMIRDemo` | the vendor demo app (129,760 B, md5 `ca7f6739…`) |
| `libcmicolorLib_arm_0.9.0.so` | camera colour lib (48,845 B) — no camera work is planned |
| `libcmirisLib2_arm_2.0.92.so` | camera IR lib (1,085,688 B) |
| `libemaLib_arm_1.0.1.so` | the EMA protocol library our toolset re-implemented (47,296 B) |

All four were pulled off the board, md5-verified board↔PC identical, then
deleted from the board. Full hashes in `vendor-snapshot/README.md`.

### `logs/` — run logs
Reserved for command output / captures (e.g. a copy of `emmc_backup.log` if desired).

### `node-red/` — the HMI service (2026-10-11)
The live Node-RED instance runs **inside an Ubuntu 14.04 armhf chroot** on the
board (host glibc 2.15 is too old for any modern node; 16.04's glibc rejects
kernel 3.0.68 — see `CHANGELOG.md`). These are the two config files that make
it a boot service:

| File | Installed on the board as | What |
|---|---|---|
| `nodered.conf` | `/etc/init/nodered.conf` | upstart job — bind-mounts `/proc /dev /sys` into `/data/chroot14`, execs `node-red --userDir /data/nodered`, unmounts on stop, respawns |
| `settings.js` | `/data/nodered/settings.js` | uiPort 1880, all interfaces, flows in `/data/nodered/flows.json` |
| `hmi-flow.json` | *(deployed to the board's flow file)* | the starter HMI flow: `ui_tab` "HMI" + `ui_group` "Status" + inject(5s) → clock `ui_text` + random `ui_gauge`. **The Node-RED dashboard is the HMI** — the openbox session autostarts Firefox at `/ui` (see `desktop/`) |

Board-side layout (on `/data`, survives rootfs work):
- `/data/chroot14/` — the trusty chroot; node v10.24.1 at `/usr/local/node10`
  inside it; node-red 1.3.7 installed globally.
- `/data/nodered/` — userDir: `settings.js`, the flow file, `nodes/`, `lib/`, and
  `node_modules/` — **the Node-RED dashboard (`node-red-dashboard`) is installed
  HERE, as a userDir-local module, NOT global** (`npm ls -g` shows nothing by
  design; verify with `ls /data/nodered/node_modules/node-red-dashboard`).

Key facts / gotchas (details in `CHANGELOG.md` and `docs/ARCHITECTURE.md`):
- **⚠ Flow-file name (open 2026-10-13):** `settings.js` sets
  `flowFile: 'flows.json'`, but the deployed flow is
  `flows_linaro-ubuntu-desktop.json` and `flows.json` does **not** exist. A clean
  restart therefore serves an **empty** dashboard until the names are reconciled
  (rename the file to `flows.json`, or drop the `flowFile` override). See the
  CHANGELOG 2026-10-13 entry.
- **FF52 renders `/ui` magenta/unstyled** — the dashboard theme CSS compiles
  client-side from `app.min.less`; if that compile fails all widget CSS is
  stripped. Open issue, CHANGELOG 2026-10-13.
- `serialport` and `bcrypt` did **not** build (no compiler in the base chroot);
  the serial node type is absent — EMA/serial I/O goes through exec + the
  proven host python tools instead.
- EOL trusty armhf apt: **`ports.ubuntu.com`** serves it; `old-releases` has no
  trusty tree. node 10 needed `libstdc++.so.6`/`libgcc_s.so.1` grafted from a
  xenial tree (`GLIBCXX_3.4.20`).
- Upload `.conf` files with **LF** line endings; SSH exec has an **empty PATH**
  so chroot commands use `/usr/bin/env PATH=…`.
- **Cold-boot auto-start verified (2026-10-12)** after the power cycle:
  HTTP 200 with no manual `initctl start`.

### `desktop/` — the appliance X session (2026-10-12)
The desktop is deliberately bare: Node-RED is the interface; the X session
only hosts VNC (vino) and the EMA touchscreen app. Board files, byte-copied:

| File | Installed on the board as | What |
|---|---|---|
| `autostart` | `/etc/xdg/openbox/autostart` | plain-shell session autostart: `vino-server &` + `firefox http://localhost:1880/ui &` — **the Node-RED dashboard is the HMI now** (EMA_Controls.sh stays on the desktop for manual VNC launch). No panel/menu/wallpaper |
| `kiosk-rc.xml` | `/root/.config/openbox/rc.xml` | kiosk window rule — FF52 has no `--kiosk`, so openbox forces the Firefox window `decor no` + `fullscreen yes`. Overrides the `/etc/xdg` copy |
| `kiosk-user.js` | `/root/.mozilla/firefox/fdg2sjwb.default/user.js` | hardened FF52 profile prefs — kills default-browser prompt, session-restore-after-crash, quit/close warnings, telemetry, updates, safebrowsing, UITour |
| `lightdm.conf` | `/etc/lightdm/lightdm.conf` | root autologin, `user-session=openbox`, gtk-greeter |
| `openbox.desktop` | `/usr/share/xsessions/openbox.desktop` | session entry — `Exec=dbus-launch --exit-with-session openbox-session` starts the session bus |
| `dmrc-root` | `/root/.dmrc` | `Session=openbox` — outvotes lightdm.conf; keep it in sync |
| `fb-early.conf` | *(not installed — REVOKED 2026-10-13)* | upstart job: was `/etc/init/fb-early.conf.disabled`. **Never ran at any boot** (CRLF, then read-only rootfs even after `started mountall`); user revoked after the 2nd power cycle showed nothing |
| `fb_early.py` | *(not installed — REVOKED 2026-10-13)* | the 1080p mode-set + splash-paint script (kept as record: 1024x600 buffer truth, mmap-only fb, paint-until-X loop) |
| `splash.raw` | *(not installed — REVOKED 2026-10-13)* | the generated boot splash: raw BGRA, **1024x600** (2,457,600 B) — fb0's window buffer, which the FIMD scaler stretches to the 1080p output |
| `make_splash.py` | *(PC-side only)* | regenerates `splash.raw` (Pillow); part of the revoked experiment, kept for the record |

Gotchas (details in `docs/ARCHITECTURE.md`): openbox **3.5** autostart is
plain shell (`@command` lines silently do nothing), and `apt-mark unhold`
segfaults on precise's apt — use `dpkg --set-selections`.

**VNC direct access lives in dconf, not in a text file.** vino 3.4.2 reads
`org.gnome.Vino` (GSettings) — `/apps/vino/*` GConf keys are dead. The
committed settings (`/root/.config/dconf/user`) are already set; to re-apply
by hand (needs the session bus: `DBUS_SESSION_BUS_ADDRESS` from
`/proc/$(pgrep -x openbox)/environ`):

    gsettings set org.gnome.Vino prompt-enabled false
    gsettings set org.gnome.Vino notify-on-connect false
    gsettings set org.gnome.Vino icon-visibility never

(`authentication-methods ['none']` = no password, `view-only false` = control.)

---

## 🔧 Recovery recipe — restore the SD card from the eMMC backup

If the SD card ever fails to boot:

1. Power off the board. Put the **eMMC module back in**, flip the boot switch
   → **eMMC**, power on → boot to the known-good vendor OS.
2. On this PC, plug the card into the USB reader. In **elevated** PowerShell:
   ```powershell
   powershell -ExecutionPolicy Bypass -File d:\phl\os\scripts\Write-ImageToCard.ps1 `
       -Image d:\phl\os\backup-eMMC\emmc_backup.img -ConfirmDisk 1
   ```
   (Decompress `emmc_backup.img.gz` → `emmc_backup.img` first if you only have the `.gz`.)
3. Wait for the `OK: … MB/s` line, eject, flip switch → **SD**, remove eMMC,
   power on → the card is back to today's working state.
4. Optional verify: `scripts\Compare-Card.ps1` (point it at the backup image).

---

## Next steps (see `memory-bank/activeContext.md` for the live list)
1. **Wiegand** — OUT solved (2026-10-13/14); read side (W-IN) **pending**
   (deferred 2026-10-11).
2. ~~Analog I/O~~ — none on this board (user, 2026-10-14); audio only, and it
   already works.
3. ~~**Node-RED HMI**~~ — **INSTALLED AND LIVE (2026-10-11)**, http://192.168.100.127:1880.
   Ubuntu 14.04 armhf chroot at `/data/chroot14` + node v10.24.1 + node-red 1.3.7;
   upstart job `/etc/init/nodered.conf` (copies in `os/node-red/`). **Cold-boot
   auto-start not yet verified — blocked on the power cycle** (see the incident
   in `CHANGELOG.md`: host `/dev` nodes were deleted through a bind mount;
   `devtmpfs` restores them at boot).
4. Optional: **RTC init** — one `hwclock --systohc` (a write; needs the go-ahead).
