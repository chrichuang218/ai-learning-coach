# 第一次体验：为什么新增 Skill 后，程序仍读到旧内容？

适合已有 Java、Python 或其他编程经验，想开始读 TypeScript / Agent 源码的开发者。预留约 15 分钟进行学习，首次下载依赖的时间另计；节奏由你的回答决定。

这次使用真实 mini-claude 的缓存测试。完成后，你会留下自己的预测、运行观察、获得的帮助和下一次入口。**跑通测试只证明环境就绪。**

## 先让教练带你开始

在已安装插件的新会话中，粘贴：

```text
带我完成 AI Learning Coach 的缓存失效首次体验。
先读取 examples/first-session/COACH-BRIEF.md 和真实源码，替我准备独立读本目录。
我有后端开发经验，希望学 TypeScript 和 Agent。先让我作出一个预测，再运行验证。
```

该相对路径属于本仓库；若当前打开的是其他项目，请把本页或仓库 URL 一并发给教练。已经有明确读本时先询问是否用此独立体验，不替换正在学习的项目。

## 环境准备

已验证：Windows、Node.js **24.15.0**、npm **11.12.1**、TypeScript **5.9.3**（lockfile 安装）。需要 Git 和 Node.js 24。clone / 安装需要网络，编译与目标测试不调用模型 API。

从 AI Learning Coach 仓库根目录运行；最后一个参数必须是尚不存在的独立目录：

```bash
python scripts/first_session.py prepare ../skills-cache-lab
```

已有该独立读本时，重新编译并检查：

```bash
python scripts/first_session.py check ../skills-cache-lab
```

没有 Python 也可以手动准备：

```bash
git clone https://github.com/chrichuang218/claude-code-from-scratch.git skills-cache-lab
cd skills-cache-lab
git checkout --detach bdb7e858ff9be8fbed82d0488e13a63b9b0e3288
npm ci --ignore-scripts --no-audit --no-fund
node node_modules/typescript/bin/tsc -p tsconfig.test.json
node --test --test-name-pattern="^cache reset makes a newly created skill discoverable$" dist-test/test/skills.test.js
```

只在刚创建的独立目录 checkout。目标输出包含 `tests 1`、`pass 1`、`fail 0`。每次修改 TypeScript 后都要重新编译。无需读本项目的 provider key；使用 Codex 教练仍需要相应账户和环境。

## 第一个动作

打开固定版本的 [目标测试](https://github.com/chrichuang218/claude-code-from-scratch/blob/bdb7e858ff9be8fbed82d0488e13a63b9b0e3288/test/skills.test.ts#L36) 和 [真实实现](https://github.com/chrichuang218/claude-code-from-scratch/blob/bdb7e858ff9be8fbed82d0488e13a63b9b0e3288/src/skills.ts#L27)。本机教学时由教练重新定位并给出可点击路径。

**同一进程第一次扫描空目录后，新增一个 Skill 文件；再次调用 `discoverSkills()`，你预测它会返回什么？依据是哪段控制流？**

把预测告诉教练，再观察实际结果。后续只围绕暴露的卡点推进，不需要先学完整套 TypeScript 语法。

## 下次继续

首次体验需要长期保存时，教练可以参照 [单轨道空白工作区](../workspaces/first-session/README.md) 按需建档。该示例没有作者的历史成绩。只有你的真实行为才能形成记录。

结束时保存：本次观察、帮助程度、仍待验证的边界，以及下一处真实入口。下次说“继续缓存失效的学习”即可；是否独立掌握由后续证据决定。

遇到问题请提交 [首次体验反馈](https://github.com/chrichuang218/ai-learning-coach/issues/new?template=first_experience.yml)，写明卡在哪一步即可。

源码 MIT，版权归原项目作者；本体验通过固定 commit 引用源码，不复制项目配置或凭据。[工程复现记录](../../docs/validation/first-session.md)
