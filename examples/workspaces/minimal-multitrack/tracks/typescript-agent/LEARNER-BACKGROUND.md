# TypeScript Agent 学习者背景

## 用户画像

- 有 Java 经验。
- 目标是通过 mini-claude 掌握 TypeScript 与 Agent 开发。

## 已验证能力

- 能解释 Promise 是未来结果对象。
- 能解释 async 函数会返回 Promise。
- 能说明 await 只暂停当前 async 函数，不阻塞 JavaScript 主线程。
- 已使用基础 Debug 操作观察执行流。

## 有效教学方式

- 真实源码切片。
- 一次一个问题。
- 执行时间线、Run 与 Debug。
- Java 对照必须指出关键差异。

## 当前能力边界

- 尚未在真实 Agent 中独立追踪 Promise 的创建、状态和消费。

## 下一处真实入口

- `src/memory.ts`：`startMemoryPrefetch()`
