本地路径已替换为 <source>、<fixture-lab> 和 <project>；完整原始输出保留在本次本地验证目录。

# 当前教练回复

接着缓存失效这一处。上次记录停在运行教练提供的测试，独立设计观察还待验证。

这次先口头设计一个小测试：同一进程第一次调用 [discoverSkills()](https://github.com/chrichuang218/claude-code-from-scratch/blob/bdb7e858ff9be8fbed82d0488e13a63b9b0e3288/src/skills.ts#L27) 后，只把已有 Skill 的正文从 `old body` 改成 `new body`，再调用一次。你预测第二次得到什么，并准备怎样观察来验证？把预测和观察办法一起说出来即可，先不用写代码。

# 实际只读操作证据

本次为模拟背景恢复测试。读取了指定 SKILL.md 和 RESUME.md；读取 lab 的 README.md、MISSION.md、PROGRESS.md、learning-records/cache.md、sources/mini-claude.md。PROGRESS 更新日期为 2026-09-01，下一检查点为修改已有 Skill 后预测第二次 discover 并设计观察。记录只假定用户运行过教练设计的测试，独立设计仍待验证。没有新增学习事实、运行测试或修改源码。

实际命令（PowerShell）：

```powershell
Get-Content -LiteralPath '<project>/plugins/ai-learning-coach/skills/learning-coach/SKILL.md'
Get-Content -LiteralPath '<project>/plugins/ai-learning-coach/skills/learning-coach/RESUME.md'
rg --files -g '*.md' -g '*.json' -g '!node_modules' '<fixture-lab>'
Get-Content -LiteralPath '<fixture-lab>/README.md','<fixture-lab>/MISSION.md','<fixture-lab>/PROGRESS.md','<fixture-lab>/learning-records/cache.md','<fixture-lab>/sources/mini-claude.md'
Get-Item -LiteralPath '<fixture-lab>/AGENTS.md' -ErrorAction SilentlyContinue
git -C '<source>' rev-parse HEAD
git -C '<source>' status --short
rg -n 'discover|cache|readFile|mtime|invalidate' '<source>/src/skills.ts' '<source>/test/skills.test.ts'
Get-Content -LiteralPath '<source>/package.json'
rg --files -g AGENTS.md '<source>'
$n=0; Get-Content -LiteralPath '<source>/src/skills.ts' | ForEach-Object { $n++; if ($n -le 116 -or $n -ge 174) { '{0}: {1}' -f $n, $_ } }
$n=0; Get-Content -LiteralPath '<source>/test/skills.test.ts' | ForEach-Object { $n++; '{0}: {1}' -f $n, $_ }
Get-Content -LiteralPath '<source>/README.md' -TotalCount 70
```

实际结果：源码 HEAD 为 `bdb7e858ff9be8fbed82d0488e13a63b9b0e3288`，与登记一致；`git status --short` 无输出。lab 的 AGENTS.md 不存在，源码范围的 AGENTS.md 搜索无命中，因此所在批次退出码为 1，不是源码核验失败。当前 `src/skills.ts:27` 为 discoverSkills 定义，`:28` 为缓存提前返回，`:76` 为读取文件，`:103` 为正文写入 promptTemplate，`:175` 为 resetSkillCache；`test/skills.test.ts:36` 为已有新增 Skill 缓存测试。README 与 package.json 证实此读本为 TypeScript 项目，单元测试命令为 `npm run test:unit`；本次未执行该命令。
