"""Which window handle actually accepts a posted click?

Background input hinges on this: Tk draws the whole UI itself, so posting to the
top-level handle should work - but if the app never reacts, the messages are going
to the wrong window and the real input window is somewhere below it. This probe
launches the gym, finds a button the same way the driver does, and posts the click
first to the child window and then to the top level, reporting what the app logged.
"""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import time

from gym_run import Actor, Driver, _ask_key

HERE = os.path.dirname(os.path.abspath(__file__))


def children(hwnd: int) -> list[tuple[int, str, list[int]]]:
    u = ctypes.windll.user32
    out: list[tuple[int, str, list[int]]] = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(h, _lp):
        buf = ctypes.create_unicode_buffer(256)
        u.GetClassNameW(ctypes.c_void_p(h), buf, 256)
        r = ctypes.wintypes.RECT() if hasattr(ctypes, "wintypes") else None
        rect = [0, 0, 0, 0]
        if r is not None:
            u.GetWindowRect(ctypes.c_void_p(h), ctypes.byref(r))
            rect = [r.left, r.top, r.right, r.bottom]
        out.append((int(h), buf.value, rect))
        return True

    u.EnumChildWindows(ctypes.c_void_p(hwnd), WNDENUMPROC(cb), None)
    return out


def history_len(state_path: str) -> int:
    try:
        with open(state_path, encoding="utf-8") as fh:
            return len(json.load(fh).get("history") or [])
    except (OSError, ValueError):
        return 0


def main() -> int:
    state = os.path.join(HERE, "_post-state.json")
    events = os.path.join(HERE, "_post-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                             "--state", state, "--events", events, "--no-topmost",
                             "--gap", "400", "--seed", "777", "--scenario", "t_button"],
                            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        time.sleep(3.0)
        d = Driver(Actor(), state, bg=True)
        d.window_rect()
        d.a.run([{"op": "window", "mode": "bottom", "title_contains": d.title}])
        top = d.hwnd
        kids = children(top or 0)
        print("toplevel hwnd=%s  children=%s" % (top, [(h, c, r) for h, c, r in kids]))

        img = d.shot()
        ask, body, _band, _box = d.chrome(img)
        print("ask on screen: %r  body_top=%s" % (ask, body))
        label = _ask_key(ask).replace("CLICKTHEBUTTONLABELLED", "")
        words = d.words(img, region=(0, body, img.width, img.height - body))
        pick = d.find(words, label, 0.8)
        if not pick:
            print("button %r not found in %s" % (label, [w["text"] for w in words]))
            return 1
        x, y = d.screen(pick["center"])
        print("button %r at screen (%d, %d)" % (label, x, y))

        for name, hwnd in [("child", kids[0][0] if kids else None), ("toplevel", top)]:
            if not hwnd:
                continue
            before = history_len(state)
            d.click_hwnd(int(hwnd), x, y)
            time.sleep(0.8)
            after = history_len(state)
            print("posted to %-8s -> history %d -> %d  %s"
                  % (name, before, after, "REACTED" if after > before else "no reaction"))
            if after > before:
                break
        try:
            with open(events, encoding="utf-8") as fh:
                for line in fh.readlines()[-4:]:
                    print("  event:", line.strip()[:160])
        except OSError:
            pass
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
