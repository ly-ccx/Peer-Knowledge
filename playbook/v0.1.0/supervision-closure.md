# 主 Bot 监督闭环补齐实施记录

创建时间：2026-10-29
最后更新：2026-10-29
状态：源码实现与内容/diff 自审；未运行验证、未发布。依据 ADR111 §12，依赖返回结果取消修复。

## 用户目标与范围

一次委托后，由主 Bot 承担子任务的普通问题、技术恢复、结果核验和返修；需要人决定时才交还。跟进责任、执行事实和操作回执分开建模，已有权限、预算、人工门与用户停止保持有效。

## 落点

| 缺口 | 实现 | 回归用例（已写，未运行） |
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
