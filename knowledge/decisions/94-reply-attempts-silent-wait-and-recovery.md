# ADR 94：主 Bot 回复、静默等待与历史错误

日期：2026-10-18  
状态：Accepted（用户要求区分三类状态、补齐静默等待和成功恢复并验证完整流程）  
级别：A（能力、状态投影与持久事实），B（协调运行时）；继承 ADR 88、89、91、93。

## 1. 现场与目标

RC15 的后台唤醒收到 HTTP 200 和 response.completed，但正文为空、没有工具调用。有限重试耗尽后，通用循环产生 empty_model_response，主运行时生成 agent_unavailable。独立诊断任务同时仍在运行。旧卡在下一次尝试开始后被 superseded，界面却显示“中断已结束，后续进展见最新回复”，没有成功交付依据。

三个事实必须独立：主 Bot 的一次回复尝试、各子任务当前状态、历史尝试的错误。回复失败不取消子任务，子任务运行不证明主回复成功，新尝试不证明恢复成功。

## 2. Module / Interface

- Wake Wait Module：通过当前宿主事实判断是否可以安静等待。常规启动/恢复/运行事件且所涉任务仍由同一工作拥有并处于 queued/starting/running/verifying 时，可以不调用模型；保存 agent_turn 的 silentWait 以及工作 waitFor。用户输入、交互重试、结果/异常/问题、权限等待、技术阻塞和未知派发不能走此路径。
- `wait_for_sessions`：模型需要观察后等待时，沿用 Delegation Provider → Manifest → Projection → Tool Call → PermissionGrant → Evidence。仅后台主 Bot、当前工作范围内、当前仍在推进的任务可接受；返回结构化等待结果和 terminal control，完成配对 Tool Result 后结束模型循环。禁止以空文本或助手声称代替等待凭据。
- Reply Failure Facts Module：从同一 workId 的尝试、canonical 消息、交付账本及子任务当前事实产生 `ProjectReplyFailureStatus`。Renderer 只解释此对象，不猜执行结果。

## 3. 静默等待不变量

1. 只有宿主判定或成功的等待 Tool Result 能产生 silentWait；空响应、HTTP 错误、未知工具结果仍是失败。
2. 静默等待保存当前任务关联和 waitFor，消费本批普通事件；结果、异常、用户新输入到达后照常继续。不能占用模型轮询、不能清空其他工作的责任。
3. 等待不是已回复、已交付或已恢复。没有真实回复交付时不向用户显示“已恢复”。重启从持久工作账本和检查点重建等待。
4. 等待与任务结束并发时重新读取事实，结果事件保留；需要主 Bot 处理的技术阻塞继续由 ADR93 接管，真实问题仍等人，取消与暂停不重开。

## 4. 历史错误投影

| phase | 依据 | 用户表达与操作 |
| --- | --- | --- |
| current | 当前尝试失败，未有后续处理 | 主 Bot 本次回复未完成；保留具体类型和可用重试 |
| retrying | 当前工作有续跑或有效重试预约 | 已安排继续回复；不额外提供重复重试 |
| superseded | 有同工作后续尝试但无成功交付 | 此前回复未完成，后续尝试已接手；不称恢复成功 |
| recovered | 错误之后，同工作 canonical agent_reply 且交付账本 delivered | 主 Bot 回复已恢复；记录 recoveredByReplyId |
| cancelled / paused | 工作已取消 / 暂停 | 说明取消 / 暂停；不称恢复成功 |

只有 recovered 可以显示恢复成功。prepared、invalidated、另一个工作交付、静默等待、仅新 agent_turn、仅任务完成都不满足。旧数据无交付账本时保守保留历史失败，不发明成功凭据。历史记录原文与错误详情保留，不改写用户数据。当前仍推进的子任务 ID 单独返回，界面说明“子任务仍在推进”，不拿它覆盖回复失败。

## 5. 实施与验收

实现落点：Protocol 状态类型；runtime-node 的 Wake Wait 与 Reply Failure Facts；Delegation Provider 的等待工具；Runner/Coordination 保存等待；Renderer 显示主回复与子任务的独立状态；i18n 双语。

验证：普通唤醒零模型调用、模型工具等待真实 PermissionGrant/Evidence 和 terminal 配对、结果唤醒后交付、空响应仍失败、连续失败只成为历史尝试不冒充成功、prepared/invalidated/跨工作拒绝恢复、重启、取消、超时、用户输入/人工等待/技术阻塞不能静默吞掉。隔离 Electron 深浅色宽窄窗口检查当前错误与仍运行子任务、历史失败、成功恢复。标准 Capture 全图自审和 Verify；认知受控，不冒称真实云模型或安装版验证。

本 ADR 不扩大文件/图片/执行权限，不安装应用、不修改真实任务、不合并或发布 RC。

## 6. 实施记录

- Protocol 定义 `ProjectReplyFailureStatus` 与 `ProjectAgentSilentWait`。主 Bot 的 turnKind 由宿主写入现有事实 Context Source，旧 inputAnchors 仍不能沿用到 wake。
- `wake-wait.mjs` 集中管理当前归属、推进状态和静默结果。`wait_for_sessions` 使用既有 Delegation Manifest / Projection / Provider 与 terminal control；先配对 Tool Result 再停止真实 Provider 循环。失败与取消结果不能产生成功等待。
- 普通运行/恢复事件在已有错误时只确认事件，不重开失败回复、不覆盖受保护检查点或清空错误；实际新结果、异常、问题仍保留主 Bot 的处理责任。
- `reply-failure-facts.mjs` 只承认同一工作、错误之后的 canonical 回复及 delivered 账本；prepared、invalidated、仅新回合、静默等待和其他工作均不能证明恢复。过期或已消费的重试预约不再宣称自动继续。旧 cards.jsonl 的 resolved 不覆盖当前失败事实。
- Renderer 分别显示历史回复失败、暂停、取消、成功回复，以及仍推进的子任务数量；完整原始诊断仍在回复详情中。没有交付凭据的旧 resolved 标记只作为历史错误显示。
- 静默唤醒也建立独立且不可见的 Activity，收尾不改变上一条可见回复、不复制上一回合公开叙述，也不以无模型调用的等待重置提供方熔断器。

完整链路测试使用生产 Runner、工作存储、Inbox、Card Projection、交付账本和实际 Responses 循环；认知为受控 SSE / 执行器，不能宣称上游云模型的空响应已经根治。

## 7. 验收记录

代码：[Peer-Agent #163](https://github.com/ly-ccx/Peer-Agent/pull/163)，当前提交 `a04909a332b0dfc421788eebf11f5fa4674571ab`。ADR 先行提交 `f61dd6a`。本轮未合并、安装或发布 RC。

| 检查 | 结果及边界 |
| --- | --- |
| 主回复与子任务完整流程 | 用户发起 → 普通恢复/运行事件零模型请求 → 持久 waitFor → 重启 → 主回复失败且子任务仍运行 → 后续普通事件不反复调用 → 第二次真实失败仅成为历史 → 结果事件唤醒 → canonical 回复交付 → 旧错误才显示 recovered；生产 Module 集成通过 |
| 模型静默等待 | 实际 Responses 循环、Runtime Projection、Tool Host、Delegation Provider 返回配对结果、PermissionGrant、Evidence 与 terminal control；只发一次模型请求，未因空正文重试，通过 |
| 保守恢复判定 | 新 agent_turn、静默等待、跨工作回复、prepared、invalidated、过期/消费预约均不能证明恢复；暂停、取消、当前失败分别投影，通过 |
| 本地工程 | Runtime 全包 1275 项通过；最后 Activity 身份修正后 19 项集成重跑通过；68 项边界测试通过；build/typecheck/architecture 检查通过。全包记录早于最后 Activity 小修，最终全包以 CI 对应提交为准 |
| 产品回归 | 完整 Capture 后，166 张必查截图经 28 张联系表逐图检查，关键状态另看原图；实现者自审 independent=false；Verify passed，2026-10-18T04:18:35.095Z |
| CI | Linux 当前提交已通过；macOS 首次 Quick Chat 原生菜单夹具发生 Resulting promise was garbage collected，正在同源码单独复跑，尚未宣称通过 |

产品包 runId：`31c5e713-99c4-4fde-88e3-f585cdd9a7c0`。源码指纹：`39f9120e43b0e946fadb70b79d0e6de6216679b082418bbc5b6c5840daaecc4e`。审查和摘要见 [验收证据](../../playbook/v0.1.0/evidence/reply-attempts-state/validation.json)、[逐图审查](../../playbook/v0.1.0/evidence/reply-attempts-state/review.json)。

保留 4 项非阻断发现：Quick Chat 透明离屏浅图不能证明原生浅色对比度；预置旧失败侧栏摘要仍有技术前缀；合成签收场景沿用旧“最近说明”，不用于证明实际签收语义；窄窗暂停帧的回到底部浮钮与详情焦点局部交叠，详情左侧及键盘仍可进入。具体说明在 review.json。不能据这些帧宣称完整读屏或所有窗口原生外观已经验收。

候选过程保留：初稿为 Activity 身份修正取消；中间测试对隐藏 Activity 的断言修正后 19 项通过；最终提交第一次完整 Capture 在 Quick Chat 句柄回收处失败，未接受；同源码完整重试、逐图自审和 Verify 才被接受。真实云模型质量、安装版升级、完整读屏和长期运行仍未覆盖。
