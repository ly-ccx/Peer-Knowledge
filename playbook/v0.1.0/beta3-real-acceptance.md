# Beta3 候选真实日用验收

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片

负责人在核验一致性补修后授权继续，执行真实模型与隔离桌面验收。本卡只收集证据，不改运行时契约、不发版、不启动 Beta4，也不把负责人连续日用要求替换为短时测试。

## 分支与基线

- 知识分支：`PeerAgent/pa/beta3-real-acceptance`，从知识库 `main` 开出。
- 初次代码候选：`cd3d1283e405dab74916011a99f4de2365206a93`；补修复跑候选：`6a4c5ecd7477a951ba5bbda1c6c532551abe3c00`，[Peer-Agent #75](https://github.com/ly-ccx/Peer-Agent/pull/75)。该 PR 尚未合入，本卡结果仅适用于候选。
- 运行时约束沿用已 Accepted ADR 80–85、既有 delegation runtime；补修契约与交接见 [Peer-Knowledge #5](https://github.com/ly-ccx/Peer-Knowledge/pull/5)。

## 范围与允许改动

- 仅本交接及 `playbook/v0.1.0/evidence/beta3-real-*` 脱敏证据。临时测试控制器保存在隔离目录，不作为产品实现。
- 真实 Electron 生产装配、既有 preload IPC、现有模型通道；任务能力仍经 Provider → Manifest → Projection → Tool Call → PermissionGrant → Evidence。
- 独立应用数据、独立 user-data-dir、tracked Git archive 项目副本。读取已有模型通道与加密凭据用于该实例，不输出秘密，结束后移除凭据副本。
- 关闭与停止只操作本轮登记的应用句柄，不影响用户已有进程；不改真实 `~/.peer-agent`。
- 优先验收：完整无窗口任务交付、非空项目熟悉后 verified 记忆及查撤恢复、真实插话并入/停止与状态一致性、送达档位差异、按需披露到可读 Evidence。
- 发现产品缺口记录复现与证据，交接另卡补修，不在本卡扩展清单。

## 判定与未覆盖要求

- 模型文字不作为任务签收或权限执行证据；判定读取持久化 Goal、Task、Tool Result、Evidence 与对话投影。
- 关窗记录覆盖提交后的全过程，核对窗口数量为零与任务交付/签收时间顺序；如恢复窗口后才交付，不能记为完整无窗口通过。
- 熟悉项目须真实模型阅读非空项目并经核验、签收与 Evidence 后写 verified 项；用户声明的 stated 项不替代此项。
- 需要区分真实运行、脚本模型测试、人工数据夹具与静态代码检查。
- 负责人连续日用 5 天、Windows/Linux 安装矩阵及真实视觉复核分别列出状态，不伪造长期或跨平台结果。

## 执行记录

### 实际运行与结论

真实 macOS Electron 生产装配与 `glm-5.3-flash`，三次有任务运行均使用独立数据和 tracked archive；每次归档内容与源提交逐 Git blob 比对，修改数均为 0。已有应用和真实用户数据未改；登记的隔离应用全部退出，加密凭据副本全部移除。另有一次选错 quick-chat 窗口的控制器启动已退出，IPC 正确拒绝该窗口，不计产品通过或失败。

脱敏结构化证据：[beta3-real-20261001.json](evidence/beta3-real-20261001.json)。本记录没有把真实模型文字当作签收证据。

| 项目 | 证据 | 判定 |
|---|---|---|
| 核验工作区 | 初次 worker 读项目根，sessionless Goal verifier 却继承另一 active workspace，两个任务复现；修复后取相同项目根 | 已修，纳入已有核验补修 PR #75 |
| 完整无窗口交付 | 02:36:49.513Z 销毁所有窗口，02:38:14.886Z 重开；85 个采样均为 0；首任务在零窗口后创建，02:37:09.271Z 已持久签收，`acceptedBy=policy` | 此限定场景通过；正常 close 的瞬时窗口保留不算立即零窗口 |
| 重复派发 | 1 条输入、同一 anchor 生成 3 个相似研究 Goal；前两个签收，第三个 Goal 核验通过但停止时尚未签收 | P1，未修 |
| 停止 | 初次真实输入触发 `cancel_session`，持久化取消及对话状态刷新；随后队列任务继续 | 此样本通过，未覆盖 amend |
| Evidence 披露 | 命令引用可读取；已签收首任务的精确文件 criterion Evidence 引用读取返回 `NOT_FOUND` | P1，未修 |
| 非空项目熟悉 | 真实文件读取有 Tool Result；内建 manual DoD 先阻塞是预期行为。补跑 02:45:14.725Z 结构化人工确认，02:45:19.222Z Goal 核验通过；02:48:01.715Z session 仍 `result_ready`，无 acceptance、记忆空、profile 无 memoryRecorded | P1，verified 记忆端到端未通过 |
| 人工确认界面 | 已有任务现场入口，但 1280×860 下右面板被挤窄，按钮落在长滚动区域，滚动后普通点击仍超时 outside viewport；最终用已有 preload 两个接口执行确认与 verify resume | UI 操作未通过；接口结果不替代 UI 通过 |

熟悉项目的代理回合还两次调用 `memory_remember`，宿主返回 `not_project_agent`，随后 `post_reply` 没有关联 session sources。这说明尚未形成可写 verified 记忆的交付链，但不是放宽记忆身份限制的理由。初次未人工确认就取消的样本已重新归类，不能据此声称没有确认入口。

### 本轮修复的范围归属

复現工作区错误后，先在既有核验补修知识分支提交 `8cc1da0`，明确只读 reviewer 使用执行工作区；再在已有代码 PR #75 的允许文件 `goal-runner-host.mjs` 与其测试补修 `6a4c5ecd`。Explorer、文本 Verifier（含格式重试）、视觉 Verifier 共用绑定规则：worktree → target → conversation → global fallback。没有新增 sendMessage 参数、IPC、依赖、存储路径或能力通道，`main.mjs` 净增 0。本验收分支仅收录记录与脱敏证据。

### 验证

- `node --test apps/desktop/electron/main/agent-host/goal-runner-host.test.mjs apps/desktop/electron/main/agent-host/verifier-report.test.mjs`：14 passed。新用例覆盖 conversation、target、worktree 绑定及格式重试；旧实现先复现失败。
- `pnpm --filter @peer-agent/desktop build`：通过。
- `pnpm --filter @peer-agent/desktop test`：5135 passed / 5 existing skipped / 0 failed。
- `pnpm typecheck`、`pnpm architecture:check`、`git diff --check`：通过。
- `pnpm test`：6479 Node + 712 TUI = 7191 passed；0 failed / 0 cancelled，Node 保留 5 个既有 skip。
- 候选 `6a4c5ecd` [CI 36806599692](https://github.com/ly-ccx/Peer-Agent/actions/runs/36806599692)：macOS、Ubuntu 都通过。这不是 Windows/Linux 安装产品验收。

### 未完成与下一步

Beta3 不能记为全部验收通过。下一张补修卡优先处理：同一输入的等价任务重复派发、文件 Evidence 披露、熟悉项目完成后的关联回复/签收/verified 记忆闭环；确认面板布局作为明确 UI 问题独立修。需要新卡明确契约与允许文件，不在本证据卡扩展实现。

未完成的真实门槛：amend 并入、送达档位差异、偏好三 episode admission、verified 记忆查撤恢复、真实视觉复核、Windows/Linux 安装矩阵、负责人连续日用 5 天。无 Beta4 启动或发版结论。
