# RI-00 E3-C：384遍审计、现场控制器与热点资格设计

2026-11-13，执行前冻结。C级诊断，已过`00-adr-map.md`、Accepted `96-task-execution-responsiveness.md`与Proposed `128-local-runtime-isolation-and-bounded-query-contract.md`；不改产品、授权、Evidence、存储、System Context边界，不实施RI-01。父记录[N及原失败](runtime-isolation-ri00-e3-pass-work.md)不改写。

## 封存数据先行

先核验N原报告SHA及producer，再对全部32个ON根/384遍解码。区分Evidence用户CPU、内核CPU、线程总CPU、wall、instructions、cycles；不把其中一种差额替换成另一种。逐层、逐遍与root余部分开记录，OFF没有逐遍PMC，不补零推算。

对21个按时间先后的同GC兼容配对，采用恒等式`T=I×(C/I)×(T/C)`的对称log-mean分解。三项分别是指令工作量、每条指令周期、每周期线程CPU时间的记账项，和必须等于实测线程总CPU差。不是因果分配、硬件频率或GC成本估计；用户/内核时间变化另列。不同GC极差及跨块边际中位只作描述，不能升级为同GC配对或机制。

N开关并非原设计声称的单一native-call因素：ON每根多52次返回JS对象的`threadCpuUsage()`调用（是否都落实为物理堆分配未测），且计数值转字符串/JSON比OFF全零buffer多约2.4–2.7KB。归档在root后也会改变下一根之前的分配历史。事实可由source及封存字节数验证，**其导致多少CPU差尚未被实验证明**。OFF本身最大24.232ms暖极差，两个mode都有不稳定块，ON−OFF四个比较正负不一；不能把2ms拒绝称为native本体固定开销，或叫无害噪声。不能据此放宽2/15ms门或重跑N追绿。

## 控制器Module与真实接缝

| Module / Interface | 事实owner及顺序 | 故障与恢复 |
|---|---|---|
| Inspector Attachment | PID/OS birth+监听差集+node endpoint+CDP PID校验；不默认9229，不继承旧listener；固定metadata操作白名单 | 未找到endpoint也必须重新盘点实际PID，未知不能当没打开；目标端口refusal且原进程alive才恢复完成 |
| Durable Ticket Reader | 单slot、单调id；提交metadata→target setImmediate→同ticket完成→PMC/row/entry归档fsync→依次ACK | request应答未知只查原id，不重新request；归档失败不ACK；failed/expired照录；不把RPC成功当读取成功 |
| Field Controller | 锁source/birth/owner→原F0→60秒静默/最初5自然根→heap-free main/ref/main→原F1；F1有效已慢直接第二确认，不能丢转换；常规signal→前史fsync→首见证→Q1/Q2 | 每阶段检查累计预算、源/owner、取消/截止；任何epoch变化即封存，不rebase/重学；新事件清零streak，最多2不同exposure，不跨事件拼确认 |
| Field IO Adapter | 同一个CDP fixed-call接口驱动owned和未来实际Peer；checkpoint仍复用原evaluate/qualified gate、每host独立时钟/PMC；自然包先归档再交policy | 零heap首见证先于dense/hash/profile；所有已发起读计费，unknown成本保留；stop保持未ACK原件，不覆写后来owner |

controller不直接取profile，已确认转换只交出候选和封存前史。热点工具未资格验证前不能隐式启动。纯数值/虚拟时钟只验证状态机，明确`notFieldCause`；不得与真实快态/机制回执混放。功能Electron可使用这些fixture门并通过真实CDP/queue/journal取证顺序，但不声称真实G2阳性。生产Electron使用实际G2；若F0拒绝，验证安全退出并保留，不由fixture强行放行。

## C/M新预算（本次可执行）

[冻结机器预算](../../playbook/evidence/runtime-isolation-ri00-e3-c-budget-20261113.json)。C固定3次Electron启动：1个functional（随机端口/完整controller接缝/异常恢复）+1个production target+1个reference，最多2同时存活；总墙钟10分钟含90秒清理、全部产品读体≤60秒、hash≤1秒、probe≤5秒/host、控制器/辅助CPU≤20秒、准备与关闭另保守预留5秒、输出128MiB、journal32MiB/未ACK16MiB。失败占槽；不能补N、替换宿主或用剩余额度做性能因素搜索。源/图/成本unknown即封存。

生产验证只做一次完整controller：实际F0可能拒绝；若通过，按真实60秒静默后5次owned普通只读入口建立学习，再heap-free首见证与F1，后续最多一个短有界无新增exposure包；不跑现场等待、顺序曝光或机制。所有这些入口明确owned输入，不称用户自然现场。

M另有1次当前已运行Peer附着、零启动/重启。仅在owned随机端口、清理和controller接缝通过后执行；active≤30秒、清理≤15秒、controller/子命令CPU≤2秒、main整窗CPU上界≤5秒、≤1000 RPC。实际装配在同一次同步CDP调用内install→renew→stop→方法/notification/global owner恢复，不让正常业务事件在中间被诊断器调用，不执行主动查询。五实际注册入口与可信外层前后身份核对；release remote对象组；实际端口refusal/原进程存活。缺任何一项保留失败，不追加附着。准备区间不是完整现场前史；主线程窗口不能计量则unknown，实际不会强停。

## 热点单变量对照与独立预算（冻结但不执行）

N仍拒绝，不把其native探针带入热点/实际Peer。H两种模式均完全不加载native库，只用已资格验证的JS逐遍CPU、原G2、整根外部PMC和真实函数时钟见证；唯一处理是Profiler以1ms start/stop。source、输入、调用多重集、间隔、逐点durable排空、默认VM、原heap统计和返回投影均固定。不得加preciseCoverage、trace/GC/JIT flags、强制GC、人工耗时。

固定2个target+1共享reference（3启动，不替换），每target固定OFF8→ON8→OFF8、两次真实读时钟见证分别包住profile块；Profiler每target只启动一次，profile读取wall≤6秒/host、启动/停止实际CPU≤1秒/host，计费完整。每块首点及每遍都保留；前后OFF各自原兼容≥3/极差≤15ms，校准10%/元数据2ms/PMC专属性不变，ON−OFF变化不按比例扣掉。任一工具门不通过则该profile只保留结构与未知份额，不能产生G2/机制结论，不挑绿点。

完整路径包括root余部与12遍；节点exclusive样本估计不与inclusive父节点重复相加，GC/idle/program/native未知节点保留。profile→hrtime→performance通过两次真实生产读得到共同区间，宽≤2ms才允许逐遍比较；每个用于比较的跨度至少10个确定样本，稀疏/边界不确定/未知份额单列。最多1个profile块，不因样本不足增加读取。wall样本份额不等于函数指令份额。

H总墙钟15分钟含90秒恢复、产品读体≤90秒、控制器/辅助≤20秒、准备关闭另预留5秒、profile≤16MiB、总输出128MiB、journal32MiB。没有本轮执行许可自动转入H：先完成C/M并封存取栈controller的真实时钟/start/stop异常验证，再按此独立固定预算执行，不能借F/R槽。原15ms资格不能被结构profile绕过；未来现场形成仍必须原G2 F0/F1/Q1/Q2，未带profile指标不得由profile推回补齐。

C新增3与H保留3将E3 owned计划帽36→42、活动执行墙钟帽127→152分钟；实际花费另记，旧已用20启动/282.034817秒读体、C1/C2累计与unknown不清零。M预算独立记账，不混作F的30分钟自然窗口。未获得现场同进程快→慢及机制复现前不重构。

## C原执行封存：不能用后续候选追认通过

producer `19bebc6a`恰好使用3个固定启动，C0四场景通过真实CDP/queue/journal：完整policy顺序、F1有效已慢分支、request应答丢失、真实写入后的注入fsync失败；各阳性gate是显式fixture、reference为逻辑替身，不是G2或现场形成。断开真实CDP后，原controller recovery-unverified结果保留；lease恢复方法、端口refusal且宿主alive，随后只归档/ACK原ticket，不重放查询。

两个production宿主启动后，在首条生产batch归档之前发生CDP `Promise was collected`，原日志没有operation字段，不能事后补出失败的具体RPC。controller没有取得真实F0，不能用C0代替。两个stderr均出现`Waiting for the debugger to disconnect`；代码却先等待host.exit、随后才disconnect，构成直接可证的收尾等待环。它不是旧30–40ms机制或应用自然多秒停顿。

按PID父子身份核对，仅终止本轮自有的2个Electron及4个Helper；原Peer未动。墙钟501.790秒，3启动全部消费；报告仍failed，原数据/错误/外部恢复单独封存。已知读体下界4.293683秒（含两次生产bootstrap选择），target没有完整exit/controlled成本，未计部分为unknown，不称在60秒帽内。counter EOF成本已知，controller/aux含准备reserve为5.677368秒；这是其已计范围，不填补target缺口。原C不足以准入现场，M当时未执行。

## D：针对取证工具故障的新单变量资格，执行前冻结

修复候选把CDP普通返回改为同步值；异步take保存在site持有的单槽中，外部轮询完成值，durable ACK后释放；不依赖CDP对临时Promise的await。每次错误保留operation，原C的缺口仍不回填。另把disconnect移到exit之前，并为自有host关闭设置强制截止；不能作用于实际Peer。审查同时发现long probe.stop清空未ACK的pendingTake，在cursor已推进时会让再次take漏掉原batch；改为stop保留原Promise直到ACK。真实Node CDP与停后重取同一batch的回归测试通过，没有强制GC或更换VM参数。

[D冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-d-budget-20261113.json)是新的工具故障隔离，不占/重算C或N：固定2个production/reference、最大2同时存活、零替换，墙钟6分钟含90秒恢复、读体≤60秒、native hash≤1秒、控制器/辅助≤20秒另5秒reserve、输出128MiB/journal32MiB。source、输入、sampler、默认VM相同；target先固定legacy-await / retained-poll / retained-poll / legacy-await，每块2根，唯一因素是CDP transport Adapter，非性能开关。任何错误只归档并恢复同ticket，不补读该失败点；按原定8点做完，不能挑绿返回块。若legacy没有复现，原Promise原因仍unknown；poll失败则该候选资格拒绝，无新增进程。

随后仅一次真实G2/controller生产接缝验证，复用已封存C0的功能覆盖，不能把旧C改为passed。原15ms/校准/PMC条件不变，F0拒绝时验证安全封存，不增加F0追绿；若F0通过，仍按60秒+5owned普通根及F1既定分支。zero profile、zero N重跑、zero 顺序曝光。D额外2启动将计划帽42→44、执行活动墙钟帽152→158分钟；旧已用23启动及C unknown保留。M只在新传输/关闭接缝与同栈装配通过后，使用原预留的一次实际附着，不另开次数。

## D实际结果与E最后固定资格

`eb4e1f65` D按legacy/poll/poll/legacy各2点做完：4个legacy全部在status复现`Promise was collected`，4个poll全部完成；错误点只归档/ACK原ticket，未补读。返回legacy时仍失败，支持改掉CDP await普通status返回这一具体传输原因；原C没有operation，仍不能事后声称其同一具体RPC已被记录。随后生产控制器尚未到F0，在预热阶段因2048条command trace上限停止。D整体failed，不能只取四个绿色poll点当完整控制器通过。

D共2启动、墙钟13.398秒、读体11.734507秒、controller/aux含reserve5.634807秒；两个宿主均有完整exit，方法/binding/队列/原件恢复，正常退出，没有强停或unknown成本。关闭先disconnect的修正得到了实际生命周期验证。失败也显示2ms状态轮询会生成大量控制命令；其main插入成本未独立计量，不能称低干扰，更不能用这个**新控制器**的行为解释N或既有现场残差。

E改成target queue完成/失败/过期的结构化终态触发一个owned Runtime binding；client等通知后只查一次真实status。通知只是唤醒，不替代ticket事实；超时仅查同id一次，不新建查询。通知函数owner、卸载/晚到owner、CPU单列，stop保持未ACK原batch。trace按重复operation RLE而不是丢弃失败；source/16MiB/32MiB上限不变。真实Node Inspector+真实queue验证单次status与binding删除；首轮测试发现不支持通知的fixture残留binding，已保留失败并修为先查支持、原生函数对象相等才删除，未放宽零泄漏断言。

[E冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-e-budget-20261113.json)仅2个production/reference、6分钟含90秒恢复、读体60秒/hash1秒、controller/aux20秒另5秒reserve、notice CPU≤1秒、输出128MiB/journal32MiB，零替换。**不再执行D八点或N开关**，只验证新事件驱动接口、一次原F0及其既定后续/安全拒绝、同栈装配和恢复；若E再失败，本轮不增加app槽。旧C/D报告都保持failed。E只可能得到工具资格，不产生现场形成或机制归因。

E把计划帽44→46、活动执行墙钟158→164分钟，实际旧25次启动、C unknown及全部原始失败不清零；H仍冻结未执行，M仍只使用原预留一次。未通过E时不进入现场，也不借剩余H/F/R启动。
