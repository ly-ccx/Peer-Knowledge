# ADR 99：权威回复回执、模型切换恢复与历史详情

创建时间：2026-10-19
最后更新：2026-11-15（修正 Architecture 文档引用；明确主 Bot 模型重基与 `work_session` 冻结分工的边界）
状态：Accepted（用户要求查明连续失败根因、修复、自主验收并发布 RC）
级别：A（执行事实与展示边界），B（主 Bot 续接）；继承 [System Context 架构](../architecture/19-system-prompt-context-architecture.md) 与 [ADR 94](94-reply-attempts-silent-wait-and-recovery.md)、[97](97-reasoning-replay-and-continuation-custody.md)、[98](98-large-history-execution-responsiveness.md)。

## 1. 现场证据

只读检查 RC18 的实际 Peer RSI 对话：两次 post_reply 完整返回为成功，序列化长度分别 9420、9142 字符；UI stream 的 4000 字符裁剪把它们改为 truncated_tool_result_preview。AgentTurnExecutor 却从这个展示事件收集执行结果，finishAgentTurn 因缺少结构化 ok/message 而拒绝正式回复，随后生成错误卡并累计熔断。短回复测试未覆盖阈值，之前小任务成功不能证明日常长回复可靠。

另一回合真实发生 continuity_model_changed：当前配置变更后仍把旧模型原生检查点传给新 Provider。适配器拒绝跨模型回放本身正确，缺少的是协调层安全的新认知续接。另有真实 verifier_timeout；不能把超时伪装成成功，也不能再把最终解释性回复因预览截断丢掉。截图中的历史错误详情只在当前可见 rows 查找，错误折叠或分页后实体仍在但详情找不到。

## 2. Module 与 Interface

### 2.1 Authoritative Tool Receipt

复用本地 agentProgress.onToolExecution Seam，消费既有完整 CapabilityExecution（ToolCall、PermissionGrant、ToolResult、Evidence）。仅已配对的本回合 toolCallId 和已登记的 delegation post_reply / wait_for_sessions 能更新控制回执；拒绝、取消、超时保持原状态。AgentTurnExecutor 使用本地完整回执覆盖同 ID 的 UI 预览，原 sink 仍只收原有有界事件，不向 renderer 额外广播完整数据。不得解析 preview 字符串寻找 ok、不得从模型参数构造宿主验证成功。回执存储和正式交付继续使用原 reducer、canonical 消息与 delivery ledger。

### 2.2 Model Recovery Admission

Provider 的原生跨模型拒绝保持。协调层比较当前已解析 selection 与检查点 provider/providerId/model。完全相同则原生续接；不同且所有历史工具均已配对、账本无未知副作用时，启动同一 work 的新认知步，沿用实际 Tool Result/Evidence 的 bounded retryContinuity、当前上下文和用量，不回放旧调用、不重建原生 reasoning。未配对/未知派发继续阻止自动续接。旧 checkpoint 保留以供追溯。新模型自己依据当前事实决定后续操作，不能冒认旧轮交付成功。

> **三层切换作用域澄清（2026-11-15 对齐）**：本节 `continuity_model_changed` 重基机制**仅适用于主 Bot（`project_agent`）**；受委派运行中的 `work_session` 子任务继续严格冻结在其 `spawn_session` 快照 `DelegationOrigin.modelSelection` 上（[ADR 83 §5](83-model-routing-by-role.md#5-开任务时冻结)），仅在步骤边界遇到不可用故障时可在角色过滤候选中切换，或由主 Bot 经 `ADR 91` 新派替代尝试换模型；单次底层传输重试仍遵循 [ADR 30](30-provider-recovery-broker.md) 同模型锁定。

### 2.3 Terminal Response Guard

真实大历史验收再次出现 unsupported_tool_response。追查共享终态守卫发现其把“tool result / exitCode / I verified / 我检查了”等普通复核报告用词一律当成未执行工具声称，完全不看前面实际配对的 Tool Result。它不只检测协议标签；因此原报错“协议文本”也不准确。使用真实工具结果后的普通总结必须可以进入报告解码与 Evidence 校验；没有工具结果的空执行声称、下一步行动旁白、正文伪工具标签仍拦截。事实真实性仍由 CapabilityExecution、Evidence、Verifier decoder 和 host acceptance 判断，不能由一个正文关键词充当完成门禁。共享 kernel 向守卫传入原生历史中是否存在结构化工具结果；不解析普通正文为工具，不把允许文本等同验收通过。

### 2.4 Foreground Input Admission

第二轮大历史真实任务完成修改、18项测试、两层实际复核、正式回复与 accepted；随后后台 wake 已在发请求，新用户消息虽入队，却要等该后台请求返回才有机会执行，取消验收两分钟未派发。新输入须能抢占无活跃工具派发的后台认知请求：调用既有 AbortSignal，旧工作按 yielded 保存保护检查点，事件继续归原 work；新输入不能继承旧批次，已完成工具不重放。有活跃工具或未知副作用时不擅自中断派发，仍由既有完整结果/取消/超时及 ledger 收尾。此变化不取消子任务，也不把正常调度抢占当成用户可见错误。

真实取消后的长回复验收发现同一问题还存在于自动续接的旧 user job：它保留原 kind=user，不能仅凭 kind=wake 判断后台身份。自动 continuation 的无活跃工具认知请求同样允许新输入抢占，原用户工作的事实与检查点保持独立。首次执行的前台用户回合仍在工具结果安全点让出；不将所有用户请求无条件取消。foreground-input 的中断原因在异常和普通终态两条路径均归类为调度让出，不计入失败熔断。

### 2.5 Provider Stream Lifecycle

The recovery run admitted a new user work but remained in one Provider request with zero tool dispatches. The compatibility Chat consumer records `[DONE]` without ending its read loop. A connection that remains open therefore withholds already received tool calls from execution. Reads also do not race AbortSignal, and cancellation/idle cleanup awaits reader.cancel indefinitely. A reader that never closes and never settles cancel reproduces both defects deterministically.

The shared SSE reader Module settles on the first protocol terminal, EOF, cancellation, timeout or error. Cleanup must not hold the business terminal open; late data must not emit events or dispatch tools. Chat Completions, Responses, Anthropic and Gemini share the read/cancel Seam. Preserve authentic usage, paired calls, partial output and replaySafe; partial failures cannot automatically replay. End a Chat stream on `[DONE]` without waiting for TCP EOF. This changes no permission or Evidence authority.

The Desktop connection-timeout adapter also removed its parent abort forwarding as soon as headers arrived. A deterministic test confirms that later caller cancellation never reached the response-body signal. Compose the connection deadline and caller lifetime with AbortSignal.any so cancellation remains authoritative through the complete body while the connection timer still stops at headers.

### 2.6 Historical Reply Details

详情选择按 canonical message identity / turnId 从已加载消息建立展示投影，不依赖该行是否因历史折叠而出现在聊天 rows；未加载的实体通过现有 conversation pager 定位。保持权限/Evidence读取入口不变，不让 renderer 读存储。暂时缺失仅在确实找不到或读取失败时显示。

标准产品回归发现，流式详情的 turnId 也可能命中 canonical 中的内部 agent_turn。选择器必须先使用可见/正式回复实体，不能因内部 turn 的同 ID 遮住流式到正式消息的交接。已补充 red→green 测试，覆盖正式回复在可见行和虚拟卸载两种状态；抽屉关闭仍返回当前回复入口，不以放宽焦点断言解决。

## 3. 实施顺序与约束

1. 先加入真实失败形状的红灯测试：超过4000字符且多 sources 的有效 post_reply，拒绝/伪造回执，structured wait，正式交付及重启。
2. 接入完整执行回执，UI裁剪保持有界；短结果兼容。
3. 安全模型切换续接与历史详情修复；保留所有拒绝/取消/超时及未知副作用测试。
4. 与 ADR98 的 P1/P2/P3 性能修复一起跑完整工程门禁与标准产品回归。
5. 使用真实 DeepSeek 主 Bot、Worker、Verifier，大历史（1100计划、约185MB journal、9.6MB主对话、46MB子对话），真实多文件修改、18项测试、复核、正式签收、长回复、取消后继续、重启和换模型恢复；执行期间持续真实输入与滚动，不以小任务替代。
6. 所有必查产品截图逐图实施者自审并 Verify；候选 CI、正式 RC 资产、签名、更新与隔离安装单独验收。失败记录不覆盖为通过，未覆盖项明确标注。

## 4. 风险与不变条件

本地回执不得泄漏秘密或无限增长；只当前回合持有，配对 ID，正式存储沿用已有 schema。读取裁剪预览绝不提升为 Evidence。模型变更不能清空预算、任务、权限或已执行事实；未知副作用宁可明确阻塞。复核超时不取消主 Bot 解释事实的能力，不能放宽 accepted 门槛。历史 UI 展示变化不得扩大执行权限。

## 5. 验收记录

实现已在代码 PR169 推送。完整执行回执、有效报告守卫、模型重基、前台调度、SSE 生命周期和历史详情均有相应测试；关键失败形状先在旧实现红灯，再在修复后绿灯。权限拒绝/错误ID/错误能力/失败结果不能发布正式回复；活跃写工具不会被新消息抢断。SSE 假传输测试保留真实 read/cancel 永不结束的形状，确认协议终点、AbortSignal 和 idle deadline 能自行完成，而非靠 TCP EOF。

完整本地 build、typecheck、architecture、测试与 37 项 tagged upgrade/recovery 矩阵通过；runtime-node 1313 项通过，Desktop 5573 项通过、5 项既有 skip，另有最新详情交接测试。后续仅详情选择与 QA 采样调整，精确最终 CI/产品包/真实任务和签名包结果仍待补。

中间提交的真实 DeepSeek 多文件任务已完成三份实现修改、18 个不可修改测试、独立上下文复核、正式回复和宿主 accepted，但随后的取消调度与长回复曾超时，所以不能把该轮计为整体验收通过。一次受控产品回归在详情交接焦点上失败，修复选择顺序并保持原断言；随后主产品回归通过，Agent 活动附加组因旧脚本直接访问虚拟卸载行失败，已通过真实滚动修复并宽窄复测通过。所有失败单列保留。

最终完整标准回归、同规模真实任务、重启/换模型与 RC19 公开资产验证仍在进行；本节未记录最终结果前不声明整体问题已解决或发布通过。

精确候选 `675313b0` 的标准四组产品回归、180张逐图实施者自审与Verify已经通过（runId `3ca48196-013d-4ba2-b894-66c4bf2eeb2f`）；不是独立产品审查。静态执行文案必须保持可读，门禁明确断言没有持续背景重绘；此前聚合器仍要求旧shimmer标志的失败保留，已修正为严格静态可读断言后重新完整capture，而非重新包装旧截图。

一次最终真实任务在任何模型请求之前遇到未签名开发凭据助手的macOS钥匙串超时，未计任务或性能通过。原装签名RC18助手在同份隔离凭据上正常读取，Rust逻辑相同而只有包版本变更；源码真实验收明确使用该原装助手，正式RC19包仍须以其自身签名助手再验证。未改动钥匙串ACL、未输出秘密或替换日常安装。

## 最终交付

RC19已发布：代码PR169合入，发布提交8cf40bd9与冻结候选ecf21f0d代码树一致。最终源码三文件/18个原有测试、独立上下文复核、宿主签收、正式回复、取消后继续与5810字符完整回执通过；同一work跨模型恢复及重启通过。公开签名RC19使用自身助手复测真实读取、模型恢复和重启，45秒无新派发观察与原正式回复展示通过。180图实施者自审/Verify、双平台CI、37升级恢复、8个正式发布作业、14公开资产、签名/公证、四npm及实际RC18下载更新均通过。[验收记录与明确限制](../../playbook/v0.1.0/rc19-candidate.md)是最终收口依据；上文中“仍在进行”是保留的中间阶段记录。
