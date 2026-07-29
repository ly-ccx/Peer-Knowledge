# 上下文压缩管线故障诊断与修复设计

日期：2026-07-29
状态：修复设计 / 已完成代码验证
关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）

关联基线：

- `knowledge/architecture/19-system-prompt-context-architecture.md`
- `knowledge/architecture/20-architecture-governance.md`
- `knowledge/architecture/21-auto-context-compaction-run-resume.md`
- `knowledge/architecture/23-compaction-path-root-governance.md`
- `knowledge/decisions/56-provider-observed-context-accounting.md`

## 一、一句话结论

上下文压缩不能以“模型返回了一段较短的新摘要”为成功标准；它必须约束历史交接摘要本身，并以最终进入下一次 provider 请求的完整上下文是否回到统一预算内作为唯一成功标准。

故障 Session `4d15e5de-4586-42d4-9a92-9394f60be6c8` 已持久化近 70 万字符的历史交接块。后续压缩只总结新增消息，却继续原样携带该交接块，导致最终候选不降反升或始终超过触发阈值，于是会话反复出现压缩错误。

## 二、问题重写

这不是报错文案、模型偶发失败或重试次数不足的问题，而是压缩管线的两个契约缺陷：

1. **历史连续性没有硬预算**：上一轮 `_compaction.summary` 被当作不可再压缩的连续性真值，合并时可以无界进入下一轮 handoff。
2. **成功验收曾使用错误对象**：管线关注本轮 LLM delta summary，而没有始终对最终 handoff 与保留消息、system context、tool schema 组成的下一次请求做预算验收。

系统层可观察症状是：压缩完成后 token 数不降反升，或新摘要很短但最终请求仍超限；旧会话一旦被污染，之后每次自动压缩都会在同一个巨型基线上失败。

## 三、故障证据

### 3.1 会话持久化证据

会话文件：

```text
~/.peer-agent/conversations/4d15e5de-4586-42d4-9a92-9394f60be6c8.jsonl
```

调查时文件约 9.57 MB，包含两个异常压缩标记：

| 时间（北京时间） | old messages | 压缩前 tokens | 压缩后 tokens | 持久化 summary 字符数 |
|---|---:|---:|---:|---:|
| 2026-07-28 21:24 | 809 | 339,553 | 353,752 | 679,174 |
| 2026-07-29 00:30 | 37 | 197,183 | 366,540 | 695,723 |

第一次候选增加 14,199 tokens；第二次增加 169,357 tokens。两次结果仍被旧实现以 `method=llm` 持久化。

第二次压缩后，只增加极少新消息时，诊断已经显示：

```text
next request:       373,011 tokens
minimal candidate:  367,593 tokens
trigger limit:       206,400 tokens
```

这证明失败基线来自历史 handoff，而不是新增消息。

### 3.2 摘要组成证据

LLM 单次实际生成的 delta summary 只有约 13,507 或 16,433 字符，但最终 `_compaction.summary` 达 679,174 和 695,723 字符。差额来自 `mergeContinuityAndDeltaSummary()` 将旧连续性摘要重新拼入新摘要。

历史内容中重复出现 `Carry-forward summary from previous compaction`，说明旧摘要被递归包裹。现有 `flattenSummaryForCarryForward()` 可以消除部分标题嵌套，却没有为历史正文设置 token 上限，也不能恢复已持久化的巨型旧摘要。

### 3.3 诊断盲区

旧日志中的 `summaryChars` 记录的是本轮模型返回值，而非合并后的最终 handoff，因此出现“日志显示摘要约一万字，落盘却近七十万字”的错觉。日志也缺少稳定的 `conversationId`，难以直接把压缩事件与会话关联。

## 四、根因

### 4.1 主根因：carry-forward 无界

压缩输入被分成：

```text
previous compaction continuity + new compactable delta + kept recent messages
```

LLM 主要压缩 delta，之后合并函数把 previous continuity 原样带回。若 previous continuity 已接近或超过预算，本轮无论把 delta 压得多小都不能收敛。

### 4.2 次根因：验收对象不是最终请求

压缩成功必须证明：

```text
final system context
+ final merged handoff
+ kept messages
+ provider tool schema
+ response reserve
<= provider-aligned trigger budget
```

只比较 `beforeTokens` 与摘要局部大小，或只检查模型调用成功，都不能证明下一次请求可以发送。

### 4.3 放大因素：旧会话兼容策略缺失

代码升级可以阻止新污染，但已经持久化的 `_compaction.summary` 仍会被读取。若读取路径不执行有界重收敛，旧 Session 永远无法自愈。

### 4.4 放大因素：观测字段失真

日志缺少历史摘要、delta 摘要、最终 handoff、keep、tool schema 的分项预算，也缺少 conversation identity。错误无法快速定位到“哪一部分占满预算”。

## 五、约束与非目标

### 5.1 必须满足

- 保留最新真人 user turn 和当前 run 的续接语义。
- 保留结构化 Evidence / Tool Result 的事实边界；摘要只是连续性导航，不能冒充原始证据。
- 新旧 Session 使用同一压缩入口和预算规则。
- provider usage / provider-aligned exact count 是容量权威；启发式 estimator 只能作为不可获得精确计数时的保守降级。
- 压缩失败不得持久化比原请求更大或仍超过触发阈值的候选。
- 修复不得依赖调高 context window、无限重试、换模型或删除全部历史。

### 5.2 非目标

- 不通过修改 UI 文案掩盖管线失败。
- 不直接手工编辑单个 Session 作为长期方案。
- 不把 Tool Result、artifact 或文件正文提升为 system instruction。
- 不为 Desktop、CLI/TUI 或不同 provider 新增独立压缩旁路。

## 六、修复后的唯一真值

压缩验收的唯一真值是 **下一次 provider 请求的最终预算快照**，而不是 delta summary 长度。

定义：

```text
finalRequestTokens =
  finalSystemTokens
  + finalHandoffTokens
  + keptMessageTokens
  + toolSchemaTokens
  + providerEnvelopeTokens
```

压缩候选只有同时满足以下条件才可持久化：

```text
finalRequestTokens < beforeRequestTokens
finalRequestTokens <= triggerLimit
finalHandoffTokens <= handoffHardLimit
```

如果精确计数 adapter 可用，使用精确值；否则使用同一共享 estimator 的保守值，并在诊断中标记 accounting source。

## 七、修复设计

### 7.1 为最终 handoff 分配硬预算

从下一次请求预算反推 handoff 可用空间：

```text
handoffBudget = triggerLimit
  - finalSystemTokens
  - keptMessageTokens
  - toolSchemaTokens
  - providerEnvelopeReserve
```

同时设置独立上限，避免大窗口模型允许 handoff 无限增长：

```text
handoffHardLimit = min(configuredCarryForwardCap, handoffBudget)
```

预算以 token 表示，不以字符数表示。

### 7.2 先压历史连续性，再合并 delta

`mergeContinuityAndDeltaSummary()` 不得原样接受任意长度的 continuity。新流程：

1. 解析并扁平化旧 `_compaction.summary`，移除递归包装标题。
2. 计算 continuity tokens。
3. 若超出 carry-forward 分配，执行有界重压缩。
4. 将有界 continuity 与本轮 delta summary 合并。
5. 对合并后的 final handoff 再做一次硬限制。
6. 若仍超限，使用确定性的结构化 fallback 生成最小连续性摘要。

LLM 重压缩可以提升质量，但确定性 fallback 必须保证容量收敛，不能因为模型失败而恢复成无界原文。

### 7.3 旧 Session 自动恢复

读取到旧 `_compaction` marker 时不修改原始文件；在下一次压缩候选构造阶段，把它视为不可信容量输入：

- 未带新版本预算元数据，或 final summary 超过当前 handoff hard limit：进入 legacy recovery。
- recovery 产出新的扁平、有界 handoff。
- 只有最终请求通过统一验收后，才以新的 `_compaction` marker 持久化。
- 新 marker 记录 schema/version 与预算组成，后续不再递归包裹。

这样旧会话通过正常压缩流程自愈，无需针对某个 conversationId 写迁移分支。

### 7.4 最终请求级验收

所有 `llm`、`structured_fallback`、minimal candidate 都必须走同一个 candidate evaluator。evaluator 接收最终构造后的 messages 与请求固定成本，输出：

```text
beforeRequestTokens
afterMessageTokens
toolSchemaTokens
finalRequestTokens
triggerLimit
accepted
rejectionReason
accountingSource
```

禁止在 evaluator 之前把候选标记为成功或落盘。

### 7.5 失败与降级顺序

建议顺序：

1. 正常 LLM delta summary + 有界 continuity。
2. 更小输出预算的 LLM retry。
3. 确定性结构化 fallback + 有界 continuity。
4. 降级 keep 中可材料化的大型 tool tail。
5. 构造 minimal candidate。
6. 若最终请求仍不能低于阈值，返回结构化 `insufficient_reduction`，不得持久化失败候选。

每一级都由同一个最终预算 evaluator 判定。

### 7.6 诊断字段

每个事件至少记录：

```text
conversationId
providerId
modelId
compactionMarkerVersion
accountingSource
beforeRequestTokens
previousSummaryTokens
deltaInputTokens
deltaSummaryTokens
finalHandoffTokens
keptMessageTokens
toolSchemaTokens
finalRequestTokens
triggerLimit
candidateMethod
accepted
rejectionReason
```

不得记录完整敏感正文。长度、token 数、hash、artifact/evidence ref 足以定位容量问题。

## 八、协议与架构影响

本修复属于 B-level Runtime / compaction 变更，并触及 System Context continuity 边界，但不改变本地能力执行链。

边界保持：

- Runtime 决定何时压缩与如何验收。
- System Context 只接纳有界 continuity。
- Tool Result / Evidence 保持事实真值，摘要仅提供导航和检索提示。
- Renderer 只展示压缩状态和错误，不成为预算或持久化事实源。
- provider encoder 继续负责最终 wire format；预算 evaluator 必须使用 encoder 对齐的计数口径。

不新增 Desktop/provider 特例。修复应留在共享压缩 seam 或当前权威 compactor 中，并由跨入口测试守住。

## 九、回归测试矩阵

### 9.1 巨型旧摘要恢复

构造约 70 万字符、包含多层 carry-forward 标题的 legacy `_compaction.summary`，后接一条小 delta。断言：

- final handoff 不包含递归增长的完整旧正文。
- final handoff tokens 不超过 hard limit。
- final request tokens 不超过 trigger limit。
- 新 marker 保留关键连续性字段并带版本/预算元数据。

### 9.2 不降反升候选拒绝

模拟 LLM 返回内容导致：

```text
afterRequestTokens >= beforeRequestTokens
```

断言候选不持久化，并继续 fallback 或返回结构化失败。

### 9.3 局部很小、整体超限

让 delta summary 很小，但 previous continuity 极大。断言不能仅凭 delta summary 成功；必须重压历史并按 final request 验收。

### 9.4 工具与固定成本

让 messages 本身低于阈值，但加入 tool schema 后超限。断言 final request evaluator 拒绝候选。

### 9.5 连续多轮稳定性

对同一会话连续执行多轮压缩。断言 handoff 大小保持有界，不随轮数线性或指数增长。

### 9.6 关键语义保持

断言最新真人 user turn、decision anchors、进行中目标、关键 Evidence/artifact refs 仍被保留；原始大型 Tool Result 不被复制进摘要。

### 9.7 诊断可定位性

断言 complete、fallback、insufficient_reduction 事件均含 conversationId 与摘要组成字段，且不写入完整正文或凭据。

## 十、验收标准

代码修复完成必须满足：

1. 约 70 万字符 legacy summary 的回归测试稳定通过。
2. 最终 handoff 与最终 provider 请求均有硬预算并被测试覆盖。
3. 压缩候选不降反升时绝不持久化。
4. 现有 context compactor 测试全部通过。
5. 仓库类型检查通过。
6. Git whitespace / conflict marker 检查通过。
7. 诊断日志可以凭 conversationId 还原摘要组成和拒绝原因。

## 十一、部署与会话恢复说明

压缩器运行在 Electron main process。修复发布或本地验证后必须完整重启主进程，仅 renderer HMR 不足以加载新逻辑。

对于故障 Session，不优先手工改文件。完成代码修复并重启后，由下一次压缩走 legacy recovery 生成有界 marker。若产品需要立即恢复，可另行提供经过备份、校验和原子替换的维护命令，但该命令仍须复用同一个压缩与预算模块，不能成为一次性脚本旁路。

## 十二、长期修复修订：动态预算 Context Compiler

### 12.1 固定 12k 仅是止血，不是正常路径

固定 `12,000 tokens` 可以阻断递归膨胀，但会把安全阀错误地变成语义上限。复杂 Session 在 provider 允许 `32k–64k` 输出且最终请求仍有空间时，应允许更完整的 handoff；空间不足时也不能只截断 handoff，而应先释放可材料化历史。

正常路径改为动态预算：

```text
requestTarget = min(
  triggerLimit,
  contextWindow - responseReserve - futureTurnReserve - safetyReserve
)

handoffBudget = min(
  providerMaxOutputTokens,
  requestTarget
    - systemTokens
    - toolSchemaTokens
    - mandatoryKeepTokens
    - providerEnvelopeTokens
)
```

`futureTurnReserve` 必须为后续正常对话保留增长空间，防止压缩刚结束就再次触发。任何产品成本上限只能作为显式 `quality_degraded` 策略，不能静默截断。

### 12.2 canonical checkpoint 是交接真值

每轮压缩不再持久化“旧摘要 + 新摘要”，而是编译一份版本化 checkpoint：

```text
checkpointVersion
checkpointId
sourceRevision
objective
constraints[]
decisions[]
rejectedOptions[]
completedWork[]
openWork[]
filesAndSymbols[]
evidenceRefs[]
coldHistoryRefs[]
recentNarrative
budgetSnapshot
coverageSnapshot
```

自然语言 narrative 是 checkpoint 的表达层，不是唯一真值。旧 `_compaction.summary` 进入迁移器后只作为 legacy input；新 marker 必须由 canonical checkpoint 重新渲染，禁止递归包装。

### 12.3 冷历史材料化

完整 Tool Result、网页正文、命令输出、文件内容和超长历史不再复制进热摘要。Context Compiler 必须：

1. 优先复用已有 artifact/evidence ref；
2. 对尚无 ref 的大型可恢复内容，通过受治理的 artifact store 落盘；
3. 在 checkpoint 中保留来源、摘要、hash、ref 和 suggested retrieval；
4. 只有 ref 已持久化且候选通过预检后，才允许从热上下文释放原文。

冷历史仍是 factual/user context，不得提升成 system instruction。

### 12.4 候选验收与原子提交

候选必须同时通过：

- provider 对齐的最终请求预检；
- `finalRequestTokens <= requestTarget`；
- 相对原请求有有效下降；
- mandatory semantic coverage 为 100%；
- 所有冷历史 ref 可解析；
- checkpoint version、source revision 和 conversation revision 匹配。

通过后才调用现有 `replaceMessages` 原子边界。失败候选不得覆盖 Session，不得更新 checkpoint persisted 标记。

### 12.5 失败是可持久查询的终态

主进程 registry 必须保存 `running | failed`，失败包含：

```text
errorCode
message
beforeRequestTokens
minimalCandidateTokens
requestTarget
budgetBreakdown
failedAt
```

coordinator 失败时发送 `stage=failed`，不得在同一路径立即发送 `idle`。Renderer 只表达该主进程真值；用户关闭、重试或下一次成功开始时再清除失败状态。

## 十三、修订后的回归矩阵

除第九节测试外，必须增加：

1. 当最终请求空间允许时，handoff 可以超过 12k，并受 provider 输出上限与增长余量约束。
2. 同一 checkpoint 连续编译多轮不会线性或指数增长。
3. legacy 69 万字符摘要迁移后产生新版本 checkpoint，不保留递归 wrapper。
4. 大型 Tool Result 释放前已有可解析 artifact/evidence ref。
5. decision、constraint、open work、Evidence ref 等 mandatory sections 覆盖率为 100%。
6. 最终预检失败时 Session 文件不变。
7. coordinator/registry/Renderer 保留 failed 终态及预算明细，不再让进度条无解释消失。

## 十四、决策摘要

```text
固定 12k 退出正常路径，只保留为旧版本止血背景。
动态预算由最终请求容量、provider 输出上限和后续增长余量共同决定。
canonical checkpoint 管语义，cold history 管可恢复事实，narrative 管表达。
只有通过最终请求预检、语义覆盖和引用完整性的候选才允许原子提交。
失败必须是可查询、可解释的终态，不能清成 idle。
```
