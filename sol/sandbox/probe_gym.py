"""One-off: why did the gym click miss?  Prints the OCR map and the click point."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gui_see as G
from gym_run import Driver
from loop import Actor

d = Driver(Actor(), os.path.join(os.path.dirname(os.path.abspath(__file__)), "gym-state.json"))
print("rect", d.window_rect())
img = d.shot()
img.save("_gym_dbg.png")
ask, body_top, band = d.chrome(img)
print("ask from screen:", repr(ask), " body_top", body_top)
body = d.words(img, region=(0, body_top, img.width, img.height - body_top))
for it in sorted(body, key=lambda w: (w["box"][1], w["box"][0])):
    print("   %-14r box=%-22s conf=%.0f" % (it["text"], it["box"], it["conf"]))
target = ask.split("labelled")[-1].strip()
hit = d.find(body, target, 0.82) or d.find(body, target, 0.7)
print("target", repr(target), "hit", hit)
state = json.load(open(d.state_path, encoding="utf-8"))
print("app truth:", json.dumps(state["truth"], ensure_ascii=False))
print("app layout:", state["layout"], " result:", state["result"])
if hit:
    x, y = d.screen(hit["center"])
    print("clicking screen", (x, y))
    d.click(x, y)
    time.sleep(0.8)
    st2 = json.load(open(d.state_path, encoding="utf-8"))
    print("after click: result=%s detail=%s" % (st2["result"], json.dumps(st2["detail"], ensure_ascii=False)))
