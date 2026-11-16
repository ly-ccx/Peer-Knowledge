# 本地运行时隔离详细设计 v1

创建时间：2026-11-11
最后更新：2026-11-16（与 ADR 129 / ADR 133 对齐：收窄为 Desktop-only 止损与 Desktop Shell ↔ 独立 Rust Core 进程接口契约；删除 Bun CLI/TUI sidecar，停止 TS 全量 M00–M14 二次内核重写）
状态：ADR128 的详细设计候选；本目录只定义设计，不包含运行时实现，不表示已接受、已重构或已通过产品验收。

上游：[总体设计](../../architecture/local-agent-system-blueprint.md)、[ADR128](../../decisions/128-local-runtime-isolation-and-bounded-query-contract.md)。本轮用户要求在开始重构前补齐所有模块、接口、数据、依赖、队列和恢复，并完成自上而下审查。该要求覆盖原先“各实施阶段再补详细设计”的安排。

## 阅读顺序

| 文档 | 决定的内容 |
|---|---|
| [01 协议与命令交付](01-protocol-and-command-delivery.md) | 类型、方法目录、来源、回执、错误、版本、订阅 |
| [02 模块合同](02-module-contracts.md) | 每个逻辑模块的输入输出、owner、依赖、顺序与异常 |
| [03 读模型](03-query-models.md) | 每个 View 的字段、索引、版本、增量、重建和分页 |
| [04 队列与资源](04-queues-and-scheduling.md) | 固定容量、保留通道、调度、期限、溢出和释放 |
| [05 存储与恢复](05-storage-and-recovery.md) | 物理归属、命令日志、锁、提交、崩溃点与旧数据 |
| [06 宿主与平台](06-host-and-platform.md) | Desktop Shell、Rust Core 进程接入、Broker、凭据、打包、代次（已删 Bun CLI/TUI sidecar） |
| [07 迁移与验证](07-migration-and-verification.md) | 生产入口映射、切换顺序、删除项与验证矩阵 |
| [审查回执](../../experience/runtime-isolation-detailed-design-review.md) | 自上而下审查、发现、修订、闭环与剩余验证限制 |

## 规格规则

代码块是接口 IDL，引用既有 Protocol 类型，不是另一套可执行代码。未重列的字段沿所引协议的现行定义；现有业务行为不因换为异步接口改变。所有方法只允许本文列出的参数和结构，拒绝额外字段、访问器、原型对象和未登记方法。

默认容量是本候选的确定设计值，不是已测量的性能保证；实现不得自行放宽或另选算法。容量、数据字段、排序、重试和恢复语义的修改必须回写本目录及 ADR128，再评审。配置可取更低上限；不得通过降低任务总轮数/执行预算、丢弃输入或清历史满足这些容量。

没有允许实现者临时决定的 `TBD`、任选 Adapter、未指定队列或自动成功回退。平台能力/性能/打包是否符合规格仍须实现验证；失败时修改设计或保留具体阻塞，不能临时换执行或恢复语义。

## 现行决策

本轮再次核对 `00-adr-map.md`、85、96、98、101、102、`104-progressive-interaction-and-coordination-storage.md`、112、115、116、120、121、126、127 和当前 ADR128。新增的耐久命令接收日志、异步 Repository 及内部执行上下文也属于 A 级提案，已在 ADR128 标注，不伪称原同步 Interface 只是搬迁。

保留 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。保留原 Work/Intent、GoalPlan、Conversation、Policy、Control、Claim、Verification/Acceptance 真源；命令日志只拥有接收/路由/对账状态，读模型只拥有派生状态。`113-checkpoint-content-addressed-storage-and-retention.md`、`123-main-bot-unnoticed-memory.md` 的未接受部分不在本次授权中。
