# 缓存命中率专项：命中率低（期望 ≥95%）的根因与修复

创建时间：2026-08-08
状态：已修复并验证

## 一句话结论

Peer Agent 的"缓存命中率"指标 = **LLM prompt cache 命中率**（cacheRead / (input + cacheRead)），不是本地代码缓存。本机真实数据（`~/.peer-agent/usage/requests.jsonl`，2854 条，2026-07-19 ~ 08-08）显示整体命中率 **64.65%**，远低于 95% 期望。差距由三层构成：**统计归因缺陷**（TUI 路径漏记 cacheRead，约 +4.9pp）、**无缓存能力渠道**（zeus/idealab 网关恒 0 命中）、**真实命中率不足**（受服务端 5 分钟 TTL 与请求间隔限制）。已修复统计缺陷：`packages/runtime-node/src/chatgpt-responses-provider.ts` 的 `usageOf` 补上 cached_tokens 解析，修复后整体命中率估算 **69.55%**（+4.9pp）。

## 专项背景与目标

- 现象：缓存命中率一直不高，期望至少 95%
- 对象：Peer Agent 产品自身的 LLM prompt cache（运行时/LLM 响应缓存）
- 期望产出：量化证据 + 根因分析 + 代码修复 + 验证 + 知识沉淀

## 一、缓存层梳理（map）

Peer Agent 的"缓存"主体是 **LLM prompt cache**（ADR 24 实现），分两类协议：

| 协议 | 机制 | 实现位置 | 断点/开关 |
|---|---|---|---|
| Anthropic-compatible | 客户端在 system/历史前缀打 `cache_control: {type:'ephemeral'}` 断点 | `packages/runtime-node/src/provider-encoders/request-encoder.mjs` `applyAnthropicCacheControl` | `promptCaching` 开关，Desktop 由 `Boolean(provider.supportsPromptCaching)` 判定 |
| OpenAI-compatible（含 DeepSeek） | 服务端自动检测，无需客户端断点 | 同一 encoder 的 OpenAI 分支 | `promptCaching` 仅作 UI 标志，usage 从 `cached_tokens` 提取 |

命中率口径与观测：
- 公式：`cacheReadTokens / (inputTokens + cacheReadTokens)`（`apps/tui/src/composer-status.ts` `cacheHitPercent`，Desktop TokenUsageDisplay 对齐）
- `cacheRead == 0` 时不显示百分比（无正命中不报 0% 徽章）
- usage 字段：`packages/protocol/src/usage-accounting.ts` `UsageAmounts`（inputTokens/outputTokens/totalTokens/cacheReadTokens/cacheWriteTokens），scope 分 provider_request / runtime_turn / conversation_lifetime
- 数据源：`~/.peer-agent/usage/requests.jsonl`（`usage-request-log.mjs` 落盘）+ conversation `meta.lifetimeUsage` 回退
- TTL/淘汰：服务端管理（OpenAI/Anthropic 缓存 TTL 约 5 分钟），客户端不管理

## 二、量化结果（quantify）

数据窗口：2026-07-19 ~ 2026-08-08，2854 条请求记录。

| 维度 | 数值 |
|---|---|
| 整体命中率 | **64.65%**（input 1.54B / cacheRead 2.82B） |
| 含 cacheRead>0 的请求占比 | 91.8%（2621/2854） |
| 含 cacheWrite>0 的请求 | 仅 8 条 / 8.2M（Anthropic 断点链路几乎无写入） |
| 按天波动 | 18.3% ~ 82.2%，从未达 95% |

按 provider/model 分层（input 降序）：

| 渠道 / 模型 | 请求数 | input | 命中率 |
|---|---|---|---|
| ChatGPT 订阅 / gpt-5.6-sol | 797 | 699M | 57.2%（最大单一来源） |
| Grok 官方 / grok-4.5 | 1571 | 352M | 82.4% |
| null / grok-4.5（TUI 记录） | 40 | 138.6M | **0%（统计缺陷）** |
| Qoder CLI / ultimate | 110 | 206M* | 4.1% |
| null / gpt-5.6-sol（TUI 记录） | 21 | 20.8M | **0%（统计缺陷）** |
| zeus / claude-opus-5/4-8 | 29 | 24M | **0%（网关无缓存）** |
| DeepSeek | - | - | 89.7%（最优） |
| Qoder kmodel | - | - | 89.7% |

*注：第一版统计的 Qoder ultimate 数值含 07-26 高峰日（命中 18.3% 那天），需注意归因。

### 关键归因分层

- **noCache 层**（cacheRead 恒 0）：217 条 / 234M input / 0% 命中——null providerName 记录（TUI 聚合路径）+ zeus/claude + Qoder 部分渠道
- **lowHit 层**（命中 <60%）：1194 条 / 738.8M input / 36.1%——gpt-5.6-sol 为主
- **goodHit 层**（命中 ≥60%）：1443 条 / 568.8M input / 80.8%——grok、deepseek、kmodel

### 稀释假设检验（否定）

"新会话首条必然 miss"不成立：新会话首条命中率 53.4%（system prompt 前缀跨会话稳定），多轮会话内非首条命中率 65.1%。差距主要在渠道层而非首条稀释。

## 三、根因分析（root cause）

### 根因 1（统计归因缺陷）：TUI 路径漏记 cacheRead，命中率被人为记 0

- **现象**：`tui:` 前缀的 runtime_turn 记录（79 条，含 grok-4.5 138.6M + gpt-5.6-sol 20.8M input）attribution 缺 providerName/pricing，且 cacheReadTokens 大量为 0；同模型同天 Desktop 记录有 cacheRead>0（如 grok-4.5 1.04M）
- **定位**：`packages/runtime-node/src/chatgpt-responses-provider.ts` 的 `usageOf()` 只解析 `input_tokens/output_tokens`，**完全没解析 `cached_tokens`**（OpenAI Responses API 的缓存命中字段）
- **对照**：Desktop `openai-responses-adapter.mjs` 的 `extractCachedInputTokens` 正确解析 4 字段 fallback；`openai-chat-stream.ts` 的 `usageFrom` 也正确解析——唯独 `chatgpt-responses-provider` 遗漏
- **影响**：TUI 使用 ChatGPT Responses wire 的请求（grok/gpt 走 `createChatGptResponsesProvider`）命中率全部误记为 0，人为拉低整体约 **4.9pp**

### 根因 2（无缓存能力渠道）：zeus = idealab adaptive 网关恒 0 命中

- **定位**：用户配置 `llm-providers.json` 中 zeus baseUrl = `https://idealab.alibaba-inc.com/api/anthropic`
- **机制**：request-encoder.mjs 注释明确——"部分网关(如 idealab adaptive 链路)只写缓存、从不返回 cache_read，实测探针证明缓存断点在该链路是纯成本(写入 $6.25/M)而无复用收益"；`supportsPromptCaching = capabilities.promptCache !== false`，但 llm-chat-service 用 `Boolean(provider.supportsPromptCaching)`——未声明能力 → false → 断点已关闭（cacheWrite=0 佐证）
- **结论**：这部分 0 命中是**设计使然**（避免纯成本），非缺陷

### 根因 3（真实命中率不足）：服务端 5 分钟 TTL + 请求间隔/前缀稳定性

- **gpt-5.6-sol 57.2%**（最大单一来源 699M input）：命中率与请求间隔强相关——**间隔 >5 分钟（TTL 过期）命中归零**（gap=460s→0%，gap=522s→53%）；间隔 <2min 时 60-77%；且大量 `read=4608` 固定小值（只命中最小前缀块）
- **grok-4.5 82.4%**：间隔 0-2min 命中反而低（56.4%，小 input 请求前缀不稳定/无缓存可命中）；10min+ 反而高（73.3%）
- **结论**：OpenAI 服务端缓存 TTL ~5 分钟，agent 多轮工作负载（工具循环、思考间隔、动态上下文）天然低于高频恒定前缀场景；**95% 期望对 agent 场景偏激进**（Anthropic 官方 prompt cache 建议目标 90%+）

## 四、修复（fix）

最小修复：`packages/runtime-node/src/chatgpt-responses-provider.ts` 的 `usageOf()` 补上 cached_tokens 解析，与 Desktop adapter / openai-chat-stream 完全同口径：

```ts
const details = usage.input_tokens_details ?? usage.prompt_tokens_details;
const cacheReadTokens = Number(
  (details && typeof details === 'object' && (details as Record<string, unknown>).cached_tokens)
  ?? usage.prompt_cache_hit_tokens
  ?? usage.prompt_cache_hit
  ?? 0,
);
return {
  inputTokens: Math.max(0, rawInputTokens - cacheReadTokens), // 互斥扣减
  outputTokens,
  totalTokens: rawInputTokens + outputTokens,                  // 保持上游毛口径
  ...(cacheReadTokens > 0 ? { cacheReadTokens } : {}),
};
```

不破坏调用方：字段语义与既有记录完全一致（totalTokens = input + output + cacheRead 的互斥和）。

## 五、验证（verify）

1. **测试**：`node --test packages/runtime-node/src/chatgpt-responses-provider.test.ts` —— 6/6 通过（新增 `reports prompt cache hit tokens in usage` 用例，断言 input_tokens=100/cached=60 → inputTokens=40, cacheReadTokens=60, totalTokens=102）
2. **全量回归**：`node --test packages/runtime-node/src/*.test.ts` —— 82/82 通过，无回归
3. **生效路径**：`apps/tui/src/index.tsx` L90 确认 TUI 使用 `createChatGptResponsesProvider`（修复作用于该路径）
4. **口径一致性**：requests.jsonl 中 1763 条带 totalTokens 的记录全部满足 `totalTokens = input + output + cacheRead + cacheWrite`（0 mismatch），修复后语义一致，无 double count
5. **量化提升**：用 Desktop 同模型命中率回填 TUI 记录后，整体命中率 **64.65% → 69.55%**（+4.9pp，全部来自统计失真修复）

### 预期命中率提升后的真实差距（修复后仍需面对）

即使统计修复到位，**整体命中率仍难达 95%**，原因是服务端/协议层限制：
- zeus/idealab 网关恒 0（无缓存能力，设计关闭断点）
- gpt-5.6-sol 57%（TTL 5 分钟 + agent 请求间隔）
- 有缓存能力的正常渠道最优仅 DeepSeek 89.7%

建议把"命中率期望"按渠道分层管理：有缓存能力渠道（grok/deepseek/kmodel）目标 85-90%+，zeus 类网关单独标注"无缓存"而非计入整体 0 命中。

## 六、后续建议（非本次范围）

1. **指标分层**：统计/显示层区分"有缓存能力渠道命中率"与"含无缓存渠道的整体命中率"，避免 zeus 类恒 0 拖低观感
2. **TTL 感知**：对支持 TTL 的渠道，可在客户端提示/优化请求节奏；或调研服务端缓存 TTL 参数（OpenAI 系不可控）
3. **TUI 归因**：`tui:` 记录 attribution 缺 providerName/pricing（根因 1 的伴生问题），建议补齐以支持按渠道归因统计（参考 `usage-stats-provider-group-id-mismatch.md` 的 A+B 双保险修复）

## 关联

- ADR：`knowledge/decisions/24-provider-cache-and-empty-response-guard.md`（prompt cache 断点设计）
- 经验：`knowledge/experience/usage-stats-provider-group-id-mismatch.md`（provider 归因双轨制）
- 经验：`knowledge/experience/anthropic-output-effort-xhigh-降级修复.md`（thinking 缺失破坏 prompt cache 命中）
- 代码：`packages/runtime-node/src/chatgpt-responses-provider.ts`（本次修复）、`apps/desktop/electron/main/provider-adapters/openai-responses-adapter.mjs`（口径参照）、`apps/tui/src/composer-status.ts`（命中率显示）

