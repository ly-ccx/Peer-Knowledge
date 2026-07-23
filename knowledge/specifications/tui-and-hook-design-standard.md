# TUI 与 Hook 设计标准对齐

> 创建时间：2026-07-09
> 最后更新：2026-07-23（对齐双宿主总览：TUI 与 Desktop 平级一等宿主；CLI 可独立 npm 安装）
> 状态：设计标准对齐（调研 + 规范；实现以代码仓为准）
> 定位：TUI = 与 Desktop 平级的一等宿主入口；Hook = 用户可配置的生命周期 hook
> 关联代码：`peer_agent`（`apps/tui`、`packages/npm-cli`）
> 关联知识：`knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`、`knowledge/decisions/48-cli-first-class-release.md`、`knowledge/decisions/16-skill-call-lifecycle.md`、`knowledge/decisions/35-mode-scoped-tool-projection.md`、`knowledge/specifications/09-high-risk-write-scope.md`、`knowledge/specifications/15-goal-plan-lifecycle-governance.md`
> 调研来源（2026-07-09 实证抓取）：opencode 官方文档 `opencode.ai/docs`（Intro / Plugins / Permissions / Server）与仓库 `github.com/anomalyco/opencode`（`packages/tui`、`packages/plugin`、`packages/server`）；其余产品（Claude Code / Codex CLI / Gemini CLI / Aider）为既有认知归纳，未逐项抓取源码。

---

## 〇、本文目的

现在要做两件事：一个**独立的终端 CLI/TUI 入口**，以及一套**用户可配置的生命周期 Hook 机制**。本文不写实现代码，而是先把市面主流能力盘一遍，抽出公认的设计标准，再映射到 `peer_agent` 已有的主链路上，得到一份可以直接作为后续实现验收依据的规范。

核心判断：**Hook 不是新发明，而是把现有主链路的关卡开放成可配置扩展点**；**TUI/CLI 是与 Desktop 平级的一等宿主**，复用同一套 Runtime 契约与本地能力主链路，不能另起旁路。  
「瘦客户端」指 **不另造推理/工具编排**，不是「Desktop 的附属品」；用户可仅通过 `@peer-agent/cli` 安装运行，**不依赖 Desktop 客户端**。

---

## 一、市面主流 TUI 能力对标

| 产品 | TUI 形态 / 技术栈 | 关键设计标准 |
|---|---|---|
| **opencode**（本次重点实证） | 终端 TUI，**client/server 分离**：`opencode` 启动时同时拉起一个 TUI 客户端 + 一个本地 HTTP server（`packages/tui` + `packages/server`）。TUI 用 TypeScript + Bun + **OpenTUI** 渲染（dev 分支 v0.4.3；早期版本曾用 Go/Bubble Tea） | 客户端/服务端解耦、OpenAPI 3.1 spec 自动生成 SDK、多客户端（TUI/desktop/IDE 扩展）共用同一 server、`/tui` 端点可远程驱动 TUI、`--auto` 审批模式、slash 命令（`/connect` 等） |
| Claude Code | 纯终端 TUI（Node + Ink/React） | 流式渲染、Esc 中断、内联 diff 预览、权限确认层、slash 命令、`/hooks` 配置 |
| Codex CLI | 终端 TUI（Rust ratatui） | 全键盘操作、审批模式（suggest / auto-edit / full-auto）、沙箱执行、会话回放 |
| Gemini CLI | 终端 TUI（Node） | 多模态输入、MCP 集成、`@` 上下文文件引用 |
| Aider | 终端交互式 REPL | git 感知、diff/commit 自动化、repo map |

### opencode 架构实证要点（对我们最有参考价值）

opencode 的关键设计不是"终端界面本身"，而是**它把 TUI 做成了一个瘦客户端**，值得我们直接借鉴：

- **client/server 分离**：`opencode` 命令启动 TUI 的同时起一个 headless HTTP server（`opencode serve` 可单独跑）。TUI 只是众多客户端之一，desktop app、IDE 扩展都连同一个 server。
- **OpenAPI 3.1 契约**：server 暴露 `/doc` 的 OpenAPI spec，SDK 由此自动生成 —— 协议即契约，客户端不手写请求类型。
- **可远程驱动**：`--hostname`/`--port` 固定端口后，`/tui` 端点可以 prefill/run prompt，IDE 插件正是靠这个驱动 TUI。
- **对我们的启示**：这与我们"云端 CEO Runtime + 多客户端（Electron / 未来 CLI）"的形态天然同构。**我们的独立 CLI 应当是连到同一 Runtime 的瘦客户端，而不是自带一套本地推理/工具编排**。opencode 用 OpenAPI 生成 SDK 的做法，对应我们应复用 `packages/protocol` 作为唯一契约，CLI 不另立协议。

### 抽象出的 TUI 公认设计标准

1. **流式增量输出可中断**：模型输出边到边渲染，用户可随时（Esc/Ctrl-C）打断当前生成而不退出会话。
2. **键盘优先**：所有核心操作（提交、中断、切换、审批、翻阅历史）都要有键位，不依赖鼠标。
3. **工具调用与权限确认要有行内卡片**：每次工具调用、每次授权确认都是可读的结构化区块，展示能力、参数摘要、风险、Evidence 去向。
4. **状态可恢复（resume）**：会话可中断后重连/续跑，对齐 `16` 号文档的 `runtime.resume` 语义。
5. **窄终端自适应**：在 80 列甚至更窄下不错版；长内容折叠可展开。
6. **非交互模式**：除交互 TUI 外提供一次性 `-p/--print` 管道模式，便于脚本与 CI 调用。

### 对 peer_agent 的 TUI 定位结论

- TUI 是**独立 CLI 客户端**，与 Electron GUI 平级，二者都是"桌面客户端"角色。
- TUI 必须走**同一条主链路**：`Capability Provider → Manifest → Runtime Projection → client_tool_call → PermissionGrant → Evidence`（见 `16` 号文档）。TUI 只是把 GUI 里的确认弹层换成终端行内卡片，**不得**在本地另起 Bash/MCP/Plugin 旁路。
- 权限确认沿用 `PermissionReview` 统一入口；TUI 负责把"待授权"渲染成终端可读、可键盘选择的确认区块。
- 模式（`chat` / `plan` / `goal` / 内部 `explorer`）沿用 `35` 号文档的 mode-scoped projection，TUI 不新增模式旁路。

---

## 二、市面主流 Hook 机制对标

市面上其实有**两种不同的 hook 形态**，我们要清楚地二选一或融合：

### 2.1 形态 A：外部命令 hook（Claude Code）

以 **Claude Code hooks** 为代表，配置 `matcher + command`，触发时以子进程执行外部命令，走 stdin JSON / stdout+exit code 契约。优点是语言无关、与主进程强隔离；缺点是每次 fork 进程、类型契约靠约定。

| Hook 点 | 触发时机 | 典型用途 | 是否可阻断 |
|---|---|---|---|
| `PreToolUse` | 工具执行前 | 校验/改写参数、拦截危险调用 | 是（可拒绝） |
| `PostToolUse` | 工具执行后 | 格式化、lint、审计留痕 | 否（结果已产生） |
| `UserPromptSubmit` | 用户提交输入时 | 注入上下文、脱敏 | 是（可拦截提交） |
| `SessionStart` | 会话开始 | 加载状态、预置上下文 | 否 |
| `Stop` / `SubagentStop` | 主/子 agent 收尾 | 通知、清理、结算 | 视实现 |
| `PreCompact` | 上下文压缩前 | 保存快照 | 否 |
| `Notification` | 需要用户注意时 | 外部通知（IM/邮件） | 否 |

### 2.2 形态 B：进程内 plugin hook（opencode，本次重点实证）

opencode 走的是**另一条路**：hook 不是外部命令，而是 **JS/TS 插件导出的 hooks 对象**，在主进程内按序调用。实证要点：

- **加载来源**：本地目录 `~/.config/opencode/plugins/`（全局）与 `.opencode/plugins/`（项目级）自动加载；或在 `opencode.json` 的 `"plugin"` 字段声明 npm 包，启动时用 Bun 自动安装到 `~/.cache/opencode/node_modules/`。
- **加载顺序**：全局 config → 项目 config → 全局插件目录 → 项目插件目录；所有来源的 hooks **按序依次执行**。
- **编程模型**：插件是一个 async 函数，接收 `context` 对象、返回一个 `hooks` 对象。hook 拿到 `(input, output)` 两个参数，**通过改写 `output` 来影响行为**（如改写 compaction prompt、改写工具参数），而不是靠 exit code。
- **事件清单（实证）**：opencode 的事件覆盖面比 Claude Code 更细，含
  - Tool：`tool.execute.before` / `tool.execute.after`
  - Permission：`permission.asked` / `permission.replied`
  - Session：`session.created` / `session.compacted` / `session.idle` / `session.error` / `session.updated` 等
  - Message：`message.updated` / `message.part.updated` 等
  - 还有 `experimental.session.compacting`（可替换压缩 prompt）、`lsp.updated`、`server.connected`、`todo.updated`、`shell.env` 等。

**两种形态对照**：

| 维度 | 形态 A 外部命令（Claude Code） | 形态 B 进程内插件（opencode） |
|---|---|---|
| 隔离性 | 强（独立进程） | 弱（同进程，插件 bug 可能影响主流程） |
| 类型契约 | stdin/stdout JSON 约定 | TS 类型 + `context/hooks` 对象 |
| 语言 | 任意 | JS/TS |
| 阻断方式 | exit code / stdout 决策 | 改写 `output` / 抛错 |
| 启动成本 | 每次 fork 进程 | 无（常驻） |
| 事件粒度 | 生命周期级 | 生命周期 + 细粒度状态事件 |

### 抽象出的 Hook 公认设计标准

1. **声明式配置**：`matcher`（匹配哪个事件/哪些工具）+ `command`（执行什么），配置文件驱动，不需要改主程序。
2. **明确的阻断能力**：`PreToolUse` 类 hook 必须能阻断后续动作。约定用**退出码**（如非 0 阻断）或 **stdout 返回结构化 JSON 决策**（allow / deny / ask + 原因）。
3. **标准 IO 契约**：输入通过 stdin 传 JSON（事件名、会话、工具名、参数等）；输出通过 stdout（JSON 决策或注入内容）+ exit code。
4. **超时与失败隔离**：单个 hook 有超时上限；hook 失败不得静默放行高风险动作，也不得拖垮主流程（失败策略需显式定义：fail-closed / fail-open 按风险分级）。
5. **可观测**：每次 hook 触发、决策、耗时都要留痕，可追溯。

---

## 三、Hook 生命周期映射到现有主链路（关键）

现有主链路（`16` 号文档）：

```text
Capability Provider -> Manifest -> Runtime Projection -> client_tool_call -> PermissionGrant -> Evidence
```

Hook 不是新链路，而是在这条链路的既有关卡上开放扩展点：

| 通用 Hook 点 | peer_agent 对应关卡 | 说明 |
|---|---|---|
| `UserPromptSubmit` | `chatSend → IPC → mode-source`（进入 System Context 前） | 用户输入进入认知前的注入/脱敏点 |
| `PreToolUse` | **`PermissionReview` / `PermissionGrant` 之前** | 天然的阻断点；hook 决策与既有 PermissionRule 合流：任一 deny 即拒绝 |
| （工具执行） | `Local Tool Host → Capability Provider`（按 capabilityId 路由） | hook 不在此另起旁路，仅围绕这一步前后切面 |
| `PostToolUse` | **`Evidence` 落账阶段** | 结果已产生，hook 做格式化/审计，写入同一 Evidence 账本 |
| `SessionStart` | `client.hello` / `runtime.resume` | 会话建立/续跑边界 |
| `Stop` / `SubagentStop` | Agent loop 终止（含 `explorer` 子 agent 收尾） | 对齐 `26` 号 agent-loop-termination |
| `PreCompact` | 本地上下文压缩前 | 对齐 `17` 号 local-context-compaction |

### opencode 权限模型实证（与我们 PermissionRule 高度同构）

opencode 的 permission 配置几乎就是我们 `PermissionReview` 想要的形态，可直接借鉴：

- **三态决策**：每条规则解析为 `"allow"`（免批直接跑）/ `"ask"`（弹窗确认）/ `"deny"`（阻断），与我们 gate 语义一致。
- **通配 + 对象语法**：可全局 `"*": "ask"` 再按工具覆盖；对 `bash` 还能按输入模式细分，例如 `"git *": "allow"`、`"rm *": "deny"`、`"grep *": "allow"`；对 `edit` 可按路径 glob 放行特定目录。
- **最后匹配优先**：规则按 pattern 匹配、**最后一条命中的规则生效**，惯例是把 catch-all `"*"` 放最前、更具体的规则放后面。
- **auto 模式**：`opencode --auto` / `opencode run --auto` 自动批准所有"非显式 deny"的请求，但**显式 `deny` 始终强制生效**——即 auto 只降 `ask`，不覆盖 `deny`。
- **对我们的启示**：这条"deny 不可被 auto 覆盖"的规则，正好对应我们 `09` 号高风险写红线应做成**硬 deny、不受任何自动批准模式影响**。opencode 的 `bash` 按命令前缀分级，也印证我们对高风险动作做细粒度 gate 的方向。

### 三条必须遵守的治理约束

1. **Hook 不能绕过 projection 与权限**：`PreToolUse` hook 与 `Runtime Projection`（`35` 号）+ `PermissionReview` 是"与"关系，只能收紧、不能放宽。projection 没投影的能力，hook 无权唤起；PermissionRule 拒绝的动作，hook 的 allow 无效。
2. **高风险写动作遵循 `09` 号红线**：hook 不得成为绕过 Governance / Studio / Memory 高风险写动作限制的后门；对这类动作，hook 失败一律 **fail-closed**。
3. **Hook 决策进 Evidence 账本**：每次 `PreToolUse` 的 allow/deny、每次 `PostToolUse` 的处理都要作为 Evidence 留痕，对齐 `16` 号"每次工具调用都过关卡并落账"的原则，可被审计与回放。

---

## 四、设计标准清单（作为后续实现验收依据）

### TUI 验收要点

- [ ] 独立 CLI 入口，走同一条云端 Runtime + 本地能力主链路，无本地旁路。
- [ ] 流式输出且可中断（Esc/Ctrl-C 中断当前生成不退出会话）。
- [ ] 键盘优先，核心操作均有键位。
- [ ] 工具调用 / 权限确认渲染为终端行内结构化卡片。
- [ ] 支持 resume（对齐 `runtime.resume`）。
- [ ] 窄终端（≥80 列）不错版，长内容可折叠。
- [ ] 提供非交互 `-p/--print` 管道模式。
- [ ] 复用 `chat/plan/goal/explorer` 的 mode-scoped projection。

### Hook 验收要点

- [ ] 声明式配置（matcher + command），配置文件驱动。
- [ ] 覆盖生命周期点：`UserPromptSubmit` / `PreToolUse` / `PostToolUse` / `SessionStart` / `Stop` / `SubagentStop` / `PreCompact`（可分期）。
- [ ] `PreToolUse` 具备阻断能力（退出码或 stdout JSON 决策）。
- [ ] 标准 IO 契约：stdin JSON 入、stdout JSON + exit code 出。
- [ ] 每个 hook 有超时；失败策略按风险分级显式定义，高风险 fail-closed。
- [ ] hook 与 projection + PermissionReview 是"与"关系，只能收紧。
- [ ] hook 决策与处理全部写入 Evidence 账本，可审计回放。

---

## 五、待后续决策的开放问题

1. **TUI 技术栈**：代码仓已采用 OpenTUI（`apps/tui`）。opencode 的启示仍是 **契约统一、不另造编排**；我们的实现是「共享 Runtime packages + 宿主 adapter」，不是必须先起一个 Desktop 服务才能跑 CLI。
2. **Hook 形态：外部命令（形态 A） vs 进程内插件（形态 B）**？这是本次调研新增的核心抉择。建议**默认形态 A（外部命令）以获得强隔离与语言无关**，对高风险动作 fail-closed；进程内插件形态 B 留给受信任的一方扩展。二者可共存但走同一决策合流。
3. **Hook 配置位置与作用域**：参考 opencode 的"全局 config → 项目 config → 全局目录 → 项目目录，按序执行"分层模型，定义我们自己的优先级与合并规则。
4. **Hook 执行环境**：本地子进程执行的沙箱与环境变量注入范围。
5. **分期**：建议先落 `PreToolUse` + `PostToolUse`（价值最高、直接挂在 PermissionGrant / Evidence 两个既有关卡上），其余生命周期点二期补齐。

---

## 六、结论

- **opencode 的最大启示是架构而非界面**：契约统一、多宿主共用同一 Runtime 语义。我们的 CLI 应复用 `packages/protocol` + runtime packages，不自带本地推理/工具编排旁路；**且可独立 npm 安装，不依赖 Desktop App**。
- **Hook 有两种事实形态**：外部命令（Claude Code，强隔离）与进程内插件（opencode，细粒度、TS 原生）。我们倾向以外部命令为默认、进程内插件为受信扩展，二者决策合流。
- TUI 与 Hook 都**不另造链路**：TUI 是主链路的一等宿主形态，Hook 是主链路既有关卡上的可配置切面。
- Hook 的 `PreToolUse` ↔ `PermissionGrant`、`PostToolUse` ↔ `Evidence` 是最自然、价值最高的两个接入点，建议一期先落地。
- opencode 的"显式 `deny` 不被 `--auto` 覆盖"印证：我们的 `09` 号高风险写红线应做成硬 deny，不受任何自动批准模式影响。
- 所有扩展点都受 `35`（projection 收敛）、`09`（高风险写红线）、`16`（关卡 + Evidence 落账）三条既有治理约束，hook 只能收紧不能放宽。
