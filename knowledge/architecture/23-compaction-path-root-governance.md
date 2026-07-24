# 压缩路径根治理:单一 Compaction Pipeline 与双端一致性

创建时间:2026-07-24
最后更新:2026-07-24(同日二次复核:代码仓已落地 Phase 1 主体与 Desktop 入口收敛,见第九节)
状态:治理方案 / 权威路线(取代各处零散压缩接线的默认做法)
关联代码仓:`peer_agent`(本地 `/Users/liangyin/Documents/DEV/github/peer_agent`)
关联文档:

- `knowledge/decisions/17-local-context-compaction.md` — 压缩机制设计(分层、触发、摘要策略)
- `knowledge/architecture/21-auto-context-compaction-run-resume.md` — 压缩与 run 续接协议
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — 双宿主治理(P1 债务「Compaction 算法双轨无统一接口」的展开)
- `knowledge/decisions/42-context-display-vs-trigger-accounting.md` — 显示口径与触发口径
- `knowledge/decisions/52-unified-next-request-context-accounting.md` — 下一请求统一记账
- `knowledge/experience/context-occupancy-ring-inaccuracy-root-cause.md` — 右下角占用圆环失准根因(本治理 Phase 1 的直接受益面)

## 一、一句话结论

```text
压缩不乱在算法,乱在所有权。
切分与摘要已下沉 runtime-core,
但预算、估算、microcompact、emergency、持久化合同、入口编排
全部散落在 provider loop × 宿主 × 触发方式的笛卡尔积里。
根治 = 一条 Compaction Pipeline,一个闸门入口,一份共享口径,两端复用。
```

## 二、压缩路径普查(2026-07-24 代码核实)

### 2.1 Layer 2 语义压缩入口(现状 5 个)

| # | 入口 | 代码位置 | 现状问题 |
|---|------|----------|----------|
| D1 | 自动 preflight | `openai/anthropic/gemini-agent-loop.mjs` 各自调 `runCompactionCheck()` | 3 份接线;压缩后 system prompt 回填方式各 loop 不同 |
| D2 | Emergency PTL 重试 | 同 3 个 loop 各自复制 `isPromptTooLongResponse` + emergency 块 | 3 份重复,细节已分叉(anthropic 的 system 过滤方式不同) |
| D3 | 手动 `/compact` | `main.mjs` `ipcMain.handle('chat:compact')` **直接调 `compactIfNeeded`**,绕过 coordinator | 自建横幅/registry/进度/持久化,与 `persistAndNotifyCompaction` 平行实现 |
| D4 | qoder-agent-loop | `chat-runtime/qoder-agent-loop.mjs` | **未接任何压缩**:无 preflight、无 emergency —— 覆盖洞 |
| T1 | TUI 压缩 | `apps/tui/src/chat-controller.ts` `runStructuralCompact()` | 仅回合开始前检查一次;多轮工具循环中途不压;**无 emergency PTL 恢复**;无 hard 线 |

另有读取侧口径:Goal Runner(`main.mjs toRuntimeMessages` + `continuityContextFromMessages`)按 `_compaction` 边界切历史 —— 该口径正确,保留。

### 2.2 口径重复与漂移

| 口径 | Desktop 权威 | TUI 副本 | 漂移事实 |
|------|--------------|----------|----------|
| Token 估算常量/估算器 | `context-compactor.mjs` `COMPACTION_CONFIG` + `estimateTextTokens/estimateTokensFromMessages/estimateToolsTokens` | `apps/tui/src/context-pressure.ts` 整份手抄("kept in lockstep" 注释自证) | Desktop 有 hardRatio 0.95、summaryOutputReserve 4000、safetyReserve 1000、overSummaryHeadroom;TUI 仅 soft 0.8 一条线 |
| 预算判定 | `compaction-coordinator.mjs` `computeContextBudget`(soft/hard/overflow/reserve) | `context-pressure.ts` `computeContextPressure`(仅 soft) | TUI 无 hard 拦截、无摘要预留 |
| 切分算法 | `runtime-core splitMessagesForCompaction`(已共享 ✓) | 同用 ✓;但 `context-compact.ts compactModelMessagesStructurally` 是第二套私有切分,生产已不用、仅测试引用 | 僵尸实现 |
| 摘要级联 | `runtime-core runCompactionSummaryCascade`(已共享 ✓) | 同用 ✓ | — |
| `_compaction` marker 写入 | `conversation-compaction-persistence.mjs` | `apps/tui/src/conversation-persistence.ts` 自写一份 | marker 形状未在 `@peer-agent/protocol` 定型,靠约定 |
| Layer 1 microcompact | `microcompactMessagesForContext`(coordinator + computeContextInfo 两处应用) | **无** | TUI 大工具输出直接进 prompt |
| 文档 vs 代码 | ADR 17 写 triggerRatio 0.75 | — | 代码实际 0.8,文档漂移 |

### 2.3 语义分叉(两端行为不一致)

1. **手动 `/compact`**:Desktop = 真·全量压缩(keep=0);TUI = `keepRecentCount 8`。同一命令两端结果不同,且无 ADR 记录该差异。
2. **handoff 形态**:Desktop 把 handoff 作为带 `_compaction` 的 user message 留在 provider 请求内;TUI 把 handoff 从 provider 历史剔除、摘要只走 system continuity。模型看到的会话形状不同,违反 22 号文档「压缩恢复形状不可私有」。
3. **压缩时机**:Desktop 每次 provider request 前 preflight(含 agent loop 中途);TUI 只在用户回合开始前检查一次,长 agent loop 中途超窗无保护。
4. **emergency**:Desktop 有 PTL 分类 + force compact + 重试一次;TUI 完全没有。
5. **circuit breaker**:`context-compactor.mjs` 的连续失败计数是 module 级全局变量,跨会话串状态。

## 三、根因

```text
R1 所有权缺失:没有单一 CompactionPipeline;每个 provider loop、每个宿主、
   每个触发方式(auto/manual/emergency)都自己拼一遍 预算→压缩→持久化→事件。
R2 下沉不完整:runtime-core 只接住了 split + summary cascade;
   估算器/预算器/microcompact/emergency 分类/持久化合同 都留在宿主层。
R3 接线靠自觉:压缩不是 kernel 的结构性步骤,而是各 loop 自愿调用
   —— 所以 qoder loop 漏接、新增 wire 必漏。
R4 一致性靠手抄:TUI 用 "lockstep 注释" 代替共享代码,漂移是时间问题。
R5 合同未定型:_compaction marker、compaction 事件 stage、手动/自动语义
   均无 protocol 级类型或 ADR 锁定。
```

## 四、目标架构

### 4.1 分层

```text
@peer-agent/protocol
  + CompactionMarker(_compaction 形状)、CompactionEventStage 类型定型

@peer-agent/runtime-core(或独立 @peer-agent/context-compaction)
  ├─ TokenEstimator          估算常量 + estimateText/Messages/Tools(单一来源)
  ├─ ContextBudget           soft/hard/reserve/overflow 判定(单一来源)
  ├─ microcompact            Layer 1 工具结果瘦身(host 无关)
  ├─ split                   splitMessagesForCompaction(已存在)
  ├─ summary cascade         runCompactionSummaryCascade(已存在)
  ├─ CompactionStrategy      接口:LlmSummaryStrategy / StructuralStrategy
  ├─ classifyPromptTooLong   PTL 错误分类 + 重试策略(纯逻辑)
  └─ CompactionPlan          纯数据输出:做什么、留什么、为何

宿主适配层(薄)
  Desktop coordinator:model port(provider fetch)+ IPC 事件 + registry + 持久化调用
  TUI controller:model port(provider-chat-model)+ snapshot 状态 + 持久化调用

入口闸门(唯一)
  Agent loop kernel / RuntimePipeline 的每次 provider request 前:
    CompactionGate.preflight()
  provider 返回 PTL 时:
    CompactionGate.emergency()(kernel 统一,loop 不再各自实现)
```

### 4.2 不变式(在 17/21 号文档基础上新增)

1. **单闸门**:任何 provider request 只能经 CompactionGate 发出;新增 wire/loop 无需(也不允许)自行接压缩。
2. **单口径**:估算常量、预算线、microcompact 规则只有共享包一份;宿主不得复制数值。
3. **单形状**:`_compaction` marker 与压缩后会话形状由 protocol 类型约束;两端持久化必须产出同一形状,任一端可恢复另一端压缩过的会话。
4. **手动语义一致**:`/compact` 在两端等价(默认真·全量 + `preserveLatestUserTurn=false`);如需宿主差异,必须落 ADR。
5. **emergency 双端等价**:PTL 分类、force 压缩、重试上限(1 次)两端一致;TUI 不得因"终端场景少"而豁免。
6. **状态不出全局**:circuit breaker 等失败状态按 conversationId 隔离,不得使用 module 级可变量。

## 五、落地路线

### Phase 0 — 止血(不动架构,先堵洞)

1. `qoder-agent-loop` 接入 `runCompactionCheck`(preflight + emergency),与其他 loop 同参。
2. `main.mjs chat:compact` 改走 `runCompactionCheck({ force: true, preserveLatestUserTurn: false })`,删平行的横幅/持久化实现。
3. 删除 TUI `compactModelMessagesStructurally` 僵尸切分及其测试(保留 `buildStructuralSummary/buildHandoffContent`)。
4. circuit breaker 改 per-conversation Map。
5. ADR 17 的 triggerRatio 记载修正为 0.8(以代码为准)。

### Phase 1 — 口径下沉

1. 估算器 + 常量 + `computeContextBudget` + microcompact 迁入 runtime-core(或新包);Desktop `context-compactor.mjs` 与 TUI `context-pressure.ts` 改为 re-export/调用,删除手抄。
2. `_compaction` marker 与 compaction 事件 stage 类型进 `@peer-agent/protocol`;两端持久化改用同一 `buildCompactionMarker()`。
3. TUI 预算补齐 hard 线、摘要输出预留,与 Desktop 同参。
4. 占用显示同步治理(见 `context-occupancy-ring-inaccuracy-root-cause.md`):renderer 删除 `tokenEstimate.ts` 历史估算,改为失效即请求 Runtime 重投影(复用 `contentRevision` 校验);跨端恢复时 `snapshot.source ≠ 当前宿主` 必须重投影;草稿增量改用下沉后的共享估算器。

### Phase 2 — 入口收敛

1. PTL 分类 + emergency 重试上提到 agent-loop kernel(Desktop)/RuntimePipeline 回合边界(TUI);删 3 个 loop 内的重复 emergency 块。
2. 压缩后 system prompt 回填(rehydrate)统一为 kernel 单点,消除各 loop 的差异拼接。
3. TUI 在多轮工具循环的每次 provider request 前走同一 preflight(不只回合开始),压缩边界遵守 21 号文档安全边界。

### Phase 3 — 策略接口化(完成 22 号文档 Phase B.3)

1. `CompactionStrategy` 接口落地:Desktop 默认 LlmSummaryStrategy(可降级 Structural);TUI 默认 Structural + 可选 LLM(已有 `summarizeCompaction` port)。
2. handoff 形状统一:压缩后 provider 请求形态(handoff user message vs system continuity)二选一定型,另一端迁移;当前倾向 **system continuity + `_compaction` marker 落库**(与 Goal Runner 读取口径一致),需在实施 PR 中以对照实验确认后写入 ADR。
3. 双端契约测试:同一份会话 fixture,两端压缩 → 持久化形状 diff 必须为空;两端互相恢复对方压缩的会话必须可继续。

## 六、验收标准

1. 全仓 `runCompactionCheck` / 压缩入口调用点 ≤ 2(kernel preflight + kernel emergency);loop 与 main.mjs 无直接压缩调用。
2. 估算常量在仓内只出现一份(grep `cjkCharsPerToken` 只命中共享包)。
3. qoder loop 与 TUI 均具备 preflight + emergency,测试覆盖 PTL 重试。
4. `/compact` 在 Desktop 与 TUI 对同一 fixture 产生相同的持久化形状与保留窗口。
5. TUI 压缩后的会话可被 Desktop 打开并继续,反之亦然(契约测试固化)。
6. 22 号文档 P1 债务「Compaction 算法双轨无统一接口」可标记为已清偿。

## 七、评审问题单(压缩相关变更必答)

1. 该变更是否新增了第二个压缩入口?(只允许 kernel 闸门)
2. 是否复制了任何估算常量或预算线到宿主层?
3. 压缩后的会话形状是否仍满足 protocol 定型,两端可互相恢复?
4. 新增 provider loop / wire 是否自动获得 preflight + emergency(而非手工接线)?
5. 手动 / 自动 / 紧急三种触发在两端语义是否仍一致?

## 八、落地进度复核(2026-07-24 二次代码核实)

### 8.1 已落地

| 原问题 | 现状 |
|--------|------|
| 估算器/常量三份手抄(R2/R4) | ✅ `runtime-core/context-projection.ts` 唯一真值(`CONTEXT_PROJECTION_CONFIG` + `estimateContextMessagesTokens/ToolsTokens` + `decideContextCompaction`);Desktop `context-compactor` 与 TUI `context-pressure` 均改为 facade,全仓 `cjkCharsPerToken` 仅一份 |
| D1 各 loop 自接压缩 | ✅ 新增 `chat-runtime/provider-request-coordinator.mjs`,openai/anthropic/gemini/qoder 四 loop 统一走 `coordinateDesktopProviderRequest` |
| D4 qoder loop 无 preflight | ✅ 已接入(但 emergency 仍缺,见 8.2) |
| 共享投影契约缺失 | ✅ runtime-core 新增六阶段 `ContextProjectionLifecycle`(request_preflight / stream_preview / tool_result / post_compaction / turn_complete / restored)+ `CompactionDecision`;21 号文档第十三章为其规范 |
| 圆环 RC1(renderer 兜底估算器成分表错误) | ✅ 以删除解决:`tokenEstimate.ts` 只剩草稿增量,`contextOccupancy` 不再接受 history 估算;圆环 = 权威投影 ?? 未知 |

### 8.2 未落地 / 新引入

| 问题 | 性质 |
|------|------|
| TUI pressure 分子未计 continuity system block(实际请求含、回合间静态投影不含;turn 内投影已含) | 小口径缺口,低优先级 |
| 圆环 RC4(切模型后到下轮 done 前分母仍旧窗口) | 待修,可在切模型时触发 restored 重投影顺带解决 |
| TUI 中途压缩的 marker 持久化在 turn 结束时写入(非压缩即时),turn 中 crash 会丢失该次压缩记录 | 已知取舍,偏离 21 号文档不变式 6,待 TUI 持久化链路支持 turn 内写入时收敛 |

### 8.3 三次复核追记(2026-07-24 同日落地)

以下两项已在 `peer_agent` 实现并验证(主进程 97 / runtime-core 8 / TUI 48 / renderer 34 测试全绿,三处 tsc 通过):

1. **双 hard 线已收敛**:删除 coordinator 的 `CONTEXT_BUDGET_GUARD(0.95)`,`computeContextBudget` 改用 runtime-core `CONTEXT_PROJECTION_CONFIG.hardRatio(0.92)`(经 `COMPACTION_CONFIG` 透传),全仓 hard 线单值。
2. **生命周期接线 6/6(restored 除外,见下)**:
   - kernel(`agent-loop-kernel.mjs`)持有 per-turn `createContextProjectionLifecycle`,经新 IPC `chat:context:projection` 发布带单调 revision 的稳定快照;
   - `request_preflight` / `post_compaction`:coordinator 接受注入的 kernel lifecycle,四个 loop 全部透传;
   - `tool_result`:四个 loop 在 applyToolResults 后发布;`turn_complete`:sendDone 前发布;
   - `stream_preview`:按 ADR 52 由展示侧叠加——Desktop renderer 以 `streamPreviewTokens`(浮点累计、稳定快照到达归零)叠在权威基线上;TUI 在 delta flush 处用同语义重算 pressure,双端圆环流式期间随 delta 增长;
   - renderer 新增 `applyContextProjectionEvent`:同 streamId 内以 revision 序丢弃乱序快照,投影事件路径不再依赖 `Math.max` 锁高(legacy done/compaction 合并路径保留兼容);
   - `restored` 仍无发布者:需要完整 system/tools 组成才能重投影,归入 Phase 1.4,不接受缺成分的伪值。

### 8.4 四次复核追记(2026-07-24 同日落地,Phase 0 清零 + Desktop emergency 收敛)

以下已在 `peer_agent` 实现并验证(chat-runtime 205 测试全绿、TUI 40 全绿、全部 loop/main 语法检查通过、TUI tsc 通过):

1. **D3 已清偿**:`main.mjs chat:compact` 改走 `runCompactionCheck({ force: true, manual: true })`;coordinator 新增 manual 语义(强制横幅 + 全事件 manual 标记),handler 内平行的横幅/进度/登记表/持久化实现全部删除;手动持久化经 persistCompaction 闭包注入 `sourceMessages`。
2. **D2 已清偿**:PTL 分类 + emergency 重试策略收敛为 `provider-request-coordinator.recoverFromPromptTooLong()`(同一请求最多重试一次);openai/anthropic/gemini 三处复制块删除,loop 只剩形态映射。
3. **qoder 补齐 emergency + 持久化**:接入同一 helper;同时修复 qoder 调用链之前未传 `persistCompaction/continuityContext/rebuildSystemPrompt` 的遗漏(qoder 压缩此前不落盘)。
4. **circuit breaker 按会话隔离**(不变式 6):module 级计数改为 per-scope Map(conversationId 优先,回退 streamId);`resetCircuitBreaker(scope?)` 兼容无参清空。
5. **TUI 僵尸切分已删**:`compactModelMessagesStructurally` 与 `StructuralCompactResult` 移除,`context-compact.ts` 只剩结构化摘要与 handoff 文本生成;切分唯一来源 runtime-core。

### 8.5 五次复核追记(2026-07-24 同日落地,台账主体清零)

以下已实现并验证(Desktop main 251 / renderer 304 / TUI 484 测试全绿,desktop/tui/runtime-core/protocol tsc 全过),分两次 commit 落在 `PeerAgent/fix-context-zero-on-send` 分支:

1. **`_compaction` 进 protocol(Phase 1.2 清偿)**:新增 `packages/protocol/src/compaction.ts` —— `ConversationCompactionMarker` 类型 + `buildCompactionMarker()` 唯一构造器;Desktop `buildCompactedMessages` 与 TUI `conversation-persistence` 均改用,TUI 不再硬编码 `method: 'structural'`,改记录真实级联结果。
2. **PTL 分类下沉 runtime-core**:`isPromptTooLongError()` 单源;Desktop `isPromptTooLongResponse` 退化为委托。
3. **T1 清偿(不变式 4、5)**:TUI 手动 `/compact` 改真·全量(keep 0)与 Desktop 对齐;`provider-chat-model.runTurn` 新增 loop 中途 preflight(共享阈值 `decideContextCompaction`)与 PTL emergency 单次重试(确定性结构化压缩,不在 loop 内嵌套 LLM);controller 收尾做连续性 carry-forward、剔除 handoff、经 compact meta 写入共享 marker。
4. **restored 重投影(Phase 1.4 清偿,圆环 RC2/RC5 收尾)**:新 IPC `chat:context:restored` 在 main 侧按完整成分(全量 system context + 模式投影工具 schema + `_compaction` 边界后 active 历史 + Layer 1 投影)重算,经六阶段生命周期 `restored` 阶段产出,并回写 `contextSnapshot(source: desktop)`;renderer 对 `source ≠ desktop` 的快照不再采信(跨宿主守卫),缺失/失效/被守卫时自动请求重投影,未知期间不渲染伪造百分比。至此六阶段全部有发布者。

### 8.6 六次复核追记(2026-07-24,阶段 E:证据引用化替代有损截断)

背景:同会话 Desktop 15% vs CLI 51% 对照暴露两个事实——TUI 无 Layer 1(下一请求真发 255k 全文);而 Desktop microcompact 是「有损截断」(800 字符预览,无回来的路,四类误解风险:中段黑洞、魔数无语义、预览堆积、Layer 2 二次失真)。经用户拍板,按 17 号文档 P1/P2 原设计补完:

1. **Layer 0 通用材料化**(`runtime-node/tool-artifact-store.ts`):超 6000 字符工具输出落盘 `~/.peer-agent/artifacts/<conv>/`,provider 消息只留 `local_tool_result_ref` 骨架(head/tail + keyFindings + suggestedRetrieval + 勿重跑提示);错误结果双倍预览;已是 local_*_ref 的跳过;写盘失败降级 inline。Desktop tool-orchestrator 与 TUI executionContent 同源接入,UI 流不受影响。
2. **Layer 1 单源化**:microcompact 下沉 `runtime-core/microcompact.ts`(含 ref 骨架保留、可回捞线索抽取);Desktop re-export(legacy 块待删);TUI runTurn 发送切片接入,state 保留原文,requestProjection 改发送口径——**两端占用收敛 + CLI 每轮真实节省 ~180k tokens**。
3. **级联清理**:conversations:delete 同时清理会话 artifact 目录(ADR 34 同口径)。

验证:runtime-node 4 新测(含中段可从 artifact 找回、ref 骨架显著小于原文、级联清理)、desktop chat-runtime 251、context-compactor 46(已改测共享实现)、TUI 484 全绿;四包 tsc 通过。

待后续:Desktop context-compactor 内 legacy microcompact 死代码块删除;artifact 体积上限/LRU;e2e「模型用 rg 从 artifact 找回中段」验收。

### 8.7 下一批优先级

1. 切模型时触发 restored 重投影,消除圆环 RC4 分母残留期。
2. TUI 回合间静态投影补计 continuity system block。
3. TUI 中途压缩 marker 的 turn 内即时持久化(对齐不变式 6)。

## 九、修订记录

| 日期 | 变更 |
|------|------|
| 2026-07-24 | 初版:压缩路径普查(5 入口、口径重复表、语义分叉)、根因、单闸门目标架构、Phase 0–3 路线 |
| 2026-07-24 | Phase 1 并入右下角占用圆环失准治理(renderer 估算器删除、revision 重投影、跨端 source 守卫) |
| 2026-07-24 | 二次复核:新增第八节落地进度(Phase 1 主体 + Desktop 单入口已落地;生命周期 1/6 接线、双 hard 线分叉等新问题入账) |
| 2026-07-24 | 三次复核:双 hard 线已收敛(0.92 单值);投影生命周期 per-turn 接线完成(preflight/post_compaction/tool_result/turn_complete + 双端 stream_preview 叠加,restored 待 Phase 1.4);新增 `chat:context:projection` IPC 与 renderer revision 序合并 |
| 2026-07-24 | 四次复核:Phase 0 清零——手动 /compact 归一单入口(manual 语义)、emergency 收敛为 recoverFromPromptTooLong 共享 helper、qoder 补 emergency+持久化、circuit breaker 按会话隔离、TUI 僵尸切分删除 |
| 2026-07-24 | 五次复核:台账主体清零——`_compaction` 进 protocol(两端同一 buildCompactionMarker)、PTL 分类下沉 runtime-core、TUI 中途 preflight/emergency + 手动全量语义对齐、restored 重投影 + 跨宿主 source 守卫(六阶段全部接线) |
| 2026-07-24 | 六次复核(阶段 E):证据引用化替代有损截断——Layer 0 通用材料化(artifact + local_tool_result_ref)双端同源、microcompact 下沉 runtime-core、TUI 发送切片接入 Layer 1、artifact 随会话级联清理 |
