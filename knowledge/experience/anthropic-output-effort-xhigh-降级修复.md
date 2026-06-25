# Anthropic 思维强度 xhigh 被悄悄降级为 high 的修复

创建时间：2026-06-24
最后更新：2026-06-24（补充前端档位被硬编码降级、effortLevels 透传 + 归一化修复一节）

## 一句话结论

Peer Agent 把用户在 UI 选的最高思维档 `xhigh` 编码成 Anthropic 请求时，曾因一条**无文档依据的注释臆断**把 `xhigh` 映射成 `high`，导致最高档思维强度被悄悄削了一档。`output_config` 字段名本身没错，错的是档位值。现已修正为忠实透传 `xhigh`。

## 背景

Peer Agent 的思维档位（UI）为 5 档：`off / low / default / high / xhigh`。
其中 `xhigh` 是用户能选的最高强度档。

Anthropic 新代际模型（Opus 4.8 / Fable 5 / Mythos 5 等）通过顶层 `output_config.effort` 控制思考强度，不再支持 manual extended thinking（`thinking.budget_tokens`，强发会被 API 以 400 拒绝）。

## 官方文档坐实的事实

来源：Anthropic TypeScript API 文档（Messages）。逐字确认：

- `OutputConfig { effort, format }`，`effort` 原生枚举 =
  `"low" | "medium" | "high" | "xhigh" | "max"`（**5 档，`xhigh` 是原生档位**）。
- `ThinkingConfigAdaptive { type, display }` —— **只有 `type` 和 `display`，没有 `effort` 字段**。

推论：`effort` 始终属于顶层 `output_config`，与 `thinking` 是 `adaptive` 还是 `enabled` 无关。
代码中"adaptive 格式下 effort 只接受 low/medium/high 三档"的注释前提是错的。

## 问题根因

`apps/desktop/electron/main/provider-encoders/request-encoder.mjs` 中：

```js
// 错误注释：adaptive 格式下 output_config.effort 只接受 low/medium/high 三档。
const ANTHROPIC_OUTPUT_EFFORT = { low: 'low', default: 'medium', high: 'high', xhigh: 'high' };
//                                                                            ^^^^^^^^^^^^ 被折叠
```

`xhigh` 被映射成 `'high'`，于是用户选最高档时，实际只发了 `high`，思维强度被悄悄削了一档。
该 `ANTHROPIC_OUTPUT_EFFORT` 同时服务于两条链路：`anthropic-adaptive-effort` 和 `anthropic-output-effort`，所以两条链路都受影响。

## 修复内容（均在 `peer_agent` 代码仓）

1. `provider-encoders/request-encoder.mjs`
   - `ANTHROPIC_OUTPUT_EFFORT` 的 `xhigh: 'high'` → `xhigh: 'xhigh'`；
   - 重写两处误导性注释，说明 `effort` 原生支持 `xhigh`、与 thinking 模式无关；
   - `max` 无对应 UI 档位，按 YAGNI 不引入。
2. `provider-encoder.test.mjs`
   - 两处 `make('xhigh') → { effort: 'high' }` 断言改为 `{ effort: 'xhigh' }`，并更新注释。

`provider-adapter.test.mjs` 中输入 `high`、期望 `high` 的断言无需改动。

## 验证

`provider-encoder.test.mjs` + `provider-adapter.test.mjs` 共 34 个用例全部通过。

## 经验教训

- **注释里的"只支持 X/Y/Z"这类断言必须能追溯到官方文档**，否则就是把臆测固化成约束，悄悄削弱功能且很难被发现。
- 枚举映射表（effort/budget 这类）改动时，要回到一手 API 文档逐字核对枚举值，不要沿用历史注释里的"经验值"。
- 这类"降级"不会报错、不会失败，只会让效果变差，属于最隐蔽的一类 bug，值得专门沉淀。

---

## 补充：display:"omitted" / redacted_thinking 下思维链回传被丢弃的修复

> 同源问题（Anthropic thinking 处理），由本次复查 thinking 链路时连带发现并修复。补记于 2026-06-24。

### 一句话结论

多轮工具调用回传 assistant 历史时，thinking block 的回推判定写成了"思维正文和签名都在才回推"。但 Opus 4.8 等新代际默认 `display:"omitted"`，思维正文恒为空、签名却携带加密思维——按旧判定会把整个 thinking block（连同 signature）丢掉，违反官方"工具多轮必须回传"的强制要求。现改为**只认 signature**。

### 官方文档坐实的事实

来源：Anthropic「Extended thinking」文档。逐字确认：

- **Opus 4.8 的 `display` 默认就是 `"omitted"`**：thinking 字段返回**空**，但 `signature` 字段仍携带加密的完整思维，用于多轮延续。
- **工具多轮是强制要求**："During tool use, you **must** pass thinking blocks back to the API for the last assistant message."
- **回传 omitted 块时**：thinking 字段填什么都被忽略，服务端靠 `signature` 解密重建——**只要 signature 在就行**。
- `redacted_thinking` 在新文档里已无独立机制章节，是安全过滤触发的罕见路径，被 `omitted` 常态机制取代。所以无需为它单独写分支，统一按"有 signature 就回推"覆盖即可。

### 问题根因

`apps/desktop/electron/main/chat-runtime/anthropic-agent-loop.mjs`（约第 166 行）：

```js
// 改前：thinkingContent 为空时，即使拿到 signature 也整个不回推
if (thinkingContent && thinkingSignature) {
  assistantContent.push({ type: 'thinking', thinking: thinkingContent, signature: thinkingSignature });
}
```

Opus 4.8 默认 `omitted` → `thinkingContent` 恒为空字符串 → `thinkingContent && ...` 为假 → thinking block 整块漏发。

### 实际影响

- **不会报错**（官方有 graceful degradation，缺块时静默禁用 thinking）。
- 但代价是：① 违反官方 "must"；② 推理连续性丢失；③ 我们每轮 `output_config.effort` 都要求 thinking，历史里却没有 thinking block，构成 "mid-turn thinking conflict" → 触发 thinking toggle → **prompt cache 失效（成本上升）+ 模型可能 off-distribution 掉质量**。

### 修复内容（在 `peer_agent` 代码仓）

`chat-runtime/anthropic-agent-loop.mjs`：判定条件 `thinkingContent && thinkingSignature` → `thinkingSignature`，正文用 `thinkingContent || ''` 兜底；补注释说明 omitted 场景。thinking block 仍 push 在 content 数组最前，满足官方顺序要求。

### 验证

- `agent-loop-kernel.test.mjs`（thinking 回推路径直接覆盖）：12 pass / 0 fail。
- `llm-chat-service.test.mjs` 有 2 个失败，经 `git stash` 暂存改动后跑 baseline 确认为**改动前就存在**，属 provider transport fallback 逻辑，与本次无关。

### 经验教训

- **判定"要不要回传 thinking"应以服务端的连续性凭证（signature）为准，而非以人类可读的思维正文为准**——后者在 `omitted`/`redacted` 下天然为空，用它当判据会误删上下文。
- 同样是"不报错只掉效果"的隐蔽降级：缺 thinking block 不会失败，但会悄悄破坏 prompt cache 命中与推理连续性，需要回到一手文档确认默认行为（如 Opus 4.8 默认 `omitted`）才能发现。


---

## 补充：前端档位被硬编码降级（UI 只显示 4 档）

### 现象

用户在 claude-opus-4-8 的思考强度下拉里只看到「关闭思考 / 简洁思考 / 标准思考 / 深度思考」4 项，缺最高的「超深度（xhigh）」档。

### 问题根因

后端 channel 早已声明 Anthropic 支持 xhigh：`provider-channels.mjs` 中 Anthropic channel 的 `capabilities.reasoning.effortLevels` = `['low','default','high','xhigh']`（含 xhigh）。但这份能力**从未透传到前端**，前端 `ChatSurface.tsx` 用 provider 名硬编码判断档位：

```ts
// 只有 openai 能拿到五档；Anthropic 落到 BASE_EFFORT_LEVELS（off/low/default/high）四档
const effortLevels = activeProvider?.provider === 'openai' ? OPENAI_EFFORT_LEVELS : BASE_EFFORT_LEVELS;
```

于是 Anthropic 被归到通用四档，`xhigh` 在 UI 直接消失。叠加上一节的后端 xhigh→high 降级，最高档被双重削弱。

### 修复内容（已批准的“更优解”：透传 effortLevels + 前端消费，在 `peer_agent` 代码仓）

数据通路 channel → resolved → 跨进程契约 → toView → 前端，共 5 处：

| 层 | 文件 | 改动 |
|---|---|---|
| channel→resolved | `provider-channels.mjs` | resolved 对象新增 `reasoningEffortLevels`（取自 capabilities） |
| 跨进程契约 | `packages/protocol/src/index.ts` | `LlmProviderConfig` 新增 `reasoningEffortLevels?: readonly string[]` |
| 主进程 toView | `llm-config-store.mjs` | 透传 `reasoningEffortLevels` 到前端 view |
| 前端归一化 | `chat/state/preferences.ts` | 新增 `normalizeEffortLevels()`：补齐 off 置顶、去重、按标准序排、空/全非法回退四档 |
| 前端消费 | `chat/components/ChatSurface.tsx` | 删掉 `provider==='openai'` 硬编码，改用 `normalizeEffortLevels(activeProvider?.reasoningEffortLevels)`；清理无用 import |

### 为什么要归一化

各 channel 对 `off` 口径不一致：Anthropic/OpenAI 的 `effortLevels` **不含 off**，Google 是 `['off','default']` **含 off**。而 UI 的「关闭思考」是通用开关，所以统一在前端补齐/去重 off 并固定顺序（off→low→default→high→xhigh），避免出现“只有关闭思考”的空菜单。

### 验证

- 新增 `chat/state/preferences.test.ts`，7/7 通过（覆盖五档补 off、四档、Google off 去重、乱序排序、非法值过滤、空回退）。
- `pnpm -r typecheck`：6 个 workspace 项目全绿，跨进程类型链一致。
- 引用闭环核对：`normalizeEffortLevels` 被 ChatSurface 消费，`BASE_EFFORT_LEVELS` 仍被归一化函数使用，无悬空引用。

### 经验教训

- **能力（capability）一旦在后端声明，就要确保它真的透传到消费端**——后端定义了 effortLevels 却没接出来，前端只能退回硬编码，是典型的“信息断流”。
- **避免用 provider 名硬编码能力分支**（`provider === 'openai'`）：能力应由数据驱动（channel capabilities），否则每加一个 provider 都要改判断，且容易把新 provider 默默降级。
- 这是“思考强度全链路”同一主题的第三处坑：后端枚举映射（xhigh→high）、后端 thinking 回传（omitted）、前端档位渲染（硬编码）——三处都属“不报错只掉效果”的隐蔽降级，合并记录便于整体检索。
