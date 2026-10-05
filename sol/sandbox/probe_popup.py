"""One-off: does a click on a tk menubar label actually post a drop-down, and what
does it look like on screen?  Uses raw actor shots (no window-front step, which may
itself dismiss a posted menu)."""
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
proc = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                         "--scenario", "t_menu", "--seed", "777", "--state", STATE,
                         "--gap", "9000"], cwd=HERE, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
time.sleep(2.5)
try:
    a = Actor()
    d = Driver(a, STATE)
    r = d.window_rect()
    print("rect", r, "state ask", json.load(open(STATE, encoding="utf-8"))["ask"])
    img = d.shot()
    my0, my1 = d.menu_band(img)
    mw = d.words(img, region=(0, my0, img.width, my1 - my0), psm="7", min_conf=25.0)
    print("menubar words", [(w["text"], w["box"]) for w in mw])
    menu = json.load(open(STATE, encoding="utf-8"))["truth"]["menu"]
    hit = d.find(mw, menu, 0.85)
    print("hit", hit)
    hx, hy = d.screen(hit["center"])
    probe = (max(hit["box"][0] - 20, 0), hit["box"][1] + 4,
             min(img.width, hit["box"][0] + 420), min(img.height, hit["box"][1] + 70))
    before = img.crop(probe)
    d.click(hx, hy)
    time.sleep(0.5)
    # raw shot: no window-front step, so nothing can steal focus from the popup
    raw = os.path.join(HERE, "probe-popup-window.png")
    a.run([{"op": "shot", "path": raw, "region": [r[0], r[1], r[2], r[3]]}])
    from PIL import Image
    after = Image.open(raw).convert("RGB")
    print("probe box", probe, "diff_frac", round(G.diff_frac(before, after.crop(probe)), 4))
    after.crop(probe).resize(((probe[2] - probe[0]) * 2, (probe[3] - probe[1]) * 2)).save(
        "probe-popup-strip.png")
    wide = (max(hx - 40, 0), hy + 8, min(hx + 460, 2559), min(hy + 560, 1599))
    raw2 = os.path.join(HERE, "probe-popup-region.png")
    a.run([{"op": "shot", "path": raw2, "region": list(wide)}])
    print("wide region", wide)
finally:
    proc.terminate()
