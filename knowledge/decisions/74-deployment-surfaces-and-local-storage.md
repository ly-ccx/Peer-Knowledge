# 74. 部署面与本机存储策略

创建时间：2026-09-06
最后更新：2026-11-16（对齐 [ADR 133](133-unified-rust-core-and-dual-host-architecture.md)：本机与各部署面承载的唯一核心 Runtime 终局统一为 Rust Core，`ADR 54` 的 TS SDK 仅作过渡兼容层；`<dataRoot>`、`~/.peer-agent`、Credential Helper v1 与按类混合存储边界不变；2026-11-15 规范状态为 Accepted）

状态：Accepted（本机 `<dataRoot>` 数据面分层、Desktop/CLI 共享规则与密钥进 Vault 已作为现行基线在 ADR [81](81-project-agent-memory-system.md)、[85](85-project-agent-hosts-inputs-and-surfaces.md)、[104-progressive](104-progressive-interaction-and-coordination-storage.md)、[121](121-desktop-session-windowing-contract.md) 采纳落地；内网自托管与远程连接 Gateway 部署拓扑仍按后续分阶段演进，不改变已生效的本机存储不变量）

级别：A 级（产品边界 + 数据面选型，影响账号、Gateway、存储）

关联：

- `design/product/peer-product-alignment.md` — 产品链路：本机持有能力、授权与 Evidence
- `design/product/peer-2-0-product-system.md` — Local-first / Cloud-enhanced
- `design/product/remote-connection-exploration.md` — 远程连接调研；落地顺序以本文为准
- `design/product/first-run-onboarding-guidance.md` — 本机首启不走注册向导
- `knowledge/architecture/20-architecture-governance.md` — Permission → Evidence 主链不可旁路
- `knowledge/architecture/22-tui-desktop-shared-runtime-and-host-governance.md` — Desktop / CLI 共享内核与 `~/.peer-agent`
- `knowledge/decisions/0001-cross-platform-credential-vault.md` — 密钥走 OS 保险箱
- `knowledge/decisions/15-plugin-skill-mcp-system.md` / `16-skill-call-lifecycle.md` — 可选云端通道不是 Peer 身份
- `knowledge/decisions/25-runtime-usage-ledger.md` — 用量账本归属 Runtime，不在 UI
- `knowledge/decisions/48-cli-first-class-release.md` — Desktop / CLI 共享数据根
- `knowledge/decisions/54-open-runtime-public-packages-and-release-policy.md` — 可嵌入 Runtime host
- `knowledge/decisions/63-user-artifact-evidence-boundary.md` — Evidence 与用户产物边界

---

## 背景

Peer Agent 已经是一套本机 Runtime：Desktop 与 CLI/TUI 是同一内核的宿主入口，数据根语义为 `~/.peer-agent`（可用环境变量覆盖，不以本机绝对路径为约定）。密钥走 OS 保险箱（ADR 0001）。能力执行必须经过：

```text
Capability Provider
  → Manifest
    → Runtime Projection
      → Tool Call
        → PermissionGrant
          → Evidence
```

产品上已经对齐三件事，但还没有单独成文：

1. **部署面**：默认本机、可内网自托管、可选远程连接，是同一套 Runtime 的三种拓扑，不是三套产品。
2. **账号职责**：注册只服务远程身份与授权，不是本机使用的前提，也不是把认知或密钥默认搬上云。
3. **数据面**：知识用 Markdown/Git，密钥不进业务库，大对象走文件系统，只有需要筛选聚合的结构化状态才进 SQLite。禁止「全部迁库」。

若不先锁这三条，后续 Gateway、注册服务、Linux 打包或会话检索很容易各自选存储、各自旁路主链，或把云端做成第二套执行真相。

探索稿 `remote-connection-exploration.md` 仍作调研背景。本文改写产品落地顺序：先内网 Gateway（可无公网注册），再加注册与远程连接；不以第三方 IM 桥为第一刀。

---

## 决策

### 1. 一套 Peer Runtime，三个部署面

同一套 Runtime，三种拓扑。Desktop / CLI/TUI 仍是本机宿主入口（架构 22、[ADR 48-cli](48-cli-first-class-release.md)），不是第四套部署产品。

| 部署面 | 谁在用 | 注册 | 数据与密钥 | Gateway |
|---|---|---|---|---|
| **本机 Desktop（默认）** | 单人、本机 | **零注册** | 数据在用户机器（`~/.peer-agent` 语义）；密钥走 OS 保险箱；执行与 Evidence 本地 | 不需要 |
| **内网自托管** | 个人电脑或内网节点 | 注册系统**可关**；可后接 LDAP / OIDC | 仍在用户侧节点 | 可选；同一套 Runtime |
| **远程连接** | 人在远端驱动用户侧节点 | **需要注册** | 认知与密钥**默认不**上云 | 只做会话路由、注册与授权 |

#### 1.1 本机 Desktop（默认）

- 安装即可用，不强制账号、不强制联网注册。
- 配置、会话、Goal、Evidence、用量落在用户机器；路径语义为 `~/.peer-agent`（与 CLI 共享，不为某一宿主另起数据根）。
- 密钥与 OAuth 只进 OS 保险箱 / Credential Helper，不进业务库、不进云同步默认集。
- 能力执行与 Evidence 只发生在本机节点。

#### 1.2 内网自托管

- 可在用户电脑或内网部署**同一套** Runtime，可选挂 Gateway。
- 交付优先一键 / 单二进制或 Docker，降低内网落地摩擦。
- 注册可以关闭；组织需要身份源时再接 LDAP / OIDC，不把公网账号做成内网前提。

#### 1.3 远程连接

- 需要用户注册。账号只做三件事：身份、设备绑定、权限委派（谁能控哪台节点、哪些 capability）。
- 账号**不是**默认把对话、工作区、密钥或 Evidence 搬上云的同步开关。
- 远端入口是新界面，不是新执行内核；远程通道权限不得高于本机已授权面。

### 2. 核心原则：执行与 Evidence 留在用户侧节点

```text
执行与 Evidence 仍在用户侧节点。
Gateway / 云端只做会话路由、注册与授权。
```

这与治理基线一致：模型是认知角色，不是部署位置；本机（或用户明确部署的节点）持有能力、授权与 Evidence。

任何部署面都必须走现有 Permission → Evidence 链。禁止：

- Gateway 或云端直接执行本机能力；
- 为远程入口另开无 PermissionGrant / Evidence 的控制通道；
- 用账号会话、IM 消息或 prompt 摘要代替 Tool Result / Evidence；
- 把密钥、Vault 主密钥或未脱敏 Evidence 默认同步到云。

远程操作产出的 Evidence 与本机同源，桌面端可完整审计。出站优先、入站默认禁（ADR 31）仍然有效；内网 Gateway 若开入站，必须显式部署、显式配对，不得做成隐藏控制面。

### 3. 按数据种类混合存储，禁止大爆炸迁库

存储按**数据种类**选型，不按「全部进 SQLite」或「全部继续 JSON」一刀切。本文不规定一次迁完。

| 种类 | 真相源 | 说明 |
|---|---|---|
| Peer-Knowledge / ADR / playbook / release notes | **Markdown + Git** | 知识仓与发版叙述继续以 Git 为真相；不迁入业务库 |
| 配置、密钥引用 | **文件 + OS 保险箱** | 元数据可在 `~/.peer-agent` 文件；秘密只走 Vault / Helper。不进业务库 |
| Evidence / 截图 / DOM 等大对象 | **文件系统 + `artifact_ref`** | 对象本体在盘上；索引只持引用。不把大 blob 塞进 SQLite |
| 用量统计、会话 / Goal 索引、需筛选聚合的结构化状态 | **SQLite** | 适合查询、过滤、聚合。过渡期允许 JSONL 追加 + 定期汇总，再收口到 SQLite |
| 对话正文 | **先文件 / JSON** | 保持现有会话落盘。需要跨会话检索时再迁库，或旁挂 SQLite 索引，正文仍可留在文件 |

补充约定：

- 现有 JSON / JSONL store（会话、Automation、用量账本等）继续合法，直到对应种类按上表收口。
- SQLite 是索引与结构化状态的选项，不是新的执行真相，也不是 Evidence 本体仓库。
- 跨设备同步若出现，必须显式投影 portable 子集（ADR 62 已对 Automation 写过 device-bound）；不得整目录复制路径、授权和密钥。
- 知识仓（本仓库）与代码仓文档继续 Markdown；Agent 与人的决策面不进运行时数据库。

---

## 非目标

- 不在本 ADR 实现 Gateway、注册服务或远程入口代码。
- 不强制本机模式注册；默认 Desktop 继续零账号可用。
- 不把 Peer-Knowledge（及 ADR / playbook / release notes）迁入数据库。
- 不定具体云厂商、不选公有云区域、不绑某一家 BaaS。
- 不把 Desktop / CLI 拆成两套 Runtime，也不为 CLI 另起数据根。
- 不在本文展开正式 **Linux Desktop** 包装（electron-builder + CI + updater）。该包装是独立产品 / 打包轨道，排在 `0.0.12` Workbench 浏览器 keep-alive 修复经验证之后；见下文相关后续。
- 不把第三方 IM 桥定为远程连接第一刀（探索稿可继续作对照，不改写本文顺序）。
- 不规定会话正文必须立刻进 SQLite，也不规定用量 JSONL 必须在某一版本消失。

---

## 后果

### 正向

- 本机默认路径保持「打开就能干活」：无注册门槛，数据与密钥不过云。
- 内网与远程是同一 Runtime 的拓扑扩展，而不是新的认知 / 执行产品。
- 账号语义收窄为身份与授权，避免「上云 = 默认同步大脑和钥匙」。
- 存储按种类演进：Git 继续服务知识，文件系统继续服务大对象，SQLite 只吃真正需要查询的结构化面。
- 后续 Gateway / 注册实现必须对齐主链，评审时有明确否决项。

### 代价

- 三套部署面要共用 Runtime 契约，Gateway 不能长成第二执行器。
- 内网「可关注册 + 可接 LDAP/OIDC」会增加配置面，必须晚于单机数据面理清再做。
- 混合存储意味着一段时间内 JSONL / 文件 / SQLite 并存；查询层要能说清哪一种是索引、哪一种是本体。
- 远程连接一旦做，设备绑定与 capability 委派会碰到账号、节点与 PermissionGrant 的交叉，需要后续专文，不能在实现时临时发明。

### 明确不采用

| 选项 | 原因 |
|---|---|
| 本机也强制注册 | 破坏默认 Desktop 与首启路径 |
| 默认把会话 / 密钥 / Evidence 同步到云 | 账号职责越权；违反 local-first |
| 为远程另开无 Evidence 的控制通道 | 旁路主链 |
| 知识与 ADR 进业务库 | Git 已是真相源；迁库损失评审与可 diff 性 |
| 大爆炸「全部 SQLite」 | 大对象与知识不适合；迁移窗口不可控 |
| 先做公网注册再做内网 | 与已对齐顺序相反；内网应能关注册 |
| 本 ADR 顺便做 Linux Desktop 包装 | 打包轨道独立，且排在 0.0.12 keep-alive 验证之后 |

---

## 落地顺序

实现未开始。接受本文方向后，代码仓按下列顺序开工；每一步仍先对照主链，再写代码。

1. **理清单机数据面**  
   盘点 `~/.peer-agent` 语义下现有文件 / JSON / JSONL；标出哪些保持文件、哪些可加可选 SQLite 索引、哪些禁止进库（密钥、知识、大对象本体）。不在这一步引入 Gateway。

2. **强化可嵌入 Runtime host**  
   沿 ADR 54 / open runtime：同一套 Runtime 能被 Desktop、CLI 与后续内网进程托管，而不是先写云端壳。

3. **内网 Gateway MVP**  
   设备配对、会话路由；**可暂无公网注册**。注册开关默认关。不在这一步绑定云厂商。

4. **再加注册与远程连接**  
   账号 = 身份 + 设备绑定 + capability 委派。执行与 Evidence 仍在用户侧节点。远程入口只投影已有任务 / 授权 / 证据，不另建执行真相。

### 相关后续（非本文实现）

正式 Linux Desktop 包装（electron-builder 目标、CI 矩阵、自动更新通道）是独立打包轨道。排期前提：`0.0.12` Workbench 浏览器 keep-alive 修复已经验证。需要时另开产品 / 打包文档或 ADR，不在本文展开。

---

## 验收（方向评审，非实现门）

本文被接受（方向 Accepted、状态仍可为 Proposed 直到实现开工）当且仅当评审同意：

- 默认 Desktop 零注册；远程才要账号。
- Gateway / 云端不得成为执行或 Evidence 真相。
- 存储按种类混合；知识留在 Git；无大爆炸迁库。
- 落地顺序为：单机数据面 → 可嵌入 Runtime → 内网 Gateway MVP → 注册与远程。
- Linux Desktop 包装不在本 ADR 范围。
