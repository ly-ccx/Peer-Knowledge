# RI-00 E3-N：逐遍工作量与热点取栈资格

2026-11-13，先冻结设计后执行；实际结果见§收据。C级诊断，沿用`00-adr-map.md`、Accepted `96-task-execution-responsiveness.md`及Proposed `128-local-runtime-isolation-and-bounded-query-contract.md`；不移动产品契约，不启动重构。父证据是[E3 K/A](runtime-isolation-ri00-e3-qualification-followup.md)。本文件不把旧16.182ms或旧现场30–40ms事后补成有栈的事件。

## 已知边界与可证伪问题

K的同GC落点暖点Evidence用户CPU差16.182ms：逐位置差为0.830、0.545、1.476、2.104、0.851、5.066、−0.082、1.629、0.192、1.451、0.318、1.802ms。最大位置只占31.3%，其余11.116ms分散；整根另有5.703ms用户CPU差不在Evidence跨度内。整窗多201,762,107条指令（2.4895%），既没有逐遍计数，也没有热点执行栈。GC wall重叠不是GC CPU，不能拿它相减。相同minor落点仍容许不同VM工作，不等于证明GC原因或核频原因。

N先回答工具能否把新增工作定位到12遍及根内余部，随后才问哪条栈增多。阶段不混合：第一阶段只加边界计数，不启动Profiler；第二阶段单独改变Profiler开关。Profiler状态下的数据不能成为无Profiler的G2快慢资格。旧归档粒度保持固定，不再检验。

## 计数Module与归属

owned宿主用一个只读Node-API C扩展，对当前进程/当前线程调用已验证过的libproc flavor34。不使用task port、优先级、硬件配置、VM参数或强制GC；不采用尚未验证的另一私有ABI。初始化核对性能层数、struct长度/保留位、线程身份、时间基准；每次读取都核对ABI并保留逐层instructions/cycles/user/system ticks。非单调、换线程或未知成本直接失格。

[Apple Recount说明](https://github.com/apple-oss-distributions/xnu/blob/main/doc/observability/recount.md)支持线程/性能层计数的含义，不承诺本机私有结构永远稳定。[Node-API文档](https://nodejs.org/api/n-api.html)说明其C ABI独立于V8；是否能在当前Electron加载、成本多大，仍以本轮真实宿主验证为准，不从文档推成通过。

每根固定预分配26个边界槽：root前后加12遍各前后。N-API写入固定BigUint64Array，成功路径不生成JS对象，不加逐getPlan计时/取栈。原函数receiver、返回值与异常保持；计数故障记录为诊断失败，不吞掉或改写产品异常。转换字符串、序列化、归档在root测量后执行并单列CPU。逐遍和root余部必须算术闭合；边界调用自身落在余部，不能当业务热点。外部原PMC仍校验整根专属性、线程身份及内外窗口成本；不能拿代数恒等式单独证明计数正确。

这次native库只进入可销毁的owned宿主。实际Peer不能安全卸载新native库，故不注入；现场仍只用已验证JS首见证和外部PMC。现场逐遍工作量若仍缺失就明确缺失，不借owned结果冒充现场形成。需要改变此边界时另做方案和恢复验证。

## 单变量与验收

N0一个functional Electron验证ABI加载、26槽、错误/返回值透明、禁用/启用、越界/嵌套拒绝、停止/owner恢复以及零JS heap getter。native首用和预热计费。失败消费本槽，不替换。

N1/N2两个production Electron使用原封存输入、Module与默认VM。各8根相同预热；随后4块、每块8根，N1按OFF/ON/ON/OFF，N2按ON/OFF/OFF/ON。唯一因素是边界native调用，OFF仍预分配同一buffer并保留相同元数据结构；两边同样排队、150ms间隔、逐点durable归档与ACK、整根外部PMC、块末3次native hash校准。不筛选GC、绿色暖点或最后一个块；失败原样保留。没有按块排空对照，没有顺序曝光。

预注册工具门：每块ON的所有完整根恰好12遍/26槽、逐层计数单调、无major/incremental拒绝规则变更；计数边界wall合计每根≤1ms且自身thread CPU上界≤1ms；内外整根指令差≤1%且CPU差≤2ms或5%中较大者；两个进程ON相对OFF的各两块Evidence用户CPU中位改善/恶化绝对值≤2ms，且返回块未出现不可解释的≥15ms状态漂移；原G2暖极差15ms不变，未通过则不产生快点资格。工具门未过不启动热点阶段或现场。

热点阶段的资格设计为OFF-profile / ON-profile / OFF-profile三块，每块2根，边界计数均ON。Profiler以1ms采样，单块最多2秒读取、每进程最多一次start/stop；启动/停止、输出及所有CPU计费，profile块不用G2。用真实函数名的读取跨度和profile样本建立时钟区间；重叠不确定样本单列，未知/GC/native不硬归到JS。若采样数、时钟校准或前后无profile稳定性不足，热点归属拒绝而不加读数追样。不得用preciseCoverage（会改变优化）、事后入口栈或栈出现次数冒充指令份额。

执行约束进一步收紧：这次三槽先只执行计数器资格，热点控制器尚须完成时钟/异常恢复验证，不得在任一宿主临时启用Profiler。原“同一两个进程各追加”的设想与“两个target都通过后、最多一个存活”不兼容，执行前撤回这一调度；保留热点单变量设计但不称已可执行。profile预留不会兑换成其它读取或新进程；N1/N2退出后不得为了补profile再拉起替代宿主。后续热点执行需冻结新的独立固定槽及预算，计数器通过不能自动准入。

热点报告至少保留每位置时间/指令/周期、GC落点、完整父子调用路径、exclusive/inclusive wall样本、未解析份额与采样不确定性；只声明采样wall热点，不称函数精确指令数。已确认工作增多需在无profile前后仍存在。候选机制必须先有同进程快→慢的真实前史及工作分布变化，再冻结一个可逆因素、固定返回对照和独立预算；不能本轮临时试缓存、堆/GC、JIT参数矩阵或人工加耗时。

## 新预算与现场准入

新增N最多3次Electron启动（N0、N1、N2），最多1个存活；15分钟墙钟（含90秒清理），产品读体≤90秒、控制器/辅助CPU≤20秒、编译/准备CPU保守预留10秒并另计、native计数总CPU≤1秒、Profiler每宿主一次且最多2根、输出128MiB、journal32MiB、未ACK16MiB。总上限非目标。所有失败占槽，工具门失败则取消后续profile；没有replacement/补进程/借用F/R/H额度。编译和Node自检不启动应用，仍单列成本；无native可用即封存，不改用另一ABI追绿。

新增后E3 owned启动总计划帽从33变36、活动墙钟从112变127分钟；旧17次启动及243.217306秒读体不清零。F/R额度仍冻结。

实际Peer装配与完整F控制器分别是独立准入门：必须核对当前安装产物、五实际注册入口/可信窗口外层、共享ports/Directory/Supervisor/store对象、读者覆盖及当前epoch，不能借N的owned身份。只做metadata发现/owner闭环，不执行业务读取、不装native、不重启。打开诊断端口前须已有同宿主lease关闭/恢复验证；记录准备本身造成的前史缺口，端口最终必须ECONNREFUSED。

F控制器须经过真实owned队列/归档接缝和异常路径验证：F0及heap-free pre-F1，F1有效已慢时保留F0及自然前史并进入第二次无profile确认，不能丢掉转换或重学；F1失配/未达确认漂移才封存。60秒静默、5根固定自然基线，first-witness先于heap/native/profile；single-slot及fsync后ACK；Q1/Q2用原G2，所有预算继承C1/C2而非重新置零；source/owner变动、RPC未知、取消/超时/断连/预算耗尽均封存并恢复，未ACK原件保留。只测纯signal不等于全控制器通过。任一门未过，F不启动。

实施结果、失败、候选与回收实测另回填，不覆盖父回执。RI-00闭合仍需现场同进程快→慢及受控机制复现；本轮工具通过也不能称根治。

## 收据：三槽已结束，计数有效不等于性能资格通过

producer `656aeb46`的N0/N1/N2全部按固定额度完成，3/3启动已用完，没有替代。N0在真实Electron加载C扩展，witness ON/OFF两根、零三类JS heap getter，确认26槽/禁用零调用。Node边界复核另有4个真实native错误参数拒绝；原异常对象透明、counter错误不替换原异常、禁用/26槽及恢复由聚焦测试验证，不把这些pure/shim测试冒充N0全路径。编译CPU约0.18秒，按冻结10秒保守预留。一次毫秒浮点累加精确断言失败保留，改为先加BigInt原始tick再转换，原断言不弱化。

两个production各8预热+4×8点，总80根，N0另2根；32个ON生产根提供384遍PMC。全部生产投影/23会话/3859 plan/12×69266行一致，零读失败、拒写、元数据丢失；整根专属性及内外指令核对全部通过，最大指令窗口差0.116829%。每根26次边界read的wall最多0.088ms、counter thread CPU上界最多0.310ms（包含计量clock），32根及N0合计8.476ms；边界自计不是无状态影响的证明。

| target | OFF/ON对应块的兼容中位差（ON−OFF，ms） | 四块原兼容极差（ms） | 工具资格 |
|---|---|---|---|
| N1 OFF/ON/ON/OFF | −3.957、+2.293 | 14.897、15.512、15.577、18.634 | 拒绝 |
| N2 ON/OFF/OFF/ON | −0.6105、−5.467 | 14.792、12.307、24.232、12.960 | 拒绝 |

原producer的报告漏用64MiB与其它线程兼容条件，使用GC-only暖点算仪器中位/极差（原数值与失败报告均保留）。当前`34ba0d24`提取结果Module，改为直接调用原`summarizeDenseBlock`，全部原点离线重算为上表，两个target依然拒绝；未改15ms或2ms门、未增加读取，不叫原producer执行了新版gate。该资格没有同birth reference和F0/F1，本来就不能创建G2快态。未通过门，因此没有Profiler、新现场或顺序曝光。

封存ON暖点按“同一块、相同完整root及逐位置GC签名”枚举全部8个配对，完整向量保留。最大Evidence用户CPU差9.583ms的一对，Evidence内指令反而少7,744,635条、root少5,012,968条；12遍CPU差之和与root余部独立保留。这是新owned、不同仪器的观察：说明CPU与工作量必须分别报告，既没有重现K的+2.49%工作增量，也没有同进程30–40ms形成。不能据它把旧额外指令改写成“只是速率”。旧16.182ms的逐遍指令/热点仍永久缺失，无法追溯补录。

进一步不增加读取，枚举每进程ON暖点中所有“原兼容门+相同完整GC签名”的**按实际时间先后**配对（含跨块），共21对，全部保留而非按高低重新排序。最大正向root指令增量75,905,403条（0.9363%）中，Evidence50,109,765条、root余部25,795,638条；Evidence用户CPU只增2.222ms。逐遍多出的指令主要在位置0/1（+18,338,275/+26,559,759），其他位置有正有负，12项及余部精确闭合。最大CPU增量仍是前述9.583ms且总指令下降的一对。这样已能把新增工作放到具体遍与非Evidence余部，证明仪器新增的分辨能力；它没有找到K的2.49%对应链，也没有确定VM/业务原因或合格快→慢。后续热点方案必须覆盖root余部，不能只对12遍取栈后把整根额外工作说成已定位。

本轮读体38.817511秒、原生hash校准0.578790秒、probe自计约0.080877秒（不可与其包含项重复相加），墙钟53.380秒。控制器+counter EOF+1秒关闭reserve计1.897636秒，另10秒编译准备保守占额；journal3,421,706字节、stage输出当时6,122,604字节。原始/离线审计附加文件另列，未删除失败腾空间。82根、24次hash均按实记录，所有方法/binding/单槽恢复、三个owned PID及counter均退出；8534内容文件SHA/size和空fence再次逐项匹配封存manifest。E3已知受控读体累计282.034817秒、已用20次Electron启动，不把F/R预算重置。

## 热点链的离线验证与硬限制

新增profile跨度归属Module保存完整parent链、exclusive leaf估计、GC/native/未知叶子及边界不确定样本。它不把inclusive父节点再累加、不把sample计数说成逐函数指令，也不把GC sibling节点强接到JS父链。协议说明见[Chrome Profiler](https://chromedevtools.github.io/devtools-protocol/tot/Profiler/)；采样开启与preciseCoverage的优化影响不是同一工具。

只重放封存的E3 profiler-v2真实profile，未启动新Profiler。两次有名字的生产读同时给出profile→hrtime及hrtime→performance的有界区间，没有假定原点相同。组合offset不确定度±2.289521ms，8根×12遍共96跨度，叶子时间估计各自闭合；但10ms采样只得到115个确定样本、64个边界不确定样本，96跨度全部不足3个确定样本。因此旧profile不能提供逐遍热点结论。1ms的ON/OFF/ON前后验证仍只是待执行设计，不能把分析器重放叫采样开销或完整F控制器通过。

## 实际Peer装配：一次失败和已完成的恢复

候选`b22ea485`的一次metadata-only附着额度已消费。安装包五个相关Module静态摘要已取到；脚本却固定寻找9229，实际进程沿启动参数在随机端口监听，最终`endpoint_missing`、0条CDP验证命令。原报告对9229的refusal只证明错端口关闭，**不能证明本次打开的端口恢复**，该报告保持失败。

随后仅作恢复：从原PID的实际监听表定位新端口，连接后核对process identity，只调度Inspector.close；255ms内取得该实际端口ECONNREFUSED、原进程存活。单独恢复收据不算第二次资格验证，没有调用业务、装产品方法probe/native或重启。最初SIGUSR1到恢复之间的主线程成本没有计量，明确unknown而非按零补账；从原尝试startedAt到恢复finishedAt的墙钟上界46.239秒，超出45秒原额度的事实保留，不把2.131秒错端口尝试写成全部成本。最终再次lsof无监听，个人任务未触碰。

`34ba0d24`修成PID监听表差集→node endpoint→PID核验→真实端口关闭；原有监听不继承所有权，未知发现/附着失败仍要走恢复而不能假定没打开。随机端口/已有监听/非loopback等pure测试及真实catalog+trusted authorizer的Node Inspector闭包测试通过；实际Peer未再附着，不能写成装配已验证。完整F控制器仍未取得真实Electron端到端资格。

## F控制器审查结论及下一步边界

继续冻结F。各事实owner和控制序列必须由一个完整控制器贯通，不能把分别绿色的Signal/Queue拼成现场通过：

| 接口/owner | 必须保留的序列与失败出口 | 当前验证范围 |
|---|---|---|
| Site discovery / 安装对象owner | 五handler、授权在callback之前、同ports/Directory/Supervisor/store；前后对象相等；晚到owner不覆盖 | owned真实注册Module与Node可信外层通过；实际Peer本次附着失败 |
| Checkpoint / 原G2事实 | F0锁定→60秒及首5自然根→heap-free main/ref/main→F1；有效F1已慢则第二确认，失配/漂移封存，不重学 | 原G2 Module测试通过；完整编排未验证 |
| Journal / durable事实owner | first-witness先于heap/hash/profile；ticket/batch/entry各先fsync后ACK，RPC超时只查原ticket，未知不重放 | 原Q/A队列接缝通过；完整F外部journal编排未验证 |
| Signal / policy owner | 5根固定自然基线、parent+root/nested覆盖、一个pending、最多2exposure；F1只夹住指纹而不替换F0 | 7项策略测试及封存A重放通过，不代表场景形成 |
| Ledger / 累计费用owner | C1/C2旧receipt SHA及unknown继承；6完整Q、48/32秒、30分钟与90秒恢复取较严；不足不降样本 | 原预算契约已定；F适配器尚未实跑 |
| Recovery / 安装租约owner | 断连/取消/source/owner/超限即封存；方法/绑定/队列恢复且actual port refusal；未ACK留原件 | 原Q/A实例通过；本次实际端口恢复单独证明，发现修正未再实际执行 |

下一步不原样再跑N两进程。先用本轮逐遍CPU/PMC和完整归档做工作量与速率分离审计；热点控制器须先验证真实读时钟、样本粒度及start/stop成本，尚无已通过的可执行profile/现场资格。实际端口发现修正需要一个另冻结、不能改写本次失败的资格额度；完整F的durable编排与异常恢复也须在真正owned Electron中单独验收。未满足这些门，不接续负窗口、不借R预算、不重构；现场同进程形成和机制复现仍是RI-00闭合条件。

[本轮公开收据](../../playbook/evidence/runtime-isolation-ri00-e3-n-results-20261113.json)绑定原报告、离线重算、热点重放与实际端口恢复。`34ba0d24`的42项相关测试一次通过，architecture/UI/diff通过；最终`ffbad972`只把两个资格CLI的`passed=false`同步为非零退出（原producer的零退出及失败JSON保留），另做语法/diff审查、不重新启动；producer、附着候选及当前candidate的PR workflow/status查询均空，不称绿色CI。没有运行全构建、完整产品回归或安装/发布验收，审查为实施者自审。
