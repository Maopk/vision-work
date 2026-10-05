"""One-off: does the driver's wheel actually scroll the t_rows list?"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gui_see as G
from gym_run import Driver
from loop import Actor

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "gym-state.json")
for f in (STATE, os.path.join(HERE, "gym-events.jsonl")):
    if os.path.exists(f):
        os.unlink(f)
seed = sys.argv[1] if len(sys.argv) > 1 else "4242"
proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                         "--scenario", "t_rows", "--seed", seed, "--state", STATE,
                         "--gap", "9000"], cwd=HERE, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
time.sleep(2.5)
try:
    d = Driver(Actor(), STATE)
    st = json.load(open(STATE, encoding="utf-8"))
    tr = st["truth"]
    print("ask:", st["ask"], "| rows", tr["rows"], "row_h", tr["row_height"])
    img = d.shot()
    ask, body_top, band, ask_box = d.chrome(img)
    region = (0, body_top, img.width, img.height - body_top)
    for step in range(4):
        w = d.words(img, region=region, min_conf=25.0)
        ids = [x["text"] for x in w if x["text"].startswith("#") or (any(c.isdigit() for c in x["text"]) and len(x["text"]) >= 4)]
        print("step", step, "ids", ids[:16])
        if str(tr["id"]) in " ".join(ids):
            print("   -> target %s visible" % tr["id"])
        x, y = d.screen((img.width // 2, body_top + (img.height - body_top) // 2))
        print("   wheel at", (x, y))
        d.wheel(-3, img.width // 2, body_top + (img.height - body_top) // 2)
        time.sleep(0.35)
        img = d.shot()
finally:
    proc.terminate()
