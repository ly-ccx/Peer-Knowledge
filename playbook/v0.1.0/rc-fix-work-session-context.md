# RC补修：批准后的委托任务执行上下文

2026-10-02，Accepted，A级。负责人已授权全部RC修复、自测和候选发布；架构补充先写入ADR80。不能通过删掉测试中的批准要求或人工改写模型输出宣布通过。

实现边界：`packages/system-context/src/sources/work-session-source.mjs`及focused测试；prompt-assembler、index.mjs/index.d.ts、系统装配契约测试；Desktop llm-chat-service的projectTurnSystemContext及mode-gate测试；TUI tui-turn-executor及对应测试。当前work-session-origin的历史/记忆保持L7。源从当前GoalPlan取得准入phase；未知不捏造批准。静态执行角色不包含用户/项目正文，不新增Runtime Projection工具，不改变PermissionGrant、租约、签收或存储。

复现：真实Luna两次spawn_session、两个plan批准成功、两个worktree实际建立，worker仍把父消息“开任务/等批准/代理不得写”套到自己，停在waiting_user，原文件没有修改。保留完整失败证明；后续同样双写输入、批准、核验、签收、合回必须复验。先源版本，再确切安装候选；手册E/F/G与多入口验收仍独立。


源码29d43dec复验两任务实际完成、精确文件内容、独立Verifier通过、代理来源与Evidence真实、用户签收成功。全程仍未合回：测试脚本错误假定签收等于合回，漏答独立“合回改动”卡，等待180s失败。这是夹具流程缺失；不能删除合回授权闸门。报告 `evidence/rc-source-complex-merge-fixture-failed-20261002.json` 保留；补齐卡片回答后再跑完整流程。27项系统上下文/Desktop focused、9项TUI focused及最终全量门禁通过（报告有绑定），最终CI待完成。


同输入源码29d43dec完整复验通过：两真实Luna写任务、两计划本机批准、两独立worktree精确文件、真实独立Verifier/Evidence、用户签收后原项目保持不变、回答两张独立合回卡后只a.txt/b.txt变更。原始证据 `evidence/rc-source-complex-passed-20261002.json`。最终worker修复HEAD8fb68de1两平台CI36918177534与候选HEAD29d43dec两平台CI36918216680均SUCCESS。多入口源码同HEAD真实模型/工具/HTTP/WS/签名/去重/desktop-only批准/TUI接管亦通过，`evidence/rc-source-multi-entry-passed-20261002.json`；其TUI是实际后端源进程，不能充作安装CLI UI通过。代码补修PR98 merge2c6b558a和文档候选PR97 merge0beeb21f均合入开发线，生产树与受验29d43dec完全相同。
