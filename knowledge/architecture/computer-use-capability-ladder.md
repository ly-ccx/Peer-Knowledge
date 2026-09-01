# Peer Agent Computer Use 分层能力架构

创建时间：2026-07-28
最后更新：2026-07-28
状态：Proposed / 架构基线
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）

## 1. 决策摘要

Peer Agent 的 Computer Use 按执行环境分成三档，并按风险由低到高逐档建设：

1. **L1：内嵌 Browser（已有）**——操控 Desktop Workbench 中用户正在观看的 Electron `<webview>`；
2. **L2：受控外部浏览器（Playwright / CDP）**——连接由 Peer 创建或用户明确授权接管的 Chrome / Chromium 上下文；
3. **L3：macOS OS UI**——通过 macOS Accessibility、屏幕录制权限和键鼠注入操控受控的前台应用。

三档不是三套 Agent。它们共享同一个认知循环、动作协议、权限事实和 Evidence 模型，仅由不同的 Environment Adapter 执行动作与生成观察。

```text
Cloud Agent Runtime（看、想、选择动作）
  -> Runtime Projection
    -> Computer Use Tool Contract
      -> PermissionGrant
        -> Computer Use Orchestrator
          -> Environment Adapter
             ├─ EmbeddedBrowserAdapter
             ├─ ExternalBrowserAdapter (Playwright / CDP)
             └─ MacOSUIAdapter (AX / ScreenCapture / Input Injection)
          -> Observation + Evidence
```

核心判断：

> 模型负责“看与决定”，本地宿主负责“授权、执行、观察与留证”。

本文是能力阶梯的总架构。L1 的既有实现继续以 ADR 40、ADR 46 为准；L2、L3 落地前应分别补充实施 ADR，但不得偏离本文的统一协议与治理主链。

## 2. 背景与问题

Peer Agent 已具备可见内嵌浏览器及 `browser_navigate`、`browser_click`、`browser_type`、`browser_screenshot`、`browser_read_dom`。该能力能操作用户眼前的 Workbench 页面，但不能：

- 自动化用户正在使用的外部 Chrome / Chromium；
- 使用 Playwright 的稳定定位、等待、下载和多页面能力；
- 观察或操控 Desktop 原生弹窗、系统设置及其他 macOS 应用；
- 用同一份动作和 Evidence 契约跨环境执行任务。

如果为外部浏览器和 OS UI 各自直接新增一组工具，会产生三套动作语义、三套权限判断和三套证据格式。模型必须理解宿主实现细节，Runtime Projection 也难以按风险一致裁剪。因此，应先确定统一 Computer Use 架构，再逐档增加执行适配器。

## 3. 设计目标

1. **同一认知循环**：模型使用稳定的观察—动作协议，不承担宿主自动化实现。
2. **环境显式**：任何动作都必须指向明确的 environment 与 target，禁止“当前全局窗口”式隐式目标。
3. **用户可见、可中止**：L1 操作可直接观看；L2/L3 应提供当前目标、运行状态和停止入口。
4. **最小权限**：按环境、动作、目标和有效期授权，不把屏幕录制或 Accessibility 权限等同于无限操作授权。
5. **证据闭环**：观察、动作结果和关键状态形成结构化 Evidence；大体积截图只保存 artifact ref。
6. **渐进增强**：优先使用语义稳定的 DOM / Accessibility 信息，像素坐标只作必要补充。
7. **宿主边界真实**：Desktop 承载可视 Computer Use；CLI/TUI 不得伪造不存在的桌面对象。

## 4. 非目标

本文不决定：

- 跨平台 Windows / Linux OS UI 自动化；
- 绕过验证码、反自动化、安全密钥或生物识别；
- 无人值守完成支付、删除账号、发送敏感信息等高风险行为；
- 将截图、键盘输入、Cookie 或 Accessibility 树默认上传到远端；
- 用 Computer Use 替代已有文件、Shell、HTTP API 或 MCP 等更稳定的结构化工具；
- 让模型直接持有 CDP 端口、Electron `webContentsId`、AXUIElement 句柄等底层对象。

## 5. 分层能力阶梯

### 5.1 L1：内嵌 Browser（已有）

#### 目标环境

Desktop Workbench 内由 Peer 创建并显示的 Electron `<webview>`。它是用户与 Agent 共同观看、共同操作的页面。

#### 既有架构约束

- 沿用 ADR 40 的 `<webview>` 可见载体与 `webContents.fromId` 直控桥；
- 沿用 ADR 46 的 `conversationId + browserTabId` 目标解析；
- Provider 不得回退到其他会话或窗口最后注册的 WebContents；
- 网页 session 与主应用 renderer 隔离，禁用 Node Integration，并限制新窗口逃逸；
- 工具继续经过 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。

#### 能力范围

当前能力包括 navigate、click、type、screenshot、read DOM。后续可在统一动作协议下补充：

- scroll、hover、double click、right click；
- key press / key chord；
- wait、页面加载状态、元素可交互性等待；
- drag、文件选择、下载结果；
- tab / frame / dialog 的显式目标。

#### 优势与边界

L1 可见、隔离、容易审计，风险最低，应作为网页任务默认入口。但它只覆盖 Workbench 内页面，不能代表用户外部浏览器的 Profile、扩展、现有标签和登录上下文，也不能操控原生 UI。

### 5.2 L2：受控外部浏览器（Playwright / CDP）

#### 定义

连接到 Peer 明确管理或用户明确授权的外部 Chrome / Chromium 浏览器上下文，通过 Playwright 优先、CDP 作为底层通道执行浏览器自动化。

“受控”意味着目标来源必须属于以下之一：

1. **Peer-managed profile**：由 Peer 启动独立浏览器进程和独立 User Data Dir；
2. **Explicit attach**：用户在 UI 中明确选择并批准接管某个可调试浏览器实例；
3. **Temporary context**：为单次任务创建临时 Browser Context，任务结束即可销毁。

禁止扫描并静默接管本机任意浏览器调试端口，也禁止默认附着用户日常 Profile。

#### Playwright 与 CDP 的职责

- **Playwright 是首选语义层**：提供 locator、auto-wait、frame/page/context、download、dialog 和稳定截图；
- **CDP 是连接与补充层**：用于 attach、Target 发现、底层网络/页面事件以及 Playwright 暂不覆盖的 Chromium 能力；
- Provider 不向模型暴露原始 Playwright API 或任意 CDP command，以免绕过动作白名单、权限和 Evidence。

#### 目标模型

```ts
type ExternalBrowserTarget = {
  environmentId: string;
  browserContextId: string;
  pageId: string;
  frameId?: string;
};
```

`environmentId` 是本地注册表发放的短期句柄，不是 CDP WebSocket URL。Registry 必须记录所有者 conversation、启动/附着来源、profile 类型、当前页面和生命周期。

#### 相比 L1 的新增价值

- 可以使用独立或授权 Profile 中的真实登录态；
- 多页面、多窗口、frame、下载、上传和 dialog 处理更稳定；
- locator 与 auto-wait 比纯坐标操作可靠；
- 能在不占用 Workbench 布局的情况下运行长任务，同时可通过预览画面保持透明。

#### 产品要求

L2 必须有“受控浏览器”可见状态：显示当前实例、Profile 类型、页面、控制中状态和立即停止入口。后台执行不等于不可见执行；用户应能打开实时预览或切到目标浏览器观察。

### 5.3 L3：macOS OS UI

#### 定义

在用户明确授权后，观察并操控 macOS 前台应用 UI。底层由三类系统能力组合：

1. **macOS Accessibility（AX）**：读取可访问性树、定位窗口/控件、执行 press / set value 等语义动作；
2. **屏幕录制权限**：通过 ScreenCaptureKit 或系统截图 API 获取受控显示器/窗口图像；
3. **键鼠注入**：通过 CGEvent 等系统接口执行坐标点击、移动、滚动、按键和文本输入。

三者权限相互独立：获得屏幕录制不代表可操作；获得 Accessibility 也不代表可采集所有窗口像素。应用必须分别检测、解释和申请。

#### 目标模型

```ts
type MacOSUITarget = {
  environmentId: string;
  bundleId: string;
  pid: number;
  windowId?: number;
  displayId?: number;
};
```

任何动作至少绑定 `bundleId + pid`；窗口动作尽量绑定 `windowId`。如果目标窗口或进程身份变化，应失败并要求重新观察，不得把坐标动作静默落到另一个应用。

#### 语义优先级

```text
Accessibility 语义动作
  > Accessibility frame + 坐标动作
    > 纯截图视觉定位 + 坐标动作
```

可访问性树能标识按钮、文本框或菜单时，优先使用稳定的 element ref。只有目标没有 AX 语义、AX 行为失效或画布类应用时，才使用视觉坐标。

#### 前台和焦点约束

- 默认只允许操作用户可见的前台应用或明确选择的窗口；
- 动作前验证 active application、pid、windowId 与最近观察一致；
- 焦点漂移、窗口移动、显示器缩放变化、屏幕锁定时立即停止；
- 每次批量动作设置短有效期和最大动作数，禁止长时间持有无边界控制权；
- 菜单栏、系统设置、权限弹窗、密码框属于更高风险区域，需要额外确认或直接禁止。

## 6. 统一动作协议

### 6.1 协议形状

模型不直接调用三套底层 API，而是调用稳定的 Computer Use 动作：

```ts
type ComputerEnvironmentKind =
  | 'embedded_browser'
  | 'external_browser'
  | 'macos_ui';

type ComputerAction =
  | { type: 'observe'; include?: Array<'screenshot' | 'dom' | 'accessibility' | 'metadata'> }
  | { type: 'navigate'; url: string }
  | { type: 'click'; target?: ElementRef; point?: Point; button?: 'left' | 'right'; count?: 1 | 2 }
  | { type: 'type'; target?: ElementRef; text: string; replace?: boolean; submit?: boolean }
  | { type: 'key'; keys: string[] }
  | { type: 'scroll'; target?: ElementRef; deltaX: number; deltaY: number }
  | { type: 'hover'; target?: ElementRef; point?: Point }
  | { type: 'drag'; from: ElementRef | Point; to: ElementRef | Point }
  | { type: 'wait'; condition?: WaitCondition; timeoutMs?: number }
  | { type: 'stop' };

type ComputerActionRequest = {
  actionId: string;
  environmentId: string;
  expectedObservationId?: string;
  target: ComputerTarget;
  action: ComputerAction;
};
```

### 6.2 乐观并发保护

`expectedObservationId` 表示模型基于哪次观察做出动作。Provider 执行前检查环境版本：如果页面导航、窗口焦点、大小或目标树已变化，返回 `stale_observation`，要求重新观察。

这避免模型根据旧截图点击已经移动或被覆盖的位置，是 L2/L3 的必要安全条件。L1 也应逐步接入。

### 6.3 ElementRef

ElementRef 是 Environment Adapter 根据 DOM 或 Accessibility 树发放的短期引用：

```ts
type ElementRef = {
  observationId: string;
  ref: string;
  role?: string;
  name?: string;
};
```

引用仅在对应 observation 和 environment 内有效。它不能是任意 CSS selector、XPath、AX path 或 JS 表达式；底层 locator 细节由 Adapter 封装，防止模型绕开动作与权限边界。

### 6.4 现有 browser_* 兼容

短期不要求立即删除 `browser_*`。迁移策略：

1. 现有公开工具保持兼容；
2. 内部先将它们映射到统一 Computer Action / Observation；
3. L2/L3 上线时优先投影 `computer_*` 通用工具，环境由明确 target 决定；
4. 只有在模型质量、权限 UX 和历史会话兼容验证完成后，才评估收敛旧工具名。

不允许简单把 `browser_click` 扩成“也能点 macOS”；同名工具跨越完全不同风险域会破坏用户预期。

## 7. 统一观察协议

```ts
type ComputerObservation = {
  observationId: string;
  environmentId: string;
  environmentKind: ComputerEnvironmentKind;
  target: ComputerTarget;
  capturedAt: string;
  viewport?: { width: number; height: number; scaleFactor: number };
  screenshotArtifactRef?: string;
  semanticTreeArtifactRef?: string;
  metadata: {
    url?: string;
    title?: string;
    bundleId?: string;
    appName?: string;
    windowTitle?: string;
    active: boolean;
  };
  elements?: Array<{ ref: string; role?: string; name?: string; bounds?: Rect }>;
};
```

约束：

- 截图、完整 DOM、AX 树属于大体积或敏感数据，落本地 artifact；模型默认只收到受限预览、元素摘要和 ref；
- 截图必须记录逻辑尺寸、像素尺寸和 scale factor，坐标统一使用观察时的逻辑坐标；
- L2 记录 URL、page/context；L3 记录 bundleId、pid、windowId、活动状态；
- 观察结果不得包含密码框值、认证令牌、Cookie 或隐藏输入内容；
- Adapter 应对敏感区域提供遮罩钩子，截图 artifact 也应带敏感级别和保留策略。

## 8. Orchestrator 与 Adapter 边界

### 8.1 Computer Use Orchestrator

Orchestrator 是本地主链中的执行协调器，不是第二个 Agent。它负责：

- 校验 environment / target / observation 生命周期；
- 将通用动作路由到正确 Adapter；
- 在执行前后采集最小必要观察；
- 执行动作数、时长、重试和停止限制；
- 统一错误、脱敏结果、artifact 与 Evidence；
- 在需要时触发 PermissionReview。

它不负责拆任务、识别用户意图、规划网页流程或决定下一步动作。

### 8.2 Environment Adapter

每个 Adapter 只处理宿主差异：

| Adapter | 权威目标 | 语义观察 | 动作执行 |
|---|---|---|---|
| EmbeddedBrowserAdapter | conversation + browserTab + webContents | DOM + capturePage | webContents / renderer bridge |
| ExternalBrowserAdapter | environment + context + page + frame | Playwright locator / DOM + screenshot | Playwright，必要时受限 CDP |
| MacOSUIAdapter | bundleId + pid + windowId | AX tree + ScreenCaptureKit | AX action + CGEvent |

Adapter 不自行判断用户是否授权，不向模型直接暴露底层任意调用，也不持有跨会话全局“当前目标”。

## 9. 权限与安全

### 9.1 两层权限必须分开

1. **操作系统权限**：macOS Screen Recording、Accessibility 等，由系统设置授予应用；
2. **Peer PermissionGrant**：用户针对某次任务、某个环境、某类动作给予的产品内授权。

OS 已授权不等于 Agent 已获准。Peer 仍须在每次能力调用或明确的限时 session grant 上执行 PermissionReview。

### 9.2 建议风险分级

| 风险 | 示例 | 默认策略 |
|---|---|---|
| 低 | observe、读取非敏感页面元数据、wait | 可按 session 授权 |
| 中 | 导航、普通点击、滚动、在非敏感字段输入 | 首次 ask，可限环境记忆 |
| 高 | 下载/上传文件、发送消息、提交表单、系统菜单、跨应用切换 | 动作前确认 |
| 禁止或特别确认 | 密码/支付、删除账号、钥匙串、安全与隐私设置、绕过系统权限 | 默认拒绝；如产品允许则逐次强确认 |

输入文本是敏感面：Permission UI 可以说明目标应用/域名和字段语义，但不得原样展示或记录密码、token 和隐私文本。

### 9.3 环境隔离

- L1：继续使用与主应用隔离的 browser partition；
- L2：默认 Peer-managed 或 temporary profile；attach 用户 Profile 必须显式授权；
- L3：限定 bundleId/pid/window，禁止默认全桌面无差别控制；
- 所有环境句柄绑定 conversation 与本地宿主生命周期；会话结束、应用退出、用户停止或权限撤销时失效。

### 9.4 立即停止

Desktop 必须提供全局清晰的“停止控制”入口，并满足：

- 中止待执行动作队列；
- 释放按键/鼠标状态；
- 断开或降级外部浏览器 attach；
- 使 environment grant 和 ElementRef 失效；
- 写入停止原因和最后状态 Evidence。

## 10. Evidence 架构

每次动作至少生成一条结构化 Evidence：

```ts
type ComputerActionEvidence = {
  actionId: string;
  environmentId: string;
  environmentKind: ComputerEnvironmentKind;
  targetSummary: string;
  actionType: ComputerAction['type'];
  permissionGrantId: string;
  startedAt: string;
  endedAt: string;
  status: 'succeeded' | 'failed' | 'denied' | 'cancelled';
  beforeObservationRef?: string;
  afterObservationRef?: string;
  artifactRefs?: string[];
  errorCode?: string;
  redactions?: string[];
};
```

Evidence 原则：

1. **事实与解释分离**：动作、目标、状态是结构化事实；模型总结不是执行证据；
2. **大内容引用化**：截图、DOM、AX 树存 artifact，只回 ref 和受限摘要；
3. **输入最小化**：默认记录“向某字段输入了 N 个字符”，不记录原文；
4. **可关联**：Observation、Action、PermissionGrant、Tool Call 和 Conversation 可互相追溯；
5. **可保留/可删除**：敏感截图使用短保留期；删除会话时按既有策略级联处理相关 artifact；
6. **失败也留证**：拒绝、目标漂移、权限缺失和用户中止都必须有结构化结果。

## 11. 错误模型

统一错误码至少包括：

- `environment_not_found`
- `target_not_found`
- `target_not_active`
- `stale_observation`
- `element_not_found`
- `element_not_interactable`
- `permission_required`
- `permission_denied`
- `os_permission_missing`
- `focus_changed`
- `navigation_blocked`
- `action_timeout`
- `user_cancelled`
- `unsupported_action`

错误结果必须说明可恢复动作（重新观察、请求权限、选择目标、切回前台），不得把底层 Playwright/CDP/AX 异常裸露给模型或用户。

## 12. Runtime Projection 与宿主策略

### Desktop

Desktop 是三档 Computer Use 的主宿主。投影能力前必须同时满足：

- 对应 Adapter 已注册；
- 当前平台与版本支持；
- environment 已创建或存在可引导的创建流程；
- modeScopes 允许；
- 权限策略和 Evidence sink 可用。

### CLI / TUI

CLI/TUI 继续是一等宿主，但没有可视桌面环境时不得投影 L1/L3。L2 只有在 CLI 明确启动/连接受控浏览器、具备同等 PermissionGrant 和 Evidence 链时才能投影；不能用无头 `web_fetch` 冒充 Computer Use。

工具协议可共享，环境能力必须诚实。共享 Runtime 不意味着所有宿主暴露相同的物理能力。

## 13. 实施顺序

### Phase 0：固化 L1 基线

- 为现有 `browser_*` 补齐统一 Observation/Evidence 映射；
- 加入 wait、scroll、key 等基础动作；
- 为截图加入 viewport / scale factor；
- 引入 observationId 与目标漂移检测；
- 保持 ADR 40、ADR 46 的会话与标签隔离。

### Phase 1：建立统一协议与 Orchestrator

- 在 protocol/runtime 层定义 Environment、Target、Action、Observation、Evidence；
- 建立 Adapter registry 和生命周期；
- 现有 L1 Provider 作为第一个 Adapter 接入；
- 保持旧 `browser_*` 兼容适配，避免一次性迁移工具面。

### Phase 2：受控外部浏览器

- 先实现 Peer-managed temporary profile（第一刀已落地：独立 `browser_external_*` / `local.web.external.*`，见 ADR 71）；
- 再实现持久 Peer-managed profile；
- 最后评估 Explicit attach 用户浏览器；
- 默认走 Playwright，CDP 只作为受限底层；
- 补实时预览、停止、profile 与下载治理。

### Phase 3：macOS OS UI

- 先做只读观察：权限状态、窗口列表、截图、AX 摘要；
- 再做低风险语义动作：选择明确应用窗口、普通按钮/文本框；
- 再做受限坐标动作和键鼠注入；
- 最后才评估跨应用工作流、高风险系统区域和批量动作授权。

每个 Phase 必须先通过自动化协议测试、权限测试、Evidence 测试和人工可见性验证，再进入下一阶段。

## 14. 验收要求

### 统一协议

- 三个 Adapter 消费同一 ComputerAction，产出同一 ComputerObservation / Evidence；
- 模型看不到 CDP URL、webContentsId、AX 原始句柄；
- stale observation 能阻止目标变化后的误点击。

### L1

- Agent 只能操作发起 conversation 的 active browser tab；
- 截图、DOM 与动作结果形成可追溯 Evidence；
- 用户可以在 Workbench 中看到动作并立即停止。

### L2

- 默认不会接管用户日常浏览器 Profile；
- environment/context/page 身份在导航、多页面和重连后仍可验证；
- Playwright 动作、下载和 screenshot 都经过 PermissionGrant 与 Evidence。

### L3

- 缺失 Screen Recording 或 Accessibility 时给出明确引导，不循环触发系统弹窗；
- 目标焦点或 pid/window 变化时动作失败而非落到别的应用；
- 密码、支付、系统安全设置等区域默认拒绝或逐次强确认；
- 停止入口可以中断动作并释放输入状态。

## 15. 关键决策与取舍

### 为什么按环境分三档

风险、目标身份和执行技术差异真实存在。把三档伪装成一个“万能点击器”会让授权不可理解；完全拆成三套工具又会破坏协议复用。正确边界是：**统一动作与证据，显式环境与 Adapter**。

### 为什么先 Browser、后 OS UI

Browser 有 DOM/locator、URL、页面生命周期和更强的隔离边界，动作可解释性远高于全桌面像素操作。OS UI 涉及全局输入、焦点漂移和系统隐私权限，必须建立在成熟的环境、观察、授权和停止机制上。

### 为什么 Playwright 优先于裸 CDP

Playwright 提供稳定 locator、auto-wait 和跨页面抽象，能把底层时序复杂度留在 Adapter 内。裸 CDP 面过大，直接投影给模型会形成高权限旁路；它只应作为连接和特殊能力补充。

### 为什么 AX 优先于纯视觉坐标

AX 元素有角色、名称、状态和 frame，更适合验证动作目标。纯视觉坐标容易受缩放、窗口移动、动画和遮挡影响，应作为没有语义信息时的降级路径，而不是默认路径。

## 16. 关联文档

- `knowledge/decisions/40-embedded-browser-and-agent-control.md` — L1 内嵌 Browser 载体、直控桥与安全基线
- `knowledge/decisions/46-conversation-bound-browser-tabs.md` — conversation / browser tab 目标隔离
- `knowledge/architecture/20-architecture-governance.md` — Capability、PermissionGrant、Evidence 主链
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — Desktop / CLI 宿主边界
- `knowledge/architecture/desktop-cli-local-capability-parity.md` — Desktop-only 可视浏览器能力与 CLI 诚实投影
- `knowledge/decisions/35-mode-scoped-tool-projection.md` — 模式能力投影
- `knowledge/decisions/37-provider-channel-and-wire-protocol-separation.md` — Provider channel / wire 分离

## 17. 后续 ADR

本文确认能力阶梯与共享边界，但下列实现决策应各自形成 ADR：

1. Computer Action / Observation 协议及旧 `browser_*` 迁移；
2. Playwright/CDP ExternalBrowserAdapter、Profile 与 attach 安全模型；
3. macOS Accessibility / ScreenCaptureKit / CGEvent Adapter 与系统权限 UX；
4. Computer Use artifact 敏感分级、保留期和删除策略；
5. 高风险动作分类与 human-in-the-loop 规则。

在这些 ADR 完成前，不应直接加入“控制任意外部浏览器”或“控制整台 Mac”的宽权限工具。
