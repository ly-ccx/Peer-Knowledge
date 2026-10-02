# 0.1.0 RC 开发者自测报告

最后更新：2026-10-02。状态：验收进行中，尚未宣布全部 Ready。

配套：[全面测试手册](acceptance-test-guide.md)、[RC 卡](rc-release.md)。正式版由负责人全面测试和七天日用后决定；本报告不代替负责人签收。

## 交付版本

候选 `0.1.0-rc.2` 已预发布：[下载页](https://github.com/ly-ccx/Peer-Agent/releases/tag/v0.1.0-rc.2)。不可变提交 `be65fb73ce672f87a144a68ed5a1622f5d632ae8`，Release36960577284全部成功、14项资产；SHA见[手册](acceptance-test-guide.md)。npm rc=0.1.0-rc.2，latest=0.0.18、beta=0.1.0-beta.5。RC1历史版本与失败证据保持不变，正式0.1.0未发布。

**当前验收：** rc.2包含PR99–103，最终两平台CI与本机全部门禁、20项矩阵、9壳/11可访问性/7诊断通过。实际macOS信任、六次安装轮换、归档CLI与npm默认助手读文件/回复通过。安装双任务首轮与恢复失败均保留：A通过answer恢复，B没有达到实际完成标准，被独立核验拒绝；未签收/合回。Astra重跑两文件及新鲜证据正确，A仍被核验拒绝：要求的计划拆分未达成，且已发生的本地批准历史未投影。未签收/合回，批准事实PR105已合入6bdbaf8c并通过两平台CI；源码Luna代理＋冻结Astra任务/核验的同夹具恢复全流程通过，首轮Astra空响应保留。新安装候选待复验。多入口限定范围已通过。GPT61经典low/default通过，机器人真实空响应未解决。整体尚未Ready，GA等负责人全面测试、七天日用及批准。

## 已有证据与适用范围

| 检查 | 结果 | 证据与边界 |
|---|---|---|
| RC01 规模与真实性能 | 通过 | [RC01 完整记录](rc-01-performance.md)。200机器人、10000消息、100000事件、10000记忆，8项预算通过；干净源 Electron 的9项壳检查通过。真实GLM五回合中位5598.32ms，真实工具回复；不是安装包测试。 |
| RC02 中英文、键盘、焦点、动效 | 本机及最终两平台CI通过 | 干净源1909c38f列表14.12ms、搜索22.40ms、Received48.90ms，9项壳/10项可访问性检查通过；新鲜任务批量投影105项focused测试通过。[窗口报告](evidence/rc02-task-batch-clean-window-20261002.json)。50条记忆分页、减少动效、中文英文、设置持久化与实际颜色对比检查通过。最终候选CI见下方绑定记录。 |
| RC03 诊断 | 本机及最终两平台CI通过 | 严格IPC调用方与载荷、逐字段脱敏、边界数量、原子写入/取消/失败、损坏registry只读测试；最终候选200机器人窗口导出93312字节，7项诊断检查通过。保存位置由夹具控制，系统保存对话框的手动交互留给负责人。 |
| RC04 跨版本矩阵 | 20项（RC2）及最终两平台CI通过 | 真正执行不可变0.0.18及Beta1–5源码；升级、逐版、实际SIGKILL恢复、降级读回和再升级、备份失败、六版用户毕业正式通道、显式beta与回退。自动更新网络/时钟受控；不宣称未发布的GA已实际安装。另有RC2六次真实macOS安装版轮换证据。 |
| RC05 完整构建与回归 | 本机门禁及最终两平台CI通过 | Desktop5294项中5289通过、原有5项跳过，独立AST1项及runtime-node1006项通过；其他包和20项矩阵通过。未发布GA草案从changelog排除并有测试，两个README和真实源截图。示意对话不作为真实模型证据。 |
| 候选签名、公证、安装 | RC2 macOS信任、安装轮换及npm安装通过 | 本次RC下载SHA与资产digest相符；ZIP/.app与DMG内.app签名、公证、Gatekeeper通过；实际六次版本轮换通过；npm安装CLI二进制及助手与发布归档逐文件SHA相同。Windows/Linux交互安装尚未执行。 |
| 候选复杂任务与多入口 | RC2多入口限定范围通过；严格安装复杂任务失败待修复 | 真实归档/npm默认CLI助手通过。实际Desktop＋源码TUI后端＋本机远程夹具多入口通过，范围明确。RC2双任务三轮原失败保留；默认Astra两文件及新鲜证据正确，但计划拆分和批准历史核验失败，未签收/合回。 |
| 设置页补修 | 本机源码及两平台CI通过、PR99已合入 | 外观/工作方式/模型分工、折叠运行与全局、Switch与SVG、固定页签及窄抽屉。9壳/11可访问性/7诊断通过，8项滑块对比度最低6.035:1，实际保存读回与原预算通过。详见[补修卡与截图](rc-settings-polish.md)；尚未更新安装应用。 |
| 机器人侧栏更新入口 | 本机通过、PR106待CI | 恢复版本、更新状态及自动/Beta/正式通道；“更新与关于”修改后底部同步。5组updater、9壳/11可访问性/7诊断与完整桌面回归通过。详见[补修卡](rc-bot-update-entry.md)；阶段事件仅验证表达，未下载/安装新资产。 |

较早文档阶段干净 `005a5abb` 的实际源窗口9项壳、10项可访问性和7项诊断检查全部通过，0页面错误，owned进程退出。列表16.82ms、可见搜索24.80ms、Received48.50ms；200机器人诊断93312字节。见[原始报告](evidence/rc05-final-source-window-20261002.json)。与完整本机门禁通过的 `ce5bb7e4` 生产代码相同，仅同步真实滚轮smoke；desktop 5287项中5282通过、原有5项跳过（2项Electron opt-in已另跑、3项完成计划不适用的文本Verifier顺序检查），独立AST测试1项通过，其他包和19项矩阵通过，没有新增skip。

## 手册分组与自测方式

机器人侧栏版本与升级入口缺失已真实复现，恢复后又复现两个渠道设置入口显示不同步，已补齐主进程确认快照的同窗口分发。源码 `6360c403` 的[实际窗口](evidence/rc-bot-update-local-window-passed-20261002.json)和[本机门禁](evidence/rc-bot-update-local-gates-20261002.json)通过；两平台CI待返回，仍未进入已发布RC2。负责人手册L11补入口、键盘、窄布局、跨入口/重启持久化与真实安装检查，仍为195个唯一用例。当前用户安装版为Beta5，原应用未替换；“我→设置→更新与关于”仍可管理更新渠道。

“自动化通过”只覆盖测试中实际断言的契约。下面分组不是把195个手工用例逐项预填Pass；负责人仍填写每项实际结果。

| 手册分组 | 开发者覆盖 | 负责人补验 |
|---|---|---|
| A 安装/首次启动 | 首启、配置、宿主生命周期契约；本次macOS签名包启动/轮换、npm安装通过 | Windows/Linux交互安装；本机系统对话框、首次配置真实凭据 |
| B 新建/身份/头像 | 稳定身份、迁移、独立profile、头像颜色/上传/归档契约和原生窗口 | 真实文件夹绑定、上传自己的图、删除确认与系统废纸篓 |
| C 列表/搜索/入口 | 200机器人和完整消息语料、SVG、键盘、可见结果/回执预算、Quick Chat | 使用自己的项目和系统快捷键；托盘与通知实际体验 |
| D 对话/引用/持久性 | canonical输入去重、归属、越界拒绝、10000消息分页/跨页引用/回最新 | 自然语言插话和不同模型恢复质量 |
| E 任务 | 真实工具通路、只读限制、计划与成功标准、任务状态；源码实际双写通过，RC安装复杂任务复验中 | 实际项目输出质量与成功标准逐项核对 |
| F 批准/签收 | PermissionGrant、拒绝、过期、来源、核验/签收区分及幂等测试 | 每张卡的可读性，拒绝/批准后的真实操作 |
| G 并行/隔离/恢复 | scheduler槽位、优先级、依赖、失败卡、worktree、合回/冲突、取代/恢复、真实崩溃恢复；源码双写/核验/签收/授权合回通过 | 三真实项目并行、故意冲突后的决定；RC安装写任务复验中 |
| H 记忆 | 来源/有效性/冲突、开关、检索、跨项目隔离、50条分页与导出契约 | 自然语言学习质量、重启后真实模型检索、修改实际来源文件 |
| I 模型分工/用量 | route冻结、fallback、严格编码、硬门限、快/慢档与用量事实测试 | 自己的订阅与渠道、真实视觉复核；不可用条件标Blocked |
| J 目标 | 权限来源、autonomy、探测/去重/暂停/恢复/熔断、实际Goal绑定测试 | 实际CI账号、生产仓库事件与自然语言目标质量 |
| K 后台/主动性 | host/lease、关窗、quiet、背景停止TCP13项及计时/去重测试 | 系统睡眠/唤醒、电源变化、通知权限和七天使用 |
| L 历史/经典/升级 | native窗口经典切换、旧历史；19项真实tag矩阵；本次macOS五次实际安装轮换通过 | 完整备份后个人数据抽样；Windows/Linux安装轮换 |
| M TUI | 同runtime/lease/队列、来源隔离；实际安装CLI版本/绑定/帮助/列表/输入/退出通过，真实模型请求受阻 | 自己的终端、尺寸、输入法、实际工作流 |
| N 远程 | HTTP/WS、设备签名、角色/allowlist、去重、desktop-only批准、受控离线及窄布局 | 真实手机、生产OIDC/account、真实外网/电脑睡眠/网络切换 |
| O 诊断/性能 | 规模预算、allowlist脱敏、只读损坏状态、严格IPC；保存失败保留旧文件 | 实际系统保存/取消/覆盖，慢机器、未知旧回合显示 |
| P 既有能力 | 全量包测试与架构门禁覆盖既有MCP/Skill/工具/附件/上下文/Evidence | 自己的外部MCP、插件、浏览器和视觉渠道配置 |

## 失败、修复与重跑记录

保留失败，不只保留最后一轮绿色结果。完整RC01失败历史在其实施卡与evidence目录。

- RC02首次CI列表122.69ms超过100ms；同提交复跑搜索157ms超过150ms。阶段记录显示文件戳重复读取profile，已复用同次新鲜catalog，外部写入刷新测试通过。本机干净重跑列表16.81ms、可见搜索24.60ms、Received49.00ms；后续新鲜任务批量投影修复及最终两平台CI通过，预算未改。[复跑失败](evidence/rc02-ci-search-retry-failed-20261002.json)。
- RC02窗口初次发现10000记忆一次渲染阻塞和摘要/时间对比不足，已补50条分页及语义文字tokens，旧完整导出和操作入口保留；夹具标签/窄布局定位错误单列。
- RC03真实导出发现registry读取会在损坏时修复落盘，新增纯诊断快照；破损字节和目录内容不变测试通过。初次集成夹具缺inbox字段及红测试失败保留。
- RC04前几次夹具使用错误automationId/role、旧版workspace端口与共享catalog校验方式，已按实际tag接口修正；原实体文件逐份SHA与旧行前缀保留，没有删除断言。最终19项干净源通过。
- 已发布Beta5安装复杂spawn_session失败曾暴露Responses隐式strict问题；PR92已修复并有真实源重复验证。本次RC安装必须重验，不把源修复等同旧包通过。

## 尚需的真实环境

这些条件不能用mock宣布通过：Windows/Linux交互安装、实体手机、生产OIDC/CI账号、所有用户渠道、真实视觉核验、系统睡眠/唤醒与连续七天使用。具备条件的macOS安装和真实模型/多入口由开发者先跑完，环境相关项在负责人手册中留有明确步骤；缺失项写Blocked和原因。

## Ready 判定与正式发布门禁

开发者候选交付必须具备：最终干净提交全部门禁、两平台CI、20项当前候选矩阵、native窗口检查、签名公证校验、实际安装Desktop和CLI、真实复杂任务与多入口证据；已发现P0/P1清零，未验证范围明确列出。任一项缺失，报告状态保持进行中。

负责人随后完成195项手册和六条流程，至少三个真实项目、一个受管机器人、TUI/远程各一次、七天日用。P0/P1为零并明确授权，才将开发线合入main、移除GA草案标记、发0.1.0和npm latest。任何RC修复都绑定新提交；已发布候选tag不移动，需重新出rc.N+1并注明回归范围。

测试手册已核对195个唯一用例编号、6条端到端流程及所引用本地文件；项目A准备命令实际执行、基线测试1项通过、初始Git提交后状态干净。[文档验证记录](evidence/rc-guide-validation-20261002.json)。


### 任务执行角色补修与最终回归

真实Luna首轮双写进入两个已批准worktree，但模型将父对话编排指令重复用于执行角色，停在waiting_user。原文件未写、失败完整保留为[首轮证明](evidence/rc-work-session-context-first-failed-20261002.json)。按[Accepted架构补修](rc-fix-work-session-context.md)增加静态执行角色和当前真实GoalPlan准入phase，父正文仍为L7；不放宽工具权限或签收。源码同样双写输入已复验通过，安装候选仍须独立执行。

本机29d43dec干净版本（与38eb6f95生产树相同，后者仅补依赖merge祖先）完整build/typecheck/architecture/test/release-readiness通过：Desktop5288项中5283通过、原有5项跳过（2项Electron opt-in已另跑、3项完成计划不适用的文本Verifier顺序检查），加独立AST1项通过；runtime-node997项通过；系统上下文、TUI和其他包通过，19项真实tag升级矩阵通过。最终两平台CI通过，安装版真实模型复验未完成，继续保持进行中。


### 候选源码和CI绑定

全部代码卡PR94/95/96/98/97均已合入开发线。候选tag v0.1.0-rc.1 → 0beeb21f，原生/真实模型源码验收29d43dec；CI36918216680实际checkout GitHub临时merge6c04239c。三者Git tree均为1204b3eb1c57a29caa6f3af975c4d0e5fdef86b8，已用Git/GitHub对象核对，生产内容一致。证据[绑定](evidence/rc-candidate-source-binding-20261002.json)、[macOS CI](evidence/rc-candidate-ci-mac-20261002.json)、[Linux CI](evidence/rc-candidate-ci-linux-20261002.json)。Mac列表52.58ms/搜索95.50ms/Received196.60ms；Linux30.51/69.60/137.80ms，全部在原预算。

原有skip边界：两个需PEER_BACKGROUND_UI_SMOKE的真实Electron用例已在13项独立后台回归中执行通过；三个已完成计划复用场景没有后续文本Verifier阶段，顺序断言不适用；ADR42旧双口径describe已由ADR52统一投影取代。不能将这5项统称opt-in，也没有新增skip。完整源码双任务与多入口已通过（见[复杂任务](evidence/rc-source-complex-passed-20261002.json)、[多入口](evidence/rc-source-multi-entry-passed-20261002.json)），Release36919331979全部成功，候选已发布。签收后的独立合回授权步骤已修正进测试脚本；先前夹具遗漏已保留，未修改生产授权门。


### 首次安装CLI真实凭据测试受阻

实际Release构建CLI归档SHA256 a68778c9…5947 与发布资产digest相同，100×30 PTY版本/新目录Y绑定/帮助/机器人列表/持久输入与可见Received/Ctrl-C退出0通过。真实模型未执行工具：报“The credential helper timed out”。电脑工具另外确认当前Mac锁屏且自动解锁失败，已请求负责人手动解锁；是否钥匙串等待所致需同安装助手复验，不能先宣布根因或通过。证明[首轮](evidence/rc-installed-cli-locked-first-20261002.json)。仅本轮凭据副本已清除，项目README未改。源码后端多入口Pass仍不能替代这个安装CLI检查。

### 实际安装轮换

本次发布RC1的真实macOS应用已完成 `0.0.18 → beta.5 → rc.1 → 0.0.18 → rc.1` 五次实际客户端启动、窗口及生产API检查，全部通过、0页面错误，每个owned进程均退出。使用真实v0.0.18源模块生成旧数据，旧conversation/Goal/automation实体逐文件SHA未变，新增canonical输入原行未改，再升级workspaceId相同。[完整证据](evidence/rc-installed-upgrade-passed-20261002.json)。这轮不配置模型、不复制凭据，因此没有验证真实模型与钥匙串，也不代替Windows/Linux实际安装。

下载ZIP/DMG/CLI SHA与GitHub资产digest相符。应用codesign严格及深层验证、Team82672N97RP、.app stapled ticket、spctl Notarized Developer ID均通过。DMG自身没有单独staple票据（校验返回65）；产品配置是在公证并staple.app之后包装ZIP/DMG，不把.app通过写为DMG自身票据通过。DMG完整性验证通过，已只读挂载并独立校验内部.app，挂载已退出。[资产与信任记录](evidence/rc-release-assets-trust-20261002.json)。

### 实际npm安装

npm发布日志UTC20:15:23显示RC1发布成功，最初本机注册表返回E404/ETARGET；没有重新发布。UTC20:19:27元数据已可读，随后在隔离prefix实际安装成功，`peer --version`为`peer 0.1.0-rc.1`；postinstall取得的`peer`与默认同目录`peer-credential-helper`，逐文件SHA256与本次发布CLI归档相同。四个公开包protocol/runtime-core/runtime-sdk/cli的`version`与`rc`均为RC1，`latest`仍为0.0.18、`beta`仍为beta.5。[完整安装证明](evidence/rc-installed-npm-passed-20261002.json)、[四包注册表证明](evidence/rc-npm-four-packages-20261002.json)。此项证明npm实际安装与版本，不代替真实模型/钥匙串测试；安装CLI仍需解锁后复验。


### 等待任务回答恢复补修

见[补修卡](rc-session-answer-resume.md)、[修复前真实失败](evidence/rc-session-answer-real-failed-20261002.json)、[限定恢复证明](evidence/rc-session-answer-recovery-scoped-20261002.json)。等待answer恢复、真实Bash字节检查、TaskRunner核验、人工签收与单独合回已实际执行；严格双独立Verifier和新来源汇报仍需新夹具/新安装候选复验。PR102 Mac CI首轮工具evaluate异常已按同提交重跑一次通过，Linux首轮通过；已合入fca715e8。GPT-6.1 Sol目录兼容另卡实施，真实订阅请求进行中。所有这些源码/装配证明不代替rc.2实际下载包。


### rc.2候选与严格复杂流程

设置/CLI助手/命令快照/回答恢复/新模型目录PR99–103已全部合入。rc.2版本源码b1cae373完整build/typecheck/architecture/test、版本/changelog/readiness通过；20项矩阵保留旧19项及六版真实tag来源，增加rc.2更新毕业行。最终两平台CI/native源窗口进行中，未发布/未宣布Ready。

[严格源码流程](evidence/rc-source-strict-complex-validated-20261002.json)实际达到两次独立核验、本轮来源回复、用户签收和独立授权合回，含一次真实用户回答/Retry。原脚本末尾误用历史格式失败已保留，实际segments/bash收据post-validation通过；安装候选重新跑已修正的断言。GPT-6.1 Sol目录已通过两平台CI并合入，但真实首轮和显式Retry均空响应，账号可用仍未通过，两个语言发布说明披露；不得把目录项等同真实工具可用。


GPT61最新范围更正：经典入口low与default均真实工具读回通过，故账号/模型通用可用不是阻塞结论；失败目前局限于先前机器人代理请求，机器人自然输入正在复验，真实旧失败保留。不能用经典通过替代bot post_reply通过。


### rc.2最终候选与新模型范围

设置页PR99、同次签名CLI助手PR100、命令快照PR101、等待answer恢复PR102与GPT-6.1 Sol目录PR103均已通过两平台CI并合入。rc.2候选PR104最终两平台CI36960002970通过，tag v0.1.0-rc.2固定到be65fb73ce672f87a144a68ed5a1622f5d632ae8，Release36960577284构建中。20项升级矩阵及完整源码门禁、9壳/11可访问性/7诊断通过；严格源码双写保留真实用户回答与一次重试，两任务独立核验、签收和单独授权合回通过。经典GPT61 low/default实际读文件回复通过；机器人同模型仍空响应，摘要请求也失败，尚无已确认根因。新安装包默认CLI、复杂任务与多入口待复验，尚未Ready；GA仍等负责人全面测试、七天日用和明确批准。 [CI绑定](evidence/rc2-candidate-ci-binding-20261002.json)、[GPT61摘要失败](evidence/rc-gpt61-bot-summary-failed-20261002.json)。源码与交付merge Git tree均e2874486c28826ca378c8c64d814e4115b4b19fc。仅变更生成清单时间戳的未提交漂移已恢复，摘要测试原始sourceDirty=true仍如实保留，不伪称干净。


### rc.2实际安装检查

[发布记录](evidence/rc2-published-release-20261002.json)、[macOS信任](evidence/rc2-installed-trust-passed-20261002.json)、[六次安装轮换](evidence/rc2-installed-upgrade-passed-20261002.json)通过。归档CLI和npm shim均用默认同次签名助手，实际读取README、post_reply、canonical回复与退出0通过：[CLI](evidence/rc2-installed-cli-passed-20261002.json)、[npm](evidence/rc2-installed-npm-cli-passed-20261002.json)。PEER_AGENT_HOME隔离正确，测试凭据副本已清除，原用户应用未替换。首次npm ETARGET为注册表短暂同步延迟，随后固定版本安装成功。

首轮双任务及一次恢复失败均保留。A误读批准后，通过实际answer恢复并独立核验通过；B只完成初始检查，未满足改动标准，最终独立核验failed，未签收/合回。不能把执行状态completed计为任务目标通过。默认Astra重验仍失败：两文件及新鲜证据正确，但A没有按要求拆出编辑/检查任务，核验上下文也缺实际本地批准历史；保持失败且未签收/合回。[失败](evidence/rc2-installed-complex-astra-failed-20261002.json)、[实际批准诊断](evidence/rc2-local-plan-approval-diagnostic-20261002.json)。已Accepted批准事实补修卡，不能将修复代码或文件正确代替完整验收。GPT61实际准备请求观察确认当前user输入、25工具（含read_file/post_reply）及medium思考档；该观察在网络前中止，不能作实际模型通过：[观察范围](evidence/rc-gpt61-request-observed-20261002.json)。


rc.2 multi-entry [actual proof](evidence/rc2-installed-multi-entry-passed-20261002.json) passed: installed Desktop uses default signed helper; source TUI backend client/takeover uses candidate signed helper explicitly; production HTTP/WS adapter and loopback fixture Ed25519 identity. Genuine read_file and canonical replies on all three surfaces, duplicate input rejection, remote approval summary only, Desktop quit -> TUI lease/tool/reply passed. This does not certify a physical phone, production OIDC or installed CLI UI; archive and npm CLI UI are separately verified above. Owned processes exited and credential copies removed.

### RC2之后：批准历史补修

PR105已于04:25:13Z合入6bdbaf8c，CI36963764691两平台SUCCESS；源码/CI/合入tree69ae6585一致。[本机门禁](evidence/rc-local-approval-source-gates-20261002.json)：focused119＋TUI host10，完整build/typecheck/architecture/test通过；Desktop5297中5292通过/原5skip＋AST1、runtime1012、TUI753、system-context35。两平台9壳/11可访问性/7诊断、原性能预算和owned退出通过，见[CI绑定](evidence/rc-local-approval-ci-binding-20261002.json)。既有GoalApproval按实际本地决定冻结，Source只准入批准事实，不是工具Evidence或签收。

[首轮真实源码](evidence/rc-local-approval-source-first-failed-20261002.json)两任务及最终独立核验通过，但Astra项目代理真实空响应使本轮来源汇报缺失，保持全流程失败。[同夹具恢复](evidence/rc-local-approval-source-recovery-passed-20261002.json)仅将项目代理配置换为Luna，已冻结worker/verifier仍Astra：重新独立核验、当前canonical两来源汇报、用户签收、单独授权合回均通过；原项目仅a/b精确变化，原用户默认未变，凭据副本清除。不能记为全Astra首次无干预或安装包通过。新候选须实际安装复验，GPT61机器人空响应未解决；总体尚未Ready，正式版继续等待负责人全面测试与批准。
