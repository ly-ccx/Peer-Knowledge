# 桌面端性能提升根治方案设计

> 创建时间：2026-07-18  
> 最后更新：2026-07-18  
> 状态：设计稿（本文件只定方案与验收，不直接改代码）  
> 关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）  
> 关联调查：`knowledge/experience/desktop-startup-init-slowness.md`  
> 关联代码仓调查副本：`docs/design/desktop-cold-start-brand-startup-loader.md`

---

## 0. 一句话目标

把 Peer Agent 桌面端从「启动/列表/内容混在一条重路径上」根治成：

**启动先可交互 → 列表只读轻 meta 且分页 → 内容按会话按需窗口加载 → 附属徽标异步增量**，  
并建立可回归的性能预算与自动化门禁。

---

## 1. 问题定义

### 1.1 用户可感知症状

| 阶段 | 现象 |
| --- | --- |
| 冷启动 | 长时间停在 `BrandStartupLoader` |
| 进入主界面后 | 左侧会话列表仍慢/空很久，再刷满 |
| 点开大会话 | 聊天区卡顿、内存飙升 |
| 日常切换 | focus/visibility 触发全量刷新，侧栏抖动 |

### 1.2 本机样本（2026-07-18）

| 指标 | 数值 |
| --- | --- |
| 会话 index 行数 | 239（全部 active） |
| 会话文件总大小 | ~586 MB |
| 单会话最大 | ~25.8 MB |
| index 中 `messageCount` 已回填比例（测量前） | **0 / 239**（全部缺失） |
| `listConversations({ includeMessageCount:false })` | **~6.4 ms** |
| 首次 `listConversations()`（缺 count 时回填） | **~1449 ms** |
| 回填后再 `listConversations()` | **~0.7 ms** |
| 回填后再 `listConversationsByWorkspace(peer-knowledge)` | **~0.6 ms / 149 条** |

结论：

1. **meta-only 列表本身可以很快**（毫秒级）。  
2. **第一次带 messageCount 的全量 list 仍会扫 ~580MB jsonl 做回填**，这是当前列表慢的最大实锤。  
3. 列表与内容 API 已分层，但**加载策略仍按「全量」组织**。

### 1.3 已落地（Phase-0 / 止血，2026-07-18）

以下已在 `peer_agent` 落地，**不能当作未做**：

| 项 | 状态 | 代码锚点 |
| --- | --- | --- |
| `messageCount` 写入 index；list 默认读 index | 已落地 | `packages/conversation-store` `ensureMessageCounts` |
| 缺 count 时批量回填 | 已落地（首次仍痛） | 同上 |
| `listByWorkspace` 先 meta 过滤 | 已落地 | `listConversationsByWorkspace` |
| `workspace:list` 跳过 messageCount | 已落地 | `main.mjs` `includeMessageCount: false` |
| bootstrap 成功即 `setSession` | 已落地 | `useDesktopBootstrap.ts` |
| `bootstrap:get` 不再同步 monorepo project index | 已落地 | `projects: []` |
| shell env snapshot 不阻塞 createWindow | 已落地 | `void createShellEnvSnapshot()` |

Phase-0 **解决了启动门闩与「每次 list 扫全文」**，但**没有解决**：

- 老数据首次回填仍扫全库  
- 列表无分页 / 无虚拟列表  
- 侧栏附属全量查询（GoalPlan 徽标等）  
- 内容路径一次读整会话 jsonl  
- 性能回归门禁与预算

---

## 2. 根因分层（不是单一 bug）

```text
L0 启动编排
  - 历史：session 门闩绑死预加载（Phase-0 已拆）
  - 残留：启动后仍立即全量 conversationsList + 附属查询

L1 存储与 list 契约
  - 历史：list 为 messageCount 读全文（Phase-0 已改为 index）
  - 残留：index 缺字段时同步回填仍在 list 热路径
  - 残留：list API 无 limit/cursor，契约即「全量」

L2 侧栏附属数据
  - goalPlansList({}) 全库聚合待批准数（渲染层）
  - 多会话 compaction 状态批量查询
  - focus/visibility/onConversationsChanged → 全量 refreshConversations

L3 内容路径
  - conversationsGet 一次 readJsonl 整文件（可达 20MB+）
  - 渲染层 map 全量 messages 进 React state

L4 观测缺失
  - 无启动/列表/打开会话的分阶段 timing 埋点
  - 无 CI/本地性能预算，回归靠体感
```

**根治原则：按层切断「全量同步」依赖，而不是继续在热路径上打补丁。**

---

## 3. 目标架构（目标态）

### 3.1 数据与加载分层

```text
┌─────────────────────────────────────────────────────────┐
│ Renderer                                                 │
│  Shell (可交互) ← session only                           │
│  Sidebar ← ConversationSummary[] (page, virtualized)     │
│  Badges  ← 增量/按可见窗口（非全量 GoalPlan）              │
│  Thread  ← MessageWindow (tail + older pages)            │
└──────────────▲──────────────────▲──────────────▲────────┘
               │                  │              │
     bootstrap:get        conversations:list  conversations:get
     (轻)                 (meta page)         (message window)
               │                  │              │
┌──────────────┴──────────────────┴──────────────┴────────┐
│ Main                                                      │
│  sessionStore / settings / llmProviders (轻)              │
│  conversation index (O(n meta), 无全文)                    │
│  conversation body store (按 id 窗口读)                    │
│  goal plan index (awaiting counts by conversationId)      │
└──────────────────────────────────────────────────────────┘
```

### 3.2 硬边界（契约级）

| 边界 | 允许 | 禁止 |
| --- | --- | --- |
| **List 路径** | 读 `index.jsonl` meta、分页、轻量 badge 字段 | 打开任意 `*.jsonl` 会话正文（含为 count 扫全文） |
| **Content 路径** | 按 conversationId 读窗口消息 | 为侧栏刷新触发正文读取 |
| **Badge 路径** | 读 goal-plan 索引 / 聚合表 | `goalPlansList({})` 拉全量 plan 对象到渲染层 |
| **Startup 路径** | session + 最小 locale/provider | 等全量 list / project git / shell snapshot |

### 3.3 首屏时序（目标）

```text
T0  app.whenReady
T1  createWindow（不等 shell snapshot）
T2  renderer 挂载 BrandStartupLoader
T3  bootstrap:get 返回 → setSession → 离开启动页（目标 < 300ms 数据路径）
T4  首屏侧栏：最近 N 条 summary（目标 < 100ms，index only）
T5  后台：messageCount 迁移、badge 增量、shell snapshot、project index 缓存
T6  用户点会话 → 仅加载该会话 tail 窗口
```

---

## 4. 分阶段根治方案

### Phase A — 存储与 list 热路径「永不读正文」（P0）

**目标**：任何 `listConversations*` 在稳态与迁移态都 **0 次** 打开会话 jsonl。

#### A1. 启动期异步迁移，移出 list 热路径

现状：`ensureMessageCounts` 在 list 时同步扫缺字段会话（本机首次 ~1.45s）。

目标设计：

1. **list 热路径**：  
   - 有 `messageCount` → 用 index 值  
   - 无 `messageCount` → 返回 `messageCount: null`（UI 显示 `—` 或隐藏条数），**不读 jsonl**
2. **后台迁移任务**（main 启动后 / idle）：  
   - 扫描 index 缺字段项，逐个或限流读 jsonl 回填  
   - 写回 index；广播 `conversations:changed`（轻量，可 debounce）  
3. **写路径继续维护 count**（已有）：create/append/replace

验收：

- 单元测试：污染 jsonl 后 `listConversations` 仍不抛错且不依赖正文  
- 性能：本机 239 条 list p95 **< 20ms**（index only，含缺 count）

#### A2. List API 分页 / 游标

扩展契约（示意）：

```ts
conversationsList({
  workspacePath?: string | null;
  status?: 'active' | 'archived' | ...;
  limit?: number;          // default 50
  cursor?: string;         // updatedAt+id
  includeMessageCount?: boolean; // default true, from index only
}): {
  items: ConversationSummary[];
  nextCursor: string | null;
}
```

规则：

- 默认 **limit=50**（侧栏首屏）  
- `startupSnapshot` 只拉第一页  
- `refreshConversations` 默认刷新第一页；滚动再加载更多  
- 搜索场景可走已有 `searchConversations`，同样禁止读正文

#### A3. ConversationSummary 字段最小化

侧栏真正需要：

- `id, title, updatedAt, createdAt, status, pinned*, workspacePath, messageCount?, mode?`

明确 **不进 list**：

- messages、usage 明细、segments、tool payloads

---

### Phase B — 侧栏加载策略与附属数据解耦（P0）

**目标**：进入主界面后「侧栏可滚动」与「徽标齐全」解耦。

#### B1. 启动预加载降级

`useDesktopBootstrap` 目标行为：

1. `setSession`（已做）  
2. **可选**：只预取 `conversationsList({ limit: 30 })`  
3. **不要**在启动路径等 `workspaceInfo` 的重 git（可骨架 + 后台）  
4. `startupSnapshot` 允许 partial：`conversations` 先有第一页即可

#### B2. Goal 待批准徽标：服务端聚合

现状：`useAwaitingGoalPlanCounts` → `goalPlansList({})` 全量。

目标：

```ts
goalPlansAwaitingCounts(): Record<conversationId, number>
// 或
conversationsList 可选 embed: { awaitingGoalCount?: number }
```

实现建议：

- goal-plan store 维护 `status=awaiting_approval` 的倒排索引 / 扫描 plan index（若 plan 本身已是轻 meta）  
- 禁止把完整 plan 图推到渲染层只为数字

#### B3. Compaction 状态

- 不要对列表每一项启动时批量 `compaction:get`  
- 仅对 **可见行** 或 **activeConversation** 查询  
- 或把 `compactionStage` 轻字段写入会话 index（写路径更新）

#### B4. 刷新风暴收敛

现状：`focus` / `visibilitychange` / `onConversationsChanged` 都 `refreshConversations()` 全量。

目标：

- `onConversationsChanged`：按 `conversationId` **补丁更新**单行，而非整表重拉  
- focus 刷新：debounce + 仅当离开超过阈值  
- 视图切换（active/archived）才整页重拉

#### B5. 虚拟列表

- Sidebar 使用虚拟滚动（只挂载可见 ~20 行 DOM）  
- 与分页配合：窗口接近底部再 `nextCursor`

---

### Phase C — 内容路径窗口化（P1）

**目标**：打开 20MB+ 会话时，首屏消息可交互 < 预算，内存可控。

#### C1. `conversationsGet` 窗口参数

```ts
conversationsGet({
  id: string;
  // 默认：尾部窗口
  tail?: number;          // default 80 messages
  before?: string;        // message id cursor for older
  includeMeta?: boolean;  // title/mode/effort/usage summary
})
```

存储实现：

- 短期：jsonl **反向读尾部**（不必全量 parse 进数组再 slice 的最优实现可迭代）  
- 中期：可选 sidecar `*.idx`（offset 表）加速随机访问  
- 长期：评估 sqlite（仅当 jsonl 窗口化仍不够）

#### C2. ChatSurface 加载策略

- 进入会话：只请求 tail  
- 上滚：加载 older page，拼接到顶部  
- 流式追加：只动 tail  
- 禁止默认 `messages.map` 全历史进重 UI（大段 tool 输出折叠/按需展开）

#### C3. 与 compaction 的关系

- 已有 `_compaction` 边界：UI 默认展示「压缩后尾部」即可  
- 窗口 API 可与 compaction 边界对齐（默认 from last compaction）

---

### Phase D — 启动与后台工作编排（P1）

在 Phase-0 基础上收尾：

| 工作 | 策略 |
| --- | --- |
| shell env snapshot | 已后台；增加成功/失败指标 |
| project index / git | 缓存 + TTL；workspace 切换时刷新；禁止 bootstrap 同步 |
| messageCount 迁移 | 后台队列，限流 CPU/IO |
| MCP probe | 保持按需，永不进冷启动 |
| Quick Chat prewarm | 保持后台，低优先级 |

编排原则：**任何后台任务不得阻塞 IPC list/get 的主响应路径**（可用独立队列 + 优先级）。

---

### Phase E — 可观测性与性能预算（P0，与实现并行）

没有预算就不叫根治。

#### E1. 分阶段 timing（main + renderer）

建议事件名：

- `perf.startup.main_ready`
- `perf.startup.window_created`
- `perf.startup.bootstrap_ms`
- `perf.startup.session_visible_ms`（离开 BrandStartupLoader）
- `perf.list.ms` + `count` + `workspace` + `limit`
- `perf.conversation_open.ms` + `messageBytes` + `messageCount`
- `perf.badge.goal_counts.ms`

开发态可打到 console / 本地 `perf-log.jsonl`；正式版可采样。

#### E2. 预算（建议初值，可按设备分级）

基于本机样本与产品预期：

| 指标 | 目标（开发机） | 说明 |
| --- | --- | --- |
| session 可见（bootstrap 数据路径） | < 300 ms | 不含首次 Electron 冷启动进程开销 |
| 侧栏第一页 list | < 50 ms | index only，≤50 条 |
| 老库首次迁移 | 后台，不挡 list | list 可先无 count |
| 打开会话 tail≤80 | < 150 ms | 排除超大单条 tool 输出极端值 |
| 全量 list（若仍暴露） | 禁止作为默认路径 | API 默认分页 |

#### E3. 自动化门禁

- 扩展 `conversation-store` 测试：list 路径 **mock/spy 禁止 readFile 会话正文**  
- 增加 fixture：1000 条 index meta 的 list 基准（CI 相对阈值）  
- 可选：本地 `scripts/bench-conversation-list.mjs` 输出 JSON，文档记录基线

---

## 5. 非目标（本根治方案不做）

- 重写整个存储为云端同步数据库（可另立 ADR）  
- 改变聊天产品信息架构（仅性能与加载策略）  
- 为了性能删除 messageCount / badge 能力（改为正确分层）  
- 一次 PR 塞进 A–E 全部（必须分阶段合入）

---

## 6. 实施顺序与依赖

```text
E(埋点基线) ──┬──► A1 迁移移出热路径 ──► A2 分页契约 ──► B1/B4 启动与刷新
              │                              │
              │                              └──► B2/B3 徽标/compaction
              │                              └──► B5 虚拟列表
              └──► C 内容窗口化（可与 B 并行，契约独立）
```

**推荐合入切片**：

1. **PR1**：A1 + E list 门禁测试（立刻消灭「首次进界面扫 580MB」）  
2. **PR2**：A2 + B1 + B4（第一页侧栏）  
3. **PR3**：B2 + B3（徽标解耦）  
4. **PR4**：B5 虚拟列表  
5. **PR5**：C 内容窗口化  
6. **PR6**：E 预算固化 + 文档基线

---

## 7. 风险与回退

| 风险 | 缓解 |
| --- | --- |
| UI 短暂无 messageCount | 显示占位；迁移完成后补丁更新 |
| 分页后搜索/多选假设全量 | 搜索走专用 API；明确「列表≠全集」 |
| 窗口化消息导致「找不到很早的消息」 | 上滚加载；提供 Jump to top / 搜索 |
| 老客户端契约 | IPC 新字段可选；默认兼容旧调用方一版 |
| 回填改写真实 index | 已发生在开发机：迁移必须幂等、可中断 |

---

## 8. 验收清单（Definition of Done）

### 8.1 设计完成（本文件）

- [x] 根因分层与已落地/未落地边界清晰  
- [x] 目标架构与契约硬边界  
- [x] 分阶段方案、顺序、风险、预算  

### 8.2 实现完成（后续 Goal 执行时勾选）

- [ ] list 热路径 0 读会话正文（测试锁死）  
- [ ] 默认 list 分页；侧栏首屏只用第一页  
- [ ] Goal 徽标不再 `goalPlansList({})` 全量  
- [ ] 打开大会话默认 tail 窗口  
- [ ] 埋点可输出启动/列表/打开会话耗时  
- [ ] 本机样本：回填后 list < 20ms；缺 count 时 list 不再出现秒级卡顿  

### 8.3 成功标准（可机器核对的设计产物）

| ID | 检查 |
| --- | --- |
| D1 | 本文存在且含「Phase A–E」 |
| D2 | 本文含本机实测数字（list 6.4ms / 首次回填 ~1.45s / 回填后 ~0.7ms） |
| D3 | 本文明确 Phase-0 已落地项与残留项 |
| D4 | 本文含契约硬边界表（List/Content/Badge/Startup） |

---

## 9. 与「列表和内容为什么不是分开的」之关系

API 层已经分开：

- List：`conversationsList` → meta  
- Content：`conversationsGet` → messages  

体感未分开的原因是 **策略层**：

1. 列表默认全量  
2. 列表曾/仍（迁移时）碰正文  
3. 列表刷新绑定全量附属查询  
4. 内容一次吞整文件  

本方案根治的是 **策略与契约默认值**，而不是再发明一套并行 API。

---

## 10. 建议的下一执行 Goal 标题

> **落地性能根治 Phase A+B（list 零读正文 + 分页 + 徽标解耦）**

范围：PR1–PR3；不含内容窗口化（C）可作第二个 Goal。

---

## 11. 证据索引

| 证据 | 含义 |
| --- | --- |
| 本机 index=239 / ~586MB / max~25.8MB | 重度用户规模 |
| `includeMessageCount:false` ~6.4ms | meta-only 可行 |
| 首次带 count list ~1449ms | 迁移仍在热路径 |
| 二次 list ~0.7ms | index 命中后已足够快 |
| Phase-0 代码锚点 | 门闩/shell/projects/count 已止血 |
| `goalPlansList({})` | 徽标全量问题仍在 |
| `loadConversationMessages` → `conversationsGet` 全量 messages | 内容路径窗口化必要 |

---

**设计结论**：根治不是继续「让全量更快」，而是 **禁止默认全量**——list 只读 index 且分页，迁移与徽标后台化，内容按窗口加载，并用预算与测试锁死回归。
