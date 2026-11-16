# ADR 133：全端统一 Rust Core 与双宿主融合终局架构

创建时间：2026-11-16
最后更新：2026-11-16（补充定案方案 B：彻底退出嵌入式 JS/TS Runtime SDK，不再维护“JS 外壳包一层调 Rust”的 npm 运行库；外部集成收敛至 `peer acp` / `peer exec` / `@peer-agent/protocol` / Rust crate）
状态：Accepted（2026-11-16 用户确定终局架构标准：后续以 Rust 为核心构建唯一运行时内核，桌面端复用同一套体系并叠加桌面专属效果；外部不另留 JS 薄壳嵌入 SDK；代码实施与发布验收另记）
级别：A（全产品运行时终局架构、Rust 单核收敛、Desktop/CLI 双宿主边界、公开 TS SDK 过渡与退场策略、在途方案冲突收口）
关联：
- [Coding Agent 工程总纲](../architecture/00-engineering-philosophy.md)
- [架构治理基线](../architecture/20-architecture-governance.md)
- [工程结构设计](../architecture/01-project-structure.md)
- [TUI 与 Desktop 共享运行时与宿主治理](../architecture/22-tui-desktop-shared-runtime-and-host-governance.md)
- [Electron Main Process 架构治理方案](../architecture/electron-main-process-governance.md)
- [Runtime SDK 分层边界规范](../specifications/runtime-sdk-boundary-architecture.md)
- [Hook / Runtime SDK / TUI 三阶段路线图](../playbook/tui-hook-sdk-roadmap.md)
- [ADR 54：开放 Runtime 公开包与发布策略](54-open-runtime-public-packages-and-release-policy.md)
- [ADR 48-cli：CLI 与 Desktop 同仓一等发布](48-cli-first-class-release.md)
- [ADR 65：CLI 无头发起（`peer exec`）](65-cli-headless-exec.md)
- [ADR 74：部署面与本机存储策略](74-deployment-surfaces-and-local-storage.md)
- [ADR 76：Peer 作为 ACP Agent](76-peer-acp-agent.md)
- 在途同仓参考：`128-local-runtime-isolation-and-bounded-query-contract.md`（`origin/codex/local-runtime-isolation-architecture` / PR #132，Proposed）、`129–132`（`origin/codex/native-rust-cli` / PR #133，Accepted）

---

## 1. 背景与待解冲突

经 2026-11-16 对 `Peer-Knowledge`（主线、在途 PR #132/#133/#134 与未并入分支）及 `Peer-Agent`（`PeerAgent/dev/0.1.0` 与 `codex/native-rust-cli` / PR #327）全量审计，现有设计之间存在三类结构性撕裂：

1. **双技术栈事实割裂与文档未同步**：
   - 早先体系（`ADR 54`、`runtime-sdk-boundary-architecture.md`、`tui-hook-sdk-roadmap.md`、`22-tui-desktop-shared-runtime-and-host-governance.md`）约定 Desktop、CLI/TUI 与外部宿主共用同一份 TypeScript `@peer-agent/runtime-sdk` 实现。
   - 2026-11-14 用户接受原生 Rust CLI（`ADR 129–131`）后，CLI 迁往 Rust（`crates/peer-*`），而 `ADR 129 §2.6` 暂将 Desktop 与公开 `@peer-agent/runtime-sdk` 留在 TS；核心 SDK 文档群尚未同步修订，且 Rust `crates/peer-runtime` 目前直连 `peer-store` / `reqwest` / `rmcp`（`publish = false`），尚无清晰宿主中立 SDK/Host Port 边界，亦尚未实现 `Skill/Plugin/Hook` 生命周期。
2. **在途方案相互冲突与过渡期三连重写风险**：
   - `PR #132`（`ADR 128` 局部运行时隔离，Proposed）旨在解决 Electron 主线程及全量查询卡顿（`RI-00` 基线），但其原文一方面包含与 `ADR 129` 互斥的“TUI 启动 Bun `--internal-runtime-host-v1` / `--internal-query-host-v1` sidecar”条款及“不选 Rust”结论，另一方面另起 15 个模块契约（`M00–M14`），未明确与 `@peer-agent/runtime-sdk` 既有 4 个公开导出（`createRuntimeSdk`、`createRuntimePipeline`、`createRuntimeSessionController`、`createRuntimeGoalController`）之间的替代或挂载关系。
   - 与此同时，TS 代码主线本就留有半迁移双轨：`@peer-agent/runtime-sdk` 导出的 `createRuntimeGoalController` 在产品源码中零调用，实际运行态走私有 `runtime-node` 的 `createGoalRunner()`；Desktop 的 `runtime-pipeline-adapter.mjs` 仍抑制 `message.completed` 与 `runtime.error` 并由外层 `agent-loop` 与 `webContents` 持有终态。
   - 若先花精力在 TS 上把 `createGoalRunner` 回填进旧 `createRuntimeGoalController`、再在 Electron 里按 `M00–M14` 用 TS 重写一遍 `utilityProcess` 内核、最后再切向 Rust 内核，将产生连续三轮大重构。

按照 `ADR 129 §2.6` 预留的升级条件（“Desktop 后续是否消费原生 Runtime 需另立明确范围的 A 级决策”），本文正式确立**全 Peer 统一 Rust Core 的终局架构标准**，一次对齐终局方向、在途方案收口与过渡期止损边界。

---

## 2. 核心决策：以 Rust Core 为唯一核心，双宿主复用 + 桌面扩展

### 2.1 三层唯一架构定型

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ 表达与宿主扩展层（两套入口共享同一个 Rust Core，各自只管 UI 与宿主独占能力） │
├─────────────────────────────────┬───────────────────────────────────────┤
│ CLI / TUI / Headless / ACP      │ Desktop（Electron + React Frost 2.0） │
│ • peer-tui (Ratatui)            │ • 窗口 / Tray / Quick Chat / 快捷键   │
│ • peer-cli (argv / exec / ACP)  │ • ResourceWindow / OpenUI / 动效      │
│ • 直接装配同一 Rust Core        │ • 桌面专属 Host Capability Provider    │
│                                 │   (L1 Embedded Browser / 桌面交互等)  │
└────────────────┬────────────────┴───────────────────┬───────────────────┘
                 │ 进程内 Trait / Port                 │ 受管隔离进程 IPC / 本地协议
                 ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 唯一运行时核心层：Peer Rust Core（crates/peer-*）                        │
│ • 会话 / 回合 / 取消域 / Goal 与协调调度状态机                           │
│ • 唯一能力链：Provider → Manifest → Projection → ToolCall → Grant → Evidence │
│ • System Context / Canonical History / Compaction / Budget & Ledger      │
│ • Provider Wire & Recovery / MCP / Skill / Hook 生命周期               │
│ • 唯一本地数据与锁真源（~/.peer-agent 语义 + Credential Helper v1）       │
└─────────────────────────────────────────────────────────────────────────┘
```

1. **Rust 是全产品唯一演进的 Runtime 内核**：
   - `crates/peer-protocol`、`crates/peer-runtime`、`crates/peer-store`、`crates/peer-credential-helper` 及后续按内聚边界拆分的原生 crate 共同构成唯一底层内核；
   - 长期只保留这一份真实执行语义，不再以任何长期 JS/TS runtime sidecar 承载产品业务主线。
2. **Desktop 是“复用同一 Rust Core + 桌面专属效果/能力”的轻量宿主**：
   - Electron（Main / Preload / Renderer）负责桌面交互壳层、视觉表现（Frost 2.0、多窗口、`NativeResourceWindow`、Quick Chat Popover、OpenUI 渲染宿、OTA 更新、托盘与系统快捷键）及少数桌面独占器官（如内置 `<webview>` `browser_*`、桌面截图/交互结果宿主等）；
   - 这些桌面独占能力作为 **Host Capability Provider** 通过受控协议向 Rust Core 声明 Manifest、受 Runtime Projection 裁剪并交回 PermissionGrant 与 Evidence；
   - Desktop 不再自建或长期维护第二套 Agent Loop、第二套 GoalRunner、第二套模型请求恢复或第二套本地业务 Store 逻辑。
3. **跨阶段不变的唯一主链**：
   任何入口与任何扩展能力（Desktop、CLI、headless `peer exec`、ACP、Automation、OpenUI、Hook）必须经过同一链路，禁止旁路：

   ```text
   Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
   ```

---

### 2.2 对 Rust Core 的强制模块化与扩展要求（对原 `PR #133` / `PR #327` 的升级约束）

原 `PR #327` 的 `crates/peer-runtime` 目前仅面向原生 CLI 垂直落地，后续升级为全端核心前必须补齐以下结构性边界：

1. **拆分宿主中立 Core/Host Interface**：
   - 在 Rust workspace 内清晰隔离核心编排（Turn / Session / Goal / Projection / Permission / Evidence）与具体存储 / 传输 / 终端 UI 适配器；
   - 暴露稳定、可由多宿主（`peer-tui`/`peer-cli` 直接装配 + Electron Host 跨进程接入）共同消费的命令入口、结构化事件流、审批 Port、Capability Provider 注册表与受控只读查询投影；
   - 禁止继续让 `crates/peer-runtime` 以仅耦合单个终端实现的方式无限膨胀。
2. **补齐 Rust Hook 生命周期与 Skill/Plugin 对齐**：
   - 以 [runtime-sdk-boundary-architecture.md §0A.2–0A.3](../specifications/runtime-sdk-boundary-architecture.md#L41-L56) 与 [tui-hook-sdk-roadmap.md](../playbook/tui-hook-sdk-roadmap.md) 定义的语义为准：支持 `<userDataPath>/hooks/hooks.json` 与工作区 `.peer/hooks.json`，实现 `PreToolUse` / `PostToolUse`（`allow` / `ask` / `deny`）、高风险红线不可覆盖、超时/异常 fail-closed、以及 Hook 审计入同一 Evidence 账本；
   - 在补齐 Hook 与对应能力前，不得声称 Rust Core 已具备取代 Desktop TS 运行时的完整对等条件。
3. **跨语言单一契约事实源留在 `packages/protocol`**：
   - 延续 ADR 131（`PR #133` `131-native-cli-contract-storage-and-recovery.md`）规则：过渡期及 Rust Core ↔ Electron JS 桥接期所需的全部消息形状、错误码、权限与 Evidence 契约及 conformance fixtures 仍在 `packages/protocol` 统一定义与生成校验，禁止 Rust 与 Electron 各自手写第二套协议副本。

---

### 2.3 Desktop 接入 Rust Core 与解决主线程隔离（吸纳 `PR #132` 的真实价值）

1. **以“独立原生内核进程”一步到位实现进程隔离**：
   - Desktop 启动并监管独立的本机 Rust Core 进程（与 CLI 共享同一核心能力与锁/租约语义），Electron Main 仅通过最小受控本地通道发送用户意图/审批命令、订阅有界展示投影，并承载桌面端 Host Capability Provider 回调；
   - 重查询、SQLite 读取、会话压缩、模型流式恢复与工作调度天然运行在 Rust Core 进程内，**不在 Electron UI / Main 线程阻塞执行**，从而直接达成 `PR #132`（`RI-00`）期望消除主线程卡顿与全量内存驻留的架构目标；
   - 存储仍遵循 [ADR 74](74-deployment-surfaces-and-local-storage.md) 与 ADR 131（`131-native-cli-contract-storage-and-recovery.md`）的单一 `~/.peer-agent` 数据根与 `host.lease` / 目录锁语义，不允许为 Electron 与 CLI 各自建立冲突的数据源。
2. **明确本 ADR 与后续接入子规范的分工**：
   - 本 ADR 正式锁定“Desktop 接入唯一 Rust Core”的终局架构决定；
   - 具体进程拉起与看门狗、Electron ↔ Rust 传输协议版本握手、Desktop 专属 Host Capability 回调授权（延续 `ADR 128` 提出的防重放/绑定准入校验思想）及 Windows/macOS 打包签名，应在实施前另以聚焦实施规范（或独立实施 ADR）冻结并逐片验证。

---

### 2.4 过渡期 TypeScript Runtime / `@peer-agent/runtime-sdk` 止损策略

为消除 A2（`M00–M14` 替代旧 SDK）与 A3（把旧 `goal-runner`/`agent-loop` 补回 `runtime-sdk` 4 个接口）同时推进导致的三重返工，**过渡期统一执行以下收敛规则**：

1. **冻结 TS 双轨扩张，不再反向回填旧接口**：
   - `@peer-agent/runtime-sdk` 现有的 4 个导出（`createRuntimeSdk`、`createRuntimePipeline`、`createRuntimeSessionController`、`createRuntimeGoalController`）以及 `@peer-agent/runtime-node` 的 `createGoalRunner`、`apps/desktop` 的 `agent-loop` / `runtime-pipeline-adapter.mjs`，统一定位为**过渡期冻结维持的遗留 TS 载体**；
   - **不再投入重构精力**把 `createGoalRunner` 迁回 `createRuntimeGoalController`，也不再在 TS 侧新建取代它们的第三套完整 TS 运行时内核；Desktop 未切上 Rust Core 前，仅在现有 Seam 上做明确边界的缺陷修复与卡顿止损。
2. **彻底退出嵌入式 JS/TS Runtime SDK（收窄并闭环 `ADR 54` 退场条件）**：
   - 鉴于 `@peer-agent/runtime-core` 与 `@peer-agent/runtime-sdk` 此前已随 `0.1.0-rc.*` 列车发布至 npm，不得在无交代的情况下悄悄断更；
   - 过渡期内二者仅作遗留兼容包随根 `VERSION` 维护（不再新增核心编排能力）；进入 `1.0.0` 前按 [ADR 54](54-open-runtime-public-packages-and-release-policy.md) 回退条款完成 deprecation 公告与退场，彻底改为 internal/归档，**不另外发布或长期维护“外面包一层 JS 壳 / N-API 调用 Rust Core”的嵌入式 npm Runtime SDK**；
   - Desktop（Electron）与 Rust Core 的本地进程通信是桌面端私有宿主桥接细节，不作为通用公开 JS SDK 对外承诺；
   - 退场后的对外公开入口彻底收敛干净：
     - **`@peer-agent/cli`**：长期公开，作为 `peer` / `peer-credential-helper` 原生二进制安装器；
     - **`@peer-agent/protocol`**：长期公开，作为跨语言契约、schema 与 conformance fixtures 的唯一事实源；
     - **外部程序化嵌入 / 自动化接入**：统一经由标准协议 **`peer acp`**（JSON-RPC 2.0，见 [ADR 76](76-peer-acp-agent.md)）或无头命令 **`peer exec --output-format json`**（[ADR 65](65-cli-headless-exec.md)）驱动原生二进制，或在 Rust 生态内直接对接原生 core crate。

---

## 3. 对在途方案与既有文档的替代与修订约束

| 对象 / 文档 / 在途 PR | 状态 / 处置决定 | 明确取代或约束内容 |
|---|---|---|
| **ADR 54**（`54-open-runtime-public-packages-and-release-policy.md`） | **部分取代 / 触发退场（Accepted 更新）** | 按其“回退条件”正式触发 `@peer-agent/runtime-core` / `@peer-agent/runtime-sdk` 退场路线（`1.0.0` 前完成 deprecation，且**不另立 JS 薄壳 / N-API 运行库替代品**）；`@peer-agent/protocol` 与 `@peer-agent/cli` 保持长期一等公开，外部程序化集成归口 `peer acp` / `peer exec` / Rust crate |
| **ADR 129 §2.6**（`PR #133`，Accepted） | **依授权升级覆盖** | `ADR 129 §2.6`“Desktop 后续是否消费原生 Runtime 需另立 A 级决策”由本 ADR 正式定案为**消费同一个 Rust Core**，结束长期双语言核心分裂假设 |
| **`PR #132`（`ADR 128` + `specifications/runtime-isolation/*`，Proposed）** | **合并前提强约束** | 1) **必须删除** `local-agent-system-blueprint.md` 与 `06-host-and-platform.md` 中“TUI 启动 Bun `--internal-runtime-host-v1` / `--internal-query-host-v1` sidecar”全部条款；<br>2) **修订** `ADR 128 §10`“不选 Rust”的表述，限定其仅针对 Electron 当前 TS 过渡期卡顿止损；<br>3) **禁止**在 TS 侧以完整的 15 模块 `M00–M14` 再重写一遍待废弃的 TS 核心：`M00–M14` 职责边界、有界查询预算与一次性调用授权不变量（如 `RI-00` 成果）作为 **Desktop Shell ↔ Rust Core 隔离接口契约** 继承，TS 侧仅保留必要的阻塞止损 |
| **`PR #133`（`ADR 129–132`）& `Peer-Agent` `PR #327`** | **后续门禁补充** | 补齐 Hook 生命周期与宿主中立 Core Interface，按多宿主（CLI + 未来 Electron Host）而非单二进制私有内部库组织 `crates/peer-runtime` 边界 |
| **`runtime-sdk-boundary-architecture.md`** | **部分取代 / 语义继承** | 原 TS 4 层物理包假设不再作为终局；文档定义的 `Capability Provider → Manifest → Projection → Grant → Evidence` 与 **Hook Port 职责/顺序/fail-closed 不变量** 由 Rust Core 完整继承并作为等价验收基准 |
| **`tui-hook-sdk-roadmap.md`** | **历史路线归档升级** | 阶段一～三（Hook → TS SDK → OpenTUI 瘦客户端）保留为 2026-07 历史事实记录；后续终局路线以本 ADR 为准（Rust Core + 双宿主适配） |
| **`22-tui-desktop-shared-runtime-and-host-governance.md`、`01-project-structure.md`、`electron-main-process-governance.md`** | **局部修订** | 将终态“共享核心”锚点从 TS `packages/runtime-*`（及早期 `crates/cu-proxy-core` 占桩）统一指向 `crates/peer-*` Rust Core；Electron Main 终态收窄为桌面 UI 壳 + 安全 IPC + Desktop Host Capability Providers，冻结 TS `Goal` 双轨改造 |
| **`48-cli` / `65` / `74` / `76` / `06-version-management.md`** | **口径对齐** | 延续各自核心契约（CLI 无 Desktop 独立安装、`~/.peer-agent` 共享数据根、本机执行与 Evidence 不上云、ACP 与版本列车），并将文中涉及的底层共享“Runtime”语境从纯 JS/TS 同步对齐至 Rust Core |

---

## 4. 不变的硬红线（复核）

1. **权限与安全底线不因换核退化**：沿用 ADR 49 / 92 / 101，Model / Project Instructions / OpenUI / Renderer / `allow` Hook 永远不能越过拒绝规则、角色裁剪或高风险写红线。
2. **CLI 独立发布与零 Desktop 依赖不变**：按 [ADR 48-cli](48-cli-first-class-release.md) 与 ADR 129（`PR #133` `129-native-rust-cli-and-ratatui.md`），独立安装和运行 `peer` 绝不依赖 Electron 或 Desktop 安装包；同样，Desktop 运行所消费的 Rust Core 必须随桌面发布包完整自包含携带或按版本锁定绑定，不能要求用户另装外部运行环境。
3. **单一用户数据根与可恢复性不变**：`PEER_AGENT_HOME` / `PEER_USER_DATA_PATH` / `~/.peer-agent` 唯一真源与凭证进 `peer-credential-helper`（[ADR 0001](0001-cross-platform-credential-vault.md)）跨阶段保持不变。

---

## 5. 分阶段演进与验收要求（不混淆决策与验收）

本 ADR 页头为 `Accepted` **仅代表终局架构标准拍板，不代表工程实现或发布验收完成**。实际落地按以下阶段独立记账与验收：

1. **阶段 0（立即生效 — 止损与卡 PR 门禁）**：
   - `Peer-Agent` 与 `Peer-Knowledge` 按本文 §3 约束对齐在途 `PR #132` 与 `PR #133`/`PR #327`；停止 TS 侧冲突重写与死接口扩建。
2. **阶段 1（原生 Rust CLI 达标并夯实唯一核心底座）**：
   - 完成 `ADR 129–132` 的恢复、内存预算与发布门禁；
   - 在 Rust workspace 拆分可嵌入式 **Core Host / SDK 接口边界** 并补齐 **Hook / Skill / Plugin 完整闭环**。
3. **阶段 2（Desktop 接入 Rust Core 专题立项与渐进切换）**：
   - 针对 Desktop ↔ Rust Core 的独立进程管理、IPC/本地协议、Electron 专属 Host Capability Provider（`browser_*`、OpenUI 宿、资源窗协作）、崩溃重启恢复与 macOS 签名/公证另立实施规范；
   - 以“同一用户数据根与历史任务零丢失、Main 进程不再承载业务 Runtime 与重查询、两端行为通过同一套 `packages/protocol` conformance fixtures”作为切换门禁。
4. **阶段 3（TS 旧 Runtime 彻底退场收尾）**：
   - 完成 `@peer-agent/runtime-sdk` / `@peer-agent/runtime-core` npm 包的 deprecation 与退出公开队列，清理 `examples/external-host` 等纯 TS SDK 依赖示例并指引迁移到 `peer acp` / `peer exec` / 原生 Rust Core，不再维护双引擎或 JS 薄壳 Runtime SDK。
