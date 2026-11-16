# RI-00：84根五处F0暖段超门拆解与校准排布诊断

创建时间：2026-11-14
最后更新：2026-11-14

## 输入、职责与验收

本轮C级离线诊断，沿工程总纲及Accepted `96-task-execution-responsiveness.md`、Proposed `128-local-runtime-isolation-and-bounded-query-contract.md`，不改变产品边界或重构状态。输入仅为[完整块顺序原84根及journal](runtime-isolation-ri00-e3-pair-order.md)，producer `1c053c5672d23c9848f29e012ada72417128bf0d`；新分析candidate `6a15ce74205f079cb63f9a4c8207b87207eeeb6a`。

[机器收据](../../playbook/evidence/runtime-isolation-ri00-e3-order-variation-results-20261114.json)绑定原report SHA、journal SHA、binding、分析源码、输出、完整进程费用与下一轮纯动作图。原84根全部按host+ticket连接，常量label不能代替身份；原线程边界重新计算PMC与原值相同，两个F0及deltas=null逐项重放不改判。48个metric、六暖块全部保留，五失败、一个6.902ms控制块；首metric根保留但不进暖统计，使用原64MiB、major/incremental、其它线程严格<120ms条件，原≥3个兼容暖点及15ms门不变。

共用的高低端点、逐遍/余部和工作量恒等分解从既有分析Module复用，journal关联改为显式84/244数量校验。旧244根审计相关测试通过，没有为本次复制另一套兼容或中位算法。全量原件仍在原journal，报告是可追溯投影；本轮未读取SQLite或调用产品查询，未启动Electron、专用Inspector或Profiler。

## 五处极差：先区分角色、CPU域和真实时间

各行取原兼容暖点的高Evidence用户CPU根减低根，单位ms；每个三元组为用户/内核/合计。数值3位小数显示，原精度下12遍和余部/全根分别闭合。余部只表示完整Supervisor根减12个Evidence跨度，尚未分配到具体plan/VM函数，不能拿其下降冲掉原用户门失败。

| F0块 | 角色 | 低/高ticket | 高值在时间上较晚？ | Evidence 用户/内核/合计 | 余部 用户/内核/合计 | 全根 用户/内核/合计 |
| --- | --- | --- | --- | --- | --- | --- |
| order-target-1/0 | target | 16/17 | 是 | +21.155 / -1.478 / +19.677 | -7.009 / -0.108 / -7.117 | +14.146 / -1.586 / +12.560 |
| order-target-1/1 | conditioning | 16/12 | 否 | +15.738 / +0.883 / +16.621 | -1.387 / +0.308 / -1.079 | +14.351 / +1.191 / +15.542 |
| order-target-1/2 | target | 26/27 | 是 | +19.053 / +0.584 / +19.637 | -4.846 / -0.362 / -5.208 | +14.207 / +0.222 / +14.429 |
| order-target-2/1 | conditioning | 26/24 | 否 | +20.205 / +0.268 / +20.473 | -4.693 / +0.743 / -3.950 | +15.512 / +1.011 / +16.523 |
| order-target-2/2 | target | 26/27 | 是 | +15.598 / +0.491 / +16.089 | -6.064 / -0.164 / -6.228 | +9.534 / +0.327 / +9.861 |

三处属于target、两处属于conditioning。两处conditioning极差都先高后低，不能把按CPU排序的高减低写成同进程变慢形成；三处高值较晚也未建立合格F0或现场自然前史，仍不是合格快→慢证据。用户极差15.598～21.155ms之外，Evidence内核有负有正（−1.478～+0.883ms）；全部余部用户变化为负，抵消1.387～7.009ms，不能据此说内核或余部已无变化。

## 十二遍与GC落点记账

位置0～11。进入表示对应minor重叠计数0→正，不是GC CPU；保留表示该位置计数相同且为正，也不保证相同VM工作。完整每遍用户/内核/观察GC wall向量保留，既不把观察wall当CPU，也不相减后追认门。

| F0块 | minor进入位置 | 进入位置用户差ms | 同计数保留位置用户差ms | 原用户极差ms |
| --- | --- | --- | --- | --- |
| order-target-1/0 | 1,2,6,8,10 | +12.261 | +8.894 | +21.155 |
| order-target-1/1 | 0,8,10 | +5.740 | +9.998 | +15.738 |
| order-target-1/2 | 1,2,6,8,10 | +13.951 | +5.102 | +19.053 |
| order-target-2/1 | 1,2,6,8,10 | +13.659 | +6.546 | +20.205 |
| order-target-2/2 | 1,2,6,8,10 | +10.781 | +4.817 | +15.598 |

四对从root minor11（4个仅在余部、7个与Evidence相交）变成12（12个与Evidence相交）；conditioning第一对root都为12，却从3余部+9与Evidence相交变成0余部+12相交。按journal已观察事件求交与端点原注释一致，不能只看整根minor总数，也不能把整根减逐遍计数当作所有余部事件；这里明确按区间重建。

进入位置合计5.740～13.951ms，保留位置仍4.817～9.998ms。target1首块位置3单独+4.385ms，其minor计数未变；不能把整个21.155ms归给“多一次GC”。这不是对保留位置排除GC，仍缺逐遍retired instructions、原生CPU与执行热点。

## 工作量和执行速率代理分开

下表同一高/低端点的**全根外部主线程窗口**，不是Evidence逐遍。I=retired instructions，CPI=cycles/I，T/C=外窗CPU时间/周期；三项对CPU的贡献使用对数均值恒等式T=I×(C/I)×(T/C)。可精确闭合不等于因果归属。原行CPU与外窗CPU差额单列，不能把外窗项强分到Evidence或当作物理频率。

| F0块 | 指令变化% | CPI变化% | T/C变化% | 外窗CPU差ms | 指令/CPI/T每周期记账项ms |
| --- | --- | --- | --- | --- | --- |
| order-target-1/0 | +0.236735 | +0.490398 | +2.228170 | +12.644 | +1.021 / +2.111 / +9.512 |
| order-target-1/1 | -0.362554 | +1.700965 | +2.384833 | +15.538 | -1.533 / +7.121 / +9.950 |
| order-target-1/2 | +0.261793 | +0.049604 | +3.115914 | +14.402 | +1.114 / +0.211 / +13.077 |
| order-target-2/1 | +0.468780 | -0.620301 | +4.181081 | +16.555 | +1.964 / -2.614 / +17.204 |
| order-target-2/2 | +0.718436 | +1.265119 | +1.010319 | +12.311 | +2.959 / +5.197 / +4.155 |

四对指令增加0.236735%～0.718436%，一对反而减少0.362554%；不能把原业务调用图相同当作实际等指令。五对T/C均增1.010319%～4.181081%，其记账项4.155～17.204ms，四对大于另两项；最后一对CPI项5.197ms仍大于T/C项4.155ms，不能统一写成“只是速率”。这些端点外窗CPU报告在Performance层，Efficiency层零/非正计数按unavailable处理，不拿它补0分解，也不以此排除未观测的调度或VM因素。

全部六块中枚举所有“原兼容暖点+相同完整root及12遍GC计数签名”按时间先后的14对，全部保留而非按CPU挑点，其中五失败块12对、控制块2对。最大正向Evidence用户差13.650ms出现在target1末块ticket24→27，整根指令+0.064111%、T/C+3.131340%；conditioning后块21→24另有+12.736ms，整根指令−0.492391%、T/C+3.867692%。这仍是新owned小窗口、共享点的描述，不是独立重复或现场30–40ms机制复现，root近恒定I也可能隐藏逐遍与余部相反工作变化。

所有84根的原IO/pagein增量及已观察GC前史保留，端点没有凭空插值。观察GC计数签名相同、外窗可用、校准稳定，都不等于每遍native/VM成本相同；完整原生GC/分配历史、热点链及现场残差自然形成仍缺。

## 为什么选校准排布，而不是再跑原F0

原18次native SHA均在各自10根之后。它们给出固定工作量的块末参考，但没有高值根之前的即时参考，也没有证明对读取前史中立。target1首个失败块之前该宿主尚未执行native校准，所以不能据此把旧块末校准认定为五失败的根因。

新问题是一个可证伪的**主动控制因素**：在不改变每块规定查询/hash工作、不改150ms根间等待窗的条件下，把同量校准移入三个既有窗，能否使暖段波动发生可重复变化？它不是删查询、缓存、forced GC、native计数ON/OFF或归档粒度重跑；不往root/Evidence计时体内人工塞延迟，实际Peer不做native热机。校准包含原生工作和少量分配，排布还会改变闲置前史，不能孤立解释为频率或GC干预。

原顺序试验两次F0拒绝、0格处理的事实不变，顺序效应仍未测试。本轮设计转向解释F0自身，不再把待解释的暖段失败当作是否采集预定B的先决条件。**旧F0准入代码和15ms门不动**；新试验没有F0通过状态、快态baseline或现场准入出口，不借诊断采集绕过原门。

## 冻结的下一轮单变量与判据

[机器预算](../../playbook/evidence/runtime-isolation-ri00-e3-calibration-placement-budget-20261114.json)绑定本次原数据、审计、纯动作图及资源代码SHA。仅设计，runnable=false、executed=false，尚无runner或新接缝资格，本轮不启动任何实验。

- 固定一个conditioning加两个target，最多同时2个，零替换；两个target固定ABBA/BAAB，每格仍target完整块→conditioning完整块，所有块10根（clock-start/8 dense/clock-end）及逐根fsync/ACK保持，远端label不变。
- A：target原3次native SHA放块末；B：同3次放序列index2/5/8读取前（clock-start=0，dense=1..8），conditioning始终块末。每次仍16轮×4MiB。150ms窗口从native之前开始，只睡剩余时间；绝不在SHA后再额外睡150ms或压缩下一窗追时。B整块会少一部分未重叠等待，属于排布及闲置前史的组合因素，记录而不伪称相同总墙钟。
- 各host在8根相同预热前统一3次native初始化，避免B出现独有首次4MiB分配；共9次公共准备。它相较旧运行改变公共前史，A若因此不再超门，必须记旧坏基线未复现，不能把变快归给B。规定工作量相同不代表实际retired work相同，继续分别保留I/C。
- 原每块8点/首点规则、兼容≥3、64MiB、major/incremental0、其它线程CPU严格<120ms、PMC专属、metadata≤2ms、输出图/epoch及**每块原暖段≤15ms的判定**都保留。A失败仍为原门失败，B达到15ms也不构成完整G2/F0资格。
- 解释诊断对比还要求所有raw target、raw conditioning及target−conditioning同arm用户中位返回绝对差≤2ms；native相对公共3次初始化中位的校准比漂移≤10%，不拿SHA比例重算用户指标。每块9间隔均≥150ms，每预定对比target间隔中位差≤5ms，逐次native与root不得重叠，hash位置/次数按journal验证。违反即对比无效，不调窗或增点救回。
- 主诊断指标是原兼容暖Evidence用户CPU**极差**。四个固定不共享块对比为target1 A0−B1、A3−B2，target2 A1−B0、A2−B3。所有控制有效、四个A均>15ms、四个B均≤15ms且各极差减少≥5ms，才支持本限定条件下校准排布对暖段门的充分性。
- 任一A已≤15ms，判旧坏基线未复现；A失败复现且控制有效、B标准不达则本假设不支持；控制/返回/源/资源/恢复不满足则诊断无效。无论哪个结果，都不输出performanceQualified/F0通过/现场资格。CLI只能以有前缀的diagnosticControlsValid及diagnosticOutcome表达；exit0仅表示诊断有效完成，不表示任何性能门成功，不能有模糊passed字段。

所有16块按原次数固定采集，普通暖段失配不阻止预定B或返回；这是一次专门诊断门统计量的试验，不是放宽15ms。source/owner/epoch、未知RPC、取消/超预算仍停止。raw/归一化、用户/内核/合计、12遍/余部、全根逐层I/C/CPI/T每周期及每个原暖门状态全部保存；同GC补充配对仅按预定格对左点时间顺序匹配最早未用右点，不按速度筛选，不替代原门。不会用该诊断移植native热机去消掉实际Peer的现场残差。

## 预算、接口和异常恢复闭环

动作图固定3次Electron、184根（24预热+16×10）、128 metric、48块内native+9初始化=57次、3次末尾语义审计。正式读CPU200秒、hash4秒、wall15分钟含90秒清理；准备另限120秒（unit、专用Node、数据binding、收据各最多30秒），总活动墙钟17分钟，全部准备CPU仍在原20秒aux内另保守计5秒准备关闭，probe每host5秒。输出128MiB/journal32MiB/未ACK16MiB，旧失败不删不置零；默认VM、零Profiler、零新native计数库、不改优先级/亲和性/功耗、不强制GC或加堆压力。

预测3个冷首根×3000ms+181暖根×750ms+1500ms语义=146250ms；native57×50=2850ms。正式wall预测454250ms（包括24000ms窗及114000ms native RPC，B中重叠部分保守重复预留）；加120000准备后574250ms/1020000ms。不是未来未知成本保证。

首次target处理前必须覆盖**两个target完整四格及尚未打开的target**：168根（含未来8预热及1冷首根）、51native（含未来3初始化）、24000ms窗口、102000ms native RPC、15000ms未来启动、1500ms全部审计、20000ms controller、10000ms源核对、90000ms清理。floor为读129750ms/hash2550ms/wall390750ms。第二target前仍预留80根/24native、全部1500ms审计、12000ms窗及返回/清理，floor读61500ms/hash1200ms/wall241500ms；两次controller剩余均≥5000ms。

费用估计用所有已完成host的首根作为cold，其余所有完成根（包括GC不兼容或慢点）作为warm，分别max(3000,已观测cold×1.5)、max(750,所有warm×1.5)；wall同样取CPU和已测wall较大。native用max(50,所有已完成native CPU×1.5)。已消费不随phase/host清零，预留不足则不开始，未知未来不得当成保证。

纯动作图拥有位置/次数/预算公式；未来controller只拥有固定调度、窗口剩余时间、累计费用及准入，不能选择green点。原probe/queue拥有真实root/ticket，native/row是独立费用域，journal唯一保存原事实和fsync后ACK，result只投影原门及新诊断判据，不向field admission发布状态。owned Adapter只拥有自有进程/端口，Store仍拥有原只读源事实。

request应答未知只查原ticket；native应答未知不能重试，停止新准入，保留未知结果与已知费用下界，若最终native ledger可取到则补入已执行成本，不能猜0。fsync失败保留原件；晚到owner不覆盖；取消/source/预算退出使用原90秒清理，CDP先断再exit，核对实际端口refusal和owner/method/binding/queue恢复，语义输出/源SHA闭环。普通暖段计时失败不改变预定采集序列，不触发额外root/slot；硬性身份、未知结果或预算错误仍停止。

前置同候选专用Node资格固定1次、2逻辑host/无目标子进程、44合成根/30秒wall/2秒合成读CPU、1MiB journal/2MiB总输出。固定4块A/B及6初始化+12块内native，加最后1次应答丢失native，共19次实际native执行；在fsync失败的原completed未ACK ticket上另试1次native，必须因pending拒绝且零SHA，共20次native RPC尝试。最后未知应答注入后不再读取/重试native，取停止ledger并恢复；原读失败后的后续准入在该场景前验证。scope与原生随机断连区分，Reporter只引用journal，不重复序列化raw record。

实现前已冻结上述序列/数据/依赖/失败出口；仍需真正runner、同候选测试、时序与归档接缝、完整编译Module/8534内容文件+空fence身份、full CPU/EOF/return成本和原件SHA绑定，全部满足才按新预算启动。纯计划与离线回放不能替代这些门；本轮不执行新Node或Electron。

## 本轮验证与边界

22项聚焦测试在分析candidate通过，兼顾旧244根分析、首点/120ms严格边界、常量label身份、真实时间方向、未知PMC/零性能层、完整预算与1微秒短缺拒绝。首轮资源测试人工预期把首次wall多加100000ms，原失败日志保留；按公式逐项和修正为390750ms，资源函数、既有帽和15ms门未变，预算在修正后才冻结。

CLI实际重放全部84根和journal、原F0、五个逐遍/余部用户内核差和全部外窗PMC；完整离线子进程用户60.931/内核15.497/合计76.428ms、wall80.777ms，父进程待退出后取值覆盖git及输出/fsync尾段。源/原report/journal SHA未变。用原warm费用做资源公式离线例证，首次读预留129900.270ms/wall390931.853ms（cold依3150.270ms而非固定3000）；第二次61500/241500ms，明确不是新执行成本或未来保证。

实施者自审，syntax/内容/引用/diff核对通过；CI查询无workflow/status，不称绿色CI，未做新Inspector、产品build/release或现场。E3实际owned仍38、已知产品读CPU下界552064.684ms及旧C未知不变；新设计仅预留3个，若未来全部使用才到41，旧失败/未用slot不复用。五极差记账已分开，原门仍失败；旧3.95秒缺口、现场同进程快→慢及机制复现缺口保留，不重构。

## 后续固定执行

上述预算和判据未修改。唯一一次Node资格及原三宿主完整执行见[校准排布执行封存](runtime-isolation-ri00-e3-calibration-placement.md)：184根/57native完成，但返回漂移失控，诊断invalid；原15ms失败及所有原件保留，没有补进程或现场资格，不能把本设计继续当作尚未执行。
