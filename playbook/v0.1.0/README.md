# 0.1.0 任务卡总目录

创建时间：2026-09-26
最后更新：2026-10-10（补充 ADR 91 自主协调实施卡）

> 用途：把 0.1.0 的全部工作拆成可以单独派给任何模型执行的任务卡。  
> 地位：执行层合同。方向与范围以 `design/product/v0.1.0-release-plan.md` 与 ADR 80–85 为准；执行规矩以 `playbook/project-agent-implementation-handbook.md` 为准（本目录取代手册 §7 的旧卡片）。  
> 冲突时的优先级：ADR > 版本计划 > 本目录卡片 > 执行手册示例。发现冲突按手册 §9 提交边界变更请求。

---

## 1. 文件

| 文件 | 内容 |
|---|---|
| `m0-prep.md` | P0-1 … P0-6：开发线、ADR 评审、基线、CI、入口指引 |
| `beta1-foundation.md` | B1-01 … B1-12、B1-R：执行宿主、待批准、设置迁移、项目身份、协议、SQLite、模型分工、开关、子会话原语 |
| `beta2-skeleton.md` | B2-01 … B2-17、B2-R：项目代理骨架与三件套界面（开关后） |
| `beta3-daily.md` | B3-01 … B3-11、B3-R：可日用能力、旧数据迁移、默认开启、全局入口 |
| `beta4-parallel.md` | B4-01 … B4-08、B4-R：并行、隔离、项目目标、恢复、记忆维护 |
| `beta5-surfaces.md` | B5-01 … B5-05、B5-R：TUI 与远程入口 |
| `rc-release.md` | RC-01 … RC-06、GA |
| `autonomous-coordination.md` | R91-01 … R91-05：主 Bot 自主协调、并行资源、取消重派、事件推进与安装版验收；ADR 91 已认可，实施未开始 |

---

## 2. 派活前负责人检查

1. 卡片的「依赖」全部已合入 `PeerAgent/dev/0.1.0`。
2. 卡片的「级别」为 A 时，对应 ADR 状态行是 `Accepted`（打开文件确认）。
3. 「允许改动」里的文件当前没有另一张卡在改（查 §4 冲突表与在途 PR）。
4. 派活提示词用手册 §10 模板，基线分支填 `PeerAgent/dev/0.1.0`。

---

## 3. 卡片字段

每张卡都有：目标 · 级别 · 规模 · 依赖 · 必读 · 代码锚点 · 允许改动 · 不许改动 · 实现要点 · 必须新增的测试 · 退出条件。部分卡另有「交接要点」（下一张卡需要知道的事）。

- **允许改动**里写「新建」的文件，路径必须一致；需要改清单外文件时停下提交边界变更请求。
- **代码锚点**的行号基于 `main` a087988c，执行时以 `rg` 重新定位为准；行号漂移不算文档偏差，符号不存在才算。
- **必须新增的测试**是下限，不是上限。
- **退出条件**全部满足才能开 PR。

---

## 4. 热点文件冲突表

以下文件多张卡都要碰。同一时间只允许一张卡在改；负责人按此表排队。

| 文件 | 会碰它的卡（按顺序） |
|---|---|
| `apps/desktop/electron/main/main.mjs` | B1-01 → B1-02 → B1-03 → B1-04 → B2-06 → B2-13（每张净增 ≤ 0 行） |
| `apps/desktop/electron/main/llm-chat-service.mjs` | B1-02（`turnProfile`）→ B1-03（`reattach` 快照）→ B1-09 → B2-01 → B2-02 → B2-11 |
| `apps/desktop/electron/main/chat-runtime/permission-gate.mjs` | B1-03 → B2-01 → B2-02 → B3-01 |
| `apps/desktop/electron/main/chat-runtime/goal-mode-gate.mjs` / `projected-tool-executor.mjs` | B2-01 |
| `apps/desktop/electron/main/agent-host/goal-runner-host.mjs` | B1-04（新建）→ B1-09 → B2-02 → B2-06 → B4-01 → B4-02 |
| `packages/runtime-node/src/goal-plan-store.mjs` | B2-04 → B2-09 → B4-03 |
| `packages/runtime-node/src/project-agent/mode-policy.mjs` | B2-01（新建）→ B2-03 → B2-10 → B3-05 → B4-04 |
| `packages/runtime-node/src/project-agent/tool-specs.mjs` / `delegation-provider.mjs` | B2-03（新建）→ B2-10 → B3-02 → B3-03 → B3-04 → B3-05 → B4-03 → B4-04 → B4-06 |
| `packages/runtime-node/src/project-agent/session-supervisor.mjs` | B2-04（新建）→ B2-09 → B3-01 → B3-02 → B4-01 → B4-02 → B4-03 → B4-07 |
| `packages/runtime-node/src/project-agent/card-projection.mjs` / `reply-composer.mjs` | B2-08（新建）→ B3-01 → B3-05 → B3-07 → B4-02 → B4-06 → B4-08 |
| `packages/conversation-store/src/index.mjs` | B1-12 |
| `packages/runtime-node/src/data-store.mjs` | B1-03 → B1-06 → B1-08 → B2-10（每张只追加自己的条目） |
| `packages/system-context/src/prompt-assembler.mjs` | B2-11 |
| `packages/protocol/src/index.ts` | B1-07 → B5-03（只追加导出） |
| `apps/desktop/electron/ipc/channels.mjs` | B1-10 → B2-13 → B3-06 → B3-09 → B4-04 → RC-03（由 `sync-ipc-catalog.mjs` 生成的部分按脚本流程改） |
| `apps/desktop/renderer/src/App.tsx` | B2-14 → B3-10 → B3-11（只加入口分支） |
| `apps/desktop/renderer/src/app/components/SettingsPage.tsx` | B1-10 → B1-11 → B3-05 |
| `packages/i18n/src/index.ts` | 几乎所有界面卡；每张卡只追加自己的键，按命名空间分块（`projectAgent.*`、`modelRouting.*`、`developer.*`…） |
| `apps/tui/src/app.tsx` | B5-02 |

---

## 5. 统一命名（补充手册 §5）

| 概念 | 代码名 | 所在 |
|---|---|---|
| 项目注册表 | `projects/registry.json`、`createProjectRegistry` | `packages/runtime-node/src/project-registry.mjs` |
| 机器人档案 | `BotProfile`、`projects/<id>/profile.json` | `protocol/src/project.ts`、`runtime-node/src/project-agent/bot-profile-store.mjs` |
| 机器人列表项 | `BotListItem`、`projectBotListItem`、`sortBotList` | `protocol/src/project.ts` |
| 输入 | `ProjectInput`、`input-queue.jsonl` | `protocol/src/delegation.ts`、`runtime-node/src/project-agent/input-queue.mjs` |
| 宿主租约 | `HostLease`、`host.lease` | `runtime-node/src/project-agent/host-lease.mjs` |
| 待批准 | `PendingApproval`、`approvals.jsonl` | `protocol/src/delegation.ts`、`runtime-node/src/project-agent/approval-store.mjs` |
| 回合执行器 | `AgentTurnExecutor`、`TurnSink` | `apps/desktop/electron/main/agent-host/` |
| 脚本化回合执行器 | `createScriptedTurnExecutor` | `packages/runtime-node/src/testing/scripted-turn-executor.mjs` |
| 设置迁移 | `SETTINGS_MIGRATIONS`、`runSettingsMigrations` | `packages/runtime-node/src/settings-migrations.mjs` |
| SQLite 驱动 | `openSqlite`、`createFtsIndex` | `packages/runtime-node/src/sqlite/` |
| 壳层设置 | `projectAgent.shell: 'bots' \| 'classic'` | `settings.json` |
| 渲染层目录 | `BotListShell`、`BotList`、`BotRow`、`BotConversation`、`BotProfileDrawer`、`NewBotSheet`、`HistorySheet` | `apps/desktop/renderer/src/project-agent/` |

---

## 6. 通用退出条件（每张卡都要满足，卡内不再重复）

1. 只改了「允许改动」的文件；`main.mjs` 净增 ≤ 0；`ChatSurface.tsx`、`Sidebar.tsx`、`LlmSettingsPanel.tsx` 无功能新增；`sendMessage` 参数表除 B1-02 的 `turnProfile` 外无新增。
2. 本机跑过：卡内定向测试、受影响包完整测试、`pnpm typecheck`、`pnpm architecture:check`；改了 IPC 的跑 `pnpm --filter @peer-agent/desktop ipc:check`；改了 TUI 的跑 `pnpm --filter @peer-agent/tui test`。
3. 开发线 CI 通过（P0-5 上线后）。
4. beta.3 之前：开关关闭时，界面、行为、存储写入与改动前一致（有测试）。
5. 新增存储已登记 `DATA_STORE_ENTRIES`；新增 IPC 有协议类型、进 catalog。
6. 交接报告按手册 §8，测试结果是真实输出。
