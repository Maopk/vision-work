# 设计：拒绝计分（第 2 件）+ 新计分口径 + 对抗题家族

状态：**已放行 r3**（2026-10-04，实施顺序 §3 → §1 → §2 → §4 → §5 → §6）。基准：`D:\DSH\vision-work\audit\STATE.md`、`D:\DSH\vision-work\sol\sandbox\SCORE.md`。
本轮实测数据源：`..\sol\sandbox\\prof1.json`（12 题混合，键通道+后台）、`probe_ocr_cost.py`（离线分项计时）。
修订 r2（按用户 6 条意见）：①题数对齐；②通过率分母钉死；③`verify_before_act` 的成本并进 §6；④本批定位为 smoke test；⑤`synonym`/`swap_mid_task` 的 `want` 与判定口径钉死；⑥`presses > 1` 归属钉死。
修订 r3（放行时的 3 个残留细节）：①`synonym` 3 题按 **2+1 变体**分配并分列报告（§3）；②`recovered_from_swap` 先按"三计数 + 一列"记，具体事件流等靶子写完复核（§5.2 **已复核定稿为 `a_hit`/`a_hit_but_failed` 两列中性计数**）；③`verify_before_act` 加**单题重读上限 3 次**，超限判 timeout（§6.1）。

修订 r4（放行后的 3 条补充）：
①**"不可比"与"数据源存疑"分开标注** —— 前者是算法换了、数字没错；后者是数字本身可能错（文件被覆盖/引用错位）。`../sol/sandbox/SCORE.md` 里四处（keys-btn / keys-chips9 / keys-menu7 / keys-tog）标 **「数据源存疑·勿引用」**；`keys-tog.json` 已按文件名彻底搜过：现存两个 `*tog*` 文件都是鼠标通道，**原始文件已丢失**，不猜（§2）。
②**加锁屏检测与等待**：`gym_run.py` 新增 `foreground_info()`/`lock_reason()`/`wait_until_unlocked()`（ctypes 直查前台进程名/窗口类/标题，不依赖 actor 与 PowerShell），CLI `--lock-wait SEC`（默认 3600，0 = 只查不等）；**跑测前**等待、**跑到一半锁屏**则暂停等待（记 `lock_waits`）、**跑测后**再查一次并把 `locked_at_end` 写进 run json。动机：锁屏时所有抓图都是空图，那样的分数测的是锁屏不是驱动。
③**profiling 分两份**：`prof2.json` = 纯 baseline（不含 t_trap，与 `prof1.json` 同 seed 同题数，直接可比）、`prof3.json` = 含 t_trap（单看新题型成本）。两份之差才是"t_trap 每题多花多少 ms"。

修订 r5（t_trap 首跑 + 两处修 + 一次复跑后，全部**实测**）：
①**同名多处出现不能直接拒答**：`t_trap-1` 里 3 题 false_refusal 的根因是匹配器选中了**正文句子里那个词**（`target_box` y=126/125，真按钮在 y=187/274），那里没有 `[k]` 徽章 ⇒ 直接拒答。修法 `find_all` + `try_other_occurrences`：**只试带徽章的其他出现**，所以真拒绝（禁用控件、只在正文出现的名字）仍然拒答。证据：false_refusal **3/16 → 0/16**，`prose_with_button 2/2`、`synonym_button 2/2`。
②**换题（swap）只能靠问题带指纹发现**：`trap_swap` 改的是 ask，控件原地不动 ⇒ `frame_task_i` 看不见、块级复验也看不见（按钮还在、标签没变），实测 3 题都按了**上一题**的答案。修法 `band_sig`/`ask_changed`：在复验那一帧（不额外抓帧）比对 ask 框指纹，变了就不按、由重试路径**按新问题重新规划**。**阈值教训**：先用"整框均值 > 12"判，实测三次 swap 的均值只有 **3.7 / 9.2 / 5.7**（450 px 宽的框里只换一个词，均值被摊薄）⇒ 改用**变化格数**（|Δ|>30 的格子 ≥ 3，32×4 网格）。证据：`ask_moved` 触发 → 3 题重规划 → 21/24 → **24/24**。
③**重规划计数此前会丢**：`_redo` 用新记录替换旧记录，调用方在它之前自增的 `replans` 落在被丢弃的记录上 ⇒ 报告写 `replan 0` 而实际重规划 3 次。修法：由 `_redo` 自己把计数搬到新记录。

修订 r6（批次 2 `t_trap2` 落地并实测后）：
①**批次 1 的 24/24 连五次是"题太简单"**，不是"系统对了"：`swap_mid_task` 三次换题全在按键**之前**（`a_hit=0`），"A 做对、屏幕随后才变"这条路径从未被测到；`half_transparent` 三档全过 ⇒ 实际没测到任何阈值；每类 3 题只有 0/33/67/100 四档。⇒ 批次 2：85 题、每类 ≥10，并把 `swap_mid_task` 拆成 **`swap_after_press`**（换题是"按下 A"的**后果**）与 `swap_timer`（旧形状，保留作对照），`half_transparent` 补 `alpha020`/`alpha030`（低于正文自身的 0.213）。
②**结果（`t_trap2-3.json`，v1 83/85 = 97.6%）**：`a_hit` 第一次非 0 —— `swap_after_press` **10/10 `a_hit=10 wrong=0`** ⇒ §5.2 第一种情况（A 对 + B 对）首次实测；**第二种（A 对 + B 错）仍是 0 例**，未验证；`swap_timer` 5 题里 2 题错（#10/#13），`ask_cells=1/0` ⇒ 换题落在**复验帧与按键之间**的残留窗口（约 70–150 ms），复验看不到就按下去了。
③**`half_transparent` 五档全过 ⇒ 这类题仍不区分**：键通道下能按下去的前提是找到 `[k]` 徽章（没有徽章 ⇒ 拒答 ⇒ 不可能五档全过），所以**操作性与填充率无关**（真正机制见 r7 ④：只有填充块走 `blend`、标签与徽章没过）；alpha 0.20 已低于正文自己的 0.213 也照过 ⇒ 按审计口径标**无区分度·不可作为 fill 阈值证据**，不能写成通过。要测阈值必须另做"淡控件 + 无徽章"变体（下一批）。
④**驱动侧三个修**（都由这批暴露）：同义动词命中**正文**就拒答（ask "close the notice"、正文里有 "Close"、真控件是 "OK"）⇒ 只接受带徽章的命中、继续试下一个同义词；`SYNONYM_ACT` 缺 `acknowledge` ⇒ 补上并把动词匹配改成**容错一位 OCR**（实测屏读 `acknowledae`）；ask 解析不出来时驱动**冻结**（靶子不前进、`--max-repeat 3` 随后砍掉整批）⇒ 改为**拒答**并记 `ask_unparsed=1`，口径上这是"一次决定"而不是"没动作"。

修订 r7（用户对批次 2 的审计 + 逐条取证后）：
①**`screen` 列的口径被审计质疑、已澄清**：判据是"归一化后的屏读文本**是否包含真值**"（`gym_run.py:1498`），不包含才记 `file`；**行动仍然用屏读文本**（`gym_run.py:1504` 只在屏读**为空**时才回落文件）⇒ `file` ≠ "没用屏幕"、≠ "屏读失败"。`t_trap2-3` 的 16 行逐题核对（全是 OCR 滑字 `GAMM.`/`TUND`/`XENON2`/`acknowledae`）= **10 题 acted + 6 题 refused、16/16 `result=ok`** ⇒ 没有"该答却拒"藏在这一列里。驱动摘要 `81/17` 是**按读取次数**（85 题 + 13 次重规划 = 98），`score` 的 `69/85` 是**按题目**，两者不矛盾。
②**`replan 13` 已全部归因**：10 × `swap_after_press`（`replan_why="no verdict arrived"` —— 按对 A 后靶子换题，旧 ask 永不再判分 ⇒ 超时重规划）+ 3 × `swap_timer`（`ask_moved=1`、`replan_why="ask re-rolled"`）⇒ 两条**互相独立**的恢复路径（超时 vs 指纹变化）。
③**竞态取证 + 拆列，但口径不升 v1.1**：靶子事件流直接证明（`trap_swap a=INDIGO b=XENON why=timer a_hit=False` → `done detail.clicked=INDIGO`）；新增事件 `trap_stale_press` 与计分行 `race(pressed the replaced ask) N/M`（旧 run 显示 `0/0` 只表示当时没有这个字段）。`race_wrong_target` 只是既有 `wrong_target` 的**子集标注**：不动分母、不动总分公式 ⇒ **与旧数据仍然可比**，故不另立 v1.1（若哪天把它从分母里剔除，才必须升版本并标旧数据不可比）。这条**保留在分母里**：看着没变就按下去是真实能力边界（窗口 70–150 ms）。
④**`half_transparent` 机制定死**：`gym_app.py:931-945` 只把**填充块**按 alpha 混合，标签文字与 `[k]` 徽章**没过 `blend`** ⇒ 五档里可读的东西完全一样，该类**结构上产生不了 fill 边界**；../sol/sandbox/SCORE.md/STATE.md 一律标"**无区分度·不可作为 fill 阈值证据**"。要测阈值两条路：①文字也走 `blend`（一行改动，同批 10 题重跑，测**驱动读数下限**）；②另做"淡控件 + **无徽章**"类，测像素可见性判断（规则须先离线冻结）。
⑤**provenance 规则**：每个 run json 已带 `scripts_sha`（`gym_run.py`+`gym_app.py`+`score.py`）+ `app_args` + `gates`；../sol/sandbox/SCORE.md/STATE.md 引用数字时**必须带 sha**（`t_trap-1..6` 是六个不同版本、互不可比；`t_trap2-1/2` 的 `gates` 还被错写成 v0）。
⑥**下一步顺序**：先把 `no_badge_fill`（淡控件+无徽章）与 `a_hit_but_failed` 跑出稳定数字，**再**跑 chaos 四类；顺带把"等判定时顺带比对 banner 指纹"的优化放进下一批（`swap_after_press` **6233 ms/题 = 整轮的 31.4%**，其中约 5 s 是在等一个永远不会来的判定）。

修订 r8（批次 3 开工前：**先交离线标定曲线**，用户把"曲线先交"当检查点）：
①**靶子 ground truth 与驱动规则解耦**：`gym_app.py` 新增 `OPERABLE_ALPHA = 0.45`（α ≥ 0.45 才可点；低于它的点击被吞、记 `ignored_click` 并**立刻结束本题**，否则整批会等一个永不到来的判定）+ `TRAP_FILL_ALPHAS`（`nb020/030/035/044/046/050/065/100`）；`_trap_faded` 把**轮廓+填充+文字**一起淡化且**不给徽章**；`nb100` = 无徽章全对比度**对照档**（没有它，"全拒"分不清是阈值还是"没徽章就永远拒"）。
②**驱动规则预注册**（`probe_fill_curve.py` 文件头；测量前写死，看过曲线不得改）：主统计量 **D1** = 标签 OCR 框扩 10/6 px 后框内 `|L − base|` 的 **90 分位**，`base` = 外环（扩 34/22 再挖掉内框）灰度**中位数**，只在**驱动自己的 body 裁剪**上算（banner 里有同一个词、全对比度，会送出完美盒子）；诊断量 D2（内框 2 px 环）、D3（峰值）、`ocr_found`/`ocr_conf`/`lenient_found` **只报不选**；**选择规则 = `T_VIS = round(0.5 × D1(α=1.00))`**，驱动**当且仅当** `ocr_found and D1 ≥ T_VIS` 才点击。
③**曲线实测**（`fill_curve.json`：21 档 × 3 帧、种子 20251007、真实 app 帧 1180×780）：**D1 ≈ 137 × α**（0.20→28、0.44→62、0.46→65、0.50→71、0.55→77、1.00→137）⇒ **`T_VIS = 68`**，驱动的可见性门槛落在 **α ≈ 0.50**，**高于靶子的 0.45** ⇒ 预期 **0.46 那 5 题（该答）会被误拒**、0.50 起可点。这是"规则先固定再测量"的应有结果（保守代价），**不是可调参数**：想看不同结果只能在**新一批**里 declare 新规则，不许回改本批。
④**两个如实记录的缺陷**：**D2 在所有 α 上都是 0.0**（内框的 2 px 环落在背景上）⇒ 死诊断，不用；**OCR 定位有非单调空洞**：0.10 就能读到、0.55 能读到，而 **0.60/0.65/0.70 三档 9 帧全读不到**、0.75 又能读到 ⇒ 链条失败在**中间带**而非最淡端 ⇒ 批次里 0.65 那 3 题可能被"读不到"拒掉，**须实测、不得预设**。
⑤**驱动落地**（`gym_run.py`）：常量块 `VIS_PAD_X/Y`、`VIS_RING_X/Y`、`T_VIS_FILL = 68`（注释带曲线数字与来源）+ `Driver.vis_score()`（与预注册统计量**逐字节同构**）+ `Driver.control_visible()`（鼠标模式：**有徽章 ⇒ 直接算控件**；无徽章 ⇒ 用 D1 判，拒时记 `vis_refuse`/`vis_d1`，使"因太淡而拒"永远不与"没找到标签"混淆）；接入三处鼠标分支（精确命中/模糊命中/同义词）。**键通道一字未改**（判据只在 `else` 鼠标分支里）⇒ 批次 2 的键通道数字仍可比。
⑥**交叉验证**（`probe_vis_rule.py`，真实帧）：α=0.30 contract **42.0** = driver **42.0**、α=0.55 **77.0** = **77.0**、空白处 D1 = **0.0**、决定 refuse/click 正确、`0 failed` ⇒ `fill_curve.json` 描述的确实是驱动在做的事；`score.py --selftest` 仍 **29/0**；新 `scripts_sha = bd4c3b0ab2ea`。
⑦**诚实边界（不许夸大）**：D1 区分的是"**淡 vs 强**"，**不是"控件 vs 正文"**——空白处 D1=0，但**正文文字**的 D1 很高（文字本身就是高对比）。所以这条规则**不能**替代徽章通道去判 `prose_only`/`bold_prose`/`disabled`/`two_close_names` 那批"该拒"类 ⇒ **批次 3 的鼠标跑只覆盖语义明确的类**：`no_badge_fill` 28 + 难 swap 8 + `swap_after_press` 10 + `swap_timer` 5 + `half_transparent` 10 + `synonym` 10 = **71 题**；徽章判据的 5 类（50 题）**留在键通道**（放鼠标模式里测的是另一句话）。
⑧**通道约束（决定跑批方式）**：`probe_click_bg.py` 文件头记录"**Tk ignores posted mouse input entirely**"，后台鼠标模式实测 **0/3**（36 次投递点击全不生效）⇒ `no_badge_fill` 无徽章 ⇒ 无键通道 ⇒ **含该类的跑批必须前台 + 真实鼠标**（窗口盖住用户屏幕、指针会被移动，约 1.5–2 分钟/71 题）。标定曲线本身只需抓帧，**已全程后台完成**。

修订 r9（批次 3 实跑后：一次失败批次 + 五处修 + 曲线 2 + 定稿数字）：

①**失败批次 `t_trap3-1.json`（不引用）**：28 题 `no_badge_fill` 全部在 ask 解析层被拒。根因是**措辞**：鼠标通道唯一的点击词汇是 `gym_run.py:1582` 的 `re.search(r"click the button labelled (.+)$", text, re.I)`，而靶子这一类当时用短形式 "click KILO" ⇒ `act=unknown`、`ask_unparsed=1` ⇒ `refuse("the ask does not parse into an action")`。**规则：任何被测类都必须用驱动的规范措辞**（措辞不是被测点）；靶子已改成 "click the button labelled X"。
②**同一批还有一处行失同步**：swap 类每题占**两行**（第一行按 A 后等判定 ~5.7 s 得 `result=none`、第二行重读同一 `task_i`）⇒ 71 行 vs app 57 题；`timeout 43`、`a_hit_but_failed 15` 全是它的产物。修法两条：`tries = 3 if (a.chaos or a.keys or not a.bg) else 1`（前台鼠标跑也会行内重读）；`score.py` 新增 `collapse_attempts()` 按 `task_i` 折叠并打印 `extra_attempts`。**修正后的真相：`a_hit_but_failed = 0`**（原来的 15 例是假象）。
③**坐标 bug（本轮最严重的一处）**：`Driver.body_words()` 经 `words(region=...)` 把区域原点加回 ⇒ 返回的是**整帧坐标**，而 `vis_score()` 当时先裁 body 再用整帧坐标索引 ⇒ 采样整体上移 `body_top`，D1 恒为 **0.0**（`probe_vis_rule.py` 没暴露它，因为它用 body 裁剪图自洽地建框）。修法：`vis_score(img, box, body_top)` 改为**整帧坐标直接计**、`body_top` 只作**夹取下界**（统计量、pad 10/6、ring 34/22 一字未改）；交叉验证重跑仍 `0 failed`；`score.py --selftest` **37/0**。
④**曲线 2（`fill_curve2.json`，`probe_fill_curve2.py`）：把刺激换成类自己的画笔、把链换成驱动自己的链，统计量与选择式一字未改**。起因是同一 α=0.50 在活帧上量到三个数：**71**（探针刺激+探针链）、**67**（同刺激+驱动链）、**54**（类的一帧、标签 KILO）。曲线 2 预检 α=1.00 → **D1=137 ⇒ `T_VIS = 68`（不变）**，α=0.50 → **71**。同帧框宽扫描（25→92、39→92、59→67、69→55、89→40）证明 **D1 主要取决于框内"文字核心 vs 抗锯齿边缘"的比例** ⇒ **门槛是个"带"而不是一条线**，随标签长度/形状漂移；曲线 1 原文件保留，仅"用于推阈值"这一点被曲线 2 取代。
⑤**批次 3 定稿（`t_trap3-2.json`，`scripts_sha 2f4bad88da13`，鼠标通道，实际 64/71）**：`v1 45/62 72.6% decided 100% extra_attempts 2`；`by_alpha`：0.20/0.30/0.35 各 3 拒对、0.44 **5 拒对**、**0.46 恰好 5/5 误拒（跑前预测被压中）**、**0.50 3/3 误拒（预测说可点，未中 ⇒ 有效门槛在 (0.50, 0.65]）**、0.65 与 1.00 各 **3/3 答对**。28 题的 D1 排序值 `40…65 | 70…125`，**66–69 之间为空**、拒答最大 65、点击最小 70 ⇒ 规则执行零例外；另有 3 题是 `no control carries the asked label`（低 α 档）⇒ **"读不到"与"看不见"是两条路径**。
⑥**§5.2 第二种情况（A 对 + B 错）仍 0 例，且判定为"当前驱动打不出来"**：`swap_after_press` 10/10（a_hit=10 全过）、`swap_hard_press` 5/5（a_hit=5 全过）⇒ 只要按对 A，驱动就会重读并按对 B；会错的全是"按下时 A 已不是当前目标"（a_hit=0）。**要测它必须让 B 侧对驱动不可答**（B 淡到门槛下 / B 标签读不出 / ask 说 B 而画面无 B）⇒ 题型重设计。
⑦**`race` 5/5、`guard-blind` 3/3**：70–150 ms 竞态窗口未消（5/5 全踩中）；"B 与 A 只差一个字形"时 **32×4 banner 指纹分辨不了**（3/3 全盲）⇒ 两条修法（按键前再验一帧并缩短复验→按键间隔；换更细指纹或重读 ask 文本）仍欠着。
⑧**同义词类在鼠标通道不可判（声明边界，不是回归）**：第 61–63 题 ask 是 "close the notice"、正文里写着 "Close"，驱动在**正文**上量到 **D1=98**（正文全对比度）⇒ 点正文、无事发生 ⇒ 三行 `NONE` ⇒ 早退。这正是 r8⑦ 声明的"**D1 量淡 vs 强、不量控件 vs 正文**" ⇒ 同义词类留在键通道（批次 2 的 6/6 + 4/4 仍是它的成绩），也是"徽章 5 类留键通道"的第二个独立理由。
⑨**曲线 1 的 OCR 中间带空洞在类自身刺激上未复现**（0.65 三题全读到并答对）⇒ 它是**单一标签刺激**下的现象，不能推广成"这段 α 必然读不到"。
⑩**状态**：批次 3 的 `no_badge_fill`、难 swap、`half_transparent` 三类都有定稿数字；`synonym` 10 题在鼠标通道无定稿（边界所致）；chaos 仍未放行。

修订 r10（批次 4：守门比较规则修好 + `swap_twin_press` 落地 + §5.2 第二种情况**首次打出 8 例**）：

①**守门失明的真根因是折叠表，不是相似度阈值**（**撤销**我上一轮"`sim 1.0` 被后续覆盖"的说法，那句是错的）：`gym_run.py:58 _CONFUSE` 把 `O/Q→0`、`I/L→1`、`S→5`、`B→8`、`Z→2`、`G→6`、`T→7`、`A→4`；`gym_run.py:62 _code()` = upper + 去非字母数字 + 折叠 ⇒ **`TANGO`→`74N60` 与 `TANGQ`→`74N60` 同码**。铁证（`t_trap3-3.json` 的 t34/t35 行）：`ask_word=TANGO`、`ask_label_read='DO: click the button labelled TANGQ'`（守门**重读读对了**）、`ask_label_sim=1.0`、`band=None text=None moved=None` ⇒ 守门确实重读、但折叠后判"未变" ⇒ 按过期 A（`guard-blind`）。
②**修法 `_plain`**：`gym_run.py:67 _plain(s)` = upper + 去非字母数字、**不折叠**；`gym_run.py:1287 ask_text_changed` 改用 `_plain(got) != _plain(want)` 判变化；`ask_label_sim`（`gym_run.py:1312`）改为在**原字**上算 difflib 比值并保留 min（仅诊断，不参与判定）。**分工定死：折叠表只用于"找目标"（容错 OCR 噪声），绝不用于"判变化"（判等）—— 两者要求相反**。这是本轮最贵的教训：同一张表在两个语义相反的位置上复用。
③**实测效果（两次跑）**：折叠相等版 `t_trap3-4.json`（50 题前台鼠标）= `40/50`、`swap_hard_timer` **0/3 → 1/3**（t33 `HARBOP` 被抓）、`race 0/0`、`guard-blind 2/2`；原字相等版 `t_trap4-1.json`（批次 4）= `swap_hard_press 4/5`、`swap_hard_timer 4/5`（`HARBOR/HARBOP` 与 `TANGO/TANGQ` 两类都被抓）⇒ **等式规则本身对，错的是把 Q/O 折在一起**。
④**竞态未清零（她的第 2 步仍欠）**：`t_trap3-4` 的 `race 0/0` 只是那一批 `swap_timer` 4 题恰好没踩中；`t_trap4-1` 又出 **`race 1/1`**（t33 `clicked=TUNDRA, want=RAVEN` —— 换的是**不同词**、指纹也没够 3 格）⇒ 70–150 ms 窗口仍在，只是从"5/5 必踩"降到偶发。守门只在**按键前**看一帧，这一帧到 `key()`/`click()` 之间仍是敞口。
⑤**难题型改用"同词双现"（`swap_twin_press`），不再去碰"找一对 OCR 会误读的词"**（机制①在实现上不可控，同词双现是确定性的）：`sol/sandbox/plans.v1.json` 的 `trap4` 计划（阶段 3.6 前 = `gym_app.py:147`；38 题：twin 8 → hard_press 5 → hard_timer 5 → 淡化切片 10 → after_press 5 → timer 5）、`gym_app.py:981 t_trap4()`；`_trap_swap_mid_task` 里 `twin = variant == "swap_twin_press"`（`gym_app.py:1307`），换题后 `repaint()` 在网格**之前** pack 一个粗体大标题（`gym_app.py:1379`，文本 = 换题后的 `want_b`、`font=("Segoe UI", -24, "bold")`、无徽章、**不是控件**），点击绑 `twin_press`（`gym_app.py:1346`）；`twin_watchdog`（`gym_app.py:1358`，9 s）保证没点击也结算，避免整批错位。
⑥**为什么必然中**：`gui_see.py:130-156 find_text` 按 score 降序、**排序稳定** ⇒ 精确匹配并列 1.0 时取 OCR 词表里靠前者（= 阅读顺序 = 上方的标题）；且 `gym_run.py:1353 verify_before_act` 的预算 `verify_calls >= 1 ⇒ return True` 使**换题后的第二次点击不再复验** ⇒ 驱动按标题、靶子判 wrong，而驱动**自认为答对了 B**。
⑦**批次 4 定稿（`t_trap4-1.json`，`scripts_sha 5e3d5949b6e9`、`gates v1`、38 题、前台真实鼠标、约 2.8 min）**：`v1 21/38 55.3% decided 100% screen 33/38 replan 25`；决策耗时均值 `1413 ms`（score 的 `ms` 列）/ 墙钟均值 `4457 ms`（runner 的 `per task` 行，含等判定）；直方图 `answered_right=21 wrong_target=11 false_refusal=6`；`false_refusal 6/38 (15.8%) false_accept 0/0`；**`swapped 27 a_hit 17 a_hit_but_failed 8`** ⇒ **§5.2 第二种情况（A 对 + B 错）首次打出，用户第二组数拿到**；分变体 `nb046 0/3 nb050 0/3 nb065 2/2 nb100 2/2 swap_after_press 5/5 swap_hard_press 4/5 swap_hard_timer 4/5 swap_timer 4/5 swap_twin_press 0/8`；`swap by variant`：`swap_after_press n=5 a_hit=5 wrong=0`、`swap_hard_press n=5 a_hit=5 wrong=1`、`swap_hard_timer n=5 a_hit=0 wrong=1`、`swap_timer n=5 a_hit=0 wrong=1`、**`swap_twin_press n=7 a_hit=7 wrong=7`**、`race 1/1`、`guard-blind 1/1`；守门统计 `ask_gates 48, ask_moved 8, ask_moved_press 8, ms_askgate 7020.9, shots 122, replans 33`。
⑧**8 例的构成（分开写，不许混）**：7 例来自 twin（`a_hit=1`，驱动换题后点到**标题**、`clicked=null` ⇒ 靶子判 wrong），第 8 例是 `swap_hard_press` 的 t9（`clicked=GAMMA, want=GAMMB`、`a_hit=1`）。twin 的第 8 题（t4）在 **phase A** 就点了标题（判决 `twin=GAMMB, want=GAMMA`）⇒ `a_hit=0`，不计入。**诚实标注**：twin 这类失败的靶子判决是"点了文字、不是控件"，与"点错了另一个按钮"不同类 ⇒ 报告里分开写。`wrong_target 11` = 8 twin + t9 + t13 + t33。
⑨**新测出的可混淆对 `GAMMA`/`GAMMB`（机制①的实测样本，不是构造）**：t4/t9/t13 三次都是驱动**自己**把 B 读成 A（t9/t13 `clicked=GAMMA, want=GAMMB`；t4 反过来把标题 `GAMMB` 读成 `GAMMA`）⇒ 真实存在、与折叠表无关；`TANGO/TANGQ` 才是仅靠折叠表才不可分。⇒ **守门剩下的真短板是"重读自己会误读"**（`guard-blind 1/1` = t13，根因就是守门的重读给出 `GAMMA`）：任何比较规则都挡不住，需要"读两次取多数"或更细指纹（32×4 指纹对一格之差只动 1 格 < 阈值 3）。
⑩**成本**：48 次守门 7020.9 ms ⇒ **146 ms/次**（OCR 进程启动占大头：4× 改 2× 只省约 20 ms）；`shots 122`/38 题 = 3.2 帧/题（守门每次多抓一帧）。twin 的看门狗让 8 题各多等最多 9 s ⇒ 墙钟均值 `4457 ms` 含这部分，**不能当成守门成本**。
⑪**状态**：`no_badge_fill`（`by_alpha` + D1 分布）、`swap_hard_press`/`swap_hard_timer`/`swap_timer`/`swap_after_press`/`swap_twin_press` 都有定稿数字；`synonym` 在鼠标通道仍无定稿（边界所致）；`race` 未清零；chaos 四类仍等放行（她的条件"`no_badge_fill` 与 `a_hit_but_failed` 出稳定数字"现已都满足）。




| 节 | 状态 | 落点 |
|---|---|---|
| §3 `t_trap` 靶子 | **已实现并自检通过** | `gym_app.py`（8 类 ×3 题、`TRAP_PLAN`、`REFUSE_KEY="F8"`）；`probe_trap.py` 正确动作 **24/24 ok**、错误动作全 wrong；F8 走后台键通道 e2e 通 ✓ |
| §1 五判定 + 钉死分母 | **已实现，selftest 25/25** | `score.py`（`v1_verdict`/`v1_counts`/`v1_row`、`--selftest`、`--v1`、`--events`）；驱动侧 `refuse`/`no_key_refuse`/`synonym_invoke`/`presses`/`wasted_actions`/`stale_actions`/`decision`/`gates`/`events`/`scripts_sha`/`app_args` |
| truth 事后 join | **已实现** | 靶子 `ready` 事件广播 `truth_class/variant/trap_class`；`score.py` 的 `load_truth`/`join_truth` **事后**填，驱动不读真相 |
| §2 旧分数标注 | **已完成** | `../sol/sandbox/SCORE.md` 顶部口径表头 + 每行 `口径/通道/读题比例`；`audit_runs.py`、`find_run.py` 逐行核对源文件（三处"数字对不上"如实写明，未复算） |
| §4 扰动按 fire 计 | **已实现** | `gym_run.py --until-interferences N`（+`--max-tasks`，`--chaos-ms` 缺省压到 `200,700`）；`score.py` 输出 `fired-task pass` 与 `quiet` 对照 |
| §5.1 帧↔题号原子对齐 | **已实现** | `rec["frame_task_i"]` + `press_hint` 开头比对 `task_i()`，不一致即不按（记 `stale_actions`/`stale_detected`） |
| §5.1 `verify_before_act` | **已实现** | `Driver.verify_before_act()`：块级复验（≤1 次/题）、重读上限 3、超限 `verify_giveup=1` + `decision=timeout`、`no_key_refuse` 不对"世界动了"的失败拒答 |
| §5.2 swap 三计数 | **已实现并实测** | 事件 `trap_a_hit`/`trap_swap` → `score.py` 事后 join 出 `swapped`/`a_hit`/`a_hit_but_failed`（**改名定稿见 §5.2**）；通过与否仍按 B 判。实测 3 题 `swapped`、`a_hit 0`（驱动都在按下前发现换题 ⇒ 从未答过 A，如实记 0） |
| §5.2 追加：问题带指纹 | **已实现并实测（r5 ②）** | `Driver.band_sig`/`ask_changed`：在复验那一帧比对 ask 框指纹（**不额外抓帧**），变化格数 ≥3 判换题 ⇒ 不按、交重试路径按新问题重规划；`ask_moved` 加入 `no_key_refuse` 豁免 |
| §5.1 追加：同名多处出现 | **已实现并实测（r5 ①）** | `Driver.find_all`/`try_other_occurrences`：只试**带徽章**的其他出现 ⇒ false_refusal 3/16 → 0/16 |
| §6 profiling | **已重跑，数字已更新** | `prof2.json`（baseline 12 题）+ `prof3.json`（t_trap 24 题）；见 §6.2 |
| §3.2 批次 3 标定（r8） | **曲线已交，规则已冻结** | `gym_app.py`（`OPERABLE_ALPHA=0.45`/`TRAP_FILL_ALPHAS`/`_trap_faded`/`_trap_no_badge_fill`/`t_probe_fill`/`--no-badge`/`--control-alpha`）；`probe_fill_curve.py`+`fill_curve.json`+`probe_vis_rule.py`（交叉验证 0 failed）；`gym_run.py`（`T_VIS_FILL=68`、`vis_score`、`control_visible`、三处鼠标分支） |

**§6.1 的成本实测口径（用户第 3 条硬伤，如实承认）**：`verify_before_act` 在有 `expect` 的按键前会**多抓一帧**（~70 ms）**+ 一次 `find_blocks`**，
所以 §6 表里"`find_blocks` 0 次/题"只对**加复验之前**的驱动成立；键通道每题预期 **+~90 ms（约 +3%）**，不是设计时估的 +22 ms（+0.7%）。
这条数字**必须重跑 profiling 后才能引用**（跑测被锁屏挡住，解锁后第一件事就是重跑 `prof2.json` 并更新 §6 表）。

离线分项（锁屏期间可测，`probe_ocr_cost.py _gym_shot.png 5`，1180×780 应用窗口帧，与 app 无关）：

| 分项 | 实测 |
|---|---|
| body 1× `psm 11`（整体读一遍） | 113.3 ms |
| body 2× `psm 6`（放大再读，含 resize 28.2 ms） | 211.1 ms |
| 底栏 1× / 2× `psm 7` | 84.6 / 107.3 ms |
| 小框 4× `read_box` | 95.0 ms |
| `find_blocks`（numpy，1180×780） | **18.8 ms** |
| `convert RGB` / `invert` | 0.8 / 2.0 ms |

⇒ `verify_before_act` = 抓一帧（~70 ms）+ `find_blocks`（18.8 ms）≈ **+89 ms/题** —— 与上面"约 +90 ms"一致 ✓。
（同一张 `psm 11` 在 2560×1600 全屏帧上要 **1035.6 ms**、`find_blocks` 要 81.6 ms ⇒ **帧越小越便宜，抓窗口而不是抓全屏本身就是提速项**，这条留给 §6 的实施。）

修订 r11（批次 6：twin 0/8 → 8/8、race 首次拿到分母、两处成本口径要走样）：

①**同词双现的判据必须用 `find_blocks`（"被绘制块"），不能用 `block_evidence.fill_share`**：实测帧（`probe_w6_twin.json`，`t_trap4` 第 1 题相位 B，banner 问 `HARBOP`）里 `HARBOP` 出现两次——大标题 `542,126,96,17`（不在任何块内，`fill_share` 0.398、neighbours 1、veto False）与真按钮 `292,192,73,14`（落在块 `228,168,172,60`，块 fill **1.0**；同帧 4 个按钮块 fill 全 1.0）。既有 `_button_candidates(img,"HARBOP")` 只返回**标题**（source=text、score 2.543、veto False）⇒ 老判据点标题。**`fill_share` 在这条 app 上是反向的**（标题 0.398 > 按钮 0.283）：阈值的对比度注释（`gym_run.py:593-596`）写明按钮底色 `#e8eef5` 与页面 `#f4f7fb` 只差 12/9/6 ⇒ 12 一个按钮都找不到、8 才看得见平色按钮。**规则：问句词出现 ≥2 次时，选"坐在被绘制块里"的那一次**（实现 `Driver.painted_boxes` / `painted_hit`，只在出现 ≥2 次时才付费；`find_blocks` 单次 77.6 ms ⇒ 只有 twin 8 题付费，≈ +1.6%，在判据内）。
②**块标签的徽章正则需要容忍丢左括号**：OCR 读回 `2] HARBOP`，原正则 `^[\[\(]\s*[0-9A-Za-z]\s*[\]\)]\s*` 匹配失败；放宽成 `^[\[\(]?\s*…` 后只命中真按钮 ⇒ 作**次级信号**，不作主判据。
③**race 的机制更正（我上一轮的说法要改）**：靶子定时型 swap 是 `self.after(rng.randrange(600, 1000), swap)`（`gym_app.py:1403`），而守门抓帧在 ~1.4 s ⇒ **守门看得到换题** ⇒ 重规划 ⇒ 不产生过期按压 ⇒ 批次 1–5 的 `race 0/0` 是**机制必然**，不是"没踩中"。唯一可达的窗口 = **守门抓帧之后、按压派发之前**。所以新 variant `swap_race_timer` 的定时改 `rng.randrange(800, 2600)` ms，驱动加 `--press-jitter 0,1200`（**只对该 variant 生效**，靠读状态文件的 `variant` 门控——否则会把批次 5 的 `swap_timer` 回归题也变成 race，破坏可比性）。实测：`t_trap5-1.json` 的 10 题 race 里拿到 **5 次过期按压，5/5 全错**。
④**两处成本口径要走样，必须一起引用**：`gate_ms` 的 `t_gate` 在 `self.shot()` 之前 ⇒ 鼠标批 P50 **366** / P95 **400** 里含 **219 ms 抓帧**，扣帧 ≈ **147 / 181**（与独立的 `ms_askgate/ask_gates = 148.1` 一致）；键通道批（`--keys --bg`）是 P50 184–189 / P95 204–224。判据 `P50 ≤ 240`、`P95 ≤ 320` 在**扣帧口径**下达标；下一批把 `t_gate` 移到 `shot()` 之后即口径一致（欠账）。
⑤**`--press-jitter` 是唯一"制造分母"的驱动侧改动**（不修任何失败）：它把"守门之后到按压之前"的敞口从 ~100 ms 拉长到 ~1.2 s，使过期按压可被测。不写这一条，race 在这条 app 上**永远拿不到分母**——这也是"分母 < 5 标非缓解"这条规则在批次 1–5 上一直无法兑现的原因。

---

修订 r12（批次 7：留档命名落地 + 两条按用户定论收口；**判定逻辑与批次 6 一字未改**）：

①**每批的 app state/events 按 `--json-out` 命名**（`x.json` → `x-state.json` + `x-events.jsonl`，`gym_run.py` main 里 8 行；不给 `--json-out` 时仍是 `gym-state.json` / `gym-events.jsonl` 老默认名）。起因：`score.py` 是按 run json 里 `events` **那条路径**读真值的（`join_truth`，`score.py:162-169`），而 app 每次启动覆盖写同一文件 ⇒ 事后重打"非最后一批"会**静默错联**（实测重打 `t_trap5-1.json` 得 `36/48`、`MISMATCH 11`、变体表变成 `t_trap2` 的；真值 `37/48`、`MISMATCH 0`）。**这条只改文件命名、不改任何判定** ⇒ sha 变但与批次 6 数字可比；**不引入 `LOGIC_VERSION` 之类的新机制**。
②**race 记"踩线达标"**：分母 5 = 判据线；5/5 全错有区分度，但不据此宣布"已缓解"，也**不单独跑扩分母**——下一批若动守门（§8.1 的 ④⑤⑥ 任一条），race 分母在同一批里扩。
③**chaos 四类都做**（用户 2026-10-04 二次修正，推翻同日"只开 `move`"的收口）：`rebuild` 批次 6 已完成；`move` / `slow` / `popup` 批次 7–8 跑，标「探索性·不并入定稿」，每类 **2 强度 × ≥5 fire**，delta 解释不了就停并写欠账。**`popup` 的前置验证结论（用户要求单独一行）：`--no-topmost` 是继承的** —— `gym_app.py:211 popup_topmost: bool = True` → `234 self.popup_topmost = popup_topmost  # False while a driver works in background` → `653 if self.popup_topmost: top.attributes("-topmost", True)` → `1484 popup_topmost=not a.no_topmost`；驱动在 `--bg` 下必然带 `--no-topmost`（`gym_run.py` 启动串）⇒ 干扰窗落在正常 z 序里，**不需要改一行代码**。**注意 `move` 会移动整窗** ⇒ 只在前台抓帧的批次里要复核 `window_rect`（批次 7/8 走 `--keys --bg`，按 hwnd 抓帧，不受影响）。

---

修订 r13（批次 8：**"读不出的重读"不再被当成"问题变了"**——批次 7 的 `move` 死锁根因）：

①**根因（用户 m09426 指定的记录口径）**：`move` 干扰下**记录的 `ask_box` 在重读时失效**——重读回来的是一段**干净的句子前缀**（`"DO: click the button labelled"`），说明取景框的**边缘切在 label 之前**，`ask_box` 已不再覆盖当帧的标签词；于是 `ask_label_now` 的 `labelled (.+)$` 取不到词，返回**哨兵 `""`**（旧 `gym_run.py:1351-1352`），而 `ask_text_changed` 把 `""` 当**变化**（旧 `1377-1379` ⇒ `ask_changed_text = True; return True`）⇒ 同一帧里**指纹说"没动"（`ask_cells 0`、`ask_delta 0.0`）而被文本路径压过** ⇒ 守门不放行 ⇒ 重规划 ⇒ 死循环。该函数 docstring（`gym_run.py:1315-1317`）从批次 5 起就写着 "an unreadable read is not evidence that the question moved" ⇒ **实现与自己的契约相反**。**次级假设（未排除、也不主导）**：OCR 在 6 px padding 的窄条上漏读末词——同属"读不到"，修法一致，故未做区分实验。
②**实测代价**（批次 7 `t_trap2-w7-move70.json` task 31，`two_close_names` + `move`）：`ask_label_read "DO: click the button labelled"`（重读覆盖到 banner 但**丢了标签词**）、同一帧指纹 `ask_cells 0` / `ask_delta 0.0`（**根本没动**）、`ask_moved_text 1`、`presses 0`、`decision none`、`replans 2`、`replan_why "no verdict arrived"`、`wall_ms 21151`、`verdict_ms null`；同一题连试 3 次 ⇒ `--max-repeat 3` **33/60 早停**。
③**修法（批次 8，都在 `gym_run.py`，不动任何匹配阈值）**：(a) `ask_label_now` 读不出标签一律 `return None`（= 交给指纹判，与同函数里 near-miss 分支 "errs towards answering instead of re-reading for ever" 同一立场）+ 记 `ask_read_unreadable`；(b) `ask_text_changed` 的 `""` 分支改为 `return False`（同一理由，并计数）；(c) **通用退化规则（用户约束：不能只对 `click_label` 类 ask 生效）**——重读 `_plain(got)` 与 `_plain(want)` **不含任何连续 ≥2 字符子串**时判"没读到这个词"，回落指纹并计数（实测：`DOCLICKTHEBUTTONLABELLED` vs `LUMEN93` 无 2 字子串）。用**子串规则**而不是剥离 `labelled` boilerplate：它对 **refuse 类 ask** 同样成立，不依赖 ask 形态（那条路径上 `ask_word` 为空时本就早退）。**放弃的东西**：一个既把 banner 改成本读法解析不出、又不动指纹任何格的换题。
④**同因的第二个 delta（`a_hit` 10→4）**：假阳性 ⇒ 不放行 ⇒ 重规划 ⇒ 首次按压被推到 8 s 安全换题之后（`gym_app.py:1403 if after_press: self.after(8000, lambda: swap("safety"))`）⇒ 按到的是 B（**正确**，故 `wrong=0`、10/10 仍 ok）但 `a_hit=False`。**逐题核对（用户 m09426 要求的"恰为 6 题"）**：move 批 `a_hit=False` 的题 = `#1 #4 #5 #7 #8 #9`，**恰好 6 题**，墙钟 **10.65–10.88 s**（全部 > 8000 ms）；`a_hit=True` 四题墙钟 4.35–4.61 s；控制批十题全 `a_hit=True`、墙钟 6.62–6.97 s ⇒ 机制成立（到 8 s 只剩 1.0–1.4 s 余量，任何延迟都会越线）。⇒ `a_hit` 不是独立指标，是"守门假阳性把按压推过换题线"的**读出量**。
⑤**Option A（每帧重算 banner box）本批不做**：只做"读不出 ⇒ 回落指纹"，不去重算框——重算会引入"用哪一帧的 banner box"这一新状态；按用户定论进欠账（`STATE.md` §7 #15）。

⑥**诚实边界（用户 m09520 定：接受并记录）**：通用退化规则把"不可读"的判定从"**完全无关**"放宽到"**无任何连续 2 字符重叠**"⇒ 极端情况下（want 很短或与 got 恰好没有 2 字重叠的无关串）可能把**无关串误判为可读**。这是**概率风险，不是结构性缺陷**：判错的后果是回到"按指纹守门"这条保守路径，不会凭空放行一次错误按压。
⑦**refuse 类 ask 的边界（自发现，用户 m09520 要求落纸）**：refuse 类 ask 的 `want` 为空 ⇒ `ask_text_changed` 的 `""` 分支（修法 b）直接 `return False` ⇒ **文本路径提前被禁用，完全靠指纹守门**（这正是 `ask_word_from` 三角验证设计要保护的路径：synonym 鼠标通道靠指纹兜底；见 `STATE.md` §10.2）。

**修订 r14（批次 8 实测结果，sha `f598406cfc70`；chaos 四类 × 2 强度，探索性）**：
①**修法有效**：`ask_read_unreadable` 在 `move@0.70` 计 2 次、**全部落在批次 7 卡死的 `task 31`**，该题这次正常作答；整批**无 `result none`**、跑满 60 题（`58/60`）。
②**但 `a_hit` 未回到 ≥8/10**（0.70 → 4/10、0.35 → 7/10）：它是"守门假阳性/干扰把首按推过 8 s 安全换题线"的**读出量**（没按中的题墙钟 10.6–11.2 s、按中的 4.3–4.9 s）⇒ 该判据按"不硬推"处理，记录而非追求。
③**`slow` 类重新打开了 race**：把靶子判定推后 1.5–3.2 s ⇒ 老 `swap_timer`（600–1000 ms）的窗口重新落到守门抓帧之后 ⇒ `race 0/2`（0.35）与 `2/2`（0.70），**两档同一对 task（#10/#14）**；同族带出第一次 `false_accept 1`（`#44`）与 `MISMATCH 1`（同一 `task_i` 重复尝试、行按 task 折叠）。
④**`popup` 类测不了**（驱动能力缺口）：弹窗标题 `"attention"` 存在，但 `dismiss_interference` 在 `--keys --bg` 下只按标题找、没找到 ⇒ 弹窗留屏吃按键 ⇒ 两档各 1 次 fire 后早停。**该类的数字不引用**（`STATE.md` §7 #16、`HANDOFF.md` 盲区 17）。

---

## 0. 现有口径（对齐基础，来自 `score.py` 实读）

`gym_run.py` 每题记 `result` ∈ `ok / wrong / none / timeout`，加 `act`（怎么做的）与 `want`（靶子声明的目标）；
`score.py` 把 `ok` 当通过、其余当失败，并打印 `act/result/want`。现在的四个口径映射为：

| 旧口径 | 现有字段判据 |
|---|---|
| 点对 | `result=ok` 且 `detail.clicked == want` |
| 点多 | 现在**没记**每题动作次数 ⇒ 无法判（新口径加 `presses`，见 §1.3） |
| 点空 | `result in (none, timeout)` |
| 点在错区域 | `result=wrong` 且 `detail.clicked` 非空但 ≠ `want`（含"点在正文/DISMISS 上"） |

**缺口**：旧口径只有"答案存在"这一种真相。靶子根本没有"这题不该点"的题，所以"点错控件"和"该拒却点了"在旧数据里是同一个 `wrong`。

---

## 1. 新口径：真相两类 × 决定两类 = 五个判定

真相由**靶子声明**（不读 truth、不背答案，判分从靶子的事件流走）：

- `answerable`：屏上有唯一合法可操作控件，`want` 就是它；
- `must_refuse`：屏上**没有**合法控件（该词只出现在正文 / 控件禁用 / 两个候选真伪不辨 = 歧义）。

代理决定：`acted(t)`（按/点了某个控件 t）/ `refused`（**主动放弃**）/ `none`（超时）。

**"拒绝"必须是个可观测动作**（否则靶子没法判 `refused_right`）：约定驱动用 **`F8`** 表示"屏上没有合法控件，我拒绝执行"。
选 `F8` 的理由：靶子的动作键只有数字/字母提示键（`HINT_KEYS`）与 `Esc`（关菜单），`F8` 不冲突、系统也无占用。

靶子的计分点只有两处（实读）：按钮 `w.bind("<Button-1>", …self.finish(…))`（`gym_app.py:551`）与键盘 `self.bind("<Key>", self._on_key)`（`gym_app.py:121`）；
键未命中只记 `key hit=False`、**不计分**（`gym_app.py:215`）。⇒ **点在正文/禁用控件/干扰窗上不产生判定**，那道题只会走向超时或被重读。
`must_refuse` 与 `F8` 的判定路径是**新加的靶子能力**（`t_trap` 那批一起做）。

| # | 判定 | 条件 | 性质 |
|---|---|---|---|
| 1 | `answered_right` | answerable & acted(want) | 通过（旧的"点对"） |
| 2 | `wrong_target` | answerable & acted(≠want) | 失败（旧的"点在错区域"） |
| 3 | `false_refusal` | answerable & refused | **失败（新）能答却拒答** |
| 4 | `refused_right` | must_refuse & refused | **通过（新）该拒就拒** |
| 5 | `false_accept` | must_refuse & acted | **失败（新）该拒却点了**（用户看到的"点正文"） |
| — | `timeout` | 到时限仍无动作 | 单列，不算上面五类（见 §1.1） |

### 1.1 分母与三个率（**钉死，跨 run 必须一致**）

- `N_total` = **所有声明了 `truth_class` 的题**（= 每一道发出去的题，含 timeout）；
- **通过率 = (`answered_right` + `refused_right`) / `N_total`** —— timeout 在分母里、按失败计；
- **有效判定率 = (`N_total` − `timeout`) / `N_total`**，单独列，用来说明"这批数字有多少题真的判过"；
- 另附三个率：**误拒率** = `false_refusal` / answerable 题数、**误受率** = `false_accept` / must_refuse 题数、**点空率** = `timeout` / `N_total`。

一句话：**通过率的分母永远是 N_total，timeout 不豁免。** 换分母必须改口径版本号。

### 1.2 报告列（按用户要求，至少四列）

通过率 / 扰动次数 / **屏幕读题率** / 重规划次数；另加：有效判定率、误拒率、误受率、点空率、`stale_actions`（§5）、`wasted_actions`（§1.3）。

每题落盘的新字段：`truth_class`、`decision`、`presses`、`ask_source`（screen/file）、`interferences`（本题内实际 fire 的干扰数）、`replans`、`frame_task_i_ok`（§5）、`swapped`（§3）。

### 1.3 `presses > 1` 归哪个判定（**钉死**）

不发第六种判定，**判定只看那次"被靶子计入的动作"，额外动作走独立计数**：

- 靶子的判定语义（实读 `gym_app.py`）：只有绑定了动作的控件才计分 —— 按钮 `w.bind("<Button-1>", …finish…)`（`:562`）、键盘 `self.bind("<Key>", self._on_key)`（`:132`），键未命中只记 `key hit=False`（`:226`）；
  点在正文/禁用控件/干扰窗上**不产生判定**（那道题只能超时或被重读）；
- 因此 `presses > 1` 只可能有两种来源：
  - **先白按 N−1 次，然后按对/按错**：判定照第一动作之后的结果走，另记 **`wasted_actions = presses − 1`**；
  - **动作打到了已经被换掉的那道题上**：记进 **`stale_actions`**（§5），那是"时间上错位"，与"点多"不同类。
- `wasted_actions` / `stale_actions` **只作报告列，不改变判定**。理由：把"按了两次才对"记成答错，会让误受率/误拒率这两个真正要看的数字失真。

**与旧口径的对齐结论**：旧 `wrong` 会拆成 `wrong_target` + `false_accept`，旧 `none/timeout` 会拆成 `false_refusal` + 超时
⇒ **旧分数在新口径下不可比**（不是"重算就好"，是当时没有这两类题）。

---

## 2. 旧分数怎么处理（不默默换算法）

三类，全部标 **不可比（口径 v0）**，不复算：

1. **键通道 + 屏幕读题率 100%**（如 `chaos-p0.5.json` 8/8，screen 8 / file 0）；
2. **键通道但含 file-read**（`mix60f.json` 16/60、`chaos-popup.json` 9、`chaos-slow.json` 8、`chaos-move.json` 5）——它测的是"读文件+读屏"的混合；
3. **鼠标时代**（`gym-*.json`：坐标 bug + 通道不同，其中 5 个还键鼠混用）。

`../sol/sandbox/SCORE.md` 顶部加口径表头，每行标注 `口径版本 / 通道 / 屏幕读题率`；run json 新增 `gates: "v1"`、`scripts_sha`、`app_args`。
**新口径从设计确认后的第一批跑测开始，旧行不改数字、只加标注。**

---

## 3. 对抗题家族 `t_trap`（**本批 = smoke test，不是统计结论**）

规模：**8 类 × 3 题 = 24 题**。定位写死：**这一批只验证"靶子造得出来、判分跑得通、拒绝能被正确奖励"**，
不是测阈值。原因：3 题/类（半透明那类还是 3 档透明度各 1 题）的命中率只有 0/33/67/100 四档，
**支撑不了"阈值 0.45 在 alpha 0.50 下失败 X%"这类结论**；真要测阈值，每类 ≥10 题，另开一批（`t_trap++`，届时才写进计分板当结论）。

| 类 | 靶子怎么造 | 真相 / `want` | 期望行为 | 打谁 |
|---|---|---|---|---|
| `prose_same_word` | 正文写 "press IGNITE to continue"，另有真按钮 IGNITE；变体：该词**只在正文** | answerable（`want`=IGNITE）/ must_refuse | 按键 / 拒答 | 语义显著性 |
| `two_close_names` | `BRAVO` 与 `BRAVO95` 同时在屏 | answerable（`want`=精确那个） | 点精确那个 | 匹配精度（0.9 阈值） |
| `disabled` | 唯一同名控件 disabled/greyed | must_refuse（`want`=null） | 拒答 | 禁用态识别 |
| `half_transparent` | 控件 alpha 0.35 / 0.50 / 0.65 各 1 题 | answerable（`want`=该控件 label） | 照点 | **阈值的真中间态**（现有样本只有 0.213 与 1.000） |
| `flat_button` | 无底色扁平按钮（fill_share ≈ 正文） | answerable（`want`=该控件 label） | 照点 | 我的 veto 项本身 |
| `synonym` | ask 说的是**意图**（"dismiss the notice"），正文里出现 "dismiss"，真按钮写近义词 `Close` / `OK` | answerable，**`want` = 真按钮的 label（`Close`/`OK`）**；变体 B：按钮写的是别的词、只有正文含 ask 词 ⇒ must_refuse | 点真按钮 / 拒答 | 语义 ⇄ 结构冲突 |
| `bold_prose` | 正文加粗放大（视觉显著性错位），该词只在正文出现 | must_refuse（`want`=null） | 拒答 | 显著性偏置 |
| `swap_mid_task` | 动作落地前后题目被重掷（A→B） | 见 §5.2 | 察觉换题、按 B 重做 | **跨题竞态** |

### 3.1 变体分配（**放行细节 1，钉死**）

有三类的 3 题不是同构重复，必须写死**并按变体分列报告**：

| 类 | 3 题怎么分 | 报告列（`variant=`） |
|---|---|---|
| `prose_same_word` | **2 题 answerable（屏上真有 IGNITE 按钮）+ 1 题 must_refuse（该词只在正文）** | `prose_with_button` / `prose_only`，**分列通过率，不合并** |
| `synonym` | **2 题 answerable（真按钮写 `Close`/`OK`）+ 1 题 must_refuse（按钮写别的词）** | `synonym_button` / `synonym_only`，**分列通过率，不合并** |
| `half_transparent` | alpha 0.35 / 0.50 / 0.65 **各 1 题**（三档，不是三个重复样本） | `alpha035` / `alpha050` / `alpha065`，**逐档列，不得合并成"半透明通过率"** |
| 其余 5 类 | 3 题同构（同一变体重复三次），只有题目内容不同 | 无需分列 |

理由：变体混在一列里，answerable 与 must_refuse 的成绩会互相抵消 —— 看起来"50% 通过"，实际可能是"两个变体各 100% / 0%"，
那是两份完全不同的结论。

每类记录：`truth_class`、`variant`、`decision`、拒绝是否被正确奖励、`wasted_actions`。

### 3.2 批次 3：`no_badge_fill` 的离线标定（**曲线先交**，见修订 r8）

**靶子侧（ground truth，与驱动规则无关）**：`OPERABLE_ALPHA = 0.45` —— α ≥ 0.45 才可点，低于它的点击被吞（记 `ignored_click`、立刻结束本题）。整控件（轮廓+填充+**文字**）按 α 淡化、**不给徽章**；`nb100` = 无徽章全对比度**对照档**。

**驱动侧（预注册，不得看曲线回改）**：D1 = 标签 OCR 框扩 10/6 px 内 `|L − base|` 的 90 分位（`base` = 外环 34/22 挖掉内框的灰度中位数，只在 body 裁剪上算）；**`T_VIS = round(0.5 × D1(1.00))`**；当且仅当 `ocr_found and D1 ≥ T_VIS` 才点击。

实测曲线（`probe_fill_curve.py` / `fill_curve.json`，21 档 × 3 帧、种子 20251007、真实 app 帧）：

| α | 0.05 | 0.10 | 0.20 | 0.30 | 0.35 | 0.40 | 0.44 | 0.46 | 0.50 | 0.55 | 0.60–0.70 | 0.75 | 0.90 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OCR 定位 | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **✗（9 帧全缺）** | ✓ | ✓ | ✓ |
| D1 | – | 15 | 28 | 42 | 49 | 57 | 62 | 65 | 71 | 77 | – | 104 | 125 | **137** |

⇒ **`T_VIS = 68`**（D1 与 α 几乎线性：D1 ≈ 137·α）⇒ 驱动门槛 **α ≈ 0.50 > 靶子 0.45** ⇒ 预期 **0.46 的 5 题（该答）误拒**、0.50 起可点、0.20–0.44 全部该拒且会拒 ✓。0.65 那 3 题取决于中间带的 OCR 空洞是否在真实题面上复现（**实测，不预设**）。

**诚实边界**：D1 量的是"淡 vs 强"，不是"控件 vs 正文"（空白 D1=0，正文 D1 很高）⇒ 本规则只作**可见性**判据，不替代徽章通道去判 5 个"该拒"类。

---

## 4. 扰动注入口径（用户第 1 条修正）

**不按题数跑，按"真正 fire 的扰动次数"跑**：每档至少 **5 次** fire，不够继续发题（`--until-interferences 5`，另设 `--max-tasks` 保险）。

原因（已测）：app 的 `--chaos-ms 600,1800` 常晚于任务结束（1.3 s/题）⇒ 计划了却没 fire —— `chaos-p0.5.json` 8 题 `interferences=0` 就是证据。
所以跑测要同时把 `--chaos-ms` 压到 200–700 ms，让扰动落在任务中间。

**主指标改成"每次干扰下的通过率"** = 有 ≥1 次 fire 的题里 `ok` 的比例（分母同样用 `N_total` 口径说明：这一项的分母是"有 fire 的题数"，与 §1.1 分开报），另列"0 干扰题"作对照。

---

## 5. 跨题竞态：两路修（用户第 3 条）

### 5.1 两路

**测试环境**（`gym_run.py`）：帧与题号**原子对齐**。抓帧后立刻把该帧绑到 `task_i`（靶子事件里的 `task_i` / banner），
动作前若 `task_i` 变了或 `hint_stale` 命中 ⇒ **整帧丢弃、重拍重读**，不允许"拿着旧帧按旧提示键"。
（已证实的失败样本：`chaos-p1.0.json` #4，`detail={"clicked": "ember61", "want": "BRAVO"}` —— 重掷后照着下一题点了。）

**真实场景**（与靶子无关的通用校验）：动作前做一次**局部低成本复验** —— "我要操作的目标现在还在原位、还是同一个吗"，
用块级检查，不一致就重读。落成 `Driver.verify_before_act()`，接口不依赖靶子特征，真实程序同样适用。

### 5.2 `swap_mid_task` 判哪一道题（**钉死**）

- **动作**按"落地瞬间仍在屏上的那道题"判（靶子 `finish()` 本来就是这么记的）；
- **任务通过与否**按**最终题（B）**判 —— 换题之后必须按 B 重做，拿 A 的答案交差不算通过；
- 记三个计数：`swapped`（本题换过题）、`stale_actions`（打在旧题上的动作数，**不判失败**，那是时间错位不是决策错误）、`stale_detected`（驱动是否察觉并重读）；
- 另立一列 **换题后重做率** = 察觉并重读的题 / 换题题数。

**通过条件的三种情况（放行细节 2；靶子事件流已写完，2026-10-04 复核定稿）**：

| 情况 | 判定 | 额外记录（**改名为中性两列**） |
|---|---|---|
| A 做对 + B 做对 | 通过 | `a_hit=1` |
| A 做对 + B 做错 | 失败（按 B 判） | **`a_hit=1` + `a_hit_but_failed=1`** |
| A 做错（没打到 A） | 失败（按 B 判） | `a_hit=0` |
| A 做对 + B 超时 | 失败（按 B 判） | `a_hit=1`、`a_hit_but_failed=1`、`decision=timeout` |

**命名定稿（用户 2026-10-04 指出 `recovered_from_swap` 偏褒义，而它的定义恰恰是"失败"）**：
报告**不再使用** `recovered_from_swap` / `recovered_and_finished` 这两个名字，改成两个**中性计数**由读者自行组合：

- `swapped` —— 本题换过题；
- `a_hit` —— 旧题（A）**真的被正确完成**（不判通过，只记事实）；
- `a_hit_but_failed` —— A 做对而最终仍判失败。

`score.py` 打印成 `swapped S  a_hit A  a_hit_but_failed F`（第三列就是"过程做对了、结果没过"的题数），通过与否**仍然只按 B 判**。
这样"agent 没被换题打崩"依旧看得见，但不会有人把一列叫 `recovered_*` 的计数误读成成绩。

---

## 6. 本轮 profiling 结果（用户第 4 条：先 profiling 再优化）

> **基准（2026-10-04 实测，`prof2.json`）**：`verify_before_act` 让键通道 **+105.5 ms/题（+3.0%）**
> —— 3658.1 vs `prof1.json` 的 3552.6，同 seed、同 12 题混合。其中 `find_blocks` 单次 18.8 ms（离线）；
> 活体每次约 75 ms（`ms_blocks 300.6` / 4 次 `verify_calls`），每题 ≤4 次（`verify_calls` 上限 1/题，
> 重读最多 3 次）。**设计初稿估的 +22 ms（+0.7%）作废，不要再引用**；下面 6.1 的推算也已被本节取代。

12 题混合、键通道、后台、3.0 s/题（`prof1.json` 逐题均值 2963 ms）：

| 阶段 | 每題 | 占比 | 每次调用 | 次数/题 |
|---|---|---|---|---|
| OCR | 1558.7 ms | **52.6%** | 167 ms | 9.3 |
| 抓图 | 273.7 ms | 9.2% | 70 ms | 3.9 |
| 按键 | 101.4 ms | 3.4% | 5 ms | 20.3 |
| 窗口解析 | 57.7 ms | 1.9% | — | ~1 |
| `find_blocks` | **0 ms** | 0% | 22 ms（离线实测） | 0（**当前**键通道不走它） |
| 其余（等待/未计时段） | 972 ms | 32.8% | — | — |

**关键发现**：单次 OCR 约 **100 ms 是固定开销**——`gui_see.py` 每次调用都新起一个 `tesseract.exe` 子进程
（`subprocess.run` + 临时 PNG）。离线实测：400×100 的小框放大 4× = 103 ms，整幅 1180×780 的 1× = 123 ms，
几乎一样 ⇒ **提速靠"少调用"，不是"裁小图"**。

### 6.1 `verify_before_act` 会让上面的数字变（用户第 3 条硬伤）

§5.1 的块级复验**会**给键通道加上 `find_blocks` 调用，所以：

- 设计约束：**`verify_before_act` 每题最多调用 1 次 `find_blocks`**（只在那一次动作之前）；
- 预算：**+22 ms/题 ≈ +0.7%**（3.0 s → ~3.02 s），前提是复验通过；**不一致时**要重读，代价 ≈ 一次 OCR（100–250 ms），
  这类题记 `verify_rereads`，单独报；
- 因此 §6 的"`find_blocks` 0 次/题"只对**当前**驱动成立；**加了复验之后必须重跑一次 profiling 再更新本表**（不重跑就不许引用这两行）。
- **单题重读上限（放行细节 3）**：靶子在动（动画/刷新/`swap_mid_task`/`bold_prose` 重绘）时复验会反复不过 ⇒ 必须封顶：
  **同一题内 `verify_before_act` 触发的重读最多 3 次**，第 3 次仍不一致就**放弃该题**（记 `verify_giveup=1`、`decision=timeout`，走 §1.1 的分母）。
  否则会"一直重读一直到整批卡死"。计数器落盘为 `verify_rereads`（成功重读次数）与 `verify_giveup`（0/1）。

### 6.2 重跑后的实测（`prof2.json`，2026-10-04，同 12 题混合、同 seed、键通道+后台）

| 指标 | `prof1.json`（加复验前） | `prof2.json`（加复验后） | 差 |
|---|---|---|---|
| 每题 | 3552.6 ms | **3658.1 ms** | **+105.5 ms（+3.0%）** |
| 抓图次数 / `ms_shot` | 47 / 3284.1 | 51 / 3533.4 | +4 次（+249 ms） |
| OCR 次数 / `ms_ocr` | 112 / 18704.6 | 112 / 19323.0 | 0 次（+618 ms = 机器噪声） |
| `find_blocks` | **0 ms** | **300.6 ms**（4 次 `verify_calls`） | 每次 ≈ 75 ms（含块内取标签） |
| 按键 / 窗口 | 1216.6 / 692.5 | 1239.6 / 793.5 | +23 / +101 ms |
| `verify_calls` | —（无此项） | **4**（12 题里 4 题按前复验） | — |

**结论**：§6.1 设计时估的 **+22 ms（+0.7%）** 是**错的**——复验要**多抓一帧**，实测 **+105 ms/题 ≈ +3.0%**，
分项和也对得上（+249 抓图 + 301 块检测 + 少量按键/窗口 ≈ +105 ms/题）。`find_blocks` 在活体 1180×780 窗口帧上
每次约 **75 ms**（离线单测 18.8 ms + 块内标签裁剪/OCR）。**§6 表的"`find_blocks` 0 次/题"自此作废**。

`t_trap` 的成本（`prof3.json`，24 题）：见下方跑测记录；`verify_calls` 与重规划次数决定它比 baseline 贵多少。

待验证方向（**本轮不实施**）：① 常驻 tesseract（stdin 循环/API）；② 把多个小框拼成一张图一次 OCR；
③ 稳定帧缓存（差异 <5% 复用，用户第 8 条建议的护栏）。

---

## 7. 明确不做（等放行）

- 不写 `t_trap` 靶子代码；
- 不改 `gym_run.py` 的计分/拒绝逻辑；
- 不跑新口径的 24 题；
- 不做 OCR 提速。

放行后顺序：§3 靶子（smoke test）→ §1 计分（含 §1.3 计数）→ §2 标注 → §4 注入 → §5 修复（修完重跑 §6 profiling）→ §6 提速。

---

## 8. 如果继续做：下一步是什么（批次 5 未做的部分）

批次 5 只做了"最小收口"那一组（`press_guard` 前置、前缀容忍、计划词三角验证、口径拆分），
本节记下**当时已有取证、但为省时间没有动手**的部分。每条都写清"证据在哪"，以便任何时候重启这条线。

### 8.1 守门（证据已在手，未做）

1. **多候选余量规则加固**（改动 ④）。现状：`find(body, c, 0.82)` 的**精确路径不设余量**，只有 fuzzy 兜底那一支有
   `best - second >= 0.15`（`gym_run.py:1772`）。实测 t9：截断词 `GAMM` 与 `GAMMA` 折叠相似度 **0.889** ⇒ 精确路径直接命中错误按钮。
   做法：所有多候选匹配先过"精确唯一命中，或 best−second ≥ 0.15"，否则重读一次后如实拒答（记 `label_ambiguous`）。
   批次 5 是用**计划词三角验证**绕过这一条（把词修对，而不是让匹配更保守），匹配器本身仍是宽进。
2. **守卫内改序：文本重读在前、廉价指纹在后**（改动 ⑤）。现状 `ask_moved_now` 先指纹后文本（`gym_run.py:1320-1328`）；
   指纹在 `swap_hard_*` 家族上 3/3 全盲（单字形改写 `ask_cells=1` < 阈值 3）却仍要先花一帧。
   做法：文本重读先判，指纹只作"非 label 形 ask"的兜底；逐门样本记 `gate_ms`，报 P50/P95。
3. **`verify_before_act` 的预算与通道**（改动 ⑥）。现状：`verify_calls >= 1 ⇒ return True`（`gym_run.py:1369`）——
   预算是**每"题"**一次，换题后的第二次按压**不复验**（twin 的 7/8 例直接受益于这条），且**鼠标通道从不调它**
   （`gym_run.py:1749` 只调 `press_guard`；批次 4 的 stats 里一个 `verify_*` 键都没有，就是证据）。
   做法：预算改为**每"计划"**一次（重读屏处归零）+ 每题总上限 4，触顶记 `verify_budget_skip`（修后期望 0）；
   鼠标按压并入同一 `verify_before_act`（成本 ≈ `find_blocks` 18.8 ms + 抓帧 70 ms ≈ **+89 ms/首次按压**，
   `--no-press-verify` 可回退）。**诚实边界**：它修不了 t9/t13/t33（那三题要的是"守门真的运行"+"匹配保守"），
   也修不了 twin（标题本身就是带正确标签的块，块级复验照样通过）。
4. **计分 P50/P95**（改动 ⑦ 的另一半）。现状 `ms_askgate` 只有总和（批次 4：48 门 7020.9 ms ⇒ 146 ms/门），算不出分位；
   判据已定：**P50 ≤ 240 ms 且 P95 ≤ 320 ms**（现值 +尾帧 75 ms ≈ 221 ms）。做法：json 存逐门样本 `gate_ms`。

### 8.2 已知机制，本轮不修

- **twin 点标题**（`swap_twin_press`，批次 4 占 `a_hit_but_failed` 的 7/8）：标题与控件在 OCR 里都是"一个文本块"，
  驱动无法只凭文本区分。要修得引入**控件可供性**判据（块是否有边框/底色/命中区），属新增感知能力，不是调阈值。
  当前口径已把它单列（`_twin`），不再混进 `wrong_target`。
- **`GAMMA`/`GAMMB` 实测可混淆对**：驱动三次把 B 读成 A（2x 与 4x 都错），与折叠表无关；批次 5 用"文件全文词 +
  屏上精确匹配"绕过，**没有修感知本身**。
- **`swap_after_press` 每题约 5 s 空等**：判定不会来（题已换），要等满 `verdict_ms` 才重规划；可改成"换题信号优先"。

### 8.3 尚未开跑的线

- **chaos 按类解锁**（用户放行条件：边界数字稳定后再跑）：`--chaos 0.5 --chaos-kind <kind> --until-interferences 5
  --max-tasks 60`，每轮一类，标"探索性·不并入定稿"。
- **`no_badge_fill` 标定改用真实题面画笔**（曲线 2 已证：合成帧 `T_VIS=68` 对不上真实 0.50 档 D1=57）。
- **分层跑测**：核心回归（14 题）每轮必跑 + 盲区探索（20 题）按假设配。批次 5 实测显示：`t_trap4` 38 题一次跑完
  比"只跑 14 题"更省事——**题表由 app 生成**，要拆题得改 `gym_app.py` 的题表生成，成本高于收益。
