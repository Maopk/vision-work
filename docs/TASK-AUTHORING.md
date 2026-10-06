# TASK-AUTHORING — how a task family is added

**Status: the task order is data; the renderers are still code.** The five plan tables
live in [`../sol/sandbox/plans.v1.json`](../sol/sandbox/plans.v1.json) (manifest v1,
stage 3.6) and are loaded at import by `gym_app.py`. There is still no plugin registry: a
task family is a method in `../sol/sandbox/gym_app.py` plus its runs in that manifest.
This document is the honest map of that path, so that adding the next family does not
require re-reading the whole app. Where the design *reasoning* lives is
[`../audit/DESIGN-refusal-scoring.md`](../audit/DESIGN-refusal-scoring.md); the
per-family design notes are `DESIGN-18` / `DESIGN-21` next to it in `../audit/`.

## 1. The four moving parts

| piece | where | what it is |
|---|---|---|
| a **scenario** | `t_<name>()` in `gym_app.py` (`t_trap` … `t_trap5`, `:966`–`:1005`) | what the target plays when the driver asks for `--scenario t_trap5`. The non-adversarial families (`t_button`, `t_rows`, `t_form`, `t_toggle`, `t_menu`, `t_chips`, `:648`–`:851`) double as the random mix |
| a **plan** | `../sol/sandbox/plans.v1.json` (loaded by `_load_plans()` `:87`; registered as `TRAP_PLAN` … `TRAP_PLAN5` at `:110`–`:151`) | a list of `(class, variant)` **runs** — `[[class, variant], n]`. `trap5` is written as `base: trap4` + ten `swap_race_timer`: that is how a later batch keeps its first N tasks byte-identical to an earlier one under the same seed |
| a **class builder** | `_trap_<class>(self, variant)` (`:1116`–`:1287`) | paints the screen for one task and declares its truth. The dispatcher is literally `getattr(self, "_trap_" + cls)(variant)` |
| the **arming call** | `_trap_task(...)` `:1007` | puts the refuse key on the map, describes the ask, and returns the task dict with its `truth` block |

A scenario is therefore three lines:

```python
def t_trap6(self) -> dict:
    cls, variant = TRAP_PLAN6[self.trap_i % len(TRAP_PLAN6)]
    self.trap_i += 1
    return getattr(self, "_trap_" + cls)(variant)
```

## 2. The truth protocol — what makes a task scorable

`_trap_task` returns

```python
{"scenario": ..., "ask": "DO: ...",
 "truth": {"truth_class": "answerable" | "must_refuse",
           "want": <what a correct press must hit>, "variant": ...,
           "class": ..., "controls": [...], "refuse_key": ...}}
```

Three consequences worth knowing before you write a family:

1. **`truth_class` decides the denominator.** `answerable` tasks count in the
   false-refusal denominator, `must_refuse` tasks in the false-accept denominator.
   Adding a class therefore moves the denominators of every later batch — which is
   exactly why a changed plan is a **new line**, not an extension of an old one.
2. **The truth rides the event stream, never the driver's decision path.** The target
   emits `ready` with `truth_class` / `variant` / `trap_class` (`:526`) and writes the
   same truth into its state file; the scorer joins it from there **after** the run. The
   driver reads pixels only. Feeding truth to the driver (or into a failure record)
   breaks the measurement — it is the one rule that has its own section in
   [`../audit/STATE.md`](../audit/STATE.md).
3. **The refuse key is protocol, not answer.** It is offered on *every* trap task,
   answerable ones included, so its presence on screen says nothing about whether
   refusing is right here (see `_trap_task`).

The target scores itself too (`_trap_press` `:1030`, `_refuse` `:1023`). Two verdicts of
the same task — the target's own `result` and the scorer's joined verdict — must agree;
when they do not, suspect the events file (see
[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) §7).

## 3. Checklist for a new family

1. **Write the builder** `_trap_<class>(self, variant)`: paint the controls, then call
   `self._trap_task(cls, variant, truth_class=..., want=..., ask=..., controls=[...])`.
   Keep the salient-but-wrong thing on screen — that is the family's whole point.
2. **Register it in the manifest** (`sol/sandbox/plans.v1.json`) with an explicit count
   per variant, and add its one-line registration in `gym_app.py`. The plans state their
   variants separately (`prose_with_button` vs `prose_only`, each alpha value, each swap
   shape) so that a finished run can never be read as one blended rate for two different
   questions. Do not collapse variants into "× N" if they measure different things.
3. **Decide the denominator effect** and say it out loud in `../audit/HANDOFF.md` §2 (the
   citation rules): which old numbers does this family make incomparable?
4. **Check the channel.** A family judged from a `[k]` hint badge is keyboard-only; a
   family whose salient feature is a heading, a fade, or a drag needs a **real mouse** —
   Tk ignores posted mouse messages, so a `--bg` mouse run cannot see it.
5. **Make sure the driver can perceive it.** The driver only knows pixels. If the family
   needs a read the driver does not do yet, that is a `gym_run.py` change, which breaks
   `scripts_sha` — and a broken `scripts_sha` is a comparability statement, not a
   bookkeeping detail.
6. **Disturbances are hard-coded too.** The four injectable kinds (`move` / `slow` /
   `popup` / `rebuild`) and the chaos planner (`_plan_chaos` `:541`) live in the same
   file; a new kind of disturbance is a change to the app *and* to the driver's recovery
   path.
7. **Verify, in this order**: dry run with `--tasks 2` (the channel is live), then
   `score.py --selftest` (the scorer is intact), then a full batch, then **declare a new
   line**: write the numbers into [`../sol/sandbox/SCORE.md`](../sol/sandbox/SCORE.md)
   with its gate and its `scripts_sha`, and the reasoning into a `DESIGN-*.md` in
   `../audit/`.

## 4. What this document is not

- Not a promise of a stable API: the manifest has a `schema` number and is meant to be
  edited, the class builders are internal to one file, and both are expected to change
  with the next batch.
- Not a substitute for the design documents: *why* refusal is a verdict of its own, and
  *why* the denominators are declared before the run, is
  [`../audit/DESIGN-refusal-scoring.md`](../audit/DESIGN-refusal-scoring.md).
- Not a way to reproduce the author's numbers: the numbers are single-machine, and the
  method — not the figures — is what travels.

## 5. Manifest v1 — implemented (stage 3.6)

The five plan tables are **data** now: [`../sol/sandbox/plans.v1.json`](../sol/sandbox/plans.v1.json),
loaded at import by `_load_plans()` in `sol/sandbox/gym_app.py` and registered one line
per plan. A plan is a list of **runs** — `[[class, variant], n]` = n consecutive identical
entries — and a plan may start from another one, which is how `trap5` is stored as
`base: trap4` + ten `swap_race_timer` instead of duplicating 48 tuples:

```json
"trap5": {"note": "...", "base": "trap4",
          "runs": [[["swap_mid_task", "swap_race_timer"], 10]]}
```

What that buys: a family that reuses an existing renderer is added by editing data (runs
plus a short `note`), and the plan-to-scenario wiring is two lines in the app — a
registration and a `t_trapN` method that slices the list. What it does **not** buy is a
plugin system: the manifest carries *task order, scenario choice and variant combination*,
never rendering. A new visual shape — a new control, a new failure mode of seeing — still
needs its `_trap_*` builder and its scenario method in `gym_app.py`, and the boundary is
written into the manifest itself (`not_a_plugin_system`) so it cannot be mistaken for a
roadmap. Renderers stay shared on purpose: a family that reuses a shape needs no new
painting, and one that invents a shape is a code change by definition.

**Why `base` is in the schema**: `trap5`'s first 38 entries are `trap4`'s verbatim, which
is what keeps the frozen core-14 subset meeting the same words under the same seed. A
manifest that spelled the 48 tuples out could drift from `trap4` by one row and quietly
break that comparison; `base` makes the derivation the only possible reading.

**The gate is an offline equivalence check, not a batch.** The 266 entries were compared
tuple-for-tuple across three sources — the literals frozen in the previous commit
(`git show <old-commit>:sol/sandbox/gym_app.py`), the working tree through the loader, and
the manifest expanded independently of the loader — plus a separate assertion that
`trap5 == trap4 + 10 races`. Then all 13 scenarios dry-ran 2 tasks to show the wiring is
live. A same-seed batch is not a usable equivalence test here: a sequence drift would
surface as *a different batch*, not as a failing assertion.

**What a manifest edit costs in comparability**: `plans.v1.json` is in `scripts_sha`'s
covered list (stage 3.6b) and every new run json carries `scripts_sha_files`, so "same
`scripts_sha`, different task order" is no longer expressible. Changing a plan still
starts a new line for that scenario — the rules are in
[`../audit/SCORE-history.md`](../audit/SCORE-history.md) §1.1 and §3.
