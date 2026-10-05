"""The sandbox's honest loop: screenshot -> read -> decide -> drag -> verify.

Runs against `spider_table.py` (the practice table, which can hand out its own
truth).  One step:

  1. one actor run: bring the table to the front, screenshot it
  2. read the shot in process with `spider_read`
  3. compare the read against the shadow state (what the table *should* show)
  4. pick a move with the sandbox policy, drag it with a second actor run
  5. re-shoot, re-read, compare again - the drag either landed or it did not

Nothing about the move is assumed: the next step acts on what step 5 saw, and
`--check-truth` presses `t` at the end so the table's own dump can be diffed
against the shadow (that proves every drag landed where it was meant to).

    loop.py --seed 1000 [--moves 8] [--dry] [--check-truth]
"""
from __future__ import annotations

import argparse
import json
import os
import random
import socket
import sys
import time

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SOL = os.path.dirname(HERE)
sys.path.insert(0, SOL)
sys.path.insert(0, HERE)
import spider_read as R          # noqa: E402
import spider_sandbox as SB      # noqa: E402
import spider_solve as S         # noqa: E402
import spider_table as T         # noqa: E402

ACTOR_HOME = os.environ.get("ACTOR_HOME", r"D:\DSH\dsh-actor")
TITLE = "Spider Practice Table"
PITCH = T.PITCH
STEP_UP = T.STEP_UP
MARGIN = (T.MARGIN_X, T.MARGIN_Y)
CARD_W, CARD_H = T.CARD_W, T.CARD_H
SEARCH_PITCH = R.FACE_PITCH          # what the reader measures on screen


def actor_port() -> int:
    try:
        with open(os.path.join(ACTOR_HOME, "port.txt")) as fh:
            return int(fh.read().strip())
    except OSError:
        return 8731


class Actor:
    def __init__(self) -> None:
        self.port = actor_port()
        self.calls = 0

    def call(self, req: dict, timeout: float = 120.0) -> dict:
        s = socket.create_connection(("127.0.0.1", self.port), timeout=timeout)
        try:
            s.sendall((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))
            buf = b""
            while b"\n" not in buf:
                chunk = s.recv(1 << 16)
                if not chunk:
                    break
                buf += chunk
        finally:
            s.close()
        self.calls += 1
        return json.loads(buf.decode("utf-8").splitlines()[0])

    def run(self, steps: list, **kw) -> dict:
        return self.call(dict({"op": "run", "steps": steps}, **kw))


# ------------------------------------------------------------------ reading


def shot(act: Actor, path: str) -> float:
    t0 = time.perf_counter()
    rep = act.run([
        {"op": "window", "mode": "front", "title_contains": TITLE},
        {"op": "sleep", "ms": 220},
        {"op": "shot", "path": path},
    ])
    if not rep.get("ok"):
        raise SystemExit("actor run failed: %s" % json.dumps(rep, ensure_ascii=False))
    return (time.perf_counter() - t0) * 1000.0


def read_shot(path: str, win: list) -> dict:
    im = Image.open(path).convert("RGB")
    arr, (ox, oy) = R.load(path, win)
    return R.read_board(arr, ox, oy, im=im)


def to_model(card: str) -> str:
    """The reader spells the ten `10` (MSC draws it that way); the model says T."""
    c = card.upper()
    return "T" + c[2:] if c.startswith("10") else c


def cols_by_x(bor: dict, xs: list) -> list:
    """Map the reader's columns onto the layout's column slots (nearest x)."""
    out = [None] * len(xs)
    for col in bor.get("columns", []):
        cxc = (col["x"][0] + col["x"][1]) / 2.0
        i = min(range(len(xs)), key=lambda j: abs(xs[j] + CARD_W / 2.0 - cxc))
        out[i] = col
    return out


def expected(st) -> list:
    """Visible cards per column, deepest first - the reader's own order."""
    done, cols, stock = st
    out = []
    for down, cards in cols:
        out.append([S.cs(c) for c in cards[down:]])
    return out


def compare(seen: list, want: list, downs_seen: list, downs_want: list) -> list:
    bad = []
    for i in range(len(want)):
        got = seen[i] or []
        if [c.upper() for c in got] != [c.upper() for c in want[i]]:
            bad.append("col%d cards read %s want %s" % (i, got, want[i]))
        if (downs_seen[i] or 0) != downs_want[i]:
            bad.append("col%d down read %s want %d" % (i, downs_seen[i], downs_want[i]))
    return bad


# ------------------------------------------------------------------ moving


def layout_xs(origin: list) -> list:
    return [origin[0] + MARGIN[0] + PITCH * i for i in range(10)]


def move_points(mv, cols: list, xs: list, origin: list):
    """Screen from/to for one move, using what the reader saw this step."""
    if mv[0] == "d":
        # the stock pile sits right of column 9; clicking felt there deals
        return (xs[9] + 24 + CARD_W // 2, origin[1] + MARGIN[1] + CARD_H // 2,
                xs[9] + 24 + CARD_W // 2, origin[1] + MARGIN[1] + CARD_H // 2)
    _, src, dst, n = mv
    sc = cols[src]
    if sc is None:
        return None
    n_face = sc.get("n_face") or 1
    y0 = sc["face_y"] + (n_face - n) * SEARCH_PITCH + 28
    x0 = (sc["x"][0] + sc["x"][1]) // 2
    dc = cols[dst]
    if dc is None or not (dc.get("cards") or []):
        return (x0, y0, xs[dst] + CARD_W // 2, origin[1] + MARGIN[1] + CARD_H // 2)
    y1 = dc["face_y"] + (dc["n_face"] - 1) * SEARCH_PITCH + 28
    x1 = (dc["x"][0] + dc["x"][1]) // 2
    return (x0, y0, x1, y1)


def truth_diff(seed: int, st) -> list:
    """The table's own dump against the harness's model (empty = they agree)."""
    path = os.path.join(HERE, "truth-%d.json" % seed)
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return ["no truth file"]
    tcols = [[c.upper() for c in col["cards"][col["down"]:]] for col in doc["columns"]]
    want = [[c.upper() for c in col] for col in expected(st)]
    out = []
    if tcols != want:
        out.append("cards %s vs %s" % (sum(tcols, []), sum(want, [])))
    if [c["down"] for c in doc["columns"]] != [d for d, _ in st[1]]:
        out.append("down counts %s vs %s"
                   % ([c["down"] for c in doc["columns"]], [d for d, _ in st[1]]))
    if doc.get("done") != st[0]:
        out.append("runs %s vs %s" % (doc.get("done"), st[0]))
    return out


def fmt_move(mv) -> str:
    if mv[0] == "d":
        return "deal"
    _, src, dst, n = mv
    return "col%d->col%d x%d" % (src, dst, n)


def pick(st, w: dict):
    cands = SB.alive_moves(st, w)
    if not cands:
        return None, []
    ranked = sorted(cands, key=lambda m: -SB.move_value(st, m, w))
    return ranked[0], ranked[:4]


# ------------------------------------------------------------------ main


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--moves", type=int, default=8)
    ap.add_argument("--origin", default="", help="x,y of the table canvas (default: read LAYOUT)")
    ap.add_argument("--shot", default=os.path.join(HERE, "loop.png"))
    ap.add_argument("--dry", action="store_true", help="decide but do not drag")
    ap.add_argument("--check-truth", action="store_true")
    ap.add_argument("--json-out", default="")
    a = ap.parse_args()

    if a.origin:
        origin = [int(v) for v in a.origin.split(",")]
    else:
        line = ""
        with open(os.path.join(HERE, "table-out.log"), encoding="utf-8") as fh:
            for row in fh:
                if row.startswith("LAYOUT"):
                    line = row
        origin = json.loads(line.split(" ", 1)[1])["origin"]
        if sum(origin) == 0:
            raise SystemExit("start the table first (LAYOUT origin is 0,0)")
    win = [origin[0], origin[1], origin[0] + 1674, origin[1] + 1082]
    xs = layout_xs(origin)
    act = Actor()
    w = SB.policy()
    st = T.deal_state(a.seed)

    print("loop: seed %d  origin %s  window %s  actor :%d  dry=%s"
          % (a.seed, origin, win, act.port, a.dry))
    report = []
    for step in range(a.moves + 1):
        t_shot = shot(act, a.shot)
        t0 = time.perf_counter()
        bor = read_shot(a.shot, win)
        t_read = (time.perf_counter() - t0) * 1000.0
        rc = cols_by_x(bor, xs)
        seen = [[to_model(c["rank"] + R.suit_char(c["suit"]))
                 for c in (col or {}).get("cards", [])] for col in rc]
        downs_seen = [(col or {}).get("down") for col in rc]
        want = expected(st)
        downs_want = [d for d, _ in st[1]]
        bad = compare(seen, want, downs_seen, downs_want)
        tbad = truth_diff(a.seed, st)
        n_vis = sum(len(c) for c in seen)
        print("step %2d  read %d cards  shot %4.0fms read %4.0fms  %s  truth %s"
              % (step, n_vis, t_shot, t_read,
                 "VERIFIED" if not bad else "MISMATCH: " + "; ".join(bad[:3]),
                 "SAME" if not tbad else "DIFF: " + "; ".join(tbad[:2])))
        report.append({"step": step, "seen": seen, "want": want,
                       "downs_seen": downs_seen, "mismatch": bad, "truth": tbad,
                       "ms_shot": round(t_shot, 1), "ms_read": round(t_read, 1)})
        if step == a.moves or not bor.get("ok", True):
            break
        mv, ranked = pick(st, w)
        if mv is None:
            print("step %2d: no legal move left" % step)
            break
        pts = move_points(mv, rc, xs, origin)
        if pts is None:
            print("step %2d: cannot place %s on what the reader saw" % (step, mv))
            break
        nxt = S.apply(st, mv)
        print("        move %-16s -> drag %s  (alts %s)"
              % (fmt_move(mv), tuple(int(v) for v in pts),
                 [fmt_move(m) for m in ranked[1:3]]))
        if not a.dry:
            t0 = time.perf_counter()
            rep = act.run([
                {"op": "window", "mode": "front", "title_contains": TITLE},
                {"op": "drag", "x1": int(pts[0]), "y1": int(pts[1]),
                 "x2": int(pts[2]), "y2": int(pts[3]), "steps": 24, "ms": 200},
                {"op": "sleep", "ms": 260},
            ])
            t_drag = (time.perf_counter() - t0) * 1000.0
            ok = rep.get("ok")
            print("        drag %s  %4.0fms" % ("ok" if ok else "FAILED", t_drag))
            report[-1]["move"] = list(mv)
            report[-1]["drag"] = [int(v) for v in pts]
            report[-1]["ms_drag"] = round(t_drag, 1)
            if not ok:
                break
        st = nxt
        if a.dry:
            break

    if a.check_truth and not a.dry:
        tbad = truth_diff(a.seed, st)
        print("truth check: %s" % ("SAME" if not tbad else "DIFFERENT - " + "; ".join(tbad)))
        report.append({"truth_file": "truth-%d.json" % a.seed, "same": not tbad})
    n_bad = sum(1 for r in report if r.get("mismatch") or r.get("truth"))
    print("done: %d steps, %d with a read mismatch, actor calls %d"
          % (len(report), n_bad, act.calls))
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1)
    return 1 if n_bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
