# 82. 项目目标与定时 / 事件驱动推进

创建时间：2026-09-24
最后更新：2026-10-01

## 状态

Accepted（2026-10-01）。方向由用户于 2026-09-24 选定；负责人于 2026-10-01 明确授权自行推进全部 B4。执行代理完成开工技术评审，见 `playbook/v0.1.0/b4-04-objectives.md`。此记录不声称存在额外人工或独立 Review 票。

## 级别

A 级。新增跨任务的协议对象、后台触发与探测、项目代理的自主开任务来源、调度器复用边界。

## 关联

- `knowledge/decisions/80-project-agent-delegation-model.md`（项目代理、锚定回复、签收策略、决策 9 主动开口）
- `knowledge/decisions/81-project-agent-memory-system.md`（记忆；目标状态沉淀为「局面」类记忆）
- `knowledge/decisions/62-automation-runtime-boundary.md`（Scheduler、幂等、missed / overlap 策略、Grant）
- `knowledge/architecture/project-agent-delegation-runtime.md`、`project-agent-capability-layers.md`
- `design/product/muse-personal-agent-research.md` §2.3（Muse Goals 与定时 / 事件驱动）

## 背景

ADR 80 的项目代理是**消息驱动**的：用户说一句，代理开任务，任务结束汇报。很多真实工作不是一句话能交代完的，而是一个持续一段时间的目标：「0.0.18 发版前把已知 bug 修掉」「把 desktop 测试稳定下来」「盯着上游 SDK 新版本，出了就评估升级」。这类工作需要代理：

1. 记住目标本身，而不只是记住某条任务；
2. 定期检查进展或外部变化，而不是等用户来问；
3. 发现变化时自己判断：开任务、调整计划、告诉用户，还是什么都不做。

Muse 用 Goals + 定时 / 事件驱动做到了这一点。Peer 已有 Automation（ADR 62）的调度能力，但 Automation 每次触发新开一个会话、独立执行，不属于项目代理，也没有「目标」这一层。

## 决策

### 1. 新对象：项目目标（`ProjectObjective`）

产品面叫「项目目标」。代码名用 `ProjectObjective`，**不用 Goal**，因为 Goal 已被 GoalPlan 与 Goal 模式占用。

```ts
interface ProjectObjective {
  objectiveId: string;
  workspaceId: string;                 // ADR 81 的稳定项目标识
  projectAgentConversationId: string;
  originMessageId: string;             // 锚定：哪条用户消息立的这个目标
  title: string;
  outcome: string;                     // 达成是什么样子
  successSignals: ObjectiveSignal[];   // 目标级的达成信号（可由探测判定）
  milestones: { id: string; title: string; sessionIds: string[]; status: 'pending' | 'active' | 'done' | 'dropped' }[];
  watches: ObjectiveWatch[];           // 定时 / 事件触发
  autonomy: 'report_only' | 'propose' | 'act'; // 触发后代理能做到哪一步
  budget: { maxAutoSessionsPerDay: number; maxProbeRunsPerDay: number; maxTokensPerDay?: number };
  deadline?: string;
  status: 'active' | 'paused' | 'achieved' | 'abandoned';
  createdBy: 'user_request' | 'agent_proposal';
  createdAt: string;
  updatedAt: string;
}
```

- 目标不是 GoalPlan 的父表，也不是 Task 表：它是项目代理维护的一份跨任务计划，里面挂着若干任务（`sessionIds`）。任务仍然是签收与证据的单位。
- 用户说出持续性目标时，代理用 `create_objective` 建立并锚定到那条消息；代理自己提议的目标（`agent_proposal`）必须用户确认后才生效。

### 2. 触发：`ObjectiveWatch`

```ts
type ObjectiveWatch =
  | { watchId: string; kind: 'schedule'; schedule: AutomationSchedule; probe: ObjectiveProbe }
  | { watchId: string; kind: 'event'; source: WatchEventSource; probe?: ObjectiveProbe };

type WatchEventSource =
  | { type: 'task_event'; filter: 'failed' | 'ended' | 'verified' }       // 本目标下任务的事件（内部）
  | { type: 'git'; ref: string; on: 'new_commits' | 'new_tag' }          // 本地 git 读取
  | { type: 'files'; paths: string[]; debounceMs: number };               // 工作区文件变化

type ObjectiveProbe =
  | { type: 'deterministic'; check: 'git_ref' | 'file_hash' | 'command'; spec: Record<string, unknown> }
  | { type: 'agent'; question: string };  // 只读子 agent 探测：CI 状态、issue、依赖发布等
```

- **定时**复用 ADR 62 的 Scheduler 模块：`nextRunAt` 是事实、timer 只是唤醒优化；幂等键 `objectiveId + watchId + scheduledAt`；missed 默认 `run_latest`，overlap 默认 `skip`；启动 / 唤醒 / 时间变化时对账。**共用 Scheduler 模块，不共用 AutomationDefinition**：目标触发不新开会话，只产生观察结果交给项目代理。
- **事件**：P1 只做内部与本机来源（任务事件、本地 git、工作区文件），不开入站网络。外部状态（CI、issue、依赖发布）一律通过定时探测拉取，不做 webhook。
- **探测一律只读**：确定性探测优先（git ref、文件哈希、只读命令的退出码与输出摘要）；需要理解的用只读探测子 agent（复用 Explorer 执行路径，`observe` 级授权，走能力链与 Evidence；默认「省」档模型，ADR 83）。探测没有副作用，不能写文件、不能对外写。

### 3. 观察结果只在「变了」时往上报

```ts
interface WatchObservation {
  objectiveId: string;
  watchId: string;
  observedAt: string;
  digest: string;          // 结果摘要的哈希，用于判断是否变化
  changed: boolean;        // 与上次 digest 不同
  summary: string;         // 一两句，叙述，不是证据
  evidenceRefs: string[];  // 探测的工具结果
  severity: 'info' | 'notable' | 'urgent'; // 确定性规则先给（失败、截止临近、安全公告），探测子 agent 可以上调，不能下调
}
```

- `changed = false` 只记录，不进收件箱（沿用 Automation `succeededOnlyOnChange` 的思路）。
- `changed = true` 产生 `DelegationEvent { type: 'objective_signal' }` 进项目代理收件箱，是否唤醒、是否打扰用户由 ADR 80 决策 9 的 SurfacingPolicy 决定。

### 4. 触发后代理能做到哪一步：`autonomy`

| 档 | 触发后代理可以 | 典型来源 |
|---|---|---|
| `report_only` | 只汇报（或按主动性档位进小结） | 「盯着，有变化告诉我」 |
| `propose`（默认） | 汇报并提出下一步，附「开始」一键动作；用户点了才开任务 | 代理提议的目标；用户没说可以自己动手 |
| `act` | 自己开任务推进，事后汇报 | 用户明说「发现就直接修」 |

- `act` 开出的任务照常过签收策略与权限审查：对外操作仍然 `confirm`，验证不过线不代签。
- 预算硬限：每个目标每天自动开任务数、探测次数、token 上限；超了停止自动推进并告诉用户。沿用 ADR 80 的 CircuitBreaker：同一目标下连续失败达到阈值即熔断。

### 5. 锚定回复

目标相关的汇报回复挂在目标的 `originMessageId` 上（「回复『发 0.0.18 前把已知 bug 修掉』」），用户一眼知道是哪件事。目标触发开出的任务，`DelegationOrigin.anchorMessageId` 同样指向这条消息，并额外带 `objectiveId`。

### 6. 达成与收尾

- 达成条件：所有未放弃的里程碑完成，且 `successSignals` 经探测判定成立。代理汇报「目标达成」，目标转 `achieved`；这是记账，不是交付，所以自动完成并告知，用户可以说「还没完」重新打开。
- 截止临近而未达成：`severity = urgent`，按 SurfacingPolicy 必达。
- 目标的进展沉淀为 ADR 81 的「局面」类记忆（短有效期），达成后转为事件卡的一部分。

### 7. 能力暴露

新增调度工具（`LocalDelegationProvider`，项目代理可见）：

| 工具 | 作用 | 约束 |
|---|---|---|
| `create_objective` | 立目标（标题、达成样子、里程碑、watches、autonomy、预算） | 必须锚定用户消息；代理提议的走确认卡 |
| `update_objective` | 调整计划、里程碑、watches | `autonomy` 只能由用户消息触发的调用上调 |
| `pause_objective` / `close_objective` | 暂停 / 放弃 / 标记达成 | — |
| `list_objectives` / `get_objective` | 查询 | 只读 |

watches 的执行不经过代理：Scheduler 与事件源在 main 进程里运行，探测走能力链，结果进收件箱。

### 8. 界面

- 右栏新增「目标」标签：每个目标一张卡，显示达成样子、里程碑进度、下一次检查时间、最近一次观察、autonomy 档位、预算用量；可暂停、调整、放弃。
- 目标卡与任务清单互链：任务卡显示所属目标。

## 后果

- 项目代理从「等你说」变成「盯着目标推进」；用户少了「去看看 CI」「再问一下进度」这类督促。
- 多了一类后台开销（探测、代理唤醒），用预算、只在变化时上报和 SurfacingPolicy 共同压住。
- Automation 与项目目标并存：Automation 仍适合「每天早上独立跑一次报告」这类与项目代理无关的定时任务；以后可以提供「把这个 Automation 交给项目代理」的迁移，不在本 ADR 范围。
- Scheduler 从 Automation 内部模块升级为共享模块，需要抽出接口并补测试。

## 不做什么

- 不做入站 webhook / 开放端口（ADR 31 出站优先仍然有效）。
- 探测不做任何写操作。
- 代理自己提议的目标不自动生效；`autonomy` 不能由代理自己上调。
- 不把目标做成 GoalPlan 的父表或新的 Task 表。


## B4-05 设备观察运行态（2026-10-01）

便携目标声明与全部观察仍沿 projects 根保存；设备 `project-runtime/<workspaceId>/objectives/watch-state.json` 保存下一次/上次定时、探测预算预约、执行与 Inbox 投递幂等游标。真实观察能力的 Call、observe Grant、Result/Evidence 与 observation 保存在同目录 `probe-evidence/<execution-sha256>.json`，不能把模型摘要或调用者给的引用当作实际执行。新增子路径已登记版本计划 §7.1；导出不迁移预算、执行游标或设备探测记录。

“CI 挂了才告诉我”以当前 canonical 用户语义保存 failure_only 通知策略，健康首次检查仍保存事实、不唤醒。预算在异步探测开始前落盘（目标 UTC 日限与项目滚动一小时 60 次），重启不重置。Evidence 后中断修复观察，观察后通知中断沿同一 eventId 补投递，不重复实际探测。代理探测使用 objective_probe 省档路由和既有临时 Explorer，Projection 与能力/路径硬闸独立于 full-access/权限缓存；读取必须限定真实项目路径，写入、shell、外部能力不可执行。

## B4-06 自主动作运行态（2026-10-01）

实施契约见 `playbook/v0.1.0/b4-06-autonomy.md`。设备 actions-state.json 持久化冻结提议、UTC 日自动任务预约、观察事实批次幂等和真实任务链接；GoalPlan origin 的 objectiveActionId 连接实际创建与恢复。用户点击沿既有 canonical 输入回答入口，执行仍沿 DelegationProvider 与既有 Grant/Evidence。显式 autoAccept 批准需真实用户锚点复核，缺失不生效。
