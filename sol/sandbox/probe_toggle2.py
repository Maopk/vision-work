"""One-off: why does the same slider click read a different value every attempt?

Reproduces the suite's stuck task (seed 333 -> task 1 = "prism OFF ... slider to 9")
by skipping task 0, then dumps the layout and scans the trough.
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
    st = json.load(open(STATE, encoding="utf-8"))
    print("task0:", st["ask"])
    d.key("k")                                   # skip to the next task
    time.sleep(1.0)
    st = json.load(open(STATE, encoding="utf-8"))
    print("task1:", st["ask"], "| truth", st["truth"])
    img = d.shot()
    ask, body_top, band, ask_box = d.chrome(img)
    body = d.words(img, region=(0, body_top, img.width, img.height - body_top))
    readout = None
    for line in G.group_lines(body):
        if re.match(r"^\s*value\s*\d+", line["text"], re.I):
            readout = line
    rx, ry, rw, rh = readout["box"]
    print("readout line", repr(readout["text"]), "box", readout["box"])
    img.crop((0, max(0, ry - 120), img.width, ry + 40)).save("probe-scale.png")
    print("scan (fresh readout box each time):")
    for dx in [40, 100, 160, 200, 240, 280, 302, 340, 400]:
        cx, cy = d.screen((rx + dx, ry - 46))
        d.click(cx, cy)
        time.sleep(0.15)
        img2 = d.shot()
        got = d.read_value(img2, readout["box"])
        got2 = d.read_slider(img2, body_top)
        print("   dx=%+4d screen=(%d,%d) value=%s (full-body read: %s)"
              % (dx, cx, cy, got, got2))
    # and once more with the *original* box after re-reading the body
    body2 = d.words(img2, region=(0, body_top, img2.width, img2.height - body_top))
    for line in G.group_lines(body2):
        if re.match(r"^\s*value\s*\d+", line["text"], re.I):
            print("re-read readout line", repr(line["text"]), "box", line["box"])
    st2 = json.load(open(STATE, encoding="utf-8"))
    print("app result now:", st2.get("result"), st2.get("detail"))
finally:
    proc.terminate()
