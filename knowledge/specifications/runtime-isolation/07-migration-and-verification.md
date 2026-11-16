# 07 迁移清单与验证合同

创建时间：2026-11-11
最后更新：2026-11-16（与 ADR 129 / ADR 133 收口：限定 TS 侧只落地 RI-00 / RI-01 止损，RI-03 直接收敛至 Desktop 接入独立 Rust Core 进程而不重造完整 TS 版 M00–M14；明确核心禁依赖冻结中的遗留 TS runtime-sdk）
状态：详细设计候选；验证用例未运行，不把设计断言称为运行通过。

## 1. 唯一迁移顺序

RI-00基线 → RI-01只读职责/选择性索引 → RI-02 Desktop Query与ClientState桥接（过渡期）→ RI-03 Desktop接入唯一Rust Core独立进程 + 受限Platform Broker（`ADR 133`，不再在TS侧重造全套`M00–M14`运行核心）→ RI-04已有状态/旧writer恢复 → RI-05最终组合产品/平台验收。每步进入实现前，本详细设计和ADR128/133边界先对齐；当前用户已明确先完成设计审查，不授权跳过此顺序直接重构。

RI-02命令仍由原owner处理，Query只能读，不能启动新Runtime writer。RI-03先以测试数据完成真实bridge，再对项目进行05的drain/fence/cutover。不存在某项目同一时刻旧main与新Runtime双执行。查询shadow比较只在相同source版本/隔离副本中进行，不允许shadow命令/工具。

## 2. 生产入口的固定落点

| 入口 | 新handler / Module | 迁完必须删除的旧行为 |
|---|---|---|
| Bot输入/quick-chat/桌面remote | input.submit → M01/M02（原CLI/TUI经ADR 129走原生Rust入口） | UI直接append对话，断线换operationId重发 |
| BotList/get/角标 | bot.list/bot.badge → M12 | directory.list同步调用完整Supervisor；view全量独立轮询 |
| 授权/义务列表 | grants.pending → M12 | 空列表加载全部session/report/Evidence |
| task列表/TaskOverview | tasks.list → M12 | read补写qualityReview/runner终态，read递归验收 |
| 会话/过程/引用/搜索 | 03命名窗口 → Session ReadRepository/M12 | 产品full=true、整份history跨进程传输 |
| 任务详情/核验详情 | session.report +独立ReportSource | 报告→验收→报告递归，UI自行判accepted |
| pause/cancel/takeover/resume | session.control/work.control → M04/M02 | UI状态控制资源释放、跨epoch迟到释放 |
| 模型/工具/Provider loop | M06/M07/M08/M09 | 依赖窗口生命期、平台缺功能时执行旁路 |
| Grant/Policy/Approval | approval.decide/policy.update → M10 | Renderer保存最终授权、Full覆盖Role/deny |
| 核验/acceptance/post_reply | M11/原交付owner | 文本/动画替代结果，未commit先done/release |
| Memory/Objective/配置/资源 | 原typed change +03 View | 任意patch/secret/fullState查询、读配置提交默认值 |
| 诊断/升级/退出 | M14受限用例 | 诊断修个人数据、Query失败重启全部Runtime |

原catalog的411项逐条冻结在[路由清单](ipc-route-inventory.json)，包含原transport/owner/roles与目标Module/contract。迁移依此清单，不在实现阶段再决定哪个方法属于谁。删除条件为静态无旧import/调用、真实trace无旧路径、结果/异常/恢复等价同时成立；源catalog改变必须重新设计该新增项。

## 3. 验证矩阵

| ID | 验证层/用例 | 必须观察 |
|---|---|---|
| D01 | schema/方法/角色/大小/跨scope/伪caller | 拒绝且无接收/副作用；合法caller正常通过 |
| D02 | 命令journal前后断线/不同digest/重复 | 同key仅一个领域操作；不知结果先lookup；无伪成功 |
| D03 | accepted后、派发前、Provider前后、commit后注入故障 | 原receipt可重建；未知不重放；后续任务按原保护准入 |
| D04 | 32/256控制、普通/查询队列满、磁盘配额与disk full | 控制独立；满返回准确接收事实；不丢输入/claim/sidecar |
| D05 | 空grant/Badge/20项任务与十倍无关历史 | 零无关hydrate、按键Evidence、无全索引归一化放大 |
| D06 | 索引冷建/追加/替换/同长度改写/损坏/半行/版本竞争 | 该source明确availability，其他项目可用，无main回退 |
| D07 | cursor过期、订阅gap、Activity溢出/迟到/重连 | source/epoch不混，原窗口/锚点可恢复，不伪造done |
| D08 | report/acceptance回调递归反例 | 独立报告源，读取调用图无环，read零业务写 |
| D09 | 用户降权/撤回/换父/旧nonce/伪ticket/旧Broker | 无新执行，原结果保留，Grant与OS事实分别处理 |
| D10 | Query/worker/Runtime/main/Broker各自退出与SIGSTOP等失联 | 精确recorder/lease/claim；无假ended/无旧代次推进 |
| D11 | 多Store/多宿主竞争、同plan写入/删除/append | 原锁序/CAS、无覆盖输入/复活删除、无双writer |
| D12 | 巨JSON/UTF-8跨块/超大checkpoint/heap或RSS超限 | 流式有效解析/具体阻塞，未知结果不丢；UI可读 |
| D13 | 已有stopping/unknown/partial/legacy缺receipt/缺核验；pendingTask claim后断线/已发送未知/跨workspace/坏文件 | 支持的对账/恢复出口；仅InputReceipt匹配后清交接；无自动passed/清history/未知重发；后续准入 |
| D14 | 跨平台真实启动/静态worker/asar/SQLite/凭据/pipe | 每个目标平台实际bridge通过；不降级main执行 |
| D15 | ≥10分钟真实交互和混合负载 | 原输入/滚动/rAF门槛；15/30秒周期；全部>50ms段命名，>500ms失败 |
| D16 | draft/IME/焦点/阅读位置/隐藏视图/reduced-motion | 输入不丢、不偷焦点、不恢复自动贴底；状态反馈真实 |
| D17 | Provider/模型/Host/Store Adapter替换 | 领域控制/授权算法不改，不复制Provider消息格式 |
| D18 | 最终合并候选的发布门禁 | 全开放PR合并、全测试/构建/类型/架构/IPC、完整产品图审和版本恢复 |

计数/故障断言必须通过真实Module/Store/host seam，不能只mocktransport。架构checker增加Query→Supervisor/GoalRunner/Permission实现禁依赖、core→Electron/UI/遗留TS `@peer-agent/runtime-sdk` 禁依赖（TS `@peer-agent/runtime-sdk` 按 `ADR 133` 进入过渡冻结，严禁在其上扩建或另造第三套 TS 运行时内核）和main业务Store调用禁止；动态trace补运行时回调循环与串行长任务。不能通过放宽断言或减少原负载通过。

## 4. 数据与验收报告

合成负载至少1,100计划、185MB协调历史、46MB会话、69,045项Evidence，并做十倍无关历史/200Bot冷建；原私有历史隔离副本只做本地读取，不能作为模型新上下文上传。真实模型任务另用可分享合成项目，保持原工具/Grant/Verifier/acceptance链。

每个候选报告source/dirty、schema/feature、runtime/OS/DPR/窗口、队列参数、数据规模、cache冷热、全部失败、来源版本和所有>50ms段；记录QG/QC/QA/QW/QT/QX/QQ/QP/QS/QR/QB/QE/QD/QU等待、字节、内存与在途数。Provider网络耗时、Inspector启停、日志/采样成本单列。source改变就重新绑定结果，不沿用旧PR绿灯。

既有阈值：输入p95<100ms、p99<200ms、max<500ms；滚动p95<100ms；rAF p95<32ms；任何>500ms主循环/输入峰值失败。不能以P95遮盖max。机器或OS异常也保留全部样本并给事实归因，不事后删样本。文档自审、确定性验证、真实模型、旧状态恢复、签名包、平台和安装验收分别标明。

## 5. 开始重构的设计门

只有总体目标、15个M模块与11个已有Feature owner合同、协议目录、21种View、14条队列、411项旧catalog路由、存储/平台/生命周期、迁移与D01–D18能相互对应且无未决设计分叉，才标记“设计自审闭合”。这不自动接受ADR，不等于实现就绪证据通过，更不自动授权安装/重启/发布。

本轮只完成设计与内容/差异/一致性审查。产品源码、日用应用、个人任务与已有授权均未改动。重构须在该设计审查之后另按阶段实施，发现新的事实冲突先修设计，不能在实现中临时选择另一个接口/队列/恢复方案。
