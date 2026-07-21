# 消息排队差距研究：Peer Agent vs Codex

创建时间：2026-07-21  
最后更新：2026-07-21  
状态：研究结论（不改代码）  
范围：对照 Codex 运行中排队 / Steer / 编辑 / 关排队；摸清 Peer 现状与缺口

> 说明：本 Goal 的写边界落在代码仓 `peer_agent`。同步副本建议放到知识库  
> `peer-knowledge/design/product/message-queue-gap-vs-codex.md`。

## 1. 结论摘要

Peer Desktop **已经有一版可用的 follow-up 排队**：运行中/压缩中再发会入队，空闲后自动出队发送，并有队列卡片、拖拽排序、移除、跨会话草稿持久化。

相对 Codex，真正差的不是“有没有队列”，而是：

1. **没有 Steer（回合中途注入）**：只能等本轮结束后 FIFO 发下一条。
2. **没有关排队 / 强制立即发送**：运行中无法选择“打断当前回合立刻发”。
3. **编辑体验半成品**：有 Edit 按钮与 `updateQueuedMessage`，但 UI 是“回填 composer 且不移出队列”，容易重复发送。
4. **能力只在 Desktop renderer**：TUI 无对等队列；runtime/protocol 无排队契约。

优先级建议：**先修 Edit 语义与关排队开关 → 再补 Steer 最小闭环 → 最后考虑 TUI/协议下沉**。

## 2. Peer 现状（证据）

### 2.1 行为链路

```text
用户发送
  → handleSend 读取 draft / attachments
  → 若 isStreaming || isCompactionActive
       → enqueueMessage({ id, text, attachments, effort })
       → 清空 draft / attachments
  → 否则 submitMessage(...)
       → chatSend（真正落会话消息并发起回合）

空闲时 useEffect
  → 非 streaming、非 compaction、无 resumeTask、队列非空
  → shiftQueuedMessage()
  → submitMessage(head)
```

关键位置：

| 能力 | 位置 | 说明 |
| --- | --- | --- |
| 运行中入队 | `apps/desktop/renderer/src/chat/components/ChatSurface.tsx` `handleSend` | 注释明确写了“类似 Codex 队列” |
| 自动出队 | 同文件 dequeue `useEffect` | 空闲后复用 `submitMessage` |
| 队列状态 | `conversationStore.messageQueue` | 按 `conversationId` 分桶 |
| 队列 UI | `MessageQueue.tsx` | 序号、拖拽重排、Edit、移除 |
| 发送按钮文案 | `ComposerDraftControls.tsx` | busy 时显示「加入队列 / Add to queue」 |
| 持久化 | `composerPersistence.ts` → `settings.composerDrafts` | draft + queue，不是会话消息真值 |

### 2.2 落库边界（重要）

- **排队项不是会话消息真值**。`composerPersistence` 注释写明：队列是“待发意图缓冲”，真正发送仍走 `submitMessage → chatSend`。
- 持久化落在 `~/.peer-agent/settings.json` 的 `composerDrafts[conversationId].queue`。
- 出队并 `chatSend` 之后，才进入会话历史 / 消息 store。
- 因此：重启后可恢复未发送队列；但队列与 transcript 是两条线。

### 2.3 已有 / 没有

| 能力 | Peer Desktop | 备注 |
| --- | --- | --- |
| 运行中再发 → 入队 | 有 | streaming 或 compaction 中 |
| 空闲自动出队 | 有 | resumeTask 优先，避免抢续传窗口 |
| 队列卡片 UI | 有 | 输入框上方 |
| 拖拽重排 | 有 | DnD |
| 移除 | 有 | × |
| 编辑 | 半有 | Edit 回填 composer，**不移出队列**；store 有 `updateQueuedMessage` 但 UI 未用 |
| 关排队开关 | 无 | 无 `queueEnabled` / Turn off queue |
| Steer / 中途注入 | 无 | 只有回合结束后 follow-up |
| 打断后立即发送队列项 | 无 | 只能等当前回合自然结束或用户 Stop 后再出队 |
| 附件随队 | 有 | `QueuedMessage.attachments` + effort |
| 运行中继续输入 | 有 | composer 可输入；附件按钮 streaming 时 disabled |
| TUI 队列 | 无 | 未发现对等 `messageQueue` |
| protocol / runtime 队列契约 | 无 | 仅 renderer 表达层状态 |

### 2.4 编辑语义细节（当前缺陷）

`refillQueuedMessageToComposer` 注释：

> 点编辑回填输入框：文案/附件回到 composer，**不从队列移除（只有 × 才移除）**。

影响：

- 用户点 Edit 后若直接再发，可能 **队列原项仍在 + 又新入一条**，或空闲后原项自动发出导致“发了两遍”。
- 与 Codex「从队列弹出回 composer 再改」的预期不一致。

## 3. Codex 模型（还原）

对照来源：

- 用户截图：运行中队列卡片，带 **Edit** / **Turn off queue**。
- Codex 开源 TUI：`chat_composer.rs`、`pending_input_preview.rs`、`footer.rs`。
- 公开 issue：Desktop 存在 local **queued-message card**，并可能因 turn 状态卡住无法出队（#34026）。

### 3.1 提交结果二分

Composer 提交不是单一路径，而是：

```text
InputResult::Submitted { text, elements }
InputResult::Queued { text, elements, action: QueuedInputAction }
```

`QueuedInputAction` 至少区分普通排队与 shell 类动作（如 `Plain` / `RunShell`）。

### 3.2 何时入队

- 任务运行中提交 → 进入排队路径。
- 另有 `queue_submissions` 开关：即使不在运行，也可强制走 queue（对应 UI「关排队 / 开排队」一类控制）。
- TUI：`Tab` 在任务运行中请求排队；无任务时 Tab 与 Enter 一样提交，避免输入丢失。

### 3.3 三层 pending 输入（比 Peer 多两层）

`PendingInputPreview` 明确渲染三类：

1. **pending steers**：回合进行中的“纠偏/追加指令”，计划在**下一个 tool/result 边界**注入；可用 interrupt 快捷键立刻打断并发送。
2. **rejected steers**：被拒绝/未接受的 steers，回合结束后再提交。
3. **queued messages**：普通 follow-up，等当前 turn 结束后再发。

这与 Peer 单一 FIFO `messageQueue` 不同：Codex 把“中途 steer”和“回合后 follow-up”拆开。

### 3.4 编辑

- TUI：可配置绑定（默认 **Alt+Up**）把 **queued user inputs** 弹回 composer 编辑。
- Desktop 截图：队列卡片上有 **Edit**。
- 语义是“从队列取出再改”，不是“复制一份到输入框但队列还留着”。

### 3.5 关排队

- Desktop 截图明确有 **Turn off queue**。
- TUI 有 `set_queue_submissions(bool)` 与 footer queue hint。
- 产品意图：用户可关闭“后续输入继续堆队列”的模式，回到更直接的发送/打断语义。

### 3.6 Codex 能力清单（对照表左侧）

| 能力 | Codex |
| --- | --- |
| 运行中 follow-up 排队 | 有 |
| 队列卡片 / preview | 有（Desktop card / TUI preview） |
| 编辑队列项 | 有（弹出回 composer） |
| 关排队 | 有 |
| Steer（tool 边界注入） | 有 |
| Esc/interrupt 立即发送 steer | 有 |
| rejected steers 回合后重提 | 有 |
| 强制 queue 模式（非 running 也可 queue） | 有（`queue_submissions`） |
| 队列与 turn 状态耦合风险 | 有（公开 bug：stale thinking 导致只 queue 不发） |

## 4. 差距清单

### 4.1 产品 / 交互

| ID | 差距 | 严重度 | 说明 |
| --- | --- | --- | --- |
| G1 | 无 Steer | **P0** | 运行中只能“等这轮结束再说”，不能在 tool 边界注入纠偏 |
| G2 | 无 Turn off queue / 强制立即发送 | **P0** | 用户无法选择“不要排队，打断并发” |
| G3 | Edit 语义错误/半成品 | **P0** | 回填不移出；`updateQueuedMessage` 未接入 UI |
| G4 | 队列类型单一 | P1 | 无 pending/rejected steer 分层 |
| G5 | 运行中附件入口关闭 | P2 | attach 按钮 `disabled={... \|\| isStreaming}`，体验弱于“整包入队” |
| G6 | 缺少队列快捷键/footer 提示 | P2 | Codex 有 queue hint / Alt+Up 等 |

### 4.2 Runtime / 协议

| ID | 差距 | 严重度 | 说明 |
| --- | --- | --- | --- |
| G7 | 队列仅 renderer | **P1** | 不在 protocol / runtime-core；多端不一致 |
| G8 | TUI 无队列 | **P1** | Desktop 学了 Codex 一半，TUI 仍是“运行中难再发” |
| G9 | 无“中途注入”执行缝 | **P0/P1** | 即使 UI 做 Steer，也缺 turn 边界注入与 Evidence 路径 |
| G10 | 出队与 turn 状态耦合脆弱 | P1 | Peer 用 `isStreaming/isCompaction/resumeTask` 门闸；Codex 也有 stale turn 卡死先例，需防“永远出不了队” |

### 4.3 数据 / 落库

| ID | 差距 | 严重度 | 说明 |
| --- | --- | --- | --- |
| G11 | 队列不在 conversation store | P2 | 只在 settings drafts；合理（待发意图），但跨端/CLI 难共享 |
| G12 | 无队列项状态机 | P2 | 缺 `queued / editing / cancelled / submitting` 显式状态 |

### 4.4 已对齐（不必重复造）

- 运行中可继续输入并入队
- 空闲自动出队
- 队列 UI + 重排 + 移除
- 队列项可带 attachments / effort
- 按会话隔离 + 草稿级持久化
- 发送主路径单一（出队仍走 `submitMessage`）

## 5. 可落地建议

### Phase 0 — 低成本修齐 Desktop 队列体验（C/B 级）

目标：先把“follow-up 队列”做到不迷惑。

1. **修正 Edit 语义**  
   - 推荐：Edit = 从队列 remove + 填入 composer（对齐 Codex pop-to-edit）。  
   - 或：就地 `updateQueuedMessage` 内联编辑。  
   - 不要继续“复制回填且留在队列”。
2. **补关排队开关**  
   - 会话级或全局 `queueEnabled`。  
   - Off + 运行中发送：明确策略二选一  
     - A. Stop 当前 turn 再立即发送（更接近“强制发送”）  
     - B. 拒绝入队并提示“先停止或开启排队”
3. **busy 态主按钮语义**  
   - 有 draft：加入队列 / 或按开关显示“停止并发送”。  
   - 无 draft：Stop。
4. **防卡死**  
   - streaming 假死时允许用户 Stop 后强制 drain；给队列“卡住”可观测状态。

验收：

- 运行中连发 3 条 → 卡片 3 条 → 结束后按序发送一次。
- Edit 后不会双发。
- 关排队后行为符合所选策略。

### Phase 1 — Steer 最小闭环（B/A 级）

目标：补上 Codex 最有价值的差异点。

1. 区分 `followup` 与 `steer` 两种排队项。
2. runtime 在 **tool/result 边界** 消费 steer（不是等整轮 assistant done）。
3. UI：steer 卡片文案区分“将在下一工具边界注入 / 可立即打断发送”。
4. 权限与 Evidence：steer 注入必须走既有 chat/runtime 链，不能靠 prompt 拼接旁路。

验收：

- 长工具循环中发 steer → 下一边界生效，无需等整轮结束。
- Stop/interrupt 可选择“立刻带 steer 重入”。

### Phase 2 — 多端一致与协议化（A 级）

1. 若 Desktop/TUI/CLI 都要队列，再把队列状态升到 protocol 或 session runtime projection。  
2. 仍保持：队列是意图缓冲，transcript 才是消息真值。  
3. TUI 先做最小：运行中 Enter 入队 + 列表 + 删除 + 自动出队。

> 注意：按治理基线，队列若影响 capability / 发送契约 / Evidence，需要 A 级设计，不要只在 React 里继续堆。

## 6. 不建议做的事

1. **不要**把未发送队列写进 conversation messages 当真历史（会污染 transcript / 重放）。  
2. **不要**为了学 Codex 再开一条旁路 send（必须仍走 `submitMessage/chatSend` 或等价 runtime 投影）。  
3. **不要**只加“Steer”文案而不做 turn 边界注入（那只是换皮 follow-up）。  
4. **不要**在未修 Edit 语义前扩 TUI 队列（会复制半成品）。

## 7. 建议决策

若资源有限，按这个顺序：

1. **P0**：Edit 语义 + 关排队/停止并发送策略  
2. **P0/P1**：Steer 是否要做（产品确认：Agent 长任务纠偏是否刚需）  
3. **P1**：TUI 对齐  
4. **P2**：快捷键、footer hint、附件 busy 态、状态机细化

一句话：

> Peer 已经“会排队发下一条”；Codex 更强在“排队可编辑可关闭，且能在回合中途 Steer”。先把前者做对，再决定要不要上真正的 Steer。

## 8. 证据索引

- Peer：`ChatSurface.tsx` handleSend / dequeue effect / MessageQueue 挂载  
- Peer：`conversationStore.ts` enqueue/update/remove/reorder/shift  
- Peer：`composerPersistence.ts` settings drafts 边界说明  
- Peer：`ComposerDraftControls.tsx` busy 文案「加入队列」  
- Codex：`pending_input_preview.rs` steers / rejected / queued 三层  
- Codex：`chat_composer.rs` `InputResult::Queued`、`queue_submissions`、`set_queue_submissions`  
- Codex Desktop：用户截图 Edit / Turn off queue；issue #34026 local queued-message card  
