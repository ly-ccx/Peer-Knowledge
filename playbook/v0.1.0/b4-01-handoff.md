## 卡片
B4-01 ExecutionScheduler（Beta4：槽位、优先级、依赖）。代码 #75/#76 和知识 #5/#7 已按负责人授权合入；从更新后的开发线推进本卡。

## 分支与提交
知识分支同名，目标 main；代码目标 PeerAgent/dev/0.1.0。
- e22a522：调度实施契约先于代码。
- 3b23a65：记录路径补齐批准。
- 483f97b：同步核验租约交接契约。
- 30a88d6：priority 存储路径批准。
- 7418e76：失败依赖卡片路径批准。
- 分支：`PeerAgent/pa/b4-01-execution-scheduler` → `PeerAgent/dev/0.1.0`
- 提交：`9c53bc69` feat(project-agent): implement Beta4 execution scheduler
- 代码 PR：[Peer-Agent #77](https://github.com/ly-ccx/Peer-Agent/pull/77)
- 知识 PR：[Peer-Knowledge #8](https://github.com/ly-ccx/Peer-Knowledge/pull/8)；契约提交先于代码。

## 改了什么
- `runtime-node/src/project-agent/execution-scheduler.mjs` 及测试：每项目 1 原地写/2 只读槽，真实 worktree 独立；全局 4 回合（设置 1–8）、high/normal/low、FIFO、30 分钟升一级、原子排序持久化、依赖签收闸门、取消/finally 租约。
- `session-supervisor.mjs` 及测试：先预留再非阻塞启动；批准/终态/取消/签收晋升，失败依赖持久化 waiting_user，启动失败不遗留占用，保留取代原子性。
- `goal-plan-store.mjs`、`runtime-node/src/index.ts`、`digest.mjs` 及测试、`tool-specs.mjs`：priority 持久化、模块导出、并发设置校验、既有 priority enum。
- `agent-turn-executor.mjs`、`goal-runner-host.mjs`、`project-agent-host.mjs` 及集成测试：共享调度器；工作/代理/Explorer/Verifier/视觉回合取槽；取消排队回合不调用 Provider；同步独立核验让出后重新取得租约，支持并发 1。
- `project-facts.mjs` 及测试：失败依赖直接投影用户决策卡，回答沿已有输入入口处理取消/重排，不自动跳过依赖。
- `protocol/src/delegation.ts` 及测试、`drawerState.ts` 及测试、`TasksTab.tsx`：宿主 queuedBehind/queueReason 事实和展示。
- `BotSettingsTab.tsx`、drawer 契约测试、settings application 测试、i18n：自定义 Dropdown 全局并发 1–8，所有机器人共享，经原 settings API 保存。
- 既有 `tools/prompts/delegation/spawn_session.md` 同步调度说明。

## 与卡片的偏差
- 原允许路径不足以接入全局回合、类型投影、生产装配及存储校验，三次清单补齐均获负责人明确批准并先写入知识实施契约。
- 失败依赖卡提供取消/重排；不会把回答解释为越过 accepted 依赖闸门。
- 全局租约是一次宿主 runTurn，内部 Provider 恢复保留同一租约。高优先级遵守硬上限；同步 verify_session 在宿主 seam 交接租约，避免上限 1 死锁。

## 验证
- `pnpm build`：通过；`pnpm typecheck`：通过；`pnpm architecture:check`：通过。
- `pnpm test`：全仓通过；runtime-node 851/851，desktop 5154 通过、5 既有跳过，system-context 29/29，TUI 712/712，其他包及 marketplace/changelog 均通过。
- `node --test packages/protocol/src/*.test.ts`：172/172。
- 新增测试覆盖项目/全局上限、读写并行、真实 worktree 判定、优先级/防饿死、签收/失败/外项目依赖、重启 FIFO、取消等待和活动回合、核验交接、重复准入、启动失败、宿主共享装配、卡片和设置保存。
- 双平台 CI：[run 36820249563](https://github.com/ly-ccx/Peer-Agent/actions/runs/36820249563) Ubuntu/macOS 均通过，验证代码 `9c53bc69f8cdcbdd571c94aa5c36e536a9c87cd5`；证据 [JSON](evidence/b4-01-validation-20261001.json)。未发布 Beta4，未运行 B4-02 的三 worktree 写任务合回验收。

## 架构影响
- A 级：ExecutionScheduler 为深模块，监督者负责 Plan 转换；回合租约在宿主内共享。排序事实在已登记 device 根 `project-runtime/<workspaceId>/scheduler.json`；Plan、权限、签收与 Evidence 仍走原真源。
- 不新增 IPC、工具、依赖；main.mjs 无改动。Renderer 只表达宿主事实。

## 文档偏差
- 分层文档 §4.2 的旧额度、P0 借槽和依赖 result_ready 选项与 Accepted ADR 80/B4-01 不一致，本次知识 PR 对齐实施契约。
- ADR 82 仍为 Proposed，本卡授权不表示接受项目目标决策。

## 未完成与后续
- B4-02 接真实 IsolationPlanner/自动 worktree/合回，B4-03 补取代继承与恢复，B4-07 完成熔断和跨进程重启恢复。
- B4-04–06 等待 ADR 82 Accepted；本卡不标记整个 Beta4 完成，不自行合并。
