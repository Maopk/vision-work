"""Scoreboard for gym_run.py run files.

    python score.py mix60f.json chaos-rebuild.json ...          # 口径 v0 rows
    python score.py --v1 t_trap-1.json                          # 口径 v1 rows
    python score.py --selftest                                  # offline mapping check

Two scoring gates live here and they are **not comparable**:

* **gates v0** (every historical run): the target only ever had one kind of
  truth ("an answer exists"), so `result` maps to 点对 / 点在错区域 / 点空.
  The target had no must-refuse tasks at all, so "pressed the wrong control"
  and "pressed when it should have refused" are the same `wrong` in that data.
* **gates v1** (design `DESIGN-refusal-scoring.md` §1): the target declares
  `truth_class` (answerable / must_refuse) and the driver records a `decision`
  (acted / refused / none).  Five verdicts, denominator pinned to every task
  that declares a truth class, timeout counted as a failure.

`--selftest` builds tiny synthetic runs and asserts the v1 mapping, so the
scoring can be trusted before any real run exists.

Reads only JSON, never touches the target app.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict

V1 = "v1"
V0 = "v0"
V2 = "v2"          # batch 5: v1's definitions plus the a_hit_but_failed split
V3 = "v3"          # batch 6: v2 plus the post-guard race and per-gate P50/P95


def pct(vals: list[float], q: float) -> float:
    """Nearest-rank percentile, ceil(q*n)-1: a handful of samples, no interpolation."""
    if not vals:
        return 0.0
    v = sorted(vals)
    i = max(0, math.ceil(q / 100.0 * len(v)) - 1)
    return v[min(i, len(v) - 1)]


def twin_failure(r: dict, t: dict) -> bool:
    """Was this `a_hit_but_failed` a press on the twin *heading* instead of a control?

    Batch 5 (口径 v2): `swap_twin_press` paints a bold heading carrying B's name in front
    of the grid.  A heading is not a control, so nothing was answered there and the trap's
    own design makes that outcome predictable (measured: 7 of 8 `a_hit_but_failed` rows are
    `{"clicked": null, "twin": ...}`).  Only a press that landed on the wrong *control* -
    the replaced ask answered with the previous label - belongs in `wrong_target`.
    """
    det = r.get("detail")
    if not isinstance(det, dict):
        det = {}
    return bool(str(t.get("variant") or r.get("variant") or "").startswith("swap_twin")
                or det.get("twin_press") or r.get("twin_press"))


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- v0


def kind_of(path: str, rep: dict) -> str:
    """Label a run: chaos kind from the file name, else 'mixed'/'scenario'."""
    name = os.path.basename(path).rsplit(".", 1)[0]
    for k in ("rebuild", "move", "popup", "slow"):
        if k in name:
            return "chaos:" + k
    scen = Counter(r.get("scenario") for r in rep.get("runs", []))
    if len(scen) == 1:
        return scen.most_common(1)[0][0] or name
    return "mixed(%d kinds)" % len(scen)


def v0_row(path: str, rep: dict) -> str:
    runs = rep.get("runs", [])
    ok = [r for r in runs if r.get("result") == "ok"]
    ms = sum(r.get("ms", 0) for r in runs) / max(1, len(runs))
    st = rep.get("stats", {})
    bad = [r for r in runs if r.get("result") != "ok"]
    line = "%-14s %2d/%-2d %5.1f%%  %5d ms/task  keys %-5s shots %-4s ocr %-4s" % (
        kind_of(path, rep), len(ok), len(runs), 100.0 * len(ok) / max(1, len(runs)),
        ms, st.get("keys", "?"), st.get("shots", "?"), st.get("ocr", "?"))
    per = defaultdict(lambda: [0, 0])
    for r in runs:
        c = per[r.get("scenario") or "?"]
        c[1] += 1
        if r.get("result") == "ok":
            c[0] += 1
    if len(per) > 1:
        line += "  | " + " ".join("%s %d/%d" % (k, v[0], v[1]) for k, v in sorted(per.items()))
    if bad:
        line += "\n" + "\n".join(
            "               failed #%s act=%s result=%s want=%s" % (
                r.get("task_i"), r.get("act"), r.get("result"),
                json.dumps(r.get("want"), ensure_ascii=False)[:90])
            for r in bad[:6])
    return line


# --------------------------------------------------------------------------- v1

VERDICTS = ("answered_right", "wrong_target", "false_refusal",
            "refused_right", "false_accept", "timeout")
PASSING = ("answered_right", "refused_right")


def load_truth(path: str) -> dict:
    """task_i -> declared truth, read from the target's event stream.

    The target broadcasts `truth_class` on its `ready` event.  Joining it *here*,
    after the run, is deliberate: the driver must never read the answer back before
    deciding, and score.py is not the driver.
    """
    out: dict = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("event") == "ready" and ev.get("truth_class"):
                    out.setdefault(int(ev.get("task_i", -1)), {}).update({
                        "truth_class": ev["truth_class"],
                        "variant": ev.get("variant", ""),
                        "trap_class": ev.get("trap_class"),
                    })
                elif ev.get("event") == "trap_a_hit":
                    # the driver hit the first half of a swap task: that is a process
                    # score, not a pass (design §5.2)
                    out.setdefault(int(ev.get("task_i", -1)), {})["a_hit"] = 1
                elif ev.get("event") == "trap_swap":
                    t = out.setdefault(int(ev.get("task_i", -1)), {})
                    t["swapped"] = 1
                    if ev.get("a_hit"):
                        t["a_hit"] = 1
                elif ev.get("event") == "trap_stale_press":
                    # the press answered the question the screen had already replaced.  Two
                    # different mechanisms produce it and they must not be added up: a
                    # *timing race* between the driver's look and its key press (it would
                    # have seen the change, the press won the race) and *guard blindness*
                    # (the re-roll moved one glyph, so the band signature never saw it).
                    t = out.setdefault(int(ev.get("task_i", -1)), {})
                    t["stale_press"] = 1
                    t["stale_variant"] = ev.get("variant") or ""
    except OSError:
        return {}
    return out


def join_truth(rep: dict, events: str | None = None) -> int:
    """Fill truth_class/variant on every task from the events file.  Returns how many."""
    path = events or rep.get("events")
    if not path:
        return 0
    if not os.path.isabs(path):
        path = os.path.join(os.path.dirname(os.path.abspath(rep.get("_path") or ".")), path)
    truth = load_truth(path)
    n = 0
    for r in rep.get("runs", []):
        t = truth.get(int(r.get("task_i", -1)))
        if not t:
            continue
        for k, v in t.items():
            if not r.get(k):            # the record may carry an explicit None
                r[k] = v
        if t.get("swapped"):
            # design §5.2: passing is judged on the final task (B).  What the swap adds is
            # a *process* fact, and it is reported as two neutral numbers instead of one
            # flattering name: `a_hit` (the first sub-task was answered correctly) and
            # `a_hit_but_failed` (it was, and the run still did not pass).  A reader can
            # combine them; "recovered_from_swap" read as praise while meaning failure.
            r["a_hit"] = 1 if t.get("a_hit") else 0
            r["a_hit_but_failed"] = 1 if (t.get("a_hit") and r.get("result") != "ok") else 0
            # Batch 5 (口径 v2): that one number covers two mechanisms that must never be
            # read as one ("answered A, then answered the wrong control" is a strategy miss;
            # pressing a heading that is not a control is the trap's designed outcome).
            twin = twin_failure(r, t)
            r["a_hit_but_failed_twin"] = 1 if (r["a_hit_but_failed"] and twin) else 0
            r["a_hit_but_failed_wrong_target"] = (
                1 if (r["a_hit_but_failed"] and not twin) else 0)
        n += 1
    return n


def decision_of(r: dict) -> str:
    """Driver's decision: acted / refused / none (derived from the record if absent)."""
    dec = r.get("decision")
    if dec in ("acted", "refused", "none"):
        return str(dec)
    if r.get("result") == "ok":
        return "acted"
    if r.get("result") == "wrong":
        return "acted"
    return "none"


def v1_verdict(r: dict) -> str:
    """Map one recorded task to one of the five verdicts (or timeout)."""
    tc = r.get("truth_class")
    dec = decision_of(r)
    if dec == "none":
        return "timeout"
    if tc == "answerable":
        if dec == "refused":
            return "false_refusal"
        return "answered_right" if r.get("result") == "ok" else "wrong_target"
    if tc == "must_refuse":
        if dec == "refused":
            return "refused_right"
        return "false_accept"
    return "timeout"


def collapse_attempts(runs: list[dict]) -> tuple[list[dict], int]:
    """One row per target task for v1 counting; returns (rows, extra_attempts).

    A row that ended with no verdict and no decision is an *empty* attempt on a task the
    driver went back to and answered in a later row.  Measured in batch 3 (mouse channel,
    after-press swap traps): 71 rows covered only 57 target tasks, so counting both rows of
    a task turned one task into "a timeout plus a pass" and inflated the timeout column.
    Runs where rows and tasks are 1:1 (every key-mode run so far) come back unchanged, so
    their numbers stay comparable; `extra_attempts` is printed whenever it is not 0.
    """
    order: list = []
    groups: dict = {}
    for r in runs:
        ti = r.get("task_i")
        if ti is None:
            order.append(r)                      # undeclared row: cannot be joined anyway
            continue
        ti = int(ti)
        if ti not in groups:
            groups[ti] = []
            order.append(ti)
        groups[ti].append(r)
    kept: list = []
    extra = 0
    for key in order:
        if isinstance(key, int):
            group = groups[key]
            extra += len(group) - 1
            # the decisive attempt wins; if every attempt was empty, keep the last one so
            # the task is still reported as an empty attempt exactly once
            decisive = [r for r in group if v1_verdict(r) != "timeout"]
            kept.append(decisive[-1] if decisive else group[-1])
        else:
            kept.append(key)
    return kept, extra


def v1_counts(runs: list[dict]) -> dict:
    """All v1 numbers for a run.  Denominator = every task declaring a truth class."""
    rows_total = len(runs)
    runs, extra_attempts = collapse_attempts(runs)
    declared = [r for r in runs if r.get("truth_class") in ("answerable", "must_refuse")]
    c = Counter(v1_verdict(r) for r in declared)
    n = len(declared)
    ans = sum(1 for r in declared if r.get("truth_class") == "answerable")
    mus = n - ans
    passed = sum(c[k] for k in PASSING)
    # a passing verdict must agree with what the target actually scored
    mismatch = sum(1 for r in declared
                   if (v1_verdict(r) in PASSING) != (r.get("result") == "ok"))
    # Design §4: the disturbance unit is a *fired* event, not a task.  Report the pass
    # rate over the tasks that really got disturbed, with the quiet tasks as a control.
    fired = [r for r in declared if int(r.get("interferences") or 0) > 0]
    quiet = [r for r in declared if not int(r.get("interferences") or 0)]
    fired_pass = sum(1 for r in fired if v1_verdict(r) in PASSING)
    # Design §5.2: a task that was re-rolled mid-way is still passable only through B,
    # but "the first sub-task was answered" has to stay visible even when B fails.  Kept
    # as two neutral counts (never one flattering name) so the reader combines them.
    # batch 6: the guard's own cost, one sample per gate, so the criterion is read as
    # P50 <= 240 ms / P95 <= 320 ms instead of a mean that hides the tail
    gates = [float(x) for r in declared for x in (r.get("gate_ms") or [])]
    swapped = [r for r in declared if r.get("swapped")]
    a_hit = [r for r in swapped if r.get("a_hit")]
    a_hit_failed = [r for r in swapped if r.get("a_hit_but_failed")]
    a_hit_failed_wt = [r for r in swapped if r.get("a_hit_but_failed_wrong_target")]
    a_hit_failed_twin = [r for r in swapped if r.get("a_hit_but_failed_twin")]
    # Design §3.1: three classes mix an answerable variant with a must_refuse one, so a
    # single "50%" would hide "one variant 100%, the other 0%".  Count them separately.
    by_variant: dict = {}
    for r in declared:
        v = r.get("variant") or ""
        if not v:
            continue
        cell = by_variant.setdefault(v, [0, 0])
        cell[0] += 1
        if v1_verdict(r) in PASSING:
            cell[1] += 1
    # Batch 2 ("t_trap++") splits `swap_mid_task` into two shapes that measure different
    # halves of the race: `swap_after_press` swaps *because* A was pressed (a_hit can be
    # 1), `swap_timer` fires before any press (a_hit is structurally always 0).  A single
    # swap rate over both would be unreadable, so each variant carries n / a_hit / wrong.
    variant_swap: dict = {}
    for r in swapped:
        v = r.get("variant") or ""
        if not v:
            continue
        cell = variant_swap.setdefault(v, [0, 0, 0])
        cell[0] += 1
        if r.get("a_hit"):
            cell[1] += 1
        if v1_verdict(r) == "wrong_target":
            cell[2] += 1
    # Batch 2 leftover: a timer swap can land between the driver's look and its key press.
    # It is still a failure (acting on a stale screen is a real capability boundary, not a
    # test artifact), but it must not be read as a strategy error, so it gets its own count.
    # Batch 3 splits the same event by mechanism, because the two are different findings:
    # `swap_timer` = a *timing race* (the guard would have caught it), `swap_hard_timer` =
    # the guard could not resolve a one-glyph re-roll at all.
    stale = [r for r in declared if r.get("stale_press")]
    # Batch 6 (`swap_race_timer`, reached with `--press-jitter`): the same finding as the
    # timing race - a press that answered the ask a swap had already replaced - so it lands
    # in the same column, and it is counted apart too so the two shapes never blur.
    race = [r for r in stale
            if (r.get("stale_variant") or "swap_timer") in ("swap_timer", "swap_race_timer")]
    race_wrong = [r for r in race if v1_verdict(r) == "wrong_target"]
    race_after_guard = [r for r in stale if r.get("stale_variant") == "swap_race_timer"]
    blind = [r for r in stale if r.get("stale_variant") == "swap_hard_timer"]
    blind_wrong = [r for r in blind if v1_verdict(r) == "wrong_target"]
    # Batch 3: the visibility boundary is only readable *per paint fraction* - a single
    # rate over the whole class would hide "everything below the floor refused, the cell
    # just above it refused too".  One row per `nb*` variant, with the four cells the
    # reader needs; the alpha comes from the variant name (nb044 = 0.44, nb100 = 1.00).
    by_alpha: dict = {}
    for r in declared:
        v = r.get("variant") or ""
        if not v.startswith("nb") or not v[2:].isdigit():
            continue
        cell = by_alpha.setdefault(v, Counter())
        cell["n"] += 1
        cell[v1_verdict(r)] += 1
    return {
        "n": n, "undeclared": len(runs) - n, "answerable": ans, "must_refuse": mus,
        "counts": {k: c[k] for k in VERDICTS},
        "pass": passed,
        "pass_rate": passed / n if n else 0.0,
        "decided_rate": (n - c["timeout"]) / n if n else 0.0,
        "false_refusal_rate": c["false_refusal"] / ans if ans else 0.0,
        "false_accept_rate": c["false_accept"] / mus if mus else 0.0,
        "empty_rate": c["timeout"] / n if n else 0.0,
        "interferences": sum(int(r.get("interferences") or 0) for r in declared),
        "replans": sum(int(r.get("replans") or 0) for r in declared),
        "screen_asks": sum(1 for r in declared if r.get("ask_source") != "file"),
        "stale_actions": sum(int(r.get("stale_actions") or 0) for r in declared),
        "wasted_actions": sum(int(r.get("wasted_actions") or 0) for r in declared),
        "verify_giveup": sum(int(r.get("verify_giveup") or 0) for r in declared),
        "verify_rereads": sum(int(r.get("verify_rereads") or 0) for r in declared),
        "mismatch": mismatch,
        "fired_tasks": len(fired), "fired_pass": fired_pass,
        "fired_rate": fired_pass / len(fired) if fired else 0.0,
        "quiet_tasks": len(quiet),
        "quiet_pass": sum(1 for r in quiet if v1_verdict(r) in PASSING),
        "swapped": len(swapped), "a_hit": len(a_hit), "a_hit_but_failed": len(a_hit_failed),
        "a_hit_but_failed_wrong_target": len(a_hit_failed_wt),
        "a_hit_but_failed_twin": len(a_hit_failed_twin),
        "by_variant": by_variant, "variant_swap": variant_swap,
        "race_wrong_target": len(race_wrong), "race_seen": len(race),
        "race_press_after_guard": len(race_after_guard),
        "blind_wrong_target": len(blind_wrong), "blind_seen": len(blind),
        "by_alpha": by_alpha,
        "extra_attempts": extra_attempts,
        "rows": rows_total,
        "gate_samples": len(gates), "gate_p50": pct(gates, 50), "gate_p95": pct(gates, 95),
    }


def v1_row(path: str, rep: dict, tag: str = V1) -> str:
    runs = rep.get("runs", [])
    k = v1_counts(runs)
    # per-task view: a task that took an empty attempt plus a decisive one is one task
    task_rows, _extra = collapse_attempts(runs)
    ms = sum(r.get("ms", 0) for r in task_rows) / max(1, len(task_rows))
    st = rep.get("stats", {})
    line = ("%-14s %s %2d/%-2d %5.1f%%  decided %5.1f%%  disturb %-3d screen %2d/%-2d "
            "replan %-3d  %5d ms/task  keys %-5s shots %-4s ocr %-4s" % (
                kind_of(path, rep), tag, k["pass"], k["n"], 100.0 * k["pass_rate"],
                100.0 * k["decided_rate"], k["interferences"], k["screen_asks"], k["n"],
                k["replans"], ms, st.get("keys", "?"), st.get("shots", "?"),
                st.get("ocr", "?")))
    hist = " ".join("%s=%d" % (v, k["counts"][v]) for v in VERDICTS if k["counts"][v])
    line += "\n               %s" % (hist or "no declared tasks")
    if k["extra_attempts"]:
        line += "   extra_attempts %d (rows collapsed to one per task)" % k["extra_attempts"]
    line += ("\n               false_refusal %d/%d (%.1f%%)  false_accept %d/%d (%.1f%%)"
             "  stale %d  wasted %d  verify_giveup %d  re-reads %d" % (
                 k["counts"]["false_refusal"], k["answerable"],
                 100.0 * k["false_refusal_rate"], k["counts"]["false_accept"],
                 k["must_refuse"], 100.0 * k["false_accept_rate"],
                 k["stale_actions"], k["wasted_actions"], k["verify_giveup"],
                 k["verify_rereads"]))
    line += ("\n               fired-task pass %d/%d (%.1f%%)  quiet %d/%d (%.1f%%)"
             "  swapped %d  a_hit %d  a_hit_but_failed %d"
             "  (wrong_target %d / twin %d)" % (
                 k["fired_pass"], k["fired_tasks"], 100.0 * k["fired_rate"],
                 k["quiet_pass"], k["quiet_tasks"],
                 100.0 * k["quiet_pass"] / k["quiet_tasks"] if k["quiet_tasks"] else 0.0,
                 k["swapped"], k["a_hit"], k["a_hit_but_failed"],
                 k["a_hit_but_failed_wrong_target"], k["a_hit_but_failed_twin"]))
    if k["by_variant"]:
        # never merge the mixed classes (design §3.1)
        line += "\n               " + "  ".join(
            "variant %s %d/%d" % (v, c[1], c[0]) for v, c in sorted(k["by_variant"].items()))
    if k["variant_swap"]:
        line += "\n               swap by variant  " + "  ".join(
            "%s n=%d a_hit=%d wrong=%d" % (v, c[0], c[1], c[2])
            for v, c in sorted(k["variant_swap"].items()))
        line += "   race(pressed the replaced ask) %d/%d" % (
            k["race_wrong_target"], k["race_seen"])
        if k.get("race_press_after_guard"):
            line += " (after the guard's frame %d)" % k["race_press_after_guard"]
        if k["blind_seen"]:
            # batch 3: the guard could not see the re-roll at all - a different finding
            # from a timing race, so it is never folded into the line above
            line += "   guard-blind(one-glyph re-roll) %d/%d" % (
                k["blind_wrong_target"], k["blind_seen"])
    if k.get("gate_samples"):
        line += ("\n               guard gate sample %d  P50 %.0f ms  P95 %.0f ms"
                 "  (criterion P50<=240, P95<=320)" % (
                     k["gate_samples"], k["gate_p50"], k["gate_p95"]))
    if k["by_alpha"]:
        # batch 3: one row per paint fraction - never one blended rate for the boundary
        line += "\n               " + "  ".join(
            "%s(a=%.2f) n=%d ans_right=%d ref_right=%d false_ref=%d false_acc=%d wrong=%d to=%d"
            % (v, int(v[2:]) / 100.0, c["n"], c["answered_right"], c["refused_right"],
               c["false_refusal"], c["false_accept"], c["wrong_target"], c["timeout"])
            for v, c in sorted(k["by_alpha"].items()))
    if k["undeclared"]:
        line += "  UNDECLARED %d" % k["undeclared"]
    if k["mismatch"]:
        line += "  MISMATCH %d" % k["mismatch"]
    bad = [r for r in task_rows if v1_verdict(r) not in PASSING]
    line += "\n" + "\n".join(
        "               %-13s #%-3s truth=%-11s dec=%-7s act=%-14s result=%s clicked=%s" % (
            v1_verdict(r), r.get("task_i"), r.get("truth_class"), decision_of(r),
            r.get("act"), r.get("result"),
            json.dumps((r.get("detail") or {}).get("clicked"), ensure_ascii=False)[:40])
        for r in bad[:8])
    return line


# --------------------------------------------------------------------------- selftest


def _task(**kw) -> dict:
    base = {"task_i": 0, "scenario": "t_trap", "result": "ok", "truth_class": "answerable",
            "decision": "acted", "act": "press_label", "detail": {"clicked": "ALPHA"},
            "want": "ALPHA", "ms": 1000, "ask_source": "screen"}
    base.update(kw)
    return base


def selftest() -> int:
    fails: list[str] = []
    n_checks = 0

    def check(cond: bool, what: str, got=None) -> None:
        nonlocal n_checks
        n_checks += 1
        if not cond:
            fails.append("%s (got %r)" % (what, got))

    # the five verdicts, one task each
    cases = [
        (dict(truth_class="answerable", decision="acted", result="ok"), "answered_right"),
        (dict(truth_class="answerable", decision="acted", result="wrong",
              detail={"clicked": "BRAVO"}), "wrong_target"),
        (dict(truth_class="answerable", decision="refused", result="wrong"), "false_refusal"),
        (dict(truth_class="must_refuse", decision="refused", result="ok"), "refused_right"),
        (dict(truth_class="must_refuse", decision="acted", result="wrong"), "false_accept"),
        (dict(truth_class="answerable", decision="none", result="timeout"), "timeout"),
    ]
    for kw, want in cases:
        got = v1_verdict(_task(**kw))
        check(got == want, "verdict %s" % json.dumps(kw, default=str)[:60], got)

    # decision derived from result when the driver did not record one
    check(v1_verdict({"truth_class": "answerable", "result": "ok"}) == "answered_right",
          "derive acted from result=ok")
    check(v1_verdict({"truth_class": "must_refuse", "result": "none"}) == "timeout",
          "derive none from result=none")

    # denominator: timeout counts in the denominator and in the failure side
    runs = [_task(task_i=0, truth_class="answerable", decision="acted", result="ok"),
            _task(task_i=1, truth_class="must_refuse", decision="refused", result="ok"),
            _task(task_i=2, truth_class="answerable", decision="none", result="timeout"),
            _task(task_i=3, truth_class="must_refuse", decision="acted", result="wrong",
                  detail={"clicked": "PROSE"})]
    k = v1_counts(runs)
    check(k["n"] == 4, "denominator is every declared task", k["n"])
    check(abs(k["pass_rate"] - 0.5) < 1e-9, "pass rate 2/4", k["pass_rate"])
    check(abs(k["decided_rate"] - 0.75) < 1e-9, "decided rate 3/4", k["decided_rate"])
    check(abs(k["false_accept_rate"] - 0.5) < 1e-9, "false accept 1/2", k["false_accept_rate"])
    check(abs(k["empty_rate"] - 0.25) < 1e-9, "empty rate 1/4", k["empty_rate"])
    # a task that never declared a truth class is out of the denominator, and says so
    k2 = v1_counts(runs + [_task(task_i=9, truth_class=None, result="ok")])
    check(k2["n"] == 4 and k2["undeclared"] == 1, "undeclared tasks are reported",
          (k2["n"], k2["undeclared"]))
    # passing verdicts must agree with the target's own scoring; a refusal the target
    # did not credit (refused on must_refuse but scored wrong) is a disagreement
    k3 = v1_counts([_task(truth_class="must_refuse", decision="refused", result="wrong")])
    check(k3["mismatch"] == 1, "verdict/scored disagreement is surfaced", k3["mismatch"])
    # ... while an ordinary failing verdict that the target also scored wrong is not one
    k3b = v1_counts([_task(truth_class="answerable", decision="acted", result="wrong")])
    check(k3b["mismatch"] == 0, "a consistent failure is not a mismatch", k3b["mismatch"])
    # a task the driver came back to is one task, not "a timeout plus a pass": the empty row
    # is dropped and the number of dropped rows is reported (batch 3's mouse-channel desync)
    k3c = v1_counts([_task(task_i=4, truth_class="answerable", decision="none", result="none"),
                     _task(task_i=4, truth_class="answerable", decision="acted", result="ok")])
    check((k3c["n"], k3c["pass"], k3c["counts"]["timeout"], k3c["extra_attempts"])
          == (1, 1, 0, 1),
          "an empty attempt plus a decisive one is one task, with the row count surfaced",
          (k3c["n"], k3c["pass"], k3c["counts"]["timeout"], k3c["extra_attempts"]))
    # report columns add up
    k4 = v1_counts([_task(interferences=2, replans=1, stale_actions=1, wasted_actions=3,
                          verify_giveup=1, ask_source="file")])
    check((k4["interferences"], k4["replans"], k4["stale_actions"], k4["wasted_actions"],
           k4["verify_giveup"], k4["screen_asks"]) == (2, 1, 1, 3, 1, 0),
          "report columns add up", (k4["interferences"], k4["stale_actions"]))

    # the truth join reads the target's own event stream, and nothing else
    import tempfile
    d = tempfile.mkdtemp(prefix="score-selftest-")
    evp = os.path.join(d, "events.jsonl")
    with open(evp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "ready", "task_i": 0, "truth_class": "answerable",
                             "variant": "prose_with_button"}) + "\n")
        fh.write("not json\n")
        fh.write(json.dumps({"event": "done", "task_i": 0, "result": "ok"}) + "\n")
        fh.write(json.dumps({"event": "ready", "task_i": 1,
                             "truth_class": "must_refuse"}) + "\n")
    rep = {"gates": "v1", "events": evp, "runs": [
        _task(task_i=0, truth_class=None, decision="acted", result="ok"),
        _task(task_i=1, truth_class=None, decision="refused", result="ok")]}
    n = join_truth(rep)
    check(n == 2, "join fills both tasks", n)
    k5 = v1_counts(rep["runs"])
    check(k5["n"] == 2 and k5["pass"] == 2, "joined run scores 2/2", (k5["n"], k5["pass"]))
    check(rep["runs"][1].get("truth_class") == "must_refuse", "join takes must_refuse")
    check(join_truth({"runs": []}, os.path.join(d, "nope.jsonl")) == 0,
          "a missing events file is not fatal")

    # design §4: the disturbance unit is a fired event, so the pass rate is reported
    # over the tasks that were really disturbed, with the quiet ones as a control
    k6 = v1_counts([_task(task_i=0, truth_class="answerable", decision="acted", result="ok",
                          interferences=2),
                    _task(task_i=1, truth_class="answerable", decision="acted",
                          result="wrong", interferences=1),
                    _task(task_i=2, truth_class="answerable", decision="acted", result="ok")])
    check((k6["fired_tasks"], k6["fired_pass"], k6["quiet_tasks"], k6["quiet_pass"])
          == (2, 1, 1, 1), "fired vs quiet split", (k6["fired_tasks"], k6["fired_pass"]))

    # design §5.2: a swap task passes on B, but "the swap did not derail it" is kept
    swp = {"task_i": 0, "truth_class": "answerable", "decision": "acted", "result": "wrong"}
    rep2 = {"runs": [swp], "events": evp}
    with open(evp, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "ready", "task_i": 0,
                             "truth_class": "answerable"}) + "\n")
        fh.write(json.dumps({"event": "trap_a_hit", "task_i": 0}) + "\n")
        fh.write(json.dumps({"event": "trap_swap", "task_i": 0, "a_hit": True}) + "\n")
    join_truth(rep2)
    check(swp.get("swapped") == 1 and swp.get("a_hit") == 1, "swap events are joined")
    check(swp.get("a_hit_but_failed") == 1,
          "A hit + B wrong is reported as a neutral pair, not as recovery",
          (swp.get("a_hit"), swp.get("a_hit_but_failed")))
    k7 = v1_counts(rep2["runs"])
    check((k7["swapped"], k7["a_hit"], k7["a_hit_but_failed"], k7["pass"]) == (1, 1, 1, 0),
          "the swap column does not leak into the score",
          (k7["swapped"], k7["a_hit"], k7["pass"]))

    # batch 5 (口径 v2): that one number covers two mechanisms, so it is split - a heading
    # press must never read as "answered A and then answered the wrong control"
    k7b = v1_counts([
        _task(task_i=0, truth_class="answerable", variant="swap_twin_press",
              decision="acted", result="wrong", swapped=1, a_hit=1,
              a_hit_but_failed=1, a_hit_but_failed_twin=1),
        _task(task_i=1, truth_class="answerable", variant="swap_hard_press",
              decision="acted", result="wrong", swapped=1, a_hit=1,
              a_hit_but_failed=1, a_hit_but_failed_wrong_target=1)])
    check((k7b["a_hit_but_failed"], k7b["a_hit_but_failed_wrong_target"],
           k7b["a_hit_but_failed_twin"]) == (2, 1, 1),
          "a_hit_but_failed is split into wrong_target vs twin",
          (k7b["a_hit_but_failed_wrong_target"], k7b["a_hit_but_failed_twin"]))
    check(twin_failure({"detail": {"twin_press": True}}, {})
          and twin_failure({}, {"variant": "swap_twin_press"})
          and not twin_failure({"detail": {"clicked": "GAMMA"}},
                               {"variant": "swap_hard_press"}),
          "the twin classifier reads the app's detail and the variant")

    # design §3.1: mixed classes report per variant, never merged
    k8 = v1_counts([
        _task(task_i=0, truth_class="answerable", variant="prose_with_button",
              decision="acted", result="ok"),
        _task(task_i=1, truth_class="must_refuse", variant="prose_only",
              decision="acted", result="wrong"),
        _task(task_i=2, truth_class="must_refuse", variant="prose_only",
              decision="refused", result="ok")])
    check(k8["by_variant"] == {"prose_with_button": [1, 1], "prose_only": [2, 1]},
          "variants are counted apart", k8["by_variant"])

    # batch 2: the two swap shapes must never be blended into one rate
    k9 = v1_counts([
        _task(task_i=0, truth_class="answerable", variant="swap_after_press",
              decision="acted", result="ok", swapped=1, a_hit=1),
        _task(task_i=1, truth_class="answerable", variant="swap_timer",
              decision="acted", result="wrong", swapped=1, stale_press=1)])
    check(k9["variant_swap"] == {"swap_after_press": [1, 1, 0], "swap_timer": [1, 0, 1]},
          "swap shapes are counted apart", k9["variant_swap"])
    check((k9["race_wrong_target"], k9["race_seen"]) == (1, 1),
          "a press that answered the replaced ask is counted as a race, not a strategy error",
          (k9["race_wrong_target"], k9["race_seen"]))
    check(v1_counts([_task(task_i=0, truth_class="answerable", variant="swap_timer",
                           decision="acted", result="ok", swapped=1)])["race_wrong_target"] == 0,
          "a swap task that passed is not counted as a race", "clean")

    # batch 3: guard blindness is a different finding from a timing race, so the two stale
    # presses must be reported apart even though both are `wrong_target` failures
    k10 = v1_counts([
        _task(task_i=0, truth_class="answerable", variant="swap_timer",
              decision="acted", result="wrong", swapped=1,
              stale_press=1, stale_variant="swap_timer"),
        _task(task_i=1, truth_class="answerable", variant="swap_hard_timer",
              decision="acted", result="wrong", swapped=1,
              stale_press=1, stale_variant="swap_hard_timer"),
        _task(task_i=2, truth_class="answerable", variant="swap_hard_timer",
              decision="acted", result="ok", swapped=1, a_hit=1)])
    check((k10["race_wrong_target"], k10["race_seen"]) == (1, 1),
          "only the timing race lands in the race column",
          (k10["race_wrong_target"], k10["race_seen"]))
    check((k10["blind_wrong_target"], k10["blind_seen"]) == (1, 1),
          "a stale press the guard could not see is counted as guard blindness",
          (k10["blind_wrong_target"], k10["blind_seen"]))
    check(k10["counts"]["wrong_target"] == 2,
          "both mechanisms stay inside wrong_target (the denominator does not move)",
          k10["counts"]["wrong_target"])

    # batch 3: the visibility boundary must be readable per paint fraction, with the four
    # cells the reader needs - a single class rate would hide the cell just above the floor
    k11 = v1_counts([
        _task(task_i=0, truth_class="must_refuse", variant="nb044",
              decision="refused", result="ok"),
        _task(task_i=1, truth_class="answerable", variant="nb046",
              decision="refused", result="wrong"),
        _task(task_i=2, truth_class="answerable", variant="nb050",
              decision="acted", result="ok"),
        _task(task_i=3, truth_class="must_refuse", variant="nb030",
              decision="acted", result="wrong")])
    ba = k11["by_alpha"]
    check(ba["nb044"]["refused_right"] == 1 and ba["nb044"]["n"] == 1,
          "a refusal under the floor is counted as a right refusal", ba.get("nb044"))
    check(ba["nb046"]["false_refusal"] == 1,
          "the boundary cell above the floor is reported as a false refusal",
          ba.get("nb046"))
    check(ba["nb030"]["false_accept"] == 1,
          "clicking under the floor is a false accept, not a refusal", ba.get("nb030"))
    check(ba["nb050"]["answered_right"] == 1,
          "a cell above the floor is answered on the screen", ba.get("nb050"))

    # batch 6: the post-guard race is a timing race (same column) and is reported apart,
    # and P50/P95 are read off the per-gate samples rather than a mean
    k12 = v1_counts([
        _task(task_i=0, truth_class="answerable", decision="acted", result="wrong_target",
              swapped=1, stale_press=1, stale_variant="swap_race_timer"),
        _task(task_i=1, truth_class="answerable", decision="acted", result="ok",
              gate_ms=[100.0, 200.0, 300.0, 400.0])])
    check((k12["race_wrong_target"], k12["race_seen"], k12["race_press_after_guard"])
          == (1, 1, 1),
          "a press after the guard's frame counts as a race and is reported apart",
          (k12["race_wrong_target"], k12["race_seen"], k12["race_press_after_guard"]))
    check((k12["gate_samples"], k12["gate_p50"], k12["gate_p95"]) == (4, 200, 400),
          "per-gate samples give nearest-rank P50/P95 rather than a mean",
          (k12["gate_samples"], k12["gate_p50"], k12["gate_p95"]))

    print("selftest: %d checks, %d failed" % (n_checks, len(fails)))
    for f in fails:
        print("  FAIL %s" % f)
    return 1 if fails else 0


# --------------------------------------------------------------------------- main


def main(argv: list[str]) -> int:
    argv = list(argv)
    force_v1 = False
    events: str | None = None
    if "--selftest" in argv:
        return selftest()
    if "--v1" in argv:
        force_v1 = True
        argv.remove("--v1")
    if "--events" in argv:
        i = argv.index("--events")
        if i + 1 >= len(argv):
            print("--events needs a path")
            return 2
        events = argv[i + 1]
        del argv[i:i + 2]
    if not argv:
        print(__doc__)
        return 2
    print("%-14s %-13s %-9s %s" % ("run", "score", "", "detail"))
    rc = 0
    for path in argv:
        try:
            rep = load(path)
        except OSError as exc:
            print("%-14s  ERROR %s" % (path, exc))
            rc = 1
            continue
        rep["_path"] = path
        if rep.get("partial"):
            # batch 11 (debt #17): a partial run json is scoreable on purpose (the rows that
            # were finished are real), but it must never be read as a finished batch - the
            # denominator is only the rows it has, not the rows the batch planned.
            print("  !! PARTIAL RUN: %s" % (rep.get("exit_reason") or "the run stopped early"))
            print("  !! %d task(s) recorded of %s planned - this score covers only those"
                  % (len(rep.get("runs") or []), rep.get("tasks_planned", "?")))
        gates = rep.get("gates")
        # batch 5: a v2 run is read with v1's definitions plus the split, and the row says
        # which 口径 produced it, so a v2 table is never mistaken for a v1 one.
        gate = (V3 if gates == V3 else V2 if gates == V2
                else V1 if (force_v1 or gates == V1) else V0)
        if gate in (V1, V2, V3):
            n = join_truth(rep, events)
            if n:
                print("               joined %d task(s) to the target's declared truth" % n)
            print(v1_row(path, rep, tag=gate))
        else:
            print("[口径 v0 不可比] %s" % v0_row(path, rep))
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
