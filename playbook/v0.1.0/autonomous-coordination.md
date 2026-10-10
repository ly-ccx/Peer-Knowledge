# R91：主 Bot 自主协调与取消重派

创建时间：2026-10-10
最后更新：2026-10-11

负责人：用户。设计依据：用户要求并行自主调度，并明确主 Bot 可识别补充/纠正、取消错误执行和重派；[ADR 91](../../knowledge/decisions/91-project-bot-autonomous-coordination.md) Accepted。

状态：实施、合入与RC12发布验收完成。2026-10-10 用户明确授权“按照这个思路来实施”，随后授权“发布新的 rc，你要验收一下”；R91-01 至 R91-05 已按依赖收拢并合入。ADR 91 / 已合入知识 PR #33 是设计依据；正式签名包真实模型8场景与发布检查见[RC12交接](rc12-candidate.md)。总体Ready/GA限制保留。

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

完整 ADR 已覆盖主 Bot 自主选择推进方式与取消重派、原目标授权、输入路由、短片段、公平资源、双向通信、版本交接、未知结果和验收矩阵。与 ADR 80/89 的覆盖关系已登记。R91-01 至 R91-05 已实现、按依赖合入并发布RC12；历史实施候选验收见 §8，正式包验收见 §9。

## 7. 实施前补充定位与接口收敛

- `runner-coordination.start` 当前会暂停其他 runnable/retry_wait work；稳定目标身份和每次协调回合必须分开，新输入不自动停止独立目标。
- `session-supervisor.cancelLocked` 在全实例 exclusive 队列内等待执行 idle；取消请求登记与异步收尾拆开，避免 A 的停止挡住 B 的调度/通信。
- R91-01 在既有 coordination journal/reducer 上增加目标、命令与 transition 记录；目标完成状态仍来自 GoalPlan。Protocol 用 `delegation-coordination.ts` 与必要出口，不新增存储路径。
- 模型命令不携带宿主权限、执行 epoch 或签发 mandate；受信的授权/材料/任务身份由 Provider 与宿主端口装配。纯内核只接纳结构化命令并输出 effect 描述，执行仍由既有能力入口负责。
- R91-02 安全让出利用已有 providerCheckpoint 与 slice budget；进入内层执行 pipeline，已调用但结果未知的操作继续遵守恢复闸门。

本节在实现前记录，后续按卡补充实际提交、命令结果与覆盖限制。

### R91-04 准入与关联细化（实施前）

- 复用注册的 project-agent L1 和 project-roster L7，提供真实目标版本、事件与 transition；Desktop/TUI 的 Context 装配同步。
- goalRevision 为协调决定的乐观版本。针对单会话的修订/取消撤销该会话的执行绑定；同一输入下其他独立执行绑定继续有效，避免一条取消把并行兄弟任务一起停掉。root 停止仍由既有 work stopScope 与预算闸门关闭全部相关工作。
- 旧记录只允许由本轮真实用户输入显式接管：在既有 journal 建立 mandate，并绑定已存在的会话，不因后台 wake 或历史锚点自动补造授权。
- 连续纠正沿 journal 中真实替代关系定位当前执行者；不以时间邻近推断。恢复使用持久决定的原始输入摘要和 operationId，不重新生成不同规格。
- 新增生命周期定向测试及现有 Context/Provider/实际 Supervisor 集成；产品投影仅表达真实 cancellation/takeover 和替代关系，不增加第二套状态。

### R91-05 真实接线与重启边界（实施前补充）

- 安装候选版真实模型验收暴露 Desktop turnProfile 丢失 workId、事件和工作身份；在既有工具上下文 seam 保留宿主完整画像，并装配已有 sendAgentMessage 端口，不新增能力旁路。
- 并行 A/B/C 和针对 A 的取消重派已得到真实执行记录。停机时旧回合抛出的租约错误会覆盖已提交的 host_handoff 暂停；Goal Runner 在回合返回与抛错两条路径写状态前检查暂停、取消及当前宿主归属。旧拥有者退出后保留可恢复状态，由新宿主按既有交接恢复。
- 替代关系只由 replace transition 表达；parallel 的上下文目标不表示取代另一个任务。增加真实 Goal Runner 迟到错误/结果与重新接手测试。
- 真实重启验收发现工作预算把主 Bot 的 blocked_system/paused 回复状态当作全部子工作停止。停止范围必须使用既有 stopScope：reply 范围仅挡主 Bot 新回合，工作树停止、累计预算耗尽和各计划未知副作用仍在本地闸门拦截。补充共享工作中父回复失败、兄弟执行与 root 取消测试。
- 收尾核对 ADR 91 §12：journal 重放核验 transition schema 与 minimumExecutorVersion，未来契约不得由不支持的宿主消费；宿主级 PEER_AUTONOMOUS_COORDINATION=0 关闭新增决定与未开始的替代派发，已登记取消继续收尾。此为执行策略开关，不是 PermissionGrant。已创建但排队的替代在 promote 同一闸门保持停止，开启后仍按原 transition 恢复，不复活已取消旧任务。历史旧版混合执行不保证兼容。
- 通信真实验收暴露 Verifier 只收到 file/command 快照，无法核实已发生的父子问答。在既有 verifier-evidence / goal-runner-host seam 按当前 plan 的宿主身份投影直属双方 AgentMessage 送达回执，验证 replyTo 与时间；仅证明通信事实，不提升消息正文权威、不新建 Evidence 库。增加跨目标拒绝与消息伪装测试；ADR 91 §9 先补充此 admission 契约。
- 完整签收验收进一步发现通信引用未登记 EvidenceIndex，模型虽判定通过，持久化仍正确拒收。上述宿主 admission 先按稳定 messageId 把身份核实后的送达事实登记到既有索引，绑定当前计划与子会话；不允许已有引用跨计划重绑定。增加实际 GoalRunner + GoalPlanStore 的 model_review 持久化、重启有效与无需人工签收测试，以及登记幂等/身份碰撞拒绝测试。保留原证据索引和目标版本门禁。
- 真实满槽验收发现已完成叶子的任务提前释放执行名额后，迟到收尾把资源准入当成身份失效，任务停在 running。区分 canRunPlan 资源准入与 canSettlePlan 当前拥有者提交权；completed 叶子待验证的任务仍可进入验证收尾，模型执行继续通过原全局名额租约。补充满槽完成到验证的宿主集成测试。


- 严格真实签收验收发现 B 报告已通过核验，但 wake 让出时提前签收事件，随后新事件复用同一 runnable work 覆盖其检查点，导致 B 缺失主 Bot 汇报。修正既有 runner-coordination：让出不提交 handled；新批次不能复用仍在续跑/重试的 work。新增两份结果交错让出、重启保留两份检查点、分别汇报且不重复模型/派发的实际 Runner 测试。ADR 91 §8 先登记归属与处理回执不变量。

## 8. 实施交付与验证记录

真实模型验收还发现工作 Agent 将父回答的裸 messageId 写为 task evidence 时，既有索引会登记为 goal_update_task，导致正确的送达回执与任务证据共用身份。按 ADR 91 §9 改用宿主派生的 agent-delivery 引用，绑定 plan/messageId；保留裸引用原记录，不改写其 provenance。验证裸引用已有其他 capability 不阻断真实送达核验、派生引用跨计划/capability 碰撞仍拒绝，以及实际 GoalRunner 核验持久化。

以下为从RC11基线逐卡交付的历史记录。所有所列堆叠PR已按依赖合入开发线；最终发布身份见 §9。无关draft PR145未纳入本轮。

| 卡 | 提交 / PR | 已完成内容 |
| --- | --- | --- |
| R91-01 | `1009c847` / Peer-Agent #143 | Protocol mandate/decision/transition、纯协调内核、既有 coordination journal 加法重放与存储 |
| R91-02 | `9c97fa2c` / #144；依赖 #143 | 主 Bot 两回合/四工具短片段、安全让出、协调保留名额、独立目标共存、只读等待释放准入 |
| R91-03 | `32581ce4` / #146；依赖 #144 | 取消登记和异步收尾分离、停止/未知结果路径、恢复与执行 epoch 闸门 |
| R91-04 | `fa73b0ab` / #147；依赖 #146 | coordinate_work 八动作、事件 mandate 准入、旧任务显式接管、幂等恢复、材料限制、替代谱系与双向通信 |
| R91-05 | `9462a4ca` / #148；依赖 #147 | 停止/结果待核实及调整记录投影、Desktop 工具上下文身份、重启迟到结果隔离、父回复停止范围、通信核验、满槽收尾、事件检查点保护、策略关闭与未来 schema 拒绝 |

### 必需矩阵与实际覆盖

- Protocol / coordination kernel / lifecycle：输入身份、乐观版本冲突、同事件去重、新版本再处置、连续替代、目标材料及直属通信、事件不可冒充新用户授权。
- pipeline / scheduler：用户插话安全点、协调保留名额、总并发限额与上限 1、公平性、只读等待释放、写工作区锁保留。
- actual Supervisor / GoalRunner：取消不阻塞兄弟、未知副作用不重放、已完成结果保留、接手 epoch、迟到错误/结果不能改写已提交暂停取消、重启恢复。
- work-budget：reply 停止范围不取消独立子工作，work 范围和累计预算耗尽继续拦截；目标版本和未知结果闸门不被主回复状态代替。
- verification：当前计划的 file/command Evidence 加直属 AgentMessage 回执；跨工作区/会话、伪造 kind、关联不存在或回答早于问题不能用作通信核验；满只读槽时 completed 叶子仍完成验证。
- rollback：PEER_AUTONOMOUS_COORDINATION=0 停止新处置与未开始替代，已登记取消继续收尾；排队替代开启后按原 transition 继续，不复活旧执行者；不支持的 schema/minimumExecutorVersion 在重放和写入前拒绝。
- Desktop 实际 tool pipeline：宿主传入的 workId、事件和协调 binding 通过 Projection/Provider 到达真实端口；子 Agent send_agent_message 端口实际装配。

最终源码 `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`（含 SVG/圆角）、全仓 `pnpm test` 与 `git diff --check` 已通过；安装候选包 workspace imports 校验通过。

### 真实模型与安装候选版验收

时间：2026-10-10 23:32:32 至 23:37:57（Asia/Shanghai）。实际打包 macOS arm64 `.app` 从隔离安装目录运行，`app.isPackaged=true`、`app.asar`，版本保持 `0.1.0-rc.11`；源码包含提交 `9462a4ca` 的最终改动。真实 OpenAI OAuth `gpt-6.1-sol`，全局模型并发配置 4、只读工作准入 2。通过生产 IPC 提交输入，由主 Bot 模型选择真实工具动作，工作 Agent 模型读取文件、提问、执行与交付；未脚本注入模型结果或人工修改签收状态。

| 故事 | 实际事实 |
| --- | --- |
| A/B/C 独立任务 | A=`45e99558-a4c6-44b7-99ea-c098003ed623`、B=`25f8a56c-4115-4a68-8fad-6bfa52ebd4ac`、C=`f37c3a69-a659-4cfd-913a-4deaf3698887`。A/B 实际模型工具执行区间重叠 42,725 ms；C 在满两个只读槽时排队，A 停止后继续 |
| B 输出格式补充 | 保持原 B session 和执行者，真实 update 回执进入其 Conversation；没有取消或重建 B |
| 纠正 A | 原 A 从 stopping 到 cancelled，替代=`e8b4cdff-52fb-408f-a915-15f4209e2336`；B/C 没有被取消。真实 replace operation=`b24607d8f76327d156f6cd3974149b233eafc29295e677246bfbdfcd78402b4b` |
| 关闭并重启 | 所有会话身份与替代关系保留；旧 A 仍 cancelled，只有一个替代，已完成核对保留 |
| 子 Agent 提问与主 Bot 回答 | Question session=`38c7835c-038e-4896-a9c6-2bc185b51da0`。实际问题=`agent-msg:715d3633ff3864221ef07b23c4de7b0010f87392531a6c6a4ca612e5556071e6`，回答=`agent-msg:670b1895746970c80fe0989ac9c37ce8db7c0e3cfab85025b9061926b01b5788`。replyTo 正确，全部 8 次 C 文件读取在关联回答之后发生，没有转交用户 |
| 结果与收尾 | B=16 条/1000，C=8 条/276，Corrected A=6 条/165，Question=8 条/276。四份结果的持久 model_review 全部 passed；主 Bot 自主汇报并签收，最终四个会话均 accepted，旧 A cancelled。严格验收不把 result_ready 当成功 |

8 个真实故事全部通过，Renderer pageErrors=0。原始验收报告 SHA-256：`b114d3f97a68d3edbfddc99fac56b47be48b82adb0ba81d09436c497ad01663d`。报告保留实际会话/消息/执行时间与任务核验记录；隔离凭据副本已删除，自有应用进程已停止。

范围与限制：此次是真实模型、实际打包安装候选版、只读并行与纠偏验收；不是官方签名、公证、安装器或 updater 安装验收。候选包复制凭据访问时其 bundled credential helper 曾超时，实测使用当前已安装 RC11 的同接口 helper；未验证新包 bundled helper 的完整安装路径。工作与 Verifier 同为 GPT-6.1 Sol，分属独立核验回合，不据此宣称异源核验。只读模型请求和本地操作都实际执行；Shell/MCP 外部副作用未知、并发写/worktree 等边界由定向集成测试覆盖，本轮未做真实外部写操作验收。原用户工作区与日常安装版未改动；既有 artifact spool 仍由生产能力管理。

### 产品回归与可访问性

执行 `pnpm qa:product:capture --output <temporary-directory-outside-repo>`，随后逐张检查全部 143 张必需截图，填写具体观察与 `review.json`，`pnpm qa:product:verify --output <same-directory>` 返回 passed。

- Packet runId：`91c98cd8-01a2-418c-ad11-fd88a8e12654`。
- Source fingerprint：`0363819692d342352360c826085646fff43343f7ea6f03adadc09730b33a3bc4`。
- 审查为实现者 AI 自审，`independent=false`，没有宣称独立审查。
- 新增 8 张协调状态截图覆盖 1280 深色、760 浅色下 stopping、awaiting_outcome、cancelled、handoff。取消中不可重复提交，未知结果不诱导重放，旧/新任务关联真实；调整记录收于任务信息，无引用竖线。
- 同时检查既有消息间距、Bot 色彩、气泡范围内右对齐且 hover/focus 显示的详情入口、具名 Agent 活动、证据降噪、窄屏侧栏、快捷输入与更新收起流程。
- 自动场景检查键盘、ARIA 与 reduced-motion 路径；未做完整 VoiceOver/屏幕阅读器或长期使用验收。截图与互动场景用脚本化模型认知，真实模型和安装候选版验收为上节独立运行，不能将二者覆盖混为一谈。

## 9. RC12正式交付与再次验收

用户另行授权发布与验收后，#148 → #147 → #146，#144/#146 → #143按依赖收拢；#143与发布准备#149合入开发线，正式tag `v0.1.0-rc.12` 指向 `cc9f9a1b9ec718c92c63eb324756bfb08b57eeaa`。无关draft #145未纳入。知识PR33已合入main。

2026-10-11实际运行官方签名RC12包，以原装签名凭据助手和真实GPT-6.1 Sol重跑8个严格故事：A/B执行区间累计重叠37,921ms；补充保持原执行者；纠正取消旧A且只有一个替代，B/C不中断；重启保留身份和谱系；父子问题以replyTo关联且回答后才继续读取；四份结果持久核验passed，主Bot自主收下，最终accepted。没有helper路径覆盖，补齐 §8 候选包原装助手未覆盖的范围。

本版143张产品截图自审、30项升级恢复、候选与实际合入两平台CI、官方8个发布job、14资产、Mac签名公证、npm隔离安装、21项更新发现、实际RC11下载RC12、正式包4张UI与Pages均通过。完整源码绑定、机器/模型/视觉证据及限制见[RC12交接](rc12-candidate.md)。实现者自审不是独立审查；只读真实模型验收不代替真实外部写入、Windows/Linux交互安装、屏幕阅读器、七天日用和GA验收。旧版下载通过不代表实际调用Squirrel安装或替换日常应用。
