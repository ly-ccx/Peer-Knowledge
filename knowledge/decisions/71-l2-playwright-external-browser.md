# 71. L2 受控外部浏览器（Playwright / CDP）安全模型

创建时间：2026-09-01
最后更新：2026-09-01

## 状态

Accepted。L2 第一刀已在 `peer_agent` 落地：temporary Peer-managed Playwright 会话、独立 `browser_external_*` / `local.web.external.*` 契约与 capability。持久 Peer-managed profile 与 Explicit attach 仍未实现。

## 级别

A 级 —— 新增 Environment Adapter（`ExternalBrowserAdapter`）、独立浏览器进程与 Profile 生命周期、download/dialog 权限面，以及 Computer Use artifact 敏感分级。改变能力暴露、权限与 Evidence 边界。

## 背景

ADR 40 / 46 / 59 / 66 / 70 已把 **L1 内嵌 Browser** 做成用户可见的 Electron `<webview>` 直控面。P0 修了点击正确性（逻辑坐标、auto-wait、`buildElementJs` 跨 iframe）；P1 补齐单页动作：hover / scroll / key / drag。模型现在面对的 L1 工具是：

| 工具 | capabilityId |
|---|---|
| `browser_open_panel` | `local.web.control.openPanel` |
| `browser_navigate` | `local.web.control.navigate` |
| `browser_click` | `local.web.control.click` |
| `browser_type` | `local.web.control.type` |
| `browser_hover` | `local.web.control.hover` |
| `browser_scroll` | `local.web.control.scroll` |
| `browser_key` | `local.web.control.key` |
| `browser_drag` | `local.web.control.drag` |
| `browser_screenshot` | `local.web.control.screenshot` |
| `browser_read_dom` | `local.web.control.readDom` |

这仍覆盖不了：真实登录态 / 独立 Profile、多 page / 多 context、download、dialog、长任务不占 Workbench。能力阶梯把这些放在 **L2：受控外部浏览器（Playwright / CDP）**，并要求落地前先写 ADR：Profile 与 attach 安全模型、download/dialog 权限、artifact 敏感分级。

代码仓当前 **没有 Playwright 依赖**。本 ADR 决定 L2 怎么接、接什么、不接什么。

## 决策

### 决策一：Playwright 是 Adapter，不是新工具面

L2 与 L1 **共享同一套 `browser_*` 工具名与 `ComputerAction` 契约**，按 `environment` 路由到 Adapter：

```text
Capability Provider
  → Manifest
    → Runtime Projection
      → Tool Call(browser_*)
        → PermissionGrant
          → Environment Adapter
               ├─ EmbeddedBrowserAdapter   (L1, 已有)
               └─ ExternalBrowserAdapter   (L2, Playwright 优先 / CDP 受限底层)
          → Evidence
```

- 模型 **不** 看到 `playwright_*`、`cdp_*` 或任意 CDP command。
- 不把 Playwright API 投影成工具。locator / auto-wait / download 事件留在 Adapter 内。
- 现有 L1 `browser_*` 保持兼容；不一次性迁移工具面。
- CLI 继续诚实投影：可视浏览器（含 L2）为 Desktop 专属，不适用 CLI。

新增的 L2 专属动作（download 确认、dialog 处理、选 page/context）可以是新 capability，但仍走同一主链，并登记进显式 Desktop-only 契约列表（与 ADR 70 同一纪律：禁止 `browser_` 前缀通配）。

### 决策二：目标来源只有三类，禁止静默 attach

「受控」意味着目标必须属于：

1. **Peer-managed profile**  
   Peer 启动独立 Chromium 进程 + **独立 User Data Dir**（不复用用户日常 Chrome/Edge Profile）。分两种：
   - **Temporary context**：单次任务 / 会话级，任务结束或用户停止即销毁。
   - **Persistent Peer-managed profile**：用户明确创建的「Peer 浏览器」配置，可保留登录态；与日常浏览器隔离。

2. **Explicit attach**  
   用户在 UI 中选择并批准接管某个 **可调试** 浏览器实例（用户开启 remote debugging 后出现在候选列表）。批准绑定 conversation 与生命周期。

3. **Temporary context**（可挂在 1 之下）  
   为单次任务创建 Browser Context，不写持久 Profile。

禁止：

- 扫描本机任意调试端口并静默接管；
- 默认附着用户日常 Chrome/Edge/Safari Profile；
- 把 L1 `<webview>` / `webContents.fromId` 伪装成 Playwright page。

实现顺序（与能力阶梯 Phase 2 一致）：

1. Peer-managed **temporary** profile（默认、最低风险）；
2. 持久 Peer-managed profile（用户显式创建）；
3. 最后评估 Explicit attach。

### 决策三：L1 与 L2 不互相接管

| | L1 内嵌 | L2 外部 |
|---|---|---|
| 载体 | Workbench `<webview>` | 独立 Chromium 进程 |
| 执行 | `webContents` + `sendInputEvent` / `executeJavaScript` | Playwright page/context（CDP 仅 Adapter 内部） |
| 登录态 | `persist:peer-browser` 分区 | Peer-managed User Data Dir 或用户批准的 attach |
| 默认入口 | 网页任务默认走 L1 | 仅当任务需要独立 Profile / 多页 / download / dialog / 长任务不占布局 |

- Playwright **不得** 接手 L1 内嵌页。
- L2 需要可见状态：当前实例、Profile 类型（temporary / persistent / attached）、页面 URL、控制中、**立即停止**。后台执行 ≠ 不可见；用户可打开预览或切到目标窗口。
- Environment 句柄绑定 conversation 与本地宿主生命周期；会话结束、应用退出、用户停止或权限撤销时失效。

### 决策四：download / dialog 权限分级

L1 没有 download/dialog。L2 引入后必须进 PermissionGrant，不能靠 prompt 当唯一闸门。

| 动作 | 风险 | 默认 | 说明 |
|---|---|---|---|
| 观察（截图 / DOM 摘要 / 元数据） | 中 | ask，可按 session 记忆 | 大体积落 artifact |
| 导航、普通点击、滚动、hover | 中 | 首次 ask，可限环境记忆 | 与 L1 同级 |
| 输入（非敏感字段） | 中 | ask | 文本不原样进授权卡片 / Evidence 模型可见面 |
| **dialog**（alert/confirm/prompt/beforeunload） | 高 | 动作前确认 | 默认不自动 accept；prompt 输入视为敏感 |
| **download** | 高 | 动作前确认 | 指定保存目录（Peer 管理的 download 区，不默认用户「下载」文件夹）；记录文件名、MIME、大小、敏感级 |
| **upload / 文件选择** | 高 | 动作前确认 | 只允许用户已授权的本地路径 |
| 提交表单、发送消息 | 高 | 动作前确认 | |
| 密码 / 支付 / 删除账号 | 禁止或特别确认 | 默认拒绝 | |

download 产物：

- 写入 Peer 管理目录（conversation 级），不自动打开、不自动执行；
- Evidence 记路径引用 + 元数据，不把文件字节回灌模型；
- 可执行文件、安装包、脚本默认更高敏感级，需额外确认才保留。

dialog：

- Adapter 拦截 Playwright dialog 事件，转成 PermissionReview，不自动点确定；
- 模型只收到 dialog 类型 + 截断文案，不把 prompt 默认值当用户输入。

### 决策五：artifact 敏感分级

沿用 ADR 63：Evidence ≠ UserArtifact。L2 额外规定 Computer Use 产物分级：

| 级别 | 例子 | 模型默认可见 | 保留 |
|---|---|---|---|
| D1 内部 | 页面标题、URL host、动作摘要、locator 失败原因 | 是（截断） | 会话级 |
| D2 敏感 | 完整 DOM、AX 树、截图、表单字段名 | 摘要 + artifact_ref | 有限期；用户可删 |
| D3 高敏感 | 下载文件、password 框值、Cookie、dialog prompt 输入、支付页截图 | **否**；只给 ref 与敏感标记 | 更短保留；默认不进 UserArtifact 列表 |

约束：

- 截图记录逻辑尺寸、像素尺寸、scale factor；坐标用观察时逻辑坐标（与 L1 / 阶梯一致）。
- 观察结果不得包含密码框值、认证令牌、Cookie、隐藏 input。
- Adapter 应对敏感区域提供遮罩钩子。
- UserArtifact 仍只能由 Provider 结构化 Tool Result 产生（截图预览、下载文件条目），Renderer 不从路径字符串猜测。

### 决策六：Playwright vs CDP

- **Playwright**：首选语义层（locator、auto-wait、frame/page/context、download、dialog、稳定截图）。
- **CDP**：连接与补充层（attach、Target 发现、Playwright 未覆盖的 Chromium 事件）。Adapter 内白名单 CDP 方法，禁止把 CDP 当通用 RPC 暴露给模型。
- 错误对模型/用户可恢复（重新观察、请求权限、选择目标），不裸传 Playwright/CDP 堆栈。

## 后果

- 网页任务默认仍是 L1；L2 是显式环境，不是替换内嵌浏览。
- 实现后 Desktop-only 契约可能增加 L2 专属 capability（选环境、download、dialog）；必须显式登记，不能靠前缀。
- 需要独立 Chromium 分发或复用 Playwright 的 browser 下载；体积与更新策略在实现 ADR/切片里定，不在本决策展开。
- 持久 Peer-managed profile 会保存登录态：这是产品价值，也是泄露面；目录权限、备份、删除必须进实现清单。

## 明确不做

- 不用 Playwright 接管 L1 `<webview>`。
- 不向模型暴露裸 Playwright API 或任意 CDP command。
- 不默认附着用户日常浏览器 Profile。
- 不扫描并静默 attach 本机调试端口。
- 不做 L3 macOS OS UI（另开 ADR）。

## 实现进度

第一刀已落地（Desktop-only）：

1. `ExternalBrowserAdapter`：temporary Peer-managed profile；conversation 绑定；`open` / `close` 启停销毁。
2. 独立工具面 `browser_external_*` → `local.web.external.*`，**不**把 L1 `browser_*` 路由进 Playwright。
3. 默认白名单：navigate / click / type / screenshot / readDom / hover / scroll。
4. download / dialog 本切片拒绝并给出可恢复错误；页面事件会 cancel/dismiss，不向模型暴露 CDP。
5. L2 仍登记在 `DESKTOP_ONLY_LOCAL_TOOL_CONTRACTS`，CLI/TUI 不执行该 Adapter。

尚未落地：

- 持久 Peer-managed profile。
- Explicit attach。
- L2 专属 download / dialog capability 与 PermissionGrant。
- 受控浏览器可见状态面板 / 立即停止 UI。

## 参考

- `knowledge/architecture/computer-use-capability-ladder.md` §5.2 / §6 / Phase 2 / 待补 ADR 第 2、4 项
- ADR 40 内嵌浏览器
- ADR 63 用户产物与 Evidence 边界
- ADR 70 L1 动作面（hover/scroll/key/drag）
- `knowledge/architecture/browser-capability-gap.md` P2
- `knowledge/architecture/desktop-cli-local-capability-parity.md`（可视浏览器 Desktop 专属）
