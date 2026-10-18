# ADR 97：推理回传、续接归属与已汇报等待

创建时间：2026-10-18
最后更新：2026-10-18
状态：Accepted（用户要求修复三条链路并用真实任务验收）
级别：A（Provider 上下文、持久协调状态），B（主 Bot 调度）；继承 ADR19、88、91、93–96。

## 1. 现场与目标

RC17 已安装。一次 DeepSeek Chat Completions 工具续跑返回 HTTP400：缺少 reasoning_content。主 Bot 的新询问已进入独立工作并查询过当前状态，但之后轮转到旧结果事件对应的多个 runnable 工作；现场有30条 runnable。多次 post_reply 返回 facts_already_reported，界面没有新增回复，waiting_agent 又把工作设为 runnable。旧事件、主回复、子执行、复核失败各自真实，但没有统一的续接归属和等待收尾。

目标：保留真实推理与配对工具结果；每个子任务结果范围只有一个自动处理者；已有正式汇报可以结束重复唤醒并等实际变化；新用户输入必须得到自己的回复。不能用关闭思考、扩大权限、清空预算或伪造通过来恢复。

## 2. Provider Replay Module

Interface：现有 Provider encoder 接收原生 assistant reasoning_content；OpenAI Chat 工具循环把该次真实响应推理与 tool_calls 一起保存到 native checkpoint。Desktop 与共享 adapter 使用同一 encoder seam。

DeepSeek tools + thinking 要求所有 assistant 推理回传（含无工具的历史轮）。不能从可见摘要、助手解释或另一模型内容拼造推理。旧历史缺失原生字段时，wire adapter 将该历史 assistant 与紧随其后的已配对 Tool Result 一起表达为带标签的普通历史数据；不发成可执行工具调用、不转为 system、不改写 canonical 历史。已存在的真实字段（包括明确空字符串）完整保留。无工具和其他 Provider 不受此历史适配影响。旧 checkpoint 同样经过 encoder。新产生的工具结果继续由原有 Runtime/PermissionGrant/Evidence 配对，不重放已完成工具。

依据：[DeepSeek Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)。

## 3. Continuation Custody Module

Interface：协调恢复前，在当前租约内按 parentConversationId 与子任务范围收敛重复的后台 report_available 唤醒。新增 coalesced 状态及 continuationOwnerWorkId 审计关联，明确不是回复已交付或子任务已取消。原检查点、用量、错误和交付账本保留；采用追加式 journal 回执，重启幂等。

只允许合并同范围纯后台结果工作；用户输入工作、取消/暂停、未知派发、未配对工具、人工控制、失败恢复预约、未决交付、其他事件类型不进入合并。保留较新的安全检查点为自动处理者，累积无进展事实不因换 workId 清零。新结果唤醒复用安全处理者，不产生另一份自动责任；事实仍以当前宿主 roster 为准。用户续接优先于后台恢复，避免旧事件队列饿死新问题。已结束或取消的子任务不因收敛重新运行。

## 4. Reported Wait Module

post_reply 去重返回已汇报的 canonical reply IDs 和当前源版本。协调端再次检查 delivered 账本与 canonical 消息，只有同项目、覆盖相同事实的真实交付才可形成 reportedWait。缺少依据时走既有无进展保护，不能声称已回复或恢复。

后台重复汇报结束本轮，并持久等待相关源版本/状态的实际变化；不因 waiting_agent 单独重新设为 runnable。当前已交付问题可以保持等待用户，但不改写子任务的技术阻塞。新结果/异常/用户输入仍能唤醒；当前用户输入不被去重历史吞掉。取消/暂停/未知执行结果优先，不能被等待解除。静默等待不是成功恢复，也不添加新的可见“完成”消息。

去重基于宿主事实，文字改写不是新进展；新的用户问题或需要用户决策的不同问题不能只凭相同任务版本隐藏。

验收所用 sourceRevision 与汇报所用 observationRevision 分开：后者包含稳定的实际核验错误、阻塞原因和结果说明，排除尝试 ID、时间与随机请求编号。超时变为 HTTP400 必须成为新事实；同因重复尝试不能续租。策略签收不改变本次汇报版本，避免交付收据自行失效。

后台观察者与创建子任务的工作拥有不同 workId。等待工具仅在同项目/父会话且协调账本已把该事件交给当前工作时承认观察归属；模型传入一个 sessionId 或伪造事件不能获得此资格。这只允许等待，不授予子任务执行或文件权限。

### 4.1 真实验收补充：未提交的后台结束文字

真实模型在结果已核验后仍可能仅输出“已经交付”的结束文字，没有调用 post_reply。普通文字不能成为交付凭证。对带实际结果事件、尚无正式交付的后台回合，协调端可在同一次预算内发起一次完成纠正，并通过显式 Project Agent Context Source 告知宿主未收到正式回复。模型仍须调用原 post_reply 接受源状态、Evidence 与签收校验；不得自动把该文字变成已交付消息。每轮最多纠正一次，停止、失败、时间片让出和用户抢占保持原路径；仍未提交时走现有无进展保护，不无限轮询。

纠正只包含宿主生成的状态标志，不把原始模型文字、工具输出或附件升级成系统指令。新结果/当前问题必须由原回复链交付；已交付且同版本的事实仍走静默等待。真实验收必须区分“子任务完成”和“主回复已提交”。

## 5. 热路径与边界

Journal recovery 只在文件版本变化且确需尾记录修复时读取正文，不能每次 kick 全读151MB journal。沿用增量 reader、租约、fsync、严格 reducer 与损坏拒绝；不另建权限、执行、IPC 或 System Context 旁路。Renderer 本次无需新增权限真值。

## 6. 实施与验收

顺序：ADR → 失败复现 → 推理回传 → 归属收敛/新输入优先 → 去重等待 → 定向与包级检查 → 隔离真实模型任务 → 证据。

必须覆盖：

- DeepSeek 连续多轮工具调用，真实推理逐字回传，切片/重启保留；旧缺失历史转数据，不伪造推理、不重放工具；其他 Provider 原请求不变。
- 30条旧同任务唤醒收敛、重启幂等、不同任务/用户输入隔离、未知派发/取消/暂停不误合并、新事件不丢、新用户询问优先。
- 已汇报后台进入静默等待、零重复模型轮询；状态/版本变更再推进并交付；当前用户询问必有新回复；没有 delivered 回执不能声称恢复。
- Provider/工具失败、超时、取消仍有结构化结果与 Evidence；不得放宽验收条件。
- 使用真实配置模型在临时项目走主 Bot → 子 Agent → 读取/修改/测试 → 复核 → 主回复，并发送进度问题、验证取消后可对话；真实请求必须包含 DeepSeek 工具续跑。日志不得保存密钥或用户历史。

实现者自验必须明确标注；源码 Electron、正式安装包、真实模型与受控场景各自说明覆盖。当前用户数据只读用于定位；不手工清库、不取消用户真实任务。发布或替换日常安装不属于本次请求。

## 7. 实施与工程记录

代码提交 `c7dd40575184d6002e2d968a0a42b65931e7ba3b`：新增 Reasoning Replay、Continuation Custody、Reported Wait 与 Session Observation Revision Module。旧后台记录通过原子 continuations_coalesced 追加事件转移自动处理责任；旧检查点和预算记录保留。未知新 journal 事件的旧版本仍拒绝恢复，不能保证降级后可继续。用户续接按真实输入时间优先，不能仅按不断更新的执行时间排队。

已用现场日志和检查点的只读副本检验收敛：约152MB journal，30条 runnable 收敛后剩6条；27条重复后台记录转移责任，用户工作和取消/暂停/系统阻塞记录不变，重启幂等。roster 为冻结身份夹具，不据此宣称用户真实任务已经恢复。

代码 PR：[Peer-Agent #167](https://github.com/ly-ccx/Peer-Agent/pull/167)。完整 build / typecheck / architecture / pnpm test 已通过；最后观察者等待与 observationRevision 改动后，572 项定向测试和 typecheck / architecture 再次通过。标准 Capture 的180张截图逐张实现者自审，Verify通过（不是独立视觉评审）。

真实模型完整流程仍在验收。已经确认 DeepSeek 多次原生工具续跑 HTTP200，实际推理字段齐全；保留 GPT 空 SSE 响应、DeepSeek 主 Bot 未调用正式交付工具而触发无进展保护等失败，不把子任务通过当成主回复通过。最终结果补录在[验收记录](../../playbook/v0.1.0/evidence/reply-continuation-repair/validation.json)。日常安装及真实任务未修改。
