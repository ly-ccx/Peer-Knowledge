# ADR 86：已持久化对话的批量读取

创建时间：2026-10-02
最后更新：2026-10-02
状态：Accepted（RC-01，负责人已授权自主完成全部实现与自测）

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
