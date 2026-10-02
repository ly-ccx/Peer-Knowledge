# RC补修：等待任务的用户回答恢复

2026-10-02，Accepted。B级：修复既有委托消息事件与Runner恢复衔接，不增加能力、权限、IPC、工具参数或存储字段。负责人“全部做完并先自测”授权此已发现P1修复；先记录边界再实施。

## 真实失败

命令Evidence源码35f4606d双写首轮B误读历史批准要求，已批准的phase=running任务自行waiting_user。项目代理的空响应通过现有Retry、排队新用户输入恢复；随后真实message_session(intent:answer)返回现有session，但只追加了三条原文用户消息，任务仍waiting_user、未写b.txt。代码messageLocked的answer分支在consumeRequestedUserInput/resume前返回，amend分支才恢复。B3-01卡明定提问回答通过answer转交，因此这是实现遗漏。原首轮证明保留；本次恢复单列，不宣布无干预通过。

## 允许改动

- packages/runtime-node/src/project-agent/session-supervisor.mjs及session-supervisor.test.mjs：answer在实际可消费等待状态走同一用户回答消费/既有goalRunner.resume；原文仍为用户事实，不包装成系统指令；运行中answer沿既有追加行为，amend沿既有下一回合纠正行为。暂停/取代/取消与前置失败排队不能借回答开启批准门。
- packages/runtime-node/src/project-agent/prompts/delegation/message_session.md及其构建生成物tool-prompts.generated.mjs：明确两种intent的等待恢复行为及批准边界。
- 本卡、运行时契约已有message_session节、RC自测与手册证据/交付状态。

不改main.mjs、上下文源、Provider投影/权限、租约、核验/签收/合回门；不新增依赖。原文历史与失败保留，不人工设置成功状态。先红测试复现answer不唤醒，focused与runtime-node全量、build/typecheck/architecture、两平台CI通过；同一真实持久夹具通过产品Retry/插话完成B的Bash命令核验、独立Verifier、来源汇报、本机签收及单独合回决定。新候选rc.2重新下载验包后才Ready。


## 本机结果与范围

源码412303b4：先完成2项真实红测试（answer不恢复、前置排队回答未拒绝），focused65/65、runtime-node1006/1006、build/typecheck/architecture均通过，生成提示已同步。PR102 Linux CI通过；Mac首轮在quick-chat自动化evaluate遇到“Resulting promise was garbage collected”，三项性能中位数55.19/88.40/154.40ms均在原预算，已按同提交重跑失败任务一次，未改断言或预算。

[真实修复前失败](evidence/rc-session-answer-real-failed-20261002.json)与[同夹具恢复的限定证明](evidence/rc-session-answer-recovery-scoped-20261002.json)均保留。修复后真实answer唤醒B、Bash字节核验/tool-result引用与TaskRunner Verifier通过；实际手动签收、单独授权合回只修改a.txt/b.txt且内容精确。B的最终hostVerification仍missing，手动签收返回verification_below_floor，因此这轮仅证明恢复、命令事实与人工签收/合回，不能记作双独立Verifier复杂流程通过。测试夹具将补强“两个hostVerifier实际passed＋本轮新来源回复＋签收返回passed”后对新候选重跑；总RC状态继续未Ready。
