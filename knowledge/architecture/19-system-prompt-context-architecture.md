# System Prompt / System Context 体系技术方案

日期：2026-06-10
状态：技术方案 / 第一阶段已落地

本文定义 Peer Agent 后续的系统提示词体系。这里故意不把问题理解成“把一段更好的 system prompt 写长一点”，而是把它升级为一套可组合、可追踪、可测试、可演进的 `System Context` 组装机制。

核心判断：

```text
系统提示词不是一个字符串。
系统提示词是 Runtime 在安全边界内组装出来的系统上下文。
```

Peer Agent 当前已经有 `buildSystemPrompt()`、工具描述 prompt、压缩 prompt 和 Skill envelope，但这些还只是分散的 prompt 片段。下一阶段要建立的是一套有明确来源、顺序、权限边界和调试能力的上下文装配管线。

## 一、设计理念

本方案延续 Peer Agent 既有的端云能力代理设计原则：

```text
Runtime owns cognition boundary.
Capability Provider owns execution boundary.
Evidence owns factual boundary.
Prompt Assembly owns context admission boundary.
```

也就是说：

- Agent / Runtime 负责认知、规划、工具选择和策略解释。
- Capability Provider 负责本地能力发现、权限确认、执行和 Evidence 采集。
- Tool Result / Evidence 是事实承载，prompt summary 只是导航。
- System Context 只负责把“模型应该知道什么”送入模型，不负责执行任何能力。
- Project instructions、Skill、Plugin、MCP 都不能绕过统一能力链路。

核心主链路不变：

```text
Capability Provider
  -> Manifest
    -> Runtime Projection
      -> Tool Call
        -> PermissionGrant
          -> Evidence
```

系统提示词体系只影响模型如何理解上下文、如何选择工具、如何遵守边界；它不能成为一条新的执行旁路。

## 二、当前现状

当前相关代码主要在：

- `apps/desktop/electron/main/llm-prompts.mjs`
- `apps/desktop/electron/main/prompt/prompt-assembler.mjs`
- `apps/desktop/electron/main/prompt/prompt-source-registry.mjs`
- `apps/desktop/electron/main/prompt/sources/core-source.mjs`
- `apps/desktop/electron/main/prompt/sources/runtime-source.mjs`
- `apps/desktop/electron/main/llm-chat-service.mjs`
- `apps/desktop/electron/main/context-compactor.mjs`
- `apps/desktop/electron/main/main.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-skill-provider.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs`
- `apps/desktop/electron/main/runtime-gateway/capability-provider-registry.mjs`
- `apps/desktop/renderer/src/chat/components/ChatSurface.tsx`
- `apps/desktop/renderer/src/chat/state/historicalLocalRecord.ts`

已经具备：

- `System Context Assembly` 第一阶段骨架。
- `PromptSourceRegistry`。
- `core.identity` / `runtime.workspace` / `runtime.attachments` / `runtime.reminders` / `runtime.continuity` / `project.instructions` 默认 Context Source；`runtime.mode` 是 mode reminder 的兼容 section id。
- section 的 layer、priority、trust、checksum。
- prompt snapshot 的 `sectionRefs`、`renderedHash` 和 `~/.peer-agent/prompt-snapshots` debug dump。
- workspace root `AGENTS.md` / `CLAUDE.md` 的项目指令注入。
- `buildSystemCorePrompt()` / `buildRuntimeContext(workspacePath)` / `buildSystemPrompt(workspacePath)` 兼容入口。
- `electron/main/tools/*` Tool Registry
- OpenAI / Anthropic tool schema 构建
- `provider-encoders/message-normalizer.mjs` 中的 OpenAI / Anthropic 多模态 user message lowering
- `provider-encoders/request-encoder.mjs` 中的 OpenAI / Anthropic request shape lowering
- compaction summary prompt
- Skill instructions envelope
- evidence discipline 规则
- 无真实工具调用时的工具幻觉拦截
- assistant 历史文本里的伪 `[Tool call]` / `[Tool result]` 清洗
- renderer 侧图片 / 文本文件附件读取和发送
- shell / file 大输出 artifact ref 和 preview materialization
- `Local Tool Host` + `CapabilityProviderRegistry` 的正式本地能力 Seam
- `runtime-gateway/local-file-provider.mjs` 正式承载 `local.file.read` / `local.file.edit` / `local.file.write`
- legacy LLM file tools 已委托到 `local.file.*` Capability Provider，保留模型可见工具名兼容
- legacy LLM bash tool 已委托到 `local.shell.exec` Capability Provider，并复用 shell permission review / artifact / stop task 链路
- `tools/runtime-projection-tool-materializer.mjs` 可从 Tool Registry 生成 Runtime Projection / CapabilityManifest，并从 Projection materialize OpenAI / Anthropic tool schema
- main runtime 侧会话级“始终允许”权限签名缓存
- 附件 metadata Context Source，且图片 dataUrl / 文本正文不会进入 system prompt
- compaction continuity Context Source
- `packages/protocol/src/system-context.ts` 中的 `ChatSendRequest`、`ContextAttachmentItem`、legacy `AttachmentContextItem`、`RuntimeReminderItem`、`ContinuityContextItem`、`ConfigInstructionContextItem`、`ContextExtensionItem`、`PromptSnapshot*`、`PromptContextEpochRecord`、`PromptContextEpochEventRecord` 跨层契约
- `provider-adapters/openai-chat-adapter.mjs` / `provider-adapters/anthropic-messages-adapter.mjs` provider fetch + stream parsing adapter
- `chat-runtime/permission-gate.mjs` 承载 pending permission request、scope grant cache、file / shell permission request 构造和 stream settle
- `chat-runtime/tool-orchestrator.mjs` 承载模型工具参数解析、tool-call/result stream event 和 permission gate 绑定
- `chat-runtime/projected-tool-executor.mjs` 承载 model-visible tool -> Runtime Projection capability -> Local Tool Host -> model-compatible output 的迁移期适配
- `chat-runtime/compaction-coordinator.mjs` 承载 microcompaction、常规压缩、prompt-too-long 紧急压缩、持久化和 UI notification
- `chat-runtime/response-guard.mjs` 承载空响应、伪工具调用文本、无工具证据声明和 dangling tool intent 的拦截策略
- `chat-runtime/openai-agent-loop.mjs` / `chat-runtime/anthropic-agent-loop.mjs` 承载 provider-specific turn loop、tool call continuation、usage 汇总和 provider error recovery
- `chat-runtime/message-sanitizer.mjs` 承载 provider 请求前的空消息清理

当前实现可用，但长期会变成：

```text
一个文件里不断加字符串。
一个服务里不断加例外分支。
出问题时很难知道最终发给模型的完整上下文是什么。
```

### 2.1 最新代码解析

以下解析基于 2026-06-10 当前代码。

| 领域 | 当前实现 | 判断 |
|---|---|---|
| Core prompt | `llm-prompts.mjs` 保留兼容入口，实际委托给 `prompt/*` 的 System Context Assembly | 已从散落字符串收敛为 Source / Section / Snapshot；默认 source 已覆盖 runtime、attachments、mode、continuity、project instructions |
| Project instructions | `prompt/sources/project-instructions-source.mjs` 加载 config instructions、workspace root / nested / explicit global `AGENTS.md`，兼容 root `CLAUDE.md`；`chat:send` 透传 `configInstructions`；模型配置页持久化 `settings.systemInstructions` | 已作为 `L3_INSTRUCTIONS` 接入，保留来源路径、scope、截断标记和 snapshot ref；config/global/workspace/scoped 顺序可测试 |
| Tool prompt/schema | `tools/index.mjs` + `tool-registry.mjs` + `legacy-local-tool-definitions.mjs` + `runtime-projection-tool-materializer.mjs` + `provider-tool-materializer.mjs` | Tool Registry 边界已落地，tool definition 已有 capabilityId、permissionPolicy、runtime migration metadata、executorCapabilityId；provider schema 已由 Runtime Projection materialize；执行侧通过 projected executor 从 Projection 定位正式 Capability Provider |
| Provider adapter | `provider-adapters/openai-chat-adapter.mjs` + `provider-adapters/anthropic-messages-adapter.mjs` | request body encoding、fetch、stream parsing 已从 chat service 抽出；provider adapter 不拥有 tool continuation 或 permission；deep/reasoning/thinking stream delta 必须作为独立 thinking side channel 收集；provider SSE `type:error` / stream error 是 provider fact，必须作为 `provider_stream_error` 返回，不能被误判为 empty response |
| Agent Loop | `chat-runtime/openai-agent-loop.mjs` + `chat-runtime/anthropic-agent-loop.mjs` | provider-specific turn loop 已从 chat service 抽出；loop 负责调用 provider adapter、compaction coordinator、tool orchestrator 和 response guard；`llm-chat-service.mjs` 只做 provider 选择、System Context assembly、stream 生命周期和权限 gate 组合 |
| Agent Loop Kernel | `chat-runtime/agent-loop-kernel.mjs` | max turn、usage 累加、stream done/error、无工具幻觉 retry 计数、终态文本响应流转已抽为 provider-neutral kernel；后续可继续抽 provider-neutral provider error / retry transition |
| Provider prompt selection | `prompt/sources/provider-source.mjs` | provider/model family 级别 runtime guidance 已作为 `runtime.provider` Context Source 接入；只声明结构化工具调用与 provider target，不承担 provider wire-format encoding |
| Provider encoder | `provider-encoders/message-normalizer.mjs` + `provider-encoders/request-encoder.mjs` | OpenAI / Anthropic message content lowering 与 request shape lowering 已抽出并测试；`effort=high` 只是用户意图，只有 provider config 显式 `supportsReasoning` 时才发送原生 `reasoning_effort` / `thinking` wire 参数；Anthropic-compatible provider 可能有不同 reasoning wire-format，例如 official `thinking.type=enabled + budget_tokens` 与 idealab `thinking.type=adaptive + output_config.effort` |
| Context extensions | `prompt/sources/context-extension-source.mjs`；`chat:send` 透传 `contextExtensions` | Plugin / Skill / MCP 可通过 `contextExtensions` 贡献受限 L3/L4/L5 上下文；extension 不授予本地执行权限，不替代 Tool Result 或 Evidence |
| Multimodal | `ChatSurface.tsx` 读取图片为 data URL，文本文件内联；`attachment-source.mjs` 只接收 metadata；provider encoder 做 OpenAI / Anthropic normalization | 附件 payload 属于 user message，metadata 属于 System Context；unsupported file 不静默丢失 |
| Local tools | `runtime-gateway/local-file-provider.mjs` + `runtime-gateway/local-shell-provider.mjs` + `chat-runtime/projected-tool-executor.mjs` | file read/edit/write 已进入正式 `local.file.*` Capability Provider；bash 已进入正式 `local.shell.exec` Capability Provider；模型工具名由 projected executor 映射到 Runtime Projection capability |
| Runtime Gateway | `local-tool-host.mjs` + `capability-provider-registry.mjs` 提供 Provider Adapter Seam | 这是正式能力运行链；当前已注册 health、file、shell、mcp、skill providers |
| Permission | `chat-runtime/permission-gate.mjs` 管理 pending request 和 main-runtime scope grant cache；文件越界写入和模型侧 bash 都通过 `chat:stream:permission-request` 阻塞等待；shell provider 仍有 `permission-review.mjs` 和 rule store | “始终允许”事实已不只存在于 renderer；后续可把 file permission 也统一到 PermissionReview 持久规则 |
| Tool Orchestrator | `chat-runtime/tool-orchestrator.mjs` + `chat-runtime/projected-tool-executor.mjs` | chat service 不再直接持有 legacy tool executor、shell artifact store、tool result event materialization；runtime 执行侧已通过 `executeModelToolCall()` 直连 Runtime Projection / Local Tool Host，旧 `executeTool()` 兼容入口已删除 |
| Compaction Coordinator | `chat-runtime/compaction-coordinator.mjs` | chat service 不再直接持有 compactor、token 阈值、`chat:compaction` event 细节；OpenAI / Anthropic loop 只接收压缩后的 messages |
| Response Guard | `chat-runtime/response-guard.mjs` | chat service 不再直接持有工具幻觉正则和拦截文案；后续应逐步由结构化 tool call/result 消除这些兜底策略 |
| Always allow | `chat-runtime/permission-gate.mjs` 的会话/工作区/能力签名 scope cache | 点击一次后同 scope 后续自动放行；后续可提升为 PermissionRule 持久化 |
| Compaction | `context-compactor.mjs` 支持 microcompact、LLM summary、structural fallback、manual `/compact`；`continuity-source.mjs` 接收 persisted compaction summary | 后续发送不再把 compaction card 当普通 user history，而是以 `runtime.continuity` 进入 System Context |
| Context Epoch | `prompt-snapshot-store.mjs` 写入 `baselines.jsonl`、`context-epochs.jsonl`、`latest-context-epochs.json`、`context-epoch-events.jsonl`；`prompt/context-baseline-recorder.mjs` 记录 provider / instruction context baseline；普通 prompt snapshot 记录 `contextEpochId` | baseline 已成为 durable Context Epoch 起点，并记录 replacement chain；`epoch_created` / `epoch_replaced` / `snapshot_anchored` 事件形成可查询 ledger；default provider/model 变化会自动创建 `model_switch` baseline；`settings.systemInstructions` 变化会自动创建 `instruction_change` baseline；同一轮 provider retry 复用同一个 assembled system prompt 和 active `contextEpochId` |
| Manual compact | `main.mjs` 的 `chat:compact` 使用 `buildSystemContext(..., { mode: 'compact' })` 并写 prompt snapshot | 已消除 core/runtime prompt 重复拼接，compact turn 有 mode reminder 和 debug dump |
| Pseudo tool guard | `hasUnsupportedToolClaim()`、`hasDanglingToolIntent()` 拦截无真实工具调用的工具声称 | 这是必要兜底，但不应成为长期主治理机制；根因应由原生 tool call / tool result 结构解决 |
| History rendering | `historicalLocalRecord.ts` 把历史工具片段包为 read-only context，并清理展示泄漏 | 过渡方案正确，长期应由结构化 ThreadEvent 替代文本 wrapper |

### 2.2 当前最重要的架构事实

当前代码里已经有两条本地工具路径：

```text
LLM provider tool call
  -> chat-runtime/tool-orchestrator.executeModelToolCall()
  -> projected-tool-executor
  -> Runtime Projection capability
  -> Local Tool Host
    -> local.file.* provider for read_file/edit_file/write_file
    -> local.shell.exec provider for bash

Runtime Gateway client tool call
  -> Local Tool Host
  -> CapabilityProviderRegistry
  -> local.health / local.file / local.shell / local.mcp / local.skill
```

这两条路径都能执行本地能力。模型仍看到 `bash/read_file/edit_file/write_file`，但执行事实已经由 `local.shell.exec` 和 `local.file.*` Provider 承担。`projected-tool-executor` 负责把模型工具名解析为 Runtime Projection capability，并把正式 provider result 适配回 provider tool message。

因此后续 System Context 体系不能继续把 `TOOL_REGISTRY` 理解成最终工具系统。当前 `TOOL_REGISTRY` 是生成 Runtime Projection 的输入，provider-visible schema 已经从 Projection materialize，执行侧也从 Projection 定位 Capability Provider：

```text
Capability Manifest
  -> Runtime Projection
    -> ToolRegistry materialization
      -> ProviderToolDefinition
```

### 2.3 当前多模态事实

当前多模态输入是“用户显式提供的消息内容”，不是本地能力执行：

```text
File / paste
  -> renderer FileReader
    -> ChatAttachment
      -> Chat API user message content parts
        -> provider-specific normalization
```

治理判断：

- 图片附件可以作为 user message image content 进入模型。
- 文本附件可以在大小限制内作为 user content 进入模型。
- unsupported file 只能提供 metadata，不能假装内容已读取。
- 附件内容不得被提升为 system instruction。
- 后续大文件、目录、二进制、压缩包必须走 artifact / Context Source / Evidence 引用。

## 三、参考基线

### 3.1 Claude Code

Claude Code 给我们的核心启发不是某几句 prompt，而是几个行为约束：

- 工具调用必须是真实 tool call，不能靠文本伪造。
- 文件编辑必须 read-before-edit。
- 工具 prompt 要描述何时使用、何时不用、失败如何处理。
- 长上下文要能 compact，并保留继续工作的摘要。
- 用户和项目指令要进入模型上下文，但不能覆盖系统安全边界。

Peer Agent 已经落地了一部分：

- evidence discipline。
- `read_file` / `edit_file` / `write_file` 的工具规则。
- 历史伪 `[Tool call]` / `[Tool result]` 清理。
- local context compaction。

还没有完整落地的是：项目指令层、mode layer、tool prompt registry、prompt snapshot 和上下文来源治理。

### 3.2 OpenCode

OpenCode 的重要启发是把“system prompt”抽象为 `System Context`。它的顶层设计包含：

- `System Context`：模型可见的系统上下文集合。
- `Context Source`：独立观测、可比较、可渲染的上下文来源。
- `Context Epoch`：一段稳定 baseline system context 的生命周期。
- `Baseline System Context`：一次 epoch 开始时完整送入模型的系统上下文。
- `Mid-Conversation System Message`：上下文来源变化后的模型可见系统更新。
- Tool Registry：工具描述、schema、权限、执行、输出截断在统一边界管理。

OpenCode 的优点：

- 上下文来源明确。
- provider / model prompt 可分流。
- project instructions 是一等上下文来源。
- Skill 先以可发现清单进入 prompt，body 通过 permission-checked skill tool 加载。
- 工具 prompt 文件化，扩展工具不会污染核心 system prompt。
- 权限和工具执行不只依赖 prompt，而是在 tool executor 中强制执行。
- compaction 是 anchored summary，重复压缩会更新 previous summary。

Peer Agent 不应直接复制完整 OpenCode V2 事件系统，但应该吸收它的抽象边界：

```text
Prompt string -> System Context
Prompt fragment -> Context Source
Tool description strings -> Tool Registry
Ad hoc compaction -> Context replacement boundary
```

## 四、目标

### 4.1 产品目标

用户应该获得稳定、可信、可解释的 Agent 行为：

- 模型知道自己能做什么、不能做什么。
- 模型知道当前 workspace、模式、工具、项目规则。
- 模型不会声称不存在的工具执行结果。
- 项目规则能自动进入上下文。
- 长会话 compact 后仍能继续。
- 调试时能看到“这一轮到底发给模型了什么系统上下文”。

### 4.2 工程目标

工程上要满足：

- 模块化：每类上下文一个 source，不堆字符串。
- 抽象清晰：source 只产出上下文，tool 只执行能力。
- 可拓展：后续 Plugin / Skill / MCP 能贡献上下文，但必须走注册入口。
- 可测试：每个 source、assembly order、provider lowering 都能单测。
- 可观测：每轮请求能生成 prompt snapshot。
- 可迁移：先不引入重型事件化 epoch，也能逐步演进。

### 4.3 非目标

本方案不做：

- 长期记忆系统。
- 向量检索系统。
- 自动学习用户偏好。
- 直接复制 Claude Code 或 OpenCode 的实现。
- 让 Plugin 任意修改最终 system prompt。
- 让 project instructions 覆盖内置安全规则。

## 五、核心抽象

### 5.1 System Context

`System Context` 是 Runtime 在一次 provider turn 前组装出来的模型可见系统上下文。

它由多个 section 组成：

```ts
type SystemContext = {
  version: number;
  sections: PromptSection[];
  snapshot: PromptSnapshot;
};
```

它不是普通聊天历史，也不是用户消息。

### 5.2 Context Source

`Context Source` 是系统上下文的最小可治理来源。

```ts
type ContextSource<TValue> = {
  id: string;
  layer: PromptLayer;
  trust: PromptTrustLevel;
  observe(input: PromptAssemblyInput): Promise<ContextObservation<TValue>>;
  render(observation: ContextObservation<TValue>): PromptSection[];
};
```

典型 source：

- `core.identity`
- `core.evidence_discipline`
- `runtime.environment`
- `runtime.workspace`
- `runtime.model`
- `instructions.project`
- `instructions.global`
- `tools.registry`
- `skills.available`
- `input.attachments`
- `mode.plan`
- `mode.compaction`
- `mode.structured_output`

source 的职责只有两个：

1. 观察当前状态。
2. 渲染模型可见 section。

source 不能：

- 执行本地工具。
- 改写聊天历史。
- 私自发起权限确认。
- 直接修改 provider request。

### 5.3 Prompt Section

`PromptSection` 是最终 system context 的可见组成单元。

```ts
type PromptSection = {
  id: string;
  layer: PromptLayer;
  priority: number;
  title: string;
  content: string;
  source: PromptSourceRef;
  trust: PromptTrustLevel;
  checksum: string;
};
```

`checksum` 用于：

- debug。
- 快照比较。
- 判断上下文是否变化。
- 后续 Context Epoch replacement。

### 5.4 Prompt Layer

分层顺序固定，不允许随意插入：

| Layer | 内容 | 是否可被覆盖 |
|---|---|---|
| `L0_CORE` | 产品身份、安全边界、证据纪律 | 不可覆盖 |
| `L1_AGENT` | 当前 agent / mode 的职责说明 | 可由 agent 配置选择 |
| `L2_RUNTIME` | workspace、model、日期、平台、语言 | Runtime 生成 |
| `L3_INSTRUCTIONS` | AGENTS / CLAUDE / 配置 instructions | 受 scope 和优先级治理 |
| `L4_CAPABILITIES` | 工具、Skill、MCP、Plugin 可见能力 | Runtime Projection 生成 |
| `L5_TOOL_RULES` | 每个工具的使用规则和 schema description | Tool Registry 生成 |
| `L6_MODE_REMINDER` | plan / compact / structured output / max steps | 当前 turn 临时注入 |
| `L7_CONTINUITY` | compact summary / handoff / previous work | Compactor 生成 |

越底层越不可覆盖。项目 instructions 只能约束项目风格和工作流，不能覆盖 `L0_CORE`。

### 5.5 Prompt Snapshot

每次 provider turn 都生成一个 snapshot。

```ts
type PromptSnapshot = {
  id: string;
  createdAt: string;
  conversationId: string;
  workspacePath: string | null;
  provider: string;
  model: string;
  mode: string;
  sectionRefs: {
    id: string;
    layer: PromptLayer;
    checksum: string;
    source: PromptSourceRef;
  }[];
  renderedHash: string;
  renderedPreviewPath?: string;
};
```

snapshot 是本地调试对象，不默认发送给模型。

用途：

- 复现模型行为。
- 判断 project instructions 是否生效。
- 判断某个 tool prompt 是否进入上下文。
- 排查 provider-specific lowering。
- 对比 compact 前后的系统上下文变化。

## 六、整体架构

```text
PromptSourceRegistry
  -> ContextSource.observe()
    -> ContextObservation[]
      -> PromptAssembler
        -> SystemContext
          -> PromptSnapshotStore
            -> ProviderPromptEncoder
              -> OpenAI / Anthropic / Compatible Provider Request

ToolRegistry
  -> ToolDefinition
    -> ToolPrompt
    -> ToolSchema
    -> PermissionPolicy
    -> ToolExecutor
```

### 6.1 模块划分

建议新增目录：

```text
apps/desktop/electron/main/prompt/
  index.mjs
  prompt-types.mjs
  prompt-source-registry.mjs
  prompt-assembler.mjs
  prompt-snapshot-store.mjs
  provider-prompt-encoder.mjs

  sources/
    core-source.mjs
    runtime-source.mjs
    instruction-source.mjs
    capability-source.mjs
    skill-source.mjs
    attachment-source.mjs
    runtime-reminder-source.mjs
    compaction-source.mjs

  tool-prompts/
    bash.txt
    read_file.txt
    edit_file.txt
    write_file.txt
```

后续工具扩展时，再把工具注册迁移到：

```text
apps/desktop/electron/main/tools/
  tool-registry.mjs
  tool-definition.mjs
  builtin/
    bash.mjs
    read-file.mjs
    edit-file.mjs
    write-file.mjs
```

旧 `executeTool()` 入口名已经删除。新增本地能力必须进入 `Local Tool Host` / `CapabilityProviderRegistry`。当前模型可见工具已由 `projected-tool-executor` 从 Runtime Projection 定位到 `local.file.*` 和 `local.shell.exec`，测试和运行时代码必须直接使用 `executeProjectedModelTool()` 或 `executeModelToolCall()`。

### 6.2 边界

| 模块 | 职责 | 禁止事项 |
|---|---|---|
| `PromptSourceRegistry` | 注册 source，按 layer / priority 排序 | 不读写用户文件 |
| `ContextSource` | 观察状态并渲染 section | 不执行工具，不改消息 |
| `PromptAssembler` | 合并 section，生成最终 context | 不关心 provider wire 格式 |
| `ProviderPromptEncoder` | 把 context 编码成 provider 请求 | 不改变 section 内容 |
| `ToolRegistry` | 工具 schema、prompt、permission、executor | 不写 system prompt |
| `Compactor` | 历史消息压缩和 continuity section | 不替代 Evidence |
| `InstructionSource` | 加载 AGENTS / CLAUDE / config instructions | 不赋予本地能力权限 |
| `AttachmentSource` | 接收用户显式选择 / 粘贴的附件上下文 | 不读取任意本地路径，不提升为 system instruction |
| `ProviderPromptEncoder` | 统一 OpenAI / Anthropic / future API lowering | 不执行工具，不做权限判断 |

## 七、Prompt Assembly Pipeline

每次 `sendMessage()` 前执行：

```text
1. resolve provider / model / effort
2. resolve active workspace
3. resolve active agent / mode
4. observe context sources
5. assemble sections
6. generate prompt snapshot
7. encode provider request
8. send request
```

伪代码：

```js
const assembly = await promptAssembler.assemble({
  conversationId,
  workspacePath,
  provider,
  model,
  mode,
  effort,
  messages,
  toolRegistry,
});

await promptSnapshotStore.write(assembly.snapshot);

const request = providerPromptEncoder.encode({
  provider,
  model,
  systemContext: assembly.context,
  messages,
  tools: assembly.tools,
});
```

### 7.1 Section 顺序

排序规则：

```text
layer asc
priority asc
source id asc
```

同层同优先级必须稳定排序，避免同一输入生成不同 prompt。

### 7.2 冲突处理

冲突分三类：

| 冲突 | 处理 |
|---|---|
| 同 source id 重复注册 | 启动时报错 |
| project instructions 和 core prompt 冲突 | core prompt 优先，instructions 作为普通上下文保留 |
| tool prompt 和 tool executor 不匹配 | 测试失败，不允许发布 |

### 7.3 不可用 source

source 不可用时不能随意生成半真半假的 section。

规则：

- `L0_CORE` 不可用：启动失败。
- `L2_RUNTIME` 不可用：本轮请求失败。
- `L3_INSTRUCTIONS` 读取失败：记录 warning，保留上一轮已确认 snapshot，或明确不注入该 source。
- `L4_CAPABILITIES` 不可用：不暴露对应工具。
- `L6_MODE_REMINDER` 不可用：禁用该 mode 或失败。

## 八、Instruction Source 设计

### 8.1 支持范围

第一阶段支持：

- 全局 `~/.peer-agent/AGENTS.md`
- workspace 向上查找的 `AGENTS.md`
- 可选兼容 `CLAUDE.md`
- 配置项 `instructions: string[]`

后续支持：

- glob instructions
- remote URL instructions
- nested instructions after file read
- plugin-defined instruction source

### 8.2 优先级

推荐顺序：

```text
global AGENTS.md
workspace root AGENTS.md
nearest scoped AGENTS.md
configured instructions
optional CLAUDE.md compatibility
```

项目指令适用范围遵循路径 scope：

```text
AGENTS.md governs its directory and descendants.
Deeper AGENTS.md overrides higher-level instructions for files under that subtree.
```

但这种 override 只在 `L3_INSTRUCTIONS` 内部生效，不能覆盖 `L0_CORE`。

### 8.3 模型可见格式

模型可见内容要带来源：

```text
Project instructions from: /repo/AGENTS.md
<content>
```

如果多个 instruction source 同时生效，应输出聚合后的完整有序集合，而不是只输出 diff。

这样模型能明确知道当前规则来源，也方便 debug。

## 九、Tool Registry 设计

当前 `TOOL_REGISTRY` 在 `llm-prompts.mjs` 中定义。后续应迁移为正式 `ToolRegistry`。

### 9.1 ToolDefinition

```ts
type ToolDefinition = {
  id: string;
  displayName: string;
  capabilityId: string;
  promptPath: string;
  inputSchema: JsonSchema;
  permissionPolicy: ToolPermissionPolicy;
  execute(args: unknown, context: ToolExecutionContext): Promise<ToolExecutionResult>;
};
```

### 9.2 Tool Prompt

每个工具一个 `.txt`：

```text
tool-prompts/read_file.txt
tool-prompts/edit_file.txt
tool-prompts/write_file.txt
tool-prompts/bash.txt
```

工具 prompt 必须描述：

- 用途。
- 何时使用。
- 何时不要使用。
- 参数约束。
- 失败语义。
- 与其他工具的关系。
- 需要验证的后续动作。

### 9.3 Tool Boundary

工具边界必须是强边界：

```text
Prompt says what the model should do.
Tool executor enforces what can happen.
Permission system decides whether it may happen.
Evidence records what actually happened.
```

禁止把安全约束只写在 prompt 里。

例如：

- `edit_file` prompt 要求 read-before-edit。
- `edit_file` executor 也必须校验 read state。
- UI 要能显示 permission request。
- tool result 要包含成功、失败、拒绝或取消的结构化结果。

### 9.4 当前 `TOOL_REGISTRY` 的迁移约束

当前 `TOOL_REGISTRY` 可以继续作为 `ToolRegistry` 的最小迁移入口，但必须遵守：

- 不再新增没有 `capabilityId` 映射的工具。
- 不再把 executor 逻辑继续塞进 `llm-chat-service.mjs`。
- `bash/read_file/edit_file/write_file` 已映射到 `local.shell.exec`、`local.file.read`、`local.file.edit`、`local.file.write` Capability Provider。
- provider-specific schema 由 registry lowering 出来，而不是手写多份 prompt。
- tool prompt、input schema、permission policy、output shape 和 executor 必须能在测试里一一对应。

短期允许：

- 保留 `buildOpenAITools()` / `buildAnthropicTools()` 的外部函数名，内部改为读 registry。
- 保留现有测试断言，新增 section order / registry consistency 测试。

不允许：

- 为附件、MCP、Plugin、Skill 增加新的 ad hoc model-visible tool path。

### 9.5 Attachment Context 设计

附件不是工具结果，也不是系统指令。它是用户显式提供给当前 turn 的输入上下文。

#### 9.5.1 当前实现

当前 renderer 已实现：

- 图片文件：读取为 `dataUrl`，作为 `{ type: 'image_url' }` 发送。
- 文本文件：在 512KB 内读取文本并追加到 user message。
- unsupported file：只携带 name / MIME / size 和“不含内容”的说明。
- 图片大小限制：8MB。
- 单轮附件数量限制：8。

当前 main 已实现：

- OpenAI：保留 `image_url`。
- Anthropic：把 data URL 转为 `{ type: 'image', source: { type: 'base64' } }`。

#### 9.5.2 目标抽象

当前正式协议对象是 `ContextAttachmentItem`，旧 `AttachmentContextItem` 只作为兼容输入存在：

```ts
type ContextAttachmentItem = {
  id: string;
  sourceKind: 'user_upload' | 'clipboard' | 'skill' | 'memory' | 'hook' | 'mcp' | 'runtime';
  scope: 'turn' | 'conversation' | 'workspace' | 'session';
  lifecycle: 'ephemeral' | 'durable_ref' | 'evidence_ref';
  name: string;
  mimeType: string;
  size: number;
  kind: 'image' | 'text' | 'unsupported';
  contentIncluded: boolean;
  transport: 'provider_image_part' | 'user_text_part' | 'metadata_only';
  contentRef?: string;
};
```

`AttachmentSource` 负责：

- 接收 renderer 传来的 attachment metadata。
- 校验大小、类型、来源。
- 生成 metadata-only System Context section。
- 记录 prompt snapshot 中的 attachment refs。

`AttachmentSource` 不负责：

- 从任意本地路径读取文件。
- 执行 OCR、解压、代码分析。
- 把附件内容写进 system prompt。
- 把 provider content part 混入 system prompt。
- 绕过 PermissionReview 读取用户未选择的文件。

图片 dataUrl 和文本正文属于 user message payload，由 renderer 处理用户显式选择 / 粘贴的 File 对象，再交给 provider encoder 做 lowering。System Context 只接收 metadata。

与 Claude Code 的差异：

- Claude Code 把很多运行态信息统一建模为 attachment message。
- Peer Agent 使用 `ContextAttachmentItem` 做协议边界，后续 hook / memory / skill / MCP / queued command 可以统一进入这个对象。
- 是否进入 user payload、system metadata 还是 Evidence，必须由 sourceKind / lifecycle / transport 决定，不能靠渲染文本猜测。

#### 9.5.3 Provider Lowering

provider lowering 必须集中到 `ProviderPromptEncoder`：

| Provider | 图片 | 文本附件 |
|---|---|---|
| OpenAI Chat Completions | `image_url` content part | `text` content part |
| Anthropic Messages | `image` base64 block | `text` block |
| future Responses API | 原生 input content parts | 原生 file / image part |

如果 provider 不支持图片，必须明确失败或降级为 metadata，不允许静默丢弃。

## 十、Skill / Plugin / MCP 上下文

### 10.1 Skill

Skill 不应该把完整 body 全量塞进 system prompt。

推荐模式：

```text
System Context:
  available skills list
  name + description + when to use

Tool:
  skill(name) -> permission checked -> returns SKILL.md body + resources
```

当前轻量入口是 `runtime.contextExtensions`：Skill / Plugin / MCP 可以贡献 manifest、能力提示或加载提示，但只能作为受限 Context Extension 进入 L3/L4/L5，不能授予本地执行权限。

这样做的好处：

- prompt 更短。
- Skill body 只有在需要时进入上下文。
- Skill loading 可被权限系统记录。
- Skill 不能绕过 Tool Registry。

### 10.2 Plugin

Plugin 可以贡献：

- capability manifest
- local tool executor
- settings UI
- diagnostics
- optional context source

Plugin 不可以：

- 任意拼接 system prompt。
- 绕过 Runtime Projection 暴露工具。
- 覆盖 core prompt。
- 直接写 permission rules。

Plugin-defined context source 必须注册到 `PromptSourceRegistry`，并声明：

- source id
- layer
- trust level
- max chars
- redaction policy

### 10.3 MCP

MCP 是能力传输协议，不是 prompt 系统。

MCP server 可以产出 tools/resources，但必须先进入：

```text
Capability Manifest -> Runtime Projection -> ToolRegistry materialization
```

MCP resource 是否进入 prompt，由 `CapabilitySource` 或显式用户引用决定。

## 十一、Runtime Reminder

很多强约束不是永久系统提示词，而是当前 turn / session / workspace 的 Runtime Reminder。

Peer Agent 借鉴 Claude Code 的 `<system-reminder>` 思路，但不把 tag 当成主要架构边界。正式边界是 `RuntimeReminderItem`：

- 协议对象：`packages/protocol/src/system-context.ts`
- Prompt Source：`apps/desktop/electron/main/prompt/sources/runtime-reminder-source.mjs`
- legacy adapter：`mode / effort / provider / model` 仍可合成 `runtime.mode` section，兼容旧快照和测试。

示例：

- `/compact`
- plan mode
- max steps reached
- structured output
- tool disabled
- waiting for permission

这些不应该散落在业务逻辑里，也不应该拼到普通 user/tool text 里，而应该进入 `runtime-reminder-source.mjs`。

Runtime Reminder 只表达运行态约束或提醒：

- 不替代 Tool Result。
- 不替代 Evidence。
- 不携带附件 payload。
- 不授予本地执行权限。
- 必须有 kind、scope、sourceKind、trust，可被 prompt snapshot 追踪。

### 11.1 Plan Mode

```text
Plan mode active.
Read-only except the plan file if explicitly allowed.
Do not edit code.
End with plan approval handoff.
```

### 11.2 Compact Mode

```text
Compaction mode active.
Summarize only historical context.
Do not call tools.
Do not answer the user task.
Return structured continuity summary.
```

### 11.3 Structured Output

```text
Structured output required.
Complete all required tool calls before final structured output.
Final answer must use the structured output channel/tool.
```

### 11.4 Max Steps

```text
Maximum steps reached.
Tools disabled.
Summarize completed work and remaining tasks.
```

Mode reminder 必须有明确生命周期：只作用于当前 provider turn 或当前 mode session。

## 十二、Compaction 与 Context Replacement

当前本地 compaction 已经具备三层机制：

- microcompact old tool refs
- semantic / structural summary
- manual `/compact`

新体系中，compaction 要成为 `L7_CONTINUITY` 的来源。

### 12.1 Anchored Summary

重复 compact 时，不应每次从零总结。

推荐结构：

```text
previous summary
new compacted history
recent tail
```

当前实现要求：

- 已持久化的 `_compaction` handoff 不再作为普通 user message 进入下一次 compactor。
- prior continuity 通过 `runtime.continuity` 和 `compactIfNeeded(..., { continuityContext })` 显式 carry forward。
- 新 handoff 的 summary 由 previous continuity summary + 本次 delta summary 合成。
- metadata 区分 `deltaMessageCount`、`previousMessageCount`、`originalMessageCount`；UI notification 的 `oldMessageCount` 表示本次新压缩的消息数。

输出固定 section：

```text
## Goal
## Constraints & Preferences
## Progress
## Key Decisions
## Next Steps
## Critical Context
## Relevant Files
## Evidence / Artifacts
```

### 12.2 Evidence 保留

compact summary 不能替代 Evidence。

所有大输出仍然应保留：

- artifact path
- command
- cwd
- exit code
- stdout / stderr preview
- suggested retrieval

模型需要事实时，应该通过工具重新读取 artifact。

### 12.3 Context Epoch 的 durable 事件模型

当前已实现 durable Context Epoch ledger：

```ts
type PromptContextEpoch = {
  conversationId: string;
  contextEpochId: string;
  baselineId: string;
  snapshotId: string;
  renderedHash: string;
  createdAt: string;
  replacesContextEpochId: string | null;
  reason: 'initial' | 'manual_compact' | 'auto_compact' | 'model_switch' | 'instruction_change';
};

type PromptContextEpochEvent = {
  eventType: 'epoch_created' | 'epoch_replaced' | 'snapshot_anchored';
  contextEpochId: string;
  previousContextEpochId: string | null;
  baselineId: string | null;
  promptRecordId: string;
  contextSnapshotId: string;
  reason: string | null;
  occurredAt: string;
};
```

当发生：

- manual compact
- auto compact
- model switch
- instruction source 变化
- agent mode 变化

生成新的 baseline snapshot，并同步生成一个 durable Context Epoch record 与 event。

事件语义：

| Event | 触发 | 含义 |
|---|---|---|
| `epoch_created` | 第一个 baseline | 一个稳定 System Context baseline 开始生效 |
| `epoch_replaced` | 新 baseline 替换旧 epoch | compact、model switch、instruction change 等上下文边界改变 |
| `snapshot_anchored` | 普通 prompt snapshot 绑定 active epoch | 某次请求或 retry 明确站在哪个 System Context baseline 上 |

查询入口：

- `listContextEpochs()`：列出 epoch。
- `listContextEpochEvents()`：列出 durable event ledger。
- `getContextEpochChain()`：从 latest epoch 反查 replacement chain。
- `prompt-context-epochs:*` IPC：把 ledger 暴露给 renderer / 调试入口。

## 十三、Provider Encoder

不同 provider 对 system prompt 的承载方式不同。

Provider Encoder 负责做最后一层转换。

```ts
type ProviderPromptEncoder = {
  encode(input: {
    provider: string;
    model: string;
    systemContext: SystemContext;
    messages: ApiMessage[];
    tools: ProviderToolDefinition[];
  }): ProviderRequest;
};
```

规则：

- OpenAI Chat Completions：system context 作为第一条 `role: system`。
- Anthropic Messages：system context 放到 `system` 字段。
- OpenAI Responses / future native APIs：按 provider 原生 instructions 字段编码。
- 如果 provider 支持多个 system chunks，保留 section 边界。
- 如果 provider 不支持，按 layer 顺序 join。

Provider Encoder 不能改变 section 内容，只能改变 wire 格式。

## 十四、Debug 与可观测性

### 14.1 Prompt Snapshot Debug

本地保存：

```text
~/.peer-agent/prompt-snapshots/<conversationId>/<snapshotId>.json
```

内容包含：

- section metadata
- rendered hash
- redacted rendered preview
- provider
- model
- mode
- workspace
- timestamp

默认不保存 secrets。

### 14.2 UI 调试入口

后续可在开发模式加：

```text
模型配置 -> 当前系统上下文
```

展示：

- 当前 provider / model。
- system context section 列表。
- instructions 来源。
- tool 列表。
- prompt token estimate。
- rendered preview。

### 14.3 日志

日志只打印：

- snapshot id
- rendered hash
- section ids
- token estimate

不默认打印完整 prompt。

## 十五、权限与安全

### 15.1 Trust Level

```ts
type PromptTrustLevel =
  | 'builtin'
  | 'runtime'
  | 'project_instruction'
  | 'user_config'
  | 'plugin'
  | 'skill'
  | 'tool_result';
```

信任等级不等于优先级。

例如：

- `project_instruction` 可以要求代码风格。
- `project_instruction` 不能允许 destructive shell。
- `plugin` 可以贡献说明。
- `plugin` 不能覆盖 evidence discipline。

### 15.2 Prompt Injection 防线

所有外部来源都必须带来源 wrapper：

```text
Project instructions from: ...
```

工具输出、网页内容、文件内容不得被提升为 system instruction，除非经过明确 Context Source admission。

### 15.3 能力暴露防线

模型看到的工具必须来自 `Runtime Projection` 或本地内置 allowlist。

不能因为某个 instructions 写了“可以使用 xxx 工具”，就把工具暴露给模型。

## 十六、迁移计划

### Phase 0：当前代码对齐

目标：先让文档、测试和代码事实一致，避免后续实现建立在错误前提上。

已确认当前事实：

- `buildSystemPrompt()` 仍是兼容入口，但内部已委托 System Context Assembly。
- `TOOL_REGISTRY` 已从 `llm-prompts.mjs` 迁到 `electron/main/tools/*`，`llm-prompts.mjs` 只保留兼容导出。
- runtime 模型工具执行已由 `executeModelToolCall()` 直连 `projected-tool-executor`；旧 `executeTool()` 迁移期兼容入口已经删除，`llm-chat-service` 不再 re-export 本地工具执行能力。
- `Local Tool Host` 已经存在，并且是正式能力执行 Seam。
- 图片 / 文本附件已经能进入 provider message，但不是 Context Source。
- `/compact` 已经存在，`chat:compact` 已复用 System Context Assembly 和 compact mode reminder。
- workspace root `AGENTS.md` / `CLAUDE.md` 已经通过 `project.instructions` 进入模型运行时。
- OpenAI / Anthropic provider-specific Agent Loop 已拆到 `chat-runtime/*-agent-loop.mjs`，`llm-chat-service.mjs` 不再直接持有 provider stream parser、compaction loop 或 tool continuation。

约束：

- Phase 0 不新增新能力。
- Phase 0 只允许补测试、补文档、补最小回归保护。
- 任何新增本地能力必须进入 Tool Registry / Runtime Projection / Local Tool Host，不得新增兼容 executor 旁路。

### Phase 1：Prompt Assembly Skeleton

目标：替换 `buildSystemPrompt()` 的内部实现，但保持外部 API 不变。

改动：

- 新增 `prompt-types.mjs`
- 新增 `prompt-source-registry.mjs`
- 新增 `prompt-assembler.mjs`
- 新增 `sources/core-source.mjs`
- 新增 `sources/runtime-source.mjs`
- `buildSystemPrompt(workspacePath)` 内部改为调用 assembler。
- `main.mjs` 的 `chat:compact` 改为复用同一 assembly 入口。

验收：

- 现有测试不变。
- `buildSystemPrompt('/tmp/workspace')` 输出仍包含 evidence discipline 和 workspace。
- section order 有单测。
- manual `/compact` 和普通 agent turn 看到同一套 core/runtime context。

### Phase 2：Instruction Source

目标：正式支持 `AGENTS.md`。

已落地：

- 新增 `sources/project-instructions-source.mjs`。
- workspace root `AGENTS.md` 生效。
- workspace root `CLAUDE.md` 兼容。
- nested `AGENTS.md` 按目标文件 scope 生效。
- explicit global `AGENTS.md` 可通过 `includeGlobalInstructions` / `dataHomePath` 注入。
- configured instructions 可通过 `configInstructions` 注入。
- 单文件字符数上限和截断提示。
- prompt snapshot 中记录 instruction path、filename、truncated、originalChars、includedChars。

验收：

- workspace root AGENTS 生效：已覆盖。
- nested AGENTS 对子路径生效：已覆盖。
- explicit global AGENTS 生效：已覆盖。
- config instructions 生效：已覆盖。
- config instructions 持久化 UI 和用户可编辑入口：已覆盖。
- project instructions 不能覆盖 core evidence discipline：已覆盖。

### Phase 3：Tool Prompt Registry

目标：把工具描述从 `llm-prompts.mjs` 拆出。

已落地：

- 新增轻量 `ToolRegistry`
- `buildOpenAITools()` / `buildAnthropicTools()` 从 registry 读取。
- 新增 `legacy-local-tool-definitions.mjs`，集中定义当前 bash/read/edit/write 的 prompt、schema、capabilityId、permissionPolicy、runtime migration metadata。
- 新增 provider tool materializer，保证 OpenAI / Anthropic schema 从同一个 registry materialize。
- `llm-prompts.mjs` 只 re-export 工具 API，不再持有工具定义。
- 新增 `runtime-gateway/local-file-provider.mjs`，承载 read-before-edit、fresh read、越界写权限、diff preview 和 Evidence。
- `legacy-llm-local-tool-provider.mjs` 的 file tools 已委托到 `local.file.*` provider，legacy adapter 不再直接读写文件。
- `legacy-llm-local-tool-provider.mjs` 的 bash tool 已委托到 `local.shell.exec` provider，legacy adapter 不再直接 `execSync`。
- 新增 `runtime-projection-tool-materializer.mjs`，由 Tool Registry 生成 CapabilityManifest / Runtime Projection，并从 Projection materialize provider tool schema。
- 新增 `chat-runtime/projected-tool-executor.mjs`，模型工具执行侧已从 Runtime Projection 解析到 Local Tool Host，再进入正式 file / shell Capability Provider。
- 新增 `tools/prompts/*.txt`，bash/read_file/edit_file/write_file 的 description 文本已资产文件化。

验收：

- OpenAI / Anthropic tool schema 数量一致：已覆盖。
- provider tool schema 不泄漏 runtime / permissionPolicy metadata：已覆盖。
- tool definition 有 capabilityId 和 permission policy：已覆盖。
- 每个工具 description 来自对应文件：已覆盖。
- schema 和正式 executor id 一致：已由 Runtime Projection materializer 和 projected executor 覆盖。

### Phase 3.5：Attachment Context Source

目标：把当前 renderer-local 附件处理收敛成可治理的 attachment context admission。

改动：

- 定义 `ContextAttachmentItem`，保留 legacy `AttachmentContextItem` adapter。
- 新增 `sources/attachment-source.mjs`。
- `ChatSurface` 继续处理用户显式 File 对象，但发送结构化 metadata。
- provider message lowering 迁到 `provider-encoders/message-normalizer.mjs`。

验收：

- 图片附件在 OpenAI / Anthropic provider 下都有测试。
- provider message lowering 已有直接单测。
- unsupported file 不会静默进入 prompt。
- 附件内容不会进入 system prompt。
- prompt snapshot 能列出附件来源和大小。

### Phase 4：Runtime Reminder Source

目标：把 plan / compact / structured output / max steps 统一管理。

改动：

- 新增 `sources/runtime-reminder-source.mjs`
- `mode-source.mjs` 只作为 legacy 兼容入口存在。
- `/compact` 使用 compact mode reminder。
- future plan mode 复用同一入口。

验收：

- compact summary 请求不携带普通工具。
- max steps reminder 只在对应 turn 出现。

### Phase 4.5：Native Reasoning Capability Gate

目标：修复“深度模式”被直接映射为 provider 原生参数导致兼容网关空响应的问题，并保证 provider stream error 不再被吞成 `empty_model_response`。

设计：

- `effort=high` 是用户意图，进入 `RuntimeReminderItem` / System Context。
- provider 原生 deep 参数是模型能力，不是 UI 模式本身。
- OpenAI `reasoning_effort`、Anthropic `thinking` 只能在模型配置 `supportsReasoning=true` 时发送。
- `supportsReasoning=true` 仍不足以决定 wire-format。Provider Encoder / Adapter 必须选择 provider-compatible reasoning format：
  - official Anthropic：`thinking: { type: 'enabled', budget_tokens }`，并保证 `max_tokens > budget_tokens`。
  - idealab Anthropic gateway：`thinking: { type: 'adaptive' }` + `output_config: { effort: 'high' }`。
- 未声明能力时，深度模式降级为 prompt-level guidance，不改变 provider wire shape。
- 已声明能力但返回空响应时，视为 provider/native reasoning 不兼容：同一轮自动用 `supportsReasoning=false` 重试，并持久关闭该 provider 的 `supportsReasoning`。
- 已声明能力但 provider 通过 SSE `type:error` 返回不兼容原因时，必须返回 `provider_stream_error` 和 provider trace，而不是把错误帧吞掉后报空响应。

验收：

- 未开启 `supportsReasoning` 的 Anthropic provider 在 `effort=high` 下不发送 `thinking`。
- 未开启 `supportsReasoning` 的 OpenAI provider 在 `effort=high` 下不发送 `reasoning_effort`。
- 开启能力后原生 deep 参数仍可用，并由 provider adapter 解析 thinking side channel。
- 开启能力后若 native deep 空响应，用户不会看到 `empty_model_response`，下一次请求也不会再次发送不兼容 native reasoning 参数。
- Provider trace 落在 `~/.peer-agent/provider-traces/YYYY-MM-DD.jsonl`，记录 request shape summary、HTTP status、SSE event/delta summary、stream error、empty stream anomaly；不得记录 API key 或完整 prompt。

### Phase 5：Prompt Snapshot

目标：让每轮请求可调试。

改动：

- 新增 `prompt-snapshot-store.mjs`
- `llm-chat-service` 发送请求前写 snapshot。
- 开发日志打印 snapshot id。

验收：

- 本地能找到 snapshot JSON。
- snapshot 不包含 API key。
- snapshot 能说明 AGENTS 是否注入。
- snapshot 能说明 attachment 是否内联、降级或仅 metadata。

### Phase 6：Context Baseline / Epoch Ledger

目标：让 System Context baseline、replacement 和 prompt snapshot anchoring 形成可持久追溯的 ledger。

已落地：

- `prompt-snapshot-store.mjs` 支持 `recordBaseline()`、`listBaselines()`、`getLatestBaseline()`。
- baseline record 写入 `baselines.jsonl`，并以 `latest-baselines.json` 保存每个 conversation 的最近 baseline。
- baseline record 同步生成 durable Context Epoch，写入 `context-epochs.jsonl`，并以 `latest-context-epochs.json` 保存每个 conversation 的最近 epoch。
- Context Epoch 记录 `contextEpochId`、`baselineId`、`reason`、`renderedHash` 和 `replacesContextEpochId` replacement chain。
- Context Epoch event 写入 `context-epoch-events.jsonl`，记录 `epoch_created`、`epoch_replaced`、`snapshot_anchored`。
- `prompt-snapshot-store.mjs` 支持 `listContextEpochEvents()` 和 `getContextEpochChain()`。
- `main.mjs` 暴露 `prompt-context-epochs:list`、`prompt-context-epochs:events`、`prompt-context-epochs:chain` IPC 查询入口。
- `prompt/context-baseline-recorder.mjs` 负责 provider context baseline；新增默认 provider、默认 provider 的 provider/model 修改、显式 set default、删除默认 provider 后自动切换都会记录 `initial` / `model_switch` baseline。
- `settings.systemInstructions` 持久化配置变化会记录 `instruction_change` baseline，并通过 `configInstructions` 进入后续 chat turn。
- manual `/compact` 成功后，会用压缩结果的 `_compaction` summary 重建带 `runtime.continuity` 的 chat baseline，并记录 `manual_compact` baseline。

验收：

- compact 后 baseline hash 更新：已覆盖。
- compact 后 Context Epoch 更新并记录 replacement chain：已覆盖。
- Context Epoch event ledger 记录创建、替换、snapshot 锚定：已覆盖。
- 可反查 latest epoch 的 replacement chain：已覆盖。
- default provider/model 变化后记录 baseline：已覆盖。
- settings.systemInstructions 变化后记录 instruction baseline：已覆盖。
- 同一轮重试复用相同 baseline：已通过固定 system prompt 和 `contextEpochId` snapshot 锚定覆盖。

## 十七、测试策略

### 17.1 Unit Tests

- source 注册顺序。
- layer 排序。
- duplicate source id 报错。
- runtime source 输出 workspace。
- core source 输出 evidence discipline。
- instruction source 读取 AGENTS。
- provider encoder 输出 OpenAI / Anthropic 格式。
- attachment source 输出 user context，不输出 system instruction。
- provider encoder 正确 lower 图片附件。

### 17.2 Integration Tests

- `sendMessage()` 使用 assembler 输出。
- 工具 schema 来自 ToolRegistry。
- compact mode 不允许工具。
- AGENTS 生效但不能覆盖 core。
- prompt snapshot 写入成功。
- `/compact` 复用普通 System Context core/runtime sections。
- `chat:send` 的多模态消息不绕过 provider encoder。

### 17.3 Regression Tests

必须覆盖这些历史问题：

- assistant 文本里的 `[Tool call]` 不变成真实工具调用。
- 没有真实 tool call 时，不能声称已经执行。
- compact 后工具调用配对仍合法。
- old tool result ref 不被展开成巨大 prompt。
- `AGENTS.md` 中的恶意“忽略系统提示词”不能覆盖 core。
- unsupported attachment 不被模型误认为内容已读取。
- manual compact 不再使用和普通 turn 不一致的 system prompt。

## 十八、验收标准

达到以下标准，才算 Peer Agent 有完整系统提示词体系：

1. 所有系统上下文都来自注册 source。
2. 所有 source 有 layer、priority、trust、checksum。
3. 每次请求有 prompt snapshot。
4. `AGENTS.md` / runtime context / tool prompt 都可在 snapshot 里定位来源。
5. 工具描述和工具执行在 ToolRegistry 内绑定。
6. Provider Encoder 是唯一负责 provider wire 差异的模块。
7. project instructions 不能覆盖 core evidence discipline。
8. compact summary 作为 continuity source 注入，不替代 Evidence。
9. 新增工具不需要修改 core prompt。
10. 新增 mode 不需要修改 `llm-chat-service` 主循环。
11. 附件和多模态输入通过 Attachment Context 进入 user context，不进入 system instruction。
12. `chat:compact`、auto compact、普通 provider turn 共用同一个 core/runtime context assembly。
13. model-visible tools 来自 Runtime Projection / ToolRegistry materialization，而不是 `llm-chat-service` 私有旁路。
14. 重复 compact 使用 carry-forward + delta summary，不重复把旧 handoff 当新消息压缩。

## 十九、架构取舍

### 19.1 为什么不直接复制 OpenCode Context Epoch

OpenCode 的 Context Epoch 很完整，但它依赖更重的 session event、durable history、runner ownership 和 provider-turn boundary。

Peer Agent 当前更适合分两步：

1. 先做 Prompt Assembly Pipeline，把散落字符串收敛成有来源的系统上下文。
2. 再基于 prompt snapshot 做轻量 baseline。
3. 最后在需要时演进到完整 Context Epoch。

这样能快速解决当前问题，又不把产品迭代压在一次大重构上。

### 19.2 为什么不让 Plugin 直接 transform system prompt

任意 transform 很灵活，但边界太弱。

更好的方式是：

```text
Plugin contributes ContextSource.
PromptAssembler controls ordering and trust.
ProviderEncoder controls wire format.
```

这样既可扩展，也可调试。

### 19.3 为什么 Tool Prompt 要离开 llm-prompts.mjs

工具 prompt 不是 core system prompt。

工具 prompt 应该跟：

- tool id
- input schema
- permission policy
- executor
- output shape

绑定在同一个 tool definition 里。

否则后续 MCP、Plugin、Skill 工具增加时，`llm-prompts.mjs` 会变成不可维护的中心泥球。

## 二十、最终目标形态

最终 Peer Agent 的模型请求应具备这种结构：

```text
System Context
  L0_CORE
    - product identity
    - evidence discipline
    - execution boundary
  L1_AGENT
    - selected agent role
  L2_RUNTIME
    - workspace
    - model
    - platform
    - date
  L3_INSTRUCTIONS
    - global AGENTS
    - project AGENTS
    - configured instructions
  L4_CAPABILITIES
    - runtime projection summary
    - available skills summary
  L5_TOOL_RULES
    - tool schemas and descriptions
  L6_MODE_REMINDER
    - plan / compact / structured output / max steps
  L7_CONTINUITY
    - compaction summary
    - artifact refs

Session History
  - user messages
  - assistant messages
  - native tool calls
  - native tool results

Tool Registry
  - provider tool schema
  - permission policy
  - executor
  - evidence result shape

Attachment Context
  - user selected / pasted files
  - image / text / unsupported metadata
  - provider lowering
  - snapshot refs
```

这套体系的关键不是 prompt 写得更长，而是：

```text
每一句系统上下文都知道自己来自哪里。
每个工具都知道自己如何被描述、授权和执行。
每次模型请求都能被复现和解释。
```

这才是可长期演进的系统提示词体系。
