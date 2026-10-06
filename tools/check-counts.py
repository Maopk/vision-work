#!/usr/bin/env python3
"""The count/inventory gate for `vision-work` (stage 3.7; the `(h)` item of v1.x).

Read-only.  Every *variable* family in the census (`audit/STATE.md` 36.2) gets one
source of truth here, and every place in the repository that *states* that family's
current value is registered as a **claim site**.  The gate recomputes each value from
its source and fails if a claim site disagrees.

  source of truth                        family
  -------------------------------------  -------------------------------------------
  the filesystem                         archive count, front-door docs, layout dirs
  the code (`_SHA_FILES`, `_load_plans`, scenario/version constants)
                                         scripts_sha coverage, manifest entries,
                                         report shape, batch range, gate versions
  a canonical doc section                rule count
  computed at check time                 line-number policy, dual-language numerals

Claim sites are anchored by a **substring, never by a line number** - inserting text
above a claim cannot break the gate, and the gate itself can be documented in the very
files it checks.  A claim site whose anchor matches zero or two+ lines is an error, so
moved or duplicated prose is reported instead of silently passing.

  python tools/check-counts.py            run the gate (exit 0 clean, 1 = drift)
  python tools/check-counts.py --list     print the registry (families + claim sites)

Adding a claim site = one tuple in that family's `claims`.  Adding a family = one dict.
History (batch results, per-stage shas, dated verification records) and design targets
are deliberately **not** gated: see `audit/STATE.md` 36.3 for the criterion that keeps
them out, and 36.6 for what this gate cannot see.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EN = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
      7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
ZH = {0: "零", 1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七",
      8: "八", 9: "九", 10: "十", 11: "十一", 12: "十二"}

# The line-number policy of `audit/REPORT.md` covers these files, in this order.
POLICY_FILES = ["audit/REPORT.md", "sol/sandbox/SCORE.md", "audit/STATE.md",
                "audit/HANDOFF.md", "audit/DESIGN-18-scroll-drag.md",
                "audit/DESIGN-21-mouse-operability.md", "audit/SCORE-history.md",
                "audit/DESIGN-refusal-scoring.md"]

_PROBLEMS: list[str] = []


def _fail(msg: str) -> None:
    _PROBLEMS.append(msg)


_cache: dict[str, list[str]] = {}


def lines(rel: str) -> list[str]:
    if rel not in _cache:
        _cache[rel] = (ROOT / rel).read_text(encoding="utf-8", errors="replace").splitlines()
    return _cache[rel]


def text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


def anchor(rel: str, needle: str) -> str:
    """The single line of `rel` containing `needle` (an error if not exactly one)."""
    hits = [ln for ln in lines(rel) if needle in ln]
    if len(hits) != 1:
        _fail(f"anchor {needle!r} in {rel} matched {len(hits)} lines (want exactly 1)")
        return ""
    return hits[0]


def section(rel: str, start: str, end: str) -> str:
    """The text of `rel` between the line holding `start` and the line holding `end`."""
    body = text(rel)
    i = body.find(start)
    j = body.find(end, i + 1) if i >= 0 else -1
    if i < 0 or j < 0:
        _fail(f"section {start!r}..{end!r} not found in {rel}")
        return ""
    return body[i:j]


# --------------------------------------------------------------- the sources ---
def src_archives() -> int:
    return len([p for p in (ROOT / "audit").glob("*.md") if p.name != "README.md"])


def src_frontdocs() -> list[str]:
    return sorted(p.stem for p in (ROOT / "docs").glob("*.md"))


def src_manifest() -> tuple[int, int]:
    """(plans, entries) straight out of the loader the app itself uses."""
    body = text("sol/sandbox/gym_app.py")
    m = re.search(r"\ndef _load_plans\(.*?(?=\n_PLANS = )", body, re.S)
    if not m:
        _fail("could not extract `_load_plans` from sol/sandbox/gym_app.py")
        return (0, 0)
    ns: dict = {"json": json, "os": os, "_PLANS_PATH": ""}
    exec(m.group(0), ns)                                     # noqa: S102 - our own repo
    plans = ns["_load_plans"](str(ROOT / "sol/sandbox/plans.v1.json"))
    return (len(plans), sum(len(v) for v in plans.values()))


def src_shafiles() -> list[str]:
    m = re.search(r"_SHA_FILES = \(([^)]*)\)", text("sol/sandbox/gym_run.py"))
    if not m:
        _fail("could not read `_SHA_FILES` from sol/sandbox/gym_run.py")
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def src_lines() -> list[int]:
    out = []
    for rel in POLICY_FILES:
        out.append(sum(1 for _ in open(ROOT / rel, encoding="utf-8", errors="replace")))
    return out


def src_batchmax() -> int:
    nums = [int(m.group(1)) for ln in lines("sol/sandbox/SCORE.md")
            for m in [re.match(r"## 批次 (\d+)", ln)] if m]
    return max(nums) if nums else 0


def src_versions() -> list[str]:
    sec = section("audit/SCORE-history.md", "## 1. 四个口径版本", "### 1.1")
    return re.findall(r"\|\s*\*\*(v\d)\*\*\s*\|", sec)


def src_rulecount() -> int:
    sec = section("audit/HANDOFF.md", "## 2. 口径", "## 3. ")
    return len(re.findall(r"^\d+\. ", sec, re.M))


def src_blindspots() -> int:
    sec = section("audit/HANDOFF.md", "## 4. ", "## 5. ")
    return len(re.findall(r"^\d+\. ", sec, re.M))


def src_fiveverdict() -> int:
    hits = 0
    for p in sorted(ROOT.rglob("*.md")):
        if ".git" in p.parts:
            continue
        if "五判定" in p.read_text(encoding="utf-8", errors="replace"):
            hits += 1
    return hits


def src_reportshape() -> tuple[int, int]:
    body = text("audit/REPORT.md")
    return (len(re.findall(r"^## \d+\. ", body, re.M)),
            len(re.findall(r"^## 附录 ", body, re.M)))


def src_topdirs() -> list[str]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout
    except Exception:                                        # not a checkout: fall back
        return sorted(p.name for p in ROOT.iterdir()
                      if p.is_dir() and not p.name.startswith("."))
    return sorted({p.split("/")[0] for p in out.splitlines() if "/" in p})


def src_v1xopen() -> int:
    """`v1.x` 仍开着的项数 = 清单行里**没有被划掉**的条目数。

    自洽检查：这一行自己报一个数，条目就在同一行 —— 数错或忘了划掉都会失败。
    行内条目总是「记号 + 空格」；标题里的 `①③⑥` 不带空格，不当作条目。
    """
    line = next((ln for ln in lines("OPENSOURCE-READINESS.md")
                 if "v1.x 清单（仍开着的欠账" in ln), "")
    if not line:
        _fail("OPENSOURCE-READINESS.md: the v1.x list line is gone")
        return 0
    rows = re.split(r"(?<=[：；。])(?=[①②③④⑤⑥⑦⑧⑨⑩]\s)", line)[1:]
    return sum(1 for r in rows if "~~" not in r)


def src_censusrows() -> int:
    """`§36.2` 普查表里【可变量】家族的行数（同表行数 vs 四处散文里自称的数）。"""
    body = section("audit/STATE.md", "**36.2 普查表**", "**36.3 分类判据**")
    return len(re.findall(r"^\| V\d+ \|", body, re.M))


# --------------------------------------------------------------- the registry ---
CHECKS: list[dict] = [
    {
        "id": "audit-archives",
        "what": "审计档案数（audit/*.md 去掉索引）",
        "value": src_archives,
        "claims": [
            ("README.md", "**Deep reading**", "the {en} audit documents"),
            ("README.zh-CN.md", "**深入阅读**", "{zh}份审计文档"),
            ("audit/README.md", "份文件原来在仓库根", "这 {n} 份文件"),
            ("OPENSOURCE-READINESS.md", "sol/sandbox 三件套", "{n} 份审计文档"),
        ],
        "meta": [("OPENSOURCE-READINESS.md", "审计文档数", "{sites} 处")],
    },
    {
        "id": "front-docs",
        "what": "前门文档数 + 成员清单（docs/*.md）",
        "value": src_frontdocs,
        "claims": [("OPENSOURCE-READINESS.md", "`docs/` 四篇", "{zh}篇")],
        "also": ["members"],
    },
    {
        "id": "manifest-entries",
        "what": "manifest 的表数与条目数（经 `_load_plans` 展开）",
        "value": src_manifest,
        "claims": [
            ("audit/STATE.md", "**35.1 一句话**", "{n} 个 `(class, variant)`"),
            ("audit/STATE.md", "**35.4 等价性闸", "**{n}/{n}**"),
            ("CHANGELOG.md", "**Stage-3.6a", "**{n}** `(class, variant)` entries"),
            ("OPENSOURCE-READINESS.md", "3.6 ✅", "{n} 个 `(class, variant)` 逐元组等价"),
            ("docs/TASK-AUTHORING.md", "offline equivalence check", "The {n} entries"),
            ("audit/REPORT.md", "`trap5` 写成 `base: trap4`", "{n} 个 `(class, variant)` 逐元组等价"),
        ],
        "literals": ["266"],
    },
    {
        "id": "sha-files",
        "what": "`scripts_sha` 覆盖清单（真源 = 代码里的 `_SHA_FILES`）",
        "value": src_shafiles,
        "claims": [
            ("audit/STATE.md", "**35.5 `scripts_sha` 扩容**", None),
            ("sol/sandbox/SCORE.md", "批次 1–24 用的是三文件定义", None),
            ("audit/SCORE-history.md", "新（六文件）", None),
        ],
        "also": ["members"],
    },
    {
        "id": "rule-count",
        "what": "引用规则条数（真源 = `audit/HANDOFF.md` §2 的条目数）",
        "value": src_rulecount,
        "claims": [("docs/OPERATING.md", "### 3.2 引用规则", "{zh}条")],
        "also": ["operating-list"],
    },
    {
        "id": "blindspot-count",
        "what": "已知盲区条数（真源 = `audit/HANDOFF.md` §4 的条目数）",
        "value": src_blindspots,
        "claims": [("docs/OPERATING.md", "条已知盲区", "{n} 条已知盲区")],
    },
    {
        "id": "line-policy",
        "what": "行号口径（真源 = 各文件实际行数，顺序即口径顺序）",
        "value": src_lines,
        "claims": [],
        "also": ["report-line-policy"],
    },
    {
        "id": "batch-range",
        "what": "批次区间上界（真源 = `SCORE.md` 的 `## 批次 N` 最大号）",
        "value": src_batchmax,
        "claims": [
            ("audit/HANDOFF.md", "# 交接页", "批次 1–{n}"),
            ("audit/HANDOFF.md", "三文件**（批次", "批次 1–{n}"),
            ("sol/sandbox/SCORE.md", "批次 1–24 用的是三文件定义", "批次 1–{n}"),
        ],
    },
    {
        "id": "gate-versions",
        "what": "口径版本数（真源 = `SCORE-history.md` §1 的版本表）",
        "value": src_versions,
        "claims": [
            ("README.md", "measurement gates are versioned", "(v0–{last})"),
            ("README.zh-CN.md", "测量 gate 是带版本的", "（v0–{last}）"),
        ],
    },
    {
        "id": "report-shape",
        "what": "成文结构（真源 = `audit/REPORT.md` 的章节与附录标题）",
        "value": src_reportshape,
        "claims": [
            ("README.md", "chapters + ", "{ch} chapters + {ap} appendices"),
            ("README.zh-CN.md", "章 + ", "{ch} 章 + {ap} 附录"),
        ],
    },
    {
        "id": "five-verdict-files",
        "what": "集合名 `五判定` 的文件数（口径写在宣称点旁边：含本文件）",
        "value": src_fiveverdict,
        "claims": [("OPENSOURCE-READINESS.md", "五判定` 这个**集合名**", "**{n}** 个 `*.md`")],
    },
    {
        "id": "dual-language",
        "what": "双语 README 的数字多重集相等",
        "value": lambda: None,
        "claims": [],
        "also": ["dual-language"],
    },
    {
        "id": "layout-dirs",
        "what": "顶层目录在双语 `## Layout` 里都在（提及的路径必须存在）",
        "value": src_topdirs,
        "claims": [],
        "also": ["layout"],
    },
    {
        "id": "v1x-open-items",
        "what": "`v1.x` 仍开着的项数（自称数 vs 同一条目行里未划掉的行数；一致性检查）",
        "value": src_v1xopen,
        "claims": [
            ("OPENSOURCE-READINESS.md", "v1.x 清单（仍开着的欠账", "**{n}** 项"),
            ("audit/STATE.md", "v1.x 清单补上缺的", "**{n}** 项"),
        ],
    },
    {
        "id": "census-rows",
        "what": "`§36.2` 普查表里【可变量】家族的行数（四处散文自称的数必须等于表里的行数）",
        "value": src_censusrows,
        "claims": [
            ("audit/STATE.md", "**36.1 一句话**", "**{n}** 个【可变量】家族"),
            ("audit/STATE.md", "只覆盖 §36.2 表里登记的", "**{n}** 个【可变量】家族"),
            ("docs/OPERATING.md", "- **管什么**", "**{n}** 个【可变量】家族"),
            ("OPENSOURCE-READINESS.md", "普查 → ", "**{n}** 个【可变量】家族"),
        ],
    },
]


# ------------------------------------------------------------------- checking ---
def fmt(tmpl: str, val, bound: dict) -> str:
    return tmpl.format(n=val if not isinstance(val, (list, tuple)) else "",
                       en=EN.get(val, val) if isinstance(val, int) else "",
                       zh=ZH.get(val, val) if isinstance(val, int) else "",
                       sites=bound.get("sites", ""), list=bound.get("list", ""),
                       ch=bound.get("ch", ""), ap=bound.get("ap", ""),
                       last=bound.get("last", ""))


def check_family(chk: dict) -> None:
    cid, val = chk["id"], chk["value"]()
    bound: dict = {}
    if cid == "front-docs":
        val, names = len(val), val
        bound["names"] = names
    if cid == "manifest-entries":
        bound["plans"], val = val[0], val[1]
    if cid == "sha-files":
        bound["list"] = " + ".join(f"`{f}`" for f in val)
        bound["names"] = val
    if cid == "gate-versions":
        bound["last"] = val[-1] if val else "?"
        val = len(val)
    if cid == "report-shape":
        bound["ch"], bound["ap"] = val
        val = None
    for rel, needle, tmpl in chk["claims"]:
        ln = anchor(rel, needle)
        if not ln:
            continue
        if tmpl is not None:
            want = fmt(tmpl, val, bound)
            if want not in ln:
                _fail(f"{cid}: {rel} [{needle}] lacks {want!r}")
        if "members" in chk.get("also", []) and cid in ("front-docs", "sha-files"):
            for name in bound["names"]:
                if name not in ln:
                    _fail(f"{cid}: {rel} [{needle}] does not name {name!r}")
    for rel, needle, tmpl in chk.get("meta", []):
        sites = len(chk["claims"])
        ln = anchor(rel, needle)
        if ln and fmt(tmpl, None, {"sites": sites}) not in ln:
            _fail(f"{cid}: {rel} [{needle}] lacks the claim-site count {sites}")


def check_operating_list() -> None:
    sec = section("docs/OPERATING.md", "### 3.2 引用规则", "### 3.3")
    got = len(re.findall(r"^\d+\. ", sec, re.M))
    want = src_rulecount()
    if got != want:
        _fail(f"rule-count: docs/OPERATING.md §3.2 lists {got} rules, HANDOFF §2 has {want}")


def check_report_line_policy() -> None:
    ln = anchor("audit/REPORT.md", "**行号口径**")
    if not ln:
        return
    i, j = ln.find("行号按"), ln.find("；后两份")
    if i < 0 or j < 0:
        _fail("line-policy: cannot slice REPORT's policy line")
        return
    got = [int(m.group(1)) for m in re.finditer(r"\*{0,2}(\d{2,4})\*{0,2} 行", ln[i:j])]
    want = src_lines()
    if got != want:
        for rel, g, w in zip(POLICY_FILES, got + [None] * 9, want):
            if g != w:
                _fail(f"line-policy: {rel} = {w} lines, REPORT says {g}")


def check_dual_language() -> None:
    en = sorted(re.findall(r"\d+", text("README.md")))
    zh = sorted(re.findall(r"\d+", text("README.zh-CN.md")))
    if en != zh:
        only_en = [x for x in en if x not in zh]
        only_zh = [x for x in zh if x not in en]
        _fail(f"dual-language: README.md numerals {only_en} vs README.zh-CN.md {only_zh}")


def check_layout() -> None:
    for rel in ("README.md", "README.zh-CN.md"):
        body, blk = text(rel), ""
        m = re.search(r"## (?:Layout|目录)\n\n```\n(.*?)```", body, re.S)
        if not m:
            _fail(f"layout: no layout block in {rel}")
            continue
        blk = m.group(1)
        for d in src_topdirs():
            if not re.search(rf"(?m)^{re.escape(d)}/", blk):
                _fail(f"layout: {rel} does not list the top-level directory {d}/")
        for hit in re.findall(r"(?m)^([A-Za-z0-9._/-]+/[A-Za-z0-9._/-]+)", blk):
            if not (ROOT / hit).exists():
                _fail(f"layout: {rel} names {hit}, which does not exist")


def check_literals() -> None:
    """`266` is distinctive enough to police the *other* direction: no unregistered site."""
    for chk in CHECKS:
        for lit in chk.get("literals", []):
            site = {rel for rel, _, _ in chk["claims"]}
            for p in sorted(ROOT.rglob("*.md")):
                if ".git" in p.parts:
                    continue
                rel = str(p.relative_to(ROOT))
                if lit in p.read_text(encoding="utf-8", errors="replace") and rel not in site:
                    _fail(f"literals: {rel} states {lit} but is not a registered claim site")


def main() -> int:
    if "--list" in sys.argv:
        for chk in CHECKS:
            print(f"{chk['id']:20s} {chk['what']}")
            for rel, needle, tmpl in chk["claims"]:
                print(f"{'':20s}   claim  {rel}  [{needle}]  -> {tmpl}")
            for rel, needle, tmpl in chk.get("meta", []):
                print(f"{'':20s}   meta   {rel}  [{needle}]  -> {tmpl}")
            for extra in chk.get("also", []):
                print(f"{'':20s}   check  {extra}")
        return 0
    for chk in CHECKS:
        check_family(chk)
    check_operating_list()
    check_report_line_policy()
    check_dual_language()
    check_layout()
    check_literals()
    for p in _PROBLEMS:
        print("DRIFT " + p)
    print(f"{len(CHECKS)} families, {len(_PROBLEMS)} problem(s)")
    return 1 if _PROBLEMS else 0


if __name__ == "__main__":
    raise SystemExit(main())
