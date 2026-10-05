# DESIGN-21 —— 鼠标通道的可操作性判据（#21 修复设计）

> 状态：**只设计，未实施**（2026-10-05 第二十四段）。本文件不含任何代码改动；三件套 sha 未变。
> 现象与性质判定见 `STATE.md` §7 #21 + §30；重跑清单见 `STATE.md` §31。

## 0. 一句话

鼠标分支要补的**不是**"有没有 `[k]` 徽章"（那是**键**通道的可操作性判据，鼠标通道按设计不用它 —— 照搬会翻掉已有的
`no_badge_fill` 证据），而是"**点了没反应 ⇒ 这不是控件**"这条行为判据。推荐路线②：挂在 `gym_run.py:3507` 之后、
"第二次等判定"之前，**+9 净行**；像素路线（路线①）留作升级路径。

## 1. 两套可操作性模型（现状）

| | 键通道（`--keys`） | 鼠标前台通道 |
|---|---|---|
| 判据 | "这个 box 旁边有没有 `[k]` 徽章" | "这块像素画得够不够实" |
| 落点 | `gym_run.py:2160-2163` → `press_hint`（`:1760-1815`；`if not hint:` 记 `hint_missing` 并返回 False）→ 失败再 `try_other_occurrences`（`:1922`）→ 仍失败 ⇒ `no_key_refuse`（`:1834-1848`）⇒ `refuse("the control carries no action key")` | `gym_run.py:2164-2168` → `control_visible`（`:1317-1335`）：先看徽章（`vis_badge`），没有徽章则用 D1 统计（`vis_score`，`:1279-1315`）比 `T_VIS_FILL = 68`（`:51`）；两者都不够 ⇒ `refuse("the control is painted below the visibility floor")` |
| 何时拒答 | 无徽章（有徽章就按键） | 徽章缺失 **且** D1 < 68 |
| 盲 | 无徽章但**该点**的控件（`no_badge_fill`）会被拒 ⇒ 这类题**从不进键通道** | 画得够实的**散文**（`prose_only`）会被当成控件 ⇒ #21 |

两套模型是**互补**的，不是"一个漏了另一个"。靶子自己写明了这件事（`gym_app.py:118-121`）：
"这五类徽章判定的 `must_refuse`（`prose_only` / `two_close_names` / `disabled` / `flat_button` / `bold_prose`，共 50 题）
留在键盘批里**是有意的**：它们的判定来自'有没有 `[k]` 徽章'，而鼠标批不问这个问题。"
⇒ #21 只在"把键盘设计的 scenario（`t_trap2`）放到鼠标通道跑"时出现（批次 14 / 批次 20 正是如此：为了 `popup` 覆盖而必须用 `t_trap2`）。

## 2. 为什么不能把键判据照搬到鼠标分支（回归证据）

`t_trap3` 的几个鼠标批已经把这件事量过（同一批内 `nb0xx` 各族，`vis_d1` 直接记在行里）：

| 变体 | 真相 | 徽章 | D1 | 现鼠标通道结果（`t_trap3-2/-3/-4` + `smoke`） |
|---|---|---|---|---|
| `nb020`/`nb030`/`nb035`/`nb044` | must_refuse | 无 | 40.0–44.1 | `refused/ok` ✓ 正确 |
| `nb046` | answerable | 无 | （未记） | `refused/wrong` —— **已知边界**（5 行，低于 68） |
| `nb050` | answerable | 无 | 54.0 | `refused/wrong`（同上，3 行） |
| `nb065` | answerable | 无 | 70.0 | **`acted/ok` ✓** ← 加"必须有徽章"就变成 `false_refusal` |
| `nb100` | answerable | 无 | 125.0 | **`acted/ok` ✓** ← 同上 |

⇒ 鼠标通道"**没有徽章也能点**"是**特性**（`no_badge_fill` 就是为它造的类），不是缺陷；加"必须有徽章"会一次翻掉
**每批 6 行、四个批 + smoke ≈ 27 行**已经判对的行。因此 #21 的判据必须落在"**有没有反应**"，不是"有没有徽章"。

## 3. 两条路线

| | 路线① 像素路线 | 路线② 行为路线（**推荐**） |
|---|---|---|
| 补什么 | `control_visible` 的 D1 兜底再加一个**填充率**统计：散文只有字形占少数像素、填充控件占多数（D1 只测"对比够不够"，分不开这两者） | "这一次点击**没有让题前进**" ⇒ 用 app 自己的拒答协议说"做不了" |
| 落点 | 新常量（`gym_run.py:51` 旁）+ 新统计（`vis_score` `:1279-1315` 旁）+ `control_visible`（`:1317-1335`）第三条判据 | `gym_run.py:3507`（`rec = _redo(...)`）之后、`:3508`（第二次 `wait_verdict`）之前 |
| 净行数 | **+15～22** | **+9** |
| 额外成本 | 必须先**标定**：现有 frame 没存盘（只有 `GYM_DEBUG_*` 会存图）⇒ 一个探针批 + 一个验证批 | 无标定；一个验证批即可 |
| 风险 | 阈值拟合样本少；散文与"无徽章控件"的**分离度未测** | 若某题只是"点偏了"，会记成 `false_refusal`（**可见的数据**，取代今天的整批死掉） |
| **风险面**（谁会被误判） | 把**可操作但无徽章**的好控件判成拒答（`nb065` D1 70.0 / `nb100` 125.0，四个鼠标批 + smoke ≈ **27 行**）—— **已否** | 残留 **overclaim**：把「点偏了」断言成「屏上没有合法控件」；面被靶子侧三道 `return` 限在**无判定**的题上 ⇒ **需人工抽查** `false_refusal` 题（见 §8） |
| 什么时候选 | 路线②跑完仍有 `false_refusal`；或将来需要"点之前就知道这不是控件" | **先跑** |

## 4. 路线②的落点与守卫（行级）

插入位置 = attempt 循环结束之后、第二次等判定之前（现 `gym_run.py:3507` 与 `:3508` 之间）：

```
            rec = _redo(d, rec, rec.get("ask") or "", "no verdict arrived")
            # ← 在这里插入 4 行守卫 + 1 行计数 + 3 行注释（净 +9）
            v = v if v.get("result") not in (None, "", "none") else d.wait_verdict(task_i, 1.5)
```

守卫四条（缺一不可）：

1. `not a.keys` —— 只动鼠标通道。键通道同一情形已经由 `no_key_refuse` 正确拒答（批次 12/13 共 74 行 `refused/ok`）。
2. `not a.bg` —— 只动**前台**鼠标通道。`--bg` 鼠标通道整条不生效（已知盲区 21），在那里拒答等于把整批变成 `false_refusal`。
3. `rec.get("act") == "click_label"` **且** `v.get("result") in (None, "", "none")` —— 只有"点了鼠标、且没等到任何判定"才算没反应。
4. `d.task_i() == task_i` —— 发 F8 之前必须确认 app **仍停在这一题**（`refuse()` 会按 `REFUSE_KEY = "F8"`，见 `gym_run.py:1816-1832`；
   题已换 ⇒ 会把**下一题**拒掉）。

**次序约束（硬）**：守卫 3、4 的读取（`v`、`d.task_i()`）与 `d.refuse(...)` 之间**不得插入任何其它操作**（不抓帧、不 OCR、不重规划、不打印）。
理由：`verdict()` 读 app 的 `history`、`task_i()` 读 state 文件，二者与「题有没有前进」是同一件事的两面 —— 中间插任何耗时操作都会把「确认仍停在这一题」的有效期拉长，
一旦 app 在此期间判过并前进，F8 就落到**下一题**上。靶子侧另有两道兜底（`finish()` 在 `result != "none"` 或 `_pending` 挂起时直接 return；`_commit()` 末尾整表清空 `keymap`），
但兜底不能替代次序约束。

动作：`d.refuse(rec, "clicking the asked label changed nothing")` —— 只写 `decision="refused"` / `refuse_why` / `stats["refusals"]` 并按键；
紧接着那一行 `d.wait_verdict(task_i, 1.5)` 会取回 app 的 `refused` 判定 ⇒ 行的 `result` 变 `ok`（真相 = `must_refuse` ⇒ `score.py` 判 `refused_right`）。
**不需要**新增任何字段、协议或靶子改动。

## 5. 影响面（三类，不是两类）

- 键通道：**零改动**（守卫 1）。
- `--bg` 鼠标通道：**零改动**（守卫 2）。
- 前台鼠标通道、**有判定**的题：**零改动** —— 点下去就有判定 ⇒ `v.get("result")` 非空 ⇒ 守卫 3 不成立。
- 前台鼠标通道、`no_badge_fill` 族：**零改动** —— 它们的 `decision` 由 `control_visible` 决定（`acted` 或 `refused`），与「有没有反应」无关。
- 前台鼠标通道、**无判定**的题 = 本次改动的**唯一**作用面，且分两类：

| 无判定题的真相 | 改前 | 改后 | 通过率 |
|---|---|---|---|
| `must_refuse` | `false_accept`（`acted/none`） | **`refused_right`（`refused/ok`）** | **上升** ← 修复目标（批次 20 的 `task 21` 正是此类） |
| `answerable` | `timeout`（`acted/none` 且无判定） | **`false_refusal`** | **不变**（两者都不过，变的只是标签与计数） |

⇒ 本文件早先那句「正常题零改动」**作废**。准确写法：**有判定**的题零改动；**无判定**的题标签会变 —— 一类上升、一类不变。
`must_refuse` 那一类还附带一个收益：同一批**不再早停**在那一题上。

**记账（任务 5）**：新增 `stats["refuse_by_stall"]`，这条路径每真正发一次 F8 就 +1。
理由：没有它，批后无从知道该路径触发了几次、落在哪一类题上（「没测过」与「测过了没事」不能混写）。
它是本设计**唯一**新增的字段：驱动侧一个计数键，不写协议、不动靶子（`score.py` 见 §6 末 + §9）。

## 6. 判据（修后怎么算过关）

1. 同一 seed、同 scenario 的鼠标 `t_trap2` 批跑到 **≥ 25 题**（越过 `task 21`）且**不早停**；
2. `task_i 21` 的 `decision == "refused"`、`refuse_why = "clicking the asked label changed nothing"`，
   `score.py` 不再出现 `false_accept`（该题记 `refused_right`）；
3. 回归：**有判定**的题与修前**逐题一致**（`swap_*` / `prose_with_button` 等同 seed 对照）；
   **无判定**的 `answerable` 题**通过率不变**（只允许标签 `timeout` → `false_refusal`）；
4. `false_refusal` 的**上升数 = 无判定 `answerable` 题数**，且逐题可解释（题号 + `refuse_by_stall` 计数）。
   **不写**「`false_refusal` 不得上升」—— 那是**陷阱判据**：无判定的 `answerable` 题本来就不过，上升是标签迁移而非回归；
   真正该盯的是「上升数是否恰好等于本来就没判定的题数」。
5. 回退回归（可选，约 3 分钟）：一个 `t_trap3` 鼠标批里 `nb065` / `nb100` 仍 `acted/ok`、`nb035` / `nb044` 仍 `refused/ok`。

**只裂哪个文件（任务 6）**：`score.py` 全文只有两处碰 `stats`（`:86`、`:387`），都是 `st = rep.get("stats", {})` 后按名取
`keys` / `shots` / `ocr` —— 没有键集校验、没有遍历、没有拿 `stats` 与逐题行交叉核对（逐题对账在驱动/人工侧）
⇒ **未知 stats 键对判定与计数零影响 ⇒ B 只裂 `gym_run.py`**（`gym_app.py` / `score.py` 不动）。

## 7. 回退

单文件 `git revert <commit>`（或 `git checkout <旧 commit> -- sol/sandbox/gym_run.py`）。改动只有一处、无状态迁移；
回退后 `scripts_sha` 回到 `3fa0e4ba4b1b9679`。**不影响历史批次 json**（判定写在各自 json 里，不回溯）。

## 8. 边界（写在前面）

- 本文件是**设计**：未改一行代码、未跑一批；行数是**净行数**（增 − 删，30 行闸口径）。
- 路线②把"点了没反应"**当作**"这不是控件" —— 这是**推断**，不是读数：它不区分"这不是控件"与"控件点偏了"。
  误判代价 = 一道 `false_refusal`（可见、可补救），收益 = 整批不再死在一道题上。
  ⇒ **每批需人工抽查**：事后逐题看该批所有 `false_refusal` 题（题号 + `refuse_by_stall`），确认每一道都落在「本来就没有判定」的题上；
  只看总数会把 overclaim 藏起来（判据 4 就是为它写的）。
- 只覆盖**前台**鼠标通道；`--bg` 鼠标通道仍是盲区 21。
- 不涉及 #18（滚轮/拖拽进体系 = 靶子侧两处一行 + `score.py` 新桶），见 `DESIGN-18-scroll-drag.md` §9。

## 9. 前置核查（第二十五段，只读）

- **未知 `stats` 键对 `score.py` 无影响**（任务 6 答案）：`score.py` 全文只有两处碰 `stats`（`:86` 与 `:387`），
  两次都是 `st = rep.get("stats", {})` 后按名取 `keys` / `shots` / `ocr`；**没有键集校验、没有遍历、没有与逐题行的交叉核对**
  ⇒ 新增 `stats["refuse_by_stall"]` 既不进判定也不进计数 ⇒ **B 只裂 `gym_run.py`**（不是「连带裂 `score.py`」）。
- 本段（第二十五段）仍未改任何 `.py`：三件套 sha 逐位与第二十四段一致
  （`gym_app.py 66632d85eac81c12` / `gym_run.py 3fa0e4ba4b1b9679` / `score.py ef066713a03eb940`）。
- 行号影响：本文件因本次补丁变长，`REPORT.md` 的行号口径随之改 **v0.13**；`scripts_sha` 与判定口径**均未变**。
