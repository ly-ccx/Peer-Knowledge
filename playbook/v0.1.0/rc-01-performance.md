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
