"""Which transport can drive a Tk window that is NOT in the foreground?

Tk silently drops posted keys when it does not believe it has the focus, and a
background driver cannot make the app the foreground window (the user is using the
machine). This probe measures the candidates on a live t_button task, one variant
per attempt, and reports which one actually moved the app on:

  key        PostMessage WM_KEYDOWN/WM_KEYUP to the toplevel
  char       PostMessage WM_CHAR (the actor's `type` in bg mode)
  focus+key  SetFocus inside the app's own thread queue (AttachThreadInput), then key
  focus+char same, then WM_CHAR

Nothing here is part of the driver: it exists to answer "does this transport work at
all" with a number instead of an assumption.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gym_run import Actor, Driver, foreground_via     # noqa: E402  (path first)

VARIANTS = ("focus+key",) * 4
KEEP_FOCUS = False          # the app's own focus_force() may be what breaks the chain
USE_DRIVER_PRESS = True     # go through Driver.press_hint instead of a raw post


def launch(state: str, events: str) -> subprocess.Popen:
    cmd = [sys.executable, os.path.join(HERE, "gym_app.py"),
           "--scenario", "t_button", "--seed", "777",
           "--state", state, "--events", events, "--gap", "300",
           "--no-topmost"]
    if KEEP_FOCUS:
        cmd += ["--keep-focus"]
    return subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)


def send(a: Actor, hwnd: int, hint: str, variant: str) -> None:
    if variant.startswith("focus+"):
        rep = a.run([{"op": "window", "mode": "focus", "hwnd": hwnd}], results=True)
        for step in rep.get("trace", []):
            data = step.get("data") or {}
            if step.get("op") == "window":
                print("   focus -> %s" % json.dumps(data, ensure_ascii=False))
    if variant.endswith("char"):
        a.run([{"op": "type", "text": hint, "bg": True, "hwnd": hwnd}])
    else:
        a.run([{"op": "key", "keys": [hint], "bg": True, "hwnd": hwnd}])


def main() -> int:
    state = os.path.join(HERE, "probe-key-state.json")
    events = os.path.join(HERE, "probe-key-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    fg_before = foreground_via(Actor())          # the user's window, before we exist
    proc = launch(state, events)
    try:
        time.sleep(2.5)
        d = Driver(Actor(), state, bg=True, keys=True)
        d.window_rect()
        d.a.run([{"op": "window", "mode": "bottom", "title_contains": d.title}])
        # starting the app made it active: put the user back in front, otherwise this
        # probe would silently measure the easy case (foreground window posts work)
        if fg_before.get("hwnd"):
            d.a.run([{"op": "window", "mode": "front", "hwnd": fg_before["hwnd"]}])
            time.sleep(0.3)
        fg = d.foreground()
        print("app  hwnd=%s  origin=%s size=%s" % (d.hwnd, d.origin, d.size))
        print("foreground is now: %s (hwnd %s)" % ((fg or {}).get("title", "?")[:50],
                                                   (fg or {}).get("hwnd")))
        results = []
        for variant in VARIANTS:
            st = d.state()
            task_i, ask = st.get("task_i"), st.get("ask") or ""
            img = d.shot()
            chrome = d.chrome(img)
            body = d.body_words(img, chrome[1])
            want = ask.split("labelled")[-1].strip()
            hit = d.find(body, want, 0.8)
            if not hit:
                print("%-11s SKIP  %r not in the OCR map" % (variant, want))
                continue
            hint = d.hint_near(body, hit["box"])
            print("%-11s task %s ask=%r want=%r hint=%s" % (variant, task_i, ask[:46],
                                                            want, hint))
            if not hint:
                print("            no [k] hint beside the label")
                continue
            if USE_DRIVER_PRESS:
                # the driver's own path: focus hand-off + PostMessage inside press_hint
                rec2: dict = {}
                ok = d.press_hint(rec2, body, hit["box"], "button")
                print("            driver press_hint -> %s  hints=%s  stats=%s" %
                      (ok, rec2.get("hints"), {k: v for k, v in d.stats.items()
                                               if k in ("keys", "focus", "no_hint")}))
            else:
                send(d.a, d.hwnd, hint, variant)
            time.sleep(1.4)
            # the app echoes every key it accepts onto its bottom key line: reading it
            # separates "the key never arrived" from "it arrived and did nothing"
            img2 = d.shot()
            bar = d.words(img2, region=(0, img2.height - 60, img2.width, 60), psm="7",
                          min_conf=20.0)
            after = d.state()
            moved = after.get("task_i") != task_i
            print("            keybar %r" % " ".join(w_["text"] for w_ in bar)[:70])
            print("            -> %s (task %s -> %s, result %s)" %
                  ("HIT" if moved else "no effect", task_i, after.get("task_i"),
                   after.get("result")))
            results.append((variant, moved))
        print("\ntransport                  delivered")
        for variant, moved in results:
            print("  %-24s %s" % (variant, "YES" if moved else "no"))
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
