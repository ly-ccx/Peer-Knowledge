# Peer Agent TUI 完整交互设计

创建时间：2026-07-15
最后更新：2026-07-15
状态：Draft（待产品评审；评审通过前冻结 TUI 代码实现）
关联代码：`peer_agent/apps/tui`（本文只定义设计，不修改代码）
关联知识：

- `knowledge/specifications/tui-and-hook-design-standard.md`
- `knowledge/specifications/runtime-sdk-boundary-architecture.md`
- `knowledge/decisions/35-mode-scoped-tool-projection.md`
- `knowledge/decisions/41-rename-goal-mode-to-plan-mode.md`
- `design/product/goal-mode-ultrathink-workflow.md`
- `design/product/goal-right-status-panel.md`

---

## 一、结论摘要

Peer Agent TUI 不应继续使用铺满底部的动作列表，也不应出现名为 **Switch model**、实际却不能完成模型切换的伪入口。

本方案采用一套经过主流 AI TUI 验证的分层结构：

1. **Composer 是唯一主入口**：输入自然语言；输入 `/` 打开命令建议；输入 `@` 引用文件；行首输入 `!` 执行 Shell（能力成熟后启用）。
2. **状态栏只回答“现在是什么”**：工作区、用户模式、权限策略、模型/推理强度、上下文占用；不承担动作列表。
3. **命令面板只回答“现在能做什么”**：可搜索、按上下文过滤；复杂动作进入二级选择器，不在一级列表中假装完成。
4. **模式、模型、权限各有专用选择器**：展示当前值、候选值、影响范围、不可用原因和确认结果。
5. **Chat / Plan / Goal 是用户模式**；`explorer` 是 Runner 内部只读 profile，不在普通模式选择器中出现。
6. **审批卡片在动作发生处抢占 Composer Dock**，呈现风险、范围和三个明确决策；不使用模糊的全局“权限开关”。
7. **会话是可恢复资源**：新建、列表、恢复、重命名、分叉和压缩进入统一 Session Picker；没有能力时不显示假命令。
8. **运行中 Esc/Ctrl+C 优先中断**，底部展示当前阶段和可执行控制；不允许模式切换静默改变正在运行的 turn。

一句话定义：

> Peer Agent TUI 是以 Composer 为中心、状态可见、命令可发现、复杂设置分层、安全决策就地发生的 Runtime 瘦客户端。

---

## 二、问题与设计目标

### 2.1 当前问题（代码审计）

| 问题 | 当前事实 | 后果 |
| --- | --- | --- |
| “Switch model” 名不副实 | 命令动作只关闭面板并提示到 Desktop 配置 | 用户以为会打开 Switch 控件，实际没有可完成路径 |
| “New session” 是占位 | 只提示当前进程不支持新会话 | 不可用动作污染主命令面板 |
| 命令全部平铺 | 模式、模型、会话、帮助、退出混在同一列表 | 缺少搜索、分类、当前值和二级状态 |
| Explorer 被当成用户模式 | 与 Chat / Plan / Goal 并列 | 与 ADR 35 的 Runner-only profile 冲突 |
| 状态与动作混层 | 状态栏、命令列表、Composer 提示各自承担部分控制 | 入口语义不稳定，信息重复或突然消失 |
| 模式切换缺少 turn 边界 | UI 状态可切换，但运行中的 mode 语义不够明确 | 用户可能误以为切换会改变正在执行的任务 |
| 审批信息不完整 | 有 allow once / allow session / deny，但风险与影响范围不足 | 用户难以做知情决策 |
| 会话能力不完整 | 没有真正的新建、恢复与浏览路径 | TUI 仍像单次进程，而不是长期客户端 |

### 2.2 目标

- 用户不记快捷键也能通过 `/` 找到全部动作。
- 用户一眼看见当前工作区、模式、权限、模型、思考强度和上下文余量。
- 用户能在 TUI 内真正完成模型、模式与权限选择，不跳转到 Desktop。
- 常用路径不超过两层：命令入口 → 专用选择器 → 完成。
- 审批发生在风险动作附近，决策文字明确且可撤销范围清楚。
- 运行、审批、计划、错误和离线状态有一致的底部优先级。
- 80 列可完整使用；40–79 列不丢关键决策，仅降低信息密度。
- TUI 继续复用 Runtime SDK、Projection、Permission 与 Evidence，不创建旁路。

### 2.3 非目标

- 本文不修改 `peer_agent` 代码。
- 不照搬某个竞品的配色或布局。
- 不把 Desktop 的全部设置页面复制进终端。
- 不为 TUI 新建独立模型、权限、会话或 Goal 状态源。
- 不把内部 Explorer 暴露成第四个普通聊天模式。
- 不用尚未实现的菜单项充当“未来能力占位”。

---

## 三、官方竞品研究

研究时间为 2026-07-15，事实来源均为产品官方文档。

### 3.1 对比表

| 产品 | 主入口 | 模型与推理 | 权限与模式 | 会话与运行控制 | 可复用原则 |
| --- | --- | --- | --- | --- | --- |
| Codex CLI | Composer 中输入 `/`；首屏直接列出 `/status`、`/permissions`、`/model` | `/model` 同时选择模型与 reasoning effort | `/permissions` 进入专用权限选择 | 状态栏显示 context left，`?` 查看快捷键 | 首屏状态可见；模型与 effort 是一个完整任务 |
| Claude Code | Slash command + 大量上下文快捷键 | `/model` 或配置别名；支持 effort | `/permissions` 管理 allow / ask / deny；审批按工具发生 | Ctrl+C 中断/清输入，Ctrl+O 展开 transcript，支持 resume | 中断语义分层；审批规则可解释、可管理 |
| OpenCode | `/` 命令；`@` 文件引用；`!` Shell；leader key | `/models` + provider/model picker；可配置 reasoning options | agent/variant 通过专用列表或 cycle | leader+n/l 管理会话，Esc 中断，Ctrl+P 命令列表 | 前缀入口分工；leader 避免抢占终端编辑键；专用 Picker |
| Gemini CLI | `/` 元命令、`@` 上下文、`!` Shell | `/model` 类设置进入对话框 | `/settings`、受控工具确认 | `/resume` 会话浏览；Ctrl+C 取消；checkpoint/restore | 命令按前缀分工；会话浏览与 checkpoint 是独立流程 |
| Aider | 以 `/` 为核心的 REPL | `/model`、`/models`、`/editor-model` | `/ask`、`/code`、`/architect` 表达工作模式 | `/clear`、`/load`、`/undo`，Git 状态深度结合 | 文本命令低成本、可脚本化；模式名字必须对应真实行为 |

### 3.2 各方案优缺点

#### 方案 A：所有动作平铺在一个命令列表

优点：实现简单，动作少时直接。

缺点：

- 模型、权限、模式、会话本质是不同数据结构，平铺后无法表达当前值和后续步骤。
- 动作增多后扫描成本迅速上升。
- 容易产生 “Switch model” 这种只有名字、没有完整流程的入口。

结论：不采用。

#### 方案 B：状态栏中的每一项都可直接 cycle

优点：高手操作快，OpenCode 对 recent model / agent 有类似快捷方式。

缺点：

- 新用户不知道候选集合和切换后果。
- 误触时反馈不足。
- 权限和 Goal 模式不适合无确认循环。

结论：只作为后续加速路径；P0 先提供专用 Picker。

#### 方案 C：`/` 可发现入口 + 专用 Picker + 高频快捷键

优点：

- 与 Codex、Claude Code、OpenCode、Gemini 的共同模式一致。
- `/` 兼顾可发现性和键盘效率。
- Picker 能表达当前值、候选、搜索、说明、禁用原因与确认结果。
- 快捷键只是加速，不成为唯一入口。

缺点：组件和焦点状态机比平铺列表复杂。

结论：采用。

### 3.3 Peer Agent 的取舍

借鉴：

- Codex：首屏状态、`/model` 把模型和 effort 一起处理、context left。
- OpenCode：`/`、`@`、`!` 分工，leader 快捷键，Session / Model 专用选择器。
- Claude Code：运行中中断、权限分层、工具发生处审批、详细 transcript。
- Gemini：会话浏览、恢复与 checkpoint 心智。
- Aider：命令可文本化、模式名称必须准确。

不照搬：

- 不把几十个快捷键常驻显示。
- 不把所有设置塞入 Composer 边框内。
- 不把权限简化为危险的全局 auto/full-access 开关。
- 不让用户模式和内部 Agent profile 共用同一个选择器。

---

## 四、信息架构

### 4.1 四个层级

```text
Conversation viewport
  └─ 消息、工具执行、计划进度、错误与 Evidence

Composer Dock
  ├─ Composer：自然语言 / 前缀输入
  └─ Status bar：当前工作区、模式、权限、模型、effort、context

Transient surface（互斥）
  ├─ Slash suggestions / Command palette
  ├─ Model picker
  ├─ Mode picker
  ├─ Permission picker
  ├─ Session picker
  └─ Help

Blocking surface（最高优先级）
  ├─ Tool approval
  ├─ Plan approval
  ├─ Irreversible action confirmation
  └─ Fatal configuration error
```

### 4.2 入口分工

| 输入/按键 | 职责 | 示例 |
| --- | --- | --- |
| 普通文本 | 发给 Agent | `修复这个测试` |
| `/` | TUI 元命令与工作流入口 | `/model`、`/mode`、`/session` |
| `@` | 引用文件/目录/已配置上下文 | `解释 @src/runtime.ts` |
| 行首 `!` | 直接 Shell，输出进入会话 | `!git status`；P1 启用 |
| `Ctrl+P` | 打开完整命令面板 | 与 `/` 同一命令注册表 |
| `Ctrl+X` leader | 高频动作快捷键前缀 | `Ctrl+X M` 模型，`Ctrl+X N` 新会话 |
| `?` | 当前 Surface 的帮助 | 只展示此时可用按键 |
| `Esc` | 关闭当前浮层；运行中则中断 | 优先级见键盘规则 |
| `Ctrl+C` | 运行中中断；空闲时清输入；再次退出 | 与终端常见习惯一致 |

`/` 与 Ctrl+P 必须共享同一份命令 schema，不允许两套清单漂移。

### 4.3 用户模式

| 模式 | 面向用户的定义 | 计划 | 副作用 | 默认 effort |
| --- | --- | --- | --- | --- |
| Chat | 直接问答与短任务 | 可选 | 按能力逐动作审批 | 模型默认 |
| Plan | 先形成可评审计划，经批准后托管执行 | 强制外部审批 | 批准前阻断；批准后仍受逐动作闸门 | high |
| Goal | 给定目标、边界和 DoD，自驱至验证通过 | 内部动态脚手架 | 仅硬边界/不可逆/歧义处打断 | xhigh（能力允许时） |

`explorer` 不出现在 Mode Picker。它只在 Goal/Plan Runner 调度只读子 Agent 时显示为运行状态，例如 `Explorer 2/3 · searching`。

---

## 五、主界面设计

### 5.1 空会话（≥100 列）

```text
                         [ Peer Agent B3 wordmark ]

                 ┌──────────────────────────────────────┐
                 │ Ask anything…                       │
                 └──────────────────────────────────────┘
                 ~/peer_agent  Chat · Ask  gpt-5.6-sol · high  ctx 100%
```

原则：

- Logo 只在真正空会话显示。
- Composer 内没有模型、模式、工具数量或快捷键说明。
- 状态栏位于边框外；值可聚焦，但默认视觉权重低于输入框。
- 不常驻展示“按 / 打开命令”；用户输入 `/` 时自然出现建议，首次使用可有一次性 hint。

### 5.2 活跃会话

```text
┌─ conversation ───────────────────────────────────────────────────────────┐
│ You  修复失败的测试                                                       │
│                                                                          │
│ Peer  我先检查测试与实现。                                               │
│   ✓ Read  apps/tui/src/app.tsx                                           │
│   ◌ Bash  bun test …                                                     │
│                                                                          │
│                               running · 12s · Esc to interrupt            │
├──────────────────────────────────────────────────────────────────────────┤
│ Ask a follow-up…                                                         │
└──────────────────────────────────────────────────────────────────────────┘
~/peer_agent  Goal · Ask  gpt-5.6-sol · xhigh  ctx 73%
```

工具细节默认压缩为单行摘要；失败、审批中和用户主动展开时显示详情。

### 5.3 Goal 运行布局

TUI 不设常驻左侧导航。宽终端中的 Goal 运行态使用“主交互区 + 右侧 Goal 状态区”双区布局；会话和工作区通过状态栏、`/session`、`/workspace` 及临时 Picker 管理，不永久占用一列。

```text
┌─ conversation / command output ───────────────┬─ Goal ─────────────────┐
│ You / Peer / tool transcript                  │ 修正 CLI Goal 布局       │
│                                               │ 1/2 · running           │
│ ┌─ composer ────────────────────────────────┐ │ 当前：修正文档布局        │
│ └───────────────────────────────────────────┘ │ 验收 / 阻塞 / 证据        │
└───────────────────────────────────────────────┴─────────────────────────┘
~/peer_agent  Goal · Ask  gpt-5.6-sol · xhigh  ctx 73%
```

Goal 状态区共享 [`goal-right-status-panel.md`](./goal-right-status-panel.md) 的信息层级、状态语义和 Runtime 状态源。终端端只改变呈现与导航方式：状态区可聚焦、可折叠；窄终端下依次降级为覆盖式抽屉、全宽临时视图和底部紧凑摘要，不把桌面端左侧导航或完整 Workbench 复制进 TUI。

### 5.4 状态栏

顺序固定：

1. 工作区
2. 模式
3. 权限策略
4. 模型
5. reasoning effort
6. context left

显示 `context left`，而不是仅显示 `context used`。剩余量更接近用户决策：“是否该 compact / 新开会话”。

状态项行为：

- Enter/Space 打开对应 Picker。
- 只用颜色表达强调，不用颜色作为唯一状态语义。
- 未知值显示 `—` 或 `unknown`，不得伪造。
- 当前后端不支持 effort 时显示 `effort auto`，Picker 中解释“由 Provider 决定”。

---

## 六、命令系统

### 6.1 Slash suggestions

输入 `/` 后从 Composer 上方展开，不清空输入：

```text
┌ Commands ────────────────────────────────────────────────────────────────┐
│ /model       Choose model and reasoning effort             gpt-5.6 · high│
│ /mode        Choose Chat, Plan, or Goal                                Chat│
│ /permissions View or change approval policy                              Ask│
│ /session     Create, resume, rename, fork, or compact                        │
│ /status      Show complete runtime status                                    │
│ /help        Show commands and keyboard shortcuts                             │
└──────────────────────────────────────────────────────────────────────────┘
│ /mo                                                                       │
└────────────────────────────────────────────────────────────────────────────┘
```

规则：

- 模糊匹配名称、别名与描述。
- 当前上下文不可用的命令默认隐藏；搜索精确命中时可显示禁用项及原因。
- Enter 执行；Tab 补全；Esc 关闭但保留输入。
- 命令执行成功后把 Composer 恢复到原草稿，除非命令本身消费了草稿。

### 6.2 P0 命令集

| 命令 | 结果 | 是否需要二级 Surface |
| --- | --- | --- |
| `/model` | 选择 Provider、模型、effort | 是，Model Picker |
| `/mode` | 选择 Chat / Plan / Goal | 是，Mode Picker |
| `/permissions` | 查看并调整本会话审批策略 | 是，Permission Picker |
| `/new` | 创建新会话 | 有未提交草稿时确认 |
| `/resume` | 浏览并恢复会话 | 是，Session Picker |
| `/status` | 展开完整状态 | 是，Status Sheet |
| `/compact` | 压缩当前上下文 | 执行前显示预计影响 |
| `/details` | 展开/折叠工具详情 | 否 |
| `/clear` | 清空 Composer 草稿，不删除会话 | 否 |
| `/help` | 上下文帮助 | 是 |
| `/quit` | 退出 | 运行中或有审批时确认 |

没有后端能力的命令不得进入 P0 清单。

### 6.3 命令面板

Ctrl+P 打开的完整面板使用分组：

- Session
- Model & Mode
- View
- Runtime
- Application

每项结构为：`动作名 / 当前值或快捷键 / 一句描述 / enabled 状态`。不再使用 “Switch model” 这类控件名；动作名统一为动宾结构，如 **Choose model**。

---

## 七、模型与思考强度流程

### 7.1 Model Picker

```text
┌ Choose model ────────────────────────────────────────────────────────────┐
│ Search models…                                                          │
│                                                                          │
│ Recent                                                                   │
│ ● OpenAI   gpt-5.6-sol       353k ctx   tools   Current                  │
│   OpenAI   gpt-5.6           353k ctx   tools                            │
│   Anthropic claude-sonnet…  200k ctx   tools                            │
│                                                                          │
│ Reasoning effort   [ low ] [ medium ] [ high ] [ xhigh ]                 │
│ Applies to: next turn and future turns in this session                   │
│                                             Enter select · Esc cancel    │
└──────────────────────────────────────────────────────────────────────────┘
```

### 7.2 行为规则

1. 默认聚焦当前模型。
2. 支持按 Provider、模型名、别名搜索。
3. 每项展示 Provider、完整模型名、上下文窗口、工具能力和可用状态。
4. effort 候选必须由所选模型能力生成；不支持的档位禁用并解释。
5. 切换只影响**下一 turn 及后续 turn**，不修改正在运行的请求。
6. 成功后状态栏立即更新，并显示一次短暂 toast：`Model: gpt-5.6-sol · high`。
7. 凭证缺失时进入 Provider setup 子流程；不得选中后才在发送时失败。
8. 持久化范围明确显示：`This session` / `Default for workspace`。P0 默认只改本会话，避免静默改全局。

### 7.3 为什么不是 Switch

Switch 表示布尔开/关；模型是多候选选择，reasoning 是离散档位。正确控件是 Picker + segmented choice，而不是 toggle/switch。

---

## 八、模式切换流程

### 8.1 Mode Picker

```text
┌ Choose mode ─────────────────────────────────────────────────────────────┐
│ ● Chat   Ask, inspect, and perform short tasks with per-action approval  │
│   Plan   Draft a reviewable plan; execution starts after approval        │
│   Goal   Work autonomously toward verifiable success criteria            │
│                                                                          │
│ Current turn: idle                                                       │
│ Applies to: next message                                                 │
└──────────────────────────────────────────────────────────────────────────┘
```

### 8.2 切换规则

- 空闲时切换立即成为 Composer 下一条消息的 mode。
- 运行中允许打开 Picker，但选择后显示 `Queued for next message`；当前 turn 不变。
- 有待审批计划时，从 Plan 切走不能静默废弃计划；提示：保留草稿 / 取消计划 / 返回。
- Goal 运行中不提供静默切换；先中断或等待停止点。
- Mode Picker 不出现 Explorer。
- 状态栏始终显示**当前 Composer 将提交的 mode**；运行卡片显示正在执行 turn 的 mode。两者不同时标记 `Goal running · next: Chat`。

---

## 九、权限与审批

### 9.1 权限不是单一开关

状态栏的权限摘要使用：

- `Read only`
- `Ask`
- `Workspace write`
- `Custom`

禁止使用容易误解的 `Full access`。任何不可逆动作仍受硬闸门；TUI 快捷选择不能放宽 Runtime 的 deny 与 Hook 规则。

### 9.2 Permission Picker

```text
┌ Permissions for this session ────────────────────────────────────────────┐
│ ● Ask              Read freely; ask before writes and commands           │
│   Read only        Never write or execute mutating commands               │
│   Workspace write  Allow ordinary writes inside ~/peer_agent              │
│                                                                          │
│ Hard rules: destructive Git, publish, external writes always ask/deny     │
│ /permissions rules  View effective allow / ask / deny rules               │
└──────────────────────────────────────────────────────────────────────────┘
```

### 9.3 动作审批卡

```text
┌ Permission required ─────────────────────────────────────────────────────┐
│ Bash                                                                     │
│ pnpm install                                                             │
│                                                                          │
│ Why: install dependencies needed by the requested build                  │
│ Scope: ~/peer_agent                                                      │
│ Risk: network access · modifies lockfile and node_modules                 │
│                                                                          │
│ [1] Allow once   [2] Allow similar this session   [3] Deny               │
│ Ctrl+E explain risk                                      Esc = Deny       │
└──────────────────────────────────────────────────────────────────────────┘
```

规则：

- 卡片抢占 Composer Dock，但不覆盖会话上下文。
- 默认选择 `Allow once`；高风险动作默认选择 `Deny`。
- “Allow session” 必须说明匹配范围，不能泛化成所有命令。
- 显示工具、规范化参数、工作区、风险标签和 Agent 原因。
- Deny 后返回结构化结果给 Agent，允许其调整方案。
- 审批结束后焦点回到此前位置。

### 9.4 Plan 审批

Plan approval 与工具权限审批是两类 Surface：

- Plan approval：批准方案与边界，选项为 `Approve and run / Request changes / Reject`。
- Tool approval：批准具体能力动作，选项为 `Allow once / Allow similar / Deny`。

不得共享文案或混为“Permission”。

---

## 十、会话流程

### 10.1 Session Picker

```text
┌ Sessions · ~/peer_agent ─────────────────────────────────────────────────┐
│ Search sessions…                                                         │
│                                                                          │
│ ● Fix TUI status layout           Goal · running · 2m                     │
│   Design command architecture     Plan · yesterday · 64% ctx              │
│   Explain runtime SDK             Chat · Jul 13                           │
│                                                                          │
│ Enter resume · Ctrl+N new · Ctrl+R rename · Ctrl+F fork · Del delete      │
└──────────────────────────────────────────────────────────────────────────┘
```

### 10.2 规则

- `/new` 立即创建标准空会话并聚焦 Composer；若当前有未发送草稿，先提供保留/丢弃/取消。
- `/resume` 默认列出当前工作区会话，可切换为所有工作区。
- 会话项显示标题、模式、运行状态、时间和上下文余量。
- 运行中的会话可恢复观看，但同一会话只允许一个写入控制端；其他端只读或明确接管。
- 删除是高风险管理动作，需要二次确认，并遵守 Goal plan 级联规则。
- `/compact` 属于当前会话动作，不等于新建会话；完成后记录压缩边界。
- 如果 Runtime 暂不支持持久化会话，隐藏 `/resume`、rename、fork、delete，不显示占位提示。

---

## 十一、运行中与错误状态

### 11.1 底部 Surface 优先级

从高到低：

1. 不可逆动作确认
2. Tool approval
3. Plan approval
4. 凭证/连接致命错误
5. Command/Model/Mode/Session Picker
6. Slash suggestions
7. Composer

同一时刻只显示一个底部交互 Surface。

### 11.2 运行控制

| 状态 | 底部反馈 | Esc | Ctrl+C |
| --- | --- | --- | --- |
| idle | Composer | 关闭浮层/清选择 | 清空输入；再次退出 |
| streaming | `Responding · Esc to interrupt` | 中断当前 turn | 中断当前 turn |
| tool running | `Running Bash · 8s` | 请求取消 | 请求取消 |
| approval | 审批卡 | Deny | Deny / 中断 turn |
| goal running | `Goal 3/7 · verifying` | 打开中断确认或暂停 | 中断当前动作并暂停 Runner |
| error recoverable | 错误卡 + Retry/Edit | 关闭卡片 | 回到 Composer |
| fatal config | 配置修复入口 | 不退出错误 | 退出应用 |

### 11.3 错误表达

每个错误必须回答：

- 发生了什么；
- 哪个范围受影响；
- 用户现在能做什么；
- 重试是否安全。

模型凭证错误提供 `Configure provider`；上下文不足提供 `Compact` / `New session`；权限拒绝提供 `Edit request`；网络错误提供 `Retry`。不能只显示底层异常字符串。

---

## 十二、键盘与焦点规则

### 12.1 焦点优先级

Blocking surface → Transient surface → Composer → Conversation viewport。

按键只交给最高优先级焦点处理；处理后必须 stop propagation，避免一次 Enter 同时批准动作又提交 Composer。

### 12.2 通用按键

| 按键 | 行为 |
| --- | --- |
| Enter | 提交单行消息或确认当前选择 |
| Shift+Enter | Composer 换行 |
| Up/Down | Picker 移动；Composer 空且无浮层时浏览输入历史 |
| Tab / Shift+Tab | 补全或移动焦点 |
| Esc | 关闭最上层 Surface；运行中中断 |
| Ctrl+C | 中断 → 清输入 → 退出的分层语义 |
| Ctrl+D | Composer 为空且空闲时退出 |
| Ctrl+L | 重绘，不丢会话与草稿 |
| Ctrl+P | 命令面板 |
| Ctrl+O | 展开/收起工具 transcript |
| Ctrl+X N | 新会话 |
| Ctrl+X L | 会话列表 |
| Ctrl+X M | 模型选择 |
| Ctrl+X P | 权限选择 |

Leader 快捷键必须可配置；默认使用 Ctrl+X，避免与终端行编辑和应用常用键冲突。

### 12.3 输入法与粘贴

- IME composition 期间 Enter 只确认候选，不提交消息。
- bracketed paste 作为一个事务插入；多行粘贴不自动发送。
- 超长粘贴折叠为可展开摘要，发送前可预览。
- `/`、`@`、`!` 只有在非 composition 状态下触发入口。

---

## 十三、响应式规则

### 13.1 断点

| 宽度 | 布局 |
| --- | --- |
| ≥120 列 | 状态栏一行；Picker 可双列；完整工作区路径；Goal 可与主交互区左右并排 |
| 80–119 列 | 状态栏两行；Picker 单列；工作区用 `~/repo`；Goal 使用覆盖式右侧抽屉 |
| 60–79 列 | 状态栏三行；隐藏次级描述但保留当前值与风险；Goal 使用全宽临时视图 |
| 40–59 列 | 最小可用：状态项逐行；审批按钮纵向；Goal 底部保留紧凑摘要，详情进入全屏视图 |
| <40 列 | 显示明确提示：终端过窄，核心审批、Goal 状态与错误恢复仍必须可读；建议扩宽 |

### 13.2 降级顺序

可以隐藏：快捷键提示、Provider 重复名、描述、时间秒数、装饰边框。

不可隐藏：

- 当前模式；
- 权限决策；
- 模型选择结果；
- 审批动作、范围和风险；
- 运行/中断状态；
- 错误恢复动作。

窄屏不使用水平滚动承载审批选项。

---

## 十四、状态模型

```text
AppState
├─ session: none | idle | running | paused | failed
├─ turnMode: chat | plan | goal
├─ composerMode: chat | plan | goal
├─ surface:
│  ├─ composer
│  ├─ slashSuggestions
│  ├─ commandPalette
│  ├─ modelPicker
│  ├─ modePicker
│  ├─ permissionPicker
│  ├─ sessionPicker
│  ├─ toolApproval
│  ├─ planApproval
│  └─ fatalError
├─ draft
├─ selection
└─ focusOwner
```

关键约束：

1. `surface` 是互斥联合类型，不用多个 boolean 拼出非法组合。
2. `turnMode` 与 `composerMode` 分离，避免运行中切换污染当前 turn。
3. Picker 先维护 candidate，Enter 后才 commit；Esc 永远不改当前值。
4. Surface 关闭后恢复调用前焦点和 Composer 草稿。
5. 所有命令来自统一 registry：名称、别名、分类、快捷键、enabled、执行结果和目标 Surface。
6. UI 只投影 Runtime 状态，不自行推断权限已经生效或任务已经取消。

---

## 十五、与 Runtime 的边界

TUI 必须通过已有 SDK/Host Port 获取：

- 会话快照与事件流；
- 模式投影；
- 模型目录、能力、凭证状态和 context window；
- 权限规则与 PendingApproval；
- Goal/Plan 快照和控制能力；
- Session list/resume/create/rename/fork/delete；
- interrupt/pause/resume/cancel 的确认结果。

TUI 不应：

- 直接读取 Desktop 私有 store 来模拟模型选择；
- 在 `app.tsx` 写死模型窗口或 reasoning 能力；
- 自己维护一套 permission allow-session 缓存；
- 仅修改前端 mode 标签而不更新 Runtime turn mode；
- 把 Explorer 作为用户选择后直接投影；
- 用 toast 代替真实命令结果。

若 SDK 缺能力，先补公共契约，再做 UI；不得以假菜单跨过架构缺口。

---

## 十六、分期与实施顺序

### P0：建立正确骨架

1. 统一 Command Registry 与 Surface 状态机。
2. Composer `/` suggestions 与 Ctrl+P Command Palette。
3. Mode Picker（只含 Chat/Plan/Goal）。
4. Model Picker（真实模型目录 + effort + credential 状态）。
5. Permission Picker 与增强审批卡。
6. 状态栏与 turn/composer mode 分离。
7. 中断、焦点恢复、IME、窄屏行为。

### P1：完整会话

1. Session Picker 与 Runtime 会话持久化契约。
2. New/resume/rename/fork/delete/compact。
3. `@` 文件引用与行首 `!` Shell。
4. Transcript details 与外部编辑器。

### P2：高级效率

1. 可配置 leader key。
2. recent/favorite model cycle。
3. checkpoint/restore。
4. 跨工作区会话与只读观察/接管。
5. 命令插件化，但仍受统一 schema 与权限治理。

每一期只展示已经端到端可完成的命令。

---

## 十七、验收标准

### 17.1 命令与入口

- [ ] 输入 `/mo` 能筛选并进入真实 Model Picker。
- [ ] Ctrl+P 与 `/` 使用同一命令注册表，名称、禁用状态与快捷键一致。
- [ ] 一级命令面板没有 “Switch” 伪控件，没有不可执行占位项。
- [ ] `@`、`!` 与 `/` 的触发规则互不冲突。
- [ ] Esc 关闭 suggestions 后保留原 Composer 草稿。

### 17.2 模型、模式与权限

- [ ] 模型列表展示真实 Provider、模型、上下文窗口、能力与凭证状态。
- [ ] reasoning effort 只展示所选模型支持的候选。
- [ ] 切换模型/模式只影响下一 turn，不改变正在运行的请求。
- [ ] Mode Picker 只有 Chat / Plan / Goal，不出现 Explorer。
- [ ] 权限摘要来自 Runtime 有效规则，不由 UI 文案猜测。
- [ ] 高风险 deny/hook 不能被 TUI 的会话级允许覆盖。

### 17.3 审批与运行

- [ ] 审批卡显示工具、参数、原因、范围、风险与三个明确决策。
- [ ] 窄屏下审批内容和决策完整可见。
- [ ] Enter 不会同时批准动作并提交 Composer。
- [ ] Esc/Ctrl+C 能中断 streaming、tool call 和 Runner，并以 Runtime 确认结果更新 UI。
- [ ] Plan approval 与 Tool approval 的文案和状态机分离。

### 17.4 会话

- [ ] 新会话、恢复、重命名、分叉、删除与压缩均有真实 Runtime 能力后才展示。
- [ ] 有未发送草稿时新建/恢复会话不会静默丢失草稿。
- [ ] Session Picker 能区分 running / paused / failed / idle。
- [ ] 删除会话遵守 Goal plan 级联治理。

### 17.5 响应式与可用性

- [ ] 120、100、80、60、40 列真实 PTY 均可完成发送、选择模型、切换模式和审批。
- [ ] 40 列不丢当前模式、审批风险、决策按钮和中断状态。
- [ ] IME 候选确认不会误发送。
- [ ] 多行粘贴不会自动执行。
- [ ] 所有颜色状态都有文本或符号冗余表达。

### 17.6 架构

- [ ] TUI 继续作为 Runtime SDK 的瘦客户端。
- [ ] Command、Mode、Model、Permission、Session 不复制 Desktop 私有状态源。
- [ ] Surface 使用互斥状态而非互相冲突的 boolean 集合。
- [ ] 相关状态机和键盘优先级有单元测试；关键宽度有 PTY 集成测试。

---

## 十八、评审问题

设计评审需要明确确认以下决策，确认前不进入代码实现：

1. 用户模式是否确定为 Chat / Plan / Goal，Explorer 仅作为内部运行状态？
2. 默认权限摘要是否采用 `Ask`，而非 `Full access` 或模糊的 `write`？
3. 模型与 reasoning effort 是否在同一个 Picker 中完成？
4. Ctrl+X 是否作为默认 leader，Ctrl+P 是否保留为命令面板直达？
5. P0 是否要求先补齐真实模型目录/能力 SDK，再实现 Picker？
6. 会话能力是进入 P1，还是与 P0 同期补齐？
7. 行首 `!` Shell 是否首发，还是等会话与审批稳定后进入 P1？

---

## 十九、官方来源

- Codex CLI overview / features：<https://learn.chatgpt.com/docs/codex/cli>
- Codex developer commands：<https://learn.chatgpt.com/docs/developer-commands?surface=cli>
- Claude Code interactive mode：<https://code.claude.com/docs/en/interactive-mode>
- Claude Code model configuration：<https://code.claude.com/docs/en/model-config>
- Claude Code permissions：<https://code.claude.com/docs/en/permissions>
- Claude Code common workflows：<https://code.claude.com/docs/en/common-workflows>
- OpenCode TUI：<https://opencode.ai/docs/tui/>
- OpenCode keybinds：<https://opencode.ai/docs/keybinds/>
- OpenCode models：<https://opencode.ai/docs/models/>
- Gemini CLI commands：<https://geminicli.com/docs/reference/commands/>
- Gemini CLI keyboard shortcuts：<https://geminicli.com/docs/reference/keyboard-shortcuts/>
- Gemini CLI checkpointing：<https://geminicli.com/docs/cli/checkpointing/>
- Aider in-chat commands：<https://aider.chat/docs/usage/commands.html>

---

## 二十、最终决策口径

本设计否决当前“平铺命令 + 假 Switch + 内部模式外露”的方向，采用：

> **Composer 前缀入口 + 可搜索命令注册表 + 专用选择器 + 就地审批 + 明确运行状态 + Runtime 单一事实源。**

设计评审完成前，`peer_agent/apps/tui` 保持代码冻结；评审后先补公共 Runtime 能力，再按 P0 顺序实施，不以视觉补丁替代完整交互链路。
