# vision-work

一个 **GUI Agent 行为审计靶场** —— 自建靶子、全盲驱动、以及一个把"点对了""点错了""拒答对了"算成三件事的计分器。

**定位**：审计与测量 · **不是**：通过率排行榜，也不是对任何模型能力的断言

> 本仓库的每个数字都来自脚本化运行、由 `score.py` 打分。分数本身在 [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) —— 这份 README 故意一个都不写。

[English](README.md) · **中文**

## 为什么需要它

通过率只回答一个问题 —— 智能体最后做对了吗？它回答不了这个靶场真正想问的问题。

- **拒答是一种行为，不是漏做。** 一个通过率会把"点错了"和"正确地什么都没点"折进同一个格子里，
  而这是两个相反的结果：一个是失误，另一个是**把一块没有任何合法控件的屏幕读对了**。这里两者
  分开计，且**分母在跑之前就声明**。
- **难的是发现屏幕在脚下变了。** "读一次屏、按下去"的驱动，与"重读一次、发现值已经挪了、重新
  规划"的驱动，是两样东西。靶子注入的正是这件事 —— 值会变、控件会移、弹窗会插进来、答案会迟到
  —— 于是跑出来的是**受扰下的行为**，而不是静止画面上的行为。
- **能带走的是方法，不是数字。** OCR、字体、DPI 都在回路里，所以这里每个数字都是**单机数字**，
  新克隆的仓库**不会**复现作者的数。但它会产出**自己的**数，用同一套规则打分、在同一个 gate 内
  可比。这才是交付物：一次你能自己重跑、能据以争论的运行，而不是一张排行榜。

**谁需要它**：在做或测 GUI 智能体的人 —— 任何必须回答"界面在它脚下动的时候它干了什么"、并且
需要这个答案**是证据而不是感觉**的人。

## 这是什么

三个刻意不共享源码的程序：

| 件 | 文件 | 干什么 |
|---|---|---|
| 靶子 | `sol/sandbox/gym_app.py` | 一个 Tk 窗口随机出题 —— 含**必须拒答**的族 —— 并可注入四类干扰（`move` / `slow` / `popup` / `rebuild`） |
| 驱动 | `sol/sandbox/gym_run.py` | 只看像素，经本机 actor 服务；把题从屏幕上读出来、按之前先守门、屏幕在底下变了就重新规划 |
| 计分 | `sol/sandbox/score.py` | 把一次运行的 JSON 变成六个判定类，分母事先声明 |

驱动**永远拿不到真值**：它从屏幕上读指令，然后点它被要求点的东西。这正是靶场的意义 —— 它测的是**受扰下的行为**，*包括*"拒答"这个被单一通过率藏起来的行为。

## 十分钟跑出一次有分数的运行

1. **装** —— 一个交互式 Windows 桌面会话、Python 3.12、PC actor 服务、Tesseract。确切版本、两个
   环境变量、以及各自缺失时的报错原文：[`docs/QUICKSTART.md`](docs/QUICKSTART.md)。
2. **跑** —— 普通 Windows 终端里，在 `sol/sandbox` 下：

   ```powershell
   $PY = 'python'   # 你的 3.12 解释器，带 numpy + Pillow
   & $PY gym_run.py --scenario t_trap5 --tasks 2 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out dry.json
   & $PY score.py dry.json
   & $PY score.py --selftest
   ```

   好跑的样子：退出码 `0`、每题都 ok，并留下三个文件（`dry.json`、`dry-state.json`、
   `dry-events.jsonl` —— 三个一起留）。
3. **跑不动** —— [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) 是一张
   现象 → 原因 → 处置 的表，按你大概会撞上的顺序排。

## 你满足条件吗？

四条必须成立。这是**起飞前检查**、不是门槛 —— 每一条不成立时给出的都是一句明确的报错，而不是一个静悄悄的错误数字。

- **Windows + 交互式桌面会话。** 靶子是 Tk 窗口、驱动读的是真像素；从服务或后台作业起的运行会
  落在屏幕外，读到的是一块空屏。
- **actor 服务在跑、且 ping 得通。** 它是另一个项目 —— 本仓库驱动它，但不包含它。
- **装了 Tesseract，或 `TESS` 指到它。** 读题用的是 OCR；没有它，运行会停下并说明。
- **屏幕上恰好一个靶窗口。** 数出来更多时驱动**拒绝启动**，因为这个计数就是它判断"该驱动哪个
  窗口"的依据。

## 这不是什么

- 不是排行榜：这里不给任何模型排名。
- 不是绝对能力断言：运行是单机的、仅 Windows、绑定在一个操作者的环境上。
- 不是单一通过率：判定是拆开的、分母是声明的、测量 gate 是带版本的（v0–v3）。两批只有在同一个 gate 内才可比 —— 规则见 [`audit/HANDOFF.md`](audit/HANDOFF.md) §2，gate 沿革见 [`audit/SCORE-history.md`](audit/SCORE-history.md)。
- 不是作者数字的复现：见上面"为什么需要它"。

## 目录

```
README.md  README.zh-CN.md  CHANGELOG.md  LICENSE  requirements.txt
docs/QUICKSTART.md               装 → 干跑 → 打分，可移植、无本机路径
docs/TROUBLESHOOTING.md          现象 / 原因 / 处置，全部来自真实失败
docs/TASK-AUTHORING.md           怎么加一类题（题目前是硬编码的）
docs/OPERATING.md                这条判分线的操作规程（中文）
audit/README.md                  什么搬进了 audit/，以及计数与引用口径
audit/STATE.md                   这条线的现状（开头是接续点，§7 是欠账表）
audit/HANDOFF.md                 三件套、测量 gate、一行命令、已知盲区
audit/DESIGN-refusal-scoring.md  为什么判定要拆开（需求 + 计分设计）
audit/REPORT.md                  成文，草稿 v0.1（8 章 + 2 附录）
audit/REPORT-draft.md            章节骨架与来源指针（有意保留）
audit/SCORE-history.md           测量 gate 的一页沿革
sol/sandbox/SCORE.md       每一批的结果，带逐批阅读注意
sol/sandbox/               三件套、探针、批次证据 JSON
```

## 该读哪一份

| 问题 | 文档 |
|---|---|
| 怎么把它跑起来 | [`docs/QUICKSTART.md`](docs/QUICKSTART.md) |
| 跑不起来 | [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) |
| 怎么加自己的一类题 | [`docs/TASK-AUTHORING.md`](docs/TASK-AUTHORING.md) |
| 逐批分数是多少 | [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) |
| A 批能不能和 B 批比 | [`audit/SCORE-history.md`](audit/SCORE-history.md)，再看 `audit/HANDOFF.md` §2 |
| 怎么重跑、已知哪里是坏的 | [`audit/HANDOFF.md`](audit/HANDOFF.md) §3 与 §4 |
| 为什么"拒答对了"要单独计 | [`audit/DESIGN-refusal-scoring.md`](audit/DESIGN-refusal-scoring.md) |
| 成文的论证 | [`audit/REPORT.md`](audit/REPORT.md) |
| 现在正在做什么 | [`audit/STATE.md`](audit/STATE.md) |

**深入阅读**：八份审计文档都在 [`audit/`](audit/) —— 从
[`audit/README.md`](audit/README.md) 开始，它说明搬进去了什么、引用现在怎么写、每个计数在哪里定义。

## 操作规程

这条判分线的日常操作规程在仓库内：[`docs/OPERATING.md`](docs/OPERATING.md)（保持中文 = 操作者
工作语言）。本机有一个名为 `gui-audit-gym` 的 harness 技能，它只是指向那份文件的**指针** ——
规程本身不在仓库外任何地方重复。

## 许可

MIT —— 见 [`LICENSE`](LICENSE)。
