# Appshots P0a 工程任务拆解（可建 issue）

创建时间：2026-07-30  
状态：**P0a 全部任务完成（T0–T11，见 §0；UI 手测项遗留）**  
产品依据：`design/product/appshots-window-context-capture.md`（P0a/P0b/P1 分期与验收标准）  
代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）  

## 0. 实现状态（2026-07-30 第三波，P0a 收口）

| 任务 | 状态 | 产物 | 偏差/备注 |
|---|---|---|---|
| T0 ADR | ✅ 完成 | `knowledge/decisions/59-appshots-capability-boundary.md`（四决策：只读边界/不暴露模型工具/artifact 落盘/日志红线） | 无 |
| T1 Spike | ✅ 完成 | 本文档 §3.1 五项实测结论 | S4 需用户配合两态实测，已完成 |
| T2 协议 | ✅ 完成 | `packages/protocol/src/appshot.ts`（AppshotPayload/AppshotResult/四类失败码），typecheck 绿 | 无 |
| T3 服务 | ✅ 完成 | `apps/desktop/electron/main/appshot-service.mjs` + `.test.mjs`（6/6 绿） | 原 3054ms 偏差已由 T3.1 消除 |
| T3.1 枚举优化 | ✅ 完成 | `defaultListWindows` 改 swiftc 预编译二进制 + 缓存复用 + 解释兜底；`warmup()` 启动预热（main.mjs 装配） | 热态枚举 0.03s（原 3.7s）；warmup 后同进程捕获 **382ms/373ms ≤1.5s 达标**。一次性 ~10s 为本机 EDR（com.alibaba.security.edr）对新二进制首次执行扫描，由启动 warmup 吸收；无 EDR 环境预计仅 swiftc 编译 ~3.9s 一次性 |
| T4 热键 | ✅ 完成 → **已回退占用** | 曾接入 `⌘⇧A` 全局热键；**2026-07-30 用户决策后解除占用**：`DEFAULT_SHORTCUTS`/`GLOBAL_ACTIONS` 不再含 `appshot`，main 不注册 `onAppshot`，启动时清理已持久化的 `shortcuts.appshot`。捕获入口保留设置页「测试捕获」+ IPC | shortcut-service 11/11 绿（含「不占用 CommandOrControl+Shift+A」断言） |
| T5 权限预检 | ✅ 完成 | `appshot-permission-preflight.mjs` + `.test.mjs`（7/7 绿）：读数 + ScreenCapture 深链三级回退 + i18n hint keys（含 restartFallback） | i18n 文案 key 已定义，实际 copy 待 T8 设置页一起进 packages/i18n |
| T6 投递路由 | ✅ 完成 | `appshot-delivery.mjs` + `.test.mjs`（6/6 绿）：最近活跃未归档/无则新建；用户侧附件消息（artifactRef 制 + 可选缩略图）；单次 append 不自动开跑 Agent | 缩略图生成（thumbnailDataUrl）暂未接线，待 T7 卡片渲染时定尺寸 |
| T7 卡片渲染 | ✅ 完成 | `ChatAttachment` 扩展 `artifactRef`+`appshot` 元数据（types.ts）；`AttachmentStrip` Appshot 分支（有缩略图走 image 预览；缺图 ⚠︎ 占位 +「图片不可用」，不伪装成功）；main.mjs 接线 nativeImage ≤480px 缩略图 | desktop tsc 绿；attachmentIntake 7/7 绿；渲染视觉待手测 |
| T8 设置页 | ✅ 完成 | `AppshotsPanel.tsx`（总开关→settings.appshots.enabled / 热键只读展示 / 权限状态+打开系统设置 / 测试捕获+失败码中英文案）；SettingsPage 注册 appshots 分区；preload.cjs+bootstrapPreloadApi+clientApi 三层补 appshot 三 IPC 契约；主进程加总开关 gate（code:'disabled'） | tsc 绿；改热键仍在「快捷键」分区（P1 再独立） |
| T9 反馈 | ✅ 完成 | `notifyAppshotOutcome`：复用 showTaskSystemNotification + openConversationFromTaskNotification；仅热键路径发通知（settings-test 走面板内联反馈）；成功可点击回流会话；四类失败分类文案；不强置前主窗口 | 通知不可用时静默降级 console |
| T10 红线 | ✅ 完成 | 全链路 grep 审计（service 9 + main.mjs 9 个日志点，违规模式零命中）+ `appshot-log-redline.test.mjs` 3/3 绿（敏感标题在成功+四失败路径日志/detail 不泄漏；整图 base64 不进会话消息） | 无 |
| T11 验收走查 | ✅ 完成 | 产品文档 §12.1 八项全勾（每项附自动化证据或代码审计依据）；四项 UI 待手测已明示 | 全仓 772 测试中 7 个失败经 git 基线对照确认为**存量失败**（llm-chat-service/Provider adapters），与 Appshots 无关 |

第三波回归：appshot 四模块（service 6 + delivery 6 + preflight 7 + redline 3）+ shortcut 14 + 相邻 quick-chat/tray = **58/58 全绿**；renderer attachmentIntake 7/7 绿；desktop `tsc --noEmit` 全绿。

**P0a 收口结论**：代码与自动化验收全部完成。发布前需一轮真机手测：热键端到端、通知点击回流、Appshot 卡片视觉、设置页交互（四项均已在产品文档 §12.1 标注）。

## 0.1 双 ⌘ 热键改造（2026-07-30 用户决策：暂缓，等开发者账号）

**决策**：目标默认热键从 `⌘⇧A` 改为**左右 ⌘ 同按**（对齐 ChatGPT）；但**暂缓开发、功能不外露**，待开发者账号申请完成后再实施。理由：双 ⌘ 依赖 NSEvent/CGEventTap 原生全局监听，需要 Accessibility 权限；无签名/公证的开发版在 TCC 授权体验上不可控（条目显示为 Electron、授权不稳定），等有开发者账号后以正式签名身份做权限申请更可靠。

**已完成的 spike 进度（中止前）**：

| 项 | 状态 | 证据 |
|---|---|---|
| Electron `globalShortcut` 路径 | ❌ 不可行（实测 accelerator conversion failure） | spike S3 |
| 原生监听方案设计 | ✅ 完成：NSEvent global monitor for `.flagsChanged` + 设备位掩码区分左 ⌘（`0x08`）/右 ⌘（`0x10`），500ms 去抖 | `peer_agent/scratch/appshot-spike/s6-doublecmd.swift` |
| 探针编译 | ✅ swiftc 编译通过（58KB 二进制） | `out/s6-doublecmd-bin` |
| 权限前置确认 | ✅ 实测无 Accessibility 授权时 `TRUSTED=false`，全局监听不产生事件——权限是硬前置 | 探针运行输出 |
| 左右 ⌘ 同按真机检测 | ⬜ **未做**（用户在授权步骤决策中止） | — |
| 主进程监听服务 + 单测 | ⬜ 未做（`monitor-impl` 任务随决策关闭） | — |

**恢复开发时的待办**（开发者账号就绪后）：

1. 完成左右 ⌘ 同按真机检测（复用 s6 探针，先授权 Accessibility）；
2. 实现主进程监听服务（预编译 helper 常驻子进程 + stdout 行协议，参照 winlist 二进制模式）+ 可注入单测；
3. 接线触发链路：双 ⌘ 触发捕获；无 Accessibility 权限时**明确提示并降级到设置页「测试捕获」**（不再默认占用 `⌘⇧A`）；
4. 设置页：热键展示改双 ⌘、增加 Accessibility 权限状态与引导；
5. 更新 ADR 59 权限面（Accessibility 从 P0b 提前到热键路径）；
6. 回归：appshot 全部单测 + shortcut-service 测试。

**当前生效状态（2026-07-30 更新）**：

- **无全局 Appshot 热键**：不注册、不占用 `⌘⇧A` 或其它 accelerator；
- 启动时会清除本地已持久化的 `shortcuts.appshot`，避免旧配置重新占用；
- 捕获入口：**设置 → Appshots → 测试捕获**（及 `appshot:capture` IPC）；
- 双 ⌘ 相关代码仅存在于 `scratch/appshot-spike/`，未进主分支运行路径。

技术底座事实（已实测确认）：

- Electron `^41.2.0`（`apps/desktop/package.json`）
- 仓库内**尚无** `desktopCapturer` 使用；OS 窗口捕获是全新链路
- 已有原生代码先例：`crates/peer-credential-helper`（Rust，说明仓库可接受原生辅助进程/模块）
- 主进程 `main.mjs` 已有 164 个 `ipcMain.handle` 注册点，新增 IPC 必须走既有注册模式

---

## 1. 架构定级与总原则

按 `peer_agent/AGENTS.md` 变更纪律：

- **定级：A-level**（新增本地能力 + 新系统权限 + Evidence 链路）。实现前需在本知识库补一份简短 ADR（见 T0）。
- Appshots P0a 是**用户手势触发**的能力（热键），不是模型可见工具；P0a **不做** Runtime Projection 暴露。若未来把 `appshot_capture` 开放给模型，必须重新走 Capability Provider → Manifest → Runtime Projection → PermissionGrant → Evidence 链，届时另立 issue。
- 大图落本地 artifact、仅回传摘要 + ref 的模式，**必须复用** `runtime-gateway/local-browser-control-provider.mjs` 已验证的 `artifactRef` 惯例（`local-browser-artifact://` 的同构做法），不得把图片 base64 塞进会话消息或日志。
- 渲染进程不得直接触碰捕获、权限、文件系统；一切经主进程 IPC（硬禁令）。

## 2. 代码挂载点（已实测锚定）

| 链路 | 现有文件 | Appshots 用法 |
|---|---|---|
| 全局热键 | `apps/desktop/electron/main/shortcut-service.mjs`（`DEFAULT_SHORTCUTS`、`GLOBAL_ACTIONS`、`RESERVED_SHORTCUTS`、校验+注册失败回滚；测试 `shortcut-service.test.mjs`） | 新增 `appshot` action 进 `GLOBAL_ACTIONS` |
| 主进程装配 | `apps/desktop/electron/main/main.mjs`（`onQuickChat: () => quickChatWindowController.toggle()` 的同构位置） | 新增 `onAppshot` 回调装配 appshot-service |
| 窗口/托盘先例 | `quick-chat-window.mjs`、`tray-controller.mjs`、`window-routing.mjs` | 反馈与回流参考，P0a 不新建窗口 |
| 截图+artifact 先例 | `runtime-gateway/local-browser-control-provider.mjs`（screenshot → bytes → artifactRef → 摘要回传） | Appshot 图片落盘与 ref 模式复用 |
| 权限预检先例 | `session-import/import-permission-preflight.mjs`（`x-apple.systempreferences` 深链 + 回退通用隐私页） | Screen Recording 预检/引导同构实现 |
| 会话存储 | `apps/desktop/electron/main/conversation-store.mjs` | 「最近活跃会话，无则新建」路由 |
| 附件进会话 | `apps/desktop/renderer/src/chat/state/attachmentIntake.ts`（+`.test.ts`）、`chat/state/types.ts`、`ChatSurface.tsx`、`ChatTurn.tsx` | Appshot 卡片 = 用户侧消息附件的扩展类型 |
| 设置页 | `apps/desktop/renderer/src/settings/`（含快捷键面板，`rg shortcut` 命中 settings 目录） | 新增 Appshots 设置分区 |
| 跨层契约 | `packages/protocol/src/` | `AppshotPayload` 协议类型（禁止 ad hoc IPC payload） |

## 3. P0a 技术 spike 验证清单（先做，1 个 issue，时间盒 2~3 天）

> spike 目的：把产品文档 §13 的 Q1（双 ⌘ 可行性）与最大技术不确定性在写正式代码前消掉。每项 spike 产出「结论 + 最小 demo 脚本/录屏 + 写回本文档」。

| # | 验证项 | 具体问题 | 候选方案 | 通过判据 |
|---|---|---|---|---|
| S1 | frontmost 窗口识别 | Electron 主进程能否拿到前台 App 的 `appName/bundleId/pid/windowId/bounds`？ | ① `active-win`（npm，含原生绑定）② `osascript` System Events ③ 自写小型原生模块（参照 credential-helper 的原生先例） | 在 Finder/VS Code/Safari 三个前台各取一次，字段齐全、耗时 <200ms；明确各方案所需权限（②需 Automation/AX） |
| S2 | 窗口截图 | 拿到 windowId 后如何截「单窗口」而非整屏？ | ① Electron `desktopCapturer`（window source，分辨率上限与匹配 windowId 的可靠性存疑）② macOS 自带 `screencapture -l<CGWindowID> -x -o` CLI ③ ScreenCaptureKit 原生模块 | 1080p 级窗口捕获 ≤1.0s（产品 §12.4）；图像清晰无黑屏；Retina scaleFactor 记录正确；给出三方案优先序 |
| S3 | 全局热键 | ① 标准 accelerator 经 `shortcut-service.mjs` 注册 `appshot` 是否与现有 quickChat 冲突检测/回滚兼容？② 双 `⌘` 手势 Electron `globalShortcut` 是否根本不支持（预期不支持，需 event tap + 额外权限）？ | `globalShortcut` + 现有 `GLOBAL_ACTIONS` 机制；双 ⌘ 仅做可行性结论不做实现 | 标准键位注册/冲突/回滚测试全绿；双 ⌘ 给出「支持/不支持+代价」书面结论（对应产品文档 Q1） |
| S4 | Screen Recording 权限 | `systemPreferences.getMediaAccessStatus('screen')` 读数是否准确？授权后**是否必须重启 App** 才能生效（TCC 行为，产品 §12.4 要求文案如实）？ | Electron `systemPreferences` + `import-permission-preflight.mjs` 的深链模式 | 未授权/已授权两态读数正确；实测记录「授权后免重启 or 需重启」结论并写回产品文档 |
| S5 | 附件链路可达性 | 主进程发起的图片能否经现有 `attachmentIntake.ts` 进入指定会话作为用户侧附件（而非模型工具结果）？ | 复用 attachment 状态机 + 新 IPC；或扩展 message part | 一张本地 PNG 从主进程投递到会话缩略图渲染成功，路径全程无 base64 进日志 |

**spike 完成定义**：S1–S5 各有书面结论；S2/S4 的结论直接决定 T3/T5 的实现方案；本文档 §3 表格补「结论」列。

### 3.1 Spike 实测结论（2026-07-30，脚本在 `peer_agent/scratch/appshot-spike/`，产物在其 `out/`）

| # | 结论 | 对实现的决定 |
|---|---|---|
| S1 | **部分通过**。`osascript` 无需任何权限可拿 `appName/pid/bundleId`（5 次中位 249.6ms）；**窗口级字段（title/bounds）被拒**：「osascript is not allowed assistive access」，需 Accessibility 权限。CGWindowList（swift 枚举）在 Screen Recording 授权下可拿 `windowId/bounds/owner`。 | T3 采用组合：CGWindowList 原生枚举定位 frontmost 窗口（仅需 Screen Recording），osascript 兜底 App 级识别；<200ms 判据需原生模块，脚本路径 250ms 级可接受为 P0a 起点 |
| S2 | **通过，两路径均产出真实 PNG**。① `screencapture -l<windowId>`：2904×1898 RGBA 644KB，**实测 0.122s**（判据 ≤1.0s）；但对 System Settings 窗口报「could not create image from window」。② `desktopCapturer` 全分辨率：3305×2160 1.6MB，getSources 270ms + PNG 编码 131ms ≈ 401ms；windowId 映射需按 name 匹配、不精确。 | **T3 主路径 = `screencapture -l`**（快、原生分辨率、独立进程崩溃隔离）；desktopCapturer 作回退；必须处理「个别系统窗口不可捕」失败分支 |
| S3 | **通过（标准键位）/ 双 ⌘ 不可行**。`CommandOrControl+Shift+A` 注册成功；`Command+Command` 与纯 `Command` 均抛 accelerator conversion failure——Electron 语法层不支持修饰键手势。`shortcut-service.mjs` 的 `validateShortcut`（恰 1 个非修饰键 + ≥1 修饰键）与失败回滚可直接复用；`register()` 当前硬编码 quickChat 回调，T4 需小改为 per-action 回调表。 | T4 默认键位 `CommandOrControl+Shift+A`；双 ⌘ 需 CGEventTap/NSEvent 原生监听 + 可能的输入监控权限，**列 P2 原生增强**，不阻塞 P0a |
| S4 | **两态均已实测通过**。未授权态：撤权后 `getMediaAccessStatus('screen')='denied'` 读数正确；此时 `screencapture -l` 失败（exit=1），**报错与「窗口不可捕」完全相同**（could not create image from window）——错误信息无法区分「无权限」与「该窗口不可捕」。重新授权后：新进程立即读到 `granted`，desktopCapturer（9 源，264ms）与 `screencapture -l`（538KB PNG）均恢复，**无需重启系统**。遗留：运行中进程能否不重启感知授权变化未捕获到（轮询进程 180s 超时早于重授权），对运行中进程仍按「可能需重启」保守处理。TCC 条目在开发态显示为「Electron」，打包后归属 Peer Agent.app。 | T5 实现定案：①捕获前**必须先读权限状态**做 preflight，不能靠 screencapture 报错区分失败原因；②denied → 引导授权 → 提示「如仍失败请重启 Peer」；③授权状态检测本身即时准确，可在设置页实时刷新 |
| S5 | **通过（ok=true）**。真实 S2 PNG（643942B）经真实 `createConversationStore` API：`createConversation → appendMessage(role:user + attachments[kind:'image', dataUrl]) → getConversation` 读回，附件无损（dataUrlIntact=true）。`ChatAttachment` 结构主进程可直接构造；`main.mjs:2721` 已有 `conversations:append-message` IPC。**发现的坑：dataUrl 内联 jsonl 会话文件膨胀**（644KB 图 → 859KB base64）。 | T6 投递复用 store 直写 + changeEvent 广播，无需新 IPC 面；**T2/T3 修正：正式实现图片存 artifact 文件 + 卡片按 ref 加载**，仅小缩略图可内联 dataUrl |

**对 T3/T5 的净影响**：T3 主路径从「三候选待定」收敛为 `CGWindowList 枚举 + screencapture -l 捕获 + desktopCapturer 回退`；**T3 失败分类不能依赖 screencapture 的错误文本**（无权限与窗口不可捕报错相同），必须先做权限 preflight 再捕获，据此区分 `permission_denied` / `window_not_capturable` 两种结构化失败；T5 权限读数即时准确可实时刷新，仅对运行中进程保留「如仍失败请重启 Peer」兜底文案；T2 的 `visual` 字段必须是 `artifactRef` 而非内联 dataUrl（缩略图例外）。

---

## 4. P0a 工程任务清单（每项可直接建 issue）

> 依赖顺序：T0 → T1(spike) → T2 → T3 → T4/T5 并行 → T6 → T7/T8/T9 并行 → T10 → T11。
> 验收方式均可追溯到产品文档 §12.1 P0a 验收项。

### T0 — ADR：Appshots 能力边界与 Evidence 链

- **内容**：一页 ADR 写清 P0a 用户手势触发、不暴露模型工具、artifact 落盘路径、日志红线；落 `peer-knowledge/knowledge/decisions/`。
- **验收**：ADR 合入；评审确认与 `AGENTS.md` Runtime Chain 不冲突。
- **依赖**：无。

### T1 — Spike 套件（§3 S1–S5）

- **验收**：§3 表格补全结论列；双 ⌘ 结论写回产品文档 §13 Q1。
- **依赖**：T0。

### T2 — 协议类型 `AppshotPayload`

- **内容**：在 `packages/protocol/src/` 新增 appshot 类型（源自产品文档 §5.4 语义模型，按 spike 结论裁剪）；含 `source` 元数据、`visual.artifactRef`、`privacy` 标记；P0a 的 `text` 字段仅占位 `mode:'none'`。
- **验收**：类型 + 单测合入；`main.mjs` 新 IPC 与 renderer 均引用协议类型，无 ad hoc payload。
- **依赖**：T1。

### T3 — 主进程 `appshot-service.mjs`

- **内容**：新文件 `apps/desktop/electron/main/appshot-service.mjs`：`resolveFrontmost() → captureWindow() → persistArtifact() → buildPayload()`；实现方案按 S1/S2 结论；Peer 自身前台时返回结构化拒绝；失败路径结构化（无权限/无窗口/捕获失败）。
- **验收**：单测覆盖成功/Peer 前台/无权限/无窗口四路径（mock 捕获层）；1080p 窗口本地捕获中位 ≤1.0s 有 bench 记录。
- **依赖**：T2。

### T4 — 热键接入 `shortcut-service.mjs`

- **内容**：`DEFAULT_SHORTCUTS` 增加 `appshot`（默认键位按 S3 结论，倾向 `CommandOrControl+Shift+A` 类标准 accelerator）；加入 `GLOBAL_ACTIONS`；`main.mjs` 装配 `onAppshot`。
- **验收**：`shortcut-service.test.mjs` 扩展：注册成功、与 quickChat/newTask 冲突检测、注册失败回滚三案例全绿。
- **依赖**：T3（可与 T5 并行）。

### T5 — Screen Recording 权限预检与引导

- **内容**：新增 `appshot-permission-preflight.mjs`（同构 `import-permission-preflight.mjs`）：`getMediaAccessStatus('screen')` 读数、系统设置深链、按 S4 结论写「是否需重启」文案 key（进 `packages/i18n`）。
- **验收**：单测两态读数；手测未授权 → 深链打开正确面板；授权后行为与 S4 结论一致。
- **依赖**：T3（可与 T4 并行）。

### T6 — destination 路由：最近活跃会话 / 新建

- **内容**：主进程基于 `conversation-store.mjs` 实现「最近活跃且未归档会话；无则新建」；投递为**用户侧 Appshot 附件消息**，不自动开跑 Agent。
- **验收**：单测三案例：有活跃会话投递正确、无会话新建、归档会话被跳过；投递后会话 `updatedAt` 不被误改导致路由自激。
- **依赖**：T3。

### T7 — 会话内 Appshot 卡片（renderer）

- **内容**：扩展 `attachmentIntake.ts` / `chat/state/types.ts` 支持 appshot 附件；`ChatTurn.tsx` 渲染缩略图 + 来源 App + 捕获时间 + 元数据；复用现有图片预览组件。
- **验收**：`attachmentIntake.test.ts` 扩展用例全绿；UI 手测卡片展示齐全；缺图 artifact 时显示损坏态而非空白成功。
- **依赖**：T2、T6。

### T8 — 设置页 Appshots 分区（P0a 最小版）

- **内容**：`renderer/src/settings/` 新增 Appshots 面板：总开关、当前热键展示（只读）、Screen Recording 权限状态 + 打开系统设置、「测试捕获」按钮（走与热键相同的 IPC）。
- **验收**：产品文档 §6.4 P0a 六项齐备；权限状态与系统实际状态一致；测试捕获成功/失败均有反馈。
- **依赖**：T4、T5。

### T9 — 成功/失败反馈

- **内容**：捕获成功后轻量反馈（toast/托盘短态，二选一，不抢焦点、不强置前 Peer 主窗口）；失败给出原因与下一步（授权/换窗口）。
- **验收**：产品 §12.1「不强行前置」「失败有明确反馈」两项手测通过。
- **依赖**：T6。

### T10 — 日志与隐私红线

- **内容**：审计 appshot 全链路：日志只允许 artifact 路径与尺寸元数据，禁止图片 bytes/base64/窗口标题以外敏感串；加防回归单测（log sink 断言）。
- **验收**：grep 全链路日志点无违规；单测合入。
- **依赖**：T3–T9 完成后收口。

### T11 — P0a 验收走查

- **内容**：按产品文档 §12.1 八项 + §12.4 性能指标逐条实测，结果写回产品文档验收清单勾选。
- **验收**：八项全勾；不达标项立修复 issue 后再收口。
- **依赖**：T10。

---

## 5. 建 issue 顺序与并行度

```text
T0 ADR ──► T1 Spike ──► T2 协议 ──► T3 appshot-service ──► T6 路由 ──► T9 反馈 ─┐
                                        │                                      ├─► T10 红线 ─► T11 验收
                                        ├─► T4 热键 ──┐                        │
                                        └─► T5 权限 ──┴─► T8 设置页 ───────────┘
                                        T7 卡片（T2+T6 后，可与 T8 并行）
```

- 单人串行预估：spike 2–3 天 + 实现 5–8 天 + 验收 1 天。
- 两人并行：T4/T5、T7/T8/T9 均可拆开并行。

## 6. P0b 评估入口（不建实现 issue，仅评估）

P0a 的 T11 收口后，先做一个 **P0b spike 评估 issue** 再决定排期：

- AX 可读文本提取的技术路径（`AXUIElement` 遍历需 Accessibility 权限；Electron 无内置，需原生模块或辅助进程——可参照 `crates/peer-credential-helper` 的 Rust 辅助先例评估 Rust + `accessibility` crate 方案）；
- 对 TextEdit / Safari / VS Code 三类目标实测文本可达性与 offscreen 覆盖率；
- 结论写回产品文档 §5.3 与 §13 Q2/Q6，再拆 P0b 任务清单。

## 7. 交叉引用

- 产品需求与分期：`design/product/appshots-window-context-capture.md`（本拆解的 T 编号验收均映射其 §12.1/§12.4）
- 快捷键治理先例：`design/product/quick-chat-floating-window.md`
- 观察能力与权限分轨：`knowledge/architecture/computer-use-capability-ladder.md`
- 浏览器截图边界（勿混用）：`design/product/embedded-browser-surface.md`
