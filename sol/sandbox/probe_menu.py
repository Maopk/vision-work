"""One-off: how to read tk menubar labels reliably."""
import json
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

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
                         "--scenario", "t_menu", "--seed", "777",
                         "--state", STATE, "--gap", "900"], cwd=HERE,
                        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
time.sleep(2.5)
try:
    d = Driver(Actor(), STATE)
    img = d.shot()
    st = json.load(open(STATE, encoding="utf-8"))
    print("ask:", st["ask"], "| truth:", st["truth"])
    my0, my1 = d.menu_band(img)
    print("band", my0, my1, "window", img.size)
    band = img.crop((0, my0, img.width, my1))
    band.resize((band.width * 2, band.height * 2)).save("probe-band-2x.png")
    band.save("probe-band.png")
    for psm in ("11", "7", "6"):
        for sc in (1, 2, 3):
            im = band if sc == 1 else band.resize((band.width * sc, band.height * sc))
            w = G.ocr_words(im, psm=psm, min_conf=20.0)
            print("psm %s scale %d -> %s" % (psm, sc, [(x["text"], round(x["conf"])) for x in w]))
    # ink blobs = labels (dark text on the light menubar)
    g = np.asarray(band.convert("L"))
    blobs = G.components(g < 140, min_area=12)
    print("blobs:", [(a, b) for a, b in blobs][:8])
    for area, (y0, x0, y1, x1) in blobs[:6]:
        if (x1 - x0) < 4 or (y1 - y0) < 6:
            continue
        box = band.crop((max(x0 - 3, 0), max(y0 - 3, 0), x1 + 4, y1 + 4))
        px = box.resize((box.width * 4, box.height * 4))
        txt, conf = G.read_box(px, (0, 0, px.width, px.height), psm="7", scale=1)
        print("  blob w=%d h=%d -> %r %s" % (x1 - x0, y1 - y0, txt, conf))
finally:
    proc.terminate()
