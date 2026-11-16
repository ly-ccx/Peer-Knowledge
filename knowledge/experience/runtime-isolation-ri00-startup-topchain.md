# RI-00：首次 Evidence 顶层链与回收状态干预

日期：2026-11-12。接续[同进程转换](runtime-isolation-ri00-thread-transition.md)，[逐点回执](../../playbook/evidence/runtime-isolation-ri00-startup-topchain-20261112.json)。本轮按用户另一次明确授权，在其通知安全退出后启动一次30秒采样；未开始RI-01或产品重构。

## 首次文件读取的完整现场链

启动前确认旧安装进程不存在。使用同一应用的临时loopback inspect-brk，先安装64帧同步栈与异步父链观察，再恢复启动。应用主可执行文件摘要前后不变；采样方法已恢复、异步深度已复位、实际监听端口以connection refusal确认关闭，应用继续运行。

捕获2872次计划文件读、1次索引文件读；首次索引前有2086次计划文件读。首次索引同步栈为27帧，未到64帧上限；CDP还保留装配await、Promise.then注册与Electron入口父链，parent/parentId解析完成。以下是这次实际启动的链，不是将前轮的两个截断片段拼接：

```text
Electron browser_init / ESM main 入口
  → bindDesktopAppLifecycle 注册的 Promise.then
  → composition root.start 的阶段 await
  → startDesktopAffordances
  → createAppTrayController
  → createTrayController
  → refresh(force:true)
  → updateBadge
  → getNeedsYouCount
  → projectAgentDirectory.listItems
  → BotDirectory.list → rows
  → readSessionsBatch
  → SessionSupervisor.listByWorkspaceIds
  → SessionReadQuery.run
  → presentSession → project
  → humanGateOf → acceptanceFacts → hostFacts
  → readSessionFacts
  → SessionVerification.facts → factsFor → evidenceRecords
  → readEvidenceIndex → readJsonl
  → 首次 evidence-index 文件读取
```

此前找回的 `startRecoveryAndAppearance → recoverContextCheckpoints → getPlan → readJson` 是另一个已记录启动阶段。此次首次Evidence读取明确来自托盘初始化的待处理数查询。同步栈与异步装配父链共同支持该入口，不将前一阶段的2086次文件读当成索引读取的父调用，也不把文件读次数当作归一化次数。

从**当前安装asar**重新读取这条链的9个相关Module，与工作区生产文件逐个核对摘要，全相同；不是只依赖上轮939文件比对。绑定范围包含tray-controller、main、composition root、project-agent-host、BotDirectory、Supervisor、Verification及Evidence/plan file reader；不是整份签名应用的发布验收。

同哈希源码显示first-main-window阶段先于desktop-affordances。托盘取得一个数值的路径同步进入跨项目会话投影和核验，再读取全Evidence；main承担这张展示读图。源码顺序不等于已测得用户当时输入延迟，本轮没有把启动栈采集当作流畅性验收。

## 相同进程的宿主夹测与自然节奏

启动观察器移除后，使用main-A → fresh只读源子宿主 → main-B完整查询夹测。三组数据和投影摘要相同，当前首轮各点CPU约389–417ms，没有旧进程正向残差。每个宿主都取自身主线程按核型的指令、周期和CPU，而非将进程总指令归给main。

随后只读导航回同一项目，没有发送消息、修改草稿或派发任务。实际main的密集CPU为451.555/462.964/453.584ms，间隔点485.536/479.296/528.540ms，恢复450.420/445.678/452.317ms。3个自然应用根CPU为488.704/478.944/497.706ms，归一化用户CPU321.718/311.491/323.023ms，其它线程CPU274.296/277.966/265.178ms。自然返回投影与受控读取一致。

100ms/20ms外围计数的时间窗口与根自身时间分开；本组实际使用20ms旁路计数并核对Python、控制器与应用时钟。自然根外围多4.997/2.401/3.006ms主线程CPU，原样保留，不将全部外围指令算入根。间隔点中的528.540ms是受控读点，不能冒称新的自然多秒停顿。

项目页再作一次同源夹测，main-A/child/main-B根CPU中位约454.550/460.216/446.697ms；归一化用户CPU中位288.773/296.898/284.190ms。仍没有main比child更慢的同向残差。首轮约400ms与后轮约450ms发生在不同窗口；指令、周期和原生SHA校准均保存，不能无证据归成重启、页面、频率、JIT或某一GC机制，也不把两个窗口直接相减回填旧430/500ms。

## 额外指令的机制干预，保留绝对延迟负例

前轮已经取得实际自然慢/暖读快的匹配原生栈：慢窗口出现分配推进标记、标记写屏障、major及增量回收，快窗口未采到这些类别。此次在只读源隔离Electron中，以默认策略和 `no-memory-reducer + heap-growing-percent=500` 作机制控制；**没有向实际应用设置这些参数**。

每个新进程都用相同S顺序、完整生产读图和数据。测hot-before三点、14.5秒间隔三点、hot-recovery三点；比较idle中位减前后hot合并中位。首对为探索，随后按交换顺序做两对新进程确认，事先固定指令判据：默认增量至少2.5亿，控制增量至多1.5亿；不删冷热/恢复点或改写负值。各点主线程计数可用、输入/投影相同、零源写拒绝/读失败。

| 新进程对 | 默认指令增量 | 控制指令增量 | 默认CPU增量 | 控制CPU增量 | 默认/控制的其它线程CPU增量 |
|---|---:|---:|---:|---:|---:|
| 1（探索） | 4.593亿 | 0.622亿 | 36.010ms | 1.103ms | 172.363 / 6.553ms |
| 2（交换顺序确认） | 4.601亿 | 0.814亿 | 35.072ms | 1.997ms | 181.232 / 2.891ms |
| 3（确认） | 3.610亿 | 0.336亿 | 29.640ms | −3.907ms | 167.131 / 0.581ms |

三个默认/控制对都满足固定指令判据。该干预重复消除了大部分间隔额外指令、主线程CPU增量和后台CPU增量，和实际进程中同一回收周期的额外工作相互印证。它验证的是周期成本的形成机制，不替代现场归因；两项策略一起改变，不能唯一归因某个flag，也没有证明旧进程所有密集残差均由它导致。

控制组密集基线反而较慢，部分绝对idle值与默认接近。不能将“增量变小”改写成应用已提速，不能通过这些VM设置作为产品修复。生产问题仍是轻量展示读完整执行/核验图、反复全量归一化、分配工作占据main；Interface必须限制读取范围和成本，执行位置还须隔离，不能只调GC参数。

同版本[V8分配观察与增量推进实现](https://raw.githubusercontent.com/v8/v8/14.6.202.34/src/heap/incremental-marking.cc)及[标记写屏障实现](https://raw.githubusercontent.com/v8/v8/14.6.202.34/src/heap/heap-write-barrier.cc)支持原生链的机制解释，不提供这台机器的精确成本份额。源码事实、现场栈、计数与干预分别保留，不用源码替代现场。

## 剩余门与迁移覆盖

启动首次Evidence顶层链的缺口已由这次授权采样补齐。原3.949秒的父调用/CPU历史缺失继续按用户允许保留；不从本次链反推当时操作。新的自然多秒链与坏基线见前篇，不用本次约0.5秒点代替它们。

另补5分钟不插入受控生产读取的自然窗口，无CPU profiler、FS/JSON包装或旧timer接管。20个目标IPC来自同一scope，均3859次getPlan和12遍Evidence/831192行；同步墙钟458.186–515.088ms，中位501.714ms，线程CPU457.448–513.141ms、中位500.632ms；归一化用户CPU284.916–323.984ms。最长主循环间隔534.912ms，500ms坏基线门按预期失败；没有新的多秒事件。资源错误、记录/GC丢弃均为0，全部owned方法恢复、端口关闭。

100ms外围硬件采样覆盖其中17个根；最初3点没有闭合计数窗口，明确为unknown，不补零。17点外围额外CPU1.308–6.144ms，均在固定计量容差内。多数慢点约86.9–89.2亿条主线程外围指令、其它线程CPU246–287ms。最后一次**自然**读取自行回到457.448ms、归一化284.916ms，外围约83.95亿指令、其它线程70.463ms，根内仅11次minor事件；前一个507.303ms点有28次minor、1次incremental和1次major。它不是受控密集读制造的快点，补到了自然节奏中回收工作变化与CPU恢复的同窗证据。最后一个快点仍未满足产品响应预算，不称为恢复流畅。

窗口后再作main/child/main夹测，根CPU中位448.613/462.577/453.436ms，归一化用户CPU287.107/298.190/286.325ms，输入/投影仍一致，仍未出现main较child更慢的同向密集残差。

旧已退出进程的特有密集30–40ms正向残差，尚无形成前后VM/硬件快照；本次三轮同窗夹测均为负例，不能以重开后没有差额冒称历史归因。该历史形成条件仍未证明，RI-00不提前关闭，不开始重构。

本次托盘计数应纳入RI-01不可漏迁入口，落在既有 `bot.badge → M12` 合同；不能只迁Renderer RPC而遗漏Shell启动回调。菜单强刷的 `listNeedsYouBots` 也是同目录读取入口，后续迁移前须核对命名View的过滤、分页、来源和不可用恢复，不能临时在Shell扫描所有Bot/会话。现阶段只登记证据与覆盖，不改产品路径。

## 验证与边界

本轮为C级诊断，核对 `00-adr-map.md`、`96-task-execution-responsiveness.md`、`128-local-runtime-isolation-and-bounded-query-contract.md`，沿用前轮其它已核对ADR。现行权限、Evidence、System Context、存储、IPC和运行时边界未移动，ADR128仍Proposed。仅把同源完整查询的主线程计数扩到main/child/main夹测，并验证跨三组的投影一致；没有性能产品补丁。

诊断候选`a2db21bab87e51262247aa3ed006b41be5b6cb78`已提交并推送。68项诊断聚焦测试、变更MJS语法、architecture/UI及diff检查通过；三轮实际main/只读源child/main、实际深栈启动、自然窗口与六个机制对照均核验恢复/输入身份/可用计数，子宿主零源写拒绝和读失败。自动CI无run/status，不称绿色。内容、计数、来源、链接、隐私与diff为实现者自审，不称独立审查；未跑完整产品/发布门、真实模型、其它平台或安装修复候选。原始用户数据、scope、路径、PID、profile和原生地址保留私有，不上传。
