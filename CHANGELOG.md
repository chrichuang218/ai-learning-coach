# Changelog

## 2.0.1 - 2026-07-23

### Fixed

- 每次创建或更新 learning record 后检查是否应将稳定知识提升或合并到 reference，避免沉淀长期滞后。
- reference promotion 使用证据质量和复用价值判断，不再让 record 数量隐式充当创建阈值。

### Added

- 为 learning record 增加已沉淀、候选及无需沉淀三种 Reference 状态。
- reference 与支撑 records 双向追踪；已有同主题文档优先更新，未稳定候选保留缺失证据。
- 稳定知识中的项目映射使用项目标识和仓库相对路径，设备绝对路径集中到 source 登记。
- 增加 promotion 行为回归场景和静态契约校验。

## 2.0.0 - 2026-07-12

### Changed

- 将 `learning-coach` 重构为主动备课、高频现场带学的私人教练。
- 将 `focus-coach` 收缩为低频战略取舍与阶段复盘教练。
- 将 lesson 正式定义为实时辅导过程，lesson 文件改为可选 Markdown 教练 brief。
- 真实项目、作品、题目和任务优先；必要时只使用一次性临时诊断实验。
- 默认一次只展示一个动作或问题，不再固定输出完整任务卡。
- 使用最低充分证据判断掌握，避免仪式化测验。
- 增加过期路径、旧 study plan 和用户最新偏好的冲突处理。

### Added

- 标准 Codex plugin manifest：`plugins/ai-learning-coach/.codex-plugin/plugin.json`。
- 仓库 marketplace 清单：`.agents/plugins/marketplace.json`。
- `plugins/ai-learning-coach/skills/learning-coach/LESSONS.md`
- `plugins/ai-learning-coach/skills/learning-coach/COACHING-MODES.md`
- `plugins/ai-learning-coach/skills/learning-coach/LEARNING-SCIENCE.md`
- `plugins/ai-learning-coach/skills/learning-coach/REFERENCE-FORMAT.md`
- `plugins/ai-learning-coach/skills/learning-coach/LEARNER-BACKGROUND-FORMAT.md`
- v1 到 v2 迁移指南。
- 跨语言、考试、写作、研究和职业技能的示例与 eval。
- 按需创建产物的多轨道示例工作区。
- 纯 Markdown `PROGRESS.md` 进度系统，分开显示目标能力和项目学习范围。
- 基于 learning record 的贡献日历、连续学习、最近成就和 ETA 置信度。
- 隔离 `CODEX_HOME` 的 marketplace 安装冒烟和 2.0 发布验收清单。

### Progress integrity

- 出勤、阅读时间、lesson 数量和文件数量不直接提高掌握进度。
- 掌握状态使用未开始、接触、需提示、独立、迁移验证五级证据。
- ETA 使用剩余有效学习小时、每周节奏、周区间和置信度，不承诺虚假精确日期。

### Removed

- 仓库根目录重复维护的 Skill 目录；两个 Skill 以插件内目录为唯一真源。
- 将 `exercises/` 作为标准学习产物和长期目录的设计。
- 固定 30-90 分钟闭环要求。
- lesson 是主要文件交付物的定义。
- 默认 HTML lesson/reference。
- 每次必须输出任务、验收标准和失败反馈的固定格式。

## v1

- 建立项目牵引学习、证据复盘和多轨道工作区。
- 引入错误驱动、钥匙句、掌握度检测、思考过程审查、高压演练和反向教学等训练模式。
