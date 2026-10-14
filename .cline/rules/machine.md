# This machine — toolchain inventory

Verified on 2026-09-25. Do not re-discover these by probing; read them here.
If something stops matching, verify once and update this file.

## Why this file exists
Toolchain paths are global facts. Rediscovering them costs a session and risks
acting on a stale answer. Project-specific details belong in that project's
`docs/ARCHITECTURE.md`, never here.

## Runtimes
| Tool | Version | Notes |
|---|---|---|
| Node.js | 25.3.0 | satisfies Playwright MCP (needs 18+) |
| Python | 3.11.9 | `C:\Users\PC\AppData\Local\Programs\Python\Python311` |
| PHP | 8.2.12 | XAMPP, `C:\xampp\php\php.exe` |
| Composer | 2.10.2 | |
| Git | 2.55.0 | identity configured globally |
| Cline CLI | 3.0.60 | **not** the same product as the VS Code extension (4.1.21) |
| PowerShell | 7 | commands here assume pwsh, not Windows PowerShell |

`pyserial` 3.5 is installed in the system Python — usable immediately for
serial work, no venv needed.

## ESP-IDF
- Framework: `D:\esp32-tools\esp-idf` — **v5.3.2**
- Activate: `& 'D:\esp32-tools\esp-idf\export.ps1'` then use `idf.py`
- Standalone launcher: `C:\Espressif\tools\idf-exe\1.0.3\idf.py.exe`
- Toolchain: xtensa-esp-elf, riscv32-esp-elf, openocd, cmake, ninja under
  `C:\Users\PC\.espressif\tools`
- Installed target: **esp32s3**

**`idf.py mcp-server` does not exist in v5.3.2.** Verified: zero matches for
`mcp` in `D:\esp32-tools\esp-idf\tools`. The command only exists on `master`,
and its docs require the `mcp` feature installed via EIM — and `eim` is not
installed. Do not promise an ESP-IDF MCP; use the terminal instead.

`idf.py monitor` is interactive and will hang a non-interactive shell. Use
`~/.cline/tools/serial_capture.py` for log capture.

## Arduino
- `D:\esp32-tools\arduino15` — Arduino IDE 1.5 core tree
- `D:\esp32-tools\arduino-sketch` — sketch location

## Hardware
- Serial port in use: **COM3**
- Before flashing: confirm the target and the port. A wrong port bricks nothing
  but wastes a flash cycle; a wrong target does damage.

## Not installed
- Docker (so the GitHub MCP local-server option is unavailable — use the
  remote server)
- `eim` (ESP-IDF Installation Manager)
- Espressif VS Code extension
