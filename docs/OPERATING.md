# GUI Gym 判分线 · 操作规程（正本）

> **这份是本仓库内的正本**（阶段 3.3 从仓库外的本机技能移入；仓库外那份
> `D:\DSH\skills\gui-audit-gym\SKILL.md` 已降为**指针**，只负责把 harness 引到这里）。
> 适用于 `vision-work` 这条"实时读屏驱动 Tk 靶子、由 `score.py` 打判定"的判分线。
> 只装**操作规程**，不装证据：任何数字引用前先看 `sol/sandbox/SCORE.md` /
> `audit/STATE.md` / `audit/HANDOFF.md`，本文档不复制批次数字。
> **语言**：本文档保持中文（操作者工作语言）；前门文档（`README.md`、
> `docs/QUICKSTART.md` 等）为英文。**机器相关的路径**在正文里都标了"本机"，
> 可移植写法见 `docs/QUICKSTART.md`。
> **平台结论（2026-10-05 已决策）**：判分线走 **Windows 原生**；**放弃 WSL 做 GUI
> 靶场**（理由与实测见 `audit/STATE.md` §11）。WSL 只作工具链（`jq`/`rg`/管道）。

## 1. 必读前置（开工前 5 分钟，别跳）

### 1.1 三件套在哪（`sol/sandbox/`）

| 文件 | 角色 | 备注 |
|---|---|---|
| `gym_app.py` | 靶子（Tk） | 只依赖 stdlib + tkinter；CLI：`--seed --state --events --scenario --gap --chaos --chaos-ms --chaos-kind --no-topmost --no-badge --control-alpha` |
| `gym_run.py` | 全盲驱动 | CLI：`--seed --press-jitter --tasks --scenario --state --events --no-start --json-out --max-repeat --chaos --chaos-ms --chaos-kind --bg --keys --until-interferences --max-tasks --lock-wait` |
| `score.py` | 计分 | `score.py <run.json>`；自检 `score.py --selftest` |

行数随改动漂，别背 —— 要引用先 `wc -l`。

### 1.2 四份文档

- `audit/STATE.md` —— 存档 + **开头的接续点** + §0 用户铁律 + §7 欠账清单 + §11 WSL 探测决策。
- `audit/HANDOFF.md` —— 交接页：§2 口径 / §3 重跑命令 / §4 已知盲区 **23 条** / §5 证据在哪 / §6 欠账。
- `sol/sandbox/SCORE.md` —— 计分板：各批数字 + 「口径版本与可比性（终版）」一节。
- `audit/DESIGN-refusal-scoring.md` —— 设计修订（拒答与计分的设计意图）；同目录还有 `DESIGN-18`（滚轮/拖拽）、`DESIGN-21`（鼠标可操作性）。
- 目录约定与计数/行号口径：`audit/README.md`（搬迁后所有引用路径的写法）。

### 1.3 环境铁律

1. **解释器**：跑测一律用**本机** venv 解释器 `D:\DSH\.venvs\vision-ci\Scripts\python.exe`
   （Python 3.12）。PATH 上的 `python` 可能是没装 numpy/PIL 的那个，直接跑会
   `ModuleNotFoundError`。可移植写法（`$PY` = 你装的 3.12 解释器）见 `docs/QUICKSTART.md`。
2. **actor 守护进程**：代码在 `D:\DSH\dsh-vision-kit\actor`（本机 HOME=`D:\DSH\dsh-actor`），
   默认端口 **`:8731`**（`ACTOR_HOME` 可覆盖，找不到 `port.txt` 时驱动会在 stderr 说明并回退）。
   开工先 `…\python.exe <actor>\act.py ping`（不在会自动拉起）。**调用姿势**：把一行 JSON 经
   **stdin** 喂给 `act.py`；PowerShell 里 `act.cmd '{"op":…}'` 会吞掉内层引号（报
   `Expecting property name enclosed in double quotes`）。
3. **同一时刻只能有 1 个 gym 窗口**（驱动要求 `target_windows(…) == 1`）⇒ **所有批次串行**。
   ⚠ 这个计数是按 UIA 窗口 name 的**子串** `"GUI Gym"` 做的 ⇒ **标题里含这四个字的其它窗口
   也会被算进去**（实测撞过：会话窗口标题含 "GUI Gym" ⇒ `refusing to drive: 2 practice
   target window(s) on screen - want exactly 1`、退出码 2）⇒ 跑前台批前先核计数，撞名就临时
   改名那个窗口、**跑完还原**（先存档原始标题）；被拒的那一次还会**留下残留靶窗口**（驱动只
   kill 启动器 pid）⇒ 下一批跑前先确认没有。详见 `docs/TROUBLESHOOTING.md` §1/§2。
4. **前台/锁屏**：跑测前确认未锁屏（驱动自带 `wait_until_unlocked()`，`--lock-wait` 控超时）；
   跑测前后记 `foreground`（前台若被抢，该批数字作废）。**鼠标批会占用用户指针与前台**；
   `--keys --bg` 走键通道 + PrintWindow，不抢前台。
5. **不背答案铁律**（`audit/STATE.md` §0，用户原话「你切记，不要背答案」）：app 状态文件的
   `truth` 只允许**评分**用，不得进任何决策路径、不得写进失败记录。

## 2. 跑批与复核

### 2.1 命令骨架（完整可复制版在 `audit/HANDOFF.md` §3，别背数字）

```powershell
# 本机：解释器 = D:\DSH\.venvs\vision-ci\Scripts\python.exe；actor 客户端 = D:\DSH\dsh-vision-kit\actor\act.py
$PY = 'D:\DSH\.venvs\vision-ci\Scripts\python.exe'   # 或你本机装好的 3.12 解释器（见 docs/QUICKSTART.md）
& $PY D:\DSH\dsh-vision-kit\actor\act.py ping
cd D:\DSH\vision-work\sol\sandbox                     # 或 <this repo>\sol\sandbox

# 鼠标通道（抢前台，必须串行）
$PY gym_run.py --scenario t_trap5 --tasks 48 --seed <n> --press-jitter 0,1200 --max-repeat 3 --json-out t_trap5-1.json
$PY score.py t_trap5-1.json

# chaos 键通道（--keys --bg，不抢前台）
$PY gym_run.py --scenario t_trap2 --tasks 60 --seed <n> --keys --bg --chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out t_trap2-w8-move70.json
$PY score.py t_trap2-w8-move70.json
$PY score.py --selftest
```

- `--chaos-kind` 的实际 choices = `{any, rebuild, move, popup, slow}`（`any` 是默认值）；
  `--chaos` 是 0–1 浮点，**两个标定档 = 0.35 / 0.70**；每类 2 强度 × **≥5 fire**。
- `--chaos-ms` 的**真实默认 = `600,1800`**（app 侧；驱动侧默认 `None` = 不转发 ⇒ 走 app 默认）；
  chaos 批惯用的 **`200,700` 是刻意选的短延迟**，让干扰几乎总落在驱动读题**之前** ⇒ 测的是
  "重读恢复"，不是"过期按压"。
- 鼠标通道与早期鼠标批可比；`--keys --bg` 与它们**不可比**（通道不同），只用于 chaos 对照。

### 2.2 留档三件套（每批都要）

`--json-out x.json` 时 app 的 state/events 自动写成 `x-state.json` / `x-events.jsonl`
⇒ **一批三件、同 `scripts_sha`**；不给 `--json-out` 就是老默认名（`gym-state.json` /
`gym-events.jsonl`），会被下一批覆盖。

⚠ **事件错联警告**：run json 的 `events` 字段是**路径**，`score.py` 按它读真值，而 app 每次
启动覆盖写同一文件 ⇒ **事后重打"非最后一批"会静默错联**（实测差 `MISMATCH 11`）。所以：
① 公布的数字一律是**跑完立刻打分**的；② 事后复核必须
`score.py <json> --events <该批留档副本>`；③ 最早的几批没有留档副本、不可事后复核（当时的
数字仍然有效）。

### 2.3 打完分看什么

`score.py` 每批打印：`pass_rate` / `decided_rate` / `false_refusal_rate`（分母 answerable）/
`false_accept_rate`（分母 must_refuse）/ 判定计数 / `race`（带分母）/ `guard gate` 样本
P50·P95 / 逐题行。**引用前先对齐口径版本**（见 §3.3）。

## 3. 口径与引用（改数字之前必须过这一节）

### 3.1 判定与分母

- 判定集合：`answered_right` / `wrong_target` / `false_refusal` / `refused_right` /
  `false_accept`，外加 **`timeout` 单列**（不算判定，按失败计）。通过 =
  `answered_right` + `refused_right`。
- **分母 = 声明了 `truth_class ∈ {answerable, must_refuse}` 的题**；未声明的题单列、不进分母。
- **`viewport` 类（阶段 3.4 起）**：`t_rows` / `t_chips` 现在声明 `truth_class = "viewport"`
  —— 它们**不进上面的五判定、不进分母**，单列成自己的桶（`score.py` 另打一行
  `viewport n/m`）。理由 = 这是「能力边界」的进度，不是第六种判定；**它的通过率与主线
  通过率不可并列引用**，混池批的 `rows_total` / `undeclared` 构成也因此与批次 1–20 不同。
  口径与回退见 `../audit/DESIGN-18-scroll-drag.md` §9。
- **拒绝 = 按 F8 协议键**（鼠标通道也按 F8——「拒绝键是协议不是答案」）⇒ F8 拒答**合法**，
  进 `refused_right` / `false_refusal`，不算违规动作。
- 主指标是**每次干扰下的通过率**（自变量 = 真正 fire 的扰动次数，不按题数）；另单列
  **屏幕读题率**（`asks_from_file > 0` 的历史分数一律标不可比）。

### 3.2 引用规则（`audit/HANDOFF.md` §2，用户审计定死；**九条** —— 逐条对齐，别再按旧条数引）

1. `race` / `guard-blind` 必须带**分母**（= 本批真正按了过期 ask 的次数，不是题数）；
   分母 < 5 标"非缓解"。
2. synonym **鼠标**通道成绩一律不引用；有效成绩 = 键通道 `synonym_button` / `synonym_only`。
3. `no_badge_fill` 的 0.50 档 D1 标定值来自合成帧，**与真实档位对不上**（未重标定）⇒ 引用时带说明。
4. 折叠表 `_code` 只用于**找目标**；判"题面是否变化"一律用 `_plain`。
5. json 里的 `gates` 是**计分算法版本**（按场景名分流），**代码版本看 `scripts_sha`** ——
   两者不是一回事。
6. 驱动的 `disturbances: N fired` **只数弹窗型**干扰；**chaos 注入率一律引用 app 侧
   `*-events.jsonl` 的 `chaos_planned` / `chaos`**，两者不可互推。
7. run json 的 `events` 是路径 ⇒ 只有**最后一批**能联对（见 §2.2 警告）。
8. **partial 批（退出码 3）的成绩不与完整批并列**：带 `partial: true` / `exit_reason` /
   `tasks_planned` 的 json 只用来证明"靶子中途没了也能落盘可打分"，**不作为成绩引用**。
9. **鼠标前台窄批引用时必须带四条**：① 通道 = **前台真实鼠标（非 `--bg`）**；② 口径 = **窄批**
   （单批单档，**不与 60 题的键通道批并列**）；③ **拆耦合** = 口径写"**路径可达 + 单次有效**"，
   **不写"保险有效 / 够用"**；④ **保险经单实例检验；"漏点是否消除" =【未决】，且已判定
   "不追加"**（再加 3 批 48 题只能把 95% 单侧上限收窄到与观测失手率同量级 ⇒ 仍分不开、
   边际收益 ≈ 0；将来真要证消除，唯一入口 = 再跑 3 批 48 题，**非当前计划**）。
   见 `audit/HANDOFF.md` §2 规则 9 与 §4 盲区 23 末尾的收口块、`audit/STATE.md` §28、
   `sol/sandbox/SCORE.md` 批次 16 节 `16.5/16.6` 与批次 17–19 节。

### 3.3 口径版本与可比性

- **v0**：靶子自己的 `result == ok`，分母 = 跑完的题（批次 0 及更早、`mix6x*`/`chaos-*`/
  `keys-mix*`/`t_chips`/`t_rows`/`t_form`、`t_trap2-1`/`-2`、`prof2`）。**与 v1 不可比。**
- **v1**：五判定 + 声明分母。**批次 1–4 全部是 v1**，跨批可比（批内 `scripts_sha` 分裂要单独
  标注——那是**驱动版本**，不是口径）。
- **v2**：把 `a_hit_but_failed` 拆成 `_wrong_target` / `_twin`（批次 5）。
- **v3**：race 的 variant 集合纳入 `swap_race_timer` 并拆出 `race_press_after_guard`；新增守门
  逐门分位 `gate_samples`/`gate_p50`/`gate_p95`（**批次 6 起**）。
- 口径版本是**计分工具的属性**、不是 json 自带属性（新列会**回填**到老 json）⇒ 引用时写清
  "哪个 json + 哪版 `score.py`"。全表在 `sol/sandbox/SCORE.md`「口径版本与可比性（终版）」。

### 3.4 结论边界（引用结论时必须一起带上）

- **`popup` 类是"部分可测"**（旧规则「测不了 ⇒ 数字任何情况下都不引用」已作废）：**键通道两个
  强度档**与**鼠标通道窄批**都有**合法成绩、可引用**；仍不可测的是 **`--bg` 鼠标通道**与
  **滚轮/拖拽**（欠账未覆盖）。引用鼠标窄批必须带上**四条边界**（见 §3.2 规则 9）。
- **`a_hit` 不是独立指标**：它是"守门假阳性把首次按压推过安全换题线"的**读出量**；
  `a_hit` 下降 ≠ 按错。
- **`stale` 与 `race` 是两套计数**：`trap_stale_press`（驱动侧记录）≠ `race`（计分侧带分母的
  那套），别混用。
- **chaos 的数字一律标「探索性·不并入定稿」**（四类 × 2 强度、每类 ≥5 fire）。
- **23 条已知盲区**在 `audit/HANDOFF.md` §4；当前挂起的欠账在 `audit/STATE.md` §7 与
  `audit/HANDOFF.md` §6（已冻结，不再为此裂 sha）。

## 4. 这个规程不做的事

- 不做通用 GUI 驱动（那是另一个技能的领域：UIA 优先、`wait_for` 不是 sleep、一次 `run` 串完）。
- 不复制任何批次数字、不在这里下结论（数字会变，`sol/sandbox/SCORE.md` 才是真源）。
- 不动三件套之外的东西：改 `gym_app.py` / `gym_run.py` / `score.py` 必须先确认"裂一次 sha"的
  代价并同步四份文档（含 `audit/REPORT.md` 的行号口径）。
- 不启 WSL 侧的 GUI 方案（已决策放弃，见 `audit/STATE.md` §11）。
- 加题请走 `docs/TASK-AUTHORING.md`；装环境请走 `docs/QUICKSTART.md`。
