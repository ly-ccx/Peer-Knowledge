# RC35 等待与接管闭环故障

创建时间：2026-11-03
最后更新：2026-11-03

范围：A/B 级契约澄清与共享 Runtime 修复。依据 ADR94、ADR116、ADR117；保留全部权限、Evidence、真人门和原目标关闭条件。源码基线为 RC35 `4a58e284`，运行安装包为 `0.1.0-rc.35`。原日常目录停在旧版本且有其他未提交工作，故在独立 worktree 实施；个人数据及运行实例只读。

## 现场事实

时间为北京时间。来源为当前 Conversation、GoalPlan、coordination-v2 派生账本、设备资源账本与安装包源码，不是复现或测试通过记录。

| 时间 | 事实 | 结论 |
| --- | --- | --- |
| 09:56 | 新任务 54a87584 建立并排队，子对话只有委托输入 | 尚未执行 |
| 10:03 | 接管 operation 0f0cb503 的 Session Control 已 settled/applied，stopReceipt.unknownCalls 为空；协调 transition 却为 awaiting_outcome | 接管层重复扫描父预算，混入自身仍在执行的 metadata 调用，推翻了停止屏障 |
| 10:04 | 原生 resume 增加 generation；旧接管仍 stopping，mandate 仍 revoked，新 generation claim 处于 draining | starting 不等于执行器启动；多个控制模块的收尾未闭合 |
| 10:06 | 主 Bot 回复“现已放行”；随后 wait_for_sessions 成功，保存 silentWait 的同一回合却以 agent_no_progress 结束 | 等待结束类型与无进展策略冲突 |
| 10:13、10:22 | 恢复回合只重复正在继续，两次 work_disposition_required | 没有实际协调动作，未恢复任务 |

另一已取消的旧任务 b677d3c1 仍有历史 shell 调用 call_072b86a229214024aed3a8f6 未知，其目录 claim 为 reconciling。applied 的撤回回执只结束跟进，不证明该 shell 的结果；不得清空真实 unknown 或声称目录已放行。这与新接管误报自身调用必须分别处理。

## 流转和职责

`用户输入 → ProjectAgentRunner → Delegation Provider/Projection/PermissionGrant → Coordination Lifecycle/Kernel → SessionTakeover → SessionControl → ExecutionScheduler/GoalRunner → Tool Result/Evidence → RunnerCoordination → ReplyDelivery`。

| Module | 持有的事实 | 本次修正 |
| --- | --- | --- |
| SessionControl | 子执行身份、停稳屏障、unknown 集合与资源结清回执 | 接管消费其结果；已有 native resume 交叉状态须先经同一屏障结清当前 generation |
| Takeover stop recovery | 原 proposal、canonical 锚点、stop/resume 回执链、当前绑定和实际执行事实的联合校验 | 窄范围接纳从未执行的旧交叉状态；与接管、transition 恢复共用当前停止证明，避免分散解释 |
| SessionTakeover | 旧执行停稳后绑定新 epoch、交接反馈、重新排队 | 从真实 control 结果选择继续或 awaiting_outcome |
| Supervision recovery | 当前 control/transition 的恢复条件 | 原操作的当前空 unknown 停止证明可恢复误挂 transition；版本、身份、代次严格匹配 |
| SessionContinuity | 原生暂停/恢复的准入与幂等 | 接管仍 stopping 时拒绝并行 native resume，保留原控制及代次；prepare/commit 共用准入检查 |
| ExecutionScheduler | 资源预留、排队准入及执行器选择 | 在预留和 running 写入前检查被撤销的绑定；协调等待不再被误写为执行失败 |
| Wake wait / Repair progress | 已准入等待与重复尝试的区别 | 静默等待既不积累也不清零无进展次数 |
| RunnerCoordination | 保存回合、等待对象、事件责任与原目标 | 等待保持 waiting_children，不写失败、完成或交付 |
| 模型与 ReplyDelivery | 模型选择处置；正式回复须核对当前事实 | 不用“已恢复”文字代替执行回执；缺合法处置仍失败关闭 |

修复不删除 work_disposition_required、不放宽 unknown、不把 queued/starting 当 running，不迁移存储或增加另一套执行路径。除阻止未来 native resume 覆盖未完成接管，还为已出现的交叉组合补充严格恢复条件；源码和隔离用例仍不能证明当前个人任务已恢复。

## 最初交付阶段的验证范围

最初两次提交新增真实 Module 的回归用例，覆盖 active Intent 的重复等待、父协调 pending 调用、子执行 unknown 保护，以及停止回执身份/代次不匹配拒绝恢复。当时只做内容和 diff 审阅，未在本地执行。此项为历史阶段记录；用户随后要求将验证和存量恢复责任写入长期开发共识，本轮据新共识进行了下述范围内的验证，不再用旧规则作为交付依据。

## 自动 CI 的实际失败与补修

用户追问交付责任后读取了 PR268 已有的[自动 CI 41566935511](https://github.com/ly-ccx/Peer-Agent/actions/runs/41566935511)，没有手动触发或重跑工作流。候选 82b186ea 在 Linux/macOS 的 Build、Typecheck、Architecture 步骤成功，但 Test 失败，Electron smoke 因此前失败而跳过。这些工程检查不等于任务恢复验收。

失败为本轮补丁引入：旧 transition 缺 operationId、旧 session 缺 origin 时，两边 undefined 被比较为相等，后续读取 takeover 抛 TypeError。原有用例已覆盖并在自动单文件重试后仍失败；不能称为偶发或已通过。提交 81efd234 要求非空操作身份并保护缺省字段，保留原用例且补充不完整旧对象的拒绝恢复断言。[后续自动 CI 41567944884](https://github.com/ly-ccx/Peer-Agent/actions/runs/41567944884) 已成功，但只覆盖 81efd234，不覆盖本轮后来增加的存量恢复实现。

## 存量恢复及针对性验证

原现场已经有 applied native resume，只有防止下次交叉的补丁不足。先将原 proposal、旧停止回执、后续 resume、canonical 锚点、当前撤销绑定和资源状态保存在仓库外的最小只读快照，再用真实 Conversation/GoalPlan/Coordination Store、Session Control、Scheduler 与 Supervisor 端口在临时目录重建该形状。模型执行器为受控替身；这是现场形状的隔离重建，不是对用户完整数据库或安装版的端到端复现。

补修前新增冷恢复用例无法结清原 transition。补修按 ADR116 的窄范围规则，为从未实际执行的新 generation 经原屏障取得新的 pause 停稳回执，再从原 proposal 恢复原 GoalPlan 和 session。新增恢复还暴露了排队调度先选中 revoked binding、再失败为 execution_resource_owner_changed 的路径；现已在资源预留前按权威 lifecycle facts 拦截。没有删除或放宽原来的 unknown、代次、权限或验收断言。

隔离验证区分三种结果：无其他阻挡时原任务只进入受控执行器一次，重复 reconcile 不重复启动，停止后同目录后续任务可准入；恢复 pause 已写入但尚无回执时再次换宿主，仍可续接同一操作；另有历史未知 shell 时只恢复原任务接管责任，执行器启动次数保持 0，原 claim 保持 reconciling、unknown 引用保留，阻碍仍明确为 execution_outcome_unknown。另有独立目录用例验证其他物理 worktree 不受该范围外 unknown 阻塞。

最终候选身份、实际命令、用例统计和日志摘要见[验证收据](evidence/agent-wait-recovery/validation.json)。验证使用 Node 24.22.0，范围为受影响的 Runtime Module、运行包构建与类型检查；实现者自审，不称独立审查。未执行真实云模型、当前安装版、UI/可访问性/全平台或完整发布回归。完整发布门禁仍须在全部 PR 合并后的最终候选执行。

## 未完成的用户现场闭环

修复及共识 PR 已分别推送，均不等于已经合并、发布或安装。运行中的 RC35 和个人任务事实没有被本次测试改写；只读快照中的原 GoalPlan 和父对话在验证前后内容摘要相同。新任务目录仍有另一旧任务的真实历史 shell unknown，现有本地材料不能证明其结束/退出结果，不能凭无 PID、取消终态或模型回复解除该保护。

因此当前交付仍是待审源码候选。现场恢复需要由包含该修复的宿主按原控制和资源协议对账；历史 unknown 必须有可核对的结束事实，或通过产品支持的独立物理工作目录恢复工作。当前安装版实际执行进展、原业务改动结果和用户验收均未完成。不得要求用户安装或重试来代替实施者的验证，也不得用 CI 或隔离执行器通过宣称原业务任务完成。
