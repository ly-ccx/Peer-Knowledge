# ADR 101：主 Bot 授权主体与子 Agent 动态继承

创建时间：2026-10-21
最后更新：2026-10-21
状态：Accepted（用户确认主 Bot 统一选权限、派生子 Agent 继承，并授权本轮先设计、评审再实现与测试；实现和验收事实另记，不以设计状态代替验收）
级别：A（权限主体、持久化、协议与撤回），B（Desktop/TUI、恢复与 IPC），C（权限入口）
依赖：ADR 49、80、84、85、89、90、91、92、100
局部取代：ADR92 §9.3 的“全局 settings.localAccessLevel 为 Bot 权限真源、不增加 Bot 权限存储”。ADR92 的角色限制、具体操作批准、图片许可及等待生命周期继续适用。

## 1. 用户问题与目标

任务子会话输入框显示可选“完全访问”，主 Bot 输入框没有权限入口。用户必须深入任务现场管理授权，且按钮看似属于一个子任务，实际改的是进程共享档位。用户明确要求：在主 Bot 对话选权限，所有派生子 Agent 会话继承主 Bot 的权限。

产品依据是“用户负责目标、边界与关键判断，代理持续推进，例外在主对话处理”，见 [产品对齐](../../design/product/peer-product-alignment.md)。本次不改变主 Bot 只读与调度职责，也不把 Full 解释成绕过计划、角色、拒绝规则或操作系统权限。

### 1.1 已核对代码事实（基线 8f0109d4）

| 事实 | 代码锚点（Peer-Agent 相对路径） | 后果 |
|---|---|---|
| `settings.localAccessLevel` 经 SettingsApplicationService 同步 SessionStore 与单例 PermissionGate | `apps/desktop/electron/main/settings-application-service.mjs`、`session-store.mjs`、`llm-chat-service.mjs` | 当前不是每 Bot 独立的权限 |
| 经典 ChatSurface 的下拉写全局设置 | `renderer/src/chat/hooks/useLocalAccessPreference.ts`、`chat/components/ChatSurface.tsx` | 子任务窗口会改别的 Bot 使用的策略 |
| BotComposer 仅接模型控制 | `renderer/src/project-agent/conversation/BotComposer.tsx`、`BotConversation.tsx` | 缺统一授权入口 |
| Desktop 权限门同时有全局 epoch、scope/source 缓存、图片资源许可、恢复单次批准 | `chat-runtime/permission-gate.mjs` | 仅改自动批准分支不够，旧批准可能继续生效 |
| 图片许可已解析宿主 GoalPlan 的父链，最长 4 层 | `runtime-node/src/project-agent/permission-inheritance.mjs` | 可复用身份检查，不能接受模型自称父会话 |
| TUI 每回合从全局设置构造独立 Host，内部仍有访问档位和批准缓存 | `tui/src/project-agent/tui-turn-executor.ts`、`tui-host.ts` | 只修 Desktop 会造成换宿主后权限变化 |
| 主 Bot 卡片、Attention 与经典窗口已共用 ApprovalStore 事实 | `project-agent-application-service.mjs`、`approval-conversation.mjs` | 继续同一批准链，无第二套请求 |

## 2. 决策与不变量

1. 授权主体为 `(workspaceId, 当前 profile.agentConversationId)`。Workspace 路径、显示名、worktree 路径、模型提供者、设备 SessionId 均不能替代这个身份。
2. 主 Bot 是本地用户管理权限的入口，不是许可签发者；权限仍由宿主为每次 Tool Call 生成 PermissionGrant，Provider 产生 Evidence。
3. 每 Bot 持有设备本地持久策略。子会话、Worker、Explorer、Verifier、视觉核验、恢复与嵌套委派动态读取同一主体的当前策略，不能独立保存更宽策略。
4. 继承授权档位，不等于继承任意一次批准。once 仍绑定具体调用；显式 scope/session 仍绑定具体能力、操作、主体和当前策略版本；图片资源许可仍绑定文件身份与期限。
5. Role / Mode / Goal / Probe / Automation / 显式 deny / 租约 / 取消先约束能力；档位只决定已准入调用是否需要用户批准。主 Bot 与只读 Verifier 不因 Full 获得写能力。
6. 不复制授权档位到 delegationOrigin 或 turnProfile。它们保存的宿主关系用于解析主体，调用执行时回读当前版本。
7. 普通独立会话继续使用经典全局策略；同一 Workspace 中的普通会话不因路径相同自动继承 Bot。
8. 新策略不得改变任一历史 ToolResult、Evidence、已执行副作用或已发送模型上下文的事实。

## 3. 权限语义

复用已有 LocalAccessLevel 枚举，不新增“继承”执行档位。继承是身份关系与界面状态。

| 档位 | 已准入本地动作的审批行为 |
|---|---|
| ask_before_local | 沿现有 Provider / PermissionReview 逐项询问；原本可直接读取的操作照常 |
| session_local | 沿现有自动批准规则；Desktop 与 TUI 对 Bot 的自动批准范围须一致，不能从名称推断全部写入获准 |
| restricted_local | 保留原受限语义；旧值能读取和显示，不静默转成 Full |
| full_local | 对通过能力与显式政策检查的调用生成当前操作 grant；不逐图询问，不覆盖 deny 或角色闸 |

所有 Bot 使用同一审批语义，换模型、窗口、worktree、执行宿主不会换权限。不会为统一语义而把 TUI 独立经典会话的既有产品行为无关扩大。

## 4. Module、存储与迁移

### 4.1 BotAccessPolicy Module

共享实现位于 runtime-node，Desktop/TUI 只装配可信的 ProfileStore、ConversationStore、GoalPlanStore 与数据根。Interface：

- `read(workspaceId)`：返回当前主体、档位、单调 revision、更新时间；只读投影不代表审批。
- `update({workspaceId, expectedRevision, accessLevel})`：仅本地用户入口调用；严格字段校验、CAS 更新、持久化成功后返回新快照；陈旧 revision 返回冲突和当前事实。
- `resolve({conversationId, workspaceId?, planId?, sessionId?, role?})`：由宿主身份解析 Bot 策略；普通独立会话返回“不适用”，无效委派返回结构化拒绝，不能回退到全局 Full。
- `valid(snapshot, identity)`：异步执行后、图片返回模型前重检主体与当前 revision；错误、删除、归档、换父、停止、降权均不匹配。

Module 深度在于集中处理跨进程持久权限、迁移、身份归属、版本失效与替换 seam；不能拆成只转发的多层包装器。策略查询不访问 UI，不依赖 BrowserWindow。

### 4.2 设备本地真源

在已登记的 `project-runtime/` 下保存 `bot-access.sqlite`，在 DATA_STORE_ENTRIES 注释明确登记其设备本地用途。SQLite 使用已有 Node/Bun SQLite 能力，不增第三方依赖；事务 + `BEGIN IMMEDIATE` + CAS 提供多进程顺序、持久 revision 和更改历史。不得使用会把损坏库自动重建的缓存数据库 helper。损坏/未知 schema/磁盘写失败返回 unavailable，不重建成宽权限。

每条策略绑定 workspaceId 与 agentConversationId；一张只追加版本表保留每个版本的档位、时间和来源（legacy_migration / local_ui / new_bot），最大 revision 投影当前快照。事务保证新版本与迁移标记一致，旧版本不被覆盖。历史是策略审计，不伪造具体 Tool Call 的 PermissionGrant 或 local_ui 操作批准。

权限不存入可移植 BotProfile、模型记忆、会话文本、压缩摘要或 renderer localStorage。设置导出不能顺带向新设备签发 Bot Full。

### 4.3 一次性迁移

首次打开策略库时，在一个事务内枚举当时已有的活动 Bot，把旧全局合法档位冻结为每 Bot 的 revision 1，记录 legacy_migration；非法旧值降为 ask。然后保存迁移完成标记。保留旧 settings 与会话/计划文件。

标准设置导入在复制任何 portable 数据前，如本机尚无 Bot 权限库，先写设备本地 `project-runtime/bot-access-imported.json` 标记。标记存在时首次迁移以 Ask 初始化导入的 Bot，不把 portable 的全局 Full 当成本机新授权；标记写失败时导入失败，不能先复制再补标记。已有本机策略库不由导入覆盖，父会话身份变化仍拒绝。标记只收紧首次迁移，不签发权限，也不随导出携带。

迁移标记之后首次出现的新 Bot 初始为 ask，写 new_bot；旧全局档位今后只影响经典独立会话，不能再次覆盖既有 Bot。重启、多个宿主同时初始化与失败重试必须幂等。策略主体与当前 profile 不匹配时拒绝，不能自动把旧 Bot 的 Full 转给新父会话。

回退旧版本时旧程序不读取新库，仍使用旧全局值；这会失去每 Bot 隔离，发布说明必须明确。再次升级以已保存 Bot 策略为准，不重新迁移、不删除新库。不同版本不能同时充当同一项目的执行宿主；既有租约规则继续适用。

## 5. 身份解析与执行链

```text
本地用户 → 主 Bot 权限控件 → typed IPC → ApplicationService
  → BotAccessPolicy 事务持久化 → 发布该 workspace 的变化

Provider → Manifest → Runtime Projection → Tool Call
  → 角色/计划/租约/取消/deny 检查
  → 宿主回读委派父链 → 当前 Bot policy revision
  → PermissionGrant → Provider 执行 → Evidence
```

主会话必须是当前 profile 绑定的 project_agent Conversation。子会话来自宿主存储的 parentConversationId / delegationOrigin；执行时核对 workspace、conversation、plan、session，检查计划执行当前性，逐级校验祖先，同一链最长 4 层，循环、断链、超限、跨 Bot、跨 workspace 直接拒绝。客户端/模型提交的 parentConversationId、accessLevel 或 policy revision 不是可信身份。

普通 Goal 保留自身会话身份。已完成/暂停任务可以展示历史继承来源，但展示解析不能替代执行许可；暂停、取消、被取代、租约转移后的执行仍由当前性闸门拒绝。

## 6. 策略变更、竞争与撤回

### 6.1 生效边界

持久事务提交是策略生效点。每个后续调用读取新版本，已创建 Worker 回合也不能一直使用回合开始时冻结的 Full。异步权限请求、文件读取、图片解码或等待期间版本发生变化，旧 grant 校验失败；尚未发生的副作用不得按旧许可启动。

已经启动的 shell/外部进程不能靠修改权限撤回已发生行为；本次不默认杀掉正在运行的命令。后续执行与输出交付按现有 Provider 合同检查，UI 说明当前策略适用于后续操作。Provider 在危险副作用前沿现有 executionGate / validate seam 重检。不可取消 Provider 的覆盖限制必须如实写入交接，不承诺跨 Provider 原子撤销。

### 6.2 缓存与批准

- scope 缓存、同 toolCallId 恢复桥、单次恢复簿的匹配键加入 Bot 主体与 revision。全局策略变化不得清除别的 Bot 许可或改变其 Full。
- 图片资源许可增加可选 policyRevision；迁移初始 revision 1 可以识别无该字段的旧合法资源许可，任意后续策略变更都使旧许可失效；不得把未审批历史补成授权。
- 同一档位重复保存不生成无意义新版本；真正变更（含升权）都失效旧版本批准，防止先降后升复活旧许可。
- 活跃批准绑定请求时的版本。改变策略不批量自动批准排队请求；旧请求按 policy_changed 关闭并返回结构化结果，新的调用按新策略重新判定。停止、超时、拒绝、重复/迟到动作依旧只有一次领取。
- 重启 stale 批准在生成恢复许可之前核对当前主体与版本；不符则关闭陈旧请求。计划批准与具体工具权限不同，不能因为改档位撤掉已签收计划或把计划批准当 Full。
- 图片继续上下文沿原 validate 绑定版本；降权后未交给模型的像素和缓存不可继续准入。
- 既有用户显式保存的长期 PermissionReview 规则保持其原始匹配范围和拒绝优先级；它们不是 Bot 档位自动签发的批准，不因新增继承机制扩散到额外能力或主体。

### 6.3 错误

typed 结果至少区分 INVALID_INPUT、NOT_FOUND、OUT_OF_SCOPE、POLICY_CONFLICT、POLICY_UNAVAILABLE。工具路径使用 access_policy_unavailable / access_identity_invalid / permission_policy_changed 等结构化原因。保存失败不先更新 UI 成成功，不签发许可；权限库读取失败也不能回退全局 Full。CAS 冲突展示最新事实，用户可以重试。

## 7. 产品交互与多入口

### 7.1 主 Bot

输入框工具栏增加权限选择，复用 SVG / Dropdown / i18n / 焦点规范，与模型、思考控件保持可读布局。提示“作用于此 Bot 及其所有子任务；主 Bot 仍按角色职责执行”。保存期间禁用重复提交；成功才展示宿主快照，失败保留原值并可重试；快速切 Bot 与晚到回执不串值。运行中可改权限，不要求停止全部任务。

### 7.2 子任务现场

经典 ChatSurface 中的 Bot 子任务替换独立权限下拉为“继承自主 Bot · 档位”只读状态，提供回到主 Bot 管理的入口。不能通过隐藏但仍生效的旧事件修改全局值。普通独立会话保留原下拉。读取本机既有权限事实不受 Bot/经典壳开关限制，避免经典壳把子任务误显示成独立全局授权；修改仍受 Bot 本地入口及模式准入约束。历史子任务仍显示实际当前来源，读取失败显示无法确认，不误标 Full。任务内部权限请求继续投影到主 Bot 卡片/Attention，经典窗口若打开则展示同一请求；任一入口决定只签发同一条 grant。

### 7.3 TUI / CLI / 远程 / 其它执行角色

TUI Bot 宿主在每次 Provider 审批读取同一设备策略库；不能由 TUI 全局切档悄悄改变 Bot。Bot 模式下本轮不新增命令式提权入口。连接 Desktop 的 TUI 使用宿主事实；独立 TUI 经典模式沿旧全局行为。远程仍只读策略事实，不增加远程批准或修改权限 API。Quick Chat 给 Bot 发消息使用 Bot 策略，不能附带客户端档位提权。无 Bot 身份的 Automation 使用自身显式政策；objective probe 仍只读。MCP/Skill/Plugin/桌面自动化不得获得额外执行路径。

## 8. 实施顺序与逐文件评审

详细实现卡及评审矩阵见 [落实评审](../../playbook/v0.1.0/bot-owned-access-policy.md)。顺序固定：

1. ADR 与调用点清点、自审收口。
2. Protocol + 共享权限主体/策略存储 + 迁移 + 版本测试。
3. Desktop 权限门三类请求器、缓存、批准恢复与 validate；TUI 同一 seam。
4. typed IPC / preload / ApplicationService，再做主 Bot 与子任务表达。
5. 真实 Provider 负向与并发测试、受影响包全测、build/typecheck/architecture/IPC 检查。
6. 完整标准截图包、逐图人工智能自审、verify；记录真实模型/安装版/无障碍覆盖限制。

## 9. 必须验收的反例

| 组 | 必须证明 |
|---|---|
| 主体 | Bot A Full、Bot B Ask、普通同目录会话、嵌套 worker、另一 worktree；不串用 |
| 生命周期 | spawn 前后改档、排队转执行、同一长回合下一次工具、暂停/取消/取代/租约丢失/恢复 |
| 版本 | 降权、升权、降后升、同值保存、并发窗口 CAS、另进程写入、等待中变更、旧批准迟到 |
| 持久 | 首次迁移 Full/Ask/restricted、非法旧值、新 Bot Ask、重复启动、迁移失败、损坏/未知 schema、磁盘失败、导出/回退/再升级 |
| 批准 | once 不扩散、scope 不跨操作、图片 TTL/文件变化、旧 revision 不恢复、计划批准隔离 |
| Provider | 真文件/Shell 权限请求、实际图片像素/Evidence、MCP/Skill/Plugin 同链、只读/显式 deny/probe/automation 拦截 |
| 表达 | 主 Bot 选项与保存失败、子任务只读继承、跨 Bot/窗口同步、键盘、窄窗深浅色、主对话收到子任务请求 |
| 多入口 | TUI fresh turn 与长回合读取新策略、宿主切换、远程不能提权、Quick Chat 无客户端提权 |

测试不得以模型“我有权限”或 UI 标签替代 PermissionGrant / Evidence。测试用受控认知提出调用可证明本地链路，不证明云模型质量。

## 10. 备选方案与代价

| 方案 | 结论 |
|---|---|
| 只把全局按钮移到 Bot 输入框 | 拒绝：不同 Bot 串用权限，子任务只是外观继承 |
| spawn 时复制 accessLevel | 拒绝：撤权不传播、恢复可能复活旧 Full |
| 每个子 Agent 独立配置且默认继承 | 本期不做：增加授权分叉，与用户统一入口目标冲突 |
| 权限放 BotProfile | 拒绝：可移植档案、通用修改入口与权限真源耦合，跨设备迁移易带出 Full |
| 新独立授权执行通道 | 拒绝：违反统一能力链 |
| 设备本地版本化 Bot 策略 + 动态解析 | 采用：增加存储/查询和迁移成本，换来权限归属、撤回与多宿主一致性 |

## 11. 评审与验收状态

本 ADR 的设计与实现评审由实施者逐路径自审，不称为独立审查。实现已完成；固定源码副本全工作区测试 8,557 passed / 5 既有 skipped / 0 failed，build、typecheck、architecture、IPC 均通过；原组合源码标准产品回归经 201 张逐图检查后 verify passed；最终代码 PR #177 独立提交重新全测，并完成 193 张逐图检查及 verify passed，提交与指纹见落实评审 §5.4。实际文件清单、首次失败与修复、源码/截图指纹和真实模型、安装版、无障碍覆盖限制见[落实评审 §5](../../playbook/v0.1.0/bot-owned-access-policy.md#5-实际验证记录)。共享目录其他在途重构不包含在此通过结论内。发布、合并、替换用户日常安装版不由本 ADR 自动授权。
