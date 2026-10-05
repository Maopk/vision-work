"""One-off: where is the Tk Scale trough, and what does the readout really say?

Vertical scan: at a fixed x inside the scale, click a series of y values and read the
readout after each. The y where the value starts moving is the trough.
"""
import json
import os
import re
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
                         "--scenario", "t_toggle", "--seed", "333", "--state", STATE,
                         "--gap", "9000"], cwd=HERE, stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT)
time.sleep(2.5)
try:
    d = Driver(Actor(), STATE)
    d.key("k")                                   # move off task 0
    time.sleep(0.8)
    st = json.load(open(STATE, encoding="utf-8"))
    print("task:", st["ask"], "| truth", st["truth"])
    img = d.shot()
    ask, body_top, band, ask_box = d.chrome(img)
    body = d.words(img, region=(0, body_top, img.width, img.height - body_top))
    print("body lines (box, text):")
    for line in G.group_lines(body):
        print("   ", line["box"], repr(line["text"])[:70])
    readout = None
    for line in G.group_lines(body):
        if re.match(r"^\s*value\s*\d+", line["text"], re.I):
            readout = line
    rx, ry, rw, rh = readout["box"]
    print("readout box", readout["box"])
    wide = (rx, ry - 4, rw + 60, rh + 8)
    a = img.crop((wide[0], wide[1], wide[0] + wide[2], wide[1] + wide[3]))
    a.resize((a.width * 4, a.height * 4)).save("probe-readout-zoom.png")
    for psm in ("7", "6", "8", "13"):
        print("   own OCR psm", psm, "->", G.read_box(img, wide, psm=psm, scale=4))
        print("   whitelist psm", psm, "->", G.read_box(img, wide, whitelist="0123456789",
                                                        psm=psm, scale=4))
    # vertical scan: which y actually moves the value?
    print("vertical scan at x = rx+300 (value after each click):")
    for dy in (-10, -20, -30, -38, -46, -54, -62, -72, -84):
        cx, cy = d.screen((rx + 300, ry + dy))
        d.click(cx, cy)
        time.sleep(0.15)
        img2 = d.shot()
        print("   y = ry%+4d (=%4d) -> targeted %s | full-body %s"
              % (dy, ry + dy, d.read_value(img2, wide), d.read_slider(img2, body_top)))
    img2.save("probe-toggle-window.png")
    print("saved probe-readout-zoom.png, probe-toggle-window.png")
finally:
    proc.terminate()
