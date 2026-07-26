# CLI 与桌面端上下文百分比对不上（深度思考阶段）根因分析

创建时间: 2026-07-25
最后更新: 2026-07-26
状态: 历史根因已解决，本文保留修复前源码证据
关联代码仓: `peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）
关联文档:

- `knowledge/experience/context-occupancy-ring-inaccuracy-root-cause.md` — 圆环历史根因（RC1–RC9）
- `knowledge/decisions/56-provider-observed-context-accounting.md` — 权威记账口径
- `knowledge/decisions/52-unified-next-request-context-accounting.md` — 下一请求投影 seam

> 2026-07-26 更新：本文记录的是统一架构落地前的根因。当前生产代码已经删除
> Desktop renderer 的 `streamPreviewTokens/authoritativeContext`、TUI 私有 pressure
> projection 和跨宿主 source 守卫，改由 `ContextAccountingSnapshot` 贯穿 Runtime、
> 持久化与双端展示。流式 reasoning/正文尚未被 provider 计量时保持最后一次权威百分比，
> 不附加自定义符号，也不再由两端字符估算器各自产生百分比。

## 现象

同模型 `grok-4.5`、同为 high /「深度思考」进行中时：

| 端 | 文案 | 百分比 |
|----|------|--------|
| 桌面端 | `深度思考` | `42%` |
| CLI (TUI) | `high` | `1%` |

本篇只回答「百分比为何对不上」。effort 文案差异是本地化（`high` → 中文「深度思考」），与百分比无关。

## 先澄清

1. **这个数字不是思考进度**，是上下文占用环：`nextRequestInputTokens / contextWindow`。
2. **两端在 mid-turn 都不把 thinking/reasoning 计入 preview**。
   上一版把「Desktop 计 thinking、CLI 不计」当成主因，**已被源码否定**。

## 重读后的代码事实

### Desktop 分子

路径：

1. `ComposerTokenUsageDisplay` 取 `authoritative + draft + streamPreview`
2. `resolveContextOccupancyTokens`：
   ```ts
   return authoritative == null ? null : authoritative + draft + Math.ceil(preview);
   ```
3. `TokenUsageDisplay`：
   ```ts
   ctxPercent = min((currentContextTokens / ctxWindow) * 100, 100)
   展示: Math.round(ctxPercent)%
   ```

`streamPreviewTokens` 只在 **正文 delta** 上累加：

```ts
// useConversationStreamRouter.ts
onChatStreamDelta:
  // 注释：隐藏推理（thinking）不进下一请求，不计入。
  streamPreviewTokens += estimateStreamDeltaTokens(content)

onChatStreamThinking:
  // 只更新 thinking typewriter / UI，不碰 streamPreviewTokens
```

权威基线来源：

- 会话 `contextSnapshot`（`source` 缺失或 `desktop` 才采信；`source === 'tui'` 会被跨宿主守卫置 null）
- stream / compaction final 投影事件
- 无权威时圆环保持 unknown（`contextReady = loadStatus==='ready' && authoritativeContext != null`）

分母：

- 优先 `authoritativeContext.contextWindow`
- 否则 `defaultProvider.contextWindow`

### CLI 分子

路径：

1. `app.tsx` → `createComposerStatus({ nextRequestInputTokens: snapshot.nextRequestInputTokens, contextWindow })`
2. `composer-status.ts`：
   ```ts
   tokens = floor(nextRequestInputTokens) // 有则用投影，否则 fallback usage
   percent = round(tokens / contextWindow * 100)
   // tokens>0 且 rawPercent<1 时显示 <1%
   ```

mid-turn 更新：

```ts
// chat-controller.ts
// 注释：assistant 正文累积（不含 reasoning，隐藏推理不进下一请求）
streamedPreviewText 仅在 event.type === 'message.delta' 时 += content
// reasoning.delta 只写 thinking segment
flush:
  pressure = pressureFor(conversationModelMessages, snapshot.usage, streamedPreviewText)
  publish({ nextRequestInputTokens: pressure.nextRequestInputTokens })
```

`pressureFor` 会重算：

- 本宿主 `projectSystemMessages`
- microcompact 后的 messages
- tools schema
- `draftText`（此处复用为 stream preview 文本）
- ADR 56：有 provider usage 时 usage 作权威下界

分母：

- `modelSelection.catalog` 里当前模型的 `contextWindow`
- controller 内 `resolveContextWindow()` 同源

## 纠正：什么不是根因

| 误判 | 源码事实 |
|------|----------|
| Desktop 把 thinking 计入占用环 | `onChatStreamThinking` 不累加 `streamPreviewTokens`；注释写明不计入 |
| CLI 不计 reasoning 而 Desktop 计 | 两端语义一致：都不计 hidden reasoning |
| 百分比是思考进度条 | 是上下文占用 |
| effort 档位不同 | 都是 high，只是本地化文案不同 |

## 真正根因（按解释力排序）

### RC1（主因）：对比的是「宿主本地权威基线」，不是共享计数器

两端圆环都依赖各自会话态上的 `nextRequestInputTokens`：

- Desktop 只信任 `source === 'desktop'`（或无 source 的旧快照）
- CLI 写入/使用 `source: 'tui'` 一侧的投影
- 跨宿主恢复时 Desktop 会把 TUI 快照置 null，再走 `chatContextRestored` 按 **Desktop 成分** 重算

因此：

- 即便模型同为 `grok-4.5`、都在「深度思考」中
- 若会话历史不同、是否同一会话、是否刚从另一端续接、system/tools 成分不同
  → 基线分子可以差一个数量级（例如 42% vs 1%）

这与历史 RC9 / 文档 21 §13.3「跨宿主不直接采信对方 next-request 快照」一致。

### RC2（次因，pure-thinking 阶段尤其明显）：mid-turn 预览都不涨 thinking

深度思考时模型先吐 reasoning、正文未到：

- Desktop：`streamPreviewTokens` 不涨（thinking 不计）
- CLI：`streamedPreviewText` 不涨（reasoning 不计）

于是 **两端百分比在 pure-thinking 阶段都基本冻结在进入本 turn 前的权威基线**。
截图差 42% vs 1%，更像是 **进 turn 前基线已经不同**，而不是 thinking 过程把 Desktop 抬上去了。

（若本 turn 已有 tool/message 正文流过，preview 才会动；但截图态是「深度思考中」，更符合冻结基线。）

### RC3（次因）：基线怎么算，宿主成分表不同

CLI 每次 `pressureFor` 用：

- TUI 的 system messages
- TUI 的 toolDefinitions
- microcompact 后的 messages
- provider usage 下界

Desktop 权威投影来自 Desktop Runtime / main process 的完整 canonical request（system + tools + history 等）。

即使「同会话同模型」，两边 idle/restored 后的数字仍可能有成分差；这是跨宿主投影问题，不是圆环渲染公式问题。

### RC4（次因，通常不是 42x 差距的主驱动）：分母与舍入

- Desktop 分母：权威 window → provider window
- CLI 分母：catalog `contextWindow`
- 同模型通常应接近，但配置缺失/回退路径不同时会偏
- 展示都是 round；CLI 另有 `<1%` 文案规则

单靠分母很难单独解释 42% vs 1%，除非一边 window 差了几十倍且分子碰巧相同——更常见仍是分子基线不同。

## 对应截图的因果链（纠正后）

```text
两端都在 high / 深度思考
  → reasoning 流式中，正文未到
  → Desktop/CLI 都不把 thinking 计入 stream_preview
  → 圆环冻结在「进入本 turn 前」的 nextRequestInputTokens 基线
  → Desktop 会话权威基线较高 → 42%
  → CLI 会话权威基线很低（短会话 / 另一会话 / 尚未 restored 完整成分 / 跨宿主未共享基线）→ 1%
  → 用户误以为「思考进度对不上」
```

## 与历史文档关系

| 项 | 关系 |
|----|------|
| 上一版本文件主因「Desktop 计 thinking」 | **错误，已废止** |
| RC9 跨端分子/投影 | 仍相关：基线是宿主本地投影 |
| ADR 56 final 权威 | 解释 turn 结束后下界；不解释 pure-thinking 中预览冻结 |
| 文档 21 §13.2 stream_preview | 两端实现一致：只叠 assistant 正文，不含 hidden reasoning |

## 修复方向（仅建议，本篇不实施）

1. **先统一对比变量**
   验收必须固定：同一 `conversationId`、同一模型、同一构建、同一 turn 阶段（idle / pure-thinking / message-streaming / turn-complete）。

2. **若产品要求跨端数字一致**
   - 共享同一 Runtime 投影服务，或
   - 跨宿主恢复时用同一 canonical request 成分表重算，而不是各算各的
   - 这比改圆环 UI 更根本

3. **不要用「让 thinking 计入 preview」去对齐截图**
   两端代码与注释已明确 hidden reasoning 不进下一请求；强行计入会与 ADR 52/56 冲突。

4. **可观测性**
   圆环 hover / CLI 调试输出同时打印：`source`、`nextRequestInputTokens`、`contextWindow`、`preview`、`usage`，避免再靠猜。

## 验收判据

1. 同会话同模型 pure-thinking：两端百分比接近进入 turn 前的 idle 值，且互相对齐（允许小舍入差）
2. message-streaming：两端都只因正文 preview 上涨，不因 reasoning 上涨
3. turn-complete：preview 归零，回到各自/共享 authoritative 投影

## 结论

**真正根因不是 thinking 计入策略分叉，而是：**

1. **百分比冻结在宿主本地权威基线**（pure-thinking 时 preview 两端都不涨）
2. **Desktop 与 CLI 的基线来自不同会话态/成分投影，且跨宿主不直接共享 next-request 快照**

所以截图里的 42% vs 1%，应优先查「是不是同一会话的同一基线」，而不是去改 effort 或把 thinking 塞进占用环。

## 修复后状态（2026-07-26）

- Desktop 与 CLI/TUI 共用 `ContextAccountingCompactionPipeline` 和
  `ContextAccountingLifecycle`；
- `ContextAccountingSnapshot` 是唯一跨宿主容量状态；
- restore 使用 `count_only/restored`，model switch 使用 `model_changed/unknown`；
- Anthropic/Gemini API-key 可在发送前 exact count，其余渠道显式为
  `observed_usage_only`；
- stream/tool 阶段只在 Runtime 内标记 `pendingUncountedChanges`，双端百分比不变且不附加
  自定义符号，不伪造动态 token；
- counted/observed 漂移超过 2% 时降级到 provider usage，并以 `!` 告警；
- 旧 `chat:context:projection`、`nextRequestInputTokens`、renderer estimator 和 TUI
  `context-pressure` 已删除，并由架构守卫防回归。

因此本文列出的“宿主本地权威基线分叉”已不再是当前架构事实；后续若再次出现差异，应优先
检查 snapshot identity、provider capability、content revision 与 model key，而不是恢复
宿主本地估算。

## 修订记录

| 日期 | 变更 |
|------|------|
| 2026-07-25 | 初版：误判 Desktop 计 thinking 为主因 |
| 2026-07-25 | 重读源码纠正：两端 thinking/reasoning 均不计 preview；主因改为宿主本地权威基线差异 + pure-thinking 冻结 |
| 2026-07-26 | 标记历史根因已解决：唯一 ContextAccountingSnapshot 与共享 lifecycle/pipeline 已落地；pending 保持内部状态，不再向百分比附加 `+` |
