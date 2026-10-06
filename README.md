# vision-work

A **behaviour audit range for GUI agents** — a self-built target, a fully blind driver, and a scorer that counts "clicked right", "clicked wrong" and "refused right" as three different things.

**Scope**: audit and measurement · **Not**: a pass-rate leaderboard, or a claim about any model's ability

**Status**: **v1.0** — the interfaces are frozen (run json `schema: 1`, the citation rules, the scoreboard's measurement gate). "Frozen" means the interfaces, **not** development: new scenario families go to v1.x or to another repository — see [OPENSOURCE-READINESS.md](OPENSOURCE-READINESS.md) §6.

> Every number in this repository comes from a scripted run and is scored by `score.py`. The scores themselves live in [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) — this README deliberately states none of them.

**English** · [中文](README.zh-CN.md)

## Why this exists

A pass rate answers one question — did the agent end up doing the right thing? It cannot
answer the questions this range was built for.

- **Refusing is a behaviour, not a miss.** A single pass rate folds "clicked the wrong
  thing" and "correctly declined to click anything" into the same cell, and those are
  opposite outcomes: one is a mistake, the other is the correct reading of a screen that
  holds no legal control. Here they are counted separately, with their denominators
  declared before the run.
- **The hard part is noticing that the screen changed under you.** A driver that read
  the screen once and pressed is a different object from one that re-read it, noticed
  the value had moved, and re-planned. The target injects exactly that — value changes,
  shifts, popups, late answers — so the run measures behaviour under disturbance rather
  than behaviour on a still picture.
- **What travels is the method, not the numbers.** OCR, fonts and DPI all sit inside the
  loop, so every figure here is single-machine and a fresh clone will not reproduce the
  author's. It *will* produce its own, scored by the same rules and comparable inside the
  same gate. That is the deliverable: a run you can re-run and argue about, not a
  leaderboard.

**Who needs it**: people building or testing GUI agents — anyone who has to say what
their agent does when the interface moves under it, and needs that answer to be
evidence rather than a feeling.

## What this is

Three programs that deliberately do not share a source:

| piece | file | what it does |
|---|---|---|
| target | `sol/sandbox/gym_app.py` | one Tk window posing random tasks — including families that must be refused — with four injectable kinds of disturbance (`move` / `slow` / `popup` / `rebuild`) |
| driver | `sol/sandbox/gym_run.py` | sees only pixels, through the local actor service; reads the task off the screen, gates before pressing, re-plans when the screen changes underneath it |
| scorer | `sol/sandbox/score.py` | turns a run's JSON into six verdict classes, with the denominators declared in advance |

The driver never receives ground truth: it reads the instruction from the screen and clicks what it was told to click. That is the point of the range — it measures behaviour under disturbance, *including* the behaviour of refusing, which a single pass-rate figure hides.

Extending it is a first-class path, not an afterthought: [`docs/TASK-AUTHORING.md`](docs/TASK-AUTHORING.md)
says where a task family is defined, what the truth-class protocol requires, and what to change.

## Ten minutes to a scored run

1. **Install** — an interactive Windows desktop session, Python 3.12, the PC actor
   service, and Tesseract. Exact versions, the two environment variables, and what
   happens when each is missing: [`docs/QUICKSTART.md`](docs/QUICKSTART.md).
2. **Run** — from a normal Windows shell, in `sol/sandbox`:

   ```powershell
   $PY = 'python'   # your 3.12 interpreter, with numpy + Pillow
   & $PY gym_run.py --scenario t_trap5 --tasks 2 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out dry.json
   & $PY score.py dry.json
   & $PY score.py --selftest
   ```

   A good run exits `0` with every task ok, and leaves three files behind
   (`dry.json`, `dry-state.json`, `dry-events.jsonl` — keep them together).
3. **If it fails** — [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) is a list of
   symptom → cause → fix, in the order you are likely to meet it.

## Do you qualify?

Four things have to be true. They are a pre-flight check, not a gate — every one of them
produces a specific error message rather than a silent wrong number.

- **Windows with an interactive desktop session.** The target is a Tk window and the
  driver reads real pixels; a run started from a service or a background job comes up
  off-screen and scores an empty screen.
- **The actor service is running and answers a ping.** It is a separate project — this
  repository drives it, it does not contain it.
- **Tesseract is installed, or `TESS` points at it.** The reader reads the task off the
  screen with OCR; without it the run stops and says so.
- **Exactly one target window is on screen.** The driver refuses to start when it counts
  more, because the count is what tells it *which* window to drive.

## What this is not

- Not a leaderboard: no model is ranked here.
- Not a claim about absolute ability: runs are single-machine, Windows-only, and tied to one operator's environment.
- Not a single pass rate: verdicts are split, denominators are declared, and the measurement gates are versioned (v0–v3). Two batches may only be compared inside the same gate — the rules are in [`audit/HANDOFF.md`](audit/HANDOFF.md) §2, the gate history in [`audit/SCORE-history.md`](audit/SCORE-history.md).
- Not a reproduction of the author's figures: see "Why this exists" above.

## Layout

```
README.md  README.zh-CN.md  CHANGELOG.md  LICENSE  requirements.txt
docs/QUICKSTART.md               install → dry run → score, portable, no local paths
docs/TROUBLESHOOTING.md          symptom / cause / fix, from real failures
docs/TASK-AUTHORING.md           how a task family is added (the tasks are hard-coded)
docs/OPERATING.md                the operating procedure for this line (kept in Chinese)
audit/README.md                  what moved into audit/, and the counting conventions
audit/STATE.md                   current state of the line (continuation point at the top, debt table in §7)
audit/HANDOFF.md                 the three pieces, measurement gates, one-line commands, known blind spots
audit/DESIGN-refusal-scoring.md  why the verdicts are split apart (requirement + scoring design)
audit/REPORT.md                  the write-up, draft v0.1 (8 chapters + 2 appendices)
audit/REPORT-draft.md            chapter skeleton and source pointers (kept on purpose)
audit/SCORE-history.md           one-page history of the measurement gates
sol/sandbox/SCORE.md       every batch result, with per-batch reading notes
sol/sandbox/               the three programs, the probes, the batch evidence JSON
```

## Where to read what

| question | document |
|---|---|
| how do I get it running | [`docs/QUICKSTART.md`](docs/QUICKSTART.md) |
| it does not work | [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) |
| how do I add my own task family | [`docs/TASK-AUTHORING.md`](docs/TASK-AUTHORING.md) |
| what were the scores, batch by batch | [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) |
| can batch A be compared with batch B | [`audit/SCORE-history.md`](audit/SCORE-history.md), then `audit/HANDOFF.md` §2 |
| how do I re-run it, and what is known to be broken | [`audit/HANDOFF.md`](audit/HANDOFF.md) §3 and §4 |
| why "refused right" is a separate count | [`audit/DESIGN-refusal-scoring.md`](audit/DESIGN-refusal-scoring.md) |
| the finished argument | [`audit/REPORT.md`](audit/REPORT.md) |
| what is being worked on right now | [`audit/STATE.md`](audit/STATE.md) |

**Deep reading**: the eight audit documents live in [`audit/`](audit/) — start with
[`audit/README.md`](audit/README.md), which explains what moved there, how references
are written now, and where each count is defined.

## Operating procedure

The day-to-day procedure for this line is in the repository, at
[`docs/OPERATING.md`](docs/OPERATING.md) (kept in Chinese, the operator's working
language). A local harness skill named `gui-audit-gym` is a pointer to that file — the
procedure itself is not duplicated anywhere outside this repository.

## License

MIT — see [`LICENSE`](LICENSE).
