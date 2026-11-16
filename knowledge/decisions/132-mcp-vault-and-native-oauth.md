# ADR 132：MCP 统一 Vault、旧凭据迁移与原生 OAuth

- 状态：Accepted（沿已接受 ADR0001、129–131 及用户 2026-11-16 的明确实施授权；实现与验收另记）
- 创建 / 更新：2026-11-16
- 级别：A

## 既有决策与修订范围

继承 `0001-cross-platform-credential-vault.md`、`31-mcp-connection-management.md`、`32-mcp-authentication.md`、`45-mcp-oauth-config-ux-simplification.md`、`129-native-rust-cli-and-ratatui.md`、`131-native-cli-contract-storage-and-recovery.md`。本条明确取代 ADR32 对新 MCP 写入使用 Electron safeStorage / plaintext file-fallback 的条款；旧数据仅供受控迁移。OAuth 登录不产生工具许可，不改变 Runtime Projection、PermissionGrant、Evidence 或 unknown 对账政策。

## 唯一秘密存储

Desktop 与原生 CLI 均经现有 v1 `peer-credential-helper` 协议访问 Vault；新增白名单 `mcp/<credentialRef 的 UTF-8 SHA256 小写 hex>/<随机 UUID generation>`。既有 model 命名空间不变。秘密只在 stdin/stdout 和所需 transport 内存中流动，不进入 argv、日志、错误详情、Evidence、registry、模型或 Renderer。系统安全存储不可用必须失败关闭。

既有 `mcp-credentials.json` 升为 v2 元数据文件；保留 credentialRef、id、非敏感字段和未知字段，不建立第二个 registry。每项保存 `vaultKey`，以及 UI 所需脱敏状态；完整敏感载荷（含 OAuth clientSecret、tokens、clientInformation、codeVerifier、discoveryState）作为绑定 `{version:1,credentialRef,kind,secret?,oauth?}` 的单个 Vault envelope。读取须核对键的 ref hash、generation、载荷版本、ref 与 kind；未来版本、损坏、重复 ref、超限、符号链接均阻断。原生端遇到 v1 只报告 `mcp_credential_migration_required`，绝不解密 Electron 或使用旧明文。

## 提交、并发与恢复

所有元数据写入持同名 `.lock` 目录锁，不能按 TTL 抢锁。以有界读取的原始源身份核对并保存未知字段。先生成不可变 Vault slot → Helper set → get 常量时间核验 → 同目录 0600 临时文件 fsync → CAS 原子 rename → fsync 目录。只有元数据发布才使新代可见；禁止原地覆盖旧 slot。rename 前失败保留原元数据和旧 slot；rename 后回执丢失按实际元数据读取对账，不返回伪成功。孤锁遵循 ADR131 离线保全和真实进程停稳维护规则。未发布 / 已退役的加密 slot 可保留，不凭失败推断可以删除；本阶段不自动垃圾回收。该残留有明确归属，不是明文 fallback 或第二个执行日志，后续清理需核对完整引用与全部 writer 已退出。

Desktop 是唯一旧格式迁移者：严格读取 v1，使用现有 safeStorage 解密或读取已存在且明确标记的旧 plaintext-fallback；绝不新建明文 fallback。全文件每项均写入并回读验证后，才一次发布 v2。任一旧项解密、Helper、验证、CAS 或提交失败则保留旧文件字节。未知版本、坏 JSON 或不完整身份不当空库重建。迁移不会在测试或 CLI 中操作个人数据；实际 OS、签名升级和历史用户样本验收独立记录。

## 原生执行与 OAuth

Vault 写入不得超过现有 reader 的 16 MiB 上限；容量拒绝发生在 rename 前，旧文件继续可读。此为既有限额的一致性修复，不扩大存储上限。已超限的历史文件须保全并受控离线修复；不截断或自动删除秘密。元数据 1 MiB / 1024 项 / 深度32，envelope 256 KiB / 8192节点 / 深度32；不同端采用相同边界。

静态 bearer / header / stdio_env 与 OAuth 都沿现有 MCP Provider。冻结非敏感 credential binding 与元数据 revision；真实 grant 后才解析 Helper，解析后、启动 transport 前及 initialize 后 tools/call 前复核同一权限、registry 与凭据身份。轮换、删除或迁移使旧池失效；禁止将过期连接用于下一次调用。返回值脱敏包括完整注入值与原始 token，不能只匹配 `Bearer <token>`。取消必须终止并等待 Helper / transport 所有者。

HTTP OAuth 使用官方 Rust SDK 的协议 seam，遵循 MCP 授权规范的 protected resource / issuer 发现、PKCE、state、resource audience、预注册或 DCR。交互授权属于显式凭据管理动作，回调仅绑定 loopback 并校验完整 redirect、state 和 issuer；受控超时 / 取消，不自动打开浏览器或启动无 owner 监听器。密钥、PKCE、刷新 token 仍在 Vault；只有新代原子提交后才使用刷新结果。刷新须在工具 dispatch 前完成，旧代 CAS 冲突阻断；401 / scope challenge 不自动重放 tools/call，已派发失败继续保留 unknown。

本条不授权 OAuth 授权码、URL、token 作为系统指令；不扩展到 model OAuth 或 ACP 登录。SDK 默认 HTTP 若不满足已有响应大小、redirect、deadline、地址策略与所有权约束，须用有界 HTTP Adapter，不直接启用无限制默认 transport。原生缺少的子能力明确阻断，不声称完整 OAuth 平价。

## 验收与回退

Desktop 的同次 OAuth provider 保存回调持有原 generation，并随自身成功提交推进；外部轮换后晚到回调拒绝，不能把旧 token 写入新 principal。原生显式管理持元数据锁至提交 / 取消，并在发布前核对原 registry revision。网络已到达授权服务器而响应或本地保存不确定时，只能保全本地事实并重新授权 / 核对，不承诺旧 refresh token 仍可用，不自动重试授权码或刷新交换。

既有预注册 client 缺失 redirectUrl 时，保留 Desktop 的 `http://127.0.0.1:33418/mcp/oauth/callback`；新 DCR 可注册实际绑定的临时 loopback 端口，显式 redirect 仍按原配置。当前 Adapter 仅支持 IPv4 `127.0.0.1` callback。单 HTTP 操作30秒、响应1 MiB、请求256 KiB；仅同源至多3次发现 / DCR redirect，token exchange 禁止 redirect / 自动重试；DNS 和 IP literal 禁止元数据地址及未获准的内网目标，不隐式通过环境代理绕开地址策略。callback 总等待300秒、至多16连接、每请求头8 KiB / 2秒；这些是实现界限，非完整协议平价。

首卡公开 `mcp auth <server-id>` 与 `mcp refresh <server-id>`；运行时只消费有效 token，过期 / 只有相对 expires_in 而无接收时间的旧 token 明确 `mcp_oauth_refresh_required`，不猜时间或沿旧池无限使用。自动刷新后 continuation / 原 grant 的代际绑定、完整代理 / 证书策略与其它原生 OAuth 平价仍须后续验证，不能将显式管理闭环标为完整 P4。

协议参考：[MCP 2025-11-25 Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)、锁定的官方 `rmcp 3.10.0` auth 源码；使用 SDK 不等于本产品通过协议或平台验收。

用隔离合成凭据验证实际 Desktop Store → Helper seam → Rust reader / Provider → transport → Evidence；覆盖三种静态注入、OAuth 登录 / 刷新、旧 safeStorage / plaintext 迁移、逐项失败、回读不一致、源并发、锁 / 新版本 / 损坏、取消、轮换和冷读恢复，证明无 secret 外流、无未授权调用与无请求重放。测试替身不能成为生产明文存储路径。

当前支持合同的 TS / Rust 必须一起读取 v2；旧发行版未实现 v2 fail-closed，不能宣称任意旧二进制可安全续跑。默认共享写入、安装、回退和发行仍受 ADR131 drain 与 release gate。本条记录决策，不表示 P4 总闸、OAuth、平台 Keychain 或默认 CLI 已通过。
