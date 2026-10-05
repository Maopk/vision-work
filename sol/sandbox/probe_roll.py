#!/usr/bin/env python3
"""Trace one rollout move by move: why did it deal, why did it stop?

  python probe_roll.py --seed 1000
  python probe_roll.py --seed 1000 --cap 8 --eps 0 --noise 0

Prints every move with the value the policy gave it, how many candidates there
were, and how many were skipped because the resulting position had already been
visited `visit_cap` times - that last number is what ends a game.
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import spider_sandbox as B  # noqa: E402
import spider_solve as S  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--cap", type=float, default=None)
    ap.add_argument("--eps", type=float, default=None)
    ap.add_argument("--noise", type=float, default=None)
    ap.add_argument("--deal", type=float, default=None)
    ap.add_argument("--moves", type=int, default=800)
    ap.add_argument("--head", type=int, default=40, help="rows to print")
    a = ap.parse_args()
    w = B.load_policy()
    over = {}
    if a.cap is not None:
        over["visit_cap"] = a.cap
    if a.eps is not None:
        over["eps"] = a.eps
    if a.noise is not None:
        over["noise"] = a.noise
    if a.deal is not None:
        over["mv_deal"] = a.deal
    w.update(over)
    print(f"policy overrides: {over}  (cap={w['visit_cap']} eps={w['eps']} "
          f"noise={w['noise']} mv_deal={w['mv_deal']})")
    st0 = S.deal(random.Random(a.seed))
    tr: list = []
    win, path, end = B.rollout(st0, random.Random(a.seed * 7919 + 13), w,
                               max_moves=a.moves, trace=tr)
    deals = [k for k, t in enumerate(tr) if t["mv"] and t["mv"][0] == "d"]
    print(f"moves={len(path)}  deals at {deals}  win={bool(win)}  done={end[0]}  "
          f"face_down={sum(c[0] for c in end[1])}")
    for k, t in enumerate(tr[: a.head]):
        mv = t["mv"]
        who = ("DEAL" if mv[0] == "d" else f"{mv[1]:>2}->{mv[2]:<2} n={mv[3]}") if mv else "--"
        mark = " *" if mv and mv[0] == "d" else ""
        print(f"  {k:>4}. {who:<14} val={str(t['val']):>9} cands={t['cands']:<3} "
              f"skipped={t['skipped']:<3} moves={t['moves']:<3} best={t['best']}{mark}")
    if len(tr) > a.head:
        print(f"  ... {len(tr) - a.head} more rows")
        for k, t in enumerate(tr[-6:], len(tr) - 6):
            mv = t["mv"]
            who = ("DEAL" if mv[0] == "d" else f"{mv[1]:>2}->{mv[2]:<2} n={mv[3]}") if mv else "--"
            print(f"  {k:>4}. {who:<14} val={str(t['val']):>9} cands={t['cands']:<3} "
                  f"skipped={t['skipped']:<3} moves={t['moves']:<3} best={t['best']}")


if __name__ == "__main__":
    main()
