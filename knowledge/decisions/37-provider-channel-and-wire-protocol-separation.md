# 37. Provider Channel 与 Wire 协议分离

创建时间：2026-06-18
最后更新：2026-11-15（更新实施状态，对齐 `effort` 全词表与 [ADR 48-provider](48-provider-model-options.md) / ADR 83 模型选项及档位校验）

## Status

Accepted / Shipped incrementally（ChannelRegistry、OpenRouter、OpenAI OAuth Responses 及渠道 `capabilities` 声明已按多轮落地；具体增量收据以对应分支和候选发布记录为准）。

设计决议见 §Review / Revision（2026-06-18）与 §Channel Taxonomy（2026-06-19）。
本设计涉及运行时契约与通道能力暴露，仍遵守 `AGENTS.md` 的 A 级变更治理约束。

2026-08-14 更新：OpenRouter 已作为一等第三方渠道落地（`openrouter` / `openrouter-api`，默认 `https://openrouter.ai/api/v1`，wire=`openai-chat`）。接入约定见 `knowledge/architecture/openrouter-channel.md`。下文 §Context 中「设置界面渠道列表 / 代码中不存在」仍是 2026-06-18 的历史快照，不再代表当前代码。

## Context

### 现状（基于代码证据，2026-06-18）

Peer Agent 目前对「provider」存在两套粒度不一致、且未对齐的概念：

| 层 | 「provider」的含义 | 取值范围 | 证据 |
|---|---|---|---|
| 协议层 `LlmProviderType` | wire 协议族 | `'openai' \| 'anthropic'` | `packages/protocol/src/index.ts:238` |
| 配置默认表 `PROVIDER_DEFAULTS` | 同上 | 仅 `openai` / `anthropic` | `apps/desktop/electron/main/llm-config-store.mjs:52` |
| 前端 `PRESETS` | 同上 | 仅 `openai` / `anthropic` | `apps/desktop/renderer/src/app/components/LlmSettingsPanel.tsx:25` |
| 设置界面渠道列表 | 品牌渠道 | DeepSeek / Azure OpenAI / Groq / Mistral / xAI / OpenRouter / Perplexity / Together / Ollama / Google AI / 阿里巴巴 … | 代码中不存在；为用户手动创建的条目，`name` 为自定义显示名 |

请求分发只有一个二分（`apps/desktop/electron/main/llm-chat-service.mjs:376` 附近）：

```text
provider.provider === 'anthropic'  -> agentLoopAnthropic -> anthropic-messages-adapter
否则（其余全部品牌）                -> agentLoopOpenAI    -> openai-chat / openai-responses adapter
```

即：设置界面里十余个「专业渠道」，后端只有 **2 条真实代码路径**。所有非
Anthropic 渠道被统一当作「OpenAI 兼容」处理。

### 问题

1. **静默降级**：`llm-config-store.mjs:254` 存在 `item.provider = 'openai'`，
   `addProvider` 中存在 `provider || 'openai'`、
   `PROVIDER_DEFAULTS[provider] || PROVIDER_DEFAULTS.openai`。任何未知渠道都被
   静默归一为 openai，掩盖真实差异。

2. **公共路径里按 host 嗅探**：`anthropic-messages-adapter.mjs` 的
   `resolveAnthropicReasoningFormat(baseUrl)` 通过判断 URL 是否含
   `idealab.alibaba-inc.com` 来切换 reasoning 格式。每接入一个新网关就要在公共
   adapter 里再加一个 host 分支。

3. **端点与鉴权硬编码在 wire adapter**：`${baseUrl}/chat/completions`、
   `${baseUrl}/v1/messages`、`x-api-key` 对 `Authorization: Bearer` 均写死在
   adapter 内。

4. **异构协议无处安放**：Azure OpenAI（`api-key` 头 + `api-version` 查询参数 +
   `deployment` 路径）与 Google AI / Gemini（`:generateContent`，非 OpenAI
   wire）在 main 进程中**没有任何适配代码**（对 `api-version|deployment|azure|
   gemini|generateContent` 的检索在 main 进程零命中）。它们在界面中可被选择，但
   大概率无法正常工作。

5. **与架构基线冲突**：`AGENTS.md` 与文档 20 要求
   「Add a Provider adapter instead of adding branches to central hosts」与
   「Provider-specific request formatting belongs behind a provider encoder
   seam」。当前 encoder / wire-adapter 分层方向正确，但缺失「品牌渠道身份」这一
   层，导致渠道差异只能漏进公共路径或被降级。

### 核心认知

「wire 协议」与「品牌渠道」是两个正交维度：多数渠道复用同一种 wire，差异仅在
端点、鉴权、方言（reasoning 字段、prompt cache、vision 等）这层元数据。因此不需
要为每家写一个完整 adapter，而应把渠道差异收敛为**数据驱动的渠道描述**，把协议
差异收敛为**少数几个深 wire adapter**。

## Decision

引入两层分离：**Channel（品牌渠道，数据驱动，N 个）** 与
**Wire 协议（少数深 adapter）**。

```text
ChannelDescriptor（品牌渠道，开放数据：内置 preset + 用户自定义，N 个）
  ├─ id: string（开放标识，非闭合联合类型；preset 用稳定字符串，
  │            用户自定义条目用生成 id）
  ├─ wire: WireProtocol（唯一闭合枚举，见下）
  ├─ endpoint 规则（path 拼法、api-version 等）
  ├─ auth 规则（header 名 / query / Bearer 形态）
  ├─ customHeaders: Record<string,string>（用户可自定义，合并进请求头）
  ├─ capabilities（能力声明，见 §1.2；驱动 UI 与请求构造）
  │     ├─ reasoning: { supported, effortLevels?, paramStyle }
  │     ├─ promptCache / vision / toolUse / temperature ...
  └─ （模型元数据不在此，拆到独立 ModelInfo 来源，见 §1.4）
        │  wire 指向
        ▼
WireAdapter（协议族，深模块，少数几个；唯一需要写代码的扩展点）
  ├─ openai-chat-adapter        （已存在）
  ├─ openai-responses-adapter   （已存在）
  ├─ anthropic-messages-adapter （已存在）
  └─ gemini-adapter             （新增；Azure 作为 openai-chat 的端点/鉴权变体）
```

> 关键区分（对标 Roo Code 的可扩展性）：
> **新增渠道/端口 = 写数据（preset 或用户自定义），零代码**；
> **新增协议族 = 写一个 wire adapter，是面向开发者的、有限的扩展点**。
> 只有 `WireProtocol` 是闭合枚举，`ChannelId` 不是。

### 1. 契约拆分

#### 1.1 维度正交

- `WireProtocol` 是**唯一闭合枚举**：`'openai-chat' | 'openai-responses' |
  'anthropic-messages' | 'gemini'`（由现有 `LlmProviderType` 演进而来）。新增协议
  族才需要扩这个枚举并配套写一个 wire adapter。
- `ChannelId` 是**开放标识（`string`）**，不是闭合联合类型。内置 preset 用稳定
  字符串（如 `'deepseek'`），用户自定义渠道用生成 id。**这是「像 Roo Code 一样可
  扩展不同 API 端口」的关键**：加端口不应改类型、不应改代码。
- Provider 配置持久化 `channelId`、`authMethod`、可选的用户 `wireOverride`（仅当
  descriptor 声明允许用户选择 wire 时存在）、以及用户在该条目上的覆盖项
  （`customHeaders` / reasoning 设置等）。**运行时实际使用的 `wire` 不是存储事实
  源**，而是由 `ChannelRegistry.resolve(config)` 解析得到。

#### 1.1.1 wire 解析事实源

新增 `ChannelRegistry.resolve(providerConfig)` 作为唯一 wire 解析入口，返回
`ResolvedChannel`：

```text
ResolvedChannel {
  channelId,
  authMethod,
  wire,                 // 本次请求实际 wire
  endpoint,
  auth,
  headers,
  capabilities,
  modelInfoRef?,
}
```

解析规则：

- descriptor 声明 `defaultWire`、`allowedWires`、`authMethods` 与必要的
  `authMethod -> wire` 约束。
- 用户配置只保存 `wireOverride`，不把派生 `wire` 当作长期事实。`wireOverride` 必须
  属于 descriptor 的 `allowedWires`，否则保存时报错或迁移时报显式 invalid 状态。
- `oauth_chatgpt` 当前只允许在「OpenAI 官方」channel 上使用，并固定解析为
  `openai-responses`；不得通过用户 override 解析成 `openai-chat`。
- 「OpenAI 兼容」默认解析为 `openai-chat`，用户可在 `allowedWires` 内显式选择
  `openai-responses`。
- 迁移期可以在 view / debug snapshot 中暴露 `resolvedWire` 便于排障，但请求分发只
  使用 `ChannelRegistry.resolve()` 的结果，避免存储里的旧派生字段与 preset 更新产生
  漂移。

#### 1.2 capabilities（能力声明，一等结构）

把「这个渠道支持什么」从隐式 host 嗅探提升为显式数据，UI 与请求构造都读它，避免
对不兼容端口发出非法字段：

```text
capabilities: {
  reasoning: {
    supported: boolean,
    // 思维强度的可配置定义，防止不兼容：不同端口表达方式不同
    paramStyle: 'openai-effort'               // openai-chat: reasoning_effort; responses: reasoning.effort
              | 'anthropic-enabled-budget'    // thinking.type=enabled + thinking.budget_tokens
              | 'anthropic-adaptive-effort'   // thinking.type=adaptive + output_config.effort
              | 'anthropic-output-effort'     // output_config.effort only, no thinking budget
              | 'qwen-enable'                 // enable_thinking + thinking_budget
              | 'none',
    effortLevels?: string[],         // 该端口允许的强度档位（UI 下拉来源）
    defaultEffort?: string,
  },
  promptCache?: boolean,
  vision?: boolean,
  toolUse?: boolean,
  temperature?: boolean,
}
```

- **思维强度**不再在 adapter 里按 host 猜，而由 descriptor 的
  `reasoning.paramStyle` 决定如何编码进请求体；UI 的强度选项由 `effortLevels`
  驱动。若 `supported=false`，UI 隐藏该项且请求不带任何 reasoning 字段。
- `paramStyle` 表达的是**渠道方言**，不是品牌名。`idealab` 这类 Anthropic 兼容网关
  需要的 adaptive 形态必须用 `anthropic-adaptive-effort` 数据声明，禁止继续在
  `anthropic-messages-adapter.mjs` 中按 host / path 嗅探。
- `anthropic-output-effort` 用于新代际 Anthropic wire：只发送 `output_config.effort`，
  绝不发送 manual `thinking.budget_tokens`。这避免把模型代际判断继续硬编码在公共
  encoder 里；模型级例外可由 `ModelInfo` 或 descriptor 方言数据覆盖。
- 用户在条目级可覆盖 `defaultEffort`，但取值受 `effortLevels` 约束。
- **跨 ADR 对齐（2026-11-15）**：系统级统一思考强度词表为 `off | low | medium | high | xhigh | max`；[ADR 83](83-model-routing-by-role.md) 档位/角色配置中的 `reasoningEffort`、`fastMode` 以及 [ADR 48](48-provider-model-options.md) 模型实例 `optionValues`，在进入请求或候选故障切换筛选前，均须按目标 `ChannelDescriptor.capabilities`（及模型目录声明）校验或裁剪，不得向不支持该能力/档位的端口静默透传非法值；`oauth_chatgpt` 仍为「OpenAI 官方」独有。

#### 1.3 自定义 Header（防不兼容的兜底扩展点）

- descriptor 与「用户条目」均可携带 `customHeaders: Record<string,string>`。
- 合并顺序：**wire adapter 协议必需头 < descriptor preset 头 < 用户条目自定义头**
  （用户优先级最高，可覆盖 preset，但**不允许覆盖鉴权头与协议必需头**，避免把
  请求改成非法形态）。鉴权头由 auth 规则单独注入并加保护。
- Header key 必须按 HTTP 语义做大小写归一后校验。冲突校验发生在保存/测试连接阶段，
  不留到首次聊天请求才失败。
- 受保护 header 至少包括：`authorization`、`x-api-key`、`content-type`、
  provider version/beta 头（如 `anthropic-version`、`openai-beta`）以及订阅链路的
  account 头（如 `chatgpt-account-id`）。用户自定义 header 命中保护列表时必须返回
  结构化配置错误，不能静默丢弃。
- 这是面向「奇怪的自建网关 / 代理」的兜底：遇到需要额外 `X-...` 头的端口，用户不
  必等代码支持。

#### 1.4 模型元数据拆分

- descriptor 只负责**连接性**（端点 / 鉴权 / 协议 / 能力 / 头），**不内嵌**模型清
  单与价格。模型信息（contextWindow / 价格 / 别名）抽到独立 `ModelInfo` 来源，可
  由远程拉取或用户填写，避免「连接配置」与「模型目录」两类生命周期不同的数据耦合
  在一个对象里。

### 2. ChannelRegistry（数据驱动 + 用户可扩展）

- 新增一个声明式渠道注册表：**内置 preset 是数据，用户自定义渠道也是同构数据**，
  二者走同一条加载/校验/分发路径（preset 仅是「预填好的用户条目」）。
- `ResolvedChannel` 是 chat runtime、testConnection、model list 与 provider
  diagnostics 共同消费的边界对象。禁止这些调用方各自重新解释 `provider` /
  `authMethod` / `baseUrl`。
- 把现散落的差异收敛进来：
  - `anthropic-messages-adapter.mjs` 的 `idealab` host 嗅探改为读 descriptor 的
    `reasoning.paramStyle` 能力字段；
  - wire adapter 内的 URL / auth / header 硬编码改为由 descriptor 提供端点、鉴权
    与 `customHeaders`。
- 提供 `testConnection(channelConfig)` 契约：发一个最小探活请求，把鉴权 / 端点 /
  头是否可用的判断前移到「保存配置时」，而非「首次对话时」。

### 3. 分发层去二分

- `llm-chat-service.mjs` 不再 `if anthropic else openai`，改为
  `ChannelRegistry.resolve(providerConfig).wire -> 选对应 wire adapter`。
- 删除 `llm-config-store.mjs` 中 `item.provider = 'openai'` 的强制降级。未知/未
  配置渠道应显式报错，或落到一个**显式命名**的渠道
  `openai-compatible`（用户主动选择「OpenAI 兼容」），而非静默归一。

### 4. wire adapter 保持为深模块

- wire adapter 只关心协议本身（请求体编码、SSE 解析、工具调用、错误归一），不
  含任何品牌名判断。端点与鉴权通过入参（来自 descriptor）传入。

## Consequences

### 正向

- 新增纯 OpenAI 兼容渠道（DeepSeek / Groq / Together 等）：仅新增一条
  descriptor，**零代码**。
- 新增端点/鉴权变体（Azure OpenAI）：在 openai-chat wire 上加端点/鉴权规则，无需
  新 wire adapter。
- 新增异构协议（Gemini）：仅此类才需要写新 wire adapter。
- 渠道差异被关在 descriptor 与各自 wire adapter 内部，公共分发路径不再随渠道数量
  增长 if-else，符合文档 20 的「Depth / Seam / Adapter」与
  「increase Locality or Leverage」要求。

### 代价 / 风险

- 这是 A 级变更，涉及 `packages/protocol`（契约）、`llm-config-store`（存储形
  态）、`llm-chat-service`（分发）、前端 `LlmSettingsPanel`（渠道选择）多处。
- **存储迁移**：历史配置里被压成 `provider: 'openai'` 的条目需要迁移到
  `channelId`（默认迁为 `openai-compatible`，保留用户填写的 `name` / `baseUrl`）。
  需要明确的就地迁移逻辑与回写策略，并加迁移测试。
- 迁移不得丢失凭据、默认项、启停状态或能力标记。旧字段需要在一个发布周期内兼容
  读取，并在 view 层投影为新字段，避免用户配置在升级时不可逆损坏。
- 需要为渠道注册表、端点/鉴权规则、迁移逻辑补充聚焦测试（契约 / reducer /
  存储边界变更）。

## Migration

1. 在 `protocol` 引入 `WireProtocol` 与 `ChannelId`，保留旧 `LlmProviderType` 为
   过渡别名（一个发布周期后移除）。
2. `llm-config-store` 读旧条目时：`provider === 'anthropic'` → `channelId:
   'anthropic'`；其余 → `channelId: 'openai-compatible'`。不把解析得到的 `wire`
   作为长期事实源写死；如需兼容旧 UI，可投影 `resolvedWire`。一次性回写前必须保留：
   `id`、`name`、`baseUrl`、`model`、加密 `apiKey` / OAuth token、`authMethod`、
   `enabled`、`isDefault`、`createdAt`、`contextWindow`、价格元数据、
   `supportsVision`、`supportsReasoning`、`supportsPromptCaching` 以及用户自定义
   header / reasoning override。
3. 分发层切换为按 `wire` 选 adapter。
4. 前端把渠道列表改为读 ChannelRegistry，用户新建时选「渠道」，自动带出端点 /
   鉴权 / 默认模型预设。

## Out of Scope（本文档不决定）

- 各渠道具体模型清单的远程拉取策略（沿用现有机制）。
- 计费 / usage ledger 的结构（见文档 25）。
- OAuth 订阅的登录、token 刷新与模型清单策略（见文档 28）。本文只把它表达为
  「OpenAI 官方 channel + `oauth_chatgpt` authMethod -> `openai-responses`」的
  解析约束，不重新定义 OAuth 流程。

## Review / Revision (2026-06-18)

针对「目标对标 Roo Code 的可扩展不同 API 端口」做的自评审，结论是大方向（Channel
与 Wire 分离）成立，但初版在「扩展点开放性」上不够，已据此修订 Decision。要点：

1. **`ChannelId` 必须是开放数据而非闭合枚举**。初版把 id 写成
   `'deepseek' | ... ` 联合类型，等于每加一个端口都要改类型声明，这与「像 Roo
   Code 一样自由加端口」矛盾。已改为 `string` 开放标识，preset 与用户自定义同构
   （见 §1.1 / §2）。
2. **capabilities 应是一等结构**，驱动 UI 与请求构造，取代隐式 host 嗅探
   （见 §1.2）。
3. **模型元数据应与连接性解耦**，descriptor 不内嵌模型清单/价格（见 §1.4）。
4. **需要 `testConnection` 契约**，把配置可用性判断前移到保存时（见 §2 末）。
5. **preset 即数据**：内置渠道与用户自定义渠道走同一加载/校验/分发路径，不为
   preset 另开代码路径。

本轮新增的两个明确扩展点（用户诉求）：

- **用户自定义 Header**（§1.3）：条目级 `customHeaders`，带受控合并顺序与鉴权头
  保护，作为遇到非标网关时的兜底，避免「等代码支持」。
- **思维强度的可配置定义**（§1.2 `reasoning`）：用 `paramStyle` 抽象不同端口表达
  思考预算的方式（openai-effort / anthropic-enabled-budget /
  anthropic-adaptive-effort / anthropic-output-effort / qwen-enable / none），用
  `effortLevels` 驱动 UI；`supported=false` 时不发任何 reasoning 字段，**防止对
  不兼容端口发非法参数**。

> 备注：本节为设计评审记录，尚未运行任何构建或测试；落地仍受 A 级变更流程约束。

## Channel Taxonomy（2026-06-19，锁定）

经讨论，面向用户的渠道按「**谁负责格式转换**」分为五类。这是 UI 的分组方式，底层
仍只收敛到少数 `WireProtocol`；提供商的差异表达为挂在 wire 上的方言数据，而非每家
一套代码。

| 类别（UI） | authMethod | wire | 格式由谁负责 | 用户可配 |
|---|---|---|---|---|
| Anthropic 官方（内置） | `api_key` | `anthropic-messages` | 内置固定 | 选模型、配端点 |
| OpenAI 官方（内置） | `api_key` / `oauth_chatgpt` | `openai-chat` / `openai-responses` | 内置固定 | 选模型、配端点；鉴权可选 API key 或 ChatGPT 订阅 |
| Anthropic 兼容 | `api_key` | `anthropic-messages` | 通用兼容层 | 端点 / key / 模型 / 自定义头 |
| OpenAI 兼容 | `api_key` | `openai-chat`（默认）/ `openai-responses`（可选） | 通用兼容层 | 端点 / key / 模型 / 自定义头 / 选 wire |
| 各提供商（DeepSeek 等） | `api_key` | 复用已有 wire + 方言数据 | 提供商方言数据 | 该提供商预置项 |

### 核心原则（本文档的一句话总纲）

> **格式（wire）写代码，数量极少；端口（端点 / 鉴权 / 头）与方言（能力）填数据，
> 数量任意。** 加一家提供商 = 选一个已有 wire + 填一份数据 = **零代码**；只有当某家
> 用了全新协议（如 Gemini）才需要写一个新 wire adapter。

### 锁定的若干决定

1. **authMethod 是 channel 的通用可选能力**（`api_key` / `oauth_chatgpt`），但当前
   **仅「OpenAI 官方」声明 `oauth_chatgpt`**。OpenAI 订阅链路（见文档 28）因此不是
   分发层的特例 `if`，而是「唯一一个声明了 oauth 的 channel」，由 authMethod 决定
   走 `openai-responses` 还是 `openai-chat`。
2. **Anthropic 官方订阅不纳入**：Anthropic 已禁止第三方使用订阅鉴权，故 Anthropic
   侧所有类别在契约层都**不暴露 `oauth_*`**，仅 `api_key`。这是「不为已禁用能力开
   后门」，非「为其预留」。
3. **OpenAI 兼容默认 `openai-chat`，可选 `openai-responses`**：第三方兼容端口绝大
   多数只实现 `/chat/completions`，故默认 chat；用户可手选 responses（两个 wire
   adapter 均已存在，纯配置切换，不新增代码路径）。
4. **wire 层一律自研，不依赖任何厂商 SDK**（含 `openai` / `@anthropic-ai/sdk` /
   未来 Gemini SDK）。理由：
   - SDK 面向「单一官方端点的快速接入」，而本项目目标是「多端点、可扩展、可自定义
     端点 / 头 / reasoning 的适配」，要求把端点、鉴权、流式、错误这些 Seam 攥在自己
     手里；
   - 「Anthropic 兼容 / OpenAI 兼容」两类本身就服务于第三方网关，SDK 覆盖不了，自研
     wire 无论如何都必须存在，再引 SDK 只会形成双轨制、破坏两侧对称；
   - OpenAI 订阅走 `chatgpt.com/backend-api/codex` + OAuth + account header，本就在
     官方 SDK 标准路径之外。
   - SDK 的请求 / 响应类型定义可作设计参考，但**不作运行时依赖**。

> 备注：本节为设计决议记录，尚未运行任何构建或测试；落地仍受 A 级变更流程约束。

## Open Questions

- `openai-compatible` 是否需要进一步细分（例如是否支持 prompt cache 由用户勾选
  还是按渠道预置）？
- Azure 的 `deployment` 与 `model` 的映射在 UI 上如何呈现最自然？
- Gemini wire adapter 的优先级：是否纳入首批落地，还是先交付 Channel/Wire 分离
  骨架 + OpenAI 兼容 / Azure，再补 Gemini？
