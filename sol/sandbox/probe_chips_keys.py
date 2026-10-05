"""Which key does what on a t_chips screen, and what does the app say back?

The chip hints are drawn under each disc, but reading them off the body pass proved
unreliable, so this probe asks the app itself: press keys in order and print the key
line it answers with ("carrying chip N - now press a slot key" proves which key
picked which chip; a slot key answers differently).

    python probe_chips_keys.py [seed]
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gym_run as R                                        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
SEED = sys.argv[1] if len(sys.argv) > 1 else "20251007"
STATE = os.path.join(HERE, "probe-chips-state.json")
EVENTS = os.path.join(HERE, "probe-chips-events.jsonl")


def keyline(d):
    img = d.shot()
    out = []
    for psm in ("7", "11"):
        ws = d.words(img, region=(0, img.height - 60, img.width, 60), psm=psm, min_conf=15.0)
        out.append(" ".join(w["text"] for w in ws))
    return out


def main() -> int:
    for p in (STATE, EVENTS):
        if os.path.exists(p):
            os.remove(p)
    app = subprocess.Popen([PY, "gym_app.py", "--scenario", "t_chips", "--seed", SEED,
                            "--state", STATE, "--events", EVENTS, "--gap", "100000",
                            "--no-topmost"], cwd=HERE)
    time.sleep(3.0)
    fg = R.foreground_via(R.Actor())
    d = R.Driver(R.Actor(), STATE, keys=True, bg=True)
    d.window_rect()
    d.a.run([{"op": "window", "mode": "bottom", "hwnd": d.hwnd}])
    if fg.get("hwnd"):
        d.a.run([{"op": "window", "mode": "front", "hwnd": fg["hwnd"]}])
    st = json.load(open(STATE, encoding="utf-8"))
    print("ask:", st.get("ask"), "| truth:", st.get("truth"), flush=True)
    img = d.shot()
    words = d.body_words(img, 90)
    print("body words:", [(w["text"], w["box"]) for w in words], flush=True)
    print("chip blobs:", d.chip_blobs(img, 90), flush=True)
    for k in "123456789":
        d.key(k)
        time.sleep(0.35)
        print("  pressed %s -> keyline %s" % (k, keyline(d)), flush=True)
        st = json.load(open(STATE, encoding="utf-8"))
        if st.get("result") != "none":
            print("  judged:", st.get("result"), st.get("detail"), flush=True)
            break
    app.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
