# 任务控制与资源交接实施卡

创建时间：2026-11-01
最后更新：2026-11-01

状态：Accepted、源码已实施并自审（2026-11-01；SC-R 未执行）。唯一决策入口：[ADR116](../../knowledge/decisions/116-session-control-and-resource-settlement.md)。

## 1. 范围和执行约定

目标：旧接管不永久占槽；确认停止后新任务自动继续；活体执行、未知副作用、权限和签收仍受保护。

这是 A/B 级运行时工作包。用户已授权整体实施，按卡片依赖顺序推进；不因单卡拆分重复请求批准。文件锚点相对 Peer-Agent；实施基线为 RC31 主线 73ff763a。保护用户数据、当前应用、凭证和其他未提交改动；不复制架构知识到代码仓。

依赖顺序 SC-01 → SC-02 → SC-03 → SC-04 → SC-05 → SC-R。日常只内容/diff 审阅、补必要用例，不自动跑测试；发布前全部门禁，提前执行需用户对当前任务明确要求。

## 2. SC-01：契约和纯决策

级别 A，规模 M。前置：ADR 获准实施，最低读写/executor 版本无撞号。

允许：Protocol 的 delegation-coordination/delegation/task-overview 及邻近测试，必要新 `session-control.ts` 和既有出口；runtime 的 coordination kernel/schema/reducer/store/derived index，必要新 `session-control-kernel.mjs` 和窄 public/build 出口；data-store 中拟新增设备资源 SQLite 的 scope/schema/备份/恢复登记。

实现：SessionControlOperation、StopBarrierReceipt、资源 claim/hold、blocker；CAS、引用关系、合法阶段、取消覆盖接管和格式保护。控制日志持有控制真源、设备账本持有资源真源，旧 GoalPlan 控制标记为可修复镜像。legacy 用户取消不造 mandate。

用例：同 ID 幂等/异参数拒绝；旧版本/跨域/伪来源拒绝；取消覆盖接管；历史签收不变；控制完成不等于任务成功；日志重放/索引重建一致；最低版本不降。

退出：契约和存储责任完整、必要用例已写并审阅。未执行不称通过。

## 3. SC-02：统一停止屏障

级别 A/B，规模 L；依赖 SC-01。

允许：session-cancellation/takeover/facts/repair、execution-ownership；新 `session-control.mjs`；现有 Runner/Executor/Provider 取消、句柄及 terminal barrier seam 和邻近测试。Supervisor 仅接线，不加业务。新 Provider 适配不增中心 capabilityId 分支。

实现：fence → signal → drain → reconcile → settle；覆盖 Worker/Verifier/Explorer/受管工具/终态提交。异步尾部失去当前性要明确 superseded/rejected，不直接返回留 stopping。请求接收、受管停止、历史 unknown、用户撤回各自记录。

用例：接管中取消及迟到尾部；取消后接管拒绝；真实 live、abort/提交失败、丢租约不造停稳；撤回结清但 unknown/预算/Evidence 不变；重复控制/旧 finally 不影响新 epoch；无 token/PR merged/runner cancelled 均不单独证明停止。

退出：所有控制共用屏障；取消器和接管器不再独立持有停止真值；无法确认停止的 adapter 缺口明确。

## 4. SC-03：资源准入统一

级别 A/B，规模 L；依赖 SC-02。

允许：execution-scheduler、isolation-planner、execution-context、goal-runner-host 的准入、Supervisor promote/reserve 接线及邻近测试；必要新 `execution-resources.mjs`。

实现：替换裸 occupying；统一 inspect/reserve/activate/settle；复用现有 SQLite adapter，设备级账本对同一规范资源原子 reserve，start 前重检控制和宿主身份。隔离规划消费相同资源身份和冲突；维持只读限额、协调保障、优先级/老化及 Provider 限流。claim/hold 交接与通知 outbox 同一事务；项目日志和账本按保守幂等顺序提交，不宣称跨存储原子。多资源全取或全不取，不持有部分资源等待。

用例：不同进程/不同 workspace 的两个候选同目录只有一个合法写拥有者；账本 busy/丢响应按操作回执恢复；多资源反向请求无等待环；启动前后失败区别是否 dispatch；alias/symlink/跨 workspace 同目录冲突；独立 worktree 正确放行，共享 Git/外部范围不假隔离；等人释放计算不破坏现场；cleanup 失败不占无关目录；released+live 触发一致性阻塞；旧 finally 不放新 claim。

退出：Scheduler、IsolationPlanner、Runner 不各算一份写者；停止确认后自动 promote，资源分离不引入全局队首阻塞。

## 5. SC-04：恢复和遗留收敛

级别 A/B，规模 L；依赖 SC-03。

允许：coordination-lifecycle/recovery-service、supervision-recovery、recovery-policy、session-host-handoff、现有 lease/writer-fence 适配及控制/资源 Module 和测试。新增存储项才触及 data-store 登记。

实现：拥有写者权后还原控制/claim/hold，按资源开放；恢复原操作，镜像/队列/事件幂等补齐。原取消回执有足够权威依据时追加收敛旧 takeover；不足则同屏障核对。不改旧 Tool Result/unknown，不批量凭 cancelled 猜结束。

用例：ADR116 §9 每个崩溃窗口，尤其项目日志/设备账本先后提交；双宿主、PID 复用、孤儿进程、回执缺失/损坏、丢 manifest/index、资源 DB 缺失/损坏与 WAL 备份、镜像落后、时钟跳变、缺 scope 保守保护、同事实不反复唤模型。

必须有隔离夹具复现真实形态：旧任务 `cancelled + cancellation.completed + takeover.stopping`，新任务 queued。有匹配停稳依据时旧接管明确 superseded，新任务无需新输入即推进；无依据/有 live 时仍保护。不得直接加载或编辑用户生产数据，不删除标记模拟修复。

诊断返回资源/控制身份、阻塞依据、已完成和未完成的停止阶段、范围、责任、合法下一步及 replayAllowed。默认脱敏，不输出凭证或整段私有正文。

退出：没有仅凭残留字段永卡队列的合法状态，没有重放未知副作用快路；不安全降级被拒绝。

## 6. SC-05：同源状态和恢复入口

级别 A/B/C，规模 M；依赖 SC-04。

允许：Protocol decideLifecycle/WorkSession、runtime session facts/read/query；Desktop drawerState/botWorkState、Agent 活动行/详情；TUI 消费者、i18n 和邻近测试。IPC 仅在需要时扩展现有 typed 通道；知识仓更新交互及 UI/动效/过渡矩阵。

实现：followUp 与 resourceProtection 分开，所有表面消费同一 blocker。排队、正在停止、安排接手、历史 unknown 各有真实依据；hold 不伪装当前任务。没有强制解锁按钮；沿现有查看/取消/诊断/接管。后台不抢焦点、不丢草稿、不改阅读意图。

用例：列表/计数/详情/TUI 一致；撤回退出列表但 unknown 历史可查；新任务显示实际资源保护；真人门不被吞；旧点击重校验；快速导航/IME/reduced-motion/读取失败保留恢复。

退出：文案和动画不造状态；矩阵只标实际源码审阅，不能填产品验收通过。

## 7. SC-R：最终组合候选验收

发布门禁；SC-01—05 全部合入，按 AGENTS.md 清点审阅并合入代码仓所有开放 PR 后冻结候选。

| 层 | 必需证据 |
|---|---|
| 协议/纯决策 | 全转移、幂等、旧版本/来源/跨域、状态与 followUp 交叉矩阵 |
| 运行时集成 | 真实 GoalRunner/Provider/PermissionGrant/Evidence 链；取消/接管竞争；停稳先于 release，reserve 先于 start |
| 恢复 | 各持久步骤 crash/replay、双宿主、执行句柄、unknown 保留、版本拒绝、索引重建 |
| 活性/公平 | 单条旧异常不挡无冲突资源；停稳后自动 promote；等父代理不饿死协调；无变化不调用模型 |
| 产品 | 完整 capture → AI 逐图 review.json → verify；补本设计专用状态故事，不以通用图替代 |
| 真实运行 | 隔离数据根/项目，正常入口取消、接管、重新排队、重启和继续；至少一个执行无法立即停止的受控句柄场景 |
| 构建/安装 | 最终组合 build/test/type/architecture/IPC、打包后的 Module、旧数据升级和降级拒绝 |

量化：同一资源不得同时有两个合法写拥有者；取消后的旧代次新 dispatch 为零；相同回执不重复执行；合法候选在资源释放后无需用户新消息即可唯一准入；热 inspect/投影不逐次重放累计历史。分别记录请求接收、Provider 停稳、terminal commit、资源处置和新准入时间，不承诺没有 Provider 依据的统一停止秒数。

收据绑定实际代码/包、证据、实现者自审或独立审阅、模型/平台/安装包/辅助技术覆盖。推 tag 前再查开放 PR 为空。脚本传输或受控进程不能宣称真实模型和任意外部副作用已验收。

## 8. 本轮状态

SC-01—SC-05 已在 `codex/session-control-resource-settlement` 实现，[代码 PR252](https://github.com/ly-ccx/Peer-Agent/pull/252)，提交 `6923cc9a`（RC31 起始基线 `73ff763a`，已同步新主线 `0f68f281`）；模块、来源、资源扩容交接与边界见 [ADR116 §13](../../knowledge/decisions/116-session-control-and-resource-settlement.md#13-2026-11-01-源码实施收据)。新增 `execution-scopes.mjs`、`execution-handles.mjs`、`execution-admission.mjs` 和 `session-resource-contention.mjs`，集中 Provider 身份、实际句柄、准入和冲突交接，不向 Supervisor 填第二套执行器。

必需契约夹具已编写，完成内容/diff 与源码解析自审（independent=false）。未执行测试、build、type/architecture/IPC、截图/交互或真实模型/安装包验收；SC-R 未开始。未修改生产记录、清 unknown、安装、重启或发布，原应用和任务保持原状，不自动纳入下一版本。外部无可靠句柄的异步操作仍保留 unknown；本批不宣称任意外部对象或脱管进程已停止。
