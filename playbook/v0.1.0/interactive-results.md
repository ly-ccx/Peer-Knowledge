# ADR 118 交互结果实施与验证

创建时间：2026-11-03
最后更新：2026-11-03

状态：实施中，未完成。七项文档补充已交付，用户现已明确恢复“完整实现并测试完成”的目标，继续完整代码实施与提前验证。既有实施、验证和未提交工作均保留。ADR 118 仍保持 Proposed；实现及单项测试不构成决策接受、运行时授权或产品验收。

## 范围与依据

后续范围由 [ADR 118](../../knowledge/decisions/118-openui-interactive-results-and-runtime-boundaries.md) 的首期 IUI-00—04、IUI-T01—29 及 §22 定义，尚待设计评审接受。既有代码起点为 Peer-Agent `4a58e2846875f85de69915764a127096721c5b0d`（RC35），分支 `codex/openui-interactive-results`；知识分支 `codex/openui-interactive-results-adr`。不以单个模块、静态 Demo 或某组测试通过代替完整交付。

当前完整目标覆盖 Protocol、Provider、材料/版本/状态存储、Context Source、界面与多入口及测试，继续推进原范围。实施与测试来自用户恢复的明确目标，不能从 Proposed 文档、阶段表或历史实施/测试记录推导能力开放。公开接口、脚本准入、按需加载和原 Provider encoder、授权、Evidence、任务内核继续作为边界。

## 实施阶段

| 阶段 | 必须交付 | 当前事实 |
| --- | --- | --- |
| IUI-00 | 固定 SDK 脚本/AST/状态/纯求值与副作用审阅，公共接口验证；材料源、事务及逐存储兼容方案 | 公共 AST/严格 token 覆盖、共享预算与纯求值已用于独立 Worker；Bun 单文件探针已从空目录运行。SDK bootstrap 禁用、生产/开发 bundle 的真实 React 挂载和状态适配已有专项验证；产品 CLI、完整宿主接线及其余共享存储兼容尚待完成，未退出 |
| IUI-01 | Protocol/InteractiveContent/MaterialSource、受治理发布与只读检查、只读 worker 例外、版本 CAS、事务与 Evidence 对账、首次新写入前兼容保护 | 已提交 `b7b429ef`、`ea7e5afd`、`94ef2e92`、`9f3e0a7a`、`aabeaef4`、`5f9953ca`。真实 Desktop/TUI Provider、投影/准入/执行闸、规范工具及用户上传材料、启动/查询对账、持久准备身份/修复预算与授权分类已接线并验证；功能默认关闭。`f5eaa173` 补实际旧草稿写者/已打开队列/Conversation 重写的材料保留与准入链；其余共享存储、留存及完整能力验收继续待完成，未退出 |
| IUI-02 | Frost 组件、资源引用/会话、状态 CAS/单写者、恢复与冻结条件经原草稿链交回 | `8b3ffbcf` 后，`f5eaa173` 接独立冻结/草稿准备回执、实际主窗口 claim/ack 与宿主读回、原 Composer CAS、明确发送、队列/规范消息及委托材料；真实 Electron 主区/独立窗口与实际草稿/队列/Conversation 联通。Verifier 固定目标、真实文档/浏览器混合场景、条件标签映射及其余产品验收尚未完成；功能默认关闭，未退出 |
| IUI-03 | 显式 Context Source、预算/修复、按角色能力准入、Bot 引用和固定版本语义核验 | 显式 L5 目录 Source 已接入两宿主，按真实投影/角色准入，规则和工具来自同一次投影；目录由公共规格生成，specHash 包含资源限制。委托先核对 Verifier inspect 库存。Verifier 固定目标/证据允许列表、Bot 结果引用与真实模型生成/修复效果待完成，未退出 |
| IUI-04 | 多入口文本、包体/按需加载、兼容和完整功能验证 | 待实现 |

## 验证与完成标准

七项文档补充提交只做内容、引用及 diff 审阅。恢复后的完整实施目标明确包含测试，提前验证与改动相关的模块和宿主链；完成后执行完整 build/test/type/architecture/IPC 及产品 capture → AI 审阅 → verify，逐项记录实际覆盖。只使用隔离临时数据，不安装或重启日常应用，不创建版本/RC 或发布标签。

验收清单是 ADR §22 的 IUI-T01—29，以及两种实际已配置 Provider 编码路径的真实模型生成/修复/降级记录。需要实际配置或外部条件的项目若无法完成，明确登记缺失，目标保持未完成；不以脚本模型夹具替代真实模型、不把源码自审称为独立验收。最终回执列明实际代码提交、测试结果、产品证据、真实模型/安装包/多入口/无障碍覆盖。

## 当前验证记录

- `ea7e5afd`：Protocol 构建与 runtime-node 依赖链构建通过；材料/事务/状态/Worker 共 26 项测试在 Node 25.9.0 与 Bun 1.4.2 通过。
- `94ef2e92045e651e80fbc5dbb9543ab3b09ef050`：五包依赖链构建通过；Protocol、Runtime Core/SDK/Node 四包 typecheck 通过；`node scripts/check-architecture-governance.mjs` 通过（未以此代称含 UI 的完整 architecture 门禁）。
- 同一代码的定向组合共 109 项 Node 测试通过，覆盖协议/内容、交互运行时、EvidenceIndex 缓存/桌面预览证据、SDK Hook 和真实 Desktop 文件 Provider；runtime-node 全包 1805 项与 runtime-sdk 全包 41 项通过；交互运行时 52 项在 Bun 1.4.2 通过。Node 为 25.9.0，无 skip/cancelled。
- 固定 RC35 normalizer 与已打开追加描述符实测保留原始发布行；丢确认的持久登记不重复追加。同一 wire call ID 跨子会话互不冲突；校验时钟不制造无变化版本，分类提高不会因 unchanged 降级。真实 Node/Desktop 文件读取改写当前源文件后，快照仍为原字节；完整 sideband 不进入序列化事件。
- 最新代码生成的 Bun 单文件校验/求值探针在无 node_modules 的空目录运行，help 与 Worker 求值通过；二进制 62,672,754 字节，SHA-256 `9905092a1ee95fdb0ed125c41ea550d840d898c36627a8ab3bee9c08abbfcfbc`。这是隔离测试探针，不是产品 TUI/CLI 的安装、包体或入口验收。
- `9f3e0a7a`：依赖链构建、Runtime Node/TUI 类型检查及 `check-architecture-governance.mjs` 通过；228 项 Node 定向组合测试与 95 项 Bun TUI 宿主/回合/模型适配测试通过，均无 skip/cancelled。覆盖真实 Desktop/TUI 文件 Provider → 固定材料 → 受限发布 → 持久索引、Verifier 实际只读求值、角色/租约/旧 epoch、原调用参数固定、跨实例修复预算与索引追加后失去所有者的恢复责任。不是完整仓库门禁或产品回归。
- 同一提交的目录 Source 为约 6 KiB，现有宿主保守估算约 1490 token；这不是 Provider tokenizer 实测。Source 只从可信目录生成，不准入程序/材料内容；普通问答、Explorer、无投影和不完整发布/检查能力组合不开放语言。生成的 specHash 与实际公共适配同源，并包含统一资源限制。
- `aabeaef4`：规范 user_upload 仅从当前工作 canonical 用户消息的有界内联正文建立固定引用；观察时间来自真实消息，密钥字段同时从文本和 JSON 投影脱敏，不伪造 Tool Evidence。190 项 Node 定向组合与 63 项 Bun 交互运行时测试、依赖链构建、Runtime Node/TUI 类型及治理检查通过，均无 skip/cancelled；不代表完整产品验收。
- `d3643cf7`：SDK 变换只作用于通过公开根入口定位的 SDK 模块；实际 Vite 配置测试确认开发 bootstrap 不进入该产物，应用其他模块不受影响。3 项定向测试通过，尚未以 React 实际挂载证明运行期无副作用。
- `5f9953ca`：授权前只读核对实际来源等级，scope 绑定最高分类；来源或 owner 分类在授权期间提高时拒绝旧 scope 提交。真实成功观测即使正文过大不能固化，也保留 owner 单调隐私底线；关闭功能不会清除此底线，首次关闭状态不创建结果子域。新冻结反馈继承当前底线，历史冻结值及分类保持不变。68 项 Node 与同样 68 项 Bun 交互运行时测试、依赖链构建、Runtime Node/TUI 类型及治理检查通过，无 skip/cancelled。
- `9c726072`：106 项 Node 定向组合、98 项 Bun 定向组合、依赖链构建、Desktop/Runtime Node/TUI 类型及完整 `architecture:check` 通过，无 skip/cancelled。共享 `prepareEvaluator` 只编译固定公开 AST，一次核对目录/状态 schema 后同步检查候选；Set/Reset 只执行当下真实已准入的 SDK plan，展开后最多 16 步，失败不部分修改输入。该限制包含在 specHash。
- 同一提交的 `interactive-renderer.test.mjs` 在独立临时数据的 Electron 41.7.1 中实际挂载固定 SDK 与 Peer 组件，分别构建 production/development bundle；在 SDK 加载前拦截网络，未观察到 HTTP/WebSocket 请求、页面异常或 devtools 自动挂载。实际覆盖输入 DOM/焦点、合成 composition、除零时隐藏结果、恢复计算、Select、Checkbox 键盘/标签点击、分页及无关参数变化保持页码、局部 Reset、宽窄及两主题。四张组件截图逐图实现者自审；窄图与前次已审图片逐字节相同，宽图再次检查。不是系统 IME、真实模型、安装版、完整产品 packet 或原生资源窗口验收。组件夹具的状态端口仅为隔离内存适配；真实 SQLite/sender/CAS/冻结链由上述独立领域测试验证，尚未接成正式产品链。
- `518420a4`：130 项 Node、115 项 Bun 定向组合和 46 项既有资源/可信窗口/返回状态组合通过，无 skip/cancelled；Desktop 构建（含依赖与 IPC catalog）、Desktop/Runtime Node/TUI 类型和完整 `architecture:check` 通过。这是本批模块与入口验证，不是完整仓库门禁。隔离 worktree 的 Electron npm 安装不完整，Node 宿主测试借用既有 dist 定位，GUI 测试直接选择既有 Electron 41.7.1 可执行文件；未安装或重启日常应用。
- 同一提交的原生专项通过实际 `NativeResourceWindow`、生成 preload、catalog 授权、应用服务、结果/状态 SQLite 和阅读记录运行；已发布结果及 Grant 为确定性领域夹具，不是真实模型或任务发布验收。覆盖确认保存、合成 composition 阻止关闭、保存后再次关闭、重开恢复同值/固定版本/读位、只读摘要降级保留损坏检查点及旧读位；同时核对无文件读取、旧 Settings 写入、重复版本/发布操作、HTTP/WebSocket 和页面异常。3 张原生图逐张自审；关闭失败提示已改为“上次关闭”的历史事实，避免保存后仍声称当前未保存。
- 最新生产/开发 SDK 组件专项也重新通过，4 张图的两种构建输出按主题分别逐字节一致；实际再次查看两张唯一图片并核对全部指纹。原生与组件证据均为实现者自审（independent=false），不是完整产品 packet、安装版、系统 IME、读屏或真实模型验收。原生返回测试的主窗 ack 为宿主夹具；正式混合标签返回消费者仍待接入。
- 交互 SQLite 当前内部 schema 为 5，内容规范编码为 `peer-interactive-content-1`；在准备记录、候选预算与 owner 分类底线之外加入有界阅读历史和布局 metadata。早期分支 schema 1—4 拒绝读写，不做静默迁移或空库重建。首次关闭功能不创建新子域，旧 Settings 写者不会接触 interactive 记录；布局仅已有发布结果的 owner 可首次建立，服务端 revision CAS 已落实，UI 消费者尚未接入。该设备本地新子域未在日常产品中启用；现有 Conversation/草稿兼容保护仍待接线。
- 下一步兼容工作须保留实证差异：输入草稿现有未知 schema 拒写，但旧输入队列会跳过不认识的 ResourceFeedback，不能只扩展联合类型就宣称兼容。冻结条件目前仍停留本机结果子域；需先补齐草稿/队列/消息/委托同值同版的保护及明确发送链，再开放交还入口。SDK chunk/挂载异常的局部降级与重试也尚待接线，不能用普通计算错误和目录不兼容测试代替。
- `98693645`：复用共享延迟加载错误边界，原生控件 chunk 缺失时保留固定摘要、源码入口和领域会话。实测同 URL 的直接重试仍失败，因此原生恢复明确先确认保存，再重载该隔离视图；主工作区备用动作只打开独立视图，不刷新整个应用。后者待正式标签消费者接线后验证。显式恢复中断的 composition 仅把原文本作为草稿保存，不改有效值，也不能冻结成新条件。8 项 Node 会话用例、13 项 Bun 会话/registry 用例与真实 Electron 原生专项通过，4 张原生图逐图自审；缺文件、恢复文件、确认重载、同值同版/旧读位恢复均实际运行，零新发布/取数/外部网络。Desktop 构建、类型及 `architecture:check` 通过；不是系统 IME、主工作区故障或完整产品验收。
- `30cb612b` / `11e2a617`：混合布局 formatVersion=2，包含独立交互表现会话（最多 32 个同 owner 固定引用与读位），参数/草稿/writer 不得进入其中；保留文档、Diff、浏览器和最近描述符。规范化后再次限制 URL/整体字节，避免 canonical URL 膨胀产生自身不可读的行。格式 1 只按已知结构保留升级，旧请求缺少交互会话字段时拒写。固定 `518420a4` 写者在同一已打开存储中先成功写格式 1，再证明格式 2 的旧 order/recent 投影仍合法、但实际旧写者因未知行字段拒绝读写，原行保持；不是靠新增 Diff key 让测试偶然失败。134 项 Node、118 项 Bun 组合与最终 15 项 Node/7 项 Bun 定向用例通过，依赖链构建、Desktop/Runtime Node/TUI 类型与治理/UI 检查通过。SQLite schema 仍为 5；布局有独立行版本，尚未接 UI 消费者。
- `8b3ffbcf01a9b9a14ac6969a9e67a1918876b528`：布局 API 固定预期完整 owner，并在主进程核对真实归属。纯表现会话按固定引用重放迟到读期间的意图，接受真实 CAS 回执；丢确认先读真实行，冲突保留两份候选，显式采用远端前确认输入并换代阅读回调。关闭仅从打开顺序移除，保留有界读位提示；满额只淘汰已关闭提示。旧 Settings 不保存交互种类/引用，旧 localStorage 适配器拒绝覆盖已有新字段/引用、未知或损坏记录。
- 同一提交经规范 EvidenceIndex 的 worker 发布元数据投影交付卡片，使用独立 `interactiveReference`；核对当前 Bot owner、真实 plan/session/conversation、capability/tool 与 Evidence/Artifact 身份。助手文本、普通文件 URI 和跨 owner 元数据不能升级为交互产物。主资源区首次打开仍经实际视图入口重新核对；该卡片不表示任务、计算或验证通过。
- 62 项 Node、同样 62 项 Bun 定向契约用例、23 项既有资源/可信窗口/返回状态用例、两个隔离 Electron 场景通过，均无 skip/cancelled。Desktop 完整构建、Desktop/Runtime Node/TUI 类型、`architecture:check`（含 UI）和 Desktop `ipc:check` 通过。这是本批验证，不是全仓测试/完整产品门禁；构建仍提示既有大 chunk，产品包体与性能验收未完成。
- 主区专项使用实际 `WorkbenchProvider` / `BotResourceLayout`、交付卡片、生成 preload、catalog 授权、领域应用服务、原生控制器及 SQLite；已发布内容和 Grant 为确定性夹具，外壳/非本域草稿索引为夹具。实测同版关后重开/读位、独立窗口接管与正式返回 ack、不覆盖原会话草稿、显式布局冲突恢复并拒绝旧读位回调、组合输入阻止关闭、离开视图后复制/保存中断原文而不改有效值。真实移走 Surface chunk，再恢复文件，确认保存后打开独立视图，未刷新主应用或新增发布/取数。原生专项同步复测缺模块重载、状态损坏摘要及旧读位保留，并在截图前加强终态断言。
- 8 张图逐图实现者自审，`independent=false`。最新主区组 `HhCsGk`、原生组 `tEmfu4`；三张主区图、三张原生图与此前已查看输出逐字节一致，其余两张实际重新查看。联合截图指纹 `c21087433effc26e68b03f7432fee26a420664ff4cf0cc03e5c8ec11cd4b70ac`。主区关闭自动化包含 Playwright 对 beforeunload dialog 的 dismiss，断言实际关闭尝试后窗口仍在及原输入可恢复；不是系统 IME 或手动安装版验收。仍未实际联跑文档/浏览器混合标签、全部缩放/减少动效/读屏/性能，也不是标准产品 packet。
- 上述均为实现者验证，未做独立审查、完整仓库门禁、真实模型或完整产品回归，不构成 IUI-00—04 完整交付；最新后续结果随接线补充。

## 冻结条件交回与传输增量（f5eaa173）

- 代码 `f5eaa17340bb56a094f403364fecf41f76713473` 已推送原实现分支。新增 typed prepareDraft 与生成 preload/catalog 接线；私有 viewHandle 只解析同 owner/固定结果的真实冻结材料，独立视图从实际 registry 找原主窗口，不接受 Renderer 自报接收者、反馈正文或 sender。冻结成功与原草稿准备成功分开；claim/ack 后宿主读回持久草稿或待发材料，不能只凭 Renderer ack 显示成功。
- 原 Composer 保留正文、quote 和附件，准备前预留传输附件额度；超额拒绝且不编辑原草稿。只有明确发送才调用原输入队列。准备确认丢失时复用原 followupId；稍后编辑、保存及接管不改变原冻结值。IME/无效的新候选不能退回上次冻结值，未知或不匹配回执不显示已准备。
- 逻辑 ResourceFeedback 增 interactive 分支，实际草稿首次写入格式 3 并保持门槛。队列/规范消息/委托使用旧端已知的有界文本附件承载完整冻结 JSON，新端在准入/消费/委托/结果访问时匹配真实冻结记录；不建立第二队列，不生成工具 Evidence 或授权。模型历史只在原 user 材料槽投影一次，界面显示未验证引用；损坏/未来版本保留原文，不跳行推进新端游标。
- 固定 `8b3ffbcf` 的真实旧草稿写者、旧上传 normalizer、已打开旧队列对象及实际 Conversation 重写/重开证明材料保留。对照用例也证明把新联合类型直接写旧队列确会被跳过并推进游标，不能用 marker 冒充兼容。真实 SessionSupervisor 将明确锚点转为子消息，原附件与冻结版本完整保留；篡改材料在创建子任务前拒绝。原结果访问与 followup 准入只接受实际记录，不借助手文本或 schema 标记取得权限。
- 295 项 Node 定向组合、55 项 Bun 定向组合及 1 条真实 Electron 主区/原生/Composer/输入链专项通过，无 skip/cancelled；新增 prepare-draft 的来源/顶层 frame 政策另在 6 项宿主组合中复核。Desktop 完整构建、Protocol/Runtime Core/Runtime Node/Desktop/TUI 类型、architecture:check（含 UI）和 Desktop ipc:check 通过。构建仍有大 chunk 提示；本轮不是全仓测试或完整发布门禁。
- Electron 专项使用真实 BotComposer/useInputRecovery、prepare/claim/ack、SQLite、输入队列及 ConversationStore。主区冻结 5、独立窗口冻结 4，原正文/quote/上传均保留；准备不提交、不抢原 Composer 焦点，人工点击发送后 canonical 消息才同时携带 5/4。关后重开、接管/正式返回、布局冲突、关闭拦截、中断草稿与缺 chunk 恢复继续通过。发布/Grant、外壳和非本域索引仍为夹具，没有真实 Provider 模型回合。
- 6 张最终截图逐图实现者自审，independent=false，目录 `peer-interactive-workspace-wGz5ql` 的 review.json 绑定上述代码；审阅指纹 `5d1c3ca2d5e1766d56552db4d6e2a9ad25a5a51535a95fbacd41cad338184ceb`。初次发现测试入口缺正式 Composer CSS 已修正并重采；冻结摘要去掉内部 ID/变量名，存储不保留表现树时暂用稳定条件序号，精确控件标签映射仍须完成。6 图不是标准全产品 packet，也没有真实模型、安装版、系统 IME、读屏、完整缩放/减少动效或性能验收。

## 后续接线与完成审计

- 主资源区标签、布局、最近项目和正式返回已接；继续覆盖实际文档/浏览器混合场景、布局超时后重试读取的读位、Bot 归属永久变化后的不可保存草稿退出恢复、SDK 挂载异常、全组件目录、缩放/辅助技术与性能，不把单结果隔离夹具算作全产品验收。
- 规范发布索引的交付入口已接；继续核对既有 Tool Result 引用到原规范发布记录的关联消费、主 Bot 的结构化引用，以及宿主确认的 head/predecessor 新版本入口。不从助手正文、标题或 URI 文本推断产物或版本关系。
- 冻结条件到原 Composer、明确发送、输入队列、canonical 消息及委托的同值同版链已接并有专项证据；继续接 Verifier 固定目标/状态完整性/证据允许列表，覆盖完整留存与清理以及其余存储重写者。补齐冻结摘要的控件标签映射，不能从本批准入/传输测试推断任务已经通过核验。
- 完成 Verifier 固定目标与证据允许列表、留存/清理责任、TUI/CLI/Remote 实际文本和独立打包入口。另核对用户参数/原始草稿中已知凭据或权限 payload 的权威准入限制，不能只保护工具观测材料或依赖提示词；接管也不能跳过仍待确认的原保存请求。
- 完成两种实际 Provider encoder 的真实模型生成/修复/降级、全仓工程门禁及标准产品 capture → AI 逐图 review → verify。还需覆盖 SDK 挂载异常、主工作区故障恢复、完整组件/图表目录、减少动效/放大/辅助技术及性能；明确记录系统 IME、安装版和真实模型覆盖边界。所有已完成的本批用例只证明其实际覆盖，不代替这些缺口。
