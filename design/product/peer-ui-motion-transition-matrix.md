# Peer UI、动效与过渡体系覆盖表

创建时间：2026-10-23
最后更新：2026-10-23

> 状态：规范到存量实现的映射；纳入[当前改造计划](peer-product-renovation-plan.md) E15/UI、E16/动效、E17/过渡，发布证据统一归 E13。
> 组件与页面逐项登记见[全产品交互矩阵](peer-interaction-standardization-matrix.md)。本文不另立视觉数值、运动常数、组件库或验收账本。

## E07–E08 本轮更新（2026-10-23）

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
|---|---|---|---|---|
| U01 语义 token 与主题 | S `styles/tokens.css` 的 `--ui-*`、Frost 语义色/材质/间距；AppearanceProvider/主题注册 | S E07 控件高度/焦点在 tokens 单点，Frost/space/字号复用；V 存量兼容/主题/远程映射，未批量迁移 | P1 · E07/E15；远程 E11 |
| U02 字体与信息层级 | S sans/mono、12/13/14/15/16/20/26 等语义档，正文行高和阅读列已有 token | V 页面主标题/紧凑标题分工、200% 放大、中英长名/路径/代码；不靠缩小字号压进窄窗 | P1 · E07/E15 |
| U03 几何、间距与密度 | S 8/12/16 曲线、`superellipse(1.4)` 支持检测、space 与 SettingsGroup | S E07 共享行/按钮/输入/模型几何，普通/紧凑密度；V 200%/窄容器/长名和其他存量 | P1 · E07/E15 |
| U04 表面、玻璃、边界与层级 | S chrome/paper/control/glass、overlay、共享 settings-floating；正文稳定底面 | V 嵌套 blur/透明降级/强制颜色、局部 z-index/portal 与模态的交互边界；原生材质需安装包实测 | P1 · E07/E15/E17 |
| U05 按钮/图标/链接 | S PeerIcon/SVG、原生 button、stone/graphite 主操作与已有 focus token | S E07 本批 ui-button 统一 H/P/F/D 与 busy 防重入、SVG 名称；V 真实目标尺寸/读屏/其他操作 | P1 · E06/E15；关键决定 E04 |
| U06 输入/文本编辑/Composer | S 受控 BotComposer、Quick Chat/TUI shared recovery kernel；正文/引用/附件/pending 先保存，匹配 input 确认；经典沿旧持久 seam | S E08 配置 saved/draft/error/stale 恢复，新建 IME 与未知创建；E02 输入不变；V OS/重开/多窗口 | P0 输入 · E02/E03；视觉 P1 E15 |
| U07 Checkbox/Switch/枚举/Slider | S boolean-controls 原生 checkbox/role=switch；AppearanceSlider/ReasoningEffort/EffortRange | S E08 模型通道 radio/键盘与受控值、range 可撤销预览；V 真实设备/读屏/其他 slider/switch | P1 · E06/E08/E15 |
| U08 搜索/Dropdown/菜单/tooltip | S Dropdown/CascadingMenu/OverflowMenu/查找/tooltip 共用层级、IME/Tab/外点/归焦；过滤 radio、真实 listbox | S E08 C114 纳入共享层级/IME/roving，浏览不写入；G07 已审阅；V 无模型/失效与跨窗口 | P1 · E03/E06/E15 |
| U09 tabs/分段/资源标签 | S Capability/Workbench/档案/Resource tabs 有键盘/roving/panel；昂贵视图手动激活，关闭回相邻 | G05/E06 实现已审阅；V RTL/多实例/失效选择/动态关闭、guest | P1 · E06/E15/E17 |
| U10 行/列表/卡/表格/图表 | S BotRow/TasksTab/AttentionSheet、SettingsGroup、UsageStats/Automation 表格、WorkStream | V Ø/L/X/T/R、选择与锚点/分页/长值；图表不只依 hover/颜色，提供文字与键盘入口 | P1 · E05/E07/E15 |
| U11 模态/抽屉/面板/原生弹选 | S modal/push/anchored 共用逻辑父子；Overlay native inert/Tab/focusin、允许自有 portal、幂等退场/恢复触发者 | E06 实现已审阅；V 嵌套/初始双层/外点/源消失/反向、原生窗口 | P1 · E06/E15/E17 |
| U12 消息/过程/决策/结果 | S CardView 不再 generic ok→done；实际 approval/current card + 当前核验/验收真源；TUI cancel 独立不授予执行 | E04 实现已审阅；V 授权/执行/核验/签收/Git交回对照、迟到/过期/撤权；G12 后置 | P0 事实 · E04；P1 表达 E15/E17 |
| U13 附件/引用/产物/媒体预览 | S QuoteChip/ReplyAnchors、BotAttachments、ImageLightbox、Markdown/Source/Diff viewers | G08；V 同一来源/失效/未支持/读失败、复制/打开错误与局部滚动，artifact 不冒充 Evidence | P1 · E09/E15/E17 |
| U14 设置/资料/能力/自动化编辑 | S SettingsGroup、12 个公开设置分区、bot 五 tab、能力/自动化各表单 | S G04/E08 设置/连接/目录/模型/名称的 dirty 与真实保存恢复；V 其他能力/记忆/目标编辑仍 E08/E10 | P1 · E07/E08/E10/E15/E17 |
| U15 空/加载/失败/失效/恢复与通知 | S 对话渐进读取、pending/stop/error、updater phase、后台记录、受管 surfacing 与通知 | S E08 读取失败保旧事实，失败保编辑/请求与重试；创建未知先核对列表；V G08/G09 与真实未知/部分写入 | P0 关键事实 E04；P1 E10/E12/E15 |
| U16 跨宿主与可访问性 | S Desktop/TUI/CLI/Gateway 各现有实现；终端有主题 primitives、remote 有原生表单/status | V shared 语义映射、焦点/读屏/目标尺寸/软键盘/窄窗；CLI/ACP 无图形状态注明 N/A；不引第二设计系统 | P1 · E11/E13/E15 |

UI 的交付单位是“一个角色 + 全部适用状态 + 实际消费者”，不是一张默认截图。并非每个角色要新建通用组件；已有共享接口优先，临时例外标注范围/原因/替代路径/退出条件。不得为了统一布局更改权限、Context Source 或存储。

## 3. 标准化动效体系

数值仍沿用 fast/medium/slow = 120/200/320ms、shift = 6/12/24px 和既有 easing；这里只登记语义与责任。历史 `za-*` keyframe、集中 `motion-*` 和 JS 表现都在治理范围，集中存放不等于每个效果都应该推广。

| ID / 语义 | 现有实现与适用消费者 | 差异/退出要求 | 排程 / 任务 |
|---|---|---|---|---|
| M01 控件即时回执 | S token 驱动 hover/pressed/focus、共享 button/switch/checkbox CSS | S E07 本批控件用共享反馈 token，真实 busy/dirty/error 独立于动效；V 对比度/目标尺寸与其他消费者 | P1 · E15/E16 |
| M02 fade/rise/pop 入场 | S `motion-enter-fade/rise/pop`；settings/menu/轻层及部分页面 | S E07 模型面板/子菜单专属 keyframes 改共享 rise/fade；V 静态偏好/重复打开/其他消费者 | P1 · E16/E17 |
| M03 inline slide 抽屉 | S `motion-enter/exit-slide-inline`；Drawer/档案覆盖层 | S E06 档案/Drawer 层级与归焦基础；V 方向/RTL、push/cover 连续和 resize，PR204 待集成 | P1 · E06/E16/E17 |
| M04 fade/sink/pop 退场 | S motion exit 与 Overlay 自带 CSS/fallback、useMotionPresence | S E08 Overlay 退场前 dirty veto；目录收到真实导入回执后直接收尾，不固定等 420ms；V 取消/卸载/竞态 | P1 · E16/E17 |
| M05 fold/grid/height | S SettingsDisclosureContent、BotProcess/details、问题的 WAAPI 高度折叠 | S E06 disclosure 隐藏立即 inert、内部焦点交回触发者；G12 问题 WAAPI 仍后置；V 反向/卸载/无触发者 | P1 · E06/E16/E17 |
| M06 分段/选值指示器 | S BotDrawerSegments/PaletteSelect/模型强度相关 transform/transition | S E08 模型选中完全受控，服务商浏览/焦点不制造保存；V range/通道重试、快速反向与真实主机 | P1 · E06/E15/E16 |
| M07 新消息/用户待发气泡 | S 保留 UserBubble/连续回复载体；恢复 kernel 延续 inputId，unknown 不制造进行中回复 | G01 实现已审阅；V arriving 最多一次、公共 echo/重开静态；未新增动画 | P0 输入 E02；P1 E16/E17 |
| M08 执行状态循环 | S `motion-pulse-soft/attention`、spin/dots、真实 activity/status 消费 | V 只在真实非终态、不可见/后台停止无意义循环；状态文字和 reduce 静态 | P1 · E04/E16 |
| M09 加载/骨架/不定进度 | S `motion-progress-slide/shimmer`、页面 loading 分支 | V 真实读取/几何稳定；无总量不造百分比、无权限不永远 skeleton | P1 · E12/E15/E16 |
| M10 定位/引用短提示 | S `motion-flash` 与 BotConversation 高亮/ReplyAnchors | V 不抢回贴底、不持续闪烁，键盘/读屏有目标；失效引用有提示 | P1 · E05/E09/E16 |
| M11 对象缩向目标 | S `motion-exit-to-target`、Overlay closeTarget、VersionBadge pending | V 目标先接住、测量无效直接淡出；timer 不能把请求写成已下载 | P1 · E12/E16/E17 |
| M12 列表重排/塌缩 | S WorkStream FLIP、useShatterExitCollapse、局部列表/队列 | V 选择/锚点保持，用户拖动与真实删除分开，reduce 即时落位 | P1 · E05/E06/E16/E17 |
| M13 品牌启动 | S `brand-startup-*` 与 BrandStartupLoader/minHold | G10；就绪不为品牌固定等待，静态错误/恢复完整 | P1 · E12/E16/E17 |
| M14 头像凝视/呼吸/思考 | S `bot-avatar-*`、头像状态和 reduce CSS 重置 gaze | V JS 指针/帧任务/可见性与偏好变化，状态名不产生假行动权 | P1 · E15/E16 |
| M15 结果庆祝/粒子 | S `result-card-*`、`gwb-item-*`、ParticleShatterOverlay | G11；先短路减少动效的 JS 工作。真实签收与消失分开，重连不重复庆祝 | P1 降级 E16；P2 装饰 E14 |
| M16 图像缩放/拖动/尺寸 | S ImageLightbox fit/actual、分割条 rAF、浏览器挂载稳定 | S G06/E06 两侧分割条取消回原值、真实屏障/清理；G08 图像失败后置；V guest/窄窗/键盘 | P1 · E06/E09/E16/E17 |
| M17 sheen/halo/ripple/glow 等存量基元 | S motion.css 中有这些定义；**定义存在不等于所有组件都在用** | V 新调用先解释理解收益、循环开销与静态终态；不扩散 blur/shadow/background 循环；逐字模糊不采用 | P2 增强 E14；存量降级 P1 E16 |
| M18 全局治理/偏好/API | S tokens 全局 reduce；集中 keyframe 架构检查；presence、Overlay、部分 WAAPI 各自处理 | G11/G12；V JS/WAAPI/smooth scroll、偏好变化/无事件/卸载。现有 checker 不覆盖所有语义/帧率/可达性 | P1 · E16/E13 |

需登记的执行顺序：真实状态变更 → 小范围呈现 → 幂等表现收尾。若实现中动画结束才写业务决定，先归到 E04 的事实边界处理，而非“微调曲线”。循环性能与帧率本轮没有测量，不承诺 GPU/120Hz。

## 4. 标准化过渡体系

编号与规范完全一致；组件状态模板 O/G/V/I 对每个来源和目标生效。

| ID / 全链路场景 | 当前来源→目标、状态和实现基础 | 缺口与必须保留 | 排程 / 任务 |
|---|---|---|---|---|
| T01 导航/换机器人/任务 | S BotListShell/任务现场/HistorySheet、经典 activePage、TUI view、remote selected | S E08 从设置离开的全局页面/deep-link 守住 dirty；E05 阅读保持不变；V 源失效/宿主恢复/其他导航 | P0 输入 E02；P1 E05/E11/E17 |
| T02 模态/抽屉/嵌套 | S Overlay/Drawer/focus scope、档案→现场→Evidence、confirm | S E08 编辑器先决定可否关闭，再用共享 Overlay 退场；save/discard/stay 与忙碌回执；V 嵌套/原生关闭/归焦 | P1 · E06/E17 |
| T03 菜单/提示/锚定 | S Dropdown/CascadingMenu/Tooltip、anchoredOverlay 与原生 QuickChat popover | S E08 统一模型菜单加入 shared owner/键盘/锚点失效关闭；V 定位/窄窗/真实跨窗口 | P1 · E06/E11/E17 |
| T04 标签/分段/分区 | S SettingsPage、BotDrawerSegments、ResourceTabStrip、CapabilityTabs、模型面板 | S G04/E08 dirty 分区/返回/深链、G05 语义与受控模型值已审阅；V 新旧设置消费者/快速竞争/焦点 | P1 · E06/E08/E15/E17 |
| T05 折叠/展开/详情 | S SettingsDisclosureContent、BotProcess、ReplyDetails、问题 dismissal | S E06 disclosure 收起归焦/inert；G12 问题 dismissal 仍待 E16；V 用户收起、反向/无 API/卸载 | P1 · E05/E06/E16/E17 |
| T06 待发/接收/连续回复 | S shared recovery kernel + device store，完整 envelope 先保存；匹配 input/public echo 确认，同 ID retry；30秒只结束界面等待 | G01/G02/G03 实现已审阅；V quote/附件/未知/迟到/重开和历史静态；不自动重发 | P0 · E02/E03；P1 E16/E17 |
| T07 决策/执行/核验/交还 | S 结构化 approval/current card 与 lifecycle/verification/acceptance 真源分开；旧展示记录不盖当前授权/验收 | E04 实现已审阅；V 列表/卡片/详情、过期/取消/拒绝/未知、核验≠签收≠交回；G12 后置 | P0 · E04；P1 E17 |
| T08 列表增删/排序/分页 | S BotList/TasksTab/Memory/Files、MessageQueue、WorkStream/virtual pager | S E05 分页保锚点、恢复有界且可取消；S E06 资源关闭归相邻；G09 后置，V 来源丢失/动态列表 | P1 · E05/E06/E10/E17 |
| T09 预览/分栏/最大化 | S ImageLightbox/Document/Browser、WorkbenchResize、档案 push/cover | G06/E06 resize 提交/撤销/恢复阶段与屏障已审阅；G08 后置；V guest 身份不误销毁、预览/窄窗 | P1 · E06/E09/E17；共享元素 P2 E14 |
| T10 启动/主题/升级/宿主恢复 | S bootstrap/minHold、AppearanceProvider、VersionBadge/updater、host lease/恢复投影 | G10；V 内容就绪即用、主题变更保编辑、窗口关闭不取消、未知执行不重放、徽标先承接 | P1 · E11/E12/E16/E17 |

## 5. 发布验收与进度记账

E15–E17 的实现卡必须引用本表 U/M/T 编号和对应 P/C 行，写明允许文件、状态事实源、已有 seam、取消恢复与降级。一个实际修改可同时关闭多行的同一差异，但不能只改共享 CSS 就把所有消费者标成达标。

进度字段使用：已登记 → 待实现 / 待核 → 实现已审阅 → 候选验证通过（绑定 source/包/证据）。S 不是流程状态；文档提交只完成“已登记”。隐藏/兼容入口注明范围，暂不实现的例外有退出条件，不标 Pass。

普通任务只审阅内容/diff；不自动跑测试、截图、构建或类型/架构/IPC 检查。发布时按 E13 和[验收指南](../../playbook/v0.1.0/acceptance-test-guide.md)将本表映射到既有场景，补没有覆盖的键盘/焦点/IME/取消/减少动效/API 降级及宿主验证，再在合并全部 PR 的最终候选运行完整门禁。不能用截图数量或旧版本 Pass 代替这些行为证据。
