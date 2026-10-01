# RC-01 性能与壳层自测实施边界

日期：2026-10-01。级别 B；依赖 Beta5 已发布。负责人已要求自主完成全部实现、自测和详细验收文档；包含必要路径、回归修复、CI及预发布合入，不新增审批停点。GA仍等待负责人全面测试。

## 边界与证据

不改 capability/permission/Evidence/Context/storage 协议。新脚本只操作 mkdtemp 隔离目录，显式区分生产数据读取、脚本执行器、真实模型和发布包。原始个人数据不重置，凭据不进入证据。每指标5次中位数并保留所有样本；规模必须200 bot/10000 messages/100000 inbox events/10000 memories，经生产读取核对。脚本回合不得充当真实快档p50。报告非全达标时exit1；供应商失败样本不能静默删除。

列表/搜索测生产应用服务投影及完整语料（首索引和热查询分列），不能仅测索引数组循环。收到/消费在实际IPC/UI或生产queue→conversation→wake链测量并写清计时边界；UI可见收到由Electron smoke额外测。收件箱冷恢复用新reader读取全部规模事件并还原游标；不能只读最后一条。空闲用独立进程初始化200宿主并稳定GC取增量RSS/heap，记录没有模型流；不是仅除以一个空数组大小。真实模型5轮要记录模型/每轮耗时/终态。

## 允许路径

- 新 `apps/desktop/scripts/seed-bot-shell-home.mjs`、`perf-project-agent.mjs`、`bot-shell-electron-smoke.mjs`、对应 `.test.mjs` 及专用fixture辅助模块（同目录）。
- `apps/desktop/package.json`：脚本入口及脚本测试登记。
- `.github/workflows/ci.yml`：mac/Linux Electron smoke（Linux Xvfb与必要系统库）；保留原完整测试门禁，不删除/skip旧测试。
- `apps/desktop/scripts/background-tasks-electron-fixture.mjs`、`apps/desktop/electron/main/global-background-service-smoke.test.mjs`：旧fixture仍导入已移除GlobalBackgroundTasksButton导致启动失败，改用现有BackgroundRunsProvider+BackgroundRuntimePanel生产组件；明确fixture入口不是当前产品全局入口，不削弱停止反馈/实际端口释放断言。新增产品图标只用SVG。
- 达标需要的生产修复：先在本边界追加测量事实和具体文件，每个修复单独提交，说明对应预算及回归测试；涉及协议/权限/Context/存储边界时先更新架构决策。

main.mjs净增0，不扩展ChatSurface/Sidebar/LlmSettingsPanel/TUIapp。验证全build→受影响包test→typecheck/architecture→mac/Linux精确HEADCI；各结果真实写handoff，性能偏差不能自行视为负责人接受。

## 首轮测量与搜索修复（2026-10-02）

基线 d90e58c2，200 bots / 10000 messages / 100000 inbox events / 10000 memories，经生产读取核对。五次中位数：list 56.62ms（<100，通过）；search 185.61ms（<150，失败）；received 15.17ms（<300，模块路径）；consume 14.26ms（<200）；warm memory 10.37ms（<50）；cold inbox 310.82ms（<1000）；idle incremental RSS 819118 bytes/bot（<2MiB，零模型调用）。首搜索188.11ms失败，记忆索引首次重建3434.37ms另列，不可混成热查询达标。

搜索同一请求重复构建目录：directory.search 读取全部机器人；readSearchCorpus 再 directory.list。允许 B 级内部端口修复：directory.query 返回同一投影的 `{items,catalog}`；应用服务与 desktop corpus 消费该快照，保留 legacy search port 兼容与实时语料指纹失效。没有新的 IPC、存储、授权或 Context 契约。

新增允许文件：`packages/runtime-node/src/project-agent/bot-directory.mjs` 及测试；`apps/desktop/electron/main/project-agent/project-agent-application-service.mjs` 及测试；`apps/desktop/electron/main/project-agent/project-agent-host.mjs` 与 `desktop-integration.test.mjs`（必要时）。每个性能修复单独提交，报告改前改后完整样本；不能删除初始失败。

搜索修复首轮：5次 search 中位128.86ms，首次索引124.29ms，均<150ms；list54.98ms，其他模块预算通过。原始报告是实施中 dirty tree 的测量，最终精确HEAD仍须重跑。

另外发现全量记忆索引重建3427ms：`fts-index.rebuild` 清空后仍对每行在 FTS 虚表按未索引 id 执行 DELETE，随着数据增长形成重复扫描。允许 `packages/runtime-node/src/sqlite/fts-index.mjs` 与测试做 B 级可丢弃索引性能修复：全量重建按 id 最后值去重后直接插入，保留普通 upsert 替换、短词/中文查询、失败 rollback 与缓存可重建语义。不改 SQLite schema、真源 JSONL、记忆准入或 Evidence；独立提交并报告冷重建改善，不把热查询伪称冷重建。

冷FTS重建修复首轮：3427ms→42.29ms，warm memory9.26ms，search129.45ms，所有本机模块预算通过；报告 `rc01-perf-fts-first-20261002.json` 为实施中 dirty tree 事实，最终仍精确HEAD重跑。定向 FTS/memory15测试通过，含重复ID最后值、数值/字符串同ID、空内容清除旧索引、不可序列化meta失败时完整rollback。

后台运行真实 Electron opt-in 重跑：13 pass / 0 skip，实际TCP服务、停止拒绝/等待/仅ack/终态 × 保持打开/关闭重开/header remount，释放端口全部通过。test-only trigger用于打开生产Panel，不宣称已删除的产品全局按钮仍存在。

Responses修复代码PR #92已合入 5ef4659f（精确tip9fc18b78，CI36890401754 macOS/Ubuntu SUCCESS）；知识PR #23合入f69ca2e6。该依赖修复不改 beta.5 tag，最终RC安装包重复真实多入口验收。

## 真窗口消息与快捷聊天修复边界（2026-10-02）

首轮200机器人/10000消息Electron失败：发送后只显示「发送中」；实际队列与conversation均已持久化输入和回复。原因是renderer按forward读取最早40×50条，漏掉末尾新消息，且没有展示已有submit-input成功回执。初始失败保存在evidence；不能修改脚本去等待虚假的模型文本标记。

允许B级修复既有分页接口适配与UI状态：`renderer/src/project-agent/state/useBotConversation.ts`、`botConversationState.ts`及测试、新`conversationPager.ts`及测试；`conversation/{BotConversation,BotMessageList,UserBubble}.tsx`与`styles/bot-conversation.css`；`renderer/src/preload/contracts/bootstrapPreloadApi.ts`补既有runtime已支持的`latest?:boolean`字段；`packages/i18n/src/index.ts`只追加收到/早期加载键。首屏读取最新50条，变化合并最新页，向上加载更早，引用可检索旧页；成功持久化回执才将同inputId从发送中变为已收到，失败保留同ID重试，收到不等于模型回答/任务签收。不改持久化协议、IPC channel、权限、Context或Evidence。

同次窗口发现QuickChat误用其角色不允许的settings:get。允许`electron/preload/preload.source.cjs`、生成`preload.cjs`、`initial-settings.test.mjs`修复现有getSettings的传输适配：QuickChat使用既有已授权settings:get-sync读最新快照，主窗口保留invoke；公开Promise返回契约不变、catalog角色权限不扩大、main.mjs不改。测试含首次和设置变更后的刷新；Electron smoke要求没有角色拒绝日志。

真实快档测量增加允许脚本`apps/desktop/scripts/perf-project-agent-real-model.mjs`：明确选择本机已配置模型，只在mkdtemp隔离home复制该渠道配置与凭据引用，源生产Electron/host/Provider真实执行5轮简单post_reply，不替换认知，最后清除复制凭据。报告只保留模型名、耗时、turnId和终态，不输出密钥/配置正文；失败样本保留，p50<6s须实测。用户原始配置不写回。它是生产模型性能证据，不取代签名安装包或复杂任务验收。

QuickChat设置修复后发现既有B3-11的project-agent:list/submit-input同样漏入角色目录。先更新ADR85 Accepted补充窗口准入边界，新增允许`electron/ipc/channels.mjs`（仅这两个channel加入quick-chat，popover保持拒绝）、`electron/main/ipc/trusted-window-registry.test.mjs`，按生成流程更新preload.cjs；main净增0、没有新channel或批准权限。真窗口须实际QuickChat发送并由租约宿主持久化一次。

真窗口修复首轮通过（dirty tree，最终clean HEAD待重跑）：200机器人、五次输入可见Received中位57.2ms、真实QuickChat列表/quick_chat输入仅一条、10000消息向上加载、更改档案设置tab、经典↔机器人列表且200身份保留，pageErrors0、角色拒绝0、owned进程退出。完整应用从脚本launch到window ready约31s单列，不能写成模块cold inbox 311ms。测试脚本中首次30s启动等待、回复与列表预览的同文定位及设置覆盖经典侧栏的测试定位问题均已修正，没有改预算或删除初始产品失败。

## 定向唤醒跨机器人丢宿主问题（2026-10-02）

复查真实入口时发现runtime-host.sync([workspaceId])把本次requested集合当作全局注册表，drop其它已就绪runner。Desktop多个原入口都用单项目sync，可能令其它正在运行机器人丢掉临时回合/Watch状态。必须补齐B级内部宿主修复，不改变租约/存储/调度协议：允许`packages/runtime-node/src/project-agent/runtime-host.mjs`及新`runtime-host.test.mjs`。局部sync只推进指定项目；清退仍依据完整有效项目目录及当前真实租约。全量sync行为保持。测试须先红：局部唤醒B保持A同一runner且在途回合能提交、未请求但租约失效/目录移除仍清退、零额外模型回合。独立修复提交并复跑真实窗口/全门禁。

局部唤醒修复回归已先红后绿：在A回合等待执行器返回时唤醒B，A保留同一runner、signal未取消、A/B各提交一次真实canonical回复、后续全量sync不重跑；未请求的B失去租约或被移出目录仍清退。两个隔离回归测试通过。初始新测试fixture未传rootDir，误用了默认路径并生成a/b测试运行目录；发现后按单条fixture输入ID/正文/时间及完整文件白名单核对并仅移除本次生成的两目录，未改既有UUID项目或设置；测试改mkdtemp隔离并再次完成先红后绿。此fixture错误与修复保留，不能称首次自测毫无失败。生产修复单独提交d70eb87a，追加preload测试进入全仓门禁；最终完整门禁与精确HEAD真实/脚本性能继续重跑。

## 真实快档首轮与测量隔离补充（2026-10-02）

Luna首轮真实生产请求两次返回HTTP200但均无文字/工具（input tokens8427/8471，output4），canonical生成agent_unavailable empty_model_response；失败后该runner按既有策略等待用户重试，后续测量输入排队。因此不能将后续150秒等候当作模型响应性能。保留全部首轮失败样本；测量脚本改为同一隔离home的5个独立机器人各1轮，避免一个供应商失败阻塞其它样本。报告明确独立项目，不代替同机器人连续聊天验收。失败只输出受控错误码/阶段/终态，不复制用户正文或密钥；SIGINT/SIGTERM只取消当前测量并经finally关闭本轮登记进程、清除凭据副本。允许该脚本及同目录纯测量辅助模块/聚焦测试。预算仍6秒，不能以测试独立作为达标。

## 正确保留宿主后的收到预算回归（2026-10-02）

精确e760819d窗口复测可见Received p50717.8ms >300，5轮均约715–732ms，必须修复。局部sync保留200runner后，每次清退检查200次ownsProject→getSettings→loadMigratedSettings→registry.sync200工作区，重复settings身份校验形成平方开销。新增B级内部只读端口`readOwnedWorkspaceIds(inventory)`，只给当前sync清退扫描使用：desktop一次读全局开关、同批active-profile inventory、逐项目读真实host lease。它不是权限或执行依据；recovery/runner/supervisor仍用原ownsProject逐次校验。fallback宿主保持原行为。允许既有runtime-host及测试、desktop装配及integration测试补入此端口；main净增0、无IPC或持久化变化。测试含200项目定向唤醒全局设置读取次数恒定、全局classic切换仍清退、真实租约失效仍拒绝执行。保留本轮Failed窗口证据，不删初始失败或提高300ms预算。

局部清退扫描的只读批次快照修复3e276eed：200项目设置读取次数回归先红后绿，28个integration/host测试通过；完整build/test/type/architecture通过（desktop5255pass/5既有skip）。精确HEAD真实GLM五轮p504402.73ms、规模八预算全达标；窗口Received75.4ms（717.8→75.4），七项通过，零pageerror/角色拒绝。完整窗口冷就绪29.61秒单列，不能冒充核心inbox312ms。

代码自审另发现已有分页修复在两次刷新之间新增超过50条时会漏中间页，以及加载更早后虚拟窗口沿用数字索引而丢掉原阅读锚点。继续在已允许的conversationPager/BotMessageList/botConversationState及测试中修复：最新页与上一份快照无ID交集时向前补齐到交集；失败时整批不发布、不推进游标；更早页按原row身份保持窗口锚点。测试新增110条突发和中间页失败重试、超过200行的前插锚点。没有新接口/权限/存储协议。最终精确HEAD继续复测，保留3e性能证据。

长对话更早页按cursor方向保持顺序（同一时间戳也正确），刷新按110条突发跨页补齐，投影卡片不能充当canonical页交集，失败整批保留旧快照。14聚焦测试通过。c3c98c33真实窗口首次扩展多页测试在第二次滚动超时；首轮怀疑前一次DOM出现时loadOlder的rAF滚动补偿尚未完成，下一次滚动被busy合并；加aria-busy后仍在同一9830目标超时，故该推断不能视为根因。增加真实aria-busy加载状态，让测试等待分页完成再滚动；不增加超时、不改变加载预算。初始扩展失败保留。

继续观察多页fixture：实际新增输入/turn也计入50条分页，不能假定每页固定rc-message编号。允许在隔离复制的application-service只读返回点收集before/nextCursor/count/firstID/lastID，报告实际游标和DOM范围；不替换读取结果或削弱断言。

确认另一个B级刷新循环：每次renderer刷新后markRead；application-service对成功结果无条件广播changed；随后又触发读取/markRead，既有cursor相同仍重写与通知。允许已列bot-directory及application-service和测试令相同read-cursor返回内部changed:false（不重写）；service保持原公开响应形状、只在实际游标变化或legacy端口未知时广播，onViewing仍每次更新。无新增IPC/权限/存储格式。须验证首次标读一次通知、同游标不写/不通知、新消息推进及仍有viewing回调。

只读游标实测4d0da5aa：读取已到9800页，但跨200行虚拟化后，DOM从9933开始且总滚动高度从13251骤降6586；占位div在flex列中默认可收缩到0，破坏虚拟滚动几何。另未虚拟化时scroll未更新阅读索引，跨阈值沿用末尾索引。按已允许BotMessageList/styles修复：占位及消息子项禁止纵向收缩，所有滚动都维护阅读锚点；继续真实多页及返回最新测试。引用跳转须先把目标窗口提交，再定位DOM，取消自动pin-bottom避免覆盖跳转。没有新IPC/权限/数据契约。

e2b76d70首次几何修复后的扩展测试推进到9780仍失败：更早9750页已读到，但固定72px估算与实际约80px行高、前插后的总高度补偿令目标移出窗口。必须把窗口计算集中为renderer深Module，实际测量行高、按row ID保留视口位置，前插补偿不再用总高度差。新增允许`state/conversationWindow.ts`、聚焦测试、`conversation/useConversationWindow.ts`；既有BotMessageList调用接口，BotConversation只传引用跳转序号，CSS为可测量行容器。无新运行时协议/权限/存储/Context边界。真实Electron仍验证跨200行、更早分页、引用远处消息及返回最新。

搜索预算补上输入→可见结果的5轮窗口计时，不用应用服务计时冒充完整UI。保留初始服务达标事实；若窗口失效/超预算，先定位再修复，预算仍150ms。

复核窗口搜索入口发现useBotList只消费search返回items（名称/预览/任务标题），忽略完整语料hits；与“搜索机器人、消息、任务”文案和预算规模不一致。允许B级既有renderer适配`state/useBotList.ts`、`botListState.ts`与测试：命中消息/任务/记忆的workspace ID与当前catalog归并去重，角标仍取当前目录；结果绑定query，旧请求结果不能瞬间充当新查询命中。不改IPC搜索协议或索引准入。先红后绿，并实测输入到可见结果五轮。

切机器人时BotConversation未以workspace ID重新挂载，旧高亮和阅读锚点可能触发新项目无意义的全历史定位。允许BotListShell现有装配点仅追加React key（净增1行，不扩展业务逻辑）；每个workspace的窗口状态随组件生命周期隔离。

精确a0fbbcef搜索窗口首轮p50=201.10ms（274.5/204.4/201.1/200.0/199.2）超过150，未执行后续消息/分页断言，owned进程正常关闭。不能以模块132ms代替。允许隔离application-service搜索点追加只读计时（目录投影、语料指纹、索引和同步总耗时），报告不得含用户正文。

454fe34e只读分段证据：目录投影185–210ms，指纹9–11ms，热索引约1ms；窗口p50=223.1ms。生产directory的listClassicGoals对每个机器人重新读取registry、全部conversation metadata和Goal index，200行重复200次；此前perf注入无经典目标读取器，因此没有覆盖此成本。允许B级投影批次快照：新增desktop `classic-goal-projection.mjs`及测试，host装配采用batch；portable bot-directory及测试追加可选`readClassicGoalsBatch`内部端口，单项目get保留实时读取。每批只读一次registry/会话元数据/计划，逐项目按既有projectHistory/projectClassicGoals隔离过滤。没有跨调用缓存或执行授权用途，不改IPC/存储/main；完整窗口和模块预算重新测。新增integration读次数回归先红后绿。

真实Desktop完整投影d8fa3ea2 p50=137.05ms仍>100ms，不能用注入简化directory的55ms代替。批准实施ADR86的A级内部批量读取契约（先文档、后实现）：新增允许`packages/conversation-store/src/index.mjs`、`index.d.ts`及`persisted-batch.test.mjs`；已列bot-directory与测试追加可选readMessagesBatch；host与性能脚本接入。现有单条读取、streaming截断/runtime检查语义、跨入口刷新仍保留；不新增IPC/权限/Evidence/持久化格式。无跨调用缓存。测试逐条/批次等价、实际索引读次数、外部修改下次可见，完整窗口预算重新测。

416addfc首轮夹具观测发生Node inspector promise被GC（没有重新执行产品动作，进程正常关闭）；readMain只对该观测错误最多重读3次，样本仍来自原动作、预算不变。复跑d8fa3ea2未触发观测重试，完整投影仍超预算。两次失败均保留。

7d61baa0完整目录投影101.88ms仍失败（首投影97.53ms不能替代5轮p50），故继续沿ADR86补批准投影批次：新增允许`packages/runtime-node/src/project-agent/approval-store.mjs`及测试；directory、host及规模脚本接入可选readApprovalsBatch。listByWorkspaceIds保留全局fold去重与workspace过滤，只把一次扫描共享给同一投影，不参与批准执行或PermissionGrant。先红后绿扫描次数及fresh-state测试，保留当前失败。

批准目录扫描计数回归先红（缺少batch Interface）后绿；20个approval/directory测试通过，验证200个项目一次catalog扫描、批准终态下次读取可见、未请求scope不混入、details与批次不可用时保留原实时路径。实现3be1110d已推送；实际窗口与最终完整门禁待验证。

精确干净3be1110d真实源Electron完整窗口通过：200行列表p50=20.98ms（100），输入到完整语料命中可见p50=35.30ms（150），发送到可见Received p50=71.90ms（300）。扩展跨200行的更早分页、加载9500引用并居中到可见视口、返回最新全部通过；Quick Chat只写一条canonical quick_chat输入；档案与classic往返保留200身份；零renderer错误/窗口角色拒绝，owned进程已退出。完整窗口冷就绪单列，不替代核心inbox恢复指标。最终完整门禁/真实模型五轮/两平台CI尚待本HEAD核实。

最终3be1110d本机完整build/test/typecheck/architecture全部通过；runtime987，desktop5265pass/5原有skip，TUI749pass，其余包零失败/取消。真实GLM五个独立机器人一回合均实际post_reply并落盘，p50=3819.20ms；单样本6091.55ms如实保留，标准为五次中位数<6000。复制的凭据已移除，自有Electron正常关闭。生产规模八项均通过：list16.72/search98.94/Received15.76/consume14.63/memory9.23/coldInbox318.44ms，增量RSS849592.32B/机器人；窗口计时独立按前述21/35/72ms记录。两平台CI仍在跑，不提前写RC-01完成。

CI36902227505：Ubuntu完整门禁及Electron窗口通过；macOS完整门禁通过，但窗口观测readMain连续3次Resulting promise was garbage collected，未产生5轮list预算，不能视为产品失败或通过。sourceHead为PR测试merge cf64a14c，PRtip3be1110d。隔离观测改为entry定义的record函数：每条已有只读观测捕获样本后持久到本fixture的JSON，测试从文件读取，不再用inspector evaluate Promise取投影数组；不重放产品动作或延长预算。main生产文件仍净0；所有失败样本保留。Linux成功报告与mac失败同存。

CI36903267497原inspector观测问题消失，Linux完整通过；macOS生产list60.58ms/search106.10ms均通过，但native click15000ms超时，故RC01仍不能完成；postmortem读到9950..9999说明产品动作已打开对话，不重放该动作充当成功。初始指示：200个SVG头像（含离屏）持续breathe/blink等动画，可能增加Intel macOS renderer事件负载。批准C级离屏动效治理：BotAvatar.tsx接可见性/窗口可见/系统reduce表达gate，共享IntersectionObserver Module；新增state/avatarMotionRegistry.ts及测试，CSS bot-list追加暂停离屏规则。只减少不可见动画，mood/头像身份/能力状态不变；实际窗口记录active avatar动画数量，原click超时与预算不放宽。新增脚本只读观测点记录数量，后续CI证明，不把假说先写成根因。
