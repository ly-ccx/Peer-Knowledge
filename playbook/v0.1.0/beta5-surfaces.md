# beta.5 多入口（`0.1.0-beta.5`）

创建时间：2026-09-26
最后更新：2026-09-26

> 主题：终端与手机网页也能和同一个机器人说话；任何时刻一个项目只有一个宿主在运行。  
> 用户可见：在项目目录运行 `peer` 打开该机器人；`peer bots`；桌面开着时 TUI 作为客户端；远程网页看机器人列表、对话、任务并发消息，批准提示回到电脑。  
> 进入条件：beta.4 已发布；ADR 85 为 Accepted。  
> 通用退出条件见 `README.md` §6。

并行关系：

```text
B5-01 → B5-02
B5-03 → B5-04
B5-03 → B5-05
（TUI 线与远程线可并行）
```

---

## B5-01 TUI 运行时接入（宿主 / 客户端两种角色）

- **级别**：A（ADR 85 决策 1、2、9）。**规模**：M。**依赖**：B2-06、B2-13。
- **目标**：TUI 能持有租约作为宿主运行项目代理，也能在桌面持有租约时作为客户端。
- **代码锚点**：`apps/tui/src/goal-runner-adapter.ts`（B2-06 让它不推进任务计划）；`apps/tui/src/chat-controller.ts`（`runGoalTurn`、回合管线）；`apps/tui/src/cli-tools.ts`、`tui-runtime.ts`（TUI 自己的工具集）；`apps/tui/src/conversation-persistence.ts`；runtime-node 的 `project-agent/*`、`memory/*`、`model-router.mjs`、`project-registry.mjs`、`settings-migrations.mjs`。
- **允许改动**：新建 `apps/tui/src/project-agent/{tui-turn-executor.ts, tui-project-host.ts, tui-project-client.ts}` 与测试；`goal-runner-adapter.ts`（`canRunPlan` 接租约）；`cli-tools.ts` / `tui-runtime.ts`（加入 `project_agent` 模式：工具来自 runtime-node `tool-specs`，执行经 runtime-node 的 delegation / memory Provider，闸门用 `mode-policy`）；TUI 的待批准界面（写 `approval-store`）。
- **实现要点**：
  - 启动：当前目录经注册表解析 `workspaceId`；有机器人档案时尝试获取租约。
  - 宿主模式：与桌面同一套 runtime-node 模块（runner、supervisor、收件箱、输入消费者、调度器、WatchRunner）；回合执行由 `tui-turn-executor` 实现与桌面 `AgentTurnExecutor.runTurn` 相同的契约；任务回合由 TUI 的 Goal Runner 推进（持有租约时）。
  - 客户端模式：输入经 `submitInput`；对话与列表经 `bot-directory` 读取，按会话存储的变更通知刷新（轮询间隔 1 秒，文件未变不重读）；待批准只显示，提示「由桌面处理」。
  - 接管：`/takeover` 命令写接管请求；持有方在下一次心跳让出后 TUI 获取租约并按恢复顺序启动。桌面在开发者分区与档案里提供对称的「接管」按钮。
  - 退出：宿主模式下退出前释放租约；有进行中的任务时提示「任务会在下一个宿主上继续」。
- **必须新增的测试**：宿主模式跑通脚本化全链路；客户端模式提交输入由另一进程的宿主消费；接管；两端同时启动只有一个宿主；TUI 宿主下代理工具白名单与桌面一致。
- **退出条件**：`pnpm --filter @peer-agent/tui test` 通过；真实运行「桌面开着时终端发消息、关掉桌面后终端接管」一次。

---

## B5-02 TUI 界面：机器人列表与对话

- **级别**：B。**规模**：L（可拆 B5-02a 列表与命令，B5-02b 对话与卡片）。**依赖**：B5-01。
- **代码锚点**：`apps/tui/src/app.tsx`（3245 行，新界面放新文件，`app.tsx` 只加入口分支）；`command-registry.ts`；`cli-argv.ts`；`leader-key.ts`；`tui-theme.ts`。
- **允许改动**：新建 `apps/tui/src/project-agent/{BotListView.tsx, BotConversationView.tsx, CardLine.tsx, commands.ts}` 与测试；`app.tsx`（入口分支）；`command-registry.ts`、`cli-argv.ts`（新命令与参数）。
- **实现要点**：
  - `peer`：当前目录有机器人 → 打开其对话；没有 → 询问「把这个目录绑定为机器人？」（是 → 创建；否 → 进入经典对话）；`peer --classic` 始终进入经典对话。
  - `peer bots`：列表（名字、需要你、进行中、最后消息时间）；方向键选择、回车进入。
  - 对话：显示 `user_input` / `agent_reply` / `system_card`；回复条显示「↳ 回复：…」；标记以简短文本显示；卡片以编号选项显示，`/approve 1`、`/deny 1`、`/answer 1 <内容>` 或方向键选择。
  - 命令：`/bots`、`/tasks`、`/task <n>`、`/memory`、`/objectives`、`/takeover`、`/classic`。
  - `peer exec` 与现有经典模式行为不变。
- **必须新增的测试**：命令解析；卡片编号映射；无机器人目录的分支；经典模式回归。
- **退出条件**：TUI 测试通过；终端录屏附在交接报告。

---

## B5-03 远程协议与设备侧准入

- **级别**：A（ADR 85 决策 8；ADR 75）。**规模**：M。**依赖**：B1-06、B2-13；P0-6（ADR 75 文件已补）。
- **目标**：远程入口可以列机器人、读对话、读任务、发消息；每一步都经过 ADR 75 的预检链，本机再次校验。
- **代码锚点**：`packages/protocol/src/remote-access.ts`（`RemoteReadRequest`、`RemoteReadContext`、拒绝码、字段白名单）；`runtime-gateway/remote-goal-read.mjs`（设备侧只读适配写法）与 `remote-goal-input.test.mjs`（非法输入测试写法）；`remote-access-controller.mjs`；`packages/runtime-node/src/remote-device-connection.mjs`（委托投影发布）；`remote-receipt-store.mjs`。
- **允许改动**：`packages/protocol/src/remote-access.ts` 与测试（新增操作与准入）；新建 `runtime-gateway/remote-project-access.mjs` 与测试；`remote-access-controller.mjs`、`remote-device-connection.mjs`（委托投影增加 `workspaceIds[]`、`allowProjectRead`、`allowProjectMessage`）。
- **实现要点**：
  - 操作：`project.list`（只返回被授权的机器人）、`project.conversation.read`（分页，每页 ≤ 50 条，只含 `user_input` / `agent_reply` / `system_card`，文本 ≤ 4000 字）、`project.session.read`（任务投影与报告摘要，不含证据原文）、`project.input.submit`（`text` ≤ 4000 字、无附件）。
  - 准入：沿用绑定版本、连接纪元、委托版本、过期时间检查；新增拒绝码 `PROJECT_DENIED`、`MESSAGE_DENIED`、`INPUT_TOO_LONG`；字段白名单拒绝多余字段。
  - `project.input.submit` → `submitInput({ surface: 'remote', inputId: <由 requestId 派生> })`；同一 requestId 重复到达返回首次结果（回执存储）。
  - 待批准在远程投影里只有摘要和「需要在电脑上批准」，没有任何决定操作。
  - 错误信息不泄露本机路径或内部错误（沿用 `remote-goal-input.test.mjs` 的断言方式）。
- **必须新增的测试**：每个操作的准入矩阵（合法 / 未授权机器人 / 能力位关闭 / 过期 / 字段多余 / 版本不支持）；输入幂等；远程投影不含证据原文与本机路径。
- **退出条件**：测试通过；交接报告附架构影响（远程第一次有写入：只写输入队列）。

---

## B5-04 网关路由与远程网页

- **级别**：B。**规模**：M。**依赖**：B5-03。
- **代码锚点**：`apps/gateway/src/remote-task-router.mjs`（中转、`OUTCOME_UNKNOWN` 语义、TTL）；`http-server.mjs`；`web-surface.mjs`（现有页面与 `/api/*` 调用写法）；`server-composition.test.mjs`、`task-routing.integration.test.mjs`。
- **允许改动**：新建 `apps/gateway/src/remote-project-router.mjs` 与测试（或扩展 `remote-task-router.mjs`，二选一并在开工确认里说明）；`http-server.mjs`（新路由）；`web-surface.mjs`（新页面）与测试。
- **实现要点**：
  - HTTP：`GET /api/projects`、`GET /api/projects/:id/conversation?before=`、`GET /api/projects/:id/sessions/:sid`、`POST /api/projects/:id/input`；全部要求已登录会话，参数长度与字符校验照现有写法。
  - 网关只中转：不存事实、不排队、不重放；设备离线 → `DEVICE_OFFLINE`；超时 → `OUTCOME_UNKNOWN`。
  - 网页：机器人列表（需要你 / 进行中）、对话（可发消息）、任务详情；手机宽度优先的布局；待批准显示「需要在电脑上批准」。
  - 发消息失败为 `OUTCOME_UNKNOWN` 时，页面提示「可能已送达」，并用**同一个** `inputId` 重试（设备侧幂等保证不重复）。
- **必须新增的测试**：路由与鉴权；离线与超时语义；网页脚本的请求形状（沿用 `web-surface.test.mjs` 写法）；同一 `inputId` 重试不重复。
- **退出条件**：gateway 测试通过；手机浏览器截图附在交接报告。

---

## B5-05 远程委托设置（按机器人勾选）

- **级别**：B。**规模**：S。**依赖**：B5-03。
- **代码锚点**：设置页「连接 → 远程」面板（`rg "remote" apps/desktop/renderer/src/app/components -l`）；`register-remote-access-ipc.mjs`；`remote-access-controller.mjs`。
- **允许改动**：远程设置面板与状态纯函数、测试；`register-remote-access-ipc.mjs`；i18n。
- **实现要点**：
  - 列出所有机器人，每行两个勾选：「可查看」「可发消息」（后者依赖前者）；默认都不勾。
  - 旧的单个 `workspaceId` 配置：迁移为对应机器人「可查看」，其余不变。
  - 显示最近一次远程访问的时间与操作。
  - 修改后委托版本号 +1，已连接的远程会话按 ADR 75 重新准入。
- **必须新增的测试**：勾选依赖；旧配置迁移；版本号递增。
- **退出条件**：测试通过。

---

## B5-R 发布 `0.1.0-beta.5`

- **步骤**：版本计划 §10 检查单；npm `@peer-agent/cli` 与运行时包以 `beta` dist-tag 发布；发布说明写明 TUI 与桌面需同时升级。
- **证据**：版本计划 §12.1 beta.5 一行。
- **退出条件**：prerelease 生成；版本计划 §5.2 更新。
