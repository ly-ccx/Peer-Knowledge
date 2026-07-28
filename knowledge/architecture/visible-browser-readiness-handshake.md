# 可见 Browser 自动展开与就绪握手

创建时间：2026-07-28
最后更新：2026-07-28
状态：Accepted / 实施基线
关联代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）

## 1. 决策摘要

`browser_*` 是对当前会话可见 Browser 的操作，不应把“右侧面板当前关闭”解释为能力不可用。当前前台会话发起 `browser_*` 时，Desktop 必须自动：

```text
ensure → ready → execute
```

1. **ensure**：展开 Workbench、切换到 Browser、确保当前 conversation 至少有一个 active tab；
2. **ready**：等待该 tab 的 `<webview>` 创建、注册 `webContentsId`，且 main-process Browser registry 能解析目标；
3. **execute**：Provider 只对握手返回的当前 conversation / active tab 执行工具。

等待超时、用户取消、会话切换、权限拒绝或 webview 创建失败时，返回结构化失败。不得回退到其他会话、其他窗口或无头浏览器。

> 无头浏览器不能冒充可见 Browser 验收。它可以补充做 DOM、计算样式或离线截图检查，但不能替代用户眼前 Workbench Browser 的交互与像素证据。

## 2. 问题

现有链路中，Renderer 收到 `browser_*` tool-call 事件后执行：

```text
setWorkbenchTab('browser')
setWorkbenchOpen(true)
```

React 状态更新、Browser tab 创建、`<webview>` guest 初始化、`dom-ready` 和 `registerBrowserWebContents` 都是异步过程；与此同时，main-process Provider 会立即查询 Browser registry。如果 registry 尚未有当前 conversation 的 active tab，Provider 会先失败，随后面板才展开。

这是目标生命周期和执行时序问题，不是 Computer Use 或视觉模型能力不足。

## 3. 目标与边界

### 3.1 目标

- 面板关闭时，首次 `browser_*` 能自动展开并等待就绪；
- 当前会话没有 Browser tab 时，自动创建默认 tab；
- 已有 active tab 时复用，不重复创建；
- Provider 执行前得到与当前 conversation 绑定的确定目标；
- 后台会话不能抢占当前 UI 或操作前台会话 Browser；
- 超时、取消、切换会话和注册失败可诊断、可测试。

### 3.2 非目标

本协议不覆盖：

- Playwright/CDP 外部浏览器；
- macOS 原生窗口或系统弹窗；
- 无头浏览器回退；
- Browser Cookie/站点会话导入；
- 在这次修复中统一全部 Computer Action / Observation 协议。

## 4. 单一事实源

Browser target 的权威事实仍位于 main process Browser registry：

```text
conversationId + browserTabId + webContentsId
```

Renderer 负责表达和生命周期推进：展开、切 tab、创建默认 tab、发布 guest 注册。Renderer state 不是执行权限，也不能用“面板已打开”文本事件代替 main registry 的可解析目标。

就绪的最低定义：

1. tool call 属于当前前台 conversation；
2. 该 conversation 存在 active Browser tab；
3. tab 已发布有效 `webContentsId`；
4. main registry 中 `(conversationId, browserTabId)` 与该 `webContentsId` 一致；
5. 对应 `webContents` 未销毁。

对于需要页面内容的动作，Adapter 仍按动作需要等待导航/DOM；“Browser ready”只表示控制目标已经存在，不表示目标网页已经加载完成。

## 5. 协议

### 5.1 请求

main process 在 Browser Provider 解析不到当前 conversation target 时，向拥有该 conversation 的 Desktop renderer 请求：

```ts
type EnsureVisibleBrowserRequest = {
  requestId: string;
  conversationId: string;
  reason: 'browser_tool';
  timeoutMs: number;
};
```

请求必须绑定发起 Tool Call 的 `conversationId`。不得使用全局“最后活动 Browser”。

### 5.2 Renderer 处理

Renderer 收到请求后：

1. 验证 `conversationId === activeConversationId`；不一致则拒绝；
2. `setWorkbenchTab('browser')`；
3. `setWorkbenchOpen(true)`；
4. 获取该 conversation 的 Browser session；若无 tab，则以既有 reducer 创建一个默认 tab；
5. 将 active tab 作为预期目标；
6. 等待 BrowserView 完成 guest 注册；
7. 通过既有注册 IPC 更新 main registry；
8. 回复候选 `browserTabId`，或由 main 直接观察 registry 满足条件。

`ensure` 必须幂等。并发调用同一 conversation 时共享同一个 pending promise，不得创建多个默认 tab或重复抢焦点。

### 5.3 Main 等待

Provider 的执行顺序：

```text
resolve current target
  ├─ found → execute
  └─ missing → request ensure
                 → wait until registry resolves current conversation target
                 → revalidate
                 → execute
```

等待必须由以下任一事件推进，而非忙轮询：

- Browser registry `register` / active target change；
- renderer ensure response；
- conversation/window lifecycle cancellation；
- timeout。

实现初期若 registry 尚无订阅接口，可以使用有上限的短间隔重试作为临时适配，但协议目标仍是事件驱动等待。

### 5.4 执行前复核

握手完成后，Provider 在执行每个动作前复核：

- conversation 仍为请求目标；
- active tab 未改变，或按策略重新解析当前 active tab；
- `webContentsId` 仍在 registry 且未销毁；
- PermissionGrant 仍有效。

复核失败时返回 `browser_target_changed` 或重新走一次 ensure；不能静默操作旧目标。

## 6. UI 行为

- 当前前台 conversation 发起 `browser_*`：自动展开右侧面板并切到 Browser；
- 若面板已展开但停在 Tasks/Artifacts：切到 Browser；
- 若 Browser 已有 active tab：保持该 tab；
- 若无 tab：创建一个默认 tab；
- 后台 conversation 的 tool event：不展开、不抢焦点，并因不可见目标返回明确错误；
- 用户在等待中主动关闭面板：视为取消或允许当前 ensure 在短时间内完成，产品必须选择一种一致策略；首期建议视为 `user_cancelled`，避免与用户争抢 UI；
- UI 显示简短状态，如“正在准备 Browser…”，但状态文本不构成执行证据。

## 7. 错误语义

统一错误至少包括：

- `browser_conversation_not_active`：调用来自非前台会话；
- `browser_ensure_unavailable`：没有可接收 ensure 请求的 Desktop renderer；
- `browser_tab_create_failed`：默认 tab 创建失败；
- `browser_registration_timeout`：面板已请求展开，但 webview 未在期限内注册；
- `browser_target_changed`：等待/执行期间 active tab 或 conversation 变化；
- `browser_webcontents_destroyed`：目标 guest 已销毁；
- `user_cancelled`：用户关闭面板或停止执行；
- `permission_denied`：Browser tool 权限被拒绝。

用户可见文案应区分：

- “正在准备可见 Browser”；
- “Browser 启动超时，请重试”；
- “当前会话已切换，未执行操作”；
- “用户已停止 Browser 操作”。

不得把暂时未注册描述成“系统没有可见浏览器能力”。

## 8. 权限与 Evidence

自动展开是 UI 生命周期动作，不授予新的本地执行权限。`browser_*` 仍必须走：

```text
Capability Provider
  → Manifest
    → Runtime Projection
      → Tool Call
        → PermissionGrant
          → Evidence
```

Evidence 至少记录：

- tool call / action；
- conversationId 与 browserTabId 摘要；
- 是否经历 ensure；
- ensure 耗时与结果；
- 最终 webContents target；
- execute 结果、截图或 DOM artifact ref；
- timeout/cancel/target-changed 等失败码。

不得把“面板已展开”作为“页面已通过视觉验收”的 Evidence。视觉验收必须来自该可见 Browser target 的真实 screenshot / DOM / interaction result。

## 9. 与无头浏览器的边界

无头浏览器可以作为另一种明确命名的测试环境，用于：

- 静态页面截图；
- DOM 和计算样式检查；
- 自动化回归测试。

但它不是当前 Workbench Browser，也不共享相同的 viewport、session、Cookie、Electron webview 行为或用户可见状态。因此：

- `browser_*` 失败后不得自动、静默切到无头环境；
- 若任务允许使用无头环境，应由独立 capability 和 Evidence 标识；
- 回复中必须说明观察源；
- 无头浏览器不能冒充可见 Browser 验收。

## 10. 最小实施方案

### Renderer

- 保留现有 `shouldRevealBrowserPanel` 作为表达层规则；
- 增加可由 main request/IPC 触发的 `ensureVisibleBrowser(conversationId)`；
- 复用 WorkbenchContext 的 session/reducer 创建默认 tab；
- BrowserView 注册成功后满足 main registry 等待；
- 组件卸载、会话切换、用户关闭时取消 pending ensure。

### Main / IPC

- 增加 main → renderer 的 ensure 请求通道，或在现有 desktop bridge 中增加 request/response；
- Browser registry 增加 `waitForActiveTarget(conversationId, timeout, signal)`；
- Provider 在 target 缺失时调用 ensure + wait，而不是立即报错；
- window 销毁和 timeout 时清理 listener/promise。

### Provider

- 对 navigate/click/type/screenshot/read_dom 使用同一 target resolver；
- resolver 先直接查 registry，缺失时 ensure；
- 所有动作都禁止跨 conversation fallback；
- 结构化返回 ensure 失败原因。

## 11. 验收标准

### 11.1 面板关闭

Given 当前 conversation 有 Browser session，但 Workbench 关闭，When 调用任意 `browser_*`，Then：

- Workbench 自动展开并切到 Browser；
- Provider 等到 registry target 就绪；
- 工具只执行一次；
- Evidence 指向该可见 Browser。

### 11.2 无标签

Given 当前 conversation 尚无 Browser tab，When 调用 `browser_navigate`，Then：

- 只创建一个默认 tab；
- 注册后执行导航；
- 并发两个 Browser 调用不会创建两个默认 tab。

### 11.3 已就绪

Given 当前 conversation active tab 已注册，When 调用 `browser_*`，Then 直接执行，不引入可感知额外等待，也不重建 tab。

### 11.4 超时

Given renderer 不存在、webview 未注册或 guest 创建失败，When 超过 timeout，Then：

- 返回 `browser_registration_timeout` 或更具体错误；
- 不执行动作；
- listener、timer、pending promise 被清理；
- 不回退到其他会话或无头浏览器。

### 11.5 会话隔离

Given conversation A 发起调用后用户切到 B，Then A 的 pending ensure 取消或失败；不得展开 B 的 Browser 并执行 A 的动作。

### 11.6 回归检查

自动化测试至少覆盖：

- `shouldRevealBrowserPanel` 当前会话规则；
- registry 已就绪快速路径；
- 缺失目标 → ensure → register → execute；
- ensure timeout；
- 多个等待者共享同一次 ensure；
- conversation/tab 变化；
- webContents destroyed；
- 无跨会话 fallback。

## 12. 关联文档

- `knowledge/decisions/40-embedded-browser-and-agent-control.md`
- `knowledge/decisions/46-conversation-bound-browser-tabs.md`
- `knowledge/architecture/computer-use-capability-ladder.md`
- `knowledge/architecture/20-architecture-governance.md`
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`

## 13. 后续演进

当统一 Computer Use Orchestrator 落地后，本协议应收敛为 `EmbeddedBrowserAdapter.ensureEnvironmentReady()`，并通过通用 Environment/Observation 生命周期实现。当前实现可以是 Desktop 专用 IPC 适配，但不得形成绕过 Provider、PermissionGrant 或 Evidence 的第二条执行路径。
