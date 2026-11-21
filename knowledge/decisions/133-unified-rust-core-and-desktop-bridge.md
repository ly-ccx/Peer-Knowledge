# ADR 133：统一 Rust Core 基座与 Desktop 接入架构（Classic 先行）

- 状态：Accepted（2026-11-21；Milestone C0–C3a 已在 `codex/native-rust-cli` 上实现并受 `PEER_CORE_CLASSIC=1` 门控，余 C3b/C4 待推进）
- 创建 / 更新：2026-11-21
- 级别：A
- 依赖：0001、22、48、54、74、85、129、130、131、132

## 1. 背景与问题

随着原生 Rust CLI 迁移（ADR 129–132）及 Bot Harness 五阶段补齐完成，代码仓已形成 Rust（`peer-protocol`、`peer-store`、`peer-runtime`、`peer-project-agent`、`peer-tui`、`peer-cli`）与 TypeScript / Node（`packages/runtime-node`、`packages/runtime-core`、`apps/desktop/electron/main/{chat-runtime,agent-host,project-agent}`）两套并行的 Agent 内核，仅靠磁盘文件与跨进程租约协同。

继续长期维持双内核会导致每一项模型线、上下文压缩、权限门控、独立核验或协调语义改动都要双端实现并靠跨语言夹具对齐。同时，`apps/desktop` 已把 Renderer（React UI）与主进程域通过 `electron/ipc/channels.mjs` 及领域级 IPC 注册器清晰解耦，可以在保持 Renderer 契约稳定的前提下，将 Desktop 后端执行内核分阶段收敛到同一套 Rust Core。

用户于 2026-11-21 明确拍板采用 **Classic 先行** 收口路径：先以受控桥梁接入 Classic（`chat:*`、`permission:*`、`goalPlans:*` / `goalRunner:*`），再顺接 Bot、Automation 与远程设备连接。

## 2. 核心架构决策

### 2.1 单一 Rust 基座与单二进制多入口

1. 新增内部 library crate `crates/peer-core-rpc`（`#![forbid(unsafe_code)]`，`publish = false`，版本号与根 `VERSION` 保持一致）。
2. `peer-core-rpc` 只允许依赖 `peer-protocol`、`peer-store`、`peer-runtime`、`peer-project-agent` 等基座 crate，**严禁依赖 `peer-tui` 或 `peer-cli`**，严禁引入 `napi-rs` 或 `unsafe` FFI 绑定，严禁反向拉起 Node / Bun / Electron sidecar。
3. 不另起第二个重型守护进程二进制；复用既有 `peer-native`（发布名 `peer`）暴露 `peer core --stdio` 子命令。Desktop 打包直接复用 `apps/desktop/electron-builder.yml` `extraResources/bin/` 与 macOS 签名/公证脚本（`after-sign.cjs`），与 `peer-credential-helper` 遵循同一打包与校验路径。

### 2.2 跨平台两阶段传输演进

通信协议采用版本化、跨平台（macOS / Windows / Linux）有界 NDJSON JSON-RPC 2.0（`protocolVersion = 1`，单帧上限 `2 MiB`，支持双向请求/响应与单向事件通知，绝不监听公网或明文 TCP 端口）：

1. **阶段一（C0–C3 与 Bot 接入期）：`peer core --stdio` 私有托管子进程**  
   由 Desktop Electron Main 的组合根（`desktop-composition-root.mjs`）统一管理 `peer core --stdio` 的启动握手、健康探测（`core.ping`）、崩溃清理与按序重连、以及应用退出前的优雅排水（`core.shutdown`）。
2. **阶段二（后续共享宿主期）：本机 UDS / Named Pipe 共享 Daemon**  
   当 Classic、Bot 与后台服务均切至 Rust Core 后，同一套 RPC 协议升级到同 UID 权限隔离的 Unix Domain Socket（0600）/ Windows ACL Named Pipe 本机共享 Daemon，使 Desktop 与 `peer` CLI 共用同一宿主实例，彻底消除跨进程 `host.lease` 竞争，并自然支撑 ADR 74 的内网自托管拓扑；同时 CLI 继续保留 `--standalone` 直连退路（不违背 ADR 129 的独立无副作用 CLI 能力）。

### 2.3 唯一能力主链与反向宿主能力桥（`ExternalRpcProvider`）

所有本地与桌面能力必须继续穿过唯一主链，禁止旁路或双写授权真相：

```text
Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
```

1. **桌面原生壳层留在 Electron Main**：`BrowserWindow` / `QuickChat` / `Tray` / `AppMenu` / `Shortcuts` / `auto-updater`、L1 内嵌 `<webview>` 操控（`browser-window-controller`）、`appshot` 截屏、`desktop-preview` 视觉复核、Chrome Cookie 会话导入、`resource-window` / `resource-edit` 与原生文件对话框留在 Electron Main。
2. **动态注册反向宿主能力（`ExternalRpcProvider`）**：上述桌面专属能力在模型回合仍可见时，由 Electron Main 在 `core.initialize` 握手声明其受限 Manifest 清单，经 `ExternalRpcProvider` 注册进 Rust `ProviderRegistry`。工具投影、权限门槛（`PermissionGrant`）与 `Evidence` 归档仍完全由 Rust Runtime 拥有；仅在实际获准执行时通过反向 RPC `host.*` 回调 Electron 执行，Desktop 断开时自动卸载，不污染纯 CLI 运行环境。
3. **凭据边界不变**：API Key 与 OAuth 凭据继续严格通过独立原生进程 `peer-credential-helper` 与系统 Keychain 交互（ADR 0001 / ADR 132），不经 JSON-RPC 暴露给 Renderer，也不写入日志或命令参数。

### 2.4 Classic 先行四阶段切片与灰度门禁

统一接入采用隔离灰度、按域渐进切换与可逆回退：

| 阶段 | 范围 | 验收与灰度边界 |
|---|---|---|
| **C0（已完成，`b55bf1fe`）** | 新增 `peer-core-rpc`（跨平台 `tokio::io` `--stdio` 骨架：`core.initialize`、`core.ping` 含双向 `probeHost`、`core.capabilities.list`、`core.shutdown`）+ `peer core --stdio` + Electron `peer-core-client.mjs` + Desktop 打包接线 | 受 `PEER_CORE_CLASSIC=1` 环境变量显式门控（默认关闭，零改变现有生产与开发行为）；验证 Rust↔Node 握手、双向探针、异常退出自愈、优雅退出与边界门禁 |
| **C1（已完成，`d1c96d62`）** | Classic Chat + Plan 核心执行链（`chat:send`、`chat:abort`、`chat:stream:reattach` / `list-active`、`chat:compact`、`permission:approve` / `deny`） | Rust `NativeConversationRuntime` 扩展 prepared-turn（消费外部 `assistantMessageId` 与节流 sidecar/终态提交）、`ClassicStreamRegistry`（ADR 22 5 分钟保留）、15 路 `chat:stream:*` 投影、双向权限审批、`ExternalRpcProvider`；TS 与 Rust 可按开关切换且不破坏磁盘 JSONL 契约 |
| **C2（已完成，`9280c3ec`）** | Classic Goal 模式 + Goal Runner + Worktree Handoff + `desktop-preview` 视觉复核回调 | 接管 `chat:start-task`、`goalPlans:*`、`goalRunner:*`，复用 Rust Goal Runner 与独立 Verifier |
| **C3a（已完成，`afe26aac`）** | Classic 周边 5 域收口至 `peer-core-rpc`（43 个 JSON-RPC 方法：`classic.conversations.*` 20、`classic.usage.*` 4、`classic.skills.*` 8、`classic.mcp.*` 8、`classic.llm.*` 3）+ `peer-store` 持久化/查询原语 | Electron Main 受 `PEER_CORE_CLASSIC=1` 门控接管上述 5 域读写与 LLM 调用，同时保持桌面壳层清理、live MCP probe/OAuth/vault 与 IPC 411 通道契约不变 |
| **C3b（待推进）** | Classic 默认灰度切换与实机/回归验收，分批退役 Electron Main 中 `chat-runtime/`、`agent-host/` 等 TS 重复引擎 | 放开默认流量门控前的稳定性、性能与回退演练达标后切换默认路径 |
| **C4（待推进）** | `project-agent` Bot、`automations` 与 `remote-device-connector` 切换至 Rust Core，推进本机 UDS / Named Pipe 共享宿主升级并最终清理 `packages/runtime-node` | 全运行形态收敛至单一 Rust Core 基座，消除跨进程 `host.lease` 竞争 |

## 3. 红线与非目标

1. 不重写 React Renderer；`apps/desktop/electron/ipc/channels.mjs` 对渲染层的通道名、权限策略与语义契约保持兼容。
2. 不得为桌面同步引入第二套 Agent loop 决策或第二份磁盘存储格式；所有已持久化会话、Goal、Evidence 与用量账本继续遵循 `~/.peer-agent` 单一真源（ADR 48 / 74 / 131）。
3. 本 ADR 不撤销或破坏公开 TypeScript 编排接口 `@peer-agent/runtime-sdk` 与 `@peer-agent/protocol` 的对外契约（ADR 54 / ADR 129 §2.6）。
4. C0–C3a 仅在显式开启 `PEER_CORE_CLASSIC=1` 时走 Rust Core，在 C3b 切换默认路径前不改变默认用户流量或既有发布门禁结果语义。
