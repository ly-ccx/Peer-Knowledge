# Hook / Runtime SDK / TUI 三阶段实施路线图

> 创建时间：2026-07-09
> 最后更新：2026-07-12
> 状态：执行中（Hook 跨宿主公共化已落地；Runtime SDK 内核与 TUI 首个纵向切片已落地）
> 顺序（已确认）：阶段一 Hook 植入 → 阶段二 Runtime 抽 SDK → 阶段三 TUI 构建
> 关联知识：`knowledge/specifications/tui-and-hook-design-standard.md`（对标与设计标准）、`knowledge/decisions/16-skill-call-lifecycle.md`、`knowledge/decisions/35-mode-scoped-tool-projection.md`、`knowledge/specifications/09-high-risk-write-scope.md`
> 关联代码：`peer_agent`（本文件是规划依据，代码改动在该仓落地）

---

## 〇、总纲

三步走，**顺序不可颠倒**，每一步都为下一步铺路：

1. **阶段一：Hook 植入 + 对齐公共社区标准** —— 在现有主链路的既有关卡上开放可配置扩展点，先把"标准"立起来。
2. **阶段二：核心 Runtime 层抽成公共 SDK** —— 把云端 Runtime 的能力/协议沉淀成独立、可复用的 SDK，作为多客户端的唯一契约。
3. **阶段三：基于 SDK 构建独立 TUI** —— TUI 作为连同一 Runtime 的瘦客户端落地。

为什么是这个顺序：
- Hook 先行，是因为它**不需要新架构**，只在既有 `PermissionGrant`/`Evidence` 关卡上挂切面，风险最小、能立刻对齐社区标准、并为后两步定义好"扩展点契约"。
- SDK 居中，是因为 TUI 必须复用 Runtime，**先有干净的 SDK 边界，TUI 才不会长成又一套旁路**。
- TUI 收尾，是因为它是纯客户端形态，依赖前两步产出的 hook 契约 + SDK 契约。

主链路（所有阶段共同锚点，见 `16` 号）：

```text
Capability Provider -> Manifest -> Runtime Projection -> client_tool_call -> PermissionGrant -> Evidence
```

### 当前实施快照（2026-07-12）

- 阶段一：Desktop Hook 闭环与**跨宿主公共 Hook Host** 已落地。外部命令 Runner、配置发现、matcher、超时及 fail-open / fail-closed 策略集中在 `@peer-agent/runtime-node`；Desktop 与 TUI 共用全局 `<userDataPath>/hooks/hooks.json` 和工作区 `.peer/hooks.json`。
- 阶段二：`@peer-agent/runtime-sdk` 已提供宿主中立 Hook Port、Runtime Event 与 Pipeline；`@peer-agent/runtime-node` 提供 Node Provider Bundle 和 Node Hook Host。SDK 仍保持不依赖文件系统、进程执行、Electron 或 UI 框架。
- 阶段三：`apps/tui` 已形成 OpenTUI + Bun 的首个真实 Agent 纵向切片，并通过公共 Node Hook Host 接入 deny、ask→审批和 PostToolUse Evidence；完整会话恢复、多模式与非交互产品能力仍待建设。
- 下一步：继续收口 SDK 发布边界和 Desktop 剩余 Runtime 迁移，再扩展 TUI 的会话、模式和分发能力；不再为 Desktop/TUI 新建私有 Hook 执行路径。

---

## 阶段一：Hook 植入并对齐公共社区标准

### 目标
在既有主链路上开放**用户可配置的生命周期 hook**，并让其行为契约对齐公共社区标准（Claude Code 外部命令 hook / opencode 进程内插件 hook 两种形态）。

### 对齐的社区标准（详见设计标准文档）
- 声明式配置：`matcher + command`（或插件导出 hooks 对象）。
- 三态权限决策：`allow / ask / deny`，且**显式 deny 不被任何自动批准模式覆盖**（对齐 opencode `--auto`）。
- 标准 IO 契约：外部命令走 stdin JSON / stdout+exit code。
- 事件覆盖：一期先做 `PreToolUse` + `PostToolUse`。

### 映射到现有主链路
| Hook 点 | 挂载关卡 | 作用 |
|---|---|---|
| `UserPromptSubmit` | 进入 System Context 前 | 注入 / 脱敏（可二期） |
| `PreToolUse` | **`PermissionReview` / `PermissionGrant` 之前** | 阻断点，与既有 PermissionRule 合流，任一 deny 即拒绝 |
| `PostToolUse` | **`Evidence` 落账阶段** | 格式化 / 审计，写入同一 Evidence 账本 |

### 进入条件
- 设计标准文档已就绪（✅ `tui-and-hook-design-standard.md`）。

### 退出条件（验收）
- [x] `PreToolUse` / `PostToolUse` 可通过全局与工作区配置文件声明，并在 Desktop / TUI 生效。
- [x] hook 决策与 `PermissionReview` 是"与"关系，只能收紧不能放宽；`ask` 进入宿主审批 Port。
- [x] 高风险写动作（`09` 号红线）不被 hook allow 覆盖；PreToolUse 超时和失败默认 fail-closed。
- [x] 每次 hook 触发与决策写入同一结构化 Evidence，可审计回放。
- [x] 一期形态已落定为 `@peer-agent/runtime-node` 的外部命令 Node Hook Host；进程内插件保留为未来受信扩展。

### 主要风险
- hook 成为绕过权限/红线的后门 → 用"只能收紧"约束 + fail-closed 兜底。
- 进程内插件形态引入主进程稳定性风险 → 一期默认外部命令形态。

---

## 阶段二：把核心 Runtime 层抽成公共 SDK

### 目标
把云端 CEO Runtime 的核心能力（会话、能力投影、工具调用、权限、Evidence、事件流）沉淀为一个**独立、版本化、契约清晰的公共 SDK**，供 Electron GUI、未来 CLI、可能的 IDE 扩展共用。

### 对齐的社区标准
- **client/server 分离 + 契约即协议**（对齐 opencode：server 暴露 OpenAPI 3.1，SDK 由 spec 自动生成，客户端不手写请求类型）。
- 复用现有 `packages/protocol` 作为唯一契约来源，SDK 不另立协议。

### SDK 应封装的边界（初稿）
- 会话生命周期：`hello` / `resume` / `send` / 中断。
- 能力目录与投影：mode-scoped projection（`35` 号）。
- 工具调用闭环：`client_tool_call` → `PermissionReview/Grant` → `Evidence`（`16` 号）。
- Hook 契约暴露：阶段一定义的扩展点作为 SDK 一等公民。
- 事件流：流式增量输出、状态事件（供 TUI/GUI 订阅）。

### 进入条件
- 阶段一完成：hook 契约已确定，SDK 需把它作为稳定接口暴露。

### 退出条件（验收）
- [ ] SDK 作为独立包发布，边界清晰、有版本。
- [ ] 现有 Electron GUI **能改用 SDK**（至少验证主链路走通），证明 SDK 不是空壳。
- [ ] SDK 契约与 `packages/protocol` 单一来源一致，无第二套协议。
- [ ] hook 扩展点、权限三态、Evidence 落账都由 SDK 统一提供。

### 主要风险
- 抽象过度或过早 → 以"GUI 能先切过来"作为 SDK 边界正确性的验收锚。
- 协议双写 → 强制复用 `packages/protocol`。

---

## 阶段三：基于 SDK 构建独立 TUI

### 目标
交付一个**独立终端 CLI/TUI**，作为连同一 Runtime 的**瘦客户端**，复用阶段二的 SDK，不自带本地推理/工具编排旁路。

### 对齐的社区标准（详见设计标准文档）
- 流式可中断、键盘优先、工具/权限行内卡片、可 resume、窄终端自适应、非交互 `-p/--print` 管道模式。
- 架构上对齐 opencode 瘦客户端形态（TUI 只是 SDK 的一个消费者）。

### 进入条件
- 阶段二完成：SDK 边界稳定、GUI 已验证可用。

### 退出条件（验收）
- [ ] CLI 通过 SDK 走通完整主链路（会话 → 工具调用 → 权限确认 → Evidence）。
- [ ] 复用 `chat/plan/goal/explorer` 的 mode-scoped projection，无模式旁路。
- [ ] 权限确认在终端渲染为可键盘操作的行内卡片。
- [ ] 支持 resume 与非交互模式。
- [ ] 阶段一的 hook 在 CLI 场景同样生效（同一 SDK 契约）。

### 主要风险
- TUI 绕过 SDK 直连底层 → 以"CLI 只依赖 SDK 包"作为硬约束。
- 渲染库选型分散精力 → 关键在 client/server 分离，渲染层可先用 Node + Ink 起量。

---

## 一、阶段依赖与里程碑

```text
阶段一 Hook 植入 ──→ 阶段二 Runtime 抽 SDK ──→ 阶段三 TUI 构建
   (定义扩展点契约)      (定义客户端契约)         (第一个新客户端)
```

- 阶段一产出 = 阶段二必须暴露的 hook 接口。
- 阶段二产出 = 阶段三唯一依赖的 SDK。
- 三阶段共享同一主链路与三条治理约束，全程不新增旁路。

## 二、贯穿三阶段的治理约束（不可违背）

1. **不另造链路**：hook 是切面、SDK 是封装、TUI 是客户端，都围绕同一条主链路。
2. **只能收紧不能放宽**：hook 与 projection + PermissionReview 是"与"关系。
3. **高风险写红线硬 deny**（`09` 号）：不受任何自动批准 / hook allow 覆盖。
4. **全程 Evidence 落账**（`16` 号）：每次工具调用、hook 决策均可审计回放。

## 三、待决策项（进入各阶段前需拍板）

- 阶段一：hook 形态默认 A（外部命令）还是 A+B 并存？配置作用域分层规则。
- 阶段二：SDK 语言/打包形态；是否同时产出 OpenAPI spec 供多语言客户端。
- 阶段三：TUI 渲染栈（Node + Ink 倾向）；是否复用 opencode 式 `serve` 远程驱动能力。
