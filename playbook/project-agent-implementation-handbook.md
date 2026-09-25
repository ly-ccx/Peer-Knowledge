# 项目代理落地 · 执行手册（给执行模型）

创建时间：2026-09-25
最后更新：2026-09-25

> 用途：把项目代理（ADR 80–84）的落地工作派给任何模型时，执行方必须遵守的约定、任务卡和交接格式。  
> 地位：执行层合同。方向与边界以 ADR 80–83 和落地计划为准；本手册与它们冲突时，以 ADR 为准，并提交「边界变更请求」（§9）。  
> 负责人：用户（仓库所有者）。执行方：被派发任务卡的模型。  
> 关联：`design/product/project-agent-landing-plan.md`（阶段与节奏）、`knowledge/architecture/project-agent-capability-layers.md`（模块与步骤编号）、`knowledge/architecture/project-agent-delegation-runtime.md`（契约）、`knowledge/architecture/project-agent-memory-system.md`、ADR 80 / 81 / 82 / 83、代码仓 `AGENTS.md`

---

## 0. 一分钟版

1. 你只做派给你的那一张任务卡；卡片外的文件不改。
2. 开工前按 §1 的顺序读文档，并确认卡片的「进入条件」全部满足；不满足就停下汇报。
3. 从负责人指定的基线分支拉自己的分支；不要在别人有未提交改动的分支上工作。
4. 遵守 §2 铁律；拿不准时选更保守的做法，并在交接报告里写明。
5. 完成后按 §8 模板交接：改了什么、怎么验证的（原样贴命令和结果摘要）、和卡片有什么偏差。
6. 没有证据不说「完成」。测试没跑、跑不了、有失败，都如实写。

---

## 1. 开工前必读（按顺序）

| 顺序 | 读什么 | 为什么 |
|---|---|---|
| 1 | 代码仓 `AGENTS.md` | 仓库治理基线：能力链、分层、禁令、变更分级、Git 同步 |
| 2 | 本手册 §2–§5 与你的任务卡 | 执行约定与本卡范围 |
| 3 | `design/product/project-agent-landing-plan.md` | 你这张卡在哪个阶段、依赖谁 |
| 4 | 任务卡「必读」列出的 ADR 与架构文档章节 | 契约与不变量 |
| 5 | 任务卡「代码锚点」列出的文件 | 现状 |

知识库根目录按代码仓 `AGENTS.md` 的解析顺序定位（环境变量 `PEER_KNOWLEDGE_ROOT` → `.peer-workspace.local.json` → 同级目录 `Peer-Knowledge` / `peer-knowledge`）。不要把本机绝对路径写进任何仓库。

---

## 2. 铁律

违反任何一条，交付即视为不合格，需要返工。

### 2.1 范围与分支

1. **只做一张卡。** 只改卡片「允许改动」列出的文件与目录；需要改清单外的文件时，先停下提交边界变更请求（§9），不要顺手改。
2. **不碰别人的在制改动。** 开工前 `git status` 必须干净；若基线分支上有不属于你的未提交改动，停下汇报，不要 stash、不要提交、不要覆盖。
3. **分支规则。** 从负责人指定的基线分支（通常是当期 `PeerAgent/dev/<版本>`）拉分支，命名 `PeerAgent/pa/<卡号小写>-<英文短名>`，例如 `PeerAgent/pa/p1-pr1-turn-sink`。一张卡一个分支、一个 PR。
4. **Git 同步。** 本地 commit 后同一轮 push 到远端自己的分支；用 `gh pr create` 向基线分支提 PR，**不要自己合并**，除非负责人明确授权。
5. **禁止危险操作。** 不 `push --force` 共享分支，不 `reset --hard` 别人的提交，不改 git 配置，不跳过 hooks（`--no-verify`）。
6. **不动发版物。** 不改 `VERSION`、`release-notes/`、`.github/workflows/`、`electron-builder.yml`、`CHANGELOG.md`，除非卡片明确要求。
7. **不加依赖。** 不新增 npm / cargo 依赖，不新增顶层 package，除非卡片明确允许。
8. **不碰用户数据。** 不删除、不迁移真实的 `~/.peer-agent`；测试用临时目录。迁移逻辑必须可重复执行、写前备份或原子写。

### 2.2 架构（来自代码仓 `AGENTS.md` 与 ADR 80–83，逐条可检查）

1. **一条能力链。** 任何新能力（调度、记忆、目标、探测）都走 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。不另开执行通道。
2. **Renderer 只做表达。** 不用 `fs` / `child_process`；权限、签收、调度、记忆的真值都在 main 进程或 `runtime-node`；renderer 只读投影、只发结构化命令。
3. **跨进程用协议对象。** 新的 IPC payload 必须在 `packages/protocol` 或 `bootstrapPreloadApi.ts` 有类型；新通道必须进 channel catalog 并通过 `pnpm --filter @peer-agent/desktop ipc:check`。
4. **大文件不再变大。**
   - `apps/desktop/electron/main/main.mjs`：每个 PR 的净增行数 ≤ 0（只允许装配调用替换，不允许新增业务逻辑）。
   - `apps/desktop/renderer/src/chat/components/ChatSurface.tsx`：不新增功能代码；项目代理界面放新目录 `apps/desktop/renderer/src/project-agent/`。
   - `llm-chat-service.mjs` 的 `sendMessage` 参数表：整个项目只允许新增**一个**参数 `turnProfile`（P1-PR2 引入），之后的新字段都放进 `turnProfile`。
5. **提示不是护栏。** 权限、模式、范围限制必须在投影层或执行层强制，不能只写在 system prompt。
6. **上下文分层。** 新的上下文内容只能经注册的 Context Source 进入；工具结果、文件内容、记忆、任务报告只能进事实层（`L7_CONTINUITY`），不能进 `L0`–`L6`。
7. **存储登记。** 新的本机持久化路径必须登记在 `packages/runtime-node/src/data-store.mjs` 的 `DATA_STORE_ENTRIES`，并写明 scope（device / portable / cache）。
8. **功能开关。** 第 2 阶段起的所有用户可见行为必须受开发者开关 `projectAgentMode` 控制；开关关闭时，行为、界面、存储写入与今天完全一致（必须有测试证明）。
9. **分级门槛。** 第 2 阶段起的卡片涉及 A 级边界，只有在对应 ADR 状态行为 `Accepted` 时才能开工。开工前打开 ADR 文件确认状态；是 `Proposed` 就停下汇报。
10. **遗留代码。** 碰到违反治理基线的旧代码，不扩大违规；能顺手移向正确 seam 就移，移不动就在交接报告里指出下一处 seam。

### 2.3 测试与诚实

1. 测试会 import 各包的 `dist/`，跑测试前先构建（§4）。
2. 按卡片「必须新增的测试」补齐；修 bug 先写能复现的失败测试。
3. 提 PR 前必须跑：卡片列出的定向测试 + 受影响包的完整测试 + `pnpm architecture:check`。
4. 已知失败（代码仓 `AGENTS.md` 列出的那几项）不需要你修，但**不能新增失败**；如果 P0-3 已处理，以处理后的基线为准。
5. 不删除、不跳过、不放宽已有测试来让自己通过。确实需要隔离时，写明原因并在交接报告里列出。
6. 交接报告里的测试结果必须是真实运行的输出摘要；没跑就写「未运行」和原因。

### 2.4 文档

1. 架构知识只写进 `peer-knowledge`，不在代码仓新建 `docs/architecture/*`。
2. 执行方默认**不修改** ADR 与架构文档；发现文档与代码不符时，在交接报告里写「文档偏差」，由负责人决定改哪边。
3. 阶段完成时由负责人（或被指派的执行方）更新落地计划的阶段表与交付状态清单 D10。
4. 代码注释只写代码表达不了的约束，风格与周边代码一致；不写「这里修改了什么」「为什么这样改是对的」这类过程说明。

---

## 3. 标准工作流程

```text
领卡
 → 读（§1）→ 核对进入条件（不满足：停，汇报）
 → 开工确认：在第一条回复里写出 分支名、要改的文件、实现要点、要补的测试（不写代码）
 → 实现（小步提交，commit message 用 feat|fix|refactor|test|docs(scope): 描述）
 → 自测（§4）
 → push + 开 PR（PR 描述 = 交接报告）
 → 交接（§8）
```

遇到以下情况，停下并提交边界变更请求（§9），不要自行决定：

- 卡片要求与 ADR / 契约文档冲突；
- 必须改动「允许改动」以外的文件；
- 需要新依赖、新存储路径未在卡片列出、新 IPC 通道未在卡片列出；
- 发现某个不变量在现有代码里做不到。

---

## 4. 验证命令

需要 Node ≥ 22.18（测试直接运行 `.ts`）、pnpm 10.22.0。

```bash
pnpm install --frozen-lockfile
pnpm build                                   # 测试依赖各包 dist，先构建
pnpm --filter @peer-agent/desktop ipc:check  # 新增或修改 IPC 通道后必跑
node --test apps/desktop/electron/main/<某个>.test.mjs   # 定向测试（在仓库根执行）
pnpm --filter @peer-agent/desktop test       # 桌面端完整测试
node --test packages/protocol/src/*.test.ts  # 协议包测试（该包没有 test 脚本，直接跑）
pnpm --filter @peer-agent/runtime-node test  # runtime-node 测试（改 runtime-node 时）
pnpm --filter @peer-agent/system-context test
pnpm --filter @peer-agent/conversation-store test
pnpm typecheck
pnpm architecture:check
```

并行跑全量测试时，依赖计时的桌面测试可能偶发 `cancelledByParent`；单独重跑该文件确认。

---

## 5. 统一术语与命名

| 概念 | 产品面 | 代码名 | 说明 |
|---|---|---|---|
| 项目代理 | 机器人（界面称谓）/ 项目代理 | `project_agent`（角色 / 模式），`ProjectAgentRunner` | 每个 Workspace 一个；界面上叫「机器人」（ADR 84） |
| 机器人身份 | 名字 · 头像 | 工作区条目 `displayName`、`avatar`、`managed` | ADR 84；头像由 `workspaceId` 确定性生成 |
| 受管文件夹 | — | `~/Peer/<名字>/`（根目录可配置） | 新建空白机器人时创建；ADR 84 |
| 档案 | 档案 | `BotProfileDrawer` | 按需滑出：概况 · 任务 · 目标 · 记忆 · 设置 |
| 任务 | 任务 | `work_session`（会话 role）、`WorkSession`（投影） | 子 Conversation + GoalPlan |
| 执行宿主 | — | `AgentTurnExecutor`、`TurnSink`（`BroadcastSink` / `CollectingSink`） | 跑一轮 agent，不依赖窗口 |
| 回合画像 | — | `turnProfile`（`sendMessage` 唯一新参数） | 角色、模式、模型选择等 |
| 模型分工 | 模型分工 | `ModelRouter`、`resolveRoleModel`、档位 `strong/fast/economy/vision` | ADR 83 |
| 项目标识 | — | `workspaceId`（UUID） | ADR 81 |
| 项目目标 | 项目目标 | `ProjectObjective`、`ObjectiveWatch` | 代码里不用 Goal，避免与 GoalPlan 冲突 |
| 记忆 | 记忆 | `MemoryItem`、`MemoryEpisode`、`LocalMemoryProvider` | ADR 81 |
| 签收 | 签收 / 需要你确认 | `resultAcceptance.acceptedBy: 'policy' \| 'user'` | ADR 80 决策 8 |
| 送达 | 推送 / 只进对话 / 今日小结 / 不打扰 | `decideSurfacing` → `interrupt/message/digest/silent` | ADR 80 决策 9 |
| 开关 | — | 开发者设置 `projectAgentMode` | 默认 `false` |

新目录约定：

- 主进程执行宿主：`apps/desktop/electron/main/agent-host/`
- 主进程项目代理服务：`apps/desktop/electron/main/project-agent/`
- 可移植运行时：`packages/runtime-node/src/project-agent/`、`packages/runtime-node/src/memory/`、`packages/runtime-node/src/model-router.mjs`
- 协议：`packages/protocol/src/delegation.ts`、`packages/protocol/src/memory.ts`（替换旧遗留类型）、`packages/protocol/src/model-routing.ts`
- 上下文来源：`packages/system-context/src/sources/project-agent-source.mjs`、`project-roster-source.mjs`、`project-memory-source.mjs`
- 界面：`apps/desktop/renderer/src/project-agent/`

---

## 6. 并行关系

```text
第 0 阶段：P0-1 ─┬─ P0-2 ─ P0-3 ─ P0-4
第 1 阶段：
  串行（同改 main.mjs / 执行路径）：P1-PR1 → P1-PR2 → P1-PR3 → P1-PR6 → P1-PR7
  可与上面并行：P1-PR4、P1-PR5、P1-PR8
第 2 阶段（进入条件：ADR 80 / 81 / 83 / 84 Accepted，第 1 阶段合入）：
  P2-1 → P2-2 → P2-5 → P2-6
  P2-3、P2-4 可与 P2-2 并行；P2-7 在 P2-5 的 IPC 契约合入后开始
```

同一时间，同一文件只允许一张卡在改。派发前负责人检查冲突。

---

## 7. 任务卡

卡片字段：目标 · 级别 · 进入条件 · 必读 · 代码锚点 · 允许改动 · 不许改动 · 实现要点 · 必须新增的测试 · 退出条件。

### 第 0 阶段：收口

#### P0-1 收口 0.0.18
- **负责人**：用户。执行方不做，除非明确指派。
- **目标**：当前开发线上的在制改动（自动更新、引用消息等）完成、提交、发版。
- **退出条件**：`PeerAgent/dev/0.0.18` 工作区干净；0.0.18 发布；负责人指定第 1 阶段基线分支（如 `PeerAgent/dev/0.0.19`）。

#### P0-2 ADR 80–84 评审
- **负责人**：用户。
- **目标**：过一遍各文档「待评审点」，把 ADR 80 / 81 / 82 / 83 / 84 转为 `Accepted`，或写明修改意见。
- **退出条件**：ADR 状态行更新；落地计划进入条件勾掉。

#### P0-3 回归基线清零
- **级别**：C。
- **进入条件**：P0-1 完成。
- **必读**：代码仓 `AGENTS.md`「Known pre-existing failures」。
- **允许改动**：失败测试对应的源文件与测试文件；`packages/protocol/src/goal.test.ts`；`architecture:check` 报告的两处 CSS。
- **实现要点**：逐项定位；小修直接修；修不动的改为 `test.skip`，写一行说明原因，并在交接报告列出。不改业务行为来迁就测试。
- **退出条件**：`pnpm build && pnpm test`、`pnpm typecheck`、`pnpm architecture:check` 全绿，或只剩显式隔离项且已列出。代码仓 `AGENTS.md` 的已知失败清单同步更新。

#### P0-4 代码仓入口指向本手册
- **级别**：C。
- **进入条件**：P0-1 完成。
- **允许改动**：代码仓 `AGENTS.md`（只加一段）。
- **实现要点**：在 `AGENTS.md` 加「进行中的专项：项目代理落地」一段，指向 `peer-knowledge/playbook/project-agent-implementation-handbook.md` 与落地计划，说明执行方必须遵守本手册。
- **退出条件**：合入基线分支并 push。

---

### 第 1 阶段：地基（0.0.19）

#### P1-PR1 抽出 TurnSink 与 CollectingSink
- **级别**：B（执行路径重构，行为不变）。
- **进入条件**：P0-1 完成；基线分支干净。
- **必读**：分层文档 §3（L1 执行宿主）。
- **代码锚点**：`apps/desktop/electron/main/main.mjs` 的 `createCollectingWebContents()`，以及 `explorerRunner.runExplorer`、`verifierRunner.runVerifier` 对它的使用；`llm-chat-service.mjs` 的 `wrapWebContentsForRuntimeEvents` 注释（adapter / loop 只用到 `send`）。
- **允许改动**：新建 `apps/desktop/electron/main/agent-host/turn-sinks.mjs` 与测试；`main.mjs`（只删函数、改 import 与调用）。
- **不许改动**：`llm-chat-service.mjs`、`chat-runtime/*`、`runtime-node`。
- **实现要点**：
  - `TurnSink` 契约：必须实现 `send(channel, payload)`；可以实现 `isDestroyed()`（默认返回 `false`）。任何调用方不得依赖 `id`、`on` 等 Electron 专有成员。
  - `createCollectingSink()` 行为与原 `createCollectingWebContents()` 完全一致：收集事件，累积 `chat:stream:delta` 文本，识别 `done / error / aborted` 终态，提供 `getText / getEvents / getTerminal`。
- **必须新增的测试**：`agent-host/turn-sinks.test.mjs`：文本累积、终态识别（三种）、`getEvents` 返回副本。
- **退出条件**：`main.mjs` 净减行；Explorer / Verifier / 视觉复核相关测试与桌面端完整测试通过（除已知隔离项）。

#### P1-PR2 BroadcastSink、后台回合不依赖窗口、待处理权限可重连
- **级别**：B（IPC 快照形状扩展，需在交接报告说明架构影响）。
- **进入条件**：PR1 合入。
- **必读**：分层文档 §3.1、§3.3；ADR 22（流重连）；运行时契约 §6（权限冒泡）。
- **代码锚点**：
  - `main.mjs` `getRunnerWebContents()` 与 `chatRuntime.runGoalTurn`（无窗口时返回 `blocked: 'No renderer window is available for Goal Runner'`）；`broadcastToAllWindows()`。
  - `chat-runtime/permission-gate.mjs`：`pendingPermissionRequests`、`registerPendingPermission`、三处 `webContents.send('chat:stream:permission-request', …)`、`chat:stream:permission-settled`。
  - `llm-chat-service.mjs` `reattach()` 返回的快照（目前**不含**待处理权限）；`sendMessage` 参数表。
  - `ipc/register-chat-ipc.mjs` 的 `chat:stream:reattach` / `chat:stream:list-active`；`preload/contracts/bootstrapPreloadApi.ts`。
  - renderer 里处理 `chat:stream:permission-request` 与重连快照的状态模块（用 `rg "permission-request" apps/desktop/renderer/src` 定位）。
- **允许改动**：`agent-host/turn-sinks.mjs`（加 BroadcastSink）；新建 `agent-host/agent-turn-executor.mjs` 与测试；`main.mjs`（只改调用）；`permission-gate.mjs`（加列出待处理权限的方法）；`llm-chat-service.mjs`（`reattach` 快照加字段；`sendMessage` 新增唯一参数 `turnProfile` 并写入 streamRecord，暂只记录 `role`）；`bootstrapPreloadApi.ts`；renderer 中重连与权限卡相关的状态模块及其测试。
- **不许改动**：provider loop、tool-orchestrator 的业务逻辑；`ChatSurface.tsx` 的功能代码。
- **实现要点**：
  - `createBroadcastSink({ getWindows })`：把事件发给所有未销毁窗口；没有窗口时丢弃即可，事实已经在 streamRecord（文本、segments）与待处理权限表里。
  - `AgentTurnExecutor.runTurn({ turnProfile, conversationId, messages, sink, ... })`：包装 `sendMessage`；Goal 回合用 BroadcastSink，Explorer / Verifier 用 CollectingSink。
  - `runGoalTurn` 删掉「没有窗口就 blocked」分支。
  - 待处理权限可重连：permission-gate 提供按 `streamId` / `conversationId` 列出待处理权限；`reattach()` 快照增加 `pendingPermissions: [{ toolCallId, streamId, call }]`；renderer 重连时据此恢复权限卡；批准 / 拒绝仍走现有 IPC，settle 事件广播给所有窗口。
- **必须新增的测试**：
  - 没有任何窗口时，Goal Runner 仍能完成一轮（用假的窗口列表）；
  - `reattach` 快照包含待处理权限，解决后消失；
  - 两个窗口都能收到 `permission-settled`；
  - renderer 状态模块：由快照恢复权限卡（纯函数测试）；
  - `turnProfile.role` 写入 streamRecord。
- **退出条件**：上述测试通过；桌面端完整测试通过；交接报告附「架构影响」一段（IPC 快照扩展、执行路径变化）。

#### P1-PR3 Goal Runner 装配移出 main.mjs
- **级别**：B（纯移动，行为不变）。
- **进入条件**：PR2 合入。
- **代码锚点**：`main.mjs` 中 `goalRunner = createGoalRunner({...})` 整段，以及定义在 `main.mjs` 里、仅被它使用的辅助函数：`buildGoalRunnerMessage`、`buildGoalRunnerReminder`、`buildExplorerMessage`、`buildExplorerContext`、`buildExplorerReminder`、`buildVerifierMessage`、`parseExplorerReport`、`collectExplorerEvidenceRefs`（移动前用 `rg` 确认没有其他调用方）。`createGoalRunnerAssistantPlaceholder`、`mapGoalTurnOutcome` 已在 `goal-runner-message-persistence.mjs`，只改 import 位置。
- **允许改动**：新建 `apps/desktop/electron/main/agent-host/goal-runner-host.mjs` 与测试；`main.mjs`。
- **实现要点**：导出 `createDesktopGoalRunnerHost(deps)`，依赖全部显式注入（goalPlanStore、conversationStore、llmChatService、executor、broadcast、worktree / branch adapters、desktopPreviewProvider…）。**同一个 PR 不改任何逻辑**，便于审查 diff。
- **必须新增的测试**：`goal-runner-host.test.mjs`：用假依赖跑通一次 runGoalTurn、一次 runExplorer、一次 runVerifier 的装配。
- **退出条件**：`main.mjs` 明显减行；Goal、Explorer、Verifier、视觉复核、Automation 回归全绿。

#### P1-PR4 稳定 workspaceId
- **级别**：A 的一部分（ADR 81 决策 12）。若 ADR 81 仍为 Proposed，负责人可单独批准本卡先行；否则停下。
- **进入条件**：P0-1 完成。
- **必读**：ADR 81 决策 12；记忆架构文档 §9。
- **代码锚点**：`workspace-application-service.mjs`（`settings.workspaces` 条目为 `{ path, name, addedAt, linkedFolders }`，按 `path` 查找）；`runtime-gateway/remote-access-controller.mjs` 与 `setup-remote-access.mjs` 中手工配置的 `workspaceId`；协议里工作区相关类型。
- **允许改动**：上述文件及测试；协议中工作区类型；设置迁移代码。
- **实现要点**：
  - 每个工作区条目增加 `id`（UUID）；读取设置时缺失就生成并原子写回，可重复执行。
  - 对外（IPC / 协议）暴露 `workspaceId`；内部仍可按 path 查找，但新代码按 id 关联。
  - 远程访问：未手工配置 `workspaceId` 时默认用当前工作区的 id；已配置的保持不变。
  - 为以后「目录搬家后重新关联」预留：不按路径猜测 id。
- **必须新增的测试**：旧设置迁移生成 id；重复加载 id 不变；改名 / 换路径 id 不变；远程访问默认值。
- **退出条件**：测试通过；桌面端完整测试通过。

#### P1-PR5 协议契约与纯函数
- **级别**：A 的契约部分；只加类型与纯函数，不接线。若相关 ADR 仍为 Proposed，负责人可单独批准先行。
- **进入条件**：P0-1 完成。
- **必读**：运行时契约 §2（含 2.4–2.7）、§3；记忆架构文档 §4；ADR 82 §1–§3；ADR 83 §1–§5。
- **代码锚点**：`packages/protocol/src/index.ts`；旧 `packages/protocol/src/memory.ts`（`WorkingMemory*` / `MemoryWiki*`，全仓无引用）；`packages/runtime-node/src/goal-runner.mjs` 的 `evaluateVerificationGate`；`packages/protocol/src/task-overview.ts` 的 `projectGoalPlan`；`packages/protocol/src/acceptance-close-gate.ts`。
- **允许改动**：新建 `packages/protocol/src/delegation.ts`、`model-routing.ts` 与测试；重写 `packages/protocol/src/memory.ts` 与测试；`packages/protocol/src/index.ts` 导出；新建 `packages/runtime-node/src/project-agent/verification-verdict.mjs` 与测试。
- **实现要点**：
  - 类型：`WorkSession`、`WorkSessionStatus`（含 `queued` / `verifying`）、`SessionReport`（含 `keyFindings`）、`DelegationOrigin`（含 `memorySnapshotId` / `objectiveId` / `modelSelection`）、`DelegationEvent`、`AgentReplyMeta`、`MessageDisposition`、`VerificationVerdict`、`AcceptanceDecision`、`ProjectObjective`、`ObjectiveWatch`、`WatchObservation`、`MemoryItem`、`MemoryEpisode`、`ModelSelectionSnapshot`、档位与角色枚举。
  - 纯函数（protocol）：`projectWorkSession`、`projectMessageDispositions`、`decideAcceptance`、`decideSurfacing`、`resolveRoleModel`（输入：已接入模型能力表、档位、角色设置、项目范围、本次指定；输出：选择或「无可用」原因）。
  - 纯函数（runtime-node）：`computeVerificationVerdict(plan, evidenceIndex, hostAuthority)`，内部复用 `evaluateVerificationGate`，只认宿主事实。
  - 旧 `memory.ts` 直接替换；确认全仓无引用（`rg "WorkingMemory|MemoryWiki"`）。
- **必须新增的测试**：运行时契约 §12 与记忆文档 §15 中所有「纯函数可测」的条目；`projectWorkSession` 与 `projectGoalPlan` 对同一 GoalPlan 结论一致；`decideSurfacing` 覆盖规则表每一行；`decideAcceptance` 覆盖每个 confirm 原因；`resolveRoleModel` 覆盖能力过滤、范围过滤、不同源复核、空集报错。
- **退出条件**：`node --test packages/protocol/src/*.test.ts`、`pnpm --filter @peer-agent/runtime-node test`、`pnpm typecheck` 通过；没有任何运行时代码调用这些新函数（本卡不接线）。

#### P1-PR6 ModelRouter 接入执行路径
- **级别**：A（ADR 83）。进入条件含 ADR 83 Accepted。
- **进入条件**：PR2、PR5 合入；ADR 83 Accepted。
- **必读**：ADR 83 全文；ADR 30（Provider 恢复）；ADR 25（用量账本）。
- **代码锚点**：`conversation-model-binding.mjs` `resolveConversationModelProviderId`；`agent-host/goal-runner-host.mjs` 中 Explorer / Verifier / 视觉复核的 `modelProviderId` 解析；`runtime-gateway/desktop-visual-review.mjs`（`supportsVision !== true` 时抛 `visual-review-vision-unavailable`）；`llm-config-store.mjs`（已接入模型与能力）；`chat-runtime/provider-recovery-broker.mjs`；`llm-chat-service.mjs` `recordConversationUsage`、usage request log。
- **允许改动**：新建 `packages/runtime-node/src/model-router.mjs`（桌面与 TUI 共用的适配，调用 protocol 的 `resolveRoleModel`）；`agent-host/*`；`settings-store.mjs` / `settings-application-service.mjs`（新增 `modelRouting` 设置的读写，默认值等价今天）；usage 记录增加 `role`；provider-recovery-broker 的候选过滤。
- **实现要点**：
  - 默认值：只有一个模型时四档都指向它，所有角色跟随档位，行为与今天完全一致。
  - Explorer / Verifier / 视觉复核按角色解析；视觉复核自动选能看图的模型；Verifier 优先不同源。
  - 故障切换只在过滤后的候选内进行。
  - 普通会话仍走 `resolveConversationModelProviderId`，不受影响。
- **必须新增的测试**：单模型行为不变；多模型时各角色解析正确；视觉复核不再因任务模型不能看图而失败；不同源复核；故障切换不越出项目范围；usage 记录带 role。
- **退出条件**：测试通过；桌面端完整测试通过；一次真实运行的视觉复核截图记录附在交接报告。

#### P1-PR7 「模型分工」设置页
- **级别**：B。
- **进入条件**：PR6 合入。
- **代码锚点**：设置页现有面板（`apps/desktop/renderer/src/app/components/` 下模型设置相关组件）；`settings-application-service.mjs`；`ipc/register-settings-ipc.mjs`；`bootstrapPreloadApi.ts`。
- **允许改动**：新建设置面板组件（放在现有设置目录下的新文件）；设置 IPC（新通道需进 channel catalog）；i18n 文案（`packages/i18n/src/index.ts`，中英文同时补）。
- **实现要点**：档位映射（主模型 + 备选）、角色表（跟随档位 / 固定 / 自动）、项目模型范围；读写全部经 main；界面参照 demo「设置 → 模型分工」。
- **必须新增的测试**：IPC 通道测试；面板状态纯函数测试；i18n 键完整性。
- **退出条件**：`ipc:check` 与桌面端完整测试通过；截图附在交接报告。

#### P1-PR8 开发者开关 projectAgentMode
- **级别**：C。
- **进入条件**：P0-1 完成。
- **代码锚点**：`ipc/register-settings-ipc.mjs` 的 `developer-settings:*`；开发者设置的存储（`DATA_STORE_ENTRIES.developerSettings`）；renderer 读取开发者设置的位置。
- **允许改动**：开发者设置的 schema 与默认值；renderer 读取开关的 hook；对应测试。
- **实现要点**：`projectAgentMode: boolean`，默认 `false`。本卡只加开关，不加任何行为。
- **必须新增的测试**：默认值、读写、重置。
- **退出条件**：测试通过。

---

### 第 2 阶段：骨架（开关后，0.0.20–0.0.21）

进入条件（所有卡）：ADR 80、81、83、84 为 `Accepted`；第 1 阶段全部合入；负责人确认本阶段基线分支。所有行为受 `projectAgentMode` 控制，关闭时零变化。

#### P2-1 带快照的子会话原语
- **目标**：把划词子会话的「父会话 + 继承背景快照」抽成通用原语，任务与划词共用。
- **必读**：运行时契约 §2.4；分层文档 §4.1 第 3 步。
- **代码锚点**：`packages/conversation-store/src/index.mjs`（`createSelectionChild`、`listSelectionChildren`、`captureInheritedBackground`）、`inherited-background.mjs`、`background-snapshot-store.mjs`；`apps/desktop/electron/main/selection-side-chat-service.mjs`。
- **允许改动**：conversation-store 与其类型声明、测试；selection-side-chat-service 改为调用新原语。
- **实现要点**：`createChildConversation({ parentConversationId, role, anchorMessageId, snapshotPolicy })`；会话元数据新增 `role`（`project_agent` / `work_session` / 缺省）与 `parentConversationId`；快照只由 main 按运行时事实捕获。
- **必须新增的测试**：划词子会话全部回归；新原语创建、快照覆盖到锚点为止、role 与父子关系持久化。

#### P2-2 SessionSupervisor 与调度能力（spawn / list / report / post_reply）
- **目标**：项目代理能开任务、查任务、发回复；`project_agent` 模式严格白名单。
- **必读**：运行时契约 §3、§4；分层文档 §4.1、§8.5；ADR 35。
- **代码锚点**：`runtime-gateway/local-goal-provider.mjs`（Provider 写法）、`tools/goal-tool-definitions.mjs`（`availableInModes` 写法）、`tools/runtime-projection-tool-materializer.mjs`、Explorer 严格白名单的实现、`chat-runtime/permission-gate.mjs`、`runtime-core` 的 `goal-idempotency` 账本。
- **允许改动**：新建 `runtime-gateway/local-delegation-provider.mjs`、`tools/delegation-tool-definitions.mjs`、`packages/runtime-node/src/project-agent/session-supervisor.mjs` 及测试；投影层加入 `project_agent` 模式；permission-gate 在该模式下对写类 kind 兜底拒绝。
- **实现要点**：深度限制（非 `project_agent` 调用 `spawn_session` 返回 `depth_limit`）；幂等键；锚点必填；结构化建 GoalPlan；`modelSelection` 与 `memorySnapshotId` 冻结进 `DelegationOrigin`；调度 Tool Result 进 EvidenceIndex。
- **必须新增的测试**：运行时契约 §12 中与白名单、深度、幂等、锚点、写类拒绝相关的条目。

#### P2-3 事件映射与收件箱
- **目标**：任务侧事实变化映射成 `DelegationEvent`，写入项目收件箱，至少一次 + 去重。
- **必读**：分层文档 §5.1–§5.3。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/event-mapper.mjs`、`project-inbox.mjs`、`session-messenger.mjs` 及测试；`DATA_STORE_ENTRIES` 登记 `delegationInbox`（scope：device）。
- **必须新增的测试**：事件 id 确定性；去重；游标只在回合成功后推进；重放；`message_session` 的投递时机与来源标注。

#### P2-4 记忆存储与基础工具（MM1）
- **目标**：记忆能写、能查、能撤；jsonl 真源 + 可重建 SQLite 索引。
- **必读**：ADR 81；记忆架构文档 §4、§9、§10。
- **允许改动**：新建 `packages/runtime-node/src/memory/*`、`runtime-gateway/local-memory-provider.mjs`、`tools/memory-tool-definitions.mjs` 及测试；`DATA_STORE_ENTRIES` 登记 `memory`（scope：portable 或 device，按 ADR 74 与负责人确认）。
- **实现要点**：只实现 `memory_search` / `memory_remember` / `memory_forget`；`stated` 只能来自用户消息锚点；敏感信息扫描复用 shell-redaction 规则；索引可从 jsonl 全量重建。
- **必须新增的测试**：记忆文档 §15 中与存储、`stated` 判定、撤销恢复、索引重建、敏感信息相关的条目。

#### P2-5 ProjectAgentRunner、回复与签收
- **目标**：代理回合（用户回合 / 唤醒回合）、回复挂靠与卡片生成、验证结论与策略代签。
- **必读**：分层文档 §6.5–§6.8、§8.1–§8.6；运行时契约 §2.5–§2.7、§5。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/runner.mjs`、`reply-composer.mjs`；`packages/system-context/src/sources/project-agent-source.mjs`、`project-roster-source.mjs`、`project-memory-source.mjs`（简报 + 用户偏好）并注册；`apps/desktop/electron/main/project-agent/project-agent-application-service.mjs`；`delegation:*` IPC（进 catalog）；签收写入走现有 `goalPlansRevise` + 关闭闸门。
- **实现要点**：单线程 actor；用户消息抢占唤醒回合；代签只在 `auto` 且代理已 `post_reply` 后发生，不接受 `userOverride`；卡片与结论标记只由 ReplyComposer 按投影生成。
- **必须新增的测试**：运行时契约 §12 与分层文档中和状态机、代签、卡片不可伪造、结论标记相关的条目。

#### P2-6 机器人生命周期：身份、新建、「熟悉项目」
- **目标**：每个工作区对应一个机器人（项目代理），懒创建其对话；机器人有名字与头像；新建机器人支持绑定已有文件夹与新建受管文件夹；首次打开发起只读「熟悉项目」任务并写入记忆。
- **必读**：ADR 84；产品稿 §1.1。
- **代码锚点**：`workspace-application-service.mjs`（`settings.workspaces` 条目）；P1-PR4 引入的 `workspaceId`；`DATA_STORE_ENTRIES`。
- **允许改动**：`project-agent-application-service.mjs`；工作区条目增加 `projectAgentConversationId`、`displayName`、`avatar`、`managed`；受管文件夹创建逻辑与根目录设置（默认 `~/Peer/`，登记为用户可见目录而非数据目录）；熟悉项目的任务模板（只读画像，不能写文件）；对应 IPC（进 catalog）。
- **实现要点**：
  - 头像由 `workspaceId` 确定性生成（形状 × 颜色），用户可改；名字默认取文件夹名，可改。
  - 新建空白机器人：名字 → 受管文件夹（重名追加序号）→ 注册为工作区；空文件夹的熟悉项目直接产出「这个机器人主要负责什么」的问题，回答写成 `stated` 职责记忆并固定进简报；建 README 只能由代理提议、用户同意后以任务执行。
  - 删除机器人不自动删除文件夹；受管文件夹删除需要二次确认。
- **必须新增的测试**：懒创建幂等；开关关闭时不创建；头像生成确定且不同 id 大概率不同；受管文件夹创建、重名、删除需二次确认；熟悉项目任务没有写能力；写入的记忆 `trust = verified` 且有证据引用；空白机器人的职责记忆为 `stated` 且固定。

#### P2-7 机器人列表、对话与档案界面
- **目标**：即时通讯式机器人列表（取代旧侧栏与工作台页面）、机器人对话、按需滑出的档案。
- **必读**：ADR 84；产品稿 §2；demo `design/product/project-agent-demo.html`（交互参照，不是实现代码）。
- **允许改动**：新建 `apps/desktop/renderer/src/project-agent/*`（`BotList`、`BotConversation`、`BotProfileDrawer` 等）及样式与测试；`App.tsx` 中按开关切换入口（只加分支，不迁移旧逻辑）；i18n；`delegation:*` 与机器人身份相关 IPC 的 renderer 适配。
- **不许改动**：`ChatSurface.tsx` 的功能代码；`Sidebar.tsx` 与工作台页面的行为（开关关闭时必须照旧）。
- **实现要点**：
  - 列表行：头像 · 名字 · 最后一条消息预览 · 时间 · 状态（需要你深色角标 / 未读小圆点 / 进行中）；按最近活动排序；顶部搜索、新建（+）、「需要你 N」筛选；底部我的头像与设置入口。没有市场入口。
  - 对话：锚定回复、处置标记、来源 / 结论 / 记忆标记、卡片；主动消息带时间分隔。
  - 档案：概况 · 任务 · 目标 · 记忆 · 设置（名字与头像、模型分工覆盖与范围、这个机器人的主动性），默认收起；点「来源：某任务」打开档案并定位任务现场。
  - 所有状态来自 main 的投影；卡片动作只调用已有 IPC。
- **必须新增的测试**：列表排序与筛选的纯函数测试；行状态（需要你 / 未读 / 进行中）由投影计算；开关关闭时新界面不出现、旧侧栏与工作台照旧；档案打开与定位；卡片动作只调用已有 IPC。

---

### 第 3–5 阶段：卡片清单（派发前由负责人细化成与第 1 阶段同等粒度）

| 阶段 | 卡号 | 内容 | 参照 |
|---|---|---|---|
| 3 | P3-1 | 需要你冒泡（权限 / 决策 / 计划批准，两处同解） | 运行时契约 §6；M6 |
| 3 | P3-2 | 插话：回答 / 并入 / 停止；引用限定范围 `AnchorScopeResolver` | 分层文档 §5.4、§8.3 |
| 3 | P3-3 | 按需披露：`get_verification_detail`、证据芯片；`verify_session` | 运行时契约 §2.7 |
| 3 | P3-4 | 主动性档位、`set_proactivity`、今日小结 | ADR 80 决策 9；运行时契约 §5.1.1 |
| 3 | P3-5 | 事件卡、项目简报、记忆进上下文、开任务冻结记忆（MM2） | 记忆文档 §4.2–§6 |
| 3 | P3-6 | Memory Curator 与准入策略（MM3） | 记忆文档 §5 |
| 3 | P3-7 | 失败唤醒与停滞检测（M8 基础） | 分层文档 §7 |
| 4 | P4-1 | ExecutionScheduler：槽位、优先级、依赖；接 `canRunPlan` | 分层文档 §4.2 |
| 4 | P4-2 | IsolationPlanner 与自动 worktree；取代、恢复、排队 | 分层文档 §4.3、§8.3 |
| 4 | P4-3 | 项目目标 OB1–OB3（共享 Scheduler、WatchRunner、只读探测、自主档位） | ADR 82 |
| 4 | P4-4 | 熔断、取消级联、重启恢复顺序（M8 完整） | 分层文档 §7.4–§7.6 |
| 4 | P4-5 | 记忆过期、冲突、衰减（MM4） | 记忆文档 §7 |
| 5 | P5-1 | 旧工作区迁移为机器人、旧会话归为历史任务；旧侧栏与工作台页面退场；退掉代理输入框的模式切换器 | 产品稿 §5 P5；ADR 84 |
| 5 | P5-2 | TUI 接入项目代理 | ADR 80；`apps/tui` |
| 5 | P5-3 | 远程入口对接项目代理 | ADR 74；路线图 #4 |
| 5 | P5-4 | 结果时间线（M9）、程序性记忆 → Skill Patch 候选（MM5） | 分层文档 §6.4；记忆文档 §14 |

---

## 8. 交接报告模板

PR 描述与交接回复都用这个格式：

```markdown
## 卡片
P1-PRx <名称>

## 分支与提交
- 分支：PeerAgent/pa/...
- 提交：<hash> <message>（逐条）
- PR：<链接>

## 改了什么
- <文件>：<一句话>
（只列实际改动；与卡片「允许改动」对照）

## 与卡片的偏差
- 无 / <偏差及原因>

## 验证
- 命令：`...`
  结果：<通过数 / 失败数，失败项名称>（真实输出摘要）
- 新增测试：<文件与用例名>
- 未运行的检查：<哪项，为什么>

## 架构影响（B 级及以上必填）
- <IPC / 执行路径 / 存储 / 上下文 的变化>

## 文档偏差
- 无 / <文档说 X，代码实际是 Y>

## 未完成与后续
- <下一张卡需要知道的事、留下的 seam、已知风险>
```

---

## 9. 边界变更请求模板

遇到 §3 列出的情况时，停下并提交：

```markdown
## 边界变更请求
- 卡片：<卡号>
- 触发：<卡片要求 / ADR 条款 / 现有代码事实>
- 冲突点：<具体到文件与条款>
- 选项：
  1. <做法 A>：影响……
  2. <做法 B>：影响……
- 建议：<哪一个，为什么>
- 在得到答复前我不会：<列出暂停的动作>
```

---

## 10. 派活提示词模板

负责人把任务派给其他模型时，可以直接使用：

```text
你负责 Peer-Agent 项目代理落地的任务卡 <卡号>。

1. 先读代码仓 AGENTS.md，然后读知识库 playbook/project-agent-implementation-handbook.md
   的 §0–§6 和你的任务卡，再读卡片「必读」列出的文档与「代码锚点」列出的文件。
2. 基线分支是 <分支名>。从它拉分支 PeerAgent/pa/<卡号小写>-<英文短名>。
   开工前 git status 必须干净；如有不属于你的改动，停下告诉我。
3. 第一条回复只写开工确认：分支名、要改的文件、实现要点、要补的测试。不要写代码。
4. 严格遵守手册 §2 铁律；只改卡片「允许改动」里的文件；需要越界时按 §9 提交边界变更请求。
5. 完成后 push 并用 gh 向基线分支开 PR，不要自己合并；PR 描述和最终回复都按 §8 交接模板。
6. 没有真实运行的测试结果，不要说完成。
```

---

## 11. 负责人检查清单（审 PR 时）

- [ ] 只改了卡片允许的文件；`main.mjs` 净增 ≤ 0；`ChatSurface.tsx` 无功能新增；`sendMessage` 无新增参数（PR2 的 `turnProfile` 除外）。
- [ ] 新 IPC 有协议类型并在 catalog 中；新存储已登记 `DATA_STORE_ENTRIES`。
- [ ] 新能力走能力链；权限与真值不在 renderer。
- [ ] 开关关闭时行为不变的测试存在（第 2 阶段起）。
- [ ] 交接报告里的测试结果是真实输出；新增测试覆盖卡片列出的条目。
- [ ] 架构影响、文档偏差已写清。
