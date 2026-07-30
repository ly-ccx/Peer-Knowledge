# 内嵌 Browser 密码管理与自动填充架构

创建时间：2026-07-28
最后更新：2026-07-28
状态：Proposed / 实施前基线
关联代码仓：`peer_agent`（Desktop 内嵌 Browser + 本地 Credential Helper）

## 1. 决策摘要

Peer Desktop **要做** Password manager 与表单 Autofill，作为内嵌 Browser 的**用户面凭据能力**，与 Codex 菜单中的 **Passwords and autofill** 对齐产品意图，但采用更严的 Agent 边界与存储治理。

核心判断：

| 能力 | 首期 | 说明 |
|---|---|---|
| 用户密码库（增删改查） | **做** | 按 origin / 用户名条目管理 |
| 登录表单自动填充与保存提示 | **做** | 仅用户可见 Browser；需用户手势或明确确认策略 |
| 从系统浏览器**导入密码** | **可选 Phase 2** | 与 Cookie「站点会话导入」分轨；不得绑成 “cookies and passwords” 一键混导 |
| 联系人 / 地址 / 银行卡 autofill | **暂缓** | 单独产品与合规评估 |
| Passkey / WebAuthn 私钥 | **不做** | 不可导出；走平台 authenticator |
| **Agent 读取或填写密码** | **默认禁止** | 不投影为 `browser_*` / `computer_*` 工具；无「把密码交给模型」通道 |

与既有能力的关系：

- **站点会话导入**（Cookie）仍只负责登录会话复制，见 `embedded-browser-session-import.md`。
- **密码库**是独立凭据系统，存储与解密复用 / 扩展 ADR 0001 Credential Vault 方向（签名 Helper、失败关闭、无明文回退）。
- **Computer Use / browser_*** 可操作已填充后的 DOM，但不得枚举密码库或索取 password 明文。

## 2. 背景

此前产品面文档将 Password manager 标为「不做」，以控制密钥面。对照 Codex 内嵌浏览器后，用户明确要求补齐密码管理与自动填充。同时：

1. Cookie 导入不能代替「尚未登录、需账号密码」场景；
2. 用户已习惯系统浏览器 / Codex 的保存与填充；
3. 若把密码导入塞进会话导入管线，会破坏 Cookie 管线的最小权限叙事。

因此改为：**独立建设密码库 + autofill**，并修正相关文档边界。

## 3. 目标

1. 用户可在 Peer Browser 中保存、查看（受保护）、编辑、删除登录条目。
2. 在密码字段获得焦点或提交登录表单时，提供安全的自动填充 / 保存提示。
3. 密码明文仅在受控本地路径短暂出现：Helper / main 解密 → 注入到目标 webview 的密码输入框；不进 renderer 业务状态机的可序列化 store、不进模型上下文、不进 Evidence 正文、不进日志。
4. 与 Cookie 会话导入、Browser 设置菜单、PermissionGrant 主链一致、可审计。
5. 默认 Agent 无法列出或读取密码库。

## 4. 非目标（首期）

- 云同步密码库、家庭共享、跨设备端到端同步协议；
- 将密码导出为明文 CSV 默认开启（若未来支持，须单独强确认 + 本地文件 + 审计）；
- 支付卡、联系人、地址自动填充；
- 导入 Passkey / 平台密钥；
- Agent 自动注册账号、自动改密、自动过验证码；
- 用密码库替代系统 Keychain 中的 LLM API Key（那是 ADR 0001 另一条 vault 用途）。

## 5. 与 Codex 对照

| 维度 | Codex（观察） | Peer（本文） |
|---|---|---|
| 菜单 | Passwords and autofill → Password manager / Contact info | Password manager；Contact **暂缓** |
| 导入 | Import cookies **and passwords** 打包 | Cookie 导入与密码导入 **分入口、分管线**；首期可只做库内保存 + 可选后续「仅导入密码」 |
| 存储 | 浏览器身份面的一部分 | 独立 Password Vault；不与 `persist:peer-browser` Cookie 库混存明文 |
| Agent | 更强网页登录闭环 | **用户面优先**；Agent 默认零密码 API |
| 命名 | cookies and passwords | 会话导入 ≠ 密码导入；密码能力称 **Password manager / Autofill** |

## 6. 概念模型

```ts
type PasswordEntryId = string; // 本地 UUID

type PasswordEntryMeta = {
  id: PasswordEntryId;
  origin: string;          // https://example.com 规范化 origin
  originDisplay: string;
  username: string;        // 可进 UI 列表；非密钥
  createdAt: string;
  updatedAt: string;
  lastUsedAt?: string;
  // 无 password 字段
};

type PasswordSecret = {
  password: SecretBytes;   // 仅 Helper/main 内存
};
```

- **Meta** 可存在 Desktop 本地元数据库（或 vault 旁路索引），供列表与匹配。
- **Secret** 仅 vault 密文；解密后一次性使用。
- 匹配键：优先 `origin` 精确匹配；可选 eTLD+1 回退须用户设置开启且 UI 明示。

## 7. 存储与信任边界

### 7.1 存储

```text
Password Meta Store（无密钥）
  - entry id, origin, username, timestamps

Password Vault（密文）
  - 经签名本地 Helper / OS 保护密钥加密
  - 与 LLM API Key vault 逻辑隔离（不同 key purpose / 命名空间）
```

原则对齐 ADR 0001：

- 签名 Helper 最小协议；
- 失败关闭，禁止明文回退；
- Desktop 与未来 CLI 若共享，须同一 Helper 身份，而非复制解密实现。

### 7.2 信任边界

```text
用户手势（点击填充 / 确认保存）
  → Desktop main: PasswordAutofillCoordinator
    → Permission / 本地策略检查
    → Helper: unlock + decrypt one entry
    → main: 向指定 conversation 的 browserTab webContents 注入
    → 立即丢弃明文
```

禁止：

- preload 向任意页面暴露 `listPasswords()`；
- 页面 JS 读取 Peer 密码库；
- 把密码写入 `sessionStorage` 供 Agent 再读；
- 在 chat / tool result 中回传 password。

### 7.3 注入方式

优先顺序：

1. **Main 对 guest webview 的受控输入事件 / 表单填充 API**（类 `browser_type` 但专用、短路径、不记入模型可见 tool log 的 secret 字段）；
2. 避免 `executeJavaScript('input.value = ...')` 把明文写进可被页面其他脚本长期观察的路径；若必须 DOM 赋值，应在文档中标明风险并限制仅 password input。

填充完成后：

- 可触发 `input`/`change` 事件以满足站点框架；
- Evidence 仅记录：`password_autofill_applied`、origin、entryId、tabId、结果状态——**无 username 可选，默认无 password**。

## 8. Autofill 产品行为

### 8.1 保存

当用户在 Peer Browser 提交或成功登录类表单时：

1. 检测 username + password 字段（启发式 + 标准 autocomplete 属性）；
2. 弹出 **非模态** 保存条：保存 / 从不（按 origin）/ 关闭；
3. 用户确认后写入 vault；
4. 同源同 username 已存在则提示更新。

### 8.2 填充

1. 密码框 focus 或表单出现时，main/渲染层展示建议条（非页面劫持广告）；
2. 用户选择条目后解密并注入；
3. 可选：Touch ID / 系统鉴权（macOS）后解锁 vault（策略可配置：会话解锁时长）。

### 8.3 管理 UI

- 菜单：Passwords and autofill → **Password manager**
- 能力：搜索 origin/username、查看（需解锁）、复制密码（需解锁 + 短时剪贴板）、编辑、删除
- 复制到剪贴板：默认 30–60s 后清除（若平台允许）

## 9. Agent 与权限边界（硬约束）

### 9.1 默认禁止

下列能力 **不得** 进入 Runtime Projection / tool schema：

- `list_password_entries` 含可到明文的路径；
- `get_password` / `autofill_password` 供模型调用；
- 在 `browser_type` 参数中由模型传入「从密码库取密」的隐式引用若会导致模型侧可见明文。

### 9.2 允许的间接路径

- 用户自己填充后，Agent 使用普通 `browser_click` 提交表单（此时密码已在 DOM，属页面态，不是 vault API）；
- 用户明确开启的未来「Agent 可请求填充」能力必须：
  - 独立 PermissionGrant；
  - 每次或每 origin 确认；
  - 模型只见 entryId + origin + username，不见 password；
  - 注入仍在 main 完成。

### 9.3 与 browser_type 的关系

Agent 仍可 `browser_type` 用户在对话中**主动提供**的密码（用户粘贴进聊天）——这是用户自担风险的文本，不是密码库泄露。产品应提示：不要在聊天中粘贴密码，改用 Password manager。

## 10. 与站点会话导入的分轨

| | Cookie 站点会话导入 | 密码管理 |
|---|---|---|
| 对象 | Cookie | 账号密码条目 |
| 入口 | 导入站点会话 | Password manager / 保存提示 |
| 写目标 | `persist:peer-browser` Cookie Store | Password Vault |
| 是否进 Agent 工具 | 否 | 否（默认） |
| 是否可与 Codex 同名打包 | 否，禁止 cookies and passwords 混入口 | 否 |

Phase 2「从 Chrome 导入密码」若做：

- 独立向导与确认；
- 只读密码 DB + OS crypt；
- 不修改「会话导入」文档的 Cookie 范围；
- 仍不自动授权 Agent。

## 11. 安全要求

1. 静态分析 / 测试：日志、Evidence、analytics 不含 password 明文；
2. 崩溃报告脱敏；
3. vault 解锁失败可重试，不可降级明文文件；
4. 卸载 / 清除浏览数据时：Cookie 与密码库清除策略**分开勾选**（避免误删密码库）；
5. 多用户 OS 账户隔离依赖系统用户目录权限。

## 12. 分期

### Phase 0

- 本架构 + 产品面菜单更正；
- Meta schema、Vault namespace、Evidence 事件名冻结。

### Phase 1（MVP）

- 手动添加 / 编辑 / 删除条目；
- 登录表单保存提示 + 用户选择填充；
- Password manager 列表页；
- 无 Agent API。

### Phase 2

- 从 Chromium 系浏览器导入密码（可选）；
- 系统生物识别解锁；
- 剪贴板自动清除。

### Phase 3（需单独产品决策）

- Contact / 地址 autofill；
- 受控的 Agent 请求填充（强确认）。

## 13. 验收标准

- [ ] 文档与菜单存在 Password manager 入口描述
- [ ] 架构明确 Agent 默认不可读密码库
- [ ] 密码与 Cookie 导入分轨，无 “Import cookies and passwords” 作为 Peer 功能名
- [ ] 明文路径仅 Helper/main/注入，不进模型上下文
- [ ] 保存 / 填充需用户可见确认或等价用户手势策略（产品可配置项写明默认）
- [ ] 与 ADR 0001 失败关闭原则一致

## 14. 关联文档

- `design/product/embedded-browser-surface.md` — 菜单与设置
- `knowledge/architecture/embedded-browser-session-import.md` — Cookie 会话导入（分轨）
- `knowledge/decisions/0001-cross-platform-credential-vault.md` — Helper / Vault
- `knowledge/architecture/computer-use-capability-ladder.md` — 网页操控；密码不进动作面
- `knowledge/decisions/40-embedded-browser-and-agent-control.md`
- `knowledge/decisions/46-conversation-bound-browser-tabs.md`

## 15. 后续 ADR（实现前）

1. Password Vault key purpose 与 LLM vault 隔离；
2. 表单检测与保存提示 UX；
3. webview 注入实现与页面脚本威胁模型；
4. （可选）Chromium 密码 DB 导入适配器；
5. （可选）Agent 请求填充的 Permission 模型。
