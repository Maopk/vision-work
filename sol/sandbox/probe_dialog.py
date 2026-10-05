"""Can the driver see and click the interfering window at all?

Forces the `popup` disturbance only, then reports what the screenshot actually
contains: every OCR word, the fuzzy score of DISMISS, and whether clicking it
unblocks scoring.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

from loop import Actor
from gym_run import Driver

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def main() -> int:
    state = os.path.join(HERE, "probe-dialog-state.json")
    events = os.path.join(HERE, "probe-dialog-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([PY, os.path.join(HERE, "gym_app.py"), "--scenario", "t_button",
                             "--seed", "777", "--state", state, "--events", events,
                             "--chaos", "1.0", "--chaos-kind", "popup",
                             "--chaos-ms", "300,400"],
                            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(3.0)
    d = Driver(Actor(), state, verbose=False)
    try:
        img = d.shot()
        img.save(os.path.join(HERE, "probe-dialog.png"))
        print("window rect", d.window_rect(), "image", img.size)
        for inv in (False, True):
            ws = d.words(img, invert=inv)
            print("invert=%s  %d words" % (inv, len(ws)))
            for w in ws:
                print("    %-14r conf=%5.1f box=%s" % (w["text"], w["conf"], w["box"]))
        for thr in (0.9, 0.75, 0.6, 0.45):
            print("find DISMISS @%.2f ->" % thr, d.find(d.words(img), "DISMISS", thr))
        before = d.task_i()
        _, n = d.dismiss_interference(img)
        print("dismiss_interference -> clicked %d, task_i %s -> %s" % (n, before, d.task_i()))
        time.sleep(1.0)
        print("result after dismiss:", d.result(), "task_i", d.task_i())
    finally:
        proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
