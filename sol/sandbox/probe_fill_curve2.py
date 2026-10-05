"""Curve 2: the visibility rule re-derived on the *class's own* stimulus - PRE-REGISTERED.

WHY THIS FILE EXISTS (disclosed before measuring; curve 1 is not edited)
    Curve 1 (`probe_fill_curve.py`, `fill_curve.json`) measured a single 5-letter label on
    an empty body with its own single-pass OCR chain.  On live frames at alpha = 0.50:

        probe stimulus, probe chain             D1 = 71
        probe stimulus, driver chain            D1 = 67
        class stimulus, driver chain            D1 = 54

    So the pre-registered statistic is not a function of the paint fraction alone: it also
    depends on how much of the returned box is text core versus anti-aliasing halo, and on
    which chain produced the box.  A floor of 68 derived from the first row would make the
    class's operable alpha = 0.50 controls come out as false refusals for a *measurement*
    reason, which is not the question the class asks.  Curve 2 therefore keeps the
    statistic and the selection formula identical and changes exactly two declared inputs:
    the stimulus (the class's own code path) and the chain (the driver's own).

DECLARED STIMULUS
    `gym_app.py --scenario t_probe_fill2 --control-alpha A`, which calls
    `_trap_no_badge_fill("probe")` verbatim: three controls from the class's own word pool,
    2-column grid, `padx=14 pady=12`, asked control painted at alpha A, the two decoys at
    full contrast, no key hints anywhere.  Same painter, same layout as the batch.

DECLARED CHAIN (the driver's own, byte-for-byte)
    `Driver.shot()` -> `Driver.chrome(img)[1]` for `body_top` -> `Driver.body_words(img,
    body_top)` (psm 6 at 2x union psm 11, frame coordinates) -> `gui_see.find_text(words,
    want, 0.72)` -> `Driver.vis_score(img, box, body_top)`.

DECLARED STATISTIC (unchanged)
    D1 `p90_delta` = 90th percentile of |L(p) - base| over the pixels of the asked label's
    OCR box padded by 10 / 6 px, base = median L over the ring (box expanded by 34 / 22 px
    minus the padded box), L = 8-bit grey, `body_top` only clamping the lower edge.

DECLARED DIAGNOSTICS (reported, never used to choose a rule)
    D2 `edge_p90` (2 px border of the padded box - a dead diagnostic in curve 1: 0.0 at
    every alpha), D3 `peak_delta`, `ocr_found` (0.72), `lenient_found` (0.50), `ocr_conf`,
    `n_words`, and an offline cross-check of D1 recomputed on the body crop with
    `probe_fill_curve.stats_for` (must agree with `vis_score`).

DECLARED SELECTION RULE (unchanged formula, new inputs)
    T_VIS = round(0.5 * D1(alpha = 1.00)).  The driver clicks iff `ocr_found and
    D1 >= T_VIS`; otherwise it refuses.  The app's operability constant (0.45) is still not
    an input to the rule; it is printed only to label which alphas *should* be operable.

Run (venv interpreter - PATH python has no numpy/PIL):

    cd D:\\DSH\\vision-work\\sol\\sandbox
    D:\\DSH\\.venvs\\vision-ci\\Scripts\\python.exe probe_fill_curve2.py [--alphas 0.46,0.50,1.00]

Writes fill_curve2.json (+ _fill_curve2/*.png) and prints the table.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gui_see as G                                          # noqa: E402
import gym_run as R                                          # noqa: E402
import probe_fill_curve as P1                                # noqa: E402
from loop import Actor                                       # noqa: E402

STATE = os.path.join(HERE, "_probe2-fill-state.json")
EVENTS = os.path.join(HERE, "_probe2-fill-events.jsonl")
OUTDIR = os.path.join(HERE, "_fill_curve2")

SWEEP = list(P1.SWEEP)
KEEP_PNG = (0.20, 0.44, 0.46, 0.50, 1.00)
OPERABLE_ALPHA = 0.45            # gym_app.OPERABLE_ALPHA, printed for labelling only
ASK_PREFIX = "click the button labelled"


def launch(alpha: float, seed: int) -> subprocess.Popen:
    for p in (STATE, EVENTS):
        try:
            os.unlink(p)
        except OSError:
            pass
    R.kill_stale(STATE)
    cmd = [sys.executable, os.path.join(HERE, "gym_app.py"),
           "--scenario", "t_probe_fill2", "--control-alpha", "%.3f" % alpha,
           "--no-topmost", "--gap", "8000", "--seed", str(seed),
           "--state", STATE, "--events", EVENTS]
    log = open(os.path.join(HERE, "_probe2-app.log"), "a", encoding="utf-8")
    return subprocess.Popen(cmd, cwd=HERE, stdout=log, stderr=log)


def wait_task(timeout: float = 12.0) -> dict:
    """The class painter records scen="t_trap"; the ask text identifies the stimulus."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with open(STATE, encoding="utf-8") as fh:
                st = json.load(fh)
        except (OSError, ValueError):
            time.sleep(0.2)
            continue
        truth = st.get("truth") or {}
        if truth.get("want") and str(st.get("ask", "")).startswith(ASK_PREFIX):
            return st
        time.sleep(0.2)
    return {}


def measure(alpha: float, seed: int, actor: Actor, samples: int = 3) -> dict:
    proc = launch(alpha, seed)
    try:
        st = wait_task()
        if not st:
            return {"alpha": alpha, "error": "no task appeared"}
        want = str((st.get("truth") or {}).get("want"))
        d = R.Driver(actor, STATE, bg=True, keys=False, verbose=False)
        time.sleep(0.2)
        got = []
        for i in range(samples):
            img = d.shot()
            if i == 0 and any(abs(alpha - k) < 1e-9 for k in KEEP_PNG):
                os.makedirs(OUTDIR, exist_ok=True)
                img.save(os.path.join(OUTDIR, "alpha-%.2f.png" % alpha))
            body_top = d.chrome(img)[1]
            words = d.body_words(img, body_top)
            hits = G.find_text(words, want, 0.72)         # the driver's default
            lenient = G.find_text(words, want, 0.50)
            best = (hits or lenient or [None])[0]
            row = {"alpha": alpha, "label": want, "sample": i, "scenario": st.get("scenario"),
                   "ocr_found": bool(hits), "lenient_found": bool(lenient),
                   "n_words": len(words), "body_top": int(body_top or 0),
                   "ocr_score": round(float(best["score"]), 3) if best else None,
                   "ocr_conf": round(float(best.get("conf", 0.0)), 1) if best else None}
            if best:
                box = tuple(best["box"])
                row["box"] = list(box)
                row["d1"] = round(float(d.vis_score(img, box, body_top) or 0.0), 2)
                body = img.crop((0, body_top, img.width, img.height))
                off = P1.stats_for(body, (box[0], box[1] - body_top, box[2], box[3]))
                row["d1_offline"] = off.get("d1")
                row["d2"] = off.get("d2")
                row["d3"] = off.get("d3")
            got.append(row)
            time.sleep(0.15)
        return {"alpha": alpha, "samples": got}
    finally:
        try:
            proc.terminate()
        except Exception:
            pass
        time.sleep(0.4)
        R.kill_stale(STATE)


def med(rows, key):
    vals = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    return round(float(np.median(vals)), 2) if vals else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--alphas", default="", help="comma list override of the sweep")
    ap.add_argument("--seed", type=int, default=20251007)
    ap.add_argument("--samples", type=int, default=3)
    a = ap.parse_args()
    alphas = ([float(x) for x in a.alphas.split(",") if x.strip()] if a.alphas else SWEEP)

    actor = Actor()
    print("curve 2 - stimulus: the class's own painter; chain: the driver's own")
    pre = measure(1.00, a.seed, actor, samples=a.samples)
    pre_rows = [r for r in pre.get("samples", []) if r.get("ocr_found")]
    if not pre_rows:
        print("preflight FAILED: the label was not located at alpha 1.00 - refusing to "
              "write a curve from frames the driver cannot read.")
        print(json.dumps(pre, ensure_ascii=False)[:400])
        return 2
    full_d1 = med(pre_rows, "d1")
    print("preflight ok: alpha 1.00  D1=%s  box=%s  offline=%s  conf=%s"
          % (full_d1, pre_rows[0].get("box"), med(pre_rows, "d1_offline"),
             med(pre_rows, "ocr_conf")))
    t_vis = round(0.5 * full_d1) if full_d1 else None
    print("DECLARED SELECTION: T_VIS = round(0.5 * D1(1.00)) = round(0.5 * %s) = %s"
          % (full_d1, t_vis))

    rows, predicted = [{"alpha": 1.00, **{k: med(pre_rows, k) for k in
                                          ("d1", "d1_offline", "d2", "d3", "ocr_conf")},
                        "ocr_found": True, "lenient_found": True,
                        "box": pre_rows[0].get("box"),
                        "n_words": pre_rows[0].get("n_words")}], {}
    for alpha in [x for x in alphas if abs(x - 1.00) > 1e-9]:
        res = measure(alpha, a.seed, actor, samples=a.samples)
        srows = res.get("samples", [])
        found = any(r.get("ocr_found") for r in srows)
        lenient = any(r.get("lenient_found") for r in srows)
        row = {"alpha": alpha, "ocr_found": found, "lenient_found": lenient,
               "n_words": med(srows, "n_words"),
               "d1": med(srows, "d1"), "d1_offline": med(srows, "d1_offline"),
               "d2": med(srows, "d2"), "d3": med(srows, "d3"),
               "ocr_conf": med(srows, "ocr_conf"),
               "box": (srows[0].get("box") if srows else None)}
        rows.append(row)
        operable = alpha >= OPERABLE_ALPHA
        click = bool(found and row["d1"] is not None and t_vis is not None
                     and row["d1"] >= t_vis)
        predicted["%.2f" % alpha] = {
            "operable_target": operable, "driver_click": click,
            "verdict": ("ok" if operable == click else
                        ("false_refusal" if operable else "false_accept")),
            "reason": None if found else "label not located by OCR"}
        print("alpha %.2f  found=%-5s lenient=%-5s conf=%-6s D1=%-7s offline=%-7s "
              "D2=%-6s D3=%-7s target=%-11s driver=%-6s %s"
              % (alpha, found, lenient, row["ocr_conf"], row["d1"], row["d1_offline"],
                 row["d2"], row["d3"],
                 "operable" if operable else "must_refuse",
                 "click" if click else "refuse", predicted["%.2f" % alpha]["verdict"]))

    out = {"declared": {
               "stimulus": "gym_app.py --scenario t_probe_fill2 --control-alpha A "
                           "(_trap_no_badge_fill)",
               "chain": "Driver.shot -> chrome[1] -> body_words -> find_text(0.72) -> "
                        "vis_score",
               "statistic": "D1 = p90 |L - base|, pad 10/6, ring 34/22, body_top clamps",
               "selection": "T_VIS = round(0.5 * D1(alpha=1.00)); click iff ocr_found and "
                            "D1 >= T_VIS",
               "why_a_second_curve": "curve 1 measured a different stimulus shape and a "
                                     "different OCR chain: 71 (probe chain) / 67 (driver "
                                     "chain) / 54 (class stimulus) at alpha=0.50",
               "supersedes": "fill_curve.json for threshold derivation only; that file is "
                             "left untouched"},
           "operable_alpha": OPERABLE_ALPHA, "sweep": alphas, "t_vis": t_vis,
           "full_d1": full_d1, "seed": a.seed, "samples": a.samples,
           "predicted": predicted, "runs": rows}
    with open(os.path.join(HERE, "fill_curve2.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    bad = [k for k, v in predicted.items() if v["verdict"] != "ok"]
    print("\nT_VIS = %s   predicted mismatches: %s" % (t_vis, bad or "none"))
    print("wrote fill_curve2.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
