# 内嵌 Browser 产品面设计（对照 Codex）

创建时间：2026-07-28
最后更新：2026-07-28
状态：Proposed / 产品设计基线
关联代码仓：`peer_agent`（`apps/desktop/renderer` Workbench BrowserView）

## 1. 背景与目标

Codex 内嵌浏览器已提供接近完整浏览器的菜单面：页内查找、打印、缩放、设备工具栏、截图、**Import cookies and passwords**、密码管理/自动填充、下载、清理浏览数据、浏览器设置。Peer 当前有可见 Browser、会话绑定标签、`browser_*` 控制与站点会话导入架构，并需补齐统一的 Browser 产品面（菜单 / 设置 / 数据治理 / **Password manager**）。

本文档约定 Peer Desktop 内嵌 Browser 的用户可见能力面，并明确与 Codex 的对齐项与分叉项。安全与实现细节分别以：

- `knowledge/architecture/embedded-browser-session-import.md`（站点 Cookie 导入）
- `knowledge/architecture/browser-password-manager-autofill.md`（密码库与自动填充）
- `knowledge/architecture/computer-use-capability-ladder.md`（Browser / OS 操控阶梯）
- `knowledge/architecture/visible-browser-readiness-handshake.md`（可见 Browser 就绪握手）
- ADR 40 / 46（载体、控制桥、conversation 绑定）

为准；本文不重复底层协议，只定义**产品信息架构、菜单、设置与分期**。

## 2. 产品定位

Peer 内嵌 Browser 是：

1. **用户可见的网页工作台**（Workbench 的 Browser 视图）；
2. **Agent `browser_*` 的默认执行与验收环境**（可见、可中止、可留证）；
3. **共享的 Peer Browser Profile**（`persist:peer-browser` 全局登录态）；
4. **用户面 Password manager / 登录表单 Autofill** 的载体（密码明文不进模型）。

它**不是**：

- 完整替代系统 Chrome 的日常浏览器；
- 云同步密码库或家庭共享保险库（首期本地）；
- 无头测试浏览器的替身（无头不能冒充可见验收）；
- Agent 的默认可调密码 API。

## 3. 与 Codex 菜单对照

对照 Codex 溢出菜单（用户截图）：

| Codex 菜单项 | Peer 立场 | 分期 | 说明 |
|---|---|---|---|
| Find in page | **对齐** | P1 | 页内查找，用户操作；可不投影给 Agent |
| Print | **对齐** | P2 | 系统打印对话框 |
| Zoom（± / 重置） | **对齐** | P1 | 每 tab 或全局缩放，需持久化策略 |
| Show device toolbar | **可选对齐** | P2 | 响应式/设备模拟；非 Agent 主路径 |
| Take a screenshot | **对齐（双入口）** | P0–P1 | 用户菜单截图 + 已有 `browser_screenshot` 工具 |
| **Import cookies and passwords...** | **分叉** | — | Peer **拆成两入口**：导入站点会话（Cookie）与（可选 Phase 2）导入密码；**禁止**打包成 cookies and passwords |
| Passwords and autofill → Password manager | **对齐（用户面）** | P1 | 内置 Password manager；架构见 browser-password-manager-autofill |
| Passwords and autofill → Contact info | **暂缓** | — | 联系人自动填充不在首期 |
| Downloads | **对齐** | P1 | 下载列表与打开目录 |
| Clear browsing data | **对齐** | P0–P1 | 分级清理；Cookie 与密码库分项勾选 |
| Browser settings | **对齐** | P1 | 设置页聚合入口，而非散落对话框 |

### 3.1 关键分叉：凭据导入与密码库

| | Codex | Peer |
|---|---|---|
| 会话导入文案 | Import **cookies and passwords** | Import **site sessions** / 导入站点会话（**仅 Cookie**） |
| 密码库 | 内置 Password manager + autofill | **做**用户面 Password manager + 登录表单 autofill |
| 密码是否与 Cookie 一键混导 | 菜单级打包 | **否**；分管线、分确认 |
| Contact / 支付资料 | 可见 Contact info | **首期不做** |
| Agent | 更易形成「可登录 + 可填密」闭环 | Cookie 导入 ≠ 授权 Agent；**密码默认不进 Agent 工具** |
| 安全叙事 | 完整浏览器身份面 | Cookie bearer 复制 + 独立 Password Vault；明文不进模型 |

产品文案：

- 会话导入避免「导入身份」「同步账号密码」；
- 密码能力使用 **Password manager / 自动填充**，不与会话导入混名。

## 4. 信息架构

### 4.1 壳层（已有 / 保持）

- 多标签（conversation 绑定，ADR 46）
- 前进 / 后退 / 刷新
- 地址栏
- Workbench 展开与 Browser 就绪握手（见 visible-browser-readiness-handshake）

### 4.2 溢出菜单（⋯）结构

```text
查找与阅读
  - 在页面中查找
  - 打印…                    （P2）
  - 缩放  [ − | 100% | + | 重置 ]

开发与取证
  - 设备工具栏               （P2）
  - 截取页面

会话与站点
  - 导入站点会话…            （Cookie；见 session-import 架构）
  - 清除此站点数据…

密码与自动填充
  - Password manager…
  - （暂缓）Contact info

浏览器数据
  - 下载
  - 清除浏览数据…
  - 浏览器设置…
```

**不出现**于 Peer 菜单：

- Import cookies and passwords（打包文案）
- 将「导入密码」与「导入站点会话」合并为一项

**出现**于 Peer 菜单：

- Password manager（用户面）
- 导入站点会话（仅 Cookie）

### 4.3 浏览器设置页（Browser settings）分组

| 分组 | 内容 |
|---|---|
| 外观与阅读 | 默认缩放、是否显示设备工具栏偏好 |
| 站点会话 | 导入站点会话入口、已导入站点列表（仅 domain + 时间，无 Cookie value）、清除单站数据 |
| 密码与自动填充 | Password manager 入口、是否提示保存密码、解锁策略说明；**不**与 Cookie 导入混入口 |
| 隐私与数据 | 清除 Cookie/缓存/下载记录/**密码库**分项勾选；说明全局 Profile 语义 |
| 下载 | 默认下载目录、打开下载文件夹 |
| 关于 Agent | 导入会话与密码库均不会自动授权 Agent；密码默认不进工具面 |

### 4.4 空状态 / 未登录提示

- Browser 新标签或导航到需登录站点时，可展示次要 CTA：**从系统浏览器导入此站点登录状态**
- CTA 只打开导入向导，不后台扫描 Profile
- 明确「不会导入密码」

## 5. 交互与状态

### 5.1 导入站点会话

- 入口：溢出菜单、浏览器设置、空状态 CTA
- 流程、权限、Helper、回滚：以 `embedded-browser-session-import.md` 为唯一权威
- 成功后可选：打开该站点并提示用户确认是否已登录（`cookies_applied` vs `session_verified`）

### 5.2 清除数据

分级（用户可选组合）：

1. **仅当前站点** Cookie + 可清的站点存储（优先）
2. **所有站点 Cookie**
3. **缓存**
4. **下载记录**（非文件本体，或可选删文件）

危险操作需确认。清除后相关标签可提示重新加载。

### 5.3 截图

| 入口 | 行为 |
|---|---|
| 用户菜单「截取页面」 | 截当前可见 tab → 保存到下载目录或工作区产物；可进 Evidence 仅当用户/任务需要 |
| Agent `browser_screenshot` | 既有工具链；目标必须是当前 conversation 可见 Browser；走 PermissionGrant + artifact |

两者共享底层 capture，**产品入口分离**，避免用户截图被默认送进模型上下文。

### 5.4 缩放

- 默认 100%
- 快捷键与菜单同步
- P1：按 origin 记忆缩放；全局默认在设置中

### 5.5 下载

- 下载开始时状态栏/Browser 内轻提示
- 「下载」面板：文件名、进度、打开文件/目录
- 默认目录可配置；敏感路径需注意权限展示

## 6. 与 Agent / Computer Use 的边界

1. **菜单能力默认是用户面**，不自动变成 `browser_*` / `computer_*` 工具。
2. 已有工具：`navigate` / `click` / `type` / `screenshot` / `read_dom` 等；扩展动作走 capability ladder，不把「导入会话」「清全部 Cookie」「列出密码库」做成模型默认可调工具。
3. **导入站点会话永不投影为 Agent 工具**。
4. **Password manager / autofill 默认不投影为 Agent 工具**；模型不得 `get_password`。
5. 可见 Browser 未就绪时：ensure → ready → execute；禁止用无头结果冒充可见验收。
6. 导入 Cookie 或用户填充密码后，页面可能处于已登录态；`browser_*` 授权 UI 应提示敏感站点风险。

## 7. 安全与隐私（产品层）

- Cookie value、密码明文、Keychain 材料不出现在 UI 列表明文区、日志、聊天与 Evidence 正文
- 设置中的「已导入站点」仅显示 eTLD+1、导入时间、可选 Cookie 数量区间
- Password manager 列表默认只显示 origin + username；查看/复制密码需解锁
- 不提供「导出 Cookie 文件」到聊天；密码导出若未来支持须单独强确认
- 清理时 Cookie / 缓存 / 密码库分项，防止误删密码库
- 会话导入是复制：来源浏览器退出登录不会自动同步

## 8. 分期与验收

### P0（与导入架构并行可感知）

- [ ] 溢出菜单骨架（即使部分项 disabled + 即将推出）
- [ ] 清除此站点数据
- [ ] 用户截图入口
- [ ] 导入站点会话入口文案与向导壳（实现可后置）
- [ ] Password manager 菜单入口（可先链到占位页）

### P1

- [ ] 在页面中查找
- [ ] 缩放
- [ ] 下载面板
- [ ] 清除浏览数据（多范围，含密码库分项）
- [ ] 浏览器设置页
- [ ] 导入向导完整打通（见 session-import 架构验收）
- [ ] Password manager MVP + 保存提示 + 用户选择填充（见 password-manager-autofill 架构）

### P2

- [ ] 打印
- [ ] 设备工具栏
- [ ] 缩放按站点记忆
- [ ] 下载目录高级策略
- [ ] （可选）从 Chromium 导入密码（独立向导，非 cookies and passwords 打包）

### 明确不在首期（除非单独 ADR）

- Contact / 支付卡 autofill 资料库
- 静默接管用户日常浏览器 Profile
- Agent 默认可读密码库或自动填密
- 与 Cookie 导入合并的 “Import cookies and passwords” 文案

### 验收抽样

- 中英文菜单完整、危险操作有确认
- 存在 Password manager 入口；会话导入文案仍为站点会话 / Cookie
- 无 Agent 工具可触发会话导入或读取密码明文
- 与 `embedded-browser-session-import.md`、`browser-password-manager-autofill.md` 无矛盾

## 9. 关联文档

- `knowledge/architecture/embedded-browser-session-import.md` — Cookie 导入管线
- `knowledge/architecture/browser-password-manager-autofill.md` — 密码库与 autofill
- `knowledge/architecture/computer-use-capability-ladder.md` — 操控能力阶梯
- `knowledge/architecture/visible-browser-readiness-handshake.md` — 面板自动展开与就绪
- `knowledge/decisions/40-embedded-browser-and-agent-control.md`
- `knowledge/decisions/46-conversation-bound-browser-tabs.md`
- `design/product/right-workbench-panel.md` — Workbench 承载 Browser 视图

## 10. 交付给代码仓的含义

实现落点（不在本知识库改代码）：

- `BrowserView` 工具栏溢出菜单
- 设置路由/面板（Desktop settings 或 Browser 内设置页）
- 复用 `session.fromPartition('persist:peer-browser')` 做清理与截图
- 导入向导调用未来的 SessionImportCoordinator（非 renderer 直读 Cookie DB）
- Password manager UI + Password Vault / Helper（见密码架构与 ADR 0001）
