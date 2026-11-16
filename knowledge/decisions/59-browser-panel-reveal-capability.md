# 59. Browser 面板主动打开与可见工作现场闭环

创建时间：2026-08-03
最后更新：2026-11-15（补充重号消歧说明，并标注受 ADR 66 / 72 / 85 / 109 收窄的适用范围）

> [!NOTE] 重号消歧
> 历史并发编写导致编号 `59` 同时对应 [59-browser-panel-reveal-capability.md](59-browser-panel-reveal-capability.md)（本篇，Browser 面板主动打开与可见工作现场闭环）与 [59-appshots-capability-boundary.md](59-appshots-capability-boundary.md)（Appshots 能力边界）。外部引用 `ADR 59` 时必须附带完整文件名以免混指。

## 状态

Accepted，进入实现。

本决策新增 `local.web.control.openPanel` capability、`browser_open_panel` 工具，以及 Main 与 Renderer 之间的 Browser Workbench reveal/ack 通道。它改变能力暴露、跨进程契约和可见 Browser 工具的前置条件，属于 A 级变更。

## 背景

ADR 40 建立了用户可见 `<webview>` 与 Agent 直控 WebContents 的能力；ADR 46 进一步把 Workbench 展开状态、BrowserSession、活跃网页标签和 Agent 目标绑定到 Conversation。当前五个可见浏览器工具为：

- `browser_navigate`
- `browser_click`
- `browser_type`
- `browser_screenshot`
- `browser_read_dom`

它们都依赖当前 Conversation 已经存在并注册活跃 Browser WebContents。Renderer 目前会在聊天流收到 `browser_*` tool-call 事件后，被动执行 `setWorkbenchOpen(true)` 与 `setActiveTab('browser')`。Provider 也预留了 `ensureBrowserReady` seam，并会等待 Browser Control Registry 出现同会话条目。

但生产环境没有向 Provider 注入真正的宿主 reveal 能力。因此存在闭环缺口：

```text
Agent 调用 browser_navigate
  -> Browser 面板未打开 / BrowserView 未注册 WebContents
  -> Provider 等待 Registry
  -> Renderer reveal 依赖聊天事件时序或根本没有对应事件
  -> no_active_browser / browser_unavailable
  -> 只能让用户手工打开面板，或错误退回系统浏览器
```

这违反“模型负责认知、本地负责能力、界面负责表达、契约负责边界、证据负责治理”：模型已经表达了可见导航意图，本地宿主却无法建立承载该能力的工作现场。

## 决策

### 一、增加显式 `browser_open_panel` 工具

新增正式能力链：

```text
Capability Provider(local.web.control)
  -> Manifest(local.web.control.openPanel)
    -> Runtime Projection
      -> Tool Call(browser_open_panel)
        -> PermissionGrant
          -> Evidence
```

工具语义是幂等的 **ensure visible**，不是 UI toggle：

1. 目标必须来自 Tool Context 的当前 `conversationId`；
2. 幂等展开该 Conversation 的 Workbench；
3. 幂等切换到 Workbench `Browser` capability；
4. 复用该 Conversation 的 BrowserSession 与活跃 BrowserTab；
5. BrowserSession 没有标签时，由既有 session reducer 补一个 `about:blank` 标签；
6. 等待该标签的 WebContents 注册到 Browser Control Registry；
7. 返回最终可见状态和会话/标签身份。

重复调用不得关闭面板、不得创建重复标签、不得改变 URL，也不得复用其他 Conversation 的 BrowserSession。

第一阶段接口不暴露 `sessionPolicy: new`。显式新建网页标签仍由 Browser UI 或未来独立资源操作负责，避免把“显示能力入口”与“创建资源”混在一个浅接口里。

### 二、返回状态采用可验证结果

成功返回：

```ts
{
  status: 'opened' | 'activated' | 'already_active';
  conversationId: string;
  browserTabId: string;
  visible: true;
}
```

- `opened`：Workbench 原先关闭，本次展开并激活 Browser；
- `activated`：Workbench 已开但停在其他 capability，本次切到 Browser；
- `already_active`：Browser 已经是当前可见 capability。

失败使用既有结构化 Tool Result/Evidence 路径，包括：

- `missing_conversation_context`
- `conversation_not_foreground`
- `renderer_unavailable`
- `browser_reveal_timeout`
- `no_active_browser`
- `browser_unavailable`

> **被后续 ADR 部分取代说明（2026-11-15 对齐）**：
> 1. 在经典前台会话中，“Workbench 面板未展开 / reveal 超时即返回 `no_active_browser` / `browser_reveal_timeout` / `renderer_unavailable` 失败”已被 [ADR 66](66-browser-headless-fallback-execution.md) 取代——reveal 降级为尽力而为副作用，未挂载可见视图时退回同分区 headless `<webview>` 执行（`status: 'background', headless: true`）。
> 2. 在 0.1.0 **Project Bot 模式**（[ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 决策 5）下，`work_session` 不投影 L1 `browser_*`、也不触发 L1 面板 reveal（网页执行走 L2 `browser_external_*` 与 `web_fetch`）；L1 `BrowserSession` 专属于用户打开的右侧资源窗口网页标签、独立浏览器窗口与经典前台对话（[ADR 109](109-resource-reference-preview-and-artifact-collaboration.md) / [ADR 125](125-resource-window-directory-tabs.md)）。

### 三、Main 负责协调，Renderer 负责表达

Main 新增 Browser Panel Reveal Coordinator，职责为：

1. 接收 Provider 的 `{ requestId, conversationId, focus }` 请求；
2. 只向主窗口 renderer 发送 `browser:panel-reveal-request`；
3. 等待匹配 `requestId` 的 renderer ack；
4. 合并同一 Conversation 的并发 ensure 请求；
5. 超时或窗口不可用时返回结构化失败；
6. 不直接维护 Workbench open/activeTab/BrowserSession 状态。

Renderer 的 WorkbenchProvider 是表达层状态的唯一真源。它收到请求后必须先验证 `conversationId` 与当前前台 Conversation 相同，然后读取原状态，幂等执行：

```text
setOpen(true)
setActiveTab('browser')
BrowserSession 复用或建立空白标签
等待 BrowserView 注册
ack(requestId, opened | activated | already_active)
```

Main 不得模拟鼠标点击，不得通过 DOM selector 操纵 Peer 自己的界面。

### 四、`browser_navigate` 自动确保前台 Browser 可见

前台可见工具的预期是“用户眼前同一个浏览器”。因此 `browser_navigate` 在解析目标 WebContents 前总是调用 `ensureBrowserReady`：

```text
browser_navigate(url)
  -> ensure Browser panel visible for toolContext.conversationId
  -> wait for same-conversation active BrowserTab registration
  -> request network permission
  -> loadURL(url)
  -> return PermissionGrant + Evidence
```

`browser_open_panel` 只建立可见工作现场，不发起网络导航，因此不触发目标站点的联网权限；仍生成本地 capability PermissionGrant 与 Evidence。

`browser_click`、`browser_type`、`browser_screenshot`、`browser_read_dom` 第一阶段保持现有行为：有已注册同会话 Browser 时直接执行；没有时可复用同一 ensure seam，确保所有可见浏览器工具的前置条件一致。

### 五、前台表达与后台调度分离

后台 Task 可以把本会话浏览器当作一等可调度能力：即使用户当前没有打开该会话的 Browser 面板、也没有切到该会话，任务仍应拉起本会话 WebContents 并完成打开标签、导航和验证。

主动 reveal 只在「请求会话就是当前前台会话，并且明确要求 focus」时打开/切到 Browser 面板。后台调度不得抢当前前台会话的工作台，也不得改窗口菜单绑定的前台 Browser 目标。

`browser_open_panel` 仍可对当前前台会话请求可见接管；后台 Goal 调用同一工具时默认只准备本会话工作现场，不自动把用户切过去。

### 六、Conversation 与 Session 隔离不变

Browser 目标仍严格使用：

```text
conversationId + browserTabId + webContentsId
```

- A 会话调用不得命中 B 会话的 WebContents；
- reveal ack 必须携带请求的 conversationId；
- Registry 等待也必须按 conversationId；
- BrowserSession 的标签集合、活跃标签和 URL 继续由 WorkbenchContext 的会话桶管理；
- Cookie/Profile 继续遵循 ADR 46 的共享 `persist:peer-browser` 决策。

## 跨层契约

### Provider → Coordinator

```ts
ensureBrowserReady({
  conversationId: string;
  focus: boolean;
  timeoutMs: number;
}): Promise<{
  ok: boolean;
  status?: 'opened' | 'activated' | 'already_active';
  conversationId: string;
  browserTabId?: string;
  error?: string;
}>
```

### Main → Renderer

事件：`browser:panel-reveal-request`

```ts
{
  requestId: string;
  conversationId: string;
  focus: true;
}
```

### Renderer → Main

IPC：`browser:panel-reveal-ack`

```ts
{
  requestId: string;
  conversationId: string;
  status: 'opened' | 'activated' | 'already_active' | 'rejected';
  browserTabId?: string;
  error?: string;
}
```

Preload 只暴露受限的订阅和 ack 方法，不暴露通用 `ipcRenderer`。

## 验证要求

1. Workbench 关闭时调用 `browser_open_panel`，返回 `opened`，Browser 可见。
2. Workbench 已开但位于 Files/Documents/Plan 时调用，返回 `activated`。
3. Browser 已经可见时重复调用，返回 `already_active`，不关闭面板、不创建重复标签。
4. 当前 Conversation 已有 BrowserSession 时复用原标签集合与活跃标签。
5. 没有 Session/标签时只建立一个 `about:blank` 标签。
6. A/B Conversation 的 open、activeTab、BrowserSession 和 WebContents 不串用。
7. `browser_navigate` 在面板关闭时自动 reveal，并在注册完成后导航。
8. reveal 本身不请求目标站点网络权限；导航仍走原有权限门。
9. Renderer 不可用、Conversation 不匹配或超时时返回结构化失败，不退回系统浏览器。
10. 所有工具继续沿 Runtime Projection、PermissionGrant 和 Evidence 链路执行。

## 影响范围

知识与契约：

- 新增本 ADR；
- `packages/runtime-core/src/local-tool-contracts.ts`；
- `capabilities/local.web.control.openPanel.json`；
- `apps/desktop/electron/main/tools/browser-tool-definitions.mjs`。

Main / IPC：

- `local-browser-control-provider.mjs`；
- Browser Panel Reveal Coordinator；
- Browser IPC registration；
- Main composition 与 projected tool executor 注入。

Renderer / Preload：

- `preload.source.cjs` 与生成的 `preload.cjs`；
- `bootstrapPreloadApi.ts`；
- `WorkbenchContext.tsx` / Browser reveal listener；
- 既有 Chat tool-call reveal 逻辑收敛为兼容提示，不再承担唯一启动责任。

## 非目标

- 不用系统默认浏览器作为可见工具失败时的自动回退；
- 不新增独立无头浏览器运行时；后台 Task 仍复用同一套会话级 `<webview>`，只是可以离屏挂载；
- 不自动把用户切到其他 Conversation 的工作台；
- 不把 Workbench UI 状态复制到 Main；
- 不模拟用户点击 Browser 标签；
- 不在本次实现 Browser Profile、标签拖拽或跨会话移动。
