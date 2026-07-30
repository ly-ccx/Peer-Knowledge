# macOS 完全磁盘访问：开屏检测与设置下方拖拽浮窗（存档）

创建时间：2026-07-30  
最后更新：2026-07-30  
状态：**功能暂存档，开屏检测已关闭**  
代码仓：`peer_agent`（`/Users/liangyin/Documents/DEV/github/peer_agent`）  
分支参考：`dev/0.0.1`

---

## 1. 产品决策（当前）

1. **开屏 / 冷启动不再自动检测、不再弹完全磁盘访问权限门。**
2. **等 Apple 开发者账号申请完成**，具备正式签名 / 公证 / 分发条件后，再决定是否重新打开开屏检测。
3. 现有实现代码**保留在仓库**，不删除；仅通过挂载开关关掉开屏入口。
4. 导入向导内的权限引导（Session Import）是否保留二次确认，不在本次关闭范围内；本次只关「打开 App 就弹」的启动门。

关闭方式（代码）：

- 文件：`apps/desktop/renderer/src/App.tsx`
- 写法：`{false && <FullDiskAccessStartupGate enabled={showMainShell} isZh={isZh} />}`
- 注释标明：开发者账号就绪后再开；实现文件与知识库文档路径。

---

## 2. 目标回顾

用户要的不是「Chrome Cookie 导入专用提示」，而是：

- Agent 在 macOS 上**必需**的系统权限（当前聚焦 **Full Disk Access**）
- 打开 App 时检测；不通过则弹窗引导
- 列表**不会自动出现 App**（macOS 设计如此），需要把 App 拖进「完全磁盘访问」列表
- 交互参考开源 [AskForPermission](https://github.com/riko2chen/AskForPermission)：设置页下方有可拖 LOGO 浮条

后续踩坑：一度把探测绑在 Chrome/导入 preflight 上，导致 Chromium 可读时 `ready=true` 把启动门短路；已纠正为「Agent 必需权限」语义。

---

## 3. 已实现到什么程度

### 3.1 通用启动权限探测（不绑 Chrome）

| 项 | 说明 |
|---|---|
| 文件 | `apps/desktop/electron/main/startup-os-permissions.mjs` |
| IPC | `os:startup-permissions` |
| preload | `getStartupOsPermissions()` |
| 语义 | 探测 TCC 保护目录只读 `readdir`；`EPERM/EACCES` → `blocked` |
| 与导入解耦 | 不依赖 Chrome 是否安装；文案为「Agent 必需」 |

相关提交（节选）：`42788a8` 等。

### 3.2 启动权限门 UI

| 项 | 说明 |
|---|---|
| 文件 | `apps/desktop/renderer/src/app/components/FullDiskAccessStartupGate.tsx` |
| 渲染 | `createPortal` 到 `document.body`（避免 Overlay render-prop / hooks 坑） |
| 行为 | 主壳就绪后 preflight；回前台 `visibilitychange` / `focus` 自动重检 |
| 操作 | 「在系统设置中完成」、品牌 LOGO 可拖、重新检测 / 稍后 |
| 已去掉 | 「在 Finder 中显示 App」 |
| **当前** | **App 层 `false &&` 关闭挂载，冷启动不弹** |

### 3.3 同步拖拽进系统设置列表

| 项 | 说明 |
|---|---|
| 主进程 | `browser:start-app-drag` → `webContents.startDrag({ file, icon })` |
| 关键约束 | 必须在 **`dragstart` 同步路径**里调用；preload 用 **`sendSync`** |
| 反例 | 异步 `send` + `await getFileIcon` → 系统设置接不住，表现为「拖了没反应」 |
| 性能 | 拖拽图标缓存并缩到约 48px；拖拽期间暂停窗口跟随，减轻卡顿 |

相关提交：`618ec9c`、`d060b90` 等。

### 3.4 设置下方 always-on-top 拖拽浮窗

| 项 | 说明 |
|---|---|
| 文件 | `apps/desktop/electron/main/full-disk-access-drag-float.mjs` |
| 触发 | 打开 `browser:open-full-disk-access-settings` 后 show 浮窗 |
| 形态 | 无边框、透明、`alwaysOnTop`、底部 LOGO 条 |
| LOGO | 优先 data URL（sandbox `data:` HTML 下 `file://` 易裂图） |
| 打包坑 | `workspaceRoot === null` 时禁止 `path.join(null, …)`，否则 `Received null` |

### 3.5 浮窗贴系统设置窗口（进行中，未完美）

| 项 | 说明 |
|---|---|
| 读窗 | 优先 `/usr/bin/swift` + `CGWindowList`（不依赖辅助功能）；备选 `/usr/bin/osascript` System Events |
| 贴边策略（最新） | 贴设置窗 **底内侧约 4px**（盖住列表 `+ / -` 一带）；失败则贴主窗底，避免贴屏幕最底 |
| 重试 | 打开设置后多次 `showFloat`（约 250/500/900/1500/2400ms） |
| 跟随 | 低频跟随设置窗移动；**拖拽中暂停跟随** |

**已知未闭环：**

1. **贴边仍可能「接近但还有空隙」**（用户最后反馈）。多屏 / 坐标换算 / 辅助功能未授权 / 设置窗动画时序仍可能影响。
2. **拖拽跟手**已改善，但不能保证所有机器上都与原生 App 完全一致。
3. **开源 AskForPermission** 是原生 AppKit 浮层；我们是 Electron 小窗近似，不是 1:1 像素复刻。
4. **未正式签名/公证**时，TCC 列表里可能出现开发态 / 多份 Peer Agent 路径，体验会乱；这也是「等开发者账号」的原因之一。

相关提交链（新→旧，节选）：

```text
2ee6c7c fix(desktop): glue FDA float to System Settings bottom edge
71908f5 fix(desktop): keep FDA float glued to System Settings bottom
d060b90 fix(desktop): tighten FDA float attach and smooth drag icon
c98dfe1 fix(desktop): pin FDA drag float to System Settings bottom band
f0a50e0 fix(desktop): attach FDA drag float under System Settings window
4656d46 fix(desktop): fix FDA drag float logo null path crash
599a833 feat(desktop): always-on-top Full Disk Access drag float under Settings
618ec9c fix(desktop): make Full Disk Access app-drag synchronous and drop Finder button
42788a8 fix(desktop): detect Agent-required Full Disk Access on launch
```

---

## 4. 关键代码地图

```text
apps/desktop/renderer/src/App.tsx
  └─ FullDiskAccessStartupGate 挂载点（当前 false && 关闭）

apps/desktop/renderer/src/app/components/FullDiskAccessStartupGate.tsx
  └─ 启动门 UI + 回前台重检 + 调 openFullDiskAccessSettings / startAppDrag

apps/desktop/electron/main/startup-os-permissions.mjs
  └─ Agent 必需 FDA 探测

apps/desktop/electron/main/session-import/import-permission-preflight.mjs
  └─ 导入 preflight + resolveFullDiskAccessDragTarget / openFullDiskAccessSettings

apps/desktop/electron/main/full-disk-access-drag-float.mjs
  └─ 设置下方 always-on-top 拖拽浮窗

apps/desktop/electron/main/main.mjs
  └─ IPC：os:startup-permissions / open-full-disk-access-settings / start-app-drag / hide-fda-drag-float*

apps/desktop/electron/preload/preload.cjs
  └─ getStartupOsPermissions / openFullDiskAccessSettings / startAppDrag(sendSync) / hideFdaDragFloat
```

---

## 5. 如何重新打开开屏检测（开发者账号就绪后）

1. 确认 **签名 + 公证 + 安装路径稳定**（尽量固定为正式 `/Applications/Peer Agent.app`，避免多份 bundle 抢 TCC）。
2. 改 `App.tsx`：去掉 `{false && ...}`，恢复  
   `<FullDiskAccessStartupGate enabled={showMainShell} isZh={isZh} />`
3. 更新 `fullDiskAccessStartupGate.test.ts` 中「关闭挂载」断言。
4. 真机验收清单：
   - 冷启动缺 FDA → 弹启动门（文案不绑 Chrome）
   - 点「在系统设置中完成」→ 打开 Full Disk Access + 底部浮窗
   - 浮窗贴设置窗底（空隙可接受）
   - LOGO 拖进列表跟手，列表可打开开关
   - 完全退出再开 → 自动重检通过后门关闭
5. 若贴边/拖拽仍差，优先查：
   - 是否读到 System Settings bounds（swift / osascript）
   - `startDrag` 是否仍在 `dragstart` 同步路径
   - 当前运行的是否为最新 dist，而非旧 `/Applications` 包

---

## 6. 验证与打包备注

- 开发期多次只打 `dist-electron/mac-arm64/Peer Agent.app`，**不默认覆盖** `/Applications`。
- 用户若从 `/Applications` 或旧 DMG 启动，会看不到最新行为。
- 相关单测目录：
  - `fullDiskAccessStartupGate.test.ts`
  - `startup-os-permissions.test.mjs`
  - `full-disk-access-drag-float.test.mjs`
  - `start-app-drag.sync.test.mjs`

---

## 7. 非目标 / 明确不做（本阶段）

- 不在未签名阶段强推开屏拦截影响日常开发。
- 不把 Accessibility / 屏幕录制等权限全家桶一次做完。
- 不嵌 AskForPermission Swift 包进 Electron。
- 不强制用户必须用 Chrome；FDA 是 Agent 本机数据能力的前置，不是浏览器绑定。

---

## 8. 一句话存档结论

**链路主体（探测、启动门 UI、同步拖 App 进 TCC 列表、设置下方浮窗）已在 `peer_agent` 落地并迭代多轮；贴边与拖拽手感仍有收尾空间。按产品决策，开屏检测先关闭，待开发者账号与正式签名就绪后再打开验收。**
