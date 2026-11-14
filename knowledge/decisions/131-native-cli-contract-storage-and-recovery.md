# ADR 131：原生 CLI 的跨语言契约、共享数据与恢复

创建时间：2026-11-14
最后更新：2026-11-14
状态：Accepted（2026-11-14 用户接受评审稿 118；正式编号 131；授权实施，不授权个人数据迁移、接管、安装或重启）
级别：A
依赖：[ADR 129](129-native-rust-cli-and-ratatui.md)、[ADR 130](130-bounded-cli-memory-and-transcript.md)

## 1. 问题

CLI 改用 Rust 后，Desktop 与公开 Runtime SDK 暂时仍使用 TS / JS。机械翻译类型不能保持权限 digest、System Context checksum、工具配对、sidecar、宿主租约、SQLite CAS 或完成门一致。新的二进制也不能因为启动成功就接管旧任务。

本 ADR 将 ADR 55 / 57 的共享 Implementation 约束扩展为跨语言 conformance；保留 ADR 0001、35、37、49、65、74、76、80–85、88、92、98、100、101 的事实、权限、存储和恢复边界。ADR 104 / 115 在本 checkout 为 Proposed，不随技术迁移被接受。

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

用户明确接受三份原生 CLI 迁移 ADR 并要求先完成 P0/P1、自测后持续推进，最终无 Bun/Node sidecar。评审稿来自落后的知识 checkout，误用主线已有编号；核对全部 origin 分支后，将原 116 / 117 / 118 按同一内容分别登记为 129 / 130 / 131。既有同号其他 ADR 未被覆盖。接受不等于实现、性能、恢复或发布验收。

### 最新主线约束复核

已补读 ADR 112、既有 116（session-control-and-resource-settlement）、120、122、124 与 127 的相关条款。ADR 127 页头为 Accepted，即使 map 的摘要仍写未接受也以文件原文为准；不能将旧稿的保守阻断描述解读为撤销当前受控对账 / claim 收口策略。恢复、停止回执、unknown 不重放与原执行政策均按这些已接受条款迁移。
