# 项目代理落地 · 执行手册（给执行模型）

创建时间：2026-09-25
最后更新：2026-09-26

> 用途：把 0.1.0（机器人列表与项目代理，ADR 80–85）的落地工作派给任何模型时，执行方必须遵守的约定与交接格式。  
> 地位：执行层合同。方向与边界以 ADR 80–85 和 `design/product/v0.1.0-release-plan.md` 为准；本手册与它们冲突时，以 ADR 为准，并提交「边界变更请求」（§9）。  
> 任务卡：`playbook/v0.1.0/`（总目录 `README.md`）。本手册不再收录卡片。  
> 负责人：用户（仓库所有者）。执行方：被派发任务卡的模型。  
> 关联：`design/product/v0.1.0-release-plan.md`（版本计划）、`knowledge/architecture/project-agent-capability-layers.md`（模块与步骤编号）、`knowledge/architecture/project-agent-delegation-runtime.md`（契约）、`knowledge/architecture/project-agent-memory-system.md`、ADR 80 / 81 / 82 / 83 / 84 / 85、代码仓 `AGENTS.md`

---

## 0. 一分钟版

1. 你只做派给你的那一张任务卡；卡片外的文件不改。
2. 开工前按 §1 的顺序读文档，并确认卡片的「依赖」都已合入、A 级卡对应 ADR 为 `Accepted`；不满足就停下汇报。
3. 从 `PeerAgent/dev/0.1.0` 拉自己的分支；不要在别人有未提交改动的分支上工作。
4. 遵守 §2 铁律；拿不准时选更保守的做法，并在交接报告里写明。
5. 完成后按 §8 模板交接：改了什么、怎么验证的（原样贴命令和结果摘要）、和卡片有什么偏差。
6. 没有证据不说「完成」。测试没跑、跑不了、有失败，都如实写。

---

## 1. 开工前必读（按顺序）

| 顺序 | 读什么 | 为什么 |
|---|---|---|
| 1 | 代码仓 `AGENTS.md` | 仓库治理基线：能力链、分层、禁令、变更分级、Git 同步 |
| 2 | 本手册 §2–§5 | 执行约定 |
| 3 | `playbook/v0.1.0/README.md` | 卡片字段、热点文件冲突表、统一命名、通用退出条件 |
| 4 | 你的任务卡（在 `playbook/v0.1.0/` 对应阶段文件里） | 本卡范围 |
| 5 | `design/product/v0.1.0-release-plan.md` §3（代码基线）与你这张卡所在的阶段 | 现状事实与上下游 |
| 6 | 任务卡「必读」列出的 ADR 与架构文档章节 | 契约与不变量 |
| 7 | 任务卡「代码锚点」列出的文件 | 现状（行号以 `rg` 重新定位为准） |

知识库根目录按代码仓 `AGENTS.md` 的解析顺序定位（环境变量 `PEER_KNOWLEDGE_ROOT` → `.peer-workspace.local.json` → 同级目录 `Peer-Knowledge` / `peer-knowledge`）。不要把本机绝对路径写进任何仓库。

---

## 2. 铁律

违反任何一条，交付即视为不合格，需要返工。

### 2.1 范围与分支

1. **只做一张卡。** 只改卡片「允许改动」列出的文件与目录；需要改清单外的文件时，先停下提交边界变更请求（§9），不要顺手改。
2. **不碰别人的在制改动。** 开工前 `git status` 必须干净；若基线分支上有不属于你的未提交改动，停下汇报，不要 stash、不要提交、不要覆盖。
3. **分支规则。** 从 `PeerAgent/dev/0.1.0` 拉分支，命名 `PeerAgent/pa/<卡号小写>-<英文短名>`，例如 `PeerAgent/pa/b1-01-turn-sink`。一张卡一个分支、一个 PR（卡片注明可拆的，拆成的每个 PR 用 `b1-07a` 这样的后缀）。
4. **Git 同步。** 本地 commit 后同一轮 push 到远端自己的分支；用 `gh pr create --base PeerAgent/dev/0.1.0` 开 PR，**不要自己合并**，除非负责人明确授权。
5. **禁止危险操作。** 不 `push --force` 共享分支，不 `reset --hard` 别人的提交，不改 git 配置，不跳过 hooks（`--no-verify`）。
6. **不动发版物。** 不改 `VERSION`、`release-notes/`、`.github/workflows/`、`electron-builder.yml`、`CHANGELOG.md`、README 的版本标记，除非卡片明确要求（发布卡 `B*-R`、`GA` 与 `P0-5`）。
7. **不加依赖。** 不新增 npm / cargo 依赖，不新增顶层 package，除非卡片明确允许。SQLite 用运行时自带的 `node:sqlite`（B1-08）。
8. **不碰用户数据。** 不删除、不迁移真实的 `~/.peer-agent`；测试用临时目录，手动验证用 `dev:lab`（`~/.peer-agent-lab`）。迁移逻辑必须可重复执行、写前备份或原子写。

### 2.2 架构（来自代码仓 `AGENTS.md` 与 ADR 80–85，逐条可检查）

1. **一条能力链。** 任何新能力（调度、记忆、目标、探测）都走 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。不另开执行通道。
2. **Renderer 只做表达。** 不用 `fs` / `child_process`；权限、签收、调度、记忆的真值都在 main 进程或 `runtime-node`；renderer 只读投影、只发结构化命令。
3. **跨进程用协议对象。** 新的 IPC payload 必须在 `packages/protocol` 或 `bootstrapPreloadApi.ts` 有类型；新通道必须进 `apps/desktop/electron/ipc/channels.mjs` 并通过 `pnpm --filter @peer-agent/desktop ipc:check`。
4. **大文件不再变大。**
   - `apps/desktop/electron/main/main.mjs`：每个 PR 的净增行数 ≤ 0（只允许装配调用替换，不允许新增业务逻辑）。
   - `ChatSurface.tsx`、`Sidebar.tsx`、`LlmSettingsPanel.tsx`、`apps/tui/src/app.tsx`：不新增功能代码；新界面放 `apps/desktop/renderer/src/project-agent/`、`apps/tui/src/project-agent/`。
   - `llm-chat-service.mjs` 的 `sendMessage` 参数表：整个 0.1.0 只允许新增**一个**参数 `turnProfile`（B1-02 引入），之后的新字段都放进 `turnProfile`。
5. **可移植优先。** 桌面与 TUI 都要用的逻辑（Provider 本体、工具定义、模式白名单、调度、记忆、目标、列表投影）放 `packages/runtime-node`；桌面只做装配与 Electron 适配（照 `local-mcp-provider.mjs` 的再导出写法）。
6. **提示不是护栏。** 权限、模式、范围限制必须在投影层或执行层强制，不能只写在 system prompt。
7. **上下文分层。** 新的上下文内容只能经注册的 Context Source 进入；工具结果、文件内容、记忆、任务报告、目标观察只能进事实层（`L7_CONTINUITY`），代理规则进 `L1_AGENT`；不把工具输出提升为系统指令。
8. **存储登记。** 新的本机持久化路径必须登记在 `packages/runtime-node/src/data-store.mjs` 的 `DATA_STORE_ENTRIES`，并写明 scope（device / portable / cache）。版本计划 §7.1 是完整清单。
9. **只加不改。** 已有存储只新增字段与文件；不改写旧会话 jsonl；需要改写设置时写迁移（B1-05 框架），写前备份。
10. **开关与默认。** beta.3 的 B3-10 合入前，所有用户可见行为受 `settings.json` 的 `developer.projectAgentMode` 控制，关闭时行为、界面、存储写入与改动前一致（必须有测试证明）；B3-10 之后改为 `projectAgent.shell`，经典界面必须零变化。
11. **分级门槛。** A 级卡只有在对应 ADR 状态行为 `Accepted` 时才能开工。开工前打开 ADR 文件确认状态；是 `Proposed` 就停下汇报。
12. **遗留代码。** 碰到违反治理基线的旧代码，不扩大违规；能顺手移向正确 seam 就移，移不动就在交接报告里指出下一处 seam。

### 2.3 测试与诚实

1. 测试会 import 各包的 `dist/`，跑测试前先构建（§4）。
2. 按卡片「必须新增的测试」补齐；修 bug 先写能复现的失败测试。
3. 提 PR 前必须跑：卡片列出的定向测试 + 受影响包的完整测试 + `pnpm typecheck` + `pnpm architecture:check`。
4. 回归基线：2026-09-26 在 `main` a087988c（macOS）上 `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm test` 全绿（desktop 4927 / 5 skipped，runtime-node 599，TUI 710）。**不能新增失败或 skip**；以 P0-3 更正后的代码仓 `AGENTS.md` 为准。
5. 不删除、不跳过、不放宽已有测试来让自己通过。确实需要隔离时，写明原因并在交接报告里列出。
6. 交接报告里的测试结果必须是真实运行的输出摘要；没跑就写「未运行」和原因。
7. 需要模型参与的集成测试用脚本化回合执行器（B1-02 的 `createScriptedTurnExecutor`），不调真实模型；卡片要求「真实运行」的另附记录。

### 2.4 文档

1. 架构知识只写进 `peer-knowledge`，不在代码仓新建 `docs/architecture/*`。
2. 执行方默认**不修改** ADR、版本计划与架构文档；发现文档与代码不符时，在交接报告里写「文档偏差」，由负责人决定改哪边。
3. 每个 beta 发布时由负责人（或被指派的执行方）更新版本计划 §5.2 与交付状态清单 D10。
4. 代码注释只写代码表达不了的约束，风格与周边代码一致；不写「这里修改了什么」「为什么这样改是对的」这类过程说明。

---

## 3. 标准工作流程

```text
领卡
 → 读（§1）→ 核对依赖与 ADR 状态（不满足：停，汇报）
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
- 发现某个不变量在现有代码里做不到；
- 卡片写的代码锚点符号不存在（行号漂移不算）。

---

## 4. 验证命令

需要 Node ≥ 22.18（测试直接运行 `.ts`）、pnpm 10.22.0、Bun（TUI）。

```bash
pnpm install --frozen-lockfile
pnpm build                                   # 测试依赖各包 dist，先构建
pnpm --filter @peer-agent/desktop ipc:check  # 新增或修改 IPC 通道后必跑
node --test apps/desktop/electron/main/<某个>.test.mjs   # 定向测试（在仓库根执行）
pnpm --filter @peer-agent/desktop test       # 桌面端完整测试
node --test packages/protocol/src/*.test.ts  # 协议包测试（该包没有 test 脚本，直接跑）
pnpm --filter @peer-agent/runtime-node test
pnpm --filter @peer-agent/system-context test
pnpm --filter @peer-agent/conversation-store test
pnpm --filter @peer-agent/tui test           # bun test
pnpm --filter @peer-agent/gateway test       # 改网关时（B5-04）
pnpm typecheck
pnpm architecture:check
pnpm dev:lab                                 # 手动验证用隔离数据目录 ~/.peer-agent-lab
```

并行跑全量测试时，依赖计时的桌面测试可能偶发 `cancelledByParent`；单独重跑该文件确认。`node --test` 在非 TTY 下输出 TAP 摘要，可加 `--test-reporter=tap` 统计 `# pass` / `# fail`。

---

## 5. 统一术语与命名

| 概念 | 产品面 | 代码名 | 说明 |
|---|---|---|---|
| 项目代理 | 机器人（界面称谓）/ 项目代理 | `project_agent`（会话角色 / 模式 / 模型角色），`ProjectAgentRunner` | 每个 Workspace 一个（ADR 84） |
| 机器人档案 | 名字 · 头像 | `BotProfile`，`projects/<workspaceId>/profile.json` | 不写进 `settings.workspaces`（ADR 85 决策 7） |
| 受管文件夹 | — | `~/Peer/<名字>/`（`projectAgent.managedRoot` 可配置） | ADR 84、85 |
| 档案 | 档案 | `BotProfileDrawer` | 按需滑出：概况 · 任务 · 目标 · 记忆 · 设置 |
| 任务 | 任务 | `work_session`（会话角色）、`WorkSession`（投影）、`session_worker`（模型角色） | 子 Conversation + GoalPlan |
| 执行宿主 | — | `AgentTurnExecutor`、`TurnSink`（`BroadcastSink` / `CollectingSink` / `CallbackSink`） | 跑一轮 agent，不依赖窗口 |
| 回合画像 | — | `turnProfile`（`sendMessage` 唯一新参数） | 角色、项目、任务、模型选择、上下文 |
| 宿主租约 | — | `HostLease`，`project-runtime/<id>/host.lease` | 每个项目只有一个宿主（ADR 85） |
| 输入 | — | `ProjectInput`，`input-queue.jsonl` | 所有入口的用户消息都走这里 |
| 待批准 | 需要你批准 | `PendingApproval`，`approvals.jsonl` | 持久；重启后为 `stale` |
| 模型分工 | 模型分工 | `ModelRouter`、`resolveRoleModel`、档位 `strong/fast/economy/vision` | ADR 83 |
| 项目标识 | — | `workspaceId`（UUID），真源 `projects/registry.json` | ADR 81、85；与远程委托共用 |
| 项目目标 | 项目目标 | `ProjectObjective`、`ObjectiveWatch` | 代码里不用 Goal，避免与 GoalPlan 冲突 |
| 记忆 | 记忆 | `MemoryItem`、`MemoryEpisode`、`MemorySnapshot` | ADR 81 |
| 签收 | 签收 / 需要你确认 | `resultAcceptance.acceptedBy: 'policy' \| 'user'` | ADR 80 决策 8 |
| 送达 | 推送 / 只进对话 / 今日小结 / 不打扰 | `decideSurfacing` → `interrupt/message/digest/silent` | ADR 80 决策 9；系统通知的唯一来源（ADR 85 决策 4） |
| 开关 | — | `developer.projectAgentMode`（beta.1–beta.2）→ `projectAgent.shell`（beta.3 起） | — |

新目录约定：

- 主进程执行宿主：`apps/desktop/electron/main/agent-host/`
- 主进程项目代理装配：`apps/desktop/electron/main/project-agent/`
- 可移植运行时：`packages/runtime-node/src/project-agent/`、`packages/runtime-node/src/memory/`、`packages/runtime-node/src/sqlite/`、`packages/runtime-node/src/model-router.mjs`、`project-registry.mjs`、`settings-migrations.mjs`、`testing/`
- 协议：`packages/protocol/src/delegation.ts`、`memory.ts`（替换旧遗留类型）、`model-routing.ts`、`project.ts`、`objectives.ts`
- 上下文来源：`packages/system-context/src/sources/project-agent-source.mjs`、`project-roster-source.mjs`、`project-memory-source.mjs`、`work-session-origin-source.mjs`
- 界面：`apps/desktop/renderer/src/project-agent/`；设置面板 `apps/desktop/renderer/src/app/components/settings/`
- TUI：`apps/tui/src/project-agent/`

---

## 6. 并行关系

见 `playbook/v0.1.0/README.md` §4（热点文件冲突表）与各阶段文件开头的并行图。同一时间，同一文件只允许一张卡在改。派发前负责人检查冲突。

---

## 7. 任务卡

见 `playbook/v0.1.0/`：

| 阶段 | 文件 | 卡号 |
|---|---|---|
| M0 准备 | `m0-prep.md` | P0-1 … P0-6 |
| beta.1 地基 | `beta1-foundation.md` | B1-01 … B1-12、B1-R |
| beta.2 骨架 | `beta2-skeleton.md` | B2-01 … B2-17、B2-R |
| beta.3 可日用 | `beta3-daily.md` | B3-01 … B3-11、B3-R |
| beta.4 并行与主动 | `beta4-parallel.md` | B4-01 … B4-08、B4-R |
| beta.5 多入口 | `beta5-surfaces.md` | B5-01 … B5-05、B5-R |
| rc 与正式版 | `rc-release.md` | RC-01 … RC-06、GA |

旧卡号对照：P1-PR1 → B1-01；P1-PR2 → B1-02 + B1-03；P1-PR3 → B1-04；P1-PR4 → B1-06；P1-PR5 → B1-07；P1-PR6 → B1-09；P1-PR7 → B1-10；P1-PR8 → B1-11；P2-1 → B1-12；P2-2 → B2-01 + B2-03 + B2-04；P2-3 → B2-05；P2-4 → B2-10；P2-5 → B2-07 + B2-08 + B2-09 + B2-11 + B2-13；P2-6 → B2-12；P2-7 → B2-14 + B2-15 + B2-16；P3-x → B3-x；P4-x → B4-x；P5-1 → B3-09 + B3-10；P5-2 → B5-01 + B5-02；P5-3 → B5-03 + B5-04 + B5-05；P5-4 → 0.1.x。

---

## 8. 交接报告模板

PR 描述与交接回复都用这个格式：

```markdown
## 卡片
B1-0x <名称>

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
你负责 Peer-Agent 0.1.0 的任务卡 <卡号>。

1. 先读代码仓 AGENTS.md，然后读知识库 playbook/project-agent-implementation-handbook.md
   的 §0–§5、playbook/v0.1.0/README.md，再读你的任务卡（playbook/v0.1.0/<阶段文件>），
   以及卡片「必读」列出的文档与「代码锚点」列出的文件。
2. 基线分支是 PeerAgent/dev/0.1.0。从它拉分支 PeerAgent/pa/<卡号小写>-<英文短名>。
   开工前 git status 必须干净；如有不属于你的改动，停下告诉我。
3. 第一条回复只写开工确认：分支名、要改的文件、实现要点、要补的测试。不要写代码。
4. 严格遵守手册 §2 铁律；只改卡片「允许改动」里的文件；需要越界时按 §9 提交边界变更请求。
5. 完成后 push 并用 gh 向 PeerAgent/dev/0.1.0 开 PR，不要自己合并；PR 描述和最终回复都按 §8 交接模板。
6. 没有真实运行的测试结果，不要说完成。
```

---

## 11. 负责人检查清单（审 PR 时）

- [ ] 只改了卡片允许的文件；`main.mjs` 净增 ≤ 0；`ChatSurface.tsx` / `Sidebar.tsx` / `LlmSettingsPanel.tsx` / TUI `app.tsx` 无功能新增；`sendMessage` 无新增参数（B1-02 的 `turnProfile` 除外）。
- [ ] 新 IPC 有协议类型并在 catalog 中；新存储已登记 `DATA_STORE_ENTRIES`，且与版本计划 §7.1 一致。
- [ ] 新能力走能力链；权限与真值不在 renderer；桌面与 TUI 共用的逻辑在 runtime-node。
- [ ] 开关关闭 / 经典界面下行为不变的测试存在。
- [ ] 只加不改：旧会话文件未被改写；设置变更有迁移与备份。
- [ ] 交接报告里的测试结果是真实输出；新增测试覆盖卡片列出的条目；CI 通过。
- [ ] 架构影响、文档偏差已写清。
