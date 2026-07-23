# TUI 会话渲染窗口技术方案

创建时间：2026-07-23
最后更新：2026-07-23
状态：Implemented（阶段 1 已落地，待性能基线验收）
变更级别：B 级（调整 TUI 会话恢复与消息表达，不改变模型上下文语义）
关联代码：`peer_agent/apps/tui`、`peer_agent/packages/conversation-store`
范围声明：本文记录技术方案与阶段 1 落地契约；代码实现在 `peer_agent` 仓完成。

## 一、结论

当前阶段不引入动态高度虚拟滚动。默认渲染范围定义为：

> **最近一次有效压缩边界（包含该压缩完成消息）后的默认渲染规则，是从该边界一直渲染到会话末尾；若不存在有效压缩边界，则渲染受消息数与估算字符数双重限制的尾部窗口。**

完整会话仍然持久化；模型续聊上下文仍按现有恢复与压缩规则构造。渲染窗口只控制终端 UI 当前挂载的消息，不删除历史、不改变模型输入、不改变导出与搜索语义。

首期优先在 TUI 展示层前建立独立窗口投影，以最小改动解决全量组件挂载导致的白屏。历史回看使用双边有界页面，不因连续向前翻页重新累积完整 transcript。后续若性能数据证明 JSONL 全量读取或全量解析仍是瓶颈，再把同一窗口契约下沉至 `conversation-store` 的游标读取接口。

## 二、背景与问题

OpenTUI 当前没有通用、稳定的动态高度虚拟列表。项目所用 OpenTUI 0.4.3 的 `viewportCulling` 只减少视口外绘制，不阻止 React 组件创建、Markdown 解析和整体布局。消息又包含 Markdown、思考过程、工具调用、图片占位、流式文本和 Goal 状态，直接引入虚拟滚动会同时引入高度测量、滚动锚点、展开状态和流式重排问题。

当前大会话恢复后，TUI 将完整消息数组交给 React/OpenTUI 渲染。随着会话增长，Markdown 解析、组件树创建、布局计算和终端绘制成本线性增加，极端情况下出现长时间白屏。因此本方案选择“有语义的尾部窗口”，而不是先实现虚拟滚动。

### 2.1 目标

1. 恢复或切换会话时，不再默认挂载完整 transcript。
2. 有压缩历史时，以最近一次有效压缩完成消息为窗口起点，并保留该消息。
3. 无压缩大会话具有确定、可测试的尾部窗口兜底。
4. 用户可按双向有界页面回看更早历史，连续翻页也不会累积为全量渲染。
5. 流式输出、工具调用更新和新压缩完成时保持稳定的尾部跟随与窗口切换行为。
6. 旧会话、损坏元数据和未完成压缩都能安全降级。

### 2.2 非目标

- 当前阶段不实现动态高度虚拟滚动；仅在连续全历史浏览成为高频需求且有界分页不能满足时重新评估。
- 不裁剪或改写会话 JSONL。
- 不把“展示窗口”当作模型上下文窗口。
- 不改变 compact 摘要的生成质量或 token 压缩算法。
- 首期不要求存储层反向分页；该能力作为第二阶段优化。
- 不修改 Desktop 的会话渲染策略。

## 三、现状与代码锚点

以下为阶段 1 实施前的代码基线，用于解释本方案解决的问题：

| 链路 | 实施前行为 | 代码锚点 |
|---|---|---|
| 消息渲染 | `ChatHistory` 直接遍历 `snapshot.messages`，没有窗口投影 | `apps/tui/src/app.tsx`：`ChatHistory` |
| 会话加载 | persistence 调用 store 的 `getConversation(id)`，读取并解析完整消息，再交给 controller restore | `apps/tui/src/conversation-persistence.ts`：`loadConversation`；`packages/conversation-store/src/index.mjs`：`getConversation` |
| 恢复状态 | controller 将恢复消息写入 `snapshot.messages`，同时由可转换消息重建 provider history | `apps/tui/src/chat-controller.ts`：`restore` |
| 结构压缩 | `compactModelMessagesStructurally` 只替换 `conversationModelMessages`；展示 transcript 不删除旧消息 | `apps/tui/src/context-compact.ts`；`apps/tui/src/chat-controller.ts`：`compactContext` |
| 压缩 UI 记录 | 压缩时先发布 pending progress system message，成功后替换为 `compact.phase === 'done'` 的 system message | `apps/tui/src/chat-controller.ts`：压缩进度与完成消息 |
| 压缩持久化 | `compact` 元数据会随稳定消息写入 JSONL，恢复时由 `storedCompactMeta` 读回；pending 消息不会恢复 | `apps/tui/src/conversation-persistence.ts`：`syncSnapshot`、`storedMessage` |

关键判断：当前已经存在可持久化的显式压缩完成标记，无需通过文案猜测边界。但它是消息级 UI 元数据，不是独立的 store 索引；首期可直接使用，后续应版本化。

## 四、设计原则

1. **展示与上下文分离**：`modelMessages` 决定模型连续性，`renderMessages` 决定 UI 成本，两者不得互相替代。
2. **边界显式优先**：只认结构化 `compact.phase === 'done'`，不匹配 “Compacted” 文本。
3. **尾部永远完整**：默认窗口必须包含当前进行中的 turn 以及会话末尾。
4. **双边有界回看**：历史回看每次替换为一个有界页面，同时维护起止锚点；连续翻页不得累积完整 transcript。
5. **稳定优于精确**：字符预算是低成本估算，不做终端行高预排版。
6. **兼容优先**：识别失败时退化到有上限的尾窗，而不是全量渲染。

## 五、渲染窗口数据契约

阶段 1 已新增纯函数模块 `apps/tui/src/conversation-render-window.ts`，使窗口计算可独立单测。

```ts
export interface ConversationRenderWindowPolicy {
  /** 无有效压缩边界时，默认最多保留的顶层消息。 */
  readonly fallbackMaxMessages: number;
  /** 无有效压缩边界时，从尾部反向累计的估算字符预算。 */
  readonly fallbackMaxChars: number;
  /** 每个历史页面最多包含的顶层消息数。 */
  readonly historyPageMessages: number;
  /** 每个历史页面的估算字符预算。 */
  readonly historyPageMaxChars: number;
  /** 防御异常压缩后超长尾部的硬上限；正常路径不截断。 */
  readonly emergencyMaxMessages: number;
  /** 防御单条/尾部内容异常膨胀的估算字符硬上限。 */
  readonly emergencyMaxChars: number;
}

export type ConversationRenderWindowState =
  | { readonly mode: 'latest' }
  | {
      readonly mode: 'history';
      readonly startMessageId: string;
      readonly endMessageId: string;
    };

export interface ConversationRenderWindow {
  readonly mode: ConversationRenderWindowState['mode'];
  /** 当前页面首条消息在完整 snapshot.messages 中的下标。 */
  readonly startIndex: number;
  /** 当前页面末条消息在完整 snapshot.messages 中的下标。 */
  readonly endIndex: number;
  /** 当前页面的选择原因。 */
  readonly reason: 'latest-compaction' | 'fallback-tail' | 'history-page' | 'empty';
  /** 最近有效压缩消息 ID；不存在时省略。 */
  readonly compactionMessageId?: string;
  /** 当前页面之前隐藏的消息数。 */
  readonly hiddenBefore: number;
  /** 当前页面之后隐藏的消息数。 */
  readonly hiddenAfter: number;
  /** 是否还能向前加载。 */
  readonly canLoadEarlier: boolean;
  /** 是否还能向后加载。 */
  readonly canLoadLater: boolean;
  /** 是否触发紧急硬上限。 */
  readonly emergencyTruncated: boolean;
  readonly estimatedRenderedChars: number;
}

export interface ConversationRenderProjection {
  readonly messages: readonly ChatMessage[];
  readonly window: ConversationRenderWindow;
}
```

初始建议值（须通过基准测试校准，而非永久魔数）：

```ts
const DEFAULT_TUI_RENDER_WINDOW_POLICY = {
  fallbackMaxMessages: 120,
  fallbackMaxChars: 160_000,
  historyPageMessages: 80,
  historyPageMaxChars: 160_000,
  emergencyMaxMessages: 600,
  emergencyMaxChars: 800_000,
} as const;
```

### 5.1 字符成本估算

`estimateMessageChars(message)` 至少计入：

- `message.content.length`；
- thinking/reasoning 文本；
- assistant segments 中的 text/thinking/tool 展示文本；
- 工具 detail、错误详情和证据摘要；
- 图片按固定占位成本计算，不读取二进制。

估算只用于选取消息边界。单条消息不能切成半条；若末尾单条消息已经超过预算，仍必须完整保留该消息，并设置 `emergencyTruncated` 供遥测记录。

## 六、边界算法

### 6.1 有效压缩边界

从 `snapshot.messages` 尾部向前扫描，第一条满足全部条件的消息即为最近一次有效压缩边界：

1. `message.role === 'system'`；
2. `message.pending !== true`；
3. `message.compact?.phase === 'done'`；
4. `message.id` 非空且该消息能按正常 ChatMessage 恢复；
5. 边界位于当前线性会话消息序列内。

不认可：`phase === 'progress'`、仅文案包含 compact、缺失/未知 phase、解析失败的 compact 对象。

当前会话结构没有分支图，因此“当前分支”就是 JSONL 恢复后的线性顺序；未来若支持分支，边界选择必须沿 active head 的祖先链完成，不能继续用全数组最后一次匹配。

### 6.2 默认窗口选择

伪代码：

```ts
function selectInitialRenderWindow(messages, policy) {
  if (messages.length === 0) return emptyProjection();

  const compactIndex = findLastIndex(messages, isValidCompletedCompaction);
  if (compactIndex >= 0) {
    return applyEmergencyGuard({
      messages,
      preferredStartIndex: compactIndex, // 包含压缩完成消息
      reason: 'latest-compaction',
      compactionMessageId: messages[compactIndex].id,
      policy,
    });
  }

  const startIndex = scanBackwardUntilEitherBudgetReached(
    messages,
    policy.fallbackMaxMessages,
    policy.fallbackMaxChars,
  );
  return project(messages, startIndex, 'fallback-tail');
}
```

规则优先级：

1. 空会话返回空窗口；
2. 有有效压缩：从最近一次完成边界（含边界消息）到末尾；
3. 无有效压缩：执行**无压缩大会话的尾部窗口兜底**，从末尾反向取消息，消息数或字符预算任一达到即停止；
4. 压缩后尾部异常巨大：启用 emergency guard，但必须保证当前进行中 turn 的原子完整性，并显示“部分近期内容因终端性能限制未加载”。

### 6.3 Turn 原子性

窗口边界不得落在一个工具交互链中间。初步选出起止下标后做 turn 修正：

- 若起点是 `tool` 消息，向前找到产生对应 tool call 的 assistant 消息；
- 若起点是 pending assistant/compact 消息，向前包含触发它的最近 user 消息；
- 历史页面的末尾向后补齐当前 turn，直到下一条 user/system 边界；
- 找不到配对时保留当前消息并记录诊断，不得无限向前扫描。

有压缩边界时，以压缩 system 消息为最高优先级起点，不跨边界补齐更早工具链。实现对异常超长 turn 使用有限扫描，避免“原子性修正”反过来制造无界窗口。

### 6.4 多次压缩

只选择最后一条有效完成压缩消息。更早的压缩消息和历史默认隐藏。新压缩成功后，窗口起点原子切换到新的完成消息；新压缩仍在 progress 阶段时不切换边界。

## 七、状态归属与组件接入

### 7.1 不修改领域快照语义

`ChatSnapshot.messages` 继续表示 controller 当前持有的完整 transcript。不要直接把它裁成窗口，否则会影响：

- provider history 的恢复与后续发送；
- persistence 的增量去重和同步；
- usage/goal 等依赖完整快照的逻辑；
- 将来的导出、搜索或诊断。

窗口状态归 TUI view 层所有：

```ts
const projection = useMemo(
  () => projectConversationRenderWindow(snapshot.messages, renderWindowState, policy),
  [snapshot.messages, renderWindowState, policy],
);

<ChatHistory messages={projection.messages} ... />
```

`ChatHistory` 接收 `messages` 与 `window`，不再内部读取完整 snapshot；status、usage 等必要字段单独传入，避免未来误用全量列表。

### 7.2 会话身份与重置

窗口状态必须绑定 `conversationId`：

- 新会话：重置为空窗口；
- 切换/恢复会话：根据该会话消息重新计算初始窗口；
- 同一会话普通 append/update：latest 模式跟随尾部，history 模式保持双端 ID；
- `/clear` 或等效重置：清空窗口状态；
- 用户显式发送新消息：回到 latest 模式，使用户能看到自己触发的新 turn；
- 不跨会话复用消息下标，因为下标不是稳定 ID。

history 模式保存 `startMessageId` 与 `endMessageId`，每次投影时重新解析下标；任一 ID 不存在或顺序失效时重新执行默认算法。

## 八、历史回看交互

### 8.1 首屏提示

当 `hiddenBefore > 0`，在消息区顶部插入 UI-only banner（不得进入 `ChatSnapshot`、不得持久化）：

```text
↑ 早期历史未渲染：已隐藏 428 条  ·  /history earlier
```

有压缩边界时可显示：

```text
↑ 当前从最近一次压缩开始显示  ·  早期历史 428 条  ·  /history earlier
```

history 模式存在较新隐藏内容时，在页面底部显示：

```text
↓ 较新历史未渲染：已隐藏 320 条  ·  /history later  ·  /history latest
```

### 8.2 双向有界翻页

- 命令：`/history earlier`、`/history later`、`/history latest`；命令面板同时暴露 `/history-earlier`、`/history-later`、`/history-latest`。
- earlier/later 每次用新页面替换当前页面，页面受 `historyPageMessages` 与 `historyPageMaxChars` 双重约束。
- 相邻页面重叠一个完整 turn 作为视觉锚点，不把旧页面继续挂载在 React 树中。
- 只改变 `startMessageId` 与 `endMessageId`，不修改 snapshot 和持久化。
- 不提供 `/history all`，避免重新制造白屏。
- `/history latest` 恢复默认窗口。
- 到达开头或末尾后，以 notice 明示当前位置。

### 8.3 滚动锚点

翻页时通过相邻页面重叠一个完整 turn 提供稳定语义锚点。首期不依赖动态高度测量；OpenTUI 若支持可靠的 `scrollChildIntoView`，可再把重叠锚点定位到视区边缘。不能因为锚点 API 不可用而累积或加载全部历史。

## 九、流式更新与运行中行为

1. **尾部 append**：latest 模式包含新消息并继续自动跟随；history 模式保持固定双端 ID，只增加 `hiddenAfter` 与“较新内容”提示。
2. **原位更新**：pending assistant 的 delta、tool 状态和 compact progress 只更新对应 message ID，不重算默认起点。
3. **用户正在回看**：新 delta 不强制抢回底部，也不把新消息挂入当前历史页；用户显式发送消息时回到 latest。
4. **压缩 progress**：它不是有效边界，继续沿用原窗口。
5. **压缩 done**：同一 ID 从 progress 变为 done 后，若用户处于默认 latest 模式，则把起点切到该消息；若用户主动加载了更早历史，则当前 turn 内不跳动，显示“已产生新压缩边界”，在 `/history latest` 或下次恢复时采用新边界。
6. **压缩失败/取消**：移除或终止 progress 展示，不改变边界。
7. **超长单次输出**：窗口只能限制消息数量，无法避免一条巨型 Markdown 本身过重。首期记录该场景；后续可给消息正文增加折叠/截断投影，但不得静默丢内容。

## 十、持久化与兼容策略

### 10.1 首期兼容

当前 `compact` 字段已进入消息 JSONL，并由 `storedCompactMeta` 恢复。首期直接读取：

```ts
message.role === 'system' && message.compact?.phase === 'done'
```

旧会话没有该字段时，自动使用 fallback tail。未知字段或未知 phase 忽略，不报错、不全量渲染。

### 10.2 推荐的版本化演进

为避免 UI phase 永久承担领域边界语义，后续将 compact metadata 扩展为向后兼容结构：

```ts
interface CompactDoneMeta {
  readonly phase: 'done';
  readonly schemaVersion: 1;
  readonly compactionId: string;
  readonly completedAt: string;
  readonly beforeCount: number;
  readonly afterCount: number;
  readonly summarizedCount?: number;
  readonly reason?: 'manual' | 'auto';
}
```

新增字段保持 optional，旧 reader 忽略，旧记录仍可识别。不要为了窗口功能迁移或重写历史 JSONL。

### 10.3 存储层第二阶段

首期只减少渲染，仍会全量读取/解析 JSONL。若基准显示恢复时间主要耗在 I/O 或解析，扩展 conversation-store：

```ts
getConversationTail(id, {
  afterMessageId?: string,
  maxMessages: number,
  maxChars: number,
}): {
  meta: ConversationMeta;
  messages: StoredMessage[];
  hiddenBefore: number;
  cursorBefore?: string;
}

getConversationPageBefore(id, {
  cursor: string,
  limit: number,
}): ConversationMessagePage
```

但下沉前必须解决一个语义冲突：controller 续聊需要足够的 model history，而 UI 只需要 render history。因此不可简单用尾部读取结果替换 `restore` 的完整输入。可选路径是：

- 单独持久化可恢复的 compacted model state；或
- store 同时返回 `modelResumeState` 与 `renderPage`；或
- 保留完整 provider-history 恢复，UI 页面独立分页。

没有该契约前，禁止为了减少 I/O 而破坏续聊上下文。

## 十一、异常与降级矩阵

| 场景 | 行为 |
|---|---|
| 空会话 | 渲染空历史，无 banner |
| 无 compact 元数据 | 双预算尾部窗口 |
| 多个 done compact | 使用最后一个有效记录 |
| 只有 progress compact | 忽略，使用前一个 done；没有则 fallback tail |
| compact 元数据损坏/未知版本 | 忽略该条并继续向前找；最终 fallback tail |
| done 边界后消息少 | 从 done（含）完整渲染到末尾 |
| done 边界后异常超长 | emergency guard + 明示警告 + 保持当前 turn 完整 |
| 边界消息 ID 重复 | 采用数组中最后一个匹配，并记录诊断 |
| 恢复消息缺少 ID | persistence 现有兼容 ID 可用；仍失败则按位置计算且不持久化窗口 |
| 历史翻页时消息列表变化 | 以 `startMessageId` / `endMessageId` 重定位；任一失败则重新计算默认窗口 |
| 单条巨型消息 | 完整保留，记录超预算；后续单消息折叠治理 |
| store 读取失败 | 沿用现有错误呈现，不构造伪历史 |

## 十二、性能预算与遥测

### 12.1 预算

在常见开发机、120×40 终端、生产构建下，目标为：

| 指标 | 目标 |
|---|---:|
| 10,000 条、最近有 compact 的会话，窗口选择纯函数 p95 | ≤ 10 ms |
| 首屏挂载的顶层消息数（正常 compact 后） | 实际边界后数量，通常 ≤ 120 |
| 无 compact 会话首屏顶层消息数 | ≤ 120（turn 修正允许小幅超出） |
| 首屏估算字符量 | ≤ 160k（单条/turn 原子性例外） |
| 恢复到首个非空 history frame p95 | ≤ 500 ms |
| 流式 delta 的窗口重算 | 不得做全数组深拷贝或 Markdown 全量重建 |
| 连续加载 5 页历史 | 无白屏、无崩溃，内存增长与新增渲染内容近似线性 |

500 ms 指标包含当前全量 store 读取，因此若未达标，必须用 profile 区分 I/O/JSON parse 与 React/OpenTUI render，再决定是否进入存储分页阶段。

### 12.2 诊断字段

开发遥测/调试日志记录，不写入 transcript：

- `conversationMessageCount`
- `renderedMessageCount`
- `hiddenBefore`
- `windowReason`
- `compactionMessageId`（可 hash）
- `estimatedRenderedChars`
- `windowSelectionMs`
- `restoreReadMs`
- `firstHistoryFrameMs`
- `emergencyTruncated`

不得记录消息正文、摘要正文或工具敏感输出。

## 十三、测试设计

### 13.1 纯函数单元测试

为 `conversation-render-window.test.ts` 覆盖：

1. 空数组；
2. 小会话无压缩，全量展示；
3. 无压缩超过 message budget；
4. 无压缩超过 char budget；
5. 单条消息超过 char budget；
6. 一个 done compact，结果包含边界本身；
7. 多个 done compact，选择最后一个；
8. progress 在 done 后出现，仍选择之前 done；
9. 损坏 compact metadata 被忽略；
10. fallback 起点落在 tool chain 中时向前修正；
11. emergency guard 保留当前 turn；
12. earlier/later 双向翻页、相邻 turn 重叠与回到 latest；
13. 连续向前翻页时挂载量不累积；
14. history 模式 append 后页面稳定且 `hiddenAfter` 增长；
15. start/end message ID 消失后的重算；
16. 输入数组不被修改，返回顺序稳定。

### 13.2 Controller 与 persistence 测试

- compact done 消息保存后重启仍能识别；
- progress/pending 不会被当作恢复边界；
- 窗口变化不改变 `snapshot.messages`、provider model history 或持久化消息数；
- 旧 JSONL 没有 compact 字段时可以恢复；
- 新 metadata 被旧结构读取时不阻断会话；
- 切换会话不会复用另一个会话的窗口状态。

### 13.3 App 交互测试

- `ChatHistory` 只收到 projection messages 与 window metadata；
- 顶部/底部 banner 的隐藏数量与操作状态正确；
- `/history earlier` 与 `/history later` 每次替换为有界页面，不累积旧页面；
- `/history latest` 回到最后 compact 或 fallback tail；
- 流式更新不重置 history 页面，新消息只增加 `hiddenAfter`；
- compact done 在 latest 模式切换边界，在历史模式不抢跳；
- 无鼠标环境可完成全部操作。

### 13.4 性能回归夹具

生成确定性夹具：

- 10k 普通消息，无 compact；
- 10k 消息，最后 80 条前有 compact；
- 500 条大 Markdown/代码块；
- 200 轮 tool call/result；
- 单条 1 MB assistant 内容；
- 连续流式追加 10k delta。

测试至少采集窗口选择耗时、首帧时间、峰值 RSS、渲染消息数。CI 可对纯函数和渲染数量设置硬门槛；终端首帧与 RSS 在专用性能任务中观察趋势，连续两次超过基线 20% 阻断发布评审。

## 十四、分阶段实施

### 阶段 0：建立基线

1. 增加大会话夹具和恢复/首帧计时。
2. 分离 store read、restore、window selection、render 四段耗时。
3. 固化当前白屏案例为可重复性能场景。

验收：能稳定复现问题，并输出分段数据；不凭主观体感判断优化结果。

### 阶段 1：纯窗口投影（P0）

1. 新增 `conversation-render-window.ts` 与纯函数测试。
2. 从最后一个 `compact.phase === 'done'` 计算边界。
3. 实现无 compact 双预算 fallback 与 emergency guard。
4. 让 `ChatHistory` 仅接收 projection messages 与 window metadata。
5. 增加顶部/底部 banner、`/history earlier|later|latest` 及命令面板别名。
6. 接入 conversationId 重置和流式稳定策略。

验收：10k 会话首屏挂载数量受控；有 compact 时从最近 done 消息开始；无 compact 时不超过默认预算；续聊上下文和持久化消息数不变。

### 阶段 2：元数据加固（P1）

1. 为 compact done 增加 `schemaVersion`、`compactionId`、计数和原因。
2. 增加损坏、旧版本和未知版本兼容测试。
3. 增加窗口诊断字段。

验收：新旧会话都能恢复，边界不依赖文案，诊断能解释窗口选择原因。

### 阶段 3：存储分页（按数据触发，P2）

仅当 profile 证明全量 JSONL I/O/解析仍使首帧超预算时启动：

1. 设计反向游标或 side index；
2. 明确 `modelResumeState` 与 `renderPage` 分离；
3. 实现 `getConversationTail` / `getConversationPageBefore`；
4. 做 crash safety、旧文件和增量追加兼容测试。

验收：首帧不再随完整 transcript 大小线性退化，且模型续聊输入与阶段 1 前一致。

## 十五、实施改动清单

阶段 1 已落地：

- 新增 `apps/tui/src/conversation-render-window.ts`
- 新增 `apps/tui/src/conversation-render-window.test.ts`
- 修改 `apps/tui/src/app.tsx`：建立 projection、调整 `ChatHistory` 入参、渲染双向 banner、绑定会话重置
- 修改 `apps/tui/src/command-registry.ts` / `command-execution.ts`：加入 `/history earlier|later|latest` 及可发现别名
- 修改 `apps/tui/src/tui-language.ts`：补齐中英文命令文案
- 修改对应 command、language、experience、layout 测试

后续阶段：

- P1 可修改 `apps/tui/src/chat-controller.ts` / persistence compact metadata
- P2 才修改 `packages/conversation-store` 的读取契约

实施时代码仓当前存在用户未提交改动，必须基于当时工作树做最小编辑，不覆盖或回退无关内容。

## 十六、风险与取舍

### 16.1 首期仍全量读取

窗口投影能直接解决 UI 挂载和布局成本，但不能消除 JSONL 全量 I/O、解析与 controller 内存。选择分阶段是为了避免把 UI 性能修复错误地演变成 model resume 契约重构。是否下沉由 profile 决定。

### 16.2 压缩后尾部仍可能很大

“从最近压缩到末尾”是主要语义，但用户可能在一次压缩后继续很久。emergency guard 是防御机制，触发时必须明示，不能静默缺失。更长期应结合自动压缩阈值和单消息折叠。

### 16.3 UI 元数据承担边界语义

当前 `compact.phase` 足够首期使用，但长期应有版本化 `compactionId`。本方案禁止通过 system 文案识别，以降低本地化和文案调整风险。

### 16.4 连续全历史浏览仍不是主路径

双边有界页面保证连续翻页不会累积挂载量，但它不提供滚动条跨越上万条历史的连续空间感。只有当连续全历史浏览成为高频产品需求、有界翻页被证明显著阻碍用户，并且 OpenTUI 具备稳定的动态高度测量能力时，才重新评估虚拟滚动或独立历史查看器。

### 16.5 数量预算不等于布局预算

Markdown、工具详情的终端行数与字符数并非严格线性。双预算是低复杂度保护，性能夹具用于校准；若误差仍大，可追加“估算终端行”而不改变窗口契约。

## 十七、验收标准

功能验收：

- [ ] 最近一次有效压缩边界存在时，默认渲染该 done 消息及其后全部消息（除明确触发 emergency guard）。
- [ ] 多次压缩只采用最后一次有效 done，progress/失败记录不成为边界。
- [ ] 无压缩大会话使用消息数 + 估算字符数的尾部窗口兜底。
- [ ] 完整 transcript 仍持久化，模型续聊上下文未因 UI 窗口被裁剪。
- [ ] 用户可按有界页面双向浏览历史并回到 latest，连续翻页不累积挂载量，不存在“加载全部”入口。
- [ ] 流式更新不反复重置窗口；用户回看时新输出不强制抢滚动。
- [ ] 旧会话、损坏 compact 元数据和单条超大消息都有明确降级。

性能验收：

- [ ] 10k 消息场景的首屏挂载量符合窗口策略。
- [ ] 窗口选择纯函数 p95 ≤ 10 ms。
- [ ] 恢复到首个非空 history frame p95 ≤ 500 ms；若不满足，有 profile 证据决定是否进入 P2。
- [ ] 大会话恢复不出现长时间白屏或进程崩溃。
- [ ] 流式 delta 不导致隐藏历史的 Markdown/组件重建。

治理验收：

- [ ] 窗口策略有纯函数单测、交互测试、持久化兼容测试和性能夹具。
- [ ] 不从文案推断 compact 边界。
- [ ] 不把 projection 回写到 `ChatSnapshot.messages`。
- [ ] 不记录消息正文到性能遥测。

## 十八、最终决策

采用“语义边界 + 有界尾窗 + 双向有界回看”的 TUI 会话表达：

1. 正常路径从最近一次有效压缩完成消息开始渲染；
2. 无压缩时用双预算尾窗保证首屏；
3. 完整历史和模型上下文保持不变；
4. 历史使用双向有界页面，不引入虚拟滚动；
5. 先解决渲染白屏，再以性能数据决定是否下沉存储分页。

该方案把性能限制放在“界面负责表达”的边界内，同时保留“上下文连续性”和“持久化完整性”，可作为 TUI 实现与回归验收的直接依据。
