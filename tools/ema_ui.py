#!/usr/bin/env python2
"""Live digital I/O UI for the board (STM8S207): IN1/IN2 lamps, OUT1/OUT2
lamps + buttons, a relay button, and a Wiegand W-OUT test row.

Link: /dev/ttySAC0 @ 115200 8N1.

Other board connectors, none of which go through the STM8 and none of which
need frames - the window shows them as a static reference line:
    RS232 = /dev/ttySAC3   proved by a TX/RX loopback jumper (rs232_loopback.py)
    RS485 = /dev/ttySAC2   proved by a differential measurement with a control
                           run, idle 0.646 V -> ~220 mV while transmitting
                           (rs485_probe.py). TX only; RX never tested.

Status frame (10 bytes): 55 0a 03 00 | b4 b5 | b6 b7 | b8 b9
    b4/b5  raw contact OUT1/OUT2  (00 = shorted to GND = ON, 01 = open)
    b6/b7  IN1/IN2               (active low: 00 = bridged)
    b8/b9  echo of the last request's mask bytes

Class-03 request acks (10 bytes, byte3=01) repeat the ACTUAL b4/b5 contacts,
so an output command is confirmed within the same read window; status frames
(byte3=00) also carry the inputs. The display always follows the board.

GPO writes -- every frame masks BOTH channels (b8=b9=01), verified in all four
OUT1/OUT2 state combinations (16/16 hardware tests, see docs/BOARD.md):
    OUT1 toggle  55 0a 03 01 <d1> <d2> 00 00 01 01    b4/b5 = desired states
    OUT2 open    55 0a 03 01 <a1> 01 00 00 01 01
    OUT2 close   TWO frames:  55 0a 03 01 <a1> 01 00 00 01 00   (prep)
                             then 55 0a 03 01 00 00 00 00 00 01  (close)
    The prep frame is mandatory: an OUT2 close with OUT1 unchanged and no
    prior b9=00 in the echo register is SILENTLY refused by the STM8
    (no ack, no action). Relay: class 04, 55 05 04 01 <state>.

Because refusal is silent, a click alone proves nothing: commands are retried
up to 3x until an ack/status confirms them, or the hint says the board did
not respond.

The STM8 answers one open with one status frame then goes quiet, so the reader
cycles close/open to keep it talking. Serial work runs on a background thread;
the Qt main loop stays responsive.

SEND WIEGAND drives W-OUT for real: it runs the proven sender /root/ema_wsend
(tools/ema_wsend.cpp) as a subprocess with the port/bits/card/count/gap from
the widgets. That binary needs /dev/ttySAC0 to itself, so the reader thread is
paused first -- it finishes the current cycle, writes CLOSE, closes the tty
and parks; polling and the lamps freeze during the send, then restart by
themselves. The STM8 echoes every frame it accepts, so a clean run = "OK" in
the hint, and the LEDs on W-OUT flash with every card.
"""

import subprocess
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

# The proven Wiegand sender, compiled on the board from tools/ema_wsend.cpp.
# Lives in /root next to the shims because it is a board-side binary, not repo
# content; rebuild instructions are in that file's header comment.
WSEND = "/root/ema_wsend"


# --- GPO write frames -------------------------------------------------------
# All verified against the hardware in every OUT1/OUT2 state combination
# (ema_uimap.py 8/8 + ema_gap.py 4/4 PASS). b4/b5 = desired OUT1/OUT2 contact
# state (00=close, 01=open); b8/b9 = per-channel mask. Frames always mask both
# channels: single-mask variants were observed being silently refused.

def frame_out1(desired_on, out2_on):
    """Frame that sets OUT1 to desired_on while preserving OUT2's state."""
    b4 = 0x00 if desired_on else 0x01
    b5 = 0x00 if out2_on else 0x01
    return "\x55\x0a\x03\x01" + chr(b4) + chr(b5) + "\x00\x00\x01\x01"


def frame_out2_prep(a1_on):
    """Primes the STM8's echo register (b9=00) so the close frame is accepted.
    Changes nothing: rewrites OUT1 as-it-is and OUT2 as open (a no-op while
    OUT2 is still open). Skipping this is why early OUT2-close attempts
    failed with zero acks."""
    b4 = 0x00 if a1_on else 0x01
    return "\x55\x0a\x03\x01" + chr(b4) + "\x01\x00\x00\x01\x00"


FRAME_OUT2_CLOSE = "\x55\x0a\x03\x01\x00\x00\x00\x00\x00\x01"


def frame_out2_open(a1_on):
    """Frame that opens OUT2 while preserving OUT1 (b4 = OUT1's true state)."""
    b4 = 0x00 if a1_on else 0x01
    return "\x55\x0a\x03\x01" + chr(b4) + "\x01\x00\x00\x01\x01"


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
        self._pause = False         # a Wiegand send wants the port released
        self._parked = False        # ack: tty closed, loop parked, safe to open
        self.ser = None

    def stop(self):
        """Ask the reader loop to finish at the next opportunity."""
        self._stop = True

    def pause(self):
        """Finish the current cycle, close the tty and park the loop.
        Needed because ema_wsend opens /dev/ttySAC0 by itself."""
        self._pause = True

    def resume(self):
        """Un-park: the loop reopens the tty on its next pass."""
        self._pause = False

    def is_parked(self):
        """True once the tty is actually released (safe for another opener)."""
        return self._parked

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
            if self._pause:
                # Park for a Wiegand send: release the tty FIRST, then ack --
                # the sender must only proceed once the port is really free.
                try:
                    if self.ser and self.ser.isOpen():
                        self.ser.close()
                except Exception:
                    pass
                self.ser = None
                self._parked = True
                time.sleep(0.1)
                continue
            self._parked = False
            try:
                if self.ser is None or not self.ser.isOpen():
                    self.ser = serial.Serial(PORT, BAUD, timeout=0.2)
                self.ser.write(FRAME_OPEN)
                self.ser.flush()
                end = time.time() + 1.5
                while time.time() < end and not self._stop \
                        and not self._pause:
                    # Relay commands go out promptly, not at the next cycle.
                    self._drain_commands()
                    chunk = self.ser.read(64)
                    if not chunk:
                        continue
                    for f in parser.feed(chunk):
                        n = len(f)
                        if n == 10:
                            # Status (byte3=00) and class-03 request acks
                            # (byte3=01) both report actual OUT1/OUT2 at
                            # bytes 4/5; only status carries the inputs.
                            msg = {"hex": hexs(f),
                                   "out1": ord(f[4]),
                                   "out2": ord(f[5])}
                            if ord(f[3]) == 0:
                                msg["in1"] = ord(f[6])
                                msg["in2"] = ord(f[7])
                            self.inbox.put(msg)
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
        self.setWindowTitle("EMA_Controls - Daikin CMIMIR I/O (STM8S207)")
        self.resize(700, 640)

        self.lamp1 = Lamp("IN1")
        self.lamp2 = Lamp("IN2")
        self.lamp3 = Lamp("OUT1")
        self.lamp4 = Lamp("OUT2")

        self.outbox = None
        self.inbox = None           # set by main()
        self.reader = None          # set by main(); parked before a send
        self.pending_relay = False
        self.out1_on = False
        self.out2_on = False
        self.pending_out = None      # (which, desired_on) while unconfirmed
        self.out_sent_at = 0.0
        self.out_retries = 0

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

        # Output buttons. Same contract as the relay: the button shows the
        # contact state the BOARD reports (status/ack bytes 4/5), never the
        # click itself -- refusals from the STM8 are silent.
        btn_style = ("QPushButton { font-size: 14pt; font-weight: bold;"
                     " background: #4a4e52; color: white;"
                     " border: 2px solid #666; border-radius: 6px; }"
                     "QPushButton:checked { background: #2f9e44;"
                     " border: 2px solid #7ee2a0; }")
        self.out1btn = QtGui.QPushButton("OUT1: OFF")
        self.out1btn.setCheckable(True)
        self.out1btn.setMinimumHeight(48)
        self.out1btn.setStyleSheet(btn_style)
        self.out2btn = QtGui.QPushButton("OUT2: OFF")
        self.out2btn.setCheckable(True)
        self.out2btn.setMinimumHeight(48)
        self.out2btn.setStyleSheet(btn_style)
        self.out1btn.toggled.connect(lambda c: self.out_toggled(1, c))
        self.out2btn.toggled.connect(lambda c: self.out_toggled(2, c))
        self.outhint = QtGui.QLabel("click to switch an output")
        self.outhint.setAlignment(QtCore.Qt.AlignCenter)

        # Wiegand test row -- sends real frames on W-OUT via /root/ema_wsend.
        # The card is a hex number (big-endian, MSB first) up to 32 bits; the
        # STM8 does NOT recompute parity, so include it in the value yourself.
        wg = QtGui.QHBoxLayout()
        wg.addWidget(QtGui.QLabel("port"))
        self.wport = QtGui.QComboBox()
        self.wport.addItems(["1", "2"])
        self.wport.setCurrentIndex(1)       # W-OUT2 = the bench-verified header
        wg.addWidget(self.wport)
        wg.addWidget(QtGui.QLabel("bits"))
        self.wbits = QtGui.QSpinBox()
        self.wbits.setRange(1, 32)
        self.wbits.setValue(24)
        wg.addWidget(self.wbits)
        wg.addWidget(QtGui.QLabel("card"))
        self.wcard = QtGui.QLineEdit("AAAAAA")
        self.wcard.setMaximumWidth(90)
        self.wcard.setInputMask("HHHHHHHH")   # 8 hex digits max, blanks ignored
        wg.addWidget(self.wcard)
        wg.addWidget(QtGui.QLabel("count"))
        self.wcount = QtGui.QSpinBox()
        self.wcount.setRange(1, 100000)
        self.wcount.setValue(30)
        wg.addWidget(self.wcount)
        wg.addWidget(QtGui.QLabel("gap ms"))
        self.wgap = QtGui.QSpinBox()
        self.wgap.setRange(1, 60000)
        self.wgap.setValue(700)
        wg.addWidget(self.wgap)
        self.wbtn = QtGui.QPushButton("SEND WIEGAND")
        self.wbtn.clicked.connect(self.send_wiegand)
        wg.addWidget(self.wbtn)
        self.whint = QtGui.QLabel(
            "watch the LEDs on W-OUT: one burst per card")
        self.whint.setAlignment(QtCore.Qt.AlignCenter)

        outs = QtGui.QHBoxLayout()
        outs.addWidget(self.out1btn)
        outs.addWidget(self.out2btn)

        lamps = QtGui.QHBoxLayout()
        lamps.addWidget(self.lamp1)
        lamps.addWidget(self.lamp2)
        lamps.addWidget(self.lamp3)
        lamps.addWidget(self.lamp4)

        frame = QtGui.QFrame()
        frame.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        v = QtGui.QVBoxLayout(frame)
        v.addLayout(lamps)
        v.addLayout(outs)
        v.addWidget(self.outhint)
        v.addWidget(self.relaybtn)
        v.addWidget(self.relayhint)
        v.addLayout(wg)
        v.addWidget(self.whint)
        v.addWidget(self.hexlabel)
        v.addWidget(self.countlabel)
        v.addWidget(self.linklabel)

        holder = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(holder)
        head = QtGui.QLabel("Bridge IN1/IN2 to GND - click OUT1/OUT2 or RELAY")
        head.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(head)

        # Static reference: which Linux device each connector is. RS232 was
        # proved by a TX-RX loopback (tools/rs232_loopback.py); RS485 by a
        # differential measurement with a control run (tools/rs485_probe.py).
        # Neither goes through the STM8, so neither needs protocol frames.
        ref = QtGui.QLabel(
            "reference:   RS232 = /dev/ttySAC3   |   "
            "RS485 = /dev/ttySAC2   |   STM8 = /dev/ttySAC0")
        ref.setAlignment(QtCore.Qt.AlignCenter)
        ref.setStyleSheet("color:#666; font-size:11px;")
        layout.addWidget(ref)

        layout.addWidget(frame, 1)

        self.setCentralWidget(holder)
        self.statusBar().showMessage(
            "%s @ %d 8N1  -  states shown are the board's, confirmed by ack"
            % (PORT, BAUD))

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

    def out_toggled(self, which, checked):
        """Queue an output command; the display is reverted until the board
        confirms via ack/status (update_out). Does not handle a dead link --
        retries simply time out into the hint text."""
        actual = self.out1_on if which == 1 else self.out2_on
        btn = self.out1btn if which == 1 else self.out2btn
        btn.blockSignals(True)
        btn.setChecked(actual)          # revert; board state wins
        btn.blockSignals(False)
        if checked == actual:
            return
        if self.pending_out is not None:
            self.outhint.setText("busy - waiting for the previous command")
            return
        if self.outbox is None:
            return
        self.pending_out = (which, checked)
        self.out_sent_at = time.time()
        self.out_retries = 0
        self._queue_out_frames(which, checked)
        self.outhint.setText("OUT%d %s sent, waiting for the board..."
                             % (which, "ON" if checked else "OFF"))

    def _queue_out_frames(self, which, desired_on):
        """Queue the hardware-verified frame(s) for one output action."""
        if which == 1:
            self.outbox.put(frame_out1(desired_on, self.out2_on))
        elif desired_on:
            # OUT2 close needs the two-frame recipe; a bare close frame is
            # silently refused unless the echo register holds b9=00.
            self.outbox.put(frame_out2_prep(self.out1_on))
            QtCore.QTimer.singleShot(
                600, lambda: self.outbox.put(FRAME_OUT2_CLOSE))
        else:
            self.outbox.put(frame_out2_open(self.out1_on))

    # --- Wiegand send -------------------------------------------------------
    # Driven from a worker thread because ema_wsend blocks for the whole run
    # (count * gap). The reader must be parked first -- it holds /dev/ttySAC0.

    def send_wiegand(self):
        """Validate the widgets, park the reader, then send in a worker thread.
        Does not touch serial directly; the result label is set on completion
        via show_wiegand()."""
        if self.reader is None or self.outbox is None:
            return
        card = str(self.wcard.text()).strip()
        if not card:
            self.whint.setText("card is empty")
            return
        args = [WSEND,
                str(self.wport.currentIndex() + 1),
                str(self.wbits.value()),
                card,
                str(self.wcount.value()),
                str(self.wgap.value())]
        self.wbtn.setEnabled(False)
        self.whint.setText("sending %s..." % card)
        threading.Thread(target=self._wiegand_worker,
                         args=(args,)).start()

    def _wiegand_worker(self, args):
        """Park the reader, run ema_wsend, post the result, resume the reader.
        Any serial error mid-send is caught and shown -- never crash the UI."""
        try:
            self.reader.pause()
            # Wait for the reader to finish its cycle and release the tty.
            end = time.time() + 8.0
            while time.time() < end and not self.reader.is_parked():
                time.sleep(0.05)
            proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            out = proc.communicate()[0]
            rc = proc.returncode
            self.inbox.put({"wiegand": self._wiegand_summary(out, rc)})
        except Exception as err:
            self.inbox.put({"wiegand": "error: %s" % err})
        finally:
            self.reader.resume()

    def _wiegand_summary(self, out, rc):
        """One-line verdict from ema_wsend's stdout. rc is 0 = clean,
        1 = refusals seen, 2 = bad args. Not a full parser -- just enough to
        say OK or name the first refusal."""
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        for l in lines:
            if "refused" in l:
                return "FAILED: %s" % l
        if rc == 0:
            tail = lines[-1] if lines else "?"
            return "OK - %d sent, 0 refusals (%s)" % (self.wcount.value(), tail)
        tail = " / ".join(lines[-2:]) if lines else "no output"
        return "FAILED rc=%d: %s" % (rc, tail)

    def show_wiegand(self, text):
        """Show the send verdict and re-enable the button (runs on Qt thread)."""
        self.whint.setText(text)
        self.wbtn.setEnabled(True)


    def check_retries(self):
        """Re-send an unconfirmed output command up to 3x. The STM8 has been
        observed silently refusing valid-looking frames, so a send alone is
        never treated as success. Called from the pump timer."""
        if self.pending_out is None:
            return
        if time.time() - self.out_sent_at < 3.0:
            return
        if self.out_retries < 3:
            self.out_retries += 1
            self.out_sent_at = time.time()
            self._queue_out_frames(*self.pending_out)
            self.outhint.setText("no confirmation, retry %d/3..."
                                 % self.out_retries)
        else:
            which = self.pending_out[0]
            self.pending_out = None
            self.outhint.setText("OUT%d: board did not respond - try again"
                                 % which)

    def update_out(self, out1_closed, out2_closed, hexframe=None):
        """Apply the contact state the BOARD reports (bytes 4/5, 00=ON).
        Clears a pending command when the report matches the ask."""
        self.out1_on = out1_closed
        self.out2_on = out2_closed
        for btn, on, name in ((self.out1btn, out1_closed, "OUT1"),
                              (self.out2btn, out2_closed, "OUT2")):
            btn.blockSignals(True)
            btn.setChecked(on)
            btn.setText("%s: %s" % (name, "ON" if on else "OFF"))
            btn.blockSignals(False)
        self.lamp3.set_on(out1_closed)
        self.lamp4.set_on(out2_closed)
        if hexframe:
            self.hexlabel.setText(hexframe)
        if self.pending_out is not None:
            which, desired = self.pending_out
            actual = out1_closed if which == 1 else out2_closed
            if actual == desired:
                self.pending_out = None
                self.outhint.setText("board confirmed OUT%d %s"
                                     % (which, "ON" if desired else "OFF"))

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
        # Outputs: 00 = contact shorted to GND = ON. update_out also settles
        # any pending click when the board's answer matches the ask.
        self.update_out(msg["out1"] == 0, msg["out2"] == 0, msg["hex"])
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
    win.inbox = inbox
    win.reader = reader

    state = {"count": 0}

    def pump():
        """Drain the reader queue into the UI without blocking the event loop."""
        try:
            while True:
                msg = inbox.get_nowait()
                if "error" in msg:
                    win.update_state(None, state["count"], msg["error"])
                elif "wiegand" in msg:
                    win.show_wiegand(msg["wiegand"])
                elif "relay" in msg:
                    win.update_relay(msg["relay"])
                elif "in1" in msg:
                    state["count"] += 1
                    win.update_state(msg, state["count"], None)
                elif "out1" in msg:
                    # class-03 request ack: actual OUT1/OUT2 contacts only
                    win.update_out(msg["out1"] == 0, msg["out2"] == 0,
                                   msg["hex"])
        except Queue.Empty:
            pass
        win.check_retries()

    timer = QtCore.QTimer()
    timer.timeout.connect(pump)
    timer.start(100)

    win.show()
    rc = app.exec_()
    reader.stop()
    return rc


if __name__ == "__main__":
    sys.exit(main())
