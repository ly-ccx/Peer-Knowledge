# 缓存命中率指标体系定义（稳态/全量双口径 + 渠道分层）

版本：v1（专项设计稿）
日期：2026-08-08
状态：待评审

## 背景与动机

外界用"缓存命中率"标定 Agent 框架优劣。但原始命中率是**口径、负载形态、渠道能力**三者的混合结果，单一数字无法正确标定。本指标体系定义：
1. 双口径公式（稳态命中率 + 全量原始命中率）
2. 排除规则（首写轮 / 过期重写轮 / 无缓存渠道）
3. 渠道分层展示（整体 + 分渠道 + 分形态）

## 一、基础口径

### 数据源
- `~/.peer-agent/usage/requests.jsonl`（runtime_turn 聚合记录，含 inputTokens / cacheReadTokens / cacheWriteTokens / providerName / model / at）
- 请求级快照（`usage-request-log.mjs` 落盘）

### 基础公式
```
命中率 HR = cacheReadTokens / (cacheReadTokens + inputTokens)
```
- 分子、分母全部来自 provider 实际返回的 usage 字段（`cached_tokens` / `cache_read_input_tokens`）
- 不估算、不模拟、不美化
- `totalTokens = input + output + cacheRead + cacheWrite`（互斥和）

### 单位
按 **token 数**加权（不是按请求数）。理由：命中率的经济含义是"节省了多少 input 成本"，token 加权才准确。

## 二、双口径定义

### 口径 A：全量原始命中率（Raw）
```
HR_raw = Σ cacheRead / Σ (cacheRead + input)     # 全部记录，一个不漏
```
- 用途：真实负载全貌，对外诚实数字
- 特性：包含首写轮、过期轮、无缓存渠道的所有稀释

### 口径 B：稳态命中率（Steady-state）
```
HR_steady = Σ cacheRead / Σ (cacheRead + input)   # 仅含"稳态有效轮"
```
- 用途：工程质量的稳定指标，剔除不可控的冷启动与超时稀释
- 特性：反映"框架在正常连续负载下能做到多少"

## 三、排除规则（口径 B 适用）

### 规则 1：首写轮排除
- **定义**：每个会话（conversationId）的第一条请求
- **理由**：该轮 system prompt 前缀首次写入缓存，全部 input 必然 miss，是**冷启动成本**，非框架质量问题
- **实现**：按 conversationId 分组，每组时间最早的一条

### 规则 2：过期重写轮排除
- **定义**：距同会话上一条请求间隔 > 5 分钟（300 秒）的请求
- **理由**：缓存 TTL 过期后前缀需重新写入，是**时间成本**，非框架质量问题
- **TTL 参数**：OpenAI/Anthropic 缓存 TTL 约 5 分钟，可配置（`STEADY_TTL_MS`）
- **实现**：`gap = at[i] - at[i-1]`，gap > 300s 则排除

### 规则 3：无缓存渠道排除
- **定义**：provider 不返回 cacheRead（恒 0）或明确无缓存能力的渠道
- **理由**：无缓存能力的渠道命中率恒 0，混入会拉低整体，掩盖真实差距
- **识别**：`providerName` 为空（TUI 归因缺陷）或以 `zeus` 开头（idealab 网关）
- **注意**：排除不等于隐藏——必须单独列出"无缓存渠道"的 input 占比，让外界看到它被排除的原因

## 四、渠道分层展示

### 分层结构（三层）

```
第一层：整体命中率（双口径并列）
  全量原始命中率 HR_raw = xx.x%
  稳态命中率   HR_steady = xx.x%   ← 标注"剔除首写/过期/无缓存"
  口径说明：公式 + 排除规则一句话

第二层：按渠道
  渠道 | 模型 | 命中率 | 形态 | 是否支持缓存
  Grok 官方/grok-4.5    | 76.8% | 稳态 | ✅
  ChatGPT 订阅/gpt-5.6-sol | 43.1% | 稳态 | ✅（弱）
  DeepSeek/deepseek-v4-flash | 80.6% | 稳态 | ✅
  Qoder CLI/ultimate    | 5.7%  | 稳态 | ⚠️ 疑似无缓存
  zeus/idealab          | 0%    | -     | ❌ 无缓存（排除）

第三层：按形态
  首写轮命中率：56.4%（n=253）
  过期重写轮命中率：68.5%（n=1057）
  无缓存渠道命中率：5.4%（n=108）
  稳态有效轮命中率：66.45%（n=1458）
```

### 渠道能力标记
| 标记 | 含义 |
|---|---|
| ✅ 支持缓存 | provider 回报 cacheRead，命中率有意义 |
| ⚠️ 疑似无缓存 | cacheRead 恒 0 但 provider 未声明，需核实 |
| ❌ 无缓存 | provider 明确无缓存能力，命中率不适用 |

### 对外解读口径（一句话）
> "我们同时公布全量原始命中率和稳态命中率：前者是真实负载全貌（含冷启动与超时），后者剔除首写轮/过期重写轮/无缓存渠道，反映框架在连续负载下的工程质量。渠道层面逐项展示，避免单一数字掩盖渠道能力差异。"

## 五、历史基线（本机数据 2026-07-19 ~ 08-08，2876 条）

| 口径 | 命中率 | 记录数 | input |
|---|---|---|---|
| 全量原始 HR_raw | 64.78% | 2876 | 1549M |
| 稳态 HR_steady | 66.45% | 1458 | 304.8M |
| 首写轮 | 56.4% | 253 | 64.3M |
| 过期重写轮 | 68.5% | 1057 | 989.6M |
| 无缓存渠道 | 5.4% | 108 | 190.6M |

### 关键结论（设计依据）
1. **稳态 66.45% 并不比全量 64.78% 高多少**——排除规则只能救"冷启动/超时"稀释，救不了**渠道能力弱**（gpt-5.6-sol 稳态 43%、Qoder ultimate 5.7%）
2. 分渠道差距是主因：Grok 76.8% vs ChatGPT 43.1% vs Qoder 5.7%，**渠道能力差异远大于口径差异**
3. 因此指标体系必须**渠道分层**，否则外界会被整体数字误导

## 六、验收标准

1. 双口径公式可按数据源复现（本文档公式可直接跑出 64.78% / 66.45%）
2. 排除规则可实现为代码（conversationId 分组 + gap>300s + providerName 判空/zeus 前缀）
3. 展示结构为三层（整体 / 渠道 / 形态），渠道层带能力标记
4. 对外解读口径一句话可对外发布

---

## 审计附录：system prompt 前缀稳定性审计

审计时间：2026-08-08
审计范围：`packages/system-context/src/` 全部 prompt source + `llm-chat-service.mjs` systemPrompt 组装路径

### 组装链路

```
llm-chat-service → buildSystemContext(input) → prompt-assembler.assembleSystemContext(input)
→ 各 source.observe(input) → source.render(observation) → sections[] → sortSections() → joinPromptSections() → systemPrompt 字符串
```

### 各 source 动态性分析

| Source | 层 | 稳定性 | 动态原因 |
|---|---|---|---|
| core.identity | L0_CORE | ✅ 完全静态 | 纯代码文本，无 input 依赖 |
| brainstorming | L1_AGENT | ✅ 静态 | 纯代码文本 |
| adaptive-planning | L1_AGENT | ✅ 静态 | 纯代码文本 |
| diagnosis-gate | L1_AGENT | ✅ 静态 | 纯代码文本 |
| runtime.workspace | L2_RUNTIME | ✅ 会话内稳定 | workspacePath 会话内不变 |
| runtime.provider | L2_RUNTIME | ✅ 会话内稳定 | provider/model 会话内不变 |
| runtime.attachments | L2_RUNTIME | ⚠️ 可动态 | attachments 在轮间可能新增 |
| runtime.project_instructions | L2_RUNTIME | ✅ 稳定 | AGENTS.md 内容不变 |
| runtime.reminders (tool rules) | L5_TOOL_RULES | ✅ 静态 | 工具规则文本 |
| runtime.reminders (mode) | L6_MODE_REMINDER | ❌ 每轮变化 | 含 `mode/effort/provider/model` 等运行时状态 |
| automation_intent | L6_MODE_REMINDER | ⚠️ 可动态 | 自动化上下文变化时 |
| goal_plan | L6_MODE_REMINDER | ❌ 每轮变化 | 目标进展、taskId 等变化 |
| goal_runner | L6_MODE_REMINDER | ❌ 每轮变化 | 当前 task、边界、预算等 |
| goal_checkpoint | L6_MODE_REMINDER | ❌ 每轮变化 | 检查点注入 |
| explorer | L6_MODE_REMINDER | ⚠️ 可动态 | explorer 活跃时变化 |
| verifier | L6_MODE_REMINDER | ⚠️ 可动态 | verifier 活跃时变化 |
| mcp_host | L4_CAPABILITIES | ✅ 会话内稳定 | MCP 注册表不变 |
| context_extension | L3_INSTRUCTIONS | ⚠️ 可动态 | 扩展上下文按需注入 |
| continuity | L7_CONTINUITY | ❌ 每轮不同 | 压缩摘要每轮追加 |

### 关键结论

1. **L0-L5 层基本稳定**（约 70-80% 的 system prompt 内容），**L6-L7 层每轮均变化**（约 20-30%）
2. 当前 system prompt 是**单块字符串**，动态内容毒化整个前缀缓存
3. 修复方向：将 system prompt 拆分为**稳定块**（L0-L5）+ **动态块**（L6-L7），稳定块独立打缓存断点

### 预期影响

- **Anthropic 渠道**：拆分后稳定块设 `cache_control: ephemeral`，动态块不设，**预期稳定块命中率接近 100%**，整体命中率提升显著
- **OpenAI 兼容渠道**（DeepSeek/Grok/GPT）：服务端自动缓存基于前缀匹配，拆分后稳定块作为 system prompt 前缀不变，**预期大幅提升前缀命中率**
- **当前会话 DeepSeek 90% 的天花板有望突破到 95%+**

---

## 实现记录（2026-08-08 专项落地）

### 交付物 1：渠道分层命中率展示

**新增模块**：`apps/desktop/electron/main/cache-hit-rate.mjs`
- `computeCacheHitRateMetrics(rows)`：核心计算引擎
  - `raw`：全量原始命中率（全部记录）
  - `steady`：稳态命中率（剔除首写轮 + 过期重写轮 + 无缓存渠道）
  - `byChannel`：分渠道（providerName/model），raw + steady 双口径
  - `byForm`：分形态（首写/过期/稳态/无缓存）
- `isNoCacheChannel(row)`：无缓存渠道识别（providerName 空 / zeus 前缀）
- `STEADY_TTL_MS = 5min`：过期阈值（可配置）
- `formatCacheHitRateMetrics(metrics)`：格式化文本输出
- `collectCacheHitRateMetrics()`：从 requests.jsonl 读取并计算

**IPC 接入**：`usage:cache-hit-rate`（register-data-ipc.mjs + main.mjs port 接线）

**测试**：`cache-hit-rate.test.mjs` 5 用例 + `register-data-ipc.test.mjs` 3 处断言，全通过

**真实数据基线**（2026-07-19 ~ 08-08）：
```
全量原始 64.79%  |  稳态 66.46%
分渠道稳态：Grok 76.8% / ChatGPT 43.1% / DeepSeek ~80% / Qoder 5.7%
分形态：首写 56.6% / 过期 68.5% / 稳态 66.5% / 无缓存 5.4%
```

### 交付物 2：system prompt 前缀稳定化

**核心改动**（向后兼容，不传新参数时行为不变）：
1. `packages/system-context/src/prompt-assembler.mjs`：新增 `renderStableSystemContext(context)`——只渲染 L0-L5 稳定层（剔除 L6_MODE_REMINDER / L7_CONTINUITY 动态层）
2. 导出链打通：`system-context/index.mjs` + `index.d.ts` → `apps/desktop/electron/main/prompt/index.mjs` → `llm-prompts.mjs` → `llm-chat-service.mjs`
3. `llm-chat-service.mjs`：systemPrompt 构建处同时渲染 `stableSystemPrompt`
4. `chat-runtime/anthropic-agent-loop.mjs`：新参数 `stableSystemPrompt` → `buildCanonicalRequest.stableSystem`
5. `packages/runtime-node/src/provider-adapters/anthropic-messages-adapter.mjs`：`sendAnthropicMessagesStream` 新参数 `stableSystem` 透传
6. `packages/runtime-node/src/provider-encoders/request-encoder.mjs`：`encodeAnthropicMessagesRequest` 新参数 `stableSystem`——system 拆为 `[稳定块(带断点), 动态块(不带)]` 两段

**效果机制**：
- Anthropic 渠道：稳定块独立打 `cache_control:ephemeral` 断点，L6/L7 动态变化不再毒化稳定前缀
- OpenAI 兼容渠道：system 前缀稳定 → 服务端前缀匹配更长 → 命中率提升

**验证**：system-context 10/10 + runtime-node 28/28 + cache-hit-rate 5/5 + ipc 4/4 = 47/47 通过

### 预期收益

- 指标展示层：外界可同时看到全量原始（真实负载全貌）+ 稳态（工程质量）双口径
- 渠道层：逐渠道展示，无缓存渠道（zeus）单独标注，不再拖累整体观感
- 真实命中率：system 稳定块约 35M tokens/月从动态 miss 变为稳定命中，Anthropic 渠道断点独立命中

### 待办（非本次范围）

1. **UI 展示落地**：cache-hit-rate.mjs 的格式化输出尚未接入 renderer 可视化（当前可通过 IPC 查询）
2. **发布后观测**：前缀稳定化需发布后跑数周，用 `usage:cache-hit-rate` 对比前后命中率
3. **TUI 归因修复**：`tui:` 记录 attribution 缺 providerName（根因 1 伴生），影响渠道归因完整性
