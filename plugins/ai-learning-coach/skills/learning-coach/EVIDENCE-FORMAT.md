# 可读取的学习证据

学习记录需要由状态工具读取、恢复、复习调度或导出时使用。普通对话和原有 Markdown 记录保持可用；只在真实证据出现后添加元数据，不批量猜测历史值。有 `learning-lab` MCP 时用 `record_evidence` 写入，它会校验字段和 ID 唯一性。

## 一个动作，一份帮助程度

同一记录可包含多个 `learning-evidence` JSON 块，每块对应一个已观察的动作。用户亲自运行教练提供的测试，动作应写“运行目标测试”，帮助程度通常为 guided；只有独立提出输入、观察点和断言并验证，才可能支持独立测试设计。

```learning-evidence
{
  "schema_version": 1,
  "id": "cache-2026-09-06-run-1",
  "observed_at": "2026-09-06",
  "milestone_id": "缓存失效",
  "action": "运行教练提供的目标测试，并比较缓存重置前后的输出",
  "assistance_level": "guided",
  "result": "目标测试通过；独立设计反向测试仍待验证",
  "source_ref": {
    "commit": "bdb7e858ff9be8fbed82d0488e13a63b9b0e3288",
    "path": "src/skills.ts",
    "symbol": "resetSkillCache"
  },
  "review_reason": "断言由教练提供，尚未证明独立测试设计",
  "next_action": "在修改已有 Skill 内容的相邻场景中预测并验证缓存行为",
  "review_after": "2026-09-09"
}
```

上面是格式示例，不是已发生的用户行为。写入时用真实日期、唯一 ID、实际观察和源码 commit。`milestone_id` 对应 PROGRESS 表中里程碑名称；尚未约定里程碑时使用具体能力名，后续保持一致。

| assistance_level | 含义 |
| --- | --- |
| demonstrated | 教练演示，用户尚未自己完成 |
| guided | 有提示、模板或共同操作 |
| independent | 无逐步提示完成这一个动作 |
| transferred | 在相邻新任务中独立使用并验证 |

这些取值描述帮助，不自动映射为掌握百分比。失败同样可以记录真实观察；不能因为元数据完整或 result 写着通过就升级能力。

## 来源类型

`source_ref.kind` 说明证据锚点，非技术学习同样可以写结构化证据：

| kind | 必填字段 | 适用 |
| --- | --- | --- |
| code（默认，有 `commit` 时可省略 kind） | `path`（仓库相对）、`symbol`、`commit`（完整 40 位） | 源码学习 |
| url | `url`（http/https） | 公开文章、题目、作品链接 |
| document | `title`，可选 `locator` | 本地文稿、讲义、书的章节 |
| task | `description` | 口语模拟、现实任务等没有文件的动作 |

代码仓库位置继续放在 sources。恢复时核对当前源码，再定位行号；历史 commit 与当前 HEAD 不同并不自动否定历史证据。

## 复习调度

`review_after`（YYYY-MM-DD，不早于 `observed_at`）表示这条边界最早何时复验。日期已到、且之后没有同一 `milestone_id` 的新证据时，这一项进入到期复习，恢复学习时优先处理。

- 提示下完成或刚纠正的误区：通常 1-3 天后复验；独立完成：约 1 周；迁移验证后一般不再安排。
- 复验得到的新证据（成功或失败）都写成新块，原有块不改；新证据自动结束旧的到期项。
- 只为确实需要保留的能力安排复习，不为凑间隔机械出题。

`review_reason` 保存需要复验的边界，`next_action` 保存一个可观察动作；最近状态仍以 PROGRESS 的下一检查点为入口，二者冲突时先查日期和实际证据。复验失败应写清观察与调整依据，不因空白学习日自动降级。

元数据属于 record 正文的一部分，派生索引可以重建，不建立第二套可独立改写的掌握数据。缺少元数据的旧记录按正文判断，不把 unknown 帮助程度默认为 independent。
