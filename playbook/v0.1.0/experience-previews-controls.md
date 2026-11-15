# E09–E10 实施交接：预览闭环与状态恢复

创建时间：2026-10-23
最后更新：2026-10-23

> 状态：**当前路径实现已审阅，候选验证待发布**。用户授权继续 E09–E10、更新矩阵并独立提交推送；测试和回归留到发布前。以下是实施者内容/diff 自审，不是独立评审、运行验收或发布 Pass。

## 来源、依赖和边界

代码分支 `codex/experience-previews-controls`，当前 head `df25f859b71025a2173096d6a0bdda0c1fdfa4ee`（实现 `f2efc4f0`、导航中待确认编辑 `df25f859`）；[PR210](https://github.com/ly-ccx/Peer-Agent/pull/210) 为基于 E07–E08 [PR209](https://github.com/ly-ccx/Peer-Agent/pull/209) / `815ab1363143788aab3c672e850db96cb7685e45` 的叠加 draft，只展示本批增量。知识父提交 `b8206bd9781329d28dfc157a3b71fb0460f8d7d9` / [PR70](https://github.com/ly-ccx/Peer-Knowledge/pull/70)。依赖仍需按最终 head 正常审阅集成，没有合并 GitHub PR。

C 级 renderer、TUI 只读表达与 i18n。沿既有 clientApi/host、Evidence inspection、Workbench 文件读取/打开、memory/objective/automation API；没有新增 IPC、协议、持久路径、能力、许可、触发器、Evidence、签收或 System Context 来源。resource reader/action 集中处理呈现层请求身份、回执与恢复，editableResource 继续承担会话草稿；未增长大 React 表面的异步控制器。AutomationCenter 与 DocumentView 文件净减。

两仓使用干净隔离 worktree；原主工作区的 HEAD/分支/index 与已有未提交文件不进入本批。没有发布、安装、重启或操作个人运行数据。

## 用户目标、状态与恢复

| 用户目标 | 状态 / 事实源 | 控制和恢复 |
|---|---|---|
| 看清附件能否使用 | 原选中文件的 intake、ChatAttachment 的 kind/dataUrl/filePath/text | Bot 附件图片共享灯箱、文本只读预览、unsupported 明确仅元信息；图片只有路径也能进入读取。移除回邻项或输入。卸载后不把迟到文件读取写回 Composer；现有读入错误和数量/大小上限沿用 |
| 图片故障后能继续 | 既有受控 image read 与真实 img load/error | 加载、读取不可用、解码失败分开；用户可清失效缓存重读，有真实路径时重读原文件。解码前禁用原尺寸；失败不删附件。复制与 reveal 检查真实回执、失败可见；不靠复制倒计时维护状态。经典缩略图解码/来源缓存与失败入口同步收敛 |
| 回到引用来源 | 原消息 ID 与既有 locateMessage/分页 | QuoteChip 可显式定位；ReplyAnchors 沿同一消费者，每批最多四页。未找到保原引用，用户可继续；手势/回最新/新请求使迟到查找失效，不猜测替代消息，不自动抢回读位 |
| 分别查看产物和 Evidence | 既有 artifact openPath 与 Evidence refs/source/body availability | Workbench 按文件/图片/diff 读受控内容，旧请求不跨来源回写；刷新失败保旧预览并提示过时，解码与外部打开失败可恢复。HTML 保原 sandbox。TaskVerification checks/outputs、任务报告、目标 observation 与 Automation receipt 可打开 Evidence；元数据每个请求最多 100 条，可继续显示，正文单独按 ref 读取/重读；metadata_only/not_found/unavailable 与截断分别表达 |
| 记忆失败后能继续 | projectMemoryList/items/switches 与每项写入/导出回执 | 初读失败不显示真空，刷新失败保旧事实；固定/撤回/恢复/冲突解决、开关、导出有同步锁及反馈。真实写回执与随后刷新失败分开，不自动重放。来源/trust/范围保留，开关未读到不显示假默认真值。导出仅收到真实文件路径后提供显示，原生取消独立表达 |
| 编辑记忆不丢内容 | 当前 renderer 会话 draft；宿主 reviseStated 产生新记录并撤回旧 ID | 失败保编辑，收起/切换后可回来；保存期间禁改。成功后结束旧记录编辑，并回原操作或稳定容器；不继续向旧 ID 提交。外部撤回/修订后须重读核对，未新增跨记录自动迁移或记忆权限 |
| 控制目标与观察 | ProjectObjectiveView 的来源、状态、watch、notificationPolicy、usage/budget、lastObservation | 每目标动作锁、实际回执、失败重读；编辑会话保留，expectedVersion 使用最近真实读取的保存基线，冲突不会强写。触发来源与通知范围可查，观察 Evidence 可达；指定目标只定位一次，后台刷新不重复 scrollIntoView |
| 自动化失败后不从头开始 | bootstrap、runs list、run receipt 各自的真实读取；definition/version 与动作回执 | 所有 view 都能看见读写反馈；初读失败不显示空/零计数，失败保旧快照与绑定 workspace 的会话 draft；pending/未知结果随编辑会话保留，返回后先等回执/核对，迟到回执不能清除后来草稿。写入期间禁改，收起保留或显式舍弃。未知操作先重新读取并核对，不自动创建/运行重试；版本冲突保表单，展示最新保存内容，用户核对后显式采用当前版本再保存 |
| 看懂暂停、取消和再运行 | 原 runtime pause/status/receipt APIs | 全局暂停只影响既有计划；单次取消/再运行仍按原主机规则。操作确认后即投影收到的定义/取消回执，不以刷新失败推翻写回执。源缺失/读取失败保留入口。已有通知与主动性设置沿 E08 保存链，详情补保存的成功/变化通知范围，不新增触发或送达策略 |
| 后台安静、终端也能恢复读取 | onProjectAgentChanged/onAutomationsChanged 只刷新事实；TUI 当前 workspace 的只读快照 | 普通后台读取不反复播报 loading、不改编辑/展开/焦点/读位；自动化提案同步锁防重复，用户展开选择不随状态刷新重置。TUI memory/objectives 读取拒绝/异常与真空分开，保当前项目上次快照、目标显示实际 outcome；可重开命令继续，不新增终端编辑能力 |

## 覆盖映射与限制

交互矩阵：G08/G09；P06/P11/P12/P14/P15/P16/P46/P47/P50/P51/P62/P63；C064/C077/C100/C108/C135–C138/C146/C148/C150/C165–C167/C169/C170/C197；新增 C207 ResourceFeedback、C208 ResourceEditor、C209 EvidencePreview。实际 Desktop 非测试 TSX 209、TUI 13。非 TSX seam 见矩阵 §6；UI/动效/过渡对应 U05/U06/U10/U11/U13–U16、M01/M02/M04/M16、T01/T02/T08/T09。

预览没有执行入口，也不把文件存在、文字摘要、展开、点击或动画作为核验/签收。Evidence ref 不猜成文件路径，artifact 不自动提升为 Evidence；metadata_only 不伪造正文。旧快照继续可读时明确本次未读到最新值。新增草稿只是当前 renderer 会话内存，不提供进程重启恢复、跨窗口 CAS 或新的配置事务。

既有 automation 创建没有本批新增的幂等协议；未知创建必须先查清单，不能承诺网络故障后再点创建一定不会产生重复对象。目标/自动化保存仍依现有版本契约，记忆依现有修订语义。导出、clipboard、外部编辑器和系统窗口结果需真实 OS 取证。

本批没有将所有挂有 E09/E10 标签的历史组件整体重写。Skills/MCP/文件树/浏览器 guest、经典选区子会话、通知原生送达、远程及完整 TUI 适配继续矩阵对应 V/E11/E12；G10–G12 继续 E16/E17。原有主题、Overlay/Drawer/motion/reduce 兜底沿用，没有增加物理常数、逐字动效或另一套组件系统。

## 内容审阅与发布责任

已完成内容/diff 自审与空白审阅。补写 `resourceState.test.ts`：失败读与真空、旧快照/迟到/取消/主机回执、逐对象同帧锁、失败不重放、刷新失败不推翻写回执、原生取消；`projectReadState.test.ts`：只读拒绝/异常、快照/范围隔离与真空；`automationEditorState.test.ts`：待确认编辑跨导航保留、同步锁与旧回执隔离。**这些用例均未运行。** 没有 unit/integration、build/type/architecture/IPC 检查、截图或交互回归，也没有独立评审、真实模型/安装包/辅助技术验收。

发布按既有 E13：所有开放 PR 正常审阅合并后冻结最终组合候选，再跑完整门禁与产品 packet/review/verify。需覆盖：图片读取/解码/晚图/路径/OS打开与复制；附件超限/移除/切换/未支持；引用旧页/未找到/继续/手势中断；Evidence 元信息/缺失/截断/权限/多层归焦；记忆修订新 ID/冲突/撤回恢复/导出取消；目标/自动化旧版本/迟到/未知写入/保存后刷新失败/失效对象/静音与真实送达；浅深/实色/减少动效/窄窗/200%/IME/键盘/读屏。实现已审阅不等于 Pass。
