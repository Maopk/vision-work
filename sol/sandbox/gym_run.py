"""A blind driver for the GUI gym: sees only pixels, acts only with mouse/key.

The app under test never tells the driver what to do - the driver reads the
instruction off the screen (the DO: banner), finds the widgets in the OCR text
map, acts, and then verifies by reading the result line back.  The app's state
file is used only for scoring, by the harness.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gui_see as G                                    # noqa: E402
from loop import Actor                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

BANNER_BAND = 150          # px: nothing but the instruction/status chrome lives here
BG_RGB = (244, 246, 248)   # the gym's window background ("#f4f6f8") - ink() compares to it

# --- mouse-channel visibility (batch 3, class `no_badge_fill`) ----------------
# A control with no "[k]" badge cannot be reached through the key channel, so in mouse
# mode the driver has to decide from pixels whether the thing is on screen at all.
# The statistic below is *pre-registered* in probe_fill_curve.py; that file is the
# contract and this code must reproduce it exactly (its header says why D1 was chosen
# before any measurement and that the rule may not be re-picked after seeing the curve).
# Measured on real app frames (fill_curve.json, 21 alphas x 3 frames, seed 20251007):
#   * D1 is linear in alpha: D1 ~= 137 * alpha (0.20 -> 28, 0.44 -> 62, 0.50 -> 71,
#     1.00 -> 137), i.e. the app's operability constant 0.45 sits at D1 ~= 62.
#   * the declared selection rule gives T_VIS = round(0.5 * D1(1.00)) = round(0.5*137)
#     = 68, which lands the driver's floor at alpha ~= 0.50 - *above* the app's 0.45.
#   * the OCR locate step has a non-monotonic hole: the label was read at 0.55 and at
#     0.75 but at none of 0.60/0.65/0.70 (0/9 frames) - the chain fails in the middle
#     band, not at the faint end (0.10 already reads).
# D2 (the 2 px border test of the same rule) measured 0.0 at every alpha and is
# therefore reported as a dead diagnostic, not used.
VIS_PAD_X, VIS_PAD_Y = 10, 6       # padding around the label's OCR box
VIS_RING_X, VIS_RING_Y = 34, 22    # outer ring the background level is taken from
T_VIS_FILL = 68                    # D1 floor; frozen from the curve, not tuned on tasks

# OCR reads the 13 px slot labels badly and swaps look-alike glyphs ("M4O" ->
# "M40", "SLOT" -> "LOT"), so every comparison goes through this fold of
# shape-alike characters instead of comparing raw text.  A slot code is always
# 3 characters, a chip number 1-2 digits, so folding digits and letters
# together cannot make the two collide.
_CONFUSE = str.maketrans({"O": "0", "Q": "0", "I": "1", "L": "1", "S": "5",
                          "B": "8", "Z": "2", "G": "6", "T": "7", "A": "4"})
_SLOT_C = ("5107", "107")  # "SLOT" folded - with and without a lost leading S


def _code(s):
    """Upper-case alphanumeric form of a word with confusable glyphs folded."""
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper()).translate(_CONFUSE)


def _plain(s):
    """Upper-case alphanumeric form of a word, *without* folding confusable glyphs.

    Change detection needs this instead of `_code`: `_CONFUSE` folds Q->0 and O->0,
    so `TANGO` and `TANGQ` share a code and a folded comparison cannot tell them
    apart - measured on the `swap_hard_timer` family, where the guard re-read the
    banner correctly as `TANGQ` and still reported "unchanged" because of the fold.
    """
    return re.sub(r"[^A-Z0-9]", "", (s or "").upper())


def _hint1(text: str) -> str | None:
    """The hint character in a read-out - the app hands out single characters."""
    for ch in (text or ""):
        if ch in HINT_KEYS:
            return ch
    return None


def _norm_text(s: str) -> str:
    """Letters and digits only, case folded - the shape both sides of a text
    comparison have to share (the confusing-glyph folding of `_code` is for codes)."""
    return re.sub(r"[^0-9a-z]", "", (s or "").casefold())


def _same_text(read: str, want: str) -> bool:
    """Whether a re-read off the screen plausibly *is* the text that was typed.

    Equality first, then a single dropped glyph at one *end* (OCR losing the first or
    last character of a short field). Deliberately not a loose ratio any more: measured
    "iGamma" for a typed "Gamma" scored 0.83 and slipped through, and the app compares
    the field exactly - so a stray character has to trigger the retype, not the benefit
    of the doubt.
    """
    a, b = _norm_text(read), _norm_text(want)
    if not a:
        return False
    if a == b:
        return True
    # A one-glyph difference is ambiguous - OCR losing a character looks exactly like the
    # field really holding one less (measured: a cleared-and-retyped "MLWI" landed as
    # "LWI", and "Gamma" landed as "iGamma"). The app compares the field exactly, so the
    # driver clears and retypes instead of guessing; that costs one round trip and its own
    # read-back is recorded either way.
    return False


def _slot_split(c):
    """("slot", rest) when a folded token looks like a slot label, else (None, c).

    Handles the label alone ("SLOT"), with a lost leading S ("LOT") and merged
    with its code ("SLOTM40" -> rest "M40").
    """
    for p in _SLOT_C:
        if c == p:
            return "slot", ""
        if c.startswith(p):
            return "slot", c[len(p):]
    return None, c


# ------------------------------------------------------------------- glyphs ---
# Shape families that OCR cannot settle from context, and that this app really mixes:
# every code is drawn from A-Z plus digits (gym_app.py:43), so `0` and `O`, `1` and
# `I`/`l`, `5` and `S`, `2` and `Z`, `8` and `B`, `6` and `G` all occur.  A target
# that compares strings exactly turns the wrong pick into a wrong answer, and the
# word-level pass does pick wrong: measured on the practice banner, the code the app
# meant as `C02S` (zero) was read as `CO2S` (letter O) - while tesseract's per-glyph
# pass read the digit.  So the driver reads such a token glyph by glyph and decides
# each ambiguous character by measuring it against the same characters rendered in
# the banner's own font (Segoe UI bold, gym_app.py:120) - a zero is much narrower
# than an O, a one than an I - instead of guessing from the word.
GLYPH_FAMILY = {"0": "0O", "O": "0O",
                "1": "1Il", "I": "1Il", "l": "1Il",
                "5": "5S", "S": "5S",
                "2": "2Z", "Z": "2Z",
                "8": "8B", "B": "8B",
                "6": "6G", "G": "6G"}
CODEISH = re.compile(r"^[A-Z0-9]{3,8}$")          # the shape of a generated code
PROTO_FONT = "C:/Windows/Fonts/segoeuib.ttf"      # the banner font, bold -26
PROTO_ASPECT: dict = {}                           # char -> ink width / ink height


def _fold_family(s: str) -> str:
    """Canonical family form: `0` and `O` both become `0`, everything else is kept."""
    return "".join(GLYPH_FAMILY[c][0] if c in GLYPH_FAMILY else c for c in s or "")


def _proto_aspect(ch: str, size: int = 64) -> float:
    """Ink aspect (w/h) of one character rendered in the banner's font."""
    if ch not in PROTO_ASPECT:
        f = ImageFont.truetype(PROTO_FONT, size)
        im = Image.new("L", (size * 2, size * 2), 255)
        ImageDraw.Draw(im).text((size // 2, size // 2), ch, font=f, fill=0)
        ink = np.asarray(im, dtype=np.uint8) < 128
        ys, xs = np.nonzero(ink)
        PROTO_ASPECT[ch] = (float(xs.max() - xs.min() + 1) / max(1, ys.max() - ys.min() + 1)
                            if len(xs) else 0.0)
    return PROTO_ASPECT[ch]


def _ask_key(s: str) -> str:
    """Ask text with OCR punctuation noise stripped - "did the text under me change?"."""
    return re.sub(r"[^A-Za-z0-9]+", "", (s or "").upper())


def _form_pairs(text: str) -> list[list[str]]:
    """The `Label = value` pairs of a form ask, whatever OCR did to the words around them.

    Anchoring on the sentence ("fill ... then press GO") made one dropped letter fatal:
    the banner read "ill Contact = 65XF and Reaion = OXKC" and the whole task was thrown
    away as unparseable. The pair itself is the only part that has to be right, and the
    label is the single word before "=" - finding it on screen is the driver's job.

    Measured (mixed run, task 45): OCR reported all four "=" glyphs *after* the last
    field - "fill Account 770 and Tier Quartz and Region 196 and Owner Gamma then = = =
    = press GO" - so the strict pass found no pair at all and the task degraded to
    act=unknown. The loose pass drops every "=" and takes the two tokens of each
    `and`-separated segment, but only when that shape is unambiguous for *all* segments.
    """
    body = re.split(r"\bthen\b|\bpress\b|\bGO\b", text or "", flags=re.I)[0]
    head = re.sub(r"^.*?\bfill\b", "", body, flags=re.I | re.S)
    body = head or body
    segs = [s for s in re.split(r"\s+and\s+|\s*,\s*", body) if s.strip()]
    strict: list[list[str] | None] = []
    for part in segs:
        m = re.search(r"([A-Za-z][A-Za-z0-9]*)\s*=\s*([A-Za-z0-9]+)", part)
        strict.append([m.group(1), m.group(2)] if m else None)
    if segs and all(strict):
        return [p for p in strict if p]
    loose: list[list[str]] = []
    for part in segs:
        toks = [t for t in re.split(r"\s+", part.strip()) if t and t != "="]
        if (len(toks) == 2 and re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", toks[0])
                and re.fullmatch(r"[A-Za-z0-9]+", toks[1])):
            loose.append(toks)
        else:
            return []
    return loose


# the gym prints "[k]" next to every control it accepts a key for; n/q/k stay with the app
HINT_RE = re.compile(r"^[\[\(<]?\s*([0-9A-Za-z])\s*[\]\)>]$")
HINT_KEYS = "123456789"          # the app hands hints out in this order
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
# gym_app.HINT_KEYS, i.e. the same alphabet *including* the letters: the tenth
# control gets "a", and t_chips hands out more than nine keys often enough that a
# scan limited to 1..9 simply never reaches the disc it wants (measured: the three
# unfinished tasks of a 12-task run all had a chip on a key past "9")
SCAN_KEYS = HINT_KEYS + "abcdefghijlmoprstuvwxyz"
# The observable act for "there is no legal control here".  Without it a refusal is
# indistinguishable from a timeout, and "did not press the wrong thing" cannot be
# scored as a win.  F8 collides with nothing: the app's action keys are the hint
# keys above plus Esc (which only closes menus).
REFUSE_KEY = "F8"
# Intents the trap family phrases an ask as.  A near-synonym is general knowledge,
# not the answer: the controls carry random labels, so nothing here is memorised.
SYNONYM_ACT = {
    "dismiss": ("close", "ok", "dismiss", "hide", "cancel", "got it"),
    "close": ("close", "dismiss", "ok", "cancel"),
    # "acknowledge the alert" is the third way a notice is phrased, and its canonical
    # control is OK - the target picks Close or OK at random, so the driver still has to
    # read which one is on screen.  Without this key the ask parsed as *nothing* and the
    # driver froze instead of deciding (measured: `act=unknown`, 3 empty attempts, and
    # the run's early-stop guard fired on it).
    "acknowledge": ("ok", "close", "acknowledge", "got it", "dismiss"),
    "confirm": ("ok", "confirm", "yes", "apply", "save"),
    "cancel": ("cancel", "close", "no", "dismiss"),
    "submit": ("submit", "send", "ok", "apply", "save"),
    "open": ("open", "show", "details", "view"),
    "skip": ("skip", "next", "later"),
    "retry": ("retry", "try again", "reload"),
}


def _hint_before(items: list[dict], i: int, back: int = 3) -> str | None:
    """The "[k]" hint sitting just left of a control's label.

    The label is a single canvas text item ("[1] SLOT 8B1"), so OCR hands it back
    as separate tokens - and sometimes glued ("[1]SLOT"), which is why this reads
    the joined text instead of matching token by token.
    """
    joined = " ".join(w_["text"] for w_ in items[max(0, i - back):i])
    m = re.search(r"[\[\(]\s*([0-9A-Za-z])\s*[\]\)]", joined)
    return m.group(1) if m else None


def _tokens(s: str) -> list[str]:
    """Word-ish pieces of a read line, used to compare two OCR passes of one banner."""
    return [t for t in re.split(r"[^A-Za-z0-9]+", s or "") if t]


def _redo(d: Driver, rec: dict, fresh: str, why: str) -> dict:
    """Run the task again from a fresh look at the screen, keeping the replan trail."""
    again = d.do_task(d.state().get("ask"))
    again["replanned"] = rec.get("replanned", 0) + 1
    # carry the per-task replan count onto the new record: `_redo` replaces `rec`, so a
    # count incremented by the caller before this call lands on the discarded one
    # (measured: a swap run reported "replan 0" after three replans actually happened)
    again["replans"] = int(rec.get("replans") or 0) + 1
    # same reason: the counters that explain *why* we replanned belong on the surviving
    # record, otherwise the per-task trail reads "asked moved: 0" for a task that was
    # replanned precisely because the ask moved (run-level stats had it right)
    for k in ("ask_moved",):
        if rec.get(k):
            again[k] = int(again.get(k) or 0) + int(rec[k])
    for k in ("ask_cells", "ask_delta"):
        # the evidence behind ask_moved, kept as the largest change seen in this task:
        # `setdefault` was wrong here - the re-planned pass runs its own verification and
        # leaves a fresh 0 on the new record, which would hide the change that caused it
        if rec.get(k):
            again[k] = max(float(again.get(k) or 0), float(rec[k]))
    # Batch 9 (#10/#11): the measurement counters are per-task bookkeeping too, and they
    # were exactly the two things a batch could not audit per task - batch 6 fired the
    # press jitter 5 times (3560 ms in `stats`) but only 2993 ms survived on 3 rows, and 33
    # of the 75 `gate_ms` samples never reached a row.  Every loss traced back to this
    # function replacing the record.  Carrying them changes no decision, only the ledger.
    if rec.get("press_delay_ms"):
        again["press_delay_ms"] = int(again.get("press_delay_ms") or 0) + int(rec["press_delay_ms"])
        again["press_jitter_task"] = 1
    if rec.get("gate_ms"):
        again["gate_ms"] = list(rec["gate_ms"]) + list(again.get("gate_ms") or [])
    # Batch 10 (debt #4): same lesson as the two counters above - `_redo` replaces the
    # record, so a box-recompute that happened before a replan would otherwise vanish
    # from the ledger and make the new counter under-count exactly where the guard is
    # most active.
    if rec.get("ask_box_recomputed"):
        again["ask_box_recomputed"] = int(again.get("ask_box_recomputed") or 0) \
            + int(rec["ask_box_recomputed"])
    if rec.get("ask_box_shift_px") and not again.get("ask_box_shift_px"):
        again["ask_box_shift_px"] = list(rec["ask_box_shift_px"])
    again["ask_before_replan"] = rec.get("ask")
    again["ask_replan_read"] = fresh
    again["replan_why"] = why
    if rec.get("interferences"):
        again["interferences"] = rec["interferences"]
    return again


def foreground_via(actor: Actor) -> dict:
    """Ask the actor which window is in front - the user's, before the gym pops up."""
    try:
        rep = actor.run([{"op": "window", "mode": "foreground"}], results=True)
    except Exception:                                   # noqa: BLE001 - best effort
        return {}
    for step in rep.get("trace", []):
        data = step.get("data") or {}
        if isinstance(data, dict) and data.get("foreground"):
            return {"hwnd": int(data["foreground"]), "title": data.get("title") or ""}
    return {}


class ShotFailed(RuntimeError):
    """The capture path lost the target: the actor handed back an empty frame.

    Batch 11 (debt #17).  Until then an empty frame ended the run through SystemExit,
    and because the summary and the run json are straight-line code *after* the task
    loop in main(), that threw away every finished row: on 2026-10-05 a batch died at
    task 47 with 46 rows already done and left no run json at all.  A capture path that
    keeps coming back empty now unwinds to main() as this exception, which saves what
    it has as a *partial* run json (`"partial": true` plus `"exit_reason"`).
    """


class Driver:
    def __init__(self, actor: Actor, state_path: str, title: str = "GUI Gym",
                 verbose: bool = True, expect_chaos: bool = False, bg: bool = False,
                 keys: bool = False, jitter: tuple = (0, 0)):
        self.a = actor
        self.state_path = state_path
        self.title = title
        self.verbose = verbose
        self.expect_chaos = expect_chaos
        # background mode: capture the window itself (PrintWindow, works while it is
        # covered or behind) and send input with PostMessage, so the user's foreground
        # is never touched.
        self.bg = bool(bg)
        # keys mode: act through the app's keyboard channel (posted keys) instead of
        # posting mouse messages - Tk ignores posted mouse input entirely
        self.keys = bool(keys)
        # batch 6: `--press-jitter LO,HI`.  A deliberate pause between the guard's frame
        # and the click, applied to the `swap_race_timer` variant only (see
        # `press_jitter`): the race the guard cannot shrink is the one that lands
        # *after* its own frame.
        self.jitter = (int(jitter[0]), int(jitter[1]))
        # chaos runs re-label and re-lay-out the body mid-task, so a control is looked
        # at once more right before it is pressed (see press_hint)
        self.verify_targets = bool(expect_chaos)
        self.hwnd: int | None = None
        self.origin = [0, 0]
        self.size = [1000, 700]
        self.stats: dict = {"shots": 0, "ocr": 0, "clicks": 0, "keys": 0, "drags": 0,
                            "scrolls": 0, "asks_from_screen": 0, "asks_from_file": 0,
                            "interferences": 0, "replans": 0, "banner_missing": 0,
                            "no_hint": 0, "focus": 0, "key_errors": 0,
                            "ms_shot": 0.0, "ms_ocr": 0.0, "ms_blocks": 0.0,
                            "ms_key": 0.0, "ms_window": 0.0,
                            # batch 11 (debt #17): empty frames, their retries and the
                            # window-restore attempts now always show up in the run json
                            "shot_empty": 0, "shot_retry": 0, "restores": 0}

    # ------------------------------------------------------------- helpers --
    def log(self, *parts) -> None:
        if self.verbose:
            print(*parts, flush=True)

    def _timed(self, key: str, fn, *args, **kwargs):
        """Run one expensive step and charge its wall time to `key`.

        Profiling only.  A practice task costs ~1.3 s and which part of it is
        capture, OCR and block detection had never been measured.
        """
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            ms = (time.perf_counter() - t0) * 1000
            self.stats[key] = round(self.stats.get(key, 0.0) + ms, 1)

    def act_step(self, step: dict) -> dict:
        """One input step, routed through PostMessage when running in background mode."""
        if not self.bg:
            return step
        if self.hwnd is None:
            self.window_rect()          # resolves self.hwnd as a side effect
        step = dict(step)
        step.pop("front_title", None)
        step["bg"] = True
        step["hwnd"] = self.hwnd
        return step

    def window_rect(self) -> tuple[int, int, int, int]:
        """[x1, y1, x2, y2] straight from the actor - no app cooperation needed."""
        rep = self._timed("ms_window", self.a.run,
                          [{"op": "window", "mode": "info", "title_contains": self.title}],
                          results=True)
        for step in rep.get("trace", []):
            data = step.get("data") or {}
            rect = data.get("rect") if isinstance(data, dict) else None
            if rect and len(rect) == 4:
                # prefer the client area: the frame (and a dark active caption) would
                # otherwise sit right above the app's own banner in every capture
                cl = data.get("client") if isinstance(data, dict) else None
                if cl and len(cl) == 4 and int(cl[2]) > int(cl[0]) and int(cl[3]) > int(cl[1]):
                    rect = cl
                self.origin = [int(rect[0]), int(rect[1])]
                self.size = [int(rect[2]) - int(rect[0]), int(rect[3]) - int(rect[1])]
                if isinstance(data, dict) and data.get("hwnd"):
                    self.hwnd = int(data["hwnd"])
                break
        else:
            # batch 11 (debt #17): the target can disappear mid-run (it did on
            # 2026-10-05); that must save the finished tasks, not kill the process
            raise ShotFailed("window %r not found - is the app running?" % self.title)
        if self.bg and self.hwnd is None:
            self.hwnd = self._find_hwnd()
        return (self.origin[0], self.origin[1],
                self.origin[0] + self.size[0], self.origin[1] + self.size[1])

    def foreground(self) -> dict:
        """Which window is in front right now - the check that we stole nothing."""
        rep = self.a.run([{"op": "window", "mode": "foreground"}], results=True)
        for step in rep.get("trace", []):
            data = step.get("data") or {}
            if isinstance(data, dict) and data.get("foreground"):
                return {"hwnd": int(data["foreground"]), "title": data.get("title") or ""}
        return {}

    def focus_window(self) -> dict:
        """Let the app hold the keyboard focus without becoming the foreground window.

        Measured with probe_post_key.py: a plain posted key is dropped by Tk while the
        app is behind the user's windows, but `window mode=focus` (SetFocus from inside
        the app's own thread queue, via AttachThreadInput) makes the same key land -
        and it never raises the window or touches what the user is doing.
        """
        if not self.hwnd:
            return {}
        try:
            rep = self.a.run([{"op": "window", "mode": "focus", "hwnd": self.hwnd}],
                             results=True)
        except Exception:                               # noqa: BLE001 - best effort
            return {}
        for step in rep.get("trace", []):
            data = step.get("data") or {}
            if isinstance(data, dict) and data.get("mode") == "focus":
                self.stats["focus"] += 1
                return data
        return {}

    def _find_hwnd(self) -> int:
        """Fallback for background mode: match the window title through UIA."""
        rep = self.a.run([{"op": "uia", "what": "windows", "max": 120}], results=True)
        for step in rep.get("trace", []):
            data = step.get("data") or {}
            for w in (data.get("windows") or []):
                if self.title.lower() in (w.get("name") or "").lower():
                    return int(w["hwnd"])
        raise ShotFailed("window %r not found in UIA either" % self.title)

    def has_banner(self, img: Image.Image, band: int = 220) -> bool:
        """Cheap sanity check: does this frame actually show the app's ask banner?

        The banner is the only large dark block near the top of the window, so a
        frame without it did not capture the app (usually the harness window was
        over that screen area at that instant).
        """
        g = np.asarray(img.convert("L"), dtype=np.int16)
        rows = (g[:min(band, g.shape[0])] < 100).mean(axis=1)
        return bool((rows > 0.55).any())

    def shot(self, *args, **kwargs) -> Image.Image:
        return self._timed("ms_shot", self._shot, *args, **kwargs)

    def _shot(self, region=None, front=True, want_app=True, retries=3) -> Image.Image:
        """Screenshot the app window, retrying a frame that missed the app.

        `front` raises the window through the actor first, but a capture can still
        come back showing whatever was over that screen area at that instant. So
        frames that are supposed to show the app are checked for the app's dark
        banner and re-taken when it is missing. Never used for posted menus - those
        live outside the window and are read with shot_screen().

        Batch 11 (debt #17): an *empty* frame (the actor's `shot` failing with
        "cannot write empty image") used to end the whole run through SystemExit and
        throw the finished tasks away.  It now retries with a short pause and, if the
        target is really gone, raises `ShotFailed` so main() can save a partial json.
        """
        x1, y1, x2, y2 = region or self.window_rect()
        tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_gym_shot.png")
        img = None
        restored = False
        for attempt in range(retries + 1):
            steps = []
            if self.bg:
                if self.hwnd is None:
                    self.window_rect()
                # PrintWindow: the window paints itself, so this works even while it
                # sits behind the user's foreground window.
                steps.append({"op": "shot", "path": tmp, "hwnd": self.hwnd,
                              "region": [x1, y1, x2, y2]})
            else:
                if front:
                    # never do this while a menu is posted: raising the window dismisses it
                    steps += [{"op": "window", "mode": "front", "title_contains": self.title},
                              {"op": "sleep", "ms": 120 if attempt == 0 else 300}]
                steps.append({"op": "shot", "path": tmp, "region": [x1, y1, x2, y2]})
            rep = self.a.run(steps)
            if not rep.get("ok"):
                # a minimised window hands back an empty frame ("cannot write empty
                # image"), and that is a state the target can end up in without the
                # driver doing anything - the user is working on this machine. Put it
                # back at the bottom of the stack and take the frame again instead of
                # ending the run.
                self.stats["shot_empty"] = int(self.stats.get("shot_empty", 0)) + 1
                if not restored and self.hwnd is not None:
                    restored = True
                    self.stats["restores"] = self.stats.get("restores", 0) + 1
                    self.a.run([{"op": "window", "mode": "restore", "hwnd": self.hwnd},
                                {"op": "window", "mode": "bottom", "hwnd": self.hwnd},
                                {"op": "sleep", "ms": 250}])
                    continue
                if attempt < retries:
                    # a cached hwnd can go stale (the target maps a fresh toplevel), and
                    # a dead hwnd answers with an empty frame for ever - re-resolve it
                    # from the title and give the window a moment to paint before the
                    # next frame (batch 11, debt #17: the old chain had no pause at all
                    # here, so three frames could be gone inside ~60 ms)
                    self.stats["shot_retry"] = int(self.stats.get("shot_retry", 0)) + 1
                    self.stats["hwnd_relookup"] = self.stats.get("hwnd_relookup", 0) + 1
                    self.hwnd = None
                    self.window_rect()
                    time.sleep(0.2)
                    continue
                # Batch 11 (debt #17): this used to be SystemExit, which killed the run
                # without writing the run json - 46 finished rows were lost that way on
                # 2026-10-05.  `ShotFailed` unwinds to main(), which saves them as a
                # partial run json instead.
                raise ShotFailed("shot failed: %s" % json.dumps(rep, ensure_ascii=False)[:400])
            self.stats["shots"] += 1
            img = Image.open(tmp).convert("RGB")
            if not (front and want_app) or self.has_banner(img):
                return img
            self.stats["banner_missing"] += 1
        return img

    def shot_screen(self, region) -> tuple[Image.Image, int, int]:
        """Screenshot an explicit *screen* region - for popups that live outside
        the app window (a posted menu is its own native window)."""
        x1, y1, x2, y2 = [int(v) for v in region]
        tmp = os.path.join(HERE, "_gym_popup.png")
        rep = self.a.run([{"op": "shot", "path": tmp,
                           "region": [x1, y1, min(x2, 2559), min(y2, 1599)]}])
        if not rep.get("ok"):
            raise ShotFailed("region shot failed: %s" % json.dumps(rep, ensure_ascii=False)[:300])
        self.stats["shots"] += 1
        return Image.open(tmp).convert("RGB"), x1, y1

    def _modal_color(self, img: Image.Image, box) -> tuple[int, int, int]:
        """The dominant colour inside `box`, quantised (the local page colour)."""
        x0, y0, x1, y1 = [int(v) for v in box]
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(img.width, x1), min(img.height, y1)
        if x1 - x0 < 2 or y1 - y0 < 2:
            return (255, 255, 255)
        px = img.load()
        counts: dict = {}
        for yy in range(y0, y1, 2):
            for xx in range(x0, x1, 2):
                c = px[xx, yy]
                key = (c[0] // 8, c[1] // 8, c[2] // 8)
                counts[key] = counts.get(key, 0) + 1
        key = max(counts.items(), key=lambda kv: kv[1])[0]
        return (key[0] * 8 + 4, key[1] * 8 + 4, key[2] * 8 + 4)

    def block_evidence(self, img: Image.Image, word: dict, want: str,
                       neighbours: int = 0) -> dict:
        """Is this word *drawn as a control*, or prose that happens to carry the label?

        A word match alone cannot decide it: a dialog that says "dismiss this before
        the task can be scored" contains the very label of its DISMISS button, and the
        folded comparison scores both the same (measured - the driver clicked the
        prose).  What separates them is the block the text sits in: a pushbutton is
        painted - its rectangle is filled or bordered, so most pixels around the glyphs
        differ from the page colour - while prose sits on the page itself, where only
        the glyph strokes differ.  `fill_share` is that ratio.
        """
        x, y, w, h = [int(v) for v in word["box"]]
        pad = 5
        inner = (x - pad, y - pad, x + w + pad, y + h + pad)
        above = (x - 20, y - 2 * h - 4, x + w + 20, y - 2)
        below = (x - 20, y + h + 2, x + w + 20, y + h + 2 * h + 4)
        page = self._modal_color(img, above)
        page2 = self._modal_color(img, below)
        if sum(abs(a - b) for a, b in zip(page, page2)) > 90:
            page = page2                     # the strip above is not the page: trust below
        x0, y0, x1, y1 = inner
        px = img.load()
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(img.width, x1), min(img.height, y1)
        tot = off = 0
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                c = px[xx, yy]
                tot += 1
                if max(abs(c[0] - page[0]), abs(c[1] - page[1]), abs(c[2] - page[2])) > 12:
                    off += 1
        share = off / float(tot or 1)
        ev = {"fill_share": round(share, 3), "page": list(page), "neighbours": neighbours,
              "case": word["text"] == want}
        # Measured on the practice target's own dialog: the DISMISS button (filled
        # #dcdcdc with a relief border) leaves ~0.8 of its rectangle off-page, the prose
        # line with the same word leaves ~0.2 (glyph strokes only).
        ev["veto"] = bool(share < 0.45 and neighbours >= 2)
        return ev

    def find_blocks(self, *args, **kwargs) -> list[tuple]:
        return self._timed("ms_blocks", self._find_blocks, *args, **kwargs)

    def painted_boxes(self, img: Image.Image, rec: dict | None = None) -> list[tuple]:
        """The painted rectangles of this frame, computed at most once per frame.

        Batch 6.  `_find_blocks` measured 77.6 ms on a 1180x780 practice frame
        (`probe-w6-twin.json`), so the ranking below asks for it once even though two
        call sites want the same answer.  The frame is identified by its object id,
        which is enough because the caller holds the image for the whole decision.
        """
        key = id(img)
        if rec is not None and rec.get("_blocks_for") == key:
            return rec.get("_blocks") or []
        boxes = self.find_blocks(img)
        if rec is not None:
            rec["_blocks_for"] = key
            rec["_blocks"] = boxes
        return boxes

    @staticmethod
    def painted_hit(hits: list[dict], boxes: list[tuple]) -> dict | None:
        """The one occurrence of a word inside a painted rectangle, else None.

        Batch 6, measured (`probe-w6-twin.json`, `t_trap4` task 1 phase B): the twin
        class prints the ask's word twice - a bare heading first in reading order, the
        real button second - and the heading sits inside no painted rectangle while the
        button sits inside one (heading `542,126,96,17` in none; button `292,192,73,14`
        inside `228,168,172,60`, fill 1.0).  The heading is a live `tk.Label` bound to a
        click, so no text-level signal separates it from the button it duplicates.

        Only a *unique* painted occurrence decides; anything else returns None so the
        caller keeps its old behaviour - the block ranks candidates, it never vetoes.
        """
        if not boxes or len(hits) < 2:
            return None
        painted = []
        for h in hits:
            cx, cy = h["center"]
            for b in boxes:
                if b[0] <= cx <= b[0] + b[2] and b[1] <= cy <= b[1] + b[3]:
                    painted.append(h)
                    break
        if len(painted) == 1 and len(painted) < len(hits):
            return painted[0]
        return None

    def _find_blocks(self, img: Image.Image, cell: int = 4, solid: float = 0.8,
                     min_w: int = 40, min_h: int = 16, max_h: int = 90,
                     max_frac: float = 0.75) -> list[tuple]:
        """Rectangles that are *painted* on the page - a control, not a sentence.

        A word tells you what something is called; only the pixels tell you whether
        anyone drew a control there.  Measured on the practice target's own dialog:
        the word pass reads the sentence ("dismiss this before the task can be
        scored") and the button under it, while a *sparse* pass over a whole window
        can miss a short bold label entirely - so the driver has to look for the
        painted block first and read its label second.

        A cell counts as painted when nearly every pixel in it differs from the page
        colour; blocks are the connected runs of painted cells big enough to hold a
        label.  Returns boxes as (x, y, w, h) in image coordinates.
        """
        rgb = img.convert("RGB")
        arr = np.asarray(rgb, dtype=np.int16)
        page = np.array(self._modal_color(img, (0, 0, img.width, img.height)),
                        dtype=np.int16)
        # Measured: the practice target paints its buttons #e8eef5 on a page of BG
        # (#f4f7fb) - a difference of only 12/9/6 per channel - so a threshold of 12
        # found no buttons at all in that window while it did find the dialog's grey
        # one.  8 keeps the flat case and still ignores antialiasing noise.
        diff = np.abs(arr - page).max(axis=2) > 8
        gh, gw = diff.shape[0] // cell, diff.shape[1] // cell
        if gh < 2 or gw < 2:
            return []
        dense = diff[:gh * cell, :gw * cell].reshape(gh, cell, gw, cell).mean(axis=(1, 3))
        grid = dense >= solid
        seen = np.zeros_like(grid, dtype=bool)
        out = []
        for gy in range(gh):
            for gx in range(gw):
                if not grid[gy, gx] or seen[gy, gx]:
                    continue
                stack, cells = [(gy, gx)], []
                seen[gy, gx] = True
                while stack:
                    y, x = stack.pop()
                    cells.append((y, x))
                    for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                        if 0 <= ny < gh and 0 <= nx < gw and grid[ny, nx] \
                                and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                if len(cells) < 4:
                    continue
                ys = [c[0] for c in cells]
                xs = [c[1] for c in cells]
                x, y = min(xs) * cell, min(ys) * cell
                w, h = (max(xs) - min(xs) + 1) * cell, (max(ys) - min(ys) + 1) * cell
                if w < min_w or h < min_h or h > max_h or w > max_frac * img.width:
                    continue
                fill = float(dense[min(ys):max(ys) + 1, min(xs):max(xs) + 1].mean())
                out.append((x, y, w, h, round(fill, 3)))
        out.sort(key=lambda b: (b[1], b[0]))
        return out

    def block_label(self, img: Image.Image, box: tuple, whitelist: str | None = None,
                    scale: int = 3) -> str:
        """Read the label painted inside a block (box is x, y, w, h).

        Reading the block's whole inner rectangle is not enough: a button's block
        merges with its frame, so the crop is mostly empty fill with the text along
        one edge, and a single-line pass then returns nothing (measured: two runs of
        the same dialog, one read `DISMISS` and one came back empty).  So the text
        band is located first - the rows inside the block that actually carry ink
        against the block's own fill colour - and only that band is handed to OCR.
        """
        x, y, w, h, _fill = box
        pad = max(2, min(4, h // 8))
        ix, iy = x + pad, y + pad
        iw, ih = max(1, w - 2 * pad), max(1, h - 2 * pad)
        fill = self._modal_color(img, (ix, iy, iw, ih))
        arr = np.asarray(img.convert("RGB"), dtype=np.int16)[iy:iy + ih, ix:ix + iw]
        ink = np.abs(arr - np.array(fill, dtype=np.int16)).max(axis=2) > 40
        rows = ink.sum(axis=1)
        best, run = (0, 0), None
        i = 0
        while i < ih:
            if rows[i] >= 2:
                j = i
                while j + 1 < ih and rows[j + 1] >= 2:
                    j += 1
                if j - i + 1 > best[0]:
                    best, run = (j - i + 1, i), (i, j)
                i = j + 1
            else:
                i += 1
        if run is None:
            band = (ix, iy, iw, ih)
        else:
            y0 = max(iy, iy + run[0] - 3)
            y1 = min(iy + ih, iy + run[1] + 4)
            band = (ix, y0, iw, max(2, y1 - y0))
        txt = ""
        for psm in ("7", "6", "11"):
            txt, _ = self._timed("ms_ocr", G.read_box, img, band,
                                 whitelist=whitelist, psm=psm, scale=scale)
            if txt.strip():
                break
        txt = re.sub(r"\s+", " ", txt).strip()
        return re.sub(r"^[^0-9A-Za-z]+|[^0-9A-Za-z]+$", "", txt)

    def _button_candidates(self, img: Image.Image, want: str,
                           min_score: float = 0.75,
                           keep_vetoed: bool = False) -> list[dict]:
        """Pushbutton candidates carrying `want`, best first.

        A dialog's own sentence may contain the very word printed on its button
        ("dismiss this before the task can be scored" + a DISMISS button), and the
        same word is read twice when both polarities are tried - so duplicates are
        merged first, then candidates are ranked by shape: a button label is short,
        alone on its line, in the target's letter case, and sits below the prose.

        Shape ranking can only *add* points, so on its own it cannot rule a candidate
        out - a prose line scores high on "is the word" alone (measured: the driver
        clicked the prose).  `block_evidence` supplies the missing veto: candidates
        that are not drawn as a block are dropped, and if that leaves nothing, nothing
        is clicked at all.
        """
        words: list[dict] = []
        for inv in (False, True):
            for w in self.words(img, invert=inv):
                if any(o["text"] == w["text"]
                       and abs(o["center"][0] - w["center"][0]) < 6
                       and abs(o["center"][1] - w["center"][1]) < 6 for o in words):
                    continue                       # same word seen in the other polarity
                words.append(w)
        hits = []
        for w in words:
            sc = self.find([w], want, min_score)
            if not sc:
                continue
            same_row = [o for o in words
                        if o is not w and abs(o["center"][1] - w["center"][1]) <= 12]
            score = sc["score"] + w["center"][1] / float(max(img.height, 1)) * 0.25
            if w["text"] == want:
                score += 0.5                       # prose is lowercase, button is not
            if not same_row:
                score += 1.0                       # a button label stands alone
            ev = self.block_evidence(img, w, want, len(same_row))
            hits.append({"word": w, "score": score, "neighbours": len(same_row),
                         "evidence": ev, "veto": ev["veto"], "source": "text"})
        # Blocks first, in the sense that a painted label is a control by construction:
        # a whole-window sparse pass can miss a short bold label (measured on the
        # practice dialog, whose DISMISS button no word pass ever returned), and the
        # block gives the evidence that lets the label be trusted once it is read.
        for blk in self.find_blocks(img):
            label = self.block_label(img, blk)
            # a control that also prints its own hint key reads "[1] bravo72", and the
            # hint is part of the app's protocol, not part of the name
            label = re.sub(r"^[\[\(]\s*[0-9A-Za-z]\s*[\]\)]\s*", "", label)
            if not label:
                continue
            bw = {"text": label, "conf": 100.0, "box": (blk[0], blk[1], blk[2], blk[3]),
                  "center": (blk[0] + blk[2] // 2, blk[1] + blk[3] // 2)}
            sc = self.find([bw], want, 0.9)        # a block must carry the name itself
            if not sc:
                continue
            if any(abs(bw["center"][0] - h["word"]["center"][0]) < 12
                   and abs(bw["center"][1] - h["word"]["center"][1]) < 12 for h in hits):
                continue                           # the word pass already had this one
            ev = {"fill_share": blk[4], "page": [], "neighbours": 0,
                  "case": label == want, "block": True}
            hits.append({"word": bw, "score": sc["score"] + 0.35, "neighbours": 0,
                         "evidence": ev, "veto": False, "source": "block"})
        hits.sort(key=lambda h: -h["score"])
        if not keep_vetoed:
            clean = [h for h in hits if not h["veto"]]
            if clean:
                return clean
            if hits:
                self.stats["dialog_refused"] = self.stats.get("dialog_refused", 0) + 1
            return []
        return hits

    def window_by_title(self, title: str) -> dict | None:
        """Find one top-level window whose name contains `title` (UIA list).

        The list is read from the step's *inline* reply, not from `data`: `results=True`
        folds the reply into `data`, but the actor's `_slim` keeps only the first few
        items of a list there (actor.py `_slim`).  Measured 2026-10-05: the same reply
        carried 11 windows inline and 7 in `data`, and the dialog of debt #16 sat past
        that cut whenever the driver was running - so `window_by_title("attention")`
        answered None, the keyboard path never sent its Return, and two whole popup
        batches (batch 8) recorded `interferences 0` with the dialog still on screen.
        """
        rep = self.a.run([{"op": "uia", "what": "windows", "max": 120}], results=True)
        for step in rep.get("trace", []):
            wins = step.get("windows") or (step.get("data") or {}).get("windows") or []
            for w in wins:
                # same guard as `target_windows`: a truncated or locked desktop answers with
                # bare strings (e.g. "(1 more items)") - skip those instead of crashing
                if not isinstance(w, dict):
                    continue
                if title.lower() in (w.get("name") or "").lower():
                    return w
        return None

    def shot_window(self, title: str, region=None):
        """Capture one named top-level window by hwnd: (image, screen x, screen y).

        Needed in background mode, where a dialog is a separate window that the main
        window's own capture (PrintWindow) does not contain.
        """
        w = self.window_by_title(title)
        if not w:
            return None
        hwnd = int(w["hwnd"])
        rect = [int(v) for v in w["rect"]]
        tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_gym_win.png")
        step = {"op": "shot", "path": tmp, "hwnd": hwnd}
        if region:
            step["region"] = [int(v) for v in region]
        rep = self.a.run([step])
        if not rep.get("ok"):
            return None
        self.stats["shots"] += 1
        return Image.open(tmp).convert("RGB"), rect[0], rect[1]

    def click_hwnd(self, hwnd: int, x, y) -> None:
        """Post a click straight to one window (not the app's main window)."""
        self.a.run([self.act_step({"op": "click", "target": {"xy": [int(x), int(y)]},
                                   "bg": True, "hwnd": int(hwnd)})])
        self.stats["clicks"] += 1

    def dismiss_interference(self, img: Image.Image | None = None,
                             tries: int = 3) -> tuple[Image.Image, int]:
        """Click away a stray window that covers the app and blocks scoring.

        A real program never announces its dialogs anywhere but on the screen, so
        this has to be noticed visually - and because the word on its button may
        also appear in its own prose, candidates are ranked by shape (see
        _button_candidates), clicked one at a time, and each click is confirmed by
        looking again: if the dialog is still there, the next candidate is tried.
        """
        if self.keys:
            # the app closes its own dialog when the main window gets the key, so a
            # keyboard driver never has to find the dialog window at all
            seen = 0
            for _ in range(tries):
                if self.bg:
                    if self.window_by_title("attention") is None:
                        break
                else:
                    img2 = img if img is not None else self.shot()
                    # presence only: the veto would drop a dialog whose button is not
                    # painted as a block, and here the question is just "is it up?"
                    if not self._button_candidates(img2, "DISMISS", keep_vetoed=True):
                        break
                if seen == 0:                   # the gate opened: the dialog was found
                    self.stats["popup_seen"] = int(self.stats.get("popup_seen") or 0) + 1
                self.key("Return")
                seen += 1
                self.stats["interferences"] += 1
                time.sleep(0.35)
                if img is not None:
                    img = self.shot()
            if seen and self.bg:                # did the key actually clear it?
                key = ("popup_dismiss_failed" if self.window_by_title("attention")
                       else "popup_dismissed")
                self.stats[key] = int(self.stats.get(key) or 0) + 1
            return (img if img is not None else self.shot()), seen
        if self.bg:
            seen, tried = 0, []
            for _ in range(tries):
                cap = self.shot_window("attention")
                if cap is None:
                    break                          # no dialog up any more
                wimg, ox, oy = cap
                hwnd = int(self.window_by_title("attention")["hwnd"])
                pick = None
                for h in self._button_candidates(wimg, "DISMISS"):
                    c = h["word"]["center"]
                    if any(abs(c[0] - t[0]) < 8 and abs(c[1] - t[1]) < 8 for t in tried):
                        continue
                    pick = c
                    break
                if pick is None:
                    break
                tried.append(pick)
                self.click_hwnd(hwnd, ox + pick[0], oy + pick[1])
                seen += 1
                self.stats["interferences"] += 1
                time.sleep(0.3)
            return (img if img is not None else self.shot()), seen
        img = img if img is not None else self.shot()
        seen, tried = 0, []
        for _ in range(tries):
            pick = None
            for h in self._button_candidates(img, "DISMISS"):
                c = h["word"]["center"]
                if any(abs(c[0] - t[0]) < 8 and abs(c[1] - t[1]) < 8 for t in tried):
                    continue                       # already clicked, still there
                pick = h["word"]
                break
            if not pick:
                break
            tried.append(pick["center"])
            x, y = self.screen(pick["center"])
            self.click(x, y)
            seen += 1
            self.stats["interferences"] += 1
            time.sleep(0.3)
            img = self.shot()
            if not self._button_candidates(img, "DISMISS"):
                break                              # it is gone
        return img, seen

    def words(self, img: Image.Image, invert=False, region=None, psm="11",
              min_conf=30.0, scale=1) -> list[dict]:
        src, off = img, (0, 0)
        if region:
            x, y, w, h = region
            src, off = img.crop((x, y, x + w, y + h)), (x, y)
        if invert:
            src = ImageOps.invert(src.convert("L")).convert("RGB")
        if scale != 1:
            # 13-px UI text: at 1:1 tesseract found 1 of 3 slot labels and mangled its
            # code; at 2x it read all three (measured on the chips canvas)
            src = src.resize((src.width * scale, src.height * scale), Image.LANCZOS)
        out = self._timed("ms_ocr", G.ocr_words, src, psm=psm, min_conf=min_conf)
        self.stats["ocr"] += 1
        for w_ in out:
            bx, by, bw, bh = w_["box"]
            w_["box"] = (int(bx / scale + off[0]), int(by / scale + off[1]),
                         int(bw / scale), int(bh / scale))
            w_["center"] = (w_["box"][0] + w_["box"][2] // 2, w_["box"][1] + w_["box"][3] // 2)
        return out

    def body_words(self, img: Image.Image, body_top: int) -> list[dict]:
        """Words in the app body, merging two OCR passes.

        Measured on a real 1180x780 frame (probe_body_ocr.py, t_button seed 777):
        psm 11 at 1:1 recovered 2 of 5 labels that are plainly on screen - `[3]
        INDIGO95` and `SABLE44` were dropped outright - while psm 6 at 2x got all
        five plus all nine `[k]` hints. Recall is what matters here, duplicates are
        cheap, so both passes run and the union is returned.
        """
        h = img.height - body_top
        region = (0, body_top, img.width, h)
        seen: list[dict] = []
        for kw in ({"psm": "6", "scale": 2}, {"psm": "11"}):
            try:
                got = self.words(img, region=region, **kw)
            except Exception as e:                  # noqa: BLE001 - keep the frame
                self.log("body ocr %s failed: %s" % (kw, e))
                continue
            for w in got:
                t = G.norm(w["text"])
                if not t:
                    continue
                c = w["center"]
                dup = any(G.norm(k["text"]) == t and abs(k["center"][0] - c[0]) <= 12
                          and abs(k["center"][1] - c[1]) <= 8 for k in seen)
                if not dup:
                    seen.append(w)
        seen.sort(key=lambda w: (w["box"][1] // 10, w["box"][0]))
        return seen

    def chrome(self, img: Image.Image) -> tuple[str, int, list[dict]]:
        """(ask text, y where the app body starts, words of the top band).

        The ask sits on the dark banner, which grows when a long instruction wraps -
        so OCR that band wherever it is instead of a fixed strip (a long form ask used
        to be cut off mid-sentence, and the truncated text matched no scenario).
        """
        g = np.asarray(img.convert("L"), dtype=np.int16)
        darkfrac = (g < 100).mean(axis=1)        # share of dark pixels per row
        # the banner is uniformly dark (>=99% of the row) while the app's header strip and
        # the pale status bar only hold a few dark glyph pixels - counting them beats any
        # row-mean threshold, which drifts with how much text a row happens to carry
        top = next((i for i in range(min(len(darkfrac), 220)) if darkfrac[i] > 0.55), None)
        if top is None:
            y0, y1 = 0, BANNER_BAND
        else:
            y0 = top
            y1 = y0 + 1
            while y1 < len(darkfrac) and darkfrac[y1] > 0.30 and y1 - y0 < BANNER_BAND:
                y1 += 1
        # OCR each text line of the banner on its own: a wrapped ask puts a second line
        # under the first, and a single pass over the whole band interleaves the two
        # ink rows: a bare banner row carries only the 4 border pixels, so >6 non-dark
        # pixels means a glyph - the ascender of "f" is 5 px wide, far below darkfrac 0.985
        nd = (g >= 100).sum(axis=1)

        def ink(y: int) -> bool:
            return 0 <= y < len(nd) and nd[y] > 6

        text_rows = [y for y in range(y0, y1) if ink(y)]
        groups: list[list[int]] = []
        for y in text_rows:
            if groups and y - groups[-1][-1] <= 2:
                groups[-1].append(y)
            else:
                groups.append([y])
        band: list[dict] = []
        parts: list[str] = []
        boxes: list[tuple] = []
        for grp in groups:
            gy0, gy1 = grp[0], grp[-1]      # walk out to the full glyph extent
            while gy0 - 1 >= y0 and ink(gy0 - 1):
                gy0 -= 1
            while gy1 + 1 < y1 and ink(gy1 + 1):
                gy1 += 1
            gy0, gy1 = max(0, gy0 - 2), min(img.height, gy1 + 3)
            # keep 14 px off the left edge: the window border carries a glyph-shaped
            # artifact down there that OCRs as a stray "3" in front of the wrapped line
            ws = self.words(img, invert=True,
                            region=(14, gy0, img.width - 28, gy1 - gy0))
            if not ws:
                continue
            ws.sort(key=lambda w_: w_["box"][0])
            band += ws
            txt = re.sub(r"^\s*[Dd][O0]\s*[:;.]?\s*", "",
                         " ".join(w_["text"] for w_ in ws)).strip()
            if not txt:
                continue
            parts.append(txt)
            boxes.append((min(w_["box"][0] for w_ in ws), min(w_["box"][1] for w_ in ws),
                          max(w_["box"][0] + w_["box"][2] for w_ in ws) -
                          min(w_["box"][0] for w_ in ws),
                          max(w_["box"][1] + w_["box"][3] for w_ in ws) -
                          min(w_["box"][1] for w_ in ws)))
        ask = " ".join(parts)
        # A tight per-line crop can lose a whole word (the digits of "GAMMA70" dip
        # below the row box and tesseract drops them), which silently truncates the
        # instruction.  Read the band once more as a single image and keep whichever
        # read carries more words - the band pass costs ~80 ms and only runs when the
        # banner was actually located.
        if groups:
            bw = self.words(img, invert=True, region=(14, y0, img.width - 28, y1 - y0))
            bw.sort(key=lambda w_: (w_["box"][1] // 8, w_["box"][0]))
            btxt = re.sub(r"^\s*[Dd][O0]\s*[:;.]?\s*", "",
                          " ".join(w_["text"] for w_ in bw)).strip()
            if len(_tokens(btxt)) > len(_tokens(ask)):
                ask = btxt
        ask_box = None
        if boxes:
            ax0 = min(b[0] for b in boxes)
            ay0 = min(b[1] for b in boxes)
            ax1 = max(b[0] + b[2] for b in boxes)
            ay1 = max(b[1] + b[3] for b in boxes)
            ask_box = (ax0, ay0, ax1 - ax0, ay1 - ay0)
        body = int(y1 + 24) if top is not None else 100
        return ask, body, band, ask_box

    def changed_box(self, before: Image.Image, after: Image.Image, thresh=24,
                    min_px=400):
        """Bounding box (image coords) of what changed between two shots."""
        if before.size != after.size:
            return None
        d = np.asarray(ImageChops.difference(before, after).convert("L"), dtype=np.int16)
        m = d > thresh
        if int(m.sum()) < min_px:
            return None
        rows = np.where(m.any(axis=1))[0]
        cols = np.where(m.any(axis=0))[0]
        return (int(cols[0]), int(rows[0]), int(cols[-1] - cols[0] + 1),
                int(rows[-1] - rows[0] + 1))

    def menu_band(self, img: Image.Image) -> tuple[int, int]:
        """(y0, y1) of the menubar strip: the rows just above the dark banner.

        The banner is a reliable landmark, and the ask text inside it mentions the
        menu by name - so searching the top of the window at large would happily
        "find" the menu label inside the ask and click the banner instead.
        """
        a = np.asarray(img.convert("L"), dtype=np.int16)
        # the banner is uniformly dark across the row (>=55% of it), while a row that only
        # carries glyphs or a stray dark edge is not - a plain row *mean* picked up an 8 px
        # dark strip at the top of the window and put the "menubar" above nothing
        darkfrac = (a < 100).mean(axis=1)
        rows = np.where(darkfrac > 0.55)[0][:220]
        if not len(rows):
            return (0, 34)
        y = int(rows[0])
        return (max(0, y - 38), max(6, y - 2))

    def click(self, x, y) -> None:
        # the actor takes a *target* here: {'xy': [x, y]} (not a bare xy pair)
        self.a.run([self.act_step({"op": "click", "target": {"xy": [int(x), int(y)]},
                                   "front_title": self.title})])
        self.stats["clicks"] += 1

    def click_many(self, x, y, times: int) -> None:
        """N clicks on one spot in a single actor run - a Tk Scale trough steps by one
        unit per click, so reaching a value can take a dozen clicks and one run each
        would cost a second of round trips."""
        times = int(times)
        if times <= 0:
            return
        step = {"op": "click", "target": {"xy": [int(x), int(y)]},
                "front_title": self.title}
        self.stats["clicks"] += times
        self.a.run([self.act_step(dict(step)) for _ in range(times)])

    def move_to(self, x, y) -> None:
        self.a.run([self.act_step({"op": "move", "x": int(x), "y": int(y),
                                   "front_title": self.title})])

    def key(self, name, times=1) -> None:
        step: dict = {"op": "key", "keys": [name] * int(times), "front_title": self.title}
        if self.keys and self.bg:
            # focus and post must travel in ONE request: handing the focus over in an
            # earlier call leaves a gap of tens of milliseconds in which the user's
            # window takes it back and Tk silently drops the key (measured: the first
            # press after a hand-off lands, the next one - after a screenshot and an OCR
            # pass - does not)
            step["focus"] = True
        rep = self._timed("ms_key", self.a.run, [self.act_step(step)], results=True)
        if os.environ.get("GYM_DEBUG_ROWS"):
            # the reply says which window the message was posted to and whether the focus
            # hand-off reported success - without it a key that vanished has no trace at all
            for st in rep.get("trace", []):
                dat = st.get("data") or {}
                print("      key %r x%d -> ok=%s bg=%s focused=%s focus_hwnd=%s err=%s"
                      % (name, int(times), st.get("ok"), dat.get("bg"),
                         dat.get("focused"), dat.get("focus_hwnd"), st.get("error")))
        # a rejected key name (the actor validates them) used to disappear into the
        # reply and cost a whole task: say it out loud instead
        for st in rep.get("trace", []):
            if st.get("op") != "key":
                continue                    # only key steps may count as key presses
            if st.get("ok", True):
                self.stats["keys"] += times
            else:
                self.stats["key_errors"] += 1
                self.log("  key %r rejected: %s" % (name, st.get("error")))

    def type_text(self, text) -> None:
        self.a.run([self.act_step({"op": "type", "text": text,
                                   "front_title": self.title})])

    def drag(self, x0, y0, x1, y1) -> None:
        self.a.run([self.act_step({"op": "drag", "x1": int(x0), "y1": int(y0),
                                   "x2": int(x1), "y2": int(y1), "steps": 18, "ms": 140,
                                   "front_title": self.title})])
        self.stats["drags"] += 1

    def wheel(self, notches, x=None, y=None) -> None:
        """Scroll `notches` wheel steps (one notch = 120 raw delta units - the actor
        passes dy straight through to MOUSEEVENTF_WHEEL, so notches must be scaled)."""
        steps = []
        if not self.bg:
            steps.append({"op": "window", "mode": "front", "title_contains": self.title})
        if x is not None:
            steps.append(self.act_step({"op": "move", "x": int(x), "y": int(y),
                                        "front_title": self.title}))
        steps.append(self.act_step({"op": "scroll", "dy": int(notches) * 120}))
        self.a.run(steps)
        self.stats["scrolls"] += 1

    def screen(self, pt) -> tuple[int, int]:
        return (self.origin[0] + int(pt[0]), self.origin[1] + int(pt[1]))

    def hint_near(self, words: list[dict], box, max_dy: int = 16,
                  max_dx: int = 90) -> str | None:
        """The "[k]" the app printed for the control whose label box is `box`.

        Hints sit on the same line as their label, left of it (buttons, rows, toggles,
        form fields, menus, slots); the nearest one wins.
        """
        best: tuple[int, str] | None = None
        for w in words:
            m = HINT_RE.match((w["text"] or "").strip())
            if not m:
                continue
            b = w["box"]
            dy = abs(b[1] - box[1])
            dx = box[0] - b[0]
            if dy > max_dy or dx < -6 or dx > max_dx:
                continue
            score = dy * 4 + abs(dx)
            if best is None or score < best[0]:
                best = (score, m.group(1))
        return best[1] if best else None

    def vis_score(self, img: Image.Image, box, body_top: int = 0) -> float | None:
        """The pre-registered D1 visibility statistic of one label box.

        Byte-for-byte the statistic declared in probe_fill_curve.py: p90 of |L - base|
        over the label box padded by VIS_PAD_X/VIS_PAD_Y, base = median L of the ring
        (padded by VIS_RING_X/VIS_RING_Y minus the box).  The statistic is local - its
        ring reaches 34 px around the box - so it is evaluated on the full frame in the
        frame's own coordinates, and `body_top` only *clamps* the sample so the dark
        banner (which repeats the same word at full contrast) cannot enter the ring.

        The box is deliberately NOT shifted by body_top: the driver's body words are
        already in frame coordinates (`words(region=...)` adds the region origin back).
        Measured in batch 3's first run: cropping by body_top *and* indexing with a
        frame-space box sampled an empty patch above the control, so every D1 came out
        0.0 - which read as "invisible" and refused nine operable controls.
        """
        g = np.asarray(img.convert("L"), dtype=np.int16)
        h, w = g.shape
        x, y, bw, bh = box
        x1 = max(0, x - VIS_PAD_X)
        y1 = max(int(body_top), y - VIS_PAD_Y)
        x2 = min(w, x + bw + VIS_PAD_X)
        y2 = min(h, y + bh + VIS_PAD_Y)
        if (x2 - x1) < 3 or (y2 - y1) < 3:
            return None
        rx1 = max(0, x1 - (VIS_RING_X - VIS_PAD_X))
        ry1 = max(int(body_top), y1 - (VIS_RING_Y - VIS_PAD_Y))
        rx2 = min(w, x2 + (VIS_RING_X - VIS_PAD_X))
        ry2 = min(h, y2 + (VIS_RING_Y - VIS_PAD_Y))
        ring = np.zeros_like(g, dtype=bool)
        ring[ry1:ry2, rx1:rx2] = True
        ring[y1:y2, x1:x2] = False
        if ring.sum() < 20:
            return None
        base = float(np.median(g[ring]))
        inner = np.abs(g[y1:y2, x1:x2] - base).ravel()
        return float(np.percentile(inner, 90))

    def control_visible(self, rec: dict, img: Image.Image, body: list[dict], box,
                        body_top: int) -> bool:
        """Mouse mode: is this hit really a control, or just a word that looks like one?

        The key channel answers this with the "[k]" badge, which only real controls
        carry.  With no badge to read, the pixels have to answer (batch 3's
        `no_badge_fill`): D1 >= T_VIS_FILL means the thing is painted strongly enough to
        be acted on.  The decision is recorded either way, so a refusal caused by this
        rule can never be mistaken for "the label was not found".
        """
        if self.hint_near(body, box):
            rec["vis_badge"] = 1
            return True
        d1 = self.vis_score(img, box, body_top)
        rec["vis_d1"] = None if d1 is None else round(d1, 2)
        if d1 is not None and d1 >= T_VIS_FILL:
            return True
        rec["vis_refuse"] = 1
        return False

    def hint_below(self, words: list[dict], cx: int, cy: int,
                   dy=(25, 95), max_dx: int = 60) -> str | None:
        """The hint the chips canvas paints under a disc (it is on no label line)."""
        best: tuple[float, str] | None = None
        for w in words:
            m = HINT_RE.match((w["text"] or "").strip())
            if not m:
                continue
            b = w["box"]
            bx = b[0] + b[2] // 2
            by = b[1] + b[3] // 2
            if abs(bx - cx) > max_dx or not (dy[0] <= by - cy <= dy[1]):
                continue
            score = abs(bx - cx) + abs(by - cy - (dy[0] + dy[1]) / 2.0)
            if best is None or score < best[0]:
                best = (score, m.group(1))
        return best[1] if best else None

    def band_sig(self, img: Image.Image, box=None) -> list[int]:
        """A coarse fingerprint of the region the ask is drawn in.

        Not a hash: the question "did the words change" needs a tolerance, and equality
        would trip on a single antialiased pixel.  32x4 grey cells are enough - two
        different instructions never land inside the same tolerance.
        """
        if box:
            x, y, w, h = [int(v) for v in box]
            x0, y0 = max(0, x - 6), max(0, y - 4)
            x1, y1 = min(img.width, x + w + 6), min(img.height, y + h + 6)
        else:
            x0, y0, x1, y1 = 0, 0, img.width, min(img.height, BANNER_BAND)
        if x1 - x0 < 4 or y1 - y0 < 2:
            return []
        return [int(v) for v in
                img.crop((x0, y0, x1, y1)).convert("L").resize((32, 4)).getdata()]

    def ask_changed(self, rec: dict, img: Image.Image, cells: int = 3) -> bool:
        """Did the question above this control change since the frame the plan came from?

        The swap family rewrites the ask mid-task and leaves the controls exactly where
        they were, so neither the frame-task guard nor the block check can see it: the
        button is still there and still labelled the same.  Measured: three tasks where
        the driver pressed the answer to the *previous* question.

        The test is the number of cells that moved a lot, not the mean: the ask box is
        ~450 px wide and one word of it changes, so a real swap left the box-wide mean at
        3.7 / 9.2 / 5.7 - under any threshold that noise would also trip.
        """
        sig = rec.get("ask_sig")
        if not sig:
            return False
        now = self.band_sig(img, rec.get("ask_box"))
        if len(now) != len(sig):
            return False
        moved = sum(1 for a, b in zip(sig, now) if abs(a - b) > 30)
        rec["ask_delta"] = round(sum(abs(a - b) for a, b in zip(sig, now))
                                 / float(len(sig)), 1)
        rec["ask_cells"] = moved
        return moved >= cells

    def ask_box_now(self, img: Image.Image) -> tuple | None:
        """Where the ask sits on *this* frame - the pixel section of `chrome()`, no OCR.

        Batch 10 (debt #4): `rec["ask_box"]` is derived once, when the task is read, and
        then frozen - but a `move` chaos re-pads the app's body and slides the banner out
        from under that box, so its right edge ends up *inside* the label and every guard
        re-read comes back as the clean prefix "DO: click the button labelled" (measured,
        batch 7 task 31 `t_trap2-w7-move70`: `ask_label_read` cut, `ask_cells 0`,
        `ask_delta 0.0`, `presses 0`, `decision none`, `replans 2`, `wall 21.3 s` x3 ->
        `--max-repeat 3` early exit at 33/60).  Re-deriving the box from the frame in hand
        restores the whole word: the probe shifted the same two real frames by 40 px and
        read `"...ONYX"` / `"...HARBOP"` out of the recomputed box where the frozen box gave
        `"...ON"` / `"...HARB"` (STATE.md 13.1).

        Cost (STATE.md 13.2, n=20 on two real frames): **3.6 ms**, against 183-196 ms for
        the full `chrome()` - the OCR is the expensive part, and the box needs none of it.

        Returns None when this frame has no banner to measure (so the caller keeps the
        recorded box and behaves exactly as before).
        """
        try:
            g = np.asarray(img.convert("L"), dtype=np.int16)
        except Exception:                # a bad frame must never break the guard
            return None
        darkfrac = (g < 100).mean(axis=1)        # same test as `chrome()`
        top = next((i for i in range(min(len(darkfrac), 220)) if darkfrac[i] > 0.55), None)
        if top is None:
            return None                  # no banner located: keep the frozen box
        y0 = top
        y1 = y0 + 1
        while y1 < len(darkfrac) and darkfrac[y1] > 0.30 and y1 - y0 < BANNER_BAND:
            y1 += 1
        nd = (g >= 100).sum(axis=1)
        rows = [y for y in range(y0, y1) if 0 <= y < len(nd) and nd[y] > 6]
        if not rows:
            return None                  # banner there but no glyph row (mid-repaint)
        # Same x convention as `chrome()`'s per-line region `(14, gy0, width - 28, ...)`,
        # i.e. 14 px off each edge: the window border carries a glyph-shaped artifact on
        # the left that OCRs as a stray "3" in front of a wrapped line.
        x_lo, x_hi = 14, img.width - 14
        if x_hi - x_lo < 20:
            return None
        sub = g[rows[0]:rows[-1] + 1, x_lo:x_hi]
        cols = np.where((sub >= 100).sum(axis=0) > 0)[0]
        if len(cols) == 0:
            return None
        bx = int(x_lo + cols[0])
        bw = int(cols[-1] - cols[0] + 1)
        by, bh = int(rows[0]), int(rows[-1] - rows[0] + 1)
        # Clamp into the band the OCR knows about (STATE.md 13.4 risk 1): on a synthesised
        # or mid-repaint frame the ink rows can wander, and a box that escapes the banner
        # would make `reread` read the app body instead of the question.
        by = max(by, y0)
        bh = min(bh, max(1, min(len(nd), y1) - by))
        if bw < 20 or bh < 6 or bx < 0 or by < 0 or bx + bw > img.width or by + bh > img.height:
            return None
        return (bx, by, bw, bh)

    def ask_label_now(self, img: Image.Image, rec: dict) -> str | None:
        """Re-read the label the current ask names, off the banner, right now.

        The 32x4 fingerprint above cannot see a one-glyph rewrite of the ask: on the
        `swap_hard_*` family B differs from A by a single character and the fingerprint
        stayed inside its tolerance on 3/3 tasks (batch 3, `guard-blind`).  The ask
        sentence is the one place that label is written down, so read it again and
        compare the word itself.

        Returns None when there is nothing to compare: the ask never named a label, or the
        banner came back unreadable - an unreadable read is not evidence that the question
        moved.

        Batch 5: the old precondition also refused every ask whose `ask_source` was `file`,
        on the premise that a file-sourced ask means "nothing on screen to re-read".  The
        recorder marks an ask `file` whenever the screen read *disagrees* with the file,
        which is exactly the truncated-read case - measured t9/t13/t33 pressed with no
        guard read at all (`ask_source=file`, `ask_word=GAMM`/`TUND`).  The banner is on
        screen in every one of those, so the only thing still required is a word to compare.
        """
        if not rec.get("ask_box") or not rec.get("ask_word"):
            return None
        t0 = time.perf_counter()
        try:
            # 2x, not the 4x the *first* ask read uses: this is a confirmation of a word
            # the driver already knows, on the un-faded banner, so it only has to be good
            # enough to tell "the same word" from "one glyph different" (measured: 166 ms
            # per gate at 4x, which is 4x the cost of the code read it confirms).
            # Batch 5: pad the box by 6 px.  The recorded ask box is tight to the text and
            # the read then loses the label's *last* glyph (measured GAMMB -> GAMM and
            # TUNDRA -> TUND out of this very box, at 2x and at 4x), and a guard that can
            # only ever see a truncated form of the new word cannot tell "same word, read
            # short" apart from "different word".
            bx, by, bw, bh = rec["ask_box"]
            # Batch 10 (debt #4): the recorded box is frozen at task-read time and a `move`
            # chaos then slides the banner out from under it - see `ask_box_now` for the
            # measured trail (batch 7 task 31) and the 3.6 ms cost.  Only the *read* window
            # is re-derived: the band fingerprint (`ask_cells` / `ask_delta`) keeps its
            # frozen baseline, so no decision rule changes here.
            fresh = self.ask_box_now(img)
            if fresh:
                rec["ask_box_recomputed"] = int(rec.get("ask_box_recomputed") or 0) + 1
                self.stats["ask_box_recomputed"] = int(
                    self.stats.get("ask_box_recomputed") or 0) + 1
                if "ask_box_shift_px" not in rec:
                    rec["ask_box_shift_px"] = [fresh[0] - bx, fresh[1] - by]
                bx, by, bw, bh = fresh
            pad = 6
            now = self.reread(img, (max(0, bx - pad), max(0, by - pad),
                                    bw + 2 * pad, bh + 2 * pad), psm="7", scale=2)
        except Exception:                    # a bad read must never break the task
            return None
        self.stats["ms_askgate"] = round(
            float(self.stats.get("ms_askgate") or 0.0)
            + (time.perf_counter() - t0) * 1000.0, 1)
        self.stats["ask_gates"] = int(self.stats.get("ask_gates") or 0) + 1
        rec["ask_label_read"] = (now or "").strip()[:60]
        m = re.search(r"labelled (.+)$", now or "", re.I)
        if not m:
            # Batch 8: an *unreadable* read must not be sent as evidence of a change.  The
            # docstring above has promised that since batch 5, but the sentinel returned here
            # was `""`, and the caller reads `""` as "the ask is no longer label-shaped at
            # all" - i.e. as a change.  Measured cost, batch 7 task 31 (`t_trap2-w7-move70`,
            # `two_close_names` + `move` chaos): the reread covers the banner but loses the
            # label token (`ask_label_read "DO: click the button labelled"`), the sentinel
            # becomes a phantom swap, the guard blocks the press and the plan re-reads for
            # ever - `presses 0`, `decision none`, `replans 2`, `wall 21.3 s`, three attempts,
            # `--max-repeat 3` early exit at 33/60 tasks.  On those same frames the band
            # fingerprint said nothing moved at all (`ask_cells 0`, `ask_delta 0.0`).
            # Returning None hands the decision back to that fingerprint - the same stance
            # the near-miss branch below already takes ("errs towards answering instead of
            # re-reading for ever").  What it gives up: a swap that both rewrites the banner
            # into a form this read cannot parse *and* moves no fingerprint cell.
            rec["ask_read_unreadable"] = int(rec.get("ask_read_unreadable") or 0) + 1
            return None
        return m.group(1).strip().rstrip(":;,. ")

    def ask_text_changed(self, rec: dict, img: Image.Image) -> bool:
        """Did the label named by the ask change while the controls stayed put?

        The comparison is on the raw word (case and punctuation only normalised), not on
        the folded `_code` the driver uses to *match* labels.  Folding is for tolerating
        OCR noise when hunting a target; it is the wrong tool for spotting a change,
        because `_CONFUSE` maps Q and O to the same character and therefore hides exactly
        the one-glyph re-rolls this guard exists to catch.  Measured: `HARBOR` vs
        `HARBOP` folds to distinct codes (the equality rule caught it, 1/3 of the family
        turned from wrong to ok), while `TANGO` vs `TANGQ` folds to `74N60` twice - the
        guard re-read the banner as `TANGQ` and still saw "no change", and those are the
        2/3 that stayed guard-blind.

        Only label-shaped asks are compared, because that is the one form where the ask
        names its target; for every other form the coarse fingerprint above is the check.
        """
        want = rec.get("ask_word")
        if not want:
            return False
        got = self.ask_label_now(img, rec)
        if got is None:
            return False
        if got == "":
            # Batch 8: the phantom-swap sentinel.  `ask_label_now` no longer returns `""` for a
            # read it could not parse - that is `None` now, because `""` deadlocked batch 7
            # task 31 (`ask_label_read "DO: click the button labelled"`, `ask_cells 0`,
            # `ask_delta 0.0`, `presses 0`, `decision none`, `replans 2`, `wall 21.3 s` x3 ->
            # early exit at 33/60 tasks).  If a future read path reintroduces it, treat it the
            # way the docstring demands - an unreadable read is not evidence that the question
            # moved - and let the band fingerprint decide.  Counted so it cannot go unnoticed.
            rec["ask_read_unreadable"] = int(rec.get("ask_read_unreadable") or 0) + 1
            return False
        a, b = _plain(got), _plain(want)
        # Batch 8, and deliberately *not* tied to label-shaped asks: if this read shares no
        # two-character run with the word it is meant to confirm, it has not read that word -
        # whatever the ask form and whatever the cause (an ask box recorded before a `move`
        # chaos shoved the layout, or plain OCR loss on the padded strip).  Measured on batch 7
        # task 31 (`move@0.70`): the reread came back as the clean prefix
        # "DO: click the button labelled" - `_plain` "DOCLICKTHEBUTTONLABELLED" vs want
        # "LUMEN93" shares no 2-char run - while the same frame's band fingerprint said the
        # ask had not moved at all (`ask_cells 0`, `ask_delta 0.0`).  A read like that is not
        # evidence of a swap: fall back to the fingerprint (`ask_changed`, already consulted
        # one level up) and count it, instead of blocking the press and re-reading for ever.
        # What it gives up: a swap whose new word also shares no 2-char run with the old one
        # *and* is misread into something unrelated - the fingerprint still covers it whenever
        # the banner actually moved.
        if len(b) >= 2 and not any(b[i:i + 2] in a for i in range(len(b) - 1)):
            rec["ask_read_unreadable"] = int(rec.get("ask_read_unreadable") or 0) + 1
            return False
        sim = difflib.SequenceMatcher(None, a, b).ratio()
        prev = rec.get("ask_label_sim")
        rec["ask_label_sim"] = round(sim, 3) if prev is None else min(prev, round(sim, 3))
        if a != b and (a.startswith(b) or b.startswith(a)):
            # Batch 5: the banner read loses the label's last glyph on this rig (measured
            # GAMMB -> GAMM, TUNDRA -> TUND, at 2x and at 4x), so a word that is a *prefix*
            # of the planned word is not evidence that the question moved - it is the same
            # word read short.  Counting it as a change would make the guard fire on every
            # press and the task would re-read for ever instead of answering (t9: the plan
            # word can only be `GAMMB` while every banner read of it says `GAMM`).
            # What this deliberately gives up: a real swap between two words where one is a
            # prefix of the other.  The measured families re-roll to unrelated words.
            rec["ask_word_short"] = int(rec.get("ask_word_short") or 0) + 1
            return False
        if a != b:
            # Batch 5: firing on OCR noise and staying silent on a real one-glyph re-roll are
            # both failure modes, and the banner text alone cannot tell them apart - measured
            # `GAMMB` (plan) read back as `GAMMI` (noise, task 9/10/11) and `GAMMA` (plan)
            # read back as `GAMMI` (real swap, task 13).  Both are one glyph off, both at 0.8
            # similarity, and the 32x4 fingerprint does *not* separate them either: the real
            # one-glyph swap of task 13 moved no cell at all (`ask_cells = 0`, `ask_delta 0.3`).
            #
            # What does separate them is the target's own current declaration: the app
            # rewrites the ask sentence in its state file the moment it re-rolls, so
            #   * file word == planned word  -> the app still declares the planned ask, the
            #     banner read is the noisy one (measured: t9 deadlocked for 3 x 16 s on this);
            #   * file word != planned word  -> the ask really moved, fire (measured: t13 went
            #     stale because this branch did not exist yet).
            # The comparison is on the raw word, never on folded `_code` (folding hides exactly
            # the one-glyph re-rolls this guard exists to catch).  When the file cannot be read
            # the old fingerprint test stands: near-miss text on a fingerprint-clean banner is
            # treated as noise, which errs towards answering instead of re-reading for ever.
            m2 = re.search(r"labelled (.+)$",
                           (self.state() or {}).get("ask") or "", re.I)
            fw = m2.group(1).strip().rstrip(":;,. ") if m2 else ""
            if fw and _plain(fw) == b:
                rec["ask_word_noise"] = int(rec.get("ask_word_noise") or 0) + 1
                return False
            self.ask_changed(rec, img)       # fill ask_cells/ask_delta for this frame
            near = abs(len(a) - len(b)) <= 1 and sim >= 0.75
            if not fw and near and rec.get("ask_cells") == 0:
                rec["ask_word_noise"] = int(rec.get("ask_word_noise") or 0) + 1
                return False
            rec["ask_changed_text"] = True
            return True
        return False

    def ask_moved_now(self, rec: dict, img: Image.Image) -> bool:
        """Cheap check first (free), the label re-read second (only where it applies)."""
        if self.ask_changed(rec, img):
            rec["ask_moved_band"] = int(rec.get("ask_moved_band") or 0) + 1
            return True
        if self.ask_text_changed(rec, img):
            rec["ask_moved_text"] = int(rec.get("ask_moved_text") or 0) + 1
            return True
        return False

    def press_guard(self, rec: dict) -> bool:
        """Last look before a press lands: is this still the question we planned for?

        `verify_before_act` runs on the frame the plan came from and its budget is one
        call per task, so a swap that fires *after* it is invisible - measured in batch 3,
        the `swap_timer` family lands in a 70-150 ms window between the verify frame and
        the press (race 5/5).  A fresh frame immediately before the press shrinks that
        window to the guard itself.  The cost is one shot plus one banner re-read, both
        counted in `ms_askgate`/`ask_gates` so the next profiling run shows what it bought.
        """
        # Batch 5: the old precondition was `ask_source == "screen"`, written on the premise
        # that a file-sourced ask means "nothing on screen to re-read".  The recorder marks
        # an ask `file` whenever the screen read *disagrees* with the file - which is
        # exactly the truncated-read case (measured t9/t13/t33: `ask_source=file` and the
        # press went out unguarded, so `ask_gates` counted 48 of 51 presses).  The banner
        # fingerprint is taken for every ask, so the guard now runs whenever a plan exists;
        # a plan with no fingerprint and no box at all is the only skip, and it is counted
        # (`ask_guard_skipped`, target 0) instead of passing silently.
        if not rec.get("ask_sig") and not rec.get("ask_box"):
            rec["ask_guard_skipped"] = int(rec.get("ask_guard_skipped") or 0) + 1
            self.stats["ask_guard_skipped"] = int(
                self.stats.get("ask_guard_skipped") or 0) + 1
            return True
        # Batch 9 (#10): the timer starts *after* the frame is in hand.  Batch 6 measured
        # this per-row `gate_ms` at P50 369.7 ms while the independent re-read-only count
        # `ms_askgate/ask_gates` said 148.1 ms - the ~220 ms gap was the capture, not the
        # gate, and it overstated what the guard costs on a plan that already has a frame.
        img = self.shot()
        t_gate = time.time()
        self.stats["ask_guard_runs"] = int(self.stats.get("ask_guard_runs") or 0) + 1
        moved = self.ask_moved_now(rec, img)
        # Batch 6: every gate reports its own cost, so a later run can print P50/P95
        # instead of one mean over a long tail (criterion: P50 <= 240 ms, P95 <= 320 ms;
        # batch 5 measured a 143.4 ms *mean* and could not see the tail at all).
        rec.setdefault("gate_ms", []).append(round((time.time() - t_gate) * 1000.0, 1))
        self.stats["gate_samples"] = int(self.stats.get("gate_samples") or 0) + 1
        if not moved:
            self.press_jitter(rec)
            return True
        rec["ask_moved"] = int(rec.get("ask_moved") or 0) + 1
        rec["ask_moved_press"] = int(rec.get("ask_moved_press") or 0) + 1
        self.stats["ask_moved"] = int(self.stats.get("ask_moved") or 0) + 1
        self.stats["ask_moved_press"] = int(self.stats.get("ask_moved_press") or 0) + 1
        self.stats["replans"] = int(self.stats.get("replans") or 0) + 1
        return False

    def press_jitter(self, rec: dict) -> None:
        """`--press-jitter LO,HI`: pause between the guard's frame and the click.

        Batch 6, and it is a measurement hook rather than a fix.  The target's timer
        shapes swap 600-1000 ms after the paint (`gym_app.py:1414`), so the guard's
        fresh frame at ~1.4 s already sees them and replans - which is exactly why batch
        5 measured race 0/0.  The only window in which a swap can still win is *after*
        that frame and before the click lands, so a run that wants a denominator widens
        its own side of it: this sleeps a random LO..HI ms right here, and only for the
        `swap_race_timer` variant.  Gating on the variant (a class label read from the
        state file, recorded in `rec["press_jitter_task"]`) keeps the batch comparable:
        without it the jitter would turn `swap_timer` regression tasks into races too.
        It never changes *what* is pressed - the plan is fixed and already cleared.
        """
        lo, hi = self.jitter
        if hi <= 0 or lo < 0:
            return
        if str((self.state() or {}).get("variant") or "") != "swap_race_timer":
            return
        delay = random.randint(lo, hi)
        rec["press_delay_ms"] = int(rec.get("press_delay_ms") or 0) + delay
        rec["press_jitter_task"] = 1
        self.stats["press_delays"] = int(self.stats.get("press_delays") or 0) + 1
        self.stats["press_delay_ms"] = round(
            float(self.stats.get("press_delay_ms") or 0.0) + delay, 1)
        time.sleep(delay / 1000.0)

    def verify_before_act(self, rec: dict, box, expect: str) -> bool:
        """Block-level sanity check on the control we are about to touch (design §5.1).

        "Is the thing I am about to operate still there and still the same?"  One
        `find_blocks` pass over the frame (measured 22 ms offline) plus, when a block
        covers the target, one label read.  Nothing here knows about the target app, so
        the same call works on a real program.

        Returns True when the target may be acted on.  Returns False when the world moved
        - the caller must re-read rather than press.  Budgets (design §6.1): at most one
        `find_blocks` per task, and at most three re-reads per task; on the fourth
        mismatch the task is given up (`verify_giveup`, `decision=timeout`) instead of
        re-reading forever while a repainting target keeps failing the check.
        """
        if rec.get("verify_giveup"):
            return False
        if int(rec.get("verify_calls") or 0) >= 1:
            return True                     # budget spent: do not slow the task down twice
        rec["verify_calls"] = int(rec.get("verify_calls") or 0) + 1
        self.stats["verify_calls"] = self.stats.get("verify_calls", 0) + 1
        img = self.shot()
        if self.ask_moved_now(rec, img):
            # the question itself moved while the control stayed put: the block check
            # below cannot see this, so check the ask first and re-read instead of press
            rec["ask_moved"] = int(rec.get("ask_moved") or 0) + 1
            self.stats["ask_moved"] = self.stats.get("ask_moved", 0) + 1
            return False
        bx, by, bw, bh = box
        cx, cy = bx + bw / 2, by + bh / 2
        over = [b for b in self.find_blocks(img)
                if b[0] <= cx <= b[0] + b[2] and b[1] <= cy <= b[1] + b[3]]
        if not over:
            # flat / translucent controls paint no block of their own; without one there is
            # nothing to compare, and guessing "stale" here would refuse honest tasks
            rec["verify_skipped"] = int(rec.get("verify_skipped") or 0) + 1
            return True
        label = self.block_label(img, over[0])
        if difflib.SequenceMatcher(None, _code(label), _code(expect)).ratio() >= 0.6:
            return True
        n = int(rec.get("verify_rereads") or 0) + 1
        rec["verify_rereads"] = n
        self.stats["verify_rereads"] = self.stats.get("verify_rereads", 0) + 1
        rec.setdefault("verify_mismatch", []).append([label, expect, list(over[0])])
        if n >= 3:
            rec["verify_giveup"] = 1
            rec["decision"] = "timeout"
            self.stats["verify_giveup"] = self.stats.get("verify_giveup", 0) + 1
        return False

    def press_hint(self, rec: dict, body: list[dict], box, what: str,
                   max_dy: int = 16, max_dx: int = 90, expect: str | None = None) -> bool:
        """Press the key hint belonging to `box`; record why when there is none.

        When the target can change under us (chaos runs), the control is looked at
        once more right before the press: `body` was read from a frame taken at the
        start of the task, and a mid-task rebuild re-labels and re-lays-out the body
        while the hint carries over to a *different* control - measured on a rebuilt
        button board, the old hint pressed `PRISM11` when the ask named `mica36`, and
        the app scored that as a wrong answer.
        """
        hint = self.hint_near(body, box, max_dy, max_dx)
        if hint and rec.get("frame_task_i") is not None and self.task_i() != rec["frame_task_i"]:
            # the app has moved on since this frame was taken: the box and its hint belong
            # to the previous question, so acting on them answers the wrong one
            rec["stale_actions"] = int(rec.get("stale_actions") or 0) + 1
            rec.setdefault("stale_detected", True)
            self.stats["stale_actions"] = self.stats.get("stale_actions", 0) + 1
            return False
        if hint and expect and not self.verify_before_act(rec, box, expect):
            return False                    # world moved under the frame: re-read, do not press
        if hint and self.verify_targets and expect:
            img2 = self.shot()
            bx, by, bw, bh = box
            pad = 4
            got = self.reread(img2, (max(0, bx - pad), max(0, by - pad), bw + 2 * pad,
                                     bh + 2 * pad), psm="7")
            sim = difflib.SequenceMatcher(None, _code(got), _code(expect)).ratio()
            if sim < 0.6:
                self.stats["hint_stale"] = self.stats.get("hint_stale", 0) + 1
                rec.setdefault("hint_stale", []).append(
                    [what, hint, got, expect, round(sim, 2)])
                return False            # the world moved: re-read instead of guessing
        if not hint:
            self.stats["no_hint"] += 1
            rec.setdefault("hint_missing", []).append(what)
            # keep the geometry of the nearest hint-shaped tokens: without it a missing
            # hint is indistinguishable from a row that never carried one
            near = []
            for w in body:
                m = HINT_RE.match((w["text"] or "").strip())
                if m:
                    b = w["box"]
                    near.append((abs(b[1] - box[1]) + abs(box[0] - b[0]),
                                 m.group(1), list(b)))
            near.sort()
            rec.setdefault("hint_missing_near", []).append([what, near[:3], list(box)])
            return False
        rec.setdefault("hints", []).append([what, hint])
        if not self.press_guard(rec):
            return False                    # the question moved: re-read, do not press
        self.key(hint)
        rec["presses"] = int(rec.get("presses") or 0) + 1
        rec.setdefault("decision", "acted")
        return True

    def refuse(self, rec: dict, why: str) -> None:
        """Say out loud that nothing on screen is a legal control: press F8, record it.

        A refusal has to be an observable act: silence is indistinguishable from a
        timeout, and "did not press the wrong thing" must be scorable as a win.

        The refusal key is protocol, not an answer: it is armed on every trap task and it
        is the *only* way to refuse.  So it is sent in the mouse channel too - `--keys`
        decides whether hint badges may be used to act, not whether a refusal can be seen.
        (In background mode a posted key is what reaches the window, and that path is the
        one `--keys` runs already use; in the foreground the key is a real one.)
        """
        rec["decision"] = "refused"
        rec["refuse_why"] = why
        self.stats["refusals"] = int(self.stats.get("refusals", 0)) + 1
        if self.keys or not self.bg:
            self.key(REFUSE_KEY)

    def no_key_refuse(self, rec: dict) -> None:
        """A control with the right name but no action key is not operable.

        Measured on the trap family: a disabled control is drawn with its label and
        gets no `[k]` badge, so `press_hint` finds no hint at all.  Reading that as
        "press nothing and wait" would score a correct refusal as a timeout.  A
        stale-hint rejection is *not* this case: there the world moved, so the right
        move is to re-read rather than to refuse - and so is a failed verification, a
        question that changed under the plan, or a frame whose task has already been left
        behind.
        """
        if rec.get("hint_stale") or rec.get("verify_rereads") or rec.get("stale_actions") \
                or rec.get("verify_giveup") or rec.get("ask_moved"):
            return
        self.refuse(rec, "the control carries no action key")

    def row_hint(self, img, box, rec: dict | None = None) -> str | None:
        """Read the `[k]` badge drawn left of a row of the list - in one tight crop.

        Measured on a 17-row task: the whole left strip (x 8..96) reads as garbage
        (`'pl'`, `'(27'`, `']'`) because a solid dark accent bar sits between the badge
        and the row id, while the badge alone (`bx-84`, 44 px wide) reads 17/17 exact at
        both 4x and 6x. Also note the badge alphabet is the app's, not just 1..9.
        """
        bx, by, _bw, bh = box
        crop = (max(0, bx - 84), max(0, by - 8), 44, bh + 16)
        got = self.reread(img, crop, whitelist=SCAN_KEYS + "[]()<>", psm="7")
        if rec is not None:
            rec.setdefault("row_hint_badge", []).append(got)
        m = re.search(r"[\[\(<]\s*([0-9A-Za-z])\s*[\]\)>]", got or "")
        if m and m.group(1) in SCAN_KEYS:
            return m.group(1)
        # Measured on a rebuilt 17-row board: the tight badge crop often comes back as
        # the bare character ("a" for a badge drawn as "[a]") - tesseract drops the thin
        # brackets. A lone allowed character therefore counts as the badge too; uppercase
        # noise such as the "I" that a mangled badge reads as is not in the app's
        # alphabet and stays rejected.
        lone = re.sub(r"[^0-9A-Za-z]", "", got or "")
        if len(lone) == 1 and lone in SCAN_KEYS:
            return lone
        return None

    def hint_of(self, words: list[dict], target: str) -> str | None:
        """The key hint printed in front of `target` on a key line."""
        for i, w_ in enumerate(words):
            if target and G.norm(target) in G.norm(w_["text"]):
                for j in range(i - 1, max(-1, i - 3), -1):
                    m = HINT_RE.match(words[j]["text"].strip())
                    if m:
                        return m.group(1)
        return None

    def synonym_verb(self, text: str, ratio: float = 0.8) -> str | None:
        """The intent verb an ask opens with, tolerating one OCR slip in that word.

        The banner is read at 2x and there is no second read of the whole sentence, so a
        single confusable glyph used to turn the ask into nothing at all (measured:
        `acknowledae the alert` -> `act=unknown`, no action taken, and the run's early-stop
        guard then threw away the rest of the batch).  Matching is on the first word only
        and only against general intent vocabulary - the control labels are still read off
        the screen, so nothing here is a memorised answer.
        """
        first = (text.split() or [""])[0].strip(".,;:!?").casefold()
        if not first:
            return None
        if first in SYNONYM_ACT:
            return first
        best, score = None, ratio
        for k in SYNONYM_ACT:
            r = difflib.SequenceMatcher(None, first, k).ratio()
            if r >= score:
                best, score = k, r
        return best

    def find(self, words, target, min_score=0.8) -> dict | None:
        hits = G.find_text(words, target, min_score=min_score)
        return hits[0] if hits else None

    def find_all(self, words, target, min_score=0.82) -> list[dict]:
        """Every occurrence of this label on screen, best match first.

        A name can stand twice in one screen: in the sentence that asks for it and on the
        control that carries it.  `find` returns whichever the matcher scores first, and
        measured on the t_trap prose class that was the sentence - which carries no `[k]`
        badge, so the driver refused a task it could have answered.
        """
        return [h for h in G.find_text(words, target, min_score=min_score) if h]

    def try_other_occurrences(self, rec: dict, body: list[dict], label: str, used) -> bool:
        """Press another occurrence of the same label when the chosen one had no key.

        Only occurrences that already show a `[k]` badge are tried, so this can turn a
        wrong refusal into a press but never a real refusal into one: a disabled control
        and a name that lives only in prose carry no badge anywhere on screen.
        """
        if not label:
            return False
        for w in self.find_all(body, label, 0.82):
            if list(w["box"])[:2] == list(used)[:2]:
                continue
            if not self.hint_near(body, w["box"]):
                continue
            rec.setdefault("alt_occurrences", []).append([w["text"], list(w["box"])])
            if not self.keys:
                if not self.press_guard(rec):
                    return False
                x, y = self.screen(w["center"])
                self.click(x, y)
                rec["target_box"] = list(w["box"])
                return True
            if self.press_hint(rec, body, w["box"], "button", expect=w["text"]):
                rec["target_box"] = list(w["box"])
                return True
            if rec.get("verify_giveup"):
                return False
        return False

    def state(self) -> dict:
        try:
            with open(self.state_path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {}

    def result(self) -> str:
        return self.state().get("result", "none")

    def task_i(self) -> int:
        return int(self.state().get("task_i", -1))

    def verdict(self, task_i: int) -> dict | None:
        """The verdict for a finished task, looked up in the app's history.

        The pending `result` field is useless for scoring: the app resets it as
        soon as the next task starts (gap_ms), so a driver that acts fast and
        then polls would always read "none" even for a task it solved.
        """
        for rec in self.state().get("history", []):
            if rec.get("task_i") == task_i:
                return rec
        return None

    def wait_verdict(self, task_i: int, timeout=3.0) -> dict:
        t0 = time.time()
        while time.time() - t0 < timeout:
            rec = self.verdict(task_i)
            if rec:
                return rec
            time.sleep(0.1)
        return {"task_i": task_i, "result": "none", "detail": {}}

    def judge_wait(self, task_i: int, timeout: float = 0.9) -> bool:
        """True once the app has scored this task - reads the state file, not the screen.

        Pressing a row key is the answer, so waiting for the verdict is cheap here; a
        full shot + body OCR (~2.5 s) just to notice the task is gone is what made the
        row scenario cost ~7.5 s per task.
        """
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self.verdict(task_i):
                return True
            time.sleep(0.08)
        return False

    def wait_task(self, previous: int, timeout=4.0) -> int:
        """Block until the app has moved on from task `previous`."""
        t0 = time.time()
        while time.time() - t0 < timeout:
            now = self.task_i()
            if now > previous:
                return now
            time.sleep(0.08)
        return self.task_i()

    def wait_result(self, timeout=3.0) -> str:
        t0 = time.time()
        while time.time() - t0 < timeout:
            res = self.result()
            if res != "none":
                return res
            time.sleep(0.12)
        return "none"

    # -------------------------------------------------------------- tasks ---
    def _overlaps(self, screen_box, win_box) -> bool:
        """Does an image-space box (window coords) touch a screen-space box?"""
        x, y, w, h = win_box
        sx, sy = self.screen((x, y))
        return (screen_box[0] < sx + w and screen_box[0] + screen_box[2] > sx and
                screen_box[1] < sy + h and screen_box[1] + screen_box[3] > sy)

    def do_task(self, want_ask: str | None = None) -> dict:
        t0 = time.perf_counter()
        img = self.shot()
        blocked = 0
        if self.keys and self.bg:
            # measured (probe_post_key.py): Tk drops posted keys unless the window holds
            # the keyboard focus, and SetFocus only works from inside its own thread -
            # `window mode=focus` does that hand-off without stealing the user's window
            self.focus_window()
        if self.expect_chaos:            # something may be sitting on top of the app
            img, blocked = self.dismiss_interference(img)
        ask, body_top, band, ask_box = self.chrome(img)
        body = self.body_words(img, body_top)
        # keep what this plan was built on: a failed task is diagnosed from the frame
        # and words the driver actually saw, not from a fresh look at a later task
        self.last_frame, self.last_band, self.last_body = img, band, body
        top = self.words(img, region=(0, 0, img.width, 40), min_conf=20.0)
        rec = {"ask_screen": ask, "ask_file": want_ask, "body_top": body_top}
        # A mouse action is a press for accounting purposes: `decision`/`wasted_actions`
        # were derived from key presses only, so every mouse-mode record came out as
        # `decision: none` even when the plan had clicked (measured in batch 3: swap_timer
        # rows were scored `wrong` by the app while the record claimed no action at all).
        # Counting the driver's own click stat as a delta covers every click site at once.
        clicks0 = int(self.stats.get("clicks", 0) or 0)
        # Design §5.2: keep a fingerprint of the question this plan answers, so a mid-task
        # swap can be told apart from a control that merely repainted (measured: three
        # tasks pressed the previous question's answer because the buttons never moved).
        rec["ask_box"] = list(ask_box) if ask_box else None
        rec["ask_sig"] = self.band_sig(img, ask_box)
        # Design §5.1: bind the frame to the task it came from.  Every box in `body`
        # belongs to the task standing at this instant; if the app moves on before the
        # action lands, the box is stale and pressing its hint answers the *next*
        # question (measured: chaos-p1.0 #4 clicked `ember61` when the ask said `BRAVO`).
        rec["frame_task_i"] = self.task_i()
        if blocked:
            rec["interferences_at_start"] = blocked
        if want_ask and G.norm(ask).endswith(G.norm(want_ask)) or (want_ask and G.norm(want_ask) in G.norm(ask)):
            self.stats["asks_from_screen"] += 1
            rec["ask_source"] = "screen"
        else:
            self.stats["asks_from_file"] += 1
            rec["ask_source"] = "file"
            ask = ask or (want_ask or "")
        text = ask.split(":", 1)[-1].strip() if ":" in ask[:4] else ask
        text = re.sub(r"^\s*[Dd][O0]\s*[:;.]?\s*", "", text).strip()
        rec["ask"] = text
        act = "unknown"
        if (m := re.search(r"click the button labelled (.+)$", text, re.I)):
            act = "click_label"
            # The banner is read at 2x, and the label is a 10-character code: measured
            # "XENON93" on screen read back as "XENONQY:" - the 9/3 pair lost to Q/Y.
            # The ask is the only place the label is named, so a bad read there costs
            # the task outright ("label not found in OCR map"). Ask for the label
            # twice: the banner read first, then a 4x re-read of the same banner box.
            rec["want"] = m.group(1).strip().rstrip(":;,. ")
            # The word the *ask* named, kept apart from `want`: the fuzzy fallback below
            # may replace `want` with the best on-screen candidate, and the pre-press
            # guard has to compare against what the banner said, not against that guess.
            rec["ask_word"] = rec["want"]
            cands = [rec["want"]]
            if ask_box:
                # Batch 5: same 6 px pad as the guard's re-read - this box is tight too,
                # and a candidate that lost its last glyph is what starts the mis-match.
                bx0, by0, bw0, bh0 = ask_box
                again = self.reread(img, (max(0, bx0 - 6), max(0, by0 - 6),
                                          bw0 + 12, bh0 + 12), psm="7")
                rec["ask_reread"] = again
                m2 = re.search(r"labelled (.+)$", again, re.I)
                if m2:
                    label2 = re.sub(r"[^A-Za-z0-9]+$", "",
                                    m2.group(1).strip().rstrip(":;,. "))
                    if label2 and label2 not in cands:
                        cands.append(label2)
            # Batch 5: the banner read loses the label's last glyph, and the truncated word
            # then matched the *other* button by folding similarity - `GAMM` vs `GAMMA`
            # folds to 0.889 >= the 0.82 the plain `find` uses - so the driver pressed a
            # label the ask never named (t9/t13: clicked GAMMA while the ask said GAMMB).
            # The file's copy of the ask is spelled in full, so it joins the candidates,
            # and the only evidence that can settle a disagreement decides: an *exact*
            # folded match on screen.  Exactly one candidate with exactly one occurrence
            # -> that is the ask's word.  No exact match anywhere -> the old fuzzy path.
            m3 = re.search(r"labelled (.+)$", want_ask or "", re.I)
            if m3:
                label3 = re.sub(r"[^A-Za-z0-9]+$", "",
                                m3.group(1).strip().rstrip(":;,. "))
                if label3 and label3 not in cands:
                    cands.append(label3)
            exact: dict = {}
            for w_ in body:
                exact.setdefault(_plain(w_["text"]), []).append(w_)
            hit = None
            # Batch 6 (measured, `probe-w6-twin.json`): when the ask's word is on screen
            # more than once, the occurrence inside a *painted* rectangle is the control
            # and the bare ones are text.  The twin's heading is a live `tk.Label` bound
            # to a click, so text alone cannot separate it from the button it duplicates
            # - the old scorer picked the heading (score 2.543, veto False) while the
            # button sat in a block of fill 1.0.  This pass only ranks: with no unique
            # painted occurrence the exact/fuzzy path below decides as it did in batch 5.
            boxes: list[tuple] = []
            for c in cands:
                occ = [w_ for w_ in body if _plain(w_["text"]) == _plain(c)]
                if len(occ) < 2:
                    continue
                rec["label_text_like"] = int(rec.get("label_text_like") or 0) + len(occ) - 1
                if not boxes:
                    boxes = self.painted_boxes(img, rec)
                pick = self.painted_hit(occ, boxes)
                if pick:
                    hit = pick
                    rec["want"] = rec["ask_word"] = c
                    rec["ask_word_from"] = "painted"
                    rec["label_painted"] = int(rec.get("label_painted") or 0) + 1
                    rec["label_alt_tried"] = int(rec.get("label_alt_tried") or 0) + 1
                    break
            if not hit:
                for c in cands:
                    same = exact.get(_plain(c)) or []
                    if len(same) == 1:
                        # an exact match is evidence, not a guess: the ask did name this
                        # word, so the guard compares the banner against it (`ask_word`)
                        # and not against the truncated read that lost the last glyph
                        hit = same[0]
                        rec["want"] = rec["ask_word"] = c
                        rec["ask_word_from"] = "exact"
                        break
            if not hit:
                for c in cands:
                    hit = self.find(body, c, 0.82) or self.find(body, c, 0.7)
                    if hit:
                        rec["want"] = c
                        rec["ask_word_from"] = "fuzzy"
                        break
            if hit:
                rec["target_box"] = hit["box"]
                if self.keys:
                    if not self.press_hint(rec, body, hit["box"], "button", expect=c) \
                            and not self.try_other_occurrences(rec, body, c, hit["box"]):
                        self.no_key_refuse(rec)
                elif self.control_visible(rec, img, body, hit["box"], body_top):
                    if self.press_guard(rec):
                        x, y = self.screen(hit["center"])
                        self.click(x, y)
                    # else: the question moved under us - the re-read loop takes it from here
                else:
                    self.refuse(rec, "the control is painted below the visibility floor")
            else:
                # last resort: the label is on screen but every read of it is wrong in
                # one glyph. Compare folded forms and accept a candidate only when it
                # wins by a clear margin - two similar labels on screen must never be a
                # coin flip, because clicking the wrong button answers wrongly.
                best, second = (None, 0.0), 0.0
                for w_ in body:
                    r = difflib.SequenceMatcher(None, _code(cands[0]), _code(w_["text"])).ratio()
                    if r > best[1]:
                        best, second = (w_, r), best[1]
                    elif r > second:
                        second = r
                rec["label_fuzzy"] = [round(best[1], 3), round(second, 3)]
                # measured: banner "XENON93" read as "XENONQY" twice (2x and even 4x re-read
                # of the same box), which folded-compares to the true label at 0.714 while
                # the next-best token on screen scores 0.267 - a mistaken read of the ask is
                # not a reason to give the task up when exactly one thing on screen is close.
                if best[0] is not None and best[1] >= 0.66 and best[1] - second >= 0.15:
                    rec["want"] = best[0]["text"]
                    rec["target_box"] = best[0]["box"]
                    if self.keys:
                        if not self.press_hint(rec, body, best[0]["box"], "button",
                                              expect=rec.get("want")) \
                                and not self.try_other_occurrences(
                                    rec, body, rec.get("want"), best[0]["box"]):
                            self.no_key_refuse(rec)
                    elif self.control_visible(rec, img, body, best[0]["box"], body_top):
                        if self.press_guard(rec):
                            x, y = self.screen(best[0]["center"])
                            self.click(x, y)
                    else:
                        self.refuse(rec, "the control is painted below the visibility floor")
                else:
                    rec["error"] = "label not found in OCR map"
                    # No control on screen carries that name.  The old behaviour was to
                    # press nothing and let the task time out, which scores the same as
                    # freezing; the honest act is to say so (must_refuse tasks are
                    # exactly the ones where the name exists only in prose, or is
                    # disabled, or two candidates are indistinguishable).
                    self.refuse(rec, "no control carries the asked label")
        elif (verb := self.synonym_verb(text)) is not None:
            act = "synonym_invoke"
            rec["verb"] = verb
            # The ask names an intent, not a label ("dismiss the notice"), so the move is
            # to find a control a UI would use for that intent.  The trap's labels are
            # random words, so this is general vocabulary, not a memorised answer.
            hit = None
            for lab in SYNONYM_ACT[verb]:
                cand = self.find(body, lab, 0.9)
                if not cand:
                    continue
                # The intent also appears *in the sentence* ("Close the notice to
                # continue"), so the first synonym hit is routinely the prose copy of the
                # word.  A word with no action key beside it is not a control: keep
                # looking rather than refusing on the prose and never reaching the real
                # button (measured: ask "close the notice", prose "Close", real control
                # "OK" - the driver refused an answerable task).
                if self.keys and not self.hint_near(body, cand["box"]):
                    rec.setdefault("synonym_prose", []).append(lab)
                    continue
                if not self.keys:
                    # Batch 6, the same judge as the twin fix: the intent word also
                    # appears in the *sentence* ("Close the notice to continue"), and
                    # the keyboard channel drops that copy through its action-key hint
                    # while the mouse channel had nothing - measured in batch 4 as
                    # clicks on prose.  The painted occurrence is the control; when it
                    # is not unique, the old first hit stands, exactly as before.
                    occ = self.find_all(body, lab, 0.9)
                    if len(occ) > 1:
                        pick = self.painted_hit(occ, self.painted_boxes(img, rec))
                        if pick:
                            cand = pick
                            rec["label_painted"] = int(rec.get("label_painted") or 0) + 1
                        else:
                            rec["label_text_like"] = int(
                                rec.get("label_text_like") or 0) + len(occ) - 1
                hit = cand
                rec["want"] = hit["text"]
                rec["synonym_hit"] = lab
                break
            if not hit:
                rec["synonym_cands"] = [w_["text"] for w_ in body][:12]
            if hit:
                rec["target_box"] = hit["box"]
                if self.keys:
                    if not self.press_hint(rec, body, hit["box"], "button",
                                           expect=rec.get("want")) \
                            and not self.try_other_occurrences(
                                rec, body, hit["text"], hit["box"]):
                        self.no_key_refuse(rec)
                elif self.control_visible(rec, img, body, hit["box"], body_top):
                    if self.press_guard(rec):
                        x, y = self.screen(hit["center"])
                        self.click(x, y)
                else:
                    self.refuse(rec, "the control is painted below the visibility floor")
            else:
                rec["error"] = "no control offers a word for %r" % verb
                self.refuse(rec, "the ask names an intent no control offers")
        elif (m := re.search(r"select the row whose id\s*(?:is\s*)?(\d+)", text, re.I)):
            act = "select_row"
            rec["want"] = m.group(1)
            if self.keys:
                # measured: Home really does jump to the top of the list, and from there
                # a single Next already reaches the bottom. The canvas keeps its scroll
                # position between tasks, so a target living in the top view is simply
                # unreachable by paging downwards only - always start from the top.
                self.key("Home")
                time.sleep(0.3)
            prev_ids: tuple = ()
            for attempt in range(7):
                if self.keys:
                    img2 = self.shot()
                    w2 = self.body_words(img2, body_top)
                else:
                    img2 = self.shot() if attempt else img
                    w2 = body if attempt == 0 else self.body_words(img2, body_top)
                hit = None
                for it in w2:
                    if re.search(r"\d", it["text"]) and rec["want"] in G.norm(it["text"]):
                        hit = it
                        break
                if hit is None:
                    for line in G.group_lines(w2):
                        if rec["want"] in G.norm(line["text"]):
                            hit = line
                            break
                if os.environ.get("GYM_DEBUG_ROWS"):
                    ids_dbg = [w_["text"] for w_ in w2 if re.search(r"\d{3,}", w_["text"])]
                    hsh = [(w_["text"], w_["box"]) for w_ in w2
                           if HINT_RE.match(w_["text"].strip())]
                    print("      attempt %d words=%d hit=%r box=%r ids=%s"
                          % (attempt, len(w2), hit["text"] if hit else None,
                             hit["box"] if hit else None, ids_dbg[:6]))
                    print("      hints=%s" % hsh)
                if hit:
                    rec["target_box"] = hit["box"]
                    rec["scrolls"] = attempt
                    if self.keys:
                        # The badge is the reliable channel here: one tight crop reads
                        # 17/17 exact, while the word list drops hints now and then.
                        k = self.row_hint(img2, hit["box"], rec)
                        if k:
                            self.key(k)
                            rec["row_hint_key"] = k
                            if self.judge_wait(self.task_i()):
                                break
                            time.sleep(0.15)
                            continue
                        if not self.press_hint(rec, w2, hit["box"], "row",
                                               expect=rec.get("want")):
                            # No hint-shaped token next to the row either. Read the badge
                            # once more from a fresh frame before blaming the scroll
                            # position: a frame taken mid-repaint can miss it.
                            img3 = self.shot()
                            k = self.row_hint(img3, hit["box"], rec)
                            if k:
                                self.key(k)
                                rec["row_hint_key"] = k
                                time.sleep(0.25)
                                continue
                            # otherwise the row is probably clipped at the canvas edge:
                            # nudge the view by a single unit (a whole page jump keeps
                            # skipping it)
                            self.key("Down")
                            time.sleep(0.25)
                            continue
                    else:
                        x, y = self.screen(hit["center"])
                        self.click(x, y)
                    break
                ids = tuple(G.norm(w_["text"]) for w_ in w2 if re.search(r"\d{3,}", w_["text"]))
                if ids and ids[:3] == prev_ids[:3]:
                    # the page did not move: the end of the list is on screen already
                    # (compared loosely - OCR of a clipped row wobbles between reads)
                    rec["error"] = "row never appeared (%d pages)" % attempt
                    break
                prev_ids = ids
                if self.keys:
                    # the wheel is a mouse message and Tk ignores those while it is not
                    # focused (measured: 63 posted wheel steps moved nothing at all), so
                    # turn the page with the key the app binds for exactly that
                    self.key("Next")
                    time.sleep(0.3)
                else:
                    self.wheel(-3, img.width // 2,
                               body_top + (img.height - body_top) // 2)
                    time.sleep(0.15)
            else:
                rec["error"] = "row never appeared"
        elif (pairs := _form_pairs(text)) and re.search(r"\bGO\b", text, re.I):
            # parse the `Label = value` pairs instead of the sentence around them: OCR
            # dropped the leading "f" of "fill" and read "Region" as "Reaion", and the old
            # "fill ... then press GO" pattern threw the whole task away over that - the
            # field label is now matched against the body, which is where it has to be found
            act = "fill_form"
            rec["want"] = pairs
            for field, value in pairs:
                lab = (self.find(body, field, 0.9) or self.find(body, field, 0.68))
                if not lab:
                    rec["error"] = "field %s not found" % field
                    break
                bx, by, bw, bh = lab["box"]
                if self.keys:
                    # A filled field keeps the focus for as long as it exists, and a text
                    # field that holds the focus swallows every key but Return (typing into
                    # a field must not fire shortcuts) - so the next field's hint key never
                    # reaches the app and the next value is typed into the *previous* field.
                    # Tab walks the focus out of the entry first; the hint key then focuses
                    # this field, and Escape clears it - including the stray hint character
                    # the key itself left behind when it landed on a focused entry.
                    self.key("Tab")
                    if not self.press_hint(rec, body, lab["box"], "field " + field,
                                       expect=field):
                        rec["error"] = "no key hint for field %s" % field
                        break
                    self.key("Escape")                 # never append to a stale value
                    time.sleep(0.12)                   # the clear must land before the text
                    # the hint key that focuses this field can also drop its own character
                    # into it (measured: Account held "iGamma"); Tk's own BackSpace binding
                    # removes it without depending on the app's keymap
                    self.key("BackSpace", 12)
                    time.sleep(0.1)
                else:
                    x, y = self.screen((bx + bw + 70, by + bh // 2))
                    self.click(x, y)
                self.type_text(value)
                if self.keys:
                    # Posting characters is not the same as the field holding them: the
                    # posted Escape and the posted characters can be ordered by different
                    # queues, and a clear that arrives *after* the first character eats it
                    # (measured: "MLWI" landed as "LWI"). Read the field back and retype
                    # once when it does not show the value.
                    got = self.entry_text(self.shot(), lab["box"])
                    reads = [[field, got]]
                    if not _same_text(got, value):
                        # Posting characters is not the same as the field holding them, and
                        # a read-back can differ for two opposite reasons: the text really is
                        # wrong (a clear that landed after the first character ate it -
                        # measured: "MLWI" arrived as "LWI"), or the read itself is off (a
                        # single glyph in front of the value - measured "iGamma" for
                        # "Gamma"). Correcting the second case by editing the field made
                        # things strictly worse (measured 7/14 vs 13/14 with Home+Delete, it
                        # removed real characters: "IKilo" -> "lilo", "1151" -> "51"), so the
                        # only correction here is a hard re-clear and one retype.
                        self.key("Escape")
                        time.sleep(0.15)
                        self.key("BackSpace", 12)
                        time.sleep(0.12)
                        self.type_text(value)
                        time.sleep(0.2)
                        reads.append([field, self.entry_text(self.shot(), lab["box"]),
                                      "retyped"])
                    rec.setdefault("field_read", []).append(reads)
            if self.keys:
                self.key("Return")
                rec["go_by"] = "Return"
            else:
                go = self.find(body, "GO", 0.9)
                if go:
                    x, y = self.screen(go["center"])
                    self.click(x, y)
                else:
                    rec["error"] = "GO not found"
        elif (m := re.search(r"set (\w+) (ON|OFF) and the slider to (\d+)", text, re.I)):
            act = "toggle_set"
            name, mode, want = m.group(1), m.group(2).upper(), int(m.group(3))
            rec["want"] = [name, mode, want]
            strip = lambda im: im.crop((0, 0, im.width, body_top))     # noqa: E731
            ref = strip(img)

            def finished(im) -> bool:
                return G.diff_frac(ref, strip(im)) > 0.006             # app said DONE

            if self.keys:
                # slider: the app steps exactly one unit per left/right press, so the
                # count is the whole problem - read the value, then press the rest
                readout = None
                for line in G.group_lines(body):
                    if re.match(r"^\s*value\s*\d+", line["text"], re.I):
                        readout = line
                if not readout:
                    rec["error"] = "slider readout not found"
                else:
                    rx, ry, rw, rh = readout["box"]
                    box = (rx, ry, rw + 60, rh)
                    cur = self.read_value(img, box)
                    rec["slider_start"] = cur
                    if cur is None:
                        rec["error"] = "slider value unreadable"
                    elif cur != want:
                        rec["slider_try"] = [[1, cur]]
                        self.key("Right" if want > cur else "Left", abs(want - cur))
                        time.sleep(0.2)
                        img = self.shot()
                        rec["slider_end"] = self.read_value(img, box)
                if not finished(img):
                    lab = self.find(body, name, 0.9)
                    if not lab:
                        rec["error"] = "switch %s not found" % name
                    else:
                        self.press_hint(rec, body, lab["box"], "switch " + name,
                                    expect=name)
                rec["act"] = act
                rec["ms"] = round((time.perf_counter() - t0) * 1000, 1)
                return rec

            # --- slider. Measured behaviour (thanks to a user watching the screen): a click
            # in the trough does NOT jump to that position - it steps the value by one unit
            # *toward* the click, and a click outside the widget does nothing. So never guess
            # an absolute x: read the current value and step relatively from the end that
            # lies on the wanted side. One actor run carries all the clicks.
            readout = None
            for line in G.group_lines(body):
                if re.match(r"^\s*value\s*\d+", line["text"], re.I):
                    readout = line
            if not readout:
                rec["error"] = "slider readout not found"
            else:
                rx, ry, rw, rh = readout["box"]
                box = (rx, ry, rw + 60, rh)                  # wide enough for "value 10"
                ty = ry - 38                                 # inside the trough (measured)
                lo, hi = rx + 6, rx + 400                    # measured: rx+400 reaches 12,
                                                             # rx+/-20 sits at 0
                cur = self.read_value(img, box)
                rec["slider_start"] = cur

                def slider_step(off, times):
                    x, y = self.screen((off, ty))
                    self.click_many(x, y, times)

                for round_ in range(3):
                    if rec.get("done_by_slider") or cur is None or cur == want:
                        break
                    slider_step(hi if want > cur else lo, abs(want - cur))
                    time.sleep(0.12)
                    img = self.shot()
                    if finished(img):
                        rec["done_by_slider"] = True
                        break
                    cur = self.read_value(img, box)
                    rec.setdefault("slider_try", []).append([round_ + 1, cur])

            # --- switch. The box starts in a random state, so a blind click can *break* an
            # already-correct switch. One click, then a shifted retry if the tick did not
            # move; the app's own status line is the completion signal.
            if not rec.get("done_by_slider") and not finished(img):
                lab = self.find(body, name, 0.9)
                if not lab:
                    rec["error"] = "switch %s not found" % name
                else:
                    bx, by, bw, bh = lab["box"]
                    cy = by + bh // 2
                    mark = (max(0, bx - 40), max(0, cy - 14), 42, 28)
                    prev = img.crop((mark[0], mark[1], mark[0] + mark[2],
                                     mark[1] + mark[3]))
                    for attempt, dx in enumerate((-14, -24), start=1):
                        x, y = self.screen((bx + dx, cy))
                        self.click(x, y)
                        time.sleep(0.2)
                        img = self.shot()
                        rec["switch_click"] = attempt
                        rec["switch_dx"] = dx
                        if finished(img):
                            break
                        now = img.crop((mark[0], mark[1], mark[0] + mark[2],
                                        mark[1] + mark[3]))
                        if G.diff_frac(prev, now) > 0.02:
                            break                            # the tick moved - we hit it
                        prev = now
        elif (m := re.search(r"menu\s+(\S+)\s*>\s*(.+)$", text, re.I)):
            # anchored on "menu <A> > <B>" rather than "invoke the menu ...": OCR dropped
            # the leading "i" and the whole task fell through as unparseable (act unknown)
            act = "menu_invoke"
            menu, item = m.group(1).strip(), m.group(2).strip()
            rec["want"] = [menu, item]
            my0, my1 = self.menu_band(img)
            # the ask itself names the menu, so the strip to search is everything above the
            # ask on the banner - a heuristic band is not needed and was wrong anyway (a
            # dark title bar above the client area put it at y=0..6)
            hi = int(ask_box[1]) - 4 if ask_box else 40
            if my1 - my0 < 8 or my1 > hi:
                my0, my1 = 0, max(12, hi)
            rec["menubar"] = [my0, my1]
            # psm 11 (sparse text) hallucinates a leading glyph on a menubar row
            # ("LUMEN" -> "BLUMEN"); psm 7 reads the same row cleanly
            mwords = self.words(img, region=(0, my0, img.width, my1 - my0), psm="7",
                                min_conf=25.0)
            hit = self.find(mwords, menu, 0.85)
            if not hit:
                rec["band_words"] = [w_["text"] for w_ in mwords][:10]
                rec["top_words"] = [w_["text"] for w_ in (top or [])][:12]
            if self.keys:
                # The menu's own key opens it, and the app echoes the menu it opened - name
                # plus every item key - on the key line at the bottom of the window. That
                # line is on screen, so the menubar strip does not have to be readable at
                # all: press an unknown menu key, read what opened, and back out if it was
                # the wrong one. (The menubar itself is missing from the captured client
                # area, which is why this path may not rely on seeing it.)
                cands: list[str] = []
                if hit and (h0 := self.hint_near(mwords, hit["box"])):
                    cands = [h0]
                else:
                    cands = list("1234")
                for k in cands:
                    self.key(k)
                    time.sleep(0.25)
                    img2 = self.shot()
                    bar = self.keyline(img2)
                    line = " ".join(w_["text"] for w_ in bar)
                    rec.setdefault("menu_probe", []).append([k, line[:90]])
                    # match the *echoed menu name*, not the whole line: an item can carry
                    # the wanted word as its own name ("EMBER: [1] Raven" while the task
                    # asked for the menu RAVEN), and a substring test on the line accepted
                    # exactly that and then hunted for the item in the wrong menu
                    mm = re.search(r"menu\s+([A-Za-z0-9][A-Za-z0-9 ]*)", line)
                    got = G.norm(mm.group(1)) if mm else ""
                    if G.norm(menu) not in got:
                        self.key("Escape")       # wrong menu: close it and try the next key
                        continue
                    rec["menu_key"] = k
                    rec["keybar"] = line[:120]
                    # A 1x read of this dense line is not trustworthy: measured, it turned
                    # "[2] Cobalt" into "[1] Cobalt" and the driver pressed the key of the
                    # *other* item - the app invoked it and scored the task wrong. Read the
                    # same strip at three magnifications (2x/3x have recovered every other
                    # misread in this harness: slot codes, row hints) and act only on a
                    # hint that two reads support, or the single hint anyone read.
                    reads: list = []
                    for sc in (2, 3, 1):
                        bar_sc = bar if sc == 1 else self.keyline(img2, scale=sc)
                        hh = self.hint_of(bar_sc, item)
                        if hh:
                            reads.append([sc, hh])
                    rec["item_hint_reads"] = reads
                    votes: dict = {}
                    for _sc, hh in reads:
                        votes[hh] = votes.get(hh, 0) + 1
                    item_hint = None
                    if votes:
                        best = max(votes.items(), key=lambda kv: kv[1])
                        if best[1] >= 2 or len(votes) == 1:
                            item_hint = best[0]
                    if item_hint:
                        rec["item_key"] = item_hint
                        self.key(item_hint)
                    else:
                        rec["error"] = "item %s hint unstable (%s)" % (item, reads)
                        self.key("Escape")
                    break
                else:
                    rec["error"] = "no menu key opened %s" % menu
            elif not hit:
                rec["error"] = "menu %s not in the menubar band %s" % (menu, [my0, my1])
            else:
                hx, hy = self.screen(hit["center"])
                self.click(hx, hy)
                time.sleep(0.4)
                after = self.shot(front=False)      # fronting would dismiss the menu
                # whatever changed between the two window shots *is* the drop-down:
                # its bounding box tells us where the item labels can possibly be,
                # which keeps the ask line (which names the item too) out of play
                popup = self.changed_box(img, after)
                rec["dropdown_box"] = list(popup) if popup else None
                if not popup:
                    rec["error"] = "no drop-down appeared under the menubar label"
                else:
                    px, py, pw, ph = popup
                    sx, sy = self.screen((px, py))
                    box = (sx, sy, sx + pw, sy + ph)
                    img3, ox, oy = self.shot_screen((max(box[0] - 40, 0), max(box[1] - 10, 0),
                                                     box[2] + 120, box[3] + 60))
                    keep, tries = [], []
                    for scale in (1, 2):
                        im2 = img3 if scale == 1 else img3.resize(
                            (img3.width * scale, img3.height * scale))
                        for psm in ("11", "6"):
                            for w_ in G.ocr_words(im2, psm=psm, min_conf=22.0):
                                bx, by, bw, bh = w_["box"]
                                cx, cy = ox + (bx + bw / 2) / scale, oy + (by + bh / 2) / scale
                                if not (box[0] <= cx <= box[2] and box[1] <= cy <= box[3]):
                                    continue
                                w_ = dict(w_, box=(bx / scale, by / scale, bw / scale,
                                                   bh / scale), center=(cx, cy))
                                if not any(k["text"] == w_["text"] for k in keep):
                                    keep.append(w_)
                        tries.append("s%d:%d" % (scale, len(keep)))
                        if keep:
                            break
                    self.stats["ocr"] += 2
                    rec["popup_words"] = [w_["text"] for w_ in keep][:10]
                    rec["popup_tries"] = tries
                    cands = G.find_text(keep, item, 0.85) or G.find_text(keep, item, 0.72)
                    if cands:
                        ibx, iby, ibw, ibh = cands[0]["box"]
                        rec["item_box"] = [ibx, iby, ibw, ibh]
                        self.click(ox + ibx + ibw // 2, oy + iby + ibh // 2)
                    else:
                        rec["error"] = "menu item %s not in the drop-down" % item
                    # never leave a posted menu behind: it keeps covering the banner
                    # (and therefore the next task's ask line)
                    self.key("Escape")
        elif (m := re.search(r"drag chip (\d+) into slot (\w+)", text, re.I)):
            act = "drag_chip"
            chip, slot = int(m.group(1)), m.group(2)
            rec["want"] = [chip, slot]
            blobs = self.chip_blobs(img, body_top)
            rec["chips"] = [[b["value"], list(b["center"])] for b in blobs]
            src = next((b["center"] for b in blobs if b["value"] == chip), None)
            if src is None:
                # a disc whose digits the blob pass misread: re-read each one at 4x
                for b in blobs:
                    got = re.sub(r"\D", "", self.reread(img, b["box"],
                                                        whitelist="0123456789", psm="10"))
                    if got and int(got) == chip:
                        src = b["center"]
                        break
            # slot labels are ~13 px tall: read the body at 2x or most of them are
            # simply invisible to tesseract (measured: 1 of 3 labels at 1:1)
            words2 = self.body_words(img, body_top)
            want = _code(slot)
            dst, seen, codes = None, [], []
            slot_keys: list[str] = []
            slot_tokens: list[tuple] = []
            hd_line: str | None = None
            for line in G.group_lines(words2):
                ws = line["items"]
                for i, w_ in enumerate(ws):
                    kind, rest = _slot_split(_code(w_["text"]))
                    here = rest if kind == "slot" else ""
                    if kind == "slot":
                        nxt = ws[i + 1]["text"] if i + 1 < len(ws) else ""
                        seen.append([w_["box"], [w_["text"], nxt]])
                        slot_tokens.append(tuple(w_["box"]))
                        if not here:
                            # the code often comes back as its own token right after the
                            # label word ("SLOT" + "OQ9") while a merged read arrives as
                            # one glued token ("SLOTMVI"), which _slot_split already took
                            # apart. Take the neighbour as a candidate either way.
                            cand = _code(nxt)
                            here = cand if 2 <= len(cand) <= 4 else ""
                        if here:
                            codes.append(here)
                        hk = _hint_before(ws, i)
                        if hk:
                            slot_keys.append(hk)
                    # the code is the anchor, not the "SLOT" prefix: the prefix is
                    # what OCR loses ("LOT"), and when the two come back merged
                    # ("SLOT1UG") _slot_split already split the code out
                    if here and here == want:
                        dst = w_
                        # the slot's own key hint is on this same label line
                        # ("[2] SLOT 8B1"); take it here instead of "nearest hint",
                        # which can grab a chip's hint printed below a nearby disc
                        hd_line = _hint_before(ws, i)
                        break
                if dst:
                    break
            rec["slot_seen"] = seen
            rec["slot_codes"] = codes
            if not dst:
                # last resort: the wanted code is on screen but the body pass mangled it
                # (15 px capitals), so re-read every code-shaped token at 4x
                alnum = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                cand = [w_ for ln in G.group_lines(words2) for w_ in ln["items"]
                        if 2 <= len(_code(w_["text"])) <= 4]
                for w_ in cand:
                    got = _code(self.reread(img, w_["box"], whitelist=alnum))
                    rec.setdefault("slot_reread", []).append([w_["text"], got])
                    if got == want:
                        dst = {"box": w_["box"], "text": got}
                        break
            if not dst and slot_tokens:
                # The 2x body pass can garble a label past recognition - one measured
                # task read "[5] SLOT 5RU" as "SLOTIBERIGT [5] VOH", so the code the ask
                # names was nowhere in the word list while it sat in plain sight. The
                # label is one 18 pt canvas item, so re-read the slice *right of* the
                # "SLOT" word at 4x. Reading a whole OCR line instead does not work:
                # two labels often share a line, and their union box reads as one
                # mangled label ("5 SLOTERRLCT VOH").
                alnum = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                by_tok: list[str] = []
                for bx, by, bw, bh in slot_tokens:
                    got = self.reread(img, (max(0, bx - 4), max(0, by - 4), bw + 120, bh + 8),
                                      whitelist=alnum, psm="7")
                    by_tok.append(got)
                    # the slice comes back as one glued run ("SLOTOQ9", measured), so a
                    # `{2,5}` token regex finds nothing at all: strip the label word and
                    # compare what is left. One stray character may trail the code (the
                    # next label's first letter); a *different* slot's code can never be
                    # our code plus noise, because every code is exactly three characters.
                    hit = None
                    for t in re.findall(r"[A-Za-z0-9]{2,9}", got or ""):
                        k2, rest2 = _slot_split(_code(t))
                        cand = rest2 if k2 == "slot" else _code(t)
                        if cand == want or (cand.startswith(want) and len(cand) <= len(want) + 1):
                            hit = cand
                            break
                    if hit:
                        dst = {"box": (max(0, bx - 4), max(0, by - 4), bw + 120, bh + 8),
                               "text": hit}
                        # the slot's own hint is the "[k]" printed left of "SLOT"
                        if not hd_line:
                            hd_line = _hint1(self.reread(
                                img, (max(0, bx - 46), max(0, by - 4), 50, bh + 8),
                                whitelist=HINT_KEYS, psm="7"))
                        break
                rec["slot_line_reread"] = by_tok
            if dst and not hd_line:
                # the "[k]" in front of the code sits in the same 18 pt canvas item as
                # "SLOT", and at 2x the body pass drops it often enough to matter
                # (measured: "SLOT 5RU" with no hint, which left a chip in hand and
                # no key to drop it with - the task could not be answered at all).
                # Re-read just that slice at 4x, the trick that recovered the chip
                # numbers printed in the middle of a disc. The whitelist is the digit
                # alphabet so the letters of "SLOT" cannot be mistaken for the hint.
                bx, by, bw, bh = dst["box"]
                got = self.reread(img, (max(0, bx - 70), by - 4, 78, bh + 8),
                                  whitelist=HINT_KEYS, psm="7")
                rec["slot_hint_reread"] = got
                hd_line = _hint1(got)
            if not dst:
                rec["slot_words"] = [w_["text"] for w_ in words2]
            rec["located"] = [bool(src), bool(dst)]
            sbox = dst["box"] if dst else None
            if sbox:
                rec["slot_box"] = list(sbox)
            if self.keys:
                # Two invariants make this channel safe, and both were learned the
                # hard way:
                #
                #  A. the app arms the slot keys first and the chip keys after them
                #     (`_bind_key(i)` per slot, then `_bind_key(len(slots) + i)` per
                #     chip), so a chip key is never below SCAN_KEYS[len(slots)] - and
                #     each slot's "[k]" hint sits on its own label, which tells us
                #     that boundary from the screen alone.
                #  B. dropping *is* the answer: `drop_slot` calls finish() the moment
                #     a chip is in hand, so a slot key pressed while the wrong disc is
                #     held answers the task wrongly. A slot key is therefore pressed
                #     exactly once, and only after the key line says the wanted chip
                #     is in hand. Walking from "1" (which this used to do) spends the
                #     task on the first slot key it meets if a disc is still held
                #     from an earlier attempt - that is what produced the three
                #     "chip 46 into slot VE0" verdicts of the 12-task run.
                hd = hd_line or (self.hint_near(words2, sbox, max_dx=120) if sbox else None)
                n_slots = 0
                for hk in slot_keys:
                    if hk in SCAN_KEYS:
                        n_slots = max(n_slots, SCAN_KEYS.index(hk) + 1)
                bb = next((b for b in blobs if b["value"] == chip), None)
                guess = None
                if bb:
                    bxx, byy, bww, bhh = bb["box"]
                    guess = _hint1(self.reread(img, (bxx + bww // 2 - 26, byy + bhh + 2, 52, 30),
                                               whitelist=HINT_KEYS, psm="10"))
                start = n_slots
                if guess and guess in SCAN_KEYS:
                    start = max(start, SCAN_KEYS.index(guess))

                def echo(settle: float = 0.0) -> str:
                    """The app's key line. It *replaces* its text on every press."""
                    if settle:
                        time.sleep(settle)
                    return " ".join(w_["text"] for w_ in self.keyline(self.shot()))

                def parse(text: str) -> tuple[str, int | None]:
                    """(kind, chip) with kind ∈ carry | empty | other.

                    Matched against the comparison form, which has no spaces left in
                    it - "carrying chip 84 - now press a slot key" arrives as
                    "carryingchip84nowpressaslotkey", so the pattern may not contain
                    literal spaces.
                    """
                    nt = G.norm(text)
                    mc = re.search(r"carryingchip\s*(\d+)", nt)
                    if mc:
                        return "carry", int(mc.group(1))
                    if "pressachipkeyfirst" in nt:
                        return "empty", None
                    return "other", None

                line = echo()
                if not n_slots and parse(line)[0] == "carry":
                    # no boundary read off the screen *and* a disc already in hand:
                    # the first key of a walk from 0 could be a slot key, which would
                    # answer the task with the wrong disc. Refuse instead of guessing.
                    rec["error"] = "slot keys unknown while a chip is in hand"
                    hs = None
                else:
                    scan: list[list] = []
                    hs = None
                    t_task = self.state().get("task_i")
                    for k in SCAN_KEYS[start:start + 10]:
                        self.key(k)
                        line = echo(0.3)
                        kind, held = parse(line)
                        # an unbound key never touches the key line (the dispatcher
                        # returns before echoing) and a frame grabbed mid-repaint reads
                        # like "eee es sss": both look like "nothing happened", so
                        # re-read before believing either
                        for _ in range(2):
                            if kind != "other":
                                break
                            line = echo(0.25)
                            kind, held = parse(line)
                        st_now = self.state()
                        scan.append([k, line[:50], st_now.get("task_i"), st_now.get("result")])
                        if st_now.get("task_i") != t_task:
                            rec["chip_aborted"] = "the app moved on to task %s" % st_now.get("task_i")
                            break
                        if kind == "other":
                            rec.setdefault("chip_silent", []).append(k)
                            break          # past the last armed key: stop, never guess
                        if kind == "carry" and held == chip:
                            hs = k
                            break
                        # "carry" with another disc, or a slot key with an empty hand:
                        # both are harmless and the walk keeps going up
                    rec["chip_scan"] = scan
                    rec["chip_guess"] = guess
                    rec["slot_keys"] = slot_keys
                rec["keys"] = [["chip " + str(chip), hs], ["slot " + slot, hd]]
                if hs and hd:
                    self.key(hd)                    # the wanted chip is in hand: drop it
                elif not hs:
                    rec.setdefault("error", "no key picks up chip %s" % chip)
                else:
                    rec.setdefault("error", "no key hint for slot %s" % slot)
            elif src and dst:
                bx, by, bw, bh = dst["box"]
                x0, y0 = self.screen(src)
                x1, y1 = self.screen((bx + bw // 2, by + bh + 26))   # inside the frame
                rec["src"], rec["dst"] = [x0, y0], [x1, y1]
                self.drag(x0, y0, x1, y1)
            else:
                rec["error"] = "chip %s or slot %s not located" % (chip, slot)
        if act == "unknown":
            # An unparsed ask is the one case where the words' geometry explains what OCR
            # did to the sentence (measured: the "=" glyphs of a form ask showed up after
            # the last field), so keep it - nowhere else is the raw band worth the bytes.
            rec["ask_words"] = [[w_["text"], list(w_["box"])] for w_ in (band or [])][:40]
            # An ask the driver cannot turn into an action must still end in a *decision*:
            # doing nothing freezes the task (the target never advances) and the run's
            # early-stop guard then throws away everything after it (measured: 3 empty
            # attempts at #54 stopped a 85-task batch at 57).  Refusing is the honest
            # statement of "I cannot tell what to do here" - it is scored, and on a
            # must_refuse task it is even the right answer.
            rec["ask_unparsed"] = 1
            self.refuse(rec, "the ask does not parse into an action")
        rec["act"] = act
        rec["ms"] = round((time.perf_counter() - t0) * 1000, 1)
        # v1 accounting (design §1): the decision is what the driver *chose* to do, the
        # result is what the target scored.  Keeping both is what makes false_refusal
        # and false_accept measurable at all - the v0 gate had only "an answer exists".
        rec["presses"] = int(rec.get("presses") or 0) + max(0, int(self.stats.get("clicks", 0) or 0) - clicks0)
        rec.setdefault("interferences", 0)
        if not rec.get("decision"):
            rec["decision"] = "acted" if (rec.get("presses") or rec.get("hints")) else "none"
        rec["wasted_actions"] = max(0, int(rec.get("presses") or 0) - 1)
        # A press that was abandoned because the frame under it had already changed: the
        # count of times the driver noticed the world move, per task (design §1.2 `stale`).
        # `press_hint` may already have counted a frame that outlived its task, so add.
        rec["stale_actions"] = int(rec.get("stale_actions") or 0) + len(rec.get("hint_stale") or [])
        return rec

    def read_slider(self, img, body_top):
        lines = G.group_lines(self.words(img, region=(0, body_top, img.width,
                                                      img.height - body_top)))
        for line in lines:
            m = re.match(r"^\s*value\s*(\d+)", line["text"], re.I)
            if m:
                return int(m.group(1))
        return None

    def read_value(self, img, box):
        """Read the slider readout ("value N") - targeted, no full-body OCR.

        The box must be wide enough for two digits: a tight box around "value 3" clips
        the "0" of "value 10" and silently turns 10 into 1.
        """
        txt, conf = self._timed("ms_ocr", G.read_box, img, box,
                                whitelist="0123456789", psm="7", scale=3)
        self.stats["ocr"] += 1
        digits = re.sub(r"\D+", "", txt or "")
        return int(digits) if digits else None

    def keyline(self, img, h=60, scale=1) -> list[dict]:
        """Words of the window's bottom strip - the line the app talks back on.

        The app announces what it just did there ("menu EMBER: [1] Xenon ...",
        "carrying chip 51 - now press a slot key"), which is what lets a driver verify
        an action instead of assuming it landed. `scale` magnifies the strip before OCR:
        at 1x a dense echo line loses items and misreads hint digits.
        """
        return self.words(img, region=(0, img.height - h, img.width, h), psm="7",
                          min_conf=20.0, scale=scale)

    def reread(self, img, box, whitelist=None, psm="7", scale=4) -> str:
        """Re-read one small word box at high magnification.

        Whole-body OCR at 2x reads 13 px capitals wrong often enough to lose a task
        (measured: the slot code "GSD" came back as "csp"); the same box cropped tight
        and blown up 4x reads correctly. Cheap enough to use as a second opinion.
        """
        x, y, w, h = box
        pad = 3
        text, _ = self._timed("ms_ocr", G.read_box, img,
                              (max(x - pad, 0), max(y - pad, 0), w + 2 * pad, h + 2 * pad),
                              whitelist=whitelist, psm=psm, scale=scale)
        return (text or "").strip()

    def entry_text(self, img, lab_box) -> str:
        """What a form field currently shows, read off the screen.

        The entry sits to the right of its label, and "the characters were posted" is a
        different claim from "the field holds the value" - measured, the first character
        of the last field went missing ("MLWI" landed as "LWI").
        """
        bx, by, bw, bh = lab_box
        box = (max(bx + bw + 8, 0), max(by - 6, 0), 320, bh + 12)
        txt, _ = self._timed("ms_ocr", G.read_box, img, box,
                             whitelist=LETTERS + DIGITS, psm="7", scale=3)
        self.stats["ocr"] += 1
        return (txt or "").strip()

    def ink_aspect(self, img, box) -> float | None:
        """Width over height of the ink inside a box, whatever the polarity.

        Works for light-on-dark (the banner) and dark-on-light (a field) alike: the
        minority class inside a tight box around one glyph is the glyph. Compared
        against the same character rendered in the app's font this is what tells a
        digit zero from a letter O (0.7 against 1.0 in Segoe UI bold).
        """
        x, y, w, h = box
        if w < 3 or h < 3:
            return None
        a = np.asarray(img.crop((int(x), int(y), int(x + w), int(y + h))).convert("L"),
                       dtype=np.uint8)
        light = a > 128
        ink = light if light.mean() < 0.5 else ~light
        ys, xs = np.nonzero(ink)
        if len(xs) == 0:
            return None
        return float(xs.max() - xs.min() + 1) / max(1, int(ys.max() - ys.min() + 1))

    def glyph_read(self, img, box, text, rec: dict | None = None) -> str:
        """Re-read one code-shaped token glyph by glyph and settle look-alike characters.

        MEASURED DEAD END - kept because the negative result is the useful part. A code
        is compared string-exactly by the app, and the word-level banner read confuses
        0/O (measured: the app's `C02S` read as `CO2S`, task judged WRONG with the field
        filled in perfectly). tesseract's `makebox` pass read the digit right when it
        looked at the *whole banner*, but on a tight word box at 3x it returned
        "Cco2SSs" for "CO2S", and deciding a character by its ink aspect against the
        same character rendered in the app's font (Segoe UI bold, `_proto_aspect`)
        flipped correct glyphs: `B` measured 0.50 against a prototype 0.76 and became
        `8`, `2` measured 0.80 against 0.63 and became `Z`. Wiring this in cost 3 tasks
        (13/14 -> 10/14 on t_form), so the driver keeps the word pass and the exact
        comparison is left to fail honestly instead.
        """
        if not CODEISH.match(text or "") or not any(c in GLYPH_FAMILY for c in text):
            return text
        x, y, w, h = box
        pad = 2
        crop = img.crop((max(0, int(x - pad)), max(0, int(y - pad)),
                         int(x + w + pad), int(y + h + pad)))
        up = 3                                   # 26 px bold glyphs: 3x is plenty
        big = crop.resize((crop.width * up, crop.height * up), Image.LANCZOS)
        raw = self._timed("ms_ocr", G.char_boxes, big, whitelist=LETTERS + DIGITS + "Il")
        self.stats["ocr"] += 1
        glyphs = [{"text": g["text"],
                   "box": (g["box"][0] / up + x - pad, g["box"][1] / up + y - pad,
                           g["box"][2] / up, g["box"][3] / up)}
                  for g in raw if g["text"].strip()]
        got = "".join(g["text"] for g in glyphs)
        # Only trust this pass when it sees the same token: a stray border artifact reads
        # as a character too, and a shifted box would decide the wrong positions.
        if len(glyphs) != len(text) or _fold_family(got.upper()) != _fold_family(text):
            if rec is not None:
                rec.setdefault("glyph_read", []).append([text, got, "kept (glyph pass differs)"])
            return text
        upper = sum(c.isupper() for c in text) >= sum(c.islower() for c in text)
        out = list(text)
        notes = []
        for i, ch in enumerate(text):
            fam = GLYPH_FAMILY.get(ch)
            if not fam:
                continue
            ar = self.ink_aspect(img, glyphs[i]["box"])
            if ar is None:
                continue
            ranked = sorted(((abs(np.log(ar / pa)), c) for c, pa in
                             ((c, _proto_aspect(c)) for c in fam) if pa > 0))
            if len(ranked) < 2 or ranked[0][1] == ch:
                continue
            margin = ranked[1][0] - ranked[0][0]
            if margin < 0.12:                    # too close to overrule the word pass
                continue
            pick = ranked[0][1]
            pick = pick if pick.isdigit() else (pick.upper() if upper else pick.lower())
            out[i] = pick
            notes.append("%d:%s->%s(ar=%.2f)" % (i, ch, pick, ar))
        fixed = "".join(out)
        if rec is not None and fixed != text:
            rec.setdefault("glyph_read", []).append([text, fixed, " ".join(notes)])
        return fixed

    def chip_blobs(self, img, body_top) -> list[dict]:
        """Coloured chips and the number printed inside each one.

        The digits are white on a saturated disc, so binarise on luminance and keep
        only the disc (the bbox corners show the pale canvas, which would otherwise
        come out as big black blobs). Inverting the colour crop - the obvious first
        try - read 1 of 3 chips.
        """
        body = img.crop((0, body_top, img.width, img.height))
        a = np.asarray(body).astype(np.int16)
        sat = (a.max(axis=2) - a.min(axis=2)) > 70
        out = []
        for area, (y0, x0, y1, x1) in G.components(sat, min_area=1200):
            if (x1 - x0) < 30 or (y1 - y0) < 30:
                continue
            w, h = x1 - x0 + 1, y1 - y0 + 1
            g = np.asarray(body.crop((x0, y0, x1 + 1, y1 + 1)).convert("L"))
            yy, xx = np.mgrid[0:h, 0:w]
            disc = (((yy - (h - 1) / 2.0) ** 2 + (xx - (w - 1) / 2.0) ** 2)
                    < (0.47 * min(h, w)) ** 2)
            bw = Image.fromarray(np.where((g > 185) & disc, 0, 255).astype(np.uint8))
            digits, txt = "", ""
            for psm in ("7", "10"):
                txt, _ = self._timed("ms_ocr", G.read_box, bw, (0, 0, w, h),
                                     whitelist="0123456789", psm=psm, scale=3)
                digits = re.sub(r"\D", "", txt)
                if digits:
                    break
            out.append({"center": ((x0 + x1) // 2, body_top + (y0 + y1) // 2),
                        "box": (x0, body_top + y0, w, h),
                        "value": int(digits) if digits else None, "text": txt,
                        "area": area})
        return out


def target_pids(state_path: str) -> list[int]:
    """PIDs of practice targets that own this state file (never our own process).

    Match on the state file *name*: a target started by hand is launched with a
    relative path, so its command line never contains the absolute one - and a
    process query that only knows the absolute path silently finds nothing (measured:
    stale targets piled up run after run because of exactly that, and two apps on one
    state file then answered each other's tasks).
    """
    ps = ("Get-CimInstance Win32_Process -Filter \"Name like '%%python%%'\" | "
          "Where-Object { $_.CommandLine -like '*gym_app.py*' -and "
          "$_.CommandLine -like '*%s*' } | ForEach-Object { $_.ProcessId }"
          % os.path.basename(state_path).replace("'", ""))
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             universal_newlines=True, timeout=40).stdout or ""
    except Exception:
        return []
    return [int(t) for t in out.split() if t.isdigit() and int(t) != os.getpid()]


def target_windows(a, title: str = "GUI Gym") -> list[dict]:
    """The practice target's top-level windows, found through UIA by title."""
    out: list[dict] = []
    rep = a.run([{"op": "uia", "what": "windows", "max": 120}], results=True)
    for step in rep.get("trace", []):
        # inline first: `data` is folded and the actor's `_slim` cuts a list after a few
        # items (see window_by_title) - the target window can sit past that cut
        for w in (step.get("windows") or (step.get("data") or {}).get("windows") or []):
            # a locked or half-torn-down desktop can answer with bare strings - skip those
            if not isinstance(w, dict):
                continue
            if title.lower() in (w.get("name") or "").lower():
                out.append(w)
    return out


def kill_stale(state_path: str) -> int:
    """Kill practice targets left over from an interrupted run.

    A stale window carries the same title as the fresh one, so the driver attaches to
    the wrong app and spends the run answering the previous run's task - and the state
    file it reads belongs to that older app too.
    """
    n = 0
    for pid in target_pids(state_path):
        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=20)
        n += 1
    return n


LOCK_PROCS = ("logonui.exe", "lockapp.exe")
LOCK_CLASS = "Windows.UI.Core.CoreWindow"
LOCK_TITLES = ("锁定", "锁屏", "lock")


def foreground_info() -> tuple[str | None, str | None, str]:
    """(process name, window class, title) of the window in front, right now.

    Written with ctypes rather than the actor or PowerShell because the one question it
    has to answer - "is this session locked" - must keep working when nothing else does:
    a locked session makes every capture come back empty, and a run started then scores
    a board of failures that say nothing about the driver (measured 2026-10-04: the
    machine locked mid-session and every GUI run had to stop).
    """
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        k = ctypes.windll.kernel32
        hwnd = u.GetForegroundWindow()
        if not hwnd:
            return None, None, ""
        title = ctypes.create_unicode_buffer(512)
        u.GetWindowTextW(hwnd, title, 512)
        cls = ctypes.create_unicode_buffer(256)
        u.GetClassNameW(hwnd, cls, 256)
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        name = None
        # PROCESS_QUERY_LIMITED_INFORMATION: enough for the image name, works on
        # LogonUI/LockApp, which a full-access open would refuse
        h = k.OpenProcess(0x1000, False, pid.value)
        if h:
            path = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            if k.QueryFullProcessImageNameW(h, 0, path, ctypes.byref(size)):
                name = os.path.basename(path.value)
            k.CloseHandle(h)
        return name, cls.value, title.value
    except (AttributeError, OSError):
        return None, None, ""


def lock_reason() -> str | None:
    """None when the session looks usable, else a short reason why it is not.

    Three independent signals, because the lock screen is not one window: the process
    that owns it (`LogonUI.exe` on the secure desktop, `LockApp.exe` on the lock screen
    itself), the class+titles it uses, and the localized title this machine showed -
    measured 2026-10-04: `foreground: Windows 默认锁屏界面`, which is the plain
    "锁屏" wording, not "锁定".
    """
    name, cls, title = foreground_info()
    if name and name.lower() in LOCK_PROCS:
        return "foreground process %s" % name
    low = title.lower()
    if cls == LOCK_CLASS and any(t in low for t in LOCK_TITLES):
        return "lock window %r (class %s)" % (title, cls)
    if "锁屏" in title:
        return "lock screen title %r" % title
    return None


def wait_until_unlocked(timeout: float, poll: float = 5.0, note=print) -> bool:
    """Wait for a lock screen to go away; timeout=0 means "check once, never wait".

    The user's machine locking is normal and expected, so a run must not fail because of
    it: check before starting, pause if it happens mid-run, and say so in the summary
    instead of collecting empty frames as if they were answers.
    """
    reason = lock_reason()
    if reason is None:
        return True
    if timeout <= 0:
        note("gym driver: session is locked (%s) - not waiting (--lock-wait 0)" % reason)
        return False
    note("gym driver: session is locked (%s) - waiting up to %.0f s" % (reason, timeout))
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(poll)
        reason = lock_reason()
        if reason is None:
            note("gym driver: unlocked after %.0f s - continuing" % (time.time() - t0))
            return True
    note("gym driver: still locked after %.0f s (%s) - giving up" % (timeout, reason))
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--press-jitter", default="0,0", metavar="LO,HI",
                    help="batch 6: sleep a random LO..HI ms between the guard's frame "
                         "and the click, for the `swap_race_timer` variant only "
                         "(measures the race that lands after the guard; 0,0 = off)")
    ap.add_argument("--tasks", type=int, default=6)
    ap.add_argument("--scenario", default=None)
    ap.add_argument("--state", default="gym-state.json")
    ap.add_argument("--events", default="gym-events.jsonl")
    ap.add_argument("--no-start", action="store_true", help="do not launch the app")
    ap.add_argument("--json-out", default=None)
    ap.add_argument("--max-repeat", type=int, default=3,
                    help="stop after the same task fails this many times in a row")
    ap.add_argument("--chaos", type=float, default=0.0,
                    help="probability per task that the target changes under the "
                         "driver (forwarded to the app; the driver also switches to "
                         "poll-and-recheck mode)")
    ap.add_argument("--chaos-ms", default=None, help="delay range for that change, e.g. 600,1800")
    ap.add_argument("--chaos-kind", default="any",
                    choices=["any", "rebuild", "move", "popup", "slow"],
                    help="train one kind of change at a time (forwarded to the app)")
    ap.add_argument("--bg", action="store_true",
                    help="background mode: capture the window with PrintWindow and send "
                         "input with PostMessage, so the user's foreground is untouched")
    ap.add_argument("--keys", action="store_true",
                    help="act through the app's keyboard channel ([k] hints printed next "
                         "to every control) instead of mouse messages; combine with --bg "
                         "for training that never touches the user's foreground")
    ap.add_argument("--until-interferences", type=int, default=0, metavar="N",
                    help="keep issuing tasks until N disturbances have actually fired "
                         "(design §4: a planned chaos event often lands after the task "
                         "ended, so tasks are not a unit of measurement)")
    ap.add_argument("--max-tasks", type=int, default=0, metavar="N",
                    help="safety cap for --until-interferences (default: 6x --tasks)")
    ap.add_argument("--lock-wait", type=float, default=3600.0, metavar="SEC",
                    help="if the session is locked, wait up to SEC seconds for it to be "
                         "unlocked before starting and after a mid-run lock (0 = only "
                         "check and refuse)")
    a = ap.parse_args()
    a.chaos = max(0.0, min(1.0, a.chaos))
    if a.until_interferences and not a.chaos_ms:
        # design §4: the app's default 600-1800 ms delay usually lands after a 1.3 s task,
        # so the disturbance never fires (measured: chaos-p0.5.json, 8 tasks, 0 fires)
        a.chaos_ms = "200,700"
        print("gym driver: --until-interferences needs the change to land mid-task; "
              "--chaos-ms defaults to 200,700 for this run")
    here = os.path.dirname(os.path.abspath(__file__))
    state = os.path.join(here, a.state)
    events = os.path.join(here, a.events)
    # STATE.md 7 #14: the app rewrites one state/events pair per start, and score.py joins
    # truth through rep["events"], so a batch could only be scored while it was the last
    # one to run.  Naming the pair after --json-out archives every batch's truth stream
    # next to its own run json (re-scorable later).  Without --json-out the historical
    # defaults stay, so old commands behave exactly as before.
    if a.json_out:
        jp = a.json_out if os.path.isabs(a.json_out) else os.path.join(here, a.json_out)
        stem = os.path.splitext(jp)[0]
        state = stem + "-state.json"
        events = stem + "-events.jsonl"
    py = sys.executable
    proc = None
    # a locked session answers every capture with an empty image, so a run started then
    # measures nothing: wait for the user instead of producing a fake scoreboard
    if not wait_until_unlocked(a.lock_wait):
        print("gym driver: refusing to start a run while the session is locked")
        return 2
    # who the user is with *before* we exist: starting the gym makes it the active
    # window, and the whole point of background mode is to give that back afterwards
    fg_before = foreground_via(Actor())
    app_args: list[str] = []
    if not a.no_start:
        for f in (state, events):
            if os.path.exists(f):
                os.unlink(f)
        n_stale = kill_stale(state)
        if n_stale:
            print("killed %d stale practice target(s) still using this state file"
                  % n_stale)
        cmd = [py, os.path.join(here, "gym_app.py"), "--state", state, "--events", events,
               "--gap", "300"]
        if a.seed is not None:
            cmd += ["--seed", str(a.seed)]
        if a.scenario:
            cmd += ["--scenario", a.scenario]
        if a.chaos:
            cmd += ["--chaos", str(a.chaos)]
            if a.chaos_ms:
                cmd += ["--chaos-ms", a.chaos_ms]
            if a.chaos_kind != "any":
                cmd += ["--chaos-kind", a.chaos_kind]
        if a.bg:
            # in background mode the driver captures the dialog by hwnd, so it must
            # not be pinned above everything the user is doing. The app must NOT be
            # asked to focus itself either: Tk's focus_force() from a background
            # thread kills the focus the driver hands over below, and every key posted
            # after the first task change is then dropped (measured, probe_post_key)
            cmd += ["--no-topmost"]
        app_args = cmd[2:]              # what the target was launched with, for the record
        proc = subprocess.Popen(cmd, cwd=here, stdout=subprocess.DEVNULL,
                                stderr=subprocess.STDOUT)
        time.sleep(2.5)
    # exactly one target must be on screen. Two apps fight over one state file, and the
    # symptom is vicious: the run scores failure after failure while the keys it pressed
    # were provably right (measured - the other app had answered that task first and
    # moved on, so every later press landed in the next task). Count *windows*, not
    # processes: the venv's python.exe is only a launcher that re-runs the app with the
    # runtime interpreter, so a single healthy target is two processes (measured).
    wins = target_windows(Actor(), "GUI Gym")
    if len(wins) != 1:
        print("refusing to drive: %d practice target window(s) on screen - want exactly 1"
              % len(wins))
        if proc is not None:
            subprocess.run(["taskkill", "/F", "/PID", str(proc.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=20)
        return 2
    try:
        jitter = tuple(int(x) for x in str(a.press_jitter).split(","))[:2]
    except ValueError:
        print("--press-jitter wants LO,HI in ms, e.g. 0,1200")
        return 2
    d = Driver(Actor(), state, expect_chaos=bool(a.chaos), bg=bool(a.bg),
               keys=bool(a.keys), jitter=jitter)
    d.window_rect()
    if a.bg:
        # slide the app behind the user's windows once: from here on it is only ever
        # read through PrintWindow and driven through PostMessage
        d.a.run([{"op": "window", "mode": "bottom", "title_contains": d.title}])
        if fg_before.get("hwnd"):
            # hand the foreground back to whoever had it: we are the foreground
            # process at this moment, so Windows lets us activate that window again.
            # Twice, because a window that the driver started itself finishes mapping
            # a moment later and takes the foreground back (measured: the summary then
            # read "foreground after: GUI Gym  unchanged: False").
            for attempt in (0, 1):
                d.a.run([{"op": "window", "mode": "front", "hwnd": fg_before["hwnd"]}])
                time.sleep(0.4)
                now = d.foreground()
                if attempt or not now or now.get("hwnd") == fg_before["hwnd"]:
                    break
    print("gym driver: window %s  actor port %s  chaos %.2f%s%s" %
          ((d.origin[0], d.origin[1], d.origin[0] + d.size[0], d.origin[1] + d.size[1]),
           d.a.port, a.chaos, "  bg" if a.bg else "", "  keys" if a.keys else ""))
    fg0 = d.foreground()
    if fg0:
        print("foreground before: %s (hwnd %s)" % (fg0["title"][:60], fg0["hwnd"]))
    runs = []
    stuck_i, stuck = None, 0
    # Design §4: tasks are not the unit of measurement, *fired* disturbances are.  A
    # planned chaos event often lands after a 1.3 s task has already ended, so a run that
    # asks for 20 tasks and fires nothing measures nothing.  `--until-interferences`
    # keeps issuing tasks until enough disturbances actually fired, with a hard cap.
    max_tasks = a.max_tasks or (a.tasks * 6 if a.until_interferences else a.tasks)
    if a.until_interferences:
        print("gym driver: running until %d fired disturbance(s), max %d task(s)"
              % (a.until_interferences, max_tasks))
    i = 0
    exit_reason = ""
    try:
        while i < max_tasks:
            if lock_reason() is not None:
                # the user locked the machine mid-run: everything captured meanwhile is an
                # empty frame, so pause here rather than score those tasks as failures
                d.stats["lock_waits"] = int(d.stats.get("lock_waits", 0)) + 1
                if not wait_until_unlocked(a.lock_wait):        # design: never guess, wait
                    print("gym driver: session stayed locked - stopping the run", flush=True)
                    break
            t0 = time.time()
            # never start a record on a task that is still being torn down: after a verdict
            # the app clears `result` and rebuilds its body a moment later, and anything
            # read or pressed inside that window belongs to the task we just answered
            # (measured: a whole run one task behind, its first record already on task 8)
            seen, st = None, {}
            for _ in range(8):
                st = d.state()
                ask_now = st.get("ask")
                if st.get("result") in (None, "", "none") and ask_now and ask_now != seen:
                    break
                seen = ask_now
                time.sleep(0.2)
            ask_file, scen, task_i = st.get("ask"), st.get("scenario"), st.get("task_i", -1)
            rec = d.do_task(ask_file)
            # the app resets `result` the moment it moves on, so score from its log.
            # The state file is read only to score and to pick the next task - the
            # app's `truth` is never copied into a record or fed back to the driver
            # (that would be memorising the answer key instead of seeing the screen).
            nxt, v = task_i, {}
            # in key mode a press can land inside the app's 300 ms gap between tasks and
            # simply be swallowed (measured: two tasks stuck at 5.4 s pressing the right
            # key), so a retry that re-reads the screen is worth it there too
            # The retry answers "no verdict arrived while the app is still on this task", which
            # is a property of the act, not of the key channel: a foreground mouse run delivers
            # real clicks, so a swap trap that rewrites the ask after the press leaves exactly
            # that state.  Measured in batch 3: with `tries = 1` the two after-press swap classes
            # spent two rows on one target task (71 rows over 57 tasks), so rows and tasks stopped
            # being 1:1 and the empty first rows were reported as timeouts.
            tries = 3 if (a.chaos or a.keys or not a.bg) else 1
            for attempt in range(tries):
                if rec.get("verify_giveup"):
                    # the target kept changing under the verification (design §6.1): stop
                    # re-reading and let the task be scored as a timeout
                    break
                if a.chaos or rec.get("ask_moved"):
                    # the ask can be re-rolled the moment we acted: the old answer is void,
                    # so look again straight away and redo the task with what is on screen.
                    # Not only under chaos: the swap trap rewrites the ask on its own, and a
                    # plan built on the old question must not be pressed (design §5.2).
                    img_fresh = d.shot()
                    fresh = d.chrome(img_fresh)[0]
                    # ... but only while the app is still on this task: once it has moved on,
                    # the banner belongs to the *next* question and acting on it answers the
                    # wrong one (measured: a rebuilt button task ended up selecting a row
                    # whose id was read off the following task)
                    if d.task_i() != task_i:
                        nxt = d.task_i()
                        break
                    if _ask_key(fresh) != _ask_key(rec.get("ask")):
                        if os.environ.get("GYM_DEBUG_CHAOS"):
                            img_fresh.save(os.path.join(HERE, "replan-%d-%d.png" % (i, attempt)))
                        d.stats["replans"] += 1
                        rec = _redo(d, rec, fresh, "ask re-rolled")
                deadline = time.time() + (4.4 if a.chaos else 3.0)
                while True:
                    v = d.wait_verdict(task_i, 0.6)
                    nxt = d.wait_task(task_i, 0.1)
                    if v.get("result") not in (None, "", "none") or nxt != task_i:
                        break
                    if time.time() >= deadline:
                        break
                    if a.chaos:             # a popup may be what is holding the verdict
                        _, n = d.dismiss_interference()
                        if n:
                            rec["interferences"] = rec.get("interferences", 0) + n
                            # the dialog is gone, but the press it swallowed was never
                            # scored: stop waiting and answer again (replan below)
                            break
                if v.get("result") not in (None, "", "none") or nxt != task_i:
                    break
                if attempt == tries - 1:
                    break
                # no verdict in 4.4 s: the chaos may have rebuilt the control we clicked,
                # so the click landed on nothing - read the screen and act again
                now = d.task_i()
                if now != task_i:
                    nxt = now
                    break                   # it moved on without a verdict: not a rebuild
                d.stats["replans"] += 1
                rec = _redo(d, rec, rec.get("ask") or "", "no verdict arrived")
            v = v if v.get("result") not in (None, "", "none") else d.wait_verdict(task_i, 1.5)
            res = v.get("result") or "none"
            if res != "none":
                # a verdict is not the same thing as a new task: the app rebuilds its body
                # during a 300 ms gap, and anything read inside that window is the question
                # we just answered (measured: three attempts in a row "answered" a task the
                # app had already moved past, all pressing a hint that no longer existed)
                nxt = d.wait_task(task_i, 2.5) or nxt
                time.sleep(0.25)
            det = dict(v.get("detail", {}))
            # Batch 9 (#11): `detail` comes from the app's verdict, so the driver's own jitter
            # delay has to be injected *here* - anything written into `rec["detail"]` earlier is
            # overwritten by this line (measured on batch 6: 5 jitter fires summed 3560 ms in
            # `stats`, but only 3 rows / 2993 ms survived on the record).
            if rec.get("press_delay_ms"):
                det["press_delay_ms"] = int(rec["press_delay_ms"])
            # Batch 10 (debt #4): the window the guard actually read through, per task.  The
            # run-level `stats` count cannot tell a run whose box moved 2 px from one where
            # every read silently fell back to the frozen box.
            if rec.get("ask_box_recomputed"):
                det["ask_box_recomputed"] = int(rec["ask_box_recomputed"])
            if rec.get("ask_box_shift_px"):
                det["ask_box_shift_px"] = list(rec["ask_box_shift_px"])
            rec.update({"i": i, "task_i": task_i, "next_task_i": nxt, "scenario": scen,
                        "result": res, "detail": det, "verdict_ms": v.get("ms"),
                        "wall_ms": round((time.time() - t0) * 1000, 1)})
            runs.append(rec)
            if res != "ok" and os.environ.get("GYM_DEBUG_FAIL"):
                # evidence for the failure: the exact frame the plan was built on, the
                # banner words with their boxes, and the driver's own record
                dark = getattr(d, "last_frame", None)
                stamp = "_fail-%d-%d" % (os.getpid(), i)
                if dark is not None:
                    dark.save(os.path.join(HERE, stamp + ".png"))
                with open(os.path.join(HERE, stamp + ".json"), "w", encoding="utf-8") as fh:
                    json.dump({"ask": rec.get("ask"), "ask_screen": rec.get("ask_screen"),
                               "ask_file": rec.get("ask_file"),
                               "band": getattr(d, "last_band", []),
                               "body": getattr(d, "last_body", []), "rec": rec},
                              fh, ensure_ascii=False, indent=1)
                print("debug dump: %s.json" % stamp, flush=True)
            print("task %2d %-9s %-52s %-5s %6.0fms %s" %
                  (i, scen, (rec.get("ask") or "")[:52], res.upper(), rec["wall_ms"],
                   (" " + json.dumps(rec["detail"], ensure_ascii=False)[:90])
                   if res != "ok" else ""), flush=True)
            if task_i == stuck_i:
                stuck += 1
            else:
                stuck_i, stuck = task_i, 1
            if stuck >= a.max_repeat:
                print("stopping early: task %s failed %d times in a row" % (task_i, stuck),
                      flush=True)
                break
            i += 1
            if a.until_interferences and i >= a.tasks \
                    and d.stats.get("interferences", 0) >= a.until_interferences:
                print("stopping: %d disturbance(s) fired over %d task(s)"
                      % (d.stats.get("interferences", 0), i), flush=True)
                break
    except ShotFailed as e:
        # Batch 11 (debt #17): losing the target mid-run used to end the process through
        # SystemExit, which threw every finished row away (the summary and the run json are
        # straight-line code *after* this loop).  Unwind into the normal tail instead and save
        # what is finished as a partial run json.
        exit_reason = str(e)
    except Exception as e:                              # noqa: BLE001 - keep the rows
        exit_reason = "%s: %s" % (type(e).__name__, e)
    if exit_reason:
        if not runs:
            print("gym driver: %s" % exit_reason, flush=True)
            print("no task finished - nothing to save", flush=True)
            if proc:
                proc.terminate()
            return 1
        print("", flush=True)
        print("PARTIAL RUN: the target was lost after %d finished task(s)" % len(runs),
              flush=True)
        print("  reason: %s" % exit_reason, flush=True)
        print("  the finished rows are saved as a partial run json", flush=True)
    ok = sum(1 for r in runs if r["result"] == "ok")
    # the tail of a run (handing the foreground back, writing the json) has to be able
    # to say whether the session was locked while all this happened: a locked tail means
    # the last tasks were measured through empty frames, which is a caveat on the score
    locked_at_end = lock_reason()
    if locked_at_end or d.stats.get("lock_waits"):
        print("screen: locked at end (%s); paused %d time(s) for the lock screen"
              % (locked_at_end or "no", int(d.stats.get("lock_waits", 0))))
    by: dict = {}
    for r in runs:
        s = by.setdefault(r["scenario"], [0, 0])
        s[1] += 1
        s[0] += 1 if r["result"] == "ok" else 0
    print("\nscore %d/%d ok  (%.0f%% of tasks)" % (ok, len(runs), 100.0 * ok / max(len(runs), 1)))
    for s, (k, n) in sorted(by.items()):
        print("  %-9s %d/%d" % (s, k, n))
    print("per task: %.0f ms avg  |  actor calls %d  shots %d  ocr %d  clicks %d  keys %d  drags %d" %
          (np.mean([r["wall_ms"] for r in runs]), 0, d.stats["shots"], d.stats["ocr"],
           d.stats["clicks"], d.stats["keys"], d.stats["drags"]))
    # not a ratio of tasks: a reloaded task reads the ask again, so the count can exceed
    # the number of tasks (measured: 26 reads over 24 tasks after three swap replans)
    print("asks read off the screen: %d  from the state file: %d  (%d task(s))"
          % (d.stats["asks_from_screen"], d.stats["asks_from_file"], len(runs)))
    fires = int(d.stats.get("interferences", 0))
    if a.chaos or a.until_interferences:
        fired_tasks = sum(1 for r in runs if r.get("interferences"))
        print("disturbances: %d fired over %d task(s), %d task(s) had >=1; "
              "verify calls %d, re-reads %d, give-ups %d, stale %d"
              % (fires, len(runs), fired_tasks, d.stats.get("verify_calls", 0),
                 d.stats.get("verify_rereads", 0), d.stats.get("verify_giveup", 0),
                 d.stats.get("stale_actions", 0)))
    if a.bg and fg_before.get("hwnd"):
        # every posted key needs the gym window focused (SetFocus activates its top-level
        # window), so hand the foreground back before reporting - and report the state
        # that is really there afterwards, not the one that was attempted
        d.a.run([{"op": "window", "mode": "front", "hwnd": fg_before["hwnd"]}])
        time.sleep(0.35)
    fg1 = d.foreground()
    if fg0 and fg1:
        same = fg0["hwnd"] == fg1["hwnd"]
        print("foreground after:  %s (hwnd %s)  unchanged: %s" %
              (fg1["title"][:60], fg1["hwnd"], same))
    if exit_reason:
        # batch 11 (debt #17): say it twice - in the log and in the json - so a partial
        # batch can never be read as a finished one
        print("PARTIAL: the run stopped early - %s" % exit_reason, flush=True)
        print("         %d task(s) recorded of %d planned" % (len(runs), max_tasks), flush=True)
    if a.json_out:
        # gates: the v1 scoring口径 needs a truth_class per task, which the target
        # now broadcasts on its event stream (`ready`).  The driver never reads it back
        # to decide - score.py joins it afterwards.  Only t_trap declares truths, so
        # every other scenario keeps the v0 gate and stays labelled 不可比.
        def _sha(paths):
            h = hashlib.sha256()
            for p in paths:
                try:
                    with open(p, "rb") as fh:
                        h.update(fh.read())
                except OSError:
                    h.update(b"?")
            return h.hexdigest()[:12]

        with open(os.path.join(here, a.json_out), "w", encoding="utf-8") as fh:
            json.dump({"runs": runs, "stats": d.stats, "foreground_before": fg0,
                       "foreground_after": fg1,
                       # Batch 5: `v2` = the guard runs on file-sourced asks too, a prefix read is
                # not a change, and the plan word is settled by an exact on-screen match.
                # The scoring side keeps v1's definitions and adds the wrong_target/twin
                # split, so a v2 run is read by score.py with the same code path.
                # batch 6: `t_trap5` carries the post-guard race, so its rows say v3 while
                # everything up to `t_trap4` keeps the v2 label it was measured under
                "gates": ("v3" if str(a.scenario or "").startswith("t_trap5")
                          else "v2" if str(a.scenario or "").startswith("t_trap")
                          else "v0"),
                       "events": events,
                       "locked_at_end": locked_at_end,
                       "lock_waits": int(d.stats.get("lock_waits", 0)),
                       # batch 11 (debt #17): a partial run is still worth reading, but
                       # never worth mistaking for a full one
                       "partial": bool(exit_reason),
                       "exit_reason": exit_reason or None,
                       "tasks_planned": max_tasks,
                       "scripts_sha": _sha([os.path.join(here, "gym_run.py"),
                                            os.path.join(here, "gym_app.py"),
                                            os.path.join(here, "score.py")]),
                       "app_args": app_args,
                       "mode": {
                           "bg": bool(a.bg), "keys": bool(a.keys), "chaos": a.chaos,
                           "chaos_kind": a.chaos_kind,
                           "chaos_ms": a.chaos_ms,
                           "until_interferences": a.until_interferences,
                           "max_tasks": max_tasks}}, fh, ensure_ascii=False, indent=1)
    if proc:
        proc.terminate()
    if exit_reason:
        return 3                    # batch 11 (debt #17): partial run, json written
    return 0 if ok == len(runs) else 1


if __name__ == "__main__":
    sys.exit(main())
