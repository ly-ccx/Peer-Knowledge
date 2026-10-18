# ADR 97：推理回传、续接归属与已汇报等待

日期：2026-10-18
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
