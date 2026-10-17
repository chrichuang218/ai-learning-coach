# 评估与复现

评估分三层，分别回答不同问题。

## 不调用模型的工程验证

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
python -m pip install -r plugins/ai-learning-coach/mcp/requirements.txt
python scripts/mcp_demo_smoke.py
python scripts/mcp_demo_smoke.py --use-config codex    # 需要 uv
python scripts/mcp_demo_smoke.py --use-config claude   # 需要 uv
python scripts/release_smoke.py --protocol
```

它们验证文件合同、状态计算与写入拒绝规则、兼容性、两种宿主启动配置下的 MCP 全工具往返和隔离安装。[首次体验核验](../docs/validation/first-session.md) 另验证公开固定源码和真实目标测试。

## 教练行为探针

[scenarios.json](scenarios.json) 保存 12 种真实类型的场景、输入上下文和判据。

### 自动运行

```bash
python scripts/run_behavior_evals.py --ids 1 9          # 默认用 codex exec 作答并评分
python scripts/run_behavior_evals.py --agent-cmd "claude -p" --judge-cmd "codex exec --skip-git-repo-check --sandbox read-only --color never -"
```

每个场景由 Agent CLI 作答，再由评分命令逐条判断断言；结果按 `grading.json` 格式写入新目录，总通过率低于 `--min-pass-rate`（默认 0.8）时退出码为 1。作答和评分最好用不同模型，减少自评偏差；这些调用会消耗对应账号的额度。GitHub Actions 的 Behavior evals 工作流在修改 Skill 的 PR 和手动触发时运行，仓库未配置 `OPENAI_API_KEY` 时自动跳过。

### 手动对照

准备独立候选与旧版本输入包：

```bash
python scripts/prepare_behavior_evals.py --output /path/to/new-eval-run --baseline /path/to/old-learning-coach --ids 1 2
```

去掉 `--ids` 准备全部场景。脚本只准备数据，不偷偷调用付费模型。每个 `prompt.txt` 交给一个独立新会话或评估 agent，按指定路径保存输出；候选与旧版采用同一模型和设置。只给模型 prompt 包，不把 assertions 当答案提示。可使用当前已有的 Codex CLI 执行能力或代理运行。

每个 run 保留：模型与设置（可获得时）、插件版本、输入包、原始 response、逐条判据及证据。缺失 token/耗时写 unknown，不能估造。判据包含语义判断，应人工抽查，不能仅靠关键词或同一模型的自评。

该输入包是 **context-only behavior probe**：观察如何选择下一步和处理证据边界，不能代替实际文件读写、冷启动或真人教学。示例上下文属于测试 fixture，不是新的用户学习事实。既有完整行为标准见 [rubric](learning-coach-rubric.md)；旧发布结论保留在 [历史验收](history/)。

本次已运行两组新旧对照，原始输出、逐条判据及边界见 [2026-09-06 验证记录](../docs/validation/2026-09-06-improvements.md)。未运行的场景保持未验证。

## 真人首次体验

邀请自愿参与者走 [首次体验](../examples/first-session/README.md)，记录是否完成有效动作、失败步骤、真实耗时及七天内是否回来。建议先收集五份，区分作者陪跑与自主使用。

工程通过和行为评分都不等于学习成效。只有真实学习者的独立或迁移行为能支持相应结论；Star、安装次数和生成的文件数不作为能力证据。
