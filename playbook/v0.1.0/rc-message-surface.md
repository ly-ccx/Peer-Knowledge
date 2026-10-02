# RC 消息卡片光晕修复

2026-10-02，C级局部表达修复。负责人实际RC4截图指出重复系统消息卡片有亮光晕，按本轮修复要求及持续自主修复/自测授权实施。基线开发线11b5f645；代码分支PeerAgent/pa/rc-message-surface。无架构边界移动。

## 原因与设计

bot-conversation.css的bot-card、bot-composer及focus-within使用graphite-base混色阴影。graphite-base是文字颜色，深色模式会翻成浅灰，导致消息卡片与输入框外侧出现光晕。对话内固定内容采用平面背景和现有细边框；输入框聚焦用原有边框提示。保留真实消息、错误文本、日期、按钮及可访问性语义。

## 允许改动

- apps/desktop/renderer/src/project-agent/styles/bot-conversation.css：去除消息卡片、输入框默认/聚焦外阴影与无效阴影过渡。
- 本卡、自测报告、对应脱敏证据与隔离预览截图。

不新增实现镜像测试。实际生产Renderer隔离数据夹具覆盖重复错误、待处理操作卡、回复、输入框聚焦和失焦；以深浅色computed style及截图复验无shadow/filter、现有边框/可点击操作/键盘焦点保持。运行桌面构建及受影响包完整测试、typecheck、architecture:check和已有源窗口检查；最终两平台CI通过后评审合入。签名安装应用更新经独立RC候选卡，不能修改已发布RC4或直接补丁原签名app；源码/预览结果不冒充原用户已更新。

## 退出条件

- 源码样式修复和真实隔离窗口检查通过，深浅色无消息/输入框光晕。
- 桌面完整门禁及两平台CI通过，无新增skip/失败；评审后交付代码PR。
- 实际签名用户应用和下一候选版本的事实独立记录；总体Ready及复杂任务独立阻塞保持。
