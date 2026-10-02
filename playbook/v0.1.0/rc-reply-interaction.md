# RC 回复引用与操作交互

2026-10-02，C级界面表达修复。负责人指出RC4回复没有引用效果、底部选项无样式，并要求参考Grok Bot和Dot。基线开发线6ce13434；代码分支PeerAgent/pa/rc-reply-interaction。沿已有跳转、引用、过程、来源、记忆、证据入口表达，不移动运行时、权限、Evidence、协议或存储边界。

## 审查与设计

- 原安装窗口已确认“回复”与来源摘录直接混成正文，“过程”只有文字；通知方式interrupt显示“马上告诉你”，易被误认成操作。引用、页脚等仍使用未定义的frost/separator/text变量，边框和前景未生效。
- 已实测Grok Bot本机消息菜单Reply/Copy与输入框回复上下文条，保留原始本机截图；取消回复恢复空输入，没有发送消息。引用条独立于正文/输入，动作有SVG和清晰点击区。
- Dot本机窗口被界面工具禁止读取，因此只参考OpenAI官方dots及messaging文档中正文、任务详情和通知位置的分工，不宣称实测Dot界面。参考https://docs.x.ai/grok-bot/chat-and-collaboration、https://learn.chatgpt.com/docs/dots、https://learn.chatgpt.com/docs/dots/channels。
- 回复引用采用主题内的淡底、细边框和左侧线，已有SVG、两行以内摘录、跳转提示；点击仍定位原消息。正文保持正常Markdown和受限阅读宽度。
- 页脚的过程/证据/来源/记忆是明确可点击控件，通知方式和结论是静态说明；不将通知策略伪装成已通知事实或虚构可选项。选中文本引用与输入框取消引用采用一致上下文样式。
- 使用现有主题tokens及PeerIcon，不新增字符图标或外光晕；深浅色、长引用、窄窗口、键盘焦点、原消息跳转、过程打开、引用取消需要实机核验。

## 允许改动

- apps/desktop/renderer/src/project-agent/conversation/ReplyBubble.tsx
- apps/desktop/renderer/src/project-agent/conversation/QuoteChip.tsx
- apps/desktop/renderer/src/project-agent/styles/bot-conversation.css
- packages/i18n/src/index.ts：已有过程/通知方式文案，以及必要的通知方式静态标签。
- apps/desktop/scripts/bot-shell-electron-smoke.mjs、bot-shell-reply-checks.mjs：在已有隔离窗口验收中复用真实回复夹具与已有跳转/引用/过程入口，检查颜色/边框/焦点/长文本布局和回调效果。不替代或弱化现有检查。
- apps/desktop/scripts/bot-shell-updater-checks.mjs：同一真实窗口验收再次遭遇旧主进程CDP evaluate发送合成更新事件时Promise被GC；以隔离入口中的显式测试命令/回执文件传递同一事件，沿生产updater:event通道返回Renderer，保持原72项布局和全部动作断言。仅测试宿主改动，不新增产品IPC或持久化路径。依负责人持续自主修复/自测授权补齐此必要路径，不重复请求已获授权。
- 本卡、自测报告及本卡脱敏证据；第三方私有消息原截图留本机，不提交知识仓。

## 门禁与交付

构建、桌面及i18n受影响包完整测试、全仓typecheck、architecture:check，现有源窗口检查含accessibility/diagnostics，以及新增回复检查。UI仅作用于机器人壳，经典界面不变。最终源码两平台CI通过后按负责人持续授权评审合入。原安装RC4和下一签名候选是独立事实，不修改已发布tag或签名app。整体Ready和复杂任务独立阻塞不因本卡改变。

## 实施与本机验收

代码PR114最终提交8dbbd283（干净，已推送），7个允许路径。短引用按内容收紧至最多420px，长引用两行；选中文本引用并入同一页脚，通知方式保持只读说明；深色真实hover使用paper-hover，修复原chrome-hover与paper-sheet同色造成无反馈。记忆列表容器使用div保留合法结构，沿原IPC取canonical记忆。

本机生产窗口9壳/11可访问性/7诊断/5回复交互、原72更新布局及36合成事件明确回执全部通过；引用跨页定位、键盘过程入口、真实记忆读取、760px布局、取消引用保留草稿已验证。列表/可见搜索/Received中位32.055/49.0/118.5ms，在原100/150/300ms预算；无页面或主进程授权错误、自有进程退出。CUA检查实际短引用深浅色布局，并验证引用Tab→过程→Enter。

[本机门禁与范围](evidence/rc-reply-local-gates-20261002.json)、[真实源窗口](evidence/rc-reply-source-window-passed-20261002.json)、[初次失败与修正](evidence/rc-reply-initial-failures-20261002.json)。完整桌面初轮5315pass/原5skip；后轮并行负载下既有Goal store监听计时失败一次，独立同文件一次重跑142/142pass保留。焦点驱动与旧GC测试通信修复没有放宽断言、预算或增加skip。最终两平台CI37023512022进行中；实际签名RC4仍为旧界面，不宣称新安装候选或总体Ready。

截图：[深色长引用](evidence/rc-reply-dark-20261002.png)、[浅色长引用](evidence/rc-reply-light-20261002.png)、[760px引用及草稿](evidence/rc-reply-narrow-20261002.png)、[深色短引用](evidence/rc-reply-short-dark-20261002.png)、[浅色短引用](evidence/rc-reply-short-light-20261002.png)。只有合成Peer预览提交；用户原窗口和第三方消息截图留本机。

## 最终 CI 与合入

最终CI37023512022 attempt1两平台完整构建、类型、架构、测试及生产窗口全部成功。Mac/Linux均9壳、11可访问性、7诊断、5回复交互、72原更新布局、36合成事件回执通过；无页面或主进程授权错误，自有进程退出。Mac列表/搜索/Received中位46.917/59.0/167.7ms；Linux27.053/41.0/71.1ms，原预算不变。[Mac窗口证明](evidence/rc-reply-ci-mac-passed-20261002.json)、[Linux窗口证明](evidence/rc-reply-ci-linux-passed-20261002.json)。

PR114按负责人持续授权于15:07:57Z合入9df7d292。源8dbbd283、CI实际checkout533885ed及合入的Git tree均b70d2ab56d5f95bed632cf8ae81f6d308df6a705，已逐一验证。[绑定证明](evidence/rc-reply-ci-binding-20261002.json)。主工作区已同步；本卡局部修复完成，实际签名RC4、后续安装候选和整体Ready仍按独立门禁判断。
