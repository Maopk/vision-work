"""Offline calibration of the driver-side visibility rule (batch 3) - PRE-REGISTERED.

Nothing below may be changed after the curve has been looked at.  The declarations were
written before the first measurement; the app's operability constant is NOT an input.

DECLARED STATISTIC (D1, primary)
    `p90_delta` = 90th percentile of |L(p) - base| over the pixels of the asked label's
    OCR box padded by PAD_X=10 / PAD_Y=6 px, where base = median L over the ring
    (the box expanded by 34 / 22 px minus the padded box) and L is 8-bit grey.
    It is computed on the driver's *body* crop only (the banner carries the same word at
    full contrast and would otherwise donate a perfect box).

DECLARED DIAGNOSTICS (reported, never used to choose a rule)
    D2 `edge_p90`  - same percentile over the 2 px border ring of the padded box.
    D3 `peak_delta` - max |L(p) - base| inside the padded box.
    `ocr_found`    - the driver's own locate step (gui_see.ocr_words psm 11, conf>=30,
                     then find_text at the driver's default 0.72) returns a hit.
    `ocr_conf`, `ocr_score`, `lenient_found` (min_score 0.5) - where the chain breaks.

DECLARED SELECTION RULE
    T_VIS = round(0.5 * D1(alpha = 1.00)), i.e. half the full-contrast statistic.
    The driver clicks iff `ocr_found and D1 >= T_VIS`; otherwise it refuses.

Run (must be the venv interpreter - PATH python has no numpy/PIL):

    cd D:\\DSH\\vision-work\\sol\\sandbox
    D:\\DSH\\.venvs\\vision-ci\\Scripts\\python.exe probe_fill_curve.py

Writes fill_curve.json (+ _fill_curve/*.png for four alphas) and prints the table.
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
from loop import Actor                                       # noqa: E402

STATE = os.path.join(HERE, "_probe-fill-state.json")
EVENTS = os.path.join(HERE, "_probe-fill-events.jsonl")
OUTDIR = os.path.join(HERE, "_fill_curve")

PAD_X, PAD_Y = 10, 6
RING_X, RING_Y = 34, 22
SWEEP = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.44, 0.46, 0.50,
         0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]
KEEP_PNG = (0.20, 0.44, 0.46, 1.00)


def clip_box(box, w, h):
    x, y, bw, bh = box
    x1, y1 = max(0, x - PAD_X), max(0, y - PAD_Y)
    x2, y2 = min(w, x + bw + PAD_X), min(h, y + bh + PAD_Y)
    return x1, y1, x2, y2


def stats_for(img: Image.Image, box) -> dict:
    """D1/D2/D3 on one OCR box, in the driver's own pixel space."""
    g = np.asarray(img.convert("L"), dtype=np.int16)
    h, w = g.shape
    x1, y1, x2, y2 = clip_box(box, w, h)
    rx1, ry1 = max(0, x1 - (RING_X - PAD_X)), max(0, y1 - (RING_Y - PAD_Y))
    rx2, ry2 = min(w, x2 + (RING_X - PAD_X)), min(h, y2 + (RING_Y - PAD_Y))
    ring = np.zeros_like(g, dtype=bool)
    ring[ry1:ry2, rx1:rx2] = True
    ring[y1:y2, x1:x2] = False
    if ring.sum() < 20 or (y2 - y1) < 3 or (x2 - x1) < 3:
        return {}
    base = float(np.median(g[ring]))
    inner = np.abs(g[y1:y2, x1:x2] - base).ravel()
    # the 2 px border of the padded box, i.e. what an edge test would look at
    edge = np.concatenate([
        np.abs(g[y1:y1 + 2, x1:x2] - base).ravel(),
        np.abs(g[max(y1, y2 - 2):y2, x1:x2] - base).ravel(),
        np.abs(g[y1:y2, x1:x1 + 2] - base).ravel(),
        np.abs(g[y1:y2, max(x1, x2 - 2):x2] - base).ravel()])
    return {"base": round(base, 1),
            "d1": round(float(np.percentile(inner, 90)), 2),
            "d2": round(float(np.percentile(edge, 90)), 2),
            "d3": round(float(inner.max()), 2),
            "px": int(inner.size)}


def launch(alpha: float, seed: int) -> subprocess.Popen:
    for p in (STATE, EVENTS):
        try:
            os.unlink(p)
        except OSError:
            pass
    R.kill_stale(STATE)
    cmd = [sys.executable, os.path.join(HERE, "gym_app.py"),
           "--scenario", "t_probe_fill", "--control-alpha", "%.3f" % alpha,
           "--no-badge", "--no-topmost", "--gap", "8000", "--seed", str(seed),
           "--state", STATE, "--events", EVENTS]
    # a file, not a pipe: the Windows sandbox forbids piped stdio for the child, and
    # swallowing the app's stderr is what hid the "scenario typo" class of failure
    log = open(os.path.join(HERE, "_probe-app.log"), "a", encoding="utf-8")
    return subprocess.Popen(cmd, cwd=HERE, stdout=log, stderr=log)


def wait_task(timeout: float = 12.0) -> dict:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with open(STATE, encoding="utf-8") as fh:
                st = json.load(fh)
        except (OSError, ValueError):
            time.sleep(0.2)
            continue
        if st.get("scenario") == "t_probe_fill" and (st.get("truth") or {}).get("want"):
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
            if KEEP_PNG and i == 0 and any(abs(alpha - k) < 1e-9 for k in KEEP_PNG):
                os.makedirs(OUTDIR, exist_ok=True)
                img.save(os.path.join(OUTDIR, "alpha-%.2f.png" % alpha))
            res = d.chrome(img)
            body_top = res[1] if len(res) > 1 else 0
            body = img.crop((0, body_top, img.width, img.height))
            words = G.ocr_words(body, psm="11")
            hits = G.find_text(words, want, 0.72)          # the driver's default
            lenient = G.find_text(words, want, 0.50)
            best = (hits or lenient or [None])[0]
            row = {"alpha": alpha, "label": want, "sample": i,
                   "ocr_found": bool(hits), "lenient_found": bool(lenient),
                   "ocr_score": round(float(best["score"]), 3) if best else None,
                   "ocr_conf": round(float(best.get("conf", 0.0)), 1) if best else None,
                   "n_words": len(words), "body_top": int(body_top or 0)}
            if best:
                row.update(stats_for(body, best["box"]))
                row["box"] = list(best["box"])
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


def median_of(rows: list[dict], key: str):
    vals = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
    return round(float(np.median(vals)), 2) if vals else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20251007)
    ap.add_argument("--alphas", default="", help="comma list; default is the sweep")
    a = ap.parse_args()
    alphas = [float(v) for v in a.alphas.split(",")] if a.alphas else SWEEP
    actor = Actor()
    print("operable alpha (the app's own constant): %.2f" % __import__("gym_app").OPERABLE_ALPHA)
    # preflight: a full-contrast control must be findable, otherwise the sweep measures
    # nothing but the banner and every alpha looks the same (that happened once already,
    # caused by an unplaced canvas - the fix was in the app's probe scenario).
    pre = measure(1.00, a.seed, actor, samples=1)
    pre_samples = pre.get("samples") or []
    if not pre_samples or not pre_samples[0].get("ocr_found"):
        print("PREFLIGHT FAILED: the full-contrast control was not found by OCR - "
              "aborting instead of writing a void curve")
        print("  frame stats:", json.dumps(pre_samples, ensure_ascii=False)[:400])
        return 3
    print("preflight ok: found %r at alpha 1.00 (score %s)"
          % (pre_samples[0].get("label"), pre_samples[0].get("ocr_score")))
    print("%6s %5s %6s %7s %7s %7s %7s  %s" %
          ("alpha", "found", "lenient", "D1", "D2", "D3", "conf", "median of 3"))
    rows = []
    for alpha in alphas:
        rep = measure(alpha, a.seed, actor)
        rows.append(rep)
        sm = rep.get("samples") or []
        med = {k: median_of(sm, k) for k in ("d1", "d2", "d3", "ocr_conf", "ocr_score")}
        found = sum(1 for r in sm if r.get("ocr_found"))
        lenient = sum(1 for r in sm if r.get("lenient_found"))
        print("%6.2f %5s %6s %7s %7s %7s %7s  found=%d/%d" %
              (alpha, "yes" if found else "no", "%d/%d" % (lenient, len(sm)),
               med["d1"], med["d2"], med["d3"], med["ocr_conf"], found, len(sm)))
        sys.stdout.flush()

    full = next((r for r in rows if abs(r["alpha"] - 1.00) < 1e-9), None)
    full_d1 = median_of((full or {}).get("samples") or [], "d1")
    t_vis = round(0.5 * full_d1) if full_d1 else None
    print("\nDECLARED SELECTION: T_VIS = round(0.5 * D1(1.00)) = round(0.5 * %s) = %s"
          % (full_d1, t_vis))
    predicted = []
    if t_vis is not None:
        print("%6s %8s %8s  %s" % ("alpha", "D1", "click?", "app truth"))
        for rep in rows:
            sm = rep.get("samples") or []
            d1 = median_of(sm, "d1")
            found = any(r.get("ocr_found") for r in sm)
            click = bool(found and d1 is not None and d1 >= t_vis)
            operable = rep["alpha"] >= 0.45
            verdict = ("ok" if click == operable else
                       ("false_refusal" if operable else "false_accept"))
            predicted.append({"alpha": rep["alpha"], "d1": d1, "ocr_found": found,
                              "click": click, "operable": operable, "predicted": verdict})
            print("%6.2f %8s %8s  %s" % (rep["alpha"], d1, click,
                                         "operable" if operable else "must refuse"))
    out = {"declared": {"statistic": "p90_delta(pad=10/6, ring=34/22)",
                        "selection": "T_VIS = round(0.5 * D1(alpha=1.00))",
                        "diagnostics": ["d2", "d3", "ocr_found", "lenient_found"]},
           "operable_alpha": __import__("gym_app").OPERABLE_ALPHA,
           "sweep": alphas, "t_vis": t_vis, "predicted": predicted, "runs": rows}
    with open(os.path.join(HERE, "fill_curve.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("\nwrote fill_curve.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
