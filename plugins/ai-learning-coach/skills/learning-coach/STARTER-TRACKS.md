# 起步路线目录

用户方向明确、但没有自己的项目时，先从这里选一个候选，再按 [RESOURCES-FORMAT.md](RESOURCES-FORMAT.md) 现场核验，不从零搜索。用户已有项目时不使用本目录。

## 使用规则

- 每条路线固定一个 commit、一个首个入口和一个可观察动作。首次使用时核对仓库、commit、文件和 symbol 仍然存在，再登记到 `sources/<project>.md`。
- “运行”列是该仓库的常规命令，**只有 TypeScript Agent 路线经过本仓库的工程验证**；其他路线首次运行失败时，按真实报错处理，不改称已验证。
- 只推荐一条主路线；用户目标不在下表时，按 RESOURCES-FORMAT.md 现场寻找，不硬套。
- 表中 Star 和维护状态只说明核验当天的情况（2026-10-17），不作为推荐理由。

## 路线

| 方向 | 仓库与固定 commit | 首个入口 | 首个动作 | 运行 |
| --- | --- | --- | --- | --- |
| TypeScript / Agent | [claude-code-from-scratch](https://github.com/chrichuang218/claude-code-from-scratch) `bdb7e858ff9be8fbed82d0488e13a63b9b0e3288` | `src/skills.ts` 的 `resetSkillCache` | 预测新增 Skill 后第二次发现调用的结果 | 见 [首次体验](https://github.com/chrichuang218/ai-learning-coach/blob/main/examples/first-session/README.md) |
| Python / 机器学习基础 | [karpathy/micrograd](https://github.com/karpathy/micrograd) `7bc720e951fe422b8f8814aa5aa1b64121d26b4c` | `micrograd/engine.py` 的 `Value.backward` | 先手算 `a*b+c` 各节点梯度，再运行比较 | `pip install torch pytest` 后 `pytest test` |
| Python / 后端安全 | [pallets/itsdangerous](https://github.com/pallets/itsdangerous) `672971d66a2ef9f85151e53283113f33d642dabd` | `src/itsdangerous/signer.py` 的 `HMACAlgorithm.get_signature` | 预测改动一个字节后验签的结果和异常类型 | `pip install -e . pytest` 后 `pytest tests` |
| Go / Web 路由 | [go-chi/chi](https://github.com/go-chi/chi) `3a33ba578e0dd93444e0ff386cc26e665d92e31e` | `tree.go` 的 `(*node).findRoute` | 预测 `/users/{id}` 与 `/users/me` 的匹配优先级 | `go test ./...` |
| 前端 / TypeScript 状态管理 | [pmndrs/zustand](https://github.com/pmndrs/zustand) `d7a5583cffd80af515f7dfb69583c95cbdc9e2ce` | `src/vanilla.ts` 的 `createStoreImpl` 与 `setState` | 预测 `replace` 为 true / false 时订阅者收到的状态 | `pnpm install` 后 `pnpm test:spec` |
| Rust / 网络与异步 | [tokio-rs/mini-redis](https://github.com/tokio-rs/mini-redis) `3d93b42bc363220f85af4fc9e1bebd35b588a4a3` | `src/frame.rs` 的 `Frame::check` 与 `Frame::parse` | 预测半个 RESP 帧到达时 `check` 返回什么 | `cargo test` |

## 选择方式

1. 先按用户已会的语言和目标找最近一行；Java 后端转 TypeScript / Agent 默认第一行。
2. 用一句话说明为什么选它，以及第一次要观察什么；不展示整张表。
3. 用户已有经验高于入口难度时，跳到同一仓库更深的入口，不换仓库。
4. 登记 sources 时写明核验日期和实际运行结果；运行前不写“可运行”。
