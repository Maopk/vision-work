"""Offline split of the OCR cost: which pass inside one task is expensive.

Profiling (prof1.json, 12 mixed tasks) says OCR = 52.6% of a task at 167 ms per
call, so the next question is *which* call.  This runs the exact passes the
driver uses, on the last captured frame, with no app involved:

    python probe_ocr_cost.py [frame.png] [reps]

Reports mean ms per pass: the 1x body pass, the 2x body pass, a tight 4x
re-read, the bottom strip, and block detection on the same frame.
"""
from __future__ import annotations

import os
import sys
import time

import gui_see as G
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))


def bench(label: str, fn, reps: int) -> float:
    fn()                                   # warm the font cache / tesseract
    t0 = time.perf_counter()
    for _ in range(reps):
        fn()
    ms = (time.perf_counter() - t0) * 1000 / reps
    print("  %-28s %7.1f ms" % (label, ms))
    return ms


def main(argv: list[str]) -> int:
    path = argv[0] if argv else os.path.join(HERE, "_gym_shot.png")
    reps = int(argv[1]) if len(argv) > 1 else 8
    img = Image.open(path).convert("RGB")
    print("frame %s  %dx%d  reps=%d" % (os.path.basename(path), img.width, img.height, reps))
    body_top = 150
    region = (0, body_top, img.width, img.height - body_top)
    body = img.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))

    bench("body psm11 1x (as-is)", lambda: G.ocr_words(body, psm="11"), reps)
    big = body.resize((body.width * 2, body.height * 2), Image.LANCZOS)
    bench("body psm6 2x (resize+ocr)", lambda: G.ocr_words(
        body.resize((body.width * 2, body.height * 2), Image.LANCZOS), psm="6"), reps)
    bench("  resize 2x only", lambda: body.resize((body.width * 2, body.height * 2),
                                                  Image.LANCZOS), reps)
    bench("  ocr on the 2x bitmap", lambda: G.ocr_words(big, psm="6"), reps)
    strip = img.crop((0, img.height - 60, img.width, img.height))
    bench("bottom strip psm7 1x", lambda: G.ocr_words(strip, psm="7", min_conf=20.0), reps)
    bench("bottom strip psm7 2x", lambda: G.ocr_words(
        strip.resize((strip.width * 2, strip.height * 2), Image.LANCZOS),
        psm="7", min_conf=20.0), reps)
    crop = img.crop((500, 150, 600, 175))
    bench("tight box 4x read_box", lambda: G.read_box(crop.resize(
        (crop.width * 4, crop.height * 4), Image.LANCZOS), (0, 0, crop.width * 4,
        crop.height * 4), psm="7", scale=1), reps)
    bench("convert RGB", lambda: img.convert("RGB"), reps)
    bench("invert (L->RGB)", lambda: ImageOps.invert(
        body.convert("L")).convert("RGB"), reps)

    # block detection: only used on the dialog / mouse path, so measure it here
    try:
        import numpy as np

        arr = np.asarray(img, dtype=np.int16)

        def blocks() -> int:
            page = np.array([int(v) for v in img.getpixel((img.width - 5, 5))], dtype=np.int16)
            diff = np.abs(arr - page).max(axis=2) > 8
            return int(diff.sum())

        bench("find_blocks-ish scan (numpy)", blocks, reps)
    except ImportError:
        print("  (numpy missing - block scan not measured)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
