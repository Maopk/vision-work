# 交接页：GUI Gym 判分线（批次 1–11）

一句话结论：**在受控靶子上，驱动的"看屏-决定-按键"闭环已经有可复现的数字和可引用的口径**；
批次 1–5 的结论（五判定口径、`fill` 边界、swap 救回路径、`file` 源跳守门的取证）**不受批次 6 影响**。
批次 6 只做两件收口：**同词双现（twin）从 0/8 修到 8/8**（按"被绘制块里的那次出现"选目标）、
**race 首次拿到分母 5/5**（靶子加 `swap_race_timer` + 驱动加 `--press-jitter`，把换题窗口挪到守门抓帧之后）。
批次 7–8 是**收尾批**：①欠账 #14 落地——每批 app 的 state/events 按 `--json-out` 命名留档，事后可复核（**只改命名、不改任何判定**）；
②chaos 扩到**四类**（`rebuild` 批次 6；`move`/`slow`/`popup` 批次 7–8，全部标「**探索性·不并入定稿**」）；
③批次 7 `move` 批暴露的守门假阳性（**读不出的重读被当成"问题变了"**）已定位并修（批次 8，见 §4 第 14 条）。
批次 9–10 各还一条欠账、**判定逻辑都不动**：批次 9 只把守门的计时点从"含抓帧"改成"扣掉抓帧"（#10）并把逐题 jitter 补齐（#11）；
批次 10 只把守门的**重读框**从"进题时冻结"改成"**每帧用像素段重算**"（#4 = `STATE.md` §7 #15）——`ask_read_unreadable` 在 `move@0.70` 由 **2 → 0**，
`move` 线成绩 `58/60 → 59/60`（同协议同 seed），成本 `+8.71 ms/门`（见 §4 第 14 条与 `../sol/sandbox/SCORE.md` 批次 10 节）。
批次 11 还掉 **#17（`shot` 空帧零容忍）**：抓帧失败不再让整批退出——重试 3 次（间隔 0.2 s、恢复链原样）+ 仍失败就把**已完成的题写成 partial run json**
（新键 `partial` / `exit_reason` / `tasks_planned`，退出码 **3**），**判定路径一字未动**；同协议同 seed 的 48 题回归批 `35/48`（批次 9 = 36/48，唯一翻转 `task_i 38` 属竞态族抖动）、
**核心 14 = 12/14、翻转 0**、`ms/题 +0.9%`、`shot_empty / shot_retry = 0 / 0`（见 §4 第 18 条与 `../sol/sandbox/SCORE.md` 批次 11 节）。

## 1. 三件套在哪

| 角色 | 文件 | 说明 |
|---|---|---|
| 靶子 | `../sol/sandbox/gym_app.py` | Tk 练习靶，自己生成题表、写 `gym-state.json`、按 `truth` 判分 |
| 驱动 | `../sol/sandbox/gym_run.py` | 抓帧 → OCR → 决定 → 按键/点击；**从不读 `truth`** |
| 计分 | `../sol/sandbox/score.py` | 跑完**之后**把 `truth` 与运行 json 连接，输出五判定 |

## 2. 口径（引用任何数字之前先读这一节）

- **v0**：靶子自己的 `result == ok`，分母 = 跑完的题。批次 0 及更早（`mix6x*`、`chaos-*`、`keys-mix*`、
  `t_chips`/`t_rows`/`t_form`）、`t_trap2-1`/`-2`、`prof2` 是 v0。**与 v1 不可比。**
- **v1**：五判定 + 声明分母（`answerable`/`must_refuse`），**批次 1–4 全部是 v1**，跨批可比。
- **v2**：v1 定义不变，只把 `a_hit_but_failed` 拆成 `_wrong_target` / `_twin`；批次 5。
- **v3**：v2 定义不变，race 的 variant 集合纳入 `swap_race_timer` 并拆出 `race_press_after_guard`
  （"守门抓帧**之后**才发生的过期按压"），新增守门逐门样本分位 `gate_samples`/`gate_p50`/`gate_p95`；**批次 6 起**。
- 口径版本是**计分工具的属性**，不是 json 自带属性：新列会**回填**到老 json（同一份 `t_trap4-1.json`
  用批次 4 的工具读是"8 例"，用带拆分的工具回读是"9 例 = 1 wrong_target + 8 twin"）。
  引用时写清"哪个 json + 哪版 `score.py`"。
- 各批 `scripts_sha` 全表在 `../sol/sandbox/SCORE.md` 的「口径版本与可比性（终版）」一节。

**引用规则（用户审计定死）**：

1. `race` / `guard-blind` 必须带**分母**（分母 = 本批真正按了过期 ask 的次数，不是题数）；分母 < 5 标"非缓解"。
2. synonym **鼠标**通道成绩一律不引用；有效成绩 = 键通道 `synonym_button 6/6` + `synonym_only 4/4`。
3. `no_badge_fill` 的 0.50 档 D1 = 57（阈值带 66–69 是空的）。
4. 折叠表 `_code` 只用于**找目标**，判变化一律用 `_plain`。
5. json 里的 `gates` 是**计分算法版本**（按场景名分流：`t_trap5→v3`、`t_trap*→v2`），**代码版本看 `scripts_sha`**
   ——批次 6 的 `t_trap2` chaos 三批打的是 `v2` 标签，但代码是批次 6 的（`ee68f457577d`）。
6. 驱动的 `disturbances: N fired` **只数弹窗型**干扰（`dismiss_interference`）；`rebuild` 型不进这个计数。
   **chaos 注入率一律引用 app 侧 `gym-events.jsonl` 的 `chaos_planned` / `chaos` 事件。**
7. run json 的 `events` 字段是**路径**，而 `score.py` 就是按它读真值的（`join_truth`，`score.py:162-169`），app 每次启动又覆盖写同一文件
   ⇒ 只有**最后一批**能联对；**事后重打任何"非最后一批"都会静默错联**（实测：跑完 chaos 0.70 再打 `t_trap5-1.json` 得 `36/48`、`MISMATCH 11`，真值是 `37/48`、`MISMATCH 0`）。
   已公布数字**全部是跑完立刻打分的**；事后复核必须 `score.py <json> --events <该批留档副本>`（每批留档是欠账 STATE §7 #14）。
8. **partial 批（退出码 3）的成绩不与完整批并列**：`gym_run.py` 从批次 11 起在 `--json-out` 里写 `partial: true` / `exit_reason` / `tasks_planned`，`score.py` 会打两行 `!! PARTIAL RUN` 警示
   —— 这类批只用来证明"靶子中途没了也能落盘可打分"，**不作为成绩引用**（两条构造产物 `t_trap7-empty6.json` / `t_trap7-minim6.json` 就是这一类）。
9. **鼠标前台窄批（批次 16 单批；批次 17–19 = 同协议三重复、三个 seed）引用时必须带四条**：① 通道 = **前台真实鼠标（非 `--bg`）**；② 口径 = **窄批**（单批、单档，**不与 60 题的键通道批并列**成"覆盖面等同"）；③ **拆耦合** = 批次 16 里**一次都没被触发**（"未受检验"，那批只支持"通道可用 + 未引入回归"）、批次 17–19 里**被触发一次且成功**（批次 18：`interferences > popup_seen`，该遭遇被清掉、该批跑满）⇒ 口径写"**路径可达 + 单次有效**"，**不写**"保险有效 / 够用"；④ **"漏点是否消除" = 【未决】且已判定"不追加"**（再加 3 批只能把 95% 单侧上限从 ≈10.7% 收窄到与观测失手率同一量级 ⇒ 与"已消除"仍分不开、**边际收益 ≈ 0**）；将来真要证消除的唯一入口 = 再跑 **3 批 48 题**（**非当前计划**，量化见 `REPORT.md` 附录 B-7/B-8）—— 见 §4 盲区 23 末尾的**收口块**与 §6 末行。

10. **鼠标前台通道的 `t_trap2` 批：旧驱动（`3fa0e4ba4b1b9679` 及之前）必早停；`d8594bff3738ca9b` 起已修**（第二十三段判定 → 第二十六段 B 实施，欠账 `STATE.md` §7 **#21**）：徽章判定族的 `must_refuse` 题在**旧**驱动的鼠标通道下会被点在 **prose 坐标**上（`gym_run.py:2164-2168` 缺键分支 `:2160 if self.keys:` 的可操作性判据）⇒ 题不前进、`--max-repeat` 早停、`score.py` 记 **`false_accept`**。**引用旧批（如批次 14、批次 20）必须同时说「该批未跑满、早停由 #21 触发、与 `popup` 通道无关」**；新驱动（`d8594bff3738ca9b`，净 +9 行）的批次 21/22 已跑满（24/24、60/60），**不再需要这条注解**。**残留风险**：修复把「点偏」也记成拒答（表现 = `false_refusal`）⇒ 见到上升时按 `DESIGN-21` §6/§8 **逐题人工抽查**（本段两批均为 0）。

## 3. 重跑命令（一行可复制）

```powershell
cd D:\DSH\vision-work\sol\sandbox
# 先确认 actor 守护进程活着（不在就自动拉起，端口 8731）—— 没有它任何一批都跑不起来
D:\DSH\.venvs\vision-ci\Scripts\python.exe D:\DSH\dsh-vision-kit\actor\act.py ping
# 批次 6 定稿（鼠标通道、抢前台，48 题约 4 分钟，会占用你的指针）
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out t_trap5-1.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap5-1.json
# 批次 9（鼠标通道 48 题，约 4 分钟；只动了守门计时点与逐题记账，判定逻辑与批次 6 相同）
#   ⚠ 必须从 Windows 侧启动、显式正常显示状态：从 WSL 后台作业启动会让 app 窗口起在 -32000（离屏）
#     ⇒ 帧全空 ⇒ 0 次按压 ⇒ `gym_run.py:508 raise SystemExit("shot failed")`，且不写 run json（白跑一次）
#   ⚠ 起正式批前先干跑 2 题（把 --tasks 48 换成 2、--json-out 换临时名）确认首题有真按压
Start-Process -FilePath D:\DSH\.venvs\vision-ci\Scripts\python.exe -WindowStyle Normal -WorkingDirectory D:\DSH\vision-work\sol\sandbox -ArgumentList "D:\DSH\vision-work\sol\sandbox\gym_run.py","--scenario","t_trap5","--tasks","48","--seed","20251007","--press-jitter","0,1200","--max-repeat","3","--json-out","t_trap6-1.json"
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap6-1.json
# 批次 5（鼠标通道，38 题）+ 计分自检
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap4 --tasks 38 --seed 20251007 --max-repeat 3 --json-out t_trap4-4.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap4-4.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py --selftest
# chaos（键通道 + --bg，不抢前台；rebuild 型）
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --max-repeat 3 --json-out t_trap2-w6c-control.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind rebuild --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out t_trap2-w6c-chaos70.json
# 批次 7（键通道 + --bg）：同上的控制批，加 move 类干扰；--json-out 现在会自动给 app 的 state/events 命名
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --max-repeat 3 --json-out t_trap2-w7-control.json
# ⚠ 下面这行是"修复前"的批（33/60 早退），只用于定位根因，**不可引用为 move 类定稿**
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind move --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out t_trap2-w7-move70.json
# 批次 8（**move 类定稿**；chaos 四类 × 2 强度全部同一行只换 --chaos-kind 与 --chaos）
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --json-out t_trap2-w8-move70.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap2-w8-move70.json
#   --chaos-kind ∈ {rebuild, move, slow, popup}；--chaos ∈ {0.35, 0.70}；每批跑完立刻打分（app 会覆盖写自己的 events）
# 批次 10（**现在的 `move` 类定稿**：只把守门重读框改成每帧重算，指纹/匹配/阈值/分支都没动）
#   ⇒ 与批次 8 逐项同协议、可逐题对照；跑完立刻打分，自带 -state.json / -events.jsonl
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out t_trap2-w9-move70.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap2-w9-move70.json
#   ⚠ 批次 10 首跑就是这么死的：一次空位图 ⇒ 整批退出 + 不写 run json（新欠账 #17 / STATE §14.8）
# 批次 11（**现在的抓帧失败处理 = 定稿**：重试 3 次 + partial 落盘 + 退出码 3；判定逻辑一字未动）
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out t_trap7-1.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap7-1.json
#   ⚠ 退出码：0 = 完整批；1 = 一题都没完成（不写 json）；3 = **partial**（靶子中途没了 ⇒ json 带 `partial: true` + `exit_reason`）
#   ⚠ partial 批的成绩**不与完整批并列**（引用规则 §2 第 8 条）；空帧构造手法与两条产物见 ../sol/sandbox/SCORE.md 批次 11 节 ③
#   ⚠ `--max-repeat N` 同时是"连续 N 题 task_i 没前进就早停"的阈值：N=1 会让**第一题就早停**（提示语 `stopping early: task 0 failed 1 times` 有误导性，实测题本身是 OK 的）
# 批次 16（**`popup` 类·鼠标通道定稿（窄批口径）**：重落第十三段选项 D 补丁 + 拆"漏一次点 ⇒ 整题死锁"耦合；`gym_run.py` = `3fa0e4ba4b1b9679`）
#   ⚠ 只跑 16 题、单批单档；跑前跑后都要确认只有一个 gym 窗口（驱动要求 == 1）；会占用前台 ≈ 72 s
#   ⚠ 必须从 Windows 侧启动、显式 -WindowStyle Normal（同批次 9 的两条 ⚠）
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 16 --seed 20251007 --chaos 0.70 --chaos-ms 200,700 --chaos-kind popup --max-repeat 3 --json-out t_trap2-w17-popup70-mouse.json
D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py t_trap2-w17-popup70-mouse.json
#   ⚠ 用 0.70 而不是 0.35：0.35 档在 16 题窄批里期望弹窗数 ≈3 < 5 ⇒ 判据 `popup_seen >= 5` 在那个组合下不可达
#   ⚠ 判据三条：跑满 16 题不早停 且 `popup_seen >= 5` 且 `popup_dismissed == popup_seen`（三项全过 = 还清 #20）
```

- 鼠标通道与批次 4/5/6 可比；`--keys --bg` 与它们**不可比**（通道不同），只用于 chaos 对照。
- **同一时刻只能有一个 gym 窗口**（驱动要求 `target_windows(...) == 1`）⇒ 所有批次**串行**。
- PATH 里的 `python` 是 `C:\Python314`（没有 numpy/PIL），必须用 venv 里的那个。
- **批次 7 起**：给了 `--json-out x.json` 时，app 的 state/events 自动写成 `x-state.json` / `x-events.jsonl`
  （留档、可事后 `score.py x.json` 复核）；不给 `--json-out` 时仍是 `gym-state.json` / `gym-events.jsonl` 老默认名。
- **批次 17–19（第十九段：拆耦合实战，三批串行）**：
  `gym_run.py --scenario t_trap2 --tasks 16 --seed <20251008|20251009|20251010> --chaos 0.70 --chaos-ms 200,700 --chaos-kind popup --max-repeat 3 --json-out t_trap2-w18-popup70-mouse-r<1|2|3>.json` + `score.py <同名>`；
  每批 ≈ 70 s 前台、**必须串行**；判据**不看通过率**，看 **`interferences > popup_seen`（补点被触发）+ 该题仍 `OK` + 批不早停 + app 侧无 `blocked`**。
- **跑任何前台批之前先核"靶窗口计数 = 1"**：驱动按 UIA `name` **子串**匹配 `"GUI Gym"`（`gym_run.py:3135–3150` 计数、`:3364–3370` 要求恰好 1 个），而**本机 DSH 的会话窗口标题里就含这四个字符** ⇒ 会数成 2 个靶而拒启动（`refusing to drive: 2 practice target window(s) …`、退出码 2）。处置 = 临时改名该窗口（原名存 `D:\DSH\dsh-actor\tmp\w18_harness_title.txt`）、**跑完还原**；**被拒的那一次还会留下残留靶窗口**（驱动只 kill 启动器 pid），下一批跑前先确认没有。

## 4. 已知盲区（引用结论时必须一起带上）

1. **同词双现（`swap_twin_press`）**：驱动侧**已修**（批次 6：8/8 转 ok，靠"被绘制块里的那次出现"选目标，
   `ask_word_from=painted`）。靶子侧的标题仍绑 `<Button-1>` ⇒ **点到标题仍判错**（设计使然）：
   任何"按 OCR 顺序取首个出现"的实现都会 0/8。
2. **`GAMMA`/`GAMMB` 实测可混淆对**：驱动多次把 B 读成 A（2x 与 4x 都错），与折叠表无关；
   批次 6 的 t4 仍把 banner 读成 `GAMMI`，但靠 painted 选目标仍答对。
3. **单字形改写的桶指纹不可靠**：`band_sig`（32×4 灰格）对单字形改写给出 `ask_cells = 0` 或 `1`，
   都低于 `ask_changed` 的 3 格阈值 ⇒ 指纹单独**不足以**发现这一家族的换题，必须靠文本重读。
4. **`nb046`/`nb050`（fade 档）全拒答**：批次 6 仍是 0/3 + 0/3（题面被淡到读不出徽章）。
5. **`swap_after_press` 每题约 5 s 空等**：判定不会来（题已换），要等满 `verdict_ms` 才重规划（未优化）。
6. **race 只在批次 6 的新题族上拿到分母**：`swap_race_timer` 10 题里 5 次过期按压（5/5 全错）。
   批次 1–5 的老题族 `swap_timer`（600–1000 ms 定时）**机制上落在守门抓帧之前** ⇒ 只能是 `0/0`，
   **不能解读成"没有按过期 ask"**（这是我上一轮口径里的一处更正）。
7. **`guard-blind` 批次 5/6 都不打印**（打印条件是 `blind_seen`）⇒ 这两批没有可引用的 guard-blind 分母。
   **2026-10-05 第六段已量 ⇒ 关闭**：批量 `--keys --bg` 20 题 `t_trap5`（`w12-trap5-keys20.json`）⇒ `blind_seen = 0`、events `trap_stale_press = 0`、
   `swap_hard_timer` 5/5 全 ok，且 `task_i 13` 在指纹 `ask_cells 0` 时仍被**文本重读**（raw `_plain` 比较）抓住 ⇒ 单字形换题**结构性不漏判**，这一条不再是盲区（证据在 `STATE.md` §17）。
8. **chaos 的两个计数不可互推**：app 侧确实注入了（同一组设置跑两遍各有自己的数：`w6b` 那遍 `chaos_planned 51` / `chaos 51`、
   `w6c` 那遍 `chaos_planned 50` / `chaos 50`，都是 `rebuild`；差 1 ≈ 2% 的运行间波动，不是矛盾），
   而驱动的 `disturbances: 0 fired` 只数**被弹窗挡住**的次数。注入率引用 **app 侧事件文件**。
   另：`--chaos-ms 200,700`（驱动默认）决定干扰几乎总落在驱动读题**之前**，所以它测的是"重读恢复"而不是"过期按压"。
   另：**chaos 0.35 档没有 `score.py` 数字**（只有驱动 59/60）——首轮 `w6b` 三批共用一个 events 文件，
   后两批把它覆盖了；要 `score.py` 数字就得复跑（`w6c` 只复跑了控制与 0.70）。
9. **`gate_ms` 含抓帧**：`t_gate` 在 `self.shot()` 之前 ⇒ 鼠标批 P50 366 ms 里有 219 ms 是抓帧，
   扣帧后 ≈147 ms（与独立的 `ms_askgate/ask_gates = 148.1` 一致）。下一批把 `t_gate` 移到 `shot()` 之后（欠账）。
10. **`press_delay_ms` 没有进逐题行**（只进了 `stats` 聚合）⇒ 逐题的 jitter 时长无法核对（欠账）。
11. **run json 的 `events` 字段是路径**，而 `score.py` 就是按它读真值的（`join_truth`，`score.py:162-169`）
    ⇒ 事后重打"非最后一批"会**静默错联**（实测：跑完 chaos 0.70 再打 `t_trap5-1.json` 得 `36/48`、`MISMATCH 11`，
    真值 `37/48`、`MISMATCH 0`）。**批次 7 起已修**：驱动按 `--json-out` 给 app 的 state/events 命名
    （`x.json` → `x-state.json` + `x-events.jsonl`）⇒ 每批留档、可事后 `score.py <json>` 复核；
    不带 `--json-out` 时仍是老默认名。**批次 1–6 的旧文件不可事后复核**（数字都是跑完立刻打的，仍然有效）。
12. **批次 3 的 `t_trap3-1.json`（sha `785cfe9412d6`）任何数字都不引用**（鼠标通道那次前台被抢占）。
13. **`no_badge_fill` 的标定用的是合成帧**（`T_VIS=68`），与真实 0.50 档对不上（未重标定）。
14. **`move` 干扰下"计划时记录的 `ask_box`"会失效**（批次 7 定位）：整窗移动 / body 加 padding 后，守门按老框重读会读回一段**干净的句子前缀**（`"DO: click the button labelled"`，边缘切在 label 之前），旧代码把这种"读不到"当成"问题变了"⇒ 不按、重规划、死锁（task 31 `none` × 3 ⇒ 33/60 早停）。
    **批次 8 已修**：读不出 ⇒ 交给指纹判；并加通用退化规则（重读与 `want` **不含任何连续 ≥2 字符子串** ⇒ 判没读到，回落指纹），计数 `ask_read_unreadable`。
    **批次 10 已还**：新增 `ask_box_now()` —— 守门**每一帧都用像素段重算** banner box（不跑 OCR，≈3.6–4.1 ms），**重算优先、失败退回冻结框**；框来源变了，但指纹基线（`ask_cells`/`ask_delta`）、匹配路径、阈值、`press_guard` 分支结构**一字未动**。
    实测（`move@0.70`，协议与批次 8 逐项相同、同 seed `20251007`）：`ask_read_unreadable` **2 → 0**、`ask_box_recomputed 124 == ask_gates 124`（每门都重算）、同 `task_i` **无 ok→非 ok 翻转**、`gate_ms` P50 124 → **139 ms**（+15 ≤ 30 判据内）、成本口径 `ms_askgate/ask_gates` **136.30 → 145.01**（+8.71 ms/门）。
    ⚠ **基线只有 2 次事件** ⇒ 样本量本身不足以证明因果；旁证是 `task_i 31` 的三代对照（批次 7 `none`×3 → 批次 8 `ok` 但读不出 2 次 → 批次 10 `ok`、读不出 0、重算 2 次）。
    ⚠ 新增字段 `ask_box_shift_px` **只记每题"首次"重算**（46 行全 `[0,0]`）⇒ **证明不了"门时那一帧被移过"**（见下文盲区 19）。
    欠账 **§7 #15 已还**；证据在 `../sol/sandbox/SCORE.md`「批次 10 结果」+ `STATE.md` §14（假设/证伪/判据/结果/作废尝试）。
15. **`a_hit` 不是独立指标**：它是"守门假阳性把首次按压推过 8 s 安全换题线"的**读出量**（`gym_app.py:1414`）。
    实测批次 7 `move@0.70`：`a_hit=False` 恰 6 题、墙钟 10.65–10.88 s；`a_hit=True` 四题 4.35–4.61 s；控制批十题全 True、6.62–6.97 s（离 8 s 只有 1.0–1.4 s）。
    所以 `a_hit` 下降**不等于**按错（那批 `wrong=0`、`swap_after_press 10/10`）。
16. **chaos 的数字一律标「探索性·不并入定稿」**（用户 m09343）：四类、每类 2 强度 × ≥5 fire；注入率引用**每批自己的** `*-events.jsonl`（`chaos_planned` / `chaos`，批次 7 起才有留档）；驱动的 `disturbances: N fired` 只数弹窗型，两者不可互推。
17. **`popup` 类干扰当前测不了**（批次 8 实测）：弹窗（Tk `Toplevel`，标题 `"attention"`，`gym_app.py:616-655`）在 `--keys --bg` 下**打不掉**——`dismiss_interference` 只按窗口标题找 `"attention"`，UIA 枚举没找到 ⇒ 弹窗留屏 ⇒ 驱动的按键被它吃掉（`dec=acted` 但靶子 `result=none`）⇒ 该题永不结束、靶子也不推进 ⇒ 两档各只 fire **1** 次后早停（4/7、1/4）。
    **这是驱动的能力缺口，不是脚本 bug**；修法见 `STATE.md` §7 #16（鼠标通道已有视觉路径 `_button_candidates(img2,"DISMISS")`，键通道没有）。**该类的数字任何情况下都不引用。**
    ⚠ **2026-10-05 第十段更正 + 已还（批次 12）**：真正根因**不是"UIA 枚举看不见弹窗"**，而是 **actor 折叠把 `data.windows` 截断**（`actor.py:_slim()` 对 list 只留前 ~6 项）而 `window_by_title()` **只读 `data`**（同一条回包的 inline 字段里一直有 `attention`，11 项）⇒ 闸门恒 `None` ⇒ **一次 Return 都没发**。改法 = `window_by_title()` / `target_windows()` 改 **inline 优先** + 清障三计数（`popup_seen` / `popup_dismissed` / `popup_dismiss_failed`）+ 清掉弹窗后**立刻 break 重答**（`gym_run.py` `105cf6cb679eea10` → **`87470aaff559`**，+24/−4 行，判定路径一字未动）。
    批次 12 实测 `popup_seen 24 / popup_dismissed 24 / failed 0`、60/60 无早停（`../sol/sandbox/SCORE.md` 批次 12 节 + `STATE.md` §18）。**批次 7/8 的 `popup` 两档成绩仍不可引用**（那是缺陷产物）；原判断的另一半**仍然成立**：`--keys --bg` 下**不能**借鼠标视觉路径（弹窗是独立 HWND、不在主窗帧里；且 `--bg` 鼠标点击整条失效，见盲区 21 与 `STATE.md` §16）。
    ⚠ **2026-10-05 第十一段补测（欠账 #19 的覆盖面）**：**键通道的第二个强度档也成立**（`../sol/sandbox/t_trap2-w13-popup70.json`：`popup_seen/dismissed = 45/45`、`popup_dismiss_failed` 键不存在、60 题无早停、`scripts_sha 186edbd9c024`）⇒ 键通道的可测性不再只是"一个档位"。但**鼠标通道（前台）仍然打不掉**（`../sol/sandbox/t_trap5-w13-popup35.json`：3 题后早停、退出码 1、驱动 `disturbances: 0 fired`、app 侧 `event blocked by modal`、`blocked 10`）⇒ 记为**新欠账 #20**（该分支没有 `popup_*` 计数，且候选走默认 veto）；不要再把"鼠标视觉路径"当成现成修法。见 `../sol/sandbox/SCORE.md` 批次 13 节 + `STATE.md` §19。
    ⚠ **2026-10-05 第二十二段（1a）：#19 的依赖先更正** —— 本条与批次 13 的边界（`../sol/sandbox/SCORE.md` 13.4 第 3 条）原按「#19 的剩余部分与 #20 **合并处理**」记账，并曾设想「若 #20 选 C 则随它收口」。**两句都已过时**：#20 的最终结论**不是**"选 C 接受边界"，而是**通道可用**（第十六段判据达成 + 第十九段保险单实例验证；#20 已收口，见 §2 规则 9、§4 末尾收口块、`STATE.md` §28.3）⇒ **#19 对 #20 的依赖解除，#19 独立走关死路径**。覆盖面按「强度档 × 通道」四格清点：`0.35` 键 ✅（批次 12）、`0.70` 键 ✅（批次 13 第一批）、`0.70` 鼠标 ✅（批次 16 + 17–19）；**唯一空格 = `0.35` 鼠标**（第二十二段 1b 跑前台窄批补齐，数值见 `../sol/sandbox/SCORE.md` 批次 20 节）。四格表与诚实边界见 `STATE.md` §19.7。
>
> ⚠ **同段 1b/1c（结果）：第四格已跑（批次 20）——「弹窗侧达标、批次未跑满」。** `popup@0.35` × 前台真鼠标（`../sol/sandbox/t_trap2-w22-popup35-mouse.json`）：fire **10**（≥5）、`popup_seen/dismissed 10/10`、`failed` 0、**补点 1 次**、`task_i 17` 被 modal 挡住 2.18 s 后恢复；但**该批 21/24 早停**（退出码 1）—— 早停的 `task_i 21` 是 `must_refuse`（`prose_only`）题，驱动**没有走拒答、反而按了标签**（`score.py false_accept 1/1`），同 seed 键通道批次 12 的同一题 `refused: true` ⇒ **与弹窗通道无关**，另记 `STATE.md` §7 **#21**。⇒ **#19 在弹窗维度四格齐 =【关死】**，判据随之改写为「每格 ≥5 fire 且清障成对」（「跑满不早停」只对键通道两格成立）。数值见 `../sol/sandbox/SCORE.md` 批次 20 节。**#18 的实现前核查结论 → `DESIGN-18-scroll-drag.md` §8（推荐方案①、零代码改动）。**
18. **`shot` 空帧原本零容忍**（批次 10 首跑实测）：一次 `PrintWindow` 返回**空位图**（stderr 原文 `shot failed: … "error": "ValueError: cannot write empty image"`）⇒ `gym_run.py:508 raise SystemExit`（当时设计如此）⇒ **整批退出 + 不写 run json + 逐题行全丢**。
    触发点是 `move` 干扰命中的那一瞬（死前最后三条 app 事件 = `ready` / `chaos_planned` / `chaos`；app 自报 `layout.origin [312,267]`，**不是批次 9 那种离屏 `-32000`**）。残留的两个 app 进程会**活着但没有窗口**（UIA 顶层窗口表里 `GUI Gym` = 0）⇒ 必须 `Stop-Process -Force` 清掉再重跑。
    **批次 11 已还**（`STATE.md` §7 #17）：`ShotFailed` 异常类型（4 处 `raise SystemExit` 改掉、消息原文不变）+ `_shot` 重试 3 次（间隔 0.2 s，恢复链原样）+ main `try` 包住题目循环 ⇒ **已完成的题写成 partial run json**（`partial` / `exit_reason` / `tasks_planned`，退出码 **3**）；判定路径一字未动。
    实测：kill 靶子 ⇒ `t_trap7-empty6.json`（`runs 1`、`exit_reason="window 'GUI Gym' not found - is the app running?"`、退出码 3）；`ShowWindow(SW_MINIMIZE)` ⇒ `t_trap7-minim6.json`（`shot_empty 4 / shot_retry 2 / restores 1 / hwnd_relookup 2`、退出码 3）——两条都能被 `score.py` 照常打分。
    ⚠ **"瞬时"类空帧没能构造出来**（两种可控手法都是永久的）⇒ "重试能救回瞬时空帧"**既未证实也未证伪**；能确证的是**空帧不再丢批**。
19. **`ask_box_shift_px` 只记每题"首次"重算的位移**（批次 10 新增字段，46 行全 `[0,0]`）⇒ 它只能说明"进题后首次重算与冻结框一致"，**不能**用来证明"守门那一帧的框被移动过"。要拿后者必须改成记 max / 分布（未做）。
20. **最小化 ⇒ 窗口对 UIA / `EnumWindows` 都不可见**（批次 11 构造 2 实测）：`ShowWindow(SW_MINIMIZE)` 后 2 s 内该窗口从枚举里**消失**，驱动侧复现 `ValueError: cannot write empty image`（`shot_empty 4 / shot_retry 2 / restores 1 / hwnd_relookup 2`）⇒ **重试链救不回最小化**；
    但 app 进程**仍活着**（state 停在 `task_i 1`、`result none`、`layout.origin [-32000,-32000]`）⇒ **"空帧"不等于"靶子死了"**。旧注释里"最小化能靠 `restore` 救回"**未复现**。
    （`dsh-vision-kit/actor/actor.py` 的 `window` op（`@op('window')`/`o_window`）只有 front/foreground/bottom/restore/focus/top，**没有 minimize** ⇒ 这个状态只能从外部构造，驱动自己无法脱离。）
21. **滚轮 / 拖拽在 v1–v3 口径下覆盖 = 0**（批次 11 只读核查，见 `STATE.md` §7 #18）：`TRAP_PLAN`/`PLAN2`–`PLAN5` 的 screen 集合**从不排 `t_rows` / `t_chips`**，所有 `t_trap*` 记录里 `stats.scrolls = 0`、`stats.drags = 0`（键通道 `clicks` 也 0，鼠标通道 `clicks` 非 0）。
    旧文件 `gym-rows.json` / `keys-rows.json` / `rows-fix*.json` / `gym-chips*.json` / `keys-chips*.json` 都是 **v0 时代**产物 ⇒ **不可引用**。驱动侧两条路径确实存在但只挂在鼠标通道：`Driver.wheel()` = `gym_run.py:1199–1210`（唯一调用点 rows 处理器 `gym_run.py:2314` 的 `self.wheel(-3, …)`）、`Driver.drag()` = `gym_run.py:1193–1197`（唯一调用点 chips 处理器 `gym_run.py:2862`）。
    **第五段已量（`STATE.md` §16）**：`--keys --bg` 下两种题型都能跑（`t_rows` 8/8、24 题 22/24；`t_chips` 8/8），但 **`--bg` 下鼠标通道整条不生效** —— 三次鼠标-bg 跑（`t_rows` / `t_chips` / `t_chips+move@0.70`）都是 `0/3` 早停：驱动确实发出了动作（`clicks 3` / `drags 3` / `drags 9`、`src`/`dst` 有坐标）而 app 侧 `task_i` 停在 0、`detail {}`。机制（代码锚点，属推断）：bg 分支走 PostMessage（`o_click` ⇒ `post_click`、`o_drag` ⇒ `post_drag`、`o_scroll` ⇒ `post_scroll`），而 `o_key` 在 bg 下**显式做 focus 交接**、其注释写明 Tk 会静默丢掉 post 进去的输入 ⇒ **滚轮与拖拽在"不抢前台"约束下量不到**（八问：1 条能 = 滚完用新帧重找；1 条代码级一致 = 方向；6 条量不到）。要量只能去前台鼠标批，或给鼠标 op 加 focus/物理通道（改代码）。
    **设计已落盘（2026-10-05 第十三段，只写设计不改代码）**：现状 / 已有键盘等价物 / 要补什么 / 三方案 / 推荐与判据见 **`DESIGN-18-scroll-drag.md`**（配 `STATE.md` §22）—— 推荐 = **C 为默认口径**（键通道优先，鼠标连续交互写成已知边界）+ 需要真凭据时用 **A 前台鼠标批**跑一次窄批（12–16 题，两场景各半）+ **B（给鼠标动作加物理通道）暂不做**（真 `SendInput` 仍要前台；改动会落在 `scripts_sha` 覆盖不到的执行器里 ⇒ 留档不可核对）。
    ⚠ **2026-10-05 第二十三段（只设计不改代码）：进成绩体系的设计已落盘 → `DESIGN-18-scroll-drag.md` §9。** 三条结论：① 靶子侧只改**两处一行**（`gym_app.py:737` / `:962-964` 的 `truth` 里加 `"truth_class": "viewport"`）—— 这两类题**本来就有真判定**（点中行 / 落对槽由 `finish()` 判 `ok`/`wrong`），只是当初没进计分协议；② **`score.py` 必改（最小）**：认识新类名 `viewport` 并**单列一行**，`viewport` **不进主分母**（`pass_rate` / `false_refusal` / `false_accept` 的定义与分母一字不动）⇒ **批次 1–20 的主线可比性不受影响**（这正是选新类名、不复用 `answerable` 的全部理由）；③ 回退 = **单文件 revert**（改动只在两个 `return` 字典里加键、无状态 ⇒ 同 seed 同 scenario 下题与判定逐题不变，只有 `ready` 事件多一个字段）。**本段未改任何 `.py`**（三件套 sha 逐位未变）；真改 `gym_app.py` = **首次裂靶子 sha**，留到下一段。  ⚠ **阶段 3.4 = 已实施**：靶子 `t_rows` / `t_chips` 的 `truth` 各加两键（`truth_class = "viewport"` / `variant`），`score.py` 给它**独立桶** `viewport_n` / `viewport_pass`（**不进五判定、不进主分母**，另打一行），`--selftest` 41 → 43 项；**离线回归 = 新旧打分器在 5 个既有 run json 上输出逐字节相同**（批次 1–20 读数不受影响）；靶子**首次裂 sha**（`66632d85eac81c12` → `17b6a59cb831dafa`）、`score.py`（`ef066713a03eb940` → `c1a251a248a029c7`）、`scripts_sha`（`b8f83571f650` → `0c2c420e4d40`）、`gym_run.py` 未动；**未跑批** ⇒ `viewport` 桶的首次真取数与滚轮/拖拽的覆盖结论**仍在 3.5**。实施记录见 `STATE.md` §33。
    ⚠ **2026-10-05 第二十四段（纯文档：只列重跑清单 + 只出修复设计，未改代码、未跑批）：**#21 的**必重跑 = 批次 14 + 批次 20**（各 3 行 `prose_only` = `acted/none` + 早停）；**批次 16–19 该族题数 = 0** ⇒ **#20 结论不受影响**（分母 0/0）；修法两路线见 `DESIGN-21-mouse-operability.md`，推荐**路线②**（`gym_run.py:3507` 之后加「点了没反应 ⇒ 走拒答」，+7 净行、不改靶子）。清单与成本见 `STATE.md` §31。
    ⚠ **2026-10-05 第二十六段（B 实施：裂 `gym_run.py` sha，`3fa0e4ba4b1b9679` → `d8594bff3738ca9b`，净 +9 行）：#21 已修** —— 鼠标分支在「一次 `click_label` 之后没等到任何判定、且 app 仍停在这一题」时走 `refuse()`（四条守卫 + 次序硬约束，见 `DESIGN-21` §4）。两批前台复跑**全跑满**（批次 21 = 24/24、批次 22 = 60/60）：`false_accept` 归零、`false_refusal` 未上升、与批次 20 前 21 题判定**逐题一致**、与批次 14 的**唯一翻转 = `task_i 21`**。**`--bg` 鼠标通道与滚轮/拖拽（#18）不变**；本段的 `popup` 结论**不引用批次 22**（仍指批次 16–19）。记录见 `STATE.md` §32、数字见 `../sol/sandbox/SCORE.md` 批次 21/22 节。
22. **驱动读 actor 回包要读 inline 字段**（2026-10-05 第十段，欠账 #16 的真根因）：`results=True` 时 actor 才写 `step["data"]`，而那份副本经过 `actor.py:_slim()` 折叠 —— **list 只留前 ~6 项**、str 截 400 字符；`step["windows"]` 这类 **inline 才是全量**（同一条回包实测 inline **11** 项 vs `data` **7** 项）。⇒ **任何"某个窗口 / 某个元素不在列表里"的结论，先确认不是被折叠掉的**；本欠账因此拖了三段（把"读错字段"当成"枚举不到"）。
    附两条环境事实（写 actor 探针时必踩）：① actor `:8731` 是**裸 TCP + 换行 JSON**（`{"op":"run","steps":[…]}`），**不是 HTTP**（用 `urllib` 会得到 `BadStatusLine`）；② **WSL 到不了 Windows loopback** ⇒ 探针必须 `pwsh` + Windows venv python（复刻驱动读法的脚本 = `D:\DSH\dsh-actor\tmp\w10-uia-probe3.py`）。

23. **非 bg 鼠标通道点不到独立弹窗：两道门**（2026-10-05 第十二段只读探针，欠账 #20；`STATE.md` §20）：① **看不见** —— 非 bg 分支读的是 **app 矩形屏幕抓帧**，而驱动自己的 reader 在这一帧上**从来没有**把按钮当候选：`_find_blocks` 在弹窗区给 **0** 块（把 `max_h` 抬到 400、`max_frac` 0.95、`solid` 0.6 **都没用**），词路径只读到散文里**小写**的 `dismiss`（`source text`、`fill_share 0.213`、`neighbours 7`）⇒ 被 veto 规则 `share < 0.45 and neighbours >= 2` 否掉 ⇒ 候选 **= 空**、一次都不点（`dialog_refused` 每帧 +1 = 批次 13-B 的 **28**）。**只有"弹窗自己的窗口帧"能干净读到它**（`box [188,104,96,48]`、`fill 1.00`、`label "DISMISS"`、`source block`、不 veto）—— 而 `dismiss_interference()` 里 `if self.bg` 那条分支读的**正是这一帧**。② **抢前台** —— 该通道的点击都带 `front_title`，`_maybe_front(front_top=True)` → `{"op":"window","mode":"top"}` = **pin TOPMOST**；实测真鼠标点按钮正中心 `[806,762]`（`how xy`、`click n1 left`、4.67 ms）**带 `front_title` ⇒ 弹窗不关**，**同一点不带 ⇒ 弹窗立刻消失**。⇒ 结论 = **两道独立门**，不是"点不动"；最小修法 = 非 bg 分支照抄隔壁 `if self.bg` 分支（读弹窗自己的窗口 + 点击别钉 topmost），约 10–15 行（`STATE.md` §20.4 选项 D）。探针产物（不进沙箱）在 `D:\DSH\dsh-actor\tmp\`：6 个脚本（`w14_popup_probe.py` / `w14_read_popup.py` / `w14_read_full.py` / `w14_blocks_caps.py` / `w14_click_button.py` / `w14_click_matrix.py`）+ `w14-probe.json`、`w14-probe2.json`、`w14-probe3.json`、`w14-probe4.json`、`w14-click-button.json`、`w14-click-matrix.json` + 5 张帧 PNG（`w14-frame-front/full/printwindow/popup/after.png`）。

> ⚠ **2026-10-05 第十三段：选项 D 试过了 —— 判据未过、已回退。** 照盲区 23 的两道门改了两处（非 bg 鼠标分支读**弹窗自己的窗口帧** + 点击**不带 `front_title`**；`shot_window()` 的屏幕原点由**窗口 rect** 换成回包的 **client origin** —— 实测两者差 **+11 / +45 px**），净 +26 行、只碰清障路径；干跑 `--tasks 2` = 2/2、清障 2/2；正式批（鼠标通道 `popup@0.35`、60 题）**task 21 早停、退出码 1**，`popup_seen 11 / popup_dismissed 10 / popup_dismiss_failed 1` ⇒ **判据 `dismissed == seen` 未达成 ⇒ 按规格回退**（`gym_run.py` 回到 `87470aaff559`；补丁留档 `D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`）。残留 = **"单次漏点即整题死锁"**（同一点不补点 + 调用方 `gym_run.py:3460` 在计数 ≠ 0 时直接 break 去 replan）；三条下一步与逐条数字见 `../sol/sandbox/SCORE.md` 批次 14 节与 `STATE.md` §21。**这道门仍未修**：别把"照抄隔壁分支"当成已验证的修法。

> ⚠ **2026-10-05 第十四段：第二条修法（漏点后降级 `self.key("Return")`）也试过了 —— 干跑 2 题即失败、已回退。** 改动 = `dismiss_interference()` 非 bg 鼠标分支尾部新增"漏点处理"块（净 **+24 行**：`window_by_title("attention")` 判在不在 → 最多 3 次 `self.key("Return")` → 每次复查窗口是否已消失，新增计数 `popup_key_dismissed`），`py_compile` + `selftest 41 checks / 0 failed` 都过。干跑（鼠标通道、`--tasks 2`、`--chaos 1.0 --chaos-kind popup`、`--seed 20251007`）结果：**两题全 NONE、退出码 1、`score 0/2`**；`stats = {clicks 0, keys 45, interferences 39, replans 66, popup_seen 13, popup_dismiss_failed 13}`，而 **`popup_dismissed` 与 `popup_key_dismissed` 两个键在 stats 里根本不存在 = 13 次发现、0 次清掉**。**机制（比"哪条修法失败"更值钱）**：`Driver.key()`（`gym_run.py:1175-1198`）**只有 `self.keys and self.bg` 时才加 `focus: True`**；非 bg 通道发的是**真实 SendInput 按键**，Windows 只把它交给**真前台窗口**，而本机 DSH 会不断抢回前台（实测 `foreground after: 搜索 (hwnd 66100) unchanged: False`）⇒ **45 次 Return 全部没落到弹窗上**。对照：**鼠标点击是"按坐标"投递**的，弹窗又是 `-topmost`，像素命中就一定能收到 ⇒ 批次 14 的 `10/11` 不是"快好了"，而是**这条通道里唯一能到弹窗的机制**。⇒ **`key()` 这条路要成立，必须像键通道那样"直接投递给 app 窗口 + `focus=True` 焦点交接"，那是 B 方案（`DESIGN-18-scroll-drag.md` §4）的范围，不是"小改动"。** 回退后 sha 回 `87470aaff5593330`，本次补丁留档 `D:\DSH\dsh-actor\tmp\w16-popup-key-fallback.patch`（35 行），**A 批 / B 批都没跑**（干跑即证伪，不试第二遍改动），`#20` **仍开着**；**别再试第三条"看起来更聪明"的坐标/按键变体** —— 先定 A（前台鼠标批）/ B（加托管通道）/ C（接受边界）。详见 `STATE.md` §23、`../sol/sandbox/SCORE.md` 批次 15 节。

> ⚠ **2026-10-05 第十五段：通道层三选一 —— 决定走 C（接受边界），A 按需、B 不做。** 依据 = `STATE.md` §24（三处逐条读到的证据：§23.4 的投递机制结论；`gym_run.py:3458-3465` 的耦合 `if n: … break` —— `n` 只表示"点了一下"、不表示"弹窗没了"，**漏一次点就早停**；`_maybe_front()` 是鼠标/按键**共用**的输入前处理）。**C 的含义（写死在文档里才算数）**：鼠标通道 `popup` 这一组合**显式记为不可测边界**（键通道两个强度档的成绩不变、仍有效），欠账 **#20 保持开着、不改"已关闭"** —— 采用的是该行判据栏的第二个分支"明确宣告不支持并划掉该组合"。**A 若日后要跑**：必须先重新落地第十三段选项 D 的补丁（否则连按钮都读不到）、**先拆上面那条耦合**（否则一次漏点白占前台），再跑 60 题前台批并显式声明通道。**B 不做**：改 `dsh-vision-kit\actor` 落在 `scripts_sha` 覆盖不到的层 ⇒ 读数不可核对（与 `DESIGN-18-scroll-drag.md` §7.4 同根）。**别再试第三条坐标/按键变体。**

> ⚠ **2026-10-05 第十六段：判据达成 —— #20 还清；改动保留为定稿（不回退）。** 用户选 (ii)「需要真凭据」⇒ 按第十五段写死的两个前置条件**一次做完**：先 `git apply` 重落第十三段选项 D 的补丁（应用后 sha = `85893817760a3be5`，与批次 14 的被测版本**逐位相同**），再拆掉"漏一次点 ⇒ 整题死锁"的耦合（非 bg 分支同一落点 ±8 px 已点过两次即不再当候选 ⇒ **允许补点一次**；调用方**只有 `window_by_title("attention") is None` 才 `break`**，原来 `if n:` 里 `n` 只表示"点了一下"）。净 **+30 行**（闸写的是"改动 **> 30 行** ⇒ 停手"⇒ **未触发，但与阈值相等**），两个调用点都在 `--chaos` 之下（`gym_run.py:2035 if self.expect_chaos:` 与等判定循环的 `if a.chaos:`）⇒ **非 chaos 批逐字未变、不需要回归批**。正式批 = **鼠标通道 `popup@0.70` / 16 题**（`t_trap2-w17-popup70-mouse.json`，json sha `c6c41590cb5ef192`，`scripts_sha 780adce4017e`，`gym_run.py 3fa0e4ba4b1b9679`）：**16/16 `OK`、退出码 0、无早停**、**`popup_seen 14 / popup_dismissed 14`（`failed` 键不存在）**、`interferences 14`（= 每次发现只点一下）、app 侧 `chaos_planned 14 / chaos 14` 一一对应、**无 `blocked` 事件**；`score.py` = `v2 16/16 100.0%`、`answered_right=16`、`guard P50 125 / P95 168 ms`、`foreground after … unchanged: True`。⇒ **`STATE.md` §7 #20 与本文件 §6 表的 #13 收口为"还清"**（窄批口径）。**为什么是 0.70 而不是 §24.2 写的 0.35**：0.35 档在 16 题窄批里期望弹窗数 ≈ 3 `< 5` ⇒ **判据本身的 `popup_seen ≥ 5` 在那个组合下不可达**。**⚠ 边界（未变的部分）**：**拆耦合一次都没被触发**（`interferences == popup_seen == 14` 可证）⇒ 它是**未被检验的保险**；批次 14 的 `1/11` 漏点**未复现**，14 次样本区分不了"率降了"与"运气好"；**`--bg` 鼠标通道整条不生效（盲区 21）不在本批范围、仍未测**；单批单档、无重复批。逐条边界见 `../sol/sandbox/SCORE.md` 批次 16 节 **16.5** + `STATE.md` §25。
>
> **⚠ 第十七段补记（回填段，纯文档、不跑批不裂 sha）：把这一条的口径收紧成三句。** ① **封存结论** = "**通道可用 + 未引入回归 + 跑满不早停（窄批口径）**" —— 原稿里"**补丁充分**"是**过度声明**：那条拆耦合**一次都没被触发** ⇒ 本批对它**零信息量**，能说的只有"没有引入回归"（已同步 `REPORT.md` §5.2 ④ / `../sol/sandbox/SCORE.md` 16.5-3 + **16.6** / `STATE.md` 接续点 ⑤ + §25）。② **"漏点是否消除" = 【未决】** —— 单批 16 题在统计上区分不了"率降了"与"运气好"（量化见 `REPORT.md` 附录 B-7）；**唯一入口 = 再跑 3 批（每批 16 题）共 48 题**，本段不跑，将来要证也**只有这一条路**。③ 下一步可做 **(i) 什么都不动** 或 **(iii) 走出练习场**（把练习场外的东西拉进来测），二者**无依赖**、可任选其一或都不选。

> ⚠ **2026-10-05 第十九段：那条保险被实战检验了一次 —— 补点被触发且救回；"漏点是否消除" 仍【未决】。** 19b 按上面写死的**唯一入口**跑了 **3 批 × 16 题**（鼠标前台通道、`popup@0.70`、seed 20251008/09/10，**代码一行未改**）：**批次 18 里 `interferences 9 > popup_seen 8`** ⇒ 恰有一次遭遇点了两发（第一发没打掉、重取帧后再点一发）、该遭遇最终被清掉（`popup_dismiss_failed 0`）、该批 **16/16**、无 `blocked`、无早停 ⇒ **补丁/拆耦合被触发且有效（在这一次上）**。三批合计：遭遇 **28**、清障点击 **29**、**补点 1**、`failed` **0**、app 侧 `chaos 28` 与驱动侧 `popup_seen` 逐批 1:1、题级 **47/48**（批次 19 的 `task 14` 是**已知 `swap_timer` 时序竞争类**、退出码 1 但**非早停**）。⇒ **死锁率 0/28 遭遇**、95% 单侧上限 ≈ **10.7%**（rule of three）、第一发失手率 1/28 ≈ 3.6%（与批次 14 的 1/11 同量级）⇒ **"漏点是否消除" 仍 =【未决】**。**能证明的**：这条通道在三次重复下都跑满、那条保险至少真的救过一次题、没有反例（`failed` 全 0）。**不能证明的**：漏点率已被消除（上限 10.7% 仍宽）、这条保险在别的通道/别的干扰下够用。数值与逐条边界见 `../sol/sandbox/SCORE.md` 批次 17–19 节 + `STATE.md` §27。> ⚠ **2026-10-05 第二十段：#20 收口（结项 —— 不再是"活动欠账"）** —— 四行定稿：① **通道可用** ✓（第十六段 16 题 + 第十九段 3 × 16 题都在同一通道上跑满、不早停）；② **保险单实例已验证** ✓ —— 那条拆耦合在**批次 18** 被真实触发一次并**救回**（`interferences 9 > popup_seen 8`、该遭遇被清掉、该批 16/16、无 `blocked`）；③ **"漏点是否消除" =【未决】，且判定为"不追加"** —— 再加 3 批（48 题）只能把 95% 单侧上限从 **≈10.7%** 收窄到与观测失手率（1/28 ≈ 3.6%）**同一量级** ⇒ 仍**分不开**"已消除"与"还剩百分之几"，**边际收益 ≈ 0**（"不追加"= 已决定不再投入，不是待办）；④ **口径只写"路径可达 + 单次有效"**，**不写**"保险有效 / 够用"（那会被读成"多次验证"）。⇒ **本项移入"已结项"**；**唯一入口**（若将来真要证消除）= 再跑 3 批 48 题，**本段不跑、非当前计划**。**下一件可做**：**(i) 什么都不动** 或 **(iii) 走出练习场**（把练习场外的东西拉进来测）—— 二者**无依赖**、可任选其一或都不选。数值与逐条边界见 `../sol/sandbox/SCORE.md` 批次 17–19 节 + `STATE.md` §27/§28。

> ⚠ **2026-10-05 第二十段：#20 收口（结项 —— 不再是"活动欠账"）—— 四行定稿。** ① **通道可用** ✓（第十六段 16 题 + 第十九段 3 × 16 题都在同一个前台鼠标通道上跑满、不早停）；② **保险单实例已验证** ✓ —— 那条拆耦合在**批次 18** 被真实触发一次并**救回**（`interferences 9 > popup_seen 8`、该遭遇被清掉、该批 16/16、无 `blocked`）；③ **"漏点是否消除" =【未决】，且判定为"不追加"** —— 再加 3 批（48 题）只能把 95% 单侧上限从 **≈10.7%** 收窄到与观测失手率（1/28 ≈ 3.6%）**同一量级** ⇒ 仍**分不开**"已消除"与"还剩百分之几"，**边际收益 ≈ 0**；④ 口径只写"**路径可达 + 单次有效**"，**不写**"保险有效 / 够用"（那会被读成"多次验证"）。⇒ **本项移入"已结项"**；**唯一入口**（若将来真要证消除）= **再跑 3 批 48 题，本段不跑、非当前计划**。**下一件可做（二者无依赖）**：(i) **什么都不动**（口径已自洽）或 (iii) **走出练习场**（把这套"全盲驱动 + 事后联结真值"的判分方法用到练习靶之外的界面）。数值与逐条边界见 `../sol/sandbox/SCORE.md` 批次 17–19 节、`STATE.md` §27/§28。

## 5. 证据在哪

- 运行 json：`../sol/sandbox/t_trap4-*.json`（`-1` 批次 4；`-2`/`-3` 批次 5 两次中途批，判据各修正一次；
  **`-4` = 批次 5 定稿，sha `ebfc7dce831a`，24/38，核心 14 题 7/14 → 10/14**）。
- 批次 6：`../sol/sandbox/t_trap5-1.json`（sha `9db420c422a2`，48 题，37/48，核心 14 题 → **12/14**，
  twin **8/8**，race **5/5**）+ chaos 三批 `t_trap2-w6b-control/chaos35/chaos70.json`（sha `ee68f457577d`）
  与逐批即时打分的复跑 `t_trap2-w6c-*`。
- 批次 7：`../sol/sandbox/t_trap2-w7-control.json`（sha `481154ca264d`，**60/60**，逐格等于批次 6 `w6c` 控制批 ⇒ 证明 #14 只改命名不改判定）；
  `../sol/sandbox/t_trap2-w7-move70.json`（同 sha，**修复前**，move 死锁 ⇒ 33/60 早退，⚠ **不可引用为 move 类定稿**，只用于定位根因）。
- 批次 8：`../sol/sandbox/t_trap2-w8-move70.json`（**move 类定稿**）+ `-move35/-slow35/-slow70/-popup35/-popup70`
  （同一 sha、每批自带 `*-state.json` / `*-events.jsonl` 留档，可事后 `score.py <json>` 复核）；
  chaos 数字一律标「**探索性·不并入定稿**」。
- 批次 9：`../sol/sandbox/t_trap6-1.json`（sha `f473ff21ad09`，鼠标通道 48 题，**36/48**，口径 v3；只动守门计时点与逐题记账 ⇒ 与批次 6 逐题同构，只差 race 家族三题）+ 自带 `-state.json`/`-events.jsonl`。
- 批次 10：`../sol/sandbox/t_trap2-w9-move70.json`（sha **`5dedae26c6e8`**，键通道 + `--bg`，`move@0.70`，**59/60**、`decided 100%`、`ask_read_unreadable 0`；`gym_run.py` = **`47c1d170f2e543c9`**）
  + 自带 `t_trap2-w9-move70-state.json` / `-events.jsonl`（可事后 `score.py t_trap2-w9-move70.json` 复核）。
  **对照批**：批次 8 `t_trap2-w8-move70.json`（`f598406cfc70`，58/60，同协议同 seed）；
  **作废批**：批次 10 首跑 —— **没有 json**，只剩 `-state.json`（`task_i 47`）与 `-events.jsonl`（2506733 B），且该 events 已被重跑覆盖 ⇒ **不可复核**。
- **批次 8 的事后复核证据**：`../sol/sandbox/t_trap2-w8-rescore.txt`（六个 json 各重跑一遍 `score.py` 的完整输出 + `selftest: 41 checks, 0 failed`）
  —— 复核逐行等于 `../sol/sandbox/SCORE.md` 批次 8 表的数字，且 `chaos == chaos_planned`（27/27、49/49、24/24、41/41、1/1、1/1）⇒ **欠账 #14 的留档-复核链路成立**。
  每批目录里同时有 `t_trap2-w8-<类><强度>.json` + `-state.json` + `-events.jsonl` 三件（共 18 个文件）。
- **批次 11**：`../sol/sandbox/t_trap7-1.json`（json sha `dd77abc08e911794`，鼠标通道 48 题，**35/48**，口径 v3；只改抓帧失败处理 ⇒ 与批次 9 逐题同构；`scripts_sha 8da029edccbc`；
  `gym_run.py` = **`105cf6cb679eea10`**、`score.py` = **`ef066713a03eb940`**、`gym_app.py` = `66632d85eac81c12` 未动）+ 自带 `t_trap7-1-state.json` / `-events.jsonl`；
  同段的失败路径产物 `t_trap7-empty6.json`(4354 B) / `t_trap7-minim6.json`(4546 B) / 合成先验 `t_trap7-partial-synth.json` —— **只做路径验证，不并入任何成绩**（见 `../sol/sandbox/SCORE.md` 批次 11 节 ③⑦）。
- **批次 12–13**（`popup` 类，键通道 + `--bg`，`scripts_sha 186edbd9c024`）：
  `../sol/sandbox/t_trap2-w12-popup35.json`（`0.35` 档，**60/60**、`popup_seen/dismissed/failed 24/24/0`）与
  `../sol/sandbox/t_trap2-w13-popup70.json`（`0.70` 档，**60/60**、`45/45/0`、`interferences 45`、无早停）+ 各自的 `-state.json` / `-events.jsonl`。
- **批次 13 的鼠标通道失败产物**：`../sol/sandbox/t_trap5-w13-popup35.json`（+ `-state.json` / `-events.jsonl`）—— 3 题早停、退出码 1、`disturbances: 0 fired`、app 侧 `event blocked by modal`；
  **不进任何成绩**，只作欠账 #20 的证据（见 §4 盲区 17 与 `../sol/sandbox/SCORE.md` 批次 13 节 13.2）。
- **批次 16**（`popup` 类，**鼠标通道、前台真实鼠标、非 `--bg`**，`scripts_sha 780adce4017e`，`gym_run.py` = **`3fa0e4ba4b1b9679`**）：
  `../sol/sandbox/t_trap2-w17-popup70-mouse.json`（json sha `c6c41590cb5ef192`，**16/16**、`popup_seen/dismissed 14/14`、`interferences 14`、无早停、退出码 0）
  + 自带 `t_trap2-w17-popup70-mouse-state.json`（sha `3960503d930d027e`）/ `-events.jsonl`（sha `45b8b5d861e9a677`）；
  同段干跑 `D:\DSH\dsh-actor\tmp\w17-dry.json`（2/2，与批次 14 干跑逐项同构），日志 `w17_A.log` / `w17_scoreA.txt`。
  `gym_app.py` = `66632d85eac81c12`、`score.py` = `ef066713a03eb940` **未动**；**这是 #20 的定稿批（窄批口径）**，见 §4 盲区 17 第十六段 ⚠ 块 + `../sol/sandbox/SCORE.md` 批次 16 节。
- **批次 17–19**（`popup` 类，**鼠标通道、前台真实鼠标、非 `--bg`**，`scripts_sha 780adce4017e`，`gym_run.py` = **`3fa0e4ba4b1b9679`** = 与批次 16 同一版）：
  `../sol/sandbox/t_trap2-w18-popup70-mouse-r1.json`（json sha `987c90db02ade387`，16/16，`popup_seen 10 / interferences 10`）、
  `-r2.json`（`ad655a1b3210d218`，**16/16，`popup_seen 8 / interferences 9` = 补点被触发且救回 ★**）、
  `-r3.json`（`e44222614893713a`，15/16，`popup_seen 10 / interferences 10`、**退出码 1**，那一题是已知 `swap_timer` 竞争类）
  + 各带 `-state.json`（`211aae967a92a50a` / `e63c98f4eaeb57e6` / `4eb532b6aa4f9074`）与 `-events.jsonl`（`d39b884685742cfc` / `5e497f046d9ed8d1` / `21b064f112d55692`）；
  日志与打分输出 `D:\DSH\dsh-actor\tmp\w18_r{1,2,3}.log` / `w18_score_r{1,2,3}.txt`。
  **这是"漏点是否消除"的唯一入口批次（3 × 16）**，也是**那条拆耦合第一次被真实触发**的证据。
- 逐题守门字段都在行里：`ask_label_read`、`ask_cells`、`ask_delta`、`ask_word_from`、`ask_word_short`、
  `ask_word_noise`、`ask_moved`、`ask_moved_press`、`ask_guard_skipped`、`label_painted`、`label_text_like`、
  `label_alt_tried`、`gate_ms`。
- 代码位置：`gym_run.py` 的 `press_guard` / `ask_label_now` / `ask_text_changed` / `ask_changed` /
  `ask_moved_now` / `painted_boxes` / `painted_hit` / `press_jitter` / `window_by_title`；
  `score.py` 的 `twin_failure` / `join_truth` / `v1_counts` / `v1_row` / `pct`。
- 设计与假设：`DESIGN-refusal-scoring.md`（修订 r2–r11 + §8「如果继续做」）、
  `STATE.md`（§6 批次 5 假设、§7 欠账清单、§8 放弃清单、§9 批次 6 假设与 §9.2 结果）。
- 批次 20（第二十二段 1b）：`../sol/sandbox/t_trap2-w22-popup35-mouse.json`（`scripts_sha 780adce4017e`、`gym_run.py 3fa0e4ba4b1b9679`，自带 `-state.json` / `-events.jsonl`）—— #19 第四格（`popup@0.35` × 前台真鼠标）：fire 10、`popup_seen/dismissed 10/10`、补点 1 次、**21/24 早停**（归因见 §4 盲区 17 内的第二十二段块）；干跑 `D:\DSH\dsh-actor\tmp\w22-dry.json`、日志 `w22_b1.log`；打分 `score.py` 逐字在 `../sol/sandbox/SCORE.md` 20.4。
- 需求原文：`REQUIREMENTS-refusal-scoring.md`（五判定与边界条件的出处）。

## 6. 如果继续做（**全部已冻结**，用户 2026-10-04 定：不再为此裂 sha）

每一条都带判据；顺序即建议顺序。"冻结"= 现在不做、也不影响上面任何已公布数字。

| # | 欠账 | 判据（做到什么算完） |
|---|---|---|
| 1 | 守门 ④：多候选匹配一律过余量（精确路径现在不设余量，`GAMM` vs `GAMMA` 折叠相似度 0.889 也能接上） | `t_trap` 家族"选到非唯一候选"次数为 0 且新增 `label_ambiguous` 计数 |
| 2 | 守门 ⑤：守卫内改序（文本重读在前、廉价指纹在后） | 单字形换题家族的 `ask_word_noise` 误判为 0 |
| 3 | 守门 ⑥：`verify_before_act` 预算改"每计划一次 + 每题上限 4"，并把鼠标通道并入 | `verify_budget_skip == 0`，鼠标首次按压 +89 ms 可接受（`--no-press-verify` 可回退） |
| 4 | **Option A：守门每帧重算 banner box**（批次 8 新增，本批只做"读不出 ⇒ 回落指纹"） | **✅ 已还（批次 10）**：守门不再依赖计划时记录的 `ask_box`（`ask_box_recomputed 124 == ask_gates 124`）；`ask_read_unreadable` 在 `move@0.70` **2 → 0**（键通道批；前台批未复跑，按同一条代码路径推及）。见 `../sol/sandbox/SCORE.md` 批次 10 节 + `STATE.md` §14 |
| 5 | `guard-blind` 清零（单字形家族仍靠"文件仲裁"兜） | 该家族给出可引用分母且漏判为 0 | **✅ 已量·关闭（第六段）**：20 题键通道批 `blind_seen = 0`（events `trap_stale_press = 0`），家族 5/5；`task_i 13` 指纹静默仍被文本重读抓住 ⇒ 文本重读已覆盖，分母不再有判别价值（见 `STATE.md` §17） |
| 6 | `t_gate` 移到 `self.shot()` 之后（口径统一） | `gate_p50` 与 `ms_askgate/ask_gates` 同口径（差 < 5 ms） |
| 7 | `press_delay_ms` 进逐题行 | 逐题能看到 jitter 时长 |
| 8 | `swap_after_press` 每题约 5 s 空等 | 换题后不再等满 `verdict_ms` 就重规划 |
| 9 | `no_badge_fill` 用**真实题面画笔**重标定（现在的 `T_VIS=68` 对不上真实 0.50 档 D1=57） | 标定曲线与受测同批，n ≥ 9/档 |
| 10 | 键通道核心 2 题（synonym）独立成批 + 分层跑测（核心 ~15 题 / 盲区 ~20 题） | 核心集可单独跑且 < 2 min |
| 11 | 批次 1–6 的 events 无留档 ⇒ 那些批次**事后不可复核**（数字都是跑完立刻打的，仍然有效） | 只对新批有效（#14 已还）；不追溯 |
| 12 | chaos 未跑到的强度组合（如 `move@0.35` 的复现性、`slow`/`popup` 若某档不足 5 fire） | 每类 2 强度 × ≥5 fire（**探索性**，不并入定稿） |
| 13 | **`popup` 类干扰打不掉**（键通道 `--keys --bg` 的 `dismiss_interference` 只按标题找 `"attention"`，找不到）⇒ 该类测不了（**第十段起：键通道可测；第十一段：鼠标通道仍不可测 = 新欠账 #20**） | `--keys --bg` 能打掉外来窗口（可借鼠标通道的视觉路径：`_button_candidates(img2,"DISMISS")`），`popup` 跑到 ≥5 fire |

> 上表是 **2026-10-04 冻结时的原样清单**（注意：**本表 #4 = `STATE.md` §7 #15**，两处编号不同）。
> **2026-10-05 第四段还掉了本表 #4**（判据两条都满足）；同一天新开的两条**不在本表**、记在 `STATE.md` §7：
> **#17 `shot` 空帧零容忍**（一次空位图 = 整批退出 + 不写 run json ⇒ 第四段首跑白跑一次，见 §4 盲区 18）与 **`ask_box_shift_px` 只记首次**（仪表局限，见 §4 盲区 19）。
> **2026-10-05 第五段还掉了 #17**（批次 11：重试 3 次 + partial 落盘 + 退出码 3，判定路径一字未动；见 §4 盲区 18 与 `../sol/sandbox/SCORE.md` 批次 11 节），并**新增 #18**（滚轮 + 拖拽的连续/视口类盲区：v1–v3 覆盖 = 0、驱动有路径但只挂鼠标通道，
> 见 §4 盲区 21 与 `STATE.md` §7 #18 / §16；**只量不改**）—— **#18 当段已量完**：`--keys --bg` 下两种题型都能跑（rows 8/8 与 22/24、chips 8/8），但 bg 鼠标通道不生效 ⇒ 八问里 **1 条能 + 1 条代码级一致 + 6 条量不到**，状态维持 **欠（有据）**（待前台鼠标批或改鼠标 op）。
> **2026-10-05 第十段还掉了 `STATE.md` §7 #16**（`popup` 类：批次 12 `popup_seen 24 / popup_dismissed 24 / failed 0`、60/60 无早停；根因更正 = **actor 折叠截断 `data.windows`**，不是"枚举看不见"；见 §4 盲区 17 与 `../sol/sandbox/SCORE.md` 批次 12 节）。
> **2026-10-05 第十一段补测了 `STATE.md` §7 #19 的覆盖面**：**键通道的第二个强度档也成立**（`popup_seen/dismissed 45/45`、60 题无早停），但**鼠标通道仍不可测**（3 题早停、退出码 1）⇒ 覆盖面 = **2 档 1 通道**，#19 只关了一半，并**新开 #20**（鼠标通道下清障路径不生效，见 §4 盲区 17 与 `../sol/sandbox/SCORE.md` 批次 13 节 13.2/13.5）。
> **2026-10-05 第十二段只读探针 + 读码（不改一行代码、不裂 sha、不动批次文件）**：**#20 根因定案 = 两道独立门**（① 该通道读的那一帧里按钮从来不是候选 ② 点击带的 `front_title` 把 app 钉成 topmost；见 §4 盲区 23 与 `STATE.md` §20）；**#18 读码结论 = 覆盖缺口、不是功能缺陷**（滚轮与拖拽在键通道里都有键盘等价物、驱动已经在用；`--bg` 下的失效 = Tk 忽略 posted 鼠标消息，`gym_run.py:2329` 的注释早已写明）⇒ 三症状**不是**同一根因。
> **2026-10-05 第十三～十六段**：D（第十三段）**试过 ⇒ 判据未过、已回退**；"漏点后降级按键"（第十四段）**干跑即证伪、已回退**；第十五段在通道层三选一里**选 C**（接受边界、A 按需、B 不做）；**第十六段用户选 (ii)「需要真凭据」⇒ 重落 D 补丁 + 拆耦合 + 16 题前台窄批 ⇒ 16/16、`popup_seen/dismissed 14/14`、无早停 ⇒ 判据达成**，`STATE.md` §7 **#20 收口为"还清"（窄批口径）**，驱动改动**保留为定稿**（`gym_run.py 3fa0e4ba4b1b9679`、`scripts_sha 780adce4017e`，净 +30 行）。
> 下一件建议：**上面这张表仍是"全部已冻结、不再为此裂 sha"**；#4 / #5 / #12 / #16 / #17 / #19（键通道那半边）/ **#20（第十六段）** 都已还或已关闭，**不要再重开**；**#18** 已读清（键通道 8/8 可用，鼠标连续交互写进已知边界即可 —— 要真凭据才跑一次 12–16 题前台窄批）；非批次类的那一件是**报告正文**（`REPORT.md` = **v0.9**，2026-10-05 第二十段同步；框架 `vision-work/audit/REPORT-draft.md`，不裂 sha）。**第十九段（19b）把 #20 的最后一块补上了**：3 批 × 16 题前台窄批让那条拆耦合**第一次被真实触发并救回**（批次 18），三批 **0/28 遭遇死锁** ⇒ 95% 单侧上限 ≈ **10.7%**；⇒ **#20 的"漏点是否消除"仍 =【未决】**（3 × 16 题仍宽），但它**不再"未受检验"**；**第二十段把 #20 收口（结项、判定"不追加"，见 §4 盲区 23 末尾的收口块与 `STATE.md` §28）**；**#18 不变**（滚轮/拖拽仍未覆盖）。
> **2026-10-05 第二十二～二十三段**：**#19 已关死** —— 批次 20 补齐第四格（`popup@0.35` × 前台真鼠标；数值与边界见 `../sol/sandbox/SCORE.md` 批次 20 节，⚠ 该批 **21/24 早停**，归因 = 新欠账 `STATE.md` §7 **#21**：「鼠标通道缺可操作性判据」）。**#21 已判定 = 通道级缺口、高优先级、未修**；**#18 进成绩体系的设计** → `DESIGN-18-scroll-drag.md` §9（**`score.py` 必改**、靶子**首次**裂 sha、回退 = 单文件 revert）。**当前计划 = 报告 v0.11 + 下面两件（无依赖）**：**(A)** 按 §9 改靶子 → 跑 `t_rows`/`t_chips` 前台窄批；**(B)** 修 #21（给 `gym_run.py:2164-2168` 加键通道那套可操作性判据）。
> **2026-10-05 第二十四段（纯文档：不跑批、不改 `.py`、不裂 sha）**：#21 的**重跑清单**（必重跑 = 批次 14/20；须重评 = **空**；不受影响 = 键通道全部 + 16–19 + `t_trap3` 6 批）与**修复设计**（推荐路线②，+7 净行）落盘 —— 清单与 #20 答复见 `STATE.md` §31，设计全文见 `DESIGN-21-mouse-operability.md`。**#20 结论不受影响**（产生它的四批该族题数 = 0）。


- **2026-10-05 第二十六段**：B 实施（修 #21）—— `gym_run.py` 裂一次 sha（`3fa0e4ba4b1b9679` → **`d8594bff3738ca9b`**，净 +9 行，`scripts_sha 586171888d39`），两批前台复跑（批次 21/22）全跑满；#21 从「已判定 / 未修」转为「**已修（有验证）**」。当前计划 = **A（#18 进体系：`gym_app.py` 两处一行 + `score.py` 新桶 = 首次裂靶子 sha）**。详见 `STATE.md` §32 与 `../sol/sandbox/SCORE.md` 批次 21/22 节。 **阶段 3.4**（2026-10-05）：`viewport` 进体系（A 落地）—— 靶子首次裂 sha（`66632d85eac81c12` → `17b6a59cb831dafa`）、`score.py` 新桶（`ef066713a03eb940` → `c1a251a248a029c7`）、`scripts_sha b8f83571f650` → `0c2c420e4d40`；`gym_run.py 2ba26b608cf7ec18` 未动；**本段未跑批**（离线回归 5 个 json 逐字节相同），验证批在 3.5。
