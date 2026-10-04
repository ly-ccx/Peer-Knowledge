# RC 对话过程与选择交互修复

2026-10-04，Accepted。负责人指出过程面板直接显示 post_reply/JSON，选择卡没有跟随提问消息，手输回答后仍留在界面，并要求沿用原聊天风格。沿既有自主修复/合入授权推进；无版本发布。

## 边界

基线 dev `5aafde23`，分支 `PeerAgent/pa/rc-chat-details`，一张代码 PR。B 级：现有 bot-directory 只读对话/卡片投影；C 级：消息关联、现有 submit-input.answerTo 的输入绑定、过程摘要与样式。无新 IPC、协议或存储字段，无能力/权限/Evidence/上下文边界移动，无 ADR 调整。

允许路径：runtime-node/src/project-agent/{bot-directory,card-projection,project-facts}.mjs 及既有对应测试（project-facts 测试在 desktop/electron/main/project-agent/）；renderer/src/project-agent/drawer/{agentProcess.ts,AgentProcessView.tsx,agentProcess.test.ts}；conversation/{CardView,ReplyBubble,ReplyAnchors,UserBubble,LiveReply}.tsx；state/{botConversationState.ts,useBotConversation.ts,botQuestionState.ts} 及关联测试；styles/{bot-conversation,bot-drawer}.css；packages/i18n/src/index.ts；现有原生 bot-shell/reply/streaming 验收脚本、新 bot-shell-chat-detail-checks.mjs；本卡及脱敏验收证据。旧聊天样式只读参考。

## 行为与退出条件

- 正式回复及停止卡优先按已有 turnId 找对应 agent_turn，允许该事实位于回复之后；明确身份缺失时不借其它回合冒充本轮。
- 过程默认显示中文/英文操作名称、明确结果状态及有界摘要。post_reply 显示发送结果，不重复正文与 JSON；原始字段按需展开，未知结果不伪造成功。
- 回复 question 卡按已有 refs.replyMessageId 嵌入该回复；历史分页不把它移到最后或再重复附加。手输回答通过现有 answerTo 入队；仅绑定最新开放的对话问题，不隐式批准任务、权限、目标或交付；失败可重发并保留原绑定，收到后收起选择项，宿主仍由 canonical input 决定解决状态。
- 兼容 RC5 已存在的手输回答：回复问题紧接的 canonical 用户输入可关闭该对话问题；明确回答其它问题或引用其它消息不自动关闭。共享纯投影用于卡片和需要你计数，不改写历史，也不解决工作任务/权限批准卡。
- 使用原聊天设计 token、正文节奏与紧凑操作栏；引用无左侧强调线，消息无光晕，图标为 SVG。回执仍在正文下方，静默/证据事实不变。
- 定向回归先证明错轮和选择不收起，再跑受影响包完整测试、build/typecheck/architecture，真实隔离 Electron 测试手输/按钮/失败重试、分页、过程状态/折叠、明暗与窄窗口，最后两平台 CI。

真实用户数据与安装版 RC5 不变。只读过程不是工具执行入口，技术详情不替代 Evidence；本卡不宣称整体 GA Ready。

## 实施记录

代码 PR [#119](https://github.com/ly-ccx/Peer-Agent/pull/119)，代码 de7220eb。先行回归、受影响包完整测试、构建/类型/architecture、真实源码窗口通过，详见 `rc-chat-details-validation.md` 与对应机器报告。两平台 CI 执行中；合入后补合并提交。不发布版本。
