# CLI 运行态反馈调研

创建时间：2026-07-24  
最后更新：2026-07-24

> 目标：调研主流 AI Agent / CLI 如何表达“仍在运行”，解释 Peer CLI 左下角「运行中…」为什么显得静止，并给出后续设计可选项。  
> 范围：本阶段只做调研与建议，不修改 `peer_agent` 代码。

## 1. 结论先行

Peer CLI 当前并非完全没有动画：运行态前缀使用 `| / - \\` 旋转字符，标签还会在最初约 6 帧做一次字符扰动，随后固定为「运行中…」。问题在于：

1. **持续变化只剩一个低显著度字符**，视觉面积太小，用户余光很难确认它还在动。
2. **主体文案很快定格**，几秒后画面几乎没有语义变化。
3. **没有时间证据**，用户无法区分“刚开始”“已经运行 20 秒”和“是不是卡住”。
4. **没有阶段证据**，「思考、调用工具、等待工具、整理结果」都折叠成同一句话。
5. **没有操作提示**，长等待时用户不知道能否取消或如何取消。

主流产品通常不会只依赖一个 spinner，而是组合使用：

> **持续运动 + 经过时间 + 当前阶段/动作 + 可中断提示**

对 Peer CLI，推荐先做一个克制的 MVP：

```text
◐ 正在思考 · 8s                         Esc 取消
◓ 正在运行 bash · 13s                   Esc 取消
◑ 正在整理结果 · 21s                    Esc 取消
```

其中 glyph 持续旋转，秒数持续增长，状态只在真实阶段变化时更新。不要为了“活泼”随机轮播没有事实依据的文案。

---

## 2. Peer CLI 当前表现

### 2.1 代码事实

关联代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`

| 位置 | 当前行为 |
| --- | --- |
| `apps/tui/src/tui-language.ts` | 中文运行态为「运行中…」，英文为 `Working…`；另有「正在取消…」「压缩中…」 |
| `apps/tui/src/tool-result-summary.ts` | `composerRunningStatusLabel()` 在前约 6 帧扰动标签，之后返回固定文案 |
| `apps/tui/src/tool-result-summary.ts` | `composerRunningStatusLine()` 用 `thinkingSpinnerGlyph(frame)` 给标签增加旋转前缀 |
| `apps/tui/src/composer-status-view.tsx` | 左下状态栏负责渲染运行态行 |

因此截图中的感受是准确的：**短暂扰动结束后，真正持续变化的只有左侧一个字符**。从实现角度它“在动”，从感知角度却接近静止。

### 2.2 为什么 spinner 仍然不够

CLI 动态反馈至少要回答三个问题：

| 用户问题 | 当前是否回答 | 缺口 |
| --- | --- | --- |
| 它还活着吗？ | 弱回答 | 只有一个小字符变化 |
| 它正在做什么？ | 否 | 始终是「运行中…」 |
| 我还要等多久 / 已等多久？ | 否 | 没有 elapsed time |
| 等太久能做什么？ | 否 | 没有取消提示 |

单字符 spinner 只能提供很弱的“活性证明”，无法提供**进展证明**。Agent 任务又经常持续数十秒甚至更久，所以这一缺口会被放大。

---

## 3. 竞品对比

> 说明：Codex、Gemini CLI、Aider 可从公开源码确认具体组件；Claude Code 主要依据官方文档和产品可见行为归纳。各产品版本会持续变化，下表关注稳定的交互模式，不追求逐像素复刻。

### 3.1 汇总

| 产品 | 持续运动 | 语义变化 | 时间反馈 | 操作提示 | 可借鉴点 |
| --- | --- | --- | --- | --- | --- |
| OpenAI Codex CLI | 状态文字 shimmer / 动效 | 展示当前活动或状态 | 显示 elapsed time | 提示 `Esc` 中断 | 信息密度高但仍是一行 |
| Google Gemini CLI | spinner 动画 | phrase / thought / 当前响应状态可变化 | 可显示计时 | 提供取消提示 | 同时提供“活着”和“在做什么” |
| Claude Code | thinking / tool 活动态随执行变化 | 思考、工具调用、结果按阶段呈现 | 运行反馈与状态栏信息分层 | 支持中断操作 | 不把整段 Agent 生命周期压成一个状态 |
| Aider | waiting spinner | 文案相对克制 | 不是核心 | 可通过终端中断 | 最低成本的持续生命感 |

### 3.2 OpenAI Codex CLI

公开 TUI 实现中，运行状态组件不是简单的静态 `Working…`：

- 状态文本具有持续 shimmer / motion 效果；
- 显示已经运行的时间；
- 同一行提供中断提示；
- 根据宽度控制信息密度，避免窄终端溢出。

它解决的是四件事：

```text
[动态视觉] [当前状态] [已运行时间] [如何停止]
```

**适合借鉴：** elapsed time 与 `Esc` 提示。这两项都是真实信息，不依赖虚构进度。

**不建议直接照搬：** 大面积 shimmer。如果 Peer 的绿色高亮整行持续扫光，容易喧宾夺主，也可能在低刷新终端中闪烁。

### 3.3 Google Gemini CLI

Gemini CLI 的公开 UI 代码包含独立的 loading indicator、responding spinner 和 phrase cycling 机制。其反馈不是只改一个字符，而是组合：

- 持续 spinner；
- 当前 thought / phrase 或响应状态；
- 经过时间；
- 取消提示；
- 在非交互或受限环境中考虑动画降级。

**适合借鉴：** 状态文案可以变化，但应优先绑定真实阶段，例如「正在思考」「正在运行工具」「正在整理结果」。

**需要警惕：** 随机趣味短语虽然能降低等待焦虑，却会稀释专业感，也可能让用户误以为系统真的进入了某个阶段。Peer 不宜在 MVP 中使用随机短语。

### 3.4 Claude Code

Claude Code 的核心做法是把 Agent 过程拆开呈现：thinking、工具调用、权限/确认、工具结果和最终回答会形成可见的阶段变化；状态栏则承载模型、目录、上下文等相对稳定的信息。

它带来的动态感主要不是装饰动画，而是**执行事件不断改变画面语义**：

```text
思考 → 调用工具 → 工具运行/完成 → 继续思考 → 输出结果
```

**适合借鉴：** Peer 左下角状态应消费已有运行事件，而不是只读取一个 `isRunning` 布尔值。真实阶段变化比随机动画更可信。

**边界：** Claude Code 的自定义 status line 主要承载持久环境信息，不应把它与瞬时运行指示器混为一谈。Peer 可以保留底部稳定状态栏，同时在运行态行展示瞬时进展。

### 3.5 Aider

Aider 采用更传统、成本较低的 waiting spinner：等待模型或后台工作时持续刷新 spinner，结束后清理临时状态，尽量不污染终端历史。

**适合借鉴：** 如果短期只做最小修补，一个更醒目的 Unicode spinner 就比 `| / - \\` 更容易被余光感知。

**局限：** spinner 仍然只能说明“进程还活着”，无法解释长任务正在做什么。它适合作为最低档降级，不应是 Agent TUI 的最终方案。

---

## 4. 常见动态反馈模式

### 模式 A：纯 spinner

```text
◐ 运行中…
```

- 优点：实现简单、兼容性高、无需理解任务阶段。
- 缺点：只能证明 UI 定时器还在刷新，无法证明工作有进展。
- 适用：短等待（约 1–3 秒）或兼容性降级。

### 模式 B：spinner + elapsed time

```text
◓ 运行中 · 12s
```

- 优点：成本低；持续数字变化有明显动态感；不伪造完成百分比。
- 缺点：仍然不知道正在做什么；运行越久，计时也可能放大焦虑。
- 适用：无法获得阶段事件时的首选方案。

### 模式 C：阶段状态 + elapsed time

```text
◑ 正在思考 · 4s
◒ 正在运行 bash · 9s
◐ 正在整理结果 · 15s
```

- 优点：既有生命感，又有真实进展语义；最适合 Agent。
- 缺点：需要稳定的运行状态模型；事件映射不准会误导用户。
- 适用：Peer 推荐的主方案。

### 模式 D：动作流 / 工具事件

```text
✓ 已读取 3 个文件
◐ 正在运行测试 · 18s
```

- 优点：证据最强，用户能看见真实工作成果。
- 缺点：容易刷屏；需要区分历史消息与临时状态。
- 适用：长任务、工具密集任务；应与主消息区配合，而非全塞到底栏。

### 模式 E：随机短语轮播

```text
正在思考… → 正在组织思路… → 正在继续探索…
```

- 优点：视觉上活泼，能降低重复感。
- 缺点：若不对应真实事件，就是“假进度”；可能显得花哨。
- 适用：消费级、品牌化场景；不建议作为 Peer MVP。

### 模式 F：不确定百分比 / 进度条

```text
██████░░░░ 60%
```

- 优点：如果总量真实已知，预期最清楚。
- 缺点：LLM/Agent 任务通常没有可靠总步数，百分比很可能是伪精确。
- 适用：下载、构建、已知批量任务；**不适用于通用思考过程**。

---

## 5. Peer CLI 的三个设计选项

### 选项 1：最小修补

```text
◐ 运行中 · 8s
```

改动概念：

- 将 ASCII spinner 换成更有面积感的 spinner；
- 添加 elapsed time；
- 保留现有固定文案；
- 宽度不足时依次隐藏计时、缩短文案。

**优点：** 风险低、见效快。  
**缺点：** 仍然没有执行语义。  
**适合：** 快速修复当前“像卡住”的问题。

### 选项 2：真实阶段反馈（推荐）

```text
◐ 正在思考 · 8s                         Esc 取消
◓ 正在运行 bash · 13s                   Esc 取消
◑ 正在等待工具结果 · 17s                Esc 取消
◒ 正在整理结果 · 21s                    Esc 取消
```

状态只来自真实事件：

- `thinking`
- `tool-running(toolName)`
- `waiting-tool-result`
- `compacting`
- `cancelling`
- `finalizing`

**优点：** 动态感与信息价值兼顾；不会制造假进度。  
**缺点：** 需要梳理已有 runtime 事件到 UI 状态的映射。  
**适合：** Peer 中期正式方案。

### 选项 3：品牌化动态

```text
◐ 正在思考 · 8s
```

在选项 2 基础上增加：

- 低强度绿色亮度呼吸；
- 文案局部 shimmer；
- 可选、克制的阶段过渡；
- 尊重 reduced motion / 低刷新配置。

**优点：** 品牌辨识度更强。  
**缺点：** 复杂度高；终端兼容性、闪烁和重绘成本需要验证。  
**适合：** 基础信息架构稳定后的视觉增强，不应先做。

---

## 6. 推荐方向

推荐采用 **“选项 1 先止痛，选项 2 成为正式方案”** 的两步路径，但在进入实现前仍需单独确认设计：

### 第一步：最低可用运行态

```text
◐ 运行中 · 8s                            Esc 取消
```

最低要求：

1. 动画在整个运行周期持续；
2. elapsed time 每秒更新；
3. 明确显示取消方式；
4. 窄终端优雅降级；
5. 非 TTY、reduced motion 或低刷新环境可退化为静态文本。

### 第二步：接入真实阶段

```text
◐ 正在思考 · 3s
◓ 正在运行 read_file · 7s
◑ 正在整理结果 · 12s
```

状态优先级建议：

```text
cancelling > compacting > tool-running > thinking > finalizing > generic-running
```

避免快速事件导致文案抖动：

- 阶段最短展示时间约 300–500ms；
- elapsed time 独立持续增长，不因阶段切换清零；
- 工具名使用面向用户的短名称，过长时截断；
- 完成态进入消息历史，底栏临时状态及时清除。

---

## 7. 不建议做的事

1. **不要用虚假的百分比。** Agent 没有稳定总工作量。
2. **不要只让省略号循环。** `.` → `..` → `...` 比当前稍好，但信息增量仍接近零。
3. **不要随机切换“搜索中、分析中、构建中”。** 除非有对应真实事件。
4. **不要整行高亮闪烁。** 长任务会造成视觉疲劳。
5. **不要把每个 token 或内部事件刷到底栏。** 更新过快会闪烁，也浪费终端重绘。
6. **不要把临时运行态写入滚动历史。** 应原地更新，完成后清理或转为简洁结果。
7. **不要一开始就做品牌化 shimmer。** 先解决“活着、在做什么、等了多久、如何停止”。

---

## 8. 后续设计需要确认的问题

本调研不进入代码实现。下一轮设计只需要先确认一个产品取舍：

> Peer 更偏向 **A. 极简克制（spinner + 秒数）**，还是 **B. 信息明确（真实阶段 + 秒数 + Esc）**？

调研建议选择 **B**，同时保持一行、低干扰，并在窄终端自动降级为 A。

---

## 9. 参考资料

- OpenAI Codex CLI 文档：https://developers.openai.com/codex/cli
- OpenAI Codex TUI `status_indicator_widget.rs`：https://github.com/openai/codex/blob/main/codex-rs/tui/src/status_indicator_widget.rs
- OpenAI Codex TUI motion / shimmer：https://github.com/openai/codex/tree/main/codex-rs/tui/src
- Google Gemini CLI：https://github.com/google-gemini/gemini-cli
- Gemini CLI `LoadingIndicator.tsx`：https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/ui/components/LoadingIndicator.tsx
- Gemini CLI `usePhraseCycler.ts`：https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/ui/hooks/usePhraseCycler.ts
- Claude Code 文档：https://code.claude.com/docs
- Claude Code status line：https://code.claude.com/docs/en/statusline
- Aider：https://github.com/Aider-AI/aider
- Aider `waiting.py`：https://github.com/Aider-AI/aider/blob/main/aider/waiting.py
