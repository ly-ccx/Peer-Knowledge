# Peer Agent 工程结构设计

> 2026-11-14 局部修订：[ADR 129](../decisions/129-native-rust-cli-and-ratatui.md) 已接受（评审稿原编号 116），CLI 的技术终态改为 Rust / Ratatui；TS 与 Rust 的共享算法 / 资源 / 契约和 conformance 规则见 [ADR 131](../decisions/131-native-cli-contract-storage-and-recovery.md)。仅替换 ADR 129 §3 点名的语言及直接共享实现条款，权限、Evidence、上下文准入与数据真源不变。旧 CLI 仍是迁移期默认入口，不能据设计接受声称已切换或验收。


创建时间：2026-06-10  
最后更新：2026-08-23  

> 状态：工程结构基线（持续修订）  
> 目标：定义 Peer Agent 的仓库组织、模块边界与双宿主落地路径。  
> 关联总览：`knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md`  
> 关联发布：`knowledge/decisions/48-cli-first-class-release.md`

---

## 一、推荐仓库结构

当前 monorepo 以 **Desktop + CLI/TUI 双宿主** 为产品入口，共享 packages 内核：

```text
peer_agent/
├── apps/
│   ├── desktop/                 # @peer-agent/desktop — Electron GUI 宿主
│   │   ├── electron/
│   │   │   ├── main/
│   │   │   └── preload/
│   │   └── renderer/
│   └── tui/                     # @peer-agent/tui (private) — CLI/TUI 构建面 → dist/peer
├── packages/
│   ├── protocol/
│   ├── runtime-core/
│   ├── runtime-sdk/
│   ├── runtime-node/
│   ├── conversation-store/
│   ├── credential-helper/
│   ├── npm-cli/                 # @peer-agent/cli — 公开 npm 安装面（postinstall 拉 peer 二进制）
│   ├── chat-kernel/
│   ├── task-thread/
│   ├── i18n/
│   └── ui/
├── VERSION
├── package.json
├── pnpm-workspace.yaml
└── .github/workflows/release.yml
```

说明：

- **构建包** `@peer-agent/tui` ≠ **安装包** `@peer-agent/cli`（见 ADR 48）。
- CLI 可 `npm install -g @peer-agent/cli` 独立运行，**不依赖 Desktop 客户端已安装**。
- 历史 `crates/cu-proxy-core` 草案若仍存在，不改变「双宿主 + packages 内核」主线。

---

## 二、模块职责

### 2.1 `apps/desktop`

Electron 桌面客户端（`@peer-agent/desktop`）。

职责：

- 窗口、托盘、快捷键。
- 本地 session store。
- 本地 capability registry。
- 本地 project index。
- 安全 IPC 边界。
- Runtime / tool / Goal 编排适配（main 进程）。
- Codex-like task thread。
- Sidebar / Header / Composer。
- Review card。
- Evidence summary。
- 设置入口。
- 可视 browser 控制（Desktop-only 能力）。

限制：

- Renderer 不允许直接读写文件。
- Renderer 不允许直接启动命令。
- Renderer 不允许直接连接 MCP。
- Renderer 不保存密钥。
- Renderer 不成为权限事实源。

### 2.1b `apps/tui` 与 `packages/npm-cli`

| 路径 | npm name | 角色 |
|------|----------|------|
| `apps/tui` | `@peer-agent/tui`（private） | OpenTUI 源码与 `peer` 二进制构建 |
| `packages/npm-cli` | `@peer-agent/cli`（公开） | npm 全局安装器；下载/启动 Release 中的 `peer` |

职责（CLI 宿主）：

- 终端会话、slash / leader、审批与时间线表达。
- 直接挂载共享 Runtime Pipeline（与 Desktop 共用契约）。
- 独立发布：`peer --version`、GitHub Release 归档、npm 安装通道。

限制：

- 运行时不得要求 Electron / Desktop App 已安装。
- 禁止另起旁路工具编排；须走 Manifest / Projection / Grant / Evidence。
- 源码树可暂时共享 Desktop Main 切片（构建嵌入），但属技术债，须迁出 shared package（见 `22`）。

### 2.2 `packages/protocol`

客户端与云端之间，以及客户端内部共享契约。

第一阶段对象：

```text
LocalAccessLevel
CapabilityManifest
RuntimeProjection
ClientToolCall
ClientToolResult
PermissionGrant
Evidence
AuditEvent
ClientSessionState
ClientBootstrap
LocaleCode
LocalizedText
```

这个包是工程的第一优先级。Desktop renderer、Desktop main、CLI/TUI、共享 Runtime packages 都应围绕这些对象对齐。

### 2.3 `packages/i18n`

客户端国际化边界。

职责：

- locale 解析。
- 中英文资源。
- 术语边界。
- capability name / description 本地化。
- UI 和 task thread 的共享文案。

原则：

```text
中文优先表达业务语义。
英文保留工程对象语义。
locale 必须来自 session，不由组件各自猜测。
```

### 2.4 `packages/chat-kernel`

对话内核，不绑定具体 UI。

职责：

- Chat Stream client。
- message model。
- quote / attachment / artifact model。
- thinking / tool event model。
- SSE event 解析。

这个包可以吸收现有 Web `module-ai-chat-flow` 的协议经验，但不能直接复制 Web 页面。

### 2.5 `packages/task-thread`

任务线程状态和渲染编排。

职责：

- thread event reducer。
- user / assistant / tool / review / evidence / artifact 的线程事件模型。
- Composer 状态。
- Review card 状态。
- 线程恢复和本地缓存策略。
- 从 `ClientSessionState + CapabilityManifest` 派生任务线程。
- 按 session locale 生成任务文案。

这个包让 UI 不直接理解底层工具协议，而是消费运行态事件。

Codex.app 参考下，`task-thread` 是客户端最核心的产品内核：

- 线程事件是运行态账本。
- Tool call、Review、Evidence、Artifact 都必须进入线程。
- 权限中心、能力中心、诊断中心默认通过线程事件或按需抽屉进入，不做首屏常驻管理页。

### 2.6 `packages/ui`

客户端基础 UI 组件。

职责：

- Button、Input、Popover、Sheet。
- Card、AttachmentCard、ToolCallCard、ReviewCard。
- StatusBadge、AccessLevelSelect。
- 设计 token。
- 中英文基础控件文案。

原则：

```text
UI 组件可以复用品牌和基础体验。
业务运行态语义不要下沉到纯 UI 组件里。
```

### 2.7 `crates/cu-proxy-core`

本地能力核心。

第一阶段只做最小本地核心：

- health capability。
- local session state。
- permission / evidence 只保留协议入口，真实任务到达前不在 UI 中伪造执行事件。

后续再进入：

- Manifest registry。
- Permission enforcement。
- Tool router。
- MCP manager。
- Plugin host。
- Evidence collector。
- Local memory store。
- Audit ledger。
- Cloud Runtime session。

原则：

```text
Rust Core 只在本地能力真的需要高信任执行时变厚。
不要为了架构完整感提前堆实现。
```

---

## 三、运行时边界

第一阶段运行时：

```text
Renderer
  → preload typed API
    → Electron main
      → local core adapter
        → Rust cu-proxy-core health stub
```

后续混合运行时（认知可云可本地，能力始终本地）：

```text
模型 / Provider Runtime
  → Desktop / TUI host
    → Runtime Projection
      → Review card
        → PermissionGrant
          → Local Capability Runtime
            → Evidence
```

边界规则：

- 模型不直接访问本地端口，也不绕过授权执行。
- Electron Renderer 只展示和请求，不执行高权限能力。
- Electron Main 只做桌面胶水和安全 IPC 转发。
- 本地工具必须进入 Manifest / Projection / ToolCall / Evidence 主链路。

---

## 四、第一阶段实现范围

### 4.1 必须有

- Monorepo 初始化。
- Electron desktop app。
- React task thread。
- Sidebar：New task、Search、Plugins、Automations、Pinned、Projects、Settings。
- Composer：`+`、local access level、model selector、input、send。
- Review card contract flow。
- Tool call card contract flow。
- Evidence summary contract flow。
- `bootstrap:get` IPC。
- `zh-CN` / `en-US` i18n scaffold。
- Electron main capability registry，来源于 `capabilities/*.json`。
- Electron main project index，来源于 workspace/package/git status。
- Electron main local session store。
- `packages/protocol` 类型。
- `crates/cu-proxy-core` health stub。

### 4.2 暂缓

- 真实文件读写。
- 真实 MCP lifecycle。
- Plugin 安装和签名。
- 云端 client gateway。
- 个人经验存储。
- 任意命令执行。
- 完整 SDK。

### 4.3 验收标准

第一阶段完成时，应该能在本地看到一个可运行客户端：

```text
用户输入任务
  → 线程中出现 assistant work summary
    → 出现 local health tool call card
      → 出现 Review card
        → 用户确认
          → Rust health stub 返回 result
            → 线程展示 Evidence summary
```

即使没有真实云端 Agent，也要先把交互和契约骨架跑通。

---

## 五、禁止事项

第一阶段与持续治理禁止：

- Renderer 直接调用 `fs`。
- Renderer 直接调用 `child_process`。
- IPC 传任意命令字符串。
- 用宿主 UI 状态充当权限事实源。
- 把 Plugin / MCP 做成 UI 内部状态。
- 把权限授权只存在前端 store。
- 把本地个人经验塞进普通 chat context。
- 把客户端描述成本地 Agent。
- **让 CLI 运行时依赖 Desktop 客户端已安装。**
- **混淆 `@peer-agent/tui`（构建）与 `@peer-agent/cli`（npm 安装）。**

这些禁止项不是洁癖，而是为了防止工程偏离 Runtime 编排、能力声明、本地授权、Evidence 闭环与双宿主独立发布的设计原则。
