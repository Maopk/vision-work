"""Which OCR settings actually read the body of the gym window?

The first background run dropped two buttons that are plainly on screen
(`[3] INDIGO95`, `SABLE44`), so this measures recall instead of guessing:
every candidate setting is run over the same saved frame and we count how many
of the wanted labels it recovers.

    python probe_body_ocr.py probe-keys.png INDIGO95 SABLE44 lumen

The frame must be a gym window capture (the body top comes from chrome()).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gui_see as G                                    # noqa: E402
from gym_run import Driver                             # noqa: E402
from loop import Actor                                 # noqa: E402

CONFIGS = [
    ("psm11 scale1", dict(psm="11", scale=1)),
    ("psm6  scale1", dict(psm="6", scale=1)),
    ("psm4  scale1", dict(psm="4", scale=1)),
    ("psm3  scale1", dict(psm="3", scale=1)),
    ("psm11 scale2", dict(psm="11", scale=2)),
    ("psm6  scale2", dict(psm="6", scale=2)),
    ("psm11 scale3", dict(psm="11", scale=3)),
    ("psm6  scale3", dict(psm="6", scale=3)),
]


def main() -> int:
    png = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "probe-keys.png")
    wants = sys.argv[2:]
    d = Driver(Actor(), os.path.join(os.path.dirname(png), "probe-state.json"))
    img = G.Image.open(png).convert("RGB")
    ask, body, _band, _box = d.chrome(img)
    print("frame %s  %dx%d" % (os.path.basename(png), img.width, img.height))
    print("ask=%r  body_top=%d  wants=%s" % (ask, body, wants))
    region = (0, body, img.width, img.height - body)
    best = None
    for name, kw in CONFIGS:
        try:
            ws = d.words(img, region=region, **kw)
        except Exception as e:                          # noqa: BLE001 - probe
            print("%-14s FAILED: %s" % (name, e))
            continue
        texts = [w["text"] for w in ws]
        hit = [w for w in wants if any(G.norm(w) in G.norm(t) for t in texts)]
        miss = [w for w in wants if w not in hit]
        print("%-14s words=%-3d hit=%-2d %s%s" % (
            name, len(texts), len(hit), ",".join(hit),
            ("   MISSING " + ",".join(miss)) if miss else ""))
        if best is None or len(hit) > best[1]:
            best = (name, len(hit), texts)
    if best:
        print("\nbest: %s (hit %d/%d)" % (best[0], best[1], len(wants)))
        print("   ", sorted(best[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
