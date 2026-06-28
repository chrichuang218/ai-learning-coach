# AI 学习教练（AI Learning Coach）

别再收藏教程了。用真实项目把能力练出来。

**AI Learning Coach** 是一套为程序员设计的项目牵引式 AI 学习教练技能合集。它不默认生成学习大纲，而是把学习目标压进真实项目、源码切片、功能任务或可交付作品里，再推进 30-90 分钟练习闭环和证据复盘。

首要服务对象是程序员：TypeScript、React、AI Agent、源码阅读、工程项目。方法本身也适用于写作、语言、考试、职业技能、创作和研究。

## 技能

这个仓库包含两个核心技能：

| 技能 | 用途 |
| --- | --- |
| `learning-coach` | 把一个学习目标推进成真实项目任务、练习、验收和复盘 |
| `focus-coach` | 在方向太多、学不动、优先级不清时，帮用户收敛主线和下一步 |

一句话记住：

```text
想学会一个东西：用 learning-coach
不知道先做什么：用 focus-coach
```

## 为什么需要它

很多学习失败不是因为资料不够，而是因为：

- 收藏了很多教程，但没有真实练习。
- 看懂时很爽，自己做时不会。
- 学了很多概念，但没有项目承载，知识缺口暴露不出来。
- 学习目标太大，没有下一步动作。
- 缺少反馈，不知道自己到底卡在哪里。
- 学完没有证据复盘，下次又从头开始。

这个项目把问题压小：

```text
学习目标
  -> 真实项目 / 源码入口 / 作品锚点
  -> 一个项目动作
  -> 验收标准
  -> 失败反馈
  -> 证据型复盘
  -> 下一轮学习
```

## 前后对比

之前：

```text
我想学 React，给我一个学习路线。
```

之后：

```text
结论：
你现在不缺路线，缺一个能暴露卡点的项目动作。

下一步：
今天只做一个 60 分钟闭环：在一个最小 React 项目里写一个带 props 和 state 的任务列表组件。

练习：
任务：实现一个可增删的学习任务列表。
验收标准：能新增、删除、标记完成，并解释 state 如何变化。
失败时反馈：把代码、报错和你卡住的步骤发回来。

复盘记录：
根据真实输出判断下一课补 JSX、props、state 还是事件处理。
```

## 安装

把需要的技能目录复制到 Codex 技能目录：

```bash
~/.codex/skills/learning-coach
~/.codex/skills/focus-coach
```

重启 Codex 后使用：

```text
用 learning-coach 帮我学习一个复杂技能。
用 focus-coach 帮我判断接下来最值得投入的方向。
```

也可以从 GitHub 链接安装：

```text
帮我安装这个技能：
https://github.com/chrichuang218/ai-learning-coach/tree/main/learning-coach
```

```text
帮我安装这个技能：
https://github.com/chrichuang218/ai-learning-coach/tree/main/focus-coach
```

## 示例提示词

```text
我想学 TypeScript / React / Agent，但不想再看泛泛教程，帮我找一个小闭环。
```

```text
我收藏了很多英语口语教程，但一开口就卡。帮我安排一个 60 分钟练习。
```

```text
我准备考试，刷题很多但分数不上去。帮我诊断下一步该怎么复习。
```

```text
我刚学完一节，帮我复盘真实卡点，并安排下一步。
```

```text
我同时想学很多东西，但时间有限。用 focus-coach 帮我判断本周最该先做什么。
```

更多示例：

- [learning-coach 示例提示词](examples/prompts.md)
- [learning-coach 样例输出](examples/sample-outputs.md)
- [focus-coach 示例提示词](examples/focus-coach-prompts.md)
- [focus-coach 样例输出](examples/focus-coach-sample-outputs.md)

## 学习工作区

长期学习时，可以把一个目录当作学习工作区：

```text
learning-workspace/
  MISSION.md
  RESOURCES.md
  GLOSSARY.md
  NOTES.md
  lessons/
  exercises/
  reference/
  assets/
  learning-records/
```

如果同时维护多个长期学习方向，可以升级为多轨道工作区：

```text
learning-workspace/
  MISSION.md
  TRACKS.md
  tracks/<track>/
  lessons/<track>/
  exercises/<track>/
  reference/<track>/
  learning-records/<track>/
  assets/
  sources/
```

核心格式：

- [WORKSPACE-FORMAT.md](learning-coach/WORKSPACE-FORMAT.md)
- [TRACKS-FORMAT.md](learning-coach/TRACKS-FORMAT.md)
- [MISSION-FORMAT.md](learning-coach/MISSION-FORMAT.md)
- [LEARNING-RECORD-FORMAT.md](learning-coach/LEARNING-RECORD-FORMAT.md)
- [GLOSSARY-FORMAT.md](learning-coach/GLOSSARY-FORMAT.md)
- [RESOURCES-FORMAT.md](learning-coach/RESOURCES-FORMAT.md)

示例工作区见 [examples/workspaces/minimal-multitrack](examples/workspaces/minimal-multitrack)。

## 好输出长什么样

合格输出必须：

- 有明确结论和下一步动作。
- 不给泛泛学习路线或长资源清单。
- 优先绑定真实项目、源码入口、作品、题目或可交付物。
- 每次只推进一个 30-90 分钟闭环。
- 给出可观察验收标准。
- 要求用户带回证据。
- 根据证据复盘真实卡点。

不合格输出包括：

- “这是 12 周完整路线。”
- “推荐这些教程、书和视频。”
- “你需要更自律。”
- “看懂了就算掌握。”
- “下一节继续讲下一章。”

## 验证

基础校验：

```bash
python path/to/quick_validate.py learning-coach
python path/to/quick_validate.py focus-coach
```

人工验证：

- [evals/smoke-prompts.md](evals/smoke-prompts.md)
- [evals/learning-coach-smoke-prompts.md](evals/learning-coach-smoke-prompts.md)
- [evals/focus-coach-smoke-prompts.md](evals/focus-coach-smoke-prompts.md)
- [evals/rubric.md](evals/rubric.md)
- [evals/learning-coach-rubric.md](evals/learning-coach-rubric.md)
- [evals/focus-coach-rubric.md](evals/focus-coach-rubric.md)

## 致谢

本项目受到 Matt Pocock 的 [`teach` 技能](https://github.com/mattpocock/skills/blob/main/skills/productivity/teach/SKILL.md) 启发，尤其是它对状态化教学工作区、使命驱动课程、学习记录和长期能力建设的设计。

## 许可证

MIT
