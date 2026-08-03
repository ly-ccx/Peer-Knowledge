# 内嵌浏览器打开失败：`Browser 工作现场启动服务尚未就绪`

> 代码仓库：`peer_agent`（桌面端 `apps/desktop`）  
> 知识仓库：`peer-knowledge`  
> 创建时间：2026-08-03  
> 最后更新：2026-08-03  
> 相关实现：`browser_open_panel` / `browser_navigate` / `ensureBrowserReady` / `createLocalToolHost`

## 1. 用户可感知现象

在对话中让 Agent「打开内嵌浏览器看一下」时：

1. `browser_navigate` 失败：`ERR_CONNECTION_REFUSED`（若先起了临时本地 HTTP，进程又被 shell 任务回收）
2. `browser_open_panel` 连续失败，错误文案固定为：
   - 中文：`Browser 工作现场启动服务尚未就绪。`
   - 英文：`The Browser workspace reveal service is unavailable.`
3. 回退用系统 `open` 打开本地 SVG 成功（说明问题在内嵌 Browser 控制链路，不是文件本身）

## 2. 正常设计链路（source of truth）

```text
模型工具调用
  browser_open_panel / browser_navigate / ...
    → tool-orchestrator.executeProjectedModelTool
      → projected-tool-executor.createLocalToolHost(...)
        → local-browser-control-provider
          → ensureBrowserReady(conversationId)
            → browser-panel-reveal-coordinator
              broadcast: browser:panel-reveal-request
                → renderer WorkbenchContext
                  展开 workbench + 切到 browser tab
                  创建/复用 BrowserSession
                  acknowledgeBrowserPanelReveal
                ← reveal ack
              → 注册表中出现 conversation 的 active WebContents
          → loadURL / click / type / screenshot
```

设计意图：

- **Renderer 拥有**可见 Workbench / BrowserSession 状态
- **Main 拥有** request/ack 桥（`browser-panel-reveal-coordinator`）
- Agent 操控前必须先 reveal 面板，再解析 `webContentsId`

`main.mjs` 里全局 `localToolHost` 已正确注入：

```js
// main.mjs ~3052
ensureBrowserReady: browserPanelRevealCoordinator.ensureBrowserReady,
```

## 3. 根因（按因果链）

### 3.1 主因：Agent 工具执行路径没有注入 `ensureBrowserReady`

聊天/Goal 的模型工具**并不**走 main 里那个长期存活的 `localToolHost`，而是走：

`tool-orchestrator` → `executeProjectedModelTool` → **每次新建** `createLocalToolHost(...)`

`projected-tool-executor.mjs` 创建 host 时注入了：

- `workspaceRoot` / `userDataPath`
- `sessionStore`
- `mcpRegistry`
- `hookRunner`
- `goalProvider`（有条件）
- `shellProvider`

但**没有**注入：

```js
ensureBrowserReady: ...
```

而 `local-tool-host.mjs` 默认值是：

```js
ensureBrowserReady = null,
browserControlProvider = createLocalBrowserControlProvider({ userDataPath, ensureBrowserReady }),
```

于是 `openPanel` 命中硬失败分支：

```js
// local-browser-control-provider.mjs ~198
if (typeof ensureBrowserReady !== 'function') {
  return failed({
    reason: zh
      ? 'Browser 工作现场启动服务尚未就绪。'
      : 'The Browser workspace reveal service is unavailable.',
  });
}
```

这与现象中的中文错误文案**逐字一致**，可判定为确定性根因，而不是超时、网络或 UI 未挂载的偶发问题。

### 3.2 次因：临时 HTTP 服务生命周期与 shell 任务绑定

为预览本地 SVG，曾：

1. 在 workspace 起 `python3 -m http.server 8766`
2. `curl` 当时拿到 `200 6882`
3. shell 任务结束后监听进程消失（`lsof :8766` 为空）
4. 随后 `browser_navigate` 到 `http://127.0.0.1:8766/...` 得到 `ERR_CONNECTION_REFUSED`

这是**独立的进程生命周期问题**：后台服务若绑定在会被回收的 shell 任务上，工具返回后服务已死。即便 `openPanel` 修好，也需要：

- 用更稳的长期服务，或
- 用 `file://`（当前 `browser_navigate` **只允许 http(s)**），或
- 在同一生命周期内先 openPanel 再 navigate

### 3.3 非根因（排查时易误判）

| 假设 | 为何不是主因 |
| --- | --- |
| Renderer 没监听 `browser:panel-reveal-request` | `WorkbenchContext` 已监听并会 `acknowledgeBrowserPanelReveal`；本次失败在更早的「服务未注入」 |
| reveal 超时（8s / 2.5s） | 失败文案不是超时包装句 `无法打开 Browser 工作现场：...`，而是「启动服务尚未就绪」 |
| 缺 conversationId | 文案会是「缺少当前会话…」，与本次不符 |
| SVG 文件损坏 | 系统 `open` 可正常打开 |
| 端口 8765 被占用 | 只影响错误目录上的旧服务；8766 当时可 200 |

## 4. 失败对照表

| 步骤 | 期望 | 实际 |
| --- | --- | --- |
| Agent 调 `browser_open_panel` | 注入 `ensureBrowserReady` → broadcast reveal → ack | `ensureBrowserReady === null` → 立即 failed |
| Agent 调 `browser_navigate` | 先 reveal，再 `wc.loadURL(http...)` | 同上，reveal no-op；若 URL 对应服务已死则 connection refused |
| 系统 `open file.svg` | 系统默认应用预览 | 成功（旁路） |

## 5. 修复方向（代码仓落地，本知识库不改代码）

### 5.1 必做：统一注入 reveal 依赖

在 `projected-tool-executor.mjs` 创建 `createLocalToolHost` 时注入与 `main.mjs` 相同的 reveal 能力，例如：

1. 给 `executeProjectedModelTool` 增加可选参数 `ensureBrowserReady`
2. `tool-orchestrator` / chat runtime 从 main 传入 `browserPanelRevealCoordinator.ensureBrowserReady`
3. `createLocalToolHost({ ..., ensureBrowserReady })`

原则：**凡能执行 `local.web.control.*` 的 host，必须持有同一套 reveal 桥**；不要再默认 `null`。

### 5.2 建议：避免每工具调用 new 一个「半残 host」

当前每次工具调用都 `createLocalToolHost`，且依赖列表已出现「goalPlanStore 必须共享」的注释先例。Browser reveal 是同类依赖。长期更稳的是：

- 复用 main 的 `localToolHost`，或
- 抽出 `createAgentToolHostDeps()`，强制 main 与 projected executor 共享关键依赖集合（goal / browser reveal / shell 策略等）

### 5.3 产品侧：本地文件预览路径

若常见需求是预览 workspace 内静态文件：

- 允许受控 `file://`（需安全评审），或
- 提供 main 持有的短生命周期静态服务，不依赖可被回收的 agent shell 任务

## 6. 验证清单

- [ ] 对话中直接 `browser_open_panel`：Workbench 展开并切到 Browser，工具返回 `status: opened|activated|already_active`
- [ ] 随后 `browser_navigate` 到公网 `https://example.com` 成功
- [ ] 本地 `http://127.0.0.1:<port>/...`：服务仍存活时可加载；服务已死时错误应是连接失败，而不是「启动服务尚未就绪」
- [ ] 单元测试：`executeProjectedModelTool` 路径下 `ensureBrowserReady` 被调用（mock coordinator）
- [ ] 回归：goal 工具仍写入共享 `goalPlanStore`（不要修 browser 时拆掉 goal 注入）

## 7. 一句话结论

**Agent 工具执行路径每次新建 `LocalToolHost` 时漏注 `ensureBrowserReady`，导致 `browser_open_panel` 在 reveal 桥入口被硬拒绝；临时 HTTP 被 shell 回收只是次要干扰项。**
