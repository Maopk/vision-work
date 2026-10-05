"""Post one key at a time and print what the target app actually received.

The driver's hint presses were reaching the app as keysym "??" with a character but no
keycode, which the app cannot dispatch - and "the task advanced" is too weak a signal to
tell a delivered key from a lucky one. This probe isolates the posting path: it presses a
few keys and then prints the app's own record of each one (keysym, character, keycode),
so the actor's message can be judged by the app's view of it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gym_run import Actor, Driver                           # noqa: E402


def read_key_events(path: str) -> list[dict]:
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("event") == "key":
            out.append({k: rec.get(k) for k in ("ks", "char", "keycode", "num", "hit")})
    return out


def main() -> int:
    keys = sys.argv[1].split(",") if len(sys.argv) > 1 else ["1", "2", "7", "Home", "Next"]
    scenario = sys.argv[2] if len(sys.argv) > 2 else "t_button"
    state = os.path.join(HERE, "probe-keymap-state.json")
    events = os.path.join(HERE, "probe-keymap-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                             "--scenario", scenario, "--seed", "777",
                             "--state", state, "--events", events, "--gap", "400",
                             "--no-topmost"],
                            cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    try:
        time.sleep(2.5)
        d = Driver(Actor(), state, bg=True, keys=True)
        d.window_rect()
        d.a.run([{"op": "window", "mode": "bottom", "title_contains": d.title}])
        fg = d.foreground()
        if fg.get("hwnd"):
            d.a.run([{"op": "window", "mode": "front", "hwnd": fg["hwnd"]}])
            time.sleep(0.3)
        for k in keys:
            before = len(read_key_events(events))
            d.key(k)
            time.sleep(0.5)
            got = read_key_events(events)[before:]
            print("posted %-6r -> %s" % (k, json.dumps(got, ensure_ascii=False)))
        print("foreground after:", json.dumps(d.foreground(), ensure_ascii=False))
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
