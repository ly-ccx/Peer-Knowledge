# Peer 代码结构、模块与加载路径审查

创建时间：2026-10-28
最后更新：2026-10-28

状态：只读审查及重构建议；本轮没有修改运行时代码，没有新增架构决策或宣称性能修复完成。

关联：[工程结构](../architecture/01-project-structure.md)、[架构治理](../architecture/20-architecture-governance.md)、[历史性能治理](multi-task-ui-performance-remediation.md)、[ADR 104](../decisions/104-progressive-interaction-and-coordination-storage.md)、[ADR 111](../decisions/111-project-agent-duplex-supervision-and-continuity.md)。代码路径均相对 Peer-Agent 根目录。

## 1. 判断

需要围绕加载边界、订阅所有权和少数运行时热点做分阶段重构。现有 apps/packages 的总体分层和统一能力链继续保留；没有证据支持全仓重写、换框架或按行数平均拆文件。

最先处理两件事：功能没有显示时仍进行的查询/投影，以及不需要某项功能时就加载其完整依赖。这两项更直接关联切页和点击体验。随后拆出 GoalPlan/GoalRunner 的纯领域决策与存储/执行边界，再推进 ADR 111 的监督功能，避免把新责任继续塞进同一批大闭包。

本次静态证据不能证明整个应用卡顿由某个文件或单一加载问题造成。持续卡顿还可能涉及主进程 I/O、渲染/GPU、数据规模与系统内存压力，需要在同一最终候选上测量。不能把按需加载的收益外推成运行中卡顿已经解决。

## 2. 方法、范围与限制

- 源码基线：HEAD `b6e8fe88c90fc56677a404c641c0978da6a64f92`，分支 `PeerAgent/tui-desktop-goal-contract-shared`，包含未提交改动。统计针对读取时的工作区，不等于该提交、已安装版本或发布候选。
- 清单来自 Git 已跟踪及未被忽略的新增文件，范围为 apps、packages、crates、scripts、examples、marketplace 下的 TS/TSX/JS/MJS/CJS/MTS/CTS/RS/CSS/SCSS 等代码。排除 node_modules、dist、target、coverage 和实验目录；不把锁文件、Markdown 提示词与构建输出计入源码行数。
- 行数为物理行，含注释和空行。实现/契约及工具脚本、测试/夹具/性能代码、样式、生成文件与声明文件分开；分类为路径/头注释启发式，不能充当精确业务规模或测试覆盖率。
- 使用已有 TypeScript 5.9.3 parser 做只读语法树分析，区分显式 type-only import 与值 import，统计静态/动态依赖、闭包跨度和 Hook 调用。没有执行应用模块、类型检查或构建。
- 源码依赖图按相对导入和工作区源码入口近似解析，不模拟打包器的 tree shaking、TS 隐式类型导入消除、条件导出或运行时求值。可达数量表示耦合范围，不是精确首屏执行模块数。
- 仓库现有 dist 来自 2026-10-21，身份未绑定本轮源码，仅作旧产物观察。没有为审查重新构建或把它当成安装版。

## 3. 规模与分布

共发现 15 个工作区包：3 个 apps、12 个 packages。

| 分类 | 物理行数 |
| --- | ---: |
| 非测试实现、契约及工具脚本 | 256,255 |
| 测试、夹具与按目录识别的性能代码 | 156,878 |
| 样式 | 34,790 |
| 识别出的生成文件 | 1,556 |
| 独立声明文件 | 580 |

非测试实现/契约/脚本共 1,434 个文件，其中 1,091 个不超过 200 行（76.1%），28 个超过 1,000 行，11 个超过 2,000 行。问题集中，不能据少数热点认定所有 Module 都需要拆分。

| 区域 | 非测试实现/契约/脚本文件 | 对应行数 | 判断 |
| --- | ---: | ---: | --- |
| Desktop Renderer | 471 | 72,914 | 聊天、旧壳、新 Bot 壳、工作台并存，加载与订阅边界需要收敛 |
| Desktop Electron main/preload | 335 | 60,290 | 有 IPC/application service 分层，但入口与聊天服务仍集中 |
| runtime-node | 250 | 50,534 | 共享价值明确，GoalPlan/GoalRunner 与总出口是主要热点 |
| TUI | 99 | 22,752 | 同时保留经典/项目入口，命令分流前的加载顺序需调整 |
| protocol | 41 | 9,012 | 保留统一契约与纯投影，不能把职责拆回各 UI |
| runtime-core | 26 | 6,539 | 核心领域层继续保留 |
| system-context | 38 | 4,023 | 既有 Source/Assembler seam 应复用 |

区域只展示主要部分，不能与分类总数直接相加。Desktop/TUI 中还包含开发工具脚本；这些数字不是安装包体积。

## 4. 需要重构的具体位置

### 4.1 首屏与功能加载边界：优先级高

`apps/desktop/renderer/src/App.tsx:4` 起静态引入 SettingsPage、CapabilitiesPanel、AutomationCenter、经典 ChatSurface、新 BotListShell 和工作台。SettingsPage 又静态引入各设置分区。当前 Renderer 语法树扫描只发现一处字面量动态 import：`app/state/openWorkbenchConversation.ts` 中的 clientApi；没有发现页面使用 React.lazy/Suspense。

源入口近似静态可达 496 个本仓模块、87,892 行。这个数字不包含第三方依赖展开，也不能直接解释为全部代码会在首屏执行，但说明源码尚未建立有效的页面加载边界。

`chat/components/markdown/codeHighlighter.ts` 静态引入 core 和 31 个语言定义。语言注册函数已经延迟到使用时调用，仍需区分“延迟注册”和“语言模块没有提前加载”。

`renderer/src/styles.css` 集中导入 37 个样式入口。旧 dist 只有一个 JS 业务 chunk（1,756,156 字节，gzip 527,732 字节）和一个 CSS（872,941 字节，gzip 125,852 字节）。这是旧产物的实数，不是当前源码重建结果，不能据此承诺拆包后节省多少时间。

**建议**：在设置、能力中心、自动化、按需工作台/预览等真实功能边界引入加载 seam；再拆设置分区与不常用高亮语言。基础 shell、tokens、输入恢复和关键状态反馈保留及时可用。按真实功能使用动态 import，并处理加载/失败/重试；仅增加 manualChunks 而保持入口全部静态依赖，不能获得同等按需收益。

### 4.2 隐藏页面仍保留订阅与完整查询：优先级高

`App.tsx:988` 的聊天/Bot 层在设置页打开时通过 aria-hidden/inert 保持挂载。保留挂载有助于草稿、焦点和阅读位置连续，不能简单全部卸载。

但 `project-agent/BotListShell.tsx:97` 的 useBotList、`:132` 的 useBotWorkSessions 仍运行。`state/useBotWorkSessions.ts:15` 订阅 Bot 事实与消息事件，每次匹配变化重新请求 sessions，并以 JSON.stringify 比较完整 sessions；该 Hook 没有可见性参数。`state/useBotList.ts` 同样订阅两类变化，已有 80ms 合并与按 workspace ID 刷新，仍通过完整目录序列化比较结果。

**建议**：保留界面连续性，把事实订阅/缓存与视图刷新分开。仅保留当前确实需要的轻量摘要；隐藏详情暂停昂贵查询并记录 dirty/version，恢复可见后补增量。共享同一工作事实读取，按 workspace/session/revision 选择性更新，避免深序列化作为普遍的变化检测。停止、权限与真实人工事项的关键送达不能被可见性策略吞掉。

这是已确认的额外工作路径，不是已测量的本次卡顿占比。也不能通过停止后台任务或拉长轮询掩盖问题。

### 4.3 少数大闭包混合领域、存储与交互：优先级高至中

| 文件 | 行数 | 有证据的职责/建议拆分边界 |
| --- | ---: | --- |
| `packages/runtime-node/src/goal-plan-store.mjs` | 4,906 | 同时包含 JSONL/原子写、normalization、计时/进度、Explorer/Verifier 报告、Evidence 索引、UI 完成与验收调用；先分纯领域规范化/变换、Evidence 查询、持久化 repository seam，外部 store Interface 保持稳定 |
| `apps/desktop/electron/main/main.mjs` | 3,790 | 153 个静态依赖；已有 composition root/IPC service，但仍有模块顶层 store/订阅创建及 OAuth 等具体实现；按现有 owner/start/dispose seam 迁出完整职责 |
| `apps/desktop/renderer/src/chat/components/ChatSurface.tsx` | 3,316 | 70 个值依赖；22 处 useEffect、4 处 useLayoutEffect、19 处 useState；将发送/队列、草稿/附件、滚动/选区、目标与权限展示按行为 seam 收束，避免把一个大组件原样搬成大 Hook |
| `apps/tui/src/app.tsx` | 3,244 | 经典终端壳与大量回调/状态集中；按路由、交互控制与共享运行态适配拆分，保留已有项目壳 |
| `packages/runtime-node/src/goal-runner.mjs` | 2,796 | pump 函数跨度 901 行；集中执行阶段、Explorer/Verifier、恢复与治理；纯阶段决策与实际副作用执行分离，使用既有共享控制 seam |
| `apps/desktop/electron/main/llm-chat-service.mjs` | 2,484 | sendMessage 跨度 878 行；有现成 provider encoder/loop/permission seam，继续缩小会话准备、运行、终态提交的职责，而非再加一个独立聊天执行器 |

函数跨度包含内部函数/闭包，不等于单一算法的圈复杂度。本审查没有覆盖率，因此不计算 CRAP 或假称某函数达到 Skill 的 CRAP 阈值。

拆分必须让调用方少知道实现细节，集中顺序、错误、权限与恢复契约。把 4,900 行分成十个相互访问共享可变闭包的文件不算完成。优先从纯变换和稳定查询接口开始，不首先迁移持久格式。

### 4.4 总出口让小调用牵入宽依赖：优先级中

`packages/runtime-node/src/index.ts` 为 649 行、160 个值 import/re-export 依赖。package.json 除 testing 外主要暴露根出口。根出口近似静态可达 310 个本仓模块、66,568 行，并可达 MCP、Qoder SDK 等依赖；其中 `provider-adapters/qoder-official-model-catalog.mjs:3` 确实静态引入 Qoder SDK。

Node ESM 根出口的 re-export 图不能默认享有浏览器打包器相同的按需消除。只需要一个恢复/路径 helper 的入口，也可能因此关联整个能力集合。图分析不证明 SDK 已建立连接，也不量化初始化耗时。

**建议**：在同一 package 内形成稳定子路径出口，例如 project-agent、storage、providers、models；为非必要 SDK 使用适配器内受控加载。保留根出口兼容既有调用，关键入口逐步迁移。不要为了导入粒度立刻创建许多新顶层 package，也不要将内部文件路径变成长期公共 API。

### 4.5 TUI 命令分流发生在重加载之后：优先级中

`apps/tui/src/index.tsx:10–26` 在检查版本/帮助/exec 参数之前，先 await import OpenTUI、App、cli-exec、tui-runtime；`:34` 后才处理相应命令。即使使用了动态 import，调用位置过早仍会阻塞轻命令。

**建议**：轻量 argv/help/version 分流先完成，再进入各模式的加载边界；终端 UI 只在交互模式加载，exec/ACP 保持自己的必要依赖。静态依赖也需检查，源文件把 if 写在顶部不保证依赖图尚未求值。实际 Bun 二进制的启动收益另行测量，本轮没有运行这些命令验证延迟。

### 4.6 明确的局部清理：优先级低，可随触及修复

`apps/desktop/electron/main/usage-request-log.mjs:15` 引入 usage-stats 的 estimateUsageCostUsd，后者 `:10` 又引入 createUsageRequestLog，构成一组直接值依赖环。可把纯费用计算抽成无 I/O 的 pricing Module，日志与聚合共同依赖它。当前没有证据表明该环已触发初始化错误。

该日志 `readAll({limit})` 在先 readFileSync 全文件后才截取尾部，limit 不限制磁盘读取/解析前的工作量；usage-stats 最高请求 200,000 条。应按数据读取契约改成有界尾读/增量统计，不能只缩小返回数组假称查询已变轻。此问题与该依赖环分别处理，不混成一个“拆文件就变快”的结论。

## 5. 应保留的结构

- 工作区声明依赖没有发现包级环；发现的源码值依赖环仅为上述近似图中的一组，不能将此结果当成完整 bundler/运行图证明。
- protocol → runtime-core → runtime-sdk/runtime-node 的职责仍清楚；System Context 有独立 Source/Assembler。不要为优化代码规模把权限、Evidence 或 followUp 真值搬到 Renderer。
- Desktop 的 `electron/main/goal-runner.mjs` 已是 runtime-node 的共享再导出，不能再按历史文档认定 Desktop/TUI 各自复制 GoalRunner。对 TUI/package 源码的直接 Desktop 实现路径搜索没有发现匹配；动态/生成依赖不在该搜索证明范围。
- project-agent 已有 135 个非测试实现文件、19,513 行；其新 Renderer 区域 109 个文件、9,590 行。大量职责已经拆出，应复用现成 seam，避免在监督功能之外再建立一套监督 store/scheduler。
- coordination-v2 已有增量日志/派生索引与 Worker 重建代码；GoalPlan 也有 JSONL 缓存。不能声称当前所有读取都全量阻塞。需要把剩余调用迁到既有轻量查询，而非不加区分地再做一次存储重构。
- `packages/i18n/src/index.ts` 虽有 4,193 行，主要是文案数据；它不与 GoalPlan store 的职责复杂度等价。文案可以按领域组织，但优先级低于实际加载、I/O 和状态所有权。
- packages/ui 和 task-thread 仍很小，不表示应把所有现有 Frost 组件搬进它们。共享组件的规范与实际消费者先对齐，保留仍在使用的兼容面，避免目录整齐但依赖更乱。

## 6. 建议实施顺序与验收依据

| 顺序 | 独立工作包 | 架构影响 | 可核对的结果 |
| --- | --- | --- | --- |
| R1 | 可见性与增量事实读取 | B；沿既有 host/query/reducer seam | 隐藏详情不重做完整查询；恢复可见不丢最终事件、用户问题或阅读位置 |
| R2 | Desktop 功能按需加载、TUI 轻命令分流 | C/B；若触及 IPC/宿主生命周期则按 B | 不常用功能不在首屏必要依赖中；加载失败可恢复，草稿/焦点不回退 |
| R3 | GoalPlan 领域/存储、GoalRunner 决策/执行分离 | B；改变存储/权限/Evidence 契约升级 A | 外部 Interface 与事实结果保持一致，领域判断集中、未知副作用不重放 |
| R4 | runtime-node 子路径、Desktop 启停所有权收束 | B；新增公共边界按 A 审阅 | 小调用不默认牵入无关 Provider；每个资源 start/dispose 有明确 owner |
| R5 | 按 ADR 111 实施监督闭环 | 沿已接受 A/B 设计 | 责任投影同源，可靠消息/续接回执成立；不增加第二套任务引擎 |

每包独立交接，避免先做一次全仓搬家再等所有功能适配。R3/R4 可以按真实消费者逐步迁移，与 ADR 111 共享热点的变更明确排队；不强制把所有重构作为修复一个缺陷的前置。

普通开发遵守当前 AGENTS：实现与内容/diff 审阅，不自动运行测试、构建/类型/架构/IPC 或截图回归。行为保留场景与必要测试代码随任务定义；执行这些检查留到发布，除非用户明确要求提前验证。Skill 的 TDD/工具建议不能覆盖用户的验证时间约定。

发布需在全部开放 PR 正常合并后的最终候选上，执行完整检查与产品回归，并补充首屏/首次切页/热切页、隐藏页查询次数、事件循环停顿、IPC 载荷和模块加载耗时的前后对照。源码依赖减少不等于这些性能指标已经通过。

## 7. 审查行动记录

| 动作 | 目的与结果 |
| --- | --- |
| 读取并安装 [ub-mode](https://github.com/unclebob/ub-mode/blob/master/SKILL.md) | 经内置 skill-installer 安装 master 根目录 Skill；实际包含 SKILL.md/README，没有附带 crapper/dryer/mutator 工具；本轮手动读取，下一轮自动发现 |
| 读取两仓规则与工程/产品基线 | 按既有统一能力链、深 Module、知识归属和验证时间约定评价，不另立框架 |
| 读取 Git 清单与包声明，分组统计 | 区分源码、测试、生成内容和样式，保留当前在途改动 |
| 使用已有 TypeScript parser 静态分析 | 排除显式 type-only 导入，检查值依赖、模块可达、闭包跨度与 Hook 分布；未运行类型检查 |
| 阅读入口、订阅、store、runner、Provider 与 composition root | 把行数与真实职责、加载时机和生命周期对上，保留已完成的共享/增量机制 |
| 读取旧 dist 字节数与压缩体积 | 只记录现存 2026-10-21 产物，不构建、不冒充当前版本体积 |
| 写入本报告并做内容/引用审阅 | 将建议和事实分开，运行时代码、用户数据与运行实例均不改；没有运行测试或变异测试 |

只读统计脚本和完整临时数据留在仓外审查目录，不向代码仓引入审计依赖。未清理 worktree，未创建提交、推送或发布；安装 Skill 不等于安装其提到的分析工具。


## 2026-10-28 后续实施

用户随后授权按上述顺序完成 R1–R5，并明确要求自测后提 PR。源码范围、静态对照、架构迁移与实际自测范围登记在[实施回执](../../playbook/v0.1.0/code-structure-refactoring.md)。本报告前文仍保留实施前审查现场，不把其只读状态、旧产物体积或行数当作后续候选的性能实测。
