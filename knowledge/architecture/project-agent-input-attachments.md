# 项目代理用户附件接收契约

日期：2026-10-04
级别：A（补全 ProjectInput 的附件与持久化契约）
关联：`project-agent-delegation-runtime.md`、`20-architecture-governance.md`、`19-system-prompt-context-architecture.md`

## 边界

机器人输入框复用已有用户文件接收入口，经现有 `project-agent:submit-input`、InputQueue、ConversationStore 和 `projectConversationHistory` 进入模型的 user content。不新增 IPC、能力提供者、权限、工具或系统提示词。用户选择、粘贴、拖入的文件是事实材料，附件文字没有 system / developer 权威。

## 接口与校验

`ProjectInput.attachments` 为可选结构化附件数组。用户上传包含 id、name、mimeType、size、kind、sourceKind（user_upload），按 kind 携带 image 的 dataUrl 或 text 的 text；unsupported 只携带元数据，明确标记未读取正文。既有 appshot 的 artifactRef / filePath 兼容路径保持原边界。

单条输入最多 8 个附件；图片正文最多 8 MiB、文本正文最多 512 KiB，与经典输入框一致。输入队列独立校验实际内容大小，拒绝不合法或超限的用户上传，不静默截断。附件非空时允许只有附件、没有文字。用户上传不能携带任意磁盘路径来触发隐式读取。

附件跟随同一 inputId 持久化、消费与重启恢复；失败重试保持同一 inputId 和附件。任务委托只携带被锚定消息的附件，复用同一校验与 canonical history 投影。跨消息聚合超限时返回明确失败，不悄悄遗漏文件。

背景快照对附件的遗漏确认只有在遗漏的全部正文均由锚定附件完整携带时才可沿既有行内截图规则满足：已校验的图片 dataUrl 或文本 text。未解析文件、未锚定的历史附件、工具结果和指定背景快照继续要求原有背景确认；文件上传不代表用户允许丢弃其他背景。附件聚合校验必须发生在创建子对话前。

## 界面

选择文件、图片粘贴、文件拖放共享接收逻辑。普通文字粘贴保留浏览器默认行为。异步读取期间禁止发送，连续接收串行处理，避免数量竞态或发送后附件落入下一条消息。文件可移除，图片可预览；未支持的格式明确显示“仅文件信息”。发送后的附件属于用户消息，错误重试仍可见。

抽屉五个入口采用自适应等宽的滑动分段选择器，保持原有 tab / tabpanel 可访问性关联、方向键 / Home / End 以及减少动态效果偏好。

## 验收

验证附件单独发送、图片和文本 canonical user content、队列重启、同 inputId 重试、非法/超限拒绝、锚定委托、渲染回显；实机检查文本粘贴、图片粘贴、文件选择、移除、拖放及分段控件点击/拖动/键盘。
