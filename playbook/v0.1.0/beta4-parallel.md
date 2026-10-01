# beta.4 并行与主动（`0.1.0-beta.4`）

创建时间：2026-09-26
最后更新：2026-10-01

> 主题：一个机器人同时推进多件事且互不污染；机器人按项目目标主动盯事；异常与重启都能收住。  
> 用户可见：多任务并行、自动 worktree 与合回、取代后可恢复、项目目标（定时 / git / 文件 / CI）、熔断提示、记忆过期与冲突提示。  
> 进入条件：beta.3 已发布；ADR 82 为 Accepted。  
> 通用退出条件见 `README.md` §6。

并行关系：

```text
B4-01 → B4-02 → B4-03
B4-01 → B4-07
B4-04 → B4-05 → B4-06
B4-08（独立）
```

---

## B4-01 ExecutionScheduler：槽位、优先级、依赖

代码 [#77](https://github.com/ly-ccx/Peer-Agent/pull/77) 与知识 #8 已于 2026-10-01 按负责人授权合入；入队计龄与缺失依赖展示问题已修复，本地门禁与双平台 CI 均通过。交接见 [B4-01 报告](b4-01-handoff.md)。

实施边界与负责人批准的路径补齐见 [B4-01 实施契约](b4-01-execution-scheduler.md)。依据 ADR 80 推进本卡；ADR 82 已于 2026-10-01 完成执行代理技术评审并 Accepted，项目目标卡 B4-04 至 B4-06 依此实施。

- **级别**：A。**规模**：M。**依赖**：B2-04。
- **目标**：取代 beta.2 的「每个项目最多 1 个」串行队列；按槽位、优先级、依赖调度任务。
- **必读**：分层文档 §4.2。
- **代码锚点**：`session-supervisor.mjs` 的排队逻辑；`goal-runner.mjs` 的 `canRunPlan` 与 `sessions` Map（无全局槽位）；Explorer 并发池（默认 5，硬顶 8）。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/execution-scheduler.mjs` 与测试；`session-supervisor.mjs`（改用调度器）；`goal-runner-host.mjs`（`canRunPlan` 同时查询调度器）；设置（`projectAgent.concurrency`）；档案设置项与 i18n。
- **实现要点**：
  - 槽位：每个项目写任务槽 1 个（隔离为 worktree 的写任务不占这个槽，见 B4-02）、只读任务槽 2 个；全局运行上限 4（可配置 1–8）。
  - 优先级：`high`（用户明确说急）> `normal` > `low`（目标触发）；同优先级先来先服务；排队超过 30 分钟的任务优先级临时提升一级（防饿死）。
  - 依赖：`dependsOn` 中任一任务未 `accepted` 就不启动；依赖失败或取消时，该任务转 `waiting_user` 并生成卡片（「前置任务未成功签收，要取消还是重新安排？」）；回答不自动跳过依赖。
  - 排队状态持久化到 `project-runtime/<id>/scheduler.json`，重启后按原顺序恢复。
  - 任务投影带 `queuedBehind`（排在谁后面），界面显示「排队中：等『X』完成」。
- **必须新增的测试**：槽位上限（项目 / 全局）；优先级与防饿死；依赖成功 / 失败；重启恢复顺序；只读任务不被写任务阻塞。
- **退出条件**：测试通过。

---

## B4-02 IsolationPlanner、自动 worktree 与合回

代码 [#78](https://github.com/ly-ccx/Peer-Agent/pull/78) 已于 2026-10-01 按负责人授权合入（`faa25d9c`），实施契约见 [B4-02 边界](b4-02-worktree-isolation.md)，验证与三 worktree 真实 Git 场景见 [交接](b4-02-handoff.md)。最终提交 `7819b883` 的本地门禁与双平台 CI 全部通过，Review 两条意见已处理；负责人已授权自行推进全部 B4。

- **级别**：A。**规模**：L（可拆 B4-02a 决策与创建，B4-02b 合回与清理）。**依赖**：B4-01。
- **目标**：并行的写任务各自在 worktree 里干活；验收后按现有交付流程合回；冲突变成需要你。
- **必读**：分层文档 §4.3；ADR 69（合回冲突判定）；ADR 79（交付绑定跟随实时 HEAD）。
- **代码锚点**：`goal-worktree-adapter.mjs`（复用 automation worktree）；`goal-delivery-handoff.mjs`（合回、冲突 verdict）；`packages/runtime-node/src/goal-delivery-binding.mjs`（`resolveWorkspaceHead`、`attachWorkspaceHeadBinding`）；GoalPlan `deliveryBinding.executionIsolation`。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/isolation-planner.mjs` 与测试；`session-supervisor.mjs`（开任务时调用）；`goal-runner-host.mjs`（接 worktree adapter）；`acceptance.mjs`（代签后触发合回）；`card-projection.mjs`（合回冲突卡）。
- **实现要点**：
  - 决策（开任务时，写进 `deliveryBinding.executionIsolation`）：只读 → `none`；写任务且没有其他进行中的写任务、工作区干净 → `none`（原地，与今天一致）；写任务且已有进行中的写任务或工作区有未提交改动 → `worktree`；非 git 目录 → `none` 且串行（占写任务槽）。
  - `spawn_session.isolation` 可指定 `none` / `worktree` / `auto`（默认 `auto`）；指定 `none` 但会与进行中的写任务冲突时，改为排队并告诉代理原因。
  - 合回：签收（策略或用户）之后调用现有交付流程；冲突按 ADR 69 判定，生成「合回冲突」卡（选项：让任务自己解决 / 我来处理 / 放弃这次改动）。
  - 清理：合回成功或任务取消后删除 worktree；失败的任务保留 7 天再清理；磁盘剩余不足 2 GB 时不再新建 worktree，改为排队并提示。
- **必须新增的测试**：决策矩阵每一格；并行两个写任务各自 worktree；合回成功 / 冲突；清理与保留期；磁盘不足。
- **退出条件**：测试通过；真实运行「三条写任务并行并各自合回」一次。

---

## B4-03 取代、恢复、排队全链路

代码 [#79](https://github.com/ly-ccx/Peer-Agent/pull/79) 已于 2026-10-01 按负责人授权合入（`46c2af0e`），实施契约见 [B4-03 边界](b4-03-session-continuity.md)，验证见 [交接](b4-03-handoff.md)。最终提交 `910f456f` 的完整本地门禁及双平台 CI 通过，代码与知识三条 Review 意见均修复/解决。

- **级别**：A（ADR 80 决策 7）。**规模**：M。**依赖**：B4-01、B4-02、B3-02。
- **目标**：用户改主意时旧任务被取代但不丢；说「还是按原来的」可以恢复；排队的任务可以调整。
- **允许改动**：`session-supervisor.mjs`、`delegation-provider.mjs`、`tool-specs.mjs` 与测试；`goal-plan-store.mjs`（`supersededBy` 字段）；`tools/prompts/delegation/*.md`；渲染层处置标记与任务分组。
- **实现要点**：
  - `spawn_session.supersedes: sessionId`：旧任务暂停（不取消），状态 `superseded`，记录 `supersededBy`；工作成果保留（worktree 不删）。
  - 新工具 `resume_session { sessionId, anchorMessageId }`：恢复被取代或暂停的任务，同时暂停取代它的任务（若仍在进行）。
  - 新工具 `reprioritize_session { sessionId, priority, anchorMessageId? }`。
  - 取代链在档案任务页可见（「被『Y』取代」「恢复」按钮）。
  - 被取代超过 7 天未恢复 → 自动取消并清理，事件通知代理（静默送达）。
- **必须新增的测试**：取代 → 恢复 → 再取代；成果保留；7 天自动清理；排队调整。
- **退出条件**：测试通过。

---

## B4-04 项目目标存储与工具（OB1）

代码 [#82](https://github.com/ly-ccx/Peer-Agent/pull/82) 已于 2026-10-01 合入（2172597a），最终 bc55d53b 完整门禁、双平台 CI 与三条 Review 修复通过；见 [实施契约](b4-04-objectives.md)与[交接](b4-04-handoff.md)。

- **级别**：A（ADR 82）。**规模**：M。**依赖**：B1-07、B2-03。
- **目标**：用户可以给机器人一个持续性的目标；目标可查、可改、可暂停；目标与它触发的任务相互关联。
- **必读**：ADR 82 §1–§3。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/objective-store.mjs` 与测试；`tool-specs.mjs`、`delegation-provider.mjs`（目标工具）；`mode-policy.mjs`（白名单）；`data-store.mjs`（`projects/` 下子目录，不新增条目）；新 IPC `project-objectives:*`；渲染层 `ObjectivesTab.tsx`；i18n。
- **实现要点**：
  - 存储：`projects/<workspaceId>/objectives/objectives.json`（当前定义）+ `observations.jsonl`（观察记录）。
  - 工具：`create_objective { title, successCondition, watches[], autonomy, anchorMessageId }`（必须锚定用户消息）、`update_objective`、`pause_objective`、`resume_objective`、`list_objectives`。
  - 目标状态：`active / paused / achieved / abandoned`；达成条件由代理判断并必须引用观察或任务证据。
  - 目标触发的任务在 `DelegationOrigin.objectiveId` 记录来源；目标卡显示「由此目标开的任务」。
  - 目标页：列表、状态、上次检查、下次检查、最近观察、自主档位；用户可以直接改档位与暂停。
- **必须新增的测试**：存储读写；无锚点创建被拒；状态流转；目标与任务关联。
- **退出条件**：测试通过。

---

## B4-05 WatchRunner 与触发器（OB2）

实现已推送代码 #83、知识 #14；完整门禁与真实只读 CI 查询记录见 [交接](b4-05-handoff.md)。Review/双平台 CI 待最终提交，未合入。

- **级别**：A（ADR 82）。**规模**：L（可拆 B4-05a 定时与共享调度器，B4-05b git / 文件 / CI）。**依赖**：B4-04。
- **目标**：目标按定时或事件检查；只在观察到变化时唤醒代理。
- **代码锚点**：`packages/runtime-node/src/automation-scheduler.mjs`（reconcile、错过策略、重叠策略、全局暂停，60 起）；`automation-schedule.mjs`（时间表种类）；`packages/protocol/src/automation.ts`（只有时间表触发，无事件）；`goal-delivery-binding.mjs` `resolveWorkspaceHead`。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/{watch-runner.mjs, probes/schedule-probe.mjs, probes/git-probe.mjs, probes/file-probe.mjs, probes/ci-probe.mjs}` 与测试；`automation-scheduler.mjs`（抽出可复用的调度内核，Automation 行为不变）；`event-mapper.mjs`（`objective_observation`）。
- **实现要点**：
  - 定时：复用 Automation 调度内核（同一套时间表种类、错过与重叠策略），命名空间 `objective-watch`，与用户的 Automation 定义互不可见。
  - git：每 60 秒读 HEAD 与分支引用（宿主只读函数，不调用模型）；变化 = 新提交 / 切分支。
  - 文件：`fs.watch` 监听目标声明的路径模式（限定在工作区内，忽略 `node_modules`、`.git`、构建产物目录），5 秒防抖。
  - CI：`gh` 可用且已登录时，用只读命令（`gh run list --json …`）按间隔查询；不可用时该触发器状态为「不可用：原因」，不报错。探测命令由宿主执行，不经模型，不经 Shell Provider 的询问流程（只读白名单，写在代码里并有测试）。
  - 观察：每次探测产生 `WatchObservation`（带 `digest`）；`diffWatchObservation` 判定有变化才写 `observations.jsonl` 并发事件；没有变化什么都不做。
  - 预算：每个项目每小时最多 60 次探测；需要解读内容（如 CI 失败日志）时由代理决定是否开只读任务或用 `objective_probe` 角色做一次临时解读。
  - 目标暂停 / 机器人删除 / 经典界面下均停止探测。
- **必须新增的测试**：每种触发器的变化判定；无变化不唤醒；预算上限；CI 不可用降级；Automation 回归全绿（抽内核后行为不变）；路径限定在工作区内。
- **退出条件**：测试通过；真实运行「CI 挂了才告诉我」一次。

---

## B4-06 自主档位（OB3）

- **级别**：A（ADR 82）。**规模**：S。**依赖**：B4-05。
- **目标**：每个目标可以设「只报告 / 先提议 / 直接做」。
- **允许改动**：`project-agent-source.mjs`（规则）；`delegation-provider.mjs`（`spawn_session` 带 `objectiveId` 时的校验）；`acceptance.mjs`；`card-projection.mjs`（提议卡）。
- **实现要点**：
  - `report_only`：只汇报观察，运行时拒绝带该 `objectiveId` 的 `spawn_session`。
  - `propose`：代理发提议卡「要我开任务处理吗？」，用户同意后才开。
  - `act`：可以直接开任务；这些任务的签收一律 `confirm`（除非用户在目标上显式允许自动签收）；每个目标每天最多自动开 3 个任务，超出转为提议。
- **必须新增的测试**：三档行为；每日上限；`act` 任务签收为 `confirm`。
- **退出条件**：测试通过。

---

## B4-07 熔断、取消级联、重启恢复

代码 [#80](https://github.com/ly-ccx/Peer-Agent/pull/80) 已于 2026-10-01 按负责人授权合入（54a937d5）。最终 f2a6d321 的本地完整门禁及双平台 CI 通过，十个实际强杀恢复点通过，Review 删除事务与两项知识清单偏差均已修复。见 [实施契约](b4-07-recovery.md) 与 [交接](b4-07-handoff.md)。

- **级别**：B。**规模**：M。**依赖**：B4-01。
- **目标**：连续失败会停下来告诉用户；取消会把相关的东西一起收干净；任何时刻强杀进程，重启后按固定顺序恢复。
- **必读**：分层文档 §7.4–§7.6。
- **允许改动**：新建 `packages/runtime-node/src/project-agent/{circuit-breaker.mjs, recovery.mjs}` 与测试；`runner.mjs`、`session-supervisor.mjs`、`project-agent-host.mjs`（装配恢复顺序）。
- **实现要点**：
  - 熔断：同一项目代理回合连续失败 5 次 → 打开 10 分钟，期间不自动唤醒，对话里显示卡片（可手动重试）；同一任务的工具失败循环沿用 Goal Runner 的 `noProgressLimit`。
  - 取消级联：取消任务 → 中止其 Explorer / Verifier → 依赖它的排队任务转 `waiting_user`（卡片询问）；删除机器人 → 取消全部任务、停止目标、释放租约。
  - 重启恢复顺序：获取租约 → 输入队列消费者 → 收件箱按游标重放 → 调度器恢复排队 → 进行中的任务按 ADR 73 恢复 → WatchRunner → 小结定时器。任一步失败只影响该项目，写诊断，不阻塞其他项目。
- **必须新增的测试**：熔断打开与关闭；级联；在全链路各节点强杀子进程（`kill -9`）后重启，结果与未中断一致（无重复消息、无重复任务、无丢失输入）。
- **退出条件**：测试通过。

---

## B4-08 记忆过期、冲突、衰减（MM4）

代码 [#81](https://github.com/ly-ccx/Peer-Agent/pull/81) 已合入（8d607ea3），最终 8811af15 的完整门禁、双平台 CI 与 Review 修复通过。见 [交接](b4-08-handoff.md)。

- **级别**：A（ADR 81）。**规模**：M。**依赖**：B3-07。
- **目标**：记忆不会越积越乱：过期的自动失效，矛盾的会问用户，引用的文件变了会重新核实。
- **必读**：记忆架构文档 §7。
- **允许改动**：新建 `packages/runtime-node/src/memory/{maintenance.mjs, conflict.mjs}` 与测试；`memory-store.mjs`；`card-projection.mjs`（冲突卡）；记忆页显示过期与冲突。
- **实现要点**：
  - 过期：带 `expiresAt` 的到期失效；推断偏好 90 天未被使用 → `expired`；固定项与职责不过期。
  - 冲突：新条目与已有条目主题相同而内容矛盾（由 Curator 标注主题键，运行时比较）→ 两条都标 `conflicted`，生成冲突卡让用户选。
  - 重新核实：`verified` 事实引用的文件在之后的提交里变了 → 标记待核实，下次熟悉项目或相关任务时重新验证；待核实期间在简报里注明「可能已过时」。
  - 维护任务每天随小结定时器跑一次，不调用模型（冲突判定的主题键来自 Curator 已有输出）。
- **必须新增的测试**：过期、冲突、待核实三条路径；固定项不过期；维护不调用模型。
- **退出条件**：测试通过。

---

## B4-R 发布 `0.1.0-beta.4`

- **步骤**：版本计划 §10 检查单。
- **证据**：版本计划 §12.1 beta.4 一行。
- **退出条件**：prerelease 生成；版本计划 §5.2 更新。
