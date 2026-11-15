# 交互优先与大日志恢复实施计划

创建时间：2026-10-22
最后更新：2026-10-22
状态：本轮源码实施与回归交付完成；已回写日常代码仓，当前运行实例与真实数据根未切换。
级别：A；决策见 [ADR104](../../knowledge/decisions/104-progressive-interaction-and-coordination-storage.md)。

## 1. 任务与退出条件

保留现有任务、用户交互、执行过程和 Evidence，消除高频全量协调快照造成的写放大；使大日志恢复不阻断主会话；主 Bot 按交互 → 相关任务摘要 → 指定报告 → 指定过程 → Evidence/受保护恢复状态渐进读取。

“完成”须同时满足：新写入近似线性增长；旧大日志能安全恢复；普通对话不深读子链；协调失败不隐藏消息；原任务身份/用量/权限/送达/证据对账通过。不能以提高内存、分块读取一个大文件或前端分页单项通过作为整体完成。

## 2. 开工基线与范围

- 先批准 ADR104，再实施。当前共享工作区两仓均有其他在制成果；实施从包含所需成果的隔离副本/合适 worktree 开始，保留源提交及 dirty fingerprint，不覆盖、stash 或提交他人的文件。依赖未合入时逐 hunk 标明来源，不默认为当前 HEAD 已含全部成果。
- 默认不动正在运行的宿主，不写真实数据根，不安装/发布新版。使用临时数据根和 dev:lab；复制诊断样本时排除凭证、限制本地权限，不把用户历史发送到真实 Provider。
- 不新增依赖、顶层 package，不扩大主 Bot 写权限，不调整模型/费用政策，不改变 ADR95/103 的进展治理、ADR97 原生恢复或 ADR102 生命周期结论。
- 生产文件只允许下列各阶段列出的 Module、关联 protocol/preload/data-store 注册、对应测试与产品回归夹具。main.mjs 仅装配替换，净增不大于 0；ChatSurface 等大组件不加业务逻辑。
- 涉及新增存储、typed IPC、语义命令或格式兼容先补具体 schema 和失败规则，再改调用方；不得用无类型参数临时贯通。

## 3. 分阶段实施

每阶段是一张可独立审阅的子卡，按依赖顺序实施。前一阶段未通过退出条件，后一阶段不在真实数据上激活。

### S0：冻结复现与数据保留基线

范围：诊断/测试夹具与测试脚本，尚不改用户可见行为。

1. 保存本轮 809 MiB 日志的本地只读统计回执与源 hash；生成可公开、无私人内容的等价大日志，包含相同全量快照增长模式。
2. 生成父交互与大 agent_turn 混排、多个子会话、结果/人工问题、native checkpoint、未结算调用、prepared/delivered 回复、显式预算和暂停/取消夹具。
3. 先红测试覆盖：整文件字符串超限；坏协调卡片隐藏正常消息；首屏/普通回合深读；用量去重表导致快照二次增长。
4. 建立保留清单：文件 hash、所有稳定 ID 与引用、每 work 的最终计数/未知标记/待决调用、事件及回复回执。

退出：原代码真实复现目标缺陷；夹具不依赖模型或真实用户文件，也不把设计指标当已测结果。

### S1：先恢复聊天可用性与大文件读取能力

允许改动：runtime-node 的 coordination-journal-reader/legacy recovery adapter、只读 SQLite 投影、readiness 与 data-store 注册、project-facts、bot-directory；Desktop project-agent application service、typed preload/协议、useBotConversation/conversationPager、BotConversation 及局部状态/i18n；对应测试。

1. v1 journal 分块读与跨块解码；重建移入共享 runtime 的 worker seam，验证 revision/schema/源身份，进度及错误可观察。worker 在 readiness 边界发布只读派生投影，ready 后短时同步查询满足既有 Guard/Store 时序，不能让同步 read() 悄悄改成 Promise。v1 写路径及累计计数语义暂不变。
2. readConversation 消息正文与 cards 分开返回/刷新，先发布父交互页，协调读取不再成为消息成功的前提。
3. 分离 messages/cards/workSummary/details 的可用性；刷新失败保留旧消息、草稿和锚点，局部重试。无旧页时显示真实失败。
4. 执行方仍等待本项目权威恢复，不将 UI 可读冒充宿主已恢复；其他项目独立工作。

退出：至少 1 GiB 日志不会触发整文件转字符串；坏协调日志下交互可读；未知状态不显示正常运行；工具/权限/签收和未知派发保护不变。此阶段是可用性修复，仍未解决新写入放大。

### S2：把交互与子链路分层落实到查询和上下文

允许改动：conversation-store 的公开交互索引/分页与投影 reader；runtime-node 的 Project Facts、SessionSupervisor 查询、agent-turn-plan/runner 所需读端口；system-context/project-roster source；Desktop/TUI 装配、protocol/preload 与 data-store 注册；对应测试。

1. 定义 InteractionPage/InteractionContext、任务摘要/报告/过程页和 QueryAvailability；来源版本、字节预算与稳定游标纳入 Interface。
2. 建立 cache/read-models/interaction 派生索引，canonical commit 后追增量，旧父历史后台重建；保留 sidecar 排除、contentRevision、附件与旧格式兼容。
3. Desktop executeTurn 使用公开交互查询；TUI 使用同一 seam。当前用户边界、引用、未答问题与公开回复进入既有 history/continuity；不主动加载全部 agent_turn、子会话或恢复检查点。
4. 相关任务先筛选 ID，再查摘要。结果/失败/问题事件只准入本轮相关信封；既有 Context Source 负责事实准入，规则顺序不改。
5. 调查时沿现有工具读取单任务报告、单过程页、单 Evidence；query/body 边界由 Provider/Projection 强制，而非只加 prompt。
6. 恢复候选与 canContinue 读取紧凑元数据，实际恢复选中后才加载可靠 native checkpoint；权限执行仍实时重检。

退出：spy 证明首屏、普通回合上下文准备的子会话正文/历史 journal 回放/checkpoint/Evidence 正文读取为 0；命令准入/追加对当前 head 和增量尾部的必要读取单列。十倍无关历史不扩大读取集合；引用定位、结果交付、真实人工门、原生恢复和工具结果配对通过。

### S3：增量事件存储与精确回执索引

允许改动：protocol 的版本化事件/回执/恢复状态；runtime-node 的 Coordination Store、reducer/kernel、work-budget、reader/segment/worker、reply delivery 和 checkpoint 引用；现有 SQLite seam；Desktop/TUI 适配；对应测试。

1. 在现有 Store 内实现 v2 Adapter 与分段事件文件；保留 Legacy Adapter。先定义 semantic events 和 reducer，不开放通用字段 patch。
2. WorkBudgetGuard 各持久边界改为小事件；usage 去重、调用预留、结算、checkpoint 引用、进展窗口和完成分开更新。WorkHead 不携带累计 observations。
3. 精确 receipts 与 work/candidate/delivery/mandate 查询放可重建 SQLite 投影；日志 fsync → transaction apply → receipt/通知的顺序及 durable_pending_projection 明确实现。
4. 迁出 read().works 全量消费路径，预算与恢复用按身份查询；审计显式分页。段轮转保留旧段，不做自动历史删除。
5. 对每个崩溃窗口做生产 Store 子进程强杀；重启返回同一回执，不重复用量、任务、工具副作用或公开回复。

退出：固定形状 1,000/10,000 事件体积增长 ≤12 倍；没有每次重写累计集合的新路径；显式预算并发/未知用量/取消/version guard/lease 全部保持；真实 Tool Result 和 Evidence 留存。

### S4：存量导入、对账与版本激活

允许改动：共享 runtime 的 migration/fence/recovery adapter、data-store 注册/说明、Desktop/TUI host 启动装配、诊断导出、对应测试。

1. legacy 只读分块导入，保留 v1 全文；累计计数按快照覆盖，精确提取旧 observation、operation、delivery 与未知调用身份。
2. 暂存 generation 全量对账；旧原文 hash、任务与引用不变。发布激活 manifest 前不得进入 v2 写路径。
3. 在既有 lease 下安全点切换、fsync/rename 原子激活；后续只写 v2。激活前/后重复运行、磁盘满、强杀、部分尾、内部损坏、writer 竞争分别验证。
4. 有效派生库启动只追尾部；库缺失/损坏后台重建，不能以空库准入。故障恢复不调用模型、工具或外部系统来补历史。
5. 明确最低读写版本与降级限制；新契约支持者强制检查，不宣称旧二进制认识新 fence。激活后不能回退旧快照继续执行；不双写全量 v1。

退出：脱敏等价大历史以及用户数据的本地隔离副本均完成结构与 hash 对账；所有任务保持原身份；已完成动作/回复不重放。原日常数据仍未改动。

### S5：整体回归、性能与隔离构建交付

允许改动：必要验收脚本、产品回归夹具、构建验证脚本与知识仓交付回执；不因验收扩张产品范围。

1. 构建受影响包后跑定向、完整包、typecheck、architecture、IPC；Desktop/TUI 两宿主共享同一 v2 事实与接管规则。
2. 生产路径测量写字节、事件大小、重建 RSS、冷/热读取、主进程 long task、恢复读取字节及实际续接；指标见 ADR104 §8，不只测 helper。
3. 标准产品 `pnpm qa:product:capture --output <仓外临时目录>`；逐张检查必需截图并写具体 review.json；`pnpm qa:product:verify --output <同目录>`。
4. 本地私有历史只做只读隔离测量。真实模型用合成工作区，经主 Bot → 子任务 → 工具/Evidence → 验证 → 正式回复；证明日常上下文不包含无关子链。Provider 请求记录做脱敏，不记录/上传私有全历史。
5. 冻结源码指纹后构建独立包，检查 asar 模块身份、打包运行时 SQLite/worker 支持、同任务升级恢复夹具；未验收安装升级就明确写覆盖缺口，不替换当前客户端。

退出：交付源版本、每卡 diff/测试、数据对账、性能与产品 review/verify、独立测试包路径及限制。明确 independent=false（若实施者自审），真实模型、安装版和无障碍范围分别记录。

## 4. 验证命令与必要用例

实施时按实际新增文件定位精确测试命令，先构建依赖 dist，再执行：

```bash
pnpm build
pnpm --filter @peer-agent/conversation-store test
pnpm --filter @peer-agent/runtime-node test
pnpm --filter @peer-agent/system-context test
node --test packages/protocol/src/*.test.ts
pnpm --filter @peer-agent/desktop test
pnpm --filter @peer-agent/tui test
pnpm --filter @peer-agent/desktop ipc:check
pnpm typecheck
pnpm architecture:check
```

大日志内存/时间对照在隔离子进程串行测量，不能与全仓并发测试混在同一指标；一次既有计时取消可单文件复验，持续失败算回归。跨进程损坏、乱序用量、回执丢失、部分尾、selected native checkpoint 和迁移强杀都必须有有意义的断言，不以 stub 永远成功代替生产恢复。

## 5. 分段交付与回退

- S1/S2 可先交付读取隔离与交互查询，不等待 v2 才让对话恢复可用；但不能据此宣布写放大已修复。
- S3/S4 先在隔离数据启用并完成迁移对账；旧格式宿主继续运行时不后台切换真实文件。
- 激活前可退回旧 reader；激活后只在兼容 v2 的版本之间回退，保留源日志与新事件。原 v1 原文可取证，但不再代表最新状态。
- 不自动取消任务、清空 budget、重新开工、删除 Evidence 或重装当前应用。安装/发布不是此卡默认动作。
- 按修改归属提交：代码在 Peer-Agent，设计/交付事实在 Peer-Knowledge；只提交本卡内容，commit 后同轮 push，不把其他在制成果带入。

## 6. 当前交付事实

2026-10-22：S0–S4 源码与本轮 S5 回归已完成。52 个本卡文件已按基线逐文件核对后回写日常 Peer-Agent 仓库，无冲突；原有在制修改（含期间另行修改的 9 个样式/测试文件）全部保留。回写后从原仓库再次运行产品 verify，通过同一个源码指纹。未提交其他在制成果，未重启、安装或替换当前运行实例，未在真实数据根激活 v2。

已实施：公开交互索引/异步读取与 Desktop/TUI 共用查询；主 Bot 默认只取公开用户输入及正式回复；相关任务摘要先筛选再投影，单选过程按 canonical 偏移读取。界面消息、任务卡、详情故障隔离，刷新失败保留原消息，首次失败明确显示并可重试。协调 v2 使用差量分段日志、精确 usage 回执与可重建 SQLite 缓存；worker 导入保留 legacy 原文，head、哈希链、lease 和来源版本共同约束恢复。

最终验证：

- 最终完整 `pnpm build`、`pnpm test` 均退出 0。Node 7,911 项：7,906 通过、5 跳过、0 失败/取消；TUI Bun 764 通过、0 失败。测试包和 Node 测试文件串行运行，未放宽断言或超时。之前一次并行负载下的 TUI 15 秒超时已保留诊断；本次完整串行重跑无失败，不以局部测试拼成最终通过结论。
- 最终 Runtime 1,420、Conversation Store 106、Renderer 1,901 项均纳入全仓通过；故障定向 19/19，产品门禁单元测试 6/6。typecheck、architecture、Desktop IPC 检查通过。Node/Electron 源码构建和 Bun 单文件 worker 重建烟测通过。
- 完整产品 capture 覆盖 200 bots / 10,000 messages / 100,000 events / 10,000 memories；205 张必需截图逐张检查并绑定 hash。`review.json` 为实现者自审，`independent=false`。从隔离工作区与回写后的原仓库执行 verify 均 passed；无未解决阻断项。
- 产品回归 runId：`6ecf3ff2-6cc1-42db-ac74-23b03ae7b84e`；源码指纹：`0a55af5ce1d8f49ce9c4127f1acdc6eb70a7b815ece6b45b5cb62a55fac8a0c5`。本地完整回执为 `product-layout-final/{packet,machine,review,result}.json`，汇总为 `verification-results.json`，全仓日志为 `test-handoff-final.log`。
- 真实 848,647,853 字节旧日志副本恢复约 2.439 秒，9 个 work / revision 8,593 与 v1 reducer 完整最终状态深比较一致；1 GiB 合成日志恢复约 2.937 秒。真实原日志 SHA-256 与隔离恢复副本仍相同，真实原对话 SHA-256 与读取基准前相同。原安装进程 PID 8352、启动时间保持不变；校验仅为只读比较。
- 固定 usage 事件从 1,000 到 10,000 次，journal 从 347,172 到 3,488,174 字节，增长 10.05 倍；metadata 最大 386 字节、p99 349 字节，精确 tokens 10,000。该指标是用量元数据 journal，不是整盘物理写入或所有 Evidence 的体积。
- 真实对话查询冷读约 27.73 毫秒、热读 p95 1.11 毫秒；模型公开交互结果含 25 条公开消息、0 个私有 turn，原对话字节未改写。大日志内存与事件循环指标、OS 缓存限制见 ADR104 §9。

验收中修正了完成 turn 到公开 reply 的详情锚点、异步问题卡与自由输入的关联、窄窗切换时回复详情入口沿用旧测量宽度的问题。保留原焦点、阅读位置、悬停、键盘及溢出断言。窗口夹具在既有 15 秒上限内检查当前动画集合，避免等待截图重置前的旧 Animation.finished promise；共享 UI 断言严格匹配已变更的 radius token，不回退产品样式或跳过场景。

覆盖边界：受控认知与真实本地 Runtime/PermissionGrant/Evidence；不是云模型质量、当前安装版、跨平台发行或完整读屏验收。Quick Chat 的 macOS 半透明材质 PNG 包含透明像素，已检查原图及浅底合成预览，原生桌面最终合成仍需安装版使用验收；记录为 minor accepted-limitation。单 canonical 记录上限 64 MiB、过程读取粒度为单 turn；更细轮次分页、tokenBudget 和超大公开正文分片仍是 ADR104 记载的后续 Interface，不宣称本轮全部实现。

激活边界：本次交付为源码。当前运行中的已安装应用继续使用原构建与数据；后续新构建获得现有 lease 后才走已验证的恢复/激活路径。v2 激活后不得用不认识 v2 的旧二进制继续写入；保留 v1 原文用于取证，不能把它当作最新执行状态。
