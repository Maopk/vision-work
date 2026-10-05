"""Page through a scrollable t_rows board and see whether the asked id is reachable.

The driver paged with the app's own key and still never found its row, so walk every
page of a board that provably scrolls and print, per page, the ids on screen, whether
the asked id is among them, and whether it carries a hint. The app's own truth is read
only afterwards, for scoring - it never feeds a decision.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gym_run import Actor, Driver, foreground_via           # noqa: E402

ID_RE = re.compile(r"^#?\d{3,5}$")


def main() -> int:
    seed = sys.argv[1] if len(sys.argv) > 1 else "20251007"
    state = os.path.join(HERE, "probe-page-state.json")
    events = os.path.join(HERE, "probe-page-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    fg_before = foreground_via(Actor())
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                             "--scenario", "t_rows", "--seed", seed,
                             "--state", state, "--events", events, "--gap", "300",
                             "--no-topmost"],
                            cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    try:
        time.sleep(2.5)
        d = Driver(Actor(), state, bg=True, keys=True)
        d.window_rect()
        d.a.run([{"op": "window", "mode": "bottom", "title_contains": d.title}])
        if fg_before.get("hwnd"):
            d.a.run([{"op": "window", "mode": "focus", "hwnd": d.hwnd}])
        # walk to the task we want to look at: task generation is a fixed rng sequence,
        # so pressing "n" k times lands on the same board the driver met as task k
        walk = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        for _ in range(walk):
            d.key("n")
            time.sleep(1.2)
        img = d.shot()
        ask, body_top, _band, _box = d.chrome(img)
        want = re.search(r"id\s*(?:is\s*)?(\d+)", ask)
        want = want.group(1) if want else "?"
        print("ask %r want=%s" % (ask[:50], want))
        d.key("Home")
        time.sleep(0.4)
        seen: list[str] = []
        for page in range(6):
            img = d.shot()
            _a, top, _band, _box = d.chrome(img)
            ws = d.body_words(img, top)
            ids = [w["text"].strip().lstrip("#") for w in ws if ID_RE.match(w["text"].strip())]
            hints = [w["text"].strip() for w in ws
                     if re.match(r"^\[[0-9a-z]\]$", w["text"].strip())]
            seen += ids
            print("page %d n=%-3d want_here=%-5s first=%-6s last=%-6s hints=%d"
                  % (page, len(ids), want in ids, ids[0] if ids else "-",
                     ids[-1] if ids else "-", len(hints)))
            d.key("Next")
            time.sleep(0.45)
        # scoring only - the driver never sees this
        st = json.load(open(state, encoding="utf-8"))
        print("truth (scoring only) =", json.dumps(st.get("truth"), ensure_ascii=False))
        print("want seen on any page: %s   distinct ids on screen: %d"
              % (want in seen, len(set(seen))))
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
