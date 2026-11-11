# RI-00 续证：自然多秒停顿、现场差值与仍未闭合的原因

创建时间：2026-11-12
最后更新：2026-11-12
状态：自然多秒链与受控坏基线已补齐；现场长期运行上下文差值已定位到具体调用，但慢化触发原因未证实，RI-00仍未闭合。RI-01和产品重构未开始。

接续[首轮调查](runtime-isolation-ri00-investigation.md)、[取证门](../../playbook/runtime-isolation-ri00-baseline.md)。本轮[机器回执](../../playbook/evidence/runtime-isolation-ri00-natural-20261112.json)保留分段、原时序、样本摘要、各代harness指纹及失败限制；原始profile、私有文件manifest、参数/正文不上传。实现者自审，非独立审查。

## 1. 可以下结论的部分

用户打开应用并正常使用后，捕获了自然发生的多秒主循环间隙，没有向该现场窗口注入八请求突发。首个轻量入口观察最大9.101秒；后续带CPU的5.417秒窗口可将入口时序与同一份CPU栈对齐。它们证明当前产品在自然负载下发生连续main阻塞，不能追认旧3.949秒的触发。

最重要的新链不在Renderer轮询里：runner恢复/选择任务的Promise微任务反复通过`resolveRoster`调用完整Supervisor列表，间接进入核验、全计划扫描与Evidence归一化。仅给IPC或timer回调量初始同步段会漏掉它；先前未分段的1.251秒中，约1.063秒采样落在这条链。

约190ms的旧隔离数值漏了Desktop核验依赖。完整读宿主稳定在约0.40–0.43秒；当前长期运行main中的相同scope自然查询约0.58–0.61秒。实测差额的大头在`getPlan`及Node路径计算；预先生成文件路径后，实际exists/stat成本接近。没有证据将差额归为网络、慢磁盘、OS睡眠、模型等待、GC或JIT中的任何单一原因。

因此没有宣称“性能已修复”，也没有把“成本落在哪个函数”提升为“为何长期运行后变慢已查清”。旧34–38ms差值的两个窗口缺逐段同源计量，不能用这次更晚、数据也不同的差额倒填。

## 2. 候选、身份与只读边界

- 产品源仍为rc.41 `b05b7afbf26b43444635f77710397c3a658d6a0f`；主要取证工具提交`495ea9f019c1ce99263ed47a10b89947ca192359`，最终清理候选`8c5af4a86413b5310280a2242db6203a7afcbc6d`，无产品路径修改。安装包内860个所比较的`@peer-agent` dist及electron/main代码文件与生产checkout哈希一致；这是明确文件集合，未声称整个签名包一致。
- 现场与独立Electron均41.7.1、Node24.15.0、macOS ARM64。当前私有只读副本11,960文件、597,125,751字节，复制前后dev/ino/size/mtimeNs/ctimeNs清单零变化；协调一致备份revision6513、3,874,816字节。不是旧事件内存/磁盘回放。
- 补齐上一宿主遗漏的27次receipt `read()`、持久授权读取及Desktop默认rootless scheduler；不能让production的catch吞掉缺方法而制造空结果快基准。只读协调端口捕获任何被吞读取失败并令实验失败。
- 另用生产CoordinationStore只读连接及原source校验做对照，SQLite强制readOnly，原个人数据根的同步FS写被guard拒绝；不持lease、不暴露写Port。实测revision各阶段保持6513，零写拒绝/零读取失败，说明本轮没有走需要恢复写入的分支；不代表所有未来source都能只读恢复。
- 最后的context前后夹测读取同一实际GoalPlanStore和同一200个原物理文件；姓名、内容不离开目标，只返回名称、强元数据和事实摘要哈希。三份哈希前后相等，不以“文件大小相似”冒充同源。
- Inspector只附着已运行应用。未安装、启动或重启日用实例；SIGUSR1启用调试前核对进程/executable和端口归属，采样器自身不发信号。所有采样已停止、包装恢复、所有权恢复检查通过，拥有的Inspector已关闭。没有触发模型、工具、个人任务恢复或规范数据修改；自然后台任务本身可能运行，不能称现场没有模型活动。

本轮重读ADR map、96、98、104-progressive-interaction-and-coordination-storage、112、121、128；为核对预测入口另读115-input-prediction-and-draft-boundary。诊断为C级，现行能力/权限/Evidence/存储/System Context边界未移动，ADR128保持Proposed。

## 3. 自然窗口：完整到什么程度

| 捕获 | UTC时间 / 长度 | 主要观测 | 限制 |
|---|---|---|---|
| A | 11月11日16:42–16:50，约8分钟元数据；CPU另延续 | 942入口，最大9100.891ms；多个Bot get、会话/对话/授权读取连续到达 | 未换算成本地11月12日以免混淆；CPU启动括号较宽，不能逐样本精确绑定该9.10秒；不是10分钟元数据 |
| B | 16:56:42–17:06:44，约10分钟 | timer/IPC/phase/CPU，选取17:02:15.883Z的5417.230ms窗口 | 前半段深FS/JSON探针；后半段关分段仍有pass-through替换，不能称无探针 |
| C | 17:23:42–17:27:44，约4分钟 | 无CPU/无FS与JSON替换；自然最大1422.096ms，同scope授权16次中位583.873ms | 原生持续键入/滚动与模型结果质量未验 |
| D / E | 各3/4分钟 | 实际GoalPlanStore/Supervisor方法，phase开关ABBA | 检查命名读Port用只读Inspector闭包引用；未把scope内容保存为产品数据 |
| F / G | 90秒/4分钟 | 路径方法分段，G真正恢复原函数做on/off/off/on | 仍保留IPC/Store/GC观察；不是零成本完整产品验收 |

B的timer枚举安装ack2038.552ms单列，不能加入自然停顿。前半深探针出现14.153秒间隙，已证明测量会明显放大耗时，因此不拿它作为未采样安装版停顿时长。选取的5.417秒位于关闭深分段之后，不包括启停、枚举、25ms对时标记。

### 选取的5.417秒

同一main单调时钟，按进入顺序及裁切区间计算同步根的**并集**，不相加嵌套timer/IPC：

| 同步根 | 在间隙中的覆盖 |
|---|---:|
| 已存在的timer回调 | 1291.76ms |
| 另一timer回调 | 1.12ms |
| access-policy读取 | 0.11ms |
| Bot get | 1118.93ms |
| list-sessions | 579.42ms |
| 另一Bot get | 1165.67ms |
| read-conversation及shell任务列表 | 8.89ms |
| 根区间并集 | 4165.888ms |
| 未被根初始同步段覆盖 | 1251.341ms |

CPU profile仅对上述未覆盖的互不相交区间裁切：roster链1063.048ms、GC80.257ms、V8 `(program)` 34.005ms、sendMessage29.959ms、readCanonicalMessages22.372ms，余量为回执中逐项命名的小样本。没有把已覆盖的Supervisor再算进这个1251ms，也没有把采样时间叫作精确span。未分类的短采样仍保留，不称完全零unknown。

```text
Node timers → runNextTicks → runMicrotasks
  → runner.pump → takeNext → runner-coordination.selectNext
    → pending/pendingFrom/rows
      或 recoverySelection → reconcileRepairCustody → roster/rows
    → runtime-host.resolveRoster
    → Desktop project-agent-host.resolveRoster (478)
    → SessionSupervisor.list → presentSession/project
    → humanGate/acceptanceFacts → SessionVerification/getPlan/Evidence
```

另有自然输入预测入口：`input-prediction:request → Desktop.readSnapshot → projectAccess.directory.get → projectRow → sessionsOf/ProjectFacts → Supervisor`。重认知请求本身不是全部初始耗时；在决定是否允许预测前的同步准备已经走深读。此链需与runner、UI查询同时纳入架构验收，不能只优化授权轮询。

对时按CDP的[timeDeltas微秒定义](https://raw.githubusercontent.com/ChromeDevTools/devtools-protocol/master/json/js_protocol.json)，累计startTime并通过首尾已命名25ms标记约束offset。B观测offset区间半宽约0.026ms；这只是标记给出的区间，不是承诺V8采样有26微秒绝对精度。标记内部子帧也计入，不能只取叶函数。

## 4. 现场差额：已排除与未排除

同scope一次自然授权读取：23个session、3859次getPlan、12次全Evidence索引归一化、830388行（69199×12）、23次control、23次lifecycle、27次receipt读取。数据较首轮略增长，不将3855/69045悄悄改成新计数。

| 成本 | 长期main自然G | 独立Electron完整读宿主、原source只读 |
|---|---:|---:|
| 整体handler | Path观察on中位599.039ms / off597.389ms | ABBA off组p50均值397.020ms / on407.309ms |
| getPlan inclusive | off中位173.674ms | 首个暖请求36.331ms |
| Path.join inclusive | on中位181.793ms，13644次 | 首个暖请求9.131ms，13643次 |
| Evidence | 约0.28–0.30秒、相同12次/行数 | 首个暖请求268.770ms |

这是分段/同源微基准支持的成本定位，不是同时发生的同一请求精确相减。Path包含normalize并嵌套在getPlan/其它调用中，三者不能相加。两宿主读取方式不同造成1次Path调用差异，保留原值。逐请求GC已保存：现场C约26–37ms，隔离完整读宿主暖请求约24–26ms；GC不是约0.2秒差额的证据支持解释。

更强的控制是相同200个文件/同函数/同Electron的main-A → fresh-child → main-B。每200次的三轮中位：

| 测项 | main A | fresh child | main B |
|---|---:|---:|---:|
| join实际文件名 | 2.392ms | 0.071ms | 2.631ms |
| normalize相同常量 | 1.010ms | 0.027ms | 1.042ms |
| 预生成路径exists | 0.114ms | 0.136ms | 0.103ms |
| 预生成路径stat | 0.257ms | 0.359ms | 0.275ms |
| 同200个getPlan | 9.216ms | 1.279ms | 8.896ms |

常量和重新展平directory字符串也保留差异；函数源码摘要、cachedDataVersionTag及文件/事实摘要匹配。这里只能证明慢化位于宿主中的Node路径JS调用，不能据版本tag或源码相同推出优化tier相同，也不将200条外推成整查询精确差值。

独立宿主依次安装/撤销同类FS/JSON/phase探针、queryObjects、CPU profiler、读取Store及Path闭包scope，均未产生main那样持续的路径慢化。现场phase ABBA：开583.833ms/关587.445ms；Path ABBA：开599.039ms/关597.389ms。它们不支持“当前差额全是这层即时观察成本”，**仍不能排除只在完整生产上下文或长时间累积后出现的诊断影响**。这就是RI-00继续保持未闭合的具体原因。

## 5. 可重复坏基线与工具

最后冻结的完整Desktop诊断宿主：暖handler p50 427.740ms、cold1890.893ms、八请求主循环3422.086ms；probe-off ABBA均值411.667ms、on428.142ms，边际16.476ms。改用无FS/JSON替换、Path分段+原source只读，暖406.814ms、cold1830.004ms、八请求3270.233ms。每一代harness指纹分别记录，不把更晚工具提交的hash倒填较早结果。

`ok:true`只证明`--expect-stall`正确拿到坏基线，500ms预算仍失败。源/私有fixture/协调备份的前后指纹保持；原source变化另外记录revision，200文件context比较另绑定强元数据；没有声称对整个活跃个人数据根做了原子快照。

代码仓的工具入口：

```sh
# RI00_MODULE_ROOT为已构建生产checkout，RI00_FIXTURE为受限私有副本；输出在副本外。
node apps/desktop/scripts/perf-runtime-baseline.mjs --module-root "$RI00_MODULE_ROOT" --fixture-root "$RI00_FIXTURE" --bindings desktop --desktop-diagnostics --coordination-snapshot "$RI00_BACKUP" --parent-hash "$RI00_SCOPE_HASH" --instrumented --paired-probe --expect-stall --output "$RI00_OUTPUT"

# 仅附着已确认PID/归属的既有loopback Inspector；close-inspector只用于本次拥有的端口。
node apps/desktop/scripts/observe-runtime-live.mjs --pid "$RI00_PID" --duration-ms 600000 --workspace-file "$RI00_PRIVATE_WORKSPACES" --output "$RI00_CAPTURE" --close-inspector
# 无CPU/无FS和JSON替换的读Port观察；不枚举已有timer。
node apps/desktop/scripts/observe-runtime-live.mjs --pid "$RI00_PID" --duration-ms 240000 --workspace-file "$RI00_PRIVATE_WORKSPACES" --output "$RI00_LIGHT_CAPTURE" --close-inspector --no-profile --no-builtins --inspect-read-ports --skip-existing-timers
# 同一实际文件的宿主前后夹测；此窗口明确标为受控读取，不并入自然窗口。
node apps/desktop/scripts/compare-runtime-context.mjs --pid "$RI00_PID" --module-root "$RI00_MODULE_ROOT" --fixture-root "$RI00_FIXTURE" --output "$RI00_CONTEXT_OUTPUT" --close-inspector
node apps/desktop/scripts/analyze-runtime-gap.mjs --report "$RI00_REPORT" --profile "$RI00_PROFILE" --gap-at 2026-11-11T17:02:15.883Z --output "$RI00_NEW_ANALYSIS"
```

private output必须新建且为空，权限0700；不要在代码/知识仓提交这些原始输出。`--readonly-coordination-root`只允许诊断child的生产source只读guard，`--readonly-source-plans`须同时提供该guard；既有损坏/需要catch-up写的source会使实验失败，不由harness修复。公开seed依旧可复现连续阻塞机制，不能代表私有历史或长期main上下文。

最终清理候选32项聚焦测试、28个MJS语法、architecture/UI约束及diff检查通过。包含实际Electron fixture的timer/IPC/CPU/恢复，PID不匹配保留对方Inspector，嵌套区间去重、裁切采样、只读源拒写、读取错误不降为空成功、Promise/异常及owner冲突。清理后继没有重测性能，不把主要计时的旧harness hash改成新值。未跑全仓发布门，未做真实性能修复或安装验收。

失败均保留：第一次timer fixture未就绪（require anchor/ready一起纠正，不能单独归因）；marker叶帧不足；guard的/var-private别名；一次备份无法打开后重试成功但原因未知；v1微基准的FS项包含join，后续预生成路径纠正。详细探针放大时延及最早失败fixture原始目录被清理只剩console记录也明确登记，没有用通过样本抹掉。

收尾新增清理反例还发现：此前包装虽然恢复，ALS未显式disable；仅补disable后，Node25.9.0已有回调仍能看到旧记录，32项中该项失败。最终改为可显式清空的间接cell，分别在同步结束、Promise结算和stop释放记录与待处理回调的原row引用，再请求disable；32项含真实Electron验证通过。旧采样可能残留的异步上下文及累积影响不能因此追认已经排除，没有证据说明它就是Path慢化的原因。

另采30秒系统级sample，不安装运行时包装；安装包原生符号不能映射JS函数/优化tier，大偏移的邻近编译器符号不作为JIT根因证据，结果登记为不确定。

## 6. 当前门与下一步

| 门 | 当前判定 |
|---|---|
| 旧3.949秒 | 按用户新指令，明确登记不可追溯证据缺口；原因未证实，不再要求伪造历史栈 |
| 新自然多秒链 | 已捕获；5.417秒同窗入口、同步并集及余量CPU链闭合到应用Module；profile/探针影响明示 |
| 完整读坏基线 | 可重复，500ms门稳定失败；缺依赖/receipt/source校验口径已纠正 |
| 现场剩余差额 | 已定位Path/getPlan宿主成本，**导致长期上下文慢化的触发未证实，门未通过** |
| 原生持续交互与发布 | 尚未验证；不以自然空闲观察/fixture rAF替代后续完整产品门 |

下一次取证集中在唯一剩余问题：复现“fresh与长期main相同Path函数不同成本”的形成过程。先在隔离宿主复用生产装配/模块导入与长寿命工作序列，分别控制diagnostics、async context、运行时间和内存负载，保留最初快值及变慢前后的同文件微基准与采样；不先改热点。若仍无法形成，不能从heap差异或V8一般知识宣布根因，也不擅自重启个人实例制造一个“恢复了”的结论。RI-00继续未闭合，RI-01及重构仍受门约束。

新证据还要求既有方案的回归覆盖runner roster微任务和预测snapshot初始准备，不能把迁移范围收窄为UI的pending-grants；此要求已回写实施卡。进入实现前要对这两条链按原详细设计重新审查事实owner、字段闭集、source版本与失败恢复，不能在改代码时决定或让调度读取UI Query作为授权真源。

已向用户请求在当前任务安全停稳后手动重开一次，准备从新进程先记录初值，再做无深探针的只读对照。依据代码仓AGENTS.md的Engineering Delivery Consensus，当前验证授权不包含重启运行中的应用；未收到回复前不执行依赖新进程的步骤。此请求用于取证，不是让用户验收未验证修复。
