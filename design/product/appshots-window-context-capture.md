# Appshots（应用窗口快照）产品功能文档

创建时间：2026-07-30  
最后更新：2026-07-30  
状态：Draft（产品方案，本轮只落知识库，不改代码）  
范围：Peer Agent Desktop（首期 macOS；Windows/Linux 见分期）  
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）

关联文档：

- `design/product/appshots-engineering-task-breakdown.md`（P0a 工程任务拆解与 spike 验证清单；本文档 §12.1 验收项的实现映射）
- `knowledge/architecture/computer-use-capability-ladder.md`（L1/L2/L3 观察与权限阶梯；Appshots 复用 L3 观察能力，但**不是** Computer Use 操控）
- `design/product/embedded-browser-surface.md`（内嵌 Browser「截取页面」与 `browser_screenshot`；与 Appshots 边界分离）
- `design/product/quick-chat-floating-window.md`（系统级热键、快捷键设置页、冲突检测与注册失败回滚）
- `design/product/menu-bar-tray-recent-sessions.md`（托盘 / 近期会话入口；destination 可与「当前会话」策略协作）
- `design/product/status-bar-task-center.md`（任务中心回流；Appshot 投递后的会话可见性）

---

## 1. 背景与目标

### 1.1 对照对象（ChatGPT Appshots）

ChatGPT Desktop 设置中的 **Appshots** 提供：

1. **一键把前台窗口上下文交给对话**  
   文案要点：*Take an appshot to show ChatGPT your frontmost window*。
2. **视觉 + 文本双通道**  
   *Appshots include visual and text content, including text scrolled offscreen*。
3. **系统级热键**  
   默认同时按下两侧 `⌘`（`⌘ + ⌘`），可改。
4. **投递目标（destination）**  
   热键触发后，快照进入哪条会话 / 哪个端（如 Automatic / 指定 chat）。
5. **成功音效**  
   *Play sound effect* 开关。
6. **设置入口**  
   Integrations 下的独立 **Appshots** 设置页。

### 1.2 Peer 要解决的问题

用户在 IDE、浏览器、设计工具、文档、邮件等**任意前台应用**工作时，需要把「当前窗口在看什么 + 系统可访问性允许的可读文本」快速送给 Peer，而不是：

- 手动 ⌘⇧4 截图再拖进 Composer；
- 只贴可见像素，模型缺少可读文本上下文；
- 只能截 Peer 内嵌 Browser，无法覆盖外部 App。

### 1.3 一句话定义

> **Appshots 是 Peer Agent 的系统级「前台应用窗口上下文快照」能力：一次热键捕获当前 frontmost 窗口的可视画面，并在系统可访问性允许时提取可读文本；对支持的应用，可包含滚动区域外仍可访问的文本。该上下文会路由到目标会话，供模型理解，而不是授予操作系统级操控权。**

### 1.4 产品定位

Appshots 是：

1. **用户主动触发的上下文采集入口**（热键 / 菜单 / 后续托盘）；
2. **视觉证据 + 结构化/纯文本上下文** 的打包物，进入会话附件与 prompt 组装链路；
3. **Computer Use L3 观察层的用户面产品化**（只读 observe），与 L3 键鼠注入解耦；
4. **跨应用工作流的桥梁**：用户留在原 App，Peer 在后台接收上下文。

Appshots **不是**：

- Computer Use / 自动点击外部 App；
- 持续屏幕录制或后台监控；
- 全显示器无差别截屏（默认是 **frontmost window**，不是整个桌面）；
- 内嵌 Browser 的 `browser_screenshot` 替代品（后者只服务 Peer 内网页）；
- 云端默认同步原图与完整 AX 树的通道。

---

## 2. 与 ChatGPT Appshots / Peer 现有能力对照

| 能力点 | ChatGPT Appshots | Peer 现状 | Peer 立场 |
|---|---|---|---|
| 捕获对象 | frontmost window | 无 OS 级窗口快照产品；仅有内嵌 Browser 截图 | **对齐**：默认 frontmost window |
| 视觉内容 | 窗口可视画面 | `browser_screenshot` / capture-page 仅限内嵌 webview | **新增** OS 窗口像素 |
| 文本内容 | 含 scrolled offscreen | 无统一「窗口文本」产品通道 | **分期对齐**：P0b 做 AX 可读文本；offscreen 仅在系统可访问性允许时声明；OCR 放 P1 |
| 热键 | 双侧 ⌘，可配置 | Quick Chat 等有全局热键方案，无 Appshot 热键 | **对齐体验，不锁死键位**：默认热键以技术 spike 为准，P0 要求稳定触发 |
| destination | Automatic / 指定 | 有会话、托盘、任务中心，无 Appshot 路由 | **先简化**：P0 投递最近活跃会话；指定会话放 P1 |
| 音效 | 可关 | 无统一成功音效约定 | **对齐**：可选成功音效 |
| 设置页 | Integrations → Appshots | 无 | **对齐**：设置分区入口 |
| 权限 | 系统隐私权限 | 仅有 Full Disk 等导入权限预检先例 | **必须**：Screen Recording +（文本）Accessibility 分轨 |
| 与操控关系 | 展示给 ChatGPT 看 | L3 架构规划操控 | **分叉**：Appshots 只读，不授权操控 |

### 2.1 关键差异（Peer 分叉）

1. **与 Computer Use 严格分层**  
   Appshots 成功 ≠ 授予 L3 操作权；权限申请文案不得写成「允许控制电脑」。
2. **destination 语义更贴近 Peer 会话模型**  
   Automatic = 当前焦点会话 / 最近活跃会话 / 可配置策略；支持「新建会话再投递」。
3. **证据与本地优先**  
   大图与完整语义树落本地 artifact；模型侧默认受限预览 + 文本摘要 + ref（与 computer-use 观察协议一致）。
4. **多入口**  
   除热键外，预留菜单栏、Composer「捕获前台窗口」、主窗口命令面板；首期 P0 以热键 + 设置为主。

---

## 3. 产品目标与非目标

### 3.1 目标

1. **一键可用**：热键后中位时延可感知完成（目标见 §12），用户不离开当前 App。
2. **先打通视觉闭环，再增强文本**：P0a 先确保窗口截图可靠投递；P0b 再加入 Accessibility 可读文本。
3. **屏外文本诚实声明**：仅当系统可访问性树能提供滚动区域外文本时，才标记为包含 offscreen；无法提取时明确降级说明。
4. **路由简单可靠**：P0 默认投递最近活跃会话；指定会话与高级 destination 放到 P1。
5. **权限诚实**：分别说明并检测屏幕录制与辅助功能；缺权可引导系统设置。
6. **隐私默认安全**：不采集 secure text value，不把原图/全文写入日志；敏感 App 黑名单作为 P1 增强。

### 3.2 非目标（首期明确不做）

- 自动连续截屏 / 定时 Appshot  
- 后台监听用户操作并自动投喂模型  
- 多窗口批量拼接为「工作区拼贴」  
- 跨显示器整屏截图作为默认行为  
- 用 Appshots 代替 Computer Use 点击/输入  
- 保证所有 App（游戏、DRM、受保护视频、远程桌面特殊层）都能拿到完整文本  
- Windows / Linux 首期对等实现（仅预留接口与文案占位）  
- 云端多设备同步 Appshot 原图库  

---

## 4. 用户故事与核心场景

| ID | 角色 | 场景 | 期望 |
|---|---|---|---|
| US-1 | 开发者 | 在 IDE 看报错，按热键 | 当前 IDE 窗口图 + 可见/可滚动错误文本进入当前 Peer 会话 |
| US-2 | 产品 | 在 Figma / 浏览器看设计稿 | 窗口画面进入会话，便于让 Agent 对照 UI 文案 |
| US-3 | 写作者 | 长文档只显示一屏 | 尽量带上滚动区域外段落文本，而不仅是可见像素 |
| US-4 | 多会话用户 | 同时开多个 Peer 会话 | destination=指定会话时，热键不误投 |
| US-5 | 隐私敏感用户 | 前台是密码管理器 | 拦截或强提示，不静默上传 |
| US-6 | 首次用户 | 未授屏幕录制权限 | 清晰引导授权，失败可重试，不假成功 |

### 4.1 主路径（Happy path）

```text
用户在任意 App 工作
  → 按下 Appshot 热键
  → Peer 识别 frontmost window（bundleId / pid / windowId / title）
  → 并行：窗口像素捕获 + 文本提取（AX 优先）
  → 组装 Appshot payload（图 + 文本 + 元数据）
  → 按 destination 路由到目标会话 Composer / 直接作为用户消息附件
  → 可选播放成功音效
  → 用户切回 Peer 或继续原 App；Agent 可基于该上下文回答
```

### 4.2 失败路径（摘要）

| 失败 | 用户可见 | 系统行为 |
|---|---|---|
| 无屏幕录制权限 | 权限引导卡片 / 通知 | 不产生「假截图」；可打开系统设置 |
| 有图无 Accessibility | 提示「仅视觉，无屏外文本」 | 仍可投递截图；标记 textMode=visual_only |
| 无法识别 frontmost | 轻错误 toast | 不投递 |
| 目标会话不存在 | 回退 Automatic 或新建 | 明确文案 |
| 敏感 App 黑名单 | 拦截说明 | 不捕获像素/文本 |
| 热键冲突 | 设置页显示注册失败 | 回滚到上一可用绑定 |

---

## 5. 功能范围详解

### 5.1 捕获对象：Frontmost window

**定义**：触发瞬间，系统判定的前台应用主窗口（或该应用的 key window）。

必须记录的元数据（用户可见摘要 + 内部字段）：

| 字段 | 说明 |
|---|---|
| `capturedAt` | ISO 时间 |
| `appName` | 显示名 |
| `bundleId` / 平台应用 ID | 稳定标识 |
| `pid` | 进程 |
| `windowId` | 若可得 |
| `windowTitle` | 窗口标题（可脱敏） |
| `bounds` | 逻辑坐标与 scaleFactor |
| `displayId` | 所在显示器 |

规则：

1. **默认不含 Peer 自身窗口**作为目标：若 frontmost 是 Peer，可提示「请先切换到要分享的应用」或允许「捕获 Peer 内焦点内容」的次级策略（P1 再定；P0 建议直接提示切换）。
2. **全屏 / Stage Manager / 多桌面**：捕获触发瞬间所在 Space 的 frontmost window。
3. **多显示器**：以 frontmost 窗口所在屏为准，不默认拼接所有屏。
4. **最小化 / 无窗口 App**：失败并提示。

### 5.2 视觉通道（Visual）

- 输出：窗口位图（推荐 PNG），落本地 artifact，会话中显示缩略图。
- 坐标与尺寸写入 observation 元数据，供后续若扩展 Computer Use 时复用（Appshots 本身不执行点击）。
- 阴影/圆角：优先「窗口内容区」；若系统 API 只能带阴影，可接受，但需在实现备注中统一。
- 动态内容：捕获单帧，不录视频。
- 失败时不得用桌面墙纸或错误占位图冒充成功。

### 5.3 文本通道（Text，含 scrolled offscreen）

这是相对普通截图的**核心差异化**。

#### 5.3.1 提取优先级

```text
1. Accessibility / UI Automation 语义树文本（P0b：优先提取系统可访问文本；仅当 AX 树实际可达时才可能含滚动区域外文本）
2. 可见区域 OCR（P1：作为弱文本兜底，不作为 P0 可靠性前提）
3. 应用特定可读 API（P2+：例如受控 Browser DOM；外部 Chrome 不默认注入，也不作为 P0/P1 承诺）
```

#### 5.3.2 scrolled offscreen 产品承诺

| 级别 | 承诺 | 分期 |
|---|---|---|
| L-Text-A | AX 树能遍历到的静态文本 / 列表项 / 文档节点，即使不在可见矩形内也尽量提取 | **P0 目标** |
| L-Text-B | 虚拟列表仅加载可视窗：对未挂载 DOM/AX 节点不保证 | 诚实降级 |
| L-Text-C | 画布 / 游戏 / 受保护渲染：仅视觉 + OCR | 降级 |
| L-Text-D | 密码框、安全输入、系统敏感字段 | **禁止提取值** |

用户可见状态（建议）：

- `文本：完整语义` / `文本：部分（含屏外）` / `文本：仅可见 OCR` / `文本：不可用`

#### 5.3.3 文本体量与整理

- 设上限（建议 P0：原始提取 200k 字符硬顶，进入模型前按策略截断并保留头尾 + 结构大纲）。
- 保留基础结构：标题、分段、列表；去掉纯装饰节点。
- 与截图一起作为**同一 Appshot 对象**，避免模型误以为是两份无关附件。

### 5.4 打包对象（逻辑模型）

这是**产品语义模型**，用于说明 Appshot 进入会话时应包含哪些信息；它不是最终 TypeScript API，也不要求研发逐字段照搬实现。

```ts
type AppshotPayload = {
  appshotId: string;
  capturedAt: string;
  source: {
    appName: string;
    bundleId?: string;
    pid?: number;
    windowId?: number;
    windowTitle?: string;
    bounds?: { x: number; y: number; width: number; height: number };
    scaleFactor?: number;
    displayId?: string | number;
  };
  visual: {
    artifactRef: string;          // 本地截图
    width: number;
    height: number;
    mimeType: 'image/png' | 'image/jpeg';
  };
  text: {
    mode: 'semantic' | 'semantic_partial' | 'ocr_visible' | 'none';
    contentRef?: string;          // 大文本 artifact
    preview: string;              // 短预览
    truncated: boolean;
    includesOffscreen: boolean;   // 是否声明含 scrolled offscreen
  };
  privacy: {
    redacted: boolean;
    reason?: string;
  };
  destination: AppshotDestination;
};
```

### 5.5 触发方式

| 入口 | P0 | 说明 |
|---|---|---|
| 全局热键 | **必须** | 任意前台 App 可用 |
| 设置页「测试 Appshot」 | 建议 | 便于权限调试 |
| 应用菜单 / 命令面板 | P1 | 「捕获前台窗口到当前会话」 |
| Composer 按钮 | P1 | 显式附件入口 |
| 菜单栏托盘 | P2 | 与 tray 信息架构协调 |

---

## 6. 热键、Destination、音效与设置

### 6.1 热键（Hotkey）

对照 ChatGPT：双侧 `⌘` 同时按下。

Peer 建议：

| 项 | 约定 |
|---|---|
| 默认热键（macOS） | **目标键位 = 左右 `⌘` 同按**（对齐 ChatGPT，用户决策 2026-07-30）。**当前状态：暂缓实现、功能不外露**——双 ⌘ 需 NSEvent/CGEventTap 原生全局监听 + Accessibility 权限，待开发者账号申请完成后再开发。**过渡期不注册任何全局 Appshot 热键**（含不占用 `⌘⇧A`）；捕获入口为设置页「测试捕获」。 |
| 可配置 | 设置页可修改、恢复默认 |
| 生效条件 | Peer 已启动（含菜单栏常驻 / 后台运行策略与现有 Desktop 生命周期一致） |
| 冲突检测 | 与 `quick-chat-floating-window.md` 快捷键设置页同一套：应用内重复检测、注册失败回滚、启动校验 |
| 与 Quick Chat 关系 | **独立动作**；不得共用同一默认键 |
| 无障碍 | 注册失败、捕获成功/失败有非仅音效的反馈（通知或即时 UI） |

> 注意：双修饰键手势在 Electron/`globalShortcut` 上可能受限，实现阶段若不可靠，P0 允许改为标准 accelerator，但产品文案需同步，不得宣传做不到的「双 ⌘」。

### 6.2 Appshot destination（投递目标）

对照 ChatGPT：*Choose where appshots go when you use the hotkey*，默认 Automatic。

Peer 选项（按分期）：

| 值 | 行为 | 分期 |
|---|---|---|
| `automatic`（默认） | 投递到「最近活跃且未归档的会话」；若无，则新建会话 | **P0a** |
| `pinned_session` | 用户指定一个会话 ID | P1 |
| `current_focused` | 仅当 Peer 主窗口有焦点会话时投递；否则回退 automatic 并提示 | P1 |
| `always_new` | 每次热键新建会话并投递 | P1 |

投递形态（P0a 默认）：

1. 在目标会话插入一条**用户侧 Appshot 消息**（缩略图 + 基础元数据；P0b 后包含文本预览）；
2. **不自动开跑 Agent**，除非用户在设置中开启「捕获后自动发送并请求分析」（P1，默认关）；
3. P0a 不要求通知回流；若 Peer 主窗口不可见，可先用轻量成功反馈，系统通知放 P1。

### 6.3 音效

- 设置项：`Play sound effect`（默认开或关与平台通知习惯对齐；建议默认开、可关）。
- 仅表示**捕获+投递成功**；权限失败、拦截不播放成功音。
- 音量跟随系统；不提供复杂音效包。

### 6.4 设置页信息架构

建议路径（对照截图 Integrations 分区）：

```text
设置
  Personal …
  Integrations
    - Appshots          ← 本功能
    - Plugins
    - Browser
    - Computer use
  …
```

页面结构按分期收敛：

**P0a 最小设置页**：

1. **标题**：Appshots  
2. **说明卡**：捕获前台窗口画面；文本能力为后续增强，不在 P0a 强承诺  
3. **总开关**：启用 / 停用 Appshots  
4. **当前热键展示**：展示默认键位；P0a 可暂不支持修改  
5. **屏幕录制权限状态**：已授权 / 未授权 → 打开系统设置  
6. **测试捕获**按钮：用于验证权限与捕获闭环

**P0b 增加**：

7. **辅助功能权限状态**：已授权 / 未授权 → 打开系统设置  
8. **文本提取状态说明**：可读文本 / 含可访问 offscreen / 已截断 / 不可用

**P1 增加**：

9. **Hotkey 修改**：改键、恢复默认、冲突检测  
10. **Appshot destination**：指定会话 / 每次新建等高级选项  
11. **Play sound effect** 开关  
12. **隐私高级项**：敏感 App 处理策略入口

搜索关键字：`Appshots`、`应用快照`、`窗口快照`、`前台窗口`、`截图给 AI`。

---

## 7. 权限、隐私与安全（重点注意点）

### 7.1 权限分轨（必须分开申请与解释）

| 权限 | 用途 | 缺失时 |
|---|---|---|
| **Screen Recording（屏幕录制）** | 窗口像素 | 无法视觉通道；整体失败或仅不允许图 |
| **Accessibility（辅助功能）** | 窗口定位增强 + 语义文本 / offscreen 文本 | 可降级为「仅截图 ± OCR」 |
| 通知权限 | 后台投递反馈 | 降级为仅音效 / 下次打开 Peer 可见 |

原则（对齐 computer-use 架构）：

- **最小权限**：Appshots 授权 ≠ Computer Use 操控授权。  
- **分别检测、分别引导**；禁止一个「一键开启所有权限」混用文案。  
- 首次触发时用情境式说明，而不是冷启动强弹全部权限。

### 7.2 隐私

1. **本地优先**：原图与完整文本默认存本地 artifact；随会话生命周期与用户清理策略。  
2. **敏感窗口策略**（P0 基线 + P1 增强）：  
   - P0：密码管理器、系统设置隐私页、银行类可配置列表 → 默认拦截或仅本地预览不发送模型（产品默认建议：拦截并提示）。  
   - 检测可基于 bundleId 列表 + 窗口标题启发式。  
3. **字段脱敏**：密码框、secure text 永不进入 text payload。  
4. **用户可控删除**：会话删除 / 附件删除应可回收 Appshot 文件（实现跟现有 attachment 清理）。  
5. **企业/托管场景**（P2）：策略关闭 Appshots。  
6. **不默认**把完整 AX 树打进模型上下文；用提炼文本 + 截图 ref。

### 7.3 安全边界

- 不注入其他 App 的 JS，不 attach 调试器作为 P0 文本方案。  
- 不把 Appshot 权限复用为键鼠注入。  
- 捕获过程避免把屏幕内容写入日志明文。  
- 模型工具若未来增加 `appshot_capture`，必须走用户手势或显式确认策略（P1 再定；P0 以用户热键为主）。

---

## 8. 与现有 Peer 能力的边界

| 能力 | 关系 |
|---|---|
| 内嵌 Browser 截图 | **不同对象**：页面 webview vs OS 窗口。菜单「截取页面」保持独立。 |
| Computer Use L3 | Appshots 复用观察/artifact/权限检测基建；**不**开启 action。 |
| 附件 / attachmentIntake | Appshot 作为一等附件类型或「复合附件」（图+文本）。 |
| Quick Chat | 可组合：P1 支持「Appshot 后打开 Quick Chat 附带上下文」；P0 不阻塞。 |
| 任务中心 / 通知 | 投递成功回流；运行中会话追加 Appshot 的可见性。 |
| Goal / Agent 模式 | Appshot 只提供上下文，不自动改变规划深度。 |

---

## 9. 交互与反馈规范

### 9.1 成功

- 可选短音效  
- 非模态反馈：菜单栏图标短暂状态 / toast / 通知三选一，避免抢焦点  
- Peer 会话内出现 Appshot 卡片：缩略图、应用名、时间、文本预览、「在访达中显示」或「复制文本」（P1）

### 9.2 进行中

- 热键后若捕获 >300ms，允许极轻量状态（菜单栏 activity）；避免全屏遮罩打断用户

### 9.3 失败

- 可理解的原因 + 下一步（去授权 / 换窗口 / 改 destination）  
- 不出现空白成功卡片  

### 9.4 焦点策略

- **默认不把 Peer 主窗口强行前置**（用户在写代码时按热键，应留在 IDE）  
- 与 Quick Chat「召出即聚焦」不同：Appshots 是**投递型**，不是输入型  

---

## 10. 信息架构与命名

| 用途 | 文案 |
|---|---|
| 功能名 | Appshots（中文可用「应用快照」副标题） |
| 动作 | 捕获前台窗口 / Take appshot |
| 设置说明 | 将前台窗口的画面与文本（含滚动区域外文本）发送到 Peer 会话 |
| 勿用 | 「屏幕监控」「自动控制」「录制你的电脑」 |

设置搜索同义词：应用快照、窗口截图、Appshot、前台窗口、offscreen 文本。

---

## 11. 分期

### P0a：窗口截图闭环（第一验收版本）

目标：先证明 Peer 能在用户主动热键下，把当前前台窗口截图可靠投递到正确会话。

1. macOS frontmost window 识别。  
2. 捕获前台窗口可视图像。  
3. 默认全局热键触发；P0a 不要求双 `⌘`，只要求稳定可用。  
4. 投递到最近活跃会话；若无会话则新建。  
5. 会话内展示 Appshot 卡片（缩略图 + 应用名 + 时间 + 基础元数据）。  
6. Screen Recording 权限检测、状态展示与系统设置跳转。  
7. 捕获成功 / 失败反馈；默认不把 Peer 主窗口强行前置。  
8. Peer 自己在前台时给出明确提示或安全行为。  
9. 不在日志中写入原图、窗口截图内容或完整上下文。  

### P0b：Accessibility 文本增强

目标：在 P0a 截图闭环稳定后，加入可读文本；对 offscreen 文本只做能力声明，不做全应用保证。

1. Accessibility 权限检测、状态展示与系统设置跳转。  
2. 提取 AX 可读文本。  
3. 标记文本质量：`none` / `visible_or_accessible` / `includes_offscreen` / `truncated`。  
4. 文本长度硬顶与截断说明。  
5. 密码框 / secure text 不提取值。  
6. 会话内 Appshot 卡片增加文本预览与文本状态。  

### P1：体验与安全增强

1. 设置页支持修改热键、恢复默认、冲突检测与注册失败回滚。  
2. destination 指定会话、每次新建、current focused 等高级路由。  
3. `Play sound effect` 开关。  
4. OCR 可见区兜底与质量提示。  
5. 敏感 App 黑名单 / 遮罩策略。  
6. 通知回流与多会话未读提示。  
7. Composer / 命令面板入口。  
8. 与 Quick Chat 组合：Appshot 后打开 Quick Chat 并附带上下文。  
9. 「捕获后自动发送并请求分析」可选，默认关。  

### P2+

1. Windows / Linux。  
2. 多窗口选择器（非仅 frontmost）。  
3. 区域框选 Appshot。  
4. 应用特定文本 adapter（如受控 Browser DOM 增强）。  
5. 企业策略。  
6. 历史 Appshot 库浏览（若有强需求）。 

---

## 12. 验收标准

### 12.1 P0a 功能验收

> 2026-07-30 走查结论（实现映射见拆解文档 §0；自动化证据 = peer_agent 单测/E2E，UI 项标注待手测）：

- [x] 在非 Peer 应用前台按下默认热键，最近活跃会话出现 Appshot，含**窗口截图**。（自动化：E2E 真机捕获 ok=true + delivery 单测；热键→UI 全链路**待手测**）  
- [x] 没有最近活跃会话时，新建会话并投递 Appshot。（自动化：appshot-delivery.test「无会话新建」「全归档新建」两案例绿）  
- [x] 关闭 Screen Recording 权限时：不产生假成功截图，并引导授权。（自动化：preflight 单测 + spike S4 两态实测 denied 读数正确；capture 在 preflight 阻断后不执行）  
- [x] 默认不把 Peer 主窗口强行前置。（代码审计：热键路径仅系统通知，无 reveal/focus 调用；**待手测**确认）  
- [x] Peer 自己在前台时给出明确提示或安全行为。（自动化：peer_frontmost 结构化拒绝单测绿；通知文案「请切换到要捕获的应用」）  
- [x] Appshot 卡片至少展示缩略图、来源 App、捕获时间与基础元数据。（实现：AttachmentStrip appshot 分支 + ≤480px 缩略图接线，tsc 绿；渲染效果**待手测**）  
- [x] 捕获失败时有明确反馈，不插入空白成功卡片。（自动化：四类失败均结构化返回且不 append 消息；缺图卡片显示 ⚠︎ 占位而非空白；失败通知文案分类）  
- [x] 日志不写入原图、窗口截图内容或完整上下文。（自动化：appshot-log-redline.test 3/3 绿 + 全链路 grep 零违规）  

**遗留待手测项（需真实 App 环境）**：热键端到端触发、通知点击回流、卡片视觉、设置页交互。**已知环境事实**：全仓 main 测试 772 中有 7 个失败（llm-chat-service 6 + Provider adapters 1），已用 git 基线对照验证为**存量失败**，与 Appshots 改动无关（appshot 四模块 22 测试 + 相邻模块全绿）。

### 12.2 P0b 功能验收

- [ ] 开启 Accessibility 权限后，同一 Appshot 可包含 AX 可读文本。  
- [ ] 对 AX 良好的 App（如 TextEdit / 多数原生文档），若系统可访问树包含当前视口外内容，可标记 `includes_offscreen`；不对所有 App 做绝对承诺。  
- [ ] 对无法提供 AX 文本的目标，产品展示降级状态，且截图投递不受影响；**不静默假装有完整文本**。  
- [ ] 关闭 Accessibility 权限时：行为符合设定（仅图或提示文本不可用），设置页状态为未授权。  
- [ ] 文本超上限时标记 `truncated`。  
- [ ] 密码框 / secure text 不提取值。  

### 12.3 P1 功能验收

- [ ] 热键可改、冲突可检测、注册失败可回滚。  
- [ ] destination 指定会话、每次新建等高级路由不串会话。  
- [ ] 音效开关有效，且只在捕获+投递成功时播放成功音。  
- [ ] OCR 可见区兜底有质量提示，不冒充完整语义文本。  
- [ ] 敏感 App 黑名单 / 遮罩策略可配置或可解释。  
- [ ] 通知回流能打开目标会话。  

### 12.4 体验与性能（建议指标）

| 指标 | 目标 |
|---|---|
| P0a 热键 → 本地捕获完成（中位） | ≤ 1.0s（1080p 级窗口） |
| P0a 热键 → 会话可见卡片（中位，本机） | ≤ 1.5s |
| P0b 文本硬顶 | 有上限且 UI 标明 truncated |
| 权限拒绝可恢复 | 授权后下一次热键无需重启（若系统要求重启则文案写明） |

### 12.5 验收场景抽样

1. **VS Code / Cursor 报错长日志**：P0a 验证截图投递；P0b 再验证可读文本提取。  
2. **Safari / Chrome 长文滚动**：P0b 验证 AX 可读文本，并仅在实际可达时标记 offscreen。  
3. **预览 PDF / 设计工具**：允许弱文本或无文本降级；OCR 放 P1。  
4. **双显示器**：仅 frontmost 窗。  
5. **Peer 自己在前台**：提示或安全行为，不误捕获敏感设置页。  
6. **无障碍权限关**：P0b 降级路径。  
7. **屏幕录制关**：P0a 授权引导路径。  
8. **destination 指定会话**：P1 验证投递不串会话。  

### 12.6 文档验收（本知识库）

- [x] 文档位于 `design/product/`  
- [x] 含一句话定义  
- [x] 含验收标准章节  
- [x] 覆盖 scrolled offscreen / 屏外文本，但不把它作为全应用 P0 承诺  
- [x] 覆盖前台窗口、视觉+文本、热键、destination、音效、权限隐私、非目标与 P0a/P0b/P1/P2 分期  

---

## 13. 风险与开放问题

| ID | 问题 | 影响 | 建议 |
|---|---|---|---|
| Q1 | 双 `⌘` 热键在技术上是否稳定？ | 默认键位 | **状态更新（2026-07-30，用户决策）：目标键位定为左右 ⌘ 同按，但暂缓开发、功能不外露，待开发者账号申请完成后再实施**。技术结论：① Electron `globalShortcut` 层不可行（accelerator conversion failure，已实测）；② 原生路径可行性已初步验证——NSEvent global monitor + 设备位掩码（左 ⌘ 0x08 / 右 ⌘ 0x10）探针已编译通过（scratch/appshot-spike/s6-doublecmd.swift），实测确认无 Accessibility 权限时 TRUSTED=false 监听不生效；左右同按检测的真机实测因决策中止未做。**过渡期无全局热键占用**（`⌘⇧A` 已解除）。详见拆解文档 §0.1 |
| Q2 | 虚拟列表 offscreen 文本承诺如何对外表述？ | 预期管理 | 用「尽量 / 视应用可访问性」避免绝对化 |
| Q3 | 捕获后是否自动 invoke 模型？ | 打扰与费用 | P0 默认否 |
| Q4 | Appshot 是否算用户消息还是系统附件？ | 历史渲染 / 计费 | 建议用户消息复合气泡 |
| Q5 | 与系统截图快捷键心智冲突 | 教育成本 | 设置说明对比「系统截图 vs Appshot」 |
| Q6 | 外部浏览器是否用 AX 还是未来接 L2 | 文本质量 | P0 AX；P2 可选受控 browser 文本增强 |
| Q7 | Windows 权限模型不同 | 跨平台 | 文档分期，不阻塞 macOS P0 |

---

## 14. 实现线索（仅供研发对照，非本轮交付）

> 本知识库不落代码。以下为与现有架构的挂载点，便于后续开 issue。

1. **复用** `computer-use-capability-ladder.md` 的 Observation / artifact / 权限分轨思想。  
2. **新建** Desktop 主进程 `appshot` 服务：P0a 先完成 resolve frontmost → capture window image → emit payload；P0b 再加入 extract AX text。  
3. **会话侧**扩展 attachment 类型或 message part：`appshot`。  
4. **设置** Integrations 导航项与快捷键注册表项。  
5. **不要**把实现塞进 `browser:capture-page`；对象模型不同。  

---

## 15. 总结

Peer 的 Appshots 应对齐 ChatGPT 的核心体验——**热键捕获前台窗口，把「看见的画面」先可靠交给 Agent，并在系统可访问性允许时补充可读文本**——同时坚持 Peer 自己的边界：

- 只读上下文，不借机拿到操控权；  
- 权限与隐私分轨、可解释；  
- 与内嵌 Browser 截图、Computer Use L3 动作清晰分层；  
- P0a 先打通截图投递闭环，P0b 再增强 AX 文本，P1 再做 OCR、多入口、指定会话与敏感窗口策略。

**产品一句话回顾**：Appshots 让用户在任何应用里按一下键，就把当前窗口的视觉上下文，以及可访问时的文本上下文，安全地交给 Peer。
