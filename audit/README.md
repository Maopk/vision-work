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
# C4 行号引用（token / 承载行 —— 两数同源 = 同一个 $PAT9；⑧c 起改 git grep，克隆可复现）
PAT9='(REPORT-draft|REPORT|STATE|HANDOFF|SCORE-history|DESIGN-18-scroll-drag|DESIGN-21-mouse-operability|DESIGN-refusal-scoring|SCORE)\.md:[0-9]+'
git grep -IohE "$PAT9" | wc -l
git grep -IlE "$PAT9" | xargs grep -cE "$PAT9" | awk -F: '{s+=$NF} END{print s}'
# C3 档案内出站路径引用
grep -oh 'sol/' $SET8 sol/sandbox/SCORE.md | wc -l
```

**本表数据点定义不同**：C4 = **⑧c（2026-10-06）复测**；C1/C2 = 3.1 末**本机口径**；其余 = 阶段 3.2 快照。复跑值见表下注（含已知项：**C5 已按节边界重写 = 136**、旧 128 / 103 一并作废，见注 6；C8 的 362 ≠ 541）—— **勿混引**。

| 量 | 值 | 命令 |
|---|---|---|
| 引用点（行 × 目标） | **714**（= 3.1 末**搬迁前本机口径**值；干净树 = **713**） | C1（**E1**；3.1 新增的 `requirements.txt` 一行再 +2）＋ **E8**：**+214 = 3.2 自身 +40 + 3.3–3.9 +175**（最大单步 = 3.7 的 **+68** = 新闸脚本引用 38 行 + STATE 普查表）；原记「搬迁前后逐位相同」**不成立** |
| 去重引用行 | **457**（= 3.1 末**搬迁前本机口径**值；干净树 = **455**） | C2（**E2**） |
| 表内行数 | **735** | C1 + C6 + C7 = 714 + 独占用 43 − 自引 22 |
| 档案内出站路径引用 | **77**（只取 8 份 = 72） | C3 |
| 行号引用 | **85 token / 32 承载行**（**⑧c · 2026-10-06** 复测；**两数同源** = 同一个 9 名正则，两条命令见注 9） | C4（**旧 42 是混合口径**：「按 9 名选文件、再按任意 `.md:NNN` 数行」，今天量得 **44**、与 85 不同源 ⇒ 弃用；阶段 3.2 搬迁时 = **80 / 28**，同一脚本在 `38513c4` 上已是 **80 / 30** ⇒ 旧记录在 3.3–3.5 期间就落后了 2 行） |
| 附录 A 行号 token | **136**（**⑧b · 2026-10-06** 按节边界重写后；旧 128 / 103 作废） | C5（**新定义 = 按标记切**：`## 附录 A` 标题之后 → 下一个 `## ` 之前；附录 A 今天在第 **368–396** 行，命令见注 6） |
| 集内互引 | **353** | C6 |
| 入站（根文件 → 档案） | **54**（记为 55 时含 3.1 的 `requirements.txt` 一行；其中 6 行在冻结的 `.py` 注释里） | C7（**口径待重写**：清单 7 文件、窄于全树） |
| 本批必改（仓内） | **362**（≠ 现行 C8 命令在 3.2 树上的 **541**；**E9**） | C8（**口径待重写**：命令写死 16 个文件，今天至少漏 **89 行**引用） |

**上表是阶段 3.2 搬迁时的快照**（只有 C4 复测过：阶段 3.9 与 ⑧c）。3.9 复跑得到的其余值是 C1 = 931 / C2 = 601 / C3 = 336（只 8 份 = 331）/ C5 = 103（**已由 ⑧b 作废**，见注 6）/ C7 = 74 / C8 = 611；它们与快照的差主要来自 3.3–3.9 新增的引用与文档。**引用前必读下面九条**（E1–E9，2026-10-06 逐 commit 复核；判定 = 树变，口径未变）：

1. **E1 / E2（C1 / C2 的口径）**：714 / 457 是 **3.1 末（搬迁前）的「本机口径」值** —— 不是今天的值，也不是干净树的值。同一脚本在三棵树上的读数：3.1 末（`34de029`）**713 / 455** → 3.2 末（`145c093`）**753 / 471** → 现行 HEAD（`2482e62`）**928 / 598**。
2. **本机口径 +1～+3**：`grep -rIlE … .` 会把**未跟踪的本机文件**算进去 ⇒ 本机口径值随本机残留文件而变（实测 +1～+3）。今天多出的 **+3** 来自两个被 `.gitignore` 忽略、不在 HEAD 里的文件（`sol/sandbox/audit_runs.py` 2 行、`sol/sandbox/find_run.py` 1 行）⇒ **从克隆复现只能得到干净树值**（928 / 598）。
3. **E7（脚本口径）**：C1 / C2 建议改成 **`git ls-files` 驱动**（只数受版本控制的文件，克隆即可复现）；现行 `grep -r` 写法没有这个性质。C7 的 7 文件清单同样窄于全树（未含 `docs/*`、`audit/README.md`、`tools/*`、`gui_see.py`、`loop.py`）。
4. **E8（「搬迁前后逐位相同」不成立）**：3.1 末干净树 **713** → 3.2 末干净树 **753**（**+40**）。搬迁本身不改内容（8 个 blob 逐位相同、行数零漂移），但**同一阶段**新建了 `audit/README.md`（贡献 **32** 个引用点）并追加了 `CHANGELOG.md`（**8** 行）⇒ 搬迁后的第一次测量就已经不是 714。
5. **+214 的归因 = 树变，不是口径变**：两代脚本（3.1 版 `check_counts.sh` / 3.2 版 `check_counts32.sh`，均在仓库外 `D:\DSH\dsh-actor\tmp\stage3\`）的 C1 / C2 段**逐字相同**，`diff` 只有 `SET8` 与 C5 两行 ⇒ 排除「grep 口径变」；脚本也不在 git 里，故 3.2 当时的版本以这两份 tmp 脚本为准。逐段增量：3.3 **+34** / 3.4 **+12** / 3.5 **+11** / 3.6 **+31** / 3.7 **+72**（其中提交 `e2251b6` 一步 **+68**）/ 3.9 **+15**。贡献最多的五个文件：`audit/STATE.md` **+44**、`tools/check-counts.py` **+38**（3.7 新建）、`docs/OPERATING.md` **+27**（3.3 新建）、`audit/REPORT.md` **+16**、`CHANGELOG.md` **+15**。
6. **C5（⑧b · 2026-10-06 已重写）**：旧命令把附录 A 硬编码成 `NR>=360 && NR<=386` —— 该窗口已错位（从附录 A **前 8 行**起、到附录 A **内部 12 行**止；附录 A 现自 **`:368`** 起、到 **`:396`** 止）⇒ 复跑的 **103 既不是附录 A 的 token 数、也不是旧值 128 的新版本**，两者一并作废。**新定义 = 按标记切**（`附录 A` 标题之后 → 下一个 `## ` 之前），复算 = 一条命令：`awk '/^## 附录 A/{f=1;next} /^## /{f=0} f' audit/REPORT.md | grep -oE ':[0-9]+([–-][0-9]+)?' | wc -l` = **136**。**与旧值不可比**（切法不同，树也变了）。
7. **C7b（口径待重写）**：`C7b` 的 6 文件清单里**有两个不在 HEAD 里**的文件（`sol/sandbox/audit_runs.py`、`sol/sandbox/find_run.py`）⇒ 干净树里它们根本不存在，读数不可复现。
8. **E9（C8 的 362 ≠ 541）**：在干净的 3.2 末树上跑**现行 C8 命令**得 **541**，表里的 **362** 与它不同源（362 出自迁移分析的语义计数：「必坏合计 412 = 仓内 362 + 仓外 50」）。现行命令还写死 16 个文件，今天至少漏 **89 行**引用（`tools/check-counts.py` 34 / `docs/OPERATING.md` 23 / `audit/README.md` 15 / `docs/TASK-AUTHORING.md` 6 / `docs/QUICKSTART.md` 4 / `docs/TROUBLESHOOTING.md` 3 / 两个本机文件 3 / `requirements.txt` 1）⇒ **口径待重写**，引用 362 时必须连这句一起引。
9. **引用状态**：**C1 / C2 可以引用，但必须带口径**（说清是「本机口径」还是「干净树」、以及是哪一棵树）；**C4** 按 **⑧c（2026-10-06）**复测的 **85 token / 32 承载行**引（**两数同源** = 同一个 `$PAT9` 的两条命令：`git grep -IohE "$PAT9" | wc -l` = **85**、`git grep -IlE "$PAT9" | xargs grep -cE "$PAT9" | awk -F: '{s+=$NF} END{print s}'` = **32**，`$PAT9` 见 §三；`git grep` 只数受版本控制的文件 ⇒ 克隆即可复现，旧 42 的混合口径已弃用）；**C7 / C7b / C8 维持「口径待重写」**（C5 已重写 = **136**，见注 6），引用前先重写命令；C3 / C6 / C7 / 表内行数（735）仍是 **3.2 快照**。**全表复测正在分段进行**（⑧c C4 ✅ → ⑧b C5 ✅；余 ⑧a = C1 / C2 改 `git ls-files` 驱动 + C6 补定义 + 表内行数、⑧d = C7 / C7b / C8、⑧e = 标签家族）。


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
