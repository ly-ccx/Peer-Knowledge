# Composer `@` 上下文选择器：从「只能选会话」补到「可钉上下文」

创建时间：2026-08-15
最后更新：2026-08-15
状态：设计草案（可评审；未在代码仓落地）
关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）
关联实现：
- `apps/desktop/renderer/src/chat/components/ComposerDraftControls.tsx`
- `apps/desktop/renderer/src/chat/state/sessionReference.ts`
- `apps/desktop/renderer/src/chat/state/attachmentIntake.ts`
- `apps/desktop/renderer/src/chat/state/contextSources.ts`
- `packages/protocol/src/system-context.ts`
关联文档：
- `design/product/tui-interaction-design.md`（TUI 已规定 `@` 引用文件/目录/已配置上下文）
- `design/product/conversation-search-palette.md`（`⌘K` 搜任务并跳转，不是往本轮挂上下文）
- `design/product/workbench-file-preview-rendering.md`（Workbench 预览文件，不是 Composer 引用）
- `knowledge/specifications/14-product-design-language.md`（Composer 是指令台）
- `design/product/task-identity-conversation-carrier.md`（`@` 停在会话层是身份泄漏；Goal / Thread 引用放到 P2，只钉标题 + id）

---

## 一、问题

Cursor 的 `@` 是一个混合选择器：空查询先给能力项（Branch / Browser / Chats），输入后立刻变成工作区文件模糊搜索。Peer Desktop 的 `@` 现在只做一件事——搜其他会话，选中后把整段对话压成文本附件发出去。

用户体感就是：对面一个 `@` 能钉很多东西，我们只能选会话。

这不是「菜单少两项」的表面问题，而是 Composer 缺一条统一的「用户主动钉上下文」入口。能力其实散落在别处：

| 入口 | 现在做什么 | 不是什么 |
| --- | --- | --- |
| `@` | 只搜会话，内联整段 transcript | 不是文件/目录/diff 选择器 |
| `+` | 系统文件选择器，走附件 intake | 不是工作区路径搜索 |
| `/` | 产品命令（help / compact 等） | 不是上下文 |
| 拖拽 / 粘贴 | 同样走附件 intake | 没有路径语义 |
| `⌘K` 搜索面板 | 跨工作区打开任务 | 不把内容挂到本轮 |
| Workbench Files | 预览本地文件 | 不进入本轮上下文 |
| Agent 工具 `read_file` / `search_files` | 模型自己去找 | 用户无法先指定 |

TUI 设计口径已经写过：`@` 用来「引用文件/目录/已配置上下文」。Desktop 实现和这份口径是反的。

---

## 二、不要照抄 Cursor

截图里 Cursor 把三类完全不同的东西塞进同一个 `@`：

1. **钉事实**：文件、目录、Chats、当前 branch diff
2. **开能力**：`Browser · Enable browser tools`
3. **搜全盘**：连 `/Applications/Cursor.app`、端口号目录都会出来

Peer 不该抄这个大杂烩。

- Peer 是本地 Agent 工作台，不是 IDE。模型已经能自己读工作区；`@` 的价值是用户**先指定**，不是再做一个迷你资源管理器。
- System Context 已有治理：附件是 user/factual，生命周期 ephemeral，不得提升成 system 指令。`sessionReference.ts` 也写明了：只装配，不另开执行路径。
- `/` 已经是命令入口，`+` 已经是「从磁盘上传」。再把「启用 Browser」塞进 `@`，三个入口会抢语义。
- 不要索引家目录、`/Applications`、任意绝对路径。默认只搜当前 workspace，尊重 gitignore / 权限边界。

一句话：**`@` 只负责「把用户点名的对象钉进本轮」；开工具、切模式、跑命令都不进这个菜单。**

---

## 三、三个入口怎么分

```text
+   上传磁盘上的文件（工作区外、图片、用户手里的材料）
@   钉工作区 / 会话里已有的对象（路径、会话、bounded diff）
/   指挥产品自己（compact、help、mode…）
```

判断口诀：

- 东西在当前工作区或 Peer 会话库里 → `@`
- 东西在工作区外、剪贴板、系统对话框 → `+` / 粘贴
- 要改产品状态或跑元命令 → `/` 或设置，不进 `@`

「启用 Browser」属于能力开关，应继续走工具投影 / 设置 / 既有 Browser 面板，不进 `@`。

---

## 四、选中之后到底发生什么

这是比菜单更重要的一层。Cursor 大量 `@file` 只是把路径写进提示词，再让模型自己读。Peer 现在的会话 `@` 则是**立刻内联全文**。两种语义必须分开，不能所有 hit 都压成 `ChatAttachment(kind=text)`。

| 对象 | 草稿里留下什么 | 发给模型的是什么 | 为什么 |
| --- | --- | --- | --- |
| 工作区文件 | `@src/foo.ts` | **路径引用**为主；小文本可内联，超限只留元数据 | Agent 已有 `read_file`，整文件内联会迅速打满 context |
| 工作区目录 | `@src/chat/` | **目录清单 + 路径**，禁止递归倒全文 | 倒树等于攻击自己的 token |
| 其他会话 | `@会话标题` | **bounded transcript 附件**（保持现有链路） | 模型没有稳定的「读另一会话」工具 |
| 当前 branch diff | `@branch` | **有上限的 diff 文本** | 这是用户明确点名的变更集，适合当轮事实 |
| 磁盘上传（`+`） | 附件 chip，不一定有 `@` | 现有 intake：图走多模态，文本内联，不支持的只留元数据 | 语义没变 |

装配原则（沿用现有，不新开发送路径）：

1. 草稿里插入 mention token，方便人看、也方便模型看见用户点名了谁。
2. 真正进模型的内容走既有 `ChatAttachment` → `buildAttachmentText` / `contextAttachments`。
3. `sourceKind` 必须分源，不要再全部写成 `user_upload`：
   - 会话：`session_reference`
   - 工作区文件/目录：`workspace_file` / `workspace_dir`
   - branch diff：`git_diff`
   - `+` / 拖拽：继续 `user_upload`
4. 一律 `lifecycle=ephemeral`，不提升为 system 指令。
5. 单轮仍受 `MAX_ATTACHMENTS`（现 8）和文本/图片体积上限约束。

协议已经预留了 `ContextAttachmentSourceKind` 的扩展位（`user_upload | clipboard | skill | memory | hook | mcp | runtime | string`），补枚举即可，不必另起 Context Source。

---

## 五、菜单信息架构

空 `@`（还没打字）先给**类别**，不要直接倒 200 个文件：

```text
@
────────────────────────────────
  Files     搜索当前工作区文件
  Chats  ›  引用另一段会话
  Branch    钉上当前分支相对默认分支的 diff   （仅 git 工作区）
────────────────────────────────
  最近在 Workbench 打开过的 3～5 个文件
```

开始输入后变成**统一搜索**：

```text
@Composer
────────────────────────────────
  TS  ComposerDraftControls.tsx    apps/desktop/renderer/src/chat/…
  TS  composerPersistence.ts       apps/desktop/renderer/src/chat/…
  会话  Compact composer draft      2 小时前
```

排序建议：

1. 工作区路径（文件名精确 / 前缀 / 模糊）
2. 最近打开的文件
3. 会话标题
4. 类别动作（Files / Chats / Branch）只在 query 很短或能匹配类别名时保留

交互沿用现有 session mention 弹层，不要新造一套视觉：

- 上下键、Tab / Enter 选中，Esc 关闭
- 点 `Chats ›` 进入现有会话列表（就是今天的 `@` 菜单）
- 选中后：替换当前 `@query` 为 mention，并触发对应装配
- 与 `/` 互斥：光标前是 slash query 时只出命令菜单

`+` 继续只做系统文件选择器。不要让 `@` 再弹一次原生 Open Dialog——那是 `+` 的活。

---

## 六、分阶段补，不一次做完 Cursor 菜单

### P0 — 先把 `@` 变成「文件 + 会话」

目标：用户打 `@` 的第一反应从「只能找会话」变成「先找这个工作区里的东西」。

要做：

1. 把 `sessionReference.ts` 里的 `detectAtQuery` 留作通用 `@query` 检测，菜单数据源改成 provider 列表，而不是写死 `conversationsSearch`。
2. 新增工作区文件搜索口（renderer 不要自己扫盘）：
   - 范围：当前 `workspacePath`
   - 尊重 gitignore / 现有 file-access 权限
   - 返回相对路径、文件名、类型；上限约 20 条
   - 现成能力：`fs:read-dir`、`file:read`、Agent 侧 ripgrep。UI 需要一条**短、可取消、workspace-scoped** 的搜索 IPC，不要把 `search_files` 工具直接暴露给输入框。
3. 选中文件：
   - 草稿写入 `@rel/path`
   - 默认**不内联全文**，附件只带路径 / 名称 / mime / size（可复用今天 `unsupported` 的「元数据 + Agent 自行读取」策略）
   - 小于现有 `MAX_TEXT_BYTES` 的文本，可选择内联；超限绝倒全文
4. 会话保持今天的行为，只是降到 `Chats ›` 和第二排序。
5. 空查询展示 Files / Chats 两个类别 + 最近文件（最近文件可先空着，不阻塞）。

验收：

- `@` 空查询不再只有会话列表
- `@Composer` 能打出工作区里的 `ComposerDraftControls.tsx`
- 选中文件后，消息里看得到路径 mention；模型能据此 `read_file`，而不是吃到整份文件
- `@某会话标题` 仍能挂上 transcript 附件
- TUI / Desktop 口径一致：`@` = 引用，不再各说各话

### P1 — Branch、目录、最近文件

- **Branch**：仅 git 工作区显示。选中后调用已有 `git:diff`，对默认分支（`main`/`master`/上游）做 bounded diff；超限截断并注明。
- **目录**：选中文件夹只附带一层 listing + 路径。
- **最近文件**：复用 Workbench 打开记录；没有记录就隐藏这一段，不要假数据。
- 弹层样式从 `session-mention-*` 升成通用 `context-mention-*`，会话只是其中一类。

### P2 — 命名上下文，仍然克制

只加「用户能理解、且已有事实源」的对象：

- 当前 Goal / Plan（只钉标题 + planId，不把整份 runner 状态塞进 prompt）
- `AGENTS.md` / 已配置 skill 文档（当作 workspace 文件的快捷方式）
- 剪贴板文本（若已有 clipboard sourceKind）

明确不做：

- `@` 里开关 Browser / MCP / Skill
- 索引工作区以外的机器路径
- 把整个 repo、整个 node_modules、整个会话库一次性挂上
- 用 `@` 取代 `+` 或 `/`

---

## 七、和现有链路怎么接

```text
detectAtQuery(draft)
        │
        ▼
 ContextPicker providers
   ├─ workspace.files     （P0，新）
   ├─ conversations       （现有 conversationsSearch）
   ├─ git.branchDiff      （P1，复用 git:diff）
   └─ recents             （P1）
        │
        ▼
 onPick(hit)
   ├─ insertMention(draft)          人看得见
   └─ assembleAttachment(hit)       进既有 attachments[]
        │
        ▼
 ChatSurface 发送
   └─ contextSources.mapAttachments
        sourceKind = session_reference | workspace_file | git_diff | user_upload
```

代码落点（实现阶段，不在本文改代码）：

| 层 | 动哪里 | 不要动哪里 |
| --- | --- | --- |
| 检测 | 把 `detectAtQuery` 留在通用 module，会话装配留下 | 不要让检测函数继续叫「只用于会话」却被文件复用而不改名 |
| UI | `ComposerDraftControls` 的 mention 弹层改成多 provider | 不要和 slash menu 合并 |
| 搜索 | main 进程新增 workspace file search | 不要在 renderer 里 `readdir` 全盘 |
| 发送 | 继续 `setAttachments` + `contextSources` | 不要另开 system prompt 拼接 |
| TUI | 同一套 provider 语义 | 不要 Desktop 钉文件、TUI 钉会话各玩各的 |

风险：

- 文件搜索若做成全树扫描，输入一个字就会卡。必须可取消、debounce、限制遍历深度/结果数。
- 会话全文 + 多个内联文件会把当轮上下文打爆。P0 文件默认路径引用，就是为了堵住这条。
- mention 只是纯文本 `@foo.ts`，没有 chip 协议；重名文件靠相对路径消歧，不在 P0 做富文本 token。

---

## 八、和 Cursor 菜单的对照（我们补什么、故意不补什么）

| Cursor `@` | Peer 怎么处理 | 阶段 |
| --- | --- | --- |
| 文件模糊搜索 | 当前工作区文件搜索，路径引用为主 | P0 |
| Chats › | 保留，降为类别，不删 | P0 |
| 目录 `0 /`、`src /` | 目录 listing，不倒全文 | P1 |
| Branch diff | git 工作区才出现，bounded diff | P1 |
| Browser · Enable tools | **不进 `@`**，继续走工具/设置 | 不做 |
| 工作区外的应用路径、奇怪绝对路径 | **不索引** | 不做 |
| Docs / 规则 / Notepad 等 IDE 资产 | 仅当 Peer 已有对应事实源再加 | P2 视情况 |

---

## 九、成功标准

用户可感知：

1. 在 Desktop Composer 敲 `@`，第一屏不再只有会话。
2. 再敲几个字母，能选中当前工作区文件，草稿出现 `@相对路径`。
3. 仍能从 `Chats` 或搜索结果里钉另一段会话。
4. `+` 上传、`/` 命令、Browser 工具开关都不被这次改动吞并。

工程可验收：

1. 文件 mention 走附件链路，且 `sourceKind` 不是 `user_upload`。
2. 大文件 / 目录不会被整份内联。
3. 文件搜索失败或无工作区时，菜单降级为现有会话列表，而不是空白死菜单。
4. 现有 session mention 单测与附件上限单测继续绿。

---

## 十、建议的实现顺序（代码仓）

1. 先改协议与装配：给 attachment 补 `sourceKind`，会话引用改名，不改 UI。
2. 再改 picker 数据源：空 `@` 出 Files / Chats，输入后混排。
3. 接 workspace file search IPC。
4. 最后才做 Branch / 目录 / 最近文件。

先把「`@` = 钉对象」这条产品合同立住，再往里加品类。菜单堆得越像 Cursor，越容易把能力开关和事实引用混在一起——那正是我们要避开的。
