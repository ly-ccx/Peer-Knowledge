# E05–E06 实施交接：阅读控制与交互层级

创建时间：2026-10-23
最后更新：2026-10-23

> 状态：**实现已审阅，候选验证待发布**。用户授权依改造计划继续 E05/E06，完成后更新矩阵、独立提交推送，测试/回归留到发布。以下内容是实施者内容自审，不能称独立评审或运行验收。

## 来源和交付

代码分支 `codex/experience-navigation-layers`；本轮提交 `2a0ee98be84344b8ae6499ee48b6d25b281afa32`；父提交 `b64337f3329539ac2fcc2a16220b62842cdf1ae0`。知识父提交 `2f5da489f39affa40cf6ad26781b30c8d6ecf99d`。在上一批干净隔离 worktree 上新建后续分支，原工作区的 HEAD/分支/index 与 dirty 文件不参与提交；不搬入其他功能 PR 的代码。

本轮代码评审：[PR208](https://github.com/ly-ccx/Peer-Agent/pull/208)（draft，基于上一批分支，仅包含 E05–E06 增量）。依赖上一批代码 [PR207](https://github.com/ly-ccx/Peer-Agent/pull/207) 与知识 [PR68](https://github.com/ly-ccx/Peer-Knowledge/pull/68)。本轮只交付 renderer/i18n 及对应文档；不合并、发布、安装或重启应用。

## 本次体验契约

| 工作包 | 用户目的 / 行为 | 事实源 / 实现落点与恢复 |
|---|---|---|
| E05 | 阅读历史、回引用或切回机器人时保住位置；背景回复、晚图、展开、测量、发送与压缩不能替用户回最新 | 沿真实 workspace/消息/turn ID、已有 pager/虚拟测量；shared threadScrollPolicy/streamingScrollScheduler、useConversationWindow、conversationReadingMemory、useThreadScrollGesture/threadReadingRestore |
| E05 | 返回旧页不一次扫描整段历史；用户滚动或新定位取消旧恢复，明确回最新才恢复跟随 | 会话内最多 40 份锚点，每份 160 条几何；旧页每批最多 4 页，失败/未找到有继续/回最新；只保存 ID/几何，绝不缓存许可或执行事实 |
| E05 | 查找结果仅在显式查询/上一条/下一条时移动；重算高亮保持阅读 | ChatFindBar 使用独立用户导航修订，后台 recompute 不导航；reduce 不 smooth；沿既有“只查已渲染内容”的能力限制 |
| E06 | 一个输入只由当前最上层处理；进入/关闭有来有回，背景不抢焦点 | interactionLayers/useInteractionLayer + React 逻辑 owner + 真实 DOM/trigger；Overlay/Drawer/push 档案、菜单/查找/tooltip；modal native inert、Tab/focusin 边界兼容自有 portal；退出归触发者/仍合法相邻/父上下文，外点保留新焦点 |
| E06 | 菜单/选择/标签不用鼠标也可达；焦点不代替选中或保存 | shared selectionNavigation、IME 优先、禁用跳过、Home/End/方向/roving；listbox/combobox/radio 按实际语义；昂贵视图需 Enter/Space/点击激活；资源 close/Delete 回相邻、真实 panel ID 和隐藏 inert |
| E06 | 拖动可撤销，取消不会保存预览；隐藏内容与提示不会困住焦点 | shared usePointerResize：pointer capture/rAF/真实覆盖屏障、up 提交、Escape/cancel/blur/lostcapture/卸载撤销，恢复右侧最大化/自动收栏阶段并清理；分段拖动有死区/取消/抑制后续 click；disclosure 收起先交回控制钮；tooltip Escape/hover 保持、原 describedby 合并且不夺焦点 |

允许的代码范围：Desktop renderer 的 app components/hooks（层级/焦点/菜单/tooltip/disclosure）、chat 的滚动/查找 seam 与 ChatSurface 的替换装配、project-agent 的 conversation/pager/reading/档案 tab 消费者、Workbench 的两侧 resize/资源 tabs/真实页面关联、capabilities tabs/panel 和 i18n；必要契约测试同步编写。ChatSurface 将新增逻辑下沉到 hook/state seam，文件净减。MCP 表单移除重复全局 Escape，只让共享 Overlay 处理并保留 busy 退出约束；没有修改其连接、凭据、执行或 Manifest 语义。

C 级表达修改；未移动 Runtime、IPC、协议、存储、Provider、权限、Evidence、签收或 System Context 边界。阅读位置仅会话内存，不新增持久路径或第二业务状态源。背景数据不会触发导航/自动激活。动画取消/缺 API/减少动效只收尾表现，不写许可或成功。

## 矩阵映射与明确边界

主矩阵：G05/G06/G07；P06/P08/P11/P13/P21/P27/P45/P48/P50/P52；C012/C016/C017/C027/C030/C031/C040/C045/C069/C070/C078/C082/C102/C138/C158/C162/C185/C186/C189/C196/C197 及 §6 TS/hook seam。体系：U08/U09/U11、M03–M06/M16、T01–T05/T08/T09。未新增 TSX 模块；其他组件通过共享层受影响仍保留自己的待核状态。

没有实现跨进程重启的阅读持久化；真实 source ID 已不存在时不能造出原内容。经典查找仍限已渲染内容，原 turn 被压缩移除后的几何回退不称原文恢复。TUI/Remote/原生跨窗口适配继续 E11，200%/读屏/guest 行为仍待 E13。G04 设置 dirty 离开、G08 图片失败、G09 记忆错误、G10–G12 启动/粒子/问题 WAAPI 降级继续原计划；本次 Overlay 的收尾修复没有关闭 G12。PR197 模型面板、PR198/206 TUI、PR204 档案宽度等以最终 head 集成后核对。

## 审阅与发布验证

已完成内容/diff 审阅；没有运行单元/集成测试、构建、类型/架构/IPC 检查、截图或交互回归，没有个人运行实例操作。已编写/调整未运行的用例涵盖：布局碰底不恢复跟随、用户主动回底、返回/显式目标优先、方向事件；40 份/160 条几何上限与对象隔离；pager 分批预算/继续/取消；逻辑父子与先子后父注册、被动提示/portal 归属、单次外点不穿透；导航跳过禁用、RTL/Home/End/空集合；Dropdown 过滤语义。

发布前须合并全部开放 PR 后，对最终候选做全套门禁与完整产品回归，补以下实际证据：

1. 主 Bot/经典上滚、代码/图片晚增高、前分页/虚拟测量、压缩、查找、切机器人/会话返回；恢复失败/缺 ID、4 页后继续、用户中断与新目标、显式回最新。
2. 模态内 portal 菜单、级联根/子层、嵌套/初始双层、IME、Tab/Shift+Tab/focusin、空/禁用/触发者消失、外点/提交/关闭后归焦；重复关闭/动画取消/缺 API/动态 reduce。
3. tabs 的焦点与选中、RTL/多实例、昂贵内容手动激活、隐藏 panel 无 Tab；浏览器/文档动态关闭/最后一页/新增，guest 不被重排销毁。
4. 两侧与 local/root Workbench 跨真实 webview/iframe 的拖动，up/取消/失焦/Escape/lostcapture/卸载/多指/重复结束；撤销还原原宽度/最大化/自动收栏，键盘范围与复原、无遗留屏障/监听/cursor/userSelect。
5. tooltip 键盘/hover 跨间隙/Escape/描述合并/边界定位、disclosure 的收起/反向/卸载归焦；200% 字号、辅助技术、安装包与真实 OS/输入设备分别记录。

所有上述运行项均是待发布覆盖，不是 Pass；实现者自审不称独立验证。沿现有 packet/review/verify，不另建验收账本。
