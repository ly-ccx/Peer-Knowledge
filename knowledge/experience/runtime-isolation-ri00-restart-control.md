# RI-00 重开对照：自然停顿仍在，宿主慢化尚未归因

创建时间：2026-11-12
最后更新：2026-11-12
状态：重开对照完成；自然多秒阻塞与读放大再次证实，旧宿主慢化形成原因和当前跨宿主归一化差额未完全闭合。RI-00保持未闭合，RI-01与产品重构未开始。

接续[自然现场续证](runtime-isolation-ri00-natural-followup.md)；[本轮回执](../../playbook/evidence/runtime-isolation-ri00-restart-20261112.json)保存逐窗口、夹测、计数、源/工具身份及失败。实现者自审，不称独立审查。

## 1. 重开后的事实

用户手动重新打开应用，新进程启动时间为2026-11-12 08:49:56（以下用户时间均Asia/Shanghai；原始材料保留UTC）。42.7秒时先量常量路径，尚未检查业务闭包或安装观察包装；随后读取同一实际GoalPlanStore，与独立Electron作main-A → child → main-B对照。

此前与本次选取的200个文件，名称、dev/ino/size/mtimeNs/ctimeNs和事实摘要三种哈希均相同。旧main的200次getPlan约9ms，本次各阶段约1.3–2.4ms；独立child仍约1.3–1.8ms。路径计算额外成本明显缩小；四分钟轻量观察和两分钟CPU采样后也没有回到旧水平。不能由此认定JIT、GC或某个探针就是形成原因，亦不能把重开称为修复。

**自然多秒停顿仍发生**：08:51–08:55无CPU/FS/JSON替换的窗口最大6146.998ms；08:58–09:01加入命名读Port根的窗口最大6565.574ms。没有注入请求突发，也没有枚举已有timer。旧Path慢化不是这些新多秒事件发生的必要条件；它也不能成为停止梳理整体调用图的理由。

所比较的939个安装产物代码文件与固定rc.41生产checkout一致，含此前860文件集合；Electron41.7.1、Node24.15.0、ARM64一致。这不是整个签名包/native framework的逐字证明。产品源仍`b05b7afbf26b43444635f77710397c3a658d6a0f`，仅诊断工具修改。

## 2. 自然链与计量边界

| 窗口 | 方法 / 时长 | 结果与限制 |
|---|---|---|
| A，08:51–08:55 | 无CPU/FS/JSON包装，4分钟 | 16次目标空授权查询中位465.542ms；最大间隙6.147秒；初始同步根不覆盖所有微任务 |
| B，08:58–09:01 | 同上，增加Supervisor的无父同步根 | 多秒间隙6.566秒；实际约3分钟，操作者停止原计划6分钟的采集；跨await的旧父请求仍可能隐藏子读取 |
| C，09:04–09:06 | 仅CPU加轻量方法根，2分钟 | 本窗口最大530.926ms，并未再捕获多秒；513.953ms同步根覆盖，其余16.973ms采样基本为idle |
| D，09:13–09:17 | 无CPU/FS/JSON，修正跨await分段，4分钟 | 最大982.726ms，其中977.755ms由同窗IPC覆盖；未捕获新多秒，不能倒填B的缺失段 |
| E，09:39–09:40 | 主机UI交付读Port发现，90秒 | 有效观察并恢复；未发现可包装的authority对象，不能把缺失metric解释为UI读取耗时为零 |

B一个5753.320ms自然间隙中，已计量同步根并集5062.040ms、余量691.281ms。真实JS调用栈直接得到：

```text
runtime-host.sweepWatch → sync → runner.pump
  → takeNext → selectNext → recoverySelection
    → reconcileRepairCustody → roster/rows → resolveRoster
  或 runJob → runRounds → turnFacts/rows → resolveRoster
  或 runJob → runRounds → readSlot → resolveRoster
  → Desktop resolveRoster → SessionSupervisor.list
  → 核验 / 全计划读取 / 全Evidence归一化
```

这三条独立roster读取各约494–504ms；同窗随后还有read-conversation、两个Bot get、list-sessions等串行读取。691ms余量没有同窗CPU，保留unknown；其中一个约491ms段暴露了计量器只看“是否有异步父请求”、没看父请求初始同步段是否结束的问题。修正后单独保留跨await子读的同步区间和原parent identity，单元反例验证；D没有触发该多秒序列，不能声称已重采其完整新链。上轮5.417秒的CPU闭合窗口继续单独成立，不与本轮拼成一次事件。

C的一次512.130ms授权查询，排他采样归组为Evidence全读/归一化300.408ms、getPlan32.819ms、协调读39.110ms、GC27.231ms、其余112.562ms。其余包含indexedRefs/evidenceRecords过滤和supervisor、gateway、V8 program等，叶栈逐项保留。它不是另外112ms异步等待；采样不是精确self span，不能与嵌套inclusive重复相加。

## 3. 同源与冻结夹具对照

输入仍为23个session、3859次getPlan、12遍Evidence；活跃源在本轮从69199条增长至69265/69266条。因此不能把所有窗口都贴上同一数据代次，也不能仅按条数比例推断新增记录的处理成本。

同一物理索引的前后夹测：main四个读点28.836/30.869/27.393/32.168ms，child首读冷198.810ms，随后30.110/28.394/28.833ms，main后组28.981/28.577/32.960/36.111ms。各点69265条，强文件版本哈希相同。每次独立读后让出100ms；这些是受控读取，**不计入自然事件**。本组说明暖全索引读本身约数十毫秒，乘以12次是主成本；不能由三次child暖值外推主机精确差额为零。

| 场景 | 暖handler p50 | ABBA off组p50均值 | ABBA on组p50均值 | cold / 八请求主循环 |
|---|---:|---:|---:|---:|
| 原冻结私有夹具，完整Desktop读依赖、深探针 | 485.556ms | 467.482ms | 480.847ms | 2139.708 / 3953.271ms |
| 所有真实Store，只读guard、无FS/JSON包装 | 423.905ms | 431.331ms | 429.977ms | 1995.220 / 3530.039ms |
| 现场D，轻量方法观察 | 中位502.571ms | 不冒充ABBA | 不冒充ABBA | 本窗口自然max982.726ms |

真实源模式将project profile、conversation、goal-plan及协调全部指向源，而非只换GoalPlan；持久授权和receipt read存在，rootless scheduler与生产一致。协调revision6713在所有阶段起止一致，零读取失败、零源写拒绝；所有SQL连接强制readOnly。没有模型/工具/runner/租约或恢复入口。其它数据源仍是活数据，不称跨Store原子快照。

冻结夹具前后内容与生产Module身份不变；同夹具本轮off约467ms，前次约412ms，也表明不同时间窗口不是固定常数。全真实源反而约430ms，不能把两轮均值相减后称“旧副本固定多花37ms”。负的ABBA边际-1.353ms原样保留，说明该轮小差值与波动叠加，不说明探针会加速。

当前D的Evidence段中位341.872ms，全真实源隔离暖段288.763ms；getPlan分别35.218/30.668ms，生命周期协调33.607/33.313ms，receipt读2.923/2.822ms。**主要剩余差额定位在相同源码的全索引归一化CPU成本，尚未证明触发其跨宿主变化的机制。**两轮非同时且源记录有更新，不把它们作为精确因果相减。

八请求是受控变量。3953ms与旧3949ms接近仍不证明旧事件发出了八请求；旧原事件的证据缺口不变。`ok:true`表示预期失败基线有效，500ms预算未通过，当前应用没有性能修复结论。

## 4. UI交付端口的分离

GoalPlanStore的可选`readUiDelivery`和Desktop `readSessionFacts`注入的同名回调是两个接缝。此前只核对前者，不能据此断言后者不存在。生产main.mjs为后者传入可选provider读取；provider本身受packaged/preview条件控制。E的authority未发现结果保持“未计量”，不写成0ms。随后F只记录绑定类型，确认sessionFacts和UI回调均为function、previewProvider为null，与打包入口的初始化条件相符：本安装现场没有活动authority可读取UI账本/图片；不将这个结论泛化到dev/preview宿主，也不伪造一个0ms authority样本。

隔离读宿主仍不伪造live UI-delivery和内存review事实。该支路的状态已明确；宿主CPU差额及其形成机制仍保留，不通过跳过核验、改签收/权限含义或补passed来制造更快的可比结果。F夹测时200次getPlan约1.283/1.406/1.445ms，旧额外慢化到本轮结束仍未重现。

## 5. 工具、失败与验收

最终诊断候选及每窗工具hash见机器回执；整个产品实现未改。新增开关`--unattributed-read-roots`只给高层Supervisor的独立同步调用记录根与已剥除路径的源码栈，不给每个getPlan制造数千条根；跨await后另起同步区间，父请求仍保留。`compare-runtime-context --evidence-reads`按点让出并绑定强版本；`perf-runtime-baseline --readonly-source-stores`必须有只读源guard。

B包装与GC均恢复，但原1秒端口检查过早，raw `ok:false`保留；09:02:25再次确认关闭。收尾等待改为最多15秒轮询，仅connection refusal认定关闭，transport timeout记uncertain；这不是放宽500ms响应性预算。后续C/D/E的实际关闭检查通过。

UI发现补充曾有一次重复变量名语法错误，38项中合成Electron检查失败；失败fixture保留，先修命名并检查语法，再重跑38项通过。其它synthetic Unicode/arity/length/invalid-input负载未重现旧慢化；仅排除这些采样负载，不概括为引擎绝不会变慢。旧profile无优化原因字段，原生符号也不能证明JIT状态，仍不作JIT归因。

最终聚焦验证覆盖真实Electron IPC/已有timer、异常/owner/异步记录释放、跨await分段、不重复计时、只读源准入/拒写及损坏读取、版本绑定、端口延迟关闭与隐私；不跑无关全仓发布门。真实原生输入/滚动、完整模型执行、平台/安装候选与发布回归仍未验收。

本轮沿用并核对`00-adr-map.md`、`96-task-execution-responsiveness.md`、`98-large-history-execution-responsiveness.md`、`104-progressive-interaction-and-coordination-storage.md`、`112-runtime-module-and-loading-boundaries.md`、`115-input-prediction-and-draft-boundary.md`、`121-desktop-session-windowing-contract.md`、`128-local-runtime-isolation-and-bounded-query-contract.md`。诊断C级，现行协议/权限/Evidence/存储/System Context边界未移动，128仍Proposed。

## 6. 当前结论与剩余工作

多次局部优化没有解决的问题已具体化为：轻量展示与调度读取共用完整执行/核验列表；缓存免掉原JSON解析，仍重复归一化全索引和过滤；UI入口、预测准备、runner的恢复/turnFacts/readSlot均可进入此图；微任务并未为同步工作提供抢占。新进程没有旧Path额外成本仍出现自然多秒停顿，不能以优化Path或重开应用代替治理读图、队列与执行位置。

RI-00尚未全闭合。当前G2缺口是旧进程内慢化的可复现形成过程，以及当前全索引归一化跨宿主成本的受控触发。不能把旧进程退出后无法取得的优化状态用新CPU样本补造，也不因主要结构问题明确就自行抹掉这个门。上轮自然5.417秒的同窗CPU闭合证据继续有效；新版B单事件的续段缺口是本事件的限制，不额外要求每个自然停顿都重采一次才能收口。下一步应在隔离宿主保留干净初值，逐段重放只读装配/诊断/寿命负载以寻找变化点；任何因果结论须绑定第一次变慢的具体候选/数据/调用序列，未命中继续记负例。进入重构前仍须补审runner roster与预测初始准备的接口、事实owner、版本、队列及恢复。
