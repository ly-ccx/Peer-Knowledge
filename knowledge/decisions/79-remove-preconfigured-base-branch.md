# 79. 移除预配置基准分支：交付绑定跟随工作区实时 HEAD

创建时间：2026-09-23

状态：Accepted

级别：B 级（收紧 ADR 68 的绑定语义与工作区设置面，不改协议对象）

关联：

- `knowledge/decisions/68-goal-delivery-mode-contract.md`（交付绑定原契约）
- `knowledge/decisions/79-` 前身事实：ADR 68 实现里的 `preconfigured` 绑定源
- peer_agent `packages/runtime-node/src/goal-delivery-binding.mjs`
- peer_agent `apps/desktop/electron/main/main.mjs`（绑定与 handoff 合回目标）
- peer_agent `apps/desktop/electron/main/workspace-application-service.mjs`（baseBranch 字段）
- peer_agent `apps/desktop/renderer/src/app/components/GitPanel.tsx`（设置 Git 区）

## 背景

ADR 68 的绑定实现里保留了一条「预配置基准分支」优先支：`resolveWorkspaceHead` 优先取设置里的 `baseBranch`（`targetBranchSource: 'preconfigured'`），取不到才落实时 HEAD；交付 handoff 的合回目标也优先读该设置。实际使用暴露出三个问题：

1. **反直觉**：用户在 `PeerAgent/dev/0.0.18` 上开发、交付，面板却显示「源头 0.0.15」——因为设置里残留着 0.0.15 时代配置的基准分支（真实案例：2026-09-23，多个 plan 绑定与实际开发分支脱节）。
2. **需要手动维护**：每次开新版本线都要去设置里改基准分支，忘改即静默错绑；设置里没有任何提醒机制。
3. **与状态栏环境信息矛盾**：状态栏显示实时分支，计划绑定显示预配置分支，两个「当前分支」来源不一致，用户无法判断哪个是真。

绑定的本意是「记录交付承诺」（计划交付到哪条线），而预配置分支表达的是「愿望分支」，两者混淆后绑定失去事实性。

## 决策

1. **绑定永远跟随实时 HEAD**：`resolveWorkspaceHead` 删除 `preferredBranch` 优先支，只读工作区实时分支；`attachWorkspaceHeadBinding` 产出的 `targetBranchSource` 只会是 `workspace_head`。状态栏环境信息显示什么分支，新计划就绑定什么分支——单一事实来源。
2. **handoff 合回目标以 plan 绑定为唯一来源**：desktop 的 `resolveMergeTarget` 从「设置基准分支 → 绑定 → targetBranch」三级降为「`deliveryBinding.targetBranch` → `targetBranch`」，不再读任何工作区设置。
3. **设置面删除基准分支**：workspace 服务删除 `baseBranch` 字段的投影与更新（`workspaceUpdate` 不再接受该键）；设置 Git 区移除该表单项；renderer 相关状态与回退（如结果页建议目标分支回退到 `workspace.baseBranch`）一并移除。
4. **历史绑定不动**：既有 plan 上已固化的 `targetBranch: '0.0.15'`（含 `preconfigured` 来源标记）是历史事实，按 ADR 68 的可追溯语义原样保留，不迁移、不改写。

## 后果

- 「源头」芯片、交付 handoff、建议合回目标从此与用户肉眼所见分支一致，消除「两个当前分支」的精神分裂。
- 用户少维护一个设置项；跨版本线开发不再需要任何手动同步动作。
- 失去「把计划统一交付到指定集成分支」的能力——若未来确有该需求，应作为计划创建时的**显式单次选择**（对话内选定，进 `deliveryBinding`），而不是全局常驻设置；届时另立 ADR。
- 已存在的 `preconfigured` 来源值成为历史遗迹：读取端兼容（不崩溃），新写入端不再产生。
