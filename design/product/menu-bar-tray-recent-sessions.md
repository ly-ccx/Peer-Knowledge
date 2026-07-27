# 菜单栏托盘 · 近期会话入口产品方案

创建时间：2026-07-27  
最后更新：2026-07-27  
状态：Draft（设计文档，未进入代码实现）

关联文档：

- `design/product/status-bar-task-center.md`（状态栏任务中心：任务状态投影、数字角标、自定义 Popover；与本方案共享菜单栏槽位但信息对象不同）
- `design/product/quick-chat-floating-window.md`（Quick Chat：轻量输入与回流）
- `design/product/task-completion-system-notification.md`（任务完成系统通知：推送、去重、点击回流）

---

## 一、方案摘要

Peer Agent Desktop 在 macOS 菜单栏（Tray）常驻一个图标。用户点击后弹出**系统原生菜单**，以 **Recent 近期会话** 为核心，提供「不打开侧边栏也能跳到最近工作」的快速入口。

参考对象：Codex / ChatGPT Desktop 的菜单栏菜单（Recent 列表 + More + New Chat + Open + Quit）。

一句话定义：

> 菜单栏托盘近期会话入口是「会话级快速跳转与应用生命周期入口」，不是任务中心，也不是迷你主窗口。

MVP 推荐：

- **形态**：Electron `Tray` + 原生 `Menu`（不用自定义 HTML 浮层）
- **内容**：Recent（默认 5 条）→ More →（可选 Running 一行）→ New Chat / Open Peer Agent / Quit
- **图标**：macOS Template Image 单色剪影；当前仓内**无专用 Tray 素材**，需补齐

---

## 二、为什么单独写这份文档

仓库里已有《macOS 状态栏任务中心》方案，解决的是：

- 有没有任务在跑？
- 有多少需要我处理 / 未读结果？
- 点一下回到对应 Goal / 任务卡

而用户本次明确要对齐的 Codex 截图解决的是：

- 最近聊过哪些会话？
- 点一下打开某个会话继续聊
- 新建会话 / 打开主应用 / 退出

两者都落在「菜单栏图标」上，但：

| 维度 | 本方案：近期会话 Tray | 任务中心方案 |
|---|---|---|
| 信息对象 | Conversation（会话） | Task Item（任务卡 / Goal 投影） |
| 交互形态 | 系统原生 Menu | 自定义 Popover 面板 |
| 主问题 | 「我去哪」 | 「现在怎样 / 要不要我管」 |
| 图标语义 | 品牌常驻入口 | 最高优先级任务状态 + 数字 |
| MVP 复杂度 | 低（复用会话列表即可） | 高（统一任务投影 + 已读模型） |

**产品决策（本文件生效口径）：**

1. **P0 先做 Codex 形态的近期会话原生菜单**，尽快提供可用的菜单栏价值。
2. 任务中心方案保留为 **P1/P2 演进方向**，不在同一 MVP 里把任务 Popover 与 Recent 菜单混成一套半成品。
3. **物理上只占一个菜单栏图标**；后续若上任务中心，优先「同一 Tray 槽位演进交互」，而不是并排两个 Peer 图标。

---

## 三、背景与现状

### 3.1 用户问题

- 主窗口被盖住或不在前台时，想快速回到最近几个会话。
- 不想先找 Dock、再找侧边栏、再点会话。
- 需要一个始终可达的「Peer 在」的系统级入口（含 New Chat / Quit）。

### 3.2 代码仓能力快照（`peer_agent`，设计时点）

| 能力 | 状态 |
|---|---|
| Electron `Tray` 常驻 | **未实现** |
| 应用菜单 `app-menu.mjs` | 已有（编辑/视图/窗口等） |
| Dock 图标深浅色切换 | 已有（`dock-icon-paths.mjs` + `icon-macos-dock*.png`） |
| 会话列表 | 主进程已有 `conversations:list` / conversation store |
| 从通知打开会话 | 已有任务通知回流路径，可复用「show 窗口 + 打开 conversationId」 |
| Tray Template 专用图标 | **缺失** |

### 3.3 已有图标素材（≠ Tray 专用）

代码仓 `apps/desktop/`：

| 路径 | 尺寸/形态 | 用途 |
|---|---|---|
| `build/icon.png` | 1024 彩色 | 通用 App Icon |
| `build/icon-macos-dock.png` / `icon-macos-dock-dark.png` | 1024 | Dock |
| `build/icon.icns` / `icon.ico` | 安装包 | 打包 |
| `public/logo.png` / `logo-light.png` / `logo-dark.png` | 256 | 应用内 UI |
| `public/favicon*.png` | 64 | Web/favicon |

知识库预览：

- `design/visual/previews/logo.png` / `logo-light.png` / `logo-dark.png` / `favicon.png`

**结论：有品牌与 Dock 素材；没有菜单栏 Template Image（建议文件名含 `Template`）。**

---

## 四、产品目标与非目标

### 4.1 目标

1. **常驻可达**：应用运行期间菜单栏始终有 Peer 图标（主窗口关闭后仍可保留进程与 Tray，与任务中心文档「关窗不退出」一致）。
2. **一眼跳转**：打开菜单即可看到最近会话，点击直达对应会话。
3. **生命周期完整**：支持 New Chat、打开主窗口、退出应用。
4. **系统一致**：优先原生 Menu，减少自定义浮层带来的焦点/暗色/无障碍成本。
5. **边界清晰**：不与任务中心、Quick Chat、系统通知抢同一信息架构。

### 4.2 非目标（MVP 不做）

- 在菜单里展示完整消息气泡、Markdown、工具调用流
- 在菜单里编辑 Goal、批准高风险操作、改设置大表单
- 自定义 HTML Tray 面板（第二期再评估）
- 并排第二个菜单栏图标专门做任务中心
- 跨设备同步 Recent 列表
- 把每条 assistant 消息当成 Recent 项

---

## 五、与周边能力的边界

```text
                    ┌─────────────────────────┐
                    │   菜单栏图标（唯一槽位）   │
                    └───────────┬─────────────┘
                                │
              P0 点击 ──────────┼────────── 后续演进
                                │
                                ▼
                    ┌─────────────────────────┐
                    │ 原生 Menu：Recent 会话   │  ← 本方案
                    └─────────────────────────┘

系统通知 ──点击──► 主窗口定位会话/任务     （推送，非常驻）
Quick Chat ──────► 轻量输入浮层           （主动唤起写作）
主窗口侧边栏 ────► 完整会话列表与搜索       （完整管理）
任务中心 Popover ► 执行中/待处理/未读任务  （状态投影，后续）
```

### 5.1 vs 状态栏任务中心

- **任务中心**：对象是任务卡；关心 running / waiting_user / unread。
- **本方案**：对象是会话；关心最近打开/更新的 conversation。
- Running 一行（可选）只做「有 N 个任务在跑」的弱提示，点击建议打开主窗口任务视图或当前活跃任务会话；**不在本 MVP 复制任务中心分组面板**。

### 5.2 vs Quick Chat

- Quick Chat：快速输入、轻会话、任务卡回流。
- Tray New Chat：创建（或打开）主窗口会话输入，不默认再开一套浮层。
- 空 Recent 时菜单可提供 New Chat，不必强绑 Quick Chat。

### 5.3 vs 系统通知

- 通知：事件驱动、可消失、需权限。
- Tray：常驻入口；不替代完成通知，也不在每次 token 流式输出时闪图标（MVP）。

### 5.4 vs Dock

- Dock：应用切换与窗口恢复。
- Tray：会话级快捷列表 + 关主窗后仍可达。
- Dock 图标继续用现有彩色/深浅色资源；Tray 必须用 Template，两套资源分离。

---

## 六、信息架构（对齐 Codex）

### 6.1 菜单结构（MVP）

```text
Recent                         ← 分组标题（disabled label）
  排查第 9 个任务崩溃 (3)        ← 主标题：会话 title
  peer_agent                     ← 副标题：workspace 短名
  为什么同一个会话 tui 的上下文…
  peer-knowledge
  …
More ›                         ← 打开主窗并聚焦会话列表
────────────────────────────────
Running · 1 task               ← 可选；无运行任务时整行隐藏
────────────────────────────────
New Chat
Open Peer Agent
────────────────────────────────
Quit Peer Agent
```

说明：

- Codex 截图中的 **Usage** 区块（Weekly xx%）Peer **MVP 不做**；若后续有本地用量统计，再以一行文案形式加入，不做图表。
- 文案默认中英可配置；实现阶段跟随应用语言包。设计示意可用中文产品语：

| 英文示意（对照 Codex） | 中文产品语（建议） |
|---|---|
| Recent | 最近会话 |
| More | 更多 |
| New Chat | 新会话 |
| Open ChatGPT / Open Peer Agent | 打开 Peer Agent |
| Quit | 退出 Peer Agent |
| Running · N task(s) | 进行中 · N 个任务 |

### 6.2 Recent 每一项

| 行 | 内容 | 规则 |
|---|---|---|
| 主标题 | `conversation.title` | 空则回退「首条用户消息摘要」→ `新会话`；超长截断约 36 字（按显示宽度近似） |
| 副标题 | workspace 短名 | `path.basename(workspacePath)`；无工作区则隐藏副标题或显示 `未关联工作区` |
| 排序 | 最近活动优先 | `updatedAt` / `lastMessageAt` 降序（与侧边栏「最近」一致，避免两套排序） |
| 数量 | 默认 5，硬顶 8 | 超过走 More，不在菜单无限拉长 |
| 当前会话 | 可选标记 | MVP 可用 `✓` 前缀或系统 `checked`；不做复杂样式 |

同一 `conversationId` 只出现一次。已删除会话不得出现。

### 6.3 点击行为

**点击 Recent 项：**

1. 显示并 focus 主窗口（若无则创建）
2. 切换到会话所属工作区（若模型需要）
3. 打开对应 `conversationId`
4. 关闭菜单（系统菜单自动关闭）

会话已删除或工作区失效：

- 打开主窗口并给出可理解错误（toast / 空态）
- 刷新 Tray 菜单，移除失效项

**More：**

- 打开主窗口 + 聚焦左侧会话列表（或会话搜索入口，若已存在）
- 不在菜单内展开二级「全部会话」长列表（MVP）

**New Chat：**

- 打开主窗口
- 创建新会话并 focus 输入框
- 工作区：沿用「当前活跃工作区」策略；无则走应用既有新建流程

**Open Peer Agent：**

- 仅 show/focus 主窗口，不强制切换会话、不清任何未读

**Running（可选 P1）：**

- 有运行中任务时显示摘要一行
- 点击：优先跳到「当前最相关」任务会话；多任务时打开主窗口任务/Goal 视图

**Quit Peer Agent：**

- 正常退出应用（销毁 Tray、结束主进程）
- 与「关闭主窗口 ≠ 退出」区分：Quit 才是退出

### 6.4 空状态

无会话时：

```text
Recent
  暂无会话                    ← disabled 说明行
────────────────────────────────
New Chat
Open Peer Agent
────────────────────────────────
Quit Peer Agent
```

不展示空的 More（或 More 仍可进主窗空列表，二选一；推荐 **保留 More**，降低结构跳动）。

### 6.5 刷新时机

- 用户打开菜单前 / 即将展示时拉取最近 N 条（避免常驻高频轮询）
- 会话创建、重命名、删除、切换工作区后主动重建 `contextMenu`
- 不在 token 流式输出时每帧刷新菜单

---

## 七、Tray 图标规格与素材缺口

### 7.1 结论

| 问题 | 答案 |
|---|---|
| 现在有顶部小 logo 素材吗？ | **有品牌/Dock/UI logo；无菜单栏 Template 专用素材** |
| MVP 能否先跑通？ | 能：临时用 favicon/logo 降采样灰度；**发版前必须换正式 Template** |

### 7.2 macOS Template Image 规范

建议新增（代码仓路径，实现时落地）：

```text
apps/desktop/build/trayTemplate.png       # 建议 16×16 或 32×32 源图按 16pt 显示
apps/desktop/build/diana.k@example.org     # 32×32（@2x）
```

可选 Windows：

```text
apps/desktop/build/tray-win.png           # 16/32 彩色可接受
apps/desktop/build/emma.t@example.net
```

**视觉要求：**

1. **纯黑图形 + 透明背景**（不要彩色 App Icon、不要灰底）
2. 文件名包含 `Template`，便于 `nativeImage` / 系统按菜单栏外观自动反色
3. 图形为 Peer logo **单色剪影**：减少细线与镂空，16pt 下可辨
4. 四周留安全边距，避免贴边被裁切
5. 与 Dock 彩色图标同源造型，但细节级别更低

### 7.3 与 Dock 图标关系

- Dock：`icon-macos-dock.png` / `dark` 彩色，可随外观切换
- Tray：Template 自动适配深浅菜单栏，**一般不需要**再维护 light/dark 两套彩色 Tray
- 解析方式可仿 `dock-icon-paths.mjs` 增加 `resolveTrayIconPath`

### 7.4 开发期临时策略

优先级：

1. 正式 `trayTemplate.png` + `@2x`（目标态）
2. 若缺失：从 `public/favicon.png` 或 `logo.png` 生成临时 template（仅 dev / 内部包）
3. 禁止直接把 1024 彩色 `icon.png` 不经处理塞进菜单栏作为发版默认

### 7.5 设计交付清单（给视觉）

- [ ] `trayTemplate.png`（@1x）
- [ ] `diana.k@example.org`（@2x）
- [ ] 可选：运行中/待处理等**状态变体**（若未来任务中心合并进同一图标；本 MVP 可不做）
- [ ] 导出说明：描边粗细、安全区、与 logo 主识别形一致

---

## 八、交互与平台细节

### 8.1 macOS

- 左键：弹出 context menu（Recent 菜单）
- `setIgnoreDoubleClickEvents(true)`，避免双击吞事件
- 右键：MVP 与左键相同；后续可扩展「仅 Quit / 设置」精简菜单
- 主窗口关闭：默认隐藏窗口、保留 Tray 与后台能力（与任务中心文档一致）
- 菜单打开时不要抢系统焦点到主窗口，直到用户点了需要打开窗口的项

### 8.2 Windows（非 MVP 重点，预留）

- 托盘图标可彩色
- 左键/右键习惯与 macOS 可能不同：常见右键菜单、左键打开主窗口
- 文案与项结构保持一致，平台差异写在实现说明而非产品信息架构里分叉

### 8.3 可访问性与文案

- Tray `setToolTip('Peer Agent')`
- 菜单项避免纯图标无文字
- 截断标题仍应尽量保留语义头部

---

## 九、实现要点（设计约束，非本仓库改代码）

> 代码一律在 `peer_agent` 落地；此处只约束设计可实现性。

建议主进程模块（示意命名）：

- `tray-controller.mjs`：创建/销毁 Tray、重建菜单、响应点击
- `resolveTrayIconPath`：packaged / dev 路径
- 数据：`listConversations` 取最近 N 条（可不带 messageCount）
- 打开会话：复用现有 notification → open conversation 回流链路
- 生命周期：`app.whenReady` 后创建；`before-quit` / `will-quit` 销毁

伪结构：

```text
app ready
  → create Tray(templateImage)
  → buildContextMenu(recent[])
  → on conversation changed → rebuild menu (debounce)
  → on menu item click → showMainWindow + openConversation / createConversation / quit
```

**不要**在 renderer 里各写一套 Tray 状态；Tray 属于主进程壳层能力。

---

## 十、分阶段范围

### 10.1 P0（MVP，对齐 Codex 主路径）

1. macOS 菜单栏常驻 Tray 图标（Template 或明确标注的临时图）
2. Recent 最多 5 条：标题 + workspace 副标题
3. More / New Chat / Open Peer Agent / Quit
4. 点击会话正确回流到主窗口对应会话
5. 关主窗口后 Tray 仍在；Quit 才退出
6. 菜单打开时数据为近期有效会话

### 10.2 P1

1. 正式 Tray Template 双倍图发版默认
2. Running 一行弱提示
3. 当前会话 checked 态
4. 会话改名/删除后菜单即时一致
5. Windows 托盘基础支持

### 10.3 P2

1. 评估与《状态栏任务中心》合并：同一图标下「任务态图标/数字 + 点击策略」
2. 自定义 Popover（仅当原生 Menu 无法承载任务分组时）
3. Usage / 本地用量一行
4. More 二级菜单展示更长 Recent（仍建议优先回主窗）

### 10.4 明确不做（除非单独立项）

- 菜单内完整聊天
- 双图标并排（Peer 会话 + Peer 任务）
- 用 Tray 替代系统通知权限与完成推送

---

## 十一、产品验收标准

### 11.1 图标

1. 启动应用后，菜单栏出现 Peer 图标。
2. 深色/浅色菜单栏下图标仍可辨（Template 自动反色）。
3. Tooltip 为 Peer Agent（或产品最终名）。

### 11.2 Recent 信息架构

1. 菜单含 **Recent** 分组与至少「New Chat / Open / Quit」操作项。
2. 存在 ≥3 个会话时，菜单展示按最近活动排序的条目，默认不超过 5 条主列表项。
3. 每条可见主标题；有工作区时可见副标题短名。
4. 点击某会话后，主窗口前置并打开该 `conversationId`。
5. 点击 New Chat 后，主窗口前置并进入可输入的新会话。
6. 点击 Open 仅前置主窗口，不错误跳到无关会话（保持当前会话或应用既定默认）。
7. 点击 Quit 后应用退出，菜单栏图标消失。

### 11.3 边界

1. 关闭主窗口后图标仍在，再次 Open 或点会话可恢复窗口。
2. 删除某会话后，再次打开菜单不再出现该项。
3. 无会话时菜单不崩溃，仍可 New Chat / Open / Quit。

### 11.4 素材

1. 设计/发版清单中存在 `trayTemplate`（及 @2x）或文档明确记录临时图与替换项。
2. 发版路径不依赖未说明的 1024 彩色 icon 直缩小。

---

## 十二、风险与开放问题

| 风险 | 说明 | 缓解 |
|---|---|---|
| 与任务中心方案「抢」同一图标语义 | 用户可能期望点开是任务面板 | 本文规定 P0=Recent；任务中心合并进 P2，并在任务中心文档交叉引用 |
| 原生 Menu 表现力有限 | 难做多行富文本、进度条 | 接受 Codex 级信息密度；复杂状态走主窗/未来 Popover |
| 临时图标发版事故 | 灰糊/彩色块 | 验收卡 Template；CI 或打包检查可选 |
| Recent 排序与侧边栏不一致 | 用户认知分裂 | 共用同一「最近活动」字段与排序函数 |
| 多窗口/多工作区 | 打开会话时工作区上下文错误 | 回流逻辑必须带 workspace + conversationId |

**开放问题（不阻塞 P0 文档）：**

1. 后续任务中心上线时：单击 = 任务 Popover，右键 = Recent 菜单？还是一级菜单顶部嵌「任务摘要」？
2. New Chat 是否应可选打开 Quick Chat 而非主窗口？（默认否）
3. More 是聚焦侧边栏还是打开会话搜索 palette？

---

## 十三、建议实现顺序（供代码仓排期）

1. 补 `trayTemplate.png` / `@2x`（或 dev 临时生成脚本）
2. 主进程 `Tray` 创建 + Quit/Open/New Chat
3. 接入 `listConversations` 填充 Recent + 点击回流
4. More 与空态
5. （P1）Running 行、Windows、与 conversation 变更事件联动

---

## 十四、文档维护

- 本文件只描述**产品设计与边界**；实现细节以 `peer_agent` 代码与其 `AGENTS.md` 工程规范为准。
- 若任务中心先行或合并策略变更，应同步更新：
  - 本文 §二、§五、§十
  - `design/product/status-bar-task-center.md` 关联文档与「菜单栏交互」相关章节
