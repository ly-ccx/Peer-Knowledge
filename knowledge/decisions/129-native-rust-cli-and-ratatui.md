# ADR 129：CLI 全面迁移到原生 Rust 与 Ratatui

创建时间：2026-11-14
最后更新：2026-11-14
状态：Accepted（2026-11-14 用户接受评审稿 116–118 并授权全面实施；本文正式编号 129；实现与验收另记）
级别：A
依赖：[ADR 130](130-bounded-cli-memory-and-transcript.md)、[ADR 131](131-native-cli-contract-storage-and-recovery.md)
执行方案：[原生 CLI 迁移方案](../../design/product/native-rust-cli-migration-plan.md)

## 1. 问题与证据边界

用户报告对话越长，CLI 内存占用越大，所附活动监视器截图显示 `peer` 约 8.27 GB、另有 `bun` 约 1.00 GB。截图未提供构建版本、会话、运行时长、父子进程关系或 heap / native allocation trace，不能相加成同一进程树消耗，也不能把全部增长归因于 OpenTUI。

代码审计基线为 Peer-Agent `f00c955359a24b3e28afcbc947d862fd074376f7`。当前是 Bun 编译 CLI，OpenTUI 0.4.3 + React 19.2.7；运行时、Provider、权限、项目代理、会话和上下文主要为 TypeScript / JavaScript。`apps/tui/src/conversation-render-window.ts` 的 latest 路径停用常规预算，改用配置为 2,000 消息 / 2,000,000 估算字符的应急策略，窗口还会对齐回合边界；这些数字不是严格分配上限，也不限制 Controller 的全部驻留历史、单消息体积、原生分配或进程树。现有性能报告主要证明局部耗时改善，不能作为本次长时间内存验收。

用户要求全面使用原生 Rust 构建 CLI。因此本次是 CLI 产品执行栈迁移，而非只换终端渲染器。

## 2. 决策

1. 最终 `peer` 的命令分流、交互终端、无头执行、ACP adapter、模型请求、Runtime Pipeline、本地能力、权限、Evidence、项目代理、存储与恢复均使用 Rust。
2. 终端表达使用 Ratatui，首选 Crossterm backend；业务状态采用显式 reducer / actor，异步 I/O 使用 Tokio。Ratatui 只承载表达，不拥有授权或执行真值。
3. 最终 CLI 内置运行链不依赖 Bun、Node、React、OpenTUI、Electron，也不通过常驻 JavaScript sidecar 承载旧 Runtime。外部用户配置的 MCP / Hook / 工具程序可以有自身运行时，必须通过原有能力链管理和单独核算资源。
4. 保留 `peer-credential-helper` 独立原生进程及既有凭证协议。Rust CLI 不直接读 Keychain / Vault，不把 Helper 合并进 UI。
5. 继续 monorepo、根 VERSION、同 tag 双宿主发布、共享数据根与 npm 安装面。npm 的薄安装器 / launcher 可保留 JavaScript；直接下载的 `peer` 必须在无 Node / Bun / Desktop 环境独立运行。
6. 本轮目标是 CLI。Desktop UI、Gateway、公开 TypeScript Runtime SDK 不借迁移被撤销或全面重写。Desktop 后续是否消费原生 Runtime 需另立明确范围的 A 级决策。
7. 迁移采用隔离候选 + 可验收纵向切片。旧版 CLI 维持既有入口，原生候选通过显式二进制运行；不会在已产生副作用后自动切回旧引擎、重放任务或双写执行。

## 3. 共享的含义与既有条款修订

跨语言后，不能继续声称 Desktop 与 CLI 直接运行同一份 TypeScript Implementation。共享目标调整为：同一工程契约、同一上下文资源、同一 schema 与兼容规则、同一份 conformance fixtures、同一个任务的本地事实与执行所有者。

本 ADR 自 2026-11-14 接受起局部取代下列技术实现条款；原生候选进入生产仍须通过兼容、恢复与发布门禁：

| 既有文件 / 条款 | 拟替换内容 | 继续有效 |
|---|---|---|
| 架构 `01-project-structure.md` §2.1b；`22-tui-desktop-shared-runtime-and-host-governance.md` §3、§5.1、§5.4、§13 | CLI 不再使用 OpenTUI / Bun 及直接链接 Node Runtime；允许 Rust Adapter 实现已治理的内核 Interface | 一等 CLI、统一能力链、宿主分工、无 Desktop 安装依赖 |
| ADR 48 Decision 4、6、8 的构建实现 | `apps/tui` 从实际构建面变为迁移期旧实现；Cargo 产出原生 CLI；版本脚本纳入 Cargo 元数据 | 安装包 `@peer-agent/cli`、版本列车、平台归档与 Helper |
| ADR 55 §2.1–2.3；ADR 57 §3.1、§3.3 的唯一 TS Implementation 要求 | 允许 Rust Implementation；共享算法规范、资源正文、版本和跨语言等价测试取代直接 TS 导入 | Context Source 顺序 / trust / hash、canonical history 结构与不完整工具处理 |
| `tui-and-hook-design-standard.md` 的 OpenTUI 技术描述 | Ratatui 表达 Adapter | Hook / Skill / MCP 的统一能力链 |
| 代码仓 AGENTS 的 React ModelPicker 与 SVG 适用面 | 终端通过一个 Rust ModelPicker Adapter 复用相同选择契约、分组和键盘行为；终端使用文字动作标签，无字符图标；Desktop 仍用共享 React ModelPicker / SVG | 不建立另一份模型 catalog / eligibility / 权限事实，不把显示名当身份 |

“不得新增第二套 Agent loop 语义”继续生效。Rust 与 TS 的两份 Implementation 只在同一可执行契约下并存，差异必须由 fixture / ADR 解释；不能各自增加决策、完成或恢复规则。此转换有持续维护成本，不能仅凭同名 struct 宣称一致。

## 4. Module 与依赖

拟采用以下深 Module；仅在 Interface 可独立验证时建立 crate，不能按文件名机械拆 crate：

| Module / 拟位置 | Interface / 所有权 | 依赖约束 |
|---|---|---|
| `crates/peer-protocol` | 版本化事实、命令、错误、资源引用、权限与 Evidence 对象 | 不依赖 UI、模型 SDK 或 OS 执行 |
| `crates/peer-runtime` | 回合、投影、权限判定、执行结算、Context / history / compaction、取消域 | 通过 Provider / Store / Clock / Credential ports 获取能力 |
| `crates/peer-store` | 既有 JSON / JSONL / SQLite、revision、分页读取、原子提交、恢复 | 不引入另一个数据真源 |
| `crates/peer-providers` | model wire encoders、文件 / Shell / Web / MCP / Skill / Hook Adapter | 执行入口必须校验 Runtime 准入与 grant |
| `crates/peer-project-agent` | 项目租约、输入队列、调度、目标、记忆、核验、签收和送达 | 使用 Runtime / Store；不依赖终端 |
| `crates/peer-tui` | 纯 View、输入 reducer、可见区域投影、草稿 / 焦点 / 阅读锚点 | 不依赖具体 Provider / Store；不持 secret 或签发 grant |
| `crates/peer-cli` | `peer` 可执行文件、argv、TUI / exec / ACP 装配、退出与更新 | 组合根，不承载业务神模块 |

默认一个前台 CLI 进程，内部通过类型和依赖方向隔离 UI 与 Host；这不是 OS 安全沙箱。凭证 Helper 和实际工具子进程保持各自进程边界。首期不引入常驻 daemon、公开本地监听端口、Node FFI 或 Electron IPC。

所有能力仍经过：

```text
Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
```

## 5. 事件、终端与退出

- 唯一终端输入所有者、唯一终端写出所有者。Crossterm EventStream 与 poll/read 二选一，禁止混读 stdin；ACP 与 exec 不初始化终端。
- 视图只由结构化事实更新；输入、批准和取消是命令，不在 reducer 中凭点击制造权限或成功。
- Tokio 任务有明确 owner、取消域和 join；禁止无限队列、无限 spawn、未登记后台任务。
- 文本增量可以在展示投影中合并，不能丢失权限、工具结算、Evidence 或持久化确认。关键控制与展示背压隔离，详见 ADR 130。
- Ctrl-C / Escape、SIGTERM、stdin EOF、broken pipe、panic 与正常退出分别覆盖。先关闭新任务准入，按既有生命周期取消 / 结算，持久化已确认事实，再释放租约和终端。
- 有限清理截止不表示“副作用已撤销”。无法确认的工具保留未知效果与恢复阻断，重启不得自动重放。
- raw mode、alternate screen、鼠标捕获、bracketed paste、光标和标题恢复集中在终端 guard；panic hook 尽力恢复，SIGKILL 无法保证清理，靠下次启动恢复事实。

## 6. 安全边界

Rust 提供更强的内存安全与资源所有权工具，但不保证无泄漏、无无限缓存或工具天然安全。权限语义沿 ADR 49 / 92 / 101，不因迁移恢复硬路径沙箱，不把 Full 扩大成忽略 role、mode、Goal、deny 或租约。

不信任的模型文本、文件名和工具输出先经终端文本安全编码；不能将 ESC / OSC / DCS、剪贴板序列或伪造的审批提示原样交给终端。模型参数、MCP 返回和日志均有大小限制；敏感 token 不进 argv、环境日志或性能 trace。自有纯逻辑默认禁止 unsafe；OS / C 依赖另作受控审计，不声称整个依赖树没有 unsafe。

## 7. 备选与取舍

| 方案 | 结论 |
|---|---|
| 继续修 OpenTUI | 可作为有证据的临时止损；不满足用户指定的技术终态 |
| Rust UI + 长期 TS sidecar | 不采用；仍保留双运行时驻留、重复历史与双生命周期 |
| 一次删除旧 CLI 后全量重写 | 不采用；恢复、权限和 Provider 验收没有安全过渡 |
| 先重写整个 Desktop 与公开 SDK | 不纳入；扩大本次 CLI 目标和发布面 |
| 原生 CLI 候选逐段完成 + 跨语言契约一致性门禁 | 推荐；承担一段双实现维护成本，换取按真实链路验收和可恢复切换 |

## 8. 验收与接受条件

接受本 ADR 只批准上述设计，不代表内存问题已解决。生产切换必须同时通过 ADR 130 的内存 / 响应性门禁、ADR 131 的协议 / 数据 / 恢复门禁、完整 CLI 功能矩阵和双宿主 release gate。必须在没有 Bun / Node / Desktop 的环境运行直接下载的原生二进制，核对进程树与依赖。

本次只做资料与内容审阅，没有运行原生实现、复现用户 8.27 GB 现场或修改个人会话。切换日期、最终 MSRV、依赖精确版本与性能数值均不能由本文状态冒充验证结果。

## 9. 官方依据（核对于 2026-11-14）

Ratatui 是 immediate-mode 表达库，应用自行组织事件与渲染循环，因此“换库”并不自动提供状态、队列或历史的内存上限。[Ratatui Rendering](https://ratatui.rs/concepts/rendering/)

reducer / Model–Update–View 选型参考 [Ratatui TEA](https://ratatui.rs/concepts/application-patterns/the-elm-architecture/)；输入所有权约束见 [Crossterm event](https://docs.rs/crossterm/latest/crossterm/event/index.html)。

## 修订记录

- 2026-11-14：新增原生 CLI 技术终态、跨语言共享边界及拟局部取代清单。旧 ADR 尚未被本 Proposed 记录覆盖；无代码或发布行为。

## 接受与编号校正（2026-11-14）

用户明确接受三份原生 CLI 迁移 ADR 并要求先完成 P0/P1、自测后持续推进，最终无 Bun/Node sidecar。评审稿来自落后的知识 checkout，误用主线已有编号；核对全部 origin 分支后，将原 116 / 117 / 118 按同一内容分别登记为 129 / 130 / 131。既有同号其他 ADR 未被覆盖。接受不等于实现、性能、恢复或发布验收。
