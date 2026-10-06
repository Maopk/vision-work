# 三仓库开源就绪 · 总纲 v1.1（**试点回灌后** · 试点 → 上游 → 下游）

> 状态：**只定标准与顺序，不改任何仓库的内容**（v1 写于 2026-10-05；**v1.1 = 试点回灌**：阶段 1（`dsh-termux-kit`）的产出按第 5 节的「试点必须回灌」条款并入本文档 —— (c)(d) 两处措辞修正、新增标准 (h)、两条示范句成文、发布通道与 sha 记录成文、新增第 8 节试点记录摘要）。
> **本文件是独立提交，不属于阶段 1 试点段**：试点段自己的改动（两份 README、`docs/TASK-AUTHORING.md`、`PILOT-FEEDBACK.md`、CHANGELOG）留在那个仓库里、**尚未发布**；回灌只改本文档 + 本仓库 `CHANGELOG.md`。
> 数据来源可复核：远端文件数/内容用**无凭据** GitHub API + `raw.githubusercontent.com` 实测；本地 dirty/行号用 `git status` / `sha256sum` / `wc -l`。

## 0. 基线（实测，不是回忆）

| 仓库 | 单元 | 远端 branch | 远端文件数 | 本地 HEAD | 工作树 | 本地 vs 远端 |
|---|---|---|---|---|---|---|
| `Maopk/dsh-termux-kit` | **B 独立** | `master` | 158 | **非 git 仓**（本地副本 `D:\DSH\dsh-termux-kit-copy`，走 `publish.ps1` / Contents API） | — | `README.md` / `CHANGELOG.md` sha256 **相同** |
| `Maopk/dsh-vision-kit` | **A 上游** | `main` | 50（`actor/` **11**） | `1e3cff6` | **dirty = 1**：`actor/actor.py` `+325 / −16` | README/CHANGELOG 相同；**`actor/actor.py` 不同** |
| `Maopk/vision-work` | **A 下游** | `main` | 116（`sol/` 102；v1 新增本文档 ⇒ 115 → 116） | `28b9cad`（本表基线取自 v1.1 提交前） | clean | 一致 |

**最硬的一条事实**：`actor/actor.py` 远端 `sha256(16) = 4cfb87076604900e`，本地工作树 `fce8caa21ce0ed58`（2910 行）。
⇒ **本地在跑的执行器是一个未发布版本**（`--keys --bg` 与 `t_rows` 键通道的滚轮等价物都依赖那 325 行）。任何"下游文档引用 actor"的动作，在发布之前都是**引用一个不存在的版本** —— 这正是终止条件 ①「引用了不存在的上游版本」当前所处的状态，也只是**待触发**，不是已违反。

**三种发布通道（标准必须照顾到）**：`dsh-termux-kit` = `publish.ps1`（git-data API，无本地 git 历史）；`dsh-vision-kit` / `vision-work` = 本地 git 直推 `main`。三条通道对「sha 记录」的影响见 §4「(d 配套)」。

## 1. 两单元关系图

```
单元 A（有依赖，方向单向，不可同批改）
    [dsh-vision-kit]  ──── 运行时硬依赖 ────▶  [vision-work]
     Windows PC Actor（127.0.0.1:8731）        GUI Agent 行为审计靶场
     actor/ 11 文件 · main 50 文件              sol/sandbox 三件套 + 8 份审计文档
          ▲
          │  信用引用（非依赖、无代码耦合）
          │  dsh-vision-kit/README.md:258「plugin is a fork of `dsh-selflook-local`
          │  from Maopk/dsh-termux-kit」
单元 B（独立）
    [dsh-termux-kit]   Termux/Android 运维包（158 文件）
    不引用 A 的任何内容；A 也不依赖 B
```

**引用方向实测（`*.md`，含行号的硬命中）**

| 方向 | 处数 | 样例 |
|---|---|---|
| vision-work → dsh-vision-kit | **14 引用行 / 12 个字面量**（原记 16；复核 `git grep -nE 'actor\.py:[0-9]' f8604df` = 10 行 + `audit/HANDOFF.md` 第 180 行的裸行号 + 3 处同行多锚；字面量表见本仓库 `CHANGELOG.md` 的 3.2 条目） | `CHANGELOG.md:16`、`audit/DESIGN-18-scroll-drag.md:73 / :152 / :264`、`audit/HANDOFF.md:62 / :177 / :194`、`audit/REPORT-draft.md:6` |
| dsh-vision-kit → vision-work | **0** | 无 |
| dsh-vision-kit → dsh-termux-kit | **4** | `README.md:183`（"Following the upstream dsh-termux-kit convention"）、`README.md:291`（fork 来源）、`README.zh-CN.md:166 / :259`（现行行号；2.2 的「Why」章与 zh-CN 重同步各插入一次，原 150 / 258 / 112 / 205 已过期） |
| dsh-termux-kit → A（kit/work） | **0** | grep `actor` 的 10 条命中全是 `refactor` 子串 |

⇒ 单元 A 的耦合**只有一条**（actor 运行时），单元 A↔B 的耦合**只有一条**（fork 信用）。两者都不是"见另一仓库"式含糊引用，而是可核对的具体指向 —— 这一点已经合格，要保住的只是它别退化。

## 2. "同一份"与"各仓库独有"清单

**跨仓库共享的同一份（一份物理副本、多方消费）**

| 内容 | 唯一副本在哪 | 谁消费 | 怎么断 |
|---|---|---|---|
| actor op 协议（23 op · `127.0.0.1:8731` · 换行 JSON） | `dsh-vision-kit/actor/actor.py` | vision-work 运行时（`sol/sandbox/loop.py:48-53`）+ 14 行 / 12 个字面量的**行号**引用（3.2 已改名字锚：`@op('window')`/`o_window`、`@op('drag')`/`o_drag`、`Hands.drag()`、`post_drag()`、`_maybe_front(req)`；复核见 `audit/README.md` §行号口径） | 改 actor 一行 ⇒ 下游**读数层**仍失效（读数层不受名字锚保护）；**文档不再随之失效**（3.2 已改名字锚） |
| actor HOME 与端口文件（`D:\DSH\dsh-actor\port.txt`） | **仓库外**（运行环境） | 两个仓库都靠它 | 环境不落盘 ⇒ 陌生人起不来 |
| 插件 fork 来源（`dsh-selflook-local`） | `dsh-termux-kit`（历史组件） | vision-kit README 的信用引用（4 处） | 组件改名/搬迁 ⇒ 引用悬空 |
| 写作权威（提交前缀 + 禁用词表 + 术语表） | `dsh-termux-kit/CONTRIBUTING.md`、`docs/术语表.md` | **实际约束三个仓库** | 权威只在一个仓库里却管三个 ⇒ 另两个引用它时必须带 commit |
| 双语 README 对、CHANGELOG、MIT、ruff/mypy 配置 | 三仓库各自一份（**同约定、非同文件**） | 三仓库 | 新仓库加入时缺项 |

**各仓库独有（不共享，也不要假装共享）**

- `vision-work`：靶子 `ready`/`verdict` 协议、六判定与 `truth_class` 门、`[k]` 徽章约定、欠账/可比性纪律（`audit/SCORE-history.md`）、批次证据 JSON（`sol/` 102 文件）。
- `dsh-vision-kit`：actor 实现、UIA/视觉工具、插件包（`plugins/`）、Generation 1 截图路线。
- `dsh-termux-kit`：Termux 工具（`tools/` 52）、两个 Android app（`apps/` 33）、12 个 widget（`widgets/` 14）、`ui/controls.json` **一源三面**（面板/控制台/桥）。

**三处"仓库外的副本"**（都不在任何仓库里 ⇒ 违反标准 e 或不落盘 ⇒ 违反 b/c；**第 1 条已在阶段 3.3 解决**，仍存在 2 处）

1. ~~`D:\DSH\skills\gui-audit-gym\SKILL.md`~~ —— **已解决（阶段 3.3）**：规程正本入库为 `vision-work/docs/OPERATING.md`，仓库外那份技能降为**指针**（只留 frontmatter + 一页指向正本的顺序清单，不再复制正文；前门也不再指向它）。
2. `D:\DSH\dsh-actor\`（actor HOME：`port.txt` / `home.txt` / `logs/`）。
3. `D:\DSH\.venvs\vision-ci` + Tesseract 安装（**阶段 3.1 起不再是代码里的死路径**：`gui_see.py` 读 `TESS`（别名 `TESSERACT`）、作者安装路径只作最后兜底，找不到就停并打印"设 `TESS=<…>`"；本机仍需装它，但那是**环境**、可按 `docs/QUICKSTART.md` 的说法复现）。

## 3. 影响清单（改谁会影响谁）

| 改动 | 影响面 | 影响方式 | 本总纲的处置 |
|---|---|---|---|
| 发布/修改 `actor.py`（单元 A 上游） | vision-work：运行时 **+** 14 引用行 / 12 个字面量 | 行为变 ⇒ 旧批读数不可比（**文档行号不再随上游漂移**：3.2 已把 11 处 `actor.py:NNNN` 改成名字锚） | 上游发布单独成段；发布后**逐条核 14 引用行**（模板第 4 格） |
| vision-work 搬迁审计档案（`audit/`） | 自身 **714 引用点 / 457 行 / 735 行（表内）** 交叉引用 + README/HANDOFF 指向 | 路径/行号漂移 | ✅ **已搬迁（3.2）**：搬迁**前**先列失效清单 **412** 处（入站 55 + 跨边界出站 202 + 跨边界入站 38 + 出站路径 68 + 仓库外 50 = 仓内 362 + 仓外 50；仍成立 381）；`git mv` 逐 blob 相同、**行数零漂移**；逐类改写与计数口径见 `audit/README.md` |
| vision-work 改三件套 | 自身 sha 表、跨批可比性、`scripts_sha` | 一次 sha 裂 = 一次可比性代价 | **原计划"合并成一次"（manifest v1 + A）已改为只落 A（阶段 3.4）**：A 是**语义**变更（新真值类 `viewport`），manifest 是**结构**变更而它的验收判据恰是"题序一字未变" —— 同批会让两类变化都不可归因，且本段不许跑批 ⇒ manifest v1 只设计（`docs/TASK-AUTHORING.md` §5），实现另起一段并**接受第二次 `gym_app.py` sha 裂** |
| 调整 vision-kit 插件目录 / README 结构 | 它自己指向 termux 的 4 处信用引用 | 被引用目标改名 ⇒ 空指针 | 动 vision-kit 前先确认 termux 侧路径稳定 |
| 改 termux-kit 的 `ui/controls.json` | 面板 + 控制台 + 桥 + 12 widget + `dsh-kit-update` | 单源改动三面同变（**优点**，也是"改一处动三面"） | 试点段只动**前门**，不碰 `controls.json` |
| 三仓库共同约定（双语对 / CHANGELOG / commit 前缀 / MIT） | 三仓库 | 缺一项就不齐 | 写进标准 (g) 与模板第 2 格 |

## 4. 共同标准八条（成文；v1.1 回灌后从七条增至八条）

### (a) 前门必须回答三问（动机 / 上手 / 加题）

| 仓库 | ① 这是什么、我为什么需要 | ② 10 分钟跑起来 | ③ 怎么加 / 扩 |
|---|---|---|---|
| `dsh-termux-kit` | ✅ `README.md` 的 `## Overview` | ✅ 其 `## Quick start`（4 步；缺 `android.jar` 时**停下并打印指令**） | ⚠ 有 12 个 widget 的清单与 `ui/controls.json` 单源，但**没有"加第 13 个 widget / 加一条命令"的路径** ⇒ 阶段 1 已补：见 §8 |
| `dsh-vision-kit` | ⚠ 无独立 Why 章；`:14 The current path: the PC Actor` 标了当前路线 | ✅ `:22 Quick start`（"nothing to install first"） | ⚠ 有 `:83 Skills`，但 Generation 1（`:103`）/ 1.5（`:200`）/ Actor **三代并置** ⇒ 新手要先读三段才知道从哪开始 |
| `vision-work` | ✅ `## Why this exists`（三条动机：拒答是行为不是漏做 / 难的是发现屏幕在脚下变了 / 能带走的是方法不是数字，+"谁需要它"一行） | ✅ `## Ten minutes to a scored run`（可移植命令、无本机路径；好跑的样子 + 失败 → `docs/TROUBLESHOOTING.md`；四条前置清单**移到路径之后**当"起飞前检查"） | ✅ `docs/TASK-AUTHORING.md`（四个活动件 + 真值协议 + 加族七步清单；题仍是硬编码，文档**如实说明**并指出改哪几处） |

### (b) 路径不写死，缺了就报"装什么 / 设什么"

真硬编码只有两处（`sol/sandbox/gui_see.py:18` 的 `TESS`、`sol/sandbox/loop.py:39` 的 `ACTOR_HOME`）—— **两处均已于阶段 3.1 参数化**：改读环境变量（`TESS` 保留作者路径为最后兜底、缺失即停并打印指令；`ACTOR_HOME` 的兜底目录没有 `port.txt` 时在 stderr 点名变量并回退端口）。标准 b 的验收语句（缺依赖必须停、并打印"装什么 / 设哪个变量"）现在**三仓库都过**（`vision-work` 两条的实测输出见 `docs/TROUBLESHOOTING.md`）；其余 `D:\` 出现在文档命令里。
**范本 = `dsh-termux-kit`**：`DSH_AJ` 环境变量 + `$HOME/.smoke/android.jar` 兜底 + 缺依赖即停并打印指令（其 `## Quick start` 的 `android.jar` 段逐字写明；该文件在阶段 1 被改过 ⇒ 此处按**节名**引用，不引行号）。标准 b 的验收语句直接抄它：**缺依赖时脚本必须停止，并打印"装什么、设哪个变量"。**

### (c) 依赖落盘 —— 拆两半：**语言级 / 系统级**（v1.1 改写）

**语言级依赖必须落盘并 pin。** `dsh-termux-kit` ✅ `requirements-dev.txt`；`dsh-vision-kit` ✅ `requirements.txt`（`numpy==2.3.5` / `pillow==12.3.0`，带 pin 理由）+ `requirements-dev.txt`；`vision-work` ✅ `requirements.txt`（**阶段 3.1 落盘**：CPython 3.12 + `numpy==2.3.5` / `pillow==12.3.0`，每条带 pin 理由；Tesseract 不是 pip 包 ⇒ 其版本记进 run json 的 `env` 块）。
**系统级依赖必须给出一行安装命令，并标注版本或"可选"。** 试点实测：`dsh-termux-kit` 的运行依赖是 Termux 系统包（`pkg install zstd imagemagick tesseract tesseract-lang`，写在其 `## Quick start` 里）—— pip 侧落盘覆盖不到它们，同一仓库还有一张"第三方组件"表兜底。⇒ **判据：新机器上，仅按落盘文件 + 这一行命令，能把依赖装齐**；装不齐的必须在同一处标"可选"。
> 回灌依据：v1 只写"依赖落盘"，试点发现那会把**系统包**整类漏掉 —— 试点仓库的 `requirements-dev.txt` 是齐的，缺的从来不是 pip 那一半。

### (d) 产物记 `env` 块 —— 拆两种产物：**运行记录 / 构建产物**（v1.1 改写）

**运行记录（每条记录一份）必须带 `env` 块** —— 谁跑的、哪一版代码、什么环境。**`vision-work` ✅（阶段 3.1）**：run json 里 `env` 与 `scripts_sha` 同级（`python` / `numpy` / `pillow` / `tesseract` / `screen{geom,dpi}` / `actor_py` / `actor_pid`；取不到一律记 `null`、不猜；actor 侧只多发一次 `ping`；**旧 json 不变**）。另两个仓库仍无这类产物 —— 它们的产物是构建物 ⇒ 走下一段的判据。
**构建产物（一份产物一个版本）必须把版本与来源写进产物本身，并有门禁能核对。** 范本 = `dsh-termux-kit`：`ui/controls.json > appVersions` 是唯一源 ⇒ `tools/ui-controls gen` 写进产物 ⇒ `tools/app-verify` 核对"同版本不同内容"；其 CHANGELOG 也记版本号（如"控制台 1.21（versionCode 34）· 桥 2.2"）与生成块 `UI_VERSION`。
> 回灌依据：v1 把两类混成一条"运行产物"，而试点仓库**根本没有运行记录类产物** ⇒ 标准在那条上落不了地。拆分后两支各有各的验收语句。

### (d 配套) 三种发布通道 —— "sha 记录"怎么写才可核对（v1.1 新增）

同一个"记 sha"的动作，在三种通道下记的**不是同一种东西**；不写清，跨仓库引用就会指向不存在的东西（§0 那条"引用了不存在的上游版本"正是这么来的）。

| 仓库 | 发布通道 | 本地有 git 历史吗 | 该记什么 | 引用它时怎么写 |
|---|---|---|---|---|
| `dsh-termux-kit` | `publish.ps1`（git-data API；**不能**用 PUT `/contents`——它永远写 mode 100644，可执行位会丢） | **没有**（本地副本不是 git 仓） | 发布后由 API 产生的**远端 commit sha** + 目标文件的 **git blob sha** + CHANGELOG 版本号 | `仓库@<远端 commit sha>` + 文件 / 节号；**不许**写"本地某次改动" |
| `dsh-vision-kit` | 本地 git 直推 `main` | 有 | 本地 commit sha（推完 = 远端 HEAD，可核） | `仓库@<commit sha>:路径:行` |
| `vision-work` | 本地 git 直推 `main` | 有 | 同上 | 同上 |

配套四条判据：
1. **发布前后各记一次**：发布前记"本地 vs 远端差异"（阶段 1 实测 = 160 项里恰好 2 create + 3 push，其余 `skip (same)`），发布后记远端 commit + 逐文件 blob sha。只记一边 = 没记。
2. **通道自身的闸也要点名**：`publish.ps1` 有一步"有文件变了而 `CHANGELOG.md` 没变 ⇒ 拒绝推送"，这是**门禁**；两个 git 直推仓库没有这道闸 ⇒ 靠发布纪律（每次 push 必须有 CHANGELOG 条目）自律。
3. **`scripts_sha` 必须写清"覆盖了哪些文件"**（阶段 3.1 发现的口径缺口）：`vision-work` 的 `scripts_sha` = 三件套字节拼接的前 12 位，**不含** driver 的 import 依赖（`sol/sandbox/gui_see.py` 的 OCR、`sol/sandbox/loop.py` 的 actor 客户端）⇒ 那两处改动**不会**让 `scripts_sha` 变。阶段 3.4 的处置 = **不扩**（扩容点在 `gym_run.py:_sha()`，而 3.4 明令该文件冻结；且 3.4 的 sha 变化必须可归因到靶子/打分器）。要扩时按**一次口径变更**办：在 `SCORE-history.md` 记新定义、run json 里**同时**写 `scripts_sha_files`（参与哈希的文件名清单）让数值自描述、**旧值不改写**（旧批按旧定义仍可比）。**本段明确留待 3.6（manifest v1 实现）同批做** —— 那一段本来就要裂 `gym_app.py`，"口径变更 + 新字段"一次做完最省。**✅ 已按此办理（阶段 3.6）**：定义改为六文件（+ `gui_see.py` / `loop.py` / `plans.v1.json`）、run json 新增 `scripts_sha_files` 清单、**旧值一字未改**；读法见 `SCORE-history.md` §1.1。
4. **取不到的版本写成边界，不要猜**：`actor` 自身代码的 sha **取不到** —— `ping` 只回 `pid` / `py` / `geom` / `dpi` / `uptime`，没有版本或哈希 op，要取得先在 `dsh-vision-kit/actor/actor.py` 加一个 op（跨仓库改动）。阶段 3.4 的处置 = **不记**，只记 `env.actor_py` / `env.actor_pid`（同一 session 内可辨认，**跨 session 不可追溯**），并把它写成已知边界。

### (e) 手册在 repo 内

`dsh-termux-kit` ✅（`docs/` 8 篇 + README 自足）；`dsh-vision-kit` ⚠（`docs/` 4 篇，Generation 1 说明仍在 README 内）；`vision-work` ✅（**阶段 3.3**：规程正本 `docs/OPERATING.md` + 前门四篇 `docs/`；仓库外技能已降为指针，见 §2 第 1 条）。

### (f) 边界诚实声明

`vision-work` ✅ 最强（`What this is not` + 已知边界 + 【未决】）；`dsh-vision-kit` ✅ `Security`（`:248`：`:8731` 无鉴权、只监听 loopback、截图含整屏）+ "No UI screenshots are published here"；`dsh-termux-kit` ✅ `Troubleshooting` 每条给出 symptom / cause / solution。
**统一新增一条**：不承诺"复现作者的数字"（OCR、DPI、字体都在环里），只承诺**方法与可重跑的运行** —— 这既是诚实，也是保护。`vision-work` **已落（阶段 3.3）**：`README.md` 的 `## Why this exists` 第三条 + `## What this is not` 第四条。

### (g) 双语策略统一

三仓库**都已具备** `README.md` + `README.zh-CN.md`（远端根级文件实测三者皆真）⇒ 冻结为「**英文主、中文对译**」。
术语与禁用词沿用 `dsh-termux-kit/CONTRIBUTING.md` + `docs/术语表.md`，但**跨仓库引用必须带 commit / 文件 / 节号**（约束 4）。

### (h) 计数与清单单一化（v1.1 新增）

**可数的量（组件数、工具数、篇数、版本号）全仓库只写一处 = 源；其余位置引用该处，或由生成产出。**

- **证据**（试点实测，全部可在**已发布**的 `dsh-termux-kit@master` 上复核）：`12` 这个数字写在 **≥9 处**（两份 README 的 Quick start / Features / 仓库结构段、`tools/dsh-kit-update` 的注释与运行输出、`widgets/common.sh`、`tests/selftest.sh`、`tools/install-widgets` 的注释），其中 **2 处已经漂了**：`widgets/common.sh:28` 写 "reaches all **10** widgets"、`tests/selftest.sh:2` 写 "self-test suite for the **9** widgets"。
- **复核命令**（任何人可跑）：`grep -rn "12 widgets\|12 个\|Twelve" README.md README.zh-CN.md tools/ widgets/ tests/`
- **可验收语句**：全库 grep 该数字，**除"源"那一处外不允许出现字面量**；参实现就在同一仓库里 —— `ui/controls.json`（三处 UI 文案的唯一源）与 `i18n/zh.json`（翻译表唯一源），两者都有生成器 + `check` 门禁。
- **为什么单列一条**：这不是"把 12 改成 13"的小事，而是**加第 N 个组件时必然踩的坑** —— 试点段新增 `docs/TASK-AUTHORING.md` 时，光是找齐"12"写在哪几处就要 grep 一轮，而其中 2 处已与实际不符。
- **`vision-work` 侧现状（阶段 3.5 核实，作为 v1.0 不声明 `(h)` 的依据）**：`五判定` 这个**集合名**出现在 9 个文件；审计文档数 `8 份` 出现在 4 处（`audit/README.md`、`README.md`、`CHANGELOG.md`、本文 §1 结构图）⇒ 属 (h) 的缺口，与计数闸一起归 **3.7**。

### 两条示范句（试点产出，可直接照抄进任一仓库的 CONTRIBUTING / README）

1. **缺依赖时脚本必须停止，并打印"装什么、设哪个变量"——不许静默降级，不许猜一个默认路径。**
   （出处 = `dsh-termux-kit` 的 `## Quick start`：给出两个选择（放进 `$HOME/.smoke/android.jar`，或用 `DSH_AJ` 指过去），并写明缺它时"脚本带着这些指令停下"；同型第二例 = 缺 `allow-external-apps` 就给一行可粘贴的命令。）
2. **一处写、多面生成：同一个量只允许有一个源，其余面由生成产出，并有 `check` 门禁比对。**
   （出处 = `dsh-termux-kit`：`ui/controls.json` 是三处界面（页面面板 / 控制台 APK / 桥 APK）的唯一文案源 —— 改它 → 跑生成 → 三个产物同步，`check` 进 CI；同型第二源 = `i18n/zh.json` 生成三个语言块。）

## 5. 执行顺序表（试点 → 上游 → 下游）

| 阶段 | 仓库 | 单元 | 为什么在这个位置 | 并行性 | 闸（做完才能进下一步） | 停止条件 |
|---|---|---|---|---|---|---|
| **1 试点** | `dsh-termux-kit` | B | 完全独立、前门最好（B+）、改它不牵动任何仓库 ⇒ 用最低试错成本把标准**真落地一遍**，验证标准本身好用（阶段 1 已完成并已发布：见 §8） | ✅ 与阶段 2/3 无依赖（但作为试点**应先做**：它的产出是"标准实测版"） | ✅ **已达成、并已发布（§8；对外 commit `1fbc1a36bc7a1131555250c96c1c9a511b72e8ac`）**：标准逐条落地并成文；前门改前/改后对照；交叉引用核（它指向 A = **0** 处；A 指向它的 4 处逐条读过，无一路径/节/行号 ⇒ 不悬空） | 若发现**标准本身**要改（某条在该仓库落不了地）⇒ 先改标准再继续 **（已触发并按此办理：v1.1 回灌）** |
| **2 上游** | `dsh-vision-kit` | A | 下游文档要引用**准确的 commit/sha** ⇒ 必须先发布；当前 `published ≠ working`，不发布则下游永远引用不存在的版本 | ❌ 与阶段 3 不可并行；✅ 与阶段 1 可并行（不同仓库、无引用） | actor 可发布版本确定（commit 记录 + 引用用的 sha）；前门三代整理（标清当前路线）；4 处 termux 信用引用仍成立 | 若发布需要改接口 ⇒ **停**，先报（会波及下游引用核） |
| **3 下游** | `vision-work` | A | 最重、依赖最多（依赖阶段 2 的 pin） | ❌ 与阶段 2 同批禁止 | 段内多步见 §6：参数化 + `env` + requirements + `audit/` 搬迁（**714 引用点 / 457 行**核验，搬迁前失效清单 412 处，见 `audit/README.md`）+ 前门 + 加题接口 + viewport 验证 + 冻结声明 | 搬迁前未列失效清单 ⇒ **停**；引用不存在的上游版本 ⇒ **停** |

**试点必须回灌 —— 已执行（v1.1）**：答案是「**没有一条不适用**，但 (c)(d) 必须改措辞、并应新增一条 (h)」；已按阶段 1 的实际写法回写本文档（§4 的 (c)(d)(h) + 示范句 + (d 配套)），回灌输入与逐条对照见 §8。⇒ 标准不再是纸面的：它被一个真实仓库走了一遍，并因此改了两次措辞、加了一条。

**备选顺序**（先解 work 的痛）：阶段 2 → 阶段 3 串行，阶段 1 任意时间并行。两种都可行；**推荐前者**，因为标准要先磨，否则 downstream 段会用一套没验证过的标准做最重的改动。

## 6. 逐仓库开工模板 + 段清单

**模板（每段一份，六格；一次只动一个仓库）**

1. **段号 / 仓库 / 单元**；
2. **前门改前 → 改后结构对照**（章节级：新增哪些节、合并哪些、降级到 `docs/` 哪些、删除哪些）；
3. **sha 变化**：三件套（work）/ `actor`（kit）/ 工具脚本（termux）**哪个变了、新值是什么**；未变就写"未变"（termux 无 git 历史 ⇒ 报**发布后的远端 commit + 已发布文件的 git blob sha + CHANGELOG 版本**，见 §4「(d 配套)」）；
4. **交叉引用核**：指向其它仓库的引用逐条列（现状 = **14 引用行（12 字面量）** / 0 / 4 / 0 处），仍成立的打勾，失效的给出修复动作（**搬迁类改动必须先列失效清单再动**）；
5. **一句话**：陌生人能否从 `clone` 到知道下一步 —— 照 §4(a) 三问逐条回答**是 / 否**，不许写"更好了"；
6. **闸与停止条件**（照 §5 该阶段那一行）。

**段清单**

- **1.x `dsh-termux-kit`（试点）**：1.1 ✅ 前门补第 ③ 问（新增 `docs/TASK-AUTHORING.md`：加 widget / 加命令的路径）；1.2 ✅ 标准落地对照表成文并**已回灌本文档 §4**（v1.1，独立提交）。**未做**：版本号 bump（该仓库 §六：纯文档 commit 不 bump）与该仓库内部 5 处计数漂移（§8）。
- **2.x `dsh-vision-kit`（上游）**：2.1 发布上游（commit + CHANGELOG + 记下可被引用的 sha）；2.2 前门三代整理（Generation 1 / 1.5 降到 `docs/` 或明确标"历史"，当前路线提到最前）；2.3 下游引用核（`vision-work` 那 14 引用行 / 12 字面量逐条）。
- **3.x `vision-work`（下游）**：3.1 ✅ 参数化（`TESS` / `ACTOR_HOME`）+ `requirements.txt` + run json `env` 块；3.2 ✅ `audit/` 搬迁 + `audit/README.md` + **714 引用点 / 457 行**内容锚定核验（搬迁前失效清单 412 处 = 仓内 362 + 仓外 50）；3.3 ✅ 前门重写（`## Why this exists` 三条动机 + `## Ten minutes to a scored run` + 前置清单移到路径之后 + `docs/` 四篇 = `QUICKSTART`/`TROUBLESHOOTING`/`TASK-AUTHORING`/`OPERATING` + 规程正本入库、仓库外技能降为指针 + `STATE.md` §14.6 的 `/mnt/d/` 判定为合法路径；三件套 sha 未动）；3.4 ✅ **viewport 进体系（A 已实施，靶子首次裂 sha）+ manifest v1 只设计**（设计见 `docs/TASK-AUTHORING.md` §5，改判理由见 §3 影响清单该行）：靶子两处 `return` 各加一行声明、判定逻辑零改动；`score.py` 加独立桶 `viewport_n` / `viewport_pass`（**不进五判定、不进主分母**）并单打一行，`--selftest` 41 → 43 项；新 sha `gym_app.py` **`17b6a59cb831dafa`**（← `66632d85eac81c12`）/ `score.py` **`c1a251a248a029c7`**（← `ef066713a03eb940`）/ `scripts_sha` **`0c2c420e4d40`**（← `b8f83571f650`），`gym_run.py 2ba26b608cf7ec18` **未动**；**离线回归 = 新旧打分器在 5 个既有 run json 上输出逐字节相同**（批次 1–20 读数不受影响的硬证据）；`scripts_sha` 覆盖面缺口与 actor sha 两条处置落 §4(d 配套) 判据 3 / 4；**本段未跑批**（验证批仍在 3.5）；3.5 ✅ **A 的验证批 + v1.0 声明 + 冻结条款 + 欠账分流**（`t_rows` / `t_chips` 两批各 8 题前台真鼠标：J1–J4 全过；跑前补 `score.py` 的 v0 打印 ⇒ `score.py` **`e80a646c63de8075`**、`scripts_sha` **`4fc217c37901`**，`gym_run.py` / `gym_app.py` **未动**；**v1.0 = 八条里七条全过**，`(h)` 不在声明内；#18 → **部分覆盖**；v1.x 清单与冻结条款见本清单末；数值见 `sol/sandbox/SCORE.md` 批次 23 / 24 节）；**3.6 ✅ manifest v1 实现 + `scripts_sha` 覆盖面扩容**（2026-10-06；同段两个 commit，可独立 revert：**A = `1c1a9b8`** 五张计划表移入 `sol/sandbox/plans.v1.json`（**266 个 `(class, variant)` 逐元组等价**；`gym_app.py` 1494 → **1483** 行、新 sha **`f8b8429725364294`**），**B = 口径变更**（`gym_run.py` 3724 → **3733** 行、新 sha **`fd8e5e1f0ee237b4`**；`scripts_sha` 改**六文件**定义 = **`7051c259fa05`** + run json 新增 `scripts_sha_files`），`score.py` **未动**；**不跑批**，闸 = 离线逐元组 **266/266** + 13 个场景各 `--tasks 2` 干跑 **13/13** + `--selftest` **43/43**；实施记录 = `STATE.md` §35 / 能力边界与 schema = `docs/TASK-AUTHORING.md` §5 / 口径读法 = `SCORE-history.md` §1.1）—— 设计原文（阶段 3.4 成文，仍然有效）：设计见 `docs/TASK-AUTHORING.md` §5（**能力边界**：只把「题序 / 场景 / 变体组合」外置成数据，**不是插件系统**；新增**视觉形态**仍要写 `_trap_*` 方法与 `t_trapN` 场景），闸 = 与上一 commit 冻结字面量的**离线逐元组等价核**（不是再跑一批），代价 = **第二次裂 `gym_app.py` sha**，并把 `scripts_sha` 覆盖面扩容 + run json 新增 `scripts_sha_files` 一并做掉；**3.7（待办）**计数闸扩展 —— 设计已在仓库外成文（`D:\DSH\dsh-actor\tmp\stage2\C3-checkcounts-design.md`；本轮只落文、不改 `dsh-vision-kit`）：op 数已有闸（`tools/check-skill-ops.py`，`ci-static.ps1` 第 6 阶段），真缺口 = 踩坑条数单一化 / 双语数字一致性 / 清单完整性 ⇒ 建议 `tools/check-counts.py` 接第 7 阶段。

**v1.0 冻结条款**（2026-10-06 声明；与 §4(a) 三问一起读）

- v1.0 之后**不再加 scenario 类**；新想法走 **v1.x** 或另开仓库。
- **"冻结" = 接口冻结**（run json `schema: 1` + 文档 + 引用纪律），**不是停止开发**。
- **声明口径**：`vision-work` 的 v1.0 = §4 八条里 **(a)(b)(c)(d)(d 配套)(e)(f)(g) 七条全过**；**(h) 计数与清单单一化明确不在声明内**（依据见 (h) 节末）。
- **v1.x 清单（仍开着的欠账）**：① #18 = **部分覆盖**（前台真鼠标、批次 23 / 24 各 8 题、`viewport` 桶；仍不覆盖 `--bg` 鼠标通道与滚轮 / 拖拽的连续交互公差）；② ~~`scripts_sha` 覆盖面缺口（只哈希三件套，漏 `gui_see.py` / `loop.py`）~~ **已还（阶段 3.6）**：六文件定义 + `scripts_sha_files`（值 `7051c259fa05`），旧值不回溯、两种定义不可互比（`SCORE-history.md` §1.1）；③ actor 自身 sha **不记**（`ping` 无版本 op；只记 `env.actor_py` / `env.actor_pid`，跨 session 不可追溯）；④ ~~**manifest v1 实现**（3.6）~~ **已做（阶段 3.6，commit A `1c1a9b8`）**：题序搬进 `sol/sandbox/plans.v1.json`，266 元组逐元组等价、题序逐字未变；⑤ **计数闸扩展**（3.7）；⑥ `dsh-termux-kit` 侧 5 处计数漂移（§8 已记，未做）。
- **已关闭 / 已还清**（归档、不再投入）：#4 / #12 / #17 / #19 / #20（窄批口径）/ #21（已修 + 回归）。

## 7. 红线（v1 写作段与 v1.1 回灌段共同适用）

- **（以下是 v1 / v1.1 写作段的历史记录；三件套的现值见 §6 的 3.4 / 3.5 行）** 本段**只写文档**：三个仓库的代码与公开内容**一字未改**；三件套 sha 未变（`gym_app.py 66632d85eac81c12` / `gym_run.py d8594bff3738ca9b（3.1 后 = `2ba26b608cf7ec18`）` / `score.py ef066713a03eb940`）。
- v1 唯一新增文件 = 本文档（在 `vision-work` 内），按发布纪律补 `CHANGELOG.md`。若你希望它不属于任何一个仓库，移到 `D:\DSH\notes\` 只是一次 `git mv`。
- **v1.1（回灌）**：只改本文档 + 本仓库 `CHANGELOG.md`；**另一份仓库（`dsh-termux-kit`）与 `dsh-vision-kit` 一字未改**，三件套 sha 仍逐位不变（`gym_app.py 66632d85eac81c12` / `gym_run.py d8594bff3738ca9b（3.1 后 = `2ba26b608cf7ec18`）` / `score.py ef066713a03eb940`）。
- **阶段 3.6（manifest v1 + `scripts_sha` 扩容）**：`vision-work` 侧**代码动了两个文件、新增一份数据** —— `sol/sandbox/gym_app.py` 1494 → **1483** 行（**`f8b8429725364294`**）、`sol/sandbox/gym_run.py` 3724 → **3733** 行（**`fd8e5e1f0ee237b4`**）、新增 `sol/sandbox/plans.v1.json`（115 行，**`080881993eb1cd7e`**）；`sol/sandbox/score.py` **未动**（`e80a646c63de8075`）。⇒ **本文件 §6 里 3.4 / 3.5 行记的三件套 sha 与 `scripts_sha` 值都是历史值**，现值见 §6 的 3.6 行与 `STATE.md` §35；`scripts_sha` 自 3.6 起是**六文件**定义，与 §6 中 3.4/3.5 的旧值**不可互比**（`SCORE-history.md` §1.1）。**另外两个仓库（`dsh-vision-kit` / `dsh-termux-kit`）一字未改**，其 sha 逐位不变。
- **一句话**：**先动 `dsh-termux-kit`（试点磨标准）**；`dsh-vision-kit` 次之、**必须在下游之前**；`dsh-termux-kit` 与单元 A **可并行**（无依赖），单元 A 的两仓库**不可同批**，`vision-work` **最后**。

## 8. 试点记录摘要（阶段 1 · `dsh-termux-kit`）

**状态：试点已执行，该仓库的改动已于 2026-10-06 发布** —— 当前对外可见标记 = `master` 的 **`0c184e91afb77067e7362170d87cf87151d16c51`**（发布链：`fa5b7b020c030d90096b3a5162b3e2c06fc2f701` → **`1fbc1a36bc7a1131555250c96c1c9a511b72e8ac`** `docs: add the extension guide and a counts gate; fix four drifted counts`（11 文件）→ **`0c184e91`** `fix: make check-counts shellcheck-clean and note the phone-only gates`（4 文件））。第二个 commit 是**自己造出来的债自己还**：第一次发布把该仓库 CI 的 static 作业弄红了（见下面"工具教训"第三条），修完重发。发布后两次都复核 `publish.ps1 -DryRun` → **changed 0 of 160**（远端逐字节等于本地副本）；GitHub API 复核 `1fbc1a36` = 11 文件、`0c184e91` = 4 文件；CI run(`0c184e91`) = **五个作业全 success**。本文档的 v1.1 回灌是**独立提交**，与试点段、与发布段都分开。

**做了什么（最终发布面 = 11 个文件：2 新建 + 9 修改）**：① 前门补第 ③ 问 —— 两份 README 各新增一节（`## Who this is for` / `## 什么时候你需要它`：4 条"你需要它" + 1 条"不需要它"的边界）+ 小组件清单末尾加指路行 + 仓库结构表补一行；② 新增 `docs/TASK-AUTHORING.md`（158 行）：加第 13 个 widget 的完整路径（文件名与头部、`MAP` 中文名门禁、`i18n/zh.json` → 三个生成块、`ui/controls.json` 接线、`dsh-tasksd` 白名单与四处 id 一致门禁、必须同步的计数、自检）与加一个运行时工具（`# install: runtime` 才是安装开关、原子替换、单一源）；③ 新增 `tools/check-counts`（111 行）= 标准 **(h) 的执行者**：以 `widgets/[0-9]*.sh` 为唯一源核对全库计数，默认档只报不一致、`--strict` 连拼写数字一起管，命中只读镜像 `apps/` 时打印"预期为红"（**不带数字**，陌生人可读）；④ 修掉下文记的 4 处漂移（判据一律是**不写数字**或**标注历史**）；⑤ 两份 README 各加"在电脑上跑门禁会报失败"一节 + `## Requirements and limits` / `## 环境要求与限制` 各一条 bullet —— 把 (b) 的边界与真源依赖写成**陌生人可见**；⑥ `docs/DSH运维笔记.md` 按该仓库守则 §一.2（**记录先于推送**：没写运维笔记、没更新 CHANGELOG 不许 push）补阶段 1 条目 —— 自查发现的缺口，此前该笔记最新一条停在 2026-10-03；⑦ CHANGELOG 条目（纯文档 + 新工具 ⇒ 按该仓库 §六 **不 bump 版本号**，那三个版本号描述的是 APK）。**`PILOT-FEEDBACK.md` 已删除**（从未发布过 ⇒ 零成本、不需要删除提交）。

**核过的**：发布前把 10 个文件逐字节备份到 `_local/pre-publish-2026-10-06/`（+ `MANIFEST.txt`，含发布前后的对外标记；更早三份在 `_local/pilot-baseline/`；该目录永不发布）；发布前 `publish.ps1 -DryRun` = 160 个文件有本地副本、**11 个会变**（2 create + 9 push）、其余 `skip (same)`，第 4 步 CHANGELOG 门禁通过；`tools/check-no-secrets.sh` = safe to publish；`tools/check-task-ids` = 退出码 0（本批唯一可能触碰的 id 门禁 —— 它按正则读 `dsh-tasksd` 的 `ALLOWED`/`VIRTUAL` 字典，而本批只改了该文件的 docstring）；`apps/**` 与 `dist/**` 逐字节未动（dry-run 逐行 `skip (same)`）；发布后复核 **changed 0 of 160**；三件套 sha 与 `dsh-vision-kit` 逐位未变；`dsh-vision-kit → dsh-termux-kit` 的 4 处引用逐条读过，**无一处指向文件路径 / 节锚点 / 行号**（2 处散文 + 2 处仓库根 URL）⇒ 前门增补不会让它们悬空。

**回灌改了什么**（= 本文件 v1 → v1.1 的差异）：(c) 拆语言级 / 系统级；(d) 拆运行记录 / 构建产物；新增 (d 配套) 三种发布通道与 sha 记录；新增 (h) 计数与清单单一化；两条示范句成文；本节 + §5 / §6 的状态更新。**七条里没有一条"不适用"** —— 试点真正的产出是**两处措辞 + 一条新标准**。

**行号口径（发布后更新）**：试点改过的 `README.md` / `README.zh-CN.md` / `CHANGELOG.md` **已随 `1fbc1a36` 发布** ⇒ 现在应引用**已发布版本的行号**；本文档涉及这三份文件的位置一律用**节名 / 段名引用**（例如"其 `## Quick start` 的 `android.jar` 段"）。v1.1 里保留的两处行号引用（`widgets/common.sh:28`、`tests/selftest.sh:2`）**已被本次修复作废**（那两行现在不写数字）—— 引用时改成"`widgets/common.sh` 的 `dsh_msg` 说明段"与"`tests/selftest.sh` 的文件头注释"。下游（阶段 3）引用这个仓库时按同一规则处理。

**试点仓库内部 5 处的去向（4 已修 + 1 转常设门禁 + 新增 S9）**：`widgets/common.sh:28`（写 "10 widgets"）、`tests/selftest.sh:2`（写 "9 widgets"）、`tools/dsh-tasksd` 的 docstring（写 "9 whitelisted"）、`tools/i18n-build-table` 的 `OLD_NAME` 表（只列到 9）—— **四处已随 `1fbc1a36` 修掉**；`12` 这个数字的散落 —— 改由 `tools/check-counts` **常设核对**：实测唯一源 = 12、**20 处一致**、1 处拼写数字（`README.md` 的 "Twelve … widgets"）、**1 处真实不一致**。**新增 S9**：那处不一致 = `apps/console/src/io/dsh/console/Lang.java` 的手写注释写 10 —— 它在**只读镜像**里（真源 = 手机上的 `~/dsh-console`）⇒ 本机改不了、也不许改镜像；修法 = 手机上改真源注释 → `tools/sync-apps` 镜像回来；在此之前 `check-counts` **预期为红**（它自己会打印这句，并给出"改真源"的提示）。

**工具教训（写进本节以免重犯）**：该仓库的门禁分两类 —— ① 只看仓库内容的（`check-no-secrets` / `check-task-ids` / `check-counts`）**能在电脑上跑**；② 读 App **真源码**或**已编 APK** 的（`i18n-table` / `i18n-audit` / `ui-controls` / `app-verify` / `sync-apps`）**只能在手机侧跑**（本机报 `FileNotFoundError: /home/dsh/...`；且它们默认 `ROOT=~/dsh-termux-kit`，电脑上须显式 `DSH_KIT_REPO=<repo>` 才走到读文件那一步）。第二个坑：**不要在 WSL 里用 `bash <工具>` 跑这些 Termux 脚本** —— 绕过 shebang 后 `tools/i18n-table` 会把 `i18n/zh.json` 当 shell 执行（实测：几十行 `command not found`、5 分钟超时、持久 shell 被重置）；事后用 `publish.ps1 -DryRun` 前后对照证明**那次误跑没有改动仓库任何文件**。核"发布是否只改了该改的"的正确做法 = 发布前后各跑一次 dry-run 并比对 changed 数。第三个坑（**本次实际踩到**）：**新写的 shell 脚本必须先跑 `tools/ci-shellcheck.sh`** —— 该仓库 CI 的 static 作业正是 `bash tools/ci-shellcheck.sh`（ShellCheck 0.11.0、`-S warning`，**warning 即算 finding**），而 `tools/check-counts:76` 在双引号串里用了两个 unicode 引号（U+201C/U+201D）⇒ `SC1111` ⇒ CI 红。这道闸**本机跑得动**：`SHELLCHECK=D:\DSH\.venvs\termux-ci\Scripts\shellcheck.exe bash tools/ci-shellcheck.sh`（与 CI 同版本，输出 `56 files, 0 with a finding` + `✔ static shell check clean`）。教训：**仓库里已有的闸，发布前要真跑一遍**；`.shellcheckrc` 里禁用的四个码都带理由，别靠猜。

**`PILOT-FEEDBACK.md` 的去向：已删除**（内容已全部并入本文档）。依据：① 它的 §1（标准逐条）、§2（两条示范句）、§6（回灌建议）已分别落在本文档 §4 的 (c)(d)(h) 与示范句段、§5；② 它的 §4（该仓库内部待修 5 处）已抄进本节；③ 该文件**从未发布过** ⇒ 删除零成本、无需删除提交。若将来要保留这类回执，必须与本文档保持同步，否则同一件事会有两份会各自漂移的真相。

**下一步** = **阶段 2（上游 `dsh-vision-kit` 发布）**。该仓库那 `+325/−16` 已按只读分析核过 = **可公开、无需清理**（逐 hunk 功能分类 + 本机路径/凭据/调试残留扫描零命中；`actor/home.txt` 含本机路径但被 `.gitignore` 忽略且未跟踪）⇒ 阶段 2 无前置阻塞。**发布后手机侧仍有两红 + 一条既有提醒，另立项、不阻塞阶段 2**：`tools/i18n-table check`（读真源码）与 `tools/app-verify console`（读已编的包）在**发布前就是这样**（手机 `bash tools/pre-push-check --strict` = 通过 10 / 失败 3 / 提醒 1）；`check-no-secrets` 报的 keystore/私钥文件**未被跟踪**（`.gitignore:12-13` 已覆盖）⇒ 不进远端，但**建议尽快移出仓库目录**（该检查按文件名扫整棵树，会一直报红）。发布后的预期动作：手机 `git pull --ff-only` → `./tools/install-tools`（本次改了两个已安装工具 `tools/dsh-tasksd` / `tools/i18n-build-table`，安装副本会先报"有差异"）→ 跑一次新门禁 `python3 tools/check-counts`。该仓库的发布**不阻塞**阶段 2。
