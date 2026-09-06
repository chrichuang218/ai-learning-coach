# mini-claude 缓存读本

- URL：https://github.com/chrichuang218/claude-code-from-scratch
- 本机路径：由教练准备或核对后填写；源码保留在独立开发目录。
- 版本：`bdb7e858ff9be8fbed82d0488e13a63b9b0e3288`
- 核验日期：2026-09-06（仅说明体验材料核验，不代表当前用户已执行）
- 入口：`test/skills.test.ts`、`src/skills.ts`。
- 测试：`cache reset makes a newly created skill discoverable`。

## 启动方式

参照 [首次体验](../../../first-session/README.md) 安装锁定依赖、编译并运行目标测试。测试不调用 provider API，不启动真实 Agent CLI。

## 学习范围

仅验证缓存发现、快照和失效机制；完成标准见使命。升级读本 commit 时重新核验 symbol 和测试，不修改历史证据。
