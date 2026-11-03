# 运行事实与资源等待收敛实施卡

创建时间：2026-11-03
最后更新：2026-11-03
状态：RC-01—RC-04 源码与文档交付完成，未运行验证、未合并；本卡不等于运行验收。

依据：[ADR120](../../knowledge/decisions/120-runtime-facts-disposition-and-resource-wait.md)、[审计](../../knowledge/experience/peer-task-chain-reliability-audit.md)。基线为 Peer-Agent 开发线 `4a58e284`，知识 `f952a447`；独立代码分支 `codex/runtime-decision-convergence`，知识沿本轮独立工作树。禁止改版本/发版物、真实运行数据、无关工作树或安装实例。

## RC-01：事实与处置内核

级别 A/B。修改范围：`packages/protocol/src/` 的运行事实、原 Intent/Work 类型及出口；`packages/runtime-node/src/project-agent/` 的新增严格类型纯处置 Module、`repair-ownership`、`intent-lifecycle` 与对应契约用例。

接口：执行三态和规范化事实；model/host/user/none；统一工作处置与未决义务；不增加活体布尔镜像，不持久化第二份事实。用例覆盖真实生产事实、无效形状、用户控制与 silentWait、根关闭。退出条件是旧 `.active` 消费和 host 责任即模型修复的路径被替代，现有语义与安全门保留；本轮不运行用例。

## RC-02：资源等待完整端口

依赖 RC-01。范围：原 `execution-scheduler`、`session-supervisor`、新增资源等待 Module、`coordination-lifecycle`、`intent-lifecycle`、`decision-frame`、`runtime-host`、`runner` 与各自声明/测试；Desktop `project-agent-host`、TUI `tui-project-host` 装配。必要类型沿 Protocol 原模块；不新增 IPC、数据库或 System Context Source。

实现 read/inspect 的作用域、目标执行身份、blocker revision、waiting/ready/stale/unavailable；原 query 返回引用；原 assessment 校验；同一端口交到 Runner 冷恢复/资源变化重查。生产端口必接，轻量无资源适配明确。删除未整合分支。补真实资源/停止回执/根等待的组合及伪范围/源故障用例；本轮不运行。

## RC-03：统一消费与引用归属

依赖 RC-01/02。范围：`runner-coordination`、`runner-reply-lifecycle`、`repair-custody`、`repair-ownership`、`reported-wait`、原恢复准入及所需测试。

finish、回复恢复与 repair 接回消费同一处置结论；引用只观察；停止/暂停优先，具体等待不会触发无进展或模型轮询。保留来源、checkpoint、预算、未知、签收与事件回执。与 PR268 交叉文件在 PR 描述明确；不把其代码/CI 当成本分支已通过。退出条件是重复 policy 实质减少，正常自治仍有路径，不增加平行执行器。

## RC-04：交付与验收入口

依赖前三包。同步知识实施收据与审计状态，补齐 ADR120 RF01—RF13 用例和两个正式宿主装配。只做源码/内容/diff 审阅；当前用户未授权早测时，不运行测试、build/type/架构/IPC/产品回归，也不等待 CI。若生效规则变化，按其明确范围记录实际执行。

代码提交同步推送，draft PR 指向原开发线，关联知识 PR。不得自行合并、发布、安装或重启。最终发布候选才执行全部工程与产品门禁，真实模型和安装版完整任务另有证据；测试未运行、未验收项明确写出。

## 2026-11-03 实施收据

设计先行提交并推送 `1cd4c5f`；代码交付 [Peer-Agent `9c20faea`](https://github.com/ly-ccx/Peer-Agent/commit/9c20faea20609ef6542cccec4b89682e2bf4e6ce)，基于 `4a58e284` 的独立工作树，已推送 `codex/runtime-decision-convergence`。四包的源码、两宿主装配、21 条新增契约用例和知识回写已完成；逐项落点见 ADR120 §14。仅源码/内容/diff 自审与 `git diff --check`，没有运行测试或工程/产品检查；非独立评审。

原工作区、其它知识脏文件、安装实例和真实任务数据保持原状。提交 draft PR 供整合；PR268 交叉路径及发布总门禁仍需最终候选验证。ADR119 的完整控制扩展、本卡 RF13 的真实模型/安装版/升级数据闭环尚未交付验收，不标成已通过。
