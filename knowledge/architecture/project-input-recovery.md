# 项目输入恢复：草稿、待确认意图与真实回执

创建时间：2026-10-23
最后更新：2026-11-27

> 状态：E02–E04 本轮实施约束。沿 ADR85 已接受的本地输入队列/多入口和体验规范；本次先记录存储与协议影响，再实现。用户已授权这三个工作包的 P0 落地，不扩大能力、权限、Evidence 或签收规则。2026-11-27 补充明确宿主拒收分流与用户显式移除/退回草稿契约，不改变磁盘 schema、权限、Evidence 或既有 ADR 边界。

## 边界与分级

本次含 A 级的本机表达连续性存储/协议补充，B 级输入状态编排与 C 级 IME/状态表达。宿主拥有持久化；renderer 仍只发结构化请求。没有新增模型工具、执行通路、System Context 来源或远程权限。

恢复数据进入已登记 `projectRuntime`（device）的项目目录：`project-runtime/<workspaceId>/input-drafts/<surface>.json` 和 `input-draft-blobs/<digest>.json`。只支持 desktop/quick_chat/tui；不导出、不入模型上下文，不作为已接收、许可、执行或 Evidence。历史队列与会话格式不改写；不存在即空草稿，损坏/不可写明确失败，禁止静默重置覆盖。

附件沿既有 user_upload 类型和限额校验。大内容单独以内容摘要存 blob，草稿 manifest 只存引用，按键写入不重复传输/序列化整个图片；不接受任意路径引用。每份记录最多 32 个待确认 envelope、引用附件合计 96 MiB；正文最多 100,000 字符。暂不自动回收孤立 blob，避免删除其他待确认输入的附件；空间维护另立卡。

## 恢复责任与顺序

1. 每个 workspaceId + surface 隔离草稿（正文、引用对象/摘录、附件）和待确认输入。文本/附件改变只写本地意图；不会唤醒 Agent。
2. 发送生成一次 inputId，先把完整 envelope 持久化，再经原 `submitInput` 投入队列。此时编辑器可让出给新草稿，原内容由可见待确认记录承担恢复责任。
3. `ok` 或本地动画不证明已接收。只有匹配 workspaceId/inputId 的结构化 ProjectInput，或公共会话中同 inputId 的真实记录，解除待确认责任；`ok:false` 携真实 input 仍表示已接收但后续交接失败。
4. 未收到回执、超时、切换、关闭或重启保留原 envelope；用户重试使用原 ID/目标/正文/附件/answerTo。重开只恢复显示，禁止自动重发。输入队列继续承担事实与去重。30 秒只结束界面等待并标为未知，不取消宿主、不判断执行成败；真实迟到回执仍可核对。
5. 清除已确认意图的落盘失败时保留错误；即使重开后再次看到该 envelope，同 ID 重试由队列去重，不复制副作用。其他新草稿不被迟到回执清空。
6. 区分**明确宿主拒收**与**结果未知**：仅当宿主在入队前明确返回无 `input` 的前置拒收错误码白名单（`QUESTION_CLOSED`、`INVALID_INPUT`、`INVALID_INPUT_ID`、`INVALID_RESOURCE_FEEDBACK`、`RESOURCE_FEEDBACK_RECIPIENT_CHANGED`、`RESOURCE_FEEDBACK_ATTACHMENT_LIMIT`、`INTERACTIVE_FEEDBACK_UNAVAILABLE`、`NOT_FOUND`、`WORKSPACE_NOT_FOUND`）时，才归类为明确拒收（确定未入队、无副作用）；超时、断连、重启恢复及非白名单错误一律保守保持 `unknown`。纯当次选项按钮触发的 `QUESTION_CLOSED` 可直接移除；用户手打或带附件/引用的输入在 `QUESTION_CLOSED` 或其他拒收下不得静默销毁，草稿空时可还原草稿或标为拒收态由用户放回输入框/删除。
7. 用户显式**移除**或**放回输入框**：非发送中的待确认记录允许由用户显式移除或原子放回输入框，写盘通过同一 CAS 串行锁完成，**仅在 `write` 成功后才更新可见状态**；写失败或冲突保留原记录并暴露错误，禁止假成功。放回输入框默认要求当前草稿为空，绝不静默覆盖新草稿，并剥离已失效的 `answerTo` / `inputId`（因资源引用失效拒收时同时剥离失效引用）。移除 `unknown` 须先给出局部行内确认，说明仅清除本机待确认提示、若后台已收到不会撤回执行；已移除记录的迟到回执安全忽略，若宿主确已接收仍通过正常会话刷新呈现。磁盘 schema 与既有 `input-draft-store` / `drafts.rs` 保持不变。
8. manifest 原子替换并使用 revision compare-and-set；并发编辑冲突不得覆盖另一窗口的内容。保存失败保留当前内存现场并阻止未持久化的新发送；冲突提示用户复制保留本窗口后重开，不悄悄覆盖并发编辑。只有已完成的保存与附件读入能承诺重开恢复，硬退出前尚在进行的 IPC/文件读取属于发布验证限制。

## 接口与实现 seam

Protocol 定义恢复快照、附件引用和读/写请求。Desktop 新增受既有 frame/origin/window policy 管理的 `project-agent:read-input-draft`、`project-agent:write-input-draft`；应用服务先检查 enabled/真实 bot 归属，不支持 remote surface。TUI 调同一 runtime-node store adapter；shared runtime-core kernel 编排恢复，不含 fs、React 或执行能力，提交端口仍接原 inputQueue/IPC。

决策卡的操作处理中仅是表达；决定/核验/签收/交回继续消费宿主事实。主机决定返回的真实 approval 可用于显示回执，但不能把通用 ok 转成已批准；过期、拒绝、取消各自保留。新宿主卡片 props 优先于局部迟到回执；approval/plan_approval/confirm_result/completion_review 不接受旧展示 resolution 覆盖当前事实。TUI cancel 沿原许可 gate 产生不授予执行的结果，并独立持久为 cancelled；不添加授权入口或放宽 gate。核验中/未知不转成失败，核验通过不转成已签收。

## 本轮允许范围与发布验证

允许：protocol 恢复契约与纯投影、runtime-core 恢复 kernel、runtime-node 本地 draft store/数据登记注释；Desktop project-agent 应用服务/IPC/preload/client、BotComposer/Conversation 与 hook、Quick Chat、共享 IME seam/经典输入的调用、决策与核验消费者；TUI project client/host、ProjectApp 的输入与回执适配；i18n、必要契约测试；知识矩阵/计划/交付记录。禁止改 Provider、工具权限、模型提示、发布物、其他任务工作区与个人数据/运行实例。

必要的契约测试随代码编写，但本轮按用户要求不运行测试、build/type/architecture/IPC 检查、截图或交互回归。IPC 目录和生成 preload 只做生成同步/内容审阅。发布前必须在合并所有 PR 的最终候选验证草稿跨切换/重开、未知回执同 ID、附件恢复、并发/损坏/写失败、IME/补全/Escape、过期决定与核验/签收/交回边界。实现已审阅不等于候选验证通过。
