# RC 消息卡片光晕修复

2026-10-02，C级局部表达修复。负责人实际RC4截图指出重复系统消息卡片有亮光晕，按本轮修复要求及持续自主修复/自测授权实施。基线开发线11b5f645；代码分支PeerAgent/pa/rc-message-surface。无架构边界移动。

## 原因与设计

bot-conversation.css的bot-card、bot-composer及focus-within使用graphite-base混色阴影。graphite-base是文字颜色，深色模式会翻成浅灰，导致消息卡片与输入框外侧出现光晕。真实Renderer核对另发现这两处使用的frost-separator/separator、frost-bg-elevated/bg-elevated均未定义，导致背景和边框没有生效，聚焦color-mix也失效。限定这两处，使用已定义paper-sheet/control-composer/chrome-hairline主题tokens；聚焦仍沿原graphite-base混色边框方式。对话内固定内容采用平面背景和细边框。保留真实消息、错误文本、日期、按钮及可访问性语义。

## 允许改动

- apps/desktop/renderer/src/project-agent/styles/bot-conversation.css：去除消息卡片、输入框默认/聚焦外阴影与无效阴影过渡；仅这两处失效背景/边框fallback换为已定义主题tokens。
- 本卡、自测报告、对应脱敏证据与隔离预览截图。

不新增实现镜像测试。实际生产Renderer隔离数据夹具覆盖重复错误、待处理操作卡、回复、输入框聚焦和失焦；以深浅色computed style及截图复验无shadow/filter、现有边框/可点击操作/键盘焦点保持。运行桌面构建及受影响包完整测试、typecheck、architecture:check和已有源窗口检查；最终两平台CI通过后评审合入。签名安装应用更新经独立RC候选卡，不能修改已发布RC4或直接补丁原签名app；源码/预览结果不冒充原用户已更新。

## 退出条件

- 源码样式修复和真实隔离窗口检查通过，深浅色无消息/输入框光晕。
- 桌面完整门禁及两平台CI通过，无新增skip/失败；评审后交付代码PR。
- 实际签名用户应用和下一候选版本的事实独立记录；总体Ready及复杂任务独立阻塞保持。

## 本机实施与视觉核验

最终源码26904009（干净）只修改上述CSS。5320项桌面测试5315pass/原5skip/0fail、独立AST1、构建/typecheck/architecture通过。实际生产main/preload/renderer在独立合成数据中重现六条错误/操作卡及产品欢迎行：基线11b5f645深浅色均为透明背景、0px边框，默认/聚焦有阴影；修复后背景为既有主题内容/控件色、1px分隔边框，六条消息和输入框shadow/filter为none，聚焦边框发生变化，真实重发按钮可键盘聚焦；无页面错误，自有进程退出。[视觉证据](evidence/rc-message-visual-passed-20261002.json)、[深色预览](evidence/rc-message-after-dark-20261002.png)、[浅色预览](evidence/rc-message-after-light-20261002.png)。

临时观察脚本先选到隔离工具新增机器人，随后误将产品欢迎行计入六条历史断言；修正为真实合成消息ID定位。基线聚焦检查又揭示背景/边框token未定义；最终新样式的严格断言保留，没有修改产品数据或弱化要求。[早期观察记录](evidence/rc-message-visual-fixture-failures-20261002.json)。

[干净源码门禁](evidence/rc-message-source-gates-20261002.json)与实际窗口9壳/11可访问性/7诊断通过，72既有更新布局通过、无页面/授权错误、自有进程退出，列表/搜索/Received在原预算。

代码[PR113](https://github.com/ly-ccx/Peer-Agent/pull/113)与最终CI37017510987进行中；原签名RC4未改变，此预览不冒充原应用安装结果。
