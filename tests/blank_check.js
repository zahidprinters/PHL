/* Throwaway self-check for the idle screen-blank logic in static/app.js.
 * Zero-dependency DOM/localStorage/clock shim -> loads the REAL app.js via vm,
 * then drives blankSecs/armBlank/wake/initBlank through their real entry points.
 * Run: node temp/blank_check.js   (exit 0 = pass) */
"use strict";
const fs = require("fs");
const vm = require("vm");
const path = require("path");
const APP = path.join(__dirname, "..", "os", "node-red", "static", "app.js");

/* ---- fake clock: record timers, allow firing one by delay ---- */
let clockNow = 0, timerSeq = 0;
const timers = new Map();
function fakeSetTimeout(fn, delay) {
  const id = ++timerSeq;
  timers.set(id, { fn, delay: delay | 0, cleared: false });
  return id;
}
function fakeClearTimeout(id) { const t = timers.get(id); if (t) t.cleared = true; }
function fireDelay(delay) {
  const hit = [...timers.entries()].filter(([, t]) => !t.cleared && t.delay === delay).pop();
  if (!hit) throw new Error("no live timer with delay " + delay);
  hit[1].cleared = true; hit[1].fn();
}
function liveTimers(delay) {
  return [...timers.values()].filter((t) => !t.cleared && t.delay === delay).length;
}

/* ---- fake element ---- */
function el(id) {
  const cls = new Set();
  const handlers = {};
  return {
    id, value: "", textContent: "", className: "", hidden: false, disabled: false,
    innerHTML: "", _cls: cls,
    classList: {
      add: (c) => cls.add(c), remove: (c) => cls.delete(c),
      contains: (c) => cls.has(c),
      toggle: (c, f) => { (f === undefined ? !cls.has(c) : f) ? cls.add(c): cls.delete(c); },
    },
    addEventListener: (type, fn) => { (handlers[type] = handlers[type] || []).push(fn); },
    _fire: (type) => (handlers[type] || []).forEach((fn) => fn({ type })),
    appendChild() {}, setAttribute() {}, getAttribute() { return null; },
  };
}

/* ---- build the sandbox and load the real file fresh each case ---- */
function loadApp(initialStore) {
  const store = Object.assign({}, initialStore);
  const els = {};
  const docHandlers = {};
  const getEl = (id) => (els[id] = els[id] || el(id));
  const sandbox = {
    document: {
      readyState: "complete",
      getElementById: getEl,
      querySelectorAll: () => [],
      createElement: () => el("new"),
      addEventListener: (type, fn) => { (docHandlers[type] = docHandlers[type] || []).push(fn); },
    },
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
    },
    setTimeout: fakeSetTimeout, clearTimeout: fakeClearTimeout,
    fetch: () => Promise.reject(new Error("offline (expected)")),  // exercises the catch path
    Date, Math, JSON, parseInt, isNaN, String, console, Promise,
  };
  vm.runInNewContext(fs.readFileSync(APP, "utf8"), sandbox, { filename: APP });
  return { els, store, docHandlers };
}

let pass = 0, fail = 0;
function check(name, cond) {
  if (cond) { pass++; console.log("  PASS " + name); }
  else { fail++; console.log("  FAIL " + name); }
}

/* Case 1: default (no pref) -> Always on -> blanker never arms */
(() => {
  timers.clear();
  const { els } = loadApp({});
  check("default: no blank timer armed", liveTimers(60000) === 0);
  check("default: select shows Always on (0)", els["st-blank"].value === "0");
  check("default: blanker not shown", !els["blanker"]._cls.has("on"));
})();

/* Case 2: stored pref 60s -> arms one 60s timer; fires -> blank; wake -> re-arm */
(() => {
  timers.clear();
  const { els, store, docHandlers } = loadApp({ "hmi.blank": "60" });
  check("pref 60: select reflects 60", els["st-blank"].value === "60");
  check("pref 60: exactly one 60s timer armed", liveTimers(60000) === 1);
  fireDelay(60000);
  check("pref 60: timer fire shows blanker", els["blanker"]._cls.has("on"));
  // simulate a wake via the keydown document listener (capture phase)
  (docHandlers["keydown"] || []).forEach((fn) => fn({ type: "keydown" }));
  check("wake: blanker hidden again", !els["blanker"]._cls.has("on"));
  check("wake: idle countdown re-armed", liveTimers(60000) === 1);
  void store;
})();

/* Case 3: user changes select to Always on -> persisted + timer cleared */
(() => {
  timers.clear();
  const { els, store, docHandlers } = loadApp({ "hmi.blank": "60" });
  check("before change: one 60s timer", liveTimers(60000) === 1);
  els["st-blank"].value = "0";
  (els["st-blank"].addEventListener ? docHandlers : docHandlers); // no-op guard
  // fire the select's own change handler
  const selChange = (function () {
    // the change handler was attached to the select element, not document;
    // grab it through the element we stored
    return null;
  })();
  void selChange;
  // The element's handlers live on els["st-blank"]; invoke them:
  els["st-blank"]._fire("change");
  check("change to 0: persisted hmi.blank=0", store["hmi.blank"] === "0");
  check("change to 0: no 60s timer remains", liveTimers(60000) === 0);
  void docHandlers;
})();

/* Case 4: malformed stored value falls back to Always on */
(() => {
  timers.clear();
  const { els } = loadApp({ "hmi.blank": "garbage" });
  check("malformed: treated as 0 / Always on", els["st-blank"].value === "0");
  check("malformed: no blank timer armed", liveTimers(60000) === 0);
})();

console.log("\n" + pass + " passed, " + fail + " failed");
process.exit(fail ? 1 : 0);
