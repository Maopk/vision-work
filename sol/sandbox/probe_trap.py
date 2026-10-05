"""Smoke-test the `t_trap` target itself: every class builds, every truth is scored.

Part A (default) runs in-process and never reads the screen - it tests the target, not
the driver.  For each of the 24 plan entries it checks the painted structure against
the declared truth, then plays the move that should be right (the wanted control's
hint key, or F8 to refuse) and the moves that should be wrong.

Part B (--e2e) proves the refuse key really travels the production channel: it starts
the app as a window, presses F8 through dsh-actor in background mode, and checks the
app's own event stream saw `ks=F8`.

Run:  python probe_trap.py            (part A)
      python probe_trap.py --e2e      (part A + the F8 delivery check)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gym_app as G  # noqa: E402

FAILS: list = []


def check(cond, what: str, extra: str = "") -> None:
    print("%s %s%s" % ("ok  " if cond else "FAIL", what, ("  " + extra) if extra else ""))
    if not cond:
        FAILS.append(what)


def fresh(seed: int = 20251007):
    d = tempfile.mkdtemp(prefix="trap-probe-")
    st, ev = os.path.join(d, "state.json"), os.path.join(d, "events.jsonl")
    app = G.Gym(seed, st, ev, "t_trap", 10, 0.0, (600, 1800), "any", popup_topmost=False)
    app.withdraw()
    pump(app, 0.30)
    return app, st, ev


def pump(app, seconds: float) -> None:
    end = time.time() + seconds
    while time.time() < end:
        app.update()
        time.sleep(0.01)


def controls(app) -> dict:
    """label -> (key or None, widget) for what is painted right now.

    The badge printed on a control is its key, and a control without one (a disabled
    button) is exactly the structural signal the driver is supposed to read.
    """
    out: dict = {}
    stack = [app.body]
    while stack:
        w = stack.pop()
        for ch in w.winfo_children():
            stack.append(ch)
            txt = ""
            kind = ch.winfo_class()
            if kind in ("Button", "Label"):
                txt = str(ch.cget("text"))
            elif kind == "Canvas":
                for it in ch.find_all():
                    if ch.type(it) == "text":
                        txt += str(ch.itemcget(it, "text"))
            if not txt:
                continue
            key = None
            if txt.startswith("[") and "]" in txt:
                key = txt[1:txt.index("]")]
            label = txt.split("] ", 1)[1] if key else txt
            out[label] = (key, ch)
    return out


def keys_of(app) -> dict:
    return {k: v for k, v in app.keymap.items() if k != G.REFUSE_KEY}


def plan_at(i: int):
    return G.TRAP_PLAN[i % len(G.TRAP_PLAN)]


def play(app, key: str) -> None:
    fn = app.keymap.get(key)
    if fn is None:
        app.result = app.result  # nothing armed: the move is a no-op, as on screen
        return
    fn()


def part_a() -> None:
    app, _st, _ev = fresh()
    seen_verdicts: list = []
    for i in range(len(G.TRAP_PLAN)):
        cls, variant = plan_at(i)
        pump(app, 0.05)
        truth = app.task.get("truth") or {}
        got_cls, got_var = truth.get("class"), truth.get("variant")
        print("--- task %d  %s/%s  truth=%s want=%r" % (
            i, cls, variant, truth.get("truth_class"), truth.get("want")))
        check(got_cls == cls and got_var == variant,
              "plan matches the built task", "%s/%s" % (got_cls, got_var))
        ctrl = controls(app)
        km = keys_of(app)
        check(G.REFUSE_KEY in app.keymap, "refuse key armed on every trap task")
        tc, want = truth.get("truth_class"), truth.get("want")

        if cls == "swap_mid_task":
            # phase A: hit the wanted label, then let the swap fire, then hit B
            lab2key = {lab: k for lab, (k, _w) in ctrl.items() if k}
            key_a = lab2key.get(want)
            check(key_a is not None, "phase A: the wanted label carries a key", repr(want))
            if key_a:
                play(app, key_a)
            check(app.result == "none",
                  "a correct phase-A hit does not score by itself", app.result)
            pump(app, 1.20)
            truth_b = app.task.get("truth") or {}
            check(truth_b.get("want") != want and app.task.get("ask", "").endswith(
                str(truth_b.get("want"))),
                "the task was re-rolled in place", "%r -> %r" % (want, truth_b.get("want")))
            ctrl_b = controls(app)
            lab2key_b = {lab: k for lab, (k, _w) in ctrl_b.items() if k}
            key_b = lab2key_b.get(truth_b.get("want"))
            check(key_b is not None, "phase B: the wanted label carries a key")
            if key_b:
                play(app, key_b)
            check(app.result == "ok", "the final ask was answered", app.result)
            check(bool((app.detail or {}).get("a_hit")) is True,
                  "the phase-A hit is carried into the verdict", repr(app.detail))
        else:
            lab2key = {lab: k for lab, (k, _w) in ctrl.items() if k}
            if tc == "answerable":
                check(want in lab2key, "the wanted label is a real control with a key",
                      repr(want))
                if want in lab2key:
                    play(app, lab2key[want])
                check(app.result == "ok", "the right control is scored right", app.result)
            else:
                asked = None
                ask = app.task.get("ask", "")
                if ask.startswith("click the button labelled "):
                    asked = ask.split("labelled ", 1)[1].strip()
                if cls == "disabled":
                    check(asked in ctrl, "the asked control is on screen", repr(asked))
                    w = ctrl.get(asked, (None, None))[1]
                    check(w is not None and str(w.cget("state")) == "disabled",
                          "the asked control exists but is disabled", repr(asked))
                    check(asked not in lab2key,
                          "the disabled control carries no hint key", repr(asked))
                elif cls in ("prose_same_word", "bold_prose"):
                    check(asked is not None and asked not in lab2key,
                          "the asked word is prose, not a control", repr(asked))
                play(app, G.REFUSE_KEY)
                check(app.result == "ok", "refusing is scored right", app.result)
        seen_verdicts.append(app.result)
        pump(app, 0.12)          # let the verdict settle and the next task appear

    # a second pass: wrong moves must be wrong
    print("\n=== wrong moves ===")
    app2, _s2, _e2 = fresh()
    for i in range(len(G.TRAP_PLAN)):
        cls, variant = plan_at(i)
        pump(app2, 0.05)
        truth = app2.task.get("truth") or {}
        tc, want = truth.get("truth_class"), truth.get("want")
        skip = (want,)
        if cls == "swap_mid_task":
            pump(app2, 1.20)      # skip to phase B, then press a decoy
            # after the swap the decoy must avoid BOTH targets: A's is stale, B's is right
            skip = (want, (app2.task.get("truth") or {}).get("want"))
        ctrl = controls(app2)
        lab2key = {lab: k for lab, (k, _w) in ctrl.items() if k}
        decoy = [lab for lab in lab2key if lab not in skip]
        if tc == "answerable":
            if decoy:
                play(app2, lab2key[decoy[0]])
            check(app2.result == "wrong", "%s: a decoy is scored wrong" % cls,
                  "%s -> %s" % (decoy[:1], app2.result))
        else:
            if decoy:
                play(app2, lab2key[decoy[0]])
                check(app2.result == "wrong",
                      "%s: pressing any control is false_accept" % cls, app2.result)
        pump(app2, 0.12)

    print("\n=== false refusal: F8 on an answerable task must lose ===")
    app3, _s3, _e3 = fresh()
    # task 0 of the plan is answerable by construction
    cls0, var0 = plan_at(0)
    check((app3.task.get("truth") or {}).get("truth_class") == "answerable",
          "task 0 is answerable", "%s/%s" % (cls0, var0))
    play(app3, G.REFUSE_KEY)
    check(app3.result == "wrong", "refusing when the control exists is scored wrong",
          app3.result)
    print("\nverdicts seen in pass 1: %s" % json.dumps(seen_verdicts))


def part_b() -> None:
    """F8 must reach the app through the same posted-key channel the driver uses."""
    print("\n=== e2e: F8 through dsh-actor (background) ===")
    d = tempfile.mkdtemp(prefix="trap-e2e-")
    st, ev = os.path.join(d, "state.json"), os.path.join(d, "events.jsonl")
    py = sys.executable
    proc = subprocess.Popen([py, os.path.join(HERE, "gym_app.py"), "--seed", "20251007",
                             "--state", st, "--events", ev, "--scenario", "t_trap",
                             "--gap", "200", "--no-topmost"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    rc = 0
    try:
        time.sleep(3.0)
        act = os.path.join(os.path.dirname(os.path.dirname(HERE)), "dsh-vision-kit",
                           "actor", "act.cmd")
        if not os.path.exists(act):
            act = r"D:\DSH\dsh-vision-kit\actor\act.cmd"
        # window mode=front is *not* used: the point is that a background key works.
        # bg+focus must ride in the SAME request: Tk drops posted keys in the gap
        # between a separate focus call and the post.
        infop = os.path.join(d, "info.json")
        with open(infop, "w", encoding="utf-8") as fh:
            json.dump({"op": "window", "mode": "info"}, fh)
        ri = subprocess.run(["cmd", "/c", act, "run", infop],
                            capture_output=True, text=True, timeout=120)
        try:
            fg = str(json.loads(ri.stdout.strip().splitlines()[-1]).get("title") or "")
        except Exception:
            fg = ""
        if "Lock" in fg or "锁屏" in fg:
            print("SKIP e2e: the session is locked (foreground %r)" % fg)
            return
        reqp = os.path.join(d, "req.json")
        with open(reqp, "w", encoding="utf-8") as fh:
            json.dump({"op": "run", "steps": [{"op": "key", "keys": "F8", "bg": True,
                                               "title_contains": "GUI Gym",
                                               "focus": True}]}, fh)
        r = subprocess.run(["cmd", "/c", act, "run", reqp],
                           capture_output=True, text=True, timeout=120)
        print(r.stdout[-400:] or r.stderr[-400:])
        time.sleep(0.6)
        events = []
        if os.path.exists(ev):
            with open(ev, encoding="utf-8") as fh:
                events = [json.loads(x) for x in fh if x.strip()]
        keys = [e for e in events if e.get("event") == "key"]
        f8 = [e for e in keys if e.get("ks") == "F8"]
        check(bool(f8), "the app's event stream saw F8",
              repr(f8[-1].get("hit") if f8 else None))
        done = [e for e in events if e.get("event") == "done"]
        check(bool(done), "the app scored the task", repr(done[-1].get("result") if done
                                                          else None))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--e2e", action="store_true", help="also check F8 over the real channel")
    a = ap.parse_args()
    part_a()
    if a.e2e:
        part_b()
    print("\n%s" % ("ALL OK" if not FAILS else "FAILED: %s" % json.dumps(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
