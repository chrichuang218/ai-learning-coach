# 缓存失效体验：工程复现记录

核验日期：2026-09-06。此结果由自动化执行，验证安装、源码和测试可复现性，尚未进行真人首次体验或留存验证。

固定源码：[bdb7e858ff9be8fbed82d0488e13a63b9b0e3288](https://github.com/chrichuang218/claude-code-from-scratch/tree/bdb7e858ff9be8fbed82d0488e13a63b9b0e3288)。匿名 commit API 返回 HTTP 200，独立公开 clone 成功。

环境：Windows、Git 2.54.0.windows.1、Node 24.15.0、npm 11.12.1、TypeScript 5.9.3。`npm ci --ignore-scripts --no-audit --no-fund` 使用独立空 npm 缓存成功；这不代表代理或 CDN 无缓存。

| 步骤 | 结果 |
| --- | --- |
| 编译测试源码 | exit 0 |
| 原实现的精确缓存测试 | tests 1 / pass 1 / fail 0 |
| 隔离副本中让 resetSkillCache 成为 no-op，重新编译 | exit 0 |
| 同一目标测试 | tests 1 / pass 0 / fail 1；新 Skill 的 source 为 undefined，期望 user |
| 恢复原字节并重新编译 | tests 1 / pass 1 / fail 0 |
| 最终源码 diff | 空 |

变异只影响独立副本，结束时恢复。原学习读本与学习档案未被此核验修改。编译与目标测试没有调用 provider API；教练自身的账户和费用另计。

完整运行命令见 [首次体验](../../examples/first-session/README.md)。每次 TypeScript 修改后需重新编译，不能用旧 JS 证明新代码通过。测试命令只选择一个精确名称，不用完整测试套件的其他失败充当目标 Red。

本机公开 clone 用时约 6.8 秒，空 npm 缓存安装约 9 秒；这属于机器执行耗时，不能据此承诺学习者在相同时限内完成。
