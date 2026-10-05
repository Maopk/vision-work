"""One-off: find a click the gym app actually reacts to."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gym_run import Driver
from loop import Actor

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "gym-state.json")
d = Driver(Actor(), STATE)
print("rect", d.window_rect())
img = d.shot()
ask, body_top, band = d.chrome(img)
body = d.words(img, region=(0, body_top, img.width, img.height - body_top))
target = ask.split("labelled")[-1].strip()
hit = d.find(body, target, 0.7)
print("ask", repr(ask), "hit", hit)


def st():
    return json.load(open(STATE, encoding="utf-8"))


bx, by, bw, bh = hit["box"]
sx, sy = d.screen((bx + bw // 2, by + bh // 2))
print("clicking", (sx, sy))
d.click(sx, sy)
time.sleep(0.8)
print("state:", st()["result"], json.dumps(st()["detail"], ensure_ascii=False)[:120])
if st()["result"] == "none":
    rep = d.a.run([{"op": "click", "target": {"xy": [sx, sy]}, "front_title": "GUI Gym"}],
                  results=True)
    print("raw reply:", json.dumps(rep, ensure_ascii=False)[:600])
