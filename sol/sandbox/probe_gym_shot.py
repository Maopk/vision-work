"""Why can the gym window no longer be captured?

Prints the foreground window, the gym window's own info, and the result of the exact
capture call the driver makes (PrintWindow by hwnd) - so "the app is gone", "the window
is minimised" and "the session is locked" can be told apart.

    python probe_gym_shot.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loop import Actor                                     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "probe-gym-shot.png")


def main() -> int:
    a = Actor()
    fg = a.run([{"op": "window", "mode": "foreground"}], results=True)
    print("foreground:", json.dumps(fg.get("trace", [{}])[0].get("data", {}),
                                    ensure_ascii=False)[:200])
    rep = a.run([{"op": "uia", "what": "windows", "max": 60}], results=True)
    wins = (rep.get("trace", [{}])[0].get("data") or {}).get("windows") or []
    gym = [w for w in wins if isinstance(w, dict) and "GUI Gym" in (w.get("name") or "")]
    print("gym windows: %d" % len(gym))
    for w in gym[:3]:
        print("  ", json.dumps(w, ensure_ascii=False)[:220])
    if gym:
        hwnd = int(gym[0]["hwnd"])
        info = a.run([{"op": "window", "mode": "info", "hwnd": hwnd}], results=True)
        print("info:", json.dumps(info.get("trace", [{}])[0].get("data", {}),
                                  ensure_ascii=False)[:300])
        shot = a.run([{"op": "shot", "path": OUT, "hwnd": hwnd}])
        print("shot ok=%s err=%s" % (shot.get("ok"),
                                     json.dumps(shot.get("trace", [{}])[0].get("error"))[:160]))
        if os.path.exists(OUT):
            print("file bytes:", os.path.getsize(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
