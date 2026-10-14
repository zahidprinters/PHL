/* ECU-30 HMI v1.0 — vanilla JS, FF52-safe subset:
 * fetch + promises + template literals OK; NO ES modules, NO optional
 * chaining, NO ?? , NO gap-dependent CSS. One 1s poll of /api/state.
 */
(function () {
  "use strict";

  var POLL_MS = 1000;
  var LOCKED = true;               // flip with the logic workflow, not before
  var state = null;
  var lastOk = 0;
  var $ = function (id) { return document.getElementById(id); };

  /* ---------- tiny helpers ---------- */
  function path(obj, p) {
    return p.split(".").reduce(function (o, k) {
      return (o === null || o === undefined) ? undefined : o[k];
    }, obj);
  }
  function setText(id, val) {
    var el = $(id);
    if (el) { el.textContent = (val === undefined || val === null) ? "--" : String(val); }
  }
  function fmtUptime(s) {
    if (s === undefined) { return "--"; }
    var d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600),
        m = Math.floor(s % 3600 / 60), sec = s % 60;
    function p2(n) { return (n < 10 ? "0" : "") + n; }
    return (d ? d + "d " : "") + p2(h) + ":" + p2(m) + ":" + p2(sec);
  }
  var toastTimer = null;
  function toast(msg) {
    var t = $("toast");
    t.textContent = msg;
    t.hidden = false;
    if (toastTimer) { clearTimeout(toastTimer); }
    toastTimer = setTimeout(function () { t.hidden = true; }, 2200);
  }
  /* all writes go through here; v1 always refuses, loudly */
  function cmd(payload) {
    if (LOCKED) { toast("Locked — commands activate with the logic workflow"); return; }
    fetch("/api/cmd", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).catch(function () { toast("Command failed"); });
  }

  /* ---------- navigation ---------- */
  var tabs = document.querySelectorAll(".tab");
  Array.prototype.forEach.call(tabs, function (b) {
    b.addEventListener("click", function () {
      var page = b.getAttribute("data-goto");
      Array.prototype.forEach.call(tabs, function (x) { x.classList.remove("active"); });
      b.classList.add("active");
      Array.prototype.forEach.call(document.querySelectorAll(".page"), function (p) {
        p.classList.toggle("active", p.getAttribute("data-page") === page);
      });
    });
  });

  /* ---------- one-time DOM builders (structure from arrays) ---------- */
  function led(hostId, item, isOut) {
    var d = document.createElement("div");
    d.className = "led" + (isOut ? " out" : "");
    d.innerHTML = '<span class="dot"></span><span class="nm">' + item.name +
      '</span><span class="st">' + (item.on ? "ON" : "OFF") + "</span>";
    if (item.on) { d.classList.add("on"); }
    return d;
  }
  function buildOnce() {
    var s = state, h;
    /* digital ins */
    h = $("io-din"); h.innerHTML = "";
    s.io.din.forEach(function (x) { h.appendChild(led("io-din", x, false)); });
    /* digital outs on I/O page */
    h = $("io-dout"); h.innerHTML = "";
    s.io.dout.forEach(function (x) { h.appendChild(led("io-dout", x, true)); });
    /* manual toggles (locked) */
    h = $("m-dout"); h.innerHTML = "";
    s.io.dout.forEach(function (x) {
      var b = document.createElement("button");
      b.className = "tg" + (x.on ? " on" : "");
      b.disabled = LOCKED;
      b.textContent = x.name + (x.on ? " ON" : " OFF");
      b.addEventListener("click", function () { cmd({ ch: x.ch, set: !x.on }); });
      h.appendChild(b);
    });
    /* manual analog sliders (locked) */
    h = $("m-aout"); h.innerHTML = "";
    s.io.aout.forEach(function (x) {
      var w = document.createElement("div");
      w.className = "sld";
      w.innerHTML =
        '<div class="hd"><span>' + x.name + "</span><span>" + x.eng + x.unit + "</span></div>" +
        '<input type="range" min="0" max="100" value="' + x.eng + '" disabled>' +
        '<div class="row"><span>' + x.unit + '</span><input type="number" value="' +
        x.setpoint + '" disabled></div>';
      h.appendChild(w);
    });
    /* home unit list */
    h = $("h-units"); h.innerHTML = "";
    s.devices.forEach(function (d) {
      var li = document.createElement("li");
      li.innerHTML = "<span>" + d.name + " (" + d.type + ")</span><b>" + d.status + "</b>";
      h.appendChild(li);
    });
    /* I/O tables */
    tblRows("io-ain tbody", s.io.ain.map(function (x) {
      return [x.ch, x.name, x.raw, x.eng, x.unit,
        x.scale.raw_lo + ".." + x.scale.raw_hi + " \u2192 " +
        x.scale.eng_lo + ".." + x.scale.eng_hi + " d" + x.scale.dec];
    }));
    tblRows("io-aout tbody", s.io.aout.map(function (x) {
      return [x.ch, x.name, x.raw, x.eng, x.unit, x.setpoint];
    }));
    /* info */
    tblRows("if-dev tbody", s.devices.map(function (d) {
      return [d.id, d.name, d.type, d.status];
    }));
    /* raw */
    tblRows("rw-regs tbody", s.raw.regs.map(function (r) {
      var v = r.val & 0xffff;
      return [r.addr, "0x" + ("000" + r.addr.toString(16)).slice(-4),
        v, ("0000000000000000" + v.toString(2)).slice(-16)];
    }));
    tblRows("rw-scale tbody", s.io.ain.map(function (x) {
      return [x.name, x.raw, x.scale.raw_lo, x.scale.raw_hi,
        x.scale.eng_lo, x.scale.eng_hi, x.scale.dec, x.eng];
    }));
    setText("rw-polled", "polls " + s.raw.polls + " / errors " + s.raw.errors);
  }
  function tblRows(sel, rows) {
    var tb = document.querySelector(sel);
    if (!tb) { return; }
    tb.innerHTML = rows.map(function (r) {
      return "<tr>" + r.map(function (c) { return "<td>" + c + "</td>"; }).join("") + "</tr>";
    }).join("");
  }
  /* ---------- per-tick render ---------- */
  function render() {
    var s = state;
    setText("t-time", s.time);
    setText("t-date", s.date);
    setText("t-mode", s.mode);
    setText("h-mode", s.mode);
    setText("h-uptime", fmtUptime(s.uptime_s));
    setText("if-ip", s.hmi.ip);
    setText("if-ver", s.hmi.version);
    setText("if-mb-port", s.modbus.port);
    setText("if-mb-line", s.modbus.baud + " " + s.modbus.parity);
    setText("if-mb-uid", s.modbus.unit_id);
    setText("if-mb-poll", s.modbus.poll_ms + " ms");
    setText("if-mb-link", s.modbus.connected ? "connected" : "no device");
    var a = $("t-alarm");
    a.textContent = s.alarm.count ? ("ALARM x" + s.alarm.count + ": " + s.alarm.text)
                                  : "No alarms";
    a.classList.toggle("on", !!s.alarm.active);
    buildOnce();   /* ~50 nodes; cheap enough at 1 Hz even on the ARM */
  }

  /* ---------- poll loop ---------- */
  var inflight = false;
  function tick() {
    if (!inflight) {
      inflight = true;
      fetch("/api/state", { cache: "no-store" })
        .then(function (r) {
          if (!r.ok) { throw new Error("http " + r.status); }
          return r.json();
        })
        .then(function (j) {
          state = j;
          lastOk = Date.now();
          $("t-link").textContent = "LINK OK";
          $("t-link").className = "chip ok";
          render();
        })
        .catch(function () {
          $("t-link").textContent = "NO LINK";
          $("t-link").className = "chip err";
        })
        .then(function () {
          inflight = false;
          var age = lastOk ? Math.round((Date.now() - lastOk) / 1000) : "--";
          setText("s-age", "data age: " + age + "s");
        });
    }
    setTimeout(tick, POLL_MS);
  }

  /* ---------- idle screen blank ----------
   * A display preference, not a hardware command, so it stays active while
   * controls are locked. Saved to localStorage (idle seconds; 0 = never blank).
   * Wake on any touch/click/key. No backend call — purely a black overlay. */
  var BLANK_KEY = "hmi.blank";
  var blanker = null;
  var blankTimer = null;
  function blankSecs() {
    var v = parseInt(localStorage.getItem(BLANK_KEY), 10);
    return isNaN(v) ? 0 : v;
  }
  function armBlank() {
    if (blankTimer) { clearTimeout(blankTimer); blankTimer = null; }
    var secs = blankSecs();
    if (secs > 0 && blanker) {
      blankTimer = setTimeout(function () { blanker.classList.add("on"); }, secs * 1000);
    }
  }
  function wake() {
    if (blanker) { blanker.classList.remove("on"); }
    armBlank();   /* activity restarts the idle countdown */
  }
  function initBlank() {
    blanker = $("blanker");
    var sel = $("st-blank");
    if (sel) {
      sel.value = String(blankSecs());
      sel.addEventListener("change", function () {
        var secs = parseInt(sel.value, 10) || 0;
        try { localStorage.setItem(BLANK_KEY, String(secs)); } catch (e) { /* private mode */ }
        wake();
      });
    }
    ["touchstart", "mousedown", "keydown"].forEach(function (ev) {
      document.addEventListener(ev, wake, true);
    });
    armBlank();
  }

  /* go */
  function start() { tick(); initBlank(); }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

})();
