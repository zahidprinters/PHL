"""Connect to the ECU-30 board over SSH and inspect it (no changes made).

The password is read from the PHL_BOARD_PASS environment variable so it is never
written to this file, to a log, or to a shell history on the board.

    $env:PHL_BOARD_PASS = '<password>'
    python tools/board_ssh.py
"""

import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")

# Read-only probes. Deliberately nothing that mutates the board.
PROBES = [
    ("identity", "id; hostname; uname -a"),
    ("os", "cat /etc/os-release | head -5"),
    ("disk", "df -h / /boot 2>/dev/null | head -5"),
    ("memory", "free -h | head -3"),
    ("uptime", "uptime"),
    ("udev-ecu30", "dmesg 2>/dev/null | grep -iE 'usb 1-|ttyS|serial' | tail -5"),
    ("adbd", "ps aux | grep -E '[a]dbd' || echo 'adbd NOT running'"),
]


def main():
    """Run the read-only probes and print the results."""
    password = os.environ.get("PHL_BOARD_PASS")
    if not password:
        print("Set PHL_BOARD_PASS first.")
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, port=PORT, username=USER, password=password,
                       timeout=15, allow_agent=False, look_for_keys=False)
    except paramiko.AuthenticationException:
        print("AUTH FAILED - wrong password for this user?")
        return 2
    except OSError as err:
        print(f"CONNECT FAILED - {err}")
        return 3

    print(f"connected to {USER}@{HOST}:{PORT}\n")
    for label, cmd in PROBES:
        print(f"--- {label} ---")
        _, out, err = client.exec_command(cmd, timeout=30)
        text = (out.read() or b"").decode("utf-8", "replace").strip()
        e = (err.read() or b"").decode("utf-8", "replace").strip()
        print(text if text else (f"(no output) {e}" if e else "(no output)"))
        print()
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())