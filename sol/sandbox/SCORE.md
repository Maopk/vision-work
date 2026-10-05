# GUI Gym - measured scoreboard

Target app: `gym_app.py` (Tk practice range). Driver: `gym_run.py`. Scoreboard tool: `score.py`.
All runs are keyboard-channel, background, no answer-peeking (`--keys --bg`, the driver never
reads `truth` from the state file), seed 20251007, `--max-repeat 3`.

## Measurement gate (read this before comparing any row)

Two gates exist. They are **not comparable**, and no old number was recomputed:
rows below only gained annotations.

| gate | verdict | denominator | appears in |
|---|---|---|---|
| **v0** | the target's own `result == ok` | every task the run got through | every run before 2026-10-04 18:30 |
| **v1** | five verdicts (below) | every task whose `truth_class` is `answerable`/`must_refuse`; undeclared tasks are listed separately and stay out | `t_trap` runs onward |

v0 knows only answerable tasks: refusing always scored wrong, there was no `must_refuse`
class, and an early-exit run shrinks its own denominator silently. v1 pins the denominator,
counts how many tasks reached a *decision* at all, and scores refusal on its own.

    v1 verdicts   answered_right | wrong_target | false_refusal | refused_right | false_accept | timeout
    passing       answered_right | refused_right

Reported per run: `pass_rate`, `decided_rate`, `false_refusal_rate` (over answerable),
`false_accept_rate` (over must_refuse), `disturb` (interference fires, **not** tasks),
`screen/file` (where the ask was read), `replan`, `stale`, `wasted`, `verify_giveup`.
A run carries `gates`, `events`, `scripts_sha` (sha256/12 of gym_run+ gym_app + score),
`app_args`; `truth` is joined by `score.py` **after** the run, never by the driver.

Per-row annotation: `gate / channel / ask reads (screen/file)`.
A v0 row's ask reads come from `stats.asks_from_screen` / `asks_from_file` (read counts,
so re-reads make them exceed the task count).

## 口径版本与可比性（终版）

口径版本是**计分工具的属性**，不是 json 自带属性：`score.py` 按 json 的 `gates` 字段选判定算法
（`score.py:634`），而**工具的算法会随版本更新**——新列（`a_hit_but_failed_wrong_target` / `_twin`）在
老 json 上也会被补算出来。所以引用任何一行都要写清"**哪个 json + 哪版 score.py**"。

| 版本 | 判定 | json 的 `gates` | 覆盖批次 | 可比性 |
|---|---|---|---|---|
| **v0** | 靶子自己的 `result == ok`，分母 = 跑完的题 | `v0` | 批次 0 及更早（`mix6x*`、`chaos-*`、`keys-mix*`、`t_chips`/`t_rows`/`t_form`）、`t_trap2-1`/`-2`、`prof2` | 与 v1 **不可比**（行前会打 `[口径 v0 不可比]`） |
| **v1** | 五判定 + 声明分母（见上节） | `v1` | **批次 1–4 全部**（`t_trap` 起） | **跨批可比**；批内 `scripts_sha` 分裂要单独标注（那是**驱动版本**，不是口径） |
| **v2** | v1 定义**一字不改**，只把 `a_hit_but_failed` 拆成 `_wrong_target`/`_twin`，行标签改 `v2` | `v2` | 批次 5（`t_trap*` 场景） | 与 v1 的 `pass/decided/false_*` **逐列可比**（拆分只是把一个合计列展开成两列） |
| **v3** | v2 定义**一字不改**，加两样：race 的 variant 集合纳入 `swap_race_timer` 并拆出 `race_press_after_guard`（"**守门抓帧之后**才发生的过期按压"），以及守门逐门样本分位 `gate_samples`/`gate_p50`/`gate_p95` | `v3` | 批次 6（`t_trap5` 场景） | 与 v2 的 `pass/decided/false_*`/`a_hit_but_failed_*` **逐列可比**；**race 分母不可与批次 5 的 `0/0` 并列解读**（批次 5 的 `swap_timer` 定时 600–1000 ms 落在守门帧之前，机制上不可能产生过期按压，见批次 6 一节） |

各批 `scripts_sha`（sha256/12，覆盖 `gym_run.py` + `gym_app.py` + `score.py`；**sha 相同才是同一版驱动**）：

| 批次 | 文件 | `scripts_sha` | 口径 | 通道 / 备注 |
|---|---|---|---|---|
| 1 | `t_trap-1..6.json` | `a04562c51c16` / `1a3c899331ff` / `31a244a3e448` / `03bf345d2b41` / `918619efcec0` / `ea755d12c9c7` | v1 | 键 + `--bg`（6 次同题重跑） |
| 2 | `t_trap2-3.json` | `f09f2ed21363` | v1 | 键 + `--bg`（`t_trap2-1`/`-2` 是 v0，不并入） |
| 3 | `t_trap3-2.json` | `2f4bad88da13` | v1 | 键 + `--bg`（**定稿引用**） |
| 3 | `t_trap3-3/-4.json` | `8876a1dd0a09` / `5c4952ece8bf` | v1 | 键 + `--bg`（修后复跑） |
| 3（失败批） | `t_trap3-1.json` | `785cfe9412d6` | v1 | 鼠标 —— **任何数字都不引用**（前台被抢占，坐标/时序失真） |
| 4 | `t_trap4-1.json` | `5e3d5949b6e9` | v1 | 鼠标（前台真实鼠标） |
| 5 | `t_trap4-4.json` | `ebfc7dce831a` | v2 | 鼠标（前台真实鼠标）；同批另有 `-2` `4b44d9cb74d8`、`-3` `4cbcd072f027` 两次中途批（判据修正，见批次 5 一节） |
| 6 | `t_trap5-1.json` | `9db420c422a2` | v3 | 鼠标（前台真实鼠标）；48 题 = 批次 4/5 的 38 题**逐题同构** + 10 题 `swap_race_timer` |
| 6 | `t_trap2-w6b-control/chaos35/chaos70.json` | `ee68f457577d` | v2（标签） | 键 + `--bg`；批次 6 的 chaos 三批（含 `window_by_title` 守卫修复后的 sha）|
| 6 | `t_trap2-w6c-control/chaos70.json` | `ee68f457577d` | v2（标签） | 键 + `--bg`；**逐批即时打分**的复跑（0.35 档没有 `score.py` 数字） |
| 7 | `t_trap2-w7-control.json` | `481154ca264d` | v2（标签） | 键 + `--bg`；**只改留档命名（欠账 #14），判定逻辑一字未改** ⇒ 与批次 6 逐格可比（控制批 60/60 逐格相同） |
| 7 | `t_trap2-w7-move70.json` | `481154ca264d` | v2（标签） | 键 + `--bg`；⚠ **修复前**、33/60 早退，**不可引用为 move 类定稿**，只用于定位根因 |
| 8 | `t_trap2-w8-move70/move35/slow35/slow70/popup35/popup70.json` | `f598406cfc70` | v2（标签） | 键 + `--bg`；chaos 四类 × 2 强度，**探索性·不并入定稿**；每批自带 `-state.json` / `-events.jsonl` 留档。⚠ **与批次 7 在读题守门这条路径上不可直接比**（本批改了退化分支；批次 1–7 已公布数字不受影响）——见「批次 8 结果」的**本批必读**两条 + 一条勘误 |
| 9 | `t_trap6-1.json` | `f473ff21ad09` | v3 | 鼠标（前台真实鼠标）；**只动计时点与记账**（#10 扣帧、#11 逐题行 `detail`、`_redo` 续带），判定逻辑一字未改；与批次 6 **逐题同构**（同 seed）；自带 `-state.json` / `-events.jsonl` |
| 10 | `t_trap2-w9-move70.json` | `5dedae26c6e8` | v2（标签） | 键 + `--bg`；**只换守门的重读框**（新增 `ask_box_now()` 每帧用像素段重算；`ask_cells`/`ask_delta` 指纹基线、匹配路径、阈值、`press_guard` 分支一字未动）⇒ 与批次 8 **协议逐项相同、可逐题对照**（`chaos_planned 49 / chaos 49` 也相同）；自带 `-state.json` / `-events.jsonl`。⚠ 与批次 7/8 在"守门重读这条路径"上不可直接并列（本批改了框来源）——见「批次 10 结果」①③ |
| 11 | `t_trap7-1.json` | `8da029edccbc` | v3 | 鼠标（前台真实鼠标）；**只改抓帧失败的处理**（#17：`ShotFailed` 异常类型 + `_shot` 重试 3 次/间隔 0.2 s + main 包 `try` 并把已完成的题写成 partial run json + 返回码 3）；判定逻辑/匹配路径/阈值/`press_guard`/`_redo` 一字未动，`score.py` 只加两行 `!! PARTIAL RUN` 警示 ⇒ 与批次 9 **逐题同构**（同 seed、同协议）；自带 `-state.json` / `-events.jsonl`。同段另有两条 partial 构造产物（`t_trap7-empty6.json` 4354 B、`t_trap7-minim6.json` 4546 B）——**只做路径验证，不并入任何成绩** |
| 16 | `t_trap2-w17-popup70-mouse.json` | `780adce4017e` | v2（标签） | 鼠标（前台真实鼠标，非 `--bg`）；**重落第十三段选项 D 补丁 + 拆「漏一次点 ⇒ 整题死锁」耦合**（净 +30 行，只落在清障路径内；**判定逻辑一字未动**）⇒ 与批次 4/5/6/9/11 **不是同一版驱动**（`scripts_sha 186edbd9c024` → `780adce4017e`、`gym_run.py 87470aaff5593330` → `3fa0e4ba4b1b9679`），差异只在 `--chaos` 下的清障路径（非 chaos 批不受影响）；自带 `-state.json` / `-events.jsonl`。⚠ 本表**没有**批次 12/13/14/15 的行（它们的 `scripts_sha` 写在各批次节与 `STATE.md` 接续点里） |
| 17 | `t_trap2-w18-popup70-mouse-r1.json` | `780adce4017e` | v2（标签） | 鼠标（前台真实鼠标，非 `--bg`）；**拆耦合实战第 1 批**（seed 20251008，16 题 `popup@0.70`）：`popup_seen 10 / dismissed 10 / failed 0 / interferences 10` ⇒ **补点 0**；16/16、退出码 0；**1 次 app 侧 `blocked`**（task 12，`swap_timer`，该题最终 `ok`）。驱动与批次 16 同一版（`gym_run.py 3fa0e4ba4b1b9679`） |
| 18 | `t_trap2-w18-popup70-mouse-r2.json` | `780adce4017e` | v2（标签） | 同一版驱动；**拆耦合被实战触发的那一批**（seed 20251009）：`popup_seen 8 / dismissed 8 / failed 0 / interferences **9**` ⇒ **同一遭遇点了两发并被清掉**（补点 1 次）、**16/16**、退出码 0、无 `blocked` |
| 19 | `t_trap2-w18-popup70-mouse-r3.json` | `780adce4017e` | v2（标签） | 同一版驱动（seed 20251010）：`popup_seen 10 / dismissed 10 / failed 0 / interferences 10` ⇒ 补点 0；**15/16、退出码 1** —— 那一题落在**已知的 `swap_timer` 时序竞争类**（`race 1/1`、`wrong_target 1`），**不是弹窗通道问题、也非早停**（`partial False`、`exit_reason None`） |
| profiling | `prof1` / `prof2` / `prof3` | 无 / `264a87d48d4c` / `264a87d48d4c` | 无 / v0 / v1 | 成本对照，不参与通过率 |

**引用规则（按用户审计定死，缺一条就算引用越界）**：

1. `race` 与 `guard-blind` 的数字**必须带分母**，分母是"本批真正按了过期 ask 的次数"，**不是题数**
   （批次 4 的 `1/1` 与批次 3 的 `5/5`、`3/3` 不能并列成"改善了 5 倍"）；分母 < 5 时标"**非缓解**"。
2. **synonym 鼠标通道的成绩一律不引用**（批次 4 的调查结论：那条路是设计使然的失败）；
   有效成绩 = 键通道 `synonym_button 6/6` + `synonym_only 4/4`。
3. `no_badge_fill` 的 0.50 档 D1 = **57**（批次 3 ≤ 65、批次 4 三题全 57）是同一现象：阈值带 66–69 是空的。
4. 折叠表 `_code` **只用于"找目标"（容错），判变化一律用 `_plain`**（依据：DESIGN 修订 r10；`TANGO`/`TANGQ` 折叠后同码）。
5. 批次 6 的 `t_trap2` chaos 三批在 json 里打的是 **`v2`**（`gates` 按场景名分流：`t_trap5→v3`、`t_trap*→v2`）——那是**计分算法版本**，不是代码版本；代码版本一律看 `scripts_sha`（本批 = `ee68f457577d`）。
6. 驱动的 `disturbances: N fired` 只数**弹窗型**干扰（`dismiss_interference`，`gym_run.py:868/893/912`，仅在 `--chaos` 时调用 `gym_run.py:3271`）——`rebuild` 型干扰不进这个计数。**引用 chaos 注入率一律用 app 侧 `gym-events.jsonl`**（`chaos_planned` / `chaos` 事件）。
7. run json 的 `events` 字段是**一个路径**，`score.py` 就是**按这个路径去读真值**的（`join_truth`，`score.py:162-169`），而 app 每次启动**覆盖写**同一文件 ⇒ ①只有**最后跑的那批**能把真值联对；②**事后重打任何"非最后一批"都会静默错联**——实测把 0.70 批跑完后再打 `t_trap5-1.json`，得到 `36/48`、`MISMATCH 11`、变体表变成 `t_trap2` 的（真值是 `37/48`、`MISMATCH 0`）。⇒ **已公布数字全部是"跑完立刻打分"的**（见 `SCORE.md` 批次 6 raw 块前的说明）；事后复核必须 `score.py <json> --events <该批留档的 events 副本>`，而当前默认 state/events 名是固定值 ⇒ 每批留档是欠账（STATE §7 #14）。跨批比较 stale/race 时要么逐批即时打分，要么只引用自包含的 `runs[]` 计数。

## Clean board (no disturbance) - `mix60f.json`

    59/60  98.3%   2612 ms/task
    t_button 10/10  t_chips 10/10  t_form 9/10  t_menu 11/11  t_rows 9/9  t_toggle 10/10

    python gym_run.py --tasks 60 --seed 20251007 --keys --bg --max-repeat 3 --json-out mix60f.json

口径 v0 · 通道 keys · 读题 44/16（屏/文件）· 源文件与数字一致 ✓（`ms` = 判定耗时 2612，
含抓图的 wall = 3223）

The single miss is a look-alike glyph the *screen* is ambiguous about (the app generated
`C02S`, the banner OCR read `CO2S`, and the app compares strings exactly). Left failing on
purpose: the driver must not read the answer out of the state file to win.

## Disturbed board (`--chaos 0.5`, one kind at a time, 20 tasks)

    kind      score        ms/task   reads     what breaks
    rebuild    2/6   33%    2561    12/1      ask re-rolls: driver re-reads the ask, then clicks the
                                              wrong control (matched PRISM11 for `mica36`); in t_rows
                                              the row list/hint letters move and the press never scores
    move      17/20  85%    2114    22/5      layout shifts under a live slider drag
    popup      4/7   57%    1671     6/9      window on top hides part of the banner -> ask read is
                                              truncated (`nvoke the ... menu`, no `Indigo`) -> act unknown
    slow      18/20  90%    2796    15/8      verdict arrives 1.5-3.2 s late; a re-plan that re-clicks is
                                              scored WRONG on the menu/t_form tasks

    python gym_run.py --tasks 20 --seed 20251007 --chaos 0.5 --chaos-kind rebuild --keys --bg --max-repeat 3 --json-out chaos-rebuild.json

口径 v0 · 通道全部 keys · `rebuild` 只有 6 题（`--max-repeat 3` 早退，分母是缩小过的）

Both weak kinds are recovery problems, not perception problems: the driver notices the
change (`replanned`, `ask_replan_read`, `interferences` are all recorded) but then acts on a
stale plan - a fuzzy label match from before the rebuild, or a banner read taken while a
dialog was covering it. The next fixes belong in `gym_run.py`:

1. dismiss interference *before* reading the task, not only while waiting for the verdict;
2. after a re-roll, re-locate the target from a fresh frame and require an exact label match
   before clicking (the rebuild miss was a fuzzy false positive);
3. re-read the hint badge immediately before pressing it, and if no verdict arrives after a
   bound-key press, re-read the row list instead of re-pressing the same key.

## Scenario singles (all keyboard channel)

    scenario    score   ms/task   run file
    t_button     1/1              keys-btn.json        ⚠ 数据源存疑·勿引用
    t_chips     10/10    2125     keys-chips9.json     ⚠ 数据源存疑·勿引用
    t_form      13/14    5214     form-fix5.json
    t_menu       7/7     2605     keys-menu7.json      ⚠ 数据源存疑·勿引用
    t_rows      12/12    2693     rows-fix2.json
    t_toggle     8/8              keys-tog.json        ⚠ 原始文件已丢失·勿引用

**两种标注不是一回事**（用户 2026-10-04 指出）：

- **不可比** = 算法换了，旧数字本身没错，只是不能跟新数字比 —— 本表**所有** v0 行都属这一类；
- **不可信 / 存疑** = 旧数字本身可能是错的（源文件被覆盖、引用错位、原文件丢失） —— 只有上面标 ⚠ 的四处，
  它们的数字**不可复现**，看到"8/8"别当真：标注为「数据源存疑·勿引用」。

口径 v0 · 通道 keys · 数字未改，源文件核对如下（`audit_runs.py` 逐行输出）：

| row | 源文件现状 | 判定 |
|---|---|---|
| `t_button 1/1` | `keys-btn.json` 现为 **8/8**、870 ms（wall 1502） | **数据源存疑·勿引用**：文件被后来的跑测覆盖，1/1 不可复现 |
| `t_chips 10/10 2125` | `keys-chips9.json` 现为 **14 题 7 对**、4801 ms（读题 14/1） | **数据源存疑·勿引用**：同上，被覆盖 |
| `t_form 13/14 5214` | `form-fix5.json` 13/14 ✓；5214 是 wall，`ms` = 4583 | 对得上（口径是 wall）✓ 只属"不可比" |
| `t_menu 7/7 2605` | `keys-menu7.json` 现为 **8/8**、1837 ms（读题 1/7） | **数据源存疑·勿引用**：被覆盖 |
| `t_rows 12/12 2693` | `rows-fix2.json` 12/12 ✓、2694 ms | 对得上 ✓ 只属"不可比" |
| `t_toggle 8/8` | `keys-tog.json` **不存在**（按文件名搜 `*tog*` 只剩两个：`gym-tog.json` = 8/8 但**鼠标通道** 29 clicks / 0 keys、`gym-tog-dbg.json` = 3 题 1 对，也都是鼠标） | **原始文件已丢失·勿引用**：找不到任何 keys 通道、t_toggle 8/8 的 run |

`t_toggle 8/8` 这行不再往下猜：全部 json 里跑过 t_toggle 且 **keys 通道**的文件，没有一个是 8/8（见 `audit_runs.py` 输出）；
现存的 `gym-tog.json` 虽然分数形状一样（8/8），但它是**鼠标通道**（29 clicks、0 keys），所以既可能是"那个 keys 文件被删/覆盖了"，
也可能是"当时把鼠标那轮记成了 keys" —— **两种都无法验证，一律标存疑，不当证据用**。

三处"数字对不上"都不复算：v0 的这些明细没有 `scripts_sha`/`app_args`，覆盖后就无法还原是哪一次跑测。
**结论：v0 的单场景行只在"文件仍在且数字一致"时可引用**（`form-fix5`、`rows-fix2`），其余一律标「数据源存疑·勿引用」。

## §2 的"不可比"三类（v0 标注）

1. **键通道 + 屏幕读题 100%**：`chaos-p0.5.json` 8/8、读题 8/0 —— 可引用，但仍无 `t_trap` 的拒绝判定；
2. **键通道但含 file-read**：`mix60f.json` 16、`chaos-popup.json` 9、`chaos-slow.json` 8、
   `chaos-move.json` 5、`keys-menu6.json` 10 —— 测的是"读文件兜底 + 读屏"的混合；
3. **鼠标时代**：`gym-12.json`（23 clicks/1 scroll）、`gym-menu.json`（12）、`gym-mix.json`（14+1 drag）、
   `gym-mix2.json`（31）、`gym-mix3.json`（86+5 drags）、`gym-tog.json`（29）—— 坐标 bug + 通道不同，其中
   多数还键鼠混用。

## `t_trap`（v1 口径，**已跑 4 次：18/24 → 24/24 → 24/24 → 24/24**）

新口径的第一批：8 类 × 3 题 = 24 题，**定位是 smoke test，不是统计结论**（3 题/类的命中率只有
0/33/67/100 四档）。跑法与分列规则见 `D:\DSH\vision-work\DESIGN-refusal-scoring.md` §3；
`variant` 必须分列（`prose_with_button`/`prose_only`、`synonym_button`/`synonym_only`、
`alpha035`/`alpha050`/`alpha065`），不得合并。

跑法（**必须用 venv 解释器**，PATH 上的 `python` 已换成没有 numpy 的 3.14）：

    cd D:\DSH\vision-work\sol\sandbox && D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py \
      --scenario t_trap --tasks 24 --seed 20251007 --keys --bg --max-repeat 3 --json-out t_trap-N.json
    D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap-N.json

> **区分度警告（用户 2026-10-04 要求写进这里）**：`24/24` 连五次是**"这批题太简单"，不是"系统对了"**。
> 两个已知盲区：① `swap_mid_task` 三次换题全在**按键之前**（`a_hit=0`）⇒ "A 做对、屏幕随后才变"
> 这条路径从未被测到；② `half_transparent` 三档全部照点通过 ⇒ 控件能否操作由 `[k]` 徽章 + 标签决定，
> **不由填充率决定**，所以这批实际没测到任何阈值。③ 每类只有 3 题 ⇒ 命中率只有 0/33/67/100 四档。
> 第二批 `t_trap2`（85 题、每类 ≥10，含 `swap_after_press` 与 `alpha020`/`alpha030`）专治前两条。

| run | v1 | 判定 | 分变体 |
|---|---|---|---|
| `t_trap-1.json`（修前） | 18/24 75.0% | `answered_right=10 wrong_target=3 false_refusal=3 refused_right=8`；`false_refusal 3/16 (18.8%)` | `prose_with_button 0/2`、`synonym_button 1/2`，其余 1/1 |
| `t_trap-3.json` / `prof3.json` / `t_trap-4.json`（修后） | **24/24 100%** | `answered_right=16 refused_right=8`；`false_refusal 0/16`、`false_accept 0/8`、`swapped 3 a_hit 0`、`replan 3` | 全部 `1/1` 或 `2/2` |

两个根因 + 修法（都写进设计 r5）：① 匹配器选中**正文里的同名词**（无 `[k]` 徽章）就直接拒答 ⇒ `find_all` +
`try_other_occurrences`（只试带徽章的其他出现）；② `swap` 改了 ask 但控件原地不动，`frame_task_i` 与块级复验
都看不见 ⇒ `band_sig`/`ask_changed` 在复验那一帧比对 ask 框指纹。**阈值有实测证据**（`t_trap-6.json` 三题换题）：
变化格数 `ask_cells` = 4 / 11 / 9（判据 ≥3），而整框均值 `ask_delta` 只有 3.7 / 9.2 / 5.7 —— 先用的"均值 > 12"
必然漏判，故改用格数。`ask_moved=1`、`replans=1`、`replan_why=ask re-rolled` 都记在题目记录上。

## `t_trap2`（批次 2 = `t_trap++`，85 题，每类 ≥10，v1 口径）

命令同上一节的 `t_trap`，只把 `--scenario t_trap` 换成 `--scenario t_trap2 --tasks 85`。

| run | v1 | 判定 | swap 分变体 | half_transparent 分变体 |
|---|---|---|---|---|
| `t_trap2-1.json`（修前） | 53/57 早退 | — | 未跑到 | 未跑到 |
| `t_trap2-2.json` | 80/85 94.1% | `wrong_target=5` | `swap_after_press 10/10  a_hit=10`、`swap_timer 3/5  a_hit=0` | 五档全 2/2 |
| `t_trap2-3.json`（定稿） | **83/85 97.6%** | `answered_right=55 wrong_target=2 refused_right=28`、`false_refusal 0/57`、`false_accept 0/28`、`decided 100%` | `swap_after_press n=10 a_hit=10 wrong=0`、`swap_timer n=5 a_hit=0 wrong=2` | `alpha020/030/035/050/065` 各 2/2 |

**批次 2 判读**：
- **`a_hit` 第一次不为 0**（10/10）⇒ 设计 §5.2 三种情况里的第一种（A 做对 + B 做对 ⇒ 通过 + `a_hit=1`）
  第一次被实测到；第二种（A 对 + B 错 ⇒ `a_hit_but_failed=1`）**仍然 0 例**，别当成已验证。
- **`half_transparent` 五档全过 = 无区分度·不可作为 fill 阈值证据**：靶子只把**填充块**按 alpha 混合
  （`gym_app.py:942-943` 的 `blend(BG, "#dbe6f2", alpha)` / `blend(BG, "#8595a8", alpha)`），而**标签文字
  是全不透明的**（`gym_app.py:944-945` 的 `c.create_text(..., fill="#12263a")` 没有过 `blend`）⇒ 五档里
  驱动读到的标签和 `[k]` 徽章**一模一样**，只有背景变淡；键通道下能按下去的前提就是找到徽章，所以
  alpha 0.20（已低于正文自身的 0.213）也照过。**这一类当前在结构上产生不了 fill 边界**，别把 2/2 读成
  "阈值 0.45 以下也能用"。要测阈值两条路：① 一行改动——让文字也走 `blend`，同一批 10 题重跑，测的是
  **驱动的读数下限**（最便宜）；② 另做"淡控件 + 无徽章"类，测**没有徽章时的像素可见性判断**（要新能力，
  规则须先离线冻结，不能在受测题上现调）。
- 剩下的 2 个失败全是 `swap_timer`，**已由靶子事件流直接证明是竞态**（不再是推测）：
  `#10` 靶子记 `trap_swap a=INDIGO b=XENON why=timer a_hit=False`，随后 `done detail.clicked=INDIGO`
  ——换题在**复验那一帧与按键之间**落地，驱动按的是被替换掉的旧 ask（`ask_cells=1`/`#13` 为 `0` ⇒ 复验
  确实没看见变化）。**这条不当作策略错误，但也不从分母里剔除**：看着没变就按下去是真实能力边界
  （窗口约 70–150 ms），剔除等于把它藏起来。新增靶子事件 `trap_stale_press` + 计分行
  `race(pressed the replaced ask) N/M`（`score.py` selftest 29 项）。**`race` 的性质写死：它是 `wrong_target` 的
  **子集标注**（`race_wrong_target ⊆ wrong_target`）、**保留在分母里**、**计分口径仍是 v1**（不升 v1.1、旧数据
  仍可比）——未来不要把它当成"新增类别"去动分母。**
  ⚠ 批次 2 那两行显示 `0/0`，意思是**当时还没有这个字段**，不是"没有竞态"——同一批已用事件流证明 2 起。
- `2330 ms/题` 的构成（别当成普遍变慢）：这是 `wall_ms`（含抓图）均值，判定耗时均值只有 `1148 ms`。
  按类拆开看，`swap_after_press` **10 题每题 6233 ms**、占整轮 198 s 的 **31.4%**，其余每类 1.5–2.7 s：
  按 A 正确后靶子换题，驱动等一个**永远不会来的判定**（旧 ask 不再评分）约 5 s 才重规划。下一批可优化：
  等判定时顺带比对 banner 指纹（复用已有的 `band_sig`，不额外抓帧），能省掉这 ~5 s。
- 驱动侧三个新 bug（都在这批里暴露、已修）：① 同义动词只试第一个词、命中正文就拒答（ask "close the
  notice"、正文里有 "Close"、真控件是 "OK"）⇒ 只接受**带徽章**的命中，继续试下一个同义词；② `SYNONYM_ACT`
  没有 "acknowledge" ⇒ "acknowledge the alert" 整句解析不出来 ⇒ 补上，并把动词匹配改成**容错一位 OCR**
  （实测屏读 `acknowledae`）；③ ask 解析不出来时驱动**什么都不做**（靶子不前进）⇒ 现在改为**拒答**并记
  `ask_unparsed=1`（这是一次"决定"，不再是冻结；批次 2 之前它会让 `--max-repeat 3` 把整批砍掉）。

**provenance（每个 run json 都写，逐行标注才可比）**：

| run | `scripts_sha` | `gates` | 备注 |
|---|---|---|---|
| `t_trap-1..6.json` | `a04562c5` / `1a3c8993` / `31a244a3` / `03bf345d` / `918619ef` / `ea755d12` | v1 | 六个不同的驱动版本，互不可比 |
| `t_trap2-1.json` / `t_trap2-2.json` | `82f71c8f` / `5829c8b9` | **v0** | `gates` 判定的 bug（`t_trap2` 被写成 v0）在这两次之后才修 |
| `t_trap2-3.json`（定稿） | `f09f2ed21363` | v1 | = `gym_run.py`+`gym_app.py`+`score.py` 三个文件的 sha |
| `prof2.json` / `prof3.json` | `264a87d48d4c` | v0 / v1 | 同一驱动，可作为 §6 基准对 |

> **勘误（用户审计第 1 条要求）**：`t_trap2-1.json` / `t_trap2-2.json` 的 `gates` 字段被错写为 `v0`
> （`gates` 按场景名判版本的 bug 在这两次之后才修），**实际场景是 `t_trap2`**。这两次的判定数字
> （`53/57` 早退、`80/85`）**不作为 v0 证据引用**，也不与 v1 行混比；`score.py` 打印它们时走的是 v0 行，
> 见本节的表注。凡按 `gates` 字段索引历史 run 的人，必须同时看 `scripts_sha`。

> 记法澄清（`screen` 列）：真正的判据在 `gym_run.py:1498` —— **归一化后的屏读文本包含靶子真值**才算 `screen`，
> 否则记 `file`（此时**仍然用屏读文本**行动，只有屏读为空时才回落到文件）。所以 `file` 那一列的意思是
> "屏读没有完整覆盖真值"，**不是"这一题没用屏幕"**，也不是"屏读失败"。
> `t_trap2-3` 的 16 行 `file` 全部是 OCR 滑字（`GAMM.`/`TUND`/`XENON2`/`acknowledae`），逐题核对结果是
> **10 题 acted + 6 题 refused，16/16 `result=ok`** ⇒ 没有"该答却拒"藏在里面。
> 另：驱动摘要里的 `asks read off the screen 81 / from the state file 17` 是**按读取次数**（85 题 + 13 次
> 重规划 = 98 次读取），`score.py` 的 `screen 69/85` 是**按题目记录**，两个数不矛盾。


## 批次 3 开工前的离线标定（**曲线先交**，尚未跑批；见 DESIGN r8 / §3.2）

口径：**靶子 ground truth = `OPERABLE_ALPHA = 0.45`**（α ≥ 0.45 可点；低于它的点击被吞、记 `ignored_click`
并立刻结束本题）。整控件（轮廓+填充+**文字**）按 α 淡化、**不给徽章**；`nb100` = 无徽章全对比度对照档。
**驱动规则在测量前预注册**（`probe_fill_curve.py` 文件头，看过曲线不得回改）：D1 = 标签 OCR 框扩 10/6 px 内
`|L − base|` 的 90 分位（`base` = 外环 34/22 挖掉内框的灰度中位数，只在驱动自己的 body 裁剪上算）；
**`T_VIS = round(0.5 × D1(1.00))`**；当且仅当 `ocr_found and D1 ≥ T_VIS` 才点击。

实测（`fill_curve.json`：21 档 × 3 帧、种子 20251007、真实 app 帧、全程后台抓帧）：

| α | 0.05 | 0.10 | 0.20 | 0.30 | 0.35 | 0.44 | 0.46 | 0.50 | 0.55 | 0.60 / 0.65 / 0.70 | 0.75 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OCR 定位 | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **✗ ✗ ✗（9 帧全缺）** | ✓ | ✓ |
| D1（中位） | – | 15 | 28 | 42 | 49 | 62 | 65 | 71 | 77 | – | 104 | **137** |

⇒ **D1 ≈ 137·α**，**`T_VIS = 68`** ⇒ 驱动的可见性门槛落在 **α ≈ 0.50，高于靶子的 0.45**。**预期**（跑批前写下，
跑完对照，不许改规则）：0.20/0.30/0.35/0.44 全部**该拒且会拒** ✓；**0.46 的 5 题（该答）会误拒** ✗；
0.50 起可点 ✓；**0.65 的 3 题取决于中间带 OCR 空洞是否在真实题面上复现**（实测，不预设）。

两条如实记录的缺陷：① **D2（内框 2 px 边框环）在所有 α 上都是 0.0** ⇒ 死诊断，只报不用；
② **OCR 定位非单调**：0.10 就起读、0.55 能读，**0.60/0.65/0.70 三档 9 帧全读不到**、0.75 又能读 ⇒
链条失败在**中间带**而不是最淡端。

诚实边界（**不许夸大**）：D1 量的是"**淡 vs 强**"，**不是"控件 vs 正文"**——空白处 D1 = **0.0**，
但**正文文字**的 D1 很高（文字本身高对比）。所以这条规则**只当可见性判据**，不替代徽章通道去判
`prose_only`/`bold_prose`/`disabled`/`two_close_names` 那批"该拒"类 ⇒ **批次 3 的鼠标跑只覆盖语义明确的类**
（`no_badge_fill` 28 + 难 swap 8 + `swap_after_press` 10 + `swap_timer` 5 + `half_transparent` 10 +
`synonym` 10 = **71 题**），徽章判据的 5 类（50 题）**留在键通道**。

交叉验证（`probe_vis_rule.py`，真实帧）：α=0.30 契约 **42.0** = 驱动 **42.0**、α=0.55 **77.0** = **77.0**、
空白 **0.0**、决定 refuse/click 正确、`0 failed`；`score.py --selftest` **29/0**。
新 `scripts_sha = bd4c3b0ab2ea`（批次 3 的 run 会带这个值；与 `f09f2ed21363`（批次 2 定稿）**不可互比**）。

**通道约束（决定跑法）**：`probe_click_bg.py` 记录"**Tk ignores posted mouse input entirely**"，后台鼠标模式
实测 **0/3**（36 次投递点击全不生效）⇒ 无徽章类没有键通道 ⇒ **含 `no_badge_fill` 的跑批必须前台 + 真实鼠标**
（窗口盖住屏幕、指针会被移动）。标定曲线本身只需抓帧，**已全程后台完成**。

> 过程记录（诚实留档）：第一次扫描（21 档）**全部 `found=0`** —— 原因是我的探针场景 `t_probe_fill` 建了
> canvas 却**没有 pack**，控件从未上屏（OCR 只看到 banner 和 F9 底栏）。该次结果存档为
> `_fill_curve/fill_curve-VOID-unplaced-canvas.json`，**不作为曲线**；修好上屏 + 加"全对比度预检"后重扫，
> 预检打印 `found 'EMBER' at alpha 1.00 (score 1.0)`。规则本身（D1/选择规则）一行未动。

### 跑批前定死的四条（用户审计后）

**① 分母：`t_trap3` = 71 题，单通道（鼠标），单一分母。** 不是 121。
71 = `no_badge_fill` 28（nb020/030/035 各 3 + nb044×5 + nb046×5 + nb050/065/100 各 3）
+ 难 swap 8（`swap_hard_press`×5 + `swap_hard_timer`×3）+ `swap_after_press`×10 + `swap_timer`×5
+ `half_transparent` 10（五个 alpha 各 2）+ `synonym` 10（button 6 + only 4）。
**徽章判据的 5 类（`prose_same_word` 10 / `two_close_names` 10 / `disabled` 10 / `flat_button` 10 /
`bold_prose` 10 = 50 题）属于 `t_trap2`（键通道）**，其定稿是 `t_trap2-3.json`（83/85，
`scripts_sha f09f2ed21363`）。**理由**：这 5 类的判定问的是"有没有 `[k]` 徽章"，而鼠标通道里
`control_visible` 见到徽章就直接放行（等于用键通道的规则回答鼠标通道的题），
且 `disabled`/`two_close_names` 这类"该拒"题在鼠标模式里会变成"点了才发现没用"——问的是另一个问题。
两类通道混进同一个分母，会让通过率由"我选了哪个通道"加权，正是 v0 口径被废弃的原因。
若日后要用新驱动复核那 50 题，那是**键通道的回归跑**，另开一行、另写 `scripts_sha`，不并入本批。

**② 边界带预期误拒（设计内，不是回归）**：靶子阈值 `OPERABLE_ALPHA = 0.45`、驱动阈值 `T_VIS = 68`
（≈ α 0.496）⇒ 中间有一条 **≈0.046 宽的"靶子可点、驱动看不见"带**。nb046 的 5 题（该答）就在这条带里，
**预期 5/5 `false_refusal`**。跑完 `false_refusal` 若正好多出这 5 例，是设计压中的边界，不是能力退化；
反过来说，**若 0.46 有题目被答对，才说明 D1 与真实帧有偏差**（那需要单独解释，不能当成绩）。

**③ 已知异常：OCR 定位在中间带空洞**（0.60/0.65/0.70 三档 9 帧全读不到、0.75 又恢复，0.10 起读、
0.55 能读）⇒ **nb065 的 3 题结果不可预设**，实测后单独报；如果它们失败，原因是"读不到"而不是"看不见"，
两件事不能混。这条在 `DESIGN` §3.2 与本节曲线表里都有。
**实测更新（`t_trap3-2.json`）：nb065 的 3 题全部读到并答对（3/3），空洞没有在类自身的刺激上复现** ⇒
曲线 1 的空洞是**单一标签刺激**下的现象（`t_probe_fill` 只有一个 5 字母标签，全文只有一处该词），
不能推广成"这类字在 α 0.60–0.70 必然读不到"。

**④ `scripts_sha`**：本批（`t_trap3`）计划时写的是 **`785cfe9412d6`**，**实际跑批（`t_trap3-2.json`）记录的是 `2f4bad88da13`**
= `gym_run.py`+`gym_app.py`+`score.py` 三个文件的 sha256 前 12 位（差值来自本轮修 A–E 与新增标定场景 `t_probe_fill2`）。两者都与批次 2 定稿
`f09f2ed21363` **不可互比**；标定阶段的交叉验证值是 `bd4c3b0ab2ea`。

> 口径细节（本批新增）：`refuse()` 现在**在鼠标通道也按 F8** —— 拒绝键是协议不是答案（靶子每个 trap 题都
> 武装它），`--keys` 决定的是"能不能用提示徽章去动手"，不是"拒绝能不能被看见"。不这样改，鼠标通道里
> 的拒答只写进记录、靶子永远收不到 ⇒ 该拒的题会全部变成超时。

## 批次 3 结果（`t_trap3-2.json`，鼠标通道，71 题计划，实际 64）

**v1 行**：`t_trap3 v1 45/62 72.6% decided 100.0% screen 59/62 replan 17 1145 ms/task extra_attempts 2`
直方图 `answered_right=31 wrong_target=9 false_refusal=8 refused_right=14`；
`false_refusal 8/48 (16.7%) false_accept 0/14`；`swapped 23 a_hit 15 a_hit_but_failed 0`。
**只跑了 64/71**：第 61–63 题（`synonym_button`）连续三行 `NONE`（13.5 s/题）触发 `--max-repeat 3` 早退（原因见下"鼠标通道的已知边界"）。
分母口径不变：v1 的 62 是 join 后按 `task_i` 折叠的结果（`extra_attempts 2`）——少跑的题不在分母里，不是缩小分母。

### ① `by_alpha`（用户第一组数）

| α | n | 答对 | 拒对 | 误拒 | 误受 | 驱动 D1（逐题） |
|---|---|---|---|---|---|---|
| 0.20 | 3 | 0 | 3 | 0 | 0 | （3 题全是"没找到标签"，无 D1 读数） |
| 0.30 | 3 | 0 | 3 | 0 | 0 | 40.3 / 40.0 / 42.0 |
| 0.35 | 3 | 0 | 3 | 0 | 0 | 40.0 / 44.1 / 40.0 |
| 0.44 | 5 | 0 | **5** | 0 | 0 | 56.2 / 47.0 / 47.0 / 47.0 / 47.0 |
| 0.46 | 5 | 0 | 0 | **5** | 0 | 53.0 / 62.0 / 50.0 / 65.0 / 57.0 |
| 0.50 | 3 | 0 | 0 | **3** | 0 | **54.0 / 54.0 / 57.0** |
| 0.65 | 3 | **3** | 0 | 0 | 0 | 70.0 / 70.0 / 74.0 |
| 1.00 | 3 | **3** | 0 | 0 | 0 | 125.0 / 78.0 / 102.0 |

- **0.46 恰好 5/5 误拒** ⇒ 跑批前写下的"边界带预期误拒"被数据压中，**不是回归**。
- **0.50 是 3/3 误拒**，而预测是"0.50 起可点" ⇒ **驱动有效门槛在 (0.50, 0.65]**，比预注册的 α≈0.496 高。
  阈值一字未改（`T_VIS = 68`），原因是 **D1 随标签形状漂移**（下条）。
- **0.65 三题全读到并答对** ⇒ 曲线 1 的"OCR 中间带空洞"在类自身刺激上**没有复现**。
- **⚠ 标定刺激与受测刺激不同分布（本轮审计新增，必须显眼）**：`T_VIS = 68` 是用**曲线 1 的刺激**（空 body 上
  单个 5 字母标签）标定的，真实题面却是"3 控件、2 列网格、满对比度诱饵下的 4 字母标签"。同一 α=0.50：
  曲线 1 的中位 **71**，真实题面三题 **54 / 54 / 57**（差 14–17 分）⇒ **0.50 的误拒不是阈值算错，而是
  标定刺激与受测刺激的 D1-α 关系不同**。预注册要求刺激一致，这个前提**没有被满足**；事后改 `T_VIS` 会违反
  预注册，所以不改，但**下一批必须用匹配刺激重新标定**：刺激 = 类自己的画笔、链 = 驱动自己的链，且
  α=1.00 取 **n ≥ 9 个样本的中位数**（本批 α=1.00 的 D1 = 125/78/102 ⇒ 单样本 ±30% 的形状方差足以让
  `T_VIS = 0.5 × D1(1.00)` 上下浮动 20 分）。

### ② `a_hit_but_failed` = 0（用户第二组数，目标 ≥3 **未达成**）

`swap_after_press` 10/10（`a_hit=10`，全过）、`swap_hard_press` 5/5（`a_hit=5`，全过）、
`swap_timer` `a_hit=0 wrong=5`、`swap_hard_timer` `a_hit=0 wrong=3`。
⇒ **"A 对 + B 错"用当前驱动打不出来**：只要按对了 A，驱动就会在换题后重读并按对 B（本批 15 例全过）；
唯一会错的是"按下时 A 已不是当前目标"（`a_hit=0`）。
**机制澄清（审核 m08247；我原稿写的"让 B 不可答"是错的方向）**：`a_hit_but_failed` 的定义是"按对 A →
检测到换题 → 重规划 → **按了 B 但按错**"，即驱动**自以为答对了**。B 不可答 ⇒ 驱动拒答 ⇒ 落
`refused_right` / `false_refusal`，**永远不进这个字段**。要造出它，必须 **B 可答、驱动认为可答、但答错**：
① B 的标签易被 OCR 误读（`guard-blind` 已证明"一个字形之差"的刺激存在）——驱动重读 ask 检测到换题，
但把 B 读成 A，于是按 A 的答案；② 驱动重规划时复用了 A 的答案缓存；③ B 的 ask 措辞有歧义，驱动理解成
另一个动作、按了看似合理的错键。**三条都以"换题检测先修好"为前提**（否则 B≈A 时驱动根本检测不到换题
⇒ `a_hit=0` ⇒ 又回到旧形状），所以顺序必须是 **守门修复 → 竞态收窄 → 难题型重设计**。

### ③ `race` 与 `guard-blind`（用户第三组数）

`race(pressed the replaced ask) 5/5`、`guard-blind(one-glyph re-roll) 3/3`
⇒ **70–150 ms 竞态窗口未消**（5/5 全踩中），且"B 与 A 只差一个字形"时 **32×4 banner 指纹分辨不了**（3/3 全盲）。
两条都要各自方案：前者"按键前再验一帧 + 缩短复验到按键的间隔"；后者换更细指纹或直接重读 ask 文本。

> **本行数据的后续（2026-10-04，见 DESIGN r10）**：守门已按"直接重读 ask 文本"落地，随后查出 3/3 `guard-blind`
> 里 **2 例的真根因是折叠表 `_code`**（`TANGO`/`TANGQ` 折叠后同码 ⇒ 守门读对了也判"未变"），修成 `_plain`
> 后 `swap_hard_timer` **0/3 → 4/5**、`guard-blind 3/3 → 1/1`、`race 5/5 → 1/1`。**批次 3 这三行数字本身没错**
> （当时的口径就是那样），但引用时要用批次 4 的现值：见下节。

### D1 分布（28 个淡化控件题，n=25 有 D1，另 3 题"没找到标签"）

排序后：`40 40 40 40 42 44 47 47 47 47 50 53 54 54 56 57 57 62 65 | 70 70 74 78 102 125`

- **66–69 之间一个值都没有**：拒答的最大值 **65**、点击的最小值 **70** ⇒ 规则执行一致（28/28 与 `D1 ≥ 68` 完全吻合，无一例外）。
- 3 题拒答理由是 `no control carries the asked label`（i=0/6/12，全在低 α 档）⇒ **"读不到"与"看不见"是两条路径**，都留档。
- ⇒ 与靶子的差不是阈值算错，而是**同一条规则下 D1 随标签形状漂移**（同一 α 下 4 字母词到 6 字母词差 ±10，本批横跨 `40…65`）。

### 鼠标通道的已知边界（本批暴露，属声明边界不是回归）

第 61–63 题 `synonym_button`：ask 是 "close the notice"，正文里就写着 "Close"，驱动在**正文**上量到 **D1 = 98**
（正文全对比度）、远高于门槛 ⇒ 点正文、无事发生 ⇒ 三行 `NONE` ⇒ 早退。
**这正是 `DESIGN` §3.2 声明的边界**：D1 量"淡 vs 强"，**不量"控件 vs 正文"** ⇒ 同义词类在鼠标通道不可判，
只能留在键通道（批次 2 的 `synonym_button 6/6` + `synonym_only 4/4` 仍是它的成绩）。
**⇒ 引用规则：`t_trap3` 鼠标通道的 `synonym_button` 未完成（第 61 题起就早退），该类在这批的成绩一律
不引用；它的有效成绩仍只有键通道批次 2 的 `synonym_button 6/6` + `synonym_only 4/4`。** 这为"徽章 5 类留键通道"
的裁剪提供了第二个独立理由。

### 失败批次（**不引用**）

`t_trap3-1.json`（`scripts_sha 785cfe9412d6`）**是失败批次**：28 题 `no_badge_fill` 全在 ask 解析层被拒
（`ask_unparsed=1`——靶子用短形式 "click KILO"，而驱动鼠标通道只认 "click the button labelled X"），
且 swap 类每题占两行（行内无重读）⇒ `timeout 43` 与 `a_hit_but_failed 15` 都是行失同步的产物
（折叠后 `14/56`、`a_hit_but_failed 0`）。**任何数字都不要引用它**；它唯一的价值是暴露了那两条驱动 bug。

### 曲线 2（`fill_curve2.json`，本轮新增，**不改阈值**）

曲线 1 的刺激是"空 body 上单个 5 字母标签"，与类自身的刺激（3 个控件、2 列网格、满对比度诱饵）不同形，
同一 α=0.50 在活帧上量到三个数：**71**（探针刺激+探针链）、**67**（探针刺激+驱动链）、**54**（类的一帧，标签 KILO）。
`probe_fill_curve2.py` 因此把**刺激换成类自己的画笔**、**链换成驱动自己的链**（`body_words` + `vis_score`），
统计量与选择式（`T_VIS = round(0.5 × D1(1.00))`）一字未改：预检 α=1.00 得 **D1 = 137 ⇒ T_VIS = 68（不变）**，
α=0.50 得 **D1 = 71**。另用同一帧做框宽扫描（25→92、39→92、59→67、69→55、89→40）
⇒ **D1 主要取决于框内"文字核心 vs 抗锯齿边缘"的比例**，即随标签长度/形状漂移 ⇒ 门槛是个**带**，不是一条线。
`fill_curve.json` 原文件保留不动，仅"用于推阈值"这一点被曲线 2 取代。

## 批次 4 结果（`t_trap4-1.json`，鼠标通道，38 题，**`a_hit_but_failed` 首次非 0**）

**v1 行**：`t_trap4 v1 21/38 55.3% decided 100.0% screen 33/38 replan 25 1413 ms/task keys 6 shots 122 ocr 331`
直方图 `answered_right=21 wrong_target=11 false_refusal=6`；`false_refusal 6/38 (15.8%) false_accept 0/0`；
**`swapped 27 a_hit 17 a_hit_but_failed 8`**。
`scripts_sha 5e3d5949b6e9`、`gates v1`、前台真实鼠标（`foreground unchanged: True`）、约 2.8 min。
两个耗时口径别混：score 的 `1413 ms/task` = 每题 `ms`（驱动自报决策耗时）均值；runner 的 `per task: 4457 ms avg` = 墙钟
（含等判定与 twin 的 9 s 看门狗）。

### ① `a_hit_but_failed` = 8（用户第二组数，目标 ≥3 **达成**）

| 变体 | n | a_hit | wrong | 错例 |
|---|---|---|---|---|
| `swap_after_press` | 5 | 5 | 0 | —— |
| `swap_hard_press` | 5 | 5 | 1 | t9 `clicked=GAMMA, want=GAMMB`（驱动把 B 读成 A）|
| `swap_hard_timer` | 5 | 0 | 1 | t13 同款误读（守门自己的重读给出 `GAMMA`）|
| `swap_timer` | 5 | 0 | 1 | t33 `clicked=TUNDRA, want=RAVEN` = **竞态** |
| `swap_twin_press` | 7 | **7** | **7** | 换题后点到**标题**（同词双现，见 ④）|

8 例构成 = **7 例 twin + 1 例 t9**；twin 的第 8 题（t4）在 phase A 就点了标题（`twin=GAMMB, want=GAMMA`）⇒ `a_hit=0`，不计入。
`wrong_target 11` = 8 twin + t9 + t13 + t33。

**诚实标注（不许合并成一句"答错 8 次"）**：twin 那 7 例的靶子判决是**"点了文字、不是控件"**（`clicked=null`），
与"点错了另一个按钮"（t9）不同类。两者都满足 §5.2 第二种情况"按对 A、驱动自认为答对 B"，但机制不同。

### ② `by_alpha`（本批 10 题淡化切片，规则与 `T_VIS` 一字未改）

| α | n | 答对 | 拒对 | 误拒 | 误受 | 驱动 D1（逐题） |
|---|---|---|---|---|---|---|
| 0.46 | 3 | 0 | 0 | **3** | 0 | 65.0 / 53.0 / 53.0 |
| 0.50 | 3 | 0 | 0 | **3** | 0 | 57.0 / 57.0 / 57.0 |
| 0.65 | 2 | **2** | 0 | 0 | 0 | 79.0 / 70.0 |
| 1.00 | 2 | **2** | 0 | 0 | 0 | 78.0 / 102.0 |

- 逐档与批次 3 **一致**（0.46 全误拒、0.50 全误拒、0.65/1.00 全答对）⇒ 这是**复现**，不是新标定。
- **66–69 之间又是空的**（拒答最大 65、点击最小 70）⇒ 批次 3 那条"规则执行零例外"在独立一批上**复现**。
- 误拒理由全是 `the control is painted below the visibility floor`（`vis_refuse=1`）⇒ 与"读不到标签"仍然是两条路径。

### ③ `race` 与 `guard-blind`（用户第三组数，本批现值）

`race(pressed the replaced ask) 1/1`、`guard-blind(one-glyph re-roll) 1/1`（批次 3 是 5/5 与 3/3）。
- `race` 的 t33 换的是**不同词**（`TUNDRA`→`RAVEN`）、banner 指纹也没够 3 格 ⇒ 竞态窗口仍在（70–150 ms），只是从"必踩"降到偶发：**未清零**。
- `guard-blind` 剩下的 1 例（t13）根因是**守门自己的重读误读**（把 `GAMMB` 读成 `GAMMA`）⇒ 任何比较规则都挡不住，要"读两次取多数"或更细指纹。
- 批次 3 的 3/3 里有 2 例其实是 `_code` 折叠造成的，修掉后 `swap_hard_timer 0/3 → 4/5`（详见上节引用框 + DESIGN r10）。

### ④ 本批新增题型 `swap_twin_press`（同词双现）

做法：换题后在网格**之前**画一个粗体大标题，文本 = 换题后的 `want_b`（无徽章、**不是控件**，点击直接判 wrong）。
为什么必然中：`gui_see.py:130-156 find_text` 按 score 降序且**排序稳定** ⇒ 精确匹配并列 1.0 时取阅读顺序靠前者（标题在上）；
`gym_run.py:1353 verify_before_act` 的预算 `verify_calls >= 1 ⇒ return True` ⇒ **换题后的第二次点击不再复验**。
⇒ 8 题里 7 题的靶子判决是 `{"clicked": null, "twin": "TANGQ/XENOM/KILQ/GAMMB/HARBOP", ...}`（铁证）。
**这是当前口径下的真实行为，不是 bug**：同词在画面出现两次时，驱动会点靠前的那个。

### ⑤ 守门成本（实测）

`ask_gates 48`、`ms_askgate 7020.9` ⇒ **146 ms/次**（OCR 进程启动占大头：4× 改 2× 只省约 20 ms）；`shots 122`/38 题 = **3.2 帧/题**（守门每次多抓一帧）。
twin 的看门狗让墙钟均值升到 `4457 ms/题`，**不能算进守门成本**。

## 批次 5 结果（口径 v2，「最小收口版」）

范围（用户选的 B）：改动 ①（守门去掉 `ask_source=="screen"` 前置 + 重读加 6 px padding）、
②（`ask_text_changed` 前缀容忍 ⇒ 后来扩成「文件仲裁」）、③（计划词三角验证）、⑦（`score.py` 拆分 + `v2` 行标签）。
不做（进欠账）：④ 多候选余量规则、⑤ 守卫内改序、⑥ `verify_before_act` 预算/鼠标接入、计分 P50/P95。

### 定稿行（`t_trap4-4.json`，sha `ebfc7dce831a`，鼠标通道 38 题）

```
t_trap4        v2 24/38  63.2%  decided 100.0%  disturb 0   screen 34/38 replan 28    1465 ms/task  keys 6     shots 137  ocr 352
               answered_right=24 wrong_target=8 false_refusal=6
               false_refusal 6/38 (15.8%)  false_accept 0/0 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 0/0 (0.0%)  quiet 24/38 (63.2%)  swapped 28  a_hit 18  a_hit_but_failed 8  (wrong_target 0 / twin 8)
               variant nb046 0/3  variant nb050 0/3  variant nb065 2/2  variant nb100 2/2  variant swap_after_press 5/5  variant swap_hard_press 5/5  variant swap_hard_timer 5/5  variant swap_timer 5/5  variant swap_twin_press 0/8
               swap by variant  swap_after_press n=5 a_hit=5 wrong=0  swap_hard_press n=5 a_hit=5 wrong=0  swap_hard_timer n=5 a_hit=0 wrong=0  swap_timer n=5 a_hit=0 wrong=0  swap_twin_press n=8 a_hit=8 wrong=8   race(pressed the replaced ask) 0/0
               nb046(a=0.46) n=3 ans_right=0 ref_right=0 false_ref=3 false_acc=0 wrong=0 to=0  nb050(a=0.50) n=3 ans_right=0 ref_right=0 false_ref=3 false_acc=0 wrong=0 to=0  nb065(a=0.65) n=2 ans_right=2 ref_right=0 false_ref=0 false_acc=0 wrong=0 to=0  nb100(a=1.00) n=2 ans_right=2 ref_right=0 false_ref=0 false_acc=0 wrong=0 to=0
               wrong_target  #0..#7   truth=answerable  dec=acted   act=click_label    result=wrong clicked=null
```

`score.py --selftest`：**39 checks, 0 failed**。

### 五组要复核的数（v2 口径）

| 组 | 批次 4（`t_trap4-1`，sha `5e3d5949b6e9`） | 批次 5（`t_trap4-4`，sha `ebfc7dce831a`） |
|---|---|---|
| `a_hit_but_failed_wrong_target` | 1（task 9） | **0** |
| `a_hit_but_failed_twin` | 8 | **8**（全部 twin 家族） |
| `race(pressed the replaced ask)` | `0/0` | `0/0` |
| `guard-blind(one-glyph re-roll)` | `1/1` | **不打印**（本批没有"按了过期 ask"的行） |
| fade 档（`by_alpha`） | `nb046 0/3`、`nb050 0/3`、`nb065 2/2`、`nb100 2/2` | **与批次 4 逐格相同** |

一个回读口径的坑：把新工具的拆分列用在**老 json** 上，`t_trap4-1.json` 读出来是
`a_hit_but_failed 9 (wrong_target 1 / twin 8)` —— 比批次 4 报告里手数的「7 twin + 1」**多 1 例**
（多的是 task 4：phase A 的同词双现，app 记 `a_hit` 为真）。以工具为准：**8 twin + 1 wrong_target**。

### 核心 14 题（两批同 `task_i`）

| task_i | 批次 4 | 批次 5 | 行内守门字段（批次 5） |
|---|---|---|---|
| 0 / 4 | wrong / wrong | wrong / wrong | `word_from=fuzzy`（twin 家族，token 无关） |
| **9** | wrong | **ok** | `word_from=exact`、`word_noise=1`、`clicks=GAMMB`、`a_hit=true` |
| 10 | ok | ok | `word_from=exact` |
| **13** | wrong | **ok** | `word_from=exact`、`ask_moved=1`、`word_noise=1`、`clicks=GAMMB` |
| 14 | ok | ok | `word_from=exact` |
| 18 / 21 | wrong / wrong | wrong / wrong | nb046 / nb050 拒答（已知） |
| 24 / 26 / 28 / 29 / 34 | ok | ok | `word_from=exact` |
| **33** | wrong | **ok** | `word_from=exact`、`ask_cells=3.0`、`ask_moved=1`、`clicks=RAVEN` |

**核心 14：7/14 → 10/14**；三处变化**全部**是本轮取证的三题（t9/t13/t33），其余 11 题逐题不变 ⇒ **无退化**。

### 成本（同批实测）

| | 批次 4 | 批次 5 | 差 |
|---|---|---|---|
| `ask_gates` | 48 | 56 | +8（守门现在也跑 `file` 源） |
| `ms_askgate` | 7020.9 | 8033.0 | — |
| ms / 门 | 146.3 | **143.4** | −2% |
| `shots` | 122 | 137 | +15 |
| 墙钟 / 题 | 4457 ms | 4823 ms | **+8.2%**（判据 ≤ +25%） |
| `ask_guard_skipped` | 不存在此键 | **不存在此键（=0）** | 守门运行率 100% |

### 三次跑批（必须一起引用，否则会误读）

| 跑批 | sha | 结果 | 发现了什么 |
|---|---|---|---|
| `t_trap4-2.json` | `4b44d9cb74d8` | 1/12，task 9 起 `--max-repeat 3` 早停 | ① 一上线就暴露**新失败模式**：守门在 OCR 噪声上误触发（banner 把 `GAMMB` 读成 `GAMMI`，`ask_cells=0`）⇒ 每次按压都被拦 ⇒ `presses=0`/`decision=none`/每题空等 16 s |
| `t_trap4-3.json` | `4cbcd072f027` | 23/38，t9/t33 转 ok，t13 仍错 | 「`ask_cells==0` ⇒ 噪声」判据**吞掉了一次真换题**（t13 的 `GAMMA→GAMMB` 单字形改写让指纹给 0 格）⇒ 也是"桶指纹对单字形改写不可靠"的直接证据 |
| `t_trap4-4.json` | `ebfc7dce831a` | 24/38，三题全转 ok | 定稿：文本不一致时由**靶子自己当前的 ask**（状态文件 `ask` 字段）仲裁——与计划词相同 ⇒ banner 读错；不同 ⇒ 真换题 |

定稿判据（写在 `STATE.md` §6，跑前定死）：(i) 三题仍无 `ask_label_read` ⇒ ① 无效；
(ii) `ask_word_short` 多而仍点错 ⇒ ③ 无效；(iii) 核心 14 出现批次 4 没有的新失败 ⇒ 有副作用。
**三条都没有成立**（t9/t13/t33 全转 ok、核心 14 无新失败）⇒ 假设保留，批次 5 到此**收口**。

## 批次 6 结果（口径 v3：twin 修好 + race 首次拿到分母）

批次 6 只做两件收口（改动清单见 `STATE.md` §9.2；设计记录见 DESIGN 修订 r11）：

- **同词双现（`swap_twin_press`）**：判据从"按 OCR 顺序取首个出现"改成"**取坐在被绘制块里的那一次出现**"
  （`find_blocks` 的块覆盖，**不是** `block_evidence.fill_share`——后者在这条 app 上是反向的）。
- **race**：靶子新增 `swap_race_timer`（定时 800–2600 ms，落在守门抓帧**之后**）+ 驱动新增
  `--press-jitter 0,1200`（**只对该 variant 生效**）⇒ 过期按压第一次被测到。

### 定稿行（`t_trap5-1.json`，sha `9db420c422a2`，鼠标通道，48 题）

跑完**立刻**打分（当时 `gym-events.jsonl` 属于这一批；见引用规则 7）：

```
t_trap5        v3 37/48  77.1%  decided 100.0%  disturb 0   screen 44/48 replan 33    1564 ms/task  keys 6    shots 170  ocr 433
               answered_right=37  wrong_target=5  false_refusal=6
               false_refusal 6/48 (12.5%)  false_accept 0/0 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 0/0 (0.0%)  quiet 37/48 (77.1%)  swapped 38  a_hit 20  a_hit_but_failed 0  (wrong_target 0 / twin 0)
               variant nb046 0/3  nb050 0/3  nb065 2/2  nb100 2/2  swap_after_press 5/5  swap_hard_press 5/5
                       swap_hard_timer 5/5  swap_race_timer 5/10  swap_timer 5/5  swap_twin_press 8/8
               swap by variant  swap_race_timer n=10 a_hit=2 wrong=5
               race(pressed the replaced ask) 5/5   (after the guard's frame 5)
               guard gate sample 42  P50 366 ms  P95 400 ms   (criterion P50<=240, P95<=320)
```

（该块按当时的输出粘贴，省掉了 `score.py` 恒打印的 `MISMATCH` 行：驱动自评 `37/48 ok` 与联合 `37/48` 完全一致 ⇒ `MISMATCH 0`。）

### ① `a_hit_but_failed` = 0（wrong_target 0 / twin 0）——twin 从 8 降到 0

| 变体 | 批次 4 | 批次 5 | **批次 6** |
|---|---|---|---|
| `swap_twin_press` | 0/8 | 0/8 | **8/8** |
| `swap_hard_press` | 5/5（t9 例外） | 5/5 | **5/5** |
| `swap_hard_timer` | 4/5 | 5/5 | **5/5** |
| `swap_after_press` | 10/10 | 5/5 | **5/5** |
| `swap_timer` | 4/4 | 5/5 | **5/5** |

逐题证据（t0–t7 全 `ok`）：8 题**全部** `ask_word_from=painted`、`label_painted=1`、`label_text_like=1`、
`label_alt_tried=1`；t4 的 banner 仍被 OCR 读成 `GAMMI`（`ask_cells=0`）却仍点对 `GAMMB`
⇒ 判据不依赖把词读对，只依赖"哪一次出现坐在块里"。

### ② race **5/5**（分母 5，且全部发生在守门抓帧之后）

逐题证据：t41/t42/t44/t46/t47 的 `detail.stale_press=True`（`detail.clicked` 是换题前按下的词、
`detail.want` 是换题后的真值）；t38/t39/t40/t43/t45 `stale_press=False` 且点对。
**分母 5 ≥ 5 ⇒ 不标"非缓解"**（这是本项目第一次让 race 的分母达标）。

**但它是"踩线达标"**：分母**恰好等于判据线 5**。5 次全错 ⇒ 有区分度（不是"24/24 连五次"那种空信息），
但样本窄，**不据此宣布 race 已缓解**。按用户 2026-10-04 定论：**不带单独一批去把 5 扩成 10**
（守门逻辑一动 race 就会变，现在扩的分母会被下一批改动覆盖）——
**下一批若涉及守门改动（欠账 ④⑤⑥ 任一条），race 分母在同一批里扩**。

### ③ `guard-blind` 本批**不打印**（`blind_seen == 0`）

`score.py` 只在 `blind_seen` 非空时打印该行 ⇒ 批次 6 没有可引用的 guard-blind 分母。
（批次 5 同样不打印；批次 3/4 的 `3/3`、`1/1` 分母都 < 5，按引用规则 1 标"非缓解"。）

### ④ `by_alpha`（10 题淡化切片，规则与 `T_VIS` 一字未改）

`nb046(a=0.46) n=3 ans_right=0 ref_right=0 false_ref=3`；`nb050(a=0.50) n=3 false_ref=3`；
`nb065(a=0.65) 2/2`；`nb100(a=1.00) 2/2` —— 与批次 4/5 **逐格相同**（0.46/0.50 仍全拒，0.65/1.00 全对）。

### ⑤ 核心 14 题（与批次 4/5 **逐题同构**：`TRAP_PLAN5[:38] == TRAP_PLAN4`，同 seed）

| 批次 | json | 核心 14 |
|---|---|---|
| 5 | `t_trap4-4.json` | 10/14（t0/t4 twin 错、t18/t21 淡化档错） |
| **6** | `t_trap5-1.json` | **12/14**（只有 t0/t4 **wrong → ok**；**无 ok → wrong 翻转**） |

逐题表（两批同一组 `task_i`；`result` 与 `detail.variant` 都取自各自 run json 的 `runs[]` ⇒
**可离线复算，不依赖 events 留档**；与联合打分（10/14 → 12/14）一致）：

| `task_i` | variant | 批次 5 | 批次 6 | 变化 |
|---|---|---|---|---|
| 0 | `swap_twin_press` | wrong | **ok** | ✅ twin 修复 |
| 4 | `swap_twin_press` | wrong | **ok** | ✅ twin 修复 |
| 9 | `swap_hard_press` | ok | ok | — |
| 10 | `swap_hard_press` | ok | ok | — |
| 13 | `swap_hard_timer` | ok | ok | — |
| 14 | `swap_hard_timer` | ok | ok | — |
| 18 | `nb046`（a=0.46） | wrong（拒答） | wrong（拒答） | 无变化（见 ④） |
| 21 | `nb050`（a=0.50） | wrong（拒答） | wrong（拒答） | 无变化（见 ④） |
| 24 | `nb065`（a=0.65） | ok | ok | — |
| 26 | `nb100`（a=1.00） | ok | ok | — |
| 28 | `swap_after_press` | ok | ok | — |
| 29 | `swap_after_press` | ok | ok | — |
| 33 | `swap_timer` | ok | ok | — |
| 34 | `swap_timer` | ok | ok | — |

⇒ **14 题里只有 2 题发生变化，且方向都是 wrong → ok**；"无 ok → wrong 翻转"这句话由这张表直接可核。

### ⑥ 成本（同批实测，鼠标通道）

| 量 | 批次 5（38 题） | 批次 6（48 题） | 差 |
|---|---|---|---|
| `shots` | 137 | 170 | +33（多出的 10 题 + twin 的额外一轮） |
| `ms / 帧` | — | **219**（`ms_shot 37281.5` / 170） | — |
| `ms / 门` | 143.4 | **148.1**（`ms_askgate 10073.1` / `ask_gates 68`） | +3.3% |
| `find_blocks` 单次 | 18.8 ms（profiling，小帧） | **77.6 ms**（1180×780 帧，探针实测） | 只在出现 ≥2 次时付费 |
| 墙钟 / 题 | 4823 ms | — | twin 8 题各多一轮按压 |
| `ask_guard_skipped` | 0 | **0** | 守门运行率 100% |

`gate_ms` 口径：`t_gate` 在 `self.shot()` 之前 ⇒ P50 366 里含 219 ms 抓帧，扣帧 ≈ **147**（P95 400 → ≈181），
与独立的 `ms_askgate / ask_gates = 148.1` 一致 ⇒ **判据（P50 ≤ 240、P95 ≤ 320）在扣帧口径下达标**。

### ⑦ chaos 三批（键通道 `--bg`，与鼠标批串行；sha `ee68f457577d`）

**两个文件系列必须先分清，否则引用会拿错数**：

| 系列 | 文件 | 是什么 | 能引用什么 |
|---|---|---|---|
| `w6b-*` | `t_trap2-w6b-control/chaos35/chaos70.json` | **首轮三批**（同一后台任务里连跑：控制 → 0.35 → 0.70） | 只有**驱动自评**与 `stats`（shots/ocr/墙钟）。`score.py` 数字**永久缺失**：三批共用一个 `gym-events.jsonl`，后两批把它覆盖了，而 `score.py` 是按 `rep["events"]` 那条路径读真值的（引用规则 7）。 |
| `w6c-*` | `t_trap2-w6c-control.json`、`t_trap2-w6c-chaos70.json` | **复跑两批**（每批跑完**立刻** `score.py`） | **唯一可引用的 `score.py` 数字**（控制 60/60、0.70 = 58/60）。0.35 **没有复跑** ⇒ chaos 0.35 档**没有 `score.py` 数字，只有驱动 59/60**。 |

| 批次 | 驱动分数 | `score.py`（v2 标签，见引用规则 5） | shots | ocr | 墙钟/题 |
|---|---|---|---|---|---|
| 控制（无 chaos）`t_trap2-w6c-control.json` | 60/60（100%） | **60/60 100.0%**，`false_refusal 0/46`，`race 0/0` | 197 | 385 | 2940 ms |
| `--chaos 0.35 --chaos-kind rebuild` `t_trap2-w6b-chaos35.json` | 59/60（98%） | **无**（该批 events 在复跑前已被覆盖；见上表） | 340 | 579 | 3198 ms |
| `--chaos 0.70 --chaos-kind rebuild` `t_trap2-w6c-chaos70.json` | 59/60（98%） | **58/60 96.7%**，`timeout 1` + `false_refusal 1`，`race 0/0` | 412 | 676 | 3924 ms |

- **干扰确实注入了，两个数属于两次不同的跑**：同一组设置（60 题、0.70、`rebuild`）跑了两遍 ⇒
  `w6b` 那遍 app 侧事件是 `chaos_planned 51 / chaos 51`，`w6c` 那遍是 `chaos_planned 50 / chaos 50`
  （各自从**那一遍自己的**事件文件读出，所以都真实；两遍差 1 ≈ 2% 的运行间波动，不是矛盾）。
  驱动的 `disturbances: 0 fired` 是**另一个口径**（只数弹窗，见引用规则 6）⇒ 两个数不能互推。
- **代价与恢复**：驱动在扰动下重读显著变多（shots 197 → 412、ocr 385 → 676、`replan` 15 → 48、
  墙钟 2940 → 3924 ms，**+33%**），通过率 **100% → 96.7%（−2 题）**：一题 `timeout`（重建后的判定没等到）、
  一题 `false_refusal`（本该点的题被拒）。
- `score.py` 末尾的 `MISMATCH 1` = 驱动把那一题 `timeout` 记成了 `ok`（它读到的是重建前的判定）
  ⇒ 这就是 chaos 下"驱动自评"与"联合真值"的唯一分歧点。

### ⑧ 本批必须一起披露的三件事

1. **race 的机制更正**：批次 1–5 的 `race 0/0` 不是"没踩中"，而是**机制必然**——老 `swap_timer` 的
   600–1000 ms 定时落在守门抓帧（~1.4 s）**之前**，守门看得到换题 ⇒ 必然重规划。批次 6 的 5/5 是换了窗口才拿到的。
2. **`--press-jitter` 只对 `swap_race_timer` 生效**（读状态文件的 `variant` 门控）：不门控就会把批次 5 的
   `swap_timer` 回归题也变成 race，**破坏跨批可比性**。
3. **48 题而不是 24 题**：`TRAP_PLAN5 = TRAP_PLAN4 + 10×swap_race_timer`，前 38 题与批次 4/5 逐题同构、
   同 seed 下 byte-identical ⇒ 核心 14 的对比是**精确同题**对比（代价是多跑 10 题）。

### ⑨ 批次 6 未做（欠账，已进 `STATE.md` §7）

守门 ④（多候选余量）、⑤（文本重读在指纹之前）、⑥（`verify_before_act` 预算每计划一次 + 鼠标接入）、
`guard-blind` 清零、`t_gate` 移到 `shot()` 之后、`press_delay_ms` 进逐题行、`swap_after_press` 5 s 空等、
chaos 每类逐个解锁、用真实题面画笔重标定 `no_badge_fill`。

## 批次 7 结果（口径 v2；欠账 #14「留档命名」落地 + `move` 类首跑）

**本批只改一件事**：给了 `--json-out x.json` 时，app 的 state/events 自动写成 `x-state.json` / `x-events.jsonl`
（`gym_run.py` main 里 8 行）⇒ **每批留档、事后可 `score.py x.json` 复核**。**判定逻辑一字未改。**
sha：`481154ca264d`（批次 6 是 `ee68f457577d`）。

### ① 定稿行（`t_trap2-w7-control.json`，sha `481154ca264d`，键通道 `--bg`，60 题）

```
t_trap2  v2  60/60  100.0%  decided 100.0%  disturb 0  screen 51/60  replan 15  1428 ms/task  keys 70  shots 197  ocr 385
answered_right=46  refused_right=14   false_refusal 0/46 (0.0%)  false_accept 0/14
stale 0  wasted 0  verify_giveup 0  re-reads 0
swapped 15  a_hit 10  a_hit_but_failed 0 (wrong_target 0 / twin 0)
variant alpha020 2/2  alpha030 2/2  alpha035 2/2  alpha050 2/2  alpha065 2/2  prose_only 4/4  prose_with_button 6/6  swap_after_press 10/10  swap_timer 5/5
race 0/0    guard gate sample 46  P50 186 ms  P95 244 ms
```

**逐格等于批次 6 的 `t_trap2-w6c-control.json`**（同协议、不同 sha）⇒ #14 只改命名、不改判定，
**批次 6 的 chaos 结论仍然有效**。

### ② `move@0.70`（`t_trap2-w7-move70.json`，同 sha）——⚠ **修复前，不可引用为 move 类定稿**

> **move 类定稿看批次 8 的 `t_trap2-w8-move70.json`。** 本批在 `two_close_names` 上因守门假阳性卡住，
> `--max-repeat 3` 早退于 **33/60**；这里只用于**定位根因**。

```
chaos:move  v2  29/31  93.5%  decided 93.5%  disturb 0  screen 29/31  replan 28  1705 ms/task  keys 35  shots 336  ocr 421
answered_right=26  refused_right=3  timeout=2   extra_attempts 2 (rows collapsed to one per task)
false_refusal 0/28  false_accept 0/3   swapped 15  a_hit 4  a_hit_but_failed 0 (wrong_target 0 / twin 0)
variant prose_only 3/3  prose_with_button 5/6  swap_after_press 10/10  swap_timer 5/5   race 0/0
guard gate sample 26  P50 188 ms  P95 212 ms      stop: task 31 failed 3 times in a row
```

**两个 delta，同一缺陷（守门假阳性 ⇒ 不放行 ⇒ 重规划）**：

| delta | 现象 | 证据 |
|---|---|---|
| ① `two_close_names` 三连 `none` ⇒ 早停 | task 31（`LUMEN93`）跑了 3 次、每次 21.2–21.8 s、`presses 0`、`decision none`、`replan_why "no verdict arrived"`、`error` 空 | 重读回来的是**干净前缀** `"DO: click the button labelled"`（`ask_cells 0`、`ask_delta 0.0` —— 指纹明确说没动），但旧代码把"读不到 label"当成"问题变了"（`ask_changed_text true`）⇒ 与同函数 docstring「读不出的重读不是问题移动的证据」**相反** |
| ② `a_hit` 10（控制）→ 4 | 首次按压被推过 8 s 安全换题线（`gym_app.py:1414`）⇒ 按到换题后的 B（正确 ⇒ `wrong=0`、`swap_after_press` 仍 10/10） | **恰 6 题**：`a_hit=False` 的 `#1 #4 #5 #7 #8 #9` 墙钟 10.65–10.88 s（全 > 8000 ms）；`a_hit=True` 四题 4.35–4.61 s（无一 > 8000 ms）；控制批十题全 True、6.62–6.97 s |

⇒ **`a_hit` 不是独立指标**，是"守门假阳性把首按推过换题线"的读出量（`HANDOFF.md` 盲区 15）。
根因口径（用户 m09426 指定）：**`move` 干扰下记录的 `ask_box` 在重读时失效**（边缘切在 label 之前），
"OCR 漏读"列为次级假设；修法见批次 8（`DESIGN-refusal-scoring.md` 修订 r13）。

### ③ 本批未做

Option A（守门每帧重算 banner box）= `STATE.md` §7 #15，用户 m09426 定：本批不动。

## 批次 8 结果（chaos 四类 × 2 强度；**探索性·不并入定稿**）

sha **`f598406cfc70`**（批次 8 = "**读不出的重读不再被当成'问题变了'**"，`DESIGN` 修订 r13）。
键通道 `--bg`，60 题/批，`--chaos-ms 200,700 --until-interferences 5 --max-tasks 60`，**每批跑完立刻 `score.py`**，
每批自带 `t_trap2-w8-*-state.json` / `-events.jsonl` 留档（#14 之后第一次全链留档）。
`sha` 覆盖 `gym_run.py + gym_app.py + score.py` 三个文件（`gym_run.py:3449-3451`）。
计分自检（本批跑批前的守门）：`score.py --selftest` = **41 checks, 0 failed**。

**本批必读：两条可比性与一条勘误**（用户 m09631 收工要求）：

- **批次 8 与批次 7 不可直接比**：sha 从 `481154ca264d` 变到 `f598406cfc70`，变的是**读题守门的退化分支**
  （`ask_label_now` 读不出标签 ⇒ `None`；`ask_text_changed` 的 `""` 与"无任何连续 2 字重叠"两种退化 ⇒ 判"没读到"、回落指纹）。
  批次 1–7 的**已公布数字不受影响**（各自 sha 下自洽、已跑完不再改）；跨批次比较时，**读题守门这条路径**要按"批次 7 之前 / 批次 8 之后"分开看。
- **勘误（把旧判定加上限定条件，不是纠正数字）**：本表**批次 6 ⑧-1** 写的是"批次 1–5 的 `race 0/0` 不是没踩中，而是**机制必然**"（老 `swap_timer` 的 600–1000 ms 落在守门抓帧之前）。
  批次 8 的 `slow` 两档给出 `race **0/2**`、`**2/2**`（同一对 task `#10/#14`）⇒ 那句话**要加限定条件**：
  "机制必然"只在**默认判定节奏**下成立；把靶子判定推后 1.5–3.2 s（`slow` 干扰）会让同一批老 variant 的窗口重新落到守门抓帧之后。
  **旧数字本身一个都不变**（批次 1–6 的 `0/0`、`5/5` 仍按各自 sha/通道引用；参见本表批次 6 ⑧-1 的原句与 `STATE.md` §10.4 ②）。
- **事后复核证据**：`sol/sandbox/t_trap2-w8-rescore.txt`（六个 run json 各跑一遍 `score.py` 的完整输出 + `selftest: 41 checks, 0 failed`）；
  复核结果**逐行等于上表数字**，且每批 `chaos == chaos_planned`（27/27、49/49、24/24、41/41、1/1、1/1）。

### 四类 × 2 强度（同一命令，只换 `--chaos-kind` 与 `--chaos`）

| 类 | 强度 | driver | `score.py` | app 侧 fire | 停法 |
|---|---|---|---|---|---|
| `move` | 0.70 | **58/60** | `58/60 96.7%` decided 98.3% · replan 35 · 1708 ms/题 | `49/49` | 跑满 |
| `move` | 0.35 | **60/60** | `60/60 100.0%` decided 100.0% · replan 28 · 1649 ms/题 | `27/27` | 跑满 |
| `slow` | 0.35 | **58/60** | `57/59 96.6%` decided 96.6% · replan 12 · 1524 ms/题 | `24/24` | 跑满 |
| `slow` | 0.70 | **57/60** | `51/54 94.4%` decided 100.0% · replan 12 · 1658 ms/题 | `41/41` | 跑满 |
| `popup` | 0.35 | **4/7** | `4/5 80.0%` | `1/1` | **早停（task 4 三连 NONE）** |
| `popup` | 0.70 | **1/4** | `1/2 50.0%` | `1/1` | **早停（task 1 三连 NONE）** |

（`rebuild` 见批次 6 的 `t_trap2-w6c-chaos70`：`58/60 96.7%`，`50/50` fire。）

### ① `move` 类：批次 8 修好的正是那一题，死锁→可测

- **`ask_read_unreadable` 在 `move@0.70` 计 2 次，全部落在 `task 31`**——就是批次 7 卡死、导致 33/60 早停的那题；
  这次它**正常作答**，整批**没有 `result == none` 的行**、没有早停（`HANDOFF.md` 盲区 14）。
- 两档数字给出**剂量-反应**：干扰越强，`a_hit` 越低（0.35 → 7/10，0.70 → 4/10），
  而**每次"没按中第一次"都对应墙钟 > 8 s 的安全换题线**（`gym_app.py:1414`）：
  0.70 档没按中的 6 题墙钟 **10.86–11.17 s**、按中的 4 题 **4.58–4.92 s**；0.35 档没按中的 3 题 **10.58–10.98 s**、按中的 7 题 **4.32–4.59 s**。
  ⇒ `a_hit` 是"守门假阳性/干扰把首按推过换题线"的**读出量**，不是独立能力指标（`HANDOFF.md` 盲区 15）。
- `move@0.70` 的两次真失败：`#15`（`prose_with_button`，驱动侧 `stale_actions 1`，`dec=none`）+ `#34`（`two_close_names`，**点错 `TUNDRA`** ⇒ `wrong_target 1`）。
  `a_hit_but_failed` 仍 **0 (0/0)**，`swap_after_press 10/10`、`race 0/0`。

### ② `slow` 类：把批次 6 判定"机制上不可能"的 race **重新打开**

- `slow@0.35`：`race **0/2**`、`swap_timer 3/5`；`slow@0.70`：`race **2/2**`、`swap_timer 3/5 a_hit=0 wrong=2`。
  **机制**：`slow` 干扰把靶子的判定推后 1.5–3.2 s ⇒ 老 `swap_timer`（600–1000 ms 定时换题）的窗口重新落到**守门抓帧之后**，
  于是出现"按了被换掉的 ask"——这正是批次 6 说"老题族只能 0/0"的那个窗口（批次 6 ⑧-1），在 `slow` 下**复现了**，两档各 2 题、**同一对 task（#10/#14）**。
- `slow@0.70` 另有本项目第一次 **`false_accept 1/14 (7.1%)`**（`#44 truth=must_refuse` 但跑成 `ok`）与 **`MISMATCH 1`**：
  都来自同一族"换题后同一 `task_i` 被重复尝试"（`extra_attempts 6`，行按 task 折叠）⇒ 记录在案、不单独解释。
- 两档 `false_refusal` 均 **0**（0/45、0/40）、`a_hit 10/10`（`swap_after_press`）⇒ `slow` 打的是"等不到判定"这条路径，**不制造误拒答**。

### ③ `popup` 类：**当前配置下这一类测不了**（探索性结论）

- 两档都只 fire 了 **1 次**（`chaos_planned 1 / chaos 1`），随后 driver 卡死：
  `#4`（`MICA`）/`#1`（`WILLOW`）三次尝试、每次 **22.8–24.6 s**、`dec=acted` 但 `result=none`、`detail {}` ⇒ `--max-repeat 3` 早停。
- 根因（读代码 + 逐行证据）：弹窗是 Tk `Toplevel`，标题 `"attention"`（`gym_app.py:616-655`），
  而 `dismiss_interference` 在 `--keys --bg` 下**只按窗口标题找 `"attention"`**（`gym_run.py` "if self.bg: if self.window_by_title('attention') is None: break"）——
  实际没找到（驱动侧 `disturbances: 0 fired`），于是**弹窗留着挡在靶子上**：驱动的按键被弹窗吃掉（`dec=acted` 但靶子没记到判定），
  该题永远不结束；而弹窗不消失 ⇒ 靶子也不再推进下一题（所以 app 侧只有 1 次 fire）。
- ⚠ 这是**驱动的能力缺口**（不是测量脚本的 bug）：`popup` 类要能跑，驱动必须先"看得见并打掉"外来窗口（鼠标通道已有这条路径：`_button_candidates(img2, "DISMISS")`），
  **`--keys --bg` 通道没有**。按用户规则：**delta 解释不了就停并写欠账** ⇒ 本类**不并入定稿**，写进 `STATE.md` §7 #16 / `HANDOFF.md` 盲区 17。
- ⚠⚠ **2026-10-05 第十段更正（本节的机制判断错了一半，勿再引用上面两句当结论）**：直接探针（`D:\DSH\dsh-actor\tmp\w10-uia-probe3.py`）证明
  **弹窗一直能被 UIA 看见**（同一条 trace 里 inline `windows` 11 项、含 `name="attention"`），真正的根因是 **actor 折叠把 `data.windows` 截断**（`actor.py:_slim`
  对 list 只留前 6 项左右），而 `window_by_title()` 当时**只读 `data`** ⇒ 枚举"看不见"。所以：①"没有这条路"**错**（路在，读错字段）；②"借鼠标视觉路径
  `_button_candidates`"在 `--keys --bg` 下**仍不可行**（弹窗是独立 HWND、不在主窗帧里；且 `--bg` 鼠标点击整条失效，见 `STATE.md` §16）——这条判断**对**。
  修法与修后结果见本节之后的 **批次 12**（`gym_run.py` `105cf6cb679eea10` → `87470aaff559`）。

### ④ 引用这批时必须带上的三条口径

1. **非 `popup` 类的 `fired-task pass 0/0` 是口径使然**：`score.py:278` 把"fired"定义为**驱动侧** `interferences > 0`，
   而驱动只数**弹窗型**（`dismiss_interference`）⇒ `move`/`slow`/`rebuild` 恒为 0/0。**注入率只引用 app 侧 `-events.jsonl`。**
2. **`stale` 与 `stale_press` 是两个计数**：打印行里的 `stale N` = 驱动侧 `stale_actions` 之和（`move@0.70` 为 1，来自 `#15`）；
   `race X/Y` 用的是 **app 事件的 `trap_stale_press`**（`slow` 两档为 2、2）。两者不可互推。
3. **这批全是「探索性·不并入定稿」**：键通道 + `--bg`，与鼠标批（批次 4/5/6）**不同通道、不同协议**，不能与之并列成"提升/退步"。

## 批次 9 结果（口径 v3；欠账 #10 + #11 还清，**判定逻辑未动**）

改动三处（假设、先量实测与证伪条件见 `STATE.md` §12）：①**#10** 守门计时点 `t_gate` 从 `self.shot()` 之前移到之后；②**#11** 逐题行 `detail` 注入驱动侧 `press_delay_ms`；③**记账续带**（实测逼出来的第三处）`_redo()` 续带 `press_delay_ms` / `press_jitter_task` / `gate_ms`。

### 定稿行（`t_trap6-1.json`，sha `f473ff21ad09`，鼠标通道，48 题）

与批次 6 **逐题同构**（同 `t_trap5`、同 seed `20251007`、同 `--press-jitter 0,1200 --max-repeat 3`）；跑完**立刻**打分，且本批自带 `t_trap6-1-events.jsonl` 留档 ⇒ 事后 `score.py t_trap6-1.json --events t_trap6-1-events.jsonl` 可复核：

```
t_trap5        v3 36/48  75.0%  decided 100.0%  disturb 0   screen 43/48 replan 32    1513 ms/task  keys 6    shots 167  ocr 426
               answered_right=36  wrong_target=6  false_refusal=6
               false_refusal 6/48 (12.5%)  false_accept 0/0 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 0/0 (0.0%)  quiet 36/48 (75.0%)  swapped 38  a_hit 20  a_hit_but_failed 0  (wrong_target 0 / twin 0)
               variant nb046 0/3  nb050 0/3  nb065 2/2  nb100 2/2  swap_after_press 5/5  swap_hard_press 5/5
                       swap_hard_timer 5/5  swap_race_timer 5/10  swap_timer 4/5  swap_twin_press 8/8
               race(pressed the replaced ask) 6/6   (after the guard's frame 5)
               guard gate sample 74  P50 124 ms  P95 164 ms   (criterion P50<=240, P95<=320)
```

### ① 判据核对（五条，2026-10-05 第二段开工定的）

| 判据 | 目标 | 实测 | 结论 |
|---|---|---|---|
| i 计时点 | `gate_ms` P50 与独立口径 `ms_askgate/ask_gates` 差 ≤ 10 ms（> 20 ms 才算证伪） | 124.1 vs **134.68** ⇒ 差 **10.58 ms** | **边缘未达**（差 0.58 ms）；证伪线 20 ms 未触发 |
| ii 记录路径 | 逐题行有 `press_delay_ms` 且与聚合一致 | 6 行 = 577/1029/562/480/911/942，**合计 4501 ms == `stats.press_delay_ms` 4501.0**；`stats.press_delays` 6 | ✅（批次 6：3 行 2993 vs 3560 ⇒ 567 ms 无归属） |
| iii 无副作用 | 核心 14 无 ok→wrong 翻转 | 12/14 → **12/14**，翻转 **0** | ✅ |
| iv jitter 生效 | `race` 分母 ≥ 5 | **6/6** | ✅ |
| v 无其他丢数 | 行内 `gate_ms` 样本数 == `stats.gate_samples` | **74 == 74**（批次 6：42 vs 75） | ✅ |

### ② `gate_ms` 换了测量范围（**不可与批次 6 的 368/400 并列**）

批次 6：抓帧 + 守门，P50 **368.0** / mean **365.33**（n=42）；批次 9：只剩守门，P50 **124.1** / mean **122.27**（n=74）。
差 ≈ **244 ms** ≈ 一次 `shot` 的实测成本 ⇒ 批次 6 的"369.7 ms"里约 2/3 是抓帧，不是守门。

### ③ 逐题对照（批次 6 → 批次 9）

只有 3 题变化，**全在 race 家族**（jitter 用未播种的 `random` ⇒ 该族跨批不可复现）：
`#36 swap_timer ok→wrong`、`#44 swap_race_timer wrong→ok`、`#45 swap_race_timer ok→wrong`；总数 37/48 → 36/48。
核心 14 逐题不变（12/14）；`a_hit_but_failed 0`；`false_refusal` 仍 6（`nb046/nb050` 低对比度族，两批同）。

### ④ 成本（同批实测，与批次 6 同量级）

`shots 167`（批 6 = 170）、`ocr 426`（433）、`clicks 62`（62）、`keys 6`（6）；`ms_shot 37910`（37282）、`ms_ocr 74782`（82458）。

### ⑤ 引用这批时必须带上的两条

1. `gate_ms` 是**扣帧后**的口径 —— 与批次 6 的 368/400 不是同一个量，并列即误读。
2. `race 6/6` 的分子分母都来自本批（jitter 随机 ⇒ 分母 5→6 是时序漂移，不是"改善"）。

### ⑥ 本批的一次作废尝试（方法学，写下来免得重犯）

第一次跑由 **WSL 后台作业**启动 ⇒ app 窗口起来就是 `-32000`（app 自报 `layout.origin`）⇒ 帧全空 ⇒ 0 次按压 ⇒ 首题 `WRONG` 后 `shot failed: "cannot write empty image"` ⇒ `gym_run.py:508 raise SystemExit`（设计如此：空帧 = 会话不可用，宁可退出也不产假分）⇒ **不写 run json**。改从 Windows 侧 `Start-Process -WindowStyle Normal` 启动后：干跑 `--tasks 2` **2/2 OK**，正式批正常。⇒ **跑批一律 Windows 侧启动 + 先干跑 2 题**。

## 批次 10 结果（口径 v2；欠账 **#4 = §7 #15「守门每帧重算 banner box」还清**，只换重读框、不动指纹基线）

改动三处（全在 `sol/sandbox/gym_run.py`；假设、证伪条件、判据见 `STATE.md` §14）：①**新增 `Driver.ask_box_now()`**（只跑像素段、不跑 OCR）；②`ask_label_now` 里"**重算优先、失败退回冻结框**"（`pad=6` 保留）；③逐题行注入 `ask_box_recomputed` / `ask_box_shift_px`，`_redo` 续带两者。**指纹路径（`ask_cells`/`ask_delta`）、匹配路径、阈值、`press_guard` 分支结构一字未动**（这就是"只换重读框"）。

### 定稿行（`t_trap2-w9-move70.json`，sha `5dedae26c6e8`，键通道 + `--bg`，`move@0.70`，60 题）

协议**逐项等于批次 8 的 `move` 类定稿**（同场景、同 seed `20251007`、同 `--chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5 --max-tasks 60`）；app 侧注入也逐项相同（`chaos_planned 49` / `chaos 49` / `ready 61` / `done 60` / `trap_swap 15`）。跑完**立刻**打分，自带 `t_trap2-w9-move70-events.jsonl` 留档 ⇒ 事后 `score.py t_trap2-w9-move70.json` 可复核：

```
chaos:move     v2 59/60  98.3%  decided 100.0%  disturb 0   screen 57/60 replan 37    1901 ms/task  keys 67    shots 479  ocr 649
               answered_right=45 wrong_target=1 refused_right=14
               false_refusal 0/46 (0.0%)  false_accept 0/14 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 0/0 (0.0%)  quiet 59/60 (98.3%)  swapped 15  a_hit 4  a_hit_but_failed 0  (wrong_target 0 / twin 0)
               variant alpha020 2/2  variant alpha030 2/2  variant alpha035 2/2  variant alpha050 2/2  variant alpha065 2/2  variant prose_only 4/4  variant prose_with_button 6/6  variant swap_after_press 10/10  variant swap_timer 5/5
               swap by variant  swap_after_press n=10 a_hit=4 wrong=0  swap_timer n=5 a_hit=0 wrong=0   race(pressed the replaced ask) 0/0
               guard gate sample 52  P50 139 ms  P95 183 ms  (criterion P50<=240, P95<=320)
               wrong_target  #34  truth=answerable  dec=acted   act=click_label    result=wrong clicked="TUNDRA"
```

对照批次 8 同协议那行（`t_trap2-w8-move70.json`，sha `f598406cfc70`）：`58/60 96.7% decided 98.3% · replan 35 · 1708 ms/题`，`shots 469 / ocr 633 / keys 64`，`ask_read_unreadable 2`。

### ① 判据核对（四条，2026-10-05 第四段开工前定的；对照 = 批次 8 同协议）

| 判据 | 目标 | 实测 | 结论 |
|---|---|---|---|
| i 守门不再依赖冻结框 | `ask_read_unreadable` 在 `move@0.70` 降为 **0** | 批次 8 **2**（全在 `task_i 31`）→ 批次 10 **0**；`ask_box_recomputed 124 == ask_gates 124`（**每一门都重算**，`ask_guard_runs 52`） | ✅ 字面达标。⚠ **样本量警告**：基线只有 2 次事件 ⇒ 单独不足以证明因果，旁证见 ③ |
| ii 读题死循环 | 不出现 `result none` + `presses 0` + `replans ≥ 1` | `result none` 行 **0**；"`presses == 0` 且 `replans ≥ 1`"只有 `task_i 37`，但它 **`result = ok`**（`replan_why = "no verdict arrived"`；批次 8 同一题也是 `presses 0` + ok）⇒ **合取条件不成立** | ✅ 未触发 |
| iii 无副作用 | 同 `task_i` 逐题无 ok→非 ok 翻转 | 共同 60 题：**ok→非 ok = 0**；非 ok→ok = 1（`task_i 15`，两批记录的题面不同 = `swap_after_press` 的读出时机差异 ⇒ **不计为改善**）；总数 `58 2 0 → 59 1 0` | ✅ |
| iv 成本 | `gate_ms` P50 相对批次 9（**124 ms**）涨 **≤ 30 ms** | 批次 10 **P50 139 / P95 183 ms**（n=52）⇒ **+15 ms**；场景匹配的独立口径 `ms_askgate / ask_gates`：批次 8 **136.30** → 批次 10 **145.01**（**+8.71 ms/门**） | ✅（两条口径都在 30 ms 内） |

### ② 机制证据与它的边界

- **覆盖**：`ask_box_recomputed 124`、`ask_gates 124`、`ask_guard_runs 52`；行内 `gate_ms` 样本合计 **52 == `stats.gate_samples` 52**（批次 9 判据 v 的同类"不丢数"核对，本批通过）。
- **题面**：死锁题 `task_i 31`（`LUMEN93`）——批次 7 `none`×3（`ask_reread "DO: click the button labelled"`、`ask_cells 0`、`presses 0`）→ 批次 8 `ok` 但 `ask_read_unreadable 2` → 批次 10 **`ok`、`ask_read_unreadable 0`、`ask_box_recomputed 2`、`gate_ms [179.4]`**。
- ⚠ **仪器局限**：`ask_box_shift_px` **只记每题"首次"重算的位移**（46 行有值，全部 `[0,0]`）⇒ 它只证明"进题后首次重算与冻结框一致"，**不能用来证明"门时那一帧确实被移过"**。要拿后者得改成记 max / 分布 —— 已写成欠账（见 ⑥）。
- **其他观察（只记、不作结论）**：`banner_missing 6 → 0`、`asks_from_screen 87 → 91`、`asks_from_file 8 → 6`、`replans 35 → 37`、`keys 64 → 67`、`nope_hint 13 → 15`、`hint_stale 20 = 20`、`refusals 15 = 15`、`interferences 0 = 0`。

### ③ 与批次 7/8 的关系（`move@0.70` 这条线现在有三个数据点）

批次 7（**修复前**，33/60 早退、`none`×3 全在 `task_i 31`）→ 批次 8（退化规则：读不出 ⇒ 回落指纹，58/60、`ask_read_unreadable 2`）→ 批次 10（**重算框**，**59/60、0 次读不出、`decided 100%`**）。
三批同协议同 seed ⇒ 这是同一题族上的三次独立观测，而不是三个不同场景的分数。

### ④ 引用这批时必须带上的三条

1. **`foreground unchanged: False`**（本批唯一环境异常）：跑批期间前台被切走（before = 用户前台窗口 `hwnd 133568`；after = 另一个应用的窗口 `hwnd 396004`）。`--bg` 模式不依赖前台（`clicks 0`、`keys 67` 全走 actor 键通道、59/60 完成），但这一条**必须随数字一起引用**（协议要求"前台没变记 True"，本批记的是 False）。
2. 本批属 chaos「**探索性·不并入定稿**」那一族（键通道 + `--bg`），**不与鼠标批（批次 4/5/6/9）并列成"提升/退步"**；可比对象只有**批次 7/8**。
3. `gate_ms` 在本批是**扣帧后**口径（批次 9 起），与批次 8 及更早的 `gate_ms` **不是同一个量**——跨批比成本要用 `ms_askgate / ask_gates`（本批 145.01 vs 批次 8 136.30）。

### ⑤ 成本（同批实测）

`shots 479`（批次 8 = 469）、`ocr 649`（633）、`ms_shot 30284.1`（34293.7）、`ms_ocr 142056.6`（128426.7）、`ms_askgate 17981.5`（16083.2）、`keys 67`（64）、`1901 ms/题`（1708）——**唯一有解释力的增量是每门 +8.71 ms**（与 §13.2 量到的像素段 ~3.6–4.1 ms 同量级），其余差异与墙钟一样受机器负载影响，不作结论。

### ⑥ 本批的一次作废尝试（方法学；与批次 9 ⑥ 同类但**根因不同**）

首跑 14:24:27 起，14:28:07 在 app 侧 `task_i 47`（driver 打印到 task 45/46）处死：stderr 原文

```
shot failed: {"ok": false, "steps": 1, "total_ms": 18.4, "trace": [{"i": 0, "op": "shot", "ms": 18.3, "ok": false, "error": "ValueError: cannot write empty image"}], "run_id": 1478}
```

⇒ `gym_run.py:508 raise SystemExit`（**设计如此**：空帧 = 会话不可用，宁可退出也不产假分）⇒ **不写 run json**，只留 `-state.json` / `-events.jsonl`（**逐题行全丢**，driver 侧新计数也随 json 一起丢）。
死前最后三条 app 事件是 `ready` / `chaos_planned`（`kind move`、`delay_ms 574`）/ `chaos`（`elapsed_ms 593.4`）⇒ **`move` 干扰触发的瞬间 `PrintWindow` 返回了空位图**（app 自报 `layout.origin [312,267]`，**不是批次 9 那种 `-32000` 离屏**）。
残留两个 app 进程（`24408` shim + `34776` 运行时）**活着但没有窗口**（UIA 顶层窗口表里 `GUI Gym` = 0）⇒ 已 `Stop-Process -Force` 清掉后重跑；重跑（14:31:00）正常跑满 60 题。
⇒ **新欠账 #17**：`shot` 空帧零容忍（一次空位图 = 整批退出 + 无 json）；修法是加一次短重试或记 `shot_retry`，**属判定路径之外，需单独一批**。
（首跑唯一留下的可比一行：`task_i 31 LUMEN93` 那次 **OK 2260.9 ms**——与重跑一致；但该批 events 已被重跑覆盖，**这一行不可再复核**。）





## 批次 11 结果（口径 v3；欠账 **#17「`shot` 空帧零容忍」还清**，只改抓帧失败的处理、判定路径一字未动）

本批只做一件事：把"抓帧拿到空位图 ⇒ `SystemExit` ⇒ **整批退出 + 不写 run json**"改成"**重试 3 次**（间隔 0.2 s、恢复链原样）+ 仍失败就把**已完成的题写成 partial run json**"。
改动清单见 `STATE.md` §15.3 / §15.5b：新增 `class ShotFailed(RuntimeError)`；4 处 `raise SystemExit` 改异常类型（消息原文不变）；main 用 `try` 包住整段题目循环；json 新增 `partial` / `exit_reason` / `tasks_planned`；partial run **返回码 3**；`score.py` 只加两行 `!! PARTIAL RUN` 警示。
**判定路径零改动**：`has_banner` / 指纹（`ask_cells`/`ask_delta`）/ 匹配路径 / 阈值 / `press_guard` / `_redo` / `score.py` 判定算法一字未动。

### ① 本批定稿行（鼠标通道 48 题 `t_trap5`，与批次 9 **逐项同协议、同 seed**；`scripts_sha 8da029edccbc`，`t_trap7-1.json` sha `dd77abc08e911794`）

```
t_trap5  v3 35/48  72.9%  decided 100.0%  disturb 0   screen 42/48 replan 31   1527 ms/task  keys 6  shots 165  ocr 421
         answered_right=35 wrong_target=7 false_refusal=6
         false_refusal 6/48 (12.5%)  false_accept 0/0 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
         fired-task pass 0/0  quiet 35/48 (72.9%)  swapped 38  a_hit 19  a_hit_but_failed 0  (wrong_target 0 / twin 0)
         variant nb046 0/3  nb050 0/3  nb065 2/2  nb100 2/2 · swap_after_press 5/5 · swap_hard_press 5/5
                 · swap_hard_timer 5/5 · swap_race_timer 4/10 · swap_timer 4/5 · swap_twin_press 8/8
         race(pressed the replaced ask) 7/7   (after the guard's frame 6)
         guard gate sample 73  P50 127 ms  P95 167 ms  (criterion P50<=240, P95<=320)
```

**与批次 9（`t_trap6-1.json`，36/48）逐项对照**：

| 项 | 批次 9 | 批次 11 | 差 |
|---|---|---|---|
| 总数 | 36/48（75.0%） | **35/48（72.9%）** | −1 题 |
| **核心 14**（`[0,4,9,10,13,14,18,21,24,26,28,29,33,34]`） | 12/14 | **12/14** | **ok→wrong 翻转 0** |
| `ms/题`（score.py 口径） | 1513 | **1527** | **+0.9%** |
| 逐行 `wall_ms` mean / p50 | 4552 / 3888 | 4463 / 3890 | −2.0% |
| `shots` / 每帧 | 167 / 227.0 ms | 165 / 218.6 ms | −3.7% |
| `ocr` / 每次 | 426 / 175.5 ms | 421 / 182.8 ms | −1.2% |
| `clicks` / `keys` / `replans` / `gates` | 62 / 6 / 44 / 74 | 61 / 6 / 43 / 73 | 各 −1 |
| `shot_empty` / `shot_retry` / `restores` | 旧代码无此键 | **0 / 0 / 0** | **失败分支一次未进** |

**唯一翻转 = `task_i 38` ok→wrong**（`swap_race_timer`，`clicked=GAMMA` want `QUARTZ`）。该族两批 `5/10 → 4/10`、`a_hit 2 → 1`、`race 6/6 → 7/7`。
**该题不在核心 14 内**，且**同族历来逐批漂移**（批次 8→9 漂过 `#44 wrong→ok`、`#45 ok→wrong`，总数 37/48 → 36/48）⇒ 本批把它记为**竞态族固有抖动**。
⚠ **本段没有做重复批**：要引用"task 38 = 噪声"必须先补 2–3 次同协议重复（未做，见 §⑦）。

### ② 判据（用户口径 i–iv，逐条）

| 判据 | 阈值 | 实测 | 结论 |
|---|---|---|---|
| i 重试后仍全空帧 | 只发生在"窗口不可达"类 | 构造 2（最小化）**4 次抓帧全空**、`shot_retry 2`、`restores 1`、`hwnd_relookup 2` ⇒ 重试救不回 | ✅ 字面成立（**这正是第二层"部分保存"存在的理由**，不是缺陷） |
| ii partial 与 `score.py` 不兼容 | 必须能打分 | 合成 partial（批次 9 截 20 行 + 三字段）：`v3 18/20`、join 20、警示两行、退出码 0；两条真构造产物也照常打分 | ❌ 不成立 |
| iii 核心 14 ok→wrong 翻转 | 0 | 12/14 → 12/14 | ❌ 不成立 |
| iv 正常路径性能 | 降 ≤ 5% | `ms/题` **+0.9%**；`shot_empty 0 / shot_retry 0`（失败分支零次进入）；逐行 `wall_ms` mean **−2.0%** | ❌ 不成立 |

### ③ partial 路径实测（**两条构造产物只做路径验证，不并入任何成绩**）

| 构造 | 手法 | 结果 |
|---|---|---|
| 永久类 | 6 题 `--keys --bg` 跑测第 14 s `Stop-Process` 掉两个 app 进程 | `t_trap7-empty6.json`(4354 B)：`partial=true`、`exit_reason="window 'GUI Gym' not found - is the app running?"`、`tasks_planned 6`、`runs 1`（第 0 题 OK 保住）、**退出码 3**、`score.py` 可读 |
| 窗口不可达 | 第 10 s `ShowWindow(SW_MINIMIZE)`（`FindWindow` 拿不到 hwnd ⇒ 用 ctypes `EnumWindows` 枚举标题） | 复现同一条 actor 报错 `ValueError: cannot write empty image`；`shot_empty 4 shot_retry 2 restores 1 hwnd_relookup 2 shots 6`；`t_trap7-minim6.json`(4546 B)：`partial=true`、`runs 1`、**退出码 3**；**app 仍活着**（state：`layout.origin [-32000,-32000]`、`result none`）⇒ **空帧 ≠ app 死了** |

⇒ **"瞬时"类空帧没能构造出来**（两种可控手法都落在"永久 / 不可达"类）："重试能救回瞬时空帧"这一半假设**既未证实也未证伪**；能确证的是**空帧不再丢批**。
⇒ 顺带更正一条旧注释："最小化能靠 `restore` 救回"**未复现**（最小化后该窗口对 `EnumWindows`/UIA 都不可见）⇒ 新盲区（见 `HANDOFF.md` §4 盲区 20）。

### ④ 引用这批时必须带上的三条

1. 本批 `foreground after: GUI Gym (hwnd 1706724) unchanged: True`（鼠标通道本来就要前台，与批次 9 同类；无前台异常）。
2. 两条 partial 构造用的是 6 题 `--keys --bg` 小批，**成绩不作引用**，只作"失败→落盘→可打分"的路径证据。
3. `partial` / `exit_reason` / `tasks_planned` 是**新键**：读旧批的脚本不受影响（旧批无这三键），但**跨批比较时不得把 partial 批与其他批的成绩并列**。

### ⑤ 成本（同批实测）

`shots 165`（批次 9 = 167）、`ocr 421`（426）、`keys 6`（6）、`clicks 61`（62）、`replans 43`（44）、`gates 73`（74）。
`ms/题` 由脚本内的墙钟决定、受机器负载影响（批次 9 与批次 11 的同一族漂移先例见批次 9 节）⇒ **只有 `shot_empty/shot_retry` 这两个新计数有解释力**：本批**零次**进入失败分支 ⇒ 改动对正常路径是**零成本**（不是"低成本"，是**不进这条代码**）。

### ⑥ 方法学：两个"看似打架"的口径

- `score.py` 行的 `ms/题`（1513 → 1527）与逐行 `wall_ms` 的 mean（4552 → 4463）**不是同一个量**（前者只统计到"判定到达"的窗口，后者含题间等待与重规划）⇒ 跨批比性能必须写清用哪一个。
- `score.py` 的 `screen 42/48`（本批）与驱动摘要的 `asks read off the screen: 69 / from the state file: 10` 也是**两个不同计数**（前者数"题面从屏幕读到的行数"，后者数"读取来源次数"）。

### ⑦ 本段**没做**的事（引用时不要把"未做"当"已证"）

1. **同协议重复 2–3 次**坐实 `task_i 38` 是噪声（只做了 1 次）。
2. **"瞬时空帧"的构造**（遮挡 / 抓帧偶发）：两种手法都是永久的 ⇒ 重试分支**在真实空帧下一次都没被走到**（只有构造产物里的 `shot_retry 2/2` 走过）。
3. **A/B 对照批**（用 `gym_run.py.bak-w5` 跑同协议小批）：未做；改动的零成本结论只由 `shot_empty 0 / shot_retry 0` 支撑。

---

## 批次 12（口径 v2；欠账 **#16「`popup` 类干扰打不掉」还清** —— 根因是 actor 折叠截断，只改"看窗口"的读法与清障计数，**判定路径一字未动**）

`t_trap2-w12-popup35.json` / `-state.json` / `-events.jsonl`；`scripts_sha **186edbd9c024**`；`gym_run.py` `105cf6cb679eea10` → **`87470aaff559`**（`gym_app.py` / `score.py` 未动）。
协议与批次 8 的 `popup35` **逐项相同**（`--keys --bg`、`t_trap2`、seed 20251007、`chaos 0.35`、`chaos-ms 200,700`、`chaos-kind popup`、`--no-topmost`、60 题、**未传 `--until-interferences`** ⇒ 跑满不早停），只有驱动版本不同。

### ① 根因（直接探针，2026-10-05 第十段）

- **弹窗一直能被 UIA 看见**：`{"op":"uia","what":"windows","max":120}` 的 trace 里有 `{"name":"attention","cls":"TkTopLevel","type":"Window","rect":[…]}`（同列表 11 项）。
- **真正的原因 = actor 折叠截断**：同一条 trace 条目里 **inline `windows` 11 项**，而 **`data.windows` 只有 7 项** —— `actor.py:_slim()` 对 list **只保留前 ~6 项**，`data` 只在 `results=True` 时写入。改前 `window_by_title()`（以及 `target_windows()`）**只读 `step["data"]["windows"]`** ⇒ "attention" 一落到截断之后，`window_by_title("attention")` 恒 `None` ⇒ 键通道 bg 分支第一行就 `break` ⇒ **一次 Return 都没发**。
- 探针方式与坑（写进这里以免下次再踩）：actor `:8731` 是**裸 TCP + 换行 JSON**（`{"op":"run","steps":[…]}`），**不是 HTTP**；**WSL 到不了 Windows loopback** ⇒ 必须 pwsh + Windows venv python；复刻驱动读法的脚本 = `D:\DSH\dsh-actor\tmp\w10-uia-probe3.py`。
- 批次 8 原始产物复核（旧驱动 `f598406cfc70`）：`t_trap2-w8-popup35.json` 只 **7** 行 / `max task_i 4` = 4 ok + 3 none；`t_trap2-w8-popup70.json` 只 **4** 行 / `max task_i 1` = 1 ok + 3 none；两批 `interferences 0`、`clicks 0 / drags 0`、无 `popup_*` 键；而 app 事件显示驱动发的键**到了 app**（`hit:true, modal:true`）却没计分（`gym_app.py:465-481 finish()` 的 modal 门）。
- ⚠ 本节推翻了批次 8 ③ 的一半判断（那里说"没有这条路"）：**路在，是读错了字段**。原判断的另一半**仍然成立**：`_button_candidates` 那条视觉路在 `--keys --bg` 下**不可用**（弹窗是独立 HWND、不在主窗帧里；且 `--bg` 鼠标点击整条失效，见 `STATE.md` §16）⇒ 只能走"按键打掉"（app 自己的设计：`gym_app.py:376-383` 弹窗在时 `Return/space/Escape/d/D` 直接关）。

### ② 本批定稿行

```
chaos:popup    v2 60/60 100.0%  decided 100.0%  disturb 15  screen 50/60 replan 29    1714 ms/task  keys 109   shots 402  ocr 595
               answered_right=46 refused_right=14
               false_refusal 0/46 (0.0%)  false_accept 0/14 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 15/15 (100.0%)  quiet 45/45 (100.0%)  swapped 15  a_hit 10  a_hit_but_failed 0  (wrong_target 0 / twin 0)
               variant alpha020 2/2  variant alpha030 2/2  variant alpha035 2/2  variant alpha050 2/2  variant alpha065 2/2  variant prose_only 4/4  variant prose_with_button 6/6  variant swap_after_press 10/10  variant swap_timer 5/5
               swap by variant  swap_after_press n=10 a_hit=10 wrong=0  swap_timer n=5 a_hit=0 wrong=0  race(pressed the replaced ask) 0/0
               guard gate sample 70  P50 127 ms  P95 138 ms  (criterion P50<=240, P95<=320)
```

驱动统计：`popup_seen 24`、`popup_dismissed 24`、`popup_dismiss_failed`（键不出现 = **0**）、`interferences 24`、`replans 29`、`keys 109`、`shots 402`、`ocr 595`、`asks_from_screen 78`、`asks_from_file 11`、`shot_empty 0 / shot_retry 0`、`key_errors 0`、`verify_calls 74`；`foreground after: <用户前台窗口> unchanged: True`。
app 事件：`chaos_planned 25` / `chaos 25`（全 `popup`）、`key 109`、`trap_swap 15`、`trap_a_hit 10`、`done 60`、`refused 14`、`ready 61`（**无 `blocked` 类事件**，批次 8 也没有 ⇒ 不要引用"app emit blocked"）。

### ③ 判据（本段规格，逐条）

| 判据 | 阈值 | 实测 | 结论 |
|---|---|---|---|
| 能 fire ≥ 5 次 | ≥5 | app 侧 **25** 次 `chaos`（24 个不同 task 被清障）+ 15 题题内命中 | ✅ |
| 不早停 | 跑满 60 题 | 逐题行 **60**（`max task_i 59`）、`done 60`、退出码 0、`--max-repeat` 未触发 | ✅ |
| 有 dismiss 记录 | ≥1 | `popup_seen 24` / `popup_dismissed 24` / `popup_dismiss_failed 0` ⇒ **24/24 全成** | ✅ |

### ④ 改动前后对照（**旧数据 = 批次 8 的历史产物**，不是随机对照）

| 项 | 批次 8 `popup35`（旧驱动 `f598406cfc70`） | 批次 12（新驱动 `186edbd9c024`） |
|---|---|---|
| 逐题行 / 最大 `task_i` | 7 / 4（早停） | **60 / 59** |
| 逐题结果 | 4 ok + **3 none** | **60 ok** |
| 驱动 `interferences` | **0** | **24** |
| `popup_seen / dismissed / failed` | 键不存在 | **24 / 24 / 0** |
| app 侧 `chaos`（popup） | 1（早停前只发 1 次） | **25** |
| `clicks / drags` | 0 / 0 | 0 / 0（纯键通道） |
| `score.py` | 无（批早停，不进任何表） | `v2 60/60` |

### ⑤ 恢复路径与时间口径

- `replan_why = "no verdict arrived"` **12 行，全部 `result = ok`**：这些正是"被弹窗吞掉第一次按压 → 重答"的题（`presses 1` 首答 + `replans 1` 重答）；`ask re-rolled` 14 行是换题类（与批次 8 同类）；其余 34 行无重规划。
- 逐题 `ms`：**1748.6**（n=12，被吞过）vs **1639.5**（n=34，未被吞）⇒ 恢复代价 **+6.7%**；全批均值 **1715.0**（= `score.py` 的 `1714 ms/task`）。
- 驱动墙钟 **3627 ms/题**（222.7 s / 60 题）与 `ms/题` **不是同一个量**（差额在题间建题/轮询与清障）⇒ **未细分，不并入性能结论**。

### ⑥ 引用这批时必须带上的边界

1. **与批次 8 的对照是"历史产物对照"**：驱动版本不同、无同批 A/B ⇒ 只能说"**这一类现在可测了**"，**不能说"改动提升了通过率"**（批次 8 没有可比的分母）。
2. **旧的 `interferences 0` 一律不可读成"没被干扰"**：那是"打不掉"的缺陷；批次 7/8 的 `popup` 两档成绩仍然**不可引用**。
3. **本批仍是「探索性·不并入定稿」**：键通道 + `--bg`，与鼠标批（批次 4/5/6/9/11）**不同通道、不同协议**，不能与之并列成"提升/退步"。
4. **`disturb 15` 只数"题内"清障**：驱动 `interferences 24` = 逐题行合计 **15** + `interferences_at_start` 合计 **9**（题首清障，`gym_run.py:2033-2034`）—— 两个计数不可互推；`screen 50/60` 与驱动摘要的 `asks read off the screen 78 / from the state file 11` 也是两个不同计数。
5. **app 侧 fire 25 对驱动清障 24 差 1 次**：两种候选解释（落在最后一题之后 / 被下一次换题的 `self._close_modal()`，`gym_app.py:512` 顺手关掉）**都成立，未取证** ⇒ 只并列、不裁定。
6. **没做的事**：同协议重复批（1 次）、`0.70` 档复跑（批次 8 的 `popup70` 仍是旧驱动的失败产物）、鼠标通道批（`--bg` 鼠标整条不生效）、A/B 对照批（用 `D:\DSH\dsh-actor\tmp\gym_run.py.bak-w10` 跑同协议）。
7. **本批留档**：`t_trap2-w12-popup35.json` / `-state.json` / `-events.jsonl` + 驱动 stdout `D:\DSH\dsh-actor\tmp\w12-driver-stdout.txt`；改前备份 `D:\DSH\dsh-actor\tmp\gym_run.py.bak-w10`（sha `105cf6cb679eea10`）。

### ⑦ 成本

新增三计数只在"真看到弹窗"时才动（本批 24 次），每次 `popup_dismissed/failed` 判定多一次 UIA 枚举（本批 24 次 × 约 40–70 ms ≈ 1.2 s，占 222.7 s 墙钟 < 1%）。无弹窗的题**零成本**：键分支的闸门在 `--keys --bg` 下本来就走一次枚举，只是改前读错字段。`shot_empty / shot_retry 0/0`、`key_errors 0`、`stale 0`、`wasted 0`、`verify_giveup 0`。

---

## 批次 13 结果（2026-10-05 第十一段）—— 欠账 #19「`popup` 只跑了 1 档 1 通道」的覆盖面补测

**本批目的**：批次 12 只给出「**0.35 档 + 键通道**」的可测证据。本段按规格补两条覆盖面：**另一强度档（0.70）** 与 **另一条通道（鼠标前台）**。**代码一字未改** —— 三件套 sha 与批次 12 相同（`gym_app.py 66632d85eac8` / `gym_run.py 87470aaff559` / `score.py ef066713a03e`）。

### 13.1 第一批：0.70 档 · 键通道（**成功**，判据全过）

- **命令（逐字）**：`gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind popup --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out t_trap2-w13-popup70.json`
- **留档**：`sol/sandbox/t_trap2-w13-popup70.json`（+ `-state.json` / `-events.jsonl`）；驱动 stdout `D:\DSH\dsh-actor\tmp\w13-driver-stdout-p70.txt`；打分输出 `D:\DSH\dsh-actor\tmp\w13_score70.txt`。`scripts_sha 186edbd9c024`、`partial False`、退出码 **0**、墙钟 **250.9 s**（驱动自己计的 4095 ms/题）。
- **干跑**（同协议 `--tasks 2`，`D:\DSH\dsh-actor\tmp\w13-dry70.json`）：`2/2 ok`（task 0 OK 4721 ms = 首题有真按压）、`disturbances: 1 fired`。

#### ① 定稿行（逐字，`score.py` 输出）

```
chaos:popup    v2 60/60 100.0%  decided 100.0%  disturb 24  screen 54/60 replan 38    1755 ms/task  keys 139   shots 450  ocr 658
               answered_right=46 refused_right=14
               false_refusal 0/46 (0.0%)  false_accept 0/14 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 24/24 (100.0%)  quiet 36/36 (100.0%)  swapped 15  a_hit 10  a_hit_but_failed 0  (wrong_target 0 / twin 0)
               variant alpha020 2/2  variant alpha030 2/2  variant alpha035 2/2  variant alpha050 2/2  variant alpha065 2/2  variant prose_only 4/4  variant prose_with_button 6/6  variant swap_after_press 10/10  variant swap_timer 5/5
               swap by variant  swap_after_press n=10 a_hit=10 wrong=0  swap_timer n=5 a_hit=0 wrong=0   race(pressed the replaced ask) 0/0
               guard gate sample 73  P50 122 ms  P95 134 ms  (criterion P50<=240, P95<=320)
```

#### ② 判据（本段规格，逐条）

| 判据 | 阈值 | 实测 | 结论 |
|---|---|---|---|
| 能 fire ≥ 5 次 | ≥5 | 驱动 `interferences` **45**（逐题行合计 **27** + 题首 `interferences_at_start` **18**）；`score.py` `disturb 24` = **有干扰的 task 数**（驱动摘要同句："45 fired over 60 task(s), **24 task(s) had >=1**"） | ✅ |
| `popup_seen ≥ 5` | ≥5 | **45** | ✅ |
| `popup_dismissed == popup_seen` | 相等 | **45 == 45**（`popup_dismiss_failed` **键不存在** ⇒ 0） | ✅ |
| 不早停 | 跑满 60 题 | 逐题行 **60**（`max task_i 59`）、全 `ok`、`stopping: 45 disturbance(s) fired over 60 task(s)`、退出码 0 | ✅ |
| `score.py` 正常 | 打印成绩行 | `v2 60/60 100.0%`（上方定稿行） | ✅ |

- **与 0.35 档并排**（同通道、同协议，只差档位）：0.35（批次 12，`t_trap2-w12-popup35.json`）`popup_seen/dismissed/failed 24/24/0`、`disturb 15`、`1714 ms/task`；0.70（本批）`45/45/0`、`disturb 24`、`1755 ms/task` ⇒ **强度档更高时清障仍然逐次成功，且不早停**。
- **`replan_why`**：`None` 28 / `no verdict arrived` 18 / `ask re-rolled` 14（合计 60）。`no verdict arrived` = 被弹窗吞掉一次按压后的重答路径（等判定循环里清障成功即 `break` 重答）。
- **其它计数**：`keys 139`、`shots 450`、`ocr 658`、`asks_from_screen 90` / `asks_from_file 8`、`verify_calls 77`、`focus 98`、`shot_empty 0`、`shot_retry 0`、`key_errors 0`、`stale 0`、`wasted 0`、`verify_giveup 0`、`re-reads 0`、逐题 ms 均值 **1755.3**。

### 13.2 第二批：鼠标通道 · 0.35 档（**失败**，按规格停手、记新欠账）

- **命令（逐字）**：`gym_run.py --scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --chaos 0.35 --chaos-ms 200,700 --chaos-kind popup --json-out t_trap5-w13-popup35.json`（鼠标通道协议照批次 4/5/6/9/11，只加 chaos 三参数；**用户已放行前台**）。
- **结果**：**driver 退出码 1、墙钟 79.1 s、只跑到第 3 题**（`score 0/3`、`stopping early: task 0 failed 3 times in a row`）。留档 `sol/sandbox/t_trap5-w13-popup35.json`（+ `-state.json` / `-events.jsonl`）、日志 `D:\DSH\dsh-actor\tmp\w13_mouse35.log`、`w13-driver-stdout-mouse35.txt`、`w13_score_mouse35.txt`。
- **驱动侧**：`disturbances: 0 fired`（**清障一次都没发生**）、`keys 0`、`clicks 10`、`shots 47`、`ocr 124`；三题同一 ask（`TANGQ`）、逐题 27317 / 24117 / 24071 ms、`detail = {"ask_box_recomputed": 4, "ask_box_shift_px": [0, 0]}`；`foreground after: GUI Gym (hwnd 3148420) unchanged: False`。
- **app 侧（决定性证据）**：`t_trap5-w13-popup35-state.json` = `task_i 0`、`variant swap_twin_press`、`result none`、`elapsed_ms 71283`、**`"event": "blocked", "by": "modal"`**；events 计数 = `ready 1 / chaos_planned 1 / chaos 1 / trap_a_hit 1 / trap_swap 1 / blocked 10 / trap_twin_timeout 1` ⇒ **弹窗真的弹了、并且一直没被清掉**，`finish()` 的 modal 门让该题永不结算（与批次 8 同一条门，`gym_app.py:465-481`）。
- **`score.py` 输出（逐字）**：

```
chaos:popup    v3  0/1    0.0%  decided 100.0%  disturb 0   screen  1/1  replan 2     2544 ms/task  keys 0     shots 47   ocr 124
               wrong_target=1   extra_attempts 2 (rows collapsed to one per task)
               false_refusal 0/1 (0.0%)  false_accept 0/0 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 0/0 (0.0%)  quiet 0/1 (0.0%)  swapped 1  a_hit 1  a_hit_but_failed 1  (wrong_target 0 / twin 1)
               variant swap_twin_press 0/1
               swap by variant  swap_twin_press n=1 a_hit=1 wrong=1   race(pressed the replaced ask) 0/0
               guard gate sample 3  P50 156 ms  P95 158 ms  (criterion P50<=240, P95<=320)
               wrong_target  #0   truth=answerable  dec=acted   act=click_label    result=none clicked=null
```

- **机制（代码级读出的候选，本段未跑探针坐实）**：`dismiss_interference()` 的**鼠标分支**（`bg=False, keys=False`）——① **没有任何 `popup_*` 计数**（三计数只加在键分支）⇒ 这一支"没看见"与"看见了但没点"在数据上**不可区分**；② 候选走 `self._button_candidates(img, "DISMISS")`（**默认 `keep_vetoed=False`**），而键分支的存在性判据特意传 `keep_vetoed=True`，注释写明 "the veto would drop a dialog whose button is not painted as a block"；③ `_button_candidates` 的 docstring 另记一条实测："a whole-window sparse pass can miss a short bold label（**measured on the practice dialog, whose DISMISS button no word pass ever returned**）" ⇒ 靠**块路径**兜。所以本支失败的两个候选机制：**(a) 候选被 veto 丢掉**；**(b) 这一帧里根本没有该按钮**（抓帧路径不同）。
- **为什么不再跑**：本段规格 §五写明"任何一批跑不通 ⇒ 停，写欠账"；定位这两个候选需要一次**只读探针**（把弹窗帧 dump 下来、对 `_button_candidates` 的两种 `keep_vetoed` 各跑一遍），那是 #20 的第一步，不在本段。

### 13.3 两批判据汇总

| 批次 | 档位 | 通道 | `popup_seen` | `popup_dismissed` | 早停 | 退出码 | 结论 |
|---|---|---|---|---|---|---|---|
| 批次 12 | 0.35 | 键 + `--bg` | 24 | 24 | 无（60 题） | 0 | ✅ 可测 |
| 批次 13 第一批 | 0.70 | 键 + `--bg` | 45 | 45 | 无（60 题） | 0 | ✅ 可测 |
| 批次 13 第二批 | 0.35 | 鼠标前台 | 键不存在（该支无计数） | 键不存在 | **有（3 题）** | **1** | ❌ 不可用 |

### 13.4 引用这批时必须带上的边界

1. **键通道两个强度档都成立**，但都是**单次批**、无重复批、无同批 A/B（与批次 8 仍是历史产物对照）⇒ 只能说"**这一类在键通道下可测且这一批逐次成功**"，不能说"提升"。
2. **鼠标通道那一批不进任何成绩**：早停、退出码 1、分母只有 1 题；它唯一的用处是**证明该支当前不可用**（见 #20）。
3. **#19 只关闭一半**：覆盖面从「1 档 1 通道」变成「**2 档 1 通道**」；**鼠标通道仍空** ⇒ #19 状态 = **部分达标（键通道两档）**，剩余部分与 #20 合并处理。
4. **`popup` 仍是探索性线**（键通道 + `--bg`，与鼠标批不同通道不同协议）⇒ 不与批次 4/5/6/9/11 并列。
5. **两个计数不可互推**：驱动 `interferences 45` 是**清障次数**（题内 27 + 题首 18）；`score.py` 的 `disturb 24` 是**有干扰的 task 数**（与驱动同句的 "24 task(s) had >=1" 一致）—— 次数 vs 题数，不是同一个量。
6. **"鼠标分支没有计数"本身就是一条测量缺陷**（与候选 veto 问题一起记入 #20）：不要把这批的 `0` 读成"这一支没被触发"——它在 app 侧留下了 `blocked 10` 与 `chaos 1`。

### 13.5 本段新增欠账 #20（落在 `STATE.md` §7）

**鼠标通道下 `popup` 清障路径不生效。** 证据 = 13.2；该分支没有 `popup_*` 计数、候选走默认 veto。
**判据（怎么算还清）**：鼠标通道的 `popup` 批跑满题数且 `popup_dismissed == popup_seen ≥ 5`；**或**明确宣告"鼠标通道不支持清障"并把该组合从覆盖面里划掉。
**出处**：本节 13.2 / 13.5 + `STATE.md` §19 + `HANDOFF.md` 盲区 17。

---

## 批次 14 尝试（2026-10-05 第十三段）—— 欠账 #20 修复（`STATE.md` §20.4 选项 D）：**未通过判据，已回退**

### 14.0 一句话

按 §20.4 的**选项 D** 改了 `dismiss_interference()` 的**非 bg 鼠标分支**（照抄隔壁 `if self.bg` 分支：读弹窗自己的窗口帧 + 点击不带 `front_title`），并修掉 `shot_window()` 的**坐标原点**问题；**干跑通过**（`--tasks 2`：2/2、`popup_seen 2 / dismissed 2`、5.3 s/题），但**正式批在 task 21 早停**（连续 3 次失败、退出码 1）⇒ 按规格的终止条件**回退改动**，`gym_run.py` 回到 `87470aaff559`。本批**不进成绩**，只作为"选项 D 的方向被验证有效、但仍有残留竞态"的证据。

### 14.1 改了什么（两处，都在弹窗清理路径内）

| # | 位置 | 改动 |
| --- | --- | --- |
| 1 | `dismiss_interference()` 非 bg 鼠标分支 | 改为 `window_by_title("attention")` 判在不在 → `shot_window("attention")` 取**弹窗自己的帧** → 候选取自该帧 → 用一条**不带 front 请求**的 `click` 直投 |
| 2 | `shot_window()` | 屏幕原点改用回包的 **client origin**（`origin`），不再用**窗口 rect** |

- **影响范围判定 = 只影响弹窗清理**：`shot_window()` 的调用点只有 `dismiss_interference()` 里的两条（`if self.bg` 分支 + 非 bg 分支）—— 共享的 `click()` / `_shot()` / `_button_candidates()` / `screen()` **一行未动**。
- **规模**：净 **+26 行**（adds 36 / dels 10，其中注释 20 行）；未超 30 行硬闸。
- **中间 sha**：第一版（只改分支）= `gym_run.py 6690c1038c7f42f7`；加上原点修复后 = **`85893817760a3be5`（本批跑的版本）**；`gym_app.py 66632d85eac81c12` / `score.py ef066713a03eb940` 全程未动。
- `py_compile` 通过；`score.py --selftest` = **41 checks, 0 failed**。

### 14.2 干跑（`--tasks 2`，鼠标通道、`--chaos 1.0 --chaos-kind popup`）

```
task  0 t_trap2   click the button labelled GAMM.                      OK      5326ms
task  1 t_trap2   click the button labelled INDIGO                     OK      5372ms

score 2/2 ok (100% of tasks) | per task 5349 ms avg | shots 14 ocr 28 clicks 6
disturbances: 2 fired over 2 task(s)
```

stats = `popup_seen 2 / popup_dismissed 2`（`popup_dismiss_failed` 键不存在）、`clicks 6`、`interferences 2`。⇒ 修好原点后清障路径**当场生效**；第一版（用窗口 rect）时是 `popup_seen 13 / popup_dismiss_failed 13`、两题全 NONE（点击落在按钮**上方 45 px**）。

### 14.3 正式批 A（唯一一次，跑完立刻打分）

命令（Windows 侧 `Start-Process -WindowStyle Normal`，工作目录 `sol/sandbox`）：

```
gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --chaos 0.35 --chaos-ms 200,700 --chaos-kind popup --json-out t_trap2-w13-popup35-mouse-fix.json
```

结果：**exit 1**、墙钟 **161.2 s**、`stopping early: task 21 failed 3 times in a row`；驱动摘要 `score 21/24 ok (88% of tasks)`、`per task 6551 ms avg`、`shots 179 ocr 306 clicks 52 keys 0 drags 0`、`asks read off the screen 37 / from the state file 7`、`disturbances: 11 fired over 24 task(s), 1 task(s) had >=1`、`foreground after: GUI Gym (hwnd 10029804) unchanged: True`；run json `scripts_sha 871ed27ca066`、`partial False`、`exit_reason None`。

判据相关计数：`popup_seen 11`、`popup_dismissed 10`、`popup_dismiss_failed 1`、`interferences 11`、`replans 23`、`ask_moved 3`。

`score.py` 定稿输出（**逐字**）：

```
chaos:popup    v2 21/22  95.5%  decided 100.0%  disturb 1   screen 15/22 replan 16    2029 ms/task  keys 0     shots 179  ocr 306
               answered_right=21 false_accept=1   extra_attempts 2 (rows collapsed to one per task)
               false_refusal 0/21 (0.0%)  false_accept 1/1 (100.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 1/1 (100.0%)  quiet 20/21 (95.2%)  swapped 15  a_hit 10  a_hit_but_failed 0  (wrong_target 0 / twin 0)
               variant prose_only 0/1  variant prose_with_button 6/6  variant swap_after_press 10/10  variant swap_timer 5/5
               swap by variant  swap_after_press n=10 a_hit=10 wrong=0  swap_timer n=5 a_hit=0 wrong=0   race(pressed the replaced ask) 0/0
               guard gate sample 38  P50 148 ms  P95 174 ms  (criterion P50<=240, P95<=320)
               false_accept  #21  truth=must_refuse dec=acted   act=click_label    result=none clicked=null
```

app 侧（`t_trap2-w13-popup35-mouse-fix-state.json` / `-events.jsonl`）：state = `task_i 21 / result none / variant prose_only / event ready`；events = `ready 22 / trap_a_hit 10 / trap_swap 15 / done 21 / chaos_planned 10 / chaos 10 / blocked 1`。

**B 批（回归）未跑**：改动已按终止条件回退，被测代码回到 HEAD ⇒ 没有可回归的对象。

### 14.4 判据

| 判据 | 结果 |
| --- | --- |
| `popup_seen ≥ 5` | ✅ **11** |
| `popup_dismissed == popup_seen` | ❌ **10 / 11** |
| 不早停 | ❌ **task 21 连续 3 次失败、退出码 1** |
| 改动 ≤ 30 行、只碰弹窗清理路径 | ✅ 净 +26 行、两处都在清障路径内 |

⇒ **未通过** ⇒ 按规格：回退 + 写欠账 + 跳第三步（报告 v0.4）。

### 14.5 残留失败机制（证据 + 下一步假设）

- 现象：11 次清障 **10 次成功、1 次失败**；失败之后**没有任何重试**（`popup_seen` 不再增长），题目卡在"被弹窗挡住"（app 侧 `blocked 1`），驱动连续 3 次拿不到判定 ⇒ 早停。
- 代码层候选：① 那一次点击**没命中**（弹窗刚创建、帧与点击之间的竞态）；② **同一点不会重试** —— 清障循环用 `tried` 去重，而弹窗自己的帧上默认 veto 只给**一个**候选 ⇒ 一旦这一下没中，**同一个调用内不会补点**；③ 调用方 `gym_run.py:3460` 在清障计数 ≠ 0 时直接 **break 去 replan**，此后**再没有人回到这个弹窗** ⇒ 一次未命中 = 整题死锁。
- 下一步（明天可做，代价从小到大）：**(a)** "清障后弹窗仍在"时**允许对同一点再点一次**（≤2 次）；**(b)** 清障失败时**降级**用 `key("Return")`（app 自己绑定：主窗收到该键就关掉自己的对话框）；**(c)** 先把 ③ 的"break 去 replan"改成"再清一次再 replan"。

### 14.6 引用这批时必须带上的边界

1. **本批不进任何成绩**：早停、退出码 1；`false_accept 1` 来自被弹窗卡住的那道题，不是驱动判错。
2. **它对应的驱动版本不在仓库里**（`85893817760a3be5` 已回退）⇒ **不可复现、不可与任何批次并列**；补丁留档 `D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`（77 行）。
3. **结论只能说到这一步**：选项 D 的**方向被验证有效**（清障 0 → 10/11），但**判据未达成**；**#20 仍然开着**。
4. **与批次 13-B 不可直接比**：13-B 是"一次都没点中"（`dialog_refused 28`），本批是"点中了 10 次、漏 1 次"。
5. **`popup_seen / popup_dismissed / popup_dismiss_failed` 三个计数在本批进入鼠标分支**（键分支早就有）⇒ 以后凡说"鼠标分支没看见弹窗"必须给出这三个数。
6. **`shot_window()` 的坐标原点坑与回退无关**：窗口 rect 与 client origin 实测差 **+11 / +45 px**，任何"窗口 rect + 帧内坐标"的点击都会偏 45 px（已写进 `HANDOFF.md` 盲区 23）。

## 批次 15（2026-10-05 第十四段）—— 欠账 #20 第二次尝试（选项 b：漏点后降级 `key("Return")`）：**干跑即失败，未成批**

### 15.0 一句话

按 `STATE.md` §20.4 的三条候选选了 **(b) 降级 `key("Return")`**（净 **+24 行**，只落在非 bg 鼠标分支的"漏点处理"路径上），`py_compile` 与 `selftest 41/0` 都过；但**干跑 2 题就失败**（两题全 NONE、退出码 1、`popup_seen 13` 而 **`popup_dismissed` / `popup_key_dismissed` 键根本不存在 = 13 次发现、0 次清掉**）⇒ 按本段终止条件**立即回退**，**A 批 / B 批都没跑**（不试第二遍改动），`#20` **仍然开着**。

### 15.1 改了什么（一处，只在"漏点处理"路径里）

`dismiss_interference()`（`gym_run.py:900`）**非 bg 鼠标分支**：原"读 app 矩形帧 → 找候选 → 点 → 睡 0.3 s → 再看还有没有候选"的循环**原样保留**，循环之后新增：

```python
# the click loop can still miss (batch 14: 1 popup in 11 stayed up and that one
# miss deadlocked the whole run), so fall back to the key the app itself binds
# on the dialog button: no coordinates, no stacking, no pixel reading.
if self.window_by_title("attention") is not None:
    if seen == 0:
        self.stats["popup_seen"] = self.stats.get("popup_seen", 0) + 1
    for _ in range(tries):
        self.key("Return")
        seen += 1
        self.stats["interferences"] += 1
        time.sleep(0.35)
        if self.window_by_title("attention") is None:
            self.stats["popup_key_dismissed"] = self.stats.get("popup_key_dismissed", 0) + 1
            self.stats["popup_dismissed"] = self.stats.get("popup_dismissed", 0) + 1
            break
    else:
        self.stats["popup_dismiss_failed"] = self.stats.get("popup_dismiss_failed", 0) + 1
```

- `git diff --stat` = **24 insertions(+), 0 deletions(-)**（未触本段 30 行硬闸）。
- **没碰**：`click()` / `_shot()` / `_button_candidates()` / `screen()` / 判定逻辑 / 匹配路径 / 阈值；`gym_app.py`、`score.py` 一行未动；批次文件未动。
- 闸门：`py_compile` 通过；`score.py --selftest` = **41 checks, 0 failed**。
- **sha 轨迹**：`gym_run.py 87470aaff5593330`（HEAD）→ **`178591e19c40c37f`**（本次改动）→ **`87470aaff5593330`**（回退后，与 `origin/main` 一致）；`gym_app.py 66632d85eac81c12` / `score.py ef066713a03eb940` 全程未动。
- 补丁留档：`D:\DSH\dsh-actor\tmp\w16-popup-key-fallback.patch`（**35 行**）。

### 15.2 干跑（`--tasks 2`，鼠标通道、`--chaos 1.0 --chaos-kind popup`、`--seed 20251007`）

命令：`gym_run.py --scenario t_trap2 --tasks 2 --seed 20251007 --chaos 1.0 --chaos-ms 200,700 --chaos-kind popup --json-out D:\DSH\dsh-actor\tmp\w16-dry.json`（Windows 侧 `Start-Process -WindowStyle Normal`，日志 `D:\DSH\dsh-actor\tmp\w16_dry.log` / `.err`）。

驱动输出（逐字）：

```
gym driver: window (316, 313, 1496, 1093)  actor port 8731  chaos 1.00
foreground before: attention (hwnd 592176)
task  0 t_trap2   click CEE a7                                         NONE   40320ms  {}
task  1 t_trap2   click CEE a7                                         NONE   36352ms  {}

score 0/2 ok  (0% of tasks)
per task: 38336 ms avg  |  actor calls 0  shots 20  ocr 85  clicks 0  keys 45  drags 0
asks read off the screen: 1  from the state file: 6  (2 task(s))
disturbances: 39 fired over 2 task(s), 2 task(s) had >=1; verify calls 0, re-reads 0, give-ups 0, stale 0
foreground after:  搜索 (hwnd 66100)  unchanged: False
```

`w16-dry.json`（逐字）：`exit_reason None`、`partial False`、`mode {bg false, keys false, chaos 1.0, chaos_kind popup, chaos_ms "200,700", max_tasks 2}`、`stats {clicks 0, keys 45, interferences 39, replans 66, popup_seen 13, popup_dismiss_failed 13, dialog_refused 1, refusals 6, ask_guard_runs 1, ask_moved 1, shots 20, ocr 85, ms_ocr 41943.9, ms_key 2331.1, ms_window 316.9}`。

**判读**：`popup_dismissed` 与 `popup_key_dismissed` **两个键在 stats 里根本不存在** ⇒ 新增的降级路径**一次都没成功**（13 次发现弹窗、13 次记 `popup_dismiss_failed`、45 次 Return 全部落空）；两题都因"弹窗立着 ⇒ app 什么都不判分"而超时 NONE。

### 15.3 判据（事前写死在 `STATE.md` §23.1）

| 证伪条件 | 结果 |
| --- | --- |
| (i) 改后 `popup_seen > 0` 但 `dismissed < seen` | **成立（更强）**：`seen 13` / `dismissed` **键不存在 = 0** |
| (ii) 改后 B 批（鼠标 48 题）核心 14 翻转 | **未测**（B 批没跑：干跑即证伪） |
| (iii) 改动 > 30 行 | 不成立（**+24 行**） |
| A 批判据：`popup_seen ≥ 5` 且 `dismissed == seen` 且不早停 | **未跑**（干跑 `dismissed == 0`，跑 60 题只是把同一失败重复 60 次） |

### 15.4 机制结论（本段真正的产出）

- `Driver.key()`（`gym_run.py:1175-1198`）**只在 `self.keys and self.bg` 时才加 `focus: True`**。非 bg 通道发的是**真实 SendInput 按键**，Windows 只把它交给**真前台窗口**；本机 DSH 会不断抢回前台（实测 `foreground after: 搜索 (hwnd 66100) unchanged: False`）⇒ **45 次 Return 全部没落到弹窗上**。
- 对照：**鼠标点击是"按坐标"投递**的，弹窗又是 `-topmost` ⇒ 像素命中就一定命中它的窗口。⇒ **批次 14 的 `10/11` 不是"快好了"，而是"这条通道里唯一能到弹窗的机制"的副作用**；剩下的 `1/11` 不是调参能补的。
- 键通道（`--keys --bg`）能 24/24、45/45 地关弹窗，靠的是**把按键直接投递给 app 窗口 + `focus=True` 做焦点交接**，**不是**"真实按键能到前台"。⇒ **(b) 这条方向不是"没写对"，而是结构上不成立**；要成立必须给鼠标通道加同等的托管投递（= `DESIGN-18-scroll-drag.md` §4 的 **B 方案**，裂 sha 且改动落在执行器侧、`scripts_sha` 覆盖不到），不属于"优先小改动"。

### 15.5 引用这批时必须带上的边界

1. **它不是批次**：只有 **2 题干跑**，`score 0/2`，**不进任何成绩**；`w16-dry.json` 是诊断证据。
2. **不可复现**：它对应的驱动版本（`178591e19c40c37f`）**不在仓库里**（已回退）；补丁只在本机 `D:\DSH\dsh-actor\tmp\w16-popup-key-fallback.patch`。
3. **不能与批次 13-B / 14 并列**：13-B = "一次没点中"（该支无计数），14 = "点中 10 次、漏 1 次"，15 = "点 0 次 + 按键 45 次全落空"。
4. **`popup_seen / popup_dismissed / popup_dismiss_failed` 之外新增过 `popup_key_dismissed`**，回退后该键**不存在**（只有回退前的这次干跑记录里有）。
5. **`#20` 仍然开着**：三条候选里 (b) 已被本段**实测否掉**（结构不成立），(a) 未试（对着未知原因再赌一次），(c) 未试且 `STATE.md` §23.1.1 已论证**单独修不好**；下一步只能在 A（前台鼠标批）/ B（加托管通道）/ C（接受边界）里选。
6. **干跑前后的环境是干净的**：跑完 `uia what=windows max=200` 里没有任何 'GUI Gym' / 'attention' 窗口，Windows 侧 python 进程只剩 actor `12008` + `32248`。

## 批次 16（2026-10-05 第十六段）—— 欠账 #20 第三次尝试（**重落选项 D 补丁 + 拆「漏一次点 ⇒ 整题死锁」耦合**）：**16 题前台窄批全过、判据达成**

### 16.0 一句话

按 `STATE.md` §24.3 的两个前置条件一次做完：**先把第十三段的选项 D 补丁重落**（应用后 `gym_run.py` sha = `85893817760a3be5`，与批次 14 的被测版本**逐位相同**）+ **再拆掉耦合**（净 **+30 行**，都在清障路径内）；干跑 2 题 = **2/2**，正式批 **16 题 / `popup@0.70` 全部 `OK`、退出码 0、无早停**、**`popup_seen 14 / popup_dismissed 14`**（`popup_dismiss_failed` **键不存在 = 0**）⇒ 判据三条全过，**#20 按判据栏第一个分支还清**（窄批口径；边界见 16.5）。

### 16.1 改了什么（两处，都只在"清障"这条路径上）

**改动 1 = 重落第十三段选项 D 的补丁**（`git apply D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`，`--stat` = 36 insertions / 10 deletions，**一字未改地重落**）：

- hunk1：`shot_window()` 改 `results=True` + 用回包的 **client origin** 当原点（窗口 `rect` 与 client origin 实测差 **+11 / +45 px**）。
- hunk2：非 bg 鼠标分支**照抄隔壁 `if self.bg` 分支** —— 读**弹窗自己的窗口帧**（不是 app 矩形帧，后者里按钮从来不是候选）+ 点击**不带 `front_title`**（`click()` 带的 `front_title` ⇒ `mode: top` 会把 app 钉在弹窗之上）+ 收尾按"它还在不在"记 `popup_dismissed` / `popup_dismiss_failed`。
- **应用后 sha = `85893817760a3be5` = 批次 14 的被测版本**（那次跑 `popup@0.35` / 60 题 ⇒ task 21 早停、`11 / 10 / 1`）。

**改动 2 = 拆耦合**（净 +4 行，`STATE.md` §24.1-2 的那一处）：

```python
                if missed >= 2:                    # one makeup click per spot (batch 14 §14.5a)
                    continue                       # clicked twice already, still there
```

```python
                            # ... and only when it really went: `n` counts clicks, not
                            # dismissals (batch 14 §14.5③ - one miss deadlocked a task)
                            if d.window_by_title("attention") is None:
                                break
```

- (a) **同点补点一次**：同一个落点（±8 px）已经点过两次就不再当候选 ⇒ 等于允许"再点一次"，且候选来自当帧 ⇒ 补点只会落在仍立着的弹窗上。
- (c) **清掉才 `break`**：原代码 `if n: … break` 里 `n` 只表示"点了一下"，漏点也会 `break` 去 replan ⇒ 弹窗还立着、靶子什么都不判分、`tries=3` 耗尽 ⇒ **一次漏点 = 整题死锁**；现在只有 `window_by_title("attention") is None` 才 `break`。
- `git diff --shortstat` = **43 insertions(+), 13 deletions(-)** ⇒ **净 +30 行**。`STATE.md:1099` 的硬闸写的是"改动 **> 30 行** ⇒ 停手"⇒ **未触发**；**但本批如实标注：净值与阈值相等（贴线）**，且批次 13/14 用的也是"净"口径（批次 14 = 净 +26）。
- **没碰**：`gym_app.py` / `score.py` 一行未动；判定逻辑 / 匹配路径 / 阈值 / `press_guard` / `_redo` 一字未动；批次文件未动。
- 闸门：`py_compile` 通过；`score.py --selftest` = **41 checks, 0 failed**。
- **sha 轨迹**：`gym_run.py 87470aaff5593330`（HEAD）→ `85893817760a3be5`（重落补丁）→ **`3fa0e4ba4b1b9679`**（本批被测版本，**保留为定稿、未回退**）；`scripts_sha` **`186edbd9c024` → `780adce4017e`**；`gym_app.py 66632d85eac81c12` / `score.py ef066713a03eb940` 全程未动。
- **影响范围（为什么不需要回归批）**：`dismiss_interference()` 的两个调用点都在 `--chaos` 之下（`gym_run.py:2035` 的 `if self.expect_chaos:` 与等判定循环里的 `if a.chaos:`），`shot_window()` 的另外两个调用点也都在 `dismiss_interference()` 内 ⇒ **非 chaos 批的行为与改动前逐字相同**，批次 4/5/6/9/11 的鼠标成绩与可比性不受影响。

### 16.2 干跑（`--tasks 2`，鼠标通道、`--chaos 1.0 --chaos-kind popup`、`--seed 20251007`）

命令：`gym_run.py --scenario t_trap2 --tasks 2 --seed 20251007 --chaos 1.0 --chaos-ms 200,700 --chaos-kind popup --json-out D:\DSH\dsh-actor\tmp\w17-dry.json`（Windows 侧 `Start-Process -WindowStyle Normal`，日志 `D:\DSH\dsh-actor\tmp\w17_dry.log` / `.err`）。

结果：**2/2 `ok`**、退出码 0、**5252 ms / 题**、`popup_seen 2 / popup_dismissed 2`（无 `popup_dismiss_failed` 键）、`clicks 6  interferences 2  replans 2`、`scripts_sha 780adce4017e`、`score.py` 打 `v2 2/2 100.0%`。

⇒ 与批次 14 的干跑（`2/2`、`5349 ms`、`popup_seen 2 / dismissed 2`、`clicks 6`）**逐项同构**：补丁重落得对、拆耦合没有改变干净路径的行为。干跑前后 UIA 列窗只有 5 个常规窗口，无残留 'GUI Gym' / 'attention'。

### 16.3 正式批（鼠标通道、`popup@0.70`、16 题、**跑完立刻打分**）

命令（逐字）：

```
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 16 --seed 20251007 --chaos 0.70 --chaos-ms 200,700 --chaos-kind popup --max-repeat 3 --json-out t_trap2-w17-popup70-mouse.json
```

驱动输出（逐字，日志 `D:\DSH\dsh-actor\tmp\w17_A.log`）：

```
gym driver: window (316, 313, 1496, 1093)  actor port 8731  chaos 0.70
foreground before: GUI Gym (hwnd 2165372)
task  0 t_trap2   click the button labelled GAMM.                      OK      4191ms
...（16 行全 OK，3076–5269 ms）...
task 15 t_trap2   click the button labelled MICA                       OK      3403ms

score 16/16 ok  (100% of tasks)
  t_trap2   16/16
per task: 4476 ms avg  |  actor calls 0  shots 98  ocr 195  clicks 40  keys 0  drags 0
asks read off the screen: 20  from the state file: 7  (16 task(s))
disturbances: 14 fired over 16 task(s), 0 task(s) had >=1; verify calls 0, re-reads 0, give-ups 0, stale 0
foreground after:  GUI Gym (hwnd 2165372)  unchanged: True
```

`score.py` 定稿行（`w17_scoreA.txt`）：

```
chaos:popup    v2 16/16 100.0%  decided 100.0%  disturb 0   screen 10/16 replan 11    2091 ms/task  keys 0     shots 98   ocr 195
               answered_right=16
               false_refusal 0/16 (0.0%)  false_accept 0/0 (0.0%)  stale 0  wasted 0  verify_giveup 0  re-reads 0
               fired-task pass 0/0 (0.0%)  quiet 16/16 (100.0%)  swapped 15  a_hit 10  a_hit_but_failed 0  (wrong_target 0 / twin 0)
               variant prose_with_button 1/1  variant swap_after_press 10/10  variant swap_timer 5/5
               swap by variant  swap_after_press n=10 a_hit=10 wrong=0  swap_timer n=5 a_hit=0 wrong=0   race(pressed the replaced ask) 0/0
               guard gate sample 27  P50 125 ms  P95 168 ms  (criterion P50<=240, P95<=320)
```

**为什么是 0.70 而不是 §24.2 里写的 `@0.35`**：`@0.35` 在 16 题窄批里的期望弹窗数按批次 14 的 `11 / 60 题` 换算只有 **≈ 3 个 < 5** ⇒ **判据自己（`popup_seen ≥ 5`）在"窄批 + 0.35"这个组合下不可达**。0.70 是同一段里键通道两个档都跑过、批次 8 也有 `popup70` 的档位，**弹窗更多 = 漏点机会更多**，对这条通道是**更严**的检验。⚠ 代价：与批次 14 的 `@0.35` **强度与长度都不同**，所以本批**不能**读成"把那 1/11 修好了"。

### 16.4 判据（事前写在 `STATE.md` §7 #20 行与 `SCORE.md:1178`）

| 判据（原文："鼠标通道的 `popup` 批跑满题数且 `popup_dismissed == popup_seen ≥ 5`"） | 结果 |
| --- | --- |
| 跑满题数、不早停 | ✅ **16/16**、`exit_reason None`、`partial False`、`rows 16`（`task_i` 0→15 一比一） |
| `popup_seen ≥ 5` | ✅ **14** |
| `popup_dismissed == popup_seen` | ✅ **14 == 14**（`popup_dismiss_failed` 键不存在 = 0 次失败） |
| `score.py` 正常打分 | ✅ `v2 16/16 100.0%`、`decided 100%`、`false_refusal 0/16` |
| 与批次 13-B / 14 / 15 的失败面对照 | 13-B = "一次没点中"（该支当时无计数）；14 = "点中 10 次、漏 1 次 ⇒ task 21 早停"；15 = "点 0 次 + 按键 45 次全落空"；**16 = "14 次全中、0 次失败、跑满不早停"** |

**三条交叉验证**：① **`interferences == popup_seen == 14`** ⇒ 每次发现**只点了一下**（没有补点、没有重试）；② app 侧留档 **`chaos_planned 14 / chaos 14`** 与驱动侧 `popup_seen 14` **一一对应**；③ app 侧 **没有任何 `blocked` 事件**（批次 13-B 是 `blocked 10`）⇒ **没有一题被弹窗卡住**，`disturbances: 14 fired … 0 task(s) had >=1` 与 `score` 的 `disturb 0` 同源。

### 16.5 引用这批时必须带上的边界

1. **是窄批，而且只有一次**：16 题、单批、单强度（0.70）、未做重复批 ⇒ 不能与 60 题的键通道批并列成"覆盖面等同"。
2. **驱动带补丁，不是批次 4/5/6/9/11 的那一版**：`scripts_sha 780adce4017e`（`gym_run.py 3fa0e4ba4b1b9679`）；差异只在 `--chaos` 下的清障路径，**非 chaos 批逐字未变**。
3. **拆耦合本身没有被检验**：`interferences == popup_seen` ⇒ (a) 补点与 (c) 重试**一次都没触发** ⇒ 本批能证明的是"**没有引入回归、这条通道能跑满 16 题不早停**"，**不能**证明这条保险"够用或有效"（它一次都没被触发 ⇒ 本批对它**零信息量**），更不能证明"漏点已被消除"（批次 14 的 `1/11` 未复现，但 14 次样本区分不了"率降了"与"运气好"）。重落的那份补丁本身**被真实执行了 14 次、每次一发命中**，但那是它在这 14 次上的表现，不能外推（同一份补丁在批次 14 只做到 10/11）。**"漏点是否消除" = 【未决】**（见 16.6）。
4. **只覆盖非 `--bg` 的前台鼠标通道**：`--bg` 鼠标通道整条不生效（盲区 #21）不在本批范围内。
5. **占用了前台**：逐题耗时合计约 **72 s**（16 × 4476 ms 均值），全程 app 在前台（`foreground after … unchanged: True`）；跑批前后 `wait_until_unlocked()`，同一时刻只有一个 gym 窗口。
6. **本批的 `scripts_sha` 是新的**：引用时写 `批次 16（口径 v2，json `t_trap2-w17-popup70-mouse.json`，json sha256/16 `c6c41590cb5ef192`，`scripts_sha 780adce4017e`）`，并注明通道 = **前台真实鼠标（非 `--bg`）**。变化可核对：`186edbd9c024`（`gym_run.py 87470aaff5593330`，第十六段改前那一版）→ **`780adce4017e`**（`3fa0e4ba4b1b9679`，本批被测版本）。

### 16.6 这一批的封存口径（第十七段回填，2026-10-05）

- **封存结论**：「**通道可用 + 未引入回归 + 跑满不早停（窄批口径）**」。原稿里"**补丁充分**"是**过度声明** —— 那条拆耦合（16.1-2）**一次都没被触发**（`interferences == popup_seen` 可证）⇒ 本批对它**零信息量**，能说的只有"没有引入回归"；改动仍**保留为定稿**（16.5-6）。
- **【未决】漏点是否消除**：本批**不关闭**也不重开这一项。唯一入口 = **再跑 3 批（每批 16 题）共 48 题** —— 单批 16 题在统计上区分不了"率降了"与"运气好"（量化见 `REPORT.md` 附录 B-7，本段不跑）。
- **前台占用如实记**：本批逐题耗时合计 ≈ **72 s**（16 题），期间 gym 窗口**就是前台**；`foreground after … unchanged: True` 只证明"跑完时没被抢走"，**不等于"没占用"**。`STATE.md` §24.2 对 A 的"占用前台约 5–8 分钟"（§23.5 另写"代价是 3 分钟"）都是**按 60 题批**给的 —— 用本批实测 **4476 ms / 题**换算，60 题 ≈ **4.5 分钟**、**落在原估计区间内** ⇒ **原估计成立，被高估的是"单批 60 题"这个前提**（窄批 16 题 ≈ 72 s 才是省法）。

## 批次 17–19（2026-10-05 第十九段）—— 拆耦合实战：3 批 × 16 题鼠标前台窄批（`popup@0.70`）

### 17.0 一句话
第十六段留下了唯一没被检验的东西：那条"漏一次点 ⇒ 整题死锁"的拆耦合是**未被检验的保险**（`interferences == popup_seen` ⇒ 一次都没被触发）。这一段按 `HANDOFF.md` §4 写死的**唯一入口**跑了 **3 批 × 16 题 = 48 题**鼠标前台窄批，**首次让那条保险实战**：**批次 18 里它被触发了一次并救回**（`interferences 9 > popup_seen 8`、该遭遇最终被清掉、该批 16/16）；三批合计 **0/28 遭遇死锁** ⇒ 死锁率 95% 单侧上限 ≈ **10.7%**（rule of three）。**代码一行未改**（`gym_run.py` 仍 `3fa0e4ba4b1b9679`、`scripts_sha 780adce4017e`）。

### 17.1 这三批要回答的问题与判别式（跑之前写死）
- 问题不是"清障率"，而是**那条补点/拆耦合有没有被真实触发、触发后有没有救回**。用户点出的关键：**复现漏点 ≠ 补丁被检验**。
- 判别式（全部用现有计数器，不需要改代码）：`popup_seen` 每次"发出过点击的调用"+1、`interferences` 每次点击+1（`gym_run.py:966–1008`）⇒ **补点触发 ⇔ `interferences > popup_seen`**；**同一弹窗跨调用重试/存活 ⇔ `popup_seen > app 侧 chaos 数` 或 `popup_dismiss_failed > 0`**；**救回 ⇔ 该题最终 `OK` + 批不早停 + app 侧无 `blocked`**。
- **反过来，(ii) 情形（漏点后弹窗直接消失、补丁仍未触发）在这些计数器下不可观测** —— 它与"干净单发命中"逐字段相同 ⇒ 只能归入"未触发/未受检验"，不能声称补丁被检验。

### 17.2 跑之前先踩到的三条环境坑（下次按这个顺序核）
1. **靶窗口按 UIA `name` 的子串计数**：`gym_run.py:3135–3150 def target_windows(a, title="GUI Gym")` 用 `title.lower() in name.lower()`，而 `gym_run.py:3364–3370` 要求**恰好 1 个**，否则 `refusing to drive: %d practice target window(s) on screen - want exactly 1`（退出码 2）。本机 DSH 的会话窗口标题里就含 "GUI Gym" ⇒ 1 真靶 + 1 我的窗口 = 2 ⇒ 拒启动。处置：跑批前把该窗口标题临时改名（原名存 `D:\DSH\dsh-actor\tmp\w18_harness_title.txt`），**跑完必须还原**（本次三批后已还原成功）。
2. 被拒的那一次**会留下残留靶窗口**（启动器 python 与 app 是两个进程，驱动只 kill 启动器 pid）⇒ 下一批的 `foreground before` 会变成 `attention`；跑前确认无残留。
3. 三批**只能串行**，每批**占用前台 ≈ 70 s**；跑批前先 `act.py ping`（actor 守护）。

### 17.3 逐批结果
命令 = `gym_run.py --scenario t_trap2 --tasks 16 --seed <20251008|20251009|20251010> --chaos 0.70 --chaos-ms 200,700 --chaos-kind popup --max-repeat 3 --json-out t_trap2-w18-popup70-mouse-r<1|2|3>.json`（Windows 侧 `-WindowStyle Normal`）；日志 `D:\DSH\dsh-actor\tmp\w18_r*.log` / `w18_r*.err`，打分输出 `w18_score_r*.txt`。

| 批次 | seed | 退出码 / 题数 | 驱动遭遇（`popup_seen`） | 清障点击（`interferences`） | **补点** | `failed` | app 侧 `chaos` | `blocked` | `score.py` |
|---|---|---|---|---|---|---|---|---|---|
| 17 | 20251008 | 0 / **16/16** | 10 | 10 | **0** | 0 | 10 | **1**（task 12，该题仍 `ok`） | `v2 16/16 100.0%` |
| 18 | 20251009 | 0 / **16/16** | 8 | **9** | **1 ★** | 0 | 8 | 0 | `v2 16/16 100.0%` |
| 19 | 20251010 | **1** / 15/16 | 10 | 10 | 0 | 0 | 10 | 0 | `v2 15/16 93.8%`（`wrong_target 1` = task 14，`swap_timer` 类、`race 1/1`） |
| **合计** | —— | —— | **28** | **29** | **1** | **0** | **28** | **1** | **47/48** |

- 三批 `scripts_sha` 全 = `780adce4017e`、`gates v2`、`partial False`、`exit_reason None`（都跑满 16 题、**无早停**）。
- 驱动逐题耗时均值 4639 / 4418 / 4667 ms（`score.py` 口径 1979 / 2191 / 2144 ms/task）；`shots` 94/88/94、`ocr` 197/185/197、`clicks` 37/35/36。
- app 侧**触发弹窗数 = `chaos` 事件数**（不是 `chaos_planned`）：10 / 8 / 10，与驱动侧 `popup_seen` **逐批 1:1 相等**。
- 留档 sha256/16：json `987c90db02ade387` / `ad655a1b3210d218` / `e44222614893713a`；state `211aae967a92a50a` / `e63c98f4eaeb57e6` / `4eb532b6aa4f9074`；events `d39b884685742cfc` / `5e497f046d9ed8d1` / `21b064f112d55692`。

### 17.4 判据分派（按跑前写死的三档）
- **(i) 补点触发且救回 = 成立（批次 18）**：`interferences 9 > popup_seen 8` ⇒ 恰有一次遭遇里点了两发（第一发没打掉、循环重取帧后再点一发），该遭遇最终 `popup_dismissed`（`failed 0`）、该批 16/16、不早停、无 `blocked` ⇒ **第十六段那条"未被检验的保险"在这一次上是有效的**（状态从"一次都没被触发"变成"被触发过一次且救回"）。
- **(ii) 漏点后弹窗直接消失 ⇒ 在本批计数器下不可观测**（见 17.1 末条）。
- **反例（补点后仍清不掉）= 未出现**：三批 `popup_dismiss_failed` 全 0、app 侧无"题被弹窗卡住"的记录。
- **逐题定位不可用**：run json 的逐题行在 `j['runs']`（不是 `j['rows']`），行内 `interferences` 三批全为 0（既有 `_redo()` 记账特性）⇒ 只能给**批级**"补点 1 次"，给不出"哪一题"。

### 17.5 率与上限（口径写死）
- **死锁率 0/28 遭遇** ⇒ rule of three：95% 单侧上限 ≈ **3/28 = 10.7%** —— **不能说"漏点已消除"**。
- **第一发失手率 1/28 = 3.6%**（本次观测），与批次 14 的 `1/11 ≈ 9%` 同量级 ⇒ 两次观测都不足以把率钉死。
- **"漏点是否消除" 仍 =【未决】**：本段把它的入口从"3 批 48 题"推进到"**已跑 3 批 48 题**"，但 16 题 × 3 在统计上仍宽。

### 17.6 引用这三批时必须带上的边界
1. **只覆盖前台真实鼠标通道**（非 `--bg`）：`--bg` 鼠标通道整条不生效（盲区 21）、滚轮/拖拽的连续鼠标交互仍未覆盖（#18 结论不变）。
2. **驱动与批次 16 同一版**：`scripts_sha 780adce4017e`、`gym_run.py 3fa0e4ba4b1b9679`（与批次 4/5/6/9/11 不是同一版；差异只在 `--chaos` 下的清障路径）。
3. **三批 seed 各异**（20251008/09/10）⇒ 是**同协议的三次重复**，**不能**与 60 题键通道批并列成"覆盖面等同"。
4. **题级成绩 47/48**：批次 19 的 task 14 是**已知的 `swap_timer` 时序竞争类**（`race 1/1`），与弹窗通道无关 —— **不要**把 15/16 读成"清障退化"。
5. **批次 17 有 1 次 app 侧 `blocked`**（task 12，`swap_timer`，该题最终 `ok`）：**不要**读成"通道失败"，批次 18/19 未再出现。
6. **占用前台**：每批 ≈ 70 s（16 题）、三批合计 ≈ 3.6 分钟；跑批前必须确认**靶窗口计数 = 1**（见 17.2）。
7. **"补丁/保险有效"的适用范围**：只在这 1 次触发（批次 18）上成立；**不能**外推成"任何情况下都够"（批次 14 拿同一份补丁只做到 10/11），也**不能**用它关闭"漏点是否消除"。
