# 智能输入建议实施任务卡

创建时间：2026-10-31
最后更新：2026-10-31
状态：IP-00—IP-06 已实现且本次提前功能验证通过；IP-07 发布门禁未执行，不代表纳入下一版本／RC。
决策：[ADR 115](../../knowledge/decisions/115-input-prediction-and-draft-boundary.md)（Accepted）。
完整方案：[Peer 智能输入建议](../../design/product/peer-input-prediction.md)。

## 1. 目标、范围与授权

交付 Desktop 主 Bot 和经典可编辑 Composer 的单候选灰字建议：空草稿预测下一句、末尾续写已有草稿，Tab／右方向键采纳，可撤销；发送、回执、权限、Evidence 和签收保持原有链路。

最初的文档轮次用户只授权把方案、ADR 和任务拆分写进 peer-knowledge，明确暂不改代码。以下是后续可派发的卡片，不是本轮执行指令；不得因卡片存在就安装、重启、发真实模型请求、写代码、合 PR 或发布。ADR 状态、用户实施授权与实际依赖就绪均需在实施入口核对。

后续授权（2026-10-31）：用户要求“完整做完，自己独立验证整个功能”，覆盖 IP-00—IP-06 的完整实现及 IP-07 中本功能的提前验证。此指令解除之前暂不编码／不提前验证的限制；不自动授权版本发布、安装／重启应用，最终联合发布门禁仍留在实际发版时执行。技术接缝、基线和验证独立性已在 ADR 115 的实施启动节登记。

不包含多候选、逐词采纳、主动扫描、自动发送、问题卡代答、预测历史、跨项目学习、Quick Chat／TUI／CLI／远程入口的实现。

## 2. 依赖图与交付顺序

```text
IP-00 治理与接口准备
  → IP-01 协议与交互内核
    → IP-02 纯预测服务、Context、模型与预算
      → IP-03 Desktop IPC、生命周期与隐私设置
        → IP-04 主 Bot 下一句预测、编辑事务与展示
          → IP-05 已有草稿续写
            → IP-06 经典 Composer 复用
              → IP-07 联合候选发布验收
```

按依赖顺序交付，不默认启动并行 Agent。具体工作树／分支由派发时确定，新增分支使用代码仓当前约定的 codex/ 前缀，不在本文件锁定旧开发分支或旧源码。用户未要求提交时不自动提交；一旦实际 commit 必须同轮 push。

## 3. 共用实施纪律与验证时机

- 以代码仓最新 AGENTS.md、产品 north star、ADR 115 和有效体验规范为准。旧手册或旧卡片里“每日必须跑测试／截图”被最新 Validation Scope 覆盖。
- 各卡补有价值的契约、reducer、准入、权限边界和时序用例；日常默认只审新增内容与 diff，不运行测试、构建、类型、架构／IPC 检查或截图／交互回归。用户明确要求提前验证时另记范围。
- IP-07 属于发布工作，只有用户授权准备版本／RC 时执行；必须使用最终联合候选，完成所有开放 PR 的合并门槛和完整验证。不能把某张功能卡的未运行用例写成通过。
- 已有 dirty 文件保留，不夹带别的任务。不得改写既有授权／Evidence／输入回执、全局发送快捷键，或借此重构整套 Provider。
- 不新增依赖。新 Module 必须拥有真实职责，提高 Locality／Leverage；主进程与 ChatSurface 不增加业务策略堆积。
- 每卡更新相关体验矩阵的实际适用行，状态最多记录实现／内容审阅，验收通过绑定 IP-07 真实证据。本旧知识工作树缺矩阵时不重建简化副本。
- 通用允许范围中的“必要出口／类型／测试／生成物”必须在 IP-00 收敛到实际文件清单。实施中确需越界先记录必要性和边界影响；涉及新能力、存储或政策则先更新 ADR，不自创旁路。

## 4. IP-00：治理、规范与实作接缝准备

级别：A 级准备；规模：小。依赖：ADR 115、用户后续实施授权；当前状态：已完成准备，接缝与基线见 ADR 115。

**目标**：让后续执行者拿到可落实的事实、契约和文件范围，解决知识工作树落后于 origin/main 的依赖问题。

**必读**：ADR 115、完整方案全部；代码仓 AGENTS；产品理念；System Context 与治理；ADR 83／85／100／101；实施工作树中的最新 Frost、交互、motion、transition、开发工作流、两份矩阵；当前有效的 runtime 模块／Bot 指令与输入性能决策。

**代码锚点**：完整方案 §14；特别是 createProjectInputRecovery.edit／flush／send、两类 textarea 的事件顺序、Provider trace／prompt snapshot、模型默认角色解析和预算端口。

**允许改动**：本卡、完整方案、ADR 115 的范围／Interface 补充；规范与矩阵的整合由现有知识分支合并流程承载，不能覆盖在途 dirty 文件。此卡本身不改代码。

**不许改动**：既有架构决策结论、发行计划的已完成状态、运行实例、代码／设置／授权存储。

**实现要点**：固定实际实施基线、来源与 owner；核对 ADR 115 编号和 Proposed／Accepted 状态；列出后续卡的精确文件和既有导出／生成流程；确认不会把默认聊天模型自动当作已选择的预测模型；明确编辑事务如何与原生 beforeinput／撤销协调，不能用 setState 代替方案；定位现有用量存储可否承载用途、token／次数、预算预约与结算。

**需登记的验证用例**：无新测试代码；登记所有尚需 IP-01—IP-07 覆盖的反例及真实 Electron／IME／读屏范围，记录基线差异。

**退出条件**：用户已授权实施且 ADR 完成必要评审；实施分支实际拥有规范／矩阵；各卡路径与责任可定位；Provider trace 保密、无工具推理、预算和编辑事务均有具体 seam。现有端口不足时先补 ADR 方案，不带着模糊“以后处理”开工。

## 5. IP-01：Protocol 与输入建议交互内核

级别：A（Protocol）／B（内核）；规模：中。依赖：IP-00；状态：已实现，验证见末尾交接。

**目标**：固定请求／候选／取消／校验／错误契约，建立不依赖 React、Electron、Provider 的输入建议状态机。

**必读**：ADR 115 §3—§5；完整方案 §3—§4、§8—§9。

**代码锚点**：packages/protocol/src/project-input-recovery.ts；packages/runtime-core/src/project-input-recovery.ts；apps/desktop/renderer/src/chat/state/compositionGuard.ts。

**允许改动（拟定）**：新建 packages/protocol/src/input-prediction.ts、packages/runtime-core/src/input-prediction.ts 及契约／状态用例；两包必要类型出口。文件命名在 IP-00 固定后使用，不能散落状态到大组件。

**不许改动**：ProjectInput／PermissionGrant／Evidence 语义、sendMessage 参数、持久草稿 schema、任何实际推理／工具执行。

**实现要点**：独立 draftVersion 和输入实例身份；状态覆盖 idle／waiting／requesting／visible／accepting／accepted／dismissed 与无建议、不可用、失败；请求／候选 owner 及模式匹配；selection、quote、attachment、输入目标／发送尝试变化使旧代次失效；定义采纳 CAS 和编辑事务效果，不由 reducer 自己持久化或提交用户输入。

**必须新增的用例**：空草稿 Enter 不采纳；真实前缀 Enter 仅发真实值；行中／选区／修饰键不采纳；IME 优先；旧 requestId／draftVersion 拒收；重复采纳幂等；validate 期间编辑／切换／发送使回填失效；dismiss 不立即重生；候选不进入 pending／恢复；候选格式／UTF 边界。

**日常退出条件**：类型、状态转移、不变量和 diff 已审阅；用例已补且如实标未运行；明确各宿主需提供的 effect／port。此卡不宣称 IME 或原生撤销实际通过。

## 6. IP-02：受控预测服务、模型与上下文

级别：A（角色／Context／用量契约）／B（服务）；规模：大。依赖：IP-01；状态：已实现，验证见末尾交接。

**目标**：实现可取消、无工具、无正文落盘的单次预测，集中上下文准入、候选检查、预算、缓存和失效规则。

**必读**：ADR 115 全部；完整方案 §5—§9、§11—§12；当前有效模型路由和运行时公共子路径决策。

**代码锚点**：model-router.mjs；protocol/model-routing.ts；system-context/prompt-assembler.mjs、prompt-source-registry.mjs、sources/；runtime-node/provider-adapters/、provider-encoders/、provider-diagnostics/provider-trace-recorder.mjs；既有 usage／预算实现。

**允许改动（拟定）**：新建 packages/runtime-node/src/input-prediction/ 下 service／context／policy 等有职责 Module 与用例；新增 system-context 的预测 Source／profile 及用例；model-routing、model-router 的角色加法；无工具纯推理 seam 的最小 Adapter／Encoder 适配；既有用量协议／存储 Module 的用途与限额必要加法；既有领域子路径与打包清单。若需新持久路径，回 ADR 处理，不能默认添加。

**不许改动**：原 chat 默认 Context 层序、Agent 工具循环、能力投影／授权策略、Provider 接口兼容、记忆与历史正文存储；不得伪造 webContents。

**实现要点**：输入 source／信任／版本和 4K token 预算；必需约束缺失时 abstain；next_turn 不带未发送草稿；continuation 明确准入；无 tools 与 executor；异常工具调用拒收；input_predictor 显式路由／localOnly／预算；有界内存、TTL 和来源重检；正式请求优先、取消和实际用量归属；prediction metadata-only tracing，禁止 body、草稿、候选或可反查正文 hash 落盘。

**必须新增的用例**：跨工作区／私有消息不准入；材料／必需约束缺失；恶意历史不能升级系统指令；profile 不污染 chat；默认 fast 指向聊天模型不等于授权预测；scope／localOnly／配置变化失效；非法 JSON／超长／模式错误／工具调用；取消／超时／晚 usage；预算预约／结算／费用 unknown；LRU／字节／TTL；trace／snapshot／错误对象不含正文；无自动修复或重试模型调用。

**日常退出条件**：服务 Interface、适配范围、错误与用量路径内容审阅完成；有相应用例但默认未运行；源／cache／trace 与存储边界清楚。不得报告实测延迟或模型质量。

## 7. IP-03：Desktop 宿主、Typed IPC 与隐私设置

级别：A（设置与 IPC）／B（owner）；规模：中。依赖：IP-02；状态：已实现，验证见末尾交接。

**目标**：提供真实受信的 request／cancel／validate 端口、单服务生命周期和可理解的功能／路由／草稿外发设置。

**必读**：完整方案 §8—§9、§11—§12；当前 IPC catalog、可信窗口、settings 迁移和 shared SettingsGroup 约定。

**代码锚点**：apps/desktop/electron/main/ipc/register-all.mjs、trusted-window-registry.mjs、register-project-agent-ipc.mjs；electron/ipc/channels.mjs；electron/preload/preload.source.cjs；renderer/src/preload/contracts/peerAgentPreloadApi.ts、clientApi.ts；settings-application-service.mjs；settings-migrations.mjs；ModelRoutingPanel 与 SettingsGroup。

**允许改动（拟定）**：新建 main/input-prediction/ 的 Desktop service／snapshot Adapter 与 main/ipc/register-input-prediction-ipc.mjs；既有 owner/composition root、IPC/preload/clientApi 的必要接线；settings schema／迁移／应用服务；设置目录内小控件及 role 配置；i18n；对应用例。生成物按原生成机制更新，不手改构建产物。

**不许改动**：main.mjs 新增业务策略、远程写端口、凭据持有方式、BotProfile 权限、任务调度语义；不创建预测数据库。

**实现要点**：服务唯一 owner／dispose；可信 sender 和 surface 白名单；workspace／conversation 归属和请求大小；跨窗口 cancel／validate 隔离；contextToken 非授权；现有安装缺省关闭、启用默认仅下一句、续写独立披露；指定预测角色模型，项目 scope 可收紧；设置失败保持原实际值，关闭取消后续请求且不声称撤回已发数据；token／请求限额沿 ADR 配置。

**必须新增的用例**：不可信窗口／错误 owner／篡改目标；重复和未知 cancel／validate；窗口销毁清理；设置读取不写入、旧配置迁移、保存失败／并发；切路由／localOnly／项目关闭；关闭时在途候选失效；下一句模式拒收非空草稿；服务不会 submitInput 或改变 permission／resultAcceptance。

**日常退出条件**：协议、catalog、生成源和宿主路径一致，内容／diff 已审阅；用例与未运行状态登记；不以 IPC 类型存在声称安全验收完成。

## 8. IP-04：主 Bot 下一句预测与可撤销采纳

级别：C（产品表达），使用已批准 A/B Interface；规模：大。依赖：IP-03；状态：已实现，验证见末尾交接。

**目标**：主 Bot 空草稿展示单灰字候选，Tab／右方向键／按钮采纳，经原草稿 seam 保存并能可靠撤销。

**必读**：完整方案 §2—§4、§9—§10、§13；Frost、交互、motion、transition 与相关矩阵。

**代码锚点**：BotComposer.tsx、BotConversationComposer.tsx、useInputRecovery.ts、inputRecoveryProjection.ts、project-input-recovery.ts；compositionGuard.ts；Bot 消息公共投影／完整回复终结身份。

**允许改动（拟定）**：主 Bot Composer 叶子接线；新建 renderer/src/chat/hooks/useInputPrediction.ts、chat/components/ComposerInputSuggestion.tsx、chat/state/composerEditTransactions.ts 及真正共享的几何／键盘接缝；必要 Bot 样式、i18n 和用例；如果输入恢复需要最小订阅／事务 Interface，由 IP-00 明列，不另造草稿库；两份知识矩阵的适用行。

**不许改动**：ChatSurface／BotConversation 历史层新增预测业务、正式发送语义、引用／附件值、草稿恢复责任、自动滚动规则、第二套视觉／动画库。

**实现要点**：只取当前完整回复，前台资格／焦点检查；灰字不进 value／复制／字数／hasContent／恢复；稳定候选、不逐 token 显示；采纳本地 validate + 本地 CAS；编辑事务覆盖原生撤销／重做和后续手工输入；采纳后第二个 Tab 能离开；按钮与读屏入口，强制颜色／窄窗不可完整显示时不建议；测量按帧合并，不放大逐键历史渲染。

**必须新增的用例**：空草稿 Enter 无发送；采纳才 edit、发送才 submit；IME／repeat／Escape／Shift+Tab；离开建议交互组失效、输入框移向采纳按钮仍可操作、菜单优先；validate 期间编辑／发送／切 Bot；一次采纳撤销、后续输入撤销／redo；保存失败仍保留草稿；unaccepted 重启不恢复、accepted 沿原草稿恢复；合法文字引用准入、引用无效或附件／resourceFeedback 存在不预测；view／history 订阅不被候选更新唤醒。真实 Electron 原生输入、几何和辅助技术归 IP-07。

**日常退出条件**：实现与测试内容已审阅，矩阵登记“实现已审阅，待发布验收”；不运行截图／交互回归，不宣称可访问性或实测性能通过。

## 9. IP-05：已有草稿末尾续写

级别：C（输入行为），复用 IP-01—IP-04 契约；规模：中。依赖：IP-04；状态：已实现，验证见末尾交接。

**目标**：启用 continuation 后，短暂停顿显示 suffix，完整保留用户前缀、selection、IME、撤销和未发送草稿隐私边界。

**必读**：完整方案 §3、§6—§7、§9—§12；continuation 外发披露和首版长度／材料限制。

**代码锚点**：IP-04 控制器、覆盖层与编辑事务；BotComposer 的 onChange／composition／selection；input_predictor Context 准入。

**允许改动**：上述共享 Module、主 Bot 叶子接线、必要 i18n／样式和用例；IP-02 仅在已固化 suffix 契约确有接线缺口时作局部调整并记录；矩阵适用行。

**不许改动**：角色范围、草稿存储、执行链、用户前缀、发送快捷键和费用政策；首版不加“消费匹配前缀”优化。

**实现要点**：input 事件去抖 500ms、IME 后再排程；末尾无选区且无修饰键才采纳；超长草稿／附件／resourceFeedback 不请求；每次编辑清旧候选、延迟响应拒收；suffix 追加边界和 grapheme 处理；Enter 只发送真实前缀；外发只使用显式开启 continuation 时的当前输入实例。

**必须新增的用例**：非末尾／选区／IME／paste／composition 尾随按键；suffix 不重复前缀；用户输入与建议冲突立即撤掉；Enter 不发送 suffix；continuation 未开时任何请求／trace 均无草稿；撤销恢复原前缀和光标；超限／材料不全 abstain；新回复、路由变化、validate 超时不回填。

**日常退出条件**：两种模式和事件竞争的内容／diff 已审阅，用例已补、未运行；矩阵更新，不写已测准确率或延迟。

## 10. IP-06：经典 Composer 复用与边界收口

级别：C（入口 Adapter）；规模：中。依赖：IP-05；状态：已实现，验证见末尾交接。

**目标**：经典可编辑输入框复用同一服务、控制器和编辑事务，正确仲裁 slash／@／引用覆盖层，保持经典发送和草稿库。

**必读**：完整方案 §3、§10、§14；经典 composerPersistence、引用流／mention／slash 行为与相关矩阵。

**代码锚点**：ComposerDraftControls.tsx；composerPersistence.ts；compositionGuard.ts；IP-04／IP-05 新共享 Module；经典 preload/clientApi 的已有调用路径。

**允许改动**：ComposerDraftControls 的叶子装配、共享覆盖层／键盘仲裁必要扩展、经典草稿 Adapter、小样式／i18n 和用例；矩阵适用行。若只读 ChatSurface 被用于任务第四栏，不因为组件存在就开放输入。

**不许改动**：经典 submitMessage／chatSend／队列真值、主 Bot ProjectInput 输入链、ChatSurface 大组件新增预测状态、Quick Chat／TUI／CLI／远程端口。

**实现要点**：真实 conversationId／输入实例绑定，slash／@ 和浮层先消费按键；引用的 text-indent 与镜像共用测量；编辑历史消息和只读面禁用；经典原草稿保存不强迁到 Bot InputRecovery；同一预测用途和预算，不能复制后端。

**必须新增的用例**：slash／@ Tab 与 Enter 优先、Escape 层级；引用缩进与开头退格语义；经典队列、发送、切会话、编辑取消、模型变化；只读任务现场／未支持入口没有请求；经典采纳／撤销／存储失败保持原恢复责任。

**日常退出条件**：两个入口均接统一 Module，差异局限于草稿／发送 Adapter；内容／diff 与矩阵已更新，测试／截图／交互默认未运行。

## 11. IP-07：最终联合候选发布验收

级别：发布门禁；规模：大。依赖：IP-00—IP-06 全部实现、用户明确授权准备版本／RC；状态：未开始；本轮只提前验证功能，未授权准备版本发布。

**目标**：在所有提交 PR 合并后的最终源码上证明输入不误发、不丢失、不越权、不泄露、可恢复，并确认建议质量与延迟的实际覆盖。

**必读**：代码仓最新 Release Pull Request Gate／Validation Scope／Product Regression；本方案 §13；知识库当前 product-regression.md／release-process.md；全部卡片实际交接记录。

**允许改动**：发布产品场景／夹具、测试发现问题的对应 Module、必要知识矩阵与证据回执。修复造成边界变化先更新 ADR；当前不预授权合并／tag／安装／重启。

**执行顺序**：先确认各实现卡必需用例和产品场景已完整纳入提交，再清点全部开放 PR（含 draft／非发布目标分支）并完成合并门槛 → 固定最终联合源码 → 按实际 package scripts 执行完整 build／tests（含本功能契约／取消／预算／隐私用例）／type／architecture／IPC → 标准隔离产品 capture → AI 查看每张必需图并填写 review.json → 同包 verify → 汇总真实模型／安装包／辅助技术覆盖与限制。验证发现需修改源码时重新冻结联合候选，重跑完整门禁，不沿用旧图或较小候选的通过结果。发布 tag 前再次清点开放 PR 必须为空。

**必须覆盖**：完整方案 §13.2 的所有反例；两类 Composer、中文／日文 IME、实际平台撤销／重做、Tab 可退出、内部滚动／字号／主题、结构化决定停用、跨 Bot／窗口、日志正文检查、预算／取消真实结算。截图不证明输入法或读屏正确，需另附实际交互依据。

**质量／性能记录**：记录实际 provider／模型／路由、样本来源、网络／设备、请求和展示分母、P50／P95、abstain／非法输出、采纳后修改／撤销和用量。不能把合成模型成功当作真实预测质量，不能把计费 unknown 当作 0，也不能编造数量目标的已达成结论。

**退出条件**：全部强制门禁通过，无开放 PR；硬性反例无未解决阻塞；截图 review 与 verify 绑定相同最终源码；独立性如实标注（实施者自审不是独立复核）；真实模型、安装包、无障碍及宿主限制有明确声明。未满足则保留阻塞，不发布，也不通过降低断言或 skip 解决。

## 12. 每卡交接与状态账本

交接至少记录卡号、实际基线／分支、修改文件、架构影响、与允许范围的偏差、补充用例、内容／diff 自审、真实运行命令及结果（无则明确“未运行，按 Validation Scope 留待发布”）、矩阵状态、未覆盖项、后续依赖。提交发生时附 commit／push／PR 身份，不默认合并。

| 卡片 | 当前状态 | 验证 |
| --- | --- | --- |
| IP-00 | 已完成 | ADR Accepted；隔离基线、规范、接缝及用量方案已核对 |
| IP-01 | 已实现 | 专项与源码 Electron 验证通过，覆盖限制见专项回执 |
| IP-02 | 已实现 | 专项与源码 Electron 验证通过，覆盖限制见专项回执 |
| IP-03 | 已实现 | 专项与源码 Electron 验证通过，覆盖限制见专项回执 |
| IP-04 | 已实现 | 专项与源码 Electron 验证通过，覆盖限制见专项回执 |
| IP-05 | 已实现 | 专项与源码 Electron 验证通过，覆盖限制见专项回执 |
| IP-06 | 已实现 | 专项与源码 Electron 验证通过，覆盖限制见专项回执 |
| IP-07 | 未开始；待发布授权 | 未执行发布门禁 |

2026-10-31：本轮仅知识交付，ADR 保持 Proposed；不修改代码仓、不运行测试或产品回归、不启动真实模型调用。


### 2026-10-31 实施交接

用户后续授权已落实，上一条“仅知识交付”保留为早期历史。本轮状态以本节及[专项验证回执](input-prediction-validation.md)为准。

| 卡片 | 实际 Module／结果 |
| --- | --- |
| IP-00 | 代码 RC31 `73ff763a`／知识 main `2f83d5f`；独立 codex 分支；原工作树不动；不新增依赖 |
| IP-01 | protocol/input-prediction、runtime-core 控制器；实例／版本／取消／TTL／单次校验与本地 CAS |
| IP-02 | system-context Source v2、runtime-node service/policy/text-inference；五种 wire 的既有 Adapter；显式模型路由、预算与无正文 trace |
| IP-03 | Desktop snapshot／usage-budget／Worker credential Adapter、固定 IPC owner、catalog／preload／client contract、设置独立开关与回执 |
| IP-04 | BotComposer 装配共享 Hook／镜像／编辑事务；灰字不入真实草稿，采纳后沿 session.edit 保存 |
| IP-05 | continuation 后缀与独立草稿外发开关；末尾折叠 selection、IME 优先与旧代次拒收 |
| IP-06 | 经典 ComposerDraftControls 叶子复用；slash／mention 原优先级、原草稿持久化／发送不换链 |
| IP-07 | 用户授权的提前源码功能验证单列；版本全部 PR、最终联合候选、完整产品包和安装版门禁仍待实际发版 |

必要范围补充：设置面增加独立 InputPredictionPanel；原 llm-config-store 仅暴露可替换的异步凭证解析 Adapter，原同步接口兼容；model-credential-client 允许 Worker 配置短 Helper 超时；验证脚本位于代码仓 desktop/scripts，所有持久知识仅写本知识仓。未引入新权限、工具、存储目录或正式输入类型。

最终交付：代码 [PR249](https://github.com/ly-ccx/Peer-Agent/pull/249)，提交 c78f861f；19 项源码 Electron、8 张图逐图自审与 verify、50 项专项通过。完整测试的时序重跑、真实模型样本及未覆盖项已在专项回执记录。当前代码未合并／发布。
