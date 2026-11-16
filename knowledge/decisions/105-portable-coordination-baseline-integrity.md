# ADR 105：协调基线的可迁移内容证明

日期：2026-10-22
最后更新：2026-11-15（规范标注 `状态：Accepted` 并消歧 [ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md)）
状态：Accepted（协调基线可迁移内容证明 `sealCoordinationBackup` / `legacy-seal.json` 已作为既定恢复契约采纳；发布验收另记）
级别：A（存储恢复契约）；实施前决策，发布验收另记。实现者自审，不宣称独立审查。
关联：[ADR 104-progressive](104-progressive-interaction-and-coordination-storage.md)、[治理基线](../architecture/20-architecture-governance.md)。用户已授权修复日志恢复并在发布前验证安装包；保留现有任务、对话、证据，不影响当前实例。

## 现场与问题

RC26 安装包恢复预检在私有副本遇到 `coordination_legacy_changed`。6,264 个既有文件的 SHA-256 全部保持一致。v2 manifest/head 的 legacyVersion 却绑定 dev、inode、size、mtime、ctime；文件复制改变机器身份，即使内容完整也无法恢复。直接修改这个标记会丢失对激活后旧写入者的保护。

## 决策与不变量

1. 保留 v1 原文、v2 manifest/head、事件链、任务和 Evidence 身份。新增内容证明，不重写既有激活标记，不回退旧快照执行。
2. 增加 `coordination-v2/legacy-seal.json`：schemaVersion、generation、原 legacyVersion、bytes、SHA-256。证明只绑定既有基线，不替代 v2 事件链、durable head、租约、PermissionGrant 或任务验收。
3. 在原文件物理身份仍与激活标记一致时，持有既有租约的 Runtime 可生成一次内容证明。哈希按有界块异步读取，前后验证源身份；证明 fsync 后原子发布。大日志解析与 SQL 重建继续走现有 worker seam。
4. 恢复到新文件身份时，prepare 必须用内容证明核对全部旧日志字节；并校验原 generation/legacyVersion、v2 链与 durable head。成功后只在可重建索引缓存当前物理 token 和证明摘要。后续正常读写保持 O(1) 身份检查，不反复扫描大日志，不写全量状态。
5. 索引删除、路径变化、inode/ctime 变化后重新验证。字节变动、证明不合法、代际不匹配、读取中源变化、缺失段/回执均保持失败关闭。未知工具结果不重放。

## 旧备份的受控过渡

旧 RC25 已激活副本没有内容证明，无法仅凭复制后大小、时间或派生 SQLite 断言它等同原始基线。

新增本地存储维护 Interface `sealCoordinationBackup({ sourceDirectory, backupDirectory })`：只读可信源，确认其物理身份仍匹配原激活标记（或已有内容证明），稳定计算源与副本的完整 SHA-256；确认副本 manifest/head 属于同一基线；仅在不同的备份目录补写证明。源目录、源租约与运行实例不得写入或接管。拒绝同目录、路径逃逸和别名指回源。

此 Interface 是本地存储备份维护 seam，不新增模型可见工具、renderer 文件访问或能力执行旁路。若未来将其开放成用户工具，仍须经过既有 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。

源不可用且备份无可信证明时，不能自动补造证明；保留原始数据并报告恢复阻塞。RC26 在原数据目录准备时生成证明，后续完整备份可随之携带。旧 reader 不认识新复制恢复路径，仍会失败关闭；不承诺旧二进制可恢复新文件身份。

## Module 边界

- 新深 Module 集中拥有内容证明格式、稳定哈希、只读源核验及备份证明发布；提高恢复排错的 Locality，给 Store 和备份维护复用提供 Leverage。
- Coordination Store 继续拥有租约、顺序、v2 事件和同步查询 Interface。prepare 为异步恢复门；不能把同步 read 改为隐式异步或执行恢复。
- Worker 的重建请求显式携带已核对的 legacy token/证明摘要；worker 在回放前后验证同一文件身份，并将核对回执写入派生索引。该回执不能代替原始证明或日志。
- 证明不是任务成功结论、模型指令、Tool Result 或新授权。System Context 与公开交互读取范围不变。

## 发布门禁

必须覆盖：已激活目录复制（含/不含索引）、索引重建、同字节文件替换、同长度改写、缺失/错误证明、跨代证明、读取中修改、源只读/目标隔离、原文件不改、用量精确去重与未知调用保留。维持既有日志线性增长、段丢失、崩溃、租约与 checkpoint 测试。

最终 RC26 必须对合并后源码完整回归并逐图审阅；实际候选和官方安装包在私有副本恢复，逐字节比对全部原文件、任务/对话身份和 Evidence refs。维护证明写入只发生在私有副本；当前已安装实例不安装、不重启、不接管租约。
