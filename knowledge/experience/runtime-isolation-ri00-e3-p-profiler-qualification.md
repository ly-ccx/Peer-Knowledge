# RI-00 E3-P：专用时钟、Profiler恢复与等工作量对照

2026-11-14，执行前补充。ADR pass：00-adr-map、Accepted 96-task-execution-responsiveness、Proposed 128-local-runtime-isolation-and-bounded-query-contract。C级独立诊断，不改变产品Module/权限/Evidence/System Context或存储边界；不实施重构。P预算原文件/SHA、3 Electron槽、144根上限、原15ms/2ms门不变。

## 专用Module和验收顺序

- Marker Adapter仅在owned实验显式启用，单槽queue只增两个固定枚举clock-start/end，不接收表达式。两具名同步函数包住原生产Supervisor读，所有mode调用多重集相同；每个边界保存hr-before/performance/hr-after三戳，root业务时间保持原口径，新增metadata完整计费并纳入字节帽。
- Clock Mapper以profile原始timeDeltas与具名函数全部子树样本，分别约束profile→hrtime、profile→performance，再用每个三戳约束hrtime→performance。区间不相交、宽>2ms、缺失marker/父链一律拒绝；不借相同原点假设或放宽旧分析器门。
- Profiler Controller只拥有一次enable/setInterval(1000)/start/read-block/stop/disable生命周期。start应答未知只stop/disable，不重发start或业务读取；stop/disable/save任一失败保留原错误、partial或unknown profile及成本，不能发放结构或计时资格。save在disable后，读取错误优先保留；命令、状态、setup/stop成本及原异常均归档。
- P Result区别OFF入场、结构、计时和机制。八个dense点仍由原兼容summarizer判定；输入/图/PMC/metadata/校准同原门。OFF入场失败即结束该target；有ON时仍保留每遍、完整父链/未解析Native与GC/idle/program份额，逐遍至少10个确定样本才可比较。结构通过不代表开销≤2ms，也不能回填现场原因。

## P0先决资格（不是追加性能槽）

[独立P0机器预算](../../playbook/evidence/runtime-isolation-ri00-e3-p0-budget-20261114.json)：固定一个Node Inspector子进程、零Electron、无产品数据、无替换；90秒、fixture读体CPU8秒、控制器10秒、输出32MiB/profile16MiB，最多6次Profiler start与9个有限SHA读取fixture根。正常→start应答丢失→读体失败→stop应答丢失→stop派发前拒绝→恢复后正常六场景固定顺序，全部通过才运行P。丢应答由真实命令执行后在Adapter应答接缝注入，保留原失败，不冒称真实网络随机故障；SHA工作只验证工具与时钟，不代替现场残差。stop派发前拒绝后必须以真实disable及Profiler已禁用响应确认恢复，不重试未知start；最后正常profile验证后续准入。单元测试另外覆盖已知拒绝、save/disable失败和未知帧分类。

P0通过后按[原P冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-p-budget-20261113.json)一次固定3宿主对照；P自身任一失败不新增宿主。P0与P报告绑定独立producer/预算SHA，未通过不追补；实际Peer本轮不附着/重启。

## P0实际结果：正常与异常恢复通过，适用范围仅此producer

producer `5775b642`只启动原定1个Node Inspector fixture、无Electron或产品数据，固定六场景依次完成，未替换/补试。9个fixture根、读取CPU605.671ms、整fixture进程CPU710.340ms、控制器51.638ms、墙钟888.604ms、profile总19400字节。正常profile的三时钟交集宽0.465208ms，异常后正常profile宽1.117625ms，均≤2ms。

start真实成功后注入应答丢失：读取0根，只stop/disable；读体异常：读取1根后保留原错误及partial profile；stop真实成功后应答丢失：读取2根、原profile私有quarantine，不发资格；stop派发前拒绝：读取2根、真实disable收尾。各场景真实协议均返回Profiler已禁用，未重试start/read；最后正常profile证明同一Node进程后续可准入。原失败是明确Adapter接缝注入，不冒称自然网络故障。退出owner恢复、未ACK/保留字节为零、Node正常退出。P0不等于Electron的Profiler时钟/成本实测。

## P原执行：预算准入算法错误，中途封存

同producer `5775b642`启动共享reference和target-1，原3槽只用了2槽；第三槽未启动，本次余槽作废而不挪用。每host8个预热+固定clock-start/dense8/clock-end，共36个Supervisor根；没有任意加读。第一组OFF实际所有图/源/PMC/metadata/校准门通过：target/reference暖兼容5/7点，极差12.637/12.487ms，中位270.423/275.201ms，差−4.778ms；校准比1.005207。不能因为此快态就解释旧残差。

Profiler启动前，控制器抛`p_complete_return_reserve_unavailable`，随后走既有恢复并结束整个实验。**P未完成固定三宿主OFF/ON/OFF，也没有P profile；不将未执行的ON/返回段补为阴性或通过。** 两host18根/各，最后2次单独Evidence语义审计均69266条且SHA等于父记录，完整计费。墙钟24.310秒、产品读取CPU18.662639秒、hash133.197ms、controller/aux含5秒准备关闭reserve为5.498650秒；没有超原90秒读CPU或15分钟墙钟，也没有unknown成本。原报告failed/SHA及两次正常exit不改。

### 直接可证的工具错误

代码误用“所有已读根的最大CPU”估计40个未来暖根，再乘1.5。最大值来自reference第一预热根2117.35ms（target第一根2002.03ms）；于是每根预留3176.025ms，总预留`40×3176.025+1500=128541ms`，而原时点剩余读取预算71600.256ms，必然拒绝。**这是预算预测把冷启动成本错误推广到暖段，不是实际预算耗尽、Profiler成本或应用慢化机制。** 冷根实际GC/堆记录仍留存，不因修正预测而从已花费账扣掉，也不将其GC签名当作现场原因。

保留失败后，`66226f35`将预测basis明确为已通过原门的两个完整OFF块（包括2×2个时钟读、首个dense点和其余所有dense点，不挑点），块内最大CPU454.204ms；原下界750ms和1.5系数、40根/1500ms语义审计预留均保留。离线封存回放得到31500ms预测预留，仍是**未来成本的保守计划假设，不是可保证上界**。剩余controller参数由最终累计已知成本推导下界19501.35ms，不伪称原时点精确量。V1回放用了保守取整19500ms，V2明示推导与原V1 SHA，两者不改原实验。随后`6aeaefbd`还把固定120秒墙钟猜值替换为完整返回预留：90000ms清理+31500ms读体/语义审计+36×150ms根间隔+5000ms控制器余量=131900ms，V3封存回放验证，预算上限不变。新增断言明确120000ms必须拒绝，不放松门；当前remainingWall876102ms可满足此预测，仍非实际未来执行证明。

回归覆盖冷根不被反复乘算、完整40根返回预留、不足预算和原OFF失败仍拒绝；90秒/15分钟及15ms/2ms/10%门都未改。另把marker外侧三戳的CPU计入probe累计、profileStarted只记录实际start事实。这些是诊断候选修正，**没有重新执行P0/P，没有新宿主/取栈，不能冒领`5775b642`实测给新candidate**。新candidate的same-producer前置校验仍会拒绝直接拿旧P0运行。

## 数据、恢复和验证收据

[机器收据](../../playbook/evidence/runtime-isolation-ri00-e3-p-results-20261114.json)绑定P0/P原始SHA、两预算SHA、V2离线回放与完整副本审计。8534个内容文件及1空fence与原manifest逐项相同；两Electron和P0 Node均已退出，owner/method/binding/队列与未ACK字节恢复，guard拒写/读取错误/metadata丢失为零。额外封存审计CPU653.924ms单列，不混入原P报告墙钟。实际Peer本轮零附着/重启，原进程存活、无诊断监听。

E3原已用27个owned Electron，本轮实际加2为29；P0独立Node fixture不冒充产品读取。新增产品读体18.662639秒，累计已知下界352.596809秒，旧C未知成本继续unknown。第三未用槽不兑换新reference/target，不续跑同类进程追绿。

聚焦测试首次83/84：新fixture将n/12重复相加产生202.99999999999997，严格203断言失败；保留日志，改为可精确表示的fixture输入，未改断言或性能门。P0前84/84通过；预留修正/marker计费后86/86通过，最后只清理未使用变量并syntax/diff检查、追加3项最终预留回归通过。architecture/UI/diff通过；三个candidate查询PR workflow/status均为空，不称CI绿。自审，未跑完整build/产品/模型或安装release验收。

## 目前的硬门

原P预算要求预留完整返回段，但具体预测公式在实现时引入，且执行前未用封存冷根验证其可行性，这是本次设计到实施检查的遗漏。修正公式、36个间隔和全部余量已明确记录，后续不得在执行时临时选择。

本次没有完成用户要求的整个P对照，根因是上述取证工具预算算法错误，不能把这种工具失败包装为性能资格失败。修正候选只经封存回放和聚焦验证；完整Electron三时钟/1ms成本/OFF返回对照仍未验证。不能借本次余槽追加应用或复写P原失败，后续任何完整执行都需单独明确预算和source绑定。自然现场同进程快→慢及机制复现仍缺证据，RI-00未闭合，不进入现场窗口或重构。
