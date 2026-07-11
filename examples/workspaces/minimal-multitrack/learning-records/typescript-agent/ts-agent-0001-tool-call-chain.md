# 能解释 Tool Call 结果必须回填消息历史

日期：2026-07-12
真实锚点：mini-claude tool call loop
贡献等级：`█`
推进里程碑：Agent 消息、工具与 memory 链路；Tool call / result 生命周期

## 本轮结论

用户已经理解：工具结果只打印到终端不会改变模型上下文，必须以 provider 要求的消息结构回填 history。

## 掌握证据

- 能解释 tool call 的参数解析、权限判断、执行和结果回填顺序。
- 能指出 OpenAI 的 `role: "tool"` 与 Anthropic 的 `tool_result` 只是 DTO 形状不同。
- 能说明 call id 为什么必须与前面的工具调用对应。

## 真实卡点与纠正

- 原模型：工具已经执行并打印，模型应该自然知道结果。
- 纠正：通过下一轮消息历史观察，确认终端输出不属于模型输入。

## 后续可默认

- 工具执行闭环和消息历史回填的基本目的。

## 能力边界

- 尚未独立追踪并发工具与 streaming early execution。

## 下一处真实入口

- `src/memory.ts`：`startMemoryPrefetch()`
