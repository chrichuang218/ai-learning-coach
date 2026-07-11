# 从 v1 迁移到 v2

v2 把 AI Learning Coach 从“项目任务生成器”升级为“主动备课、实时带学的私人教练”。迁移不要求删除已有学习历史。

## 核心变化

| v1 | v2 |
| --- | --- |
| 30-90 分钟小闭环 | 难度和时长由真实卡点决定 |
| 默认展示任务、验收和失败反馈 | 教练后台准备，前台一次一个动作 |
| lesson 文件是主要交付物 | 实时辅导过程才是 lesson |
| 常先创建练习再映射项目 | 真实项目优先，必要时只做一次性诊断实验 |
| learning 与战略判断混在一起 | `learning-coach` 与 `focus-coach` 分工 |
| reference 常是 HTML 速查 | Markdown 是稳定知识主格式 |

## 更新为插件安装

v2 使用标准 Codex marketplace 插件结构，同时分发两个 Skill：

```bash
codex plugin marketplace add chrichuang218/ai-learning-coach
codex plugin add ai-learning-coach@ai-learning-coach
```

也可以直接让 Codex 完成同一套插件安装：

```text
帮我安装这个 Codex plugin：
https://github.com/chrichuang218/ai-learning-coach
```

如果曾手工安装旧版，请先移走或删除旧的独立目录，避免同名 Skill 被重复发现：

```text
~/.codex/skills/learning-coach
~/.codex/skills/focus-coach
```

确认插件安装成功后，新开 Codex 会话，让 Skill description 和附属文档重新加载。

## 现有工作区怎么处理

### 历史 lesson 和 HTML

可以保留。它们是历史学习材料，不需要为了升级立即删除。

从 v2 开始：

- 不再默认生成新 HTML lesson。
- 新 lesson 文件只在跨时间恢复或复用教学设计时创建。
- lesson brief 使用 Markdown，并面向教练连续性。

### 历史 exercises

历史目录可以先保留，不要求为了升级立即删除。新版不再创建或继续维护 exercises 体系：

- 一次性代码确认无长期价值后可以归档或删除。
- 可复用的机制、命令和预期输出整理到 `reference/`。
- 用户通过实验表现出的个人掌握证据写入 `learning-records/`。
- 以后确需隔离机制时使用临时位置，完成后回到真实项目验证并清理。

### learning records

继续保留。建议逐步补充：

- 日期、贡献等级和已知时的有效学习时间。
- 真实掌握证据。
- 原误解与纠正。
- 后续可默认的能力。
- 当前能力边界。
- 下一处真实入口。

### reference

稳定知识建议迁移为 Markdown。HTML 可以作为交互附件，但不再作为唯一知识源。

### study plan 和 notes

检查是否仍写着“练习先行、默认 HTML、固定时长”。用户最新偏好和最近掌握证据优先于旧计划。

## 推荐新增

长期工作区可以按需增加：

- `LEARNER-BACKGROUND.md`：汇总已验证能力、已有经验、教学偏好和能力边界。
- `PROGRESS.md`：掌握状态从使命、项目范围和 learning records 派生；同时保存紧凑贡献日历、最近活动与 ETA。
- `sources/`：登记真实项目和材料路径。
- `reference/*.md`：稳定知识源。

不要一次创建所有目录。

创建 `PROGRESS.md` 前，先在 `MISSION.md` 写清目标完成标准，并在 `sources/<project>.md` 写清项目学习范围。历史课程数、文件数和模糊的“以前学过”不能批量换算为进度或补签贡献日历；已有能力可以通过一份带证据的基线 learning record 建立当前状态。只有低强度出勤时直接记录在 progress 的最近活动中，不创建伪掌握记录。

## 外部知识库

Obsidian、LLM Wiki、Notion 等仍可使用，但它们是可选消费者。`reference/*.md` 必须在没有任何外部工具时独立可用。

## 验证升级是否成功

新开会话后输入：

```text
开始学习 TS 吧。
```

正确行为：教练读取现有工作区和真实项目，只给一个当前动作。

错误行为：要求用户先选文件、生成完整课程、创建 HTML lesson，或忽略已有学习记录重新从第一章开始。
