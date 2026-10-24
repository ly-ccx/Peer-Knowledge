# 菜单、浮层、抽屉与设置过渡梳理

创建时间：2026-10-24
最后更新：2026-10-24

状态：E16/E17-F5 实现与内容/diff 自审完成；候选测试与产品回归待 E13。实施者自审，不是独立评审或发布 Pass。

用户目标：避免逐个入口才发现动效遗漏；覆盖现有产品的菜单、浮层、抽屉、设置及兼容入口，按既有规范补齐，保留输入、焦点和阅读连续性。

交付：代码 [59451598](https://github.com/ly-ccx/Peer-Agent/commit/59451598dc513e0702bbacc961c1b366f73efbe3)；沿两仓 codex/reply-progress-feedback，代码父提交 040a3e1b、知识父提交 e4184b8；复用[代码 PR214](https://github.com/ly-ccx/Peer-Agent/pull/214)和[知识 PR74](https://github.com/ly-ccx/Peer-Knowledge/pull/74)。不混原工作区 dirty，不改版本、不发布。

## 实现责任

C 级 UI 表达：MotionSurface 无额外布局节点，保最后已提交画面，真实 open 关闭即 inert/aria-hidden，退出由共享 visualMotion 收尾，反向/卸载取消旧 watcher，保原 ref。MotionDetails 是保留原生 details/summary 语义的尺寸过渡；支持检测与静态 fallback，不承诺所有浏览器均播放。没有新 keyframes、运动常数、动画库或第二套设计体系。

Overlay/Drawer 的关闭准备支持既有保存 API：pending 合并；false/异常/拒绝不退场；卸载/新代次使旧结果失效。SelectionChatWorkspace 保存成功才启动退场，保存期间新编辑/错误保留现场和局部恢复；原 parent/代次核对防旧回执影响新对象。此门只处理 UI 关闭，不产生许可、执行/保存成功或 Evidence；事实仍取原 API。业务操作/导航及真正结束不等待动画。

CSS 收敛：设置只在分区 key 变化时一次 fade，后台刷新不重播；目录过滤不逐卡级联；配色/目录/档案/GoalPanel 移除私有固定退出计时；抽屉静态关闭 opacity、逻辑边框与 RTL 位移明确。Workbench/webview 不因动效重新挂载。

## 轻层逐源清单

以下路径均相对代码仓 apps/desktop/renderer/src；组件编号回链[交互矩阵](../../design/product/peer-interaction-standardization-matrix.md)。每项均已接 MotionSurface；rise/fade 语义、焦点与身份责任见[体系覆盖表 F5-01–12](../../design/product/peer-ui-motion-transition-matrix.md#菜单浮层抽屉与设置过渡复核2026-10-24)。

| 模块 / 编号 | 载体数 | 当前实现与待验证 |
|---|---|---|
| `app/components/CascadingMenu.tsx` / C012 | 2 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `app/components/Dropdown.tsx` / C017 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `app/components/LlmSettingsPanel.tsx` / C026 | 1 | S F5：目录与已连接视图一次 fade 交接，删除私有关闭 timer/逐卡级联；OAuth 不再向不可关闭浮层传 noop onClose，避免 Escape 留空壳；V 真实反向/层级/归焦/读位/静态降级 |
| `app/components/OverflowMenu.tsx` / C030 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `app/components/Tooltip.tsx` / C045 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `app/pages/TaskOverviewPage.tsx` / C055 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；悬停预览按锚点身份登记被动层，内容晚到重定位；V 真实反向/层级/归焦/读位/静态降级 |
| `appearance/PaletteSelect.tsx` / C063 | 1 | S F5：移除私有退出 timer/强制 reflow，接 MotionSurface 和共享 layer/Tab/IME；原 ARIA listbox/选值保留；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/ComposerDraftControls.tsx` / C079 | 2 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/SelectionQuoteAction.tsx` / C088 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/Sidebar.tsx` / C089 | 2 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/thread/ChatFindBar.tsx` / C102 | 1 | S F5：查找条接 MotionSurface fade，关闭立即停 layer/高亮/检索并清查询；隐藏实例不清除别处高亮；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/thread/ChatHeader.tsx` / C103 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/thread/ChatHeaderCapabilities.tsx` / C104 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/thread/ContextUsagePanel.tsx` / C107 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/thread/ModelSelectionPanel.tsx` / C114 | 2 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `chat/components/thread/ReasoningEffortSlider.tsx` / C116 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `project-agent/AppMenu.tsx` / C122 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `project-agent/conversation/BotSelectionQuote.tsx` / C141 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `workbench/OpenTargetSplitButton.tsx` / C184 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |
| `workbench/file-preview/DiffViewer.tsx` / C191 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；悬停预览按当前锚点切换/移除，关闭销毁事件订阅；V 真实反向/层级/归焦/读位/静态降级 |
| `workbench/views/BrowserView.tsx` / C196 | 1 | S F5：MotionSurface 统一入退场、关闭即 inert/aria-hidden、反向取消旧收尾；行为仍由原受控状态决定；V 真实反向/层级/归焦/读位/静态降级 |

## 原生折叠逐源清单

每项均改用 MotionDetails，保留原 props/summary；按真实内容高度过渡，完成释放 overflow。缺 API/减少动效为静态；V 原生键盘/读屏、嵌套反向、动态高度与打开后的浮层不被裁切。

| 模块 / 编号 | 折叠数 |
|---|---|
| `app/components/ConfiguredModelRow.tsx` / C013 | 1 |
| `automations/AutomationCenter.tsx` / C064 | 2 |
| `project-agent/diagnostics/ProjectDiagnosticsPanel.tsx` / C156 | 1 |
| `project-agent/drawer/AgentProcessView.tsx` / C157 | 1 |
| `project-agent/drawer/BotPolicyFields.tsx` / C161 | 1 |
| `project-agent/drawer/BotSettingsTab.tsx` / C163 | 1 |
| `project-agent/drawer/EvidenceView.tsx` / C165 | 1 |
| `project-agent/drawer/MemoryTab.tsx` / C166 | 2 |
| `project-agent/drawer/ObjectivesTab.tsx` / C167 | 1 |
| `project-agent/drawer/SessionDetail.tsx` / C169 | 1 |
| `project-agent/drawer/TaskVerification.tsx` / C170 | 2 |
| `ui/resources/ResourceEditor.tsx` / C208 | 1 |
| `workbench/BackgroundRunDetails.tsx` / C181 | 2 |

## 模态/抽屉逐源清单

这是生产 JSX 挂载点盘点，不能把 DOM 容器数当成不同页面数；Drawer 自身转 Overlay 计入适配一行。纯按钮取消/关闭、Escape 和外点复用 requestClose；事件/业务完成与已就绪目标交接由原事实直接移除或切页，不让动画持有副作用。

| 模块 / 编号 | Overlay / Drawer 点 | 关闭与交接责任 |
|---|---|---|
| `App.tsx` / C001 | 0 / 2 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `app/components/ConfirmProvider.tsx` / C014 | 1 / 0 | 原确认回调与取消焦点契约保留；视觉不得产生真实操作回执 |
| `app/components/Drawer.tsx` / C016 | 1 / 0 | 共享适配，透传 requestClose/关闭准备/restoreFocus |
| `app/components/FullDiskAccessStartupGate.tsx` / C021 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `app/components/LlmSettingsPanel.tsx` / C026 | 2 / 0 | 表单 requestClose + dirty guard；OAuth 为真实授权流程控制，删除 noop onClose，Escape 不淡成空壳，完成直接交接 |
| `app/components/McpSettingsPanel.tsx` / C027 | 1 / 1 | 新增表单按钮经 requestClose + dirty guard；详情 Drawer 原 Escape/外点，无内部绕过按钮；编辑跳转为目标交接 |
| `app/components/ModelCatalogDialog.tsx` / C028 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `app/components/ModelSettingsDialog.tsx` / C029 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `app/components/UpdateModal.tsx` / C046 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `automations/AutomationCenter.tsx` / C064 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `capabilities/components/QoderMarketplacePanel.tsx` / C071 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `capabilities/components/SkillDetailDialog.tsx` / C072 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `capabilities/components/SkillMarketplacePanel.tsx` / C073 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `capabilities/components/SkillUploadDialog.tsx` / C074 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `chat/components/ConversationSearchPalette.tsx` / C082 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `chat/components/CreateBranchDialog.tsx` / C083 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `chat/components/EditProjectDialog.tsx` / C084 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `chat/components/SelectionChatWorkspace.tsx` / C087 | 0 / 1 | 先保存再退场；错误/保存中新编辑留现场、重复关闭合并，旧 parent/代次失效 |
| `chat/components/thread/ImageLightbox.tsx` / C108 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/AttentionSheet.tsx` / C123 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/HistorySheet.tsx` / C131 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/NewBotSheet.tsx` / C132 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/conversation/BotAttachments.tsx` / C135 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/conversation/CompletionReview.tsx` / C143 | 0 / 1 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/drawer/BotProfileDrawer.tsx` / C162 | 0 / 1 | cover 关闭按钮 requestClose；push 真实 CSS watcher 与原宽度记忆另列 |
| `project-agent/drawer/EvidencePreview.tsx` / C209 | 0 / 1 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/drawer/SessionDetail.tsx` / C169 | 0 / 1 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `project-agent/onboarding/ClassicShellNotice.tsx` / C173 | 1 / 0 | Escape/外点共享退场；切换经典壳是立即导航交接 |
| `settings/UsageStatsPanel.tsx` / C176 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `ui/forms/UnsavedChanges.tsx` / C205 | 1 / 0 | 继续编辑 requestClose；舍弃/保存并离开依真实编辑与导航立即交接 |
| `workbench/BackgroundRuntimePanel.tsx` / C182 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `workbench/views/PasswordManagerPanel.tsx` / C199 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |
| `workbench/views/SessionImportWizard.tsx` / C200 | 1 / 0 | 原共享挂载/纯关闭 requestClose；业务确认或目标导航沿原回执交接；V 嵌套/取消/来源失效与归焦 |

## 设置与独立机制

SettingsPage 的 12 个公开分区都使用同一 keyed settings-content fade；设置搜索/深链/返回先处理已有 dirty guard。通用、外观、个性化、快捷键、服务商、模型分工、用量、Git、开发者、远程访问、更新关于、已归档都登记此入口；各真实字段/保存仍各负责。服务目录只有一次 view 交接，SettingsDisclosureContent 保已有 grid/可逆挂载和焦点，自动化高级区保原 reducer，不添加第二套开关状态。

BotProfileDrawer push 保原双帧 width 入场，退出观察真实 CSS motion；cover 与共享 Drawer 同路。TaskMonitorRailView 保原 presence，只由 visible 决定停用。经典 GoalPlanPanel 的关闭从共享 token 取时间、watchVisualMotion 负责取消/静态终态，卸载清宿主 data-closing。ChatFindBar 真实 open 关闭即撤层/清高亮，视觉淡出不继续搜；隐藏实例不干扰别处高亮。

## 有意即时或宿主负责的路径

| 路径 | 源码事实 / 责任 | E13 保留 |
|---|---|---|
| QuickChatPopover/Host、electron/main/quick-chat-window.mjs | 原生窗口承载模型/权限/强度/快速选值，DOM 入场 fade；选择/失焦/隐藏保持即时主进程生命周期；既有 closed 事件清旧 DOM | 重开/多屏/焦点/迟到事件、真实 Electron |
| 系统选择/文件对话框/原生 context menu | OS 拥有弹出与退场，renderer 不再加等待或伪遮罩 | OS/取消/目标失效与原焦点 |
| Gateway web-surface.mjs | 原生 select 与行内设备/任务/配对表单；没有自绘浮层或 details，静态/宿主负责 | 移动/软键盘/读屏/过期 |
| Gateway project-web-surface.mjs | 行内会话/任务详情，无 DOM modal/menu/select/details；不跨宿主导入 renderer 样式 | 真浏览器/返回/焦点与读位 |
| TUI/CLI/ACP | 无 renderer DOM 动效；按原终端/命令与结构化状态处理，动画 N/A | 真终端/取消/读屏/恢复 |
| Workbench tabs/Browser keepalive；ReplyDetails/Goal 内容 portal | portal 只是稳定内容宿主，层级由外层 Drawer 或 panel 拥有；不额外重挂 guest/正文 | guest/嵌套/切目标/读位 |
| 对话历史/过程内的原生 details 与行内 ArtifactList | 保既有原生/专属折叠语义及静态历史；没有给历史重播入场；不属于新增浮层 | 动态内容/焦点/原 ID 与阅读保持 |
| 保存完成、继续任务、选值/导航、OAuth 完成 | 原决定/回执先交目标；真实完成可即时切换，不由退场 timer 生成成功 | 失败/部分写入/未知结果、目标先就绪 |

## 审阅与发布责任

本次只做内容/diff、生产入口登记与 JSX 源码结构审阅。未运行单元/集成测试、构建/类型/架构/IPC 检查、截图或交互回归，未发真实模型请求或写个人配置。closePreparation 四个边界用例已编写未运行：成功后才关闭、在途合并、false/异常/拒绝保留、取消的旧结果不关闭或解锁新现场。

E13 在所有 PR 汇合的最终候选取证：逐个菜单/子层开关与快速反向；Escape/Tab/IME/外点/锚点移除；嵌套遮罩/来源失效/归焦/读位；保存失败/保存中新编辑/旧 parent 与迟到；ref 清理/卸载/StrictMode；默认 open/长内容/动态高度/内部浮层不裁切；reduce/隐藏/API 缺失/ready/finished 拒绝/无 end；RTL/窄窗/200%/真实 native window/guest/辅助技术。既有历史点查不覆盖本批新代码。
