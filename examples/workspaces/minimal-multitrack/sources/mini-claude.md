# mini-claude 源码读本

- 类型：本地 Git 项目
- URL：https://github.com/Windy3f3f3f3f/claude-code-from-scratch
- 本机路径：`待配置`
- 版本：`commit 5e674776c12833edf5c8819d752416179a1d500f`
- 核验日期：2026-07-12
- 技术栈：TypeScript 5.8、Node.js、Anthropic SDK、OpenAI SDK
- 当前用途：通过真实 coding agent 学习 TypeScript、Agent 主循环、工具调用、memory、session、skills 和 MCP

## 选择理由

- 代码规模较小，CLI、模型调用、工具和 memory 边界清楚，适合有 Java 经验的 TypeScript 学习者逐条验证。

## 启动方式

- `npm install`
- `npm run build`
- `npm start`

## 推荐入口

- `src/cli.ts`：CLI 与 Agent 入口
- `src/agent.ts`：模型请求、消息历史和 tool loop
- `src/memory.ts`：memory prefetch 与注入
- `src/tools.ts`：工具定义与执行

## 已知约束

- 运行真实模型请求需要配置 provider API key，学习源码和静态 build 不依赖付费调用。
- 本示例固定到上述 commit；上游更新后先重新核验入口，再更新版本和日期。

## 学习范围

- CLI 到 Agent 的主调用链。
- OpenAI / Anthropic 模型请求与消息历史。
- Tool call / result 生命周期。
- Memory prefetch 的启动、消费与注入。
- Session、skills 和 MCP 的一条代表性链路。
- 一个可验证的跨模块低风险修改。

不要求读完所有文件、覆盖所有 provider 细节或掌握仓库外的复杂多 Agent 架构。

## 项目学习完成标准

- 能独立从入口追踪以上链路，解释关键类型和运行时状态。
- 能用 Run 或 Debug 验证至少一个异步或消息流预测。
- 能完成一个低风险跨模块修改并运行目标测试或最小冒烟。
