# RC post_reply 回合终结补修

2026-10-02，Accepted；负责人自主完成、自测与候选交付授权适用。B 级：恢复已经实现于 ProjectAgentRunner 的成功 post_reply 结束回合语义，在真实 Provider loop 中缺失的装配；不新增权限、工具、IPC、存储或 Context 契约。

## 实测与实施边界

401 旧计划/历史及双机器人隔离副本在启动读取修复后 GPT-6.1 Sol 四次 HTTP200：两次真实 post_reply 调用与两次空文本响应，最终被记不可用，未落 canonical 回复。旧单元仅验证外层 runner 看到 post_reply 后停，未覆盖内层 Provider loop。保留此失败，不能把 HTTP200 当对话成功。

沿现有 ToolResult.outputPreview.control 标记成功 post_reply terminal，理由 project_agent_reply。控制只由已完成的本地 Delegation Provider 生成，经 Runtime Projection/Grant/Evidence 回到 tool-orchestrator 的现有 extractToolControlSignal、各 Provider loop 的既有 terminal tool 收尾。先写回 tool result，再统一 sendDone；不放宽 empty-response guard，不从名字/助手文字/模型参数/伪造结果推断成功。拒绝、失败、取消、未装配 composer 不终结；成功 suppressed 与幂等重放同样终结。

允许代码：packages/runtime-node/src/project-agent/delegation-provider.mjs 与 .test.mjs；apps/desktop/electron/main/project-agent/desktop-integration.test.mjs（真实 OpenAI Responses loop + default LocalToolHost + production host 的回归）。知识：本卡、脱敏失败/恢复证据与自测报告。新分支 PeerAgent/pa/rc-post-reply-terminal，从开发线 68b9689e 起。

退出：先红测试重现控制缺失/Provider 多请求；补修后成功/抑制/重放终结，负面不终结。真实生产 loop 的一次模型工具请求即 canonical 回复，ToolResult 在 done 前、Grant/Evidence 保留且无不可用卡/重复回复/额外模型请求。受影响 runtime-node 与 desktop 完整测试、build/typecheck/architecture、两平台 CI；真实 GPT61 复验。已安装 rc.2 未变，GA 等负责人。

## 源码验证与交接

### Review 范围追加（Accepted）

PR108 Review 发现 TUI 的现有 Adapter 未读取 outputPreview.control，也未把 project_agent_reply 的 stopped 结果作为成功。负责人自主完成授权覆盖必要补齐；允许追加 apps/tui/src/project-agent/tui-turn-executor.ts 与 .test.ts，在既有工具结果控制入口读取该事实、保留 request_user_input 和工具预算失败语义。先用真实 Delegation Provider/Grant/Evidence 写红测试：成功/抑制/重放一次模型请求且 done；失败不终结。补齐后定向与 TUI 完整测试、类型/构建/架构及最终新 HEAD 两平台 CI 重跑。本卡不修改经典 chat-controller、不新增共享契约或 Module。

PR108 源提交 ca56024d95bed1ab00769ca26ff60ad001e1eb19（tree 0d673ef65de7b0fe6a2c365435c0df8d42e21ce6）已推送。三个允许路径完成；先红测试确认控制缺失且真实 production loop 请求 3 次，补修后定向 58/58、runtime-node 1014/1014、desktop 5302 项中 5297 通过/原 5 skip 与独立 i18n 1/1，构建/类型/架构全部通过。没有新增 skip，没有放宽 empty-response guard。CI36977994241 进行中，尚未合入或发布。

相同 401 旧计划/历史双机器人副本、真实 GPT-6.1 Sol 与生产输入路径：[补修前失败](evidence/rc-post-reply-model-failed-20261002.json)保留四次 HTTP200、未落 canonical；[补修后通过](evidence/rc-post-reply-model-passed-20261002.json)仅一次 HTTP200 工具请求，4889ms 落下「连接正常」canonical 回复，无错误/项目改动。此轮在源码使用明确指定的既有签名 helper，不冒充新安装包默认 helper 测试。凭据副本已清除，owned 进程已退出，原用户数据与配置不变。

Review 补修后源 HEAD a8d7058e52a706b778fc466fee52035908fcde6a（tree bb6426c10a4463a733382f0bd890c0b065677e4f），TUI 定向正确夹具先红 10pass/1fail（真实工具 success 但回合 false），后绿11/11；最初测试传入未支持的 idempotencyKey 导致 invalid_input 的夹具失败另存，未当作红证据。TUI 全量755/755、构建、全类型与架构通过。最终 CI36978709629 进行中；旧 HEAD CI36977994241 已通过但不替代最终门禁。

真实 GPT61 [多入口源码复验](evidence/rc-post-reply-source-multi-passed-20261002.json)通过：终端客户端/远程分别由 Desktop 消费，退出 Desktop 后 TUI 接管并完成真实只读文件工具和 canonical marker 回复；输入去重、独占租约、无写工具与页面错误，owned 两进程退出、凭据副本清除。源码 TUI 后端和 loopback 测试身份的范围保留，不写成新包或实体手机通过。
