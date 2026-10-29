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
