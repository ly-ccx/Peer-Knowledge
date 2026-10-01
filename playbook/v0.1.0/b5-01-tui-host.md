# B5-01 终端宿主实施契约

创建时间：2026-10-01
最后更新：2026-10-01

状态：Accepted。用户于 2026-10-01 授权执行剩余 Beta5、RC 开发、修复与自测；正式发布前由用户全面测试。此前合并授权持续有效。本文固定 B5-01 的实施路径，不扩大 ADR 85 的产品能力范围。

## 交付与发布边界

- 逐卡完成 B5-01 至 B5-05、B5-R、RC-01 至 RC-05；提交、Review、CI、合并、预发布及真实验证随卡推进。
- RC 交接包含可安装候选版、逐功能自测证据和详细用户测试文档；未运行、受环境限制、待用户验收的检查必须分别写明。
- RC-06 连续七日日用属于用户验收。自动测试、脚本执行和短时自测不能冒充这七天。
- GA 合入正式发布线、稳定 tag、npm latest 与更新通道毕业，等待用户全面测试后明确确认。

## 架构与 Module

依 ADR 85 决策 1/2/3/9：每个项目只有一个持有租约的宿主；所有入口写 ProjectInput；只有宿主消费并推进代理、任务、Watch。模型回合经过 Runtime Pipeline；工具来自 Manifest / Projection 并经 Provider / PermissionGrant / Evidence 执行。

1. 将桌面 `createProjectAgentHost` 的输入、恢复、收件箱、回合与时钟编排移动到 runtime-node 的 `project-agent/runtime-host.mjs`；通过 sink 端口表达事件。桌面保留兼容导出及 Electron 组合适配。不得复制第二份编排。
2. 把被两端消费的 reply composition、verification、事实投影与 objective watch 组合提取到 runtime-node。桌面可保持兼容导出，桌面 IPC/dialog/shell 仍属于桌面。
3. TUI 的 `tui-project-host` 装配同一 runner/supervisor/scheduler/inbox/input queue/watch/recovery；`tui-turn-executor` 适配共享 Pipeline 与宿主工具，冻结角色模型、权限和会话身份。
4. TUI 的 `tui-project-client` 读目录与持久会话，提交输入队列。每秒检查变更戳；未变时不重复读正文。客户端批准只显示，由桌面处理；持有租约的 TUI 才可作本机批准。
5. 在现有 TUI host 的 Provider seam 接入 delegation/memory；project_agent 投影与执行硬闸都调用共享 mode-policy。任务仍走普通 file/shell Provider、read-only Gate、持久 PendingApproval。没有真实 Grant/Evidence 不得声称工具已执行。
6. 接管请求在下一次心跳交接；失去租约后取消旧模型流并停止任务泵送，新的宿主按既有恢复顺序启动。退出先停止执行再释放租约。

## 路径清单补齐

除卡片已有 TUI 新模块与锚点之外，现有装配分散在桌面主进程，必须补齐以下路径。用户的全部完成授权覆盖这些必要路径，不新增依赖或存储根目录。

- runtime-node：`src/project-agent/runtime-host.mjs`、共享事实/回复/验证/Watch/工具适配模块与测试；`src/index.ts` 导出。
- 任务宿主同样复用：提取 `agent-host/goal-runner-host`、work-session profile、verifier report/evidence、goal runner message persistence、preferred worktree、Goal/Automation worktree 与交付合回算法到 runtime-node；任务分支名称策略由宿主注入既有 System Context 的 resolver，runtime-node 不反向依赖 System Context 或 Electron。桌面旧入口保持兼容导出/适配，TUI 不复制任务推进或 worktree 实现。
- runtime-node 的只读 file/search Manifest 补入 `project_agent` modeScope；写入和 Shell Manifest 不扩大。两端仍通过共享白名单和执行硬闸拒绝副作用能力。
- desktop：`electron/main/project-agent/project-agent-host.mjs` 及被提取模块的兼容导出、测试；已有宿主租约装配与 typed takeover IPC；catalog/preload 类型；开发者设置和档案接管 UI 与 i18n。
- TUI：`tui-host.ts`、`tui-mode.ts`、`tui-runtime.ts`、`tui-language.ts` 的共享模式/Context Source 接入；`goal-runner-adapter.ts` 与 tests；新模块的类型和构建入口所需最小适配。
- protocol：既有 `project-agent:takeover-host` 的 typed request/result 若尚未实现则补齐，不增加卡片外 IPC 操作。

`main.mjs` 净增不大于零；`app.tsx` 的功能入口留给 B5-02，新界面另建文件；ChatSurface/Sidebar/LlmSettingsPanel 不增长。旧经典、peer exec、原会话文件兼容保持测试覆盖。

## 验证

先跑有竞争的双进程租约、客户端输入被另一进程消费、接管与流取消、脚本化完整委托链路、投影/执行双闸、持久批准与只读任务测试；再跑受影响包完整测试、typecheck、architecture、IPC 检查和双平台 CI。真实桌面/终端模型交接另附证据，不用替身结果代替。
