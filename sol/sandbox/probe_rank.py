"""Dump the exact crops the card reader feeds to OCR, at OCR scale.

    probe_rank.py <shot.png> <window x0,y0,x1,y1> [col] [k]

Writes rank-<col>-<k>.png (rank box) and suit-<col>-<k>.png (suit box) next to
the shot, plus ink statistics, so a human can see what tesseract sees.
"""
from __future__ import annotations

import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import spider_read as R  # noqa: E402


def ink_stats(crop: Image.Image) -> str:
    a = np.asarray(crop.convert("RGB")).astype(np.int16)
    mx, mn = a.max(axis=2), a.min(axis=2)
    ink = ((mx - mn) > 55) | (mx < 150)
    ys, xs = np.where(ink)
    if len(ys) == 0:
        return "ink 0 px"
    return ("ink %d px  box x%d..%d y%d..%d of %dx%d"
            % (ink.sum(), xs.min(), xs.max(), ys.min(), ys.max(),
               crop.width, crop.height))


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    shot = sys.argv[1]
    win = tuple(int(v) for v in sys.argv[2].split(","))
    want = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    kk = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    im = Image.open(shot).convert("RGB")
    arr, (ox, oy) = R.load(shot, win)
    st = R.structure(arr, ox, oy)
    lay = R.column_layout(arr, st)
    print("origin", ox, oy, "board", st["board"], "cards_y", st["cards_y"])
    for L in lay:
        if L["i"] != want:
            continue
        y0 = (L["face_y"] or 0) + kk * R.FACE_PITCH
        print("col %d x=%s w=%d down=%d face_y=%d n_face=%d"
              % (L["i"], L["x"], L["w"], L["down"], L["face_y"], L["n_face"]))
        print("card top y=%d  (crop rows 4..34 => absolute %d..%d)"
              % (y0, y0 + 4, y0 + 34))
        rx = (L["x"][0] + R.RANK_BOX[0], y0 + R.RANK_BOX[1],
              L["x"][0] + R.RANK_BOX[2], y0 + R.RANK_BOX[3])
        sx = (L["x"][0] + R.SUIT_BOX[0], y0 + R.SUIT_BOX[1],
              L["x"][0] + R.SUIT_BOX[2], y0 + R.SUIT_BOX[3])
        rcrop = im.crop(rx)
        scrop = im.crop(sx)
        print("rank box", rx, "->", ink_stats(rcrop))
        print("suit box", sx, "->", ink_stats(scrop))
        print("ocr rank:", R.ocr_rank(rcrop))
        rcrop.resize((rcrop.width * 8, rcrop.height * 8), Image.LANCZOS).save(
            os.path.join(HERE, "rank-%d-%d.png" % (L["i"], kk)))
        scrop.resize((scrop.width * 8, scrop.height * 8), Image.LANCZOS).save(
            os.path.join(HERE, "suit-%d-%d.png" % (L["i"], kk)))
        # a wide strip of the card's top-left corner, 2x, for eyeballing
        wide = im.crop((L["x"][0], y0, L["x"][0] + 120, y0 + 110))
        wide.resize((wide.width * 2, wide.height * 2), Image.LANCZOS).save(
            os.path.join(HERE, "corner-%d-%d.png" % (L["i"], kk)))
        print("wrote rank-%d-%d.png suit-%d-%d.png corner-%d-%d.png"
              % (L["i"], kk, L["i"], kk, L["i"], kk))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
