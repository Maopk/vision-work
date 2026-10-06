# QUICKSTART — from zero to a scored run

This is the portable version of the quick start: it names no machine-local path, and it
says what to set when something is missing. If a step cannot work out, see
[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) — every entry there is a symptom we have
actually hit, with its cause and its fix.

The scores themselves live in [`../sol/sandbox/SCORE.md`](../sol/sandbox/SCORE.md);
this document states none of them.

## 1. What you need

| piece | what it must be |
|---|---|
| Windows with an **interactive desktop session** | the target is a Tk window and the driver reads real pixels. A run started from a service, a scheduled job, or a WSL-side background job comes up off-screen and every frame is empty |
| Python **3.12** | the recorded batches ran on CPython 3.12.14 |
| `numpy` + `Pillow` | pinned in [`../requirements.txt`](../requirements.txt) — `pip install -r requirements.txt`. `numpy` is the image maths behind the reader, `Pillow` is every screenshot, crop and diff |
| the **PC actor** | a separate project (`dsh-vision-kit/actor` in the author's setup): a resident process that screenshots the screen and sends clicks/keys on request. The three programs here talk to it over a plain socket; it is not part of this repository |
| **Tesseract** OCR | the reader shells out to `tesseract` to read the task off the screen. Install it, or point `TESS` at the binary |
| exactly **one target window** | the driver refuses to start when it counts more than one. See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) |

## 2. Environment variables

Both are read at start-up. Neither is required if you installed things in the usual
places — and neither fails silently if you did not.

| variable | what it does | when it is missing |
|---|---|---|
| `TESS` (alias `TESSERACT`) | full path to `tesseract` / `tesseract.exe` | `../sol/sandbox/gui_see.py` falls back to the standard install location (`%ProgramFiles%\Tesseract-OCR\tesseract.exe`). If that does not exist either, the process **stops and prints what to install and which variable to set** — it never guesses somebody else's path |
| `ACTOR_HOME` | the actor's state directory (the driver reads `port.txt` from it) | the driver prints a warning to stderr naming both the variable and the default it fell back to, and uses the default port `8731` |

The actor itself needs no variable here: start it the way its own README says, then
check that it answers.

```powershell
# the actor's client - path is wherever you installed the actor
python <actor>\act.py ping      # {"ok":true, ... "geom":..., "dpi":...}
```

## 3. The minimal run

Two tasks, to prove the whole channel is live before you spend ten minutes on a batch.
Run it from a normal Windows shell, in `sol/sandbox`:

```powershell
cd <this repo>\sol\sandbox
$PY = 'python'   # the 3.12 interpreter with numpy + Pillow from step 1

& $PY gym_run.py --scenario t_trap5 --tasks 2 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out dry.json
& $PY score.py dry.json
& $PY score.py --selftest
```

What a good run looks like:

- the driver starts the target itself, reads each task off the screen and presses;
- it ends with **exit code 0** and every task ok — no `wrong`, no `timeout`;
- three files land next to the scripts: `dry.json` (the run), `dry-state.json` and
  `dry-events.jsonl` (the target's own record — keep all three together);
- `score.py` prints the verdict counts for the run, and `score.py --selftest` reports
  zero failures.

If it does not look like that, stop here and read
[`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

**Score immediately.** The run json records the *path* of the target's events file, and
the target overwrites that file on its next launch — so a batch scored later can join
against the wrong events. The full command set (48-task mouse line, keyboard + chaos
line) is in [`../audit/HANDOFF.md`](../audit/HANDOFF.md) §3.

## 4. Where the rest is written down

| you want | read |
|---|---|
| the one-line commands, the gates, the known blind spots | [`../audit/HANDOFF.md`](../audit/HANDOFF.md) |
| how a run is scored, and what a "refusal" counts as | [`../audit/DESIGN-refusal-scoring.md`](../audit/DESIGN-refusal-scoring.md) |
| how to add your own task family | [`TASK-AUTHORING.md`](TASK-AUTHORING.md) |
| the operating procedure for this line | [`OPERATING.md`](OPERATING.md) (kept in Chinese) |
