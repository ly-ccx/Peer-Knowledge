# ADR 99：权威回复回执、模型切换恢复与历史详情

创建时间：2026-10-19
状态：Accepted（用户要求查明连续失败根因、修复、自主验收并发布 RC）
级别：A（执行事实与展示边界），B（主 Bot 续接）；继承 ADR 19、94、97、98。

## 1. 现场证据

只读检查 RC18 的实际 Peer RSI 对话：两次 post_reply 完整返回为成功，序列化长度分别 9420、9142 字符；UI stream 的 4000 字符裁剪把它们改为 truncated_tool_result_preview。AgentTurnExecutor 却从这个展示事件收集执行结果，finishAgentTurn 因缺少结构化 ok/message 而拒绝正式回复，随后生成错误卡并累计熔断。短回复测试未覆盖阈值，之前小任务成功不能证明日常长回复可靠。

另一回合真实发生 continuity_model_changed：当前配置变更后仍把旧模型原生检查点传给新 Provider。适配器拒绝跨模型回放本身正确，缺少的是协调层安全的新认知续接。另有真实 verifier_timeout；不能把超时伪装成成功，也不能再把最终解释性回复因预览截断丢掉。截图中的历史错误详情只在当前可见 rows 查找，错误折叠或分页后实体仍在但详情找不到。

## 2. Module 与 Interface

### 2.1 Authoritative Tool Receipt

复用本地 agentProgress.onToolExecution Seam，消费既有完整 CapabilityExecution（ToolCall、PermissionGrant、ToolResult、Evidence）。仅已配对的本回合 toolCallId 和已登记的 delegation post_reply / wait_for_sessions 能更新控制回执；拒绝、取消、超时保持原状态。AgentTurnExecutor 使用本地完整回执覆盖同 ID 的 UI 预览，原 sink 仍只收原有有界事件，不向 renderer 额外广播完整数据。不得解析 preview 字符串寻找 ok、不得从模型参数构造宿主验证成功。回执存储和正式交付继续使用原 reducer、canonical 消息与 delivery ledger。

### 2.2 Model Recovery Admission

Provider 的原生跨模型拒绝保持。协调层比较当前已解析 selection 与检查点 provider/providerId/model。完全相同则原生续接；不同且所有历史工具均已配对、账本无未知副作用时，启动同一 work 的新认知步，沿用实际 Tool Result/Evidence 的 bounded retryContinuity、当前上下文和用量，不回放旧调用、不重建原生 reasoning。未配对/未知派发继续阻止自动续接。旧 checkpoint 保留以供追溯。新模型自己依据当前事实决定后续操作，不能冒认旧轮交付成功。

### 2.3 Terminal Response Guard

真实大历史验收再次出现 unsupported_tool_response。追查共享终态守卫发现其把“tool result / exitCode / I verified / 我检查了”等普通复核报告用词一律当成未执行工具声称，完全不看前面实际配对的 Tool Result。它不只检测协议标签；因此原报错“协议文本”也不准确。使用真实工具结果后的普通总结必须可以进入报告解码与 Evidence 校验；没有工具结果的空执行声称、下一步行动旁白、正文伪工具标签仍拦截。事实真实性仍由 CapabilityExecution、Evidence、Verifier decoder 和 host acceptance 判断，不能由一个正文关键词充当完成门禁。共享 kernel 向守卫传入原生历史中是否存在结构化工具结果；不解析普通正文为工具，不把允许文本等同验收通过。

### 2.4 Foreground Input Admission

第二轮大历史真实任务完成修改、18项测试、两层实际复核、正式回复与 accepted；随后后台 wake 已在发请求，新用户消息虽入队，却要等该后台请求返回才有机会执行，取消验收两分钟未派发。新输入须能抢占无活跃工具派发的后台认知请求：调用既有 AbortSignal，旧工作按 yielded 保存保护检查点，事件继续归原 work；新输入不能继承旧批次，已完成工具不重放。有活跃工具或未知副作用时不擅自中断派发，仍由既有完整结果/取消/超时及 ledger 收尾。此变化不取消子任务，也不把正常调度抢占当成用户可见错误。

### 2.5 Provider Stream Lifecycle

The recovery run admitted a new user work but remained in one Provider request with zero tool dispatches. The compatibility Chat consumer records `[DONE]` without ending its read loop. A connection that remains open therefore withholds already received tool calls from execution. Reads also do not race AbortSignal, and cancellation/idle cleanup awaits reader.cancel indefinitely. A reader that never closes and never settles cancel reproduces both defects deterministically.

The shared SSE reader Module settles on the first protocol terminal, EOF, cancellation, timeout or error. Cleanup must not hold the business terminal open; late data must not emit events or dispatch tools. Chat Completions, Responses, Anthropic and Gemini share the read/cancel Seam. Preserve authentic usage, paired calls, partial output and replaySafe; partial failures cannot automatically replay. End a Chat stream on `[DONE]` without waiting for TCP EOF. This changes no permission or Evidence authority.

The Desktop connection-timeout adapter also removed its parent abort forwarding as soon as headers arrived. A deterministic test confirms that later caller cancellation never reached the response-body signal. Compose the connection deadline and caller lifetime with AbortSignal.any so cancellation remains authoritative through the complete body while the connection timer still stops at headers.

### 2.6 Historical Reply Details

详情选择按 canonical message identity / turnId 从已加载消息建立展示投影，不依赖该行是否因历史折叠而出现在聊天 rows；未加载的实体通过现有 conversation pager 定位。保持权限/Evidence读取入口不变，不让 renderer 读存储。暂时缺失仅在确实找不到或读取失败时显示。

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

实施与真实验收结果待补；本节未完成前不声明问题已解决或发布通过。
