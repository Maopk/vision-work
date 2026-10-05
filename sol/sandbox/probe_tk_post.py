"""Does Tk honour posted window messages at all? Self-contained experiment.

Posts a matrix of mouse/keyboard messages to its own Tk window and prints which
ones came back out as Tk events. Run it with no arguments; nothing is written
outside the window itself.
"""
from __future__ import annotations

import ctypes
import sys
import time
import tkinter as tk

WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0200, 0x0201, 0x0202
WM_CHAR, WM_KEYDOWN, WM_KEYUP = 0x0102, 0x0100, 0x0101
MK_LBUTTON = 0x0001
u = ctypes.windll.user32

log: list[str] = []


def _lp(x: int, y: int) -> int:
    return (y & 0xFFFF) << 16 | (x & 0xFFFF)


def to_client(hwnd: int, x: int, y: int) -> tuple[int, int]:
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    pt = POINT(x, y)
    u.ScreenToClient(ctypes.c_void_p(hwnd), ctypes.byref(pt))
    return int(pt.x), int(pt.y)


def children(hwnd: int) -> list[int]:
    out: list[int] = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def cb(h, _lp_):
        out.append(int(h))
        return True

    u.EnumChildWindows(ctypes.c_void_p(hwnd), WNDENUMPROC(cb), None)
    return out


def main() -> int:
    root = tk.Tk()
    root.title("postprobe")
    root.geometry("320x180+400+300")
    tk.Label(root, text="post me", font=("Segoe UI", -18)).pack(pady=10)
    btn = tk.Button(root, text="PRESS", font=("Segoe UI", -16))
    btn.pack(pady=6)
    ent = tk.Entry(root)
    ent.pack()

    for name, seq in (("Button-1", "<Button-1>"), ("ButtonRelease-1", "<ButtonRelease-1>"),
                      ("Key", "<Key>"), ("Motion", "<Motion>")):
        root.bind_all(seq, lambda e, n=name: log.append("%s@%d,%d" % (n, e.x, e.y)))
    btn.configure(command=lambda: log.append("command:button"))
    ent.bind("<Key>", lambda e: log.append("entry:%r" % e.char))

    hwnd = int(root.winfo_id())
    top = int(ctypes.windll.user32.GetParent(ctypes.c_void_p(hwnd)) or hwnd)
    kids = children(hwnd)
    print("hwnd(winfo_id)=%s  parent=%s  children=%s" % (hwnd, top, kids))

    root.update()
    # keep out of the way: bottom of the z-order, no activation
    u.SetWindowPos(ctypes.c_void_p(hwnd), ctypes.c_void_p(1), 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
    bx, by = btn.winfo_rootx() + 20, btn.winfo_rooty() + 12
    print("button at screen (%d, %d); winfo_id client coords %s" % (bx, by, to_client(hwnd, bx, by)))

    def trial(name: str, send) -> None:
        log.clear()
        send()
        # posted messages are queued: pump the loop long enough to dispatch them
        for _ in range(40):
            root.update()
            time.sleep(0.01)
        print("%-34s -> %s" % (name, log or "NOTHING"))

    tgt = hwnd
    cx, cy = to_client(tgt, bx, by)
    trial("move+down+up to winfo_id",
          lambda: (u.PostMessageW(ctypes.c_void_p(tgt), WM_MOUSEMOVE, 0, _lp(cx, cy)),
                   u.PostMessageW(ctypes.c_void_p(tgt), WM_LBUTTONDOWN, MK_LBUTTON, _lp(cx, cy)),
                   u.PostMessageW(ctypes.c_void_p(tgt), WM_LBUTTONUP, 0, _lp(cx, cy))))
    trial("down+up only",
          lambda: (u.PostMessageW(ctypes.c_void_p(tgt), WM_LBUTTONDOWN, MK_LBUTTON, _lp(cx, cy)),
                   u.PostMessageW(ctypes.c_void_p(tgt), WM_LBUTTONUP, 0, _lp(cx, cy))))
    trial("SendMessage down+up",
          lambda: (u.SendMessageW(ctypes.c_void_p(tgt), WM_MOUSEMOVE, 0, _lp(cx, cy)),
                   u.SendMessageW(ctypes.c_void_p(tgt), WM_LBUTTONDOWN, MK_LBUTTON, _lp(cx, cy)),
                   u.SendMessageW(ctypes.c_void_p(tgt), WM_LBUTTONUP, 0, _lp(cx, cy))))
    trial("WM_CHAR 'k'",
          lambda: u.PostMessageW(ctypes.c_void_p(tgt), WM_CHAR, ord("k"), 0))
    trial("WM_KEYDOWN/UP 'k'",
          lambda: (u.PostMessageW(ctypes.c_void_p(tgt), WM_KEYDOWN, 0x4B, 0),
                   u.PostMessageW(ctypes.c_void_p(tgt), WM_KEYUP, 0x4B, 0)))
    if kids:
        kx, ky = to_client(kids[0], bx, by)
        trial("move+down+up to child",
              lambda: (u.PostMessageW(ctypes.c_void_p(kids[0]), WM_MOUSEMOVE, 0, _lp(kx, ky)),
                       u.PostMessageW(ctypes.c_void_p(kids[0]), WM_LBUTTONDOWN, MK_LBUTTON, _lp(kx, ky)),
                       u.PostMessageW(ctypes.c_void_p(kids[0]), WM_LBUTTONUP, 0, _lp(kx, ky))))
    root.destroy()
    return 0


if __name__ == "__main__":
    sys.exit(main())

