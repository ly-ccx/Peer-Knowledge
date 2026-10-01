# B4-R 发布交接（进行中）

创建 / 更新：2026-10-01。

## 卡片 / 分支

负责人授权完成全部 B4、必要路径、Review 与发布。代码 PR #85，基线 dev 30496b04；候选 4470a3a1。知识分支 PeerAgent/pa/b4-r-release。实施契约先于代码登记，见 b4-r-release.md 与 ADR 80。

## 改了什么 / 架构影响

宿主事实键沿 canonical 回复持久化；重复自动报告返回实际 suppressed 结果并安静收尾，新的用户输入不压制。签收后记录最终事实；宿主处理的合回回答不重复成为任务授权；混合目标 / 任务唤醒的核验依据实际 session 事件。对话事实变化与完整分页重新投影；证据有界 + 展开 SVG；严格目标参数给出具体字段路径；根 build 串行。版本 / Cargo / README / release-notes / changelog 准备 beta.4。

A 级先登记，无新 IPC、工具、依赖、存储路径；main.mjs 未改。模型文字不作为实际签收或合回证据。

## 验证

- build、test、typecheck、architecture:check、IPC、Protocol 173、version / changelog / readiness 均通过。
- 完整 Runtime 950；Desktop 5202 通过 / 5 既有跳过；TUI 712；后加最终签收事实的定向测试 3 通过。最终 PR CI 含该测试，结果待确认。
- 针对修复先红后绿；生产 SDK 集成 23 通过，去重涵盖重启与新用户追问；混合事件 / 交付 42 定向通过。
- 本机 macOS arm64 dir pack 与 packaged runtime 校验通过，本地 ad-hoc 签名仅用于隔离安装验收。正式 Release 必须沿既有 Developer ID / 公证流程。
- 真实模型初次运行发现重复四次任务汇报、合回卡片没刷新、模型把合回一个任务扩大为新任务；已据此补代码回归。初次样本不记为三任务宿主合回通过。修复后候选正重跑真实模型与完整隔离升级 / 降级。

## 未完成

最终双平台 CI / Review、真实模型重验、安装数据保留证据、prerelease / npm beta 与版本计划 / D10 回写。跨平台交互安装及五天负责人日用没有冒充通过。
