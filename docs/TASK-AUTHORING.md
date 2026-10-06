# TASK-AUTHORING — how a task family is added

**Status: the task set is hard-coded in the target.** There is no plugin registry: a
task family is a method in `../sol/sandbox/gym_app.py` plus an entry in a plan table.
This document is the honest map of that path, so that adding the next family does not
require re-reading the whole app. Where the design *reasoning* lives is
[`../audit/DESIGN-refusal-scoring.md`](../audit/DESIGN-refusal-scoring.md); the
per-family design notes are `DESIGN-18` / `DESIGN-21` next to it in `../audit/`.

## 1. The four moving parts

| piece | where | what it is |
|---|---|---|
| a **scenario** | `t_<name>()` in `gym_app.py` (`t_trap` … `t_trap5`, `:976`–`:1015`) | what the target plays when the driver asks for `--scenario t_trap5`. The non-adversarial families (`t_button`, `t_rows`, `t_form`, `t_toggle`, `t_menu`, `t_chips`, `:659`–`:861`) double as the random mix |
| a **plan** | `TRAP_PLAN` `:78`, `TRAP_PLAN2` `:99`, `TRAP_PLAN3` `:122`, `TRAP_PLAN4` `:147`, `TRAP_PLAN5` `:162` | a list of `(class, variant)` tuples, written out explicitly. `TRAP_PLAN5` = plan 4 verbatim + ten `swap_race_timer` — that is how a later batch keeps its first N tasks byte-identical to an earlier one under the same seed |
| a **class builder** | `_trap_<class>(self, variant)` (`:1127`–`:1298`) | paints the screen for one task and declares its truth. The dispatcher is literally `getattr(self, "_trap_" + cls)(variant)` |
| the **arming call** | `_trap_task(...)` `:1017` | puts the refuse key on the map, describes the ask, and returns the task dict with its `truth` block |

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
   emits `ready` with `truth_class` / `variant` / `trap_class` (`:536`) and writes the
   same truth into its state file; the scorer joins it from there **after** the run. The
   driver reads pixels only. Feeding truth to the driver (or into a failure record)
   breaks the measurement — it is the one rule that has its own section in
   [`../audit/STATE.md`](../audit/STATE.md).
3. **The refuse key is protocol, not answer.** It is offered on *every* trap task,
   answerable ones included, so its presence on screen says nothing about whether
   refusing is right here (`:1023`–`:1027`).

The target scores itself too (`_trap_press` `:1040`, `_refuse` `:1031`). Two verdicts of
the same task — the target's own `result` and the scorer's joined verdict — must agree;
when they do not, suspect the events file (see
[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) §7).

## 3. Checklist for a new family

1. **Write the builder** `_trap_<class>(self, variant)`: paint the controls, then call
   `self._trap_task(cls, variant, truth_class=..., want=..., ask=..., controls=[...])`.
   Keep the salient-but-wrong thing on screen — that is the family's whole point.
2. **Register it in a plan** with an explicit count per variant. The plans state their
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
   `popup` / `rebuild`) and the chaos planner (`_plan_chaos` `:552`) live in the same
   file; a new kind of disturbance is a change to the app *and* to the driver's recovery
   path.
7. **Verify, in this order**: dry run with `--tasks 2` (the channel is live), then
   `score.py --selftest` (the scorer is intact), then a full batch, then **declare a new
   line**: write the numbers into [`../sol/sandbox/SCORE.md`](../sol/sandbox/SCORE.md)
   with its gate and its `scripts_sha`, and the reasoning into a `DESIGN-*.md` in
   `../audit/`.

## 4. What this document is not

- Not a promise of a stable API: the plan tables and the class builders are internal to
  one file, and they are expected to change with the next batch.
- Not a substitute for the design documents: *why* refusal is a verdict of its own, and
  *why* the denominators are declared before the run, is
  [`../audit/DESIGN-refusal-scoring.md`](../audit/DESIGN-refusal-scoring.md).
- Not a way to reproduce the author's numbers: the numbers are single-machine, and the
  method — not the figures — is what travels.

## 5. Manifest v1 — designed, not implemented

The five plan tables are literals inside the target (`TRAP_PLAN`, `PLAN2`, `PLAN3`,
`PLAN4`, `PLAN5` in `sol/sandbox/gym_app.py`). The planned v1 moves them into a
JSON manifest beside the scripts, so that a new family becomes a **data** edit. This
section records the design; **as of stage 3.4 nothing loads a manifest.**

*What it buys*: a new family that reuses an existing renderer becomes one manifest entry
plus a scenario name that points at it — no `.py` edit, therefore no `scripts_sha` break.
*What it does not buy*: a family with a new **visual form** still needs a `_trap_*`
builder and a `t_trapN` scenario method. The manifest carries data, not rendering.

Schema sketch:

```json
{"plans": {"trap": [["prose_same_word", "same_word"], ...], "trap2": [...]},
 "scenarios": [{"name": "t_trap5", "plan": "trap4", "append": ["swap_mid_task", "swap_race_timer"], "repeat": 10}]}
```

The `plan` + `append` + `repeat` form is deliberate: `t_trap5` is defined today as
`TRAP_PLAN4 + [("swap_mid_task", "swap_race_timer")] * 10`, and the manifest has to express
that derivation instead of duplicating 48 tuples.

*The gate is an offline equivalence check, not a batch*: for every scenario, the loaded
manifest must equal the literals frozen in the previous commit (`git show <old-commit>:
sol/sandbox/gym_app.py`), tuple for tuple, before any batch runs. A same-seed batch is not
a usable equivalence test here — a sequence drift would surface as *a different batch*, not
as a failing assertion.

*Why stage 3.4 did not implement it*: 3.4 landed the `viewport` truth class (a change of
meaning) and the manifest is a change of structure whose acceptance criterion is precisely
"the task sequences did not move". Landing both in one commit would make the two
unattributable, and 3.4 forbids batch runs, so the end-to-end check would have to wait.
The cost of splitting is one more `gym_app.py` sha break — accepted, recorded here.
