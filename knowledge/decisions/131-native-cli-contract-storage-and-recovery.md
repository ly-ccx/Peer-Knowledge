# ADR 131：原生 CLI 的跨语言契约、共享数据与恢复

创建时间：2026-11-14
最后更新：2026-11-17
状态：Accepted（2026-11-14 用户接受评审稿 118；正式编号 131；授权实施，不授权个人数据迁移、接管、安装或重启）
级别：A
依赖：[ADR 129](129-native-rust-cli-and-ratatui.md)、[ADR 130](130-bounded-cli-memory-and-transcript.md)

## 1. 问题

2026-11-16 NR-04模型OAuth条件提交：按[ADR0001原生模型OAuth修订](0001-cross-platform-credential-vault.md)先登记Helper可协商快照/CAS，再实现原生token读取、刷新和模型传输；不增加能力或本地执行授权。配置元数据不能取代实际Vault token，迟到刷新不得复活删除或覆盖新一代。模型配置完整写入、登录回执和提示投影恢复未验证前仍属于P4余项。旧Helper特性缺失须在远端效果前拒绝，原子Vault提交与失败保全需真实跨进程验证。

同日补强：远端刷新前先以同一加密token的`peerModelRefresh`意图争取唯一刷新者，未知结果保留意图并阻止自动重放；完成仅CAS自己的意图代。完整新旧宿主须迁移同一seam并验证，旧预读token的宿主不因新增字段自动变安全。该连续性事实不改变本地能力授权或Evidence，未完成多宿主兼容不记P4总闸。

CLI 改用 Rust 后，Desktop 与公开 Runtime SDK 暂时仍使用 TS / JS。机械翻译类型不能保持权限 digest、System Context checksum、工具配对、sidecar、宿主租约、SQLite CAS 或完成门一致。新的二进制也不能因为启动成功就接管旧任务。

本 ADR 将 ADR 55 / 57 的共享 Implementation 约束扩展为跨语言 conformance；保留 ADR 0001、35、37、49、65、74、76、80–85、88、92、98、100、101 的事实、权限、存储和恢复边界。`104-bot-capability-visibility.md` 在最新实施 checkout 仍为 Proposed，不随技术迁移被接受；同号的 `104-progressive-interaction-and-coordination-storage.md` 已接受，其日志 / writer 屏障 / 恢复契约继续保留，二者不能混称。ADR 115 页头已 Accepted，按其既有准入 / 草稿边界迁移当前 CLI 可达功能，不能继续沿用初次旧 checkout 的 Proposed 判断。

## 2. 单一工程契约

1. `packages/protocol` 保持现有公共契约归属。新增语言无关的 contract resources 与 fixtures，供 Rust / TS 共同消费；不另建由 Rust 私自维护的第二份协议仓库。
2. 先以现有已治理 Interface 和测试冻结 v1 schema / fixtures，再生成或校验 Rust 类型与 TS 类型；无法自动提取的 TS 类型必须逐项审阅。schema 只管形状，顺序、权限、幂等、错误和恢复规则另以可执行 fixture 表达。
3. 生成产物可提交以支持 Cargo 独立构建，CI 重生成对比，禁止手工维护相同常量的两份副本。契约版本独立标识于产品版本，根 VERSION 仍统一发布列车。
4. 导入共享 Context Source 的资源正文、layer / trust / priority、稳定排序、hash 输入及 snapshot 规则。宿主只投影事实，不在 Rust encoder 临时添加身份、mode 或 Skill 提示。
5. 以 ADR 57 的同一 canonical history 规范实现 Rust projector；顺序、工具配对、不完整历史、附件和 compaction 边界一致，再经 provider encoder lowering。展示分页不能改变模型上下文准入。
6. 明确区分展示兼容和执行兼容：未知可选展示字段可保留，未知权限枚举、未知控制消息、未知 checkpoint / schema 或执行 policy version 必须拒绝准入；不能默认 allow / success。

## 3. 必须冻结的等价性

| 合同域 | 验证要求 |
|---|---|
| 工具 Manifest / schema / mode / role projection | 同一配置与事实得到同一可见工具面；未投影工具在执行入口仍拒绝 |
| Context Source 与 history | 相同输入得到相同 section 顺序、正文 / hash、canonical tool pairing、history fingerprint 和预算归属 |
| 权限 | 相同主体、capability、args、scope、policy revision 得到相同审批要求与拒绝；过期 / 降权 / 撤回后不能命中旧缓存 |
| 生命周期 | 同一事实序列得到同一等待、yield、失败、取消、核验、签收和送达结果 |
| Provider wire | 固定 clock / IDs 后，请求与 SSE 归一化等价；error、空回复、截断、tool args 碎片、reasoning replay、usage 与重试政策不漂移 |
| 命令 / 外部协议 | argv、stdin、stdout、stderr、退出码、JSONL 与 ACP 能力协商保持已发布行为 |

特别注意：当前 `permission-operation.mjs` 使用对象 key 排序 + JavaScript JSON 序列化 + SHA-256，不是可以随意替换的“任意 canonical JSON”。Rust 必须对齐 UTF-16 key 排序、UTF-8 编码、number 格式、null / 缺失、数组顺序和异常输入；安全整数范围与时间单位显式约束。不得只用 serde map 默认顺序重算旧批准。不能一致表示的参数失败关闭；若要更换 digest 算法，需另记版本化授权兼容决策，不能默认复用历史 grant。

conformance 采用可分享合成数据，固定不确定量；同时以不变量断言防止“旧实现有 bug 就永久复制”。发现原契约冲突先修订 ADR，不通过修改 expected 输出隐藏行为变化。

## 4. 共享数据而不大迁库

- 根目录仍为 `PEER_AGENT_HOME` → `PEER_USER_DATA_PATH` → 用户默认 `.peer-agent`。不建立原生 CLI 专用事实根；测试候选使用显式隔离根。
- 会话 / JSONL、streaming sidecar、contextSnapshot、contentRevision、GoalPlan、协调日志、输入队列、批准、Bot policy SQLite、记忆及 FTS、artifact / Evidence 引用维持现有格式和语义。正文与大对象不因 Rust 迁为 SQLite blob。
- 新增的 viewport / offset index 只能是可重建 cache，按 DATA_STORE_ENTRIES 登记 scope、schema、失效和回退；不得重写原会话或把索引当 Evidence。
- 未知字段保留，不能把旧开放对象反序列化为窄 struct 后覆盖写回。canonical 正文、toolCallId、grantId、Evidence ref、inputId、reply receipt 和任务身份保持；不能重建为新的“等价会话”。
- 原子临时文件、flush / fsync、rename、锁顺序、目录布局、SQLite transaction / CAS、busy / schema / corruption 错误均与现有 Store 对齐。Node / Bun / Rust 对同一 SQLite schema 和 FTS tokenizer 做交叉实测，不因 Rust 选择 rusqlite 就假定兼容。
- 凭证继续经 ADR 0001 Helper v1 请求，保留相同 app 身份与 OS 授权边界；配置只持非秘密元数据及引用。

## 5. 写入所有权与锁

项目任务继续用现有 `host.lease` / yield / holdsLease 规则；Rust 宿主仍声明 surface=`tui`，不新增一个绕过互斥的 surface。Native / Desktop 同时打开时只能一个项目执行所有者，其他入口只提交持久输入与读投影，不能双跑 Supervisor / Watch / Goal。

项目租约不能代替所有 Store 的写锁。例如会话 Store 已使用 `${file}.lock` 目录互斥，异步多锁获取失败会释放已持有锁，再等待重试；原生实现必须参与同一锁命名和获取顺序，不能自行换为旧版不识别的 advisory lock。跨进程 stale revision、sidecar merge 与索引更新需分别测试。

当前目录锁无 owner 元数据，崩溃残留无法仅凭 TTL 或“没有租约”证明安全删除。原生首版对此失败关闭，报告具体锁与受阻写入；支持的恢复路径是离线维护：确认该数据根所有写入宿主已退出、保全锁及相关文件的诊断副本，再通过显式受控维护清理已核实的孤锁并重试原事务。无法确认所有权时不清锁、不重放，保留阻断。此方案不在本次文档阶段执行；若要自动回收，须先给新旧宿主统一补 owner / fencing 契约并评审。

对其他 Store，P0/P2 必须逐项登记已有互斥 / CAS / append 保证。发现竞态时按 Store seam 双端修复并记录接受条款，不能把“相同 JSON 格式”或“都用 Rust”当并发正确性的证明。未经证明的共享写域不开放生产写入。

## 6. 旧任务与中断恢复

恢复先读事实，再决定是否能继续。顺序：数据 / schema → 项目身份 → 当前所有者 / lease → 输入和回复幂等 → 未结算工具 / Evidence → policy / approval revision → checkpoint / provider compatibility → 原有调度和核验策略。

| 已有状态 | 原生候选的处理 |
|---|---|
| 完成 / 已送达 | 原样读取，不能再次执行、核验、签收或发送重复回复 |
| 输入已入队、尚未确认显示 / 回复 | 用原 inputId / receipt 继续观察与消费，不生成新输入 |
| 旧 Host 仍持租约 | 客户端读取 / 提交，不抢占；接管只走现有显式移交流程 |
| 待审批 / stale approval | 展示原记录；按既有具体操作、主体、期限、revision 重新核对；不自动继承未知允许 |
| 运行中崩溃、未知工具效果 | 保留 ToolCall 与未知效果；先结算 / 对账，不能按“Rust 首次启动”盲目重跑 |
| 已有有效 checkpoint | 仅当版本、模型 wire、历史 fingerprint、lease、权限及原恢复闸全部兼容才续接 |
| 未知 / 不兼容 checkpoint | 可读诊断；继续由兼容旧引擎恢复，或在明确新执行尝试中沿原系统支持的重试政策处理；不能丢掉后从头自动执行 |
| 中断的 sidecar / 部分提交 / 不完整尾行 | 按原 Store 恢复语义保全已确认记录；隔离坏尾、拒绝无法证明的提交，不制造完成 |
| policy 损坏 / SQLite 未知 schema / 磁盘满 | 结构化拒绝，保留旧库及诊断；不得重建为空库后回退 Full |
| 已取消 / 暂停 / 取代、晚到结果 | 严格校验 execution identity / revision / lease；保留合法事实，不重新激活旧任务或写入新会话 |

所有恢复用故障注入、独立数据副本与真实 Store 验证；恢复后必须再接收一个新任务，证明所有权、队列和取消域没有卡住。不能通过删用户数据制造成功。

## 7. 发布与回退

1. 迁移期保留两份可执行候选，但一次会话只选一个执行引擎。没有运行中热切引擎或自动双写。
2. 切换前完成 TS→Rust→TS 的配置、会话、权限、任务和 Evidence 往返；旧版本无法读取的新事实不得进入默认共享写域。
3. 回退保留数据和审计，只在执行已 drain 或已明确结算未知效果后释放所有权；旧版重新获取并按其支持的 checkpoint 恢复。不兼容任务维持阻断，不清历史后重跑。
4. 新版和旧版的不兼容信息须能被 doctor / 启动检查说明。不能只增加一个旧版完全不识别的 manifest 就声称有兼容保护。
5. CLI 平台归档仍包含 `peer` + `peer-credential-helper`，先保留当前正式构建的 darwin-arm64 / linux-x64。其他平台须独立通过构建、终端、Helper 和安装验收后才能宣告支持。
6. 原生二进制默认切换前需完整 release gate；包括所有开放 PR 合入、最终合并候选全仓测试及产品回归、逐图审查、再次核对 PR 清单、公开产物与安装器验证。不得在本次方案阶段安装、重启或发布。

## 8. 协议 SDK 的兼容注意

MCP 首选官方 Rust SDK `rmcp`，但其当前 upstream 明确不提供 legacy HTTP+SSE，而现有 Peer `mcp-client.mjs` 提供 `SSEClientTransport`。必须实现受控 legacy Adapter 或选定仍支持的安全版本并审查维护成本；不允许静默把已有 `sse` 配置当作 Streamable HTTP。任何移除 / 代理部署方案均需独立产品接受，不能作为迁移的隐性前提。[官方 MCP Rust SDK](https://github.com/modelcontextprotocol/rust-sdk#transports)

ACP 使用官方 Rust SDK 的稳定协议入口，对齐现有 TS SDK 的已实现能力，不因换库默认开启 draft v2、新客户端工具、登录或恢复能力。[官方 ACP Rust SDK](https://github.com/agentclientprotocol/rust-sdk)

## 9. 验收

- 对同一 fixture 运行 TS / Rust 的 projection、Context、digest、错误与 reducer，输出逐字段对比。
- 真实双子进程竞争租约、文件锁、SQLite CAS、输入幂等、late approval、sidecar commit；故障点含写前、写中、rename 后、回执前与退出中。
- 断连 / 超时 / 拒绝 / 取消后无未授权执行；重启后不重放未知效果；恢复阻断必须给出具体对象与可用路径。
- `exec` JSON / 退出码、ACP stdio、公开 SDK smoke 和 Desktop 原合同保持；候选绑定 commit、构建 hash、fixtures / schema hash 与平台。
- 本文当前只有方案与静态审阅，不表示上述验证已运行。

## 修订记录

- 2026-11-14：新增跨语言单一契约、兼容数据与锁、旧状态恢复、原生发布和回退提案；未改权限档位、数据真源或当前已接受 ADR。

## 接受与编号校正（2026-11-14）

同日措辞澄清：§1 将同号 ADR 104 区分为文件名。未接受的是能力可见性提案；已接受的 progressive storage / writer fence 决策未被撤销。此为消除引用歧义，不变更既有存储 / 权限 / 恢复边界。

用户明确接受三份原生 CLI 迁移 ADR 并要求先完成 P0/P1、自测后持续推进，最终无 Bun/Node sidecar。评审稿来自落后的知识 checkout，误用主线已有编号；核对全部 origin 分支后，将原 116 / 117 / 118 按同一内容分别登记为 129 / 130 / 131。既有同号其他 ADR 未被覆盖。接受不等于实现、性能、恢复或发布验收。

### 最新主线约束复核

已补读 ADR 112、既有 116（session-control-and-resource-settlement）、120、122、124 与 127 的相关条款。ADR 127 页头为 Accepted，即使 map 的摘要仍写未接受也以文件原文为准；不能将旧稿的保守阻断描述解读为撤销当前受控对账 / claim 收口策略。恢复、停止回执、unknown 不重放与原执行政策均按这些已接受条款迁移。

### NR-03 原生 attempt 的停稳观测补充（2026-11-14，实施前）

按本 ADR 的跨语言恢复授权，明确一个新增的可选存储合同：既有 canonical `work.budget.attempts[attemptId]` 与其 `pendingTools`/`uncertainDispatches` 行可携带 `nativeRecorder`，形状为 `{schemaVersion:1, runtime:"peer-native", execution:<原 SessionExecutionIdentity>, recorder:<既有完整 bootId/pid/pidStart/hostId/acquiredAt tuple>}`。写入者必须是当前 lease 的实际原生 executor，在首次模型/工具 dispatch 前采集，随同一 canonical budget 事务提交。它不是新任务表、私有执行日志、checkpoint 或可重用 grant。TS 保留未知字段并继续保守恢复，不能把其存在当执行成功。新增合同必须在 packages/protocol contract resources 固化并对照旧 TS 冷读。

此条补充 ADR 124 的原生停稳 Adapter：只有原执行 identity 完全匹配、全部相关 recorder 一致、实际 OS 观测证明旧 executor 已死、且不存在任何未结束 capability handle 时，Host 可据此确认本地原生 runner/scheduler 已停止并生成既有 managed_execution stop receipt。它不证明历史工具的效果；所有 pending dispatch 仍转入 canonical uncertainDispatches，unknown 保留，原工具绝不重放。Shell/MCP/外部任务句柄未能证明结束时继续阻断，不能用 recorder 死亡伪造 ended。缺失/不完整/混杂/新版本 recorder 或 OS 观测失败一律不可用。Session Control operation 自身的 recorder 仍是实际记录该 operation 的新 Host，不冒充旧进程。现有 ADR 124/127 的其它 recorder、claim closure、策略与人工确认要求不变。此为 A 级可选合同补充，不替代运行/平台验收。

### NR-03 已确认文件创建的 claim 身份（2026-11-14，实施前）

允许既有 ledger 中属于同一执行与 hostEpoch、仍为 reserved/active 且无 unknown/closure 的 file claim，从 `identity=missing` 更新为本 Host 的实际 File Provider 刚创建并确认的文件身份。必须先持久化配对的真实 Tool Result、Evidence 与 dispatch receipt，再在 ledger 事务内重新核对 scope、执行、owner、当前文件身份；递增原 claim revision，并在既有 resource_events 记录真实 tool-result 引用。相同已应用身份为幂等；已有非 missing 身份变化、外来 owner、reconciling/closed、unknown 或观测不一致全部拒绝。它不推断助手文字、工具计划、文件存在或历史 approved 为创建成功，也不释放 unknown。此为既有 schema 的受控身份确认补充，不新增执行日志或授权路径；须验证同轮“创建→读取→改写”和 TS 冷读。

### NR-04 用量双文件提交恢复（2026-11-15，实施前）

ADR25 的 scope、Store 所有权和既有格式不变；本条收紧其“不声称 index/JSONL 崩溃原子性”处的恢复保证，仍不声称两个文件瞬时原子可见。已用隔离真实 TS Store 复现：index 累加10后 ledger append EACCES，重试同一 id 后 index20而 ledger一行。按本迁移的恢复授权，A 级补充如下，先登记再实施：

- 同一 ConversationStore sink 负责 Node/Rust。持锁顺序为 index.jsonl.lock → .usage-ledger-transaction.lock → usage/requests.jsonl.lock；无 TTL 清锁。辅助 usage 日志写入也参与最后一把锁并拒绝不完整尾行。
- 既有 `.usage-ledger-transaction` basename 增加可选 schemaVersion=1 的单笔 Store 提交意图文件：ledgerRelative（只与 Host 已配置目的地比较，绝不据内容解析写入位置）、conversationId、before/after（仅 lifetimeUsage/runtimeTurnCount）、完整 ledgerRow、ledgerLine（其唯一末尾换行的原始UTF-8行；解码内容必须与ledgerRow一致）、prefixBytes/prefixSha256。它是用量提交恢复材料，不是第二个执行日志、任务、checkpoint 或权限真源；不得包含秘密。生产目的地仍为既有 usageRequests。意图随 conversations portable 数据保留，未结算提交须在同步/回退前 drain。
- 严格验证、有限内存扫描与同 id 去重 → fsync 意图并同步目录 → 原子更新并 fsync index → append并fsync真实 ledger行 → 删除意图并同步目录。返回前必须完成两边。重复身份且已提供字段冲突（重试省略可选归因仍返回原行，保留ADR25既有幂等）、未知 schema、坏账本/非普通文件、安全整数溢出全部失败关闭，不归零或略过。
- 恢复只比较相关计数器；仍为 before 则应用 after，已为 after 则只补日志，其它值冲突即阻断。保留其它 metadata/未知字段。先核对保存的 ledger 前缀长度与 SHA256；完整额外行可以保留，并在追加前重新持久化当前前缀。只有从已证明前缀开始、逐字节等于原行前缀的部分追加，才允许补剩余字节；不截断未知数据。已存在相同行为幂等，重复/冲突阻断。
- 单行256KiB、意图512KiB、index沿既有8MiB/4096行边界；扫描不将整个 lifetime 日志驻留内存。取消只在提交意图前终止；已开始提交必须完成或留下可诊断意图，不能删失败记录制造成功。错误区分 invalid/limit/conflict/commit_uncertain。
- 崩溃残留目录锁仍按§5离线维护：确认全部写入者退出、保全文件/锁副本，核实并受控移除孤锁后，由支持v1意图的新 Store 先恢复，才准许旧版本写入。旧版不能自行忽略意图恢复。未带意图的历史半提交无法可靠推断；不自动重算、回填或改个人账单，保留原计数和明确诊断限制。
- 原生 Host 用稳定 runtime-turn id，在成功和已知终态错误都持久化已观察的 turnTotal；null usage不制造零量。lastRequest仍独立，ledger禁止用于容量恢复。Store失败不得跳过真实 attempt/工具停稳。硬退出前尚未持久观察的供应商用量不能重建，不重放模型请求；需保留未知，不能宣称已知零费用。原生公开接线与恢复分别验收。

实施验收：实际 TS↔Rust 写读与同 id 冷读；index后追加失败、部分行、意图清理失败、冲突/损坏/新版本、双进程竞争与已知孤锁离线恢复；每次恢复后再写新回合。旧失败保留。未完成这些验证不得宣告 P4 总闸通过。

### NR-04 已观察用量的 canonical 预算快照（2026-11-15，实施前）

A 级补充：终态提交意图只能恢复已经进入 Store 的账目；原生 executor 在工具效果之后硬退出时，旧预算虽保留 tokens 总和，却不足以重建 input/output/cache 的分量。保留旧数据的 unknown 限制；本条只为新观察增加预防，不推断旧记录或重放请求。

允许既有 canonical `work.budget.attempts[attemptId].nativeUsage` 携带 v1 billing-only 快照：`{schemaVersion:1, workId, execution:<完整原execution identity>, conversationId, attribution:<原stable stream/ledger id、模型/渠道、workspace与role>, usage:<tagged RuntimeTurnUsage>, knownAmountsOnly:true}`。仅支持当前已迁移 `work_session` executor；其它角色须先完成其兼容 pass。每次真实模型请求的归一化观察，同预算 tokens/unknown 更新原子进入同一 canonical Work 事务，并先于任何后续工具 dispatch。它不是第二个执行日志、checkpoint、grant 或 Context 来源；不能据此生成 Tool Result、Evidence、完成或许可。只存分量和归因，不存凭证、原始供应商签名、正文或 lastRequest 容量观察；账本仍不得用于 Context restore。

Loop 结束时，原 attempt 的快照和 nativeRecorder 原样移入 `work.budget.nativeUsagePending[attemptId]`，同时沿原规则保留 settled/pending dispatches。原 attempt 保留 `nativeLoopFinished:true` 与完整 nativeRecorder，直到匹配 execution 的真实 managed_execution stop receipt 证明 runner/scheduler idle 且 admission closed，才移除该结束标记；标记本身不证明工具或进程已停稳，未产生可计费用量的 loop 也保留此恢复来源。未知/新版本快照保留并阻断记账，不得阻断真实 stop/drain。只有现有 Store 返回相同身份、分量与归因的真实 ledger receipt 后，当前 journal owner 才能 CAS 移除相同 pending 值；失去 lease、回执丢失或值变化时保留，下一次用原 id 去重核对。工具 unknown 和 budget unknown 不因记账而清除。

新执行先核对 Store 意图和已结束的 pending 快照，再准入模型。恢复正在运行时先取得既有实际停稳/对账证明，才把旧 attempt 的完整快照转入 pending；未停稳的活跃观察不能被另一 Host当完整回合提前封账。已记录 loop结束的 pending 可独立核对费用，不证明历史工具效果。每次恢复最多处理64条；超量保留剩余并要求继续显式 recover，首次执行保持阻断。单快照16KiB，已知计数安全整数，未知/冲突/损坏均失败关闭。

兼容范围：当前旧 TS 的 worker 路径保留未知预算字段；delegation dispatch recovery 只删除 project_agent/spawn_session attempt，不能把该证明扩展到尚未迁移的 coordinator。必须用实际 TS read→saveWork→read 及 Native重读验证两种字段保留。旧引擎不负责结算新增快照，回退/同步仍受§7的 drain 要求；此条不声称已通过默认共享写入或发布验收。新增形状先冻结在 packages/protocol contract resources，复用现有 canonical journal、锁、身份与 Ledger，不建私有文件或第二套任务系统。

验收包括：真实“模型→文件效果→硬退出→停稳→已知用量一次入账”；stop后/意图前硬退出；Store错误及回执丢失；未知快照仍先停稳、事实原样保留；TS往返与后续任务；无模型/工具重放。此前未携带分量快照的旧记录继续 unknown，不自动制造账目。

### NR-04 可恢复的压缩历史选择与容量绑定（2026-11-15，实施前）

A 级补充，修订 ADR57 §3.1/§3.6/不变式5。实际 TS split 在同一用户回合只保留原 user，现有 marker 插在 user 之前，冷读却重新引入其后的已压缩工具历史。daa4c478 的隔离基线 warm1/cold4 已保存。不能用内存历史宣称持久压缩成功，也不能删除原文或复制相同 id。

既有 `_compaction` marker 允许可选 `historySelection:{version:1,compactionEpoch:<安全正整数>,retainedMessageIds:<原始消息id有序列表>}`。marker 追加在 canonical JSONL 末尾，原始消息和 Tool Result/Evidence 原位保留。选择仅引用 marker 之前唯一存在的非 marker user/assistant/tool 行，次序与原文一致；随后接 marker 后的新行。缺失、重复、乱序、未知版本、非法类型、超限或与后续重复身份均失败关闭，原文不动。上限在 packages/protocol resource 冻结。旧 marker 仍按既有 suffix 规则解释。

Canonical projector 升至3，TS/Rust 同时实施、重生成差分 fixtures；新 marker epoch 进入 continuity metadata。选择只决定上下文，不提供许可、执行、Evidence 或完成真值。Renderer/Ratatui 不解释引用。压缩后必须从实际持久源重新投影、装配和计数，不能复用旧 count。

容量继续使用既有 `.context-snapshots/<conversation>.json` 和 index mirror，不从账单恢复。新写入增加 `projectorVersion:3`、`compactionBoundaryId:null|<实际最后marker id>`。同模型、合法 provider-request observation、匹配 boundary/epoch 才能恢复 pending 基线。新选择出现后，缺失/旧 binding 和 superseded observation 不可复活压缩前高水位；未知快照保留，仅投影未知。summary 计费但 capacityBearing=false。

Store 持既有 index→conversation 锁，以原 content/source revision CAS 追加完整 marker，随后更新派生 index。沿用 body已提交/index未完成时的显式 reconcile_index，不声称瞬时双文件原子。marker 已落盘而 snapshot 未更新时，即使旧 index revision 未推进，boundary 不匹配也必须使旧快照失效。当前 TS/Rust getter 同时核对。Native recover 在真实停稳后才修复派生 index、核对账目，不重放模型或工具，不删除旧 snapshot/unknown。

首次原生 worker 会话若无模型 metadata，可由已通过准入的冻结 Goal model selection 写入实际绑定；已有不同绑定时拒绝，不覆盖用户选择。此 metadata 不是授权。System Context 增补注册的 continuity Source 和专用 summary cognition Source Adapter；历史原文只进入 user/factual payload。

兼容限制：v3 selection 要求支持合同的当前 TS/Rust reader。旧发行版不能安全续跑新选择，不宣称任意旧二进制兼容。默认共享写入、安装和回退仍须 §7 联合兼容与 drain 门禁；本条授权源码及隔离夹具，不授权个人数据、安装或默认切换。

验收覆盖真实工具后的自动压缩→落盘→重读→重建→重计数→发送；温/冷一致、原始字节及工具身份保留；summary/失败计费；overflow 单次恢复；marker后硬退出、index部分提交、旧容量不复活和后续任务；实际 TS↔Rust 冷读。未完成不得记 P4 总闸通过。

### NR-04 原生 MCP dispatch 与停稳观测（2026-11-15，实施前）

沿 ADR31/32、116/124/127 迁移 MCP Provider，不改变可见性、许可或 unknown 收口政策。三种 transport 分别实现；原生 SDK 不支持的 legacy SSE 使用有界 Adapter，不改写配置。连接初始化和 tools/call 分开：Host 在启动受管 transport 前验证真实 grant，在初始化完成、实际 tools/call 写出前再次核对同一 grant、registry source、Goal/binding、policy 与 lease；拒绝或取消不能发出 tools/call。MCP description、resources、prompts 均不自行成为 System Context 指令。

允许既有 resource handle 携带可选 `nativeMcp:{schemaVersion:1,role:"rpc"|"connection",transport,registryRevision,ownerRecorder:<完整原生 recorder>,childRecorder?:<实际 stdio 子进程完整 recorder>}`，与原 execution、hostEpoch、toolCallId 一起核对。它只证明受管本地连接/进程的身份和活性，不证明远端效果。未知版本、不完整身份和未登记启动窗口保持阻断；不得按 PID、超时、连接关闭或原生 owner 死亡推断任意外部工具已结束。stdio 的进程组必须实际结束并回收；HTTP 的 owner 死亡只证明本地请求泵已消失。恢复只针对匹配原执行和完整 recorder 的本地受管句柄，不重放请求，不把其 ended 写成工具成功或无效果。

MCP 已发出的请求在超时、断连、取消、超限或回执不确定时保留 canonical pending/uncertain dispatch；对账为 `unfenced_external`，不可凭本机 Git clean 自动收口。只有协议结果或明确的未派发事实可以进入相应已有结算；实际协议错误与业务 `isError` 分开。结果、失败、拒绝与 unknown 均经既有 Conversation/Evidence Store，元数据可携带 server/transport/tool/投影身份但不携带 headers/env/凭证或原始底层错误。

本条不引入新的执行日志或可重用 grant。bounded 连接/消息/通知/输出、真实正常/拒绝/降权/取消/超时/截断、重启 unknown 不重放及后续任务须通过公开 CLI 和 TS 差分验证。启动登记窗口和任何不支持的 credential/schema 明确阻断；未证明的恢复不记 P4 总闸通过。凭证命名空间与旧密文迁移仍按 ADR0001/32，不能在 transport 内暗中解密 Electron 或回退明文。

本卡 v1 界限冻结于 mcp-runtime-v1 resource：最多8个受管连接、通道1条、单帧1MiB、单RPC累计8MiB/128帧、单请求256KiB、归一化结果256KiB、30秒deadline。超限明确失败并保留可能效果，不静默截断或替换原返回类型。明确未写出 tools/call 时可在 Evidence 追加 `dispatchOutcome:"not_dispatched"`，canonical receipt 仅由 Host 采用此受信 Provider 事实；模型/服务端字段不能提供该事实。HTTP 不自动重试或重定向；legacy SSE endpoint 限同源，避免配置凭证跨源发送；这属于本原生 Adapter 的保守限制，不将此卡记为完整协议平价。现有已显式配置 headers/env 的注入值在返回进入模型/Evidence 前脱敏；新凭证管理仍须 Vault Adapter。

2026-11-16 B级协议补齐：Streamable HTTP等待原RPC的SSE结果时，仍须发送SDK产生的服务器请求回复/通知；最多保留原响应流和一个控制POST，不创建脱离受管owner的后台任务。控制回复只能沿已有transport，不生成工具、许可、Evidence或模型调用。客户端与服务器各自的请求id可重合；只有同id的JSON-RPC响应/错误可结束原响应流，服务器同id的请求不算工具结果。协商版本只绑定到真实initialize请求的响应，Tool Result里的同名字段仍是原始事实，不能改变连接配置或下一请求header。明确禁用底层HTTP协议NACK重试，保持不自动重放；断连/失败仍按原unknown契约处理。此补齐沿ADR31既有双向协议，未移动能力、授权、存储或System Context边界。

### NR-04 原生模型账号登录与只读状态（2026-11-16，实施前 A级补齐）

沿 ADR0001/28 和已接受的全面迁移，新增 `models auth <configured-channel-id>`、`models logout <configured-channel-id>`、`models status <configured-channel-id>`。这些是用户显式调用的本地凭据管理命令，不进入模型工具面，不授予能力、PermissionGrant 或 Evidence；不能因 auth 成功自动执行用户任务。既有裸 `models` 列表与完整配置 CRUD/写入所有权继续按 P4 功能表交付，本节不将缺项删出目标。

- 只选择现有 v2 channels 的唯一 id，认证方式来自当前已声明 Adapter，ChatGPT/Google 使用实际 TS 中冻结的 installed-app identity、固定授权/token端点、现有 localhost 回调路径/端口和 S256 PKCE。原生实现使用外部浏览器授权 URL（CLI 明示 URL 及取消方式），不嵌入浏览器、不用 Bun/Node 或旧 CLI 引擎代办。授权 URL 不包含 code verifier、token 或用户 client secret。
- 单次 flow 拥有 listener、state/verifier、HTTP请求与 Helper 子进程。回调只绑定 IPv4 loopback；按实际 redirect 检查唯一 Host、路径、唯一 state/code，拒绝混淆/重复/错误 state。头大小/连接数/每次读写与总等待有界，取消/拒绝/超时关闭所有自有资源。callback 页面只确认已收到回调，不能在 Vault 验证前宣称登录成功；输出/错误不带 code/verifier/token。
- 授权码交换固定端点，禁止重定向和自动重放，整响应有期限/大小界限；按现有 token schema 验证 access、Bearer、正 expiry 与账号元数据。JWT claims 仅用于既有路由/显示元数据，不被提升成新的授权事实。
- 开始时捕获只读 channel 绑定和真实 Helper snapshot/revision（包括明确重新登录要替换的 pending/损坏 token JSON）；交换完成先复核 channel，再只 CAS 原始凭据代。新登录/退出/配置移除或修改使迟到 flow 失败，不无条件覆盖。Helper 缺 CAS feature 在授权 URL 和远端效果前拒绝。Vault 密文/schema 损坏仍保全，不为重登重建 Vault。
- 登录只有在 Vault 条件提交且原值回读验证后返回 credential_updated；回执丢失报告 unknown，status/新登录以实际 Vault 对账，不自动重放授权码。logout 只条件删除当前代，不调用远端撤销、不复活已删账号；缺失幂等。status 仅投影真实凭据为 not_logged_in/authenticated/refresh_required/recovery_required，不输出秘密，pending/未知 token 不能冒充未登录或可自动刷新。
- 明确修正原生 loader 的实现偏差：oauthConfigured/oauthExpires/oauthAccountId 是非权威提示，不能替代实际 Helper token 或阻止已成功落盘的原生登录准入。仍需唯一配置绑定、已启用模型/渠道和原授权链；无 token、pending、错误 provider、未知 schema 仍拒绝。本卡保持 llm-providers.json 原字节，不无锁回写元数据。完整配置写入所有权、提示恢复、账号创建、混合旧安装版本升级/drain 和 P4总闸仍必须另行实现/验收。
- PKCE/state/请求参数从真实 TS 登录流程生成 conformance 资源；隔离 IdP + 真实原生 CLI + 加密 Helper Vault 验证正确/错误/重复回调、端口冲突、拒绝、取消、超时、晚到登录/退出、提交回执丢失，以及登录后实际模型/工具/Evidence 闭环。共享 loopback parser 可抽为 runtime 内部 Module，MCP仍保留原 redirect 限制与错误契约；不得顺带放开 MCP 端点。

正式 IdP、系统 Vault 和多平台安装分别验收；模拟网络不冒充真实平台认证。依据：[RFC8252](https://www.rfc-editor.org/rfc/rfc8252) 与 [RFC7636](https://www.rfc-editor.org/rfc/rfc7636)。

### NR-04 模型配置写入所有权与损坏保全（2026-11-16，实施前 A级补齐）

完整原生模型管理继续迁移既有 v2 `llm-providers.json`（channels/models），不建立另一份配置或把凭据写入JSON。新增跨语言 ModelConfigStore Module：边界是有界读取、源版本、同名目录锁与条件原子替换，负责配置事实，不负责模型、工具或凭据授权。此项收紧 §5 对此 Store 原先未证明的写入所有权；不改变 channel/model 身份、Vault命名空间或本地执行链。

- Rust 与当前 Desktop / runtime-node 配置写入参与同一个 `${file}.lock` mkdir协议，按文件所在目录的真实路径统一名称；锁自身不得是symlink。完整同步 read→mutate→write 在锁内，不仅锁 rename。进程内嵌套沿同一 owner，异步网络/浏览器等待不得持锁。等待有期限，可取消的宿主应检查取消；超时/锁替换失败关闭，未知残留锁不因TTL自动删除，沿 §5 离线维护恢复。
- 读取上限 1MiB，深度32/节点16384；拒绝非普通文件、损坏JSON、显式未知version及不支持shape。不存在才是空配置。已发布的flat数组及version缺失的channels/models兼容形态仍由既有迁移Adapter处理；当前原生写入先仅接受明确v2，旧格式不擅自升级。不能把解析错误当空配置后覆盖原文件。未知 root/channel/model 字段在相关更新中保留。
- 写入以同一快照身份/内容版本进行CAS；原子同目录0600临时文件→fsync→rename→目录fsync。rename前失败保留旧文件；rename后确认失败报告commit_unknown，重新读取实际配置对账，不回放修改或还原旧快照。锁被替换不得删除替代owner。没有未知效果时原配置可在修复后再次接收修改。
- Desktop 的同步CRUD、读取时迁移及metadata回写都由同一事务拥有。异步诊断/价格获取在网络结束后重读锁内最新对象，只更新仍匹配原对象身份/配置的结果，禁止用网络前整份旧数组覆盖其它宿主更新。runtime-node显式OAuth提示写入也必须在共享锁内重读，保留原布局和未知字段。
- 凭据提交与配置原子性不能仅凭此文件锁宣称完成。最终账号创建/删除/修改、原生auth/refresh和TS凭据管理需在各自短提交段取得此锁并重新核对绑定，锁顺序config→Helper/Vault；网络等待释放。失败恢复必须以真实凭据代条件核对，禁止无条件还原消耗过的旧refresh。提示是可重建投影；配置提示失败不使已提交token失效。完整Vault/配置联合故障、混合安装版本drain与CRUD命令仍逐项验收；未接入的写者/旧二进制不被此新规则自动保护。
- 验收必须从实际Desktop和runtime-node入口及原生Store跨进程竞争，覆盖丢更新、超时/取消、损坏/未知版本保全、未知字段、迟到网络、替代锁owner、提交不确定与后续修改。Store地基或源码接线通过均不等于完整原生命令/P4总闸。

### NR-04 配置能力范围校正（2026-11-16，后续命令实现前 A级澄清）

按 ADR129 与用户原始全面迁移目标，终态覆盖原 CLI 的实际可达行为，不借“全面”新增 Desktop-only 产品能力。重新核对 `apps/tui/src/cli-argv.ts`、`cli-models.ts`、`cli-model-lines.ts`、`model-config.ts` 与方案 §6 后确认：原 `models` 只输出可选模型的tab分隔列表，`PEER_MODEL_API_KEY` / `PEER_MODEL_BASE_URL` / `PEER_MODEL_ID` 提供无需Desktop的环境配置；原CLI没有新增/删除渠道与模型的完整CRUD命令。配置Store及Desktop写者共锁仍是跨宿主一致性的必做项，但不等于必须把Desktop设置产品全部搬成新增CLI命令。

本澄清取代上两节及实施账本中把“完整原生配置CRUD/账号创建命令”作为P4必要退出条件的扩大解释；不删除原有入口，不将尚缺的原生功能记为完成。P4配置交付必须包含：

- 原 `models` 的选择过滤、provider/model/display身份、stdout/stderr、退出码与环境优先级；按实际TS入口生成fixture，与真实公开原生CLI对照。
- 三个已发布 `PEER_MODEL_*` 环境配置字段、缺省模型/baseURL及显式选择的原生模型/工具/Evidence执行，不把环境秘密持久化、不需Desktop或Helper代取环境秘密，不靠JS sidecar。环境只是既有本地模型配置来源，不是System Context或工具授权来源。
- 已有文件/旧格式的模型读取、模型/强度选择、Vault引用、原有OAuth刷新/显式重登与metadata写入/恢复；当前 `models auth/logout/status` 已接受的账号入口保留。配置创建不成为普通模型工具，也不扩张能力/权限/Evidence。
- 所有当前Desktop/runtime-node配置写者与原生凭据短提交参与相同Store/锁/条件恢复；混合旧安装版本drain、真实平台和协议验收仍分别满足。未知/损坏配置不因范围校正被覆盖或默认授权。

将来若增加一套用户可见的模型/渠道CRUD命令，应作为新增产品能力单独确定Interface；不作为本次CLI迁移完成的额外前提。先前共享Store、损坏保全与并发修复继续有效，不回退为无锁写入。

### NR-04 OAuth配置提示重建与显式对账（2026-11-16，实施前 A级补齐）

原 `models`/ModelPicker只读metadata判断可选项；它们不应为列出模型而打开Vault秘密。原生登录已经能写真实Vault，旧候选刻意不写metadata，因此可能出现真实已登录而旧oauthConfigured仍false、列表没有该账号的既有状态。本节补齐这条用户可用链，取代模型账号首卡“本卡保持llm-providers.json原字节”的阶段限制；不改变Vault作为凭据权威、status只读或能力授权。

- 新增窄恢复入口 `models reconcile <configured-channel-id>`：仅核对该已配置OAuth渠道的真实Helper记录与配置绑定，在同一config→Helper顺序下重建 `oauthConfigured` / `oauthExpires` / `oauthAccountId`；不创建渠道/模型，不登录、不刷新、不请求模型/工具，不迁移个人任务，也不因修复提示生成授权或Evidence。
- 真实缺失可清理上述提示；有效已知token可投影存在/expiry/account。pending、损坏、未知schema、错误provider、无法读取Vault均保全原始事实并拒绝修复，不把unknown写成未登录。Account/expiry只来自已验证的token字段，提示中不写秘密。相同投影不改文件/revision；保留root/channel/model的其它字段，修复已知同组model残留的三种提示覆盖。
- auth/logout成功确认真实Vault结果后，在仍持config锁时尝试同一提示重建。凭据结果与提示结果分别结构化返回：已知updated/removed不能因metadata失败变成“凭据未更新”，失败也不能恢复旧token；提示失败返回rebuild_required或commit_unknown及明确reconcile动作。Vault提交本身未知仍沿原未知错误，不因metadata看似已更新宣称凭据成功，不重放code/refresh。
- 自动刷新沿同一Module尝试提示重建。非权威提示失败不能让已验证的新token失效；但配置operational binding、凭据代或锁owner无法证明时仍拒绝模型准入。无新增秘密影子库、独立修复日志或后台重试；对账从原配置引用和实际Vault可重跑。
- 为避免自身提示更新使原绑定失效，Native与当前TS凭据绑定比较只忽略上述三种非权威提示；provider/auth/endpoint/header/project/model/启用状态及其它既有操作配置仍按原边界核对。跨语言fixtures验证提示变化不伪造配置许可，真实操作配置变化仍使迟到结果失败。
- status保持只读，models列表保持metadata/环境来源，不为列表解封秘密。正式系统Vault、混合安装版本与默认共享域仍单独验收。新增reconcile的理由是已有原生账号操作的部分提交恢复，不扩展为Desktop整套CRUD。

2026-11-16 环境来源接线前补充（A级身份/Adapter澄清）：原环境catalog使用 `providerId=openai-compatible`、当前PEER_MODEL_ID或gpt-4o-mini，reasoning选择为off/low/default/high。原生模型factory只在显式选择该source且model相符时取环境秘密；普通三字段RuntimeModelSelection可用，canonical Goal既有四字段格式不变，该来源的modelProviderId/family若存在须同为openai-compatible。已有文件渠道绑定不因环境变量存在被重定向或获得环境key。独立Env Provider沿实际createOpenAICompatibleProvider的Chat请求（含off、default和tools语义），不误套品牌Chat启发式；它是现有wire encoder seam的Adapter，不另开工具loop。模型列表只读metadata/环境，不调用Helper；非法终端控制文本与未知配置版本可见拒绝，原文件保全。以上需真实TS请求fixture及公开原生CLI模型→工具→Grant/Evidence验证，不能由列表或factory单测冒充完成。

### NR-04 MCP刷新未知结果持久化（2026-11-16，实施前 A级补齐）

沿ADR132新增可选Vault envelope refreshState意图，先持锁发布并验证，再允许SDK刷新；同owner持锁publish推进binding，失败/中断不恢复旧refresh。当前Rust工具/refresh与Desktop冷读拒绝pending，显式原生重新授权才能清除。原不可变slot与历史保留，旧安装/预读token仍受drain闸。该凭据操作不是tools/call派发或工具Evidence；grant延续与当前TS token发送guard尚须后续实现验收。具体schema、顺序、异常恢复与测试见ADR132同日修订。

### NR-04 原生MCP credential epoch与原grant续行（2026-11-16，实施前 A级补齐）

沿ADR132同日修订引入execution绑定、只在内存存续的凭据epoch：只有受管OAuth持锁发布的内部凭据证明可以推进已知真实Store revision。Host每次检查真实revision，只对这条已验证代际链规范化credential来源以复核原grant；其它授权/Context事实和外部变化继续精确拒绝。连接owner有限排队，旧HTTP连接停稳/join后才刷新与替换，stdio不自动重启；不重放tools/call，不改写grant/Evidence或清除unknown。重启丢失epoch证明，沿原Store/任务恢复准入。细项与验收见ADR132；当前TS预读发送guard、安装drain与P4总闸另验。

### NR-04 当前TS MCP token发送与共享恢复（2026-11-16，实施前 A级补齐）

沿ADR132同日修订，TS官方SDK fetch seam在token HTTP之前取得共享metadata owner并发布已有refreshState，code交换也用同一pending合同；只由该owner验证并发布新Vault代，SDK晚到save仅消费匹配回执。当前读/保存/redirect回调复核代，显式Host authorize purpose可保留已知pending写入新的PKCE并重新授权，未知schema保全。tools/call认证失败/redirect不自动重放且保留unknown；close取消并等待受管HTTP。原生兼容已保存且一致的SDK issuer cache与真实token.scope，仍经受限发现和原权限链。新回调是同进程Host Interface，不是Renderer许可或新跨进程真值；旧已运行版本drain仍另验。


## 2026-11-16 NR-04 Grok 原生订阅接入（A，实施前登记）

沿ADR28/37/50和已接受129的完整Provider范围，将当前CLI实际`oauth_grok`接入原生Responses wire；不启动官方Grok CLI、JS引擎或业务sidecar。复用原ModelBinding、Helper模型OAuth CAS/前置刷新意图、Context/用量/压缩与模型编码接缝。Grok当前channel descriptor只声明订阅OAuth，不借本卡新增API-key渠道或工具授权。当前TS仍为迁移对照与Desktop实现，不把它当原生运行依赖。

### 认证与凭据

固定已有公共client身份、`auth.x.ai` issuer/device/token/userinfo和`cli-chat-proxy.grok.com/v1`模型平面，常量由当前TS生成共享contract resource。显式`models auth <已配置Grok渠道>`使用RFC8628 device flow：一次device request、至少按interval等待后poll；只对authorization_pending/slow_down继续同一device grant，slow_down每次再加5秒，denied/expired/未知错误/redirect/取消即结束。整体至多15分钟且服从服务器更短到期；单HTTP沿原15秒/64KiB模型OAuth预算，不自动刷新device code、不把轮询扩展为模型/工具重放。Secret device_code只在有owner的有界内存中，绝不落盘、入argv或回显；给用户的verification URL/userCode/有效期是独立的管理提示，不代表登录或任务成功。Ctrl-C取消当前登录，保留原凭据/配置/任务；新显式登录从新device授权开始。

Protocol登记可序列化的模型认证提示：保留旧browser的authorizationUrl输出，新device方式仅增加明确的userCode/有效期可选字段；CLI展示端消费结构化提示。原browser账户不改变callback/state/PKCE。仅呈现受限HTTPS官方验证地址；test-only loopback替换继续受编译feature与自有fixture marker限制，featureless产物不开放端点覆盖或读第三方Grok auth文件。不会自动打开浏览器或把URL内容作为系统指令。TUI完整交互仍在P6接同一管理入口，headless模型执行本身不暗中创建登录流程。

`model/<channel>/oauth-tokens`沿既有加密payload保存access/refresh/expires/scope/issuer/clientId与可选账号信息，未知字段保留；明确provider若存在须匹配Grok，提供的issuer/clientId必须匹配固定绑定。实际scope必须包含api:access，缺失不向模型平面发请求。刷新省略scope/refresh延续实际原值；返回scope集合变化或丢失api:access保留刷新pending并要求显式重登。新device授权的scope省略只按OAuth省略语义延续本次完整请求范围，不据metadata scopes_supported扩大scope。公共userinfo仅用于非权威账号展示，失败不伪造账号或撤销已证明的token；userinfo不进入System Context/许可。登录前后核对原配置身份与Vault代，晚到登录不得覆盖新登录/退出/删除；最终提交和提示投影恢复继续沿原Account seam，不另建凭据存储。

### Grok兼容传输

新增私有深Module持有每个原生模型实例的有界兼容状态，不按host散落分支。元数据只从已有`https://x.ai/cli/stable`读取，无Authorization/账号/自定义origin头；4秒、至多64字节、无redirect，只接受完整major1 semver。沿原6小时cache/24小时有限stale策略，不持久化版本、不从服务器报错或环境变量猜版本；未来major在推理前拒绝。取消覆盖本次metadata/HTTP，无detached task。元数据准备结束后、每次真正模型POST前，再走真实OAuth/config绑定检查；不能因为cache预读沿用过时token。

模型请求复用同一prepared原始字节与fingerprint，按既有Grok固定身份头加实际发现的client-version。只对原协议明确的推理前426拒绝，强制重读官方feed；仅版本确实改变且仍受支持时，允许同一逻辑请求再发一次。相同版本/第二个426/其它错误不重试，不更换模型或从error text取版本；取消/Context绑定变化阻断下一次物理请求。这个Grok专用426行为不开放给其它Provider、MCP或本地工具。预算/用量仍按既有逻辑请求，实际返回的观察与unknown不能用兼容重试制造成功。

账号头归Provider描述而非Responses wire：ChatGPT的chatgpt-account-id不能泄到Grok，仅发送该Provider实际声明的账号头；协议/品牌/凭据仍正交。普通OpenAI/Google/Anthropic请求保持原Module路径。

### 验证与边界

先冻结实际TS refresh、channel/request/header和版本状态fixture；用公开原生models auth/status/logout/reconcile、真实加密Helper和本机合成IdP/模型走工具→Grant→Evidence闭环。覆盖pending/slow_down/拒绝/到期/取消、无api scope、issuer/client/provider冲突、token轮换、迟到配置/凭据、bad/超限/未来版本、metadata无密钥、426最多一次且body/fingerprint不变、之后的新任务和原unknown保全。网络/TLS/代理继续同一Native Network；featureless候选通过隔离TLS/proxy入口核对，不触个人凭据或系统信任。实际公开IdP/模型、OS Vault和安装drain仍另验；本修订不是Grok或P4已完成声明。

核对于2026-11-16的主来源：[xAI OIDC metadata](https://auth.x.ai/.well-known/openid-configuration)、[官方CLI认证说明](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/02-authentication.md)、[RFC8628](https://www.rfc-editor.org/rfc/rfc8628.html)、[CLI稳定版本feed](https://x.ai/cli/stable)。feed当前返回1.0.77只是核对事实，不写成原生固定版本。当前TS真实实现决定迁移兼容行为；公开文档不取代本地Grant/Evidence与恢复事实。

## 2026-11-17 NR-04 会话只读壳与有界导出（A，实施前登记）

沿已接受`108-cli-basic-shell-commands.md`迁移doctor、sessions list与export。它们是人明确调用的管理/阅读入口，不向模型投影新工具，不创建PermissionGrant、Evidence、会话接收或任务完成事实。sessions resume的完整交互仍须P6；不能以列表或导出冒充可继续普通对话。删除仍沿ADR34的独立跨Store级联，不能顺便实现为直接删文件。

doctor检查当前原生可执行文件及同目录Helper的存在/可执行性、数据根可写或其最近存在目录可创建下级、版本、TTY/颜色；不执行Helper、不解封Vault、不联网、不修复配置。不为检查而创建数据根/会话，缺HOME/非法根/不可执行Helper均如实失败。这里收紧旧TS检查时mkdir的副作用以遵守ADR108“只检查”；可写检查不承诺磁盘配额、未来权限或实际供应商可用。

列表由同一ConversationStore读index，继承原三种角色投影、时间降序和标题/更新时间输出；不触正文、stream、用量或任何后台迁移。索引沿原8MiB/4096行、节点/字符串预算，重复/损坏/非法身份或持续变化明确报错、原数据保全，不截取前N行冒充完整列表。时间按Store正常ISO字符串处理；非法类型/控制字符不作为可打印事实放行。完整源版本在输出前复核。

导出是展示快照，沿当前TS可见user/assistant content结构与Markdown格式，包括正确v1流式patch；不借用canonical persisted history的provisional-tail排除规则，也不把导出送入模型Context。Store复用现有有界JSON projection Reader，按行扫描/回读；先只投影id/role、跳过未选正文，再为可见行选择content。保留全源UTF-8/JSON结构/深度校验，100MiB工具行不分配其正文AST。扫描缓冲16KiB，每记录源上限1GiB；可见所选值原始编码/字符串各至多12MiB、65536节点/深度64、单key4096bytes，保证10MiB普通正文可处理且不加载整份1GiB历史。超出所选解析能力返回明确限制，不截断/修改源记录。索引/单次投影/临时格式化错峰，沿ADR130的32MiB其它缓冲预算；不是完整P6内存验收。

sidecar先投影身份与patch形状，只在首个匹配消息上读取其role/content，存在content覆盖时不再读原大正文。必须v1、conversationId/messageId匹配及object patch；未知/损坏/缺目标明确拒绝，区别于旧getConversation静默忽略坏sidecar的遗留行为。原JSONL、索引、sidecar的文件身份在开始/完成复核；同长度替换、内容改写、追加和stream代变化使本次导出失效。只返回派生sourceRevision/展示范围，不能据此证明停稳或授权。

CLI先将脱敏Markdown写入自己拥有的0600临时文件，源检查成功后才向stdout或目标发布。复用原sk-/Bearer/ya29模式，不读取Vault来搜索秘密，也不导出工具参数/原始Tool Result/Evidence字段；此模式过滤不承诺识别任意无前缀秘密。标题等可见metadata同样过滤。stdout只接受无终端控制/bidi控制的正文；出现不安全文本时明确拒绝，保留源，显式文件导出仍可取得脱敏阅读副本，不静默删除正文字符。用法诊断/输出路径须安全编码。

目标默认禁止覆盖；--force捕获原目标身份，完整spool后再次校验并原子替换，发布前失败/取消保留原目标，正常清理自有临时文件。拒绝会话Store内目标、所读源文件的symlink/hardlink别名及非普通文件，不允许--force写回会话。目录/文件版本变化拒绝而不制造成功；原生export发布阶段对输出父目录短暂取OS advisory lock（至多等5秒、可取消、进程退出自动释放），锁内复核目标CAS并rename，避免两个原生--force覆盖同一旧代。此锁无持久锁文件，仅用于显式阅读副本输出，绝不替代canonical Store既有mkdir锁/顺序；不合作的外部写者仍受协作式文件身份复核的局限，不称OS路径沙箱。磁盘满、broken pipe、SIGINT/TERM及发布异常分别如实结算；未确认的发布不能输出成功回执；rename已发生后的目录flush/回执失败保留现状并报发布结果未知，不反向删除/覆盖目标制造回滚。后续显式重试从当前目标重新捕获CAS；stdout写出失败可能已有前缀，非0退出不代表完整副本。不改变任何运行任务或unknown记录。没有新增持久化真源或自动清理用户文件。

验证先冻实际TS格式/脱敏/参数与正常Store/stream可见结果；损坏/未来sidecar的明确差异单列。公开原生CLI覆盖无HOME/TTY/JS、空/多角色目录、Helper/数据根失败、可见正文与秘密/控制、覆盖拒绝/原子--force、源/目标竞争、取消/损坏后原字节与后续导出。使用隔离合成Store验证1GiB历史、10MiB正文与100MiB被跳过工具行及资源曲线；正式二进制与普通P4总闸/安装/全产品/长时P6验收分开记录。实现与验收另记。


## 2026-11-17 NR-04 Qoder 本地凭据与目录格式原生化（A，实施前登记）

沿ADR129的Qoder完整迁移范围及本ADR的Provider encoder/credential seam，先替换现有`qoder-local-auth.mjs`依赖官方程序内嵌WASM的本地解封和model-cache算法。最终CLI使用RustCrypto执行相同密码原语，不启动qodercli/Bun/Node，不嵌入WASM VM或捆绑官方SDK二进制；官方模块只在隔离开发夹具中作为互操作oracle。这里不声称Qoder原生请求/认证/队列/工具闭环已经完成，也不能以本Module替代整条Provider验收。

核对对象固定为当前TS实际引用的兼容版本1.0.39；由官方文档指向的`@qoder-ai/qodercli@1.0.39`公开npm包提取认证模块，仅作有来源/hash/包integrity记录的合成对照，不安装/运行官方CLI或读取个人登录数据。`credential_storage_decrypt`格式是标准base64、AES-128-CBC、PKCS#7，16字节UTF-8 key同时作为IV；保持已有格式，不把其称为具备认证的新加密方案。`model_cache_decrypt`新格式为base64(`QMC\x01` + 12字节nonce + AES-256-GCM ciphertext/tag)，HKDF-SHA256以实际uid字节为IKM，salt=`qoder-model-cache-enc`、info=`model-cache-v1`、32字节输出。旧目录格式与未知/损坏数据必须通过真实官方样本和当前TS调用点再确定，不能猜成功或悄悄清空目录。未确认格式明确阻断且保留原文件；v1 helper不接管第三方账户事实。

原生密码Module对编码、密钥、密文/明文长度、GCM tag、CBC块/填充及UTF-8作严格校验，限制单份本地凭据1MiB、目录4MiB及调用方更小预算。边界先检查、运算后再检查；不把异常异常文本、明文、key或ciphertext写入错误/日志。解封缓冲归唯一owner并在释放时零化，算法使用维护中的RustCrypto crate，不自写AES/GCM/HKDF或引入JavaScript执行路径。CBC既有格式不能证明内容真实性，后续Qoder身份、expiry、字段类型与配置绑定仍由Credential Adapter验证；解密成功不生成工具许可或账户在线事实。

后续文件Adapter沿现有`QODER_CONFIG_DIR` / `QODER_CLI_HOME` / HOME解析来源，第三方`.auth/user`、machine_id和目录只读，禁止通过host Node绕过EACCES/EPERM，不写入第三方凭据/刷新或创建新真源。路径、非普通文件、读取大小、取消及读前/后文件身份须有界核对；变化拒绝当前请求并支持修正后的显式重试。Qoder外部登录仍由其账户所有者管理，不借本卡新增Peer登录/自动安装或重启第三方程序。原生模型装配必须绑定明确选中的Qoder渠道及真实凭据来源，每次真正发送前复核，不能把本地文件存在当Grant、Evidence或远端登录成功。

验收先以官方模块和当前TS生成合成Unicode/空值/边界/坏key及旧/新cache样本，再跑Rust双向/固定样本、GCM篡改/CBC填充/UTF8/预算否决及源字节保全。原生完整模型→工具→Grant/Evidence、实际第三方登录/目录和安装多平台仍独立验收；本补充不开放任何工具或System Context来源，不改变canonical恢复和unknown规则。

来源：`https://docs.qoder.com/cli/authentication`、`https://docs.qoder.com/cli/installation`（2026-11-17核对；官方安装文档仍列出npm包）；实际TS `packages/runtime-node/src/provider-adapters/qoder-local-auth.mjs` 与 `qoder-model-catalog.mjs` 是迁移行为的对照，公开新版文档不覆盖本仓已存在的本地格式/权限契约。

2026-11-17 同卡补充：官方Module合成对照确认目录兼容非base64文本原样返回，以及标准base64无`QMC\x01` magic时按UTF-8返回解码文本。二者均须由调用方按原catalog schema校验，不产生已认证事实；空输入、无效UTF-8和损坏GCM tag失败保全。请求body按固定64字符表作base64位分组，使用`$` padding，再交换首/尾floor(n/3)区段。这只是传输混淆，仍须HTTPS、真实凭据与配置绑定。原生实现沿字节预算拒绝超限、坏字符、残片或非canonical padding；charset和合成向量由官方Module提供，消息形态由实际TS builder对照。完整Provider装配、网络、取消与工具闭环另验。

### 2026-11-17 Qoder 原生账户与模型 Host 接线（A，实施前补充）

沿同一Model factory/encoder/Native Network接入`qoder-private`与显式`qoder_local_auth`（现有`local_cli`别名同义）。账户来源是Qoder所有的本地登录文件；不启动第三方CLI、不自行刷新/写回第三方账户，不借API-key或旧JS sidecar填充缺口。沿已有QODER_CONFIG_DIR→QODER_CLI_HOME/.qoder→HOME/.qoder解析；环境token的既有优先级只属于显式Qoder来源，不能流入其它Provider。准备后的账户绑定当前选定channel/model的operational配置和真实来源文件身份，每次物理HTTP发送前重查取消、expiry、配置及凭据身份；晚到换号/退出/禁用使旧实例拒绝，不缓存grant或以目录存在充作在线账户。

文件读取对最终文件NOFOLLOW/NONBLOCK，只接受普通文件；路径别名可通过显式根目录解析，不使用host Node绕过权限。机器标识至多4KiB，user密文至多1MiB，索引/目录沿前述4MiB及有界JSON节点/深度限制。读前lstat→open/fstat→有界分块读取→fd/path再核对dev/inode/size/mtime/ctime；连续追加不扩大已捕获读取窗口，取消/坏UTF8/不可读/未来格式明确失败并保留源。已有加密文件仍以trim后的machine_id前16个JS字符取16字节CBC key；不合字节预算/不完整Unicode边界拒绝。实际token、uid、expiry与字段类型由Credential Adapter校验；账户JSON及应用持有的字符串副本在owner结束时零化。可选metadata不产生授权或Evidence。

保留官方兼容版本1.0.39的认证封装：已有encrypt_user_info/key均在时复用；缺少任一时，以OS随机UUID去连字符后的前16个ASCII字符为新key，对现有uid及实际存在的organization_id/organization_tags/data_policy_agreed按原TS顺序序列化，用AES-128-CBC/PKCS7（IV=key）加密，并以官方固定RSA1024公钥及PKCS#1 v1.5加密该key。使用维护中的RustCrypto公钥加密API，生产不允许外部seed/私钥或任意公钥覆盖，不自写密码算法。它只是已有第三方线协议兼容，不改变Peer Vault格式或工具许可。

COSY envelope使用每次认证准备独立生成的OS随机UUID作为requestId（官方模块不复用正文request_id；二者不代表工具执行身份）、encrypt_user_info、固定cosyVersion和空ideVersion。base64 envelope、Cosy-Key、当次epoch秒、**实际编码后的body**、固定API路径按换行连接计算现有MD5兼容摘要；URL的/algo前缀与查询不进入该API路径。签名/弱旧密码格式不作为Peer授权或安全设计范本。固定字段和合成随机源样本必须与未修改官方模块逐字段对照；源码测试才可注入合成随机源，featureless产物不读取fixture开关。

认证header只由账户Adapter产生并标记sensitive；自定义header不能覆盖Cosy身份、机器、日期、key或Authorization。当前2MiB prepared-request总上限保留，body先由Qoder专用encoder从同一canonical history和Projection生成，再编码成冻结原字节/指纹。它不拼接新System Context，不改变源历史或ToolResult/Evidence。工具配对、相邻assistant合并、双content/contents、工具schema、effort/context档位沿实际TS规则对照。Qoder使用observed-only计数；用量/未知收费仍归原Runtime账本，编码大小不当token容量。

普通发送走同一Native Network代理/TLS/证书/redirect和取消边界；Stream decoder复用经过Qoder业务错误/帧形态适配的现有Chat归一化，只有真实完整终态才公开工具intent。网络错误、队列/重试、部分usage和已发请求不因认证换代被清成未发送，不重放本地工具。完整目录、队列/连接重试及真实服务另按既有TS预算逐项验证；首条正常模型/工具闭环不能替代整个Qoder/P4总闸。

以真实CLI、隔离第三方文件、合成TLS/HTTP模型、当前TS与官方模块验证正常/缺字段生成、坏/过期/换代凭据、坏/超限/FIFO/取消文件、禁用/改选配置、代理/TLS、错误/截断/取消流、真实工具Grant/Evidence、后续任务及原unknown保全。来源、写域、授权与Evidence边界继续沿原主链，P5–P7不因本卡自动完成。


### 2026-11-17 Qoder 旧私有端点与环境凭据（A，实施前补充）

按现有TS分支选择Qoder方言：当前目录命中所选模型，或配置有非空modelOptions时，使用已登记的准备端点；其它模型使用旧/model/v1/chat/completions的JSON/Bearer方言。此选择只由同一ModelBinding、只读目录和已有配置派生，不增加用户可写的方言开关，也不在HTTP/认证/目录解析失败后降级为另一方言。坏/未来/身份冲突的目录继续明确失败，不能伪装成“目录没有该模型”。配置的空modelOptions数组仍是显式覆盖；null按未声明处理。

Qoder三个环境token保持QODER_ACCESS_TOKEN→QODER_PERSONAL_ACCESS_TOKEN→QODER_PAT的trim后非空优先级。环境来源获胜时不读取.auth/user或machine_id，也不借另一磁盘账户补资料：目录选择准备端点则报qoder_local_user_info_required；旧方言则仅在该Qoder模型/配置绑定下使用该环境token。无环境token时，继续只读解封既有本地文件，验证token/expiry；旧Bearer方言不要求准备端点独有uid或加密封装字段，但已有字段仍按原有类型/大小限制验证。准备端点继续要求有效uid，并沿上一条生成/复用封装。两种来源和方言均不得自行登录/刷新/写回第三方数据。

旧端点优先使用已有显式baseUrl。未配置时，沿QODER_MODEL_SERVER_HOST或QODER_ENV/ENVIRONMENT的prod/daily/test既有默认主机选择，严格通过同一URL、Native Network、代理/TLS、redirect和取消政策；环境主机不能覆盖显式配置。正文保留原messages/tools/max_tokens及metadata.context请求/会话标识，直接发送冻结JSON字节而不是准备端点的混淆载体。Authorization、X-Request-ID、X-Session-ID只由Adapter产生并保护，外层/内层业务失败规则相同，只有完整终态才公开工具intent。

来源读取的存在与缺失观察集中为同一有界read set；credentials/catalog/endpoint均沿前述普通文件与有限快照规则。每次物理发送前重查该集合、当前环境、expiry和ModelBinding；目录出现/变化导致方言选择失效时，旧实例拒绝而不换token或自动重放。后续新实例可按实际修复后的来源重建，既有unknown、费用、工具效果、权限和Evidence不清除。此集中不新增持久化源、授权事实或恢复捷径。

以当前TS请求/headers/方言选择对照及真实公开CLI验证两个方言的账户来源、优先级、正常工具链、拒绝、损坏、过期、换代、目录出现/配置变更、取消和后续任务。环境令牌不能进入其它Provider或日志。队列/连接重试及全部目录/流变体、真实服务和P4总闸仍须另验，不由本条接受或首环测试代替。

### 2026-11-17 Qoder 逐尝试重试、身份与计费（A，实施前补充）

原生Qoder沿当前TS的有界策略：10605队列至多40次等待、累计等待600000ms、单次50–60000ms，retryAfterSeconds优先于waitTime秒/estimatedWaitMs估计；估计至多作15000ms基础，再加min(attempt,3)*2000ms。剩余预算不足50ms时直接结束，不因下限突破总预算。103重复只重试一次、2000ms；其它已分类限流/瞬态失败按1000/2000/4000ms；收到响应前的连接失败按1000/3000ms，耗尽后进入同一外层瞬态预算，每次外层重试重置连接轮次。累计等待不是端到端耗时；每次HTTP仍受原有deadline与Host预算约束。取消、鉴权/配置/来源变化、上下文溢出、超限、非法流、缺终态和读空闲超时不自动重试；上下文溢出继续归既有压缩路径。两种Qoder方言共享该策略，其它Provider不借本条新增重试。

重试以同一冻结的非身份正文为种子，只重建request/session/task标识、准备端点is_retry与实际编码字节/指纹；首次真实runtime task_id也用peer-agent:UUID，纯builder固定向量保留原默认值。每次认证仍从实际body重新生成并复核同一只读账户、环境、ModelBinding和Native Network。拒绝后不能换号、换方言或重放本地工具。分类只保留有界枚举/数值，不保留上游错误正文、秘密或部分工具intent。

重试协调归现有Host请求生命周期，不能藏进网络层后只记最终一次。沿ADR25：每个已准入发送尝试都增加canonical modelRequests和providerRequestCount；失败的已知usage先进入同一budget/nativeUsageSnapshot，未知usage继续标unknown。费用/容量观察在策略等待前结算，晚到收费先保存事实再处理租约丢失。后续每次尝试前及等待后重新核对执行权、取消、Goal/MCP身份、预算与历史sourceRevision；maxTokens/maxCost的未知阻断不得绕过。等待由同一owned cancellation/heartbeat包裹；无独立后台请求、无持久重试队列，进程重启不自动续发旧模型请求。摘要请求沿同一逐次计费但capacityBearing=false；容量不能被摘要或累计费用替代。

验收须包括实际TS分类/等待向量、真实公开CLI两方言队列/重复/HTTP限流/连接恢复与耗尽、逐次新身份/指纹和非身份正文不变、失败usage累积、预算阻断、等待取消与凭据/历史变化拒绝、已有工具不重放、硬退出后known/unknown保全和后续任务。只用隔离合成服务/账户；真实服务、P4完整总闸和P5–P7仍另验。
