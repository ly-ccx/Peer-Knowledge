# RC补修：等待任务的用户回答恢复

2026-10-02，Accepted。B级：修复既有委托消息事件与Runner恢复衔接，不增加能力、权限、IPC、工具参数或存储字段。负责人“全部做完并先自测”授权此已发现P1修复；先记录边界再实施。

## 真实失败

命令Evidence源码35f4606d双写首轮B误读历史批准要求，已批准的phase=running任务自行waiting_user。项目代理的空响应通过现有Retry、排队新用户输入恢复；随后真实message_session(intent:answer)返回现有session，但只追加了三条原文用户消息，任务仍waiting_user、未写b.txt。代码messageLocked的answer分支在consumeRequestedUserInput/resume前返回，amend分支才恢复。B3-01卡明定提问回答通过answer转交，因此这是实现遗漏。原首轮证明保留；本次恢复单列，不宣布无干预通过。

## 允许改动

- packages/runtime-node/src/project-agent/session-supervisor.mjs及session-supervisor.test.mjs：answer在实际可消费等待状态走同一用户回答消费/既有goalRunner.resume；原文仍为用户事实，不包装成系统指令；运行中answer沿既有追加行为，amend沿既有下一回合纠正行为。暂停/取代/取消与前置失败排队不能借回答开启批准门。
- packages/runtime-node/src/project-agent/prompts/delegation/message_session.md及其构建生成物tool-prompts.generated.mjs：明确两种intent的等待恢复行为及批准边界。
- 本卡、运行时契约已有message_session节、RC自测与手册证据/交付状态。

不改main.mjs、上下文源、Provider投影/权限、租约、核验/签收/合回门；不新增依赖。原文历史与失败保留，不人工设置成功状态。先红测试复现answer不唤醒，focused与runtime-node全量、build/typecheck/architecture、两平台CI通过；同一真实持久夹具通过产品Retry/插话完成B的Bash命令核验、独立Verifier、来源汇报、本机签收及单独合回决定。新候选rc.2重新下载验包后才Ready。
