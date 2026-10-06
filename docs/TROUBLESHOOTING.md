# TROUBLESHOOTING — symptom / cause / fix

Every entry below is a failure this line actually hit, in the order you are likely to
meet it. The rule that produced them: **stop, and say what to install or which variable
to set** — never silently fall back to a path that happens to work on the author's
machine.

## 1. The driver refuses to start

```
refusing to drive: 2 practice target window(s) on screen - want exactly 1     (exit 2)
```

**Cause.** The count is a *substring* match on the window title: the driver counts every
UIA window whose name contains `GUI Gym`. Any unrelated window — an editor, a chat, a
browser tab — with that string in its title is counted as a target.

**Fix.** Close or temporarily rename the offending window, then re-check the count. Note
that a refused start can leave a target window behind (the driver only kills the
launcher process), so confirm none is left before the next run.

### 1b. The driver hangs and prints nothing

**Symptom.** Started with output redirected to a file, the driver produces a **zero-byte** log and
never exits. Blaming the target or the actor wastes a lot of time — check the desktop first.

**Cause.** A **locked** Windows session. The driver's own guard reads the foreground process; when
it is `LockApp.exe` it prints

```
gym driver: session is locked (foreground process LockApp.exe) - waiting up to 3600 s
```

and **blocks** until the session is unlocked (that is deliberate: a locked desktop cannot be driven
honestly). With the output redirected, Python buffers that line, so the log stays empty and the run
merely looks hung.

**Fix.** Unlock the session (the wait ends by itself and the run continues; `lock_waits` in the run
json records that it happened), or pass **`--lock-wait 0`** to make it fail fast —
it then prints `refusing to start a run while the session is locked` and exits. Add
**`PYTHONUNBUFFERED=1`** (or run `python -u`) so the reason is visible in redirected logs. **Do not**
kill the driver by hand; a driver that never started writes no run json at all.

### 1c. `t_trap*` scenarios start but produce 0 tasks, or a `scripts_sha` looks wrong

**Cause.** `sol/sandbox/plans.v1.json` — the task-order manifest stage 3.6 moved the five plan
tables into — is missing, truncated or malformed. The app then has no plan to build tasks from, so
`t_trap*` scenarios come up with nothing to do. The same file is part of `scripts_sha`, and `_sha()`
hashes a **missing** file as `b"?"`: a value can therefore change silently instead of failing loudly.

**Fix.** Validate the manifest on its own:

```bash
python -c "import json; json.load(open('sol/sandbox/plans.v1.json'))"
```

It prints nothing and exits 0 when the file parses; a traceback is the answer. Then confirm the file
is still tracked — `.gitignore` must keep the `!sol/sandbox/plans.v1.json` line, otherwise
`sol/sandbox/*.json` silently drops it and the hash no longer covers the task order.

**Not the same symptom as §1b.** §1b is the driver *hanging* (locked desktop, zero-byte log). This
one is the app coming up with an empty plan, or a `scripts_sha` that does not match its recorded
value. The two have different causes and different first commands; do not merge them.

## 2. `shot failed`, or no run json at all

**Cause.** The run was started without an interactive desktop session — from a service,
a scheduled job, or a background job on the Linux side. The target's window comes up
off-screen, so every frame is empty and the driver exits rather than scoring a blank
screen.

**Fix.** Start the run from the Windows side, in a normal window (in PowerShell,
`-WindowStyle Normal`). A dry run with `--tasks 2` is the cheap way to check.

## 3. Tesseract

```
tesseract not found at C:\Program Files\Tesseract-OCR\tesseract.exe
  set TESS=<full path to tesseract(.exe)> - e.g. TESS=...
  or install it at that default path
```

**Cause.** Neither `TESS`/`TESSERACT` nor the default install location exists.

**Fix.** Install Tesseract, or set `TESS` to the binary. This is a deliberate stop, not
a crash: the reader refuses to guess (see [`QUICKSTART.md`](QUICKSTART.md) §2).

## 4. The actor

```
ACTOR_HOME=C:\somewhere has no port.txt
  - falling back to port 8731; set ACTOR_HOME=<the actor's state dir>
```

**Cause.** The driver could not find the actor's state directory, so it does not know
which port the actor is on.

**Fix.** Start the actor, or set `ACTOR_HOME` to its state directory. The fallback is
announced on stderr on purpose — a run that used it is still a run, but you should know
which port it went to.

## 5. "It worked yesterday, today it does not"

**Cause.** The target and the driver are separate processes and the driver starts a
fresh target for every run; a leftover target window from an interrupted run, a locked
screen, or another program holding the foreground all change what the driver sees.

**Fix.** Check, in this order: one target window and no leftovers → session unlocked →
nothing else stealing the foreground (the driver records the foreground window before
and after a run; a run whose foreground was taken is not a usable measurement).

## 6. Two batches that look identical disagree

**Cause.** A batch number is only comparable inside the same **gate** (the scoring
algorithm version, the `gates` key in the run json) **and** the same `scripts_sha` (a
hash of the three programs). `scripts_sha` changing means the *driver* changed, which is
a different statement from "the measurement changed".

**Fix.** Read [`../sol/sandbox/SCORE.md`](../sol/sandbox/SCORE.md) (per-batch notes) and
[`../audit/SCORE-history.md`](../audit/SCORE-history.md) (one page of gate history), then
[`../audit/HANDOFF.md`](../audit/HANDOFF.md) §2. Do not mix channels: a keyboard run and
a mouse run are different measurements of the same task.

## 7. Re-scoring an older run prints `MISMATCH`

**Cause.** The run json records the *path* of the target's events file, and the target
overwrites that file on its next launch. Re-scoring an older json therefore joins
against somebody else's truth.

**Fix.** Score immediately after a run, or re-score with the archived copy:
`score.py <run.json> --events <that batch's archived events file>`. The earliest batches
have no archived copy and cannot be re-checked after the fact — their published numbers
stand as published.

## 8. The run stopped early, exit code 3

**Cause.** This is not a crash: the driver saves what it had instead of dying (for
example after repeated empty frames). Such a json carries `partial: true`,
`exit_reason` and `tasks_planned`.

**Fix.** Treat it as evidence about the failure path, **not** as a score. A partial run
is never comparable with a complete batch.
