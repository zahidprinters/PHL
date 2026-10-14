"""Minimal SSH exec/SFTP helper for the ECU-30 board (dev/testing only).

Password comes from PHL_BOARD_PASS so it is never written to a file.

    $env:PHL_BOARD_PASS = '...'
    python temp/board_run.py --upload tools\\ema_wsend.cpp /root/ema_wsend.cpp
    python temp/board_run.py -- g++ --version
"""
import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
USER = os.environ.get("PHL_BOARD_USER", "root")


def main():
    args = sys.argv[1:]
    password = os.environ.get("PHL_BOARD_PASS")
    if not password:
        print("Set PHL_BOARD_PASS first.")
        return 1

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=password,
                   timeout=15, allow_agent=False, look_for_keys=False)

    rc = 0
    if args and args[0] == "--upload":
        local, remote = args[1], args[2]
        sftp = client.open_sftp()
        sftp.put(local, remote)
        sftp.close()
        print(f"uploaded {local} -> {remote}")
    elif args and args[0] == "--download":
        remote, local = args[1], args[2]
        sftp = client.open_sftp()
        sftp.get(remote, local)
        sftp.close()
        print(f"downloaded {remote} -> {local}")
    else:
        cmd = " ".join(args) if args else "id; hostname"
        # long-running ops (bulk dpkg removals) need more than the 120 s default
        exec_timeout = int(os.environ.get("PHL_BOARD_TIMEOUT", "120"))
        _, out, err = client.exec_command(cmd, timeout=exec_timeout)
        text = (out.read() or b"").decode("utf-8", "replace")
        etext = (err.read() or b"").decode("utf-8", "replace")
        code = out.channel.recv_exit_status()
        if text:
            sys.stdout.write(text)
        if etext:
            sys.stderr.write(etext)
        print(f"[exit {code}]")
        rc = code
    client.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
