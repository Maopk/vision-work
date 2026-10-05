"""Look at one row's badge in a failure frame and say which crop reads what.

    python probe_badge.py _fail-36456-0.png 254

Prints an ASCII render of the left strip around the given row y, then re-reads a
sweep of crops (x offset x width) with the same OCR the driver uses, so a badge
that a fixed crop misses (or reads wrong) becomes visible as a number.
"""
import sys

from PIL import Image

import gui_see as G

ROW_MATCH = None


def ascii_render(im, x0, y0, x1, y1, thresh=150):
    px = im.convert("L").load()
    for y in range(y0, y1):
        line = []
        for x in range(x0, x1):
            v = px[x, y]
            line.append(" " if v > 230 else ("." if v > thresh else "#"))
        print("%4d %s" % (y, "".join(line)))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "_fail-36456-0.png"
    rowy = int(sys.argv[2]) if len(sys.argv) > 2 else 254
    im = Image.open(path)
    print("image", im.size, "row y =", rowy)
    print("--- left strip x=0..140 ---")
    ascii_render(im, 0, rowy - 20, 140, rowy + 26)
    print("--- crop sweep, psm 7, scale 4, whitelist 0-9a-z[]()<> ---")
    wl = "0123456789abcdefghijlmoprstuvwxyz[]()<>"
    for x0 in range(0, 130, 8):
        for w in (30, 44, 60):
            box = (x0, rowy - 8, x0 + w, rowy + 18)
            txt, _ = G.read_box(im, box, whitelist=wl, psm="7", scale=4)
            if txt.strip():
                print("  x=%3d w=%2d -> %r" % (x0, w, txt))
    print("--- word pass on the same strip ---")
    words = G.words(im, invert=True, psm="11")
    near = [w for w in words if abs(w["box"][1] - rowy) < 22 and w["box"][0] < 140]
    print(" ", [(w["text"], w["box"]) for w in near])


if __name__ == "__main__":
    main()
