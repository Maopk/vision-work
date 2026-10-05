#!/usr/bin/env python3
"""Throwaway: what does the beam actually build, and why does it stop?

Prints, per depth: layer/candidate counts, the best state's score breakdown,
its legal move list and a compact board so the stall is visible.
"""
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import spider_solve as S          # noqa: E402
import spider_sandbox as B        # noqa: E402

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 3
width = int(sys.argv[2]) if len(sys.argv) > 2 else 64
depth_max = int(sys.argv[3]) if len(sys.argv) > 3 else 40
w = B.load_policy()
st0 = S.deal(random.Random(seed))


def board(st, tag=""):
    done, cols, stock = st
    parts = []
    for i, (d, cards) in enumerate(cols):
        up = " ".join(S.cs(c) for c in cards[d:]) or "-"
        parts.append(f"{i}:{d}|{up}")
    return f"{tag}done={done} stock={len(stock)}  " + "   ".join(parts)


print(board(st0, "start "))
seen = {st0}
parent = {}
layer = [(B.score(st0, w), st0)]
for d in range(depth_max):
    cands = []
    for _sc, st in layer:
        for mv in B.alive_moves(st, w):
            ns = S.apply(st, mv)
            if ns in seen:
                continue
            seen.add(ns)
            parent[ns] = (st, mv)
            cands.append((B.score(ns, w) + (w["deal_pen"] if mv[0] == "d" else 0.0), ns))
    if not cands:
        print(f"depth {d:>2}: NO CANDIDATES -> stop (seen={len(seen)})")
        print(board(layer[0][1], "best  "))
        print("  moves of best:", B.alive_moves(layer[0][1], w))
        print("  all moves    :", S.moves(layer[0][1]))
        break
    cands.sort(key=lambda x: -x[0])
    layer = cands[:width]
    best_sc, best = layer[0]
    ms = B.alive_moves(best, w)
    print(f"depth {d:>2}: layer={len(layer):>3} cand={len(cands):>4} new={len(seen):>6} "
          f"score={best_sc:8.0f} moves={len(ms)}")
    print("   ", board(best))
    if d >= 2 and d <= 6:
        print("    moves:", ms[:12])
