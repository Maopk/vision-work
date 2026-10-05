"""A general GUI practice target: random tasks, random layout, honest truth.

The point is not cards.  It is a stand-in for "some GUI on this machine", so the
seeing-and-driving skill can be trained and scored without risking a real
program: every task is randomised (labels, positions, sizes, colours, which
scenario), the app writes down what actually happened, and the ask is rendered
on screen so an agent can read it the same way a human would.

Run:  python gym_app.py --seed 1234 --state state.json --events events.jsonl
Keys: n = new random task, k = skip, q = quit.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import string
import sys
import time
import tkinter as tk

SCHEMA = "gui-gym/1"

WORDS = ["alpha", "bravo", "cobalt", "delta", "ember", "frost", "gamma", "harbor",
         "indigo", "juno", "kilo", "lumen", "mica", "nova", "onyx", "prism",
         "quartz", "raven", "sable", "tundra", "umber", "vega", "willow", "xenon"]
NAMES = ["Ada", "Bo", "Cy", "Dee", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jo",
         "Kai", "Lia", "Mo", "Nia", "Ola", "Pia", "Quinn", "Rex", "Sam", "Tia"]
CITIES = ["Oslo", "Lima", "Kyiv", "Perth", "Quito", "Riga", "Sofia", "Tunis"]
STATUS = [("ok", "#1b8a3a"), ("warn", "#c8890a"), ("fail", "#b3261e"), ("idle", "#5a6675")]
FIELDS = ["Account", "Region", "Contact", "Channel", "Tier", "Owner", "Notes", "Ref"]
CHIP_COLORS = ["#2f6fd0", "#d0402f", "#1b8a3a", "#8a3fd0", "#c8890a", "#0f8a8a"]
BG = "#f4f6f8"
PANEL = "#ffffff"
# Keyboard channel: every control carries a visible "[k] label" hint, so a driver
# that must not steal the foreground can still work - Tk ignores posted *mouse*
# messages but does handle posted keys.  n/q/k stay reserved for the app itself.
HINT_KEYS = "123456789abcdefghijlmoprstuvwxyz"

# --- the no-badge class: where does "I can see a control" end? ---------------
# THE APP OWNS THE GROUND TRUTH.  A faded control is *operable* exactly when its
# paint fraction is at or above this constant - a click below it is ignored on
# purpose (and recorded as `ignored_click`), a click at or above it works.  The
# number is a declared task parameter, fixed before the batch runs; it is NOT
# derived from the driver's pixels, and the driver's visibility rule must not
# share this constant (that would make the class test one sentence twice).
OPERABLE_ALPHA = 0.45

# --- the trap family (`t_trap`, design: DESIGN-refusal-scoring.md §3) ---------
# Refusing has to be an *action*, otherwise the app cannot score "it was right to
# refuse" any differently from "it never did anything".  F8 is free: the action keys
# are the hint keys (digits/letters) and Escape only closes menus.
REFUSE_KEY = "F8"
# The five alphas bracket the block-fill threshold from *below*: prose sits at 0.213 and
# a painted button at 1.000, so 0.20/0.30 probe the low end - and 0.20 is deliberately
# under prose, where a fill-share test alone cannot tell the control from body text.
TRAP_ALPHAS = {"alpha020": 0.20, "alpha030": 0.30, "alpha035": 0.35,
               "alpha050": 0.50, "alpha065": 0.65}
# Batch 3's new class: the *whole* control (outline, fill and text) is painted at this
# fraction and carries no "[k]" hint badge, so the only way to act is to decide from
# pixels whether the control is really there.  Operability is the app's own constant
# (OPERABLE_ALPHA = 0.45): below it a click is swallowed and scored as a failure, at or
# above it the click works.  nb100 is the control condition - full contrast, no badge -
# without it "refused everything" cannot be told apart from "no badge, always refuse".
TRAP_FILL_ALPHAS = {"nb020": 0.20, "nb030": 0.30, "nb035": 0.35, "nb044": 0.44,
                    "nb046": 0.46, "nb050": 0.50, "nb065": 0.65, "nb100": 1.00}
# Batch 3's hard swap: the re-rolled word differs from the old one by exactly one glyph.
# The driver's staleness guard compares a 32x4 grey signature of the ask band, so a
# one-glyph change moves roughly one cell - far under its threshold - and the guard is
# structurally blind to it.  That is the point: it separates "the guard saw the change"
# from "the guard could not see the change", which the 600-1000 ms timer alone cannot.
HARD_PAIRS = (("XENON", "XENOM"), ("TANGO", "TANGQ"), ("KILO", "KILQ"),
              ("HARBOR", "HARBOP"), ("GAMMA", "GAMMB"))
# 8 classes x 3 tasks = 24 = the smoke-test batch.  Variants are laid out explicitly
# (2+1 for `prose_same_word` and `synonym`, three alphas for `half_transparent`) so a
# finished run can never be read as one blended rate for two different questions.
TRAP_PLAN: list[tuple[str, str]] = (
    [("prose_same_word", "prose_with_button")] * 2 + [("prose_same_word", "prose_only")]
    + [("two_close_names", "")] * 3
    + [("disabled", "")] * 3
    + [("half_transparent", "alpha035"), ("half_transparent", "alpha050"),
       ("half_transparent", "alpha065")]
    + [("flat_button", "")] * 3
    + [("synonym", "synonym_button")] * 2 + [("synonym", "synonym_only")]
    + [("bold_prose", "")] * 3
    + [("swap_mid_task", "")] * 3
)

# `t_trap2` = batch 2 ("t_trap++"), written after batch 1 went 24/24 five runs in a row.
# Five clean sweeps are a statement about the batch, not about the driver, so every class
# gets >= 10 tasks here and the two blind spots keep their own variants:
#   * batch 1's swap only ever fired on a 600-1000 ms timer, i.e. *before* the driver's
#     press - a_hit was 0 in all five runs, so the "A was right, then the screen changed"
#     half of the race was never exercised.  `swap_after_press` swaps *because* A was
#     pressed, which is the only shape in which a_hit can be 1.
#   * 0.35/0.50/0.65 all got clicked, so the low end was untested; 0.20/0.30 go below
#     prose's own 0.213.
TRAP_PLAN2: list[tuple[str, str]] = (
    # the swap class leads on purpose: it is the headline measurement of batch 2, and an
    # early stop anywhere later in the batch must not be able to hide it
    [("swap_mid_task", "swap_after_press")] * 10
    + [("swap_mid_task", "swap_timer")] * 5
    + [("prose_same_word", "prose_with_button")] * 6 + [("prose_same_word", "prose_only")] * 4
    + [("two_close_names", "")] * 10
    + [("disabled", "")] * 10
    + [("half_transparent", a) for a in ("alpha020", "alpha030", "alpha035",
                                         "alpha050", "alpha065")] * 2
    + [("flat_button", "")] * 10
    + [("synonym", "synonym_button")] * 6 + [("synonym", "synonym_only")] * 4
    + [("bold_prose", "")] * 10
)

# Batch 3 (`t_trap3`) = the *mouse-channel* batch.  Only classes whose question is
# answerable from pixels alone are in it: the faded no-badge control (the visibility
# boundary - the headline measurement, so it leads), the two hard-swap shapes, the two
# batch-2 swap shapes re-run on the real mouse, the five half-transparent alphas (they
# carry a badge, so `control_visible` short-circuits on the badge) and the synonyms.
# The five badge-judged must_refuse classes (prose_only / two_close_names / disabled /
# flat_button / bold_prose, 50 tasks) stay in the keyboard batches on purpose: their
# verdict comes from "is there a [k] badge", which a mouse run does not ask.
TRAP_PLAN3: list[tuple[str, str]] = (
    [("no_badge_fill", v) for v in ("nb020", "nb030", "nb035",
                                    "nb050", "nb065", "nb100")] * 3
    + [("no_badge_fill", "nb044")] * 5
    + [("no_badge_fill", "nb046")] * 5
    + [("swap_mid_task", "swap_hard_press")] * 5
    + [("swap_mid_task", "swap_hard_timer")] * 3
    + [("swap_mid_task", "swap_after_press")] * 10
    + [("swap_mid_task", "swap_timer")] * 5
    + [("half_transparent", a) for a in ("alpha020", "alpha030", "alpha035",
                                         "alpha050", "alpha065")] * 2
    + [("synonym", "synonym_button")] * 6 + [("synonym", "synonym_only")] * 4
)

# Batch 4 (`t_trap4`) = the "self-believed correct" batch.  Its headline class is
# `swap_twin_press`: after a correct press on A the ask moves to B, B's button is on
# screen for the whole episode, and B's word *also* sits in a heading above the grid.
# A driver that trusts text over controls clicks the heading - not a control - and the
# target scores the task wrong: A was hit, B was never answered.  That is the one cell
# the first three batches could not produce (`a_hit_but_failed`), and it is reachable in
# two ways, both landing in it: with the guard working the driver re-plans onto B and
# then picks the wrong occurrence of the word; with the guard missing the one-glyph
# re-roll it presses A again and is judged wrong.  The twin family leads the plan, the
# two hard-swap shapes then verify the guard fix, the visibility slice is the unchanged
# reference, and the two batch-2 swap shapes are the race regression.
TRAP_PLAN4: list[tuple[str, str]] = (
    [("swap_mid_task", "swap_twin_press")] * 8
    + [("swap_mid_task", "swap_hard_press")] * 5
    + [("swap_mid_task", "swap_hard_timer")] * 5
    + [("no_badge_fill", v) for v in ("nb046",) * 3 + ("nb050",) * 3
                                 + ("nb065",) * 2 + ("nb100",) * 2]
    + [("swap_mid_task", "swap_after_press")] * 5
    + [("swap_mid_task", "swap_timer")] * 5
)

# Batch 5 (`t_trap5`) = batch 4's plan with the post-guard race appended.  The first 38
# entries are copied verbatim, so under the same seed tasks 0-37 are byte-identical to
# `t_trap4` and the frozen core-14 subset meets the same words instead of a re-roll.  The
# ten new tasks are the one race shape batch 5 could not produce: `swap_race_timer` fires
# late enough to land between the driver's pre-press guard frame and the click itself.
TRAP_PLAN5: list[tuple[str, str]] = TRAP_PLAN4 + [("swap_mid_task", "swap_race_timer")] * 10


def code(rng: random.Random, n: int = 4) -> str:
    return "".join(rng.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def blend(a: str, b: str, t: float) -> str:
    """Mix two #rrggbb colours - how a half-transparent control is painted here.

    Tk has no per-widget alpha, and the driver only ever sees pixels, so the control
    is drawn as a canvas rectangle whose fill sits `t` of the way from the page
    colour to the button colour.  That is exactly the "block fill share" the driver
    measures, which is the point: 0.35/0.50/0.65 probe the middle of the threshold.
    """
    ar, ag, ab = (int(a[i:i + 2], 16) for i in (1, 3, 5))
    br, bgc, bb = (int(b[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (round(ar + (br - ar) * t), round(ag + (bgc - ag) * t),
                              round(ab + (bb - ab) * t))


def scatter(rng: random.Random, taken: list, w: int, h: int, cx: int, cy: int,
            jitter: int = 10) -> tuple[int, int]:
    """A random spot in the cx*cy grid whose w*h box clears everything already in `taken`.

    Plain uniform placement lets two 150x96 slot boxes land on top of each other, and then
    their labels are drawn as overlapping text - unreadable for a human and for OCR alike.
    The randomness is kept per task; only the self-occlusion is engineered away.
    """
    cells = [(i, j) for i in range(cx) for j in range(cy)]
    rng.shuffle(cells)
    for i, j in cells:
        for attempt in range(6):
            dx = rng.randrange(-jitter, jitter + 1) if attempt else 0
            dy = rng.randrange(-jitter, jitter + 1) if attempt else 0
            x = min(max(i * w + dx, 8), max(8, cx * w - w - 8))
            y = min(max(j * h + dy, 8), max(8, cy * h - h - 8))
            box = (x, y, x + w, y + h)
            if not any(box[0] < t[2] and t[0] < box[2] and box[1] < t[3] and t[1] < box[3]
                       for t in taken):
                return x, y
    return 8, 8


def make_dpi_aware() -> None:
    """Without this Windows bitmap-stretches the window (blurry pixels = bad OCR)."""
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


class Gym(tk.Tk):
    def __init__(self, seed: int, state_path: str | None, events_path: str | None,
                 scenario: str | None = None, gap_ms: int = 250, chaos_p: float = 0.0,
                 chaos_ms: tuple[int, int] = (600, 1800), chaos_kind: str = "any",
                 popup_topmost: bool = True,
                 no_badge: bool = False, control_alpha: float | None = None):
        super().__init__()
        self.rng = random.Random(seed)
        self.seed = seed
        self.state_path = state_path
        self.events_path = events_path
        self.fixed_scenario = scenario
        self.gap_ms = gap_ms
        self.chaos_p = chaos_p
        self.chaos_ms = chaos_ms
        self.chaos_kind = chaos_kind       # train one disturbance at a time
        self.popup_topmost = popup_topmost  # False while a driver works in background
        self.no_badge = no_badge          # paint controls without "[k] label" hints
        self.control_alpha = control_alpha  # forced paint fraction (probe mode)
        self.keymap: dict = {}            # keysym -> callable, rebuilt for every task
        self.open_menu = None             # (name, [(hint, item)]) while a menu is open
        self.keymap_items: dict = {}      # item hint -> callable, armed by _menu_open
        self.chip_sel = None              # chip carried over the keyboard path
        self.row_hints: list = []         # [(hint label widget, row id)]
        self.row_keys: list = []          # hint keys bound to the visible page
        self.row_want = None              # t_rows: the row id the task asks for
        self.row_canvas = None            # t_rows: the canvas the page keys scroll
        self.trap_i = 0                   # t_trap: position in TRAP_PLAN
        self.trap_truth = None            # t_trap: "answerable" | "must_refuse"
        self.trap_want = None             # t_trap: the label that would be right
        self.trap_variant = ""            # t_trap: which variant is on screen
        self.modal = None                 # interference window: scoring is blocked
        self.verdict_delay_ms = 0         # "slow": the verdict shows up late on purpose
        self._pending = None              # a delayed verdict still waiting to commit
        self.task_i = -1
        self.task: dict = {}
        self.result = "none"
        self.detail: dict = {}
        self.history: list = []
        self.t0 = time.time()
        self.title("GUI Gym")
        w, h = 1180, 780
        x0 = 120 + self.rng.randrange(0, 260)
        y0 = 90 + self.rng.randrange(0, 200)
        self.geometry("%dx%d+%d+%d" % (w, h, x0, y0))
        self.configure(bg=BG)
        self.banner = tk.Label(self, text="", font=("Segoe UI", -26, "bold"),
                               bg="#12263a", fg="#ffffff", anchor="w", padx=14, pady=8,
                               wraplength=w - 40, justify="left")
        self.banner.pack(fill="x")
        self.status = tk.Label(self, text="", font=("Segoe UI", -20),
                               bg="#dbe4ee", fg="#12263a", anchor="w", padx=14, pady=6)
        self.status.pack(fill="x")
        self.body = tk.Frame(self, bg=BG)
        self.body.pack(fill="both", expand=True, padx=10, pady=10)
        self.keybar = tk.Label(self, text="", font=("Segoe UI", -18), bg="#eef3f8",
                               fg="#3b4a5a", anchor="w", padx=14, pady=4)
        self.keybar.pack(side="bottom", fill="x")
        self.bind("<Key>", self._on_key)
        self.bind_all("<Key-n>", lambda e: self.next_task())
        self.bind_all("<Key-q>", lambda e: self.destroy())
        self.bind_all("<Key-k>", lambda e: self.finish(False, {"skipped": True}))
        self.after(200, self.next_task)

    # ------------------------------------------------------------ plumbing --
    def layout_info(self) -> dict:
        self.update_idletasks()
        return {"origin": [self.winfo_rootx(), self.winfo_rooty()],
                "size": [self.winfo_width(), self.winfo_height()]}

    def state(self) -> dict:
        return {"schema": SCHEMA, "seed": self.seed, "task_i": self.task_i,
                "scenario": self.task.get("scenario"), "ask": self.task.get("ask"),
                "truth": self.task.get("truth"), "layout": self.layout_info(),
                "result": self.result, "detail": self.detail,
                "history": self.history[-60:],
                "elapsed_ms": round((time.time() - self.t0) * 1000, 1)}

    def write_state(self, rec: dict) -> None:
        """Replace the state file, surviving a reader that has it open right now.

        A driver polls this file every ~80 ms, and on Windows Python opens files without
        FILE_SHARE_DELETE, so os.replace intermittently fails with WinError 5. That is
        expected traffic, not an error: retry briefly, then fall back to a plain rewrite
        (which does land while the file is open for reading).
        """
        if not self.state_path:
            return
        data = json.dumps(rec, ensure_ascii=False)
        tmp = self.state_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(data)
        for attempt in range(6):
            try:
                os.replace(tmp, self.state_path)
                return
            except PermissionError:
                time.sleep(0.004 * (attempt + 1))
        with open(self.state_path, "w", encoding="utf-8") as fh:
            fh.write(data)
        try:
            os.unlink(tmp)
        except OSError:
            pass

    def emit(self, event: str, **extra) -> None:
        rec = dict(self.state(), event=event, **extra)
        # never let bookkeeping abort its caller: this is called from the key handler as
        # the first statement, so an OSError here used to swallow a delivered key whole
        # (the app then looks like it dropped an input it actually received)
        try:
            self.write_state(rec)
            if self.events_path:
                with open(self.events_path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError as exc:
            print("emit %s failed: %s" % (event, exc), file=sys.stderr, flush=True)
        print(json.dumps({"event": event, "task_i": self.task_i,
                          "scenario": rec.get("scenario"), "ask": rec.get("ask"),
                          "layout": rec["layout"]}, ensure_ascii=False), flush=True)

    # ----------------------------------------------------- keyboard channel --
    def _hint(self, i: int) -> str:
        """The hint a driver has to *read off the screen* for control i."""
        return "[%s]" % HINT_KEYS[i] if 0 <= i < len(HINT_KEYS) else ""

    def _bind_key(self, i: int, fn) -> str:
        if 0 <= i < len(HINT_KEYS):
            self.keymap[HINT_KEYS[i]] = fn
        return self._hint(i)

    def _hinted(self, i: int, text: str) -> str:
        return ("%s %s" % (self._hint(i), text)).strip()

    def _echo(self, text: str) -> None:
        self.keybar.configure(text=text)

    def _on_key(self, e) -> None:
        """Every task shares one key dispatcher; the per-task map says what a key means.

        Typing into an Entry must never fire a hint, and the app's own keys (n/q/k)
        keep working - both are filtered out before the lookup.
        """
        ks = e.keysym
        if ks in ("??", "") and e.char:
            # a key posted from another process can arrive with the character but no
            # keysym mapping (no scan code in the message); accept the character too,
            # the way any app that binds <Key> would
            ks = e.char
        # diagnosis only, *before* the guards: a key that is filtered out must still be
        # visible, otherwise "the driver pressed it" and "the app saw it" cannot be told
        # apart from the app's side
        self.emit("key", ks=ks, hit=ks in self.keymap, armed=sorted(self.keymap.keys()),
                  char=e.char, keycode=e.keycode, num=e.keysym_num, state=e.state,
                  widget=type(e.widget).__name__, modal=self.modal is not None,
                  menu=self.open_menu is not None)
        if e.state & 0x20005:                       # shift/ctrl/alt held: not a hint
            return
        if self.modal is not None:
            # an interference window is up and nothing is scored until it is gone; a
            # driver that may not use the mouse answers it with a key posted to *this*
            # window (finding the dialog's own hwnd would be a second problem)
            if ks in ("Return", "space", "Escape", "d", "D"):
                self._close_modal()
                self._echo("interference dismissed")
            return
        if isinstance(e.widget, tk.Entry) and ks != "Return":
            return
        if ks in ("n", "q", "k"):
            return
        if self.open_menu is not None:
            self._menu_key(ks)
            return
        fn = self.keymap.get(ks)
        if fn is None:
            return
        self._echo("key %s" % ks)
        fn()

    def _menu_open(self, name: str, items: dict, cmds: dict, hints: dict) -> None:
        """Keyboard path through a menubar: the open menu states its items in words.

        The popup itself is a separate native window that a background driver cannot
        capture, so the items are echoed as text and their keys stay armed until one
        is picked (or Escape closes the menu).
        """
        # the key that picks an item is the bare hint key (HINT_KEYS), not the bracketed
        # form _hint() prints: the bracketed one is what a driver reads off the screen,
        # and arming that string as a key made every item key miss (lookup returned None
        # and the menu just stayed open, silently)
        idx = {it: HINT_KEYS[j] for j, it in enumerate(items[name])}
        self.keymap_items = {idx[it]: cmds[(name, it)] for it in items[name]}
        self.open_menu = (name, [(hints[(name, it)], it) for it in items[name]])
        self._echo("menu %s: %s" % (name, "   ".join(
            "%s %s" % (hints[(name, it)], it) for it in items[name])))

    def _menu_key(self, ks: str) -> None:
        if ks in ("Escape", "Return"):
            self.open_menu, self.keymap_items = None, {}
            self._echo("")
            return
        fn = self.keymap_items.get(ks)
        if fn is None:
            return
        self._echo("key %s" % ks)
        fn()

    def _page(self, step: int) -> None:
        """Scroll the row canvas by pages - the wheel is a mouse message, so a
        keyboard driver needs page keys to reach rows below the fold."""
        c = self.row_canvas
        if c is None:
            return
        c.yview_scroll(step * 9, "units")
        self._row_keys()

    def _row_keys(self) -> None:
        """Hint only the rows that are on screen - a key for an unseen row is a trap."""
        c = self.row_canvas
        if c is None or not self.row_hints:
            return
        for ks in self.row_keys:
            self.keymap.pop(ks, None)
        self.row_keys = []
        top, h = c.canvasy(0), c.winfo_height()
        i = 0
        first_y = last_y = None
        for hint, rid in self.row_hints:
            try:
                y = hint.master.winfo_y()
            except tk.TclError:               # a widget from a previous build
                continue
            if top - 4 <= y <= top + h:
                hint.configure(text=self._hinted(i, ""))
                self._bind_key(i, lambda rid=rid: self.finish(
                    rid == self.row_want, {"selected": rid, "want": self.row_want}))
                self.row_keys.append(HINT_KEYS[i])
                if first_y is None:
                    first_y = y
                last_y = y
                i += 1
            else:
                hint.configure(text="")
        # diagnosis only: which slice of the list the canvas considers visible right now
        self.emit("rowkeys", top=top, height=h, armed=len(self.row_keys),
                  rows=len(self.row_hints), first_y=first_y, last_y=last_y)

    def finish(self, ok: bool, detail: dict) -> None:
        """Record a verdict - unless an interference window is still up.

        While a modal window exists the app refuses to score, the way a real
        program ignores clicks behind a dialog.
        """
        if self.result != "none" or self._pending is not None:
            return
        if self.modal is not None and self.modal.winfo_exists():
            self.emit("blocked", by="modal")
            return
        if self.verdict_delay_ms:                     # "slow": the answer arrives late
            self._pending = self.after(self.verdict_delay_ms,
                                       lambda: self._commit(ok, detail))
            self.emit("verdict_delayed", ms=self.verdict_delay_ms)
            return
        self._commit(ok, detail)

    def _commit(self, ok: bool, detail: dict) -> None:
        self._pending = None
        if self.result != "none":
            return
        self.result = "ok" if ok else "wrong"
        self.detail = detail
        # the driver may only look at the screen, so the verdict has to outlive
        # the task it belongs to: it auto-advances after gap_ms
        self.history.append({"task_i": self.task_i, "scenario": self.task.get("scenario"),
                             "ask": self.task.get("ask"), "truth": self.task.get("truth"),
                             "result": self.result, "detail": detail,
                             "ms": round((time.time() - self.t0) * 1000, 1)})
        self.status.configure(text=("DONE  " if ok else "WRONG  ") +
                              json.dumps(detail, ensure_ascii=False)[:140],
                              bg="#c8e6c9" if ok else "#ffcdd2")
        # the old keys must not fire during the gap before the next task exists:
        # a driver that presses "7" now would be answering a question that is gone
        self.keymap, self.keymap_items, self.open_menu = {}, {}, None
        self.emit("done")
        self.after(self.gap_ms, self.next_task)

    def next_task(self) -> None:
        for ch in self.body.winfo_children():
            ch.destroy()
        self.unbind_all("<MouseWheel>")     # t_rows binds it globally
        self.configure(menu="")             # t_menu installs one
        if self._pending is not None:       # a stale delayed verdict must not land here
            self.after_cancel(self._pending)
            self._pending = None
        self._close_modal()
        self.verdict_delay_ms = 0
        self.keymap, self.row_hints = {}, []
        self.open_menu, self.chip_sel, self.row_canvas = None, None, None
        self._echo("")
        try:
            self.focus_set()            # a stale Entry focus would swallow every hint
        except Exception:
            pass
        self.result, self.detail, self.t0 = "none", {}, time.time()
        self.trap_truth, self.trap_want, self.trap_variant = None, None, ""
        self.task_i += 1
        pool = [self.t_button, self.t_rows, self.t_form, self.t_toggle, self.t_menu,
                self.t_chips]
        build = getattr(self, self.fixed_scenario) if self.fixed_scenario else self.rng.choice(pool)
        self.banner.configure(text="")
        self.status.configure(text="working", bg="#dbe4ee")
        self.task = build()
        self.banner.configure(text="DO: " + self.task["ask"])
        self.update_idletasks()
        # The declared truth rides the event stream so a scorer can join it after the
        # fact.  It is here for scoring, never for acting: the whole point of the trap
        # family is that the driver must not read the answer back before deciding.
        tr = self.task.get("truth") or {}
        if tr.get("truth_class"):
            self.emit("ready", truth_class=tr["truth_class"], variant=tr.get("variant", ""),
                      trap_class=tr.get("class"))
        else:
            self.emit("ready")
        self._plan_chaos()

    # -------------------------------------------------------------- chaos ---
    def _close_modal(self) -> None:
        if self.modal is not None:
            try:
                self.modal.destroy()
            except Exception:
                pass
            self.modal = None

    def _plan_chaos(self) -> None:
        """Schedule one live change for this task - the "reactive" training target.

        A driver that only memorised the first read must lose; a driver that keeps
        looking must recover.  The change is visible on screen, never announced in
        the state file alone: values get re-rolled, the layout shifts, a window
        appears, or the verdict simply takes longer than usual.
        """
        if self.chaos_p <= 0 or not self.task or self.rng.random() >= self.chaos_p:
            return
        kind = (self.chaos_kind if self.chaos_kind != "any"
                else self.rng.choice(["rebuild", "move", "popup", "slow"]))
        delay = self.rng.randrange(self.chaos_ms[0], self.chaos_ms[1])
        tok = self.task_i
        self.emit("chaos_planned", kind=kind, delay_ms=delay)
        self.after(delay, lambda: self._chaos_fire(tok, kind))

    def _chaos_fire(self, tok: int, kind: str) -> None:
        if self.task_i != tok or self.result != "none" or not self.task:
            return
        if kind == "rebuild":
            self._chaos_rebuild()
        elif kind == "move":
            self._chaos_move()
        elif kind == "popup":
            self._chaos_popup()
        elif kind == "slow":
            self.verdict_delay_ms = self.rng.randrange(1500, 3200)
        self.emit("chaos", kind=kind, ask=self.task.get("ask"))

    def _chaos_rebuild(self) -> None:
        """Re-roll this very task: same scenario family, new values, new positions."""
        build = getattr(self, self.fixed_scenario or self.task.get("scenario", ""), None)
        if build is None:
            return
        old = self.task.get("ask")
        for _ in range(6):
            for ch in self.body.winfo_children():
                ch.destroy()
            self.unbind_all("<MouseWheel>")
            self.configure(menu="")
            # Per-scenario widget registries must be dropped with the widgets they
            # point at. Measured: a rebuilt t_rows kept the old (destroyed) hint
            # labels in self.row_hints, so the next _row_keys() died on the first
            # dead widget (TclError inside an `after` callback), every row stayed
            # un-hinted, and the task had no keyboard answer at all.
            self.keymap, self.row_hints = {}, []
            self.open_menu, self.chip_sel, self.row_canvas = None, None, None
            self.task = build()
            if self.task.get("ask") != old:       # the change has to be visible
                break
        self.banner.configure(text="DO: " + self.task["ask"])
        self.update_idletasks()

    def _chaos_move(self) -> None:
        """Shift the body mid-task, and sometimes the whole window."""
        self.body.pack_configure(padx=10 + self.rng.randrange(20, 90),
                                 pady=10 + self.rng.randrange(20, 70))
        if self.rng.random() < 0.5:
            self.geometry("%dx%d+%d+%d" % (self.winfo_width(), self.winfo_height(),
                                           120 + self.rng.randrange(0, 300),
                                           90 + self.rng.randrange(0, 220)))
        self.update_idletasks()

    def _chaos_popup(self) -> None:
        """A stray window over the app: nothing is scored until it is gone.

        Painted like an ordinary light dialog with dark text, because that is what
        a real one looks like - a dark panel with pale text would only be legible
        to a driver that already knew what it said.
        """
        bg = "#f3f3f3"
        top = tk.Toplevel(self)
        top.title("attention")
        top.configure(bg=bg)
        top.geometry("%dx%d+%d+%d" % (470, 210,
                                      self.winfo_rootx() + self.rng.randrange(80, 420),
                                      self.winfo_rooty() + self.rng.randrange(150, 400)))
        tk.Label(top, text="interference", bg=bg, fg="#20232a",
                 font=("Segoe UI", -24, "bold")).pack(pady=(18, 6))
        tk.Label(top, text="dismiss this before the task can be scored", bg=bg,
                 fg="#3b4048", font=("Segoe UI", -16)).pack()

        def close() -> None:
            self.modal = None
            top.destroy()

        btn = tk.Button(top, text="DISMISS", font=("Segoe UI", -20, "bold"), bg="#dcdcdc",
                        fg="#101216", relief="raised", bd=3, command=close)
        btn.pack(pady=(14, 4))
        tk.Label(top, text="or press space", bg=bg, fg="#5a6675",
                 font=("Segoe UI", -15)).pack()
        # a driver that may not use the mouse has to be able to answer with a key:
        # Tk hands a posted key to the focused widget of the whole application
        btn.focus_set()
        btn.bind("<Return>", lambda e: close())
        btn.bind("<space>", lambda e: close())
        top.bind("<Escape>", lambda e: close())
        # the driver pins the main window topmost before every look, so a plain
        # toplevel would be covered and never seen - unless it works in background
        # mode, where it captures this window by hwnd and must not steal the screen.
        if self.popup_topmost:
            top.attributes("-topmost", True)
            top.lift()
        self.modal = top

    # ---------------------------------------------------------- scenarios ---
    def t_button(self) -> dict:
        """Click the button whose label matches."""
        rng = self.rng
        n = rng.randrange(6, 13)
        labels = rng.sample(WORDS, min(n, len(WORDS)))
        labels = [w.upper() if rng.random() < 0.5 else w for w in labels]
        for i in range(len(labels)):                 # make some labels look alike
            if rng.random() < 0.4:
                labels[i] = labels[i] + str(rng.randrange(10, 99))
        target = rng.choice(labels)
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="both", expand=True)
        cols = rng.choice([2, 3, 4])
        for i, lab in enumerate(labels):
            pad_x = rng.randrange(6, 40)
            pad_y = rng.randrange(4, 28)
            b = tk.Button(grid, text=self._hinted(i, lab), font=("Segoe UI", -20),
                          width=rng.randrange(8, 16), pady=rng.randrange(2, 10),
                          bg="#e8eef5", activebackground="#c9dcf0")
            b.grid(row=i // cols, column=i % cols, padx=pad_x, pady=pad_y, sticky="ew")
            b.configure(command=lambda L=lab: self.finish(L == target, {"clicked": L, "want": target}))
            self._bind_key(i, b.invoke)
        return {"scenario": "t_button", "ask": "click the button labelled %s" % target,
                "truth": {"label": target, "buttons": labels}}

    def t_rows(self) -> dict:
        """Select the row with a given id - the row is often below the fold."""
        rng = self.rng
        n = rng.randrange(14, 34)
        ids = rng.sample(range(1000, 9999), n)
        names = [rng.choice(NAMES) + " " + rng.choice(CITIES) for _ in range(n)]
        st = [rng.choice(STATUS) for _ in range(n)]
        target_i = rng.randrange(n)
        target = ids[target_i]
        wrap = tk.Frame(self.body, bg=PANEL, highlightthickness=1, highlightbackground="#9aa3ad")
        wrap.pack(fill="both", expand=True)
        canvas = tk.Canvas(wrap, bg=PANEL, highlightthickness=0)
        bar = tk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=PANEL)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        row_h = rng.choice([34, 40, 46])
        for k in range(n):
            row = tk.Frame(inner, bg=PANEL, height=row_h)
            row.pack(fill="x", pady=1)
            hint = tk.Label(row, text="", width=4, font=("Segoe UI", -18, "bold"),
                            bg=PANEL, fg="#b3261e", anchor="w")
            hint.pack(side="left", padx=(8, 2))
            dot = tk.Label(row, text="  ", bg=st[k][1], font=("Segoe UI", -16))
            dot.pack(side="left", padx=(2, 10))
            lab = tk.Label(row, text="#%d  %s   %s" % (ids[k], names[k], st[k][0].upper()),
                           font=("Segoe UI", -18), bg=PANEL, anchor="w")
            lab.pack(side="left", fill="x", expand=True)
            for w in (row, dot, lab, hint):
                w.bind("<Button-1>", lambda e, k=k, rid=ids[k]: self.finish(
                    rid == target, {"selected": rid, "want": target}))
            self.row_hints.append((hint, ids[k]))
        # a spacer under the last row: at the very bottom of the scroll the last row
        # would otherwise sit outside the hinted window and could never be picked, so
        # a keyboard driver would page around it forever
        tk.Frame(inner, bg=PANEL, height=52).pack(fill="x")
        inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        self.row_canvas, self.row_want = canvas, target
        self.bind_all("<MouseWheel>", lambda e: (canvas.yview_scroll(int(-e.delta / 60), "units"),
                                                 self._row_keys()))
        canvas.bind("<Configure>", lambda e: self._row_keys())
        self.keymap["Next"] = lambda: self._page(1)
        self.keymap["Prior"] = lambda: self._page(-1)
        # fine scrolling: a page jump can leave the wanted row clipped at the edge of
        # the canvas, where its hint label is only half drawn and cannot be read
        self.keymap["Up"] = lambda: (canvas.yview_scroll(-1, "units"), self._row_keys())
        self.keymap["Down"] = lambda: (canvas.yview_scroll(1, "units"), self._row_keys())
        self.keymap["Home"] = lambda: (canvas.yview_moveto(0.0), self._row_keys())
        self.keymap["End"] = lambda: (canvas.yview_moveto(1.0), self._row_keys())
        self.after(60, self._row_keys)
        return {"scenario": "t_rows", "ask": "select the row whose id is %d" % target,
                "truth": {"id": target, "rows": n, "row_height": row_h}}

    def t_form(self) -> dict:
        """Fill the named fields, then press GO."""
        rng = self.rng
        fields = rng.sample(FIELDS, rng.randrange(3, 6))
        want = {f: rng.choice([code(rng), str(rng.randrange(100, 999)),
                               rng.choice(WORDS).title()]) for f in fields}
        box = tk.Frame(self.body, bg=BG)
        box.pack(fill="both", expand=True)
        entries = {}
        for i, f in enumerate(fields):
            tk.Label(box, text=self._hinted(i, f + ":"), font=("Segoe UI", -20), bg=BG,
                     anchor="e", width=12).grid(row=i, column=0, padx=(10, 8),
                                                pady=rng.randrange(6, 22), sticky="e")
            e = tk.Entry(box, font=("Segoe UI", -20), width=rng.randrange(14, 26),
                         relief="sunken", bd=2)
            e.grid(row=i, column=1, padx=6, pady=6, sticky="w")
            e.bind("<Escape>", lambda ev, w=e: (w.delete(0, "end"), "break")[1])
            entries[f] = e
            # whether a *posted* character reaches a focused Entry is the open question of
            # the keyboard channel, so record what lands in it, one key at a time
            e.bind("<KeyRelease>", lambda ev, w=e, n=f: self.emit("entry", field=n, text=w.get()))
            self._bind_key(i, e.focus_set)
        def go():
            got = {f: e.get() for f, e in entries.items()}
            want_sub = {f: want[f] for f in want}
            ok = all(got[f].strip() == want_sub[f] for f in want_sub)
            self.finish(ok, {"filled": got, "want": want_sub})
        for e in entries.values():
            e.bind("<Return>", lambda ev: go())
        gb = tk.Button(box, text=self._hinted(len(fields), "GO"), font=("Segoe UI", -22, "bold"),
                       bg="#c9dcf0", width=10, command=go)
        gb.grid(row=len(fields), column=1, pady=18, sticky="w")
        self._bind_key(len(fields), gb.invoke)
        ask = "fill " + " and ".join("%s = %s" % (f, want[f]) for f in fields) + " then press GO"
        return {"scenario": "t_form", "ask": ask, "truth": {"want": want, "fields": fields}}

    def t_toggle(self) -> dict:
        """Turn one named switch on/off and set a slider to a number."""
        rng = self.rng
        names = rng.sample(WORDS, rng.randrange(3, 6))
        which = rng.choice(names)
        target_on = rng.random() < 0.5
        want_num = rng.randrange(3, 10)
        box = tk.Frame(self.body, bg=BG)
        box.pack(fill="both", expand=True)
        state = {n: tk.BooleanVar(value=(rng.random() < 0.5)) for n in names}
        readout = tk.Label(box, text="", font=("Segoe UI", -22, "bold"), bg=BG)
        cbs: dict = {}
        hint_of: dict = {}
        def paint(n) -> None:
            """The switch shows its own state as text: a driver that cannot judge a
            tick mark by sight can still read ON/OFF and decide whether to press."""
            cbs[n].configure(text="%s %s   %s" % (hint_of[n], n,
                                                  "ON" if state[n].get() else "OFF"))
        def check(*_):
            for n in cbs:
                paint(n)
            ok = state[which].get() == target_on and int(scale.get()) == want_num
            if ok and self.result == "none":
                self.finish(True, {"switch": which, "on": target_on, "slider": want_num})
        for i, n in enumerate(names):
            cb = tk.Checkbutton(box, text=n, variable=state[n], font=("Segoe UI", -20),
                                bg=BG, command=check)
            cb.grid(row=i, column=0, sticky="w", padx=12, pady=rng.randrange(4, 16))
            cbs[n], hint_of[n] = cb, self._hint(i)
            self._bind_key(i, cb.invoke)
            paint(n)
        scale = tk.Scale(box, from_=0, to=12, orient="horizontal", font=("Segoe UI", -18),
                         length=420, bg=BG, command=lambda v: (readout.configure(text="value " + str(int(float(v)))),
                                                              check()))
        scale.set(rng.randrange(0, 13))
        scale.grid(row=len(names), column=0, padx=12, pady=16, sticky="w")
        readout.configure(text="value " + str(int(scale.get())))
        readout.grid(row=len(names) + 1, column=0, padx=12, sticky="w")
        tk.Label(box, text="slider: press left / right (one step each)", bg=BG, fg="#3b4a5a",
                 font=("Segoe UI", -16)).grid(row=len(names) + 2, column=0, padx=12, sticky="w")

        def step(d: int) -> None:
            scale.set(max(0, min(12, int(scale.get()) + d)))
        self.keymap["Left"] = lambda: step(-1)
        self.keymap["Right"] = lambda: step(1)
        self.toggle_probe = {"names": names, "which": which, "target_on": target_on,
                             "want_num": want_num}
        return {"scenario": "t_toggle",
                "ask": "set %s %s and the slider to %d" % (which, "ON" if target_on else "OFF", want_num),
                "truth": {"switch": which, "on": target_on, "slider": want_num,
                          "names": names}}

    def t_menu(self) -> dict:
        """Invoke a menu command (mouse path through a menubar)."""
        rng = self.rng
        menus = [m.upper() for m in rng.sample(WORDS, rng.randrange(2, 4))]
        items = {m: [rng.choice(WORDS).title() for _ in range(rng.randrange(2, 4))] for m in menus}
        m_want = rng.choice(menus)
        i_want = rng.choice(items[m_want])
        bar = tk.Menu(self)
        last = {"cmd": None}
        cmds: dict = {}
        hints: dict = {}
        def mk(menu, item):
            def fn():
                self.open_menu, self.keymap_items = None, {}
                last["cmd"] = (menu, item)
                self.finish(menu == m_want and item == i_want,
                            {"invoked": [menu, item], "want": [m_want, i_want]})
            return fn
        for i, m in enumerate(menus):
            sub = tk.Menu(bar, tearoff=0, font=("Segoe UI", -18))
            for j, it in enumerate(items[m]):
                fn_j = mk(m, it)
                cmds[(m, it)], hints[(m, it)] = fn_j, self._hint(j)
                sub.add_command(label="%s %s" % (self._hint(j), it), command=fn_j)
            bar.add_cascade(label=self._hinted(i, m), menu=sub)
            self._bind_key(i, lambda m=m: self._menu_open(m, items, cmds, hints))
        self.configure(menu=bar)
        panel = tk.Frame(self.body, bg=BG)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="use the menu bar", font=("Segoe UI", -20), bg=BG).pack(pady=20)
        return {"scenario": "t_menu", "ask": "invoke the menu %s > %s" % (m_want, i_want),
                "truth": {"menu": m_want, "item": i_want, "menus": menus}}

    def t_chips(self) -> dict:
        """Drag a numbered chip into the labelled slot that matches it."""
        rng = self.rng
        n = rng.randrange(3, 6)
        slots = [code(rng, 3) for _ in range(n)]
        chips = rng.sample(range(10, 99), n)
        pair = rng.randrange(n)
        c = tk.Canvas(self.body, bg="#e9edf2", highlightthickness=1, highlightbackground="#9aa3ad")
        c.pack(fill="both", expand=True)
        c.update_idletasks()
        W = max(self.winfo_width() - 40, 600)
        H = max(self.winfo_height() - 220, 380)
        slot_boxes = {}
        taken: list[tuple[int, int, int, int]] = []
        for i, s in enumerate(slots):
            x, y = scatter(rng, taken, 150, 96, max(2, W // 174), max(2, H // 120), jitter=14)
            bx0, by0, bx1, by1 = x, y, x + 150, y + 96
            taken.append((bx0 - 6, by0 - 6, bx1 + 6, by1 + 6))
            c.create_rectangle(bx0, by0, bx1, by1, outline="#5a6675", width=3, dash=(6, 4))
            c.create_text(bx0 + 75, by0 + 26, text="%s SLOT %s" % (self._hint(i), s),
                          font=("Segoe UI", -18, "bold"), fill="#33475c")
            slot_boxes[s] = (bx0, by0, bx1, by1)
            self._bind_key(i, lambda s=s: drop_slot(s))
        chip_xy = {}
        for i, v in enumerate(chips):
            x, y = scatter(rng, taken, 74, 96, max(2, W // 84), max(2, H // 110), jitter=12)
            taken.append((x - 6, y - 6, x + 74 + 6, y + 96 + 6))
            col = rng.choice(CHIP_COLORS)
            tag = "c%d" % v
            c.create_oval(x, y, x + 74, y + 74, fill=col, outline="#1b2733", width=2,
                          tags=(tag, "chip"))
            c.create_text(x + 37, y + 37, text=str(v), font=("Segoe UI", -22, "bold"),
                          fill="#ffffff", tags=(tag, "chip"))
            c.create_text(x + 37, y + 86, text=self._hint(len(slots) + i),
                          font=("Segoe UI", -18, "bold"), fill="#12263a")
            chip_xy[v] = [x, y]
            self._bind_key(len(slots) + i, lambda v=v, tag=tag: pick(v, tag))
        sel = {"v": None, "tag": None}

        def pick(v, tag):
            """Keyboard path: pick a chip up, then name the slot it goes into."""
            sel["v"], sel["tag"] = v, tag
            c.itemconfigure("chip", width=2)
            # a tag covers the disc *and* its number, and a text item has no -outline:
            # configuring the tag itself raised TclError, which killed this callback
            # before it could echo what it had picked up
            for it in c.find_withtag(tag):
                if c.type(it) == "oval":
                    c.itemconfigure(it, outline="#101216", width=5)
            self._echo("carrying chip %d - now press a slot key" % v)

        def drop_slot(s):
            v, tag = sel["v"], sel["tag"]
            if v is None:
                self._echo("press a chip key first")
                return
            bx0, by0, bx1, by1 = slot_boxes[s]
            x0, y0, x1, y1 = c.coords(tag)[:4]
            c.move(tag, (bx0 + bx1) / 2 - (x0 + x1) / 2, (by0 + by1) / 2 - (y0 + y1) / 2)
            sel["v"] = None
            want_slot = slots[pair]
            self.finish(v == chips[pair] and s == want_slot,
                        {"chip": v, "slot": s, "want_chip": chips[pair], "want_slot": want_slot})

        drag = {"tag": None, "last": (0, 0)}
        def press(e):
            items = c.find_withtag("current")
            if not items:
                return
            tags = [t for t in c.gettags(items[0]) if t.startswith("c")]
            if not tags:
                return
            drag["tag"] = tags[0]
            drag["last"] = (c.canvasx(e.x), c.canvasy(e.y))
        def move(e):
            tag = drag["tag"]
            if not tag:
                return
            x, y = c.canvasx(e.x), c.canvasy(e.y)
            dx, dy = x - drag["last"][0], y - drag["last"][1]
            drag["last"] = (x, y)
            for item in c.find_withtag(tag):
                c.move(item, dx, dy)
        def drop(e):
            tag = drag["tag"]
            drag["tag"] = None
            if not tag:
                return
            v = int(tag[1:])
            x0, y0, x1, y1 = c.coords(tag)[:4]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            hit = None
            for s, (bx0, by0, bx1, by1) in slot_boxes.items():
                if bx0 <= cx <= bx1 and by0 <= cy <= by1:
                    hit = s
            want_slot = slots[pair]
            self.finish(hit == want_slot and v == chips[pair],
                        {"chip": v, "slot": hit, "want_chip": chips[pair], "want_slot": want_slot})
        c.tag_bind("chip", "<ButtonPress-1>", press)
        c.bind("<B1-Motion>", move)
        c.bind("<ButtonRelease-1>", drop)
        return {"scenario": "t_chips",
                "ask": "drag chip %d into slot %s" % (chips[pair], slots[pair]),
                "truth": {"chip": chips[pair], "slot": slots[pair],
                          "slots": slot_boxes, "chips": chip_xy}}


    # ------------------------------------------------------------- traps ----
    # The adversarial family: every task is built so that the *salient* thing on
    # screen is the wrong one.  Truth comes in two kinds and the app scores both:
    #   answerable  - exactly one legal control exists and the ask names it;
    #   must_refuse - the asked thing is prose, disabled, or absent, so the right
    #                 move is to refuse (F8) rather than click whatever is nearby.
    # 24 tasks = 8 classes x 3 = a smoke test that the target can build these and
    # that refusing is rewardable; it is not a threshold measurement.
    def t_trap(self) -> dict:
        cls, variant = TRAP_PLAN[self.trap_i % len(TRAP_PLAN)]
        self.trap_i += 1
        return getattr(self, "_trap_" + cls)(variant)

    def t_trap2(self) -> dict:
        """Batch 2 of the trap family: >10 tasks per class, the two blind spots split out."""
        cls, variant = TRAP_PLAN2[self.trap_i % len(TRAP_PLAN2)]
        self.trap_i += 1
        return getattr(self, "_trap_" + cls)(variant)

    def t_trap3(self) -> dict:
        """Batch 3: the mouse-channel batch - the visibility boundary and the hard swaps.

        No badge anywhere in the leading class, so this plan is only meaningful with a
        real mouse: Tk ignores posted mouse messages, and a hint key is exactly what the
        class withholds.
        """
        cls, variant = TRAP_PLAN3[self.trap_i % len(TRAP_PLAN3)]
        self.trap_i += 1
        return getattr(self, "_trap_" + cls)(variant)

    def t_trap4(self) -> dict:
        """Batch 4: the self-believed-correct batch (`swap_twin_press` leads).

        Mouse channel, like batch 3: the twin is a heading rather than a hint badge, so
        there is no key that would answer it.
        """
        cls, variant = TRAP_PLAN4[self.trap_i % len(TRAP_PLAN4)]
        self.trap_i += 1
        return getattr(self, "_trap_" + cls)(variant)

    def t_trap5(self) -> dict:
        """Batch 5: batch 4's plan plus the race that lands after the guard's frame.

        Mouse channel, like batch 4: nothing here is answerable through a hint key.
        """
        cls, variant = TRAP_PLAN5[self.trap_i % len(TRAP_PLAN5)]
        self.trap_i += 1
        return getattr(self, "_trap_" + cls)(variant)

    def _trap_task(self, cls: str, variant: str, truth_class: str, want, ask: str,
                   controls: list, scen: str | None = None) -> dict:
        """Arm the refuse key and describe the task; the class builders paint."""
        fixed = self.fixed_scenario or ""
        scen = scen or (fixed if fixed.startswith("t_trap") else "t_trap")
        self.trap_truth, self.trap_want, self.trap_variant = truth_class, want, variant
        # The refuse key belongs to the protocol, not to the answer: it is offered on
        # every trap task, answerable ones included, so its presence on screen says
        # nothing about whether refusing is right here.
        self.keymap[REFUSE_KEY] = self._refuse
        self._echo("%s = skip this task" % REFUSE_KEY)
        return {"scenario": scen, "ask": ask,
                "truth": {"truth_class": truth_class, "want": want, "variant": variant,
                          "class": cls, "controls": list(controls),
                          "refuse_key": REFUSE_KEY}}

    def _refuse(self) -> None:
        """The driver states that no legal control is on screen."""
        self.emit("refused", truth_class=self.trap_truth, want=self.trap_want)
        self.finish(self.trap_truth == "must_refuse",
                    {"refused": True, "want": self.trap_want,
                     "truth_class": self.trap_truth, "variant": self.trap_variant})

    def _trap_press(self, lab: str, truth_class: str, want, variant: str) -> None:
        """A control was used: right only if the ask named it and it was really there."""
        self.finish(truth_class == "answerable" and lab == want,
                    {"clicked": lab, "want": want, "truth_class": truth_class,
                     "variant": variant})

    def _trap_alpha(self, parent, i: int, lab: str, alpha: float, cb) -> tk.Canvas:
        """A control painted `alpha` of the way from the page to the button colour."""
        c = tk.Canvas(parent, width=212, height=58, bg=BG, highlightthickness=0)
        c.create_rectangle(3, 3, 209, 55, fill=blend(BG, "#dbe6f2", alpha),
                           outline=blend(BG, "#8595a8", alpha), width=2)
        c.create_text(106, 29, text=self._hinted(i, lab), font=("Segoe UI", -20),
                      fill="#12263a")
        c.bind("<Button-1>", lambda e: cb())
        return c

    def _trap_faded(self, parent, lab: str, alpha: float, cb, *,
                    operable: bool = True) -> tk.Canvas:
        """A control with no hint badge, painted `alpha` from the page to the button colour.

        Unlike `_trap_alpha` the label is faded by the same fraction, so the outline, the
        fill *and* the text all carry the paint fraction - that is the only shape in which
        a pixel-visibility rule can be the thing under test.  Below OPERABLE_ALPHA the
        click is swallowed and recorded (`ignored_click`) and the task is scored as a
        failure right away: an action on a control that is not really there has to end
        the task, otherwise the batch would sit and wait for a verdict that never comes.
        """
        c = tk.Canvas(parent, width=212, height=58, bg=BG, highlightthickness=0)
        c.create_rectangle(3, 3, 209, 55, fill=blend(BG, "#dbe6f2", alpha),
                           outline=blend(BG, "#8595a8", alpha), width=2)
        c.create_text(106, 29, text=lab, font=("Segoe UI", -20),
                      fill=blend(BG, "#12263a", alpha))

        def clicked(_e=None):
            if operable:
                cb()
            else:
                self.emit("ignored_click", label=lab, alpha=round(alpha, 3))
                self.finish(False, {"ignored_click": True, "clicked": lab,
                                    "want": self.trap_want, "variant": self.trap_variant,
                                    "truth_class": self.trap_truth,
                                    "paint_alpha": round(alpha, 3)})
        c.bind("<Button-1>", clicked)
        return c

    def _trap_buttons(self, labels: list, *, truth_class: str = "answerable", want=None,
                      variant: str = "", disabled=(), flat: bool = False,
                      alpha=None, pick=None) -> dict:
        """A grid of controls; hint keys go to the enabled ones only.

        A disabled control is drawn without a hint on purpose - "no key to press" is
        the honest structural signal that it cannot be operated, and inventing a key
        for it would turn refusing into a guess instead of a reading.
        """
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="both", expand=True)
        cols = 2 if len(labels) <= 4 else 3
        made: dict = {}
        i = 0
        for k, lab in enumerate(labels):
            off = lab in disabled

            def act(L=lab):
                if pick is not None:
                    pick(L)
                else:
                    self._trap_press(L, truth_class, want, variant)

            if alpha is not None and lab == alpha[0]:
                w = self._trap_alpha(grid, i, lab, alpha[1], act)
            else:
                w = tk.Button(grid, text=(self._hinted(i, lab) if not off else lab),
                              font=("Segoe UI", -20), width=15, pady=8,
                              bg=(BG if flat else "#e8eef5"),
                              activebackground="#c9dcf0",
                              relief="flat" if flat else "raised",
                              state=("disabled" if off else "normal"),
                              disabledforeground="#9aa3ad")
                if not off:
                    w.configure(command=act)
            w.grid(row=k // cols, column=k % cols, padx=14, pady=12, sticky="ew")
            if not off:
                self._bind_key(i, act)
                i += 1
            made[lab] = w
        return made

    def _trap_prose_same_word(self, variant: str) -> dict:
        """The asked word sits in the prose; a real control may or may not carry it."""
        rng = self.rng
        word = rng.choice(WORDS).upper()
        decoys = rng.sample([w.upper() for w in WORDS if w.upper() != word], 3)
        tk.Label(self.body, text="press %s to continue" % word, font=("Segoe UI", -18),
                 bg=BG, fg="#3b4048").pack(pady=(6, 2))
        if variant == "prose_only":
            self._trap_buttons(decoys, truth_class="must_refuse", variant=variant)
            return self._trap_task("prose_same_word", variant, "must_refuse", None,
                                   "click the button labelled %s" % word, decoys)
        labels = [word] + decoys
        rng.shuffle(labels)
        self._trap_buttons(labels, want=word, variant=variant)
        return self._trap_task("prose_same_word", variant, "answerable", word,
                               "click the button labelled %s" % word, labels)

    def _trap_two_close_names(self, variant: str) -> dict:
        """Two labels differing only by a numeric suffix - an exact match is required."""
        rng = self.rng
        base = rng.choice(WORDS).upper()
        near = base + str(rng.randrange(10, 99))
        want = rng.choice([base, near])
        labels = [base, near] + [w.upper() for w in rng.sample(
            [w for w in WORDS if w.upper() != base], 2)]
        rng.shuffle(labels)
        self._trap_buttons(labels, want=want, variant=variant)
        return self._trap_task("two_close_names", variant, "answerable", want,
                               "click the button labelled %s" % want, labels)

    def _trap_disabled(self, variant: str) -> dict:
        """The only control carrying the asked label is greyed out and unclickable."""
        rng = self.rng
        word = rng.choice(WORDS).upper()
        decoys = rng.sample([w.upper() for w in WORDS if w.upper() != word], 3)
        tk.Label(self.body, text="%s is not available right now" % word,
                 font=("Segoe UI", -17), bg=BG, fg="#5a6675").pack(pady=(6, 2))
        labels = [word] + decoys
        rng.shuffle(labels)
        self._trap_buttons(labels, truth_class="must_refuse", variant=variant,
                           disabled=(word,))
        return self._trap_task("disabled", variant, "must_refuse", None,
                               "click the button labelled %s" % word, labels)

    def _trap_half_transparent(self, variant: str) -> dict:
        """One control painted at 0.35 / 0.50 / 0.65 - the middle of the threshold."""
        alpha = TRAP_ALPHAS[variant]
        rng = self.rng
        want = rng.choice(WORDS).upper()
        labels = [want] + rng.sample([w.upper() for w in WORDS if w.upper() != want], 3)
        rng.shuffle(labels)
        self._trap_buttons(labels, want=want, variant=variant, alpha=(want, alpha))
        return self._trap_task("half_transparent", variant, "answerable", want,
                               "click the button labelled %s" % want, labels)

    def _trap_flat_button(self, variant: str) -> dict:
        """A real button with no fill of its own: its fill share looks like prose."""
        rng = self.rng
        want = rng.choice(WORDS).upper()
        labels = [want] + rng.sample([w.upper() for w in WORDS if w.upper() != want], 3)
        rng.shuffle(labels)
        self._trap_buttons(labels, want=want, variant=variant, flat=True)
        return self._trap_task("flat_button", variant, "answerable", want,
                               "click the button labelled %s" % want, labels)

    def _trap_no_badge_fill(self, variant: str) -> dict:
        """The asked control is painted faintly and carries no key hint (batch 3).

        Ground truth is the app's own constant, not the driver's pixels: the target is
        operable iff `alpha >= OPERABLE_ALPHA`.  Below it the honest move is to refuse
        (the click is swallowed and scored as a failure); at or above it the honest move
        is to click it.  Decoys are painted at full contrast, so a click on one is a
        plain wrong target.
        """
        rng = self.rng
        alpha = TRAP_FILL_ALPHAS.get(variant, self.control_alpha
                                     if self.control_alpha is not None else OPERABLE_ALPHA)
        want = rng.choice(WORDS).upper()
        decoys = rng.sample([w.upper() for w in WORDS if w.upper() != want], 2)
        labels = [want] + decoys
        rng.shuffle(labels)
        operable = alpha >= OPERABLE_ALPHA
        truth_class = "answerable" if operable else "must_refuse"
        grid = tk.Frame(self.body, bg=BG)
        grid.pack(fill="both", expand=True)
        for k, lab in enumerate(labels):
            def act(L=lab):
                self._trap_press(L, truth_class, want, variant)
            w = self._trap_faded(grid, lab, alpha if lab == want else 1.0, act,
                                 operable=(operable if lab == want else True))
            w.grid(row=k // 2, column=k % 2, padx=14, pady=12, sticky="ew")
        self.emit("paint", variant=variant, alpha=round(alpha, 3), operable=operable,
                  badge=False)
        # The ask must use the driver's one click vocabulary ("click the button labelled
        # X").  Measured in batch 3's first run: the short form "click KILO" parsed into no
        # action at all, so all 28 tasks were refused for a wording reason and the
        # visibility rule was never exercised.  This class measures the paint fraction, not
        # the phrasing, so the phrasing has to be the canonical one.
        return self._trap_task("no_badge_fill", variant, truth_class, want,
                               "click the button labelled %s" % want, labels,
                               scen=self.fixed_scenario or "t_trap3")

    def t_probe_fill(self) -> dict:
        """Calibration-only scenario: one faded, badge-less control at --control-alpha.

        It exists so the visibility curve is measured on *real* app frames instead of
        on hand-drawn approximations; it declares no truth about the driver's rule.
        """
        alpha = self.control_alpha if self.control_alpha is not None else OPERABLE_ALPHA
        lab = self.rng.choice(WORDS).upper()
        box = tk.Frame(self.body, bg=BG)
        box.pack(fill="both", expand=True)
        operable = alpha >= OPERABLE_ALPHA
        truth_class = "answerable" if operable else "must_refuse"

        def act():
            self._trap_press(lab, truth_class, lab, "probe_%.3f" % alpha)

        # the canvas must be *placed*: `_trap_faded` only builds it (the class builders
        # grid it themselves), and an unplaced canvas renders nothing at all - which is
        # what made the first calibration sweep void: every alpha looked identical
        # because the control was never on screen.
        self._trap_faded(box, lab, alpha, act, operable=operable).pack(pady=40)
        self.emit("paint", variant="probe_%.3f" % alpha, alpha=round(alpha, 3),
                  operable=operable, badge=False)
        return self._trap_task("no_badge_fill", "probe_%.3f" % alpha, truth_class, lab,
                               "click %s" % lab, [lab], scen="t_probe_fill")

    def t_probe_fill2(self) -> dict:
        """Calibration-only: the *class's own* stimulus, driven by --control-alpha.

        Curve 1 (`t_probe_fill`) painted a single 5-letter label on an otherwise empty
        body; the class paints three controls from the same word pool in a 2-column grid,
        so the asked label's OCR box carries a different share of text pixels and the same
        alpha measures a different D1 (71 vs 54 on live frames at alpha=0.50).  This
        scenario therefore reuses `_trap_no_badge_fill` verbatim - same painter, same
        layout, same full-contrast decoys - so the curve is measured on the stimulus
        family the batch actually uses.  A variant name outside `TRAP_FILL_ALPHAS` makes
        the painter read `self.control_alpha`.
        """
        return self._trap_no_badge_fill("probe")

    def _trap_synonym(self, variant: str) -> dict:
        """The ask states an intent the prose repeats; the button says something else."""
        rng = self.rng
        intent = rng.choice(["dismiss the notice", "close the notice",
                             "acknowledge the alert"])
        tk.Label(self.body, text="%s to continue" % intent.capitalize(),
                 font=("Segoe UI", -18), bg=BG, fg="#3b4048").pack(pady=(6, 2))
        decoys = [w.upper() for w in rng.sample(WORDS, 2)]
        if variant == "synonym_only":
            self._trap_buttons(decoys, truth_class="must_refuse", variant=variant)
            return self._trap_task("synonym", variant, "must_refuse", None, intent,
                                   decoys)
        real = rng.choice(["Close", "OK"])
        labels = [real] + decoys
        rng.shuffle(labels)
        self._trap_buttons(labels, want=real, variant=variant)
        return self._trap_task("synonym", variant, "answerable", real, intent, labels)

    def _trap_bold_prose(self, variant: str) -> dict:
        """The asked word is big, red and loud - and exists only as prose."""
        rng = self.rng
        word = rng.choice(WORDS).upper()
        tk.Label(self.body, text="PRESS %s NOW" % word, font=("Segoe UI", -40, "bold"),
                 bg=BG, fg="#b3261e").pack(pady=26)
        decoys = rng.sample([w.upper() for w in WORDS if w.upper() != word], 3)
        self._trap_buttons(decoys, truth_class="must_refuse", variant=variant)
        return self._trap_task("bold_prose", variant, "must_refuse", None,
                               "click the button labelled %s" % word, decoys)

    def _trap_swap_mid_task(self, variant: str) -> dict:
        """The screen is re-rolled while the driver works; the last ask counts.

        Both phases stay inside one episode on purpose.  A correct action on the old
        task is recorded (`trap_a_hit`, carried into the verdict as `a_hit`) but does
        not score by itself: that is what separates "the swap did not fluster it" from
        "it answered the question that was on screen a moment ago".

        Two shapes, because they measure different halves of the race:
          `swap_timer` (default) - the swap fires 600-1000 ms after the paint, so with a
              ~1.9 s driver it lands *before* the press: a_hit stays 0 and the question
              is "did it re-read after the change".
          `swap_after_press` - the swap is the *consequence* of pressing A correctly, so
              a_hit is 1 whenever the driver acted on the ask that was on screen.  That
              is the only shape in which the "A was right" half can be observed, and it
              puts the change exactly where a stale plan is most likely to survive: right
              after the driver's own successful action.

        Batch 3 adds the *hard* pair of each shape (`swap_hard_press`, `swap_hard_timer`):
        B differs from A by one glyph, so the driver's band-signature guard cannot see the
        change at all.  The interesting cell is `swap_hard_timer`: a press on the replaced
        ask that is *not* a timing race - the guard simply could not resolve the re-roll -
        which the 600-1000 ms timer alone can never show.

        Batch 4 adds `swap_twin_press`, the shape that can score "A was answered, B was
        not" without the driver ever being confused about *what* the ask says: B's word is
        painted twice - once as the heading above the grid, once on a real button - and the
        heading comes first in reading order, so a text-first driver clicks the word
        instead of the control.  The heading carries a binding purely so the target can
        see that it was clicked: a click on prose is not an answer, so the task is scored
        wrong.  A 9 s watchdog closes the episode if the driver clicks something else
        inert, because a task that never resolves would desynchronise the whole batch.
        """
        rng = self.rng
        hard = variant in ("swap_hard_press", "swap_hard_timer")
        twin = variant == "swap_twin_press"
        if hard or twin:
            want_a, want_b = HARD_PAIRS[rng.randrange(len(HARD_PAIRS))]
            labels = [want_a, want_b] + [w.upper() for w in rng.sample(
                [w for w in WORDS if w.upper() not in (want_a, want_b)], 2)]
        else:
            labels = [w.upper() for w in rng.sample(WORDS, 4)]
            want_a, want_b = labels[0], labels[1]
        ask_a = "click the button labelled %s" % want_a
        ask_b = "click the button labelled %s" % want_b
        st = {"phase": "a", "a_hit": False, "a_miss": 0}
        tok = self.task_i
        after_press = variant in ("swap_after_press", "swap_hard_press",
                                  "swap_twin_press")

        def pick(lab: str) -> None:
            if st["phase"] == "a":
                if lab == want_a:
                    st["a_hit"] = True
                    self.emit("trap_a_hit", label=lab)
                    self._echo("that one is gone now - look again")
                    if after_press:
                        swap("press")     # the change lands on top of its own success
                else:
                    st["a_miss"] += 1
                    self.emit("trap_a_miss", label=lab, want=want_a)
                return
            # `want_b` differs from `want_a` by construction, so pressing A's answer while
            # the screen already asks B is exactly the stale signature.  In the timer shapes
            # the swap landed between the driver's look and its press: `swap_timer` is a
            # timing race (the guard would have caught it, the press won the race),
            # `swap_hard_timer` is guard blindness (one glyph moved, the signature missed it).
            stale = bool(variant in ("swap_timer", "swap_hard_timer", "swap_race_timer")
                        and lab == want_a)
            if stale:
                self.emit("trap_stale_press", label=lab, want=want_b, variant=variant)
            self.finish(lab == want_b,
                        {"clicked": lab, "want": want_b, "truth_class": "answerable",
                         "variant": variant, "a_hit": st["a_hit"], "stale_press": stale})

        def twin_press() -> None:
            """A click on the heading: the word the ask names, but not a control."""
            if self.result != "none" or self.task_i != tok:
                return
            want = want_b if st["phase"] == "b" else want_a
            self.emit("trap_twin_press", label=want_b, phase=st["phase"],
                      a_hit=st["a_hit"])
            self._echo("that is a label, not a button")
            self.finish(False, {"clicked": None, "twin": want_b, "want": want,
                                "truth_class": "answerable", "variant": variant,
                                "a_hit": st["a_hit"], "twin_press": True})

        def twin_watchdog() -> None:
            """Close the episode if nothing answerable was pressed, so the batch stays in sync."""
            if self.result != "none" or self.task_i != tok:
                return
            want = want_b if st["phase"] == "b" else want_a
            self.emit("trap_twin_timeout", phase=st["phase"], a_hit=st["a_hit"])
            self.finish(False, {"clicked": None, "twin": want_b, "want": want,
                                "truth_class": "answerable", "variant": variant,
                                "a_hit": st["a_hit"], "no_press": True})

        def repaint() -> None:
            for ch in self.body.winfo_children():
                ch.destroy()
            # a hint key from the old screen must not fire on the new one; the refuse
            # key is protocol and stays armed across the swap
            for ks in [k for k in self.keymap if k != REFUSE_KEY]:
                self.keymap.pop(ks, None)
            if twin:
                # B's word a second time, as text above the controls: first in reading
                # order, so a driver that ranks words rather than widgets picks the label
                # over the button that carries the same word.
                head = tk.Label(self.body, text=want_b, font=("Segoe UI", -24, "bold"),
                                bg=BG, fg="#2b3440")
                head.pack(pady=(4, 2))
                head.bind("<Button-1>", lambda e: twin_press())
            self._trap_buttons(labels, pick=pick)

        def swap(why: str = "timer") -> None:
            if st["phase"] != "a" or self.result != "none" or self.task_i != tok:
                return
            st["phase"] = "b"
            repaint()
            self.task["ask"] = ask_b
            self.task["truth"]["want"] = want_b
            self.banner.configure(text="DO: " + ask_b)
            self.emit("trap_swap", a=want_a, b=want_b, a_hit=st["a_hit"], why=why,
                      hard=hard)
            self._echo("the task changed - read it again")

        repaint()
        if after_press:
            # A driver that never presses must not hang the class: the safety swap keeps
            # the task moving, and `why` says which of the two paths actually happened.
            self.after(8000, lambda: swap("safety"))
        else:
            # Batch 6 (`swap_race_timer`): the older timer shapes fire 600-1000 ms after
            # the paint, so the driver's pre-press guard frame (~1.4 s in) already sees
            # them and replans - which is why batch 5 measured race 0/0 rather than a
            # lucky miss.  The only window a swap can still win is between that frame and
            # the click, so this variant draws a delay that brackets the driver's own
            # guard time while the driver widens its half with `--press-jitter`.
            lo, hi = (800, 2600) if variant == "swap_race_timer" else (600, 1000)
            self.after(rng.randrange(lo, hi), swap)
        if twin:
            self.after(9000, twin_watchdog)
        return self._trap_task("swap_mid_task", variant, "answerable", want_a, ask_a,
                               labels)



def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=None, help="omit for a random board")
    ap.add_argument("--state", default="gym-state.json")
    ap.add_argument("--events", default="gym-events.jsonl")
    ap.add_argument("--scenario", default=None,
                    help="t_button | t_rows | t_form | t_toggle | t_menu | t_chips | "
                         "t_trap (the adversarial family: its own 24-task batch, so it "
                         "is deliberately not part of the random mix) | t_trap2 (batch 2, "
                         "85 tasks: >=10 per class, swap_after_press and alpha020/030) | "
                         "t_trap3 (batch 3, 71 tasks, mouse channel: the no-badge "
                         "visibility boundary + the hard swaps) | t_trap4 (batch 4, 38 "
                         "tasks, mouse channel: the twin label that scores "
                         "a_hit_but_failed, the hard swaps, a visibility slice) | "
                         "t_trap5 (batch 5, 48 tasks, mouse channel: batch 4's first 38 "
                         "tasks verbatim plus the post-guard race `swap_race_timer`) | "
                         "t_probe_fill (calibration only: one faded no-badge control)")
    ap.add_argument("--gap", type=int, default=250, help="ms between tasks")
    ap.add_argument("--chaos", type=float, default=0.0,
                    help="probability per task of a live change (0..1): the target "
                         "re-rolls its values, shifts, spawns a window, or answers late")
    ap.add_argument("--chaos-ms", default="600,1800",
                    help="delay range (ms) in which that change fires")
    ap.add_argument("--chaos-kind", default="any",
                    choices=["any", "rebuild", "move", "popup", "slow"],
                    help="train one disturbance at a time instead of a random mix")
    ap.add_argument("--no-topmost", action="store_true",
                    help="keep the interference window in the normal z-order, so a "
                         "driver working in background mode can still capture it")
    ap.add_argument("--no-badge", action="store_true",
                    help="paint the faded class without any [k] hint: the control must be "
                         "found from its pixels, not from a key label")
    ap.add_argument("--control-alpha", type=float, default=None,
                    help="force the paint fraction of the faded class (calibration runs)")
    a = ap.parse_args()
    seed = a.seed if a.seed is not None else random.randrange(1, 10 ** 6)
    make_dpi_aware()
    lo, hi = [int(v) for v in a.chaos_ms.split(",")]
    app = Gym(seed, a.state, a.events, a.scenario, a.gap, a.chaos, (lo, hi), a.chaos_kind,
              popup_topmost=not a.no_topmost, no_badge=a.no_badge,
              control_alpha=a.control_alpha)
    print(json.dumps({"event": "start", "seed": seed, "state": a.state,
                      "chaos": a.chaos}, ensure_ascii=False), flush=True)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
