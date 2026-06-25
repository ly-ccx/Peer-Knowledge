# 29. 工具调用参数流式进度（Tool Arg Progress Streaming）

状态：Accepted

## 背景与问题

工具调用的参数（尤其 `edit_file` / `write_file` 的整文件 `content`）在
provider 流式响应里是**逐片增量**抵达的：

- Anthropic Messages：`content_block_delta` 的 `input_json_delta.partial_json`
- OpenAI Responses：`response.function_call_arguments.delta`
- OpenAI Chat Completions：`choices[].delta.tool_calls[].function.arguments`

在参数完全累积、落地为 `chat:stream:tool-call` 之前，renderer 对“正在写哪个
文件、已经写了多少”完全不可见。对于长内容编辑，UI 会长时间停留在“等待中”，
缺少 Codex 式的“已编辑 N 行 / 文件名”实时体感。

## 决策

在 **provider 适配层**（运行时投影的一部分）新增一个瞬时投影事件
`chat:stream:tool-progress`，在参数累积期间节流发出，供 renderer 展示实时进度。

事实仍由既有链路接管：参数累积完成 -> `chat:stream:tool-call` -> 本地能力执行
（`PermissionGrant -> Evidence`）。本事件**不**进入 Evidence，**不**替代
Tool Result，**不**写入 JSONL 历史，重载后不重放（参考 ADR 22 的重连语义：
进度是瞬时 UI 反馈，不是可重放的事实）。

## 契约

事件：`chat:stream:tool-progress`

载荷：

```ts
{
  streamId: string;        // 关联当前流
  toolCallId: string;      // 工具调用 id（chat 流早期可能为空字符串）
  tool: string;            // 工具名，如 edit_file
  path: string | null;     // 从增量 JSON 前部尽早解析出的目标路径
  receivedChars: number;   // 已累积参数 JSON 字符数
  receivedLines: number;   // 以字面量 \n 估算的“已接收行数”
}
```

renderer 侧将其投影为**单一的瞬时进度提示**（`toolProgress`），按最新事件覆盖，
不按 `toolCallId` 建表；并在 `tool-call` 落地 / `done` / `aborted` / `error`
时清空。因此 chat 流早期 `toolCallId === ''` 不影响展示。

## 共享 Seam

三个 provider 路径共用同一 Adapter 实现，收敛“解析 path / 估算行数 / 节流 /
发送”逻辑，避免三份拷贝（增加 Locality）：

- 模块：`apps/desktop/electron/main/provider-adapters/tool-arg-progress.mjs`
- 导出：`emitToolArgProgress(progress, ctx)`
  - `progress`：per-tool-call 的可变进度状态，由各 adapter 持有并复用
    （挂在各自的 block / entry 对象上），模块在其上记录
    `argPath` / `lastProgressAt` / `lastProgressLines`。
  - `ctx`：`{ webContents, streamId, toolCallId, toolName, argsJson }`。

节流：至少间隔 `120ms`；但只要“已接收行数”发生变化即立即发送，保证“行数在涨”
的体感不被节流吞掉。`webContents` 被销毁时静默跳过，不抛错。

调用点：

- `anthropic-messages-adapter.mjs`：`input_json_delta` 累积后
- `openai-responses-adapter.mjs`：`response.function_call_arguments.delta` 累积后
- `openai-chat-adapter.mjs`：`tool_calls[].function.arguments` 累积后

## 测试

`apps/desktop/electron/main/provider-adapters/tool-arg-progress.test.mjs`
覆盖：path 解析、行数估算、节流、行数变化时强制发送、path 尚未出现、
`webContents` 销毁、空 `progress`/`ctx` 容错、转义引号路径。

运行：`node --test electron/main/provider-adapters/tool-arg-progress.test.mjs`
（注意：仓库默认 `test` 脚本只 glob `electron/main/*.test.mjs` 顶层，
此文件位于子目录，需显式路径运行。）

## 边界声明（与治理基线一致）

- 这是运行时投影的瞬时反馈，属于“界面负责表达”。
- 它不是 Tool Result，不是 Evidence，不是可重放历史。
- 它不绕过 Runtime Projection / PermissionGrant / Evidence 链路；真正的写入
  仍由后续 tool-call 与本地能力执行接管。
