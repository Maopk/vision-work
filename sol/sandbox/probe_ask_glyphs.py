"""Look at the ask banner one glyph at a time and ask: is 0 vs O readable at all?

Why: t_form lost a task because the app's ground truth was `C02S` (digit zero) and the
banner read as `CO2S` (letter O) - the app compares exactly, so the task was judged
WRONG although the screen was read "reasonably". Before writing any disambiguation
rule into the driver this probe measures whether the rendered glyphs actually differ:
it renders both candidates in the same font the banner uses (Segoe UI bold -26, see
gym_app.py:120) and reports IoU plus ink aspect for every confusable character found
on the banner.

Diagnosis only: this probe compares its reading with the app's own truth, which the
driver never does (m02754).
"""

import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gui_see as _gui_see                                                 # noqa: F401,E402
from gym_run import Driver, foreground_via, kill_stale                       # noqa: E402
from loop import Actor                                                       # noqa: E402

# Characters that share a shape family: reading either one on the banner is a coin
# flip for tesseract, and the app compares strings exactly.
CONFUSE = {"0": "O", "O": "0", "1": "I", "I": "1", "1": "l", "l": "1", "5": "S", "S": "5",
           "2": "Z", "Z": "2", "8": "B", "B": "8", "6": "G", "G": "6", "9": "g", "g": "9"}

FONT = "C:/Windows/Fonts/segoeuib.ttf"
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
N = 32


def ink(im: Image.Image, thr: int = 128) -> np.ndarray:
    a = np.asarray(im.convert("L"), dtype=np.uint8)
    return a < thr


def norm_mask(m: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return np.zeros((N, N), bool)
    m = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    small = Image.fromarray((m * 255).astype(np.uint8)).resize((N, N), Image.LANCZOS)
    return np.asarray(small) > 127


def aspect(m: np.ndarray) -> tuple[int, int, float]:
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return 0, 0, 0.0
    w, h = int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)
    return w, h, round(w / max(1, h), 3)


def proto(ch: str, size: int = 26) -> np.ndarray:
    """Render one character the way the banner does (Segoe UI bold, -26 px)."""
    f = ImageFont.truetype(FONT, size)
    im = Image.new("L", (120, 80), 255)
    ImageDraw.Draw(im).text((20, 10), ch, font=f, fill=0)
    return norm_mask(ink(im))


def iou(a: np.ndarray, b: np.ndarray) -> float:
    u = (a | b).sum()
    return float((a & b).sum() / u) if u else 0.0


def char_boxes(im: Image.Image, psm: str = "7") -> list[dict]:
    """Per-character boxes for one line: tesseract's makebox, no chopping."""
    tmp = os.path.abspath("_glyph.png")
    out = os.path.abspath("_glyph")
    if os.path.exists(out + ".box"):
        os.remove(out + ".box")
    im.convert("L").save(tmp)
    cmd = [TESS, tmp, out, "-l", "eng", "--psm", psm, "batch.nochop", "makebox"]
    subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    boxes: list[dict] = []
    if not os.path.exists(out + ".box"):
        return boxes
    with open(out + ".box", encoding="utf-8") as fh:
        for line in fh:
            p = line.split()
            if len(p) < 5:
                continue
            ch, x1, y1, x2, y2 = p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4])
            boxes.append({"ch": ch, "box": (x1, im.height - y2, x2 - x1, y2 - y1)})
    boxes.sort(key=lambda c: c["box"][0])
    return boxes


def banner_chars(img: Image.Image, up: float = 2.0) -> tuple[str, list[dict], tuple]:
    """OCR the dark banner char by char: returns (text, per-char boxes, crop origin)."""
    g = np.asarray(img.convert("L"), dtype=np.int16)
    darkfrac = (g < 100).mean(axis=1)
    rows = np.nonzero(darkfrac > 0.30)[0]
    if len(rows) == 0:
        return "", [], (0, 0)
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    crop = img.crop((0, y0, img.width, y1))
    big = crop.resize((int(crop.width * up), int(crop.height * up)), Image.LANCZOS)
    out: list[dict] = []
    for c in char_boxes(big):
        bx, by, bw, bh = c["box"]
        out.append({"ch": c["ch"], "box": (int(bx / up), int(by / up),
                                           max(1, int(bw / up)), max(1, int(bh / up)))})
    text = "".join(c["ch"] for c in out if c["ch"].strip())
    return text, out, (0, y0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", type=int, default=10, help="answer this many, then look")
    ap.add_argument("--seed", type=int, default=20251007)
    ap.add_argument("--scenario", default="t_form")
    ap.add_argument("--state", default="askglyph-state.json")
    ap.add_argument("--events", default="askglyph-events.jsonl")
    ap.add_argument("--py", default=sys.executable)
    ap.add_argument("--no-start", action="store_true")
    ap.add_argument("--keep", action="store_true", help="leave the app running")
    args = ap.parse_args()

    a = Actor()
    fg0 = foreground_via(a)
    print("foreground before:", fg0)
    app = None
    if not args.no_start:
        kill_stale(args.state)
        for f in (args.state, args.events):
            if os.path.exists(f):
                os.remove(f)
        app = subprocess.Popen(
            [args.py, "-u", "gym_app.py", "--state", args.state, "--events", args.events,
             "--seed", str(args.seed), "--scenario", args.scenario, "--no-topmost"],
            cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("app pid", app.pid)
        time.sleep(3.0)

    d = Driver(a, args.state, verbose=False, bg=True, keys=True)
    d.a.run([{"op": "window", "mode": "front", "hwnd": fg0.get("hwnd")}], results=True)
    try:
        for i in range(args.tasks):
            rec = d.do_task()
            print("task %2d %-8s %s" % (i, rec.get("result"), (rec.get("ask") or "")[:70]))
            time.sleep(0.3)
        img = d.shot()
        img.save("askglyph-frame.png")
        text, chars, origin = banner_chars(img)
        ask, _top, _words, _ask_box = d.chrome(img)
        st = d.state()
        truth = (st.get("truth") or {}).get("want")
        print("\nbanner read char-by-char :", text[:110])
        print("driver chrome() ask      :", ask[:110])
        print("app truth (diagnosis)    :", json.dumps(truth, ensure_ascii=False)[:110])

        # only judge the characters that matter
        rows = []
        for c in chars:
            if c["ch"] not in CONFUSE:
                continue
            bx, by, bw, bh = c["box"]
            pad = 2
            glyph = ink(img.crop((max(0, bx - pad), origin[1] + max(0, by - pad),
                                  bx + bw + pad, origin[1] + by + bh + pad)))
            if glyph.sum() == 0:
                continue
            cands = [c["ch"], CONFUSE[c["ch"]]]
            scores = {k: round(iou(norm_mask(glyph), proto(k)), 4) for k in cands}
            w, h, ar = aspect(glyph)
            par = {k: aspect(ink(_proto_img(k))) for k in cands}
            rows.append((c["ch"], (bx, by), (w, h, ar), scores, par))
        print("\n%-3s %-12s %-16s %-28s %s" % ("ocr", "box", "ink w,h,aspect", "IoU vs candidates",
                                               "candidate aspects"))
        for ch, box, (w, h, ar), scores, par in rows:
            best = max(scores, key=lambda k: scores[k])
            print("%-3s %-12s %-16s %-28s %s   -> best %s" % (
                ch, "%d,%d" % box, "%d,%d,%s" % (w, h, ar),
                " ".join("%s=%.3f" % (k, v) for k, v in scores.items()),
                " ".join("%s=%.2f" % (k, v[2]) for k, v in par.items()), best))
    finally:
        if not args.keep:
            if app is not None:
                app.terminate()
            time.sleep(0.5)
            d.a.run([{"op": "window", "mode": "front", "hwnd": fg0.get("hwnd")}], results=True)
            print("foreground after:", foreground_via(a))
    return 0


_PROTO_CACHE: dict = {}


def _proto_img(ch: str, size: int = 26) -> Image.Image:
    key = (ch, size)
    if key not in _PROTO_CACHE:
        f = ImageFont.truetype(FONT, size)
        im = Image.new("L", (120, 80), 255)
        ImageDraw.Draw(im).text((20, 10), ch, font=f, fill=0)
        _PROTO_CACHE[key] = im
    return _PROTO_CACHE[key]


if __name__ == "__main__":
    raise SystemExit(main())
