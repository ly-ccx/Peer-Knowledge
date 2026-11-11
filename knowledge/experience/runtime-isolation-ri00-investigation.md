# RI-00：周期停顿的调用链、坏基线与未闭合项

创建时间：2026-11-12
最后更新：2026-11-12
状态：已交付可重复坏基线与现场业务栈；RI-00未闭合，RI-01及整体重构未开始。没有性能修复或安装验收结论。

上游：[首次调查](desktop-runtime-responsiveness-architecture-audit.md)、[详细设计自审](runtime-isolation-detailed-design-review.md)、[RI-00门](../../playbook/runtime-isolation-ri00-baseline.md)。数值、原始请求时序、失败尝试和摘要指纹见[机器回执](../../playbook/evidence/runtime-isolation-ri00-20261112.json)。审查与实现为同一Agent，不称独立审查。

## 1. 此次纠正的结论

此前约190ms的隔离查询只装配裸SessionSupervisor，漏掉了Desktop注入的SessionVerification读依赖，也没有WorkBudget读取。这不是完整Desktop请求的基准。用它直接解释现场约500ms，或据此宣称已找全根因，均不成立。

补齐读依赖后，同一rc.41生产Module、同一隔离历史、相同Electron/Node的暖查询约426ms；现场两次自然查询的同步段为460–464ms，await剩余不足0.2ms。主要成本确实在main中的同步业务调用，而不是这两次请求的异步网络等待。仍有约34–38ms的跨场景差距；这不是同一请求的受控相减，不能给它指定未经验证的原因。

八个同时到达的只读IPC能产生3.54秒主循环间隙，单个handler仍可低于500ms。这证明连续同步回调能放大为多秒停顿。它不证明19:02原事件就是八次授权列表查询。

## 2. 候选、数据与测量边界

- 产品源固定`b05b7afbf26b43444635f77710397c3a658d6a0f`、`release/v0.1.0-rc.41`；没有产品运行路径修改。诊断代码位于Peer-Agent的`codex/ri00-responsiveness-baseline`，最终提交由机器回执绑定。
- 安装现场与隔离Electron均为41.7.1 / Node24.15.0 / macOS ARM64。七个关键安装产物与本地构建Module哈希一致，详见机器回执；不能由七项推出整个安装包逐字一致。
- 私有数据只读复制goal-plans、conversations、projects，共11,949文件、595,794,423字节；不复制Provider、凭据、identity或活跃lease。协调索引另用SQLite在线一致备份，revision6279、3,772,416字节。快照来自调查时刻，不是19:02全部内存和磁盘状态的回放。
- 每轮绑定harness、生产目录、三个输入Store及协调备份的运行前后内容指纹。诊断日志和SQLite锁文件是单列输出；原始11,949文件复核无改变。私有manifest、原始CPU profile和身份不上传，公开内容只有计量、源码位置和摘要。
- harness复用真实catalog owner、受信窗口、top-frame/origin和生产IPC注册。Renderer为隔离测试页，返回真实空授权结果；不是产品页面、原生键盘、滚动或安装包端到端验收。
- 宿主只有只读服务，`deferRecovery:true`、`canManageWorkspace:false`，没有runner、模型、工具或执行租约。协调Adapter只读一致备份，匹配既有读形状，不测source-token校验、恢复和writer检查；未装配live UI-delivery或完整执行宿主。
- cold指新进程/应用缓存，未逐出操作系统文件缓存。短轮不替代10分钟混合负载门；rAF流畅也不能证明main或输入流畅。

本卡先核对`00-adr-map.md`及`96-task-execution-responsiveness.md`、`98-large-history-execution-responsiveness.md`、`104-progressive-interaction-and-coordination-storage.md`、`112-runtime-module-and-loading-boundaries.md`、`121-desktop-session-windowing-contract.md`和`128-local-runtime-isolation-and-bounded-query-contract.md`。诊断脚本为C级，不改变现行运行契约、IPC产品面、权限、Evidence、存储归属或System Context。ADR128仍Proposed，不因取证自动接受。

## 3. 完整的已观测慢查询链

现场V8 CPU profile得到业务函数名，生产源码和隔离计数相互核对：

```text
Renderer invoke
  -> catalog-ipc-main：窗口/owner/来源准入
  -> register-project-agent-ipc
  -> ApplicationService.listObligationGrants
     -> selected为空仍调用sessionRows(workspaceId)
     -> SessionSupervisor.list / presentSession / project
        -> humanGateOf / acceptanceFacts
           -> indexedRefs
              -> GoalPlanStore.listEvidenceIndex
                 -> readEvidenceIndex / normalizeEvidenceIndexRecord
           -> hostFacts / Desktop.readSessionFacts
              -> SessionVerification.facts
                 -> findPlan：目录扫描 / GoalPlanStore.getPlan
                 -> factsFor / evidenceRecords
                    -> listEvidenceIndex / 全索引再次归一化
        -> WorkBudget.readSessionControl / readLifecycleFacts
  -> 空结果序列化、IPC返回
```

一次请求投影23个session，其中6个进入核验事实读取。裸宿主：23次getPlan、6次全证据索引读取、414,270行。补齐Desktop核验：3,855次getPlan，其中3,832次来自核验findPlan扫描；全证据索引12次、828,540行（69,045×12）。源码中的解析缓存没有消除每次全索引归一化及随后过滤。

另一个已观测调用入口是Bot get：`ApplicationService.get → directory.get → projectRow → sessionsOf/listSessions → Supervisor`；同一projectRow还走`readQuestionCards → ProjectFacts.questionCards → sessionsForProject → Supervisor`。这说明改变上层入口后仍会重新进入相同深事实读取。此处只记录调用关系，不把该入口的CPU样本拼进19:02事件。

冻结轮首个暖请求总同步段445.62ms：Supervisor445.29ms；直接证据索引153.08ms；Desktop.readSessionFacts215.84ms；coordination lifecycle36.94ms。后三项是Supervisor内不同子段，核验中的第二组Evidence读取又嵌套在215.84ms内，不能重复相加。完整inclusive/self计量和大于50ms的段保存在回执。

现场120秒元数据观察得到两次自然`list-obligation-grants`：同步464.27/460.15ms、总时长464.46/460.20ms；每次23次lifecycle共34.00/37.76ms，23次control共2.03/2.04ms。该窗口实际约60秒一次，符合后台节流后的观察，不能把源码15秒定时器当成现场必然15秒。只记录channel/时钟/次数，不记录参数、结果正文或用户输入。12处观察包装全部恢复。

## 4. 受控坏基线与探针成本

以下均是原产品实现，`--expect-stall`断言500ms门必须失败；脚本`ok:true`表示坏基线实验有效，绝非响应性通过。

| 冻结场景 | 暖handler p50 | 暖handler max | cold handler | 八请求主循环最大间隙 |
|---|---:|---:|---:|---:|
| 私有副本、裸Supervisor | 173.84ms | 183.52ms | 1541.26ms | 1425.90ms |
| 同副本、Desktop核验+协调备份、探针开 | 444.68ms | 466.92ms | 1937.28ms | 3542.28ms |
| 同进程off/on/on/off | off两组p50平均425.93ms | 原始各组见回执 | 不重新冷启动 | 不把不同轮max相减 |
| 公开合成夹具、Desktop核验、探针开 | 145.14ms | 146.84ms | 296.58ms | 1148.31ms |

同进程、同数据、相同宿主的ABBA对照：probe-off p50平均425.932ms，probe-on437.954ms，边际12.022ms。前一冻结轮同法为10.497ms。off仍保留根时钟和shim间接调用；该对照测分段FS/JSON/方法探针的边际成本，不声称“所有测量零成本”，也未把现场同步日志writer整体成本从自然业务段独立分离。

Transport-only对照往返p50约0.20ms。保存每次client send/receive与main enter/settle四时钟、序号和到达顺序；跨进程时钟校准声明每项1ms误差界，实际最小时钟步长约0.1ms。排队/返回是带不确定度的估计，不裁掉负的亚毫秒估计，不减两个不相干最大值。主线程单时钟500ms门不因校准放宽。突发轮每个IPC的排队、同步段与返回都能独立追踪。

V8 profile是诊断证据，不作为无profile验收。现场90秒profile启动ack243.29ms、停止ack41.85ms单列。最初关闭表达式使用动态import失败，却未检查Inspector的exceptionDetails，导致端口仍开；随后改用`process.getBuiltinModule`，检查实际返回并确认关闭。后续120秒观察恢复成功且端口关闭。最后拟做15分钟全入口观察时原pid已不存在（ESRCH），没有新样本；不能记成15分钟已验证，也没有重启应用。收尾时9229关闭。

## 5. 原始3.949秒：证据到哪里为止

应用日志轮转后，从本次聊天归档的原工具输出找回：

```text
[event-loop] at=2026-11-11T19:02:39.283 windowMs=1000 max=3949 mean=136
[phase] at=2026-11-11T19:02:39.283 name=plan.normalize calls=30840 hit=30840 miss=0 ms=68
```

同一区间还有19:02:34.623的max996、19:02:40.355的max934与watch.sync10ms、19:02:41.357的watch.reconcile1192ms。后者可能跨await，不能加入3949ms，也不能认定同一个父请求。原授权日志在11:02:35.830Z和11:02:50.884Z各有一次空结果完成；原事件附近没有八次授权列表调用证据。

30,840恰好等于当前完整查询3,855×8，是值得追踪的数量一致性。它不是调用身份、时序或原事件的CPU栈。八请求实验的3.54秒也不能仅凭接近3.95秒变成历史归因。19:00–19:09的电源事件没有实际Sleep/Wake/DarkWake迁移；PreventSleep断言不等于发生睡眠，当前不以睡眠解释停顿。用户不记得当时操作，不影响对上述事实的记录。

原事件当时未记录IPC父身份、同步任务序列与CPU调用栈。现在已经过去且原进程退出，这些信息不能从聚合max、归一化次数或用户回忆补造。原事件原因为**未证实**；已证实的是相同生产慢链及多请求连续阻塞机制。

## 6. 为什么多次优化仍反复，以及方案约束

已证实的结构问题是：轻量展示查询借用完整执行/签收事实API；下游通过宿主注入再次遍历历史；多个调用方把这些同步工作串到main。缓存原始解析、改一个入口或迁一个函数，都没有建立查询复杂度和主循环占用上界。上一轮裸宿主基准还遗漏真实依赖，使对比口径失真；只看单查询也漏掉了连续回调放大。过去针对具体路径的收益不能推导为整个应用已根治。

因此继续保留既定顺序：先闭合RI-00，再按固定详细设计完成RI-01选择性只读模型/索引、RI-02 Query Service与有界队列、RI-03唯一Runtime及存储/平台接缝、RI-04旧状态与异常恢复、RI-05最终组合真实交互验收。每阶段用同一坏基线先红后绿，保留语义、权限、Evidence、unknown、writer fence和后续任务准入。进程隔离与查询收窄必须同时成立；不把当前全量Supervisor搬到新进程后就收工。

## 7. 尚未闭合的门与下一次取证

| 门 | 当前证据 | 缺口 / 有效出口 |
|---|---|---|
| G1 原事件 | 找回原行、时间、周边日志 | 原父请求/CPU栈从未记录，不能追溯补造；若要求该历史事件的精确因果证明，RI-00保持未闭合 |
| G2 主差值 | 裸/完整读依赖对照、现场V8栈与同步时间 | 现场460–464与副本off约426仍跨场景；需同一代数据/状态的分段观察，单列source校验、UI-delivery、诊断writer及调度/GC，未证明的段继续unknown |
| G3 多秒机制 | 私有和公开夹具的真实IPC突发稳定失败 | 八请求数量是实验变量；仍需捕获自然多秒事件的父身份、到达次序、全部同步工作与采样栈，不能事后拼不同窗口 |
| G4 完整产品基线 | 有真实IPC、cold/warm、探针对照和预期失败门 | 未做原生连续输入/滚动、10分钟混合负载、真实模型、完整执行宿主、跨平台或安装候选验收 |

下一次有效现场采样必须在已运行的进程上有界收集：IPC入口只记channel/序号/四时钟、主循环间隙、当前执行段和CPU栈；对跨await段明确区分同步自耗时。全部观察有owner、到期恢复和实际端口关闭检查，启停成本单列，不记录正文或令诊断改变执行事实。若进程已退出则停止该次采样，不私自启动/安装/重启。新事件能证明新现场机制，但仍不能追认旧事件未记录的细节。原事件证明要求如需改为“同机制复现+前瞻现场闭合”，应由用户明确接受，不能由实现者自行降低门。

## 8. 重复运行与验证记录

代码仓提供`apps/desktop/scripts/seed-runtime-baseline.mjs`、`perf-runtime-baseline.mjs`及`ri00/`。先按代码仓说明准备依赖与构建生产包；本轮复用rc.41已构建dist，没有重建整个产品。诊断脚本所在checkout与被测生产Module checkout允许不同，但两者指纹分别记录。

```sh
# RI00_MODULE_ROOT指向已构建的生产候选；以下在诊断代码checkout执行。
ri00_fixture=$(mktemp -d)
ri00_output=$(mktemp -d)
node apps/desktop/scripts/seed-runtime-baseline.mjs --module-root "$RI00_MODULE_ROOT" --home "$ri00_fixture"
node apps/desktop/scripts/perf-runtime-baseline.mjs --module-root "$RI00_MODULE_ROOT" --fixture-root "$ri00_fixture" --bindings desktop --instrumented --expect-stall --output "$ri00_output"
node --test apps/desktop/scripts/ri00/*.test.mjs
```

合成数据默认1460计划、23session、6个历史候选、69,045条合成Evidence形状记录，明确不是实际执行、核验通过或用户Evidence；新ID由生产seed生成，重复的是负载结构而不是跨次随机ID指纹。`--bindings bare`用于缺宿主依赖对照，`--coordination-snapshot`只允许隔离一致备份，`--paired-probe --instrumented`运行ABBA。后续修复候选必须用`--expect-responsive`，不能继续把预期失败当成通过。

本轮Node25.9.0下15项聚焦测试通过，覆盖生产详细会话读seam、核验重复读取计数、损坏JSON、当前control head、只读writer拒绝、嵌套计量、并发请求隔离、异常/恢复、时钟量化与输入指纹；architecture/UI约束、语法与diff核对通过。未运行全仓构建/类型/测试或全产品回归，因为改动限诊断MJS脚本，不据此声称原应用已修复。

启动参数、首帧基准、时钟量化、首次输入指纹范围、SQLite备份重开及Inspector清理的失败均保留在机器回执，不能用最终成功覆盖。第一次synthetic冻结轮与聚焦验证短时重叠，保留结果，另做无并行验证的sealed-v3-synthetic作为冻结对照。私有快照和profile仍在本地受限取证目录，未上传、未作为模型任务上下文使用；跨机器可用公开seed复现实验机制。
