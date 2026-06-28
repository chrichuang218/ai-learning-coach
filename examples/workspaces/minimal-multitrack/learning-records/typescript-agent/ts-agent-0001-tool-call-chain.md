# ts-agent-0001-tool-call-chain

## 主题

用最小 tool call 理解 Agent 执行链路。

## 目标

把 “Agent 会调用工具” 从抽象说法变成可解释的输入、执行、输出过程。

## 本轮动作

实现并运行一个 mock `getWeather` tool call。

## 证据

- 能说清 tool schema 描述参数。
- 能说清 handler 接收参数并返回结果。
- 能说清 result 需要回到后续消息或控制流。

## 真实卡点

容易把 schema 当成真正执行逻辑；实际上 schema 只是描述，handler 才执行。

## 影响

下一轮不急着学完整框架，先练 tool result 如何接回 agent message。

## 下一步

做一个 60 分钟闭环：把 tool result 包装成下一条 assistant/tool message。
