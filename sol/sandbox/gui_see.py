"""General "see a GUI" primitives: one OCR pass over a window, colour blobs, diffs.

Nothing here knows about cards.  It answers the questions any GUI task asks -
where is this text, what does this box say, where is this colour, did the screen
change - so the same code drives a card game, an installer or a settings dialog.
"""
from __future__ import annotations

import difflib
import os
import re
import subprocess
import tempfile

import numpy as np
from PIL import Image

TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---------------------------------------------------------------- OCR --------

def ocr_words(im: Image.Image, lang: str = "eng", psm: str = "11",
              min_conf: float = 30.0, whitelist: str | None = None) -> list[dict]:
    """Every word tesseract finds, with its box, in image coordinates.

    psm 11 = sparse text: good for a whole window with scattered labels.
    One call per frame instead of one per widget, which is what makes a
    general "find the text on screen" step affordable.
    """
    fd, tmp = tempfile.mkstemp(prefix="dsh-ocr-", suffix=".png")
    os.close(fd)
    try:
        im.save(tmp)
        cmd = [TESS, tmp, "stdout", "-l", lang, "--psm", psm, "tsv"]
        if whitelist:
            cmd += ["-c", "tessedit_char_whitelist=" + whitelist]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    out = []
    for line in (r.stdout or "").splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 12 or not f[11].strip():
            continue
        try:
            conf = float(f[10])
        except ValueError:
            continue
        if conf < min_conf:
            continue
        out.append({"text": f[11].strip(), "conf": conf,
                    "box": (int(f[6]), int(f[7]), int(f[8]), int(f[9]))})
    return out


def read_box(im: Image.Image, box, whitelist: str | None = None,
             psm: str = "7", lang: str = "eng", scale: int = 4) -> tuple[str, float]:
    """Read the text inside one box (a field, a cell, a counter)."""
    x, y, w, h = box
    crop = im.crop((x, y, x + w, y + h))
    crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    fd, tmp = tempfile.mkstemp(prefix="dsh-box-", suffix=".png")
    os.close(fd)
    try:
        crop.save(tmp)
        cmd = [TESS, tmp, "stdout", "-l", lang, "--psm", psm]
        if whitelist:
            cmd += ["-c", "tessedit_char_whitelist=" + whitelist]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass
    return (r.stdout or "").strip(), 0.0


def char_boxes(im: Image.Image, lang: str = "eng", psm: str = "7",
               whitelist: str | None = None) -> list[dict]:
    """Per-character boxes for one line of text, in image coordinates.

    tesseract's own word pass decides a glyph from the word context; `makebox` with
    `batch.nochop` hands the classifier whole, unchoped glyphs instead.  Measured on
    the practice banner (Segoe UI bold -26): the word pass read the code `C02S` as
    `CO2S` - letter O instead of digit zero - and a target that compares strings
    exactly then rejects a value the screen actually spelled out.  The per-glyph pass
    read the digit.  Boxes come back sorted left to right, `{"text", "box"}`.
    """
    fd, tmp = tempfile.mkstemp(prefix="dsh-glyph-", suffix=".png")
    os.close(fd)
    base = tmp[:-4]
    box_path = base + ".box"
    rows: list[dict] = []
    try:
        im.save(tmp)
        cmd = [TESS, tmp, base, "-l", lang, "--psm", psm, "batch.nochop", "makebox"]
        if whitelist:
            cmd += ["-c", "tessedit_char_whitelist=" + whitelist]
        subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if os.path.exists(box_path):
            with open(box_path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    p = line.split()
                    if len(p) < 5:
                        continue
                    ch, x1, y1, x2, y2 = p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4])
                    rows.append({"text": ch,
                                 "box": (x1, im.height - y2, x2 - x1, y2 - y1)})
    finally:
        for p_ in (tmp, box_path):
            try:
                os.unlink(p_)
            except OSError:
                pass
    rows.sort(key=lambda c: c["box"][0])
    return rows


# ------------------------------------------------------------- matching ------

def norm(s: str) -> str:
    """Comparison form: casefold, drop everything that is not alphanumeric."""
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", s.casefold())


def find_text(words: list[dict], want: str, min_score: float = 0.72) -> list[dict]:
    """Rank OCR words against a target string.

    Exact match wins, then prefix/substring, then fuzzy - GUI labels are rarely
    OCR-perfect (l/1, O/0, missing punctuation), so refusing anything but an
    exact string makes the whole approach brittle.
    """
    w = norm(want)
    hits = []
    for it in words:
        t = norm(it["text"])
        if not t or not w:
            continue
        if t == w:
            score = 1.0
        elif t.startswith(w) or w.startswith(t):
            score = 0.9 * min(len(t), len(w)) / max(len(t), len(w)) + 0.1
        elif w in t or t in w:
            score = 0.8 * min(len(t), len(w)) / max(len(t), len(w)) + 0.1
        else:
            score = difflib.SequenceMatcher(None, t, w).ratio() * 0.85
        if score >= min_score:
            hits.append({"text": it["text"], "conf": it["conf"], "box": it["box"],
                         "score": round(score, 3),
                         "center": (it["box"][0] + it["box"][2] // 2,
                                    it["box"][1] + it["box"][3] // 2)})
    return sorted(hits, key=lambda h: -h["score"])


def group_lines(words: list[dict], y_tol: int = 12) -> list[dict]:
    """Words grouped into reading-order lines (for tables and lists)."""
    rows: list[dict] = []
    for it in sorted(words, key=lambda i: (i["box"][1], i["box"][0])):
        x, y, w, h = it["box"]
        for r in rows:
            if abs(r["y"] - y) <= y_tol:
                r["items"].append(it)
                r["y"] = min(r["y"], y)
                break
        else:
            rows.append({"y": y, "items": [it]})
    out = []
    for r in rows:
        items = sorted(r["items"], key=lambda i: i["box"][0])
        x0 = min(i["box"][0] for i in items)
        y0 = min(i["box"][1] for i in items)
        x1 = max(i["box"][0] + i["box"][2] for i in items)
        y1 = max(i["box"][1] + i["box"][3] for i in items)
        out.append({"text": " ".join(i["text"] for i in items), "items": items,
                    "box": (x0, y0, x1 - x0, y1 - y0),
                    "center": ((x0 + x1) // 2, (y0 + y1) // 2)})
    return out


# --------------------------------------------------------------- pixels ------

def components(mask: np.ndarray, min_area: int = 30) -> list[tuple]:
    """Connected blobs of a boolean mask: [(area, (y0, x0, y1, x1)), ...], big first."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    for i in range(h):
        for j in range(w):
            if not mask[i, j] or seen[i, j]:
                continue
            stack = [(i, j)]
            seen[i, j] = True
            n = 0
            y0 = y1 = i
            x0 = x1 = j
            while stack:
                y, x = stack.pop()
                n += 1
                y0, y1 = min(y0, y), max(y1, y)
                x0, x1 = min(x0, x), max(x1, x)
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
            if n >= min_area:
                out.append((n, (y0, x0, y1, x1)))
    return sorted(out, key=lambda b: -b[0])


def color_blobs(im: Image.Image, rgb, tol: int = 50, min_area: int = 30,
                region=None) -> list[dict]:
    """Where is this colour?  Boxes + centres + mean colour, big first."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    ox = oy = 0
    if region:
        x, y, w, h = region
        a, ox, oy = a[y:y + h, x:x + w], x, y
    d = np.abs(a - np.array(rgb, dtype=np.int16)).max(axis=2)
    out = []
    for area, (y0, x0, y1, x1) in components(d <= tol, min_area):
        mean = a[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3).mean(axis=0)
        out.append({"area": area, "box": (x0 + ox, y0 + oy, x1 - x0 + 1, y1 - y0 + 1),
                    "center": ((x0 + x1) // 2 + ox, (y0 + y1) // 2 + oy),
                    "color": tuple(int(v) for v in mean)})
    return out


def ink(img: Image.Image, box, bg=(255, 255, 255), tol: int = 40) -> float:
    """Fraction of pixels in a box that are not the background colour.

    A checkbox that is ticked, a dot that is lit and an empty cell differ here
    without needing to know what widget it is.
    """
    x, y, w, h = box
    a = np.asarray(img.convert("RGB").crop((x, y, x + w, y + h))).astype(np.int16)
    if a.size == 0:
        return 0.0
    d = np.abs(a - np.array(bg, dtype=np.int16)).max(axis=2)
    return float((d > tol).mean())


def diff_frac(a: Image.Image, b: Image.Image) -> float:
    """Share of pixels that differ - the cheapest "did anything happen" test."""
    if a.size != b.size:
        b = b.resize(a.size)
    x = np.asarray(a.convert("L")).astype(np.int16)
    y = np.asarray(b.convert("L")).astype(np.int16)
    return float((np.abs(x - y) > 24).mean())


def save(img: Image.Image, path: str, box=None) -> str:
    if box:
        x, y, w, h = box
        img = img.crop((x, y, x + w, y + h))
    img.save(path)
    return path
