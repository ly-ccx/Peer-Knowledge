# B4-03 取代与恢复实施契约

创建时间：2026-10-01
最后更新：2026-10-01

## 授权与基线

依据负责人“自行推进 B4 全部”的授权完成必要接入、验证、Review 修复与合入，不再逐个路径重复确认。基于 B4-02 已合入代码 `faa25d9c` 与知识 `1da4743`；依据 Accepted ADR 80 的决策 7、P0-2 插话边界。

## A 级接口与不变量

- 取代先建好新任务，旧任务进入持久化 `superseded` phase 与 Goal `paused`，记录 `supersededBy`、`supersededAt`。关闭准入、取消回合预留、中止并等待工具结束；不删除旧 worktree、标准、结果、证据和冻结模型。
- 仅同项目、同项目代理对话且可继续执行的任务可取代；引用范围在 Provider 端强制。待验收、已验收、终态不可取代。新任务建立失败不改变旧任务；新任务启动失败保留已建立替换线与错误事实。
- 新工具 `resume_session {sessionId, anchorMessageId}` 只接受本项目代理对话中的用户输入锚点，恢复 paused/superseded 任务；仍活跃的替换链暂停并指向被恢复任务。重复同一恢复锚点不重放为新操作。恢复仍经 Scheduler/IsolationPlanner 准入，不绕过审批、依赖、磁盘、全局槽位。
- 新工具 `reprioritize_session {sessionId, priority}` 调整未结束任务，存储 priority，排队计龄保持原始创建事实。新能力沿现有 Delegation Provider、Manifest、Runtime Projection、Grant、Evidence 链注册。
- 七天未恢复的 superseded 任务自动取消并按 B4-02 清理执行目录，保留 Plan/证据与任务分支线索。清理失败可重试；只投递静默事实，不制造用户消息。经典界面或失去项目租约时不运行维护。
- Renderer 只读投影；暂停任务独立分组，显示替换任务名称。恢复按钮经类型化宿主命令先持久化用户动作锚点，再调用同一恢复模块；不以模型文字当作用户动作。SVG 图标与现有控件风格。

## 必要路径

原卡 supervisor/provider/tool-specs/GoalPlan store/提示/任务投影；Goal Runner 的 pause 同步委托 paused phase，避免用户手动暂停后被自动准入；新增深模块 `session-continuity.mjs` 集中作用域、取代链、暂停结算、恢复幂等和过期；Protocol 状态与元数据、Provider 模式注册、已注册提示及工具目录、project-agent host/application service、现有 IPC 注册与 channels/preload 类型、drawer 状态/任务页/详情/样式、i18n 和聚焦测试。必要 IPC 为 `project-agent:resume-session`；不增加依赖，main.mjs 净增为零。

## 验证

取代→恢复→再取代、暂停结算前不准入、worktree/成果保留、审批保持、待验收/跨项目/引用/伪锚点拒绝、恢复动作幂等、七天自动清理与失败重试、优先级重启保留，以及 affected package 完整套件、build/typecheck/architecture/ipc 和当前提交双平台 CI。
