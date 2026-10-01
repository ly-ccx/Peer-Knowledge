# B4-03 交接记录

创建时间：2026-10-01
最后更新：2026-10-01

## 卡片
B4-03 取代、恢复、排队全链路。

## 分支与提交
- `PeerAgent/pa/b4-03-session-continuity`
- `910f456f796c593b15ba44b0da13c6efdd5567d0`
- 基线：B4-02 已合入的 dev，`faa25d9c`。

## 改了什么
- 新深模块 SessionContinuity：取代暂停旧任务、等待异步工具结束，持久化取代关系并保留 worktree/成果；锚定恢复、恢复链暂停替换者、动作幂等、七天过期。
- 新 resume_session/reprioritize_session 沿现有 Provider/Manifest/Projection/Grant/Evidence 链注册，实际用户锚点、项目/父对话和引用范围在宿主/Provider 强制。
- Goal pause 关闭委托准入；审批和 message_session 不得意外恢复暂停任务；替换启动失败释放槽位并保留旧任务可恢复。
- 档案任务页暂停分组、取代名称、SVG 恢复动作；类型化既有应用服务命令先保存点击的用户输入事实，再调用同一恢复模块。经典界面和无租约时不维护。
- 新状态及 origin 字段由既有 Plan store 保存，已注册 Context Source 与提示同步。
- Review 修复：暂停/取代后仍可结构化拒绝授权；high 新建/调整统一要求当前用户的明确加急锚点，拒绝唤醒、旧输入、引用与否定。新队列消息标记 user_input，旧队列 ID 锚点兼容且不重写 jsonl。

## 与卡片的偏差
- 必要的协议、宿主、IPC/preload、Goal pause、当前回合事实/既有 toolContext 装配、输入队列 kind、新共享 urgency 校验、已注册 Context Source、i18n 与测试路径已先写知识仓实施契约。负责人授权自行完成全部 B4；无新增依赖，main.mjs 无改动。

## 验证
- pnpm build / pnpm typecheck / pnpm architecture:check / Desktop ipc:check / git diff --check：通过。
- runtime-node 完整套件：878 通过，0 失败/跳过。
- desktop 完整套件：5167 通过，0 失败，5 既有跳过。
- system-context：29 通过；Protocol：173 通过。
- 真实临时 Git 与生产 Goal host：三写 worktree 合回原场景通过；取代后未提交成果保留、恢复复用原 worktree 的新增场景通过。脚本执行器，不是远程模型证据。
- 覆盖取代→恢复→再取代、旧恢复锚点幂等、七天清理/重试、优先级重启持久、审批/引用/项目/用户锚点/待验收限制、异步工具结算、手动暂停准入、失败替换释放槽位。
- 一个全套文件监听测试在并行负载时超时，隔离文件 142/142 通过；最终全套全部通过，无新增 skip。
- 双平台 CI：当前提交 `910f456f` 的 [run 36833602054](https://github.com/ly-ccx/Peer-Agent/actions/runs/36833602054) 双平台全部通过。
- Review 回归先失败后通过：暂停授权拒绝、当前加急护栏、输入 kind、否定优先级；新增生产接入与旧输入兼容测试。

## 架构影响
A 级，Accepted ADR 80。暂停/取代/恢复真值在 GoalPlan，Renderer 只表达；重用 Scheduler/IsolationPlanner 和现有 Goal 执行/清理链。新增结构化 IPC 已登记并同步生成目录。

## 文档偏差
实施契约在 companion knowledge；不在代码仓创建架构文档。任务卡的取代/恢复落地，不改变签收、合回授权或经典 Goal 行为。

## 未完成与后续
本 PR 交付 B4-03，全部 Review 已修复/解决，代码 #79 已按负责人授权合入 dev（`46c2af0e`）。后续 B4-07/B4-08 与目标卡 B4-04…06 逐卡推进；Beta4 未发布，真实模型与打包/UI 验收留 B4-R。

代码 PR：[Peer-Agent #79](https://github.com/ly-ccx/Peer-Agent/pull/79)。
