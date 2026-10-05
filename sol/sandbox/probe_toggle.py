"""One-off: calibrate the checkbox-indicator ink threshold + the Home/Right slider route."""
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gui_see as G
from gym_run import Driver, BG_RGB
from loop import Actor

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "gym-state.json")


def start(seed):
    for f in (STATE, os.path.join(HERE, "gym-events.jsonl")):
        if os.path.exists(f):
            os.unlink(f)
    p = subprocess.Popen([sys.executable, os.path.join(HERE, "gym_app.py"),
                          "--scenario", "t_toggle", "--seed", str(seed), "--state", STATE,
                          "--gap", "9000"], cwd=HERE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.STDOUT)
    time.sleep(2.5)
    return p


d = Driver(Actor(), STATE)
for seed in [int(x) for x in sys.argv[1:]] or [11, 22]:
    proc = start(seed)
    try:
        st = json.load(open(STATE, encoding="utf-8"))
        probe = st.get("truth") or {}
        print("== seed", seed, "ask:", st["ask"], "| truth", st["truth"])
        img = d.shot()
        ask, body_top, band, ask_box = d.chrome(img)
        body = d.words(img, region=(0, body_top, img.width, img.height - body_top))
        names = probe.get("names", [])
        for nm in names:
            lab = d.find(body, nm, 0.9)
            if not lab:
                print("   %-8s label not found" % nm)
                continue
            bx, by, bw, bh = lab["box"]
            cy = by + bh // 2
            vals = {}
            for dx, w in ((-26, 20), (-28, 24), (-24, 16)):
                vals["%d/%d" % (dx, w)] = round(G.ink(img, (bx + dx, cy - w // 2, w, w),
                                                      bg=BG_RGB, tol=45), 3)
            print("   %-8s box=%s ink %s %s" % (nm, (bx, by, bw, bh), vals,
                                                "<== the one asked" if nm == probe.get("which")
                                                else ""))
        readout = None
        for line in G.group_lines(body):
            if re.match(r"^\s*value\s*\d+", line["text"], re.I):
                readout = line
        print("   readout:", readout["text"] if readout else None,
              "| scale box guess near y", (readout["box"][1] - 46) if readout else None)
        if readout:
            rx, ry, rw, rh = readout["box"]
            print("   scan: click x -> value (readout box %s)" % (readout["box"],))
            for dx in range(-20, 461, 20):
                cx, cy = d.screen((rx + dx, ry - 46))
                d.click(cx, cy)
                time.sleep(0.12)
                print("      x=%+4d -> %s" % (dx, d.read_slider(d.shot(), body_top)))
            d.key("Home")
            time.sleep(0.15)
            print("   after Home : value", d.read_slider(d.shot(), body_top))
            d.key("Right", 7)
            time.sleep(0.15)
            print("   after 7xRight: value", d.read_slider(d.shot(), body_top))
    finally:
        proc.terminate()
        time.sleep(0.6)
