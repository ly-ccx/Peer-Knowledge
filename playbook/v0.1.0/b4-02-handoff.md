# B4-02 交接记录

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片
B4-02 IsolationPlanner、自动 worktree 与合回（Beta4）。

## 分支与提交
- 分支：`PeerAgent/pa/b4-02-worktree-isolation`
- 提交：`105c1381` feat(project-agent): isolate delegated writes and govern merge-back decisions
- 提交：`2bb9d198` fix(project-agent): keep failed merge cleanup decisions actionable
- 提交：`9d8ad3ee` fix(project-agent): settle cancelled turns before worktree cleanup
- 提交：`4e1da4a1` fix(project-agent): keep invalid workspace inspection blocked
- 提交：`f039b4e9` fix(project-agent): inspect free space on the execution volume
- 最终提交：`7819b883` fix(project-agent): keep worktree creation behind admission checks
- 代码 PR：[Peer-Agent #78](https://github.com/ly-ccx/Peer-Agent/pull/78)。
- 基线：B4-01 已合入的 `PeerAgent/dev/0.1.0`，`c2d997e7`。

## 改了什么
- runtime-node `isolation-planner`：只读/非 Git/干净写/并行写/脏工作区/显式选择的决策，2 GiB 磁盘门槛、隔离失败排队与重试、成功/取消清理、失败保留七天。
- Supervisor、scheduler、GoalPlan store 与协议：准入前准备真实隔离，持久化请求/阻塞/保留/合回授权字段；工作区租约限制准备与执行；启动失败回滚若清理失败保留 Plan。
- Desktop Goal host/worktree adapter/Runner：复用既有 Git 链，核对仓库、分支及真实路径；委托隔离失败关闭执行，逐回合检查；清理拒绝把原工作区当作 worktree。
- `session-handoff`、acceptance、card-projection、project facts/application service：签收与合回分开；现有输入入口处理合回确认、冲突修复、自己处理、放弃；修复清除旧签收并添加待办；卡片标识随事实变化防止旧卡复用。
- Profile policy/settings、preload 参数类型、i18n/drawer：自动合回默认关闭，以现有自定义 Switch 保存项目配置；排队原因可读。工具输入限定 isolation enum，并同步已注册提示。
- 聚焦测试与真实 Git 集成测试：生产 Goal host 三条同时运行的独立 worktree，分别用户签收/确认合回并清理；执行绑定的唯一写根确认为各自 worktree。

## 与卡片的偏差
- 原清单不足以完成生产装配、存储/协议和用户确认。负责人“自行推进 B4 全部”授权与补齐路径先记录在 companion knowledge 的 B4-02 实施契约中。
- ADR 80 的签收/合回边界优先于卡片简写：策略签收默认不合回；用户确认或明确开启项目自动合回后才执行。不推送远端。
- 三写验收使用脚本执行器与真实临时 Git/文件系统，经生产宿主及现有 handoff；没有调用远程模型。实际产品日用/发版验收留在 B4-R，不能从此测试推断已完成。

## 验证
- `pnpm build`：通过。
- `pnpm --filter @peer-agent/runtime-node test`：864/864 通过。
- `pnpm --filter @peer-agent/desktop test`：5162 通过、5 既有跳过，无新增跳过。
- `node --test packages/protocol/src/*.test.ts`：172/172 通过。
- `pnpm typecheck`、`pnpm architecture:check`、Desktop `ipc:check`、`git diff --check`：通过。
- 新增覆盖：隔离矩阵/低磁盘恢复/七天保留，start/resume 不回退，租约拒绝，策略代签不擅自合回，当前用户卡作用域，冲突三种处置/重新验证，清理失败保留证据，设置原子保存，真实 Git 三 worktree 合回。
- 自查修复：原应用服务对清理失败仍返回 ok，新增回归在旧实现失败（exit 1），修复后应用服务定向测试全部通过；不会把未清理的改动当作已放弃。真实 Git 场景与门禁见 [证据](evidence/b4-02-validation-20261001.json)。
- CI：最终提交 `7819b883` 的 [运行 36830424073](https://github.com/ly-ccx/Peer-Agent/actions/runs/36830424073) 双平台全部通过。以上本地门禁与真实 Git 场景均复核于此提交。
- Review 两条意见已修复：合回/清理失败向界面返回失败；磁盘门槛读取实际 worktree 目标卷。另补齐取消等待工具结束、缺失/损坏仓库检查，以及 start/resume 不得绕过准入创建 worktree 的回归，旧实现失败、修复后通过。

## 架构影响
- A 级，依据 Accepted ADR 80/69/79。实际隔离真值仍是 deliveryBinding 和 Git 事实；模型参数不能证明隔离或合回授权。
- 深模块 IsolationPlanner 和 SessionHandoff 集中决策；持久化只新增既有 Plan/profile 字段。Renderer 仅投影宿主事实、调用现有输入/配置端口。
- 不新增依赖、IPC 通道或工具；main.mjs 无改动。

## 文档偏差
- 依照 ADR 80 把策略签收与合回确认分开，实施契约记录了必要接入路径。

## 未完成与后续
- 当前 PR 只交付 B4-02。B4-03 负责取代恢复，B4-07 负责跨进程重启与熔断；未发布 Beta4。
- 双平台 CI 与 Review 已完成，按负责人全部 B4 授权合入并继续下一卡。
