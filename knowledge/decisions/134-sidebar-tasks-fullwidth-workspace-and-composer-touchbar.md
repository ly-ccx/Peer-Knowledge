# 134. 侧栏任务层级、全宽任务工作台与输入框一体化动态 Touch Bar

创建时间：2026-11-23
最后更新：2026-11-23
状态：Accepted（用户已审阅交互原型与实施契约并批准开工；实现与验收另记）
级别：A（壳层任务导航与输入引用契约，部分修订 ADR 84 壳层任务入口），B（Rust/RPC 增量只读分页投影、任务引用草稿与 UI 触发独立重验）
关联：
- `knowledge/decisions/80-project-agent-delegation-model.md`（保留 1 项目 = 1 主 Bot，不变）
- `knowledge/decisions/84-bot-list-shell.md`（修订侧栏任务展示、主区任务视图与右侧抽屉职责）
- `knowledge/decisions/91-project-bot-autonomous-coordination.md`（复用自主协调与有界独立重验上限）
- `knowledge/decisions/110-follow-up-responsibility-and-current-list.md` & `124-legacy-stop-obligation-controlled-resolution.md`（唯一 `followUp` 投影与隐藏 `obligation_indexed`）
- `knowledge/specifications/peer-product-experience-standard.md`（Peer Frost v1 体验红线）

## 背景

ADR 84 将桌面壳层收敛为「左栏 Bot 列表 + 主区 Bot 对话 + 按需右侧档案抽屉」，并在后续迭代中增加了右侧「工作现场（`BotWorkPanel`）」。实际使用中暴露出三类结构摩擦：
1. 任务详情被挤压在右侧窄栏内，查看计划边界、代码 Diff、核验回执与审批内容过于局促；
2. 跨 Bot 查看多个活跃任务需要反复切换 Bot 并打开右侧面板；
3. 历史任务与输入心流割裂，既容易打断当前对话阅读，又无法把某条历史任务直接 `@ 引用` 进正在编写的输入中。

## 决策

1. **左侧栏引入「Bot → 当前任务」两层轻量结构**。
   - 外壳维持 Peer Frost「冷灰 Chrome 侧栏 + 16px 圆角浮起阅读纸面」。
   - 侧栏顶部收敛为精简工具带（侧栏收起、`⌘K` 全局快搜、真实前进/后退导航）与 `Bots +`。
   - 展开的 Bot 下方默认显示最多 **3 条**活跃任务（支持原地展开/收起其余项），仅消费宿主投影的 `followUp.inCurrentList == true`（排除 `obligation_indexed`），按 `owner == 'user'` > `verification_failed` > 运行/核验中 > 排队中排序。
   - `BotListItem` 增量携带宿主一次投影出的 `activeSessions`、`activeSessionTotal` 与 `historySessionTotal`，避免前端展开多 Bot 时产生 N+1 查询。
2. **主区全宽任务工作台 + 按需右侧证据抽屉**。
   - 从侧栏、对话卡片、Touch Bar、`⌘K`、通知或「需要你」点击任一任务，主区切换为**全宽任务工作台**，顶部显示由宿主 `anchorMessageId` 绑定的来源回链（一键返回原对话并恢复草稿与阅读位置）。
   - 证据与核验依据默认隐藏，按需从右侧滑出 **Evidence Inspector**（宽窗推开，窄窗磨砂覆盖），底层复用只读 `readEvidence` 边界。
   - 原默认常驻的右侧「工作现场（`BotWorkPanel`）」退场；`BotProfileDrawer` 收敛为纯 Bot 档案与配置抽屉（概况 / 目标 / 记忆 / 设置）。
3. **输入框一体化动态 Touch Bar（就地向上展开）**。
   - Touch Bar 与 `BotComposer` 物理融合为同一 Frost 胶囊，不破坏输入预测、IME 守卫、附件、授权模式与模型选择器。
   - **Bot 对话态**：左侧为可点击的实时状态汇总（点击向上展开「进行中的任务」磨砂托盘）；右侧仅保留「历史任务 N」（点击向上展开「历史任务」磨砂托盘，支持服务端防抖筛选、分段状态过滤、时间分组与游标加载，不清空背后对话与输入草稿）。
   - **结构化 `@ 引用` 历史任务**：在历史托盘悬停点 `@ 引用` 将合法的 `taskRefs` 写入既有持久化草稿（`InputDraftValue.taskRefs`）；提交 `submitInput` 时宿主校验每个 `sessionId` 隶属当前 `workspaceId` 并把结构化摘要注入 Bot 轮次上下文。
   - **任务工作台态**：Touch Bar 随权威 `followUp` / 审批状态动态变形，遵循 Frost「单局部决定唯一石墨主 CTA」红线：待批准提供「核查范围 / 拒绝 / 批准计划」；运行/核验中提供「证据 N / 停止」（对齐宿主 `cancelSession` 停稳回执，不造假暂停）；`verification_failed` 提供经 `project.bot.verifySession` 触发的有界独立重验（复用 ADR 91 最多 3 次上限与租约围栏）；历史任务提供「证据 / `@ 引用回对话` / 基于此重跑（仅预填草稿，不静默执行）」。
4. **严格保留的边界**。
   - 维持 ADR 80「1 项目 = 1 主 Bot」与 ADR 84 不做模板市场。
   - 列表与计数唯一消费宿主 `followUp`，禁止前端另建状态白名单；`obligation_indexed` 继续对用户不可见。
   - 任务页追问走主 Bot 规范输入队列（绑定 `taskRefs` / `answerTo`），不绕过主 Bot 直接向无权 Worker 写入。
