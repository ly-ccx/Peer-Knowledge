# Hook / Runtime SDK / TUI 三阶段实施路线图

> [!NOTE] 2026-11-16 历史阶段归档与终局升级（[ADR 133](../decisions/133-unified-rust-core-and-dual-host-architecture.md)）
> 本文记录 2026-07 TS 路线图（Hook 植入 → TS `@peer-agent/runtime-sdk`（`0.1.0-rc.*` 后续已随列车发布至 npm）→ OpenTUI 瘦客户端切片）。随 ADR 129（`PR #133` / `129-native-rust-cli-and-ratatui.md`）与 [ADR 133](../decisions/133-unified-rust-core-and-dual-host-architecture.md) 定案，终局不再让 CLI 或 Desktop 长期构建在 TS `@peer-agent/runtime-sdk` 上，而是统一收敛至 **Rust Core + 双宿主表达**；本文第一阶段沉淀的 **Hook 点顺序（`PreToolUse`/`PostToolUse`）、`allow/ask/deny` 只能收紧、高风险硬 deny、fail-closed 及 Evidence 落账契约** 全部升格为 Rust Core 必须补齐的等价验收标准。

> 创建时间：2026-07-09
> 最后更新：2026-11-16（关联 ADR 133 路线归档升级；原快照 2026-07-14）
> 状态：执行中（阶段一、Runtime SDK Phase 2.1/2.2 与 Phase 2.3 发布准备已完成；待实际 npm 发布）
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
- Phase 2.1 实施快照：`packages/protocol` 已成为最小 Runtime 工具调用、结果、请求和执行上下文契约的单一来源；SDK root 入口重新导出这些权威类型，并保留旧 `RuntimeSdk*` 名称作为兼容别名。新增公共 API/类型兼容测试与 Desktop SDK 主链路测试，严格验证 `PreToolUse → PermissionGrant → Provider → PostToolUse → Evidence → Runtime Event`。
- Phase 2.2 实施快照：稳定 Session / Turn 身份、单活动 turn、单调 `turnIndex`、resume、SDK 所有的 `AbortSignal`、`cancelled` / `failed` 终态保护和跨 turn Runtime Event 顺序已进入 `@peer-agent/runtime-sdk`；Desktop 通过宿主 Adapter 转换结构化取消，不在 SDK 中引入 Electron、文件系统、子进程或 UI 依赖。
- Phase 2.3 发布准备已完成；实际 npm registry 发布尚未执行。`@peer-agent/protocol`、`@peer-agent/runtime-core`、`@peer-agent/runtime-sdk` 已形成统一 `0.1.0` 公共包族，补齐 `dist`、root exports、类型声明、README、SemVer 兼容策略、MIT/Node/public access 元数据和 `prepack`；SDK 的工作区依赖在 tarball 中转换为 `^0.1.0`。
- Phase 2.3 验证结果：三包 tarball 内容白名单、空项目离线安装、ESM 导入、外部严格 TypeScript 消费、深层导入拒绝、Runtime Core/SDK 测试、三包类型检查与构建、Desktop 构建、宿主隔离、架构治理、版本检查和差异格式检查均通过。`runtime-node` 不在首批公共发布包中。
- 阶段三：`apps/tui` 已形成 OpenTUI + Bun 的首个真实 Agent 纵向切片，并通过公共 Node Hook Host 接入 deny、ask→审批和 PostToolUse Evidence；完整会话恢复、多模式与非交互产品能力仍待建设。
- 下一步：在单独、显式的发布操作中确认 npm scope 权限、凭证、目标版本与 dist-tag 后发布三个 `0.1.0` 公共包；在此之前阶段二“已发布”退出条件保持未完成。不得为 Desktop/TUI 新建私有 Hook、权限或 Evidence 路径。

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
把本机共享 Runtime 的核心能力（任务、能力投影、工具调用、权限、Evidence、事件流）沉淀为一个**独立、版本化、契约清晰的公共 SDK**，供 Desktop、TUI/CLI、可能的 IDE 扩展共用。

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
- [ ] SDK 作为独立包发布，边界清晰、有版本（Phase 2.3 发布准备已完成；实际 npm 发布未执行）。
- [x] 现有 Electron GUI **能改用 SDK**（至少验证主链路走通），证明 SDK 不是空壳（Phase 2.1 已完成）。
- [x] SDK 契约与 `packages/protocol` 单一来源一致，无第二套协议（Phase 2.1 已完成最小 Runtime 执行契约收口）。
- [x] hook 扩展点、权限三态、Evidence 落账都由 SDK 统一提供（Phase 2.1 已由 Desktop 主链路测试验证）。
- [x] Session / Turn 生命周期、resume、结构化取消和跨 turn 事件顺序由 SDK 统一管理（Phase 2.2 已完成）。
- [x] Protocol / Runtime Core / Runtime SDK 三包产物、发布元数据、公共文档和 tarball 外部消费验收通过（Phase 2.3 发布准备已完成）。

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
