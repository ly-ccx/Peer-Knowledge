# ADR 115：智能输入建议与用户草稿边界

创建时间：2026-10-31
最后更新：2026-10-31
状态：Accepted（2026-10-31 用户要求“完整做完，自己独立验证整个功能”，授权按本方案实施及提前功能验证；实施、验证与发布状态分别登记，不替代交付记录或授权发布）
级别：A（Protocol、System Context、模型角色、未发送草稿准入与配置边界）；实施包含 B 级宿主／IPC 与 C 级输入体验。

产品依据：[产品理念与价值对齐](../../design/product/peer-product-alignment.md)。
架构依据：[架构治理](../architecture/20-architecture-governance.md)、[System Context](../architecture/19-system-prompt-context-architecture.md)、[ADR 83 模型分工](83-model-routing-by-role.md)、[ADR 85 宿主与输入](85-project-agent-hosts-inputs-and-surfaces.md)、[ADR 100 决策生命周期](100-actionable-attention-and-question-lifecycle.md)、[ADR 101 Bot 授权主体](101-bot-owned-access-policy.md)。
完整方案：[Peer 智能输入建议](../../design/product/peer-input-prediction.md)。
实施入口：[IP-00—IP-07 任务卡](../../playbook/v0.1.0/input-prediction.md)。

## 1. 背景与目标

用户希望 Peer 根据对话现场预测下一句表达，以灰色文字呈现，按 Tab 或右方向键即可填入草稿，减少组织语言和决定如何表达的成本。参考截图只说明外部产品的可见交互，不证明其内部架构或模型机制。

功能同时支持空草稿的下一句预测（next_turn）与已有草稿的末尾续写（continuation）。默认只显示一个短候选，允许不建议。它服务于目标表达、补充约束和结果追问，不把本应由 Peer 自主推进的工作变成反复建议用户发送“继续”。

## 2. 决策摘要

1. 建立独立的输入预测认知请求，由主进程服务管理，复用既有模型路由、Provider Adapter 和 Encoder；不启动 AgentTurnExecutor，不写普通聊天消息，不进入工具循环。
2. 新增非必要模型角色 input_predictor，受项目模型范围、localOnly、显式路由、费用预算及可用性约束。没有合适路由时不建议，不静默换账号、云端或高成本模型。
3. 预测规则通过显式 Context Source 和独立的装配 profile 准入，复用唯一 System Context assembler；聊天／草稿等事实保留原始角色和来源，不提升为系统指令。
4. 未采纳候选只在短期内存中存在，不是用户输入、授权、记忆、Tool Result、Evidence 或任务状态。
5. Tab／右方向键只触发可撤销的草稿编辑；Enter 仅按已有发送设置处理真实草稿。接受建议、发送消息、收到输入回执、执行、验证、签收是不同事实。
6. 预测请求使用严格空工具面，并且没有工具执行端口。任何意外工具调用使结果失效。以后新增上下文检索或本地能力仍走唯一能力链。
7. 下一句预测和未发送草稿续写分别启用；现有安装缺省关闭，启用总开关后默认仅 next_turn，continuation 需明确开启并说明草稿将交给所选模型。
8. 所有候选绑定输入实例、草稿版本、宿主上下文版本、路由／配置版本和有效期。采纳前做宿主本地有效性检查与 Renderer 草稿版本检查，迟到响应不得覆盖新草稿。

## 3. 职责与能力链

| Module | Interface 与归属 | 约束 |
| --- | --- | --- |
| 输入建议控制器 | 输入实例、selection、IME、候选状态、编辑事务；Renderer | 不读取本地文件、凭据或权限真值，不自己连接模型 |
| 输入预测服务 | request／cancel／validateCandidate、状态与预算；共享 runtime，Desktop 注入宿主端口 | 处理调度、取消、快照、校验和诊断；不执行工具或提交用户输入 |
| Context profile | 预测角色规则、允许来源、版本和预算；system-context | 不把执行型 Agent 的全量提示词或工具目录带入预测 |
| 模型路由／传输 | input_predictor 角色选择、编码、取消与用量；既有 seam | Provider 特有字段留在 Encoder，不伪造 webContents 或聊天 stream |
| 现有草稿与输入 | ProjectInputRecovery 等既有草稿流程和正式发送端口 | 只在用户采纳后接收文字编辑，不增加第二个发送／回执入口 |

纯模型推理属于认知请求，不是模型调用本地工具。后台服务对既有状态库的受控读取属于宿主 Context 装配职责，不能泛化为允许任意文件／目录读取。模型发起的新增检索、附件展开、Shell、MCP、Skill 或 App 操作必须继续经过：

```text
Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence
```

配置启用不是 PermissionGrant；预测调用记录不是执行 Evidence。关闭预测只停止预测和后续草稿外发，不中止原任务或撤销已经产生的工具事实。

## 4. 上下文与信任边界

首版只准入当前会话有界公共消息、最近完整公开回复、用户已发送的约束、当前已选择且允许进入该模型的文字引用、必要结构化状态；continuation 额外准入当前草稿。正文是事实内容，始终低于产品内置规则。

不准入隐藏推理、原始工具参数／日志、其他项目历史、剪贴板、未展开文件、未发送附件正文或未被准入的 MCP／Skill 内容。首版存在附件或 resourceFeedback 的草稿暂停预测，避免在材料不完整时猜测。

普通预测在影响当前输入目标的权限、计划批准、结果签收或结构化选择未决时停用。输入建议不代填“同意授权／验收通过”等决定，不选择真实卡片默认项，也不回答模型并不知道的个人事实。

预测 profile 复用已有准入策略，继承适用于当前主体的强制限制。不能借“小上下文”删除有效限制；必需来源缺失、版本无法确定、用户约束无法在预算内保留时返回 unavailable／none。与其他在途 Bot 指令／能力绑定决策的整合由 IP-00 重新核对，不引入旁路注入。

## 5. 草稿、版本与采纳

预测有独立 composerInstanceId 与立即递增的 draftVersion，不能把异步落盘的 revision 当逐键版本。selection／引用／附件／目标变化也使当前候选失效；候选未写入草稿，不参加字数、hasContent、发送、复制或恢复。

采纳流程：键盘或可访问按钮锁定当前 candidateId → 宿主有界本地 validateCandidate 检查当前上下文、配置、主体和 TTL → Renderer 对触发采纳时的草稿／selection／IME／目标做 compare-and-set → 原草稿 seam 一次性提交文字编辑。等待验证期间用户仍可编辑，任何变更使本次采纳放弃，不得回填。

校验不访问模型，不授予执行权限，不承诺跨进程中所有事实永远不变；正式发送与后续执行仍重新使用既有闸门。采纳后内容可能随任务发展而过时，用户保有编辑责任与控制。

采纳作为单个编辑事务，可一次撤销到原文本和 selection；撤销不删除引用／附件。直接 setState／setRangeText 不能被当成浏览器原生撤销可用的证明。首版需在实际 Electron 输入 seam 实现统一事务，并保证后续手工编辑、撤销、重做次序；不能另造持久草稿库。

IME、现有命令／引用补全和有效浮层优先于智能建议。建议不可见、无效或正在 composition 时不消费 Tab／方向键。Shift+Tab 保留导航。采纳后抑制同一交互代次立即再展示，第二次 Tab 能正常离开；Escape 也必须提供可达退出。

## 6. 配置、隐私和存储

目标设置为 settings 的一个版本化 inputPrediction 子对象：enabled、continuationEnabled、disabledWorkspaceIds、dailyRequestLimit、dailyTokenLimit；角色路由沿 modelRouting.roles.input_predictor，项目限制沿既有 ProjectModelPolicy，不保存第二份模型身份或凭据。缺省读为关闭，不在读取时写配置；保存失败以宿主回执为准。每日请求／token 初值与计数恢复要求见完整方案 §11—§12，计数复用原用量存储，不新增预测账本目录。

开启时说明公共会话上下文会送至预测角色所选模型；开启 continuation 时另说明未发送草稿会送至该模型。显式选定路由内的 fallback 也必须受相同项目与数据准入限制，不允许从 localOnly 静默切换到云端。

不新增候选／草稿正文持久化目录。短期缓存有 LRU、字节与 TTL 上限；候选撤销、关闭、切换、宿主释放时清理。候选采纳后沿原草稿存储保存；未发送草稿已有的本地恢复策略不被本 ADR 改写。

普通诊断和 Provider trace 不记录原始草稿、候选和含正文的请求快照，仅记录用途、路由、来源版本摘要、耗时、用量与结果码。包含草稿的 debug dump 首版不提供；不能因通用 Adapter 默认 tracing 打开而偷偷持久化。采用已有用量存储，不新增遥测上传。

## 7. 模型、预算与失败

角色初始参考 fast 档位，但 fast 不保证模型实际快速或低价。只有明确配置且准入通过的路由才发请求；IP-00／IP-02 必须避免默认 role resolution 自动把普通聊天模型当作已选择的后台预测模型。

优先短输出、少推理、单候选和合法结构响应。兼容模型不支持 schema 时可用相同 JSON 契约解析，解析失败不建议；不走自动“修 JSON”第二次调用。模型自报置信度不能替代质量评估。

请求优先级低于正式用户推理；首版每宿主最多一个预测请求，不堆积过期队列。每输入实例有节流，每角色有每日用量限制，缺价格时实际 tokens 与费用未知分别记录。预算不足不阻塞输入、不弹审批或聊天错误；设置页按需解释不可用原因。上游已消费的 tokens 即使取消也仍记账，不能宣称取消即免费。

## 8. 备选方案与取舍

| 方案 | 不采用原因 |
| --- | --- |
| 让主 Agent 每轮输出隐藏建议 | 耦合正文生命周期与执行角色；难独立取消、预算、准入和审计；无法自然响应草稿变化 |
| 将预测作为有工具的 Agent 子任务 | 对输入辅助引入权限、任务和执行副作用，超过目标需要 |
| Renderer 直接调模型 API | 暴露凭据和供应商细节，绕过路由／本地准入 |
| 在 textarea.value 预写建议 | 未采纳内容变成可发送草稿，混淆输入、恢复与意图 |
| 所有按键均重新调用模型 | 延迟、费用及隐私不可控，放大竞态 |
| 同时显示多个候选 | 首版增加选择负担；完整方案保留不建议，而非强行凑选项 |
| 为个性化保存候选全文 | 没有当前需求，不建立额外长期用户画像或记忆来源 |

## 9. 范围、后果与验收

首期交付 Desktop 主 Bot 与经典可编辑 Composer 的 next_turn／continuation；首落主 Bot，再复用到经典输入框。新会话缺少上下文、只读任务现场、Quick Chat、TUI／CLI／远程入口首期不展示；未来增加 Adapter，不能复制预测后端或发送真相。

新增 Protocol、角色、Context profile、IPC 与设置属于 A/B 级变更。实现要补契约、状态、预算、取消、IME、撤销、隐私与回归用例，但运行时机服从代码仓最新 Validation Scope：日常只审内容／diff，发布前执行完整联合候选验证，用户另有明确授权除外。

硬性反例：空草稿回车发送候选、迟到结果覆盖新输入、composition 采纳／误发、Tab 陷阱、跨 Bot 串候选、trace 泄露正文、建议生成授权／验收事实、后台预测阻塞用户请求。任何一项均阻塞功能发布。

## 10. 规范来源、状态与审阅记录

本轮代码锚点基于 Peer-Agent HEAD `5dffbd4b4ced0bb841c9e879debd50b8bb081b9c`，知识工作树基于 `f5af51d84cb8adf63dac9a1d3802889308de2be3`；不是产品验收源码。

知识工作树尚未包含新体验规范，但已通过 git show 只读核对 origin/main `f805c053ca84e45bfb0a83a7f465d769d8f58e95` 的规范、motion、transition、开发工作流和两份矩阵。固定来源及链接在完整方案 §15；实施前须整合进实施工作树，不复制旧规范或把缺文件解释为规范豁免。

ADR 编号已核对本地文件及 fetch 后所有 origin 远程引用：114 已被回复引用方案使用，本 ADR 使用 115。跨任务尚未推送的占号无法由本轮证明，派发前再次检查。

2026-10-31：只完成方案、ADR、任务卡与入口索引，进行实现者内容／diff 自审；未改代码，未运行测试、构建或产品回归，未宣称独立复核。Proposed 不因文档完成自动升级为 Accepted，也不自动加入下一 RC。

### 2026-10-31 实施启动与 IP-00 收敛

用户随后明确授权完成全部功能并自行验证。代码使用独立 codex/input-prediction 工作树，基于开发线 `73ff763a`（RC31）；知识使用独立 codex/input-prediction-implementation，基于 main `2f83d5f`。两份原工作树及在制修改不动。当前工作树已包含完整体验规范及两份矩阵，不再缺少该依赖。

- 无工具推理：既有 Provider Adapter 增补显式回调 sink 和 metadata-only trace 策略，继续由原 Encoder 编码，不伪造 webContents；共享 text inference 只调用一次传输，没有工具 executor。Responses 复用现有响应消费者；Qoder 关闭传输的队列／瞬态重试，预测截止独立生效。
- 草稿编辑：共享 Composer 编辑事务持有有界的本地文本／selection 历史，协调 beforeinput 的 historyUndo／historyRedo 和平台快捷键；正文编辑、采纳、撤销统一经原草稿 edit 端口，持久草稿 schema 不变。真实 Electron 验证普通输入与采纳的撤销次序，不凭 setState 推断。
- 预算：复用 usage/requests.jsonl。输入预测增加无正文的 purpose、预约／结算与估算标识，同一预测 requestId 的预约与结算只聚合一次；启动从日志重建当日消费，读取不完整时拒绝新预测。普通聊天记录与 lifetime 不改写，也不新建预测数据库。
- 接线：共享 input-prediction 服务与输入内核；Desktop 专属 snapshot／credential／IPC Adapter；主 Bot 与经典 Composer 通过相同控制器复用，SettingsGroup 中明确开关、模型、草稿外发与限额。正式用户请求优先，取消预测不影响任务。
- 提前验证由本次用户指令明确授权，覆盖契约、Provider／服务、两个真实输入面、IME 事件、撤销、失败、隐私与预算，并执行相关构建／类型／架构／IPC 检查。实施者自审记 independent=false；不把本次功能验证冒充未来版本联合候选或已安装版验收。不发版本、不安装或重启用户实例。


### 2026-10-31 实作补记

实现沿既定边界落地，详细收敛见[完整方案 §16](../../design/product/peer-input-prediction.md#16-首版实现收敛2026-10-31)。增加第四个只读 status IPC 为设置提供真实不可用原因／当日用量；不增加授权或执行事实。凭证仍由原 CredentialHelper／resolver 管理，以可取消 Worker Adapter 隔离同步 OS 访问，避免后台预测阻塞输入主线程。Provider callback 与 metadata-only 策略只扩展既有推理 seam；原普通聊天调用兼容。

Context Source v2 的历史是保留 role 字段的事实数组，避免模型接着扮演原助手；固定预测规则仍只由显式 Source 提供。暂无 tokenizer 的首版采用保守 UTF-8 字节上界，无法在预算内保留强制指令时 abstain。该取舍减少适用范围，不放松上下文或权限限制。验证、已知边界及提交身份见[功能回执](../../playbook/v0.1.0/input-prediction-validation.md)，不作为发布或安装授权。
