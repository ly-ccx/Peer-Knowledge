# Desktop 与 CLI/TUI 本地能力对齐

创建时间: 2026-07-23
最后更新: 2026-07-23
状态: Implemented

## 1. 决策摘要

Peer Agent 将 Desktop 与 CLI/TUI 视为同一 Agent Runtime 的两个一等宿主。凡是不依赖可视界面语义的本地能力，都必须通过同一份公开工具契约和同一条受治理执行链对模型暴露；宿主只负责授权交互、运行环境适配和结果表达。

本次对齐范围是：

1. `batch_search` / `local.search.aggregate`：批量并行内容搜索；
2. `web_fetch` / `local.web.fetch`：明确 URL 的受治理网页读取；
3. `request_explorer` / `local.goal.explore`：Goal Runner 的只读 Explorer；
4. Goal Runner Verifier：完成门禁前的独立验证子会话；
5. `shell_stop` / `local.shell.stop`：停止由同一宿主管理的后台 Shell 任务；
6. 基础文件、Shell、Goal、交互工具的公开名称、`capabilityId`、输入 Schema 和模式投影。

以下能力明确不要求 CLI 对齐：

- `browser_navigate`
- `browser_click`
- `browser_type`
- `browser_screenshot`
- `browser_read_dom`

它们操作的是用户正在观看的 Desktop Workbench `<webview>`，语义依赖可视页面、活动标签页和 Electron 主进程。CLI 没有同等宿主对象，不能用无头浏览器冒充相同能力。CLI 需要读取网页时统一使用 `web_fetch`。

本决策延续且不替代以下既有文档：

- `knowledge/decisions/35-mode-scoped-tool-projection.md`
- `knowledge/decisions/38-web-search-fetch-provider.md`
- `knowledge/decisions/40-embedded-browser-and-agent-control.md`
- `knowledge/decisions/51-unified-desktop-cli-file-tools.md`
- `design/product/batch-search-parallel-aggregation.md`
- `design/product/goal-mode-multi-agent-orchestration-plan.md`
- `design/product/goal-runner-explorer-task-list.md`

## 2. 问题与现状

### 2.1 用户可见问题

同一模型、同一工作区、同一种运行模式，在 Desktop 和 CLI/TUI 中看到的工具集合不同：

- Desktop 可一次发起多路搜索，CLI 只能重复调用单路搜索；
- Desktop 可读取 URL，CLI 没有 `web_fetch`；
- Desktop Goal Runner 可派发 Explorer 和 Verifier，TUI Runner 将两者显式设为 `null`；
- Desktop 有 Shell 任务管理器和停止能力，Node Runtime 只有前台 `local.shell.exec`；
- 相同意图在两端存在 `bash` / `local_shell_exec`、`local.file.search` / `local.search.content` 等名称漂移；
- TUI 某些结果摘要和 Goal 门禁已识别尚未真正注册的工具，形成“看起来支持、实际不可调用”的假能力。

这些差异会扩大 Prompt 分叉、增加模型重试轮次，并使权限、Evidence、测试和故障排查难以复用。

### 2.2 2026-07-23 审计基线

#### Desktop 已有

- 文件：`read_file`、`list_files`、`search_files`、`edit_file`、`write_file`；
- Shell：`bash`，底层有 `local.shell.exec`、`local.shell.stop` 与任务管理器；
- 搜索：`batch_search` / `local.search.aggregate`；
- Web：`web_fetch` / `local.web.fetch`；
- Goal：create/update/get、`request_explorer`、Explorer Runner、Verifier Runner；
- 交互：`request_user_input`；
- Skill/MCP：按注册表动态投影；
- 浏览器控制：五个 Desktop-only 工具。

#### CLI/TUI 已有

- Node Runtime Provider Bundle：file、shell、interaction；
- 文件：read/list/search/edit/write；
- Shell：`local.shell.exec`；
- Goal Bridge：create/update/get 与 intake 门禁；
- Goal Runner：主循环已复用 Desktop runner，但 `explorerRunner: null`、`verifierRunner: null`；
- Skill/MCP Bridge：动态投影与本地执行；
- TUI 已能摘要部分 Desktop 工具结果，但摘要支持不等于执行能力。

#### 基线测试

在实施前：

- `pnpm --filter @peer-agent/runtime-node test` 通过；
- `pnpm --filter @peer-agent/tui test` 通过。

代码仓在实施开始时存在与本目标无关的 UI 未提交改动。实现必须避开、不覆盖、不清理这些改动。

## 3. 目标能力矩阵

图例：

- **共享**：两端公开契约和核心语义相同；
- **适配**：能力相同，宿主实现允许不同；
- **专属**：能力只在该宿主成立；
- **内部**：不是模型工具，由编排器调用。

| 能力意图 | 模型工具名 | Canonical capabilityId | Desktop | CLI/TUI | 目标分类 |
|---|---|---|---|---|---|
| 读文件 | `read_file` | `local.file.read` | 有 | 有 | 共享 |
| 列目录 | `list_files` | `local.file.list` | 有 | 有 | 共享 |
| 搜内容 | `search_files` | `local.file.search` | 有 | 有 | 共享 |
| 增量编辑 | `edit_file` | `local.file.edit` | 有 | 有 | 共享 |
| 整文件写入 | `write_file` | `local.file.write` | 有 | 有 | 共享 |
| 执行 Shell | `bash` | `local.shell.exec` | 有 | 有但工具名漂移 | 共享 + 宿主任务适配 |
| 停止 Shell | `shell_stop` | `local.shell.stop` | 有底层能力 | 缺失 | 共享 + 宿主任务适配 |
| 批量搜索 | `batch_search` | `local.search.aggregate` | 有 | 缺失 | 共享 |
| 读取 URL | `web_fetch` | `local.web.fetch` | 有 | 缺失 | 共享 + 抓取适配 |
| 请求用户输入 | `request_user_input` | `local.interaction.request_user_input` | 有 | 有 | 共享 + UI 适配 |
| 建立 Goal 计划 | `goal_create_plan` | `local.goal.create_plan` | 有 | 有 | 共享 |
| 更新 Goal 任务 | `goal_update_task` | `local.goal.update_task` | 有 | 有 | 共享 |
| 读取 Goal 计划 | `goal_get_plan` | `local.goal.get_plan` | 有 | 有 | 共享 |
| 请求 Explorer | `request_explorer` | `local.goal.explore` | 有 | 缺失 | 共享 |
| 独立 Verifier | 无公开工具 | Runner 内部接口 | 有 | 缺失 | 内部共享编排 |
| MCP 工具 | 注册表工具名 | MCP manifest ID | 有 | 有 | 共享注册表，宿主生命周期适配 |
| Skill 工具 | Skill manifest 名 | Skill manifest ID | 有 | 有 | 共享注册表，宿主生命周期适配 |
| 可视浏览器控制 | `browser_*` | `local.web.control.*` | 有 | 不适用 | Desktop 专属 |

## 4. 架构原则

### 4.1 唯一运行链

所有新增或对齐能力都必须保持：

```text
Capability Provider
  -> Manifest
    -> Runtime Projection
      -> Tool Call
        -> PermissionGrant
          -> Evidence
```

禁止：

- 在 TUI `chat-controller` 里按工具名直接执行文件、Shell 或网络；
- 用 renderer/TUI React 状态保存权限真相；
- 用普通 assistant 文本模拟 Tool Result；
- 为 CLI 复制一套脱离 Runtime Projection 的“快捷工具”；
- 把网页正文、文件内容或工具输出提升为 system instruction。

### 4.2 共享语义内核，宿主适配执行

目标分层：

```text
packages/runtime-node
  ├─ Canonical manifests / model tool names
  ├─ host-neutral provider orchestration
  ├─ Node implementations: file, shell, static HTTP, artifacts
  └─ provider bundle / runtime projection

apps/desktop/electron/main
  ├─ Electron authorization and UI events
  ├─ BrowserWindow-enhanced web fetch adapter
  ├─ visible browser control adapter (Desktop-only)
  └─ Desktop Goal worker transport

apps/tui
  ├─ terminal authorization interaction
  ├─ TUI Goal worker transport
  └─ textual progress/result presentation
```

共享不等于强迫 Desktop 使用纯 Node 的所有实现。应共享契约与可复用语义，保留深层宿主适配：

- 批量搜索可共享 fan-out、并发、去重、聚合算法；两端复用各自受治理的单路搜索执行体；
- `web_fetch` 共享 URL 校验、HTTP fallback、正文清洗、大小限制和 artifact 结果形状；Desktop 可额外注入 BrowserWindow 渲染抓取器；
- Shell 共享任务状态和停止语义；子进程环境、进程组终止方式由宿主适配；
- Goal Runner 继续共享编排器，Explorer/Verifier 只注入“运行一次受限 Agent 会话”的端侧适配器。

### 4.3 Canonical 名称与兼容边界

公开模型工具名与 `capabilityId` 必须一一稳定映射：

```text
read_file          -> local.file.read
list_files         -> local.file.list
search_files       -> local.file.search
edit_file          -> local.file.edit
write_file         -> local.file.write
bash                -> local.shell.exec
shell_stop          -> local.shell.stop
batch_search        -> local.search.aggregate
web_fetch           -> local.web.fetch
request_user_input  -> local.interaction.request_user_input
goal_create_plan    -> local.goal.create_plan
goal_update_task    -> local.goal.update_task
goal_get_plan       -> local.goal.get_plan
request_explorer    -> local.goal.explore
```

兼容策略：

1. Runtime Projection 只向新回合暴露 canonical 工具名；
2. Tool Result 摘要、持久化回放和旧会话恢复可继续识别旧名称；
3. Provider 不通过散落的 `if (capabilityId === ...)` 维护多套长期别名；确需兼容时放在单一映射表；
4. `local.search.content` 不再作为 canonical ID，统一为现有文件 Provider 使用的 `local.file.search`；
5. 不迁移或重写历史 Tool Result，只保证读取兼容。

## 5. 能力设计

### 5.1 批量并行搜索

#### 接口

```ts
type BatchSearchInput = {
  queries: Array<{
    id?: string;
    label?: string;
    query: string;
    path?: string;
    case_sensitive?: boolean;
    max_results?: number;
  }>;
  max_concurrency?: number; // 1..8，默认 4
  dedupe?: boolean;         // 默认 true
};
```

约束：

- `queries` 数量为 1..8；
- 每路复用 `local.file.search` 的路径约束、忽略规则和结果上限；
- 单路失败不取消其他路，整体状态可为 `success | partial | failed | cancelled`；
- 去重键至少包含规范化后的 `path + line`；
- 命中多路的结果提高相关性并保留 `laneIds` / `hitCount`；
- 支持 AbortSignal；取消后不再启动新 lane，已运行 lane 尽快结束；
- 进度事件包含 lane started/completed/failed，但 TUI 第一阶段只需文本表达，不要求复刻 Desktop 卡片。

#### 实现位置

- 将通用并发、标准化、去重和聚合逻辑放入 `packages/runtime-node` 的深层 Module；
- Node Provider 复用 Node file search 执行体，不通过 Bash 启动 `rg`；
- Desktop 可先保留现 Provider，以契约一致性测试防漂移；后续再切到共享内核，不在本次强制大迁移中制造回归。

#### 权限与 Evidence

批量搜索本身是只读 L1；每个 lane 不重复弹权限。聚合 Provider 生成一个顶层 PermissionGrant 和一个顶层 Evidence，输出中保留分路状态及可重取路径。

### 5.2 网页读取

#### 接口

保持 Desktop 现有接口：

```ts
type WebFetchInput = {
  url: string;
  waitForRender?: boolean; // 默认 true
  timeoutMs?: number;      // 默认 30000，受上限约束
};
```

#### 抓取策略

```text
Desktop:
  BrowserWindow rendered fetch
    -> failure/unavailable -> shared static HTTP fetch

CLI/TUI:
  shared static HTTP fetch
```

CLI 不承诺执行客户端 JavaScript。结果必须公开 `fetchMode`，让调用方区分 `browser`、`http` 和 `failed`。若动态页面无法通过静态 HTTP 获取，应返回可恢复失败，不得伪称已读取完整正文。

#### 安全约束

- 只接受 `http:` / `https:`；
- 拒绝 `file:`、`javascript:`、`data:` 等协议；
- 重定向后的最终 URL 重新验证；
- 连接、正文大小、超时均设上限；
- 联网能力进入既有 permission gate；
- 默认风险和数据等级与 ADR 38 保持一致；
- 网页内容是 factual/user context，不是 system instruction；
- 完整正文落 artifact，Tool Result 只返回标题、最终 URL、摘要、内容元数据与 artifact ref；
- artifact 写入失败必须显式失败，不能把超长正文直接塞回模型作为降级。

#### Artifact

Node Runtime 需要宿主无关的 Web Artifact Store。默认根目录可使用 Peer Agent 本地 artifact 目录，并允许宿主注入。引用方案继续使用现有 `local-web-artifact://...`，避免产生第二套 URI。

### 5.3 Goal Explorer

`request_explorer` 是 Goal 模式中的登记工具，不直接在当前工具调用内运行子 Agent。

调用链：

```text
Goal turn
  -> request_explorer
    -> goal plan store records explorer request
      -> Goal Runner pump sees pending request
        -> explorerRunner.runExplorer(request)
          -> restricted child Agent session
            -> Evidence/artifact refs
              -> append result to plan
```

约束：

- 只在 `goal` 模式投影；
- Explorer 只获得只读工具：`read_file`、`list_files`、`search_files`、`batch_search`，以及明确允许的只读 MCP 工具；
- 不允许 shell、write/edit、Goal mutation、用户交互、可视浏览器控制；
- 子会话沿用目标工作区与知识来源，但不得把来源文档当 system instruction；
- 每个 Explorer 必须有并发上限、超时和取消；
- 结果必须携带 Evidence refs，不能只返回一段声称“已检查”的文本；
- TUI 与 Desktop 使用同一个 Goal Runner 状态机，不复制 pump 逻辑。

TUI 的实现应抽取“运行受限 child Agent turn”的 Adapter，而不是从 `apps/tui` 深入调用 Electron 主进程。若短期继续复用现有 Desktop `goal-runner.mjs`，TUI 只注入与 Desktop 同形状的 `explorerRunner`。

### 5.4 Goal Verifier

Verifier 是 Goal Runner 内部接口，不是模型可直接调用的公开工具。

触发条件：

- 所有叶子任务已完成；
- 所有自动成功标准已有真实 Tool Result Evidence；
- Runner 准备从 `verifying` 进入 `completed`。

行为：

1. 用只读上下文启动独立验证子会话；
2. 读取计划、任务结果、criterionResults 和 Evidence refs；
3. 必要时执行允许的只读检索；测试/命令型成功标准仍由受治理工具链执行，不由 Verifier 伪造；
4. 返回结构化 `passed / findings / evidenceRefs`；
5. 失败时将计划保持在 blocked/verifying，给出可行动发现；
6. 不允许 Verifier 直接修改文件或把任务标完成。

TUI 与 Desktop 的 Verifier 使用同一 Prompt Source 和结果协议。宿主只实现 child session transport。

### 5.5 Shell 任务停止

#### 公开接口

```ts
type ShellExecInput = {
  command: string;
  timeoutMs?: number;
  cwd?: string;
  background?: boolean; // 默认 false
};

type ShellStopInput = {
  taskId: string;
  reason?: string;
};
```

#### 行为

- `background: false` 保持现有等待完成行为；
- `background: true` 在进程成功启动后立即返回 `taskId`、`startedAt` 和状态；
- 所有任务由创建它们的宿主管理，`shell_stop` 只能停止同一宿主、同一工作区授权域中的任务；
- 停止时先发送温和终止信号，短暂等待后再强制终止进程组；
- 不因 TUI 组件卸载就遗失正在运行任务的权限与状态真相；
- 进程输出持续写 artifact，停止结果引用同一 artifact；
- 前台调用的 AbortSignal 与显式 `shell_stop` 汇入同一个任务管理器状态机；
- 不暴露任意 PID kill 工具；模型只能使用不可猜测的 `taskId`。

如果实现成本要求分阶段，第一阶段至少做到：Node Runtime 内部任务注册、AbortSignal 统一取消、`local.shell.stop` Provider 和测试。后台输出实时重连可以后续增强，但不能声称已支持未实现的行为。

### 5.6 工具模式投影

目标模式矩阵：

| 工具 | chat | plan | goal | explorer | compact/system |
|---|---:|---:|---:|---:|---:|
| read/list/search | ✓ | ✓ | ✓ | ✓ | 按现行规则 |
| batch_search | ✓ | ✓ | ✓ | ✓ | 否 |
| edit/write | ✓ | 否 | ✓ | 否 | 否 |
| bash/shell_stop | ✓ | 否 | ✓ | 否 | 按现行内部规则 |
| web_fetch | ✓ | ✓ | ✓ | 可配置只读 | 否 |
| request_user_input | ✓ | ✓ | ✓ | 否 | 否 |
| goal create/update/get | 按现行 intake | plan/goal | ✓ | 否 | 否 |
| request_explorer | 否 | 否 | ✓ | 否 | 否 |
| browser_* | Desktop chat/goal 按现行规则 | Desktop-only | Desktop-only | 否 | 否 |

投影必须由 Manifest `modeScopes` 或单一 Runtime Projection 规则产生。TUI Goal Bridge 的门禁名单不能成为第二份工具注册表；它只能判断已投影工具是否允许执行。

## 6. 模块与文件落点

建议实现落点如下，实际文件名允许按仓库现有命名微调：

```text
packages/runtime-node/src/
  search-aggregate-provider.ts
  search-aggregate-provider.test.ts
  web-fetch-provider.ts
  web-fetch-provider.test.ts
  web-artifact-store.ts
  shell-task-manager.ts
  shell-task-manager.test.ts
  tool-contracts.ts                 # canonical names / IDs / shared schemas
  provider-bundle.ts                # 装配，不承载深层行为

apps/tui/src/
  goal-bridge.ts                    # 加 request_explorer manifest + store execute
  goal-worker-adapter.ts            # child Agent transport
  goal-worker-adapter.test.ts
  goal-runner-adapter.ts            # 注入 explorer/verifier runner
  tui-host.ts                       # 只负责宿主装配

apps/desktop/electron/main/
  现有 Providers 保持可运行；
  添加契约一致性测试；
  在低风险时切换到共享 contract/semantic kernel。
```

不接受把以上行为继续塞入大型 `chat-controller.ts`、`tui-host.ts` 或 `main.mjs`。装配点可以变动，但深层行为必须在独立 Module 内。

## 7. 迁移阶段

### Phase 0：文档与基线

- 冻结当前能力清单、名称、ID、模式和测试基线；
- 落成本文件；
- 标记代码仓已有无关改动，后续不触碰。

退出标准：本文档 `Accepted，实施中`，能力矩阵和验收项齐全。

### Phase 1：共享只读能力

1. 在 `runtime-node` 增加 `batch_search`；
2. 在 `runtime-node` 增加静态 HTTP `web_fetch` 与 artifact；
3. 接入 Provider Bundle 和 TUI 最终工具投影；
4. 增加 Provider、Bundle、TUI 投影和摘要测试。

退出标准：CLI 模型最终能看到并调用两个工具，失败/取消/权限/Evidence 路径有测试。

### Phase 2：Goal Workers

1. TUI Goal Bridge 增加 `request_explorer`；
2. 抽出 TUI child Agent worker adapter；
3. 给共享 Goal Runner 注入 Explorer 与 Verifier；
4. 测试只读工具限制、并发/取消、Evidence 和完成门禁。

退出标准：TUI 不再传入 `explorerRunner: null` 或 `verifierRunner: null`，端到端测试证明请求会被执行并写回计划。

### Phase 3：Shell 生命周期

1. 抽取 Node Shell Task Manager；
2. `local.shell.exec` 接入统一任务状态；
3. 增加 `shell_stop`；
4. 对齐 Abort、超时、停止和 artifact；
5. 测试越权 taskId、重复停止、已完成任务和进程组终止。

退出标准：CLI 可用 taskId 停止自己启动的后台任务，Tool Result 与 Evidence 状态一致。

### Phase 4：契约收口

1. 建立 canonical 工具名/ID 映射；
2. 修正 TUI Goal 门禁中的旧 ID；
3. 加 Desktop/TUI 最终投影快照或集合对比测试；
4. 显式维护 Desktop-only allowlist；
5. 保留旧结果读取别名，停止向新回合投影旧名称。

退出标准：除 allowlist 外，两端共享工具的名称、ID、Schema 和模式一致。

### Phase 5：回写与清理

- 将本文件状态更新为 `Implemented`；
- 填写真实文件路径、测试命令与实现偏差；
- 若实现发现新架构决策，先更新本文档再扩展代码；
- 不在代码仓复制本架构文档。

## 8. 兼容、失败与回滚

### 8.1 兼容

- 历史会话中的旧工具名和能力 ID继续可摘要、可回放；
- 新会话只看到 canonical 名；
- Desktop Provider 可在共享内核迁移期间保留，不要求一次性重写；
- `web_fetch` 的 CLI `fetchMode=http` 是受支持的能力差异，不是工具契约差异。

### 8.2 失败语义

所有能力至少区分：

- `success/completed`
- `partial`（仅聚合类）
- `denied`
- `cancelled`
- `timeout`
- `failed`

失败结果必须包含稳定错误码、可恢复性和真实 Evidence；不能把异常栈作为唯一用户输出。

### 8.3 回滚

每阶段可独立回滚 Provider 注册，而不删除历史 Evidence：

- 只读 Provider 出现回归：从 Bundle 移除 Manifest/Provider，单路文件工具仍可用；
- Goal Worker 出现回归：停止新请求投影，保留既有计划数据；
- Shell stop 出现回归：禁用后台模式，保留前台 exec；
- 契约别名出现问题：恢复兼容映射，不复制 Provider。

## 9. 测试与验收

### 9.1 自动测试矩阵

#### runtime-node

- 批量搜索：输入校验、1..8 路、并发上限、去重、排序、partial、Abort；
- Web：协议校验、重定向校验、超时、正文上限、HTML 清洗、artifact、权限拒绝；
- Shell：前台回归、后台 taskId、stop、重复 stop、timeout、Abort、输出 artifact；
- Bundle：每种 mode 的最终工具名与 capabilityId。

#### TUI

- 最终工具投影包含 `batch_search`、`web_fetch`、`shell_stop`；
- Goal 模式包含 `request_explorer`；plan/explorer 不获得写入或 Shell；
- Explorer 请求经过 Runner 被执行并写回 Evidence；
- Verifier 参与完成门禁；
- 文本摘要正确展示 success/partial/cancelled/failed；
- 权限提示和终止回合控制不回归。

#### Desktop

- 现有批量搜索、Web、Goal、Shell 测试继续通过；
- 契约一致性测试验证共享工具；
- Desktop-only 浏览器控制不参与共享集合断言。

### 9.2 仓库级命令

实施完成至少运行：

```bash
pnpm --filter @peer-agent/runtime-node test
pnpm --filter @peer-agent/tui test
pnpm run typecheck
pnpm run architecture:check
```

若改动 Desktop Provider 或共享契约，还需运行对应 Desktop Node tests。

### 9.3 Definition of Done

只有同时满足以下条件才可将本文档状态改为 `Implemented`：

- [x] 本文件存在且包含“目标能力矩阵”；
- [x] CLI 最终投影具有 `batch_search` 和 `web_fetch`；
- [x] TUI Goal Runner 的 Explorer 与 Verifier 不再为空；
- [x] CLI 有 `local.shell.stop` 的真实 Provider，不只是摘要/白名单；
- [x] 共享工具的 canonical 名称、ID、Schema 与模式投影有自动测试；
- [x] Desktop-only 浏览器控制有显式 allowlist；
- [x] 权限、取消、失败和 Evidence 路径有覆盖；
- [x] runtime-node 与 TUI 聚焦测试通过；
- [x] 全仓类型检查通过；
- [x] 架构治理检查通过；
- [x] 未覆盖实施前已有的无关工作区改动；
- [x] 本文档回写真实实现路径、验证结果和任何偏差。

## 10. 非目标

本次不做：

- 给 CLI 增加可视浏览器或伪造 Workbench webview；
- 新增搜索引擎 `web_search`；
- 改变 MCP 服务器安装、认证或生命周期架构；
- 改变 Goal Plan 持久化格式，除非 Worker Evidence 无法在现有协议表达；
- 重写 Desktop 所有 Provider；
- 为统一而把 Electron 依赖引入 `runtime-node`；
- 清理与本目标无关的 UI、样式或历史代码。

## 11. 实施记录

### 11.1 实际落点

- `packages/runtime-core/src/local-tool-contracts.ts`：集中定义 Desktop 与 CLI/TUI 共享的模型工具名和 canonical `capabilityId`；`packages/runtime-core/src/projection.ts` 统一模式过滤默认值。
- `packages/runtime-node/src/`：新增批量搜索、网页读取、后台 Shell task/stop，并将文件、Shell、交互能力的 mode scope 收紧到显式边界。
- `apps/tui/src/tui-host.ts`、`provider-chat-model.ts`、`chat-controller.ts`、`tui-mode.ts`：让模型投影与实际 Tool Call 执行共用运行时 mode，`compact/system` 不再被降级为 `chat`。
- `apps/tui/src/goal-bridge.ts`、`goal-worker-adapter.ts`、`goal-runner-adapter.ts`：接通 Explorer 与 Verifier 子会话、Evidence 写回和完成门禁。
- `apps/tui/src/skill-mcp-bridge.ts`：动态 Skill/MCP 工具使用统一 `modeScopes`，只进入普通会话模式。
- `apps/desktop/electron/main/tools/` 与 `runtime-gateway/local-shell-provider.mjs`：Desktop 复用共享名称/ID，并将 `shell_stop` 经既有 Runtime Projection 路由到 `local.shell.stop`；结构化 `taskId` / `toolCallId` 不再丢失。
- Desktop 可视浏览器控制继续保持 Desktop-only，没有在 `runtime-node` 或 TUI 中伪造等价工具。

### 11.2 最终公开契约

本次新增对齐的公开契约为：

- `batch_search` → `local.search.aggregate`
- `web_fetch` → `local.web.fetch`
- `request_explorer` → `local.goal.explore`
- `shell_stop` → `local.shell.stop`

基础文件、Shell、Goal 与交互工具也统一引用 `SHARED_LOCAL_TOOL_CONTRACTS`。未声明 `modeScopes` 的普通工具默认只在 `chat`、`plan`、`goal` 中投影；`explorer`、`compact`、`system` 必须显式授权。

### 11.3 验证结果（2026-07-23）

以下命令全部退出 0：

```bash
pnpm --filter @peer-agent/runtime-node test
pnpm --filter @peer-agent/tui test
pnpm run typecheck
pnpm run architecture:check
node --test apps/desktop/electron/main/shell-system.test.mjs apps/desktop/electron/main/tool-registry.test.mjs
```

其中 Desktop 测试覆盖了模型工具注册和 `executeCapability(local.shell.stop)` 的真实 taskId 停止路径。TUI 全套测试存在既有 React `act(...)` 警告输出，但测试通过；本次未为消除该无关告警扩大 UI 改动范围。

### 11.4 与设计的偏差和后续 seam

- 没有建立第二条 Desktop Shell stop 执行路径；Desktop 仅增加模型 Definition，并继续复用已有 Shell Provider、Runtime Projection、PermissionGrant 和 Evidence 链。这比单独适配器更符合既有主链。
- `compact/system` 作为内部运行时模式加入 TUI Host 的投影边界，但没有加入用户可选择或可持久化的 `TuiMode`，避免改变会话产品语义。
- 旧 capability ID 仅保留读取/兼容 canonicalization；新投影统一发出 canonical ID。
- 本次没有清理实施前已有的无关 UI 工作区改动，也没有把架构文档复制进代码仓。
