# 渠道账户余额与用量

创建时间：2026-09-05
最后更新：2026-09-05
状态：实现与自动回归完成；受控 UI 样式方向已确认（A 级协议扩展，真实账户联调未验证）

## 边界

沿用现有订阅额度查询入口和 main 进程凭据读取链路，以兼容的可选字段扩展协议。Renderer 仅展示快照，不读取凭据、不访问厂商、不维护权限事实。此次不新增模型可调用工具；未来如暴露为工具，必须经过 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。

运行时适配器负责固定目标端点、解析和标准化。主进程负责读取当前已授权渠道凭据、账户隔离及聚合本地请求日志。渠道注册表是渠道身份事实源；远端响应是账户数据事实源；既有请求日志是本地统计事实源。UI 不根据渠道名猜测能力。

仅使用当前已有 API Key、OAuth 或 Qoder 登录态。Admin Key、浏览器 Cookie、新 CLI 登录流程不在本阶段范围内。不得读取浏览器凭据或发送收费推理请求来探测额度。不得把任意兼容端点的 Key 发给某个官方查询端点；官方渠道修改了端点也必须验证目标范围。请求拒绝重定向，不返回响应体中的密钥或原始错误。

缓存至少隔离渠道实例、认证方式、端点和凭据版本（不得持久化原始 Key）。换账号/换 Key 不得命中旧账户快照。失败不是零余额；缺失字段不是零用量；本地记录为空不证明账户未消费。

主进程配置视图额外投影可选 `accountUsageRevision`：进程内随机标记，不是密钥摘要，不写入配置。凭据事务改变 secret 时失效；渠道、认证、端点或 OAuth 账户元数据改变时换标记。账户查询在每个异步边界之后复核当前视图，变更返回 `account_changed` 而非旧余额；旧 OAuth 缓存也按此标记隔离。Renderer 只展示匹配修订的快照并丢弃旧请求，不把修订当权限凭据。Token 刷新若触发修订，当前查询安全失效，UI 重新获取配置后再查询。该机制只观察配置服务管理的凭据；外部 CLI 账号切换仍依赖既有 CLI 查询刷新，不扫描额外凭据源。

### 固定账户网关映射

百炼国区 Coding 渠道只允许模型 origin `https://coding.dashscope.aliyuncs.com` 映射到账户 origin `https://bailian.console.aliyun.com`，使用固定 queryCodingPlanInstanceInfoV2 只读 POST、固定 commodityCode 和地区。不从 URL 猜地区，不向国际区重试。传输层分别校验模型与账户 origin；POST 方法、固定请求体及附加认证头种类参与缓存 identity。此网关源自用户提供的 CodexBar 源码，其 API Key 路径为 best-effort：失败明确提示可能需要控制台登录，不自动获取会话。新渠道映射需单独核实，禁止任意跨域 key 转发。

参考来源：CodexBar 本地源码包（MIT，Copyright (c) 2026 Peter Steinberger），`MoonshotUsageFetcher.swift`、`Resources/Plugins/openrouter.js`、`MiniMaxUsageFetcher.swift`、`AlibabaCodingPlanUsageFetcher.swift`。源码包未绑定已核实 Git commit。Moonshot 响应未声明币种时不根据参考 UI 的美元符号推断币种；OpenRouter 不调用需要 Management Key 的 activity 接口。

## 数据表示

保留 LlmSubscriptionQuota 旧字段（含 Qoder 点数），增加可选余额、消费、本地用量、来源、缺失原因与过期标志。窗口增加绝对值和单位。金额用十进制字符串，避免浮点金额精度损失；不同币种不汇总。来源、范围分项标注，避免同一快照中的本地统计污染远端账户口径。

无权限或不支持仍返回结构化状态与本地统计；远端成功但缺少维度应表达部分可用。兼容渠道默认只提供本地统计，不声称厂商账户覆盖。估算费用必须标记为估算。

## 渠道和认证矩阵

| 渠道/认证 | 本阶段远端维度 | 缺失维度原因 |
|---|---|---|
| OpenAI / ChatGPT OAuth | 原有订阅窗口 | 非 API 账户账单 |
| OpenAI / API Key | 无 | 组织用量需 Admin Key |
| Anthropic / API Key | 无 | 组织用量需 Admin Key，订阅需独立会话 |
| DeepSeek / API Key | 余额 | 详细用量需网页会话 |
| GLM CN、Global / API Key | 计划窗口 | 非现金余额 |
| Kimi Coding / API Key | 计划窗口 | 会员池需网页会话 |
| Moonshot / API Key | 余额 | 无已核实总账用量接口 |
| MiniMax CN、Global / API Key | Token / Coding Plan Key 的窗口 | 普通 Key 不保证支持；只在原地区回退到 Coding 接口 |
| Volcengine Ark / API Key | 无 | 计划用量需额外 CLI；不发推理请求探测限流 |
| MiMo、MiMo Token Plan / API Key | 无 | 需控制台会话 |
| 百炼 Coding / API Key（国区） | 固定只读网关的计划窗口（best-effort） | API Key 路径不保证可用，可能要求控制台会话，不自动降级读取 |
| OpenCode Go / API Key（含旧 ID） | 计划窗口 | Zen 余额需网页会话 |
| OpenRouter / API Key | 余额、消费、Key 限额 | 账户/Key 口径分别标注 |
| 两种 Compatible / API Key | 无 | 任意服务商没有统一账户接口 |
| Google / OAuth | 原有额度 | 非 API 账户余额 |
| Google / API Key | 无 | 不提供相同的账户额度接口 |
| Grok / OAuth | 原有额度 | 非现金余额 |
| Qoder / 当前及旧 CLI 认证 | 原有点数 | 非现金余额 |

所有行均可附本地统计（仅既有日志保留范围）。实现时不得将未经核实的数据源宣称为已接通。

## 验收交叉矩阵

独立轴：渠道及认证变体 × 远端数据维度 × 凭据状态 × 端点/地区 × 缓存状态；本地统计与远端成功与否独立。

集中命令 `node scripts/verify-account-usage.mjs` 必须从注册表枚举全部行。每行运行命名测试：`<channel>/<auth>/capability`、`/missing-credential`、`/local-only`。对每个可查数据源再运行 `/success`、`/partial-or-malformed`、`/http-failure`、`/timeout`、`/redirect-denied`、`/cache-hit`、`/credential-rotation`、`/endpoint-isolation`。地区适配分别运行，不共享密钥目标。无远端能力行的上述网络项跳过原因即本表的缺失维度原因，并验证不发网络请求。

余额×币种：多币种、零、负数（仅厂商允许）、非法金额；窗口×数值：百分比、绝对值、重置时间、缺失；消费×范围：账户与 Key 不混淆；本地×远端状态：成功/失败/缺失均保留正确分组与统计范围。

保留旧 OAuth/CLI 与格式化测试，构建协议依赖链和 Desktop。受控 UI 检查覆盖余额、多窗口、本地、加载、失败、过期。Mock 通过不代表真实账户接口联调成功；交付须说明限制。

## 实现验收记录（2026-09-05）

用户已明确确认“新样式方向可以”。正式组件采用主题化分区卡片、PeerIcon 展开箭头、标题栏查询/刷新、额度进度及独立本地统计，不再使用原生 details 箭头与纯文本堆叠。

集中命令 `node scripts/verify-account-usage.mjs` 本次执行 358 项通过，0 失败、0 跳过。下表记录实际测试命名；上文的短名为验收意图，不要求一项意图单独占一个测试函数。

| 独立轴与必需组合 | 命名测试及检查位置 |
|---|---|
| 全部注册渠道 × 认证变体 × 本地记录有/无 | `channels/<channel>/<auth>/missing-credential/local-<true|false>`；同一测试断言适配/旧额度分流或不可用维度原因，禁止无凭据发网络 |
| 11 条数据源/地区配置 × 缺 Key、自定义端点、兼容渠道 | `adapter-matrix/<channel>/<host>/<scenario>/no-network` |
| 上述配置 × 换 Key、缓存命中、过期、force、不同实例、clear | `key-change/cache-isolation`、`success-expiry-force-instance-isolation`；同函数中依次断言各缓存状态 |
| 上述配置 × 非法响应、HTTP 500、401、重定向、超时 | `adapter-matrix/<channel>/api_key/<state>`；同时验证错误不泄漏响应或密钥 |
| 余额 × 币种/金额有效性；窗口 × 百分比/计数/重置/缺失；消费 × 账户/Key | `account-usage-parsers`、`account-usage-balances`、`account-usage-glm`、`account-usage-plan-adapters` 的厂商命名测试；无远端维度的组合按渠道矩阵明确排除，不伪造零值 |
| 本地统计 × 远端成功/失败/缺凭据/不支持 | `local/remote-<status>/group-attribution/retained-range`；另测空记录、缺价格与分组前缀碰撞 |
| API/旧认证 × 异步边界 × Key/账号/端点/删除变化 | `identity/<api|legacy>/<credential|remote|local>/<change>/drops-old-observation`；旧认证的凭据解析由既有链路持有，服务层无对应独立等待点 |
| Renderer × 修订变化/失败/取消/并发顺序 | `view/identity/*`、`refresh/*`、`request/*`、`order/*`；旧 OAuth/CLI 与格式化测试同时保留 |

证据：集中测试 `local-shell-artifact://shell_b44a071d-a9c8-49f2-a54c-1193caf8af90/stdout`。独立 `pnpm --filter @peer-agent/desktop build` 退出 0，包含 protocol/runtime-core/runtime-sdk/runtime-node、IPC、Vite 和 overlay 检查：`local-shell-artifact://shell_e284dbfb-639d-4e9e-87cc-8e2586f3612f/stdout`；构建有动态导入和包体积警告。`pnpm --filter @peer-agent/desktop exec tsc --noEmit && git diff --check` 退出 0：`local-shell-artifact://shell_c01371c7-9792-400b-a316-5e9d09b3823f/metadata`。

受控预览使用真实 `AccountUsageDetails`，不加载凭据：余额、窗口、本地统计、浅/深色及窄布局沿用已记录预览；空态、失败、过期的 DOM 记录已复核。补充无旧快照首次加载：`local-browser-artifact://8368961c-9aca-45b8-9c8c-318155fe5ad1/content`（展开、aria-busy=true、查询禁用、无余额）。Enter 展开与 Space 收起分别记录于 `local-browser-artifact://413fedda-2f6d-41ab-9856-956fb7ff66bb/content`、`local-browser-artifact://67f72ce9-a908-4bf0-8f6b-3e96774521b5/content`。预览脚本支持 `state=initial-loading`，以及 `slow=1` 延长模拟刷新观察时间。

### 验证限制

- 本次为代码、fixture 回归和受控组件预览验收，不是全部真实厂商账号联调，也不是已安装 Desktop 的完整端到端验收。
- 不承诺所有渠道同时提供余额与总账；百炼国区为 best-effort，额外 Admin Key、网页登录态和新 CLI 登录均未接入。
- 本地统计只覆盖已有日志保留范围（默认最多最近 5000 条全渠道记录），可能含换账号前记录；费用是估算，不代表厂商总账。
- 预览刷新使用模拟计时器；不以点击工具成功或刷新后的静态快照代替真实 IPC/厂商刷新验证。主进程及 Renderer 的刷新/竞态逻辑由自动回归验证。
- 上述验收不包含发版、安装或正式应用重启；提交与推送另行记录。
