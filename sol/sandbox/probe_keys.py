"""Does the keyboard channel work while the gym sits in the background?

The app is started, pushed to the bottom of the z-order, read through PrintWindow
and driven with posted WM_KEYDOWN messages - the foreground is never touched.

    python probe_keys.py [scenario] [seed]

It prints what the driver can see (ask + words with boxes), which hint it picked
off the screen, and what the app recorded afterwards.
"""
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gui_see as G                                    # noqa: E402
from gym_run import Driver                             # noqa: E402
from loop import Actor                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
HINT_RE = re.compile(r"^[\[\(<]?\s*([0-9A-Za-z])\s*[\]\)>]?$")


def hints_of(ws):
    """[(hint char, word, box)] for every word that looks like a hint token."""
    out = []
    for w in ws:
        m = HINT_RE.match((w["text"] or "").strip())
        if m:
            out.append((m.group(1), w["text"], w["box"]))
    return out


def main() -> int:
    scen = sys.argv[1] if len(sys.argv) > 1 else "t_button"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 777
    state = os.path.join(HERE, "probe-state.json")
    events = os.path.join(HERE, "probe-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    cmd = [sys.executable, os.path.join(HERE, "gym_app.py"), "--state", state,
           "--events", events, "--gap", "300", "--seed", str(seed),
           "--scenario", scen, "--no-topmost"]
    proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    time.sleep(2.5)
    try:
        d = Driver(Actor(), state, bg=True)
        d.window_rect()
        d.a.run([{"op": "window", "mode": "bottom", "title_contains": d.title}])
        print("window origin=%s size=%s hwnd=%s" % (d.origin, d.size, d.hwnd))
        img = d.shot()
        img.save(os.path.join(HERE, "probe-keys.png"))
        ask, body, _band, _box = d.chrome(img)
        print("ask from screen: %r   body_top=%d" % (ask, body))
        ws = d.words(img, region=(0, body, img.width, img.height - body), psm="11")
        ws.sort(key=lambda w: (w["box"][1] // 10, w["box"][0]))
        print("body words: %d" % len(ws))
        for w in ws[:36]:
            print("   %-18r box=%s" % (w["text"], w["box"]))
        print("hint-shaped tokens:", [(h, t, b) for h, t, b in hints_of(ws)])
        chk = G.ocr_words(img, psm="7")
        print("whole-window psm7 words: %d" % len(chk))
        st = d.state()
        print("state: task_i=%s result=%s scenario=%s" %
              (st.get("task_i"), st.get("result"), st.get("scenario")))
        print("truth (scoring only):", st.get("truth"))
        # ---- act: find the target word, take the hint on its own line, post that key
        want = (ask or "").split()[-1]
        hit = d.find(ws, want, 0.8)
        print("target word %r -> %s" % (want, hit and hit["box"]))
        picked = None
        if hit:
            ty, tx = hit["box"][1], hit["box"][0]
            cands = [(abs(b[1] - ty), b[0], h) for h, t, b in hints_of(ws) if abs(b[1] - ty) <= 14]
            cands.sort()
            picked = cands[0][2] if cands else None
        print("hint picked off the screen: %r" % picked)
        if picked:
            i0 = d.state().get("task_i")
            d.key(picked)
            time.sleep(1.2)
            st2 = d.state()
            print("after key %r -> task_i=%s result=%s detail=%s" %
                  (picked, st2.get("task_i"), st2.get("result"), st2.get("detail")))
            print("task advanced: %s" % (st2.get("task_i") != i0))
    finally:
        proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
