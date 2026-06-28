# 学习工作区格式

学习工作区用于长期学习复杂技能。它不是资料仓库，而是保存学习使命、真实任务、练习证据和复盘结果的地方。

工作区有两种形态：**单主题工作区** 和 **多轨道工作区**。默认从单主题开始；当用户同时维护多个长期学习方向时，再升级为多轨道。

## 单主题工作区

适合只学习一个主题，例如英语口语、TypeScript、写作、考试复习或一个源码项目。

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

### 各目录职责

- `MISSION.md`：学习指南针。
- `RESOURCES.md`：可信资源和真实练习锚点。
- `GLOSSARY.md`：已经掌握的共同语言。
- `NOTES.md`：用户偏好、背景、教学注意事项。
- `lessons/`：单节小课。
- `exercises/`：练习任务和用户输出。
- `reference/`：长期复习卡片。
- `assets/`：跨课程复用的模板、测验组件、评分表、练习脚手架或展示辅助。
- `learning-records/`：证据型学习记录。

## 多轨道工作区

适合用户把一个目录当作长期学习实验室，同时学习多个方向。例如技术、写作、语言、考试、项目阅读分别并行，但每次只推进其中一个轨道。

```text
learning-workspace/
  README.md
  MISSION.md
  TRACKS.md
  NOTES.md
  tracks/
    <track>/
      MISSION.md
      STUDY-PLAN.md
      RESOURCES.md
      NOTES.md
  lessons/
    <track>/
  exercises/
    <track>/
  reference/
    <track>/
  learning-records/
    <track>/
  assets/
  sources/
```

### 多轨道职责

- 根目录 `MISSION.md`：整个学习工作区的总使命，不写某一节课细节。
- `TRACKS.md`：所有学习轨道的状态、当前焦点、边界和下一编号。格式见 `TRACKS-FORMAT.md`。
- 根目录 `NOTES.md`：跨轨道用户偏好和协作规则。
- `tracks/<track>/MISSION.md`：该轨道为什么学、学到什么程度、服务什么目标。
- `tracks/<track>/STUDY-PLAN.md`：该轨道的短地图，只展开最近一个闭环。
- `tracks/<track>/RESOURCES.md`：该轨道可信资源、真实任务入口、考试范围或项目材料。
- `tracks/<track>/NOTES.md`：该轨道专属偏好、背景迁移和反复卡点。
- `lessons/<track>/`：该轨道单节小课。
- `exercises/<track>/`：该轨道练习、实验、题目、作品草稿或可验证输出。
- `reference/<track>/`：该轨道长期复习卡片、框架卡、流程卡和对照表。
- `learning-records/<track>/`：该轨道证据型学习记录。
- `assets/`：跨轨道复用的模板、测验组件、评分表、样式或练习脚手架。
- `sources/`：外部读本、项目、课程、平台或资料源登记，不复制大仓库源码。

## 什么时候升级到多轨道

满足任一条件时，建议升级：

- 用户有两个以上长期学习方向。
- 不同方向需要不同使命、资源、练习和复盘记录。
- 用户需要比较、冻结、恢复或切换学习主线。
- 单主题工作区已经开始混写不同主题，导致下一步判断变乱。

不要为了“看起来专业”提前升级。一个主题能解决，就保持单主题。

## 写入规则

- 懒创建。只有真正需要时才创建文件或目录。
- 多轨道工作区写入前先判断目标轨道；不确定时先问一个短问题或写入 `TRACKS.md` 的待定区。
- 每次只推进一个 30-90 分钟闭环，即使工作区里有多个轨道。
- 新课程写入 `lessons/<track>/`，练习写入 `exercises/<track>/`，复习材料写入 `reference/<track>/`，学习记录写入 `learning-records/<track>/`。
- 只有有证据的学习结果才进入 `learning-records/`。
- 长期复习材料进入 `reference/`，过程闲聊不进入。
- 可复用的样式、模板、评分表和练习组件进入 `assets/`，不要散落在每节课里。

## 边界

- 多轨道不是同时学很多东西的理由。它只是把长期学习现场整理清楚。
- `TRACKS.md` 负责导航和取舍，不替代每个轨道的 `MISSION.md`。
- `tracks/<track>/STUDY-PLAN.md` 只保留短地图，不生成宏大课程大纲。
- `sources/` 只登记外部来源，不把资料仓库搬进学习工作区。
