# ADR 98：大历史规模下的任务执行响应性

创建时间：2026-10-18
最后更新：2026-10-19
状态：Accepted（负责人要求先完成 ADR，再按 P1 → P2 → P3 实施；验收结果另记，不以本状态宣称实施完成）
级别：A。关联 ADR 80、85、92、94、95、96、97；产品北极星和工程治理继续生效。

## 1. 决策背景与可复现证据

RC18 用户反馈：任务执行时输入、滚动同时卡顿。只读现场采样中主进程 25 秒 CPU 峰值约单核 136%，均值约 46%；不能用一次空闲采样代表执行窗口。

在权限 0700 的真实历史隔离副本上运行生产 Conversation Store、SessionSupervisor、Project Facts 与 BotDirectory，未启动任务、未复制凭证至该副本、未修改用户数据：

- 1,059 份计划，8 个委托会话；协调日志约 185MB，父对话约 9.5MB，已有大对话约 46MB。
- 一次最近 50 条对话投影耗时 618～734ms；`getPlan` 26,475 次，即 25 次扫描全部计划。任务查询、acceptance、completionReview 和 deliveryFacts 各自查找计划。
- 同次查询对话相关读取约 54MB，恢复检查点约 41MB / 27 次。历史错误即使已被替代，仍读取检查点；任务投影读取全文构造报告、干预列表及仅需 createdAt 的元数据。
- 此为包含真实存储与任务投影的查询下界，缺少活跃执行器、审批与完整 IPC 成本，不称完整端到端输入测量。

既有小型真实任务和 200 Bot 合成验收没有覆盖此计划分布、错误历史与内容密度。旧输入指标从 DOM input 事件计到 rAF，漏掉 Browser 主进程分发前的等待。旧脚本 setViewportSize 将 DPR 设成 1，也未覆盖日常 Retina 窗口。运行文字渐变带来额外绘制成本，但单独动画对照没有复现全部卡顿，不将绘制当作已证明的唯一原因。

## 2. 目标与不变量

1. 热查询成本随当前项目相关计划、变化文件与当前活动增长，不能按“全部计划 × 任务数 × 消费者数”增长。
2. 展示共享同一次读取中的事实；执行、权限、签收仍在命令边界重新读取当前宿主事实。缓存不能批准能力、接受结果、恢复未知工具调用或隐藏真实失败。
3. JSONL、计划、检查点、sidecar、PermissionGrant 和 Evidence 真源及格式不变；无用户数据清理、迁移、日志截断或旧版本读取破坏。
4. Renderer 保持表达职责，不读取文件、不执行能力；无新工具通道和系统提示旁路。
5. 活动、最终结果、授权、取消和失败均不丢；跨 Bot/卸载迟到结果不回写错误页面。
6. 每一优化都有对照和正确性测试；测试失败与真实 Provider 失败保留。只有通过全部指定验收才能声称执行流畅。

## 3. Module 与 Interface

### 3.1 Delegated Plan Catalog 与 Read Query Scope（P1）

新增独立 Catalog Module，Interface 提供当前委托计划目录；Implementation 按文件身份、大小、纳秒 mtime/ctime 校验候选文件，缓存其是否委托及所属项目，只有相关候选进入现有 getPlan 归一化/overlay/完成门。新增、删除、同长度改写、替换、跨进程写及损坏必须重新判断；目录 mtime 本身不足以证明文件未变。缓存有界，逐出不改变事实。已有完整 getPlan 不成为可变共享全局缓存。

SessionSupervisor 的同步展示 Query Scope 在一次调用内复用 Catalog、按 sessionId 查找、会话投影和协调投影。嵌套读取共享最外层 scope；退出或异常立即释放，不跨 await 延续，不承载写操作。批量卡片投影显式进入此 seam；单项公开读接口也建立 scope。返回值不能泄漏可污染下一查询的内部引用。

scope 中的复用仅节省同一同步观察内的重复工作。取消、派发、amend、恢复、签收等命令继续沿原 exclusive/lease/PermissionGrant 路径，不能借旧展示快照执行。

后台恢复的调用边界也纳入 P1：`hasContinuation → recoverJob → resolveRoster → Supervisor.list` 不得对没有候选工作的 Bot 无条件查询任务目录。遗留预算恢复和 continuation custody 的 Interface 接受数组或惰性读取函数；Implementation 先检查本地 work、预算与 checkpoint 候选，确实需要子任务事实时才调用读取函数。一次 custody 的分组阶段共享同一只读 roster，写阶段沿原规则执行；不跨恢复操作保存 roster，不缓存权限或执行准入。恢复候选先按 runnable、到期 reservation 和已核对的 system block 筛选，再为这些候选读取 user input 检查点计算优先级；paused/delivered/cancelled 历史不因排序读取正文，候选间用户优先级及原恢复顺序不变。定向测试覆盖空 Bot、paused/delivered 历史、真实候选、失效与 coalesce 结果，不能用跳过恢复提速。

### 3.2 Session Conversation Facts 与 Recovery Card Admission（P2）

任务投影只请求报告、干预 ID 和创建时间所需的紧凑事实，避免为了 createdAt 调用合并流式正文的 getConversation。报告计算必须沿用 buildSessionReport 的可见正文选择、provisional tail 排除、Evidence refs 和 sourceRevision 语义，不把 thinking/tool 参数升为报告。

紧凑事实缓存由 Conversation Store/宿主的只读 Module 管理，以真实历史、sidecar 文件版本和 contentRevision 为失效依据；不能仅依靠事件或时间 TTL。缓存条目与总量有界，返回隔离值；替换、删除、同长度改写、损坏、外部提交和 sidecar 变更立即失效。缓存不供授权和执行命令作真值。跨进程写入若恰好发生在描述与读后版本校验之间，丢弃该次投影并最多重读 3 次；每次重新取得版本，持续冲突仍明确返回 BACKGROUND_VERSION_CHANGED，稳定损坏仍返回原严格错误，不回退旧事实。此规则修复终端客户端与另一进程宿主并发写入时的可复现读取失败，不以放宽错误隐藏竞争。冷解析及发生变化后的重建独立计时；若大文件同步解析仍超预算，将该纯持久化投影准备移到 worker，经文件版本复核后发布，不把未知/旧值冒充当前事实。

同一 Store 提供投影工厂，任务报告缓存只保留最后可见正文与干预 ID；卡片事实剔除内部 rounds 和附件正文。Bot 历史读取为保留现有过程详情字段，可以使用独立的有界展示快照缓存（最多 8 会话、合计 32MB），不得修改原记录或把此展示缓存替换执行读取。超过容量不缓存，不能截断消息。两类缓存均逐次校验文件版本、返回隔离值，不能只凭 TTL 命中。

恢复卡先判断结构化历史关系、终态和廉价准入条件。已 superseded/recovered/cancelled/paused 的历史卡不读取检查点；无法恢复的终态也不加载恢复正文。仅当前可继续候选按需读取所需检查点。复用只可针对已校验文件内容；实际恢复命令重新检查当前 lease、预算策略、未结算工具与检查点，不能使用展示 canContinue 直接放行。

追加写入的 Interface 增加可选 `returnMessages:false`：只返回已持久化的会话元数据，不为了被忽略的返回值重新读取整份 JSONL；默认返回完整会话的旧契约保持不变。Desktop Project Agent 的 append 适配器使用该选项，通知仍在原持久化调用成功之后发出。该元数据不是新 Evidence 或成功签收凭据；幂等检查、执行读取、锁、contentRevision、标题与计数更新沿用原路径。定向测试必须证明不读正文、正常追加、默认兼容、空消息规则及写失败不通知。

### 3.3 Presentation Refresh 与 Activity Rendering（P3）

使用有界的合并刷新 Module，合并同一 Bot 的 changed/conversation-changed 突发，最多一个在途读取和一个待刷新标记；异常可重试，卸载取消待调度，不积累 Promise 队列。最终状态和输入关联仍由成功读取确认，不能用静默吞事件提速。

未改变的历史消息保留对象身份；当前 Activity 更新不重新派生整份历史、重建所有监听器和测量历史节点。虚拟列表按实际视口和有界 overscan 工作，不能在 200 条以下无条件挂载全部内容。高度变化与滚动锚点保持稳定，引用跳转、选项发送、历史加载及键盘阅读不退化。

运行状态动效采用合成友好的 transform/opacity 或静态表达，避免 background-position 文字渐变每帧重绘。隐藏窗口、离屏和减少动态效果继续停止动画，不通过禁用全部动效达到性能目标。

## 4. 顺序、范围与回退

1. P1：runtime-node 的 Catalog/Query Scope、SessionSupervisor 装配与计数回归，先验证扫描复杂度。
2. P2：Conversation Facts、历史恢复卡按需读取及失效/污染/严格错误测试，再测真实隔离历史。
3. P3：Renderer 刷新、稳定身份、虚拟窗口与动效；补端到端测量。
4. 全部受影响包测试、typecheck、architecture、标准产品 capture → AI 自审全部必查图片 → verify；随后真实模型大历史任务。

允许改动为上述 runtime-node/conversation-store Module 与类型/构建清单、Desktop project-agent 装配与 renderer/state/styles、测试/验收脚本。main.mjs 只允许净零或减少的装配替换；性能修复本身不改版本、发版配置、权限策略、Provider 编码和认知提示；后续负责人追加授权的 RC19 发布与 ADR99 记录的回复恢复修复单独说明。需要 worker 时只负责持久化内容的纯投影准备，不能执行工具。无新增依赖或持久化真源。可分别回退 P1/P2/P3，不删除历史、不自动重跑未知执行。

## 5. 验收矩阵与通过门槛

### 5.1 正确性与复杂度

- 至少 1,100 份计划，其中 8～12 个委托任务，其余为历史非委托计划。稳定刷新只归一化相关候选；一次批量查询只扫描目录一次，不出现消费者乘法。
- 同进程与跨进程更改、overlay、同长度且恢复 mtime 的改写、rename 替换、删除、损坏、LRU 逐出、caller mutation、scope 异常退出/嵌套均覆盖。
- 至少 185MB coordination、9.5MB 父会话、46MB 子会话及多份历史失败/恢复检查点；使用生产 Module 与完整任务事实。冷/热、变更后读取分开报告，不能只测空任务端口。
- 热 conversation/cards/sessions 查询 p95 < 50ms，常规变化后查询 p95 < 100ms；主进程执行窗口 >50ms 停顿逐项解释，不能靠平均值掩盖连续卡顿。

### 5.2 真实任务与交互

在隔离数据根和隔离项目运行已配置真实 Provider，经主 Bot → 独立子 Agent → 文件/命令工具 → Verifier → 宿主签收 → 正式回复；实际修复并运行检查。覆盖任务详情开闭、连续输入草稿、真正滚动 scroller、加载历史、取消后新回复和至少一次大历史终态提交。真实模型输出不能替换为注入 Tool Results。

分两组：同等规模的可分享合成数据用于云模型；用户历史隔离副本只做本地生产读取/绘制对照，禁止把无关私人历史发送给真实 Provider。若使用真实历史作新任务上下文，须先获得明确内容出域授权，不能把性能授权解释为上传全部历史。

窗口保留原生 DPR（Retina >=2 时必须记录实际值），宽窗/窄窗、详情打开和内容密集历史均覆盖。至少 120 秒真实任务交互窗口和 100 次输入/滚动采样；较早完成则继续实际对话/已授权检查，不能伪造任务运行。

记录以下独立指标：

- 按键发出至页面处理/绘制的端到端延迟（包含自动化传输成本，不能冒充硬件测量），p95 <100ms，p99 <200ms，max <500ms；DOM input→rAF 单列。
- 实际滚轮输入、scrollTop 变化与 scroll→rAF 延迟，p95 <100ms；rAF 帧间隔 p95 <32ms；>50ms renderer long task、最长连续停顿逐项列出。
- 主进程 event-loop delay、主/renderer/GPU 进程 CPU、挂载行数、输入样本数、当前历史规模、源 HEAD/脏状态和模型；GPU 数字为进程 CPU 而非硬件利用率。
- 健康任务持续推进并最终正式回复；取消、权限和恢复原语义不退化。渲染指标通过但任务未完成，不称完整通过。

### 5.3 交付事实

产品回归为实施者自审，明确 independent=false；真实模型、源码 Electron、签名安装包、无障碍覆盖分别列出。初始性能授权不含发布；负责人随后明确追加查明连续失败、修复、自主验收并发布 RC19 的授权，按 ADR99 与 RC 发布门禁执行。替换日常安装仍不属于测试范围。没有通过本 ADR 的大历史真实任务，不宣称已经根治。

## 6. 实施记录

代码审阅：[Peer-Agent #169](https://github.com/ly-ccx/Peer-Agent/pull/169)；设计审阅：[Peer-Knowledge #49](https://github.com/ly-ccx/Peer-Knowledge/pull/49)。P1 → P2 → P3 依次实现并提交；真实任务和产品验收尚在进行，本节不宣称整体通过。

### 已完成的实现与局部验证

- P1：独立委托计划目录与同步 Read Query Scope；1,100 计划/8 委托候选，一次查询的 25 次消费只执行 8 次 getPlan。保留跨进程文件版本校验、overlay 和原完成门。
- P2：版本校验的有界展示投影工厂、紧凑任务报告、历史错误检查点按需读取与当前恢复视图。严格历史错误、sidecar 排除、caller mutation 和文件替换等进入测试；真正恢复命令继续使用原始检查点。
- P3：80ms 有界刷新合并、消息身份复用、40 行以上按视口虚拟化、稳定几何键和 footer 测量合并；运行文字保持静态可读，不再逐帧绘制渐变，当前身份 SVG 动效仍可用。
- 全仓 build/test/typecheck/architecture 在实施后的产品代码上通过；新增验收夹具另以生产 Supervisor 确认 8 个历史会话均为 cancelled，18 个多文件测试在缺陷实现上真实失败且语法有效。原有 Desktop 5 项 skip 未新增。

### 读取性能

同规模合成数据使用完整生产 Supervisor/Facts/Directory：1,100 计划、8 会话、9,636,034 字节父对话、46,417,948 字节子对话、185,000,987 字节 journal、32 个历史错误。各 20 次热查询：conversation p95 7.53ms、cards 4.95ms、sessions 4.13ms，每次最多归一化 8 个候选；首次冷 conversation 为 134ms，单列保留。

用户实际历史的本地隔离对照（未启动任务或 Provider，副本 finally 删除）：journal 已增长至 189,309,887 字节。20 次热 conversation 查询 p50 25.03ms、p95 28.34ms；每次 getPlan 为 8 次，热检查点正文读取 0 次。首次冷读取 248.70ms，仍是启动/冷读取成本，不能用热数值宣称冷恢复已经无阻塞；执行期间有变化的大文件与主循环停顿继续由真实任务测量。

### 保留的失败尝试

1. 首轮混合 GPT-6.1 Sol / DeepSeek 最大强度真实任务：文件修复与命令测试通过，但 DeepSeek 一次独立复核返回工具协议正文而未产生结构化工具调用，按现有 guard 形成 unsupported_tool_response，未放宽门禁。主 Bot 曾查询、重核并派出补救任务；窗口结束时尚未完成签收，不记完整通过。该轮采集器还错误地对合成历史会话断言当前冻结档位，最终报 default 与 undefined 不等；随后修正为只校验本轮真实会话，并补上失败时采集数据的 finally 路径。不能将 2,274 次已执行交互等同于完整性能通过，该轮缺少最终端到端统计。
2. 后续源码 Electron 启动一次出现 Resulting promise was garbage collected，在发送任务和采样前结束；保留为启动失败，不计为任务/性能通过。增加进程退出与错误堆栈诊断后重新启动。
3. 多文件负载的单元验收首次继承 NODE_TEST_CONTEXT，Node 拒绝递归运行测试，错误返回成功；显式移除该子进程环境变量后确认 18 个测试真实执行并在缺陷实现上失败。未改动产品测试断言。

### 待补的最终闸门

18 用例、三实现文件、两万行聚合的真实 Provider 全流程；原生 DPR 下输入、真实滚轮、主循环与大历史终态提交；取消后继续回复；标准产品全部必查截图的实施者自审与 verify。未发布 RC、未替换日常安装，尚不能宣称完整验收通过。

### 大历史真实任务的首轮完整结果（2026-10-19）

GPT-6.1 Sol 最大强度在 1,100 计划、185MB journal、9.6MB 父会话与 46.4MB 子会话下真实修复三份实现；18 个测试、独立模型复核、宿主签收、正式回复、主动取消后继续对话均通过。原生 DPR=2、1280×860；连续约 12.5 分钟，2,688 次输入和 2,688 次真实滚轮均产生滚动；测试文件额外按初始 hash 逐份确认没有修改。

功能成功不等于性能通过：输入往返 p95 20.79ms、p99 21.59ms、max 545.56ms；滚轮往返 p95 27.21ms、max 696.64ms；主循环 p95 1.38ms、max 699.40ms；renderer 帧间隔 p95 9.70ms、long task 0。最大输入延迟超过 500ms 门槛，因此此轮明确不通过性能验收，保留失败，不放宽阈值。46MB 历史终态提交经真实 worker 约 105ms，但该步骤的并发输入覆盖仍须补强。

隔离副本上的后续压力诊断（无 Provider，不算真实任务验收）显示：会话 append 后触发展示投影重建时，主线程出现约 75～79ms 阻塞；46MB 终态提交后首次投影重建约 70～75ms。单次 append 本身约 16～18ms；不能把整个重建成本说成磁盘写入。该短诊断没有复现 700ms 尖峰，继续以真实任务记录长调用堆栈，禁止据此宣称尖峰已解决。

### 周期性尖峰的进一步归因

附带 CPU 采样的真实任务中，多个 233～394ms 主循环窗口由 `runtime-host.sync → hasContinuation → recoverJob → resolveRoster → delegated-plan-catalog` 主导；单个窗口内 stat 系统调用采样可累计约 82～114ms，目录枚举另占约 25～36ms。12 Bot 夹具中空 Bot 的恢复检查仍无条件取得 roster，形成跨 Bot 的扫描乘法。此证据补上了之前只测 conversation/cards/sessions 热查询漏掉的后台执行入口。

此前包装 JSON 的诊断运行在 Playwright evaluate 上下文，未证明覆盖 Node 模块使用的全部 JSON 调用；因此“没有任何慢 JSON”不能作为结论。CPU 采样用于归因，采样器自身 stop/start 的时间另行识别；最终性能验收仍须关闭采样器。


### 验收采样器自身成本

旧采样器每次等待都会全文重新解析约9MB的隔离对话，可能污染自动化往返时延。现按文件 dev/ino/size/mtimeNs/ctimeNs 复用采样器自己的只读结果，变化时重读，变化中或不完整尾行等待下一次采样；不缓存执行授权。滚轮超过100ms的样本另记录自动化派发等待与 rAF 等待，原始总体分布与通过门槛不变。该调整属于测量工具，不能冒充产品性能优化，也不据此将旧失败改为通过。

### 真实交付路径的残余放大（2026-10-19，实施前补充）

最终阶段已真实完成三文件修复、18项原有测试、独立上下文复核、宿主accepted与正式交付，取消后回复也通过。但持续采样仍记录到411ms主循环尖峰。额外诊断重现332ms/418ms连续窗口和约30秒一次的96ms窗口；原始性能通过不等于这些停顿已经消失。

CPU调用栈定位到两条未收敛的路径：`post_reply → deliveryFacts → acceptance → parentMessages → getPersistedConversationHistory` 对多个会话重复读取/解析同一主对话；`beforeTool / coordination lifecycle / recoverJob → coordination-journal-reader.read → structuredClone` 多次复制整个已验证协调状态。另有恢复名册的重复归一化。凭据助手本轮约23ms、元数据采样约0.35ms，都不能解释400ms尖峰。

补充设计：

1. Acceptance Parent Facts复用已有版本校验History Projection，只保留锚点正文、消息身份及正式引用事实；同步Read Query内同父会话只取一次。不把正文预览当Evidence，不改变签收规则；跨查询仍校验文件版本，错误严格传播。
2. Journal Reader增加单工作读取Interface，在相同完整日志验证与文件版本检查后，仅克隆指定work。默认read仍返回完整隔离副本；readWork不返回私有缓存引用。Work Budget及saveWork只取需要的work，不复制全部历史工作。
3. 恢复协调器一次同步判定内复用观察到的协调快照；本判定内一旦写入必须失效重读。异步或跨判定绝不复用授权/执行真相。

这是B级Module接口与缓存Locality修复，不新增持久化真源、不改协议、权限、Evidence或原日志格式。先补计数、失效、调用者污染和严格错误测试，再实现；之后重新跑大历史真实调用与交互，不将诊断带采样器的统计冒充最终无采样器验收。

单工作读取补充后的对照仍出现410ms窗口，不能记为性能根治。剩余调用栈为每个会话的`coordination-lifecycle.forSession → read`，它只需要mandates/transitions/decisions和工作停止状态，却复制了完整works预算及历史events/deliveries。Journal Reader补充独立命名的`readLifecycleFacts` Interface，返回当前完整验证后的控制记录及最小workStates，不暴露私有缓存；仅纯facts/forSession使用。coordinate/recover/effect和内核admit仍读原完整状态，不能使用这种展示投影授权执行。该补充仍须同场景对照，不将410ms标为已消除。

进一步追踪到Desktop的Bot Directory把完整`history.messages`作为列表/get/markRead读取端口，版本缓存命中后仍反复structuredClone约9.6MB内部rounds。补充明确的Summary Messages / Batch Interface，仅给列表、get和未读游标提供预览、提问/回答和时间事实；原readMessages继续给聊天分页和完整回复详情，绝不以摘要代替执行或Evidence。摘要Module复用版本投影工厂，丢弃rounds/segments/附件像素，只保留列表算法实际读取的字段；跨文件变化与损坏仍严格处理。不增加IPC或持久化真源，默认未接入的宿主继续原读取行为。

摘要拆分后的诊断仍有357ms连续窗口。CPU样本分散在多次有界查询、fsync和状态提交，而不是一个单独400ms文件操作：连续Promise微任务把几段同步本地工作串成一次长占用。补充调度公平性：Desktop执行器在进入新认知步之前、完整工具批次及原生检查点成功持久化之后、用量/未决结果完成登记之后，使用原生事件循环让出。同步PermissionGrant、执行和Evidence提交中间不得让出；不把未配对结果留给后台重试。所有下一次请求/派发继续经过原signal、lease、版本和权限检查；让出本身不可变成checkpoint_persistence_failed。补充真正macrotask心跳及“检查点完成后取消，不发下一次请求”测试。内部同步接口保持，既有async Seam增加公平调度，不引入新的执行路径。

公平性对照还记录到约300ms窗口。装配审计确认：Runner的readMessages、hasMessage和Objective上下文仍走未经缓存的完整历史读取；一次完成/去重判定多次解析同一主会话。Desktop将这些完整读取接入现有32MB有界版本缓存，保留全部消息/轮次和复制隔离；Evidence正文读取仍走原严格入口。仅消息身份判断使用独立ID投影，Runner新增可选hasMessage本地端口，缺省继续原完整读取。默认InputQueue缺省行为不变。不得把列表摘要传入模型上下文或执行判定。

### 200 机器人列表缓存边界

最终 Linux CI 的列表投影 p50 为105.88ms，超过既有100ms门禁。新摘要读口沿用了通用32会话 LRU，200机器人轮询会反复淘汰全部摘要；每轮重新解析历史与投影。摘要专用缓存扩大到512会话，仍受8MiB总量硬界限及严格文件版本检查约束；完整历史缓存保持原界限。新增200会话多轮读取和单会话版本变化回归，不放宽CI预算。

## 最终源码实测与剩余峰值

冻结候选 `ecf21f0d7efb06b415905f1ce57896a7e2711c9b` 全仓门禁、37项升级恢复及双平台CI通过；200机器人列表p50为Linux40.71ms、macOS32.87ms，预算保持100ms。新180图包Verify通过，实施者自审（156张变化图重新看图、24张与已审哈希相同），六项轻微布局/捕获限制保留。

真实DeepSeek/max全流程：1100计划、约185MB日志、9.6MB主会话、46MB子会话；实际三文件修复、18个不可修改测试、独立上下文复核、宿主签收和正式回复，取消后继续与5810字符完整回执均通过。同一work换GPT恢复和重启通过，原执行回执/原生批次未重放。1801组交互中输入/滚动p95为21.09/27.38ms，帧p95为10ms、最大17.7ms；输入绘制最大9.7ms，渲染长任务为0。结果回流阶段仍测得470–485ms往返和283ms滚动绘制峰值、主循环最大494ms，完整保留，不宣称零峰值或长期日用已覆盖。

源码首张真实任务截图停在中间历史位置，并出现生成历史中缺少`turnId`的旁白行：该字段在当前真实agent_turn生产记录中由宿主写入；缺少它的生成行不能证明完整历史旁白渲染负载。正式签名包补测先保存生成原始快照及哈希，仅为`scale-turn-*`记录补上其自身id作为turnId，不修改真实输入、工具结果、权限、Evidence、交付或验收记录，再以实际四次46MB提交和真实长回执调用测量输入/滚动。正式包另须定位并展示实际三文件任务的正式验收回复。源码数字与正式包补测分开，不能互相替代。

### 正式包收口

RC19公开签名包补测通过：250条生成历史身份字段修正后，1511组真实调用期间交互，输入/滚动p95为20.75/27.17ms、最大114.02/71.70ms；渲染帧p95为10.1ms、最大25ms，渲染长任务0，输入/滚动绘制最大9.7/27.2ms，主循环仍有285ms峰值。四次46MB持久提交约103–106ms且有并发交互。正式包的自身助手、实际模型恢复/重启、45秒无新派发观察、原正式验收回复展示均通过。完整范围、六项产品限制、保留失败和公开资产在[最终证据](../../playbook/v0.1.0/evidence/rc19-published-validation-20261019.json)中；此结果不代表零延迟峰值或长期日用。

## RC19 安装后全局停顿：真实状态分布复现与修复补充（2026-10-19，B 级）

负责人反馈 RC19 安装后所有操作间歇停顿，滚动只放大症状。此前规模夹具虽覆盖日志、对话、计划大小，没有充分覆盖实际恢复记录和未处理事件分布；上一轮性能通过不能代表本次场景已解决。

### 新证据

已安装 RC19 的主进程采样显示同步文件访问和对象序列化集中在定时器执行链，三个 Renderer 在采样窗口大部分空闲（该窗口未证明包含每次用户手势，不能据此排除全部渲染问题）。实际数据中约 190.9MB coordination journal、2.9GB 历史 checkpoint。体积本身不是根因。

仅在本地、无凭据/Provider/工具执行的隔离副本中，以生产 Desktop 装配和原查询/恢复入口复现：热 host.sync 815–865ms，事件循环连续间隙约 832–901ms；首次冷恢复 2485ms。CPU 样本 structuredClone 自占约 7.90s，stat 4.64s；主要上层为 runner-coordination.transfer（反复 resolveRoster）及 verification-dispatch-recovery.reconcileAll（每个 work 复制完整 state）。此运行带采样器，只作归因和前后同条件对照。

### 实施 Interface 与边界

1. Verification Dispatch Recovery 发现工作 ID 后，使用已有 readWork Interface 读取单项，并在实际状态提交前再次读该项及检查 lease/active attempt。未实现 readWork 的旧 Adapter 兼容原 read。不可共享可变全量状态、跳过当前状态复核、改变未知执行或核验判定。
2. 一次 transfer 的只读事件分类共享一个惰性 roster；没有需要分类的恢复事件时不取。复用仅活在本次同步分类内，提交/下一次调用不复用，不能变成授权缓存。
3. 先补“历史工作增长不导致重复全量克隆”“多事件多恢复工作仅一次 roster、下一批重新读取”“回调期间取消/租约丢失不可提交”的失败测试，再实施并重跑本地真实副本。若仍有明显长占用，继续按 CPU 调用链收敛，不以平均/P95 合格宣称消除峰值。

权限、Evidence、Tool Result、持久化格式与认知策略不变。修改范围为上述 runtime-node Module、必要的调度公平性 seam 和诊断/回归脚本；不改日常历史、清空任务、关闭主 Bot、停用权限，亦不把私有历史发给云模型。最终验证分别报告真实历史本地副本、可分享夹具真实模型、正式安装包覆盖；未重新验证不称修复完成。

首轮两处修复后，同场景热 sync 从 815–865ms 降至 184–197ms，但仍不可验收。后续 CPU 样本显示：历史送达回执的 onRecovered 逐条复制整份 works；熔断卡的存在性判断每轮复制完整对话。补充收敛：Runner Coordination 的单 work 读取统一使用已有 readWork；恢复卡的两个消息 ID 判断统一使用已有 hasMessage（旧 Adapter 仍回退完整消息）。空 pendingExecution 时不读取完整对话；非空仍按原历史答复/停止事实进行持久确认，不用内存已拥有代替完成。上述均为已有 Interface 的消费修复，不新增协议或缓存真源。

第二轮热 sync 为 141–153ms，仍不能表示日用流畅。补充两个已有 seam 的收口：

- Host 增加可选本地 readInputFacts（默认沿用 readMessages），Desktop 用现有严格文件版本投影，只保留 pendingExecution 实际读取的回复锚点、停止 turnId、用户 inputId。完整 Runner 上下文、执行和详情仍用原 readMessages；投影不得传入模型或充当 Evidence。非空队列仍依据持久化事实完成确认。
- Host 的输入归属核对、watch/continuation 观察、kick 之间，以及 Runner pump 选取下一工作之前，在原 async seam 使用 Node macrotask 让出。让出后重新检查 disposed/lease；工具执行/授权/Evidence 原子区间内不插入让出。单轮旧读取结果不能越过恢复/执行的原守卫。验证让出期间取消或租约失效不会发请求；不能以延迟后台运行/停用功能代替公平调度。

冷启动 journal 回放仍单列，不将热优化冒充冷恢复无阻塞。最终必须关掉 CPU profiler 测量连续主循环停顿、原生交互和最大值，不能只报告 P95。

CPU 第三轮确认剩余热占用还包含 custody 发现阶段反复解析数 MB checkpoint。补充明确的 readContinuationCheckpoint Interface：以严格文件版本校验的有界内存投影，仅返回 job 的身份、kind、interactive、用户 inputId/createdAt 与事件 eventId/kind/sessionId；仅作候选发现和优先级。真正合并写入与执行选中项必须重新 readCheckpoint 原文，保留原始 outcome、完整 events 和 native batch；不可把发现投影用作续跑检查点。旧 Adapter 缺此端口仍按原文读取。该派生缓存不改磁盘真源，损坏/替换/删除严格失效，计数与冷/热读取测试必须覆盖。

首次原生 DPR=2、1440px 真实历史界面对照（各65秒，均无 CPU profiler）：修复前输入 max1010ms、滚轮983ms、主循环985ms，P95 却仅22/62ms；说明旧 P95 闸门遗漏间歇停顿。修复后首轮输入207ms、滚轮213ms、主循环103ms，仍不能宣布无卡顿。继续将 Runner 本地 takeNext 异步化，在用户续接发现、未处理事件筛选与后台续接发现之间使用1ms计时器让出；每次让出后重新检查 disposed/lease/新用户输入，实际派发仍走原 runJob。1ms 是事件循环公平调度，不延迟或停用后台工作；重试与执行预算保持原值。Verification reconcileAll 只发现含未决 verification dispatch 的工作 ID，再以 readWork 校验当前项，历史无关工作不逐项 stat/复制。

完整窗口 profiler（本地实际历史副本，55秒）定位剩余三处具体放大，未将该带 profiler 运行作为性能通过：

1. publishWatch → delegation-facts-reader 调用 listPlans，后者的 projectUiMeta 会在过滤项目归属前 hydrate 大量 completed plan。新增 listPlanMetadata Interface：只返回规范化索引发现元数据的隔离副本；Watcher 用该口先过滤归属，再对选中计划 getPlan，保留原 watchFacts 及完成门；原 listPlans UI 语义不变。
2. Bot readConversation 热刷新仍从完整历史投影复制内部 rounds，单次 clone 约10–12ms，之后还要按页重复传输。新增可选 readConversationMessages 本地口：Desktop 以严格版本的有界历史投影排除内部 rounds，保留公开段落、正文、附件和卡片；readMessage/回复详情与 Runner 继续完整原文。Renderer 不以展示投影认定执行/权限；不得损失点击后的完整过程。
3. input-queue.readInputs 每次消费/确认都会重新解析并校验历史图片的 base64。新增队列内部有界规范化缓存，严格文件身份/版本及 strict 模式分别命中，冷读仍完整校验；返回扁平规范记录和数组/附件对象的隔离副本（不可变字符串可共享），不缓存 lease、游标或执行权限。外部修改、同长改写/恢复mtime、删除、损坏、严格/宽松隔离、调用者污染均须覆盖。

这三处是已有持久化真源上的读取/投影 Interface 调整（B级），无协议新通道、权限放宽、工具旁路或持久格式变动。

展示投影的兼容收口：既有 read-conversation 增加可选 `presentationOnly: true`（常规聊天刷新）与 `processFor: messageId`（用户显式打开某次过程，禁止与 presentationOnly 混用）。旧调用默认仍返回原完整页。processFor 从完整历史按既有精确 turnId/旧版当前输入内最近 turn 规则选出该回复及其源 turn，不把整段聊天交给 Renderer。Renderer 的详情读取 Module 只在打开历史详情时请求、隔离过期响应，失败明确不可用；活动详情继续真实 Activity。完整过程不混回聊天分页缓存，不每帧重取，也不改变权限/Evidence/消息身份。输入参数类型和定向/窗口测试同步补齐。

常规页仍需保留用户输入上的“已派发/排队/取消/取代”等真实处置。新增明确的 `dispositionCalls` 展示事实字段：仅由宿主从实际持久化 spawn/message/cancel 调用投影所需的最小 input/result 字段，并覆盖任何同名存储字段；Renderer 只用它计算处置和任务名字，不将它渲染为完整执行过程。完整 rounds 仍仅由详情按需获取。旧页没有该字段时继续原 rounds 规则；模型提供的 dispositions 字段仍不采用。定向测试比较原调用和投影的全部处置结果，并保留真实失败、嵌套回执、依赖及标题。

恢复选择收敛为 `RunnerCoordination.selectNext`：原 takeNext 的 recoverUserJob → pending（再次 coalesce）→ recoverJob 三阶段重复准备，在同一次同步观察内只执行一次核验回执协调、reservation 到期、旧预算迁移、custody 与已报告等待核对；随后按原优先级选择用户续接、未处理事件、后台续接。没有跨 await 或跨调用缓存；任何本阶段 work 写入使 decision snapshot 失效，缺失 checkpoint 的阻塞写入后也重新读取。独立 recoverJob/pending Interface 保留兼容；实际选中仍原文读取、原 prepare/runJob、当前 lease/版本/权限门。新增计数及选中次序/写后重读测试，不能将 stale job 当作可执行事实。

可分享的大历史真实模型夹具同时补足状态分布：默认200项历史work，其中100项已送达、100项明确work级暂停，并包含对应的已送达回执；维持1100计划、185MB日志及大主/子会话。所有历史均明确synthetic，只增加负载，不给新任务注入结果、权限或Evidence；历史计划保持取消，不安排旧任务执行。生成agent_turn正式写入其自身turnId，避免再次漏掉公开旁白渲染负载。小规模单元夹具可缩减数量，必须验证实际重放状态数、终态和回执数。性能门禁覆盖单次峰值与P99，不能只以平均或P95通过。

834组无采样操作仍有输入231ms、主循环102ms峰值（P99输入59ms，滚动53ms），保留为未收口轮次。后续55秒CPU归因未见单次>8ms的慢文件/克隆，但发现大量短操作串联：SessionSupervisor在一次无排队变化的promote中多次做1100文件严格版本发现，pendingInputs又逐输入复制整份work ledger。补充仅以下已有seam收口：

- Coordination提供ownedInputIds批量只读身份集合；Host一次读取用于当前pending过滤，原单input口保留。只表示持久归属，不能当已完成确认；新调用重新读取，执行仍由原prepare核对。
- promote在没有await和写入的同步段共享一次全量计划观察；任何实际prepare await、阻塞/派发持久化后重新发现，不跨这些边界复用。目录仍严格逐文件版本检查，外部改写不漏报，不改缓存过期规则。
- SessionSupervisor的后台恢复阶段在进入过期扫描、持久队列核对和调度观察前在已有async Interface让出一次事件循环；之后仍从当前磁盘事实和lease判断。授权、工具和Evidence提交原子区内不加让出。目的为切断连续微任务中的多轮同步发现，不停用调度或延长原重试间隔。

上述Supervisor新增让出方案在既有测试发现启动恢复/批准冻结和终态队列推进时序回归，已撤回这三处让出，不调整测试等待来掩盖行为变化。保留无await/写入同步段的观察复用和input归属批量读取；原Host/Runner既有async seam的公平调度及lease/dispose守卫继续保留。该失败不记作通过，不将调度语义变更混入性能修复。

本地真实历史第8轮（125秒、871组、native DPR=2，无采样器/凭据/Provider）：输入往返P95/P99/max=33.16/101.28/127.07ms，滚轮27.25/57.55/100.05ms；输入事件到绘制max9.5ms、滚轮max69.5ms、帧max26.4ms，渲染长任务0，主循环max88.34ms。对应RC19前测为输入max1010.27ms、滚轮983.08ms、主循环985.14ms。完整保留中间未收口轮次，不把这些本地离线操作统计写成真实任务、正式包或长期日用通过；候选完整门禁、真实模型和公开包验收另记录。逐轮数值见[安装后停顿复现](../../playbook/v0.1.0/evidence/rc20-installed-history-stall-20261019.json)。

Desktop集成隔离重试仍发现Host额外让出改变目标观察事件入账的可见时序，并增加fallback设置读取。该两处Host让出亦撤回，保留读取批处理/投影与Runner原prepare前的async让出。不能以等待更多时间或放宽settings读取计数来掩盖本次回归。撤回后须重跑集成和本地实际历史性能，前述第8轮数字仅代表当时中间候选。

撤回Host额外让出后的第9轮：125秒841组，输入P95/P99/max=26.33/107.81/137.04ms，滚轮27.74/92.95/107.99ms；输入绘制max9.7ms、滚轮max65.8ms、帧max25.1ms，无渲染长任务，主循环max100.34ms。35项Desktop集成隔离重跑通过。保留约100ms峰值，不声称完全没有峰值；原近1秒重复阻塞在本轮未再出现。第8轮改标中间候选，不能作为最终回归语义通过。

### RC20 首轮真实模型：功能通过，性能未通过，不发布

冻结源码6d672bea，以DeepSeek/max、200项工作及100条已送达回执的生成历史跑完三文件18项原断言、独立上下文复核、宿主签收和正式回复。取消后新回复成功、旧任务未重跑；1879字符正文、5790字符完整工具回执成功，四次46MB持久提交约100–105ms，复制凭据已移除。

但572秒2314组交互测得输入max631ms、主循环max763ms，超过既有500ms上限；滚轮max301ms、绘制max259ms。输入/滚轮P99虽仅26/28ms，仍不得通过。该轮ok=false保留，RC20不打tag。继续使用带操作栈与阶段标记的实际模型诊断，区分持久提交/恢复/请求装配与采样器开销；不放宽门槛，不将功能成功冒充执行流畅。再次根因收口及无采样器同规模复测通过后，才进入产品和公开包门禁。

### 真实提交阶段收口设计（B级）

带阶段标记的真实模型续跑诊断中，append累计约985ms，反复writeFileSync coordination-snapshot.json.tmp单次约12–13ms；一次工作用量/工具/检查点连续提交会叠加此开销。源码全仓检索确认该快照只有writer，没有任何恢复reader；coordination journal reader始终以日志重放及严格版本为真源。补充：停止每次append写这一未被消费的可重建缓存；保留原journal append、文件fsync、目录fsync、lease复核和cache发布顺序，不改日志格式、不合并或丢弃预算/派发/Evidence提交。已有旧快照不删除也不再当当前事实。新增“无快照/伪造旧快照均以当前日志恢复、旧缓存不被重写、丢租约不追加”的测试。若此后仍不满足原峰值门禁，继续归因，不能据累计热点直接宣称通过。

CI界面门禁同时揭示详情兼容遗漏：按需过程读取保留完整rounds后，还必须传递同一workspace响应中的真实Activity。停止时可能有准备中但从未派发、因此未进入持久rounds的步骤；既有attachBotProcesses已经按精确turnId隔离这种Activity，新的读取Module应复用该投影。不得把准备显示成执行/Evidence，不得给历史回复附上另一turn的活动。补充停止/错误及不同turn回归。

Linux的真实pointer hover测试在循环中每50ms移出再移入，反复重置120ms的透明度过渡，导致15秒仍无法满足opacity===1。仅修正测试等待：真实指针命中后等有限CSS过渡完成，再检查hover与opacity；断言、实际指针和虚拟列表命中要求保持，不能强制按钮可见或放宽布局。

### RC20 冷投影共享输入的收口设计（A 级，只读存储 Interface）

48c72109 完整真实任务在功能上再次通过，但输入最大674ms、主循环552ms仍超过原500ms门槛，不发布。新鲜任务第一阶段的采样显示391ms派发窗口、349ms回复交付窗口、334ms定时观察窗口，均由多段同步工作串联；没有发现单次超过40ms的文件/JSON/克隆操作。多个独立投影在同一父会话变化后分别重读并解析同一9.6MB JSONL：消息身份、列表摘要、卡片、父任务事实、聊天分页。原投影输出缓存虽有效，冷输入没有共享。`dispatchOrigin`全文读取仍是遗留候选，但此轮栈未证明它主导，不能据静态代码将其宣称为本次根因。

Conversation Store 增加独立的严格历史输入 Module，在每个 Store 内按会话ID和完整已校验文件版本缓存解析后的只读输入；最多8会话、合计64MiB，不写磁盘。所有投影仍先 describe 索引、正文和sidecar的严格版本，读取后再核对；替换、同长改写、删除、稳定损坏、写入竞争继续走原错误/最多3次重试，不能命中旧成功。

已有 createHistoryProjection 保持默认可变输入的兼容性：回调获得隔离副本。新增显式 immutableInput 选项，仅经核对的纯投影使用深冻结共享输入，且投影输出仍结构化复制隔离。深冻结在首次解析后执行一次；调用者无法污染其他投影。缓存逐出/超限只影响成本，不能截断历史。该输入缓存仅供既有展示/事实投影，getPersistedConversationHistory、权限、Evidence及真正执行读取 Interface 不改，不将缓存当作权限或完成证明。

先补多投影单次正文读取、默认回调污染隔离、不可变回调拒绝写入、侧车/替换/损坏失效、竞争与容量测试，再接入明确纯投影。不得用Host/Supervisor时序让出掩盖重复解析，原被撤回的让出保持撤回。重新运行完整门禁、标准产品回归和同规模无Profiler真实任务，失败峰值保留。

既有 Desktop botHistory 端口也通过 createHistoryProjection 保留完整 canonical messages/rounds，Runner 已经使用这一严格版本缓存。本次共享解析不裁剪该端口、不把列表或卡片摘要传入认知上下文；其输出继续完整复制隔离。getPersistedConversationHistory 的直接读取不接入新缓存，权限/执行命令仍依赖原lease、signal及本地准入，绝不以共享输入证明许可。

### 真实验收捕获的 CSV header 误判（A 级，完成门准入）

ac5e4ea6 的生成历史真实 Node 任务已经完成三文件修复、18项原断言及独立复核，仍被 ui-artifact:judgment-missing 阻止签收。宿主事实确认：唯一成功标准为 command/node --test；Intake 分类仅命中 ui-surface:header、score=2。该词来自 renderCsv 契约中的“输出 header category,count,total”，指CSV字段行，并非界面。主Bot如实提出截图不适用并查询原任务，不能靠这句话解除宿主视觉完成门。这是完整验收揭露的产品误判，不将其当Provider失败，也不修改生成任务描述来绕过。

在原纯分类 Module 中仅补数据字段语境消歧：当唯一正向视觉信号是英文header，且无其他界面表层、渲染层、预览或视觉验收信号时，识别明确CSV/TSV header或CSV/renderCsv行内header后跟逗号分隔字段名的语句。其他header及混合界面任务保持原判定；不新增模型自报的“免视觉”标志，不改变Evidence、视觉判断或权限执行链。先补真实契约复现、CSV字段行、真实页眉、CSV界面组件/配色和混合交付回归，再改分类。

已持久化武装的视觉门不由本补丁自动撤销；这轮失败保留，新鲜完整任务重新验证。若未来要纠正旧误判，必须另以明确的宿主事实/决策路径设计，不能复用此次文本分类悄悄删除已武装门。

本次新增Intake误判修复先经过46项分类/视觉完成门定向检查及构建/集成，再运行同规模新鲜真实任务确认阻断和峰值；候选冻结后重新完整产品capture/逐图自审/verify，仍须全部门禁通过才能发布。该顺序调整避免在已知功能阻断尚未收敛时反复生成视觉包，不删减任何最终验收范围。


### CSV 消歧后的完整真实任务仍未过性能门槛

冻结f7b67b0a的新鲜DeepSeek/max任务已通过三文件修复、18项未修改断言、独立上下文复核、宿主签收、正式回复、四次46MB提交、主动取消后回复和5790字符完整回执。405秒1618组交互，输入P95/P99/max=24.47/49.85/273.27ms，滚轮27.36/35.64/574.63ms，主循环max734.53ms；Renderer帧max25.2ms、long task 0。功能阻断已消失，但峰值再次失败，仍不打tag或发布。

继续以完整新鲜流程采样并记录Profiler.start/stop前后的performance.now时钟边界、各阶段标记与主循环间隙；先前hrtime与CPU profile时基不同，不得据错误对齐归因。诊断运行只作调用栈归因，最终门禁仍用无Profiler同规模真实任务。保留原500ms上限，不对失败阶段省略采样。

### 完整阶段 CPU 采样后的写入与派发收口（A 级，内部存储 Interface）

f7b67b0a完整诊断在派出取消验收任务时测得552ms间隙；工具准入窗口约372ms，其中beforeTool约206ms。以独立12ms命名时钟标记校准CPU样本，避免Profiler启动约52ms区间的不确定性。栈确认：工作记账append先复制全量ledger，committed再复制一次；Verifier continuation单项归属检查仍read完整ledger；Activity为幂等判断和被忽略的append返回值读取父对话全文。首次派发还出现GoalRunnerHost.currentPlans加载全部1100份计划约53ms，调度器实际只用delegationOrigin项目与session依赖。未据静态代码认定dispatchOrigin全文扫描是本轮热点。

补充以下Interface，先写失败回归再实现：

1. Coordination Journal Reader增加内部commitEntry：严格读取当前版本、用原Reducer构造下一状态，调用原同步persist回调，原append/fsync/目录fsync全部成功后才发布私有状态。内部构造的next不向调用方泄漏；既有committed/read与默认append/saveWork仍返回隔离副本。新增显式returnState:false仅供忽略返回值的宿主记账调用，避免复制其他历史work；失败不发布，重试仍严格重放已落盘记录。没有合并、丢弃、延迟预算/PermissionGrant/Evidence记录，没有跨await写入缓存。Verifier单work检查用readWork；binding核对用已有readLifecycleFacts，仍检查当前mandate/transition和lease。
2. Activity发布器使用已有严格版本投影取得消息ID，旧Store无工厂时保持全文兼容；append显式returnMessages:false，事件持久化后再发changed。不能把内存去重当持久化、吞掉写失败或把Activity当Evidence。Coordination在一次无await的决策内只读一次同一父消息集；原当前用户、附件、锚点和作用域判断不变。
3. GoalRunnerHost的调度观察复用已有DelegatedPlanCatalog，只对具有delegationOrigin的候选getPlan，保留已接受依赖、终态、同长度改写/替换/损坏失效及原getPlan完成门。非委托Goal仍走原canRunPlan路径；实际能力、执行权和当前宿主租约不缓存。

不扩展为修改父上下文继承或降低签收条件；createChildConversation的当前完整背景和版本复核先保持。原被撤回的Host/Supervisor调度让出继续撤回。上述收口后重新完整受影响包测试、同规模无Profiler真实流程及冻结候选产品回归，所有峰值失败保留。


上述写入/派发收口冻结为70e00f13：完整build、typecheck、architecture、release-readiness通过；64项定向检查通过。Runtime全包1355项中1353通过、2项输入抢占时序在并行负载下失败，对应两文件隔离35项全通过，未改断言。Desktop5579通过、5项原有skip及3项附加检查通过。私有next不通过persist泄漏；Reducer中transition patch也复制其嵌套handoff，补齐输入/输出污染、写前失败、写入后确认失败的重放，以及单work取消复核测试。无Profiler新鲜完整模型任务另测，尚不声称性能通过。

### 调度观察的只读完整快照（A 级，原状态的不可变 Interface）

70e00f13无Profiler新鲜流程仍全功能通过；1196组交互输入max530.56ms（dispatch523.88ms）、滚轮253.56ms、主循环419.17ms，原峰值门槛仍失败，不发布。完整阶段采样已证明recoverySelection/custody/送达恢复继续多次read整份ledger，产生短克隆与GC放大；仅消除写入两次复制没有清除观察链的复制。

Journal Reader增加显式readSnapshot Interface：每次仍执行原readState严格文件版本检查，返回完整canonical state的深冻结快照，不截字段、不提供许可或签收结论。未变化时可以共享该不可变对象；落盘并发布的新revision得到新快照；旧快照保持旧值。默认read仍返回可变隔离副本，readWork仍返回单项隔离副本。冻结在冷回放成功或持久提交发布时执行一次，仅遍历新的对象，跳过已冻结子树；Reducer始终copy-on-write，不可修改旧state或保留可变entry别名。

仅RunnerCoordination、ContinuationCustody和ReplyDelivery经逐项审查的只读观察消费此端口，旧Adapter缺省继续read。它们原有await/写入后的重新读取、prepare、lease/版本/取消/未知执行守卫保持；不能把过去快照跨操作当最新事实。命令和PermissionGrant/Evidence提交不新增缓存真源。先测试深层写入拒绝、默认copy隔离、外部append/替换/损坏失效、旧快照稳定及相关消费者完整恢复/取消，再完整回归及新鲜真实任务；不以放宽530ms门槛收尾。

同一只读观察审查还包括recoverLegacyBudgetWorks和VerificationDispatchRecovery的候选筛选；真正候选继续readWork/当前lease及原记录提交。既有pendingEvents内部可消费快照，但返回仍复制实际事件数组，保留可变副本兼容，不能将冻结引用意外传给旧消费者。新增取消/核验/旧预算/continuation/送达完整测试共同保护这些范围。


完整不可变快照收口冻结391d0cfa：47项相关定向检查及全build/typecheck/architecture/readiness通过；Runtime1357中1356通过、1项并行输入抢占时序失败，原文件隔离7项通过；Desktop5579通过、原有5skip及3项附加检查通过。原调度计数仍严格要求4次准备/决策观察，新增不可变端口、旧Adapter回退与0次整账本副本检查。送达回调和pendingEvents保持可变副本，不能让冻结引用泄漏改变旧回调契约。最终无Profiler新鲜模型流程仍在进行，未发布。

### Markdown 数据表头的真实反例

391d0cfa的新鲜任务再次被相同视觉门阻断：实际goal为`renderCsv(groups)…输出以 header \`category,count,total\` 开头`，原46项回归只覆盖未包裹字段行，withoutDataHeaders的lookahead未接受反引号。18项原断言与独立复核已通过，主Bot读取详情并在原任务继续核对，宿主仍不能凭其“written skip”解除已武装门。该轮不记完整成功，不删除门、不修改夹具措辞。

只在已有“唯一视觉线索为header、明确CSV/TSV语境、无其他UI/renderer/preview/visual线索”的窄分支补字段列表的引号/Markdown分隔符及冒号/等号写法；实际页面header、CSV界面组件和混合UI仍保留。先补本轮实际完整契约及带反引号/单双引号字段行、真实界面反例，再改纯分类；已武装的旧计划继续保留失败。最终新鲜完整任务必须真正签收，不能靠局部指标收尾。

格式消歧以同一逻辑段落内的CSV契约为边界，允许普通换行和代码分隔符包裹字段列表；不把另一段落的CSV提及扩散成全目标豁免。独立段落中的真实header，以及任何额外UI线索，继续保留完成门。

### 通知身份查询的读取放大（B 级，既有档案 Adapter）

c207f2d0首次完整新鲜模型流程已通过全部功能阶段：18项原断言、独立复核/宿主签收、正式回复、四次大提交、主动取消后回复和5790字符回执；519秒2093组交互仍测得输入max588.79ms、主循环544.74ms，因此不发布。随后的120秒带时钟校准续跑诊断只针对后半段（非完整新鲜验收），捕获取消派发473ms、取消回复305ms、长回执267ms窗口。

栈确认通知handleAppended → botNameForWorkspace → Desktop.botName → directory.get → projectRow约35–40ms，且同一回复阶段多次发生；它只需要profile.displayName，却读取完整消息、任务、审批和未读状态，引发多次冷历史投影。改为直接消费同一dataRoot上已有BotProfileStore.read，并保留workspaceId校验、缺失/损坏/归档返回空串、最新displayName语义。无需新增缓存、IPC、存储或Module，不改通知决策、去重、前台抑制及权限/Evidence。

先补真实Desktop装配用例：聊天损坏仍可取得档案名字、外部改名立即生效、归档/删除/非法身份仍空；再替换这一名称Adapter。父背景的完整继承和版本核对在本步保持，未据此放宽完成门。随后重跑同规模无Profiler完整流程，保留本轮失败，不用短诊断的477ms主循环冒充通过。

通知名称Adapter冻结9d7eda60：真实Desktop装配用例旧实现失败、新实现通过；完整Desktop5580通过、原有5skip及附加3通过，完整构建/类型/架构/提交后readiness通过。Runtime源码未变，保留c207全包1356通过及一项时序文件隔离7通过记录。正以相同生成历史和原18断言重新启动无Profiler新鲜完整真实流程，不将尚未结束的运行算通过。
