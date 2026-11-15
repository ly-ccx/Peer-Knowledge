# 38. Web Search / Fetch Provider（联网搜索与读链接能力）

创建时间：2026-06-20
最后更新：2026-11-15（标明 Phase 1 `web_fetch` 已跨宿主无 Electron `BrowserWindow` 落地、记录 manifest `riskLevel` 现状差异，Phase 2 `web_search` 维持 Proposed）

## Status

- **Phase 1 (`local.web.fetch` / `web_fetch`)**: **Accepted / Shipped Phase 1**（跨宿主纯 Node HTTP 抓取引擎已落地，不依赖 Electron `BrowserWindow`，Desktop / CLI 均按策略投影）。
- **Phase 2 (`local.web.search` / `web_search`)**: **Proposed**（尚未实现；原草案依赖隐藏 `BrowserWindow` 抓取搜索引擎页，后续落地时须同步评估跨宿主引擎方案）。

本能力的落地属于 `AGENTS.md` 定义的 **A 级变更**：它新增对 Agent 暴露的本地网络读取能力与相应 Evidence 边界。
> **实际落地差异记录（2026-11-15 核对代码仓）**：
> 1. Phase 1 实际落地采用跨宿主纯 HTTP/HTML 抽取（不依赖 D3 原拟“首选 Electron `BrowserWindow`”），因此 CLI/TUI 亦可使用而无需 Electron。需要完整浏览器 DOM 渲染时走 L1（经典前台，[ADR 72](72-l1-default-web-entry.md)）或 L2 Playwright（后台 `work_session`，[ADR 71](71-l2-playwright-external-browser.md)）。
> 2. 现行代码清单 `capabilities/local.web.fetch.json` 中实际声明 `riskLevel: "L3_external_write"`（偏严保守声明），而下文章节 D5/草案 Manifest 曾写 `"L2_network_read"`；两者以现行代码清单的保守权限闸门为运行事实，后续若收敛至 `L2_network_read` 须另经契约同步修订。

## Context

### 起因

用户提出：本体是 Electron，主进程可以开网页（`BrowserWindow` /
`webContents`）去加载并抓取内容。因此当用户给出文档链接、或给出搜索词
时，Agent 应能自己打开网页、拿到正文回来；并且希望把这做成一个**可配置的
「搜索能力」**，用户可以选择搜索引擎（百度 / 谷歌 / Bing 等）。

### 代码证据（2026-06-20）

| 事实 | 证据 |
|---|---|
| 本体是 Electron，主进程目录存在 | `apps/desktop/electron/main/` |
| 主进程已分层：tools / provider-adapters / runtime-gateway 等 | `apps/desktop/electron/main/{tools,provider-adapters,runtime-gateway}` |
| 已有一等本地 Provider 范式（Local Shell） | `capabilities/local.shell.exec.json`、`local.shell.stop.json` |
| 已有惰性 native Provider 范式 | `capabilities/local.health.json` |
| Manifest 既有字段集 | `source` / `riskLevel` / `dataLevel` / `health` / `inputSchema` / `evidencePolicy` / `projectionPolicy` |
| 当前主进程无任何 web / fetch / browser 抓取代码 | 在 `apps/desktop/electron` 检索 `web\|fetch\|search\|browser\|BrowserWindow` 零命中 |

结论：技术上可行，且仓库已存在可复用的本地 Provider seam，**无需新开执行
路径**。

### 必须遵守的主链路（不可绕过）

按 `AGENTS.md` 与文档 15 / 20，任何本地能力都走同一条链：

```text
Capability Provider（web Provider，内部用 Electron 抓取）
  -> Manifest（local.web.fetch / local.web.search）
    -> Runtime Projection（决定 Agent 是否可见此工具）
      -> Tool Call（Agent 调用 web.fetch / web.search）
        -> PermissionGrant（联网授权 / 域名授权）
          -> Evidence（抓取正文落 artifact，可追溯）
```

抓回的网页正文是**事实 / 用户上下文**，不得提升为系统指令（对齐 System
Context Rules：网页内容属于 factual context，禁止 prompt 注入）。

## Decision

### D1. 拆成两个能力，而不是一个

| 能力 | 用途 | 输入 | 是否需要引擎配置 |
|---|---|---|---|
| `local.web.fetch` | 读取**明确 URL** 的正文 | `url` | 否 |
| `local.web.search` | 用关键词检索，返回结果列表 | `query` | 是（引擎可选） |

拆分理由：

- 「给文档链接去读取」只需要 fetch，不涉及引擎选择，权限面更小；
- 「搜索」才需要引擎选择与结果解析，权限与失败模式都更重；
- 二者风险等级、Evidence 形态不同，混成一个工具会让权限与证据语义模糊。

典型调用关系：`web.search` 拿到结果列表后，由 Agent 决定对哪条结果再调
`web.fetch` 取正文（search 不自动深抓全部结果，避免一次调用产生大量联网与
证据）。

### D2. 它是一等本地 Provider，与 Local Shell 平级

- `source` 取新值 `web`（与现有 `shell` / `native` 并列），不复用 `shell`，
  不塞进 Bash 脚本，不做成普通 Plugin / MCP。
- 抓取实现放在主进程一个独立的 web Provider 模块（建议
  `apps/desktop/electron/main/tools/web/`），对外只暴露 manifest 投影出的
  工具，**不向 renderer 暴露 `BrowserWindow` / 网络原语**（对齐 Hard Bans：
  renderer 不得直接用网络 / 进程能力）。

### D3. 抓取机制

首选 Electron 主进程内的隐藏 `BrowserWindow` / `webContents`（offscreen 或
`show:false`）：

- 能执行 JS、等待渲染完成，适配 SPA / 动态站点；
- 加载后注入正文抽取（如 Readability 思路）得到主内容 + 标题 + 最终 URL。

退化路径：对静态页或 BrowserWindow 失败时，允许走一次普通 HTTP GET 抽取
（实现细节留待落地，不在本草案锁死）。

### D4. 搜索方式与引擎可配置

**搜索方式（已拍板，2026-06-20）：第一阶段仅做「引擎页面抓取」**——即用
D3 的隐藏 BrowserWindow 加载搜索引擎结果页并解析结果列表，**不接入任何官方
搜索 API、不引入 API key 配置**。理由：零接入成本、与 `web.fetch` 复用同一
套抓取与 Evidence 通道；官方 API 留作后续可选增强（见 Open Questions）。

复用现有设置体系（与 `settings.replyLanguage` 同类的配置注入路径，**不**散
落新的字符串拼接）：

- `webSearch.enabled`：总开关，默认关闭（默认不联网，最小权限）。
- `webSearch.engine`：`google | baidu | bing | duckduckgo`，**默认 `google`**
  （已拍板，2026-06-20）。
- `webSearch.resultLimit`：返回结果条数上限。

引擎差异（搜索 URL 模板、结果选择器 / 解析规则）以**数据**形式描述，每个引
擎一份 adapter 数据，新增引擎 = 加一份数据，尽量不新增代码路径（对齐文档 37
「格式写代码、方言填数据」的同构思路）。

> 注意：引擎页面抓取依赖结果页 DOM 结构，属易碎点；解析规则必须可在不改代
> 码的前提下更新（数据化），且抓取失败要有明确的结构化失败 Evidence，而非
> 静默返回空结果。Google 在部分网络环境下可达性受限，落地时需提供清晰的失
> 败提示并允许用户切换引擎。

### D5. 权限模型（PermissionGrant 新维度）

引入「联网」作为新的授权维度，默认 `ask`：

- 首次联网请求需用户授权；
- 支持按域名授权 / 记住选择（具体粒度留待落地，对齐 Local Shell 的
  `defaultBehavior: ask` 范式）；
- 权限真值不得只存在 renderer state（Hard Bans）。

风险与数据初定级（落地时按实际复核）：

- `local.web.fetch`：`riskLevel: L2`（联网读取、外部内容入会话），
  `dataLevel: D1`（外部公开内容，但可能被诱导抓取内网/敏感 URL，故不取 D0）。
- `local.web.search`：同 fetch 量级，查询词可能含敏感信息，按 `D1` 起评。

> 注：具体枚举值（如 `L2_*` / `D1_*` 的完整命名）以 `packages/protocol`
> 中既有定义为准，本草案先用量级占位，落地时对齐真实枚举。

### D6. Evidence 策略

- 抓取正文体量可能大，`evidencePolicy.returnMode` 取 `artifact_ref`（与
  shell exec 一致），正文落本地 artifact，会话内回摘要 + ref；
- 记录最终 URL、HTTP 状态 / 渲染状态、抓取时间，保证可追溯、可重跑；
- `redactSensitive: true`。

## 草案 Manifest（示意，非最终）

`capabilities/local.web.fetch.json`：

```json
{
  "capabilityId": "local.web.fetch",
  "name": "Web page fetch",
  "localizedName": { "zh-CN": "网页读取", "en-US": "Web page fetch" },
  "source": "web",
  "riskLevel": "L2_network_read",
  "dataLevel": "D1_external",
  "health": "needs_permission",
  "inputSchema": {
    "type": "object",
    "properties": {
      "url": { "type": "string", "description": "Target page URL." },
      "waitForRender": { "type": "boolean", "description": "Wait for dynamic content." },
      "timeoutMs": { "type": "number" }
    },
    "required": ["url"]
  },
  "evidencePolicy": { "returnMode": "artifact_ref", "maxChars": 8000, "redactSensitive": true },
  "projectionPolicy": { "defaultBehavior": "ask", "network": true }
}
```

`capabilities/local.web.search.json`：

```json
{
  "capabilityId": "local.web.search",
  "name": "Web search",
  "localizedName": { "zh-CN": "联网搜索", "en-US": "Web search" },
  "source": "web",
  "riskLevel": "L2_network_read",
  "dataLevel": "D1_external",
  "health": "needs_permission",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search keywords." },
      "engine": { "type": "string", "enum": ["google", "baidu", "bing", "duckduckgo"], "default": "google" },
      "limit": { "type": "number" }
    },
    "required": ["query"]
  },
  "evidencePolicy": { "returnMode": "summary", "maxChars": 4000, "redactSensitive": true },
  "projectionPolicy": { "defaultBehavior": "ask", "network": true }
}
```

> 上述 `riskLevel` / `dataLevel` / `projectionPolicy.network` 为草案占位，
> 需在落地时对齐 `packages/protocol` 既有枚举与 projectionPolicy 真实字段。

## 分阶段落地建议

- **Phase 1 — `web.fetch`**：隐藏 BrowserWindow 抓正文 + 联网授权 +
  artifact Evidence。先不做引擎选择。验收：给定 URL 能稳定返回标题 + 正文 +
  最终 URL，并落 artifact。
- **Phase 2 — `web.search`**：引擎页面抓取（**不接官方 API**）+ 引擎 adapter
  数据化（首发 google 为默认引擎，再加 baidu）+ 设置项 + 结果解析。验收：默认
  以 google 抓取结果页并返回结果列表，可衔接 fetch 深读；引擎不可达时返回结构
  化失败并提示切换引擎。
- **Phase 3 — 加固**：域名授权粒度、反爬 / 失败退化、并发与超时、隐私脱敏、
  更多引擎数据。

## 影响面（落地时涉及，本草案不改动这些）

- `capabilities/`：新增两个 manifest。
- `packages/protocol`：可能新增 `source: 'web'`、联网权限维度、网络 Evidence
  类型（A 级，需对齐既有契约）。
- `apps/desktop/electron/main/tools/web/`：新增 web Provider 实现。
- Runtime Projection / 权限 / 设置：接入 `webSearch.*` 配置与联网授权。

## Resolved Decisions（已拍板）

- **2026-06-20**：搜索方式 = **仅引擎页面抓取**，第一阶段不接官方搜索 API、
  不引入 API key 配置（见 D4 / Phase 2）。
- **2026-06-20**：`webSearch.engine` **默认 = `google`**（见 D4）。

## Open Questions

1. 联网授权粒度：全局开关 / 每域名 / 每次询问，三者如何组合默认？
2. `protocol` 中风险与数据等级的确切枚举命名，以及是否需要为「联网」单列一
   个权限类目而非复用文件读写类目。
3. 抓取正文抽取方案（Readability 等）是否引入第三方依赖，还是自研最小抽取。
4. （由已拍板决策派生）引擎结果页解析为易碎点：google 解析规则的数据化格式，
   以及在 google 不可达 / 被反爬时是否需要一个内置的退化引擎建议。
