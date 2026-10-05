"""Look at one t_chips task with the driver's own eyes: what blobs, what words.

    python probe_chips.py [seed]

Checks the two things the driver gets wrong on this scenario:
  * the chip number printed in white on a saturated circle,
  * the code printed next to "SLOT", which tesseract reads at this size as
    "88V" -> "0QP" (3 confusions in 3 characters).
Ground truth comes from the app's own state file, so the reads can be graded.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

import gym_run as R
import gui_see as G

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def try_chip(img, box, tag):
    """White glyphs on a saturated disc: threshold luminance, drop the bbox corners."""
    x0, y0, x1, y1 = box
    crop = img.crop((x0, y0, x1 + 1, y1 + 1)).convert("L")
    a = np.asarray(crop)
    h, w = a.shape
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    yy, xx = np.mgrid[0:h, 0:w]
    inside = ((yy - cy) ** 2 + (xx - cx) ** 2) < (0.47 * min(h, w)) ** 2
    text = (a > 185) & inside
    out = np.where(text, 0, 255).astype(np.uint8)
    im = Image.fromarray(out)
    res = []
    for scale in (3, 5, 8):
        for psm in ("7", "10", "8"):
            txt, _ = G.read_box(im, (0, 0, w, h), whitelist="0123456789", psm=psm,
                                scale=scale)
            digits = "".join(ch for ch in txt if ch.isdigit())
            res.append((scale, psm, digits))
    print("   %-12s ink=%-5d %s" % (tag, int(text.sum()),
                                    "  ".join("s%d/psm%-2s=%s" % r for r in res)))
    return res


def main() -> int:
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 333
    state = os.path.join(HERE, "_probe_chips_state.json")
    events = os.path.join(HERE, "_probe_chips_events.jsonl")
    for f in (state, events):
        if os.path.exists(f):
            os.unlink(f)
    proc = subprocess.Popen([PY, os.path.join(HERE, "gym_app.py"), "--state", state,
                             "--events", events, "--gap", "300", "--seed", str(seed),
                             "--scenario", "t_chips"],
                            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        time.sleep(2.5)
        d = R.Driver(R.Actor(), state)
        img = d.shot()
        img.save(os.path.join(HERE, "probe-chips.png"))
        st = d.state()
        task = st.get("task") or {}
        truth = task.get("truth") or {}
        print("ask      :", task.get("ask"))
        print("truth    :", json.dumps(truth, ensure_ascii=False)[:200])
        body_top = d.chrome(img)[1]
        print("rect     :", d.window_rect(), " body_top:", body_top)

        print("\nchips:")
        blobs = d.chip_blobs(img, body_top)
        for b in blobs:
            print("   blob value=%-5s center=%-14s box=%s" % (b.get("value"), b.get("center"),
                                                              b.get("box")))
        a = np.asarray(img).astype(np.int16)
        sat = (a.max(axis=2) - a.min(axis=2)) > 70
        for area, (y0, x0, y1, x1) in G.components(sat, min_area=1200)[:8]:
            if (x1 - x0) < 30 or (y1 - y0) < 30 or y0 < body_top:
                continue
            try_chip(img, (x0, y0, x1, y1), "blob(%d,%d)" % (x0, y0))

        print("\nslot codes (truth %r):" % truth.get("slot"))
        words = d.words(img, region=(0, body_top, img.width, img.height - body_top))
        slot_w = next((w for w in words
                       if w["text"].strip().upper().startswith("SLOT")), None)
        if not slot_w:
            print("   no SLOT word found; words =", [w["text"] for w in words][:20])
        else:
            sx, sy, sw, sh = slot_w["box"]
            mid = sy + sh / 2.0
            cands = [w for w in words if w is not slot_w and w["box"][0] >= sx + sw - 3
                     and abs((w["box"][1] + w["box"][3] / 2.0) - mid) < max(sh, 10)
                     and w["box"][0] - (sx + sw) < 60]
            cands.sort(key=lambda w: w["box"][0])
            if not cands:
                print("   SLOT word at %s has no neighbour; words = %s"
                      % (slot_w["box"], [w["text"] for w in words][:20]))
            for cw in cands[:3]:
                cx, cy, cww, chh = cw["box"]
                box = (max(cx - 4, 0), max(cy - 4, 0), cww + 8, chh + 8)
                print("   word OCR %r box=%s" % (cw["text"], cw["box"]))
                for scale in (3, 6, 9):
                    for psm in ("7", "8", "13"):
                        txt, _ = G.read_box(img, box, whitelist=ALPHA, psm=psm, scale=scale)
                        print("      scale=%d psm=%-2s -> %r" % (scale, psm, txt))
    finally:
        proc.terminate()
    return 0


if __name__ == "__main__":
    sys.exit(main())
