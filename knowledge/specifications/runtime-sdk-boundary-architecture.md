# Runtime SDK Boundary Architecture

> 创建时间：2026-07-09
> 最后更新：2026-07-12
> 状态：边界已落地首批纵向切片（持续迁移中）
> 关联路线：`knowledge/playbook/tui-hook-sdk-roadmap.md`
> 关联设计：`knowledge/specifications/tui-and-hook-design-standard.md`、`knowledge/specifications/hook-phase1-implementation-design.md`、`knowledge/specifications/hook-phase1-code-walk.md`
> 关联治理：`knowledge/architecture/20-architecture-governance.md`
> 目标代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`

---

## 0A. 已落地边界补充（2026-07-12）

本节记录代码已经形成的事实，优先级高于后文 2026-07-09 的前置调研描述。

### 0A.1 当前分层

```text
@peer-agent/runtime-core
  Manifest / Projection / PermissionGrant / Evidence 基础契约
        ↓
@peer-agent/runtime-sdk
  Runtime Pipeline / Runtime Event / Hook Port / Approval Port
        ↓
@peer-agent/runtime-node
  Node Provider Bundle / File / Shell / Model Provider / Node Hook Host
        ↓
Desktop Adapter                         TUI Adapter
Electron 路径与 UI                       OpenTUI 路径与审批 UI
```

### 0A.2 SDK Hook Port 与 Node Hook Host 的职责

| Module | Interface | Implementation responsibility | 明确不负责 |
|---|---|---|---|
| Runtime SDK Hook Port | `RuntimeSdkHookRunner`、结构化 Hook payload/record、`allow/ask/deny` 决策 | 定义 Pre/Post 执行顺序、`ask` 进入 Approval Port、Hook record 进入 Evidence | 不读取配置、不启动进程、不知道 Node/Electron/OpenTUI |
| **Node Hook Host** | `createNodeHookRunner()`、`createConfiguredNodeHookRunner()`、配置加载与 matcher API | 读取全局 `<userDataPath>/hooks/hooks.json` 和工作区 `.peer/hooks.json`，合并配置，执行外部命令，处理 timeout、非零退出与 fail-open/fail-closed | 不展示审批 UI、不写 Renderer 状态、不绕过 PermissionGrant |
| Desktop Adapter | Runtime SDK / Node Hook Host 的宿主参数 | 提供 Electron `userDataPath`、workspace、既有 permission UI 和 Desktop Evidence 展示 | 不再维护私有 `child_process` Hook Runner；原文件仅保留兼容导出 |
| TUI Adapter | Runtime SDK / Node Hook Host 的宿主参数 | `PEER_USER_DATA_PATH`（默认 `~/.peer-agent`）、workspace、终端审批 UI 和事件呈现 | 不导入 Desktop/Electron 私有实现，不复制 Hook Runner |

### 0A.3 治理不变式

1. Hook 仍处于 `Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence` 主链内，未建立第二执行通道。
2. PreToolUse 的 `deny` 直接阻断；`ask` 只能通过宿主 Approval Port 转成明确 PermissionGrant；hook `allow` 不能覆盖 Shell/File 自身风险策略。
3. PostToolUse 在 Provider 之后运行，用于审计与 Evidence，不回滚已经产生的 Provider 结果。
4. Runtime SDK 生产源码保持宿主中立；文件系统、`child_process` 和路径发现只存在于 Node Hook Host。
5. Desktop 与 TUI 使用同一配置语义、匹配器、决策合并、超时/失败策略和 Evidence 记录。

### 0A.4 当前未完成边界

- `@peer-agent/runtime-sdk` / `@peer-agent/runtime-node` 仍为 monorepo 私有包，独立发布和兼容性矩阵尚未收口。
- Desktop 仍有部分会话、模型和宿主编排未迁移到公共 Pipeline。
- TUI 已有真实模型、File/Shell、审批与 Hook 纵向切片，但会话恢复、多模式、非交互 CLI 与完整分发仍待建设。

---

## 0. 一句话结论

当前 `peer_agent` 的方向是正确的：已经形成了 **Tool Projection → Runtime Gateway → Capability Provider → PermissionGrant → Evidence → Hook** 的主链，且 Hook 植入后已经具备生命周期扩展的雏形。

但它还不适合被原样抽成公共 SDK。现在更准确地说是：

```text
Electron Main 内的一套 Runtime 实现，已经有 SDK 化雏形；
但 Runtime Core、Node 能力实现、Desktop 宿主适配、未来 TUI 适配还没有在代码结构上彻底分层。
```

因此，在真正 SDK 化之前，需要先做一次 **Runtime 边界重整**：把可复用、可版本化、无宿主依赖的 Runtime Core 抽出来，把 Shell/File/Hook 子进程等 Node 能力放入 Runtime Node，把 Electron IPC、Renderer permission gate、窗口事件、桌面路径解析留在 Desktop Adapter，把未来 TUI 也设计成 Adapter，而不是新的 Runtime 分叉。

---

## 1. 背景：为什么 Hook 之后必须先梳理 Runtime 边界

三阶段路线已经确定：

```text
阶段一：Hook 植入
阶段二：Runtime 抽成公共 SDK
阶段三：基于 SDK 构建独立 TUI
```

阶段一完成后，Runtime 主链开始包含更多治理能力：Hook 决策、Permission 合流、Evidence 记录、UI 确认、工具结果归一。此时如果直接把 `apps/desktop/electron/main` 里的模块搬进 `packages/runtime`，很容易把 Desktop Main 的实现细节也固化成 SDK 公共 API，例如：

- Electron `webContents` / IPC / window event。
- Renderer permission gate 的交互协议。
- Desktop `userDataPath`、`workspaceRoot`、会话状态。
- Node `child_process`、文件系统、shell artifact 的具体实现。
- 当前 `.mjs` 文件里的隐式对象约定。

这会导致未来 TUI 不是复用 SDK，而是被迫兼容 Desktop Runtime 的内部形状。

本文件的目标是定义 SDK 化前的架构边界，避免“抽包”变成“搬目录”。

---

## 2. 当前代码分布

当前代码仓中，Runtime 相关逻辑主要分布在以下区域。

### 2.1 `apps/desktop/electron/main/chat-runtime`

职责偏上层编排和会话运行：

- Agent loop / provider streaming。
- tool call 编排。
- projected tool executor。
- permission gate 与用户确认。
- tool card / event 状态转译。
- compaction / session / dispatcher 等桌面运行时逻辑。

关键模块：

```text
apps/desktop/electron/main/chat-runtime/tool-orchestrator.mjs
apps/desktop/electron/main/chat-runtime/projected-tool-executor.mjs
apps/desktop/electron/main/chat-runtime/permission-gate.mjs
```

这层已经承担了 Runtime 编排职责，但同时也靠近 Desktop 会话、UI 事件和 provider streaming，不应整体进入 Runtime Core。

### 2.2 `apps/desktop/electron/main/runtime-gateway`

职责偏本地能力网关：

- Local Tool Host。
- Capability Provider Registry。
- Shell/File/Search/MCP/Browser/Goal/Interaction 等 provider。
- Shell permission review。
- Hook runner/config/evidence。
- Tool result factory。

关键模块：

```text
apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs
apps/desktop/electron/main/runtime-gateway/capability-provider-registry.mjs
apps/desktop/electron/main/runtime-gateway/local-shell-provider.mjs
apps/desktop/electron/main/runtime-gateway/permission-review.mjs
apps/desktop/electron/main/runtime-gateway/hook-runner.mjs
apps/desktop/electron/main/runtime-gateway/hook-config.mjs
apps/desktop/electron/main/runtime-gateway/hook-evidence.mjs
apps/desktop/electron/main/runtime-gateway/tool-result-factory.mjs
```

这层是 SDK 化最重要的候选来源，但内部同时混有三类不同性质的代码：

1. 可进入 Runtime Core 的协议与 pipeline 概念。
2. 只适合 Runtime Node 的本地能力实现。
3. 只适合 Desktop Adapter 的宿主路径、UI 确认、会话上下文接入。

### 2.3 `apps/desktop/electron/main/tools`

职责偏工具定义、投影和 provider-family materializer：

```text
apps/desktop/electron/main/tools/index.mjs
apps/desktop/electron/main/tools/tool-registry.mjs
apps/desktop/electron/main/tools/runtime-projection-tool-materializer.mjs
apps/desktop/electron/main/tools/provider-tool-materializer.mjs
```

这层已经有 Runtime Projection 的概念，但目前仍放在 Desktop Main 下。SDK 化后，Projection contract、mode scope、provider-family materializer 应拆到 Runtime Core 或 runtime projection 包中。

### 2.4 `packages/protocol`

已有跨端协议类型，包括 chat、execution、system-context、goal、memory 等。

它是 SDK 化的良好基础，但当前不等于 Runtime SDK：

- 它偏协议类型集合，不是执行内核。
- Runtime pipeline、Capability Provider、Hook、Permission Policy、Evidence Sink 等接口还没有形成独立公共包。
- 部分类型面向 UI / chat card，不应全部进入 Runtime Core。

### 2.5 `packages/chat-kernel` / `packages/task-thread`

这些包已经体现“纯状态/纯逻辑可复用”的方向，但不是本次 Runtime SDK 的主承载：

- `chat-kernel` 更偏 renderer/chat state reducer。
- `task-thread` 更偏任务线程数据结构。

Runtime SDK 应当借鉴它们的分层方式，而不是把 Runtime 逻辑塞进这些包。

---

## 3. 当前 Runtime 主链

当前主链可以抽象为：

```text
Tool Registry
  ↓
Runtime Projection
  ↓
Provider-family Tool Materializer
  ↓
Model Tool Call
  ↓
Tool Orchestrator
  ↓
Projected Tool Executor
  ↓
Local Tool Host
  ↓
PreToolUse Hook
  ↓
Capability Provider Registry
  ↓
Capability Provider
  ↓
Provider-specific Permission / Execution
  ↓
PermissionGrant
  ↓
PostToolUse Hook
  ↓
Evidence
  ↓
Tool Result
  ↓
Chat Runtime / Renderer / Future TUI
```

更具体地看：

### 3.1 Projection 阶段

`runtime-projection-tool-materializer.mjs` 根据 Tool Registry 创建 Runtime Projection，并为 OpenAI / Anthropic 等 provider family 生成 tool schema。

这一步决定：

- 模型能看到哪些工具。
- 工具在不同 mode 下是否可见。
- model-facing tool name 如何映射回 executor capability。

SDK 化时，这层应成为公共 Runtime Projection 能力，而不是 Desktop 专属工具定义。

### 3.2 Orchestration 阶段

`tool-orchestrator.mjs` 接收模型工具调用，负责调度、状态事件和执行闭环。

这一步目前混有：

- Runtime 应有的 tool call 编排。
- Chat session / streaming 状态。
- Desktop UI tool card 事件。

SDK 化时应拆为：

```text
Runtime ToolCall Orchestrator  // 环境无关
Desktop Tool Event Adapter     // 桌面 UI 投影
TUI Tool Event Adapter         // 终端 UI 投影
```

### 3.3 Execution 阶段

`projected-tool-executor.mjs` 将 model tool call 映射成 runtime capability request，并调用 Local Tool Host。

这里是 SDK 化的重要接缝：它不应该直接绑定 Desktop Main，而应调用一个稳定的 `RuntimePipeline.execute()` 或 `RuntimeHost.executeToolCall()`。

### 3.4 Host / Provider 阶段

`local-tool-host.mjs` 当前做了多件事：

- 组装默认 provider。
- 创建 Capability Provider Registry。
- 创建 Hook Runner。
- 执行 Host 层 PreToolUse。
- 根据 Hook ask/deny 处理阻断或确认。
- 调用 provider。
- 执行 PostToolUse。
- 附加 Hook Evidence。

这说明 Local Tool Host 已经成为事实上的 Runtime Pipeline，但名字和代码位置仍偏 Desktop / local implementation。

SDK 化后建议拆成：

```text
RuntimePipeline          // Core：pipeline 阶段与合流规则
CapabilityRegistry       // Core：provider 注册与查找
NodeProviderBundle       // Node：shell/file/search/mcp 等默认 provider
DesktopRuntimeAdapter    // Desktop：接入 permission UI、event bus、session context
```

### 3.5 Permission 阶段

当前 Permission 有三层：

```text
Shell PermissionReview       // shell-specific policy/rule merge
Chat Permission Gate         // Desktop human approval UI
PermissionGrant              // 工具执行返回的授权证据
```

问题在于三者尚未被统一抽象为公共 `PermissionGateway` / `PermissionPolicy` / `PermissionGrant` contract。Shell 的 `PermissionReview` 已经有最严合流和规则判断，但它是 Shell-specific；通用能力仍需要统一权限接口。

### 3.6 Hook 阶段

Hook 当前已经有：

- 外部命令 runner。
- PreToolUse / PostToolUse。
- matcher。
- timeout / failure strategy。
- most-restrictive decision。
- Evidence 附加。
- global/workspace config。

这符合社区标准方向，但 SDK 化需要拆分：

```text
Hook Contract / HookPipeline       // Core
ExternalCommandHookRunner          // Runtime Node
DesktopHookConfigResolver          // Desktop Adapter / Node helper
Future InProcessPluginHookRunner   // 后续受信插件
```

### 3.7 Evidence 阶段

当前 Evidence 通过 tool result 和 hook evidence helper 附加，已经有“执行必须可审计”的方向。

但 SDK 化后应显式建模：

```text
EvidenceRecord
EvidenceSink
EvidenceCollector
EvidenceRedactor
EvidenceRef
```

否则 Evidence 会继续散落在各 provider result 里，难以被 TUI、Desktop、测试和未来远程 runtime 统一消费。

---

## 4. 当前架构评估

| 维度 | 当前状态 | 判断 |
| --- | --- | --- |
| 优雅性 | 主链概念清晰，但 Local Tool Host 承担了过多职责 | 中等偏好 |
| 可拓展性 | Capability Provider Registry 和 Hook Runner 已经具备扩展点 | 好，但缺少版本化公共接口 |
| 语义清晰 | Projection、PermissionGrant、Evidence、Hook 等核心语义已经存在 | 好，但命名和目录还偏实现层 |
| 职责清晰 | provider、projection、permission、hook 各有文件 | 中等，Core/Node/Desktop 尚未拆开 |
| 模块解耦 | renderer 不能直接执行本地能力，主链有治理 | 好，但 Runtime 仍耦合 Electron Main 宿主 |
| 插件化机制 | Capability Provider + Hook 是插件化雏形 | 方向正确，但插件类型、加载边界、生命周期还未统一 |
| SDK 就绪度 | 可作为 SDK 化输入 | 不能原样抽包，需要先边界重整 |

结论：

```text
当前架构的“治理主链”是科学的；
当前代码分布的“SDK 边界”还不够科学。
```

---

## 5. SDK 化前的边界问题

### 5.1 Runtime Core 与 Electron Main 目录混在一起

当前 Runtime 相关核心逻辑主要在：

```text
apps/desktop/electron/main/chat-runtime
apps/desktop/electron/main/runtime-gateway
apps/desktop/electron/main/tools
```

这让代码天然带有 Desktop Main 语义。未来 TUI 如果复用这些模块，会引入不必要的 Electron 心智模型。

### 5.2 Pipeline 阶段没有独立命名

当前事实 pipeline 是 `local-tool-host.execute()`，但它同时包含：

- provider registry。
- hook。
- permission request callback。
- provider execution。
- evidence append。
- result normalization。

SDK 化前应把它命名为独立概念，例如：

```text
RuntimePipeline.executeToolCall()
```

否则 Local Tool Host 会继续膨胀。

### 5.3 Permission 是 Shell-first，而不是 Runtime-first

当前 `permission-review.mjs` 对 Shell 做得比较清楚，但 Runtime SDK 需要的是：

```text
PermissionPolicy       // 机器策略
HumanApprovalPort      // 人类确认
PermissionDecision     // allow/ask/deny
PermissionGrant        // 执行后授权证明
```

Shell classification 应是某个 provider 的输入，而不是 Permission 系统本身。

### 5.4 Evidence 没有统一 Sink

Hook Evidence 已经附加到 result，但 Evidence 还不是 Runtime pipeline 的正式阶段。

SDK 化后需要强制：

```text
每次工具调用必须产生 ExecutionEvidence 或明确 no-op evidence；
每次 Hook / Permission 决策必须能被 EvidenceSink 记录；
UI 只能展示 Evidence，不能成为 Evidence 的事实源。
```

### 5.5 Hook 配置解析与 Hook Contract 混在一起

`hook-runner.mjs` 更像 Runtime Node 能力，`hook-config.mjs` 读取 global/workspace 配置则接近宿主/环境适配。

SDK Core 只应定义：

```text
HookEvent
HookInput
HookDecision
HookRecord
HookRunner interface
HookPipeline merge rule
```

配置文件位置、子进程执行、环境变量、cwd 解析应留给 Runtime Node / Adapter。

### 5.6 Projection Materializer 位置偏 Desktop

Projection 决定模型看见哪些工具，是 Runtime contract 的一部分，不应长期放在 Desktop Main 的 `tools` 目录下。

需要从“桌面工具定义”升级为：

```text
RuntimeToolDefinition
RuntimeProjection
ProjectionMaterializer
ProviderFamilyToolSchema
```

### 5.7 Capability Provider Contract 是隐式 JS 约定

当前 provider 只要满足 `providerId`、`capabilityIds` / `capabilityPrefix`、`executeCapability()` 即可注册。

这对当前迭代足够轻量，但作为 SDK 需要版本化、类型化、可测试：

```text
interface CapabilityProvider<TInput, TOutput> {
  id: string;
  manifest: CapabilityManifest;
  canHandle(capabilityId): boolean;
  prepare?(request, context): PreparedCapabilityCall;
  execute(request, context): Promise<CapabilityResult>;
}
```

### 5.8 Desktop UI Event 与 Runtime Event 需要分层

Chat Runtime 里的 tool card、permission gate、streaming event 不应成为 SDK 内部事件格式。

应拆成：

```text
RuntimeEvent           // SDK 内核事件
DesktopToolCardEvent   // Desktop UI 投影
TuiRenderEvent         // TUI UI 投影
```

---

## 6. 目标分层

目标结构：

```text
packages/runtime-core
  环境无关 Runtime 内核

packages/runtime-node
  Node.js 本地能力与默认实现

packages/protocol
  跨端、跨进程、跨 UI 的稳定协议类型

apps/desktop
  Desktop Adapter：Electron 宿主、Renderer UI、IPC、窗口与本地用户数据

apps/tui
  TUI Adapter：终端 UI、键盘交互、终端 permission prompt、SDK thin client
```

### 6.1 Runtime Core

`Runtime Core` 是 SDK 最核心的包，必须满足：

```text
不 import electron
不 import child_process
不直接读写 fs
不持有 webContents / BrowserWindow / IPC
不决定 Desktop 或 TUI 怎么展示
不依赖具体 LLM provider transport
```

它应该包含：

- Tool call contract。
- Runtime context contract。
- Runtime pipeline。
- Capability provider contract。
- Capability provider registry。
- Projection contract。
- Hook contract 与 Hook pipeline。
- Permission decision / policy / grant contract。
- Evidence contract / sink contract。
- Result normalization。
- Error taxonomy。
- Contract tests。

建议 API 形态：

```ts
interface RuntimePipeline {
  executeToolCall(call: RuntimeToolCall, context: RuntimeExecutionContext): Promise<RuntimeToolResult>;
}

interface CapabilityProvider {
  readonly providerId: string;
  readonly manifest: CapabilityManifest;
  canHandle(capabilityId: string): boolean;
  execute(request: CapabilityRequest, context: CapabilityExecutionContext): Promise<CapabilityResult>;
}

interface PermissionPolicy {
  decide(request: PermissionRequest, context: PermissionContext): Promise<PermissionDecision>;
}

interface HumanApprovalPort {
  requestApproval(request: HumanApprovalRequest, context: RuntimeExecutionContext): Promise<HumanApprovalDecision>;
}

interface HookRunner {
  run(event: HookEvent, input: HookInput, context: HookContext): Promise<HookRecord[]>;
}

interface EvidenceSink {
  record(record: EvidenceRecord, context: RuntimeExecutionContext): Promise<EvidenceRef>;
}
```

### 6.2 Runtime Node

`Runtime Node` 是 Node 环境下的默认能力实现，不应依赖 Electron。

它应该包含：

- Shell provider。
- File provider。
- Search provider。
- External command Hook runner。
- Node artifact store。
- Node config resolver。
- Node process/signal adapter。
- Node filesystem/path adapter。
- 可选 MCP local client wrapper。

它可以 import：

```text
node:fs
node:path
node:child_process
node:os
```

但不可以 import：

```text
electron
webContents
Renderer store
Desktop window/session 实现
```

### 6.3 Desktop Adapter

`Desktop Adapter` 负责把 Runtime SDK 接入 Electron 桌面产品。

它应该包含：

- Electron IPC。
- `webContents.send()` event bridge。
- Renderer permission gate。
- Desktop session / conversation store。
- app userData path。
- Browser control / visible browser panel。
- Desktop-specific artifact 展示。
- Desktop provider transport 接入。

Desktop Adapter 可以实现 Runtime Core 的 ports：

```text
HumanApprovalPort
RuntimeEventSink
EvidenceViewerAdapter
ConfigScopeResolver
SessionContextProvider
```

它不应重新实现 Runtime pipeline。

### 6.4 TUI Adapter

TUI 是未来独立 CLI/TUI 客户端，不应依赖 Electron Main。

它应该：

- 复用 Runtime Core。
- 复用 Runtime Node 默认 provider。
- 自己实现 terminal permission prompt。
- 自己实现 TUI event renderer。
- 共享 Hook config 语义。
- 共享 Evidence 数据结构。
- 共享 Projection / Tool schema materializer。

它不应该：

- import Desktop Main。
- 复用 Renderer store。
- 假装成 Desktop 的另一个窗口。
- 复制一套工具执行链。

### 6.5 Protocol

`packages/protocol` 应继续作为跨端协议层，但需要和 Runtime Core 明确分工：

```text
protocol：跨进程/跨端数据形状，偏 wire contract
runtime-core：执行内核、合流规则、pipeline、插件接口
```

Runtime Core 可以依赖 protocol 的稳定类型，也可以将部分 runtime-specific 类型迁入 protocol，但不能让 protocol 变成所有实现逻辑的容器。

---

## 7. SDK Core 边界

### 7.1 应进入 Runtime Core 的内容

| 模块 | 是否进入 Core | 说明 |
| --- | --- | --- |
| `CapabilityProviderRegistry` | 是 | 环境无关的 provider 注册与路由 |
| `PermissionDecision` / `PermissionGrant` | 是 | 公共授权语义 |
| `mostRestrictiveDecision` | 是 | Hook/Permission 合流核心规则 |
| Hook event/decision/record contract | 是 | 生命周期公共协议 |
| Hook pipeline merge rule | 是 | hook 只收紧不放宽 |
| Runtime Projection contract | 是 | mode scope、capability exposure、tool schema source |
| Tool result normalization | 是 | SDK 输出稳定化 |
| Evidence contract / redaction contract | 是 | 治理闭环 |
| Runtime error taxonomy | 是 | deny / ask / timeout / cancelled / provider error 等 |
| Runtime event contract | 是 | 与 UI 无关的进度事件 |

### 7.2 不应进入 Runtime Core 的内容

| 内容 | 应放位置 | 原因 |
| --- | --- | --- |
| Electron `webContents` | Desktop Adapter | UI/event bridge 细节 |
| Renderer permission gate | Desktop Adapter | 交互实现 |
| `app.getPath('userData')` | Desktop Adapter | 桌面路径策略 |
| Shell 子进程执行 | Runtime Node | Node 能力实现 |
| File system read/write | Runtime Node | 环境能力实现 |
| External command hook spawn | Runtime Node | 依赖 child_process |
| Browser panel control | Desktop Adapter | Electron/可视浏览器能力 |
| Provider streaming UI card | Desktop/TUI Adapter | 展示层投影 |
| Workspace root 自动发现 | Adapter / Node helper | 宿主策略 |

---

## 8. 插件化扩展模型

插件化不能只有一个笼统的 `plugin` 概念，应拆成四类一等扩展点。

### 8.1 Capability Provider 插件

用途：新增可执行能力。

示例：

- shell。
- file。
- search。
- browser。
- MCP server tools。
- DingTalk/O2 等企业能力。
- future remote tool provider。

公共 contract：

```ts
interface CapabilityProviderPlugin {
  readonly pluginId: string;
  readonly capabilities: CapabilityManifest[];
  register(registry: CapabilityRegistry): void;
}
```

设计要求：

- Provider 必须声明 capability manifest。
- Provider 不直接和 UI 交互。
- Provider 如需授权，返回或发起标准 PermissionRequest。
- Provider 执行结果必须可归一为 RuntimeToolResult。
- Provider 必须能产出 Evidence 或 EvidenceRef。

### 8.2 Lifecycle Hook 插件

用途：在生命周期点执行用户配置逻辑。

一期已落地：

```text
PreToolUse
PostToolUse
```

未来可扩展：

```text
UserPromptSubmit
SessionStart
Stop
SubagentStop
PreCompact
```

公共 contract：

```ts
type HookDecision = 'allow' | 'ask' | 'deny';

interface HookRecord {
  event: HookEventName;
  hookId: string;
  decision: HookDecision;
  reason?: string;
  startedAt: string;
  completedAt: string;
  exitCode?: number;
  timedOut?: boolean;
}
```

规则：

```text
deny > ask > allow
hook allow 不能覆盖系统 deny
hook 崩溃不能破坏主链
高风险写入继续 fail-closed
PostToolUse 不允许改写工具结果，只能审计/补充 Evidence
```

### 8.3 Permission Policy 插件

用途：对工具调用做 allow/ask/deny 决策。

可能来源：

- Shell risk classifier。
- 用户记忆规则。
- workspace policy。
- enterprise policy。
- mode policy。
- hook pre decision。
- human approval result。

公共合流：

```text
system hard deny
  > enterprise/workspace deny
  > hook deny
  > provider risk deny
  > ask
  > allow
```

设计要求：

- Policy 只能返回 decision，不能直接执行工具。
- Human approval 是一个 port，不是 Core UI。
- PermissionGrant 是执行证据的一部分。
- 所有 ask/deny/allow 来源都要进入 Evidence。

### 8.4 Projection Materializer 插件

用途：把 Runtime capability 投影成不同 provider family 的 tool schema。

示例：

- OpenAI tools。
- Anthropic tools。
- MCP tool schema。
- future local TUI command schema。

公共 contract：

```ts
interface ProjectionMaterializer {
  readonly providerFamily: string;
  materialize(projection: RuntimeProjection): ProviderToolSchema[];
}
```

规则：

- Projection 是 capability 的对外可见面。
- Materializer 不能绕过 mode scope。
- Materializer 不决定工具真实执行，只生成模型可见 schema。
- Projection 输出必须可追溯到 executor capabilityId。

### 8.5 Evidence Sink 插件

Evidence 不一定是“插件”，但应允许替换 Sink：

- Desktop local artifact store。
- TUI local log store。
- Test in-memory sink。
- Future remote audit sink。

公共 contract：

```ts
interface EvidenceSink {
  record(record: EvidenceRecord): Promise<EvidenceRef>;
}
```

规则：

- Evidence 是治理事实源。
- UI 只展示 Evidence，不制造 Evidence。
- Sensitive output 必须经过 redaction。

---

## 9. 目标目录建议

建议最终演进为：

```text
peer_agent/
├── packages/
│   ├── protocol/
│   ├── runtime-core/
│   │   ├── src/contracts/
│   │   ├── src/pipeline/
│   │   ├── src/capabilities/
│   │   ├── src/projection/
│   │   ├── src/hooks/
│   │   ├── src/permission/
│   │   ├── src/evidence/
│   │   └── src/events/
│   ├── runtime-node/
│   │   ├── src/providers/shell/
│   │   ├── src/providers/file/
│   │   ├── src/providers/search/
│   │   ├── src/hooks/external-command/
│   │   ├── src/config/
│   │   └── src/artifacts/
│   ├── chat-kernel/
│   ├── task-thread/
│   ├── i18n/
│   └── ui/
├── apps/
│   ├── desktop/
│   │   ├── electron/main/runtime-adapter/
│   │   └── renderer/
│   └── tui/
└── docs/
```

短期不一定一次性创建所有包，但目录方向要稳定。

---

## 10. 推荐抽象：RuntimePipeline

SDK 化的核心不是“导出一堆工具函数”，而是形成一个稳定 pipeline：

```text
RuntimePipeline.executeToolCall(call, context)
  1. validate projection
  2. normalize tool call
  3. run PreToolUse hooks
  4. evaluate permission policies
  5. request human approval if needed
  6. create PermissionGrant
  7. execute capability provider
  8. normalize result
  9. run PostToolUse hooks
  10. record Evidence
  11. emit RuntimeEvents
  12. return RuntimeToolResult
```

这条 pipeline 应成为 Desktop 和 TUI 的共同入口。

### 10.1 RuntimeContext

Core 里的 context 只应包含抽象信息：

```ts
interface RuntimeExecutionContext {
  runId: string;
  sessionId?: string;
  workspace?: WorkspaceRef;
  mode?: RuntimeMode;
  signal?: AbortSignal;
  permissions: PermissionGateway;
  hooks: HookPipeline;
  evidence: EvidenceSink;
  events?: RuntimeEventSink;
  logger?: RuntimeLogger;
}
```

不应出现：

```text
webContents
BrowserWindow
Electron app
Renderer store
具体 userDataPath
```

### 10.2 RuntimeToolResult

工具结果需要统一：

```ts
interface RuntimeToolResult {
  status: 'completed' | 'failed' | 'denied' | 'waiting_user' | 'timeout' | 'cancelled';
  output?: unknown;
  outputPreview?: unknown;
  permissionGrant?: PermissionGrant;
  evidence?: EvidenceBundle;
  error?: RuntimeToolError;
}
```

---

## 11. 迁移顺序

迁移必须小步、可回滚、行为不变优先。

### Step 0：冻结当前行为基线

目标：确保后续移动代码不改变行为。

动作：

- 保留现有 runtime-gateway 测试。
- 补齐 Host/Hook/Permission/Evidence 的 contract tests。
- 记录当前 hook + shell permission + evidence 的关键路径。

验收：

- 现有测试通过。
- Hook deny/ask/allow、Shell L5 deny、PostToolUse evidence 都有测试覆盖。

### Step 1：创建 `packages/runtime-core` 但不迁移实现

目标：先立公共 contract。

迁移内容：

- `RuntimeToolCall`。
- `RuntimeToolResult`。
- `CapabilityProvider`。
- `PermissionDecision`。
- `PermissionGrant`。
- `HookEvent` / `HookRecord`。
- `EvidenceRecord` / `EvidenceSink`。
- `RuntimeEvent`。

验收：

- 包不依赖 Electron / Node-only API。
- 可以被 Desktop Main 和测试共同 import。

### Step 2：迁移 Capability Registry

目标：把最纯的 registry 先移入 Core。

候选：

```text
apps/desktop/electron/main/runtime-gateway/capability-provider-registry.mjs
→ packages/runtime-core/src/capabilities/capability-provider-registry.ts
```

验收：

- Desktop 通过 SDK import registry。
- provider contract 类型化。
- 现有 provider 注册行为不变。

### Step 3：迁移 Hook contract 与合流规则

目标：把 Hook 的公共语义放入 Core，Node 执行留在 Runtime Node。

迁移：

```text
mostRestrictiveDecision
HookDecision
HookRecord
HookPipeline
```

保留在 Runtime Node：

```text
ExternalCommandHookRunner
spawn command
timeout process control
```

验收：

- Hook decision merge 在 Core 测试。
- External command runner 不进入 Core。

### Step 4：抽 Permission Gateway

目标：统一 Shell-specific 与 generic permission。

拆分：

```text
PermissionPolicy / PermissionDecision / PermissionGrant  → Core
Shell risk classifier / shell rule store                 → Runtime Node
Desktop permission gate                                  → Desktop Adapter
TUI permission prompt                                    → TUI Adapter
```

验收：

- Shell L5 destructive 仍 hard deny。
- Hook allow 不能放宽 Shell deny。
- ask 能走 Desktop Adapter 的 approval port。

### Step 5：抽 Evidence contract

目标：Evidence 成为 pipeline 正式阶段。

迁移：

```text
EvidenceRecord
EvidenceBundle
EvidenceSink
EvidenceRedactor
```

保留：

- Desktop artifact storage in Desktop/Node adapter。
- TUI log rendering in TUI Adapter。

验收：

- 每次工具执行至少有一条 runtime execution evidence。
- Hook/Permission 决策可回放。

### Step 6：抽 Runtime Projection

目标：把 model-visible tools 与 executor capability 的映射移出 Desktop Main。

迁移：

```text
RuntimeProjection
RuntimeToolDefinition
ProjectionMaterializer
Mode-scoped availability
```

验收：

- OpenAI / Anthropic materializer 共享同一 projection input。
- Desktop 不再拥有唯一工具定义事实源。

### Step 7：引入 `RuntimePipeline`

目标：替代事实上的 `local-tool-host.execute()`。

动作：

- 在 Core 创建 pipeline。
- Desktop Local Tool Host 改为组装 pipeline 的 adapter。
- Provider 执行由 pipeline 调用 registry。

验收：

- Desktop 行为不变。
- TUI 可以用同一 pipeline + node provider bundle 执行最小工具。

### Step 8：拆 Runtime Node provider bundle

目标：把 shell/file/search 等 Node 能力从 Desktop Main 移出。

迁移：

```text
local-shell-provider
local-file-provider
local-search-provider
hook external command runner
artifact store
```

验收：

- `packages/runtime-node` 不依赖 Electron。
- Desktop 和 TUI 均可按需注册 provider bundle。

### Step 9：Desktop Adapter 收口

目标：Desktop 只做宿主，不再是 Runtime 本体。

动作：

- Electron IPC / Renderer permission gate 留在 Desktop。
- Desktop adapter 实现 `HumanApprovalPort`、`RuntimeEventSink`、`SessionContextProvider`。
- Desktop 通过 SDK public API 执行工具。

验收：

- Desktop Main 中不再有可复用 Runtime Core 逻辑的唯一实现。
- Renderer 仍不能直接执行本地能力。

### Step 10：TUI 最小接入

目标：证明 SDK 边界成立。

动作：

- 创建 `apps/tui`。
- import `runtime-core` + `runtime-node`。
- 实现 terminal approval prompt。
- 渲染 RuntimeEvent。
- 执行最小 shell/read-only 工具。

验收：

- TUI 不 import Desktop。
- 同一 Hook config 语义可复用。
- 同一 Evidence contract 可复用。

---

## 12. 验收标准

SDK 边界梳理成功后，应满足：

1. `Runtime Core` 不依赖 Electron / Node-only API / UI。
2. `Runtime Node` 不依赖 Electron / Renderer。
3. `Desktop Adapter` 不拥有 Runtime pipeline 的唯一实现。
4. `TUI Adapter` 可以不依赖 Desktop 复用 Runtime。
5. Capability Provider、Hook、Permission Policy、Projection Materializer 四类扩展点都有明确 contract。
6. Permission 合流遵守 `deny > ask > allow`。
7. Hook 只能收紧，不能放宽系统/权限策略。
8. High-risk destructive write 继续 hard deny。
9. 每次工具执行都有 PermissionGrant / Evidence 或明确失败 evidence。
10. OpenAI / Anthropic / future TUI tool schema 都来自同一 Runtime Projection。

---

## 13. 禁止事项

SDK 化过程中禁止：

- 把 `apps/desktop/electron/main/runtime-gateway` 整目录原样搬成 SDK。
- 在 Runtime Core 中 import Electron。
- 在 Runtime Core 中 spawn 子进程。
- 在 Runtime Core 中读取 `userDataPath` / workspace config 文件。
- 让 TUI 复用 Desktop Renderer store。
- 让 Hook allow 覆盖 Permission deny。
- 让 UI 成为 PermissionGrant / Evidence 的事实源。
- 为 TUI 再写一条平行工具执行链。
- 为每个 provider family 维护一套独立工具事实源。

---

## 14. 对“是否足够科学”的最终判断

回答用户最初的问题：

> 现在整体的架构设计和代码分布足够科学吗？有没有符合优雅、可拓展、语义清晰、职责清晰、模块解耦、插件化机制方向去设计？

判断如下：

```text
架构思想：基本科学。
执行主链：已经正确。
Hook / Permission / Evidence 方向：正确。
插件化雏形：已经出现。
代码分布：还不够 SDK 化。
职责边界：需要在 Core / Node / Desktop / TUI 上重新切分。
```

所以，下一步不应立即“大抽包”，而应执行一轮 SDK Boundary Refactor：

```text
先立 Runtime Core contract，
再迁移纯逻辑，
再迁移 Node 能力，
最后让 Desktop 和 TUI 都成为 adapter。
```

只要按这个顺序推进，Peer Agent 的 Runtime SDK 就不会变成 Desktop Runtime 的重命名包，而会成为真正可复用、可扩展、语义清晰、职责清晰的公共运行时内核。
