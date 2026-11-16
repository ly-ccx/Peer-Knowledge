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

## 2026-11-16 修订：原生 MCP 网络策略接缝（A，实施前登记）

实际旧 `packages/runtime-node/src/mcp-client.mjs` 将配置 headers 交给 MCP SDK 的默认 HTTP/SSE transport，没有注入 `apps/tui` 的模型专用 fetch。不能声称旧 MCP 已实现模型的完整 macOS / extra CA 策略。本修订明确将原生普通 MCP 的 Streamable HTTP 和 legacy SSE 纳入 ADR50 的同一个 Native Network Module：每次物理 GET/POST 选择环境 / NO_PROXY / macOS fallback 路由，同一附加证书与系统公共根选择，保持 TLS 主机名验证、无自动 redirect / retry、已有帧/响应/连接界限和已配置端点的授权事实。stdio 不改变。

该统一是显式网络配置策略补充，不新增工具或授权。网络预检及 client 构造完成前不能标记 tools/call 已发送；真正发出后的断连/取消继续保留 unknown，不自动重放。SSE 主响应与控制 POST 仍由同一已登记 worker 持有，取消同时关闭。配置错误、超限及取消须保留原任务、历史、凭据和已有 Evidence，修正配置后按原任务准入/恢复规则继续。

仅实际选中代理的秘密进入该连接的有界、可零化脱敏集合，包括 URI 编码/解码凭据及 Basic 注入值。代理认证仅用于代理，不能作为 origin header；不可信代理/服务端回显仍须在 Tool Result、Context、Evidence 落盘前脱敏。协议 isError 真值独立保留，脱敏不能把失败改成功；超过保护集合预算须在下次 dispatch 前失败关闭。错误仅返回稳定代码，不打印 URL、header 或底层错误详情。

OAuth 仍按本 ADR 的地址合同：不能直接使用普通代理客户端。后续代理实现必须先本地有界解析并批准目标 IP，CONNECT 绑定批准的数值 IP:port，origin HTTP Host 与 TLS SNI/主机名验证保留原域名；每跳重新验证，不允许代理重新解析并绕过限制。HTTP(S) 代理自身使用同一可信根策略，代理凭据不进入 origin 请求。此条只是后续实现约束，本卡不宣称 OAuth 代理已接通；当前无代理的受限 OAuth Adapter 不放宽。

验收通过公开原生 CLI → 模型 → Grant → MCP 实际 HTTP/HTTPS/两种 SSE → Tool Result/Evidence，并覆盖 NO_PROXY、错误代理/CA、未知根/错主机、真实代理认证、回显脱敏、前置失败后续任务、dispatch 后未知和取消。使用隔离合成服务与证书，不修改个人代理/系统信任，不冒充真实 IdP、安装或 P4 总闸。

## 2026-11-16 实施复核：OAuth 数值目标连接（B，接线前）

沿上一修订实现，不移动已接受的授权、Evidence、Context、Vault 或地址范围。SDK 仍编码发现、DCR、授权码及刷新；私有 Native Network Module 的 pinned HTTP 接缝只持有经 OAuth 地址策略批准的数值 SocketAddr。每次物理操作先验证原 URL，再有界解析（至多64个 DNS 结果，超限拒绝），筛选获准地址；直连仅在获准集合内连接。代理选择仍针对原 URL，代理 authority 是用户本地网络配置，与不可信 OAuth 发现目标分开。

HTTP(S) 代理通过已锁定 hyper 的有界 HTTP/1 CONNECT parser / upgrade 获得隧道，不能把目标域名交给代理解析。CONNECT 不携带授权码、token 或 origin Authorization。仅代理认证发送给代理；origin HTTP/1 请求保留原 Host、origin TLS 使用原域名或 IP 的严格 SNI/主机名验证。根证书由同一个严格 PEM/DER 来源同时投影给 reqwest 和 Rustls，不维护第二套根选择策略。已选路由不能代理失败后直连，也不重放 origin HTTP。只允许在 origin HTTP 字节尚未发送前、同一已批准集合内做有界 TCP 建连；CONNECT 一经开始就不改目标或自动重试。

整个 SDK HTTP 操作（包括至多3次同源重定向）保留30秒总界限，请求256KiB / 响应1MiB；HTTP/1响应头缓冲32KiB / 至多100字段，建连和 TLS 各至多5秒并服从原取消域。挑战探测只消费有界响应头，不等待成功的无限 SSE body；正常SDK操作有界读 body。origin HTTP 连接驱动与响应读取在同一 owner future 中共同轮询，返回/错误/取消时一起释放；不新增 detached driver、业务 Agent loop 或 Bun/Node sidecar。

用公开 MCP auth/refresh、真实加密凭据夹具及后续 Grant/工具/Evidence 验证；必须包含数值 CONNECT、TLS原主机/未知根/错主机、代理认证隔离、禁止地址/混合DNS、跨源/token redirect不重放、响应界限、取消及之后可准入。隔离实验成功不计产品验收，实现与实际平台/服务覆盖另记。

实施复核补记：隔离 reqwest CONNECT/upgrade 探针确认标准数值 authority 可行，但锁定 reqwest 0.12.24 的公开 ClientBuilder 不提供 HTTP/1 header buffer 上限，不能据此声称 CONNECT 已满足32KiB界限。实际 Adapter 复用同一根投影和已锁定 hyper/rustls，对 proxy TLS、CONNECT 和 origin HTTP 都持有同一受限 driver；不手写 HTTP parser，不放宽头预算或地址/取消政策。此为实现机制校正，不改变上述决策边界。

## 2026-11-16 修订：刷新前置意图与未知结果保全（A，实施前登记）

本条收紧“网络已到达授权服务器后不自动重试”的持久执行条件，局部取代前述“刷新失败保留原元数据”在已登记刷新阶段的解释：旧不可变加密slot继续保留，但不能继续把它发布为当前可刷新凭据。所有发现、issuer/client/token基本校验完成后，在调用SDK刷新前，当前元数据锁owner先向新不可变Vault slot保存并回读验证加密意图，再原子发布该代。envelope继续version1，新增可选顶层 `refreshState:{schemaVersion:1,operationId:<UUID>,previousTokens:<原tokens>}`；普通 `oauth.tokens` 移除，metadata `oauth.tokenStatus` 为 `recovery_required`。意图不是工具dispatch或授权，不创建工具Evidence。

同一事务保持目录锁所有权，并将自身binding推进到真正发布的意图代；只有该owner、未变registry与匹配意图代才能发布SDK返回的新token代。Store支持持锁publish并更新自身revision；最终commit释放锁。Helper写入/回读或意图rename前失败不请求token；意图发布后取消、超时、拒绝、超限、失去原绑定或最终提交失败均保留意图，不还原旧代，不猜测远端是否消耗旧refresh。rename回执不确定也不发请求。该策略允许保守阻断，但禁止自动重放。

Rust真实工具准入及显式refresh、当前Desktop冷读OAuth解析均拒绝任何含refreshState的envelope（包括未知schema），返回 `mcp_oauth_recovery_required`；普通metadata列表仍可显示恢复状态，不解封token。已有TS SDK保存回调受原Vault generation CAS约束，不能清除此意图；普通凭据编辑也不把它清空。已开始的旧TS请求、已预读token的旧发行版并不因此自动受保护，完整自动刷新仍需所有当前token发送者的受管guard、grant代际延续及安装版本drain；本条不冒充该总闸。

本卡支持的恢复为显式原生 `mcp auth <server-id>`：读取原client/issuer配置，新的PKCE/state/code交换成功并验证原registry/意图代后，发布不含refreshState的新凭据；不得复用previousTokens恢复。失败仍保全意图、旧slot、任务历史和原unknown。显式auth只恢复已知schemaVersion1、合法UUID operationId和object previousTokens的意图；未知/损坏意图保全并阻断，不用重登擦除未来语义。未来Desktop原地重新授权恢复须单独接入该所有权路径，不能以普通patch冒充认证成功。无TTL清锁或自动删除Vault slot。

验收使用真实公开CLI、合成IdP与加密Helper：记录已收到的一次刷新，TERM与KILL后冷读均阻断第二次刷新和真实工具；元数据不含秘密，原slot与历史保留；当前Desktop冷读/预持有回调拒绝；显式重登成功后原ready任务可经真实Grant/ToolResult/Evidence继续。覆盖意图提交前失败不发token、意图owner丢失、未知schema、最终发布失败及后续恢复。自动刷新、完整P4、真实IdP/OS Vault、多平台安装与默认切换仍另验。

## 2026-11-16 修订：原生运行时刷新与原授权代际延续（A，实施前登记）

本修订局部取代前文首卡“运行时只消费有效token、过期要求显式refresh”的阶段限制。原生MCP Provider可在实际grant之后、tools/call之前，对过期/临近过期或只有相对有效期的OAuth token执行至多一次受管刷新；缺client/refresh token、交互授权、scope/issuer/client变化或pending仍阻断，不自动注册client、打开浏览器、重放tools/call或追随401。所有操作继续SDK编码、同一Network/地址/TLS/取消/响应边界及前置加密意图。成功后重新检查有效期、原权限、Goal/policy/lease/registry，再派发一次；失败保留真实刷新事实，未发工具不产生工具unknown。

新增仅在当前原生执行内存中存在的credential epoch，由Host创建并绑定完整SessionExecutionIdentity与registry revision；保存初始凭据revision和当前已知revision，不落盘、不成为新授权或秘密副本。只有OAuth Module实际持锁publish返回的不可伪造内部publication可以推进它；严格匹配原expected binding、前一revision和实际Store回读，且限同一ref/client/issuer/resource/scopes的token刷新。发现的issuer/client必须与原实际加密配置一致，scope不扩大；未来/未知、DCR或外部轮换不能伪装刷新。意图与最终代均以同一owner的真实发布推进；提交失败或未知不能推进为成功。

Host授权指纹继续逐次读取并校验真实Store revision；只有当前execution的epoch证明实际revision等于本次已确认代时，才将此单一来源规范化为初始revision以复核原grant。Goal、args、policy、祖先/角色、执行绑定、lease、registry及其它来源仍逐次精确比较，不改写grant事实或延长权限。Context同样检查当前epoch的真实revision，不因本机刷新恢复旧历史或绕过其它Context准入。外部任何凭据行/全文件变化、旧写者、metadata/registry身份变化均失去此映射而阻断；重启没有此内存证明，只从真实已提交Vault与既有任务恢复重新准入。

每server的原生连接owner使用有限队列串行承接当前工具请求及其真实Host检查port；Provider不持有或生成许可事实。有效token可复用同一连接；需要刷新时先停止并join旧Connection/transport/SDK任务，确认停稳后才登记刷新，再以新token初始化。初始化后再次使用当前请求的port检查并只call_tool_once。逻辑connection handle覆盖该owner内HTTP连接的有序替换，取消覆盖整个owner；stdio不因本卡自动重启，旧childRecorder不能被替换抹去。服务端通知/控制流不成为授权来源；断连、超限、超时或已发调用失败仍unknown且不重放。

验收通过公开原生exec：过期token→唯一刷新→真实工具/Grant/Evidence→下一模型请求和第二工具；有效token复用、回合中自然到期后的关闭/刷新/新初始化；拒绝不读Helper或访问IdP；policy/Goal/registry/外部credential在刷新期间变化会停止工具；取消/硬退出保留意图、所有者和原unknown，显式重登/新准入可恢复。覆盖真实加密Vault、HTTP(S)/proxy及其它transport回归。此条为原生执行接线：当前TS已预读token发送者的guard和旧安装版本drain仍是完整跨宿主P4/默认发布的独立必需条件，冷读/CAS不被当作该条件已满足。实现与平台验收另记。

实施前B级复核：逻辑连接跨token代替换时，既有脱敏义务仍覆盖已注入旧token/代理认证与本次刷新接触的凭据；不能因关闭旧physical Connection就使旧秘密在后续Tool Result中外流。沿同一64值/256KiB预算保留可零化保护集合直到logical owner结束，溢出在下一次工具dispatch前阻断，不新增秘密持久副本或扩大响应预算。epoch只存非秘密revision；保护集合由Session owner持有。代理测试区分OAuth批准数值CONNECT和普通MCP既有域名CONNECT，不能把仅OAuth适用的地址规则断言为全部MCP的新合同。
