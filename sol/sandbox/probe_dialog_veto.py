"""Does the block veto tell the DISMISS button apart from the prose that says "dismiss"?

    python probe_dialog_veto.py

Starts a practice target with popup chaos forced, waits for its "attention" window,
captures that window the way the driver does, and prints every candidate the word
match finds with the block evidence behind it - then what the vetoed list shrinks to.
This is the offline check for the mouse path, which cannot be exercised end to end
while the user's screen must not be touched.
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

from gym_run import Actor, Driver, kill_stale          # noqa: E402

PY = sys.executable
STATE = os.path.join(HERE, "_probe-veto-state.json")
EVENTS = os.path.join(HERE, "_probe-veto-events.jsonl")


def main():
    for f in (STATE, EVENTS):
        if os.path.exists(f):
            os.unlink(f)
    kill_stale(STATE)
    cmd = [PY, os.path.join(HERE, "gym_app.py"), "--state", STATE, "--events", EVENTS,
           "--gap", "300", "--seed", "20251007", "--scenario", "t_button",
           "--chaos", "1.0", "--chaos-kind", "popup", "--no-topmost"]
    proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT)
    try:
        d = Driver(Actor(), STATE, verbose=False, bg=True)
        cap = None
        for _ in range(20):
            time.sleep(0.5)
            cap = d.shot_window("attention")
            if cap is not None:
                break
        if cap is None:
            print("no dialog appeared - rerun")
            return 2
        wimg, ox, oy = cap
        print("dialog window at %s, size %s" % ((ox, oy), wimg.size))
        for inv in (False, True):
            words = d.words(wimg, invert=inv)
            print("words invert=%s: %s" % (inv, [(w_["text"], w_["box"]) for w_ in words]))
        print("--- coarse render of the lower half (1 char = 8x8 px) ---")
        g = wimg.convert("L")
        px = g.load()
        for yy in range(100, wimg.height, 8):
            row = []
            for xx in range(0, wimg.width, 8):
                vals = [px[x, y] for x in range(xx, min(xx + 8, wimg.width))
                        for y in range(yy, min(yy + 8, wimg.height))]
                m = sum(vals) / float(len(vals))
                row.append("#" if m < 120 else ("+" if m < 200 else "."))
            print("%4d %s" % (yy, "".join(row)))
        print("--- painted blocks (x, y, w, h, fill) and the label inside each ---")
        import gui_see as G
        for blk in d.find_blocks(wimg):
            label = d.block_label(wimg, blk)
            print("   %s fill=%.3f label=%r" % (blk[:4], blk[4], label))
        print("--- re-read of the button area, boxes are (x, y, w, h) ---")
        for box in [(185, 118, 125, 34), (190, 120, 105, 26), (192, 122, 104, 20)]:
            for psm in ("7", "8", "6"):
                txt, _ = G.read_box(wimg, box, psm=psm, scale=3)
                if txt.strip():
                    print("   %s psm=%s -> %r" % (box, psm, txt.strip()))
        all_hits = d._button_candidates(wimg, "DISMISS", keep_vetoed=True)
        print("candidates (with vetoed kept): %d" % len(all_hits))
        for h in all_hits:
            w_ = h["word"]
            print("   %-10r box=%s score=%.2f neigh=%d fill=%.3f veto=%s source=%s"
                  % (w_["text"], w_["box"], h["score"], h["neighbours"],
                     h["evidence"]["fill_share"], h["veto"], h.get("source")))
        kept = d._button_candidates(wimg, "DISMISS")
        print("after the veto: %d candidate(s)" % len(kept))
        for h in kept:
            print("   -> %r at %s (fill %.3f)"
                  % (h["word"]["text"], h["word"]["center"], h["evidence"]["fill_share"]))
        prose = [h for h in all_hits if h["veto"]]
        button = [h for h in all_hits if not h["veto"]]
        print("VERDICT: vetoed %d prose candidate(s), kept %d block candidate(s)"
              % (len(prose), len(button)))
        if kept:
            cx, cy = kept[0]["word"]["center"]
            print("         would click (%d, %d) in window coords" % (cx, cy))
        return 0
    finally:
        proc.terminate()
        time.sleep(0.5)


if __name__ == "__main__":
    sys.exit(main())
