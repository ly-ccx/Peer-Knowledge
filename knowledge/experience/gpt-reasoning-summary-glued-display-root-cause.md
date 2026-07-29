# GPT reasoning 显示「粘在一起」：现象、链路与根因

> 代码仓库：`peer_agent`（桌面端 `apps/desktop` + `packages/chat-kernel`）  
> 知识仓库：`peer-knowledge`  
> 创建时间：2026-07-28  
> 最后更新：2026-07-28  
> 范围：**只做认知与口径沉淀**；不改动现有 thinking 拼接链路

## 1. 用户可感知现象

在 GPT / o 系列（Responses 路径）对话中，思考区内容常出现两类观感：

1. **不像完整 thinking**：读起来更像一串短状态句，而不是逐步展开的完整推理。
2. **短语粘连**：多句状态摘要中间缺少空格或换行，例如  
   `Planning inspectionInvestigating pathFixing earliest human turn tracking`。

用户直觉常是：「是不是前端渲染坏了？」「为什么不是完整 thinking？」

## 2. 问题重写（系统语言）

| 维度 | 表述 |
|------|------|
| 层 | Provider 产出形态 + 流式拼接契约 + 展示文案预期 |
| 可观察症状 | thinking 通道里多条 reasoning summary 被原样 concat，短语边界丢失 |
| 不是什么 | 不是 virtual viewport / scroll 导致的「拆词」；也不是 Markdown 吃空格 |

## 3. 数据链路（source of truth）

```text
OpenAI Responses SSE
  ├─ response.reasoning_summary_text.delta   ← 多数场景主要是它
  └─ response.reasoning_text.delta           ← 完整 reasoning（若模型/策略提供）
        │
        ▼
openai-responses-adapter
  → chat:stream:thinking { content }
        │
        ├─ renderer: useConversationStreamRouter.appendThinking
        │     (lastSeg.content || '') + chunk     ← 现状：朴素拼接
        │
        └─ main: llm-chat-service
              accumulatedThinking += content
              segments thinking 同段 append
                    │
                    ▼
              Chat UI 思考区原样展示最终字符串
```

关键代码锚点（只读定位，**本次不改**）：

| 环节 | 位置 |
|------|------|
| 事件映射 | `apps/desktop/electron/main/provider-adapters/openai-responses-adapter.mjs`（`reasoning_summary_text` / `reasoning_text` → `chat:stream:thinking`） |
| Live 拼接 | `apps/desktop/renderer/src/chat/hooks/useConversationStreamRouter.ts` → `appendThinking` |
| Main 累积 | `apps/desktop/electron/main/llm-chat-service.mjs`（`accumulatedThinking` + thinking segment） |
| Kernel 归约 | `packages/chat-kernel/src/thinking-reducer.ts` → `thinkingContent + content` |

## 4. 根因假设与证伪

### 主因 A：API 给的是 summary，不是完整 CoT

- **假设**：GPT 在常见配置下只流式吐出 **reasoning summary（状态摘要）**，短句、进度条式。
- **证据**：adapter 显式订阅 `response.reasoning_summary_text.delta`；多数回合用户只看到短语级内容。
- **如何证伪**：若同模型在 API 层稳定吐出长篇 `reasoning_text` 且前端仍只显示短句，则主因不在 summary 形态。

### 主因 B：短语之间无分隔 + 客户端朴素拼接

- **假设**：多条 summary delta 常 **不带尾部空格/换行**；客户端对 thinking 使用 **朴素字符串拼接**，边界被抹平。
- **证据**：  
  - 现状拼接均为 `prev + next` / 模板字符串累加；  
  - 手工复现：`"Planning inspection" + "Investigating path"` → 粘连。
- **如何证伪**：若上游每个 delta 已自带 `\n` 或空格，而 UI 仍粘连，则问题在展示层而非拼接。

### 已排除 / 易混淆

| 假说 | 为何排除或降级 |
|------|----------------|
| virtual viewport 把词拆行 | 那是滚动/虚拟列表几何问题；粘连是**内容字符串本身**无分隔 |
| Markdown 渲染吃空格 | 粘连发生在 segment `content` 累加阶段，早于展示 |
| 必须用启发式按大写断行 | 曾尝试 `joinThinkingContent` 防粘连，会误伤流式切开的 camelCase（`set`+`State`）；产品决策已 **整段还原为朴素拼接** |

## 5. 因果链（改与不改）

```text
[资源] 模型/API 策略 → 多为 summary 短句
   → [加载/适配] summary_text / reasoning_text 并入同一 thinking 通道
   → [状态] 朴素拼接累积 thinkingContent / segment.content
   → [展示] 思考区按最终字符串渲染
```

**当前产品决策（边界）**：

- **保持** 朴素拼接链路不变（连在一起就连在一起）。
- **不做** 客户端启发式断句（避免再伤 camelCase / 中途 token）。
- **要做** 认知与文案：明确「这是推理摘要」，管理预期。

## 6. 约束

| 类型 | 约束 |
|------|------|
| 工程 | 不修改 `peer_agent` 现有 thinking 拼接实现 |
| 产品 | 不把 summary 宣传成「完整思考过程」 |
| 验收 | 知识库文档可独立阅读；代码仓 diff 无 thinking 拼接相关变更 |
| 黑名单 | 不再默默加「大写开头就插换行」类启发式作为默认路径 |

## 7. 成功检查（本文档范围）

- [x] 诊断文写清：summary 形态 + 朴素拼接 = 粘连观感  
- [x] 标明链路锚点与「不改代码」边界  
- [ ] 产品文案另文给出用户可见命名（见 `design/product/gpt-reasoning-summary-product-copy.md`）

## 8. 非目标

- 不恢复 / 不迭代 `joinThinkingContent` 启发式  
- 不在本次改 adapter 事件分流或 UI 组件  
- 不承诺「完整 CoT 可视化」（受模型与 API 策略限制）  
- 不把 virtual scroll、sticky、测高等滚动问题并入本因

## 9. 经验口诀

> GPT 思考区先问：**是 summary 还是完整 reasoning？**  
> 粘连先查：**delta 有没有分隔符 + 是不是朴素拼接**。  
> 断句启发式能修观感，也容易拆碎 `setState`——**默认链路保持朴素拼接**。  
> 产品侧用「推理摘要」管理预期，比假装「完整思考」更诚实。

## 10. 相关记录

- 曾引入再还原：`joinThinkingContent`（防 status phrase 粘连 → 误伤 camelCase → 整段还原朴素拼接）  
- 产品文案与命名口径：`design/product/gpt-reasoning-summary-product-copy.md`
