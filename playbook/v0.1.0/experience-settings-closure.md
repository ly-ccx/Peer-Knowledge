# E07–E08 实施交接：共享控件与配置保存

创建时间：2026-10-23
最后更新：2026-10-23

> 状态：**当前路径实现已审阅，候选验证待发布**。用户授权继续 E07–E08、更新矩阵并独立提交推送；测试和回归留到发布前。以下为实施者内容/diff 自审，不是独立评审或运行验收。

## 来源、依赖和范围

代码分支 `codex/experience-settings-closure`，当前 head `815ab1363143788aab3c672e850db96cb7685e45`（本轮实现提交 `e6afa786`、重试回读 `a8647978`、失效错误隔离 `815ab136`），评审 [PR209](https://github.com/ly-ccx/Peer-Agent/pull/209)。起点 E05–E06 `2a0ee98be84344b8ae6499ee48b6d25b281afa32` / [PR208](https://github.com/ly-ccx/Peer-Agent/pull/208)；保留原提交身份 merge 复用模型面板 [PR197](https://github.com/ly-ccx/Peer-Agent/pull/197) `21c3f424`、名称优先新建 [PR200](https://github.com/ly-ccx/Peer-Agent/pull/200) `132a0e47`，没有重新实现这些功能或合并 GitHub PR。知识父提交 `4392e29901408f7d8e55529cd36f53a8687b640d` / [PR69](https://github.com/ly-ccx/Peer-Knowledge/pull/69)。依赖仍须按最终 head 审阅集成。

自身是 C 级 renderer/i18n 修改：tokens/Frost 设置样式；共享 SettingsRow、FormFeedback、按钮/输入、editableResource/guard；新建、模型面板/档案、General/Git/个性化/routing/vision、连接/目录/模型元数据消费者；App 仅将设置离开意图接至共享 hook。LlmSettingsPanel 逻辑下沉、文件净减。没有新增 IPC、协议、持久路径、能力、权限、Evidence、签收或 System Context 准入。PR197 自有的协议/runtime fast-mode 变更是依赖的既有实现，不能算本轮新增边界或跳过其评审。

两仓均从干净隔离 worktree 开后续分支；原主工作区的 HEAD/分支/index 和已有未提交文件不进入本批。没有发布、安装、重启或个人运行数据操作。

## 用户目标、状态与恢复

| 目标 | 状态 / 事实源 | 控制与恢复 |
|---|---|---|
| 一套可读、可点、可放大的控件 | 既有 Frost 色/space/字号/曲率；tokens 单点控件高度与焦点，SettingsRow/FormFeedback | 普通/紧凑密度、可收缩行、真实 label/description/error、可见焦点；模型 CSS 独立，专属 keyframes 改共享 motion，实色/reduce/强制颜色静态兜底 |
| 名称明确的新建与绑定 | 复用 PR200；主机 lifecycle receipt 才开新 bot | 名称规范化、无效关联、IME、单次创建；失败/取消保名称；未知明确提示先看列表，不自动重发；绑定目录名称沿现有宿主规则 |
| 看清当前模型与下轮配置 | 宿主 profile/role projection、活动回复的真实 modelSelection 分开 | 浏览服务商不写；焦点与选中分开，面板无乐观 saved；同一模型与有效强度由调用者一次提交；失败请求按 workspace 保留，手动重试先重新读取宿主，再只改原意图字段，保留无关新配置；切换或新选择使旧重试失效；当前范围仍由 host 校验 |
| 配置失败后能继续 | editableResource 的 saved/draft、loaded/loading/saving/dirty/error/stale；原 get/updateSettings、modelRoutingGet/Update、updateProfile | 旧读取不盖新编辑，单次写锁；保存回执才更新 saved，规范化值回读，失败保草稿与重试；model routing 预算保原始输入且写前校验，解析预览与保存分别反馈 |
| 离开前不丢修改 | 编辑器注册 dirty/busy；来源 editor 持有 draft，guard 持有待完成导航 | 设置分区/返回/全局页面/深链均先处理 dirty；可保存并继续/舍弃/继续编辑，忙碌不能舍弃正在提交的写。多阶段连接/目录提供舍弃/继续，回到当前流程执行保存；Overlay 在退场前 veto，安全初始焦点/同层恢复沿 E06 |
| 连接与模型目录不重复/不误删 | 既有 provider/model IPC 结果与当前 catalog | 敏感字段只留当前编辑器，不进共享 draft cache；读取失败保旧列表并重试；父 render 不清目录选择，手动增加保留已有模型；新连接首个手动模型确认后关闭；实际导入后直接共享退场，不额外等 420ms |
| 机器人档案可恢复编辑 | 名称、并发与各项策略/头像/删除的真实宿主回执 | 名称按 workspace 在当前 renderer 会话保留，重新读取不会盖 dirty；并发读失败不可提交假默认值；动作防重入、失败可见且用户重试，取消上传不显示已保存 |

草稿内存只保留非凭据编辑，成功写入配置仍走既有存储。没有新增跨重启持久草稿、跨窗口 CAS、创建幂等请求、配置原子事务或自动业务重试。创建未知先核对列表，已有多项 provider 写入/回滚可能部分完成，须沿真实主机事实核对；界面不把未确认当失败，也不承诺已替宿主回滚。OS 关闭拦截依宿主行为，完整输入法、读屏、真实窗口与系统故障留发布取证。

## 覆盖映射和未完成工作

G04；P03/P17/P28/P29/P31/P33/P34/P35/P37；C001/C020/C022/C023/C026/C028/C029/C031/C041/C044/C050/C114/C128/C132/C137/C161/C163/C180，新增 C203/BotModelFeedback、C204/FormFeedback、C205/UnsavedChanges、C206/SettingsRow；TS/hook seam 登记在矩阵 §6。U01/U03/U05–U08/U14/U15、M01/M02/M04/M06、T01–T04 由同一次实现承接。实际 Desktop 非测试 TSX 206，TUI 13。

E07 是本批真实消费者的收敛，不声称所有历史按钮/图表/设置都已迁移；能力、远程、用量/快捷键/开发宿主等其他面板继续按各矩阵行。G08 图片失败、G09 记忆恢复、G10–G12 启动/粒子/问题 WAAPI 继续 E09/E10/E16/E17。PR204 抽屉、PR198/206 TUI、其他运行时与 Goal 仍待最终 head 集成；未夹带主工作区的抽屉/TUI/Git 在制代码。

## 内容审阅与发布责任

已完成内容/diff 自审与空白审阅。新增或调整的用例涉及：保存失败保草稿、迟到读取与较新回执、dirty 重读/还原、同帧重入和保存中继续编辑、读取失败不得写、routing 最小 patch/预算校验、导航待决与确认后不重复拦截、模型重试保留无关新角色/范围及以新读取值判断是否需要写入，以及已有设置返回控件断言。**均未运行**；没有 unit/integration、build/type/architecture/IPC、截图或交互回归，也没有真实模型/安装包/辅助技术验收。

发布按既有 E13：全部开放 PR 正常合并后，冻结最终组合候选，跑完整门禁和产品回归。需补证：新建取消/未知与列表重试；各保存读写失败/迟到/外部变化/非法输入；dirty 分区/深链/全局导航/嵌套确认/保存中/OS 关闭；连接/OAuth/Key/目录空或失败/手动与部分导入；本轮/下轮/继承/范围及 slider；浅深/主题/实色/reduce/200%/长名/窄窗/真实 IME/键盘/归焦/读屏。仍沿既有 packet/review/verify，不新建第二验收账本。实现已审阅不等于 Pass。
