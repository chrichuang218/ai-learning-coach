# Contributing

AI Learning Coach 最需要的贡献不是更多教学口号，而是真实失败案例、可复现行为、跨领域适配和能阻止回归的 eval。

## 最有价值的贡献

- **触发问题**：该调用 `learning-coach` 却没有触发，或与 `focus-coach` 路由错误。
- **教学回归**：让用户选文件、一次展示完整任务卡、默认生成 lesson/HTML、忽略真实项目。
- **真实卡点案例**：某种解释为什么没有帮助，什么动作最终改变了理解。
- **跨领域适配**：语言、考试、写作、研究、职业技能中的真实锚点和反馈机制。
- **评估用例**：一个现实 prompt、预期行为和明确失败信号。
- **文档改进**：让用户更快理解、安装和验证 Skill。

## 提交 Issue

优先使用仓库的 Issue 表单。一个好的行为问题应包含：

1. 用户原始请求。
2. 当时可用的学习背景或工作区信息。
3. 实际响应。
4. 期望行为。
5. 为什么实际行为会浪费学习时间或破坏私人教练体验。

删除 API key、公司代码、私人路径、真实姓名和其他敏感信息。可以把项目和变量替换成最小匿名版本，但要保留导致行为差异的结构。

## 修改原则

- 用户不是课程设计师。
- 真实项目、作品、题目或任务优先。
- 教练后台可以复杂，用户前台一次只看到一个动作。
- 具体问题先直接回答。
- Lesson 是实时辅导过程，文件只是可选教练 brief。
- 证据决定掌握，不靠“我懂了”。
- 新规则要说明为什么，避免堆叠僵硬的 ALWAYS/NEVER。
- 优先修改最小职责边界，不把战略判断重新塞进 `learning-coach`。

## 新增训练模式

修改 `COACHING-MODES.md` 时，请说明：

- 它解决哪类可观察卡点。
- 第一个用户可见动作是什么。
- 什么证据表示应停止。
- 什么时候不应使用。
- 它与现有模式有什么不同。

训练模式不能成为每轮必须执行的固定流程。

## 新增领域适配

不要只替换名词。请明确：

- 该领域的真实锚点。
- 最快、可信的反馈来源。
- 掌握证据是什么。
- 哪些动作只能在真实世界验证。
- 它何时应交给 `focus-coach` 做战略取舍。

同时为 `evals/cross-domain-smoke-prompts.md` 增加一个现实用例。

## 本地验证

安装 Python 依赖：

```bash
python -m pip install pyyaml
```

运行仓库校验：

```bash
python scripts/validate_repo.py
```

安装了 Codex CLI 时，再运行隔离 marketplace 冒烟：

```bash
python scripts/release_smoke.py
```

人工检查相关 eval：

- `evals/learning-coach-smoke-prompts.md`
- `evals/cross-domain-smoke-prompts.md`
- `evals/focus-coach-smoke-prompts.md`
- `evals/release-checklist.md`

## Pull Request 清单

- [ ] 修改解决了一个清楚的问题。
- [ ] Skill 职责边界没有变模糊。
- [ ] 没有恢复固定时长、完整任务卡或默认 HTML lesson。
- [ ] 新行为有对应示例或 eval。
- [ ] 本地校验通过。
- [ ] 修改插件结构或发布行为时，隔离 marketplace 安装冒烟通过。
- [ ] 文档没有包含敏感信息。
