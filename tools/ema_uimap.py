#!/usr/bin/env python
# UI-FRAME MAP TEST: every action the desktop buttons need, in sequence.
# Hypothesis-driven two-frame recipe for OUT2-close:
#   prep:  55 0a 03 01 <a1> 01 00 00 01 00   (no-op writes; sets echo b9=00)
#   close: 55 0a 03 01 00 00 00 00 00 01     (b8=00 close; accepted when echo b9=00)
# Everything else: single full-state frame, b8=b9=01.
# Start: both outputs open (01,01). LED expectations noted per step.
import serial, time

def mk(h): return bytearray(int(x,16) for x in h.split())
s = serial.Serial("/dev/ttySAC0", 115200, timeout=1)
time.sleep(0.3); s.flushInput()

def status():
    s.write(mk("55 04 01 00")); time.sleep(0.4)
    if s.inWaiting(): s.read(s.inWaiting())
    time.sleep(0.2)
    s.write(mk("55 04 01 01")); time.sleep(0.6)
    d = s.read(s.inWaiting()) if s.inWaiting() else ""
    h = " ".join("%02x"%b for b in bytearray(d))
    i = h.find("55 0a 03 00")
    if i>=0:
        f = h[i:i+29].split()
        if len(f)==10: return f[4],f[5]
    return ("?","?")

def send(frame, secs):
    t0=time.time(); n=0; acks={}
    while time.time()-t0 < secs:
        s.write(frame); n+=1; time.sleep(0.5)
        if s.inWaiting():
            hx=" ".join("%02x"%b for b in bytearray(s.read(s.inWaiting())))
            acks[hx]=acks.get(hx,0)+1
    return n, acks

def step(tag, frames, expect, note=""):
    print("@@ %s  expect (OUT1,OUT2)=(%s,%s) %s" % (tag, expect[0], expect[1], note))
    total_n = 0; allacks = {}
    for fr in frames:
        n, acks = send(fr, 4)
        total_n += n
        for k,v in acks.items(): allacks[k] = allacks.get(k,0)+v
    st = status()
    ok = st == expect
    print("   STATUS OUT1=%s OUT2=%s -> %s  TX=%d ACKs=%s" %
          (st[0], st[1], "PASS" if ok else "FAIL", total_n,
           allacks if allacks else "none"))
    return ok

results = []
a = status()
print("@@ START OUT1=%s OUT2=%s" % a)
if a != ("01","01"):
    print("!! expected both open to start; aborting"); s.close(); raise SystemExit(1)

# OUT2 close via recipe (a1=01 here)
results.append(("OUT2 ON recipe", step("1 OUT2 ON  (recipe)", [
    mk("55 0a 03 01 01 01 00 00 01 00"),   # prep, echo->b9=00
    mk("55 0a 03 01 00 00 00 00 00 01")],  # close OUT2
    ("01","00"), "[LED2 lit]")))

# OUT2 open, single full-state frame
results.append(("OUT2 OFF single", step("2 OUT2 OFF (single)", [
    mk("55 0a 03 01 01 01 00 00 01 01")],
    ("01","01"), "[LED2 dark]")))

# OUT2 close recipe again (repeatability)
results.append(("OUT2 ON recipe2", step("3 OUT2 ON  (recipe again)", [
    mk("55 0a 03 01 01 01 00 00 01 00"),
    mk("55 0a 03 01 00 00 00 00 00 01")],
    ("01","00"), "[LED2 lit]")))

# OUT1 toggle while OUT2 closed (full-state, b4 changes -> accepted)
results.append(("OUT1 ON /OUT2on", step("4 OUT1 ON  (OUT2 on)", [
    mk("55 0a 03 01 00 00 00 00 01 01")],
    ("00","00"), "[LED1 lit, LED2 lit]")))
results.append(("OUT1 OFF/OUT2on", step("5 OUT1 OFF (OUT2 on)", [
    mk("55 0a 03 01 01 00 00 00 01 01")],
    ("01","00"), "[LED1 dark, LED2 lit]")))

# OUT2 open with OUT1 closed state preserved (b4=a1=01 here)
results.append(("OUT2 OFF single2", step("6 OUT2 OFF (single)", [
    mk("55 0a 03 01 01 01 00 00 01 01")],
    ("01","01"), "[LED2 dark]")))

# OUT1 toggle with both open
results.append(("OUT1 ON  open", step("7 OUT1 ON  (both open)", [
    mk("55 0a 03 01 00 01 00 00 01 01")],
    ("00","01"), "[LED1 lit]")))
results.append(("OUT1 OFF open", step("8 OUT1 OFF (both open)", [
    mk("55 0a 03 01 01 01 00 00 01 01")],
    ("01","01"), "[LED1 dark]")))

st = status()
print("@@ FINAL OUT1=%s OUT2=%s" % st)
print("@@ SUMMARY: " + ", ".join("%s=%s" % (t,"PASS" if r else "FAIL") for t,r in results))
s.write(mk("55 04 01 00")); time.sleep(0.5); s.close()
print("@@DONE")
