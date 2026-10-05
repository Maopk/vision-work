"""probe_w6_twin.py - batch 6, step 2: measure before changing anything.

Question: on a real twin frame, do the judges that *already exist* in the driver
separate the bare heading from the painted button?

  * `find_blocks(img)`      - rectangles that are painted on the page (gym_run.py:573)
  * `block_evidence(...)`   - fill_share of the glyph box vs the page (gym_run.py:529)
  * `_button_candidates`    - the dialog ranking that already encodes "painted =
                              control", blocks first, prose vetoed (gym_run.py:678)

The app is launched with `--no-topmost` and read through PrintWindow in background
mode, and the A button is pressed through the app's own key channel, so neither the
user's pointer nor the foreground is touched.  This is a measurement, not a run: the
artifacts are named probe-w6-* and must never be scored as a benchmark.

Usage: python probe_w6_twin.py [scenario] [task_index]
"""
import json
import os
import re
import subprocess
import sys
import time
import atexit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from loop import Actor                                     # noqa: E402
import gym_run as G                                        # noqa: E402

PY = sys.executable
SCEN = sys.argv[1] if len(sys.argv) > 1 else "t_trap4"
STATE = os.path.join(HERE, "probe-w6-state.json")
EVENTS = os.path.join(HERE, "probe-w6-events.jsonl")
SHOT = os.path.join(HERE, "probe-w6-twin.png")


def hit_word(h: dict) -> dict:
    """The word dict inside a find_text hit, whatever shape the hit has."""
    return h.get("word") or h


def hit_box(h: dict):
    w = hit_word(h)
    return w.get("box") or h.get("box")


def main() -> int:
    for f in (STATE, EVENTS):
        if os.path.exists(f):
            os.unlink(f)
    cmd = [PY, os.path.join(HERE, "gym_app.py"), "--state", STATE, "--events", EVENTS,
           "--scenario", SCEN, "--gap", "300", "--no-topmost"]
    proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)

    def _kill():                                            # also on a crash
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        except Exception:                                   # noqa: BLE001
            pass

    atexit.register(_kill)
    print("probe: launched %s" % " ".join(cmd[1:]), flush=True)
    time.sleep(2.5)

    d = G.Driver(Actor(), STATE, verbose=False, bg=True, keys=True)
    d.window_rect()
    print("probe: window rect %s  task_i %s" % (d.window_rect(), d.task_i()), flush=True)

    pressed = 0
    frame = None
    for i in range(80):                                    # ~20 s
        img = d.shot()
        ask, body_top, _band, _ask_box = d.chrome(img)
        m = re.search(r"labelled\s+(.+?)\s*$", ask or "", re.I)
        want = m.group(1).strip() if m else None
        if not want:
            time.sleep(0.25)
            continue
        body = d.words(img, invert=True,
                       region=(14, body_top, img.width - 28, img.height - body_top - 14))
        hits = d.find_all(body, want, 0.82)
        tag = "task %s frame %d: ask=%r hits=%d" % (d.task_i(), i, want, len(hits))
        if len(hits) >= 2:
            frame = (img, want, body, hits)
            print(tag + "  <-- twin frame (the word stands twice in the body)", flush=True)
            break
        if not pressed and hits:
            box = hit_box(hits[0])
            hint = d.hint_near(body, box, 16, 90) if box else None
            if hint:
                d.key(hint)
                pressed += 1
                print(tag + "  pressed A via hint %r" % hint, flush=True)
        else:
            print(tag, flush=True)
        time.sleep(0.25)

    out = {"scenario": SCEN, "want": None, "frame_index": i, "pressed": pressed,
           "occurrences": [], "blocks": [], "block_labels": [], "candidates": [],
           "ms": {"blocks_one_call": None, "shot": d.stats.get("ms_shot"),
                  "ocr": d.stats.get("ms_ocr")}}
    if frame is None:
        out["error"] = "no twin frame seen within the loop"
    else:
        img, want, body, hits = frame
        img.save(SHOT)
        t0 = time.perf_counter()
        blocks = d.find_blocks(img)
        out["ms"]["blocks_one_call"] = round((time.perf_counter() - t0) * 1000, 1)
        out["want"] = want
        out["blocks"] = [list(b) for b in blocks]
        out["block_labels"] = [[list(b), d.block_label(img, b)] for b in blocks]
        for h in hits:
            w = hit_word(h)
            bx, by, bw, bh = [int(v) for v in w["box"]]
            cx, cy = bx + bw / 2, by + bh / 2
            over = [list(b) for b in blocks
                    if b[0] <= cx <= b[0] + b[2] and b[1] <= cy <= b[1] + b[3]]
            rowmates = [o for o in body if o is not w
                        and abs(o["center"][1] - w["center"][1]) <= 12]
            ev = d.block_evidence(img, w, want, len(rowmates))
            out["occurrences"].append(
                {"text": w["text"], "box": [bx, by, bw, bh], "score": h.get("score"),
                 "rowmates": len(rowmates), "in_block": over, "evidence": ev})
        for h in d._button_candidates(img, want):
            w = hit_word(h)
            out["candidates"].append(
                {"source": h.get("source"), "score": round(float(h.get("score") or 0), 3),
                 "veto": h.get("veto"), "text": w.get("text"),
                 "box": [int(v) for v in w["box"]], "evidence": h.get("evidence")})
        # --- the two rules batch 6 is choosing between, evaluated on this frame -----
        occ = out["occurrences"]
        painted = [o for o in occ if o["in_block"]]
        bare = [o for o in occ if not o["in_block"]]
        out["rule_block_covers_text"] = {
            "occurrences": len(occ), "painted": len(painted), "bare": len(bare),
            "picks": painted[0]["text"] if len(painted) == 1 and len(bare) == 1 else None,
            "decides": bool(len(painted) == 1 and len(bare) == 1)}
        # the older idea: match the ask word against the label read inside a block.
        # OCR drops the badge's leading bracket often ("2] KILQ"), which the current
        # strip regex (gym_run.py:726) does not catch, so measure both strips.
        strip_now = re.compile(r"^[\[\(]\s*[0-9A-Za-z]\s*[\]\)]\s*")
        strip_new = re.compile(r"^[\[\(]?\s*[0-9A-Za-z]\s*[\]\)]\s*")
        out["rule_block_label"] = []
        for b in blocks:
            label = d.block_label(img, b)
            out["rule_block_label"].append(
                {"block": list(b), "label": label,
                 "stripped_now": strip_now.sub("", label),
                 "stripped_new": strip_new.sub("", label),
                 "match_now": bool(d.find([{"text": strip_now.sub("", label),
                                            "conf": 100.0,
                                            "box": (b[0], b[1], b[2], b[3]),
                                            "center": (b[0] + b[2] // 2, b[1] + b[3] // 2)}],
                                          want, 0.9)),
                 "match_new": bool(d.find([{"text": strip_new.sub("", label),
                                            "conf": 100.0,
                                            "box": (b[0], b[1], b[2], b[3]),
                                            "center": (b[0] + b[2] // 2, b[1] + b[3] // 2)}],
                                          want, 0.9))})
    with open(os.path.join(HERE, "probe-w6-twin.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps(out, ensure_ascii=False, indent=2), flush=True)

    try:
        subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
    except Exception:                                       # noqa: BLE001
        pass
    return 0 if frame is not None else 1


if __name__ == "__main__":
    sys.exit(main())
