# Peer CLI / TUI 渲染与交互性能优化方案

> 创建时间：2026-08-04  
> 最后更新：2026-08-04  
> 关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`  
> 分析基线：`dev/0.0.2` @ `6d5c8e1b5e0ba821ab68cefde867123034eb0a41`  
> 主要范围：`apps/tui`、OpenTUI 渲染链路、流式消息与工具输出  
> 文档性质：诊断模型、目标架构、实施路线与验收规范；本文不直接修改产品代码。

## 摘要

Peer CLI 当前的“卡顿感”不能简单归因于“没有 60Hz”。终端界面的可见更新需要经过 runtime 事件、controller 缓冲与发布、React/OpenTUI 计算、Markdown 与布局、终端差分、PTY 写出以及终端模拟器绘制。任意一层的突发、阻塞或放大，都可能表现为动画跳跃、文字成团、输入迟滞、滚动顿挫或大工具输出冻结。

当前代码已有正确基础：流式 delta 以 `STREAM_BUFFER_FLUSH_MS = 32` 合批，会话内容具有 render window，装饰动画采用低频定时器而非固定 60Hz 全屏循环。但当前缺少端到端性能观测，也尚未证明主要瓶颈究竟是无效 `publish`、完整 snapshot 传播、活跃消息更新放大、Markdown 重算、工具输出洪峰、OpenTUI diff，还是终端写出与模拟器本身。

本方案的核心决策是：

1. **先建立可重复的性能基线，再改架构。**
2. **先修最短因果链：无效发布、引用不稳定、重复渲染和大输出背压。**
3. **保留业务 `ChatSnapshot` 作为一致性事实源，先通过 selector、memo 与结构共享减小传播。**
4. **只有数据证明多时钟和多发布竞争明显时，才引入按需、分优先级的视觉提交调度器。**
5. **只有数据证明 React reconciliation 是主瓶颈时，才拆分状态域。**
6. **不把固定 60Hz、常驻 frame loop 或大规模状态重构作为默认答案。**

最终目标不是让性能面板显示一个漂亮的 fps 数字，而是确保输入优先、流式稳定、动画连贯、长会话可控、大输出有背压，并且每一次优化都能由基准数据证明。

---

## 1. 问题重写与范围

### 1.1 系统语言中的问题

用户感知的“一卡一卡”应重写为：

> Peer TUI 的端到端可见提交节奏不稳定；高频事件、同步计算、布局与终端写出可能在主线程形成突发或长任务，使输入、流式文本、状态动画和滚动无法在各自延迟预算内完成。

这里至少包含五类不同症状：

| 症状 | 可见表现 | 优先怀疑层 |
| --- | --- | --- |
| 动画跳跃 | spinner、呼吸或状态文字步进明显 | timer 延迟、动画设计、提交竞争 |
| 流式成团 | 文字间歇性批量出现 | 上游 chunk、32ms flush、event-loop lag、单次 render 成本 |
| 输入迟滞 | 键入、删除、确认反馈晚 | 主线程长任务、终端写出洪峰、优先级倒置 |
| 滚动顿挫 | 长会话翻页或贴底时停顿、跳动 | render window、布局/wrap、视口锚定 |
| 大输出冻结 | 工具日志或长代码块出现时 UI 暂停 | 无背压、节点爆炸、Markdown/高亮、ANSI 写出 |

这些症状不能用同一个“提高帧率”补丁处理。

### 1.2 工程约束

1. TUI 运行在终端，不具备浏览器 `requestAnimationFrame` 与显示器 vsync 的同等契约。
2. OpenTUI、PTY 和终端模拟器共同决定最终可见节奏；应用只能控制链路前半段。
3. 输入与审批交互必须高于装饰动画。
4. 空闲状态不应为追求帧率持续消耗 CPU。
5. 长会话、大工具输出、窄终端和不同终端模拟器都必须纳入基准。
6. 业务状态一致性不能为局部性能优化让路。
7. 本方案不预设拆 store、重写 renderer 或替换 OpenTUI。

### 1.3 非目标

- 不承诺全屏固定 60Hz；
- 不用顶层 `frame` state 每 16.7ms 或 33ms 驱动整棵 App；
- 不在 profiling 前拆分 controller 的业务状态模型；
- 不原地修改已经发布给 UI 的 snapshot；
- 不通过关闭 Markdown、虚拟窗口或状态反馈掩盖问题；
- 不把某个终端模拟器的表现当作所有平台事实；
- 不以“空闲时零定时器”替代用户可感知的延迟指标；
- 不在本文档任务中直接修改 `peer_agent` 产品代码。

---

## 2. 当前代码事实

以下事实来自分析基线，不等同于对瓶颈的最终判断。

### 2.1 流式事件已经合批

`apps/tui/src/chat-controller.ts` 定义：

```ts
const STREAM_BUFFER_FLUSH_MS = 32;
```

`message.delta` 与 `reasoning.delta` 进入 `streamDeltaBuffer`，首个事件启动 `setTimeout`，约 32ms 后由 `flushStreamDeltaBuffer` 统一应用并 `publish`。

理论上流式提交上限约为每秒 31 次。若仍有文字成团或卡顿，必须继续检查：

- 上游 delta 是否本就突发到达；
- event loop 是否无法按时执行 32ms timer；
- 一次 flush 内处理的字符与 segment 数是否过大；
- flush 后的 snapshot、Markdown、layout 或终端写出是否超过预算；
- 同期是否有 plan、accounting、tool、status 等额外发布。

### 2.2 controller 发布完整 ChatSnapshot

`chat-controller.ts` 中 `publish(next)` 更新内部 `snapshot`，随后通知全部 listener。App 订阅后调用 `setSnapshot(next)`。

这会让 App 函数组件重新执行，但不能据此断言“终端全屏重绘”：React reconciliation 与 OpenTUI diff 仍可能复用未变化节点。需要 profiling 判断 App 重算、子树 reconciliation 和最终终端写出各自占比。

### 2.3 流式 flush 更新活跃消息

当前 flush 会创建 `messages = [...snapshot.messages]`，再将缓冲事件追加到末尾 assistant 消息，并发布包含新 `messages` 的 snapshot。

待验证问题包括：

- 已完成历史消息对象是否保持引用稳定；
- 活跃 assistant 的 segments 是否只替换必要路径；
- 渲染窗口是否因数组引用变化重新遍历过多内容；
- 下游消息组件能否借助稳定 key、memo 与 revision 跳过历史重算。

### 2.4 会话已有 render window

`apps/tui/src/conversation-render-window.ts` 已提供 latest/history 模式、分页与窗口投影。App 通过 `useMemo` 从 `snapshot.messages` 和窗口状态生成 `renderProjection`。

优化方向不是“从零增加虚拟化”，而是验证现有窗口是否在以下场景真正限制工作量：

- latest 模式下超长单条消息；
- 大量工具输出嵌入单条消息；
- history 翻页；
- 终端宽度变化导致重新 wrap；
- active tail 高频增长。

消息条数窗口不能自动解决“单条消息非常重”。

### 2.5 Markdown 在渲染链路中解析和高亮

`apps/tui/src/markdown-view.tsx` 负责 block 解析、inline 处理、表格、代码高亮和终端宽度适配。流式内容每次变化时，活跃消息可能重新进入这些路径。

需要分别测量 parse、code highlight、table layout、wrap 和已完成消息重复执行时间，不能先验认定 Markdown 是主瓶颈。

### 2.6 动画是多套低频时钟

| 动画/状态 | 间隔 | 约等效频率 |
| --- | ---: | ---: |
| thinking spinner | 80ms | 12.5fps |
| 普通状态动画默认值 | 280ms | 3.6fps |
| wordmark breathe | 125ms | 8fps |
| 流式 delta flush | 32ms | 最多约 31 次/秒 |

这些频率本身并非错误。问题只在于 timer 是否延迟、多个提交是否竞争、动画是否引发过大的 React/OpenTUI 工作，以及设计上的离散步进是否被误认为性能卡顿。

### 2.7 当前没有统一性能事实源

目前没有足够证据回答：

- `publish/s` 按事件类别分别是多少；
- 一次 stream flush 平均和峰值包含多少字符；
- App、消息列表、MarkdownView 各执行多少次；
- event-loop lag 的 p95/p99 是多少；
- OpenTUI commit 和 terminal write 各耗时多少；
- 一次大工具输出写出多少 ANSI 字节；
- 输入事件到文本可见的延迟是多少。

因此任何大规模架构结论都必须暂缓。

---

## 3. 端到端因果链

### 3.1 主链路

```text
模型/runtime/tool 事件
  → runtime session / event stream
  → ChatController 缓冲、归并与业务 snapshot
  → publish / listener
  → App setSnapshot 与 selector/projection
  → React reconciliation
  → Markdown / 高亮 / wrap / layout
  → OpenTUI render tree 与 terminal diff
  → ANSI/PTY write
  → 终端模拟器解析、合成与显示
```

### 3.2 输入竞争链路

```text
键盘事件
  → OpenTUI input dispatch
  → composer/command/approval state
  → React/OpenTUI commit
  → PTY write
  → 输入字符或焦点状态可见
```

当主链路存在长同步任务或大写出时，输入链路会被延迟。优化必须保证输入优先，而不是仅让 spinner 更快。

### 3.3 性能放大节点

1. 一个上游事件触发多个业务 `publish`；
2. 一个小字段变化创建大范围新对象；
3. 活跃消息变化使历史消息重新解析或布局；
4. 单条工具输出生成海量终端节点；
5. 终端宽度变化使大量内容重新 wrap；
6. 多个 timer 在同一窗口触发独立 commit；
7. renderer 产生大量重复 ANSI；
8. 大写出占用事件循环，输入得不到调度。

---

## 4. 根因假设与证伪方式

### H1：无效或重复 publish 放大更新次数

**假设**：状态没有可见变化，或同一逻辑事件跨多个路径连续发布。

**证伪**：统计按 lane 分类的 `publish/s` 与 no-op 比例；若 no-op 接近零、发布率受控，则降低优先级。

### H2：活跃消息更新破坏历史引用稳定性

**假设**：流式只改变末尾内容，但下游无法跳过历史消息计算。

**证伪**：记录历史消息组件和 MarkdownView render 次数；若纯流式时仅 active tail 重算，则不成立。

### H3：Markdown、高亮或 wrap 超过预算

**假设**：长代码块、表格和未闭合 Markdown 在每次 flush 时重复解析。

**证伪**：对 parse/highlight/layout 分段计时；若 p95 占比很小，则检查 OpenTUI diff 或写出。

### H4：大工具输出缺少背压

**假设**：工具完成事件把大量文本直接转成 UI 节点与 ANSI，阻塞输入。

**证伪**：运行固定 5,000 行及更大输出；若节点、写出量和 event-loop lag 未显著升高，则降低优先级。

### H5：多套 timer 和业务发布竞争

**假设**：spinner、wordmark、status、stream 等 timer 在相近时间提交，形成脉冲式工作。

**证伪**：记录提交时间线；若冲突少或动画成本极低，则不引入统一调度器。

### H6：OpenTUI/终端写出是主要瓶颈

**假设**：React 计算不重，但 terminal diff 或 ANSI 写出量过大。

**证伪**：对比计算、commit/write 耗时并跨终端运行相同 trace；若差异主要来自终端端，应减少写出面积和频率，而不是先拆业务 store。

---

## 5. 优化原则与目标架构

### 5.1 原则

1. **测量先于缓存，基线先于架构。**
2. **输入与审批优先于流式，流式优先于装饰动画。**
3. **业务事实与视觉提交分离。**
4. **已发布状态不可变。** 可变缓冲只能存在于提交之前。
5. **局部变化只影响局部渲染。**
6. **突发数据必须有背压。**
7. **自适应优于固定帧率。**
8. **每阶段都有退出条件和回滚点。**

### 5.2 目标结构

```text
Runtime / Tool Events
  ├─ interaction lane（输入、审批、Escape、焦点）
  ├─ stream lane（message/reasoning delta）
  ├─ state lane（plan、status、accounting）
  └─ decorative lane（spinner、breathe）
          ↓
ChatController：业务状态唯一事实源
          ↓
可观测 publish 边界：分类、no-op guard、revision
          ↓
UI selector / projection：稳定引用，只暴露所需切片
          ↓
渲染缓存：completed message / markdown block / width / theme
          ↓
OpenTUI diff + 受控 terminal write
```

视觉调度器不是必选基础层。只有数据证明 lane 冲突时，才在 publish 边界和 UI commit 之间加入按需 scheduler。

### 5.3 状态事实源

- **业务状态事实源**：`ChatController` 内部 `ChatSnapshot`；
- **性能事实源**：固定基准场景输出的 trace 与统计摘要；
- **渲染缓存键**：消息/块 ID、content revision、terminal width、theme/highlighter revision；
- **视口事实源**：`ConversationRenderWindowState` 与明确的贴底/历史模式。

---

## 6. 性能基线与观测体系

### 6.1 调试入口

引入显式开关：

```bash
PEER_TUI_PERF=1 peer
PEER_TUI_PERF=summary peer
PEER_TUI_PERF=trace PEER_TUI_PERF_OUTPUT=/tmp/peer-tui-perf.jsonl peer
```

默认关闭。开启后输出结构化采样到 stderr、文件或退出摘要；不得把高频 debug 文本直接画入主 TUI。

### 6.2 必测指标

| 指标 | 说明 | 价值 |
| --- | --- | --- |
| input-to-visible ms | 键盘事件到对应 UI 可见 | 核心交互指标 |
| event-loop lag | timer 实际执行相对计划时间的延迟 | 判断主线程阻塞 |
| publish/s by lane | stream/tool/plan/status/accounting | 找更新洪峰 |
| no-op publish count | 新状态无可见变化的发布 | 找无效工作 |
| stream flush size | 每次字符数、事件数、间隔 | 区分上游突发与本地阻塞 |
| App/render count | App、conversation、message、MarkdownView | 判断传播范围 |
| parse/highlight ms | Markdown 与代码高亮耗时 | 判断内容计算成本 |
| projection ms | render window 投影耗时 | 验证窗口效率 |
| commit/diff ms | React/OpenTUI 提交与差分耗时 | 判断 renderer 成本 |
| terminal bytes/write | 每次及每秒 ANSI 写出量 | 判断写出放大 |
| long task count | 超过 16/33/50/100ms 的同步任务 | 定位冻结 |
| memory / node count | 长会话与大输出下增长 | 防止空间失控 |

### 6.3 Trace 关联字段

```text
runId, timestamp, scenario, lane, eventType,
conversationIdHash, turnIdHash, messageRevision,
terminalWidth, terminalHeight,
durationMs, eventCount, charCount, outputBytes
```

不得记录完整用户消息、密钥、工具敏感输出或真实路径。

### 6.4 固定基准场景

1. **Idle**：欢迎页静置 30 秒；
2. **Short stream**：普通 300–500 字回复；
3. **Fast long stream**：高吞吐 5,000–10,000 字；
4. **Markdown stress**：标题、嵌套列表、表格、长代码块和未闭合 fence；
5. **Tool burst**：一次产生 5,000 行，再测试更高档位；
6. **Concurrent input**：流式和工具输出期间持续键入；
7. **Long conversation**：大量历史消息下 latest/history 与 resize；
8. **Narrow terminal**：窄宽度制造高 wrap 压力；
9. **Terminal matrix**：macOS Terminal、iTerm2/Kitty 之一、VS Code terminal。

### 6.5 测量纪律

- 使用 release 构建；
- 每个场景预热后至少运行 5 次；
- 保存 p50、p95、p99 与 max；
- 同机器、相同终端尺寸和相同 fixture 对比；
- 一次只改变一类因果节点；
- 只改善装饰动画但损害输入延迟，应判定失败。

---

## 7. 第一优先级：低风险、高收益优化

### 7.1 去除无效与重复发布

在 controller 发布边界增加分类与最小 guard：

- 重复 status 不发布；
- accounting 显示值未变化时不驱动 UI；
- plan 引用与可见 revision 未变化时不发布；
- 同一 macrotask 内可安全合并的 state 更新只提交一次；
- 不跨越 approval、turn completion、error 等关键边界合并。

不做昂贵完整深比较，优先使用字段 revision、引用和领域 equality。

### 7.2 稳定消息与 segment 引用

目标是流式 flush 只替换 active assistant 路径：

```text
messages array：可以更新
completed messages：引用保持不变
active assistant message：新引用
未变化 segments：引用保持不变
active tail segment：新引用
```

controller 可在提交前维护可变 `streamDeltaBuffer`，但 `publish` 后的 snapshot 必须保持不可变语义。

### 7.3 隔离渲染子树

- conversation 只接收 `renderProjection` 和必要状态；
- composer/status/plan/approval 使用明确 selector；
- completed message 按 `id + revision + width + theme` memo；
- 不把动画 frame 或 meter 数值变成整个 App 的公共依赖；
- 通过 profiling 验证 memo 收益。

### 7.4 缓存已完成内容

缓存层级按成本推进：block parse、code highlight token、table 结构、width/theme 相关终端投影。

- 已闭合 Markdown blocks 固化并缓存；
- 仅重新解析最后一个未闭合 block；
- turn 完成时校正尾部 block；
- 不把整条消息先画纯文本、完成后突然切换完整 Markdown，以免跳版。

### 7.5 大工具输出背压

- 完整输出保存在 artifact 或现有结果事实源；
- TUI 默认显示摘要、头尾窗口或有限行数；
- 折叠内容不创建全部 OpenTUI 节点；
- 展开时分页或分批消费；
- 单次视觉提交设置字符/行预算；
- 输入、审批与 Escape 高于日志刷新；
- 明确提示剩余行数和完整 artifact 入口。

背压不能丢失事实，只限制可见投影和提交节奏。

### 7.6 视口与自动滚动

- 贴底时允许 active tail 推进视口；
- 用户进入 history 或主动上翻后冻结贴底；
- 新内容只显示未读提示，不抢视口；
- width 变化与翻页保持稳定锚点；
- 几何使用 ref/内部状态，只有窗口边界变化才推进 React state。

---

## 8. 可选视觉提交调度器

### 8.1 进入条件

只有满足以下条件之一才实现：

- trace 显示多个 timer/publish 在短窗口重复 commit；
- 合并能显著降低 commit 数和 terminal bytes；
- 装饰动画与流式/工具更新产生优先级倒置；
- Phase 1 后仍有可重复节奏抖动。

### 8.2 正确模型

调度器是“按需唤醒、分 lane、带 deadline 与背压”的提交协调器，不是固定 30/60Hz 顶层循环。

```ts
scheduleVisualUpdate({
  lane: 'interaction' | 'stream' | 'state' | 'decorative',
  deadlineMs,
  coalesceKey,
  apply,
});
```

优先级：

1. `interaction`：输入、审批、焦点、Escape；
2. `stream`：消息与 reasoning delta，最高约 30 次/秒且可自适应；
3. `state`：工具进度、plan、accounting，按可见精度 5–20 次/秒；
4. `decorative`：spinner、wordmark，忙时降级或暂停。

### 8.3 关键行为

- 无 dirty update 时不运行；
- 同 `coalesceKey` 在 deadline 内只保留必要最终状态；
- 不跨越 approval、turn completion、error 等语义关键点；
- 上一提交超预算时降低 decorative/state 频率；
- interaction 到来时抢占装饰工作；
- 记录排队时间、合并数、过期装饰帧与实际提交耗时。

### 8.4 动画策略

- spinner 保持约 12–20fps；
- breathe 保持 8–12fps，使用稳定缓动和少量亮度档；
- meter 可 5–10fps，且只在显示值变化时提交；
- 大工具输出期间暂停 wordmark 等装饰；
- 固定字符宽度，避免水平布局抖动。

禁止以下顶层全局驱动：

```ts
setInterval(() => setFrame((n) => n + 1), 16);
```

它会无条件制造工作。调度器必须协调 dirty work，而不是制造 work。

## 9. 状态域拆分的决策门

### 9.1 为什么不先拆 store

完整 `ChatSnapshot` 使 turn、plan、approval、accounting 等状态在同一发布点保持一致。过早拆分会引入：

- 跨 store 提交的短暂不一致；
- selector 与订阅生命周期复杂度；
- controller API 与测试大面积变更；
- 难以区分架构收益和其他并行优化收益。

### 9.2 进入条件

只有在完成 Phase 1/2 后，profiling 仍证明以下事实，才允许拆分：

- 纯 stream flush 让非 conversation 子树频繁执行且成本显著；
- memo、稳定引用和 selector 无法隔离；
- React reconciliation 占端到端 commit 的主要比例；
- 拆分原型能显著降低 p95，且不破坏状态一致性。

### 9.3 候选状态域

```text
transcript：messages、active tail、render revisions
interaction：mode、approval、command surface、focus
execution chrome：plan、tool status、notices
meter：context accounting、usage、quota
```

业务 controller 仍应提供原子事件或版本号，避免多个 store 各自猜测同一 turn 的完成状态。

### 9.4 回滚条件

若拆分后出现任一情况，应回滚或缩小范围：

- approval 与 transcript 短暂不同步；
- 测试复杂度显著增加但 p95 收益不足；
- 多 store 更新反而增加 commit；
- persistence、resume 或 goal/plan 生命周期出现竞态。

---

## 10. 分阶段实施路线

### Phase 0：建立性能事实源

**目标**：回答“卡在哪里”，而不是先改变体验。

实施项：

1. 增加 `PEER_TUI_PERF` summary/trace 开关；
2. 为 runtime event、buffer、publish、App/Markdown、OpenTUI commit/write 打点；
3. 建立九类固定 fixture 与运行脚本；
4. 输出 p50/p95/p99、long task、字符数与 terminal bytes；
5. 保存基线报告，记录机器、终端、尺寸和 commit。

退出条件：

- 能区分上游突发、本地 event-loop lag、计算、diff 与 write；
- 每类症状至少能关联一个 trace；
- 观测开关关闭时性能影响不可测或处于可接受阈值。

回滚点：instrumentation 由 feature flag 控制，可独立删除。

### Phase 1：修复已证实的局部放大

**目标**：以最小改动减少不必要工作。

候选实施项按证据选择：

1. no-op/repeated publish guard；
2. lane 分类与同 tick 安全合并；
3. completed message/segment 引用稳定；
4. conversation、status、plan 等子树隔离；
5. completed Markdown block 与高亮缓存；
6. active tail 增量解析；
7. 工具输出摘要、分页与提交预算；
8. 贴底/历史模式的稳定视口锚定。

退出条件：

- 目标场景 p95 有明确下降；
- 输入延迟不回退；
- 业务状态与终端输出内容正确；
- 新缓存具备宽度、主题与 revision 失效测试。

### Phase 2：按数据决定视觉调度

**目标**：若仍有提交冲突，用优先级和背压稳定节奏。

实施项：

1. 小型 scheduler 原型，仅接 decorative 与一个高频 lane；
2. 验证 coalesce、deadline、抢占和自动降级；
3. 对比开关前后的 commit/s、bytes/s 与输入延迟；
4. 收益成立后逐步迁移 status/stream；
5. 保留直接提交逃生通道，关键语义事件不排队。

退出条件：

- 提交峰值下降且视觉连续性改善；
- interaction p95 不回退；
- 空闲时不产生固定全局帧循环；
- scheduler 队列与调试成本可控。

### Phase 3：有证据时拆分状态域

**目标**：只在 reconciliation 仍是主瓶颈时减少订阅范围。

实施项：

1. 先拆 meter 或 decorative 等低耦合域；
2. 建立跨域 revision/transaction 规则；
3. 再评估 transcript 与 interaction；
4. 对 resume、approval、goal/plan、compaction 做一致性回归；
5. 每拆一域重新运行完整基准，不做一次性大迁移。

退出条件：

- 非目标子树 render 数明显下降；
- 端到端 p95 获得与复杂度相称的收益；
- 状态一致性测试完整通过。

### Phase 4：持续回归治理

**目标**：防止后续功能重新引入卡顿。

实施项：

1. CI 运行确定性 micro-benchmark；
2. release 前运行本机 terminal matrix；
3. 对 publish rate、long task 和大输出设置告警预算；
4. PR 模板要求说明新增高频 timer、订阅和大文本投影；
5. 维护历史基线与已知终端差异。

---

## 11. 验收指标与性能预算

在 Phase 0 得到真实基线前，以下为初始工程预算，不是已达成事实。基线若证明平台差异明显，应按设备等级调整，但不能取消输入优先原则。

### 11.1 用户可感知指标

| 场景 | 建议验收目标 |
| --- | --- |
| 普通键入 | input-to-visible p95 ≤ 50ms，max 不持续 >100ms |
| 流式期间键入 | p95 ≤ 80ms，不丢键、不乱序 |
| 审批/Escape | p95 ≤ 80ms，不能被动画或工具输出阻塞 |
| 普通流式 | 节奏稳定，无持续 >100ms 的本地停顿 |
| 大工具输出 | 主 TUI 可交互，单次同步冻结不超过 100ms 预算 |
| 长会话翻页 | 视口锚定稳定，不因新内容抢滚动 |
| resize | 收敛后布局正确，不持续重复重排 |

### 11.2 内部预算

| 指标 | 初始预算 |
| --- | --- |
| stream visual commits | 正常最高约 30/s，忙时允许自适应下降 |
| decorative commits | 8–20/s，忙时可暂停 |
| meter commits | 仅显示值变化，通常不高于 10/s |
| event-loop lag | p95 < 20ms；>50ms 需定位；>100ms 视为长卡顿 |
| 单次 App/React 计算 | p95 尽量 < 8ms |
| 单次完整 visual commit | p95 尽量 < 16–33ms，按场景解释 |
| no-op publish | 目标接近 0，保留语义必要例外 |
| historical message re-render | 纯 active tail 流式时目标接近 0 |
| terminal write | 以场景基线回归比例治理，不脱离场景设固定字节数 |

### 11.3 回归闸门

一次优化只有同时满足以下条件才可合入：

1. 目标场景至少一个主指标显著改善；
2. 输入与审批延迟无统计显著回退；
3. CPU、内存和 terminal bytes 不出现无法解释的放大；
4. snapshot 内容、工具事实、Markdown 和视口行为正确；
5. 普通模式下无性能 trace 泄漏或敏感信息记录；
6. 至少在两个终端环境验证。

---

## 12. 测试策略

### 12.1 单元测试

- no-op guard 的领域 equality；
- stream buffer 在 32ms 边界的 flush 与 turn 完成强制 flush；
- completed message 引用稳定；
- Markdown cache key 与 width/theme/revision 失效；
- scheduler lane 优先级、deadline、coalesce 与取消；
- 工具摘要不丢失 artifact 引用；
- render window 在 latest/history 的锚点与边界。

### 12.2 集成测试

- 固定 runtime event fixture 回放；
- 同时输入与高速 stream；
- approval 出现时立即响应；
- 工具输出洪峰期间 Escape；
- resize + active stream；
- history 模式收到新消息不抢滚动；
- turn 完成时 Markdown 尾部校正不跳版。

### 12.3 性能测试

1. **确定性 micro-benchmark**：parse、highlight、projection、snapshot update，可进 CI。
2. **终端端到端 benchmark**：PTY、OpenTUI、终端模拟器参与，运行在 release 前或专用机器。

CI 不使用严格绝对毫秒阈值制造噪声；更适合检查数量预算、算法复杂度和相对回归。终端端到端数据用于 release gate 与人工分析。

### 12.4 正确性回归清单

- 流式 message/reasoning 顺序不变；
- 工具调用与结果归属不变；
- accounting/usage 最终值准确；
- approval 不被合并或延迟越过；
- persistence/resume 得到完整 snapshot；
- plan/goal 状态与 transcript 一致；
- Markdown、代码高亮和表格最终显示一致；
- 复制、选择、滚动、主题与 resize 不退化。

---

## 13. 风险与缓解

### 风险 A：观测本身改变性能

缓解：默认关闭；采样而非每事件同步落盘；批量写 trace；记录 instrumentation overhead。

### 风险 B：过度 memo 导致旧内容

缓解：使用明确 revision 与完整 cache key；建立 width/theme/content 失效测试。

### 风险 C：合并发布破坏语义边界

缓解：approval、error、turn completion、tool result 等关键事件强制 flush；业务 snapshot 仍原子更新。

### 风险 D：背压被误解为丢日志

缓解：完整输出保存在 artifact；TUI 只限制可见投影；明确显示截断、总量与查看入口。

### 风险 E：调度器演变成第二套状态机

缓解：scheduler 只管理“何时提交”，不拥有业务事实；关键事件可直达。

### 风险 F：状态拆分带来竞态

缓解：设置严格决策门；先拆低耦合域；保留跨域 transaction/revision；逐域迁移。

### 风险 G：某个终端优化损害其他终端

缓解：终端 matrix；优先减少应用层工作和写出；平台特化必须可检测、可回退。

---

## 14. 决策门汇总

### 决策门 D0：是否已能定位瓶颈

若不能从 trace 区分 event loop、计算、diff 与 write，禁止进入大架构改造。

### 决策门 D1：是否需要缓存或引用治理

只有历史内容在 active tail 更新时重复计算，才增加对应缓存/memo。

### 决策门 D2：是否需要视觉调度器

只有提交时间线证明多 lane 冲突或无效峰值，且原型能改善输入/commit 指标，才正式引入。

### 决策门 D3：是否需要拆状态域

只有 reconciliation 仍是主要成本，selector/memo 无法解决，才拆 store。

### 决策门 D4：是否需要 OpenTUI 或终端特化

只有应用层优化后 write/diff 仍占主导，并在多终端对比中有明确证据，才深入 renderer 或平台适配。

---

## 15. 推荐首轮实施清单

1. 实现 `PEER_TUI_PERF=summary|trace`；
2. 为 stream enqueue/flush、publish、App snapshot、Markdown parse/highlight、render projection 打点；
3. 准备 short/long/markdown/tool fixtures；
4. 输出第一份基线报告；
5. 从报告中只选一个最大瓶颈；
6. 优先尝试 no-op guard、引用稳定或大输出投影之一；
7. 重跑基准并记录前后差异；
8. 未证明 scheduler/store split 必要前，不启动对应重构。

第一轮应回答而不是预设：

- 32ms flush 是否准时？
- 一次 flush 到可见的最大延迟在哪一层？
- active tail 是否使历史 Markdown 重算？
- 大工具输出主要卡在节点、diff 还是 write？
- spinner 的“卡”是低帧设计还是 event-loop lag？

---

## 16. 最终架构判断

Peer TUI 的优化目标应从“有没有 60Hz”转为“每类工作是否在正确预算和优先级内完成”。固定 60Hz 只能提高触发频率，不能缩短 Markdown、layout、diff、write 的长任务；事件循环拥塞时，它还会增加竞争。

正确路径是：

```text
先测量端到端链路
  → 找到放大节点
  → 减少无效发布与重复计算
  → 稳定 active tail 与历史内容边界
  → 为大输出建立背压
  → 数据需要时再引入按需视觉调度
  → reconciliation 仍占主导时才拆状态域
```

最终治理结果：

- 业务状态由 controller 统一维护；
- 性能事实由固定基准和 trace 统一维护；
- 输入始终拥有最高视觉优先级；
- 流式文本有上限、有合批、可自适应；
- 已完成内容不因 active tail 重复计算；
- 大工具输出不再把完整事实等同于一次性完整渲染；
- 装饰动画在空闲时连贯，在繁忙时主动让路；
- 每项性能重构都有进入条件、退出指标和回滚证据。

一句话原则：

> **不要让 TUI 更勤地重画；要让它只在必要时，以正确优先级，重画真正变化的最小区域。**

---

## 17. 实施结果与验证记录

> 实施时间：2026-08-04  
> 代码工作区：`peer_agent/dev/0.0.2`  
> 代码报告：`apps/tui/perf/tui-performance-report.md`  
> 原始数据：`apps/tui/perf/baseline.json`、`apps/tui/perf/optimized.json`

### 17.1 已实施内容

#### 性能观测 Module

新增 `apps/tui/src/tui-perf.ts`，提供默认关闭的：

```bash
PEER_TUI_PERF=summary peer
PEER_TUI_PERF=trace PEER_TUI_PERF_OUTPUT=/tmp/peer-tui-perf.jsonl peer
```

观测覆盖：

- stream enqueue / flush；
- controller publish；
- App snapshot 接收；
- conversation render-window projection；
- Markdown parse 与 syntax highlight；
- Markdown/highlight cache hit 与 miss。

Module 使用有界 duration samples 和 trace events，提供 p50/p95/p99/max 与 numeric fields 聚合；不记录消息正文、密钥或完整工具输出。TUI 正常退出时由 shutdown 边界同步写出摘要，避免 renderer 销毁后丢失证据。

#### 可重复性能基准

新增 `apps/tui/perf/tui-performance-benchmark.ts` 与 `perf:benchmark` script，覆盖：

1. 40 段复杂 Markdown；
2. 200 个持续增长的流式 Markdown revision；
3. 1,000 行 TypeScript 高亮；
4. 10,000 条消息的 render-window projection；
5. 5,000 行、约 540K 字符工具输出的 presentation projection。

#### 有界渲染缓存

新增 `apps/tui/src/bounded-text-cache.ts`，以条目数和源文本字符数双重限制 LRU：

- Markdown blocks：最多 256 项、单项 64K 字符、总源文本 1M 字符；
- syntax tokens：最多 128 项、单项 256K 字符、总源文本 2M 字符。

缓存 key 使用完整 source；高亮额外包含 language。完成内容可复用不可变投影；流式 active tail 每次内容变化会自然 miss，不修改已发布的 `ChatSnapshot`。

### 17.2 基线诊断

首轮基准 p95：

| 场景 | 基线 p95 |
| --- | ---: |
| 复杂 Markdown parse | 0.1164 ms |
| 1,000 行代码高亮 | 2.9140 ms |
| 10,000 消息窗口投影 | 0.0478 ms |
| 5,000 行工具摘要投影 | 0.0113 ms |

诊断结论：

- 会话窗口投影不是主瓶颈；
- 工具结果已经通过有界摘要投影控制，不需要重写输出链；
- Markdown block parse 成本低；
- 完成消息的重复 syntax highlight 是唯一达到多毫秒的局部放大。

### 17.3 优化结果

优化后典型 p95：

| 场景 | 优化后 p95 | 结论 |
| --- | ---: | --- |
| Markdown parse cache hit | 约 0.0008 ms | 重复 parse 基本消除 |
| 1,000 行 highlight cache hit | 约 0.062 ms | 相对基线约降低 97.9% |
| 200 个流式 revision 一轮 | 约 0.024 ms | active tail 仍正确失效 |
| 10,000 消息窗口投影 | 约 0.046 ms | 无需额外虚拟化重构 |
| 5,000 行工具摘要投影 | 约 0.009 ms | 无需新增背压路径 |

绝对值会受机器负载影响，代码仓中的 raw JSON 是单次运行的事实源；文档只记录量级和决策。

### 17.4 决策门结果

#### D2 视觉调度器：关闭

未实现统一 frame scheduler，原因是：

- 已测 projection 与 parse 路径远低于 1ms；
- 唯一多毫秒重复工作已在 Markdown seam 局部消除；
- 当前没有 trace 证明多 lane commit collision 或 event-loop long task；
- 顶层 frame clock 会制造额外工作。

只有后续真实 runtime trace 显示输入饥饿或重复 commit，才重新打开此门。

#### D3 状态域拆分：关闭

未拆分 `ChatSnapshot` / store，原因是：

- 10,000 消息 projection 的 p95 约 0.046ms；
- 没有 React reconciliation 为主成本的证据；
- 局部缓存已经在正确 seam 消除重复工作；
- 保留单一业务 snapshot 可避免 turn、approval、plan、accounting、persistence 与 resume 的跨 store 一致性风险。

### 17.5 验证结果

已通过：

- `tui-perf` 5 个单元测试；
- 新增 bounded cache 与 Markdown cache 测试；
- controller、render-window、code-highlighter 聚焦测试；
- TUI TypeScript typecheck；
- TUI release build、二进制签名与 Designated Requirement 校验；
- scoped `git diff --check`；
- 优化后 benchmark replay。

首次全量 TUI suite 暴露了并行 runtime 变化下的两个过时测试契约：

1. `conversation-persistence.test.ts` 的旧断言未包含 runtime data-store 新增的 `lifetimeUsage.byModel`；
2. `theme-governance.test.ts` 将 `colorToRgb(`、`mixRgb(` 等 helper 名误判为独立 raw `rgb(` 调用。

没有修改对应产品实现：persistence 测试改为验证完整 `byModel` 聚合；治理正则改为只匹配独立 `rgb/rgba` 调用。两个聚焦文件随后 29/29 通过，最终 `pnpm --filter @peer-agent/tui test` 以 exit code 0 完成。因此全量测试验收项现已关闭。

### 17.6 最终实施判断

本轮没有为了完成清单而引入 60Hz、视觉调度器或状态拆分。实际完成的是：

```text
可关闭观测
  → 可重复基准
  → 用数据排除窗口与工具摘要
  → 定位重复代码高亮
  → 在 Markdown seam 加有界缓存
  → 验证流式失效与重复内容复用
  → 关闭未触发的架构决策门
```

这符合本文最初的治理原则：先修可证明的最小因果链，再决定是否扩大架构范围。
