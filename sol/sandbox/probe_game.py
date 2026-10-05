#!/usr/bin/env python3
"""Look at how a search actually dies: play one deal and dump the end board.

  python probe_game.py --seed 1003 --breadth 1 --nodes 150000
  python probe_game.py --seeds 1000,1001,1002 --breadth 1

Prints per deal: stats, the end position, and the diagnostics that say *why* it
lost (face-down cards left, columns holding a single suit, runs completed).
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import spider_sandbox as B  # noqa: E402
import spider_solve as S  # noqa: E402


def diagnose(st) -> dict:
    done, cols, stock = st
    down = sum(c[0] for c in cols)
    exposed = sum(len(S.visible(c)) for c in cols)
    pure = 0
    for _d, cards in cols:
        up = S.visible((_d, cards))
        if up and len({S.suit_of(c) for c in up}) == 1:
            pure += 1
    empty = S.empty_cols(st)
    runs = sum(S.top_run(S.visible(c)) for c in cols)
    return {"done": done, "deals_left": len(stock) // 10, "down": down,
            "exposed": exposed, "empty": empty, "one_suit_cols": pure,
            "sum_top_runs": runs}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--seeds", default=None)
    ap.add_argument("--breadth", type=int, default=1)
    ap.add_argument("--nodes", type=int, default=150000)
    ap.add_argument("--policy", default=None)
    ap.add_argument("--board", action="store_true", help="print the end position")
    ap.add_argument("--rollouts", type=int, default=0,
                    help="instead of dfs: play N rollouts and dump each one")
    a = ap.parse_args()
    w = B.load_policy(a.policy) if a.policy else B.load_policy()
    seeds = ([int(x) for x in a.seeds.split(",")] if a.seeds else [a.seed])
    for seed in seeds:
        st0 = S.deal(random.Random(seed))
        if a.rollouts:
            rng = random.Random(seed * 7919 + 13)
            print(f"=== deal #{seed}: {a.rollouts} rollouts ===")
            best = st0
            for k in range(a.rollouts):
                win, path, end = B.rollout(st0, rng, w)
                d = diagnose(end)
                deals_used = 5 - d["deals_left"]
                print(f"  r{k:<3} moves={len(path):<4} deals_used={deals_used} "
                      f"done={d['done']} face_down={d['down']} exposed={d['exposed']} "
                      f"empty={d['empty']} top_runs={d['sum_top_runs']}"
                      f"{'  WIN' if win else ''}")
                if end[0] > best[0]:
                    best = end
            print(S.show(best, f"    best of deal #{seed}: "))
            continue
        path, stats = B.dfs(st0, w, breadth=a.breadth, node_limit=a.nodes,
                            rng=random.Random(seed))
        end = stats.get("best_state", stats.get("end", st0))
        if path:
            cur = st0
            for mv in path:
                cur = S.apply(cur, mv)
            end = cur
        d = diagnose(end)
        print(f"--- deal #{seed}  breadth={a.breadth}  exp={stats['exp']}  "
              f"deals_made={stats['deals']}  best_done={stats['best_done']}  "
              f"{stats['ms']:.0f} ms")
        print(f"    end: done={d['done']} deals_left={d['deals_left']} "
              f"face_down={d['down']} exposed={d['exposed']} empty={d['empty']} "
              f"one_suit_cols={d['one_suit_cols']} sum_top_runs={d['sum_top_runs']}  "
              f"score={B.score(end, w):.0f}")
        if a.board:
            print(S.show(end, f"    deal #{seed}: "))


if __name__ == "__main__":
    main()

