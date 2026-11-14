# RI-00：取证策略复审与单进程现场首见证方案

创建时间：2026-11-14
最后更新：2026-11-14
状态：封存审计完成；FR1为待实现、待执行的设计，runnable=false。本轮不采样、不重构。

## 结论先于新实验

多轮失败不能概括成“都是F0没通过”，也不能概括成“都是采样器开销”。[本轮审计](../../playbook/evidence/runtime-isolation-ri00-evidence-strategy-audit-20261114.json)重新绑定11份封存收据与当前控制器源码，确认了四类不同问题：已知工具缺陷、不能稳定通过的性能对照、现场采集依赖前述对照的准入循环，以及过去现场观察的覆盖缺口。底层VM/工作量为何变化仍未定因；本报告查清的是取证失败的结构和可观察来源，不把它写成用户卡顿根因。

以往把“先证明测量程序稳定”放在“先保存自然变化”之前，逐步转成了独立的资格研究。应停止继续猜一个操作因素、开三个宿主、要求两边暖段和返回均稳定、失败后再猜下一因素的循环。保留原15ms/2ms门和所有旧结果；新现场记录入口与旧性能资格分开，不以记录成功授予性能或重构资格。

C级诊断设计，读过`00-adr-map.md`、Accepted `96-task-execution-responsiveness.md`及Proposed `128-local-runtime-isolation-and-bounded-query-contract.md`。不修改产品Module/权限/Evidence/System Context边界。这里修订未来诊断的**采集准入**提案，不修改旧F0/G2算法，不把自然指标冒充旧密集指标，原RI-00机制与重构门继续保留。

## 逐轮失效审计

| 轮次 | 封存事实 | 为什么未给出有效归因 |
| --- | --- | --- |
| C1现场长观察 | 109.55分钟；heap/space getter会释放线性分配区，code getter还可进入sweeping等路径 | 已知观察干预存在；小自计CPU不能证明VM状态中立。该作用不是30–40ms根因证据 |
| H读取顺序 | 六target均有F0暖段失败，实际顺序处理0次 | 没有进行待检验处理；不能称六例机制负例 |
| K归档粒度 | 8检查点仅2个当前暖段控制合格，固定改善+3.360/−3.021ms，B未形成合格快点对 | 不满足预定充分原因；不能抽绿色B用作现场资格，也不能推广成该因素在所有状态无影响 |
| N逐遍PMC | 边界/计数结构通过，两个target均有ON/OFF中位差及暖段失败 | 同GC计数仍可有不同VM工作；整根、逐遍和探针状态效应不能用结构正确相互替代 |
| C/D传输 | Promise collected、调试等待和trace cap导致原失败；后续E/M正常/取消及实际零读装配通过 | 这些是已定位的工具故障，不能继续当作后续所有对照漂移的解释；E/M也不代表现场性能通过 |
| P/P2 Profiler | 原P因返回预算拒绝而未启Profiler；P2一target未入ON，另一完成OFF→ON→OFF但返回−2.1535ms及暖段失败 | 原P属于资源模型拒绝；P2不能用+0.54025ms公式值宣称低干扰中立。二者不是同一故障 |
| CAD 150/0 | 两个F0均armed，完整固定处理已执行；6处处理暖段失败，A归一化返回−2.622/+4.594ms | 即使进入处理，参考和目标的状态仍漂移；F0一次通过不保证后续平稳 |
| ORDER完整块顺序 | 84根、6块中5处暖段失败，两target均拒绝，处理0格 | 没有执行顺序因子，不能给顺序假设阴性结论 |
| HASH校准排布 | 184根/57native/位置与间隔通过，8个raw域/arm返回中3个超2ms，另3个归一化返回超门；A两块未复现旧坏基线 | 参考独立漂移、实际工作不同，且坏基线本身未全复现；不是排布的有效支持或反证 |
| C2现场长观察 | 128.95059分钟、129自然包络，观察到的入口类别只有ipc-obligation-grants；只有8/12位置进入旧指纹 | 不是整个应用所有操作的覆盖。后续全12遍封存重放仍0信号，heldout最大只+7.511ms，因此不能声称旧算法已漏掉一个实际30–40ms事件 |

表中轮次不是独立随机样本，不计算“失败率”或伪显著性。部分性能失败由采样状态改变也可能发生，但旧数据没有把该因果拆开；不能用“参考波动”给它们指定核频、GC、缓存或JIT的唯一原因。

审计首轮还保留了一次离线聚合断言失败：K的status=armed有3次，但其中一次保留旧armed状态、当前reason为unmatched_gc_state_or_unstable_warm且极差16.182ms。按当前summaries/compatibility/validation/calibration重算才是2次合格暖段。不是原gate误放行；原qualified函数还检查当前门。新报告不以phase/status或tests passed代替本次事实资格。

## 最新返回的实质来源

从原中位联合锚点重放，不重选点。八个raw比较（两个target×两个arm×目标/条件）前后锚点的完整root+12遍GC计数签名全部不同，整根指令变化−1.17884%～+0.44148%；“同名查询、同调用数”不等于相同实际工作/状态。这不证明GC差异是唯一原因，不能按它扣成本或追认门。

| 原返回 | Evidence用户差ms | Evidence内核差ms | 余部用户差ms | 整根用户差ms | 整根指令变化% |
| --- | --- | --- | --- | --- | --- |
| target1/A，条件宿主 | −9.721 | +2.197 | +2.579 | −7.142 | −1.17884 |
| target1/B，目标宿主 | −8.867 | +0.304 | +8.170 | −0.697 | +0.44148 |
| target2/B，条件宿主 | +3.645 | +0.082 | −2.262 | +1.383 | −0.74361 |

target1/B的Evidence下降几乎被余部上升抵消，不能直接宣布整个查询变快；target1/A条件宿主是真实独立下降，不能拿它当稳定的扣除项；target2/B的用户变化与指令方向相反，也不能统一归为新增指令。全部8组用户/内核/合计、逐遍锚点与余部算术闭合，原始数值保留于审计收据。

这解释了旧对照为什么不能完成归因：它要求未获证明的状态平稳和可抵消参考，又把多种成本位置混成单一Evidence标量。ABBA/BAAB可以平衡部分顺序，不能使独立堆/GC/JIT/闲置历史恢复，更不能修复非线性、跨窗的状态变化。2ms/15ms门没有据此失效；失效的是把当前设计当成一定能提供合格反事实的假设。

## FR1：直接保存同一进程的自然变化

[机器方案及预算](../../playbook/evidence/runtime-isolation-ri00-field-first-witness-plan-20261114.json)固定一份现有Peer进程身份，零参照、零SHA热机、零主动业务查询，不再以H、F0、F1通过作为保存现场的条件。没有周期夹测，没有旧8根预热，没有heap/space/code统计、堆快照、强制GC、新native库、VM或功耗设置改变。选择现有进程，禁止为了得到快态重启；若入场已经慢，只记录入场异常。

本轮只是方案。原C1+C2活动已接近4小时，旧接续预算不足；新30分钟是独立新增的预算提案，不挪旧余额，不把本次设计视为已获执行许可。未来执行前仍须当前安装产物、实际入口/owner及同候选装配核对，不能复用M的历史对象身份。需要未来启动级观测时另定范围，本方案不给自动重启或新启动采样额度。

### 常开且不丢前缀的记录

记录从attach安装完成的第一条事件开始，包含基线前、失败、未完成和所有GC类型的根；不再丢初始10根或只留“兼容位置”。实际业务仍按自己的调度运行。仅自然方法调用触发记录，诊断Controller没有request业务接口。

每条记录包含PID+OS birth、编译/观察器SHA与generation、单调seq、实际入口/同步root/12遍span和parent ID、root用户/内核/合计CPU及wall、12遍对应CPU及原观察GC、root减Evidence的余部、plan/index顺序和计数、scope摘要、输入/输出/查询依赖代次。CPU只赋给连续同步root/span；异步入口只记wall和父链，不能把跨await的线程CPU差都记成该IPC消耗。父子inclusive成本不重复相加。

主指标同时看心跳延迟、整个同步查询CPU/wall和Evidence十二遍，不能仅凭Evidence波动代替整应用卡顿。root未变、Evidence升且余部降的事件标为成本位置变化，不能算整查询慢化。首轮不注入被N拒绝的逐遍PMC库；指令层仍缺失就写缺失，不补0。

入口和每个Evidence调用当时捕获有界同步栈，ALS记录已映射入口的真实异步parent，按seq保存，不拿first-kind缓存栈冒充后来调用。96帧/32KiB、父链128层、256签名/8MiB字典；截断、未映射caller或父链缺失使chainIncomplete，禁止用相近时间补父子。原实际链中已知的IPC/Directory→Supervisor→humanGateOf→acceptanceFacts/indexedRefs→readEvidenceIndex只是应核对的路径，不能把这串名字硬填给每次事件；代码/索引与source map SHA绑定到实际产物。

控制器只追加hash链式元数据块、先fsync后ACK，磁盘从安装到触发的**全前缀**一直保留。内存只作未ACK缓冲；不把最近几十秒ring称为完整前史，也不覆盖未ACK原件。保留读取、通知、序列化、源归档、Profiler和native sample的全部诊断边界。attach以前、旧C1/C2空窗、出生时的JIT/分配状态不可追溯，明确为缺口；这里的完整指已观察前缀无丢失，不承诺VM逐指令重放。

输入身份按实际查询依赖归代次，不因无关项目写入而重置全部历史。优先用已有Store revision和原读取所绑定文件身份；去重路径/源身份由外部Source Adapter核验，不能每30秒全树扫描或在main散列68MB。源watch只作失效提示，不当逐写入的完整内容凭证。最多一份一致只读源归档在前置阶段取得，明确记录它会影响文件缓存；安装后不再重复归档/热机。未能证明的依赖标identityIncomplete，仍保存异常，但不作“同输入机制”结论。源变更保留旧代次并分新cohort，不跨代次比较或追绿；超过4个cohort结束可比性采集。

### 可执行的触发与前后段

1. 按entry/root kind、scope、查询图和已核对输入/输出/依赖代次建立cohort，前9个完整自然根按时间入基线；不按耗时、GC、heap或某个漂亮子组筛选。固定中位B和MAD，保留每个原根/离散度，后面不滚动重学。该自然基线不是旧G2合格快态；入场异常不能倒填前史。
2. 第一条满足root用户CPU或全12遍Evidence用户CPU相对B同时增加≥12ms、≥4%、≥3×MAD的自然根产生CPU候选。无可比基线也记录自然root wall≥1000ms；主线程250ms诊断心跳缺失≥1000ms由外部watchdog即时触发。心跳缺失也可能来自调度或传输，只是信号，必须结合当时线程状态判别。
3. 候选先封存全部前史。CPU候选之后，保持无Profiler，最多120秒只看最先出现的3个同cohort完整自然根；不发起查询、不筛GC、不额外补第4个。3根root用户CPU均相对B增加≥25ms且≥8%，才标whole-query-change-candidate；仅Evidence达标而root不达则标redistribution-candidate。缺3根、未持续或身份不完整分别记录，不追样本、不宣称原密集残差已复现。
4. 这些是候选分类，不是统计因果检验或旧G2确认。自然基线离散度和GC签名始终显示；首次安装后无低成本前史、数据变化、已存在的慢态都不能叫已捕获原快态形成。是否是原430/500ms与30–40ms问题，须在后续指标桥接中单独证明。
5. 最多一个CPU episode、一个wall/heartbeat episode；同一在途事件合并理由，不排队业务查询。所有捕获不论阳性/阴性/不完整都消费额度。CPU假警报后不能换一批根重试。

### 调用链与取栈，明确不可倒录的部分

逻辑caller和父链在自然调用时已经记录，解决原来“事件发生后才找顶层栈”的顺序问题。心跳watchdog在主线程尚堵塞时，最多一次外部`sample`，2秒、1ms间隔，独立5秒硬截止；只可终止自有sampler，不终止Peer。已有原生sample曾无法符号化V8 JIT，因此未知地址继续记未知，不能用它冒充JS业务热点。native采样也有观察影响：与采样重叠的root/span标sampler-overlap，只能保留采样开始前已出现的堵塞事实，不能把采样后的尾段称为未干预计时；若最先3个自然后续根被它污染，也不另挑3根追绿。

只有第一条异常及其3个无Profiler自然后续根已封存，才准入最多一次500µs V8 profile：等待下一个自然入口最多30秒，窗口最多10秒、输出16MiB；没有业务就停止，绝不主动读来填profile。Profiler前后是不同观察阶段，所有后续计时标profiled，不进入前面的自然变化判定。API边界参考与实测Electron Node24.15.0对应的[官方Inspector文档](https://nodejs.org/download/release/v24.15.0/docs/api/inspector.html#cpu-profiler)，但实际安装Electron的开始/停止、时钟、超时和恢复仍须功能验证。

**首次慢根已经结束的CPU热点不能补录。**上述profile只可说明仍慢或再现时执行了什么，不可倒填第一次慢化热点；捕不到重复就明确hotspotMissing。逻辑父链完整也不等于已解释额外CPU。映射宽度>2ms或某遍确定样本<10，不给逐遍热点结论；采样self time不精确拼成30ms。Profiler应答未知不重启追绿，沿原有stop/disable/disconnect恢复；无法证实停干净则封存unverified。

## 覆盖、预算与停止

新方案限定30分钟，短于旧单次129分钟；关键变化是零主动读、全量逻辑前史、同进程raw指标及堵塞尚未返回时的外部watchdog，不是单纯延长等待。

第一10分钟内须观察到前台交付状态、至少两类真实已映射入口及可比cohort基线。焦点不证明用户操作，记录只称foreground-delivery；没有来源证据的后台轮询不冒充点击。如果仍只有一种后台轮询或没有可比基线，按coverage-insufficient结束，不续时或让用户反复制造动作。已捕获异常原件仍保留，覆盖不足只限制解释范围。窗口到期无事件只可写“这些已覆盖条件下未观察到”，不能写机制被排除。

| 资源 | 新提案硬准入/停止边界 |
| --- | --- |
| 正式现场 | 1个现有Peer，30分钟含90秒清理；0参照、0启动/重启、0新增业务查询、0 native SHA |
| 前置准备 | 最多3分钟，含unit≤30秒、一固定owned功能Electron≤60秒、源归档≤30秒、binding≤30秒、收据≤30秒；总活动33分钟，不把开发/分析空窗拼成连续现场 |
| 唯一功能槽 | 1 owned Electron，≤12次原自然入口调用，读CPU≤8秒、完整进程CPU≤12秒，无替换；只验证透明性/归档/触发/恢复，不验证性能中立或产品原因 |
| main诊断 | probe自计CPU≤3秒，单root自计≤2ms；诊断RPC整窗CPU上界另计≤5秒，可能含普通业务，不能当净开销；Profiler整窗main CPU保守≤8秒，同样包含普通业务 |
| 外部CPU | 准备/Controller/源worker/counter/native sampler连关闭总≤40秒：准备≤25秒、正式辅助≤10秒、关闭留5秒；native sampler至多3秒占正式辅助 |
| 保存 | source一份≤768MiB，journal≤128MiB，profile≤16MiB，native sample≤8MiB，全输出含临时文件≤1GiB；未ACK≤8MiB，栈字典≤8MiB |
| 事件/记录 | 最多2 episode（CPU1、wall/heartbeat1）、1次Profiler、1次native sampler，≤1500自然root、10000入口、65536 GC、4 cohort |

任何episode准入先留完整返回：120秒自然后续、30秒下个自然入口等待、10秒profile、10秒控制/停用及90秒源核对/清理，共260秒。正式开始后1540秒起只留存晚到信号，不再启动不足预留的episode；native sample单独至少留95秒。首个episode及有界取栈封存即可结束，无需为花完第二类事件额度继续等待；未使用额度退休。

自计不含全部隐含状态效应，整窗上界也可能含普通业务；两者分别报告，不凭小数值宣布无扰动。同步JS不能被CPU帽强抢占：最后一次越界原值保留、停止新诊断准入，绝不杀真实应用。profile原件大小只能在stop返回后核对，若单次越帽照录失败而不是丢原件追绿。

在时间、记录、未ACK/输出、自计/整窗CPU触帽，source/birth/build/owner变化，序号丢失、fsync或传输结果未知、用户取消、90秒lease失联、Profiler恢复不明时停止。已完成的普通warm统计不再决定是否保存下一条自然异常，但未知执行效果/原件损坏不能被忽略。

停止顺序：停止诊断准入→保存原未ACK批次且不新读业务→停止/disable Profiler→恢复自有方法且不覆盖新owner→移除心跳/监听/binding→源/内容核对与fsync→只关闭本轮拥有的Inspector并确认拒绝连接、原Peer仍活着。若main仍堵塞，外部采样立即截止，main内恢复须等它能运行；此时明确unverified，不能声称硬watchdog已恢复，也不能借此重启Peer。

## 模块合同与执行前最后检查

| Module | 唯一事实/Interface | 必须验证的失败出口 |
| --- | --- | --- |
| Natural Recorder | 原方法透明执行，输出Entry/Root/Span/DiagnosticBoundary，seq/parent/CPU与栈由其拥有；不公开controlled read接口 | 原receiver/值/Promise/异常；重入/嵌套不重复计CPU；cap后原业务继续；晚到owner不覆盖 |
| History Journal | 拥有完整追加事实和durable ACK，Controller只持引用 | fsync失败原批次重取不重读业务；满额不覆盖；断档不伪造前史 |
| Cohort Detector | 只消费已归档记录、前9根和固定阈值，输出typed candidate | 无基线/源变更/GC/不完整根/超时，不倒填、重学或补点 |
| Stall Watchdog | 只读OS身份、心跳与一次自有native sampler，不依赖main返回 | CDP断线与真堵塞区分；native child硬截止；PID复用拒绝 |
| Episode Controller | 独占CPU/wall额度、自然后续根和一次profile生命周期 | 先封存后取栈；未知start不重启；busy只合并；lease/取消/恢复可审计 |
| Source/Identity Adapter | 输入副本、实际query依赖代次及源码/source map绑定 | snapshot不一致、watcher缺口、无revision标identityIncomplete，不给同输入结论 |

复用已经验证的对象发现、真实入口映射、原异常透明、durable ACK、时钟与Profiler恢复机制，不再次跑三宿主性能资格。新增部分须在同一候选一次功能槽验证：所有基线前记录被保留、真实入口父链、无heap getter/controlled request、first-witness先于profile、活main长同步时外部watchdog能唤醒、原件丢失/取消/晚到owner/恢复以及原端口拒绝。功能fixture可测试等待/错误和阈值，但合成耗时/数字显式notFieldCause，不当产品根因。槽失败保留并停止，不再增加Node/Electron资格进程。

运行前冻结源码、实际build/runtime、当前入口对象、data/source map、所有新接口、阈值、预算和时间域，逐项绑定receipt；当前代码尚无FR1执行器，不拿现有143项/Node结果当FR1完成。没有本任务实现或发布，不为这篇方案运行产品测试。

## 什么才算根因进展

工具验证成功只算工具就绪；第一阶段要交付同一OS birth下、同输入/图、无Profiler阶段的较低成本→较高成本原根，以及无断档前缀与当时逻辑父链。若只得慢态、热点缺失、输入变化或仅Evidence与余部互换，按实际缺项报告，不能说原问题已归因。

下一步只有在现场候选出现后，才围绕其**实际额外工作/状态与形成动作**冻结机制反事实：同输入同动作史重现、只移除该因素阻断、恢复因素再现，并检验recorder ON/OFF本身是否制造状态。VM内部状态未被完整记录时，不得把顺序日志叫完整VM快照或确定性重放。不得从通用“保留8份输出”等矩阵再试起。

本方案机制复现执行额度为0，旧G2密集指标与新自然变化的桥接也未获本方案验证；若拟替代原确认协议，需另有明确方案评审，不在实现时临时改门。机制候选未出现前不启动大矩阵、不重跑资格；任何工具/窗口结果都不给RI-01/产品重构开工状态。

本轮11份封存收据、8组返回锚点、当前控制器及C2覆盖审计完成；首轮status聚合误用已保留修正，数据SHA/算术/引用/JSON/diff按文档范围自审。没有产品代码变更、新产品查询、owned宿主、实际Peer附着或Profiler，累计owned41、已知产品读CPU下界635118.989ms及旧C未知不变。本次交付是策略复审与可评审设计，不称发现产品根因。
