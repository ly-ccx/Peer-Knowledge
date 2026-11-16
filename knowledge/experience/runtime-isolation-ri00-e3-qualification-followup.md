# RI-00：封存F0拆解与补充资格对照

2026-11-13。状态：封存审计、两个A资格槽、三个K对照槽均已收尾；K不支持归档粒度的预定充分原因，未进入现场。C级诊断；沿用`00-adr-map.md`、`96-task-execution-responsiveness.md`及仍Proposed的`128-local-runtime-isolation-and-bounded-query-contract.md`，产品/权限/Evidence/存储/System Context边界不变。不是重构或现场开工许可。[原Q/H](runtime-isolation-ri00-formation-e3.md#9-本轮实际qh收据与现场准入结论)及[本轮封存审计与冻结预算](../../playbook/evidence/runtime-isolation-ri00-e3-f0-audit-20261113.json)分别保留。

## 1. 先查封存点，不增加产品读取

原H报告SHA与已提交回执核对后，重算18块、144点，排除每块首点得到126暖点，按原门保留115个兼容点。另11暖点因major/incremental或其它线程CPU拒绝，未删除原始点。10块极差超过15ms，分布在六个F0；不是每一块都不稳定。

18块的兼容最高/最低Evidence用户CPU点，已观察root minor GC次数均分别为12/11；更关键的是GC与12个Evidence调用的重叠位置不同。例如C1 main-A最高点11个Evidence跨度观察到minor，最低点只有7个，Evidence用户CPU差18.797ms，整根用户CPU差12.781ms，根外于Evidence的用户CPU反向变化−6.016ms。计时边界内外的分配/回收相位不能忽略。但这里只记录相关性与成本迁移；GC记录是wall重叠，不能从user CPU减掉它来证明精确GC成本。

仅按root minor次数分层仍有三块超过15ms：T1 main-B同12次组19.707ms，T2 main-B15.610ms，T3 main-A16.973ms。根GC次数也不等于Evidence内GC位置相同。细分到逐位置GC签名通常只剩1–2点，不具备独立验收样本量，不能靠事后分层替换15ms门。T1 main-B的最高/最低整根指令相差约0.99%、周期相差4.58%；T3 main-A对应周期仅相差约0.41%、counter CPU却增加约16.28ms。根内工作量与执行速率代理均变化；PMC只包住整个Supervisor，不能把它们拆成Evidence内部指令/真实核频，也不能断言是哪种系统活动造成。

兼容点自计元数据CPU为0.662–0.993ms；Efficiency层主线程CPU最多0.266ms。没有证据支持“此次暖段极差由主线程大规模转去E核”或简单的元数据CPU相加；这不证明采样器没有状态影响。18块全12遍CPU向量与GC位置保留，不只看中位数。H相邻根间隔161.919–166.344ms；旧C2夹测约154–157ms。两版都明确等待150ms，故不能把“新加了150ms”当解释；新增差别包含排队调度和每点take/序列化/fsync/ACK，跨窗口差异本身不是因果证明。

目前能闭合的是拒绝项来源和观测到的结构：GC进入哪个调用边界不同，加上整根工作量/执行速率波动；尚不能证明这些相位为何形成，更没有解释旧30–40ms。先检验一个确实在两版测量程序中不同的因素，而非同时改预热、间隔、heap、VM或样本数。

## 2. K：只改变排空归档的粒度

唯一因素为probe `take/ACK`：A每点排空，B每8点块后排空。两者都保持同一个setImmediate单槽队列、原生产读图、heap统计、150ms等待、每点PMC、块末3次原生校准、同源输入/输出和默认VM。每个ticket完成记录在ACK ticket前fsync；B只延后完整row batch排空，最多8行，仍受16MiB未ACK上限。没有把完整业务数组传回或留存。A/B都使用相同的完成ticket日志，因此不会把durable ACK与unsafe ACK作为混杂因素。

固定2个target及1个常驻参照，target-1按A/B/B/A，target-2按B/A/A/B，每宿主8次相同预热；每checkpoint仍main-A8→参照8→main-B8。每target四次完整checkpoint是本次归档粒度资格对照，不是原H补样本，不实施Evidence顺序曝光。两种模式都完整跑固定顺序，原失败保留；只有身份/未知成本/预算/元数据损坏立即终止，没有看到绿就提前停、重排或追加。

K使用封存`8cfb68f0`的probe/queue/installer精确源码，不加载A新增入口包装或hook。本轮先冻结K设计，A的功能/映射验证可独立推进；未执行K不得写成K通过，也不能据A通过进入F。后续K须先补齐控制器与counter全程成本收据，不能把旧helper未计量边界按零补账。

支持“逐点排空足以造成本数据资格失败”必须同时满足：两个进程各两次A均仅因暖极差拒绝；各两次B均通过原fast资格（包含所有块≤15ms、校准、PMC、图和差额）；每个进程A/B的最大块极差中位改善至少5ms；A返回时重新失败。任一不满足就不支持这一充分原因，不能把最后一个B绿色挑出作现场入场证。若A/B均失败或时间顺序决定结果，继续保留unknown，不自动改成预热或另一个因素矩阵。

K支持也只说明本测量程序的资格影响，既不说明旧残差，也不自动恢复H形成证据。原六例仍是0/3，不重算。现场仍须自己的F0/F1及自然前史。

执行前细化：B的完整batch在8点及块末3次原生校准之后排空；A仍每点排空。每种模式两个“最大块极差”的中位在本对照中定义为两值算术平均，改善必须≥5ms。当前新增入口代码不进入K；从git封存candidate逐文件核对后装配私有采样bundle。装配只允许一次≤5秒的git archive，外部准备CPU按5秒保守占额；counter沿用封存的read(pid)函数源码，只由单线程Python launcher附加自身累计CPU及EOF最终收据，正常关闭≤1秒，另按1秒CPU保守占额。准备、counter、控制器连同A已用1.808026秒一起受共用20秒帽约束；缺EOF/超时强停/成本不明使K失格，不能按零计。counter真实只读接口预检不执行产品查询，单独记验证范围。

## 3. A：入口与信号适配器合同，验证后才能谈现场

实际注册入口限定五个IPC（list/get/list-sessions/get-session/list-obligation-grants）和Directory.list根。必须从实际注册handler的具名闭包定位ports、service、Directory与Supervisor，记录对象相等性和未覆盖项。源码显示Directory.list使用`Supervisor.listByWorkspaceIds`，只包装`Supervisor.list`会漏掉该读者；get/getSession也不能从方法名推断和list相同的读图。不得以空Directory stub的通过冒充生产映射。

Adapter只包装已定位的原函数，保持receiver、原返回值/Promise和原异常；原权限校验链外层不动。入口元数据只含枚举shape、递增seq/parent、epoch、起止与有界首签名栈，不存参数值。同步嵌套与异步父链区分，无法关联的根明确unknown；不把相近时钟推成父子。Directory.list在IPC内为子入口，根外才能记tray-compatible目录根，不能单凭目录被调用宣称用户点击了tray。列表批读必须记录实际命中的reader identity，根外index继续归档；只声明已装配范围。

Signal Adapter消费已归档行，不执行产品查询。固定F0后60秒静默，再用最初5个同源完整自然根的全12遍用户CPU中位作基线；不筛掉minor/major/incremental位置、不滚动重学。单根≥+12ms且≥4%或wall≥2秒只产生signal；单遍+6ms只记定位；新的已映射入口/端口顺序可准入一次首见证而不要求CPU升高。单槽busy合并原因但不追加查询，最多2个不同exposure、无新覆盖8分钟终止；源/产物/owner变化、记录满额、RPC不确定即封存。首见证→旧Q的前后次序不能颠倒，signal不等于G2确认。

固定两个owned验证槽：一个functional Electron验证getter、receiver/Promise/error、同步/异步父链、重入/忙槽/期限/源与owner失配、先fsync后ACK、lease失联恢复；一个生产只读Electron用封存输入、真实服务/注册Module及Directory查询接缝验证五入口与batch reader映射、index顺序、自然信号及方法恢复。没有Runner/模型/写入口；其它不参与映射的消息/审批等依赖明确是空只读替身，不宣称完整Desktop运行。合成CPU数字只在纯策略测试，显式notFieldCause，不向宿主加耗时。生产自然数据若没有signal，只验证它未错误触发，不能伪造形成。

两个槽的原始失败各占预算，不能改名补槽；方法/绑定/队列/端口和源恢复不确定则资格失败。现场Inspector装配仍须核对当前实际对象和安装产物；无法证明的读者标缺并拒绝入场，不能沿用owned对象身份。

生产`listObligationGrants`还会写固定诊断`logs/obligation.log`。owned接缝验证仅把这一固定log及其轮转文件、目录操作映射到本轮私有output；canonical仍经过原只读guard。记录重定向次数及方法owner恢复，不宣称入口没有任何诊断写入。不会在实际Peer安装该Fs Adapter；其普通权限链不变。该接缝的首次单测因macOS词法临时路径与realpath别名不匹配失败，原失败保存后修别名解析，未弱化“源目录无新日志/普通写仍拒绝”的断言。

## 4. 新预算及账本

用户要求设计新预算并继续补齐适配器。以下是本次新增、执行前冻结的owned额度，不挪用已用完的原Q/H，不重启或接入实际Peer：

| 阶段 | 启动、工作与截止 |
|---|---|
| K | 2 target+1共享reference，≤10分钟，全部读体≤150秒；8次完整checkpoint，共192根加24预热，3次最终语义审计计费。固定A/B/B/A与B/A/A/B；不追加 |
| A | 1 functional+1 production Electron，≤5分钟，全部产品读体≤30秒；功能lease2.5秒/外部恢复15秒截止；最多8入口/256记录/每根64段 |
| 共用 | 新增5次Electron启动，最多2个同时存活，Node控制器和libproc辅助另列；总墙钟15分钟、读体180秒、控制器/辅助CPU20秒，新增逻辑输出256MiB、总journal32MiB、未ACK16MiB；零profile、零强制GC、零VM flags、零替换 |

已用E3 Q5/H7共12次启动、读体133.290262秒全部保留；新增5次后owned计划总帽从28变33，活动墙钟总帽从97变112分钟。新增只为K/A，旧F/R的预算和门不变，不能把未花预算换成H或A补样本。F/R仍未准入；没有K的可用资格策略和完整A验证，不进入现场。成本未知或最后一次同步读越界照录并停止新增，不杀实际应用或抹掉失败。

实现/实际运行候选、失败及恢复另回填；设计文档和通过纯测试都不能冒称K/A已执行或现场归因。RI-00闭合与产品重构的门不变。

## 5. A实际执行：两槽通过，仍不是性能入场

候选`c8ee0f4f80ca90325ca4497fe97d1000646ffb54`的[实际回执](../../playbook/evidence/runtime-isolation-ri00-e3-entry-qualification-20261113.json)：两个固定Electron均通过，墙钟76.967秒，读体保守计费6.825781秒、控制器1.808026秒；没有追加。功能槽验证同步退出后才执行、原Promise/值/异常、真实异步父链、过期不读、reader与入口晚到owner不覆盖。失续租测试保留completed未ACK记录，lease恢复全部方法及binding，实际Inspector拒绝连接且宿主尚存活；本次没有杀控制器，不冒领一次新的SIGKILL实验。owner失败的false字段保留，只有owned同一进程的显式复位后续测试通过。

生产槽从五个实际注册handler的具名闭包发现并比较ports、Directory、Supervisor、goalPlanStore对象；batch与single回调都严格等于同一Supervisor，观察6类入口及真实`listByWorkspaceIds`根。8534文件及空fence前后逐项SHA/size匹配，完整23会话/3859 getPlan/12遍投影仍匹配H。源、生产Module、采样代码与父报告不变；三类JS heap getter均0、零读取失败/源写拒绝/元数据错误，方法/队列/binding恢复，两个宿主退出。固定诊断log映射3次，Fs Adapter已恢复。

生产槽真实等待60秒之后，用5根owned普通入口调用学习全12遍中位284.427ms；这些是owned功能验证输入，不是用户现场。没有给策略伪造F0/F1，`bracketed=false/events=0`保持，基线存在也不会发起取证。纯策略测试另验证CPU单根、新入口、单遍标记、单槽busy、两事件及8分钟截止。47项聚焦测试、10个文件语法、architecture/UI/diff通过；首次log路径别名失败保存后修正。已验证新增入口/信号Module及owned序列化装配，尚未验证当前实际Peer的对象发现、可信窗口外层或完整F控制器；不据此进入现场。K当时尚未执行，下一段单独封存它的结果，不能把A投影/快慢计量混进K。

## 6. K实际结果：归档粒度不是本轮的充分原因

[K回执](../../playbook/evidence/runtime-isolation-ri00-e3-drain-qualification-20261113.json)绑定实际控制器`1de20ad88c670b4675af76444b7428d91b3cfb40`和精确封存`8cfb68f0`采样bundle：2个target、1个共享reference全部完成，没有加载A的入口包装，没有增加样本。每行依次列出四个检查点的最大兼容暖段极差，单位ms。

| 固定顺序 | 第1点 | 第2点 | 第3点 | 第4点 | A减B的极差改善 |
|---|---:|---:|---:|---:|---:|
| D1：逐点/按块/按块/逐点 | 20.919 | 11.494 | 16.182 | 13.477 | +3.360 |
| D2：按块/逐点/逐点/按块 | 22.743 | 16.690 | 20.909 | 20.898 | −3.021 |

八个检查点的source/graph/PMC及校准门均通过，但只有D1第2/4点的所有块极差≤15ms；D1第二个B仍失败，返回A却通过，D2两个B均失败。两个target都没有合格B快点对，亦未满足≥5ms改善。故预注册充分原因不获支持，不能把某个绿色B挑出来放行F，也不扩成“排空粒度在所有状态都没有任何影响”。原H六例依然0/3，不重算为K的样本。

K的封存再审取得更强的边界反例：D1第3检查点main-B的两个暖点，均观察到11次root minor，逐遍minor重叠签名完全相同（7个Evidence跨度有重叠），但Evidence用户CPU为277.837/294.019ms，相差16.182ms。两点Evidence GC重叠wall为17.846667/17.739501ms，不能用它相减解释用户CPU。整根夹取窗口指令8,104,504,147→8,306,266,254，增加约2.49%，周期增加约3.78%，根读体CPU增加22.443ms；窗口之外的测量CPU约1ms，通过原专属性门。这里仍只证明整根窗口的工作量与执行速率代理都变化，不是逐遍归一化指令，也没有当时热点栈。相同GC次数/落点不能证明相同VM工作，更不能把全部差额按GC暂停或核频补齐。

三个进程各72次完整受控读，共216根（24预热、192检查点），加3次末尾语义审计，读体103.101263秒、墙钟139.984秒。counter正常EOF退出，最终CPU276.544ms、关闭5.084ms、未强停；控制器2.012618秒。连A控制器与5秒准备/1秒关闭保守占额，共计10.097188秒，低于共用20秒帽。K/A合计墙钟216.951秒、读体109.927044秒，新增5个Electron额度恰好用完。两stage输出约11.09MB、journal8,316,998字节，低于256MiB/32MiB；审计/claim等附加小型回执单列，未删除失败腾额度。

所有方法/binding/队列恢复，零元数据丢失/读取失败/拒写，三个语义审计匹配H；五个A/K应用PID及counter均已不存在。源、生产Module、驱动及封存sampler一致，结束后8534内容文件和空fence又逐项核验。收尾仅把控制器所导入的dense gate加入未来driver identity清单，候选`e0e53a19`未重跑；实际`1de20ad8`定义的gate源码也与封存值相同，不冒领新candidate计量。

## 7. 收尾的纯信号修正与剩余门

自审发现A原控制器把Directory.list的root与IPC内nested调用合成同一exposure（原回执knownExposures=5保留）；虽然原始父链已记录，这会漏掉一个已定义的覆盖变化。候选`7327a7bb`只修纯controller key，加入root/nested类别并拒绝不合法parentSeq，未改Electron中的entry/probe装配。6项纯策略测试通过；用封存A的70个真实输入包重放，覆盖恢复为6类，基线仍284.427ms、五根学习、未armed/零事件，不增加产品读取或进程。[重放回执](../../playbook/evidence/runtime-isolation-ri00-e3-signal-parent-replay-20261113.json)保留新旧版本差异，不把旧A报告改成新控制器的现场验证。

同一轮纯策略审查还确认静默门必须看root自身start，不能只看批次抵达时钟。保留`7327a7bb`会把start=59,999ms、61,000ms才交付的旧根收入学习的失败；`a59d067d`改为root start≥60秒、拒绝非法/未来clock，并返回隔离的baseline快照，调用方不能改写事实owner。7项当前策略测试及相同70个真实包再次重放通过，基线/覆盖仍为284.427ms/6类。[静默与owner重放回执](../../playbook/evidence/runtime-isolation-ri00-e3-signal-quiet-replay-20261113.json)单独绑定新版源码，原始A、K及前一次重放不改；没有新增Electron启动或产品调用。当前累计53项不同聚焦测试分组通过，不称53项同时执行、完整产品或已安装构建验收。

本轮唯一新增性能因素已按固定返回对照完成并未获支持，不能原样续跑、换进程或降低15ms门。现有证据把“多一次minor/相位迁移”与“额外窗口内工作及执行速率变化”分开了，但额外指令落在哪个Module/哪一遍、为何出现，仍缺逐遍计数器与当时CPU栈；现有入口栈和整根PMC不能事后补造它们。后续应先针对这笔未定位工作设计更窄的取栈/计数资格，不能再将归档粒度或周期GC当结论。

A说明入口/信号Module可工作；K没有给出可稳定使用的B快态资格，当前实际Peer对象发现及完整F控制器也未验证。没有新现场窗口、没有实际用户同进程残差形成或机制复现，RI-00仍未闭合，RI-01/产品重构继续冻结。计费/恢复/源码与失败回执均已封存；剩余额度不兑换追加K/H/A启动。审查为实施者自审，非独立、真实模型、安装或发布验收。

[范围验证收据](../../playbook/evidence/runtime-isolation-ri00-e3-followup-validation-20261113.json)区分producer、K控制器/封存sampler和最新纯策略候选。当前源码architecture/UI/diff通过；可查询的三candidate workflow/status均返回空，不称绿色CI。知识改动另做JSON、预算算术、链接、隐私与内容/diff自审，未为文档运行代码全套或产品发布验收。

## 8. 后续N：逐遍指令取得，但未获得性能/现场资格

[N冻结设计、实际结果与入口失败恢复](runtime-isolation-ri00-e3-pass-work.md)新增3个固定owned槽，均结束无替换。每根26槽的逐遍/余部计数与整根PMC核对通过，32个ON生产根共384遍；两target均因ON/OFF中位差及原15ms暖极差拒绝。实际一次metadata附着因固定端口假设失败，随后仅恢复实际随机端口，连接拒绝且原进程存活，未再附着追绿；unknown成本与超额墙钟保留。封存profile离线重放也表明旧10ms采样不足以给逐遍热点。最新数据与完整收据不反向改写本文件K/A结论；现场、机制复现及RI-01仍未准入。


## 后续封存审计及C/D/E/M资格

[384遍定量拆解、原门拒绝来源、控制器与实际装配结果、P冻结预算](runtime-isolation-ri00-e3-controller-qualification.md)保留本记录的原失败：N未重新过门，C/D仍失败，E完成owned真实F0/F1正常及取消路径，M完成实际Peer随机端口与零读取装配。工具资格不解释旧16.182ms、2.49%或现场30–40ms，P未执行，RI-00及重构门不变。
