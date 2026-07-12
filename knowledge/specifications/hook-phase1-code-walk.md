# 阶段一 Hook 植入 —— 代码走查结论

> 创建时间：2026-07-09
> 最后更新：2026-07-09
> 状态：只读代码走查（未改代码）
> 目标代码仓：`/Users/liangyin/Documents/DEV/github/peer_agent`
> 对照设计：`knowledge/specifications/hook-phase1-implementation-design.md`
> 结论一句话：阶段一 Hook 可以落地，但实现 seam 应优先选 **Local Tool Host 的统一执行层**，而不是直接塞进 Shell-only 的 `PermissionReview`；`PermissionReview` 仍作为 Shell 权限合流的一部分接入。

---

## 一、已确认的真实主链路代码

### 1. Local Tool Host 是统一执行入口

文件：`apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs`

走查结论：
- `createLocalToolHost()` 创建所有本地 Provider，并注册到 `CapabilityProviderRegistry`。
- `execute(request, context)` 读取 `request.call`，通过 `providerRegistry.execute(request, context)` 路由能力。
- 未找到 Provider 时，Host 层已经统一构造 denied grant + failed result。
- 返回结构是 Provider 的 `{ call, grant, result }`。

这说明：**PreToolUse/PostToolUse 的通用植入点应在 `local-tool-host.mjs` 的 `execute()` 外层**，这样能覆盖 shell/file/web/mcp/skill/goal/health 等所有能力。

### 2. Provider Registry 已经是 capabilityId 路由层

文件：`apps/desktop/electron/main/runtime-gateway/capability-provider-registry.mjs`

走查结论：
- Registry 通过 `capabilityId` 或 `capabilityPrefix` 找 Provider。
- `execute(request, context)` 调用具体 Provider 的 `executeCapability()`。
- 这正好支持设计中的"不要堆 `capabilityId === ...` 分支"。

Hook 不应改 Registry 路由规则，只应在 Host 层围绕 Registry 的 execute 做前/后置切面。

### 3. Shell 权限与风险分级已成体系

文件：
- `apps/desktop/electron/main/runtime-gateway/local-shell-provider.mjs`
- `apps/desktop/electron/main/runtime-gateway/permission-review.mjs`
- `apps/desktop/electron/main/runtime-gateway/shell-classifier.mjs`
- `apps/desktop/electron/main/runtime-gateway/shell-permission-rules.mjs`

走查结论：
- Shell Provider 内部执行 `classifyShellCommand({ command, cwd, workspaceRoot })`。
- 之后调用 `permissionReview.decideShellExecution({ call, classification, localApproval })`。
- `PermissionReview` 的 `resolveShellDecision()` 先看 ruleStore；`allow/deny` 直接返回，`ask` 会走 `localApproval` 或 `approvalDecider`。
- `permission-review.mjs` 明确限制 allow rule：不能 wildcard、prefix 不能太短、allow 必须绑定 cwd 和 maxRiskLevel、maxRiskLevel 不能覆盖 `L5_destructive`。
- `shell-permission-rules.mjs` 里 destructive / unknown / privileged 当前走 ask，由上层 approvalDecider 决定；这与 `09` 高风险写红线之间需要 Hook 层或后续策略层再兜住 hard deny。

这说明：Shell 的 PreToolUse 可以拿到 classification，但**如果 Hook 写在 Host 层，classification 默认还没计算**。因此有两个实现选择：

1. Host 层做通用 PreToolUse（覆盖所有能力），payload 只含 `call`/`context`，Shell classification 为空。
2. Shell Provider 在 classification 后调用同一个 HookRunner 的 `runPreToolUse()`，用于 Shell 精细风险合流。

建议一期采用**两段式**：Host 层先做通用能力阻断；Shell Provider classification 后再做 Shell 精细 PreToolUse 合流。

### 4. Evidence/Grant 由各 Provider 构造，缺少统一 hook 附加位

文件：
- `apps/desktop/electron/main/runtime-gateway/tool-result-factory.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-shell-provider.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-file-provider.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-web-provider.mjs`
- `apps/desktop/electron/main/runtime-gateway/local-mcp-provider.mjs`

走查结论：
- `createPermissionGrant()` 统一创建 grant 结构。
- `createFailedClientToolResult()` 可用于 Host 层生成 denied/failed result。
- 但成功 result 的 `evidence` 是各 Provider 自己构造的，格式上都有 `evidenceId/toolCallId/summary/locale/returnedToCloud/dataLevel/redactions/artifactRefs` 等字段。
- 当前没有统一的 `evidence.hooks` 或 `metadata.hooks` 附加位。

这说明：PostToolUse 结果可在 Host 层统一执行，但**hook 决策落账需要新增一个统一的附加策略**：
- 最小方案：Host 层在返回前把 `execution.result.evidence.hooks = [...]` 挂进去（若无 evidence 则创建最小 evidence）。
- 更稳方案：新增 `appendHookEvidence(result, hookRecords)` helper，避免各 Provider 重复改。

---

## 二、实际调用面

### 1. Electron IPC 路径

文件：`apps/desktop/electron/main/main.mjs`

走查结论：
- `localToolHost = createLocalToolHost(...)` 在 app ready 时初始化。
- IPC `client-tool:execute` 最终 `return localToolHost.execute(...)`。
- preload 暴露 `executeClientToolCall: ipcRenderer.invoke('client-tool:execute', { call, grant })`。

这意味着 Host 层 Hook 可以覆盖 UI/Renderer 发起的本地能力调用。

### 2. 内部 Agent/Goal 路径

文件：`apps/desktop/electron/main/chat-runtime/projected-tool-executor.mjs`

走查结论：
- 内部 projected tool executor 也 `createLocalToolHost(...)`。
- 因此 Hook 如果挂 `createLocalToolHost()`，也能覆盖内部 agent 调本地工具的路径。

### 3. Projection Guard 的现实状态

文件：`apps/desktop/electron/main/runtime-gateway/projection-guard.mjs`

走查结论：
- `projection-guard.mjs` 定义了 `validateRequest(event)`，检查 `event.type === 'client_tool_call.request'`、`sessionId`、`projectionId`、`capabilityId` 是否投影，以及 capability health。
- 但本轮搜索没有发现它在主执行路径中被调用。

影响：设计文档里说 Hook 在 projection guard 之后是正确目标态，但**当前代码落地时不能假设 projection guard 已接入**。阶段一要么先把 guard 接入 Host 前置；要么在 Hook 文档/代码里明确"Host 接收到的调用已经由上游保证 projection"，并把 guard 接入列为前置重构项。

建议：阶段一编码时优先做一个 `executeWithGuardsAndHooks()` seam：未来 projection guard、hook runner 都挂这里。

---

## 三、最小改动面

### 新增文件（建议）

1. `apps/desktop/electron/main/runtime-gateway/hook-runner.mjs`
   - 读取/合并 hooks 配置。
   - matcher 匹配 `capabilityId` / Shell arguments pattern。
   - 子进程执行外部 command。
   - 超时、exit code、stdout JSON 解析。
   - 输出统一 `HookDecisionRecord[]`。

2. `apps/desktop/electron/main/runtime-gateway/hook-evidence.mjs`
   - `appendHookEvidence(result, hookRecords, finalDecision)`。
   - 统一把 hook 记录写入 `result.evidence.hooks`（或 `result.evidence.extensions.hooks`，编码时二选一）。

3. `apps/desktop/electron/main/runtime-gateway/hook-config.mjs`
   - 全局/工作区配置路径解析。
   - schema 验证。
   - 后续可迁移到阶段二 SDK。

### 修改文件（建议）

1. `apps/desktop/electron/main/runtime-gateway/local-tool-host.mjs`
   - 构造时接收 `hookRunner` 或 `hooksConfig`。
   - `execute()` 前：运行通用 `PreToolUse`。
   - 若 deny：返回 `createFailedClientToolResult()` + denied `createPermissionGrant()`，并附 hook Evidence。
   - Provider 执行后：运行 `PostToolUse`，附 hook Evidence。

2. `apps/desktop/electron/main/runtime-gateway/local-shell-provider.mjs`
   - 在 `classification` 之后、`permissionReview.decideShellExecution()` 前，调用 Shell 精细 PreToolUse。
   - 将 hook decision 作为 `localApproval` 或新增参数合流到 `PermissionReview`。

3. `apps/desktop/electron/main/runtime-gateway/permission-review.mjs`
   - 不建议把 hook runner 直接塞进这里。
   - 只需支持一个更通用的外部决策输入，如 `preDecision` / `hookDecision`，并按"取最严"合流。
   - 保持 `PermissionReview` 作为 Shell PermissionRule 入口，不变成通用 hook 执行器。

4. `apps/desktop/electron/main/main.mjs` 与 `chat-runtime/projected-tool-executor.mjs`
   - 初始化 LocalToolHost 时传入相同 HookRunner/配置根。
   - 确保 Electron IPC 路径和内部 agent 路径行为一致。

### 测试文件（建议新增/扩展）

- 新增：`apps/desktop/electron/main/runtime-gateway/hook-runner.test.mjs`
  - stdout JSON allow/ask/deny。
  - 非零退出。
  - 超时。
  - matcher。

- 扩展：`apps/desktop/electron/main/runtime-gateway/local-tool-host.test.mjs`（若没有则新建）
  - PreToolUse deny 阻断 provider 执行。
  - PostToolUse 失败不阻断结果。
  - hook Evidence 写入 result。

- 扩展：`apps/desktop/electron/main/shell-system.test.mjs`
  - `L5_destructive` + hook allow 仍 deny。
  - hook deny 比 PermissionRule allow 更严。
  - PreToolUse fail-closed 超时 deny。

---

## 四、与原设计的偏差/修正建议

### 修正 1：不能只把 Hook 植入 PermissionReview

原因：`PermissionReview` 当前是 Shell-specific；file/web/mcp/goal/skill 等 Provider 都自己构造 grant/result，有些通过 `context.requestPermission`，有些直接 grant。若只改 `PermissionReview`，公共社区标准的 PreToolUse/PostToolUse 不能覆盖所有 capability。

修正：新增 Host 层 HookRunner，作为公共切面；PermissionReview 只接收 Shell 精细决策合流。

### 修正 2：当前 projection guard 未明显接入主执行路径

原因：走查只发现 `projection-guard.mjs` 定义，未发现主执行调用。

修正：阶段一实现时把 `projection guard + hook runner` 设计为同一个 Host 前置 seam，或者先保持 Hook 在 Host execute 内，但在文档/代码注释里声明 projection guard 接入是前置技术债。

### 修正 3：Evidence 需要统一附加 helper

原因：各 Provider 自己构造 Evidence；如果逐个加 hooks 字段会产生重复和漂移。

修正：新增 `appendHookEvidence()`，Host 层统一改 result。

---

## 五、阶段一可执行落地顺序

1. 新增 `hook-runner.mjs`，只支持内存传入 hook 定义（先不读文件），把执行/超时/stdout JSON 解析测稳。
2. 在 `local-tool-host.mjs` 接入 Host 层 Pre/Post（测试用 fake hookRunner）。
3. 新增 `appendHookEvidence()`，确认所有 Provider result 都能被附加 hook records。
4. 再加 `hook-config.mjs` 读取全局/工作区 `hooks.json`。
5. 最后接 Shell classification 后的精细 PreToolUse 与 `PermissionReview` 合流。

这个顺序可以把风险拆开：先验证通用切面，再接配置，再接 Shell 高风险细粒度。

---

## 六、结论

阶段一 Hook 可落地，且代码结构已经有较好的统一 seam：`LocalToolHost.execute()` + `CapabilityProviderRegistry.execute()`。

但落地时需要注意三点：
1. **通用 Hook 不应只放在 `PermissionReview`**，否则只覆盖 Shell。
2. **PostToolUse/Evidence 应通过统一 helper 附加**，否则 Provider 分散修改会失控。
3. **projection guard 当前可能未接入主执行路径**，阶段一最好顺手预留 `executeWithGuardsAndHooks()` 作为后续 SDK/TUI 的统一入口。

建议下一步进入编码时，先做最小闭环：`hook-runner.mjs` + Host 层 Pre/Post + Evidence 附加 + 单元测试；Shell 精细合流作为第二个 PR/commit。
