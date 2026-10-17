# Learning Lab：查看、检查和继续

Learning Lab 是包含使命、证据和下一入口的 Markdown 学习档案。新用户可以从 [单轨道示例](../examples/workspaces/first-session/README.md) 开始；多轨道用户继续使用原来的结构。

## 标准库命令行

以下命令在 AI Learning Coach 仓库根目录运行，Python 3.10+；不依赖 MCP 或额外 Python 包。

```bash
python scripts/learning_lab.py snapshot /path/to/learning-lab
python scripts/learning_lab.py doctor /path/to/learning-lab
python scripts/learning_lab.py resume /path/to/learning-lab
python scripts/learning_lab.py review /path/to/learning-lab
python scripts/learning_lab.py weekly /path/to/learning-lab
python scripts/learning_lab.py sync /path/to/learning-lab
python scripts/learning_lab.py view /path/to/learning-lab --output /path/to/exports/progress.html
```

`review` 列出到期复习，`weekly` 输出最近 7 天的复盘草稿（加 `--output` 保存）。`sync` 是唯一会写入的命令：只重算 PROGRESS 中的派生数字（加权进度行、快照百分比、学习节奏），不改里程碑、证据或手写文字。

打开生成的 HTML 即可查看下一检查点、到期复习、能力与证据、最近进展、学习节奏。页面没有外部字体、脚本或网络请求，生成后是静态快照；记录变化后重新生成。覆盖已有导出时显式添加 `--force`，程序仍拒绝覆盖已知学习事实文件。

导出应放到学习档案之外；若要放在档案内部，仅允许 `.learning-coach-exports/` 目录。`--force` 也不能覆盖其他位置。缺少当前周的日历时节奏显示未知，不把未覆盖日期当成零活动。

`--as-of YYYY-MM-DD` 可复现某个日期的计算；默认使用本机日期。页面分别标明状态更新时间和节奏计算日期，避免把几天前的“连续 1 天”冒充今天的状态。当前连续天数允许今天尚未学习但昨天有记录的情况。

doctor exit 0 表示当前支持的检查未发现问题；exit 1 表示有诊断；exit 2 表示输入或读取失败。检查包括过期 README 日期、ETA 与节奏天数冲突、可用日历范围内的计数、失效本地记录链接、权重或快照矛盾、结构化证据与独立程度冲突。

这是领域数据检查，**不自动证明旧记录的学习结论正确**，也不会读取或验证读本的当前 Git 状态。`sourceVerification: not_checked` 提醒教练恢复前检查当前仓库、commit、symbol 和行号。根目录快照表示整个工作区，多轨道记录递归纳入；尚未提供独立的轨道筛选界面。

## 帮助程度和向后兼容

已有 Markdown 记录直接读取，缺少机器元数据时标记为 legacy；不会从措辞猜测帮助程度，也不会重写历史成绩。新技术学习证据可使用 [证据合同](../plugins/ai-learning-coach/skills/learning-coach/EVIDENCE-FORMAT.md) 中的 `learning-evidence` JSON 块，支持教练演示、提示下完成、独立完成、迁移验证。

帮助程度属于具体动作：“亲自运行教练给的测试”并不能证明“独立设计测试”。掌握状态仍由教练根据真实证据判断，读取层只负责计算和诊断。

百分比使用 PROGRESS 中约定的权重和状态重新计算；权重无效时返回待核对，不填零。原有只有“快照”的格式保留为 legacy_snapshot，明确其来源。历史日历已截断时仅核对可见窗口，不删除或归零更早的累计天数。

## 手动导出成果

选择一条含有效结构化证据的记录：

```bash
python scripts/learning_lab.py share /path/to/learning-lab --record learning-records/cache.md --output /path/to/exports/learning-result.md
```

只导出选中证据的动作、帮助、结果和待验证点；不读取 LEARNER-BACKGROUND 或任何聊天历史。常见本机路径和链接会替换为占位文字，发布前仍需预览并删除其他个人信息。代码链接由用户核对可公开性后手动添加。没有上传、社区发帖或通知操作。

## MCP 工具

MCP 服务器与命令行共用同一读取层，额外提供经过校验的写入：

| 工具 | 作用 |
| --- | --- |
| `get_learning_snapshot` / `doctor_learning_lab` / `get_resume_context` | 读取状态、诊断、续学上下文（含到期复习） |
| `get_review_queue` / `get_weekly_review` | 到期复习与 7 天复盘 |
| `record_evidence` | 校验后把一条证据追加到 `learning-records/`，不改变掌握状态 |
| `set_milestone_state` | 修改一个里程碑状态并链接记录；证据帮助程度不足时拒绝 |
| `sync_progress` | 重算 PROGRESS 中的派生数字 |
| `record_checkin` / `list_checkins` | 打卡写入 `.learning-coach/checkins.jsonl`，计入学习节奏，不改变掌握状态 |

旧版原型写在 `.learning-coach-prototype/checkins.jsonl` 的打卡继续被读取。没有手工日历时，学习节奏由最近活动、证据日期和打卡派生；已有手工日历继续有效。[MCP 配置及验证](../plugins/ai-learning-coach/mcp/README.md)
