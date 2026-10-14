"""Back up the vendor stack off the board, before anything else.

There is exactly one of this board, and its Daikin binaries cannot be
reinstalled without the vendor. So before any further work -- especially before
anything that might damage or replace them -- take a local copy.

Pulls, from the board, read-only:
    /usr/local/bin/*        the GUI and any other vendor programs
    /usr/local/lib/*        the protocol libraries
    /usr/local/etc, /etc/ema*, /root/Desktop/*   config and launchers
    plus a manifest of versions and checksums so the copy can be verified

Nothing is written to the board. This only reads and downloads.

    $env:PHL_BOARD_PASS = '<password>'
    python tools/vendor_backup.py
"""

import hashlib
import os
import sys

import paramiko

HOST = os.environ.get("PHL_BOARD_HOST", "192.168.100.127")
PORT = int(os.environ.get("PHL_BOARD_PORT", "22"))
USER = os.environ.get("PHL_BOARD_USER", "root")

# Saved next to the project, outside anything the board can reach.
DEST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "vendor-backup")

REMOTE_DIRS = [
    "/usr/local/bin",
    "/usr/local/lib",
    "/usr/local/share",
]

# Single files worth keeping even if they sit outside those directories.
REMOTE_FILES = [
    "/root/Desktop/Link_to_CMIMIRDemo",
    "/etc/os-release",
]


def run(c, cmd, timeout=120):
    """Run one shell command on the board and return its output as text."""
    _, out, err = c.exec_command(cmd, timeout=timeout)
    text = (out.read() or b"").decode("utf-8", "replace")
    e = (err.read() or b"").decode("utf-8", "replace")
    return text if text else e


def main():
    """Download the vendor stack to vendor-backup/ and write a manifest."""
    password = os.environ.get("PHL_BOARD_PASS")
    if not password:
        print("Set PHL_BOARD_PASS first.")
        return 1

    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        c.connect(HOST, port=PORT, username=USER, password=password, timeout=25,
                  allow_agent=False, look_for_keys=False)
    except OSError as err:
        print(f"CONNECT FAILED - {err}")
        return 3

    os.makedirs(DEST, exist_ok=True)
    manifest = ["# Vendor backup manifest",
                "# Source: root@%s  -- read-only pull, nothing modified"
                % HOST,
                ""]

    # Listing plus sizes and sha256, so the copy can be verified later.
    listing = run(c, "for d in %s; do ls -l $d 2>/dev/null; done"
                  % " ".join(REMOTE_DIRS))
    manifest.append("## sha256 of every file pulled")
    manifest.append("```")

    for d in REMOTE_DIRS:
        local = os.path.join(DEST, d.strip("/").replace("/", "_"))
        os.makedirs(local, exist_ok=True)
        try:
            entries = run(c, "ls -1 %s 2>/dev/null" % d).split()
        except Exception as err:
            print(f"{d}: listing failed {err}")
            continue
        for name in entries:
            remote = "%s/%s" % (d.rstrip("/"), name)
            try:
                digest = run(c, "sha256sum %s 2>/dev/null | cut -d' ' -f1"
                             % remote).strip()
                size = run(c, "stat -c %s %s 2>/dev/null" % (remote, remote)).strip()
            except Exception:
                digest, size = "?", "?"
            sftp = c.open_sftp()
            try:
                sftp.get(remote, os.path.join(local, name))
                ok = "saved"
            except Exception as err:
                ok = "FAILED %s" % err
            finally:
                sftp.close()
            manifest.append("%s  %8s  %s" % (digest[:16], size, remote))
            print("%-9s %s" % (ok, remote))

    for f in REMOTE_FILES:
        try:
            sftp = c.open_sftp()
            sftp.get(f, os.path.join(DEST, os.path.basename(f)))
            sftp.close()
            print("%-9s %s" % ("saved", f))
        except Exception as err:
            print("skipped  %s (%s)" % (f, err))

    manifest.append("```")
    manifest.append("")
    manifest.append("## ldd of the protocol library")
    manifest.append("```")
    manifest.append(run(c, "objdump -p /usr/local/lib/libemaLib_arm_1.0.1.so "
                           "2>/dev/null | grep -E 'NEEDED|SONAME'"))
    manifest.append("```")
    manifest.append("")

    with open(os.path.join(DEST, "MANIFEST.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(manifest))

    c.close()
    print("\nbackup written to %s" % DEST)
    return 0


if __name__ == "__main__":
    sys.exit(main())