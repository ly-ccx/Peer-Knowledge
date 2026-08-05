# Appshots 能力边界与 Evidence 链

日期：2026-07-30  
分支：`dev/0.0.1`  
状态：已定案（P0a 实现依据）  
关联：`design/product/appshots-window-context-capture.md`（产品）、`design/product/appshots-engineering-task-breakdown.md`（工程拆解 + spike 实测结论 §3.1）

## 背景

Appshots 是用户主动触发的「前台应用窗口上下文快照」能力：热键一次捕获 frontmost 窗口画面（P0b 起加可读文本），投递到目标会话供模型理解。Spike（S1–S5，2026-07-30）已实测定案技术路径。本 ADR 固化 P0a 的四条架构红线。

## 决策 1：能力边界 —— 只读观察，不是操控

- Appshots 是 **observe-only** 能力：捕获窗口像素与元数据，不注入键鼠事件、不驱动目标 App。
- 权限面仅 Screen Recording（P0b 文本再加 Accessibility），**与 Computer Use 操控授权严格分轨**；任何 UI 文案不得把 Appshots 授权表述为「允许控制电脑」。
- 触发源仅限用户手势：目标为左右 ⌘ 同按（**暂缓实施**，见附录 A）；**当前不注册全局热键、不占用 `⌘⇧A`**，仅保留设置页「测试捕获」。
- Peer 自身为 frontmost 时返回结构化拒绝（`peer_frontmost`），不静默捕获自己。

## 决策 2：不暴露模型工具

- P0a **不注册任何模型可见工具**：`appshot_capture` 不进 Runtime Projection，不进 capabilities/*.json 的模型投影。
- 理由：模型可发起的屏幕捕获必须完整走 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence 链，且需要独立的权限授予 UX；这超出 P0a 范围。
- 若未来开放，另立 ADR，且默认策略为「每次调用需用户确认」。
- appshot-service 只接受主进程内部调用（热键回调 / 设置页 IPC），不接受来自 chat runtime 工具执行路径的调用。

## 决策 3：artifact 落盘与 payload 形态

- 捕获产物 PNG **必须落本地 artifact 文件**，payload 中以 `artifactRef`（`local-appshot-artifact://<id>` 同构现有 `local-shell-artifact://` 惯例）引用。
- **禁止**把整图 base64/dataUrl 内联进会话 jsonl（spike S5 实测：644KB 图 → 859KB base64，会话文件不可接受地膨胀）；仅允许 ≤64KB 级缩略图内联用于卡片即时渲染。
- 落盘目录随会话生命周期管理，会话/附件删除时可回收。
- 失败路径结构化四类：`permission_denied` / `peer_frontmost` / `no_window` / `window_not_capturable`。其中 `permission_denied` 必须由 **preflight 判定**，不得依赖 screencapture 错误文本（spike S4 实测：无权限与窗口不可捕报错完全相同）。

## 决策 4：日志红线

- 全链路日志**禁止**出现：图片 bytes、base64/dataUrl 片段、AX 文本内容（P0b）。
- 允许记录：artifactRef、文件路径、尺寸/字节数元数据、耗时、结构化失败码、appName/bundleId。
- 窗口标题（windowTitle）默认**不进日志**（可能含文档名/网址等敏感串），只进 payload。
- 该红线以单测防回归（log sink 断言，T10）。

## 实现锚点（spike 定案）

```text
resolveFrontmost: CGWindowList 原生枚举（swift/原生模块）+ osascript 兜底 App 级识别
capture:          screencapture -l<windowId>（主路径，实测 0.122s）
                  desktopCapturer（回退，实测 ~401ms 全分辨率）
preflight:        systemPreferences.getMediaAccessStatus('screen')（读数即时准确）
投递:             conversation-store appendMessage（role:user + attachments），复用 changeEvent 广播
```

## 后果

- P0a 交付面小而稳：热键 → 截图 → 会话卡片，无模型侧新攻击面。
- 模型无法自主截屏，牺牲部分自动化能力换取权限模型清晰——这是有意取舍。
- artifact 引用制使会话文件保持轻量，但渲染侧需按 ref 异步加载大图（T7 承担）。

## 附录 A：双 ⌘ 热键决策记录（2026-07-30，用户决策）

- **目标**：默认热键改为**左右 ⌘ 同按**（对齐 ChatGPT Appshots）。
- **状态**：**暂缓开发、功能不外露**，待开发者账号申请完成后实施。
- **理由**：双 ⌘ 无法用 Electron accelerator 表达（spike S3 实锤），必须走 NSEvent/CGEventTap 原生全局监听，硬依赖 Accessibility 权限（spike S6 实测：未授权时 `TRUSTED=false`，监听零事件）。无签名/公证的开发版在 TCC 授权面上不可控（条目显示为 Electron 而非 Peer Agent），正式签名后再做权限申请体验才成立。
- **权限面影响（恢复开发时生效）**：Accessibility 从「P0b 文本提取才需要」提前到「热键路径即需要」；决策 1 的权限分轨原则不变——Accessibility 授权仅用于修饰键监听与（未来的）AX 文本，仍不授予操控。
- **回退契约**：双 ⌘ 上线前**不占用** `⌘⇧A`；上线后若无 Accessibility 权限，应明确提示并降级到设置页「测试捕获」，不得静默失效、也不得默认抢占其它系统/应用快捷键。
- **进度与恢复待办**：见拆解文档 §0.1（spike 探针 s6-doublecmd.swift 已编译验证，左右同按真机检测未做；`⌘⇧A` 全局占用已于 2026-07-30 解除）。
