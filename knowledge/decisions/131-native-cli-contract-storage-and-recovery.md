# ADR 131：原生 CLI 的跨语言契约、共享数据与恢复

创建时间：2026-11-14
最后更新：2026-11-16
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
