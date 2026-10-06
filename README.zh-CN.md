# vision-work

**GUI 智能体的行为审计靶场** —— 一个自建靶子、一个全盲驱动、一个把"点对了""点错了""拒得对"分成三个计数的评分器。

**定位**：审计与测量 · **不是**：通过率排行榜，也不对任何模型的能力下绝对结论

> 本仓库里每一个数字都来自一次脚本化跑批、由 `score.py` 打出。分数本身住在 [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) —— 这份 README 故意一个分数都不写。

[English](README.md) · **中文**

## 这是什么

三个刻意不同源的程序：

| 角色 | 文件 | 做什么 |
|---|---|---|
| 靶子 | `sol/sandbox/gym_app.py` | 一个 Tk 窗口，随机出题（含"必须拒答"的题族），可注入四类干扰（`move` / `slow` / `popup` / `rebuild`） |
| 驱动 | `sol/sandbox/gym_run.py` | 只看像素，经本机 actor 服务取帧、发键、点鼠标；从屏幕上读题，按压前守门，屏幕在它脚下变了就重规划 |
| 评分器 | `sol/sandbox/score.py` | 把一次跑批的 JSON 打成六类判定，分母事先声明 |

驱动**永远拿不到真值**：它从屏幕上读指令，然后去点它被告知要点的东西。这正是这条线的意义 —— 它测量"干扰下的行为"，**包括拒答这个行为**；而单看通过率会把这个行为整个藏起来。

## 这不是什么

- 不是排行榜：这里不给任何模型排名。
- 不对绝对能力下结论：跑批是单机、Windows 专用，且绑定在一位操作者的环境上。
- 不是单一通过率：判定被拆开、分母被声明、口径被版本化（v0–v3）。两批成绩只有在**同一口径**下才可比 —— 规则见 [`audit/HANDOFF.md`](audit/HANDOFF.md) §2，口径史见 [`audit/SCORE-history.md`](audit/SCORE-history.md)。

## 目录

```
README.md  README.zh-CN.md  CHANGELOG.md  LICENSE
audit/STATE.md                   这条线的当前状态（开头是接续点，§7 是欠账表）
audit/HANDOFF.md                 三件套、口径、一行可复制的命令、已知盲区
audit/DESIGN-refusal-scoring.md  为什么判定要拆开（需求与判定设计）
audit/REPORT.md                  报告正文初稿 v0.1（8 章 + 2 附录）
audit/REPORT-draft.md            章节骨架与素材指针（有意保留）
audit/SCORE-history.md           口径史一页纸
sol/sandbox/SCORE.md       逐批结果与逐批阅读须知
sol/sandbox/               三件套、探针、批次证据 JSON
```

## 运行要求

- Windows + 有桌面会话；本机 actor 服务监听 `:8731`。
- 每次跑批用的解释器：`D:\DSH\.venvs\vision-ci\Scripts\python.exe`（Python 3.12、Pillow 12）。
- 读文字要调 Tesseract；可执行文件路径写死在 `sol/sandbox/gui_see.py:18`，换机器必须改这一行。
- 同一时刻只能开 1 个靶子窗口。

## 快速开始

从 Windows 侧启动、用正常窗口；`--bg` 让跑批不抢你的前台。

```powershell
$py = 'D:\DSH\.venvs\vision-ci\Scripts\python.exe'
cd D:\DSH\vision-work\sol\sandbox

# 先干跑 2 题，确认输入通道是活的
& $py gym_run.py --scenario t_trap5 --tasks 2 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out dry.json

# 鼠标通道 —— 唯一支持逐题对比的那条线
& $py gym_run.py --scenario t_trap5 --tasks 48 --seed 20251007 --press-jitter 0,1200 --max-repeat 3 --json-out my-run.json

# 键通道 + 干扰 —— 探索性线，永不并入定稿线
& $py gym_run.py --scenario t_trap2 --tasks 60 --seed 20251007 --keys --bg --chaos 0.70 --chaos-kind move --chaos-ms 200,700 --until-interferences 5 --max-tasks 60 --max-repeat 3 --json-out my-chaos.json

# 跑完立刻打分：靶子下次启动会覆盖自己的 events 文件
& $py score.py my-run.json
& $py score.py --selftest
```

退出码：`0` 全部题目 ok · `1` 跑完整批但其中有失败题 · `3` **部分批**（驱动没死，把它手头的存下来了 —— 部分批的成绩**不与完整批并列**）。注意 `--max-repeat` 数的是"**连续几题没有前进**"，不是单题内部的重试次数。

## 该读哪一份

| 问题 | 文档 |
|---|---|
| 逐批成绩是多少 | [`sol/sandbox/SCORE.md`](sol/sandbox/SCORE.md) |
| 这两批能不能比 | [`audit/SCORE-history.md`](audit/SCORE-history.md)，再看 `audit/HANDOFF.md` §2 |
| 怎么重跑、已知哪里坏了 | [`audit/HANDOFF.md`](audit/HANDOFF.md) §3 与 §4 |
| 为什么"拒得对"要单独计数 | [`audit/DESIGN-refusal-scoring.md`](audit/DESIGN-refusal-scoring.md) |
| 完整的论证 | [`audit/REPORT.md`](audit/REPORT.md) |
| 现在正在做什么 | [`audit/STATE.md`](audit/STATE.md) |

## 技能

这条线的操作规程不在仓库里，而是一个本机技能：
`D:\DSH\skills\gui-audit-gym\SKILL.md`（面板只从 `D:\DSH\skills\` 识别技能；这份**有意**不在仓库里放副本）。

## 许可

MIT —— 见 [`LICENSE`](LICENSE)。
