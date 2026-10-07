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

背景快照对附件的遗漏确认只有在遗漏的全部正文均由锚定附件完整携带时才可沿既有行内截图规则满足：已校验的图片 dataUrl 或文本 text。已准入的未解析文件、工具结果和指定背景快照继续要求原有背景确认；文件上传不代表用户允许丢弃其他背景。附件聚合校验必须发生在创建子对话前。

## 2026-10-06：委托背景按任务锚点准入（A 级修订）

事故：用户已经选择替换只读任务，宿主却因为此前另一条 UI 消息的截图再次要求背景确认。代理生成的普通问题回答不携带可信的 `historyConfirmed`，因此重复点击“确认启动”也无法解除。新任务不是整个主对话的分叉；无关历史不应成为新任务的启动前提。

未指定背景快照时，SessionSupervisor 通过 ConversationStore 的 `backgroundMessageIds` 接口，只准入 `anchorMessageIds` 指定的持久消息。列表必须存在、含委托主锚点、属于同一父对话；仅 `work_session` 且具有合法 delegation 的调用可使用。快照保存 `scope: { kind: 'delegation', messageIds }`，继续绑定原对话 revision、不可变内容 hash 和运行状态。任务说明和锚点内容保持事实上下文，不提升为系统指令。需要更早的材料时，代理必须显式添加其锚点。

未准入的历史消息不是“丢失的委托材料”，不进入 missingItems。锚定附件、锚定工具内容、已指定背景快照的遗漏检查仍然有效。经典继续、选择分叉、整段历史快照不改变；它们仍要求确认全部未解析的背景材料。不得从普通回答的文字推断 `confirmMissing`，不得把所有 spawn 的确认位设为 true。

替换仍为原子流程：新任务构建成功后才暂停旧任务；失败保留旧任务。重放同一输入不重复创建，权限、Evidence、人工验收标准均不绕过。回归必须包含“历史截图 → 用户选择替换 → 一次创建 → 旧任务暂停 → 重放不重复”，以及锚定不完整附件和显式部分背景仍被拒绝。

## 界面

选择文件、图片粘贴、文件拖放共享接收逻辑。普通文字粘贴保留浏览器默认行为。异步读取期间禁止发送，连续接收串行处理，避免数量竞态或发送后附件落入下一条消息。文件可移除，图片可预览；未支持的格式明确显示“仅文件信息”。发送后的附件属于用户消息，错误重试仍可见。

抽屉五个入口采用自适应等宽的滑动分段选择器，保持原有 tab / tabpanel 可访问性关联、方向键 / Home / End 以及减少动态效果偏好。

## 验收

验证附件单独发送、图片和文本 canonical user content、队列重启、同 inputId 重试、非法/超限拒绝、锚定委托、渲染回显；实机检查文本粘贴、图片粘贴、文件选择、移除、拖放及分段控件点击/拖动/键盘。
