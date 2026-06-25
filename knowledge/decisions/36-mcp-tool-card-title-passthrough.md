# 36. MCP 工具卡标题透传（MCP Tool Card Title Passthrough）

状态：Accepted

## 背景与问题

聊天时间线里每个工具调用会渲染一张工具卡，卡片标题对内置工具
（`bash` / `read_file` / `edit_file` / `write_file`）有专门的展示文案，对其余
工具回退到 `tool` 字段——即模型可见的裸 capability 名。

MCP 工具被投影给模型时，名字是 `mcp__{serverId}__{toolName}`
（见 `mcp-registry.mjs` 的 capability manifest 构造）。它的友好展示文案
`displayName`（形如 `服务名: 工具名`，由 `mcp-registry.mjs` 生成）**已经存在于
后端 Runtime Projection 的 capability manifest 里**，但没有沿事件链路传到表达层：

- `chat:stream:tool-call` 事件（`tool-orchestrator.mjs`）只发了
  `{ streamId, tool, args, toolCallId }`，`tool` 是裸名，`displayName` 在此被丢弃。
- 表达层段结构 `ContentSegment(tool-call)` / `ToolCallLegacy` 没有承载 `displayName`
  的字段位。
- 渲染层 `AssistantContent` 对 MCP 工具回退成裸名。

结果：MCP 工具卡“标题不见了”，显示成 `mcp__server__tool` 这类裸 capability 名，
而不是 `服务名: 工具名`。

## 决策

沿既有的 `Runtime Projection -> Tool Call -> 渲染` 链，把后端注入的
`displayName` 作为**一个可选的展示字段**透传到表达层。不新增执行路径，不改变
权限 / Evidence 链路。

`displayName` 是“界面负责表达”的展示文案：渲染层只消费它来显示标题，**不**据此
做能力路由、权限判定或 Evidence 归因。真正的工具执行仍由
`PermissionGrant -> Evidence` 接管，`tool`（裸 capability 名）仍是执行与匹配的真值。

缺省语义：找不到 / 为空串时回退到 `null`，渲染层据此回退到裸 capability 名，
保持既有行为不被破坏（内置工具的标题逻辑完全不变）。

## 契约变更

事件：`chat:stream:tool-call`（扩展，新增可选字段）

```ts
{
  streamId: string;
  tool: string;                    // 模型可见的裸 capability 名（执行真值，不变）
  displayName?: string | null;     // 新增：后端注入的展示文案（MCP 为「服务名: 工具名」）
  args: Record<string, unknown>;
  toolCallId: string;
}
```

表达层段结构（`apps/desktop/renderer/src/chat/state/types.ts`）：

- `ContentSegment`（`type: 'tool-call'`）新增 `displayName?: string | null`。
- `ToolCallLegacy`（聚合后的展示模型）新增 `displayName?: string | null`。

跨进程契约（`bootstrapPreloadApi.ts`）：`onChatStreamToolCall` 载荷与
`StreamReattachResult` 的 tool-call 段形状同步新增 `displayName?: string | null`。
preload 透传层原样转发 payload，无需改动。

## 后端 Seam

模块：`apps/desktop/electron/main/chat-runtime/tool-orchestrator.mjs`

新增导出纯函数：

```ts
resolveCapabilityDisplayName(runtimeProjection, name): string | null
```

按 capability `name` 从 Runtime Projection 反查后端注入的 `displayName`；
找不到或为空串返回 `null`。`executeModelToolCall` 在发出 `chat:stream:tool-call`
前调用它，把结果随事件透传。`runtimeProjection` 已是该函数入参，数据现成，
不引入新的数据源。

## 表达层透传

- `streamSegments.ts`：`normalizeStreamSegment` / `groupSegments` /
  `migrateToSegments` 三处在构造 tool-call 段 / `ToolCallLegacy` 时保留 `displayName`。
- `useChatStreamSubscription.ts`：从 `tool-call` 事件解构 `displayName` 写入段。
- `AssistantContent.tsx`：内置工具标题逻辑不变；其余工具
  `tc.displayName ?? tc.tool`，从而 MCP 工具显示「服务名: 工具名」。

## 测试

- `apps/desktop/electron/main/chat-runtime/tool-orchestrator.test.mjs`：
  `resolveCapabilityDisplayName` 的反查 / 无 displayName / 不在投影 / 空投影防御 /
  空串回退。
- `apps/desktop/renderer/src/chat/state/streamSegments.test.ts`：新增
  `groupSegments` 透传 displayName 的回归；同步更新 `normalizeStreamSegment` /
  `migrateToSegments` 因新增字段的断言。

运行：
`node --test "electron/main/**/*.test.mjs" "renderer/src/**/*.test.ts"`
（注意：`tool-orchestrator.test.mjs` 位于 `chat-runtime/` 子目录，仓库默认
`test` 脚本的顶层 glob 覆盖不到时需显式路径运行。）

## 边界声明（与治理基线一致）

- `displayName` 是运行时投影注入的展示文案，属于“界面负责表达”。
- 它不是 Tool Result，不是 Evidence，不是权限真值；渲染层只用于标题展示。
- 它不绕过 Runtime Projection / PermissionGrant / Evidence 链路；执行与匹配仍以
  `tool`（裸 capability 名）为真值。
- 缺省可回退（`null` -> 裸名），不破坏内置工具与历史消息的既有渲染。
