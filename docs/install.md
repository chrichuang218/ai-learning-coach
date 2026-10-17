# 安装与验证

AI Learning Coach 是一个插件，包含 learning-coach 和 focus-coach。Learning Lab 是你自己的学习档案，可按需创建，不需要安装第二个产品。

## 主入口：Codex plugin

```bash
codex plugin marketplace add chrichuang218/ai-learning-coach
codex plugin add ai-learning-coach@ai-learning-coach
```

安装后新开一个会话，再说“开始学习 TypeScript”。需要明确指定时说“使用 $learning-coach 带我开始”。升级说明见 [MIGRATION-v2](../MIGRATION-v2.md)。

也可以把仓库链接发给 Codex，让它完成插件安装。公共仓库命令安装远端已发布版本；本地候选改动需使用下面的本地入口验证，不能把本地测试结果当作远端已发布。

## 本地候选版本

从当前源码运行隔离安装验证，它使用临时 CODEX_HOME，不改变日常插件配置：

```bash
python scripts/release_smoke.py
```

需在日常环境试用本地源码时，在新会话中让 Codex 从本仓库绝对路径安装；以下是手工命令：

```bash
codex plugin marketplace add /absolute/path/to/ai-learning-coach
codex plugin list --json --marketplace ai-learning-coach --available
codex plugin add ai-learning-coach@ai-learning-coach
```

如果已登记同名 marketplace，先查看当前状态和 CLI 提示，确认来源；不要清空整个插件缓存或删除其他插件。

## Claude Code plugin

```bash
claude plugin marketplace add chrichuang218/ai-learning-coach
claude plugin install ai-learning-coach@ai-learning-coach
```

也可在 Claude Code 会话中运行 `/plugin marketplace add chrichuang218/ai-learning-coach`，再用 `/plugin` 安装。两个 Skill 与 Codex 版相同；MCP 由插件根目录的 `.mcp.json` 通过 `${CLAUDE_PLUGIN_ROOT}` 启动。Claude Code 的插件安装尚未进入本仓库的自动安装冒烟；CI 只验证该配置能启动服务器并跑通全部工具。

## 其他 Agent（Cursor、Gemini CLI、OpenCode 等）

这些客户端可以只装 Skill：把 `plugins/ai-learning-coach/skills/` 下的两个目录复制到客户端读取 Skill 的位置，或使用下文 skills.sh 命令并把 `--agent` 换成对应客户端。需要状态工具时，在客户端的 MCP 配置中添加一个 stdio 服务器：

```json
{
  "command": "uv",
  "args": ["run", "--quiet", "--script", "/absolute/path/to/ai-learning-coach/plugins/ai-learning-coach/mcp/server.py"],
  "env": {"PYTHONUTF8": "1"}
}
```

这些客户端未经本仓库测试；Skill 本身是普通 Markdown，没有 MCP 时教练按文件完成同样的工作。

## Learning Lab 状态工具（MCP）

插件自带 `learning-lab` MCP 服务器：读取状态、诊断、续学、到期复习、周复盘，以及经过校验的写入（证据、里程碑状态、派生进度、打卡）。它通过 [uv](https://docs.astral.sh/uv/) 启动，uv 会自动准备 Python 和固定依赖 `mcp==1.27.0`，不需要手动 `pip install`：

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

装好 uv 后重开会话。纯 Skill 教学用文件工具即可完成；命令行与 HTML 导出只用 Python 标准库：

```bash
python scripts/learning_lab.py doctor /path/to/learning-lab
```

完整说明见 [Learning Lab 工具](learning-lab.md)。

## 安装形态的边界

| 入口 | 内容和验证边界 |
| --- | --- |
| 本仓库 Codex marketplace plugin | 包含两个 Skill、参考文档和 MCP 服务器；本地安装冒烟检查插件缓存文件，并在 uv 可用时按真实启动方式跑通工具。验证基线为 CLI 0.144.1。 |
| 本仓库 Claude Code marketplace plugin | 同一插件目录，`.claude-plugin/` 提供清单；MCP 启动配置经 CI 验证，插件安装流程尚未自动化验证。 |
| skills.sh 的 `npx skills add` | 属于独立 Skill 分发入口。已用 skills@1.5.23 在隔离项目验证本地候选的两个 Skill 及参考文档可完整复制；不会安装 plugin manifest 或注册 MCP。远端目录当前版本不由此测试保证。 |

复现本地 Skill-only 安装（在新的隔离项目中，替换为实际源码绝对路径）：

```bash
npx --yes skills@1.5.23 add /absolute/path/to/ai-learning-coach/plugins/ai-learning-coach/skills --agent codex --skill focus-coach learning-coach --copy --yes
```

该命令在项目 `.agents/skills/` 放置两个 Skill；`RESUME.md`、`EVIDENCE-FORMAT.md` 已比对与源文件一致。它不等同于 marketplace 的完整插件安装，不需要为其假设 MCP 能力。

平台支持以实际测试为准。官方插件说明建议安装后开始新会话；可用界面及组织限制请参照 [OpenAI Plugins 文档](https://developers.openai.com/codex/plugins)（2026-09-06 核对）。

## 卡住时

- `codex` 命令找不到：先按 [官方 CLI 安装文档](https://developers.openai.com/codex/cli) 配置客户端。
- 已安装却不触发：新开会话，明确指定 `$learning-coach`，并提供当前项目或学习目标。
- 读本测试失败：保留错误输出，使用首次体验固定版本；每次修改 TS 后重新编译。
- MCP 工具不出现：确认 `uv --version` 可用，然后重开会话；企业网络需能访问 PyPI 以下载 `mcp`。
- doctor 返回 warning：阅读具体文件和原因；它不会自动改写证据。缺少 PROGRESS 对一次短学习并不致命，长期状态工具才需要它。
- 仍有问题：提交 [首次体验反馈](https://github.com/chrichuang218/ai-learning-coach/issues/new?template=first_experience.yml)，说明卡在哪一步。
