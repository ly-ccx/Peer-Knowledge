# Quick Chat 独立 Popover 窗

日期：2026-07-30
最后更新：2026-11-15（规范标注 Accepted 并对齐 `effort` 全词表与渠道分组口径）
分支：`dev/0.0.1`
状态：Accepted（已定案实现依据；其中 `effort` 选项已由 [ADR 37](37-provider-channel-and-wire-protocol-separation.md) 与 [ADR 48-provider](48-provider-model-options.md) 统一为 `off | low | medium | high | xhigh | max`，`model` 分组逻辑与 [ADR 76](76-peer-acp-agent.md) 共享）
关联：`design/product/quick-chat-floating-window.md`

## 背景

Quick Chat 悬浮 bar 的 workspace / model / mode / effort 下拉原先画在 **同一 BrowserWindow 的 DOM** 内。  
为避免列表被窗口边界裁切，主进程在打开 popover 时用 `setBounds` **拉高整窗**。这带来：

1. 列表仍可能贴边裁切（透明圆角 + alwaysOnTop 更明显）
2. 输入区长高与菜单扩窗耦合，状态难维护
3. 扩窗/缩窗与焦点、maxHeight 竞态（已有测试在补救，根因未消）

备选曾讨论：Flutter 悬浮窗、Swift + C# 双原生业务窗。均过重，且与 Peer Frost / Electron 业务复用冲突。

## 决策

### 1. 采用 Electron 独立 Popover BrowserWindow

```text
Quick Chat Bar  (window=quick-chat)
  内容驱动高度：输入多行 / 附件 / 任务卡
  不为菜单扩窗

Quick Chat Popover  (window=quick-chat-popover)
  独立 BrowserWindow
  主进程按 anchor + workArea 定位（可上翻）
  渲染同一套 React popover 内容
```

业务真相仍在 Electron 主进程 + TS/React；不引入第二 UI 运行时。



### 1b. 简单枚举 vs 富内容（2026-07-31 补充）

| kind | 呈现 |
| --- | --- |
| `workspace` / `mode` / `access` / `effort` | Electron **`Menu.popup`**（系统菜单，天然不裁切） |
| `model` | **`Menu.popup` 二级 submenu**（按 provider `group` 分组） |

Renderer 仍统一走 `quickChatShowPopover` IPC；主进程按 `MENU_KINDS` / `WINDOW_POPOVER_KINDS` 分流。

### 2. 高度策略分离

| 原因 | 是否允许改 Bar 高度 |
| --- | --- |
| textarea 换行 / 附件条 / 错误 / 任务卡 | ✅ 内容驱动长高（默认 104，上限 480） |
| 打开 workspace/model 等下拉 | ❌ 禁止；由独立 popover 窗承担 |

### 3. 否决项（现阶段）

| 方案 | 结论 |
| --- | --- |
| Flutter 悬浮窗 | 否。第二套 UI 运行时；自身仍可能有窗口边界问题 |
| Swift + C# 整窗业务双维护 | 否。成本 ×3～4，Composer 语义无法复用 |
| 继续同窗 DOM + setBounds 扩高 | 否。不得再作为终态 |
| 系统 Menu 覆盖全部选择器 | 否。**枚举项**（workspace/model/mode/access/effort）均 `Menu.popup`；model 按 provider 二级 submenu |

### 4. 进程与 IPC 边界

- `quick-chat-popover:show`：bar → main，携带 kind/items/selected/anchorRect  
- main 创建或复用 popover 窗，按屏幕坐标 `setBounds` 并 `show`  
- `quick-chat-popover:state`：main → **popover 窗**（不是 bar）  
- `quick-chat-popover:select` / hide：popover 或 bar → main  
- `quick-chat:popover-selected` / `quick-chat:popover-closed`：main → **bar**  
- bar 隐藏、提交、toggle 关闭时必须级联 hide popover

### 5. 定位规则

- 水平：相对 trigger；model/effort 右对齐；夹入 workArea  
- 垂直：优先 bar 底部 flush；下方空间不足则上翻  
- 尺寸：与现有 `resolveQuickChatPopoverSize` 一致（最大约 360×280）

### 6. 后续可选（非本 ADR 范围）

- ~~极简枚举改为 `Menu.popup`~~（已落地，见 §1b）
- 仅当独立 Electron 窗仍不满足质感时，评估 **薄原生 Popup 壳**（不做业务）

## 验收

1. 打开任意 Quick Chat 下拉，列表不被 bar 边缘裁切  
2. 贴屏幕底/顶可自动翻向有空间一侧  
3. 多行输入时 bar 可长高；关闭 popover 后 bar 高度回到内容高度  
4. Esc / 失焦 / 再次点击 trigger 可稳定关闭  
5. 单测覆盖独立窗创建、定位、选择回传、不扩 bar
