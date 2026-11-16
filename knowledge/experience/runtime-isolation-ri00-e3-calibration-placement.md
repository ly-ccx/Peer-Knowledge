# RI-00：校准排布执行、原始接缝及无效对照封存

创建时间：2026-11-14
最后更新：2026-11-14

## 结果与边界

[冻结设计](runtime-isolation-ri00-e3-order-variation.md)、[原机器预算](../../playbook/evidence/runtime-isolation-ri00-e3-calibration-placement-budget-20261114.json)未修改。执行候选`55675ca5cef5439b3fa6d4768c3bc9508b103b0a`完成固定三宿主、两个target的ABBA/BAAB，共184根、16块、8格、57次native SHA和3次语义审计。没有补进程、改变15ms、加Profiler或接入实际Peer。

**本轮诊断对照无效（invalid）**：顺序、校准位置、间隔、原调用图/输出、PMC/metadata及校准比控制通过，但同arm返回超原2ms门。返回失败不是程序执行异常，原report的failures=[]不能表示诊断通过，正式CLI按规则退出1。原15ms逐块暖段分类完整保留，本轮不输出F0通过、快态baseline、性能或现场资格。

四个A中两个≤15ms，四个B中两个>15ms，四个固定极差改善也未全达5ms。坏基线并未全复现，且返回控制先失效，因此不能将结果重命名为“假设不支持”的有效反证，更不能归因于排布、GC或频率。原84根五处失败及所有更早失败保持原判；现场同进程自然快→慢与机制复现仍缺，RI-00不闭合、不重构。

## 同候选装配、数据与接缝

C级隔离诊断，按Accepted `96-task-execution-responsiveness.md`和仍为Proposed的`128-local-runtime-isolation-and-bounded-query-contract.md`，产品Module/权限/Evidence边界未移动。

复用原`run-e3-pair-order.mjs`自有宿主、持久单槽、原始journal、线程计数器和清理，预算kind选择冻结的诊断流程。新增`e3-calibration-placement-controller.mjs`拥有固定动作序列与等待窗，`e3-calibration-placement-result.mjs`拥有原门投影及诊断判据；不修改原F0准入Module。binder拥有同候选/数据身份，审计器只重放原事实。native尝试先写durable记录，成功后分别计费及归档；RPC应答未知不重试，归档失败也不把已知执行降格成未执行。全部返回与尚未开启target的预留使用已完成的所有根，未过滤慢或GC不兼容点。

实现静态自审在专用Node前修正了旧seal键名和未装notification binding的资格断言：原seal的字段是journal，不是primaryJournal；资格现明确安装自有notification以验证恢复。这两处修正在候选冻结前完成，没有消费额外Inspector或Electron资格。两次合成定向测试日志保留，随后最终同候选聚焦143项通过，覆盖原顺序执行器、旧244/84审计、原队列与恢复、整段预留、排布/时间方向及序列化重放。

唯一一次专用Node实际打开随机Inspector，2逻辑host、44次合成读取、19次已执行native/20次RPC尝试（含未ACK原ticket上的已知拒绝零SHA），验证A块末/B窗前2、5、8，150ms等待只睡余部；fsync失败保留原票据、未知request查询原id、失败读后后续准入、最后native丢应答不重试及停止ledger。原方法、notification/completion binding、queue/retained状态恢复，关闭后原端口实测拒绝连接。无Profiler线上命令，输出535126字节<2MiB，完整返回wall7464.625ms<30秒。

[启动前绑定](../../playbook/evidence/runtime-isolation-ri00-e3-calibration-placement-execution-binding-20261114.json)已在启动任何Electron之前封存提交。143项结果、Node原报告与完整返回费用、原84根report/journal/audit、纯动作图、生产Module及8534内容文件+1空围栏、源码清单SHA同候选绑定。旧38个owned与历史未知/失败成本没有清除，新预算仅使用原定3个新槽。

## 逐格原暖段门

单位ms；使用原首metric保留但不计暖统计、64MiB、major/incremental0、其它线程严格<120ms、兼容暖点≥3及15ms门。本轮16块各有6或7个兼容暖点，不以删点或GC wall扣除补门。表中值来自原report并由原journal连接重放。

| target / 格 | arm | target极差 | conditioning极差 |
| --- | --- | --- | --- |
| 1 / 0 | A | 13.942 | 10.379 |
| 1 / 1 | B | **16.869** | 13.614 |
| 1 / 2 | B | 8.587 | **15.678** |
| 1 / 3 | A | **19.120** | 12.377 |
| 2 / 0 | B | 12.022 | 11.516 |
| 2 / 1 | A | **15.271** | 14.295 |
| 2 / 2 | A | 13.053 | 13.347 |
| 2 / 3 | B | **16.460** | 13.198 |

本轮5处原暖段超门为4 target、1 conditioning；它们与旧84根的3 target/2 conditioning是两组原件，不能合并改判。固定四对A−B极差改善依次−2.927、+10.533、+3.249、−3.407ms；没有统一改善，也不因其中一对改善重新选择对照。

## 返回漂移：目标与条件宿主分开

每个joint锚点按原Evidence用户中位同一根/相同权重选择，用户/内核/合计及root I/C共用该锚点；归一化为target减conditioning。下表同arm后一次减前一次，单位ms；绝对值>2即失败。

| target / arm | 原格 | raw target用户 | raw conditioning用户 | 归一化用户 |
| --- | --- | --- | --- | --- |
| 1 / A | 0→3 | +0.1785 | **−9.7210** | **+9.8995** |
| 1 / B | 1→2 | **−8.8670** | −1.5955 | **−7.2715** |
| 2 / A | 1→2 | +0.5370 | +0.2360 | +0.3010 |
| 2 / B | 0→3 | −1.8425 | **+3.6450** | **−5.4875** |

六个独立域/arm返回值超2ms，对应target1三项返回控制、target2两项返回控制失败。target1/A的归一化变化主要由条件宿主向下漂移构成；target1/B主要由目标向下漂移构成；target2/B是目标下降与条件宿主上升共同形成。这里是中位锚点代数贡献，不是逐遍VM/GC成因；conditioning不是未处理且稳定的参考，不能用归一化值掩盖raw失败。

## 校准位置和真实间隔

全部块顺序实际为target→conditioning，两target顺序分别ABBA/BAAB。57次native由57个durable尝试及成功记录一一对应；9次初始化均在各host8根预热之前，48次块内工作中，4个B target的12次落在原序列index2、5、8之前，其余36次在各完整块最后一根之后。每次仍16轮×4MiB；开始/结束均不与该host任一root重叠。journal跨host动作和await边界核对没有另一个root插入native尝试/完成之间，不比较不同host的performance时钟来伪造先后。

16块共144个真实内部间隔为168.403166～217.282042ms，均≥150ms。四对target间隔中位差为2.472333、0.437000、0.606416、1.124667ms，均≤5ms。记录请求窗及实际间隔，不把150ms设定值当作真实间隔。各target/conditioning SHA比相对公共初始化基线漂移≤10%，没有用比例重算用户CPU。

[机器收据](../../playbook/evidence/runtime-isolation-ri00-e3-calibration-placement-results-20261114.json)保留每块原门、raw/归一化joint锚点及用户/内核/合计、逐层外部指令/周期的原件引用、每次校准位置和全部间隔；完整原件在私有report/journal，摘要不重复保存业务payload。原始184个外部PMC均从线程边界重算一致，16个块起止、所有ticket与57校准位置重放一致，重新计算出的invalid与原结果相同。机械和归档结构通过不等于低干扰/诊断有效。

## 成本与恢复

正式产品读CPU83054.305ms/200000，含184根用户75821.112ms、内核6829.467ms、合计82650.579ms，以及末尾3次语义审计403.726ms；native1273.902ms/4000。正式wall118262.256ms/900000；父进程等待完整返回及输出/fsync后为118503.626ms，尾段241.370ms另保留。完整已等待子树用户99207.681ms、内核10508.967ms、合计109716.648ms；包含宿主启动等工作，不能和读体重复相加或当作Evidence CPU。

准备完整子进程CPU3795.778ms，已测三个阶段wall合计9586.901ms，加收据阶段保守预留30000ms，共39586.901ms/120000。按预留计算总活动wall157849.157ms/1020000，计完整正式返回后158090.527ms；controller运行4055.193ms、counter最终224.321ms、准备3795.778ms及关闭预留5000ms，aux计13075.296ms/25000。正式输出16923607字节，含准备总17566259<128MiB；journal6677087<32MiB，恢复journal0。离线封存重放另耗完整CPU111.900ms、wall133.022ms；连同完整返回及准备预留计总活动158223.549ms，aux加该审计为13187.196ms，均在帽内。没有预算超限或未知成本被当0。

三个Electron均正常exit0，所有原方法owner、notification/completion binding、queue ticket/inFlight、retained/unACK均恢复，metadata/drop/GC丢失/ledger overflow为0，sourceWritesDenied0。3次原始69266 Evidence语义SHA一致，8534文件+空fence及生产/诊断源码首尾不变。counter EOF与最终CPU已知；3个Electron端口和1个Node端口均实测拒绝连接。143项通过，CI查询无workflow/status，不称绿色CI；自审非独立评审，没有产品build/release、真实模型或现场验证。

累计实际owned从38到41，已知产品读CPU下界由552064.684ms到635118.989ms；旧C未知及全部旧失败保留，三槽均已消费，无替换额度。完成的是一次固定、可审计的排布对照；得到的是返回控制失败和坏基线不全复现，尚未得到现场剩余残差机制。下一步需要先用本轮封存数据拆开返回漂移的形成贡献，再冻结新的单变量与额度；本轮不启动新实验或重构。

## 取证策略复审

用户要求停止资格对照循环后的[共同失效审计与FR1直接现场方案](runtime-isolation-ri00-evidence-strategy.md)重新审查本轮返回锚点与历轮证据，保留本轮invalid及全部原门，未再次执行校准排布或新采样。
