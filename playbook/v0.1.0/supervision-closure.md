# 主 Bot 监督闭环补齐实施记录

创建时间：2026-10-29
最后更新：2026-10-29
状态：随 RC29 接手合入；runtime-node/desktop 套件已在接手分支实际运行（见文末），发布门禁与产品回归以 RC29 发布回执为准。依据 ADR111 §12，依赖返回结果取消修复。

## 用户目标与范围

一次委托后，由主 Bot 承担子任务的普通问题、技术恢复、结果核验和返修；需要人决定时才交还。跟进责任、执行事实和操作回执分开建模，已有权限、预算、人工门与用户停止保持有效。

## 落点

| 缺口 | 实现 | 回归用例（RC29 接手时已运行，见文末） |
|---|---|---|
| 返回结果后原任务返修 | session-repair / session-takeover 允许 resume 未签收结果；原 plan/session/criteria 保留；反馈先持久入箱再排队 | session-repair.test、session-supervisor.test |
| 旧协调记录漏掉责任 | repair-custody 按已有 followUp 回收 delivered/技术等待的原 checkpoint，一份责任只有一个已有承接者 | repair-ownership.test |
| 结果未知后的出口 | supervision-recovery 提供 blockers/nextAction/replayAllowed；本机核验对账允许处理旧 delivered 记录；实际对账证明可重新进入停止/idle 检查 | supervision-recovery.test、verification-dispatch-recovery.test |
| 旧任务结构化监督 | 沿当前用户与既有 coordinate_work adoption 建立原生 mandate；无授权唤醒不能承接 | coordination-lifecycle.test |
| 无进展治理 | 执行代次、核验来源哈希等纯元数据不构成新进展；report 保留技术阻塞与下一动作 | continuation-policy.test |
| 重启通信回执 | 同一真实完成回合的已观察命令以一个 agent_execution_completed 日志提交批量确认 | agent-supervision.test |
| 连续监督验收 | 补脚本/宿主用例；真实模型多轮与崩溃窗口尚待发布验收 | 不能登记为通过 |

恢复报告是既有 get_session(report) 的只读结构，不授予权限。Agent 问题保留 requestId/revision；消息入队和实际应用仍分开。没有真实凭据的外部副作用继续 reconciliation_required，不提供模型自证成功或强制清账入口。

## 行动记录

1. 在独立代码/知识 worktree 开发，保留主线程清理修复、脏文件和当前运行实例。
2. 先补 ADR111 §12，再实现上述宿主与协议 seam。
3. 编写返修、人工/停止保护、责任去重、旧任务承接、未知状态、批量回执及停滞回归。
4. 内容/diff 自审补正：返修反馈必须先于可调度状态持久化；新 epoch 同时改变语义核验和 host verification 内容身份；纯代次/哈希不规避 no_progress；记录格式 6 的最低读写要求在重建/历史恢复中保留。
5. 只运行必要的源文件生成脚本与 git diff --check；未运行测试、构建、类型/架构/IPC检查、截图交互或真实模型验证。

## 发布前验证

按代码仓 AGENTS，在全部 PR 正常合入的最终候选上执行完整门禁和产品回归；另外验证原任务提问/选项回答、技术中断、核验失败返修、用户停止、真实人工门、旧数据承接、消息已答未启动和已执行未记账的崩溃窗口。实现者自审不称独立验收；安装包、真实模型与无障碍覆盖分别记载。

本轮不重启/安装 App，不修改真实任务数据，不发布版本。源码完成不表示当前运行窗口已加载这些改动。

源码审阅补记：返修还须穿过 Runner 的旧完成快捷分支。只在真实绑定且尚未 applied 的返修 epoch 中跳过一次旧完成判定，进入实际工作回合；已有 unknown dispatch 不借此重放。实际 GoalRunner + Supervisor 的用例检查“旧叶子全完成仍会执行返修”，尚未运行。无进展指纹排除单纯 epoch/来源哈希变化，具体结果或执行回执阶段变化仍计入进展。

## 子 Agent 问题承接与状态表达补记

后续用户截图显示报告正文写了 A/B/C 与批准要求，但没有原生 Agent question/request，也没有 waitingOnUser；主 Bot 仍在查询和核验，未及时在主对话交还。修正规则通过现有 work-session/project-agent Context Sources 进入：工作选项先交父代理关联回答；报告文字不制造审批，原用户实现目标不能被调研步骤变成额外批准；真正权限/人工问题沿原入口。同步修正 spawn_session 对未签收返修的旧 replace 指引，避免与 resume 契约冲突。

Desktop 在首次活动位置合并同 session 的所有通知，使用宿主当前状态和稳定阅读/虚拟行身份；保留原始事件/详情。图标改为静态盒子内的高光扫过，等待/终态/缺事实/reduced-motion/不支持 mask 时静态。修改仅影响表达和现有规则，不新建文本审批或执行旁路，不操作真实运行任务。

新增/修订活动合并与分页身份、当前状态投影和 Context Source 角色边界用例；生成嵌入提示正文与工具提示并做内容/diff 审阅。未运行测试、截图、交互、真实模型或安装包验收；没有重启当前 App。

问题承接的运行时补正：按 canonical agentRequests 读取未回答的父代理问题并恢复其原消息，独立于消息回执是否 applied，避免它在后续消息超过最近上下文窗口后丢失；回答、取消或升级后不再强制重入。只读有界查询，不推测报告正文是问题，也不创建新权限。已写忙碌邮箱和关联回答用例，未运行。发布场景脚本同步按“一 Agent 一行、当前状态、静止图标”断言，未执行。


## 隔离手测故障与修复（2026-10-29）

用户后续要求本地手测，另启隔离数据目录/端口的开发实例，保留原开发实例，不复制原会话/任务/订阅登录。启动仅确认窗口和机器人加载，未声明监督通过。

用户点击“熟悉项目”后实际失败：生命周期任务 delegationOrigin 没有 workId；新增报告恢复投影将 undefined 传给 coordination-v2 SQLite，get_session(report) 与任务详情均抛 ERR_INVALID_ARG_TYPE。主 Bot 调用未正常返回，被记录 execution_outcome_unknown 并反复中断。子任务独立核验又因 ephemeral conversationId=null 未沿已验证 GoalPlan 会话核对祖先，工具返回 access_identity_invalid，最终 criterion_unverified。

修复按 ADR111 §13.1：缺 workId 不查工作主键，不制造绑定；临时 work_session 只在显式 plan/session、现有 PermissionPrincipal 和未停止持久祖先一致时继承同一 Bot 的当前权限；只读监督查询已返回异常产出失败 Tool Result，控制/写异常继续保留未知保护。新增真实 coordination-v2 无 workId 报告、临时核验身份正反例与只读失败/控制未知区分用例，未运行。

本轮只做内容/diff 审阅和用户本地手测所需 runtime-node 构建。单元/集成测试及发布回归仍留到发布门禁，不能称通过。只更新隔离测试实例，历史 unknown、失败、原始任务与 Evidence 保留，不手工改账；后续真实模型交互仍由用户测试。

更新回执：代码 c85f83ff 已推送，runtime-node 启动必需构建完成，隔离 Electron 已重启到该源码。重新打开同一 session 的任务详情后，“任务资料暂时无法读取”消失，实际呈现核验结果、Evidence 操作记录和历史核验入口；旧中断记录保留。该观察仅覆盖此次用户故障的详情读取，不等于真实模型监督/核验、回归套件或发布验收通过。


## 原任务收尾闭环补记

用户再次反馈答复后任务卡仍在。只读现场确认：仍只有原 session 0f959c5b 的“熟悉项目”，原 runner=blocked；新“？”回合的 work.sessionIds=[]，fallback agent_reply.sources=[]，该工作直接 delivered；旧工作因 get_session 未知 dispatch 保持 blocked_system。此前修复解决了读取异常，尚未把此链闭环，不能宣称现场完成。

按 ADR111 §14 补齐：用户回合 roster 纳入同一父 Bot 未决任务，唤醒保留范围；L7 保留责任、阻塞和中断查询事实；有未决任务的用户回合强制已有结构化 post_reply，在原预算内只补一次交付机会，普通文本不走无源 fallback；真实已投递回复的 sources 写回当前工作跟进关系，崩溃后恢复也保留，仍有修复责任则继续，真实 settled 后才 delivered。只读 get_session/get_verification_detail 遗留 unknown 按原 dispatch/turn、唯一目标、父子归属、非活动 attempt 与核验进行对账，记 query_interrupted，既不提供原结果也不验收任务，外部副作用保持保护。

新增同父 Bot 旧任务名册/跨父与唤醒隔离、普通文本交付拒绝/一次修正、真实交付后的跟进责任、只读 unknown 正反例和 L7 信任边界用例，未运行。日常验证仍仅内容/diff 审阅；本地测试实例更新所需 protocol/runtime-node 构建与针对用户故障的现场观察单独记录，不替代发布测试。

补充：原失败 verifier 有 canonical failed/completedAt，continuation 却遗留 requesting/formatAttempt=1，重核验会直接 no_progress。continuation port 仅凭晚于最后进展的真实终态核验回执与核验阻塞原因，沿现有 completed recheck 收口旧请求，保留累计使用量、失败和工具未知保护。新增 requesting/tools/过时回执边界用例，未运行。


### 原任务真实模型恢复回执（隔离实例，2026-10-29 14:30 CST）

源码 e4c13e1c，启动必需 protocol/runtime-node 构建完成；无单元/集成套件运行。原 session 0f959c5b-aee0-4e29-8618-36fc44a6d43e 与 plan 3e49e658-e0ff-477d-b20b-0e74e11e1d14 保持不变。宿主按原 dispatch/turn 记录 query_interrupted，保留调用身份与预算，随后沿原 work 唤醒并实际调用 get_session/get_verification_detail/verify_session。新 verifier 独立只读获取事实并通过 c1-c3；plan.status 与 runner.status 都成为 completed。主 Bot 通过 post_reply.sources 引用原 session，2026-10-29T06:30:57.037Z 写入 resultAcceptance.acceptedBy=policy（verdictRef 指向真实 passed 核验），没有伪造用户批准或手工改账。

原生窗口观察确认：同一 Agent 活动行显示“熟悉项目 已完成”；底部“当前任务（1）”退出，机器人不再标记进行中，历史中断、原输入、报告与 Evidence 均保留。原用户输入仍是同一条 lifecycle-research 请求，没有新增子任务；没有替用户发送新测试提示。本次是实现者对用户报告故障的窄范围现场观察，非独立审阅，不代表全套监督、多模型、安装包、无障碍或发布回归通过。模型答复措辞与重复结论仍有产品改进空间，不以本次成功关闭其他缺口。

## 并入 RC29：实测与接手修复（2026-10-29）

发布 RC29 时由发版执行者接手。代码 PR 合入最新 PeerAgent/dev/0.1.0（含撤回、取消与恢复入口修复），解开 session-supervisor/coordination-lifecycle 用例与 coordinate_work 提示冲突（两侧规则都保留），重新生成 coordination worker 与工具提示嵌入文件。首次实际运行套件后发现并修复：

1. repair-custody 在对账入口就读取名册，没有待处理工作时也触发读取；改为与 continuation-custody 相同的惰性名册。
2. 返修回合被旧完成判定吞掉：接管先暂停 plan，promote 的 revisePlan 又按全部完成的旧叶子重新派生为 completed，调度随即按终态跳过。GoalRunner 只对真实绑定、尚未 applied 的返修 epoch（repairExecutionPending）以 execute/repair 进入实际回合；hasActiveGoalRepair 识别已完成接管的返修。不会因此重放 unknown dispatch。
3. 一条 supervisor 用例直接写验收，绕过了关闭门；改为提供宿主核验事实与已索引 Evidence。
4. Renderer 的 conversationWindow 以无扩展名做值导入，Vite 能解析而 node 测试不能，三个测试文件加载失败；改为与同目录一致的显式 .ts。
5. Desktop 重启/唤醒集成用例的叶子 Evidence 从未索引，宿主核验结论实为失败，结果仍由 Bot 承担修复。按本记录的修复托管，该工作正确保持可运行，脚本化模型每次只重复汇报，于是出现重复回复，直到 no_progress。修正夹具：先索引 Evidence；脚本化模型的 post_reply 执行回执按生产路径交给回合收集器。未放宽宿主规则。
6. Electron 冒烟仍按旧的单行引用和逐事件 Agent 行断言，两个平台都在回复检查处失败。断言改为已选定的两层引用预览：一个 SVG 定位原文操作、有效来源时间、来源在上、摘录单行省略；产品回归契约改读 stacked。完成复核检查先经产品的“回到最新消息”控件回到最新，再等待追加的卡片，不再依赖虚拟窗口碰巧覆盖末尾。Agent 行改用展示 ID 后，滚动辅助函数按 data-source-message 定位固定行，避免 Home 键竞态。只改检查，未改产品行为。

运行结果（接手分支，macOS，Node 25）：runtime-node 1619/1619 通过；desktop 6113 项中 6108 通过、0 失败、5 跳过，另一组 3/3 通过。Electron 冒烟主场景及 recovery、startup、selection-quote、agent-activity、verification、shared-ui 六个专项本机全部通过，无页面或授权错误。PR CI 40869747028 在 macOS 与 Ubuntu 均成功（构建、类型、架构、测试与冒烟）。

需在发布回归中观察的产品风险：已汇报但核验未通过的结果会让汇报所在的工作继续可运行。真实模型若只重复汇报而不返修，用户会看到重复回复，两次无进展后转为 blocked_system 恢复卡。上限由宿主保证，但真实模型的多轮措辞与返修选择未经验证，不能据此宣称监督体验已验收。
