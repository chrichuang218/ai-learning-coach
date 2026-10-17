# Release Acceptance

当前候选版本：`2.2.0`
最近执行日期：2026-10-17
Codex CLI：`0.144.1`（CI 基线）；本机安装冒烟使用 `0.160.0`
状态：PASS（2.2.0 工程发布验收；学习效果不作承诺）

## 本次发布范围

经过校验的状态写入（证据、里程碑状态、派生进度、打卡）、间隔复习与周复盘、非代码证据、英文 Learning Lab、uv 启动的 MCP、Claude Code 插件清单、起步路线目录、精简后的 learning-coach Skill 与自动行为评估脚本。Markdown 仍是事实源。

## 发布验证

- 仓库静态校验：Codex 与 Claude Code 清单、两份 MCP 启动配置、Skill 合同、链接、空白字符与版本一致性。
- Learning Core / 写入 / 导出：34 项确定性测试，其中 11 项覆盖写入拒绝规则、派生节奏、复习队列、周复盘、英文档案与非代码证据。
- MCP 十工具往返：进程内启动，以及完全按 Codex（`.codex-mcp.json`）和 Claude Code（`.mcp.json`）配置经 uv 启动。
- Codex 隔离安装：插件缓存文件齐全，并在已安装缓存中按 uv 真实启动方式跑通十个工具；`codex mcp list` 确认只注册声明的 `learning-lab` 服务器。

## 行为与证据边界

- 自动行为评估三轮记录见 [2026-10-17 自动评估](../docs/validation/2026-10-17-auto-evals.md)：第一轮 12 场景 89%，失败主要来自 Windows 沙箱无法读取 Skill；修正提示方式与 Skill 后，复跑的 3 个场景 9/9。其余 8 个场景未在最终 Skill 上复验。
- 作答与评分为同一模型，结论需人工抽查；这是 context-only 探针，不代表真实文件读写或真人教学。
- 未验证：Claude Code 的实际插件安装流程、真实 Codex 对话中的 MCP 调用（`codex_mcp_demo_smoke.py`）、Cursor / Gemini CLI 等手动配置、起步路线中除 TypeScript Agent 外各仓库的运行命令。真人学习效果、七日复用和 Star 增长不属于已验证结论。

[2.1.0 历史验收](history/2.1.0-release-checklist.md) 与 [2.0.3 历史验收](history/2.0.3-release-checklist.md) 保留原样，不作为本版本的运行结果。
