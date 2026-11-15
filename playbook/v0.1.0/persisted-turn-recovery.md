# 持久化终态、失败恢复与新输入响应修复

创建时间：2026-11-06
最后更新：2026-11-06
状态：源码候选已通过范围内验收；未发布、安装或恢复个人原任务。

先过 origin/main 的 ADR 图谱，已读 ADR 91、94、95、96、99、110、116、117、120。95/96/120 已覆盖本次行为，本轮补充现场、不变量和验收，不另起 ADR。Protocol 故障归属为 A 级收紧，宿主实施为 B 级；持久格式、权限与 Evidence 执行边界保持。未接受 ADR 113/119 不作为实施依据。

源码基线为 Peer-Agent origin/PeerAgent/dev/0.1.0@156c959f（rc.37）；知识基线 24b3906。隔离分支 codex/persisted-turn-recovery / codex/persisted-turn-recovery-adr。原工作区、运行实例、个人任务不改。

现场只读身份：parentConversation=084a3d1f-d533-49ce-bb76-a4da2baa0b26；session=eb32ba58-9b43-4868-a4cf-a74206ef9cf6；plan=f94e56ae-ee59-47a8-9d8f-8a783d10678a；resumeOperation=b010099ff2e0c4393736bf3210712810dc858d875d5c52266662efe872c1880f。15:40 初始持久化失败、16:01 接管后仍 failed/0 tools；16:04、16:06 等待被拒；16:10 原工作仍 runnable，新问题（input c2ee6304-5c19-410f-a046-be2e32f054a8）未续跑。具体因果待隔离生产 seam 复现，不将原数据写入仓库。

| 验收 | 场景与操作 | 预期 | 验证方式 |
|---|---|---|---|
| F1 | 真实 Goal Host/Conversation Store 发起受控回合，追加占位、流式、终态提交 | 同一真实 messageId 正式落盘，模型/工具不重放 | 实际 Store + Host 集成；修改前反例、提交回执、JSONL 读回 |
| F2 | 并发 append/replace/压缩、删除、版本冲突及晚提交 | 保留新输入，精确消息身份；不复活被删除目标，不假 done | 实际 worker/锁/文件测试，临时目录 |
| F3 | 存储错误、终态前后崩溃/重启 | 原始 cause、Tool Result/Evidence、可恢复 sidecar 保留；不重放未知工具 | 受控故障及生产终态 barrier；区分模型与本地故障 |
| F4 | 技术失败后同 work/session 恢复；立即再次失败；已完成步骤混合 | 当前绑定合法、安全步骤恢复；completed/queued 不等于开始/成功；历史和已完成步骤保留 | 真 Supervisor/Scheduler/Runner，重建 store/计数，结构化事实 |
| F5 | 同一错误反复查询、读取报告、新包装/UUID/时间/换模型/重启 | 有界收口、不伪进展；真实新材料仍可观察；具体 blocker 和 Bot 责任保留 | Progress Policy + Runner 跨回合/重启，精确调用数 |
| F6 | 旧 wake 无 userInputs 但 updatedAt 一直更新，新 user 已让出等待续跑 | 原新输入优先，后台不能每更新就抢先；历史同级公平有序 | 真实 Runner Coordination selection、可控时钟/原检查点 |
| F7 | 停止、人工等待、unknown effects、旧 revision/epoch/租约失效 | 拒绝越权/重放，不复活；无关新输入继续准入 | 原恢复/控制/权限 seam 与异常矩阵 |
| F8 | 代表性卡住状态副本，多次恢复和后续输入 | 一次合法续跑、无重复副作用/回复、不擦历史；证据绑定最终候选 | 隔离持久 store/ConversationStore + 真实执行链；类型/构建/架构和相关测试 |

验证比例：修改前反例与实际 host/store seams 先建立；范围内测试、包构建、类型/架构检查；相关全包用于回归。真实模型、安装版升级、个人原任务恢复与完整产品回归单独标记未验证。纯文档只审阅内容/diff，不以补测试代替复现。

## 实施与验收记录

代码候选 [b079f522](https://github.com/ly-ccx/Peer-Agent/commit/b079f522ec8dd84e315158c1f00d47274d11bc5c)，基于 rc.37 `156c959f`，23 个本轮文件。范围内源码指纹 `c4ea7b983b85031cb772e12e6e931584b80643ff15b7310dd516dd90b9f729d6`；逐文件 hash、实际命令和日志 hash 见[证据清单](evidence/persisted-turn-recovery.json)。原工作区的其他改动未进入候选。

| 验收 | 实测结果与证据 | 限制 |
|---|---|---|
| F1 | 修改前 aborted/error 两个真实 Router 回调排队了全量替换，覆盖下一 Goal Host 占位并导致精确终态提交失败；修改后 done/aborted/error 三路各一真实 Host 回合提交成功，草稿保留 | 通过实际回调、状态 Store、Goal Host 和 Conversation Store 构造竞态；没有逐事件重放现场第一次删除 |
| F2 | Conversation Store 终态 worker 并发 append、跨进程写、版本冲突、删除/替换/损坏/晚提交、超时与崩溃恢复检查通过；目标不存在仍拒绝，不复活 | 压缩/交互身份相关包测试通过，未新增完整应用压缩时序录像 |
| F3 | 本地提交超时在修改前即使带机器故障前缀也调用认知 3 次，修改后异常及 result 两路各 1 次，原原因保留；终态 barrier 的失败/侧车检查通过 | 脚本认知，无真实网络模型；不将 Tool Result/文件内容当成新 Evidence |
| F4 | 真 Supervisor/Scheduler/GoalRunner 从本地失败叶子进入第 2 个实际回合，完成兄弟叶子与标准保持，原错误历史保留；同操作重放不再执行。再次立即失败仍 failed/host，transition completed 不等于执行成功 | 受控认知/隔离执行标记，不冒充原任务验收 |
| F5 | 完整查询工件规范化到原材料；截断包装、路径/UUID/hash/读取范围变化不续预算。真父 Runner 经重启第 3 次重复后 no_progress；再次重启零新增调用；独立新输入正常答复一次 | 截断内容不能证明新进展，原工具参数和 Evidence 未改；普通文件路径/内容 hash 与完整新材料仍能产生新观察 |
| F6 | 修改前旧 wake 抢占 new；修改后刷新旧工作并重开 Store 三次仍选 new，处理后旧工作仍可选。原纠偏测试和新带时间的“纠偏承接/更晚独立输入”测试通过 | 缺到达时间不假造新到达；同输入显式承接优先，非累计硬预算 |
| F7 | 原人工/暂停/取消/未知效果/旧绑定/失租矩阵通过；新增真实未知子工具回执挡住技术失败准备，failed/Evidence 保留。新 followUp 保留 Bot 当前责任，无需伪造用户确认 | UI 原状态投影/草稿与事件专项；未运行签名安装版或系统辅助技术 |
| F8 | 冻结现场失败状态移植到独立权限/路径/绑定：原 632963 字节会话和 498 字节 abandoned 文件保持原字节；旧目标仍拒绝，新 Goal Host 回合正式提交一次，重放零新增；原 0 条验收结果保持未验证 | 保留现场 tasks/runner/runTrace/消息字节，身份来源以 manifest hash 绑定；fixture 接管合法权限并非操作个人原任务 |

总计：Runtime **2018/2018**，Protocol/Conversation Store **464/464**，Desktop 专项 **152/152**，冻结副本 **1/1**；桌面构建、Protocol/Runtime/Desktop typecheck、架构与 SVG/UI 检查通过，IPC 检查包含在桌面 build。无 skip/cancel。所有整包检查绑定冻结源码；最终额外只把宿主测试路径转换改为 fileURLToPath 以兼容 Windows URL，并重跑该测试 3/3，通过；运行实现未再改变。

### 失败尝试与纠正

初始四个反例均失败（两个终态写回、重复包装、旧 wake 排序），恢复反例显示只执行 1 次而预期恢复到第 2 次；本地超时异常/result 反例均为 3 次而非 1 次。没有删除保护断言换取通过。

第一次 Runtime 扩展运行 1995 pass / 6 fail，保留为失败结果，不当最终验收：并发 Desktop 构建更新 dist 导致一次缺导出，Electron 依赖因 offline ignore-scripts 未准备导致两个文件加载失败；旧纠偏续跑测试暴露本补丁排序回归，已补同输入显式承接且保留原期望；另一个既有未知效果测试因临时改了前置状态触发了不同原闸门，已恢复原测试，并新建本地失败+未知效果用例。依赖准备、构建、测试现按顺序执行，最终整包 2018/2018。

新增测试第一次完整新材料检查使用 failed 诊断摘要，按原失败分类契约不会构成进度；改为 result_ready 的真实新材料，并保留 failed 重复诊断测试。父 Runner 重启测试初次未提供 native checkpoint，正确被原恢复门挡住；补齐成对的原 checkpoint 后验证 3 次有界收口。冻结副本测试初次缺本地 lease 及共享 Scheduler，原门正确拒绝；补齐隔离宿主后，又证实旧 intent=block 会被带入新回合，实施已改成仅对本次安全技术准备选 execute。准备中崩溃的同 operation 重入也沿 runTrace 保留 execute，不重复准备。

### 尚未覆盖

实施者自审，非独立审阅。没有真实模型、Windows/Linux 执行、安装版升级、完整产品 Capture/Review/Verify、系统辅助技术或个人原任务恢复。现场第一次丢失 assistant 的确切事件仍未逐条重放；已证实可产生同一错误的真实跨层竞态及副本恢复，不将其写成唯一已证实根因。源代码和副本通过不等于原用户任务已完成。自动 CI 以 PR 实际结果为准，不借本地通过冒充远端。
