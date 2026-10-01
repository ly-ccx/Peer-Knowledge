# B4-02 worktree 隔离与交付实施契约

创建时间：2026-10-01
最后更新：2026-10-01

## 授权与依赖

负责人于 2026-10-01 明确授权：“我同意，你直接自己推进把 B4 全部做完”。这覆盖 B4 各卡的实施、必要接入路径补齐、验证、修复 Review 后合并以及 B4-R 的发版验收；每卡独立分支与 PR，门禁仍须通过。不以该授权扩大能力、权限或外部写入范围。

B4-01 代码 #77 与知识 #8 已合入，代码基线 `c2d997e7`，知识基线 `775d7bf`。B4-02 依据 Accepted ADR 80/69/79。

## A 级接口与边界

- IsolationPlanner 消费宿主事实，不另写 Git 执行链。只读为 none；非 Git 写任务为 none 并占原地写槽；Git 写任务在其他写任务进行中或工作区脏时 auto 选择 worktree。显式 none 遵守原地写槽，不能抢占。显式 worktree 在 Git 中必须获得真实隔离。
- 持久化 requested isolation 与准备阻塞原因属于 DelegationOrigin；实际执行真值仍是 deliveryBinding。只有成功创建并验证的 worktreePath 才能绕过原地写槽。磁盘可用不足 2 GiB 或创建失败时保持 queued，后续重算可重试，不能回退到原工作区写入。
- 磁盘闸门读取实际 worktree 目标卷，不以源仓库卷代替。目标目录还不存在时读取最近已存在的父目录卷。Automation worktree adapter 只新增只读 `getRootDir` 事实端口，让 Goal 创建与检查使用同一执行根；不改变 Automation 执行/权限链。
- Supervisor 在准入前准备实际执行工作区，并串行保留其决策事实，随后才交给 B4-01 排序/预留/启动。宿主 start/resume 与每轮执行也检查隔离事实；隔离故障不静默回退。已有经典 Goal 路径保持原语义。
- ADR 79 的目标分支从创建时实时 HEAD 固化，复用现有 Goal task branch/worktree adapter；不自动 stash 用户改动。
- 复用现有 handoff。委托任务必须签收后才能合回；ADR 80 优先于卡片的简写，策略签收默认只产生合回确认，`autoHandoffOnPolicyAccept` 默认 false；用户明确确认合回或项目明确开启自动合回才执行。不会推送远端。
- 合回 CONFLICT/BLOCKED_ENV 直接投影宿主卡片。冲突选项为让任务处理、用户处理、放弃，使用已有输入/交付应用服务；模型文字不能构造合回授权。成功后清理 worktree；取消清理 worktree、保留分支；失败保留七天，过期清理但保留提交线索。清理不覆盖用户原工作区。

## 必要路径

原卡路径：`project-agent/isolation-planner.mjs` 及测试、supervisor、goal-runner-host、acceptance、card-projection。

完成生产接入还包括 runtime-node index、Goal Runner（委托隔离失败关闭执行）、GoalPlan store 的新 origin 字段校验、scheduler 的准备闸门、tool-specs 与 spawn-identity（隔离输入/幂等）、protocol DelegationOrigin/排队事实、Goal worktree/task branch/handoff adapters、`session-handoff.mjs`（深模块，集中合回用户决策）、project-agent-host/project-facts/application service（事实与用户决策）、bot profile/settings（自动合回默认关闭）、renderer 抽屉/状态/卡片与 i18n，以及对应聚焦测试、已注册 spawn 提示。main.mjs 仅允许装配替换且净增不大于零；优先在现有宿主 seam 装配。

## 验证与退出

矩阵覆盖只读/原地写/并行写/脏工作区/非 Git/显式 none/worktree/低磁盘；失败不执行 Provider；两写隔离与重启重试；代签不擅自合回；合回成功、冲突和三种用户处置；成功/取消清理、失败七天保留。真实临时 Git 仓中三条写任务在独立 worktree 并行并各自经现有 handoff 合回，记录可复跑证据。受影响包、类型、架构、双平台 CI 通过后按本次授权合并。
