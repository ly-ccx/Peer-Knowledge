# 多任务并行导致工作台与会话 Drawer 卡顿：完整诊断与修复方案

> 代码仓库：`/Users/liangyin/Documents/DEV/github/peer_agent`  
> 知识仓库：`/Users/liangyin/Documents/MiaoYan/peer-knowledge`  
> 日期：2026-08-11  
> 影响范围：Desktop main TaskOverview 投影、GoalPlan store、renderer 工作台/会话 Drawer、聊天滚动热路径

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
