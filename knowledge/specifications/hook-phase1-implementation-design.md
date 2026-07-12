# 阶段一 Hook 植入 —— 落地设计

> 创建时间：2026-07-09
> 最后更新：2026-07-09
> 状态：落地设计（可执行规范，尚未落地实现）
> 归属：三阶段路线图（`knowledge/playbook/tui-hook-sdk-roadmap.md`）中的「阶段一」
> 关联知识：`knowledge/specifications/tui-and-hook-design-standard.md`、`knowledge/decisions/16-skill-call-lifecycle.md`、`knowledge/decisions/35-mode-scoped-tool-projection.md`、`knowledge/specifications/09-high-risk-write-scope.md`
> 关联代码：`peer_agent`（本文件是实现依据，代码改动在该仓落地）
> 一句话：一期只做 `PreToolUse` + `PostToolUse` 两个外部命令 hook，挂在 Local Tool Host 的 `client_tool_call` 执行闭环里，与 `PermissionReview` 决策合流，全程 Evidence 落账。

---

## 一、插入点：hook 挂在哪

现有工具调用闭环（`16` 号）：

```text
Gateway 下发 client_tool_call.request
  → 客户端 projection guard（sessionId / projectionId / capabilityId 校验）
  → Local Tool Host 按 capabilityId 路由到 Provider
  → Provider 内部 command classification → PermissionReview（读/写 PermissionRule）
  → 执行 → ClientToolResult + Evidence → 回传 Gateway
```

一期 hook **不新增链路**，只在这条闭环里插两刀：

```text
client_tool_call.request
  → projection guard
  → [PreToolUse hook] ────┐
  → PermissionReview      ├── 决策合流（见第四节）
  → Provider 执行         ┘
  → [PostToolUse hook]
  → ClientToolResult + Evidence
```

关键约束（继承自 `16`/`35`/`09`）：
- hook 位于 **projection guard 之后**：projection 没投影的 capability，hook 根本看不到，无权唤起。
- `PreToolUse` 位于 **PermissionReview 决策合流环节**：它与 PermissionRule 是"与"关系，只能收紧不能放宽。
- hook 不写 `CapabilityProviderRegistry`、不堆 `capabilityId === ...` 分支，仅作为 Local Tool Host 的一个前/后置切面。
- hook 不是新执行通道：不能绕过 Gateway / Local Tool Host 另起进程去"代替"工具执行，只能返回决策/附加信息。

---

## 二、Hook 配置格式

一期采用**外部命令形态（形态 A）**：语言无关、与主进程强隔离，适合作默认。

配置文件位置（分层，后者覆盖前者，参考 opencode 加载顺序）：
- 全局：`<userData>/hooks/hooks.json`
- 工作区：`<workspace>/.peer/hooks.json`

```jsonc
{
  "$schema": "peer-agent/hooks.schema.json",
  "version": 1,
  "hooks": {
    "PreToolUse": [
      {
        "id": "block-rm-rf",
        "match": { "capabilityId": "local.shell.exec", "argumentsPattern": "rm -rf*" },
        "command": "./.peer/hooks/guard-rm.sh",
        "timeoutMs": 3000,
        "onError": "fail-closed"
      }
    ],
    "PostToolUse": [
      {
        "id": "audit-log",
        "match": { "capabilityId": "*" },
        "command": "./.peer/hooks/audit.sh",
        "timeoutMs": 2000,
        "onError": "fail-open"
      }
    ]
  }
}
```

字段说明：
- `match.capabilityId`：精确值或 `*`；只能匹配当前 projection 已投影的 capability。
- `match.argumentsPattern`：对参数的 glob（一期仅对 `local.shell.exec` 的命令串生效，`exact` / `prefix` 语义，禁用可放宽风险的宽通配当 allow 用）。
- `command`：本地可执行；工作区级 hook 的 command 必须在 workspace 内（防止指向任意路径）。
- `timeoutMs`：单个 hook 超时上限。
- `onError`：`fail-closed`（默认，超时/非零退出/异常都当拒绝）或 `fail-open`（仅允许用于 PostToolUse 等不影响放行的场景）。

作用域与合并：多来源同事件的 hook **按 全局 → 工作区 顺序依次执行**；任一 `PreToolUse` 给出 deny 即短路拒绝。

---

## 三、事件与 payload schema

### 3.1 通用 IO 契约
- 输入：hook 进程从 **stdin** 读一个 JSON。
- 输出：从 **stdout** 读一个 JSON 决策（可选）；同时看 **exit code**。
- 约定：`exit 0` = 放行/正常；非 0 = 拒绝（PreToolUse）或记为失败（PostToolUse）。stdout 的 JSON 决策优先级高于 exit code。

### 3.2 PreToolUse 输入（stdin）
```jsonc
{
  "event": "PreToolUse",
  "sessionId": "…",
  "projectionId": "…",
  "conversationId": "…",
  "call": {
    "toolCallId": "…",
    "capabilityId": "local.shell.exec",
    "arguments": { "command": "rm -rf /tmp/x", "cwd": "…" }
  },
  "classification": { "riskLevel": "L5_destructive", "kind": "destructive" }
}
```
> 字段直接取自 `client_tool_call.request` 的 `sessionId / projectionId / conversationId / call.toolCallId / call.capabilityId / call.arguments`，外加 Shell Provider 的 command classification 结果，让 hook 能基于风险分级判断。

### 3.3 PreToolUse 输出（stdout，可选）
```jsonc
{ "decision": "deny", "reason": "rm -rf 命中禁用规则" }
// decision ∈ "allow" | "ask" | "deny"；缺省视 exit code
```

### 3.4 PostToolUse 输入（stdin）
```jsonc
{
  "event": "PostToolUse",
  "sessionId": "…",
  "call": { "toolCallId": "…", "capabilityId": "…" },
  "result": {
    "status": "success",           // success | failed | cancelled | running
    "outputPreview": { "…": "redacted" },
    "artifactRefs": ["local-shell-artifact://…"]
  }
}
```
> PostToolUse 拿到的是 `ClientToolResult` 的 redacted 视图 + artifact refs（对齐 `16`：云端只拿 redacted preview 和 artifact 引用）。PostToolUse **不能改结果**，只做格式化/审计/通知。

---

## 四、决策合流算法（PreToolUse × PermissionReview）

三态：`allow` / `ask` / `deny`。合流是"取最严"，且高风险红线不可被放宽：

```text
输入：hookDecisions[]（各 PreToolUse hook 的 decision）、ruleDecision（PermissionReview 依 PermissionRule + classification 得出）

1. 若 classification.riskLevel == L5_destructive:
      → 直接 deny（09 号红线；hook 的 allow 无效，任何 auto 模式不可覆盖）
2. 若 任一 hookDecision == deny 或 任一 hook onError=fail-closed 且失败:
      → deny
3. 若 ruleDecision == deny:
      → deny
4. 若 任一 hookDecision == ask 或 ruleDecision == ask:
      → ask（走本地授权 UI；无 UI 或未命中 allow rule 时按 16 号默认拒绝）
5. 否则（hook 与 rule 均 allow / 无意见）:
      → allow
```

要点：
- **只能收紧**：hook 的 `allow` 永远不能把 PermissionReview 的 `ask/deny` 提升为放行。
- **PermissionReview 仍是写 PermissionRule 的唯一入口**：hook 不写 rule store，只在单次调用上表达 allow/ask/deny。
- **allow rule 约束不变**（`16`）：match 仅 `exact`/具体 `prefix`、绑定 workspace `scope.cwd`、声明 `scope.maxRiskLevel` 且不覆盖 `L5_destructive`。

---

## 五、失败、超时与隔离

| 场景 | PreToolUse | PostToolUse |
|---|---|---|
| 超时 (`timeoutMs`) | 按 `onError`；默认 fail-closed → deny | 默认 fail-open → 记失败，不阻断结果回传 |
| 非零退出 | 视为 deny（除非显式 fail-open） | 记为 hook 失败，写审计 |
| 进程崩溃 | fail-closed → deny | fail-open → 记失败 |
| 高风险动作 | **一律 fail-closed**，忽略 hook 的 fail-open 配置 | —— |

隔离：hook 以独立子进程执行，崩溃不影响 Local Tool Host；总时长受 `timeoutMs` 约束，避免拖垮工具调用闭环。

---

## 六、Evidence 落账

每次 hook 触发都作为 Evidence 的一部分记录（对齐 `16`：进本地队列、Gateway 连通后 flush）：

```jsonc
{
  "toolCallId": "…",
  "hooks": [
    { "id": "block-rm-rf", "event": "PreToolUse", "decision": "deny",
      "reason": "…", "durationMs": 42, "outcome": "ok" },
    { "id": "audit-log", "event": "PostToolUse", "outcome": "fail-open-timeout", "durationMs": 2001 }
  ],
  "finalDecision": "deny"
}
```
- hook 决策与最终合流结果一并进入该 toolCall 的 Evidence，可审计回放。
- 云端账本以最终 `ClientToolResult` 为准；hook 记录是决策链的证据，不改变 result 语义。

---

## 七、一期验收清单

- [ ] `PreToolUse` / `PostToolUse` 可经 `hooks.json` 声明并生效。
- [ ] hook 位于 projection guard 之后、只对已投影 capability 生效。
- [ ] 合流算法实现"取最严"，hook allow 不能放宽 PermissionReview。
- [ ] `L5_destructive` 恒 deny，不被 hook / auto 覆盖（`09` 号红线）。
- [ ] `onError` 语义正确：PreToolUse 默认 fail-closed，高风险强制 fail-closed。
- [ ] hook 以独立子进程执行且受 `timeoutMs` 约束，崩溃不影响主闭环。
- [ ] 每次 hook 决策写入 Evidence 并可回放。
- [ ] PostToolUse 只拿 redacted result，不能改写结果。

## 八、明确不做（一期范围外）

- 进程内插件形态（形态 B）——留待受信扩展，二期评估。
- `UserPromptSubmit` / `SessionStart` / `Stop` / `PreCompact` 等其余生命周期点——二期。
- hook 动态热加载、hook 市场/分发——不在一期。
