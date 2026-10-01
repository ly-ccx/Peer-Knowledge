# B5-03 远程项目准入实施边界

创建时间：2026-10-01
最后更新：2026-10-01

状态：Accepted。负责人授权完成剩余Beta5/RC、必要修复、Review、合并、预发布及完整自测与测试文档；GA等待用户全面测试确认。ADR85 Accepted，ADR75既有边界沿用。B5-01已合入，B5-02最终PR #87双平台CI通过并合入dev `31527990`；本卡独立分支已同步latest分页接口。

## A级协议与能力边界

- 新 type=project.submit 的严格联合请求，只接受 project.list / project.conversation.read / project.session.read / project.input.submit；已有 task.submit/task.read字段集合与接口保持。
- 设备端resolveLocal同步读取授权，await事实读取后同步复查，防止授权快照在微任务间变旧。所有操作复查本机绑定、撤销、bindingVersion、delegationVersion、connectionEpoch、online及30秒请求寿命。project操作按机器人本机委托和能力位准入；默认关闭。session归属由本机目录决定。
- 本机设置 projectGrants[]={workspaceId,allowProjectRead,allowProjectMessage}，发消息依赖可查看；传输投影的全局能力位由这些行派生，并保留逐机器人权限。最多200行；旧单workspaceId配置在读取适配中只给对应机器人查看，不给发消息；更新时持久化并递增delegationVersion，当前连接重新准入/重连。不会因全局位为true而把权限扩大到其他机器人。
- project.list只返回有效且获授权机器人。conversation最新分页≤50，只含user_input/agent_reply/system_card，文本≤4000字；卡片只含有界摘要和电脑批准提示，无决定操作。session只含任务投影、报告摘要；对话附最多50项任务短摘要（160字）和最多20项待批准短摘要（250字），均无动作。2MiB容纳50条4000字Unicode及有界元数据。所有投影用字段白名单，不导出本机路径、Evidence原文、文件引用、工具结果或审批参数。
- project.input.submit只接受≤4000字纯文本，不接受附件、路径、工具、任意参数或远程批准。输入只写既有submitInput(surface=remote)，租约持有者沿原能力链消费；成功回执证明入队，不能称执行完成。
- requestId派生稳定inputId（身份命名空间），设备侧真实receipt store保存首次入队结果。先当前准入，再查回执。同requestId同逻辑正文返回首次结果；不同正文/工作区冲突。队列写成功而回执未写的崩溃窗口，用稳定inputId及首次队列结果恢复，不能重复消费。不创建模型ToolResult或伪Evidence。

## 必要路径补齐

原卡列protocol/remote-project-access/controller/remote-device-connection。为实际装配、持久幂等和200机器人授权补入：

- protocol index导出与remote-access测试；runtime-node index包导出、remote-receipt-store及测试（新增project输入回执表，既有M1执行receipt不变）。项目回执位于已登记device目录project-runtime/remote-receipts.sqlite；登记旧remote-binding.sqlite为device项，补data-store测试。
- runtime-gateway/setup-remote-access及测试：装配新handler、固定当前发布委托而不是每次请求延长有效期、当前settings复查和最近访问device事实。旧task.read对带delegationOrigin的任务核对实际工作区，不把请求workspaceId当本地归属。
- project-agent/project-agent-host及测试：onReady提供共享directory/inputQueue本机端口，作为远程表达的事实读取/消息入口，不加执行接口。
- main.mjs只依赖注入getProjectAccess/getRemoteSettings及完整session配置，净增≤0；不增加IPC或渲染层fs。控制器状态带安全最近访问摘要，后续B5-05设置页使用。

远程UI读取属于已授权事实投影，和本机UI相同，不是模型可执行工具；远程消息是用户输入，后续能力执行仍须Manifest→Projection→ToolCall→PermissionGrant→Evidence。不会另开远程工具执行通道。

## 帧预算与后续网关装配

旧4KiB限制无法容纳4000字中文或50条对话。为新增project操作固定有界预算：请求32KiB、授权投影128KiB、回答2MiB；正文/条数/字段仍各自校验。旧握手、heartbeat、task请求/回答保持旧限制；未上线或其他类型的超限帧拒绝。逐机器人投影最多200，旧M1投影仍最多32。B5-04补gateway/device-websocket对应类型检查与传输上限，不扩大旧类型，也不在网关保存或重放输入。新客户端与网关需共同升级。

## 验证与退出

四种操作完整准入矩阵、字段/版本/长度/标识、默认关闭与逐机器人权限、session归属、输入同ID幂等/冲突/崩溃窗口、投影路径/Evidence泄露、await后撤权复查、固定授权有效期、旧M1回归、settings版本与连接重准入、帧预算。协议/Runtime/Desktop全包与build/typecheck/architecture/IPC、双平台CI。代码/知识各自提交推送，Review通过后依既有授权合入。网关手机UI与设置页分别由B5-04/B5-05交付。
