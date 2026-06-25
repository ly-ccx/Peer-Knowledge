# ADR 22 — HMR/重载后的流式重连(Stream Reattach on Reload)

状态: Accepted（实现中）
级别: A 级（触及运行时流式状态留存 + 新增跨进程 IPC 契约 + renderer 时序）
关联: 19-system-prompt-context-architecture, 20-architecture-governance

## 背景

开发期反复修改 renderer 会触发 Vite HMR / 整页重载。此时：

- 后端（main 进程）不受 HMR 影响，正在进行的一次流（agent loop / 推理）仍在运行，
  继续用原 `streamId` 通过 `webContents.send('chat:stream:delta', …)` 推送增量。
- 前端（renderer）被重载：
  - `streamIdRef`（内存 ref）重置为 `null`，丢失当前流身份。
  - `messages` 从磁盘重载，但正在生成、尚未落盘的 assistant 正文不在磁盘上
    （落盘只在 `done`/`aborted` 发生）。
  - 监听器重新挂上，守卫 `streamId !== streamIdRef.current` 此时恒为真（current=null），
    后端继续来的 delta 全被丢弃，正文接不上；而 done/usage 等副作用路径仍会触发
    setState/persist，表现为「界面不断刷新却接不上正文」。

根因一句话：**流的身份只存在内存，重载即失忆，无法重新认领正在进行的流。**

## 关键现状事实（已由代码核实）

- `llm-chat-service.mjs` 的 `activeStreams: Map`（约 19 行）每条记录是
  `{ controller, webContents, permissionIds }`（约 97 行）—— **不累积流式正文**。
- delta 通过 `webContents.send` 一次性推送，发完即弃。
- 因此「重载后取完整快照再续接」不可行：重载前已发出的正文在 main 侧无处可取。
- 可恢复的只有 `streamId / conversationId / webContents` 引用。

## 决策

为活跃流增加 main 侧文本累积缓冲 + 重连取快照入口，使重载后前端能认领进行中的流。

### Q1 缓冲留存范围（已定）

`accumulatedText` / `accumulatedThinking` 在流进行中保留，`done` / `aborted` 即删。
理由：够用、省内存；不为极小的「done 前后缝隙」付出常驻内存代价。

### Q2 reattach 触发方式（已定）

重载后**自动**认领唯一活跃流，无需用户操作。这正是「无缝续上」的本意。

## 设计

1. **main / `activeStreams` 记录扩展**
   - 记录增加 `accumulatedText: string`、`accumulatedThinking: string`、`conversationId`。
   - 每次发 `chat:stream:delta` / `chat:stream:thinking` 时同步追加到对应缓冲。
   - `done` / `aborted` / `error` 删除 `activeStreams` 记录时缓冲一并释放。

2. **新增 IPC `chat:stream:reattach`**
   - 入参：`{ streamId? }`。不传则返回「当前唯一活跃流」；存在多条时返回最近一条或要求显式 streamId。
   - 返回：`{ streamId, conversationId, accumulatedText, accumulatedThinking, isStreaming } | null`。
   - 只读，不改变流状态。

3. **renderer 时序**
   - `submitMessage` 生成 streamId 时，把 `{ streamId, conversationId }` 写入 `sessionStorage`
     （HMR/整页重载不清空 sessionStorage）。
   - 启动 effect：读 sessionStorage → 若有 → 调 `reattach`：
     - 命中活跃流：重建 assistant 占位消息、用 `accumulatedText/Thinking` 填回正文、
       `streamIdRef.current = streamId`、`setIsStreaming(true)` → 后续 delta 守卫即可匹配续接。
     - 未命中（流已结束）：清理 sessionStorage，恢复到稳定历史态。
   - `done` / `aborted` / `error` 时清空 sessionStorage。

## 与「任务续传（pending-task）」的边界

两套独立机制，不可混淆：

- **pending-task**：跨**进程重启**后接着发**新任务**（写盘 → 重启 → consume → 发送）。
- **stream reattach**：HMR/整页**重载**（同一进程）后接回**正在进行的流**（sessionStorage + main 缓冲）。

本 ADR 只覆盖后者。pending-task 的 `peekPendingTask` 改动与本 ADR 解耦，独立推进。

## 影响与边界

- 内存：每条活跃流多保留两段字符串，进行中保留、结束即释放，规模可控。
- 不改变流式对外事件契约（delta/thinking/done/...）本身，只新增 reattach 只读入口。
- 不持久化到磁盘：reattach 仅覆盖「同进程内重载」；进程重启的连续性由 pending-task 负责。

## 扩展 — 全局活跃流状态广播（左侧列表运行指示）

### 背景

左侧会话列表需要为「正在运行」的会话显示 Loading 图标。最初实现把运行真值挂在
当前激活会话（`ChatSurface.isStreaming` 经 `onStreamingChange` 上提单值），导致两个缺陷：

- 切到别的会话后，旧会话的 Loading / 停止按钮状态错误地跟随当前视图。
- 不点进某会话就无法得知它是否在跑（后台并行会话无指示）。

根因：运行状态被当成「当前视图的局部状态」，而它本质是 **main 进程 `activeStreams`
的全局真值**（已按 `conversationId` 记录，可枚举）。

### 设计

1. **service 暴露只读枚举 + 变更广播**
   - `listActiveConversationIds()`：从 `activeStreams` 去重收集 `conversationId`。
   - `activeStreams` 每次 set/delete（创建、finally 删除、abort 删除）后调用
     `emitActiveStreamsChanged()`，经注入的 `broadcast` 向所有窗口发
     `chat:stream:active-changed`，payload `{ conversationIds }`。
   - `broadcast` 由 main 注入（`BrowserWindow.getAllWindows()` 群发），service 不直接依赖 electron。

2. **新增 IPC `chat:stream:list-active`**
   - 只读，返回 `{ conversationIds }`。供 renderer 挂载时拉取初始快照（广播是增量，需快照兜底）。

3. **renderer**
   - App 持有 `runningConversationIds: ReadonlySet<string>`；挂载时 `chatStreamListActive`
     拉快照，并订阅 `onChatActiveStreamsChanged` 覆盖更新。
   - `ChatSurface.onStreamingChange` 仍保留，作为本会话的**即时**信号合并进集合（比广播更快反馈），
     权威真值最终由广播覆盖，二者一致。
   - Sidebar 由单值 `runningConversationId` 改为 `runningConversationIds.has(id)` 判断。

### 边界

- 与 reattach 正交：reattach 解决「重载后接回正文」，本扩展解决「全局列表运行指示」，
  两者都读 `activeStreams`，但前者取文本快照、后者取会话 id 集合。
- 广播是表达层用途，不是 Evidence，也不改变 delta/done/aborted 既有事件契约。

## 验证

- store/service 单测：缓冲随 delta 累积、done/aborted 后清空、reattach 返回快照、无活跃流返回 null。
- service 单测：`listActiveConversationIds` 随活跃流增删反映正确集合（去重、终态后清空）。
- 手动：发起一次长流式 → 改 renderer 触发 HMR → 确认正文从断点续接、界面不再乱刷。
- 手动：A 会话发起长流式 → 切到 B 会话 → 左侧 A 仍显示 Loading、B 不显示；A 结束后 A 的指示消失。
