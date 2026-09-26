# 项目代理记忆体系

创建时间：2026-09-24
最后更新：2026-09-24

> 状态：随 ADR 81 Accepted（2026-09-26）。§16 已关闭。简报预算以 6000 字符为准。  
> 级别：A 级（上下文准入、存储边界、System Context 来源、能力暴露）  
> 关联决策：`knowledge/decisions/81-project-agent-memory-system.md`、`knowledge/decisions/80-project-agent-delegation-model.md`  
> 关联文档：
> - `knowledge/architecture/project-agent-delegation-runtime.md`（调度工具、`DelegationOrigin.contextRefs`）
> - `knowledge/architecture/project-agent-capability-layers.md`（七层模块；本文新增记忆模块组）
> - `knowledge/architecture/19-system-prompt-context-architecture.md`（L0–L7 分层、`ContextAttachmentItem`）
> - `knowledge/architecture/00-engineering-philosophy.md` §五（个人记忆只能作为辅助上下文）
> - `knowledge/decisions/74-deployment-surfaces-and-local-storage.md`（按数据种类混合存储）
> - `knowledge/decisions/17-local-context-compaction.md`（压缩不是记忆）
> - `design/product/peer-2-0-product-system.md` §13（四层记忆的早期设想）

---

## 0. 一句话

项目代理要跨天、跨任务地「记得这个项目和这个人」。记忆是**带来源、可验证、会过期、可撤销的事实记录**，只以事实上下文进入模型，不是系统指令，也不能给任何人权限。已验证的事实和用户亲口说的话自动生效，推测出来的东西要攒够证据或经用户确认才生效；用户随时能看见、能改、能撤。

---

## 1. 为什么项目代理必须有记忆

没有记忆时，项目代理有四个硬伤：

1. **对话无限长**：代理对话常驻，压缩只保证连续性，不保证「三周前定下的那个决定」还能被找回。
2. **每条任务从零开始**：任务要重新探查测试命令、目录约定、上次踩过的坑，浪费轮次，还会重复犯错。
3. **听不懂指代**：「之前那个面板」「上次发布的方式」需要知道过去发生过什么。
4. **学不会这个人**：用户说过三次「只说结论」「发布前让我看」，下次还是要再说。

这正好对应产品价值里的「少解释」和「越用越顺」。

---

## 2. 记忆不是什么

先划清边界，避免一套东西冒充另一套：

| 东西 | 是什么 | 和记忆的关系 |
|---|---|---|
| 会话历史 | 双方说过的原话 | 记忆的**来源**之一，不是记忆本身 |
| 压缩摘要（ADR 17） | 一条会话窗口内的连续性 | 窗口满了之后的续命；不跨会话、不跨任务 |
| 项目指令（AGENTS.md 等，`L3_INSTRUCTIONS`） | 用户写下、受 Git 评审的规则 | 优先级高于记忆；记忆只能**建议**写进去，不能自己写 |
| GoalPlan / Runner 检查点 | 单个任务的执行现场 | 任务级工作记忆的真源，记忆体系只读它 |
| Evidence | 某件事确实发生过的证明 | 记忆**引用**证据来证明自己，不复制证据 |
| Skill | 打包好的做事方法 | 被反复验证的程序性记忆可以提议成 Skill Patch（路线图 #10），需评审 |
| 权限 / 签收策略 / 项目设置 | 运行时的治理配置 | 记忆**只能让它更严，不能让它更松**（§8） |

---

## 3. 五类记忆

按「记的是什么、归谁、活多久」分五类：

| 类 | 作用域 | 记什么 | 例子 | 真源 |
|---|---|---|---|---|
| **任务工作记忆** | 单条任务 | 目标、计划、检查点、阻塞、下一步 | 「S3 卡在复现环境，已补复现步骤」 | GoalPlan + Runner（已有，不新建） |
| **对话事件记忆**（episodic） | 项目 | 每一次「用户说了什么 → 代理怎么处置 → 结果如何 → 用户怎么反应」 | 「9/24 用户要按天分组，中途改为按模型；已签收」 | 事件卡（§4.2） |
| **项目语义记忆** | 项目 | 事实、决策、约定、踩坑、当前局面 | 「desktop 测试要先 build 各包 dist」「用量面板按本地时区切日」 | 记忆条目 |
| **程序性记忆** | 项目 | 被验证有效的做法 | 「改 renderer UI 后跑 typecheck + 相关单测 + 截图对比」 | 记忆条目（可晋升 Skill Patch） |
| **用户协作记忆** | 用户（跨项目） | 语言、汇报粒度、确认偏好、风格 | 「只说结论」「对外发布前一定让我看」 | 记忆条目 |

「当前局面」（进行中的大事、已知问题、发版进度）归项目语义记忆里的 `state` 类，它变化快，默认短有效期。

---

## 4. 数据模型

落点：`packages/protocol/src/memory.ts`。现有同名文件里的 `WorkingMemory*` / `MemoryWiki*` 是旧远端接口遗留，全仓无引用，由本节契约替换。

### 4.1 记忆条目

```ts
type MemoryScope =
  | { kind: 'project'; workspaceId: string }
  | { kind: 'user' };

type MemoryKind =
  | 'fact'        // 事实：命令、路径、结构、版本
  | 'decision'    // 决策：为什么这么做
  | 'convention'  // 约定：这个项目习惯怎么做
  | 'pitfall'     // 踩坑：什么会出错、怎么避开
  | 'procedure'   // 做法：被验证有效的步骤
  | 'state'       // 局面：进行中的事、已知问题（短有效期）
  | 'preference'; // 用户偏好（只在 user 作用域）

type MemoryTrust =
  | 'verified'    // 有可解析的 Evidence 支撑
  | 'stated'      // 用户亲口说的
  | 'inferred';   // 代理从现象推断

type MemoryStatus = 'candidate' | 'active' | 'stale' | 'superseded' | 'revoked';

interface MemoryItem {
  id: string;
  scope: MemoryScope;
  kind: MemoryKind;
  statement: string;              // 一句陈述句，能单独读懂
  detail?: string;                // 可选补充（markdown，限长）
  subjects: string[];             // 检索锚点：路径、模块、主题词
  provenance: {
    origin: 'task_outcome' | 'user_statement' | 'user_correction' | 'agent_observation' | 'repeated_behavior';
    sourceRefs: string[];         // messageId / sessionId / planId
    evidenceRefs: string[];       // 必须能在 EvidenceIndex 解析；verified 至少一条
    fromUntrustedContent: boolean; // 陈述来自网页 / MCP / 文件内容时为 true（§8.3）
  };
  trust: MemoryTrust;
  status: MemoryStatus;
  sensitivity: 'normal' | 'sensitive';
  validity: {
    observedAt: string;
    lastConfirmedAt: string;
    expiresAt?: string;           // state 类默认 14 天
    anchors?: { path: string; contentHash: string }[]; // 文件变了就要复核（§7.1）
  };
  usage: { retrievedCount: number; lastUsedAt?: string; helpful: number; harmful: number };
  pinned: boolean;                // 用户固定进项目简报
  supersedes?: string[];
  conflictsWith?: string[];
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

### 4.2 事件卡（对话事件记忆）

锚定回复模式天然给了事件边界：一条用户消息及其派生的全部任务、回复、插话，就是一件事。

```ts
interface MemoryEpisode {
  id: string;
  workspaceId: string;
  anchorMessageId: string;
  userAsk: string;                // 用户原话（截断）
  dispositions: MessageDisposition[]; // 回答 / 开任务 / 并入 / 取代 / 停止…（运行时契约 §2.6）
  sessionIds: string[];
  outcome: 'answered' | 'delivered' | 'partially_delivered' | 'stopped' | 'superseded' | 'reopened';
  verdicts: { sessionId: string; outcome: 'passed' | 'partial' | 'failed' }[];
  userReaction?: 'accepted' | 'corrected' | 'praised' | 'none';
  summary: string;                // 两三句
  derivedMemoryIds: string[];     // 这件事沉淀出的记忆条目
  openedAt: string;
  closedAt: string;
}
```

事件卡在锚点下所有任务结束（或纯回答完成）时生成。它是记录，不是指令，所以自动写入。

### 4.3 项目简报

每个项目一份生成物（不是真源）：从活跃条目中挑最重要的若干条，按类分组渲染，控制在约 800 tokens。用户固定（`pinned`）的条目必进。条目变化后后台重建。

---

## 5. 写入路径：记忆怎么形成

### 5.1 触发源

| 触发 | 产出 | 谁提取 |
|---|---|---|
| 任务结束（`session_verified` / 签收） | fact / decision / pitfall / procedure 候选，带任务证据 | Memory Curator |
| 修复循环收敛（`blockerAudit` 指纹被解决） | pitfall 候选：「X 会失败，原因 Y，解法 Z」 | Memory Curator |
| 用户明说「记住…」「以后…」 | stated 条目 | 项目代理调用 `memory_remember` |
| 用户纠正（「不对」、打回、撤销签收） | pitfall / 修订已有条目；被用过的记忆记一次 harmful | Memory Curator + 运行时 |
| 用户重复同一种反应（多次要结论、多次要求过目） | inferred preference 候选 | Memory Curator 按计数 |
| 锚点事件结束 | 事件卡 | 运行时直接生成摘要骨架，Curator 补两三句 |

### 5.2 Memory Curator

提取不在项目代理的回合里做，避免拖慢对话、挤占代理上下文。Curator 是一个后台只读子 agent：

- 画像：新增 `memory_curator`（AgentProfileRegistry），只读工具 + 读取任务报告、证据摘要、事件卡；P3 优先级，走子 agent 池；默认用「省」档模型（ADR 83），受项目模型范围约束。
- 输入：一件事的事件卡、相关任务的 `SessionReport` 与 `VerificationVerdict`、现有相关记忆（去重与冲突检查用）。
- 输出：结构化候选 JSON（`MemoryCandidate[]`），不直接写库。
- 运行时校验：字段完整、`evidenceRefs` 可解析、`statement` 长度与格式、敏感信息扫描（复用 shell-redaction 的规则）、来源是否含不可信内容。校验不过的候选丢弃并记日志。

### 5.3 准入策略：MemoryAdmissionPolicy

与签收策略同一个思路：能自动的自动，该问的才问，所有变化可见可撤。纯函数 `decideMemoryAdmission(candidate, existing, projectInstructions, userPrefs) → 'activate' | 'candidate' | 'reject'`：

| 条件 | 决定 |
|---|---|
| `trust = verified`，证据可解析，非敏感，不与活跃条目或项目指令冲突 | **自动生效** |
| `trust = stated`（用户亲口说的），且不涉及权限 / 费用 / 范围扩大 | **自动生效**，回复里一行确认「记住了：…」 |
| 事件卡 | **自动写入** |
| `trust = inferred` 的偏好 | 同类现象 ≥ 3 次才生效，生效时告知一次「以后默认这样，可撤销」；不足 3 次保持候选 |
| 与已有活跃条目冲突 | 新证据是 verified 或 stated 且更新 → 取代旧条目（旧条目 `superseded`，保留）；否则留作候选，等下个自然时机问用户 |
| 与项目指令（AGENTS.md）冲突 | 不生效；代理建议「要不要改 AGENTS.md」，改就开任务走正常治理 |
| 敏感内容（凭据、密钥、个人信息） | **拒绝**，不落盘 |
| 试图放宽权限、签收策略、验证下限或预算 | **拒绝**，并告诉用户这类事要改项目设置 |
| 陈述来自网页 / MCP / 文件内容等不可信来源，且类型是 convention / preference / procedure | **拒绝**（防提示注入）；fact 类可以作为 `verified` 以外的候选 |

### 5.4 写入的透明度

- 用户说「记住」→ 代理回复带一行「记住了：发布前一定让你确认。」
- 任务沉淀出新记忆 → 不打断，只在那条回复下挂一个收起的「新记住 2 条」标记，点开可看、可撤。
- 推断偏好生效 → 告知一次。
- 冲突需要问 → 代理在下一次汇报时顺带问，不单独打扰。

---

## 6. 读取路径：记忆怎么用

### 6.1 谁读、读多少

| 角色 | 读什么 | 预算（约） |
|---|---|---|
| 项目代理 | 项目简报 + 用户偏好 + 按本轮消息检索到的条目 + 按指代检索到的事件卡 | 1500 tokens |
| 任务（worker） | 与任务相关的 fact / convention / pitfall / procedure（开任务时冻结一份）+ 用户偏好中与交付相关的 | 1000 tokens |
| Explorer | 与问题相关的 fact / pitfall | 400 tokens |
| Verifier | 与验证相关的 procedure / pitfall | 400 tokens |
| Memory Curator | 与候选相关的现有条目（去重用） | 按需 |

### 6.2 检索：MemoryRetriever

分三路合并，后两路按需：

1. **常驻**：项目简报 + 用户偏好，每轮都带。
2. **按主题检索**：用本轮用户消息、任务目标、任务将触碰的路径做查询；SQLite FTS5 全文检索 + `subjects` 精确匹配 + kind 过滤；按「相关度 × 可信度 × 新鲜度 × 用得好的次数」排序，截到预算。本地向量检索是后续增强，不是 P1 前提。
3. **按指代检索事件卡**：用户消息里有「上次」「之前那个」「又」等指代，或引用了很早的消息时，检索事件卡。

### 6.3 准入：只作为事实上下文进入

- 记忆以 `ContextAttachmentItem { sourceKind: 'memory', scope: 'workspace' | 'user', lifecycle: 'durable_ref' }` 进入，由新的 `project-memory-source` 渲染到 **`L7_CONTINUITY`**，每条带来源标签：`[记忆 · 已验证 · 9/20 · 来源：任务「用量面板按天分组」]`。
- 永远不进 `L0`–`L6`。约定和偏好也只是「这个用户 / 项目的习惯记录」，不是系统规则。
- 优先级：当前用户消息 > 项目指令（L3）> 记忆。冲突时模型按高优先级来，代理顺带提示记忆可能过期。
- 标为 `stale` 或带 `needs_revalidation` 的条目若被检索到，渲染时加「可能过期」。

### 6.4 开任务时带上记忆

`spawn_session` 时，SessionSupervisor 调 MemoryRetriever 为这条任务挑一组相关条目，冻结成 `memorySnapshotId` 放进 `DelegationOrigin`：

```ts
interface DelegationOrigin {
  // …已有字段
  memorySnapshotId?: string;   // 这条任务开出时用了哪些记忆（条目 id + 版本）
}
```

冻结的意义：任务执行期间记忆变了不影响这条任务；事后能回答「这个任务当时依据了哪些记忆」。

### 6.5 用了哪些记忆：可追溯

每次检索写一条使用记录（哪一轮、哪些条目、什么版本）。用途：

- 用户问「你为什么这么做？」→ 代理能指出依据的记忆及其来源；
- 回复上挂收起的「参考了 2 条记忆」标记；
- 上下文用量面板（ADR 42 / 56）里单列记忆占用；
- 反馈：用了某条记忆后用户纠正了结果 → 该条 `harmful + 1`，达到阈值转候选复核。

---

## 7. 维护：过期、冲突、遗忘

### 7.1 过期检测

- **文件锚点**：fact / convention / procedure 写入时记录相关文件的内容哈希。Curator 空闲时比对：文件变了 → 条目标 `needs_revalidation`，下次被检索时标「可能过期」，Curator 用只读工具复核后转回 `active` 或 `stale`。
- **有效期**：`state` 类默认 14 天过期；其他类无固定有效期，靠锚点与使用反馈。
- **项目指令变更**：AGENTS.md 变了，重新跑一遍与项目指令的冲突检查。

### 7.2 冲突

- 同一 `subjects` 下出现矛盾陈述 → 按准入策略：新的 verified / stated 取代旧的；否则候选 + 冲突标记。
- 取代保留旧版本（`superseded`），可以追溯「以前以为是 X，后来发现是 Y」。

### 7.3 遗忘与衰减

- 长期未用、低重要度的条目退出项目简报，仍可检索。
- 事件卡按月卷成月度摘要，原卡保留可检索。
- 每个项目有条目总数与简报长度上限，超出时按「最久未用 × 最低可信度」先退出简报。
- 用户「忘掉这个」→ `revoked`（可恢复）；「彻底删除」→ 物理删除该条及其版本，并记一条删除事件（不含内容）。

---

## 8. 治理红线

1. **记忆不是指令**：只进 `L7_CONTINUITY` 事实层；不自动写 AGENTS.md，不自动改 Skill，不改系统提示。
2. **记忆不给权限**：偏好和约定只能让签收策略、确认要求更严（例如「发布前让我看」→ 对外操作一律 `confirm`），不能让它更松；不能授予 PermissionGrant、提高预算、下调验证下限。这由 AcceptancePolicy 与权限审查在读取偏好时只接受「收紧」方向来强制。
3. **防提示注入**：来自网页、MCP 返回、文件内容、任务日志中引用的外部文本的陈述，`fromUntrustedContent = true`，不能成为 convention / preference / procedure；只能作为有证据的 fact 候选。
4. **不存秘密**：写入前做敏感信息扫描，凭据、密钥、token、个人隐私直接拒绝。
5. **本机、不上云**：记忆随 ADR 74 留在用户节点；远程 / 手机入口只能读投影，写入仍经本机准入。
6. **一切可见可撤**：每条记忆能看到来源、可信度、用了几次、最后一次什么时候；能改、能撤、能导出、能整体关闭。

---

## 9. 存储

按 ADR 74 的数据种类选型：人可读的文件是真源，SQLite 只是可重建的索引。

```text
~/.peer-agent/memory/
  user/
    items.jsonl                 # 用户作用域条目的版本事件（只追加）
  projects/<workspaceId>/
    items.jsonl                 # 项目条目的版本事件（只追加）
    episodes/2026-09.jsonl      # 事件卡，按月分文件
    brief.md                    # 项目简报（生成物）
    usage.jsonl                 # 检索使用记录
  memory-index.sqlite           # FTS5 + 过滤索引，可从 jsonl 全量重建
```

- `workspaceId` 用稳定的工作区标识，不用路径字符串，避免改目录后记忆丢失。现状：Desktop 工作区按路径识别，没有稳定 id（只有远程访问协议里有 `workspaceId`）。MM1 需在工作区设置里生成并持久化 `workspaceId`（UUID），与 ADR 80 的 `projectAgentConversationId` 放在一起；远程访问复用同一个 id；目录搬家时由用户在设置里重新关联，不按路径猜。
- 记忆不写进用户的代码仓。团队共享是远景：用户可以显式「导出为项目文档」，写成仓库里的 markdown，经 Git 评审后作为项目指令的一部分，而不是自动同步。
- 证据本体不复制，只存 `evidenceRefs`。

---

## 10. 能力暴露

记忆读写同样走 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。新增 `LocalMemoryProvider`：

| 工具 | 投影给谁 | 作用 | 约束 |
|---|---|---|---|
| `memory_search` | 项目代理、任务、Explorer、Verifier | 检索条目与事件卡 | 只读；结果带来源标签 |
| `memory_remember` | 项目代理 | 记下一条 | 必须带 `anchorMessageId`；锚点是用户消息且用户在表达「记住 / 以后」时才算 `stated`，否则按 `inferred` 进候选；过准入策略 |
| `memory_forget` | 项目代理 | 撤销一条 | 必须带 `anchorMessageId` 指向用户消息；只能 `revoked`，物理删除只能用户在界面上做 |
| `memory_explain` | 项目代理 | 某次决定依据了哪些记忆 | 只读，读使用记录 |

任务不能写记忆；Curator 不用工具写，只交结构化输出由运行时准入。没有任何工具能写项目指令文件。

---

## 11. 在七层里的位置

记忆是一组横向模块，和 L2–L6 都有接点：

| 模块 | 层 | 作用 |
|---|---|---|
| MemoryStore（jsonl 真源 + SQLite 索引） | 基座旁的存储 | 读写条目、事件卡、使用记录；重建索引 |
| MemoryAdmissionPolicy | L4（与签收策略同层） | 纯函数准入决定 |
| MemoryCurator | L1 画像 + L2 调度 | 后台只读子 agent 提取候选 |
| EpisodeBuilder | L3 / L4 | 锚点事件结束时生成事件卡 |
| MemoryRetriever + 项目简报生成 | L6 上下文 | 按角色与预算检索 |
| `project-memory-source` | System Context `L7_CONTINUITY` | 渲染带来源标签的记忆 |
| MemoryMaintenance（锚点复核、过期、衰减） | L5 旁 | 空闲时后台运行 |
| LocalMemoryProvider | L6 模型侧接口 | 四个工具 |
| 记忆面板、记忆标记 | L7 | 看、改、撤、固定、导出 |

---

## 12. 用户看到什么

- **回复上**：收起的「参考了 N 条记忆」（点开看条目与来源）；用户说「记住」后一行「记住了：…」；任务沉淀新记忆时收起的「新记住 N 条」。
- **右栏新标签「记忆」**：
  - 项目简报（可固定条目）
  - 事实与约定 · 踩过的坑 · 做法
  - 你的偏好（跨项目）
  - 最近形成 · 待确认 · 可能过期
  - 每条：陈述、可信度标记（已验证 / 你说的 / 推断）、来源链接（任务 / 消息）、最后使用时间；操作：编辑、撤销、固定、「写进 AGENTS.md」（开任务）
- **设置**：本项目记忆开关、是否自动学习偏好、导出、清空。
- **问答**：「你还记得我们怎么定的发布流程吗？」「你为什么这次先跑了 build？」都能答出依据。

---

## 13. 衡量

| 指标 | 含义 |
|---|---|
| 检索命中后被引用率 | 记忆真的被用上 |
| harmful 率 | 用了记忆后被用户纠正的比例 |
| 过期率 / 复核转 stale 率 | 记忆腐烂速度 |
| 用户撤销率 | 自动生效的准不准 |
| 任务探查轮次变化 | 有记忆后任务少走了多少弯路 |
| 简报与检索的 token 占比 | 记忆有没有挤占上下文 |

---

## 14. 建设顺序

接在 ADR 80 的 M1–M9 之后，也可与 M5 之后并行：

| 步 | 内容 | 退出条件 |
|---|---|---|
| MM1 | 工作区稳定 `workspaceId` + 契约（替换旧 `memory.ts`）+ MemoryStore（jsonl + 索引重建）+ `memory_search` / `memory_remember` / `memory_forget` + 记忆面板只读 | 用户说「记住」能生效、能检索、能撤销；索引删了能重建；工作区改名 / 换路径后记忆仍在 |
| MM2 | 事件卡 + 项目简报 + `project-memory-source` 进代理回合 + 开任务冻结 `memorySnapshotId` | 代理能回答「上次怎么做的」；任务开出时带上相关记忆；上下文里记忆带来源标签且只在 L7 |
| MM3 | Memory Curator + 准入策略 + 回复上的记忆标记 + 使用记录与 `memory_explain` | 任务结束自动沉淀已验证事实；推断偏好 3 次才生效；提示注入用例无法写入约定 |
| MM4 | 文件锚点复核 + 过期 + 冲突取代 + 衰减 + harmful 反馈 | 改了文件后相关记忆标「可能过期」并被复核；冲突按规则处理 |
| MM5 | 程序性记忆 → Skill Patch 候选（接路线图 #10）+ 导出为项目文档 | 反复验证的做法能提议成 Skill Patch 并走评审 |

---

## 15. 测试清单

- 记忆只进 `L7_CONTINUITY`；项目指令与当前用户消息优先于记忆。
- `verified` 条目证据不可解析时不能生效。
- 用户「记住」→ `stated` 生效；非用户消息锚点的 `memory_remember` 只能进候选。
- 推断偏好不足 3 次不生效；生效时有一次告知。
- 放宽权限 / 签收 / 验证下限 / 预算的记忆被拒绝；「发布前让我看」能让对外操作变为 `confirm`。
- 网页 / MCP / 文件内容里的「以后都这样做」无法成为约定或偏好。
- 敏感信息扫描命中时拒绝落盘。
- 文件内容变化 → 条目 `needs_revalidation` → 复核后转 `active` 或 `stale`。
- 取代保留旧版本；撤销可恢复；物理删除只能从界面发起并留删除事件。
- `memorySnapshotId` 冻结后，记忆变更不影响进行中的任务。
- 索引文件删除后可从 jsonl 全量重建且检索结果一致。
- Curator 输出校验失败的候选被丢弃，不写库。

---

## 16. 待评审点

已于 2026-09-26（P0-2）关闭，1–5 与 7 按原文采纳。第 6 点：项目简报的可执行预算是 6000 字符；§6.1 的 token 数只作量级参考。存储位置以 ADR 85 为准。
