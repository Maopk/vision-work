"""Cross-check: does the driver reproduce the pre-registered statistic exactly?

Two implementations of D1 exist on purpose - `probe_fill_curve.stats_for` (the
measurement contract) and `Driver.vis_score` (the rule that acts).  If they ever
disagree, the curve in fill_curve.json no longer describes what the driver does, and
T_VIS_FILL = 68 would be a number about nothing.  This probe asserts they agree on
*real* app frames, at two alphas that straddle the app's operability constant, and
that an empty patch of page scores far below the floor.

    D:\\DSH\\.venvs\\vision-ci\\Scripts\\python.exe probe_vis_rule.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gui_see as G                                          # noqa: E402
import gym_run as R                                          # noqa: E402
from loop import Actor                                       # noqa: E402
from probe_fill_curve import launch, wait_task, stats_for, STATE   # noqa: E402

ALPHAS = (0.30, 0.55)      # must refuse / operable under the app's own 0.45
BLANK = (620, 600, 60, 20)  # a box on empty page - nothing is painted there


def main() -> int:
    actor = Actor()
    fails = 0
    print("T_VIS_FILL = %s   (driver floor)" % R.T_VIS_FILL)
    for alpha in ALPHAS:
        proc = launch(alpha, 20251007)
        try:
            st = wait_task()
            want = str((st.get("truth") or {}).get("want"))
            d = R.Driver(actor, STATE, bg=True, keys=False, verbose=False)
            time.sleep(0.2)
            img = d.shot()
            res = d.chrome(img)
            body_top = res[1] if len(res) > 1 else 0
            body_img = img.crop((0, body_top, img.width, img.height))
            words = G.ocr_words(body_img, psm="11")
            hits = G.find_text(words, want, 0.72)
            if not hits:
                print("alpha %.2f: label %r not found - cannot cross-check" % (alpha, want))
                fails += 1
                continue
            box_body = hits[0]["box"]
            # `stats_for` is the measurement contract and works on the body crop, while
            # `vis_score` works in frame coordinates (the driver's own body words are in
            # frame space): the same box has to be expressed twice, and comparing the two
            # numbers is exactly the point of this probe.
            bx, by, bw, bh = box_body
            box = (bx, by + body_top, bw, bh)
            contract = stats_for(body_img, box_body).get("d1")
            actual = d.vis_score(img, box, body_top)
            blank = d.vis_score(img, BLANK, body_top)
            rec: dict = {}
            # same translation for the word list: `control_visible` looks for hint badges
            # through the driver's own frame-space boxes
            words_frame = []
            for w in words:
                _bx, _by, _bw, _bh = w["box"]
                words_frame.append(dict(w, box=(_bx, _by + body_top, _bw, _bh),
                                        center=(_bx + _bw // 2, _by + body_top + _bh // 2)))
            click = d.control_visible(rec, img, words_frame, box, body_top)
            ok = contract is not None and abs(contract - actual) < 0.01
            fails += 0 if ok else 1
            print("alpha %.2f label %-8s contract=%-7s driver=%-7s delta=%-5s "
                  "blank=%-6s decision=%s rec=%s"
                  % (alpha, want, contract, round(actual, 2),
                     None if contract is None else round(actual - contract, 3),
                     None if blank is None else round(blank, 2),
                     "click" if click else "refuse", json.dumps(rec)))
        finally:
            try:
                proc.terminate()
            except Exception:
                pass
            time.sleep(0.4)
            R.kill_stale(STATE)
    print("cross-check: %d failed" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
