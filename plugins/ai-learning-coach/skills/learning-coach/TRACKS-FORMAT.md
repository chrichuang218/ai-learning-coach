# TRACKS.md：多轨道总览格式

只有用户确实维护多个长期学习方向时才创建 `TRACKS.md`。它负责状态和取舍，不保存具体教学内容。

## 推荐模板

```markdown
# 学习轨道总览

## 当前主线

- 轨道：`{track}`
- 本周期现实结果：{...}
- 复盘触发器：{...}

## 轨道状态

| 轨道 | 状态 | 学习使命 | 最近证据 | 下一入口 |
| --- | --- | --- | --- | --- |
| `{track-a}` | 活跃 | {...} | {...} | {...} |
| `{track-b}` | 冻结 | {...} | {...} | {...} |

## 当前取舍

- 保留：{...}
- 最低维护：{可选}
- 冻结：{...}
- 重新评估条件：{...}
```

## 轨道目录

```text
tracks/<track>/
  MISSION.md
  LEARNER-BACKGROUND.md  # 可选
  STUDY-PLAN.md          # 可选
  RESOURCES.md           # 可选
  NOTES.md               # 可选
```

证据和知识按需写入：

```text
learning-records/<track>/
reference/<track>/
lessons/<track>/         # 仅可选教练 brief
```

不要在新增轨道时一次创建所有目录。

## 使用原则

- 一个周期只保留一条高成本主线。
- 主线选择和冻结由 `focus-coach` 处理。
- 具体带学由 `learning-coach` 处理。
- `TRACKS.md` 只记录当前决定和状态，不变成课程表。
- 恢复冻结轨道前先读取它的使命和最近学习记录，不机械从旧 lesson 编号继续。
