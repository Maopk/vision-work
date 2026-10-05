"""Replay the driver's exact key sequence against a practice target, step by step.

The driver's runs never deliver a hint key, while probe_key_map.py - same Driver, same
actor, same app - delivers every one of them. This probe walks the run's own sequence
(bottom, hand the foreground back, Home, screenshot + body OCR, hint key) with each step
switchable, and prints for every step the actor's reply, what the app recorded and who
holds the foreground. That isolates which step in the run's path is the one that kills the
next key.

    python probe_key_seq.py t_rows 20251007 --home --shot --hint
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


def key_events(path: str) -> list[dict]:
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


def press(d, events, name, label=""):
    before = len(key_events(events))
    rep = d.a.run([d.act_step({"op": "key", "keys": [name], "front_title": d.title,
                               "focus": True})], results=True)
    step = (rep.get("trace") or [{}])[0]
    data = step.get("data") or {}
    time.sleep(0.45)
    got = key_events(events)[before:]
    fg = d.foreground()
    print("  press %-6r %s ok=%s bg=%s focused=%s focus_hwnd=%s" %
          (name, label, step.get("ok"), data.get("bg"), data.get("focused"),
           data.get("focus_hwnd")))
    print("      app saw: %s" % json.dumps(got, ensure_ascii=False))
    print("      foreground now: %s" % (fg.get("title") or "")[:60])
    return got


def main() -> int:
    scenario = sys.argv[1] if len(sys.argv) > 1 else "t_rows"
    seed = sys.argv[2] if len(sys.argv) > 2 else "20251007"
    flags = set(sys.argv[3:])
    state = os.path.join(HERE, "probe-seq-state.json")
    events = os.path.join(HERE, "probe-seq-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                             "--scenario", scenario, "--seed", seed,
                             "--state", state, "--events", events, "--gap", "300",
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
        print("app state:", json.dumps(d.state(), ensure_ascii=False)[:160])

        if "--home" in flags:
            press(d, events, "Home", "(task start)")
        if "--shot" in flags:
            t0 = time.perf_counter()
            img = d.shot()
            body_top = d.chrome(img)[1]
            words = d.body_words(img, body_top)
            print("  shot+body in %d ms, %d words" % ((time.perf_counter() - t0) * 1000,
                                                      len(words)))
            print("      after it, foreground: %s" %
                  ((d.foreground().get("title") or "")[:60]))
        if "--hint" in flags:
            st = d.state()
            truth = st.get("truth") or {}
            print("  truth (scoring only):", json.dumps(truth, ensure_ascii=False)[:120])
            want = str(truth.get("id") or (truth.get("row") or {}).get("id") or "")
            img = d.shot()
            words = d.body_words(img, d.chrome(img)[1])
            hit = d.find(words, want) if want else None
            print("  want %r -> %s" % (want, (hit or {}).get("box")))
            hint = d.hint_near(words, hit["box"]) if hit else None
            print("  hint off the screen: %r" % hint)
            if hint:
                press(d, events, hint, "(the hint the app printed)")
        print("all key events the app recorded:")
        for r in key_events(events):
            print("   ", json.dumps(r, ensure_ascii=False))
        print("foreground at exit:", json.dumps(d.foreground(), ensure_ascii=False))
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
