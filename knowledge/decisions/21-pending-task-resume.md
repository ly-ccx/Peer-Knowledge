# ADR 21 — 跨重启的任务续传（Pending Task Resume，会话锚定版）

状态: Accepted（实现中）
级别: A 级（新增/升级跨重启持久化契约 + consume 职责跨组件迁移 + 启动期会话切换时序）
关联: 20-architecture-governance, 22-stream-reattach-on-reload

## 背景

自我迭代场景中，本体修改主进程代码后必须重启才能生效；重启会中断当前会话。
为免用户每次重启后手动说「继续」，需要一种机制：**重启前把"未完成的任务"落盘，
重启后自动回到中断现场并接着执行。**

## 旧设计的根本缺陷（已暴露）

第一版 `pending-task.json` 只存 `{ prompt }`，**丢失了任务的坐标**：

- 没有 `sessionId`：重启后不知道该回到哪个会话，只能塞给"恰好当前打开的会话"，
  可能塞到错误会话甚至新会话。
- 没有 `workspace`：无法防止把 A 工作区的任务恢复到 B 工作区。
- consume + 自动发全塞在 `ChatSurface`，但 `ChatSurface` **不持有会话坐标**
  （它只接收 `conversationId` prop），没有"先切到正确会话再发"的能力，
  所以"回到中断现场"这一步在旧设计里根本不存在。

## 关键现状事实（已由代码核实）

- 会话坐标 `activeConversationId` 由 `App.tsx` 持有（`useState`，约 32 行）。
- `App.tsx` 已有 `setActiveConversationId(id)`（约 84 行，`handleSelectConversation`）——
  即"程序化打开任意会话"的现成能力。
- `ChatSurface` 仅消费 `conversationId` prop（约 512 行），自身无法切换会话；
  切换能力在父组件 `App.tsx`。
- `clientApi` / `main` 无"切会话"IPC——打开哪个会话是纯 renderer 状态，不经过 main。
- `/restart` 命令在 `ChatSurface`（约 967 行）触发，可拿到当前 `conversationId`。

## 决策

续传记录升级为**会话锚定**结构，consume/恢复职责上移到 `App.tsx`。

### Q1 sessionId 来源（已定：a）

只支持 **(a)**：sessionId = 触发 `/restart` 时的当前 `activeConversationId`。
即续传只在"会话内手动 `/restart`"这一条路径写入；命令行/自动重启不写续传。
理由：数据结构与恢复逻辑最简，且贴合实际工作流（重启都在某个会话里发起）。

## 续传记录结构

```json
{
  "version": 2,
  "workspace": "/Users/.../peer_agent",
  "sessionId": "<触发 /restart 时的 activeConversationId>",
  "task": "<未完成的任务文本>",
  "createdAt": "<ISO 时间戳>"
}
```

## 设计

1. **store（`pending-task-store.mjs`）**
   - 写入/读取升级结构（`workspace` / `sessionId` / `task`）。
   - 保留 `peekPendingTask`（只读不清）与 `readAndClearPendingTask`（读后清）双入口，
     供"先 peek 预填、自动发成功后再 clear"的抗 StrictMode 时序使用。
   - 损坏 / 版本不符 / 非对象 → 丢弃返回 null。

2. **写入时机（`ChatSurface` `/restart` 分支）**
   - renderer 落盘 `{ sessionId: 当前 conversationId, task: followUp }`。
   - 无 followUp 则不写（保持现状语义）。
   - **workspace 由 main 补齐**：renderer 拿不到 workspace 绝对路径，
     故 `pending-task:write` handler 在 main 侧用 `workspaceRoot` 补上 `workspace`，
     `peek`/`consume` handler 在 main 侧校验 workspace 匹配（不匹配则丢弃）。
     这样 renderer 只需提供会话坐标，工作区坐标的真相留在持有它的 main。

3. **恢复职责上移到 `App.tsx`（核心修正）**
   - 启动 effect：`peek` 续传记录。
   - **校验 `workspace` 匹配**（不匹配则丢弃，防跨工作区误恢复）。
   - `setActiveConversationId(sessionId)` —— 用现成能力回到中断现场。
   - 将 `task` 下发给 `ChatSurface`（经 prop）。
   - `ChatSurface` 在已切对的会话里自动发出 `task`；发送成功后通知 `App.tsx`
     调 `clearPendingTask`（读后清的 clear 推迟到发送成功，抗 StrictMode 双挂载）。

## 职责边界（与旧设计的差异）

| 职责 | 旧设计 | 本 ADR |
|---|---|---|
| peek / 校验 workspace | ChatSurface | **App.tsx** |
| 切到 sessionId（回现场） | （缺失） | **App.tsx**（`setActiveConversationId`）|
| 在会话内自动发 task | ChatSurface | ChatSurface（收下发的 task）|
| 发送成功后 clear | ChatSurface | App.tsx（由 ChatSurface 回调触发）|

## 与「stream reattach（ADR 22）」的边界

两套独立机制：

- **pending-task（本 ADR）**：跨**进程重启**后回到原会话并发**新任务**。
- **stream reattach（ADR 22）**：同一进程 HMR/重载后接回**正在进行的流**。

## 验证

- store 单测：升级结构 write→read 往返、peek 不清、read 清、损坏/版本不符丢弃、
  缺 workspace/sessionId 的容错。
- 手动端到端：在某会话输 `/restart 续传指令` → 重启 → 新实例自动切回该会话 +
  自动发出续传指令 + 任务完成后续传记录已清除。
- 跨工作区保护：workspace 不匹配时不恢复。
