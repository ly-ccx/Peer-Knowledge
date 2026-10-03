# RC 对话流式与完整交互修复

2026-10-04，Accepted。负责人当前要求详细参照 ChatGPT 流式体验；按已有自主推进和合入授权执行。本卡不发布版本。

## 目标、级别、依赖

A 级：ADR85 本日 Accepted 补充；B 级 runner/宿主/IPC 装配；C 级表达与样式。依赖已合入 RC5 / dev 64d20d34。分支 `PeerAgent/pa/rc-chat-streaming`，一张代码 PR。必读产品 north star、release-plan §3、执行手册 §2–5、v0.1.0 README、ADR80/85、本卡。

## 允许改动与代码锚点

- protocol/src/project.ts、index.ts：Activity 与 StopResponse 类型及测试。
- runtime-node/src/project-agent/{runner,runtime-host,agent-turn-plan,project-facts,card-projection}.mjs 与测试；新 turn-activity.mjs 与测试。保留租约/输入/真实工具及停止系统卡；无新持久存储路径。
- runtime-node/src/provider-adapters/tool-arg-progress.mjs、新 reply-text-preview.mjs 与测试；runtime-node/src/index.mjs：共享进度实现导出。
- desktop/electron/main/provider-adapters/tool-arg-progress.mjs 与测试：改用共享 Module，覆盖 Responses/Chat/Anthropic/Gemini 原事件 seam。
- desktop/electron/main/project-agent/{project-agent-host,project-agent-application-service}.mjs 与测试；ipc/register-project-agent-ipc.mjs 与测试；electron/ipc/channels.mjs 及生成 catalog；preload/preload.source.cjs 及既有生成物。
- renderer/src/{clientApi.ts,preload/contracts/bootstrapPreloadApi.ts}：类型化接口。
- renderer/src/project-agent/conversation/、state/{useBotConversation,botConversationState,conversationPager,botConversationContract,conversationWindow} 与相关测试；新 botActivityState.ts 与测试；styles/bot-conversation.css：草稿/过程/停止/回执/滚动；已有 ui/icons 仅使用已有 SVG。
- packages/i18n/src/ 的中英键及既有生成物。
- scripts/rc-response-interaction-smoke.mjs（新）：隔离受控流式提供方、真实 Electron 场景；现有原生壳 harness 如需接入；知识本卡、自测/评测文档与脱敏 evidence。

不碰 main.mjs、旧大 React surface、版本/发布文件、依赖、真实用户数据、模型提示、能力/权限/Evidence 规则。新增只限一个活动推送与一个主窗口停止命令；现有 read-conversation/retry 保留语义并扩展停止回合。

## 实现与必须新增测试

按 ADR85 同日补充。先复现首片/回执位置失败，再实现实际 delta 与工具参数前缀投影；接入 snapshot/revision 重连、完成原子交接、停止与显式重试。测试覆盖完成/失败/停止/切换/乱序/宿主失效，逐片不读文件，工具真实状态与私有内容排除。保持 Markdown/引用/IME、输入草稿、回看和跳到最新。

## 退出条件

定向及受影响完整包测试、build/typecheck/architecture/ipc、真实原生窗口流式状态及所有上述交互；两平台 CI 通过后按授权合入。详细报告区分受控流式和真实模型，不能把最终文本截图当首片证明。当前 RC5 不变，GA 仍等待原整体 Ready 与负责人完整评测。
