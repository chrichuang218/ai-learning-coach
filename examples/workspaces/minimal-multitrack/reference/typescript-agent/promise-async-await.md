# Promise、async 与 await

状态：稳定

## 一句话心智模型

> Promise 是未来结果对象；`async` 让函数返回 Promise；`await` 只暂停当前 async 函数，不阻塞 JavaScript 主线程。

## 易错点

- Promise 不是线程。
- `async` 不会自动创建后台线程。
- 普通函数只要返回 Promise，也可以被 `await`。
- 调用 async 函数时会立即执行到第一个未完成的 `await`，然后返回 pending Promise。
- Debug 断点可能改变 timer 的观察顺序。

## 真实项目映射

- `src/memory.ts`：`startMemoryPrefetch()` 立即返回包含 pending Promise 的 handle。
- `src/agent.ts`：模型调用循环只在 `settled && !consumed` 时消费结果。

## 复习问题

1. 为什么 `const p = recallMemory()` 能立刻得到 Promise？
2. `await delay()` 暂停了谁？
3. `settled` 与 `consumed` 分别回答什么问题？
