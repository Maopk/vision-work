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

### Changed
- `REPORT.md` version line, scope line and the line-number index are re-aligned to the current file lengths (report v0.3; see appendix A's line-number note).

### Fixed
- The keyboard + background driver channel could not dismiss the `attention` dialog (debt #16): `window_by_title()` and `target_windows()` read the folded `data` window list, which the actor's `_slim` truncates to its first few entries, so the dialog was never found and **no key was ever sent**. Both now read the inline reply, dismissal is counted (`popup_seen` / `popup_dismissed` / `popup_dismiss_failed`), and a cleared dialog short-circuits the wait so the task is re-answered instead of stalling.
