# 双向监督与连续工作实施文档

创建时间：2026-10-28
最后更新：2026-10-29

状态：设计已接受；2026-10-28 本批源码已接入。当前实施范围、自测结果及覆盖限制见[工作包回执](code-structure-refactoring.md)。下文保留任务卡及发布验证要求，不等于已通过退出验证。

依据：[ADR 111](../../knowledge/decisions/111-project-agent-duplex-supervision-and-continuity.md)、[设计理念与模块架构](../../knowledge/architecture/25-duplex-supervision-and-continuity.md)、[项目代理实施手册](../project-agent-implementation-handbook.md)、[版本计划](../../design/product/v0.1.0-release-plan.md)。所有代码路径相对于 Peer-Agent 根目录。

下文 `project-agent/` 是 `packages/runtime-node/src/project-agent/` 的目录缩写；同一入口列表中省略目录的文件沿用前一个明确目录。拟新增文件会明确标注，不能把目标文件名误当作现存实现。

## 1. 交付边界与基线

本批实施先实现“子 Agent 出问题后主 Bot 有责、有信息、有可用控制、有真实回执”，再接入换窗与工作笔记。保持主 Bot 读取/协调角色、统一能力执行链和既有 GoalPlan/Conversation/ProjectWorkReceipt，不新建任务引擎或后台监督模型。

研究时代码仓 HEAD 为 `b6e8fe88c90fc56677a404c641c0978da6a64f92`，分支 `PeerAgent/tui-desktop-goal-contract-shared`；知识仓 HEAD 为 `cfa51a26daf69e299cd0fe851354cd7934354645`。两仓均有在途改动，安装版 RC28 与工作区也不是同一构建。上述身份只定位研究现场，不是可直接实施的干净基线。

启动 D0 时记录实际提交、分支与相关 PR：

| 前置契约 | 要核实的内容 |
| --- | --- |
| ADR 89/91/93/94 | 父子消息、协调 mandate、接手、修复责任和主回复/子执行分离 |
| ADR 97/99 | Provider continuation custody、权威输入/回复回执 |
| ADR 100/101 | 问题与 Attention 去重、Bot 自有能力政策与执行准入 |
| ADR 102/103/110 | 单一 lifecycle/followUp、停滞治理与核验收口 |
| ADR 104 | 增量协调存储、轻量查询、lease、崩溃恢复与兼容 adapter |

逐项登记“已合并 / 在途 PR / 仅设计 / 需补齐”，不要以文档存在代替代码已交付。依赖未合并时可以在明确的隔离基线上准备改动，不得覆盖别人的脏文件或另实现一套同名机制。A-level 契约以 ADR 111 为先；发现新增边界先修订 ADR。

## 2. 协议增量与命名边界

以下表保留设计概念，当前实际落点以 §2.3 为准。使用既有 ID/引用类型，不为设计概念机械建立重复对象或别名。

| 对象 | 核心字段/不变量 | 建议位置 |
| --- | --- | --- |
| `InterruptionFact` | 宿主来源、scope、session/attempt/epoch、goalRevision、停止确认、未决副作用引用、发生时间 | Protocol 监督契约；由现有执行/停止事实派生或引用 |
| `AgentDecisionRequest` | requestId/revision、问题、options/answerSchema、responder、阻塞范围、材料与目标绑定 | 既有 AgentMessage 的可辨别载荷 |
| `AgentDecisionAnswer` | answerId、requestId、expectedRequestRevision、optionIds/text、可信来源引用 | 同一通信契约，条件提交解决问题 |
| `AgentDeliveryIntent` | `mailbox_only` / `ensure_turn`，接收范围与幂等键 | 现有发送参数与耐久 outbox |
| `AgentCommandReceipt` | operationId、目标版本、delivery/admission/effect 分维度回执、事实引用 | 复用 work coordination 操作记录与查询 seam |
| `ContextWindowRecord` | windowId、前窗引用、历史游标、Hint/Notes refs、开放义务 refs、budgetRef | 工作上下文契约，不能复用 executionEpoch |
| `WorkNoteRevision` | noteId、revision、author、scope、内容引用、来源、supersedes | 设备侧工作正文及版本事件 |

优先扩展 `packages/protocol/src/delegation-coordination.ts`、`work-coordination.ts` 及既有通信类型；内容形成独立完整 Interface 时可增加 `agent-supervision.ts`，由旧入口导出，避免继续堆积无关类型。

### 2.1 工具入口

- 扩展现有 `local.delegation.send_agent_message`：普通文本保持兼容，新增结构化问题/答案与可选 delivery。旧普通消息默认不唤醒；原有父代理回答恢复行为显式编码并保留原准入规则。
- 扩展既有 `coordinate_work` 的恢复表达。已增加 `resume` action，要求 mandate、当前 expectedRevision 及执行绑定；宿主重检目标 attempt/epoch 与关联问题/失败引用；`handoff` 继续负责更换执行者。最终公开 capability ID 与参数名以 D0 的现有 Manifest/Tool Spec 对照为准。
- `query` 通过既有能力返回有界状态、开放问题和操作回执，不把完整 ledger 当作默认输出。
- D5 已增加工作笔记/历史检索 Provider adapter，使用 `local.continuity.read_notes`、`write_note`、`search_history`。2026-10-28 已连同 prepare_handoff 注册；须持续保持完整接入 Manifest、Runtime Projection、Tool Call、PermissionGrant 与 Evidence，不直接暴露 fs。

不能把既有用户手动恢复工具的权限默认值照搬给主 Bot。主 Bot 的恢复依据是原目标内有效 CoordinationMandate，工具执行权限仍由本地政策与 PermissionGrant 决定。内部 outbox 的恢复也不能成为模型绕过能力入口的方法。

### 2.2 请求与回执的提交顺序

```text
校验身份、范围、版本与幂等键
  → 持久提交消息/答案事实及其待处理义务
  → 更新可重建的收件/问题/恢复索引
  → 发布事件、尝试调度
  → 准入前重检停止、lease、预算与当前目标
  → 接收方上下文纳入 / 执行实际开始
  → 追加对应回执，消费已被覆盖的义务
```

上述流程跨模型执行与工具副作用，不宣称单个数据库事务可以包住全程。将“新监督信封和待唤醒义务”放入同一持久事件的原子语义；请求解决与恢复义务同样一次提交。正文先写不可变 blob；Conversation 中的相应记录只是带 messageId/sourceRef 的投影，丢失后按日志重建，不能再生成一条独立消息。旧 AgentMessage 经 Conversation 兼容 adapter 读取，不能强制转存历史。回执跟随真实事实分别落盘。若日志已落盘而索引未提交，沿 ADR 104 返回可查询的 `durable_pending_projection` 与 operationId，先恢复投影，不能把它作为可重新派发的普通失败。

### 2.3 当前冻结的实现落点（2026-10-29）

下列为本批实际 Interface，优先于任务卡中的早期建议文件名与字段草案。D0–D6 的核心源码已经接入；任务卡的退出条件仍区分本地自测与发布验收。

| 范围 | 实际落点与约束 |
| --- | --- |
| 中断与责任 | `packages/protocol/src/agent-supervision.ts` 的 `InterruptionOrigin` 扩展现有 `GoalRunnerState.interruption`；`task-overview.ts` 的唯一 lifecycle/followUp 出口保留技术、人工与未知事实。不另建 `InterruptionFact` 或第二个义务状态机。 |
| 信箱与回执 | `project-agent/agent-delivery.mjs`、`agent-supervision-communication.mjs`、`agent-supervision-state.mjs`，复用 `work-coordination-store.mjs` 和 coordination-v2 journal/blob。信封、开放请求和待处理义务同一次提交；delivery/admission/effect 独立记录。 |
| 真实观察 | `agent-communication-source.mjs` 只将本次 L7 factual Source 实际纳入的 ID 标为 observed；旧 pending 与最近历史合并有界读取，120 条消息及删索引回放用例防止早期消息饥饿。 |
| 工作问题 | `AgentDecisionRequest/Answer` 保留 request revision 与 optionId；消息 ID 是宿主赋予的操作/答案身份。原生 `post_reply.question` 与升级关联原子提交；人工答案只取当前真实 `user_input.answerTo`，普通后续对话不能代答。 |
| 恢复控制 | 扩展现有 `coordinate_work` 的 `resume`，继续 TaskTransition/SessionTakeover/GoalRunner seam；不新增 execution-control 执行循环。原 work、预算、检查点与核验义务保留，epoch、停止、人工门和未知工具结果仍阻断过期动作。 |
| 工作上下文 | `working-context.mjs`、`working-context-provider.mjs`、`working-context-specs.mjs` 与 `execution-context.mjs`。Provider 能力为 `local.continuity.read_notes`、`local.continuity.write_note`、`local.continuity.search_history`、`local.continuity.prepare_handoff`，对应模型工具为 `read_work_notes`、`write_work_note`、`search_work_history`、`prepare_context_handoff`。 |
| 笔记与历史 | 笔记按 work/conversation 作用域 CAS 修订，正文先落不可变 blob，引用仍是事实材料；历史使用 native page 与受限父子边界。敏感正文不成为全局搜索片段，缺源返回明确失败。 |
| 换窗边界 | `prepare_context_handoff` 只得到 `state=prepared / providerWindowChanged=false`；开放问题、预算与未知 dispatch 引用连续。实际 Provider 压缩或换窗仍由已有 encoder/checkpoint 负责，不能用 prepared 记录冒充已经换窗。 |
| 格式与宿主 | 沿用 schema/storageVersion 2 和物理旧 writer fence，新增监督记录要求最小 reader/writer 5；Desktop/TUI 共用 Provider → Manifest → Projection → Tool Call → PermissionGrant → Evidence，不把 fs 或控制权交给 Renderer。 |

构建、完整范围分段测试、隔离 Electron、逐图审查及测量限制以[实施回执](code-structure-refactoring.md)登记的最终候选为准；没有部署、安装或重启用户实例。

## 3. 实施任务卡

### D0：冻结契约与兼容基线

**入口**：现有通信、工具 spec、协调 store、Protocol 与上述依赖文档。阅读 `packages/runtime-node/src/data-store.mjs` 的分类，确认 projectRuntime 与 cache/portable 的边界。

**工作**：建立实际字段与新增字段对照；确认问题类型、delivery 默认值、operation 幂等键、lease/epoch 校验点、schema/min-reader/min-writer 与历史兼容。记录各 Provider 的原生续接、回合中信息纳入、结构化中断能力，不支持的能力明确降级到下一回合边界。

**退出**：有唯一协议表与迁移方案；没有同名第二状态机；后续卡的依赖提交可定位。不会因添加 optional 字段就默认旧 writer 安全。

### D1：责任判定贯穿投影与调度

**入口**：`packages/protocol/src/task-overview.ts`、`delegation.ts`；`packages/runtime-node/src/project-agent/repair-ownership.mjs`、`runner-coordination.mjs`、`session-supervisor.mjs`、`event-mapper.mjs`。

**工作**：把可信中断来源送入原 lifecycle/followUp 出口；调度修复候选读取同一判定。failed、技术 interrupted、开放父代理问题、恢复未决与未知事实保留 Bot 跟进；用户明确暂停仍不自动恢复。修正主 Bot 正常回复后过早 delivered/收口的路径，但不把“用户消息已回复”与“工作未完成”混成同一个回执。

可增加 `supervision-obligations.mjs`，Interface 仅接受带版本的 canonical 事实与唯一 followUp，返回可处置义务及去重键；它不再解释一套状态字符串、不持有独立任务状态，也不自行执行恢复。

**退出**：列表、计数、调度对同一组事实产生一致的责任归属；主 Bot 本轮结束后开放义务仍可被后续调度发现。不能仅把 failed 改成 waiting_agent 掩盖执行失败。

### D2：可靠信箱、唤醒与消费回执

**入口**：`project-agent/agent-communication.mjs`、`work-coordination-store.mjs`、`goal-runner-host.mjs`、`runner.mjs`、`execution-scheduler.mjs`；`packages/system-context/src/sources/agent-communication-source.mjs`。

**工作**：扩展原消息 envelope；使用 coordination-v2 记录 message committed、wake intent、context observed、admission 和 effect。接收方使用宿主序号与实际纳入消息 ID 建立游标。运行中到达而未纳入上下文的消息不得因已有活跃回合被误消费。

统一查询 seam 合并旧 Conversation 消息与新日志信封，返回明确 source kind/ref，并按稳定 ID 去重。所有消费端（模型上下文、父代理观察与界面详情）都从该 seam 读取，禁止依赖 Conversation 镜像一定已经写入。纯信息消息的 admission/effect 不适用，不能误列为恢复未决。

从 `agent-communication.mjs` 拆出确有完整职责的 `agent-delivery.mjs`，集中 outbox 恢复、版本去重与回执查询。Interface 可为 `commitDelivery`、`reconcilePendingDeliveries`、`recordContextObservation`、`readDeliveryReceipt`；具体持久化仍在原 store 内，不新建文件队列或数据库。

**退出**：mailbox_only 不启动空闲目标；ensure_turn 不绕过停止/授权；重复通知不重复启动；崩溃重启可区分未入箱、已入箱待调度、实际已启动。工具正文和 UI 都不能把 queued 表达为 resumed。

### D3：父代理优先的结构化工作问题

**入口**：原通信模块、`project-agent/tool-specs.mjs`、`delegation-provider.mjs`、`prompts/delegation/send_agent_message.md`、`packages/runtime-node/src/goal-runner.mjs`；既有请求卡/Attention 投影入口。

**工作**：增加 AgentDecisionRequest/Answer 解析、option ID 校验、请求版本与一次有效解决的条件提交；问题向父代理发送，主 Bot 可回答或升级。子 Agent 不通过 `request_user_input` 伪装普通内部问答。真实用户请求、PermissionGrant、manual DoD 与结果人工验收保持原生入口。

答案与恢复义务同一原子提交。用户升级请求与原 question 通过稳定引用合并成一个待答对象；答复到达时校验当前 request revision、目标与停止状态，不能从随后的任意对话推断答复。若答案已解决而恢复失败，只保留恢复责任。

**退出**：普通选择题由主 Bot 接手；只有真实人工事项增加 Attention；旧用户问题不自动重分类，旧选项答案不能解决新问题。工具说明与 System Context factual source 同步，不能把子 Agent 消息提升为系统指令。

### D4：受控恢复与接手

**入口**：`project-agent/coordination-lifecycle.mjs`、`session-takeover.mjs`、`session-supervisor.mjs`、`recovery-policy.mjs`、`runner-coordination.mjs`；`packages/protocol/src/delegation-coordination.ts`。

**工作**：把 resume/handoff 的校验和效果确认收束在既有控制 seam；如需新 `execution-control.mjs`，应集中停止边界、epoch fencing 与未决副作用判定，不再建立执行循环。resume 继续原工作，是否新建物理 attempt 由原 runner/native continuation 契约决定；handoff 必须绑定新的执行 attempt。两者不能重置工作预算与核验义务。

同一工作只允许有效 lease 的宿主提交当前控制；准入时核对 expectedGoalRevision、attempt/epoch 和取消状态。发生未知 dispatch 时进入 awaiting_outcome 并先核对。取消/修订需在下一次工具准入点阻止过期动作；不能只等模型读到通知。保留既有 TaskTransition 的 phase，不把既有“消息提交完成”改造成虚假的“执行恢复完成”；新增执行效果回执与其关联。

**退出**：恢复请求成功与真实执行开始可分别查询；旧 epoch 不改变新执行；用户暂停不被普通消息解除；Provider 无法安全继续时明确失败/阻塞并交还责任，而非反复新建任务。

### D5：Hint、Notes、History 与换窗

**入口**：`packages/protocol/src/system-context.ts`、`packages/system-context/src/sources/work-session-source.mjs`、`agent-communication-source.mjs`、现有 Context Source 注册与 Provider encoder/checkpoint seam、`packages/runtime-node/src/data-store.mjs`、协调 store。

**工作**：新增 working-context Module，Interface 为有界读取、笔记条件修订、历史检索与窗口交接。笔记正文先保存不可变 blob，再提交版本引用；并发旧 revision 返回冲突并保留旧版。写笔记属于完整能力调用，不是模型直接写系统提示。

Main Bot 的笔记写入只允许命名明确的本工作运行时对象；在 Manifest/Projection/本地政策定义其角色准入和事实记录，不把只读角色扩成任意项目写入。工作 Agent 与主 Bot 都不能通过 noteId/path 参数逃逸至项目文件或其他工作的笔记。

按工作/父子范围控制访问：工作 Agent 只读取被授予的本工作材料；主 Bot 读取其有效 mandate 范围内材料。History 不开放全局私密会话或跨 Bot 内容；模型准入前沿既有附件、敏感数据和来源政策过滤。清理索引不删除 canonical 历史与已引用正文。portable 对话引用设备侧记录却缺源时明确返回 source_unavailable，不能从展示副本自动续跑；跨设备监督状态迁移另行设计。

窗口交接记录独立 windowId、历史游标和开放义务 refs，再生成 Hint。摘要失败可从结构化事实构建最小工作集。Hint、Notes、历史以 factual Context Source 进入，不新增 Developer/System 高权限通道。工作 usage/budget 连续累计；不照搬参考文章的固定 token 阈值、4 KB Hint 或 fork 历史轮数。

**退出**：可以依原始引用核实笔记；换窗后不重复向用户提问、不遗忘恢复、不重放未知工具；Provider checkpoint 不可移植时明确走新窗而非伪造续接。

### D6：多宿主、增量观察与产品表达

**入口**：既有 desktop/TUI shared host 与 IPC/protocol seam、调度器、轻量查询、Renderer 的 `project-agent/state/botWorkState.ts` 与任务详情/提问入口。实现前重新核对实际文件位置。

**工作**：界面仅消费同一 lifecycle/followUp/操作回执；共享宿主消费同一控制与投递机制。局部订阅按 work/request/operation 更新，卸载取消、读版本与迟到丢弃沿既有规则。主 Bot 只在关键事实变化时唤醒；保留既有 coordination/work 执行分道，容量为 1 时安全交替，不长期持锁等子 Agent。

用户流记录：目标=委托后持续推进；状态=执行、待 Bot 决策、恢复排队、实际恢复、真实待用户、停止未确认、核验；事实源=宿主日志与唯一投影；控制=补充、回答、停止、查询；恢复=同一任务上下文与已答事实。后台更新不抢焦点、不恢复用户已关闭的自动滚动，保留草稿/IME/阅读位置。

复用 Frost、SVG、共享动效与原 reducer/kernel seam。实施时更新体验覆盖矩阵及 UI/动效/过渡矩阵，将“静态实现”与“发布验收”分别登记；本轮设计不提前标记矩阵已完成。

**退出**：Desktop/TUI 看到一致的责任与回执；界面没有补造恢复成功或用户授权；监督没有新增全量热读取和按 token 唤醒模型。

## 4. 故障窗口与发布用例

以下是必须实现的场景及验证设计；初次设计时尚未运行。用户随后明确要求“全部完成再自测没问题后提 PR”，本批因此提前执行构建、测试、类型/架构/IPC 和隔离产品回归，实际范围与限制见[实施回执](code-structure-refactoring.md)。普通开发仍遵守默认约定，未获明确提前验证请求时只做实现内容/diff 审阅，完整执行留到发布。

| 场景 | 必须核对的结果 |
| --- | --- |
| 消息已提交、进程在发布唤醒前退出 | 重启恢复同一 outbox；没有丢消息或无依据的新目标 |
| 日志已持久、索引事务失败 | 返回 durable_pending_projection；重建后查原回执，不再次启动模型或工具 |
| 实际启动后、效果回执前退出 | 先核对既有 attempt/lease，不能重复执行 |
| ensure_turn 在运行中、上下文快照之后到达 | 不误标 observed；后续边界或下一回合覆盖该消息 |
| mailbox_only 发给空闲目标 | 入箱但没有自动启动 |
| 旧 goalRevision/epoch 的消息、答案、停止结果迟到 | 保留历史/拒绝回执，不改变当前执行或新问题 |
| 两个答案并发提交、答案和取消同时到达 | 一次有效解决；根据提交顺序和当前停止事实控制准入 |
| 普通选项、真实用户问题、权限与人工完成检查 | 父代理路由和人工边界准确；Attention 不重复计数 |
| 用户已回答后恢复失败 | 已答事实保留，Bot 接手恢复，不重复要求用户回答 |
| 技术中断与用户暂停外观同为 paused | 归属依可信事实；未知来源不自动恢复 |
| 未知工具副作用、lease 丢失、跨宿主接手 | 先核对/fence；旧宿主不能继续提交有效控制 |
| 主 Bot 回合失败、资源满载、容量为 1 | 责任不丢，有界重试与公平推进，不出现无限监督循环 |
| 压缩失败、Hint/Notes 过期、上下文换窗 | 最小事实可恢复；预算、问题与未知 dispatch 不重置 |
| 索引删除重建、旧数据缺字段、旧 writer 试图写入 | 事实可回放，保守兼容；不静默抹除新义务 |
| 子消息或笔记含伪造系统指令/用户批准 | 只作不可信事实处理，不获得执行权限 |

## 5. 存储与性能验收设计

复用 ADR 104 的事件大小、blob 引用、分段和读版本机制。实际已实现的 60 KiB 正文外置阈值与 64 KiB 元数据事件上限不能混淆；新增契约在 D0 核对当前版本，不另复制一组硬编码阈值。关键提交不能 debounce 后先报成功。

发布时记录下列实测，结果未知时写未知，不以目标值当通过：

- 无关历史增长 10 倍时，当前工作状态/问题/回执查询的扫描范围仍有界；热路径不读取全 ledger 或全部 checkpoint。
- 固定大小新消息/进度的追加元数据近似线性增长，索引与大正文成本分列；不为保存一个回执重写所有历史结果。
- 关键事件提交到主 Bot 获得调度、恢复准入到实际开始的分段耗时，按等待预算、模型资源与 Provider 网络分别解释。
- Renderer/main 事件循环、查询 p95、持久提交耗时、读写字节与内存；对照同一候选、机器与数据规模，不能只测脱离 Electron 的 JSON 序列化。
- 纯进度更新引起的主 Bot 模型调用数和界面刷新范围；关键人工事项及时可达，展示合并不能吞掉最终状态。

本批不能通过关闭 fsync、删除 Evidence、忽略未知结果或取消权限检查换性能。最初“整个界面都慢”的问题需与其他性能任务共同测量，本设计只承担本批新增/修改路径的责任。

## 6. 兼容、启用与回退

1. 新 reader 先支持旧记录：缺 responder 的旧用户问题仍是用户问题；缺 delivery 的普通旧消息不新增唤醒；缺中断来源的记录保留 unknown。
2. 新 writer 启用前检查工作存储 schema 与宿主最小读写版本，拒绝无法保留新字段的旧 writer；能力 projection 也必须与实际实现一致。
3. 按任务卡依赖启用；D1–D4 可先交付完整监督闭环，D5 的上下文功能独立启用。不能用开关隐藏已经持久化的开放义务。
4. 回退先关闭新自动唤醒入口，核对活跃执行、问题与 outbox，转交兼容宿主或明确人工处理；保留所有事实。激活后不能直接切回旧日志最后状态继续执行。
5. 不迁移用户数据来演示功能，不自动安装或重启用户当前应用。发布包、日常数据和实验夹具的覆盖范围分别说明。

## 7. 发布收口

发布新版本/RC 前盘点并合并代码仓全部开放 PR（含草稿和其他目标分支），阻塞 PR 就阻塞发布。合并后冻结唯一最终候选，再运行完整 build、tests、typecheck、architecture/IPC 与完整产品回归；推 tag 前再次确认开放 PR 清空。

产品回归使用 `pnpm qa:product:capture --output <仓外临时目录>`，AI 检查全部要求截图并写入 `review.json`，再运行 `pnpm qa:product:verify --output <同目录>`。实现者自审不得称独立审查；真实模型、安装包、跨平台与可访问性未覆盖的部分明确记录。故障恢复用例需要真实事实断言，截图不能替代。

原设计文档交付仅做内容/diff 与引用审阅。用户随后明确要求“全部完成再自测没问题后提 PR”，本任务因此获准提前运行构建、测试、类型/架构/IPC、隔离产品及性能验证；结果以[本批回执](code-structure-refactoring.md)为准。未创建版本或 RC 发布；后续发布仍需在全部 PR 合并后的最终候选重新完成门禁。设计接受、源码实现、自测通过和发布验收分别记录。
