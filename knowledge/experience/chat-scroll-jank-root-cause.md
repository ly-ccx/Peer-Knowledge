# 聊天窗口滚动一顿一顿（scroll jank）根因与修复

> 代码仓库：`peer_agent`（桌面端 `apps/desktop`）  
> 知识仓库：`peer-knowledge`  
> 日期：2026-07-27  
> 相关实现：`useVirtualChatTurns` / `virtualTurns` / `ChatSurface` 滚动路径

## 1. 用户可感知现象

长会话中上下滚动聊天窗口时，列表明显「一顿一顿」：不是单纯内容加载慢，而是滚动过程中频繁掉帧、视口跳动或 sticky 上下文闪动。

## 2. 渲染链路（source of truth）

```text
ChatSurface
  div.chat-thread (threadRef, onScroll=handleThreadScroll)
    frameCoalescer (每帧最多一次)
      → useVirtualChatTurns.updateViewport
      → sticky/header 几何探测
  虚拟窗口 items → ChatTurn (memo + areChatTurnRenderPropsEqual)
    measureElement → ResizeObserver 动态测高
```

- 轮次 > 20 且查找面板关闭时启用虚拟列表。
- 虚拟模型：`paddingStart + 可见 turn DOM + paddingEnd`，高度默认估算 360px，overscan 900px。
- 测高缓存按 turn index 存在 hook 内部 `Map`，是滚动几何的 source of truth。

## 3. 根因（按因果链）

### 3.1 主因：滚动把 scrollTop 写进 React state

旧实现里 `useVirtualChatTurns` 每次 `updateViewport` 都：

1. 读 `scrollTop/clientHeight`
2. `setViewport(...)`
3. `useMemo(calculateVirtualTurnRange, [..., viewport.scrollTop])`

即便窗口内 turn 集合完全没变，`viewport.scrollTop` 变化也会让 **整个 `ChatSurface` 重渲染**（该 hook 挂在巨型父组件上）。长会话里每帧重绘 Composer/Header/侧栏联动状态 + 可见 turn 协调，足以造成「一顿一顿」。

**证伪条件**：若滚动时 React Profiler 显示 `ChatSurface` 每帧 commit，而虚拟 `startIndex/endIndex` 不变，即可确认不是「虚拟化没生效」，而是 state 边界放错层。

### 3.2 次因：测高同步 `setRevision` + 同步改 `scrollTop`

`ResizeObserver` 在窗口滑动时对新挂载 turn 测高，旧逻辑：

- 每个高度变化立即 `setRevision(+1)`
- 若条目在视口上方，同步 `scrollElement.scrollTop += delta`

这会在同一滚动手势里叠出：测高 → 改 scrollTop → 再触发 scroll → 再 setState 的反馈环，表现为内容跳动/卡顿。

### 3.3 辅因：滚动帧全量 DOM 扫描

`findCurrentTurnIdForScroll` 曾 `querySelectorAll('[data-chat-turn-id]')` 并对每个节点 `getBoundingClientRect()`。虚拟窗口内节点虽少，但仍是滚动热路径上的多余布局读取；同一帧还可能重复探测（sticky + snapshot）。

## 4. 修复（最小正确链，不做表面补丁）

### 4.1 `useVirtualChatTurns`

- `scrollTop/clientHeight` 只写 **ref**。
- 计算 range 后用 signature（`startIndex/endIndex/padding*/totalSize/forceIndex/enabled/count`）比较；**只有窗口真正变化才 `setRange`**。
- 测高 delta 累计到 `pendingScrollAdjust`，**rAF 合并一次**写 `scrollTop` + publish。
- 关闭虚拟化仍走同一路径：`overscanPx = MAX_SAFE_INTEGER`，不另开渲染分支。

### 4.2 `ChatSurface` 滚动路径

- sticky turn 探测改为 `elementFromPoint` + `closest('[data-chat-turn-id]')`。
- `setCurrentTurnId` / `setIsThreadAtBottom` / `setThreadScrolled` 做 **同值短路**。
- 同一滚动帧内把已探测的 `turnId` 传给 snapshot，避免重复 DOM 命中。

## 5. 验证

- 单元测试：`node --experimental-strip-types --test renderer/src/chat/state/virtualTurns.test.ts renderer/src/chat/state/chatTurnRenderEquality.test.ts`（含「同窗口内 scrollTop 变化 range 签名稳定」契约）。
- 相关 `tsc` 无新增报错。
- 手工：长会话上下快速滚动，应不再每像素触发整树重绘；窗口跨 turn 边界时才换挂 DOM。

## 6. 非目标 / 后续

- 未引入第三方虚拟列表库（保持现有 padding 模型与测高契约）。
- 未拆 `ChatSurface` 大组件为独立 VirtualThread 子树（主因已通过 hook 侧 setState 门闩解决；若仍有流式输出期卡顿，再把列表渲染隔离到 memo 子组件）。
- Markdown/代码高亮单条 turn 成本不在本次范围；若单 turn 极重，应在 `AssistantContent` 层做惰性/分片，而不是关掉虚拟化。

## 7. 经验口诀

> 滚动热路径里，**几何进 ref，窗口进 state**。  
> 测高修正要 **合并写 scrollTop**，不要在 ResizeObserver 里同步连环 setState。  
> sticky 探测用 **命中测试**，不要全量 query + 全量 layout。
