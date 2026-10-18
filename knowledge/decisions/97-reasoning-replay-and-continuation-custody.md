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

### 4.1 真实验收补充：检查点不得覆盖当前 System Context

进一步定位发现：OpenAI 原生检查点保存了旧 system 消息；恢复时整份 messages 覆盖新组装的 System Context。当前唤醒事件、名册、post_reply 交付规则虽已重新组装，却没有实际发给模型。真实模型因此仍按旧用户回合输出普通结束文字，主 Bot 并未正式交付。

恢复 Interface 必须保留原生 assistant reasoning、tool_calls 与配对 Tool Result；同时丢弃检查点中的旧 system 消息，以当前 Context Sources 组装的唯一 system 消息替换。检查点只保留连续执行的事实，不能成为当前系统指令的权威。Anthropic 原生消息本来就与当前 system 参数分离，保持原路径。新规则、事件与名册仍进入既有 Context Sources，不把模型文字或文件内容升级成系统指令。

曾考虑追加一次完成纠正请求；发现上下文覆盖根因后，优先修复恢复 seam，不再增加一层猜测性的模型重试。模型仍须调用原 post_reply 接受源状态、Evidence 与签收校验，不能自动把“已经交付”的普通文字当成正式回复。若仍未提交，保留现有无进展保护，不无限轮询。

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

最终代码提交 `31cb84184c74e2224c7f47042f532f546dcb568a`，实现 [Peer-Agent #167](https://github.com/ly-ccx/Peer-Agent/pull/167)。新增 Reasoning Replay、Continuation Custody、Reported Wait 与 Session Observation Revision Module。旧后台记录通过原子 continuations_coalesced 追加事件转移自动处理责任；旧检查点和预算记录保留。未知新 journal 事件的旧版本拒绝恢复，不能保证降级后继续。用户续接按真实输入时间优先。

真实验收与跨平台集成又发现两处缺口，已在最终源码修复：原生检查点覆盖当前 System Context；canonical 回复组装与签收丢失 observationRevision，导致有效交付被误判过期。当前宿主观察版本完整穿过回复组装、持久交付、签收和展示。未放宽交付校验；模型声明的版本不能覆盖宿主事实。

工程验证：完整 build / typecheck / architecture / pnpm test 在前候选通过；最后协调修改后572项定向测试通过；最终上下文与交付版本修复后桌面集成66项、终端集成10项通过，typecheck / architecture再次通过。最终 CI 的 macOS/Linux 测试阶段通过，桌面交互检查仍在进行。

标准 Capture 的180张截图逐张实现者自审（24张与前候选完全相同 SHA-256，156张重新检查），最终 Verify通过，runId `48915e2b-a6b4-4114-8402-0d58a7bd2153`。不是独立视觉审查；保留三个既有非阻塞局限，见 review.json。

已用现场日志和检查点只读副本检验收敛：约152MB journal，30条 runnable 收敛后剩6条；27条重复后台记录转移责任，用户工作和取消/暂停/系统阻塞记录不变，重启幂等。roster 为冻结身份夹具，不据此宣称用户真实任务已经恢复。

最终源码的全 DeepSeek 真实任务完整通过：主 Bot 派发独立子 Agent、读取并修复隔离项目、实际 node --test 从0通过/1失败变为1通过/0失败、独立复核上下文通过、主对话正式交付并签收。执行中询问获得独立回复；取消另一真实只读任务后能继续回复且没有重跑。捕获27次 DeepSeek 请求，其中26次HTTP200（20次工具结果续跑），一次在取消前未完成；原生推理字段缺失0次、HTTP400为0。

真实 post_reply 去重收据产生持久 reportedWait，指向实际 delivered 消息与当前观察版本；重启后30条人工构造旧结果事件复用实际验收结果，29条转移责任，新用户问题得到回复；静默观察12秒新增模型请求0。执行期间333次操作，输入到绘制p95约5.2ms，帧间隔p95约9.9ms。复核会话独立、模型同源；不把同源性隐藏为跨模型独立审查。

GPT主 Bot / DeepSeek子 Agent组合补验仍在进行。保留所有早期失败尝试，不把它们覆盖成成功。详见[验收记录](../../playbook/v0.1.0/evidence/reply-continuation-repair/validation.json)及[真实任务记录](../../playbook/v0.1.0/evidence/reply-continuation-repair/real-model.json)。日常安装及真实任务未修改；本轮未发布RC。
