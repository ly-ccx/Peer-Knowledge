# E15–E17 实施交接：UI、动效降级与过渡连续性

创建时间：2026-10-24
最后更新：2026-10-24

> 状态：**本批消费者实现已审阅，候选验证待发布**。按用户授权优先处理 G11/G12，收敛当前可确认的 UI、动效和过渡差异，更新计划与矩阵并独立提交推送。已补用户授权的基础点查与三项针对性检查，见下节；实施者自审不是独立评审，全量构建/测试与产品回归仍归发布。

## 全部 PR 汇合与模型强度补齐（2026-10-24）

用户本轮授权：合并两个仓库全部开放 PR，并修复全局模型分工的思考强度。不是版本/RC 发布，也不吸收原工作区未提交文件。初始清单：代码 16 项、知识 7 项；包含 draft 与堆叠分支，均按原提交身份审阅和汇合。

最终合并回执（2026-10-23 23:17 UTC）：原清单代码 **16/16**、知识 **7/7** 均为 GitHub 实际 MERGED，重新枚举两个仓库全部目标分支与 draft，开放 PR **0/0**。原清单每项 head 均已核对为对应开发线/main 的祖先，原提交身份保留。

- 组合候选：`b4d774046d3dcdb76b8fde16e1292cf6c18a3f77`；最终开发线 `PeerAgent/dev/0.1.0`：`bf1d10d203a2bde0c72aaebda5be5a8c82a16682`；两者源树同为 `ccdb72e389639ecda2937e9a4eb508fc09eec30f`。
- 合并门禁：最终 PR213 [CI 40037173238](https://github.com/ly-ccx/Peer-Agent/actions/runs/40037173238) 的当前组合候选 macOS/Linux 两项必需检查通过，包括构建、类型、架构、测试及隔离 Electron 场景。另保留 [PR197 源头检查](https://github.com/ly-ccx/Peer-Agent/actions/runs/40032957388)、[PR207 源头检查](https://github.com/ly-ccx/Peer-Agent/actions/runs/40032953270)、[PR198 源头检查](https://github.com/ly-ccx/Peer-Agent/actions/runs/40007128261) 各自的双平台成功及祖先身份。失败旧 head 不算通过；本轮没有另起本地测试套件。
- 合并后 push 自动 CI 的记录：[40038711134](https://github.com/ly-ccx/Peer-Agent/actions/runs/40038711134) in_progress。这是本回执时点的自动状态，与上面的合并门禁分开；没有将运行中状态计为通过。
- 本地开发实例已停止旧候选，先快进到组合候选 `b4d774046d3dcdb76b8fde16e1292cf6c18a3f77` 并用原命令启动；合并后工作树快进到最终开发线，源树与已启动代码一致。Vite HTTP 200，Electron 进程来自该工作树。启动所需依赖编译已完成，未另起本地测试；未重置个人数据、安装应用、发布或打标签。
- 最新候选的亲自点击检查仍受本机 Mac 锁定阻塞；较早 `a0ae1a33` 的基础点查见下节，不转作当前候选通过。GitHub 的隔离窗口检查不代替个人数据、真实模型、IME、辅助技术或安装包验证。实施者自审，非独立评审；E13 发布门禁保留。
- 原代码工作区 HEAD/分支/index/816 项内容指纹复核不变；本次使用独立工作树与知识克隆，仅提交本任务文件。

| 仓库 / PR | 原始 head | GitHub 合并记录 |
|---|---|---|
| [Peer-Agent #197](https://github.com/ly-ccx/Peer-Agent/pull/197) | `21c3f4249046` | `0ed634ff11c6` |
| [Peer-Agent #198](https://github.com/ly-ccx/Peer-Agent/pull/198) | `86eb3fbbd055` | `3ba8f66dd7d3` |
| [Peer-Agent #199](https://github.com/ly-ccx/Peer-Agent/pull/199) | `b0767a163525` | `a1b97d4a8104` |
| [Peer-Agent #200](https://github.com/ly-ccx/Peer-Agent/pull/200) | `132a0e47dc64` | `3403b15890bc` |
| [Peer-Agent #201](https://github.com/ly-ccx/Peer-Agent/pull/201) | `3b8218a43889` | `0aa0bde58679` |
| [Peer-Agent #203](https://github.com/ly-ccx/Peer-Agent/pull/203) | `71b7d993fb72` | `4aa0b7434abd` |
| [Peer-Agent #204](https://github.com/ly-ccx/Peer-Agent/pull/204) | `8ce158711ba5` | `0d03b2f57b0c` |
| [Peer-Agent #205](https://github.com/ly-ccx/Peer-Agent/pull/205) | `2d6af0d3e62e` | `a1b97d4a8104` |
| [Peer-Agent #206](https://github.com/ly-ccx/Peer-Agent/pull/206) | `1269ce29b1f8` | `3ac22586e587` |
| [Peer-Agent #207](https://github.com/ly-ccx/Peer-Agent/pull/207) | `b64337f33295` | `0ed634ff11c6` |
| [Peer-Agent #208](https://github.com/ly-ccx/Peer-Agent/pull/208) | `2a0ee98be843` | `a4b55bb6a0bb` |
| [Peer-Agent #209](https://github.com/ly-ccx/Peer-Agent/pull/209) | `815ab1363143` | `c8039a487a75` |
| [Peer-Agent #210](https://github.com/ly-ccx/Peer-Agent/pull/210) | `df25f859b710` | `2fd4389012bd` |
| [Peer-Agent #211](https://github.com/ly-ccx/Peer-Agent/pull/211) | `ec1de36b01d8` | `9945de9f4bed` |
| [Peer-Agent #212](https://github.com/ly-ccx/Peer-Agent/pull/212) | `7f38f121c7bf` | `a5599a96104d` |
| [Peer-Agent #213](https://github.com/ly-ccx/Peer-Agent/pull/213) | `a0ae1a334292` | `bf1d10d203a2` |
| [Peer-Knowledge #67](https://github.com/ly-ccx/Peer-Knowledge/pull/67) | `f4e2bb77cf73` | `9be1917f07e6` |
| [Peer-Knowledge #68](https://github.com/ly-ccx/Peer-Knowledge/pull/68) | `2f5da489f39a` | `b68da93438c8` |
| [Peer-Knowledge #69](https://github.com/ly-ccx/Peer-Knowledge/pull/69) | `4392e2990140` | `a0d4876c8702` |
| [Peer-Knowledge #70](https://github.com/ly-ccx/Peer-Knowledge/pull/70) | `b8206bd97813` | `39551c2221fe` |
| [Peer-Knowledge #71](https://github.com/ly-ccx/Peer-Knowledge/pull/71) | `73faf9667930` | `5817d270c06e` |
| [Peer-Knowledge #72](https://github.com/ly-ccx/Peer-Knowledge/pull/72) | `572f153f3b3b` | `3a20cbb72c79` |
| [Peer-Knowledge #73](https://github.com/ly-ccx/Peer-Knowledge/pull/73) | `c0206f287bb1` | `98cbaf9d3193` |

模型强度实现 `c4336a84`、恢复候选约束 `ec60b99a`，内容为 A/B 级可选契约补齐和 C 级表达。先提交知识 `2e03fff`，更新 ADR83 与 SDK 边界，再实施：

- RoleSetting 的 reasoningEffort 可用于 tier/fixed/auto。未设用最终模型默认；显式值须由该模型支持，失败不静默降档。覆盖仍按请求/任务/项目/全局解析，已冻结任务不回写。单模型仍可调角色强度。
- UI 根据当前角色合格候选声明的交集给选项，恢复模型默认会真正移除覆盖；模式/模型变化不会把 tier 变成 fixed，不兼容值保留并允许清除。已保存预览由主进程返回实际解析值，失败保本地草稿/原事实。恢复候选过滤显式强度，避免后续换成不支持的模型。
- 沿原 model-routing get/update/preview IPC、settings 和共享 resolver，补可选预览字段，没有新增通道或持久目录。SDK 正式声明既有 stream.discard 的流身份/计数及统一事件元数据，移除 TUI 的强转旁路；只撤回失败请求的流式草稿，不撤回持久结果/工具/Evidence。

统一模型面板补修：服务商浏览只移动本地浏览位置，不触发模型保存；模型/强度/快速通道读取受控配置。EffortRange 沿 onEffortChange 返回的实际保存 Promise 保留选中滑块，收到回执后再释放临时显示；失败仍以宿主旧保存值和既有待重试草稿反馈表达。触发按钮以 aria-disabled 与点击 guard 禁止忙碌时重复动作，同时保持 Escape 可归焦，不把焦点落到禁用按钮。脚本点查改为统一 dialog/provider/options/slider 路径，保留 650ms 延迟、失败不写、重选不写、其他 bot/角色/全局配置不变和真实保存核对，不再等待已替换的级联菜单或独立强度浮层。

C031/Overlay 的真实归焦补修：Layer 清理先注销自身，此时旧 focusin 拦截器还未清理。原 ownsScope 将两个 undefined 比为相等，误把已退出的浮层当成焦点拥有者，重捕获归还给版本入口的焦点。现在要求自身 layer.current 仍存在且为 topInteractive 才能捕获焦点；不以延迟强抢目标，不改关闭动画或下载事实。新增 overlayFocusRestore.test.ts 在模拟 DOM/React 调度夹具中执行实际 Overlay、useInteractionLayer、useFocusScope 源码的挂载/清理顺序，覆盖旧 DOM 仍在但 layer 已注销的归焦；既有 updater-minimize 真实窗口检查保留全部焦点与终点断言。

合并冲突保留 PR204 的 dock frame、宽度记忆、双帧入场，同时保留 E06/E17 的逻辑层级及静态/中断收尾。列表和新档案分隔条复用 usePointerResize，Esc/失焦/取消/卸载均释放真实屏障和光标状态，关闭态不残留可聚焦分隔条。PR206 的 Markdown/紧凑列表、单行引用回显、卡片键盘合入 E02/E11 的草稿、稳定卡片身份和焦点，输入框提示移出边框。

CI 阻塞修复推回原 PR：197 两个严格行数断言改为不超过原 3306 行预算，并将稳定回调逻辑抽到既有 hooks seam（本候选 ChatSurface 3283 行，未放宽模块上限）；198/206 源码断言分别与其分支的 Enter/composer 实现一致，组合后跟随已有 shared submission 入口；199/205 复用既有 Git 类型修复、补实际运行模块输出并保留成功准入白名单字段的归一化/重载；201 将既有流撤回声明进 SDK。组合候选另修 E08/E15 测试夹具的 Promise/数组/字面量类型，以及运行中模型摘要引用未声明字段；保存值比较的两个 details 复用 PeerIcon、共享几何/焦点 token 和静态展开指示。Desktop 的脚本 cognition/集成夹具保留真实 Runtime Projection 的能力清单接口；未知能力仍拒绝。更新旧自动化、卡片、导航、开关和拖动源码断言以跟随已抽离的 reducer/hook/reader 接线，不提高模块预算、不放行未知工具。

虚拟历史窗口检查补修：旧 scrollToBotMessage 直接写 scrollTop，未建立用户阅读意图，会被跟随最新策略拉回底部，导致尚未挂载的第 9960 条消息定位超时。现沿真实滚轮/键盘操作导航并等待虚拟测量，不关闭虚拟化、不放宽定位或页面错误断言，生产阅读策略保持不变。

E05 阅读锚点补修 `3a6631c1`、`1bad790a`：真实 wheel/touch 意图先退出跟随。最初下一帧采样仍可能先于 compositor 的实际滚动，CI 记录 5340→5690，2px 门限未通过；最终改在原生 scroll 捕获阶段记录已应用的行锚点，先于延迟的 React/委托处理。只采纳已有手势，不由几何变化生成新意图；显式回最新仍沿原入口，卸载释放 listener 和原调度器。模拟 DOM/React 调度夹具执行实际 hook，覆盖“帧先执行、浏览器随后滚动、React scroll 尚未投递、几何提交仍保原位置”及清理；窗口脚本走真实滚轮，保留事件投递延迟和 2px 门限。

TUI 输入/机器人页/卡片焦点集成夹具 `4802b08a`、`cd62e44a`：macOS 下在 React act 内启用真实系统主题 watcher，execSync 检测触发 Bun 调度重入并遗留轮询句柄。沿既有 systemThemeWatch:false 的测试 seam，在 act 外构造主题 store；保留直接/经典入口、图片+中文与 RETURN/LINEFEED/ctrl-m 的全部内容断言。主题轮询的独立用例仍保留，这些输入/键盘夹具不宣称覆盖真实 OS 外观。

E02/E04 问题状态补修 `0abb187f`：hideAcknowledgedQuestions 原先只排除 failed/sending，把 unknown 也视作已收到回答，导致回执未知时提前关闭选择。改为只接受 canonical（无 pending）或明确 received 的输入；unknown 保留原问题与 inputId/answerTo。窗口脚本使用现有“重试同一消息”入口，新增未知文案/原 inputId/原问题关联和最终 canonical 仅一条的核对，不把失败注入改成成功、不放宽去重。

发送/关闭占位补修 `dffc1b1d`：macOS/Linux 同样记录新输入与等待回复一次增加 175px，问题结束前又从 1px 回弹至 81px。新增 C213/ConversationRow 在既有集中式 motion.css 注册 motion-enter-layout，沿 medium/standard 与现有行间距，把新输入/等待回复的 intrinsic height/spacing 同步展开；不换原 DOM/key，不对历史恢复或虚拟重挂载重播。减少动效、隐藏或 API 不支持直接静态完整内容，偏好中断由 watchVisualMotion 收尾。已解决问题的 finish 先设置 display:none，再等待 React 移除，避免 cancel fill 露回自然高度；重新打开清理临时显示。新增模拟 DOM/React 的实际源码用例覆盖中断不重播、插值不支持的可读静态和关闭终态，窗口检查保留原 <80px 帧差、单一回执/身份和减少动效断言。

减少动效归焦补修 `162387ee`：普通发送最大帧差已实测降至 30–61px，但 reduce 下卡片立即移除，旧 Promise 回调从 ref 查找 composer 时节点已空。改在动作禁用前记录卡片焦点归属，只在真实 resolved 回执、原焦点仍归该卡且文档可见/有焦点时交回可用 composer；用户点外部、移走焦点或后台取消交接。移除仅凭通用 ok 在 Promise 中无条件抢焦点的接线。临时 pointer/focus 监听器在交接、移走与卸载清理；模拟用例覆盖即时移除、背景点击、隐藏文档和清理。页脚初始几何检查改为同一浏览器帧读取两个矩形，并写报告；保持 <=64px 高度与 1px 对齐门限，避免两次远程坐标读取跨窗口布局时误判。

交互层/夹具一致性补修 `6a7490f4`：C162 档案先登记 Layer 再进入 focus scope，自身 Layer 不存在时不拥有焦点，保留既有归焦策略。响应式父布局重挂载的窗口检查先等旧 scene 断开、有限可见动画结束及两帧布局，再判定是否重开；机器人切换按真实名称和 composer 对象确认，恢复阅读位置后显式点回最新才检查尾部。隔离宿主夹具的 conversationMessages 卡片与 cards 事实回读保持一致：失败保留，受控成功由真实回读移除，不用 generic ok 生成 UI 完成事实。更新下载快速完成由实际第四次 download 调用触发，先布置宿主事件再点击，保留退出期间完成、内容和焦点全部断言。回执文件原子替换，避免读取半个 JSON。均为 C 级表达/隔离测试 Adapter 修复，没有新增生产权限或 IPC 边界。

状态/键盘驱动补修 `7259fc47`：6a 候选的 macOS/Linux 均走到授权排版场景，失败于旧脚本将 expired 要求为“已超时”；改按现行“已失效”回执。真实 TIMEOUT 场景另展开原详情核对“等待授权已超时，本次没有读取图片”，保留真实 timeout/Evidence/无像素/迟到批准拒绝的检查。档案标签驱动跟随 E06 的手动激活契约：方向键只移动焦点并保原 selected，Enter 后才确认目标 selected；不是改产品为自动激活或删掉状态断言。

打开会话与到期反馈补修 `0ed634ff`：7259 候选有 macOS/Linux 完整通过，也有切回机器人时跟随状态仍为 true、实际停在历史顶部的失败画面。原前沿调度器会丢弃同帧后续请求，空壳先提交而消息/测量随后提交时可能没有最终贴底；C138 在原调度器重置后增加一个有界帧复核，仍读当前 pinned，用户已读历史则不执行，卸载释放两类帧，空闲不循环。原调度器契约保持不变。实际 hook 的模拟 DOM/调度用例补同帧最终几何、空闲和复核前用户滚轮，不宣称是真 React 窗口。

同候选另一 Linux 失败在已打开 AttentionSheet 的限时项没有及时刷新。C123 对观察到的期限安排一次宿主重读，并请求父列表刷新计数；只以返回事实更新清单，不由本地 clock 关闭问题或生成授权。按对象/期限限制自动尝试，失败保旧清单与重读入口，时钟偏差不重复轮询同一已到期限，离开清理 timer；模拟组件用例核对回读前仍保行、真实空清单才移除、父计数刷新、时钟偏差及卸载。两项均为 C 级表达与读取恢复，不新增协议、权限、Evidence、执行或存储路径。

动效度量与最终集成 `e6c241e6`：0ed 的 PR197、PR207 双平台全部通过，PR213 Linux 通过，macOS 只失败于点击后 650ms 卡片仍未进入关闭；稍后的失败截图已显示同一回答收到、回复完成且选项收起。原脚本将实际宿主回执等待混入关闭窗。现保留从点击开始的全部帧，记录首个渲染 resolved 事实的耗时，再完整观察原 650ms 关闭窗；<80px 帧差、动画/静态、同一输入、持久唯一回执及归焦断言不变。12s 仅为夹具死锁边界，不是产品性能验收结论，也不以 timer 改产品事实。该脚本修正只推最终集成 PR213；PR197/207 保留各自已通过的 0ed head，PR198 保留已通过的 d355 head，最终候选包含这些 source head 并单独完成双平台必需检查。

嵌套现场驱动补修 `b4d77404`：e6 的 Linux 完整通过；macOS 已通过修正后的问题发送窗口，停在首个子会话现场入口。失败画面保留了已展开的父任务信息，子现场不在；原脚本没有等待注入的 conversationId 被宿主读取，并在原生 details 裁剪高度展开时立即点其内部按钮。现先核对真实 listSessions 的目标子会话，按任务标题定位，等待实际有限展开动画与两帧布局，再发出单次真实点击并核对现场可见；宽窄重开共用该入口。未重试业务动作、伪造继承事实或放宽权限/只读/主题/返回断言。该修正仍仅落最终集成 PR213，其余源 head 保留成功检查。

新增用例覆盖：三模式强度/层级覆盖/不支持失败、存储重读/预览/单模型保存与拒绝、候选交集/恢复默认/模式不变、恢复候选不降强度、SDK 撤回事件身份和顺序、TUI 卡片打印字符回到草稿、准入记录保存/重载及幂等重放。PR197 曾快进到与 PR207/213 相同的组合 head，保留原提交身份；其旧分支 macOS 的折叠采样/权限抽屉失败不作通过，以组合源的实际检查结果替换，既有阈值与事实断言不删。PR198 自身检查已通过，其冲突在同一候选内解决并复核。合并所需 GitHub CI 与本地手动点查分别记录，不冒充正式发布验收、独立评审或全平台通过。未发布/打标签/安装，发布门禁 E13 继续保留。

## 用户授权的基础交互点查（2026-10-24）

用户要求先亲自点查改造的基础交互，重点对话、页面切换、设置与抽屉，发现问题修好并独立提交推送。因此本次明确提前执行下表手动检查及三项针对性检查，不是发布全量验收。代码 `a0ae1a334292305161693b58bb87522322a6c3df`，父提交 `ed0f81b4e3da68462bb8c9383a5bc4c89f44d92e`，在同一 0.1.0 本地集成线运行；[PR213](https://github.com/ly-ccx/Peer-Agent/pull/213)。本节是后续记录，下文原批“未运行”保留其当时含义。

发现并修复：

1. 对话更新时出现多个历史列表、空态和“回到最新”，正文叠影。`BotMessageList` 与同级 `BotComposer` 原先都用 workspaceId 作 key；现在分别使用 thread/composer 身份。保留按 bot 重建语义，读取失败不重建草稿表面。新增 `BotConversation.identity.test.ts` 执行真实组件渲染树，检查加载/成功/失败/重试与换 bot 时的同级唯一性和身份连续性。
2. 机器人壳“新建自动化任务”及空态创建入口误接经典聊天 `conversationStore` 的草稿，导航回 bot 后不显示该模板。机器人壳改用既有 AutomationCenter 编辑器；移除该壳到旧 callback 的接线。经典聊天仍用原模板入口，创建/权限/调度 API 沿现有实现。

两项均为 C 级 renderer 修复。用户目标是进入正确页面、保留草稿与阅读现场；真实执行、授权和 Evidence 继续来自原宿主。本次没有修改协议、IPC、持久存储、Capability、PermissionGrant、Evidence 或 System Context。

| 路径 | 实际操作与结果 |
|---|---|
| 首屏/对话 | 从最近机器人打开既有对话；多次从能力/自动化返回，重载后再次打开；修复后单个对话和输入框，无错误边界或重复叠影。只覆盖一个既有机器人 |
| 列表搜索 | 输入无匹配关键词，显示无匹配；清空后原机器人恢复，对话仍可用 |
| 设置页面 | 通用、外观、个性化、快捷键、服务商、模型分工、使用统计、Git、开发者、远程访问、更新与关于、已归档会话逐一打开，再返回对话；没有修改保存值 |
| 未保存设置 | 个性化空值输入临时文本，切换 Git 显示保护；继续编辑保留内容；再次离开选择舍弃，再进入字段回到原空值 |
| 档案 | 概况、任务、目标、记忆、设置逐一切换；设置按钮打开后 Escape 关闭，焦点回原按钮；当前目标真空可见 |
| 任务与 Evidence | 打开既有任务详情，再打开一个读取文件 Evidence；关闭预览恢复原详情及原 Evidence 按钮焦点，返回任务列表正常。未执行取消/重试/签收 |
| 记忆 | 打开已有记录编辑，舍弃返回，无保存、撤回或固定变化 |
| 模型/权限菜单 | 两菜单分别打开并 Escape 关闭，焦点回各自原入口；未选择新模型或权限 |
| 新建机器人 | 名称为空时建立禁用，输入临时名称后可建立；Escape 退出。未点击建立或绑定真实目录 |
| 附件 | 打开原生文件选择器，取消后回输入界面及原附件按钮；没有选择或上传文件 |
| 需要你/历史 | 打开待处理清单和历史对话浮层，Escape 关闭；未回答/批准或修改原待办 |
| 能力 | Skills 市场及已安装页、MCP 标签可切换；MCP 新增浮层可打开和取消；未安装/借用/连接 |
| 自动化 | 修复后顶部新建与空态创建均进入原编辑页，舍弃返回列表；未创建、启用或运行 |
| 草稿/阅读 | 向上读历史后开关抽屉，页面往返仍处阅读模式且只有一个回最新；临时对话草稿经自动化往返和热更新重进仍保留；随后清空临时草稿，点击回最新正常 |
| 正常窗口重载 | 使用开发菜单对应的整窗重载快捷键；短暂加载后首屏恢复，重开对话和设置抽屉成功。未再现崩溃页自身的重新加载，不据此关闭其 V |

已运行：`node --test` 指定 `useConversationWindow.browser.test.ts`、`BotConversation.identity.test.ts`、`automationCreateNav.test.ts`，最终 3/3 通过。完成源码、内容和 diff 审阅。

实施者亲自操作本机 macOS Electron 开发实例，非独立评审；通过可访问性状态及现场截图检查了叠影修复和最终界面。未生成发布 packet/review/verify；含真实历史的现场截图不提交仓库。临时对话草稿、设置草稿及搜索已清理，新建自动化草稿已舍弃，原任务、配置及权限未作业务写入，开发实例留在对话可用状态。

覆盖限制：没有真实模型发送、工具授权/执行、签收、自动化持久创建/运行、网络/存储失败注入、多机器人、真实 IME、TUI/远程、减少动效/透明度、辅助技术、跨窗口或安装包验证。最终合并候选仍须 E13 全量门禁和回归；不能将本次正常路径点查扩为全产品/全部状态通过。此前崩溃页重载未恢复的记录保留，只有正常开发窗口重载获得本次确认。

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
