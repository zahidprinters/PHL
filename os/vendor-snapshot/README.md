# CMITECH vendor binaries — archived from ECU-30

Archived 2026-10-11 from the board before deletion (rootfs slimming, PHL project).
Origin: CMITECH ECU-30 stock rootfs, Linaro 12.11, kernel 3.0.68-svn r0.

| File | Board path (original) | Size | MD5 |
|---|---|---|---|
| CMIMIRDemo | /usr/local/bin/CMIMIRDemo | 129760 | ca7f67398da703f6f78d14bddfc7afee |
| libcmicolorLib_arm_0.9.0.so | /usr/local/lib/ | 48845 | 35f5076e9b9b0e6164e02b30eaf365f0 |
| libcmirisLib2_arm_2.0.92.so | /usr/local/lib/ | 1085688 | e9ff65096b36200fa0bbea24db1daf2b |
| libemaLib_arm_1.0.1.so | /usr/local/lib/ | 47296 | 0e6795cb3768397270bb2eaa216c466c |

Why kept:
- `libemaLib_arm_1.0.1.so` — the EMA telemetry protocol implementation; our toolset
  re-implemented it (`tools/ema_decode.py`), but this is the reference/original.
- CMIMIRDemo + cmicolor/cmiris libs — vendor demo app; no camera work is planned
  (decision: "no need cam"), but kept in case the demo is ever needed again.

Hashes were verified (board `md5sum` == PC `Get-FileHash -Algorithm MD5`).
Removed from the board including the Desktop symlink `Link_to_CMIMIRDemo`.
