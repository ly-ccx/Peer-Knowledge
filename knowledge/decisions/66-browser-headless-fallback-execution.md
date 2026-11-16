# 66. 浏览器工具的后台降级执行（Headless Fallback）

创建时间：2026-08-21
最后更新：2026-11-15（明确 L1 headless 降级适用于经典对话内嵌 `<webview>`；0.1.0 Project Bot 后台任务走 ADR 71 L2 + ADR 38 `web_fetch`；2026-11-14 曾修正架构文档引用）

## 状态

Accepted，已实现（代码在 peer_agent 仓库，含测试）。

## 级别

A 级 —— 变更了能力执行的边界条件（可见面板从「执行前提」降为「尽力而为的展示请求」），
并扩展了 PermissionGrant/Evidence 的语义标注。本文记录该决策。

## 背景

ADR 46 定义了会话绑定的浏览器标签：Agent 浏览器工具（`local.web.control.*`）通过
reveal 协调器请求 renderer 打开 Workbench Browser 面板，等 renderer ack 后解析该会话的
活跃 WebContents 并执行。这条链隐含一个前提：**面板必须在场，工具才能执行**。

实际运行中该前提频繁不成立，产生三类失败：

1. `browser_open_panel` 返回 failed 且无 reason 透出（reveal 超时 / renderer 未挂载 /
   registry 无活跃条目），且主进程日志无痕迹，事后无法归因；
2. 面板未打开时，后续 navigate/click/type/screenshot/readDom 全部以
   `no_active_browser` 失败——**展示层的缺席否决了能力层的执行**；
3. 云端模型流断连时，正在执行的浏览器工具调用被标记为「工具调用已中断（连接错误）」，
   文案与真实故障层（模型通道）不符，误导排查方向。

根因是执行与展示的依赖方向反了。[架构治理基线](../architecture/20-architecture-governance.md)说
「界面负责表达」，表达层的缺席不应阻断能力执行。

> **适用边界（2026-11-15 对齐）**：本 ADR 规定的是**经典前台会话 L1 内嵌 `<webview>`（`browser_*`）**在面板未挂载时的后台降级（取代 [ADR 59](59-browser-panel-reveal-capability.md) 无面板即失败）；在 0.1.0 **Project Bot 模式**（[ADR 85](85-project-agent-hosts-inputs-and-surfaces.md) 决策 5）下，`work_session` 不投影 L1 `browser_*`（改用 L2 Playwright [ADR 71](71-l2-playwright-external-browser.md) 与 [ADR 38](38-web-search-fetch-provider.md) `web_fetch`），L1 `BrowserSession` 仅服务于用户打开的右侧资源窗口标签、独立浏览器窗口及经典前台对话。

## 决策

### 决策一：执行不依赖展示（核心原则）

浏览器工具的目标解析顺序：

```text
1. registry 中该会话的可见活跃 entry   → 在可见 webview 上执行
2. 等待 registry 出现 entry（原超时语义保留）
3. 都没有 → 惰性创建 headless WebContents，注册为 hidden entry → 在后台执行
4. headless 不可用（如测试环境无真实 electron）→ 才返回 no_active_browser 失败
```

reveal 请求从「必须成功的调用」降级为「尽力而为的副作用」：失败不再短路工具执行，
只影响「结果是否同时可见」。

### 决策二：headless entry 复用既有执行链，不开旁路

headless 会话不是第二套浏览器，而是 registry 的一个普通 entry：

- `browserTabId` 固定为 `__headless__`，注册时带 `hidden: true`；
- 走同一条 `Capability Provider → Manifest → Runtime Projection → Tool Call →
  PermissionGrant → Evidence` 链路；
- 与可见面板共享 `persist:peer-browser` 分区（登录态一致，与 ADR 46 决策三对齐）；
- 不参与前台焦点竞争（`claimForeground: false`）。

**共存规则**：可见 entry 注册时接管该会话的 active 槽位，headless entry 同步让位；
headless entry 存在期间，后续工具调用幂等复用（同一隐藏窗口，不重复创建）。
可见面板在场时绝不创建 headless 会话——它只是「面板缺席」的兜底，不是并行浏览器。

### 决策三：降级语义必须可审计

后台执行不是「默默执行」，治理链上显式可见：

- PermissionGrant 的 `scope` 增加 `headless: true` 标注（hidden entry 为目标时）；
- 工具输出（outputPreview/output）带 `headless: true`；
- `browser_open_panel` 在 reveal 失败时返回 `status: 'background'` 的成功结果
  （`visible: false, headless: true`），Evidence summary 记录降级事实
  （`degraded to headless`），不再是硬失败；
- 首次 headless 执行的输出标注 `reused: false`（隐含于幂等语义），同一会话后续调用
  复用同一 entry。

### 决策四：失败文案与真实层对齐

`no_active_browser` 的用户可见文案改为区分两种情况：面板未打开且 headless 不可用
（建议重试或打开面板）；WebContents 已销毁（建议重试）。文案不再暗示「必须先打开面板」
是唯一出路。

## 实现落点（peer_agent 仓库）

| 文件 | 变更 |
|---|---|
| `electron/main/runtime-gateway/browser-control-headless.mjs` | 新增：headless 会话管理器（隐藏 BrowserWindow + WebContentsView，幂等 ensure，dispose 清理） |
| `electron/main/runtime-gateway/local-browser-control-provider.mjs` | resolveTarget 降级链；openPanel 后台模式；scope/output 的 headless 标注；文案更新 |
| `electron/main/runtime-gateway/browser-control-registry.mjs` | entry 白名单增加 `hidden` 字段 |
| `electron/main/runtime-gateway/browser-control-headless.test.mjs` | 新增 7 测试：创建/幂等/重建/可见接管/清理/识别/优雅失败 |
| `electron/main/runtime-gateway/local-browser-control-provider-headless.test.mjs` | 新增 4 测试：降级执行/grant 语义/openPanel 后台模式/可见优先 |

测试基线：browser 相关 39/39 通过（新增 11 + 既有 28）。

## 迁移与兼容

- 既有引用方（`local-tool-host.mjs`、`browser-tool-definitions.mjs`）无需改动接线：
  provider 工厂默认惰性创建 headless 管理器；传 `headlessManager: false` 显式禁用
  （保持旧行为，用于隔离测试或极端环境）。
- 测试环境（node --test，无真实 electron BrowserWindow）自动降级为旧行为
  （headless = null → no_active_browser），既有测试零改动通过。
- registry 的 `hidden` 字段对旧读取方是加法兼容（未识别字段被忽略）。

## 验证要求

1. 面板关闭时，navigate/click/type/screenshot/readDom 仍成功执行，输出带 headless 标注。
2. 打开面板后，同一会话的后续工具调用自动切到可见 entry（headless 让位）。
3. openPanel 在面板无法展示时返回 background 成功语义而非失败。
4. headless 执行的 PermissionGrant scope 与工具输出均携带 `headless: true`。
5. 同一会话多次降级执行复用同一隐藏窗口（不泄漏窗口）。
6. headless 不可用的环境（纯 node 测试）回退旧行为，既有断言不破坏。

## 暂不处理

- headless 会话的空闲回收（当前生命周期 = 会话生命周期；长期后台会话的窗口泄漏治理
  留待后续观察）；
- headless → 可见面板的会话接管后的页面状态迁移（两边共享 partition，URL 各自独立，
  不做 DOM/滚动位置迁移）;
- CLI/TUI 宿主的 headless 浏览器（双宿主共享内核的浏览器能力对齐是另一个议题）；
- 云端模型流断连导致工具调用被标记「连接错误」的文案修正（属 chat runtime 文案层，
  与本决策正交，单独立项）。
