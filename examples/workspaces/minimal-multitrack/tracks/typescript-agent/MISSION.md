# Mission: 通过 mini-claude 学 TypeScript 与 Agent

## Why

学习者有 Java 经验，希望通过真实 coding agent 源码建立 TypeScript 和 JavaScript 运行时心智，而不是先背完整语法表。

## Success looks like

- 能从 `src/cli.ts` 进入 `Agent.chat()` 并追踪模型请求。
- 能解释常见类型边界、消息结构和 async 控制流。
- 能用 Run 与 Debug 验证预测。
- 能在理解边界后完成低风险修改。

## Completion criteria

- 能在不依赖逐步提示时追踪一条新的 Agent 链路并解释类型与运行时边界。
- 能完成一个低风险跨模块修改，并用测试、Run 或 Debug 验证结果。
- 不要求读完 mini-claude 每个文件，也不以 lesson 数量作为完成标准。

## Constraints

- 真实项目默认只读。
- 一次只追一条控制流、数据流或类型关系。
- 不默认生成 HTML lesson 或玩具练习。

## Out of scope

- React。
- 高级类型体操。
- 尚未理解当前单 Agent 链路前的复杂多 Agent 架构。
