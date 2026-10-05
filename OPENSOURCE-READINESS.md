# 三仓库开源就绪 · 总纲 v1（试点 → 上游 → 下游）

> 状态：**只定标准与顺序，不改任何仓库的内容**（2026-10-05）。本段唯一新增文件 = 本文档（在 `vision-work` 内），已按发布纪律补 `CHANGELOG.md`。
> 数据来源可复核：远端文件数/内容用**无凭据** GitHub API + `raw.githubusercontent.com` 实测；本地 dirty/行号用 `git status` / `sha256sum` / `wc -l`。

## 0. 基线（实测，不是回忆）

| 仓库 | 单元 | 远端 branch | 远端文件数 | 本地 HEAD | 工作树 | 本地 vs 远端 |
|---|---|---|---|---|---|---|
| `Maopk/dsh-termux-kit` | **B 独立** | `master` | 158 | **非 git 仓**（本地副本 `D:\DSH\dsh-termux-kit-copy`，走 `publish.ps1` / Contents API） | — | `README.md` / `CHANGELOG.md` sha256 **相同** |
| `Maopk/dsh-vision-kit` | **A 上游** | `main` | 50（`actor/` **11**） | `1e3cff6` | **dirty = 1**：`actor/actor.py` `+325 / −16` | README/CHANGELOG 相同；**`actor/actor.py` 不同** |
| `Maopk/vision-work` | **A 下游** | `main` | 115（`sol/` 102） | `97008dc` | clean | 一致 |

**最硬的一条事实**：`actor/actor.py` 远端 `sha256(16) = 4cfb87076604900e`，本地工作树 `fce8caa21ce0ed58`（2910 行）。
⇒ **本地在跑的执行器是一个未发布版本**（`--keys --bg` 与 `t_rows` 键通道的滚轮等价物都依赖那 325 行）。任何"下游文档引用 actor"的动作，在发布之前都是**引用一个不存在的版本** —— 这正是终止条件 ①「引用了不存在的上游版本」当前所处的状态，也只是**待触发**，不是已违反。

**三种发布通道（标准必须照顾到）**：`dsh-termux-kit` = `publish.ps1`（Contents API，无本地 git 历史）；`dsh-vision-kit` / `vision-work` = 本地 git 直推 `main`。

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
| vision-work → dsh-vision-kit | **16** | `CHANGELOG.md:16`、`DESIGN-18-scroll-drag.md:73 / :152 / :264`、`HANDOFF.md:62 / :177 / :194`、`REPORT-draft.md:6` |
| dsh-vision-kit → vision-work | **0** | 无 |
| dsh-vision-kit → dsh-termux-kit | **4** | `README.md:150`（"Following the upstream dsh-termux-kit convention"）、`README.md:258`（fork 来源）、`README.zh-CN.md:112 / :205` |
| dsh-termux-kit → A（kit/work） | **0** | grep `actor` 的 10 条命中全是 `refactor` 子串 |

⇒ 单元 A 的耦合**只有一条**（actor 运行时），单元 A↔B 的耦合**只有一条**（fork 信用）。两者都不是"见另一仓库"式含糊引用，而是可核对的具体指向 —— 这一点已经合格，要保住的只是它别退化。

## 2. "同一份"与"各仓库独有"清单

**跨仓库共享的同一份（一份物理副本、多方消费）**

| 内容 | 唯一副本在哪 | 谁消费 | 怎么断 |
|---|---|---|---|
| actor op 协议（23 op · `127.0.0.1:8731` · 换行 JSON） | `dsh-vision-kit/actor/actor.py` | vision-work 运行时（`sol/sandbox/loop.py:48-53`）+ 16 处文档引用（含 `actor.py:1427–1513`、`actor.py:1665` 这类**行号**引用） | 改 actor 一行 ⇒ 下游读数层与文档行号**同时**失效 |
| actor HOME 与端口文件（`D:\DSH\dsh-actor\port.txt`） | **仓库外**（运行环境） | 两个仓库都靠它 | 环境不落盘 ⇒ 陌生人起不来 |
| 插件 fork 来源（`dsh-selflook-local`） | `dsh-termux-kit`（历史组件） | vision-kit README 的信用引用（4 处） | 组件改名/搬迁 ⇒ 引用悬空 |
| 写作权威（提交前缀 + 禁用词表 + 术语表） | `dsh-termux-kit/CONTRIBUTING.md`、`docs/术语表.md` | **实际约束三个仓库** | 权威只在一个仓库里却管三个 ⇒ 另两个引用它时必须带 commit |
| 双语 README 对、CHANGELOG、MIT、ruff/mypy 配置 | 三仓库各自一份（**同约定、非同文件**） | 三仓库 | 新仓库加入时缺项 |

**各仓库独有（不共享，也不要假装共享）**

- `vision-work`：靶子 `ready`/`verdict` 协议、六判定与 `truth_class` 门、`[k]` 徽章约定、欠账/可比性纪律（`SCORE-history.md`）、批次证据 JSON（`sol/` 102 文件）。
- `dsh-vision-kit`：actor 实现、UIA/视觉工具、插件包（`plugins/`）、Generation 1 截图路线。
- `dsh-termux-kit`：Termux 工具（`tools/` 52）、两个 Android app（`apps/` 33）、12 个 widget（`widgets/` 14）、`ui/controls.json` **一源三面**（面板/控制台/桥）。

**三处"仓库外的副本"**（都不在任何仓库里 ⇒ 违反标准 e 或不落盘 ⇒ 违反 b/c）

1. `D:\DSH\skills\gui-audit-gym\SKILL.md` —— `vision-work/README.md:85-88` 明写手册在仓库外（"deliberately not duplicated here"）。
2. `D:\DSH\dsh-actor\`（actor HOME：`port.txt` / `home.txt` / `logs/`）。
3. `D:\DSH\.venvs\vision-ci` + Tesseract 安装（`sol/sandbox/gui_see.py:18` 的写死路径指向它）。

## 3. 影响清单（改谁会影响谁）

| 改动 | 影响面 | 影响方式 | 本总纲的处置 |
|---|---|---|---|
| 发布/修改 `actor.py`（单元 A 上游） | vision-work：运行时 **+** 16 处文档引用 | 行号漂移 ⇒ 引用变假；行为变 ⇒ 旧批读数不可比 | 上游发布单独成段；发布后**逐条核 16 处引用**（模板第 4 格） |
| vision-work 搬迁审计档案（`audit/`） | 自身 **77** 处交叉引用 + README/HANDOFF 指向 | 路径/行号漂移 | 搬迁**前**列失效清单 + 内容锚定核验（第 4 格） |
| vision-work 改三件套 | 自身 sha 表、跨批可比性、`scripts_sha` | 一次 sha 裂 = 一次可比性代价 | 合并成**一次**（manifest v1 + A 的 viewport） |
| 调整 vision-kit 插件目录 / README 结构 | 它自己指向 termux 的 4 处信用引用 | 被引用目标改名 ⇒ 空指针 | 动 vision-kit 前先确认 termux 侧路径稳定 |
| 改 termux-kit 的 `ui/controls.json` | 面板 + 控制台 + 桥 + 12 widget + `dsh-kit-update` | 单源改动三面同变（**优点**，也是"改一处动三面"） | 试点段只动**前门**，不碰 `controls.json` |
| 三仓库共同约定（双语对 / CHANGELOG / commit 前缀 / MIT） | 三仓库 | 缺一项就不齐 | 写进标准 (g) 与模板第 2 格 |

## 4. 共同标准七条（成文）

### (a) 前门必须回答三问（动机 / 上手 / 加题）

| 仓库 | ① 这是什么、我为什么需要 | ② 10 分钟跑起来 | ③ 怎么加 / 扩 |
|---|---|---|---|
| `dsh-termux-kit` | ✅ `README.md:9 Overview` | ✅ `:15 Quick start`（4 步；缺 `android.jar` 时**停下并打印指令**，`:38-41`） | ⚠ 有 12 widget 清单（`:87`）与 `ui/controls.json` 单源，但**没有"加第 13 个 widget / 加一条命令"的路径** |
| `dsh-vision-kit` | ⚠ 无独立 Why 章；`:14 The current path: the PC Actor` 标了当前路线 | ✅ `:22 Quick start`（"nothing to install first"） | ⚠ 有 `:83 Skills`，但 Generation 1（`:103`）/ 1.5（`:200`）/ Actor **三代并置** ⇒ 新手要先读三段才知道从哪开始 |
| `vision-work` | ❌ 无动机段（`:11 What this is` / `:23 What this is **not**` 有了，但没有"你为什么需要它"） | ⚠ `:50 Quick start` 命令完整，但解释器路径、`TESS`、cwd 三处要改 | ❌ **完全没有**（题硬编码在 `gym_app.py`） |

### (b) 路径不写死，缺了就报"装什么 / 设什么"

真硬编码只有两处（`sol/sandbox/gui_see.py:18` 的 `TESS`、`sol/sandbox/loop.py:39` 的 `ACTOR_HOME`）；其余 `D:\` 出现在文档命令里。
**范本 = `dsh-termux-kit`**：`DSH_AJ` 环境变量 + `$HOME/.smoke/android.jar` 兜底 + 缺依赖即停并打印指令（`README.md:38-41` 逐字）。标准 b 的验收语句直接抄它：**缺依赖时脚本必须停止，并打印"装什么、设哪个变量"。**

### (c) 依赖落盘

`dsh-termux-kit` ✅ `requirements-dev.txt`；`dsh-vision-kit` ✅ `requirements.txt`（`numpy==2.3.5` / `pillow==12.3.0`，带 pin 理由）+ `requirements-dev.txt`；`vision-work` ❌ **无**（本机 venv 3.12.14 恰好等于上游 pin ⇒ 可直接引用上游 pin，但必须落盘自己那份 + 声明 Tesseract 版本）。

### (d) 运行产物记 `env` 块

三仓库**都没有**。`vision-work` 的 run json 是唯一"产物" ⇒ 加 `env`（actor sha / Tesseract 版本 / Python pins / 屏幕 DPI / OS / 三件套 `scripts_sha`）。
已有半个实例：`dsh-termux-kit` 的 CHANGELOG 记「控制台 1.21（versionCode 34）· 桥 2.2」与生成块 `UI_VERSION`（`CHANGELOG.md:229 / :453`）⇒ 可作为 d 的第二个参照。

### (e) 手册在 repo 内

`dsh-termux-kit` ✅（`docs/` 8 篇 + README 自足）；`dsh-vision-kit` ⚠（`docs/` 4 篇，Generation 1 说明仍在 README 内）；`vision-work` ❌（手册在仓库外，见 §2）。

### (f) 边界诚实声明

`vision-work` ✅ 最强（`What this is not` + 已知边界 + 【未决】）；`dsh-vision-kit` ✅ `Security`（`:248`：`:8731` 无鉴权、只监听 loopback、截图含整屏）+ "No UI screenshots are published here"；`dsh-termux-kit` ✅ `Troubleshooting` 每条给出 symptom / cause / solution。
**统一新增一条**：不承诺"复现作者的数字"（OCR、DPI、字体都在环里），只承诺**方法与可重跑的运行** —— 这既是诚实，也是保护。

### (g) 双语策略统一

三仓库**都已具备** `README.md` + `README.zh-CN.md`（远端根级文件实测三者皆真）⇒ 冻结为「**英文主、中文对译**」。
术语与禁用词沿用 `dsh-termux-kit/CONTRIBUTING.md` + `docs/术语表.md`，但**跨仓库引用必须带 commit / 文件 / 节号**（约束 4）。

## 5. 执行顺序表（试点 → 上游 → 下游）

| 阶段 | 仓库 | 单元 | 为什么在这个位置 | 并行性 | 闸（做完才能进下一步） | 停止条件 |
|---|---|---|---|---|---|---|
| **1 试点** | `dsh-termux-kit` | B | 完全独立、前门最好（B+）、改它不牵动任何仓库 ⇒ 用最低试错成本把七条**真落地一遍**，验证标准本身好用 | ✅ 与阶段 2/3 无依赖（但作为试点**应先做**：它的产出是"标准实测版"） | 七条在该仓库逐条落地并成文；前门改前/改后对照；交叉引用核（它指向 A = **0** 处） | 若发现**标准本身**要改（某条在该仓库落不了地）⇒ 先改标准再继续 |
| **2 上游** | `dsh-vision-kit` | A | 下游文档要引用**准确的 commit/sha** ⇒ 必须先发布；当前 `published ≠ working`，不发布则下游永远引用不存在的版本 | ❌ 与阶段 3 不可并行；✅ 与阶段 1 可并行（不同仓库、无引用） | actor 可发布版本确定（commit 记录 + 引用用的 sha）；前门三代整理（标清当前路线）；4 处 termux 信用引用仍成立 | 若发布需要改接口 ⇒ **停**，先报（会波及下游引用核） |
| **3 下游** | `vision-work` | A | 最重、依赖最多（依赖阶段 2 的 pin） | ❌ 与阶段 2 同批禁止 | 段内多步见 §6：参数化 + `env` + requirements + `audit/` 搬迁（77 处核验）+ 前门 + 加题接口 + viewport 验证 + 冻结声明 | 搬迁前未列失效清单 ⇒ **停**；引用不存在的上游版本 ⇒ **停** |

**试点必须回灌**：阶段 1 结束时回答一个问题 —— 「七条里哪几条在真实仓库上落地时改了措辞？」以**阶段 1 的实际写法**为准并回写本文档；否则标准只是纸面的。

**备选顺序**（先解 work 的痛）：阶段 2 → 阶段 3 串行，阶段 1 任意时间并行。两种都可行；**推荐前者**，因为标准要先磨，否则 downstream 段会用一套没验证过的标准做最重的改动。

## 6. 逐仓库开工模板 + 段清单

**模板（每段一份，六格；一次只动一个仓库）**

1. **段号 / 仓库 / 单元**；
2. **前门改前 → 改后结构对照**（章节级：新增哪些节、合并哪些、降级到 `docs/` 哪些、删除哪些）；
3. **sha 变化**：三件套（work）/ `actor`（kit）/ 工具脚本（termux）**哪个变了、新值是什么**；未变就写"未变"（termux 无 git 历史 ⇒ 报**已发布文件的 git blob sha + CHANGELOG 版本**）；
4. **交叉引用核**：指向其它仓库的引用逐条列（现状 = 16 / 0 / 4 / 0 处），仍成立的打勾，失效的给出修复动作（**搬迁类改动必须先列失效清单再动**）；
5. **一句话**：陌生人能否从 `clone` 到知道下一步 —— 照 §4(a) 三问逐条回答**是 / 否**，不许写"更好了"；
6. **闸与停止条件**（照 §5 该阶段那一行）。

**段清单**

- **1.x `dsh-termux-kit`（试点）**：1.1 前门补第 ③ 问（加 widget / 加命令的路径）+ 版本与 `env` 落盘；1.2 七条落地对照表成文并回灌本文档 §4。
- **2.x `dsh-vision-kit`（上游）**：2.1 发布上游（commit + CHANGELOG + 记下可被引用的 sha）；2.2 前门三代整理（Generation 1 / 1.5 降到 `docs/` 或明确标"历史"，当前路线提到最前）；2.3 下游引用核（`vision-work` 那 16 处逐条）。
- **3.x `vision-work`（下游）**：3.1 参数化（`TESS` / `ACTOR_HOME`）+ `requirements.txt` + run json `env` 块；3.2 `audit/` 搬迁 + `audit/README.md` + 77 处内容锚定核验；3.3 前门重写（动机 + 三问 + 加题接口 `TASK-AUTHORING`）；3.4 manifest v1 + viewport（**一次** sha 裂）+ 验证批（占前台，同时是 #18 的首次真取数）；3.5 v1.0 声明 + 冻结条款 + 欠账分流。

## 7. 本段的红线（自我约束）

- 本段**只写文档**：三个仓库的代码与公开内容**一字未改**；三件套 sha 未变（`gym_app.py 66632d85eac81c12` / `gym_run.py d8594bff3738ca9b` / `score.py ef066713a03eb940`）。
- 本段唯一新增文件 = 本文档（在 `vision-work` 内），按发布纪律补 `CHANGELOG.md`。若你希望它不属于任何一个仓库，移到 `D:\DSH\notes\` 只是一次 `git mv`。
- **一句话**：**先动 `dsh-termux-kit`（试点磨标准）**；`dsh-vision-kit` 次之、**必须在下游之前**；`dsh-termux-kit` 与单元 A **可并行**（无依赖），单元 A 的两仓库**不可同批**，`vision-work` **最后**。
