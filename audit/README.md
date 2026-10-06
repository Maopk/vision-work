# audit/ —— 审计档案（2026-10-06 自仓库根迁入）

这 8 份文件原来在仓库根（`STATE.md` / `REPORT.md` / `HANDOFF.md` / `REPORT-draft.md` /
`SCORE-history.md` / `DESIGN-18-scroll-drag.md` / `DESIGN-21-mouse-operability.md` /
`DESIGN-refusal-scoring.md`）。阶段 3.2 用**一次纯 `git mv`** 把它们搬进 `audit/`
（`--stat` = 8 files changed, **0 insertions(+), 0 deletions(-)**，搬迁前后 8 个 blob
逐位相同 ⇒ **文件内部行号零漂移**）。随之只改两样东西：**引用路径**与**行号锚**。

> **根路径 `vision-work/X.md` 已失效**，等价路径是 `vision-work/audit/X.md`。
> 计分板 `SCORE.md` **不随迁**（决策 A），仍在 `../sol/sandbox/`。

## 一、路径怎么写（搬迁后）

| 从哪儿 | 指哪儿 | 写法 |
|---|---|---|
| 根文件（`README.md` / `README.zh-CN.md` / `CHANGELOG.md` / `OPENSOURCE-READINESS.md` / `requirements.txt`） | 档案 | `audit/X.md` |
| 档案 | 根文件 | `../README.md`、`../README.zh-CN.md`、`../CHANGELOG.md`、`../OPENSOURCE-READINESS.md` |
| 档案 | 三件套与证据 | `../sol/sandbox/…`（`gym_run.py`、`score.py`、`t_trap*.json` …） |
| 档案 | 计分板 | 裸 `SCORE.md` = `../sol/sandbox/SCORE.md` |
| 档案 | 同目录兄弟 | 裸名 `X.md`（集内互引 353 行，**本次未动**） |
| 仓库外（`D:\DSH\skills\gui-audit-gym\SKILL.md` 等） | 本仓库档案 | `vision-work/audit/X.md` |

**有意不破的一类**：`sandbox\` 是 `STATE.md` 头部定义的绝对路径简写
（`D:\DSH\vision-work\sol\sandbox\` 的简称）⇒ 12 行不受搬迁影响，本次**未改**
（改了反而与定义行矛盾）。同理，档案里的 Windows / WSL **绝对路径**（`D:\DSH\vision-work\…`、
`/mnt/d/DSH/vision-work/…`）仍然有效，全部保留原样。

## 二、搬迁前的失效清单（五类）

| # | 类别 | 行数 | 处置 |
|---|---|---|---|
| ① | 入站（根文件 → 档案） | 55 | 加 `audit/` 前缀；其中 **49 行**本次可改，**6 行**在 `sol/sandbox/*.py` 注释里（三件套 sha 冻结 ⇒ 不改，留待下次改 `.py` 时同批） |
| ② | 跨边界出站（档案 → 计分板） | 202 | 裸 `SCORE.md` → `../sol/sandbox/SCORE.md`（含 2 行 Windows 反斜杠写法 `sandbox\SCORE.md`） |
| ③ | 跨边界入站（计分板 → 档案） | 38 | 裸名 → `../../audit/X.md`（含 1 处 Windows 绝对路径） |
| ④ | 出站路径（档案 → `sol/sandbox/*`、`README`、`CHANGELOG`） | 68 | 加 `../` 前缀（另有 4 行只写目录名，不破） |
| ⑤ | 仓库外（`SKILL.md` 4 行 + `tmp/stage2` 草案） | 50 | 同批改；`.bak-w5/w10/w13` 备份副本**不改** |
| | **必坏合计** | **412** = 仓内 362 + 仓外 50 | |
| | 仍成立 | 381 = 集内互引 353 + 入站到计分板 20 + 4 + 4 | |

## 三、计数口径（数字只在这里写一次；总纲只引用本节）

```bash
SET8="audit/STATE.md audit/REPORT.md audit/HANDOFF.md audit/REPORT-draft.md audit/SCORE-history.md \
      audit/DESIGN-18-scroll-drag.md audit/DESIGN-21-mouse-operability.md audit/DESIGN-refusal-scoring.md"
PAT='REPORT\.md|REPORT-draft\.md|STATE\.md|HANDOFF\.md|SCORE-history\.md|DESIGN-18-scroll-drag\.md|DESIGN-21-mouse-operability\.md|DESIGN-refusal-scoring\.md|SCORE\.md'

# C1 引用点（行 × 目标）
grep -rIlE "$PAT" . --exclude-dir=.git | xargs grep -cE "$PAT" | awk -F: '{s+=$NF} END{print s}'
# C4 行号引用（token）
grep -rIEoh '(REPORT-draft|REPORT|STATE|HANDOFF|SCORE-history|DESIGN-18-scroll-drag|DESIGN-21-mouse-operability|DESIGN-refusal-scoring|SCORE)\.md:[0-9]+([–-][0-9]+)?' . --exclude-dir=.git | wc -l
# C3 档案内出站路径引用
grep -oh 'sol/' $SET8 sol/sandbox/SCORE.md | wc -l
```

| 量 | 值 | 命令 |
|---|---|---|
| 引用点（行 × 目标） | **714** | C1（搬迁前后逐位相同；3.1 新增的 `requirements.txt` 一行再 +2） |
| 去重引用行 | **457** | C2 |
| 表内行数 | **735** | C1 + C6 + C7 = 714 + 独占用 43 − 自引 22 |
| 档案内出站路径引用 | **77**（只取 8 份 = 72） | C3 |
| 行号引用 | **85 token / 42 承载行**（阶段 3.9 复测） | C4（`check_counts32.sh` 在仓库根执行；阶段 3.2 搬迁时 = **80 / 28**，同一脚本在 `38513c4` 上已是 **80 / 30** ⇒ 旧记录在 3.3–3.5 期间就落后了 2 行） |
| 附录 A 行号 token | **128** | C5 |
| 集内互引 | **353** | C6 |
| 入站（根文件 → 档案） | **54**（记为 55 时含 3.1 的 `requirements.txt` 一行；其中 6 行在冻结的 `.py` 注释里） | C7 |
| 本批必改（仓内） | **362** | C8 |

**上表是阶段 3.2 搬迁时的快照**（只有 C4 在阶段 3.9 用同一脚本复测过）。3.9 复跑得到的其余值是 C1 = 931 / C2 = 601 / C3 = 336（只 8 份 = 331）/ C5 = 103 / C7 = 74 / C8 = 611；它们与快照的差主要来自 3.3–3.9 新增的引用与文档，**但要重写这些行得先修 C5 的命令** —— 它把附录 A 硬编码成 `NR>=360 && NR<=386`，该区间早已随 REPORT 增长而漂移，所以那个 103 不是可信的新值。全表复测列为后续项。

## 四、行号口径

- **行号零漂移**：8 份文件行数逐位未变 —— `STATE.md` 1590 / `REPORT.md` 631 / `HANDOFF.md` 289 /
  `REPORT-draft.md` 139 / `SCORE-history.md` 72 / `DESIGN-18-scroll-drag.md` 272 /
  `DESIGN-21-mouse-operability.md` 156 / `DESIGN-refusal-scoring.md` 435 ⇒ `REPORT.md` 附录 A 的行号
  索引**不需要重算**（`REPORT.md` 的「行号口径」段已按本文件追加 ⑧ 条）。
- **行号锚 → 名字锚**：`actor.py:NNNN` 共 11 处改成名字（`@op('window')`/`o_window`、
  `@op('drag')`/`o_drag`、`@op('scroll')`/`o_scroll`、`Hands.drag()`、`post_drag()`、
  `post_scroll()`、`_maybe_front()`、模块 docstring 的 `Ops:` 行）⇒ 以后改 actor 不再连带这批文档失效。
  **历史豁免**：`CHANGELOG.md` 里的总纲 v1 条目按「不改历史」保留原行号写法与当时的 `**16**` 计数。
- 引用格式：裸 `X.md:NNN` = 本目录（`audit/`）内文件；`../` 前缀 = 出 `audit/` 的仓库内文件；
  `../sol/sandbox/SCORE.md:NNN` = 计分板。
- 复核命令里的 `git grep -nE 'actor\.py:[0-9]' f8604df` 指的是搬迁提交 `f8604df` 的树
  （改写前，10 行命中），用于复现「14 引用行 / 12 个字面量」这个数。
