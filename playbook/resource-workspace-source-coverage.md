# 资源工作区 R1–R10 源码覆盖与交接现状

日期：2026-10-27
状态：完成源码连线；用户随后明确要求的 R1–R10 组合模块、实际 Electron 深浅色联调和 89 张截图自审已通过，问题已修复复跑。详见[本轮验证记录](resource-workspace-r1-r10-validation.md)；不是完整产品发布验收凭据。

本表汇总分散实施卡的最新源码状态，不覆盖其中有日期/候选身份的历史记录。原始范围以 ADR109 为准；早期“待 R9/R10”的文字只是当时进度，不代表当前仍缺整个编辑或提交阶段。R1–R4d 已有第一阶段交接；后续累积工作位于专题隔离工作区，尚未提交推送，本表不表示已可在另一台电脑获取。

## 逐项连线

代码落点均相对于 Peer-Agent 仓库。`renderer` = `apps/desktop/renderer/src`，`host` = `apps/desktop/electron/main`，协议在 `packages/protocol/src`；这只是阅读缩写，不是新的 Module 或机器路径。每行列的是实际入口/Module 与对应已编写用例；**文件存在、内容审阅和代码生成不等于用例已通过**。

| 实施包 | 实际入口、宿主与事实归属 | 恢复/拒绝边界 | 对应回归用例 |
|---|---|---|---|
| R1 引用契约 | `document-reference.ts`、resource-reference hints、`renderer/workbench/documentSessionState.ts` | 版本、任务、来源与呈现元数据分开；可选旧字段兼容，未知输入不能造授权 | protocol 引用/hints、documentSessionState、workbenchTabState |
| R2 回复引用 | `renderer/chat/components/markdown/documentReference.ts` / InlineMarkdown、`project-agent/state/botResourceReference.ts`；现有 runtime.workspace Context Source、历史 Interaction Reader | 分支/符号不因斜杠变文件；裸文件名仅同轮唯一结构化来源绑定，同名要求选择；不重写旧正文 | documentReference / inlineMarkdownPreview、botResourceReference、interaction-reader、runtime-source |
| R3 有界解析 | `host/bot-document-reference.mjs`、file-access application service、已有 workspace-file-search | 当前 Bot/任务/已登记根与知识库身份复核；相对来源不明给候选；不扫描全盘、不换别的会话/根 | bot-document-reference、file-access-application-service、workspace-file-search、scoped IPC |
| R4 非模态外壳 | BotResourceLayout、WorkbenchPanel、ResourceWorkspaceHeader、useResourcePresentation | 默认侧面、显式放大、确实不足才单区；原会话/Composer 草稿保留；关闭与挤压复用动效，后台不夺焦点 | resourceWorkspaceState、workbenchLayoutProjection / ResizeStages / Maximize、useConversationWindow 浏览器用例 |
| R4a 网页 | BrowserView / BrowserPage、BrowserSession、browser-core application service、browser Registry/reveal coordinator | 真实 guest 稳定挂载；混合切换不重载；后台 reveal 不能替换正在读的文档；不执行恢复导航/表单重放 | BrowserPage、workbenchBrowserVisibility、browser-control-registry、browser-panel-reveal-coordinator |
| R4b 目录 | ScopedResourceNavigator、FilesView、已有 scoped directory reader | 代码/知识库根单独核对，面包屑/展开/刷新只读；不变更任务 cwd 或权限根 | filesTreeFilter / Presentation / Refresh、file-access-application-service |
| R4c Diff | ResourceChanges、ScopedComparisonPage / ComparisonRead、DiffViewer / DiffFileIndex、scoped Git reader | working/staged/固定提交/真实任务完整来源；无隔离工作树不回退项目根；读取不 apply | resourceComparisonState、ComparisonRead、DiffViewer、file-access-application-service、project-agent host |
| R4d 启动器 | ResourceLauncher、ResourceSearchResults、ResourceWorkspaceHeader | 显式 URL/路径、文件名有界查找、文件与目录/比较入口、scoped 最近记录；打开 launcher 不分配文件/guest、不执行命令 | resourceWorkspaceState、resourceWorkspace smoke（历史候选）、workspace-file-search |
| R5 身份/历史 | useObservedDocument、documentObservationState / RevisionState、DocumentHistoryTools、git-document-reader | 当前内容变化保留已接受正文；固定完整 SHA 与仓库身份；历史缺失不借当前正文补齐 | documentObservationState / RevisionState、DocumentHistoryTools、git-document-reader |
| R5 领域恢复 | directorySessionState、browserRecoveryState、useDirectoryReadingPosition、WorkbenchContext | 按 Bot 恢复阅读元数据；网页只声明 URL 级恢复，崩溃/失效明确；旧设置迁移不隐式执行 | directorySessionState、browserRecoveryState、settings-store |
| R5w1 文档/目录/比较窗口 | resource-window-controller / view-registry / reader / history / handoffs，NativeResourceWindow / NativeResourceRead / NativeResourceComparison | 实际 sender/window/view/generation/owner；最小 sandbox preload；显式副本/返回；独立读位、跨窗 writer 仍由草稿宿主裁决 | resource-window-controller / reader / history / handoffs / view-registry、nativeNavigationState、NativeNavigation、resourceWindowReturnState |
| R5w2 网页窗口 | browser-window-controller、NativeBrowserWindow、browser-target-continuity、window-aware Registry | 真实 WebContentsView 单一归属；只能显式地址副本；未证明保活迁移时无“移动”动作；关闭不停止任务 | browser-window-controller、nativeBrowserPresentation、browser-target-continuity、local-browser-control-provider-headless |
| R5a 详情统一 | useResourceDetails、BotProfileDrawer 的工作区 Portal、ConversationScene / SessionDetail / EvidenceView | 复用原 Bot/task/Evidence 真源；embedded 路径不嵌第二工作台/旧 modal；设置启动收起、展开状态准确 | detailSurface、drawerState、resourceDetailState、useResourceDetails |
| R6 适配与退化 | MarkdownDocument、SourceViewer、RasterImageView、DiffViewer、documentAdapterState | Markdown 正文、源码/JSON、位图；HTML/SVG 只读不执行；复杂/过大 Diff 明确退化、图片解码失败局部恢复 | documentAdapterState、presentationBudget / Components、rasterImageState、diffPresentationState |
| R6a 辅助导航 | ComparisonNavigation、useResourceNavigation / ForegroundRefresh / ComparisonRefresh、ComparisonRead | 来源切换与固定比较分开；前台观察只提示候选，不替换读位；已有 dirty 文件不冒称当前任务成果 | resourceNavigationState、foregroundRefreshState、comparisonRefreshState、ComparisonRead |
| R7 交付关联 | host/project-agent/evidence-deliveries、EvidenceDeliveries、DocumentDeliveryTools / DeliveryHistory | 仅真实 UserArtifact/Evidence/任务归属生成关联；路径只定位当前文件；历史快照缺失明确，不能用当前文件冒充 | evidence-deliveries、deliveryBindingState / Presentation、evidence reader 范围用例 |
| R8 主窗口选区 | ResourceSelectionFeedback / DirectoryFeedbackAction、ResourceFeedbackCards、feedbackDraft、现有 InputRecovery/Queue 和 user-role 历史投影 | 明确固定 recipient/resource/version/selection；准备仅持久草稿，明确发送后才进模型；摘录无工具/权限真值 | resource-feedback、resourceSelection.browser、directoryFeedback、feedbackDraft、resource-feedback-input、project-input-recovery、conversation-history-projector |
| R8 网页/原生交接 | browser-selection-feedback、resource-window-feedback、resource-feedback-preparation / recipient、useResourceFeedbackPreparations | 真实菜单/frame/导航代次；原 sender claim→持久回执；截止和迟到结果失败关闭，不自动发消息/重试 | browser-selection-feedback、resource-window-feedback、resource-feedback-preparation / recipient、useResourceFeedbackPreparations |
| R9 草稿与快照 | resource-edit 协议、runtime-core/resource-edit-state、runtime-node/project-agent/resource-edit-storage、host resource-edit application/sources | 保存意图、blob/索引分离、限额/清理/schema 迁移、真实 writer/CAS；旧稿/操作事实保留，恢复不 start | resource-edit、resource-edit-state、resource-edit-storage、resource-edit-application-service / sources、resource-window-edit-source |
| R9 编辑/恢复 | ResourceEditor / DraftDocumentPage / ResourceDraftLibrary / ResourceEditContinuity、resourceEditSession / Registry | IME、later input、冲突、明确接管、三方比较、另建基础、关闭先安全保存；不写原文件 | resourceEditSession / Registry、textInputEdit、NativeNavigation、resource-window-controller |
| R10 条件能力 | local-conditional-file-provider、resource-file-replace-projection、resource-edit-runtime、file-mutation-lock | 人提交专用 Manifest/Projection，既有 SDK→Provider→实际 Grant→Evidence；权限后版本检查；同宿主互斥；部分写入保留 uncertain | resource-file-replace、local-conditional-file-provider、resource-edit-runtime、file-mutation-lock、versioned-file-diff |
| R10 日志/授权 | resource-edit-execution-storage / journal / permission-bridge / submission-host / service、typed IPC/preload、实际 Bot authority/ApprovalStore | 原始结果先持久再 PostHook；固定 nonce 只启动一次；同窗真实 view 恢复原授权，其他窗不能代批；未知只核对，不重放 | resource-edit-execution、execution-storage / journal、permission-bridge、submission-host、register-resource-edit-ipc |
| R10 局部交互 | ResourceSubmissionControl / Details、resourceSubmissionController / State | 固定稿与后来输入分开；局部允许/拒绝/取消/核对；真实 Diff/Result 与独立验证/签收分开；关窗不是取消/重跑 | resourceSubmissionController / State、submission-host 的固定稿/新基础/后置待确认/清理组合用例 |

## 本轮发现并修正的实际缺口

R5w1 原生关闭仍沿用“500ms 无回执也关闭”的只读阶段规则，与 R9 的草稿安全关闭契约冲突。beforeunload 虽另有保留输入措施，宿主一次性许可却会在 unload veto 后留到下次关闭，后续可绕过新检查点。不能只靠渲染层拦截来掩盖这条生命周期遗漏。

先补 ADR109 §38.8，再落协议、真实 handoff/controller、最小 preload 和 NativeNavigation/NativeResourceWindow：确认/阻止均明确回执；超时保留窗口；迟到回执失效；许可仅消费这一次关闭，下一次重新核验；局部错误说明、继续输入/保存/关闭，不夺焦点、不取消或重跑提交。新增前端检查点用例及宿主 timeout/迟到确认/失败重试/unload veto 用例，纳入原组合清单。必要 preload 代码生成已完成；未运行这些用例。

另核对关闭草稿标签时保存等待跨 Bot 的路径：WorkbenchContext 的 document updater 已捕获原 conversation key，后续邻居激活另核当前 owner；本轮未发现该路径会修改新 Bot，因此没有添加多余的状态层或改动。

## 静态审阅时的未验收项与边界

以下“未运行”保留静态审阅当时的状态。当前组合结果以[本轮验证记录](resource-workspace-r1-r10-validation.md)为准：697 项模块、10 组 Electron 深浅色联调、98 个具名检查、89 张截图自审及源码/图片完整性核验通过。G8、安装包、真实模型和完整辅助技术验收仍未完成。

- R1–R10 原计划内的源码入口、宿主和恢复链已有对应落点；本轮未发现另一个整包未接线的阶段。后续若运行发现问题，按实际结果修，不能拿这份静态表当通过证据。
- 当前累积候选没有执行完整编译/类型/架构/IPC 检查、模块/跨层用例、真实 Electron 明暗/宽窄/原生窗口/IME/辅助技术/减少动效/任务中断组合。历史第一阶段、R5–R6 或 R6a 的记录仅覆盖其当时候选。**G7/G8 未通过**。
- 按仓库当前 Validation Scope，普通继续不自动执行测试/截图/联调，也不重启应用。需用户明确当前任务提前验证，或进入版本/RC 发布门禁时，才在隔离夹具跑最终组合；不拿个人正在进行的任务或已完成写入作验证。
- 原计划允许增量的 PDF/Office 专用正文适配、复杂格式区域编辑、生成网页/本地 dev server 自动执行、跨设备草稿同步、实时多人协同、未经验证的同 guest 跨窗移动不伪称已实现。真实 HTTP(S) 网页、文档/源码、目录、Diff 与显式网页地址副本已在上表覆盖；不能将普通网页推迟为“后续能力”。
- 本地原工作区、索引、运行实例、当前任务和成果继续保留；未提交/推送/发布。源码交接需用户明确提交范围后再组织两仓提交并同轮推送，不能把无关 dirty 文件捎带进去；Git 不迁移运行任务、应用数据或密钥。

## 验证材料使用方式

`apps/desktop/scripts/resource-workspace-tests.mjs` 是已编写模块/夹具组合入口，不是最近运行报告。G0–G8 前后端与跨层场景仍以 [回归测试设计](resource-workspace-regression-test-design.md) 为准，所有动态结果绑定实际候选。发布时还必须遵守代码仓全量 open PR 合并、最终候选冻结和完整产品回归门禁。普通开发的内容/diff 审阅与保留性摘要只证明本次改动边界，不证明业务成功。
