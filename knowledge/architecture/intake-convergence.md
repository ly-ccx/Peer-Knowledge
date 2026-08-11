# Intake 契约收敛状态机与审计口径

创建时间：2026-08-11
最后更新：2026-08-11
状态：已落地（修复 + 审计埋点已合入 peer_agent）
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）

关联文档：

- `knowledge/decisions/16-skill-call-lifecycle.md` — Skill 调用生命周期与授权
- `knowledge/architecture/24-goal-runner-context-checkpoint-and-seamless-resume.md` — Goal 自驱工作流持久化
- `knowledge/architecture/20-architecture-governance.md` — 端云能力代理治理基线

## 一、结论与架构决策

本文记录 Goal/聊天模式下 **intake 契约**（首答阶段的任务意向占位契约）从创建、收敛到删除的完整状态机，以及 2026-08-11 修复的「中断任务被误删、跑到讨论区」缺陷与新增审计埋点口径。

核心决策：

1. **intake 契约不是一次性探针**：它代表「用户可能下达了任务」的意向占位。只要契约还存在，任务总览就必须展示它（含「执行中断」态）。
2. **收敛决策是纯函数**：`decideIntakeConvergence(activePlan, outcome)` 是唯一删除闸门，落在 `@peer-agent/runtime-node`，可单测。
3. **中断升级为「待用户确认」**：首答回合被打断（用户停止/流错误）后，契约打 `runner.interruption` 标记，即使后续回合正常结束也保留在任务页，直到用户显式「放弃」。
4. **删除必须留痕**：每次静默删除与中断打标都追加一条结构化审计事件到 `intake-convergence.jsonl`，未来可定量回答「并发/中断漏了多少任务」。

## 二、Intake 契约收敛状态机

```text
用户首答（goal 模式）
      │
      ▼
createIntakeContract(conversationId)     契约 status=executing，任务页「执行中 0/1」
      │
      ▼ 首答回合结束（convergeIntakeAfterGoalTurn）
      │
      ├─ decision='skip'（契约已升级 accepted_goal / 无契约）
      │     └─ 不处理，落入 Runner 自驱推进
      │
      ├─ decision='keep' + 回合被打断（aborted/error）
      │     ├─ setRunnerState: interruption={source:'stream_interrupted',...}
      │     ├─ 审计: intake_convergence action=mark_interrupted
      │     └─ 任务页显示「执行中断」，等待用户「继续」或「放弃」
      │           ├─ 继续 → resumeRunner 清标记 → 推进中
      │           └─ 放弃 → goalPlans:delete → deletePlan → 契约删除
      │
      ├─ decision='keep' + requestedUserInput（模型澄清提问）
      │     └─ markRequestedUserInput → 等待用户下一轮回复
      │
      └─ decision='remove'（纯问答/咨询，回合正常结束）
            ├─ 审计: intake_convergence action=delete_plan（删除前）
            └─ deletePlan → 契约消失，会话回到普通聊天/讨论
```

### 状态迁移表

| 前置状态 | 触发 | 决策 | 后置状态 |
|---|---|---|---|
| intake (executing) | 模型调用 goal_create_plan | skip | accepted_goal → Runner |
| intake (executing) | 回合 error/aborted | keep | intake + interruption（执行中断） |
| intake + interruption | 任何后续正常回合 | keep（新规则） | intake + interruption（保留） |
| intake (executing) | outcome.requestedUserInput | keep | intake + waiting_user |
| intake (executing) | 回合 done 且无标记/无提问 | remove | 删除契约（纯问答） |

## 三、本次修复（2026-08-11）

### 缺陷现象

用户中断一个并发任务后，任务从任务页消失，变成未读会话出现在首页「正在讨论」。

### 根因

intake 契约首答被中断后，**当轮**收敛器看到 `terminalStatus='aborted'/'error'` 会 keep；但用户下一轮补发消息（如「继续」）回合正常结束（`done`）时，收敛器按旧规则把它当「纯问答」→ `remove` → `deletePlan`。契约被静默删除后，任务总览只剩未读会话，于是投影进「正在讨论」（`source='conversation'`）。

### 修复（peer_agent 已合入）

1. `packages/runtime-node/src/goal-intake-convergence.mjs`
   - `decideIntakeConvergence` 新增：`activePlan.runner.interruption` 存在 → 即使 outcome 正常结束也 `keep`。
2. `apps/desktop/electron/main/main.mjs`
   - `convergeIntakeAfterGoalTurn`：中断打标（`setRunnerState` 写 `interruption`）+ 两处审计埋点。
3. `apps/desktop/renderer/src/app/pages/TasksPage.tsx`
   - 「执行中断」卡片新增「放弃」按钮 → `goalPlansDelete({planId})`（复用现成 `goalPlans:delete` IPC → `deletePlan`）。

### 测试

- `goal-intake-convergence.test.mjs`：+3 用例（曾中断 keep / 纯问答 remove 回归 / 升级 skip）
- `goal-plan-store.test.mjs`：+2 用例（审计字段完整性 / 追加语义）
- goal 系列 3 文件 136/136 全绿；desktop typecheck 通过。

## 四、审计事件口径（intake-convergence.jsonl）

### 存储位置与读取入口

- 文件：`<goal-plan-store storeDir>/intake-convergence.jsonl`（默认在 data-home 的 goal-plans 目录下，scope=portable，随迁移）
- 写入：`goalPlanStore.appendIntakeConvergenceAudit(entry)`（追加式 JSONL，失败仅 `console.warn` 不阻塞主流程）
- 读取：`goalPlanStore.getStoreDir()` 定位目录后按行解析；每行一个 JSON 对象

### 事件结构

```jsonc
{
  "event": "intake_convergence",        // 事件名固定
  "action": "delete_plan",              // delete_plan | mark_interrupted
  "decision": "remove",                 // remove | keep | skip（收敛器决策）
  "reason": "pure_qa",                  // 见 reason 取值表
  "conversationId": "conv-xxx",         // 关联会话
  "planId": "plan-xxx",                 // 被收敛的 intake 契约
  "terminalStatus": "done",             // 回合终态：done/aborted/error/...
  "createdAt": "2026-08-11T08:00:00Z",  // 事件时间戳
  "writerPid": 12345                    // 写入进程（多窗口并发时区分）
}
```

### action × reason 口径

| action | reason | 含义 |
|---|---|---|
| delete_plan | pure_qa | 纯问答/咨询，回合正常结束，契约静默删除（**统计「并发漏任务」的核心事件**） |
| mark_interrupted | terminal_aborted | 首答被用户停止，契约升级为「执行中断」待确认 |
| mark_interrupted | terminal_error | 首答流错误，契约升级为「执行中断」待确认 |

### 定量统计入口（未来）

- **并发漏任务估算**：`delete_plan + pure_qa` 且同一时段（如某窗口期）的条数，减去用户明确「放弃」删除的条数（goalPlans:delete 路径，可在 delete_plan 后补记 reason=user_abandon 区分）。
- **中断影响面**：`mark_interrupted` 条数（升级为待确认，不再静默漏）。
- **按会话/时间窗聚合**：`conversationId`、`createdAt` 字段支持按会话或按日期分组。

## 五、并发漏任务排查入口

1. **现象定位**：首页「正在讨论」里的卡片 = 无 GoalPlan 的未读会话。若该会话本应是任务，说明契约已被收敛删除或从未建立。
2. **查审计**：`grep '"action":"delete_plan"' <storeDir>/intake-convergence.jsonl`，按 conversationId 过滤，看删除时间与 reason。
3. **查中断升级**：`grep '"action":"mark_interrupted"' <storeDir>/intake-convergence.jsonl`，确认中断契约是否保留在任务页。
4. **存量会话**：`delete_plan` 事件自 2026-08-11 埋点上线后开始记录；更早的存量删除无法回溯（无历史埋点）。

