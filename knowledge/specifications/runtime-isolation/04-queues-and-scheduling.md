# 04 队列与资源配额

创建时间：2026-11-11
最后更新：2026-11-11
状态：固定设计参数；性能效果待实现测量。[协议](01-protocol-and-command-delivery.md)与[存储](05-storage-and-recovery.md)决定接收/提交语义。

## 1. 全局规则

容量同时按条数与字节计，先到上限者生效。参数表示内部运输/调度容量，不是任务数量、模型总轮数或用户授权额度。已接受工作不能因内存队列满而丢弃，保留在原 durable queue/journal。主循环每片最多 8ms；达到时间/条数上界后用真正 timer/macrotask 让出，不连续 Promise microtask 自旋。

普通队列拒绝新 admission 前先查幂等 key，已有 receipt 的重试不再占位。高优先级不能中断已经开始的同步 JS，所有扫描、序列化和 SQLite busy wait 都必须离开 main/Runtime control loop。

## 2. 固定队列目录

| ID / owner | 在途/等待容量 | 调度与 deadline | 满/取消/失败的确定行为 |
|---|---|---|---|
| QG Gateway decode | 每连接 16 requests/1 MiB；全宿主 128/8 MiB | 每片最多 16 帧或 8ms；协议握手 5s | 超限拒绝该新 request；恶意大帧关闭连接；不影响其他连接 |
| QU ClientState / Gateway | 每窗口64 keys；同key最多1在途+1待保存/1MiB | 250ms合并表达写，预算1s、最大5s；CAS保护其它窗口 | 只合并自身同key的未发送表达状态；失败保留内存draft，不生成模型输入 |
| QC 控制 admission / Session Control | 独立于普通命令；32 在途、256 等待/4 MiB；同 session 一次当前控制 | 按原控制顺序；停止优先于尚未派发的普通工作；接收预算 2s、最大5s | 相同 operation 合并；不同操作保留原顺序；full 返回未接收，不伪造 stopped |
| QA 普通 command admission / Gateway | 64 等待/8 MiB；每连接8 | workspace deficit round robin，每轮最多4条；接收2s、最大5s | journal 未提交才拒绝；已接受转 durable backlog，不继续占内存等待槽 |
| QW Work mailbox / Coordination | 每项目一个在途判定；最多32条事件/256 KiB 一批；全宿主8批在途 | 项目轮转；每批≤8ms，跨 await 重检 control/source | 输入/事实仍在原 durable queue；满仅延期读取，不丢事件 |
| QT Agent attempt / Scheduler | 每Runtime在途16；每项目沿当前1–8配置；待启动只持最多128个轻引用/1 MiB | 保留1个交互与1个核验槽；空闲可借用，已运行不强杀；既有priority/30分钟aging保持 | 等待在原 queue/Plan；不得设新的累计模型/工具上限；等待子任务让出attempt槽 |
| QX Capability dispatch / Executor | 每 attempt同一工具调用批次最多8在途；每Runtime32在途/64轻引用等待 | 批次原顺序和工具依赖不变；deadline沿原调用/批准政策 | 不能用并发上限改变工具序列语义；已派发使用原 receipt，对未知效果不重试 |
| QQ Product query / Query Service | 每客户端4在途、8等待/2 MiB；全进程8在途、64等待/16 MiB | 交互页:后台刷新=3:1轮转；默认总预算1s，最大5s | 同 view/scope/filter/source只共享纯读在途；full 返回QUEUE_FULL；取消最后等待者可停纯读 |
| QP Projection catch-up / Query owner | 每 source一个 job；128个source refs/2 MiB | 当前可见项目优先；256记录或1 MiB或8ms一批取最小；延迟100ms合并失效 | 溢出合并为该source的dirty checkpoint，保留canonical cursor，不丢业务事件 |
| QS Storage commit / Repository | 最多8个已准备aggregate；实际commit2个槽；每aggregate1个commit、64个step refs/4 MiB等待 | 每aggregate FIFO；1个控制Store进程+1个普通Store进程；终态prepare总期限30s、最多4次版本冲突重准备 | 同aggregate已开始写不抢占；过期后lookup；队列满不删除原sidecar |
| QR CPU/rebuild pool / Host | 同一数据根的宿主采用共享许可，最多4个；每Runtime最多2个；job描述≤256KiB | 关键prepare至少1许可，rebuild最多3；可见重建:背景=3:1；单批读取1MiB | job只传refs；Node/Electron CPU worker受192MiB heap约束，终局迁由Rust Core进程按内存预算承担；大记录按05流式解析，不硬吞全文 |
| QB Platform / Desktop Broker | 每窗口8在途；全Broker32在途/64等待/2 MiB | 短系统操作ack1s/执行5s；modal ack1s后等待用户，不堵执行线程 | stale ticket拒绝；UI关闭返回unavailable；未知副作用查receipt，不自动重复弹窗/调用 |
| QE 订阅/Activity egress / Gateway | 每连接32个view订阅；失效128帧/256 KiB；Activity256帧/1 MiB | 最多每16ms发送合并Activity；每100ms合并view失效 | 溢出发gap/resync并释放纯展示缓存；绝不丢canonical/Grant/Evidence |
| QD diagnostics / Host | 1024条/1 MiB，轮换总4 MiB | 异步sink每250ms≤64KiB；记录query/queue/worker成本 | 满可丢非权威诊断并增加dropped计数；不得丢业务日志，也不得同步console阻塞主循环 |

QT/QX是每Runtime运输/在途上限，不冒称跨独立宿主的设备业务并发锁；业务占用仍按原M05跨宿主claim与每项目并发。共享许可只管理 CPU/rebuild，不管理执行授权。许可实现使用原设备资源协调 seam 中独立的临时计算许可：持有者为 `(hostGeneration,jobId)`，由真实受管worker退出回收，不能只凭超时认定已退出。许可状态与业务 claim 分表，任何回收不释放文件/工具资源。实现登记在05中。

## 3. 内存与磁盘背压

Query 结果缓存最多32 MiB/256项，纯索引连接cache最多16个、总page cache64MiB；无全历史JS数组cache。上下文最多8个已准备请求/32MiB，不适合内联的大内容使用原blob/附件refs，Provider的真实token准入仍按原权威计量。Node worker192MiB上限指V8 heap；接入独立Rust Core进程后按原生有界内存预算控制，不伪称内核硬限制或OS沙箱。

普通未结command参数合计64MiB/数据根，控制command独立预留16MiB。已经接收的记录不因为配额变小而删除；停止新普通接收并继续结算。磁盘实际耗尽时无法保证耐久接收：返回 LOCAL_PERSISTENCE_FAILED，Runtime 内存立即关闭该执行的新工具准入并沿原 Stop Port 尽力中断，明确 `interruption_may_have_started`，不报耐久停止成功。原claim/unknown保留，恢复按原source回执对账。

已结command日志不做自动GC，避免operationId复用产生重放。其参数在结算后可原子替换为digest/原领域receipt refs，但operation identity和结果永久保留；immutable附件refs的保留权沿原artifact策略，不在本案新增GC。达到设备磁盘阈值只停止新普通接收，提示受支持的备份/诊断；不自动删历史解锁。

## 4. 锁、等待与公平

不持有Repository写锁等待模型、用户批准、Platform modal、子任务、网络或worker排队。采用 prepare → 在原短锁/事务内CAS commit。不同聚合能并发；跨聚合流程用明确step receipts，不拿一个全局mutex包住全部工作。

控制提交与普通提交分开排队；同一聚合已提交的次序不可逆，控制不越过一个已开始的耐久写。控制意图先在原ControlOperation记录，再关闭新dispatch；查询不会占有执行聚合的写锁。

同优先级按接收序号FIFO，项目间deficit round robin、每轮最多4个admission，避免一个Bot事件风暴饿死其他项目。普通补偿/扫尾从原 durable候选分页发现；不为扫描全部项目而占用control循环。30秒周期只做有界对账/索引检查，15秒每视图全量轮询退出已迁移入口；无变化不唤醒模型。

## 5. 期限和取消

各跳传剩余预算，不重置deadline。命令响应超时不停止已接受业务；查询超时可终止纯计算，引用仍在。停止屏障仍使用现行30s观测窗口，超时进入reconciling/unknown，不能延长timer制造通过。模型、工具和人工批准沿现行配置；内部资源限额不能变成新的任务总执行上限。

worker纯prepare取消可丢临时文件；commit开始后的取消只阻止新步骤并等待lookup。读取取消不取消任务。借用交互/核验槽的任务在下一合法让出点归还，不能通过kill丢结果。所有slot在finally与实际worker/handle退出事实中释放，重复release幂等。

QR纯job的进度、10秒停滞处理及真实exit确认固定见06，不能把timer到期当成释放证明。Store commit与Provider/tool的取消各走自己的原回执，不复用纯计算job的终止捷径。
