"""
Talk to the ECU-30 debug UART over a USB-TTL adapter.

The board's debug port is a ~1.8 V domain (measured 1.7 V). That matters for
wiring, not for this script -- but see WARNINGS below.

Reads console output to logs/, and can type commands into the console.

Examples
    python tools/uart_console.py --list
    python tools/uart_console.py --port COM5 --capture 30
    python tools/uart_console.py --port COM5 --sweep          # try common bauds
    python tools/uart_console.py --port COM5 --send "adb tcpip 5555"
"""

import argparse
import sys
import time
from pathlib import Path

import serial
from serial.tools import list_ports

# SMDK Exynos debug UARTs are normally 115200 8N1; the rest are cheap to try.
BAUDS = (115200, 230400, 38400, 57600, 9600, 921600)
LOGDIR = Path(__file__).resolve().parent.parent / "logs"

WARNINGS = """
WIRING (cross TX and RX, and mind the logic level)
  adapter TX  -> board RX
  adapter RX  -> board TX
  adapter GND -> board GND
  adapter VCC -> leave UNCONNECTED unless you intend to power the board

  The board's UART runs at ~1.8 V. A 3.3 V adapter's TX into a 1.8 V input is
  above VDD+0.3 V and can stress the SoC. Either use a 1.8 V adapter, or fit a
  divider on the adapter's TX: 3.3k from TX to the junction, 4.7k from the
  junction to GND gives ~1.9 V. Reading is the safe direction: the board's 1.7 V
  TX into a 3.3 V adapter input is usually fine.
"""


def list_ports_action() -> int:
    """Print every COM port the OS knows about."""
    ports = list(list_ports.comports())
    if not ports:
        print("No COM ports found. Plug in the USB-TTL adapter.")
        return 1
    for p in ports:
        print(f"{p.device:<8} {p.description}  [{p.hwid}]")
    return 0


def capture(port: str, baud: int, seconds: float, echo: bool = True) -> int:
    """Read console output for `seconds`, printing and saving it.

    Returns a process exit code: 0 if anything was received, 1 if silent.
    """
    LOGDIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    log = LOGDIR / f"uart-{port}-{baud}-{stamp}.log"
    deadline = time.monotonic() + seconds
    received = 0

    with serial.Serial(port, baud, timeout=0.2) as ser, log.open("wb") as fh:
        # PL2303 clones (incl. counterfeits) will not RECEIVE unless DTR is
        # asserted; PuTTY does this by default, so we must too or we see 0 bytes.
        ser.dtr = True
        ser.rts = True
        print(f"Capturing {port} @ {baud} for {seconds:g}s -> {log}")
        while time.monotonic() < deadline:
            chunk = ser.read(256)
            if not chunk:
                continue
            received += len(chunk)
            fh.write(chunk)
            if echo:
                sys.stdout.write(chunk.decode("utf-8", "replace"))
                sys.stdout.flush()

    print(f"\n{received} bytes -> {log}")
    return 0 if received else 1


def sweep(port: str, seconds: float) -> int:
    """Try each candidate baud for `seconds` and report which one talks."""
    for baud in BAUDS:
        print(f"\n--- {port} @ {baud} ---")
        if capture(port, baud, seconds) == 0:
            print(f"  ^^ THIS ONE IS TALKING: {port} @ {baud}")
            return 0
    print("\nNothing on any baud. Check TX/RX are crossed and GND is shared.")
    return 1


def send(port: str, baud: int, text: str, settle: float) -> int:
    """Type `text` into the console, then capture the reply."""
    with serial.Serial(port, baud, timeout=0.2) as ser:
        ser.dtr = True
        ser.rts = True
        ser.write(text.encode() + b"\r")
        ser.flush()
    print(f"Sent: {text}")
    time.sleep(settle)
    return capture(port, baud, settle)


def main(argv=None) -> int:
    """Command-line entry point."""
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog=WARNINGS,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--list", action="store_true", help="list COM ports and exit")
    ap.add_argument("--port", help="COM port, e.g. COM5")
    ap.add_argument("--baud", type=int, default=115200, help="baud rate (default 115200)")
    ap.add_argument("--capture", type=float, metavar="SEC", help="capture for SEC seconds")
    ap.add_argument("--sweep", action="store_true", help="try common baud rates")
    ap.add_argument("--send", metavar="TEXT", help="type TEXT into the console, then capture")
    args = ap.parse_args(argv)

    if args.list or not args.port:
        list_ports_action()
        if not args.port:
            print("\nPass --port to talk to the board.")
        return 0 if args.list else 1

    if args.sweep:
        return sweep(args.port, args.capture or 5.0)
    if args.send:
        return send(args.port, args.baud, args.send, args.capture or 6.0)
    return capture(args.port, args.baud, args.capture or 30.0)


if __name__ == "__main__":
    raise SystemExit(main())