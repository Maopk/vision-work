"""Look at the banner after a live change - pixels first, no guessing.

The chaos run read "click the button labelled" with the label missing on three
tasks in a row, so dump the actual band: raw rows, both OCR polarities, the
driver's own chrome() verdict, and a PNG to look at.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import gui_see as G
from gym_run import Driver
from loop import Actor

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable


def band_report(d: Driver, img: Image.Image) -> None:
    g = np.asarray(img.convert("L"), dtype=np.int16)
    darkfrac = (g < 100).mean(axis=1)
    nd = (g >= 100).sum(axis=1)
    rows = [y for y in range(0, 220)]
    print("  row profile (y: darkfrac, light-pixels):")
    for y in rows:
        if darkfrac[y] > 0.02 or nd[y] > 6:
            print("    %3d  dark=%.2f  light=%4d" % (y, darkfrac[y], nd[y]))
    ask, body_top, band, ask_box = d.chrome(img)
    print("  chrome() -> ask=%r body_top=%s band=%s ask_box=%s" % (ask, body_top, band, ask_box))
    for inv in (False, True):
        ws = d.words(img, invert=inv, region=(0, band[0] - 6, img.width, band[1] - band[0] + 12))
        print("  %s band words: %s" % ("inverted" if inv else "normal",
                                       [w["text"] for w in ws]))
    txt, _ = G.read_box(img.crop((0, band[0], img.width, band[1])), (0, 0, img.width,
                                                                    band[1] - band[0]),
                        psm="7", scale=2)
    print("  whole-band OCR psm7 x2: %r" % txt)
    inv = Image.fromarray(255 - np.asarray(img.crop((0, band[0], img.width, band[1])))
                          .astype(np.uint8))
    txt2, _ = G.read_box(inv, (0, 0, img.width, band[1] - band[0]), psm="7", scale=2)
    print("  inverted-band OCR psm7 x2: %r" % txt2)


def main() -> int:
    state = os.path.join(HERE, "probe-chaos-state.json")
    events = os.path.join(HERE, "probe-chaos-events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([PY, os.path.join(HERE, "gym_app.py"), "--scenario", "t_button",
                             "--seed", "777", "--state", state, "--events", events,
                             "--chaos", "1.0", "--chaos-ms", "100,300"],
                            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(3.0)
    d = Driver(Actor(), state, verbose=False)
    try:
        img = d.shot()
        img.save(os.path.join(HERE, "probe-chaos.png"))
        st = json.load(open(state, encoding="utf-8"))
        print("state ask   : %r" % st.get("ask"))
        print("state task_i: %s   result=%s" % (st.get("task_i"), st.get("result")))
        band_report(d, img)
        print("--- 2.5 s later ---")
        time.sleep(2.5)
        img2 = d.shot()
        img2.save(os.path.join(HERE, "probe-chaos-2.png"))
        print("state ask   : %r" % json.load(open(state, encoding="utf-8")).get("ask"))
        band_report(d, img2)
    finally:
        proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
