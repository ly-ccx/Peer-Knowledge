# B5-05 逐机器人远程设置实施边界

日期：2026-10-01。状态：Accepted。B5-03代码`43765d84`/知识`6ccf239`已合入；B5-04代码/知识PR #89/#20在CI，本卡独立基于B5-03，无热点冲突。负责人已授权完成全部Beta5/RC及必要修复、Review/合并/预发布；GA等待用户测试。

## B级边界

renderer只读取已有projectAgentList与remoteAccess状态、通过已有update IPC提交设置；无fs、secret、执行或新IPC。typed preload DTO补RemoteProjectGrant[]、workspaceIds、delegationVersion与安全lastAccess。IPC update拒绝未知顶层字段和畸形参数，权限依赖/身份/版本仍由controller本机验证保存，再重新连接。版本不能由renderer指定。

每个active机器人两列可查看/可发消息；默认关闭；消息依赖查看，取消查看同时取消消息。保留当前设置里的其他有效机器人授权，不因列表过滤丢失。旧单workspace配置只迁移该机器人查看。保存期间禁用变更；晚轮询不能覆盖保存结果，关闭面板不更新已卸载React状态。错误有明确文字。

最近访问来自已登记device事实project-runtime/remote-access.json，字段只含at/operation/workspaceId。连接关闭或app重启且远程关闭时仍可读取摘要，不需要启动连接/访问钥匙串。沿setup现有白名单导出只读summary函数，controller注入读取，不新建持久路径。

## 必要路径

RemoteAccessPanel、拆出的状态纯函数/子面板/CSS/测试；SettingsPage只传i18n；已有boolean-controls Checkbox/Switch与BotAvatar复用，不改。protocol新增remote-access-settings.ts及index导出（设置/patch/访问摘要契约，bootstrapPreloadApi改为协议type alias，不继续在renderer扩展合同）；register-remote-access-ipc和测试；controller/setup及测试补最近访问只读状态；main仅依赖注入readLastAccess，净增≤0。i18n补remoteAccess资源模块与index接缝（两语言相同key，不继续堆巨大字典）。不碰LlmSettingsPanel/ChatSurface/Sidebar；无新依赖/存储/模型能力。B5-04的protocol index导出先待CI/合入，再补本卡导出，避免同文件在制冲突。

## 验证

默认关闭/旧配置查看迁移/依赖组合/取消查看/其他项目保持；拒绝远程传版本或未知字段；授权保存版本+1/重连/幂等；停用和冷启动最近访问白名单；刷新与保存竞态；中英key一致、SVG控件/可读标签。实际Electron设置操作及截图；完整build/type/architecture/IPC/Desktop测试，最终双平台CI。之后B5-R实际预发布和RC门禁。
