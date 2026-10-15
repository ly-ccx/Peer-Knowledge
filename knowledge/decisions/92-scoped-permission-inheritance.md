# ADR 92：具体资源授权与执行链继承

创建时间：2026-10-11
最后更新：2026-10-12
状态：Accepted（用户明确要求补齐图片授权，并全局检查权限继承；先记录决策再实现）
级别：A（权限、协议、批准记录），B（Desktop/TUI 执行与恢复），C（授权入口文案）
依赖：ADR 49、85、88、89、90、91

当前完全授权语义以 §9 为准。§2–6 的具体图片批准与 30 分钟资源许可用于需要逐项审批的模式；历史实施记录保留原行为与证据。

## 1. 已确认的断点

RC12 的主 Bot 在用户通过普通问题选项表示同意后，读取五张项目外截图仍得到 `image_outside_read_scope`。图片 Provider 在正式 PermissionGrant 请求前硬拒绝 project_agent；普通问题答复本身没有形成宿主授权。不能据此把聊天文本当通行证。

全局审计还发现：Desktop 同一 toolCallId 的批准复用不绑定参数或能力；“允许一次”会被记为同类文件写/Shell 许可；TUI 会话许可仅绑定能力和工作区，未绑定参数；授权条的“一直允许”会批准所有待处理请求。现有一次性恢复批准虽绑定摘要和 session，workspace 未进入索引键；恢复审批检查又排在无审批者拒绝之后。

## 2. 决策与 Module

新增共享 `PermissionInheritance` Module，集中计算授权身份、具体操作摘要、资源批准、有效期与撤回。Desktop/TUI 负责提供宿主身份与现有 ApprovalStore，不能从模型参数取得父会话身份。主 Bot 协调权仍不是权限签发权。

本次资源继承限定为 `local.image.read` 的单一真实图片文件。许可绑定 workspaceId、机器人父会话、真实路径、文件身份（设备、inode、大小、mtime、ctime）、`read_image_for_model` 动作与 30 分钟有效期。无 workspace 身份的普通会话只能在自身会话内复用。委派执行者须从 GoalPlan 的 delegationOrigin 回读 workspace/session/父会话，并检查当前计划没有取消、暂停或被取代；核验者和恢复执行者走同一判断。独立任务不能从另一机器人会话继承。许可不扩大 readableRoots，也不授权目录、其他文件、文本读取、Shell、写入、浏览器、MCP 或密钥。

Provider 在范围外图片读取时进入既有结构化权限入口。项目代理的工具职责仍由角色与 Runtime Projection 约束；已开启的 `full_local` 按 §9 覆盖其获准使用的本地能力，项目外读图不再额外逐张审批。非 Full 模式继续按具体资源许可审批。无人工审批者时先检查有效宿主许可，未命中立即结构化拒绝；不能等待不存在的确认窗口。图片读取前后仍检查真实文件身份、取消和大小/解码上限。

## 3. 用户决定与复用

- “允许”只批准当前操作；后续同类写入或命令不因这次批准获得许可。
- 明确选择本轮图片许可后，宿主记住该具体图片，直属执行者/核验者可在有效期内再次实际读取。入口明确图片会交给当前模型，范围为当前机器人及其任务。旧普通问题答复不迁移成 PermissionGrant。
- “一直允许”只作用于当前展示的请求。自动合并只允许同一宿主身份、相同具体操作；不能批量批准不可见的其他请求。
- 通用 scope/session 批准绑定 capability、参数摘要、conversation/session、workspace；命令程序名称或文件写能力名称不足以复用。
- 同一 toolCallId 的恢复桥还需相同能力、参数、工作区、会话和有效期，最多复用一次。Goal 高风险确认只有宿主明确标注的实际目标能力可复用，不能任意跨能力。
- 下调或更改访问策略清除既有内存批准，并撤回当前宿主记住的图片批准；当前策略、取消、租约与只读闸仍在每次执行时重检。

## 4. 持久化与 Evidence

沿用已登记的 projectRuntime `approvals.jsonl`，扩展可选 `imageReadGrant` Protocol 字段；不新增授权文件、图片副本或 renderer 真值。仅本地用户明确 scope/session 决定可签发可继承图片批准。批准记录保留原 toolCall、主体、范围、有效期与 local_ui 来源。压缩保留未过期的有效图片批准；撤回追加 expired 状态。重启从最新状态回读，不把历史 audit-only 批准推断为资源许可。

存储失败不签发可继承许可。过期、撤回、文件变化、任务停止和主体不符不继承。工具结果保留真实 PermissionGrant 的 grantId 与结构化范围，Evidence 仍沿原工具链生成；像素只进入宿主视觉侧带。用户/Agent 普通文本和报告不参与授权判定。

## 5. 验收

先用聚焦回归复现：范围外主 Bot 图片请求被硬拒绝、批准一次被扩大、同编号不同参数/能力误放行、TUI 同能力不同操作误放行；修复后全部红转绿。

验证图片批准→主 Bot→子执行者→Verifier→重启恢复的真实 Provider 像素链；另一 workspace/父会话、不同文件、变更文件、取消任务、无审批者、过期、撤回及存储失败拒绝。验证主 Bot/只读 Verifier 写闸、objective probe 与自动化政策不被继承覆盖。运行受影响包完整测试、build/typecheck/architecture；授权入口变更执行产品截图逐图自审及 verify。

明确真实模型、日常安装版、独立审查覆盖边界。此次不改旧任务完成事实，不发布 RC，不替换日常安装版。回滚时旧 ApprovalStore 读者忽略新可选字段；新版不为旧记录补造资源许可。

## 6. 全局审计与实现落点

| 路径 | 原问题 / 核对结果 | 本次处理 |
| --- | --- | --- |
| Desktop 图片 Provider / 项目代理闸 | 范围外图片在人工授权前硬拒绝；带 workspacePath 的图片请求还可能被派到文本文件授权 | 改走 local.image.read 的正式 PermissionGrant，具体文件身份进入参数摘要；项目代理仍不能接收 global full/session 自动许可 |
| 主 Bot → Worker → Verifier → 重启 | 历史批准不提供图片资源真值，无 approver 时先拒绝 | 共享模块核对宿主计划、父 Bot 与 session；现有批准日志存资源授权，继承命中后才判断是否需要 approver |
| 一次授权 / 通用会话授权 | 文件写、命令名称或能力相同便复用 | once 不进 scope 缓存；scope/session 绑定具体参数、能力、会话、计划和工作区；恢复簿键补 workspace |
| Goal 前置确认 → Provider | 同 toolCallId 可跨能力与参数复用 | 限一次桥接；确认处记录宿主投影出的实际能力；Provider 参数规范化只沿同一次宿主外层参数桥接 |
| 并发主回合 | 会话工具上下文缓存被不同回合改写角色、目标路径、权限与回调 | 每回合 fork 上下文，只共享工具缓存；角色、授权与目标字段各自独立 |
| 本地授权条 / Bot 授权卡 | “一直允许”批准所有排队请求；陈旧图片卡缺资源授权入口 | 只决定当前展示操作；图片卡明确读取并交给模型、具体文件、当前 Bot 及任务、30 分钟；重启后同样持久签发 |
| 撤回 / 文件变化 / 解码期间 | 已缓存许可可能继续返回像素 | 改访问策略清空缓存并撤回图片批准；Provider 读取前与返回像素前重检授权；文件身份变化拒绝 |
| TUI | 同一 session 相同能力批准不同参数；chat mode 下角色边界未再次核对；toolContext 未传入 Node Runtime | 同一操作摘要隔离；当前角色和 mode 共同执行能力闸；转交权限上下文、检查取消和租约 |
| MCP / Skill / Hook / 自动化 / objective probe | 核对各 Provider 的宿主策略及执行闸，不从模型说明取得批准 | 不新增图片之外的资源继承，不将 Shell/文本/图像许可互换；原自动化、只读及 probe 执行拒绝保持 |

普通非委派 Goal 只能沿自身宿主绑定会话使用资源许可，不能伪称另一 Bot 的父身份。局部 UI 只提交用户决定，主进程和共享 Runtime 保存并执行权限真值。

TUI 的本次验收重点是具体操作许可、恢复和角色边界；默认 TUI 尚无内置本地图片解码 Provider，不宣称其视觉 UI 或真实图像模型闭环已被验证。

## 7. 实施与验收记录（2026-10-11）

代码交付：[Peer-Agent PR #151](https://github.com/ly-ccx/Peer-Agent/pull/151)，追加提交 `09b51770323a5f2b73a9e600a331e35d8f669bcf`。前一提交的委托核验生命周期修复继续适用；本 ADR 补上图片正式授权与继承，并修正全局审计发现的通用操作复用问题。

### 契约与运行回归

- 三项越权用例在修复前实际失败：同一 toolCallId 改能力/参数/主体仍放行、一次文件批准扩大到另一文件、scope 缓存未隔离操作；修复后通过。
- 真实 `LocalImageProvider` 路径输出 PNG 模型侧带，确认主 Bot → 子执行者 → Verifier → ApprovalStore 压缩/重启后仍使用原授权 grantId。解码适配器为受控测试，不代表真实云模型理解质量。
- 不同 workspace/父 Bot/文件、文件身份变化、取消/暂停/被取代的计划、未授权普通 Goal、无审批者、过期、撤回、保存失败与解码期间撤回均拒绝。权限真值和像素来源仍由本地链提供。
- Desktop 同一操作显式 scope 复用与不同参数重新询问、宿主 Goal 确认桥限次与实际能力、并发回合权限上下文隔离均覆盖。
- TUI 覆盖具体操作、workspace/session 恢复隔离及 project_agent 角色在 chat mode 下的写闸；默认 TUI 无本地图像 Provider，视觉闭环不在此验收范围。
- 全仓 `pnpm test`：8,301 passed、5 skipped、0 failed、0 cancelled；Runtime 1,225、Desktop 5,503 + i18n 1、TUI 760。最终授权文案修改另通过 i18n 构建与测试。
- `pnpm build`、`pnpm typecheck`、`pnpm architecture:check`、UI 图标/圆角约束与 diff 检查通过。

初次全仓重跑暴露旧测试仍期待宽泛文件授权，已改为具体文件批准并追加不同文件重新询问断言；并发重建 dist 曾引起缺导出，单文件及稳定源码串行完整重跑后通过。未放宽权限闸或把失败记为预期通过。

### CI

[CI run 38112740621](https://github.com/ly-ccx/Peer-Agent/actions/runs/38112740621) 最终 Linux 与 macOS 均通过 build、typecheck、architecture、全仓测试和 Electron 冒烟。首次 macOS 失败发生在本次未改动的引用跳转场景：等待 `#bot-msg-rc-message-9500.is-anchored` 超过 15 秒，尚未进入图片授权卡场景。只重跑失败 job，未修改源码、放宽断言或跳过用例，第二次通过。首次 trace 中 Enter 操作耗时约 3 秒，而高亮存续 1.8 秒，提示瞬时状态观察的时序风险；这是调查推断，未据此宣称生产引用跳转根因已修复。

### 产品回归

正式产物包 `/tmp/peer-permission-product-v4`，`qa:product:capture` 与 `qa:product:verify` 均通过。Run ID：`d777c2df-d9d8-4667-821a-dfc6ab7eca16`；源码指纹：`da28c147c6c5e9c5bc23c51f14a881f559e87fa02657f3eeeb2302f9ab0fe7d9`。捕获期间代码文件稳定；main 场景启动时记录前一 Git HEAD，期间仅提交相同文件，后续独立场景记录当前提交，最终文件指纹校验通过。

AI 实施者实际检查全部 145 张必需截图，逐图记录观察；`independent=false`，没有称为独立审查。新增深色 1280 与浅色 760 图片授权卡明确区分“仅这一次 / 本轮允许此图片 / 拒绝”，显示具体路径、交给当前模型、当前机器人及任务、30 分钟有效期。机器交互使用生产 CardView → IPC → ApplicationService → ApprovalStore，键盘 Enter 签发资源授权，并确认另一排队写请求仍未批准。长路径在窄窗口换行，不产生横向溢出。

两项既有次要限制记录在 review.json：透明 Quick Chat 的离屏 PNG 无法证明原生浅色合成对比度；旧侧栏失败摘要仍可能带 response_ 技术前缀。均不改变本次图片权限真值或阻止授权动作。

覆盖为源码 Electron、隔离数据和受控模型。键盘与 reduced motion 场景通过，未覆盖完整读屏、真实 Provider 的网络时序、安装版 RC 或长期运行。用户日常源码、当前 RC12 与真实用户授权/任务数据未修改。

## 8. 活跃权限请求的完整生命周期（2026-10-11）

状态：Accepted。用户明确授权补齐权限卡展示、授权续跑、取消、超时，并要求真实看图调用验证。

### 8.1 已确认的根因

RC13 的主 Bot 读项目外图片时，PermissionGate 已追加 open 批准记录，但 Bot 收集式 TurnSink 没有窗口，Activity 又忽略 permission-request；ApprovalStore 写入不发布事实变化。LLM Chat Service 与 Desktop Bot Host 还分别创建了批准存储实例，仅给 Bot 存储加通知不能收到权限门的实时追加。界面因此无法及时取得权限卡，把等待用户误显示为正在查看图片。等待 Promise 无期限，单次读图可悬挂数小时。旧界面测试预先注入卡片，未覆盖真实调用到卡片的链路。

### 8.2 Module 与不变量

沿用 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。新增 PendingPermissionWait Module 管理宿主内活跃请求、截止时间、AbortSignal、唯一领取和清理；PermissionGate 负责策略、批准与资源继承，ApprovalStore 负责持久事实。Renderer 只提交决定。

- 每个请求在宿主登记后发布卡片事实变化和 Activity 的 awaiting_permission。工具段显示等待授权，不声称正在解码；授权恢复时回到工具执行。并发等待逐项管理，不因一项决定消除另一项等待。
- 默认等待期限为 5 分钟。期限只限制尚未获准的权限等待，不限制获准后的图片执行，不构成 30 分钟资源授权的续期。宿主测试可注入短期限和时钟。截止时间持久化为 deadlineAt；超时写 expired、decisionReason=permission_timeout。
- 允许一次或本轮此图片从同一请求继续实际读取，不重跑整个任务、不要求重复发送；只有获准后才解码像素。具体文件身份、取消、主体、资源授权与解码限制仍按 ADR 90/92 重检。
- 拒绝写 denied；卡片取消或停止所属回复写 cancelled；宿主无法呈现/保存请求时明确失败。每项决定只领取一次，清除计时器、AbortSignal 监听和待处理索引，发布 permission-settled；所有出口均携带结构化原因。
- 已过期、取消、停止或丢失现场请求的旧 open 卡不得签发许可。迟到和重复动作返回最新宿主事实，不覆盖终态，也不创建可继承授权。允许动作先领取活跃请求，再保存授权；保存失败不返回像素。重启的 stale 仍沿既有恢复路径，但已经超过 deadlineAt 的请求先变 expired。
- 保存批准事实后通知 Desktop 刷新相应 workspace，Bot 和经典会话均获得收口事件。后台子执行者使用同一批准日志和宿主权限门；不能依赖真实 BrowserWindow 才能发布等待。
- Desktop 在组合入口把 Bot Host 的 ApprovalStore 注入 LLM PermissionGate，使用一个实例发布落盘后的事实变化。沿现有 ConversationStore 保存、更新同一 cardId 的 system_card 展示回执；批准日志压缩后，历史卡也不得留下可点击的 open 外观。回执只表达宿主决定，不能签发权限或代替 ApprovalStore 真值。
- Provider 将权限取消和超时分别返回 cancelled / timeout ToolResult，Evidence 记录真实失败原因；失败不含视觉侧带。不把普通聊天同意推断为本地许可。

### 8.3 产品表达与验收

活跃图片卡显示具体文件、将像素交给当前模型、等待授权说明、允许一次、本轮此图片、拒绝、取消本次读取。超时和取消卡关闭动作并说明本次没有读取图片；需要重新发起时使用新的调用，不让旧按钮复活。

新增测试必须从真实 view_image Runtime Projection 调用产生请求，自动出现生产权限卡，经 UI → IPC → ApplicationService → PermissionGate 决定；确认实际 Desktop 图片解码器产出像素并进入模型视觉侧带。覆盖允许一次、本轮许可、拒绝、卡片取消、回复停止、超时、并发互不干扰、重复/晚到批准、落盘失败和重启过期。控制模型只用于提出调用和接收像素，不伪称真实云模型语义理解；已安装 RC 的长期运行另记覆盖限制。

标准产品截图包加入真实调用产生的授权等待、授权后结果、拒绝、取消和超时，实施者逐图审阅并 verify。禁止通过注入预制权限卡替代这条完整路径。

### 8.4 实施与真实调用验证

代码：Peer-Agent PR #156，提交 `05d04526`。新增 `PendingPermissionWait` 与 `ApprovalConversation`，在 Desktop 组合入口注入同一 ApprovalStore；协议扩展请求截止时间、取消与结束原因，Activity 表达 awaiting_permission。权限决定保存后才释放 Provider，停止回复也把结构化取消结果与 Evidence 引用送回原 TurnSink。

构建、全量测试、类型检查、架构 / SVG / 圆角检查与产品验收规则测试通过。工作区测试日志包含 7515 项通过（Desktop 主测试 5518 项通过，5 项显式跳过），升级与流式脚本测试也通过。权限、继承、批准存储和应用服务聚焦回归 74 项通过；工具与详情回归 24 项通过。覆盖并发等待隔离、超时领取竞争、读取 session 期间截止时间跨越、AbortSignal 监听清理、展示 / 落盘失败、重启过期与日志压缩后的历史回执。

隔离源码 Electron 实际执行生产 `view_image` Runtime Projection → ToolHost → PermissionGate → CardView / IPC → ApplicationService → PermissionGate → LocalImageProvider → Electron nativeImage 解码 → 视觉侧带。六个用例为允许一次、本轮图片授权、拒绝、卡片取消、停止回复与超时；均由真实调用自动产生卡片，未注入预制批准。成功用例校验实际 PNG 字节 SHA-256、1×1 尺寸、PermissionGrant 与 Evidence，本轮许可再次读取同一图片复用原 grantId；其余用例不返回像素，清空活跃等待，迟到的批准返回原终态。停止回复仍向生产 TurnSink 返回取消原因和 Evidence 引用。

超时界面测试注入 2.5 秒期限，宿主单元测试注入时钟，生产默认 5 分钟。模型调用意图由受控认知执行器提供，因此证明真实本地图片调用与原生解码，不证明云模型语义理解、网络时序或安装版 RC 已升级。数据与截图均在临时隔离目录，未修改用户真实任务或授权记录。

### 8.5 产品回归验收

标准 `qa:product:capture` 与 `qa:product:verify` 通过；包为 `/tmp/peer-image-permission-product-v2`，Run ID `4cb5be54-c016-436f-9ef4-9d50640a9aca`，源码提交 `05d04526961098641f44c1f5552625622f86636d`，文件指纹 `801d5b9c45ca5debdfb4c16bdd8dc0494391aa955c9f64c107dc39440cb99b56`。最终 Verify 于 `2026-10-11T15:37:06.208Z` 通过；机器回归无页面异常或授权事件异常。

实施者实际审阅全部 152 张必需截图，逐图记录具体观察，`independent=false`。新增 7 张真实请求截图覆盖深色宽窗 / 浅色窄窗等待、授权后续跑、拒绝、卡片取消、停止回复和超时；另以原尺寸检查这 7 张的路径、按钮、提示与关闭状态。长路径在窄窗完整换行，等待不再误显示为正在查看图片；授权后原调用继续，拒绝 / 取消 / 超时卡移除旧操作。另一项操作保持单独等待，未被当前图片授权一并批准。

同一包记录两个既有次要限制：透明 Quick Chat 离屏图无法证明原生浅色合成对比度；旧侧栏失败摘要仍带 `response_` 前缀。无未解决的阻断发现。键盘与 reduced motion 交互在机器回归覆盖，完整读屏、真实云模型与网络时序、日常安装版和长期运行未覆盖；不以源码包通过宣称安装的 RC13 已更新。

[CI run 38151003913](https://github.com/ly-ccx/Peer-Agent/actions/runs/38151003913) 的 macOS 与 Linux 均通过构建、类型检查、架构检查、全量测试及 Electron 冒烟；新增真实图片权限生命周期随标准 `--work-surfaces` 用例执行。


## 9. 完全授权遵循统一访问策略（2026-10-12）

状态：Accepted。用户明确指出逐张图片授权不可接受，要求完全授权。现场只读核对确认其已有 `settings.localAccessLevel = full_local`，本节在实现前修改 ADR92 的权限决策。

### 9.1 根因与纠正范围

Desktop PermissionGate 的通用本地能力请求器在 `full_local` 分支显式排除 `project_agent` 和 `agentKind=verifier`。另有 ProjectAgentPermission 包装器把权限门返回的 Full/session 自动许可改为拒绝，并在外部文本读取到达权限门前硬拒绝。文件及 Shell 权限门遵循 Full，主 Bot 的角色适配器与核验者例外却造成策略分叉；30 分钟资源授权仍只匹配同一真实文件。RC14 的请求展示、取消和超时补齐了等待生命周期，未消除这一访问策略冲突。用户界面已经选择完全授权，无须要求再批准每张图片。

### 9.2 权限策略与角色职责分开

- `full_local` 是用户已持久保存的本地授权策略，统一用于通过 Runtime Projection 和角色能力检查的本地调用。主 Bot、子执行 Agent、只读核验 Agent 及恢复回合不因角色名称被额外排除。
- Full 下项目内外的可用图片直接沿 PermissionGate 生成本次 Tool Call 的 PermissionGrant；多个文件、同一文件新调用、并行调用及重启后的调用无需逐图弹卡。用户继续保持 Full 时，不受逐图资源批准的 30 分钟期限限制。
- 自动生成的 grant 仍对应真实调用与结构化资源范围；grant 的 once 表示这次实际执行的凭据，不表示用户必须再次点击。不伪造 local_ui 批准记录，不把所有路径扩成图片缓存授权，也不把 renderer 状态作为权限真值。
- Role/Mode/Goal 决定能使用哪些能力及执行职责；LocalAccessLevel 决定这些已准入能力是否需要逐项审批。Full 不改变 Verifier 与主 Bot 的只读职责、明确的 objective probe/automation 策略、取消信号、计划执行准入与既有拒绝规则。这些条件沿原 Provider 链执行。
- 降为非 Full 后，新调用立即按当前策略处理；自动图片许可在文件读取前及像素返回前校验同一策略 epoch，降权后不能继续把尚未交出的像素返回模型。已执行副作用或已进入模型上下文的内容不能被撤回事实抹除。
- `ask_before_local` / `session_local` / `restricted_local` 继续保留需要批准的真实请求卡与 §8 的拒绝、取消、停止、超时闭环；一张图片的单次/本轮批准不会被误升级为 Full。只修正已开启的 Full，不静默把现有审慎配置改为 Full。

### 9.3 Module、存储与实现

复用现有 `settings.localAccessLevel` 真源、PermissionGate 自动许可分支、每次调用 grant 与 ImageProvider 的 validate 回调；移除 ProjectAgentPermission 对已准入只读调用的重复路径/自动批准否定包装，角色写闸仍在执行请求前，不增加 Bot 档案权限字段、存储目录、工具或审批旁路。Full 与读图资源审批共用 Provider → Manifest → Runtime Projection → Tool Call → PermissionGrant → Evidence。主进程依当前策略生成许可，ImageProvider 仍核对真实文件、取消、大小、类型及解码限制。

A 级权限决策；Desktop 门与 Provider 校验为 B 级实现，窗口回归与文案为 C 级。本次无需新的 Protocol 字段或 System Context Source，角色约束不变。

### 9.4 必须验证

1. 先复现已有 Full 下主 Bot / 无审批窗口 Verifier 项目外读图被拒绝。
2. Full 下连续读取至少四个不同项目外真实 PNG，验证像素 SHA-256、PermissionGrant 与 Evidence；没有权限等待、open 批准记录或逐图卡片。
3. 主 Bot、Worker、Verifier、恢复与重新初始化宿主均遵循已保存的 Full；同一图片变化后新的正常调用可重新读取，无旧资源批准期限造成的提示。
4. Non-Full 仍需授权；拒绝、取消、停止、超时与迟到批准闭环不退化。单次批准不授权其他图片。
5. Full 不能覆盖 objective probe、显式自动化许可、角色写闸和取消；实际读取过程中降权不返回未获准的像素。
6. 实际源码 Electron / HTTP Provider 调用验证多图无卡与设置重启读取，另跑受影响测试、构建、类型和架构门禁。新无卡场景进入标准产品包，逐图自审及 verify，并明确受控模型与日常安装版覆盖范围。

### 9.5 连续看图的切片恢复边界

正常 HTTP Provider 验证另外发现：主 Bot 每两轮主动让出执行片，当前 checkpoint 按要求去除本地图片像素；第 2 / 4 张刚读取、尚未发往模型的像素也被去除，恢复回合只有“需重新读取”的提示。这不属于授权拒绝，但会使成功读取与实际视觉准入不一致。

沿既有 LocalImageCheckpoint Module 增加受限的进程内继续上下文。Provider 发行的真实 observation 以本地 WeakMap 绑定模型图块，原权限 validate 闭包跟随发行证明。主动让出时仍只落盘无像素 checkpoint，加不含数据的随机恢复定位符；相同宿主内恢复按会话 / 项目 / 计划 / Provider / 模型身份及无像素消息指纹查找，验证原许可仍有效，才恢复已解码图块。模型文字、普通 JSON、复制的 observation 或 renderer 不能登记发行证明或构造可恢复上下文。

缓存有条目 / 字节总量与有效期上限，单次领取并清理，过期、降权、来源不匹配或进程重启均只保留无像素 checkpoint 与原重读提示。它不是新权限或跨进程授权存储，不让缓存定位符代替 PermissionGrant；新调用继续按当前 Gate 执行。四种 Provider loop 在同一 seam 创建 / 恢复继续上下文，持久保存始终不含本地像素。验证必须跨主 Bot 的真实主动让出边界，确认四张不同图片均实际进入 HTTP Provider 请求，并覆盖伪造、篡改、撤权、过期与重启。

### 9.6 实施与验收记录

代码 [Peer-Agent PR #159](https://github.com/ly-ccx/Peer-Agent/pull/159)，提交 `bf5dd64a`（统一 Full）与 `12deec9e`（继续上下文）。ADR 在对应实现前分别提交。已移除两处否定 Full 的角色例外，复用同一 PermissionGate；未更改用户已保存的权限级别、日常任务数据或安装 App。

先加入真实 Provider 测试得到 Full 下主 Bot / Verifier 拒绝的红灯（7 项中 4 项失败）；移除第一处角色例外后，原生 Electron Full 场景仍失败，从实际 projected executor 定位到第二处角色包装器。两处移除后权限、资源继承、生命周期、角色、objective probe 聚焦 57 项通过。继续上下文、实际 Provider 和视觉投影 23 项通过，验证普通 JSON / 复制 observation 无发行证明、跨会话 / 项目 / 计划 / Provider / 模型隔离、消息篡改、图块字节更换、撤权、过期、容量与 fresh-host 退回无像素状态。

正常源码 Electron 的 HTTP Provider 入口进一步复现主动切片丢图：四个真实 ToolResult 成功，模型只收到第 1 / 3 张。修复 LocalImageCheckpoint 后，在持久 `full_local` 设置下，初次运行与关闭再启动两轮各产生四个不同项目外 PNG 的原调用。共八个调用均有持久 Evidence；四种 PNG 字节 SHA-256 在两轮各自实际 HTTP 请求中全部出现，跨越主 Bot 每两轮主动让出的边界，没有逐图权限卡、权限等待或批准记录。HTTP 模型只控制调用意图及回包，使用正常编码、原生图片解码和 PermissionGate；没有注入成功 ToolResult 或预制授权。临时验证凭据已清理。

继续上下文缓存默认 5 分钟、16 条、128 MiB 上限，单次领取；其过期只影响缓存图块，Full 下新调用仍直接获准。缓存进程内发行证明不跨重启，重启测试是按已保存 Full 正常发起新读图，不声称旧图片字节被持久化恢复。

`pnpm build`、`typecheck`、`architecture:check` 和完整 `test` 均退出 0。标准产品包 `/tmp/peer-full-local-product` Capture / Verify 通过，Run ID `23d8f48c-7136-4102-9397-e69af11a643d`，源码 `12deec9e8021c8a1eb5f2b7ce3c269ba49241753`，指纹 `2b47719fd95f2ce607a0f19a89f6d7e765ea39aa0b204b09b551c97c8660de96`，Verify 时间 `2026-10-12T00:03:11.591Z`。实施者实际查看全部 154 张必需截图，逐图记录具体观察，`independent=false`。新增宽深 / 窄浅 Full 场景没有新增图片授权卡，已有另一项旧写入审批保持独立；原需要询问模式的允许、本轮图片许可、拒绝、卡片取消、停止、超时六个真实调用分支仍通过。

两项既有次要限制仍记录：透明 Quick Chat 离屏截图不能证明原生浅色合成对比度，另一机器人旧失败摘要仍可能带 `response_` 前缀。键盘和 reduced motion 在机器回归覆盖；完整读屏、真实云模型视觉语义质量、日常安装版与长期运行未覆盖。本次验收不声称 RC14 安装包已包含新代码。

CI 首次 [run 38185946323](https://github.com/ly-ccx/Peer-Agent/actions/runs/38185946323) 两平台构建、类型、架构和全量测试通过，界面回归失败。macOS 在新增读图之前可见搜索 p50 为 152.4ms（预算 150ms）；Linux 已通过 Full 四图和需要询问的六个图片生命周期，随后历史固定“今天”断言在 UTC 日期切换后只得到“昨天 / 最近 7 天 / 更早”。两条失败所在界面路径本次均未修改，已保存原始报告并复跑，未降低性能门槛。此记录不把本地产品 Verify 当成 CI 通过，复跑结论另补。


### 9.7 CI 复查：取消动作后的焦点时序（2026-10-15）

上一轮 run 38185946323 attempt 2 的 Linux 全部通过；macOS 构建、类型、架构和测试通过，Electron 在任务取消后返回焦点的断言超时。保留的失败截图及结构化状态已经显示“已取消”、取消按钮消失，失败发生在返回“任务列表”的键盘焦点，不是图片权限再次被拒绝。该失败阻止 PR #159 合并，因此 RC14 仍不含 §9 的修复。

旧表达实现只在成功回执后安排一次 requestAnimationFrame；如果这时 React 尚未移除按钮，或宿主先返回 stopping、稍后才发布 cancelled，它会直接放弃恢复焦点。新增真实 Electron 用例让成功回执先返回 stopping，500ms 后发布 cancelled；旧实现稳定复现同一焦点断言失败。C 级修复以 DOM 中动作实际卸载作为焦点恢复条件，同时等待成功回执；监听用户已主动移动的焦点并放弃自动归还，关闭详情时不把焦点移入背景。没有改动取消 IPC、权限或宿主状态真值。

提交 `c3f83936` 已推送同一 PR。聚焦原生窗口回归通过，覆盖失败重试、共享 pending、重复取消去重、无关任务保留、立即结束、延迟停止、窄窗口键盘返回以及用户主动移动焦点不被抢走。类型、架构和产品门禁测试通过；新版全量测试、标准产品包和两平台 CI 的最终结果另补，不将聚焦回归视作完整验收。


补充捕获诊断：完整标准回归在既有悬停入口测试两次超时；虚拟消息测量和抽屉退出后，一次性屏幕坐标不能证明 Chromium 已命中当前回复。测试提交 `21e82937` 在同一 15 秒动作期限内重新计算可见真实落点，并同时要求原生 `:hover` 和原按钮 opacity=1；隐藏、对齐、键盘打开及返回焦点断言保留，不强制显示按钮、不重试整段场景、不提高阈值。聚焦取消窗口再次通过；标准捕获从最终源码重新执行。
