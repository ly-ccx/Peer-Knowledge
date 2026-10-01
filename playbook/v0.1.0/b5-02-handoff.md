# B5-02 终端机器人界面交接

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片、分支与状态

B5-02。Accepted 实施边界见 `b5-02-tui-surface.md`。基线 dev `f69691ac`，分支 `PeerAgent/pa/b5-02-tui-surface`，提交 `cf7b2dcf`、`111333a6` 已推送，[代码 PR #87](https://github.com/ly-ccx/Peer-Agent/pull/87)。本地验证完成，双平台 CI 待确认。

## 实现与架构影响

- 独立 ProjectApp / BotList / Conversation / Card / 命令 / 用户动作端口；经典 app.tsx、main、ChatSurface、Sidebar、LlmSettingsPanel 未改。新界面只在交互项目分支动态加载。
- 当前目录绑定是/否、peer bots、--classic；列表键盘、最新对话/早页、回复锚点、标记、编号卡片及命令，任务/记忆/目标页、接管和经典模式切换。
- UI 读共享投影、消息进共享队列；客户端只发普通输入/回答。本机批准、签收、记忆冲突和合回要求宿主租约，不把人类决定冒充模型工具调用。
- executor 持有任务批准 scope，包含工作区/持久session/plan/capability/path；跨回合保留，跨任务/工作区拒绝，宿主停止清除。经典 scope 行为不变。
- 明确 latest 分页选项，默认旧 before 向前分页保留；不让新回复永久藏在第一页。ANSI/OSC 控制字符过滤；终端不加字符装饰图标。
- 停止 Promise 完成后才恢复终端并退出；切经典先停止项目宿主。无新 IPC、依赖、存储根。

## 验证

命令：`pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm test`、`git diff --check`；最终动态入口调整后再次 `pnpm --filter @peer-agent/tui build` / `typecheck`、`bun test apps/tui/src/acp apps/tui/src/cli-argv.test.ts apps/tui/src/cli-exec-integration.test.ts`（Bun 按现有文件匹配，9个文件）。

- 全仓通过：TUI 749，Runtime 969，Desktop 5206 / 5既有skip。最终 ACP/argv/exec 定向103通过。没有增加跳过或放宽用例。
- Desktop首次全包1项 goal-plan-store 文件监听超时；隔离文件142通过，随后全仓 pnpm test 通过。首次超时保留记录，不混称为初次全绿。
- 新增命令/编号/过期/终端文本过滤、入口分支、async shutdown 顺序和错误恢复、实际 OpenTUI 键盘绑定/消息/列表/卡片/经典、客户端动作拒绝、合回回答、任务批准隔离、最新50条分页测试。
- [真实编译CLI录屏](evidence/b5-02-terminal-20261001.cast)：90×30 PTY，最终 `cf7b2dcf` 编译；绑定Y、tasks/memory/objectives/help/bots、回车进入、cards/Esc、classic、Ctrl-C退出0。仅隔离测试目录，路径脱敏；录屏没有模型调用。真实模型双进程交接证据在B5-01；已安装最终候选包会在RC再次验证。

## Review、偏差与后续

首次完整终端测试暴露重复 copy 声明，导致 CLI/ACP 解析错误，已修复并全包通过。最后 Review 将消息回执提示改成「已收到」，避免让入队事实看起来像任务完成；新增实际键盘断言，最终终端全包749和typecheck通过。录屏对应前一提交，覆盖的绑定/导航/退出行为相同；最终CI针对111333a6重新运行。Review 将新项目 UI 静态导入改为交互分支动态加载，保留 ACP 首先分流。卡片外必要路径及 A 级批准范围先登记实施契约。

B5-03–05远程协议/网关与手机页面/按机器人委托、Beta5预发布、RC全功能自测矩阵和详细用户测试文档继续执行。RC-06由用户进行正式发布前全面测试，未宣称已完成；不发布GA。
