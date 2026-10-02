# RC post_reply 回合终结补修

2026-10-02，Accepted；负责人自主完成、自测与候选交付授权适用。B 级：恢复已经实现于 ProjectAgentRunner 的成功 post_reply 结束回合语义，在真实 Provider loop 中缺失的装配；不新增权限、工具、IPC、存储或 Context 契约。

## 实测与实施边界

401 旧计划/历史及双机器人隔离副本在启动读取修复后 GPT-6.1 Sol 四次 HTTP200：两次真实 post_reply 调用与两次空文本响应，最终被记不可用，未落 canonical 回复。旧单元仅验证外层 runner 看到 post_reply 后停，未覆盖内层 Provider loop。保留此失败，不能把 HTTP200 当对话成功。

沿现有 ToolResult.outputPreview.control 标记成功 post_reply terminal，理由 project_agent_reply。控制只由已完成的本地 Delegation Provider 生成，经 Runtime Projection/Grant/Evidence 回到 tool-orchestrator 的现有 extractToolControlSignal、各 Provider loop 的既有 terminal tool 收尾。先写回 tool result，再统一 sendDone；不放宽 empty-response guard，不从名字/助手文字/模型参数/伪造结果推断成功。拒绝、失败、取消、未装配 composer 不终结；成功 suppressed 与幂等重放同样终结。

允许代码：packages/runtime-node/src/project-agent/delegation-provider.mjs 与 .test.mjs；apps/desktop/electron/main/project-agent/desktop-integration.test.mjs（真实 OpenAI Responses loop + default LocalToolHost + production host 的回归）。知识：本卡、脱敏失败/恢复证据与自测报告。新分支 PeerAgent/pa/rc-post-reply-terminal，从开发线 68b9689e 起。

退出：先红测试重现控制缺失/Provider 多请求；补修后成功/抑制/重放终结，负面不终结。真实生产 loop 的一次模型工具请求即 canonical 回复，ToolResult 在 done 前、Grant/Evidence 保留且无不可用卡/重复回复/额外模型请求。受影响 runtime-node 与 desktop 完整测试、build/typecheck/architecture、两平台 CI；真实 GPT61 复验。已安装 rc.2 未变，GA 等负责人。
