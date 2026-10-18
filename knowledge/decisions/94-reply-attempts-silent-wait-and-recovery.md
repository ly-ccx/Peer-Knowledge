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
