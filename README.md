# vision-work

A **behaviour audit range for GUI agents** — a self-built target, a fully blind driver, and a scorer that counts "clicked right", "clicked wrong" and "refused right" as three different things.

**Scope**: audit and measurement · **Not**: a pass-rate leaderboard, or a claim about any model's ability

> Every number in this repository comes from a scripted run and is scored by `score.py`. The scores themselves live in [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) — this README deliberately states none of them.

**English** · [中文](README.zh-CN.md)

## What this is

Three programs that deliberately do not share a source:

| piece | file | what it does |
|---|---|---|
| target | `sol/sandbox/gym_app.py` | one Tk window posing random tasks — including families that must be refused — with four injectable kinds of disturbance (`move` / `slow` / `popup` / `rebuild`) |
| driver | `sol/sandbox/gym_run.py` | sees only pixels, through the local actor service; reads the task off the screen, gates before pressing, re-plans when the screen changes underneath it |
| scorer | `sol/sandbox/score.py` | turns a run's JSON into six verdict classes, with the denominators declared in advance |

The driver never receives ground truth: it reads the instruction from the screen and clicks what it was told to click. That is the point of the range — it measures behaviour under disturbance, *including* the behaviour of refusing, which a single pass-rate figure hides.

## What this is not

- Not a leaderboard: no model is ranked here.
- Not a claim about absolute ability: runs are single-machine, Windows-only, and tied to one operator's environment.
- Not a single pass rate: verdicts are split, denominators are declared, and the measurement gates are versioned (v0–v3). Two batches may only be compared inside the same gate — the rules are in [`audit/HANDOFF.md`](audit/HANDOFF.md) §2, the gate history in [`audit/SCORE-history.md`](audit/SCORE-history.md).

## Layout

```
README.md  README.zh-CN.md  CHANGELOG.md  LICENSE
audit/STATE.md                   current state of the line (continuation point at the top, debt table in §7)
audit/HANDOFF.md                 the three pieces, measurement gates, one-line commands, known blind spots
audit/DESIGN-refusal-scoring.md  why the verdicts are split apart (requirement + scoring design)
audit/REPORT.md                  the write-up, draft v0.1 (8 chapters + 2 appendices)
audit/REPORT-draft.md            chapter skeleton and source pointers (kept on purpose)
audit/SCORE-history.md           one-page history of the measurement gates
sol/sandbox/SCORE.md       every batch result, with per-batch reading notes
sol/sandbox/               the three programs, the probes, the batch evidence JSON
```

## Requirements

- Windows with a desktop session, and the local actor service listening on `:8731`.
- The interpreter used for every batch: `D:\DSH\.venvs\vision-ci\Scripts\python.exe` (Python 3.12, Pillow 12).
- Text reading shells out to Tesseract; the executable path is pinned in `sol/sandbox/gui_see.py:18` and must be changed for another machine.
- Exactly one target window at a time.

## Quick start

Start runs from the Windows side with a normal window; `--bg` keeps a run off your foreground.

```powershell
$py = 'D:\DSH\.venvs\vision-ci\Scripts\python.exe'
cd D:\DSH\vision-work\sol\sandbox

# dry run first — 2 tasks, to prove the input channel is live
& $py gym_run.py --scenario t_trap5 --tasks 2 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out dry.json

# mouse channel — the per-task comparable line
& $py gym_run.py --scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out my-run.json

# key channel with disturbance — exploratory line, never merged into the fixed line
& $py gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out my-chaos.json

# score it immediately: the target overwrites its events file on the next launch
& $py score.py my-run.json
& $py score.py --selftest
```

Exit codes: `0` every task ok · `1` a complete run containing failures · `3` a **partial** run (the driver saved what it had instead of dying — partial scores are never comparable with a complete batch). Note that `--max-repeat` counts *consecutive tasks that failed to advance*, not retries within a task.

## Where to read what

| question | document |
|---|---|
| what were the scores, batch by batch | [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) |
| can batch A be compared with batch B | [`audit/SCORE-history.md`](audit/SCORE-history.md), then `audit/HANDOFF.md` §2 |
| how do I re-run it, and what is known to be broken | [`audit/HANDOFF.md`](audit/HANDOFF.md) §3 and §4 |
| why "refused right" is a separate count | [`audit/DESIGN-refusal-scoring.md`](audit/DESIGN-refusal-scoring.md) |
| the finished argument | [`audit/REPORT.md`](audit/REPORT.md) |
| what is being worked on right now | [`audit/STATE.md`](audit/STATE.md) |

## Skill

The operating procedure for this line lives outside the repository, as a local skill at
`D:\DSH\skills\gui-audit-gym\SKILL.md` (the harness discovers skills from `D:\DSH\skills\`; the file is deliberately not duplicated here).

## License

MIT — see [`LICENSE`](LICENSE).
