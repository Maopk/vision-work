"""Why does one t_rows row have no key hint on screen?

Reproduces the mixed-run failure (seed 20251007, task 34: `select the row whose id is
4468`) and then reads the *same* screen the driver reads: every row id it can find with
the hint strip left of it, at 1x and at 4x, plus the app's own `rowkeys` bookkeeping.

    python probe_row34.py            # drives tasks 0..33 first, then inspects
    python probe_row34.py --keep     # keep the target running afterwards
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gui_see as G                                          # noqa: E402
from gym_run import (HERE, Driver, foreground_via, kill_stale,   # noqa: E402
                     target_windows)
from loop import Actor                                       # noqa: E402

STATE = os.path.join(HERE, "probe34-state.json")
EVENTS = os.path.join(HERE, "probe34-events.jsonl")
ERR = os.path.join(HERE, "probe34-err.log")
SEED = "20251007"


def start_app(py: str) -> subprocess.Popen:
    kill_stale(STATE)
    for p in (STATE, EVENTS, ERR):
        if os.path.exists(p):
            os.unlink(p)
    proc = subprocess.Popen(
        [py, "-u", os.path.join(HERE, "gym_app.py"), "--state", STATE, "--events", EVENTS,
         "--seed", SEED, "--scenario", "t_rows", "--gap", "300", "--no-topmost"],
        cwd=HERE, stdout=subprocess.DEVNULL, stderr=open(ERR, "w"))
    time.sleep(2.5)
    return proc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    ap.add_argument("--py", default=sys.executable)
    a = ap.parse_args()
    fg = foreground_via(Actor())
    start_app(a.py)
    print("app started, foreground was %s" % str(fg.get("title"))[:50])

    run = subprocess.run(
        [a.py, os.path.join(HERE, "gym_run.py"), "--scenario", "t_rows", "--tasks", "34",
         "--seed", SEED, "--keys", "--bg", "--max-repeat", "3", "--no-start",
         "--state", STATE, "--events", EVENTS, "--json-out", "probe34-run.json"],
        cwd=HERE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        universal_newlines=True, timeout=900)
    tail = (run.stdout or "").strip().splitlines()[-4:]
    print("driver tail:", " | ".join(tail))

    Actor().run([{"op": "window", "mode": "front", "hwnd": fg["hwnd"]}])
    time.sleep(0.3)
    wins = target_windows(Actor())
    if not wins:
        print("no target window")
        return 1
    d = Driver(Actor(), STATE, bg=True, keys=True)
    d.window_rect()
    img = d.shot()
    print("frame %dx%d hwnd=%s" % (img.width, img.height, d.hwnd))
    print("truth (diagnosis only):",
          json.dumps(json.load(open(STATE, encoding="utf-8")).get("truth"))[:200])

    body = d.words(img, region=(0, 40, img.width, img.height - 60), psm="11", scale=2)
    rows = [w for w in body if re.fullmatch(r"#?\d{3,5}", w["text"].strip())]
    print("rows seen: %d" % len(rows))
    for w in sorted(rows, key=lambda w: w["box"][1]):
        bx, by, bw, bh = w["box"]
        strip_ok = d.reread(img, (max(bx - 92, 0), max(by - 6, 0), 88, bh + 12),
                            whitelist="123456789abcdefghijlmoprstuvwxyz[]()<>", psm="7")
        strip_all = d.reread(img, (0, max(by - 10, 0), max(bx - 4, 1), bh + 20), psm="7")
        print("  y=%-4d id=%-6s strip=%-8r whole=%-14r" % (by, w["text"], strip_ok, strip_all))

    ev = []
    if os.path.exists(EVENTS):
        for line in open(EVENTS, encoding="utf-8"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("event") in ("rowkeys", "key"):
                ev.append(r)
    print("last rowkeys:", json.dumps(ev[-1] if ev else None)[:200])
    print("events with rowkeys:", sum(1 for r in ev if r.get("event") == "rowkeys"))
    if not a.keep:
        kill_stale(STATE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
