# 会话搜索面板（Search Chats）整体设计

创建时间：2026-07-18  
最后更新：2026-07-18  
状态：Ready for implementation（关键产品决策已确认，可进入代码实现）  
关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）  
参考对象：Codex.app 顶部搜索入口 +「Search chats」快速面板

---

## 一、一句话定义

> Peer Agent 的会话搜索面板是**跨工作区的任务索引快速切换器**，不是侧边栏内联过滤器，也不是全文检索引擎。

用户通过侧栏顶部的搜索图标或快捷键打开一个居中的轻量面板：输入关键词，实时从本地会话索引里匹配任务标题，一键跳转；空查询时展示最近会话，并附带少量「建议动作」。

---

## 二、问题与动机

### 2.1 现状痛点

当前左栏 `Sidebar` 的会话列表：

1. **按当前工作区过滤**：`conversationsList({ workspacePath: activeWorkspace })`，换项目就要先切 workspace。
2. **只有纵向滚动列表**：会话一多（本地已约 200+ 条）靠肉眼扫标题成本高。
3. **没有全局入口**：左栏收起时（`⌘B` / 拖窄收起）几乎无法快速找旧任务。
4. **已有「查找」语义被占用**：线程内 `ChatFindBar` 绑定 `⌘F`，只搜**当前会话消息**，不能跨会话。

### 2.2 Codex 对标（截图行为拆解）

| 元素 | Codex 行为 | Peer 取舍 |
| --- | --- | --- |
| 入口 | 侧栏顶栏放大镜图标 | **采用**：侧栏顶栏常驻搜索按钮 |
| 面板形态 | 居中浮层，带输入框 + 分组列表 | **采用**：复用 `Overlay` 基座，轻量 palette |
| 主结果区 | `Chats`：标题 + 工作区名 + `⌘1…⌘9` | **采用** |
| 建议区 | `Suggested`：New chat / Open folder / Search files | **部分采用**：P0 仅「新建任务」 |
| 搜索范围 | 跨项目会话标题 | **MVP 跨工作区搜标题，不含归档**；正文搜索后置 |
| 快捷键 | 图标打开；结果位 `⌘1-9` | **采用**；打开面板快捷键 **`⌘K`**（已确认） |

### 2.3 非目标（本期明确不做）

- 不做完整 Command Palette（命令、设置、MCP、技能全量索引）。
- 不做会话**消息正文**全文检索（需要索引/扫描 `*.jsonl`，成本与隐私边界另议）。
- 不做语义 / 向量搜索。
- 不做云端同步检索。
- 不把侧栏列表本身改成「永远显示过滤框」（侧栏保持任务索引简洁；搜索走浮层）。

---

## 三、用户场景

1. **跨项目找回任务**  
   在 `peer-knowledge` 里突然想起 `aper` 下某次「修复 git config」会话 → 打开搜索 → 输入关键词 → 回车跳转（必要时自动切换工作区）。

2. **左栏收起时快速切换**  
   宽屏写代码、左栏已收起 → `⌘K` 打开搜索 → 键盘完成切换，无需先展开侧栏。

3. **空查询浏览最近任务**  
   打开面板不输入 → 看到最近 N 条（跨工作区）+ 建议动作，相当于「最近任务启动台」。

4. **键盘流操作**  
   输入 → `↓/↑` 移动 → `Enter` 打开；或直接 `⌘3` 打开第 3 条。

---

## 四、信息架构与交互

### 4.1 入口

| 入口 | 行为 |
| --- | --- |
| 侧栏顶部搜索图标 | 打开面板；`aria-label`：搜索会话 |
| 全局快捷键 | 打开 / 关闭面板（**`⌘K`**，已确认） |
| 建议动作「搜索会话」（若未来扩展命令板） | 同打开 |

放置建议（对齐 Codex + 现有 Sidebar 结构）：

```text
┌ Sidebar ──────────────────┐
│ [Brand]          [🔍]     │  ← 搜索入口（顶栏右侧）
│ [Workspace ▾]             │
│ [＋ 新建任务]              │
│ 置顶 / 会话列表 …         │
│ 设置                      │
└───────────────────────────┘
```

左栏收起时：搜索入口不可见，**必须依赖快捷键**；可选后续在 `ChatHeader` 增加次要入口（非 MVP）。

### 4.2 面板结构

```text
┌──────────── Search chats ─────────────────┐
│ 🔍  Search chats…                         │
│                                           │
│ Chats                                     │
│  ● 查看文档和代码并总结认知    aper    ⌘1 │
│    怎么构建出来之后报错了？ peer-know… ⌘2 │
│    …                                      │
│                                           │
│ Suggested                                 │
│  ＋ 新建任务                         ⌘N   │
└───────────────────────────────────────────┘
```

布局规则：

- 浮层居中，宽度约 `min(560px, 92vw)`，最大高度约 `min(70vh, 520px)`。
- 复用 `Overlay`（`apps/desktop/renderer/src/app/components/Overlay.tsx`）+ `overlay.css` 动效基座；面板 class 如 `.conversation-search-palette`。
- 打开时自动 focus 输入框；关闭时恢复打开前焦点。
- 点击遮罩 / `Esc` 关闭（`Overlay` 已支持）。

### 4.3 列表行

每条会话结果行展示：

| 字段 | 来源 | 说明 |
| --- | --- | --- |
| 标题 | `ConversationMeta.title` | 空标题时降级为「未命名任务」/ `Untitled` |
| 工作区短名 | `workspacePath` → basename，或 workspaces 表 `name` | 与 Codex 右侧灰字一致 |
| 快捷位 | 前 9 条显示 `⌘1`…`⌘9` | 仅当前可见结果列表排序下的前 9 |
| 状态微标（可选） | running / compacting / pinned | 复用侧栏已有视觉语言，避免信息过载 |

选中态：键盘高亮与 hover 共用同一 `is-active` 样式。

### 4.4 空查询 / 有查询 / 无结果

| 状态 | 内容 |
| --- | --- |
| 打开且 query 为空 | `Chats` = 最近更新的 active 会话（跨工作区，默认 20 条）；下方 `Suggested` |
| 有 query | `Chats` = 标题匹配结果（排序见 §六）；`Suggested` 可收起或仅保留「新建任务」 |
| 无匹配 | 文案：「未找到相关会话」+ 建议「新建任务」 |

### 4.5 选择会话后的跳转语义（关键）

选中一条会话时：

1. 若该会话 `workspacePath` ≠ 当前 `activeWorkspace` → **先切换工作区**，再选中会话。  
2. **MVP 搜索结果仅含 `status: active` 会话**，不出现归档项，因此不涉及归档恢复 / 归档视图跳转。  
3. 关闭搜索面板。  
4. 主区加载该 `conversationId`（复用现有 `onSelectConversation` 路径）。

> 原则：搜索是「定位并进入」，不改会话内容；跨工作区切换必须明确、可预期。

### 4.6 Suggested 动作（MVP）

| 动作 | 行为 | 快捷键展示 |
| --- | --- | --- |
| 新建任务 | 调用现有 `onNewChat`（当前工作区） | `⌘N`（若与系统/应用冲突则只展示、不强制全局抢占） |

P0 **只保留「新建任务」**，不包含「打开文件夹」「查看已归档」。

- 「打开文件夹」→ P1 可选。  
- 「查看已归档」→ 不进 Suggested；归档仍走侧栏既有入口。  
- **不做** Codex 的 `Search files`（那是代码/文件搜索，Peer 已有 workbench / agent 工具链，不应塞进会话搜索 MVP）。

### 4.7 键盘交互

| 按键 | 行为 |
| --- | --- |
| `⌘K` | 开关面板 |
| `Esc` | 关闭 |
| `↑` / `↓` | 在「结果 + 建议动作」扁平列表中移动 |
| `Enter` | 激活当前高亮项 |
| `⌘1`…`⌘9` | 直接打开对应会话结果（不含 Suggested） |
| 输入 | 重置高亮到第 1 项；防抖 0–50ms（纯本地标题匹配可不防抖） |

焦点陷阱：面板打开时 Tab 只在输入框与列表间循环（或仅保留输入框 + 方向键，简化实现）。

---

## 五、范围分层

### P0 — MVP（对齐截图核心价值）

1. 侧栏搜索入口 + 全局快捷键打开面板。  
2. 基于本地 `index.jsonl` 的**标题子串匹配**（大小写不敏感）。  
3. **跨工作区**列表；行内展示工作区名。  
4. 键盘导航 + `⌘1-9` + Enter 跳转（含自动切工作区）。  
5. 空查询展示最近会话。  
6. Suggested：**仅「新建任务」**（P0 不包含打开文件夹 / 归档入口）。  
 
7. i18n（中/英）+ 无障碍基础（`role="dialog"`、`aria-label`、列表 `aria-activedescendant` 或 option 语义）。

### P1 — 增强

1. 匹配 **pinned 加权**、**当前工作区加权**。  
2. 查询词高亮（标题内 `<mark>`）。  
3. 过滤 chip：仅当前工作区 / 仅置顶 / 含归档。  
4. 侧栏收起时在 `ChatHeader` 放次要搜索入口。  
5. 最近打开会话 MRU（内存 + 可选持久化），空查询优先 MRU。

### P2 — 后置

1. 消息正文 / 工具结果片段检索（需独立索引或按需扫描，明确性能预算）。  
2. 升级为通用 Command Palette（会话 + 命令 + 设置项）。  
3. 拼音 / 模糊（fzf 风格）匹配。  
4. 多窗口 / 多实例会话变更同步下的搜索一致性压测。

---

## 六、检索与排序

### 6.1 数据源

- 权威源：`packages/conversation-store` 的 `index.jsonl`（`ConversationMeta`）。  
- 字段：`id`, `title`, `workspacePath`, `updatedAt`, `status`, `pinnedAt`, `pinnedOrder`, `mode`, …  
- **MVP 只读 index，不打开每条 `/{id}.jsonl`。**

现状 API：

- `listConversations({ status })`  
- `listConversationsByWorkspace(workspacePath, params)`  
- **无** `searchConversations`

### 6.2 匹配规则（MVP）

```text
normalize(s) = trim + lowerCase
match = normalize(title).includes(normalize(query))
```

可选轻量增强（仍 P0 可做）：

- 多 token：按空白切分，要求全部 token 命中（AND）。  
- `workspace` 短名也参与匹配（用户可能搜项目名）。

### 6.3 排序（有 query）

1. 标题**前缀**命中优先于中间命中  
2. `pinnedAt` 有值优先  
3. `workspacePath === activeWorkspace` 优先  
4. `updatedAt` 降序  
5. 稳定次序：`id`

### 6.4 排序（空 query）

1. 可选：本会话周期 MRU  
2. `updatedAt` 降序  
3. 默认 `limit = 20`（可配置常量）

### 6.5 归档策略（已确认）

- **MVP 明确不含归档**：只搜 `status: active`（与侧栏主列表一致）。  
- 搜索 API / 前端 filter 均不得默认返回 `archived`。  
- P1 可增加「包含归档」开关；归档结果行用弱化样式 + `Archived` 标记。

### 6.6 性能预算

| 规模 | 策略 |
| --- | --- |
| ≤ 500 条 index | 渲染进程内存过滤即可（先 IPC 拉全量 active meta） |
| 500–5000 | Main 进程 `searchConversations`，只返回 top K（如 50） |
| \> 5000 或要搜正文 | 必须独立索引（P2） |

本地观测：当前约 200+ 条，**P0 走「list + 前端 filter」或「main 端 filter 返回 topK」均可**；推荐直接在 store 加 `searchConversations`，避免把全量 meta 反复丢给 renderer。

---

## 七、技术设计

### 7.1 分层

```text
Renderer
  Sidebar search button / ⌘K
       ↓
  ConversationSearchPalette (新组件)
       ↓ clientApi.conversationsSearch / conversationsList
Preload bridge
       ↓ ipc
Main
  conversationStore.searchConversations(query, opts)
       ↓
  ~/.peer-agent/conversations/index.jsonl
```

### 7.2 Store API 草案

```ts
// packages/conversation-store
searchConversations(params?: {
  query?: string;                 // 空 = 最近列表
  status?: string | string[];     // 默认 ['active']
  workspacePath?: string | null;  // 可选：限制单工作区
  limit?: number;                 // 默认 50
  includeWorkspaceNameMatch?: boolean;
}): ConversationMeta[];
```

实现要点：

- 复用 `listConversations` 读 index。  
- 纯函数 `rankConversation(meta, query, ctx)` 便于单测。  
- **不**在 search 路径读 message 文件。

### 7.3 IPC / clientApi

| 通道 | 说明 |
| --- | --- |
| `conversations:search` | 新 IPC；参数同上 |
| `clientApi.conversationsSearch` | renderer 封装 |

若 P0 极简：也可复用 `conversations:list`（不传 workspace）在 renderer filter——但会破坏「侧栏只拉当前工作区」的隐含约定，且跨层排序难单测。**更推荐正式 search API。**

### 7.4 UI 组件

| 文件（建议） | 职责 |
| --- | --- |
| `apps/desktop/renderer/src/chat/components/ConversationSearchPalette.tsx` | 面板 UI + 键盘 |
| `apps/desktop/renderer/src/styles/conversation-search.css` | 面板样式（token 化） |
| `Sidebar.tsx` | 增加搜索按钮，回调 `onOpenSearch` |
| `App.tsx` | 持有 `searchOpen` state；处理选中后的 workspace + conversation 切换 |

状态归属：

- `searchOpen`：App 级（需快捷键、侧栏、未来 header 共用）。  
- 查询字符串、高亮 index：面板内部 state，关闭即丢（不持久化 query）。

### 7.5 与现有能力边界

| 能力 | 关系 |
| --- | --- |
| `ChatFindBar`（`⌘F`） | **当前线程**消息查找；互不替代 |
| 侧栏列表 | 当前工作区任务索引；搜索是全局补充 |
| `batch_search` / agent 工具 | Agent 搜代码/知识库；与用户 UI 会话搜索无关 |
| Quick Chat 浮窗 | 系统级**新建**入口；搜索是**找回**入口 |
| `Overlay` | 统一模态基座，必须复用 |

### 7.6 工作区显示名解析

```text
workspacePath
  → workspaces 列表中的 name（优先）
  → path.basename(workspacePath)
  → 「未关联工作区」
```

历史数据可能缺 `workspacePath`（本地 index 抽样可见部分记录字段不全）：行内工作区位显示「—」或隐藏，跳转时**不强制切工作区**。

### 7.7 样式与设计语言

- 颜色 / 圆角 / 阴影走 Peer Frost token（`--chrome-raised`、`--shadow-popover` 等）。  
- 动效走 `Overlay` 的 enter-rise / exit-sink，不散写 keyframes。  
- 列表行高度与侧栏会话行接近（约 36–40px），保证信息密度一致。  
- 快捷键徽章样式可参考 `ChatHeader` 菜单 shortcut 或 Codex 灰底小胶囊。

---

## 八、i18n 文案键（草案）

| Key | en | zh |
| --- | --- | --- |
| `searchChats.open` | Search chats | 搜索会话 |
| `searchChats.placeholder` | Search chats | 搜索会话 |
| `searchChats.section.chats` | Chats | 会话 |
| `searchChats.section.suggested` | Suggested | 建议 |
| `searchChats.empty` | No chats found | 未找到相关会话 |
| `searchChats.untitled` | Untitled | 未命名任务 |
| `searchChats.action.newTask` | New task | 新建任务 |
| `searchChats.noWorkspace` | No workspace | 未关联工作区 |

> `searchChats.action.openFolder` 等文案键留到 P1 再补，不进入 MVP 文案表。

---

## 九、产品决策（已确认）

> 2026-07-18 用户确认：S1 选 `⌘K`；S3 不含归档；S5 按建议 P0 仅「新建任务」。其余项沿用默认方案，作为开工基线。

| 编号 | 议题 | 结论 | 状态 |
| --- | --- | --- | --- |
| S1 | 打开面板快捷键 | **`⌘K`** | ✅ 已确认 |
| S2 | 是否与 `⌘F` 线程查找并存 | **并存**（语义不同） | ✅ 默认确认 |
| S3 | MVP 是否含归档 | **不含**，仅 `active` | ✅ 已确认 |
| S4 | 跨工作区跳转是否二次确认 | **不确认，直接切** | ✅ 默认确认 |
| S5 | Suggested 范围 | **P0 仅「新建任务」**（不含打开文件夹 / 归档入口） | ✅ 已确认 |
| S6 | 实现位置 filter | **store.searchConversations** | ✅ 默认确认 |
| S7 | 左栏收起时 header 是否补入口 | **P1** | ✅ 默认确认 |

---

## 十、验收标准（设计落地后可测）

### P0 验收

1. 点击侧栏搜索图标或按 **`⌘K`**，面板打开且输入框聚焦。  
2. 空 query 展示跨工作区最近 **active** 会话，行内可见工作区名；**结果不含归档**。  
3. 输入标题片段，结果实时过滤；大小写不敏感；仍仅 active。  
4. `↓/↑` + `Enter` 可打开会话；`⌘1-9` 对前 9 条生效。  
5. 打开其他工作区会话时，activeWorkspace 与会话一致，主区内容正确。  
6. `Esc` / 点击遮罩关闭；关闭后 `⌘K` 可再次打开。  
7. 与 `⌘F` 线程查找互不抢逻辑（面板关闭时 `⌘F` 仍只开 ChatFindBar）。  
8. Suggested **仅展示「新建任务」**，无「打开文件夹」等次要动作。  
9. 中英文文案完整；typecheck / 相关单测通过。

### 非功能

- 200 条 index 下输入到出结果可感知延迟 **&lt; 50ms**。  
- 不新增对消息 jsonl 的全量扫描。  
- 不引入新的云端依赖。

---

## 十一、实现拆解（供 peer_agent 排期）

1. **Store + 单测**：`searchConversations` + 排序/匹配纯函数测试。  
2. **IPC + preload + clientApi**：`conversations:search` 贯通。  
3. **ConversationSearchPalette UI**：Overlay、列表、键盘、`⌘1-9`。  
4. **App 接线**：打开状态、选中后 workspace/conversation 切换、新建任务动作。  
5. **Sidebar 入口 + 快捷键 + i18n + 样式**。  
6. **回归**：当前工作区侧栏列表行为不变；归档/置顶/删除不受影响；左栏收起仅快捷键可用。

---

## 十二、风险与开放问题

1. **历史数据缺 `workspacePath`**：跨工作区展示与跳转降级策略需在实现时打日志或兼容。  
2. **快捷键冲突**：`⌘K` 是否与浏览器/系统或未来 Command Palette 冲突；应走可配置 shortcuts（可复用 `shortcut-service` 模式，P1）。  
3. **「搜索」心智膨胀**：用户可能期望搜消息内容；MVP 需在空状态或无结果文案中降低预期（「按标题搜索会话」）。  
4. **多窗口**：若未来多 window 共用 store，search 只读 index 仍然安全；写路径仍靠现有 change 订阅。

---

## 十三、结论

Peer Agent 应补齐与 Codex 同级的 **Search chats** 能力：以**本地会话索引 + 居中快速面板 + 跨工作区标题搜索 + 键盘优先**为第一性原理。

- **产品形态**：任务索引快速切换器，而不是通用命令板或全文搜索。  
- **工程路径**：`conversation-store.searchConversations` → IPC → `ConversationSearchPalette`（Overlay）→ App 统一跳转。  
- **交付策略**：P0 对齐截图 80% 体验；正文搜索与 Command Palette 明确后置，避免 scope 膨胀。  
- **已锁定决策**：快捷键 `⌘K`；MVP 不含归档；Suggested 仅「新建任务」。

§九 决策已确认，可在 `peer_agent` 按 §十一 开工。
