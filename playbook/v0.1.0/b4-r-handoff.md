# B4-R 发布交接（进行中）

创建时间：2026-10-01
最后更新：2026-10-01



## 卡片

B4-R 发布 `0.1.0-beta.4`

## 分支与提交

负责人授权完成全部 B4、必要路径、Review 与发布。代码 PR #85，基线 dev 30496b04；最终候选 151b080c。知识分支 PeerAgent/pa/b4-r-release。实施契约先于代码登记，见 b4-r-release.md 与 ADR 80。

- 分支：`PeerAgent/pa/b4-r-release`；代码合入开发线 `ca0736da`。
- 提交：`4470a3a1` 发布准备；`c556fb52` 当前输入授权与冲突合回边界；`1ef4d1c3` 文本任务 UI 分类；`b9026929` 生产恢复转接；`151b080c` 确定性冲突测试。
- 知识 PR：[#16](https://github.com/ly-ccx/Peer-Knowledge/pull/16)。

## 改了什么

宿主事实键沿 canonical 回复持久化；普通事件唤醒无当前输入不得借旧锚点开任务，当前输入锚点严格匹配；文本任务的界面签收说明不误武装视觉门；生产 liveDelegationSupervisor 补齐 resume / reprioritize；重复自动报告返回实际 suppressed 结果并安静收尾，新的用户输入不压制。签收后记录最终事实；宿主处理的合回回答不重复成为任务授权；混合目标 / 任务唤醒的核验依据实际 session 事件。对话事实变化与完整分页重新投影；证据有界 + 展开 SVG；严格目标参数给出具体字段路径；根 build 串行。版本 / Cargo / README / release-notes / changelog 准备 beta.4。

A 级先登记，无新 IPC、工具、依赖、存储路径；main.mjs 未改。模型文字不作为实际签收或合回证据。

## 与卡片的偏差

发布前实际验收补入事实去重、卡片刷新、授权范围、文本 UI 分类及生产恢复适配器；均先登记实施契约，负责人全 B4 授权涵盖必要路径。没有新工具、IPC、依赖或存储路径。

## 验证

实际命令：`pnpm build`、`pnpm test`、`pnpm typecheck`、`pnpm architecture:check`、`pnpm --filter @peer-agent/desktop ipc:check`、`pnpm version:check`、`pnpm check:changelog`、`RELEASE_TAG=v0.1.0-beta.4 pnpm release:readiness-check` / `pnpm release:source-check`。下列计数来自实际完整输出；真实模型和安装证据单独列出。


- 完整 build、test、typecheck、architecture:check、IPC、Protocol 173、version / changelog / readiness 通过。最终完整 Runtime 955、Desktop 5204 通过 / 5 既有跳过、TUI 712。记忆冲突 IPC 的两条写入固定为相同时间戳，以明确验证冲突而非更晚 verified 记录的取代语义。
- 新回归先红后绿；生产 SDK 集成 24 通过，实际 LocalToolHost / Grant / Evidence 覆盖 live 适配器取代→恢复→调优先级，另含重启判重与当前用户追问。
- 真实 `glm-5.3-flash`：三条 code 写任务在独立 worktree 同时执行（实际 1 秒采样最大并行 3），同基线，各自只改 a/b/c.txt，主目录在合回前全为 before；三项实际宿主 UI 合回后全为 after。A/C 按策略签收，B 用户确认；不冒充三项手动签收。
- 实际 C 被一个明确授权的只读任务取代，重启后沿修复的实际 resume_session 恢复。原 planId、conversationId、goal、criteria、tasks、criterionResults、deliveryBinding 与初始快照一致，原输入锚点保留、新恢复锚点记入，原 worktree/证据使用到最终交付。没有重建 C 或重复自动开工（仅三个原任务 + 一个显式临时替代）。
- 真实重复自动报告返回 suppressed 六次；关窗期间连续 0 BrowserWindow，宿主仍写入 canonical 回合和回复，重开正常。Owned 实例退出，临时凭据副本清理。
- 真实 Actions 夹具失败 run 36851994140 → 重复失败 → 成功 run 36852488422 → 重启同一健康，共四条观察；各有实际 Call/Grant/Result/Evidence，仅一个 objective_signal 和一条实际模型失败通知（另有创建确认回复）。failure_only 无任务开工，目标已实际暂停，独立临时远端分支已删除。见 [真实模型脱敏证据](evidence/b4-r-real-model-20261001.json)。夹具故意失败不算产品 CI 回归。
- B4-07 的实际生产 SDK 子进程 SIGKILL 十个断点 + baseline 共 11 通过；使用脚本模型，不冒充真实模型强杀。
- macOS arm64 本地安装包首启、beta3→候选beta4→0.0.18→候选beta4 已跑；旧 canonical 消息逐条保留。见 [安装证据](evidence/b4-r-install-20261001.json)。本地包候选4470a3a1（后续修复前），正式 tag 产物仍须重验。
- b9026929 双平台 CI 36852890685 通过；仅测试时钟修复的最终151b080c CI 36853412270 两平台通过。两个代码 Review 与两项知识 Review 已修复并解决。

## 发布状态

代码 [PR #85](https://github.com/ly-ccx/Peer-Agent/pull/85) 已合入 dev `ca0736da83d0451099494cd7f30e532f174cef92`；`v0.1.0-beta.4` 已推送。[Release 工作流 36854035033](https://github.com/ly-ccx/Peer-Agent/actions/runs/36854035033) 正在构建。真实功能验收及本机完整门禁已完成。尚待实际 prerelease / npm beta 与正式签名包重验、版本计划 / D10 / 路线图回写。没有把五天负责人日用或 Windows/Linux 交互安装写为通过。

## 架构影响

A 级事实连续性先写 ADR 80 / b4-r-release.md；权限真值仍在宿主。普通任务 / 目标事件的核验与开工权限由 Provider 从实际回合事实判断，模型 prose 不提升权限。UI 仅投影既有 canonical 与卡片。B 级文本 UI 分类和 live supervisor 转接均保留原 seam。main.mjs 净增 0。

## 文档偏差

无未登记的运行时边界变化。五天日用与跨平台交互安装保留为未验收，不以测试代替。

## 未完成与后续

实际 Release 产物与 npm 查询、正式 macOS arm64 包启动/升级/降级重验以及版本计划回写；完成后可进入 Beta5 多入口，不代表 0.1.0 GA 验收完成。
