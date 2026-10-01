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
7. 同一宿主内所有回合复用同一个 GoalPlanStore，避免独立 store 的 runner overlay 覆盖任务证据。跨进程读缓存和待刷进度按文件版本失效，不覆盖新宿主已写入的状态。工具调度在异步 Hook 返回后再次检查租约；delegation/memory 返回标准 ToolResult.output，同时保留已有兼容字段。事件唤醒省略新用户消息，事实仍经既有 Context Source 入场。
8. 完整链路测试可以在模型 Adapter seam 注入脚本模型；它仍执行实际 Pipeline、Manifest、Provider、Grant、Evidence 和持久化。测试替身不能作为真实模型运行的证据。
9. 补齐只读工作会话的执行约束：从持久 GoalPlan 的 delegationOrigin 读取 readOnly，不依赖模型自述或提示。共享工作会话 Gate 拒绝写入、Shell、浏览器控制和未知副作用能力；只读工具及任务事实登记/提问仍可用。两端在投影阶段隐藏被拒绝的能力，并在 Provider 调度前（异步 Hook/批准之后）重查持久身份与租约。Skill 的说明读取不产生执行权限；MCP 未声明只读时按有副作用处理。
10. 交接只挂起实际执行中的任务，不改写已完成、等待用户、待批准或用户手动暂停的状态。新宿主只自动恢复持久 `blockedReason: host_handoff`、原 phase 为 running 的交接暂停，并保留原执行 intent；普通暂停继续等待用户。补入共享 session-host-handoff 状态判定和 supervisor 恢复测试。

## 路径清单补齐

除卡片已有 TUI 新模块与锚点之外，现有装配分散在桌面主进程，必须补齐以下路径。用户的全部完成授权覆盖这些必要路径，不新增依赖或存储根目录。

- 工具提示随 Manifest 共享：delegation/memory 的提示资产从桌面移动到 runtime-node；构建时生成内嵌文本模块，桌面与单文件终端二进制读取同一描述。不新建 System Context 拼接路径。共享证据正文投影和项目说明行比较也移动到 runtime-node；两端只注入受登记工件约束的本地读取端口。
- 租约新增停止并等待端口；接管期间执行闸关闭而心跳继续，只有停止成功才能释放。批准恢复只触及新宿主持有租约的项目，不能把另一宿主的现场批准转为 stale。
- runtime-node：`src/project-agent/runtime-host.mjs`、共享事实/回复/验证/Watch/工具适配模块与测试；`src/index.ts` 导出。
- 任务宿主同样复用：提取 `agent-host/goal-runner-host`、work-session profile、verifier report/evidence、goal runner message persistence、preferred worktree、Goal/Automation worktree 与交付合回算法到 runtime-node；任务分支名称策略由宿主注入既有 System Context 的 resolver，runtime-node 不反向依赖 System Context 或 Electron。桌面旧入口保持兼容导出/适配，TUI 不复制任务推进或 worktree 实现。
- runtime-node 的只读 file/search Manifest 补入 `project_agent` modeScope；写入和 Shell Manifest 不扩大。两端仍通过共享白名单和执行硬闸拒绝副作用能力。
- desktop：`electron/main/project-agent/project-agent-host.mjs` 及被提取模块的兼容导出、测试；已有宿主租约装配与 typed takeover IPC；catalog/preload 类型；开发者设置和档案接管 UI 与 i18n。
- TUI：`tui-host.ts`、`tui-mode.ts`、`tui-runtime.ts`、`tui-language.ts` 的共享模式/Context Source 接入；`goal-runner-adapter.ts` 与 tests；新模块的类型和构建入口所需最小适配。
- 真实交接发现共享模型渠道仍被终端拒绝：补齐共享模型元数据的能力声明、wire override 及终端模型路由。OpenCode Go 的按模型选协议/端点算法提取为 runtime-node 的纯函数，桌面保留兼容导出；终端消费相同算法与现有请求编码 Adapter。API-key Responses 沿现有 Responses Provider seam 使用，不新增请求格式旁路。补入 provider-wire-matrix、tui-runtime、shared-model-config、provider-channels 及对应测试路径。
- protocol：既有 `project-agent:takeover-host` 的 typed request/result 若尚未实现则补齐，不增加卡片外 IPC 操作。

`main.mjs` 净增不大于零；`app.tsx` 的功能入口留给 B5-02，新界面另建文件；ChatSurface/Sidebar/LlmSettingsPanel 不增长。旧经典、peer exec、原会话文件兼容保持测试覆盖。

## 验证

先跑有竞争的双进程租约、客户端输入被另一进程消费、接管与流取消、脚本化完整委托链路、投影/执行双闸、持久批准与只读任务测试；再跑受影响包完整测试、typecheck、architecture、IPC 检查和双平台 CI。真实桌面/终端模型交接另附证据，不用替身结果代替。
