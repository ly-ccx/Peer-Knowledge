# Peer UI、动效与过渡体系覆盖表

创建时间：2026-10-23
最后更新：2026-10-24

> 状态：规范到存量实现的映射；纳入[当前改造计划](peer-product-renovation-plan.md) E15/UI、E16/动效、E17/过渡，发布证据统一归 E13。
> 组件与页面逐项登记见[全产品交互矩阵](peer-interaction-standardization-matrix.md)。本文不另立视觉数值、运动常数、组件库或验收账本。

## 基础交互点查补充（2026-10-24）

用户授权提前点查，代码 `a0ae1a33` / [PR213](https://github.com/ly-ccx/Peer-Agent/pull/213)；[路径与限制](../../playbook/v0.1.0/experience-ui-motion-transitions.md#用户授权的基础交互点查2026-10-24)。C 级渲染身份和入口修复，没有新增动效常数、组件体系或运行时边界。

| 体系 | 本次实际确认 | 保留覆盖 |
|---|---|---|
| UI · U06/U08/U10/U11/U13/U15 | 修复消息/输入框重复 key 的内容叠影；12 个设置分区、五个档案标签、任务/Evidence、搜索、菜单和新建取消可操作；自动化新建到编辑器 | 未作全主题/200%/读屏/布局验收；真实写入/失败仍依各行 V |
| 动效 · M01/M02/M04/M18 | 本机真实浏览器 request/cancel 首帧与退出用例通过；实际菜单/浮层/抽屉打开关闭完成，无再次崩溃 | 未切换减少动效、透明度或注入 WAAPI 异常；G11/G12 全覆盖仍待 E13，不能以正常开关替代降级验证 |
| 过渡 · T01/T02/T06/T08/T09 | 页面往返保留本 bot 草稿和阅读模式；回最新只有单个入口；抽屉 Escape、模型/权限菜单及附件取消、Evidence 返回原入口；dirty 设置继续/舍弃 | 未验证跨 bot/窗口/真实 IME/未知回执，崩溃页恢复未重演；正常开发窗口重载能恢复首屏并重开对话 |

三项针对性检查通过；无独立评审或发布验收。下文“未运行”为当批历史记录，本次只补充明确列出的路径，其他 U/M/T 覆盖不升级。

## E15–E17 本轮更新（2026-10-24）

代码 `7f38f121c7bff5859e54ea98b25d315e07ad3cc8`；[PR212](https://github.com/ly-ccx/Peer-Agent/pull/212)（draft，叠加 PR211）、[实施交接](../../playbook/v0.1.0/experience-ui-motion-transitions.md)。**本批消费者实现已审阅，候选验证待发布**。起点 `ec1de36b01d844497ea9ad663bc2e2b03bcfa0d9`，知识父提交 `572f153f3b3bd68b2e1f0a6fd0111b943f9f3b96`；两仓分支 `codex/experience-ui-motion-transitions`。只提交隔离分支的本批文件，未混入主工作区 dirty，也未合并 GitHub PR。

| 体系 / 编号 | 本批实现 | 发布前责任 |
|---|---|---|
| UI · U01/U03/U05–U12/U14–U16 | C210 ChoiceStrip 复用实际 tabs/radio 消费者；C211 文件新建保护 IME/显式提交/失焦保留；能力/Skills/MCP 读失败/未知数量/逐项回执/敏感编辑保护；原生远程控件作 Frost 角色适配 | 211 个 TSX 是登记数量，不是符合率；真实键盘/读屏/200%/长名/触控/对比度、未知/部分写入、其他消费者逐行 V |
| 动效 · M01–M06/M08/M12/M14/M15/M18 | G11 采样/帧前置偏好、可取消捕获/隐藏停帧与失败保真源；G12 共享 WAAPI/静态收尾。motionEnvironment/visualMotion 承接 Overlay/presence/disclosure/问题/档案/FLIP/塌缩；头像/思考球/流式显示停止无意义 JS 工作 | ready/finished 拒绝/无事件/无 API/卸载/快速反向、实际离屏和真源；其余 CSS 循环仍按 M08/M17/M18 核对，装饰增强归 E14 |
| 过渡 · T01/T02/T04–T09 | MCP dirty 离开保当前敏感表单；问题只交还已有焦点；rail 重开取消旧退出；文件原 scope 回执/失败留名/条件归焦；经典授权立即派发原回调，查找/定位静态完成 | 跨列 remount 焦点未改成保 DOM，完整树键盘/原生窗口/实际 IME 和旧宿主的部分写入仍 V；业务执行/许可/签收不由退场决定 |

流式显示泵的文本批次为 B 级影响：只交出已收到文本并保留顺序，不新增请求/合成正文；其余是 C 级表达。没有新增协议、IPC、存储、权限、Evidence、触发器或 Context Source。新增 C210/ChoiceStrip、C211/FileEntryInput，实际 Desktop 非测试 TSX **211**、TUI **13**。只做内容/diff 自审；边界用例已补写/调整但均未运行，测试、build/type/architecture/IPC、截图及交互回归留到 E13 最终合并候选。不是独立评审或发布 Pass。

Gateway 是已有 standalone host adapter：复用其 palette，并显式映射 8/12/16 几何、普通/紧凑高度、字号、focus 和现有 fast/easing；原生表单/强制颜色/粗指针负责宿主降级。它不能导入 renderer CSS，不宣称已经自动共享主题或全部视觉通过。退出条件是最终候选对照角色/主题/对比度；若后续需要自动分发 token，另按实际构建边界处理，不在本批添加第二套系统。

本地联调补修（2026-10-24）：用户点击机器人触发 `Illegal invocation`。代码 `ed0f81b4` / [集成 PR213](https://github.com/ly-ccx/Peer-Agent/pull/213) 已将 E05 `useConversationWindow` 的 request/cancel 包装为显式 `Window` 调用，保留原同帧调度、阅读意图与取消策略。C 级 UI 接线；新增真实 hook+有 receiver 约束的用例，未运行。仅确认重启该开发实例后可打开同一机器人、历史与输入框可见；未发消息或操作原任务，不等于全量回归。崩溃页原重载未恢复，采用重启恢复，reload 机制仍待 E12/E13 核对。 对应 U10/M18/T01/T08 的原生帧接线，未调整任何动效数值或批量升级覆盖状态。

## E11–E12 前一批更新（2026-10-24）

代码 `ec1de36b01d844497ea9ad663bc2e2b03bcfa0d9`；[PR211](https://github.com/ly-ccx/Peer-Agent/pull/211)（draft，叠加 PR210）、[实施交接](../../playbook/v0.1.0/experience-entry-recovery.md)。**当前路径实现已审阅，候选验证待发布**。PR198 `86eb3fbb` 通过真实分支 merge 保留原提交身份；未合并 GitHub PR 或复制原工作区 dirty。无新增 TSX，实际 Desktop 209、TUI 13。

| 体系 / 编号 | 本批实现 | 发布前责任 |
|---|---|---|
| UI · U05/U06/U10/U11/U12/U15/U16 | 终端 Tab 卡片焦点/原卡 ID/回编辑；远程真实读写回执、草稿/IME、loading/错误/重读、按 ID 稳定消息与列表；Desktop bootstrap 失败恢复，长历史有界分批 | 真实 terminal/软键盘/读屏/200%/移动、旧对象/撤权/失败；远程仍原生表单/现有样式映射，不引新系统，也不假称所有 token 已共享 |
| 动效 · M09/M13 | G10 的固定 2200ms 门禁删除；品牌只表达真实启动，session 就绪即进入。沿现有 reduce 与静态反馈；远程/终端新增状态不加装饰循环，阅读恢复不用 smooth | 冷启耗时/减少动效/原生窗口待 E13；G11/G12 的 JS/WAAPI 降级仍 E16，不批量标达标 |
| 过渡 · T01/T06/T08/T10 | TUI 保存成功后才关闭/卸载/切换，失败留原编辑；远程按 bot/session 保草稿和读位，旧请求不跨关闭/换 bot/退出/页面恢复，原 inputId 回执；Desktop 四页追读暂停继续，远程单页缺口保持明确 | 多批/中断/重试/未知送达/晚回执/终端退出、主题/升级/备份恢复仍候选取证；来源/目标/焦点与事实各有责任，不重放未知执行 |

当前实现已做内容/diff 自审，非独立评审；补写/更新边界用例但均未运行，没有测试、build/type/architecture/IPC、截图或交互回归。真实验证统一归最终合并候选的 E13。

## E09–E10 前一批更新（2026-10-23）

代码 `df25f859b71025a2173096d6a0bdda0c1fdfa4ee`；[PR210](https://github.com/ly-ccx/Peer-Agent/pull/210)（draft，基于 PR209）、[实施交接](../../playbook/v0.1.0/experience-previews-controls.md)。**当前路径实现已审阅，候选验证待发布**。新增 C207/ResourceFeedback、C208/ResourceEditor、C209/EvidencePreview，实际 Desktop 非测试 TSX 209、TUI 13；原主工作区其他未提交内容未进入交付。

U05/U06/U10/U11/U13–U16：附件/引用/产物/Evidence 受控预览与真实读取/失败恢复，记忆/目标/自动化会话草稿、逐对象写回执和版本核对。M01/M02/M04/M16 沿既有按钮/Overlay/Drawer/motion，复制反馈不靠倒计时维持，图片未解码不开放原尺寸；本批没有新增动画常数或物理系统。T01/T02/T08/T09：引用定位有界且手势可打断，来源失效保引用；嵌套 Evidence 按原层级关闭/归焦，失败预览可重读；记忆修订关闭旧编辑并恢复焦点，后台刷新不重置提案展开或重复目标定位。

G08/G09 的上述实现已审阅；G10–G12、真实系统/读屏/200%/reduce 与其他存量继续各行 V。新 kernel 用例未运行；没有 build/type/architecture/IPC、截图或交互回归、独立评审或发布验收。

## E07–E08 前一批更新（2026-10-23）

代码 `815ab1363143788aab3c672e850db96cb7685e45`；[PR209](https://github.com/ly-ccx/Peer-Agent/pull/209)、[实施交接](../../playbook/v0.1.0/experience-settings-closure.md)。**本批消费者实现已审阅，候选验证待发布**。基于 E05–E06 并保留提交身份复用 PR197/200；不把依赖代码说成重新开发，不混主工作区 dirty，不合并 GitHub PR。

U01/U03/U05/U06/U07/U08/U14/U15 的设置、新建、模型、档案消费者已迁移：token 单点、共享行/反馈/按钮/输入；模型专属 CSS 独立并复用 motion 入场，取消硬编码颜色梯度，实色/减少透明度/强制颜色兜底。表单真实回执才更新 saved，失败保留与显式重试；G04 的 dirty 分区/返回/全局导航与深链已接 guard，敏感字段不进共享 cache。T02 先解决编辑再退场；模型目录真实导入后直接收尾，不额外等 420ms。没有把共享样式修改等同所有页面已迁移。

新增 C203–C206；实际 Desktop 206 个非测试 TSX、TUI 13 个。G08–G12、其他设置/记忆/目标/远程与原生窗口继续其工作包，不能批量标 Pass。测试已编写/调整但未运行；没有构建/类型/架构/IPC、截图/交互回归或个人应用实例操作。

## E05–E06 前一批更新（2026-10-23）

代码 `2a0ee98be84344b8ae6499ee48b6d25b281afa32`（父提交 `b64337f3`）；[代码 PR208](https://github.com/ly-ccx/Peer-Agent/pull/208)（draft，依赖 PR207）、[实施交接](../../playbook/v0.1.0/experience-navigation-layers.md)。**实现已审阅，候选验证待发布**。G05/G06/G07 的真实消费者与滚动/焦点 seam 已修改；没有新增主题、TSX 页面、物理参数或动画业务回执。未运行测试、构建/类型/架构/IPC 检查、截图或交互回归。

阅读意图不由布局/倒计时改变；返回使用会话内有界 ID/几何快照，旧消息分批恢复且可打断。模态、portal 菜单/提示和 push 档案使用同一逻辑层级；进入/退出、背景隔离和归焦先满足，动画只收尾。tabs 的焦点与选择分开，昂贵视图手动激活；两侧分割条可提交/撤销并清理真实屏障；Tooltip 可关闭、可保持且不抢焦点。原生跨窗口、TUI/remote、200%/读屏/真实 guest 仍须 E11/E13；G04/G08–G12 没有自动关闭。

## E02–E04 前一批更新（2026-10-23）

代码 `b64337f3329539ac2fcc2a16220b62842cdf1ae0`；[交接与待验证项](../../playbook/v0.1.0/experience-p0-input-decisions.md)。U06/U08/U12/U15、M07、T01/T06/T07 的当前输入/决策路径已完成实现与内容/diff 审阅；**候选验证待发布**。沿用 Frost 控件/提示/消息载体，没有新增主题、动效常数或动画成功信号。其余 U/M/T 行及 G04–G12 仍按原排程，尤其 G12 的 WAAPI 降级没有被本次卡片事实修复自动关闭。

本轮实施基线为 `7f900bdb`（RC26 + 已授权规范指令），不是下面原始登记的本地组合 `cb2f5695`；未复制 PR197/198/203/206 或主工作区 dirty 代码。新增 InputRecoveryNotice/InputRecoveryStatus 及 TS/IPC/storage seam 已登记主矩阵，所有新增适用状态仍须 E13 取证。

## 1. 三个体系怎样合作

| 体系 | 回答什么 | 唯一规范 | 本表责任 |
|---|---|---|---|
| UI | 表面、排版、布局、控件及各状态如何组成界面 | [Frost 产品体验规范](../../knowledge/specifications/peer-product-experience-standard.md)；数值以代码 tokens 为准 | U01–U16 把视觉/组件角色映射到实现、差异与任务 |
| 动效 | 一个真实变化如何表现、何时停止、减少动效怎样表达 | [motion-system](../../knowledge/specifications/motion-system.md) | M01–M18 登记现有基元与 CSS/JS 调用边界，不能只数 keyframes |
| 过渡 | 页面/对象/层级改变时，输入、焦点、阅读与事实怎样连续 | [transition-system](../../knowledge/specifications/transition-system.md) | T01–T10 对应规范编号，覆盖来源/目标、取消、恢复与静态终态 |

固定源码：代码仓 `cb2f5695ea164fec7a291570c27c640217c98f1b`，含本地 PR 切片，不等于发布；未提交 CSS 不计入。下文路径 `r/` = `apps/desktop/renderer/src/`。S 为静态已有，G 为交互矩阵的已确认差异，V 为候选待验证。优先级为排程，不是已确认缺陷等级。每行即使有 S，仍不能据此宣告全产品已统一或实机通过。

## 2. 标准化 UI 体系

| ID / 角色与适用页面 | 标准要求 / 现有实现 | 差异或待核 | 排程 / 任务 |
|---|---|---|---|
| U01 语义 token 与主题 | S `styles/tokens.css` 的 `--ui-*`、Frost 语义色/材质/间距；AppearanceProvider/主题注册；S E15 Gateway 既有 palette 下加入角色适配，未引新系统 | S E07/E15 本批 token/角色实现已审阅；V 其他存量兼容、真实主题/远程对比度 | P1 · E07/E15；远程 E11 |
| U02 字体与信息层级 | S sans/mono、12/13/14/15/16/20/26 等语义档，正文行高和阅读列已有 token | V 页面主标题/紧凑标题分工、200% 放大、中英长名/路径/代码；不靠缩小字号压进窄窗 | P1 · E07/E15 |
| U03 几何、间距与密度 | S 8/12/16 曲线、`superellipse(1.4)` 支持检测、space 与 SettingsGroup；S E15 共享 ChoiceStrip/文件输入与远程普通/紧凑几何 | S E07/E15 当前消费者已审阅；V 200%/窄容器/长名和其他存量 | P1 · E07/E15 |
| U04 表面、玻璃、边界与层级 | S chrome/paper/control/glass、overlay、共享 settings-floating；正文稳定底面 | V 嵌套 blur/透明降级/强制颜色、局部 z-index/portal 与模态的交互边界；原生材质需安装包实测 | P1 · E07/E15/E17 |
| U05 按钮/图标/链接 | S PeerIcon/SVG、原生 button、stone/graphite 主操作与已有 focus token；S E15 文件确认/取消 SVG、MCP 按钮/复制失败反馈、远程 focus/target | 当前消费者已审阅；V 读屏/实际目标尺寸/强制颜色及其他操作 | P1 · E06/E15；关键决定 E04 |
| U06 输入/文本编辑/Composer | S 受控 BotComposer、Quick Chat/TUI shared recovery kernel；正文/引用/附件/pending 先保存，匹配 input 确认；经典沿旧持久 seam；E11 远程 composition/229、原请求回执与会话 draft，终端卡片焦点/编辑分开；S E15 C211 文件名 IME/keyup/repeat、失焦留名、明确确认/取消，写入失败保原编辑 | E02/E08/E11/E15 当前路径已审阅；V 真终端/软键盘/读屏/重开与原持久化限制 | P0 E02/E03；P1 E08/E11/E15 |
| U07 Checkbox/Switch/枚举/Slider | S boolean-controls 原生 checkbox/role=switch；AppearanceSlider/ReasoningEffort/EffortRange；S E15 C210 本地 radio、嵌套 Switch 键盘不触发卡片、真实开关回执与逐项 pending | E08/E15 当前消费者已审阅；V 真实设备/读屏/其他 slider/switch 与未知回执 | P1 · E06/E08/E15 |
| U08 搜索/Dropdown/菜单/tooltip | S Dropdown/CascadingMenu/OverflowMenu/查找/tooltip 共用层级、IME/Tab/外点/归焦；过滤 radio、真实 listbox | S E08 C114 纳入共享层级/IME/roving，浏览不写入；G07 已审阅；V 无模型/失效与跨窗口 | P1 · E03/E06/E15 |
| U09 tabs/分段/资源标签 | S Capability/Workbench/档案/Resource tabs 有键盘/roving/panel；昂贵视图手动激活，关闭回相邻；S E15 Capability/Skills tabs 改复用 C210，同 panel 关联、焦点/选择分离 | G05/E06/E15 当前消费者已审阅；V RTL/多实例/失效/动态关闭和 guest | P1 · E06/E15/E17 |
| U10 行/列表/卡/表格/图表 | S BotRow/TasksTab/AttentionSheet、SettingsGroup、UsageStats/Automation 表格、WorkStream；E12 Desktop 四页续读、TUI 50 条公共投影、远程单页/ID 去重/显式缺口与锚点；S E15 installed/available 读失败保快照，文件创建原 scope，E16 FLIP 收尾 | a0ae1a33 对话重复 key 修复，基础列表/对话点查通过；当前路径已审阅；V 跨列 remount 焦点/锚点与真实大列表，其他列表仍待核 | P1 · E05/E07/E11/E12/E15 |
| U11 模态/抽屉/面板/原生弹选 | S modal/push/anchored 共用逻辑父子；Overlay native inert/Tab/focusin、允许自有 portal、幂等退场/恢复触发者；S E16/E17 共享 visualMotion 处理退出拒绝/无事件/隐藏，rail 重开取消旧退出 | 当前路径已审阅；V 嵌套/源消失/反向/归焦/原生窗口 | P1 · E06/E11/E15/E17 |
| U12 消息/过程/决策/结果 | S CardView 不再 generic ok→done；实际 approval/current card + 当前核验/验收真源；TUI cancel 独立不授予执行；S E17 经典授权点击立即交原宿主回调，问题关闭只清显示 footprint | E04/E11/E16/E17 当前路径已审阅；V 迟到/过期/跨入口事实/实际焦点，不从动画造许可 | P0 事实 · E04；P1 表达 E11/E15/E17 |
| U13 附件/引用/产物/媒体预览 | S QuoteChip/ReplyAnchors、BotAttachments、ImageLightbox、Markdown/Source/Diff viewers | S E09/G08 图片/文本/元信息、原 ID 定位、Evidence/文件分别可达和失败重读已审阅；V OS/解码/旧源/局部阅读/长内容与键盘 | P1 · E09/E15/E17 |
| U14 设置/资料/能力/自动化编辑 | S SettingsGroup、12 个公开设置分区、bot 五 tab、能力/自动化各表单；S E15/E17 Skills/MCP reader/真实回执、敏感编辑 dirty 离开/显式舍弃；无新增缓存 | E08/E10/E15 当前消费者已审阅；V 外部变化/未知/部分写入与未触及表单 | P1 · E07/E08/E10/E15/E17 |
| U15 空/加载/失败/失效/恢复与通知 | S 对话渐进读取、pending/stop/error、updater phase、后台记录、受管 surfacing 与通知；E12 bootstrap 重读/旧壳层与历史继续，E11 远程详情/设备保快照；S E15 能力/Skills/MCP 真空只由成功读取确认，失败保快照/重读、数量未确认 | 当前路径已审阅；V OS/迟到/未知/部分写入与真实通知，不批量判定其他空态 | P0 关键事实 E04；P1 E10/E11/E12/E15 |
| U16 跨宿主与可访问性 | S E11 按 host 对照事实、输入、许可、恢复；终端主题原语/焦点，远程原生表单/静态状态；CLI/ACP 图形态 N/A；S E15 Gateway 原生表单角色适配、coarse target/强制颜色，不照搬 Desktop CSS | 当前路径已审阅；V 真终端/软键盘/读屏/200%/跨窗口/安装、完整视觉对照 | P1 · E11/E13/E15 |

UI 的交付单位是“一个角色 + 全部适用状态 + 实际消费者”，不是一张默认截图。并非每个角色要新建通用组件；已有共享接口优先，临时例外标注范围/原因/替代路径/退出条件。不得为了统一布局更改权限、Context Source 或存储。

## 3. 标准化动效体系

数值仍沿用 fast/medium/slow = 120/200/320ms、shift = 6/12/24px 和既有 easing；这里只登记语义与责任。历史 `za-*` keyframe、集中 `motion-*` 和 JS 表现都在治理范围，集中存放不等于每个效果都应该推广。

| ID / 语义 | 现有实现与适用消费者 | 差异/退出要求 | 排程 / 任务 |
|---|---|---|---|
| M01 控件即时回执 | S token 驱动 hover/pressed/focus、共享 button/switch/checkbox CSS；S E15 共享 ChoiceStrip/文件确认/MCP 反馈与远程 focus/pressed | 本批控件状态已审阅；V 对比度/目标尺寸/其他消费者 | P1 · E15/E16 |
| M02 fade/rise/pop 入场 | S `motion-enter-fade/rise/pop`；settings/menu/轻层及部分页面；S E16 motionEnvironment/visualMotion 接入相关消费者 | 当前路径已审阅；V 静态偏好/重复打开/其他入场和动画 API | P1 · E16/E17 |
| M03 inline slide 抽屉 | S `motion-enter/exit-slide-inline`；Drawer/档案覆盖层；S E16 档案 push 监听偏好/隐藏，关闭中断不留旧 out timer | 当前路径已审阅；V RTL/方向/push-cover/resize，PR204 未纳入 | P1 · E06/E16/E17 |
| M04 fade/sink/pop 退场 | S motion exit 与 Overlay 自带 CSS/fallback、useMotionPresence；S E16 Overlay/presence 共用 watchVisualMotion，幂等 finish/cancel、有界 fallback | 当前路径已审阅；V 缺 API/无事件/拒绝/反向/嵌套/真实归焦 | P1 · E16/E17 |
| M05 fold/grid/height | S SettingsDisclosureContent、BotProcess/details、问题的 WAAPI 高度折叠；S G12/E16 问题 animateVisual 静态/无 API/拒绝/fallback，disclosure 同收尾 | 当前实现已审阅；V 快速反向/无触发者/卸载/旧 promise 与实际焦点 | P1 · E06/E16/E17 |
| M06 分段/选值指示器 | S BotDrawerSegments/PaletteSelect/模型强度相关 transform/transition；S E15 C210 本地 radio/手动 tabs，选择指示由受控值决定 | 当前消费者已审阅；V 真实键盘/RTL/快速反向/其他选择器 | P1 · E06/E15/E16 |
| M07 新消息/用户待发气泡 | S 保留 UserBubble/连续回复载体；恢复 kernel 延续 inputId，unknown 不制造进行中回复 | G01 实现已审阅；V arriving 最多一次、公共 echo/重开静态；未新增动画 | P0 输入 E02；P1 E16/E17 |
| M08 执行状态循环 | S `motion-pulse-soft/attention`、spin/dots、真实 activity/status 消费；S E16 ThinkingOrb 动态偏好/隐藏暂停，typewriter 停 rAF 并交出已收到文本 | 当前消费者已审阅；V 其余 CSS 循环/真实离屏/能耗与正文思考交接 | P1 · E04/E16 |
| M09 加载/骨架/不定进度 | S 现有 progress/shimmer；E12 bootstrap 事实与可选预取分开，远程详情先 loading/可恢复失败 | 当前路径实现已审阅；V 几何稳定/无权限/耗时，未知执行不永远假进行中；无总量不造百分比 | P1 · E12/E15/E16 |
| M10 定位/引用短提示 | S `motion-flash` 与 BotConversation 高亮/ReplyAnchors | V 不抢回贴底、不持续闪烁，键盘/读屏有目标；失效引用有提示 | P1 · E05/E09/E16 |
| M11 对象缩向目标 | S `motion-exit-to-target`、Overlay closeTarget、VersionBadge pending | V 目标先接住、测量无效直接淡出；timer 不能把请求写成已下载 | P1 · E12/E16/E17 |
| M12 列表重排/塌缩 | S WorkStream FLIP、useShatterExitCollapse、局部列表/队列；S E16 FLIP/塌缩用 token/visualMotion，偏好/隐藏取消，缺 API 静态 | 当前实现已审阅；V 跨列 remount 选择/焦点/锚点，未改保 DOM 布局 | P1 · E05/E06/E16/E17 |
| M13 品牌启动 | S BrandStartupLoader/brand-startup-* 表达真实启动；E12 已删除 minHold 与强制等待 | G10 当前实现已审阅；V 真实冷启/减少动效/失败重读/窗口；不宣称时延已测 | P1 · E12/E16/E17 |
| M14 头像凝视/呼吸/思考 | S `bot-avatar-*`、头像状态和 reduce CSS 重置 gaze；S E16 共享 observer/偏好/隐藏，gaze 前置检查，缺 observer 静态 | 当前实现已审阅；V 真实离屏/事件顺序/能耗，状态名不制造行动权 | P1 · E15/E16 |
| M15 结果庆祝/粒子 | S `result-card-*`、`gwb-item-*`、ParticleShatterOverlay；S G11/E16 捕获/运行前短路、AbortSignal/隐藏停帧、捕获失败保真源 | 当前实现已审阅；V canvas/CSP/API/重复 active/卸载；真实签收与可选特效分开 | P1 降级 E16；P2 装饰 E14 |
| M16 图像缩放/拖动/尺寸 | S ImageLightbox fit/actual、分割条 rAF、浏览器挂载稳定 | S G06/E06 分割条、E09/G08 加载/解码失败可重读，图片就绪后原尺寸；V guest/窄窗/真实键盘与 reduce | P1 · E06/E09/E16/E17 |
| M17 sheen/halo/ripple/glow 等存量基元 | S motion.css 中有这些定义；**定义存在不等于所有组件都在用** | V 新调用先解释理解收益、循环开销与静态终态；不扩散 blur/shadow/background 循环；逐字模糊不采用 | P2 增强 E14；存量降级 P1 E16 |
| M18 全局治理/偏好/API | S tokens 全局 reduce；集中 keyframe 架构检查；presence、Overlay、部分 WAAPI 各自处理；S E16 共享 motionEnvironment/visualMotion/useMotionAllowed 与消费者，显式定位静态 | G11/G12 当前实现已审阅；V 其他 CSS/WAAPI/JS、真实偏好/可见性/无事件/卸载，checker 不替代行为证据 | P1 · E16/E13 |

需登记的执行顺序：真实状态变更 → 小范围呈现 → 幂等表现收尾。若实现中动画结束才写业务决定，先归到 E04 的事实边界处理，而非“微调曲线”。循环性能与帧率本轮没有测量，不承诺 GPU/120Hz。

## 4. 标准化过渡体系

编号与规范完全一致；组件状态模板 O/G/V/I 对每个来源和目标生效。

| ID / 全链路场景 | 当前来源→目标、状态和实现基础 | 缺口与必须保留 | 排程 / 任务 |
|---|---|---|---|
| T01 导航/换机器人/任务 | S BotListShell/任务现场/HistorySheet、经典 activePage、TUI view、remote selected；E11 TUI 先保存后关闭/卸载切换，远程按 bot 保草稿/读位和旧请求隔离；S E17 tools 离开也经 dirty guard，MCP 表单当前编辑不静默丢失 | 本机同 bot 的设置/能力/自动化往返、草稿保留点查通过；当前路径已审阅；V 原生/旧源/跨窗口/未知与真实 IME；背景不夺焦点 | P0 输入 E02；P1 E05/E11/E17 |
| T02 模态/抽屉/嵌套 | S Overlay/Drawer/focus scope、档案→现场→Evidence、confirm；S E17 表单 dirty 在退场前决定；Overlay/档案/rail 中断共用清理 | 当前路径已审阅；V 嵌套/反向/源消失/原生关闭与归焦 | P1 · E06/E17 |
| T03 菜单/提示/锚定 | S Dropdown/CascadingMenu/Tooltip、anchoredOverlay 与原生 QuickChat popover | S E08 统一模型菜单加入 shared owner/键盘/锚点失效关闭；V 定位/窄窗/真实跨窗口 | P1 · E06/E11/E17 |
| T04 标签/分段/分区 | S SettingsPage、BotDrawerSegments、ResourceTabStrip、CapabilityTabs、模型面板；S E15/E17 Capability/Skills tabs 和 MCP radio 共用 C210；切离 MCP 经 guard | 当前消费者已审阅；V 快速竞争/失效选择/旧设置消费者与真实焦点 | P1 · E06/E08/E15/E17 |
| T05 折叠/展开/详情 | S SettingsDisclosureContent、BotProcess、ReplyDetails、问题 dismissal；S G12/E16/E17 无 API/拒绝/无事件静态收尾，原问题持焦点才交本地 composer | 当前实现已审阅；V 反向/卸载/旧闭包/背景解决不夺焦点/真实系统 | P1 · E05/E06/E16/E17 |
| T06 待发/接收/连续回复 | S shared recovery kernel + device store，完整 envelope 先保存；匹配 input/public echo 确认，同 ID retry；30秒只结束界面等待；E11 远程匹配原 requestId+ok+received 才确认、手动同 ID 重试；S E16 静态/后台直接交出已收到文本，停止显示泵；无新请求/正文 | E02/E11/E16 当前路径已审阅；V 正文/思考/工具交接/取消、未知与真实宿主 | P0 · E02/E03；P1 E11/E16/E17 |
| T07 决策/执行/核验/交还 | S 结构化 approval/current card 与 lifecycle/verification/acceptance 真源分开；旧展示记录不盖当前授权/验收；S E17 经典授权立即交原回调，同展示对象防重；移除动画派发延迟 | E04/E16/E17 当前路径已审阅；V 宿主 grant/过期/拒绝/取消/未知/核验与签收分开 | P0 · E04；P1 E17 |
| T08 列表增删/排序/分页 | S BotList/TasksTab/Memory/Files、MessageQueue、WorkStream/virtual pager；E12 Desktop 四页衔接、远程单页/显式缺口/锚点、TUI 同目标在途公共页合并；S E15/E17 文件名失焦保留/显式创建，原 scope 回执、失败留现场/条件归焦；E16 FLIP 中断 | 本机历史阅读模式与单个回最新点查通过；当前路径已审阅；V 完整树键盘/目录并发/跨列 remount 焦点与实际阅读，其他列表仍 V | P1 · E05/E06/E10/E11/E12/E17 |
| T09 预览/分栏/最大化 | S ImageLightbox/Document/Browser、WorkbenchResize、档案 push/cover；S E16 push 档案的隐藏/偏好与静态退出已接共享收尾 | 当前路径已审阅；V guest/resize/窄窗/旧源/真实辅助技术，PR204 待集成 | P1 · E06/E09/E17；共享元素 P2 E14 |
| T10 启动/主题/升级/宿主恢复 | S bootstrap reader/真实就绪、AppearanceProvider、VersionBadge/updater、host lease/恢复投影；E12 删除 minHold、按真实就绪/失败重读保旧壳层，E11 模式/页面恢复使旧请求失效 | G10 当前实现已审阅；V 主题保编辑/徽标承接/关窗不取消、未知执行不重放、备份一致性/身份与安装包恢复 | P1 · E11/E12/E16/E17 |

## 5. 发布验收与进度记账

E15–E17 的实现卡必须引用本表 U/M/T 编号和对应 P/C 行，写明允许文件、状态事实源、已有 seam、取消恢复与降级。一个实际修改可同时关闭多行的同一差异，但不能只改共享 CSS 就把所有消费者标成达标。

进度字段使用：已登记 → 待实现 / 待核 → 实现已审阅 → 候选验证通过（绑定 source/包/证据）。S 不是流程状态；文档提交只完成“已登记”。隐藏/兼容入口注明范围，暂不实现的例外有退出条件，不标 Pass。

普通任务只审阅内容/diff；不自动跑测试、截图、构建或类型/架构/IPC 检查。发布时按 E13 和[验收指南](../../playbook/v0.1.0/acceptance-test-guide.md)将本表映射到既有场景，补没有覆盖的键盘/焦点/IME/取消/减少动效/API 降级及宿主验证，再在合并全部 PR 的最终候选运行完整门禁。不能用截图数量或旧版本 Pass 代替这些行为证据。
