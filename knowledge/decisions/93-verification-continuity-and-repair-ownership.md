# ADR 93：复核续跑与未完成工作的处理责任

创建时间：2026-10-18  
最后更新：2026-10-18  
状态：Accepted（用户明确要求“出完整的修复 ADR 文档，然后着手根治这个问题”；本决策先于实现记录）  
级别：A（状态、续跑、错误及持久化契约），B（协调与核验运行时）  
依赖：ADR 80、83、85、88、89、91、92；产品方向沿用 `design/product/peer-product-alignment.md`。

## 1. 问题与现场证据

RC15 的实际任务已经完成代码与隔离产品回归，却在独立复核失败后停下。主 Bot 发出“独立复核仍失败，尚未验收”的汇报后，没有保存后续处理责任。此处没有未回答的人类问题，也没有未批准的人工标准。

已核实的故障链：

1. 两次核验运行均因桌面 Verifier 固定 12 轮的限制退出。该限制被当成执行失败，原生上下文没有用于接续。第三次异常被抹成 `verifier_failed`，不能反推第三次也由轮数导致。
2. `verify_session` 捕获异常时丢掉具体原因。另一次 focus 超过 500 字被拒绝；查询协调状态却要求先给出查询才知道的 goalRevision。
3. `deriveSessionFacts` 将所有 `runner.blocked` 映射为 `waiting_user`。Watchdog 再为每个 blocked 合成一条 question，即使没有真实问题。
4. 父协调器将一次成功汇报视为该批次处理完毕：子任务被误判为等待人，父责任进入 waiting_user，waitFor 为空，事件已处理且没有自动续跑责任。现场父预算仍有余额。
5. 旧任务无 ADR91 mandate，查询与修复不能依赖新任务才有的绑定；成功重查只允许关闭只读任务，对已经完成写入、仅剩复核的任务也不能收口。

以上来自本地持久事实及生产函数的内存重现，不通过修改用户数据修饰状态。具体会话正文和机器路径不进入架构文档。

## 2. 目标与不变量

- Bot 对已经授权且未完成的工作持续负责，包括检查失败原因、继续复核、修复和交付。普通进展汇报不能消除责任。
- “等待用户”必须由真实的人类请求支撑：计划批准、工具权限、待答问题或人工验收。技术阻塞由主 Bot 接手；无法自动恢复时明确标识系统阻塞。
- 软切片只让出执行权。硬预算、总截止时间、权限拒绝、取消、未知工具结果和无进展保护仍限制自动执行。
- 继续核验保留已配对 Tool Result、Evidence 和原生 Provider 上下文；不重做完成的写入，不将报告或聊天文本当权限、证据或人工签字。
- 通过仍需要当前版本的完整闸门。独立复核不是实现者自审，也不等于签收、安装、合并或发布。

## 3. 顶层 Module 与责任

| Module / Seam | Interface 与责任 | Implementation 落点 |
| --- | --- | --- |
| Session Facts | 输出执行状态、真实 needsUser 和技术阻碍；真实终态和人工请求优先 | Protocol 纯投影；Runtime 从计划、活跃核验和问题事实装配 |
| Continuation Obligations | 从当前关联 Session 推导未解决责任；控制汇报后的 runnable / waiting / blocked | 既有 ProjectWorkReceipt 与协调 checkpoint；不另建任务表 |
| Verification Continuation | 有限核验切片、累计额度、原生 checkpoint、版本绑定、格式重试、取消与超时 | 独立共享 Module；桌面 Executor 只适配既有 Provider Loop |
| Verification Failure | 保留 code、message、下一步，按类别决定能否继续 | Session verification 及 report decoder 共用失败归一化 |
| Verification Settlement | 不重放 Worker，重算全闸门后关闭纯复核阻塞 | 既有 GoalRunner completeRecheck Seam |
| Coordination Discovery | 查询真实当前版本，不要求模型先知道版本；修改仍 CAS | 既有 coordinate_work 的只读 query 分支 |

本地执行链仍为 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。UI 和 System Context 都不签发执行事实。

## 4. 状态与处理责任

1. cancelled / failed、已签收、取消或接手等待未知结果等权威终态沿用原优先级。
2. 有真实未解决的人类请求才是 waiting_user。`runner.waiting_user` 与宿主 `waitingOnUser` 继续表示真实请求；普通 blocked 不生成 question。
3. 活跃核验显示 verifying，即使之前的 runner 仍记录旧复核阻塞。持久 verifying 标志不证明活跃执行。
4. 技术 blocked 投影为既有 waiting_agent，表示主 Bot 应接手，不引入与任务存储竞争的新状态。实际 blockedReason 保留。
5. 父 Bot 汇报后，关联 waiting_agent 仍使工作 runnable；未答的子 Agent 工作问题也由父 Bot 处理。正在执行的子任务继续等待真实事件；真人请求进入 waiting_user。
6. 无进展、硬预算、明确停止、Provider 不能恢复或未知结果优先，不能被“仍有责任”覆盖成无限自动运行。

责任由当前 Session 的身份与版本推导，存入既有 receipt / checkpoint。事件 handled 表示责任已转交给持久协调工作，不能表示目标完成。父任务恢复时重新读取 Session；已取消、被取代、暂停、签收或版本变化的对象不因旧快照复活。技术等待不能吞掉其他任务和新用户输入。

旧 waiting_user receipt 仅在宿主当前事实证明所有相关等待均无真人请求、确有 waiting_agent 且已有有效 checkpoint 时转回 runnable。不改旧人工决定、目标正文、原始消息、完成历史或预算。无法解析的旧责任保持可诊断，不猜测其授权。

## 5. Verifier 的有限续跑

### 5.1 两级限制

12 轮改成核验软切片：Provider Loop 在一批工具结果配对后返回 yielded 与原生 checkpoint，不抛出“任务失败”。宿主在同一次独立核验责任内继续该上下文。每个核验责任另有有限累计请求 / 工具额度与原有最多 5 分钟总截止时间；格式修复也计入同一额度。有关联工作预算时仍经既有 WorkBudgetGuard 累计，不为重查、重启或切片重置真实 allowance。

默认核验责任最多 96 个模型轮次、512 次工具调用；这是最后的安全边界，不是每片重置的额度。用户或全局工作预算更小则先停止。不能声称请求数可以精确限定 Provider 费用；真实物理 dispatch 仍由原计量入口预约。

### 5.2 恢复状态

已有 GoalPlan.runner 增加可选核验续跑元数据：源版本、模型身份、累计消耗、截止时间、原生 checkpoint 引用、格式重试阶段及 indexed tool result refs。原生内容放入已登记的 projectRuntime/checkpoints；元数据不是 Evidence，也不是新 Context Source。Provider Encoder 仍负责原生格式，恢复时经现有 providerCheckpoint Seam 读取，不能把内容提升成系统指令。

有本地工作区协调存储的委派核验可跨宿主恢复；没有该端口的普通 Goal 仍支持本次调用内的软切片，但不宣称跨进程恢复能力。恢复前重检宿主租约、计划源版本、模型、停止状态、截止时间和剩余额度。已关闭/取消或源变更的责任不能使用旧 checkpoint。保留已知调用结果，不从文字摘要重造调用；未结算 dispatch 沿 ADR92 后续恢复审计处理，不能直接重试。

每个计划同一时刻最多一个独立核验 continuation。持久化失败立即停止，不假装保存成功。checkpoint 缺失、损坏、身份不符返回明确错误，不静默从头运行。旧未保存原生现场的失败可以开始一次新的有界核验，但保留原失败历史与工作累计预算。

### 5.3 失败处理

| 结果 | 后续 |
| --- | --- |
| 软片结束 | 保存已配对现场并继续，不向用户报任务失败 |
| 合法失败报告 | 保存具体未通过项、证据和修复建议，主 Bot 决定修复；不冒充通过 |
| 格式不合法 | 一次有界格式修复；仍非法保留具体错误 |
| 取消 / 权限拒绝 / 超时 / 真实预算耗尽 | 立即结束这次自动执行，保留原因；不扩大授权、自动续期或另起任务逃避限制 |
| 工具结果未知 / checkpoint 不可用 | 系统阻塞，先核对执行事实，不重放副作用 |
| 重复观察且无新事实 | 既有无进展保护终止重复调度并交付明确阻碍 |

异常原始 message 有界保留；`verifier_failed` 是类别，不再替代全部诊断。返回当前阶段和可采取的下一步；路径、密钥和整段 Provider payload 不无差别暴露到主回复。

## 6. 安全收口、旧任务与工具发现

成功重查可关闭“所有叶子任务已完成，仅剩 verifier_failed / verification_gate_failed”的空闲委派任务，包括之前写过文件的任务。必须同时满足：目标与报告版本相同、当前 host independentVerifier 通过、完整 gate 通过、无活跃 Worker/Verifier、无停止或取代、无未满足的 UI 交付闸。原命令、人工标准、产品回归和交付证据不得绕过。仅修改 runner 收口状态，不重新执行 Worker，不自动 merge / install / release。

coordinate_work query 只读回当前主 Bot 所属 Session 的当前事实与可用 goalRevision。没有 mandate 时返回明确 legacy 状态与当前事实；不通过查询自动制造 mandate、扩大权限或启动执行。后续写动作继续要求真实来源锚点、现有协调准入和 expectedRevision。工具 schema 明示 focus 的 500 字上限，减少“调用时才发现”的反复。

## 7. 实施顺序

1. 以实际故障链建立确定性回归：技术 blocked 被误判、汇报后丢责任、12 轮失败、原因被吞、写任务重查不收口、查询需要预知版本。
2. 改 Protocol 事实投影及 Watchdog，保留真实人类请求。
3. 新建核验续跑 Module，适配既有 Executor 的 soft yield 和 providerCheckpoint；在既有存储与预算 Seam 持久化。
4. 补充父协调责任与旧 receipt 恢复，保留取消、预算、未知结果及无进展边界。
5. 修复诊断、只读发现和纯复核收口。
6. 聚焦测试、受影响包全测、build/typecheck/architecture；若用户可见投影或文案变化，执行产品 Capture → 全图实施者自审 → Verify。

## 8. 验收与限制

必须覆盖：跨 12 轮继续并返回合法带证据报告、格式修复累计计量、恢复不重复读/写、源版本与模型变化、重启/缺失 checkpoint、持久化失败、取消/超时/拒绝、累计预算、并发核验、真实人工请求不被清除、写任务验证收口、无副作用重放、父汇报后仍可继续、旧 receipt 恢复及查询零变更。

使用生产入口与可控模型复现调度；真实 Provider 网络与模型语义质量单独记录。产品截图的实施者自审必须标 independent=false，不冒称独立复核。本次不修改真实用户任务和授权，不替换安装版，不含合并与发布。交付记录补充实际通过项及未覆盖项，不能只依据本 ADR 计划称已完成。

## 9. 迁移与回滚

新增字段为加法式；旧读者忽略 continuation 字段，旧失败记录保留。新读者只从经过校验的宿主续跑元数据恢复，不给旧文本补造 checkpoint、批准或通过证据。回滚代码不会撤销已发生工具结果；暂停自动恢复后仍保留原日志供诊断。未解析/未结算的记录不得因为回滚而自动重派。

## 10. 取舍

没有选择直接增大每次 Verifier 轮数：它仍会在下一次上限处丢现场。没有选择让 prompt 说“你必须继续”承担执行保证：持久责任、调度与权限必须由宿主落实。没有选择复核失败就让用户重新发消息：这会把技术恢复工作转嫁给人。有限切片与累计限制增加了状态校验，但将调试集中在两个 Module，能够实际验证何时继续、何时停止以及谁负责。
