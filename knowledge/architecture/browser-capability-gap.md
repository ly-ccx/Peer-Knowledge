# 内置浏览器能力缺口（对 Playwright 水位）

> 状态：诊断（Draft）；P1 动作面见 [ADR 70](../decisions/70-l1-browser-action-surface.md)；P2 外部浏览器见 [ADR 71](../decisions/71-l2-playwright-external-browser.md)
> 范围：L1 内嵌 Browser（`local.web.control.*`）
> 基准：Playwright 元素定位 / auto-wait / frame / download / dialog / 多页能力面
> 目标：说明「为什么现有内置浏览器点不准、能力弱」，并给出修 L1 vs 加 L2 的边界结论。

## 1. 现状：能力清单

现有 `browser_*` 工具共 6 项，全部经
Capability Provider(`local.web.control.*`) → Manifest → Tool(`browser-tool-definitions.mjs`)
→ Runtime Projection → Tool Call → PermissionGrant → Evidence 主链。

| 工具 | capabilityId | 参数面 | 执行方式 |
|---|---|---|---|
| browser_open_panel | local.web.control.openPanel | 无 | reveal Workbench Browser |
| browser_navigate | local.web.control.navigate | url | `loadURL` |
| browser_click | local.web.control.click | selector 或 x/y | `queryDeep`（主文档 / iframe / open shadowRoot）+ `getBoundingClientRect` 中心点 + `sendInputEvent` |
| browser_type | local.web.control.type | selector + text | focus + `sendInputEvent(char)` |
| browser_screenshot | local.web.control.screenshot | - | `capturePage` |
| browser_read_dom | local.web.control.readDom | selector | `executeJavaScript` 采集 innerText/outerHTML |

执行层（`local-browser-control-provider.mjs`）只触及单个 `WebContents`：
`loadURL / executeJavaScript / sendInputEvent / capturePage`。

## 2. 为什么点不准（根因）

`browser_click` 不是元素级点击，而是「先找中心点，再打像素」，整条链都脆：

1. **定位方式**：原先 `document.querySelector` 只在**主 frame** 里查，且只按 CSS 选择器命中**第一个**节点。
   - iframe 已可用 `frame:N` 前缀下钻；open shadowRoot 已由 `queryDeep` 递归进入。**closed shadow 仍查不到**。
   - 选择器命中不到预期节点（重复类名、动态 id）时仍会点错元素。
2. **坐标来源**：取 `getBoundingClientRect()` 的**几何中心点**，再通过 `sendInputEvent` 向该点打 `mouseDown/mouseUp`。
   - 几何中心 ≠ 可点击热区（圆形按钮、内边距、绝对定位覆盖层）；
   - 该点若被遮罩/浮动层覆盖，点击落到遮罩而非目标；
   - 目标是否 visible / stable / enabled，全都不校验。
3. **无等待（auto-wait）**：Playwright 默认等待元素可见、稳定、可交互；当前实现**直接取坐标就点**。
   - 动画未完成、懒加载未渲染、DSP 布局未稳定 → 取到的坐标是旧的；
   - 点击发生在正确坐标但目标尚未挂载 → 点到空白。
4. **坐标系不统一**：只用了 CSS 视口坐标，**未处理 devicePixelRatio（DPR）、zoom、`visualViewport`、滚动偏移**。
   - Retina 屏 / 网页缩放下，CSS 坐标与 `sendInputEvent` 期望的物理/逻辑坐标不一致 → 偏移；
   - 存在头部/侧栏偏移时，中心点没换算到 webContents 的视图坐标系。
5. **无目标漂移防护**：观察（读 DOM/截图）和点击之间页面可能变化，没有 `stale observation` 检测。
6. **回归测试**：click 路径已补 selector / 坐标 / `frame:N` 三条测试；坐标换算与 `buildElementJs`/`queryDeep` 另有单测。live Retina+缩放页面的端到端点击稳定性仍待人工验收。

**结论：这是 L1 执行器的问题，不是「没用 Playwright」这个口号能自动修好的。**坐标错是坐标系/等待/主 frame 限制同时作用的结果。

## 3. 缺失 / 薄弱能力矩阵（对照 Playwright）

schema 层面 `browser_*` 全部是**单向动作**（一个 capacity 一个动作），没有 Playwright 的组合动作与上下文模型。

| 维度 | Playwright 水位 | 当前 L1 状态 | 缺失性质 |
|---|---|---|---|
| 元素定位 | locator（text/role/testid/nth）+ 任意 CSS | CSS + `frame:N` + open shadowRoot（`queryDeep`）；`format=roles` 可扫 shadow | **剩余缺口**：closed shadow、text/role/testid/nth locator、多匹配 |
| 等待 | 默认 auto-wait（visible/stable/enabled）+ 显式 waitFor | `waitForElementStable`（click/type 接入） | **剩余缺口**：enabled/遮挡/stale observation |
| 坐标/缩放 | 统一逻辑坐标，维护 DPR/scale | 逻辑 CSS 坐标 + Evidence 记录 dpr/scale/scroll | **剩余缺口**：live Retina+缩放端到端验收 |
| 多动作 | hover / drag / key / scroll / check 等 | hover / scroll / key / drag 已落地 | **剩余缺口**：check 等 |
| hover | 悬停以触发 tooltip/子菜单 | `browser_hover` | 已落地（ADR 70） |
| scroll | 元素滚动 / 增量滚动 | `browser_scroll` | 已落地（ADR 70） |
| key 键盘 | press / type / shortcut | `browser_key` 白名单 + 修饰键 | 已落地（ADR 70）；文本仍走 type |
| frame | frameLocator 跨 iframe | `frame:N` 前缀 | 已落地；无 CSS iframe locator |
| dialog | 自动 accept/dismiss | 无 | 能力缺口 |
| download | 下载事件 / 文件保存 | 无 | 能力缺口 |
| 多页/多上下文 | 多 page / 多 context | 单 WebContents | 能力缺口（L1 不需要，L2 需要） |
| 可观测性 | force/position/timeout 参数 | 无 | 可调性缺口 |
| 错误可恢复 | 明确报可恢复动作 | 直接报底层异常 | 体验缺口 |

> 需要区分：**L1 内嵌 Browser** 是用户眼前正在看的页面，目标是与用户同看同操作，其「对齐 Playwright」应聚焦**元素定位 + auto-wait + 坐标系 + 补充动作（hover/scroll/key/drag）**；**多页/多上下文/download/dialog** 属于 **L2 受控外部浏览器** 的能力面，不应塞进 L1。

## 4. 架构边界结论：修 L1 vs 加 L2 Playwright

**不要把 Playwright 拿来替换 L1 内嵌浏览器。** 二者是能力阶梯里两档独立的 Adapter：

- **L1 内嵌 Browser**（已有）：Workbench 里用户正在看的 Electron `<webview>`，经 `webContents.fromId` 直控（ADR 40 / 46）。用户看到的就是 Agent 操作的，这是「与用户同看同操作」的窗口，**Playwright 无法也没必要替换**——Playwright 管理的是它自建/授权的 Chromium context，和 Electron 进程里的 WebContents 不是同一个执行面。
- **L2 受控外部浏览器**（Playwright / CDP）：连 Peer 创建或用户明确授权的 Chrome / Chromium 上下文。这才是 Playwright 该落的位置，用来补 L1 不能给的多页 / 下载 / 对话框 / 独立 profile 登录态。

**边界原则（不可越过）：**
- 模型始终只面对白名单后的 `browser_*` 工具，**不能拿到裸 Playwright API 或任意 CDP command**；
- 所有动作仍走 Capability → Manifest → Projection → Tool Call → PermissionGrant → Evidence；
- L1 / L2 共享同一套 ComputerAction 契约（observe/navigate/click/type/key/scroll/hover/drag/wait），靠 environment/Adapter 路由，而不是给模型两套工具面。

**所以：**
- 「点不准」→ **修 L1**，不是换 Playwright；
- 「要多页/下载/对话框/独立登录态」→ **加 L2 Playwright Adapter**，落地前需 ADR。

## 5. 可执行改造建议（优先级 + 验收口径）

### 优先级（先修正确性，再补能力）

**P0 —— 修 L1 点击正确性（直接治「点不准」）**
1. 坐标换算：读取 `devicePixelRatio`、`visualViewport`、zoom、页面滚动偏移，把 CSS 中心点正确映射到 webContents 视图坐标。✅ `computeViewportPoint()`（按契约保留逻辑坐标，记录 dpr/scale/scroll 观测字段）
2. 元素级定位：允许 CDP `Runtime.evaluate` + `getBoundingClientRect`，优先元素级动作；用 playwright 的 `ElementHandle` 语义替代纯坐标。✅ `buildElementJs(selector, body)` 统一元素定位（click/type/readDom/waitForElementStable 共用）。现用 `queryDeep` 在主文档 / iframe / **open shadowRoot** 里查第一个匹配；**closed shadow 仍不可达**。
3. auto-wait：点击/输入前等待目标 visible + stable + enabled（限定 timeout）。✅ `waitForElementStable()`（click/type 接入）
4. frame 支持：能跨主 frame / iframe 定位（固定 selector 前缀如 `frame:index`）。✅ `parseFrameSelector()` 解析 `frame:N` 前缀 + `buildElementJs()` 沿 `window.frames[i].document` 下钻跨 iframe 定位。

> **P0 落地记录（本次）**
> 改动文件：`local-browser-control-provider.mjs`
> - 新增 `sleep(ms)`、`computeViewportPoint(cssPoint, viewport)`、`waitForElementStable(wc, selector, opts)`（后两个已导出供单测）。
> - click 段：executeJavaScript 采集目标中心点 + `devicePixelRatio` + `visualViewport.scale` + `scrollX/scrollY`；经 `computeViewportPoint` 规范化；点击前 `waitForElementStable(1500ms/120ms)`；`outputPreview/output` 增加 `viewport` 字段（dpr/scale/scroll/css 坐标）。
> - type 段：focus 前 `waitForElementStable`。
> - 坐标契约：按 `computer-use-capability-ladder.md` 约束「坐标统一用逻辑坐标」，不对 x/y 做 DPR/物理放大，底层处理 scaleFactor；dpr/scale/scroll 仅作 Evidence/诊断字段。
> - 测试：新增 `local-browser-control-provider.coordinate.test.mjs`（6 用例）验证 `computeViewportPoint`；`node --test` 全绿（17/17：坐标 6 + provider 7 + headless 4）。schema/工具契约未改动。

> **P0 二阶段（元素级定位 + frame 支持）已落地**
> 改动文件：`local-browser-control-provider.mjs` + 新增 `local-browser-control-provider.element.test.mjs`
> - 新增 `parseFrameSelector(selector)`：解析 `frame:N` 前缀 → `{ framePath: number[], css }`，无前缀返回主文档。
> - 新增 `buildElementJs(selector, body)`：生成跨 iframe 定位元素的 IIFE（`doc` 沿 `framePath` 下钻 `defaultView.frames[i].document`，未命中返回 null），支持注入 `body`（`el` 命中后的动作）。selector 以 JSON 转义防注入。
> - 统一替换：click（取中心点+视口字段）、type（focus+clear）、readDom（取 innerText/outerHTML）、waitForElementStable（采样 boundingRect）四处原裸 `document.querySelector` 全部改用 `buildElementJs`，消除重复、支持跨 iframe。
> - 测试：`local-browser-control-provider.element.test.mjs` 9 用例（parseFrameSelector 4 + buildElementJs 5，含下钻/转义防注入），全绿。全量 22/22（坐标 6 + provider 7 + element 9）。
>
> **P0 三阶段（open shadowRoot + click 路径测试）已落地**
> 改动文件：`local-browser-control-provider.mjs` + `local-browser-control-provider.element.test.mjs` + `local-browser-control-provider.actions.test.mjs`
> - `buildElementJs` 注入 `DEEP_QUERY_HELPER` / `queryDeep`：先 `querySelector`，再遍历 `*` 并递归进入 **open** `node.shadowRoot`。
> - `buildRolesSnapshotJs` 同样注入 helper；角色采集显式走 `current.shadowRoot.children` 再走 `current.children`。
> - click 路径测试：selector `#go`（mouseDown/Up + viewport）、坐标点（跳过 lookup）、`frame:0 #submit`。
> - 单测：element + actions + coordinate **35/35** 全绿。**closed shadow 仍不可达**（本切片非目标）。
> - 代码 commit：`eab5f3dc`（已 push `origin/PeerAgent/sept-1-changes`）。
>
> **提交现状**
> - 坐标规范化 + auto-wait 已 commit：`46b3b05c`（已 push `origin/PeerAgent/sept-1-changes`）。
> - 元素级定位 + frame 支持（buildElementJs）已 commit：`d9ab02c6`（已 push 同分支）。
> - P1 动作面：决策见 [ADR 70](../decisions/70-l1-browser-action-surface.md)。**P1a hover+scroll 与 P1b key+drag 均已落地**（契约、capability json、工具 schema、provider、动作路径测试）。
> - L1 观察面：`browser_read_dom` 已支持 `format=roles`（role/name/selector 快照，支持 `frame:N` 与 open shadowRoot）。**不在 ADR 70 范围**。
> - P2 外部浏览器：决策见 [ADR 71](../decisions/71-l2-playwright-external-browser.md)。**L2 第一刀已落地**：temporary Peer-managed Playwright 会话、独立 `browser_external_*` / `local.web.external.*`，不接管 L1 webview，不向模型暴露 Playwright/CDP。download/dialog 本切片拒绝并给出可恢复错误。
> - 剩余：L1 closed shadow / text-role-testid locator；live Retina+缩放端到端验收；L2 持久 Peer-managed profile、Explicit attach、download/dialog capability。

**P1 —— 补齐 L1 缺失动作（对齐 Playwright 单页语义）**

> 设计见 **ADR 70**。P1a（`browser_hover` / `browser_scroll`）与 P1b（`browser_key` / `browser_drag`）均已实现。

5. 新增 `hover`、`scroll`、`key`(press/tab/enter/escape/组合键)、`drag` 动作；必须同步 `DESKTOP_ONLY_LOCAL_TOOL_CONTRACTS`、capability json、provider、reveal 白名单与 parity 测试。实现切 P1a（hover+scroll，已落地）/ P1b（key+drag，已落地）。
6. 给 `browser_read_dom` 增加 `role` / `accessibility` 观测，方便模型选元素而非猜坐标。**不在 ADR 70 范围**（观察面，不是动作面）。**已落地**：`format=roles` 产出 role/name/selector 快照，支持 `frame:N` 与 open shadowRoot。

**P2 —— 加 L2 Playwright Adapter（补多页/下载/对话框/独立登录态）**

> 设计见 **ADR 71**。L2 第一刀（temporary Peer-managed profile + 白名单动作）已实现。Playwright 不得接管 L1 内嵌页，也不得向模型暴露 Playwright/CDP。

7. 引入 `ExternalBrowserAdapter`（Playwright 优先，CDP 仅 Adapter 内受限底层），独立 Peer-managed profile / 显式 attach / 临时 context。
8. 安全模型、download/dialog 权限、artifact 敏感分级见 [ADR 71](../decisions/71-l2-playwright-external-browser.md)。实现顺序：temporary profile → 持久 Peer-managed profile → 最后评估 attach。

### 验收口径

| 验收项 | 通过标准 |
|---|---|
| 点击正确性 | 在 Retina + 网页 缩放 + 含 iframe 的页面上，按 selector 点击命中目标（而非中心点附近），连续 10 次稳定 |
| auto-wait | 懒加载/动画页面，等待目标稳定后再点，不再点空白 |
| 补充动作 | hover 能触发子菜单，scroll 能滚动到目标，key 能发送 Tab/Enter |
| L1 边界 | 模型仍只看到 `browser_*` 工具，无裸 Playwright 暴露 |
| 回归 | click selector / 坐标 / `frame:N` 路径测试存在；element+actions+coordinate 单测全绿 |

### 明确不做（Non-goals）
- **不**用 Playwright 接管 L1 内嵌页面执行面；
- **不**向模型暴露裸 Playwright API 或任意 CDP command；
- **不**在 peer_agent 代码仓库 `docs/` 下重建架构知识（已按规则落 peer-knowledge）。


