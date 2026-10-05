"""Where is the app's menubar? Screenshot the strip *above* the captured window.

The t_menu driver reads the menubar inside its window shot, but OCR of the top of that shot
returns the ask banner itself (`DO: invoke the menu ...`), so the strip the driver calls the
window top is already below the menubar. This probe captures the window plus 90 px above it
and prints what is actually in those rows.

    python probe_menu_above.py 20251007
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gym_run import Actor, Driver                                    # noqa: E402


def main() -> int:
    seed = sys.argv[1] if len(sys.argv) > 1 else "20251007"
    state = os.path.join(HERE, "probe-above-state.json")
    events = os.path.join(HERE, "probe-above-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                             "--scenario", "t_menu", "--seed", seed,
                             "--state", state, "--events", events, "--gap", "100000",
                             "--no-topmost"],
                            cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    try:
        time.sleep(2.5)
        d = Driver(Actor(), state, bg=True, keys=True)
        x1, y1, x2, y2 = d.window_rect()
        print("window rect:", (x1, y1, x2, y2), "size", (x2 - x1, y2 - y1))
        img = d.shot(region=(x1, max(0, y1 - 90), x2, y2))
        img.save(os.path.join(HERE, "probe-menu-above.png"))
        print("saved probe-menu-above.png", img.size)
        for psm in ("7", "11", "6"):
            ws = d.words(img, region=(0, 0, img.width, 120), psm=psm, min_conf=15.0)
            print("psm %-3s top120: %s" % (psm, json.dumps(
                [(w["text"], w["box"][1]) for w in ws][:14], ensure_ascii=False)))
        ask, body_top, band, ask_box = d.chrome(img)
        print("chrome: ask=%r body_top=%s ask_box=%s" % (ask[:60], body_top, ask_box))
        # the window capture starts *below* the toplevel's menubar, so look at the screen
        # strip just above the captured rect
        simg, sx, sy = d.shot_screen((x1, max(0, y1 - 46), x2, y1 + 2))
        simg.save(os.path.join(HERE, "probe-menu-screen-above.png"))
        for psm in ("7", "6"):
            ws = d.words(simg, region=(0, 0, simg.width, simg.height), psm=psm, min_conf=15.0)
            print("screen above psm %-3s: %s" % (psm, json.dumps(
                [(w["text"], w["box"]) for w in ws][:14], ensure_ascii=False)))
        print("state:", json.dumps(d.state().get("ask"), ensure_ascii=False))
        # last resort: is the menubar anywhere on screen at all?
        full, fx, fy = d.shot_screen((0, 0, 2560, 1600))
        full.save(os.path.join(HERE, "probe-menu-fullscreen.png"))
        ws = d.words(full, region=(0, 0, full.width, full.height), psm="11", min_conf=20.0)
        hits = [(w["text"], w["box"]) for w in ws
                if "EMBER" in (w["text"] or "").upper() or "LUMEN" in (w["text"] or "").upper()]
        print("EMBER/LUMEN words on the whole screen:", json.dumps(hits[:8], ensure_ascii=False))
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
