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
| SessionControl | 子执行身份、停稳屏障、unknown 集合与资源结清回执 | 接管消费其结果，不再次自行解释父预算 |
| SessionTakeover | 旧执行停稳后绑定新 epoch、交接反馈、重新排队 | 从真实 control 结果选择继续或 awaiting_outcome |
| Supervision recovery | 当前 control/transition 的恢复条件 | 原操作的当前空 unknown 停止证明可恢复误挂 transition；版本、身份、代次严格匹配 |
| SessionContinuity | 原生暂停/恢复的准入与幂等 | 接管仍 stopping 时拒绝并行 native resume，保留原控制及代次；prepare/commit 共用准入检查 |
| Wake wait / Repair progress | 已准入等待与重复尝试的区别 | 静默等待既不积累也不清零无进展次数 |
| RunnerCoordination | 保存回合、等待对象、事件责任与原目标 | 等待保持 waiting_children，不写失败、完成或交付 |
| 模型与 ReplyDelivery | 模型选择处置；正式回复须核对当前事实 | 不用“已恢复”文字代替执行回执；缺合法处置仍失败关闭 |

修复不删除 work_disposition_required、不放宽 unknown、不把 queued/starting 当 running，不迁移存储或增加另一套执行路径。修复阻止未来 native resume 覆盖未完成接管；已经出现的新 generation 与旧接管组合仍须按最新控制事实核对，本轮不能据源码修改宣称当前个人任务已恢复。

## 验证范围

新增真实 Module 的回归用例，覆盖 active Intent 的重复等待、父协调 pending 调用、子执行 unknown 保护，以及停止回执身份/代次不匹配拒绝恢复。仅内容和 diff 审阅；未运行测试、构建、类型/架构/IPC 检查、真实模型或安装版产品回归。完整验证留到发布，除非用户另行明确要求提前验证。

## 自动 CI 的实际失败与补修

用户追问交付责任后读取了 PR268 已有的[自动 CI 41566935511](https://github.com/ly-ccx/Peer-Agent/actions/runs/41566935511)，没有手动触发或重跑工作流。候选 82b186ea 在 Linux/macOS 的 Build、Typecheck、Architecture 步骤成功，但 Test 失败，Electron smoke 因此前失败而跳过。这些工程检查不等于任务恢复验收。

失败为本轮补丁引入：旧 transition 缺 operationId、旧 session 缺 origin 时，两边 undefined 被比较为相等，后续读取 takeover 抛 TypeError。原有用例已覆盖并在自动单文件重试后仍失败；不能称为偶发或已通过。提交 81efd234 要求非空操作身份并保护缺省字段，保留原用例且补充不完整旧对象的拒绝恢复断言。补修只经内容/diff 审阅，新的自动 CI 尚无本记录确认的结果。

交付仍为草稿，未安装或修改个人任务。下一次发布验收须在隔离数据副本复现原失败链，确认原任务身份保留、等待不误失败、接管与 native resume 不交叉覆盖、对账后相关任务和同目录后续任务实际进入执行；真实未知 shell 的保护与无法证明的恢复部分单独报告。不得用 CI 通过替代这条实际任务链的恢复证据。
