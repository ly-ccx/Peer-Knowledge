# 本地运行时隔离：详细设计与自上而下审查回执

创建时间：2026-11-11
最后更新：2026-11-11
状态：详细设计候选已完成实现者自审；ADR128仍为Proposed。没有独立审查者、没有生产重构或产品验收结论。

审查对象：[总体设计](../architecture/local-agent-system-blueprint.md)、[ADR128](../decisions/128-local-runtime-isolation-and-bounded-query-contract.md)、[详细设计v1](../specifications/runtime-isolation/README.md)、[实施包](../../playbook/runtime-isolation-implementation.md)。用户要求先一次补齐接口、数据、依赖、队列和异常恢复，再自上而下审查，不在实现时临时决定。

## 1. 候选身份、范围与依据

- 产品源码基线：`b05b7afbf26b43444635f77710397c3a658d6a0f`，`release/v0.1.0-rc.41`；本轮没有产品源码修改。
- 知识分支：`codex/local-runtime-isolation-architecture`，本轮基于`bd5f58f73351c1ecbfe22fa7511fe570351bb7c4`继续补齐；本回执不把父提交当成本轮最终候选。最终提交见PR；[内容核对收据](../../playbook/evidence/runtime-isolation-detailed-design-20261111.json)绑定本轮文件摘要与源码目录指纹。
- 现行ADR pass：先读`00-adr-map.md`；核对85、96、98、101、102、`104-progressive-interaction-and-coordination-storage.md`、112、115、116、120、121、126、127及当前128；保留113/123未接受部分，不借本设计授权CAS、GC或情节记忆。
- 详细设计为15个核心M Module、11个已有Feature owner、21种View、14条队列、411项现有IPC路由；F编号是已有服务责任，不创建一个总FeatureService。
- 该变化为A-level：新增命令交付权威日志、计算许可、异步提交与平台上下文，收紧两项Renderer生产权，修订头像返回与重启输入交接。已先写入ADR128和map。模型能力、Grant含义、Evidence、System Context层序不变。

原现场证据仍以[调查](desktop-runtime-responsiveness-architecture-audit.md)和[可行性记录](../../playbook/evidence/runtime-isolation-feasibility-20261111.json)为准：存在周期性查询放大，隔离实验说明main可避开该段CPU；原日志最大3949ms尚未归因。它们不能证明新架构已经实现、所有尖峰已解释或当前应用已修复。

## 2. 自上而下的审查方法

第一轮从产品北极星和五条分工推导系统责任，再核对逻辑Module、caller知道的Interface、事实owner、依赖/反馈、部署与有界资源。只增加Locality或Leverage的seam；没有把文件/进程分离当作解耦证明。

第二轮逐条走正常输入—认知—能力—核验—交付、展示读取、负载下取消、崩溃恢复—后续准入，并覆盖拒绝、失败、超时、断线、迟到、换代与旧数据。每条都回到原身份/源版本/耐久回执，检查是否存在凭文本、定时器或缓存制造成功的分叉。

第三轮将实际411项catalog逐项核对目标Module/contract与原窗口权限，并回读关键生产handler；检查非session任务、自动化定义/运行、attention、计数、pending input、预测、窗口表达与秘密是否被误归类。最后做文件链接、ID/数量、源指纹、路由和差异的一致性检查。下面保留发现及修订，不只给一个“通过”。

这是同一实现者的设计自审，既无独立审查也无多agent审查；内容检查不替代真实Module/Host验证。

## 3. 发现、修订与设计收口

| ID | 审查发现 / 风险 | 已固定的设计与位置 |
|---|---|---|
| R01 | 只画Runtime/Query进程会把原God Module整体搬家 | 02逐个给15个M的Interface、owner、依赖、队列、顺序与恢复；11个F分别拥有已有功能；M14只装配生命周期 |
| R02 | 一张文件/依赖图无法证明实际读取无环 | 02明确ReportSource不回M11，M12不依赖执行实现；委派合法反馈经typed命令/持久事件，不持锁递归等待；D08检查真实调用 |
| R03 | 运输ack、领域提交、工具成功、核验签收混在一起 | 01/05的accepted仅journal fsync；domainRefs保留原事实；dispatching崩溃先查原dispatch，unknown不自动重放 |
| R04 | 重连换connection会绕过命令幂等 | 01稳定actor与连接/窗口身份分离；pending CommandKey保留，同principal/scope重新认证后lookup原operation；不同digest拒绝 |
| R05 | 全部旧API套成万能RPC会重建未治理边界 | 冻结411个schema-bound精确方法；原typed参数/结果/角色与目标Module分列；未知方法/字段拒绝；内部wire另列私有ACL |
| R06 | 客户端直调Repository会令存储拥有业务规则 | 01/02取消客户端M13路由；Feature owner和M02–M11构造私有typed操作；M13只保证耐久/锁/CAS/fence |
| R07 | 空grant仍hydrate全部session/Evidence；badge反复全读 | 03空结果零hydrate、按Evidence键索引、attention_counts聚合；21个View各有字段/排序/分页/字节界限；D05做原规模与十倍无关历史 |
| R08 | task_heads/session.report单一session键遗漏普通Plan/自动化/后台任务 | 03主键改为taskKind/taskId；report为targetKind/targetId/source；任务不伪造sessionId；conversation.list只取meta |
| R09 | automation定义、attention、审批计数被塞进任务/报告；权限规则成了task | 新增automation.page、attention.page、tasks.counts、pendingInput.peek；approval/obligation、resource recordKind与settings section显式区分；路由清单给selector |
| R10 | read/mark-read与诊断可能偷偷写入passed或推进状态 | M12零canonical写；F09拥有读游标；旧TaskOverview补passed行为删除，缺核验保留未验证；诊断不能repair/reconcile |
| R11 | SourceVector没覆盖Evidence/usage/claim等独立变更 | 03列完整source kind，Control属于coordination、context有原epoch；超过32项存完整snapshot；不拿plan版本冒充独立库版本 |
| R12 | TTL/mtime或旧live连接被当成当前执行真值 | selected实体强版本前后校验；raw write发现窗口明确observed；live owner snapshot超时/断线只是unknown；执行始终再查canonical |
| R13 | 无容量的worker/队列把卡顿转移或抢占取消 | 04固定14条队列及字节、保留通道、调度/期限/溢出/释放；QS两个Store进程；QR同根共享4许可，纯job停滞与exit证明固定 |
| R14 | “设备并发”实际只有每进程计数，或跨根全机上限没有实现者 | QT/QX明示每Runtime运输上限；原M05管理跨宿主业务claim。QR同数据根跨宿主共享，不虚构跨独立根全机daemon/硬上限 |
| R15 | Node heap上限被说成总内存上限；Bun线程无法提供同样限制 | 06固定Node192MiB heap、Bun独立worker RSS320MiB/100ms采样；承认采样间超额；不支持即平台候选失败，无main同步回退 |
| R16 | 大JSON在worker仍一次读成巨字符串；prepare取消等于半提交丢失 | 05流式tokenizer跨UTF-8/转义/嵌套且完整结构校验，保留原格式；prepare可取消、commit后lookup；过大必要context返回具体阻塞，不删历史 |
| R17 | 原UI resize/ack/reattach和每次预测都进永久业务journal | 01精确分离presentation-request、client-state、transient-request；四类envelope不变。quick-chat提交仍进M02，表达反馈不授予任务事实 |
| R18 | “draft绝不进模型”与Accepted ADR115续写合同冲突 | M00保存不等于正式输入；F11按原显式启用/选模型的预测profile准入draft，空工具面、不启AgentTurn、不持久化候选/草稿trace；每宿主最多1预测且无过期队列 |
| R19 | ModelAdapter拿凭据被迫伪造ToolGrant/AgentTask | 06区分CapabilityInvocationTicket与CredentialRequestTicket；后者绑定原attempt或prediction/completion/catalogAuth身份，专用私有端口，不创造工具/批准事实 |
| R20 | Broker ticket只有旧签名，等待Runtime回调可能死锁 | Broker5s一次nonce、私有HMAC与当前准入检查；专用保留control port不等待AgentTurn/锁。取消后已发生效果按原句柄/receipt收口 |
| R21 | 明文/secret digest进journal，或重连换secretRef破坏幂等 | Broker32项/1MiB/60s staging；01固定Provider/MCP/Vault/导入器的原敏感对象变换与宽Record字段收紧，journal只存opaque ref。失效先查dispatch，确证未派发才拒绝并新operation补输入；unknown只对账 |
| R22 | 失去lease后拒绝一切旧结果会丢真实Evidence；允许旧writer则会推进新任务 | 05分StateTransition和HistoricalObservation；后者只追加原durable dispatch的不可变事实，无Plan/Grant/Control/acceptance/claim释放权 |
| R23 | floor13或新manifest被当作能围栏任何旧程序 | 05先drain/静止已知旧writer、取得原lease/fence再cutover；不支持新floor的classic/外部writer必须先静止；回滚不降低floor，冲突给具体blocker |
| R24 | pendingTask的consume先删，重启/跨workspace/坏文件可能丢输入或重发未知 | M02 stage/claim/finish/discard；claim不删，匹配原InputReceipt后CAS清除；旧unknown不重发，坏/跨workspace保留诊断；交接step不成为第二输入真源 |
| R25 | ≤1MiB头像单帧与256KiB协议响应冲突 | 03保留原PNG/JPEG/WebP/≤1MiB，scope/source绑定assetRef，180KiB原字节chunk和≤256KiB帧，客户端收齐后data URL；ADR128明确拟修订85决策12 |
| R26 | 原Renderer usage与client-tool投递角色跟着旧清单进入新Host | 原角色作为快照保留，targetRolePolicy另列两项收紧；usage仅原Provider producer，工具投递仅受信Gateway/Runtime；不扩大模型/Grant政策 |

上述“收口”指设计已固定，不能在实现时从多个方案中任选；不表示这些行为的代码已经成立。若后续源码/平台事实推翻某合同，必须修订本规格和ADR，再据新候选验证。

## 4. 每条链路的闭环

| 链路 | 接收/事实owner | 队列/耐久点 | 异常后的出口 |
|---|---|---|---|
| 用户输入到正式交付 | M01接收；M02输入/责任；M06回合；M09工具；M11核验签收 | QA/QW/QT/QX/QS；journal、原inputId/dispatch、terminal、verdict/acceptance依次提交 | lookup原operation→owner恢复；unknown对账；旧结果只归原历史；缺核验保持缺口 |
| 冷索引与打开页面 | M12派生；原ReadRepository提供source | QQ/QP/QR/QE；只发布已核对source的generation | rebuilding/damaged/version_changed；该源独立重建；保留锚点，不回main全文计算 |
| 满负载中的批准与停止 | M10批准；M04屏障；M05资源保护 | 独立QC/控制Store；原ControlOperation/StopReceipt | 未停稳reconciling/unknown；磁盘满仅尽力中断及关闭新准入，不回stopped |
| Runtime/平台/Store失联 | 各领域恢复；M14只排依赖 | 原lease/fence/recorder及step/dispatch；Store历史观察独立 | 查真实worker/handle exit；未知不重放、不释放新claim；有限重启，后续任务按原scope评估 |
| 重启待发送与预测 | M02交接；F11建议；M00草稿 | pending文件/原input receipt；预测仅短期内存/QT许可 | claim后崩溃查原inputId；预测过时取消且仍计已消费usage；不把候选当输入 |
| 切换与回滚 | M14迁移回执；原领域owner | prepared→fenced→cutover→verified，阻塞留blocked | 旧writer不明则该项目不切换；高floor不回退写；原格式/历史/Evidence保留 |

每条权威写路径都能回到领域owner与原提交身份；每个展示/连接路径都只拥有表达或派生状态。没有用Query可见性代替授权，没有用timer退出代替执行结束，也没有用缓存重建代替权威恢复。

## 5. 内容核对与尚未运行的验证

[机器可读收据](../../playbook/evidence/runtime-isolation-detailed-design-20261111.json)只记录文档与catalog一致性检查：本地链接、围栏、无机器绝对路径、M/F/View/Q数量、411个源条目/原owner/transport/窗口策略/指纹、目标模块/读写归属、两项角色收紧、21种View与selector、diff空白检查。它不执行产品代码或证明任一D用例通过。

首轮内容检查发现52项event有原payload合同描述，但未列显式schemaBinding；该轮失败及当时文件摘要保留在收据priorAttempts。已补齐每项closed event enum、原subscriber合同、canonical/presentation/activity envelope与原audience，再用相同检查重跑，不放宽断言。

真实Module/Store/Host/schema验证、队列满与磁盘故障、历史unknown/partial恢复、真实模型、十分钟原生交互、IME/焦点、签名安装包和Windows/Linux/macOS实际桥接，均为[07的D01–D18](../specifications/runtime-isolation/07-migration-and-verification.md)的后续实施门。尚未运行，不用一次有限隔离实验或本次自审代替。原3949ms峰值仍未解释，不能称“全部卡顿已修复”。

本轮仅知识文件变化，执行内容/差异/一致性审查；按仓库Validation Scope不跑代码测试、构建或产品回归。没有安装、发布、重启应用或修改个人任务。

## 6. 设计就绪判断

本候选的职责、接口、事实归属、依赖、队列、存储提交、异常恢复、平台与迁移方案在设计层已完成自审，R01–R26已落实到规格，没有保留“实现时任选”的架构分叉。固定参数是待验证设计值；原接口保留的具体业务类型按冻结源码的Protocol/preload/owner合同引用，不重新发明一套业务schema。

ADR128保持Proposed，PR保持draft；设计自审不是用户接受、独立审查或运行验收。产品重构尚未开始。下一阶段应以这份固定合同和RI-00原失败基线为入口，按阶段证据推进，不能再把临时性能补丁称为整体方案落地。
