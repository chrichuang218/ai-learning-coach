# 追踪 memory prefetch 进入模型请求

状态：进行中
轨道：typescript-agent

## 为什么现在做

用户已掌握 Promise、async 和 await，但尚未把这些能力映射回 mini-claude 真实源码。

## 真实锚点

- `src/memory.ts`：`startMemoryPrefetch()`
- `src/agent.ts`：`chatOpenAI()`
- `src/agent.ts`：`callOpenAIStream()`

## 用户起点

已经证明：

- async 函数立即返回 pending Promise。
- await 暂停当前函数而非线程。
- 能解释 resolve / reject。

尚未验证：

- 能否独立追踪 Promise 的创建和消费。

## 教练的第一个动作

让用户打开 `src/memory.ts`，搜索 `startMemoryPrefetch`，只回答返回类型可能表达什么。

## 预计卡点

- `MemoryPrefetch | null`
- `Promise<RelevantMemory[]>`
- `settled` 与 `consumed`
- sideQuery 的来源

## 掌握证据

用户能够指出创建点、消费点、消息修改点和 SDK 调用点。

## 实际教学路径

Lesson 结束后补充。

## 结果

- 学习记录：课程结束后决定。
- 稳定知识：`reference/typescript-agent/promise-async-await.md`
- 下一处真实入口：课程结束后决定。
