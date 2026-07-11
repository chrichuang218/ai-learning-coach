# TypeScript、异步与 Debug 能力基线

日期：2026-07-12
真实锚点：mini-claude 的 CLI、模型消息与 memory prefetch 链路
贡献等级：`█`
推进里程碑：TypeScript 运行时与类型边界；模块、工具链与 Debug；异步与并发心智模型；CLI 到 Agent 主链路；模型请求与消息历史；Memory prefetch 注入

## 本轮结论

用户已经形成 TypeScript 基础、Promise/async/await 和 Debug 的稳定能力；在教练提示下能够进入 mini-claude 的 CLI、模型消息与 memory prefetch 链路，但尚未在新位置独立迁移。

## 掌握证据

- 能解释 TypeScript 类型在编译期工作，JavaScript 运行时值仍需真实检查。
- 能独立 build、run，并使用断点、Step Over、Step Into、变量和调用栈验证控制流。
- 能在运行前预测 Promise 启动、`await` 暂停与恢复顺序，再用 Run 和 Debug 对照事实。
- 在提示入口后，能从 `src/cli.ts` 进入 `Agent.chat()`，找到 provider 分支和模型调用前的消息历史。
- 能解释 memory prefetch 提前启动的目的，并识别 `settled` 与 `consumed` 是两个不同状态。

## 真实卡点与纠正

- 原模型：`await` 会像 Java `Thread.sleep()` 一样阻塞线程。
- 纠正：通过 timer 输出和断点观察，确认它只暂停当前 async 函数的后半段。
- 原模型：类型断言会验证运行时输入。
- 纠正：通过外部消息与 JSON 边界确认 `as` 只改变编译期视角。

## 后续可默认

- Promise、async、await、基础模块和 Debug 操作不需要从定义重讲。
- 可以直接使用消息历史、pending Promise、settled 和 consumed 作为共同语言。

## 能力边界

- CLI、模型消息和 memory 链路仍需要入口提示，尚未达到独立状态。
- 尚未完成跨模块修改或迁移验证。

## 下一处真实入口

- `src/memory.ts`：`startMemoryPrefetch()`
- `src/agent.ts`：`chatOpenAI()` / `chatAnthropic()`
