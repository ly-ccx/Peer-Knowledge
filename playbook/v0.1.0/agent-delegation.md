# RC-AGENT：独立 Agent 通信与工作动态

负责人：用户；授权：2026-10-10 要求完善完整 ADR 后落地。  
级别：A/B/C；ADR：[89](../../knowledge/decisions/89-independent-agent-delegation-and-communication.md) 已在实现前 Accepted。  
依赖：回复恢复 PR #138；允许从其已推送 clean HEAD 建堆叠分支，PR base 指向该依赖分支，合入开发线按顺序。  
代码基线：`codex/reply-recovery`，`28ddb755f3069ca68f2ccd8d7250f0c868347894`；经典执行不变，不自动合并、不发布 RC。

## 范围

真实独立 WorkSession 的双向通信、持久交付与身份门禁；工作动态投影；连续气泡间距。保留现有固定派发深度、GoalPlan、权限、Evidence、恢复与调度，不新增依赖/数据库。

允许改动：

- `packages/protocol/src/delegation*`、必要类型出口；
- `packages/runtime-node/src/project-agent/` 通信/动态 Module、工具规范、Provider、Supervisor 少量装配、工作回合画像与现有消息投影、相关测试及 runtime-node 出口；
- `packages/runtime-core/src/conversation-history-projector*`；
- `packages/system-context/src/sources/`、来源注册与对应测试；
- `apps/desktop/electron/main/project-agent/` 与 `llm-chat-service.mjs` 少量 context 准入适配，`tools/delegation-tool-definitions*`，相关测试；
- `apps/desktop/renderer/src/project-agent/conversation/`、`state/botConversationState*` 与工作动态状态、styles；
- `apps/tui/src/project-agent/` 的工具/共享宿主装配和测试；
- `packages/i18n/` 工作动态文案；
- `apps/desktop/scripts/` 必要独立窗口场景、截图检查/审查清单；
- 本知识卡与 ADR 89 的证据记录。

必要范围扩展（实现前记录）：`packages/runtime-node/src/goal-runner.mjs`、`goal-plan-store.mjs`、`packages/protocol/src/session-facts*`、`packages/protocol/src/goal*`，以及 renderer 的工作状态投影。理由：区别等待主 Bot 与等待人类，持久化协调等待/恢复标记，防止自动 kick 空转，补足 ADR §6 的真实执行闭环；不改用户授权闸门。

必要范围扩展（验证前记录）：`packages/protocol/src/task-overview*`、`apps/desktop/electron/main/task-overview-aggregator.mjs`、`scripts/product-regression.mjs`。理由：统一主 Bot 等待状态的操作归属，增加真实工作动态与连续气泡间距的产品验收门禁。

实现按 ADR §8 Module 分工，不扩 god module。任何发现的必要路径扩展先在本卡记录原因再改；不覆盖原工作区未提交修改。

## 退出条件

ADR §10 矩阵；焦点单测、受影响包、build/typecheck/architecture；产品 capture、逐张观察、review.json、verify。测试与文档同轮 push，交付独立 PR 与明确的覆盖限制。不得将实现自审写成独立审查。
