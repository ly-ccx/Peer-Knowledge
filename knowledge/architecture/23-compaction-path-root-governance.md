# 压缩路径根治理:单一 Compaction Pipeline 与双端一致性

创建时间:2026-07-24
最后更新:2026-07-25
状态:核心 provider 发送管线已统一，手动命令与 UI 协议迁移继续
关联代码仓:`peer_agent`(本地 `/Users/liangyin/Documents/DEV/github/peer_agent`)
关联文档:

- `knowledge/decisions/17-local-context-compaction.md` — 压缩机制设计(分层、触发、摘要策略)
- `knowledge/architecture/21-auto-context-compaction-run-resume.md` — 压缩与 run 续接协议
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — 双宿主治理(P1 债务「Compaction 算法双轨无统一接口」的展开)
- `knowledge/decisions/42-context-display-vs-trigger-accounting.md` — 显示口径与触发口径
- `knowledge/decisions/56-provider-observed-context-accounting.md` — provider 实测优先的精确上下文记账（当前权威）
- `knowledge/decisions/52-unified-next-request-context-accounting.md` — 已被 ADR 56 部分取代的本地估算方案
- `knowledge/experience/context-occupancy-ring-inaccuracy-root-cause.md` — 右下角占用圆环失准根因(本治理 Phase 1 的直接受益面)

## 一、一句话结论

> 2026-07-25 口径修订：本文早期阶段把共享启发式 `TokenEstimator` 视为上下文权威来源。
> 该部分已被 ADR 56 取代。共享 estimator 可以保留给非容量场景，但压缩闸门、上下文圆环、
> provider request 放行和权威快照只能消费 provider usage 或 provider-aligned exact count。

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
  └─ ContextAccountingCompactionPipeline
      ├─ BUILD canonical request
      ├─ COUNT provider usage / provider-aligned exact count
      ├─ DECIDE input budget / compaction threshold
      ├─ COMPACT + REBUILD + RECOUNT
      ├─ SEND fingerprint gate
      ├─ OBSERVE / VERIFY
      ├─ RECOVER prompt-too-long
      ├─ microcompact / split / summary cascade(内部原语)
      └─ CompactionStrategy:LlmSummaryStrategy / StructuralStrategy

宿主适配层(薄)
  Desktop:ProviderRequestAdapter + IPC/持久化 HostEffectsAdapter
  TUI:ProviderRequestAdapter + snapshot/持久化 HostEffectsAdapter

入口闸门(唯一)
  普通发送 / tool loop / Goal tick / manual / auto / emergency
    -> ContextAccountingCompactionPipeline.execute(command)
```

### 4.2 不变式(在 17/21 号文档基础上新增)

1. **单闸门**:任何 provider request 只能经 CompactionGate 发出;新增 wire/loop 无需(也不允许)自行接压缩。
2. **单真值**:provider usage 与 provider-aligned exact count 是容量真值;启发式 estimator 不得参与 UI、压缩、放行或权威快照。
3. **单形状**:`_compaction` marker 与压缩后会话形状由 protocol 类型约束;两端持久化必须产出同一形状,任一端可恢复另一端压缩过的会话。
4. **手动语义一致**:`/compact` 在两端等价(默认真·全量 + `preserveLatestUserTurn=false`);如需宿主差异,必须落 ADR。
5. **emergency 双端等价**:PTL 分类、force 压缩、重试上限(1 次)两端一致;TUI 不得因"终端场景少"而豁免。
6. **状态不出全局**:circuit breaker 等失败状态按 conversationId 隔离,不得使用 module 级可变量。
7. **共享原语不算统一**:Desktop 与 CLI/TUI 不得分别编排 preflight、压缩、重计数、发送和 PTL recovery。
8. **策略可替换、状态机不可替换**:摘要实现可通过 `CompactionStrategy` 注入，但切分合同、epoch、重计数、重试和终态必须一致。

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

### Phase 4 — 端到端管线收敛（ADR 56）

1. 在 runtime-core 建立 `ContextAccountingCompactionPipeline`，完整拥有
   BUILD → COUNT → DECIDE → COMPACT → REBUILD → RECOUNT → SEND → OBSERVE/RECOVER。
2. Desktop 的 `provider-request-coordinator`、`compaction-coordinator` 和 provider loops
   改为 adapters，删除宿主侧状态机编排。
3. CLI/TUI 删除 `provider-chat-model.compactModelMessagesMidTurn` 和 controller 私有压缩流程；
   `/compact`、自动 preflight 与 emergency 都提交给共享 pipeline。
4. `context-pressure` 退化为 snapshot formatter，不再计算或决定容量。
5. 原有共享 estimator 退出容量链路；精确记账按 ADR 56 的 provider usage /
   provider-aligned exact count 和 fingerprint 合同实现。
6. 用跨宿主契约测试证明同 fixture 的 count、decision、epoch、marker、retry 终态一致。

## 六、验收标准

1. 所有 provider send 只能由 `ContextAccountingCompactionPipeline` 放行；宿主和 provider loop 无直接发送旁路。
2. `decideContextCompaction`、`splitMessagesForCompaction`、summary cascade 和 PTL retry 在 pipeline 外的生产调用点为 0。
3. qoder loop 与 TUI 均具备 preflight + emergency,测试覆盖 PTL 重试。
4. `/compact` 在 Desktop 与 TUI 对同一 fixture 产生相同的持久化形状与保留窗口。
5. TUI 压缩后的会话可被 Desktop 打开并继续,反之亦然(契约测试固化)。
6. 22 号文档 P1 债务只有在 Desktop 与 CLI/TUI 不再拥有私有压缩状态机后才可标记为已清偿。

## 七、评审问题单(压缩相关变更必答)

1. 该变更是否新增了第二个压缩入口?(只允许 kernel 闸门)
2. 是否让任何启发式估算重新进入 UI、压缩、放行或权威快照?
3. 压缩后的会话形状是否仍满足 protocol 定型,两端可互相恢复?
4. 新增 provider loop / wire 是否自动获得 preflight + emergency(而非手工接线)?
5. 手动 / 自动 / 紧急三种触发在两端语义是否仍一致?
6. 该变更是否让宿主直接编排了 pipeline 内部原语?(生产宿主调用必须为 0)

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

### 8.5 五次复核追记(2026-07-24 同日落地,当时判定“台账主体清零”)

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

待后续:~~Desktop context-compactor 内 legacy microcompact 死代码块删除;artifact 体积上限/LRU;e2e「模型用 rg 从 artifact 找回中段」验收~~ 均已于同日收尾(见 8.6.1)。

#### 8.6.1 阶段 E 收尾(2026-07-24,原语下沉台账清零)

1. legacy microcompact 死代码块(~410 行)已从 context-compactor 删除,runtime-core 成为唯一实现。
2. artifact 体积治理:单会话预算 256MB,每次写后按 mtime LRU 逐出最旧文件(新写入文件不会被误逐);治理失败不阻断材料化。
3. 检索回路 e2e:测试验证「预览确实看不到中段 + 沿 suggestedRetrieval 用真实 shell 工具(grep/tail)能找回中段」——回来的路是可执行的事实,不是注释。

至此共享原语、marker 和 Layer 0/1 下沉台账清零；但 2026-07-25 复核确认 Desktop 与
CLI/TUI 仍分别编排端到端压缩状态机，主线不能宣告全部完成，见 8.8。

### 8.7 下一批优先级

1. 按 ADR 56 收敛 `ContextAccountingCompactionPipeline`，删除 Desktop/CLI 双编排。
2. 切模型时触发 restored 重投影,消除圆环 RC4 分母残留期。
3. TUI 回合间静态投影补计 continuity system block。
4. TUI 中途压缩 marker 的 turn 内即时持久化(对齐不变式 6)。

### 8.8 七次复核追记（2026-07-25，端到端统一缺口）

对当前 `peer_agent` 代码重新核实后，结论是“共享原语”已经完成，但“共享管线”尚未完成：

| 层 | 当前事实 | 判定 |
|---|---|---|
| 统计常量与阈值 | Desktop 与 TUI 都调用 `runtime-core/context-projection.ts` | 已共享，但仍是 ADR 52 的启发式估算，ADR 56 尚未落地 |
| Provider usage | 两端都能取得 usage | 仍只作诊断，未成为 UI 与压缩权威值 |
| microcompact / split / summary cascade | 位于 runtime-core | 共享原语已完成 |
| Desktop 编排 | `provider-request-coordinator` + `compaction-coordinator` + `context-compactor` | Desktop 私有状态机仍存在 |
| CLI/TUI 编排 | `chat-controller` + `provider-chat-model.compactModelMessagesMidTurn` | CLI/TUI 私有状态机仍存在 |
| PTL classifier | runtime-core 单源 | 共享，但尚未覆盖 Grok `maximum prompt length ... request contains ...` 文案 |

因此当前不能表述为“Desktop 与 CLI 共用一套计算和压缩逻辑”。准确表述是：

```text
共享了一套旧估算内核和大部分压缩原语，
但 Desktop 与 CLI/TUI 仍有两条端到端编排管线。
```

完成标准以 ADR 56 为准：宿主不再直接调用判定、切分、摘要和 PTL retry 原语；所有发送
经同一个 `ContextAccountingCompactionPipeline` 的 fingerprint gate 放行。

### 8.9 八次复核追记（2026-07-25，Phase 4 核心发送链路落地）

本轮完成了七次复核指出的核心缺口：

| 层 | 落地事实 | 判定 |
|---|---|---|
| 共享状态机 | 新增 `runtime-core/context-accounting-pipeline.ts`，统一 build/count-or-observe/decide/compact/rebuild/send/overflow retry | 核心已落地 |
| Desktop 编排 | OpenAI/Anthropic/Gemini/Qoder 全部改走 `executeDesktopProviderRequest`；loop 私有 recovery 删除 | provider 发送链路已统一 |
| CLI/TUI 编排 | `provider-chat-model.runTurn` 改走同一 pipeline；私有 mid-turn compactor 与 PTL catch 删除 | provider 发送链路已统一 |
| 压缩策略 | 新增 `compactMessagesWithSummaryStrategy`；TUI turn 内与 `/compact` 均复用 | 策略边界已共享 |
| 实测真值 | 上一轮 usage 显式进入下一轮；498K 可触发预压缩，显示不再被低估算覆盖 | 已修复已知故障 |
| PTL 证据 | Grok maximum-prompt 文案可解析 requested/max；同请求仅重试一次 | 已落地 |
| 手动入口 | Desktop/TUI 仍由各宿主命令入口调用共享 strategy/coordinator | 尚未完全 command 化 |
| 未计量 UI | 取得 usage 后精确；无 usage / exact counter 时仍有兼容 projection | 尚待改“待计量” |

因此当前准确结论更新为：

```text
Desktop 与 CLI/TUI 的普通 provider 发送、自动压缩和 PTL 恢复，
已由同一个 ContextAccountingCompactionPipeline 编排；
手动 compact command、无实测 UI 和 provider exact-count adapter
仍是 Phase 4 的剩余工作。
```

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
| 2026-07-24 | 阶段 E 收尾:legacy 死代码块删除(~410 行)、artifact 256MB/LRU 体积治理、检索回路 e2e 验收——台账主线清零 |
| 2026-07-25 | 上下文真值改由 ADR 56 定义：provider usage / provider-aligned exact count 取代启发式 estimator 的权威地位 |
| 2026-07-25 | 七次代码复核：纠正“台账主线清零”结论；共享原语不等于共享管线，Desktop/CLI 双编排列为 Phase 4 首要债务 |
| 2026-07-25 | 八次代码复核：共享 ContextAccountingCompactionPipeline 落地；四条 Desktop loop 与 CLI/TUI provider loop 统一，498K usage 与 Grok PTL 回归通过；手动 command、未计量 UI、exact-count adapter 留作 Phase 4 收尾 |
