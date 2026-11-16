# ADR 102：任务生命周期单一投影

创建时间：2026-10-21
最后更新：2026-11-15（明确关联引用为 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md)）
状态：Accepted；既有实现见 Peer-Agent PR #180，RC25 组合发布验证进行中。
级别：A（协议投影），B（Runtime 事实采集、任务聚合、Renderer 消费）。

关联：ADR 88、93、96、99、100、[104-progressive](104-progressive-interaction-and-coordination-storage.md)；产品北极星与架构治理基线继续适用。

## 决策

同一份事实只能产生一份生命周期决策。`decideLifecycle` 在既有 Protocol Module 内统一给出 `status / statusLabel / actionRight / nextAction / cancelable`；任务列表、工作会话、抽屉和取消入口直接消费，不另建状态表。兼容入口 `deriveSessionFacts` 必须完整转发事实，不能吞掉未消费中断等当前行动权信息。

Runtime 负责事实，Protocol 负责纯投影，Renderer 负责表达。`runner.status` 是上次持久化观测，不能证明执行仍在运行。执行和核验的进程内 token 才能给出 `live`，并在 finally 释放；runner 明确终态可给出 `ended`，其余为 `unknown`。重启不因缺 token 伪造失败、完成或验收，不读时钟推断执行活性。

已完成计划仍有活执行时不得显示已完成；审批、提问、人工 DoD、未消费中断、停止中、结果未知、核验、等待父代理按各自更具体的事实投影。技术阻塞不是人类决策。持久化验收结论才允许委派任务进入 accepted；计划 completed 或核验 passed 不制造验收。普通历史非委派 Goal 沿用既有完成契约。

取消事实来自同一决策；已验收/已终结不可取消，停止中与结果未知不靠重复取消解决。真实预算门和待回答问题不能被 completed 吞成终态，也不能因界面隐藏按钮而取消合法能力。权限、Tool Result、Evidence 和执行链不变，投影不授权执行。

## 列表聚合与兼容

轻量计划索引不含完整 runner，故在既有活跃窗内、尚未验收的 completed 候选可以 hydrate，再由唯一决策决定是否有人类门。过期和已验收历史不批量加载。门计划与普通计划竞争同一会话的最新计划卡，不额外制造多张门卡；既有 live handoff 的独立投影保留。

不迁移、取消、删除或批量改写旧计划、对话、报告与 Evidence。未知状态通过投影和既有恢复链解释，不能按超时写回失败，也不能把持久化 running 当活执行。该变更不表示当前已安装进程已升级。

## 报告与验收事实的依赖方向（RC25 整合修正）

报告原文是核验输入，不得依赖核验或验收投影。合并验证在 TUI 完整链路复现循环：工作会话进入 result_ready 后，投影读取 acceptanceFacts → verification.facts → 通过 supervisor.get(report) 取报告 → 再次进入投影；回调捕获异常掩盖递归，导致主线程阻塞与超时。Desktop 使用同一装配，也必须修正。

SessionSupervisor 的 `readReportSummary(sessionId)` Interface 只从指定计划/会话的 canonical 报告内容生成摘要，不读取验收 authority、不调用完整 session 投影。两宿主核验端口统一使用该入口；用户详情仍用既有 get(report)，但其核验回读已无环。报告身份、证据、核验与验收规则均保持，不能靠降级验收或延长超时修复循环。

## 验证与记录

PR #180 已有协议生命周期矩阵、真实聚合器与三表面一致性、Runtime token/会话事实、监督者及 Renderer 取消事实测试；原 PR 双平台 CI 通过。RC25 合并审查发现兼容包装缺少 interruption 转发，须补真实回归后纳入最终候选。

窗口验收须涵盖 completed + 预算门/待回答门、技术阻塞、活执行、取消事实和同会话去重；通用界面截图不能代替这些专用组合。发布时对全部合入的最终候选重新执行完整回归，准确记录源码、截图指纹、自审独立性和安装包覆盖边界，结果见 [RC25 发布回执](../../playbook/v0.1.0/rc25-candidate.md)。

原本地 ADR 的现场调查、历史红绿测试与失败窗口记录保留在原工作区；本文件提炼可公开的契约，不上传私有任务身份或用户历史。
