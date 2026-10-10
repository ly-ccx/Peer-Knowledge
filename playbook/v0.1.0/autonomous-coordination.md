# R91：主 Bot 自主协调与取消重派

创建时间：2026-10-10
最后更新：2026-10-10

负责人：用户。设计依据：用户要求并行自主调度，并明确主 Bot 可识别补充/纠正、取消错误执行和重派；[ADR 91](../../knowledge/decisions/91-project-bot-autonomous-coordination.md) Accepted。

状态：实施中。2026-10-10 用户明确授权“按照这个思路来实施”；按 R91-01 至 R91-05 顺序推进。已推送 ADR 91 / 知识 PR #33 是本次批准的设计依据，允许从已合入 RC11 的 clean HEAD 建逐卡堆叠 PR；后续卡可沿前卡已推送提交继续，合入时按依赖顺序。实施授权不等于测试或发布完成，不自动合并或发布 RC。

级别：A/B/C。依赖：已发布 RC11 的 ADR 88/89 连续执行与双向通信、现有能力代理链、宿主租约、GoalPlan、验证与结果政策。

代码核实基线：Peer-Agent `438d1a6f52853ff55031fb351cb14625de554514` / `v0.1.0-rc.11`。实施从当时最新 `PeerAgent/dev/0.1.0` clean HEAD 建专用分支，不覆盖用户在制改动；不用旧主工作区 HEAD 代替已发布源码。

## 1. 目标

主 Bot 及时接住新要求，自主决定补充、修订、并行、取消、替换和接手。多个独立工作 Agent 持续执行；后台事件能在原目标范围内推动工作，用户无需反复处理内部调度或取消确认。

## 2. 必读与边界

代码仓 AGENTS.md、知识仓 AGENTS.md、工程治理、产品北极星、执行手册、卡总目录、ADR 80/82/85/88/89/91，以及本卡对应源码。规则冲突以 ADR 91 已明确覆盖的条款为准，其他边界保持。

不新增递归任务派发、任意跨 Bot 通信、第二套任务/权限/完成数据库、直接主 Bot 项目写入或新执行旁路。不改真实用户数据、版本号、发版物、第三方依赖或默认远端推送政策。

## 3. 分阶段卡与验收

| 卡 | 级别 / 依赖 | 实现与必要测试 |
| --- | --- | --- |
| R91-01 契约与输入路由 | A；RC11 | Protocol 的 mandate、目标修订、决定与 transition；现有协调 work 加法存储。测试输入身份保留、引用范围、独立新目标、无关内容无授权、并发 expectedRevision 冲突、旧记录兼容 |
| R91-02 短片段与资源 | A/B；01 | 外层 runner 与内层工具循环的安全让出；协调/工作名额；waiting 与实际资源分离。测试长用户回合插话、总并发不超发、上限 1 交替、跨项目公平、满槽等待父回复、写目录锁保留 |
| R91-03 取消/替换/接手 | A/B；01、02 | 版本与 epoch 闸门、取消传播、交接材料、可恢复 transition。测试运行工具取消、未知结果对账、旧执行者迟到、取消只影响指定树、替代排队不复活旧流程、逐步崩溃/重放、依赖适用性、已完成结果纠正 |
| R91-04 自主事件推进 | A/B；01–03 | Provider/Projection 的 mandate 准入、原目标内事件动作、Agent 问答与接手补偿。测试有效/过期/取消 mandate、跨项目/目标/材料拒绝、waiting_user 不消费、同事件幂等与新版本不丢、重复失败无进展保护 |
| R91-05 表达与真实验收 | B/C；01–04 | 真实任务/替代关系投影、主 Bot 回复与后台工作分离；安装版真实模型并行、纠偏与恢复验收。按 ADR 91 §13 全矩阵，执行产品回归；注明覆盖与审查独立性 |

每张卡只推进本阶段允许范围，一张卡一个可审查提交/PR；堆叠 PR 明确依赖顺序。实现前再次定位符号并登记必要范围扩展，不把全部功能塞进 runner、Supervisor 或大 React surface。

## 4. 代码锚点与允许范围

路径相对于 Peer-Agent 根；均包含对应定向测试，实际新 Module 按 ADR 91 Interface 分工。未列出的必要文件先在本卡记录原因和范围再改。

- 共享契约：`packages/protocol/src/delegation*`、`goal*`、`session-facts*`、`task-overview*` 及必要类型出口。
- 协调与能力：`packages/runtime-node/src/project-agent/` 的输入队列、runner、work-coordination/reducer/store、scheduler、SessionSupervisor、通信、Provider、工具 specs/prompts、Context 画像与状态投影；目录内新深 Module；runtime-node 必要出口。
- 执行生命周期：`packages/runtime-node/src/goal-runner.mjs`、`goal-plan-store.mjs`、执行租约/交接相关 Module；仅按生命周期接口抽取和装配，不扩中心分支。
- 内层安全点：`packages/runtime-sdk/src/pipeline*`、`packages/runtime-core/` 的相关执行接口、`apps/desktop/electron/main/chat-runtime/agent-loop-kernel.mjs`、相应调用/工具执行 seam；先核实当前文件职责，不在 provider encoder 重复拼调度逻辑。
- Context：`packages/system-context/src/sources/` 及注册/测试；`packages/runtime-core/src/conversation-history-projector*` 仅必要事实投影。
- 存储：`packages/runtime-node/src/data-store.mjs` 仅必要新增登记；`packages/conversation-store/` 仅需要的加法字段/消息种类，不改写历史 jsonl。
- Desktop 装配：`apps/desktop/electron/main/agent-host/`、`project-agent/`、委托能力定义、`llm-chat-service.mjs` 必要 turnProfile/安全点适配及测试；`main.mjs` 只替换装配，净增不得大于 0。
- TUI：`apps/tui/src/project-agent/`、`provider-chat-model.ts`、任务执行器及共享宿主必要装配/测试，核心策略复用 runtime-node。
- 表达：`apps/desktop/renderer/src/project-agent/` 的 conversation/state/styles、必要 `packages/i18n/`；不向 ChatSurface/Sidebar 大组件新增业务。
- 产品门禁：`apps/desktop/scripts/`、`scripts/product-regression.mjs` 必要场景与覆盖声明；变更 IPC 时先登记 Protocol/preload 类型和 catalog。
- 知识：本卡、ADR 91、ADR 80/89 对应引用和证据记录，卡总目录；不在代码仓新建架构知识。

## 5. 通用退出条件

1. 卡内定向测试、受影响包测试与 build/typecheck/architecture:check；按实际 IPC/TUI 变更补对应门禁。失败不得改 skip 或放宽已有断言掩盖。
2. 真实执行器集成验证单拥有者、取消/未知副作用、模型资源、通信、权限和事件恢复；不能用 assistant 文字证明执行。
3. 有 UI 变化运行 `pnpm qa:product:capture --output <仓外临时目录>`，逐张 AI 观察全部必需截图、写 review.json，再 verify；实施者自审标记 independent=false。
4. R91-05 用安装版和真实模型验证 A/B/C 执行区间重叠、同目标插话、错误方向取消重派、父子通信和重启；渠道真实限制单独记录。
5. 每张卡交接记录源码、实际命令结果、未覆盖内容、限制和偏差；未验证不得写已完成或发布就绪。
6. commit 同轮 push；交付 PR 不默认合并或发布 RC。RC/GA 另行按用户授权和发版门禁进行。

## 6. 本轮设计交付

完整 ADR 已覆盖主 Bot 自主选择推进方式与取消重派、原目标授权、输入路由、短片段、公平资源、双向通信、版本交接、未知结果和验收矩阵。与 ADR 80/89 的覆盖关系已登记。运行时代码和产品验收未开始。

## 7. 实施前补充定位与接口收敛

- `runner-coordination.start` 当前会暂停其他 runnable/retry_wait work；稳定目标身份和每次协调回合必须分开，新输入不自动停止独立目标。
- `session-supervisor.cancelLocked` 在全实例 exclusive 队列内等待执行 idle；取消请求登记与异步收尾拆开，避免 A 的停止挡住 B 的调度/通信。
- R91-01 在既有 coordination journal/reducer 上增加目标、命令与 transition 记录；目标完成状态仍来自 GoalPlan。Protocol 用 `delegation-coordination.ts` 与必要出口，不新增存储路径。
- 模型命令不携带宿主权限、执行 epoch 或签发 mandate；受信的授权/材料/任务身份由 Provider 与宿主端口装配。纯内核只接纳结构化命令并输出 effect 描述，执行仍由既有能力入口负责。
- R91-02 安全让出利用已有 providerCheckpoint 与 slice budget；进入内层执行 pipeline，已调用但结果未知的操作继续遵守恢复闸门。

本节在实现前记录，后续按卡补充实际提交、命令结果与覆盖限制。
