# 多任务并行导致工作台与会话 Drawer 卡顿：完整诊断与修复方案

> 代码仓库：`/Users/liangyin/Documents/DEV/github/peer_agent`  
> 知识仓库：`/Users/liangyin/Documents/MiaoYan/peer-knowledge`  
> 日期：2026-08-11  
> 最后更新：2026-08-14（待验收改回首页全量展示，见文末「15」）  
> 影响范围：Desktop main TaskOverview 投影、GoalPlan store、renderer 工作台/会话 Drawer、聊天滚动热路径、search_files 主进程 IO

## 0. 2026-08-13 Trace 跟进

Chrome Trace `Trace-20260813T162505.json.gz`（约 21s）确认卡顿在 **Electron 主进程 CrBrowserMain**，不是 renderer：

| 证据 | 数值 |
| --- | --- |
| 主进程 `RunTask` | 4 次 ≥2.0s（最长 2721ms），间隔符合 queued reload |
| `readFileUtf8` + `readFileSync` 自时间 | 约 10.5s / 18s 采样窗 |
| `runFileSearch` / `spawn` | 同步扫盘 + 子进程 |
| Renderer | 几乎全是 idle；React 侧 InboxRow 有引用抖动，但不是 2.7s 冻结的主因 |

落地修复（`peer_agent`）：

1. **总工作台 `listTaskOverview()`** 不再调用无筛选的 `listPlanDetails()`。先用 index meta 的 `isGoalPlanMetaCandidate` 丢掉已验收/祖父化 completed 与 cancelled/failed，再 hydrate。
2. **`search_files`** 优先异步 `rg`；否则 `fs.promises` 分片扫描并 `setImmediate` 让出事件循环，避免主进程 `readFileSync` 扫到 5000 个文件。

800 条夹具（795 completed + 5 executing）：全量 hydrate 约 24ms（内存盘小文件）；筛选后全局 overview 约 1.2–2.3ms，只返回 5 条。真实磁盘上千个大 JSON 时，前者会放大到数百毫秒～数秒。

---

## 1. 摘要

多任务并行时，未打开任务的 runner progress 会高频广播 `taskOverview:changed`。工作台和会话 Drawer 各自订阅广播并重新调用 `taskOverview:list`；聚合器在筛选前调用 `goalPlanStore.listPlanDetails()`，同步水合全部历史 GoalPlan。当前用户数据包含约 2577 个计划，其中约 2493 个已经完成，但仍参与每次热路径水合。

在真实数据上的只读基准：

| 路径 | 返回量 | 耗时 |
| --- | ---: | ---: |
| `goalPlanStore.listPlanDetails()` | 2576+ | 平均约 281ms，冷样本最高约 584ms |
| 全局 TaskOverview | 111 条 | 平均约 256ms |
| 会话 Drawer 的工作区查询 | 200 条 | 平均约 307.63ms |
| 两次顺序 Drawer 查询 | 400 条 | 约 639.48ms |
| 会话列表 | 655 条 | 平均约 3.66ms |

runner progress 的通知窗口是每个计划 100ms。事件生产速度高于单次全量投影的消费速度，hook 又会在 in-flight 期间记录 queued reload，形成连续无空闲重拉。打开 Drawer 后，底层工作台与 Drawer 内 `ChatSurface` 同时存在，重复消费同一事实。主进程长任务、IPC 新数组、React 更新、流式 Markdown、虚拟列表动态测高和滚动布局读取叠加，最终让滚动与输入事件一起饥饿。

## 2. 用户可感知现象

1. 没有其他任务执行时，工作台和会话基本流畅。
2. 多个任务并行后，工作台滚动明显掉帧。
3. 从工作台打开侧边栏会话 Drawer 后，上下滚动严重卡顿，输入字符也延迟出现。
4. 未打开任务越多、runner progress 越频繁，卡顿越明显。
5. 任务停止后卡顿快速缓解，说明运行中任务是触发器，而非静态 CSS 或单个长会话独立问题。

## 3. 系统语言重写

### 3.1 问题

多任务事件通过全局广播驱动昂贵的全量投影重建；投影消费者没有按可见性、工作区和会话收敛，导致 main 进程同步长任务与 renderer 更新持续占用事件循环。

### 3.2 约束

- main 进程继续拥有 TaskOverview 行动权投影的唯一事实来源。
- renderer 不自行从 GoalPlan 状态推断行动权。
- 不删除用户历史数据，不降低任务并行能力。
- 不用关闭动画、减少功能、隐藏内容或单纯拉长轮询掩盖问题。
- 保留创建、批准、拒绝、完成、失败、取消、验收、runner progress 等状态语义。
- 保留 structured cancellation、denial、timeout、failure 与 Evidence 路径。

### 3.3 source of truth

修复后仍由 main TaskOverview projection 作为 UI 状态事实源，但查询必须以轻量 GoalPlan 元数据索引为候选集，只水合与查询相关的计划；当前会话使用受治理的单项投影查询，而不是 renderer 侧推断。

## 4. 根因链

### 4.1 主因：筛选前水合全部 GoalPlan

`task-overview-aggregator.mjs` 先调用 `goalPlanStore.listPlanDetails()`，再按 workspace、terminal、active window、limit 等条件过滤。`listPlanDetails()` 从全部元数据出发读取完整计划文件，成本与历史计划总量线性相关。

当前 2577 个计划中仅约 46 个非终态，但 2493 个 completed 计划仍在每次变化后重新读取。一个计划的轻量 progress 变化被放大为数千文件/对象的同步水合与投影。

### 4.2 主因：按计划合并的高频 progress 驱动全局重拉

GoalPlan runner progress：

- 持久化窗口：300ms；
- 通知窗口：100ms；
- 合并粒度：单 plan。

多个计划并行时，总通知频率随任务数增长。main 对变化广播 `goalPlans:changed` 与 `taskOverview:changed`，renderer 的 `useTaskOverview` 收到后重拉完整列表。

### 4.3 主因：Drawer 查询范围远大于需求

`ChatSurface` 只需要当前 `conversationId` 对应的一条 `TaskOverviewItem`，却调用工作区级 `useTaskOverview({ includeTerminal: true, activeWithinMs: 0 })`，返回最多 200 条后再本地查找。

这条路径实测平均约 307.63ms，说明当前会话徽标/操作区付出了整个工作区投影成本。

### 4.4 放大器：底页与 Drawer 重复消费

工作台打开会话 Drawer 时，底层页面保留挂载；Drawer 新挂载 `ChatSurface`。两者拥有独立 hook、独立订阅和独立 IPC 请求。同一广播可触发两次顺序聚合，实测约 639.48ms。

`isPageActive` 已用于部分聊天行为，但没有成为所有昂贵查询与轮询的统一门闩。

### 4.5 放大器：无内容稳定性

`useTaskOverview` 每次响应直接 `setItems(result)`。即使投影内容没有变化，新数组也会触发消费者更新。in-flight 去重只防并发，不防持续排队：请求期间收到变化后，完成即再次 reload。

### 4.6 放大器：聊天滚动布局扫描

聊天列表已有虚拟化、frame coalescing 和 memo，草稿也已叶子化并 300ms debounce；因此输入框不是根因。但滚动帧仍可能重复查找 turn DOM 并逐个调用 `getBoundingClientRect()`，同时动态高度列表用 `ResizeObserver` 测量和补偿。流式内容持续增长时，布局读取与高度修正会放大已被 TaskOverview 占用的 renderer 主线程。

## 5. 已证伪或降级的解释

- CSS 动画、毛玻璃不是首因：纯 Node 基准中投影本身已达 250–380ms。
- 不是所有历史会话同时挂载：流式路由为应用级单例，普通聊天页面条件挂载。
- 不是完全没有虚拟化：复杂度超过阈值会进入虚拟列表。
- 不是每次按键重渲染整棵消息树：draft selector 已下沉；输入延迟是 renderer 长任务饥饿的表现。
- 未发现明确 IPC listener 泄漏：订阅提供 unsubscribe/removeListener。

## 6. 修复设计

### 6.1 GoalPlan 候选查询

在 GoalPlan store 提供或复用轻量查询能力：

1. 从 plan index/meta 获取候选，不先读取全部完整计划。
2. 优先按 conversationId、workspacePath、状态和更新时间限制候选。
3. 对候选执行 hydrate；无法由旧索引判断的 legacy meta 才回退读取，并回填索引。
4. terminal 计划仍要保留“待验收/需用户处理”语义，不能简单删除 completed。

接口应当增加 Locality：TaskOverview 只知道“列出相关计划”，不复制 GoalPlan store 索引判断。

### 6.2 当前会话单项投影

扩展 `taskOverview:list` 查询契约支持 `conversationId`（或提供语义等价的单项查询）。main 聚合器使用 `listPlanDetailsByConversation`，并结合该会话的 conversation/shell/automation 候选，返回 0～少量受治理投影。

`ChatSurface` 改为按当前 `conversationId` 查询，renderer 仍只消费 main 投影结果。

### 6.3 广播与刷新收敛

- `useTaskOverview` 根据 payload scope 判断是否相关；runner progress 带 `planId`/workspace/conversation 时只唤醒相关查询。
- 页面不可见时停止定时轮询和广播重拉；重新可见时执行一次同步。
- Drawer 打开时底层工作台暂停刷新，或共享同一个 query cache；本次优先最小可验证的可见性门闩。
- 对结果做稳定比较；投影无变化时保留原引用，不提交 React 更新。
- shell task 更新不再通过每 4 秒重建全部 GoalPlan 来保鲜；若短期不能加 changed 事件，轮询必须受页面可见性约束。

### 6.4 聊天滚动热路径

- 同一 rAF 内只计算一次 current turn，结果同时供 sticky context 与 scroll snapshot 使用。
- 优先使用 `elementFromPoint().closest('[data-chat-turn-id]')` 或虚拟范围/offset 数据，禁止全量 `querySelectorAll + getBoundingClientRect`。
- 同值状态更新短路。
- 保持“几何进 ref，窗口进 state”；ResizeObserver 的 scrollTop 修正继续合并到 rAF。

## 7. 测试策略

### 7.1 main 回归测试

- 构造大量无关 terminal GoalPlan，查询单个 conversation/workspace，断言不会调用全量 `listPlanDetails()`。
- conversationId 查询只返回相关投影，并保持 action/state/status 语义。
- legacy meta 无索引时能回退并正确输出。
- runner progress 变化不会使无关查询重建。

### 7.2 renderer 回归测试

- `ChatSurface` 将 conversationId 传给 TaskOverview 查询。
- Drawer 打开时底层工作台的昂贵刷新被禁用；关闭后只恢复一次。
- 相同投影结果不触发 state replacement。
- disabled/hidden hook 不轮询，不响应广播。
- current turn 每滚动帧只探测一次，不出现全量 DOM scan。

### 7.3 自动化命令

```bash
pnpm --filter @peer-agent/desktop test
pnpm --filter @peer-agent/desktop typecheck
pnpm --filter @peer-agent/desktop build
```

并运行新增的定向性能/契约测试。

## 8. 性能验收

使用至少“2500 个 terminal + 50 个活跃计划”的夹具：

1. 当前会话 TaskOverview 查询耗时不随无关历史计划数量线性增长。
2. 当前会话查询不调用全量 `listPlanDetails()`。
3. 相同 projection 不产生 renderer state commit。
4. Drawer 打开时，底层工作台不发起重复请求。
5. 8 个并行计划持续 runner progress 时，查询不会形成永不空闲的 queued reload。
6. dev 模式中工作台可连续滚动；打开 Drawer 后会话可连续上下滚动并持续输入。

建议目标：候选受限后的 TaskOverview 热查询 p95 小于 20～30ms；若受机器磁盘影响，至少必须从 O(全部历史计划) 降为 O(相关候选计划)。

## 9. 发布与回滚

- 改动保持 IPC 参数向后兼容；旧调用不传 conversationId 时语义不变。
- 候选查询保留 legacy index fallback，避免旧数据不可见。
- 若单项查询出现语义偏差，可暂时回退到 workspace 查询，但不得删除 main 行动权投影。
- 不迁移或删除用户数据；索引回填是幂等优化。

## 10. Definition of Done

- 完整文档落库。
- main 不再为相关范围查询水合全部 GoalPlan。
- ChatSurface 使用当前会话范围的受治理投影。
- hidden workbench/Drawer 不重复刷新。
- 聊天滚动无重复全量布局扫描。
- desktop test、typecheck、build 全部通过。
- dev 中并行任务运行时完成工作台、Drawer 滚动和输入实测，最后交给用户验收。

## 12. 2026-08-14 trace 实测：300ms 自激循环实锤

样本：`Trace-20260814T143010.json.gz`（7.2s 窗口，dev 模式，2802 个 goal plan）。

### 12.1 量化事实

| 指标 | 数值 |
| --- | --- |
| Browser（Electron main）CrBrowserMain RunTask 总负载 | 6048ms / 7209ms（**84%**） |
| Renderer CrRendererMain 总负载 | 1943ms（27%） |
| Browser 长任务（>100ms） | 22 个，间隔 p50=**305ms**，时长 146-216ms |
| Renderer TimerFire | 25 次，间隔 p50=**302ms** |
| `activeMeta`（goal-plan-store listPlans 内联过滤）self time | **4711ms** |
| `spawn`（child_process）self time | 4095ms |
| `evidence-index.jsonl` 规模 | **302MB / 50.7 万行** |
| `index.jsonl` | 1.2MB / 2802 行 |
| `.changes.jsonl` | 4.9 万行 |
| `performWorkUntilDeadline`（React 渲染调度） | 7.2s 内 186 次（≈39ms/次） |

### 12.2 循环闭环（trace 证据 + 代码对齐）

```
外部 runner 持续写 plan（活跃任务多）
  → .changes.jsonl 追加 → fs.watch 触发 subscribeChanges
  → main.mjs:377 广播 taskOverview:changed + conversations:changed（main.mjs:386 trayController.scheduleRefresh）
  → renderer：App.tsx onConversationsChanged → refreshConversations（120ms debounce，App.tsx:351 附近）
             useTaskOverview.onTaskOverviewChanged → reload()（无 scope 过滤、无可见性门闩）
  → renderer IPC 全量查询回 main
  → main 聚合器走 listPlans() 全量路径：readIndex() 同步读 1.2MB JSONL
     + 2802 次 normalizePlan + activeMeta 过滤（activeMeta self 4711ms）
     + evidence/index 相关同步 IO（existsSync 140ms、readFileSync 126ms、readdir 92ms）
  → 聚合响应返回 renderer → setState → React 186 次渲染调度
  → 本进程写入 → 又触发 .changes.jsonl watcher → 循环重复（周期 ~300ms）
```

关键代码锚点：
- `packages/runtime-node/src/goal-plan-store.mjs`：`listPlans() = readIndex().map(normalizePlan).filter(activeMeta)`（dist 产物 1960 行即 activeMeta）。
- `apps/desktop/renderer/src/app/hooks/useTaskOverview.ts`：`onTaskOverviewChanged(() => reload())` 无 payload 过滤；4s 轮询无 `document.hidden` 门闩。
- `apps/desktop/electron/main/main.mjs:377/386/392/421`：conversations/automations/goalPlans 变更 → fan-out 广播 + tray refresh。
- `apps/desktop/electron/main/tray-controller.mjs:276`（scheduleRefresh 120ms debounce → buildMenu → listRecentConversations）在 trace 中 self 728ms。

### 12.3 与既有修复方案的对齐（截至 2026-08-14 源码）

- 6.1 候选过滤（`isGoalPlanMetaCandidate`）✅ 已落地（aggregator.mjs:685/833）。
- 6.2 conversationId 单项查询（`listPlanDetailsByConversation`）✅ 已落地（aggregator.mjs:836-838）。
- 6.3 广播收敛（scope 过滤 + 可见性门闩 + tray 按需刷新）❌ **未落地** —— trace 中每 300ms 全量 reload 仍在发生。
- 6.4 聊天滚动（本次 trace 未覆盖，不判定）。

### 12.4 结论

卡顿主因不在 React 组件树，而在 main 进程：任务量大（2802 plans / 302MB evidence index）时，广播驱动的全量 `listPlans()` 同步重算形成 ~300ms 周期的自激循环，主进程 CPU 占用 84%，IPC 响应变慢，renderer 端表现为连续 React 渲染调度与输入/滚动掉帧。上一轮 6.1/6.2 已削减单次成本，但 6.3 广播收敛缺失导致**触发频率**未被治理——这是当前主要剩余根因。

修复优先级（按 ROI）：
1. main 广播节流：conversations/automations/goalPlans → taskOverview:changed fan-out 合并 + 最小间隔（如 2s），payload 带 planId/conversationId scope。
2. `useTaskOverview`：按 payload scope 判断相关性；`document.hidden` 时暂停广播重拉与 4s 轮询，恢复可见时同步一次。
3. tray `scheduleRefresh` 仅在菜单实际打开或最近会话列表可能变化时刷新（当前每次 conversations:changed 都重建菜单）。
4. `listPlans()` 增量缓存：index.jsonl mtime 未变时复用上次 normalize 结果（消除 activeMeta 4711ms 重复计算）。
5. `evidence-index.jsonl` 302MB 单文件增长无界：评估滚动/归档策略（独立工单，非卡顿直接根因但会持续恶化）。

## 13. 2026-08-14 修复落地与实测验证

按 §12.4 优先级完成四项修复，全部通过单测 + 全量回归 + 隔离环境 dev 实测。

### 13.1 改动清单（peer_agent 仓）

| # | 文件 | 改动 |
| --- | --- | --- |
| 1 | `apps/desktop/electron/main/task-overview-broadcast.mjs`（新建） | taskOverview:changed 节流调度器：最小间隔 2s 合并 fan-out；payload 携带合并 scope（reasons + planIds/conversationIds，超 8 个退化为全量 `scoped:false`）；trailing 保证不丢通知；flush/dispose 生命周期 |
| 2 | `apps/desktop/electron/main/main.mjs` | 三个广播点（conversations/automations/goalPlans）全部接入调度器；dispose 挂入 composition root |
| 3 | `apps/desktop/renderer/src/app/hooks/useTaskOverview.ts` | ① `isRelevantTaskOverviewChange`：scoped payload 与 conversationId 无交集时跳过重拉（旧 payload 保守兼容）② `document.hidden` 门闩：广播只置位 pending、4s 轮询不安装 ③ `visibilitychange` 恢复立即同步一次 |
| 4 | `apps/desktop/electron/main/tray-controller.mjs` | `scheduleRefresh` 默认 120ms→2s 退避，已有排队刷新时不提前不重置；点击/右键仍即时 `refresh()` |
| 5 | `packages/runtime-node/src/goal-plan-store.mjs` | `readJsonlCached`（mtimeMs+size 键控）：`readIndex` 命中时跳过 readFileSync+JSON.parse×2802，返回浅拷贝防调用方 sort 污染；写路径 mtime 变化自动失效 |

新增单测：`task-overview-broadcast.test.mjs`（5 用例：合并/scope、节流、风暴退化、flush、300ms 风暴模拟 7.2s 内 ≤5 次广播 vs 旧 ~24 次）、`useTaskOverview.performance.test.ts`（+3 门闩/scope 用例）、`goal-plan-store.cache.test.mjs`（3 用例：命中/外部写失效/同进程写失效）。

### 13.2 回归与实测数据

- desktop 全量测试：**2548/2548 通过**（stash 基线对照 2542 中 1 个跨进程 CLI 10s 超时为环境性预存失败，本次未复现；typecheck 唯一报错 GoalPlanPanel `quality_review` 为预存错误，与本次无关）。
- dev 实测（`~/.peer-agent-lab` 隔离 home，2802 plans + 302MB evidence-index，`pnpm dev:lab`）：
  - 外部变更风暴：99 次注入 / 300ms 间隔 / 30s（`/tmp/pa-trace/storm.mjs`）。
  - 风暴期间主进程 CPU：**0.5-8%**（仅每 2s 节流广播时出现 ~180ms 尖峰）；风暴结束立即归零（0.0-0.1%），无残留负载。
  - 对照修复前同环境 trace（§12.1）：主进程 84% 打满、每 ~300ms 一个 146-216ms 长任务、activeMeta 热点 4.7s/7.2s——**全部消失**。

### 13.3 遗留项（独立工单，非本次范围）

- `evidence-index.jsonl` 302MB 无界增长：需要滚动/归档策略（§12.4 第 5 项）。
- `spawn` 4.1s 热点在本次实测中未再现（与自激循环消除相关），若后续复现需单独归因。
- tray 菜单打开时若后台有排队刷新，最多延迟 2s 才反映最新状态（点击路径已即时刷新，可接受）。

## 14. 2026-08-14 工作台产品收口：待验收预览 + 讨论区常驻

用户截图复核：性能修复后工作台仍铺 200 张「结果待验收」，「正在讨论」整块消失。这不是主进程长任务残留，而是首页产品契约。

### 14.1 根因

- 协议把未验收 `completed` 投影为 `result_ready`；聚合层按产品旧注释「不限条」返回全部待验收。
- 首页 `TaskOverviewPage` 把 `displayedResults` 全量渲染，徽标也用渲染条数，于是 200 张卡铺满首屏。
- 「正在讨论」只消费 `source === 'conversation'`，且 `{discussions.length > 0 ? ... : null}`。无未读会话时整块不渲染。有 GoalPlan 的会话还会被挤出讨论桶。

### 14.2 落地（`peer_agent`）

| 文件 | 改动 |
| --- | --- |
| `apps/desktop/renderer/src/app/pages/TaskOverviewPage.tsx` | 新增 `RESULT_PREVIEW_LIMIT = 4`；首页只渲染 `previewedResults`；徽标用 `resultReady.length` 真实总数。讨论区去掉 `length > 0` 整块消失；无未读时保留标题 + 空态。 |
| `apps/desktop/renderer/src/app/pages/TaskOverviewPage.discussionLayout.test.ts` | 补两条源码契约：讨论区常驻、待验收预览截断且徽标保真。 |

完整待验收队列仍走「查看历史」。聚合层默认仍可不限条，避免任务/历史页丢队列。

### 14.3 验证

- `node --test apps/desktop/renderer/src/app/pages/TaskOverviewPage.discussionLayout.test.ts apps/desktop/electron/main/task-overview-aggregator.test.mjs`：**66/66 通过**。

## 15. 2026-08-14 产品回退：待验收首页全部展示

用户随后明确要求「待验收的全部展示」。历史页只筛 `terminal`，「查看历史」看不到 `result_ready`，4 条预览等于把队列藏起来。

### 15.1 回退范围

- 去掉 `RESULT_PREVIEW_LIMIT` / `previewedResults`。
- 首页「结果待验收」改回 `groupResultCardsByGoalThread(displayedResults)` 全量渲染。
- 徽标继续用 `resultReady.length`。
- 讨论区常驻空态不回退。

### 15.2 验证

- `node --test apps/desktop/renderer/src/app/pages/TaskOverviewPage.discussionLayout.test.ts`：**10/10 通过**。
