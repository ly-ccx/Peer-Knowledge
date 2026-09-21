# 77. 多服务图片生成能力与凭证、产物边界

创建时间：2026-09-15
最后更新：2026-09-15

状态：Proposed（待架构评审；不是已接受或已实现能力）
级别：A（新增能力、配置用途、消费授权与图片结果协议）

关联：[产品实施规格](../../design/product/image-generation-implementation.md)、[架构治理](../architecture/20-architecture-governance.md)、[ADR 63 用户产物与 Evidence](63-user-artifact-evidence-boundary.md)、[ADR 15 插件/Skill/MCP](15-plugin-skill-mcp-system.md)、[ADR 16 Skill 生命周期](16-skill-call-lifecycle.md)。

## 背景与已知事实

用户需要在没有 GPT 订阅时也能配置 Google、OpenAI API Key、Seedream 等服务，且与当前聊天模型解耦。已有一次 Peer 订阅凭证调用 Codex 图片端点成功的现场证据，详见产品规格 §1；它不是跨账号保证或正式公开 API 稳定性承诺。

前期讨论曾把 Codex 生图推断为对话 Responses 中的 hosted tool，仅凭二进制字符串不足以支撑该结论。后来核对的公开源码存在客户端 `image_gen.imagegen` 工具处理器及独立 ImagesClient 请求；因此本决策采用“本地能力工具调用远程服务”，不以前期错误推断为依据。公开 main 分支会变化，正式实现须固定所参考版本并重新确认端点/字段，不把源码名称当成服务授权。

参考（外部源码，非本仓已实现）：[工具处理](https://github.com/openai/codex/blob/main/codex-rs/ext/image-generation/src/tool.rs)、[生图后端](https://github.com/openai/codex/blob/main/codex-rs/ext/image-generation/src/backend.rs)、[图片端点](https://github.com/openai/codex/blob/main/codex-rs/codex-api/src/endpoint/images.rs)。

## 决策 1：统一能力，不统一厂商协议

图片生成是一个 Capability Provider，按既有链注册：

```text
Capability Provider → Manifest → Runtime Projection
  → Tool Call → PermissionGrant → adapter → remote image service
  → validated local image → Tool Result { evidenceRefs, userArtifacts }
  → EvidenceIndex → 对话/任务/工作台投影
```

所有入口（自然语言、输入框、测试图、再次生成）调用同一治理流程。Renderer 不持有秘密、不直接执行厂商 HTTP，也不在快捷按钮中绕开 PermissionGrant。Skill 可说明提示词与流程，但不能配置账号、运行私有脚本绕开能力链。

adapter 负责厂商参数、认证协议、传输、轮询/取消能力与错误规范化；Capability Provider 负责通用校验、授权上下文、生命周期、产物与证据。通过组合注册适配器，不在中心 host 以厂商名称分叉执行；不创建第二套 provider/capability 注册体系。

当前不扩展聊天 Responses encoder 为 hosted tools 平台。未来真正服务端托管工具若有独立需求，另立契约，不能据此绕过消费、数据传输与 Evidence 治理。

## 决策 2：连接、模型用途与调用快照分离

拟议逻辑结构（字段名待协议评审，不表示现有类型已具备）：

- ServiceConnection：既有连接 ID、service/endpoint 类型、auth method、credential reference；秘密由 helper 管理。
- ImageBinding：bindingId、connectionId、image modelId、operation=`generate`、启用状态、默认参数；仅生图连接合法。
- ImageSelection：全局默认 binding 或本次显式选择；聊天模型的 default/vision/toolUse 不表示生图能力。
- Verification：按连接/认证修订/端点/模型/操作记录验证状态、时间、脱敏错误；任何相关变更使旧状态过期。
- ImageInvocationSnapshot：requestId、binding 与配置修订、实际目标/模型、规范化参数、授权范围及来源；建立后不可受 UI 切换影响，秘密不持久复制。

现有 store 保持连接单一事实源；扩展用途/图片 binding，不新建平行凭证库。配置迁移须版本化、可读取旧数据，未知字段不无故丢弃。新增用途字段不得使纯图片模型进入聊天下拉、改变聊天默认或破坏已有 provider 分组。

删除连接使引用失效而非自动重路由；进行中调用保留已授权目标快照，未取得凭证或权限的请求不得继续发起。实现阶段应明确禁用对新请求的即时作用，已提交远端请求只能按真实取消能力处理。

## 决策 3：操作能力与认证矩阵显式表达

首版支持四种目标适配：ChatGPT 订阅、OpenAI API Key、Google Gemini API Key、Seedream 对应服务 Key。真实可用入口按交付证据开放，Google Vertex AI 独立云认证后置。Seedance 视频、编辑、参考图和批量不属于本决策首版。

能力描述至少区分 supported operations、尺寸/比例约束、输出 MIME、remote cancellation、task status query 与 idempotency support。未支持参数明确拒绝，不当作成功忽略。服务目录支持是静态知识，实际模型权限需账号实测；不得把“有 Key”推成“有所有模型权限”。

最小统一输入含 prompt、可选 binding、受支持参数；输出含实际服务/模型、生命周期状态、图片产物和 evidenceRefs。不将厂商完整 JSON 或 base64 塞入模型上下文。新增统一参数必须能给出逐适配器映射或明确 unsupported，不引入任意 JSON 透传绕过校验。

## 决策 4：认证与消费授权留在宿主边界

复用 credential helper 与既有认证刷新逻辑，通过宿主依赖注入供共享 runtime 使用。图片运行时不能导入 Renderer，共享库也不硬依赖 Electron。刷新是凭证操作，不应被生图重试逻辑错误重放；认证成功不意味着自动授权消费。

订阅 token 只发送到批准的对应订阅 origin；OpenAI/Google/Seedream Key 只发送到对应连接的批准目标。禁止跨域重定向携带认证。自定义 base URL 必须明确服务契约和授权范围，不能根据“OpenAI 兼容”标签发送别的连接凭证。错误日志、Tool Result、提示词和 UI 仅包含脱敏标识，不含 token、Key、完整认证头。

授权至少绑定服务连接、模型/操作、发送数据及单次/用户选择的允许范围；测试图、重新生成、跨服务切换遵循相同策略。不得后台选择另一收费来源。参考图上传当前不支持，未来要重新定义敏感文件出网授权。

## 决策 5：不确定结果不得自动重生成

生命周期分别表示远端生成和本地交付。建议状态：awaiting_permission、submitting、processing、persisting、completed、failed、unknown、stopped_waiting、save_failed。准确命名以最终协议为准，但不得丢失 unknown/save_failed 区别。

本地 requestId 做同一操作的调度去重及结果关联，不等于远端幂等。没有可证明的远端幂等支持时，超时/连接中断/应用重启后禁止自动重发生成请求。若适配器支持任务查询可恢复查询，否则保留 unknown 并告知可能计费。迟到结果只允许按原调用归属落盘一次，不自动恢复另一笔生成。

取消须区分请求取消成功与本地停止等待。无远端取消保证时不显示“已取消生成/已退款”。图片已生成但本地写入失败应重试保存而非重生成；仅在可恢复数据已安全暂存或后端支持检索时提供恢复动作，不虚构可恢复性。

## 决策 6：图片是用户产物，Evidence 是执行事实

遵守 ADR 63：Provider 返回结构化 image UserArtifact，EvidenceIndex 持久化治理元数据，GoalTask 只引用 Evidence。不能将所有 evidenceRefs/日志当图库内容，也不能从 assistant 文本中的图片路径构造假产物。

远端返回 base64 时，受限解码并核验 MIME/文件头、尺寸、最大字节数，防止超大响应和无效图片；保存到宿主管理的会话产物目录，使用受控随机文件名和原子写入，登记摘要。仅 URL 响应则按适配器允许来源受控下载，不转发生成凭证到任意 URL，限制重定向、体积和超时；UI 不依赖短期 URL。异常 payload 必须产生失败证据，不输出完成卡。

图片保存和结构化登记完成之后才可显示“已保存到本次对话”。应用重启可从既有事实链恢复，不建立 Renderer 附件真相库。导出到项目是独立文件写能力的授权行为，校验路径/符号链接/工作区边界及覆盖确认；不因导出失败删除原图。

Evidence 记录实际服务/模型、规范化参数、时间、状态、请求关联标识、实际已知用量及产物引用。未知价格不推算为零，订阅不标“免费”。提示词遵循会话保留策略，图片 base64 不进入日志或通用 tool preview。旧 screenshot 仍为 image，必要时调整展示文案而不是另造重复产物类型。

## 替代方案与后果

| 方案 | 取舍 |
|---|---|
| 仅内置 Skill + 脚本 | 不采用：凭证、计费、产物和重试治理容易散落在 shell，难以提供统一界面 |
| 生图绑当前聊天模型 | 不采用：用户切聊天模型不应失去独立配置的图片服务 |
| 先建设通用 hosted tool 平台 | 不采用：不对应已核对的这条图片端点执行链，增加无关范围 |
| 各厂商独立生图页面和 Key 库 | 不采用：重复配置与事实源，不利于授权和产物统一 |
| 一个万能 HTTP/JSON 透传适配器 | 不采用：隐藏认证、参数、任务语义差异，无法承诺兼容 |

正面：复用既有连接和治理流程，支持多服务/多认证，图片可被任务继续使用。代价：配置用途迁移、消费状态机、各厂商适配器与交叉测试都须实现，不能把订阅探针改名即交付；订阅端点还存在变化风险，因此按服务独立开关并保留实验性标记。

## 实施与验收

代码接缝、P0–P3 工作项、完整交叉矩阵见[产品实施规格 §6–§8](../../design/product/image-generation-implementation.md)。任何平台标为可用之前须通过该适配器契约测试及经过用户授权的真实冒烟。没有凭证时阻塞真实验收，不能为了完成计划读取其他客户端凭证或静默使用另一计费路径。

架构评审确认后才能实施 A 级改动；接受本草案不等于各厂商已经接通。回滚以禁用新增调用入口为主，旧聊天配置、凭证、产物和 Evidence 保持可读，不做破坏性迁移。
