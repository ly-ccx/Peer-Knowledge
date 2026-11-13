# RI-00 E3-N：逐遍工作量与热点取栈资格

2026-11-13，执行前设计。C级诊断，沿用`00-adr-map.md`、Accepted `96-task-execution-responsiveness.md`及Proposed `128-local-runtime-isolation-and-bounded-query-contract.md`；不移动产品契约，不启动重构。父证据是[E3 K/A](runtime-isolation-ri00-e3-qualification-followup.md)。本文件不把旧16.182ms或旧现场30–40ms事后补成有栈的事件。

## 已知边界与可证伪问题

K的同GC落点暖点Evidence用户CPU差16.182ms：逐位置差为0.830、0.545、1.476、2.104、0.851、5.066、−0.082、1.629、0.192、1.451、0.318、1.802ms。最大位置只占31.3%，其余11.116ms分散；整根另有5.703ms用户CPU差不在Evidence跨度内。整窗多201,762,107条指令（2.4895%），既没有逐遍计数，也没有热点执行栈。GC wall重叠不是GC CPU，不能拿它相减。相同minor落点仍容许不同VM工作，不等于证明GC原因或核频原因。

N先回答工具能否把新增工作定位到12遍及根内余部，随后才问哪条栈增多。阶段不混合：第一阶段只加边界计数，不启动Profiler；第二阶段单独改变Profiler开关。Profiler状态下的数据不能成为无Profiler的G2快慢资格。旧归档粒度保持固定，不再检验。

## 计数Module与归属

owned宿主用一个只读Node-API C扩展，对当前进程/当前线程调用已验证过的libproc flavor34。不使用task port、优先级、硬件配置、VM参数或强制GC；不采用尚未验证的另一私有ABI。初始化核对性能层数、struct长度/保留位、线程身份、时间基准；每次读取都核对ABI并保留逐层instructions/cycles/user/system ticks。非单调、换线程或未知成本直接失格。

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

F控制器须经过真实owned队列/归档接缝和异常路径验证：F0及heap-free pre-F1，F1已慢拒绝而非重学；60秒静默、5根固定自然基线，first-witness先于heap/native/profile；single-slot及fsync后ACK；Q1/Q2用原G2，所有预算继承C1/C2而非重新置零；source/owner变动、RPC未知、取消/超时/断连/预算耗尽均封存并恢复，未ACK原件保留。只测纯signal不等于全控制器通过。任一门未过，F不启动。

实施结果、失败、候选与回收实测另回填，不覆盖父回执。RI-00闭合仍需现场同进程快→慢及受控机制复现；本轮工具通过也不能称根治。
