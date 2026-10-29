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
