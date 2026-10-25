# Peer UI、动效与过渡体系覆盖表

创建时间：2026-10-23
最后更新：2026-10-24

> 状态：规范到存量实现的映射；纳入[当前改造计划](peer-product-renovation-plan.md) E15/UI、E16/动效、E17/过渡，发布证据统一归 E13。
> 组件与页面逐项登记见[全产品交互矩阵](peer-interaction-standardization-matrix.md)。本文不另立视觉数值、运动常数、组件库或验收账本。

## Bot 文档引用只读预览（2026-10-24）

P06、FilePathCode/BotDocumentPreview，U02/U08/U14/U15、T03/T04/T08：文档候选在 Bot 上下文中可点击/键盘打开，主进程核对范围与真实文件，Markdown 默认正文；既有 file:read 契约按 ADR108 先登记。局部 Drawer 复用共享模态层、关闭归焦、动效/静态降级，不挂整套工作台或增加写入/执行入口；刷新、路径/权限错误、迟到响应沿既有资源模块，切 Bot 清临时对象。内容/diff 已审阅，边界/解析用例已补未运行，真实权限与交互验收继续 E13，不以开发服务加载替代发布证据。

2026-10-25 过渡补充（C 级）：文档预览显式消费共享 slide-inline，入场 slow（320 ms）、退场 medium（200 ms），位移沿 shift-lg（24 px）。useMotionSettled 仅在监听清理时保留 CSS 所有的动画，避免开发 StrictMode 重跑 effect 将真实入场取消；完成、减少动效/后台与有界降级仍走既有 visualMotion 收尾。落定后不保留入场 fill，读取/刷新/内部文档切换不重播，关闭仍由 Overlay 退场及归焦。补监听重跑和减少动效用例但未运行；只做内容/diff 审阅，未做截图/交互验收，本轮按用户授权提交并推送至现有 PR，不发布新版本。


## 回复中三点提示（2026-10-24）

P06/C137/C144，U02/U06/U14、M01/T01/T08：已知运行活动显示三点跳动与“正在回复”，正文不熄灭提示；done 交付中保持同一标签但静态三点，正式消息到达后收口，不插入同步/普通接收回执或刷新小字。读取不再提前清 Activity，而与完整正文快照一起应用 renderer read/push fence，迟读不盖新推送；无活动不伪造执行，异常/授权/重连/停止与恢复未知沿原状态。复用 PeerIcon ellipsis、集中 motion-dots 与时长 token，文字不额外流光；减少动效保留静态三点与标签，不新建定时器或业务事实。C 级内容/diff 审阅，状态/交接用例已补未运行，截图/交互与真实活动验收继续 E13。

## 请求通道按能力显示（2026-10-24）

P35/C050，U08/U14、T04：无可用快速通道时隐藏整个通道字段及说明，思考强度在档位参数行填满；支持时保留原通道与角色继承控件。沿既有能力判断、共享 Dropdown/焦点与布局，不写配置、不改宿主准入或解析错误，不新增动画。C 级内容/diff 审阅，未运行测试及截图/交互回归，视口/候选变化验证继续 E13。

## 档位与角色参数覆盖（2026-10-24）

P35/C050、RoutingParameterFields，U08/U14/U15、T04/T05，契约按 ADR83 先登记。档位的强度/通道在模型行下方并列展示，角色沿原六列中的参数列设置继承、模型默认/正常或显式覆盖；窄窗单列，使用既有 Dropdown/菜单归焦/MotionSurface，无新增动画。候选能力、共享解析与宿主保存预览是事实源，不能以选择动作冒充保存成功或快速通道支持；失效值保持可见、失败保留草稿。冻结参数含正常/快速贯穿持久化与执行，Bot 现有模型控件展示实际继承通道。内容/diff 已审阅，用例已补未运行，运行产物更新仅为本地开发试用；测试、截图/交互回归与真实通道证据继续 E13。

## 模型分工失效提示与六列布局（2026-10-24）

P35/C050，U08/U14/U15、T04/T05，C 级展示：失效模型 ID 显示可恢复提示，角色解析说明已保存的档位跟随关系；关系与解析取同一宿主预览，草稿不冒充已生效。单一六列布局按组内容器折为带标签的两列/单列，长文案换行，预算不再意外掉列；删除旧五列覆盖。复用原菜单/焦点/动效与保存恢复，不写配置、不自动重选模型、不改运行时或预算规则。仅内容/diff 审阅，未运行测试及截图/交互回归；宽窄窗、主题/字号/读屏、失效与保存失败候选验证继续 E13。

## 远程授权修订按需查看（2026-10-24）

P39/C038，U14/U15、T05：授权版本从普通权限标题移入默认收起的诊断 MotionDetails；沿原生 summary、共享 SVG/焦点、折叠动效与静态降级，轮询不重挂折叠对象，不额外保存或读取授权。原 delegationVersion 与后台递增/校验保持不变，仅 renderer/文案/CSS 调整；内容/diff 已审阅，键盘、轮询、减少动效与权限撤回验证继续 E13。

## 权限菜单图标与范围说明（2026-10-24）

P06/P17、C017/C124/C179，U02/U03/U08/U14、T03/T04：权限菜单局部使用 16px 连续圆角、图标/名称/原权限说明、右侧对勾及完全访问 state-danger 警示；新增可选展示字段不改变其他 Dropdown 的原布局。沿共享 portal 定位、listbox 导航、关闭归焦和 MotionSurface，说明与名称有程序化关联，普通模式与高权限有图标/文字区分。选中态继续由原宿主回执决定，不改保存/失败恢复或运行时权限规则。仅内容/diff 审阅，键盘/读屏、主题/缩放/视口、慢保存与拒绝等候选验证继续 E13。

## 头像设置移除上传（2026-10-24）

P17/C163，U02/U14、T04：移除头像上传按钮、renderer 上传调用分支与废弃文案，只保留既有预览/重新生成/颜色操作。按钮继续消费共享样式和原忙态/失败回执，不增加动画、导航或运行时边界；历史头像不变。仅内容/diff 审阅，真实重新生成、失败恢复与键盘验证继续 E13。

## 机器人入口圆角（2026-10-24）

P01/C126/C129、U03/U05、T01/T08：用户指定机器人列表行与启动页最近机器人卡片统一为 16px，两处局部消费 ui-radius-panel，沿用全局连续曲线；不改全局圆角值、布局、导航、焦点或动效。仅内容/diff 审阅并交开发服务，主题/尺寸及产品验证继续 E13。

## 暗色列表当前项（2026-10-24）

P01、BotRow，U03/U05、T01/T08：bot-list.css 仅暗色已打开行改用 chrome-active；按用户反馈去掉额外侧边标记和加亮边框，原边框/阴影保留，普通 hover 保持原色阶，浅色不变。沿 openedId 与既有稳定行身份、导航/焦点/阅读策略，不增加动效或业务状态。C 级内容/diff 已审阅，未运行测试、截图/交互回归，主题/键盘浏览与当前项、静态与强制颜色验证继续 E13。

## 历史失败卡片的消息归属（2026-10-24）

P06/C137/C144，U14/U15、T06/T08：conversationSections 只把恢复卡快照归到当前已加载的原失败消息，不将分页之外的旧失败/停止记录合成新消息插到最新回复后。原消息时间/ID/详情保留，卡片状态继续来自宿主，当前真实失败与授权/任务决定仍可见；不凭新回复把旧错误标为恢复，不改焦点、滚动策略或动效。C 级内容/diff 已审阅，补充用例未运行，分页历史/当前失败/详情与读位仍待 E13。

## Composer 模型辅助说明（2026-10-24）

U02/U06/U14、T06，P06/P34/C128：本地移除输入区常驻的当前回合模型说明段落，信息改由模型控件既有 title/aria-label 按需表达；沿原 activeSelection 与受控配置，不改模型选择/生效范围或失败恢复。仅内容/diff 审阅，输入区生成前后布局、悬停与辅助技术仍待 E13，无新增动效或运行时状态。

## 机器人设置入口与恢复（2026-10-24）

U05/U14、T01/T05/T10，P01/P06/P08/P17、C127/C162：C 级本地补修，设置按钮默认无填充，仅悬停或机器人档案面板实际展开且非 inspect 时高亮，后续按用户反馈覆盖全部页签；普通进入机器人只恢复 tab/width，旧展开与任务/目标定位不自动回放。按 workspace 归属交接偏好与抽屉，非当前对象先收起，保原手动开启、焦点与动效。无新运行时、存储位置或授权事实。仅内容/diff 审阅，状态用例已更新未运行；启动/切换/显式定位、归焦与发布候选验证继续 E13。

## 模型菜单固定浏览基准（2026-10-24）

代码实现：[5c1394b7](https://github.com/ly-ccx/Peer-Agent/commit/5c1394b7)，包含本节定位与下节选项间距修复。

U08/U11、T03/T09、P17/P34/C114：本地 useModelSelectionPosition 复用共享锚定定位，每次打开只记录一次高度，内容变化不再驱动上/下翻转；保留打开时最小高度、视口内高度上界与局部正文滚动，提供商入口不随正文移动。真实触发器/视口移动仍避让边界，关闭重开重置基准；不重挂选项面板或重播入场，不改已选值、保存与焦点层级。仅内容/diff 审阅，长短提供商切换、内容增长、窄窗/滚动/重开及静态降级的候选验证仍待 E13。

## 模型菜单选项间距（2026-10-24）

U03/U08、P17/P34/C114：服务商与模型候选列表复用 space-1 留 4 px 行间隔，避免相邻选中和悬停背景粘连；T03 的受控选值、浏览、键盘与菜单身份保持原样。C 级本地 CSS 补修，仅内容/diff 审阅，未运行测试、截图或交互回归；长列表/滚动/主题与发布验证继续 E13。

## 档案模型保存反馈（2026-10-24）

P17/C114/C128/C161/C163，U08/U14/U15、M01/M08、T03/T06：基线 `53eb9850`，实现提交 [6176ca67](https://github.com/ly-ccx/Peer-Agent/commit/6176ca67)，根据既有 pending/已保存 policy 的角色差异局部显示保存忙态，组级正常保存提示不占位；共享选择面板区分写锁与不可用态，保存期间允许浏览而阻止重复写入，其他角色和候选列表不因保存一起变灰。沿原持久回执、保存锁、失败恢复、层级/焦点与动效收尾，没有新状态真源或运动常数。范围与限制见[交互矩阵](peer-interaction-standardization-matrix.md#档案模型保存局部反馈2026-10-24)。仅内容/diff 审阅，慢保存/失败恢复/跨角色阻写、真实焦点/读屏和发布验收继续 E13。

## 服务商设置局部布局（2026-10-24）

U02/U03/U04/U08/U14，P33/C002/C013/C026：基线 `7b6c9972`，实现 [53eb9850](https://github.com/ly-ccx/Peer-Agent/commit/53eb9850) 统一连接/模型/用量的内容边线，展开模型使用稳定 paper-sheet、局部 hover 使用 paper-hover，可读参数使用 graphite-soft。复制/删除收至既有 OverflowMenu，测试/设置留在操作区；来源/同步时间使用帮助文字色与紧凑本地时间，完整时间仍可查看。范围和状态责任见[交互矩阵](peer-interaction-standardization-matrix.md#服务商设置布局局部补修2026-10-24)。M05/T03/T05 沿用 MotionDetails/SettingsDisclosureContent/共享菜单层级，展开静态终态释放菜单溢出，未改展开事实、键盘、焦点、恢复和动画收尾。仅内容/diff 审阅；菜单开合/禁用/删除回执、各主题/200%/窄窗、辅助技术及发布验收继续 E13，不以热更新交付作为已验收证据。

同范围 C013/U11/T02 复用 ConfirmProvider 给单模型删除增加具名确认，仅确认后调用原删除回调；取消/关闭不删。沿共享模态/归焦/退场，无新权限或业务状态。仅内容/diff 审阅，确认/取消/关闭、键盘与实际删除回执待 E13。

## PR214/215 合并与本地验证（2026-10-24）

用户明确要求本次提前本地测试，覆盖范围不再沿用上批“未运行”的交付状态。PR214 修复共享 MotionDetails 的 ref 类型、测试夹具接线与 UI 退场终点；PR215 保留防闪烁与快照稳定性，并整合共享入口。没有修改原主工作区 dirty 或个人模型配置。

入场收尾复用 useMotionSettled → visualMotion，不采用 PR215 初版 400/280ms 固定 timer；MotionSurface、Overlay 与档案 pane/push 在真实结束后解除入场 fill/过渡，普通数据刷新不重播。保留原 trigger resize 定位、保存期间的选择防重和失败恢复；头像读取按真实资源键，目录/模型/会话事实不变时保留引用，选中/高亮仍独立核对合法性。

退出的 CSS finished Promise 不能抢在原生终点事件前取消 fill；Overlay 保留终点到原生 end/下一帧，并沿原有 2s 硬上界处理无事件/停帧，静态/拒绝/隐藏仍立即收尾。升级弹窗测试保留真实中点/去向/终点，额外观察原生 end 后 React 的关闭提交；没有放宽几何或制造成功事实。

验证结果和实际合并标识见[本地验证记录](../../playbook/v0.1.0/surface-motion-merge-validation.md)。仍非完整发布包验收，真实服务、安装版、读屏及跨平台限制继续 E13。

## 菜单、浮层、抽屉与设置过渡复核（2026-10-24）

E16/E17-F5；基线 040a3e1b，本批代码 [59451598](https://github.com/ly-ccx/Peer-Agent/commit/59451598dc513e0702bbacc961c1b366f73efbe3)。全量按生产源码的 portal、menu/dialog/tooltip/listbox、共享 Overlay/Drawer、独立窗口、设置页和折叠区归类，补齐兼容经典入口；[逐文件清单与关闭例外](../../playbook/v0.1.0/surface-motion-sweep.md)。下表 S 均为内容/diff 自审，V 全部仍交 E13，不能沿用此前点查来验收本批代码。

| 家族 / 对象 | UI 与入退场实现 | 交互/中断/静态责任 | 状态 / 排程 |
|---|---|---|---|
| F5-01 共享 Dropdown / CascadingMenu 根与子层 / OverflowMenu | C214 单 DOM 载体，medium rise 或 fade；fast fade 退场，原 token/方向 | 受控 open 立即停 layer/控件；portal 测量子层用 fade 防坐标受 transform 扰动；旧退出取消 | S；V 子层/全禁用/锚点消失/IME/Tab/反向 · E06/E16/E17 |
| F5-02 设置应用菜单 AppMenu | 移除上次局部 watcher，直接复用 C214 | 保原菜单键盘/导航与 metadata 归焦；不等退场才导航 | S；V 设置/历史/能力往返与重开 · E16/E17 |
| F5-03 Sidebar 目录弹层及项目/会话右键菜单 | 目录 rise；两个 context 分支共用一个 fade 载体/ref | 原操作立即派发；单所有者避免旧退场 ref 清掉新菜单 ref | S；V 目标切换/删除/外点/归焦 · E06/E17 |
| F5-04 ChatHeader 与能力开关菜单 | C214 接既有 DOM 和 layer | 不重建会话/权限状态，背景刷新不重播 | S；V 快速切换/已禁用项/键盘 · E16/E17 |
| F5-05 模型主面板及服务商子菜单 | 主面板 rise，服务商 fade，Context 保留在载体外 | 浏览/保存受控值与 Promise 回执保留，关闭即停用；旧退场不拥有新 ref | S；V 保存中重开/失败/子层/slider/窄窗 · E08/E16/E17 |
| F5-06 独立强度/上下文用量面板 | C214；ResizeObserver 缺失可静态定位 | 原数据/选择和层级不变，异步回读不重新入场 | S；V API 缺失/窗口变化/键盘与归焦 · E16/E17 |
| F5-07 配色选择 PaletteSelect | 移除私有 160ms timer、强制 reflow 和局部退出样式；共享载体 | 接共享 layer/Tab/IME，保 listbox/选值；aria-controls 对应真实打开面 | S；V 快速选值/主题/外点/归焦 · E06/E16/E17 |
| F5-08 slash 命令、文件/会话 mention | 两处 C214，保原候选与输入边界 | 不以视觉缓存接收输入；关闭不改 composer 草稿或提交 | S；V IME/候选消失/读位/异步迟到 · E03/E16/E17 |
| F5-09 页内查找条 | 单次 fade 入退场 | 真实 open 控制 layer/高亮/查询；隐藏实例不运行查找或清别处高亮 | S；V 多会话/关闭后重开/原焦点 · E05/E16/E17 |
| F5-10 Tooltip / BotSelectionQuote / SelectionQuoteAction | fade；原悬停宽限/选区/确认保留 | 不夺焦点；选区失效不产生新引用，动画只保留旧画面 | S；V 锚点失效/确认/键盘/选区位置 · E06/E09/E17 |
| F5-11 任务产物悬停与 Diff 文件预览 | C214 fade，锚点 identity 被动 layer；晚内容重定位 | anchor 移除/Escape 可关，不夺焦点；关闭清 scroll/resize/observer | S；V A→B 锚点/解码/窄窗/事件清理 · E09/E17 |
| F5-12 外部打开 split / Browser overflow | C214，业务打开/导航仍立即 | 保原真实目标、外点/键盘与 guest 身份 | S；V webview/外部打开失败/归焦 · E09/E17 |
| F5-13 全部共享模态/确认/Sheets | 28 个 Overlay JSX 点（含 Drawer 适配）；原 backdrop fade、panel rise/fast sink/目标交接 | 纯 close/cancel 统一 requestClose；异步准备失败不退场；接受后立即 inert，watcher 有界完成 | S；V 逐源清单的嵌套/dirty/保存/无事件 · E08/E16/E17 |
| F5-14 会话/选区/Evidence/核验/MCP/档案 cover 抽屉 | 8 个 Drawer JSX 点；原 inline-slide、逻辑方向/RTL 边框 | 补内部绕过；选区 save 成功才退出，失败/新编辑留现场，旧代次失效 | S；V 保存失败/迟到/原焦点/窄窗/RTL · E02/E08/E17 |
| F5-15 档案 push / TaskMonitor rail | 档案保原 width/opacity 与双帧入场，真实 CSS animation watcher 取代固定 360ms；rail 保 presence | 关闭即 inert/aria-hidden；重开撤销旧退出，原 width/ID/状态保留 | S；V push-cover/拖动/偏好/反向 · E06/E16/E17 |
| F5-16 经典 GoalPlan 侧栏 | 移除私有 200ms 常量；共享 medium token/watchVisualMotion 承接现有宽度过渡 | 收起即 inert；反向/隐藏/卸载取消旧收尾，清宿主 data-closing；决定立即派发原回调 | S；V 强制展开/切会话/旧侧栏/焦点 · E04/E16/E17 |
| F5-17 设置框架与 12 个公开分区 | settings-content key=section 一次 fade，移除整页+每子项叠加 rise | dirty guard 先处理编辑，async 数据刷新不重播、不新增状态小字 | S；V 搜索/深链/快速往返/焦点/读位 · E08/E16/E17 |
| F5-18 服务目录/已连接视图 | 一次共享 fade 交接；移除 170ms 私有退场及逐组/逐卡延迟 | 已就绪视图直接承接，筛选不重新级联，模型设置/目录确认仍沿原 Overlay | S；V 长目录/过滤/返回/编辑状态 · E08/E16/E17 |
| F5-19 设置高级区/视觉兜底/自动化高级表单 | 保既有 SettingsDisclosureContent/grid/reducer | 保原 expanded、收起后 inert、可取消收尾与焦点；不另造折叠状态 | S 沿用；V 反向/动态控件/保存中 · E08/E17 |
| F5-20 原生 details：模型行、档案设置/任务/记忆/目标/Evidence/过程/诊断、资源旧值/自动化比较、后台日志 | C215：13 模块 17 处；CSS 支持检测后 height/opacity/content-visibility，完成释放 overflow | 保 details/summary/open/onToggle/ref；共享取消/降级；无支持保持原生静态 | S；V 嵌套/快速开合/默认 open/读屏/控件溢出 · E06/E16/E17 |
| F5-21 原生 Quick Chat 弹选窗口 | DOM 每次真实打开一次 fade 入场；退出依主进程/OS 即时隐藏，既有 closed 事件同时送达独立菜单宿主清旧内容 | 不延迟选择/失焦/hide IPC，不另造窗口许可/状态 | S；V 真窗口重开/焦点/旧事件/多屏 · E11/E13 |
| F5-22 OAuth 授权码、保存完成/切页/目标交接 | 保共享入场；这些结束由真实流程或目标页面立即承接 | 删除 noop onClose，Escape 不再把待授权面淡为空壳；真实完成不为动画等待 | S；V 授权完成/失败/重复 Escape/目标消失 · E08/E13 |
| F5-23 Workbench tabs/browser keepalive、历史正文/行内技术详情 | 保原局部 tabs/折叠/静态阅读，不额外 remount guest 或重播历史 | 这是内容/对象连续性；不因“全产品动效”给每条历史补入场 | S 沿用；V 真实 guest/读位/焦点 · E05/E11/E13 |
| F5-24 Gateway 两网页、TUI/CLI/ACP、系统 select/dialog/context menu | Gateway 原生 select/行内面；终端无 DOM；系统窗口按宿主绘制 | DOM 动画 N/A/有意静态，无跨宿主 renderer CSS；业务与原生选择保持即时 | 源码登记；V 真宿主/辅助技术 · E11/E13 |

本次专项已验证的 F5-02/05/13/15/17/20 子用例及源头见本文顶部 PR214/215 记录；不能将专项通过扩展到整行全部 V，以下为原始批次的完整待核列表。

本次 U08/U11/U13/U14、M02–M06/M18、T01–T04/T08/T09 的消费者补齐以本节为当前进度。减少动效/隐藏/缺 API/结束拒绝由既有 motionEnvironment/visualMotion 和 CSS 静态终态承接；没有新 keyframes、运动常数或动画库。支持检测后的原生尺寸过渡仍有短时布局成本，不宣称帧率或辅助技术通过。E13 必须在最终合并候选逐项核对反向、卸载、失焦/锚点移除、保存失败/期间新编辑/迟到、ref/读位/IME/RTL、reduce/隐藏/API 失效及原生窗口。

## 全 PR 汇合后的体系补充（2026-10-24）

来源与合并门禁见[交接记录](../../playbook/v0.1.0/experience-ui-motion-transitions.md#全部-pr-汇合与模型强度补齐2026-10-24)。U06/U07/U08/U10：全局角色思考强度复用 Dropdown、既有 effort 文案/能力声明，tier/fixed/auto 选择与模型关系独立，单模型可设、失效可清除、宿主预览显示真实已保存强度。C114/C128 的统一面板保留受控模型/强度，滑块待真实回执收尾，忙碌入口保持归焦并阻止重复动作。U14/T09：C212 档案拖动保留宽度记忆，列表及档案均接共享 pointer resize，隐藏分隔条 inert。

M01/M02/M04/M18：沿原 motion token/静态收尾；合并 PR204 双帧入场与 E17 中断/层级，没有新运动参数。T02/T08：C031 仅在自身 Layer 仍注册且居顶时捕获焦点，退出清理后不重捕获版本入口的归焦。T01/T04/T06：配置继承不因调整强度变成固定模型，恢复候选守住显式强度；TUI 卡片焦点/引用回显保留原 draft 和真实行动回执。T05：E05 原生 scroll 捕获手势后的实际锚点，React 延迟投递不拉回旧位置；卸载释放 listener，回最新沿原入口。T04/T06：问题关闭只由 canonical/received 回执驱动，unknown 保留原选择与输入身份，不用退出动效代替回答事实。测试夹具类型、模块行数上限和 SDK 既有撤回事件类型补齐是合并修复，不以断言放宽替代行为依据；M01/M02/M05：C213/ConversationRow 沿共享 motion-enter-layout、medium/standard token 展开新输入/等待回复占位，保原 key/DOM；无插值/API、reduce/隐藏静态收尾，不重播历史/虚拟重挂载。已解决问题在 React 移除前固定零占位，避免 cancel fill 回弹。T02/T08：问题动作前记录焦点归属，真实 resolved 时交本地 composer，reduce 即时移除也成立；外部点击/焦点外移/后台不抢回，监听器清理。页脚几何在同一帧取样，门限不变。完整发布覆盖仍按 E13。

T02/T08/T09：C162 档案先登记 Layer 再进入 scope，零层级不拥有焦点；响应式窗口检查等待旧 scene 与实际有限动画收尾，随后核对新对象。更新快速完成夹具由真实 download 调用触发，避免远程命令迟到；保留内容、几何、完成时序及焦点门限，不以测试夹具制造产品事实。

T05/T06：C138 对同帧多次几何提交增加一次有界贴底复核，只采纳当前 pinned；用户读历史后不恢复跟随，离开取消、空闲停帧。U10/T04/T06：C123 期限只触发一次宿主重读和父计数刷新，真实回读才移除行，保失败快照与手动重读，不以 clock 生成决定事实。

M05/T04：问题收起的窗口从真实 resolved 投影开始，回执等待单列；点击起的输入/滚动帧、原 650ms 关闭窗、去重与归焦仍核对。不能以 timer 要求未收到回执的卡片提前完成，夹具死锁上限不代表产品性能通过。

## 基础交互点查补充（2026-10-24）

用户授权提前点查，代码 `a0ae1a33` / [PR213](https://github.com/ly-ccx/Peer-Agent/pull/213)；[路径与限制](../../playbook/v0.1.0/experience-ui-motion-transitions.md#用户授权的基础交互点查2026-10-24)。C 级渲染身份和入口修复，没有新增动效常数、组件体系或运行时边界。

| 体系 | 本次实际确认 | 保留覆盖 |
|---|---|---|
| UI · U06/U08/U10/U11/U13/U15 | 修复消息/输入框重复 key 的内容叠影；12 个设置分区、五个档案标签、任务/Evidence、搜索、菜单和新建取消可操作；自动化新建到编辑器 | 未作全主题/200%/读屏/布局验收；真实写入/失败仍依各行 V |
| 动效 · M01/M02/M04/M18 | 本机真实浏览器 request/cancel 首帧与退出用例通过；实际菜单/浮层/抽屉打开关闭完成，无再次崩溃 | 未切换减少动效、透明度或注入 WAAPI 异常；G11/G12 全覆盖仍待 E13，不能以正常开关替代降级验证 |
| 过渡 · T01/T02/T06/T08/T09 | 页面往返保留本 bot 草稿和阅读模式；回最新只有单个入口；抽屉 Escape、模型/权限菜单及附件取消、Evidence 返回原入口；dirty 设置继续/舍弃 | 未验证跨 bot/窗口/真实 IME/未知回执，崩溃页恢复未重演；正常开发窗口重载能恢复首屏并重开对话 |

三项针对性检查通过；无独立评审或发布验收。下文“未运行”为当批历史记录，本次只补充明确列出的路径，其他 U/M/T 覆盖不升级。

## 回复状态与后台刷新补修（2026-10-24）

E16/E17-F4，P1；U08/U11、M02/M04/M18、T03：C122 设置应用菜单补 motion-enter-rise（medium/shift-sm）及 motion-exit-fade（fast），不另设运动常数。关闭态的静态 opacity 为 0，并立即 inert/aria-hidden；watchVisualMotion 处理结束/拒绝/有界兜底、reduce/隐藏/API 缺失与重开取消。焦点和导航沿真实 open 立即处理，不等动画，保阅读位置。只审阅内容/diff，实机开关、反向、偏好/无事件与归焦仍待 E13。

E07/E17-F3，P1；U02/U03/U12、T06：回复身份恢复正文级名称、32 px 头像及 8 px 分组间距；别名定位节点脱离 flex，空正文载体不产生段落留白。原 ID、连续回复载体与阅读意图策略保留；M01/M18 无新动画/常数或偏好分支。仅 CSS 与内容/diff 审阅，多别名、无正文失败、长名/字号、引用与阅读锚点仍待 E13。

E08-F2，P1；U08/U14/U15、M08、T02/T06：补齐主动保存的反馈归属，对话不再插入“正在保存”段落；原模型按钮沿共享 SVG/motion-spin 和 reduce 静态路径表达真实在途状态，原浮层接失败/重试/舍弃。选择锁定不阻止重开状态菜单，关闭后失败入口留标记；抽屉反馈归模型设置组。无新动画常数、成功计时器、自动开层或焦点跳转；保存事实与 pending 生命周期不变。只完成内容/diff 审阅，慢保存、失败后关闭/重开、窄窗/键盘/读屏与 reduce 均待 E13。

U12/U15/U16、T06/T10，E08/E11-F1：跨宿主同一模型能力投影补齐 TUI 强度元数据，修复已声明强度误拒绝；非执行宿主的重试说明接管位置。历史本地校验拦截不冒充模型服务拒绝，沿原租约交接，不增加动效或业务重试。B 级实现已审阅，实际 TUI/声明强度边界用例未运行，完整覆盖待 E13。

E04/E08-F1，P1；U12/U14/U15、M08、T06。真实活动阶段不再被固定时长覆盖，公开正文接住普通进展；权限/恢复/停止仍显式，接收/未知/终态不冒充活跃模型。设置回焦重读保留已有控件和布局，不向对话添加瞬时加载提示；首次读取只在设置现场显示，真实错误和恢复入口保留。无新动画、最短等待或业务计时，沿现有连续回复/详情与减少动效路径。

实现与内容/diff 已审阅；现场只读状态观察不能证明动态等待/读屏/reduce/隐藏恢复或模型端速度。测试和最终候选回归待 E13，见[本轮记录](../../playbook/v0.1.0/reply-status-feedback-20261024.md)。

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
| U02 字体与信息层级 | S sans/mono、12/13/14/15/16/20/26 等语义档，正文行高和阅读列已有 token；E07/E17-F3 回复名称采用正文字号/主文字色 | V 页面主标题/紧凑标题分工、200% 放大、中英长名/路径/代码；不靠缩小字号压进窄窗 | P1 · E07/E15 |
| U03 几何、间距与密度 | S 8/12/16 曲线、`superellipse(1.4)` 支持检测、space 与 SettingsGroup；E07/E17-F3 回复头像/身份间距消费共享 token，别名/空正文不占 gap；S E15 共享 ChoiceStrip/文件输入与远程普通/紧凑几何 | S E07/E15 当前消费者已审阅；V 200%/窄容器/长名和其他存量 | P1 · E07/E15 |
| U04 表面、玻璃、边界与层级 | S chrome/paper/control/glass、overlay、共享 settings-floating；正文稳定底面 | V 嵌套 blur/透明降级/强制颜色、局部 z-index/portal 与模态的交互边界；原生材质需安装包实测 | P1 · E07/E15/E17 |
| U05 按钮/图标/链接 | S PeerIcon/SVG、原生 button、stone/graphite 主操作与已有 focus token；S E15 文件确认/取消 SVG、MCP 按钮/复制失败反馈、远程 focus/target | 当前消费者已审阅；V 读屏/实际目标尺寸/强制颜色及其他操作 | P1 · E06/E15；关键决定 E04 |
| U06 输入/文本编辑/Composer | S 受控 BotComposer、Quick Chat/TUI shared recovery kernel；正文/引用/附件/pending 先保存，匹配 input 确认；经典沿旧持久 seam；E11 远程 composition/229、原请求回执与会话 draft，终端卡片焦点/编辑分开；S E15 C211 文件名 IME/keyup/repeat、失焦留名、明确确认/取消，写入失败保原编辑 | E02/E08/E11/E15 当前路径已审阅；V 真终端/软键盘/读屏/重开与原持久化限制 | P0 E02/E03；P1 E08/E11/E15 |
| U07 Checkbox/Switch/枚举/Slider | S boolean-controls 原生 checkbox/role=switch；AppearanceSlider/ReasoningEffort/EffortRange；S E15 C210 本地 radio、嵌套 Switch 键盘不触发卡片、真实开关回执与逐项 pending | E08/E15 当前消费者已审阅；V 真实设备/读屏/其他 slider/switch 与未知回执 | P1 · E06/E08/E15 |
| U08 搜索/Dropdown/菜单/tooltip | S Dropdown/CascadingMenu/OverflowMenu/查找/tooltip 共用层级、IME/Tab/外点/归焦；过滤 radio、真实 listbox；E08-F2 模型浮层承接配置失败恢复，入口保留状态提示；E16/E17-F4 AppMenu 共享入退场、关闭即停用 | S E08 C114 纳入共享层级/IME/roving，浏览不写入；G07 已审阅；V 无模型/失效与跨窗口 | P1 · E03/E06/E15 |
| U09 tabs/分段/资源标签 | S Capability/Workbench/档案/Resource tabs 有键盘/roving/panel；昂贵视图手动激活，关闭回相邻；S E15 Capability/Skills tabs 改复用 C210，同 panel 关联、焦点/选择分离 | G05/E06/E15 当前消费者已审阅；V RTL/多实例/失效/动态关闭和 guest | P1 · E06/E15/E17 |
| U10 行/列表/卡/表格/图表 | S BotRow/TasksTab/AttentionSheet、SettingsGroup、UsageStats/Automation 表格、WorkStream；E12 Desktop 四页续读、TUI 50 条公共投影、远程单页/ID 去重/显式缺口与锚点；S E15 installed/available 读失败保快照，文件创建原 scope，E16 FLIP 收尾 | a0ae1a33 对话重复 key 修复，基础列表/对话点查通过；当前路径已审阅；V 跨列 remount 焦点/锚点与真实大列表，其他列表仍待核 | P1 · E05/E07/E11/E12/E15 |
| U11 模态/抽屉/面板/原生弹选 | S modal/push/anchored 共用逻辑父子；Overlay native inert/Tab/focusin、允许自有 portal、幂等退场/恢复触发者；S E16/E17 共享 visualMotion 处理退出拒绝/无事件/隐藏，rail 重开取消旧退出 | 当前路径已审阅；V 嵌套/源消失/反向/归焦/原生窗口 | P1 · E06/E11/E15/E17 |
| U12 消息/过程/决策/结果 | S CardView 不再 generic ok→done；实际 approval/current card + 当前核验/验收真源；TUI cancel 独立不授予执行；S E17 经典授权点击立即交原宿主回调，问题关闭只清显示 footprint | E04/E11/E16/E17 当前路径已审阅；V 迟到/过期/跨入口事实/实际焦点，不从动画造许可 | P0 事实 · E04；P1 表达 E11/E15/E17 |
| U13 附件/引用/产物/媒体预览 | S QuoteChip/ReplyAnchors、BotAttachments、ImageLightbox、Markdown/Source/Diff viewers | S E09/G08 图片/文本/元信息、原 ID 定位、Evidence/文件分别可达和失败重读已审阅；V OS/解码/旧源/局部阅读/长内容与键盘 | P1 · E09/E15/E17 |
| U14 设置/资料/能力/自动化编辑 | S SettingsGroup、12 个公开设置分区、bot 五 tab、能力/自动化各表单；E08-F2 模型反馈归原控件/设置组；S E15/E17 Skills/MCP reader/真实回执、敏感编辑 dirty 离开/显式舍弃；无新增缓存 | E08/E10/E15 当前消费者已审阅；V 外部变化/未知/部分写入与未触及表单 | P1 · E07/E08/E10/E15/E17 |
| U15 空/加载/失败/失效/恢复与通知 | S 对话渐进读取、pending/stop/error、updater phase、后台记录、受管 surfacing 与通知；E12 bootstrap 重读/旧壳层与历史继续，E11 远程详情/设备保快照；S E15 能力/Skills/MCP 真空只由成功读取确认，失败保快照/重读、数量未确认 | E08-F2 模型保存不插对话小字，失败/待恢复仍可见；当前路径已审阅；V OS/迟到/未知/部分写入与真实通知，不批量判定其他空态 | P0 关键事实 E04；P1 E10/E11/E12/E15 |
| U16 跨宿主与可访问性 | S E11 按 host 对照事实、输入、许可、恢复；终端主题原语/焦点，远程原生表单/静态状态；CLI/ACP 图形态 N/A；S E15 Gateway 原生表单角色适配、coarse target/强制颜色，不照搬 Desktop CSS | 当前路径已审阅；V 真终端/软键盘/读屏/200%/跨窗口/安装、完整视觉对照 | P1 · E11/E13/E15 |

UI 的交付单位是“一个角色 + 全部适用状态 + 实际消费者”，不是一张默认截图。并非每个角色要新建通用组件；已有共享接口优先，临时例外标注范围/原因/替代路径/退出条件。不得为了统一布局更改权限、Context Source 或存储。

## 3. 标准化动效体系

数值仍沿用 fast/medium/slow = 120/200/320ms、shift = 6/12/24px 和既有 easing；这里只登记语义与责任。历史 `za-*` keyframe、集中 `motion-*` 和 JS 表现都在治理范围，集中存放不等于每个效果都应该推广。

| ID / 语义 | 现有实现与适用消费者 | 差异/退出要求 | 排程 / 任务 |
|---|---|---|---|
| M01 控件即时回执 | S token 驱动 hover/pressed/focus、共享 button/switch/checkbox CSS；S E15 共享 ChoiceStrip/文件确认/MCP 反馈与远程 focus/pressed | 本批控件状态已审阅；V 对比度/目标尺寸/其他消费者 | P1 · E15/E16 |
| M02 fade/rise/pop 入场 | S `motion-enter-fade/rise/pop`；settings/menu/轻层及部分页面；S E16 motionEnvironment/visualMotion 接入相关消费者；E17-F4 C122 rise/shift-sm | 当前路径已审阅；V 静态偏好/重复打开/其他入场和动画 API | P1 · E16/E17 |
| M03 inline slide 抽屉 | S `motion-enter/exit-slide-inline`；Drawer/档案覆盖层；S E16 档案 push 监听偏好/隐藏，关闭中断不留旧 out timer | 当前路径已审阅；V RTL/方向/push-cover/resize，PR204 未纳入 | P1 · E06/E16/E17 |
| M04 fade/sink/pop 退场 | S motion exit 与 Overlay 自带 CSS/fallback、useMotionPresence；S E16 Overlay/presence 共用 watchVisualMotion，幂等 finish/cancel、有界 fallback；E17-F4 C122 fast 淡出、关闭即 inert，重开取消旧收尾 | 当前路径已审阅；V 缺 API/无事件/拒绝/反向/嵌套/真实归焦 | P1 · E16/E17 |
| M05 fold/grid/height | S SettingsDisclosureContent、BotProcess/details、问题的 WAAPI 高度折叠；S G12/E16 问题 animateVisual 静态/无 API/拒绝/fallback，disclosure 同收尾 | 当前实现已审阅；V 快速反向/无触发者/卸载/旧 promise 与实际焦点 | P1 · E06/E16/E17 |
| M06 分段/选值指示器 | S BotDrawerSegments/PaletteSelect/模型强度相关 transform/transition；S E15 C210 本地 radio/手动 tabs，选择指示由受控值决定 | 当前消费者已审阅；V 真实键盘/RTL/快速反向/其他选择器 | P1 · E06/E15/E16 |
| M07 新消息/用户待发气泡 | S 保留 UserBubble/连续回复载体；恢复 kernel 延续 inputId，unknown 不制造进行中回复 | G01 实现已审阅；V arriving 最多一次、公共 echo/重开静态；未新增动画 | P0 输入 E02；P1 E16/E17 |
| M08 执行状态循环 | S `motion-pulse-soft/attention`、spin/dots、真实 activity/status 消费；S E16 ThinkingOrb 动态偏好/隐藏暂停，typewriter 停 rAF 并交出已收到文本 | E08-F2 保存忙态沿共享 motion-spin/reduce，真实回执结束，无成功循环；当前消费者已审阅；V 其余 CSS 循环/真实离屏/能耗与正文思考交接 | P1 · E04/E16 |
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
| T03 菜单/提示/锚定 | S Dropdown/CascadingMenu/Tooltip、anchoredOverlay 与原生 QuickChat popover | S E08 统一模型菜单加入 shared owner/键盘/锚点失效关闭；E17-F4 设置应用菜单补入退场与静态终态，动作不等动画；V 定位/窄窗/真实跨窗口/反向与归焦 | P1 · E06/E11/E17 |
| T04 标签/分段/分区 | S SettingsPage、BotDrawerSegments、ResourceTabStrip、CapabilityTabs、模型面板；S E15/E17 Capability/Skills tabs 和 MCP radio 共用 C210；切离 MCP 经 guard | 当前消费者已审阅；V 快速竞争/失效选择/旧设置消费者与真实焦点 | P1 · E06/E08/E15/E17 |
| T05 折叠/展开/详情 | S SettingsDisclosureContent、BotProcess、ReplyDetails、问题 dismissal；S G12/E16/E17 无 API/拒绝/无事件静态收尾，原问题持焦点才交本地 composer | 当前实现已审阅；V 反向/卸载/旧闭包/背景解决不夺焦点/真实系统 | P1 · E05/E06/E16/E17 |
| T06 待发/接收/连续回复 | S shared recovery kernel + device store，完整 envelope 先保存；匹配 input/public echo 确认，同 ID retry；30秒只结束界面等待；E11 远程匹配原 requestId+ok+received 才确认、手动同 ID 重试；S E16 静态/后台直接交出已收到文本，停止显示泵；无新请求/正文 | E07/E17-F3 连续回复别名定位保留且不占段落间距；E08-F2 模型设置不插入对话布局，保存反馈留原位置；E02/E11/E16 当前路径已审阅；V 正文/思考/工具交接/取消、未知与真实宿主 | P0 · E02/E03；P1 E11/E16/E17 |
| T07 决策/执行/核验/交还 | S 结构化 approval/current card 与 lifecycle/verification/acceptance 真源分开；旧展示记录不盖当前授权/验收；S E17 经典授权立即交原回调，同展示对象防重；移除动画派发延迟 | E04/E16/E17 当前路径已审阅；V 宿主 grant/过期/拒绝/取消/未知/核验与签收分开 | P0 · E04；P1 E17 |
| T08 列表增删/排序/分页 | S BotList/TasksTab/Memory/Files、MessageQueue、WorkStream/virtual pager；E12 Desktop 四页衔接、远程单页/显式缺口/锚点、TUI 同目标在途公共页合并；S E15/E17 文件名失焦保留/显式创建，原 scope 回执、失败留现场/条件归焦；E16 FLIP 中断 | 本机历史阅读模式与单个回最新点查通过；当前路径已审阅；V 完整树键盘/目录并发/跨列 remount 焦点与实际阅读，其他列表仍 V | P1 · E05/E06/E10/E11/E12/E17 |
| T09 预览/分栏/最大化 | S ImageLightbox/Document/Browser、WorkbenchResize、档案 push/cover；S E16 push 档案的隐藏/偏好与静态退出已接共享收尾 | 当前路径已审阅；V guest/resize/窄窗/旧源/真实辅助技术，PR204 待集成 | P1 · E06/E09/E17；共享元素 P2 E14 |
| T10 启动/主题/升级/宿主恢复 | S bootstrap reader/真实就绪、AppearanceProvider、VersionBadge/updater、host lease/恢复投影；E12 删除 minHold、按真实就绪/失败重读保旧壳层，E11 模式/页面恢复使旧请求失效 | G10 当前实现已审阅；V 主题保编辑/徽标承接/关窗不取消、未知执行不重放、备份一致性/身份与安装包恢复 | P1 · E11/E12/E16/E17 |

## 5. 发布验收与进度记账

E15–E17 的实现卡必须引用本表 U/M/T 编号和对应 P/C 行，写明允许文件、状态事实源、已有 seam、取消恢复与降级。一个实际修改可同时关闭多行的同一差异，但不能只改共享 CSS 就把所有消费者标成达标。

进度字段使用：已登记 → 待实现 / 待核 → 实现已审阅 → 候选验证通过（绑定 source/包/证据）。S 不是流程状态；文档提交只完成“已登记”。隐藏/兼容入口注明范围，暂不实现的例外有退出条件，不标 Pass。

普通任务只审阅内容/diff；不自动跑测试、截图、构建或类型/架构/IPC 检查。发布时按 E13 和[验收指南](../../playbook/v0.1.0/acceptance-test-guide.md)将本表映射到既有场景，补没有覆盖的键盘/焦点/IME/取消/减少动效/API 降级及宿主验证，再在合并全部 PR 的最终候选运行完整门禁。不能用截图数量或旧版本 Pass 代替这些行为证据。

## 2026-10-25 预览相对来源选择（T02/T09）

文件候选不再仅由斜杠推断，分支／引用语义保持原文；相对文件找不到且存在其它已确认来源时，在原 BotDocumentPreview 中提供完整位置选择。候选不直接交付正文，选择后仍按宿主当前范围读取。明确来源不自动切换，原请求身份与迟到隔离继续由 useResourceRead 管理。

来源选择保持同一 Drawer，不重新播放入场；选择动作将焦点交给稳定标题，关闭仍回最初对话入口，不改变会话读位。复用原组件、token、动效与减少动效收尾，没有新动画或业务计时器。状态：实现与内容/diff 自审，新增用例未运行；已按明确授权正常重启实验室实例，原任务、成果与其他本地改动保留，不发布；启动确认不作为交互／辅助技术验收。

## 历史子任务活动动画（2026-10-25）

P06/C133、AgentActivityRow，U06/U14、M01、T06/T08/T10：保留原 started／reported／ended／cancelled 历史事件、文字、消息 ID、图标身份与任务入口；动画单独消费按 sessionId 关联的既有 BotWorkIndex 宿主当前快照，仅 starting／running／verifying 允许活动行跳动。已结束、取消、等待、排队、停止中、快照不可读或找不到子任务时静态呈现；状态暂不可读不回退历史 started，减少动效沿原静态规则。BotConversation 只将已有索引传给活动行，不新增轮询、计时器、执行、存储或协议路径，不重跑任务或写入。C 级内容/diff 审阅；同任务结束/取消、并行隔离、读取失败与历史保留用例已补未运行，未运行截图/交互回归，本地开发服务热更新供用户试用，发布验证继续 E13。
