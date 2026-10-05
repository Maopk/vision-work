"""Watch the practice target arm its row badges while a rebuild chaos runs.

    python probe_rebuild_rows.py

Starts a t_rows target with --chaos 1.0 --chaos-kind rebuild, then prints every
`rowkeys` event the app emits (armed / rows / first_y / last_y / canvas height)
and, after poking it with page keys through the actor, prints what changed. The
question it answers: does a rebuilt row table ever get its hint badges again?
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

from gym_run import Actor, Driver, kill_stale          # noqa: E402

PY = sys.executable
STATE = os.path.join(HERE, "_probe-rebuild-state.json")
EVENTS = os.path.join(HERE, "_probe-rebuild-events.jsonl")


def read_events():
    out = []
    if not os.path.exists(EVENTS):
        return out
    with open(EVENTS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def show(tag):
    evs = read_events()
    rows = [e for e in evs if e.get("event") == "rowkeys"]
    print("--- %s: %d events, %d rowkeys" % (tag, len(evs), len(rows)))
    for e in evs:
        if e.get("event") in ("task", "verdict", "chaos"):
            print("    %-8s i=%s %s" % (e.get("event"), e.get("task_i"),
                                        (e.get("ask") or "")[:44]))
    for e in rows:
        print("    rowkeys  i=%s armed=%s rows=%s first=%s last=%s ask=%s"
              % (e.get("task_i"), e.get("armed"), e.get("rows"), e.get("first_y"),
                 e.get("last_y"), (e.get("ask") or "")[-24:]))


def main():
    for f in (STATE, EVENTS):
        if os.path.exists(f):
            os.unlink(f)
    kill_stale(STATE)
    cmd = [PY, os.path.join(HERE, "gym_app.py"), "--state", STATE, "--events", EVENTS,
           "--gap", "300", "--seed", "20251007", "--scenario", "t_rows",
           "--chaos", "1.0", "--chaos-kind", "rebuild", "--no-topmost"]
    proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    try:
        time.sleep(4.0)
        show("after rebuild")
        d = Driver(Actor(), STATE, title="GUI Gym", verbose=False, bg=True, keys=True)
        d.window_rect()
        for i in range(3):
            d.key("Next")
            time.sleep(0.6)
            show("after Next #%d" % (i + 1))
        d.key("Home")
        time.sleep(0.6)
        show("after Home")
        st = json.load(open(STATE, encoding="utf-8"))
        print("truth:", json.dumps(st.get("truth"), ensure_ascii=False)[:200])
        print("ask:", st.get("ask"))
    finally:
        proc.terminate()
        time.sleep(0.6)


if __name__ == "__main__":
    main()
