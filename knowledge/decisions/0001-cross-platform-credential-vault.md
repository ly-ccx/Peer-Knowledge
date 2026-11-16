# ADR 0001：跨平台凭证 Vault 与统一 Helper

- 状态：Accepted
- 创建时间：2026-07-15
- 最后更新：2026-07-15
- 2026-11-16 MCP 补充：[ADR132](132-mcp-vault-and-native-oauth.md) 将同一 Helper / Vault 扩展到 MCP credentialRef 与 OAuth envelope，原生端仍不解密 Electron。旧密文的 Desktop-only 安全迁移责任不变。

## 背景

Peer Agent Desktop 当前使用 Electron `safeStorage` 加密 LLM API Key 与 OAuth Token，并把密文写入 `llm-providers.json`。在 macOS 上，`safeStorage` 的主密钥由 Keychain 保护。TUI 为复用 Desktop 凭证，直接读取 `Electron Safe Storage` 钥匙串项并复刻 Electron 的 AES-CBC 解密格式。

该实现存在以下问题：

1. Desktop 与 TUI 是两个独立访问主体，macOS 可能分别请求 Keychain 授权。
2. 当前发布构建允许 ad-hoc 签名，更新后代码身份变化会导致重复授权。
3. TUI 依赖 Electron 的内部密文格式，Windows 与 Linux 无法复用。
4. `safeStorage` 不可用时存在静默明文降级，违反凭证失败关闭原则。
5. API Key、Access Token、Refresh Token 与普通模型元数据混存在同一配置文件中。

## 决策

### 1. 独立 Credential Helper

新增独立原生二进制 `peer-credential-helper`。Desktop 与 TUI 不直接访问平台安全存储，也不自行解密 Vault。

每次请求由调用端启动 Helper，通过继承的 stdin/stdout 交换单条版本化 JSON 请求与响应：

```text
Desktop ─┐
         ├─ spawn + stdin/stdout ─ peer-credential-helper ─ platform key store
TUI ─────┘
```

选择按请求启动而不是常驻 Socket/Named Pipe 的原因：

- 不暴露可被其他本地进程连接的监听端点；
- 不需要额外的进程发现、锁、重连和生命周期治理；
- 凭证不进入 argv、环境变量或日志；
- macOS Keychain 看到的访问者始终是稳定签名的 Helper；
- Windows、macOS、Linux 使用同一个上层协议。

请求协议版本为 `1`，只允许 `ping`、`get`、`set`、`delete`。凭证键必须通过白名单校验，响应不得包含堆栈或底层系统错误文本。

### 2. 版本化加密 Vault

具体凭证保存在用户数据目录的 `credentials.vault.json` 中。Vault 版本为 `1`，每条记录独立使用 AES-256-GCM 加密：

- 32 字节随机主密钥；
- 每条记录使用 12 字节随机 nonce；
- AAD 绑定协议版本与凭证键；
- 认证标签由 AES-GCM 密文携带；
- 所有二进制字段使用 Base64；
- 更新使用同目录临时文件、`fsync` 与原子 rename；
- Unix 目录权限为 `0700`，文件权限为 `0600`。

Vault 只包含密文。普通模型配置只保存 provider、model、base URL、reasoning 等非敏感元数据和 `apiKeyConfigured` / `oauthConfigured` 布尔状态。

### 3. 平台主密钥保护

Vault 主密钥只由 Helper 访问：

- macOS：Keychain Generic Password；
- Windows：Windows Credential Manager，数据由当前用户的 DPAPI 保护；
- Linux：Secret Service（libsecret/KWallet 兼容服务）。

平台安全存储不可用时必须失败关闭。不得自动把主密钥或业务凭证写成明文。测试使用内存 Key Protector 注入，不访问真实系统凭证库。

### 4. 迁移

Desktop 首次读取旧配置时执行一次迁移：

1. 使用现有 Electron `safeStorage` 解密旧 API Key/OAuth Token；
2. 通过 Helper 写入 Vault；
3. 重新读取并进行常量时间等价校验；
4. 原子写回去除秘密字段的元数据文件；
5. 迁移任一步失败则保留旧文件，不删除旧密文，并返回明确错误；
6. 迁移完成后，TUI 只通过 Helper 读取 Vault。

TUI 不负责旧格式迁移，也不再读取 `Electron Safe Storage` 钥匙串项。

### 5. 签名与打包

Desktop 和 TUI 均打包同一个 `peer-credential-helper` 二进制。macOS 正式发布必须使用稳定 Developer ID Application 身份并完成 notarization；ad-hoc 签名只允许开发构建，不能承诺升级后免重复授权。

Windows Helper 随 Desktop/TUI 一同发布，凭证绑定当前 Windows 用户。Linux 若无 Secret Service，应提示安全存储不可用，而不是降级明文。

## 威胁模型

本方案防护：

- 凭证文件被单独复制或备份泄露；
- 配置文件被普通读取；
- 密文被篡改；
- Desktop/TUI 更新导致各自直接访问平台安全存储；
- 秘密通过命令行参数或日志泄露。

本方案不防护：

- 已完全控制当前用户会话或能注入 Peer Agent 进程的恶意程序；
- 已解锁用户会话中的管理员/root 级攻击者；
- 调试器读取进程内存。

## 失败语义

- 平台安全存储不可用：拒绝保存/读取，并返回稳定错误码；
- Vault 认证失败或格式损坏：拒绝返回任何秘密；
- Helper 不存在或协议不兼容：Desktop/TUI 显示可操作错误；
- 旧凭证迁移失败：保留旧密文，不做破坏性清理；
- 禁止任何隐式明文回退。

## 影响

### 原生模型 OAuth 的条件提交（2026-11-16，实施前 A级修订）

本节为已接受 ADR129/131 全面原生迁移中的模型 OAuth 生命周期补齐，取代§1「只允许四种action」在已协商扩展上的封闭限制，不改变旧四种action、Vault v1密文格式、Helper身份或权限边界。设计接受与实现/验收分别记录。

- Helper协议仍为1，`ping.data.features`可声明`model-oauth-cas-v1`；新增可选`get-snapshot`与`compare-set`，仅允许既有`model/<group>/oauth-tokens`键。旧客户端继续使用ping/get/set/delete；旧Helper不声明feature时，新客户端必须在远端token刷新之前拒绝条件更新，不能发送后才发现不能持久化。
- `get-snapshot`在既有Vault共享锁下返回原secret及不含秘密的opaque revision；缺失键返回secret/revision均null。revision来自该记录已有的随机nonce，不是授权、时间、配置版本或文件全局revision。每次旧/新`set`都生成新nonce，delete使旧revision失效。
- `compare-set`携带expectedRevision（null表示仅当不存在）与secret（null表示删除）。Helper在同一既有Vault独占锁内核对原revision；匹配后认证原密文、加密新值并原子保存，再返回applied与新revision。失配不写Vault，不返回当前secret；失败和未知返回不能当作成功。原密文损坏、未知Vault版本或容量不足继续失败关闭。
- 原生刷新使用既有token JSON的access/refresh/expires/accountId等字段，保留未知字段；secret只经继承管道，不进argv/环境日志/ToolResult/Evidence。临近过期的请求先以当前快照刷新，落盘成功才准入模型；迟到refresh若遇旧/新客户端轮换或删除，条件写入必须失败，不能无条件覆盖、复活或自动重放。远端可能已经轮换而本地提交失败时，保留当前Vault与原错误，支持重新登录/显式恢复，不声称旧refresh仍有效。
- 配置中的oauthConfigured/oauthExpires/oauthAccountId保持非敏感投影，不是token有效性、凭据读取授权或请求成功的权威。原生模型读取实际Helper token与绝对expires；不为更新提示字段无锁覆写整个llm-providers.json。现有Desktop元数据提示可能暂旧，完整配置写入/登录收据须经共享Store ownership另行补齐并验证，未完成不记P4总闸。不得借本节新增明文token、私有事实根或从原生端解密Electron旧数据。

验收覆盖真实Helper加密Vault（注入测试KeyStore）、旧客户端set/delete使新快照失效、同键与异键并发、条件删除/创建、容量/损坏保全、双向TS/Rust协议；原生模型真实HTTP刷新→条件持久化→模型/工具/Evidence、取消/超时/重定向/截断/过期/缺refresh、竞争退出/新登录、提交失败和后续准入。真实平台Vault/IdP与安装升级验收独立，不以注入KeyStore替代。

2026-11-16同日实施前补强（A）：仅有完成时CAS不能防止并发发送同一refresh token，也不能记录超时后的未知远端轮换。已协商客户端须在远端请求前以原快照CAS写入加密token内保留字段`peerModelRefresh:{schemaVersion:1,attemptId:<UUIDv4>,authMethod,phase:"in_flight",createdAt:<epoch-ms>}`，再核对自己提交的revision后才发送；只有一个客户端能取得该意图。字段是刷新操作的连续性事实，不是凭证授权或远端成功证明，不新建明文日志/私有根。

完成时仅从自己仍持有的意图revision条件提交新token并移除此字段。取消、超时、连接中断、提交回执丢失或崩溃后可能已发出请求的意图必须保留，后续自动请求不得重放旧refresh；重新登录以新授权凭据显式替换，或由支持该状态的恢复流程对账。明确在HTTP future首次poll前取消、可证明未发送时，可按原意图revision条件恢复原token；CAS失配仍保留新状态。未知schema/损坏意图保全并拒绝，不按时间或进程死亡猜测远端未轮换。

新Helper的旧`get`以及新TS客户端对模型OAuth键发现该字段时返回稳定pending错误，不向不支持连续性状态的调用方返回旧refresh；`get-snapshot`仍向条件更新客户端提供原始加密payload解密结果。已预读token的旧运行时也必须迁移到同一前置意图/CAS seam，不能靠get时保护声称全版本并发安全；旧Helper与旧运行时混合在新刷新状态上的执行兼容须经ADR131 drain/升级门禁，未验证不得开放默认共享写域。现有配置元数据、Tool/Evidence与权限契约不变。

- 新增 Rust Helper 与 TypeScript 客户端包；
- Desktop LLM Store 改为元数据 + Vault；
- TUI 共享模型配置改为通过 Helper 取 secret；
- release 构建增加 Helper 编译与资源打包；
- 需要 Windows 与稳定签名 macOS 的人工升级验证。
