# Peer UI、动效与过渡体系覆盖表

创建时间：2026-10-23
最后更新：2026-10-23

> 状态：规范到存量实现的映射；纳入[当前改造计划](peer-product-renovation-plan.md) E15/UI、E16/动效、E17/过渡，发布证据统一归 E13。
> 组件与页面逐项登记见[全产品交互矩阵](peer-interaction-standardization-matrix.md)。本文不另立视觉数值、运动常数、组件库或验收账本。

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
| U01 语义 token 与主题 | S `styles/tokens.css` 的 `--ui-*`、Frost 语义色/材质/间距；AppearanceProvider/主题注册 | V 存量 `--za-*` 合法兼容与旧 ink/cinnabar 不再扩散；组件硬编码/透明度例外需登记。远程 CSS 独立变量，尚未共享映射 | P1 · E07/E15；远程 E11 |
| U02 字体与信息层级 | S sans/mono、12/13/14/15/16/20/26 等语义档，正文行高和阅读列已有 token | V 页面主标题/紧凑标题分工、200% 放大、中英长名/路径/代码；不靠缩小字号压进窄窗 | P1 · E07/E15 |
| U03 几何、间距与密度 | S 8/12/16 曲线、`superellipse(1.4)` 支持检测、space 与 SettingsGroup | V 老组件/自绘菜单/图表/原生窗口各状态同角色一致，边框变化不跳尺寸；特殊形状记录例外 | P1 · E07/E15 |
| U04 表面、玻璃、边界与层级 | S chrome/paper/control/glass、overlay、共享 settings-floating；正文稳定底面 | V 嵌套 blur/透明降级/强制颜色、局部 z-index/portal 与模态的交互边界；原生材质需安装包实测 | P1 · E07/E15/E17 |
| U05 按钮/图标/链接 | S PeerIcon/SVG、原生 button、stone/graphite 主操作与已有 focus token | V H/P/F/D/B/X、32px 默认目标/触控44px目标、紧凑例外、hover 操作键盘可发现；复制/打开失败不静默 | P1 · E06/E15；关键决定 E04 |
| U06 输入/文本编辑/Composer | S BotComposer、ComposerDraftControls、textarea、引用/附件/停止控制 | G01/G02/G03；V 同份草稿与 pending envelope、IME、发送/停止位置、dirty/invalid、保留附件和引用 | P0 输入 · E02/E03；视觉 P1 E15 |
| U07 Checkbox/Switch/枚举/Slider | S boolean-controls 原生 checkbox/role=switch；AppearanceSlider/ReasoningEffort/EffortRange | V 受控实际值、S/D/B/X/R、标签关联、键盘范围与离散档、保存失败回读；不以移动旋钮制造保存成功 | P1 · E06/E08/E15 |
| U08 搜索/Dropdown/菜单/tooltip | S Dropdown/CascadingMenu/OverflowMenu/搜索 palette、Tooltip portal | G07；V 无结果/加载/错误/旧响应、组合输入/方向键/Escape、disabled item 与关闭归焦 | P1 · E03/E06/E15 |
| U09 tabs/分段/资源标签 | S BotDrawerSegments 有 roving/方向键/手势；ResourceTabStrip、CapabilityTabs 有部分语义 | G05；V panel 名称关联、多实例/RTL/关闭当前标签、昂贵加载手动激活；选中事实先于指示器 | P1 · E06/E15/E17 |
| U10 行/列表/卡/表格/图表 | S BotRow/TasksTab/AttentionSheet、SettingsGroup、UsageStats/Automation 表格、WorkStream | V Ø/L/X/T/R、选择与锚点/分页/长值；图表不只依 hover/颜色，提供文字与键盘入口 | P1 · E05/E07/E15 |
| U11 模态/抽屉/面板/原生弹选 | S Overlay/Drawer/useFocusScope、BotProfileDrawer push/cover、QuickChatPopoverHost | V 真 modal 与 anchored 语义、背景隔离、命名、进出焦点、嵌套 Escape、退场不拖住操作 | P1 · E06/E15/E17 |
| U12 消息/过程/决策/结果 | S 连续公共回复、CardView/ApprovalReceipt、统一核验详情/任务取消和 lifecycle 消费 | V 授权→执行→核验→签收→Git交回不混、未知与旧错误区分、已解决问题可收起；G12 降级 | P0 事实 · E04；P1 表达 E15/E17 |
| U13 附件/引用/产物/媒体预览 | S QuoteChip/ReplyAnchors、BotAttachments、ImageLightbox、Markdown/Source/Diff viewers | G08；V 同一来源/失效/未支持/读失败、复制/打开错误与局部滚动，artifact 不冒充 Evidence | P1 · E09/E15/E17 |
| U14 设置/资料/能力/自动化编辑 | S SettingsGroup、12 个公开设置分区、bot 五 tab、能力/自动化各表单 | G04/G09；V 表单一致结构：名称/作用域→当前值→编辑→提交/错误→恢复；dirty 离开和异步回读 | P1 · E07/E08/E10/E15/E17 |
| U15 空/加载/失败/失效/恢复与通知 | S 对话渐进读取、pending/stop/error、updater phase、后台记录、受管 surfacing 与通知 | V 全页各错误类型有原因/保住什么/谁处理/下一步；Memory/G08 的真空与失败补分支；无假百分比 | P0 关键事实 E04；P1 E10/E12/E15 |
| U16 跨宿主与可访问性 | S Desktop/TUI/CLI/Gateway 各现有实现；终端有主题 primitives、remote 有原生表单/status | V shared 语义映射、焦点/读屏/目标尺寸/软键盘/窄窗；CLI/ACP 无图形状态注明 N/A；不引第二设计系统 | P1 · E11/E13/E15 |

UI 的交付单位是“一个角色 + 全部适用状态 + 实际消费者”，不是一张默认截图。并非每个角色要新建通用组件；已有共享接口优先，临时例外标注范围/原因/替代路径/退出条件。不得为了统一布局更改权限、Context Source 或存储。

## 3. 标准化动效体系

数值仍沿用 fast/medium/slow = 120/200/320ms、shift = 6/12/24px 和既有 easing；这里只登记语义与责任。历史 `za-*` keyframe、集中 `motion-*` 和 JS 表现都在治理范围，集中存放不等于每个效果都应该推广。

| ID / 语义 | 现有实现与适用消费者 | 差异/退出要求 | 排程 / 任务 |
|---|---|---|---|---|
| M01 控件即时回执 | S token 驱动 hover/pressed/focus、共享 button/switch/checkbox CSS | V 不改控件几何、操作不等动画、D/B 有文字/名称；reduce 静态保留选值 | P1 · E15/E16 |
| M02 fade/rise/pop 入场 | S `motion-enter-fade/rise/pop`；settings/menu/轻层及部分页面 | V 语义使用/位移档、同屏叠加预算；历史/主题重挂载不全量重播 | P1 · E16/E17 |
| M03 inline slide 抽屉 | S `motion-enter/exit-slide-inline`；Drawer/档案覆盖层 | V 真实方向/RTL、进出焦点、反向/卸载；push 与 cover 同对象连续 | P1 · E06/E16/E17 |
| M04 fade/sink/pop 退场 | S motion exit 与 Overlay 自带 CSS/fallback、useMotionPresence | V 一次幂等收尾、animationcancel/缺事件/无 API、不把关闭回调当成功 | P1 · E16/E17 |
| M05 fold/grid/height | S SettingsDisclosureContent、BotProcess/details、问题的 WAAPI 高度折叠 | G12；V hidden Tab 立即移除、焦点先退回/用户收起意图；不是零 layout | P1 · E06/E16/E17 |
| M06 分段/选值指示器 | S BotDrawerSegments/PaletteSelect/模型强度相关 transform/transition | G05 是键盘差异；V 多实例隔离、选择先成立、反向不排队 | P1 · E06/E15/E16 |
| M07 新消息/用户待发气泡 | S UserBubble arriving、连续回复/LiveReply 组合 | V 一条新消息最多一次、同身份接管、历史/reconnect 静态；G01 恢复先行 | P0 输入 E02；P1 E16/E17 |
| M08 执行状态循环 | S `motion-pulse-soft/attention`、spin/dots、真实 activity/status 消费 | V 只在真实非终态、不可见/后台停止无意义循环；状态文字和 reduce 静态 | P1 · E04/E16 |
| M09 加载/骨架/不定进度 | S `motion-progress-slide/shimmer`、页面 loading 分支 | V 真实读取/几何稳定；无总量不造百分比、无权限不永远 skeleton | P1 · E12/E15/E16 |
| M10 定位/引用短提示 | S `motion-flash` 与 BotConversation 高亮/ReplyAnchors | V 不抢回贴底、不持续闪烁，键盘/读屏有目标；失效引用有提示 | P1 · E05/E09/E16 |
| M11 对象缩向目标 | S `motion-exit-to-target`、Overlay closeTarget、VersionBadge pending | V 目标先接住、测量无效直接淡出；timer 不能把请求写成已下载 | P1 · E12/E16/E17 |
| M12 列表重排/塌缩 | S WorkStream FLIP、useShatterExitCollapse、局部列表/队列 | V 选择/锚点保持，用户拖动与真实删除分开，reduce 即时落位 | P1 · E05/E06/E16/E17 |
| M13 品牌启动 | S `brand-startup-*` 与 BrandStartupLoader/minHold | G10；就绪不为品牌固定等待，静态错误/恢复完整 | P1 · E12/E16/E17 |
| M14 头像凝视/呼吸/思考 | S `bot-avatar-*`、头像状态和 reduce CSS 重置 gaze | V JS 指针/帧任务/可见性与偏好变化，状态名不产生假行动权 | P1 · E15/E16 |
| M15 结果庆祝/粒子 | S `result-card-*`、`gwb-item-*`、ParticleShatterOverlay | G11；先短路减少动效的 JS 工作。真实签收与消失分开，重连不重复庆祝 | P1 降级 E16；P2 装饰 E14 |
| M16 图像缩放/拖动/尺寸 | S ImageLightbox fit/actual、分割条 rAF、浏览器挂载稳定 | G06/G08；V 手势直接跟随/取消原位、无 API/窄窗/键盘、reduce 不做平滑 | P1 · E06/E09/E16/E17 |
| M17 sheen/halo/ripple/glow 等存量基元 | S motion.css 中有这些定义；**定义存在不等于所有组件都在用** | V 新调用先解释理解收益、循环开销与静态终态；不扩散 blur/shadow/background 循环；逐字模糊不采用 | P2 增强 E14；存量降级 P1 E16 |
| M18 全局治理/偏好/API | S tokens 全局 reduce；集中 keyframe 架构检查；presence、Overlay、部分 WAAPI 各自处理 | G11/G12；V JS/WAAPI/smooth scroll、偏好变化/无事件/卸载。现有 checker 不覆盖所有语义/帧率/可达性 | P1 · E16/E13 |

需登记的执行顺序：真实状态变更 → 小范围呈现 → 幂等表现收尾。若实现中动画结束才写业务决定，先归到 E04 的事实边界处理，而非“微调曲线”。循环性能与帧率本轮没有测量，不承诺 GPU/120Hz。

## 4. 标准化过渡体系

编号与规范完全一致；组件状态模板 O/G/V/I 对每个来源和目标生效。

| ID / 全链路场景 | 当前来源→目标、状态和实现基础 | 缺口与必须保留 | 排程 / 任务 |
|---|---|---|---|---|
| T01 导航/换机器人/任务 | S BotListShell/任务现场/HistorySheet、经典 activePage、TUI view、remote selected | G01/G03；V 草稿/pending/选中身份/来源读位、旧响应隔离、失败回源可达 | P0 输入 E02；P1 E05/E11/E17 |
| T02 模态/抽屉/嵌套 | S Overlay/Drawer/focus scope、档案→现场→Evidence、confirm | V 初始/恢复焦点、最上层 Escape、背景边界、退场幂等和未保存选择 | P1 · E06/E17 |
| T03 菜单/提示/锚定 | S Dropdown/CascadingMenu/Tooltip、anchoredOverlay 与原生 QuickChat popover | G07；V 锚点消失/越界/滚动、不同窗口焦点与关闭 | P1 · E06/E11/E17 |
| T04 标签/分段/分区 | S SettingsPage、BotDrawerSegments、ResourceTabStrip、CapabilityTabs、模型面板 | G04/G05；V dirty 离开、方向键/tabpanel、昂贵读取手动激活、latest selection | P1 · E06/E08/E15/E17 |
| T05 折叠/展开/详情 | S SettingsDisclosureContent、BotProcess、ReplyDetails、问题 dismissal | G12；V 退出时焦点/hidden controls、反向/取消/无 API、用户折叠优先 | P1 · E05/E06/E16/E17 |
| T06 待发/接收/连续回复 | S useBotConversation pending/ack、UserBubble、ContinuousReply；remote 同 ID Map | G01/G02/G03；V 输入身份/引用附件恢复、晚到回执与历史静态 | P0 · E02/E03；P1 E16/E17 |
| T07 决策/执行/核验/交还 | S CardView/Receipt、lifecycle、TaskVerification、CompletionReview、Git handoff | V 六种事实分别投影；旧卡失效/提交失败、接收决定不等成功、部分结论第一层 | P0 · E04；P1 E17 |
| T08 列表增删/排序/分页 | S BotList/TasksTab/Memory/Files、MessageQueue、WorkStream/virtual pager | G09；V 刷新/分页失败保数据、选中删除归处、拖动撤销/读位不跳 | P1 · E05/E06/E10/E17 |
| T09 预览/分栏/最大化 | S ImageLightbox/Document/Browser、WorkbenchResize、档案 push/cover | G06/G08；V 源对象/焦点/缩放/滚动、guest 不误销毁、支持检测/普通打开 fallback | P1 · E06/E09/E17；共享元素 P2 E14 |
| T10 启动/主题/升级/宿主恢复 | S bootstrap/minHold、AppearanceProvider、VersionBadge/updater、host lease/恢复投影 | G10；V 内容就绪即用、主题变更保编辑、窗口关闭不取消、未知执行不重放、徽标先承接 | P1 · E11/E12/E16/E17 |

## 5. 发布验收与进度记账

E15–E17 的实现卡必须引用本表 U/M/T 编号和对应 P/C 行，写明允许文件、状态事实源、已有 seam、取消恢复与降级。一个实际修改可同时关闭多行的同一差异，但不能只改共享 CSS 就把所有消费者标成达标。

进度字段使用：已登记 → 待实现 / 待核 → 实现已审阅 → 候选验证通过（绑定 source/包/证据）。S 不是流程状态；文档提交只完成“已登记”。隐藏/兼容入口注明范围，暂不实现的例外有退出条件，不标 Pass。

普通任务只审阅内容/diff；不自动跑测试、截图、构建或类型/架构/IPC 检查。发布时按 E13 和[验收指南](../../playbook/v0.1.0/acceptance-test-guide.md)将本表映射到既有场景，补没有覆盖的键盘/焦点/IME/取消/减少动效/API 降级及宿主验证，再在合并全部 PR 的最终候选运行完整门禁。不能用截图数量或旧版本 Pass 代替这些行为证据。
