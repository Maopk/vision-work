"""Dump the pixels of the row list's left column: what is actually next to a row?

    python probe_row_pixels.py            # saves probe34-frame.png + one crop per row
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gym_run import HERE, Driver                      # noqa: E402
from loop import Actor                                # noqa: E402

STATE = os.path.join(HERE, "probe34-state.json")


def main() -> int:
    d = Driver(Actor(), STATE, bg=True, keys=True)
    d.window_rect()
    img = d.shot()
    full = os.path.join(HERE, "probe34-frame.png")
    img.save(full)
    print("frame saved", img.width, img.height)
    for y in (150, 230, 390, 420, 452, 620):
        box = (0, max(y - 18, 0), 230, 40)
        crop = img.crop((box[0], box[1], box[0] + box[2], box[1] + box[3]))
        crop = crop.resize((crop.width * 3, crop.height * 3))
        out = os.path.join(HERE, "probe34-row-%d.png" % y)
        crop.save(out)
        print("saved", os.path.basename(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
