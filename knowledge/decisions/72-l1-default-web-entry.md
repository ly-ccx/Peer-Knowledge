# 72. 网页任务默认入口：L1 内置浏览器（`browser_*`）

创建时间：2026-09-02
最后更新：2026-09-02（第一刀系统提示落地）

## 状态

Accepted（第一刀已落地：系统提示）。产品边界钉死为 L1 `browser_*`。`peer_agent` 已增加 `runtime.web-entry` Context Source，并在 `browser_external_open` 提示中写明 L2 不是默认网页入口。本切片**不**删除 `browser_external_*` 投影。locator / 等待补全仍属后续切片。

## 级别

A 级 —— 变更网页任务的默认执行面与模型可见入口：默认走 L1 `browser_*` / `local.web.control.*`，L2 `browser_external_*` 不再作为默认执行面。

## 背景

能力阶梯 §5.1 已写「L1 应作为网页任务默认入口」；ADR 71 决策三表格也写「网页任务默认走 L1」。但这两处都是顺带一句，没有单独成文回答：

- 模型做网页任务时，第一选择是哪套工具；
- L2 Playwright 会话什么时候才允许上场；
- 「后续所有操作都在内置浏览器承接」覆盖到哪一层，哪一层永远接不住。

当前事实：

- L1 是用户眼前的 Workbench `<webview>`，会话绑定见 ADR 46，登录态在共享分区 `persist:peer-browser`，面板缺席时可按 ADR 66 降级到同一分区的隐藏 WebContents。模型看到 `browser_*`。
- L2 第一刀已落地（ADR 71）：独立临时 Playwright 会话、`browser_external_*` / `local.web.external.*`。它不接管 L1 webview，也不向模型暴露 Playwright/CDP。renderer 没有对应面板。
- 用户明确要求：先不要把 Playwright 当默认执行面；网页操作应落在用户能看见的内置浏览器里。选择 D：先写 ADR，再改代码。

若不把默认入口钉死，L1 缺口会继续被「去开 L2」短路，用户眼前的页面和 Agent 实际操作的页面会分叉。

## 决策

### 决策一：网页任务默认入口是 L1 `browser_*`

Agent 处理网页任务时，默认只走：

```text
Capability Provider(local.web.control.*)
  → Manifest
    → Runtime Projection
      → Tool Call(browser_*)
        → PermissionGrant
          → Evidence
```

具体约定：

1. 打开、导航、点击、输入、悬停、滚动、按键、拖、截图、读 DOM，一律针对当前 conversation 的内嵌 Browser（可见 `<webview>`，或 ADR 66 的同一分区 headless 降级）。
2. 用户应能在 Workbench Browser 面板看到页面变化；headless 降级必须在 PermissionGrant / Evidence 上标注 `headless: true`，不得假装成另一套浏览器。
3. 登录态继续用 `persist:peer-browser`。这是 Peer 自己的持久分区，不是用户日常 Chrome Profile。

### 决策二：L2 不再作为默认执行面

L2（`browser_external_*` / `local.web.external.*` / Playwright Adapter）仍然存在，但**不是**网页任务的默认路径。

禁止：

- 因为 L1 点不准、缺 locator、缺 download/dialog，就把任务默默切到 Playwright；
- 把 L1 `<webview>` 伪装成 Playwright page；
- 向模型暴露裸 Playwright API 或任意 CDP command（沿用 ADR 71）。

允许 L2 上场的条件（必须显式，不能当默认）：

- 任务需要**独立 Profile**（与 `persist:peer-browser` 隔离的登录态）；
- 任务需要**多 page / 多 context**，且 L1 单 WebContents 接不住；
- 任务需要 L2 才有的 download / dialog 治理（在对应 capability 落地之前，L2 仍按 ADR 71 第一刀拒绝）；
- 长任务不应占 Workbench 布局，且用户知道这是独立外部会话。

在上述条件成立之前，实现切片应把缺口补进 L1，而不是扩大 L2 的默认投影。

本 ADR **不**要求立刻从模型可见工具列表删除 `browser_external_*`。那是后续实现切片的产品选择（藏起 / 降权 / 仅在显式环境里投影）。本决策只禁止把它当默认入口。

### 决策三：「所有操作都在内置浏览器承接」的边界

这句话的产品含义是：

- 默认网页操作发生在用户眼前的 L1 页面上；
- L1 还缺的单页能力（更稳定位、等待、文件选择、以及将来若纳入 L1 的 dialog/download）优先补 L1。

这句话**不**覆盖：

| 永远不是 L1 | 原因 |
|---|---|
| 用户日常 Chrome / Edge / Safari Profile、扩展、已有标签 | ADR 46 / 71：L1 只用 `persist:peer-browser`；附着外部日常浏览器属 L2 Explicit attach，且默认禁止静默附着 |
| 系统原生窗口、桌面 UI | 能力阶梯 L3 |
| 完整 Chrome History 页、跨会话恢复 history stack | ADR 46：跨会话只恢复标签集合与 URL |
| 把 Playwright 塞进 webview 来「补齐」 | 不同执行面；会破坏会话、权限与 Evidence |

L1 接得住的上限：Workbench 内、Peer 分区、当前 conversation 的网页。超出这个上限，要么补 L1 能力，要么显式走 L2/L3，不能假装已经接住。

### 决策四：后续实现顺序

本 ADR 落地后的代码切片按这个顺序，不得颠倒成「先把默认切到 Playwright」：

1. **投影与提示**：网页任务默认只强调 `browser_*`；L2 不得在系统提示里被写成常规网页入口。**已落地**：`runtime.web-entry` Context Source + `browser_external_open` 提示降权。尚未从模型可见列表删除 L2。
2. **L1 正确性**：locator（text / role / nth）、等待补全（enabled / 遮挡 / stale）、减少纯几何中心点击、真机 Retina+缩放验收。**部分落地**：`browser_click` / `browser_type` / `browser_hover` 已可按 `role`/`name` 定位，并用 0 起 `nth` 消歧；text / testid、等待补全与真机验收仍属后续切片。
3. **L1 单页加分**：check、双击、右键、文件选择器。dialog / download 若要进 L1，必须另开 A 级 ADR，不得 silently 塞进本决策。
4. **L2**：仅在决策二的显式条件下继续（持久 Peer-managed profile、attach、download/dialog capability）。

## 后果

- 用户与 Agent 共同观看同一页面，授权和停止路径更短。
- L1 缺口不能再靠「去开 L2」回避；点不准必须继续修执行器。
- L2 代码可以保留，但产品叙事从「第二套默认浏览器」改为「显式独立环境」。
- CLI/TUI 仍无可见 webview；Desktop-only 契约与 parity 排除列表不变（ADR 70 / 71）。headless 降级仍是 L1，不是 L2。

## 不做（Non-goals）

- 本 ADR 原文不改代码；第一刀实现只加系统提示，不删 `browser_external_*`。
- 不把 L1 做成用户日常浏览器的替身。
- 不在本 ADR 里规定 dialog / download 必须进 L1。
- 不重开「用 Playwright 接手内置页」的讨论。

## 实现时必改（评审通过后的代码切片，不在本轮）

- 系统提示 / Context Source：网页任务默认入口写成 `browser_*`（第一刀已落地：`packages/system-context/src/sources/web-entry-source.mjs`）。
- 若选择隐藏 L2：Runtime Projection 与 Desktop-only 契约的模型可见集合。
- L1 缺口实现仍走 `local.web.control.*` Provider，不走 ExternalBrowserAdapter。

## 相关

- ADR 40 内嵌浏览器与 Agent 直控
- ADR 46 会话绑定标签与 `persist:peer-browser`
- ADR 59 面板 reveal
- ADR 66 headless 降级（仍属 L1）
- ADR 70 L1 动作面
- ADR 71 L2 Playwright 安全模型（L2 仍有效，但不再是默认入口）
- `knowledge/architecture/computer-use-capability-ladder.md` §5.1 / §5.2
- `knowledge/architecture/browser-capability-gap.md`
