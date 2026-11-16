# ADR 86：已持久化对话的批量读取

创建时间：2026-10-02
最后更新：2026-11-15（补充与 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) 及 [ADR 121](121-desktop-session-windowing-contract.md) 的演进边界）
状态：Accepted（RC-01，负责人已授权自主完成全部实现与自测；注：Desktop 热会话打开与分页现已优先走 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md) 交互 SQLite 读模型与 [ADR 121](121-desktop-session-windowing-contract.md) 窗口契约，本文批量/高频只读 Seam 继续服务兼容读取、目录投影与 `getRuntimePolicy`）

## 问题

200机器人真实Desktop目录投影仍需137ms，超过100ms。逐项目调用ConversationStore.getPersistedConversationHistory会重复读取、规范化同一个200行会话索引。仅优化经典目标目录仍不能满足完整生产链路预算。

## 决策与Interface

新增存储模块内部只读接口getPersistedConversationHistories(ids)，返回Map，重复ID合并，已存在ID返回与单条读取相同的persisted history，未知ID为null。一次调用只读取一份当前会话索引，再逐文件通过既有readPersistedHistoryFiles读取；单条接口复用此Implementation。不缓存跨调用结果。

每份history保留conversationId、contentRevision、messages、excludedFromMessageId及requiresRuntimeCheck:true。Streaming sidecar指向的活跃消息及其后记录仍被排除。该批次不是跨文件事务，不能证明运行时静止、权限、Evidence或上下文可准入；既有调用方仍负责作用域和runtime attestation。

Portable目录增加可选readMessagesBatch内部端口，供list/query同一批投影使用；单项目详情、分页、标读保持单条实时路径，旧存储Adapter可以不实现批量方法。Desktop和规模测量通过该端口复用当前存储读取，首次搜索语料重建也用同一批读API。

Renderer仍只经已有IPC获取投影；没有新IPC、模型工具、能力、授权、存储格式或路径。canonical JSONL及sidecar归属、内容修订语义、Capability→PermissionGrant→Evidence链均保留。

## 验证

- 批量与单条history一致，含streaming排除和未知ID；一次批量读取索引一次。
- 下一次读取能看到外部写入和终态落盘，没有跨调用缓存。
- Desktop完整目录/搜索预算及消息分页实测；旧Adapter兼容。
- 完整build/test/typecheck/architecture及两平台CI。

## 同一准则应用于批准列表投影（2026-10-02，Accepted）

7d61baa0完整目录投影仍为101.88ms。ApprovalStore.list({workspaceId})每次都会扫描全部项目批准目录；200行列表因此重复扫描200次。新增listByWorkspaceIds(ids)只做一次既有foldAll，再按workspaceId分桶，返回Map。合并同approvalId的规则、state及scope与既有list完全一致；空批次不扫描，下次调用重新读取。

目录通过可选readApprovalsBatch消费此只读投影。批准决定、PermissionGrant与执行侧仍经原实时读取和验证，不能拿本批次作为授权真源。存储格式/落盘/状态迁移不变。测试批次目录扫描一次、与旧逐项目结果等价、状态变更下次可见、scope隔离。

## 高频运行策略的只读投影（2026-10-02，Accepted）

Mac CI 36909719055 的真实主线程 CPU profile 确认：ownsProject、Watch 与日常维护每次读取设置，都会通过 loadMigratedSettings/reconcileWorkspaceIdentity 对全部200项目执行 registry.sync→realpathSync。一次轮询30.8秒、CPU27秒；不是 Playwright 的断言或导航问题。不能加超时掩盖。

SettingsStore新增 getRuntimePolicy 只读 Interface：每次重新读取并解析当前 settings.json，只返回运行策略的 projectAgent 与 memory 字段。若 schema 仍需升级，沿现有 loadMigratedSettings 执行备份/原子迁移后再投影；schema 已是当前版本时，本接口不执行项目身份修复。没有跨调用缓存。getAll 与 merge 保持原身份修复、远程别名、数据迁移语义。

该投影只用于已有宿主开关、并发、主动性、安静时段、小结和记忆开关读取。不能包含或充当工作区 ID/路径/远程范围/PermissionGrant/Evidence 真源；这些仍由 Registry、Profile、Lease 与既有执行链逐次验证。Desktop装配增加可选 readRuntimePolicy，老Adapter回退getSettings；main只在原有一行装配注入，不新增逻辑、净增0行。Portable调用方原行为保留。

测试要求：两次读之间外部改写classic/记忆开关立即可见；返回值不含workspaces、remoteAccess、凭据；旧schema真实迁移与备份；200已迁移项目策略读取不触发注册表拓扑扫描，getAll仍修复身份；现有Classic/租约/记忆拒绝与真实窗口原预算、完整门禁必须继续通过。
