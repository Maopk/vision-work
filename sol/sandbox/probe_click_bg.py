"""Why do mouse clicks posted to the app not register while backgrounded?

    python probe_click_bg.py [--seed 20251007]

Evidence so far: a mouse-mode run in --bg scored 0/3 with 36 clicks and 6 dialog
clearings - every click was posted (no cursor movement, no activation) yet the app
never scored anything, including clicks on its own DISMISS button. The keyboard
channel works in the same window, so the window handle and the capture are right;
what is unproven is whether Tk acts on posted mouse messages at all.

This probe tries the posted variants in order and reports which one (if any) makes
the app record a verdict. It never moves the user's cursor: every variant goes
through PostMessage.
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import gui_see as G                                      # noqa: E402
from gym_run import Actor, Driver, kill_stale            # noqa: E402

PY = sys.executable
STATE = os.path.join(HERE, "_probe-click-state.json")
EVENTS = os.path.join(HERE, "_probe-click-events.jsonl")


def verdict(d):
    st = d.state()
    hist = st.get("history") or []
    return (st.get("task_i"), st.get("result"), hist[-1] if hist else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20251007)
    a = ap.parse_args()
    for f in (STATE, EVENTS):
        if os.path.exists(f):
            os.unlink(f)
    kill_stale(STATE)
    cmd = [PY, os.path.join(HERE, "gym_app.py"), "--state", STATE, "--events", EVENTS,
           "--gap", "2600", "--seed", str(a.seed), "--scenario", "t_button",
           "--no-topmost"]
    proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    try:
        d = Driver(Actor(), STATE, verbose=False, bg=True)
        time.sleep(1.5)
        img = d.shot()
        _ask, body_top, _band, _abox = d.chrome(img)
        body = d.body_words(img, body_top)
        print("capture %s, window rect %s, hwnd %s"
              % (img.size, d.window_rect(), d.hwnd))
        ask = d.state().get("ask")
        truth = d.state().get("truth") or {}
        want = truth.get("want") or truth.get("label") or truth.get("target")
        if not want:
            m = re.search(r"labelled\s+(\S+)", ask or "")
            want = m.group(1) if m else None
        print("ask=%r want=%r (truth keys %s)"
              % (ask, want, sorted(truth.keys())))
        hit = None
        for w in body:
            if want and G.find_text([w], str(want), min_score=0.82):
                hit = w
                break
        if hit is None:
            print("target label not read from the capture - abort")
            return 2
        cx, cy = hit["center"]
        sx, sy = d.screen((cx, cy))
        print("label %r box=%s center=%s -> screen=%s"
              % (hit["text"], hit["box"], (cx, cy), (sx, sy)))
        blocks = [b for b in d.find_blocks(img)
                  if b[0] - 10 <= cx <= b[0] + b[2] + 10 and b[1] - 10 <= cy <= b[1] + b[3] + 10]
        print("blocks covering the label: %s" % [(b[:4], d.block_label(img, b)) for b in blocks])
        allb = d.find_blocks(img)
        print("all blocks in the window: %d, first: %s"
              % (len(allb), [(b[:4], b[4]) for b in allb[:6]]))

        variants = []
        b = blocks[0] if blocks else None
        if b:
            bcx, bcy = b[0] + b[2] // 2, b[1] + b[3] // 2
            variants.append(("block centre", d.screen((bcx, bcy))))
        variants.append(("label centre", (sx, sy)))
        # a posted click carries client coordinates in the message, so any mismatch
        # between the client origin the driver believes in and the one Windows uses
        # shows up as a constant offset: sweep the plausible ones and see which lands
        for ox, oy in ((0, -28), (-11, -28), (-11, 0), (11, -28), (0, 28), (-22, -56)):
            variants.append(("offset %+d%+d" % (ox, oy), (sx + ox, sy + oy)))
        for name, (x, y) in variants:
            i0 = d.task_i()
            step = d.act_step({"op": "click", "target": {"xy": [int(x), int(y)]}})
            rep = d.a.run([step], results=True)
            tr = (rep.get("trace") or [{}])[0]
            dat = tr.get("data") or {}
            clk = dat.get("click") or {}
            time.sleep(1.2)
            print("  %-14s screen=(%d,%d) bg=%s posted=%s -> task_i %s->%s result=%s"
                  % (name, x, y, dat.get("bg"), clk.get("how"), i0, d.task_i(),
                     d.state().get("result")))
            if d.task_i() != i0:
                print("VERDICT: posted click works at %s" % name)
                return 0
        print("VERDICT: posted clicks never land - checking the geometry once with a real"
              " (SendInput) click; the window is put in front for ~1 s and the previous"
              " foreground window is restored right after")
        fg = d.foreground().get("hwnd")
        # the proven foreground path is the one Driver.click uses: carry front_title so
        # the actor raises the window itself (a bare `window mode=front` did not visibly
        # take, and a click that misses the app lands in whatever window *is* in front -
        # the user's - so check who is in front right before clicking)
        step = {"op": "click", "target": {"xy": [int(sx), int(sy)]},
                "front_title": d.title}
        i0 = d.task_i()
        d.a.run([step], results=True)
        fg_now = d.foreground()
        time.sleep(1.2)
        i1, res = d.task_i(), d.state().get("result")
        print("  foreground click at %s with front_title=%r -> front during click: %s"
              " (app hwnd %s) task_i %s->%s result=%s"
              % ((int(sx), int(sy)), d.title, fg_now.get("title"), d.hwnd, i0, i1, res))
        if fg:
            for _ in range(2):
                d.a.run([{"op": "window", "mode": "front", "hwnd": int(fg)}], results=True)
                time.sleep(0.4)
                if d.foreground().get("hwnd") == fg:
                    break
        print("  foreground click at %s -> task_i %s->%s result=%s"
              % ((int(sx), int(sy)), i0, i1, res))
        print("  foreground restored: %s (was hwnd %s, now %s)"
              % (d.foreground().get("hwnd") == fg, fg, d.foreground().get("hwnd")))
        return 0 if i1 != i0 else 1
    finally:
        proc.terminate()
        time.sleep(0.4)


if __name__ == "__main__":
    sys.exit(main())

