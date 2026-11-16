# 40. 内嵌浏览器 + Agent 操控（webview 载体 + webContents 直控桥）

## Status

Accepted（2026-06-25 M1/M2 本地落地并后续由 [ADR 46](46-conversation-bound-browser-tabs.md)、[ADR 59-browser](59-browser-panel-reveal-capability.md)、[ADR 70](70-l1-browser-action-surface.md)、[ADR 72](72-l1-default-web-entry.md) 扩展会话绑定、reveal 通知、动作面与默认策略；注意按 [ADR 71](71-l2-playwright-external-browser.md) / [ADR 85](85-project-agent-hosts-inputs-and-surfaces.md)，0.1.0 Project Bot 的后台 `work_session` 已剥离 `browser_*` L1 工具并固定改用 L2 受控 Playwright + [ADR 38](38-web-search-fetch-provider.md) `web_fetch`）。

本特性新增了一条 runtime 能力链路（`local.web.control.*` capability + provider +
工具投影），属 `AGENTS.md` 定义的 A 级变更范畴；代码改动一律在 `peer_agent` 仓，
本知识库仅作可追溯记录。

- 创建时间：2026-06-25
- 最后更新：2026-11-15（规范标注 Accepted 并标明 L1 在经典会话／独立浏览窗口与后台 `work_session` 间的适用边界）

## Context

### 背景与诉求

Workbench 左侧已有「浏览器」面板入口（与 目标 / 终端 / 文件 / Diff 并列），但此前
面板内是空白占位，既不能给人浏览网页，Agent 也无法操控浏览器。用户诉求是「全都
要」：

1. 面板里要有**真实可见**的浏览器（地址栏 + 前进/后退/刷新/停止 + 加载态 +
   错误兜底），人可以正常浏览网页；
2. Agent 要能操控**用户眼前那个同一个**浏览器实例（导航/点击/输入/截图/读 DOM），
   操作对用户实时可见，而不是另起一个看不见的无头浏览器。

### 既有能力基线（改造前，基于代码证据）

- 已有 `local.web.fetch`（ADR 38）：无头抓取网页正文 → 落 artifact → 仅回摘要 +
  ref，走 capability manifest + provider + 权限门 + Evidence 范式。但它是「抓取」
  而非「操控可见浏览器」，且不可见。
- runtime 能力链路范式成熟：
  `capabilities/<id>.json`(manifest) → `tools/*-tool-definitions.mjs`(工具定义) →
  `runtime-projection`(投影) → tool call → `requestPermission`(权限门) →
  provider 执行 → Evidence。
- `capability-registry.mjs` 按 manifest **内部 `capabilityId` 字段**匹配（不是文件
  名）；provider 分发按工具的 `runtime.executorCapabilityId`（= capabilityId）匹配
  到 `provider.capabilityIds`。

### 技术选型的关键问题

让 Agent 操控「用户可见的浏览器」，难点在于**渲染进程里的可见承载** 与 **主进程里
的可编程控制** 如何打通：

- 可见承载只能在 renderer（React）里；
- 但 Agent 工具执行在 main 进程的 provider 里；
- 若每个操控动作都 main→renderer→webview 逐跳 IPC 往返，链路长且脆弱（时序、序列
  化、回执）。

## Decision

### 决策一：载体用 Electron `<webview>`（独立会话隔离）

面板内用 `<webview>` 标签承载真实浏览器，而非 `<iframe>`（被 X-Frame-Options /
CSP 限制，多数站点打不开）或 `BrowserView`（覆盖在 React 之上、与布局/层级耦合，
难以嵌进面板内容流）。

安全默认：

- 独立 `partition` 会话隔离（与主应用 cookie/storage 分离）；
- 禁用 `nodeIntegration`；
- 新窗口默认拦截（`setWindowOpenHandler` / `new-window` 阻止弹窗逃逸）。

### 决策二：webContents 直控桥 —— renderer 上报 id，main 用 `webContents.fromId` 直接操控

不走逐跳 IPC，而是建立「句柄注册桥」：

1. renderer 在 webview `dom-ready` 后取 `wv.getWebContentsId()`，经 IPC
   `browser:register-webcontents` 上报给 main；
2. main 侧 `browser-control-registry.mjs` 记录**当前活跃**的 `webContentsId`（含
   url/title 等调试元信息）；webview 卸载时 `browser:unregister-webcontents` 注销；
3. Agent 工具执行时，provider 调 `getActiveWebContentsId()` +
   `webContents.fromId(id)`，**直接拿到同一个 WebContents** 操控：
   - 导航：`loadURL`
   - 点击：`executeJavaScript`(定位元素中心点) + `sendInputEvent`(mouseDown/Up)
   - 输入：`executeJavaScript`(聚焦/清空) + `insertText` + 可选回车
   - 截图：`capturePage().toPNG()`
   - 读 DOM：`executeJavaScript`(innerText / outerHTML)

因为操控的就是用户眼前那个 webview 的 WebContents，所以**所有动作对用户实时可见**，
且避免了多跳往返的脆弱性。这是本 ADR 的核心设计。

### 决策三：5 个工具走统一 capability + 权限门 + Evidence 范式

新增 capability `local.web.control.*`（navigate / click / type / screenshot /
readDom），对应 5 个工具 `browser_navigate / browser_click / browser_type /
browser_screenshot / browser_read_dom`：

- **风险分级**：导航/点击/输入为 `L3_external_write`（写/副作用），截图/读 DOM 为
  `L2_external_read`（读）；统一 `D2_sensitive`。
- **授权语义**：导航类复用联网授权语义（同会话授权一次）；点击/输入/截图/读 DOM 在
  已授权的可见浏览器上执行，经 `requestPermission` 弹权限门，拒绝走 `denied` 兜底。
- **Evidence/落盘**：截图 PNG 与 DOM 文本落本地 artifact（`local-browser-artifact://`），
  **仅返回摘要 + artifactRef**，不把大图/全文回灌进模型上下文（符合
  `evidencePolicy=artifact_ref`）。输入文本可能含敏感信息，`type` 不回灌原文
  （`returnedToCloud=false`）。

### 决策四：分 M1 / M2 推进

- **M1（人用的可见浏览器）**：`BrowserView.tsx`（webview UI + 工具条 + 地址栏 +
  加载态 + did-fail-load 兜底）+ `workbench.css` 样式。typecheck + 自测先过。
- **M2（Agent 操控）**：注册桥 + preload/契约 + capability manifest + 工具定义 +
  provider + host 注册。

## 契约与边界

- **分发匹配**：manifest 的 `capabilityId` 必须与工具 `runtime.executorCapabilityId`
  **逐字一致**。本次踩坑：读 DOM 的 id 是驼峰 `local.web.control.readDom`，manifest
  文件名/字段一度写成 kebab `read-dom` 导致不匹配，已修正为
  `local.web.control.readDom.json` + 字段同名（registry 按字段匹配，文件名仅求整洁）。
- **活跃实例语义**：注册表只保存「当前活跃」一个 webview（单实例）。多标签页、并发
  多 webview 不在本期范围。
- **目标不可用兜底**：无活跃 webview / 已销毁 / selector 未命中 / 必填参数缺失，均
  返回结构化失败 + 友好文案，不抛裸异常。

## 涉及文件（均在 `peer_agent` 仓）

渲染层 / 桥：

- `apps/desktop/renderer/src/workbench/views/BrowserView.tsx`（M1 可见浏览器 +
  dom-ready 上报 / 卸载注销）
- `apps/desktop/renderer/src/styles/workbench.css`（浏览器面板样式）
- `apps/desktop/electron/preload/preload.cjs`（`registerBrowserWebContents` /
  `unregisterBrowserWebContents` 通道）
- 渲染层契约：`bootstrapPreloadApi.ts` 类型 + `clientApi.ts` 封装/占位

主进程 / runtime：

- `apps/desktop/electron/main/main.mjs`（`ipcMain.handle('browser:register-webcontents'
  / 'browser:unregister-webcontents')`）
- `apps/desktop/electron/main/runtime-gateway/browser-control-registry.mjs`（句柄
  注册表：register / unregister / getActiveWebContentsId / getActiveBrowserEntry）
- `apps/desktop/electron/main/runtime-gateway/local-browser-control-provider.mjs`
  （provider：权限门 + webContents.fromId 直控 + artifact 落盘）
- `apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs`（注册 provider）
- `apps/desktop/electron/main/tools/browser-tool-definitions.mjs` +
  `tools/index.mjs`（工具定义与聚合）
- `capabilities/local.web.control.{navigate,click,type,screenshot,readDom}.json`
  （5 个 capability manifest）

## 安全模型小结

- 会话隔离（独立 partition）+ 禁 nodeIntegration + 拦新窗口；
- 每个 Agent 操控动作经权限门授权（导航类复用联网授权，其余 ask）；
- 敏感产物（截图/DOM/输入）落 artifact，不整段回灌；输入原文不回云端；
- provider 操控的对象就是用户眼前那个可见 webview，行为透明可见、可审计。

## 验证

- `pnpm -r typecheck`：6 个 workspace 项目（protocol / i18n / chat-kernel / ui /
  task-thread / apps-desktop）全部 Done。
- 端到端 IPC 契约一致性核对：renderer ↔ preload ↔ main ↔ registry ↔ provider 的
  通道名与参数全链路对齐，无断点。
- 待人工自测：① M1 浏览网页（导航/前进后退/刷新/停止/错误页兜底）；② Agent 五类
  操控对用户可见；③ 权限门弹窗与未授权拒绝兜底；④ 截图/读 DOM 的 Evidence 落盘 +
  摘要回显。

## 范围外（Out of Scope）

多标签页、书签/历史持久化、下载管理、扩展插件、操控录制回放。
