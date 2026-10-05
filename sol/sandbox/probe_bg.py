"""Does a window grab work without touching the user's foreground?

Captures a window that is already on screen twice - once through PrintWindow
(`shot` with an hwnd) and once through a plain screen grab of the same rectangle -
and compares the two. Nothing is focused, moved or clicked by this probe.
"""
import json
import os
import socket
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("ACTOR_PORT", "8731"))


def call(req: dict, timeout: float = 20.0) -> dict:
    with socket.create_connection(("127.0.0.1", PORT), timeout=timeout) as sk:
        sk.sendall((json.dumps(req) + "\n").encode())
        buf = b""
        while b"\n" not in buf:
            chunk = sk.recv(65536)
            if not chunk:
                break
            buf += chunk
    return json.loads(buf.decode("utf-8", "replace").splitlines()[0])


def stats(tag: str, arr: np.ndarray, other: np.ndarray | None = None) -> None:
    lum = arr.mean(axis=2)
    line = ("%s: %dx%d mean %.1f  dark%% %.3f  colours %d"
            % (tag, arr.shape[1], arr.shape[0], lum.mean(),
               float((lum < 100).mean()), len(np.unique(arr.reshape(-1, 3), axis=0))))
    if other is not None and other.shape == arr.shape:
        d = np.abs(arr.astype(np.int16) - other.astype(np.int16)).sum(axis=2)
        line += "  |diff| vs screen %.1f  identical %.3f" % (d.mean(), float((d == 0).mean()))
    print(line)


def shoot(name: str, **req) -> np.ndarray | None:
    path = os.path.join(HERE, "probe-bg-%s.png" % name)
    r = call(dict(op="shot", path=path, **req))
    if not r.get("ok"):
        print("%s failed: %s" % (name, r.get("error")))
        return None
    return np.asarray(Image.open(path).convert("RGB"))


def main() -> int:
    wins = [w for w in (call({"op": "uia", "what": "windows", "max": 80}).get("windows") or [])
            if w.get("rect") and (w["rect"][2] - w["rect"][0]) > 250
            and (w["rect"][3] - w["rect"][1]) > 150]
    wins = [w for w in wins if "overlay" not in (w.get("name") or "").lower()]
    wins.sort(key=lambda w: -((w["rect"][2] - w["rect"][0]) * (w["rect"][3] - w["rect"][1])))
    print("candidates (largest first):")
    for w in wins[:10]:
        r = [int(v) for v in w["rect"]]
        print("  hwnd=%-9s %-40s rect=%s" % (w.get("hwnd"), (w.get("name") or "")[:40], r))
    if not wins:
        print("no candidate window found")
        return 1
    for w in wins[:3]:
        x0, y0, x1, y1 = [int(v) for v in w["rect"]]
        cx0, cy0 = max(0, x0), max(0, y0)
        cx1, cy1 = min(2559, x1), min(1599, y1)
        print("\n--- hwnd=%s %r ---" % (w.get("hwnd"), (w.get("name") or "")[:40]))
        shot = shoot("win-%s" % w["hwnd"], hwnd=int(w["hwnd"]))
        if shot is None:
            continue
        # the hwnd capture includes the frame; crop the visible part for the compare
        part = shot[max(0, cy0 - y0):max(0, cy0 - y0) + (cy1 - cy0),
                    max(0, cx0 - x0):max(0, cx0 - x0) + (cx1 - cx0)]
        stats("printwindow", part)
        if cx1 > cx0 and cy1 > cy0:
            screen = shoot("screen-%s" % w["hwnd"], region=[cx0, cy0, cx1, cy1])
            if screen is not None:
                stats("screen-crop", screen, part)
    return 0


if __name__ == "__main__":
    sys.exit(main())
