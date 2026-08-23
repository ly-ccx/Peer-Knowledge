# Peer Agent 架构治理与开发准则

日期：2026-06-10
状态：治理基线
产品理念：`design/product/peer-product-alignment.md`（本文不另立品类，只锁工程如何实现那条委托链路）

本文把 Peer Agent 的设计理念落成后续代码开发必须遵守的治理准则。它不是一次性技术方案，而是所有新功能、重构、修复和实验体同步时的架构判断标准。

核心判断：

```text
模型负责认知。
本地负责能力。
界面负责表达。
契约负责边界。
证据负责治理。
```

这里的「模型」是**角色**而非**部署位置**：认知可以来自云端 provider，也可以来自未来的本地推理 runtime。无论模型在哪里，能力执行、授权与 Evidence 始终留在本地。

Peer Agent 可以学习 Claude Code、Codex、OpenCode 的实现经验，但不能退化成普通 Electron 聊天壳、无治理的工具拼装、企业工单台，或靠 prompt 兜底的自动化脚本集合。

## 一、治理目标

架构治理要解决四件事：

1. 防止能力旁路：任何本地能力都必须进入统一主链路。
2. 防止认知与能力混层：桌面不替代模型做规划，也不把授权 / Evidence 交给模型口头完成。
3. 防止 UI 变成事实源：权限、执行、Evidence、协议状态不能只存在 renderer state。
4. 防止模块浅化：新增代码必须提升 Locality 和 Leverage，而不是把复杂度摊到更多文件。

治理不是为了让代码更“抽象”，而是为了让每次变更都能回答：

```text
谁负责认知？
谁负责执行？
谁负责授权？
谁负责事实？
谁负责展示？
出错后在哪里定位？
```

## 二、不可破坏的主链路

所有本地能力，包括 Bash、文件读写、MCP、Plugin、Skill、本地 App 自动化和未来多模态文件处理，都必须经过：

```text
Capability Provider
  -> Manifest
    -> Runtime Projection
      -> Tool Call
        -> PermissionGrant
          -> Evidence
```

禁止为某一种能力新增独立旁路，例如：

- Plugin 直接执行本地文件写入。
- MCP server 绕过 Runtime Projection 暴露工具。
- Skill 自己持有权限判断。
- Renderer 直接读写文件或启动进程。
- Prompt summary 代替 Tool Result 或 Evidence。
- UI state 代替 PermissionGrant。

如果某个功能看起来很小，也必须先判断它属于主链路中的哪一层。找不到归属时，不应该先实现，而应该先补充设计。

## 三、层级职责

| 层 | 职责 | 禁止 |
|---|---|---|
| Cloud Agent Runtime | 认知、规划、工具选择、组织策略、执行账本 | 直接访问本地端口、假装拥有本机能力 |
| Runtime Projection | 本次会话可见能力裁剪 | 暴露未授权、未注册、未声明能力 |
| Local Tool Host | 本地工具调用统一入口 | 为 Bash / MCP / Plugin / Skill 各开执行旁路 |
| Capability Provider | 能力声明、执行、脱敏、Evidence 采集 | 成为认知层或权限事实源 |
| PermissionReview | 本地确认、规则、执行时约束 | 把授权只放在 renderer store |
| Protocol | 跨层契约 | 让 app 代码到处拼 ad hoc payload |
| Task Thread | 运行态事件展示 | 把工具结果伪装成普通 assistant 文本 |
| Renderer | 表达、确认、输入、状态投影 | 直接执行高权限能力 |
| System Context | 上下文准入和提示词组装 | 成为能力执行旁路 |

## 四、模块设计准则

后续代码评审使用以下工程语言：

- `Module`：任何有 Interface 和 Implementation 的代码单元。
- `Interface`：调用方必须知道的一切，包括类型、时序、错误、权限、配置和不变量。
- `Implementation`：模块内部实现。
- `Depth`：Interface 小但 Implementation 能力强，才是深模块。
- `Seam`：行为可以被替换或扩展的位置。
- `Adapter`：在 Seam 上接入的具体实现。
- `Leverage`：调用方从深模块获得的能力。
- `Locality`：变更、排错、知识集中在少数位置。

准则：

1. 新增 Module 必须提高 Locality，不能只是把一段代码搬到另一个文件。
2. 新增 Interface 必须有真实 Leverage，不能让调用方仍然理解全部 Implementation。
3. 一个 Seam 只有一个 Adapter 时要谨慎；两个以上 Adapter 才说明 Seam 真实存在。
4. 能用协议对象表达的边界，不允许用散乱 plain object 临时拼装。
5. 能用 Provider / Registry 扩展的能力，不允许在中心服务里继续堆 `if capabilityId === ...`。
6. 能通过 reducer / kernel 表达的运行态，不允许继续塞进大型 React 组件。

删除测试：

```text
如果删除一个 Module 后复杂度只是平均散回多个调用方，它就是有价值的。
如果删除一个 Module 后复杂度直接消失，它多半只是浅包装。
```

## 五、代码分区治理

### 5.1 `packages/protocol`

协议包是第一优先级。

必须：

- 定义跨 main / renderer / cloud / local runtime 的稳定对象。
- 承载 `CapabilityManifest`、`RuntimeProjection`、`ClientToolCall`、`ClientToolResult`、`PermissionGrant`、`Evidence` 等对象。
- 优先通过类型和 schema 收敛边界。

禁止：

- 让 app 层长期使用未登记的 ad hoc payload。
- 把 UI 文案、组件状态或 provider 细节塞进 protocol。

### 5.2 `apps/desktop/electron/main`

Electron main 是桌面组合层和安全 IPC 层，不是本地大脑。

必须：

- 通过 IPC 暴露最小 typed API。
- 把本地能力交给 Local Tool Host / Capability Provider。
- 把 provider streaming、tool execution、permission、compaction、prompt assembly 分成明确 Module。
- 把 provider request lowering、reasoning/thinking wire-format、SSE error parsing 集中在 provider encoder / adapter seam。

禁止：

- 在单个 chat service 中继续堆所有 provider、tool、permission、prompt、compaction 逻辑。
- 在 main IPC handler 中临时拼协议对象。
- 绕过 runtime-gateway 直接执行未来可被云端调用的能力。
- 在 chat service、renderer 或 prompt source 里硬编码 provider wire-format。

### 5.3 `apps/desktop/renderer`

Renderer 是运行态表达层。

必须：

- 使用 preload typed API。
- 把工具调用、权限、Evidence、artifact 渲染为结构化事件。
- 把复杂状态放进 kernel / reducer / hook，而不是堆在单个组件里。

禁止：

- 直接 `fs`、`child_process`、MCP lifecycle、密钥存储。
- 把 `[Tool call]`、`[Tool result]` 这类文本当作真实工具事件。
- 让 assistant 文本伪装成已执行工具结果。
- 让 UI 本地状态成为最终权限事实。

### 5.4 `packages/chat-kernel` 与 `packages/task-thread`

这两个包承载任务线程运行态，而不是纯 UI 工具包。

必须：

- 把 message、stream、thinking、tool、review、evidence、artifact 状态归一化。
- 对关键 reducer、event lowering、historical migration 写测试。
- 让 renderer 只消费明确状态，不直接理解所有 provider 细节。

禁止：

- 把 provider SDK 或 Electron IPC 细节下沉进 kernel。
- 让任务线程事件绕过协议类型。

### 5.5 `System Context` / Prompt

系统提示词不是一个字符串，而是 Runtime 组装出的系统上下文。

必须：

- 通过 Context Source / Prompt Assembly 组装。
- 记录来源、顺序、版本和调试快照。
- 把 AGENTS / project instructions / tool prompt / compaction summary 作为可治理来源。

禁止：

- 在多个文件重复拼 system prompt。
- 让 project instructions 覆盖内置安全边界。
- 用 prompt 代替 executor 中的权限和能力约束。

### 5.6 Attachment / Multimodal Context

附件和多模态输入属于上下文准入问题，不是普通 UI 状态。

必须：

- 明确区分图片、文本文件、暂不支持文件和未来二进制 artifact。
- 使用 `ContextAttachmentItem` 记录来源、scope、lifecycle、文件名、MIME、大小、transport 和是否内联内容。
- 图片进入 provider 前必须经过 provider-specific lowering。
- 文本文件内联必须有大小限制，并被标记为用户提供的附件内容。
- 未来可执行文件、目录、压缩包、大文件必须走 artifact / Evidence 引用，而不是直接塞进 prompt。
- 运行态提醒必须使用 `RuntimeReminderItem` / `runtime-reminder-source.mjs` 进入 System Context；不要把提醒伪装成普通 user/tool text。

禁止：

- 把附件内容提升为 system instruction。
- 让 renderer 直接读取高权限本地路径；只能处理用户显式选择或粘贴的 File 对象。
- 让 unsupported file 静默丢失；必须在 UI 和模型上下文里说明未包含内容。
- 把 textual `<system-reminder>` 当作主要架构边界；它只能作为 provider 兼容或 legacy envelope，不能替代协议对象。

### 5.7 System Context / Tool Runtime 联动

System Context 只描述模型能看到什么，Tool Runtime 决定系统能执行什么。

必须同时满足：

- Prompt 里说工具如何使用。
- Tool schema 限制模型可提交的参数形状。
- Executor 强制执行 read-before-edit、路径、权限、超时、取消和输出脱敏。
- Renderer 只展示结构化 Tool Call / Tool Result / Permission / Evidence。
- Provider Adapter 必须把 provider SSE error / stream error 转成结构化 provider error，不允许被空内容 guard 误判为 `empty_model_response`。
- Provider Encoder 必须区分 provider capability 与 provider wire-format；例如 Anthropic official `thinking.type=enabled` 和 idealab Anthropic gateway `thinking.type=adaptive + output_config.effort` 不能共用同一硬编码形态。

任何只改 prompt、不改 executor 的安全约束都不算完成。

## 六、变更分级

### A 级：必须先有设计文档或 ADR

满足任一条件即为 A 级：

- 改变主链路对象或跨层契约。
- 新增一种 Capability Provider。
- 新增工具执行权限模型。
- 新增云端可见本地能力。
- 改变 Evidence 采集、脱敏或回传语义。
- 改变 System Context assembly 顺序。
- 改变数据存储目录、密钥存储、权限规则持久化。

### B 级：必须说明架构影响

满足任一条件即为 B 级：

- 拆分或合并 main / renderer 里的核心 Module。
- 修改 Chat Runtime、Tool Runtime、Compaction、Prompt、PermissionReview。
- 修改 task thread event model。
- 新增跨进程 IPC。

### C 级：普通实现

局部 UI、样式、小 bug、文案、测试补充属于 C 级。但如果 C 级改动触碰能力执行、权限、Evidence、协议对象，自动升级为 B 或 A。

## 七、代码评审清单

每次较大变更至少检查：

1. 是否仍然满足“模型负责认知，本地负责能力”？
2. 新能力是否进入 `Capability Provider -> Manifest -> Runtime Projection -> Tool Call -> PermissionGrant -> Evidence`？
3. 是否新增了工具、权限、Evidence 或 prompt 旁路？
4. Renderer 是否只表达和确认，没有直接执行高权限能力？
5. Protocol 是否有稳定对象，还是 app 层到处拼 payload？
6. Module 是否变深，还是只是把复杂度拆散？
7. 错误、取消、超时、拒绝是否都有结构化结果？
8. Evidence 是否可追踪、可脱敏、可回放？
9. 长上下文 summary 是否只做导航，没有替代事实？
10. 新增行为是否有单测、集成测试或可复现实验记录？

## 八、反模式

以下写法默认不接受：

- “先在 UI 里做一个状态，后面再接协议。”
- “这个工具很简单，先绕过 Local Tool Host。”
- “权限先用前端变量记一下。”
- “模型已经被 prompt 约束了，executor 不用再校验。”
- “工具结果直接塞 assistant markdown 里展示。”
- “compact 后原始事实不保留也没关系。”
- “为了快，把 provider streaming、tool execution、permission 都放一个文件。”
- “Plugin / MCP / Skill 各自做一套调用流程。”

如果因为短期实验必须临时违反，必须满足：

1. 文件或 PR 中明确标注临时性。
2. 不进入默认主路径。
3. 有删除计划。
4. 不成为后续功能依赖。

## 九、实验体与本体同步

实验体可以更快验证，但不能形成另一套架构。

同步规则：

- 实验体可以先做 Adapter，不可以改主链路语义。
- 实验体发现的有效模式，合并前必须落到 protocol / runtime-gateway / chat-kernel 等正式 Seam。
- 本体和实验体共享用户数据时，必须尊重相同的权限、Evidence 和存储边界。
- 不允许因为实验体方便而引入路径、权限、工具调用的隐式分叉。

## 十、落地优先级

近期架构治理优先级：

1. 保持 `executeTool()` 兼容入口已删除的状态；model-visible tools 已绑定 Runtime Projection，后续不允许新增 executor 分支。
2. 拆分 Chat Runtime：provider adapter、agent loop、tool orchestrator、stream session、compaction coordinator。
3. 拆分 ChatSurface：conversation state、stream state、permission state、composer attachment、compaction state、presentational UI。
4. 把 main 进程收敛为 composition root + IPC registration modules。
5. 落地 System Context Assembly，消除重复拼 prompt。
6. 让 protocol 成为跨层硬契约，而不是参考类型集合。

## 十一、当前代码治理锚点

以下锚点来自 2026-06-10 的当前代码状态。后续改动必须以它们为迁移起点，而不是重新发明旁路。

| 领域 | 当前代码锚点 | 治理判断 |
|---|---|---|
| Core prompt | `apps/desktop/electron/main/llm-prompts.mjs` 的 `buildSystemPrompt()` + `electron/main/prompt/*` | 入口已收敛到 System Context Assembly；后续新增上下文必须以 Prompt Source 进入 |
| Protocol | `packages/protocol/src/system-context.ts` | chat send context、`ContextAttachmentItem`、`RuntimeReminderItem`、continuity summary、config instructions、context extensions、prompt snapshot、context epoch、context epoch event 已有跨层契约；`chat:send` 必须完整透传协议字段，后续新增跨进程 payload 必须先进入 protocol |
| Tool schema | `electron/main/tools/*`、`buildOpenAITools()`、`buildAnthropicTools()`、`runtime-projection-tool-materializer.mjs` | Tool Registry 边界已落地；provider-visible schema 已由 Runtime Projection materialize；model-visible tools 已通过 projected executor 进入正式 file / shell providers |
| Chat runtime | `apps/desktop/electron/main/llm-chat-service.mjs` + `chat-runtime/*-agent-loop.mjs` + `chat-runtime/agent-loop-kernel.mjs` | service 只保留 provider 选择、System Context assembly、stream 生命周期和 permission gate 组合；provider-specific Agent Loop、provider adapter、shared loop kernel、terminal text transition、projected tool executor、file Capability Provider、shell Capability Provider 委托、tool orchestrator、compaction coordinator、response guard、prompt snapshot 已拆到独立 Module；后续重点是继续把 provider-neutral provider error / retry transition 抽进 kernel |
| Inline LLM tools | `executeModelToolCall()` -> `chat-runtime/projected-tool-executor.mjs` -> `Local Tool Host` -> `runtime-gateway/local-file-provider.mjs` / `runtime-gateway/local-shell-provider.mjs` | file / bash tools 已进入正式 Provider；runtime 模型工具调用已直连 Runtime Projection / Local Tool Host；旧 `executeTool()` 兼容入口已删除 |
| Local Tool Host | `apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs` | 正式能力执行 Seam，已注册 health、file、shell、mcp、skill providers，应成为所有本地能力的统一入口 |
| Provider registry | `runtime-gateway/capability-provider-registry.mjs` | 新能力必须以 Provider Adapter 注册，不在中心 host 堆分支 |
| Compaction | `context-compactor.mjs`、`chat:compact` IPC、`prompt/sources/continuity-source.mjs` | manual compact 已复用 System Context；后续 continuation 通过 `runtime.continuity` 注入，不再把 compaction card 当普通 user history |
| Context Baseline / Epoch | `prompt/prompt-snapshot-store.mjs` 的 `recordBaseline()` / `latest-baselines.json` / `context-epochs.jsonl` / `latest-context-epochs.json` / `context-epoch-events.jsonl` + `prompt/context-baseline-recorder.mjs` | manual compact 成功后记录带 continuity 的 chat baseline，并同步创建 durable Context Epoch replacement chain；`epoch_created` / `epoch_replaced` / `snapshot_anchored` 形成可查询 ledger；default provider/model 变化自动记录 `model_switch` baseline；`settings.systemInstructions` 变化自动记录 `instruction_change` baseline；普通 prompt snapshot 锚定 active `contextEpochId`，同一轮 retry 复用同一 baseline |
| Project instructions | 根 `AGENTS.md` + `prompt/sources/project-instructions-source.mjs` + 模型配置页系统指令 | config、global、workspace root、nested scoped 项目指令已作为 `L3_INSTRUCTIONS` 注入；`settings.systemInstructions` 通过 `chat:send.configInstructions` 进入 System Context |
| Provider prompt selection | `prompt/sources/provider-source.mjs` | provider/model family 级别提示已作为 `runtime.provider` 注入；provider wire-format 仍只属于 provider encoder / adapter；`effort=high` 不能直接开启原生 reasoning/thinking，必须先由 provider config 声明 `supportsReasoning`；Anthropic-compatible provider 的 reasoning wire-format 由 adapter policy 选择，不由 UI mode 或 prompt source 决定 |
| Context extensions | `prompt/sources/context-extension-source.mjs` | Plugin / Skill / MCP 只能通过受限 `contextExtensions` 或注册 Context Source 贡献上下文；不能直接拼接 system prompt 或授予执行权限 |
| Runtime reminders / attachments | `ChatSurface.tsx` 的 FileReader + `prompt/sources/attachment-source.mjs` + `prompt/sources/runtime-reminder-source.mjs` + provider normalization | 附件正文/图片仍属于 user message；系统上下文只接收 metadata；运行态提醒通过 `RuntimeReminderItem` 进入 System Context；不把 payload 或提醒伪装成普通 user/tool text |
| Permission always allow | `chat-runtime/permission-gate.mjs` 的 main-runtime scope grant cache | 会话/工作区/能力签名级“始终允许”已移到 main runtime；后续可升级为 PermissionReview 持久规则 |
| Local access mode | `settings.localAccessLevel` -> `session-store.mjs` -> `llm-chat-service.mjs` -> `chat-runtime/permission-gate.mjs` | Renderer 只表达 Ask / Approve for me / Full access 选择；真实策略在 main runtime 生成 `PermissionGrant`，仍走 Runtime Projection / Tool Call / PermissionGrant / Evidence 链。`session_local` 只自动批准低/中风险 shell；`full_local` 自动批准文件写入和低/中风险 shell，高风险 shell 与既有 deny 规则仍进入 PermissionReview/拒绝路径。 **路径硬沙箱已取消（2026-07-21）**：`path_outside_workspace` / `cwd_outside_workspace` 不再作为 runtime 硬失败；跨工作区绝对路径可进入权限与执行链。详见 `knowledge/decisions/49-cancel-path-hard-sandbox.md`。 |
| Historical tool text | `historicalLocalRecord.ts` | 已防止伪 `[Tool call]` 被当作真实调用，但应逐步收敛到结构化 ThreadEvent |

## 十二、架构更新规则

当代码进入以下区域时，必须同步检查文档：

| 改动区域 | 必查文档 |
|---|---|
| prompt、tool schema、provider request | `19-system-prompt-context-architecture.md` |
| Capability Provider、Runtime Projection、Local Tool Host | `15-plugin-skill-mcp-system.md`、`16-skill-call-lifecycle.md`、本文 |
| compaction、artifact ref、历史消息压缩 | `17-local-context-compaction.md`、`19-system-prompt-context-architecture.md` |
| renderer chat surface、tool card、permission strip | `14-product-design-language.md`、本文 |
| 文件写入、shell、越界权限 | `09-high-risk-write-scope.md`、本文 |

如果文档被 `.gitignore` 或迁移策略隐藏，也不能把架构更新跳过；至少要更新当前可版本化的治理文档。

## 十三、最终判断标准

任何代码变更只要让下面这句话更真实，就是好方向：

```text
模型知道边界，工具服从契约，用户掌握授权，系统留下证据。
```

任何代码变更只要让下面这句话更模糊，就应该停止：

```text
不知道谁决定、谁执行、谁授权、谁证明。
```

## 相关文档

- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — Desktop 与 TUI/CLI 共享运行时边界与长期治理
- `knowledge/decisions/48-cli-first-class-release.md` — CLI 一等发布与 npm 安装面
- `knowledge/specifications/runtime-sdk-boundary-architecture.md` — Runtime SDK 分层边界
- `knowledge/architecture/desktop-cli-local-capability-parity.md` — 本地能力对齐

