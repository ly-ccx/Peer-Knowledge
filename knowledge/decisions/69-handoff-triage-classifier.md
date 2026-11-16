# 69. 合回分流（Triage）分类器：结构化 verdict 替代布尔判定

创建时间：2026-08-26
最后更新：2026-11-15（标明 Project Bot 模式下静默 `AUTO_MERGE` 由 ADR 80 决策 7–8 取代，且合回写入受 ADR 116 / 127 资源锁约束）

状态：Accepted（分类诊断保留；0.1.0 Project Bot 模式下 `AUTO_MERGE` 无确认自动合并已部分取代）

级别：B 级（改 handoff 执行层判定语义；`goal-delivery-handoff.mjs` 分类器、测试、协议文案）

关联：

- `knowledge/decisions/68-goal-delivery-mode-contract.md`（脏检查分级；本案接续其执行层缺口）
- `knowledge/architecture/20-architecture-governance.md`
- peer_agent `apps/desktop/electron/main/goal-delivery-handoff.mjs`
- peer_agent `packages/protocol/src/goal.ts`（`handoffStoppedReasonLabel` 文案）

## 背景

ADR 68 把合回脏检查从「porcelain 非空即挡」升级为三级（modified/staged 挡；untracked 无碰撞放行；同内容碰撞放行、异内容碰撞挡），并在 §5 提出「空壳任务线治理」方向——但只给了源头与存量两条原则，**未给出运行时分类判定**。落地后暴露两处执行层缺口，均由真实场景实测触发：

1. **`git status --porcelain` 折叠未跟踪目录**。全未跟踪目录（如 `demo/`）被折叠成单行目录条目 `?? demo/`，三级分级里的「同内容碰撞比对」分支根本不会触发——判定函数对目录条目只能保守挡。实测：工作区里 `demo/version-map.html` 与任务线版本逐字节一致（同 blob hash），仍被挡 `target_checkout_dirty`。修复方式：加 `-uall` 展开到单文件粒度（已随 P0 止血提交 `015fe81f`）。
2. **布尔判定无法区分「空壳 / 可自动合 / 已过时 / 真冲突 / 环境挡」五种本质不同的情形**。`isTargetCheckoutMergeable` 只回 `{ mergeable, identicalCollisions }`，所有「不合」统一糊成 `target_checkout_dirty` 一个 stoppedReason。工作台实测堆积 16 项「合不进源头」，其中绝大多数是空壳（领先 0、改动早已合进目标线）或同内容碰撞——本可静默消化，却全部亮红卡逼用户逐条验收。

用户视角的症结：验收对象被错置成了「每条任务线」（O(n) 次决断），而非「合并后的目标线是否符合预期」（O(1) 次决断）。

## 决策

### 1. 布尔判定升级为 Triage 分类器

`goal-delivery-handoff.mjs` 新增纯函数 `triageTaskLine`，不直接执行，只输出分类：

```js
triageTaskLine({ repositoryRoot, taskBranch, targetBranch, baseCommit }) -> {
  verdict: 'AUTO_CLEAN' | 'AUTO_MERGE' | 'STALE' | 'CONFLICT' | 'BLOCKED_ENV',
  reason: 结构化原因（供 UI 文案与 Evidence 落盘）,
  detail: {
    ahead, behind,                 // 任务线相对目标线的领先/落后提交数
    changedFiles: [...],           // baseCommit..taskBranch 变更集
    collisions: [{ path, kind }],  // 与目标工作区未跟踪文件的碰撞（kind: identical|different）
    blockingEntry,                 // BLOCKED_ENV 时的具体原因（tracked 脏 / git lock / 命令失败）
  },
}
```

分类规则（按判定顺序）：

| verdict | 判定条件 | 语义 |
|---|---|---|
| `AUTO_CLEAN` | `ahead === 0`（变更集为空，或任务线已被目标线包含）。**先于脏检查**：目标工作区 tracked 脏挡不住空壳「已进」事实 | 空壳：改动早已合进，静默标「已进」并清线 |
| `BLOCKED_ENV` | 仅在 ahead>0 时：tracked 工作区脏（modified/staged/deleted）、git lock、merge-base/diff 命令失败 | 环境挡：不丢数据但需用户先处理环境 |
| `CONFLICT` | 存在碰撞未跟踪文件且内容与任务线版本**不同** | 真冲突：合并会覆盖工作区内容，必须用户决断 |
| `AUTO_MERGE` | 有变更集，无 tracked 脏，碰撞仅同内容未跟踪文件（或无碰撞） | 可自动合：暂移同内容碰撞后 ff-only 合入 |
| `STALE` | `behind` 超过阈值（暂定 ≥20）且 `changedFiles` 与目标线当前内容 diff 为空（改动已失效） | 已过时：置灰一键清理，不打扰 |

`isTargetCheckoutMergeable` 保留作为 `verdict === 'AUTO_MERGE'` 的薄封装（向后兼容现有调用点），内部改为调用 `triageTaskLine`。

### 2. 处置语义

- `AUTO_CLEAN` / `AUTO_MERGE` / `STALE`：**系统自动消化，不进「需要你」队列**。AUTO_CLEAN/STALE 静默标记并归档；AUTO_MERGE 走原有暂移→合入链路。（**2026-11-15 对齐**：该规则仅保留于经典单对话合回；在 0.1.0 Project Bot 模式下，按 [ADR 80](80-project-agent-delegation-model.md) 决策 7–8，实质代码合入主工作区须由用户确认触发，不得静默执行 `AUTO_MERGE`。此外，所有暂移/合并写盘及 worktree 清理动作必须先取得并通过 [ADR 116](116-session-control-and-resource-settlement.md) / [ADR 127](127-unknown-outcome-reconciliation-and-delegated-resolution.md) 资源 claim 校验。）
- `BLOCKED_ENV`：维持现有 stopped + 重试，文案修正为「目标工作区有未提交的改动 / 环境暂不可用」，不再笼统说「改别的东西还没提交」。
- `CONFLICT`：唯一需要用户实质决断的情形。携带 `collisions` 清单，供后续收口视图（P2）批量呈现；本期先维持单卡 + 修正文案，但 verdict 数据已落盘可回溯。

### 3. 协议文案分层

`packages/protocol/src/goal.ts` 的 `handoffStoppedReasonLabel` 增加按 verdict 的区分文案：空壳/已过时不再映射为「合不进」（它们是 delivered/cleaned，不是 stopped）；`target_checkout_dirty` 拆为「有未提交改动」（tracked 脏）与「有同名文件挡路」（untracked 碰撞）。

### 4. Evidence

每次 triage 判定写一条 Evidence：verdict + reason + detail（ahead/behind/collisions）。自动动作（静默清理/自动合并）必须有对应 Evidence 可查。

## 非目标

- 不做真冲突的收口视图 UI（P2，另案）：本期只产出 verdict 数据结构与单卡文案修正。
- 不做落后任务线的自动 rebase（P3 评估）。
- 不做「两个都要」的内容三方合并：CONFLICT 里选择两个都要时只落到工作区交给用户手动合，不替用户合并内容。
- 不引入第二条 git 执行路径：triage 复用现有 handoff 链的 git 调用，是 `isTargetCheckoutMergeable` 的内部升级。

## 验收

- `goal-delivery-handoff.test.mjs` 新增分类器用例覆盖五类 verdict：空壳（AUTO_CLEAN）、同内容碰撞（AUTO_MERGE）、异内容碰撞（CONFLICT）、落后失效（STALE）、tracked 脏（BLOCKED_ENV）。
- 现有 19 个 handoff 测试全部通过，无回归。
- 分类器对真实仓库（当前 0.0.9 + 存量任务线）抽样判定结果与人工核对一致。
- 改动提交并推送到 0.0.9；协议类型检查通过。
