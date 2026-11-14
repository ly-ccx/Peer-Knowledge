# 81. 项目代理记忆体系：带来源的事实记录，只进事实层，自动但可撤

创建时间：2026-09-24
最后更新：2026-11-14（仅修正历史文档引用；2026-09-26 P0-2 评审结论不变）

## 状态

Accepted（2026-09-26，P0-2）。实现未开工。

落地修订见 ADR 85：`workspaceId` 的真源是 `projects/registry.json`，与远程委托共用；项目记忆在 `projects/<workspaceId>/memory/`，跨项目用户偏好在 `memory/`；索引用运行时自带的 `node:sqlite` FTS5（trigram 分词），不新增依赖。

记忆架构文档 §16 的评审点按原文采纳，实现口径如下：

1. 已验证事实与用户明说自动生效；推断偏好要在 3 个不同片段里出现才生效，生效时告知一次。
2. 用户偏好跨项目共享；项目记忆按 `workspaceId` 隔离。
3. 记忆只进 `L7_CONTINUITY`。提取由后台 Curator 做，不在代理回合里做。0.1.0 不做向量检索。
4. 项目简报的可执行预算是 6000 字符（B3-06）。记忆文档 §6.1 的 token 数只作量级参考。
5. 旧 `packages/protocol/src/memory.ts` 直接替换。替换前确认全仓无 `WorkingMemory` / `MemoryWiki` 引用。

## 级别

A 级。新增上下文来源（`project-memory-source`，`L7_CONTINUITY`）、新增能力（`LocalMemoryProvider` 四个工具）、新增本机存储种类（`~/.peer-agent/memory/`）、新增稳定 `workspaceId`。

## 关联

- `knowledge/architecture/project-agent-memory-system.md`（完整设计）
- `knowledge/decisions/80-project-agent-delegation-model.md`（项目代理、锚定回复、验证与签收）
- `knowledge/architecture/archive/peer-agent-engineering-philosophy.md` §五（历史项目说明；当前准入规则以本 ADR 及后续有效修订为准）
- `knowledge/decisions/74-deployment-surfaces-and-local-storage.md`（按数据种类混合存储）
- `knowledge/decisions/17-local-context-compaction.md`（压缩不是记忆）
- `design/product/peer-2-0-product-system.md` §13（早期四层记忆设想，本 ADR 落地并修订）

## 背景

ADR 80 让一个常驻的项目代理替用户开任务、盯任务、汇报结果。代理对话无限长、任务一条接一条、用户的习惯要一次次重复说——没有记忆，项目代理只是一个换了壳的聊天窗。

现状：没有任何跨会话记忆。协议里的 `packages/protocol/src/memory.ts` 是旧远端接口遗留，全仓无引用。压缩（ADR 17）只保证单会话连续性。项目指令（AGENTS.md）是用户手写的规则，不会自己长。

## 决策

1. **五类记忆**：任务工作记忆（沿用 GoalPlan，不新建）、对话事件记忆（按锚点事件生成事件卡）、项目语义记忆（事实 / 决策 / 约定 / 踩坑 / 局面）、程序性记忆（被验证的做法）、用户协作记忆（跨项目偏好）。项目记忆严格按项目隔离；用户偏好跨项目。
2. **记忆是带来源的事实记录**：每条有来源（消息 / 任务 / 计划）、可信度（已验证 / 用户说的 / 推断）、有效性（观察时间、文件锚点、有效期）、使用记录。已验证的条目必须引用可解析的 Evidence。
3. **只进事实层**：记忆以 `ContextAttachmentItem { sourceKind: 'memory' }` 经 `project-memory-source` 渲染到 `L7_CONTINUITY`，带来源标签。永不进 `L0`–`L6`；约定和偏好也不升为指令。优先级：当前用户消息 > 项目指令 > 记忆。
4. **准入：自动但可撤**：已验证事实、用户亲口说的、事件卡自动生效；推断出的偏好同类现象 ≥ 3 次才生效并告知一次；冲突按「新的已验证 / 用户说的取代旧的」处理，否则留候选；与项目指令冲突不生效，改为建议修改 AGENTS.md（开任务走正常治理）。
5. **提取不占代理回合**：由后台只读子 agent（Memory Curator，P3 优先级）从任务报告、验证结论、事件卡提取候选；运行时校验证据、格式、敏感信息与来源后再过准入策略。
6. **记忆只能收紧，不能放宽**：偏好可以让签收策略、确认要求更严（如「发布前让我看」→ 对外操作一律 `confirm`），不能放宽权限、签收策略、验证下限或预算。
7. **防提示注入**：来自网页、MCP、文件内容等不可信来源的陈述不能成为约定、偏好或做法。
8. **会过期**：事实、约定、做法记录相关文件的内容哈希，文件变了先标「可能过期」再由 Curator 复核；「局面」类默认 14 天过期；用了记忆后被用户纠正计一次 harmful，达到阈值转复核。
9. **本机文件为真源**：`~/.peer-agent/memory/` 下的 jsonl（条目版本、事件卡、使用记录）是真源，`memory-index.sqlite`（FTS5）是可重建索引。不写进用户代码仓；团队共享只能显式导出为仓库文档、经 Git 评审。不上云。
10. **能力走同一条链**：新增 `LocalMemoryProvider`：`memory_search`（代理与任务只读）、`memory_remember` / `memory_forget`（仅代理，必须锚定用户消息；非用户明说只能进候选；撤销可恢复，物理删除只能从界面发起）、`memory_explain`（某次决定依据了哪些记忆）。没有任何工具能写项目指令。
11. **开任务时冻结记忆**：SessionSupervisor 为任务挑选相关记忆，冻结为 `DelegationOrigin.memorySnapshotId`，事后可追溯。
12. **稳定项目标识**：工作区设置新增持久化 `workspaceId`（UUID），记忆、项目代理、远程访问共用；目录搬家由用户重新关联。
13. **替换旧契约**：`packages/protocol/src/memory.ts` 里的 `WorkingMemory*` / `MemoryWiki*` 由新契约替换。

## 后果

- 代理能回答「上次怎么做的」「你为什么这么做」；任务开出时就知道测试命令、约定和已知的坑，少走探查轮次。
- 用户能在右栏「记忆」标签里看见、修改、撤销、固定每一条记忆；回复上会出现收起的「参考了 N 条记忆」「新记住 N 条」。
- 上下文里多了一块记忆占用，需要按角色设预算（代理约 1500、任务约 1000、Explorer / Verifier 约 400 tokens）并在上下文用量面板单列。
- 多了一类后台工作（Curator 提取、锚点复核、索引维护），走 ADR 80 的子 agent 池与 P3 优先级。
- 2.0 总纲 §13 的「用户确认或满足保守自动规则」具体化为本 ADR 的准入策略表。

## 不做什么

- 不做聊天向量库式的「全量记住」；会话历史是来源，不是记忆。
- 不让记忆自动写 AGENTS.md、改 Skill、改系统提示或授予任何权限。
- 不把记忆同步到云或手机云；远程入口只读投影。
- P1 不做本地向量检索。
- 不把团队共享记忆作为当前目标。
