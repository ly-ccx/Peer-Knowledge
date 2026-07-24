# Local Context Compaction 机制设计

创建时间：2026-06-08
最后更新：2026-07-24
状态：设计草案

本文定义 Peer Agent 本地侧的上下文压缩机制。重点不是“如何把历史塞进更短摘要”，而是建立一套本地任务线程可持续工作的上下文治理方法。

核心判断：

```text
本地不怕大文本存在。
本地怕大文本无选择地进入模型上下文。
```

本地有 shell、文件系统、`rg`、`sed`、`jq`、`head`、`tail` 等能力，因此大日志、大 JSON、大 diff、大工具输出不应该被急着语义销毁。它们应该成为可查询 Evidence / artifact，模型上下文里只保留索引、摘要、关键锚点和下一步检索方式。

## 一、目标

Local Context Compaction 要同时满足四件事：

1. 控制 LLM prompt 长度，避免请求超窗、变慢、变贵。
2. 保留任务连续性，让 compact 后的 agent 知道用户目标、当前进展和下一步。
3. 保留证据可追溯性，让大文本可以通过本地工具重新读取和精查。
4. 保持工具调用结构合法，不能切断 assistant tool call 和 tool result 的配对。

它不是长期记忆系统，也不是本地认知系统。

Peer Agent 仍然遵守既有边界：

```text
Cloud / model owns cognition.
Local runtime owns execution and evidence.
Compaction owns prompt hygiene and handoff continuity.
```

## 二、与云端机制的差异

云端压缩通常依赖 `summary + refId`：

- 大工具结果外置。
- LLM 只看到摘要和引用。
- 需要完整内容时通过服务接口恢复。

本地压缩应使用 `summary + local artifact + retrieval command`：

- 大文本保留在本地 artifact 中。
- LLM 看到路径、字节数、命令、exit code、head/tail、关键命中和建议检索命令。
- 需要完整内容时，让本地 shell 按需读取、过滤、切片。

示例：

```text
不要：
  把 5MB stdout 全量放进下一轮 prompt。

也不要：
  只保留“命令输出很长，发现一些错误”。

应该：
  command: pnpm test
  cwd: /repo
  exitCode: 1
  stdoutArtifact: .peer-agent/runs/run-123/stdout.txt
  stderrArtifact: .peer-agent/runs/run-123/stderr.txt
  byteCount: 5_241_900
  keyFindings:
    - 18 个测试失败
    - 首个失败在 packages/foo/src/bar.test.ts
  suggestedRetrieval:
    - rg -n "FAIL|Error|Expected" .peer-agent/runs/run-123/stdout.txt
    - sed -n '120,180p' .peer-agent/runs/run-123/stdout.txt
```

## 三、分层机制

Local compaction 分四层执行。顺序很重要。

### 3.1 新输出材料化

本地工具执行结束后，先决定 tool result 如何进入上下文。

小结果可以 inline。

大结果必须材料化为 artifact，并生成轻量 result message：

```ts
type LocalToolResultRef = {
  kind: 'local_tool_result_ref';
  command: string;
  cwd: string;
  exitCode: number;
  stdoutPath?: string;
  stderrPath?: string;
  outputPath?: string;
  byteCount: number;
  lineCount?: number;
  preview: {
    head?: string;
    tail?: string;
  };
  keyFindings?: string[];
  suggestedRetrieval?: string[];
};
```

原则：

- artifact 是事实承载。
- summary 是导航，不是事实本体。
- retrieval command 是恢复能力。

### 3.2 Microcompact 历史工具结果

每轮 LLM 调用前，先压缩历史中的旧工具结果。

策略：

- 保留最近若干个 tool result 的较完整内容。
- 对更早的大 tool result，只保留 `LocalToolResultRef`。
- 已经是 ref 的结果不能重复压缩。
- 错误结果可以比成功结果保留更多上下文，但仍要有 artifact。

这层优先处理最容易膨胀的内容：shell stdout、stderr、read file、大 JSON、搜索结果、构建日志。

### 3.3 Message window

Microcompact 后，如果消息数仍然过多，做消息窗口裁剪。

规则：

- 永远保留 system prompt。
- 永远保留最近 N 条消息。
- 不能让保留窗口从 `tool` message 开始。
- 如果切点落在 tool result 上，要向前回退到对应 assistant/tool call 之前，或整体转成 handoff block。

这一层只负责结构安全，不负责语义摘要。

### 3.4 Conversation handoff compaction

当 prompt token 压力超过阈值，生成一次上下文交接块：

```text
system
user: [上下文交接 - 共压缩 N 条消息]
recent messages...
```

交接块必须包含：

- 用户原始目标和最近明确要求。
- 已完成操作。
- 当前正在处理的工作。
- 未完成任务。
- 关键文件、命令、artifact refs。
- 已知错误和失败路径。
- 下一步建议。

交接块不应该包含：

- 大段原始日志。
- 大段工具输出。
- 大段文件全文。
- 无法追溯来源的泛化总结。

推荐结构：

```text
[上下文交接 - 共压缩 42 条消息]

## 用户请求
...

## 当前进展
...

## 已完成操作
...

## 关键证据
- runId: ...
- command: ...
- artifact: ...
- suggested retrieval: ...

## 文件与代码位置
...

## 未完成任务
...

## 下一步
...
```

## 四、触发策略

Local compaction 应支持三类触发。

### 4.1 Preflight

每次发送 LLM 前估算当前 prompt。

建议阈值：

```text
triggerRatio: 0.8
targetRatio: 0.35
```

（2026-07-24 校准：早期草案建议 0.75，`peer_agent` 实际落地为 0.8，另有 hardRatio 0.95 硬拦截线与摘要输出/安全区预留；以代码为准，详见 `knowledge/architecture/23-compaction-path-root-governance.md`。）

如果模型 context window 特别大，可以把 trigger 提高到 0.85，但不应因此允许工具输出无节制 inline。

### 4.2 Manual `/compact`

手动 compact 必须强制执行，不应受 triggerRatio 限制。

用户输入 `/compact` 的含义是：

```text
现在整理上下文，释放 prompt 空间，并保留可继续工作的交接信息。
```

因此即使当前 token 未超过阈值，也应该生成 handoff 或至少执行 microcompact。

### 4.3 Emergency

如果上游返回 prompt-too-long、context_length_exceeded、413 等错误，必须执行 emergency compact 并重试。

Emergency 策略：

- `force: true`
- `targetRatio: 0.2`
- 保留更少 recent messages。
- 必须保留 artifact refs 和下一步 retrieval commands。

## 五、摘要策略

Local compaction 的摘要不是越像自然语言越好，而是越可恢复越好。

摘要优先级：

1. 结构化事实：文件路径、命令、退出码、错误码、函数名、测试名。
2. 用户意图：用户明确要求、限制、偏好。
3. 工作状态：已完成、正在做、下一步。
4. 证据锚点：artifact path、line number、search command。
5. 简短语义解释：为什么这些事实重要。

不应该让 LLM 摘要替代可重放证据。

如果有 LLM semantic summary，可以作为 handoff 的一部分，但必须和 artifact refs 一起出现。

## 六、与当前实现的差距

当前 `context-compactor.mjs` 更接近“旧消息摘要 + 保留最近 10 条”的 MVP。

需要补齐：

- `/compact` 支持 force。
- 自动 compact 成功后写回线程上下文，避免下一轮又加载未压缩历史。
- 引入 local artifact ref，避免大工具输出进入 prompt。
- 引入 microcompact，优先清理旧工具结果。
- handoff block 使用 user message，而不是单纯 system summary。
- 切分时保护 tool call / tool result 配对。
- prompt-too-long emergency compact 后自动重试。

## 七、建议落地顺序

### P0：修正现有 compact 的正确性

- 修复触发路径中的未定义变量。
- 给 `/compact` 增加 `force`。
- 给 compact 入口增加单元测试：
  - 未达阈值但手动 compact 仍执行。
  - 自动 compact 达阈值不抛错。
  - compact 后保留 system + handoff + recent。

### P1：引入本地 tool result ref

- shell/read/search 输出超过阈值时写入 artifact。
- message 中只保留 ref、preview、key findings、retrieval commands。
- UI 可展开 artifact preview。

（2026-07-24 落地：shell/file/batch_search 早已有结构化 local_*_ref 落盘体系；本日补齐「其余大输出」的通用兜底材料化 —— `runtime-node tool-artifact-store`：超阈值输出落盘 `~/.peer-agent/artifacts/<conversationId>/`，provider 消息只留 `local_tool_result_ref` 骨架（head/tail 预览 + keyFindings + suggestedRetrieval + 勿重跑提示）；错误结果双倍预览；写盘失败降级 inline 交给 Layer 1；会话删除级联清理。Desktop tool-orchestrator 与 TUI executionContent 同源接入，UI 展示流不受影响。）

### P2：引入 microcompact

- 每轮调用前扫描历史 tool results。
- 旧的大结果替换为 ref stub。
- 最近结果保留原状。
- 已压缩结果不重复处理。

（2026-07-24 落地：microcompact 下沉 `runtime-core/microcompact.ts` 单源，Desktop re-export、TUI runTurn 发送切片接入（state 保留原文，与 Desktop apiMessages 同构）；结构化 local_*_ref 保留骨架与检索路径不哑截断；无结构长文本先抽可回捞线索（artifact/path/retrieval）再预览化。自此新结果经 P1 材料化后，Layer 1 几乎不再需要哑截断任何全文。）

### P3：引入 handoff compaction

- 以 `[上下文交接]` user message 替代纯 system summary。
- handoff 中必须列出 artifact refs。
- 支持 LLM summary + structural fallback。

### P4：引入 emergency retry

- 捕获 prompt-too-long 类错误。
- 强制 compact。
- 使用 compact 后消息重试一次。

### P5：Context Budget Manager（长期方向，方案 C）

2026-06-30 的最小闭环已把预算守卫集中在 `chat-runtime/compaction-coordinator.mjs`，并在 OpenAI / Anthropic / Gemini agent loop 的 provider 请求前调用：

- `computeContextBudget` 按 `messages + tools + contextWindow` 计算用量；工具 schema 每次请求都会发送，因此必须计入预算。
- `soft` 线沿用自动压缩触发线；`hard` 线作为发送前拦截线；超过 hard/window 时进入 `emergency + force` 压缩。
- provider 返回 prompt/context too long 时，先 emergency compact，并最多重试一次；重试仍失败时给明确的 context-window 错误。
- 本轮不改 provider adapter，不把预算逻辑下沉到各 provider wire protocol。

长期 Context Budget Manager 不应只是“更早触发 compact”，而应成为统一的请求预算规划层：

1. **统一预算模型**：把 system、messages、tools、attachments、reasoning 预留、max output、provider cache 影响纳入同一 Budget Snapshot。
2. **统一裁剪策略**：在发送前选择 microcompact、semantic compact、artifact ref、工具 schema 裁剪、附件摘要化等动作，并返回可解释计划。
3. **统一错误恢复**：将 prompt-too-long、rate/output budget、provider-specific context 错误归一为可恢复策略，而不是散落在各 loop。
4. **统一 UI 信号**：让进度条、压缩横幅、继续生成按钮看到同一预算状态，避免 `412k / 258k` 仍裸发 provider 请求。
5. **可测试边界**：Budget Manager 输出纯数据计划，provider adapter 只负责协议编码，agent loop 只负责执行计划和控制流。

非本轮范围：

- 不重构 provider adapter。
- 不引入全新的长期记忆系统。
- 不实现工具 schema 动态裁剪与附件级预算规划。
- 不改变 tool call / tool result 配对规则。

## 八、验收标准

本地 compact 机制完成后，应满足：

- 大于 1MB 的 shell output 不会完整进入 LLM prompt。
- `/compact` 在短会话中也能产生明确效果。
- compact 后下一轮不会重新带入被压缩的旧历史。
- compact 不会生成以 `tool` message 开头的上下文窗口。
- prompt-too-long 后可以自动压缩并重试。
- compact summary 中包含 artifact path 或 retrieval command，而不是只有自然语言摘要。

## 九、最终原则

```text
Local compaction does not delete evidence.
It moves evidence out of prompt and keeps the route back.
```

本地有 bash，所以大文本可以留在本地。

模型上下文只应该承载：

- 当前任务状态。
- 必要事实。
- 可追溯证据索引。
- 下一步执行意图。

这才是 Peer Agent 本地 compact 与云端 compact 的核心差异。
