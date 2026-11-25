# ADR 135：自然绘本猫形象体系、主对话内联任务流与可插拔 CLI 执行器架构

创建时间：2026-11-25  
最后更新：2026-11-25（初版定案：确立路线 A 自然毛色绘本猫、侧栏树 + 对话流内联任务动态 + 输入框汇总条三位一体流转模型、自家小猫 CLI 优先的 `ExecutorIcon` 抽象，以及后续多 CLI 执行器 Control Plane / Worker Runtime 边界）  
状态：Accepted（阶段 1 桌面端视觉、侧栏与内联任务流体验授权立即实施；阶段 2–4 多 CLI 执行器适配按本 ADR 架构边界分期落地，代码实施与发布验收另记）  
级别：A（产品核心视觉身份、Bot ↔ Worker 跨区域流转契约、Rust Core Control Plane 与外部 Coding Agent CLI 执行器隔离与核验边界）  
关联：
- [ADR 133：全端统一 Rust Core 与双宿主融合终局架构](./133-unified-rust-core-and-dual-host-architecture.md)
- ADR 134（在途 `Peer-Agent` `codex/native-rust-cli`：Desktop 壳层导航、侧栏任务、Touch Bar 与全宽任务工作台）
- [ADR 110：跟进责任收口与当前待办列表判定](./110-follow-up-responsibility-and-current-list.md)
- [ADR 116：任务控制、执行停稳与资源交接](./116-session-control-and-resource-settlement.md)
- [ADR 118：OpenUI 可交互结果复用与运行时边界](./118-openui-interactive-results-and-runtime-boundaries.md)
- [ADR 124：遗留停止义务的受控核实与跟进退役](./124-legacy-stop-obligation-controlled-resolution.md)
- [ADR 76：Peer 作为 ACP Agent](./76-peer-acp-agent.md)
- [实施设计规范：ADR 135 工程实施文档](../specifications/adr-135-implementation-design.md)
- [产品体验规范](../specifications/peer-product-experience-standard.md)
- [Peer Frost 设计语言规范](../specifications/14-product-design-language.md)

---

## 1. 背景与待解问题

在 `v0.1.0-rc.42` 桌面端实机体验与视觉审查过程中，暴露出四类影响产品质感与长期扩展性的核心问题：

1. **Bot 头像视觉与 Peer 品牌气质割裂**：
   - 既有几何机器人/全头高饱和染色猫（荧光绿、霓虹粉、亮紫、青色 + 几何耳蜗/胡须/`w` 嘴拼接）呈现强烈的“塑料贴纸 / 程式化刻意感”，与 Peer 温润克制的霜纸界面（Frost v2）及“黑猫望月”品牌主图标格格不入。
2. **Bot ↔ 子任务（Worker）的视觉噪音与流转摩擦**：
   - 侧栏子任务在选中时使用高对比度纯黑键帽条（`var(--chrome-keycap-bg)`）并在行内塞入灰色状态/动作胶囊（如「重验」），在浅色侧栏里形成刺眼视觉黑块；同时常驻的大面积灰底搜索输入框在顶部已有搜索图标与 `⌘K` 的情况下造成额外视觉拥堵。
   - 主对话流中，Bot 回复下方挂载的委派任务引用（`ReplyTaskReferences`）当前采用偏重的块状底色卡片与双行堆叠，并行派出 3–5 个任务时横向折行且扫读效率低，难以像极简事件流那样一眼掌握各 Worker 的实时进展与异常原因。
3. **Bot 抽屉细节冗余（已形成修复基线，需纳入本次规范收口）**：
   - 概况页「沟通风格 / 主动性 / 签收策略 / 对话模型 / 挂载能力」卡片此前因 `> div + div` 误放竖向分割线并叠套有框按钮，线条杂乱；
   - 设置页模型角色选择行（如 `任务执行`）将「跟随全局」说明文字孤立悬空在下拉控件下方，破坏行高均衡与视觉对齐。
4. **未来多 CLI 执行器接入缺少一等概念抽象**：
   - 行业内多 Agent 桌面端普遍通过任务左侧或头像角标标识底层执行的 Coding Agent CLI（如 Claude Code、Codex CLI、OpenCode 等）。
   - Peer 当前完全运行于自家原生 Rust 引擎（`peer-native` / 自家小猫 CLI），若现在直接将模型供应商图标当作 CLI 执行器图标展示，会误导用户；而若不提前建立 `ExecutorKind` 与执行器边界，后续对接外部 CLI 时将面临 UI 返工或破坏 Peer 宿主隔离/核验闭环的风险。

---

## 2. 决策一：路线 A「自然毛色绘本猫」形象体系与兼容契约

### 2.1 美学准则（强制）
1. **真实自然毛色 + 哑光绘本水粉调色板（Matte Gouache）**：
   - 全面禁止将猫脸/猫毛整体涂成荧光绿、霓虹粉、亮紫、天青等非自然色。
   - 全部 8 款内置角色统一采用温暖、低饱和的真实猫毛色与纸感配色（炭黑、奶白、三花暖橘、雾蓝灰、拿铁米棕、焦糖棕、奶牛黑白、燕麦灰褐），在浅色霜纸与深色静谧两种主题下均保持清晰轮廓与柔和对比。
2. **极简 3/4 微侧脸五官 + 柔圆领口底座**：
   - 五官保持极致克制：仅保留两颗略偏左的 **3/4 视角细长豆豆眼** 与一枚若有若无的微柔鼻点（黑猫可纯豆豆眼）；**严禁画卡通三角鼻、`w` 嘴与外伸棍状胡须**。
   - 每只猫底部配一弯柔和收口的**圆弧领口/围巾/胸毛底座**（无平切硬底边），赋予绘本肖像的安定感而非漂浮贴纸感。
3. **靠「自然花色 + 克制微配饰」区分 8 只角色，兼容既有 8 键协议**：
   - **严格保留** `@peer-agent/protocol` 中被单测锁定的 `BOT_AVATAR_SHAPES`（8 键）与 `BOT_AVATAR_COLORS`（8 色）定义，不破坏已有 `profile.json` 持久化与确定性哈希测试：

   | 协议 `shape` 键 | 角色名（中 / 英） | 毛色与微配饰特征 |
   |---|---|---|
   | `circle` | 望月黑猫 / Midnight Moon | 深炭靛黑毛色、奶白下巴、暖金新月项圈（直接呼应 Peer 品牌 Logo） |
   | `square` | 三花小猫 / Calico | 奶白底色、暖橘与炭黑有机花斑、赤陶圆领 |
   | `pill` | 橘猫画师 / Ginger Beret | 暖杏橘毛色、奶油腮颊、倾斜鼠尾草绿贝雷帽 |
   | `arch` | 拿铁暹罗 / Latte Siamese | 燕麦奶咖毛色、烘焙可可耳与轻柔面罩、牛仔蓝围巾 |
   | `hex` | 蓝猫学者 / Dusty Blue | 雾蓝灰英短毛色、轻盈暖黄铜细框椭圆眼镜、燕麦毛衣领 |
   | `diamond` | 奶牛绅士 / Tuxedo | 象牙白毛色、不对称炭黑斜刘海、酒红小领结 |
   | `triangle` | 珍珠白猫 / Pearl Cat | 暖象牙白毛色、不对称钴蓝与金黄头巾、单颗白色珍珠点 |
   | `star` | 暖棕狸花 / Warm Tabby | 燕麦暖棕毛色、柔棕额帽、温暖赤陶围巾 |

4. **`avatar.color` 的新语义（禁止反染猫毛）**：
   - `avatar.color`（以及设置页的 8 色点选）**不得**用于重绘猫毛或猫脸；
   - `avatar.color` 继续驱动对话区主题点缀变量 `--bot-message-accent`，并可选作极克制的领巾/围巾低饱和混色调色（如与暖纸基色混合，绝不破坏绘本调性），同时在设置页「外观」中提供直选 8 只绘本猫造型或一键切换的交互。

### 2.2 「自家小猫 CLI」执行器微标与“防猫套猫”原则
1. 引入一等执行器微标抽象 `ExecutorIcon`，当前阶段默认且唯一运行态值为 `'peer'`，渲染 **14px 极简「Peer 小猫 CLI」单色剪影微标**（浅色温炭墨、深色暖月白）。
2. **显隐防冗余原则**：
   - **任务维度（侧栏子任务行、主对话内联任务行、Touch Bar 抽屉、任务工作台标题）**：始终展示 `ExecutorIcon`（当前为自家小猫 CLI 微标），明确每条任务由哪个执行器 CLI 驱动。
   - **Bot 头像右下角 `ExecutorBadge`**：保留完整插槽；在单执行器（纯 Peer 原生 CLI）模式下**默认不叠加显示**，避免“绘本猫头像右下角再叠一只小猫”的视觉重复。仅当项目启用了多 CLI 或该 Bot 显式绑定非默认外部 CLI 时浮现对应执行器角标。

---

## 3. 决策二：三位一体 Bot ↔ Worker 直观流转模型（不采用割裂的 `Bots | Tasks` 双 Tab 切换）

经过交互对比评审，正式确定 Peer 桌面端**不采用**将 Bot 与 Task 拆入侧栏底部两个互斥 Tab 的切换方式，而是在 ADR 134 既有结构上升级为 **「侧栏树直出 + 主对话内联任务流 + 输入框上方汇总条」** 三位一体流转模型：

> **核心依据**：Peer 中每个 Bot 严格对应一个项目工作区，所有委派任务均归属其父 Bot。将活跃任务直接呈现于对应 Bot 下方并同步透出于主对话回复流中，可避免来回切换视图带来的上下文割裂与归属丢失。

### 3.1 侧栏：Bot → 活跃子任务直出树（红框 1 规范）
1. **Bot 摘要行（`BotRow`）**：
   - 当 `item.state.running > 0` 时，副标题位优先显示安静直观的 **`{running} 个工作中`**（英文 `{running} working`），避免旧对话预览与活跃执行状态争抢注意力；空闲时显示最近回复摘要与浅色时间戳。
   - 保留现有点击进入 Bot 主对话、右键/展开控制与无障碍键盘导航。
2. **活跃子任务行（`BotSidebarTasks`）**：
   - 在父 Bot 头像中心下方用一条**极轻竖向引导线**（1px，低透明度）建立自然父子层级，取代无归属感的松散缩进。
   - 每行严格采用三段轻量结构：`[状态微标]` + `[ExecutorIcon（自家小猫 CLI）]` + `[完整任务标题]`：
     - 状态微标：执行/核验中为轻柔旋转小弧（琥珀/青蓝语义）；待用户确认或核验失败为 `6px` 暖橙/警示点；就绪待交接为柔和绿点；排队中为浅灰空心小圆。
     - **严禁**在侧栏任务行右侧附加项目目录名胶囊（Peer 每个 Bot 本身即项目，附加目录胶囊只会把任务名挤压成 `r... / co...`）。
     - **严禁**使用高对比度纯黑选中条（废止 `.bot-sidebar-task.is-selected` 的 `--chrome-keycap-bg` 黑块）及行内「重验」小按钮；选中态改为柔和霜纸浮起底色，重验动作严格留在右侧任务工作台与 Touch Bar 中执行。
   - 默认每 Bot 最多展示 3–5 条活跃任务（沿用可配置阈值），超出部分以极轻文本行 **`再显示 N 个任务`** 折叠展开。
   - 活跃/历史边界严格遵守 ADR 110 / ADR 124，**唯一消费宿主 `followUp.inCurrentList`**，绝不在前端另写第二套状态过滤白名单，绝不向用户暴露 `obligation_indexed`。
3. **侧栏整体降噪**：
   - 顶栏已提供放大镜搜索按钮与 `⌘K` / `⌘F`，将默认常驻的厚灰底 `.bot-search-frame` 改为**按需展开的轻量过滤栏**（无查询且未聚焦搜索时隐藏占位，输入/快捷键唤起时平滑呈现，保留全部既有筛选与键盘选择能力）。
   - 跨 Bot 的全局待处理汇总保留在侧栏左下角简洁的待处理徽章按钮（点开进入 `AttentionSheet`），无需额外 Tab。

### 3.2 主对话流：无边框单行内联任务动态 + 输入框上方汇总条（红框 2 规范）
1. **主对话内联任务动态流（重构 `ReplyTaskReferences`）**：
   - 废止此前带底色块的双行堆叠卡片样式；在 Bot 回复正文下方改为**无边框、轻盈单行可点击事件流**：
     ```text
     [小猫 CLI 微标] 任务标题（单行省略，权重 520）    [简短实时状态 / 结论]  ›
     ```
   - 静息态无背景填充、无边框，仅在 hover/focus 时出现微弱全宽行底色；通过负水平外边距与正文严格左对齐。
   - 状态/结论摘要遵循实事求是原则：运行中显示「执行中 / 核验中」、待批显示「待你确认」、核验未通过显示「核验未通过」、执行失败显示真实简短失败原因或「执行失败」、已签收显示「已完成」；点击整行直达该任务工作台，点顶部面包屑一键返回父 Bot 主对话。
2. **输入框上方任务汇总条（打磨 `ComposerTouchBar`）**：
   - 保持紧贴输入框顶部的单行轻盈汇总条形态（`[小猫 CLI / 状态微标] N 个任务 · M 个运行中 ⌄` + 右侧 `历史任务 K ⌄`），点击平滑展开 `TouchBarTray` 切换所有活跃与历史任务。

### 3.3 Bot 抽屉视觉收口（已验收基线）
1. **概况页详情卡（`OverviewTab` / `bot-drawer.css`）**：取消 2×2 属性格之间的内部竖线及误加在第 2 行首列的左缩进，改为留白 2×2 排版；「挂载能力」入口取消嵌套边框按钮，改为无边框全宽悬停行加右侧轻箭头，与上方仅以单条极细水平分隔线相隔。
2. **设置页模型角色行（`BotPolicyFields` / `BotModelControls`）**：将「跟随全局 / 自动选择」来源文案从下拉框下方移至角色标题行最右侧（左：`任务执行`，右：`跟随全局` 11px 浅色文字），消除悬空说明文字导致的错落感；当模式为 `tier` 且下拉文本已直接展示档位名时不重复渲染来源文案。

---

## 4. 决策三：可插拔多 CLI 执行器架构（Control Plane / Worker Runtime 分层）

为确保未来接入 Claude Code、Codex CLI、OpenCode、Gemini CLI 等外部 Coding Agent CLI 时不破坏 ADR 133 确立的唯一 Rust Core 主链，现确立以下硬性架构边界：

### 4.1 职责分层：Peer 永远是 Control Plane，CLI 只是可插拔 Worker Runtime

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ Peer Control Plane（始终归 Peer Rust Core 唯一掌控，不可被外部 CLI 旁路）   │
│ • Main Bot 对话、项目记忆 (MemoryStore)、持久目标 (ObjectiveStore)        │
│ • 并发调度与槽位管理 (ExecutionScheduler)、Git Worktree 隔离 (Worktree)    │
│ • 权限审批真源 (ApprovalStore / PolicyStore)                              │
│ • 独立事实核验与证据链 (Verifier + EvidenceIndexStore + Acceptance)       │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │  Rust Trait: WorkerExecutor (零 unsafe)
       ┌────────────────────────┼────────────────────────┬──────────────────┐
       ▼                        ▼                        ▼                  ▼
┌──────────────┐       ┌────────────────┐       ┌────────────────┐  ┌──────────────┐
│ Peer Native  │       │  Claude Code   │       │   Codex CLI    │  │  ACP Generic │
│  小猫 CLI    │       │  CLI Adapter   │       │  CLI Adapter   │  │ (OpenCode /  │
│ (内置默认)   │       │ (stream-json)  │       │ (exec --json)  │  │  Gemini CLI) │
└──────────────┘       └────────────────┘       └────────────────┘  └──────────────┘
```

### 4.2 四条硬性架构铁律
1. **Worktree 强制隔离**：任何外部 CLI 执行写任务时，必须在 Peer `GoalWorktreeAdapter` 预先分配的隔离目录/分支内运行；任务完成后由 Peer 控制面基于真实 git diff 执行审查与 `Handoff`，外部 CLI 严禁直接污染主工作区或跳过合入确认。
2. **统一结构化事件与取消域**：每个外部 CLI 适配器必须实现 Rust `WorkerExecutor` trait，将其原生流式输出翻译为 Peer 规范 `ExecutorEvent`（阶段、工具摘要、审批请求、产物引用、最终汇报与退出码），并绑定 Peer `CancellationToken` 与进程组清理（防止取消/崩溃后留下孤儿 CLI 子进程）。
3. **权限最小化与审批桥接**：
   - 支持权限钩子/回调的 CLI（如 Claude Code hooks 或 ACP `request_permission`）必须将高风险动作桥接回 Peer `ApprovalStore` 审批卡；
   - 不支持细粒度实时回调的 CLI，必须按当前 Bot/Task 的 `LocalAccessLevel` 映射为对应沙箱/只读参数，严禁默认透传 `--dangerously-skip-permissions` 等无限制提权标志；
   - 仅向子进程注入该执行器运行所需的最小环境变量，禁止批量透传 Peer Vault 中其它渠道密钥。
4. **统一核验闭环（不可信任外部 CLI 自报成功）**：
   - 外部 CLI 退出后交回的文本与产物，**一律与 Peer Native Worker 同等进入 `SessionSupervisor` 的 `finish_verifier_run` 与 `EvidenceIndexStore`**；
   - 核验器基于真实工作树差异、构建/测试输出与产物证据给出通过/失败结论，确保所有执行器共享同一质量门槛与重验流程。

---

## 5. 不变量与禁行项（Hard Invariants & Non-Goals）

- **协议向后兼容**：`BOT_AVATAR_SHAPES`（8 项）与 `BOT_AVATAR_COLORS`（8 项）数组长度、枚举值及 `generateAvatar(workspaceId)` 确定性分布不可破坏。
- **零 `unsafe` 约束**：Rust 侧新增 `executors` 模块及所有子进程管理代码严格禁止使用 `unsafe`。
- **不另建前端状态真源**：侧栏与内联任务动态严格消费宿主 `followUp` 与 `WorkSession` 投影，不绕开 ADR 110 / 124。
- **阶段 1 非目标（Explicit Non-Goals）**：阶段 1 不修改 Rust 执行引擎、不启动外部 Claude Code / Codex 子进程、不引入新的本地数据存储格式门槛；阶段 1 仅完成前端视觉/流转升级、抽屉修复整合及 `ExecutorIcon` 默认 `'peer'` 抽象。

---

## 6. 分阶段路线图

| 阶段 | 范围 | 主要产出 | 状态 |
|---|---|---|---|
| **Phase 1（立即执行）** | 桌面端形象、侧栏树、主对话内联任务流、Touch Bar 与抽屉收口 | 路线 A 8 只绘本猫、`ExecutorIcon`（自家小猫 CLI）、红框 1 侧栏重构、红框 2 内联单行动态流、概况卡 & `跟随全局` 修复 | Accepted · 交给 Codex 实施 |
| **Phase 2（架构抽象）** | Protocol `executor` 字段 + Rust `WorkerExecutor` trait 抽出 | `packages/protocol/src/executor.ts`、`crates/peer-project-agent/src/executors/`、`PeerNativeExecutor` 无损迁入、本机 CLI 探测器 | Accepted · 规划定案 |
| **Phase 3（首批外部 CLI）** | 接入结构化协议最成熟的外部 CLI | `ClaudeCodeExecutor`（`stream-json`）与 `CodexCliExecutor`（`exec --json`）适配、沙箱权限映射、设置页 CLI 健康检测 | Accepted · 规划定案 |
| **Phase 4（ACP 与多 CLI 混编）** | 通用 ACP 适配器 + Bot 粒度执行器切换 + 头像角标自动点亮 | `AcpExecutor`（OpenCode / Gemini CLI 等）、Bot 设置页执行器选择、多 CLI 模式下自动显示 Bot 头像右下角 `ExecutorBadge` | Accepted · 规划定案 |
