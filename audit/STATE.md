# 存档：GUI 感知驱动的训练场（2026-10-05 更新）

> 从这里继续。所有路径都在 `D:\DSH\vision-work\sol\sandbox\`（下称 `sandbox\`）。
> 计分板：`sandbox\SCORE.md`；分表工具 `sandbox\score.py`。

## 接续点（2026-10-05 收工：探路日 + 技能落盘 + 批次 9 + 第三段三件 + 第四段（#4 改完、批次 10 定稿）+ **第五段（#17 改完、批次 11 定稿、#18 已量）+ 第六段（#12 关闭）+ 第七段（报告正文初稿）+ 第八段（独立仓库已推送）**+ 第九段（报告 v0.2 打磨）+ **第十段（报告 v0.2 已提交推送、#16 还清 → 批次 12 定稿、`gym_run.py` 裂一次 sha = `87470aaff559`）+ 第十一段（报告 v0.3 改正 `popup` 表述、#19 覆盖面补测：0.70 档键通道 ✅ / 鼠标通道 ❌ → 新增 #20；三件套一字未动）**+ 第十二段（#20 只读探针定案「两道门」、#18 读码结案「覆盖缺口、不是功能缺陷」；报告与三件套一字未动）+ 第十三段（#20 选项 D 修复尝试：干跑 2/2、正式批清障 10/11 但 task 21 早停 ⇒ 按终止条件**已回退**、sha 回 `87470aaff559`；报告 v0.4；#18 设计落盘）+ 第十四段（#20 第二次尝试「降级按键」干跑 2 题即被证伪、**未成批已回退**；报告 v0.5 仅同步）+ **第十五段（#20 通道层选择 + #18 方案选定：两处都选 C「接受边界」；不改代码、不跑批、不裂 sha；报告 v0.6）**+ **第十六段（#20 第三次尝试：重落第十三段选项 D 补丁 + 拆「漏一次点 ⇒ 整题死锁」耦合 ⇒ 鼠标通道 16 题前台窄批**全过、判据达成、#20 还清**；`gym_run.py` 裂一次 sha = `3fa0e4ba4b1b9679`、`scripts_sha 780adce4017e`；**保留为定稿**；报告 v0.7）**+ **第十七段（回填段：收回"补丁充分"过度声明、补 `scripts_sha` 前值 `186edbd9c024 → 780adce4017e`、把"漏点是否消除"标成【未决】；纯文档、不跑批、不裂 sha；提交 `6a29a61`）+ 第十八段（**18a 封账**：技能注入复验**通**、"补丁充分"改证清单 **3 处声称 → 0 处**、CHANGELOG 归属确认；**纯文档、不跑批、不裂 sha**；明细见本文 **§26**）**+ 第十九段（**19a 技能正文对齐**：盲区 17→**23** 条、`popup` 旧规则"任何情况下不引用"→"键通道两档 + 鼠标窄批可引用"、`gym_run.py` 3465→**3687** 行；技能 sha `823a33e02889c3c0 → 88f62d610d87af0b`；**19b 拆耦合实战**：3 批 × 16 题鼠标前台窄批 `popup@0.70`（seed 20251008/09/10）⇒ **批次 18 里补点被触发且救回**、三批 **0/28 遭遇死锁**（95% 单侧上限 ≈ **10.7%**）、`failed` 全 0、题级 **47/48**（批次 19 那题是已知 `swap_timer` 竞争类、退出码 1 但**非早停**）；**代码一行未改**（`gym_run.py` 仍 `3fa0e4ba4b1b9679`）；明细见本文 **§27** 与 `../sol/sandbox/SCORE.md` 批次 17–19 节）**+ **第二十段（技能正文**全量对齐 4 处**：引用规则 7→**9**、窗口计数按标题**子串**匹配的坑、`--chaos-kind` 的实际 choices 与 `--chaos-ms` 的真实默认；技能 sha `88f62d610d87af0b → 8d3182cbfc514df4`、110→112 行）+ **#20 收口（结项）**：① 通道可用 ✓ ② 保险单实例已验证（批次 18 触发一次并救回）✓ ③ "漏点是否消除" =【未决】且**判定"不追加"**（边际收益 ≈ 0）④ 口径只写"路径可达 + 单次有效"；**纯文档、不跑批、不裂 sha**；明细见本文 **§28**）**；开工先读这几行）

- **最新一段（第十六段 2026-10-05）：#20 第三次尝试（重落选项 D 补丁 + 拆耦合）—— 16 题前台窄批全过、判据达成、#20 还清**：
  ① **用户在三选一里选了 (ii)「需要真凭据」**。按 §24.3 写死的两个前置条件**一次做完**：先 `git apply` 重落第十三段的选项 D 补丁（`D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`；应用后 sha = `85893817760a3be5`，与批次 14 的被测版本**逐位相同**），再拆掉「漏一次点 ⇒ 整题死锁」的耦合 —— (a) 同一落点（±8 px）已点过两次即不再当候选 ⇒ **允许补点一次**；(c) 清障后**只有 `window_by_title("attention") is None` 才 `break`**（原来 `if n:` 里 `n` 只表示"点了一下"）。**净 +30 行**，`gym_app.py` / `score.py` 一字未动。
  ② **为什么不需要回归批**：`dismiss_interference()` 的两个调用点都在 `--chaos` 之下（`gym_run.py:2035` 的 `if self.expect_chaos:` 与等判定循环里的 `if a.chaos:`），`shot_window()` 的另外两个调用点也都在它内部 ⇒ **非 chaos 批逐字未变**，批次 4/5/6/9/11 的鼠标成绩与可比性不受影响。
  ③ **sha 轨迹**：`gym_run.py 87470aaff5593330` → `85893817760a3be5` → **`3fa0e4ba4b1b9679`（保留为定稿、未回退）**；`scripts_sha 186edbd9c024 → 780adce4017e`。闸门：`py_compile` 过、`score.py --selftest` = **41 checks / 0 failed**。**硬闸如实标注**：净值 **+30**、闸写的是"改动 **> 30 行** ⇒ 停手"⇒ 未触发，但**与阈值相等（贴线）**。
  ④ **两批**：干跑 2 题 = **2/2**（与批次 14 干跑逐项同构：`seen 2 / dismissed 2 / clicks 6`）；正式批 = **鼠标通道 `popup@0.70`、16 题**（`t_trap2-w17-popup70-mouse.json`，json sha `c6c41590cb5ef192`）**16/16 `OK`、退出码 0、无早停**、**`popup_seen 14 / popup_dismissed 14`**（`popup_dismiss_failed` 键不存在 = 0）、`interferences 14`、`clicks 40`、`shots 98`、`ocr 195`、`gate P50 125 / P95 168 ms`、`foreground after … unchanged: True`；app 侧留档 `chaos_planned 14 / chaos 14`、**没有任何 `blocked` 事件**。**为什么是 0.70 不是 §24.2 写的 0.35**：0.35 在 16 题窄批里期望弹窗 ≈ 3 个 `< 5` ⇒ **判据自己的 `popup_seen ≥ 5` 在那个组合下不可达**；0.70 是更严的档（弹窗更多 = 漏点机会更多）。
  ⑤ **#20 还清（窄批口径）**：判据栏**第一个分支**达成 ⇒ §7 #20 行**从"根因已定案 / 判据未达标"改为"已还清"**。但**拆耦合本身没有被检验**（`interferences == popup_seen == 14` ⇒ 补点与重试**一次都没触发**，是未被检验的保险）；批次 14 的 `1/11` 漏点**未复现**，可 14 次样本区分不了"率降了"与"运气好"；`--bg` 鼠标通道整条不生效（盲区 #21）不在本批范围。⇒ 本批**能证明**"**没有引入回归**、这条通道能跑满 16 题不早停、判据达成"，**不能证明**那条保险"够用或有效"（一次都没被触发 ⇒ **零信息量**），更**不能证明**"漏点已被消除"（= **【未决】**，唯一入口 = 3 批 48 题，见 `HANDOFF.md` §4；量化见 `REPORT.md` 附录 B-7）。边界逐条见 `../sol/sandbox/SCORE.md` 批次 16 节 **16.5**。
  ⑥ **落点**：`../sol/sandbox/SCORE.md` 批次 16 节（文件末，含 sha 表新增一行）+ 本文 **§7 #20 行**与 **§25** + `HANDOFF.md` §3/§4/§5/§6 + `../CHANGELOG.md` + 报告 **v0.7**（版本行、§5.1 第 17 行、§5.2 ④、§5.3、§6.2 D、§7.2/§7.3、第 8 章、附录 A 行号重算、**新增附录 B-7**、附录 C 一行命令）。
- **第十五段（2026-10-05）：#20 通道层选择 + #18 方案选定 —— 两处都选 C（接受边界）；不改代码、不跑批、不裂 sha**：
  ① **#20 通道层三选一 ⇒ 选 C（接受边界）**：鼠标通道的 `popup` 写成**已知边界**（键通道两档是有效成绩、账目不变、**#20 保持开着**）；**A（前台批 + 显式声明通道）降级为按需**——要用就得重落批次 14 的补丁，且**必须先拆掉"漏一次点 ⇒ 整题死锁"的耦合**（两个前置条件写进 §24.3）；**B（给鼠标动作加托管输入 + 焦点交接）不做**——要改 `dsh-vision-kit\actor` 里鼠标与按键**共用**的 `_maybe_front()`，读数落在 `scripts_sha` 覆盖不到的层、不可核对，还可能抢前台。依据 = §23.4 + `gym_run.py:3452-3470` + actor 的 `o_click` / `o_key` 两条分支（§24.1 三处逐条读过）。
  ② **#18 同样选 C**：键通道优先（键盘等价物本就存在、驱动已在用），滚轮 / 拖拽的**真实鼠标路径写成已知边界**（代价 = 永远不会被自动化测试覆盖，只能靠前台手工验证）；A 的唯一适用场景 = 偶尔跑一次 **12–16 题前台窄批**拿真凭据；**B 不做**（与 #20 的 B 同根：actor 层改动、代价大、收益边际）。
  ③ **落点**：`STATE.md` §24（`:1257–1292`）+ `DESIGN-18-scroll-drag.md` §7（`:129–154`）+ `HANDOFF.md` 盲区 23 的 ⚠ 第十五段块（`:174–175`）+ 报告 **v0.6**（版本行、§5.1 **第 16 行 = 决策行不是批次**、§5.2 ④、§6.2 D 族、§7.2/§7.3、第 8 章、附录 A 行号重算、**新增附录 B-6**）；口径本身没变，变的是"这条洞被写成显式边界"。
  ④ **明天开工顺序（固定）**：**第一件 = 新会话验证技能目录注入**（`D:\DSH\skills\gui-audit-gym\SKILL.md` —— **阶段 3.3 起该技能只是指针**，规程正本 = 仓库内 `docs/OPERATING.md`）；**第二件 = 三选一**：(i) 什么都不动（口径已自洽、报告 v0.6 已同步）；(ii) 需要真凭据时按 §24.3 先拆耦合、再用 A 方案跑 12–16 题窄批；(iii) 走出练习场 / 报告 v0.7（若又有行号漂移）。
- **第十四段（2026-10-05）：#20 第二次修复尝试（降级按键）+ 报告 v0.5 仅同步 —— 干跑即被证伪、未成批、已回退**：
  ① **先读码再选方向，选了 (b)「失败时降级用靶子自己绑定的按键」**（§23.1.1 逐条结论：`gym_run.py:3460` 的"清障计数 ≠ 0 ⇒ break 去 replan"耦合**真实存在，但单独修不好**——弹窗还在 ⇒ 靶子什么都不判分 ⇒ 每题都判不出 ⇒ 仍会三连败早停，只改变"死在哪、不改变会不会死"；同点补点 = 对未知原因再赌同一条路；降级 Return 的残留风险 = 控件级焦点被别的控件抢走时键会落错）。改动 = 非 bg 鼠标分支**尾部**加"漏点处理"块（`window_by_title("attention")` 仍在 ⇒ `seen == 0` 时记 `popup_seen`、连发 `self.key("Return")`、按"还在不在"记 `popup_key_dismissed` / `popup_dismissed` / `popup_dismiss_failed`），**净 +24 行 / −0 行**、只碰清障路径（30 行硬闸未触）；**sha 轨迹 `87470aaff559` → `178591e19c40c37f` →（回退）`87470aaff559`**。
  ② **干跑 2 题即失败**（鼠标通道、`--tasks 2`、`--chaos 1.0 --chaos-kind popup`）：两题全 `NONE`、退出码 1、`popup_seen 13` 而 **`popup_dismissed` 与新增的 `popup_key_dismissed` 两个键在 `stats` 里根本不存在 = 13 次发现、0 次清掉**（`keys 45`、`replans 66`、`interferences 39`、`clicks 0`）⇒ 按终止条件**直接回退**，**A 批 / B 批都没跑**（同一段不试第二遍改动）。
  ③ **机制结论（比"哪条修法失败"更重要）**：非 `--bg` 通道里驱动发的按键是**真实前台按键**（Windows 把它交给前台窗口；只有 `--keys --bg` 才带 `focus` 焦点交接），而本机前台会被不断抢回 ⇒ 45 次按键**全部落空**；鼠标点击是**按坐标**投递的、弹窗又是 `-topmost` ⇒ 像素命中即可达。⇒ 该支**只剩"按坐标投递"这一种机制能到弹窗**；批次 14 的 10/11 因此不能读成"快好了"。
  ④ **收口**：`../sol/sandbox/SCORE.md` 批次 15 节（**未成批、只有逐字干跑**，`:1268–1349`）+ 本文 **§23** + §7 #20 行 ⚠ 第十四段块 + `HANDOFF.md` 盲区 23 ⚠ 第十四段块 + `../CHANGELOG.md`；报告 **v0.5 仅同步**（版本行、§5.1 第 15 行、§5.2 ④、§5.3 七类、§6.2 D、§7.2/§7.3、第 8 章、附录 A 行号重算 + **首次核对** `SCORE-history.md` / `DESIGN-refusal-scoring.md`、**新增附录 B-5**）。补丁留档 `D:\DSH\dsh-actor\tmp\w16-popup-key-fallback.patch`（35 行）；**仓库里没有本批任何证据 json**。提交链 `00e4396`（批次 15 文档）→ `3ae2b21`（报告 v0.5）。
  ⑤ **当段收工时的开工顺序（已被第十五段的 ④ 取代）**：**第一件 = 新会话验证技能目录注入**（`D:\DSH\skills\gui-audit-gym\SKILL.md`，每天早上第一件，先确认技能能被注入再谈别的）；**第二件 = 二选一**：按 `DESIGN-18-scroll-drag.md` §4/§5 在三方案里选一个（**推荐 C 为默认口径**；要真凭据则 A 前台鼠标批跑一次窄批 12–16 题；**B 不做**），或者按 **§23.4** 的收敛结论给 #20 做**通道层**选择（前台批并显式声明通道／给鼠标动作加托管输入与焦点交接／接受边界）；报告 **v0.6** 的待同步项见 §22.2 与 `REPORT.md` 附录 A。
- **第十三段（2026-10-05）：#20 修复尝试（选项 D）+ 报告 v0.4 + #18 设计 —— 裂了一次 sha 又回退**：
  ① **#20 选项 D 已实现、跑了一批、判据未过、按终止条件回退**：改动两处（非 bg 鼠标分支照抄隔壁 `if self.bg` 分支读**弹窗自己的窗口帧** + 点击**不带 `front_title`**；`shot_window()` 原点改用回包 **client origin**），净 **+26 行**、只碰清障路径（硬闸未触发）；干跑 `--tasks 2` = **2/2**、`popup_seen 2 / dismissed 2`；正式批（鼠标通道 `popup@0.35`、60 题）= **task 21 早停、退出码 1**、`popup_seen 11 / popup_dismissed 10 / popup_dismiss_failed 1` ⇒ 判据 `dismissed == seen` ❌、不早停 ❌ ⇒ **回退**，三件套回到 `66632d85eac8` / **`87470aaff559`** / `ef066713a03e`。**#20 仍开着**（失败面从"一次没点中"缩到"11 次漏 1 次"）。补丁留档 `D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`；B 批（回归）未跑（无可回归对象）。
  ② **三条下一步**（明天可直接挑）：(a) 清障后弹窗仍在 ⇒ **允许对同一点补点一次**；(b) 失败时**降级用 `key("Return")`**（app 自己绑定：主窗收到该键即关自己的对话框）；(c) 把 `gym_run.py:3460` 的"清障计数 ≠ 0 ⇒ break 去 replan"改成"**再清一次再 replan**"（拆掉"单次漏点 = 整题死锁"的耦合）。
  ③ 报告 **v0.4**（版本行、§5.2 ④ 补"尝试 + 回退"、附录 A 行号重算、附录 B-4 四问复查）；**`DESIGN-18-scroll-drag.md`** 落盘（#18 三方案 + 推荐 + 判据）。详见 `../sol/sandbox/SCORE.md` 批次 14 节 + 本文 **§21 / §22**。
  ④ **当段收工时的开工顺序（已被第十四段的 ⑤ 取代）**：**第一件 = 新会话验证技能目录注入**（每天早上第一件，先确认 `skills\` 下的技能能被注入再谈别的）；**第二件 = 二选一**：在 §22.1 的 A/B/C 里选一个（**推荐 C 为默认口径**；若要真凭据则用 **A 前台鼠标批**跑一次窄批 12–16 题；**B 不做**），或者按 §21 的 (a)(b)(c) 三条继续推 #20；报告 **v0.5** 的待同步项见 §22.2 与 `REPORT.md` 附录 A。
- **第十二段（2026-10-05）：#20 只读探针 + #18 读代码 —— 都不裂 sha、不改三件套、不动批次文件、未开代码线**：
  ① **#20 根因定案 = 两道独立门**。**(1) 看不见**：非 bg 分支读的是 **app 矩形屏幕抓帧**，驱动自己的 reader 在这一帧上**从没把按钮当候选** —— `_find_blocks` 在弹窗区给 **0** 块（`max_h` 抬到 400 / `max_frac` 0.95 / `solid` 0.6 **都无效**），词路径只读到散文里**小写**的 `dismiss`（`source text`、`fill_share 0.213`、`neighbours 7`）⇒ 被 veto 规则 `share < 0.45 and neighbours >= 2` 否掉 ⇒ **候选空、一次都不点**（`dialog_refused` 每帧 +1 = 批次 13-B 的 **28**）。**只有"弹窗自己的窗口帧"能干净读到按钮**（`box [188,104,96,48]`、`fill 1.00`、`label "DISMISS"`、`source block`、不 veto）—— 而 `dismiss_interference()` 里 `if self.bg` 那条分支读的**正是它**。**(2) 抢前台**：该通道的点击都带 `front_title` ⇒ `_maybe_front(front_top=True)` → `{"op":"window","mode":"top"}` = **pin TOPMOST**；实测真鼠标点按钮正中心 `[806,762]`（`how xy`、`click n1 left`、4.67 ms）**带 `front_title` ⇒ 弹窗不关**、**同一点不带 ⇒ 弹窗立刻消失**。
  ② **#18 读码结案 = 覆盖缺口、不是功能缺陷**：`wheel()` 在 `gym_run.py:1214`（**唯一调用点 `:2329`**）、`drag()` 在 `:1208`（**唯一调用点 `:2877`**），两条在键通道里**都有键盘等价物**（`Next`/`Prior`/`Up`/`Down`/`Home`/`End`；chips 的 `_bind_key` 拾取/落位）且**驱动已经在用**；`--bg` 下失效 = **Tk 忽略 posted 鼠标消息**（`gym_run.py:2329` 的注释早已写明）；**全仓没有任何批次 json 的 `drags > 0`**（`drags 3`/`drags 9` 出自 §16 的 P4/P5 = 鼠标 + 强制 `--bg`、0/3 早停）。
  ③ **三症状不是同一根因**：滚轮 + 拖拽 = **一个**根因（posted 鼠标消息被 Tk 忽略）；弹窗鼠标通道 = **另一个**（帧来源 + topmost pin）—— 修正了本段规格第三节的假设。
  ④ **下一步 = 本文 §20.4 的 A/B/C/D 四选一**（本段建议**先评估 D** = 非 bg 鼠标分支照抄隔壁 `if self.bg` 分支：读弹窗自己的窗口 + 点击别钉 topmost，约 **10–15 行**，**会裂 `gym_run.py` 的 sha**）；本段**未开代码线**。
  ⑤ 探针产物全在 `D:\DSH\dsh-actor\tmp\w14-*`（6 脚本 + 6 JSON + 5 帧 PNG，**不进沙箱**）；**`../sol/sandbox/SCORE.md` 未动**（探针不是批次）、`REPORT.md` 未动。详见本文 **§20** + `HANDOFF.md` 盲区 **23**。
- **最新一批（第十一段 2026-10-05）：批次 13**，两批 = **键通道 `popup@0.70` 成功**（`../sol/sandbox/t_trap2-w13-popup70.json`，**60/60**、`popup_seen/dismissed/failed 45/45/0`、`interferences 45` = 题内 27 + 题首 18、无早停、墙钟 250.9 s、`scripts_sha 186edbd9c024`）+ **鼠标通道 `popup@0.35` 失败**（`../sol/sandbox/t_trap5-w13-popup35.json`，**3 题早停、退出码 1**、驱动 `disturbances: 0 fired`、app 侧 `event blocked by modal` + `blocked 10`）⇒ 欠账 **#19 只关闭一半**（覆盖面 1 档 1 通道 → **2 档 1 通道**）、**新增 #20**（鼠标通道清障路径不生效）。**代码一字未改**（三件套 sha 与批次 12 相同），本段只动报告与文档。详见 `../sol/sandbox/SCORE.md` 批次 13 节 + 本文 **§19**。
- **批次 12（第十段 2026-10-05，`popup` 类 / 键通道 + `--bg`）**，`../sol/sandbox/t_trap2-w12-popup35.json`（**`popup` 类 / 键通道 + `--bg`**，**60/60**、`decided 100%`，口径 v2，`scripts_sha` **`186edbd9c024`**，wall **222.7 s**）—— 欠账 **#16「`popup` 打不掉」还清**：
  根因**不是**"UIA 看不见弹窗"，而是 **actor 折叠把 `data.windows` 截断**（`actor.py:_slim` 对 list 只留前 6 项左右）而 `window_by_title()` 当时**只读 `data`**（同一条回包的 inline 字段里明明有 11 项、含 `attention`）⇒ 闸门恒 `None` ⇒ **一次 Return 都没发**（批次 8 两批因此 `interferences 0`、各 1 次 fire 后早停）。
  改动 4 处、**24 行（+24 / −4，含注释）**、**判定路径一字未动**：① `window_by_title()` 与 ② `target_windows()` 改 **inline 优先**；③ 键分支加 `popup_seen` / `popup_dismissed` / `popup_dismiss_failed` 三计数；④ 等判定循环里清掉弹窗后**立刻 break** 走重答（被吞掉的按压不会补分）。
  实测：`popup_seen 24 / popup_dismissed 24 / failed 0`、`interferences 24`（15 题内 + 9 题首，计数闭合）、逐题 **60 行全 ok**、**无早停**、`false_refusal 0/46`、`gate_ms` P50 **127 ms**；其中 **12 题**走"被弹窗吞一次 → 重答"路径（逐题 ms 1748.6 vs 干净题 1639.5 ⇒ **+6.7%**）。详见 `../sol/sandbox/SCORE.md` 批次 12 节 + 本文 **§18**。
- **上一批定稿**：**批次 11**，`sandbox\t_trap7-1.json`（**鼠标通道 48 题**，**35/48**、`decided 100%`、口径 v3，`scripts_sha` **`8da029edccbc`**，json sha `dd77abc08e911794`）—— 欠账 **#17「`shot` 空帧零容忍」还清**：
  只改抓帧失败的处理（`ShotFailed` + `_shot` 重试 3 次 + main `try` ⇒ **已完成的题写成 partial run json** + 退出码 **3**），**判定路径一字未动**（`score.py` 只加两行 `!! PARTIAL RUN` 警示）；
  与批次 9（36/48）**逐项同协议同 seed** ⇒ **核心 14 = 12/14、翻转 0**、`ms/题 +0.9%`、`shot_empty / shot_retry = 0 / 0`；唯一翻转 `task_i 38`（`swap_race_timer`，**不在核心 14**）记为竞态族抖动（**未做重复批，引用前要补**）。详见 `../sol/sandbox/SCORE.md` 批次 11 节 + 本文 **§15**。
- **move 线定稿仍是批次 10**：`sandbox\t_trap2-w9-move70.json`（**`move` 类 / 键通道 + `--bg`**，**59/60**、`decided 100%`，口径 v2，sha **`5dedae26c6e8`**）—— 欠账 **#4 = §7 #15「守门每帧重算 banner box」还清**：
  只换守门的重读框（新增 `ask_box_now()` 每帧用**像素段**重算、不跑 OCR），**指纹基线 / 匹配路径 / 阈值 / `press_guard` 分支一字未动**；
  `ask_read_unreadable` **2 → 0**、`ask_box_recomputed 124 == ask_gates 124`（每门都重算）、同 `task_i` 无 ok→非 ok 翻转、`gate_ms` P50 **139 ms**（批次 9 = 124 ⇒ +15 ms，判据 ≤30 内）。详见 `../sol/sandbox/SCORE.md` 批次 10 节 + 本文 **§14**。
- **次新**：批次 9 `sandbox\t_trap6-1.json`（鼠标通道 48 题，**36/48**，口径 v3，`f473ff21ad09`）—— 欠账 **#10 / #11 还清**
  （`gate_ms` 扣掉抓帧后 P50 **124.1 ms**；逐题行 jitter 合计 **4501 ms == `stats`**），**判定逻辑一字未改**；与批次 6（`t_trap5-1.json`，`9db420c422a2`，37/48）**逐题同构**，
  只差 race 家族三题（#36/#44/#45；jitter 用未播种 `random` ⇒ 该族跨批不可复现）。详见 `../sol/sandbox/SCORE.md` 批次 9 节 + 本文 §12。
- **再往前**：批次 8 `sandbox\t_trap2-w8-move70.json`（`move` 类**对照批**，58/60，`f598406cfc70`）；批次 7 控制批 `t_trap2-w7-control.json`（`481154ca264d`，60/60，逐格等于批次 6 `w6c`）；
  批次 7 的 `t_trap2-w7-move70.json` ⚠ **不可引用**（修复前、33/60 早退）。
- **2026-10-05（探路日，不跑批、不改三件套）**：WSL 探测完成，结论写在本文 **§11** ⇒
  **放弃 WSL 做 GUI 靶场**（走 A 不可行：抓不了整屏 + 失焦后无任何 X 侧注入手段 + 到不了 actor `:8731`；
  走 B 技术成立但与现有 Windows 通道能力等价，代价是几何标定 + 三处辅助重做 + 字体差异致 OCR 需重调 ⇒ 数字不可比）。
  WSL 保留作**工具链**（`jq`/`rg`/管道：已用它独立复算批次 8 的 `chaos` fires 与 `trap_*`，与 `../sol/sandbox/SCORE.md` 逐项一致）。
- **技能已落盘（2026-10-05 13:57）**：`D:\DSH\skills\gui-audit-gym\SKILL.md`（10234 B；**项目级、非软链**；三块 = 必读前置 / 跑批与复核 / 口径与引用；数字一律指向 `../sol/sandbox/SCORE.md`/`STATE.md`/`HANDOFF.md`，技能里不存批次数字）。**阶段 3.3 更新**：三块正文已移入仓库、成为 `docs/OPERATING.md` 正本（中文），仓库外这份降为**指针**（只留 frontmatter + 一页顺序清单）—— 从此规程随仓库版本一起提交，不再有第二份会漂的副本。
- **技能验证（本会话，2026-10-05）三项全过**：①面板 list 由 15 → **16 条**，`gui-audit-gym` 在列（`provider=dsh-skills-manager-external`、`level=other:project-openclaw`、**`modelInvocable=true`**、`userInvocable=true`；清单存 `D:\DSH\dsh-actor\tmp\se_list2.json`）；
  ② frontmatter 显式写了 `disable-model-invocation: false`，与面板 `modelInvocable=true` 一致；
  ③ 本会话 `skill` 工具**当场解析成功**（返回正文 + `Base directory for this skill: D:\DSH\skills\gui-audit-gym`）⇒ 项目级技能根是活的，**不需要重载会话**。
- **明天第一件事：新开会话 → 验证技能目录注入 → 再决定接哪条主线欠账。** 本会话上下文里没有"技能目录消息"（工具与面板都正常，只剩"目录是否作为消息注入"这一项没法自验）；
  会话记录 `session.v4.jsonl.zstd` 是 zstd 压缩，直接 `rg` 的 0 命中不能当证据（先 `zstd -d` 再搜）。机制出处：`@deepseek-ai/dsh-skill` README.zh.md（注册表无 TTL；消费方 `dsh-tool-skill` 把 provider 摘要渲染成持久的初始目录消息，失效时追加替换目录消息）。
  若注入正常 ⇒ 在新会话里试一次"技能路由命中"；异常 ⇒ 排查技能中心 / skills-manager 插件层并记回本节。
- **今天第四段：把 #4 的"改"做完了（批次 10 定稿；只裂一次 sha）** —— 假设/证伪四条/观测点/判据写在本文 **§14.1–14.4**，改动三处写在 **§14.5 / §14.5b**，结果与判据核对写在 **§14.7**，本批唯一一次作废尝试写在 **§14.8**；
  过程一句话：`ask_box` 进题即冻结 ⇒ `move` 干扰下边缘切在 label 之前 ⇒ 守门重读只剩前缀（文本路径说"变了"、指纹说"没变"）⇒ 不放行 ⇒ 死锁；改成**每帧用像素段重算 banner box**（重算优先、失败退回冻结框），成本 **+8.71 ms/门**（场景匹配口径），60 题里读不出次数 2 → **0**。
- **明天第二件事（二选一）**：①**报告再下一轮（v0.3）** —— `REPORT.md` 现为 **v0.2**（第九段打磨已完成：第 2 章 11 条**已核对**外部引用、附录 A **带行号**、附录 B-2 四问复查、新增附录 C「复现指南」），可做的：与公开基准做同题对照、把行号改成**自动生成**、找同侪复核、**同步批次 12**（v0.2 里"`popup` 类测不了"的表述已被批次 12 推翻 ⇒ 第 6 章"能力缺口"那一族要改口径）；②或从 `HANDOFF.md` §6 挑一条欠账开工（现在**只剩** §7 #18 滚轮+拖拽，用户明示排在最后）。**#4 / #12 / #16 / #17 都已还或已关闭，都不要再重开**（证据冻结在 `../sol/sandbox/SCORE.md` 批次 10/11/12 节 + 本文 §13/§14/§15/§17/§18）。
- **今日第三段（2026-10-05，三件都不裂 sha、不改三件套）**：① `D:\DSH\vision-work\audit\SCORE-history.md`（**口径史一页纸**：v0–v3 四版表 + 10 条勘误/"勿引用" + 可比性判定六步 + 批族矩阵）
  ② `D:\DSH\vision-work\audit\REPORT-draft.md`（**报告框架**：标题 + 摘要 + 七章 × 3–5 个一句话要点 + 每章素材指针；**未写正文**）③ 本文 **§13**（#4 前置量：机制 + 成本 + 改法草案）。
- **今日新增欠账（未冻结）**：① 走 B 的坐标映射只做了定性；② 技能目录注入待新会话验证；③ 报告正文未写（框架已成，取材顺序见 `REPORT-draft.md` 附录）。
- **新增定式（批次 9 的教训；也写进 `../sol/sandbox/SCORE.md` 批次 9 ⑥ 与本文 §12.5）**：**跑批一律从 Windows 侧启动**，且显式正常显示状态 ——
  `Start-Process -FilePath D:\DSH\.venvs\vision-ci\Scripts\python.exe -ArgumentList "<sandbox>\gym_run.py", … -WorkingDirectory <sandbox> -WindowStyle Normal -RedirectStandardOutput <log>`；
  **先干跑 `--tasks 2`** 确认首题有真按压，再跑正式批。从 **WSL 后台作业**启动会让 app 窗口起在 `-32000`（离屏）⇒ 帧全空 ⇒ 0 次按压 ⇒ `gym_run.py:508 raise SystemExit("shot failed")`（白跑一次）。
- **第四段新增欠账 / 旧账（未冻结）**：① **§7 #17 `shot` 空帧零容忍**（第四段首跑因此白跑一次：一次空位图 = 整批退出 + **无 run json** + 逐题行全丢，见 §14.8；修法 = 短重试或记 `shot_retry`，属判定路径之外、**需单独一批**）；② `ask_box_shift_px` 只记每题"**首次**"重算 ⇒ **仪器局限**，证明不了门时那一帧的位移（要拿后者得记 max/分布，见 §14.7 ②）；③ B 路线坐标映射只做定性（§11.3）；④ 技能目录注入待新会话验证；⑤ **批次 9 判据 i 边缘未达**（`gate_ms` P50 与独立口径差 **10.58 ms**，目标 ≤10 —— 两者本就不是同一子集，未再挖机制）。
- **第五段新增欠账 / 旧账（未冻结）**：① **§7 #18 连续 / 视口类交互盲区（滚轮 + 拖拽）** —— v1–v3 覆盖 = 0，本段只"量"不改（八问逐条判定见 **§16**）：**1 条能 + 1 条代码级一致 + 6 条量不到**，原因是新发现的**能力缺口**（`--bg` 下鼠标通道不生效；滚轮/拖拽都只在鼠标分支）⇒ 状态维持 **欠（有据）**，要量得去前台鼠标批或给鼠标 op 加 focus/物理通道（改代码）；② 批次 11 的 `task_i 38` 翻转**未做重复批**坐实（属"竞态族抖动"的推断，不是已证）；③ "瞬时"类空帧**没能构造出来** ⇒ 重试分支在真实空帧下一次都没走到（`../sol/sandbox/SCORE.md` 批次 11 ⑦）；④ `ask_box_shift_px` 只记每题"**首次**"重算 ⇒ **仪器局限**，证明不了门时那一帧的位移（要拿后者得记 max/分布，见 §14.7 ②）；⑤ B 路线坐标映射只做定性（§11.3）；⑥ 技能目录注入待新会话验证；⑦ **批次 9 判据 i 边缘未达**（`gate_ms` P50 与独立口径差 **10.58 ms**，目标 ≤10 —— 两者本就不是同一子集，未再挖机制）。
- **第六段：把 #12（`guard-blind` 分母）量完并关闭（只量不改、不裂 sha）** —— 读码结论与假设写在 **§17.1–17.3**，跑批命令 **§17.4**，结果与判定 **§17.5**；一句话：`--keys --bg` 20 题 `t_trap5` ⇒ `blind_seen = 0`、events `trap_stale_press = 0`、`swap_hard_timer` 5/5 全 ok，且 `task_i 13` 在**指纹 `ask_cells 0`** 时仍被**文本重读**（raw `_plain` 比较）抓住 ⇒ 单字形换题自批次 4/5 起已被文本路径覆盖、判据"漏判时给分母"不再成立 ⇒ **关闭·已量**（`../sol/sandbox/SCORE.md` 不动、三件套一字未改）。
- **第七段：报告正文初稿写完了（只写文档，不裂 sha、不碰三件套、不动任何批次文件）** —— 落盘 `D:\DSH\vision-work\audit\REPORT.md`（**353 行**，初稿 v0.1；1 引言 / 2 相关工作 / 3 方法论 / 4 系统 / 5 实验 / 6 发现 / 7 讨论 / 8 结论 + 附录 A 数字索引 + 附录 B 逐章自检）；
  `REPORT-draft.md` 同步修订（**101 → 129 行**：新增 **`## 0. 写作原则`**（五条 + 每章自检四问），章节由 7 章扩为 **8 章**——新增独立第二章「相关工作」（原 2–7 顺延为 3–8），摘要与状态行由"批次 1–9"更新为"**批次 1–11 + 三组只读探针**"，§6 盲区数由 17 改为 21，附录取材顺序加第 5 条（第 5 章只写转折、第 6 章只写结论）；**原 `REPORT-draft.md` 未删**。
  正文遵守五条原则：**数字一律指向 `../sol/sandbox/SCORE.md`（不复制任何通过率/分母/毫秒——`grep` 校验只命中章节引用）、口径版本集中定义并逐行标注、每章带"诚实边界"、做到与没做到各写一半、每章首句回答"本章回答什么问题"**；六条可引用结论各带"成立工况"，21 条盲区归纳为五族（感知与文本 / 竞态与时序 / 记账与仪器 / 能力缺口 / 环境与几何）并逐族标"对主结论的影响"，第 6.3 节用三个例子说明"盲区可以被量到结论"（修好了 / 量到它不存在 / 把丢证据改成留证据）。
- **第六段新增欠账 / 旧账（未冻结）**：① #12 的结论**只在键通道量过**（鼠标通道共用 `press_guard`，但受 `--bg` 鼠标缺口限制未复测）；② 样本只 1 批 20 题（家族 5 题），未重复；③ **§7 #16（`popup`）与 #18（滚轮 + 拖拽）仍未动**；④ `ask_box_shift_px` 只记每题"**首次**"重算 ⇒ 仪器局限（§14.7 ②）；⑤ B 路线坐标映射只做定性（§11.3）；⑥ 技能目录注入待新会话验证；⑦ 批次 9 判据 i 边缘未达（`gate_ms` P50 与独立口径差 **10.58 ms**）。
- **第七段新增欠账 / 旧账（未冻结）**：① **第 2 章（相关工作）没有任何外部引用**——规格要求"不引未核对文献"，故留作待办；② 附录 A 的"数字索引"只到**节名**不到行号/锚点（引用仍需人工对齐）；③ 报告正文**未做同侪复核**（自检表是自己填的）；④ 上述第六段 ④–⑦ 四条全部照旧。
- **第八段：`vision-work` 建了独立公开仓库并推送完成**（只加文件；未改三件套、未删任何文件、未动任何批次文件）—— 仓库 **https://github.com/Maopk/vision-work**（public，默认分支 `main`，MIT 已被 GitHub 识别），首次 commit **`9bc567d297fcf95854264a92e6d5f0d9447b4df9`**（信息 `initial: GUI audit gym (batches 1-11, 口径 v0-v3)`；**102 个文件 / 5.3 MB**）。
  格式**对齐参考** `dsh-vision-kit`（分支 `main`、MIT、双版 README、Keep a Changelog、小写 `scope: 祈使句` 的 commit 风格）与 `dsh-termux-kit`（本地副本 `D:\DSH\dsh-termux-kit-copy`，远端默认分支 `master`）；**不对齐**：CI 工作流、`mypy.ini`、`ruff.toml`、`CONTRIBUTING.md`、`requirements-dev.txt`（应用层不引入工具层）。
  入库 = 三件套 + `gui_see.py` + `loop.py`（`gym_run.py` 里 `from loop import Actor`，不带它跑不起来）+ 42 个 `probe_*.py` + **43 个批次证据 `t_trap*.json`** + 四份文档（`../sol/sandbox/SCORE.md` `STATE.md` `HANDOFF.md` `DESIGN-refusal-scoring.md`）+ 报告三件（`REPORT.md` `REPORT-draft.md` `SCORE-history.md`）+ `../README.md`/`../README.zh-CN.md`/`../CHANGELOG.md`/`../LICENSE`/`../.gitignore`；
  **排除** = `*-events.jsonl`（最大 12 MB）/ `*-state.json` / `*.png`（含本机 UI 截图）/ `*.log`·`*-out.txt`·`*.err` + 与判分线无关的历史材料（蜘蛛纸牌、QQ、爱心、几何实验等；**只在 `.gitignore` 里声明，未删除任何文件**）。`.gitignore` 以**显式路径**为主；sandbox 那段 = 先忽略 `sol/sandbox/*.json` → `!sol/sandbox/t_trap*.json` 放行批次证据 → 最后重新排除 `t_trap*-state.json`。
  **脱敏**（本段唯一的文字改动，共 3 处）：`STATE.md` 两处 + `../sol/sandbox/SCORE.md` 一处，把"前台窗口标题 = 具体页面标题"改成通用描述（"用户前台窗口" / "另一个应用的窗口"）；hwnd、数字、结论一字未改；验证 `grep -n "Chrome|浏览器|DeepSeek 窗口" STATE.md HANDOFF.md ../sol/sandbox/SCORE.md` ⇒ **0 命中**。
  推送细节：`~/.ssh` 为空 ⇒ remote 用 **HTTPS**（`https://github.com/Maopk/vision-work.git`；规格里写的 `git@github.com:` 无密钥必然失败）；WSL 里 `127.0.0.1:7897` **不通**（那是 Windows 侧监听，进程 = verge-mihomo pid 29176），可达的是 **WSL 默认网关 `172.31.96.1:7897`** ⇒ 仍按规格**走代理**，只是换了地址；token 走 `http.extraheader` 逐次传入，**未写进 `.git/config`**。
  推送后核验：远端 blob **102 == 本地 102**、`raw` 取回的 `gym_app.py`/`gym_run.py`/`score.py`/`gui_see.py`/`loop.py` 的 sha256 与本地**逐字节一致**、`.png`/`.jsonl`/`-state.json`/`.log`/`.txt`/`__pycache__` **0 命中**、无关历史材料 **0 命中**、12 个顶层文件与文档全部 HTTP 200、远端 `refs/heads/main` = 本地 HEAD、GitHub 页面认定 `README.md` 为仓库 README（5283 B）。
- **第八段新增欠账 / 旧账（未冻结）**：① **报告打磨未做**（第 2 章外部引用 / 附录 A 升级为带行号 / 按附录 B 四问复查）⇒ `REPORT.md` 仍是 **v0.1**；② 仓库**有意不配 CI**（应用层决策）；③ 后续推送仍需带 token 头（**未做凭据持久化**，避免把 token 落盘）；④ 上述第七段 ①–③ 与第六段 ④–⑦ 全部照旧。
- **第九段：报告打磨 v0.1 → v0.2（只改 `REPORT.md` + `REPORT-draft.md`；不裂 sha、不碰三件套、不动任何批次文件、不删任何文件）** —— 四处改动：①**第 2 章补 11 条已核对的外部引用**（Sikuli UIST 2009 / GUI Testing CHI 2010 / RERAN ICSE 2013 / WebArena / Mind2Web / WebVoyager / OSWorld / *An Illusion of Progress?* / reject-option 综述 / selective classification / refusal direction；**逐条打开核对过标题+作者+年份+可查链接**，核不到的一律不引）；②**附录 A 升级为带行号引用**（`../sol/sandbox/SCORE.md:7–33` 这种；含行号口径与"文件一改就漂"的说明）；③**附录 B-2**：v0.2 逐章四问复查表 + **发现并改掉的三处问题**（版本行把 #17 误称"探针"、§7.3 第 4 项与本轮重复、"不做文献综述"与新增引用冲突）；④**新增附录 C「复现指南」**（环境三件事 / 跑批骨架 / 四件留档 / 引用前四步手续；**只整理、不新增实验、不含任何成绩数字**）。**干扰鲁棒性那一小节没有可核文献 ⇒ 明写留空**，不用"已有大量研究"带过。
- **第九段新增欠账 / 旧账（未冻结）**：① 报告**仍无外部同题对照**（第 2 章是差异说明，不是综述）；② 附录 A 行号**人工对齐**，文件一改就漂（§7.3 第 4 项后半"自动生成"仍开放）；③ 报告**未做同侪复核**（附录 B 自检表仍是自己填的）；④ 上述第八段 ②–④、第七段 ①–③、第六段 ④–⑦ 全部照旧。
- **第十段新增欠账 / 旧账（未冻结）**：① **§7 #19 `popup` 只跑了 1 档 1 通道**（`0.35` + 键通道 + 1 次；`0.70` 档与鼠标通道无修后数据；与批次 8 是历史产物对照、无同批 A/B）；② `REPORT.md` 里"`popup` 类测不了"的表述**已被推翻但未同步**（`REPORT.md:237` + 附录 A 索引 `:347`，见 §18.4 ⑤）；③ 报告**仍无外部同题对照**、附录 A 行号仍人工对齐、**未做同侪复核**；④ 上述第九段 ②–④、第八段 ②–④、第七段 ①–③、第六段 ④–⑦ 全部照旧。
- **第十一段（2026-10-05 收工）：报告 v0.3（改正 `popup` 表述）+ `popup` 覆盖面补测（#19）；三件套一字未动** —— ① **报告 v0.3**：`popup` 从"这一类在当前通道下不可测"改正为「**键通道两个强度档可测（批次 12/13）、鼠标通道仍不可测（新欠账）**」，同步第 1 章边界句、§5.1 迭代表（新增第 12/13 行）、§5.2 ④、§5.3（第五类失败批）、§6.2 D 族（21 → 22 条）、§7.2、§7.3 第 1 项、第 8 章"还剩"句、`:328` 边界（两条 → 三条欠账）、附录 A 各行与行号口径注，并**新增附录 B-3**（本轮四问复查）；`REPORT-draft.md` 顶部加 v0.3 修订说明并同步三处 `popup` 点。**改动清单**：只碰报告事实错误、不新增实验、不新增引用。② **批次 13**：`--keys --bg` + `popup@0.70` **成功**（`../sol/sandbox/t_trap2-w13-popup70.json`，**60/60**、`popup_seen/dismissed/failed 45/45/0`、`interferences 45`、无早停、墙钟 250.9 s、`scripts_sha 186edbd9c024`）；鼠标通道 `popup@0.35` **失败**（`../sol/sandbox/t_trap5-w13-popup35.json`，**3 题早停、退出码 1**、驱动 `disturbances: 0 fired`、app 侧 `event blocked by modal` + `blocked 10`）⇒ **#19 半关闭**（覆盖面 1 档 1 通道 → **2 档 1 通道**）+ **新欠账 #20**。③ 文档落位：`../sol/sandbox/SCORE.md` 新增「批次 13 结果」整节（13.1–13.5）、`HANDOFF.md` 盲区 17 补测块 + §5 证据两条 + §6 表第 13 行注记 + 本表 §7 #19/#20、`../CHANGELOG.md` `### Added`/`### Changed`。④ 未做（本段无时间）：规格 §四的 #18 先读代码。⑤ 三件套 sha 与第十段收工**完全一致**（`gym_app.py 66632d85eac8` / `gym_run.py 87470aaff559` / `score.py ef066713a03e`）。
- **主线仍悬着的那一件**：从 `HANDOFF.md` §6 挑一条（**#4 / #16 / #17 已还清、#12 已量完关闭，都跳过**）—— 现在**只剩两条**：**§7 #18 滚轮 + 拖拽**（新题型 + `--bg` 鼠标通道缺口，用户明示排在所有欠账之后）与 **§7 #20 鼠标通道 `popup` 清障**（第十一段新记；**第十二段已定案 = 两道门**：该通道读的那一帧里按钮从来不是候选 + 点击带的 `front_title` 把 app 钉成 topmost ⇒ 修法见 §20.4 选项 **D**，约 10–15 行、**会裂 sha**；而 **#18 已读清** = 键通道**都有键盘等价物**、驱动已经在用 ⇒ **覆盖缺口、不是功能缺陷**。两者**不是**同一个根因，别再把它们当一件处理）。
  非批次类的那一件是**报告正文**（`REPORT.md` 现 **v0.3**；框架 `REPORT-draft.md` **133 行**，取材顺序在它的附录；写它不裂 sha、不动三件套）。**报告 v0.3 已改完**：`popup` 从"这一类不可测"改正为"**键通道两个强度档可测、鼠标通道仍不可测**"（本段唯一的事实改正）。
- **开工前必读**：本文件开头 + `HANDOFF.md` §2（口径）与 §4（已知盲区 **23** 条；第十二段新增盲区 **23** = 非 bg 鼠标通道点不到独立弹窗的两道门）+ 本文 **§20**（第十二段：探针做法、#20 两道门、#18 读码结案、A–D 四选项、边界、教训）；动报告时再读 `REPORT-draft.md` **§0 写作原则** + `REPORT.md`（**v0.3**）+ 它的附录 A（带行号）/ 附录 B-2（四问复查）/ 附录 C（复现指南）。**仓库已在 https://github.com/Maopk/vision-work**（公开，首 commit `9bc567d`，2026-10-05 推送；README 双版 + `../CHANGELOG.md` + `LICENSE` + `.gitignore` 都在仓库根）。
- **开工前必查**：venv `D:\DSH\.venvs\vision-ci\Scripts\python.exe` 可用；actor 守护进程在（`:8731`，**第十二段采样 pid 12008、uptime 9587 s**；`act.py ping` 一句话可查）；
  `foreground` 当前状态（收工时未锁屏；**同一时刻只能有 1 个 gym 窗口 ⇒ 各批串行**）。
- **本日状态（2026-10-05 收工）**：**第十一段已收工**（报告 v0.3 + 批次 13：`0.70` 档键通道 ✅ / 鼠标通道 ❌ ⇒ 新欠账 #20；**代码一字未动**；见本节上方 bullet 与 §19）—— **第十段已收工** —— ① 报告 **v0.2 已提交推送**（commit **`b08243bb0130a942c945c100a429e205024be512`**，远端 HEAD 同 hash；远端 `REPORT.md` **446** 行 / `../README.md` **92** 行核过）；② **欠账 #16（`popup` 打不掉）还清**并定稿 **批次 12**（根因 = actor 折叠截断 `data.windows`；`gym_run.py` `105cf6cb679eea10` → **`87470aaff559`**，+24/−4 行，判定路径一字未动；`popup_seen/dismissed/failed = 24/24/0`、60/60 无早停）；**第九段已收工** —— 报告打磨 **v0.1 → v0.2**（`REPORT.md` **353 → 446 行**：第 2 章 11 条**已核对**外部引用 + 附录 A **带行号** + 附录 B-2 四问复查 + **新增附录 C「复现指南」**；`REPORT-draft.md` **129 → 132 行**同步修订；**只改这两份文档**，三件套、批次文件、仓库文件一字未动）；第八段 —— `vision-work` 已推成独立公开仓库 **https://github.com/Maopk/vision-work**（首 commit `9bc567d297fcf95854264a92e6d5f0d9447b4df9`，102 文件 / 5.3 MB，MIT；未删任何文件、未改三件套、未动任何批次文件）；第七段 —— 报告正文初稿 `D:\DSH\vision-work\audit\REPORT.md`（**353 行**：8 章 + 附录 A 数字索引 + 附录 B 逐章自检）完成；数字一律指向 `../sol/sandbox/SCORE.md`（未复制任何通过率/分母/毫秒），**未裂 sha、未动三件套、未动任何批次文件**；**三件套 sha 与第六段收工完全一致**（`gym_app.py 66632d85eac81c12` / `gym_run.py 105cf6cb679eea10` / `score.py ef066713a03eb940`）；
  此前：第六段 #12（`guard-blind` 分母）量完并**关闭**（探针批 `D:\DSH\dsh-actor\tmp\w12-trap5-keys20.json` + 留档 `w12-events-archive.json`；`../sol/sandbox/SCORE.md` 未动）；批次 11 定稿（`gym_run.py` `105cf6cb679eea10`、`score.py` `ef066713a03eb940`）、#17 还清、#18 只量不改（探针产物全在 `D:\DSH\dsh-actor\tmp\`）；
  批次 8 的四类 chaos 结果已入 `../sol/sandbox/SCORE.md` 与本文 §10.4；`popup` 类不可测（欠账 #16）、`a_hit` 未达标如实记录（不硬推）、`shot` 空帧零容忍（#17 已还）。

## 0. 用户铁律与新方向
- **「你切记，不要背答案」**（2026-10-03 晚）—— 练习靶/实战一律靠**实时读屏**决策：不读 app 状态文件的 `truth`、不硬编码答案、不把真值喂进任何决策路径。状态文件只允许**评分**用（`ask`/`scenario`/`task_i`/`result`），真值只在诊断（probe）里出现，不得回流。（曾把 `truth` 记进失败记录，已回退。）
- **「要训练实时应变能力的 skill」** —— 靶子会**在运行中变化**：值被改（rebuild）、控件移位（move）、弹窗干扰（popup）、判定延迟（slow），逼驱动重新看屏、重算。
- **机器是用户的**（m03132）：训练必须走**后台通道**（不抢前台），每轮结束核对 `foreground unchanged: True`。用户还点名过：清干扰**不要点弹窗里的正文**，要点/按到真正的 DISMISS。
- 既有三要求（m01903）：题目**随机**、速度**要快**、靶子**通用**。

## 1. 现在能跑什么
| 角色 | 文件 | 说明 |
|---|---|---|
| 练习靶（被测 app） | `sandbox\gym_app.py` | tkinter，6 类随机题 + chaos 四类；状态 `gym-state.json`、事件 `gym-events.jsonl`；CLI：`--seed --state --events --scenario --gap --chaos --chaos-ms --chaos-kind --no-topmost` |
| 驱动（全盲） | `sandbox\gym_run.py` | 只看像素：截屏 → OCR → 鼠标/键盘 → 读回校验；**从不读 `truth`** |
| 视觉底板 | `sandbox\gui_see.py` | `read_box/words/components/group_lines/norm/find_text/char_boxes` |
| 常驻执行器 | `D:\DSH\dsh-vision-kit\actor\`（:8731，HOME `D:\DSH\dsh-actor`） | `run` 一次跑完「看→动→验」；`window mode=focus` 可把键盘焦点交给靶子**而不动前台** |

跑测命令（一行可复制，全部后台键盘通道）：
```
cd D:\DSH\vision-work\sol\sandbox && D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --tasks 60 --seed 20251007 --keys --bg --max-repeat 3 --json-out mix60f.json
cd D:\DSH\vision-work\sol\sandbox && D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --tasks 20 --seed 20251007 --chaos 0.5 --chaos-kind rebuild --keys --bg --max-repeat 3 --json-out chaos-rebuild.json
cd D:\DSH\vision-work\sol\sandbox && D:\DSH\.venvs\vision-ci\Scripts\python.exe score.py mix60f.json chaos-*.json
```

## 2. 成绩（都是实测，seed 20251007，`--keys --bg --max-repeat 3`）
- **干净盘混合 60 题 = 59/60（98.3%），2612 ms/题**：
  `t_button 10/10、t_chips 10/10、t_form 9/10、t_menu 11/11、t_rows 9/9、t_toggle 10/10`。
- **单场景**：`t_rows 12/12`（2693 ms/题）、`t_form 13/14`（5214 ms/题）、`t_menu 7/7`（2605 ms/题）、`t_chips 10/10`、`t_toggle 8/8`、`t_button 1/1`。
- **唯一的干净盘失分**是屏幕本身有歧义的字形：app 生成 `C02S`（数字零），banner OCR 读成 `CO2S`，app 精确比对判 WRONG。**故意不绕过**（不读状态文件的真值）。
- **chaos 四类（`--chaos 0.5`，一类一轮，20 题）**：

  | kind | 得分 | 用时 | 破在哪 |
  |---|---|---|---|
  | rebuild | **2/6 (33%)** | 2561 ms | ask 被重掷：驱动**读到了新 ask**，却点了错控件（要 `mica36` 点了 `PRISM11`，模糊匹配假阳性）；t_rows 里行表/提示字母整体换位后按键不再得分 |
  | move | 17/20 (85%) | 2114 ms | 布局在拖动中途平移 |
  | popup | **4/7 (57%)** | 1671 ms | 干扰窗出现后 ask 读残（`invoke the ONYX > Indigo menu`），`act=unknown` |
  | slow | 18/20 (90%) | 2796 ms | 判定迟到 1.5–3.2 s，重规划后重复点击被判 WRONG |
- 六场景 ask 原文（驱动正则必须匹配）：
  `click the button labelled %s` / `select the row whose id is %d` /
  `fill A = V and B = V then press GO` / `set %s ON|OFF and the slider to %d` /
  `invoke the menu %s > %s` / `drag chip %d into slot %s`。

## 3. 关键实现要点（别重新踩）
- **banner/ask 读取（`Driver.chrome`）**：暗像素占比 `.55` 的**连续**行块 = banner（只取从首个暗行起的连续暗行，避免把下方浅色状态栏并进来）；文本行 = 非暗像素 `>6` 的行分组；**左边缘 14 px 必须裁掉**（有会被 OCR 成 `3` 的伪影）；长 ask 会换行，`DO` 行之后的同块行要拼成一条 ask。
- **后台键盘通道**：`--keys --bg` 全程不抢前台。要点：①Tk 会丢弃未聚焦窗口的投递按键 → 每次 `do_task` 前 `window mode=focus`（AttachThreadInput+SetFocus，不动前台）；②靶子自己**不能** `focus_force()`；③等判定要 `judge_wait` 轮询 state（0.08 s 步进，**不截屏**），比再跑一次全身 OCR 快 2 s+。
- **banner 值回读竞态**：`Escape`（清空）与随后 `type_text` 的字符走**不同队列**，清空晚到会吃掉首字符（实测 `MLWI` → `LWI`）→ 每个字段填完**读回**，不符就 `Escape`+`BackSpace 12`+重打一次（**不要**用 `Home`/`Delete` 去"修"多余字形，实测把它从 13/14 打到 7/14）。
- **形近字**：`_code()` 折叠 O/Q→0、I/L→1、S→5、B→8、Z→2、G→6、T→7、A→4（chips 槽码用）；`_form_pairs` 对表单值**不折叠**（要输入的字符必须逐字对）。t_form 的值 token 曾用「逐字符 makebox + 字形宽高比」纠正，实测更差（13/14→10/14），已回退并把负结果写进 `Driver.glyph_read` 的注释。
- **t_rows 提示徽章**：裁 `(bx-84, by-8, 44, bh+16)`、whitelist `SCAN_KEYS+"[]()<>"`、psm 7；**旧的 (bx-92,…,88) 宽裁剪会把右侧黑竖条一起 OCR，全是垃圾**。
- **Tk 经典 Scale**：点槽是**相对步进 ±1**，不是跳到点击位置，点控件外无效；做法＝先读值 → 相对步进 `|差|` 次 → 重读校正（≤3 轮）。**这是用户看屏幕点破的**。
- **滚轮单位**：actor 的 `scroll(dy)` 直接进 `MOUSEEVENTF_WHEEL`（一格=120）→ `dy = notches*120`。
- **chips/slots**：chip 数字＝灰度 `L>185` ∩ 内切圆（`0.47·min(w,h)`）后 OCR（psm 7/10、scale 3）；槽码 13 px 要 `scale=2` 读；以槽码为锚匹配，落点＝标签框底 +26 px。
- **写盘竞态（app 侧已修）**：`os.replace` 撞上驱动的读句柄会 `PermissionError`，而 `emit` 是 `_on_key` 第一行 → 异常吞掉按键（假故障「Home 总能到、数字键从来没到」）。现在 `write_state()` 重试 6 次后退化为直接覆写，`emit` 全程 `try/except OSError`。
- **防呆**：`--max-repeat 3`；题没做对时靶子不前进，一个坏分支会吃掉整轮题数。
- **工作方法**：同一处连续失败两次就停下 **dump 原始像素/坐标**（行剖面、连通域、crop 图、离线给候选打分的探针），按量到的结构写规则。靠"猜阈值→跑一次"曾在一处连崩 7 轮。

## 4. 下一步（优先级从上到下）
0. **拒绝计分这批（放行 r3）—— 已实跑收口**：设计见 `D:\DSH\vision-work\audit\DESIGN-refusal-scoring.md`（§3 靶子 → §1 口径 → §2 标注 → §4 fire 计 → §5 竞态 → §6 profiling 全部落地并实测；顶部"落地状态"表 + 修订 r5）。
   - **`t_trap` 24 题 × 4 次：18/24 → 24/24 → 24/24 → 24/24 → 24/24**（`t_trap-1/3/4/5/6.json`、`prof3.json`）。v1 行：`24/24 100%  decided 100%  false_refusal 0/16  false_accept 0/8  swapped 3  a_hit 0  replan 3`，分变体全 `1/1` 或 `2/2`（`prose_with_button 2/2`、`synonym_button 2/2`）。
   - 两处修（r5）：① 匹配器选中**正文里的同名词**（无 `[k]` 徽章）就直接拒答 ⇒ `find_all` + `try_other_occurrences`（只试带徽章的其他出现）；② `swap` 改 ask、控件不动 ⇒ `band_sig`/`ask_changed` 在复验那一帧比对 ask 框指纹（**均值阈值 12 漏判**，实测均值 3.7/9.2/5.7 ⇒ 改"变化格数 ≥3"）。
   - 跑测**必须用 venv 解释器**（PATH 上的 `python` 现在是 C:\Python314，没 numpy/PIL）：
     `cd D:\DSH\vision-work\sol\sandbox && D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap --tasks 24 --seed 20251007 --keys --bg --max-repeat 3 --json-out t_trap-N.json`，再 `... score.py t_trap-N.json`。
   - profiling 已重跑：`prof2.json`（12 题混合）= **3658.1 ms/题**，对比 `prof1.json` 3552.6 ⇒ **+105.5 ms/题（+3.0%）**，§6.1 设计时估的 +22 ms 已作废（`find_blocks` 活体每次约 75 ms）；`prof3.json`（24 题 t_trap）= 1921 ms/题 —— 比混合集**便宜**（新题型全是按钮/正文，OCR 次数少），"t_trap 每题多花多少 ms"这个提法本身不成立，实际贵的是**重规划**（3 题各 +1.4 s）。
   - **批次 1（`t_trap` 24 题）的已知盲区 —— 24/24 连五次是"题太简单"，不是"系统对了"**：
     a. `swap_mid_task` 三次换题全在**按键之前**（`a_hit=0`）⇒ "A 做对了、屏幕随后才变"这条路径
        **从未被测到**（设计 §5.2 三种情况里的第一种，也是最该测的一种）；
     b. `half_transparent` 三档（0.35/0.50/0.65）全部照点通过 ⇒ 这批**没测到任何阈值**：
        控件能不能点由 `[k]` 提示徽章 + 标签决定，不由填充率决定（0.35 就是这么过的；换题
        前后 `ask_cells` 那类证据才真正决定成败）；
     c. 每类只有 3 题 ⇒ 命中率只有 0/33/67/100 四档，任何"某类全过"都没有统计意义。
     ⇒ 批次 2 `t_trap2`（85 题、每类 ≥10）专治 a/b：`swap_after_press`（换题是"按下 A"的**后果**）
     + `alpha020`/`alpha030`（低于正文自身的 0.213）。跑法：
     `D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 85 --seed 20251007 --keys --bg --max-repeat 3 --json-out t_trap2-N.json`。
   - **批次 2 `t_trap2`（85 题）已跑完：v1 83/85 = 97.6%**（`t_trap2-3.json`；`answered_right=55
     wrong_target=2 refused_right=28`、`false_refusal 0/57`、`false_accept 0/28`、`decided 100%`）。
     - **`a_hit` 第一次非 0**：`swap_after_press` 10/10（`a_hit=10 wrong=0`）⇒ 设计 §5.2 第一种情况
       （A 对 + B 对 ⇒ 通过 + `a_hit=1`）首次实测；第二种（A 对 + B 错）**仍 0 例**，别当已验证。
     - `swap_timer` 5 题里 2 题错（#10/#13，`ask_cells=1/0`）⇒ 换题落在**复验帧与按键之间**的残留竞态；
       `a_hit=0` 是结构性的（换题早于任何按键）。**已从靶子事件流取证**：`trap_swap a=INDIGO b=XENON why=timer a_hit=False` → `done detail.clicked=INDIGO`。新增事件 `trap_stale_press` + 计分行 `race(pressed the replaced ask) N/M`（`score.py` selftest 29 项）；旧 run 显示 `0/0` 只表示"当时没有这个字段"。这条**不从分母里剔除**：看着没变就按下去是真实边界（窗口 70–150 ms）。
     - `half_transparent` 五档（0.20/0.30/0.35/0.50/0.65）**各 2/2 全过 = 无区分度·不可作为 fill 阈值证据**（用户审计要求这样标，不能写成通过）：键通道下
       能按下去的前提是找到 `[k]` 徽章，**操作性与填充率无关**（真正的机制：靶子只把**填充块**按 alpha 混合，`gym_app.py:931-943`；标签文字与 `[k]` 徽章**没过 blend**，见 `gym_app.py:933-945` 的 `create_text(..., fill="#12263a")` ⇒ 五档里可读的东西完全一样，**该类在结构上产生不了 fill 边界**）。另一条更便宜的路：让文字也走 `blend`，同批 10 题重跑，测的是驱动读数下限；要测阈值必须做"淡控件 + 无徽章"变体。
     - `2330 ms/题` 是 `wall_ms`（含抓图）均值，判定耗时均值只有 1148 ms；按类拆开：`swap_after_press` **6233 ms/题 × 10 题 = 整轮 198 s 的 31.4%**，其余每类 1.5–2.7 s ⇒ 差别全在这 10 题（按对 A 后靶子换题，驱动等一个**永远不会来的判定**约 5 s：`wait_verdict(..., 0.6)` → "no verdict in 4.4 s"）。**下一批可优化**：等判定时顺带比对 banner 指纹（复用 `band_sig`，不额外抓帧）能省掉这 ~5 s。
      - 每个 run json 都带 `scripts_sha`（`gym_run.py`+`gym_app.py`+`score.py` 三个文件）：`t_trap-1..6` 六版各不相同（`a04562c5`/`1a3c8993`/`31a244a3`/`03bf345d`/`918619ef`/`ea755d12`）、`t_trap2-1`=`82f71c8f`、`t_trap2-2`=`5829c8b9`（这两次 `gates` 还被错写成 v0）、定稿 `t_trap2-3`=`f09f2ed21363`、`prof2`/`prof3`=`264a87d48d4c`；跨版本的数字不可直接比，引用要带 sha。
      - `screen 69/85` **不是 16 题屏读失败**（审计疑点，已核对）：判据是**归一化后的屏读文本是否包含真值**（`gym_run.py:1498`），不包含才记 `file`，而行动**仍用屏读文本**（`gym_run.py:1504` 只在屏读为空时才回落文件）。那 16 行全是 OCR 滑字（`GAMM.`/`TUND`/`XENON2`/`acknowledae`），逐题核对 = **10 题 acted + 6 题 refused、16/16 `result=ok`**。
      - 这批暴露并修掉的三个驱动 bug：同义动词命中正文就拒答（改：只接受带徽章的命中，继续试下一个
       同义词）、`SYNONYM_ACT` 缺 "acknowledge"（补 + 动词匹配容错一位 OCR，实测屏读 `acknowledae`）、
       ask 解析不出来时**冻结**（改：拒答 + `ask_unparsed=1`；此前它会让 `--max-repeat 3` 砍掉整批）。
    - **批次 3 `t_trap3`（71 题计划，鼠标通道 / 前台真实鼠标）已跑：`t_trap3-2.json`、`scripts_sha 2f4bad88da13`、
      v1 45/62 = 72.6%（`decided 100%`、`extra_attempts 2`），实际只跑 64/71**（第 61–63 题同义词类连续三行
      `NONE` 触发 `--max-repeat 3`；原因是**声明边界**"D1 量淡 vs 强、不量控件 vs 正文"——正文里的 "Close" 被量到
      **D1=98** ⇒ 点正文、无事发生）。
      - **`by_alpha`（用户第一组数）**：0.20/0.30/0.35 各 3 拒对、0.44 **5 拒对**、**0.46 恰好 5/5 误拒**（跑前
        预测被压中 = 边界带预期误拒，不是回归）、**0.50 3/3 误拒**（预测"0.50 起可点"未中 ⇒ **有效门槛在
        (0.50, 0.65]**）、0.65 与 1.00 各 **3/3 答对**（曲线 1 的 OCR 中间带空洞**未复现**）。28 题的 D1 排序
        `40…65 | 70…125`，**66–69 之间为空**、拒答最大 65、点击最小 70 ⇒ 规则执行零例外；另有 3 题拒答理由是
        `no control carries the asked label`（都在低 α 档）⇒ **"读不到"与"看不见"是两条路径**。
      - **`a_hit_but_failed = 0`（用户第二组数，目标 ≥3 未达成，且判定为"当前驱动打不出来"）**：
        `swap_after_press` 10/10（a_hit=10 全过）、`swap_hard_press` 5/5（a_hit=5 全过）⇒ 只要按对 A 就会重读并按对 B；
        会错的全是"按下时 A 已不是当前目标"（a_hit=0）。要测 §5.2 第二种情况必须**让 B 侧对驱动不可答**
        （B 淡到门槛下 / B 标签读不出 / ask 说 B 而画面无 B）⇒ 题型重设计，不是阈值问题。
      - **`race 5/5`、`guard-blind 3/3`（用户第三组数）**：70–150 ms 竞态窗口**未消**（5/5 全踩中）；
        "B 与 A 只差一个字形"时 **32×4 banner 指纹分辨不了**（3/3 全盲）。
      - **曲线 2（`fill_curve2.json`，`probe_fill_curve2.py`）不改阈值**：刺激换成类自己的画笔、链换成驱动自己的链，
        统计量与选择式一字未改 ⇒ 预检 α=1.00 **D1=137 ⇒ `T_VIS = 68` 不变**；同帧框宽扫描 25→92 / 39→92 /
        59→67 / 89→40 证明 **D1 主要取决于框内"文字核心 vs 抗锯齿边缘"的比例** ⇒ **门槛是带不是线**，随标签形状漂移。
      - 失败批次 `t_trap3-1.json`（`scripts_sha 785cfe9412d6`）**任何数字都不引用**：ask 措辞不匹配（短形式
        "click KILO"）+ swap 类一行两题 ⇒ `timeout 43` / `a_hit_but_failed 15` 都是行失同步产物（折叠后
        `14/56`、`a_hit_but_failed 0`）。它的价值只在于暴露了那两条驱动 bug（+坐标 bug 见 `DESIGN` r9③）。
    - **批次 4 `t_trap4`（38 题，鼠标通道 / 前台真实鼠标）已跑：`t_trap4-1.json`、`scripts_sha 5e3d5949b6e9`、
      v1 21/38 = 55.3%（`decided 100%`、`screen 33/38`、`replan 25`）**。这批专治第 2 组数（§5.2 第二种情况）。
      - **`a_hit_but_failed = 8`（目标 ≥3 达成）**：7 例来自新题型 `swap_twin_press`（`a_hit=1`、驱动换题后点到**标题**、
        `clicked=null`）+ 1 例 `swap_hard_press` t9（`clicked=GAMMA, want=GAMMB`）。整行 `swapped 27 a_hit 17 a_hit_but_failed 8`；
        `wrong_target 11` = 8 twin + t9 + t13 + t33。**两类机制不同，报告里不许合并成"答错 8 次"。**
      - **`swap_twin_press`（同词双现）**：换题后在网格**之前**画一个粗体大标题（文本 = 换题后的 `want_b`、无徽章、
        **不是控件**，点击直接判 wrong）。必中原因：`gui_see.py:130-156 find_text` 按 score 降序且**排序稳定** ⇒
        精确匹配并列 1.0 时取阅读顺序靠前者；且 `gym_run.py:1353 verify_before_act` 的 `verify_calls >= 1 ⇒ True`
        使**换题后的第二次点击不再复验**。8 题里 7 题靶子判决 `{"clicked": null, "twin": "TANGQ/…", ...}`。
        **这是当前口径下的真实行为，不是 bug。** 代码：`sol/sandbox/plans.v1.json` 的 `trap4` 计划（阶段 3.6 前 = `gym_app.py:147 TRAP_PLAN4`）、`gym_app.py:981 t_trap4()`、
        `gym_app.py:1307 twin = variant == "swap_twin_press"`、`gym_app.py:1379` 标题、`gym_app.py:1346 twin_press()`、
        `gym_app.py:1358 twin_watchdog()`（9 s 兜底结算，防止题目永不结算导致整批错位）。
      - **守门失明的真根因是折叠表（我上一轮"`sim 1.0` 被后续覆盖"的说法是错的，已撤销）**：`gym_run.py:58 _CONFUSE`
        把 O/Q→0 ⇒ `TANGO` 与 `TANGQ` 折叠后**同码**（都 `74N60`）⇒ 守门**重读读对了**（`ask_label_read` 里就是 `TANGQ`）
        仍判"未变"⇒ 按过期 A。修法：`gym_run.py:67 _plain()`（不折叠）+ `ask_text_changed`（`gym_run.py:1287`）改用
        `_plain(got) != _plain(want)`；`ask_label_sim` 改在**原字**上算、保留 min（只诊断，不参与判定）。
        **分工定死：折叠表只用于"找目标"（容错 OCR 噪声），绝不用于"判变化"（判等）—— 两者要求相反。**
        效果：`swap_hard_timer` **0/3 → 4/5**、`swap_hard_press 4/5`（`HARBOR/HARBOP` 与 `TANGO/TANGQ` 两类都被抓）。
      - **`race 1/1`、`guard-blind 1/1`（批次 3 是 5/5、3/3）**：竞态**未清零**（t33 `clicked=TUNDRA, want=RAVEN`，
        换的是**不同词**、banner 指纹也没够 3 格）；剩下的 `guard-blind` 1 例根因是**守门自己的重读误读**
        （把 `GAMMB` 读成 `GAMMA`）⇒ 任何比较规则都挡不住，下一步"读两次取多数"或更细指纹。
      - **新测出的可混淆对 `GAMMA`/`GAMMB`（机制①的实测样本）**：t4/t9/t13 三次都是驱动**自己**把 B 读成 A ⇒
        真实存在、与折叠表无关；`TANGO/TANGQ` 才是仅靠折叠才不可分。
      - **`by_alpha` 复现**（本批 10 题淡化切片，`T_VIS` 一字未改）：0.46 → D1 `65.0/53.0/53.0` 三题全误拒、
        0.50 → `57/57/57` 全误拒、0.65 → `79.0/70.0` 两题答对、1.00 → `78.0/102.0` 两题答对
        ⇒ **66–69 之间又是空的**（拒答最大 65、点击最小 70），与批次 3 **逐档一致**；误拒理由全是
        `the control is painted below the visibility floor`（`vis_refuse=1`）。
      - **守门成本**：`ask_gates 48` / `ms_askgate 7020.9` ⇒ **146 ms/次**（4×→2× 只省约 20 ms）；`shots 122`/38 题
        = **3.2 帧/题**。墙钟均值 `4457 ms/题` 含 twin 的 9 s 看门狗，**别当守门成本**（score 的 `1413 ms/task` 是决策耗时均值）。
      - 跑法：`cd D:\DSH\vision-work\sol\sandbox && D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap4 --tasks 38 --seed 20251007 --max-repeat 3 --json-out t_trap4-1.json`
        （**必须前台**：无徽章类只有真实鼠标点得动），再 `... score.py t_trap4-1.json`。
   - chaos 分项**排在 `t_trap2` 之后**（用户放行条件）：chaos 用的是旧题型，测的是"扰动下的稳定性"，
     在边界还没摸清的题上刷分没有意义。命令仍是
     `--chaos 0.5 --chaos-kind <kind> --until-interferences 5 --max-tasks 60`（`--chaos-ms` 缺省自动压到 200,700）。
1. **chaos 恢复能力**（三类修法，都有取证）：
   a. **读题之前**就清干扰（现在只在等判定时清）→ popup；
   b. ask 重掷后从**新帧**重新定位目标，点击要求**精确**标签匹配（rebuild 那次是模糊假阳性）；
   c. t_rows：按键前重读徽章（已做），按下去没判定就**重读行表**而不是重按同一个键；slow 类要区分「判定迟到」和「答错」，迟到时不要重规划重做。
2. **t_form 的 O/0**：属感知固有风险，当前策略＝照实算错（不读 truth）。若要做，只能靠更高分辨率的再次感知（`scale=3~4`、psm 8 + 白名单），不能再走字形宽高比。
3. 蜘蛛纸牌（暂停中）：读牌器 `rank` 框几何仍错（`RANK_BOX=(4,4,32,30)` 落在角花色字形上）；求解器 `spider_solve.py` 太弱（portfolio 300 次/副仍 **0/10 胜**）。牌桌保持现状，**不要点"使用求解器"**。
4. `sandbox\spider_table.py` / `score_read.py` 的 `face_y` 每列一律高 16 px，与真实牌面不符，待修。

## 5. 相关但不在本线
- 录制→回放（`dsh-vision-kit` 的 `macro` op）已落地并推送（`43b71a3` + `a0fa306`，CI run #8/#9 全绿）；实测冷启动前台解析 1361 ms、热 1–3 ms（`front_resolve_ms`）。
- VMware/Kali（`D:\kali-linux-2025.4-vmware-amd64\...vmx`）可用，当前无需求；若哪天必须抢前台的点按，可把训练搬进虚拟机。

## 6. 批次 5（最小收口版：改动 ①③⑦ + ② 防回归）—— 假设与证伪条件

**假设（写在动代码之前）**：t9/t13/t33 的失败是两个**可分离的驱动缺陷**，不是同一个：
(a) `press_guard` 的前置条件 `ask_source == "screen"` 把"屏读与文件不一致"误当成"屏上没有可重读的 banner"
⇒ 这三次按压**一次都没进守门**（整行无 `ask_label_read`）；
(b) 计划词取自**截断读**（`GAMMB→GAMM`、`TUNDRA→TUND`，2x 与 4x 都截断），截断词再被 `find(..., 0.82)` 的
模糊路径接到**另一个按钮**（`GAMM` vs `GAMMA` 折叠相似度 0.889）；余量规则只管 fuzzy 兜底那一支，不管精确路径。
去掉 (a)（守门无条件运行 + 记 `ask_guard_skipped`）＋计划词三角验证 (b)（候选 = 屏读 / 加 6 px 的 4x 重读 /
**文件全文词**，由"屏上精确折叠匹配"裁决）＋② 把"互为前缀"判成"同一词读短了"之后：
**期望 t9/t13/t33 至少 2 题转 OK，且整批 `ask_guard_skipped == 0`（守门运行率 100%）。**

**证伪条件（跑完照这个判，不许事后改口径）**：
(i) 三题里仍 ≥2 题 `wrong_target` 且整行仍无 `ask_label_read` ⇒ 守门没进去，① 未生效，假设错；
(ii) `ask_word_short` 触发很多而 t9/t13 仍点错按钮 ⇒ ③ 没选出正确词，假设错；
(iii) 核心 14 题出现**批次 4 里没有的**新失败（退化）⇒ 改动有副作用。
任一条成立 ⇒ **停止代码线、直接收口**（转 A：只写终版文档 + 放弃清单）。

**本轮范围（用户 m08605 选 B）**：① 守门去掉 `ask_source=="screen"` 前置（+6 px padding）；
② `ask_text_changed` 前缀容忍；③ 计划词三角验证；⑦ `score.py` 拆 `a_hit_but_failed_wrong_target`/`_twin` + 行标签 `v2`。
**不做（进欠账清单）**：④ 多候选余量规则加固、⑤ 守卫内尾帧改序、⑥ `verify_before_act` 预算改每计划 + 鼠标接入、计分 P50/P95。
跑测：`t_trap4` 38 题鼠标通道 **1 批**（核心 14 题在此批内按 `task_i` 子集单独汇总；不拆题——拆题要改 app 的题表生成，成本高于收益）。

**跑完的判定（对上面三条证伪条件逐条判）**：定稿批 `t_trap4-4.json`（sha `ebfc7dce831a`）**24/38**，
核心 14 题 **7/14 → 10/14**，三处变化**恰好**是 t9/t13/t33（wrong → ok），其余 11 题逐题不变。
(i) **不成立**：三题全转 ok，t9 `ask_word_from=exact` + `ask_word_noise=1`（banner 把 `GAMMB` 读成 `GAMMI`，被文件仲裁判成读错）、
t13 `ask_moved=1`（守门真的开火了，重规划到 `GAMMB`）、t33 `ask_cells=3.0` + `ask_moved=1`（指纹先发现换题）。
(ii) **不成立**：t9/t13 都拿到了正确词（`ask_word=GAMMB`，精确唯一命中），`ask_word_short` 只在 twin 家族出现 2 次。
(iii) **不成立**：核心 14 里没有批次 4 没有的新失败；`a_hit_but_failed 8 = wrong_target 0 + twin 8`，
`race 0/0`，fade 四个档位与批次 4 逐格相同。⇒ **假设保留，批次 5 收口。**
代价（必须一起引用）：`ask_gates` 48 → 56、ms/门 146.3 → 143.4、`shots` 122 → 137、墙钟/题 4457 → **4823 ms（+8.2%）**、
`ask_guard_skipped` 为 0（守门运行率 100%）。**三次 sha 分裂**：`-2`（守门被 OCR 噪声误触发 ⇒ 不按键死等）、
`-3`（"指纹 0 格 ⇒ 噪声"的判据吞掉真换题）⇒ 定稿判据 = **文本不一致时由靶子自己当前的 `ask` 仲裁**。

## 7. 欠账清单（每条带判据 + 出处，别再往下做）

| # | 欠账 | 判据（怎么算还清） | 出处 | 状态 |
|---|---|---|---|---|
| 1 | 改动 ④ 多候选余量规则：精确路径不设余量（`GAMM` vs `GAMMA` 折叠相似度 0.889 也能接上） | `t_trap` 家族里"选到非唯一候选"的次数为 0 且新增 `label_ambiguous` 计数 | `DESIGN` §8.1、`gym_run.py:1772` | 欠 |
| 2 | 改动 ⑤ 守卫内改序：文本重读在前、廉价指纹在后 | 单字形换题家族的 `ask_word_noise` 误判为 0 | `DESIGN` §8.1、`gym_run.py:1320-1328` | 欠 |
| 3 | 改动 ⑥ `verify_before_act` 预算改"每计划一次 + 每题上限 4"、鼠标通道接入 | `verify_budget_skip == 0`，且鼠标首次按压 +89 ms 可接受（`--no-press-verify` 可回退） | `DESIGN` §8.1、`gym_run.py:1369`/`1749` | 欠 |
| 4 | 计分 P50/P95（判据 P50 ≤ 240 ms、P95 ≤ 320 ms） | `score.py` 打印分位数 | `DESIGN` §8.1 | **还**（批次 6；扣帧口径 147/181 达标，见 ../sol/sandbox/SCORE.md 批次 6 ⑥） |
| 5 | twin 点标题（8/8）：需要**控件可供性**判据（文本块不是控件） | twin 家族不再损失 | `DESIGN` §8.2、`../sol/sandbox/SCORE.md` 批次 5 | **还**（批次 6：painted 判据，twin 8/8） |
| 6 | `swap_after_press` 每题约 5 s 空等（判定不会来） | 该家族 per-task 墙钟降到与 `swap_timer` 同档 | `DESIGN` §8.2、`../sol/sandbox/SCORE.md` 批次 4 ⑸ | 欠 |
| 7 | `no_badge_fill` 标定用合成帧（`T_VIS=68`）与真实 0.50 档对不上 | 用**真实题面画笔**重新标定 | `DESIGN` §8.3、`STATE.md` §4.1 | 欠 |
| 8 | 键通道核心 2 题（synonym）本轮未跑（跨场景选点成本高于收益） | 分类跑测落地后，键通道核心集独立成批 | `STATE.md` §6 | 欠 |
| 9 | chaos 只解锁了 `rebuild` 一类（`move`/`popup`/`slow` 未跑） | 每类各跑 ≥5 次干扰且 delta 可解释 | `DESIGN` §8.3、`../sol/sandbox/SCORE.md` 批次 6 ⑦/批次 7 | **四类都跑**（用户 2026-10-04 二次修正，见 §8.1）：`rebuild` 批次 6；`move`/`slow`/`popup` 批次 7，标「探索性·不并入定稿」 |
| 10 | `gate_ms` 口径含抓帧（`t_gate` 在 `self.shot()` 之前） | `t_gate` 移到 `shot()` 之后，P50 与 `ms_askgate/ask_gates` 同口径 | `../sol/sandbox/SCORE.md` 批次 6 ⑥ | **还**（批次 9：368.0 → **124.1 ms**，扣掉 ≈244 ms 抓帧；与独立口径差 **10.58 ms**，判据 ≤10 边缘未达、证伪线 20 未触发） |
| 11 | `press_delay_ms` 没留在逐题行上（**措辞修正**：它确实写了逐题行，是 `_redo()` 换记录时丢的） | 逐题行能看到 jitter 时长，且合计 == `stats` | `../sol/sandbox/SCORE.md` 批次 6 ② | **还**（批次 9：逐题行 6 行合计 **4501 ms == `stats.press_delay_ms` 4501.0**；`_redo` 续带 `press_delay_ms`/`press_jitter_task`/`gate_ms`） |
| 12 | `guard-blind` 在批次 5/6 都没有分母（不打印） | 单字形换题家族再出现且被指纹漏判时给出分母 | `../sol/sandbox/SCORE.md` 批次 6 ③ | **关闭·已量**（第六段，见 §17）：`--keys --bg` 20 题 `t_trap5` ⇒ `blind_seen = 0`、events `trap_stale_press = 0`、`swap_hard_timer` 5/5 全 ok，且 `task_i 13` 在**指纹 `ask_cells 0`** 的情况下仍被**文本重读**抓住 ⇒ 单字形换题自批次 4/5（raw `_plain` 比较 + pad 6 px）起已覆盖，判据"漏判时给分母"不再成立；未改代码 |
| 13 | run json 的 `events` 是路径且 app 覆盖写 ⇒ 跨批 stale 归因要逐批即时打分 | `--events` 按批命名（或 json 内嵌事件） | `../sol/sandbox/SCORE.md` 引用规则 7 | **还**（批次 7：`--json-out` 带出 `x-state.json`/`x-events.jsonl`） |
| 14 | 每批的 app state/events 不留档 ⇒ **事后重打分一定错联**（`score.py:162-169` 按 `events` 路径读真值；实测重打 `t_trap5-1.json` 得 36/48、`MISMATCH 11`，真值 37/48、`MISMATCH 0`） | 驱动把 app 的 `--state/--events` 按 `--json-out` 命名（或每批拷一份 events）⇒ 事后 `score.py <json> --events <留档>` 可复核 | `../sol/sandbox/SCORE.md` 引用规则 7 | **还**（批次 7，只改命名不改判定逻辑 ⇒ 与批次 6 数字可比；批次 1–6 的旧数字仍是"跑完立刻打的"） |
| 15 | **Option A：守门每帧重算 banner box**（本批只做"读不出 ⇒ 回落指纹"，不去重算框） | 守门不再依赖"计划时记录的 `ask_box`"，`ask_read_unreadable` 在 move/前台批次里降为 0 | `DESIGN` 修订 r13 ⑤、`STATE.md` §10.2 | **还**（批次 10：新增 `ask_box_now()` 每帧用像素段重算（重算优先、失败退回冻结框），指纹基线/匹配/阈值一字未动；`move@0.70` `ask_read_unreadable` **2 → 0**、`ask_box_recomputed 124 == ask_gates 124`、同 `task_i` 无 ok→非 ok 翻转、`gate_ms` P50 **139 ms**（+15 ≤ 30）；见 `../sol/sandbox/SCORE.md` 批次 10 节 + 本文 §14） |
| 16 | **`popup` 类干扰打不掉**：`dismiss_interference` 在 `--keys --bg` 下只按窗口标题找 `"attention"`（UIA 枚举没找到）⇒ 弹窗留屏、按键被吃、该题永不结束（两档各 1 次 fire 后早停） | `--keys --bg` 通道能"看见并打掉"外来窗口（鼠标通道已有视觉路径 `_button_candidates(img2,"DISMISS")`）⇒ `popup` 类能跑到 ≥5 fire | `STATE.md` §10.4、`../sol/sandbox/SCORE.md` 批次 8 ③、`HANDOFF.md` 盲区 17 | **还**（批次 12：`popup_seen/dismissed/failed = 24/24/0`、`interferences 24`、60/60 无早停、判定路径一字未动；见 §18 + `../sol/sandbox/SCORE.md` 批次 12 节）<br>⚠ 第十段更正：根因**不是**"枚举看不见弹窗"，而是 **actor `_slim` 折叠把 `data.windows` 截断**、驱动只读 `data`（inline 里有 `attention`）；"借鼠标视觉路径"在 `--keys --bg` 下**仍不可行**（弹窗是独立 HWND、不在主窗帧里；`--bg` 鼠标点击整条失效，见 §16） |
| 17 | **`shot` 空帧零容忍**：一次空位图（`ValueError: cannot write empty image`）⇒ `gym_run.py:508 raise SystemExit` ⇒ **整批退出 + 不写 run json + 逐题行全丢** | 遇到空帧先做一次短重试（或至少记 `shot_retry` 并把已跑题的逐题行落盘）⇒ 单次抓帧失败不再作废整批 | `../sol/sandbox/SCORE.md` 批次 10 ⑥、`STATE.md` §14.8 | **还**（批次 11：`ShotFailed` 异常类型 + `_shot` 重试 3 次（间隔 0.2 s）+ main `try` ⇒ 已完成的题写成 partial run json（`partial`/`exit_reason`/`tasks_planned`）+ 退出码 **3**；判定路径一字未动。实测两类空帧构造（kill / minimize）都不再丢批、`score.py` 可打分；同协议 48 题回归 `35/48`、核心 14 翻转 0、`ms/题 +0.9%`、`shot_empty/shot_retry = 0/0`。见本文 §15.6B + `../sol/sandbox/SCORE.md` 批次 11 节） |
| 18 | **连续 / 视口类交互盲区（滚轮 + 拖拽）**（**阶段 3.5 = 部分覆盖**：前台真鼠标通道、批次 23 `t_rows` / 24 `t_chips` 各 8 题、`viewport` 桶 `8/8`；**仍不覆盖** `--bg` 鼠标通道与滚轮/拖拽的连续交互公差 —— 见 §34.6）：v1–v3 口径下**覆盖 = 0**——`TRAP_PLAN`/`PLAN2`–`PLAN5` 从不排 `t_rows`/`t_chips`，所有 `t_trap*` 记录里 `stats.scrolls = 0`、`stats.drags = 0`；驱动侧两条路径**只挂在鼠标通道**（`Driver.wheel()` = `gym_run.py:1199–1210`，唯一调用点 `gym_run.py:2314`；`Driver.drag()` = `gym_run.py:1193–1197`，唯一调用点 `gym_run.py:2862`）⇒ "主动移动视口后重定位"与"连续动作轨迹 + 落点"**从未在口径内被测过** | `t_trap` 家族里补可滚动场景 + 可拖拽场景，覆盖这两种交互；八问（滚轮 4：会不会滚 / 方向 / 幅度 / 滚完重定位；拖拽 4：会不会拖 / 起点抓准 / 落点精度 / 拖拽中途 `move` 干扰能否适应）逐条有据 | `HANDOFF.md` §4 盲区 21、本文 §16 | **欠（有据）** —— 见 §16 的八问逐条判定（八问 = **1 能 / 1 代码级一致 / 6 量不到**，原因 = `--bg` 鼠标通道不生效；**新题型，排在所有现有欠账之后**；本段只量不改、不裂 sha）<br>⚠ 第十二段复核：**行号已漂**（批次 11 的 `ShotFailed` 补丁 +~15 行）—— `Driver.wheel()` 现在 `gym_run.py:1214`、唯一调用点 `:2329`；`Driver.drag()` 现在 `gym_run.py:1208`、唯一调用点 `:2877`。并且两条在键通道里**都有键盘等价物**（`Next`/`Prior`/`Up`/`Down`/`Home`/`End`；chips 的 `_bind_key` 拾取/落位），**驱动已经在用** ⇒ 这是**覆盖缺口、不是功能缺陷**（见 §20.3） |
| 19 | **`popup` 类只跑了 1 档 1 通道**（第十段新增，未冻结）：批次 12 = `0.35` 档、键通道 + `--bg`、只跑 1 次；`0.70` 档（批次 8 的 `popup70` 仍是旧驱动的失败产物）与**鼠标通道**（受 §16 的 `--bg` 鼠标缺口限制）都**没有**可引用的修后数据；与批次 8 的对照是**历史产物对照**（驱动版本不同、无同批 A/B） | `popup` 两类档位都有修后数据（每档 ≥5 fire），或明确宣告只做 `0.35` 档并把口径写死；**两条通道各有一档达标**（第二十二段把判据按「强度档 × 通道」四格补齐） | `../sol/sandbox/SCORE.md` 批次 12/13 节与批次 16–19 节 / `STATE.md` §19.7、`HANDOFF.md` 盲区 17 | ✅ **已关死（第二十二段）** —— **依赖已更正**：原按「若 #20 选 C 则随它收口」记账，而 **#20 的最终结论是「通道可用」**（不是选 C）⇒ **依赖解除，#19 独立走关死路径**。覆盖面：`0.35` 键 ✅（批次 12）、`0.70` 键 ✅（批次 13 第一批）、**`0.70` 鼠标 ✅（批次 16 + 17–19）**、**`0.35` 鼠标 ✅ 弹窗侧达标**（第二十二段 1b = 批次 20：fire **10**、`popup_seen/dismissed 10/10`、补点 1 次、`task_i 17` 被 modal 挡住 2.18 s 后恢复）。⚠ 批次 20 为 **21/24 早停**（`task_i 21` 的 `must_refuse`/`prose_only` 题**没有走拒答、反而按了标签**，`score.py false_accept 1/1`）⇒ 归因**另记 #21**、与弹窗通道无关。边界：**只 `popup` 类、只这两档**；见 §19.7 + `../sol/sandbox/SCORE.md` 20.3<br>✅ **第二十六段补记（#21 已修）**：该批已用**同 seed / 同协议**复跑 = **批次 21**（24/24 不早停、`task_i 21/22/23` 全 `refused_right`、`false_accept 0/3`）⇒ 「未跑满」这条**形态**自本段起解除（原文保留只为记录当时的批次形态）；**本行的强度档证据仍取批次 20 的 fire 数**，20.5 的六条边界照旧适用。 |
| 20 | **鼠标通道下 `popup` 清障路径不生效**（第十一段新增，未冻结）：鼠标分支 `dismiss_interference()` 清障次数 **0**（驱动 `disturbances: 0 fired`）、题目卡在 `blocked by modal`（app 侧 `blocked 10` + `chaos 1`）、3 题后早停（退出码 1）；该分支**没有 `popup_*` 计数**（"没看见"与"看见了没点"在数据上不可区分）、候选走默认 veto（键分支特意传 `keep_vetoed=True`） | 鼠标通道的 `popup` 批跑满题数且 `popup_dismissed == popup_seen ≥ 5`；**或**明确宣告"鼠标通道不支持清障"并把该组合从覆盖面里划掉（第一步 = 一次只读探针：dump 弹窗帧 + 两种 `keep_vetoed` 对照） | `../sol/sandbox/SCORE.md` 批次 13 节 13.2/13.5、本文 §19/§20、`HANDOFF.md` 盲区 17/23 | **根因已定案**（第十二段只读探针，两道独立门：① **看不见** —— 该通道读的那一帧里按钮从来不是候选：块 0、词路径只给被 veto 的散文 ⇒ 候选空、一次不点；② **抢前台** —— 点击带的 `front_title` ⇒ `mode: top` 把 app 钉到弹窗之上 ⇒ 坐标点对了也白点）；**判据已达成 → 已还清**（第十六段批次 16：鼠标通道 16 题**前台**窄批跑满不早停、`popup_seen 14 / popup_dismissed 14`、`failed 0` ⇒ 判据栏**第一个分支**达成；窄批口径，边界见 `../sol/sandbox/SCORE.md` 批次 16 节 16.5）；修法见 §20.4 选项 D（约 10–15 行）<br>⚠ **第十三段：选项 D 已实现并跑了一次**（批次 14 = 鼠标通道 `popup@0.35`、60 题；干跑 2/2、清障 `popup_seen 11 / dismissed 10 / failed 1`），但 **task 21 早停、退出码 1** ⇒ **判据未过、已回退**（`gym_run.py` 回到 `87470aaff559`）；补丁留档 `D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`，残留机制与三条下一步见 `../sol/sandbox/SCORE.md` 批次 14 节 + 本文 §21<br>⚠ **第十四段：第二次尝试（选项 b = 降级 `key("Return")`，净 +24 行）—— 干跑即失败**（`popup_seen 13` / `popup_dismiss_failed 13`、`popup_dismissed` 与 `popup_key_dismissed` **键根本不存在 = 一次没清掉**、2 题全 NONE、退出码 1）⇒ 按本段终止条件**立即回退**（`gym_run.py` 回 `87470aaff559`，本次补丁留档 `D:\DSH\dsh-actor\tmp\w16-popup-key-fallback.patch`）；**A/B 两批都没跑**。机制 = 非 bg 通道的 `key()` 是**真实 SendInput 前台按键**、本机抢不到前台 ⇒ 45 次 Return 全落空（对照：坐标点击能命中 topmost 弹窗）⇒ **(b) 不是没写对，是结构上不成立**；见 `../sol/sandbox/SCORE.md` 批次 15 节 + 本文 §23<br>✅ **第十六段（本行收口）：还清** —— 用户选 (ii)「需要真凭据」后按 §24.3 的两个前置条件一次做完（重落选项 D 补丁 → `85893817760a3be5` + 拆耦合 → **`3fa0e4ba4b1b9679`**，净 **+30 行**、只落在 `--chaos` 下的清障路径），正式批 = **鼠标通道 `popup@0.70` / 16 题 / 16 全 `OK` / 退出码 0 / 无早停**、**`popup_seen 14 / popup_dismissed 14`**（`failed` 键不存在）、`interferences 14`（= 每次发现只点一下）、app 侧 `chaos 14` 一一对应、**无 `blocked` 事件**；驱动改动**保留为定稿**（未回退）。⚠ 边界：窄批单次、0.70 档（§24.2 写的 0.35 在 16 题里期望弹窗 ≈3 `< 5` ⇒ 判据不可达，故取更严档）、**拆耦合未被触发**（(a)/(c) 是未被检验的保险）、`--bg` 鼠标通道仍不生效（盲区 #21）。见 `../sol/sandbox/SCORE.md` 批次 16 节 + 本文 §25<br>✅ **第十九段（补记）：那条保险已被实战检验一次** —— 3 批 × 16 题鼠标前台窄批（seed 20251008/09/10）里，**批次 18 的补点被触发且救回**（`interferences 9 > popup_seen 8` ⇒ 同一遭遇点了两发、该遭遇最终被清掉、该批 16/16），三批合计 **0/28 遭遇死锁** ⇒ 死锁率 95% 单侧上限 ≈ **10.7%**（rule of three）、第一发失手率 1/28 = 3.6%；"**漏点是否消除**" 仍 **【未决】**（3 × 16 题仍宽，不能宣告消除）。数值与逐条边界见 `../sol/sandbox/SCORE.md` 批次 17–19 节、本文 **§27**<br>🔒 **第二十段（收口 / 结项 —— 不再是活动项）**：① **通道可用** ✓；② **保险单实例已验证** ✓（批次 18 触发一次并救回）；③ **"漏点是否消除" =【未决】且判定"不追加"** —— 再加 3 批（48 题）只能把 95% 单侧上限从 ≈10.7% 收窄到与观测失手率（1/28 ≈ 3.6%）同一量级 ⇒ 仍分不开、**边际收益 ≈ 0**（"不追加"= 已决定不再投入）；④ 口径只写"**路径可达 + 单次有效**"、**不写**"保险有效"。**唯一入口**（若将来真要证消除）= 再跑 3 批 48 题，**本段不跑、非当前计划**。见本文 **§28.3** |
| 21 | **鼠标通道下「徽章判定」族的 `must_refuse` 题不走拒答、反而按标签**（第二十二段新增 / **第二十三段已判定，未修**；**高优先级**）：**性质 = 通道级缺口，按「判定依据」分层** —— 键通道靠「有没有 `[k]` 徽章 = 可操作性」判出「这不是控件」（`gym_run.py:2160 if self.keys:` ⇒ `:2161 press_hint` 失败 ⇒ `:2163 no_key_refuse`），**鼠标分支（`:2164-2168`）没有任何可操作性判据**，`control_visible()` 只测「画出来没有」⇒ exact 命中的那行 **prose** 坐标被 `click()` 按下、app 收不到任何事件 ⇒ 题不前进 ⇒ `--max-repeat` 早停；而 `:2210`「no control carries the asked label」在 `else:`（标签**全屏都找不到**）分支里，**prose 题永远走不到**。**已观测 2 批 100% 复现、同一道题**：批次 14 `t_trap2-w13-popup35-mouse-fix.json` 与批次 20 `t_trap2-w22-popup35-mouse.json` 都停在 `task_i 21`（ask `click the button labelled XENON`、`next_task_i 21`、三行 `acted/none`）⇒ 鼠标通道**从未**在 `t_trap2` 上跑完。**反证（因此不是「鼠标通道不能拒答」）**：可见性判定族 `t_trap3`（`nb020/nb030/nb035/nb044`）在鼠标前台通道 **6 批 60+ 行全部 `refused/ok`**（走 `:2170`/`:2202`「the control is painted below the visibility floor」）；键通道 `t_trap2` 族 14–28 题/批**几乎全 `refused/ok`**（仅 2 行 `acted/ok`）。**代码级推断（未观测）**：同分支的 `disabled` / `two_close_names` 等徽章判定族**同样受影响**（同一缺失判据），且批一到该族就早停 ⇒ 后面的题看不到 | 鼠标前台通道下**徽章判定族**的 `must_refuse` 题能落到 `refuse()`（逐题行有 `refused: true` / `refuse_why`）、题正常前进、`score.py` 的 `false_accept` 为 0 | `../sol/sandbox/SCORE.md` 批次 20 节 20.3/20.4 / `STATE.md` §29.2 + **§30** / `HANDOFF.md` 盲区 17 | **已修（第二十六段 B 实施，2026-10-05）** —— 落点 = `gym_run.py:3507`（`_redo` 之后、第二次 `wait_verdict` 之前）插入四条守卫 + 一次 `refuse()` + 计数 `stats["refuse_by_stall"]`，**净 +9 行**；新 sha **`d8594bff3738ca9b`**（回退点 `3fa0e4ba4b1b9679`、`scripts_sha 586171888d39`）。**验证（两批前台真实鼠标）**：**批次 21**（`popup@0.35`、24 题、与批次 20 同 seed 同协议）= **24/24 不早停**、`task_i 21/22/23` 全 `refused/ok`（`refuse_why "clicking the asked label changed nothing"`）⇒ `false_accept 0/3`、`refuse_by_stall 3`；**批次 22**（60 题、与批次 14 同参）= **60/60**、`refused_right 14`、`false_accept 0/14`、`false_refusal 0/46`、`refuse_by_stall 4`。**回归**：与批次 20 比 ⇒ 前 21 题判定**逐题一致**；与批次 14 比 ⇒ **唯一翻转就是 `task_i 21`**。**残留风险**：点偏会被记成 `false_refusal`（表现可见）⇒ 见到上升按 `DESIGN-21` §6/§8 **逐题人工抽查**；本段两批均为 0。记录见 §32、复跑清单结果见 §31.6、数字见 `../sol/sandbox/SCORE.md` 批次 21/22 节；重跑清单见 §31、修复设计见 `DESIGN-21-mouse-operability.md` |


## 8. 放弃清单（B 收口时明确不做的，各一句"为什么不影响主结论"）

- **`race` 未清零**：批次 3 的 `5/5`、批次 4 的 `1/1` 分母都小，批次 5 是 `0/0`；主结论是"守门能不能发现换题"，不是"竞态窗口有多宽"，而且分母已按"真正按了过期 ask 的次数"钉死，不会被题数放大。
- **`guard-blind` 未修**：批次 4 的 `1/1`（t33）在批次 5 已由 ① 修掉；剩下的单字形家族靠"文件仲裁"覆盖，指纹单独不可靠这条已写进 `HANDOFF.md` 已知盲区第 3 条。
- **`verify_calls` 缺陷**（换题后第二次按压不复验）：只影响"复验覆盖率"这个成本口径，不影响任何一次按压的正确性判定；已写进欠账第 3 条。
- **twin 点标题（8/8）**：属**设计使然的可预测失败**（标题与控件在 OCR 里都是文本块，驱动取靠前者），且口径已把它单列成 `_twin`，不混进 `wrong_target`。
- **chaos 未跑**：测的是"扰动下的稳定性"，用的是旧题型；在边界没摸清前刷这个分没有解释力，用户也已把它排在 `t_trap2` 之后。
- **`nb046`/`nb050` 全拒答（6/6 `false_refusal`）**：fade 档把徽章淡到读不出，属**可预测的题面退化**，不是驱动缺陷；口径里 `false_refusal` 已按 answerable 分母单列。
- **不再裂 sha**：批次 5 是本线的终止点；`t_trap4-4.json`（sha `ebfc7dce831a`）之后不再改动 `gym_run.py`/`score.py`，要动就先读 `HANDOFF.md`。

### 8.1 追记（用户 2026-10-04 复核后的定论，批次 6 之后）

- **`race`：不单独跑扩分母，记"踩线达标"**。分母 5 = 判据线，5 次全错**有区分度**（不是"24/24 连五次"那种空信息），但不据此宣布"已缓解"；**下一批若涉及守门改动（欠账 ④⑤⑥ 任一条），race 分母在同一批里扩**（单独跑只会被下一批的改动覆盖）。
- **`chaos`：四类都做，不放弃任何一类**（用户 2026-10-04 **二次修正**，推翻同日晚间"只开 `move`/`popup`/`slow` 永久放弃"那一条）。顺序与理由：①`move`（`gym_app.py:595-614`：`self.body.pack_configure(padx=10+rng.randrange(20,90), pady=…）` + 50% 概率 `self.geometry(...)` 移整窗）与已跑的 `rebuild`（换题）互补 ⇒ "重建 vs 移动"对比；②`slow` 正对 `timeout` 分支（批次 6 已出现 `timeout=1`）：量"判定晚到"时驱动会不会重复按压；③`popup` **前置验证：`--no-topmost` 是继承的**（`gym_app.py:211 popup_topmost: bool = True` → `234 self.popup_topmost = popup_topmost  # False while a driver works in background` → `653 if self.popup_topmost:` → `1484 popup_topmost=not a.no_topmost` ⇒ 驱动在后台跑时干扰窗**不置顶**，不需要改代码；实测以各批 `foreground unchanged` 为准）；④`rebuild` 已完成（批次 6）。每类 **2 强度（0.35 / 0.70）× ≥5 fire**，标「探索性·不并入定稿」；delta 解释不了就停并写欠账。
- **欠账 #14 已做**：驱动按 `--json-out` 给 app 的 state/events 命名（`x.json` → `x-state.json` + `x-events.jsonl`）⇒ 每批留档、可事后 `score.py <json>` 复核。**它只改文件命名、不改任何判定逻辑** ⇒ sha 会变但**与批次 6 数字可比**（`../sol/sandbox/SCORE.md` sha 表里已按此标注），且**不引入 `LOGIC_VERSION` 之类的新机制**。
- **其余欠账全部冻结**（守门 ④⑤⑥、`guard-blind` 清零、`t_gate` 移到 `shot()` 之后、`press_delay_ms` 进逐题行、`swap_after_press` 5 s 空等、`no_badge_fill` 重标定、键通道核心 2 题），只保留在 `HANDOFF.md` 的「如果继续做」与本节 §7 表里，**不再为此裂 sha**。

### 8.2 追记 2（2026-10-04 收工复核；今天明确不做的三件，各一句"为什么不影响主结论"）

- **Option A（守门每帧重算 banner box）不做**：它影响的只是"计划时记录的 `ask_box` 在重排后失效"这一条路径，而批次 8 已用**通用退化规则**（读不出 ⇒ 回落指纹）覆盖同一场景 —— `ask_read_unreadable` 2 次全落在 `task 31`、本批**无 `none` 题**、不再早停 ⇒ **不影响 `move`/`slow` 的任何已公布数字**（升级为欠账 #15）。
- **`popup` 类的打窗能力不修**：该类两档各只 fire 1 次就早停，数字**一律不引用**（`HANDOFF.md` 盲区 17）⇒ 它本来就不进任何结论，**不影响 `move`/`slow`/`rebuild` 三类的主结论**（升级为欠账 #16）。
- **本批不追 `a_hit`**：判据 ③ 未达标（4/10、7/10）如实记录、未改阈值也未加题量 —— 已查明它是"守门假阳性/干扰把首按推过 8 s 安全换题线"的**读出量**（剂量-反应 + 墙钟两簇：按中的 4.3–4.9 s、没按中的 10.6–11.2 s）⇒ 追求它等于改测量工具去迎合一个派生量，**不影响"死锁已修好"这个主结论**。

## 9. 批次 6 —— 假设与证伪条件（先写，后量，再改）

**假设（四行）**：`swap_twin_press` 8/8 全错的根因是**驱动排"词"、不排"被绘制的控件"**。
同一个词出现两次：标题按阅读顺序在前（`gym_app.py:1376-1393`，注释原文 "a driver that ranks words
rather than widgets picks the label over the button"），而**标题是裸文字**（`tk.Label(bg=BG)`，页面上没有画矩形），
**真按钮是被绘制的块**（`find_blocks` 的判据，`gym_run.py:573-580`："only the pixels tell you whether anyone
drew a control there"）。⇒ 命中文本后改用"是否坐在被绘制的块里"给候选排序，twin 家族应转为点真按钮；
同一条判据同时修 synonym 鼠标通道的正文误点（正文也是裸文字）。

**证伪条件（两条，先量后改）**：
(i) **量**：抓一帧 twin 题（相位 B），若 `find_blocks` 在标题处给框、或真按钮处给空 ⇒ 判据不存在，**不写修复代码**即停、写欠账；
(ii) 改完跑 `t_trap5` 24 题，twin 仍 0/8 转 ok ⇒ 假设被证伪，停、写欠账。

**观测点**：twin 8 题的 `detail.clicked`（`null` = 点到裸文字、控件 id = 点到按钮）；
新增计数 `label_painted` / `label_text_like` / `label_alt_tried`。

**判据**：twin ≥6/8 转 ok，且核心 14 题**没有 ok→wrong 的翻转**（t0/t4 转 ok 属预期，10/14 → 12/14）。

**保险条件（写进代码注释）**：绘制块只用于**排序候选**，不用于否决；全部候选都未被 `find_blocks` 认出时
回落批次 5 的老路径（否则会把"能点对"变成"新拒答"，直接踩核心回归判据）。

**本轮范围（用户 m08820 确认）**：① twin 候选排序（`widget_like` + 计数）；② race 重测 =
新 variant `swap_race_timer`（220–420 ms）+ 驱动 `--press-jitter LO,HI`（**按 variant 生效，只有
`swap_race_timer` 加 sleep**，即选项 A）+ `score.py` 把新 variant 计入 `race`（+ `race_press_after_guard`）；
③ 逐门采样 `gate_ms_hist` + `score.py` 打 P50/P95（消掉"§1.4 要 P50/P95 / §二 说 P50/P95 不做"的冲突）；
④ chaos 首类：家族 = synonym、场景 `t_trap2`、通道 `--keys --bg`、kind = `rebuild`（四类 = rebuild/move/popup/slow，
`gym_app.py:545-557`；`synonym` 不是 kind），另跑无 chaos 对照批。
**不做**：`press_guard` 逻辑（只加 jitter 钩子）、④⑤⑥ 三条老欠账、nb046/nb050 边界带。
**终止条件**：核心回归出 ok→wrong 翻转 ⇒ 停；twin 0/8 ⇒ 停；chaos delta 解释不了 ⇒ 停；
twin 在"量"这步就证伪 ⇒ 不写代码即停；race `0,80` 拿不到 5 行 ⇒ 收窄到 `0,40` 再一批，仍不足 ⇒ 写"已知未测"。

### 9.1 第 2 步（量）结果 —— 假设确认，两个判据只有一个能用

探针 `../sol/sandbox/probe_w6_twin.py`（后台 PrintWindow + 键盘通道点 A，不碰用户指针），
`probe-w6-twin.json` 是原始证据，`probe-w6-twin.png` 是那一帧。量到的帧：`t_trap4` 第 1 题相位 B，
banner 问 `HARBOP`，正文里 `HARBOP` 出现**两次**：

| 判据 | 标题（裸文字 542,126,96,17） | 真按钮（292,192,73,14 落在块 228,168,172,60 内） | 分得开？ |
|---|---|---|---|
| `find_blocks` 覆盖（中心是否在块内） | **否** | **是**（块 fill 1.0，块标签 `2] HARBOP`） | **是** |
| `block_evidence.fill_share` | 0.398（neighbours 1，veto False） | 0.283（neighbours 4，**veto True**） | **否，而且是反的** |
| 现有 `_button_candidates` 排序 | **第 1 名**（score 2.543、veto False、唯一候选） | 根本没进候选 | **否** |
| 块标签匹配（`block_label` + 去徽章） | — | 现正则 `^[\[\(]...` **匹配失败**（OCR 给 `2] HARBOP`，丢了左括号）；放宽成 `^[\[\(]?` 后**匹配成功** | 可用但依赖读标签 |

**结论**：① 假设成立——`find_blocks` 明确把标题与真按钮分开（块 fill 1.0 vs 标题处无块）；
② 修法用**"问句词在正文中的多个出现里，选那个坐在被绘制块里的"**，不是 `fill_share` 排序：
`block_evidence` 的 12/12 阈值量不到这个 app 的浅色按钮（`#e8eef5` 对页面 `#f4f7fb` 只差 12/9/6，
`_find_blocks` 自己用 8 才看得见，见 `gym_run.py:593-596`），所以它在按钮文字上给出 0.283、在标题上 0.398 —— **反的**；
③ 帧内裁决 `{"occurrences":2,"painted":1,"bare":1,"picks":"HARBOP","decides":true}` ⇒ 新规则在这一帧**判对**；
④ 成本：`find_blocks` 单次 **77.6 ms**（1180×780 帧），按"只在问句词出现 ≥2 次时才跑"计，核心 14 里只有 twin 8 题付费 ⇒ 墙钟增幅 ≈ 0（判据 ≤ +25%）。

⇒ 进第 3 步（改 7 处）。**唯一的规则来源是 `find_blocks`；`fill_share` 在这条 app 上不可用作判据**（写进 DESIGN r11）。

### 9.2 第 3–4 步（改 + 跑）结果 —— twin 0/8 → 8/8，race 首次拿到分母 5

**改了什么（三文件一起改、同一次 sha 分裂；`patch_w6.py` 是表驱动补丁，每个锚点必须恰好命中 1 次）**

| 位置 | 改动 |
|---|---|
| `gym_run.py:15` | `import random` |
| `gym_run.py:305` | `Driver.__init__(..., keys: bool = False, jitter: tuple = (0, 0))` + `self.jitter` |
| `gym_run.py:579` | 新 `painted_boxes(img, rec=None)`：`find_blocks` 的按帧缓存（`rec["_blocks_for"]`/`rec["_blocks"]`），避免同一帧付两次 77 ms |
| `gym_run.py:597` | 新 `@staticmethod painted_hit(hits, boxes)`：出现中心落在任一被绘制块内即命中；**只有"唯一被绘制命中且少于全部出现"才返回，否则 None** ⇒ 不否决、可回落 |
| `gym_run.py:1878-1900` | 读题匹配块在 `exact`/`fuzzy` 之前插"被绘制块里的出现"一轮（`ask_word_from="painted"`、计数 `label_painted`/`label_text_like`/`label_alt_tried`）；精确/模糊循环改为嵌在 `if not hit:` 下 |
| `gym_run.py:2052` 附近 | synonym 分支鼠标侧同判据（`find_all(body, lab, 0.9)` → `painted_hit`）；键通道的 prose 过滤不动 |
| `gym_run.py:1468` | `press_guard` 逐门采样 `rec["gate_ms"]` + `stats["gate_samples"]` |
| `gym_run.py:1480` | 新 `press_jitter(rec)`：只在 state 文件 `variant == "swap_race_timer"` 时 `random.randint(lo, hi)` 并 `sleep`，记 `press_delay_ms`/`press_jitter_task`/`stats["press_delays"]` |
| `gym_run.py:3052`/`3158`/`3395` | `--press-jitter LO,HI`（默认 `0,0`）；main 解析并传 `jitter=`；`gates` = `v3`(t_trap5) / `v2`(t_trap*) / `v0` |
| `sol/sandbox/plans.v1.json` 的 `trap5`（= `base: trap4` + 10 条；阶段 3.6 前 = `gym_app.py:162`）/ `gym_app.py:997`/`1354`/`1425`/`1449` | `TRAP_PLAN5 = TRAP_PLAN4 + [("swap_mid_task","swap_race_timer")] * 10`（48 题，**前 38 题与批次 4/5 逐字相同**）；`t_trap5` 分派；`stale` 集合加 `swap_race_timer`；定时 `800-2600`（其余仍 `600-1000`）；帮助串补 t_trap5 |
| `score.py:34`/`37`/`372`/`377`/`423`/`679`/`728` | `V3`；`pct()` nearest-rank；`race_after_guard` + `race_press_after_guard`；`gate_samples`/`gate_p50`/`gate_p95`；race 行加 `(after the guard's frame N)`、新增 gate 分位行；selftest 39 → **41 checks, 0 failed** |

**定稿批**：`t_trap5-1.json`，sha `9db420c422a2`，`gates v3`，鼠标前台（不 `--bg`），`--press-jitter 0,1200`，48 题 4 分 05 秒。

```
t_trap5   v3 37/48  77.1%  decided 100.0%  disturb 0   screen 44/48 replan 33   1564 ms/task  keys 6  shots 170  ocr 433
          answered_right=37 wrong_target=5 false_refusal=6
          false_refusal 6/48 (12.5%)  false_accept 0/0  stale 0  wasted 0  verify_giveup 0  re-reads 0
          fired-task pass 0/0  quiet 37/48  swapped 38  a_hit 20  a_hit_but_failed 0 (wrong_target 0 / twin 0)
          variant swap_twin_press 8/8   swap_hard_press 5/5   swap_hard_timer 5/5   swap_timer 5/5
                  swap_after_press 5/5   swap_race_timer 5/10   nb065 2/2   nb100 2/2   nb046 0/3   nb050 0/3
          race(pressed the replaced ask) 5/5 (after the guard's frame 5)
          guard gate sample 42  P50 366 ms  P95 400 ms  (criterion P50<=240, P95<=320)
```

- **判据达成**：twin **8/8**（批次 5 是 0/8）≥ 6/8 ✅；`a_hit_but_failed 0`（批次 5 是 8 = 0 wrong_target + 8 twin）✅；`race` 分母 **5/5** ≥ 5 ✅（批次 5 是 0/0）；核心 14 **10/14 → 12/14**，变化恰好 t0/t4（twin wrong→ok），**无 ok→wrong 翻转** ✅（t18/t21 两批都因 nb046/nb050 拒答）。
- **twin 逐题证据**：t0–t7 全部 `ok`，全部 `ask_word_from=painted`、`label_painted=1`、`label_text_like=1`、`label_alt_tried=1`（⇒ 8 次都是"多个出现里选中坐在被绘制块里的那个"）。t4 的 banner 被 OCR 读成 `GAMMI`（`ask_cells=0`），仍点对 `GAMMB` —— 这条路径与批次 5 的"文件仲裁"互补。
- **race 逐题证据**：t41/t42/t44/t46/t47 `detail.stale_press=True` 且 `detail.clicked == want`、`detail.want`（换题后真值）不同 ⇒ 正是"按了被替换的 ask"；t38/t39/t40/t43/t45 `stale_press=False` 且点对。`stats.press_delays=5`、`press_delay_ms=3560`（均值 712 ms，均匀 0–1200 期望 600）⇒ 抖动生效 5 次、恰好命中 5 次换题窗口。
- **成本**：`ms_askgate/ask_gates = 10073.1/68 = 148.1 ms`（批次 5 是 143.4 ms，**+3.3%**）；墙钟 **4677 ms/题**（批次 5 是 4823 ms，**−3.0%**，twin 不再重规划）；`ms_blocks 618.8`（新判据只在同词多现时才付 77 ms/帧）。**判据 `ms_askgate` P50 ≤ 240 / P95 ≤ 320 达标**——见下条口径说明。
- **口径说明（必须随数字一起引用）**：`gate_ms` 的计时**包含守门的那一帧截图**（`t_gate` 在 `self.shot()` 之前，`gym_run.py:1465-1468`），所以 P50 366 不能直接对判据；本次 `shots 170`/`ms_shot 37281.5` ⇒ 单帧 **219 ms**，`366 − 219 = 147 ms`，与独立算出的 `ms_askgate/ask_gates = 148.1 ms` 相差 1 ms ⇒ 判据口径（批次 5 的 `ms_askgate`，不含帧）下 P50≈147、P95≈400−219=181，**达标**。下一批把 `t_gate` 移到 `shot()` 之后（2 行）即口径一致。
- **第二次 sha 分裂（披露）**：chaos 首类第一次跑崩在 `gym_run.py:807 window_by_title`——`AttributeError: 'str' object has no attribute 'get'`。量到根因：actor 的 `uia windows` 回复在**列表被截断时混入字符串** `'(1 more items)'`（实测 7 条 = 6 dict + 1 str），而 `target_windows` 早就防了这一手（注释 "a locked or half-torn-down desktop can answer with bare strings - skip those"），`window_by_title` 漏了。⇒ 补同款 `isinstance(w, dict)` 守卫（3 行），`py_compile` 通过，并以真实回复验证（修前必崩、修后返回 `None`）。该守卫只在含 chaos 的路径上被调用 ⇒ 上面那批 `9db420c422a2` 的测量不受影响；chaos 三批另用新 sha。

### 9.3 第 5 步（chaos）结果 + 三条口径差

**chaos 三批**（键通道 `--keys --bg`，与鼠标批**串行**——驱动要求同一时刻恰好 1 个 gym 窗口；sha `ee68f457577d`，`app_args` 里带 `--chaos-ms 200,700`）：

| 批次 | 驱动自评 | `score.py` | shots | ocr | `replan` | 墙钟/题 |
|---|---|---|---|---|---|---|
| 控制（无 chaos）`t_trap2-w6c-control.json` | 60/60（100%） | **60/60 100.0%**，`false_refusal 0/46`、`race 0/0`、gate P50 189 / P95 224 | 197 | 385 | 15 | 2940 ms |
| `--chaos 0.35 --chaos-kind rebuild` `t_trap2-w6b-chaos35.json` | 59/60（98%） | （未即时打分，见口径差③） | 340 | 579 | — | 3198 ms |
| `--chaos 0.70 --chaos-kind rebuild` `t_trap2-w6c-chaos70.json` | 59/60（98%） | **58/60 96.7%**，`timeout 1` + `false_refusal 1`（`false_refusal 1/49`）、`race 0/0`、gate P50 184 / P95 208 | 412 | 676 | 48 | 3924 ms |

- **干扰确实注入了**：0.70 那批 app 侧事件文件实测 `chaos_planned 50 / chaos 50`（全是 `rebuild`）。驱动的 `disturbances: 0 fired` 是**另一个口径**（只数被弹窗挡住的次数）⇒ 两数不能互推。
- **代价与恢复**：驱动在扰动下重读显著变多（shots +109%、ocr +76%、`replan` 15 → 48、墙钟 **+33%**），通过率 **100% → 96.7%（−2 题）**：一题 `timeout`（重建后的判定没等到）、一题 `false_refusal`（本该点的题被拒）。
- `score.py` 末尾 `MISMATCH 1` = 驱动把那一题 `timeout` 记成了 `ok`（它读到的是**重建前**的判定）⇒ 这就是 chaos 下"驱动自评"与"联合真值"的唯一分歧点。

**三条口径差（都已写进 `../sol/sandbox/SCORE.md` 引用规则 5/6/7 与 `HANDOFF.md` §2）**：

1. **`--chaos-ms 200,700`（驱动默认）决定干扰几乎总落在驱动读题之前** ⇒ 这批测的是"**重读恢复**"，不是"过期按压"；race 在 chaos 批里仍是 `0/0`（那要 `swap_race_timer` + jitter，见批次 6 定稿批）。
2. **`gates` 标签按场景名分流**（`t_trap5→v3`、`t_trap*→v2`、else `v0`）⇒ 批次 6 代码跑的 `t_trap2` 批打的是 `v2` 标签；**代码版本一律看 `scripts_sha`**。
3. **run json 的 `events` 是一个路径**，而 app 每次启动**覆盖写**同一文件 ⇒ 只有**最后跑的那批**能把 per-run stale 归因对到自己的事件流。这就是"控制批重跑一次、逐批即时打分"（`t_trap2-w6c-*`）的原因；上表 0.35 那行因此只给自评分数。

**终止条件核对（照 m08820 的五条）**：核心 14 无 ok→wrong 翻转 ✅ / twin 8/8（不是 0/8）✅ / chaos delta 已解释且可复现（0.70 两次独立跑都是 59/60 自评、58/60 联合）✅ / "量"这步没被证伪（`fill_share` 反向 ⇒ 改用 `find_blocks` 块覆盖，假设保留）✅ / race 分母 5 ≥ 5 ✅ ⇒ **五条全部未触发**。批次 6 到此收口，本线不再裂 sha；剩下的都进了 §7 欠账。

## 10. 批次 7–8（欠账 #14 落地 + chaos 四类 + 批次 7 move 死锁的定位与修复）

**背景**：用户 m09250 的三条定论（#14 落地、race 记"踩线达标"不单独跑、其余欠账冻结）与 m09343 的 **Q2 二次修正**（chaos **四类都做**、不放弃任何一类，每类 2 强度 × ≥5 fire，标「探索性·不并入定稿」；`popup` 的前置验证单独记一行 ⇒ 见 §8.1）。

**sha**：批次 7 控制批 + move 批 = **`481154ca264d`**（= #14 落地后的代码，**只改文件命名、不改判定** ⇒ 与批次 6 的 `ee68f457577d` 数字可比）；批次 8（修 `ask_label_read` 哨兵）另记于 §10.3 之后。

### 10.1 批次 7 控制批 —— 同协议、改名前后逐格一致

`t_trap2-w7-control.json`（`--scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg`，21:42:33 起；**无 chaos**）：驱动 60/60（100%）、2934 ms/题、`shots 197`、`ocr 385`、`keys 70`、读屏 65 / 文件 10。`score.py`：

```
t_trap2  v2  60/60  100.0%  decided 100.0%  disturb 0  screen 51/60  replan 15  1428 ms/task  keys 70  shots 197  ocr 385
answered_right=46  refused_right=14      false_refusal 0/46 (0.0%)  false_accept 0/14 (0.0%)
swapped 15  a_hit 10  a_hit_but_failed 0 (wrong_target 0 / twin 0)   race 0/0
variant alpha020 2/2  alpha030 2/2  alpha035 2/2  alpha050 2/2  alpha065 2/2  prose_only 4/4  prose_with_button 6/6
        swap_after_press 10/10  swap_timer 5/5
guard gate sample 46  P50 186 ms  P95 244 ms
```

与批次 6 的 `t_trap2-w6c-control.json`（sha `ee68f457577d`）**逐格一致** ⇒ 证明 #14 的改名**没有碰任何判定**（这也是"只改命名"这一条可以放行收口的证据）。

### 10.2 批次 7 `move@0.70` —— 33/60 早停，两个 delta 已定位到同一缺陷

> ⚠ **`t_trap2-w7-move70.json` 是"修复前"的批，不可引用为 move 类定稿**（用户 m09520 定）：它在 `two_close_names` 上因守门假阳性卡住、`--max-repeat 3` 早退于 33/60。
> **move 类定稿看批次 8 的 `t_trap2-w8-move70.json`**（同一命令、同一 sha 系列，修的是"读不出 ⇒ 回落指纹"）。本节的数字只用于**定位根因**。

`t_trap2-w7-move70.json`（同协议 + `--chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5`，21:45:33 起）：驱动 **29/33 ok（88%），`stopping early: task 31 failed 3 times in a row`**；6746 ms/题、`shots 336`、`ocr 421`、`keys 35`。`score.py`：

```
chaos:move  v2  29/31  93.5%  decided 93.5%  disturb 0  screen 29/31  replan 28  1705 ms/task  keys 35  shots 336  ocr 421
answered_right=26  refused_right=3  timeout=2   extra_attempts 2 (rows collapsed to one per task)
false_refusal 0/28  false_accept 0/3  stale 0  wasted 0  verify_giveup 0
swapped 15  a_hit 4  a_hit_but_failed 0 (wrong_target 0 / twin 0)
variant prose_only 3/3  prose_with_button 5/6  swap_after_press 10/10  swap_timer 5/5   race 0/0
guard gate sample 26  P50 188 ms  P95 212 ms
timeout #15 truth=answerable dec=none act=click_label result=wrong clicked=null
timeout #31 truth=answerable dec=none result=none clicked=null
```

- **干扰确实注入了**：本批自己的事件文件 `t_trap2-w7-move70-events.jsonl` 实测 **`chaos_planned 26 / chaos 26`**（全 `kind=move`）⇒ ≥5 fire ✅（驱动的 `disturbances: 0 fired` 仍是"只数弹窗"那个口径）。
- **delta ①：`#30/#31/#32` 三行全是 app 的 task 31（`two_close_names`，ask `LUMEN93`），`result none`、`presses 0`、`decision none`、`replans 2`、`replan_why "no verdict arrived"`、`verdict_ms null`、`wall_ms 21151/21151/21786` ⇒ 连试 3 次 ⇒ `--max-repeat 3` 早停（33/60）。** 原始行关键字段：`ask_reread "DO: click the button labelled"`、`ask_label_read "DO: click the button labelled"`、`ask_cells 0`、`ask_delta 0.0`、`ask_changed_text true`、`ask_moved_text 1`、`ask_moved 3`、`ask_word LUMEN93`、`ask_word_from exact`。
- **根因（读码定位，非猜；口径按用户 m09426 指定）**：**`move` 干扰下记录的 `ask_box` 在重读时失效**——重读回来的是一段**干净的句子前缀**（`"DO: click the button labelled"`），说明取景框**边缘切在 label 之前**、`ask_box` 已不再覆盖当帧的标签词；于是 `ask_label_now` 的 `labelled (.+)$` 取不到词、返回**哨兵 `""`**（旧 `gym_run.py:1351-1352`），而 `ask_text_changed` 把 `""` 当**变化**（旧 `1377-1379`）⇒ **同一帧指纹说"没动"（`ask_cells 0`/`ask_delta 0.0`）而文本路径说"变了"** ⇒ 守门不放行 ⇒ 重规划 ⇒ 死循环。该函数 docstring（`gym_run.py:1315-1317`）从批次 5 起就写着 "an unreadable read is not evidence that the question moved" ⇒ **实现与自己的契约相反**。**次级假设（未排除、不主导）**：OCR 在 6 px padding 的窄条上漏读末词——同属"读不到"，修法一致。分类：**可修**（不是异常：无 traceback；不是超时：压根没按；是判据缺陷）。
- **delta ②：`a_hit` 10（控制）→ 4（move），而 `wrong=0`、`swap_after_press 10/10`** ⇒ 不是按错，是**首次按压被推过 8 s 安全换题线**（`gym_app.py:1403 if after_press: self.after(8000, lambda: swap("safety"))`）⇒ 按到的是换题后的 B（正确 ⇒ 仍 ok）但 `a_hit=False`。**逐题核对（用户 m09426 要求：`a_hit=false` 且 `wall_ms>8000` 是否恰为 6 题）**：**是，恰为 6 题**——`#1 #4 #5 #7 #8 #9`（墙钟 10.65–10.88 s，全部 > 8000 ms）；反方向也干净：`a_hit=True` 的四题墙钟 4.35–4.61 s，**没有一题 > 8000 ms**；控制批十题全 `a_hit=True`、墙钟 6.62–6.97 s（到 8 s 只剩 1.0–1.4 s 余量）⇒ **机制成立**。⇒ `a_hit` 不是独立指标，是"守门假阳性把按压推过换题线"的**读出量**。

### 10.3 批次 8 —— 假设与证伪条件（先写，后改，再跑）

**假设（一行）**：批次 7 `move` 批的 `LUMEN93` 死锁（`none` × 3 ⇒ 33/60 早停）与 `a_hit 10→4` 是**同一个缺陷**——`ask_label_now` 把"读不出标签"当成 `""`、`ask_text_changed` 把 `""` 当成"问题变了"，于是**一次读失败被当成一次换题**；修掉哨兵语义（读不出 ⇒ `None` ⇒ 交给指纹判），两处 delta 应同时消失。

**改动（批次 8，三处都在 `gym_run.py`；不动任何匹配/阈值）**：(a) `ask_label_now` 读不出标签 ⇒ `return None`（= 交给指纹判）+ 记 `ask_read_unreadable`；(b) `ask_text_changed` 的 `""` 分支 ⇒ `return False`（同一立场、同样计数）；(c) **通用退化规则**（用户约束：**不能只对 `click_label` 类 ask 生效**）——重读 `_plain(got)` 与 `_plain(want)` **不含任何连续 ≥2 字符子串**时判"没读到这个词"，回落指纹并计数（实测 `DOCLICKTHEBUTTONLABELLED` vs `LUMEN93` 无 2 字子串）。选**子串规则**而非剥离 `labelled` boilerplate：它对 **refuse 类 ask** 同样成立，不依赖 ask 形态。**Option A（每帧重算 banner box）本批不做**，进欠账 #15。

**证伪条件（三条，任一命中就停并写欠账）**：i. 修后 `move@0.70` 仍出现 `result none` + `presses 0` + `replans ≥ 1` 的题；ii. `a_hit` 仍 < 8/10，且 `a_hit=False` 的题墙钟仍普遍 > 8 s；iii. 核心 14（`t_trap2` 子集 `[0,4,9,10,13,14,18,21,24,26,28,29,33,34]`）出现新翻转或 `stale > 0`。

**判据（达标线）**：`ask_read_unreadable > 0`（证明该分支确实被触发过，而不是改动没生效）②`move@0.70` 无 `none` 题、不再早停（跑到 60 题或 ≥5 fire 的协议上限）③`a_hit ≥ 8/10`。

### 10.4 批次 8 结果（chaos 四类 × 2 强度；sha `f598406cfc70`；**探索性·不并入定稿**）

**逐条对判据**：

| 判据 | 结果 | 证据 |
|---|---|---|
| i. `ask_read_unreadable > 0` | ✅ **2 次，全部落在 `task 31`** | `t_trap2-w8-move70.json`：`task 31` 就是批次 7 卡死那题；这次正常作答 |
| ii. 无 `none` 题、不早停 | ✅ 跑满 60 题、`result none` 0 行 | driver `58/60`（另两行是 `wrong`/`timeout`，不是卡死） |
| iii. `a_hit ≥ 8/10` | ❌ **未达标（4/10、7/10）** | 见下；`a_hit` **不是独立指标**（§10.2 delta ②、`HANDOFF.md` 盲区 15）：0.70 档没按中的 6 题墙钟 10.86–11.17 s、按中的 4 题 4.58–4.92 s；0.35 档没按中的 3 题 10.58–10.98 s、按中的 7 题 4.32–4.59 s |

**四类 × 2 强度**（`--keys --bg`，60 题/批，`--chaos-ms 200,700`，每批即时打分、自带留档）：

| 类 | 强度 | driver | `score.py` | app 侧 fire | 停法 |
|---|---|---|---|---|---|
| `move` | 0.70 | 58/60 | `58/60 96.7%` decided 98.3% · replan 35 · 1708 ms/题 · `race 0/0` · `a_hit_but_failed 0` | `49/49` | 跑满 |
| `move` | 0.35 | 60/60 | `60/60 100.0%` decided 100.0% · replan 28 · 1649 ms/题 | `27/27` | 跑满 |
| `slow` | 0.35 | 58/60 | `57/59 96.6%` decided 96.6% · `swap_timer 3/5` · **`race 0/2`** | `24/24` | 跑满 |
| `slow` | 0.70 | 57/60 | `51/54 94.4%` decided 100.0% · **`race 2/2`** · **`false_accept 1/14`** · `MISMATCH 1` | `41/41` | 跑满 |
| `popup` | 0.35 | **4/7** | `4/5 80.0%` | `1/1` | **早停**（task 4 三连 `NONE`） |
| `popup` | 0.70 | **1/4** | `1/2 50.0%` | `1/1` | **早停**（task 1 三连 `NONE`） |

- **`move` 类的两处 delta 都还在**（不是同一缺陷的另一半）：`#15` `prose_with_button`（`stale_actions 1`、`dec=none`）与 `#34` `two_close_names` **点错 `TUNDRA`**（`wrong_target 1`）；`a_hit` 的剂量-反应见上表判据 iii ⇒ **修好的是死锁，不是 `a_hit`**。
- **`slow` 类把批次 6 判定"机制上不可能"的 race 重新打开了**：`slow` 把靶子判定推后 1.5–3.2 s ⇒ 老 `swap_timer`（600–1000 ms）的窗口重新落到**守门抓帧之后** ⇒ `race 0/2`、`2/2`，**两档都是同一对 task（#10/#14）**。同族还带出本项目第一次 `false_accept 1`（`#44`）与 `MISMATCH 1`（同一 `task_i` 被重复尝试、行按 task 折叠，`extra_attempts 6`）。
- **`popup` 类当前测不了**（**驱动能力缺口，不是脚本 bug**）：弹窗标题 `"attention"`（`gym_app.py:605-655`），但 `dismiss_interference` 在 `--keys --bg` 下只按标题找它、**没找到**（`disturbances: 0 fired`）⇒ 弹窗留屏 ⇒ 驱动的按键被吃（`dec=acted` 但 `result=none`）⇒ 该题永不结束、靶子也不推进 ⇒ 两档各只 fire 1 次后早停。
- 口径提醒：非 `popup` 类打印的 `fired-task pass 0/0` 是**口径使然**（`score.py:278` 的 "fired" = 驱动侧 `interferences`，只数弹窗）；注入率引用 app 侧 `-events.jsonl`。`stale N`（驱动 `stale_actions`）与 `race X/Y`（app `trap_stale_press`）是两个计数。

## 11. WSL 探测（2026-10-05；结论：**放弃 WSL 做 GUI 靶场**，WSL 保留为工具链）

> 提问（用户 m09794 / m09853）：能不能把靶子或驱动搬进 WSL（WSLg），只换掉"抓帧/发键"两处？
> 判定**只允许三个**：走 A（靶子+驱动全在 WSL）/ 走 B（靶子在 WSL、驱动在 Windows）/ 放弃 WSL。
> 纪律：**不改三件套**（探测前后 sha256 前 16 位一致：`gym_app.py 66632D85EAC81C12`、`gym_run.py 61FD81D5795CF158`、`score.py F9CEFB9FBCF7D8CE`）、**不碰批次证据**（探测的 state/events 全指到 `/tmp`）、探测进程跑完即 kill（收尾核对：WSL 侧无残留）。

### 11.1 七条清单（逐条：能/不能 + 最小证据）

| # | 问题 | 结果 | 证据 |
|---|---|---|---|
| ① | 发行版 / WSLg / DISPLAY | ✅ | Ubuntu 24.04.5 LTS、内核 `6.18.40.1-microsoft-standard-WSL2`、`DISPLAY=:0`、`WAYLAND_DISPLAY=wayland-0`、X11 socket `/tmp/.X11-unix/X0`、`/mnt/wslg` 有 weston.log/PulseServer |
| ② | WSLg 里起 Tk 窗 | ✅ | `tk 8.6 / screen 2560x1600 / dpi=96`；窗口确实出现在 Windows 桌面 |
| ③ | **Windows 侧能枚举该窗（第一闸）** | ✅ | `uia what=windows`：`hwnd=393250 cls=RAIL_WINDOW title="wslg-probe-7f3a (Ubuntu-24.04)" rect=[28,28,584,385]`；`state` 的窗口表同样列出 |
| ④ | WSL 侧抓自己的 X11 屏 | ⚠ **能抓窗、抓不了根** | 抓窗 ✅ `import -window 0x600019` → 480x260 `mean=0.859`；抓根 ❌ mss `full=2560x1600 full_mean=0.0`、`import -window root` 报 `unable to read X window image 'root': Resource temporarily unavailable @ error/xwindow.c/XImportImage/5004` |
| ⑤ | WSL 侧发键到 X11 窗 | ⚠ **只在窗口已被激活时才通** | 刚映射（被 WSLg 激活）时 `xdotool key a` / `type 'hi'` → Tk 收到 `KEY #1..#10`，标题变 `-keys10`；**一旦失焦就全灭**：`windowfocus --sync` 返回 0 但紧接 `xdo_focus_window reported an error`、`windowactivate` 报 `XGetWindowProperty[_NET_ACTIVE_WINDOW] failed (code=1)`（weston 的 XWM 不支持 EWMH）、定向 `xdotool key --window`（XSendEvent）零事件 |
| ⑥ | **现有 `gym_app.py` 不改代码在 WSLg 跑** | ✅ | 直接 `python3 gym_app.py --seed 7 --state /tmp/gym_wsl-state.json --events /tmp/gym_wsl-events.jsonl`：`{"event":"ready","task_i":0,"scenario":"t_toggle","ask":"set lumen ON and the slider to 7","layout":{"origin":[291,155],"size":[1180,780]}}`；state 366 B、字段齐；X 窗名 `GUI Gym`；Windows 侧 `hwnd=199002 cls=RAIL_WINDOW rect=253,96,1509,973`、PrintWindow 35172 B、主色 `[244,244,252] n=768154` ⇒ 渲染正常且被 Windows 看到 |
| ⑦ | `gym_run.py` 平台相关性 | 主体无关，耦合集中在 4 处 | 见 11.2 |

### 11.2 第 7 条：`gym_run.py`(3465 行) 逐块判定

- **与平台无关（逻辑主体）**：OCR 文本地图、`ask` 解析、守门（`press_guard`/`ask_label_now`/`ask_text_changed`）、五判定、重规划、chaos 干扰处理——都是 `numpy`/`PIL`/字符串运算。`gym_run.py` 内 `8731`/`urllib`/`socket`/`mss`/`sys.platform`/`os.name` 的命中数**全是 0**。
- **耦合 1｜抓帧 + OCR**：`gui_see.py`（硬编码 `TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`，抓帧走 actor 的 `shot`）。WSL 侧要换 `import -window <id>`/mss + Linux tesseract。
- **耦合 2｜输入**：`loop.Actor`（TCP `:8731` 的 `click/drag/type/key/scroll`）。WSL 侧要换 xdotool——而 ⑤ 已证它在失焦窗上不可用。
- **耦合 3｜Windows 专属辅助**（三处）：`target_pids()`/`kill_stale()`（PowerShell `Get-CimInstance Win32_Process` + `taskkill`）；`foreground_info()`/`lock_reason()`（`ctypes.windll.user32` 查前台进程名/类名判断"是否锁屏"）；`foreground_via()`（actor `window mode=foreground`）。WSLg 窗口的宿主张是 `msrdc.exe`/`wslhost`，这些检查在 WSLg 上语义失效。
- **耦合 4｜后台通道**：`--bg` = PrintWindow 抓帧 + `window mode=focus` + PostMessage 键/鼠标。

### 11.3 清单外的实测（B 路线的关键补充）

- **Windows 侧能看到 WSLg 的真实像素**：整屏 `probe colors` 命中原色 `[44,108,180] n=9602`（= 画布 `#2b6cb0` 的 120×80）；且**该窗被 DSH 窗完全遮挡时**，`shot hwnd=`（PrintWindow）仍拿到真内容——556×357 图里蓝色像素 9660 px + 浅灰 `#D8D8D8`，不是遮挡窗的画面 ⇒ 抓帧这一环与现有 Windows 通道**等价**。
- **Windows 侧真输入 ✅**：`click front=<hwnd>` → Tk 收到按下+抬起（标题 `b0→b2`）；`key front=<hwnd>` → `k1→k2`。
- **PostMessage：鼠标 ❌、键盘 ✅（需先给焦点）**：`click bg=` 与 `type bg=` **无任何事件**；先 `window mode=focus`（**不动前台**）再 `key bg=` → Tk 收到 `k1` ⇒ **后台键通道在 WSLg 上可用**（与原生 Tk 的"鼠标被丢弃、键盘有效"完全同型）。
- **几何不一致（B 的标定成本）**：X11 客户区 `480x260 @ (104,146)`；Windows `uia` 矩形 `556×357 @ (28,28)`；PrintWindow 图（556×357）内蓝块 bbox `120x128+48+69`，而 X11 侧蓝块在客户区 `(10,10)-(130,90)` ⇒ 三者不是同一取景，B 必须先做一次坐标标定。
- **字体**：WSLg 侧 `fonts_total=7 dejavu=True noto_cjk=False` ⇒ 中文缺字、度量与 Windows 不同 ⇒ OCR 链（`psm`/阈值）得重调（**本批不做**）。
- **抢前台**：WSLg 窗口**每次映射都会抢走 Windows 前台**（实测两次）；`window mode=focus` 不抢。

### 11.4 结论 → **放弃 WSL（就 GUI 判分线而言）**

- **走 A（全在 WSL）不可行**，三条实测死因：①抓不了整屏（根窗口不可读）⇒ 驱动的"整屏帧"前提不成立，只剩"抓自己那一个窗"；②发键在失焦后**没有任何 X 侧手段**（EWMH 不支持、XSetInputFocus 报错、XSendEvent 零事件）⇒ 只能等 Windows 侧把它激活，**A 反而绕不开抢前台**；③WSL 到不了 actor `:8731`（NAT 下 Windows 只监听 loopback）⇒ 现有执行器、锁屏检查、进程清理全部不可用。
- **走 B 技术上成立**（第一闸过、抓帧过、真输入过、后台键通道过、靶子原样跑），但**不带来现有 Windows 线没有的能力**：抓帧同为 PrintWindow、键通道同为 `focus`+PostMessage、鼠标同为真输入（都要抢前台）；代价却是几何标定 + 耦合 3 的三处辅助重做 + 字体差异导致 **OCR 链重调 ⇒ 既有全部数字不可比**（口径规则禁止静默复用旧数据）。
- 所以本线的动作：**Windows 原生靶子保持不变**；WSL 的实测价值在**工具链**（`jq`/`rg`/管道：已用它独立复算批次 8 的 `chaos` fires `49/27/24/41/1/1`、`trap_stale_press` slow 两批各 `2`、`verdict_delayed 23/40`、`trap_a_hit 4/7/10/10`，与 `../sol/sandbox/SCORE.md` 逐项一致）。
- **可翻案条件**（将来若要 Linux 原生靶场）：先补 ⑤（找到可靠的 X 侧焦点/注入手段）与 CJK 字体，再重标 OCR；那是**新口径**，必须单独标注，不得与 v1/v2/v3 混用。

### 11.5 本批没动的东西

三件套 sha256 未变（见 11.1 开头）；未启批次；未改任何既有结论；探测脚本只在 `/tmp`（`wslg_probe_tk{,2,3}.py`、`x11_grab.py`），进程已全部 kill；actor 守护进程 `:8731` 起过一次（pid 12008），收尾时把用户前台还原为原窗口。

## 12. 批次 9（欠账 #10 + #11）—— 假设 / 先量 / 改动 / 证伪

**本线第 9 次裂 sha（只 `gym_run.py`）。顺序：先技能落盘（不裂 sha，已完成）→ 再本批。**

### 12.1 假设（动代码之前写，2026-10-05 第二段开工）

「#10（`t_gate` 移到 `shot()` 之后）与 #11（`press_delay_ms` 进逐题行）是两条纯口径/诊断改动，**不动判定逻辑**，对既有数字无影响，只让两个口径自洽。」

**证伪条件（任一命中 ⇒ 停、写欠账、不硬推）**：
- i. 移后 `gate_ms` P50 与独立口径 `ms_askgate/ask_gates` 仍差 > 20 ms ⇒ 计时点找错了；
- ii. 逐题行没有 `press_delay_ms`，或逐题行合计与 `stats` 聚合不一致 ⇒ 记录路径错了；
- iii. 核心 14（同 `task_i` 子集）出现 ok→wrong 翻转 ⇒ 改动有副作用；
- iv. `race` 分母 < 5 ⇒ jitter 没生效；
- v.（本批新增，实测逼出来的）**行内 `gate_ms` 样本总数 ≠ `stats.gate_samples`** ⇒ 还有别的丢数路径。

**判据**：i–v 全不成立；`gate_ms` P50 与 `ms_askgate/ask_gates` 差 ≤ 10 ms；逐题行 `press_delay_ms` 合计 == `stats.press_delay_ms`；核心 14 无 ok→wrong 翻转；`race` 分母 ≥ 5。

### 12.2 「先量」实测（批次 6 `t_trap5-1.json` —— 原规格的估算不成立，作废重写）

- **#11 实测**：`stats.press_delays = 5`、`stats.press_delay_ms = 3560.0`，但逐题行只有 **3 行**带 `press_delay_ms`（`task_i` 41/42/44 = 727/1178/1088 ms，合计 **2993 ms**）⇒ **567 ms 无归属**；10 个 `swap_race_timer` 题里另有 7 行 `replans = 1` 却完全没有 jitter 痕迹。
- **#10 实测**：逐题行 `gate_ms` 样本**总共 42 个**，而 `stats.gate_samples = 75` ⇒ **33 个样本（44%）也没进逐题行**；旧口径 P50 = **369.7 ms**（含抓帧），独立口径 `ms_askgate/ask_gates = 10073.1/68 = 148.13 ms`。
- **共同根因**：`_redo()`（`gym_run.py:261-286`）用 `again = d.do_task(...)` **换掉整条记录**，只续带 `replanned / replans / ask_moved / ask_cells / ask_delta / ask_before_replan / ask_replan_read / replan_why / interferences` —— **不带 `press_delay_ms` / `press_jitter_task` / `gate_ms`**；调用点 `gym_run.py:3307`（ask re-rolled）与 `3331`（no verdict arrived）。所以欠账 #11 的措辞「只进 `stats` 聚合」**不准确**：它确实写了逐题行，只是**被 replan 丢掉了**。
- 结论：**改动是三处，不是两处**（第三处是纯记账续带，不改任何判定路径，也不碰用户写下的"不动"清单）。

### 12.3 改动清单（三处，全在 `../sol/sandbox/gym_run.py`）

- ① **#10** `press_guard`：`t_gate = time.time()` 从 `self.shot()` **之前移到之后**（`1499/1500`）。
- ② **#11** 逐题行组装（`3341-3343`）：往 `detail` 里注入驱动侧 `press_delay_ms`（`detail` 由 app 判定 `v` 提供，必须在组装这行注入，否则被覆盖）。
- ③ **记账续带** `_redo`（`261-286`）：续带 `press_delay_ms` / `press_jitter_task` / `gate_ms`。
- **不动**：`press_guard` 判定逻辑、`ask_label_now`、`ask_text_changed`、`painted_hit`、匹配路径、阈值。

### 12.4 跑批

- 命令（用户给的原命令；其 venv 路径少一个反斜杠，已修正）：`cd D:\DSH\vision-work\sol\sandbox` → `D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out t_trap6-1.json`。
- 已知前提：`--seed` 只递给 app（`gym_run.py:3169-3170`），**驱动侧 jitter 用未播种的 `random`** ⇒ 跨批不比毫秒值，只比"是否 fire / 是否 stale / `race` 分母"。
- 新文件名 `t_trap6-1.json`，不覆盖批次 6 的 `t_trap5-1.json`；跑完**立刻** `score.py`（引用规则 7：app 的 events 会被下一批覆盖）。
- 结果与终版数字见 12.5。

### 12.5 结果与判据核对（2026-10-05，跑完**立刻**打分）

- **定稿行**：`t_trap6-1.json`，sha `f473ff21ad09`（口径 v3、鼠标通道、48 题、**36/48**；批次 6 = 37/48，逐题只差 race 家族三题）。
  三件套留档齐：`t_trap6-1.json` / `t_trap6-1-state.json` / `t_trap6-1-events.jsonl`（`--json-out` 自动命名 ⇒ 欠账 #14 的机制复用，事后可用 `--events` 复核）。
- **判据核对**：i **边缘未达**（`gate_ms` P50 **124.1** vs 独立口径 `ms_askgate/ask_gates` **134.68** ⇒ 差 **10.58 ms**，目标 ≤ 10 ms，**证伪线 20 ms 未触发**）；
  ii ✅（逐题行 6 行 `press_delay_ms` = 577/1029/562/480/911/942，**合计 4501 ms == `stats.press_delay_ms` 4501.0**，`stats.press_delays` 6）；
  iii ✅（核心 14 **12/14 → 12/14**，ok→wrong 翻转 **0**；变化的只有 #36 ok→wrong、#44 wrong→ok、#45 ok→wrong，三题全在 race 家族）；
  iv ✅（`race` **6/6** ≥ 5）；v ✅（行内 gate 样本 **74 == `stats.gate_samples` 74**；批次 6 是 42 vs 75 ⇒ 33 个样本丢在 `_redo`）。
- **`gate_ms` 换了范围**：批次 6 = 含抓帧 P50 368.0 / mean 365.33（n=42）→ 批次 9 = 只守门 P50 124.1 / mean 122.27（n=74），差 ≈ **244 ms** ≈ 一次 `shot` ⇒ **两批不可并列**（写进 `../sol/sandbox/SCORE.md` 批次 9 ②）。
- **第一次尝试作废（1 次，教训，已写进 ../sol/sandbox/SCORE.md 批次 9 ⑥）**：驱动由 **WSL 后台作业**启动 ⇒ app 窗口起来就是 `-32000`（app 自报 `layout.origin`，每条事件都是）⇒ 帧全空 ⇒ 0 次按压 ⇒ 首题 `WRONG` 后
  `shot failed: {"error": "ValueError: cannot write empty image"}` ⇒ `gym_run.py:508 raise SystemExit`（设计如此：空帧 = 会话不可用，宁可退出也不产假分）⇒ **不写 run json**，只留 state/events + 僵尸 app（venv shim + 运行时 = **2 进程**，属一个健康靶子）。
  排除项：**不是代码**（新代码干跑 `--tasks 2` **2/2 OK**、`py_compile` 过、`score.py --selftest` **41 项 0 失败**）、**不是残留窗口**（全场只有 1 个 gym 窗）、**不是锁屏**（`lock_waits 0`、无 LogonUI）。
  **定式（以后照做）**：跑批一律 **Windows 侧**启动，且显式正常显示状态 —— `Start-Process -FilePath <venv python> -ArgumentList "<sandbox>\gym_run.py", … -WorkingDirectory <sandbox> -WindowStyle Normal -RedirectStandardOutput <log>`；**先干跑 `--tasks 2`** 看首题有没有真按压，再跑正式批。
- **本批没动的东西**：判定逻辑（`press_guard` / `ask_label_now` / `ask_text_changed` / `painted_hit` / 匹配路径 / 阈值）一字未改；`gym_app.py` `66632d85eac81c12`、`score.py` `f9cefb9fbcf7d8ce` 未变，只有 `gym_run.py` 变（`61fd81d5795cf158` → 新 sha，合并 sha `f473ff21ad09`）。

## 13. #4 前置量（守门每帧重算 banner box）—— 机制 / 成本 / 改法草案（2026-10-05 第三段，**只量不改**）

**性质**：只读探针 + 草案，**未写一行代码**；三件套 sha 未变（`4ae46f4cda176671` / `66632d85eac81c12` / `f9cefb9fbcf7d8ce`）。探针脚本（自有文件，不在沙箱内）：`D:\DSH\dsh-actor\tmp\w4_boxprobe.py`（A/B 段）、`w4_boxprobe_c.py`（C 段）。

### 13.1 机制确认（证据 = 批次 7 `t_trap2-w7-move70.json` 的 `task_i=31` 行）

- **原始行**（`i=30/31/32` 三行逐字段相同）：`ask "click the button labelled LUMEN93"`；`ask_box [18,20,342,19]`（**进题时冻结的窄框**）；`ask_reread`/`ask_label_read` = `"DO: click the button labelled"`（**label 整段丢失**）；`ask_cells 0`、`ask_delta 0.0`（指纹：band 没动）；`ask_changed_text true`（文本路径：说变了）；`ask_moved_text 1`、`ask_moved 3`；`presses 0`、`decision "none"`、`result "none"`、`replans 2`、`wall_ms 21325/21151/21786` ⇒ 重规划死循环 ⇒ `--max-repeat 3` 早停（批次 7 `move` 29/33）。
- **机制**：`ask_label_now`（`gym_run.py:1316-1357`）**永远用 `rec["ask_box"]`**（进题时算好、之后冻结），`pad=6`、`psm="7"`、`scale=2`。干扰把 banner 右移后，**框的左边缘留在旧位置、右边缘切在 label 之前** ⇒ 重读只剩前半句 ⇒ `labelled (.+)$` 取不到词 ⇒（旧代码）`return ""` ⇒ `ask_text_changed` 把 `""` 当成"问题变了" ⇒ 守门不放行。
  （这条**判据缺陷**批次 8 已修：读不出 ⇒ 不再判"变了"，并计 `ask_read_unreadable`。**本欠账要修的是剩下的一半：框本身**。）
- **复现**（合成 `move`：两张**真帧**各整体右移 40 px，只读）：`base + 旧框` → `"DO: click the button labelled ONYX"` ✅；**`右移40 + 旧（冻结）框`** → `"7 DO: click the button labelled ON"` / `"| DO: click the button labelled HARB"`（**尾巴被裁，形状与 task 31 一致**）；**`右移40 + 用当前帧重算框`** → `"- DO: click the button labelled ONYX"` / `"- DO: click the button labelled HARBOP"`（**整词恢复**）。
- ⇒ 结论：**这不是 OCR 漏读，是取景框冻结**。同一帧、同一 OCR，只把框换对就读全（`reread()` 返回纯 `str`）。

### 13.2 成本实测（两张真帧，`_gym_shot.png` / `probe-w6-twin.png`，均 1180×780）

| 做法 | 实测 | 说明 |
|---|---|---|
| 全量 `chrome()`（像素段 + 逐行 OCR + band 复读） | **mean 193.5 / p50 195.9 ms**（n=4）；另一帧 183.1 / 183.4 | 含 2 次 OCR/帧 |
| **只跑像素段（不 OCR）** | **mean = p50 = 3.6 ms**（两帧各 n=20） | 就是"重算 box"需要的全部 |
| 像素段算出的 box vs `chrome()` 的 OCR box | `(18,20,425,19)` vs `(18,20,425,19)`；`(18,20,459,19)` vs `(18,20,458,19)` | **差 ≤ 1 px ⇒ 不用 OCR 也能算对框** |
| 参照：批次 9 守门重读 | `ms_askgate/ask_gates` = **134.68 ms/门**；`gate_ms` P50 124.1 | 守门本来就要抓一次帧 |
| 参照：单次 OCR | `ms_ocr/ocr` = **175.5 ms/次**（含 4x 首读） | —— |

⇒ **每帧重算 box 的成本 = +3.6 ms，只在"守门已抓帧、准备按下去"时付一次**（不新增抓帧、不新增 OCR）；相对守门总成本 ≈ **+2.7%**。

### 13.3 改法草案（不写代码）

- **位置**：`press_guard`（`gym_run.py:1486+`）里 `img = self.shot()` **之后**、`ask_moved_now(rec, img)` **之前**。
- **复用什么**：把 `chrome()`（`980-1065`）的**像素段**（`darkfrac` → `top` → `y1` 增长 → `ink(y)` → 列范围）抽成一个**无 OCR 的纯函数**，返回 `(x, y, w, h)`；重算后**只换重读用的框**（保留 `pad=6`），指纹基线暂不动。
- **时机（三选一，建议 B）**：**A** 只在守门里重算（+3.6 ms/门，最小）；**B** 守门里重算 + `ask_label_now` 用重算框（+3.6 ms/门，让"文本通道"和"指纹通道"看**同一帧同一框**）；**C** 每帧全量 `chrome()`（+190 ms/帧，**不必要**——像素框已与 OCR 框一致）。
- **记账**：新增两个计数进 `stats` 与逐题行（`ask_box_recomputed`、`ask_box_shift_px`），事后可核对"框真的被移动了多少"；`ms_askgate` 照旧累加。
- **边界**：若重算框与旧框位移过大（例如 > band 宽的 1/3）**且仍读不出** ⇒ 如实判"读不出"并按批次 8 的规则处理，**不拿"读不出"当"问题变了"**。
- **不动**：`press_guard` 的分支结构、`ask_text_changed` 的退化规则、匹配路径与阈值（本批只换"框从哪来"）。

### 13.4 明天开"改"的判据（草案，待确认）

- **主判据（沿用 §7 #15）**：`move` 类（或前台批次）里 **`ask_read_unreadable` 降为 0**，且 task 31 类的读题死循环消失（该题 `replans` 不再因读题退化累积）。
- **副判据**：核心 14 无 ok→wrong 翻转；`gate_ms` P50 增幅 ≤ 10 ms（预期 ≈ +3.6 ms）；`ask_guard_skipped` 仍为 0；`race` 分母照旧 ≥ 5。
- **证伪**：若重算框后 `ask_read_unreadable` 仍 > 0，或核心 14 出现翻转 ⇒ 说明失效不只是取景框 ⇒ 回退并记"机制未确认"。
- **风险（明天别踩）**：①像素框在**合成帧**上会退化成整带框（`(0,0,483,56)`；真帧上没出现）⇒ 实现时要 clamp 到 banner band 内取墨迹行/列；②若把 `ask_sig`/`ask_cells` 指纹基线也改用新框，**指纹语义会变** ⇒ 建议本批**只换重读框**（改动面最小、口径最稳）。

## 14. 批次 10（欠账 #4）—— 假设 / 改动 / 跑批 / 判据（2026-10-05 第四段，**动代码之前先写**）

**本线第 10 次裂 sha（只 `gym_run.py`）。** 用户规格（m10393）一句话：「开 #4 的"改"：只换重读框，不换指纹基线。裂一次 sha，跑一批 move70，判据四条。出问题就停，写欠账，不硬推。」

### 14.0 开工前确认（只读，已完成）
- 三件套 sha 逐字相符：`gym_app.py 66632d85eac81c12`(81169 B) / `gym_run.py 4ae46f4cda176671`(192782 B) / `score.py f9cefb9fbcf7d8ce`(38958 B)；无后台任务（bash-1 / pwsh-49 均 completed）。
- actor `:8731` ping ✅（`pid 12008`、`uptime 2228.4 s`、`geom 2560x1600`、`dpi per-monitor`、`py 3.12.14`）；`state`（44.3 ms）foreground = **DSH 窗**（`hwnd 132886`）⇒ 用户前台未被占。
- 顶层窗口表里 **`GUI Gym` 窗口数 = 0**；`Win32_Process` 匹配 `gym_app|gym_run` 的进程数 = **0** ⇒ 无残留、可开新靶。
- 目标文件名 `t_trap2-w9-move70.json` 尚不存在 ⇒ 不覆盖批次 7/8 的任何文件。

### 14.1 假设（一句话）
「`ask_box` 在进题时冻结 ⇒ `move` 干扰把 banner 右移后，框中线留在旧位置、**右边缘切在 label 之前** ⇒ 守门重读只剩前缀 `"DO: click the button labelled"` ⇒ 文本路径说"变了"、指纹说"没变" ⇒ 守门不放行 ⇒ 重规划死循环。改成**每帧重算 banner box**（只跑像素段、不跑 OCR；§13.2 实测 **+3.6 ms/门**）后，`ask_read_unreadable` 应降为 0。」

### 14.2 证伪条件（任一命中 ⇒ 停、写欠账、不硬推）
- i. 修后 `move@0.70` 仍出现 `ask_read_unreadable > 0` 的题 ⇒ 失效不只是取景框；
- ii. 修后仍出现 `result none` + `presses 0` + `replans ≥ 1` 的题 ⇒ 读题死循环还在；
- iii. 核心 14（同 `task_i` 子集）出现 ok→wrong 翻转 ⇒ 改动有副作用；
- iv. `gate_ms` P50 相对批次 9（**124.1**）涨 **> 30 ms** ⇒ 成本超判据（§13.4 草案写的 ≤ 10 ms 是估的；本批以用户规格的 **30 ms** 为准）。

### 14.3 观测点
`ask_read_unreadable`、`result none` 行数、`replans`、核心 14 逐题 ok/wrong、`gate_ms` P50/P95、新增计数 **`ask_box_recomputed`**（+ `ask_box_shift_px` = 重算框相对冻结框的位移）。

### 14.4 判据
i–iv 全不成立；`ask_read_unreadable` 在 `move@0.70` 降为 **0**；无 `none` 题；核心 14 无 ok→wrong 翻转；`gate_ms` P50 涨幅 ≤ **30 ms**。

### 14.5 改动清单（三处，全在 `../sol/sandbox/gym_run.py`）
- ① **新增 `Driver.ask_box_now(self, img)`**（纯像素段，不 OCR）：`(g<100).mean(axis=1) > 0.55` 扫前 220 行找 `top`（**找不到 ⇒ `None`**，退回冻结框）→ `y1` 沿 `> 0.30` 增长、上限 `BANNER_BAND=150` → 取 `nd[y] > 6` 的墨迹行 → 列范围限制在 `x ∈ [14, width-14]`（与 `chrome()` 的 `region=(14, …, width-28, …)` 同约定：最左 14 px 是 OCR 会把边框伪影读成 `"3"` 的地方）→ **clamp** + 最低尺寸门槛（`bw ≥ 20 and bh ≥ 6`）⇒ 返回 `(x, y, w, h)` 或 `None`（§13.4 风险 ① 的 clamp 落在这里，并写进代码注释）。
- ② **`ask_label_now`**（`1316+`）：在 `bx, by, bw, bh = rec["ask_box"]` 之后插入重算 —— 有结果就**用它**（`rec["ask_box_recomputed"] += 1`、`stats["ask_box_recomputed"] += 1`，首次位移记 `rec["ask_box_shift_px"] = [dx, dy]`），没有就**照旧用冻结框**；`pad=6` 保留。重算发生在 `t0` 之后 ⇒ 成本计入 `ms_askgate`（诚实记账），也计入逐题 `gate_ms`。
- ③ **记账**：逐题行组装（`3355-3361`，`detail` 由 app 判定覆盖，只能在这一行注入）注入 `ask_box_recomputed` / `ask_box_shift_px`；`_redo`（`286-290` 一带）续带这两个新计数（批次 9 的 #11 教训：replan 会换掉整条记录）。
- **不动**：`ask_changed` / `ask_cells` / `ask_delta` 指纹路径（基线仍用冻结 `ask_box`）、`ask_text_changed` 的退化规则、匹配路径、阈值、`press_guard` 分支结构、`gym_app.py`、`score.py`。
- **成本约束**：只跑像素段；若发现必须跑全量 `chrome()` ⇒ 停、写欠账、不硬推。

### 14.5b 改动落地与单点验证（已做，2026-10-05 14:2x）

- **落地**：①新方法 `Driver.ask_box_now`（像素段：`darkfrac>0.55` 找 `top`（找不到 ⇒ `None`）→ `y1` 沿 `>0.30` 增长、上限 `BANNER_BAND` → `nd[y]>6` 的墨迹行 → 列范围 `x∈[14, width-14]` → clamp 进 band + 尺寸门槛 `bw≥20, bh≥6`）；②`ask_label_now` 里 `rec["ask_box"]` 之后插入"重算优先、失敗退回冻结框"，位移首次记 `ask_box_shift_px`；③逐题行 `detail` 注入 `ask_box_recomputed`/`ask_box_shift_px` + `_redo` 续带这两个计数。
- **新 sha**：`gym_run.py` = **`47c1d170f2e543c9`**（旧 `4ae46f4cda176671`）；`gym_app.py 66632d85eac81c12`、`score.py f9cefb9fbcf7d8ce` **未动**；`py_compile` 过；`score.py --selftest` **41 项 0 失败**。
- **单点验证**（探针 `D:\DSH\dsh-actor\tmp\w4_boxprobe_d.py`，只读两张真帧）：`_gym_shot.png` → `ask_box_now = (18,20,425,19)` **与 `chrome()` OCR 框逐字节相同**；`probe-w6-twin.png` → `(18,20,459,19)` vs OCR `(18,20,458,19)`（**差 1 px**）；成本 **p50 4.1 / 3.8 ms**（§13.2 的 3.6 ms 复核成立）。合成右移 40 px 帧：返回 `(14,0,469,56)`/`(14,0,503,56)` —— **clamp 生效**（不越 band、不出图），退化为整带框但仍在 band 内（真帧上不出现，与 §13.4 风险 ① 一致）。
- **干跑**（`--tasks 2`，Windows 侧 + `-WindowStyle Normal` + `--keys --bg`）：**2/2 OK**、`keys 3`（**首题有真按压**）、`foreground unchanged: True`；干跑 json = `t_trap2-w9-dry2.json`（正式批会覆盖同名 state/events，已预期）。

### 14.6 跑批（键通道 + `move@0.70`，协议照批次 8，与它直接对比）
- 命令：`cd /mnt/d/DSH/vision-work/sol/sandbox` → `D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out t_trap2-w9-move70.json` → `score.py t_trap2-w9-move70.json` → `score.py --selftest`。（`/mnt/d/` = WSL 侧看到的 `D:\`，是当时从 WSL bash 起跑的真实记录 —— **合法路径、不是漏**；阶段 3.2 的路径改写有意只动相对路径、不动绝对路径。）
- 从 **Windows 侧**启动 + 显式 `-WindowStyle Normal`；先干跑 `--tasks 2` 确认首题有真按压；新文件名不覆盖批次 7/8；跑完**立刻**打分（events 会被覆盖）。
- 可选对照：时间够再跑 `move@0.35` 看剂量-反应。

### 14.7 结果与判据核对（2026-10-05 14:36 跑完**立刻**打分；**四条全过**）

- **终版**：`sandbox\t_trap2-w9-move70.json`，sha **`5dedae26c6e8`**；`gym_run.py` = **`47c1d170f2e543c9`**（改前 `4ae46f4cda176671`；`gym_app.py 66632d85eac81c12` / `score.py f9cefb9fbcf7d8ce` 未动）。
- **正式行**：`chaos:move v2 59/60 98.3% decided 100.0% disturb 0 screen 57/60 replan 37 1901 ms/task keys 67 shots 479 ocr 649`；`answered_right 45 / wrong_target 1 / refused_right 14`；`false_refusal 0/46`、`false_accept 0/14`、`stale 0 wasted 0 verify_giveup 0 re-reads 0`；变体全过（`alpha020/030/035/050/065 各 2/2`、`prose_only 4/4`、`prose_with_button 6/6`、`swap_after_press 10/10`、`swap_timer 5/5`）；`race 0/0`；`guard gate sample 52 P50 139 ms P95 183 ms`；唯一 wrong = `#34 TUNDRA86`（点成 `TUNDRA`）。`score.py --selftest` = **41 checks, 0 failed**。
- **对照批次 8（同协议、同 seed、app 侧注入逐项相同 `chaos_planned 49 / chaos 49 / ready 61 / done 60 / trap_swap 15`）**：`58/60 96.7% decided 98.3% replan 35 1708 ms/题`、`ask_read_unreadable 2`（全在 `task_i 31`）。
- **i（守门不再依赖冻结框）✅**：`ask_read_unreadable` **2 → 0**；`ask_box_recomputed 124 == ask_gates 124`（每一门都重算）、`ask_guard_runs 52`。⚠ 基线只有 **2** 次事件 ⇒ **样本量不足以单独证明因果**，旁证见下面「机制旁证」。
- **ii（不出现 `result none` + `presses 0` + `replans ≥ 1`）✅**：`result none` 行 = **0**；该合取只有 `task_i 37` 半成立（`presses 0`、有 `replans`）但 **`result = ok`**（`replan_why = "no verdict arrived"`；批次 8 同一题也是 `presses 0` + ok）⇒ 合取不成立。
- **iii（同 `task_i` 无 ok→非 ok 翻转）✅**：共同 60 题 **ok→非 ok = 0**；非 ok→ok = 1（`task_i 15`，两批记录的题面不同 = `swap_after_press` 的读出时机差异 ⇒ **不计为改善**）；总数 `58/2/0 → 59/1/0`。⚠ `t_trap2` 线**没有"核心 14"这个子集**（那词是 `t_trap4/t_trap5` 线的）⇒ 本条用"批次 8 ∩ 批次 10 同 `task_i` 逐题对照"代替（同 seed `20251007` ⇒ 题表相同）。
- **iv（成本）✅**：`gate_ms` P50 **139 / P95 183 ms**（n=52），批次 9 = 124 ⇒ **+15 ms ≤ 30**；**场景匹配**的独立口径 `ms_askgate / ask_gates`：批次 8 **136.30** → 批次 10 **145.01**（**+8.71 ms/门**，与 §13.2 量到的像素段 3.6–4.1 ms 同量级）。行内 `gate_ms` 样本合计 **52 == `stats.gate_samples` 52**（不丢数）。
- **观测点全表（批次 8 → 批次 10）**：`ask_read_unreadable 2 → 0`；`ask_box_recomputed — → 124`；`none 行 0 = 0`；`replans 35 → 37`；`banner_missing 6 → 0`；`asks_from_screen 87 → 91`；`asks_from_file 8 → 6`；`keys 64 → 67`；`nope_hint 13 → 15`；`hint_stale 20 = 20`；`refusals 15 = 15`；`interferences 0 = 0`；`shots 469 → 479`；`ocr 633 → 649`；`ms_askgate 16083.2 → 17981.5`。
- **机制旁证（`task_i 31` = `LUMEN93`，三代对照）**：批次 7 `none`×3（`ask_reread "DO: click the button labelled"`、`ask_cells 0`、`presses 0`）→ 批次 8 `ok` 但 `ask_read_unreadable 2` → 批次 10 **`ok`、`ask_read_unreadable 0`、`ask_box_recomputed 2`、`gate_ms [179.4]`**。
- **⚠ 仪器局限（不得越读）**：`ask_box_shift_px` 只记每题"**首次**"重算的位移（46 行有值、**全部 `[0,0]`**）⇒ 只能证明"进题后首次重算与冻结框一致"，**证明不了门时那一帧确实被移过**；要拿后者得改成记 max / 分布（已入欠账）。
- **环境异常（必须随数字引用）**：`foreground unchanged: False`（before = 用户前台窗口 `hwnd 133568`；after = 另一个应用的窗口 `hwnd 396004`）—— `--bg` 模式不依赖前台（`clicks 0`、`keys 67` 全走 actor 键通道、59/60 完成）。
- **结论**：欠账 **#4 = §7 #15 还清**（判据原文两条都满足：① 守门不再依赖计划时记录的 `ask_box`；② `ask_read_unreadable` 在 `move` 批次降为 0）。本批属 chaos「探索性·不并入定稿」族（键通道 + `--bg`），可比对象**只有批次 7/8**。

### 14.8 本批的一次作废尝试（方法学；与批次 9 ⑥ 同类但**根因不同**）

- 首跑 14:24:27 起，**14:28:07** 在 app 侧 `task_i 47`（driver 打印到 task 45/46）处死，stderr 原文：
  `shot failed: {"ok": false, "steps": 1, "total_ms": 18.4, "trace": [{"i": 0, "op": "shot", "ms": 18.3, "ok": false, "error": "ValueError: cannot write empty image"}], "run_id": 1478}`
  ⇒ `gym_run.py:508 raise SystemExit`（**设计如此**：空帧 = 会话不可用，宁可退出也不产假分）⇒ **不写 run json**，只留 `-state.json` / `-events.jsonl`（**逐题行全丢**，driver 侧新计数也随 json 一起丢）。
- 死前最后三条 app 事件 = `ready` / `chaos_planned`（`kind move`、`delay_ms 574`）/ `chaos`（`elapsed_ms 593.4`）⇒ **`move` 干扰触发的瞬间 `PrintWindow` 返回了空位图**；app 自报 `layout.origin [312,267]`（**不是批次 9 那种 `-32000` 离屏**）⇒ 与"窗口离屏"无关。
- 残留两个 app 进程（`24408` venv shim + `34776` 运行时）**活着但没有窗口**（UIA 顶层窗口表里 `GUI Gym` = 0）⇒ `Stop-Process -Force` 清掉后重跑；重跑（14:31:00）跑满 60 题。
- 首跑唯一留下的可比一行：`task_i 31 LUMEN93` = **OK 2260.9 ms**（与重跑一致）；但该批 events 已被重跑覆盖 ⇒ **这一行不可再复核**。
- ⇒ 新欠账 **§7 #17**（`shot` 空帧零容忍）。

## §15 第五段：开 #17（`shot` 空帧零容忍）—— 假设、改动、判据

### 15.0 开工前确认（只读，2026-10-05 14:44）

- 三件套 sha：`gym_app.py 66632d85eac81c12`(81169 B) / `gym_run.py 47c1d170f2e543c9`(198046 B) / `score.py f9cefb9fbcf7d8ce`(38958 B) —— 与第四段收工一致，**未漂移**。
- 残留 gym 进程 **0**：Windows 侧只有 actor `pid 12008` 与 `python -m md_cg.mcp_server` `pid 32248`（都不是靶子）；无后台作业。
- actor ping ✅ `{"ok": true, "pid": 12008, "uptime_s": 3607.4, "geom": [0,0,2560,1600], "dpi": "per-monitor", "py": "3.12.14"}`。

### 15.1 读码结论（改前，`gym_run.py`）

- **空帧的判定标准 = actor 报告的 `ok: false`**（`{"error": "ValueError: cannot write empty image"}`），**不是**像素判据；像素侧的 `has_banner()`（452–461）只判"抓到了但没抓到靶子"（`banner_missing`），是另一条路。
- `Driver._shot`（**466–523**）已经是**带恢复链的重试**：`retries=2`（⇒ 最多 3 次抓帧）；第 1 次失败 → `window mode=restore` + `mode=bottom` + 250 ms（`stats["restores"]`，只做一次）；之后失败 → `self.hwnd=None` + `window_rect()` 重解析 + `time.sleep(0.25)`（`stats["hwnd_relookup"]`）；预算用尽 → **`raise SystemExit("shot failed: …")`（517）**。
- 另有三个 SystemExit 也在跑批路径上：`window_rect` **405**（`window %r not found - is the app running?`）、`_find_hwnd` **450**（`… not found in UIA either`）、`shot_screen` **533**（`region shot failed`，弹窗那条路）。
- 主循环 = `while i < max_tasks:`（**3340** 起）**整段没有 try/except**；`runs.append(rec)` 在 **3452**；摘要打印与 json 写盘（**3527–3566**）都在循环**之后**的直线代码里；收尾 `proc.terminate()`（3567）、返回码 `0 if ok == len(runs) else 1`（3569）。
  ⇒ 循环里任何异常 = 进程死 = **不写 json**（这就是批次 10 首跑丢 46 条逐题行的机制）。
- **读码后的修正（重要）**：批次 10 首跑**不是"第一次空帧就退"**，而是恢复链三次都拿到空帧后才退；当时 app 进程活着但 **UIA 顶层窗口表里 gym 窗口 = 0**（§14.8）⇒ 那是"**窗口没了**"这一类，恢复链对它**天然无效**。所以"空帧=暂时性"要拆成两类（见 15.2）。
- **改动规模**：比预想小（不动判定路径，只动抓帧失败的处理 + main 的异常出口）。

### 15.2 假设

**假设**：空帧分两类 —— **(a) 瞬时**（窗口被遮挡/最小化/抓帧偶发失败）：现有恢复链能救，但耐心不足（无间隔等待、只 3 次）；**(b) 永久**（窗口/进程消失，`shot hwnd=` 永远返回空）：重试无用，**唯一出路是把已完成的题保存下来**。改成"**重试 + 部分保存**"后，两类空帧都不再导致整批丢失（批次 10 首跑白跑 4 分钟、丢 46 行同类）。

**证伪条件（用户口径 i–iv）**：
- (i) 重试 N 次后仍 100% 空帧（⇒ 判定为永久失效，重试无用）；
- (ii) 部分保存的 run json 与 `score.py` 的 join 不兼容（⇒ 保存格式不对）；
- (iii) 核心 14 出现 ok→wrong 翻转（⇒ 改动有副作用）。⚠ `t_trap5` 线才有"核心 14"（§14.7 已勘误）；本段回归批正是 `t_trap5` ⇒ 本条**能用真口径**核。
- (iv) 正常路径（非空帧）性能下降 > 5%。

**观测点**：`shot_empty`（空帧次数，新增）、`shot_retry`（重试次数，新增）、`restores`/`hwnd_relookup`（已有）、`partial` 标志与 `exit_reason`（新增字段）、部分保存的题数、`score.py` 能否对 partial json 打分、回归批的 48 题成绩与 `ms/题`（对批次 9）。

**判据**：i–iv 全不成立；并**构造一次空帧场景**，实测重试触发 + 部分保存写出 + `score.py` 能打分。构造不出则如实记"只做代码审查、路径未实测"。

### 15.3 改动方案（先读码后定稿）

- **新增** `class ShotFailed(RuntimeError)`：抓帧路径"目标丢了"的统一信号，带 actor 报告文本。
- **改 4 处 raise**：`_shot` 最终失败（517）、`window_rect`（405）、`_find_hwnd`（450）、`shot_screen`（533）⇒ 一律 `raise ShotFailed(...)`（**消息原文不改**，改的只是异常类型）。这样"窗口没了"也不再是 SystemExit。
- **`_shot` 重试加耐心 + 计数**：`retries=3`（⇒ 最多 4 次）；每次失败 `stats["shot_empty"] += 1`；每次重试 `stats["shot_retry"] += 1`；恢复链保持原样（首次 restore+bottom，其后 hwnd 重解析），重试间隔 **0.2 s**。**正常路径零改动**（无失败 ⇒ 不 sleep、不加 op）。
- **main 的异常出口**：把 `while i < max_tasks:` 整段包进 `try`，`except ShotFailed`（+ 兜底 `except Exception`）⇒ 记 `exit_reason`、**打印醒目的 PARTIAL 行**、然后**掉进原有的收尾直线代码**（摘要 + json + `proc.terminate()`）。`runs` 为空时不写 json（保持"启动就失败"的老行为，返回 1）。
- **json 新字段**：`"partial": bool`、`"exit_reason": str|None`、`"tasks_planned": int`（旧批无这三个键 ⇒ 读旧批的脚本不受影响，不静默复用任何旧数字）。
- **返回码**：partial run 返回 **3**（区分于 0 = 全 ok、1 = 有非 ok 题）。
- **明确不动**：`has_banner` 判据、`ask_cells`/`ask_delta` 指纹、匹配路径、阈值、`press_guard` 分支、`_redo`、`score.py` 的**判定算法**（只允许加一行 partial 警示语；`--selftest` 41 项必须仍全过）。

### 15.4 验证计划

1. `py_compile` + `score.py --selftest`；
2. **partial 兼容性**（先于跑批）：把批次 9 的 `t_trap6-1.json` 截成 20 行 + `partial: true` 造一份 `t_trap7-partial-synth.json`，看 `score.py` 是否照常打分、分母是否只算已完成题；
3. **干跑** `--tasks 2`（鼠标通道，确认首题有真按压）；
4. **构造空帧**：跑小批（键通道 `--bg`，6–8 题）中途 `Stop-Process` 掉靶子 ⇒ 期望 `shot_empty`/`shot_retry` 增长、写 partial json、`score.py` 能打分（永久类）；若时间允许再试"最小化"类（瞬时类，恢复链应救回、不写 partial）；
5. **回归批**（鼠标通道，协议照批次 9）：`--scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out t_trap7-1.json` → `score.py t_trap7-1.json` → `score.py --selftest`；对批次 9（36/48、核心 14 无翻转、`ms/题` ±5%）。

### 15.5 跑批命令（与批次 9 同协议；用户原命令里的 `D:\DSH.venvs\...` 缺一个反斜杠，实际用 `D:\DSH\.venvs\vision-ci\Scripts\python.exe`）

- 回归：`D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out t_trap7-1.json`
- 从 **Windows 侧**启动 + 显式 `-WindowStyle Normal`；新文件名不覆盖批次 9 的 `t_trap6-1.json`；跑完**立刻**打分（events 会被覆盖）。

### 15.5b 改动落地与预检（2026-10-05 14:47–14:50）

- **改动落地**（`gym_run.py`，机械缩进 + 定向编辑；`py_compile` 过；缩进前后**剥离空白后逐行相同**——脚本断言 145 行）：
  - 新增 `class ShotFailed(RuntimeError)`（`gym_run.py:321–329`）；
  - 抓帧路径 4 处 `raise SystemExit` → `raise ShotFailed`（`window_rect` 422 / `_find_hwnd` 467 / `_shot` 547 / `shot_screen` 563），**消息原文不变**；
  - `_shot`：`retries=3`（最多 4 次抓帧）、每次空帧 `stats["shot_empty"] += 1`、每次重试 `stats["shot_retry"] += 1`、重试间隔 `time.sleep(0.2)`；恢复链（restore+bottom 一次、其后 hwnd 重解析）**原样未动**；
  - `stats` 初值新增 `shot_empty / shot_retry / restores`（`gym_run.py:368`），零值也进 json；
  - main：`exit_reason = ""` + `try:` 包住整个题目循环（`gym_run.py:3370–3516`）；`except ShotFailed` + 兜底 `except Exception` ⇒ 记原因、打印醒目 PARTIAL 行（失败点 + 摘要各一次）、**掉进原有收尾直线代码**；`runs` 为空则不写 json、返回 1；
  - json 新增 `"partial" / "exit_reason" / "tasks_planned"`；**partial run 返回码 3**；
  - `score.py`：读 json 之后加两行 `!! PARTIAL RUN` 警示（**判定算法零改动**）。
- **新 sha**：`gym_run.py` **`105cf6cb679eea10`**（旧 `47c1d170f2e543c9`）；`score.py` **`ef066713a03eb940`**（旧 `f9cefb9fbcf7d8ce`）；`gym_app.py 66632d85eac81c12` **未动**。运行期 `scripts_sha`（三件套合并）**`8da029edccbc`**（批次 10 = `5dedae26c6e8` ⇒ **裂一次**）。
- **预检**：①`score.py --selftest` = **41 checks, 0 failed**；②**partial 兼容性**（先验）：把批次 9 的 `t_trap6-1.json` 截 20 行 + `partial/exit_reason/tasks_planned` 造 `t_trap7-partial-synth.json` ⇒ `score.py` 照常打分（`v3 18/20`、只 join 20 题）+ 顶部 `!! PARTIAL RUN` 警示 + 退出码 0（**证伪条件 (ii) 不成立**）；③**旧批不回退**：`score.py t_trap2-w9-move70.json` = 批次 10 定稿行逐字相同（`59/60 98.3% … 1901 ms/task`）；④**干跑** `--tasks 2`（鼠标通道 `t_trap5`）：**2/2 OK**、`clicks 4`（真按压）、`foreground unchanged: True`、`partial=False`、退出码 0。

### 15.6 结果与判据核对（2026-10-05 14:47–14:55）

**A. 空帧路径构造（两次，键通道 `--bg` 6 题，`scripts_sha 8da029edccbc`）**

| 构造 | 手法 | 结果 |
|---|---|---|
| 永久类（kill） | 跑测第 14 s `Stop-Process` 掉靶子（2 个 app 进程） | 已完 1 题**保住**：`t_trap7-empty6.json`（4354 B）`partial=true`、`exit_reason="window 'GUI Gym' not found - is the app running?"`、`tasks_planned=6`、`runs=1`；退出码 **3**；`score.py` 读得动（`!! PARTIAL RUN` 两行 + `t_trap2 1/1`） |
| 窗口不可达（minimize） | 跑测第 10 s Win32 `ShowWindow(SW_MINIMIZE)`（`FindWindow('GUI Gym')` 拿不到 hwnd ⇒ 改用 `EnumWindows` 枚举标题） | 复现了 #17 的**同一条 actor 报错**（`ValueError: cannot write empty image`）；重试链按设计跑满：`shot_empty=4`、`shot_retry=2`、`restores=1`、`hwnd_relookup=2`、`shots=6` ⇒ 窗口仍不可达 ⇒ **部分保存**：`t_trap7-minim6.json`（4546 B）`partial=true`、`runs=1`、退出码 **3** |

- **机制旁证（app 侧）**：minimize 之后 app **仍活着**（`t_trap7-minim6-state.json`：`task_i 1`、`result none`、**`layout.origin [-32000,-32000]`**）⇒ **空帧 ≠ app 死了**，是窗口对 actor 的抓帧与 UIA 都不可达。
- **⚠ 与旧代码注释不符（新盲区）**：`_shot` 里"最小化 ⇒ `restore`+`bottom` 能救回"这次**没有复现**——`window mode=restore` 拿旧 hwnd 没把窗口带回来，`_find_hwnd` 的 UIA 列表里 gym 窗口 = 0，我自己的 `EnumWindows` 也扫不到（同一进程的 state 文件却还在写）⇒ 记为新盲区（`HANDOFF.md` 盲区 20）。
- **未能构造出"瞬时"类空帧**：两种可控手法（kill / minimize）都落在"永久 / 不可达"这一类 ⇒ 关于"重试能把**瞬时**空帧救回来"这一半假设，**既未证实也未证伪**；证伪条件 (i)「重试 N 次后仍 100% 空帧」在"窗口不可达"这一类上**成立**（4 次全空）—— 这正是第二层（部分保存）存在的理由。**本段能确证的**：空帧**不再丢批**（第二层 ✅ 实测 + `score.py` 可读 + 退出码 3），重试链按设计运行（计数齐全），但它救不回已经不可达的窗口。

**B. 正常路径回归（`t_trap7-1.json`，48 题 `t_trap5` 鼠标协议，14:51:20–14:54:58，Windows 侧 `-WindowStyle Normal`）**

终版行（`score.py t_trap7-1.json`，跑完**立刻**打；json 132667 B、`sha` **`dd77abc08e911794`**、`scripts_sha 8da029edccbc`）：

```
t_trap5  v3 35/48  72.9%  decided 100.0%  disturb 0   screen 42/48 replan 31   1527 ms/task  keys 6  shots 165  ocr 421
         answered_right=35 wrong_target=7 false_refusal=6
         false_refusal 6/48 (12.5%)  false_accept 0/0  stale 0  wasted 0  verify_giveup 0  re-reads 0
         swapped 38  a_hit 19  a_hit_but_failed 0
         variant nb046 0/3  nb050 0/3  nb065 2/2  nb100 2/2 · swap_after_press 5/5 · swap_hard_press 5/5
                 · swap_hard_timer 5/5 · swap_race_timer 4/10 · swap_timer 4/5 · swap_twin_press 8/8
         race(pressed the replaced ask) 7/7   (after the guard's frame 6)
         guard gate sample 73  P50 127 ms  P95 167 ms  (criterion P50<=240, P95<=320)
```

- **逐项对照批次 9**（`t_trap6-1.json`：`36/48 75.0%`、`screen 43/48 replan 32`、`1513 ms/task`、`shots 167 ocr 426`、`race 6/6`、`gate P50 124 / P95 164`、`gates 74`）：

| 项 | 批次 9 | 批次 11 | 差 |
|---|---|---|---|
| 总数 | 36/48（75.0%） | 35/48（72.9%） | **−1 题** |
| **核心 14** | 12/14 | **12/14** | **ok→wrong 翻转 0** ✅ |
| `ms/题`（score.py 同口径） | 1513 | **1527** | **+0.9%** ✅ |
| 逐行 `wall_ms` mean / p50 | 4552 / 3888 | 4463 / 3890 | −2.0% |
| `shots` / 每帧 | 167 / 227.0 ms | 165 / 218.6 ms | −3.7% |
| `ocr` | 426 | 421 | −1.2% |
| `shot_empty` / `shot_retry` / `restores` | （旧代码无这些键） | **0 / 0 / 0** | 失败分支**未进** ✅ |

- **唯一翻转 = `task_i 38`（`ok → wrong`）**，落在**定时竞态族** `swap_race_timer`（`clicked=GAMMA want=QUARTZ`）；同族两批 `5/10 → 4/10`、`a_hit 2 → 1`、`race 6/6 → 7/7`（"swap 落在守门帧 5 → 6"）。该族**历来逐批漂移**：批次 8→9 就漂过 `#44 wrong→ok`、`#45 ok→wrong`（总数 37/48 → 36/48，`../sol/sandbox/SCORE.md` 批次 9 节）⇒ 记为**该族固有抖动**（有先例，但本段**未做重复批**坐实），且该题**不在核心 14 内** ⇒ 不构成判据 (iii) 的翻转。
- **判据 (iii)**：核心 14 **12/14 → 12/14，翻转 0** ⇒ **不成立**。
- **判据 (iv)**：`ms/题` **+0.9% ≤ 5%**（逐行 `wall_ms` 反而 −2.0%、`shots`/每帧同降）⇒ **不成立**；机制侧更硬：`shot_empty=0`、`shot_retry=0`、`restores=0` ⇒ **失败分支一次也没进**（正常路径与改前逐行同构，`w5_check.py` 断言 145 行）。
- **判据 (i)/(ii)**：见 A 段 —— (ii) 由合成 partial 先验证伪；(i) 在"窗口不可达"这一类上**成立**（4 次抓帧全空），这正是第二层（部分保存）存在的理由。
- **未做**：同协议重复跑 2–3 次来把竞态族抖动坐实（时间不够）⇒ 引用"task 38 = 噪声"前需先补这个重复批；本段只把它记成**未坐实的 −1 题**（不影响判据 iii/iv 的结论）。
- **本段结论**：**#17 = §7 #17 还清**（第二层 ✅ 实测两类空帧都不再丢批 + `score.py` 兼容 + 退出码 3；第一层重试链按设计运行但救不回"窗口不可达"）⇒ 转入 `../sol/sandbox/SCORE.md` 批次 11 节 + `HANDOFF.md` 盲区 18/20。

## §16 第五段：#18「连续 / 视口类交互盲区（滚轮 + 拖拽）」—— 只量不改

### §16.0 开工前确认（只读）
- 三件套 sha（探针全程）：`gym_app.py` **`66632d85eac81c12`** / `gym_run.py` **`105cf6cb679eea10`** / `score.py` **`ef066713a03eb940`** —— 与批次 11 定稿**同一套**；本段**没有**再改任何文件（探针脚本只在 `D:\DSH\dsh-actor\tmp\`）。
- 6 个探针**串行**跑（同一时刻只有 1 个 gym 窗口）；`foreground unchanged: True` × 6；无 gym 残留窗口。

### §16.1 现状（判据第①节，只读）
- **覆盖 = 0**：`TRAP_PLAN`/`PLAN2`–`PLAN5` 的 screen 集合里**没有** `t_rows`/`t_chips`；所有 `t_trap*` 记录 `stats.scrolls = 0`、`stats.drags = 0`。
- **两条路径都只在鼠标分支**：`Driver.wheel()`（`gym_run.py:1199–1210`）唯一调用点 **`gym_run.py:2314`**（rows 处理器鼠标分支）；`Driver.drag()`（`gym_run.py:1193–1197`）唯一调用点 **`gym_run.py:2862`**（chips 处理器鼠标分支）。键通道走 `Home`/`Next`/`Down`（`gym_run.py:2228–2316`）与 chip/slot 键（`gym_run.py:~2830` `self.key(hd)`），**完全不经过这两个函数**。
- **靶子场景**：`t_rows()` = `gym_app.py:673–738`（14–34 行、行高 34/40/46、canvas 视口 621 px、末尾 52 px spacer、`<MouseWheel>` 绑定在 **725**、`Next`/`Prior`/`Up`/`Down`/`Home` 在 728–735）；`t_chips()` = `gym_app.py:850–965`（chip→slot；鼠标 = `tag_bind("chip","<ButtonPress-1>")` + `<B1-Motion>` + release 里命中槽判定；键 = `pick`/`drop_slot`）。真值坐标可从 app 状态文件读到（`truth.chips` 给 chip 中心、`truth.slots` 给槽位矩形，`layout.origin/size` = 窗口 `(316,313) / 1180×780`）。

### §16.2 探针与产物（日志与 json 全在 `D:\DSH\dsh-actor\tmp\`，队列日志 `w18_queue.log`）
| 探针 | 命令（`--max-repeat 3` 统一） | 结果 |
|---|---|---|
| P1b | `t_rows --tasks 8 --keys --bg` | **8/8 OK**、`keys 17`、`shots 17`、`ocr 58`、`clicks 0`、`drags 0`、`stats.scrolls 0`；逐题 `rec["scrolls"]`：只有 `task_i 2` = 1，其余 0 |
| P1c | `t_rows --tasks 24 --keys --bg` | **22/24**、`keys 53`、`shots 53`、`ocr 178`、每题 3.3 s avg；需翻页的 5 题（`task_i 2/12/14/16/19`，`scrolls = 1`）**全 OK** |
| P3 | `t_chips --tasks 8 --keys --bg` | **8/8 OK**、`keys 18`、`shots 26`、`ocr 74`、`drags 0`；逐题 `detail` 一次到位（`chip`/`slot`/`want_*` 全等） |
| P2 | `t_rows --tasks 16`（鼠标 + bg） | **0/3 早停**、`clicks 3`、`shots 3`、`result NONE`、`detail {}`、每题 ~5.7 s |
| P4 | `t_chips --tasks 8`（鼠标 + bg） | **0/3 早停**、**`drags 3`**、`clicks 0`、`result NONE`、`detail {}`、每题 ~6.4 s |
| P5 | `t_chips --tasks 8`（鼠标 + bg + `move@0.70`） | **0/3 早停**、**`drags 9`**、`shots 63`、每题 ~23.3 s（`NONE` + 等判定）、三次同一题 |

- **`--max-repeat` 语义（本段发现，`gym_run.py:3503–3510`）**：`stuck` 数的是"**连续几行的 `task_i` 没前进**"，`stuck >= a.max_repeat` 就早停并打印 `stopping early: task %s failed %d times in a row` ⇒ **`--max-repeat 1` 会在第一题就停**，提示语有误导性（实测该题其实 `result=ok`）。探针因此统一用 `--max-repeat 3`。

### §16.3 决定性观察：`--bg` 下**鼠标通道整条不生效**
- **实测**：P2/P4/P5 三次都是 app 侧 `task_i` **停在 0**（`stopping early: task 0 failed 3 times in a row`），驱动却确实发出了动作（`clicks 3` / `drags 3` / `drags 9`，`rec["src"]/["dst"]` 有坐标、都在窗口内）⇒ **动作发出去了，靶子一次都没认**。同场景键通道：8/8、22/24、8/8。
- **机制（代码锚点；属推断，未做隔离实验）**：`actor.py` 的 bg 分支走 PostMessage 家族 —— `o_click` **1266–1270** ⇒ `post_click`（**1088–1097**，docstring "no cursor move, no activation"）、`o_drag` **1311–1314** ⇒ `post_drag`（**1104–1116**）、`o_scroll` **1357–1359** ⇒ `post_scroll`（**1188–1200**）；而 `o_key` **1340–1346** 在 bg 下**显式做 focus 交接**，同文件注释 **1342–1344** 写明"post 进 IPC 间隙的键会被 **Tk 静默丢掉**"。鼠标三个 op **没有**这一步。
- **含义**：滚轮与拖拽都只在鼠标分支 ⇒ **在"不抢前台"的约束下量不到**（鼠标分支要有效必须走物理输入 `SendInput`，那要么去掉 `--bg` 由驱动把窗口提到前台，要么给 actor 的鼠标 op 加 focus/物理通道 —— 后者是**改代码**）。

### §16.4 八问逐条判定（"能/不能 + 最小证据"）
| # | 问题 | 判定 | 最小证据 |
|---|---|---|---|
| 滚1 | 会不会滚 | **量不到（有据）** | 唯一调用点在鼠标分支（`gym_run.py:2314`）+ bg 鼠标通道不生效（§16.3）；6 跑里 `stats.scrolls` 全 0（鼠标跑的第一题目标就在可视区，没走到 `wheel()`）|
| 滚2 | 方向对不对 | **代码一致，未实测** | `wheel(-3)` ⇒ `dy = -360`（`gym_run.py:1199–1210`，一格 = 120）⇒ actor `scroll` ⇒ `MOUSEEVENTF_WHEEL`；靶子 `<MouseWheel>` = `yview_scroll(int(-e.delta/60),"units")`（`gym_app.py:714`）⇒ 负 delta = 视口下移 = 驱动想去的方向 ✓（只读推导）|
| 滚3 | 幅度对不对 | **未实测** | 代码每次 3 格；靶子把 delta 折成 `units`（一次 ≈ 6 行），而视口 621 px / 行高 34–46 ⇒ 一屏 13–18 行；处理器循环上限 7 次，够不够**没有数据** |
| 滚4 | 滚完重新定位 | **能（实测，键通道）** | 处理器每轮重抓帧（`img2 = self.shot()` + 新帧 `body_words` 重找行）；P1c 需翻页的 5 题**全 OK**（`task_i 2` 目标行 y=658 在首帧视口外），每题只多 ~1.0–1.2 s（4.1 s vs 3.0 s）⇒ **用新帧重找**，不是进题冻结坐标 |
| 拖1 | 会不会拖 | **量不到（有据）** | bg 鼠标跑真的发了 `drag`（P4 `drags 3`、P5 `drags 9`）而 app `detail {}`、`task_i` 不动（§16.3）|
| 拖2 | 起点抓准不准 | **量不到** | 判据只能是 app 侧认不认；驱动侧只有它自己算的坐标（P4 `src [1102,748]`、P5 `src [1001,808]`，都在窗口内），无真值对照 |
| 拖3 | 落点精度 | **量不到** | 同上（P4 `dst [1140,491]`、P5 `dst [1039,551]`）；代码语义 = 槽位框中心 x、**框底 + 26 px**（注释 "inside the frame"，`gym_run.py:2862`）；`t_chips` **从未在任何批次跑过** ⇒ 无历史旁证 |
| 拖4 | 中途 `move` 干扰能否适应 | **量不到** | P5 只证明 chaos 在发（`move@0.70`、`drags 9`、每题 23.3 s）；"干扰下能否适应"需要一次真落地的拖拽 |

- **旁证（顺带量到的、值得记的）**：P1c 的 2 道失败（`task_i 11` want 3767 / `task_i 15` want 3935）**都在视口最底一行** —— `target_box` y=716（视口底 ≈ 727），选中了错的 id（5004 / 5267）⇒ 行场景的弱点是**底边行的 OCR/匹配**，不是滚动本身。

### §16.5 结论与状态
- 八问：**1 条能**（滚4 = 用新帧重找，键通道实测）、**1 条代码级一致但未实测**（滚2）、**6 条量不到**（滚1/滚3 + 拖 1–4）。
- "量不到"的原因是新发现的**能力缺口**：`--bg` 下鼠标通道（click/drag/scroll）POST 出去、Tk 端不生效（§16.3）；滚轮与拖拽都只挂在鼠标分支 ⇒ 在"不抢前台"约束下不可测。
- **钥匙通道侧两种题型都能跑**（rows 8/8 + 22/24、chips 8/8）⇒ `t_trap` 家族补这两种场景**不必**先修鼠标通道（**滚轮除外** —— 滚轮没有键通道等价物，只能靠前台鼠标批）。
- ⇒ `STATE.md` §7 **#18 状态维持「欠（有据）」**：题面覆盖仍是 **0**（判据未达），并新增一条证据/子问题（bg 鼠标通道缺口）。**本段没改任何代码、没裂 sha、没把探针产物并入任何成绩。**
- **留给下一批的两次实验**（写明备查，本段不做）：①**前台鼠标批**（去掉 `--bg`）跑 `t_rows`/`t_chips` 各 8 题 ⇒ 滚1/滚3 + 拖2/拖3 四问直接可判（代价：占用前台，与"不抢前台"冲突，需用户放行）；②若必须 `--bg`：给 actor 的鼠标 op 加 focus 交接或走物理通道（**改代码**，超出"只量"）。


## 17. 欠账 #12（`guard-blind` 分母）——第六段：先读码，再小量

### §17.0 开工前确认（只读）
- 三件套 sha：`gym_app.py 66632d85eac81c12` / `gym_run.py 105cf6cb679eea10` / `score.py ef066713a03eb940`（与批次 11 收工逐字节相同）。
- 无后台任务；无 gym 窗口；actor `:8731` **pid 12008、uptime 5166 s**；开工前前台 = 用户前台窗口 `hwnd 132886`。
- 从 Windows 侧启动、显式 `-WindowStyle Normal`、带 `--bg`（不抢前台）。

### §17.1 读码结论（三问，不写代码）
**① `blind_seen` 的计数逻辑与打印条件（全在 `score.py`）**
- `stale = [r for r in declared if r.get("stale_press")]`（`score.py:324`）；`stale_press` / `stale_variant` 来自 **events 文件**里 app 发的 `trap_stale_press` 事件（`score.py:148–156`）。
- `blind = [r for r in stale if r.get("stale_variant") == "swap_hard_timer"]`（**332**）；`blind_wrong_target = len(...)`、`blind_seen = len(blind)`（**373**）。
- 打印：`if k["blind_seen"]:`（**425**）⇒ **只有非 0 才打印** `guard-blind(one-glyph re-roll) %d/%d`（**428**）；0 时整行不出现 ⇒ 读者既看不到家族跑了几题（分母），也分不清"家族没跑"与"跑了但没漏判" —— 这就是 #12 说的"没有分母"。
- 计数来源是 **app 自己的记账**（不是驱动自报）：`gym_app.py:1349–1368`，phase b 按到 `want_a` 且 `variant in ("swap_timer","swap_hard_timer","swap_race_timer")` 时 `emit("trap_stale_press", variant=…)`。

**② 指纹漏判 + 文本说"变了"这两个条件现在还能同时成立吗**
- `swap_hard_*` 的设计就是 B 与 A 只差一个字形（`gym_app.py:1305–1320`："band-signature guard cannot see the change at all"）。
- 但**批次 4 起**驱动加了文本重读：`ask_label_now`（`gym_run.py:1413–1488`）读 banner 上的 label 词，`ask_text_changed`（**1490–1522**）用 `_plain`（**不折叠**）逐字比较。docstring（1493–1501）记着批次 3 的实测：折叠版放过 `TANGO→TANGQ`（2/3 仍 guard-blind），raw 版抓到 `HARBOR→HARBOP` ⇒ **批次 3 的 `blind_seen=1` 是"折叠比较"时代的产物，不是现在的性质**。
- 键通道**也走守门**：`press_hint` 在 `self.key(hint)` 之前调 `press_guard`（**1767**；鼠标分支在 2123 / 2156 / 2220）⇒ 键通道的测量与鼠标通道同义，`--keys --bg` 可用。
- app 侧按键与点击同源：`pick(L)`（`gym_app.py:1093`）绑在按钮 badge 键上 ⇒ 两条通道进同一段 stale 判定。
- **残余窗口（唯一可能出分母的路）**：`ask_label_now` 返回 `None`（`ask_box`/`ask_word` 缺失，或 banner 读不出 `labelled X` 形）⇒ `ask_text_changed` 直接 False，判定退回**指纹**（`ask_moved_now` / `ask_cells` / `ask_delta`）⇒ 单字形换题在这条路上仍可能被漏判。

**③ 现有题型能不能产生 `blind_seen`**
- **能跑**：`plans.v1.json` 的 `trap5`（`t_trap5`；阶段 3.6 前 = `gym_app.py:162`）含 `("swap_mid_task","swap_hard_timer") * 5`（`gym_app.py:139`、`plans.v1.json` 的 `trap5`）；`--seed 20251007 --tasks 20` 时该家族落在 `task_i 13–17`（plan 顺序：twin 8 → hard_press 5 → hard_timer 5）。
- 批次 5/6 的 `blind_seen == 0` **不是"没题"**，而是文本重读抓住了（批次 4 起有文本重读，批次 5 又加 pad 6 px 治截断）。
- **方法学注意**：`blind_seen` 只来自 **events 文件**，而 events 每次 app 启动被覆盖 ⇒ 这个数字**跑完必须立刻打分**；历史批（5/6）的 events 已不存在，**不能事后补出分母**。

### §17.2 一句结论
**覆盖路径成立（raw 比较 + 键通道同走守门），但留了"读不出 label ⇒ 退回指纹"的窗口 ⇒ 不能凭读码宣布结构性为 0，按最坏假设先跑小量。**

### §17.3 假设与判据（按"#12 有据"版写）
- **假设**：只有 `ask_label_now` 返回 `None` 的题才可能漏判；若出现 `blind_seen`，它必须落在"该题 `ask_read_unreadable > 0`，或该题 `ask_gates == 0`"上。
- **证伪条件**：小批跑完 `blind_seen == 0`，`swap_hard_timer` 5 题在屏幕上确实换过题（events 有对应 `trap_swap`）、`ask_gates` 正常 ⇒ 文本重读已覆盖 ⇒ #12 关闭（情况 B）。
- **观测点**：`blind_seen`；`ask_gates` / `ask_read_unreadable`；`swap_hard_timer` 5 题的逐题 `result` / `replans` / `stale_actions` / `ask_gates`；events 里 `trap_swap` 与 `trap_stale_press` 的条数与 variant。
- **判据**：`blind_seen ≥ 1` 且能指出是哪几题 ⇒ **情况 A**（只改 `score.py` 的打印条件，裂一次 sha，收口）；否则 ⇒ **情况 B**（不改代码，关闭 #12，标"已量·文本重读已覆盖"）。

### §17.4 小量跑批（3.1）
```
cd D:\DSH\vision-work\sol\sandbox
D:\DSH\.venvs\vision-ci\Scripts\python.exe gym_run.py --scenario t_trap5 --tasks 20 --seed 20251007 --keys --bg --max-repeat 3 --json-out D:\DSH\dsh-actor\tmp\w12-trap5-keys20.json
```
（从 Windows 侧 `Start-Process -WindowStyle Normal` 启动；跑完**立刻** `score.py` 该 json + `--selftest`；events 留档副本入 `dsh-actor\tmp\`；不覆盖任何批次文件。）

### §17.5 结果与判定（2026-10-05 15:11–15:13 实测）
**跑批**：`t_trap5 --tasks 20 --seed 20251007 --keys --bg --max-repeat 3`，从 Windows 侧 `Start-Process -WindowStyle Normal` 启动（pid 15568，15:11:23 → 15:13:22，119 s；退出码 **1** 是因为 17/20 有 3 题非 ok，属这个驱动的正常返回码），产物 `D:\DSH\dsh-actor\tmp\w12-trap5-keys20.json`；events（111 行 JSONL）已留档 `D:\DSH\dsh-actor\tmp\w12-events-archive.json`；**score.py 跑完立刻打**（events 每次 app 启动被覆盖）。
**score.py 行**：`t_trap5 v3 17/20 85.0% decided 100.0% disturb 0 screen 17/20 replan 18 1572 ms/task keys 33 shots 111 ocr 202`；变体 `nb046 0/2 · swap_hard_press 5/5 · swap_hard_timer 5/5 · swap_twin_press 7/8`；`race(pressed the replaced ask) 0/0`；`stale 0`；gate sample 31，P50 127 / P95 141 ms；`score.py --selftest` = 41 checks 0 failed；前台 `unchanged: True`。
**判据（§17.3）逐条**：
- `blind_seen` = **0** —— score 行里**没有** `guard-blind(one-glyph re-roll)` 那一行（打印条件 `if k["blind_seen"]` 为假）。
- **两条独立口径一致**：events 里 `trap_stale_press` = **0 条**（111 行全量扫过）；`ask_gates = 67`、`ask_read_unreadable` **缺键（= 0）**、`ask_box_recomputed = 67`（每道门都重算框，批次 10 的改动在键通道同样生效）。
- `swap_hard_timer` 5 题（`task_i 13–17`）**确实换过题**：events 有 `trap_swap {a: GAMMA, b: GAMMB, why: timer, hard: True}` 这一类记录；5 题全 `ok`，每题 `replans=1`、`ask_moved=1`、`presses=1`、`stale_actions=0`。
- **最小证据（指纹静默、守门仍起效）**：`task_i 13`（GAMMA→GAMMB）逐题行 `ask_cells = 0`、`ask_delta = 0.3` —— **32×4 指纹一格没动** —— 而 `ask_moved = 1`、`replans = 1`、`ask_word = GAMMB`、`result = ok` ⇒ 抓住这次单字形换题的**不是指纹，是文本重读**（`ask_text_changed` 的 raw `_plain` 比较）。t14–17 的指纹也动了 1 格（`ask_cells 1.0`），所以它们不能单独指认是哪条路；13 这一题正是这个欠账要找的那一类。
⇒ **判定 = 情况 B**：**#12 关闭**（`blind_seen` 结构性为 0）。本段**没有改任何代码、没有裂 sha、没有把这次探针并入任何成绩**（`../sol/sandbox/SCORE.md` 不动）。
**已知局限（不许读成"已证"）**：①本次量在**键通道**（`--keys --bg`）完成；鼠标通道共用同一个 `press_guard`（`gym_run.py:2123` / `2156` / `2220`），但受 §16.3 的 `--bg` 鼠标缺口限制**没有复测**；②样本 = 1 批 20 题（家族 5 题），不是多批重复；③要让分母**打印**出来仍得改 `score.py`，按判据（`blind_seen ≥ 1` 才改）**不做**。
**旁证（顺带量到的）**：`swap_twin_press` 7/8（唯一失败 `task_i 0`：`no_press`，9.0 s 一个东西都没按 ⇒ 与批次 11 的 twin 抖动同族）；`nb046` 0/2（全拒答，与批次 9/10/11 的 `nb046 0/3` 同构）；`ask_source` 屏幕 32 / 文件 6。


## 18. 第十段（2026-10-05）：#16 `popup` 打不掉 —— 根因是 **actor 折叠截断**，改 4 处、批次 12 定稿

### 18.0 一句话
弹窗**一直看得见**，是驱动**读错了字段**：actor 把 `data` 里的 list 折叠截断（`actor.py:_slim()`，只留前 ~6 项），而 `window_by_title()` 只读 `data.windows` ⇒ "attention" 只要排在截断之后，`window_by_title("attention")` 恒 `None` ⇒ 键通道 bg 分支第一行 `break` ⇒ **一次 Return 都没发**（批次 8 两批 `interferences 0`、各 1 次 fire 后早停）。

### 18.1 定位过程（不猜阈值，直接探针）
- **协议坑（教训）**：actor `:8731` 是**裸 TCP + 换行 JSON**（`loop.py:Actor.call` 发 `{"op":"run","steps":[…]}`），**不是 HTTP**（用 `urllib` 会得到 `BadStatusLine`）；**从 WSL 到不了 Windows loopback** ⇒ 探针必须 `pwsh` + Windows venv python。
- 探针 1：app 以 `--chaos 1.0 --chaos-kind popup --no-topmost` 起，`{"op":"uia","what":"windows","max":120}` 的 trace 里**有** `{"name":"attention","cls":"TkTopLevel","type":"Window"}`（同列表 11 项）；app 事件确认 `chaos kind=popup` 真的 fire。
- 探针 2（决定性；脚本 `D:\DSH\dsh-actor\tmp\w10-uia-probe3.py`，用 actor 自己的 `loop.Actor` 复刻驱动读法）：**同一条 trace 条目**里 inline `windows` **11** 项、`data.windows` **7** 项 ⇒ 截断坐实（`results=False` 时 `data` 干脆为空）。
- 批次 8 原始产物复核（旧驱动 `f598406cfc70`）：`w8-popup35.json` 只 7 行 / `max task_i 4` = 4 ok + 3 none；`w8-popup70.json` 只 4 行 / `max task_i 1` = 1 ok + 3 none；两批 `interferences 0`、`clicks 0 / drags 0`、无 `popup_*` 键；而 app 事件显示驱动发的键**到了 app**（`hit:true, modal:true`）却没计分（`gym_app.py:454-481 finish()` 的 modal 门）。

### 18.2 改了哪 4 处（`../sol/sandbox/gym_run.py`；+24 / −4 行，其中约 8 行是注释/docstring；**判定路径一字未动**）
1. `Driver.window_by_title()`（约 `:849`）：**inline 优先** —— `wins = step.get("windows") or (step.get("data") or {}).get("windows") or []`，docstring 写明 `_slim` 截断根因与批次 8 症状。
2. `target_windows()`（约 `:3111`）：同一改法（同一缺陷类；它是"挂窗口"用的）。
3. `dismiss_interference()` 键分支（约 `:922-935`）：越过闸门时 `popup_seen += 1`；发完 Return 后再查一次 `attention` ⇒ `popup_dismissed += 1` 或 `popup_dismiss_failed += 1`（`interferences` 语义未动）。
4. 等判定循环（约 `:3461-3466`）：清干扰返回 `n>0` ⇒ **立刻 `break`**（弹窗已清，但被它吞掉的按压不会补分 ⇒ 马上走 `_redo(..., "no verdict arrived")` 重答，省掉剩余最多 4.4 s 空等）。
- 未采用"盲按 Return"方案：闸门本身可修；盲按有 60 题 × 3 键噪声与表单题 Entry `<Return>` 误提交风险（`gym_app.py:757`）。
- 备份：`D:\DSH\dsh-actor\tmp\gym_run.py.bak-w10`（sha `105cf6cb679eea10`，与改前一致）。

### 18.3 批次 12 结果（判据逐条）
`../sol/sandbox/t_trap2-w12-popup35.json`，`scripts_sha 186edbd9c024`，协议与批次 8 `popup35` **逐项相同**（`--keys --bg` / t_trap2 / seed 20251007 / `chaos 0.35` / `chaos-ms 200,700` / kind popup / `--no-topmost` / 60 题 / **未传 `--until-interferences`**）。

| 判据 | 阈值 | 实测 | 结论 |
|---|---|---|---|
| 能 fire ≥ 5 次 | ≥5 | app 侧 `chaos 25`（24 个 task 被清障） | ✅ |
| 不早停 | 60 题跑满 | 逐题行 60、`max task_i 59`、`done 60`、退出码 0 | ✅ |
| 有 dismiss 记录 | ≥1 | `popup_seen 24` / `popup_dismissed 24` / `popup_dismiss_failed 0` | ✅ |

- 成绩行：`v2 60/60 100.0%`、`disturb 15`、`screen 50/60`、`replan 29`、`1714 ms/task`、`false_refusal 0/46`、`false_accept 0/14`、`fired-task pass 15/15`、`quiet 45/45`、`gate_ms` P50 127 / P95 138 ms。定稿行在 `../sol/sandbox/SCORE.md` 批次 12 节 ②。
- **计数闭合（可复算）**：驱动 `interferences 24` = 逐题行合计 **15** + `interferences_at_start` 合计 **9**（9 行，题首清障，`gym_run.py:2033-2034`），涉及 **24 个不同 task**；`score.py` 的 `disturb 15` 只数"题内"那 15 次 ⇒ 两个计数**不可互推**。
- **恢复代价**：`replan_why = "no verdict arrived"` **12 行全 ok**；逐题 ms **1748.6**（n=12）vs 未被吞的 **1639.5**（n=34）⇒ **+6.7%**。驱动墙钟 3627 ms/题（222.7 s / 60 题）与 `ms/题 1714` 不是同一个量 ⇒ 未细分、不并入性能结论。
- **app 侧 fire 25 vs 驱动清障 24 差 1 次**：两种候选解释（落在最后一题之后 / 被下一次换题的 `_close_modal()` 顺手关掉，`gym_app.py:501`）都成立、**未取证** ⇒ 只并列、不裁定。

### 18.4 引用时必带的边界
1. 与批次 8 是**历史产物对照**（驱动版本不同、无同批 A/B）⇒ 只能说"**这一类现在可测了**"，不能说"通过率被提升"。
2. 旧的 `interferences 0` **不可**读成"没被干扰"；批次 7/8 的 `popup` 两档成绩仍**不可引用**。
3. 本批仍标「**探索性·不并入定稿**」（键通道 + `--bg`，与鼠标批不同通道不同协议）。
4. 未做：同协议重复批、`0.70` 档复跑、鼠标通道批、A/B 对照批（`gym_run.py.bak-w10`）。
5. **报告 v0.3 待同步项**：`REPORT.md` 第 6 章"能力缺口"族里关于 `popup` 类"测不了"的表述（`REPORT.md:237`）及其附录 A 的索引行（`REPORT.md:347`，指向 `../sol/sandbox/SCORE.md:804–814` + `STATE.md:809–858`）已被本段推翻（本段按规格**未改报告**）。

### 18.5 可复用的教训（跨项目）
- **读 actor 回包要读 inline 字段**：`results=True` 时 `data` 会被 `_slim` 折叠（list 只留前 ~6 项、str 截 400 字符）；`step["windows"]` 这类 inline 才是全量。判"某个东西不存在"之前，先确认不是被折叠掉了。
- **"看不见"与"看得见但拿不到"要分开证**：本欠账拖了三段，起因是把"枚举结果里没有"当成"枚举不到"（其实是读错了字段）；直接探针（同一请求，两种读法对照）一次就定了性。
- **actor 是裸 TCP+JSON，不是 HTTP**；`WSL → Windows loopback` 不通 ⇒ 探针走 `pwsh` + Windows venv python。

---

## 19. 第十一段（2026-10-05）：报告 v0.3 + 欠账 #19 的覆盖面补测

### 19.0 一句话

报告里那条**唯一被自己推翻的事实错误**（"`popup` 类不可测"）已经改正；改正后的覆盖面**补测过了**：**键通道两个强度档都成立，鼠标通道仍然打不掉** —— 后者记为**新欠账 #20**。本段**没改一行被测代码**（三件套 sha 与第十段收工完全一致）。

### 19.1 两批（都立刻打分，产物都已入库）

| 批 | 通道 | 命令要点 | 结果 |
|---|---|---|---|
| 批次 13 A | 键通道 `--keys --bg` | `gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind popup --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out t_trap2-w13-popup70.json` | **成功**：60/60、`popup_seen/dismissed/failed 45/45/0`、`interferences 45`（题内 27 + 题首 18）、**无早停**、墙钟 250.9 s、`scripts_sha 186edbd9c024` |
| 批次 13 B | 鼠标前台 | `--scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --chaos 0.35 --chaos-kind popup --chaos-ms 200,700 --json-out t_trap5-w13-popup35.json` | **失败**：**3 题后早停、退出码 1**；驱动 `disturbances: 0 fired`；app 侧 `event blocked by modal` + `blocked 10`；墙钟 79.1 s |

口径同批次 12：`--chaos` 只在 `--bg` 下改驱动策略（改成"轮询 + 复核"）；`--until-interferences` 是**停止条件**，在 `--tasks 60 --max-tasks 60` 下**不会**提前停。启动一律从 Windows 侧 `Start-Process -WindowStyle Normal`，跑前跑后各看一次锁屏（`wait_until_unlocked()` 内置）与残留进程。

### 19.2 判据（每档 ≥5 fire）

| 判据 | A（0.70 键通道） | B（0.35 鼠标） |
|---|---|---|
| `popup_seen ≥ 5` | ✅ 45 | ❌ 未产出（该通道无此计数 —— 这本身是一条缺口） |
| `popup_dismissed == popup_seen` | ✅ 45 == 45（`failed` 键不存在 = 0） | ❌ 清障 0 次 |
| 不早停（跑满题数） | ✅ 60/60 | ❌ 3 题 |
| `score.py` 正常 | ✅ | ✅（但分母只有 3 题 ⇒ **不并入任何成绩**） |
| 立刻打分 | ✅ | ✅ |

### 19.3 鼠标通道为什么打不掉（候选机制，未取证）

`dismiss_interference()` 的三条分支里，**只有键分支**写 `popup_seen/popup_dismissed/popup_dismiss_failed`；鼠标前台分支（`bg=False, keys=False`）**一个计数都没有** —— 所以"没看见"与"看见了没点"在数据上不可区分。它的候选来自 `self._button_candidates(img, "DISMISS")`（**默认 `keep_vetoed=False`**），而键分支特意传了 `keep_vetoed=True`，注释写着："the veto would drop a dialog whose button is not painted as a block"。两个候选机制：**(a)** 候选被 veto 丢掉；**(b)** 该帧里根本没有这个按钮（抓帧与弹窗几何对不上）。下一步必须是**一次只读探针**（dump 弹窗那一帧 + 两种 `keep_vetoed` 对照），而不是直接改代码。

### 19.4 报告 v0.3 改了什么

只改**一处事实错误**及其连带：第 1 章边界句、§5.1 迭代表（新增第 12/13 行）、§5.2 ④ 整段（改判 + 写明真根因是**折叠截断**而不是"看不见"）、§5.3（失败批从四类变五类）、§6.2 D 族与"21 → 22 条"、§7.2 覆盖有洞、§7.3 第 1 项（推翻"把鼠标通道的视觉路径搬过来"这个设想）、第 8 章"还剩"句、`:328` 边界（两条 → 三条欠账）、附录 A 各行与**行号口径注**，并**新增附录 B-3**（本轮四问复查）。`REPORT-draft.md` 顶部加 v0.3 修订说明 + 三处 `popup` 点同步。**没有新增引用、没有复制任何数字**（数字一律指向 `../sol/sandbox/SCORE.md` 批次 12/13 节）。

### 19.5 边界

① 键通道的"可测"**只证明清障路径在 `--keys --bg` 下逐次成立**，不证明真实软件里的模态弹窗同理；② 鼠标通道的失败是**一次 3 题早停**，不是统计意义上的失败率；③ 本段的结论**没有同侪复核**，也没有外部同题对照；④ 本段**没有冻结 #19/#20 的编号口径**，两条都还算"未冻结"。

### 19.6 教训（写进盲区 17）

**"另有一条路径可以借"是一个需要先验证的假设，而不是修法**：批次 8 的失败被解释成"后台键通道没有视觉清障路径、鼠标通道有"，第十段发现真根因是读字段被折叠截断；第十一段去借那条"已有的"视觉路径，才发现它**一次都没点中**。两段加起来一句话：**先证"它本来能不能做"，再谈"能不能借"。**

### 19.7 覆盖面四格表（第二十二段 1a：**依赖更正 → #19 独立走关死路径**）

**依赖更正**：#19 原来记作「`0.70` 档与鼠标通道待补；鼠标通道待 §16 的鼠标 op 修好后再量」，批次 13 的边界里还写成「**剩余部分与 #20 合并处理**」。**这两句都已过时** —— #20 的最终结论**不是**第十五段的"选 C（接受边界）"，而是**通道可用**（第十六段判据达成 + 第十九段保险单实例验证，#20 已收口，见 §25 / §27 / §28.3）⇒ **#19 对 #20 的依赖解除**，#19 从此**独立走关死路径**，不再与 #20 合并记账。

**四格表**（自变量 = 强度档 × 通道；判据 = 每格 **≥5 fire 且清障成对**（`popup_seen == popup_dismissed`、`failed` = 0）；「跑满不早停」**只对键通道两格成立**，理由见第 4 格与 1b 后的改写）：

| 格 | 档位 × 通道 | 批次 | 依据 |
|---|---|---|---|
| 1 | `popup@0.35` × 键（`--keys --bg`） | 批次 12 | ✅ 达标（第十段，`popup_seen/dismissed 24/24`、60/60 不早停） |
| 2 | `popup@0.70` × 键（`--keys --bg`） | 批次 13 第一批 | ✅ 达标（第十一段，`45/45`、60/60 不早停） |
| 3 | `popup@0.70` × 鼠标（前台真鼠标） | 批次 16（16 题）+ 批次 17–19（3 × 16 题） | ✅ 达标（第十六/十九段，fire 14 + 28、四批全跑满） |
| 4 | `popup@0.35` × 鼠标（前台真鼠标） | 第二十二段 1b = **批次 20** | ✅ **弹窗侧达标**：fire **10**（app 侧 `chaos 10 == chaos_planned 10`）、`popup_seen/dismissed 10/10`、`failed` = 0、**补点 1 次**（`interferences 11`）、`task_i 17` 被 modal 挡住 2.18 s 后恢复。⚠ **该格所在批次未跑满**（21/24、退出码 1）：早停题 `task_i 21` 是 `must_refuse`（`prose_only`）、驱动**没走拒答**（`false_accept 1/1`）⇒ 归因见 §7 **#21**、与弹窗通道无关（**补记（第二十六段）：#21 已修** ⇒ 同 seed 同协议复跑 = **批次 21**：24/24 不早停、`task_i 21/22/23` 均 `refused_right`；「未跑满」这条限制自本段起解除，**fire 数仍取本批**） |

**数值与逐条边界一律取 `../sol/sandbox/SCORE.md`**（批次 12/13 节 + 批次 16–19 节 + 批次 20 节）；本表只记"哪一格由哪一批填上"。**1b 结论：四格在弹窗维度全部达标 ⇒ #19 【关死】**（判据 = fire ≥ 5 且清障成对；第四格的「未跑满」不按「跑满不早停」计，理由已写在第 4 格里、并落到新欠账 #21）。诚实边界仍按 19.5：**只覆盖 `popup` 这一类干扰、只覆盖这两个强度档**；`--bg` 鼠标通道与滚轮/拖拽（#18）另计。

---

## 20. 第十二段（2026-10-05）：#20 只读探针 + #18 读代码（都不裂 sha）

### 20.0 一句话

弹窗在鼠标通道打不掉是**两个独立的原因**（**看不见** + **抢前台**），**不是**"点不动"；滚轮与拖拽在 `--bg` 下不生效是**另一个**原因（Tk 忽略 posted 鼠标消息），而且这两条在键通道里**本来就有键盘等价物**、驱动**已经在用** ⇒ 欠账 #18 是**覆盖缺口、不是功能缺陷**。三症状**不是**同一根因。本段**没改一行被测代码**（三件套 sha 仍 `66632d85eac8` / `87470aaff559` / `ef066713a03e`），`../sol/sandbox/SCORE.md` 未动（探针不是批次）。

### 20.1 探针怎么做的（只读，产物全在 `D:\DSH\dsh-actor\tmp\`）

- 起最小 popup 靶子：`gym_app.py --state … --events … --gap 300 --seed 20251007 --scenario t_trap2 --chaos 1.0 --chaos-ms 200,700 --chaos-kind popup`（**不带 `--no-topmost`**，与批次 13-B 同协议）。⚠ 用 `--chaos 0.35` 时那一次掷骰没中就看不到弹窗 ⇒ **探针必须 `--chaos 1.0`** 才能确定性起弹窗。
- 抓四种帧：① 非 bg 驱动实际读的那一帧（**app 矩形屏幕抓帧**，1202×836，弹窗在里面）② **全屏**（2560×1600）③ **app 主窗 PrintWindow**（bg 驱动读的那条）④ **弹窗自己的窗口抓帧**（470×210）。
- 用**驱动自己的 reader** 读这四帧：`Driver.words / _find_blocks / block_label / _button_candidates`，两种 `keep_vetoed` 各跑一遍。
- 两次**真鼠标点击**（用户当场放行）：同一坐标，一次带 `front_title`（= 13-B 的写法），一次不带。
- 脚本与产物（都在 tmp，不进沙箱）：`w14_popup_probe.py` / `w14_read_popup.py` / `w14_read_full.py` / `w14_blocks_caps.py` / `w14_click_button.py` / `w14_click_matrix.py`；`w14-probe.json`、`w14-probe2.json`、`w14-probe3.json`、`w14-probe4.json`、`w14-click-button.json`、`w14-click-matrix.json`，帧 PNG `w14-frame-front/full/printwindow/popup/after.png`。

### 20.2 #20 根因：两道独立门（都实测）

**(1) 看不见 —— 该通道读的那一帧里，按钮从来不是候选。**

- app 矩形帧上 `_find_blocks` 只给 **3** 个块，弹窗区域 **0** 个；把上限抬到 `max_h=400 / max_frac=0.95 / solid=0.6` 仍是 **0** ⇒ 不是"块太大被上限砍掉"。而**弹窗自己的窗口帧**上它恰好给 **1** 个：`box [188,104,96,48]`、`fill 1.00`、`label "DISMISS"`。
- 词路径在那帧只读到散文里**小写**的 `dismiss`（`source text`、`fill_share 0.213`、`neighbours 7`）⇒ 被 veto 规则 `share < 0.45 and neighbours >= 2` 否掉 ⇒ 默认 `keep_vetoed=False` 时候选 **= 空** ⇒ **一次都不点**；`dialog_refused` 每帧 +1 —— 13-B 的 **28** 就是这么来的。
- **全屏帧也读不到按钮**（只多一个 `¥` 噪声）；那帧里的散文反而 `fill_share 0.283 / neighbours 1` ⇒ **不被 veto**，但点它没用（part 1 实测点散文中心 `[686,710]`，弹窗不关）。
- bg 驱动读的 **app 主窗 PrintWindow 帧里根本没有弹窗**（独立 `Toplevel`）⇒ 键通道不走视觉路径是对的（它按窗口标题 + `Return` 清障）。

**(2) 抢前台 —— 就算点对了坐标，通道自己会先把 app 钉成 topmost。**

- 13-B 的 click 都带 `front_title="GUI Gym"`；`_maybe_front(front_top=True)` → `{"op":"window","mode":"top"}` = **pin TOPMOST**（`actor.py` `_front`）。
- 实测：真鼠标点**按钮正中心** `[806,762]`（= 弹窗 client 原点 `[570,634]` + 块中心 `[236,128]`，由 actor 回包的 `origin`/`client` 字段独立校核），**带** `front_title` ⇒ `ok:true`、`click {n 1, button left, ms 4.67}`、回包 `front.mode "top"`，**弹窗仍在**（UIA 同 hwnd 同 rect）；**同一点不带** `front_title` ⇒ 弹窗**立刻消失**。
- ⇒ 失败**不是**"发不出"：`how:"xy"`、`at:[806,762]`、4.7 ms、真 SendInput 到达。是"**读不到按钮**"与"**点之前把 app 抬到弹窗之上**"两道叠加。

### 20.3 #18 读码结论（滚轮 / 拖拽）

- **滚轮**：`wheel()` 定义在 `gym_run.py:1214`，**唯一调用点 `gym_run.py:2329`**，写法 `if self.keys: self.key("Next") else: self.wheel(-3, …)`（"行没出现"的重试分支）；注释已记录实测原文："the wheel is a mouse message and Tk ignores those while it is not focused (measured: 63 posted wheel steps moved nothing at all)"。app 侧有**完整键盘路径**：`keymap["Next"]=lambda: self._page(1)`（另有 Prior/Up/Down/Home/End），`_page()` 在 `gym_app.py:414-432`。⇒ **键通道本来就靠 `Next` 翻页、驱动已经在用**；滚轮只是"没有键盘路径时"的兜底 ⇒ **不是缺口**；`--bg` 下 posted `WM_MOUSEWHEEL` 被 Tk 忽略（`post_scroll` 固定发到窗口中心，**与焦点无关**）。
- **拖拽**：`drag()` 定义在 `gym_run.py:1208`，**唯一调用点 `gym_run.py:2877`**（chips 的视觉兜底：`if hs and hd: self.key(hd) … else: self.drag(…)`）；app 侧有鼠标绑定（`gym_app.py:948-961`）**同时有完整键盘路径**（`_bind_key(i, drop_slot)` / `_bind_key(len(slots)+i, pick)`，doc "Keyboard path: pick a chip up, then name the slot it goes into"）。全仓扫描：**没有任何批次 json 的 `drags > 0`**；`drags 3`/`drags 9` 出自 §16 的 P4/P5（鼠标 + 强制 `--bg`，0/3 早停）与 `HANDOFF.md` 盲区 21；同场景键通道 8/8（§16 P1b/P3）。⇒ **`--bg` 下拖拽不生效与滚轮同一坑**；键通道有等价物 ⇒ **覆盖缺口、不是功能缺陷**。
- **行号漂移更正**（§7 #18 行与 `HANDOFF.md` 盲区 21 里记的是批次 11 时代的坐标）：`wheel()` 由 `1199–1210` 漂到 **`1214`**、调用点 `2314` → **`2329`**；`drag()` 由 `1193–1197` 漂到 **`1208`**、调用点 `2862` → **`2877`**（批次 11 的 `ShotFailed` 补丁加了 ~15 行）。
- **共同点（修正本段规格第三节的假设）**：滚轮 + 拖拽 = **一个**根因（Tk 忽略 posted 鼠标消息）；弹窗鼠标通道 = **另一个**根因（帧来源 + topmost pin）。**不是"一个根因、三个症状"。**

### 20.4 下一步选项（明天选一个；本段不开代码线）

- **A 给鼠标 op 加 focus/物理通道**：对滚轮/拖拽**无必要**（键通道已有等价物），只对"必须用鼠标"的场景有意义。不建议。
- **B 前台鼠标批**：已经在用（13-B）；修好 #20 的两道之后前台就有意义了。
- **C 接受"键通道优先"**：现状已成立（弹窗键通道两档 ✅、滚轮/拖拽键通道 8/8），把鼠标通道交互写成已知边界。
- **D（本段新增，最小改动，建议先评估这条）**：非 bg 鼠标分支**照抄它下面 `if self.bg` 分支的做法** —— ① 读**弹窗自己的窗口**取按钮（`shot_window("attention")` + `_button_candidates`，实测那帧给的是**干净、未被 veto 的块候选**）；② 点击时**不要把 app 钉成 topmost**（实测不带 `front_title` 就点得掉）。量级约 **10–15 行**，不动判定逻辑；修完 #20 的判据（跑满 + `popup_dismissed == popup_seen ≥ 5`）**有可能一批满足**。

### 20.5 边界

① 探针是**单实例**（一个靶子、一次弹窗、两次真点击），不是统计；② 坐标是这一台的（2560×1600、per-monitor DPI）；③ "看不见"只定位到"该帧上块检测不返回这个按钮、词路径只给被 veto 的散文"，**没有**继续挖块检测内部为什么在那帧上漏掉它（抬上限无效，`solid` 放宽也无效）；④ 真鼠标点击是用户当场放行的，且只做了两次；⑤ 本段**未改一行被测代码**、`../sol/sandbox/SCORE.md` 未动、`REPORT.md` 未动。

### 20.6 教训

- **先分清"看不见"和"点不动"，再谈"借路径"**：第十一段把 13-B 的失败归到"候选被 veto"一条；本段对照**四种帧来源 + 两次真点击**才看清是**两道独立门**，其中第二道是**通道自己加的**（`front_title` → `mode: top` 把 app 钉到弹窗之上）。
- **同一段代码里隔壁分支可能已经写对了**：`dismiss_interference()` 的 `if self.bg` 鼠标分支读的就是弹窗自己的窗口（正是实测唯一能读到按钮的那一帧）。修法常常是"照抄隔壁分支"，而不是发明新通道。

## 21. 第十三段（2026-10-05）：#20 修复尝试（选项 D）—— 方向有效、判据未过、**已回退**

### 21.0 一句话

本段按 §20.4 的**选项 D** 真去改了 `gym_run.py`（裂一次 sha）：干跑 **2/2**、清障 **2/2**；正式批清障 **10/11**，但在 **task 21 早停**（连续 3 次失败、退出码 1）⇒ **判据未达成**，按本段规格的终止条件**回退**，`gym_run.py` 回到 `87470aaff559`。**#20 仍然开着**，但失败面从"一次都没点中（0/28 帧）"缩到"11 次里漏 1 次"。

### 21.1 事前写死的假设与判据

- **假设**：非 bg 鼠标分支只要**读弹窗自己的窗口帧** + **点击不带 `front_title`**，就能清掉弹窗（把 §20.2 的两道门一次修掉）。
- **判据**：A 批（鼠标通道 `popup@0.35`、60 题）`popup_seen ≥ 5` 且 `popup_dismissed == popup_seen` 且**不早停**；B 批（鼠标通道 48 题，与批次 9 同协议）核心 14 **无 ok→wrong 翻转**。
- **硬闸**：改动 > 30 行、或影响范围波及共享帧读取/点击路径 ⇒ 停手写欠账。

### 21.2 做了什么（两处，都在弹窗清理路径内；净 +26 行）

1. `dismiss_interference()` 非 bg 鼠标分支：`window_by_title("attention")` 判在不在 → `shot_window("attention")` 取**弹窗自己的帧** → 侯选取自该帧 → 一条**不带 front 请求**的 `click` 直投（绕开 `click()` 的 `front_title`）；新增 `popup_seen` 与 `popup_dismiss_failed/dismissed`。
2. `shot_window()`：屏幕原点改用回包的 **client origin**，不再用**窗口 rect**（实测差 **+11 / +45 px** —— 第一版就是栽在这里：干跑 `popup_seen 13 / popup_dismiss_failed 13`、两题全 NONE）。

影响范围 = **只影响弹窗清理**（`shot_window()` 只有 `dismiss_interference()` 里那两个调用点；`click()` / `_shot()` / `_button_candidates()` / `screen()` 一行未动）⇒ 硬闸未触发。`py_compile` 通过、`score.py --selftest` = 41 checks / 0 failed；中间 sha `6690c1038c7f42f7` → `85893817760a3be5`（跑批版本）。

### 21.3 结果（数字一律去 `../sol/sandbox/SCORE.md` 批次 14 节取）

- **干跑** `--tasks 2`（鼠标通道、`chaos 1.0 popup`）：2/2、`popup_seen 2 / dismissed 2`、5.3 s/题。
- **正式批**（`t_trap2-w13-popup35-mouse-fix.json`，唯一一次）：**exit 1**、墙钟 161.2 s、`stopping early: task 21 failed 3 times in a row`；`popup_seen 11 / popup_dismissed 10 / popup_dismiss_failed 1`、`clicks 52`、app 侧 `blocked 1`。
- **判据**：`popup_seen ≥ 5` ✅（11）；`dismissed == seen` ❌（10/11）；不早停 ❌。⇒ 终止条件触发。
- **B 批未跑**：改动已回退，被测代码 = HEAD，无可回归对象。

### 21.4 为什么回退、留下了什么

- 回退动作：`git checkout -- ../sol/sandbox/gym_run.py` ⇒ 三件套 sha 回到 `66632d85eac81c12` / **`87470aaff5593330`** / `ef066713a03eb940`（`py_compile` + `selftest` 复验通过）。
- 留档：补丁 `D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`（77 行）；本批 run json 留在沙箱但**明确标注"不进成绩、不可复现"**（它对应的驱动不在仓库里）。
- 残留机制（待明天）：11 次里漏 1 次，之后**没有任何重试** ⇒ 题目死锁。三个候选：**(a)** 同一点允许补点一次；**(b)** 失败时降级用 `key("Return")`（app 自己绑定：主窗收到该键就关自己的对话框）；**(c)** 把 `gym_run.py:3460` 的"清障计数 ≠ 0 ⇒ break 去 replan"改成"再清一次再 replan"。

### 21.5 教训

- **干跑的价值在这次体现得很直白**：第一版（只改分支、沿用窗口 rect）干跑就把"点了 13 次、一次没中"暴露出来，省下一整批 60 题；第二版干跑 2/2 才放行正式批。
- **"方向对"不等于"判据过"**：本段把失败率从 100% 降到 ~9%，但规格写的是 `dismissed == seen` 且不早停 —— 一次竞态就足以让整批作废。这类"单次漏点即整题死锁"的耦合本身就是下一步要拆的对象（候选 (c)）。
- **回退也要留证据**：回退不是删记录；补丁 + run json + 本节的中间 sha 让明天可以从"10/11 有效、1/11 死锁"继续，而不是从零重来。


## 22. 第十三段（2026-10-05）：#18（滚轮 + 拖拽）设计落盘 —— **只写设计，不改代码、不加题型**

### 22.0 一句话
欠账 #18 第一次被写成可执行设计：`vision-work/audit/DESIGN-18-scroll-drag.md`（现状 / 已有键盘等价物 / 要补什么 / 三方案 A·B·C / 推荐 / 判据）。**本段未改一行代码、未加任何题型**；三件套 sha 与 §21 回退后完全一致。

### 22.1 结论摘要（细节全在设计文档，此处只留指针与骨架）
- **现状**：v1–v3 口径下覆盖 = 0（计划表 `TRAP_PLAN`/`PLAN2`–`PLAN5` 从不排 `t_rows`/`t_chips`；所有 `t_trap*` 记录 `stats.scrolls = 0`、`stats.drags = 0`）；第十一段的六跑只是**探针**，不进成绩；v0 时代的 rows/chips 文件**一律不可引用**（`SCORE-history.md` 勘误）。
- **已有等价物**：滚轮 ⇒ `Next`/`Prior`/`Up`/`Down`/`Home`/`End`（`gym_app.py:714-735` 的 `bind_all("<MouseWheel>")` 同处把 `keymap["Next"]` 绑到 `_page(1)`，`_page()` = `:425-432` 的 `c.yview_scroll(step*9,"units")`），驱动**已经在用**（`gym_run.py:2329` 的 `if self.keys: self.key("Next") else: self.wheel(-3, …)`）；拖放 ⇒ `_bind_key(i, drop_slot)` / `_bind_key(len(slots)+i, pick)`（`gym_app.py:948-961` 邻域）。⇒ 本族是**覆盖缺口，不是功能缺陷**（§20.3）。
- **要补什么**（四件事，键盘等价物替不了）：① 连续量的物理性（方向 / 单格幅度 / 累计位移，键通道的 `Next` 是离散翻页，把"滚多少"整个抹掉）；② 轨迹与落点精度（起点抓得准不准、中途经过什么、偏几像素算命中）；③ **动作中途的干扰适应**（拖拽进行中撞上 `move` ⇒ 必须重新抓帧重算落点）；④ "键盘等价物根本不存在"的真实界面（画布 / 拖拽排序 / 按住拖选 / 地图式视口）——这条不影响已有结论，但影响**口径可移植性**（`REPORT.md` §7.3 第 5 项）。
- **八问现状**（§16.4 逐条判定，此处只记状态）：滚轮四问 = 1 能 / 1 代码级一致 / 2 量不到；拖拽四问 = 4 量不到。**量不到的原因不是驱动不会，而是没有一条不抢前台的通道能把鼠标动作送进 Tk。**
- **三方案**：**A 前台鼠标批**（零代码改动，驱动两条路径本来就在；代价 = 每次占用前台与指针、必须标通道、单窗口串行）/ **B 给鼠标动作加物理通道**（裂 sha；两条硬伤：① 真 `SendInput` 本质上仍要前台，占用不会消失 ⇒ 它只是 A 的自动化版本；② 改动落在**执行器** `D:\DSH\dsh-vision-kit\actor`，而 `scripts_sha` 只覆盖沙箱三个文件 ⇒ 这批是谁跑的无法从留档核对，违反记账纪律）/ **C 接受键通道优先、把鼠标交互写成已知边界**（零成本、与报告既有边界写法一致）。
- **推荐**：**C 作为默认口径 + 需要真凭据时用 A 跑一次窄批（12–16 题，两场景各半）+ B 暂不做。** 理由：这是覆盖缺口而非缺陷，不该为它引入第二套鼠标实现与不可核对的改动（详见设计文档第 5 节）。
- **判据**：设计文档第 6 节 = 前置 8 条（一行代码不改 / venv / actor ping / 单窗口串行 / `-WindowStyle Normal` / 干跑 `--tasks 2` 看 `stats.scrolls`·`stats.drags > 0` / 前后 `wait_until_unlocked()` / 跑完立刻打分）+ **滚轮四问**（会不会滚 / 方向 / 幅度（`dy = 120` 每格）/ 滚完必须重新定位）+ **拖拽四问**（会不会拖 / 起点抓准 / 落点精度 / 中途 `move` 能适应）+ **收口三选一**（C 成立 / A 部分成立 ⇒ #18 改"部分覆盖（鼠标通道、单批少量题）" / A 完全成立 ⇒ 关闭）。

### 22.2 与其它文档的关系
- **原始只量记录**：本文 **§16**（六跑 + 八问逐条判定）—— 别再重做一遍；盲区条目：`HANDOFF.md` **盲区 21**（已加一行指向设计文档）。
- **报告侧**：`REPORT.md` §6.2 D 族 / §7.2 已把"滚轮与拖拽没有有效覆盖"写成边界（v0.4 后措辞未变）；若将来走 A，报告需按"通道 + 单批少量题"的标签同步，并在 §5 迭代表新增一行。
- **本段不动任何代码**：`gym_app.py 66632d85eac8` / `gym_run.py 87470aaff559` / `score.py ef066713a03e`（与 §21 回退后一致）；不动任何批次 json；`../sol/sandbox/SCORE.md` 无新增节（设计不是成绩）。

### 22.3 教训
- **"没测过"和"测不了"要分开写**：这一族在键通道上早就跑得通（探针 rows 8/8、chips 8/8），真正缺的只是"放进计划表、按鼠标通道跑一次"。把两者混在一句话里，下一个人会误以为驱动不支持滚轮 —— 设计文档把它们分列成两节就是为了防这个误读。
- **设计也要带判据**：本文件第 6 节直接沿用 §16 的八问，只把"量不到"改写成"要量它需要什么条件"。设计的价值在于让下一次动手的人**不必重新推导**，而不是多写一份说明书。
- **不可核对的改动要提前否掉**：B 被否的理由不是难，而是它会把读数重新变得不可核对（改动进不了 `scripts_sha`）。**记账纪律可以先于技术评估做决定。**

## 23. 第十四段（2026-10-05）：#20 第二次修复尝试 —— **漏点处理路径**（降级用 app 自己的按键）

### 23.0 一句话
选了 **(b) 降级 `key("Return")`**（净 +24 行，只在非 bg 鼠标分支的"漏点处理"路径上）⇒ **干跑 2 题即失败**（`popup_seen 13` 但 `popup_dismissed` 键根本不存在 = 一次都没清掉，两题全 NONE，exit 1）⇒ 按本段终止条件**立即回退**（sha 回 `87470aaff5593330`），**`#20` 保持开着**；机制结论：**这条通道里 `key()` 发的是真实 SendInput 按键，要求目标窗口真持有前台焦点，而本机 DSH 会不断抢回前台 ⇒ 45 次 Return 全部落空**；只有"按坐标投递"的鼠标点击能命中 topmost 的弹窗（这也解释了批次 14 的点击路径为什么能 10/11）。A/B 两批都没跑（干跑即证伪，不试第二遍改动）。

### 23.1 事前写死的假设与判据（动代码**之前**写）

**读码结论（先选方向）**：三条方向里 **(b) 降级 `key("Return")` 最像真因**；(c) 的耦合确实存在但**单独修不好**（见 23.1.1 ①），(a) 是对着未知原因再赌一次同一条路。

**假设**：批次 14 的"11 次里漏 1 次"不是点击算法的问题（那条路 **10/11 有效**），而是**漏点之后没有第二条路**。证据链：驱动非 bg 鼠标分支把"我点了一次"（`seen`）当成"弹窗没了"，而它**从不检查弹窗是否真的消失**；调用侧 `gym_run.py:3461` 见 `n`（= `seen`）非零就 `break` 去 replan，此时弹窗往往还立着；app 侧"弹窗在 ⇒ 什么都不判分"（`_chaos_popup` 只在 `close()` 里清 `self.modal`）⇒ 该题与**之后每一题**都判不出结果 ⇒ `task 21 failed 3 times in a row` 早停。⇒ 只要在**鼠标没清掉**时补一条**不依赖坐标**的降级路径（app 自己在弹窗按钮上绑了 `Return`/`space`），#20 的判据就能过。

**证伪条件**：(i) 改后 `popup_seen > 0` 但 `dismissed < seen`（真有清不掉的弹窗）；(ii) 改后 B 批（鼠标 48 题）核心 14 出现 ok→wrong 翻转；(iii) 改动超 30 行。
**观测点**：`popup_seen` / `popup_dismissed` / `popup_dismiss_failed` / 新增 `popup_key_dismissed`、`interferences`、`dialog_refused`、核心 14 逐题、改动行数。
**判据**：i–iii 全不成立；A 批（鼠标通道 `popup@0.35`、60 题）`popup_seen ≥ 5` 且 `dismissed == seen` 且**不早停**；B 批核心 14 无翻转。

### 23.1.1 三条方向逐条读码（结论先行）

**① `gym_run.py:3459-3465` 的耦合（候选 c）—— 真实存在，但单独修不好**
```python
                    if a.chaos:             # a popup may be what is holding the verdict
                        _, n = d.dismiss_interference()
                        if n:
                            rec["interferences"] = rec.get("interferences", 0) + n
                            # the dialog is gone, but the press it swallowed was never
                            # scored: stop waiting and answer again (replan below)
                            break
```
- **触发条件**：只在 `--chaos` 下、且"等待判定 4.4 s 没等到"时进入。
- **是驱动侧**（`gym_run.py` 的 run 循环），不是 app 侧：`n` = 该分支**自己发起了几次点击**，不是"弹窗已消失"的证据；非 bg 鼠标分支每次都 `seen += 1`，唯一的存在性检查是 `if not self._button_candidates(img, "DISMISS")`，而那一帧（app 矩形帧）**永远给不出候选** ⇒ HEAD 上它是**点 0 次就 break**。
- **拆掉它会怎样**：不会立刻死锁，但也没有救 —— 弹窗还立着 ⇒ 每题都判不出结果 ⇒ 仍然 `3 times in a row` 早停。⇒ **(c) 只改变"死在哪一步"，不改变"会不会死"。**

**② 同点补点一次（候选 a）**：现在 `tries=3` 的循环只换**不同的**候选（8 px 去重），从不补点同一点、也不做窗口存在性校验。补一次的成本 ≈ 一次 actor 往返 + 0.3 s ≈ 0.4 s（便宜），但**失败原因未知**（批次 14 的 1/11 是同一坐标静默失败），同点重试是**对着未知原因再赌一次**，且不改变"弹窗还在 ⇒ 全批死"的结构。

**③ 降级 `key("Return")`（候选 b）**：app 侧 `gym_app.py:635-649` = `btn.focus_set()` + `btn.bind("<Return>")`/`<space>`（`close()`）+ `top.bind("<Escape>")`；驱动键分支本来就走这条路（`:926 self.key("Return")`，`:911-912` 注释："the app closes its own dialog when the main window gets the key"），**实测 24/24（批次 12）+ 45/45（批次 13-A）**。`Driver.key()`（`gym_run.py:1175-1198`）在非 bg 鼠标通道发的是**真实前台按键**（带 `front_title`；`focus=True` 只在 `keys and bg` 时加），弹窗与主窗**同进程**，Tk 把按键交给**持有焦点的控件**（`btn`）⇒ **不用坐标、不看层叠、不读像素**。
- **残留风险（要写进收口）**：若在弹窗立着期间有别的控件抢走了 Tk 的控件级焦点（例如驱动点到了某个 Entry），Return 会落到那个控件上。降级路径只在"弹窗确实还在"时触发，触发时 `btn` 是最后被 `focus_set` 的控件。

### 23.2 做了什么

**只改一处：`gym_run.py` 非 bg 鼠标分支的"漏点处理"路径**（`dismiss_interference()` 尾部，`git diff --stat` = **24 insertions(+), 0 deletions(-)**，未触 30 行硬闸）。改动内容：原循环（"读 app 矩形帧 → 找候选 → 点 → 睡 0.3 s → 再看还有没有候选"）**原样保留**，循环之后新增：

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

**没碰**：`click()` / `_shot()` / `_button_candidates()` / `screen()` / 判定逻辑 / 匹配路径 / 阈值（全部一行未动）；`gym_app.py`、`score.py` 一行未动；批次文件未动。

**闸门**：`py_compile` 通过；`score.py --selftest` = **41 checks, 0 failed**。改动后中间态 sha = `gym_run.py 178591e19c40c37f`（`gym_app.py 66632d85eac81c12` / `score.py ef066713a03eb940` 未动）。

**为什么选 (b)**：见 23.1.1 —— (c) 的耦合真实但单独修不好（只改变"死在哪一步"），(a) 是对未知原因再赌一次同一条路，(b) 是唯一"不依赖坐标"的第二条路，而且 app 自己在按钮上绑了 `Return`/`space`。

### 23.3 结果：干跑即失败（**没有进入 A 批**）

干跑 = 鼠标通道、`--tasks 2`、`--chaos 1.0 --chaos-kind popup`（确定性立弹窗）、`--seed 20251007`、`--json-out D:\DSH\dsh-actor\tmp\w16-dry.json`、日志 `D:\DSH\dsh-actor\tmp\w16_dry.log` / `.err`。

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

`w16-dry.json` 的 `stats`（逐字）：`clicks 0, keys 45, interferences 39, replans 66, popup_seen 13, popup_dismiss_failed 13, dialog_refused 1, refusals 6, ask_guard_runs 1, ask_moved 1, shots 20, ocr 85, ms_ocr 41943.9, ms_key 2331.1, ms_window 316.9`；`exit_reason: None`、`partial: False`、`mode {bg false, keys false, chaos 1.0, chaos_kind popup, chaos_ms "200,700", max_tasks 2}`。

**判读**：**`popup_dismissed` 与 `popup_key_dismissed` 两个键在 stats 里根本不存在** ⇒ 新增的降级路径**一次都没成功**（13 次发现弹窗、13 次记 `popup_dismiss_failed`、45 次 Return 全部落空）。两题都因为"弹窗立着 ⇒ app 什么都不判分"而超时 NONE。⇒ 这就是 23.1 写死的证伪条件 (i) 的**更强版本**：不是 `dismissed < seen`，而是 `dismissed == 0`。

**环境检查（干跑后）**：`uia what=windows max=200` 里**没有任何 'GUI Gym' / 'attention' 窗口**（app 已被驱动收尾），Windows 侧 python 进程只剩 actor `12008` + `32248`；`../sol/sandbox/_gym_win.png` 是 `shot_window` 的临时抓帧文件。

### 23.4 为什么回退、以及回退后的账

- **回退**：`git diff > D:\DSH\dsh-actor\tmp\w16-popup-key-fallback.patch`（35 行）留档 ⇒ `git checkout -- ../sol/sandbox/gym_run.py` ⇒ sha 回 **`87470aaff5593330`**（与 `origin/main` 一致），`py_compile` + `selftest 41 checks / 0 failed` 复验通过。
- **A 批 / B 批都没跑**，理由 = 探针（干跑）已经证伪了改动：A 批的判据是 `dismissed == seen`，而实测 `dismissed == 0`，再跑 60 题只是把同一个失败重复 60 次。这符合本段"**同一段不试两次代码改动**"和"不硬推"的终止条件。
- **机制结论（本段最值钱的一条）**：`Driver.key()`（`gym_run.py:1175-1198`）在非 bg 通道发的是**真实 SendInput 按键**，Windows 只会把它交给**真前台窗口**；而本机（DSH 自己会不断抢回前台）这条通道**抢不稳前台** —— 这一跑里 45 次 Return 全部没落到弹窗上（`foreground after: 搜索 (hwnd 66100) unchanged: False`）。对照：鼠标点击是**按坐标**投递的，弹窗是 `-topmost`，像素命中了就一定能收到 ⇒ **批次 14 的点击路径 10/11 有效不是偶然，而是这条通道里唯一能到弹窗的机制**。
  - 推论：键通道能在 `--bg` 下拉弹窗，靠的不是"按键能到"，而是驱动**把按键直接投递给 app 窗口 + `focus=True` 做焦点交接**（`self.keys and self.bg` 才加，见 `:1175-1198`）；这条非 bg 路径**没有**这个机制（非 bg 走真实前台按键）。
  - ⇒ (b) 这条方向**不是"没写对"，而是结构上不成立**（除非把降级改成"投递到 app hwnd + 焦点交接"，那已经是 **B 方案**（给鼠标通道加物理/托管通道）的范围，不是本段允许的"优先小改动"）。
- **三条候选的最终状态**：(a) 同点补点 —— 未试，仍是"对着未知原因再赌一次"；(b) 降级 Return —— **本段实测否掉**（结构不成立，见上）；(c) 拆耦合 —— 未试，且 23.1.1 已论证**单独修不好**。⇒ `#20` 仍然开着，下一步要么接受边界（C），要么走 B（给鼠标通道加托管按键/焦点交接，裂 sha 且改动落在执行器侧、`scripts_sha` 覆盖不到，见 `DESIGN-18-scroll-drag.md` §4 的同一论点）。
- **边界（不可引用为成绩）**：本次是 **2 题干跑**，不是批次；`w16-dry.json` 是诊断证据、**不进任何成绩**；改动已回退，仓库里没有任何"修好的版本"可复现（补丁只在本机 tmp 里）。

### 23.5 教训

- **"发得出"不等于"到得了"**：同一条 `key()` 调用，在 `--bg` 通道里是"投递 + 焦点交接"（必达），在非 bg 通道里是"真实按键 + 指望前台"（不可靠）。**改代码前要先问"这个 op 在这个通道里是怎么送达的"**，而不是只看它上一条通道里的战绩（批次 12/13-A 的 24/24、45/45 都是 bg 通道的成绩）。
- **干跑这一步救了 60 题的浪费**：判据写在跑之前（23.1），所以"干跑 2 题就证伪"能立刻停；如果先跑 A 批再判，代价是 3 分钟 + 一次前台占用 + 一份不可用的 json。
- **同一个数字可以是"能力"也可以是"巧合"**：批次 14 的 `10/11` 看起来像"快好了"，本段证明它是"这条通道只有这一种投递机制"的副作用 —— 剩下的 1/11 不是调参能补的。
- **回退不等于白做**：这一段的产出是"把 (b) 从候选里划掉 + 说清为什么"，比留着一段过不了判据的代码有价值；补丁留档使得"重做一遍"不需要重新推导。

---

## 24. 第十五段（2026-10-05）：#20 通道层三选一 —— 评估与决策（**不改代码、不跑批、不裂 sha**）

### 24.0 一句话

第十四段把候选 (b) 实测划掉之后，#20 剩下的不是"再换一种写法"，而是**在哪条通道上认账**。本段只做评估与决策：**选 C（接受边界）**；A（重新落地选项 D 补丁 + 前台窄批）降级为"需要真凭据时的一次性手段"；**B 不做**（改动落在 `scripts_sha` 覆盖不到的执行器侧）。本段未改一行代码、未跑任何批次，三件套 sha 与第十四段收工**完全一致**。

### 24.1 评估依据（三处，逐条读到）

1. **`STATE.md` §23.4 的收敛结论**：非 `--bg` 通道的 `key()` 是**真实 SendInput 按键**（`Driver.key()` `gym_run.py:1175-1198`，只有 `self.keys and self.bg` 才加 `focus: True` 做焦点交接），本机前台会被不断抢回 ⇒ 第十四段的 45 次 `Return` 全部落空；而鼠标点击**按坐标**投递、弹窗又是 `-topmost` ⇒ 像素命中即达 ⇒ 这一支只剩"按坐标投递"一种机制。
2. **`gym_run.py:3458-3465` 的耦合**（第 23.4 节候选 (c) 的真身）：`if a.chaos: _, n = d.dismiss_interference(); if n: rec["interferences"] += n; break`，注释逐字 *"the dialog is gone, but the press it swallowed was never scored: stop waiting and answer again (replan below)"*。**`n` 只表示"点了一下"，不表示"弹窗没了"** ⇒ 漏一次点 = 判定等待循环提前退出 + 转 replan，而弹窗仍立着 ⇒ app 什么都不判分 ⇒ `tries = 3`（`:3426`，注释写明 chaos 时给 3 次）耗尽 ⇒ **三连败早停**。批次 14 在第 21 题停下就是这个机制（逐条数值见 `../sol/sandbox/SCORE.md` 批次 14 节 14.3/14.5）。
3. **actor 的 `_maybe_front()`**（逐字 docstring）：*"Input ops may carry front=<hwnd> or front_title=<substring>: raise (and pin) the target first, so DSH stealing the foreground cannot eat the keystrokes."* + `_front(..., top=True)` ⇒ **执行器本来就自带"钉最上层 + 抬前台"的输入前处理**：它既是 `--bg` 键通道能工作的原因（配合 `o_key` 的焦点交接），也正是鼠标分支点不中弹窗的机制（它把**主窗**钉到了弹窗之上）。⇒ 选项 B 要动的正是这条**被鼠标/按键两种 op 共用**的路径。

### 24.2 三个选项

| 选项 | 改动范围 | 是否裂 sha | 判据 | 风险 |
|---|---|---|---|---|
| **A 前台批 + 显式声明通道** | **必须先重新落地第十三段的选项 D 补丁**（非 `--bg` 鼠标分支改读**弹窗自己的窗口帧** + 点击**不带** `front_title`；补丁留档 `D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`）—— HEAD 版本的鼠标分支在自己的抓帧里**看不到按钮**（§20.2 门①），不落地补丁**连"前台批"都跑不起来** | **裂**（`gym_run.py`） | 鼠标通道 `popup@0.35` 跑满题数、`popup_seen ≥ 5` 且 `dismissed == seen`、不早停 | ① 残留的漏点（批次 14 那 10/11 里的 1）是**坐标投递对"弹窗被重建 / 移动"的固有竞态**，调参补不上；② 因为 §24.1-2 的耦合，**漏一次就早停** ⇒ 能否跑满 60 题由运气决定、不由修法决定；③ 占用前台约 5–8 分钟（按批次 14 的逐题耗时换算，数值见 `../sol/sandbox/SCORE.md` 批次 14 节 14.3） |
| **B 给鼠标动作加托管输入 + 焦点交接** | `D:\DSH\dsh-vision-kit\actor\actor.py`（`o_click` / `_maybe_front` 一线），**不在被测工件内** | **裂的不是三件套 sha** —— 改动落在 `scripts_sha`（只覆盖 `../sol/sandbox` 三件套）**覆盖不到的层** ⇒ 以此跑出的读数在留档里**不可核对**（第十段 #16 的根因就在 actor 侧；第十三段已用同一理由否过一次） | 改动后鼠标通道 `popup` 批 `dismissed == seen` | ① `_maybe_front` 是**两种 op 共用**的输入前处理，改它等于改所有输入 op 的语义（actor 是全机常驻件、别的任务也在用）；② 焦点交接**必然要动前台** ⇒ 与 `--bg` 通道"不抢前台"的性质冲突；③ 收益边际：成功了也只是让一条**已被键通道覆盖**的能力"在鼠标通道上也能测" |
| **C 接受边界** | **0**（只改文档：本节结论 + `HANDOFF.md` 盲区 23 + 报告 v0.6 的 §5.2 ④ / §6.2 D 族各一句） | 不裂 | `HANDOFF.md` 盲区 23 与报告里把"**键通道两个强度档可测、鼠标通道 `popup` 不可测**"写成**显式边界**并给出机制（两道门 + 投递机制 + 耦合） | 该组合**永远不进入自动化覆盖**；代价是这条覆盖面缺口被永久记在账上 —— 这正是诚实的做法：欠账**保持开着**，不改写成"已关闭" |

### 24.3 决策：**C**（A 降级为按需、B 不做）

- **选 C，三条理由**：① #20 已经花掉两次改动机会（第十三段选项 D、第十四段降级按键），第三次改动的边际收益递减；② 键通道两个强度档的 `popup` 成绩是**有效且已定稿**的成绩（`../sol/sandbox/SCORE.md` 批次 13 节），缺口只落在"鼠标通道"这一个组合上；③ C 让账目更清楚 —— 把"测不了"写成边界，比"再赌一次、可能过可能不过"更能保住"**数字可核对**"这条线。
- **A 的定位 = 手段，不是计划**：只有当外部明确要求"鼠标通道 `popup` 也能清障"的**真凭据**时，才**先拆 §24.1-2 的耦合**（否则一次漏点就早停、白占前台），再重落补丁 + 跑一次 60 题前台批，并**显式声明通道与前台占用**。这两步都属于"改 + 批"的段，不是决策段。
- **B 不做**：与 `DESIGN-18-scroll-drag.md` §4 的 B **同根**（改执行器、`scripts_sha` 覆盖不到、改动面大），两处一起否掉。

### 24.4 边界（本节不能当成绩读）

- 本段**不改代码、不跑批、不裂 sha**：三件套 sha 与第十四段收工一致，仓库里没有新增任何证据 json。
- `STATE.md` §7 **#20 行保持"根因已定案 / 判据未达标"**，**不改"已关闭"**：C 采用的是该行判据栏的**第二个分支**（"或明确宣告鼠标通道不支持清障并把该组合从覆盖面里划掉"），而"划掉"要在文档里写清才算数 —— 本节 + `HANDOFF.md` 盲区 23 + 报告 v0.6 就是这三处落点。

### 24.5 要点（可复用）

- **"改哪里"与"改多大"是两个问题**：B 看起来只是加一次焦点交接，但它落在**两种 op 共用**的路径上 ⇒ 语义面远大于行数。
- **耦合会把小概率失败放大成必然失败**：1/11 的漏点本身可忍，配上"漏一次就早停"（`if n: … break`）就变成整批不可用 ⇒ 评估修法时必须把耦合算进代价。
- **决策段也要写判据**：C 的判据是"文档里写清边界与原因"，不是"心里的决定"。

## 25. 第十六段（2026-10-05）：#20 第三次尝试 —— 重落选项 D 补丁 + 拆耦合；16 题前台窄批全过、判据达成

### 25.1 起点与授权

第十五段把 #20 定成"接受边界（C）"，同时把 **A（前台批）降级为"按需"** 并写死两个前置条件（§24.3）：**必须先重落第十三段的选项 D 补丁**（否则连弹窗上的按钮都读不到）、**必须先拆掉"漏一次点 ⇒ 整题死锁"的耦合**（否则一次漏点就白占前台）。第十六段开工时用户在三选一里选了 **(ii)「需要真凭据」** ⇒ 本段的任务就是**把这两个前置条件做完 + 跑一次 12–16 题前台窄批**，而不是再改第三种坐标/按键写法。

### 25.2 改了什么（`../sol/sandbox/gym_run.py`，净 +30 行，两处都在清障路径内）

1. **重落第十三段选项 D 的补丁**（`git apply D:\DSH\dsh-actor\tmp\w15-popup-fix.patch`，36 insertions / 10 deletions，**一字未改**）：① `shot_window()` 改 `results=True` + 用回包的 **client origin** 当原点（窗口 `rect` 与 client origin 实测差 +11 / +45 px）；② 非 bg 鼠标分支照抄隔壁 `if self.bg` 分支 —— 读**弹窗自己的窗口帧**、点击**不带 `front_title`**（带则 `mode: top` 会把 app 钉在弹窗之上）、收尾按"还在不在"记 `popup_dismissed` / `popup_dismiss_failed`。应用后 sha = **`85893817760a3be5`**，与批次 14 的被测版本**逐位相同**。
2. **拆耦合**（净 +4 行）：**(a)** 同一落点（±8 px）已点过两次即不再当候选 ⇒ 允许补点一次（候选取自当帧 ⇒ 补点只会落在仍立着的弹窗上）；**(c)** 清障后**只有 `window_by_title("attention") is None` 才 `break`** —— 原代码 `if n: … break` 里 `n` 只表示"点了一下"，漏点也 `break` 去 replan ⇒ **弹窗还立着、靶子什么都不判分、`tries=3` 耗尽 ⇒ 一次漏点 = 整题死锁**（批次 14 停在第 21 题即此机制）。

- `git diff --shortstat` = **43 insertions(+), 13 deletions(-)** ⇒ 净 **+30 行**；`STATE.md:1099`/§14 的硬闸写的是"改动 **> 30 行** ⇒ 停手" ⇒ **未触发**，但**与阈值相等（贴线），如实标注**。**没碰**：`gym_app.py` / `score.py` / 判定逻辑 / 匹配路径 / 阈值 / `press_guard` / `_redo`；批次文件未动。
- 闸门：`py_compile` 通过；`score.py --selftest` = **41 checks, 0 failed**。
- **sha 轨迹**：`87470aaff5593330` → `85893817760a3be5` → **`3fa0e4ba4b1b9679`（保留为定稿，未回退）**；`scripts_sha 186edbd9c024` → **`780adce4017e`**。
- **影响范围 = 只有 `--chaos` 路径**：`dismiss_interference()` 的两个调用点分别在 `gym_run.py:2035` 的 `if self.expect_chaos:` 与等判定循环的 `if a.chaos:` 之下，`shot_window()` 的另外两个调用点也在它内部 ⇒ **非 chaos 批逐字未变** ⇒ 批次 4/5/6/9/11 的鼠标成绩与可比性不受影响，**不需要回归批**。

### 25.3 两批与结果

- **干跑**（`--tasks 2`、鼠标通道、`--chaos 1.0 --chaos-kind popup`）：**2/2**、`5252 ms / 题`、`popup_seen 2 / dismissed 2`、`clicks 6`、`scripts_sha 780adce4017e` ⇒ 与批次 14 的干跑（`2/2`、`5349 ms`、`seen 2 / dismissed 2`、`clicks 6`）**逐项同构**：补丁重落得对、拆耦合没有改变干净路径的行为。
- **正式批**（`--scenario t_trap2 --tasks 16 --seed 20251007 --chaos 0.70 --chaos-ms 200,700 --chaos-kind popup --max-repeat 3`，`t_trap2-w17-popup70-mouse.json`，跑完**立刻**打分）：**16/16 `OK`、退出码 0、无早停**；`popup_seen 14 / popup_dismissed 14`（`popup_dismiss_failed` 键不存在 = 0）、`interferences 14`、`clicks 40`、`shots 98`、`ocr 195`、`ms_ocr 33648.3`、`replans 12`；`score.py` = `v2 16/16 100.0% decided 100%`、`answered_right=16`、`false_refusal 0/16`、`swapped 15 / a_hit 10 / a_hit_but_failed 0`、`guard P50 125 / P95 168 ms`、`foreground after … unchanged: True`；app 侧 `chaos_planned 14 / chaos 14`、**无 `blocked` 事件**。逐题耗时合计 ≈ **72 s**（16 × 4476 ms 均值）。
- **为什么用 0.70 而不是 §24.2 里写的 0.35**：0.35 档在 16 题窄批里的期望弹窗数按批次 14 的 `11 / 60 题` 换算 ≈ **3 `< 5`** ⇒ **判据本身的 `popup_seen ≥ 5` 在"窄批 + 0.35"这个组合下不可达**；0.70 是更严的档（弹窗更多 ⇒ 漏点机会更多）。⚠ 代价：与批次 14 的 `@0.35` **强度与长度都不同**，本批**不能**读成"把那 1/11 修好了"。

### 25.4 判据、结论与边界

- **判据（`../sol/sandbox/SCORE.md:1178` / `STATE.md` §7 #20 行）**："鼠标通道的 `popup` 批跑满题数且 `popup_dismissed == popup_seen ≥ 5`" ⇒ **三条全过**（16/16 跑满不早停；`seen 14 ≥ 5`；`dismissed == seen == 14`）⇒ **按判据栏第一个分支还清**，§7 #20 行从"根因已定案 / 判据未达标"改为**已还清**。
- **三条交叉验证**：① `interferences == popup_seen == 14` ⇒ 每次发现**只点了一下**（没有补点、没有重试）；② app 侧 `chaos 14` 与驱动侧 `popup_seen 14` **一一对应**；③ app 侧**没有 `blocked` 事件**（批次 13-B 是 `blocked 10`）⇒ **没有一题被弹窗卡住**。
- **本批能证明**：补丁重落后这条通道**能跑满 16 题不早停**、判据达成、清障计数闭合，且这次改动**没有引入回归**。**不能证明**：① **拆耦合本身有效** —— (a)/(c) **一次都没被触发**（`interferences == popup_seen` 可证），它们是**未被检验的保险**，本批对它**零信息量**；② 漏点已被消除 —— 批次 14 的 `1/11` **未复现**，但 14 次样本区分不了"率降了"与"运气好" ⇒ **记为【未决】**；③ `--bg` 鼠标通道可用（盲区 #21，整条不生效）。
- **口径改正（第十七段回填）**：本段原稿与本段同期的三处文档曾写"本批证明**补丁充分**"—— 那是**过度声明**：拆耦合一次都没被触发 ⇒ 本批对它**零信息量**，能说的只有"**没有引入回归**"（16 题全部正常，且改动只落在 `--chaos` 路径 ⇒ 非 chaos 批逐字未变）。**能证明**与**未受检验**必须分开写，账才清楚。已同步：`REPORT.md` §5.2 ④、`../sol/sandbox/SCORE.md` 16.5-3 + 新增 **16.6**、本文接续点 ⑤。
- **【未决】漏点是否消除 —— 唯一入口 = 3 批 / 48 题**：单批 16 题在统计上区分不了"率降了"与"运气好"（量化见 `REPORT.md` 附录 B-7），所以这一项**不因本批而关闭**；将来要判定它，**只能**再跑 3 批（每批 16 题）共 48 题 —— 这是唯一路径，写进 `HANDOFF.md` §4，**本段不跑**。
- **A 的前台占用：原估计没有被高估，被高估的是"单批 60 题"这个前提**：本批实测 **4476 ms / 题**、16 题墙钟 ≈ **72 s**；`foreground after … unchanged: True` 只说明"**跑完时前台仍归 gym 窗口（没被抢走）**"，**不等于"没占用"** —— 跑批期间 gym 窗口**就是**前台。§23.5「代价是 3 分钟」与 §24.2 A 行风险③「占用前台约 5–8 分钟」都是**按 60 题批**给的；用本批实测换算，**60 题 ≈ 4.5 分钟、落在原估计区间内** ⇒ 原估计**成立**（把"3–5 分钟"当成一次窄批的代价来读，是**比较基准错位**，不是数字错）；真正值得记住的是**窄批（16 题 ≈ 72 s）才是拿真凭据的省法**。
- **#20 的封存口径（三件事一起读）**：① **封存结论** = "**通道可用 + 未引入回归 + 跑满不早停（窄批口径）**"；② "**漏点是否消除**" = **【未决】**（见上一条）；③ 后续可选动作 **(i) 什么都不动** / **(iii) 走出练习场**，二者**无依赖**（指向写进 `HANDOFF.md` §4）。
- **驱动改动保留为定稿**（与批次 9/10/11 的处理一致：判据过的改动不回退），因此**本批的 `scripts_sha` 是新的**（`780adce4017e`）、引用时必须写清通道与版本。
- 逐条边界另见 `../sol/sandbox/SCORE.md` 批次 16 节 **16.5**。

### 25.5 要点（可复用）

- **"接受边界"和"把边界做成可测的窄批"不矛盾**：第十五段选 C 之后，剩下唯一有信息量的动作就是**按判据本身设计一次最小批**（12–16 题），而不是把 60 题的失败批重跑一遍。
- **判据里隐含的强度约束要算**：判据要求 `seen ≥ 5`，而 0.35 档在 16 题里给不出 5 个弹窗 ⇒ **不改档位就等于选了一个判据不可达的组合**；把这一点写进文档，读者才知道"为什么不是照着 §24.2 的 0.35 跑"。
- **保险也要标成"未受检验"**：拆耦合是为"漏点"买的保险，本批一次都没触发它 —— 证据只能支持"通道可用"，不能支持"保险有效"；把两者分开写，账才清楚。
- **贴线的闸要主动说**：净 +30 与硬闸阈值相等，虽按"`> 30` 才停手"的口径未触发，也必须明写，避免读者自己去算。

## 26. 第十八段（2026-10-05）：18a 封账 —— 技能注入复验「通」+「补丁充分」改证清单封存

**这一段只做三件事：给凭证、确认归属、复验固定前置。三件套一字未动、不跑任何批次、不裂 sha。**

1. **「补丁充分」改证清单（第十七段的签收凭证）**：v0.7 基线（提交 `e760d2a`）里该表述共 **3 处、全部是"声称"** —— `REPORT.md:247`（§5.2 ④ 边界①）+ `STATE.md:13`（接续点 ⑤）+ `../sol/sandbox/SCORE.md:1451`（16.5-3）；改后（`6a29a61`）**声称性出现 = 0 处**（`REPORT.md` 内 `grep -c "补丁充分"` = **0**）。另有 **3 处"撤回引用"**（`HANDOFF.md:186` / `../sol/sandbox/SCORE.md:1458` / 本文 §25.4），三处都紧邻"**过度声明**／原稿曾写"这类限定词 —— 它们**记账、不构成声称**。同义英文（`sufficien*` / `suffices` / `adequate`）在基线里同为 **0 处**（基线与现行的逐处行号由本段交付的清单给出）。
2. **CHANGELOG 归属 = 已确认**：批次 16 / v0.7 的条目**留在 `6a29a61`** —— 它与第十七段同源（对第十五～十六段条目的措辞回填），不是新事件，不另立提交。
3. **技能注入（第十五段起的固定前置）复验 = 通**：本会话 `skill(name="gui-audit-gym")` **当场解析出全文**（`D:\DSH\skills\gui-audit-gym\SKILL.md`、**110 行**；frontmatter 含 `disable-model-invocation: false`）⇒ **无需会话层重载**，故障排查路径 ①②③ 不适用（本会话开场那次的同一调用也成功）。
4. **⚠ 待修（本段只记账、不改技能正文）**：技能正文**落后于 v0.7** 三处 —— ① 它写「已知盲区 **17 条**」⇒ 实际 `HANDOFF.md` §4 = **23 条**（编号 1–23 已逐条核）；② 它写「`popup` 类**当前测不了 ⇒ 该类的数字任何情况下都不引用**」⇒ 已被键通道两档（批次 12/13）+ 鼠标通道窄批（批次 16）取代，现行口径 = 「键通道两档可测；鼠标通道窄批可测；`--bg` 鼠标与滚轮/拖拽仍不可测」；③ 它写 `gym_run.py` **3465 行** ⇒ 实际 **3687 行**。技能正文属**操作规程**，改动**另立一段**（不与"封账"的范围混在一起）。
5. **18b（3 批 × 16 题排漏点 · 前台）未启**：按 18a 判据封账即止；要证「漏点是否消除」仍只走唯一入口（`HANDOFF.md` §4：**3 批 48 题**）。启用前提 = **用户明确要那个数字并接受前台占用**（3 批 ≈ 3.6 分钟前台 + 打分与文档同步）。

## 27. 第十九段（2026-10-05）：19a 技能正文对齐 + 19b 拆耦合实战（3 批 × 16 题前台窄批）

**19a 只改技能正文三处事实/规则（改 5 行、仍 110 行，sha `823a33e02889c3c0 → 88f62d610d87af0b`）；19b 不改任何代码（`gym_run.py` 仍 `3fa0e4ba4b1b9679`、`scripts_sha 780adce4017e`），只跑批。**

### 27.1 19a：技能正文落后 v0.7 的三处（本段修正）
- 「已知盲区 **17 条**」→ **23 条**（`HANDOFF.md` §4 编号 1–23 已逐条核）；表格里 `gym_run.py` **3465 行** → **3687 行**（`gym_app.py` 1493 行属实、未改）。
- 旧规则「`popup` 类**当前测不了** ⇒ 该类的数字**任何情况下都不引用**」→「**部分可测（旧规则已作废）**：键通道两档（批次 12 `0.35` / 批次 13 `0.70`）+ 鼠标通道窄批（批次 16）都有合法成绩可引用；仍不可测 = `--bg` 鼠标通道（盲区 21）与滚轮/拖拽（#18）；引窄批须带三条边界，指向 `HANDOFF.md` §2 规则 9 与 `../sol/sandbox/SCORE.md` 16.5/16.6」。
- **同类待核（本段按"只改这三处"的范围留着）**：技能描述里写「**七条**引用规则」，而 `HANDOFF.md` §2 实际有 **9 条**（1–9 已核齐）—— 不改会让新会话漏掉规则 8（partial 批不并列）与规则 9（批次 16 三条边界）。**要不要补由用户定。**

### 27.2 19b：为什么必须跑，以及跑之前把判别式写死
- 第十六段留下了唯一没被检验的东西：那条"漏一次点 ⇒ 整题死锁"的拆耦合**一次都没被触发** ⇒ 它是**未被检验的保险**。用户点出的关键：**复现漏点 ≠ 补丁被检验** —— 只有"漏点 → 补点触发 → 题被救回"这一串同时发生，才算补丁被检验。
- 判别式（跑之前写死，全用现有计数器）：**补点触发 ⇔ `interferences > popup_seen`**；**同一弹窗跨调用重试/存活 ⇔ `popup_seen > app 侧 chaos 数` 或 `popup_dismiss_failed > 0`**；**救回 ⇔ 该题 `OK` + 批不早停 + app 侧无 `blocked`**。**反过来：除非弹窗直接消失，否则 (ii) 情形在计数器上不可观测** ⇒ 它与"干净单发命中"逐字段相同，不能据此声称补丁被检验。

### 27.3 结果（三批 = 48 题；批次 17/18/19，seed 20251008/09/10，`popup@0.70`，前台真实鼠标）
- **批次 18：那条保险被触发了一次并救回** —— `popup_seen 8` / `interferences **9**` ⇒ 恰有一次遭遇点了两发（第一发没打掉、重取帧后再点）、该遭遇最终被清掉（`failed 0`）、该批 **16/16**、无 `blocked`、无早停 ⇒ **(i) 情形成立**。
- 批次 17：`seen 10 / interferences 10`（补点 0）、16/16、退出码 0；**1 次 app 侧 `blocked`**（task 12，`swap_timer`，该题最终 `ok`）。批次 19：`seen 10 / interferences 10`（补点 0）、**15/16、退出码 1** —— 那一题是**已知的 `swap_timer` 时序竞争类**（`race 1/1`、`wrong_target 1`），**不是弹窗通道问题、也非早停**（`partial False`、`exit_reason None`）。
- 合计：遭遇 **28**、清障点击 **29**、**补点 1**、`popup_dismiss_failed` **0**、app 侧 `chaos` **28** 与驱动侧 `popup_seen` 逐批 1:1、题级 **47/48**。
- **上限口径**：死锁率 **0/28 遭遇** ⇒ rule of three 95% 单侧上限 ≈ **10.7%**；第一发失手率 **1/28 = 3.6%**（与批次 14 的 `1/11 ≈ 9%` 同量级）⇒ **"漏点是否消除" 仍 =【未决】**，不能宣告消除。

### 27.4 边界与坑（引用时必须一起带走）
- **只覆盖前台真实鼠标通道**；`--bg` 鼠标通道（盲区 21）与滚轮/拖拽（#18）**未覆盖**、结论不变。
- **三批 seed 各异**，是同协议的三次重复，**不能**与 60 题键通道批并列成"覆盖面等同"。
- **跑之前先核"靶窗口计数 = 1"**：驱动按 UIA `name` **子串**匹配 "GUI Gym"，本机 DSH 会话窗口标题里就含这四个字符 ⇒ 会数成 2 个靶而拒启动（退出码 2；`gym_run.py:3135–3150` / `:3364–3370`）；处置 = 临时改名该窗口（原名存 `D:\DSH\dsh-actor\tmp\w18_harness_title.txt`）并**跑完还原**（本次已还原）。被拒的那次还会**留下残留靶窗口**（只 kill 启动器），下一批跑前要确认没有。
- **逐题定位不可用**：run json 的逐题行在 `j['runs']`（不是 `j['rows']`）、行内 `interferences` 三批全 0（既有 `_redo()` 记账特性）⇒ 只能给批级"补点 1 次"。

### 27.5 要点（可复用）
- **"保险"要专门设计一次能触发它的批**：第十六段把"通道可用"与"保险有效"分开写了，这一段才把后者补上 —— 判据不是清障率，而是"补点有没有被触发、触发后有没有救回"。
- **判据要能用既有计数器表达**：这次沿用 `interferences > popup_seen` 就够，不需要为了判据改一行代码（也就没有裂 sha）。
- **环境前置条件也要记账**："窗口标题撞名（子串匹配）"这种坑只会在"自己就是干扰源"的机器上出现 —— 写进 `HANDOFF.md` §3 才不会再踩。

## 28. 第二十段（2026-10-05）：技能正文全量对齐 + **#20 收口**（纯文档：不跑批、不改 `.py`、不裂 sha）

### 28.1 任务 1：技能全量扫（**可变事实 20 条 + 绝对措辞 11 句**，逐条对源）

**源** = `HANDOFF.md` §2/§3/§4 + 本文件现行节 + `../sol/sandbox/SCORE.md`。**已核一致 = 16 条（可变事实）**：`gym_app.py` **1494** 行 ✓ / `gym_run.py` **3724** 行 ✓（**阶段 3.4 复核**：前者因 `viewport` 声明 +1；后者 3687 → **3724** 的两步是第二十六段 #21 修复 +9 与阶段 3.1 参数化 +28 —— 本行两个数在第二十段那次核之后已各漂过一次，凡引用以当次 sha 为准）；`gym_app.py` CLI **11 个开关逐字一致** ✓；`gym_run.py` CLI **17 个开关逐字一致** ✓；"`gym_app.py` 只依赖 stdlib + tkinter" ✓（import 实测）；`score.py --selftest` ✓；判定集合 = `score.py:110-112` ✓；`join_truth` = `score.py:162-169` ✓；本文件 §0 用户铁律 / §7 欠账 / §11 WSL 决策 = `:102/:285/:526` ✓；`HANDOFF.md` §4 已知盲区 **23 条** ✓；§4 #12（前台被抢 ⇒ 该批作废）✓；#15（`a_hit` 是读出量）✓；#16（chaos 探索性、引 app 侧事件）✓；v0/v1/v2/v3 四版定义与批次归属 ✓；引用规则 **1–7** 逐条 ✓；"不适用"引的两支（全局技能 `drive-a-windows-gui`、`univer/office`）✓。
**绝对措辞 11 句**逐句对源：解释器（`:32`）、通道不可比（`:58`）、事件错联（`:64`）、主指标与读题率（`:77`）、synonym 鼠标不引用（`:82`）、`_code`/`_plain`（`:84`）、chaos 计数（`:86`）、v0 不可比（`:91`）、批次 1–4 全是 v1（`:92`）、**popup 边界（`:99`，随本段 #20 收口同步改写）**、chaos 探索性（`:102`）—— 除 `:99` 外**全部已核一致、无未核过的绝对措辞**。

**改前 / 改后（4 处；技能 110 → 112 行，sha `88f62d610d87af0b → 8d3182cbfc514df4`）**

| # | 位置 | 改前 | 改后 | 类型 |
|---|---|---|---|---|
| 1 | `:3` 描述 + `:79` §3.2 | 「**七条**引用规则」；规则只写到 **7** | 「**九条**」（逐条对齐）+ 补齐**规则 8**（partial 批不与完整批并列）、**规则 9**（鼠标前台窄批**四条边界**） | 计数陈旧（**已知必修**） |
| 2 | `:56` 跑批参数 | `--chaos-kind ∈ {rebuild, move, slow, popup}` | 实际 choices = `{any, rebuild, move, popup, slow}`（`any` 为默认） | **新偏差**（集合不全） |
| 3 | `:57` 延迟档 | 「`--chaos-ms 200,700`（**默认**）」 | **真实默认 = `600,1800`**（`gym_app.py:1455`；驱动侧默认 `None` ⇒ 不转发、走 app 默认）；**`200,700` 是 chaos 批刻意选的短延迟** | **新偏差**（写成默认 = 错） |
| 4 | `:34` §1.3 铁律 3 | 「同一时刻只能有 1 个 gym 窗口…不要在 GUI 里开第二个 gym」 | 计数按 UIA 窗口 name 的**子串** `"GUI Gym"`（`gym_run.py:3135-3150` / `:3364-3370`）⇒ **标题含这四个字的别的窗口也会被算进去**；实测撞过（`refusing to drive: 2 practice target window(s)…`、退出码 2）⇒ 临时改名 + **跑完还原**，被拒那次还会**留残留靶窗口** | **新偏差**（缺口） |

⇒ **新偏差 3 处，未超"发现 >3 处即停"的阈值**（阈值是 `>3`）⇒ 三处当场改完、未触发停止。**复查第十九段那三处**：盲区 **17→23** ✓ 稳；`gym_run.py` **3465→3687** ✓ 稳（`wc -l` 实测）；`popup` 旧规则 ✓ 稳，并按本段收口再改一次（`:99`：三条边界 → **四条**，并加"批次 17–19 同样是合法证据"）。

### 28.2 任务 2：结构建议（**只记账，不改技能结构**）

技能"写完即冻结、源文档继续涨" ⇒ **计数/行数硬编码必然第三次漂移**（已两次：17→23、3465→3687；本段又撞 7→9、`--chaos-ms` 默认）。**记账句**：*本技能内的计数/行数为**硬编码**；源文档（`HANDOFF.md` / `STATE.md` / `../sol/sandbox/SCORE.md`）更新后**须同步**。结构性解法 = **指向"文件 + 节号"而非硬编码**，待评估。*

### 28.3 任务 3：**#20 收口（结项）** —— 四行定稿

1. **通道可用** ✓ —— 鼠标前台通道在第十六段（16 题）与第十九段（3 × 16 题）都跑满、不早停。
2. **保险单实例已验证** ✓ —— 那条拆耦合在**批次 18** 被真实触发一次并**救回**（`interferences 9 > popup_seen 8`、该遭遇被清掉、该批 16/16、无 `blocked`）。
3. **"漏点是否消除" =【未决】，且判定为"不追加"** —— 再加 3 批（48 题）只能把 95% 单侧上限从 **≈10.7%** 收窄到与观测失手率（1/28 ≈ 3.6%）**同一量级** ⇒ 仍**分不开**"已消除"与"还剩百分之几"，**边际收益 ≈ 0**。**"不追加"= 已决定不再投入，不是待办。**
4. **口径只写"路径可达 + 单次有效"** —— **不写**"保险有效 / 够用"（会被读成"多次验证"）。

⇒ **#20 从"活动欠账"移入"已结项"**；**唯一入口**（若将来真要证消除）= **再跑 3 批 48 题**，**本段不跑、非当前计划**。数值与逐条边界见 `../sol/sandbox/SCORE.md` 批次 17–19 节。

### 28.4 落点、约束与下一件

- **落点**：本文件**接续点（行内追加）+ §7 #20 行（行内补记）+ 本节 §28**；`HANDOFF.md` §2 **规则 9 重写**（三条边界 → **四条**）+ §4 盲区 23 末尾**收口块**（含下一件指向）+ §6 末行（报告 **v0.9**）；`REPORT.md` 版本行 **v0.9** + §7.3 第 1 项 + 第 8 章 + §5.2 ④ / §6.2 D 的行内收口括注 + **附录 A 第六次重算**；`../CHANGELOG.md` 新增条目；技能正文 4 处。
- **约束遵守**：**未跑任何批次、未改任何 `.py`**；三件套 sha 逐位未变（`gym_app.py 66632d85eac81c12` / `gym_run.py 3fa0e4ba4b1b9679` / `score.py ef066713a03eb940`）；`REPORT.md` **不复制数字**（只写过程计数与指针）。
- **下一件**：**(i) 什么都不动**（口径已自洽、#20 已结项）或 **(iii) 走出练习场**（练习场外的东西拉进来测）—— 二者无依赖。


---

## 29. 第二十二段（2026-10-05）：#19 **关死** + #18 实现前核查（跑一批、**不改任何 `.py`**）

### 29.0 一句话

#19 在**弹窗维度**四格齐（`0.35`/`0.70` × 键/鼠标）⇒ **关死**（第四格 = 批次 20，带一条显式保留：该批 21/24 早停、归因非弹窗）；同时把 #18（滚轮 + 拖拽）的**实现前核查**做完 —— actor 本来就支持 `drag`/`scroll`、驱动两条路径都在 ⇒ **方案①零代码改动**（结论写进 `DESIGN-18-scroll-drag.md` §8）。

### 29.1 任务 1：1a 依赖更正 → 1b 跑批 → 1c 关死

- **1a**：依赖描述更正。**用户引用的那句「若 #20 选 C 则随它收口」在文档里没有逐字原文**（`grep` 0 命中）；实际过时落点 = `../sol/sandbox/SCORE.md` §13.4 第 3 条「剩余部分与 #20 合并处理」+ §7 #19 判据栏「鼠标通道待 §16 的鼠标 op 修好后再量」⇒ 判据改成「**两条通道各有一档达标**」，新增 **§19.7 四格表**，`HANDOFF.md` §4 盲区 17 内加 ⚠ 块。
- **1b**：**批次 20** = `../sol/sandbox/t_trap2-w22-popup35-mouse.json`（`popup@0.35` × 前台真鼠标、`t_trap2`、seed 20251007、24 题、`--max-repeat 3`、`scripts_sha 780adce4017e`）。**弹窗侧全达标**：fire **10**、`popup_seen/dismissed 10/10`、`failed` 0、**补点 1 次**、`task_i 17` 被 modal 挡住 2.18 s 后恢复且该题 `ok`；**批未跑满**：21/24、退出码 1（`task_i 21` 的 `must_refuse`/`prose_only` 题**没走拒答、反而按了标签** ⇒ `false_accept 1/1`）—— 归因见 §7 **#21**，**与 `popup` 无关**（该题事件序列只有 `ready`；同 seed 键通道批次 12 的同一题 `refused: true`）。数值与边界全在 `../sol/sandbox/SCORE.md` 批次 20 节。
- **1c**：§19.7 第 4 格填上 + 判据改写成「**每格 ≥5 fire 且清障成对**」（「跑满不早停」只对键通道两格成立）+ §7 #19 行改 **✅ 已关死**；`HANDOFF.md` §4/§5/§6 与 `REPORT.md` 相应处同步。

### 29.2 新欠账 #21（第二十二段新增，未冻结）

鼠标通道下 `must_refuse`（`prose_only`）题**不走拒答、反而按标签** ⇒ `score.py` 记 `false_accept`、题不前进 ⇒ `--max-repeat` 早停。证据、判据与出处见 §7 #21 行。

**第二十三段已判定**：性质 = **通道级缺口**（按判定依据分层，不是单题偶发），机制定位到 `gym_run.py:2164-2168` 缺可操作性判据 ⇒ 见 **§30**。

### 29.3 任务 2：#18 实现前核查（**只读**，结论写进 `DESIGN-18-scroll-drag.md` §8）

- **actor 能力（不用改）**：模块 docstring 的 `Ops:` 行里 **`drag` 与 `scroll` 都是一等 op**（`@op('drag')`/`@op('scroll')`）；`Hands.drag(..., steps=30, ms=240)`（SendInput）、`post_drag(...)`（bg 版，「a drag needs no foreground」）、`o_drag` ⇒ **不重蹈 #20 的 B 案否决理由**（读数仍落在 `scripts_sha` 之内）。
- **驱动侧路径都在**：`gym_run.py:1235-1239 Driver.drag`（`stats["drags"]`）、`:1241-1252 Driver.wheel`（`stats["scrolls"]`）；调用点 = 滚轮 `:2356`（t_rows 处理器）、拖拽 `:2900-2904`（t_chips 处理器）。
- **滚轮**：键通道**等价物已存在且已实现** —— `:2349-2353` 注释（「the wheel is a mouse message and Tk ignores those while it is not focused (measured: 63 posted wheel steps moved nothing at all)」）→ `self.key("Next")`；app 侧 `gym_app.py:717-729 keymap["Next"]/["Prior"]`（= Page Down/Page Up → `_page(±1)`，另有 `Up`/`End`）。
- **拖拽**：键通道**无等价物**（`gym_app.py:949-962` 的 `t_chips` 只绑 `<ButtonPress-1>` / `<B1-Motion>` / `<ButtonRelease-1>`）⇒ 只能前台鼠标；「造键盘版拖拽」要改**靶子**（裂 `gym_app.py` 的 sha + 语义不等价）⇒ **不做**。
- **方案与推荐**：**①前台鼠标批**（`--scenario t_rows` / `--scenario t_chips`，**零代码改动**，一次覆盖滚轮 + 拖拽）；②键通道等价物只对**滚轮**成立（第十一段探针已跑过：rows 8/8、24 题 22/24、chips 8/8）⇒ **推荐 ①**，② 当滚轮的轻量补测。**边界**：`t_rows`/`t_chips` 题**不声明 `truth_class`**（`gym_app.py:726`/`:962`）⇒ 只能按**题级 + `scrolls`/`drags` 计数 + 屏幕读题率**量，**不是五判定**；`--bg` 鼠标通道仍不可用（盲区 21）。

### 29.4 约束与下一件

- **未改任何 `.py`**（任务 2 只读；#19 不需要改代码）⇒ 三件套 sha 逐位未变（`gym_app.py 66632d85eac81c12` / `gym_run.py 3fa0e4ba4b1b9679` / `score.py ef066713a03eb940`）；`REPORT.md` 不复制数字、只指 `../sol/sandbox/SCORE.md`。
- **下一件（二选一，无依赖）**：**(A)** 把 #18 按方案①排一次前台窄批（`t_rows` + `t_chips`，零改动）—— #18 从「欠（有据）」走向「有真凭据」的唯一路径；**(B)** 修 #21（鼠标通道拒答路径）—— 让前台批遇到 `must_refuse` 题时不再早停（**需改 `gym_run.py`、裂一次 sha**）。

## 30. 第二十三段（2026-10-05）：#21 **性质判定**（只读 + 跨批普查，**未跑新批、未改任何 `.py`**）+ #18 进成绩体系**设计**

### 30.0 一句话

#21 **已判定**：性质 = **通道级缺口**（不是单题偶发）—— 鼠标通道缺 `gym_run.py:2160 if self.keys:` 的**鼠标孪生判据**，于是「徽章判定」族的 `must_refuse` 题会被点在 prose 坐标上 ⇒ 题不前进、`false_accept`；已观测 **2 批 100% 复现**（批次 14 + 批次 20，同一 `task_i 21`），**反证** = 可见性判定族在鼠标通道 60+ 行全对 ⇒ 标**高优先级**。#18 进成绩体系的设计写进 `DESIGN-18-scroll-drag.md` **§9**；结论 = **`score.py` 必改**（最小改动：认识新类名 `viewport` 并单列，**不进主分母**），否则要么污染主分母、要么被算成 `undeclared`。

### 30.1 任务 1：1a 定性（读码）→ 1b **有意不跑** → 1c 落文

- **1a（代码行级，落到行）**：`gym_run.py:2158` 的 `if hit:` 之后**一分为二** —— `:2160 if self.keys:`（键）与 `:2164 elif self.control_visible(...)`（鼠标）。键分支用 `press_hint`（`[k]` 徽章 = 可操作性）判定「这不是控件」⇒ `:2163 no_key_refuse(rec)` ⇒ `refuse("the control carries no action key")`；**鼠标分支只问「画出来没有」**，于是把 `click()` 打在 prose 坐标上。**这一条行就是原因**：`:2164-2168` 没有可操作性判据（孪生缺失），而 `:2210`「no control carries the asked label」位于 `else:`（`hit` 为假 = 标签全屏找不到）分支，prose 题进不去。
- **1b（条件不成立 ⇒ 有意不跑，本段唯一偏离任务书处）**：任务书 1b 的触发条件是「1a 不能定性或需确认普遍性」。1a 已定性到行；普遍性用**既有批次**就能判：**2 批鼠标 `t_trap2` 全失败**（且都停在同一个族的第一道题）、**6 批鼠标 `t_trap3` 60+ 行全对**、键通道 12 批几乎全对。再跑一批：因为**批一到该族就早停**，至多再加**同一道题**的一条同类数据点，却要占前台 ≈3 分钟 + 一份新 json ⇒ 判定为**不需要**。
- **1c**：§7 #21 行改写为「**已判定（性质 = 通道级缺口，高优先级；未修）**」+ §29.2 加指针 + 本节。

### 30.2 跨批普查（1a 证据，全部来自既有文件，未跑新批）

| 通道 | 判定依据族 | 批次 | `must_refuse` 行 | 结果 |
|---|---|---|---|---|
| 键 + `--bg` | 徽章判定（`t_trap2`：`prose_only`/`disabled`/`two_close_names`…） | 12 批（`t_trap2-1/-2/-3`、`w6-control`、`w7-control`、`w7-move70`、`w8-move35/70`、`w8-slow35/70`、`w9-move70`、`w12-popup35`、`w13-popup70`…） | 14–28 / 批 | **几乎全 `refused/ok`**（仅 `w6b-chaos35`、`w8-slow70` 各 1 行 `acted/ok`） |
| 鼠标（前台真鼠标） | 可见性判定（`t_trap3`：`nb020/nb030/nb035/nb044`） | 6 批（`t_trap3-1/-2/-3/-4`、`t_trap3-smoke`、`t_trap3-smoke2`、`_dbg-class4.json`） | 14/14/14/14/13/3/3 | **全部 `refused/ok`** |
| 鼠标（前台真鼠标） | **徽章判定**（`t_trap2`） | **2 批**（批次 14 `t_trap2-w13-popup35-mouse-fix.json`、批次 20 `t_trap2-w22-popup35-mouse.json`） | 3 + 3（= 同一道题各 3 次尝试） | **全部 `acted/none`** ⇒ 早停 |

归因方法：`ready` 事件的 `truth_class` 优先、逐题行 `detail.truth_class` 兜底（旧批 events 已被后续批覆盖，见 `HANDOFF.md` §2 规则 7）。

### 30.3 任务 2：#18 进成绩体系的设计（**只设计不实施**）

- **落点**：`DESIGN-18-scroll-drag.md` **§9**（9.1 现状 / 9.2 设计 / 9.3 风险与回退 / 9.4 边界）。
- **要点**：新增真值类 **`viewport`**（`t_rows`/`t_chips` 共用）⇒ 靶子侧**两处一行改动**（`gym_app.py:726`、`:962-964` 的 `truth` 里加 `truth_class`）+ **`score.py` 必改（最小）**：认识新类名、**单列一行**、**不进** `pass_rate` 与两个假阳/假阴分母；历史可比性靠「不进主分母」保住（批次 1–20 的主线不受影响）；回退 = **单文件 revert**（改动只在两个 `return` 的字典里加键，无状态）。
- **两问答案**：**`score.py` 要不要改？→ 要**（不改的话新类只会被算成 `undeclared`，进不了体系；除非改用 `answerable`，但那会把这两类题灌进主分母、破坏与批次 1–20 的可比性）。**历史可比性怎么处理？→ 新类不进主分母 + 报告另开一节**（明写「批次 1–20 与之后不可直接比」只发生在「混池批」的 `rows_total`/`undeclared` 口径上，主线通过率不受影响）。

### 30.4 约束与下一件

- **未改任何 `.py`**（任务 2 只读设计；#21 不需要改代码来判定）⇒ 三件套 sha 逐位未变（`gym_app.py 66632d85eac81c12` / `gym_run.py 3fa0e4ba4b1b9679` / `score.py ef066713a03eb940`）；本段**未跑批**（无新 json）。
- **下一件（两件，无依赖）**：**(A)** 按 `DESIGN-18-scroll-drag.md` §9 真改 `gym_app.py`（**首次裂 sha**）→ 跑一次 `t_rows` + `t_chips` 前台窄批，把 #18 从「欠（有据）」推到「有真凭据」；**(B)** 修 #21（给 `gym_run.py:2164-2168` 的鼠标分支加可操作性判据 = 键通道徽章判据的孪生；要裂 `gym_run.py` 的 sha）。

## 31. 第二十四段（2026-10-05）：#21 重跑清单 + 修复设计（纯文档：不跑批、不改 `.py`、不裂 sha）

**31.0 一句话**：#21 的**必重跑**只有两批（批次 14、批次 20）；产生 #20 结论的四批（16–19）**该族题数 = 0** ⇒ **#20 结论不受影响**；
修复设计两条路线，推荐**路线②**（"点了没反应 ⇒ 走拒答"，**+9 净行**（含驱动侧计数键 `stats["refuse_by_stall"]`）、不改靶子），全文见 `DESIGN-21-mouse-operability.md`。

**31.1 1a 普查：哪些批次含"靠 `[k]` 徽章判可操作性"的 `must_refuse` 题**
（方法 = 全库 run json 逐题行 + 同名 `-events.jsonl` 的 `ready.truth_class` 联结；靶子侧 5 类里有 4 类 `variant` 为空串 ⇒ 位置靠 plan 题序 + 各批 `--tasks` 值判）

| 批（文件） | 通道 | 题窗 | 该族 `must_refuse` 行 | 该行判定 | 早停 |
|---|---|---|---|---|---|
| 批次 14 `t_trap2-w13-popup35-mouse-fix.json` | 鼠标前台 | plan 60 / 实跑 24 行（21 题） | **3 行 `prose_only`** | `acted` / `none` | **是**（`task_i 21`） |
| 批次 20 `t_trap2-w22-popup35-mouse.json` | 鼠标前台 | plan 24 / 实跑 24 行（21 题） | **3 行 `prose_only`** | `acted` / `none` | **是**（`task_i 21`） |
| 批次 16 `t_trap2-w17-popup70-mouse.json` | 鼠标前台 | plan 16 | **0** | — | 否（16/16） |
| 批次 17/18/19 `t_trap2-w18-popup70-mouse-r{1,2,3}.json` | 鼠标前台 | plan 16 各 | **0** | — | 否（16/16 各） |
| `t_trap3-1/-2/-3/-4/-smoke/-smoke2`（6 批） | 鼠标前台 | plan 48 | 0（该 5 类**按设计排除**，见 `gym_app.py:107-121`）；此处的 `must_refuse` 行全是 `no_badge_fill`（**可见性**判定） | `refused` / `ok` ✓ | 否 |
| `_dbg-class4.json` | 鼠标前台 | 4 | 0（同上：`no_badge_fill` 3 行） | `refused` / `ok` ✓ | 否 |
| 键通道 12 批（`t_trap2-w12/w13/w6*/w7*/w8*/w9*`） | `--keys --bg` | 14–28 行/批 | 有（`prose_only` 等） | `refused` / `ok`（`refuse_why = "the control carries no action key"`） | 否 |

- 全库其余鼠标批（`fill_curve*` / `gym-*` / `chaos-*` / `t_trap7-*` 等）`must_refuse` = 0，或该族不在 plan 里 ⇒ 不列入。
- 另有 2 行 `acted/ok` 出现在 `w6b-chaos35` / `w8-slow70`（键通道 chaos 批）—— 早已记账的残余，**与 #21 无关**。

**31.2 1b/1c 三类 + 题数 / 前台成本 / 紧迫度**

- **【必重跑】2 批**（早停直接由 #21 造成）：
  - **批次 20**（24 题 / 实测 155.8 s ≈ **2.6 分钟**前台）—— 紧迫度 **中**：#19 第四格的证据批本身早停，重跑一次同时"验证修复 + 让该格跑满"。
  - **批次 14**（plan 60、实跑 24 行 / 157.2 s ≈ **2.6 分钟**）—— 紧迫度 **低**：它的 `popup` 结论已被批次 20 取代，重跑只为验证修复。
- **【须重评结论】空** —— 不存在"该族被错误处理但批未停"的批次（含该族的两批都停了；批次 16–19 该族题数 = 0）。
- **【不受影响】**：键通道全部（12 批，该族 `refused/ok`）；鼠标批次 16–19（16 题窗口止于 task 15，而第一个徽章判定题在 task 21）；
  `t_trap3` 6 批（该 5 类按设计排除）；`_dbg-class4` 与其余 `must_refuse` = 0 的鼠标批。

**31.3 #20 结论是否受影响 = 不受影响**（明确回答，三条理由）
① 产生 #20 结论的四批（16/17/18/19）**该族 `must_refuse` 题数 = 0**（16 题窗口 = `swap_after_press` ×10 + `swap_timer` ×5 + `prose_with_button` ×1，第一个徽章判定题在 task 21）；
② `score.py` 对这四批的 `false_accept` 分母本来就是 **0/0**；
③ #20 的结论内容是"通道可用 + 保险触发一次"，保险 = `dismiss_interference` 的补点（弹窗/清障路径），与 `click_label` 的可操作性判据无关。
唯一边界：四批里出现 1 道 `prose_with_button`（同类的 **answerable** 变体）在鼠标通道**通过**（1/1），不受 #21 影响。

**31.4 任务 2 摘要（设计全文 = `DESIGN-21-mouse-operability.md`）**
- **不能照搬键判据**：鼠标通道"没有徽章也能点"是**特性** —— `t_trap3` 里 `nb065`（D1 70.0）/ `nb100`（125.0）正是 `acted/ok`；
  加"必须有徽章"会一次翻掉每批 6 行、四个批 + smoke ≈ **27 行**已判对的行（`DESIGN-21` §2）。
- 路线①（像素：D1 兜底再加填充率统计，+15～22 行，需先标定）/ **路线②（行为：点了没反应 ⇒ 拒答，+7 净行，无需标定）⇒ 推荐 ②**。
- 路线②落点 = `gym_run.py:3507` 之后、`:3508`（第二次 `wait_verdict`）之前；四条守卫 = `not a.keys` / `not a.bg` / `act == "click_label"` 且无判定 / `d.task_i() == task_i`。
- 回退 = 单文件 `git revert`（或 `git checkout <旧 commit> -- ../sol/sandbox/gym_run.py`），`scripts_sha` 回到 `3fa0e4ba4b1b9679`。

**31.5 约束与下一件**
- **未跑任何批次、未改任何 `.py`** ⇒ 三件套 sha 逐位未变（`gym_app.py 66632d85eac81c12` / `gym_run.py 3fa0e4ba4b1b9679` / `score.py ef066713a03eb940`）；技能 sha `208366a01c45a2ae` 未动。
- **下一件 = B 开工**：按 `DESIGN-21` §4 改 `gym_run.py`（+9 行，**首次裂驱动 sha**）→ 跑验证批（判据见 `DESIGN-21` §6：跑到 ≥25 题不早停 + `task 21` 记 `refused_right` + 回归）；
  之后才是 A（#18：靶子侧两处一行 + `score.py` 新桶，见 `DESIGN-18-scroll-drag.md` §9）。

**31.6 第二十六段复跑结果（B 实施后，指针）**
- **批次 20 → 批次 21**（同 seed 20251007、同协议、只换 `--json-out`）：**24/24 不早停**；`task_i 21/22/23` = `refused/ok`；`false_accept 0/3`；`refuse_by_stall 3`。详见 `../sol/sandbox/SCORE.md` 批次 21 节。
- **批次 14 → 批次 22**（同参 60 题；**仅作回归验证** —— 其 `popup` 结论已弃、仍指 `../sol/sandbox/SCORE.md` 批次 16–19 节）：**60/60**；`refused_right 14`；`false_accept 0/14`、`false_refusal 0/46`；`refuse_by_stall 4`（= 4 道 `prose_only`，另 10 条 `disabled` 族走原有可见性路径）；回归 = **唯一翻转 `task_i 21`**。详见 `../sol/sandbox/SCORE.md` 批次 22 节。
- **§31.3 的三类归因结论未变**（必重跑 = 批次 14 / 批次 20；须重评 = 空；#20 不受影响），**两类都已在 §32 完成复跑**。

## 32. 第二十六段（2026-10-05）：B 实施 —— 修 #21（**裂 `gym_run.py` sha**）+ 两批前台复跑

**32.0 一句话**：鼠标分支现在有了键通道早就有的那条**行为判据** —— 「点了一次 `click_label`、没等到任何判定、且 app 仍停在这一题 ⇒ 说『没反应』并走拒答」；**净 +9 行**、`gym_run.py 3fa0e4ba4b1b9679 → d8594bff3738ca9b`（`scripts_sha 586171888d39`），**两批前台复跑全部跑满**（批次 21 = 24/24、批次 22 = 60/60），`false_accept` 归零、`false_refusal` **没有**上升。

**32.1 改动（逐项）**
- **落点**：`gym_run.py:3507` 之后（即 `rec = _redo(...)` 之后、第二次 `wait_verdict` 之前）；**+9 行** = 3 行注释 + 4 行守卫 + `d.refuse(...)` + 计数行。
- **四条守卫**（缺一不可）：① `not a.keys`（键通道同情形已由 `no_key_refuse` 正确拒答）② `not a.bg`（`--bg` 鼠标通道整条不生效 = 盲区 21）③ `rec.get("act") == "click_label"` **且** `v.get("result") in (None, "", "none")` ④ `d.task_i() == task_i`（发 F8 前确认 app 仍停在这一题）。
- **次序硬约束**：守卫 ③④ 的读取与 `d.refuse(...)` 之间**不插任何其它操作**（不抓帧、不 OCR、不重规划、不打印）—— 否则「仍停在这一题」的有效期被拉长，F8 会落到**下一题**。
- **动作与计数**：`d.refuse(rec, "clicking the asked label changed nothing")`（只写 `decision` / `refuse_why` / `stats["refusals"]` 并按键）+ `stats["refuse_by_stall"] += 1`（新键，随 json 落盘）。
- **前置核查（本轮实测，已补进 `DESIGN-21` §4）**：`rec` **不是**驱动持有的实时引用 —— `_redo()`（`:261`）内部 `again = d.do_task(...)` **新建**记录并返回 ⇒ 落点必须在 `_redo` **之后**；否则 `decision` / `refuse_why` 会写进**被丢弃的记录**（= 记账错位；同类事故见 `_redo` docstring `:265-271` 与批次 9 的 #10/#11）。
- **零改动核**：键通道（守卫①）、`--bg`（守卫②）、有判定题（守卫③的 `result` 条件）**逐项未动**；`no_badge_fill` 族走 `control_visible` 的可见性路径（`t_trap3` 60+ 行 `refused/ok` 与批次 22 的 10 条 `disabled` 族同型）⇒ 修复**不碰**那条路。

**32.2 批次 21（#21 修复主验证：`popup@0.35` × 前台鼠标、24 题、与批次 20 同 seed 同协议）**
- **24/24 不早停**（批次 20 = 21/24 早停）；`task_i 21/22/23` = `refused/ok`（`refuse_why "clicking the asked label changed nothing"`、`replanned 2`）；`false_accept 0/3`、`false_refusal 0/21`、`refuse_by_stall 3`。
- **回归**：`task_i 0–20` **21/21 判定逐题一致**；`replans` 两批同为 23 ⇒ 修复只改「最后那一下收尾」，**不改** stall 路径本身。

**32.3 批次 22（回归复跑：`popup@0.35` × 前台鼠标、60 题、与批次 14 同参）**
- **60/60**、`refused_right 14`、`false_accept 0/14`、`false_refusal 0/46`、`refuse_by_stall 4`。
- **14 条拒答的路径分布**：4 条 `prose_only`（`task_i 21–24`）= **新 stall 路径**；10 条 `disabled` 族（`task_i 35–44`）= **原有可见性路径**（「the control is painted below the visibility floor」）。
- **与批次 14 的逐题比**：旧批 24 行 / 22 个 `task_i`，**唯一翻转 = `task_i 21`**（`acted/none` → `refused/ok`）。⚠ 两批**不是同一版驱动**（批次 14 的 `scripts_sha 871ed27ca066`）⇒ 只作回归对照、**不作成绩**；**批次 22 的 `popup` 结论不引用**，仍指批次 16–19 节。

**32.4 `false_refusal` 上升的逐题可解释清单**
- 本段**两批都没有上升**（批次 21 `0/21`、批次 22 `0/46`）⇒ 清单为**空**（这正是判据「上升数 = 无判定 `answerable` 题数」的最简情形）。
- 若将来上升：逐题看该批**所有 `false_refusal` 行**的题号 + `refuse_by_stall`，确认每道都落在「本来就没有判定」的题上（`DESIGN-21` §6 判据 4 / §8 的 overclaim 抽查）。

**32.5 边界与下一件**
- **只覆盖前台真实鼠标通道**：`--bg` 鼠标通道（盲区 21）与滚轮/拖拽（#18）**不变**。
- **#21 的判据达成 = 「不再早停 + 该题 `refused_right`」**；「鼠标通道拒答率」**没有**被测（两批合计 `must_refuse` 17 题，其中走新路径 7 题）。
- **回退点**：`gym_run.py 3fa0e4ba4b1b9679`（单文件 `git checkout <旧 commit> -- ../sol/sandbox/gym_run.py`，或 `git revert`）；`scripts_sha` 随之回到 `3fa0e4ba4b1b9679`。
- **下一件 = 3.5（v1.0 声明 + 冻结条款 + 欠账分流）**；A（#18）已于**阶段 3.4** 落地 —— 见 §33，验证批与 `viewport` 桶的首次真取数在 3.5。

## 33. 阶段 3.4：`viewport` 进体系（A 已实施）+ manifest v1 只设计

**33.1 一句话** = `t_rows`（滚轮）与 `t_chips`（拖拽）两类题自本段起**声明真值类 `viewport`**，打分时单列成桶（**不进五判定、不进主分母**）；靶子**首次裂 sha**。本段**未跑批**（验证批在 3.5）。

**33.2 改了什么（逐条）**

- 靶子 `../sol/sandbox/gym_app.py`：`t_rows` / `t_chips` 两条 `finish(...)` 的 truth 字典各加两键（`truth_class` / `variant`），**判定逻辑一字未改**；1493 → **1494** 行。
- 打分器 `../sol/sandbox/score.py`：新增 `VIEWPORT` 常量与独立桶 `viewport_n` / `viewport_pass`；`undeclared` 改为 `len(runs) - n - len(viewport)`；打印**独立一行** `viewport n/m (x%) [own bucket: not in the rates above]`（最多 4 条失败行）；`v1_row` 的 bad 列表排除 `viewport` 行（否则会被印成 `timeout`）；`--selftest` 41 → **43** 项（新增两条：viewport 不进主分母；viewport 的 ok/wrong 计数正确）；748 → **795** 行。新增代码放**文件尾块**（`v1_counts` / `v1_row` / `selftest` 都是调用时解析该名字）⇒ v1 段的行结构不动。
- **没改什么**：五判定的定义与分母、`pass_rate` / `false_refusal_rate` / `false_accept_rate`、任何既有题的 `finish(...)` 判定、`../sol/sandbox/gym_run.py`（一字未动）。

**33.3 sha（本段）**

| 文件 | 3.3 后 | 3.4 后 |
| --- | --- | --- |
| `gym_app.py` | `66632d85eac81c12` | **`17b6a59cb831dafa`** |
| `score.py` | `ef066713a03eb940` | **`c1a251a248a029c7`** |
| `gym_run.py` | `2ba26b608cf7ec18` | `2ba26b608cf7ec18`（未动） |
| `scripts_sha` | `b8f83571f650` | **`0c2c420e4d40`**（阶段 3.5 又改了一次 `score.py`：现行 `score.py` = `e80a646c63de8075`、`scripts_sha` = `4fc217c37901`，见 §34） |

**33.4 离线验证（本段不许跑批 ⇒ 只用离线证据）**

- 新旧打分器在 **5 个既有 run json**（`t_trap2-w9-move70` / `t_trap5-1` / `t_trap6-1` / `t_trap4-1` / `t_trap3-1`）上输出**逐字节相同** ⇒ 批次 1–20 的读数不受影响。
- 合成 run（1 个 `answerable` + 3 个 `viewport` 行）：新版打 `n 1/1` + `viewport 2/3 (66.7%)` 独立行、**无 `UNDECLARED`**；旧版打 `UNDECLARED 3` + 三行 `timeout #N truth=viewport` —— 那正是"新类未声明时会被误判"的缺陷本身。
- 两个文件 `python -m py_compile` 通过。

**33.5 边界（写死）**

- `viewport` 通过率**不是**五判定、**不可与主线通过率并列引用**；混池批的 `rows_total` / `undeclared` 构成与批次 1–20 不同 —— 主线通过率仍与 1–20 同源（这正是选新类名、而不是复用 `answerable` 的全部理由）。
- 旧 json **不回溯**（`truth_class` 来自各批自己的 `events.jsonl`）。
- 回退 = 单文件：`git checkout <3.4 前 commit> -- sol/sandbox/gym_app.py`（`score.py` 同理）。
- `--bg` 鼠标通道仍不可用（盲区 21）⇒ 本桶覆盖的只是**前台真鼠标**路径。

**33.6 两项决策（本段只处置、不实施）**

- **`scripts_sha` 覆盖面缺口**（只哈希三件套，漏 `gui_see.py` / `loop.py`）：**本段不扩** —— 扩容点在 `gym_run.py`，本段冻结该文件；且本段的 sha 变化必须可归因到靶子/打分器。迁移规则 = 一次**口径变更**：`SCORE-history.md` 记新定义 + run json 同时写 `scripts_sha_files`（参与哈希的文件清单）+ **旧值不改写**。见总纲 §4(d 配套) 判据 3。
- **actor 自身 sha 取不到**（`ping` 只回 `pid` / `py` / `geom` / `dpi` / `uptime`，没有版本/哈希 op）⇒ **不记**，只记 `env.actor_py` / `env.actor_pid`；同一 session 内可辨认、**跨 session 不可追溯**。要取它得先在 `dsh-vision-kit/actor/actor.py` 加一个 op（跨仓库）。见判据 4。

**33.7 manifest v1**

- **只设计、未实施**：设计落 `docs/TASK-AUTHORING.md` §5（schema、闸 = 离线等价核、为什么不同批）。实现另起一段，并接受**第二次** `gym_app.py` sha 裂。

**33.8 下一件**

- **3.5** = v1.0 声明 + 冻结条款 + 欠账分流；验证批（含 `viewport` 桶首次真取数）占前台。（**已完成** —— 见 §34）

## 34. 阶段 3.5 —— A 的验证批 + v1.0 声明 + 冻结条款（2026-10-06）

**34.1 一句话**：`viewport` 类进体系（§33）之后**第一次真取数 = 两批各 8 题、判据 J1–J4 逐条成立**；据此**声明 v1.0 并冻结接口**（八条标准里七条在 `vision-work` 上全过，`(h)` 明确不在声明内 —— 见 34.5）。本段**又裂了一次 `score.py`**（跑前按用户裁决补 v0 打印，见 34.3），`gym_run.py` / `gym_app.py` **未动**。

**34.2 两批**（数值源 = `../sol/sandbox/SCORE.md` 批次 23 / 24 节与合并表；本节只记判据结论）
| 批 | 场景 | 通道 | 判据 | 结论 |
|---|---|---|---|---|
| 23 | `t_rows`（滚轮） | 前台真鼠标、无 chaos | J1 / J2 / J3 / J4 | ✅ 全过（桶单列；滚轮 1 次；`--v1` 主分母 0） |
| 24 | `t_chips`（拖拽） | 同上（同 seed、同版驱动） | J1 / J2 / J3 / J4 | ✅ 全过（8 行 `drag_chip`；主分母 0） |

J5（既有场景无翻转）= **静态论证 + 干跑承担**：本段对靶子的改动只有阶段 3.4 的两个 `truth` 字典，对打分器的改动只有 v0 打印；五判定与判定链一字未动。干跑 `t_trap5 --tasks 2 --press-jitter 0,1200` 仍能构建、能出判定（1/2，`WRONG` 的 detail 里带 `truth_class`）⇒ "改的只是记录方式"成立。**干跑 json 不进任何成绩**。

**34.3 本段的第二次 `score.py` sha 裂（必须与两批一起读）**：B3 §2.3 第 3 项要求 v0 分支也打 viewport 行，而阶段 3.4 的实现只覆盖 v1 路径 —— 因为 `gym_run.py` 按场景名分流（`t_rows` / `t_chips` ⇒ `gates v0`），默认输出里**根本打不出桶**。⇒ 本段**先补再跑**：`main()` 里 `join_truth` 前移到 gate 分支之前无条件执行（它读的是靶子自己的声明，不是打分口径）、v0 分支追加一行 `vp_line(...)`、尾块新增 `vp_line()`（净 +17 = **+19/−2**，795 → 812 行）。新 sha：`score.py` `c1a251a248a029c7` → **`e80a646c63de8075`**、`scripts_sha` `0c2c420e4d40` → **`4fc217c37901`**；离线回归 = 新旧打分器在 **54 个既有 run json × 2 模式（默认 + `--v1`）= 108 次调用上 0 处不同**，`--selftest` 仍 **43/43**。（**行尾说明**：这次补丁同时把 `score.py` 的 CRLF 规范成 LF —— 真实改动是 **+19/−2**，其余是 `\r` 的差，核对命令 `git diff --ignore-cr-at-eol -- sol/sandbox/score.py`。收益 = **记录里的指纹与提交后的字节一致**：从工作树重算三件套 `sha16` 与 `scripts_sha`，能逐位复现两个 batch json 里的值。）

**34.4 跑批前置与踩坑（下次照做）**：① 从 **Windows 侧** `Start-Process <venv python> -ArgumentList … -WorkingDirectory D:\DSH\vision-work\sol\sandbox -WindowStyle Normal` 起（WSL 侧起会离屏、帧全空）；② 跑前 `act.py ping`；③ **靶窗口计数必须 == 1** —— 驱动按 UIA `name` 子串匹配 `"GUI Gym"`，而**本机 DSH 会话窗口标题含这四个字符** ⇒ 跑前 `SetWindowTextW` 改名、跑完**还原**（本段已还原，标题逐字一致）；④ 每批跑完**立刻**打分；⑤ 每批写自己的 `<json 名>-events.jsonl`，不会被下一批覆盖；⑥ 被拒的启动会留下残留靶窗口，后续批会 `foreground before: attention`。

**34.5 v1.0 声明（口径写死，别再扩大）**：`vision-work` 的 v1.0 = 总纲 §4 八条标准里 **(a) 前门三问 / (b) 路径不写死 / (c) 依赖落盘 / (d) 运行记录带 `env` 块 / (d 配套) sha 记录可核对 / (e) 手册在 repo 内 / (f) 边界诚实声明 / (g) 双语策略** 八项中**七条全过**；**(h) 计数与清单单一化明确不在声明内** —— 本仓库侧 `五判定` 这一集合名出现在 9 个文件、审计文档数 `8 份` 出现在 4 处，另两个仓库侧仍有未收口的漂移 ⇒ 归 v1.x（设计见 3.7）。**冻结条款**：v1.0 之后**不再加 scenario 类**；新想法走 **v1.x** 或另开仓库；**"冻结" = 接口冻结**（run json `schema: 1` + 文档 + 引用纪律），**不是停止开发**。

**34.6 欠账分流**：**已关闭 / 已还清**（归档、不再投入）= #4 / #12 / #17 / #19 / #20（窄批口径）/ #21（已修 + 批次 21/22 回归）。**仍开着（= v1.x 清单）**：① #18 = **部分覆盖**（前台真鼠标、批次 23/24 各 8 题、`viewport` 桶；仍不覆盖 `--bg` 鼠标通道与连续交互公差）；② `scripts_sha` 覆盖面缺口（只哈希三件套，漏 `gui_see.py` / `loop.py`）⇒ 留 **3.6** 同批扩容并新增 `scripts_sha_files`；③ actor 自身 sha **不记**（`ping` 无版本 / 哈希 op；只记 `env.actor_py` / `env.actor_pid`，跨 session 不可追溯）；④ **manifest v1 实现**（3.6）；⑤ **计数闸扩展**（3.7）；⑥ `dsh-termux-kit` 侧 5 处计数漂移（总纲 §8 已记，未做）。**（3.5 快照 —— ②④ 已在阶段 3.6 还、⑤ 已在阶段 3.7 做 ⇒ 当前仍开着 = ①③⑥（3.5 快照）；**现 4 项 = ①③⑥⑧，见总纲 §6 的 v1.x 清单**）**

**34.7 手册双份分叉封死（复核）**：`docs/OPERATING.md` 是规程**正本**；仓库外 `D:\DSH\skills\gui-audit-gym\SKILL.md` 只留 frontmatter + 一页指针（阶段 3.3 起）⇒ 改规程只改正本，指针**不再复制正文**。本段复核：指针未复制正文 ✓（技能仍可被会话层列出、注入）。

**34.8 下一件**：**3.6** = manifest v1 实现（+ `scripts_sha` 覆盖面扩容 + run json 新增 `scripts_sha_files`）；**3.7** = 计数闸扩展（设计已在仓库外成文）。**（已完成 —— 见 §35）**

---

## 35. 阶段 3.6 — manifest v1 + `scripts_sha` 覆盖面扩容（两个可独立回退的提交；未跑批）

**35.1 一句话**：五张 plan 表从 `gym_app.py` 的字面量变成 `sol/sandbox/plans.v1.json`（**266 个 `(class, variant)` 逐元组等价**），`scripts_sha` 的覆盖面从三件套扩到**六个文件**并让每个新 json 自带清单（`scripts_sha_files`）。本段**没跑任何批**；两次 sha 裂分别是提交 A（`gym_app.py`）与提交 B（`gym_run.py`），`score.py` **未动**。

**35.2 三个提交的分工（A/B 为什么各自只含那几个文件）**
| 提交 | 内容 | 文件 | 回退 |
|---|---|---|---|
| A `1c1a9b8` | manifest v1：5 张 plan 表 → 数据 | `plans.v1.json`（新）、`gym_app.py`、`.gitignore` | `git checkout` **数据 + 装载器一起**（一个单元） |
| B（本段） | `scripts_sha` 扩容 + 清单自描述 | `gym_run.py`、`audit/SCORE-history.md`、`CHANGELOG.md` | `git checkout` 单文件 |
| C（本段） | 文档收口 | `audit/STATE.md`（§35）、`audit/REPORT.md`、`OPENSOURCE-READINESS.md`、`docs/OPERATING.md`、`docs/TROUBLESHOOTING.md`、`docs/TASK-AUTHORING.md`、`audit/HANDOFF.md` 与三份 `DESIGN-*.md`、`sol/sandbox/SCORE.md`（**共 11 个文件**；含全仓库 `gym_app.py` −11 / `gym_run.py` +9 的行号机械改写） | 纯文档 |

**A 单元含 3 个文件**（`gym_app.py` + `plans.v1.json` + `.gitignore`）：后两者是 A 的**不可分部分** —— `.gitignore` 与 A 同提交是**唯一正确**选择，分开会出现中间状态（manifest 已被 `sol/sandbox/*.json` 静默忽略、下一个提交找不到它），而一个不在哈希里的 manifest 正好就是 3.6b 要堵的「同一 `scripts_sha`、两套题序」。理由已写进 `CHANGELOG.md` 3.6a 条目（不只写在报告里）。

**35.3 manifest v1 长什么样（`schema: 1`）**：每张 plan = 一串 **run** `[[class, variant], n]`（n 个连续相同的条目）；plan 可以用 `base` 从另一张长出来 —— `trap5 = trap4 + 10 × ("swap_mid_task","swap_race_timer")`，于是 48 条既不必写死、也不可能与 `trap4` **悄悄**漂移。文件头部自带 `what` / `adding_a_family` / `not_a_plugin_system` 三块说明，这就是 A2 的**能力边界**落点：manifest 管**题序**（哪一类、哪个变体、几个），**不管渲染**；加一类**新题** = 改 manifest + 复用现有渲染器，改一个**新视觉形态**仍要写 `_trap_*` 与 `t_trapN`；共享渲染器是**有意的**，不是插件系统的雏形。

**35.4 等价性闸 = 离线，不是跑批**：**266/266** 三方一致（HEAD 里的字面量 / 工作树经 `_load_plans()` / manifest 独立展开，不经过装载器），`trap5 == trap4 + 10 races` 单独断言；**13 个场景各 `--tasks 2`** 前台干跑（13/13 写出 json、恰好 2 行、`partial false`，gate 分流仍 `v0`（池类）/`v2`（`t_trap*`）/`v3`（`t_trap5`）；5 个 exit 1 的场景里 `t_trap4`/`t_trap5` 是**该族设计如此**、其余 3 个（`t_menu`/`t_probe_fill`/`t_probe_fill2`）与 3.6 前同形）；`score.py --selftest` **43/43**；3.5 的六个证据文件 sha16 逐位未变。**同 seed 跑批不能当等价测试**：它只覆盖"这次跑到的那些题"。

**35.5 `scripts_sha` 扩容**：覆盖清单 = `gym_run.py` + `gym_app.py` + `score.py` + **`gui_see.py`**（屏读/OCR 路径）+ **`loop.py`**（驱动循环）+ **`plans.v1.json`**（题序）；run json 新增 **`scripts_sha_files`** = 清单本身 ⇒ 任何值都能离线重算，不再依赖"那一版恰好哈希了哪几个文件"。**旧值不回溯**（批次 1–24 保持三文件定义，最后一个值 `4fc217c37901` 属批次 23/24）；**两种定义数值不可互比**，读法落在 [`SCORE-history.md`](SCORE-history.md) §1.1（定义表、重算方法、3.6a/3.6b 逐段读法：题序同构、驱动行为未改）。判定口径（五判定、分母、gate）**一字未动**。

**35.6 本段 sha 轨迹**
| 文件 | 进段值 | 提交 A 后 | 提交 B 后 |
|---|---|---|---|
| `gym_app.py` | `17b6a59cb831dafa` | **`f8b8429725364294`**（1494 → 1483 行，CRLF 保持） | 同左 |
| `gym_run.py` | `2ba26b608cf7ec18` | 同左 | **`fd8e5e1f0ee237b4`**（3724 → 3733 行，LF 保持） |
| `score.py` | `e80a646c63de8075` | **未动** | **未动** |
| `scripts_sha` | `4fc217c37901` | `cebcb97fb952`（三文件） | **`7051c259fa05`**（六文件） |
| `plans.v1.json` | —（新） | `080881993eb1cd7e` | 同左 |

**35.7 行号偏移（核引用时用）**：`gym_app.py` 的装载器（`:84`–`:105`）**之下全部 −11**（5 张表、场景方法、renderer、chaos planner）—— 落在改动区内的引用改用**名字锚点**（本段已把这类引用改成**名字锚点**，例如原先指向 `gym_app.py:147 TRAP_PLAN4` 的那处现写 `plans.v1.json` 的 `trap4`）；`gym_run.py` 的哈希块（`:3675` 起）**之下 +9**，该区间只有 3 处引用（`audit/DESIGN-18-scroll-drag.md` 两处、`sol/sandbox/SCORE.md` 一处），已按新值改。`audit/REPORT.md` 口径行的漂移源新增 **⑪**。**引用零越界（系统核验，3.6 收口段复算）**：文档（`*.md`）里 `gym_app.py:NNN` = **80** 处、`gym_run.py:NNN` = **163** 处；含 `.py` 内注释的全仓库 = **84** / **168** —— 全部落在文件行数内（最大 `1455` ≤ 1483、`3703` ≤ 3733）；复算 = `git grep -o 'gym_app\.py:[0-9]*' | wc -l`（加 `-- '*.md'` 只数文档，`| cut -d: -f2 | sort -n | tail -1` 取最大值），`gym_run\.py` 同法。

**35.8 诚实边界**：① 本段**没跑批** ⇒ 没有任何新读数；"manifest 不影响判分"的证据只有**离线逐元组等价 + 13 场景干跑**两档；② 覆盖面扩容**不等于** `gui_see.py`/`loop.py` 被审过 —— 它只说明"这两个文件变了，值就会变"；③ B3 的**活体字段检查**（新 json 里真带 `scripts_sha_files`）**尚未取证**（3.6 收口段复查：桌面仍锁，前台进程 = `LockApp`）：锁屏时前台进程是 `LockApp.exe`，驱动会打印 `session is locked … waiting up to 3600 s` 并**挂住**，而 `-RedirectStandardOutput` 会把输出缓冲成 **0 字节**日志（跑驱动请加 `PYTHONUNBUFFERED=1`）—— 解锁后跑一次 2 题干跑即可取证（Windows 侧 `Start-Process -WindowStyle Normal` 起 `--scenario t_trap5 --tasks 2`，再 `grep scripts_sha_files` 该 run json；预期 = 字段存在、值 = 六文件清单，与 `_SHA_FILES` 逐条一致）**离线部分已做完**（把 `gym_run.py` 里的 `_SHA_FILES` + `_sha` 代码文本**原样抽出并执行** ⇒ `scripts_sha` = `7051c259fa05`，逐文件 sha16 = `gym_run.py fd8e5e1f0ee237b4` / `gym_app.py f8b8429725364294` / `score.py e80a646c63de8075` / `gui_see.py a683d18d8d617ee7` / `loop.py 535a567d1ffb1ece` / `plans.v1.json 080881993eb1cd7e`；`score.py --selftest` = **43/43**；3.5 两批用现行 `score.py` 复评读数不变 = `t_rows` `viewport 8/8`、`t_chips` `viewport 8/8`）；④ 干跑 json（`t36-<场景>-dry.json`）被 `.gitignore` 忽略、只留本地，**不进任何成绩**。

**35.9 下一件**：**3.7** = 计数闸扩展（设计已在仓库外成文）—— **已完成，见 §36**。

## 36. 计数闸（阶段 3.7 = v1.x 的 `(h)`）—— 普查、分类、闸、边界

**36.1 一句话**：`(h)`（计数与清单单一化）在 `vision-work` 侧的处置 = ①**普查**出 **14** 个【可变量】家族（每条带位置 / 出现次数 / 当前值）②给每个家族定**唯一真源**③把仓库里所有**断言当前值**的位置登记为**宣称点**，由 `tools/check-counts.py` 逐个比对；【历史引用】与【设计目标】**明确不进闸**。v1.0 不动，v1.x 清单划掉一项（⑤）。

**36.2 普查表**（2026-10-06。扫描口径 = `git grep` / `git ls-files`，只数 `*.md`（`.git` 除外）；"宣称点" = 断言**当前值**的位置；"出现次数" = 该字面 / 集合名在全仓库 `*.md` 里的**行数**）

| # | 量 / 集合名 | 真源（唯一） | 当前值 | 宣称点（位置 → 写法） | 出现次数 | 类别 | 进闸 |
|---|---|---|---|---|---|---|---|
| V1 | 审计档案数 | `audit/*.md` 去掉索引 | **8** | `README.md`（`the eight audit documents`）/ `README.zh-CN.md`（`八份审计文档`）/ `audit/README.md`（`这 8 份文件`）/ `OPENSOURCE-READINESS.md` §1 结构图（`8 份审计文档`）+ §(h) 元声明（`4 处`） | 4 处宣称（`8 份` 另见 `audit/README.md` 的两行历史记录） | 可变量 | ✅ |
| V2 | 前门文档数 + 成员清单 | `docs/*.md` | **4**（`QUICKSTART` / `TROUBLESHOOTING` / `TASK-AUTHORING` / `OPERATING`） | `OPENSOURCE-READINESS.md` §6（`` `docs/` 四篇 `` + 四个名字） | 1 处 | 可变量 | ✅ |
| V3 | manifest 表数 / 条目数 | `plans.v1.json` **经 `_load_plans()` 展开** | **5 表 / 266 个 `(class, variant)`** | `STATE.md` §35.1、§35.4 / `CHANGELOG.md` Stage-3.6a / `OPENSOURCE-READINESS.md` §6 3.6 ✅ / `docs/TASK-AUTHORING.md` §5 / `REPORT.md` v0.17 版本行 | `266` 6 处 | 可变量 | ✅（+ 白名单） |
| V4 | `scripts_sha` 覆盖清单 | 代码 `_SHA_FILES`（`gym_run.py`） | **6 个**：`gym_run.py` / `gym_app.py` / `score.py` / `gui_see.py` / `loop.py` / `plans.v1.json` | `STATE.md` §35.5 / `SCORE.md:47` 表头 / `SCORE-history.md` §1.1 新行（这三处**必须列全**） | `六文件` 12 行 / `三文件` 11 行 / `三件套` 94 行 | 可变量 | ✅ |
| V5 | 规则条数 | `HANDOFF.md` §2 的条目数 | **11** | `OPERATING.md` §3.2 标题（`十一条`）+ 该节的副本列表 | 2 份副本 | 可变量 | ✅ |
| V6 | 盲区条数 | `HANDOFF.md` §4 的条目数 | **23** | `OPERATING.md` §3.4（`23 条已知盲区`） | 1 处 | 可变量 | ✅ |
| V7 | 行号口径（8 份档案行数） | 各文件 `wc -l` | `REPORT.md` 642 / `SCORE.md` 1766 / `STATE.md` **本文件** / `HANDOFF.md` 290 / `DESIGN-18` 272 / `DESIGN-21` 156 / `SCORE-history` 88 / `DESIGN-refusal` 435 | `REPORT.md` 行号口径行（**唯一**） | 1 处 | 可变量 | ✅ |
| V8 | 批次区间上界 | `SCORE.md` 的 `## 批次 N` 最大号 | **24**（`## 批次 23` `:1659` / `## 批次 24` `:1708`） | `HANDOFF.md` 标题 + §2 规则 11 / `SCORE.md:47` 表头 | `批次 1–24` 3 处（另有 `REPORT.md:47` 的 `批次 1–16` = **有意**只覆盖到第十六段） | 可变量 | ✅ |
| V9 | 口径版本数 | `SCORE-history.md` §1 的版本表 | **4**（v0 / v1 / v2 / v3） | `README.md`（`(v0–v3)`）/ `README.zh-CN.md`（`（v0–v3）`） | 双语各 1 处 + `SCORE-history.md:9` 的标题 | 可变量 | ✅ |
| V10 | 成文结构（章 / 附录） | `REPORT.md` 的标题 | **8 章 + 3 附录** | `README.md` / `README.zh-CN.md` 的 `## Layout` 行 | 双语各 1 处 | 可变量 | ✅（本轮修：原写 `2 附录`） |
| V11 | 集合名 `五判定` 的文件数 | 扫 `*.md` | **11**（含本文件） | `OPENSOURCE-READINESS.md` §(h) 末段 | `五判定` 39 行 / 11 个文件 | 可变量 | ✅（本轮修：原写 9） |
| V12 | 顶层目录 / 提及路径 | `git ls-files` + 文件系统 | `audit/` `docs/` `sol/` `tools/` | 双语 `## Layout` 块 | 双语各 1 块 | 可变量 | ✅ |
| V13 | 双语数字一致性 | `README.md` 的数字多重集 | 与 `README.zh-CN.md` **逐位相同** | （关系式，没有宣称点） | 双语各 1 份 | 可变量 | ✅ |
| V14 | `v1.x` 仍开着的项数 | 同一条目行里**未划掉**的条目（自洽） | **3**（= ①③⑥；3.7 时；**现 4 项，见总纲 §6**） | `OPENSOURCE-READINESS.md` §6 v1.x 清单行 → `**3** 项`（3.7 时；现 4 项） | 1 处 | 可变量 | ✅（审查提问触发，本轮补） |
| H1 | 批次读数（每批通过率 / 桶 / 墙钟） | `SCORE.md` 各批次节 | 只增不改 | 全仓库引用一律指向 `SCORE.md`（`REPORT.md` 明写"不复制任何批次数值"） | `批次` 全仓库 11 文件 | 历史引用 | — |
| H2 | 逐阶段的 sha / 行数 / 覆盖面 | `STATE.md` §34 / §35 的 sha 轨迹表 + `OPENSOURCE-READINESS.md` §6 各阶段行 | 每阶段一条 | 同上 | 10+ 处 | 历史引用 | — |
| H3 | `audit/` 搬迁记录（`77 / 72`、`8 files changed, 0 insertions`） | `audit/README.md` | 搬迁那天的事实 | `audit/README.md` | 1 文件 | 历史引用 | — |
| H4 | 日期戳（`2026-10-06` 等）、`v0.1`–`v0.17` 版本行 | 各自文件 | 逐版追加 | 各处 | 多处 | 历史引用 | — |
| H5 | 桌面锁 / 驱动解释器 / 行尾等环境事实 | 现场实测 | 逐次实测 | `docs/TROUBLESHOOTING.md` / `OPERATING.md` | 3 处 | 历史引用 | — |
| D1 | v1.0 的八条标准（§4 (a)–(h)）与"七条全过"声明 | `OPENSOURCE-READINESS.md` §4 | 冻结 | §6 声明口径 | 多处 | 设计目标 | — |
| D2 | `docs/TASK-AUTHORING.md` §5 的能力边界（不是插件系统） | 同文件 | 设计 | manifest 头注释 | 2 处 | 设计目标 | — |
| D3 | `HANDOFF.md` §2 的规则内容（规则本身，不是条数） | 同文件 | 纪律 | `OPERATING.md` §3.2 副本 | 2 份 | 设计目标 | — |

**36.3 分类判据**（三类；判据只有一条问句）
- 【可变量】：**今天再数一遍，值会变**（会随工作推进改变，或"应当等于某个现场值"）⇒ 必须单一源 + 可核对。V1–V14 属此类。
- 【历史引用】：**去掉日期就说不通**（记的是某一天 / 某一阶段的快照）⇒ 改了就是篡改。H1–H5 属此类。
- 【设计目标】：**是设定，不是事实**（标准、边界、纪律）⇒ 没有"对不对"只有"遵不遵"。D1–D3 属此类。
- **可变量 vs 历史引用的判定问句**：把日期填进去再读 —— "批次 1–24 的读数"填 `2026-10-06` 后仍然是一句**记录** ⇒ 历史；"审计档案数 8"填上日期反而变怪（今天是 8，明天也该是 8）⇒ 可变量。
- 后两类共 8 条**不进闸**：动了它们只会破坏历史真实性 / 把设计当读数。

**36.4 闸设计（只对可变量）**
- **真源**：见 36.2 第 3 列 —— 文件系统（V1/V2/V12/V13）、数据文件 + 装载器（V3）、代码常量（V4）、权威小节（V5/V6/V8/V9）、现场计算（V7/V10/V11）。
- **断言**：① **相等** —— 宣称点必须出现由真源算出的那个值（含双语词形）；② **列全** —— V2/V4 的宣称点必须把成员逐个列名（"上述三件 + …"不算，本轮就修了两处）；③ **关系** —— V13 要求两份 README 的数字多重集相等；④ **白名单**（只对 `266`）—— 别处再出现 `266` 即报"未登记的宣称点"（本轮它抓到 `REPORT.md` 版本行，是我漏登记的站点）。
- **形态**：`tools/check-counts.py` —— Python 3.9+、只 stdlib、**只读**、无参数即跑；`--list` 打登记表（家族 + 每个宣称点的锚子串与期望写法）。宣称点用**锚子串**而不是行号：否则插入本节就会把闸自己打崩；锚命中 0 或 ≥2 行一律报错（散文被移动 / 复制会被抓住）。
- **接入点**：② 的**变体** —— 写进 `docs/OPERATING.md` **§3.5**（本仓库的规程正本是 OPERATING，不是 `CONTRIBUTING.md`：新建前门文件等于多一份要维护且没人读的东西）。① 退化为"只放进 `tools/` 靠自觉" = 现状的补充，不单独采用。③ pre-commit **可选、本轮不启用**：`git config core.hooksPath .githooks` + 一个调本脚本的 hook —— 需要你明确同意才装（会拦下你自己的补丁脚本之外的每次提交）。
- **自证（用临时数据，不跑批）**：把 `OPENSOURCE-READINESS.md` 的 `10 个` 临时改成 `9 个` ⇒ 闸 `exit 1` 且**只**报这一条；还原后 `exit 0`。
- **为什么不是"不加闸"**：普查当场抓到 4 处实际缺陷（36.5），其中两处（`9 个文件`、`批次 1–11`）已经存在数月而没人发现；行号口径更是**第六次手工重算**（漂移 ①–⑫）。但闸只值它覆盖的那 12 个家族 —— 边界见 36.6。

**36.5 闸抓到的实际缺陷（本段全部修掉）**

| # | 位置 | 原来 | 现在 | 说明 |
|---|---|---|---|---|
| (i) | `OPENSOURCE-READINESS.md` §(h) 末段 | `五判定` 出现在 **9 个文件** | **11 个 `*.md`（含本文件）** | 阶段 3.5 的写法没写计数口径（当时实测 10；本节与 `CHANGELOG.md` 条目使它 +1 —— 闸随即自己抓到了这处变化）；同一条还漏 `README.zh-CN.md`、多列了 `CHANGELOG.md`（`8 份` 的 4 处成员也一并改正） |
| (ii) | `audit/HANDOFF.md` 标题 | 批次 1–**11** | 批次 1–**24** | 标题没跟上批次区间真源（`SCORE.md` 的 `## 批次 N`） |
| (iii) | `sol/sandbox/SCORE.md` + `audit/SCORE-history.md` §1.1 | 六文件定义只列新增的三个（"上述三件 + …"） | 六个 `basename` 全列 | 定义要能独立核，不能靠上文 |
| (iv) | `docs/OPERATING.md` §3.2 | 引用规则"九条" | "十一条" | **阶段 3.6 收口段已修**；这是"同一集合名两处副本必然漂移"的实证（正本在 `HANDOFF.md` §2，OPERATING 是副本） |

**36.6 闸自己的边界（诚实）**
1. 只覆盖 §36.2 表里登记的 **14** 个【可变量】家族（登记表另含 1 个自洽家族，专门核对这个数本身）；**新增宣称点不会被自动发现** —— 只有 `266` 有白名单式反向检查。
2. 跨仓库计数（`dsh-termux-kit` 的 `tools/` 52 / `apps/` 33 / 12 widget / `docs/` 8 篇；`dsh-vision-kit` 的 `docs/` 4 篇；`OPENSOURCE-READINESS.md` §1/§3/§8 的引用）**在别的仓库**，本闸管不了 —— 改上游时必须人工重核（v1.x ⑥ 仍是欠账）。
3. 词形要逐点登记：`eight` / `八份` / `8 份` 是三种写法，脚本不做智能匹配（宁可靠登记表，不靠正则猜）。
4. `scripts_sha` 两套定义的**末值**分散在 5 处（`HANDOFF.md` §2 规则 11 / `OPERATING.md` §3.2 规则 11 / `SCORE-history.md` §1.1 / `SCORE.md:47` / 本文 §35.5）—— 本闸**不查末值一致性**：它记的是"最后一次记录"，不是今天重算的值；要查得升级成 relation check。
5. 无 CI ⇒ 靠 `docs/OPERATING.md` §3.5 的规程 + 自觉；pre-commit **未启用**。
6. V7 只保证那 8 个行数今天与 `wc -l` 一致，**不保证**正文里的 `:NNN` 引用都还指对 —— 那是 §3.4 / 附录 A 自己的纪律。

**36.7 本段没跑批、没裂 sha**：三件套 sha 逐位未变（`gym_run.py` `fd8e5e1f0ee237b4` / `gym_app.py` `f8b8429725364294` / `score.py` `e80a646c63de8075`，`scripts_sha` `7051c259fa05`）；`plans.v1.json`、装载器、五判定 / 分母 / 判定逻辑未动；`dsh-vision-kit` 与 `dsh-termux-kit-copy` 未动。**净增远超 30 行**（普查表 + 新脚本 + 规程）：按本仓库"改动 > 30 行要说清"的口径主动说明 —— 本段是文档 / 工具段，判定逻辑零改动。

**36.8 下一件**：`(h)` 已处置 ⇒ v1.x 只剩 ① `#18` 部分覆盖 / ③ actor 自身 sha 不记 / ⑥ `dsh-termux-kit` 侧 5 处计数漂移。**B3 活体字段证据**仍欠（桌面锁，见 §35.8③）。

## 37. 阶段 3.9 —— v1.x 清单补洞 + `dsh-vision-kit` 的 v1.0 状态（只读核）+ 3.8 技能对齐

**37.1 一句话**：v1.x 清单补上缺的 **⑦**（`dsh-vision-kit` 侧计数闸）并把清单行改成自述 **4** 项、标「三仓库共用」（后续「①+③ 小段」再补 **⑧** ⇒ 当时 **5** 项；**⑧ 段把 ⑦ 划掉 ⇒ 现为 **4** 项**）；对 `dsh-vision-kit` 把 §4 八条**逐条只读核了一遍**，3.9 当时的结论 = **未全过 4 条**（**1 ❌ / 3 ⚠ / 5 ✅**；**真未过只有 (h) 一条**）；**⑧ 段（`dsh-vision-kit@07a56c5` 落闸 + 修 `five stages`）后 = 未全过 3 条 = **0 ❌ / 3 ⚠ / 6 ✅**（❌ 清零）** ⇒ 终止条件「≥2 条未过」按**严格读法**（只数 ❌ = 1 条）**未命中**、按**宽读法**（未全过 = 4 条）命中 —— 两种读法处置相同：**不擅自定口径**、交用户裁决；用户裁决 = **两种口径都写**（声明主体仍是「`vision-work` 的 v1.0」）⇒ §6 冻结条款新增「产品级口径」一行。

**37.2 `dsh-vision-kit` 对 §4 八条的逐条核验（阶段 3.9；只读，命令可复跑）**

| 条 | 状态 | 证据（只读实测） |
|---|---|---|
| (a) 前门三问 | ✅（**总纲 §4(a) 原记的 ⚠ 已过期**） | `README.md:14 ## Why this exists`；`:34 ## The current path: the PC Actor` + `:40`（nothing to install first）；`:101 ## Skills: what the model is told`；`:136 ## Generation 1: seeing the screen (reference)`（已降级）—— 由 `00373f7`（docs: answer the front door's three questions）与 `76505f9` 完成 |
| (b) 路径不写死 | ✅ | 代码 / 脚本零真硬编码：`grep -rn -F 'D:\' --include=*.py --include=*.ps1` 唯一命中 = `tools/install-skills.ps1:13` 的**用法示例** |
| (c) 依赖落盘 | ✅ | `requirements.txt`（`numpy==2.3.5` / `pillow==12.3.0` + pin 理由）与 `requirements-dev.txt`；`README.md:269 ## Requirements` 给系统级（PS 5.1+ / Python 3.9+ / 可选 `tesseract` + `chi_sim+eng` / 可选 Ollama + 两个模型名）+ `actor.ps1 -Setup` 一行装 `comtypes` |
| (d) 产物记 `env` / 构建产物 | ⚠ **半条** | 无 run 记录类产物（该支不适用）；构建产物侧 = DSH 插件包 `plugins/dsh-selflook-local/`，`package.json:3` 有 `"version": "1.0.0"` ✓，但 `tools/ci-static.ps1` 无版本 / manifest 门禁 ✗ |
| (d 配套) sha 记录可核对 | ✅ | 通道 = 本地 git 直推 `main` ⇒ 引用写 `仓库@<commit sha>:路径:行`；`CONTRIBUTING.md:82` 的检查清单要求每次变更带 `CHANGELOG.md` 条目 |
| (e) 手册在 repo 内 | ⚠（总纲原记，仍成立） | `docs/` 4 篇 + `actor/README.md` + `skills/drive-a-windows-gui/SKILL.md` 都在仓库内，但 Generation 1 的说明仍在 `README.md`（`:136`）而不在 `docs/` |
| (f) 边界诚实 | ⚠ 差一句 | `README.md:281 ## Security` + `:293`（No UI screenshots…）✓；但 §4(f) 末尾「统一新增一条」（不承诺复现作者的数字）**尚未落** |
| (g) 双语统一 | ✅ | `README.md`(**296** 行) + `README.zh-CN.md`(**264** 行) 成对（3.9 当时 294 / 262；⑦ 段各 +2 行）；完成那次再同步的 HEAD = `76505f9`，**现行 HEAD = `07a56c5`**（⑦ 落闸） |
| (h) 计数与清单单一化 | ✅（**⑧ 段关闭**；3.9 当时 ❌） | `tools/` 无 `check-counts.py`；**且已有一处活漂移**：`CONTRIBUTING.md:94` 写 `tools/ci-static.ps1` 是 all five stages（5 个），脚本实为 **6** 个（`tools/ci-static.ps1:150` 的 `# ── 6. skills`） —— **⑧ 段已修**（现 `CONTRIBUTING.md:98` = `all seven stages`），且闸 `tools/check-counts.py`（297 行、纯标准库）已接 `tools/ci-static.ps1` **第 7 阶段**（该管线 7 阶段全过、exit 0）：见 `dsh-vision-kit@07a56c5`。**保留** = C3 §1 表的「依赖 pin」「跨文件测量值」两行（C3 自判不需要 / 可选） |

⇒ **未全过 = (h) ❌ + (e) ⚠ + (d) ⚠ + (f) 差一句 = 4 条**（3.9 当时 = **1 ❌ / 3 ⚠ / 5 ✅**）；**⑧ 段后 (h) 已关 ⇒ 未全过 3 条 = **0 ❌ / 3 ⚠ / 6 ✅**（九行里 ✅ 由 5 变 6 —— 含 `(d 配套)` 那一行）**。**勘误（交付后核账）**：旧措辞「4 条未过」把 ⚠ 与 ❌ 混为一谈 —— **真未过只有 (h) 一条**；终止条件按严格读法（只数 ❌ = 1 条）**未命中**、按宽读法（未全过 = 4 条）命中，两种读法处置相同。

**37.3 终止条件的处置**：3.9 的终止条件写「`dsh-vision-kit` 有 ≥2 条未过 ⇒ 停，报『v1.0 声明需重新评估』」。处置 = **不改任何声明语义、不擅自选口径**，把证据交用户裁决；用户裁决 = **两种口径都写进总纲**（原声明不动，另加产品级门槛与今日状态）⇒ 落地为 `OPENSOURCE-READINESS.md` §6 冻结条款的「产品级口径」一行。**产品级 v1.0 = 0 ❌ / 3 ⚠ / 6 ✅，未达成**（`vision-work` 已声明；`dsh-vision-kit` 3.9 当时 **未全过 4 条 = 1 ❌ / 3 ⚠ / 5 ✅**、真未过只有 (h) 一条 ⇒ **⑧ 段把 (h) 关掉**（`07a56c5`）= **0 ❌ / 3 ⚠ / 6 ✅**；**剩 3 ⚠ = (d) 缺门禁 / (e) Generation 1 说明仍在 `README.md:136` / (f) 统一追加句未落**）；`dsh-termux-kit` 未评且 ⑥ 未做）。

**37.4 清单自身的记账缺口（本段顺手核出）**：`OPENSOURCE-READINESS.md` §6 的 `2.x` 行（2.1 发布上游 / 2.2 前门三代整理 / 2.3 下游引用核）**三条都没有 ✅ 标记**，但 2.1 与 2.2 的**事实要件已由仓库提交完成**（`00373f7` + `76505f9` + `CHANGELOG.md` 的 `## [Unreleased]`）⇒ 这是**记账缺口**（清单没跟上仓库），不是工作缺口；**2.3 是否做过无记录，判为不确**。本段**未动 §6 的 2.x 行**（不越权改历史记录）。同类缺口还有一处：v1.x 清单自身直到本段才补上 ⑦ —— 而它从阶段 3.7 起就该在（`(h)` 那次只做了 `vision-work` 侧）。

**37.5 3.8（技能正文对齐）的记录**：改的**不在任何 git 仓库里** —— `D:\DSH\skills\gui-audit-gym\SKILL.md`（阶段 3.3 起已降级为指针文件，**30 行 / LF**）。

- **全量扫的可变事实**：只有一处漂移 —— 第 3 行（frontmatter `description`）与第 16 行写「**九条**引用规则」，实际 = **十一条**（`audit/HANDOFF.md` §2 = 11 条，第 32 行是规则 11；`docs/OPERATING.md:123` 亦写「现 **十一条**」）。其余逐条对得上：`已知盲区 23 条`（HANDOFF §4 = 23 ✓）、`五判定` ✓、`口径版本 v0–v3` ✓、`:8731` ✓、留档三件套（`x.json` / `x-state.json` / `x-events.jsonl`）✓、四个 `docs/` 指针都存在 ✓。
- **技能里根本没有的类别（故无可改）**：解释器路径 / `ACTOR_HOME` / `TESS` / `scripts_sha` / 三文件或六文件定义 / 硬编码行数 —— 这些只写在仓库内文档里。
- **绝对措辞四处**（第 10/11、21、29/30 行）：都是技能自己的变更纪律（「不要改本文件正文」「不要复制规程」）与「数字一律引用 `SCORE.md` + `STATE.md`」，逐条核过 = **现行有效**。
- **改前 / 改后**：`九条引用规则`（2 处）→ **`十一条引用规则`**；文件仍 30 行 / LF，sha16 `020286dd1b7e64bd` → **`959cbc8c80680201`**；`skill(name=gui-audit-gym)` 当场解析出新文案 ✓（未加 `disable-model-invocation`）。
- **留给 3.10 的待评估项（按 3.8 的终止条件只报不做；3.10 已处置，见本节末 38）**：技能把**条数硬编码**（「十一条引用规则」「已知盲区 23 条」）—— 与技能自己的纪律（不复制会漂的数字）同向的改法是**只指节号**（「引用规则见 `HANDOFF.md` §2」「已知盲区见 §4」），这样条数变化不再需要改技能。

**37.6 闸与行号**：`python3 tools/check-counts.py` = **15 families, 0 problem(s)**（当时；后续更正段补了第 16 个家族 `vk-status` ⇒ **现为 16 families**）（家族 14 `v1x-open-items` 自动对上：3.9 当时 **4** 项 → 「①+③ 小段」补 ⑧ 后 = **5** 项 → **⑧ 段划掉 ⑦ 后 = **4** 项**；本段把 `audit/STATE.md` 本节的这句话也登记成家族 14 的**第 2 个宣称点** —— 这正是 3.7 那条「未登记的宣称点看不见」的教训）。本段**没跑批、没动三件套 / 六文件**：`gym_run.py fd8e5e1f0ee237b4` / `gym_app.py f8b8429725364294` / `score.py e80a646c63de8075` / `gui_see.py a683d18d8d617ee7` / `loop.py 535a567d1ffb1ece` / `plans.v1.json 080881993eb1cd7e`，`scripts_sha 7051c259fa05` 逐位未变；`dsh-vision-kit` / `dsh-termux-kit-copy` 只读、未改。

**37.7 诚实边界**：(1) 八条核验是**只读的文档与 grep 实测**，没有跑 `dsh-vision-kit` 的任何脚本（(c) 的两条安装命令未逐条实测）；(2) (a) 判 ✅ 的依据是**章节结构**（三个问题各有专节），命令细节未逐条复核；(3) 2.3 的「不确」= 没找到记录，**不等于没做过**；(4) 本段改了 `OPENSOURCE-READINESS.md` §4 的 **(a)(d)(f)(h) 四行**（登记实测）与 §6 的三处（⑦ / 产品级口径 / 待外部条件）—— 这些是**记录更新**，标准原文未动；(5) 技能 sha16 变化只说明**文件字节变了**，技能不在任何仓库里 ⇒ 无 commit、无 diff 可回溯，改动内容只在本节与 `SKILL.md` 自身。

**37.8 下一件**：3.10 = 技能「只指节号」（**已实施**：见本节末 38；3.8 的待评估项）；**⑦ 已做（⑧ 段，2026-10-06）**：`dsh-vision-kit@07a56c5` 落 `tools/check-counts.py`（297 行，接其 `tools/ci-static.ps1` 第 7 阶段）+ C3 正本入仓 `docs/计数闸设计.md`（仓库外那份已标注为历史）⇒ **现只剩 ⑥**。 **38. 阶段 3.10（技能「只指节号」：评估 + 实施，2026-10-06）**：仓库外指针文件 `D:\DSH\skills\gui-audit-gym\SKILL.md` **行内替换 6 处** —— 行 3 三处（`十一条引用规则与结论边界（已知盲区 23 条）` → `引用规则（audit/HANDOFF.md §2）与结论边界（已知盲区见 §4）`、`口径版本 v0–v3 的可比性` → 同句加 `（以 audit/SCORE-history.md 为准）`、`计分 score.py 的五判定` → 同句加 `—— 口径名；VERDICTS 六类含 timeout 单列，见 score.py`）、行 16（`十一条引用规则、口径版本 v0–v3 与结论边界` → `引用规则（HANDOFF §2）、口径版本 v0–v3 与结论边界（盲区 §4）`）、行 20（`重跑命令、已知盲区 23 条。` → `重跑命令、已知盲区清单。`）、行 25（`（用 drive-a-windows-gui）` → `（若本机已装 drive-a-windows-gui —— 由 tools/install-skills.ps1 装 —— 才转用它）`）；**两处偏差**（行 3 的五判定、行 25 的驱动名，任务书目标文本自带括号 ⇒ 改破折号夹注，避免 `））` 嵌套，字面信息不丢）。技能仍 **30 行 / LF / 结尾换行**、sha16 `959cbc8c80680201` → **`070e5907bac1cf38`**；**改前副本 = `D:\DSH\dsh-actor\tmp\stage310\SKILL.md.pre-3.10impl`**（技能不在任何 git 仓库 ⇒ 无 commit 可回溯，同 §37.7 第 (5) 条的边界）；`五判定` 仍是可 grep 的口径专名、`十一条` 与 `23 条` 已 0。**治本（正本侧）** = `docs/OPERATING.md` §3.2 末尾新增一段**非编号**纪律「技能文件（`SKILL.md`）的纪律（阶段 3.10 起）：它是指针 —— 不得复制会漂的量（条数 / 版本范围 / 行数），这些量只在正本与源文件里维护。」（放在 §3.2 内、§3.3 之前；闸的 `rule-count` 只数该节 `N. ` 行 ⇒ 加段落不影响）。**注入面** = `skill(name="gui-audit-gym")` **按需解析已验证**（解析文案与文件逐字一致、frontmatter 三键仍在）；**新会话的技能目录注入未验**（本会话无法自验）⇒ 不声称已验证。**边界** = 本记录**保持 `audit/STATE.md` 行数不变**（多行记录会让附录 A 记的 1800 与实测不符、触发 `line-policy` 红，而本段范围不许动 `audit/REPORT.md`）；评估正文（13 项清单 + 逐条四问 + A/B/C + 分段与实施判据）在仓库外 `D:\DSH\dsh-actor\tmp\stage310\skill-hardcode-audit.md`。**下一件 = ⑧ 全表复测**（v1.x 清单第 ⑧ 项；复测前先定三处口径：C5 改节边界解析 / C1·C2 改 `git ls-files` 驱动 / C7·C8 的清单来源）。
