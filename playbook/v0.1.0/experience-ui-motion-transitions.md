# E15–E17 实施交接：UI、动效降级与过渡连续性

创建时间：2026-10-24
最后更新：2026-10-24

> 状态：**本批消费者实现已审阅，候选验证待发布**。按用户授权优先处理 G11/G12，收敛当前可确认的 UI、动效和过渡差异，更新计划与矩阵并独立提交推送。内容/diff 自审不是独立评审；测试、构建与产品回归留发布前。

## 来源、允许范围与边界

代码分支 `codex/experience-ui-motion-transitions`，head `7f38f121c7bff5859e54ea98b25d315e07ad3cc8`；[PR212](https://github.com/ly-ccx/Peer-Agent/pull/212) 是叠加 E11–E12 [PR211](https://github.com/ly-ccx/Peer-Agent/pull/211) / `ec1de36b01d844497ea9ad663bc2e2b03bcfa0d9` 的 draft。知识父提交 `572f153f3b3bd68b2e1f0a6fd0111b943f9f3b96` / [PR72](https://github.com/ly-ccx/Peer-Knowledge/pull/72)。本批未合并其他 GitHub PR、未纳入 PR204 resize 或 PR206 Markdown/System Context；原主工作区的 HEAD、分支、index 与原有未提交文件未作为来源或交付内容。

允许范围为本批 50 个代码文件：renderer 的 motionEnvironment/visualMotion 与 hook、粒子/问题关闭、Overlay/presence/disclosure/档案/FLIP/塌缩/头像/思考球消费者、显示文本泵；能力/已装 Skills/MCP 读取与编辑、共享选项/文件名输入及现有文件创建；Gateway 两个已有网页的样式适配；对应边界用例。ChatSurface、ChatFindBar、LlmSettingsPanel 仅替换显式定位的 scroll behavior；没有继续扩展大组件职责。移除无消费者的 useExitAnimation；原工程文档留在知识库。

B 级影响限 `useTypewriterStream` 的显示批次：减少动效、页面隐藏或无帧 API 时，直接交出已收到 buffer，停止显示帧；正文/思考切换仍经原 handoff，flush/reset 继续保序。不新增网络请求、流事件、正文来源或合成内容，原 turn/tool/Evidence 结构与 Runtime 状态不变。其余为 C 级 UI 表达与恢复；没有新增或改变协议、IPC、持久路径、Capability、PermissionGrant、Evidence、触发器或 System Context 准入，不需要移动架构边界或新 ADR。

## 用户目标、事实、控制与恢复

| 用户目标 / 范围 | 事实来源与适用状态 | 控制、恢复与静态终态 |
|---|---|---|
| 减少动效也能确认结果 / G11 | 原 acceptance phase 与结果事实；粒子只装饰已有变化，active 不产生签收 | 采样与引擎都先读偏好/可见性；隐藏或偏好变化 abort 捕获、停帧并恢复源。捕获失败/空粒子/API 缺失直接保真实源；只有实际粒子/画布可用才遮盖源。卸载幂等清理，恢复前台不重播旧粉碎 |
| 已解决问题能够收尾 / G12 | 原 card resolved/current props；不是动画 finished 决定“已解决” | animateVisual 在无 WAAPI、异常、ready/finished 拒绝、无结束事件时静态完成 footprint；一次收尾。反向与卸载 cancel 旧关闭，不移除重开的对象；仅当问题原来拥有焦点且用户未移走时交本地可用 composer，不从后台抢焦点 |
| 退出/重开浮层与折叠 | 原关闭意图、dirty veto、visible/expanded/dockPhase；focus scope 与 interactionLayers 沿原实现 | watchVisualMotion 统一 finish/cancel、偏好/隐藏中断、bounded fallback；Overlay 保原触发者/层级，presence 提供 cancelExit，rail 重开取消旧移除。disclosure 隐藏立即 inert，档案 push 静态就位；目标消失/真实归焦仍待候选验证 |
| 重排/塌缩与查看历史 | 原列表 key/布局与用户阅读策略；WAAPI/ResizeObserver/帧 API 只是表现 | FLIP/塌缩复用已有 token/easing，隐藏/reduce 取消；缺 ResizeObserver 用 resize、缺帧 API 静态布局。显式查找/定位用 auto，不更改跟随意图。跨列仍沿原 remount 结构，未宣称保 DOM 或已解决跨列焦点 |
| 头像/思考/流式正文 | 原 activity、已收到文本和状态标签；不是有动画就代表正在执行 | 头像沿共享 observer/偏好与可见性，缺 observer 静态，gaze 前置短路；ThinkingOrb 动态暂停。静态/后台泵释放已有文本、停止帧，返回前台不重放已有退出；未触及的 CSS 循环仍按 M08/M17/M18 待核 |
| 经典授权决定立即生效 | 原 pending head 和原 onApprove/onApproveAlways/onReject；宿主仍拥有 grant/settled truth | 点击直接派发原回调，去掉 180ms 退场后派发；同一展示对象同步防重。没有乐观创建授权、跨请求重放或新增批准范围；异步未知仍依原宿主路径 |
| 能力/Skills/MCP 的读取与操作 | 原 listCapabilities、workspace/listSkills、available、MCP installed/credentials/detail API；清单不等于可执行权限 | reader 初读失败有提示/重读，失败保快照，未知数量不作零，真空只由成功读取确认。Skills 逐对象同步锁/真实回执后 accept，旧读不覆盖确认；详情可重读，失败不伪造开关成功，嵌套开关键盘不打开卡片 |
| MCP 配置和离开 | 当前敏感表单、原连接/凭证/OAuth/Manifest 回执；busy、失败与读取失败分开 | fieldset busy 与同步操作锁、局部状态反馈/复制失败替代；transport radio 只改本地值。离开 MCP、能力页、取消/关闭前经 existing dirty guard，敏感值仅留当前 editor；可继续编辑或显式舍弃，不写共享缓存。保存仍原多阶段宿主流程，没有承诺新事务/幂等；未知/部分写入先核对原列表 |
| 文件新建 / C211 | 当前名称 draft 与原 mkdir/writeFile 结果、原 workspace scope；输入不代表落盘 | 共享 composition/229/keyup，候选 Enter/Escape 不创建/删除；blur 留名称，显式确认/取消，readonly busy、失败/重名可继续。同步创建锁与 scope 对象屏蔽 A→B→A 迟到；确认成功仅原输入仍持焦点才交回筛选，取消回工具栏。项目切换仍原策略，不新增跨项目持久草稿 |
| tabs / 本地枚举 / C210 | 受控 value、disabled、对应 panel；浏览不等于写入 | tabs roving/方向/Home/End/RTL/IME，按键只移焦点，Enter/Space 才激活昂贵页；radio 方向键更新本地表单枚举。能力/Skills 与 MCP 接入共享 ChoiceStrip，panel ID 与状态对应；真读屏/多实例/选项失效候选待验 |

## UI 与宿主适配

Desktop 复用已有 Frost/`--ui-*` token、SVG/PeerIcon、ResourceFeedback/reader/action、UnsavedChanges、selectionNavigation 与 compositionGuard；没有组件库/新主题或动画物理参数。新增 ChoiceStrip 和 FileEntryInput 分别登记 C210/C211，原 C001–C209 责任保留；实际非测试 TSX Desktop 211、TUI 13。文件树没有重做完整 WAI tree roving/层级键盘，其余目录读取/刷新策略仍按原行 V。

Gateway 是已有 standalone host adapter。它继续既有浅深 palette 和原生表单，显式映射 Frost 的普通/紧凑字号/高度、8/12/16 几何、focus 与现有 fast/easing，补粗指针目标、强制颜色边界、换行与 disabled 反馈。它不导入 renderer CSS，也不新增 token 分发构建；不得称为全宿主自动共享主题。最终候选对照角色/主题/200%/对比度；若后续需要自动分发，按实际构建边界另卡处理。TUI、CLI、ACP 和原生窗口本批无代码改动，沿 E11 与各自 V。

## 覆盖、审阅和发布责任

同步[改造计划](../../design/product/peer-product-renovation-plan.md)、[交互矩阵](../../design/product/peer-interaction-standardization-matrix.md)、[UI/动效/过渡覆盖表](../../design/product/peer-ui-motion-transition-matrix.md)。相关 P07/P08/P23/P42/P43/P45/P49/P72/P74、对应 C010/C027/C031/C040/C051/C052/C055/C057/C065/C069/C070/C072/C075/C076/C099/C102/C115/C125/C142/C162/C198/C201/C210/C211 与 TS seam；U01/U03/U05–U12/U14–U16、M01–M06/M08/M12/M14/M15/M18、T01/T02/T04–T09。G11/G12 当前实现已审阅；不把未修改的全部页面/体系状态标完成。

已做源码/内容/diff 自审、空白和提交 allowlist 审阅。新写 `visualMotion.test.ts`、`choiceInputInteraction.test.ts`、`typewriterMotionPolicy.test.ts`、`permissionStripTiming.test.ts`，补写 `particleShatter.test.ts`，调整 TaskMonitor 两份既有用例；覆盖静态/拒绝/超时竞争/取消重开/偏好中断、粒子前置短路与停帧、tabs 显式激活与文件名 IME、显示文本顺序及授权无动画派发。**全部未运行**。没有 unit/integration、build/type/architecture/IPC、截图/交互回归、真实模型/安装包/辅助技术验证；没有独立评审或测试 Pass。

E13 在重新盘点并正常合并全部开放 PR 后，绑定最终组合 commit/安装包，执行完整门禁与产品 packet/review/verify。优先核对：G11/G12 的 CSS+JS reduce、隐藏/恢复/无 API/异常/卸载/快速反向；源/目标/嵌套归焦；正文/思考/工具交接；授权/核验/签收事实；MCP 初读失败/dirty/凭据与 OAuth 部分失败；Skills scope/旧读与确认；文件重名/失败/候选 Enter/软键盘；跨列/窄窗/200%/强制颜色/真实读屏/原生跨窗口。经候选证据确认的关键链路缺陷先修；其余 V 保原责任，E14 装饰增强仍可选。

## 本地点击对话崩溃补修（2026-10-24）

本地联调补修（2026-10-24）：用户点击机器人触发 `Illegal invocation`。代码 `ed0f81b4` / [集成 PR213](https://github.com/ly-ccx/Peer-Agent/pull/213) 已将 E05 `useConversationWindow` 的 request/cancel 包装为显式 `Window` 调用，保留原同帧调度、阅读意图与取消策略。C 级 UI 接线；新增真实 hook+有 receiver 约束的用例，未运行。仅确认重启该开发实例后可打开同一机器人、历史与输入框可见；未发消息或操作原任务，不等于全量回归。崩溃页原重载未恢复，采用重启恢复，reload 机制仍待 E12/E13 核对。

源码新增 `useConversationWindow.browser.test.ts`：用带 receiver 约束的 request/cancel 模拟器执行真实 hook 和调度器，覆盖进入对话的首帧与退出清理；旧接线会在首帧抛错。仅编写并内容审阅，未执行用例。原计划的候选门槛和其他 V 保持不变。
