# 46. 会话绑定的 Workbench 与多标签浏览器

创建时间：2026-07-15
最后更新：2026-09-02

## 状态

Accepted，进入实现。

## 背景

ADR 40 落地了单个可见 `<webview>` 以及 Agent 直控该 WebContents 的能力，但当时明确把
多标签页排除在范围外。后续代码只补了“每个会话记住最后一个 URL”：切换会话时销毁旧
`<webview>`、创建新 `<webview>` 并重新加载该 URL。

这留下三个边界问题：

1. `workbench.open` 仍是窗口级布尔值，A 会话打开或关闭右栏会直接改变 B 会话的布局；
2. BrowserView 只有一个页面，不能像桌面浏览器一样在同一会话中并行保留多个网页；
3. main 进程只保存一个全局 `activeEntry`，Agent 工具的权限属于发起会话，但目标 WebContents
   没有会话身份，后台会话存在误操作前台网页的风险。

## 决策

### 决策一：Workbench 展开状态属于会话

- `open` 改为 `openByConversation[conversationId]`；无会话时使用 `__none` 桶。
- `activeTab` 继续保持现有会话级映射。
- `width` 仍为窗口级偏好，因为它表达用户对工具区宽度的稳定偏好，而不是会话任务状态。
- 左侧栏的 `sidebarOpen / sidebarWidth` 仍为窗口级偏好；右侧挤压导致的
  `sidebarAutoCollapsed` 仍是瞬时布局状态。

### 决策二：每个会话拥有独立的 BrowserSession

```ts
interface BrowserSession {
  tabs: Array<{
    id: string;
    url: string;
    title: string;
  }>;
  activeTabId: string;
}
```

- 新会话从一个 `about:blank` 标签开始。
- 新建、关闭、切换、导航和标题更新都只修改当前会话的 BrowserSession。
- 关闭最后一个标签时立即补一个新的空白标签，BrowserView 始终至少有一个页面。
- 当前会话内的多个 `<webview>` 同时保持挂载，仅活跃标签可见，以保留页面 DOM、滚动位置和
  前进后退历史。
- 进程内切换 conversation 时，最近用过的非空白会话浏览器可继续挂着同一批 WebContents
  （上限 8 个，LRU）。点回来复用同一个 BrowserView，不按 URL 拆掉重建。超出上限的最旧项、
  以及应用重启后，仍按持久化的 URL 元数据重建；不承诺恢复页面 DOM、滚动位置与 history stack。
  空白 `about:blank` 不占活页名额。登录分区仍是共享的 `persist:peer-browser`。
- BrowserSession 元数据随现有 workbench settings 防抖持久化；不把网页正文、表单内容或
  history stack 写入 settings。

### 决策三：登录态共享，任务状态隔离

所有网页继续使用 `persist:peer-browser` partition。它与主应用 renderer 隔离，但不同会话和
标签共享 Cookie、localStorage 与登录态，避免用户在每个会话重复登录。

“会话绑定”在本决策中指 Workbench 展开、标签集合、活跃标签和 Agent 操控目标隔离，不表示
浏览器身份隔离。若未来需要账号沙箱，应新增显式的 Browser Profile 概念，而不是把
conversationId 隐式编码进 partition。

### 决策四：Agent 目标使用 conversationId + browserTabId

renderer 注册 WebContents 时必须同时上报：

```text
webContentsId + conversationId + browserTabId + active + url + title
```

main 注册表按 `(conversationId, browserTabId)` 保存条目，并为每个 conversation 保存一个
active browser tab。`local.web.control.*` Provider 必须从 Tool Context 读取 conversationId，
只解析该会话的活跃标签：

- 命中：操控该会话的活跃网页；
- 未命中或 WebContents 已卸载：返回结构化 `no_active_browser`；
- 禁止回退到其它会话最后注册的 WebContents。

应用菜单 `Cmd/Ctrl+R` 仍操控当前前台会话的活跃网页标签；这是窗口交互，不是 Agent 工具调用。

## 状态与数据流

```text
conversationId
  -> Workbench open / active workbench tab
  -> BrowserSession(activeBrowserTabId, tabs[])
  -> BrowserView(webview per tab)
  -> IPC registration(conversationId, browserTabId, webContentsId)
  -> Browser Control Registry
  -> local.web.control Provider(toolContext.conversationId)
  -> PermissionGrant + Evidence
```

renderer 继续只负责表达与用户交互；main 负责可操控 WebContents 的权威登记与目标解析。
浏览器工具仍沿用既有 Capability Provider → Manifest → Runtime Projection → Tool Call →
PermissionGrant → Evidence 链路，不新增旁路。

## 迁移与兼容

- 旧的 `workbench.open: boolean` 只作为首次读取时的默认值；新写入使用
  `workbench.openByConversation`。
- 旧的每会话单 URL 内存结构不再作为真值；无法恢复的会话从空白标签开始。
- IPC 注册接口在 renderer、preload 与 main 同步升级，不保留缺少会话和标签身份的 Agent
  目标选择语义。

## 验证要求

1. A/B 会话的 Workbench 展开状态互不影响。
2. 同一会话可新增、切换、关闭多个网页标签，关闭最后一个标签后出现空白标签。
3. A/B 会话分别恢复自己的标签集合和活跃标签。
4. Agent 从 A 会话调用浏览器工具时，只能命中 A 的活跃标签；A 的 WebContents 未挂载时失败，
   不得操控 B。
5. 切换活跃网页标签后，Agent 操控与 `Cmd/Ctrl+R` 都指向新标签。
6. 所有浏览器工具仍生成原有 PermissionGrant 和 Evidence。

## 暂不处理

- 自动把 `target=_blank` 或 `window.open` 转换为新标签；
- 标签拖拽排序、固定、分组、书签、下载管理；
- 跨应用重启恢复 DOM、滚动位置和前进后退历史；
- 每会话独立 Cookie/Profile。
