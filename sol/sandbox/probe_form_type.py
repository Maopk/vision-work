"""Which way of posting text actually lands in a focused Entry?

The form task focuses each field with its own hint key, but the values never arrive - the
app records stray hint digits (`{"Contact": "19"}` where "Ember" was typed). Both paths are
in play and they are not equivalent: the `type` op posts WM_CHAR (post_text), while the
`key` op posts WM_KEYDOWN/WM_KEYUP with the scan code in lParam (post_key, fixed earlier).
This probe focuses one field and tries both against the app's own record of the Entry.

    python probe_form_type.py 20251007
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gym_run import Actor, Driver, _form_pairs                  # noqa: E402

HINT_KEYS = "123456789"


def events_of(path: str, kind: str) -> list[dict]:
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("event") == kind:
            out.append(rec)
    return out


def main() -> int:
    seed = sys.argv[1] if len(sys.argv) > 1 else "20251007"
    state = os.path.join(HERE, "probe-form-state.json")
    events = os.path.join(HERE, "probe-form-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                             "--scenario", "t_form", "--seed", seed,
                             "--state", state, "--events", events, "--gap", "100000",
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
        st = d.state()
        print("ask:", (st.get("ask") or "")[:100])
        print("truth (scoring only):", json.dumps(st.get("truth") or {}, ensure_ascii=False))

        img = d.shot()
        ask, body_top, _band, _ask_box = d.chrome(img)
        body = d.body_words(img, body_top)
        pairs = _form_pairs(ask)
        print("pairs off the banner:", pairs)
        for field, _v in pairs:
            w = d.find(body, field, 0.9) or d.find(body, field, 0.68)
            print("  label %-9s -> %s" % (field, (w or {}).get("box")))

        def step(label, fn):
            before = len(events_of(events, "entry"))
            keys_before = len(events_of(events, "key"))
            fn()
            time.sleep(0.5)
            got = events_of(events, "entry")[before:]
            keys = events_of(events, "key")[keys_before:]
            print("%-26s -> entry %s" % (label, json.dumps([(r.get("field"), r.get("text"))
                                                            for r in got], ensure_ascii=False)))
            if keys:
                print("%-26s    keys %s" % ("", json.dumps(
                    [(r.get("ks"), r.get("hit")) for r in keys], ensure_ascii=False)))
            print("%-26s    foreground %s" % ("", (d.foreground().get("title") or "")[:44]))

        # focus field 0 with its own hint key, the way the driver does
        step("hint key %r (focus field 0)" % HINT_KEYS[0],
             lambda: d.key(HINT_KEYS[0]))
        step("type op 'AA'", lambda: d.type_text("AA"))
        # once an Entry holds the focus the app ignores every key but Return (typing into a
        # field must not fire shortcuts), so the next hint key is swallowed: leave the
        # Entry first and see whether the focus actually moves to field 1
        step("key op 'Tab' (leave Entry)", lambda: d.key("Tab"))
        step("hint key %r (focus field 1)" % HINT_KEYS[1],
             lambda: d.key(HINT_KEYS[1]))
        step("type op 'BB'", lambda: d.type_text("BB"))
        step("key op 'Escape'", lambda: d.key("Escape"))
        step("type op 'CC'", lambda: d.type_text("CC"))
        print("state result:", d.state().get("result"), "| events:", os.path.basename(events))
        print("foreground at exit:", json.dumps(d.foreground(), ensure_ascii=False))
        return 0
    finally:
        proc.terminate()


if __name__ == "__main__":
    sys.exit(main())
