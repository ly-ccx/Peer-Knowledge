# RC：等待跟进任务的取消入口

创建时间：2026-10-10
状态：ReadyForOwner（代码已推送，最终源码产品门禁及 Mac/Linux CI 通过，PR 待负责人处理）
派单来源：负责人截图反馈“这个任务就不能取消吗？一直显示等待跟进”。
分类：C 级；复用现有取消 API、IPC、Supervisor 与队列通知，不移动 Runtime、权限、Evidence、System Context 或存储边界。
分支：`PeerAgent/pa/rc-task-cancel`，基线为 RC10 的 `013a0a17d644d491f59a07471ee85598ccda372b`。
PR：[Peer-Agent #136](https://github.com/ly-ccx/Peer-Agent/pull/136)。

## 根因与范围

生产链路已有 `projectAgentCancelSession` → `project-agent:cancel-session` → Application Service → Session Supervisor。Supervisor 会取消排程、停止执行、等待正在收尾的工作、保存取消状态并发送通知。聊天后台任务条目与任务详情没有绑定该动作，导致用户只能看到“等待跟进”。历史报告摘要也可能继续显示“等待你的选择”，与最新取消状态矛盾。

- 聊天展开的任务条目及侧栏任务详情加入直接取消入口。
- 两处入口共享提交状态，防止重复提交；失败时保留任务并允许重试。
- 状态以宿主确认和刷新为准；已取消目标移出待跟进列表，历史条目显示已取消。
- 保留历史结果和无关工作；点击按钮卸载后恢复合理的键盘焦点。
- 本卡不取消用户个人数据中的任务，不更改发版版本，也不修复历史任务统计能力的其他限制。

## 允许改动

代码仓相对路径：

- `apps/desktop/renderer/src/project-agent/BotListShell.tsx`
- `apps/desktop/renderer/src/project-agent/conversation/DelegatedWork.tsx`
- `apps/desktop/renderer/src/project-agent/drawer/SessionDetail.tsx`
- `apps/desktop/renderer/src/project-agent/state/botWorkState.ts` 及其测试
- 新建 `apps/desktop/renderer/src/project-agent/state/TaskCancellation.tsx`
- 新建 `apps/desktop/renderer/src/project-agent/styles/bot-task-cancel.css`
- `packages/i18n/src/index.ts`
- `packages/runtime-node/src/project-agent/session-supervisor.test.mjs`（只增加既有宿主能力的回归）
- `apps/desktop/scripts/bot-shell-electron-smoke.mjs`
- `apps/desktop/scripts/bot-history-motion-checks.mjs`（收起详情时核对全部动作均未持有焦点）
- 新建 `apps/desktop/scripts/bot-task-cancel-checks.mjs`
- `scripts/product-regression.mjs`

知识交付：本卡、产品回归流程的取消用例及真实本轮证据。

## 本机验证

- 修复前：独立 Electron 检查在“等待任务必须有直接取消入口”断言失败（0 个按钮，预期 1）；不是仅凭截图猜测。
- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check` 均通过。
- 受影响桌面包完整测试：5433 项，5428 通过、原有 5 项跳过、0 失败；i18n 独立检查 1 项通过。
- Runtime Node 完整测试：1129 项全部通过，包含等待任务取消的持久化、历史保留、无关工作保留和重复取消事件去重。
- 定向状态、Supervisor 与产品门禁测试：88 项全部通过。
- 独立源码 Electron：10 项取消交互断言全部通过，0 页面错误、0 主进程授权错误，测试自有进程已退出。
- 最终源码 `78965d80` 的 `qa:product:capture` 完整通过；118 张必查截图逐张检查，`qa:product:verify` 通过。审查为实现者自审，`independent=false`。
- [最终 Mac/Linux CI](https://github.com/ly-ccx/Peer-Agent/actions/runs/37964118366) 两项均通过，包含完整构建、类型、架构、测试及真实源码 Electron 窗口场景。
- 逐张观察见 [产品审查](evidence/rc-task-cancel-product-review-20261010.json)，绑定源码、门禁、交互断言及 CI 的事实见 [本轮核验](evidence/rc-task-cancel-validated-20261010.json)。

### 完整窗口场景衔接

首次整套回归时，前序场景已展开任务，新取消检查又点击摘要造成收起；修正为读取并保留展开状态，等待按钮实际可见，原缺失按钮断言保留。第二次运行的 10 项取消检查全部通过，但旧历史动效检查把任务详情中的所有按钮当作唯一节点；新增取消动作后它匹配两个按钮。该检查改为断言已收起内容内没有键盘焦点，覆盖全部动作而非只覆盖旧详情按钮。两次未完整通过的包均保留为 `not-accepted`，不复用其产品通过标记。第三次运行绑定 `03ddbbf0` 源码。

第三次本机整套运行与 118 张截图自审通过；同提交的 macOS CI 通过，Linux CI 在新增取消场景的初始准备步骤超时。前序场景可能收起外层任务列表，检查却用 `innerText` 等待其中隐藏的标题。改为等待最新任务事实进入 DOM，再按当前展开状态打开列表，最后仍要求取消按钮实际可见。该修正不改生产 UI，也不延长超时或放宽取消断言。最终第四次截图包及新的双平台 CI 绑定 `78965d80187633f414142431270176cae5a4db6d`。

## 覆盖限制

本轮只在隔离数据运行，窗口测试的取消回执由现有 Application Service seam 受控提供；真实宿主取消另有隔离 Supervisor 测试。未覆盖真实模型质量、已安装 RC、全屏幕阅读器或长时间使用。AI 截图审查为实现者自审，不称独立审查。正式 RC10 尚未包含本卡。

## 提交与交付

- `671993b9`：取消 UI、状态与文案，以及定向宿主和窗口回归。
- `e14b628c`：取消检查保留当前展开状态。
- `03ddbbf0`：历史详情收起检查覆盖全部动作焦点。
- `78965d80`：收起外层列表时先等待 DOM 中的最新任务事实，再检查可见动作。

PR 已准备好审核，按实施手册等待负责人合并授权。没有更新正式版本。透明快捷窗口的浅色截图只确认布局，未据此声称 OS 合成对比度通过。
