# OpenRouter 渠道说明（openrouter / openrouter-api）

创建时间：2026-08-14
最后更新：2026-08-14

## 1. 这个渠道是什么

OpenRouter 是 Peer Agent 桌面端的一条一等第三方服务渠道：用户在服务商中心可以直接添加，预填官方地址，用 API Key 走 OpenAI Chat 协议发请求。

代码侧标识：

- 渠道 ID：`openrouter`
- 服务模板 ID：`openrouter-api`
- 接入分类：第三方（`third_party`）
- 支持级别：验证兼容（`verified`）
- 鉴权方式：`api_key`
- 通信协议（wire）：`openai-chat`（唯一允许的 wire）
- 默认推理地址：`https://openrouter.ai/api/v1`
- 默认模型：`openai/gpt-4o`

一句话定义：**它不是自定义兼容网关，而是内置的 OpenRouter 官方 API 渠道；一个 Key 可以路由多家上游模型。**

## 2. 接入约定

对照现有第三方 OpenAI 兼容渠道（如 Moonshot）落地，差异只在默认地址、默认模型和可选识别头。

| 项 | 约定 |
|---|---|
| 用户操作 | 添加服务 → 选 OpenRouter → 填 API Key |
| 默认地址 | 预填并默认隐藏 `https://openrouter.ai/api/v1` |
| 请求路径 | `${baseUrl}/chat/completions` |
| 鉴权 | `Authorization: Bearer <api_key>` |
| 可选识别头 | `HTTP-Referer: https://github.com/ly-ccx/Peer-Agent`、`X-Title: Peer Agent`（OpenRouter 推荐，用于应用排名；不是鉴权） |
| 能力标记 | 按第三方 OpenAI 兼容渠道：vision / toolUse / temperature / promptCache；reasoning 走 `openai-effort` |

不要为 OpenRouter 新开一条执行路径。它必须走现有 Channel → Wire → Tool Call → PermissionGrant → Evidence 链，复用 `openai-chat` adapter。

## 3. 品牌识别

设置页按渠道 / 模板识别为 OpenRouter 自己的品牌，不要显示成未知，也不要把服务卡片显示成上游模型厂商。

- `channelId=openrouter` 或 `serviceTemplateId=openrouter-api` → 品牌 `openrouter`
- 模型行仍可按 `vendor/model`（例如 `anthropic/claude-sonnet-4`）显示模型厂商
- `openrouter` 必须在 `openai` 之前匹配，避免被 `openai` 子串误伤

图标来源见代码仓 `apps/desktop/renderer/src/assets/llm-providers/SOURCES.md`。

## 4. 代码落点

- 渠道 / 模板：`apps/desktop/electron/main/provider-channels.mjs`
- 渠道测试：`apps/desktop/electron/main/provider-channels.test.mjs`
- 品牌识别：`apps/desktop/renderer/src/app/components/llmBrand.ts`
- 品牌图标：`apps/desktop/renderer/src/app/components/LlmBrandIcon.tsx`
- 品牌测试：`apps/desktop/renderer/src/app/components/llmBrand.test.ts`

## 5. 相关文档

- 渠道与 wire 分离：`knowledge/decisions/37-provider-channel-and-wire-protocol-separation.md`
- 产品主设计：`design/product/ai-service-provider-center.md`
- P0 冻结清单：`design/product/ai-service-provider-center-p0-freeze.md`（OpenRouter 不在 P0 原生官方清单，按第三方验证兼容接入）
- OpenRouter 官方文档：<https://openrouter.ai/docs/quickstart>
