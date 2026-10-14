#!/usr/bin/env python2
"""Live indicator UI for the board's digital inputs (IN1 / IN2).

Shows two indicator lamps on the board's desktop, one per input, driven by real
traffic from the STM8S207. Bridge an input to GND and its lamp lights.

What it reads, and how it was established (see docs/BOARD.md):

    port   /dev/ttySAC0 @ 115200 8N1
    frame  55 0a 03 00 01 01 BB RR 00 00
                      BB byte 6 = IN1, RR byte 7 = IN2
    both inputs are ACTIVE LOW: 00 = bridged/asserted, 01 = open

The STM8 answers one open with one status frame then goes quiet, so the reader
cycles close/open to keep it talking. Serial work happens on a background
thread; the Qt main loop stays responsive.

READ-ONLY: it transmits only the vendor handshake frames 55 04 01 01 (open) and
55 04 01 00 (close). It never sends an actuator command.

Runs on the board:

    DISPLAY=:0 python2 ema_ui.py
"""

import sys
import threading
import time

import serial

from PyQt4 import QtCore, QtGui

PORT = "/dev/ttySAC0"
BAUD = 115200
SOF = 0x55

FRAME_OPEN = "\x55\x04\x01\x01"
FRAME_CLOSE = "\x55\x04\x01\x00"

# Relay control. Class 04 is the actuator command: 55 | 05 | 04 | sel | state.
# Byte 3 selects the device, byte 4 is the state. sel=1 is the relay -- found by
# disassembling CMIMIRDemo and then confirmed on the hardware, where it moved
# the relay while leaving OUT1 and OUT2 untouched.
FRAME_RELAY_ON = "\x55\x05\x04\x01\x01"
FRAME_RELAY_OFF = "\x55\x05\x04\x01\x00"
RELAY_SELECTOR = 1


def hexs(data):
    """Render bytes as spaced hex."""
    return " ".join("%02x" % ord(b) for b in data)


class Parser(object):
    """Resyncs on 0x55 and splits the stream into length-delimited frames."""

    def __init__(self):
        self.buf = ""

    def feed(self, chunk):
        """Add received data and return every complete frame it revealed."""
        self.buf += chunk
        frames = []
        start_byte = chr(SOF)
        while True:
            if start_byte not in self.buf:
                self.buf = ""
                break
            start = self.buf.index(start_byte)
            if start:
                self.buf = self.buf[start:]
            if len(self.buf) < 2:
                break
            length = ord(self.buf[1])
            if length < 2 or length > 64:
                self.buf = self.buf[1:]
                continue
            if len(self.buf) < length:
                break
            frames.append(self.buf[:length])
            self.buf = self.buf[length:]
        return frames


class Reader(threading.Thread):
    """Background serial reader; pushes status frames into a shared queue.

    Runs forever so the UI can be closed and reopened without re-implementing
    the link. Any serial error is reported and retried, because a transient UART
    hiccup should not require restarting the app.
    """

    def __init__(self, inbox, outbox):
        threading.Thread.__init__(self)
        self.daemon = True
        self.inbox = inbox          # queue.Queue of dicts -> the UI
        self.outbox = outbox        # queue.Queue of bytes  -> the serial line
        self._stop = False
        self.ser = None

    def stop(self):
        """Ask the reader loop to finish at the next opportunity."""
        self._stop = True

    def _drain_commands(self):
        """Send any relay command the UI has queued. Returns True if one went."""
        sent = False
        try:
            while True:
                data = self.outbox.get_nowait()
                if data and self.ser:
                    self.ser.write(data)
                    self.ser.flush()
                    sent = True
        except Exception:
            pass          # queue empty, or python2 Queue import naming
        return sent

    def run(self):
        """Cycle open/collect/close forever, queueing frames to the UI."""
        parser = Parser()
        while not self._stop:
            try:
                if self.ser is None or not self.ser.isOpen():
                    self.ser = serial.Serial(PORT, BAUD, timeout=0.2)
                self.ser.write(FRAME_OPEN)
                self.ser.flush()
                end = time.time() + 1.5
                while time.time() < end and not self._stop:
                    # Relay commands go out promptly, not at the next cycle.
                    self._drain_commands()
                    chunk = self.ser.read(64)
                    if not chunk:
                        continue
                    for f in parser.feed(chunk):
                        n = len(f)
                        if n == 10:
                            self.inbox.put({"hex": hexs(f),
                                            "in1": ord(f[6]),
                                            "in2": ord(f[7])})
                        elif n == 5 and ord(f[2]) == 4 \
                                and ord(f[3]) == RELAY_SELECTOR:
                            # The STM8 echoes class-04 frames back, so the
                            # echo is the authoritative relay state.
                            self.inbox.put({"hex": hexs(f),
                                            "relay": ord(f[4])})
                self._drain_commands()
                self.ser.write(FRAME_CLOSE)
                self.ser.flush()
                time.sleep(0.2)
            except Exception as err:
                self.inbox.put({"error": str(err)})
                try:
                    if self.ser:
                        self.ser.close()
                except Exception:
                    pass
                self.ser = None
                time.sleep(2)


class Lamp(QtGui.QWidget):
    """A round indicator lamp: dark when the input is open, lit when bridged."""

    def __init__(self, title, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.title = title
        self.on = False
        self.setMinimumSize(150, 190)

    def set_on(self, on):
        """Light or dim the lamp and repaint."""
        if on != self.on:
            self.on = on
            self.update()

    def paintEvent(self, event):
        """Draw the lamp face and its label."""
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0 - 10
        r = min(w, h - 40) / 2.0 - 10

        if self.on:
            outer = QtGui.QColor(90, 230, 120)
            inner = QtGui.QColor(205, 255, 218)
            text_col = QtGui.QColor(20, 90, 40)
        else:
            outer = QtGui.QColor(70, 74, 78)
            inner = QtGui.QColor(40, 43, 46)
            text_col = QtGui.QColor(190, 195, 200)

        p.setPen(QtGui.QPen(outer.darker(140), 3))
        p.setBrush(QtGui.QBrush(outer))
        p.drawEllipse(QtCore.QRectF(cx - r, cy - r, 2 * r, 2 * r))

        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 90), 2))
        p.setBrush(QtGui.QBrush(inner))
        p.drawEllipse(QtCore.QRectF(cx - r * 0.62, cy - r * 0.62,
                                    r * 1.24, r * 1.24))

        f = p.font()
        f.setPointSize(17)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QtGui.QColor(255, 255, 255))
        p.drawText(QtCore.QRectF(0, cy + r * 0.16, w, 32),
                   QtCore.Qt.AlignCenter, "ON" if self.on else "off")

        f2 = p.font()
        f2.setPointSize(14)
        f2.setBold(True)
        p.setFont(f2)
        p.setPen(text_col)
        p.drawText(QtCore.QRectF(0, h - 32, w, 26), QtCore.Qt.AlignCenter,
                   self.title)


class Window(QtGui.QMainWindow):
    """The app window: two lamps, a hex readout, and a link status line."""

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Daikin CMIMIR - digital inputs (STM8S207)")
        self.resize(470, 400)

        self.lamp1 = Lamp("IN1")
        self.lamp2 = Lamp("IN2")

        self.hexlabel = QtGui.QLabel("-")
        self.hexlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.hexlabel.setFont(QtGui.QFont("Monospace", 10))

        self.countlabel = QtGui.QLabel("frames: 0")
        self.countlabel.setAlignment(QtCore.Qt.AlignCenter)

        self.linklabel = QtGui.QLabel("link: starting...")
        self.linklabel.setAlignment(QtCore.Qt.AlignCenter)

        # Relay control. The button state is driven by the STM8's own echo of
        # the command, not by the click, so the display reflects what the MCU
        # actually did rather than what we asked for.
        self.relay_on = False
        self.relaybtn = QtGui.QPushButton("RELAY: OFF")
        self.relaybtn.setCheckable(True)
        self.relaybtn.setMinimumHeight(52)
        self.relaybtn.setStyleSheet(
            "QPushButton { font-size: 15pt; font-weight: bold; background: #4a4e52;"
            " color: white; border: 2px solid #666; border-radius: 6px; }"
            "QPushButton:checked { background: #2f9e44; border: 2px solid #7ee2a0; }")
        self.relaybtn.toggled.connect(self.relay_toggled)
        self.relayhint = QtGui.QLabel("click to switch the relay")
        self.relayhint.setAlignment(QtCore.Qt.AlignCenter)

        lamps = QtGui.QHBoxLayout()
        lamps.addWidget(self.lamp1)
        lamps.addWidget(self.lamp2)

        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        v = QtGui.QVBoxLayout(frame)
        v.addLayout(lamps)
        v.addWidget(self.relaybtn)
        v.addWidget(self.relayhint)
        v.addWidget(self.hexlabel)
        v.addWidget(self.countlabel)
        v.addWidget(self.linklabel)

        holder = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(holder)
        head = QtGui.QLabel("Bridge an input to GND to light its lamp")
        head.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(head)
        layout.addWidget(frame, 1)

        self.setCentralWidget(holder)
        self.statusBar().showMessage(
            "%s @ %d 8N1  -  read-only, sends open/close only" % (PORT, BAUD))

    def relay_toggled(self, checked):
        """Queue a relay command. Does not change the display by itself --
        the echo from the STM8 does that, via update_relay()."""
        self.pending_relay = checked
        if self.outbox is not None:
            self.outbox.put(FRAME_RELAY_ON if checked else FRAME_RELAY_OFF)
            self.relayhint.setText("command sent, waiting for the board to echo")
        self.relaybtn.blockSignals(True)
        self.relaybtn.setChecked(self.relay_on)
        self.relaybtn.blockSignals(False)

    def update_relay(self, state):
        """Show the relay state the STM8 echoed back, not what we asked for."""
        if state == self.relay_on:
            return
        self.relay_on = state
        self.relaybtn.blockSignals(True)
        self.relaybtn.setChecked(state)
        self.relaybtn.setText("RELAY: ON" if state else "RELAY: OFF")
        self.relaybtn.blockSignals(False)
        self.relayhint.setText("board confirmed" if self.pending_relay == state
                               else "board reported the opposite")

    def update_state(self, msg, count, error):
        """Apply one decoded status frame, or an error, to the display."""
        if error:
            self.linklabel.setText("link: %s" % error)
            self.lamp1.set_on(False)
            self.lamp2.set_on(False)
            return

        # Active low: byte 00 means bridged, so the lamp lights when it is 0.
        self.lamp1.set_on(msg["in1"] == 0)
        self.lamp2.set_on(msg["in2"] == 0)
        self.hexlabel.setText(msg["hex"])
        self.countlabel.setText("frames: %d" % count)
        self.linklabel.setText("link: LIVE  (/dev/ttySAC0)")


def main():
    """Start the reader thread, then run the Qt event loop."""
    try:
        import Queue
    except ImportError:
        import queue as Queue

    inbox = Queue.Queue()
    outbox = Queue.Queue()
    reader = Reader(inbox, outbox)
    reader.start()

    app = QtGui.QApplication(sys.argv)
    win = Window()
    win.outbox = outbox
    win.pending_relay = False

    state = {"count": 0}

    def pump():
        """Drain the reader queue into the UI without blocking the event loop."""
        try:
            while True:
                msg = inbox.get_nowait()
                if "error" in msg:
                    win.update_state(None, state["count"], msg["error"])
                elif "relay" in msg:
                    win.update_relay(msg["relay"])
                else:
                    state["count"] += 1
                    win.update_state(msg, state["count"], None)
        except Queue.Empty:
            pass

    timer = QtCore.QTimer()
    timer.timeout.connect(pump)
    timer.start(100)

    win.show()
    rc = app.exec_()
    reader.stop()
    return rc


if __name__ == "__main__":
    sys.exit(main())
