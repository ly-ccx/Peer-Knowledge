# 内嵌 Browser 站点会话导入架构

创建时间：2026-07-28
最后更新：2026-07-28
状态：Proposed / 实施前基线
关联代码仓：`peer_agent`（本地 `/Users/liangyin/Documents/DEV/github/peer_agent`）

## 1. 决策摘要

Peer Agent Desktop 支持把用户在外部浏览器中明确选择的**站点 Cookie / 登录会话**一次性复制到内嵌 Browser 的持久 Session，使用户不必在同一站点重复登录。

本能力命名为“导入站点会话”，而不是“导入身份信息”或“迁移浏览器资料”。**这与 Codex 的 “Import cookies and passwords…” 打包入口不是同一条管线**：本文件只覆盖 **Cookie / 登录会话** 复制；**不**在本管线导入密码。Peer **另建**用户面 Password manager / autofill（见 `browser-password-manager-autofill.md`），与 Cookie 导入分入口、分存储、分确认。产品面菜单见 `design/product/embedded-browser-surface.md`。

Cookie 是可直接代表用户登录状态的 bearer credential，必须按高敏凭据治理：

- 用户从设置或 Browser 空状态页主动发起；
- 用户明确选择来源浏览器、Profile 与站点；
- 导入前展示范围与风险，用户必须逐次确认；
- 解密和明文流转只发生在签名本地 Helper、Desktop main process 与 Electron Cookie Store 内；
- renderer、模型上下文、日志、遥测与 Evidence 永不接触 Cookie value；
- 只写入 `persist:peer-browser`，不修改外部浏览器数据；
- 不导入密码、通行密钥、银行卡或整份浏览器 Profile；
- 不默认导入 localStorage、IndexedDB、Service Worker、Cache、扩展数据或浏览历史。

首期支持 macOS 上基于 Chromium 的浏览器；Firefox 作为后续独立适配器；Safari 因二进制存储、系统隐私和权限边界暂不支持。

## 2. 背景

内嵌 Browser 当前使用固定持久分区：

```text
persist:peer-browser
```

该分区由所有 conversation 和 browser tab 共享，因而登录态也是全局共享的。这符合浏览器产品语义：同一个 Peer Browser Profile 中打开同一站点时，应共享 Cookie 与登录状态。

当前用户如果已在 Chrome、Chromium、Edge、Brave 等外部浏览器登录，仍需在内嵌 Browser 重复完成密码、MFA 或 OAuth。站点会话导入可以降低摩擦，但如果直接复制整个 Profile、读取密码库或把 Cookie value 暴露给 renderer/Agent，会形成严重的凭据泄露和权限绕行风险。

因此，本设计只建立受控的“站点 Cookie 复制”管线，不做浏览器 Profile 克隆。

## 3. 目标

1. 用户能选择一个外部浏览器 Profile，并只导入一个或多个明确站点的有效 Cookie。
2. 导入成功后，`persist:peer-browser` 中对应站点可复用登录会话。
3. 整个过程中 Cookie value 不进入 renderer、模型上下文、日志、遥测或 Evidence。
4. 外部浏览器数据只读；导入失败不损坏来源 Cookie 数据库和 Peer Browser 原有登录态。
5. 权限请求有可解释原因，用户可以取消、重试和删除已导入站点会话。
6. 支持结果必须诚实：站点仍要求重新认证时，不伪报“身份导入成功”。

## 4. 非目标与硬边界

### 4.1 明确不导入

本能力不导入密码、通行密钥、银行卡或整份浏览器 Profile，也不读取或复制：

- 浏览器密码数据库、自动填充资料和支付资料；
- WebAuthn / Passkey 私钥、平台凭据和硬件密钥；
- 浏览器扩展、扩展私有存储和扩展注入状态；
- 浏览历史、书签、下载记录、打开的标签页；
- OAuth refresh token 文件、系统钥匙串中的非 Cookie 凭据；
- localStorage、sessionStorage、IndexedDB、Service Worker、Cache Storage；
- TLS 客户端证书及私钥；
- 整个 User Data / Profile 目录。

localStorage/IndexedDB 可能也是站点认证链路的一部分，但缺乏统一标准和安全的跨引擎导入契约，首期不支持。对依赖这些状态的站点，结果应是“Cookie 已复制但登录验证失败”，引导用户在内嵌 Browser 重新登录。

### 4.2 不承诺绕过站点安全

不尝试绕过：

- MFA、验证码、设备绑定和风险控制；
- 与浏览器指纹、TLS、IP、设备密钥绑定的会话；
- 企业策略、DRM、硬件认证或受保护内容限制；
- 服务端主动撤销、过期或轮换的 Cookie。

### 4.3 不提供 Agent 工具

会话导入是用户设置能力，不作为 `browser_*` 或 `computer_*` 工具投影给模型。Agent 不得自行枚举外部 Profile、选择站点、读取或发起 Cookie 导入。

### 4.4 与 Codex「Import cookies and passwords」及密码管理的边界

Codex 将 **Import cookies and passwords…** 与 **Passwords and autofill** 放在同一浏览器身份面。Peer **拆轨**：

| 维度 | Codex（产品观察） | Peer · 本文（Cookie 会话导入） | Peer · 密码能力（另文） |
|---|---|---|---|
| 对象 | Cookie + 密码打包 | **仅 Cookie / 登录会话** | 密码条目 + 登录 autofill |
| 入口名 | cookies and passwords | **导入站点会话** | Password manager |
| 存储 | 浏览器身份面 | `persist:peer-browser` Cookie | 独立 Password Vault |
| Agent | 强登录闭环 | 不投影为工具 | **默认不投影**；见密码架构 |
| Contact autofill | 有 | 无 | 暂缓 |

因此（**针对本 Cookie 管线**）：

1. 不得使用 “Import cookies and passwords” 作为 Peer 会话导入功能名；
2. 本管线实现与测试**不得**读取浏览器密码数据库或把密码写入 Cookie Store；
3. 密码管理 / autofill **不**通过扩展本文静默加入，而由 `browser-password-manager-autofill.md` 与后续 ADR 约束；
4. 可选的「从 Chrome 导入密码」若做，必须是**独立向导**，不得与本流程合并确认；
5. 菜单与设置以 `design/product/embedded-browser-surface.md` 为准：两入口并存、文案分清。

## 5. 支持矩阵

### 5.1 Phase 1：macOS Chromium 系

首期适配：

- Google Chrome；
- Chromium；
- Microsoft Edge；
- Brave Browser；
- 其他 Chromium 浏览器仅在路径、Local State、Cookie schema 和钥匙串服务名经显式适配后加入。

支持来源形态：

- 用户选择的具体 Profile；
- Profile 下 `Network/Cookies`（或兼容路径）数据库的只读快照；
- 由 Chromium OS crypt 保护、并能通过当前用户 Keychain 合法解密的 Cookie value。

不以“扫描到类似目录”自动宣布支持。每个 Browser Adapter 必须明确声明：bundle id、User Data 根目录、Profile 发现规则、Cookie 数据库路径、钥匙串服务名/账户名、支持的 schema 版本和测试版本。

### 5.2 Phase 2：Firefox

Firefox Cookie 数据通常位于 Profile 的 `cookies.sqlite`，存储与 Chromium 不同。Firefox 支持应作为独立 Adapter 实现和验收：

- 单独发现 Profile；
- 只读复制 SQLite/WAL 快照；
- 映射 Firefox Cookie 字段至统一模型；
- 不因为 Cookie value 可能是明文就降低权限或脱敏要求。

### 5.3 暂不支持 Safari

Safari 的 Cookie 二进制格式、容器路径和 macOS 隐私边界不同，还可能涉及 Full Disk Access 或系统容器保护。首期不请求宽泛系统权限来换取 Safari 导入。

在完成独立安全评审、签名/沙箱策略、系统版本兼容和合法访问路径前，UI 显示“不支持”，不得静默尝试读取。

### 5.4 Windows / Linux

本文聚焦 macOS。其他平台必须分别确认 Chromium OS crypt、系统凭据库、文件锁和安装路径，不能把 macOS 的 Keychain 流程直接复用为跨平台契约。

## 6. 核心数据模型

### 6.1 来源身份

```ts
type BrowserSource = {
  adapterId: string;          // chrome-macos / edge-macos / brave-macos ...
  browserName: string;
  bundleId: string;
  userDataRoot: string;       // 仅 main/helper 持有，不进入 Evidence
  profiles: BrowserProfileSummary[];
};

type BrowserProfileSummary = {
  profileId: string;          // 本地短期句柄，不是任意路径
  displayName: string;
  browserName: string;
  lastUsedAt?: string;
};
```

renderer 只能拿到适合显示的摘要和短期 `profileId`。任意文件路径、Keychain 查询参数和 SQLite 路径不由 renderer 提交。

### 6.2 站点范围

```ts
type SiteImportSelection = {
  profileId: string;
  registrableDomains: string[]; // eTLD+1，如 example.com
  includeSubdomains: boolean;
};
```

站点选择以 registrable domain（eTLD+1）为边界，使用 Public Suffix List 计算，禁止字符串后缀匹配。选择 `example.com` 不得误匹配 `notexample.com`。

默认包含该站点及其子域 Cookie，因为真实登录常分布在 `www`、`accounts`、`auth` 等子域；确认页必须列出实际涉及的 domain 和 Cookie 数量。用户可取消某个 domain，但不在普通 UI 中展示 Cookie value。

### 6.3 统一 Cookie 记录

```ts
type ImportableCookie = {
  name: string;
  value: SecretBytes;
  domain: string;
  hostOnly: boolean;
  path: string;
  secure: boolean;
  httpOnly: boolean;
  sameSite: 'unspecified' | 'no_restriction' | 'lax' | 'strict';
  expiresAt?: number;         // Unix seconds；缺失表示 session cookie
  sourcePort?: number;
  sourceScheme?: 'http' | 'https';
};
```

`SecretBytes` 只存在于 Helper/main 内存，不可序列化到通用 JSON 日志。Helper 协议应使用长度前缀二进制帧或受控 IPC，并对 debug/trace 做强制脱敏。

### 6.4 目标能力限制

Electron 41 `CookiesSetDetails` 可写：

- `url`、`name`、`value`；
- `domain`、`path`；
- `secure`、`httpOnly`；
- `expirationDate`；
- `sameSite`。

它不能完整表达 Chromium Cookie 数据库中的所有扩展属性，例如 partition key、priority、source scheme/port、SameParty 等。因此：

- 首期跳过 CHIPS / partitioned Cookie，结果中计入 `unsupported_attributes`；
- 不降级写成 unpartitioned Cookie，避免扩大授权范围；
- 无法无损映射的属性一律失败关闭，而不是猜测；
- 后续 Electron API 支持扩展字段后再单独启用。

## 7. 组件与信任边界

```text
Renderer（选择来源/Profile/站点；不见 secret）
  -> typed IPC
Desktop Main: SessionImportCoordinator
  -> PermissionReview / user confirmation
  -> Signed Session Import Helper
       -> discover profiles
       -> create read-only SQLite snapshot
       -> query selected domains only
       -> Keychain-authorized decrypt
       -> return secret records over private IPC
  -> validate + normalize + diff
  -> Electron session.fromPartition('persist:peer-browser').cookies.set(...)
  -> session.cookies.flushStore()
  -> verify metadata / optional site probe
  -> redacted result + Evidence
```

### 7.1 Renderer

负责：

- 展示浏览器/Profile 列表；
- 展示按站点聚合的 Cookie 数量、domain、有效期范围和风险说明；
- 接收用户选择与逐次确认；
- 展示导入、验证、部分成功和删除结果。

不得：

- 获取 Cookie value、加密 value、Keychain secret 或数据库路径；
- 自行访问浏览器 Profile 文件；
- 把 Cookie 内容放入 Redux/React state、localStorage 或崩溃报告。

### 7.2 SessionImportCoordinator（Desktop main）

是流程权威状态机，负责：

- 将短期 source/profile/site 句柄解析为允许的 Adapter 输入；
- 验证 PermissionGrant 与确认摘要；
- 启停 Helper，执行超时和取消；
- 验证 Cookie domain、期限、属性与大小；
- 生成目标 Cookie URL 并写入指定 partition；
- 维护导入事务和回滚材料；
- 产出无 secret 的结果与 Evidence。

### 7.3 签名本地 Helper

沿 ADR 0001 的“签名本地 Helper + 最小协议”方向实现，而不是让 renderer 或通用 Node 子进程直接查询 Keychain。

Helper 负责：

- 识别支持的浏览器和 Profile；
- 复制 Cookie SQLite 数据库以及必要的 `-wal`/`-shm` 到私有临时目录；
- 以只读方式查询用户已选 domain；
- 在 macOS 用户授权下访问对应浏览器 OS crypt Keychain 项并解密；
- 把标准化 Cookie 通过私有 IPC 交给 main；
- 尽快清零密钥和 Cookie value 内存，删除临时快照。

Helper 不负责选择站点、决定导入范围、写 Electron Cookie Store 或保留任何长期明文。

### 7.4 Electron Cookie Store

唯一目标是：

```ts
session.fromPartition('persist:peer-browser').cookies
```

导入影响 Peer Browser 全局 Profile，而不是单个 conversation/tab。确认页必须明确：“导入后，此站点登录状态将对所有 Peer Browser 标签和会话可用。”

## 8. 导入流程

### 8.1 用户入口

入口位于：

- Settings → Browser → Import site sessions；
- 或内嵌 Browser 未登录页面的“从浏览器导入登录状态”。

不可由网页内容、Agent tool call、模型建议按钮或后台启动自动触发系统权限。

### 8.2 流程状态机

```text
idle
 -> discovering_sources
 -> source_selected
 -> profile_selected
 -> scanning_site_metadata
 -> site_selected
 -> awaiting_confirmation
 -> reading_snapshot
 -> awaiting_os_authorization?（Keychain）
 -> decrypting
 -> validating
 -> applying
 -> flushing
 -> verifying
 -> completed | partially_completed | failed | cancelled
```

每个状态都可取消。取消后停止 Helper、删除临时快照、丢弃内存 secret；已经写入目标的部分 Cookie按事务策略回滚。

### 8.3 Profile 与站点发现

第一阶段只读取低敏元数据：浏览器名、Profile 显示名、Cookie domain 聚合和数量，不返回 Cookie name/value。

即使元数据扫描不需要解密，仍只在用户主动打开导入流程后执行，不做常驻后台扫描。

站点列表：

- 按 eTLD+1 聚合；
- 默认排除已过期 Cookie；
- 显示有效 Cookie 数、相关子域、最早/最晚过期时间；
- 支持搜索；
- 不显示 Cookie name，避免泄露认证实现细节。

### 8.4 确认

确认页至少展示：

- 来源浏览器与 Profile；
- 选中的 eTLD+1；
- 将涉及的实际 Cookie domain 与数量；
- 目标为 Peer Browser 全局 Profile；
- Cookie 可代表登录身份，导入后 Peer Browser 页面与被授权的 Browser automation 可在该登录态下操作；
- 不导入密码、通行密钥和其他浏览器资料；
- 可能触发 macOS Keychain 授权；
- 可稍后从 Peer Browser 删除该站点数据。

用户必须逐次确认；不提供“今后总是允许导入任何站点”的永久授权。

### 8.5 快照读取

禁止直接对外部浏览器正在使用的 SQLite 文件做长时间查询。Helper 应：

1. 验证路径位于已注册 Adapter 的 User Data root；
2. 打开前检查目标不是符号链接逃逸；
3. 将数据库与 WAL/SHM 复制到应用私有临时目录，或使用 SQLite backup API 创建一致快照；
4. 对快照只读查询；
5. 无论成功失败都删除快照。

不要求用户关闭浏览器作为默认路径；如果无法创建一致快照，明确提示用户关闭来源浏览器后重试。

### 8.6 解密

- 仅解密用户所选站点、未过期且可映射的 Cookie；
- Keychain 查询由签名 Helper 发起；
- 系统拒绝、钥匙串锁定、服务名不匹配或密文版本未知时失败关闭；
- 禁止把密文当明文、使用硬编码默认密钥或落盘明文重试；
- Helper 不返回 OS crypt 主密钥，只返回本次所需的标准化 Cookie；
- 导入结束立即释放解密材料。

### 8.7 验证与过滤

main 在写入前验证：

- domain 属于用户选择的 eTLD+1；
- domain/path/name/value 满足 Cookie 和 Electron 限制；
- `Secure` Cookie 只能构造 `https://` URL；
- `SameSite=None` 必须保持 Secure；
- 过期 Cookie 跳过；
- 不可表达的 partitioned/扩展 Cookie 跳过；
- 单 Cookie、单站点总数和总字节设置上限；
- 控制字符、非法域、Public Suffix Cookie 一律拒绝。

目标 URL 建议：

```text
scheme = secure ? https : sourceScheme ?? https
host = hostOnly ? exactHost : normalizedDomainWithoutLeadingDot
url = `${scheme}://${host}${pathOrSlash}`
```

禁止通过导航到目标站点并执行 `document.cookie` 注入，因为该路径无法写 HttpOnly，且会把 secret 暴露给 renderer/page JavaScript。

## 9. 写入事务与冲突策略

### 9.1 默认冲突策略

默认使用“来源覆盖同键 Cookie”，Cookie identity 为目标引擎可表达的：

```text
name + domain + path
```

写入前记录目标 Store 中同站点 Cookie 的内存快照，用于失败回滚。快照只在 main 内存存在，不进入 Evidence。

确认页展示：

- 新增数量；
- 将覆盖数量；
- 跳过数量；
- 不显示 name/value。

### 9.2 原子性

Electron Cookie API 是逐条 `set`，没有原生批量事务。因此 Coordinator 提供补偿事务：

1. 获取目标站点现有 Cookie 内存快照；
2. 逐条写入并记录成功项；
3. 任一硬失败触发回滚：删除本次新增/覆盖项，恢复旧快照；
4. `flushStore()`；
5. 重新读取 metadata 验证数量与属性；
6. 回滚失败时标记 `rollback_failed`，提示用户清除该站点数据并重新登录。

“不支持属性/已过期”属于预先过滤，可产生部分成功；解密失败、目标写入失败、权限撤销属于硬失败，默认整站点回滚。多个站点以站点为事务单元，一个站点失败不必撤销已完成的其他站点，但最终结果必须明确列出。

### 9.3 会话 Cookie

来源中无持久过期时间的 session Cookie 可以导入，但目标 Electron Session 重启后可能丢失。UI 和结果应显示“临时会话”；不得擅自给 session Cookie 添加持久过期时间。

## 10. 权限与安全

### 10.1 两层授权

1. **macOS 授权**：文件/容器访问、Keychain 访问等由系统控制；
2. **Peer 产品授权**：用户对来源 Profile、站点集合和本次导入逐次确认。

macOS 已允许 Keychain 访问不代表 Agent 或应用可以后台导入任意站点。产品授权永不被 OS 授权替代。

### 10.2 PermissionGrant

内部记录可以使用一次性 `PermissionGrant`：

```ts
type SessionImportGrant = {
  grantId: string;
  sourceAdapterId: string;
  profileId: string;
  registrableDomains: string[];
  targetPartition: 'persist:peer-browser';
  expiresAt: string;          // 短期，如 5 分钟
  maxUses: 1;
};
```

Grant 不包含 Cookie value、源文件路径、Keychain secret。流程取消、来源变化、站点变化或超时后立即失效。

### 10.3 Secret 处理规则

- Cookie value 不写日志、错误、analytics、crash metadata 或 Evidence；
- IPC schema 对 secret 字段标记并禁止通用 debug dump；
- 不复制到剪贴板；
- 不写临时 JSON/CSV/Netscape cookie 文件；
- 不通过命令行参数或环境变量传递；
- Helper stdout/stderr 只允许结构化无 secret 诊断；
- 导入期间不得调用远程模型处理 Cookie 内容；
- 测试只使用合成 Cookie，不读取开发者真实 Profile。

### 10.4 路径安全

- renderer 不能提交任意 Profile 路径；
- Adapter 发现后发放短期 profileId；
- main/helper canonicalize 路径并验证位于允许根目录；
- 拒绝 symlink/hardlink 逃逸和可疑权限；
- 临时快照目录权限限制为当前用户，名称随机，完成后删除。

### 10.5 导入后的能力边界

导入后，站点页面自然可以使用 Cookie，已获 `browser_*` / Computer Use 权限的 Agent 也可能在该登录态下执行操作。这不是导入流程中的 secret 泄露，但提升了 Browser automation 的实际权限。

因此：

- 确认页明确说明该影响；
- 高风险网页动作仍按 Computer Use 的 PermissionGrant/确认规则治理；
- 会话导入不得自动授予 Browser automation 权限；
- 用户应能一键清除导入站点数据并撤销登录态。

## 11. Evidence、日志与遥测

### 11.1 Evidence 只记录事实摘要

```ts
type SessionImportEvidence = {
  importId: string;
  sourceBrowser: string;
  sourceProfileLabel: string;
  registrableDomains: string[];
  targetPartition: 'persist:peer-browser';
  addedCount: number;
  overwrittenCount: number;
  skippedExpiredCount: number;
  skippedUnsupportedCount: number;
  failedCount: number;
  status: 'succeeded' | 'partially_succeeded' | 'failed' | 'cancelled';
  errorCodes?: string[];
  startedAt: string;
  endedAt: string;
};
```

不得记录：Cookie name/value、encrypted_value、完整数据库路径、Keychain 服务秘密、HTTP header、完整 Profile 目录。

### 11.2 遥测

若产品启用匿名遥测，仅允许：

- 浏览器 Adapter 类型；
- 成功/失败状态；
- 粗粒度 Cookie 数量区间；
- 标准错误码；
- 耗时区间。

默认不上传站点 domain。若业务确需站点兼容统计，必须另行隐私评审与显式选择加入，不能直接上传明文域名或稳定 hash。

## 12. 验证登录状态

写入 Cookie 成功只表示 Cookie Store 接受了数据，不等于站点登录成功。

### 12.1 本地结构验证

必须验证：

- 写入后能从目标 Session 读取对应 cookie metadata；
- domain/path/secure/httpOnly/sameSite/expiration 与可表达源属性一致；
- flush 成功；
- Cookie value 仅在常量时间比较或本地哈希比较中验证，不进入输出。

### 12.2 站点验证

默认采用用户可见的 Browser 导航验证：

1. 打开所选站点；
2. 用户观察是否已登录；
3. UI 提供“已登录 / 仍需登录”结果。

不使用隐藏后台请求通用判断登录态，因为站点没有统一协议，且网络探测可能触发会话副作用。

未来可以为少量站点提供显式 Site Adapter，声明安全的登录态检查 URL/DOM 条件；该适配器不得读取或上报身份详情。

结果语义：

- `cookies_applied`：Cookie 已写入并通过本地结构验证；
- `session_verified`：站点适配器或用户确认已登录；
- `reauth_required`：Cookie 已应用但站点要求重新认证；
- `import_failed`：未能安全应用并已回滚。

## 13. 失败语义与恢复

标准错误码：

- `source_not_found`
- `profile_not_found`
- `profile_changed`
- `source_access_denied`
- `snapshot_failed`
- `database_schema_unsupported`
- `keychain_permission_denied`
- `keychain_locked`
- `decrypt_unsupported`
- `decrypt_failed`
- `domain_out_of_scope`
- `cookie_invalid`
- `cookie_attribute_unsupported`
- `target_session_unavailable`
- `cookie_set_failed`
- `flush_failed`
- `verification_failed`
- `rollback_failed`
- `user_cancelled`
- `grant_expired`

恢复原则：

- 权限拒绝：说明为何需要权限，提供系统设置入口，不循环弹系统框；
- 浏览器正在写导致快照失败：建议关闭来源浏览器后重试；
- schema/密文版本不支持：显示该浏览器版本暂不支持，不尝试降级解密；
- 部分 Cookie 不支持：列出数量和类别，不泄露名称；
- 站点仍未登录：保留或清除本次 Cookie由用户选择，引导正常登录；
- 回滚失败：突出提示清除目标站点数据。

任何失败都不得修改或删除来源浏览器文件。

## 14. 验收标准

### 14.1 支持范围

- UI 仅列出显式支持的 macOS Chromium 浏览器与 Profile；
- Safari 显示暂不支持，且不申请 Full Disk Access；
- 导入流程和文档明确不导入密码、通行密钥、银行卡或整份浏览器 Profile；
- localStorage、IndexedDB、Service Worker 等不在首期范围。

### 14.2 用户授权

- 只有用户主动进入导入流程后才扫描来源；
- 用户能选择来源浏览器、Profile 和 eTLD+1 站点；
- 用户必须逐次确认，Grant 单次、短期、不可泛化到其他站点；
- Agent 工具无法调用或绕过导入流程；
- 取消在任意阶段生效，并删除临时快照与内存 secret。

### 14.3 Secret 安全

- 自动化测试证明 renderer IPC、应用日志、Helper stdout/stderr、analytics 和 Evidence 不包含 Cookie value；
- 不生成明文 Cookie 临时文件；
- Helper 不返回 OS crypt 主密钥；
- 任意路径输入、symlink 逃逸和非注册 Profile 均被拒绝；
- 权限/解密失败时没有明文回退。

### 14.4 数据正确性

用合成 Chromium Profile 验证：

- host-only 与 domain Cookie 不扩大 domain；
- path、Secure、HttpOnly、SameSite、expiration 正确映射；
- session Cookie 不被擅自持久化；
- 过期、Public Suffix、非法和 partitioned Cookie被正确跳过；
- 只查询并写入用户选择的 eTLD+1；
- `persist:peer-browser` 刷新/重启后持久 Cookie 仍存在；
- 其他站点和来源数据库保持不变。

### 14.5 事务与恢复

- 中途注入写入失败后，目标站点恢复到导入前状态；
- 多站点导入按站点报告成功/失败；
- 回滚失败生成明确错误与“清除站点数据”操作；
- Keychain 拒绝、来源浏览器运行中、数据库 schema 不支持都有可操作提示。

### 14.6 登录结果

- UI 区分 `cookies_applied` 与 `session_verified`；
- Cookie 被接受但站点要求 MFA 时，结果为 `reauth_required`，不宣称身份导入成功；
- 用户可从 Browser 设置清除某个站点的 Cookie/站点数据并退出登录。

## 15. 实施顺序

### Phase 0：协议与合成测试

- 定义 Browser Adapter、ProfileSummary、SiteImportSelection、ImportableCookie；
- 定义 Helper 私有协议、脱敏规则、一次性 Grant 和错误码；
- 构建不包含真实凭据的合成 Chromium Cookie 数据库/Keychain 测试替身；
- 测试 Electron Cookie 属性映射与补偿事务。

### Phase 1：Chrome macOS MVP

- 仅 Google Chrome 稳定版；
- 用户选择 Profile 与一个站点；
- 签名 Helper 快照、Keychain 解密；
- 写入 `persist:peer-browser`；
- 本地结构验证和用户可见站点验证；
- 提供清除站点数据入口。

### Phase 2：Chromium Adapter 扩展

- Chromium、Edge、Brave；
- 多站点批量选择；
- 兼容性矩阵与 schema telemetry（无 domain/secret）；
- 更细的 unsupported attribute 报告。

### Phase 3：Firefox 评估

- 独立 Adapter 与威胁评审；
- SQLite/WAL 快照与字段映射；
- 达到同等 PermissionGrant、脱敏、事务和验收标准后再启用。

### Phase 4：其他状态类型评估

只有在站点兼容数据证明 Cookie 不足、且能建立标准化、安全、可删除的契约时，才评估少量站点的 localStorage/IndexedDB adapter。不得把“复制整份 Profile”作为捷径。

## 16. 关键取舍

### 为什么是“复制”而不是持续同步

持续同步需要常驻读取外部 Profile、处理双向覆盖和随时解密 Cookie，扩大攻击面与用户预期。首期只做用户触发的一次性复制；来源后续退出登录或撤销会话时，Peer Browser 不保证自动同步，UI 必须说明这一点。

### 为什么本管线不导入密码和通行密钥

密码库和 Passkey 是独立的凭据系统，涉及更高权限、用户在场证明和不可导出的私钥。Cookie 会话导入只解决「已登录会话复制」；**尚未登录、需账号密码** 由 **Password manager / autofill** 承担（`browser-password-manager-autofill.md`），而不是把密码塞进 Cookie 快照管线。

对照 Codex 的打包入口：Peer 故意拆成「导入站点会话」与「Password manager」，避免一次确认覆盖 Cookie + 密码双重敏感面，并保持 Agent 对密码库默认零 API。Passkey 仍不导入。

### 为什么使用 Helper

外部浏览器 Cookie 解密涉及 Keychain、签名身份、SQLite schema 和 secret 内存。签名 Helper 能提供最小协议、稳定系统身份和明确审计边界，也与跨平台 Credential Vault 的既有方向一致。renderer 或模型直接读取会破坏安全边界。

### 为什么不直接复制 Cookies 文件

整库复制会带入未选择站点、不可表达属性、数据库状态和潜在损坏，也可能与 Electron 当前 Store 冲突。逐条验证并通过 `session.cookies.set` 写入，才能保持最小范围和属性控制。

### 为什么目标是全局 Browser Profile

当前内嵌 Browser 所有 tab 使用固定 `persist:peer-browser` 分区，登录态天然全局共享。伪装成 conversation 级导入会误导用户。若未来需要隔离身份，应先设计多 Browser Profile/partition，而不是在导入层制造虚假隔离。

## 17. 关联文档

- `design/product/embedded-browser-surface.md` — 内嵌 Browser 菜单/设置；会话导入与 Password manager 分入口
- `knowledge/architecture/browser-password-manager-autofill.md` — 密码库与自动填充（与本文分轨）
- `knowledge/decisions/40-embedded-browser-and-agent-control.md` — 内嵌 Browser 的持久 partition、安全基线与 Browser control
- `knowledge/decisions/46-conversation-bound-browser-tabs.md` — Browser tab 的会话绑定；登录态仍由共享 partition 承载
- `knowledge/architecture/computer-use-capability-ladder.md` — Browser automation 权限与 Evidence；导入会话不等于授权 Agent 操作
- `knowledge/architecture/visible-browser-readiness-handshake.md` — 可见 Browser 自动展开与就绪后再执行
- `knowledge/decisions/0001-cross-platform-credential-vault.md` — 签名本地 Helper、失败关闭与凭据治理原则
- `knowledge/architecture/20-architecture-governance.md` — PermissionGrant、Capability 与 Evidence 主链

## 18. 后续 ADR

代码实现前至少补充或确认：

1. macOS Chrome SessionImportHelper 协议、签名和 Keychain access group；
2. Chromium Cookie schema / os_crypt 版本兼容矩阵；
3. Electron Cookie 补偿事务和站点数据清除语义；
4. Browser 设置页的逐次确认、系统权限引导和可访问性；
5. 合成 Profile 测试夹具与 secret-leak 自动检查。

在上述实施 ADR 和安全测试完成前，不应直接从 renderer 读取外部浏览器 Cookie 数据库，也不应通过通用 Shell 命令拼装解密流程。
