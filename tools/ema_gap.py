#!/usr/bin/env python
# GAP TEST: OUT2 operations while OUT1 is CLOSED (a1=00) -- the only state
# combination the UI-frame map has not verified.
# Start (01,01) -> OUT1 ON -> (00,01) -> OUT2 recipe ON -> (00,00)
# -> OUT2 OFF with a1=00 -> (00,01) -> OUT1 OFF -> (01,01)
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

def step(tag, frames, expect):
    print("@@ %s expect (%s,%s)" % (tag, expect[0], expect[1]))
    total=0; acks={}
    for fr in frames:
        t0=time.time()
        while time.time()-t0 < 4:
            s.write(fr); total+=1; time.sleep(0.5)
            if s.inWaiting():
                hx=" ".join("%02x"%b for b in bytearray(s.read(s.inWaiting())))
                acks[hx]=acks.get(hx,0)+1
    st = status()
    ok = st == expect
    print("   STATUS OUT1=%s OUT2=%s -> %s TX=%d ACKs=%s" %
          (st[0],st[1],"PASS" if ok else "FAIL",total, acks if acks else "none"))
    return ok

r = []
a = status(); print("@@ START (%s,%s)" % a)
if a != ("01","01"):
    print("!! not both open, abort"); s.close(); raise SystemExit(1)

r.append(step("1 OUT1 ON", [mk("55 0a 03 01 00 01 00 00 01 01")], ("00","01")))
# OUT2 recipe with a1=00: prep b4=00,b5=01,b8=01,b9=00 then close
r.append(step("2 OUT2 ON recipe (a1=00)", [
    mk("55 0a 03 01 00 01 00 00 01 00"),
    mk("55 0a 03 01 00 00 00 00 00 01")], ("00","00")))
# OUT2 OFF with a1=00
r.append(step("3 OUT2 OFF (a1=00)", [mk("55 0a 03 01 00 01 00 00 01 01")], ("00","01")))
r.append(step("4 OUT1 OFF", [mk("55 0a 03 01 01 01 00 00 01 01")], ("01","01")))

st = status()
print("@@ FINAL (%s,%s)" % st)
print("@@ SUMMARY: " + ", ".join("%d=%s" % (i+1,"PASS" if x else "FAIL") for i,x in enumerate(r)))
s.write(mk("55 04 01 00")); time.sleep(0.5); s.close()
print("@@DONE")
