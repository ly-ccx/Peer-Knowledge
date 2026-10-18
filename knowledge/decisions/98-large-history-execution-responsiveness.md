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
