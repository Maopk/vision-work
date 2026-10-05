"""Where does a background (PrintWindow) capture start relative to the client area?

    python probe_capture_offset.py [--seed 20251007]

The driver maps an image point to the screen as `client origin + image point`. That is
only right if the actor's `shot` of an hwnd returns the *client* area. If it returns the
whole window instead, every mouse coordinate is off by the frame, and clicks miss.

No clicks here: take the window capture and a screen capture of the client rect, then
find the (dx, dy) that lines the two images up. dy = 0 means the capture is the client
area; dy ~ caption height means it is the window.
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

from PIL import Image                                     # noqa: E402
from gym_run import Actor, Driver, kill_stale             # noqa: E402

PY = sys.executable
STATE = os.path.join(HERE, "_probe-offset-state.json")
EVENTS = os.path.join(HERE, "_probe-offset-events.jsonl")


def diff_at(a: Image.Image, b: Image.Image, dx: int, dy: int, box) -> float:
    """Mean |a - b| over `box`, with b sampled at (x+dx, y+dy)."""
    x0, y0, x1, y1 = box
    pa, pb = a.load(), b.load()
    tot = n = 0
    for y in range(y0, y1, 3):
        for x in range(x0, x1, 3):
            bx, by = x + dx, y + dy
            if not (0 <= bx < b.width and 0 <= by < b.height):
                return 1e9
            ca, cb = pa[x, y], pb[bx, by]
            tot += abs(ca[0] - cb[0]) + abs(ca[1] - cb[1]) + abs(ca[2] - cb[2])
            n += 1
    return tot / max(1, n) / 3.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20251007)
    a = ap.parse_args()
    for f in (STATE, EVENTS):
        if os.path.exists(f):
            os.unlink(f)
    kill_stale(STATE)
    cmd = [PY, os.path.join(HERE, "gym_app.py"), "--state", STATE, "--events", EVENTS,
           "--gap", "5000", "--seed", str(a.seed), "--scenario", "t_button",
           "--no-topmost"]
    proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    try:
        d = Driver(Actor(), STATE, verbose=False, bg=True)
        time.sleep(1.6)
        rep = d.a.run([{"op": "window", "mode": "info", "title_contains": d.title}],
                      results=True)
        data = (rep.get("trace") or [{}])[0].get("data") or {}
        print("info by title: rect=%s client=%s hwnd=%s title=%r"
              % (data.get("rect"), data.get("client"), data.get("hwnd"),
                 data.get("title")))
        hwnd = int(data.get("hwnd") or 0)
        if hwnd:
            rep2 = d.a.run([{"op": "window", "mode": "info", "hwnd": hwnd}],
                           results=True)
            d2 = (rep2.get("trace") or [{}])[0].get("data") or {}
            print("info by hwnd : rect=%s client=%s title=%r"
                  % (d2.get("rect"), d2.get("client"), d2.get("title")))

        win = d.shot()                       # the real path: hwnd grab + region crop
        win.save(os.path.join(HERE, "_cap-win.png"))
        print("d.shot() -> %s, driver origin=%s size=%s" % (win.size, d.origin, d.size))

        wr = d.window_rect()
        scr, ox, oy = d.shot_screen(wr)
        scr.save(os.path.join(HERE, "_cap-client.png"))
        print("driver after window_rect(): origin=%s size=%s -> rect %s"
              % (d.origin, d.size, wr))
        print("capture sizes: hwnd shot %s, screen shot of that rect %s at (%d,%d)"
              % (win.size, scr.size, ox, oy))

        box = (200, 120, min(win.width, scr.width) - 60, min(win.height, scr.height) - 120)
        cands = []
        for dy in range(-8, 65, 2):
            for dx in range(-16, 17, 2):
                cands.append((diff_at(win, scr, dx, dy, box), dx, dy))
        cands.sort()
        print("best alignments (mean |diff| per channel, dx, dy):")
        for v, dx, dy in cands[:5]:
            print("   %.2f  dx=%+d dy=%+d" % (v, dx, dy))
        best = cands[0]
        true_client = (ox + best[1], oy + best[2])
        print("VERDICT: the hwnd capture lines up with the screen at dx=%+d dy=%+d, so its"
              " true screen origin is %s; the driver believes %s -> %s"
              % (best[1], best[2], true_client, tuple(d.origin),
                 "MATCH" if max(abs(true_client[0] - d.origin[0]),
                                abs(true_client[1] - d.origin[1])) <= 2 else "MISMATCH"))
        return 0
    finally:
        proc.terminate()
        time.sleep(0.4)


if __name__ == "__main__":
    sys.exit(main())
