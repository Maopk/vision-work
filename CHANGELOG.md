# Changelog

All notable changes to this repository are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Initial repository: the GUI behaviour-audit line — target (`sol/sandbox/gym_app.py`), fully blind driver (`sol/sandbox/gym_run.py`) and scorer (`sol/sandbox/score.py`) — together with the measurement documents (`sol/sandbox/SCORE.md`, `STATE.md`, `HANDOFF.md`, `DESIGN-refusal-scoring.md`, `SCORE-history.md`) and the report draft (`REPORT.md`, `REPORT-draft.md`), as of batches 1–11 (measurement gates v0–v3).
- Batch evidence JSON (`sol/sandbox/t_trap*.json`) and batch-time probes (`sol/sandbox/probe_*.py`).
- `README.md`, `README.zh-CN.md`, `CHANGELOG.md`, `LICENSE`, `.gitignore`.
- Batch 12 evidence (`sol/sandbox/t_trap2-w12-popup35.json`) — the `popup` interference class is measurable again (60/60, 24/24 dialogs dismissed); see `sol/sandbox/SCORE.md` batch 12 and `STATE.md` §18.
- Batch 13 evidence (`sol/sandbox/t_trap2-w13-popup70.json`) — the `popup` class also holds at a **second strength level** on the keyboard + background channel (60/60, every dialog dismissed, no early stop); see `sol/sandbox/SCORE.md` batch 13 and `STATE.md` §19.
- Report **v0.3** (`REPORT.md`, `REPORT-draft.md`) — the batch-8 statement "the `popup` class cannot be measured" is corrected to "**measurable on the keyboard channel (two strength levels), still not measurable on the mouse channel**", with that boundary written into §5.2 ④, §5.3, §6.2 D, §7.2, §7.3 and chapter 8, plus a new appendix B-3 record of this pass.
- Batch 14 attempt record (`sol/sandbox/t_trap2-w13-popup35-mouse-fix.json`, kept as **non-scoring evidence**: the driver version it ran against was reverted, so it is not reproducible) — debt #20's option D was implemented, dismissed 10 of 11 dialogs, then early-stopped at task 21; see `sol/sandbox/SCORE.md` batch 14 and `STATE.md` §21.
- Batch 15 diagnostic record (`SCORE.md` batch 15, **no evidence JSON in the repository**: the change was reverted before any batch ran) — debt #20's second attempt (fall back to `self.key("Return")` after a missed click) failed its own dry run: 2 tasks, both `NONE`, exit 1, `popup_seen 13` with `popup_dismissed` / `popup_key_dismissed` **absent from `stats`** (= 13 dialogs found, 0 dismissed, 45 Return presses all missed); see `STATE.md` §23.

### Changed
- `REPORT.md` version line, scope line and the line-number index are re-aligned to the current file lengths (report v0.3; see appendix A's line-number note).
- Debt #20 stays **open** after the thirteenth segment: the two-door fix was measured (10/11 dialogs dismissed, early stop at task 21) and **reverted** by the segment's own termination rule; `gym_run.py` is back to `87470aaff559…` and the patch is archived at `D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`.
- Debt #20 also stays **open** after the fourteenth segment: the key-fallback attempt (`gym_run.py` intermediate `178591e19c40c37f`) was reverted the same way, and the mechanism is now explained — a real `SendInput` key only reaches the **foreground** window (which this machine keeps stealing back), while a mouse click is delivered **by coordinates** and therefore does reach a `-topmost` dialog. So the remaining fix is not another coordinate/key variant but a channel decision (foreground batch / managed input channel / accept the boundary); patch archived at `D:\DSH\dsh-actor\tmp\w16-popup-key-fallback.patch`.

### Fixed
- The keyboard + background driver channel could not dismiss the `attention` dialog (debt #16): `window_by_title()` and `target_windows()` read the folded `data` window list, which the actor's `_slim` truncates to its first few entries, so the dialog was never found and **no key was ever sent**. Both now read the inline reply, dismissal is counted (`popup_seen` / `popup_dismissed` / `popup_dismiss_failed`), and a cleared dialog short-circuits the wait so the task is re-answered instead of stalling.
