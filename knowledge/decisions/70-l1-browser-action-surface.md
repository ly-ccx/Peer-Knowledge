# 70. L1 内嵌浏览器动作面扩展（hover / scroll / key / drag）

创建时间：2026-09-01
最后更新：2026-09-01

## 状态

Accepted。P1a（hover + scroll）与 P1b（key + drag）均已在 `peer_agent` 落地。

## 级别

A 级 —— 新增四个 `local.web.control.*` capability 与四个 `browser_*` 工具，扩张 Desktop-only 契约面、权限门、Evidence 与 CLI/Desktop parity 排除列表。

## 背景

ADR 40 落地了可见 `<webview>` 与 Agent 直控 WebContents；ADR 46 / 59 / 66 补了会话绑定、面板 reveal 与 headless 降级。P0 已修 L1 点击正确性：逻辑坐标契约、`computeViewportPoint`、`waitForElementStable`、`parseFrameSelector` / `buildElementJs` 跨 iframe 定位。

当前模型可见的 L1 动作仍只有：

| 工具 | capabilityId |
|---|---|
| `browser_open_panel` | `local.web.control.openPanel` |
| `browser_navigate` | `local.web.control.navigate` |
| `browser_click` | `local.web.control.click` |
| `browser_type` | `local.web.control.type` |
| `browser_screenshot` | `local.web.control.screenshot` |
| `browser_read_dom` | `local.web.control.readDom` |

这与能力阶梯的 `ComputerAction`（observe / navigate / click / type / **key / scroll / hover / drag / wait**）不对齐。模型要悬停子菜单、滚到视口外目标、按 Tab/Enter/Escape、拖滑块时，只能硬用 click/type 或猜坐标，这是「能力弱」的剩余主因。

Playwright 不接手 L1 执行面（见能力阶梯与缺口文档）。P1 只把 L1 单页语义补齐；多页 / download / dialog / 独立 profile 仍属 P2 `ExternalBrowserAdapter`。

## 决策

### 决策一：四个独立 capability，不合成一个 `browser_act`

新增：

| 工具 | capabilityId | 语义 |
|---|---|---|
| `browser_hover` | `local.web.control.hover` | 悬停到元素或视口点，触发 tooltip / 子菜单 |
| `browser_scroll` | `local.web.control.scroll` | 滚视口或目标滚动容器 |
| `browser_key` | `local.web.control.key` | 发送按键 / 组合键（非文本输入） |
| `browser_drag` | `local.web.control.drag` | 从源拖到目标（元素或点） |

拆开的理由：

- 权限文案、Evidence、默认行为可以按动作分级（key/drag 比 hover/scroll 更敏感）；
- 模型不必猜一个万能 `act` 的参数组合；
- 与阶梯 `ComputerAction.type` 一一对应，L2 可复用同一工具名按 environment 路由。

不做第五个 `browser_wait`：P0 的 `waitForElementStable` 已内嵌在动作前；显式 wait 留到后续，避免再扩契约。

### 决策二：必须显式登记 Desktop-only 契约

`DESKTOP_ONLY_LOCAL_TOOL_CONTRACTS` 的注释写明：parity **只能排除这份显式列表**，不能按 `browser_` 前缀通配。实现时必须同步：

1. `packages/runtime-core/src/local-tool-contracts.ts` 增加四条 `defineToolContract`；
2. `local-tool-contracts.test.ts` 的精确数组断言一并更新；
3. `BROWSER_TOOL_NAMES` / capability→tool 映射 / `BROWSER_TOOL_DEFINITIONS`；
4. `capabilities/local.web.control.{hover,scroll,key,drag}.json`；
5. provider `CONTROL_CAPABILITIES` + 分发分支 + `permissionReason`；
6. renderer `shouldRevealBrowserPanel` 白名单（当前只列 navigate/click/type/screenshot/read_dom）；
7. `desktop-cli-local-capability-parity.md` 与相关测试：四者仍是 Desktop 专属，CLI 诚实投影为「不适用」。

漏登任何一项，都会被当成未知 browser 工具，parity 失败或模型看不到工具。

### 决策三：复用 P0 定位链，不新开执行面

四个动作都走现有链：

```text
Capability Provider(local.web.control.*)
  → Manifest
    → Runtime Projection
      → Tool Call(browser_*)
        → PermissionGrant
          → Evidence
```

定位一律 `parseFrameSelector` + `buildElementJs` + `waitForElementStable`；坐标仍用观察时的**逻辑坐标**（不乘 DPR）。点坐标继续作为 selector 的兜底，与 click 一致。

执行器仍是当前 WebContents：`executeJavaScript` + `sendInputEvent`。不引入 Playwright，不向模型暴露 CDP command。

### 决策四：各动作技术选型

#### hover

- 有 selector：定位、stable、scrollIntoView，再 `sendInputEvent({ type: 'mouseMove', x, y })`。
- 仅 x/y：直接 mouseMove。
- 不合成 click。Evidence 记 `locatedBy`、逻辑点、viewport 观测字段。
- 失败：元素未找到 / 超时未稳定 → 可恢复错误（换 selector 或重新观察）。

#### scroll

优先 **元素滚动**，避免把整页滚飞：

- `selector` + `deltaX`/`deltaY`：对命中元素 `scrollBy`（优先最近可滚祖先，否则自身）。
- `selector` + `block`/`inline`（`start|center|end|nearest`）：`scrollIntoView`。
- 无 selector：对 `document.scrollingElement` / visualViewport 滚 `delta`。
- 不用系统级鼠标滚轮事件做默认路径（坐标与嵌套滚动容器不可靠）。mouseWheel 仅作明确「滚视口中心」的次选，实现阶段用测试钉死。
- Evidence 记滚动前/后 `scrollX/scrollY` 或目标元素 `scrollTop/Left`。

#### key

与 `browser_type` 分开：`type` 是文本插入；`key` 是按键语义。

- 参数：`keys: string[]`（有序），可选 `selector`（先 focus）。
- 允许白名单：`Tab` `Enter` `Escape` `Backspace` `Delete` `ArrowUp/Down/Left/Right` `Home` `End` `PageUp` `PageDown` `Space`，以及 `Meta|Control|Alt|Shift+<Key>`。
- 实现：`sendInputEvent` 的 `keyDown` / `char` / `keyUp`；组合键先按下修饰键再主键，再反向抬起。
- **禁止**：任意 Unicode 当 keyCode 绕过 type；禁止把密码/token 经 key 逐字打入（敏感文本仍走 type 的脱敏门）。
- 未在白名单的键名 → 参数错误，不执行。

#### drag

P1 只做 **鼠标按下-移动-抬起** 的通用拖拽（滑块、排序、画布平移），不做 HTML5 `DataTransfer` 文件拖入。

- 参数：`from` / `to`，各自为 selector 或 `{x,y}`。
- 路径：from 点 `mouseDown` → 若干 `mouseMove`（至少终点，建议 3～8 步避免被当成 click）→ `mouseUp`。
- 源或目标在 iframe 内：两端都经 `buildElementJs`；跨 frame 拖拽若坐标无法映射到同一 WebContents 视口，返回可恢复错误，不静默降级。
- 原生 OS 文件 DnD、浏览器下载拖出窗口：**不做**，留给 P2/L3。

### 决策五：权限与 Evidence

沿用现有 click/type 的 `projectionPolicy`：

- `cwdScope: none`
- `defaultBehavior: ask`
- `readOnlyAutoAllow: false`
- `sandboxAvailable: false`

分级建议（实现时写进 manifest，可按产品再收紧）：

| 动作 | 默认 | 说明 |
|---|---|---|
| hover / scroll | ask，可按 session+host 记忆 | 中风险，改变可见 UI 但不提交表单 |
| key | ask，不默认记忆含 Enter/组合键的授权 | Enter 可能提交表单；组合键可能触发快捷键 |
| drag | ask，不默认记忆 | 可能改顺序、改数值、触发上传区 |

Permission UI 展示 host + 动作摘要；key 的 `keys` 可展示键名，不得把伴随的私密文本写入授权卡片。Evidence：`artifact_ref`，摘要含动作、locatedBy、逻辑坐标或键名、viewport 观测；不把输入隐私写进模型可见 output。

### 决策六：实现顺序与验收切面

实现分两刀，避免一次改四轴却只测一轴：

1. **P1a**：hover + scroll（最高频、实现最直）。
2. **P1b**：key + drag（权限与事件序列更重）。

每轴至少：无前缀 selector、`frame:N` selector、纯坐标兜底、失败可恢复。hover×frame、scroll×嵌套容器、key×修饰键、drag×from/to 四点组合都要有测试或明确 skip 理由。

## 后果

- 模型在 L1 获得与 Playwright 单页相近的动作词汇，仍看不到 Playwright/CDP。
- Desktop-only 列表从 6 条扩到 10 条；CLI 继续不投影这些工具。
- provider 与 tool-definitions 会变长，但继续按 capabilityId 分发，不在中心 host 加 `browser_*` 分支。
- `browser_read_dom` 的 role/AX 观测（缺口文档第 6 项）**不在本 ADR**；那是观察面，不是动作面。

## 明确不做

- 不用 Playwright 接管 L1 `<webview>`。
- 不向模型暴露裸 Playwright API 或任意 CDP command。
- 不把四个动作合成 `browser_act`。
- 不做 `browser_wait`、download、dialog、多 page/context。
- 不做 HTML5 文件拖入 / OS 级 DnD。
- 本轮不改 `peer_agent` 产品代码。

## 实现时必改文件（评审通过后）

- `packages/runtime-core/src/local-tool-contracts.ts` + `.test.ts`
- `apps/desktop/electron/main/tools/browser-tool-definitions.mjs` + `.test.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-browser-control-provider.mjs` + 坐标/元素测试
- `capabilities/local.web.control.{hover,scroll,key,drag}.json`
- `apps/desktop/renderer/src/chat/state/browserToolReveal.ts` + 测试
- `knowledge/architecture/desktop-cli-local-capability-parity.md`（知识库，实现同期回写）

## 参考

- ADR 40 内嵌浏览器与 Agent 直控
- ADR 46 会话绑定标签
- ADR 59 面板 reveal
- ADR 66 headless 降级
- `knowledge/architecture/computer-use-capability-ladder.md` §6 ComputerAction
- `knowledge/architecture/browser-capability-gap.md` P1
- `packages/runtime-core/src/local-tool-contracts.ts` `DESKTOP_ONLY_LOCAL_TOOL_CONTRACTS`
