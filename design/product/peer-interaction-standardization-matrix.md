# Peer 全产品交互状态覆盖矩阵

创建时间：2026-10-23
最后更新：2026-10-23

> 状态：全产品源码登记与改造依据，未完成全产品实机验收。纳入[当前改造计划](peer-product-renovation-plan.md) E00–E17。
> 规范：[体验/UI](../../knowledge/specifications/peer-product-experience-standard.md)、[人机交互](../../knowledge/specifications/peer-human-agent-interaction-contract.md)、[动效](../../knowledge/specifications/motion-system.md)、[过渡](../../knowledge/specifications/transition-system.md)。UI、动效与过渡的专门覆盖见[体系覆盖表](peer-ui-motion-transition-matrix.md)。

## 1. 覆盖边界和证据口径

源码固定为代码仓 `cb2f5695ea164fec7a291570c27c640217c98f1b`，是本地组合，**不是已发布候选**。排除工作区未提交 CSS、AGENTS 和其他任务文件。远端发布/在途精确 head 的区别沿用[改造计划 §2–3](peer-product-renovation-plan.md)，本表不声明又产生了新发布。PR198 最新 head 不在这份源码中，不能把其最新修复记成已集成。

登记 Desktop renderer 全部 **201 个非测试 TSX 模块**，包含 **348 个具名函数/导出声明**（包括内部子组件、图标、Provider、包装与启动装配，不能说成 348 个独立页面）。每个模块均在 §5 有独立行，同文件子组件随该行登记；其异步、焦点、布局依赖的 TS/MJS/CSS seam 在 §3、§6 和体系覆盖表另列。另登记 TUI 全部非测试 TSX、CLI/ACP、Gateway 两套网页、托盘/通知/窗口等原生入口。

“整个产品”指现有客户端及现有可达/兼容/隐藏实现，不把规划中的团队、市场新能力、远程批准、远程附件列成已存在页面。已有 Skills 市场入口属于现有能力；“机器人模板市场”仍是未来范围。测试夹具、截图脚本和历史 Demo 不是生产页面。

| 标记 | 含义 | 不能推导 |
|---|---|---|
| S | 静态源码看到了相应分支/调用/共享接口 | 不等于交互、像素或辅助技术已通过 |
| G01–G12 | §3 指定的源码可确认差异/恢复风险 | 不等于已复现实机事故或判定缺陷严重度 |
| V | 需要在发布候选核对；行内写明具体边缘 | 不能标 Pass，也不能当作确定缺陷 |
| N/A | 对组件语义不适用，并由状态模板解释 | 不能用来跳过适用状态 |
| 隐藏/装配/兼容 | 保留登记，但不算默认公开入口 | 不代表默认用户会看到 |

P0/P1/P2 是**改造排程**，不是 bug 严重度；发布门槛沿用现有规则。凡表内 V 项都由 E13 在该项进入发布范围时取得证据，工作包只列改造责任，不表示本轮已执行。

## 2. 状态模板：每行都适用，不靠只画默认态交付

基础状态：N 默认、H hover、P pressed、F focus-visible、S selected/checked、D disabled/unavailable、B busy/submitting、Ø empty、L loading、X error、T stale/expired/outcome-unknown、R recovery/retry。`T` 不与过渡编号 T01–T10 混用。

| 模板 | 必须评估的状态与行为 | 不适用项 |
|---|---|---|
| A 动作 | N/H/P/F/D/B/X/R；危险动作的确认、取消及副作用未知 | 无选值的按钮 S；无取数的按钮 Ø/L/T，若异步则补入 |
| F 编辑/配置 | N/H/P/F/D/B/L/X/T/R；编辑/dirty/invalid/保存/还原/离开未保存；IME；有选值则 S | 非集合 Ø；不支持的操作不虚构按钮 |
| Q 列表/搜索/选择 | N/H/P/F/S/D/B/Ø/L/X/T/R；键盘、筛选无结果、分页、选中对象消失 | 单纯容器自身 H/P/F，由其行/控件承接 |
| I 委托输入 | N/H/P/F/D/B/Ø/L/X/T/R；composition、引用/附件、排队、接收回执、未知去重、草稿恢复、停止与取消区别 | 输入框自身 S；模型选择等子控件另用 Q/F |
| V 阅读/进程/结果 | N/Ø/L/X/T/R；跟随/历史/定位/晚加载、流式/停止/核验/部分结果；内含动作适用 A | 纯正文 H/P/F/S/D/B；读屏状态不能每 token 广播 |
| O 浮层/窗口 | N/L/X/T/R；打开/关闭/反向/嵌套/背景刷新/卸载；按语义决定 modal；焦点进出、Escape、窄窗、减少动效 | 遮罩自身 S/D/B；内部控件单独采用模板 |
| G 手势/几何 | N/H/P/F/S/D/X/R；死区、capture、越界、取消/失焦/卸载、键盘替代、复原 | 纯手势 Ø/L/B/T；若保存布局异步则补 B/X/T/R |
| R 只读显示/图标 | N；数据读取时补 Ø/L/X/T/R；信息层级/长值/主题/放大 | 纯装饰 H/P/F/S/D/B；装饰图标 aria-hidden，交互由外层命名 |
| H 宿主/装配 | bootstrap、连接、权限不可用、租约、恢复、关闭、错误；保留静态入口与真实事实 | 无独立界面者 H/P/F/S 为 N/A；消费者负责动作状态 |

矩阵的“源码已有”只列实际看到的机制；模板中其余适用状态默认 **V**。这让每个状态有去向，同时避免把没有逐一实测的 12 个状态预填成已完成。表中“检查”均指日常实现/diff 审阅或发布时验证，不新增日常回归门槛。

## 3. 已确认的源码差异与优先修复

结论以 §1 固定源码为准；链接选用已推送、且该文件 blob 与本地组合完全相同的 RC26/PR 来源，避免给出未推送 merge commit 的不可达链接。结论限列出的路径。

| ID / 排程 | 当前实现与缺口 | 改造任务 / 静态退出条件 |
|---|---|---|
| G01 / P0 | [BotComposer](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/project-agent/conversation/BotComposer.tsx) 发起 void onSend 后立即清空文本/附件；BotConversation 按 workspaceId 重建；useBotConversation 虽已有 inputId/失败重试，但切换时清 pending | E02：正文、引用、附件、未确认发送按机器人有恢复责任；不能误称所有失败都丢失。新增持久边界先 ADR |
| G02 / P0 | [QuickChatWindow.submit](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/app/components/QuickChatWindow.tsx) bot 路径成功回执后才清草稿，已有保护；但 inputId 在每次 submit 内重新生成。未知送达后人工重试缺少同 ID 延续 | E02/E11：保存待确认 envelope 与目标，未知重试同 ID；不把“可能重复接收”的风险写成已复现重复副作用 |
| G03 / P0 | [TUI ProjectApp](https://github.com/ly-ccx/Peer-Agent/blob/c8423eb2d55c8c6cf6029fe30053e42b1ca40730/apps/tui/src/project-agent/ProjectApp.tsx) textarea 先 clear 再 submit；普通文本调用 client.submit 后固定返回 ok，未使用其 receipt，异常只给 notice。client 本身已有真实同步队列回执 | E02/E11：消费真实 receipt，失败恢复编辑文本与输入身份；项目输入与经典 composer-submit 分开处理，不能用 PR198 普通 composer 修复代替 |
| G04 / P1 | [SystemInstructionsPanel](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/app/components/SystemInstructionsPanel.tsx) 读取/保存 catch 静默，无可见失败；本地 draft 与 SettingsPage 的 key={section} 重挂载没有共同的离开未保存契约 | E08/E17：保存失败明确反馈且保住编辑；分区切换先处理 dirty；不改变既有 System Context 准入路径 |
| G05 / P1 | [CapabilityTabs](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/capabilities/components/CapabilityTabs.tsx) 有 role=tab/selected，但无方向键/roving；[ResourceTabStrip](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/workbench/ResourceTabStrip.tsx) 有 roving tabIndex 但无方向键，非活动页选择按钮不能经普通 Tab 进入；二者本地也未提供 panel ID 关联 | E06/E15：先统一 tabs/radio 语义、键盘与 panel 关联，再统一指示器；BotDrawerSegments 已有方向键，保留复用 |
| G06 / P1 | [SidebarResizer](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/workbench/SidebarResizer.tsx) 有键盘/双击/rAF，但当前指针路径只注册 move/up，无 pointercancel/blur/卸载收尾；右 WorkbenchPanel 已有 capture/cancel/blur/lostcapture，cancel 仍沿用提交宽度收尾，未提供 Escape 撤销 | E06/E17：共享拖动会话收尾，区分提交与撤销；清 cursor/userSelect/监听/帧；分隔条补值范围语义。不能把左右都描述成没有键盘或没有 cancel |
| G07 / P1 | [Tooltip](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/app/components/Tooltip.tsx) 有 hover/focus、describedby、定位清理；没有 Escape 关闭入口，anchor mouseleave 立即 hide，内容 hover 保持无承接 | E06/E15：补可关闭/可保持的提示契约，合并原 describedby；主操作不能只靠 tooltip 命名 |
| G08 / P1 | [ImageLightbox](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/chat/components/thread/ImageLightbox.tsx) 共享 Overlay、适应/原尺寸已存在；缺加载失败/onError 分支，路径读取无图时仍为 Loading，复制失败无提示 | E09/E15：缺失/读取失败/解码失败与真 loading 分开；复制/打开失败可恢复。保留现有共享灯箱，不重做图片系统 |
| G09 / P1 | [MemoryTab](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/project-agent/drawer/MemoryTab.tsx) 有筛选/分页/编辑/撤回/恢复，但初始读取 catch 设空数组，无法区分读取失败与真空；多项写入只 then(reload)，缺统一失败/处理中表达 | E10/E15：保留来源与草稿，补读取错误和逐项写入回执/恢复；不把记忆提升为权限或 Evidence |
| G10 / P1 | [useBrandStartupMinHold](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/app/state/useBrandStartupMinHold.ts) 常规偏好强制 2200ms 品牌展示，App 以它和 session 联合放行；减少动效已立即放行。与“内容就绪不为动画延迟可用”有差异 | E17：将实际 bootstrap 与品牌表达分开，保留启动/错误反馈，不追加人为等待；性能与实际体感留发布取证 |
| G11 / P1 | [ParticleShatterOverlay](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/app/fx/ParticleShatterOverlay.tsx) 和执行函数未读减少动效；CSS 虽隐藏 canvas，仍会采样/运行 JS rAF；调用方在 shattering 时仍激活组件 | E16：减少动效短路采样/循环，保留实际结果与一次收尾；粉碎本身属可选 E14，修降级不等于推广特效 |
| G12 / P1 | [useQuestionDismissal](https://github.com/ly-ccx/Peer-Agent/blob/3583d06a971f16bcf8f0b23090bc452f2b21e08a/apps/desktop/renderer/src/project-agent/conversation/useQuestionDismissal.ts) 已测量折叠并支持减少动效；直接 node.animate，无 API 缺失短路，finished 拒绝被忽略且无独立 fallback | E16/E17：无 API、取消/拒绝和卸载皆有幂等静态收尾；动画不能决定问题的运行时已解决事实 |

IME 已有 isComposing/Process 保护，不宣告“中文必然误发”。Overlay 已有最上层处理、focus scope、减少动效与超时兜底；其重复关闭幂等和焦点交回时点列 V，不宣告已产生双重提交。透明合成、200% 放大、对比度、读屏、帧率、安装与真实模型，本轮均未实测。

## 4. 逐页面/产品入口矩阵

源码路径以下均相对于代码仓；`r/` 代表 `apps/desktop/renderer/src/`。模板含全部适用状态，页面内容和对应子组件共同承担。每行 V 均纳入 E13。

| ID / 页面或入口 | 模板 / 当前实现与事实来源 | 缺口/待核边缘 | 排程 / 改造任务 |
|---|---|---|---|
| P01 启动、失败恢复、OS 权限门 | H/O；App、AppErrorBoundary、FullDiskAccessStartupGate，bootstrap/OS IPC | G10；V 权限不可用/重试/窗口关闭/静态终态 | P1 · E12/E17 |
| P02 首启/升级引导/经典迁移提示 | O/F；project-agent/onboarding、设置 shell 事实 | V 无模型/取消/返回/重复进入，不能误写迁移完成 | P1 · E08/E11 |
| P03 新建机器人/绑定目录 | F/O；NewBotSheet、BotListShell，新建 lifecycle 回执；含 PR200 本地切片 | V 名称无效/重名/受管目录/已有项目/失败保留 | P1 · E01/E08 |
| P04 机器人列表/搜索/行操作 | Q；BotList/BotRow、useBotList 与目录投影 | V 空/无结果/归档/对象删除/长名称/键盘选择 | P1 · E04/E07 |
| P05 需要你筛选与清单 | Q/O；AttentionSheet、projectAgentListAttention | V 计数与原卡一致、过期/迟到决定、读失败不变空 | P0 · E04 |
| P06 主机器人对话 | I/V；BotConversation、useBotConversation、受管输入回执与公共交互读取 | G01；V 切换/刷新/停止/失败/恢复、阅读意图 | P0 · E02/E03/E05 |
| P07 授权/计划/问答/项目熟悉 | A/F/V；CardView、ApprovalReceipt、结构化卡与决定 API | V 拒绝/失效/重复点/自由回答/范围变化；G12 的折叠降级 | P0 · E04/E16/E17 |
| P08 档案框架与五个标签 | O/Q；BotProfileDrawer、Drawer、分栏/覆盖布局与 tab 记忆 | V resize/反向/嵌套/已消失 trigger；保留草稿 | P1 · E06/E17 |
| P09 档案·概况 | V/A；OverviewTab、profile、宿主/模型解析 | V 无模型/来源不可用/打开目录失败/长路径 | P1 · E08/E12 |
| P10 档案·任务 | Q/A；TasksTab、sessions、生命周期 cancelable | V 空/加载/过期报告、取消失败、历史与当前分组 | P0 · E04/E12 |
| P11 任务详情/原任务现场 | O/V/I；SessionDetail/ConversationSceneDrawer、useTaskReport 与 ChatSurface | V stale/未知报告、关闭回原卡、草稿/定位不丢 | P0 · E04/E05/E09 |
| P12 核验/签收/CompletionReview | V/A；TaskVerification、CompletionReview，核验 detail 与实际签收 | V passed/partial/failed/unverifiable、旧 attempt/迟到结果；不隐藏限制 | P0 · E04/E09 |
| P13 回复过程/协调/记忆上下文 | O/V；ReplyDetails/AgentProcessView/CoordinationDetails/ReplyContext | V 收起后持续更新、读失败、返回回复锚点 | P1 · E05/E06/E10 |
| P14 Evidence 明细/文件/失效引用 | V/O；EvidenceView/EvidenceList、projectAgentReadEvidence | V 无权限/缺文件/过期、Evidence 与 artifact 区别 | P1 · E09 |
| P15 档案·目标 | F/Q；ObjectivesTab、objectives/automation 投影 | V 未保存/暂停恢复/触发不可用/关闭后重开 | P1 · E10/E17 |
| P16 档案·记忆 | F/Q；MemoryTab、memory CRUD 与 switches | G09；V 来源/冲突/忘记恢复/编辑被刷新覆盖 | P1 · E10/E15 |
| P17 档案·设置/权限/模型/宿主 | F；BotSettingsTab/BotAccessControl/BotHostControl、受管设置与策略 | V 当前值/作用域/保存失败/接管失败/删除后归处 | P0 决策 / P1 配置 · E04/E08 |
| P18 历史清单/预览/继续 | Q/O/V；HistorySheet/HistoryConversationList、listHistory/continueHistory | V 搜索无结果/分页/读取失败/重复继续/身份保持 | P1 · E05/E11/E12 |
| P19 项目诊断 | V/A；ProjectDiagnosticsPanel、诊断报告 IPC | V 生成/复制失败、报告缺失、敏感值展示边界 | P1 · E12/E15 |
| P20 经典壳/侧栏/项目编辑 | Q/F；Sidebar/EditProjectDialog、workspace 与 conversation store | V 重命名/归档/移除/切换的草稿和焦点；保留兼容 | P1 · E06/E11 |
| P21 经典对话/Composer/队列 | I/V/G；ChatSurface、ComposerDraftControls、MessageQueue、composerPersistence | V IME/补全/排队改序/失败恢复/停止作用域 | P0 输入 · E02/E03/E05/E11 |
| P22 经典 Goal/批准/验证/调查 | V/A/F；GoalPlanPanel/goal 子组件、GoalPlan/runner/structured interaction | V 计划/执行/核验/签收不混；失效决定与重连 | P0 · E04/E11 |
| P23 经典工作台雷达/任务/历史 | Q/V；HomePage→GlobalWorkbenchPage、TaskOverviewPage、TasksPage/HistoryPage | V 老消费者真值对齐、签收与交回文案；G11 | P1 · E04/E11/E16 |
| P24 经典结果/Git 交回/冲突处理 | V/F/A；ConversationResultView/SourceCheckoutPanel/HandoffConflictPanel | V diff失败/冲突重试/提交未知、操作成功与关闭分开 | P0 事实 / P1 控件 · E04/E09/E17 |
| P25 选区对话/引用/子任务 | I/O；SelectionChatWorkspace/SelectionQuoteAction、持久子会话与 quote refs | V 原文失效/返回定位/已有草稿/保存失败/权限边界 | P1 · E02/E05/E09 |
| P26 Quick Chat 独立窗口/原生弹选 | I/O/Q；QuickChatWindow/PopoverHost、窗口 IPC 与受管发送 | G02；V bot 文本限制、经典附件、Escape/IME、切换对象草稿 | P0 · E02/E03/E11 |
| P27 全局/会话搜索/页内查找 | Q/O；ConversationSearchPalette/ChatFindBar、搜索 API/当前文本 | V 旧请求/无结果/不可搜索内容/原消息定位和返回 | P1 · E05/E06 |
| P28 设置框架/搜索/返回 | Q/F；SettingsPage，分区导航非跨面板全文搜索 | G04；V 空结果、section deep-link、脏编辑离开 | P1 · E08/E17 |
| P29 设置·通用/主动性/通知 | F；GeneralPanel、getSettings/updateSettings | V 保存与回读/静音时段/不可用设置/送达事实 | P1 · E08/E10 |
| P30 设置·外观 | F/G；AppearanceProvider/Panel/Slider/PaletteSelect | V 深浅/注册主题/字号/实色/重开回读、视口不重置 | P1 · E07/E15/E17 |
| P31 设置·个性化 | F；SystemInstructionsPanel、既有设置入口 | G04；保存失败/未保存离开；不新增系统注入路径 | P1 · E08/E17 |
| P32 设置·快捷键 | F；ShortcutsPanel、录制/冲突/注册状态 API | V 组合键/IME/取消录制/冲突/注册失败/恢复默认 | P1 · E03/E06/E08 |
| P33 设置·服务商/渠道/模型 | F/Q/O；LlmSettingsPanel、ConfiguredModelRow、目录与模型弹层 | V 发现/手动模型/凭据/OAuth/配额失效/保存失败与草稿 | P1 · E07/E08 |
| P34 模型/强度/请求通道弹层 | F/Q/G；ModelSelectionPanel/BotModelControls、角色模型解析；含 PR197 | V 当前/继承/预览/下轮生效/失败回退、长值与窄窗 | P1 · E01/E07/E08 |
| P35 设置·模型分工/视觉兜底 | F；ModelRoutingPanel/FallbackVisionSetting、router preview/update | V 继承来源、缺渠道、关闭/保存失败、配置不改当轮快照 | P1 · E08 |
| P36 设置·用量/账号明细 | Q/V；UsageStatsPanel/AccountUsageDetails、用量/订阅 quota | V 空/过期/请求失败/未知单位、图表键盘替代 | P1 · E08/E15 |
| P37 设置·Git | F；GitPanel、当前 workspace 配置 | V 无项目/非法前缀/保存失败/dirty 离开 | P1 · E08/E17 |
| P38 设置·开发/宿主调试 | F/H；DeveloperPanel/BotHostDeveloperControl | V 无 bot/租约冲突/接管失败；不把调试能力当默认授权 | P1 · E08/E12 |
| P39 设置·远程访问/配对 | F/O/Q；RemoteAccessPanel/Pairing、gateway/controller 投影 | V 绑定/过期码/离线/撤回/作用域/复制失败 | P1 · E08/E11 |
| P40 设置·更新与关于/版本徽标 | V/O/A；UpdatesPanel/UpdateModal/VersionBadge、updater phase | V 请求与真实下载分开、失败/重试/关闭/目标消失；T10 | P1 · E12/E17 |
| P41 设置·已归档 | Q/A；ArchivedConversationsPanel、持久 archive/restore/delete | V 空/失败/删除确认/恢复回原对象/焦点 | P1 · E06/E11 |
| P42 能力总览/Skills/MCP 标签 | Q/V；CapabilitiesPanel/CapabilityWorkbench/CapabilityTabs | G05；V 清单读取失败与空；Manifest 不等于当前 Projection | P1 · E06/E08/E15 |
| P43 已安装 Skills/详情/上传 | Q/F/O；SkillsInstalledPanel/SkillDetailDialog/SkillUploadDialog | V 作用域/启停/卸载/压缩包失败/链接项目/取消 | P1 · E08/E09 |
| P44 Skills 市场/分类/安装 | Q/F；SkillMarketplacePanel/QoderMarketplacePanel、服务端列表/安装 | V 网络失败/无结果/旧搜索/安装回执/目标项目 | P1 · E08/E09 |
| P45 MCP 配置/认证/资源/Prompt | F/Q/O；McpSettingsPanel、安装/OAuth/credentials/manifest API | V 连接失败/认证过期/刷新能力/读取资源失败；不把外部内容当指令 | P1 · E08/E09 |
| P46 自动化清单/编辑/提案 | Q/F/A；AutomationCenter/AutomationProposalCard、automation API | V 未保存/冲突时区/暂停/删除/提案过期与后台失败 | P1 · E10/E17 |
| P47 自动化详情/运行记录/回执 | Q/V/A；AutomationDetail/RunsTable/RunReceipt，同一 AutomationCenter 内 | V 空/分页/取消/重试未知/原任务入口/静音 | P1 · E10/E12 |
| P48 Workbench 框架/标签/分栏 | O/Q/G；WorkbenchContext/Panel、稳定 browser 挂载与 resize stage | G05/G06；V 最大化/窄容器/快捷键/原上下文返回 | P1 · E06/E17 |
| P49 文件树/新建/筛选 | Q/F；FilesView/TreeNode、受管 readDir/watch/mkdir/write IPC | V 无权限/并发刷新/重名/失败保留名称/键盘树 | P1 · E06/E09 |
| P50 文档/源码/Markdown/diff | V/Q/O；DocumentView/SourceViewer/MarkdownDocument/DiffViewer | V 缺失/过大/二进制/解码失败/行定位/局部横滚 | P1 · E05/E09 |
| P51 图片附件/Markdown 图片灯箱 | V/O/G；共享 ImageLightbox、BotAttachments/AttachmentStrip | G08；V 缩放/返回/读取失败/晚加载/窄窗 | P1 · E09/E17 |
| P52 浏览器标签/导航/页面错误 | Q/F/H；BrowserView/BrowserPage、webview 事件与受管 browser API | V 加载/崩溃/重试/外部打开/页面与宿主键盘边界 | P1 · E06/E09/E12 |
| P53 浏览器会话导入/密码管理 | F/O/Q；SessionImportWizard/PasswordManagerPanel、凭据/OS 权限服务 | V OS 权限/锁定/取消/部分导入/揭示失败；保密信息不入普通日志 | P1 · E08/E09 |
| P54 后台运行/终端输出/停止 | Q/V/A；BackgroundRuntimePanel/BackgroundThreadsView/TaskMonitorRailView | V 无结果/截断/停止失败/未知回执/回原任务；无 renderer 执行旁路 | P1 · E04/E09/E12 |
| P55 原生托盘/系统通知/窗口关闭 | H/A；electron/main/tray-controller、task-notification-broker、window-routing | V 同一行动权去重/通知点回原任务/关窗继续/静音 | P1 · E10/E11/E12 |
| P56 TUI 首次绑定 | H/F；ProjectApp bind、共享 registry/lifecycle/lease | V 同意/拒绝/取消/原目录失效、进入经典清理 | P1 · E08/E11 |
| P57 TUI 机器人列表 | Q；ProjectApp bots/BotListView、公共目录快照 | V 空/读失败/长名称/方向键/终端 resize | P1 · E06/E11 |
| P58 TUI 主对话/输入 | I/V；ProjectApp conversation/BotConversationView、公共交互/真实输入队列 | G03；V 草稿/未知回执/读位、非宿主限制 | P0 · E02/E03/E11 |
| P59 TUI 卡片选择/回答 | A/F/Q；ProjectApp cards/CardLine、编号与 card-actions | V 旧编号/失效决定/自由回答/键盘切换、非宿主回电脑批准 | P0 · E04/E11 |
| P60 TUI 任务列表 | Q；ProjectApp tasks、snapshot.sessions | V 空/读失败/状态更新、序号变化与原 session 身份 | P1 · E04/E11 |
| P61 TUI 任务详情 | V；ProjectApp task、supervisor report/detail | V 部分/未知核验、Evidence 引用、回原列表 | P0 事实/P1 入口 · E04/E09/E11 |
| P62 TUI 记忆 | Q/V；ProjectApp memory、host.memory.list | V 来源/冲突/错误与空；不支持编辑不虚构控制 | P1 · E10/E11 |
| P63 TUI 项目目标 | Q/V；ProjectApp objectives、host.objectives.list | V 暂停/等待/触发不可用的读数、回原对话 | P1 · E10/E11 |
| P64 TUI 诊断 | V；ProjectApp diagnostics、恢复卡诊断记录 | V 当前/历史故障区别、长内容和终端宽度 | P1 · E11/E12 |
| P65 TUI 帮助/命令反馈 | V/I；ProjectApp help、parseProjectCommand/project-copy | V 非法命令/无卡片、命令不被误作用户任务、返回焦点 | P1 · E03/E11 |
| P66 TUI 经典模式 | I/Q/V；app.tsx、command-registry、composer-submit 等 | V Enter/LF/kpenter、草稿/队列/权限/退出清理；最新 PR198 head 未集成 | P0 输入/P1 其余 · E01/E03/E11 |
| P67 CLI 帮助/版本/参数错误 | H/V；index.tsx/cli-argv/cli-version/cli-exit | V 非 TTY、无效参数/退出码、版本来源；图形交互态 N/A | P1 · E11 |
| P68 CLI headless exec | H/V；cli-exec/cli-exec-goal/cli-output、shared Runtime | V text/json 与 stderr、权限不足/SIGINT/超时/部分结果；不假成功 | P1 · E04/E11/E12 |
| P69 CLI 更新/安装反馈 | H/V；cli-update、npm-cli 的平台/安装/更新入口 | V 无适配平台/网络/权限/校验失败、版本回读；不动个人运行实例 | P1 · E11/E12 |
| P70 ACP stdio | H/V；acp/stdio/agent/permission/updates | V 请求取消/断开/批准与结果语义；机器协议入口无图形 UI 态 | P1 · E04/E11 |
| P71 远程登录/退出/会话过期 | F/H；gateway/web-surface、账号会话 API | V 过期/旧响应隔离/退出未确认、清除私有视图 | P1 · E11/E17 |
| P72 远程设备/配对 | F/Q；web-surface、device/pairing API | V 过期码/离线/撤回/重复提交、键盘/触控 | P1 · E11/E15 |
| P73 远程传统任务读取 | F/V；web-surface 的 task-read、remote-task API | V 未授权/未知任务/离线/部分结果、返回原来源 | P1 · E04/E11 |
| P74 远程机器人列表 | Q；project-web-surface 的公共授权项目/设备列表 | V 空/读失败/撤权/长名，导航选中真实身份 | P1 · E11/E15 |
| P75 远程对话/历史分页 | V/Q；project-web-surface 的 role=log、readConversation 与游标 | V 加载更早保阅读锚点、软键盘/读屏、失败不抹草稿 | P1 · E05/E11/E17 |
| P76 远程任务内联详情 | V/O；project-web-surface readTask、taskGeneration/关闭详情 | V 旧请求隔离、缺报告/核验限制、焦点回合理触发点 | P1 · E04/E11/E17 |
| P77 远程发消息 | I；已有按目标 drafts/pending Map、同 inputId 未知重试与 received 回执 | V 刷新/登出内存清除是现有限制；4000字/无附件，批准仍回电脑；不新增远程能力 | P1 · E02/E11/E15 |
| P78 隐藏/兼容/诊断性组件 | R/H；AppshotsPanel 不在设置导航；CapabilityInventory 等旧源保留 | V 维持隐藏与合法 deep-link 回退；未来开放先立卡，不算当前公开页 | P2 · E00/E11 |

## 5. 逐组件源码登记与状态责任

以下每行包含该文件的具名子组件；纯 helper/icon 声明保留是为防漏，不代表都独立呈现。`r/` 路径固定为 §1 版本，源码已有栏是静态分支/事实接口摘要，**没有标注的适用状态都是 V**。行内未出现 G 的“待核”不是确定缺陷。E13 承担所有行的发布验证映射，其他 E 号承担改造。

| ID / 源码（r/ 前缀）与具名子组件 | 状态模板 / 源码已有机制与事实 | 差异或具体待核项 | 排程 / 改造任务 |
|---|---|---|---|
| C001 · `App.tsx`<br>`App`, `MainApp` | H/O · S 主窗口/Quick Chat 分流，默认机器人壳和经典页/结果抽屉装配；接口：`chatStreamListActive`, `clearPendingTask`, `conversationsArchive` 等 | G10；待核导航保留草稿、结果与窗口目标 | P1 · E11/E12/E17 |
| C002 · `app/components/AccountUsageDetails.tsx`<br>`AccountUsageDetails` | V · S 受控 quota 明细/加载/过期信息；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核未知额度与过期不写成零，重试入口和长值 | P1 · E08/E15 |
| C003 · `app/components/AppErrorBoundary.tsx`<br>`AppErrorBoundary` | H/A · S 渲染失败保留错误详情与 Reload；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核重载说明与保住的数据、无主题依赖的可读兜底 | P1 · E12/E15 |
| C004 · `app/components/AppshotsPanel.tsx`<br>`AppshotsPanel` | F · S 截图权限、热键、OS 设置入口；当前设置导航隐藏；接口：`appshotCapture`, `appshotOpenScreenSettings`, `appshotPermissionStatus` 等 | 隐藏保留；未来开放前核对录屏权限/失败/热键冲突 | P2 · E00/E11 |
| C005 · `app/components/ArchivedConversationsPanel.tsx`<br>`ArchivedConversationsPanel` | Q/A · S 归档读取、恢复/删除、pendingId/error 与确认；接口：`conversationsDelete`, `conversationsList`, `conversationsRestore` | 待核删除失败保留原项、恢复定位、空与读失败 | P1 · E06/E11 |
| C006 · `app/components/BotTargetPicker.tsx`<br>`BotTargetPicker` | Q · S 受控机器人目标选择与 disabled；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核长名/无目标/目标被删、跨 bot 编辑归属 | P1 · E08/E15 |
| C007 · `app/components/BotTimeField.tsx`<br>`BotTimeField` | F · S 受控时间字段/禁用，供策略设置消费；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核非法时间/键盘/时区说明与提交失败 | P1 · E10/E15 |
| C008 · `app/components/BrandStartupLoader.tsx`<br>`BrandStartupLoader` | R · S 品牌启动显示，不是 bootstrap 成功源；事实：受控 props / 所属 hook（装配模块由子树承接） | G10；待核静态/错误态与主内容就绪交接 | P1 · E16/E17 |
| C009 · `app/components/BrandWordmark.tsx`<br>`BrandWordmark` | R · S 品牌字标 SVG/文字表达；事实：受控 props / 所属 hook（装配模块由子树承接） | 纯显示交互态 N/A；待核主题/放大和装饰命名 | P2 · E15 |
| C010 · `app/components/CapabilitiesPanel.tsx`<br>`CapabilitiesPanel` | H/Q · S listCapabilities 后交 CapabilityWorkbench，失败退空；接口：`listCapabilities` | 待核清单失败是否须单独提示；不把其空等同 Skills/MCP 空 | P1 · E08/E15 |
| C011 · `app/components/CapabilityInventory.tsx`<br>`CapabilityInventory` | R/Q · S 能力清单的旧展示实现；事实：受控 props / 所属 hook（装配模块由子树承接） | 兼容/引用可达性待核；Manifest 与 Projection 含义不可混 | P2 · E00/E11 |
| C012 · `app/components/CascadingMenu.tsx`<br>`CascadingMenu` | Q/O · S portal 定位、分组/子菜单 active 索引与键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核嵌套 Escape、空/禁用项、锚点卸载与焦点恢复 | P1 · E06/E17 |
| C013 · `app/components/ConfiguredModelRow.tsx`<br>`ConfiguredModelRow` | F/A · S 受控模型行、编辑/错误/删除等操作；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核长模型名、保存中防重入、单行错误与焦点 | P1 · E07/E08 |
| C014 · `app/components/ConfirmProvider.tsx`<br>`ConfirmProvider` | O/A · S 共享确认请求与模态，替代 native confirm；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核危险动作初始安全焦点、并发请求与重复关闭 | P1 · E06/E17 |
| C015 · `app/components/ConversationResultView.tsx`<br>`ConversationResultView`, `AcceptanceArtifactButton` | V/A · S GoalPlan、diff、artifact 按实际 API 读取；接口：`gitDiffRange`, `goalPlansGet`, `goalPlansList` 等 | 待核取数失败/部分证据、签收和交回分开、回原任务 | P0 · E04/E09 |
| C016 · `app/components/Drawer.tsx`<br>`Drawer` | O · S 共享抽屉包装；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核各调用方正确 modal/非 modal、关闭与读位恢复 | P1 · E06/E17 |
| C017 · `app/components/Dropdown.tsx`<br>`Dropdown` | Q/O · S 搜索/分组/activeIndex、portal 与键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核无结果/已选项消失/长值/关闭恢复焦点 | P1 · E06/E15 |
| C018 · `app/components/FallbackComposer.tsx`<br>`FallbackComposer` | I · S 降级输入包装与受控提交；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核降级状态不误发、失败保草稿、禁用有原因 | P0 · E02/E03 |
| C019 · `app/components/FallbackRuntimeView.tsx`<br>`FallbackRuntimeView` | V · S 降级 Runtime 信息展示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核不可用/恢复与真实执行结果区分 | P1 · E04/E12 |
| C020 · `app/components/FallbackVisionSetting.tsx`<br>`FallbackVisionSetting` | F · S 展开式视觉兜底设置、saving 反馈；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核缺渠道/保存失败/折叠时焦点与隐藏内容 | P1 · E08/E17 |
| C021 · `app/components/FullDiskAccessStartupGate.tsx`<br>`FullDiskAccessStartupGate` | H/O · S OS 权限快照、打开系统设置、拖应用入口与错误；接口：`getStartupOsPermissions`, `openFullDiskAccessSettings`, `startAppDrag` | 待核权限不可用/往返/取消拖动/无 API、后台不抢焦点 | P1 · E08/E12/E17 |
| C022 · `app/components/GeneralPanel.tsx`<br>`GeneralPanel` | F · S locale、回复语言、主动性/安静时段等设置读写；接口：`getSettings`, `initialSettings`, `setLocale` 等 | 待核逐项保存竞态、非法时间、回读、离开编辑与静音作用域 | P1 · E08/E10 |
| C023 · `app/components/GitPanel.tsx`<br>`GitPanel` | F · S 分支前缀编辑与 savedPrefix/error；接口：`initialSettings`, `updateSettings` | 待核无 workspace、非法值、保存失败和未保存切换 | P1 · E08/E17 |
| C024 · `app/components/HandoffConflictPanel.tsx`<br>`HandoffConflictPanel` | F/V · S 冲突选择、预览、busy/error 与 resolve API；接口：`goalPlansCleanupHandoffPreview`, `goalPlansPreviewHandoffMerge`, `goalPlansResolveHandoffConflicts` | 待核旧预览失效/部分失败/重复提交、关闭保留已发生事实 | P0 · E04/E09 |
| C025 · `app/components/LlmBrandIcon.tsx`<br>`LlmBrandIcon` | R · S 模型服务商图标；事实：受控 props / 所属 hook（装配模块由子树承接） | 纯装饰操作态 N/A；待核 fallback/SVG 和外层名称 | P2 · E15 |
| C026 · `app/components/LlmSettingsPanel.tsx`<br>`LlmSettingsPanel` | F/Q/O · S 服务商/渠道/凭据/模型目录、quota 与错误/保存分支；接口：`getSettings`, `llmAddModel`, `llmAddProvider` 等 | 待核凭据失败/过期、服务探测与保存不同、表单恢复和多层焦点 | P1 · E07/E08/E17 |
| C027 · `app/components/McpSettingsPanel.tsx`<br>`McpSettingsPanel` | F/Q/O · S 安装/启停/刷新 Manifest、credentials/OAuth、资源与 Prompt；接口：`mcpConnectAndRegister`, `mcpDeleteCredential`, `mcpFinishOAuth` 等 | 待核断连/认证过期/部分读取/长命令、外部内容边界 | P1 · E08/E09 |
| C028 · `app/components/ModelCatalogDialog.tsx`<br>`ModelCatalogDialog` | Q/F/O · S 搜索/选择导入、手动模型、importing/importError；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核空目录/旧搜索/部分导入失败/关闭保留选择 | P1 · E06/E08 |
| C029 · `app/components/ModelSettingsDialog.tsx`<br>`ModelSettingsDialog` | F/O · S 受控模型 form、saving/saveError；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 dirty 关闭/禁用原因、失败保表单和焦点 | P1 · E08/E17 |
| C030 · `app/components/OverflowMenu.tsx`<br>`OverflowMenu` | Q/O · S 菜单 open、项目 disabled 与键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核方向键/Home/End、点击外部/最上层 Escape/归焦 | P1 · E06 |
| C031 · `app/components/Overlay.tsx`<br>`Overlay` | O · S portal、focus scope、最上层 Escape、anchored/closeTarget、退场 fallback；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 finishClose 幂等、反向/无 API、退场与焦点交回时序 | P1 · E06/E16/E17 |
| C032 · `app/components/QuickChatPopover.tsx`<br>`QuickChatPopover` | Q/O · S 原生弹选内容：目标/模型/强度、键盘索引；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核长列表/滚动、选中消失、返回窗口焦点及 IME 优先 | P1 · E03/E06/E11 |
| C033 · `app/components/QuickChatPopoverHost.tsx`<br>`QuickChatPopoverHost` | H/O · S 窗口状态订阅与 structured select/hide IPC；接口：`onQuickChatPopoverState`, `quickChatHidePopover`, `quickChatSelectPopoverValue` | 待核跨窗口 Escape、卸载订阅和旧选择事件归属 | P1 · E11/E17 |
| C034 · `app/components/QuickChatTaskCard.tsx`<br>`QuickChatTaskCard` | Q/A · S 目标卡选中与 disabled 展示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核目标删除/失效、实际选择与视觉一致 | P1 · E08/E11 |
| C035 · `app/components/QuickChatWindow.tsx`<br>`QuickChatWindow` | I/O · S 文本草稿已有 localStorage；bot 回执后清草稿；经典路径支持附件；接口：`chatSend`, `conversationsAppendMessage`, `conversationsCreate` 等 | G02；待核目标隔离/未知恢复、Escape/IME、附件失败 | P0 · E02/E03/E11 |
| C036 · `app/components/ReleaseNotesView.tsx`<br>`ReleaseNotesView` | V · S 发布说明只读展示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核空/长文/链接打开失败、版本身份与滚动 | P1 · E09/E12 |
| C037 · `app/components/RemoteAccessPairing.tsx`<br>`RemoteAccessPairing` | V/A · S 受控配对信息与 copied/failed 反馈；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核码过期/刷新/复制失败，不能泄露到普通日志 | P1 · E08/E11 |
| C038 · `app/components/RemoteAccessPanel.tsx`<br>`RemoteAccessPanel` | F/Q · S gateway/controller 状态、加载/错误/重试；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核断联/撤回/授权范围、无 bot 与真实失败区分 | P1 · E08/E11 |
| C039 · `app/components/RuntimeFacts.tsx`<br>`FactCard`, `RuntimeFacts` | R/V · S FactCard 汇总运行时事实；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核未知/过期事实、有来源入口，不从文本推导成功 | P1 · E04/E12 |
| C040 · `app/components/SettingsDisclosureContent.tsx`<br>`SettingsDisclosureContent` | O · S 保留退场 DOM、inert/aria-hidden、200ms timer 与 reduce 分支；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核快速反向/卸载、内部焦点先退回、晚 timer 不卸载新内容 | P1 · E16/E17 |
| C041 · `app/components/SettingsPage.tsx`<br>`SettingsPage` | Q/F · S 分区搜索/aria-current；key=section 重建内容；事实：受控 props / 所属 hook（装配模块由子树承接） | G04；待核未保存离开、无结果、兼容 deep-link 与页面焦点 | P1 · E08/E17 |
| C042 · `app/components/ShortcutsPanel.tsx`<br>`ShortcutRow`, `ShortcutsPanel` | F · S 录制/注册状态、更新/恢复热键、aria-live；接口：`getShortcutStatus`, `resetShortcut`, `updateShortcut` | 待核 IME/冲突/系统拒绝/取消录制、合理广播频率 | P1 · E03/E06/E08 |
| C043 · `app/components/SourceCheckoutPanel.tsx`<br>`SourceCheckoutPanel` | F/V/A · S 源头检查/文件、提交/拒绝/重试 handoff、busy/error；接口：`goalPlansCommitSourceCheckout`, `goalPlansDeclineSourceHandoffs`, `goalPlansInspectSourceCheckout` 等 | 待核真实 Git 事实与按钮回执、未知提交不盲重试、冲突恢复 | P0 · E04/E09 |
| C044 · `app/components/SystemInstructionsPanel.tsx`<br>`SystemInstructionsPanel` | F · S 读取/本地 draft/还原/保存，失败静默；接口：`getSettings`, `initialSettings`, `updateSettings` | G04；可见错误与 dirty 离开；保持 Context Source 边界 | P1 · E08/E17 |
| C045 · `app/components/Tooltip.tsx`<br>`Tooltip` | O/R · S hover/focus、aria-describedby、portal 自适应定位；事实：受控 props / 所属 hook（装配模块由子树承接） | G07；待核描述合并与读屏、锚点消失不悬空 | P1 · E06/E15 |
| C046 · `app/components/UpdateModal.tsx`<br>`UpdateModal` | O/V/A · S updater 状态投影、关闭状态与真实操作；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核无新版本/错误/下载/安装分开、关闭不重复发请求 | P1 · E12/E17 |
| C047 · `app/components/UpdatesPanel.tsx`<br>`ExternalLinkIcon`, `UpdatesPanel` | V/A · S 版本/更新状态与产品链接；接口：`openProductLink` | 待核离线/版本未知/打开失败、受支持安装方式提示 | P1 · E12/E15 |
| C048 · `app/components/VersionBadge.tsx`<br>`VersionBadge` | V/O · S 徽标/弹层、pendingDownload 承接请求；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核下载前 pending 与真实 phase、closeTarget 消失降级 | P1 · E12/E17 |
| C049 · `app/components/settings/DeveloperPanel.tsx`<br>`DeveloperPanel` | F/H · S 开发配置入口，内含宿主开发控制；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核无 bot/读失败/危险范围与租约状态，不默认扩权 | P1 · E08/E12 |
| C050 · `app/components/settings/ModelRoutingPanel.tsx`<br>`ModelRoutingPanel`, `ModelDropdown`, `Chevron`, `RemoveIcon` | F/Q · S 角色路由 view/preview/update，ModelDropdown 与错误；接口：`modelRoutingGet`, `modelRoutingPreview`, `modelRoutingUpdate` | 待核继承/缺模型、预览与已保存值、键盘选择与失败恢复 | P1 · E07/E08 |
| C051 · `app/fx/ParticleShatterOverlay.tsx`<br>`ParticleShatterOverlay` | R/O · S 采样 canvas、active 防重播与卸载 stop；事实：受控 props / 所属 hook（装配模块由子树承接） | G11；待核只收尾显示、静态结果仍可到达 | P1 修降级/P2 特效 · E16/E14 |
| C052 · `app/pages/GlobalWorkbenchPage.tsx`<br>`GlobalWorkbenchPage`, `InboxRow`, `ActionArrowIcon` | Q/V/A · S 全局雷达、InboxRow、实际 workspace/attention 事实；接口：`onConversationsChanged`, `workspaceList`, `workspaceSetActive` | 待核旧消费者含义/签收与交回文案，G11 降级 | P1 · E04/E11/E16 |
| C053 · `app/pages/HistoryPage.tsx`<br>`HistoryPage` | Q · S 经典历史过滤与查询；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核空/无结果/读失败区别、回原任务和位置 | P1 · E05/E11 |
| C054 · `app/pages/HomePage.tsx`<br>`HomePage` | H/V · S 经典首页包装，委托 GlobalWorkbenchPage；事实：受控 props / 所属 hook（装配模块由子树承接） | 包装不另造主语；待核兼容入口与范围选择 | P1 · E11 |
| C055 · `app/pages/TaskOverviewPage.tsx`<br>`WorkItemMeta`, `SectionLink`, `TaskOverviewPage`, `TopLine`, `HeroLayout`, `ListLayout`, `HandoffRow`, `DiscussionCard`, `WorkItem`, `ArtifactHoverPreview`, `ArtifactPreviewPortal`, `ArtifactList`, `ResultCard` | Q/V/O · S 多类任务/产物/交回/结果卡和预览，受控事实投影；接口：`openPath` | 待核旧生命周期消费者、hover 预览键盘替代，G11 | P1 · E04/E09/E11/E16 |
| C056 · `app/pages/TasksPage.tsx`<br>`TasksPage` | Q/A · S 任务筛选/搜索/标记已读/删除；接口：`goalPlansDelete`, `taskOverviewMarkRead` | 待核批处理失败、选择对象消失、删除确认/恢复 | P1 · E04/E06/E11 |
| C057 · `app/pages/WorkStream.tsx`<br>根装配；无独立组件声明 | G/V · S 经典响应式工作流布局与 FLIP、reduce guard；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核增删/重排锚点与反向、列数变化不重置对象 | P1 · E05/E16/E17 |
| C058 · `app/pages/actionLabelDisplay.tsx`<br>`ActionLabel` | R · S ActionLabel 的图文表达；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核动词/对象与真实动作一致，非装饰箭头用 SVG | P1 · E04/E15 |
| C059 · `app/pages/goalThreadGrouping.tsx`<br>`ThreadList` | Q/V · S ThreadList 归组与原目标节点导航；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核当前/历史分组、节点移除与原现场定位 | P1 · E04/E05 |
| C060 · `appearance/AppearancePanel.tsx`<br>`AppearancePanel`, `ThemeModeCards`, `ThemeLivePreview` | F/G · S 模式卡/实时预览、主题/材质/字号偏好；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核放大/强制颜色/减少透明、设置应用失败与读位保持 | P1 · E07/E15/E17 |
| C061 · `appearance/AppearanceProvider.tsx`<br>`AppearanceProvider` | H · S 外观设置与系统 scheme 的统一投影；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核系统变更/多窗口/重挂载不丢草稿和 focus | P1 · E07/E17 |
| C062 · `appearance/AppearanceSlider.tsx`<br>`AppearanceSlider` | F/G · S 受控外观连续值；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核范围值/键盘/取消、字体放大不压没关键操作 | P1 · E06/E15 |
| C063 · `appearance/PaletteSelect.tsx`<br>`PaletteSelect` | Q/O · S phase/activeIndex、键盘与 transitionend；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核重复开合/丢 transitionend/当前选项消失/归焦 | P1 · E06/E16/E17 |
| C064 · `automations/AutomationCenter.tsx`<br>`Icon`, `AutomationCenter`, `Metric`, `Editor`, `AutomationDetail`, `RunsTable`, `RunReceipt`, `PageBack`, `FormSection`, `Field`, `Choice`, `Review` | Q/F/V · S 列表/Editor/Detail/RunsTable/RunReceipt、草稿与运行 API；接口：`automationRunsCancel`, `automationRunsGet`, `automationRunsList` 等 | 待核 dirty 离开、时区/触发、全局暂停与单次取消/重试差异 | P1 · E10/E17 |
| C065 · `capabilities/components/CapabilityCard.tsx`<br>`CapabilityCard` | Q/A · S 受控能力摘要与打开详情；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核键盘发现/禁用原因、来源与可用能力区分 | P1 · E08/E15 |
| C066 · `capabilities/components/CapabilityDetailPanel.tsx`<br>`DetailList`, `CapabilityDetailPanel` | V/A · S 详情与展开 Manifest；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核长参数/缺字段、Manifest 不是当前授权、关闭回卡 | P1 · E08/E09 |
| C067 · `capabilities/components/CapabilityEmptyState.tsx`<br>`CapabilityEmptyState` | R/A · S 能力空态/引导入口；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核真空与失败区分、主动作与原因明确 | P1 · E08/E15 |
| C068 · `capabilities/components/CapabilitySection.tsx`<br>`CapabilitySection` | R/Q · S 能力分组容器；事实：受控 props / 所属 hook（装配模块由子树承接） | 容器交互态 N/A；待核标题层级/列表空与密度 | P1 · E07/E15 |
| C069 · `capabilities/components/CapabilityTabs.tsx`<br>`CapabilityTabs` | Q · S Skills/MCP tabs 与 selected；事实：受控 props / 所属 hook（装配模块由子树承接） | G05；键盘、roving、panel 关联 | P1 · E06/E15 |
| C070 · `capabilities/components/CapabilityWorkbench.tsx`<br>`CapabilityWorkbench` | Q/O · S 能力标签、数量与详情/上传打开状态；接口：`mcpListInstalled` | 待核计数取数失败/选中对象失效，复用 G05 修复 | P1 · E06/E08 |
| C071 · `capabilities/components/QoderMarketplacePanel.tsx`<br>`SkillAvatar`, `DownloadIcon`, `QoderMarketplacePanel` | Q/F · S 搜索/分类/分页、详情/安装与项目列表；接口：`getQoderSkillDetail`, `installQoderSkill`, `listQoderTaxonomies` 等 | 待核旧搜索覆盖/离线/安装失败、安装目标明确 | P1 · E08/E09 |
| C072 · `capabilities/components/SkillDetailDialog.tsx`<br>`ScopeBadge`, `SkillDetailDialog` | V/O/A · S 详情读取、启停/卸载确认、loading/error；接口：`getSkillDetail` | 待核卸载失败留现场/跨 scope、关闭和初始焦点 | P1 · E06/E08 |
| C073 · `capabilities/components/SkillMarketplacePanel.tsx`<br>`DownloadIcon`, `SkillIcon`, `SkillMarketplacePanel` | Q/F · S Skills 市场分类/搜索/分页与安装；接口：`installSkillHubSkill`, `listSkillHubCategories`, `querySkillHubSkills` 等 | 待核无结果/失败区别、旧请求、安装回执/项目作用域 | P1 · E08/E09 |
| C074 · `capabilities/components/SkillUploadDialog.tsx`<br>`SkillUploadDialog` | F/O · S 文件上传、uploading/error、说明折叠；接口：`uploadSkill` | 待核格式/超限/取消/部分上传、成功依真实回执 | P1 · E08/E09 |
| C075 · `capabilities/components/SkillsInstalledPanel.tsx`<br>`SkillIcon`, `SkillSection`, `SkillsInstalledPanel` | Q/F · S 已装/可链接、启停/卸载、workspace 订阅与错误；接口：`disableSkill`, `enableSkill`, `linkSkill` 等 | 待核 empty/available 失败区别、链接范围/逐项忙态与恢复 | P1 · E08/E09 |
| C076 · `capabilities/components/SkillsPanel.tsx`<br>`SkillsPanel` | Q/H · S 已安装/市场等视图与 revision 刷新；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核视图切换选择/滚动/草稿保留、旧数据不覆盖新操作 | P1 · E08/E17 |
| C077 · `chat/components/AutomationProposalCard.tsx`<br>`AutomationProposalCard` | V/A · S 提案折叠、pendingAction/actionError；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核提案失效/拒绝/重复操作与真实 automation 回执 | P1 · E04/E10 |
| C078 · `chat/components/ChatSurface.tsx`<br>`ChatSurface` | I/V/O · S 经典任务现场、流式/权限/模型/Goal/附件与恢复装配；接口：`approveLocalAction`, `automationProposalAct`, `chatAbort` 等 | 待核旧消费者/输入/卸载；不继续增长 god component | P0 输入/决策 · E02/E03/E04/E11 |
| C079 · `chat/components/ComposerDraftControls.tsx`<br>`ComposerDraftControls`, `ComposerDraftField` | I/Q · S 共享字段与 slash/mention 补全、文件/会话搜索；接口：`conversationsList`, `conversationsSearch`, `searchWorkspaceFiles` | 待核 IME 优先、候选 Escape/Enter、旧异步结果与草稿 | P0 · E02/E03 |
| C080 · `chat/components/ComposerTokenUsageDisplay.tsx`<br>`ComposerTokenUsageDisplay` | R/V · S 受控上下文用量；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核未知/估算/限制说明、不可用不渲染假零 | P1 · E08/E15 |
| C081 · `chat/components/ConversationAccessControl.tsx`<br>`ConversationAccessControl` | F/O · S 经典会话权限控件的加载/错误/禁用投影；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核实际 scope/撤回/失效与旧决定，不在 renderer 造许可 | P0 · E04/E11 |
| C082 · `chat/components/ConversationSearchPalette.tsx`<br>`BotSearchSections`, `ConversationSearchPalette` | Q/O · S 全局会话/机器人搜索、loading/activeIndex；接口：`conversationsList`, `projectAgentSearch` | 待核无结果/旧响应/输入法/原消息定位与焦点归还 | P1 · E03/E05/E06 |
| C083 · `chat/components/CreateBranchDialog.tsx`<br>`CreateBranchDialog` | F/O · S 分支源/名称/push/upstream 受控表单；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核非法/重复分支、提交失败/未知、未保存关闭 | P1 · E08/E09 |
| C084 · `chat/components/EditProjectDialog.tsx`<br>`EditProjectDialog` | F/O · S 项目名/关联目录/主目录编辑与 busy/error；接口：`workspaceAddLinkedFolder`, `workspaceRemoveLinkedFolder`, `workspaceSetPrimary` 等 | 待核移除失败/dirty 关闭、当前 world 不被悄换 | P1 · E08/E11/E17 |
| C085 · `chat/components/GoalPlanPanel.tsx`<br>`GoalTaskStatusIcon`, `GoalContractSection`, `PlanProjectionSection`, `RunTraceItem`, `RunTraceSection`, `TaskNode`, `RunnerSection`, `VerifierItem`, `ExplorerItem`, `CompactApprovalBar`, `PlanCard`, `GoalPlanPanel` | V/F/A · S Goal/Plan/RunTrace/Runner/Verifier/Explorer 与真实批准/暂停/交回 API；接口：`goalPlansDiscardLine`, `goalPlansIsolate`, `goalPlansList` 等 | 待核同事实投影、过期批准/手工标准、机器结束不等签收 | P0 · E04/E11 |
| C086 · `chat/components/MessageQueue.tsx`<br>`QueueDragHandle`, `EditIcon`, `TrashIcon`, `ForceSendIcon`, `MessageQueue`, `PEER_QUEUED_MESSAGE_DND_TYPE` | Q/G/F · S 待发消息拖动/编辑/删除/强发回调；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核键盘改序、pointercancel/卸载、强发作用域与去重 | P0 输入/P1 手势 · E02/E03/E06 |
| C087 · `chat/components/SelectionChatWorkspace.tsx`<br>`SelectionChatWorkspace` | I/O · S 持久选区子会话、draft/保存/待发文本与 parent 来源；接口：`conversationsGet`, `onConversationsChanged`, `selectionCreateChild` 等 | 待核保存失败/原文失效、关闭回位/不覆盖已有草稿 | P1 · E02/E05/E09 |
| C088 · `chat/components/SelectionQuoteAction.tsx`<br>`SelectionQuoteAction` | A/O · S 选区定位、引用 API、busy/error/confirmation；接口：`conversationsGet`, `selectionQuote` | 待核键盘等价入口、失效 Range/滚动重定位与恢复 | P1 · E05/E06/E09 |
| C089 · `chat/components/Sidebar.tsx`<br>`PinIcon`, `Sidebar` | Q/F/O · S 经典 workspace/会话管理、搜索/菜单/改名/确认；接口：`onConversationsChanged`, `onWorkspacesChanged`, `openPath` 等 | 待核键盘/拖动/上下文菜单、切换草稿和删除后归处 | P1 · E06/E11 |
| C090 · `chat/components/SidebarConversationRow.tsx`<br>`PinIcon`, `SidebarConversationRow` | Q/A · S 受控行、pin/选中/键盘与禁用；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 hover 操作 focus 可发现、长标题/重命名/失效对象 | P1 · E06/E15 |
| C091 · `chat/components/SidebarWorkbenchCounts.tsx`<br>`SidebarWorkbenchCounts` | R · S 工作台数字摘要；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核计数与原清单同投影、过期不伪装最新 | P0 · E04/E11 |
| C092 · `chat/components/gitGlyphs.tsx`<br>`GitBranchGlyph`, `GitWorktreeGlyph` | R · S Git branch/worktree SVG；事实：受控 props / 所属 hook（装配模块由子树承接） | 纯装饰交互态 N/A；外层动作名称/状态文本须明确 | P2 · E15 |
| C093 · `chat/components/goal/ChatGoalApprovalCard.tsx`<br>`ChatGoalApprovalCard` | V/A · S 受控 Goal 批准卡、busy/error；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核旧计划/范围变化/拒绝/重试与真实决定回执 | P0 · E04 |
| C094 · `chat/components/goal/GoalActivityLabel.tsx`<br>`GoalActivityLabel` | R/V · S 真实 Goal 进展标签；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核等待/核验/未知区分，不用颜色独自表达 | P0 · E04/E15 |
| C095 · `chat/components/goal/GoalInvestigationCards.tsx`<br>`GoalInvestigation` | V/A · S 调查/探索卡与本地 dismiss；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核收起不改运行事实、失败/报告不可用与原任务 | P1 · E04/E11 |
| C096 · `chat/components/goal/SuccessCriteriaEditor.tsx`<br>`SuccessCriteriaEditor` | F · S 标准 draft/error、goalPlansRevise；接口：`goalPlansRevise` | 待核保存失败/并发修订/未保存离开与真实版本 | P1 · E04/E17 |
| C097 · `chat/components/markdown/InlineMarkdown.tsx`<br>`FilePathCode`, `WorkspacePathContext` | V/O · S 内联文本/文件路径、存在检查、图片预览与打开；接口：`openPath` | 待核缺失/无权限/旧预览/打开失败，来源可辨 | P1 · E09/E15 |
| C098 · `chat/components/markdown/MarkdownMessage.tsx`<br>`HistoricalPreviewBlock`, `CopyableCodeBlock`, `CodeBlockContent`, `MarkdownMessageImpl`, `MarkdownMessage` | V/A · S 富文本/历史预览/代码块/复制与展开；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核复制失败、长代码局部滚动、链接来源、静态阅读 | P1 · E05/E09/E15 |
| C099 · `chat/components/thread/AssistantContent.tsx`<br>`ToolProgressInline`, `LiveToolProgress`, `AssistantContentImpl`, `ProcessingDetailsSection`, `ThinkingTextGroup`, `TimelineGroups`, `ToolCallCard`, `CompactionSummaryCard`, `AssistantContent` | V/O · S 真实工具/思考/压缩详情、timeline 与 motion presence；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核用户收起后不被更新展开、工具事实/文本区分 | P1 · E04/E05/E16 |
| C100 · `chat/components/thread/AttachmentStrip.tsx`<br>`AttachmentStrip`, `ResolvedImageChip`, `AttachmentThumb`, `PEER_ATTACHMENT_DND_TYPE` | Q/G/V · S 附件重排/缩略图/读取失败和 pending；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核键盘顺序/拖动取消、缺失图、移除不影响待确认输入 | P1 · E02/E06/E09 |
| C101 · `chat/components/thread/BatchSearchToolCard.tsx`<br>`BatchSearchToolCard` | V/O · S 搜索调用批量展示、展开与 error/pending；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核失败/空结果分开、收起保留意图、参数证据可达 | P1 · E04/E09 |
| C102 · `chat/components/thread/ChatFindBar.tsx`<br>`ChatFindBar` | Q/O · S 页内查询/计数/当前匹配、unsupported 与 live status；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核虚拟内容定位/键盘、关闭回原焦点、无结果 | P1 · E05/E06 |
| C103 · `chat/components/thread/ChatHeader.tsx`<br>`ChatHeader` | F/Q/O · S 标题改名、菜单与模型/任务操作受控；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核改名失败/dirty 退出、长标题与焦点 | P1 · E06/E08 |
| C104 · `chat/components/thread/ChatHeaderCapabilities.tsx`<br>`ChatHeaderCapabilities` | Q/O · S 当前能力/Skills 列表、启停/卸载与错误；接口：`disableSkill`, `enableSkill`, `listCapabilities` 等 | 待核清单失败/实际 Projection、卸载后当前请求/焦点 | P1 · E08/E09 |
| C105 · `chat/components/thread/ChatTurn.tsx`<br>`StreamingElapsedTime`, `ChatTurnImpl`, `ChatTurn` | V · S 稳定 turn 展示、elapsed 与受控子内容；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核流式到持久身份、停止不完整、历史不重播 | P1 · E05/E16/E17 |
| C106 · `chat/components/thread/ContextAccountUsage.tsx`<br>`ContextAccountUsage` | V · S 订阅 quota 请求、状态与时间读数；接口：`llmGetSubscriptionQuota` | 待核过期/未知/请求失败与刷新，不推断计费 | P1 · E08/E15 |
| C107 · `chat/components/thread/ContextUsagePanel.tsx`<br>`ContextUsagePanel` | O/V · S 上下文用量锚定面板与定位；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核无数据/过期、键盘入口/关闭归焦/长值 | P1 · E06/E08 |
| C108 · `chat/components/thread/ImageLightbox.tsx`<br>`ImageLightbox` | O/V/G · S 统一图片预览、适应/原尺寸、复制路径/打开；接口：`openPath` | G08；待核键盘/缩放/晚图/失效来源与回位 | P1 · E09/E17 |
| C109 · `chat/components/thread/ImagePreviewBar.tsx`<br>`ImagePreviewBar` | Q/V · S 受控图片预览条；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核缺图/移除/文件名与外层可达名称 | P1 · E09/E15 |
| C110 · `chat/components/thread/InteractionToolCard.tsx`<br>`InteractionToolCard` | V/F/A · S 结构化问答/交互卡与 optimisticAnswer；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核选项/自由输入/失效/提交失败、乐观态不冒充决定事实 | P0 · E04/E11 |
| C111 · `chat/components/thread/MessageActionBar.tsx`<br>`MessageActionBar` | A/O · S 复制/删除确认反馈；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核复制失败、删除后焦点、hover 与 focus-within 可发现 | P1 · E06/E09/E15 |
| C112 · `chat/components/thread/MessageRail.tsx`<br>`MessageRail` | R/V · S 消息操作/元信息侧轨；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核放大/窄窗、操作发现与正文阅读不冲突 | P1 · E07/E15 |
| C113 · `chat/components/thread/MessageRichParts.tsx`<br>`MessageRichParts` | V/A · S 受控富消息片段与动作；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核部分数据/不可用操作、来源/Evidence 关系与长内容 | P1 · E04/E09 |
| C114 · `chat/components/thread/ModelSelectionPanel.tsx`<br>`EffortRange`, `RequestChannelToggle`, `ModelSelectionPanel`, `AnchoredModelSelectionMenu`, `ComposerModelMenu` | F/Q/G/O · S 统一模型/强度/通道、dragValue/dirty 与菜单；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核保存失败/当前角色来源、slider 键盘、冻结当轮与窄窗 | P1 · E01/E06/E08 |
| C115 · `chat/components/thread/PermissionGateStrip.tsx`<br>`PermissionGateStrip` | V/A · S 受控待权限提示与 live 状态；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核同 approval/作用范围、失效/拒绝/取消；不从文本造授权 | P0 · E04 |
| C116 · `chat/components/thread/ReasoningEffortSlider.tsx`<br>`ReasoningEffortSlider` | F/G/O · S 强度选值、dragValue/dirty/saving 与浮层定位；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核离散档/键盘/失败回读/拖动取消，复用统一模型入口 | P1 · E06/E08/E15 |
| C117 · `chat/components/thread/SkillCapsuleCard.tsx`<br>`SkillCapsuleCard` | V/O · S 技能摘要、展开与键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核用户折叠意图/缺来源/长名，技能提示不是执行证明 | P1 · E08/E09 |
| C118 · `chat/components/thread/ThinkingTimeline.tsx`<br>`ThinkingTimeline` | V · S 真实思考/工具 timeline 的受控展示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核等待/错误语义、不自动展开内部过程或重播历史 | P1 · E04/E05/E16 |
| C119 · `chat/components/thread/TokenUsageDisplay.tsx`<br>`TokenUsageDisplay` | V/A · S lastKnownContext 与 token 提示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 stale/估算/缺数据，不能把上一轮值当实时 | P1 · E08/E15 |
| C120 · `chat/components/thread/VirtualChatTurnList.tsx`<br>`VirtualChatTurnList` | V/G · S 虚拟消息列表/测量 seam；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核旧 index/图片晚到/字体变化/定位，保持阅读意图 | P1 · E05/E17 |
| C121 · `main.tsx`<br>根装配；无独立组件声明 | H · S 根挂载、主题和错误/确认 Provider 装配；事实：受控 props / 所属 hook（装配模块由子树承接） | 装配无独立交互态；待核启动失败仍有恢复入口 | P1 · E12/E15 |
| C122 · `project-agent/AppMenu.tsx`<br>`AppMenu` | Q/O · S 机器人壳应用菜单与键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核最上层 Escape/焦点、切经典/设置后返回 | P1 · E06/E11 |
| C123 · `project-agent/AttentionSheet.tsx`<br>`AttentionSheet` | Q/O · S 真实 attention 清单、loading/error/retry、事实订阅；接口：`onProjectAgentChanged`, `onProjectAgentConversationChanged`, `projectAgentListAttention` | 待核失效行/计数同步/点回原任务/空态与错误 | P0 · E04 |
| C124 · `project-agent/BotAccessControl.tsx`<br>`BotAccessControl` | F/O · S 主 Bot 访问策略、加载/保存/失败/重试；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核继承/Full/Session/撤回真实范围，子任务不自造策略 | P0 · E04 |
| C125 · `project-agent/BotAvatar.tsx`<br>`BotAvatar` | R · S 头像读取与状态 SVG/材质；接口：`projectAgentReadAvatar` | 待核缺图 fallback、后台 gaze/循环节制、reduce JS 路径 | P1 · E15/E16 |
| C126 · `project-agent/BotList.tsx`<br>`BotList` | Q · S 受控搜索/列表选择、组合输入保护；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核无结果/切换/搜索 Escape/长名称与选中消失 | P1 · E03/E06/E07 |
| C127 · `project-agent/BotListShell.tsx`<br>`BotListShell` | H/Q/O · S 机器人壳/新建/档案/历史/任务上下文装配；接口：`projectAgentMarkRead` | 待核跨 bot 草稿、嵌套 drawer/focus 与旧请求；不增长大组件 | P1 · E02/E06/E17 |
| C128 · `project-agent/BotModelControls.tsx`<br>`BotModelControls` | F/Q/O · S 消费 useBotModels 与统一选模面板；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 busy/继承/失败回读/当前与下轮；不重做 PR197 | P1 · E01/E08 |
| C129 · `project-agent/BotRow.tsx`<br>`BotRow` | Q/A · S 受控机器人行、键盘与行动权入口；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核需要你/进行中语义、hover 操作可达与长名 | P0 事实/P1 视觉 · E04/E07 |
| C130 · `project-agent/HistoryConversationList.tsx`<br>`HistoryConversationList` | Q · S 历史搜索/limit/加载/重试与键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核空/无结果/加载失败区别、分页选择不跳 | P1 · E05/E11/E12 |
| C131 · `project-agent/HistorySheet.tsx`<br>`HistorySheet` | Q/O/V · S 历史列表/预览、继续确认、读失败/重试；接口：`conversationsGet`, `projectAgentContinueHistory`, `projectAgentListHistory` | 待核双击继续/旧预览/原身份、关闭回列表位置 | P1 · E05/E11/E17 |
| C132 · `project-agent/NewBotSheet.tsx`<br>`NewBotSheet` | F/O · S 受控名称/路径/错误/提交；含名称优先实现；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核空名/重名/取消/目录绑定两语义/失败保留 | P1 · E01/E08 |
| C133 · `project-agent/conversation/AgentActivityRow.tsx`<br>`AgentActivityRow` | R/V · S 命名活动/图标和真实 agent activity；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核同身份去重、未知/等待人/核验不混淆 | P0 · E04/E16 |
| C134 · `project-agent/conversation/ApprovalReceipt.tsx`<br>`ApprovalReceipt` | V · S 已决定授权回执与具体范围；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核批准/拒绝/取消/超时/失效分开，历史可追原对象 | P0 · E04 |
| C135 · `project-agent/conversation/BotAttachments.tsx`<br>`BotAttachments` | Q/V/O · S 附件列表/移除和共享灯箱预览；事实：受控 props / 所属 hook（装配模块由子树承接） | G08 由共享灯箱处理；待核读取失败/晚图/键盘移除 | P1 · E02/E09 |
| C136 · `project-agent/conversation/BotComposer.tsx`<br>`BotComposer` | I · S 局部草稿/附件、IME 保护、发送与停止、读入提示；事实：受控 props / 所属 hook（装配模块由子树承接） | G01；待核组合输入兼容/模型保存中/引用附件整体恢复 | P0 · E02/E03/E09 |
| C137 · `project-agent/conversation/BotConversation.tsx`<br>`BotConversation` | I/V/O · S 公共对话/引用/详情/定位、按 workspaceId 重建 composer；接口：`projectAgentReadEvidence` | G01；待核 quote 恢复、切换/回读、来源缺失 | P0 · E02/E05/E09 |
| C138 · `project-agent/conversation/BotMessageList.tsx`<br>`BotMessageList`, `SystemCard` | V/Q · S 公共消息/系统卡、加载更早/读位和键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核失败后保持消息、分页锚点/虚拟重测/历史不重播 | P1 · E05/E12/E17 |
| C139 · `project-agent/conversation/BotNarration.tsx`<br>`BotNarration` | V · S 公共叙述和 aria-live；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核流式广播频率、停止/完成保留叙述、无私有思考 | P1 · E04/E05/E16 |
| C140 · `project-agent/conversation/BotProcess.tsx`<br>`BotProcess`, `Preview` | V/O · S 过程预览/用时与真实记录；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核收起权、未知用时、历史重开不伪装进行中 | P1 · E04/E05/E16 |
| C141 · `project-agent/conversation/BotSelectionQuote.tsx`<br>`BotSelectionQuote` | A/O · S 选区与浮动引用位置；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核键盘等价、Range 失效/滚动、引用源定位与 draft | P1 · E05/E06/E09 |
| C142 · `project-agent/conversation/CardView.tsx`<br>`CardView`, `CardDiagnostics`, `CardItem` | V/A/F · S CardItem 防重入/busy/error、宿主决定回执、已决问题 presence；接口：`projectAgentAcceptReadme`, `projectAgentConfirmResult`, `projectAgentDecideApproval` 等 | G12；待核失效/迟到/多卡/free answer 与作用范围 | P0 决策/P1 降级 · E04/E16/E17 |
| C143 · `project-agent/conversation/CompletionReview.tsx`<br>`CompletionReview` | V/O · S 核验摘要展开与既有 review 投影；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核旧 attempt/partial/unverified 第一层可见、收起保意图 | P0 · E04/E09 |
| C144 · `project-agent/conversation/ContinuousReply.tsx`<br>`ContinuousReply` | V · S 连续公共回复与 live 状态，稳定对象组合；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核段落身份/晚到持久消息/停止与失败不重放 | P1 · E05/E16/E17 |
| C145 · `project-agent/conversation/DelegatedWork.tsx`<br>`DelegatedWork`, `WorkRow` | Q/V/A · S 子任务 WorkRow、状态与原任务入口；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核同 lifecycle/cancelable、并行分组不误归属、取消失败 | P0 · E04 |
| C146 · `project-agent/conversation/EvidenceList.tsx`<br>`EvidenceList` | V/Q · S 按 Evidence 引用读取来源；接口：`projectAgentReadEvidence` | 待核缺失/权限/读取失败与空的区别、来源定位 | P1 · E09 |
| C147 · `project-agent/conversation/LiveReply.tsx`<br>`LiveReply` | V · S 真实活动和流式公共回复、aria-live；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核已停止/未知/持久接管不闪退/不重复播报 | P1 · E04/E05/E16 |
| C148 · `project-agent/conversation/QuoteChip.tsx`<br>`QuoteChip` | V/A · S 受控引用内容/来源/移除入口；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核长引用/来源失效/键盘移除、焦点回 composer | P1 · E02/E09/E15 |
| C149 · `project-agent/conversation/RecoveryHistory.tsx`<br>`RecoveryHistory` | V · S 既有恢复记录的只读投影；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核历史失败与当前恢复分开、无检查点不诱导自动重放 | P0 · E04/E12 |
| C150 · `project-agent/conversation/ReplyAnchors.tsx`<br>`ReplyAnchors`, `ReplyAnchorPreview` | Q/O · S 回复与输入锚点/预览；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核源缺失/历史分页定位、预览键盘与读位保留 | P1 · E05/E06/E09 |
| C151 · `project-agent/conversation/ReplyBubble.tsx`<br>`ReplyBubble` | V · S 稳定回复气泡与受控内容；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核首次/历史/重连身份、字号/窄窗和静态终态 | P1 · E05/E07/E16 |
| C152 · `project-agent/conversation/ReplyContext.tsx`<br>`ReplyContext`, `ReplyDetailsContext`, `MemoryContext` | O/V/Q · S 回复详情/MemoryContext、pending/failed 和 memory 按需读取；接口：`projectMemoryList` | 待核来源 unavailable、收起/切 tab、返回同回复与焦点 | P1 · E06/E09/E10 |
| C153 · `project-agent/conversation/ReplyDetails.tsx`<br>`ReplyDetails` | V/O · S 过程/工具/恢复等按需详情、loading/error；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核详情失败不抹正文、保持展开/原回复定位 | P1 · E04/E05/E09 |
| C154 · `project-agent/conversation/ReplyPresence.tsx`<br>`ReplyPresence` | R/V · S 真实活动/等待/slow 提示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核计时只提示不造进度、结束清理与 reduce 静态 | P1 · E04/E16 |
| C155 · `project-agent/conversation/UserBubble.tsx`<br>`UserBubble` | V/A · S 乐观待发/失败 retry、一次 arriving 动画；事实：受控 props / 所属 hook（装配模块由子树承接） | G01 恢复责任；待核回执后身份、未知重试同 ID | P0 · E02/E16/E17 |
| C156 · `project-agent/diagnostics/ProjectDiagnosticsPanel.tsx`<br>`ProjectDiagnosticsPanel` | V/A · S 按需 diagnostics、busy/status/live 反馈；接口：`projectAgentDiagnostics` | 待核失败/复制、长报告/敏感值和任务来源定位 | P1 · E12/E15 |
| C157 · `project-agent/drawer/AgentProcessView.tsx`<br>`AgentProcessView` | V · S 已命名代理的活动/错误过程视图；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核同一活动身份、后台不抢焦点/不展开私有过程 | P1 · E04/E05 |
| C158 · `project-agent/drawer/BotDrawerSegments.tsx`<br>`BotDrawerSegments` | Q/G · S roving/Arrow/Home/End、6px 手势门槛与 pointercancel；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核失焦/lostcapture/Escape 撤销、panel 关联和多实例隔离 | P1 · E06/E15/E17 |
| C159 · `project-agent/drawer/BotHostControl.tsx`<br>`BotHostControl` | H/A · S 宿主身份/接管、busy/status 与实际 takeover；接口：`projectAgentTakeoverHost` | 待核租约冲突/失效/错误；接管点击不能充当已取得租约 | P1 · E11/E12 |
| C160 · `project-agent/drawer/BotHostDeveloperControl.tsx`<br>`BotHostDeveloperControl` | H/Q · S 开发页选择 bot/宿主控制；接口：`projectAgentList` | 待核空/读取失败/旧选择、与公开控制语义一致 | P1 · E08/E12 |
| C161 · `project-agent/drawer/BotPolicyFields.tsx`<br>`BotApprovalFields`, `BotPolicyFields` | F · S 受控主动性/批准策略字段；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核非法/不支持的策略项、作用范围和保存失败 | P0 决策/P1 配置 · E04/E10 |
| C162 · `project-agent/drawer/BotProfileDrawer.tsx`<br>`BotProfileDrawer` | O/Q · S 五 tab、push/cover、focus scope、dock phase 与报告按需读；接口：`openPath`, `projectAgentGet`, `projectAgentListHistory` 等 | 待核反向/resize/trigger 消失、退场兜底/未保存编辑 | P1 · E06/E17 |
| C163 · `project-agent/drawer/BotSettingsTab.tsx`<br>`BotSettingsTab` | F/A · S 名称/主动级/并发/删除编辑，busy/error；接口：`getSettings`, `projectAgentDelete`, `projectAgentUpdateProfile` 等 | 待核 dirty 离开、删除不可逆说明、失败恢复与返回列表 | P1 · E08/E10/E17 |
| C164 · `project-agent/drawer/CoordinationDetails.tsx`<br>`CoordinationDetails` | V · S 真实协调日志/等待与决策细节；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核增量读取失败/旧 revision、执行与报告不同事实 | P1 · E04/E12 |
| C165 · `project-agent/drawer/EvidenceView.tsx`<br>`EvidenceView` | V/O · S Evidence/文件的受控详情；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核缺文件/旧来源/局部滚动/打开失败与返回 | P1 · E09/E17 |
| C166 · `project-agent/drawer/MemoryTab.tsx`<br>`MemoryTab` | Q/F/A · S 筛选/分页/编辑/固定/忘记/恢复/学习开关；接口：`projectMemoryEdit`, `projectMemoryExport`, `projectMemoryForget` 等 | G09；待核冲突/来源/逐项操作不覆盖 draft | P1 · E10/E15/E17 |
| C167 · `project-agent/drawer/ObjectivesTab.tsx`<br>`ObjectivesTab` | Q/F/A · S 目标编辑/预算/自主性/暂停恢复、loading/error；接口：`automationsList`, `onProjectAgentChanged`, `projectObjectivesDelete` 等 | 待核 dirty 离开/触发不可用/终态重开/失败保表单 | P1 · E10/E17 |
| C168 · `project-agent/drawer/OverviewTab.tsx`<br>`OverviewTab` | V/A · S 项目/模型/主机概况与打开入口；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核未知/路径缺失/长值、跳转保留当前上下文 | P1 · E08/E12/E15 |
| C169 · `project-agent/drawer/SessionDetail.tsx`<br>`SessionDetail`, `ConversationSceneDrawer` | V/O/I · S 任务报告与嵌套 ConversationSceneDrawer，旧配置按需读；接口：`getSettings`, `llmListProviders` | 待核 stale/不可用详情、子现场草稿/读位、关闭回原任务 | P0 事实/P1 连续性 · E04/E05/E09/E17 |
| C170 · `project-agent/drawer/TaskVerification.tsx`<br>`TaskVerification` | V · S 核验结论/attempt/checks 真实投影；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 passed/partial/failed/unverifiable、来源缺失与旧 attempt | P0 · E04/E09 |
| C171 · `project-agent/drawer/TasksTab.tsx`<br>`TasksTab` | Q/A · S 当前/历史/经典任务、resume 状态与错误；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核空/分页/恢复失败、生命周期判断不由名称推导 | P0 事实/P1 列表 · E04/E12 |
| C172 · `project-agent/onboarding/BotOnboarding.tsx`<br>`BotOnboarding` | F/O · S 机器人首次使用引导与受控动作；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核无模型/中断重开/取消、不伪造完成熟悉 | P1 · E08 |
| C173 · `project-agent/onboarding/ClassicShellNotice.tsx`<br>`ClassicShellNotice` | R/A · S 经典模式迁移提示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核切换取消/恢复入口、提示不改原数据/权限 | P1 · E08/E11 |
| C174 · `project-agent/onboarding/UpgradeBanner.tsx`<br>`UpgradeBanner` | A/V · S 读取/更新 shell 设置、pending；接口：`getSettings`, `updateSettings` | 待核写失败/重复点击/关闭重开，不称未完成迁移已完成 | P1 · E08/E11 |
| C175 · `project-agent/state/TaskCancellation.tsx`<br>`TaskCancellationProvider`, `TaskCancelButton` | A/H · S 共享 cancel pending/failed、宿主 cancelable 与焦点收尾；接口：`projectAgentCancelSession` | 待核慢取消/失败/跨 bot、停止回复与取消任务明确分开 | P0 · E04 |
| C176 · `settings/UsageStatsPanel.tsx`<br>`GroupTable`, `TokenHeatmap`, `HeatmapDayStrip`, `TokenTrendChart`, `DayDetailPanel`, `UsageStatsPanel` | Q/V/G · S 分组表、热图/趋势、日期详情与 loading/error；接口：`usageGetDaily`, `usageGetDay`, `usageGetStats` | 待核空/过期/失败、图表键盘文字替代、单位与长值 | P1 · E08/E15 |
| C177 · `ui/boolean-controls/Checkbox.tsx`<br>`Checkbox` | F · S 原生 checkbox 语义与 SVG 勾选；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 disabled/focus/indeterminate 需求、外层 label/forced colors | P1 · E06/E15 |
| C178 · `ui/boolean-controls/Switch.tsx`<br>`Switch` | F/A · S button role=switch/aria-checked、受控值与 disabled；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核忙态/保存失败不谎报已生效、名称和键盘 | P1 · E06/E15 |
| C179 · `ui/icons/PeerIcon.tsx`<br>`PeerIcon` | R · S 共享 SVG 图标注册；事实：受控 props / 所属 hook（装配模块由子树承接） | 装饰交互态 N/A；待核新图标来源/外层 aria-label 一致 | P1 · E15 |
| C180 · `ui/settings/SettingsGroup.tsx`<br>`SettingsGroup` | R/F · S 共享分组/设置行结构与说明；事实：受控 props / 所属 hook（装配模块由子树承接） | 容器交互态 N/A；待核长文/值列/错误放置和 focus 样式 | P1 · E07/E15 |
| C181 · `workbench/BackgroundRunDetails.tsx`<br>`BackgroundRunDetails` | V/A · S 后台运行结果/输出与复制错误；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核部分/截断/未知结果、来源回任务和复制恢复 | P1 · E04/E09/E12 |
| C182 · `workbench/BackgroundRuntimePanel.tsx`<br>`BackgroundRuntimePanel` | Q/V/O · S 后台运行选中/历史 limit/确认、loading/error/stale；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核取消与重试范围、读失败保原记录、关闭恢复焦点 | P1 · E04/E06/E12 |
| C183 · `workbench/GlobalBackgroundTasksButton.tsx`<br>`BackgroundRunsProvider` | H/A · S BackgroundRunsProvider 与全局运行入口；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核计数同投影、多窗口订阅清理、打开原任务 | P1 · E04/E11 |
| C184 · `workbench/OpenTargetSplitButton.tsx`<br>`EditorAppIcon`, `OpenTargetSplitButton` | Q/O/A · S 编辑器选择与受控打开目标、键盘/禁用；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核编辑器失效/打开失败、菜单归焦/长应用名 | P1 · E06/E09 |
| C185 · `workbench/ResourceTabStrip.tsx`<br>`CloseIcon`, `ResourceTabStrip` | Q/A · S 选中、roving tabIndex、独立 close 按钮；事实：受控 props / 所属 hook（装配模块由子树承接） | G05；待核关闭当前页后的相邻焦点/动态新增 | P1 · E06/E15/E17 |
| C186 · `workbench/SidebarResizer.tsx`<br>`SidebarResizer` | G · S rAF 跟手、键盘/双击、阈值收栏；事实：受控 props / 所属 hook（装配模块由子树承接） | G06；补 pointercancel/blur/卸载/撤销和值范围 | P1 · E06/E17 |
| C187 · `workbench/SidebarToggle.tsx`<br>`SidebarToggle` | A · S 受控侧栏开关；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核 aria-expanded/控制对象、focus/快捷键与阅读位置 | P1 · E06/E15 |
| C188 · `workbench/WorkbenchContext.tsx`<br>`WorkbenchProvider`, `WORKBENCH_DEFAULT_WIDTH`, `WORKBENCH_MIN_WIDTH`, `WORKBENCH_MAX_WIDTH`, `MAIN_MIN_WIDTH`, `MAIN_RESTORE_WIDTH`, `SIDEBAR_DEFAULT_WIDTH`, `SIDEBAR_MIN_WIDTH`, `SIDEBAR_MAX_WIDTH`, `SIDEBAR_COLLAPSE_THRESHOLD` | H/G · S 按 conversation 保存打开/标签/文档/浏览器、布局与 reveal；接口：`acknowledgeBrowserPanelReveal`, `initialSettings`, `onBrowserPanelRevealRequest` | 待核导航/resize/关闭保对象，不为视觉动作销毁 guest | P1 · E05/E12/E17 |
| C189 · `workbench/WorkbenchPanel.tsx`<br>`MaximizeIcon`, `RestoreIcon`, `WorkbenchPanel` | O/Q/G · S 稳定 webview 挂载、尺寸阶段、capture/cancel/blur/lostcapture 与键盘；事实：受控 props / 所属 hook（装配模块由子树承接） | G06 的撤销/范围语义；待核卸载与 iframe 跨越、窄窗 | P1 · E06/E17 |
| C190 · `workbench/WorkbenchToggle.tsx`<br>`WorkbenchToggle` | A · S 受控工作台开关；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核名称/expanded、首次/重开 focus 与正确会话目标 | P1 · E06/E15 |
| C191 · `workbench/file-preview/DiffViewer.tsx`<br>`DiffLines`, `DiffFilePreviewPortal`, `DiffFileIndex`, `DiffViewer` | V/Q/O · S diff 行/文件索引与 hover preview portal；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核空/二进制/截断、键盘等价预览/原行定位与局部滚动 | P1 · E05/E06/E09 |
| C192 · `workbench/file-preview/FileKindIcon.tsx`<br>`FileKindIcon` | R · S 文件类型 SVG；事实：受控 props / 所属 hook（装配模块由子树承接） | 装饰状态 N/A；待核未知类型 fallback 和非颜色识别 | P2 · E15 |
| C193 · `workbench/file-preview/MarkdownDocument.tsx`<br>`Heading`, `CodeBlock`, `MarkdownDocument` | V/A · S 文档 Markdown、标题/代码块/复制；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核复制失败/长代码/链接、标题可定位与阅读保持 | P1 · E05/E09/E15 |
| C194 · `workbench/file-preview/SourceViewer.tsx`<br>`SourceViewer` | V · S 受控源码行与语法展示；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核超长/截断/行定位/200% 放大与局部横滚 | P1 · E05/E09/E15 |
| C195 · `workbench/views/BackgroundThreadsView.tsx`<br>`BackgroundThreadsView` | Q/V/A · S shell tasks 列表、选中/停止 busy/error；接口：`listShellTasks`, `stopShellTask` | 待核停止未知/失败、不从输出文本推导终态、回原任务 | P1 · E04/E09/E12 |
| C196 · `workbench/views/BrowserView.tsx`<br>`IconBack`, `IconForward`, `IconReload`, `IconStop`, `IconGo`, `IconOpenExternal`, `IconGlobe`, `IconPlus`, `IconMore`, `BrowserPage`, `BrowserView` | F/Q/H · S BrowserPage/webview 事件、地址/导航/标签、菜单/导入/密码入口；接口：`captureBrowserPage`, `clearBrowserSiteData`, `openBrowserExternal` 等 | 待核崩溃/断联/错误/外开失败，guest 焦点与宿主拖动 | P1 · E06/E09/E12/E17 |
| C197 · `workbench/views/DocumentView.tsx`<br>`DocumentIcon`, `AddIcon`, `DocumentView`, `DocumentPage` | Q/V/O · S 文档/图片/diff、editor 默认值与受管文件读取；接口：`gitDiff`, `listEditors`, `openPath` 等 | 待核失效路径/大文件/读取失败、关闭选中与来源焦点 | P1 · E09/E17 |
| C198 · `workbench/views/FilesView.tsx`<br>`FileTreeIcon`, `RefreshIcon`, `NewFileIcon`, `NewFolderIcon`, `SearchIcon`, `TreeNode`, `FilesView` | Q/F/G · S TreeNode、watch/目录读取、筛选/新文件夹/新文件；接口：`mkdir`, `onFsDirChanged`, `readDir` 等 | 待核权限/重名/读取失败、树键盘/刷新保选择和滚动 | P1 · E06/E09 |
| C199 · `workbench/views/PasswordManagerPanel.tsx`<br>`PasswordManagerPanel` | Q/F/O · S 凭据列表/筛选/揭示/填充/保存删除、loading/error；接口：`deletePasswordVaultEntry`, `fillPasswordVaultEntry`, `listPasswordVaultEntries` 等 | 待核锁定/揭示失败/超时与 dirty 离开，秘密不入日志 | P1 · E08/E09/E17 |
| C200 · `workbench/views/SessionImportWizard.tsx`<br>`SessionImportWizard` | F/O/H · S preflight→来源→站点→导入，OS 设置/拖动与错误；接口：`getAppDragTarget`, `getBrowserSessionImportPreflight`, `importBrowserSiteSession` 等 | 待核取消/部分失败/过期权限/返回步骤保选择 | P1 · E08/E09/E17 |
| C201 · `workbench/views/TaskMonitorRailView.tsx`<br>`BranchIcon`, `FolderIcon`, `DeviceIcon`, `TerminalIcon`, `HammerIcon`, `GlobeIcon`, `ArtifactIcon`, `CheckIcon`, `MonitorSection`, `MonitorRow`, `TaskMonitorRailView` | Q/V/O · S 真实任务/运行/产物 rail、展开和 motion presence；事实：受控 props / 所属 hook（装配模块由子树承接） | 待核当前对象失效/无报告、停止确认、收起保意图 | P1 · E04/E05/E09/E16 |

## 6. 非 TSX 交互 seam 与其他宿主

| 源码入口（代码仓相对路径） | 当前实现/状态责任 | 缺口或待核 / 排程 / 任务 |
|---|---|---|
| r/app/hooks/useFocusScope.ts、focusScope.ts、app/components/overlayStack.ts | 进入、Tab 边界、最上层、恢复合法触发者 | V 嵌套、trigger 消失、背景 pointer 隔离与减少动效时点 · P1 E06/E17 |
| r/app/hooks/useMotionPresence.ts、app/components/overlayCloseTarget.ts、anchoredOverlay.ts | 已有幂等 presence、测量目标、浮层定位 | V Overlay 的独立 finishClose 与 presence 收尾差异、反向/卸载 · P1 E16/E17 |
| r/project-agent/conversation/useComposerAttachments.ts；state/useBotConversation.ts；chat/state/composerPersistence.ts | 附件并发读取、待发/去重、经典草稿持久 seam | G01；V 各入口恢复责任，不复制新持久真源 · P0 E02/E03/E09 |
| r/project-agent/state/useBotModels.ts；chat/components/thread/ModelSelectionPanel.tsx | 模型选择/保存/来源解析，具体文件以调用处定位 | V 当轮快照/下轮生效与过期请求 · P1 E08 |
| r/chat/state/threadScrollPolicy.ts、streamingScrollScheduler.ts；project-agent/conversation 的滚动 hook | 跟随、阅读、定位、每帧调度已有基础 | V 上滚/图片晚到/虚拟重测/恢复，不能说全部已通过 · P1 E05 |
| r/project-agent/conversation/useCardPresence.ts、useQuestionDismissal.ts；state/conversationMotion.ts | 已解决问题保留显示直至折叠；真实卡片与退出分开 | G12，V 连续卡片变化与旧闭包 · P1 E16/E17 |
| r/workbench/workbenchResizeStages.ts、browserPanelReveal.ts、browserSessionState.ts | 窄窗/分栏阶段、稳定 browser 顺序、会话身份 | G06；V iframe 越界/卸载与取消恢复 · P1 E06/E17 |
| r/app/fx/particleShatter.ts、useShatterExitCollapse.ts；styles/particle-shatter.css | canvas 粒子与 CSS collapse，CSS 已有 reduce | G11；V JS 短路与不影响真实签收 · P1 E16；特效 P2 E14 |
| apps/desktop/electron/main/tray-controller.mjs、quick-chat-window.mjs、window-routing.mjs | 托盘/原生弹选/窗口路由；不是普通 DOM 组件 | V 跨窗口焦点、关窗/重新打开、原任务目标/错误 · P1 E11/E12/E17 |
| apps/desktop/electron/main/task-notification-broker.mjs、task-notification-policy.mjs；runtime-node 的 surfacing | 原生送达/去重/前台抑制与机器人送达策略各有职责 | V 各入口对同一事实不重复打扰，通知设置遵循真实 scope · P1 E10/E11 |
| apps/tui/src/index.tsx | TUI/CLI/ACP 装配与模式路由；H，业务真值由 client/host 承担 | V 非 TTY/模式转换/启动失败/退出清理 · P1 E11/E12 |
| apps/tui/src/app.tsx | 经典 TUI；I/Q/V，普通 Composer/选择器/状态面板 | V 精确 PR198 head、Enter/LF/kpenter、保存失败、切换卸载 · P0 输入 E01/E03/E11 |
| apps/tui/src/project-agent/ProjectApp.tsx | bind/bots/conversation/cards/tasks/task/memory/objectives/diagnostics/help；H/I/Q | G03；V 每个 view 的焦点/错误/返回/草稿 · P0 E02/E04/E11 |
| apps/tui/src/project-agent/BotListView.tsx | 选择窗口/空态/行动权计数；Q | V 长名/范围变化/终端尺寸/选择锚点 · P1 E04/E11 |
| apps/tui/src/project-agent/BotConversationView.tsx | 公共回复/Markdown/引用/卡片，sticky scrollbox；V | V 用户读历史/新内容/分页、稳定消息身份与状态文字 · P1 E05/E11 |
| apps/tui/src/project-agent/CardLine.tsx | 编号/选项/选中/恢复卡及非宿主电脑批准提示；A/Q/V | V 旧编号/失效/自由回答/真实范围、键盘可达 · P0 E04/E11 |
| apps/tui/src/b3-wordmark-view.tsx | 品牌文字显示；R | 纯装饰动作态 N/A；V 窄终端/无颜色/不拖慢可用 · P2 E11/E16 |
| apps/tui/src/composer-status-view.tsx | 受控输入/上下文状态；R/V | V 未知/限流/上下文估算、长状态不挤没输入 · P1 E08/E11 |
| apps/tui/src/goal-status-view.tsx | Goal/runner 状态显示；V | V 决定/执行/核验/签收区分、窄终端静态可读 · P0 事实 E04/E11 |
| apps/tui/src/markdown-view.tsx | Markdown/代码的终端表示；V | V 长行/链接/流式/终端宽度/选择复制；不逐 token 重播 · P1 E05/E09/E11 |
| apps/tui/src/themed-primitives.tsx | ThemedText/Textarea 等宿主原语；H/R/F | V 无颜色/主题/IME/终端输入兼容；不复制桌面像素 · P1 E03/E07/E11 |
| apps/tui/src/thinking-view.tsx | 受控思考/过程显示；V | V 收起权/真实状态/历史恢复，装饰循环可静态 · P1 E04/E11/E16 |
| apps/tui/src/composer-submit.ts、runtime-controls.ts、surface-state.ts、tui-shutdown.ts、conversation-scroll.ts | 已有普通输入提交、键名、生命周期/退出与滚动 seam | V 不将经典修复泛化到 ProjectApp；按宿主判断 IME 能力 · P0 E03/E11 |
| apps/tui/src/approval-card.ts、user-input-card.ts、goal-status-panel.ts、command-registry.ts | 经典权限/自由输入/目标/命令选择 | V 回答/批准分离、无宿主权限、旧决定/未知结果 · P0 决策 E04/E11 |
| apps/tui/src/cli-argv.ts、cli-exec.ts、cli-exec-goal.ts、cli-output.ts、cli-exit.ts、cli-update.ts；packages/npm-cli 的安装/更新入口 | 帮助、参数、headless text/json、退出码、更新；无图形页面 | V 非 TTY/SIGINT/超时/无权限/部分结果；H/P/F/S 动画 N/A · P1 E11/E12 |
| apps/tui/src/acp/stdio.ts、agent.ts、permission.ts、updates.ts | ACP 是机器协议入口，现有 adapter 负责状态/批准 | V 不把聊天文本当许可/结果；断开/取消/错误的消费者语义 · P1 E04/E11 |
| apps/gateway/src/web-surface.mjs | 登录/设备/配对/任务读取的 HTML/CSS/JS 模板与路由 | V 过期/拒绝/离线/旧响应/焦点、移动窄窗；远程样式尚非共享 token 消费 · P1 E11/E15/E17 |
| apps/gateway/src/project-web-surface.mjs | 机器人页、日志、任务内联详情、输入；同 ID 重试/按 bot 草稿 Map | V 重载限制/读屏日志/加载更早的阅读锚点；现有文案明确电脑批准 · P1 E02/E11/E15/E17 |
| apps/gateway/src/account-*.mjs、remote-project-http.mjs、remote-task-router.mjs；desktop runtime-gateway/remote-project-access.mjs | 支撑上述页面的账号/授权/设备连接/结构化 API | 本轮只读作事实源；缺 UI 事实才按 A/B 补契约，不为统一外观改安全策略 · P1 E11 |

## 7. 发布覆盖映射与维护

| 本矩阵范围 | 既有 acceptance-test-guide 入口 / packet 场景族 | 新增或仍待明确的证据 |
|---|---|---|
| P01–P06/P18/P26/P55 | A–D/K/L；startup、composer-*、history-*、quick-chat-bots-*、conversation-*-failed | G01/G02/G03 的跨切换草稿、未知回执去重、IME 事件序列；原生窗口/托盘焦点 |
| P07/P10–P14/P17/P22/P24 | E–G；image-live-*、coordination-*、verification-*、completion-review-*、task-report-* | 列表/原卡/详情消费同一决定；迟到/失效/停止与取消、G12 无 API/取消终态 |
| P08/P13/P20–P27/P48–P54 | D/F/L/P；classic-*、conversationFlow/details、selection-* 等现有条件 | G05/G06/G07/G08 的键盘/拖动/错误/焦点；不能从截图推断已覆盖 |
| P15/P16/P29/P46/P47 | H/J/K；bot-memory、automation-* | G09 读失败与空、逐项写回执；编辑草稿/自动化暂停与真正重试 |
| P28–P45 | I/O/P；providers-*、settings-floating-*、fallback-vision-*、ui-appearance-* | G04/G10；全设置 dirty 离开、复制失败、200% 字号、完整读屏与对比度 |
| P56–P77 | M/N；TUI 与远程专题记录、流程5 | 精确 PR198 head；真实终端组合输入/键名/卸载，浏览器软键盘、断联/登出/授权撤回 |
| 全部 UI/动效/过渡 | O/P、体系覆盖表 U/M/T 编号 | G11；无透明/强制颜色/减少动效、反向/卸载、JS API 降级、安装包/真实模型/日用；不可用时记录限制 |

上表是现有入口到新要求的映射，不宣称现有脚本已包含新增场景。E13 在实际发布卡中注明每个 matrix ID → 用例/脚本字段/人工步骤 → 候选 commit/包 → 结果与证据；无覆盖写待覆盖，不能填 Pass。沿现有 packet/review/verify，不再造第二套验收账本。

新增页面或组件时：先补对应 P/C 行、状态模板、事实源、失败恢复、UI/M/T 语义和工作包，再实现。拆分/移除组件时迁移原 ID 责任并记录原因；不按文件数量宣称规范符合率。日常只做内容/diff 审阅，完整测试与产品回归留到发布或用户明确要求。
