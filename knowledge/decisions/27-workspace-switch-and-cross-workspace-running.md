# ADR 27 — 工作区切换与跨工作区运行可见性(Workspace Switch & Cross-Workspace Running)

最后更新：2026-11-15（明确跨工作区可见性在 0.1 默认 Bot 列表工作台与项目代理宿主下的衔接）
状态: Accepted（实现中；跨项目／跨 Bot 并发投影与侧栏可见性已由 [ADR 80](80-project-agent-delegation-model.md)、[ADR 84](84-bot-list-shell.md) 与 [ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 扩展承接）
级别: A 级（触及活跃流运行时投影契约 + 跨进程 IPC payload 形状 + renderer 投影）
关联: [22-stream-reattach-on-reload](22-stream-reattach-on-reload.md), [20-architecture-governance](../architecture/20-architecture-governance.md), [19-system-prompt-context-architecture](../architecture/19-system-prompt-context-architecture.md)

## 背景

用户报告两个现象：

1. 点击切换工作区时整个界面"卡住"，没有任何过渡动画。
2. 切换工作区后，原工作区"正在执行中的任务全丢失了"。

## 关键现状事实（已由代码核实）

- 后端流在 `llm-chat-service.mjs` 的 `sendMessage` **进入时即快照** `activeWorkspacePath`，
  分别传入 `buildSystemContext` / `getConversationToolContext` / agent loop 的 `workspacePath`
  参数（约 246–272 行）。`workspace:set-active` 调用的 `setWorkspacePath` 只改模块级变量
  `activeWorkspacePath`（22 / 134 行），**只影响之后新发起的消息**，不触碰已在循环中的流。
  → 因此切换工作区**不会** abort 或污染正在跑的流。
- `listActiveConversationIds()`（137 行）返回的是**裸 conversationId 列表，不带工作区标签**。
  广播 `chat:stream:active-changed` 与 `chat:stream:list-active` 同样只携带 `conversationIds`。
- renderer 侧 `App.runningConversationIds` 是**全局集合**（含后台并行会话），本身正确；
  但左侧列表只渲染 `conversations`，而 `refreshConversations(newWs)` 会把列表过滤到新工作区
  （`conversations:list` → `listConversationsByWorkspace`）。
  → 原工作区那条仍在运行的会话**没有 DOM 行可挂载 spinner**，于是"看起来丢了"。
- `Sidebar.handleSwitchWorkspace` 串行 `await`：`workspaceSetActive` →
  `refreshWorkspaces`（内部 `workspaceList` + `workspaceInfo`，而 **`workspaceInfo` 跑 git**）
  → `onWorkspaceChanged`（再次 `workspaceList` + `refreshConversations` 磁盘读）。
  整条 git+磁盘链跑在点击处理器里、期间无 pending UI、列表硬切 → 即"卡住"观感。

根因一句话：
- 问题二是**投影丢失，不是任务丢失**——活跃流投影缺少工作区维度。
- 问题一是**串行 git/磁盘 + 无过渡态/无动画**。

## 决策

### D1 — 活跃流投影携带工作区（治本，问题二）

在非协商运行链 `Provider -> Manifest -> Runtime Projection -> Tool Call` 的"运行时投影"
一环，把活跃流的工作区维度补齐：

- `streamRecord` 在创建时快照 `workspacePath: activeWorkspacePath`（与 ADR 22 的
  `accumulatedText` 等运行态字段并列，同一处真值）。
- 新增 `listActiveStreams()` 投影函数，返回 `[{ conversationId, workspacePath }]`。
- `chat:stream:list-active` 与 `chat:stream:active-changed` 在**保留既有 `conversationIds`**
  的同时，附带 `streams`。`conversationIds` 不删除——ChatSurface 等既有消费者不受影响（演进而非破坏契约）。
- renderer 由 `streams` 派生「有运行中流的工作区路径集合」，在左侧工作区入口与下拉项上
  显示运行指示。这样"任务在其它工作区仍在跑"成为**可见事实**，而非静默丢失。

### D2 — 切换去阻塞 + 过渡动画（问题一）

- 工作区切换的两次独立 `workspaceList` 合一，git 信息（`workspaceInfo`）不再阻塞名称展示：
  先用已有的 workspaces 条目乐观回填名称，git 分支异步补。
- 切换时给主内容一次轻量 reveal（复用既有 `za-content-reveal` / `za-panel-in` 动效 token），
  与设置页、Thread 等大面板的入场约定一致；`prefers-reduced-motion` 由 `tokens.css` 全局降级兜底。

## 不做什么

- 不把"运行中流"提升为 System Context 指令，它是事实/运行态投影。
- 不引入新的跨进程临时 payload：复用既有两条 IPC，仅扩展其对象形状并同步契约类型。
- 不改变流的工作区归属语义（仍是发起时快照），本 ADR 只补"可见性"。

## 影响面

- main: `llm-chat-service.mjs`（streamRecord、listActiveStreams、广播、导出）、`main.mjs`（list-active handler）。
- 契约: `bootstrapPreloadApi.ts` 两处签名扩展。
- renderer: `App.tsx`（派生工作区运行集合并下传）、`Sidebar.tsx`（运行指示 + 去阻塞切换）、`sidebar.css`。
- 测试: 为 `listActiveStreams` 投影补单测（工作区维度存在、切换后旧工作区流仍被投影）。
