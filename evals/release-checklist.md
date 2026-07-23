# Release Acceptance

当前候选版本：`2.0.1`
最近执行日期：2026-07-23
Codex CLI：`0.144.1`
状态：PASS（发布候选验证）

## 自动验证

- [x] `python scripts/validate_repo.py`
- [x] `quick_validate.py`：`learning-coach`
- [x] `quick_validate.py`：`focus-coach`
- [x] `python scripts/release_smoke.py`
- [x] `git diff --check`
- [x] reference promotion 新旧 skill 对比：旧版 6/8，候选版 8/8

## 行为验收

| 场景 | 预期 | 结果 |
| --- | --- | --- |
| 已有工作区时开始学习 | 读取真实项目，只给一个动作或问题 | PASS：直接进入 `chatAnthropic()` 的 memory prefetch 单一问题 |
| 用户连续追问一个异步概念 | 直接回答并换维度，不展开完整课程 | PASS：使用命名展开、时间线和 Java 对照，最后只留一个判断问题 |
| 用户查看目标、项目进度和 ETA | 分开进度，说明区间、节奏与置信度 | PASS：返回 55% / 15%、小时与周区间，并说明低置信度 |
| 只有低强度出勤 | 更新活动与日历，不伪造 learning record 或掌握上涨 | PASS：只更新 progress，明确不写 record、不改变百分比 |
| 多目标且已有现实目标 | focus-coach 做明确取舍并及时退出 | PASS：选择 TS + mini-claude，冻结算法与多 Agent，定义月底证据 |
| 多目标且缺少决定性背景 | 只问一个短问题或明确临时假设 | PASS：明确声明无面试、无交付期限的临时假设和改线条件 |
| 多条同主题 records | promotion 检查后合并为一篇稳定 reference | PASS：三条 Agent 消息记录合并，reference 与 records 双向追踪 |
| 多条无关或冲突 records | 不按数量补 reference，保留候选缺失证据 | PASS：拒绝 5:5 对齐，冲突主题写入候选状态 |
| 已有同主题 reference | 优先更新，不创建重复文档 | PASS：Promise 迁移证据合并到原 reference |
| 单条强证据 record | 证据充分时允许直接 promotion | PASS：解释、Run、Debug 与迁移足以创建 reference |

Forward tests 使用独立新 agent 读取候选 Skill；测试 prompt 只提供用户场景，不提供预期答案。

## 发布条件

- 自动验证全部通过。
- 行为验收全部通过，没有 P1/P2 未解决发现。
- `CHANGELOG.md`、plugin manifest 和 Git tag 使用同一版本。
- 发布提交不包含私人路径、密钥、临时文件或无关改动。
