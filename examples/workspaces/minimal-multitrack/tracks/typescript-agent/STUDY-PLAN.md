# TypeScript Agent 短主线

## 当前真实锚点

追踪 memory prefetch 进入模型请求：

1. `src/memory.ts`：`startMemoryPrefetch()` 创建 handle。
2. `src/agent.ts`：`chatOpenAI()` / `chatAnthropic()` 检查并消费结果。
3. 消息数组修改后进入对应 SDK 调用。

只展开当前链路。后续入口根据用户在真实源码中的证据决定，不预排完整课程表。

## 当前掌握要求

- 能指出 Promise 在哪里创建。
- 能解释为什么启动时不 await。
- 能找到结果消费和消息修改位置。
- 能使用 Run 或 Debug 验证至少一个状态变化。
