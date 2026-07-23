# TUI 与 Desktop Provider Wire 缺口映射

创建时间：2026-07-20  
最后更新：2026-07-20

> 性质：架构现状与缺口映射（只读结论，不改代码）  
> 关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）  
> 关联 ADR：`knowledge/decisions/37-provider-channel-and-wire-protocol-separation.md`  
> 关联总览：`knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`  
> 本机配置样本：`~/.peer-agent/llm-providers.json`  
> 本机观测样本：`~/.peer-agent/provider-traces/`

---

## 1. 问题一句话

**配置共享了，请求路径没共享。**

TUI 与 Desktop 都读同一份 `~/.peer-agent/llm-providers.json`，但真正发模型请求时：

- Desktop 按 `channelId / authMethod` 解析成 `wire`，再走专用 adapter / agent loop
- TUI 多数通道被压成 `createOpenAICompatibleProvider`

因此同一模型可能出现：

- Desktop 私有/专用路径可用
- TUI 兼容层报 `Model provider "<uuid>" returned HTTP xxx`

这不是“用户配错了”，而是 **UI 分叉后 provider wire 未统一**。

---

## 2. 现状分叉图

```text
llm-providers.json
        │
        ├─ Desktop
        │    └─ resolveChannel(wire)
        │         ├─ qoder-private      → agentLoopQoder / sendQoderPrivateStream
        │         ├─ anthropic-messages → agentLoopAnthropic
        │         ├─ gemini             → agentLoopGemini
        │         ├─ openai-responses   → agentLoopOpenAI (Responses)
        │         └─ openai-chat        → agentLoopOpenAI (Chat Completions)
        │
        └─ TUI
             └─ sharedProvider(authMethod)
                  ├─ oauth_chatgpt / oauth_grok → createChatGptResponsesProvider
                  └─ 其他全部（含 Qoder / Anthropic / Gemini / Zeus）
                       → createOpenAICompatibleProvider
```

| 层 | 是否共享 | 说明 |
|---|---|---|
| 模型/通道配置 | 是 | `llm-providers.json` |
| 凭证位置 | 基本共享 | 同本地配置与本机 OAuth/CLI 登录态 |
| Provider wire / 协议 | **否** | Desktop 多 wire；TUI 两档分流 |
| 错误语义 | **否** | TUI 常见 OpenAI-compatible 模板错误 |
| provider-trace | 部分 | Desktop 更完整；TUI 路径更薄 |

---

## 3. Desktop 正式 wire 目录

证据：

- `apps/desktop/electron/main/provider-channels.mjs`（`CHANNEL_IDS` / wire 解析）
- `apps/desktop/electron/main/llm-chat-service.mjs`（`resolvedChannel.wire === ...` 分流）

| channelId | 典型 authMethod | Desktop wire | Desktop 执行入口 |
|---|---|---|---|
| `openai` | `api_key` | `openai-chat` | `agentLoopOpenAI` |
| `openai` | `oauth_chatgpt` | `openai-responses` | `agentLoopOpenAI`（Responses） |
| `openai-compatible` | `api_key` | `openai-chat` | `agentLoopOpenAI` |
| `anthropic` / `anthropic-compatible` | `api_key` | `anthropic-messages` | `agentLoopAnthropic` |
| `google-ai` | `api_key` / `oauth_google` | `gemini` | `agentLoopGemini` |
| `grok` | `oauth_grok` | `openai-responses` | Responses 路径 |
| `qoder` | `qoder_local_auth` / `local_cli` | `qoder-private` | `agentLoopQoder` → `sendQoderPrivateStream` |

Desktop 当前 wire 集合：

```text
openai-chat
openai-responses
anthropic-messages
gemini
qoder-private
```

---

## 4. TUI 当前分流（粗）

证据：

- `apps/tui/src/index.tsx`（`sharedProvider()` / `createOpenAICompatibleProvider`）
- `packages/runtime-node/src/shared-model-config.ts`（共享配置读取）
- `packages/runtime-node/src/openai-compatible-provider.ts`（错误模板）

| 条件 | TUI 路径 | 备注 |
|---|---|---|
| `authMethod ∈ {oauth_chatgpt, oauth_grok}` | `createChatGptResponsesProvider` | 与 Desktop Responses 大致对齐 |
| `authMethod = qoder_local_auth` | 先 `loadQoderAccessToken()`，再 OpenAI-compatible | **只复用 token，不复用 private wire** |
| `authMethod = oauth_google` | 刷新 token 后，常改写 baseUrl 到 `.../v1beta/openai`，再 OpenAI-compatible | 与 Desktop `gemini` wire 不同 |
| 其他全部 | `createOpenAICompatibleProvider` | 含 Anthropic / Zeus / 多数兼容通道 |

TUI 典型错误模板：

```text
Model provider "<credentialId/uuid>" returned HTTP <status>
```

这是 OpenAI-compatible 路径特征，不等于 Desktop Qoder/Anthropic 私有链路错误语义。

---

## 5. 本机已配置通道映射（2026-07-20 样本）

样本来源：`~/.peer-agent/llm-providers.json`

状态定义：

- **ALIGNED**：Desktop / TUI 请求协议同类
- **LIKELY_OK**：都走 OpenAI chat 兼容语义，结构性分叉小
- **GAP**：Desktop 专用 wire，TUI 仍走兼容层；结构性不一致

| 通道名 | channelId / auth | Desktop 应走 | TUI 现在走 | 状态 | 主要缺口 / 风险 |
|---|---|---|---|---|---|
| ChatGPT 订阅 | `openai` + `oauth_chatgpt` | `openai-responses` | Responses | **ALIGNED** | 路径大体一致；上游 403/503 仍可能单独失败 |
| Grok 官方 | `grok` + `oauth_grok` | `openai-responses` | Responses | **ALIGNED** | 路径一致；失败更常是 OAuth scope/凭证 |
| DeepSeek | `openai-compatible` + `api_key` | `openai-chat` | OpenAI-compatible | **LIKELY_OK** | 协议接近；字段/多模态差异仍可能 400 |
| xty | `openai-compatible` + `api_key` | `openai-chat` | OpenAI-compatible | **LIKELY_OK** | 同上 |
| Qoder CLI | `qoder` + `qoder_local_auth` | **`qoder-private`** | OpenAI-compatible + 仅借 token | **GAP（P0）** | 协议、签名、endpoint、错误语义全不同 |
| zeus | `anthropic`（Idealab） | **`anthropic-messages`** | OpenAI-compatible | **GAP（P0）** | Desktop 打 Anthropic Messages；TUI 当 chat/completions |
| 1688MT | `anthropic` + `api_key` | **`anthropic-messages`** | OpenAI-compatible | **GAP（P0）** | 同 Zeus |
| Gemini OAuth | `google-ai` + `oauth_google` | **`gemini`** | OpenAI-compatible（并改 `/openai`） | **GAP（P1）** | Cloud Code / scope / endpoint 易偏 |

统计：

- ALIGNED：2
- LIKELY_OK：2
- GAP：4

---

## 6. 缺口分级

### P0：结构性协议错误（必须先对齐）

1. **Qoder**
   - Desktop：`qoder-private`（私有 SSE / prepareInfer / 业务字段）
   - TUI：token + OpenAI-compatible
   - 表现：同一账号 Desktop/TUI 结果不一致；易见 402 / 空流 / 无效模型

2. **Anthropic 系（zeus / 1688MT / 官方 Anthropic 兼容）**
   - Desktop：`anthropic-messages`
   - TUI：OpenAI-compatible
   - 表现：请求体、headers、tool/stream 语义错位；上游 stream error 难诊断

### P1：半对齐但会踩坑

3. **Gemini OAuth**
   - Desktop：`gemini` wire
   - TUI：OAuth 后塞进 OpenAI-compatible
   - 表现：Cloud Code vs generativelanguage、scope、项目权限差异

### P2：路径大体一致，问题多在上游/凭证

4. **ChatGPT / Grok**
   - 已走 Responses，结构对齐
   - 失败优先查 OAuth/上游，不是 wire 分叉

5. **纯 OpenAI-compatible 通道**
   - 路径同类
   - 失败多是 key、模型名、字段兼容性

---

## 7. 与 ADR 37 的关系

ADR 37 已明确：

> **格式（wire）写代码，数量极少；端口（端点 / 鉴权 / 头）与方言（能力）填数据，数量任意。**

本缺口映射说明：

1. Desktop 已朝 channel/wire 分离演进（`qoder-private` / `gemini` / `anthropic-messages` 等）
2. TUI 仍停留在“共享配置 + 兼容请求捷径”
3. 结果是 **同一 channel 在不同 UI 上落到不同 wire 实现**

因此后续对齐不应再“给 TUI 多堆 if-else 特例”作为终态，而应：

- 短期：TUI 复用 Desktop 已有 wire 入口（止血）
- 中期：抽出 shared provider runtime，Desktop/TUI 共用 wire 分发

---

## 8. 推荐修复顺序（尚未开工）

| 顺序 | 对象 | 目标 |
|---|---|---|
| 1 | Qoder | TUI 接 `qoder-private` 同款发送路径 |
| 2 | Anthropic / zeus / 1688MT | TUI 接 `anthropic-messages` |
| 3 | Gemini | TUI 接 `gemini` wire，去掉强行 `/openai` 捷径 |
| 4 | Shared runtime | 抽公共 provider runtime，消灭双实现 |

每通道验收标准：

1. 同一 `credentialId + model`
2. Desktop 与 TUI 的 **wire / URL 形态 / 鉴权方式** 一致
3. 失败错误类型同类  
   - 不应再出现“Desktop 私有路径成功，TUI 只剩 `Model provider "<uuid>" returned HTTP xxx`”的结构性偏差

---

## 9. 关键代码锚点

| 角色 | 路径 |
|---|---|
| Desktop 通道/wire 解析 | `apps/desktop/electron/main/provider-channels.mjs` |
| Desktop 请求分流 | `apps/desktop/electron/main/llm-chat-service.mjs` |
| Desktop Qoder private | `apps/desktop/electron/main/provider-adapters/qoder-private-adapter.mjs` |
| Desktop Qoder 本地鉴权 | `apps/desktop/electron/main/provider-adapters/qoder-local-auth.mjs` |
| Desktop Qoder agent loop | `apps/desktop/electron/main/chat-runtime/qoder-agent-loop.mjs` |
| TUI 入口与 provider 组装 | `apps/tui/src/index.tsx` |
| 共享配置读取 | `packages/runtime-node/src/shared-model-config.ts` |
| OpenAI-compatible 错误模板 | `packages/runtime-node/src/openai-compatible-provider.ts` |

---

## 10. 结论

1. 用户感知“TUI 和客户端不是一套请求路径”是正确的。  
2. 分叉点不在配置文件，而在 **provider wire 实现层**。  
3. 本机 8 通道里，**Qoder + Anthropic 系是最大结构性 GAP**。  
4. 对齐目标应是：

> **UI 可以分叉；Provider wire 必须统一。**
