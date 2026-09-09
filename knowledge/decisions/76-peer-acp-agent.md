# ADR 76：Peer 作为 ACP Agent

日期：2026-09-08
状态：实施边界已确定，尚未完成实现或验收
级别：A（新增外部协议与授权交互适配）

## 目标与非目标

通过 `peer acp` 提供本地 stdio Agent Client Protocol Agent，让编辑器作为交互客户端调用 Peer。Peer 保留模型选择、Agent 循环、本地执行、授权与 Evidence 的责任。不是 ACP Client，不接入其他 ACP Agent，不要求 Desktop 或终端 UI 启动。产品依据为 `design/product/peer-product-alignment.md`，治理依据为 `knowledge/architecture/20-architecture-governance.md`。

首期仅实现明确验证过的稳定协议能力。不实现远程监听、客户端凭据转发、会话恢复、多模态、客户端文件/终端代理、动态客户端 MCP 配置或任意协议扩展；不宣告这些能力。非空且不支持的配置必须明确拒绝，不能静默忽略后让客户端误以为已生效。

## 协议与入口

参考：https://agentclientprotocol.com/protocol/v1/overview 。ACP 使用双向 JSON-RPC 2.0；initialize 协商版本与能力，session/new 创建会话，session/prompt 开始一轮，session/update 提供进度，session/cancel 为无需响应的通知。具体字段在实现前以官方 schema/SDK 验证，不自行发明兼容协议。

`peer acp` 必须在终端渲染器加载前分流，stdout 专用于换行分隔的协议消息；诊断走 stderr。没有 TTY 也可运行。不改变既有交互入口和 peer exec 的权限策略。

## Module 边界

ACP transport 负责消息边界、请求关联、校验、错误响应与断连。ACP Agent adapter 负责会话路由、能力协商以及 Peer 状态到协议更新的映射。运行时继续使用现有 CLI runtime/controller/host 与协议类型，不在适配层直接执行 shell、文件操作或工具。

所有能力仍经过 Capability Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。ACP 不是模型 Provider；不把客户端数据注入系统指令，不向核心运行时散布 ACP 专用分支。

## 会话与本地状态

每个 ACP session 绑定独立 Peer conversation/controller、workspace 和取消域。cwd 必须为有效本地绝对目录。sessionId 不能直接当文件路径使用。不同会话不得共享待审批请求或对话历史。同一会话一轮未结束时的新 prompt 明确拒绝，避免交错。

使用 Peer 已配置的本地模型和凭据设施；不通过协议返回密钥，不通过客户端传入数据覆盖密钥。未配置时明确返回配置/认证错误，不启动交互登录。首期不提供协议登录能力。

## 会话模型选择（2026-09-09 后续）

采用官方推荐的 Session Config Options（https://agentclientprotocol.com/protocol/v1/session-config-options）：session/new 返回 category=model、type=select 的 configOptions；session/set_config_option 接受 model 配置并返回完整配置状态。当前 SDK 提供 setSessionConfigOption；不自行实现已移除或实验性的模型切换方法。具体 Zed UI 实测与协议自动化结果分开记录。

唯一状态来源是每个 ACP runtime 的 TuiModelSelectionControl。仅投影 catalog 中 available 的条目，选项值使用 providerId 与 modelId 的无歧义组合，不暴露凭据。显示名称保留 Provider 信息以区分同名模型。切换通过既有 setSelection，推理强度在目标模型支持时保留，否则使用其默认值；同步当前会话持久化模型，不写全局默认配置。

同一会话 active prompt（包括工具执行及审批等待）期间拒绝切换；配置更新同步完成，不留异步窗口供新 prompt 读到半更新状态。未知会话、配置键、模型值均拒绝且不改变状态；其他会话不受影响。成功返回实际生效配置，后续模型请求与上下文窗口读取同一选择器。

验证矩阵：合法/非法模型 × 空闲/忙碌 × 单/双会话；模型标识覆盖同名不同 Provider 与不可用条目；集成测试必须断言切换后 HTTP 请求的 model 和双会话选择隔离。仅 UI 选项变化不构成完成。既有授权、取消与 Evidence 路径保持不变。

## 渠道分组投影（2026-09-09 修订）

用户确认采用“分组一致，隐藏置灰条目”。实际聊天入口是 TokenUsageDisplay 的 CascadingMenu，不是 ChatSurface 的平铺 modelOptions。抽取无执行副作用的共享模型菜单投影到 protocol，Desktop 与 ACP 复用：按渠道首次出现顺序分组，组内保持输入顺序，不按名称排序或去重；组名沿用渠道显示名称（含 ChatGPT 订阅本地化），项名为 modelLabel || model。内部唯一 ID 不追加到显示名称。

ACP 使用标准 SessionConfigSelectGroup。由于标准选项没有 disabled 字段，投影时隐藏不可选项并移除空组，不把不可用项变成可选；分组须先建立再过滤，以保持渠道首次出现顺序。运行时选择仍以原 providerId/modelId 为真源，菜单不写入全局配置，不变更执行或凭据授权。不得从“模型 · 渠道”展示字符串反向拆分元数据。无共享渠道元数据的环境变量模式用单组 Peer 展示原模型名。

验收矩阵：渠道同名/异名 × 可用/混合/全不可用；模型有/无 modelLabel；交错渠道与重复模型保持顺序；当前值属于分组选项；禁用项无法切换；原忙碌、非法选择、会话隔离、HTTP模型请求、授权与取消测试保持通过。协议分组不保证 Zed 呈现与 Desktop 完全相同的二级菜单，不能将自动化验证称为 Zed 人工实测。

## 推理强度与上下文窗口（实施中）

ACP 会话配置将暴露当前模型支持的推理档位，以及 modelOptions 中首个含正数 contextWindow 的定义；不得凭静态上限生成容量选项。共享配置读取保留 modelOptions/modelOptionValues，默认值解析复用 resolveLlmModelOptionValues。无容量选项的模型只采用静态容量，不显示虚构菜单。

选择只存于当前 ACP 会话。模型切换时强度在支持范围内保留，否则回退目标默认；上下文选项仅在目标定义支持同一值时保留，否则回退目标配置/默认。provider 请求预算、controller 统计/压缩与会话容量记录必须读取同一会话真源。忙碌期统一拒绝所有配置修改，非法值不得改变状态。

验收矩阵：强度支持/不支持 × 容量可选/固定；两者均可选时覆盖每个强度×容量组合；每种模型切换验证保留/回退；合法/非法值×空闲/忙碌×单/双会话。实际HTTP请求断言强度，实际上下文统计和压缩断言容量，不能仅测菜单。最终重建并运行独立二进制，不以源码替代。

## 权限与执行归属

文件读写与终端执行仍归 Peer 本地 Provider，客户端 fs/terminal 能力不改变执行归属；首期不调用这些客户端方法。能力协商不构成 PermissionGrant。默认采用逐次授权，不继承可能扩大权限的 UI 持久化全权限设置。

现有运行时提出权限请求时，adapter 发送 session/request_permission，并将有效的本次允许/拒绝决定交回既有授权接口。不得在 adapter 中直接运行工具。首期仅提供一次允许和一次拒绝选项；未知 optionId、错误响应、超时、取消与断连均按拒绝处理。审批与 session、toolCallId 和请求关联；迟到结果不能使已取消操作重新执行。未能映射的交互型能力必须在 Projection 层禁用或失败关闭，不能假装已获授权。

客户端可以报告用户批准，但本地授权 store/host 才是执行权限真源；协议批准不持久化为全局信任。

## 消息与 Evidence

助手增量映射为 agent_message_chunk；工具生命周期按稳定 toolCallId 映射 tool_call/tool_call_update。不能将助手文本解析为真实工具事件。工具结果与 Evidence 引用来自本地结构化结果；ACP 展示是这些事实的投影，不替代本地 Evidence。未完成的工具不能标记 completed。

取消需终止 controller/运行任务并结算待审批；session/prompt 在清理后返回 cancelled。断连清理所有会话、取消任务与待决请求并释放资源。协议错误不得泄露凭据或内部敏感对象。

## 验收矩阵

独立行为轴及必要交叉用例：

| 行为轴 | 交叉用例 |
|---|---|
| 生命周期 × 输入有效性 | 初始化前请求、有效初始化、不支持版本、未知方法、畸形 JSON、非法参数 |
| 会话 × 并发 | 单会话顺序、多会话交错、同会话重入拒绝、未知会话 |
| 更新类型 × 结束方式 | 文本/工具分别正常结束、取消、运行时失败；顺序和 toolCallId 稳定 |
| 权限决定 × 会话 | 允许/拒绝/未知选择分别在单会话和双会话隔离下验证 |
| 待审批 × 中断 | 取消、断连、超时、客户端错误、迟到允许均不执行工具 |
| 入口 × 环境 | peer acp 管道无 TTY、stdout 纯协议；原 help/version/exec/TUI 入口回归 |
| 能力声明 × 请求 | 不支持的媒体、会话恢复、客户端 MCP 配置明确拒绝且不宣告支持 |

每格必须对应实际测试名及运行证据，不能只测 transport 就宣告完成。真实子进程协议握手不等于真实模型工具授权闭环；分别记录结果。未执行部分保留未完成状态。
